"""Arte procedural gratuita: cenas em silhueta geradas por código a partir de palavras-chave do prompt.

Não usa IA nem internet. É um substituto de demonstração para o Flux: serve para ver o pipeline
funcionando a custo zero, mas não tem a qualidade nem a variedade de um gerador de imagens de verdade.

Palavras-chave reconhecidas (em inglês, no prompt da cena):
  cenas exclusivas: globe, map, clock, crack
  paisagem: volcano, island, eruption, explosion, lava, plume, ash, smoke, lightning, sea, ship,
            village, tsunami, moon, sun, sunset, dawn, night, day, ember, blackout, stars
"""
import hashlib
import math
import random
import re

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1920, 1080

PALETTES = {  # (topo, meio, horizonte)
    "night": ((6, 8, 24), (18, 22, 56), (56, 44, 86)),
    "dawn": ((28, 24, 64), (150, 70, 80), (250, 160, 90)),
    "sunset": ((40, 16, 48), (170, 50, 50), (255, 150, 60)),
    "ember": ((18, 6, 10), (110, 24, 20), (235, 95, 30)),
    "ash": ((14, 14, 16), (46, 40, 38), (104, 80, 62)),
    "day": ((40, 90, 160), (110, 160, 210), (220, 230, 240)),
}


def _mix(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def _rng(prompt):
    return random.Random(int(hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8], 16))


def _to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _sky(pal):
    top, mid, bot = [np.array(c, dtype=np.float32) for c in pal]
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    a = np.clip(y / 0.55, 0, 1)
    b = np.clip((y - 0.55) / 0.45, 0, 1)
    col = np.where(y < 0.55, top * (1 - a) + mid * a, mid * (1 - b) + bot * b)
    return _to_img(np.broadcast_to(col, (H, W, 3)).copy())


def _glow(img, cx, cy, r, color, k=1.0):
    arr = np.asarray(img, dtype=np.float32).copy()
    x0, x1 = max(0, int(cx - r)), min(W, int(cx + r))
    y0, y1 = max(0, int(cy - r)), min(H, int(cy + r))
    if x1 <= x0 or y1 <= y0:
        return img
    yy, xx = np.ogrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2 * k
    arr[y0:y1, x0:x1] += a[..., None] * np.array(color, dtype=np.float32)
    return _to_img(arr)


def _over(img, layer):
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def _add_light(img, layer_rgb):
    return ImageChops.add(img, layer_rgb)


def _stars(img, rng, n=280):
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.62)
        b = rng.randint(110, 255)
        r = rng.choice([0.8, 1, 1, 1.4, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 15)))
    return img


def _plume(img, bx, by, height, spread, rng, glow=True):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lit, dark = (205, 120, 78), (78, 66, 68)
    n = 80
    for i in range(n):
        t = i / (n - 1)
        cx = bx + math.sin(t * 2.6 + rng.random()) * spread * 0.22 * t + rng.uniform(-1, 1) * spread * 0.05
        cy = by - t * height
        r = spread * (0.10 + 0.52 * (t ** 1.4)) * rng.uniform(0.8, 1.15)
        col = _mix(lit, dark, min(1.0, t * 1.25))
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=col + (205,))
    for _ in range(9):  # topo achatado, em forma de cogumelo
        cx = bx + rng.uniform(-0.25, 0.25) * spread
        cy = by - height * rng.uniform(0.93, 1.02)
        rx = spread * rng.uniform(0.7, 1.15)
        d.ellipse([cx - rx, cy - rx * 0.22, cx + rx, cy + rx * 0.22], fill=dark + (190,))
    layer = layer.filter(ImageFilter.GaussianBlur(16))
    img = _over(img, layer)
    if glow:
        img = _glow(img, bx, by - height * 0.08, spread * 1.3, (255, 110, 40), 0.55)
    return img


def _volcano(img, cx, base, w, h, rng):
    d = ImageDraw.Draw(img)
    cw = w * 0.06
    n = 16
    left, right = [], []
    for i in range(1, n):
        t = i / n
        yy = base - h * (t ** 0.85)
        left.append((cx - w / 2 + (w / 2 - cw) * t, yy + rng.uniform(-1, 1) * h * 0.02))
        right.append((cx + w / 2 - (w / 2 - cw) * t, yy + rng.uniform(-1, 1) * h * 0.02))
    pts = [(cx - w / 2, base + 12)] + left + [(cx - cw, base - h), (cx + cw, base - h * 0.97)] + right[::-1]
    pts.append((cx + w / 2, base + 12))
    d.polygon(pts, fill=(7, 7, 9))


def _lava(img, cx, base, h, w, rng):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(4):
        x, y = cx + rng.uniform(-0.05, 0.05) * w, base - h
        pts = [(x, y)]
        for _ in range(14):
            x += rng.uniform(-14, 24) * rng.choice([-1, 1])
            y += rng.uniform(10, 26)
            pts.append((x, y))
            if y > base - h * 0.35:
                break
        d.line(pts, fill=(255, 130, 40), width=4)
    soft = layer.filter(ImageFilter.GaussianBlur(9))
    return _add_light(_add_light(img, layer), soft)


def _lightning(img, x, y0, rng):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for branch in range(3):
        px, py = x + (0 if branch == 0 else rng.uniform(-30, 30)), y0 + (0 if branch == 0 else rng.uniform(40, 160))
        pts = [(px, py)]
        for _ in range(rng.randint(8, 14) if branch == 0 else rng.randint(4, 7)):
            px += rng.uniform(-34, 34) + (0 if branch == 0 else rng.choice([-18, 18]))
            py += rng.uniform(22, 44)
            pts.append((px, py))
        d.line(pts, fill=(235, 238, 255), width=4 if branch == 0 else 2)
    out = _add_light(img, layer)
    out = _add_light(out, layer.filter(ImageFilter.GaussianBlur(4)))
    return _add_light(out, layer.filter(ImageFilter.GaussianBlur(18)))


def _ocean(img, hy, hcol, rng, rough=1.0):
    arr = np.asarray(img, dtype=np.float32).copy()
    n = H - hy
    t = (np.arange(n, dtype=np.float32) / n)[:, None, None]
    top = np.array(_mix(hcol, (0, 0, 0), 0.45), dtype=np.float32)
    bot = np.array(_mix(hcol, (0, 0, 0), 0.9), dtype=np.float32)
    arr[hy:H] = top * (1 - t) + bot * t
    img = _to_img(arr)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    light = _mix(hcol, (255, 255, 255), 0.35)
    for k in range(70):
        f = (k / 70) ** 1.6
        y = hy + 6 + f * (n - 10)
        amp = 1.5 + 9 * f * rough
        freq = rng.uniform(0.006, 0.02) / (0.4 + f)
        x0 = rng.uniform(-100, W)
        length = rng.uniform(100, 420) * (0.5 + f)
        pts = [(x0 + i, y + math.sin((x0 + i) * freq + k) * amp) for i in range(0, int(length), 12)]
        if len(pts) > 1:
            d.line(pts, fill=light + (int(40 + 80 * f),), width=max(1, int(1 + 3 * f)))
    return _over(img, layer.filter(ImageFilter.GaussianBlur(1.2)))


def _tsunami(img, hy, rng):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    px = W * rng.uniform(0.50, 0.62)
    peak = H * 0.62
    floor = hy + (H - hy) * 0.30
    top_pts = []
    for x in range(0, W + 1, 6):
        u = (x - px) / (W * 0.30)
        top_pts.append((x, floor - peak * math.exp(-u * u * (0.55 if u < 0 else 9.0))))
    d.polygon(top_pts + [(W, H), (0, H)], fill=(8, 28, 38, 255))
    crest = [(x, y + 4) for x, y in top_pts if y < floor - peak * 0.30]
    if len(crest) > 2:
        d.line(crest, fill=(226, 236, 240, 235), width=9)
        for x, y in crest:
            if rng.random() < 0.6:
                r = rng.uniform(5, 15)
                d.ellipse([x - r, y - r + rng.uniform(0, 16), x + r, y + r + rng.uniform(0, 16)], fill=(232, 240, 244, 220))
    return _over(img, layer.filter(ImageFilter.GaussianBlur(2.2)))


def _ship(img, x, y, s):
    d = ImageDraw.Draw(img)
    d.polygon([(x, y), (x + 160 * s, y), (x + 132 * s, y + 34 * s), (x + 22 * s, y + 34 * s)], fill=(5, 5, 7))
    d.rectangle([x + 50 * s, y - 26 * s, x + 112 * s, y], fill=(5, 5, 7))
    d.rectangle([x + 72 * s, y - 58 * s, x + 90 * s, y - 26 * s], fill=(5, 5, 7))
    d.line([(x + 28 * s, y), (x + 28 * s, y - 78 * s)], fill=(5, 5, 7), width=max(2, int(3 * s)))
    d.line([(x + 135 * s, y), (x + 135 * s, y - 64 * s)], fill=(5, 5, 7), width=max(2, int(3 * s)))


def _village(img, rng, y):
    d = ImageDraw.Draw(img)
    d.polygon([(0, y + 40), (260, y + 10), (620, y + 24), (780, y + 70), (780, H), (0, H)], fill=(6, 6, 8))
    x = 30
    while x < 700:
        w, h = rng.randint(40, 64), rng.randint(28, 44)
        gy = y + 12 + (x / 700) * 14
        d.rectangle([x, gy - h, x + w, gy], fill=(6, 6, 8))
        d.polygon([(x - 6, gy - h), (x + w / 2, gy - h - 26), (x + w + 6, gy - h)], fill=(6, 6, 8))
        x += w + rng.randint(14, 34)


def _particles(img, rng, n, color, rmax=3.0, alpha=170):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.8, rmax)
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (rng.randint(alpha // 2, alpha),))
    return _over(img, layer.filter(ImageFilter.GaussianBlur(0.8)))


def _finish(img, rng):
    arr = np.asarray(img, dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    arr = arr * (1 - 0.42 * np.clip(d - 0.35, 0, 1) ** 1.5)[..., None]
    arr = arr + np.random.default_rng(rng.randint(0, 10 ** 6)).normal(0, 4.0, arr.shape).astype(np.float32)
    return _to_img(arr)


# ---------------- cenas exclusivas ----------------

def _globe(rng):
    img = _stars(_sky(PALETTES["night"]), rng, 380)
    cx, cy, r = W * 0.5, H * 0.5, H * 0.30
    img = _glow(img, cx, cy, r * 1.7, (50, 110, 255), 0.55)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - cx) / r, (yy - cy) / r
    rr = dx ** 2 + dy ** 2
    inside = rr < 1
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    light = np.clip(-0.5 * dx - 0.4 * dy + 0.75 * z, 0, 1)
    base = np.array([24, 70, 140], dtype=np.float32)
    rim = np.array([90, 150, 255], dtype=np.float32)
    col = base * (0.15 + 0.95 * light)[..., None] + rim * ((1 - z) ** 3)[..., None] * 0.9
    arr = np.asarray(img, dtype=np.float32).copy()
    arr[inside] = col[inside]
    img = _to_img(arr)
    px, py = cx - r * 0.35, cy + r * 0.05  # ponto da erupção
    img = _glow(img, px, py, 90, (255, 120, 40), 1.0)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(1, 9):
        R = r * 0.26 * k
        d.ellipse([px - R, py - R, px + R, py + R], outline=(255, 160, 80, max(50, 240 - 25 * k)), width=5)
    mask = Image.fromarray((inside * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return _over(_over(img, layer.filter(ImageFilter.GaussianBlur(5))), layer)


def _map(rng):
    arr = np.asarray(_sky(((8, 14, 30), (14, 24, 48), (20, 34, 62))), dtype=np.float32).copy()
    img = _to_img(arr)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 120):
        d.line([(x, 0), (x, H)], fill=(26, 40, 66), width=1)
    for y in range(0, H, 120):
        d.line([(0, y), (W, y)], fill=(26, 40, 66), width=1)
    ox, oy = W * 0.28, H * 0.56
    for cx, cy, rad in ((W * 0.22, H * 0.45, 150), (W * 0.16, H * 0.68, 190), (W * 0.36, H * 0.70, 120)):
        pts = []
        for k in range(28):
            a = k / 28 * 2 * math.pi
            rr = rad * rng.uniform(0.72, 1.12)
            pts.append((cx + math.cos(a) * rr * 1.5, cy + math.sin(a) * rr * 0.7))
        d.polygon(pts, fill=(24, 36, 54), outline=(60, 84, 118))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k in range(1, 9):
        R = 130 * k
        ld.ellipse([ox - R, oy - R, ox + R, oy + R], outline=(255, 150, 70, max(30, 230 - 26 * k)), width=3)
    tx, ty = W * 0.88, H * 0.40
    for t in range(0, 100, 2):
        a = t / 100
        ld.ellipse([ox + (tx - ox) * a - 2, oy + (ty - oy) * a - 2, ox + (tx - ox) * a + 2, oy + (ty - oy) * a + 2],
                   fill=(200, 220, 255, 150))
    img = _over(img, layer.filter(ImageFilter.GaussianBlur(1.0)))
    img = _glow(img, ox, oy, 140, (255, 120, 40), 1.0)
    return _glow(img, tx, ty, 90, (90, 200, 255), 0.9)


def _clock(rng):
    img = _glow(_sky(PALETTES["ember"]), W / 2, H * 0.55, 800, (255, 100, 40), 0.35)
    cx, cy, r = W / 2, H / 2, H * 0.34
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 8, 10), outline=(232, 204, 160), width=9)
    for k in range(60):
        a = math.radians(k * 6)
        l1 = r * (0.86 if k % 5 == 0 else 0.93)
        w = 6 if k % 5 == 0 else 2
        d.line([(cx + math.sin(a) * l1, cy - math.cos(a) * l1), (cx + math.sin(a) * r * 0.97, cy - math.cos(a) * r * 0.97)],
               fill=(232, 204, 160), width=w)
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for ang, length, width in (((10 + 2 / 60) * 30, r * 0.52, 16), (2 * 6, r * 0.78, 9)):  # 10h02
        a = math.radians(ang)
        ld.line([(cx, cy), (cx + math.sin(a) * length, cy - math.cos(a) * length)], fill=(240, 220, 180), width=width)
    ld.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(240, 220, 180))
    img = _add_light(img, layer)
    return _add_light(img, layer.filter(ImageFilter.GaussianBlur(12)))


def _window(rng):
    img = _glow(_sky(PALETTES["ember"]), W * 0.5, H * 0.78, 900, (255, 110, 40), 0.7)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = W * 0.2, H * 0.06, W * 0.8, H * 0.94
    t = 46
    d.rectangle([x0 - t, y0 - t, x1 + t, y0], fill=(8, 7, 8))
    d.rectangle([x0 - t, y1, x1 + t, y1 + t], fill=(8, 7, 8))
    d.rectangle([x0 - t, y0, x0, y1], fill=(8, 7, 8))
    d.rectangle([x1, y0, x1 + t, y1], fill=(8, 7, 8))
    d.rectangle([(x0 + x1) / 2 - 12, y0, (x0 + x1) / 2 + 12, y1], fill=(8, 7, 8))
    d.rectangle([x0, (y0 + y1) / 2 - 12, x1, (y0 + y1) / 2 + 12], fill=(8, 7, 8))
    cx, cy = W * 0.36, H * 0.34
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(16):
        a = rng.uniform(0, 2 * math.pi)
        pts, L, x, y = [], rng.uniform(260, 700), cx, cy
        steps = int(L // 30)
        for s in range(steps):
            a += rng.uniform(-0.18, 0.18)
            x, y = x + math.cos(a) * 30, y + math.sin(a) * 30
            pts.append((x, y))
        if pts:
            ld.line([(cx, cy)] + pts, fill=(235, 240, 245), width=3)
    for R in (90, 170, 270):
        pts = [(cx + math.cos(k / 24 * 2 * math.pi) * R * rng.uniform(0.92, 1.08),
                cy + math.sin(k / 24 * 2 * math.pi) * R * rng.uniform(0.92, 1.08)) for k in range(25)]
        ld.line(pts, fill=(200, 210, 220), width=2)
    img = _add_light(img, layer)
    return _add_light(img, layer.filter(ImageFilter.GaussianBlur(6)))


# ---------------- paisagem ----------------

def _landscape(has, rng, palname):
    pal = PALETTES[palname]
    img = _sky(pal)
    if palname == "night" or has("stars", "night"):
        img = _stars(img, rng)
    hy = int(H * rng.uniform(0.68, 0.74))
    vx = int(W * rng.uniform(0.38, 0.62))
    big = has("eruption", "explosion")
    vh = H * rng.uniform(0.27, 0.34)
    vw = W * 0.55
    if has("moon"):
        mx, my = W * rng.uniform(0.15, 0.3), H * rng.uniform(0.12, 0.25)
        img = _glow(img, mx, my, 260, (120, 140, 190), 0.8)
        ImageDraw.Draw(img).ellipse([mx - 52, my - 52, mx + 52, my + 52], fill=(228, 232, 240))
    if has("sun", "sunset", "dawn") and not has("blackout"):
        sx = W * rng.choice([rng.uniform(0.12, 0.28), rng.uniform(0.72, 0.88)])
        sy = hy - H * 0.05
        img = _glow(img, sx, sy, 520, (255, 150, 60), 1.0)
        ImageDraw.Draw(img).ellipse([sx - 70, sy - 70, sx + 70, sy + 70], fill=(255, 214, 150))
    has_volcano = has("volcano", "island", "eruption", "explosion", "lava")
    if has("plume", "eruption", "explosion", "ash", "smoke", "cloud"):
        ph = H * (0.62 if big else 0.42)
        img = _plume(img, vx, hy - (vh if has_volcano else 0), ph, W * (0.30 if big else 0.20), rng, glow=big)
    if has("lightning"):
        img = _lightning(img, vx + rng.uniform(-150, 150), hy - vh - H * 0.45, rng)
    if has_volcano:
        _volcano(img, vx, hy, vw, vh, rng)
        if has("lava", "eruption", "explosion"):
            img = _lava(img, vx, hy, vh, vw, rng)
    img = _ocean(img, hy, pal[2], rng, rough=1.6 if has("tsunami", "storm") else 1.0)
    if has("lava", "eruption", "explosion"):
        img = _glow(img, vx, hy + 70, 420, (255, 110, 40), 0.35)
    if has("tsunami"):
        img = _tsunami(img, hy, rng)
    if has("ship"):
        _ship(img, W * rng.uniform(0.12, 0.62), hy + H * 0.1, 1.7)
    if has("village", "houses"):
        _village(img, rng, hy + H * 0.12)
    if has("ash", "eruption", "explosion", "blackout"):
        img = _particles(img, rng, 500, (190, 180, 170), 2.6, 150)
    if has("ember", "lava", "eruption", "explosion"):
        img = _particles(img, rng, 90, (255, 140, 50), 2.4, 230)
    return img


def paint(prompt):
    rng = _rng(prompt)
    tags = set(re.findall(r"[a-z]+", prompt.lower()))

    def has(*words):
        return any(w in tags for w in words)

    if has("globe"):
        img = _globe(rng)
    elif has("map"):
        img = _map(rng)
    elif has("clock"):
        img = _clock(rng)
    elif has("crack"):
        img = _window(rng)
    else:
        if has("ash", "blackout", "darkness"):
            name = "ash"
        elif has("eruption", "explosion", "lava", "ember"):
            name = "ember"
        elif has("sunset"):
            name = "sunset"
        elif has("dawn", "morning"):
            name = "dawn"
        elif has("day", "calm"):
            name = "day"
        else:
            name = "night"
        from . import art2
        return art2.paint(prompt)  # renderizador cinematográfico
    return _finish(img, rng)
