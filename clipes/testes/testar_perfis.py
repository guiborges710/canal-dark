"""Testes da etapa 2 (perfis e migração). Rodar: .venv\\Scripts\\python -m clipes.testes.testar_perfis

- CRUD, duplicar, arquivar e versionamento (em pasta temporária; não toca os perfis reais).
- Projeto congela o perfil: mudar o perfil-base não altera o projeto.
- Regressão: projeto anterior à V2 (sem perfil.json) seleciona exatamente os mesmos momentos da V1
  (referência gravada com o código V1 sobre o vídeo real clipes_out/flow-games-fgn).
- Mesmo núcleo, critérios distintos: Geral (sem termos de tema) e GTA 6 escolhem com regras diferentes.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from clipes import perfis as PF
from clipes import pipeline as P

AQUI = Path(__file__).resolve().parent
REAL = P.SAIDA / "flow-games-fgn"
falhas: list[str] = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def copia_projeto(destino: Path) -> Path:
    destino.mkdir(parents=True)
    for f in ("transcricao.json", "fonte.json"):
        shutil.copy2(REAL / f, destino / f)
    try:
        os.link(REAL / "fonte.mp4", destino / "fonte.mp4")
    except OSError:
        shutil.copy2(REAL / "fonte.mp4", destino / "fonte.mp4")
    return destino


def teste_crud(tmp: Path):
    print("CRUD e versões")
    real_pasta, real_hist = PF.PASTA, PF.HISTORICO
    PF.PASTA, PF.HISTORICO = tmp / "perfis", tmp / "perfis" / "_historico"
    try:
        shutil.copytree(real_pasta, PF.PASTA, ignore=shutil.ignore_patterns("_historico"))
        novo = PF.salvar({"nome": "Xadrez ao vivo", "palavras_chave": "xeque, mate, abertura",
                          "duracao": {"min": 15, "max": 40}}, novo=True)
        ok(novo["id"] == "xadrez-ao-vivo" and novo["versao"] == 1, "cria perfil personalizado com id gerado")
        ok(novo["palavras_chave"] == ["xeque", "mate", "abertura"], "aceita lista separada por vírgula")
        try:
            PF.salvar({"nome": "", "duracao": {"min": 50, "max": 10}}, novo=True)
            ok(False, "recusa perfil inválido")
        except PF.PerfilInvalido as e:
            ok(len(e.erros) >= 2, f"recusa perfil inválido ({len(e.erros)} erros)")
        v2 = PF.salvar({**novo, "quantidade": 8})
        ok(v2["versao"] == 2, "editar gera versão 2")
        ok(PF.carregar("xadrez-ao-vivo", 1)["quantidade"] == 5, "versão 1 continua no histórico")
        ok(PF.salvar(v2)["versao"] == 2, "salvar sem mudança não cria versão")
        dup = PF.duplicar("xadrez-ao-vivo")
        ok(dup["id"] != "xadrez-ao-vivo" and dup["quantidade"] == 8 and dup["versao"] == 1, "duplica")
        PF.arquivar(dup["id"])
        ok(dup["id"] not in [p["id"] for p in PF.listar()], "arquivado some da lista")
        ok(dup["id"] in [p["id"] for p in PF.listar(True)], "arquivado aparece com incluir_arquivados")
        d = tmp / "proj"
        d.mkdir()
        PF.congelar(d, "xadrez-ao-vivo")
        PF.salvar({**PF.carregar("xadrez-ao-vivo"), "quantidade": 3})
        ok(PF.do_projeto(d)["quantidade"] == 8 and PF.do_projeto(d)["versao"] == 2,
           "projeto mantém a versão congelada após mudar o perfil")
        aj = PF.ajustar_projeto(d, {"quantidade": 2})
        ok(aj["quantidade"] == 2 and aj["ajustado_no_projeto"] and PF.carregar("xadrez-ao-vivo")["quantidade"] == 3,
           "ajuste por projeto não altera o perfil-base")
    finally:
        PF.PASTA, PF.HISTORICO = real_pasta, real_hist


def sem_tempo(m):
    return [{k: c[k] for k in ("id", "ini", "fim", "dur", "score", "quentes", "texto")} for c in m]


def teste_regressao(tmp: Path):
    print("Regressão GTA 6 (projeto anterior à V2)")
    if not (REAL / "fonte.mp4").exists():
        ok(False, f"vídeo real ausente em {REAL}")
        return
    d = copia_projeto(tmp / "legado")
    ok(PF.do_projeto(d)["id"] == "gta6" and PF.do_projeto(d)["versao"] == 1, "sem perfil.json usa gta6 v1")
    novo = P.momentos(d, 8)
    ref = json.loads((AQUI / "referencia_v1_momentos.json").read_text(encoding="utf-8"))
    ok(sem_tempo(novo) == sem_tempo(ref), "mesmos 8 momentos, notas e textos da V1")
    ok(all(c.get("motivo") and c.get("status") == "sugerido" for c in novo), "cada sugestão traz motivo e status")
    return novo


def teste_nichos(tmp: Path):
    print("Mesmo núcleo, critérios distintos")
    res = {}
    for pid in ("geral", "gta6"):
        d = copia_projeto(tmp / pid)
        PF.congelar(d, pid)
        res[pid] = P.momentos(d)
        p = PF.carregar(pid)
        durs_ok = all(p["duracao"]["min"] <= (c.get("fim_sugerido", c["fim"]) - c.get("ini_sugerido", c["ini"]))
                      <= p["duracao"]["max"] for c in res[pid])
        assuntos = {(c.get("serie") or {}).get("id") or c["id"] for c in res[pid]}  # série em partes conta como UM assunto
        ok(len(assuntos) == p["quantidade"] and durs_ok,
           f"{pid}: {len(assuntos)} assuntos ({len(res[pid])} cortes, partes de série incluídas) na janela {p['duracao']}")
        ok(all(c["perfil"]["id"] == pid for c in res[pid]), f"{pid}: sugestões registram o perfil")
    a = {(c["ini"], c["fim"]) for c in res["geral"]}
    b = {(c["ini"], c["fim"]) for c in res["gta6"]}
    ok(a != b, f"seleções diferentes ({len(a & b)} em comum de {len(a)})")
    ok(all(not c["sinais"]["palavras_chave"] for c in res["geral"]), "Geral não depende de palavras de tema")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="clipes_teste_"))
    try:
        teste_crud(tmp)
        teste_regressao(tmp)
        teste_nichos(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'TUDO OK' if not falhas else f'{len(falhas)} FALHA(S)'}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
