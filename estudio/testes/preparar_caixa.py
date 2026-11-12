"""Monta uma cópia descartável com material real de output/, para os testes nunca tocarem nas produções de verdade.
Uso: python preparar_caixa.py <pasta vazia>. Imprime as variáveis de ambiente do estúdio, em JSON."""
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ORIGEM = REPO / "output"
PRINCIPAL = "fim-dos-terceiros-lugares"  # real, com roteiro, componentes, cenas, narração por cena e vídeo
SEGUNDA = "esquema-de-piramide"


def copiar(slug, destino, sem=()):
    shutil.copytree(ORIGEM / slug, destino / slug, ignore=shutil.ignore_patterns("__pycache__", "frames", "transparentes", *sem))


def main(caixa):
    caixa = Path(caixa).resolve()
    saida = caixa / "output"
    saida.mkdir(parents=True)
    copiar(PRINCIPAL, saida, sem=("upload.json",))
    copiar(SEGUNDA, saida, sem=("upload.json", "video.mp4", "audio.wav", "falas", "componentes"))
    (saida / "publicado-exemplo").mkdir()
    (saida / "publicado-exemplo" / "roteiro.txt").write_text("Vídeo já publicado.\n", encoding="utf-8")
    (saida / "publicado-exemplo" / "upload.json").write_text(json.dumps({"url": "https://youtu.be/x", "privacy": "private"}), encoding="utf-8")
    for slug in (PRINCIPAL, SEGUNDA):  # as cópias herdam a data original, e a pasta só conta como em andamento se for recente
        (saida / slug / ".recente").write_text("", encoding="ascii")
    (caixa / "componentes").mkdir()
    (caixa / "componentes" / "aprendizados.md").write_text("Fase: aprendendo\n", encoding="utf-8")
    (caixa / "thumbnails").mkdir()
    py = sys.executable
    sim = Path(__file__).resolve().parent / "claude_simulado.py"
    cmd = caixa / "claude.cmd"
    cmd.write_text(f'@"{py}" "{sim}" %*\r\n', encoding="ascii")
    print(json.dumps({"ESTUDIO_RAIZ": str(caixa), "ESTUDIO_DADOS": str(caixa / "dados"), "ESTUDIO_CLAUDE": str(cmd),
                      "ESTUDIO_SIMULADOR": str(Path(__file__).resolve().parent / "comandos_simulados.py")}))


if __name__ == "__main__":
    main(sys.argv[1])
