"""Caminhos e limites do estúdio. As variáveis ESTUDIO_* existem para os testes rodarem numa cópia, sem tocar em output/."""
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAIZ = Path(os.environ.get("ESTUDIO_RAIZ") or REPO)  # onde ficam output/, componentes/ e thumbnails/
SAIDA = RAIZ / "output"
DADOS = Path(os.environ.get("ESTUDIO_DADOS") or REPO / "estudio" / "dados")  # banco, versões e logs (gitignored)
WEB = REPO / "estudio" / "web"
PY = sys.executable

CLAUDE = os.environ.get("ESTUDIO_CLAUDE") or shutil.which("claude")
SIMULADOR = os.environ.get("ESTUDIO_SIMULADOR")  # só testes: troca os comandos pesados por um simulador

PORTA = 8765
LIMITE_RAIAS = {"agente": 3, "pesado": 1}  # CLAUDE.md: só o render roda um por vez; os textos seguem em paralelo
ORCAMENTO_AGENTE = "3.00"  # mesmo teto por tarefa do De Bruyne no Telegram (ORCAMENTO_TAREFA)
TEMPO_AGENTE_S = 45 * 60
TEMPO_PESADO_S = 90 * 60
BATIMENTO_S = 3
BATIMENTO_MORTO_S = 25
ASSENTAR_S = 3  # arquivo mexido há menos que isso ainda pode estar sendo escrito
DIAS_ATIVA = 14  # pasta antiga sem studio: fica em andamento só se mexida nestes dias
