"""Painel do Ronaldo: a central de controle no navegador (http://127.0.0.1:8766/).

Mostra o que o Ronaldo e os outros agentes já mantêm (agenda, tarefas, lembretes, finanças,
sprint da programação, consumo) e deixa o Guilherme dar ordens sem sair da tela:

  - caixa de comando: "@Pedri o que está parado?" funciona igual ao Telegram (mesmo roteamento,
    mesmos agentes, mesmas permissões, mesmo histórico de conversa);
  - marcar tarefa/compromisso como feito e criar tarefa, compromisso ou lembrete: direto nos
    arquivos, sem Claude e sem gastar token;
  - "Resumo do dia": o mesmo texto das 08:30, montado por `avisar.montar_resumo`, sem Claude.

Só biblioteca padrão. Só ouve em 127.0.0.1 (nunca na rede). Nada é publicado nem enviado a
ninguém: o painel não manda mensagem no Telegram. Dados que não existem aparecem como NÃO
CONECTADO (casa, Slack, e-mail e clima não têm integração): nunca se inventa status.

Uso:
  python produtividade/painel.py            sobe o painel e abre o navegador
  python produtividade/painel.py --sem-navegador
  python produtividade/painel.py --porta 8766
  python produtividade/painel.py --estado   imprime o estado (JSON) e sai, para teste
"""
import argparse
import csv
import json
import os
import re
import sys
import threading
import time
import unicodedata
import webbrowser
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import avisar
import ronaldo_telegram as rt
from avisar import DIAS, PASTA, RAIZ, ler_json

PORTA = 8766
HTML = PASTA / "painel.html"
AGENDA = PASTA / "agenda.json"
LEMBRETES = PASTA / "lembretes.json"
ORDENS = PASTA / ".ronaldo_painel_ordens.jsonl"  # coberto pelo .gitignore (produtividade/.ronaldo*)
QUADRO = RAIZ / "programacao" / "quadro.md"
MOVIMENTOS = RAIZ / "financas" / "movimentos.csv"

_trava_ordem = threading.Lock()
_trava_arquivo = threading.Lock()
_ocupado = {"agente": None, "desde": None, "pedido": ""}


# ---------- utilidades ----------

def idade(arq):
    """Segundos desde a última escrita do arquivo, ou None."""
    try:
        return time.time() - Path(arq).stat().st_mtime
    except OSError:
        return None


def ha(seg):
    if seg is None:
        return "sem registro"
    if seg < 90:
        return "agora há pouco"
    if seg < 5400:
        return f"há {int(seg // 60)} min"
    if seg < 172800:
        return f"há {int(seg // 3600)} h"
    return f"há {int(seg // 86400)} dias"


def salvar_json(arq, dados):
    tmp = arq.with_name(arq.name + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, arq)


def ler_ordens(limite=10):
    try:
        linhas = ORDENS.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    out = []
    for ln in linhas[-limite:]:
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            pass
    return out[::-1]


def registrar_ordem(reg):
    with ORDENS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")


# ---------- estado (somente leitura) ----------

def sec_agenda(agora):
    ag = ler_json(AGENDA, {})
    hoje = f"{agora:%Y-%m-%d}"
    fim = f"{agora + timedelta(days=7):%Y-%m-%d}"
    comp = sorted(ag.get("compromissos", []), key=lambda c: (c.get("data", ""), c.get("hora", "") or "99:99"))

    def enxuto(c):
        return {k: c.get(k, "") for k in ("id", "data", "hora", "titulo", "local", "emoji")} | {"feito": bool(c.get("feito"))}
    hoje_l = [enxuto(c) for c in comp if c.get("data") == hoje]
    prox_l = [enxuto(c) for c in comp if hoje < c.get("data", "") <= fim]
    proxima = None
    for c in comp:
        if c.get("feito") or c.get("data", "") < hoje:
            continue
        if c["data"] == hoje and c.get("hora") and c["hora"] < f"{agora:%H:%M}":
            continue
        if c.get("hora"):
            proxima = {"titulo": c["titulo"], "quando": f"{c['data']}T{c['hora']}:00"}
            break
    for c in hoje_l:
        c["emoji"] = c["emoji"] or avisar.emoji_de(c, "📌")
    for c in prox_l:
        c["emoji"] = c["emoji"] or avisar.emoji_de(c, "📌")
    return {"hoje": hoje_l, "proximos": prox_l, "proxima": proxima}


def sec_tarefas(agora):
    ag = ler_json(AGENDA, {})
    hoje = f"{agora:%Y-%m-%d}"
    fim = f"{agora + timedelta(days=7):%Y-%m-%d}"
    todas = ag.get("tarefas", [])
    pend = sorted((t for t in todas if not t.get("feito") and t.get("data")),
                  key=lambda t: (t["data"], t.get("hora", "") or "99:99"))
    feitas_hoje = [t for t in todas if t.get("feito") and t.get("data") == hoje]
    visiveis = [t for t in pend if t["data"] <= fim] + feitas_hoje

    def enxuto(t, pos):
        return {"id": t["id"], "titulo": t["titulo"], "data": t["data"], "hora": t.get("hora", ""), "obs": t.get("obs", ""),
                "feito": bool(t.get("feito")), "atrasada": (not t.get("feito")) and t["data"] < hoje,
                "emoji": avisar.emoji_de(t, "🔹"), "prioridade": (not t.get("feito")) and t["data"] <= hoje and pos < 3}
    itens, n = [], 0
    for t in visiveis:
        itens.append(enxuto(t, n))
        if not t.get("feito"):
            n += 1
    return {"itens": itens, "depois": sum(1 for t in pend if t["data"] > fim)}


def proxima_execucao(lem, agora):
    try:
        if lem.get("repete", "nunca") == "nunca":
            alvo = datetime.strptime(lem["quando"], "%Y-%m-%d %H:%M")
            return alvo if alvo >= agora else None
        h = datetime.strptime(lem["quando"], "%H:%M").time()
        alvo = datetime.combine(agora.date(), h)
        while alvo < agora or (lem["repete"] == "dias_uteis" and alvo.weekday() >= 5):
            alvo += timedelta(days=1)
        return alvo
    except (KeyError, ValueError):
        return None


def sec_lembretes(agora):
    lems = ler_json(LEMBRETES, {}).get("lembretes", [])
    prox = []
    for lem in lems:
        alvo = proxima_execucao(lem, agora)
        if alvo:
            prox.append((alvo, lem))
    prox.sort(key=lambda x: x[0])
    return {"total": len(lems),
            "recorrentes": sum(1 for lem in lems if lem.get("repete", "nunca") != "nunca"),
            "proximos": [{"id": lem["id"], "texto": lem.get("texto", "").split("\n")[0][:110], "agente": lem.get("agente", ""),
                          "quando": f"{a:%Y-%m-%dT%H:%M}", "repete": lem.get("repete", "nunca")} for a, lem in prox[:6]]}


def sec_financas(agora):
    try:
        with MOVIMENTOS.open(encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
    except FileNotFoundError:
        return {"estado": "offline", "detalhe": "financas/movimentos.csv não existe"}
    hoje = agora.date()
    ini = hoje - timedelta(days=29)
    recebido = gasto = a_pagar = 0.0
    por_dia = {}
    contas = []
    for r in linhas:
        try:
            d, v = date.fromisoformat(r["data"]), float(r["valor"])
        except (ValueError, KeyError):
            continue
        if r["status"] == "a pagar":
            a_pagar += v
            contas.append({"descricao": r["descricao"], "data": r["data"], "valor": v})
        elif r["status"] == "pago" and ini <= d <= hoje:
            if r["tipo"] == "recebido":
                recebido += v
            else:
                gasto += v
                por_dia[d] = por_dia.get(d, 0) + v
    serie = [round(por_dia.get(ini + timedelta(days=i), 0), 2) for i in range(30)]
    contas.sort(key=lambda c: c["data"])
    return {"estado": "ok", "recebido_30d": round(recebido, 2), "gasto_30d": round(gasto, 2), "a_pagar": round(a_pagar, 2),
            "contas": contas[:4], "serie_gasto_30d": serie, "atualizado": ha(idade(MOVIMENTOS))}


SECOES_QUADRO = [("Backlog da sprint", "Backlog"), ("Fazendo", "Fazendo"), ("Code Review", "Review"), ("Em teste", "Teste"),
                 ("Pronto para aceite", "Aceite"), ("Feito", "Feito"), ("Bloqueado", "Bloqueado")]


def sec_programacao():
    try:
        txt = QUADRO.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"estado": "offline", "detalhe": "programacao/quadro.md não existe"}
    contagem, bloqueados, atual = {}, [], None
    for ln in txt.splitlines():
        if ln.startswith("## "):
            atual = ln[3:].strip()
            continue
        m = re.match(r"^\s*(?:-|\d+\.)\s*\[(PROG-\d+)\]\s*(.*)$", ln)
        if m and atual:
            contagem[atual] = contagem.get(atual, 0) + 1
            if atual == "Bloqueado":
                bloqueados.append({"id": m.group(1), "titulo": re.split(r"[.·]", m.group(2), 1)[0].strip()[:70]})
    colunas = []
    for chave, rotulo in SECOES_QUADRO:
        n = sum(v for k, v in contagem.items() if k.startswith(chave))
        colunas.append({"rotulo": rotulo, "n": n})
    sprint = re.search(r"\((Sprint \d+),\s*(ABERTA|FECHADA)[^)]*\)", txt)
    return {"estado": "atencao" if bloqueados else "ok", "sprint": f"{sprint.group(1)} {sprint.group(2).lower()}" if sprint else "sem sprint",
            "colunas": colunas, "bloqueados": bloqueados[:3], "atualizado": ha(idade(QUADRO))}


def sec_consumo(agora):
    por_dia, hoje_n = {}, 0
    try:
        linhas = rt.CUSTO.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        linhas = []
    for ln in linhas:
        try:
            r = json.loads(ln)
            d = r["quando"][:10]
            por_dia[d] = por_dia.get(d, 0) + float(r.get("usd") or 0)
            if d == f"{agora:%Y-%m-%d}":
                hoje_n += 1
        except (ValueError, KeyError, TypeError):
            pass
    serie = [round(por_dia.get(f"{agora - timedelta(days=i):%Y-%m-%d}", 0), 4) for i in range(6, -1, -1)]
    mes = sum(v for d, v in por_dia.items() if d.startswith(f"{agora:%Y-%m}"))
    return {"hoje_usd": round(por_dia.get(f"{agora:%Y-%m-%d}", 0), 4), "mes_usd": round(mes, 4), "mensagens_hoje": hoje_n, "serie_7d": serie}


def sec_conexoes():
    vivo = ler_json(rt.VIVO, {})
    seg = time.time() - vivo.get("t", 0) if vivo.get("t") else None
    tg = {"id": "telegram", "nome": "TELEGRAM (Ronaldo ouvindo)", "estado": "ok" if seg is not None and seg < rt.TRAVADO_SEG else "offline",
          "detalhe": ha(seg) if seg is not None else "sem sinal"}
    out = [tg]
    s = idade(PASTA / ".google_agenda_estado.json")
    out.append({"id": "agenda", "nome": "GOOGLE AGENDA", "estado": "offline" if s is None else ("ok" if s < 1800 else "atencao"),
                "detalhe": ("sincronizado " + ha(s)) if s is not None else "sem registro"})
    s = idade(PASTA / ".trello_quadro.json")  # a data do arquivo é a da última mudança no quadro, não a da última sincronização
    out.append({"id": "trello", "nome": "TRELLO", "estado": "offline" if s is None else "ok",
                "detalhe": ("quadro mudou " + ha(s)) if s is not None else "sem registro"})
    return out


NAO_CONECTADO = [("CASA E IOT", "luzes, TV, robô aspirador"), ("SEGURANÇA", "alarme, câmeras"), ("SLACK", "mensagens"),
                 ("E-MAIL", "caixa de entrada")]

# ---------- clima (Open-Meteo: grátis, sem chave; só as coordenadas da cidade saem do computador) ----------
CLIMA_CFG = PASTA / ".ronaldo_painel_local.json"  # {"nome": "...", "lat": .., "lon": ..}; coberto pelo .gitignore
CLIMA_PADRAO = {"nome": "Jundiaí", "lat": -23.1857, "lon": -46.8978}  # suposição: a conta de água (DAE) é de Jundiaí
CLIMA_VALIDADE = 600  # segundos
_clima = {"t": 0.0, "dados": None}
WMO = {0: ("Céu limpo", "☀️", "🌙"), 1: ("Quase limpo", "🌤️", "🌙"), 2: ("Parcialmente nublado", "⛅", "☁️"), 3: ("Nublado", "☁️", "☁️"),
       45: ("Neblina", "🌫️", "🌫️"), 48: ("Neblina", "🌫️", "🌫️"), 51: ("Garoa fraca", "🌦️", "🌧️"), 53: ("Garoa", "🌦️", "🌧️"),
       55: ("Garoa forte", "🌧️", "🌧️"), 61: ("Chuva fraca", "🌦️", "🌧️"), 63: ("Chuva", "🌧️", "🌧️"), 65: ("Chuva forte", "🌧️", "🌧️"),
       80: ("Pancadas de chuva", "🌦️", "🌧️"), 81: ("Pancadas fortes", "🌧️", "🌧️"), 82: ("Pancadas violentas", "⛈️", "⛈️"),
       95: ("Tempestade", "⛈️", "⛈️"), 96: ("Tempestade com granizo", "⛈️", "⛈️"), 99: ("Tempestade com granizo", "⛈️", "⛈️")}


def wmo(codigo, dia=True):
    nome, e_dia, e_noite = WMO.get(codigo, ("Tempo variável", "🌡️", "🌡️"))
    return nome, e_dia if dia else e_noite


def buscar_clima(local):
    import urllib.parse
    import urllib.request
    q = urllib.parse.urlencode({
        "latitude": local["lat"], "longitude": local["lon"], "timezone": "America/Sao_Paulo", "forecast_days": 2,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day",
        "hourly": "temperature_2m,precipitation_probability,weather_code,is_day",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset"})
    with urllib.request.urlopen("https://api.open-meteo.com/v1/forecast?" + q, timeout=8) as r:
        d = json.load(r)
    cur, hor, dia = d["current"], d["hourly"], d["daily"]
    cond, emoji = wmo(cur["weather_code"], bool(cur["is_day"]))
    i0 = max(0, next((i for i, t in enumerate(hor["time"]) if t >= cur["time"][:13] + ":00"), 0))
    horas = []
    for i in range(i0 + 1, min(i0 + 13, len(hor["time"])), 2):  # próximas 12 h, de 2 em 2
        horas.append({"h": hor["time"][i][11:13] + "h", "temp": round(hor["temperature_2m"][i]), "chuva": hor["precipitation_probability"][i],
                      "emoji": wmo(hor["weather_code"][i], bool(hor["is_day"][i]))[1]})
    return {"estado": "ok", "local": local["nome"], "atualizado": cur["time"][11:16], "temp": round(cur["temperature_2m"]),
            "sensacao": round(cur["apparent_temperature"]), "umidade": cur["relative_humidity_2m"], "vento": round(cur["wind_speed_10m"]),
            "condicao": cond, "emoji": emoji, "max": round(dia["temperature_2m_max"][0]), "min": round(dia["temperature_2m_min"][0]),
            "chuva_hoje": dia["precipitation_probability_max"][0], "chuva_amanha": dia["precipitation_probability_max"][1],
            "max_amanha": round(dia["temperature_2m_max"][1]), "nascer": dia["sunrise"][0][11:16], "por": dia["sunset"][0][11:16], "horas": horas}


_clima_busca = threading.Lock()


def _atualizar_clima():
    """Roda em segundo plano para nunca travar o painel. Falhou: guarda o erro e tenta de novo em 1 min."""
    cfg = ler_json(CLIMA_CFG, {})
    local = {**CLIMA_PADRAO, **{k: cfg[k] for k in ("nome", "lat", "lon") if k in cfg}}
    try:
        _clima.update(t=time.time(), dados=buscar_clima(local), erro=None, local=local["nome"])
    except Exception as e:  # noqa: BLE001  sem internet ou API fora do ar
        _clima.update(t=time.time() - CLIMA_VALIDADE + 60, erro=f"Open-Meteo sem resposta ({type(e).__name__})", local=local["nome"])
    finally:
        _clima_busca.release()


def sec_clima():
    if time.time() - _clima["t"] >= CLIMA_VALIDADE and _clima_busca.acquire(blocking=False):
        threading.Thread(target=_atualizar_clima, daemon=True).start()
    if _clima["dados"]:  # erro ao atualizar: continua mostrando o último dado, marcado como desatualizado
        return {**_clima["dados"], "desatualizado": bool(_clima.get("erro"))}
    if _clima.get("erro"):
        return {"estado": "offline", "local": _clima.get("local", CLIMA_PADRAO["nome"]), "detalhe": _clima["erro"]}
    return {"estado": "carregando", "local": CLIMA_PADRAO["nome"]}


def estado():
    agora = datetime.now()
    out = {"agora": f"{agora:%Y-%m-%dT%H:%M:%S}", "dia_semana": DIAS[agora.weekday()], "ocupado": dict(_ocupado)}
    secoes = {"agenda": lambda: sec_agenda(agora), "tarefas": lambda: sec_tarefas(agora), "lembretes": lambda: sec_lembretes(agora),
              "financas": lambda: sec_financas(agora), "programacao": sec_programacao, "consumo": lambda: sec_consumo(agora),
              "conexoes": sec_conexoes, "clima": sec_clima}
    for nome, fn in secoes.items():
        try:
            out[nome] = fn()
        except Exception as e:  # noqa: BLE001  uma seção quebrada não derruba o painel
            out[nome] = {"estado": "offline", "detalhe": f"erro ao ler: {e!r}"[:120]}
    out["agentes"] = [{"chave": k, "nome": v["nome"], "segundo_plano": bool(v.get("segundo_plano"))} for k, v in rt.AGENTES.items()]
    out["nao_conectado"] = [{"nome": n, "detalhe": d} for n, d in NAO_CONECTADO]
    out["recentes"] = ler_ordens(8)
    return out


# ---------- ações ----------

class Erro(Exception):
    def __init__(self, msg, codigo=400):
        super().__init__(msg)
        self.codigo = codigo


def validar_data(txt, obrigatoria=True):
    txt = (txt or "").strip()
    if not txt and not obrigatoria:
        return ""
    try:
        datetime.strptime(txt, "%Y-%m-%d")
    except ValueError:
        raise Erro("Data inválida (use AAAA-MM-DD).") from None
    return txt


def validar_hora(txt):
    txt = (txt or "").strip()
    if not txt:
        return ""
    try:
        datetime.strptime(txt, "%H:%M")
    except ValueError:
        raise Erro("Hora inválida (use HH:MM).") from None
    return txt


def slug(txt):
    sem_acento = unicodedata.normalize("NFKD", txt.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento).strip("-")[:32] or "item"


def marcar_feito(corpo):
    tipo, id_, feito = corpo.get("tipo"), corpo.get("id"), bool(corpo.get("feito"))
    chave = {"tarefa": "tarefas", "compromisso": "compromissos"}.get(tipo)
    if not chave or not id_:
        raise Erro("Pedido incompleto.")
    with _trava_arquivo:
        ag = ler_json(AGENDA, None)
        if ag is None:
            raise Erro("agenda.json ilegível; nada foi mudado.", 500)
        for it in ag.get(chave, []):
            if it.get("id") == id_:
                if feito:
                    it["feito"] = True
                else:
                    it.pop("feito", None)
                salvar_json(AGENDA, ag)
                return {"ok": True}
    raise Erro("Item não encontrado.", 404)


def adicionar(corpo):
    tipo = corpo.get("tipo")
    titulo = " ".join(str(corpo.get("titulo", "")).split())[:140]
    if not titulo:
        raise Erro("Escreva um título.")
    agora = datetime.now()
    if tipo in ("tarefa", "compromisso"):
        data = validar_data(corpo.get("data") or f"{agora:%Y-%m-%d}")
        hora = validar_hora(corpo.get("hora"))
        with _trava_arquivo:
            ag = ler_json(AGENDA, None)
            if ag is None:
                raise Erro("agenda.json ilegível; nada foi mudado.", 500)
            lista = ag.setdefault("tarefas" if tipo == "tarefa" else "compromissos", [])
            base = f"painel-{slug(titulo)}-{data}" + (f"-{hora.replace(':', '')}" if hora else "")
            ids = {x.get("id") for x in lista}
            id_, n = base, 2
            while id_ in ids:
                id_, n = f"{base}-{n}", n + 1
            item = {"id": id_, "titulo": titulo, "data": data, "hora": hora, "origem": "Painel"}
            if tipo == "compromisso":
                item["local"] = " ".join(str(corpo.get("local", "")).split())[:80]
            elif corpo.get("obs"):
                item["obs"] = " ".join(str(corpo["obs"]).split())[:140]
            lista.append(item)
            salvar_json(AGENDA, ag)
        return {"ok": True, "id": id_}
    if tipo == "lembrete":
        data = validar_data(corpo.get("data") or f"{agora:%Y-%m-%d}")
        hora = validar_hora(corpo.get("hora"))
        if not hora:
            raise Erro("Lembrete precisa de hora.")
        quando = f"{data} {hora}"
        if datetime.strptime(quando, "%Y-%m-%d %H:%M") <= agora:
            raise Erro("Essa hora já passou. Escolha uma hora futura.")
        with _trava_arquivo:
            dados = ler_json(LEMBRETES, None)
            if dados is None:
                raise Erro("lembretes.json ilegível; nada foi mudado.", 500)
            lista = dados.setdefault("lembretes", [])
            base = f"painel-{slug(titulo)}-{data}-{hora.replace(':', '')}"
            ids = {x.get("id") for x in lista}
            id_, n = base, 2
            while id_ in ids:
                id_, n = f"{base}-{n}", n + 1
            lista.append({"id": id_, "agente": "Ronaldo", "texto": titulo, "quando": quando, "repete": "nunca"})
            salvar_json(LEMBRETES, dados)
        return {"ok": True, "id": id_}
    raise Erro("Tipo desconhecido.")


def dar_ordem(corpo):
    texto = str(corpo.get("texto", "")).strip()[:1500]
    if not texto:
        raise Erro("Escreva a ordem.")
    chave, resto = rt.rotear(texto)
    ag = rt.AGENTES[chave]
    if not resto:
        return {"agente": ag["nome"], "chave": chave, "resposta": rt.AJUDA if chave == "ronaldo" else f"{ag['nome']} por aqui. Escreva o pedido depois do nome.\n\n{rt.DICAS.get(chave, '')}".strip(), "segundos": 0}
    if ag.get("segundo_plano"):
        return {"agente": ag["nome"], "chave": chave, "segundos": 0,
                "resposta": f"{ag['nome']} trabalha pelo Claude Remote (app do Claude no celular, sessão 'Ecossistema'), não por aqui."}
    if not _trava_ordem.acquire(blocking=False):
        raise Erro(f"Ainda estou processando outra ordem ({_ocupado['agente']}). Aguarde terminar.", 409)
    t0 = time.time()
    try:
        _ocupado.update(agente=ag["nome"], desde=f"{datetime.now():%H:%M:%S}", pedido=resto[:60])
        try:
            resposta = rt.perguntar_claude(chave, resto, datetime.now())
            ok = True
        except Exception as e:  # noqa: BLE001
            resposta, ok = f"Não consegui concluir a ordem: {str(e)[:200]}", False
    finally:
        _ocupado.update(agente=None, desde=None, pedido="")
        _trava_ordem.release()
    seg = round(time.time() - t0, 1)
    registrar_ordem({"quando": f"{datetime.now():%Y-%m-%dT%H:%M:%S}", "agente": ag["nome"], "pedido": resto[:140],
                     "resposta": resposta[:400], "segundos": seg, "ok": ok})
    return {"agente": ag["nome"], "chave": chave, "resposta": resposta, "segundos": seg, "ok": ok}


# ---------- servidor ----------

class Painel(BaseHTTPRequestHandler):
    server_version = "PainelRonaldo/1"

    def log_message(self, *a):  # silencioso
        pass

    def _enviar(self, codigo, corpo, tipo="application/json; charset=utf-8"):
        dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'")
        self.end_headers()
        self.wfile.write(dados)

    def _host_ok(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def _post_ok(self):
        origem = self.headers.get("Origin")
        if origem and urlparse(origem).hostname not in ("127.0.0.1", "localhost"):
            return False
        return self.headers.get("X-Painel") == "1"

    def do_GET(self):
        if not self._host_ok():
            return self._enviar(403, {"erro": "host não permitido"})
        caminho = urlparse(self.path).path
        if caminho in ("/", "/index.html"):
            try:
                return self._enviar(200, HTML.read_bytes(), "text/html; charset=utf-8")
            except FileNotFoundError:
                return self._enviar(500, {"erro": "painel.html não encontrado"})
        if caminho == "/api/estado":
            return self._enviar(200, estado())
        if caminho == "/api/resumo":
            return self._enviar(200, {"resposta": avisar.montar_resumo(datetime.now()), "agente": "Ronaldo"})
        self._enviar(404, {"erro": "não encontrado"})

    def do_POST(self):
        if not self._host_ok() or not self._post_ok():
            return self._enviar(403, {"erro": "pedido não permitido"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 20_000:
                raise Erro("Pedido grande demais.", 413)
            corpo = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(corpo, dict):
                raise Erro("Formato inválido.")
            rota = {"/api/feito": marcar_feito, "/api/adicionar": adicionar, "/api/ordem": dar_ordem}.get(urlparse(self.path).path)
            if not rota:
                raise Erro("não encontrado", 404)
            self._enviar(200, rota(corpo))
        except Erro as e:
            self._enviar(e.codigo, {"erro": str(e)})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._enviar(400, {"erro": "JSON inválido."})
        except Exception as e:  # noqa: BLE001
            rt.log(f"painel: erro em {self.path}: {e!r}")
            self._enviar(500, {"erro": "Erro interno; veja produtividade/.ronaldo.log"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--porta", type=int, default=PORTA)
    ap.add_argument("--sem-navegador", action="store_true")
    ap.add_argument("--estado", action="store_true")
    args = ap.parse_args()
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    if args.estado:
        print(json.dumps(estado(), ensure_ascii=False, indent=1))
        return
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", args.porta), Painel)
    except OSError:
        url = f"http://127.0.0.1:{args.porta}/"
        print(f"Já tem algo na porta {args.porta}. Provavelmente o painel já está aberto: {url}")
        if not args.sem_navegador:
            webbrowser.open(url)
        return
    url = f"http://127.0.0.1:{args.porta}/"
    print(f"Painel do Ronaldo em {url}  (Ctrl+C para fechar)")
    if not args.sem_navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
