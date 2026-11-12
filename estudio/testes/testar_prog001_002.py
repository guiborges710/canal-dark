"""PROG-001 (motivo de "nao se aplica") e PROG-002 ("Iniciar cenas" responde, sem duplicar), no nivel do modulo fluxo.
Isolado: cria pasta temporaria propria (ESTUDIO_RAIZ/ESTUDIO_DADOS), nao toca output/ real, nao chama agente, render, rede nem Trello.
Uso: python estudio/testes/testar_prog001_002.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
caixa = Path(tempfile.mkdtemp(prefix="qa-prog001002-"))
os.environ["ESTUDIO_RAIZ"] = str(caixa)
os.environ["ESTUDIO_DADOS"] = str(caixa / "dados")
sys.path.insert(0, str(REPO))
(caixa / "output").mkdir()
(caixa / "componentes").mkdir()
(caixa / "componentes" / "aprendizados.md").write_text("Fase: aprendendo\n", encoding="utf-8")

from estudio import fluxo  # noqa: E402

falhas = []


def confere(cond, nome, detalhe=""):
    print(("PASSOU " if cond else "FALHOU ") + nome + (f" -> {detalhe}" if detalhe else ""))
    if not cond:
        falhas.append(nome)


def pasta(slug, roteiro=True, cenas=None):
    p = caixa / "output" / slug
    p.mkdir()
    if roteiro:
        (p / "roteiro.txt").write_text("Texto de teste.\n", encoding="utf-8")
    if cenas is not None:
        (p / "cenas.json").write_text(json.dumps(cenas), encoding="utf-8")
    return p


def etapa(slug, ident):
    return next(e for e in fluxo.estado(slug, sincroniza=True)["etapas"] if e["id"] == ident)


# PROG-001: motivo citando a regra real
pasta("terminal-pasta")  # origem 'pasta' (veio de fora do estudio)
e = etapa("terminal-pasta", "componentes")
confere(e["status"] == "nao_aplica", "PROG-001 c1: componentes de pasta externa = nao_aplica", e["status"])
confere(bool(e["motivo_nao_aplica"]) and "fora do estúdio" in e["motivo_nao_aplica"], "PROG-001 c1/c2: motivo cita a regra (origem fora do estudio)", str(e["motivo_nao_aplica"]))

pasta("sim")
fluxo.garantir_producao("sim")
fluxo.faz("UPDATE producoes SET simulado=1 WHERE slug=?", "sim")
e = etapa("sim", "componentes")
confere(e["status"] == "nao_aplica" and "simulada" in (e["motivo_nao_aplica"] or ""), "PROG-001 c2: motivo cita producao simulada (--mock)", str(e["motivo_nao_aplica"]))
a = etapa("sim", "auditoria_texto")
confere(a["status"] == "nao_aplica" and (a["motivo_nao_aplica"] or "").startswith("Produção simulada"), "PROG-001 c1: auditoria no modo simulado tem motivo", str(a["motivo_nao_aplica"]))

# A regra de componentes não depende do estilo escolhido: cobre os quatro estilos do Corte.
for estilo in ("sketch", "cartoes", "cartoon_alive", "documentary_collage"):
    slug = f"sim-{estilo}"
    p = pasta(slug)
    (p / "estilo.json").write_text(json.dumps({"estilo": estilo}), encoding="utf-8")
    fluxo.garantir_producao(slug)
    fluxo.faz("UPDATE producoes SET simulado=1 WHERE slug=?", slug)
    e = etapa(slug, "componentes")
    confere(e["status"] == "nao_aplica" and "simulada" in (e["motivo_nao_aplica"] or ""), f"PROG-001 c2/c4: motivo vale no estilo {estilo}", str(e["motivo_nao_aplica"]))

# PROG-001 c6: etapa que se aplica nao traz motivo
r = etapa("terminal-pasta", "roteiro")
confere(r["status"] != "nao_aplica" and r["motivo_nao_aplica"] is None, "PROG-001 c6: etapa aplicavel sem motivo", f"{r['status']} / {r['motivo_nao_aplica']}")

# toda etapa nao_aplica de qualquer estado tem motivo nao vazio
for slug in ("terminal-pasta", "sim"):
    for x in fluxo.estado(slug)["etapas"]:
        if x["status"] == "nao_aplica":
            confere(bool(x["motivo_nao_aplica"]), f"PROG-001 c1: {slug}/{x['id']} nao_aplica tem motivo")
        else:
            confere(x["motivo_nao_aplica"] is None, f"PROG-001 c6: {slug}/{x['id']} aplicavel sem aviso")

# PROG-002: dependencia faltando = recusa com texto (c2); sem cenas e sem roteiro nao inicia
pasta("sem-roteiro", roteiro=False).joinpath("notas.md").write_text("n\n", encoding="utf-8")
try:
    fluxo.iniciar_etapa("sem-roteiro", "cenas")
    confere(False, "PROG-002 c2: cenas sem roteiro deve ser recusado")
except fluxo.Recusado as exc:
    msg = str(exc.args[0]) if exc.args else ""
    confere(bool(msg) and msg != "[]", "PROG-002 c2: recusa traz explicacao", msg[:160])
e = etapa("sem-roteiro", "cenas")
confere(not e["acoes"]["iniciar"] or not e["acoes"]["iniciar"]["habilitado"], "PROG-002 c2: botao desabilitado quando nao pode iniciar")
motivos = (e["acoes"]["iniciar"] or {}).get("motivos") or []
confere(bool(motivos or e.get("bloqueio")), "PROG-002 c2: botao desabilitado traz o motivo", str(motivos))

# PROG-002 c3: clique repetido = mesmo job (aprovar o roteiro ja dispara cenas sozinho, entao novo1 pode ser False)
import time
time.sleep(4)  # arquivos precisam assentar para o sincronizar registrar a versao
fluxo.sincronizar("terminal-pasta", forcar=True)
vr = fluxo.Contexto("terminal-pasta").versoes["roteiro"]
fluxo.aprovar("terminal-pasta", "roteiro", vr["id"])
job1, novo1 = fluxo.iniciar_etapa("terminal-pasta", "cenas")
job2, novo2 = fluxo.iniciar_etapa("terminal-pasta", "cenas")
confere(not novo2 and job1["id"] == job2["id"], "PROG-002 c1/c3: clique duplo gera um unico job", f"{job1['id']} {job2['id']} novo={novo1},{novo2}")
n = fluxo.um("SELECT COUNT(*) n FROM jobs WHERE slug=? AND etapa='cenas'", "terminal-pasta")["n"]
confere(n == 1, "PROG-002 c3: 1 job no banco", str(n))
e = etapa("terminal-pasta", "cenas")
confere(e["status"] in ("fila", "executando") and e["job"] is not None, "PROG-002 c1: estado em andamento retornado", e["status"])

print(f"\n{len(falhas)} falha(s)." if falhas else "\nTudo passou.")
sys.exit(1 if falhas else 0)
