"""Texto na tela estilo 'viral' (CapCut): poucas palavras por vez, fonte pesada, contorno grosso.

Gera um PNG transparente do tamanho do vídeo para cada bloco de legenda; o render.py compõe
esses PNGs com o filtro `overlay` do FFmpeg (não precisa de libass/drawtext no build). A legenda
também continua indo para captions.srt como faixa separada, via render.build_srt.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Fontes pesadas que dão o visual "viral". A primeira que existir é usada.
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def caps_cfg(cfg):
    """Lê os ajustes de estilo do bloco render do config, com padrões de Short vertical."""
    r = cfg["render"]
    return {
        "size": r.get("caption_size", 0.06),            # altura da fonte como fração da altura do vídeo
        "y": r.get("caption_y", 0.72),                   # centro vertical do texto (fração da altura)
        "font": r.get("caption_font"),                   # caminho .ttf opcional; senão usa os candidatos
        "stroke": r.get("caption_stroke", 0.11),         # espessura do contorno como fração da fonte
        "color": r.get("caption_color", "#FFFFFF"),
        "stroke_color": r.get("caption_stroke_color", "#000000"),
        "uppercase": r.get("caption_uppercase", True),
        "max_words": r.get("caption_max_words", 3),      # palavras por bloco (poucas = mais viral)
    }


def _load_font(path, size):
    for p in ([path] if path else []) + FONT_CANDIDATES:
        if p and Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def build_cues(scenes, durs, pause, max_words=3):
    """Divide cada cena em blocos curtos e distribui o tempo falado entre eles.

    Devolve [(inicio, fim, texto)] em segundos, alinhado ao mesmo tempo da narração que o
    render usa para montar o vídeo (mesma lógica do build_srt, só que com blocos menores).
    """
    t, cues = 0.0, []
    for sc, d in zip(scenes, durs):
        words = sc["text"].split()
        if not words:
            t += d
            continue
        chunks = [words[i:i + max_words] for i in range(0, len(words), max_words)]
        speak = max(0.1, d - pause)
        cur = t
        for ch in chunks:
            dur = speak * len(ch) / len(words)
            cues.append((cur, cur + dur, " ".join(ch)))
            cur += dur
        t += d
    return cues


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if not cur or draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_cue_png(text, path, width, height, style):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = max(12, int(height * style["size"]))
    font = _load_font(style["font"], size)
    if style["uppercase"]:
        text = text.upper()
    margin = int(width * 0.08)
    lines = _wrap(d, text, font, width - 2 * margin)
    stroke = max(2, int(size * style["stroke"]))
    asc, desc = font.getmetrics()
    line_h = asc + desc + int(size * 0.12)
    total_h = line_h * len(lines)
    y0 = int(height * style["y"]) - total_h // 2
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=font)
        x = (width - tw) // 2
        y = y0 + i * line_h
        d.text((x, y), line, font=font, fill=style["color"],
               stroke_width=stroke, stroke_fill=style["stroke_color"])
    img.save(path)


def render_captions(cfg, cues, outdir):
    """Gera um PNG por bloco e devolve [(png, inicio, fim)] para o render compor."""
    style = caps_cfg(cfg)
    d = outdir / "captions"
    d.mkdir(parents=True, exist_ok=True)
    w, h = cfg["render"]["width"], cfg["render"]["height"]
    items = []
    for i, (s, e, txt) in enumerate(cues):
        p = d / f"{i:03}.png"
        render_cue_png(txt, p, w, h, style)
        items.append((p, s, e))
    return items
