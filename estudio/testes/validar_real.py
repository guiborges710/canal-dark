"""Validação com os comandos de verdade, sem simulador: Chatterbox, run.py (render real) e run.py --mock. Não chama agente nenhum,
então não consome nada pago. Leva alguns minutos de CPU. Grava só em pastas próprias de output/, apagadas no final.

Uso: python estudio/testes/validar_real.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PORTA = 8792
BASE = f"http://127.0.0.1:{PORTA}"
SLUG = "estudio-validacao-real"
MOCK = "mock-estudio-validacao"
PASTA = REPO / "output" / SLUG
FALAS = ["Esta é a primeira fala da validação do estúdio.", "E esta é a segunda fala, para testar o trecho separado."]
falhas = []


def api(metodo, rota, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + rota, data=dados, method=metodo, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def etapa(slug, i):
    return next(e for e in api("GET", f"/api/producoes/{slug}")[1]["etapas"] if e["id"] == i)


def confere(cond, nome, extra=""):
    print(f"  {'ok' if cond else 'FALHOU'}  {nome}{'' if cond else f' -> {extra}'}", flush=True)
    if not cond:
        falhas.append(nome)


def esperar_fim(slug, i, minutos=15):
    fim = time.time() + minutos * 60
    while time.time() < fim:
        e = etapa(slug, i)
        if e["status"] not in ("fila", "executando"):
            return e
        p = e.get("progresso") or {}
        print(f"    {e['nome']}: {p.get('passo') or ''} {p.get('detalhe') or ''} {str(p.get('porcentagem')) + '%' if p.get('porcentagem') is not None else ''}", flush=True)
        time.sleep(8)
    raise SystemExit(f"{i} não terminou em {minutos} min")


def semear():
    PASTA.mkdir()
    (PASTA / "notas.md").write_text("Pasta de validação do estúdio. Fontes: a, b, c.\n", encoding="utf-8")
    (PASTA / "angulo.md").write_text("Validação técnica.\n", encoding="utf-8")
    (PASTA / "roteiro.txt").write_text("\n\n".join(FALAS) + "\n", encoding="utf-8")
    (PASTA / "metadados.json").write_text(json.dumps({"titulo": "Validação real do estúdio", "descricao": "Teste.", "tags": ["teste"], "thumbnail_texto": "TESTE"}), encoding="utf-8")
    (PASTA / "auditoria_texto.md").write_text("**APROVADO** (validação técnica)\n", encoding="utf-8")
    (PASTA / "cenas.json").write_text(json.dumps([{"tipo": "sketch", "desenho": f"cena_{i}", "duracao": 11, "fala": f, "rotulos": [f"cena {i + 1}"], "sons": []} for i, f in enumerate(FALAS)], ensure_ascii=False), encoding="utf-8")
    (PASTA / "sketch_cenas.py").write_text("from media.sketch_lib import *\n\n\ndef cena_0(lt, dur):\n    return papel()\n\n\ndef cena_1(lt, dur):\n    return papel()\n", encoding="utf-8")


def tem_audio_e_formato(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height", "-of", "json", str(video)], capture_output=True, text=True)
    fluxos = json.loads(r.stdout)["streams"]
    v = next(s for s in fluxos if s["codec_type"] == "video")
    return any(s["codec_type"] == "audio" for s in fluxos), (v["width"], v["height"])


def principal():
    print("\n[Narração real, com a voz do canal]", flush=True)
    time.sleep(1)
    versao = etapa(SLUG, "roteiro")["versao_id"]
    confere(api("POST", f"/api/producoes/{SLUG}/aprovar", {"material": "roteiro", "versao_id": versao})[0] == 200, "aprova o roteiro")
    st, r = api("POST", f"/api/producoes/{SLUG}/iniciar", {"etapa": "narracao"})
    confere(st == 201, "inicia a narração", r)
    e = esperar_fim(SLUG, "narracao")
    confere(e["status"] == "aguardando" and e["total_itens"] == 2, "gerou 2 trechos reais", e)
    wav0 = (PASTA / "falas" / "00.wav").read_bytes()
    textos = json.loads((PASTA / "falas" / "textos.json").read_text(encoding="utf-8"))
    confere(textos == FALAS, "textos.json no contrato que o render reaproveita", textos)

    print("\n[Refazer só um trecho, com ajuste de voz]", flush=True)
    api("POST", f"/api/producoes/{SLUG}/item", {"material": "narracao", "versao_id": e["versao_id"], "item": "cena_0", "decisao": "aprovado"})
    (PASTA / "voz_ajustes.json").write_text(json.dumps({"1": {"velocidade": 1.0, "dizer": "E esta é a segunda fala, para testar o trecho separado, ajustada."}}, ensure_ascii=False), encoding="utf-8")
    st, r = api("POST", f"/api/producoes/{SLUG}/iniciar", {"etapa": "narracao", "forcar": True, "escopo": [1]})
    confere(st == 201, "pede só a cena 2", r)
    e = esperar_fim(SLUG, "narracao")
    confere(e["versao"] == 2 and e["pendentes"] == 1, "v2: a cena 1 segue aprovada, só a cena 2 volta para revisão", e)
    confere((PASTA / "falas" / "00.wav").read_bytes() == wav0, "o áudio da cena 1 não foi tocado")
    confere(json.loads((PASTA / "falas" / "textos.json").read_text(encoding="utf-8")) == FALAS, "a fala oficial não mudou por causa do ajuste de pronúncia")
    st, _ = api("POST", f"/api/producoes/{SLUG}/aprovar", {"material": "narracao", "versao_id": e["versao_id"]})
    confere(st == 200, "aprova a narração")

    print("\n[Render real: python run.py video]", flush=True)
    versao = etapa(SLUG, "cenas")
    st, r = api("POST", f"/api/producoes/{SLUG}/iniciar", {"etapa": "video", "forcar": True})
    confere(st == 201, "inicia o render", r)
    e = esperar_fim(SLUG, "video", 20)
    confere(e["status"] == "aguardando" and e["versao"] == 1, "vídeo real pronto para revisão", e)
    log = api("GET", f"/api/jobs/{r['job']}/log")[1]["log"]
    confere("reaproveitando a narração" in log, "o render usou a narração aprovada, sem narrar de novo", log[-400:])
    audio, tam = tem_audio_e_formato(PASTA / "video.mp4")
    confere(audio and tam == (1080, 1920), "mp4 com áudio em 1080x1920", (audio, tam))
    confere((PASTA / "CONFORMIDADE.md").exists() and (PASTA / "PUBLICAR.txt").exists(), "run.py rodou até o fim (conformidade e PUBLICAR.txt)")
    api("POST", f"/api/producoes/{SLUG}/aprovar", {"material": "video", "versao_id": e["versao_id"]})
    with urllib.request.urlopen(f"{BASE}/download/{SLUG}?versao={e['versao_id']}") as baixa:
        confere(baixa.status == 200 and len(baixa.read()) == (PASTA / "video.mp4").stat().st_size, "download entrega o render aprovado")

    print("\n[Falha real: render com duração fora do formato]", flush=True)
    cenas = json.loads((PASTA / "cenas.json").read_text(encoding="utf-8"))
    cenas[0]["duracao"] = 90
    (PASTA / "cenas.json").write_text(json.dumps(cenas, ensure_ascii=False), encoding="utf-8")
    time.sleep(4)
    st, r = api("POST", f"/api/producoes/{SLUG}/iniciar", {"etapa": "video", "forcar": True})
    if st == 409:  # cenas mudaram e o estúdio já exige reaprovar: é o comportamento certo. Reaprova para ver a falha do comando.
        print(f"    (recusado antes de rodar: {r['erro']})", flush=True)
    e = esperar_fim(SLUG, "video", 5)
    if st == 201:
        confere(e["status"] == "falhou" and "formato" in (e["falha"]["erro"] or ""), "erro real do run.py chega à tela", e.get("falha"))

    print("\n[Pipeline simulado real: run.py --mock pelo estúdio]", flush=True)
    st, r = api("POST", "/api/producoes", {"tema": "estudio validacao", "estilo": "cartoes", "simulado": True})
    confere(st == 201 and r.get("slug") == MOCK, "cria a produção --mock", r)
    e = esperar_fim(MOCK, "pesquisa", 10)
    confere(e["status"] == "concluida", "run.py --mock terminou", e)
    time.sleep(4)
    rot = etapa(MOCK, "roteiro")
    st, _ = api("POST", f"/api/producoes/{MOCK}/aprovar", {"material": "roteiro", "versao_id": rot["versao_id"]})
    confere(st == 200, "aprova o roteiro simulado")
    nar = etapa(MOCK, "narracao")
    st, _ = api("POST", f"/api/producoes/{MOCK}/aprovar", {"material": "narracao", "versao_id": nar["versao_id"]})
    confere(st == 200, "aprova a narração simulada")
    vid = etapa(MOCK, "video")
    confere(vid["status"] == "aguardando" and vid["acoes"]["aprovar"]["habilitado"], "vídeo simulado aguarda revisão", vid["acoes"]["aprovar"])
    audio, tam = tem_audio_e_formato(REPO / "output" / MOCK / "video.mp4")
    confere(audio and tam == (1080, 1920), "render real do motor SVG", tam)
    aud = etapa(MOCK, "auditoria_texto")
    confere(aud["status"] == "nao_aplica", "modo simulado não aciona o Vini", aud["status"])
    st, _ = api("POST", f"/api/producoes/{MOCK}/aprovar", {"material": "video", "versao_id": vid["versao_id"]})
    confere(st == 200, "aprova o vídeo simulado")
    pos = api("GET", f"/api/producoes/{MOCK}/detalhes")[1]["jobs"]
    confere(not any(j["tipo"] == "agente" for j in pos), "nenhum agente foi chamado", pos)


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    if PASTA.exists() or (REPO / "output" / MOCK).exists():
        raise SystemExit("As pastas de validação já existem: apague-as antes.")
    dados = tempfile.mkdtemp(prefix="estudio-real-")
    semear()
    env = {**os.environ, "ESTUDIO_DADOS": dados}
    srv = subprocess.Popen([sys.executable, "-m", "estudio", "--porta", str(PORTA), "--nao-abrir"], cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                if api("GET", "/api/producoes")[0] == 200:
                    break
            except OSError:
                time.sleep(0.5)
        time.sleep(4)  # os arquivos recém-criados precisam assentar para virar versão
        principal()
    finally:
        srv.kill()
        srv.wait()
        shutil.rmtree(PASTA, ignore_errors=True)
        shutil.rmtree(REPO / "output" / MOCK, ignore_errors=True)
        shutil.rmtree(dados, ignore_errors=True)
    print(f"\n{'TUDO OK' if not falhas else str(len(falhas)) + ' FALHA(S): ' + '; '.join(falhas)}", flush=True)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
