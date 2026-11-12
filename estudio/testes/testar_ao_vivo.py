"""PROG-003 (fatia B): confere estudio/ao_vivo.py e a rota GET /api/agentes/ao-vivo em banco e pasta temporários.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_ao_vivo.py"""
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="ao_vivo_"))
os.environ["ESTUDIO_RAIZ"] = str(TMP / "raiz")
os.environ["ESTUDIO_DADOS"] = str(TMP / "dados")
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import ao_vivo as AV, fluxo  # noqa: E402
from estudio.banco import faz, varios  # noqa: E402

(TMP / "raiz" / "output").mkdir(parents=True)
(TMP / "dados").mkdir()
passou, falhas = 0, []
# Fixtures derivam dos nós reais do fluxo, nunca de ids fixos.
OLISE, NEYMAR, MBAPPE = (fluxo.POR_ID[i]["agente"] for i in ("cenas", "roteiro", "metadados"))
AGORA = datetime.now()


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}", flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def iso(seg_atras):
    return (AGORA - timedelta(seconds=seg_atras)).isoformat(timespec="seconds")


def job(agente=OLISE, slug="video-a", etapa="cenas", status="rodando", ini=None, term=None, spec_extra=None, motor=None, nota=None, erro=None,
        disp=0, sem_agente=False, criada=None, spec_raw=None):
    spec = {"tipo": "agente", "raia": "agente"} | ({} if sem_agente else {"agente": agente}) | (spec_extra or {})
    cur = faz("INSERT INTO jobs (slug, etapa, raia, titulo, craque, assinatura, status, spec, erro, motor, motor_nota, dispensado, criada_em, iniciado_em, terminado_em) "
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", slug, etapa, "agente", f"t {slug} {etapa}", "X", f"a{time.time_ns()}", status,
              spec_raw or json.dumps(spec), erro, motor, nota, disp, criada or iso(60), ini, term)
    return cur.lastrowid


def limpar():
    faz("DELETE FROM jobs")
    faz("DELETE FROM producoes")
    AV.invalidar_cache()


def ver():
    return AV.montar(AGORA)


def agente(r, ident):
    return next((a for a in r["agentes"] if a["id"] == ident), None)


def main():
    print("[Ocioso]")
    limpar()
    r = ver()
    confere(r["agentes"] == [] and r["concluidos_1h"] == [] and r["resumo"]["trabalhando"] == 0, "sem jobs: lista vazia")
    confere(set(r) >= {"gerado_em", "servidor_s", "resumo", "agentes", "concluidos_1h", "frescor"} and r["frescor"] == "ok", "campos do contrato", list(r))
    job(status="ok", ini=iso(7200), term=iso(7000))
    confere(agente(ver(), OLISE) is None, "agente só com job antigo concluído não aparece (ocioso)")

    print("[Trabalhando e fila]")
    limpar()
    job(OLISE, "video-a", "cenas", "rodando", ini=iso(128), motor="claude")
    j2 = job(NEYMAR, "video-b", "roteiro", "fila", criada=iso(30))
    j3 = job(MBAPPE, "video-c", "metadados", "fila", criada=iso(10))
    r = ver()
    a = agente(r, OLISE)
    t = a["trabalhos"][0]
    confere(a["estado"] == "trabalhando" and a["estado_texto"] == "Trabalhando" and a["craque"] == "Olise", "trabalhando", a)
    confere(t["segundos_na_tarefa"] == 128 and t["slug"] == "video-a" and t["etapa_id"] == "cenas" and t["etapa_nome"] == "Cenas" and t["job_id"], "segundos, slug e etapa", t)
    confere(t["aguarda_s"] is None and t["posicao_fila"] is None and t["erro_curto"] is None, "trabalhando não tem campos de fila nem erro", t)
    n, m = agente(r, NEYMAR), agente(r, MBAPPE)
    confere(n["estado"] == "fila" and n["estado_texto"] == "Na fila" and n["trabalhos"][0]["posicao_fila"] == 1 and n["trabalhos"][0]["aguarda_s"] == 30, "fila: posição 1 e espera", n)
    confere(m["trabalhos"][0]["posicao_fila"] == 2 and m["trabalhos"][0]["segundos_na_tarefa"] is None, "fila: posição 2", m)
    confere(r["resumo"]["trabalhando"] == 1 and r["resumo"]["fila"] == 2 and r["resumo"]["falhou"] == 0 and r["resumo"]["espera_voce"] == 0, "resumo", r["resumo"])
    confere(r["agentes"][0]["id"] == OLISE, "trabalhando vem antes da fila")
    confere(all(x["trabalhos"][0]["origem"] == "estudio" for x in r["agentes"]), "origem estudio sem execução em grafo")
    faz("INSERT INTO execucoes (slug, fluxo, fluxo_versao, fluxo_numero, grafo, agentes, status, criada_em) VALUES ('video-a','f',1,1,'{}','{}','ativa','x')")
    confere(agente(ver(), OLISE)["trabalhos"][0]["origem"] == "grafo", "origem grafo quando há execução")
    faz("DELETE FROM execucoes")

    print("[Falhou]")
    limpar()
    f1 = job(OLISE, "video-a", "cenas", "falhou", ini=iso(500), term=iso(400), erro="Primeira linha do erro\nsegunda linha")
    r = ver()
    a = agente(r, OLISE)
    confere(a["estado"] == "falhou" and a["estado_texto"] == "Falhou" and a["trabalhos"][0]["erro_curto"] == "Primeira linha do erro", "falhou com erro_curto de uma linha", a)
    confere(r["resumo"]["falhou"] == 1, "resumo conta falhou")
    faz("UPDATE jobs SET erro=? WHERE id=?", "x" * 400, f1)
    confere(len(agente(ver(), OLISE)["trabalhos"][0]["erro_curto"]) == 160, "erro_curto máx. 160 caracteres")
    faz("UPDATE jobs SET dispensado=1 WHERE id=?", f1)
    confere(agente(ver(), OLISE) is None, "falha dispensada some")
    faz("UPDATE jobs SET dispensado=0 WHERE id=?", f1)
    job(OLISE, "video-a", "cenas", "ok", ini=iso(300), term=iso(200))
    r = ver()
    confere(agente(r, OLISE) is None, "falha some após sucesso posterior da mesma etapa")
    confere(len(r["concluidos_1h"]) == 1, "o sucesso posterior aparece nos concluídos")
    job(OLISE, "video-z", "cenas", "falhou", ini=iso(9000), term=iso(8000), erro="antiga")
    confere(agente(ver(), OLISE)["estado"] == "falhou", "falha continua aberta mesmo com mais de 1 h")
    job(OLISE, "video-z", "cenas", "ok", ini=iso(100), term=iso(50))
    confere(agente(ver(), OLISE) is None, "sucesso posterior limpa a falha antiga")
    # falha em outra etapa do mesmo vídeo não é limpa por sucesso em etapa diferente
    job(NEYMAR, "video-y", "roteiro", "falhou", term=iso(100), erro="e")
    job(OLISE, "video-y", "cenas", "ok", term=iso(50))
    confere(agente(ver(), NEYMAR)["estado"] == "falhou", "sucesso em outra etapa não limpa a falha")

    print("[Espera você]")
    limpar()
    slug = "video-espera"
    pasta = TMP / "raiz" / "output" / slug
    pasta.mkdir()
    (pasta / "roteiro.txt").write_text("Texto do roteiro.", encoding="utf-8")
    fluxo.garantir_producao(slug)
    fluxo.sincronizar(slug, forcar=True, assentar=False)
    AV.invalidar_cache()
    r = ver()
    a = agente(r, NEYMAR)
    confere(a is not None and a["estado"] == "espera_voce" and a["estado_texto"] == "Espera você", "roteiro sem aprovação: agente do Neymar espera você", r["agentes"])
    if a:
        t = a["trabalhos"][0]
        confere(t["slug"] == slug and t["etapa_id"] == "roteiro" and t["estado"] == "espera_voce" and t["titulo_video"], "trabalho espera_voce com slug e etapa", t)
    confere(r["resumo"]["espera_voce"] == 1, "resumo conta espera_voce", r["resumo"])
    # com job do agente na última etapa, o agente vem de spec["agente"]
    jid = job(MBAPPE, slug, "roteiro", "ok", term=iso(100))
    AV.invalidar_cache()
    r = ver()
    confere(agente(r, MBAPPE) is not None and agente(r, MBAPPE)["estado"] == "espera_voce" and agente(r, NEYMAR) is None, "agente = o do último job da etapa (spec.agente)", r["agentes"])
    # cache de 3 s: aprovar não muda a resposta dentro da janela; invalidar muda
    faz("UPDATE producoes SET arquivada=1 WHERE slug=?", slug)
    confere(agente(ver(), MBAPPE) is not None, "cache de 3 s segura a produção dentro da janela")
    AV.invalidar_cache()
    confere(agente(ver(), MBAPPE) is None, "produção arquivada não entra em espera você")
    del jid

    print("[Vários trabalhos, sem agente, motor]")
    limpar()
    job(OLISE, "video-a", "cenas", "rodando", ini=iso(10))
    job(OLISE, "video-b", "cenas", "fila")
    job(OLISE, "video-c", "cenas", "falhou", erro="boom", term=iso(20))
    r = ver()
    confere(len(r["agentes"]) == 1 and len(r["agentes"][0]["trabalhos"]) == 3, "um agente, uma entrada com lista de trabalhos", r["agentes"])
    confere(r["agentes"][0]["estado"] == "falhou" and [x["estado"] for x in r["agentes"][0]["trabalhos"]] == ["falhou", "trabalhando", "fila"], "estado do agente é o mais relevante; lista ordenada")
    limpar()
    job(sem_agente=True, slug="video-x", etapa="render", status="rodando", ini=iso(5))
    job(slug="video-y", status="rodando", ini=iso(5), spec_raw="{lixo")
    r = ver()
    confere(r["agentes"] == [] and r["resumo"]["ignorados"] == 2, "job sem spec.agente (ou spec ilegível) fica de fora e conta em ignorados", r["resumo"])
    limpar()
    job(slug="v1", status="rodando", ini=iso(5), motor="codex", nota="Claude esgotou; rodando pelo Codex.")
    job(NEYMAR, "v2", "roteiro", "rodando", ini=iso(5), motor="claude")
    job(MBAPPE, "v3", "metadados", "rodando", ini=iso(5))  # job antigo: sem motor
    r = ver()
    t1, t2, t3 = (agente(r, x)["trabalhos"][0] for x in (OLISE, NEYMAR, MBAPPE))
    confere(t1["motor"] == "codex" and t1["motor_nota"] == "Claude esgotou; rodando pelo Codex.", "motor com nota", t1)
    confere(t2["motor"] == "claude" and t2["motor_nota"] is None, "motor sem nota: motor_nota None, nunca texto", t2)
    confere(t3["motor"] in ("claude", None) and t3["motor_nota"] is None and "None" not in json.dumps(t3).replace("null", ""), "job sem campo motor não quebra e não vira texto 'None'", t3)
    limpar()
    job(OLISE, "__agentes__", "teste:1", "rodando", ini=iso(5), spec_extra={"origem": "teste_agente"})
    t = ver()["agentes"][0]["trabalhos"][0]
    confere(t["origem"] == "teste_agente" and t["etapa_nome"] == "Teste de agente", "job de teste de agente vem com origem e rótulo", t)

    print("[Alerta longo e concluídos]")
    limpar()
    job(OLISE, "v1", "cenas", "rodando", ini=iso(899))
    job(NEYMAR, "v2", "roteiro", "rodando", ini=iso(900))
    r = ver()
    confere(agente(r, OLISE)["trabalhos"][0]["alerta_longo"] is False and agente(r, NEYMAR)["trabalhos"][0]["alerta_longo"] is True, "alerta_longo em 900 s (899 não, 900 sim)")
    limpar()
    job(NEYMAR, "v1", "roteiro", "ok", term=iso(900), motor="claude")
    job(OLISE, "v2", "cenas", "ok", term=iso(3500))
    job(MBAPPE, "v3", "metadados", "ok", term=iso(3700))
    r = ver()
    c = r["concluidos_1h"]
    confere({x["agente"] for x in c} == {NEYMAR, OLISE} and len(c) == 2, "concluídos só da última hora", c)
    confere(next(x for x in c if x["agente"] == NEYMAR)["terminou_ha_s"] == 900 and c[0]["etapa_nome"] and c[0]["craque"], "terminou_ha_s e rótulos", c)
    confere(r["agentes"] == [], "concluído não vira agente ativo")

    print("[Rota]")
    from estudio.servidor import Manipulador
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        limpar()
        job(OLISE, "video-a", "cenas", "rodando", ini=iso(10))
        with urllib.request.urlopen(base + "/api/agentes/ao-vivo") as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
            confere(resp.status == 200 and "json" in resp.headers["Content-Type"], "GET /api/agentes/ao-vivo -> 200 JSON")
        confere("resumo" in corpo and "concluidos_1h" in corpo and "erro" not in corpo, "ao-vivo não cai na rota <id> (sem 'erro', com contrato)", list(corpo))
        confere(corpo["agentes"] and corpo["agentes"][0]["id"] == OLISE, "rota devolve o estado do banco")
        # a rota <id> continua funcionando para um agente real do catálogo
        try:
            urllib.request.urlopen(base + "/api/agentes/olise-diretor-arte")
            outro = "ok"
        except Exception as e:  # sem catálogo na raiz temporária: 404 do <id>, não do ao-vivo
            outro = getattr(e, "code", repr(e))
        confere(outro in ("ok", 404), "rota /api/agentes/<id> segue ativa", outro)

        print("[Falha na consulta]")
        original = AV._jobs
        AV._jobs = lambda *_: (_ for _ in ()).throw(RuntimeError("banco quebrou"))
        try:
            urllib.request.urlopen(base + "/api/agentes/ao-vivo")
            confere(False, "consulta com erro deve dar 500")
        except urllib.error.HTTPError as e:
            corpo = json.loads(e.read().decode("utf-8"))
            confere(e.code == 500 and "erro" in corpo and "banco quebrou" not in json.dumps(corpo), "consulta com erro -> 500 JSON com 'erro' e sem vazar detalhe", corpo)
        finally:
            AV._jobs = original
        with urllib.request.urlopen(base + "/api/agentes/ao-vivo") as resp:
            confere(resp.status == 200, "servidor segue vivo depois do erro")

        print("[50 jobs]")
        limpar()
        for i in range(50):
            ag = (OLISE, NEYMAR, MBAPPE)[i % 3]
            st = ("rodando", "fila", "falhou", "ok")[i % 4]
            job(ag, f"v{i:02d}", ("cenas", "roteiro", "metadados")[i % 3], st, ini=iso(100 + i), term=iso(60 + i) if st in ("falhou", "ok") else None, erro="e" if st == "falhou" else None)
        for i in range(30):  # 30 produções ativas esperando você: o pior caso do "Espera você" sem cache
            p = TMP / "raiz" / "output" / f"prod-{i:02d}"
            p.mkdir()
            (p / "roteiro.txt").write_text(f"Roteiro {i}.", encoding="utf-8")
            fluxo.garantir_producao(p.name)
            fluxo.sincronizar(p.name, forcar=True, assentar=False)
        AV.invalidar_cache()
        t0 = time.perf_counter()
        AV.montar()
        frio = (time.perf_counter() - t0) * 1000
        confere(frio < 200, f"50 jobs + 30 produções, cache frio: montar() em {frio:.0f} ms (limite 200 ms)")
        AV.invalidar_cache()
        tempos = []
        for _ in range(5):
            t0 = time.perf_counter()
            with urllib.request.urlopen(base + "/api/agentes/ao-vivo") as resp:
                corpo = json.loads(resp.read().decode("utf-8"))
            tempos.append((time.perf_counter() - t0) * 1000)
        confere(resp.status == 200 and len(corpo["agentes"]) == 3, "50 jobs: 3 agentes, servidor vivo", len(corpo["agentes"]))
        confere(max(tempos) < 200, f"50 jobs: resposta pela rota em {max(tempos):.0f} ms no pior de 5 (limite 200 ms)", tempos)
        t0 = time.perf_counter()
        AV.montar()
        confere((time.perf_counter() - t0) * 1000 < 200, f"50 jobs: montar() em {(time.perf_counter() - t0) * 1000:.0f} ms")
    finally:
        srv.shutdown()

    print("[Só leitura]")
    antes = varios("SELECT id, status, dispensado FROM jobs ORDER BY id")
    ver()
    confere(varios("SELECT id, status, dispensado FROM jobs ORDER BY id") == antes, "ler o estado não altera jobs")

    print(f"\n{passou} ok, {len(falhas)} falhas")
    for f in falhas:
        print("  -", f)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
