"""Renderizador procedural "cinematográfico" (gratuito, sem IA): nuvens fBm, coluna de cinzas volumétrica
iluminada pelo fogo, bombas de lava, raios, reflexo no mar, bloom e correção de cor.

Continua sendo arte feita por código: fica bem mais dramática que silhuetas, mas NÃO é fotorrealista.
Para realismo de verdade use imagens de arquivo (Wikimedia Commons) ou Flux (fal/Cloudflare).
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080


# ---------------- ruído ----------------

def fbm(h, w, nrng, octaves=6, base=3, persist=0.55, aniso=1.0):
    """Ruído fractal normalizado em [0,1]. aniso>1 estica na horizontal (ondas, nuvens baixas)."""
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gh, gw = max(2, int(base * aniso * 2 ** o)), max(2, int(base * 2 ** o))
        g = nrng.random((gh, gw)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= persist
    out /= tot
    lo, hi = np.percentile(out, 1), np.percentile(out, 99)
    return np.clip((out - lo) / max(1e-6, hi - lo), 0, 1)


def blur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def vgrad(stops):
    """Gradiente vertical a partir de [(pos 0..1, (r,g,b)), ...]."""
    ys = np.linspace(0, 1, H, dtype=np.float32)
    pos = [s[0] for s in stops]
    cols = np.array([s[1] for s in stops], np.float32)
    ch = [np.interp(ys, pos, cols[:, i]) for i in range(3)]
    return np.stack(ch, -1)[:, None, :].repeat(W, 1).astype(np.float32)


# ---------------- céu ----------------

SKIES = {
    "night": [(0, (4, 6, 18)), (0.5, (14, 20, 46)), (1, (46, 48, 84))],
    "dawn": [(0, (22, 26, 62)), (0.45, (120, 78, 110)), (0.8, (246, 150, 96)), (1, (255, 190, 120))],
    "sunset": [(0, (24, 12, 40)), (0.4, (140, 40, 56)), (0.75, (250, 110, 50)), (1, (255, 170, 80))],
    "ember": [(0, (8, 4, 8)), (0.5, (52, 14, 14)), (0.85, (160, 50, 20)), (1, (230, 100, 30))],
    "ash": [(0, (8, 8, 10)), (0.5, (30, 24, 22)), (0.85, (92, 62, 44)), (1, (140, 90, 52))],
    "day": [(0, (34, 80, 150)), (0.6, (110, 160, 210)), (1, (214, 226, 238))],
}


def sky(pal, nrng, clouds=0.5, tint=(1, 1, 1)):
    base = vgrad(SKIES[pal])
    n = fbm(H, W, nrng, 6, 2, 0.58, aniso=2.2)
    n2 = fbm(H, W, nrng, 5, 3, 0.5, aniso=3.0)
    m = smooth(0.38, 0.8, n * 0.7 + n2 * 0.3) * clouds
    # nuvens mais escuras no topo, claras perto do horizonte iluminado
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    cloud_col = base * (0.42 + 0.5 * ys[..., None]) + vgrad(SKIES[pal]) * 0.1
    img = base * (1 - m[..., None]) + cloud_col * m[..., None]
    # bordas inferiores das nuvens pegam a luz do horizonte
    rim = np.clip(blur(m, 6) - blur(m, 1.5), 0, 1) * 4
    img += rim[..., None] * np.array(SKIES[pal][-1][1], np.float32) * 0.5
    return img * np.array(tint, np.float32)


def stars(img, nrng, n=420, ymax=0.6):
    layer = np.zeros((H, W), np.float32)
    xs, ys = nrng.integers(0, W, n), nrng.integers(0, int(H * ymax), n)
    layer[ys, xs] = nrng.random(n) ** 3 * 1.0 + 0.2
    layer = blur(layer, 0.8) * 9
    fade = np.clip(1 - np.linspace(0, 1, H)[:, None] / ymax, 0, 1)
    return img + (layer * fade)[..., None] * 230


# ---------------- vulcão ----------------

def volcano_mask(cx, base, w, h, nrng, crater=0.05):
    xs = np.arange(W, dtype=np.float32)
    u = np.clip(np.abs(xs - cx) / (w / 2), 0, 1)
    prof = np.clip(1 - u, 0, 1) ** 1.25
    rough = (fbm(1, W, nrng, 7, 6, 0.6)[0] - 0.5) * 0.16 * (0.3 + prof)
    top = base - h * np.clip(prof + rough * prof, 0, 1)
    # cratera: corte côncavo no topo
    notch = np.clip(1 - np.abs(xs - cx) / (w * crater), 0, 1)
    top = top + notch * h * 0.05
    yy = np.arange(H, dtype=np.float32)[:, None]
    mask = (yy >= top[None, :]) & (yy <= base + 4) & (u[None, :] < 1)
    return mask.astype(np.float32), top


# ---------------- coluna de cinzas ----------------

def plume(bx, by, ph, pw, nrng, fire=1.0, light_top=(95, 100, 125)):
    """Devolve (rgb premultiplicado de luz, alfa). Iluminação: fogo por baixo + luz fria por cima."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (by - yy) / ph
    warp = (fbm(H, W, nrng, 5, 3, 0.6) - 0.5) * pw * 0.55
    warp2 = (fbm(H, W, nrng, 5, 3, 0.6) - 0.5)
    sway = np.sin(t * 3.0 + 1.0) * pw * 0.10
    dx = np.abs(xx - bx - sway + warp * (0.3 + np.clip(t, 0, 1.2)))
    half = pw * (0.16 + 0.34 * np.clip(t, 0, 1) ** 0.7)
    # guarda-chuva no topo (cogumelo)
    cap = smooth(0.62, 0.98, t) * (1 - smooth(1.0, 1.18, t))
    half = half + cap * pw * 1.15 * (1 - np.abs(warp2) * 0.5)
    inside = np.clip((half - dx) / (half * 0.55 + 1), 0, 1)
    inside *= smooth(-0.02, 0.05, t) * (1 - smooth(1.02, 1.2, t) * (1 - cap))
    turb = fbm(H, W, nrng, 7, 4, 0.62)
    puff = 1 - np.abs(2 * fbm(H, W, nrng, 6, 5, 0.58) - 1)  # ridged: bordas de couve-flor
    fine = fbm(H, W, nrng, 6, 9, 0.6)
    field = inside * 1.25 + (turb - 0.5) * 0.85 + (puff - 0.5) * 0.7 + (fine - 0.5) * 0.35
    dens = smooth(0.30, 0.80, field) * (inside > 0.001)
    shade_h = np.clip(field, 0, 1.4) * (inside > 0.001)
    alpha = 1 - np.exp(-dens * 3.2)
    # transmitância: luz de baixo (fogo) e de cima
    cum_b = np.cumsum(dens[::-1], 0)[::-1] * (ph / H * 0.55)
    cum_t = np.cumsum(dens, 0) * (ph / H * 0.55)
    Tb, Tt = np.exp(-cum_b * 0.05), np.exp(-cum_t * 0.05)
    # puxa a luz do fogo para dentro por difusão
    Tb = np.clip(Tb * 0.55 + blur(Tb, 18) * 0.7, 0, 1)
    dist = np.sqrt(((xx - bx) / (pw * 1.6)) ** 2 + ((yy - by) / (ph * 0.95)) ** 2)
    glow = np.exp(-dist * 1.6) * fire
    fire_c = np.array([255, 118, 36], np.float32)
    hot_c = np.array([255, 205, 120], np.float32)
    base_c = np.array([34, 28, 30], np.float32)
    rgb = base_c[None, None] * (0.6 + 0.8 * turb[..., None])
    rgb = rgb + fire_c * (glow * Tb * 1.9)[..., None] + hot_c * (np.exp(-dist * 4.5) * Tb * 1.2 * fire)[..., None]
    # relevo falso: normais do campo de densidade (multi-escala) dão o aspecto de couve-flor
    bump = np.zeros_like(dens)
    for sg, wt in ((2.5, 1.0), (7, 1.2), (18, 1.0)):
        hgt = blur(shade_h, sg) * sg
        gy, gx = np.gradient(hgt)
        bump += -gy * wt
    down = np.clip(bump * 0.9, 0, 1)      # superfícies viradas para baixo: pegam o fogo
    up = np.clip(-bump * 0.9, 0, 1)       # viradas para cima: luz fria do céu
    rgb = rgb * (0.55 + 0.9 * (1 - np.clip(blur(dens, 10) * 1.2, 0, 1))[..., None])
    rgb = rgb + (fire_c * (glow * 2.6)[..., None] + hot_c * (np.exp(-dist * 3.0) * 1.2)[..., None]) * down[..., None] * (0.35 + 0.65 * Tb[..., None])
    rgb = rgb + np.array(light_top, np.float32) * (up * (0.5 + 0.9 * Tt))[..., None]
    edge = np.clip(dens - blur(dens, 4), 0, 1) * 2.5
    rgb = rgb + edge[..., None] * fire_c * (glow[..., None] * 1.2)
    alpha = np.clip(smooth(0.05, 0.55, alpha) * 1.05, 0, 1)
    return rgb, alpha


def composite(img, rgb, alpha):
    return img * (1 - alpha[..., None]) + rgb * alpha[..., None]


# ---------------- fogo, bombas, raios ----------------

def bombs(nrng, cx, cy, n, spread, upward, gravity=1.0, scale=1.0):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        ang = nrng.uniform(math.radians(58), math.radians(122))
        sp = nrng.uniform(0.35, 1.0) * upward
        vx, vy = math.cos(ang) * sp * spread, -math.sin(ang) * sp
        x, y = cx, cy
        pts = []
        g = 0.035 * gravity * upward / 20
        for k in range(70):
            pts.append((x, y))
            x += vx * 0.55
            y += vy * 0.55
            vy += g * 6
            if y > cy + 40:
                break
        life = nrng.uniform(0.5, 1.0)
        for i in range(len(pts) - 1):
            f = (i / max(1, len(pts) - 1))
            c = (int(255 * life * (1 - f * 0.55)), int(150 * life * (1 - f * 0.85)), int(40 * life * (1 - f)))
            d.line([pts[i], pts[i + 1]], fill=c, width=max(1, int((3.5 - 2 * f) * scale)))
        hx, hy = pts[-1] if f > 0.3 else pts[len(pts) // 2]
        r = nrng.uniform(2, 5) * scale
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 190, 90))
    a = np.asarray(layer, np.float32)
    return a + blur(a, 5) * 1.6 + blur(a, 16) * 1.2


def fire_core(cx, cy, r, intensity=1.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / (r * 0.9)) ** 2)
    a = np.exp(-d * 1.8) * intensity
    hot = np.exp(-d * 5) * intensity
    return (a[..., None] * np.array([255, 110, 30], np.float32) + hot[..., None] * np.array([255, 220, 160], np.float32))


def lightning(nrng, x, y0, length, branches=3):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)

    def bolt(x, y, ang, ln, w):
        pts = [(x, y)]
        steps = int(ln / 14)
        for _ in range(steps):
            ang += nrng.uniform(-0.45, 0.45)
            x += math.sin(ang) * 14
            y += math.cos(ang) * 14
            pts.append((x, y))
        d.line(pts, fill=(235, 235, 255), width=w, joint="curve")
        return pts

    main = bolt(x, y0, nrng.uniform(-0.2, 0.2), length, 3)
    for _ in range(branches):
        p = main[nrng.integers(len(main) // 4, len(main) - 2)]
        bolt(p[0], p[1], nrng.uniform(-1.0, 1.0), length * nrng.uniform(0.2, 0.45), 2)
    a = np.asarray(layer, np.float32)
    return a + blur(a, 4) * 2.2 + blur(a, 22) * 2.2 * np.array([0.7, 0.75, 1.0], np.float32)


def lava_flows(nrng, cx, top, base, w, mask):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(7):
        x, y = cx + nrng.uniform(-0.03, 0.03) * w, top
        pts = [(x, y)]
        side = nrng.choice([-1, 1])
        for _ in range(60):
            x += side * nrng.uniform(0.5, 5) + nrng.uniform(-3, 3)
            y += nrng.uniform(4, 11)
            pts.append((x, y))
            if y > base - 6 or nrng.random() < 0.018:
                break
        d.line(pts, fill=(255, 120, 30), width=int(nrng.integers(2, 5)))
    a = np.asarray(layer, np.float32) * mask[..., None]
    return a + blur(a, 3) * 1.5 + blur(a, 14) * 1.6


# ---------------- mar ----------------

def ocean(img, hy, nrng, rough=1.0, mirror=1.0):
    """Mar com reflexo real do que está acima do horizonte (fogo, céu, vulcão)."""
    out = img.copy()
    n = H - hy
    ys = np.arange(hy, H, dtype=np.float32)
    depth = (ys - hy) / n  # 0 horizonte .. 1 primeiro plano
    wave = (fbm(n, W, nrng, 6, 3, 0.6, aniso=9.0) - 0.5)
    wave2 = (fbm(n, W, nrng, 5, 6, 0.55, aniso=14.0) - 0.5)
    # reflexo: espelha linhas acima do horizonte, esticado
    src_y = hy - 1 - (depth ** 0.85) * (hy * 0.55)
    map_y = np.repeat(src_y[:, None], W, 1).astype(np.float32)
    map_x = (np.arange(W, dtype=np.float32)[None, :] + wave * (30 + 120 * depth[:, None]) * rough).astype(np.float32)
    refl = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    refl = blur(refl, 2.0)
    refl = cv2.GaussianBlur(refl, (0, 0), sigmaX=3, sigmaY=9)
    sea_col = vgrad([(0, (6, 10, 16)), (1, (2, 4, 8))])[:n] if False else np.array([5, 9, 15], np.float32)
    fres = (0.78 - 0.30 * depth)[:, None, None] * mirror
    ripple = 0.72 + 0.7 * np.clip(wave2 * 2 + 0.5, 0, 1)
    sea = sea_col[None, None] * (0.6 + depth[:, None, None]) + refl * fres * ripple[..., None]
    # faixa de brilho no horizonte
    hz = np.exp(-((ys - hy) / 6.0) ** 2)[:, None, None] * img[hy - 3:hy - 2].mean(1, keepdims=True) * 0.5
    out[hy:] = sea + hz
    return out


# ---------------- tsunami, navio, vila ----------------

def tsunami(img, hy, nrng, flip=False):
    """Onda gigante sobre o mar: face escura e translúcida, crista com espuma, base espumante e borrifo."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    X = xx if not flip else (W - xx)
    x0 = W * 0.60
    hw = H * 0.60
    up = smooth(0, 1, np.clip((X - W * 0.04) / (x0 - W * 0.04), 0, 1)) ** 1.7
    down = 1 - smooth(0, 1, np.clip((X - x0) / (W * 0.20), 0, 1)) ** 0.8
    prof = np.where(X < x0, up, down)
    jag = (fbm(1, W, nrng, 7, 9, 0.62)[0][None, :] - 0.5) * H * 0.06
    top = hy - hw * prof + jag * np.clip(prof * 3, 0, 1)
    base = hy + H * 0.17 + (fbm(1, W, nrng, 5, 8, 0.6)[0][None, :] - 0.5) * H * 0.03
    cover = smooth(0.02, 0.16, prof)
    mask = ((yy >= top) & (yy <= base)).astype(np.float32) * cover
    mask = blur(mask, 1.0)
    d = np.clip((yy - top) / (hw * 0.9), 0, 1.5)
    vstreak = fbm(H, W, nrng, 6, 5, 0.6, aniso=0.3)
    hrip = fbm(H, W, nrng, 6, 4, 0.6, aniso=3.0)
    sky_tint = img[int(H * 0.2), int(W * 0.5)] * 0.9 + 22
    shallow = np.array([70, 118, 124], np.float32) * (0.5 + 0.5 * min(1.5, sky_tint.mean() / 70))
    deep = np.array([2, 12, 20], np.float32)
    t = smooth(0.0, 0.75, d)[..., None]
    col = shallow * (1 - t) + deep * t
    col = col * (0.55 + 0.55 * vstreak[..., None] * (1 - t * 0.5) + 0.35 * hrip[..., None] * (1 - t))
    gy, gx = np.gradient(blur(mask, 7))
    col += np.clip(gy * 140, 0, 1)[..., None] * sky_tint * 0.9
    fn = fbm(H, W, nrng, 7, 10, 0.64)
    crest = smooth(0.40, 0.95, fn + (0.20 - d) * 3.2) * smooth(0.34, 0.0, d + (fn - 0.5) * 0.16)
    drips = smooth(0.58, 0.9, vstreak * 0.8 + fn * 0.4) * np.exp(-d * 3.2) * 0.8
    dbase = np.clip((yy - (base - H * 0.06)) / (H * 0.06), 0, 1)
    bfoam = smooth(0.30, 0.8, fn + dbase * 0.9 - 0.35) * dbase
    foam = np.clip(crest + drips + bfoam, 0, 1)
    col = col * (1 - foam[..., None]) + np.array([228, 236, 240], np.float32) * foam[..., None] * (0.5 + 0.5 * fn[..., None])
    out = img * (1 - mask[..., None]) + col * mask[..., None]
    spray = fbm(H, W, nrng, 6, 6, 0.6)
    near = np.exp(-np.clip(top - yy, 0, None) / (H * 0.09)) * (yy < top + 20) * smooth(0.3, 0.7, prof)
    mist = np.clip((spray - 0.42) * 2.6, 0, 1) * near
    out = out * (1 - mist[..., None] * 0.75) + sky_tint * 1.3 * (mist[..., None] * 0.75)
    nb = np.exp(-np.clip(yy - base, 0, None) / (H * 0.04)) * (yy >= base - 4) * smooth(0.2, 0.5, prof) * np.clip((spray - 0.4) * 3, 0, 1)
    out = out + nb[..., None] * np.array([160, 175, 185], np.float32) * 0.5
    return out, top


def ship(img, x, y, s=1.0, col=(3, 5, 8)):
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    u = 38 * s
    d.polygon([(x - 3 * u, y), (x + 3.4 * u, y), (x + 2.6 * u, y + 0.9 * u), (x - 2.4 * u, y + 0.9 * u)], fill=col)
    d.rectangle([x - 1.2 * u, y - 0.9 * u, x + 1.0 * u, y], fill=col)
    d.rectangle([x - 0.2 * u, y - 1.9 * u, x + 0.35 * u, y - 0.9 * u], fill=col)      # chaminé
    d.line([(x - 2.2 * u, y), (x - 2.2 * u, y - 2.6 * u)], fill=col, width=max(2, int(u * 0.12)))  # mastro
    d.line([(x + 2.4 * u, y), (x + 2.4 * u, y - 2.2 * u)], fill=col, width=max(2, int(u * 0.12)))
    for k in range(4):  # janelas acesas
        wx = x - 0.9 * u + k * 0.55 * u
        d.rectangle([wx, y - 0.6 * u, wx + 0.18 * u, y - 0.4 * u], fill=(255, 190, 90))
    return np.asarray(pil, np.float32)


def village(img, x0, x1, ybase, nrng, lit=True):
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    d.rectangle([x0 - 40, ybase, x1 + 40, ybase + H], fill=(4, 5, 7))
    x = x0
    while x < x1:
        w = float(nrng.uniform(50, 95))
        h = float(nrng.uniform(36, 62))
        d.polygon([(x, ybase), (x + w, ybase), (x + w, ybase - h), (x + w / 2, ybase - h - 34), (x, ybase - h)], fill=(4, 5, 7))
        if lit and nrng.random() < 0.5:
            d.rectangle([x + w * 0.4, ybase - h * 0.6, x + w * 0.58, ybase - h * 0.3], fill=(255, 180, 80))
        x += w + float(nrng.uniform(8, 30))
    return np.asarray(pil, np.float32)


# ---------------- pós-processamento ----------------

def grade(img, nrng, bloom=0.55, grain=0.035, vig=0.55, teal=0.10, contrast=1.1, flicker=1.0):
    a = img / 255.0
    # bloom: realça luzes
    hi = np.clip(a - 0.55, 0, 1)
    a = a + (blur(hi, 8) * 0.9 + blur(hi, 30) * 1.1 + blur(hi, 90) * 0.9) * bloom
    # curva filmica
    a = a * flicker
    a = a / (1 + a * 0.55) * 1.55
    a = np.clip(a, 0, 1) ** (1 / 1.05)
    a = (a - 0.5) * contrast + 0.5
    # teal nas sombras, quente nas luzes
    lum = a.mean(2, keepdims=True)
    a = a + (1 - lum) ** 2 * np.array([-teal * 0.6, teal * 0.15, teal], np.float32)
    a = a + lum ** 2 * np.array([0.04, 0.0, -0.04], np.float32)
    # vinheta
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.68)) ** 2)
    a = a * (1 - np.clip(r - 0.35, 0, 1) ** 1.6 * vig)[..., None]
    a = a + (nrng.standard_normal((H, W, 1)).astype(np.float32) * grain * (0.5 + 0.5 * (1 - lum)))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------- cenas ----------------

def scene(has, seed, pal):
    nrng = np.random.default_rng(seed)
    big = has("eruption", "explosion")
    close = has("close", "fountain")
    hy = int(H * float(nrng.uniform(0.70, 0.76)))
    vx = int(W * float(nrng.uniform(0.40, 0.60)))
    img = sky(pal, nrng, clouds=0.75 if not big else 0.45)
    if pal in ("night", "dawn") or has("stars"):
        img = stars(img, nrng, 450 if pal == "night" else 120)
    if has("moon"):
        mx, my = W * float(nrng.uniform(0.15, 0.3)), H * float(nrng.uniform(0.12, 0.25))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        img += (np.exp(-d / 150) * 70)[..., None] * np.array([0.6, 0.7, 1.0], np.float32)
        img += (smooth(56, 50, d))[..., None] * np.array([232, 236, 245], np.float32) * (0.9 + 0.1 * fbm(H, W, nrng, 4, 8)[..., None])
    if has("sun", "sunset", "dawn") and not has("blackout"):
        sx = W * float(nrng.choice([nrng.uniform(0.12, 0.3), nrng.uniform(0.7, 0.88)]))
        sy = hy - H * 0.04
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        img += (np.exp(-d / 220) * 210)[..., None] * np.array([1.0, 0.55, 0.22], np.float32)
        img += (np.exp(-d / 60) * 200)[..., None] * np.array([1.0, 0.85, 0.6], np.float32)
        img += smooth(66, 60, d)[..., None] * np.array([255, 235, 190], np.float32)

    has_v = has("volcano", "island", "eruption", "explosion", "lava")
    flick = 1.0
    if close:
        by = int(H * 1.0)
        rgb, al = plume(W * 0.5, by, H * 1.05, W * 0.33, nrng, fire=1.5)
        img = composite(img, rgb, al)
        img += fire_core(W * 0.5, by - 40, W * 0.30, 1.6)
        img += bombs(nrng, W * 0.5, by - 30, 90, 1.3, 38, scale=1.7)
        if has("lightning"):
            img += lightning(nrng, W * float(nrng.uniform(0.3, 0.7)), 0, H * 0.7)
        # bordas da cratera em primeiro plano (rocha escura)
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        pts = [(0, H)]
        for x in range(0, W + 40, 40):
            pts.append((x, H - 60 - 120 * abs(math.sin(x / 260.0 + 1)) * (0.4 + abs(x - W / 2) / W) - float(nrng.uniform(0, 30))))
        pts.append((W, H))
        d.polygon(pts, fill=255)
        mk = np.asarray(m, np.float32)[..., None] / 255
        img = img * (1 - mk) + np.array([5, 4, 5], np.float32) * mk
        return grade(img, nrng, bloom=0.8, flicker=1.05)

    if has_v:
        vh = H * float(nrng.uniform(0.20, 0.25) if big else nrng.uniform(0.27, 0.33))
        vw = W * 0.62
        mask, top = volcano_mask(vx, hy, vw, vh, nrng)
        crater_y = float(top[vx])
    if big:
        rgb, al = plume(vx, crater_y + 6, crater_y * 0.93, W * 0.27, nrng, fire=1.0)
        img = composite(img, rgb, al)
        img += fire_core(vx, crater_y, W * 0.12, 1.3)
        img += bombs(nrng, vx, crater_y, 55, 1.6, 30, scale=1.1)
        if has("lightning", "explosion"):
            for _ in range(2):
                img += lightning(nrng, vx + float(nrng.uniform(-260, 260)), crater_y - H * 0.55, H * 0.4)
        flick = 1.05
    elif has("plume", "ash", "smoke"):
        s = 0.55 if has("plume") else 0.3
        rgb, al = plume(vx, crater_y + 6 if has_v else hy, H * 0.55 * s * 2, W * 0.13 * s * 2, nrng,
                        fire=0.35 if pal in ("ember", "ash") else 0.0, light_top=(120, 110, 120))
        img = composite(img, rgb, al * (0.8 if has("smoke") else 1.0))
    if has_v:
        vol_col = np.array([5, 5, 7], np.float32)
        glow_below = has("lava", "eruption", "explosion")
        body = np.broadcast_to(vol_col, (H, W, 3)).copy()
        if glow_below:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            d = np.sqrt((xx - vx) ** 2 + (yy - crater_y) ** 2) / (vh * 1.1)
            body += (np.exp(-d * 2.2) * 120)[..., None] * np.array([1, 0.38, 0.1], np.float32) * (0.5 + 0.5 * fbm(H, W, nrng, 6, 6)[..., None])
        # ventos de luz (rim) na borda superior da silhueta
        rim = np.clip(mask - np.roll(mask, 3, 0), 0, 1)
        img = img * (1 - mask[..., None]) + body * mask[..., None]
        if glow_below:
            img += rim[..., None] * np.array([255, 130, 50], np.float32) * 0.8
            img += lava_flows(nrng, vx, crater_y, hy, vw, mask)
        elif pal in ("dawn", "sunset"):
            img += rim[..., None] * np.array([255, 150, 90], np.float32) * 0.5
    if has("ash", "blackout", "darkness") and not big:
        rgb, al = plume(W * 0.5, H * 1.05, H * 1.7, W * 0.9, nrng, fire=0.15, light_top=(90, 80, 80))
        img = composite(img, rgb, np.clip(al * 0.85, 0, 1))
    img = ocean(img, hy, nrng, rough=1.8 if has("tsunami", "storm") else 1.0, mirror=1.0)
    if has("tsunami"):
        img, _ = tsunami(img, hy, nrng)
    if has("village", "houses"):
        xa, xb = (W * 0.58, W * 0.97) if has("tsunami") else (W * 0.10, W * 0.90)
        img = village(img, xa, xb, hy + H * 0.14, nrng, lit=not has("ash", "darkness"))
    if has("ship"):
        img = ship(img, W * 0.84 if has("tsunami") else W * float(nrng.uniform(0.2, 0.7)), hy + H * 0.10, 1.25)
    return img, hy, nrng, flick


def paint(prompt, seed=None):
    import hashlib
    import re
    tags = set(re.findall(r"[a-z]+", prompt.lower()))

    def has(*w):
        return any(x in tags for x in w)
    if seed is None:
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
    if has("ash", "blackout", "darkness"):
        pal = "ash"
    elif has("eruption", "explosion", "lava", "ember", "fountain"):
        pal = "ember"
    elif has("sunset"):
        pal = "sunset"
    elif has("dawn", "morning"):
        pal = "dawn"
    elif has("day", "calm"):
        pal = "day"
    else:
        pal = "night"
    res = scene(has, seed, pal)
    if isinstance(res, Image.Image):
        return res  # cena de close já finalizada
    img, hy, nrng, flick = res
    return grade(img, nrng, bloom=0.6 if pal == "ember" else 0.45, flicker=flick)
