"""Sobe o Corte lendo o painel numa pasta temporária (nunca o repositório real). Uso: subir_painel_caixa.py <caixa> <porta>. Só para o e2e_painel."""
import os
import sys
from pathlib import Path

caixa = Path(sys.argv[1]).resolve()
porta = sys.argv[2]
os.environ["ESTUDIO_RAIZ"] = str(caixa)
os.environ["ESTUDIO_DADOS"] = str(caixa / "dados")
(caixa / "dados").mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from estudio import painel  # noqa: E402

painel.RAIZ = caixa
sys.argv = ["estudio", "--porta", porta, "--nao-abrir"]
from estudio.__main__ import main  # noqa: E402

main()
