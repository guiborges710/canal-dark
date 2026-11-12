"""Prepara uma pasta de saída descartável para os testes E2E do painel (V2).
Uso: python -m clipes.testes.preparar_e2e <pasta_saida> <slug>
Copia transcrição e fonte do projeto real flow-games-fgn (o vídeo entra por link físico, sem cópia),
congela o perfil Geral com cortes curtos (teste rápido) e grava o fluxo padrão."""
import os
import shutil
import sys
from pathlib import Path

from clipes import etapas as T
from clipes import perfis as PF

REAL = Path(__file__).resolve().parents[2] / "clipes_out" / "flow-games-fgn"


def main():
    saida, slug = Path(sys.argv[1]), sys.argv[2]
    d = saida / slug
    d.mkdir(parents=True, exist_ok=True)
    for f in ("transcricao.json", "fonte.json"):
        shutil.copy2(REAL / f, d / f)
    try:
        os.link(REAL / "fonte.mp4", d / "fonte.mp4")
    except OSError:
        shutil.copy2(REAL / "fonte.mp4", d / "fonte.mp4")
    PF.congelar(d, "geral")
    PF.ajustar_projeto(d, {"quantidade": 2, "duracao": {"min": 8, "max": 12}})
    T.gravar(d, T.padrao())
    print(d)


if __name__ == "__main__":
    main()
