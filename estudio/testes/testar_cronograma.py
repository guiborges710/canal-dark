"""PROG-011 (entrega 1, só leitura): confere estudio/cronograma.py e a rota GET /api/cronograma em pasta temporária.
Nunca toca em output/ real. Uso: .venv\\Scripts\\python estudio\\testes\\testar_cronograma.py"""
import hashlib
import json
import os
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="cronograma_"))
os.environ["ESTUDIO_RAIZ"] = str(TMP / "raiz")
os.environ["ESTUDIO_DADOS"] = str(TMP / "dados")
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import cronograma as C  # noqa: E402

SAIDA = TMP / "raiz" / "output"
SAIDA.mkdir(parents=True)
(TMP / "dados").mkdir()
passou, falhas = 0, []


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}", flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def pasta(slug, pronto=True, titulo="T", auditoria="APROVADO", video=True, roteiro=True):
    p = SAIDA / slug
    p.mkdir(parents=True, exist_ok=True)
    if roteiro:
        (p / "roteiro.txt").write_text("oi", encoding="utf-8")
    if video:
        (p / "video.mp4").write_bytes(b"x")
    if auditoria and video:
        (p / "auditoria.md").write_text(f"# Auditoria\nVeredito: {auditoria}\n", encoding="utf-8")
    if pronto and video:
        (p / "thumbnail.jpg").write_bytes(b"x")
    if titulo is not None:
        (p / "metadados.json").write_text(json.dumps({"titulo": titulo}), encoding="utf-8")


def fila(*slugs):
    (SAIDA / "fila_postagem.txt").write_text("\n".join(slugs) + "\n", encoding="utf-8")


def limpa():
    import shutil
    for d in SAIDA.iterdir():
        shutil.rmtree(d) if d.is_dir() else d.unlink()


def hash_saida():
    h = hashlib.sha256()
    for f in sorted(SAIDA.rglob("*")):
        if f.is_file():
            h.update(f.name.encode() + f.read_bytes() + str(f.stat().st_mtime_ns).encode())
    return h.hexdigest()


AGORA = datetime(2026, 12, 1, 10, 0)  # terça
DIARIA = {"dias": "todos", "hora": "18:00"}
SEG_QUA_SEX = {"dias": ["seg", "qua", "sex"], "hora": "18:00"}

print("T1/T2 fila com vários vídeos, ordem da fila")
pasta("a", titulo="Vídeo A")
pasta("b", titulo="Vídeo B")
pasta("c", titulo="Vídeo C")
fila("c", "a", "b")
h0 = hash_saida()
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
ls = [x for x in r["linhas"] if x["slug"]]
confere([x["slug"] for x in ls] == ["c", "a", "b"], "ordem segue a fila", [x["slug"] for x in ls])
confere([x["data"] for x in ls] == ["2026-12-01", "2026-12-02", "2026-12-03"], "1 vídeo por dia, a partir de hoje (18h ainda não passou)", [x["data"] for x in ls])
confere(ls[0]["titulo"] == "Vídeo C" and all(x["hora"] == "18:00" for x in ls), "título e hora")
confere(all(x["status_texto"] for x in ls), "status em texto")
confere(all(x["status"] == "na_fila" for x in ls) and not any(x["alerta"] for x in ls), "tudo pronto, sem alerta")
confere(r["proxima"]["texto"] == "Pronto para postar", "topo: pronto", r["proxima"])
fila("b", "c", "a")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere([x["slug"] for x in r["linhas"] if x["slug"]] == ["b", "c", "a"], "reordenar o arquivo muda o cronograma")

print("T3/T23 título ausente ou inválido")
pasta("semmeta", titulo=None)
(SAIDA / "invalido").mkdir()
(SAIDA / "invalido" / "metadados.json").write_text("{quebrado", encoding="utf-8")
(SAIDA / "invalido" / "roteiro.txt").write_text("x", encoding="utf-8")
fila("semmeta", "invalido")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere([x["titulo"] for x in r["linhas"] if x["slug"]] == ["sem título", "sem título"], "sem título, sem erro")

print("T8/T9 vídeo sem auditoria / sem vídeo no topo")
pasta("semaud", auditoria=None)
fila("semaud", "a")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(r["proxima"]["texto"].startswith("Sem vídeo pronto para 01/12"), "topo: sem vídeo pronto", r["proxima"])
confere("auditoria APROVADA" in r["proxima"]["texto"], "cita a auditoria", r["proxima"])
confere(r["proxima"]["pronto"] is False and r["linhas"][0]["alerta"] is True, "alerta no slot de hoje")
pasta("semvideo", video=False)
fila("semvideo")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere("video.mp4" in r["proxima"]["texto"], "cita o vídeo que falta", r["proxima"])

print("T10-T12/T19/T20 fronteira do alerta (menos de 2 dias corridos)")
fila("semaud")
sem = {"dias": "todos", "hora": "18:00"}
r = C.calcular(datetime(2026, 12, 1, 19, 0), sem, saida=SAIDA)  # hoje já passou das 18h: slot é amanhã (1 dia)
confere(r["linhas"][0]["data"] == "2026-12-02" and r["linhas"][0]["alerta"], "1 dia, sem vídeo = alerta", r["linhas"][0])
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(r["linhas"][0]["data"] == "2026-12-01" and r["linhas"][0]["alerta"], "0 dias (hoje) = alerta")
r = C.calcular(AGORA, {"dias": ["qui"], "hora": "18:00"}, saida=SAIDA)  # próxima quinta = 03/12 (2 dias)
confere(r["linhas"][0]["data"] == "2026-12-03" and not r["linhas"][0]["alerta"], "2 dias = sem alerta", r["linhas"][0])
r = C.calcular(AGORA, {"dias": ["sex"], "hora": "18:00"}, saida=SAIDA)  # 04/12 (3 dias)
confere(r["linhas"][0]["data"] == "2026-12-04" and not r["linhas"][0]["alerta"], "3 dias = sem alerta")
fila("a")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(not r["linhas"][0]["alerta"], "vídeo pronto a 0 dias: sem alerta")
r = C.calcular(datetime(2026, 12, 31, 19, 0), DIARIA, saida=SAIDA)
confere(r["linhas"][0]["data"] == "2027-01-01", "virada de ano", r["linhas"][0]["data"])
fila("semaud")
r = C.calcular(datetime(2026, 12, 31, 19, 0), DIARIA, saida=SAIDA)
confere(r["linhas"][0]["alerta"], "virada de ano: 1 dia conta certo")

print("T11 cadência 3 por semana (seg, qua, sex)")
pasta("d")
fila("a", "b", "c", "d")
r = C.calcular(AGORA, SEG_QUA_SEX, saida=SAIDA)  # terça
confere([x["data"] for x in r["linhas"][:4]] == ["2026-12-02", "2026-12-04", "2026-12-07", "2026-12-09"], "seg/qua/sex", [x["data"] for x in r["linhas"][:4]])
r = C.calcular(datetime(2026, 12, 2, 18, 0), SEG_QUA_SEX, saida=SAIDA)  # quarta exatamente 18:00: já passou
confere(r["linhas"][0]["data"] == "2026-12-04", "no minuto do horário, o slot é o seguinte")
r = C.calcular(datetime(2026, 12, 2, 17, 59), SEG_QUA_SEX, saida=SAIDA)
confere(r["linhas"][0]["data"] == "2026-12-02", "um minuto antes, ainda vale hoje")

print("sem seção de cadência: assume 1/dia e avisa")
r = C.calcular(AGORA, None, saida=SAIDA)
confere(r["cadencia"]["assumida"] is True and r["linhas"][0]["data"] == "2026-12-01", "assunção 1/dia", r["cadencia"])
r = C.calcular(AGORA, {"dias": ["xyz"], "hora": "99:99"}, saida=SAIDA)
confere(r["cadencia"]["assumida"] is True and r["cadencia"]["aviso"], "cadência inválida cai na assunção, com aviso", r["cadencia"])

print("T15 fila vazia / T16 slug sem pasta / publicado fora")
fila()
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(r["proxima"]["texto"].startswith("Nenhum vídeo na fila"), "fila vazia", r["proxima"])
confere(all(x["slug"] is None for x in r["linhas"]) and r["linhas"], "slots vazios em linhas 'Sem vídeo na fila'")
confere("Sem vídeo na fila para" in r["linhas"][0]["titulo"], "texto do slot vazio", r["linhas"][0])
fila("fantasma", "a")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(r["linhas"][0]["slug"] == "fantasma" and "pasta não encontrada" in r["linhas"][0]["status_texto"].lower() and r["linhas"][0]["alerta"], "slug sem pasta: aviso e alerta", r["linhas"][0])
confere(r["linhas"][1]["slug"] == "a", "resto continua")
confere("pular fantasma" in r["proxima"]["envio"] and "subir a" in r["proxima"]["envio"], "avisa que o envio pula o bloqueado", r["proxima"])
(SAIDA / "a" / "upload.json").write_text(json.dumps({"privacy": "private", "url": "u"}), encoding="utf-8")
fila("a", "b")
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere([x["slug"] for x in r["linhas"] if x["slug"]] == ["b"], "já publicado não ocupa slot")

print("T21 fila com 50 itens")
for i in range(50):
    pasta(f"v{i:02d}")
fila(*[f"v{i:02d}" for i in range(50)])
r = C.calcular(AGORA, DIARIA, saida=SAIDA)
confere([x["slug"] for x in r["linhas"]] == [f"v{i:02d}" for i in range(50)], "50 itens, ordem preservada")

print("travas")
fonte = (REPO / "estudio" / "cronograma.py").read_text(encoding="utf-8")
confere("youtube" not in fonte and "postar_pendentes" not in fonte and "publish_at" not in fonte.lower(), "não importa nem cita youtube/postar_pendentes/publishAt")
confere("write_text" not in fonte and "open(" not in fonte, "módulo não escreve")
h1 = hash_saida()
C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(hash_saida() == h1, "calcular não altera output/ (conteúdo e data)")
fila("v00")
h2 = hash_saida()
C.calcular(AGORA, DIARIA, saida=SAIDA)
confere(hash_saida() == h2, "fila_postagem.txt intacta")

print("config_shorts.yaml real: sem seção, assume; com seção, lê")
cfg = TMP / "c.yaml"
cfg.write_text("cronograma:\n  dias: [seg, qua, sex]\n  hora: \"09:30\"\n", encoding="utf-8")
confere(C.ler_cadencia(cfg) == {"dias": ["seg", "qua", "sex"], "hora": "09:30"}, "lê a seção", C.ler_cadencia(cfg))
cfg.write_text("channel: {}\n", encoding="utf-8")
confere(C.ler_cadencia(cfg) is None, "sem seção = None")
confere(C.ler_cadencia(TMP / "nao_existe.yaml") is None, "sem arquivo = None")

print("rota GET /api/cronograma (só GET, mesmo porteiro das demais)")
from http.server import ThreadingHTTPServer  # noqa: E402
from estudio import servidor  # noqa: E402
fila("v00", "v01")
srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.Manipulador)
if srv is None:
    confere(False, "servidor.Manipulador existe")
else:
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        corpo = json.loads(urllib.request.urlopen(base + "/api/cronograma", timeout=10).read())
        confere("linhas" in corpo and "proxima" in corpo and "cadencia" in corpo, "GET devolve linhas/proxima/cadencia", list(corpo))
        confere(corpo["linhas"][0]["slug"] == "v00", "GET usa a fila da pasta de teste")
    except Exception as e:  # noqa: BLE001
        confere(False, "GET /api/cronograma", repr(e))
    try:
        req = urllib.request.Request(base + "/api/cronograma", data=b"{}", method="POST", headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        confere(False, "POST recusado")
    except urllib.error.HTTPError as e:
        confere(e.code in (400, 403, 404, 405), "POST recusado", e.code)
    srv.shutdown()

print(f"\n{passou} ok, {len(falhas)} falhas")
for f in falhas:
    print("  -", f)
sys.exit(1 if falhas else 0)
