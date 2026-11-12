"""Base dos estilos desenhados por camadas (Cartoon Vivo, Colagem Documental): sprites com pivô, matrizes, câmera e transições.

Cada parte (cabeça, braço, recorte, fita...) é desenhada uma vez, com antisserrilhado, e guardada como sprite RGBA. A cada quadro
as partes são recolocadas pela matriz delas: é o que permite mexer em cada camada sem redesenhar a cena nem achatar a imagem.
Tudo depende só do tempo local da cena: o mesmo `lt` dá sempre o mesmo quadro.
"""
import math
import os
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SEGURO_TOPO, SEGURO_BASE = 190, 1500
DENS = 1.5  # pixels do sprite por pixel do quadro: a câmera aproxima sem borrar
SS = 3  # superamostragem ao desenhar um sprite

_DIR_FONTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_F = "C:/Windows/Fonts/"
_LINUX = "/usr/share/fonts/truetype/dejavu/"
FONTES = {
    "impacto": [_F + "impact.ttf", _F + "ariblk.ttf", _F + "arialbd.ttf", _LINUX + "DejaVuSans-Bold.ttf"],
    "pesada": [_F + "ariblk.ttf", _F + "arialbd.ttf", _LINUX + "DejaVuSans-Bold.ttf"],
    "maquina": [_F + "courbd.ttf", _F + "consolab.ttf", _LINUX + "DejaVuSansMono-Bold.ttf"],
    "jornal": [_F + "georgiab.ttf", _F + "timesbd.ttf", _LINUX + "DejaVuSerif-Bold.ttf"],
    "mao": [os.path.join(_DIR_FONTES, "Kalam-Bold.ttf"), _F + "comicbd.ttf", _LINUX + "DejaVuSans-Bold.ttf"],
}


@lru_cache(maxsize=None)
def fonte(nome, tam):
    for caminho in FONTES[nome]:
        try:
            return ImageFont.truetype(caminho, int(tam))
        except OSError:
            continue
    return ImageFont.truetype(os.path.join(_DIR_FONTES, "Kalam-Bold.ttf"), int(tam))


# ---------- tempo ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def saida_rapida(x):
    return 1 - (1 - clamp(x)) ** 3


def mola(x):
    """Passa do alvo e volta (0 -> 1.1 -> 1)."""
    x = clamp(x)
    if x <= 0 or x >= 1:
        return x
    return 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2


def quique(x):
    x = clamp(x)
    if x < 1 / 2.75:
        return 7.5625 * x * x
    if x < 2 / 2.75:
        x -= 1.5 / 2.75
        return 7.5625 * x * x + 0.75
    if x < 2.5 / 2.75:
        x -= 2.25 / 2.75
        return 7.5625 * x * x + 0.9375
    x -= 2.625 / 2.75
    return 7.5625 * x * x + 0.984375


# ---------- matrizes 2D: (a, b, c, d, e, f) leva (x, y) a (a x + b y + c, d x + e y + f) ----------
IDENT = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)


def mul(m, n):
    a, b, c, d, e, f = m
    g, h, i, j, k, l = n
    return (a * g + b * j, a * h + b * k, a * i + b * l + c, d * g + e * j, d * h + e * k, d * i + e * l + f)


def mover(x, y):
    return (1.0, 0.0, float(x), 0.0, 1.0, float(y))


def girar(graus):
    r = math.radians(graus)
    c, s = math.cos(r), math.sin(r)
    return (c, -s, 0.0, s, c, 0.0)


def escalar(sx, sy=None):
    return (float(sx), 0.0, 0.0, 0.0, float(sx if sy is None else sy), 0.0)


def compor(*ms):
    r = IDENT
    for m in ms:
        r = mul(r, m)
    return r


def aplicar(m, x, y):
    return (m[0] * x + m[1] * y + m[2], m[3] * x + m[4] * y + m[5])


def _inversa(m):
    a, b, c, d, e, f = m
    det = a * e - b * d
    if abs(det) < 1e-9:
        return None
    return (e / det, -b / det, (b * f - c * e) / det, -d / det, a / det, (c * d - a * f) / det)


class Sprite:
    """Imagem com origem própria. `ox`, `oy` é o ponto da imagem que fica na origem local; `dens`, os pixels por unidade."""
    __slots__ = ("im", "ox", "oy", "dens", "opaco")

    def __init__(self, im, ox=0.0, oy=0.0, dens=DENS):
        self.im, self.ox, self.oy, self.dens = im, float(ox), float(oy), float(dens)
        self.opaco = im.mode == "RGB"

    def caixa(self):
        w, h = self.im.size
        return (-self.ox / self.dens, -self.oy / self.dens, (w - self.ox) / self.dens, (h - self.oy) / self.dens)

    def colar(self, quadro, m, alfa=1.0, filtro=Image.BICUBIC):
        if alfa <= 0.003:
            return
        x0, y0, x1, y1 = self.caixa()
        cantos = [aplicar(m, x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        bx0 = max(0, int(math.floor(min(c[0] for c in cantos))))
        by0 = max(0, int(math.floor(min(c[1] for c in cantos))))
        bx1 = min(quadro.width, int(math.ceil(max(c[0] for c in cantos))) + 1)
        by1 = min(quadro.height, int(math.ceil(max(c[1] for c in cantos))) + 1)
        if bx1 <= bx0 or by1 <= by0:
            return
        inv = _inversa(m)
        if inv is None:
            return
        d = self.dens
        dados = (inv[0] * d, inv[1] * d, (inv[0] * bx0 + inv[1] * by0 + inv[2]) * d + self.ox,
                 inv[3] * d, inv[4] * d, (inv[3] * bx0 + inv[4] * by0 + inv[5]) * d + self.oy)
        peca = self.im.transform((bx1 - bx0, by1 - by0), Image.AFFINE, dados, resample=filtro)
        if self.opaco:
            quadro.paste(peca, (bx0, by0))
            return
        if alfa < 0.997:
            a = peca.getchannel("A").point(lambda v: int(v * alfa))
            peca.putalpha(a)
        quadro.alpha_composite(peca, (bx0, by0))


def desenhar(x0, y0, x1, y1, fn, dens=DENS):
    """Sprite da região local (x0, y0)-(x1, y1). `fn(d, f)` desenha em unidades locais, com `f` convertendo cada ponto para a tela do rascunho."""
    w, h = max(1, int((x1 - x0) * dens)), max(1, int((y1 - y0) * dens))
    g = SS
    im = Image.new("RGBA", (w * g, h * g), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    esc = dens * g

    def f(px, py):
        return ((px - x0) * esc, (py - y0) * esc)

    fn(d, f, esc)
    return Sprite(im.resize((w, h), Image.LANCZOS), -x0 * dens, -y0 * dens, dens)


# ---------- traço de desenho ----------
def _catmull(pts, fechado, passos=8):
    n = len(pts)
    if n < 3:
        return list(pts)
    saida = []
    alcance = n if fechado else n - 1
    for i in range(alcance):
        p0 = pts[(i - 1) % n] if fechado or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if fechado or i + 2 < n else pts[-1]
        for k in range(passos):
            t = k / passos
            t2, t3 = t * t, t * t * t
            saida.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not fechado:
        saida.append(pts[-1])
    return saida


def irregular(pts, seed, amp=2.0):
    """Ondulação de baixa frequência: o contorno parece feito à mão, mas fica igual em todos os quadros."""
    rng = random.Random(seed)
    fa, fb, fc, fd = (rng.uniform(0, math.tau) for _ in range(4))
    saida = []
    for i, (x, y) in enumerate(pts):
        saida.append((x + amp * (math.sin(i * 0.31 + fa) + 0.5 * math.sin(i * 0.83 + fb)), y + amp * (math.sin(i * 0.27 + fc) + 0.5 * math.sin(i * 0.71 + fd))))
    return saida


def forma(d, f, esc, pts, cheio=None, contorno=None, w=8, seed=0, amp=1.6, fechado=True, curva=True):
    """Polígono com contorno grosso e levemente irregular."""
    base = _catmull(pts, fechado) if curva else _denso(pts, fechado)
    base = irregular(base, seed, amp)
    tela = [f(*p) for p in base]
    if cheio is not None and fechado:
        d.polygon(tela, fill=cheio)
    if contorno is not None and w > 0:
        linha(d, tela + ([tela[0]] if fechado else []), contorno, w * esc)


def _denso(pts, fechado, passo=26):
    saida = []
    ligados = list(pts) + ([pts[0]] if fechado else [])
    for (x0, y0), (x1, y1) in zip(ligados[:-1], ligados[1:]):
        n = max(1, int(math.dist((x0, y0), (x1, y1)) / passo))
        saida.extend((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n))
    if not fechado:
        saida.append(pts[-1])
    return saida


def linha(d, tela, cor, larg):
    larg = max(1, int(larg))
    d.line(tela, fill=cor, width=larg, joint="curve")
    r = larg / 2
    for x, y in (tela[0], tela[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=cor)


def circulo(cx, cy, rx, ry=None, n=14):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(math.tau * k / n), cy + ry * math.sin(math.tau * k / n)) for k in range(n)]


def retangulo(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


@lru_cache(maxsize=512)
def texto_sprite(s, nome_fonte, tam, cor, contorno=None, w_contorno=0, sombra=None, desloc=0):
    """Texto como sprite, com contorno e sombra sólida opcionais. A origem local é o centro do texto."""
    fo = fonte(nome_fonte, tam * DENS * 2)
    x0, y0, x1, y1 = fo.getbbox(s, stroke_width=int(w_contorno * DENS * 2))
    margem = int((w_contorno + desloc + 4) * DENS * 2)
    larg, alt = x1 - x0 + margem * 2, y1 - y0 + margem * 2
    im = Image.new("RGBA", (larg, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = (margem - x0, margem - y0)
    if sombra is not None:
        k = int(desloc * DENS * 2)
        d.text((p[0] + k, p[1] + k), s, font=fo, fill=sombra, stroke_width=int(w_contorno * DENS * 2), stroke_fill=sombra)
    d.text(p, s, font=fo, fill=cor, stroke_width=int(w_contorno * DENS * 2), stroke_fill=contorno)
    im = im.resize((max(1, larg // 2), max(1, alt // 2)), Image.LANCZOS)
    return Sprite(im, im.width / 2, im.height / 2)


# ---------- câmera ----------
def chave_em(chaves, lt, base):
    """Interpola as chaves {t, x, y, zoom, rot, curva}. `curva`: "suave" ou "rapida" (a chegada à chave vem num golpe)."""
    if not chaves:
        return dict(base)
    atual = {**base, **{k: v for k, v in chaves[0].items() if k in base}}
    if lt <= chaves[0].get("t", 0):
        return atual
    for a, b in zip(chaves[:-1], chaves[1:]):
        ta, tb = a.get("t", 0), b.get("t", 0)
        va = {**atual, **{k: v for k, v in a.items() if k in base}}
        vb = {**va, **{k: v for k, v in b.items() if k in base}}
        if lt <= tb:
            x = (lt - ta) / max(0.001, tb - ta)
            e = saida_rapida(x) if b.get("curva") == "rapida" else suave(x)
            return {k: va[k] + (vb[k] - va[k]) * e for k in base}
        atual = vb
    return atual


class Camera:
    """Cada camada tem um fator de parallax `p`: 1 acompanha a cena; menor fica mais longe e anda menos."""

    def __init__(self, x=W / 2, y=H / 2, zoom=1.0, rot=0.0, dx=0.0, dy=0.0):
        self.x, self.y, self.zoom, self.rot, self.dx, self.dy = x, y, zoom, rot, dx, dy

    def matriz(self, p=1.0):
        z = 1 + (self.zoom - 1) * p
        return compor(mover(W / 2 + self.dx * p, H / 2 + self.dy * p), girar(self.rot * p), escalar(z), mover(-(W / 2 + (self.x - W / 2) * p), -(H / 2 + (self.y - H / 2) * p)))


def tremida(lista, lt):
    """Soma as tremidas {t, forca}: amortecidas e sempre iguais para o mesmo `lt`."""
    dx = dy = 0.0
    for tr in lista or ():
        idade = lt - tr.get("t", 0)
        if 0 <= idade < 0.45:
            amp = tr.get("forca", 24) * (1 - idade / 0.45) ** 2
            dx += amp * math.sin(idade * 71 + tr.get("t", 0) * 13)
            dy += amp * 0.8 * math.sin(idade * 93 + tr.get("t", 0) * 7)
    return dx, dy


# ---------- entradas de objetos ----------
def entrada(tipo, lt, t0, dur=0.45, lado=1):
    """(dx, dy, sx, sy, alfa) do elemento. `salto` e `queda` achatam ao tocar o chão (squash-and-stretch)."""
    x = (lt - t0) / dur
    if x < 0:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    if x >= 1.5 or tipo in (None, "corte"):
        return (0.0, 0.0, 1.0, 1.0, 1.0)
    if tipo == "pop":
        e = mola(x)
        return (0.0, 0.0, max(0.001, e), max(0.001, e), 1.0)
    if tipo == "deslize":
        e = mola(x)
        return ((1 - e) * 900 * lado, 0.0, 1.0, 1.0, 1.0)
    if tipo == "queda":
        if x < 0.62:
            q = x / 0.62
            return (0.0, -1500 * (1 - q * q), 0.9, 1.14, 1.0)
        pos = (x - 0.62) / 0.88
        amortece = (1 - clamp(pos)) * math.cos(clamp(pos) * math.pi * 3)
        return (0.0, 0.0, 1 + 0.2 * amortece, 1 - 0.2 * amortece, 1.0)
    if tipo == "salto":
        if x < 0.75:
            q = x / 0.75
            return (0.0, 620 * (1 - q) - 760 * q * (1 - q) * 2, 0.92, 1.1, 1.0)
        pos = (x - 0.75) / 0.75
        amortece = (1 - clamp(pos)) * math.cos(clamp(pos) * math.pi * 3)
        return (0.0, 0.0, 1 + 0.16 * amortece, 1 - 0.16 * amortece, 1.0)
    raise ValueError(f"entrada desconhecida: {tipo}")


# ---------- fechamento em loop ----------
def fechar_loop(quadro, primeiro, x):
    """O primeiro quadro do vídeo entra deslizando e, em x = 1, a imagem é exatamente ele: o Short recomeça sem emenda aparente."""
    if x <= 0:
        return quadro
    if x >= 1:
        return primeiro.copy()
    e = suave(x)
    saida = quadro.copy()
    saida.paste(primeiro, (int(round(W * (1 - e))), 0))
    return saida


def borrar(im, r):
    return im.filter(ImageFilter.GaussianBlur(r))
