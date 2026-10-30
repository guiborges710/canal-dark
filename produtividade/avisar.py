"""Envia os lembretes de produtividade para o Telegram do Guilherme.

Rodado a cada minuto pelo Agendador de Tarefas do Windows. Lê
produtividade/lembretes.json (escrito pelo Ronaldo) e manda o que venceu.
Quem LÊ as mensagens do Guilherme é o ronaldo_telegram.py (só ele consome o
getUpdates do bot); a resposta "feito" chega aqui pelo arquivo .feitos.json.

Credenciais ficam só no .env: TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.

Uso:
  python produtividade/avisar.py                 roda um ciclo (é o que o agendador chama)
  python produtividade/avisar.py --teste         manda uma mensagem de teste
  python produtividade/avisar.py --descobrir-chat  mostra o chat id (mande antes uma mensagem ao bot)
  python produtividade/avisar.py --simular       mostra o que seria enviado, sem enviar
  python produtividade/avisar.py --resumo        manda agora o resumo do dia (o de 08:30 sai sozinho)
"""
import argparse
import json
import os
import re
import socket
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# O IPv6 desta rede até o Telegram falha na maioria das vezes e cada falha espera 21 s antes de cair no IPv4
# (medido em 30/10/2026: um áudio levou 1,5 min para ser respondido). Para o Telegram, só IPv4.
_getaddrinfo = socket.getaddrinfo


def _so_ipv4_no_telegram(host, *args, **kwargs):
    infos = _getaddrinfo(host, *args, **kwargs)
    if isinstance(host, str) and host.endswith("telegram.org"):
        return [i for i in infos if i[0] == socket.AF_INET] or infos
    return infos


socket.getaddrinfo = _so_ipv4_no_telegram

RAIZ = Path(__file__).resolve().parent.parent
PASTA = Path(__file__).resolve().parent
LEMBRETES = PASTA / "lembretes.json"
ESTADO = PASTA / ".estado_avisos.json"
FEITOS = PASTA / ".feitos.json"  # escrito pelo ronaldo_telegram.py
ATRASO_MAX_RECORRENTE = timedelta(minutes=90)  # PC dormiu? não manda aviso velho demais
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]

# emoji por palavra-chave, quando o item não traz "emoji" próprio
EMOJIS = [
    (("mãe", "mae", "buscar", "carro", "uber"), "🚗"),
    (("show", "festival", "música", "musica", "cinema"), "🎤"),
    (("academia", "treino", "corrida"), "🏋️"),
    (("café", "cafe", "almoço", "almoco", "jantar", "lanche"), "☕"),
    (("conta", "pagar", "boleto", "fatura", "luz", "água", "agua", "internet"), "💳"),
    (("reunião", "reuniao", "call"), "👥"),
    (("médico", "medico", "consulta", "dentista", "exame"), "🩺"),
    (("seguro", "tarefa", "projeto", "trabalho", "deploy", "sprint"), "💼"),
    (("senha", "acesso"), "🔐"),
    (("linkedin", "post"), "✍️"),
]


def carregar_env():
    arq = RAIZ / ".env"
    if not arq.exists():
        return
    for linha in arq.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def telegram(metodo, **params):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        sys.exit("TELEGRAM_BOT_TOKEN não está no .env")
    dados = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/{metodo}", dados, timeout=70) as r:
        return json.load(r)


def enviar(texto):
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not chat:
        sys.exit("TELEGRAM_CHAT_ID não está no .env (rode --descobrir-chat)")
    for i in range(0, len(texto), 4000):  # limite do Telegram: 4096 por mensagem
        telegram("sendMessage", chat_id=chat, text=texto[i:i + 4000])


def enviar_foto(caminho, legenda=""):
    """sendPhoto (multipart) para o chat do Guilherme."""
    return enviar_arquivo(caminho, legenda, "photo", "sendPhoto", "image/png")


def enviar_arquivo(caminho, legenda="", campo="video", metodo="sendVideo", tipo="video/mp4"):
    """Envio multipart (foto, vídeo, documento) para o chat do Guilherme."""
    import uuid
    chat = os.environ["TELEGRAM_CHAT_ID"]
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    lim = uuid.uuid4().hex
    crlf = "\r\n"
    corpo = b""
    for nome, valor in (("chat_id", chat), ("caption", legenda[:1000])):
        corpo += (f'--{lim}{crlf}Content-Disposition: form-data; name="{nome}"{crlf}{crlf}{valor}{crlf}').encode()
    corpo += (f'--{lim}{crlf}Content-Disposition: form-data; name="{campo}"; filename="{Path(caminho).name}"{crlf}'
              f'Content-Type: {tipo}{crlf}{crlf}').encode()
    corpo += Path(caminho).read_bytes() + f"{crlf}--{lim}--{crlf}".encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}", data=corpo,
                                 headers={"Content-Type": f"multipart/form-data; boundary={lim}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def ler_json(arq, padrao):
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def venceu(lem, agora, estado):
    """Devolve a chave de envio se o lembrete deve sair agora, senão None."""
    quando = lem["quando"]
    repete = lem.get("repete", "nunca")
    if repete == "nunca":
        alvo = datetime.strptime(quando, "%Y-%m-%d %H:%M")
        chave = f"{lem['id']}|{alvo:%Y-%m-%d %H:%M}"
        if agora - alvo > timedelta(days=7):
            return None  # velho demais: não reenviar quando o histórico de enviados for podado
        return chave if agora >= alvo and chave not in estado["enviados"] else None
    if repete == "dias_uteis" and agora.weekday() >= 5:
        return None
    hora = datetime.strptime(quando, "%H:%M").time()
    alvo = datetime.combine(agora.date(), hora)
    chave = f"{lem['id']}|{agora:%Y-%m-%d}"
    if not (alvo <= agora <= alvo + ATRASO_MAX_RECORRENTE) or chave in estado["enviados"]:
        return None
    grupo = lem.get("grupo")
    if grupo and f"{grupo}|{agora:%Y-%m-%d}" in estado["feitos"]:
        return None
    return chave


_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍]+")


def emoji_no_fim(texto):
    """Tira os emojis do começo e os põe no fim: a prévia da notificação (relógio) fica só com texto."""
    emojis = "".join(_EMOJI.findall(texto))
    limpo = " ".join(_EMOJI.sub("", texto).split())
    return f"{limpo} {emojis}".strip() if emojis else texto


def emoji_de(item, padrao):
    if item.get("emoji"):
        return item["emoji"]
    titulo = item.get("titulo", "").lower()
    for palavras, emoji in EMOJIS:
        if any(p in titulo for p in palavras):
            return emoji
    return padrao


SEPARADOR = "──────────────"


def montar_resumo(agora):
    """Resumo do dia a partir de agenda.json (escrito pelo Ronaldo). Sem Claude, sem token."""
    agenda = ler_json(PASTA / "agenda.json", {})
    hoje = f"{agora:%Y-%m-%d}"
    if agora.hour < 12:
        saudacao, sol = "Bom dia", "☀️"
    elif agora.hour < 18:
        saudacao, sol = "Boa tarde", "🌤️"
    else:
        saudacao, sol = "Boa noite", "🌙"
    linhas = [f"{sol} {saudacao}, Guilherme!", f"{DIAS[agora.weekday()].capitalize()}, {agora:%d/%m}", "", SEPARADOR, ""]

    comp = sorted((c for c in agenda.get("compromissos", []) if c["data"] == hoje), key=lambda c: c.get("hora", ""))
    linhas.append("📅 COMPROMISSOS")
    if comp:
        for c in comp:
            quando = f"⏰ {c['hora']}" if c.get("hora") else "📆 dia todo"
            linhas += ["", f"{quando}  {emoji_de(c, '📌')} {c['titulo']}"]
            if c.get("local"):
                linhas.append(f"📍 Local: {c['local']}")
    else:
        linhas += ["", "Nada marcado hoje 🎉"]

    tarefas = [t for t in agenda.get("tarefas", []) if t.get("data") and t["data"] <= hoje]
    tarefas = [t for t in tarefas if not t.get("feito") or t["data"] == hoje]
    pendentes = sorted((t for t in tarefas if not t.get("feito")), key=lambda t: (t["data"], t.get("hora", "")))
    feitas = [t for t in tarefas if t.get("feito")]
    if tarefas:
        linhas += ["", SEPARADOR, "", f"📝 PARA HOJE · {len(feitas)} de {len(tarefas)} feitas"]
        if pendentes:
            linhas += ["", "A FAZER"]  # o estado vai em palavras, não só em emoji (relógio)
        for t in pendentes:
            hora = f" · {t['hora']}" if t.get("hora") else ""
            atraso = " · ATRASADA 🔴" if t["data"] < hoje else ""
            linhas += ["", f"⏳ {emoji_de(t, '🔹')} {t['titulo']}{hora}{atraso}"]
            if t.get("obs"):
                linhas.append(f"      {t['obs']}")
        if feitas:
            linhas += ["", "JÁ FEITAS"]
            linhas += [f"✅ {emoji_de(t, '🔹')} {t['titulo']}" for t in feitas]

    if agora.weekday() < 5:
        linhas += ["", SEPARADOR, "", "⏰ Apontamento de horas: aviso às 17:30"]
    # 1ª linha só com texto: o relógio mostra a prévia da notificação e não desenha emoji
    n_c, n_p = len(comp), sum(1 for t in tarefas if not t.get("feito"))
    manchete = (f"Resumo de {DIAS[agora.weekday()]}, {agora:%d/%m}: {n_c} compromisso{'s' if n_c != 1 else ''}"
                f" e {n_p} tarefa{'s' if n_p != 1 else ''} pendente{'s' if n_p != 1 else ''}")
    return manchete + "\n\n" + "\n".join(linhas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", action="store_true")
    ap.add_argument("--descobrir-chat", action="store_true")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--resumo", action="store_true", help="manda agora o resumo do dia")
    args = ap.parse_args()
    carregar_env()
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")

    if args.resumo:
        texto = montar_resumo(datetime.now())
        print(texto)
        if not args.simular:
            enviar(texto)
        return
    if args.descobrir_chat:
        for upd in telegram("getUpdates").get("result", []):
            c = upd.get("message", {}).get("chat")
            if c:
                print("chat id:", c["id"], "| nome:", c.get("first_name", ""))
        return
    if args.teste:
        enviar("Teste do setor de produtividade: se você leu isso, o aviso no celular funciona.")
        print("enviado")
        return

    agora = datetime.now()
    estado = ler_json(ESTADO, {})
    estado.setdefault("enviados", {})
    estado.setdefault("feitos", {})
    estado["feitos"].update(ler_json(FEITOS, {}))

    for lem in ler_json(LEMBRETES, {}).get("lembretes", []):
        chave = venceu(lem, agora, estado)
        if not chave:
            continue
        if lem.get("tipo") == "resumo_dia":
            texto = montar_resumo(agora)
        else:
            rotulo = lem.get("agente", "")
            texto = (f"{rotulo}: " if rotulo else "") + emoji_no_fim(lem["texto"])
        if lem.get("grupo"):
            texto += "\n(responda 'feito' para parar os avisos de hoje)"
        print(("SIMULADO: " if args.simular else "enviando: ") + texto)
        if not args.simular:
            enviar(texto)
            estado["enviados"][chave] = agora.isoformat(timespec="seconds")
            estado["ultimo_grupo"] = lem.get("grupo")

    # aviso automático 1 hora antes de cada compromisso com hora (inclui os que vêm do Google Agenda)
    hoje = f"{agora:%Y-%m-%d}"
    for c in ler_json(PASTA / "agenda.json", {}).get("compromissos", []):
        if c.get("data") != hoje or not c.get("hora"):
            continue
        inicio = datetime.strptime(f"{hoje} {c['hora']}", "%Y-%m-%d %H:%M")
        chave = f"comp|{c['id']}|{hoje} {c['hora']}"
        if inicio - timedelta(hours=1) <= agora < inicio and chave not in estado["enviados"]:
            texto = (f"Daqui a 1 hora, às {c['hora']}: {c['titulo']}" + (f" (local: {c['local']})" if c.get("local") else "")
                     + f" ⏰ {emoji_de(c, '📌')}")
            print(("SIMULADO: " if args.simular else "enviando: ") + texto)
            if not args.simular:
                enviar(texto)
                estado["enviados"][chave] = agora.isoformat(timespec="seconds")

    limite = (agora - timedelta(days=60)).isoformat()
    estado["enviados"] = {k: v for k, v in estado["enviados"].items() if v >= limite}
    if not args.simular:
        ESTADO.write_text(json.dumps(estado, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
