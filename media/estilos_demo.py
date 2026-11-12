"""Gera as demonstrações da tela de escolha de estilo, sempre pelo renderizador real de cada estilo. Nada aqui é ilustração à parte.

Uso:  python -m media.estilos_demo [id do estilo]
Saída: estudio/web/demos/<id>.mp4 e <id>.jpg (a escolha na tela reduz o vídeo, então 406x722 basta).
"""
import json
import multiprocessing as mp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import estilos, sketch, sketch_lib
from .util import run

ROOT = Path(__file__).resolve().parent.parent
DEMOS = ROOT / "media" / "demos"
DESTINO = ROOT / "estudio" / "web" / "demos"
FPS = 30


def _quadros_python(pasta, frames):
    cenas = json.loads((pasta / "cenas.json").read_text(encoding="utf-8"))
    tabela, t = [], 0.0
    for c in cenas:
        tabela.append((c["desenho"], t, float(c["duracao"])))
        t += float(c["duracao"])
    total = round(t * FPS)
    variante = sketch._variante(pasta)
    with mp.Pool(min(8, mp.cpu_count()), initializer=sketch._iniciar, initargs=(str(sketch.fonte_desenho(pasta, cenas)), tabela, FPS, str(frames), "vertical", variante)) as pool:
        for _ in pool.imap_unordered(sketch._quadro, range(total), chunksize=8):
            pass
    return total


def _quadros_svg(pasta, frames):
    spec = pasta / "cenas.json"
    sys.path.insert(0, str(ROOT))
    from agents.mocks import CENAS  # as cenas de exemplo do próprio pipeline de cartões
    gancho = {**CENAS[0], "duracao": 3.2, "numeros": ["7h", "3h"], "legenda": ["COM AMIGOS,", "POR SEMANA"], "pergunta": ["O QUE MUDOU?"], "rodape": []}
    barras = {**CENAS[1], "duracao": 3.2, "titulo": ["HORAS COM AMIGOS"], "escala_max": 8, "unidade": "", "barras": [{"rotulo": "2013", "valor": 7, "cor": "azul"}, {"rotulo": "2021", "valor": 3, "cor": "laranja"}], "rodape": []}
    spec.write_text(json.dumps([gancho, barras], ensure_ascii=False), encoding="utf-8")
    run(["node", "render.mjs", "--spec", str(spec), "--out", str(frames.parent)], cwd=ROOT / "render")
    return len(list(frames.glob("*.png")))


def gerar(ident, variante=None, opcoes=None, nome=None):
    nome = nome or ident
    with tempfile.TemporaryDirectory() as d:
        pasta = Path(d)
        frames = pasta / "frames"
        frames.mkdir()
        origem = DEMOS / ident
        if origem.is_dir():
            for f in origem.iterdir():
                shutil.copy(f, pasta / f.name)
        if variante:
            estilos.gravar(pasta, estilos.validar_escolha(ident, variante, opcoes))
        total = _quadros_svg(pasta, frames) if estilos.obter(ident)["motor"] == "svg" else _quadros_python(pasta, frames)
        sketch_lib.definir_variante()
        DESTINO.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.png"), "-vf", "scale=406:722:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-movflags", "+faststart", "-an", str(DESTINO / f"{nome}.mp4")], check=True)
        quadro = frames / f"{min(total, 45):04d}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(quadro), "-vf", "scale=406:722:flags=lanczos", "-q:v", "4", str(DESTINO / f"{nome}.jpg")], check=True)
    print(f"   {nome}: {total} quadros, {(DESTINO / f'{nome}.mp4').stat().st_size // 1024} KB", flush=True)


def main():
    pedidos = sys.argv[1:] or list(estilos.ESTILOS)
    for i in pedidos:
        gerar(i)
    if "sketch" in pedidos:
        gerar("sketch", "caderno_pautado", {"papel": "bege", "traco": "grafite"}, "sketch_caderno_pautado")


if __name__ == "__main__":
    main()
