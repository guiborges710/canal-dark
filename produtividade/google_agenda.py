"""Sincroniza os compromissos de produtividade/agenda.json com o Google Agenda (calendário principal).

Mão dupla, e o Guilherme sempre ganha:
- compromisso novo no agenda.json (Ronaldo)        -> vira evento no Google Agenda, com aviso de 1h;
- evento novo que o Guilherme cria no Google        -> entra no agenda.json (origem "google");
- evento que o Guilherme muda ou cancela no Google  -> o agenda.json acompanha (vale o Google);
- só o agenda.json mudou desde a última rodada      -> o evento do Google é atualizado.

Garantias: nunca apaga evento do Google; só mexe nos eventos que ela mesma criou ou
importou (e nos que o Guilherme alterar, apenas lendo); janela de ontem até +90 dias.
Estado da última rodada: .google_agenda_estado.json. Roda a cada 5 min pelo Agendador.

Uso:
  python produtividade/google_agenda.py             sincroniza
  python produtividade/google_agenda.py --simular   mostra o que faria, sem alterar nada
"""
import argparse
import json
import sys
from datetime import date, datetime, time, timedelta

from googleapiclient.discovery import build

import avisar
import google_pessoal
from avisar import PASTA, ler_json

AGENDA = PASTA / "agenda.json"
ESTADO = PASTA / ".google_agenda_estado.json"
TZ = "America/Sao_Paulo"
DURACAO = timedelta(hours=1)
AVISO_MIN = 60


def do_evento(e):
    """Evento do Google -> (data, hora, titulo, local)."""
    ini = e["start"]
    if "dateTime" in ini:
        dt = datetime.fromisoformat(ini["dateTime"]).astimezone()
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M"), e.get("summary", "(sem título)"), e.get("location", "")
    return ini["date"], "", e.get("summary", "(sem título)"), e.get("location", "")


def corpo_evento(item):
    if item.get("hora"):
        ini = datetime.strptime(f"{item['data']} {item['hora']}", "%Y-%m-%d %H:%M")
        horarios = {"start": {"dateTime": ini.isoformat(), "timeZone": TZ},
                    "end": {"dateTime": (ini + DURACAO).isoformat(), "timeZone": TZ}}
    else:
        d = datetime.strptime(item["data"], "%Y-%m-%d").date()
        horarios = {"start": {"date": d.isoformat()}, "end": {"date": (d + timedelta(days=1)).isoformat()}}
    return {"summary": item["titulo"], "location": item.get("local", ""), **horarios,
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": AVISO_MIN}]},
            "extendedProperties": {"private": {"ronaldoId": item["id"]}}}


def tupla(item):
    return [item.get("data", ""), item.get("hora", ""), item.get("titulo", ""), item.get("local", "")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    sim = ap.parse_args().simular
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        creds = google_pessoal.credenciais()
    except SystemExit as e:  # token vencido (app em teste vence a cada 7 dias) ou revogado
        estado = ler_json(ESTADO, {"mapa": {}})
        hoje_txt = date.today().isoformat()
        if estado.get("aviso_desconexao") != hoje_txt and not sim:
            avisar.carregar_env()
            avisar.enviar("🔌 A conexão com o Google Agenda venceu. Quando estiver no computador, me peça para reconectar: leva 1 minuto. Enquanto isso, o resto continua funcionando.")
            estado["aviso_desconexao"] = hoje_txt
            ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
        sys.exit(str(e))
    servico = build("calendar", "v3", credentials=creds, cache_discovery=False)
    hoje = date.today()
    ontem = (hoje - timedelta(days=1)).isoformat()
    inicio = datetime.combine(hoje - timedelta(days=1), time.min).astimezone()
    fim = datetime.combine(hoje + timedelta(days=90), time.min).astimezone()
    eventos = servico.events().list(calendarId="primary", timeMin=inicio.isoformat(), timeMax=fim.isoformat(),
                                    singleEvents=True, orderBy="startTime", showDeleted=True,
                                    maxResults=250).execute().get("items", [])

    agenda = ler_json(AGENDA, {"compromissos": [], "tarefas": []})
    por_id = {c["id"]: c for c in agenda.get("compromissos", [])}
    estado = ler_json(ESTADO, {"mapa": {}})
    mapa = estado["mapa"]
    vistos, mudou = set(), False

    for e in eventos:
        chave = (e.get("extendedProperties", {}).get("private", {}).get("ronaldoId")) or f"gcal-{e['id']}"
        vistos.add(chave)
        if e.get("status") == "cancelled":
            if chave in por_id:
                print(f"removido no Google: '{por_id[chave]['titulo']}' sai do agenda.json")
                del por_id[chave]
                mudou = True
            mapa.pop(chave, None)
            continue
        g = list(do_evento(e))
        item = por_id.get(chave)
        ant = mapa.get(chave, {}).get("snap")
        if item is None:
            print(f"novo no Google: '{g[2]}' ({g[0]} {g[1]}) entra no agenda.json")
            por_id[chave] = {"id": chave, "data": g[0], "hora": g[1], "titulo": g[2], "local": g[3], "origem": "google"}
            mudou = True
            final = g
        elif ant is None or g != ant:  # o Guilherme mexeu no Google (ou 1ª rodada): vale o Google
            if tupla(item) != g:
                print(f"mudou no Google: '{item['titulo']}' -> '{g[2]}' ({g[0]} {g[1]})")
                item.update({"data": g[0], "hora": g[1], "titulo": g[2], "local": g[3]})
                mudou = True
            final = g
        elif tupla(item) != ant:  # só o agenda.json mudou: atualiza o Google
            print(f"atualizar no Google: '{item['titulo']}' ({item['data']} {item['hora']})")
            if not sim:
                servico.events().patch(calendarId="primary", eventId=e["id"], body=corpo_evento(item)).execute()
            final = tupla(item)
        else:
            final = g
        mapa[chave] = {"event": e["id"], "snap": final}

    for chave, item in list(por_id.items()):  # compromisso do agenda.json que ainda não existe no Google
        if chave in vistos or item.get("data", "") < ontem or item.get("origem") == "google":
            continue
        print(f"criar no Google: '{item['titulo']}' ({item['data']} {item['hora']})")
        if not sim:
            novo = servico.events().insert(calendarId="primary", body=corpo_evento(item)).execute()
            mapa[chave] = {"event": novo["id"], "snap": tupla(item)}

    if sim:
        return
    if mudou:
        atual = ler_json(AGENDA, agenda)  # relê logo antes de gravar (o Ronaldo pode ter editado)
        atual["compromissos"] = sorted(por_id.values(), key=lambda c: (c.get("data", ""), c.get("hora", "")))
        AGENDA.write_text(json.dumps(atual, ensure_ascii=False, indent=1), encoding="utf-8")
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
