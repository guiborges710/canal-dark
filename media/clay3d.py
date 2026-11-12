"""Vídeo no estilo 3D low-poly (bonecos e cenários em three.js, renderizados no Chrome local), conduzido pela narração.

Entrada, em output/<slug>/cenas3d.json: lista de cenas
  {"fala": "texto para a voz (números por extenso)", "legenda": "texto da tela, com *destaque*", "duracao": N (mínimo),
   "env": "sala|rua|mesa|estudio", "camera": {...}, "atores": [...], "objetos": [...], "sons": [{"t": s, "tipo": "..."}]}
O vocabulário completo do motor está em render3d/engine.js (POSES, EXPR, PERSONAGENS, objetos, cenários).
Saída: video.mp4, thumbnail.jpg, audio.wav, eventos.json, cenas_render3d.json.
O áudio vem primeiro: a narração é gerada antes dos quadros, e cada cena dura o que a fala dura. A boca dos atores com
"fala": true abre conforme a energia da própria voz.

Uso:  python -m media.clay3d --slug <pasta> [--previa] [--sem-voz]
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import yaml

from . import motion, sfx, voz
from .sketch import _falas_salvas

ROOT = Path(__file__).resolve().parent.parent
RENDER = ROOT / "render3d" / "render3d.mjs"
SONS_OK = {"impact", "ding", "whoosh"}
PALAVRAS_POR_S = 3.0


class SpecErro(SystemExit):
    pass


def _estimar(c):
    return len(c["fala"].split()) / PALAVRAS_POR_S + 0.2


def validate(cenas, limite=(20.0, 60.0)):
    if not isinstance(cenas, list) or not cenas:
        raise SpecErro("cenas3d.json: lista vazia ou não é uma lista")
    total = 0.0
    for i, c in enumerate(cenas, 1):
        onde = f"cena {i}"
        for campo in ("fala", "legenda", "env"):
            if not isinstance(c.get(campo), str) or not c[campo].strip():
                raise SpecErro(f"{onde}: falta '{campo}'")
        if c["env"] not in {"sala", "rua", "mesa", "estudio"}:
            raise SpecErro(f"{onde}: env desconhecido: {c['env']}")
        cam = c.get("camera") or {}
        if not (len(cam.get("pos", [])) == 3 and len(cam.get("look", [])) == 3):
            raise SpecErro(f"{onde}: 'camera' precisa de pos e look com 3 números")
        if not isinstance(c.get("duracao"), (int, float)) or c["duracao"] < 1.5:
            raise SpecErro(f"{onde}: 'duracao' (mínimo da cena) deve ser número >= 1.5 s")
        for s in c.get("sons", []):
            if s.get("tipo") not in SONS_OK or not isinstance(s.get("t"), (int, float)):
                raise SpecErro(f"{onde}: 'sons' aceita {{\"t\": segundos, \"tipo\": {sorted(SONS_OK)}}}")
        total += max(c["duracao"], _estimar(c))
    lo, hi = limite
    if not lo <= total <= hi + 2:
        raise SpecErro(f"duração estimada {total:.0f} s fora do formato (de {lo:.0f} a {hi:.0f} s)")
    return total


def _envelope(wav, fps):
    """Energia da voz por quadro (0 a 1), para a boca dos atores."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "s16le", "-ac", "1", "-ar", "8000", "-"],
                       capture_output=True, check=True)
    x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    passo = 8000 // fps
    n = len(x) // passo
    if n == 0:
        return []
    rms = np.sqrt((x[: n * passo].reshape(n, passo) ** 2).mean(axis=1))
    ref = np.percentile(rms, 92) or 1.0
    env = np.clip(rms / ref, 0, 1)
    env = np.convolve(env, [0.25, 0.5, 0.25], mode="same")
    return [round(float(v), 2) for v in env]


def carregar_config():
    return yaml.safe_load((ROOT / "config_shorts.yaml").read_text(encoding="utf-8"))


def _spec(out, cenas, durs, falas, fps, voz_cfg):
    inicio_s = float((voz_cfg or {}).get("inicio_s", 0.05))
    lista = []
    for i, (c, d) in enumerate(zip(cenas, durs)):
        item = {k: v for k, v in c.items() if k not in ("fala", "sons", "duracao")}
        item["dur"] = d
        fala_s = falas[str(i)]["dur"] if str(i) in falas else _estimar(c)
        item["fala_ini"] = inicio_s
        item["fala_fim"] = round(inicio_s + fala_s, 3)
        item["env_fala"] = _envelope(falas[str(i)]["wav"], fps) if str(i) in falas else []
        lista.append(item)
    return {"fps": fps, "cenas": lista}


def _node(spec_path, frames_dir, so_quadros=None, workers=4):
    cmd = ["node", str(RENDER), "--spec", str(spec_path), "--out", str(frames_dir), "--workers", str(workers)]
    if so_quadros:
        cmd += ["--frames", ",".join(str(q) for q in so_quadros)]
    r = subprocess.run(cmd, cwd=ROOT / "render3d")
    if r.returncode != 0:
        raise SpecErro(f"Falha no render 3D (código {r.returncode})")


def previa(out, cfg):
    """3 quadros por cena numa folha de contato: previa.jpg (sem voz, sem vídeo)."""
    from PIL import Image
    out = Path(out)
    cenas = json.loads((out / "cenas3d.json").read_text(encoding="utf-8"))
    validate(cenas, (0, 999))
    fps = cfg["render"]["fps"]
    durs = [max(c["duracao"], _estimar(c)) for c in cenas]
    spec = _spec(out, cenas, durs, {}, fps, cfg.get("voz"))
    spec_path = out / "cenas_render3d.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    quadros, t0 = [], 0.0
    for d in durs:
        for p in (0.25, 0.6, 0.95):
            quadros.append(int((t0 + d * p) * fps))
        t0 += d
    pasta = out / "previa_frames"
    shutil.rmtree(pasta, ignore_errors=True)
    _node(spec_path, pasta, quadros)
    mini = (216, 384)
    colunas = 6
    linhas = (len(cenas) + 1) // 2
    folha = Image.new("RGB", (mini[0] * colunas, mini[1] * linhas), (255, 255, 255))
    for k, q in enumerate(quadros):
        i, j = divmod(k, 3)
        im = Image.open(pasta / f"{q + 1:04d}.png").convert("RGB").resize(mini, Image.LANCZOS)
        folha.paste(im, (((i % 2) * 3 + j) * mini[0], (i // 2) * mini[1]))
    destino = out / "previa.jpg"
    folha.save(destino, quality=88)
    shutil.rmtree(pasta, ignore_errors=True)
    print(f"   prévia: {destino} ({len(cenas)} cenas)")
    return destino


def render(out, cfg, sem_voz=False, workers=4):
    out = Path(out)
    cenas_path = out / "cenas3d.json"
    cenas = json.loads(cenas_path.read_text(encoding="utf-8"))
    r = cfg["render"]
    lo, hi = r.get("duracao_min_s", 20), r.get("duracao_max_s", 60)
    validate(cenas, (0, 9999))  # a duração só é conferida com a voz real, logo abaixo; a estimativa não barra a narração
    voz_cfg = cfg.get("voz")
    fps = r["fps"]

    falas = {}
    if not sem_voz:
        falas = _falas_salvas(out, cenas)
        if falas:
            print("   reaproveitando a narração já gerada (as falas não mudaram)", flush=True)
        else:
            print("   narrando as cenas (Chatterbox, CPU; leva alguns minutos)...", flush=True)
            falas = voz.gerar(out, cenas_path, voz_cfg)
            (out / "falas" / "textos.json").write_text(
                json.dumps([c["fala"] for c in cenas], ensure_ascii=False, indent=1), encoding="utf-8")
    inicio_s = float((voz_cfg or {}).get("inicio_s", 0.05))
    respiro_s = float((voz_cfg or {}).get("respiro_s", 0.12))
    durs = []
    for i, c in enumerate(cenas):
        fala_s = falas[str(i)]["dur"] if str(i) in falas else _estimar(c)
        durs.append(round(max(float(c["duracao"]), inicio_s + fala_s + respiro_s), 3))
    total_s = sum(durs)
    if not lo <= total_s <= hi:
        raise SpecErro(f"duração total {total_s:.1f} s fora do formato (de {lo:.0f} a {hi:.0f} s). Ajuste as falas.")
    spec = _spec(out, cenas, durs, falas, fps, voz_cfg)
    spec_path = out / "cenas_render3d.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")

    total_frames = round(total_s * fps)
    frames = out / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    print(f"   desenhando {total_frames} quadros 3D ({total_s:.1f} s, {fps} fps)...", flush=True)
    _node(spec_path, frames, workers=workers)

    eventos, t = [], 0.0
    for i, (c, d) in enumerate(zip(cenas, durs)):
        if i > 0:
            eventos.append({"frame": round(t * fps), "kind": "whoosh"})
        for s in c.get("sons", []):
            eventos.append({"frame": round((t + s["t"]) * fps), "kind": s["tipo"]})
        t += d
    eventos = [e for e in eventos if 0 <= e["frame"] < total_frames]
    (out / "eventos.json").write_text(json.dumps({"total": total_frames, "fps": fps, "eventos": eventos}, indent=1), encoding="utf-8")
    inicios, t = [], 0.0
    for d in durs:
        inicios.append(t)
        t += d
    falas_mix = [(inicios[int(k)] + inicio_s, v["wav"]) for k, v in falas.items()]
    sfx.build(eventos, total_frames, fps, out / "audio.wav", falas=falas_mix)
    video = motion._encode(out, total_frames, fps)
    motion._thumbnail(out)
    shutil.rmtree(frames, ignore_errors=True)
    print(f"   vídeo: {video.name} ({total_s:.0f} s, {total_frames} quadros{', com narração' if falas else ', mudo (teste)'})")
    return video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-voz", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    cfg = carregar_config()
    out = ROOT / "output" / a.slug
    if a.previa:
        previa(out, cfg)
    else:
        render(out, cfg, sem_voz=a.sem_voz, workers=a.workers)


if __name__ == "__main__":
    main()
