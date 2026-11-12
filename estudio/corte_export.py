"""Prepara as fontes de imagem do corte e exporta o MP4. Roda como trabalho do estúdio (ver executor.py), nunca dentro do servidor.

Uso:
  python -m estudio.corte_export --slug <pasta> --fontes    desenha os clipes por cena a partir do sketch_cenas.py
  python -m estudio.corte_export --slug <pasta>             compõe o corte e grava output/<slug>/video.mp4

O encode é o mesmo do render (media/motion.py). Quadro sem legenda nem asset sai direto do clipe; os demais passam pelo mesmo
web/compositor.js da prévia, no Chrome local (render/corte_compor.mjs).
"""
import argparse
import json
import multiprocessing as mp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import DADOS, REPO

sys.path.insert(0, str(REPO))

FONTES_TMP = DADOS / "exportando"


def _ffmpeg(*args):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=0x08000000)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg falhou: {r.stderr[-600:]}")


def preparar_fontes(slug):
    """Desenha cada cena que ainda não tem clipe. A mesma função do render, no mesmo `lt` e `dur`; se o desenho não rodar, recorta do vídeo do projeto."""
    from media import sketch, sketch_lib

    from . import corte, materiais as M
    from .banco import agora, faz, um
    e = corte.carregar(slug)
    faltam = [c for c in e["cenas"] if c["fonte"]["tipo"] == "sketch" and not corte._resolver_fonte(c["fonte"])[0]]
    if not faltam:
        print("   nenhuma fonte a preparar", flush=True)
        return
    FONTES_TMP.mkdir(parents=True, exist_ok=True)
    fps, formato = e["fps"], e["formato"]
    codigo = sketch.fonte_desenho(M.pasta(slug), M.ler_cenas(slug))
    variante = sketch._variante(M.pasta(slug))
    sketch_lib.definir_formato(formato)
    for n, c in enumerate(faltam, 1):
        f = c["fonte"]
        if um("SELECT sha FROM fontes WHERE chave=?", f["chave"] or ""):
            continue
        with tempfile.TemporaryDirectory(dir=FONTES_TMP) as d:
            d = Path(d)
            saida = d / "clipe.mp4"
            total = max(1, round(f["dur"] * fps))
            origem = "sketch"
            try:
                if not f["chave"]:
                    raise ValueError("a cena não existe mais no sketch_cenas.py")
                with mp.Pool(min(8, mp.cpu_count()), initializer=sketch._iniciar, initargs=(str(codigo), [(f["desenho"], 0.0, f["dur"])], fps, str(d), formato, variante)) as pool:
                    for _ in pool.imap_unordered(sketch._quadro, range(total), chunksize=8):
                        pass
                _ffmpeg("-framerate", fps, "-i", d / "%04d.png", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", 12, "-g", 15, "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-an", "-movflags", "+faststart", saida)
            except Exception as ex:  # noqa: BLE001
                if not (f.get("video") and f.get("ini") is not None):
                    raise SystemExit(f"{c['rotulo']}: não foi possível desenhar ({ex}) e não há vídeo do projeto para recortar. Peça o ajuste ao Olise.")
                print(f"   {c['rotulo']}: sem desenho ({ex}); recortando do vídeo do projeto", flush=True)
                origem = "video"
                _ffmpeg("-ss", f"{f['ini']:.3f}", "-i", M.caminho_blob(f["video"]), "-frames:v", total, "-c:v", "libx264", "-preset", "veryfast", "-crf", 12, "-g", 15, "-pix_fmt", "yuv420p", "-an", saida)
            sha = M.sha_arquivo(saida)
            M.guardar_blob(saida, sha)
            faz("INSERT OR REPLACE INTO fontes (chave, sha, dur, origem, criada_em) VALUES (?,?,?,?,?)", f["chave"] or f"sem-{c['id']}-{sha}", sha, f["dur"], origem, agora())
        print(f"   fonte {n}/{len(faltam)}: {c['rotulo']}", flush=True)


def _extrair_quadros(comp, frames):
    """Um PNG por quadro do corte, numerado como o motion._encode lê."""
    from . import materiais as M
    fps = comp["fps"]
    for s in comp["segmentos"]:
        n = s["f1"] - s["f0"]
        tocar = min(n, s["quadros_fonte"])
        # -ss antes do -i entrega o primeiro quadro com tempo >= ao pedido; recuar meio quadro garante cair exatamente no quadro certo.
        k = round(s["base_ini"] * fps)
        _ffmpeg("-ss", f"{max(0, (k - 0.5) / fps):.4f}", "-i", M.caminho_blob(s["fonte_sha"]), "-vf", f"fps={fps},scale={comp['w']}:{comp['h']}", "-frames:v", tocar, "-start_number", s["f0"] + 1, frames / "%04d.png")
        ultimo = frames / f"{s['f0'] + tocar:04d}.png"
        if not ultimo.exists():
            achados = sorted(frames.glob("*.png"))
            raise SystemExit(f"{s['rotulo']}: o clipe tem menos quadros que o esperado ({len(achados)} no total).")
        for f in range(s["f0"] + tocar, s["f1"]):  # quadro congelado: repete o último
            shutil.copyfile(ultimo, frames / f"{f + 1:04d}.png")
        print(f"   imagem: {s['rotulo']} ({n} quadros)", flush=True)


def exportar(slug):
    from media import motion

    from . import corte, fluxo, materiais as M
    from .banco import agora, faz
    fluxo.sincronizar(slug, forcar=True)  # o vídeo que será substituído entra no histórico antes, e continua consultável
    e = corte.carregar(slug)
    comp = corte.compilar(e)
    if comp["fontes_faltando"]:
        preparar_fontes(slug)
        comp = corte.compilar(e)
        if comp["fontes_faltando"]:
            raise SystemExit("Sem fonte de imagem para: " + ", ".join(comp["fontes_faltando"]))
    FONTES_TMP.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(dir=FONTES_TMP, prefix=slug[:20] + "-"))
    try:
        frames = pasta / "frames"
        frames.mkdir()
        print("▶ Preparando os quadros", flush=True)
        _extrair_quadros(comp, frames)
        print("▶ Compondo legendas e assets", flush=True)
        arq = pasta / "compilado.json"
        recursos = {m["sha"]: M.caminho_blob(m["sha"]).as_uri() for m in (s["midia"] for s in comp["segmentos"]) if m}
        arq.write_text(json.dumps({**comp, "recursos": recursos}, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["node", "corte_compor.mjs", "--compilado", str(arq), "--frames", str(frames)], cwd=REPO / "render", text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x08000000)
        print(r.stdout, flush=True)
        if r.returncode != 0:
            raise SystemExit(f"A composição falhou: {r.stdout[-600:]}")
        print("▶ Misturando o áudio", flush=True)
        corte.mixar(comp, pasta / "audio.wav")
        print("▶ Codificando", flush=True)
        motion._encode(pasta, comp["total_f"], comp["fps"])
        sha = M.sha_arquivo(pasta / "video.mp4")
        M.guardar_blob(pasta / "video.mp4", sha)
        faz("INSERT INTO exportacoes (slug, assinatura, video_sha, compilado, criada_em) VALUES (?,?,?,?,?)", slug, comp["assinatura"], sha, json.dumps(comp, ensure_ascii=False), agora())
        destino = M.pasta(slug) / "video.mp4"
        tmp = destino.with_suffix(".corte.tmp")
        shutil.copyfile(pasta / "video.mp4", tmp)
        tmp.replace(destino)
        print(f"   vídeo: {destino.name} ({comp['total_s']:.1f} s, {comp['total_f']} quadros)", flush=True)
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--fontes", action="store_true")
    a = ap.parse_args()
    if a.fontes:
        preparar_fontes(a.slug)
    else:
        exportar(a.slug)


if __name__ == "__main__":
    main()
