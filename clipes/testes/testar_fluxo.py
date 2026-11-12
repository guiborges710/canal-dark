"""Testes da etapa 3 (fluxo configurável, revisão e agentes). Rodar:
    .venv\\Scripts\\python -m clipes.testes.testar_fluxo

Usa cópias do projeto real clipes_out/flow-games-fgn (transcrição pronta) em pasta temporária e o
simulador de agentes (claude_simulado.py): nenhuma chamada real ao Claude.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from clipes import estado as E
from clipes import etapas as T
from clipes import perfis as PF
from clipes import pipeline as P
from clipes.orquestrador import rodar

AQUI = Path(__file__).resolve().parent
REAL = P.SAIDA / "flow-games-fgn"
falhas: list[str] = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def projeto(raiz: Path, nome: str, fluxo: dict | None) -> Path:
    d = raiz / nome
    d.mkdir()
    for f in ("transcricao.json", "fonte.json"):
        shutil.copy2(REAL / f, d / f)
    try:
        os.link(REAL / "fonte.mp4", d / "fonte.mp4")
    except OSError:
        shutil.copy2(REAL / "fonte.mp4", d / "fonte.mp4")
    PF.congelar(d, "geral")
    PF.ajustar_projeto(d, {"quantidade": 2, "duracao": {"min": 8, "max": 12}})  # cortes curtos: teste rápido
    if fluxo is not None:
        T.gravar(d, fluxo)
    return d


def fluxo(desligar=(), revisao=True) -> dict:
    f = T.padrao()
    for e in f["etapas"]:
        if e["id"] in desligar or (e["id"] == "revisao" and not revisao):
            e["ativa"] = False
    return f


def status(d, no):
    return E.ler(d)["nos"].get(no, {}).get("status")


def mom(d):
    return json.loads((d / "momentos.json").read_text(encoding="utf-8"))


def teste_revisao(raiz):
    print("Fluxo V2 com revisão humana e agentes (simulados)")
    d = projeto(raiz, "com-revisao", fluxo())
    fim = rodar(d)
    ok(fim == "revisao" and status(d, "revisao") == "espera_voce", "para na revisão esperando você")
    ok(status(d, "curadoria") == "concluido" and all(m.get("parecer") for m in mom(d)), "Kaká (curadoria) deu parecer")
    ok(not (d / "clipes").exists(), "nenhum corte antes da revisão")
    vivos = [m for m in mom(d) if m.get("status") != "rejeitado"]
    ok(1 <= len(vivos) <= 2, f"depois da curadoria sobra no máximo a cota do perfil ({len(vivos)} de 2; o pool é maior)")
    m1 = vivos[0]
    P.decidir(d, m1["id"], "aceito", m1["ini"] + 0.5, m1["fim"])
    for outro in vivos[1:]:
        P.decidir(d, outro["id"], "rejeitado")
    novo = next(m for m in mom(d) if m["id"] == m1["id"])
    ok(novo["ajustado"] and novo["ini_original"] == m1["ini"], "ajuste de limite guarda o original")
    fim = rodar(d)
    ok(fim == "aprovacao" and status(d, "aprovacao") == "espera_voce", "segue até a aprovação")
    cl = sorted(x.name for x in (d / "clipes").glob("[0-9][0-9].mp4"))
    ok(cl == [f"{m1['id']:02d}.mp4"], f"só a sugestão aceita virou corte ({cl})")
    j = json.loads((d / "clipes" / f"{m1['id']:02d}.json").read_text(encoding="utf-8"))
    ok(j["gancho"] == f"GANCHO {m1['id']}" and j["comentario_proprio"], "gancho do Zidane entrou no corte")
    ok(abs(j["ini"] - (m1["ini"] + 0.5)) < 0.01, "corte usa o limite ajustado")
    ok(status(d, "potencial") == "concluido" and status(d, "originalidade") == "concluido", "Totti e check concluídos")
    ok((d / "publicar").exists(), "embalagem gerada")


def teste_triagem(raiz):
    print("Triagem da fonte (Rivaldo): primeiro agente do fluxo, antes do Kaká")
    os.environ.pop("CLIPES_SIM_TRIAGEM_NOTA", None)
    # 1) nota alta: segue sozinho e a triagem vem ANTES dos momentos
    d = projeto(raiz, "tri-alta", fluxo(revisao=False))
    fim = rodar(d)
    est = E.ler(d)["nos"]
    ok(status(d, "triagem") == "concluido" and "Nota 80" in est["triagem"]["msg"], f"nota alta conclui com a nota no painel ({est['triagem']['msg']})")
    ok((d / "triagem_dados.json").exists() and (d / "triagem.json").exists(), "dados do código e triagem.json gravados")
    ev = [x["no"] for x in E.ler(d)["eventos"]]
    ok(ev.index("triagem") < ev.index("momentos"), "a triagem acontece antes de sugerir momentos")
    ok(fim == "aprovacao", f"nota alta segue até o fim ({fim})")
    # 2) nota baixa: PARA e pergunta; nenhum momento/agente seguinte roda
    os.environ["CLIPES_SIM_TRIAGEM_NOTA"] = "30"
    d = projeto(raiz, "tri-baixa", fluxo(revisao=False))
    fim = rodar(d)
    ok(fim == "triagem" and status(d, "triagem") == "espera_voce", "nota baixa para e espera você")
    ok(not (d / "momentos.json").exists() and not (d / "agentes" / "curadoria.log").exists(), "nada mais roda enquanto você não decide")
    ok("Nota 30" in E.ler(d)["nos"]["triagem"]["msg"] and "Continuar" in E.ler(d)["nos"]["triagem"]["msg"], "mensagem diz a nota e como continuar")
    t0 = (d / "triagem.json").stat().st_mtime_ns
    fim = rodar(d)  # você clicou em Continuar mesmo assim
    ok(status(d, "triagem") == "concluido" and (d / "momentos.json").exists(), "Continuar segue sem reavaliar a fonte")
    ok((d / "triagem.json").stat().st_mtime_ns == t0, "o Rivaldo não foi chamado de novo")
    # 3) mínimo 0 = nunca para
    f = fluxo(revisao=False)
    for e in f["etapas"]:
        if e["id"] == "triagem":
            e["ferramentas"]["nota_minima"] = "0"
    d = projeto(raiz, "tri-zero", f)
    fim = rodar(d)
    ok(status(d, "triagem") == "concluido" and fim == "aprovacao", "com mínimo 0 a nota baixa não para o fluxo")
    os.environ.pop("CLIPES_SIM_TRIAGEM_NOTA", None)
    # 4) triagem desligada: fluxo igual ao de antes
    d = projeto(raiz, "tri-off", fluxo(desligar=("triagem",), revisao=False))
    rodar(d)
    ok(status(d, "triagem") in (None, "pendente") and not (d / "triagem.json").exists(), "triagem desligada não roda")


def teste_falha_retomada(raiz):
    print("Falha de agente e retomada sem refazer o anterior")
    d = projeto(raiz, "falha", fluxo(revisao=False))
    os.environ["CLIPES_SIM_FALHA"] = "zidane-editor-cortes"
    try:
        fim = rodar(d)
        ok(fim == "comentario" and status(d, "comentario") == "falhou", "falha do Zidane aparece no nó dele")
        ok(E.ler(d)["nos"]["comentario"].get("detalhe"), "falha traz detalhe do log")
        t_mom = (d / "momentos.json").stat().st_mtime_ns
        t_tr = (d / "transcricao.json").stat().st_mtime_ns
        fim = rodar(d, desde="comentario")
        ok(fim == "aprovacao", "tentar de novo continua até o fim")
        ok((d / "transcricao.json").stat().st_mtime_ns == t_tr, "transcrição não foi refeita")
        ok(all(m.get("gancho") for m in mom(d) if m.get("status") != "rejeitado"), "comentário escrito na retomada")
        n_cortes = len(list((d / "clipes").glob("[0-9][0-9].mp4")))
        n_aceitos = sum(1 for m in mom(d) if m.get("status") == "aceito")
        ok(n_cortes == n_aceitos and 1 <= n_cortes <= 2, f"sem revisão: corta o que o Kaká aceitou, até a cota ({n_cortes} de {n_aceitos} aceitos)")
        ok(t_mom != (d / "momentos.json").stat().st_mtime_ns, "momentos só mudaram pelo agente (não refeitos do zero)")
    finally:
        os.environ.pop("CLIPES_SIM_FALHA", None)


def teste_dependencias(raiz):
    print("Etapas opcionais e dependências")
    f = fluxo(desligar=("comentario",))
    ok(any("comentário" in x for x in T.validar(f)), "desligar o comentário com o check ligado é recusado")
    f = fluxo(desligar=("triagem", "curadoria", "comentario", "revisao_texto", "gancho", "potencial", "originalidade", "embalagem"), revisao=False)
    ok(not T.validar(f), "desligar todas as opcionais (e as que dependem delas) é válido")
    d = projeto(raiz, "minimo", f)
    fim = rodar(d)
    ok(fim == "aprovacao" and len(list((d / "clipes").glob("[0-9][0-9].mp4"))) == 2, "fluxo mínimo gera os cortes")
    ok(not (d / "agentes").exists(), "nenhum agente disparado")
    def mover(eid, antes_de):
        g = T.padrao()
        for e in g["etapas"]:
            if e["id"] == "revisao_texto":  # a aprovação do texto obriga o Figo a vir depois dela
                e["ativa"] = False
        ids = [e["id"] for e in g["etapas"]]
        item = g["etapas"].pop(ids.index(eid))
        g["etapas"].insert([e["id"] for e in g["etapas"]].index(antes_de), item)
        return g
    ok(not T.validar(mover("gancho", "comentario")), "Figo antes do Zidane é uma ordem válida")
    ok(bool(T.validar(mover("potencial", "corte"))), "Totti antes de existir corte é recusado")
    ok(bool(T.validar(mover("comentario", "curadoria"))), "Zidane antes da curadoria do Kaká é recusado")


def teste_legado(raiz):
    print("Projeto anterior à V2 (sem fluxo.json)")
    d = projeto(raiz, "legado", None)
    (d / "perfil.json").unlink()
    fim = rodar(d)
    ok(not (d / "agentes").exists(), "agentes não são disparados (fluxo V1, pelo Pelé)")
    ok(len(list((d / "clipes").glob("[0-9][0-9].mp4"))) >= 1, "cortes gerados como na V1")
    ok(fim in ("originalidade", "aprovacao"), f"para no check ou na aprovação, como na V1 ({fim})")


def main():
    raiz = Path(tempfile.mkdtemp(prefix="clipes_fluxo_"))
    os.environ["CLIPES_CLAUDE"] = json.dumps([sys.executable, str(AQUI / "claude_simulado.py")])
    os.environ["CLIPES_SAIDA_TESTE"] = str(raiz)
    try:
        teste_dependencias(raiz)
        teste_revisao(raiz)
        teste_triagem(raiz)
        teste_falha_retomada(raiz)
        teste_legado(raiz)
    finally:
        shutil.rmtree(raiz, ignore_errors=True)
    print(f"\n{'TUDO OK' if not falhas else f'{len(falhas)} FALHA(S)'}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
