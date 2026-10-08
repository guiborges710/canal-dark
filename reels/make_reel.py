#!/usr/bin/env python3
"""Mini-fluxo de REELS (Instagram) — TOTALMENTE SEPARADO do canal do YouTube.

O conteúdo (roteiro + cenas + prompt de imagens em lote) é escrito à mão pela squad
no chat e salvo em reels/projetos/<slug>/cenas.json. As IMAGENS vêm de FORA (outra IA):
você gera lá, salva em reels/projetos/<slug>/imagens/ e roda este script, que só faz
narração (Kokoro local), legendas, música e a montagem 9:16. Nenhuma chamada a LLM aqui.

Uso:
  python reels/make_reel.py novo <slug>        # cria a pasta do projeto (esqueleto)
  python reels/make_reel.py <slug>             # monta o reel.mp4 (precisa das imagens)
  python reels/make_reel.py <slug> --mock      # testa sem Kokoro (tom senoidal)
  python reels/make_reel.py --vozes            # lista as vozes do Kokoro

cenas.json = [{"text": "frase narrada", "image_prompt": "prompt da imagem"}, ...]
As imagens em imagens/ são casadas por ordem alfabética do nome com as cenas (1 por cena).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # raiz do projeto (para achar media/, models/, music/)
sys.path.insert(0, str(ROOT))
import yaml  # noqa: E402

from media import render, tts  # noqa: E402  (helpers genéricos; não modificamos)
from media import captions as capmod  # noqa: E402
from media.util import duration, parallel  # noqa: E402

HERE = Path(__file__).resolve().parent
PROJ = HERE / "projetos"
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

ESQUELETO = [
    {"text": "Primeira frase narrada da cena um.", "image_prompt": "descrição da imagem da cena um"},
    {"text": "Segunda frase narrada da cena dois.", "image_prompt": "descrição da imagem da cena dois"},
]


def cfg():
    return yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))


def novo(slug):
    d = PROJ / slug
    (d / "imagens").mkdir(parents=True, exist_ok=True)
    cenas = d / "cenas.json"
    if not cenas.exists():
        cenas.write_text(json.dumps(ESQUELETO, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "prompt_imagens.txt").touch()
    print(f"Projeto criado em {d.relative_to(ROOT)}")
    print("  1) a squad preenche cenas.json e prompt_imagens.txt")
    print("  2) você gera as imagens na outra IA e salva em imagens/ (001.png, 002.png, ...)")
    print(f"  3) python reels/make_reel.py {slug}")


def imagens_do_projeto(d):
    return sorted(p for p in (d / "imagens").iterdir() if p.suffix.lower() in IMG_EXT)


def montar(slug, mock=False):
    c = cfg()
    d = PROJ / slug
    cenas_file = d / "cenas.json"
    if not cenas_file.exists():
        sys.exit(f"Não achei {cenas_file}. Rode primeiro: python reels/make_reel.py novo {slug}")
    scenes = json.loads(cenas_file.read_text(encoding="utf-8"))
    n = len(scenes)
    if n == 0:
        sys.exit("cenas.json está vazio.")

    for sub in ("audio", "clips", "imagens"):
        (d / sub).mkdir(exist_ok=True)

    imgs = imagens_do_projeto(d)
    if len(imgs) < n:
        if not mock:
            sys.exit(f"Faltam imagens: {n} cenas, só {len(imgs)} imagem(ns) em {d / 'imagens'}.\n"
                     "Salve uma imagem por cena (ordem alfabética do nome = ordem das cenas).")
        from media.util import run as _run          # --mock: placeholders cinza numerados
        w, h = c["render"]["width"], c["render"]["height"]
        for i in range(n):
            p = d / "imagens" / f"_mock_{i:03}.png"
            if not p.exists():
                _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x333844:s={w}x{h}",
                      "-frames:v", "1", str(p)])
        imgs = imagens_do_projeto(d)
    if len(imgs) > n:
        print(f"Aviso: {len(imgs)} imagens para {n} cenas; usando as {n} primeiras.")
    imgs = imgs[:n]

    print(f"[1/3] Narração ({n} cenas, voz {c['tts']['voice']})")
    audio = [d / "audio" / f"{i:03}.mp3" for i in range(n)]
    parallel(lambda a: tts.synth(c, scenes[a[0]]["text"], a[1], mock), list(enumerate(audio)))

    print("[2/3] Montando cenas")
    pause = c["tts"]["pause_seconds"]
    durs = [duration(a) + pause for a in audio]
    clips = [d / "clips" / f"{i:03}.mp4" for i in range(n)]
    for i in range(n):
        if not clips[i].exists():
            render.scene_clip(c, imgs[i], audio[i], durs[i], clips[i], i)

    srt = render.build_srt(scenes, durs, pause)
    caps = None
    if c["render"].get("captions"):
        cues = capmod.build_cues(scenes, durs, pause, capmod.caps_cfg(c)["max_words"])
        caps = capmod.render_captions(c, cues, d)
        print(f"      {len(caps)} blocos de legenda queimados")

    print("[3/3] Render final")
    final = render.assemble(c, clips, d, final_name="reel.mp4", srt_text=srt, captions=caps, total=sum(durs))
    print(f"\nPronto: {final.relative_to(ROOT)}  ({sum(durs):.0f}s, {n} cenas)")


def main():
    ap = argparse.ArgumentParser(description="Mini-fluxo de Reels (separado do canal).")
    ap.add_argument("slug", nargs="?", help="pasta do projeto em reels/projetos/")
    ap.add_argument("extra", nargs="?", help="slug quando o 1º argumento é 'novo'")
    ap.add_argument("--mock", action="store_true", help="sem Kokoro (tom senoidal); dispensa imagens")
    ap.add_argument("--vozes", action="store_true", help="lista as vozes do Kokoro e sai")
    args = ap.parse_args()

    if args.vozes:
        print("\n".join(tts.list_voices(cfg())))
        return
    if args.slug == "novo":
        if not args.extra:
            sys.exit("Uso: python reels/make_reel.py novo <slug>")
        novo(args.extra)
        return
    if not args.slug:
        ap.print_help()
        return
    montar(args.slug, mock=args.mock)


if __name__ == "__main__":
    main()
