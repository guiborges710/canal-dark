"""Estilo Colagem Documental: mural de evidências em papel, com recortes, fita, carimbo, marca-texto e câmera sobre a mesa.

Como no Cartoon Vivo, não há código por cena: o `cenas.json` descreve a mesa e os recortes, e este módulo compõe as camadas a cada
quadro. Toda textura e toda imagem nascem aqui, por código (grão de papel, xerox, retícula, silhuetas). Foto só entra se for arquivo
local do projeto, indicado em `arquivo`, e passa pelo mesmo duotone. Nada depende de mídia externa nem de serviço pago.

Contrato de uma cena (px no quadro de 1080x1920; o mural pode ir além da tela, a câmera anda sobre ele):
{"tipo": "documentary_collage", "desenho": "cena_0", "fala": "...", "duracao": 5, "acao": "o que a câmera revela, em uma frase",
 "superficie": "mesa_preta",
 "recortes": [{"id": "doc", "tipo": "documento", "x": 540, "y": 760, "larg": 760, "rot": -3, "t": 0.1, "entrada": "pousa", "fita": true,
               "titulo": "RELATÓRIO", "linhas": ["Em 2013: 7 horas", "Em 2021: menos de 3"]},
              {"id": "foto", "tipo": "foto", "figura": "pessoa", "x": 300, "y": 1200, "larg": 340, "rot": 4, "t": 0.8, "legenda": "Jovem, 24"}],
 "conexoes": [{"de": "foto", "para": "doc", "t": 1.4, "dur": 0.5}],
 "destaques": [{"em": "doc", "linha": 1, "t": 2.0, "dur": 0.5}],
 "carimbos": [{"texto": "CONFIRMADO", "x": 760, "y": 1040, "rot": -12, "t": 2.6}],
 "anotacoes": [{"texto": "caiu pela metade", "x": 620, "y": 1260, "t": 3.0, "seta_para": [540, 980]}],
 "textos": [{"texto": "MENOS DE 3 HORAS", "x": 540, "y": 330, "tam": 84, "t": 0.1}],
 "camera": {"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}, {"t": 3.0, "x": 560, "y": 900, "zoom": 1.3}], "tremidas": []},
 "transicao": {"entrada": "corte", "saida": "virada"}, "rotulos": [...], "sons": [...]}
"""
import hashlib
import math
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .camadas import DENS, SEGURO_BASE, SEGURO_TOPO, H, W, Camera, Sprite, aplicar, chave_em, clamp, compor, escalar, fechar_loop, fonte, girar, irregular, mola, mover, saida_rapida, suave, texto_sprite, tremida

MAX_TEXTO = 26
CAMPOS = {"acao", "superficie", "recortes", "conexoes", "destaques", "carimbos", "anotacoes", "textos", "camera", "transicao"}
PRETO, BEGE, BRANCO, VERMELHO, AMARELO = "#141312", "#E4D6B8", "#F5F1E6", "#C8281E", "#F2C230"
GRAFITE = "#3A3631"  # preto impresso sobre papel: é o mesmo preto com a tinta gasta
SUPERFICIES = {"mesa_preta": PRETO, "kraft": "#B99E74", "papel_bege": BEGE, "folha_branca": BRANCO}
TIPOS = ("documento", "jornal", "ficha", "foto", "mapa", "linha_tempo", "grafico", "data", "papel", "tira")
FIGURAS = ("pessoa", "grupo", "predio", "casa", "celular")
ENTRADAS = ("pousa", "desliza", "rasga", "corte")
TRANS_ENTRADA = ("corte", "virada", "recorte", "sobrepoe")
TRANS_SAIDA = ("corte", "virada", "recorte", "sobrepoe", "loop")
PARALLAX = {"fundo": 0.72, "meio": 0.9, "frente": 1.08}
DUR_TRANS = 0.36
DUR_LOOP = 0.5
_PASTA = {"caminho": None}


def definir_pasta(p):
    """Pasta do projeto: é só de lá que uma foto em `arquivo` pode vir."""
    _PASTA["caminho"] = Path(p)


# ---------- texturas ----------
@lru_cache(maxsize=None)
def _grao(w, h, seed, forca=9.0):
    rng = np.random.default_rng(seed)
    fino = rng.normal(0, forca, (h, w))
    grosso = np.asarray(Image.fromarray(rng.normal(0, forca * 0.55, (max(2, h // 24), max(2, w // 24))).astype("float32")).resize((w, h), Image.BICUBIC))
    return fino + grosso


def _texturizar(im, seed, forca=9.0, xerox=False):
    """Grão de papel; em `xerox`, também as manchas e riscos de fotocópia."""
    a = np.asarray(im.convert("RGB"), dtype="float32")
    g = _grao(im.width, im.height, seed, forca)
    if xerox:
        rng = np.random.default_rng(seed + 1)
        for _ in range(5):
            x = int(rng.integers(0, im.width))
            g[:, x:x + int(rng.integers(1, 3))] -= 16
    a = np.clip(a + g[..., None], 0, 255).astype("uint8")
    saida = Image.fromarray(a)
    if im.mode == "RGBA":
        saida = saida.convert("RGBA")
        saida.putalpha(im.getchannel("A"))
    return saida


def _reticula(cinza, passo=9):
    """Retícula de jornal: cada ponto cresce com o escuro da imagem."""
    a = np.asarray(cinza.convert("L"), dtype="float32") / 255.0
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    g = (np.sin((xx + yy) * math.pi / passo) * np.sin((xx - yy) * math.pi / passo) + 1) / 2
    return Image.fromarray((((a > g * 0.92 + 0.04)) * 255).astype("uint8"))


def _borda_rasgada(w, h, seed, amp=7, lados="b"):
    """Máscara do recorte: tesoura torta nos lados comuns e rasgo fino em `lados` (t, d, b, e)."""
    rng = random.Random(seed)
    k = 2
    im = Image.new("L", (w * k, h * k), 0)
    pts = []
    m = amp + 3

    def lado(x0, y0, x1, y1, rasgado):
        n = max(3, int(math.dist((x0, y0), (x1, y1)) / (14 if rasgado else 110)))
        nx, ny = (y1 - y0), -(x1 - x0)
        d = math.hypot(nx, ny) or 1
        for i in range(n):
            t = i / n
            a = rng.uniform(-amp, amp) if rasgado else rng.uniform(-amp * 0.55, amp * 0.55)
            pts.append(((x0 + (x1 - x0) * t + nx / d * a) * k, (y0 + (y1 - y0) * t + ny / d * a) * k))
    lado(m, m, w - m, m, "t" in lados)
    lado(w - m, m, w - m, h - m, "d" in lados)
    lado(w - m, h - m, m, h - m, "b" in lados)
    lado(m, h - m, m, m, "e" in lados)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return im.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=None)
def _mesa(nome):
    """Superfície maior que a tela: a câmera anda sobre ela sem ver a borda. Pouca densidade: fica ao fundo."""
    dens = 0.5
    w, h = int((W + 1600) * dens), int((H + 1600) * dens)
    im = Image.new("RGB", (w, h), SUPERFICIES[nome])
    forca = 5 if nome == "mesa_preta" else 9
    im = _texturizar(im, 90 + len(nome), forca)
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(len(nome))
    if nome != "mesa_preta":  # dobras do papel de fundo
        for _ in range(4):
            y = rng.randint(0, h)
            d.line([(0, y), (w, y + rng.randint(-20, 20))], fill=(0, 0, 0, 22), width=2)
    return Sprite(im, 800 * dens, 800 * dens, dens)


@lru_cache(maxsize=None)
def _retalhos(nome):
    """Papéis soltos ao fundo: é a camada que dá a sensação de profundidade quando a câmera anda."""
    saida = []
    rng = random.Random(7 + len(nome))
    cor = BEGE if nome == "mesa_preta" else BRANCO
    for k in range(6):
        w_, h_ = rng.randint(180, 340), rng.randint(120, 300)
        base = Image.new("RGB", (w_, h_), cor)
        d = ImageDraw.Draw(base)
        for y in range(20, h_ - 10, 22):
            d.line([(16, y), (rng.randint(w_ // 2, w_ - 16), y)], fill=GRAFITE, width=3)
        base = _texturizar(base, 200 + k, 12, xerox=True).convert("RGBA")
        base.putalpha(_borda_rasgada(w_, h_, 300 + k, 6, "bd").point(lambda v: int(v * (0.55 if nome == "mesa_preta" else 0.8))))
        saida.append((Sprite(base, w_ / 2, h_ / 2, 1.0), rng.randint(-160, W + 160), rng.randint(90, H - 100), rng.uniform(-26, 26)))
    return saida


# ---------- recortes ----------
class Peca:
    """Recorte pronto: imagem, sombra e onde ficam as linhas (é ali que o marca-texto passa)."""
    __slots__ = ("sprite", "sombra", "linhas", "larg", "alt")

    def __init__(self, sprite, sombra, linhas, larg, alt):
        self.sprite, self.sombra, self.linhas, self.larg, self.alt = sprite, sombra, linhas, larg, alt


def _quebrar(texto_, fo, larg):
    linhas, atual = [], ""
    for p in str(texto_).split():
        tentativa = f"{atual} {p}".strip()
        if fo.getlength(tentativa) > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = tentativa
    if atual:
        linhas.append(atual)
    return linhas


def _silhueta(figura, w, h):
    """Figura em tom de cinza, para virar retícula. Sem rosto: nunca representa uma pessoa real."""
    im = Image.new("L", (w, h), 196)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=int(208 - 60 * y / h))
    cx, cy = w / 2, h / 2
    r = min(w, h)
    if figura in ("pessoa", "grupo"):
        for dx, s in ([(0, 1.0)] if figura == "pessoa" else [(-0.28, 0.72), (0.28, 0.72), (0, 0.9)]):
            x = cx + dx * w
            d.ellipse((x - 0.17 * r * s, cy - 0.32 * r * s, x + 0.17 * r * s, cy + 0.02 * r * s), fill=32)
            d.rounded_rectangle((x - 0.3 * r * s, cy + 0.06 * r * s, x + 0.3 * r * s, h + 40), radius=int(0.14 * r), fill=32)
    elif figura == "predio":
        for k, (x, a) in enumerate(((0.1, 0.5), (0.36, 0.75), (0.66, 0.6))):
            d.rectangle((w * x, h * (1 - a), w * (x + 0.26), h), fill=36 + k * 12)
            for lin in range(int(a * 8)):
                d.rectangle((w * x + 12, h * (1 - a) + 14 + lin * 28, w * (x + 0.26) - 12, h * (1 - a) + 24 + lin * 28), fill=170)
    elif figura == "casa":
        d.rectangle((cx - 0.3 * w, cy, cx + 0.3 * w, h - 12), fill=40)
        d.polygon([(cx - 0.4 * w, cy), (cx, cy - 0.34 * h), (cx + 0.4 * w, cy)], fill=26)
        d.rectangle((cx - 0.07 * w, cy + 0.14 * h, cx + 0.07 * w, h - 12), fill=180)
    elif figura == "celular":
        d.rounded_rectangle((cx - 0.22 * w, 0.1 * h, cx + 0.22 * w, 0.92 * h), radius=18, fill=26)
        d.rectangle((cx - 0.18 * w, 0.16 * h, cx + 0.18 * w, 0.82 * h), fill=200)
    return im


def _foto(spec, w, h):
    """Foto em duotone reticulado. `arquivo` usa um asset local do projeto; sem ele, a figura é desenhada aqui."""
    arq = spec.get("arquivo")
    if arq and _PASTA["caminho"]:
        cinza = Image.open(_PASTA["caminho"] / arq).convert("L")
        r = max(w / cinza.width, h / cinza.height)
        cinza = cinza.resize((int(cinza.width * r) + 1, int(cinza.height * r) + 1), Image.LANCZOS)
        x, y = (cinza.width - w) // 2, (cinza.height - h) // 2
        cinza = cinza.crop((x, y, x + w, y + h))
    else:
        cinza = _silhueta(spec.get("figura", "pessoa"), w, h)
    pontos = _reticula(cinza)
    claro = spec.get("duotone", BEGE)
    return Image.composite(Image.new("RGB", (w, h), claro), Image.new("RGB", (w, h), PRETO), pontos)


def _chave_lru(spec):
    return tuple(sorted((k, repr(v)) for k, v in spec.items() if k in ("tipo", "larg", "titulo", "linhas", "manchete", "sub", "campos", "nome", "figura", "arquivo", "legenda", "duotone", "pinos", "eventos", "barras", "data", "texto", "cor", "id")))


_CACHE = {}


def peca_de(spec):
    chave = _chave_lru(spec)
    p = _CACHE.get(chave)
    if p is None:
        p = _CACHE[chave] = _construir(spec)
    return p


def _construir(spec):
    """Desenha o recorte em `DENS` e aplica textura, borda rasgada e sombra."""
    tipo = spec["tipo"]
    larg = spec.get("larg", 600)
    w = int(larg * DENS)
    seed = int(hashlib.md5(repr(_chave_lru(spec)).encode()).hexdigest()[:6], 16)
    k = DENS
    linhas_pos = []
    if tipo == "documento":
        fo_t, fo = fonte("maquina", 54 * k), fonte("maquina", 46 * k)
        conteudo = []
        for x in spec.get("linhas", []):
            conteudo += [(y, x) for y in _quebrar(x, fo, w - 110 * k)]
        alt = int(((160 if spec.get("titulo") else 70) + 68 * len(conteudo) + 70) * k)
        im = Image.new("RGB", (w, alt), BRANCO)
        d = ImageDraw.Draw(im)
        y = 46 * k
        if spec.get("titulo"):
            d.text((48 * k, y), spec["titulo"], font=fo_t, fill=PRETO)
            y += 70 * k
            d.line([(48 * k, y), (w - 48 * k, y)], fill=PRETO, width=int(4 * k))
            y += 30 * k
        for texto_, _ in conteudo:
            d.text((48 * k, y), texto_, font=fo, fill=GRAFITE)
            linhas_pos.append((48 * k, y, 48 * k + fo.getlength(texto_), y + 54 * k))
            y += 68 * k
        im = _texturizar(im, seed, 8, xerox=True)
    elif tipo == "jornal":
        fo_m, fo_s = fonte("jornal", 66 * k), fonte("jornal", 34 * k)
        manchete = _quebrar(spec.get("manchete", ""), fo_m, w - 80 * k)
        alt = int((90 + 78 * len(manchete) + (60 if spec.get("sub") else 0) + 230) * k)
        im = Image.new("RGB", (w, alt), BEGE)
        d = ImageDraw.Draw(im)
        y = 40 * k
        for x in manchete:
            d.text((40 * k, y), x, font=fo_m, fill=PRETO)
            linhas_pos.append((40 * k, y, 40 * k + fo_m.getlength(x), y + 70 * k))
            y += 78 * k
        if spec.get("sub"):
            d.text((40 * k, y), spec["sub"], font=fo_s, fill=GRAFITE)
            y += 56 * k
        d.line([(40 * k, y), (w - 40 * k, y)], fill=PRETO, width=int(3 * k))
        rng = random.Random(seed)
        col = (w - 110 * k) / 2
        for c in range(2):
            for lin in range(int((alt - y - 30 * k) / (22 * k))):
                x0 = 40 * k + c * (col + 30 * k)
                d.line([(x0, y + 24 * k + lin * 22 * k), (x0 + col * rng.uniform(0.82, 1), y + 24 * k + lin * 22 * k)], fill=GRAFITE, width=int(4 * k))
        im = _texturizar(im, seed, 10)
    elif tipo == "ficha":
        fo_n, fo_r, fo_v = fonte("maquina", 44 * k), fonte("maquina", 26 * k), fonte("maquina", 36 * k)
        campos = spec.get("campos", [])
        foto_l = int(larg * 0.32 * k)
        alt = max(int((120 + 90 * len(campos) + 40) * k), foto_l + int(150 * k))
        im = Image.new("RGB", (w, alt), BEGE)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w, 86 * k), fill=VERMELHO)
        d.text((32 * k, 18 * k), spec.get("nome", "FICHA"), font=fo_n, fill=BRANCO)
        im.paste(_foto({"figura": spec.get("figura", "pessoa"), "arquivo": spec.get("arquivo")}, foto_l, foto_l), (int(32 * k), int(118 * k)))
        d.rectangle((32 * k, 118 * k, 32 * k + foto_l, 118 * k + foto_l), outline=PRETO, width=int(3 * k))
        x0 = 32 * k + foto_l + 28 * k
        y = 112 * k
        for cp in campos:
            d.text((x0, y), str(cp.get("rotulo", "")).upper(), font=fo_r, fill=GRAFITE)
            d.text((x0, y + 30 * k), str(cp.get("valor", "")), font=fo_v, fill=PRETO)
            linhas_pos.append((x0, y + 30 * k, x0 + fo_v.getlength(str(cp.get("valor", ""))), y + 72 * k))
            y += 90 * k
        im = _texturizar(im, seed, 9)
    elif tipo == "foto":
        moldura = int(22 * k)
        alt_foto = int(w * spec.get("proporcao", 1.15))
        fo = fonte("mao", 36 * k)
        leg = int(66 * k) if spec.get("legenda") else moldura
        im = Image.new("RGB", (w, alt_foto + moldura + leg), BRANCO)
        im.paste(_foto(spec, w - moldura * 2, alt_foto), (moldura, moldura))
        d = ImageDraw.Draw(im)
        if spec.get("legenda"):
            d.text((w / 2, alt_foto + moldura + leg / 2), spec["legenda"], font=fo, fill=PRETO, anchor="mm")
        alt = im.height
        im = _texturizar(im, seed, 5)
    elif tipo == "mapa":
        alt = int(w * spec.get("proporcao", 1.0))
        im = Image.new("RGB", (w, alt), BEGE)
        d = ImageDraw.Draw(im)
        rng = random.Random(seed)
        for x in range(0, w, int(90 * k)):
            d.line([(x, 0), (x, alt)], fill="#CBBB99", width=2)
        for y in range(0, alt, int(90 * k)):
            d.line([(0, y), (w, y)], fill="#CBBB99", width=2)
        pts = []
        n = 34
        fa, fb = rng.uniform(0, 6), rng.uniform(0, 6)
        for i in range(n):
            a = math.tau * i / n
            r = 0.36 + 0.06 * math.sin(a * 3 + fa) + 0.035 * math.sin(a * 7 + fb)
            pts.append((w / 2 + w * r * math.cos(a), alt / 2 + alt * r * math.sin(a)))
        d.polygon(pts, fill=BRANCO, outline=PRETO)
        d.line(pts + [pts[0]], fill=PRETO, width=int(4 * k))
        for i in range(3):  # divisões internas: é um mapa esquemático, não geográfico
            a = rng.uniform(0, math.tau)
            d.line([(w / 2, alt / 2), (w / 2 + w * 0.34 * math.cos(a), alt / 2 + alt * 0.34 * math.sin(a))], fill=GRAFITE, width=int(2 * k))
        fo = fonte("maquina", 30 * k)
        for pino in spec.get("pinos", []):
            px, py = pino.get("x", 0.5) * w, pino.get("y", 0.5) * alt
            r = 13 * k
            d.ellipse((px - r, py - r, px + r, py + r), fill=VERMELHO, outline=PRETO, width=int(2 * k))
            if pino.get("rotulo"):
                d.text((px + 20 * k, py), pino["rotulo"], font=fo, fill=PRETO, anchor="lm")
        im = _texturizar(im, seed, 8)
    elif tipo == "linha_tempo":
        eventos = spec.get("eventos", [])
        alt = int((70 + 118 * len(eventos)) * k)
        im = Image.new("RGB", (w, alt), BRANCO)
        d = ImageDraw.Draw(im)
        x0 = 64 * k
        d.line([(x0, 40 * k), (x0, alt - 40 * k)], fill=PRETO, width=int(6 * k))
        fo_d, fo_t = fonte("maquina", 40 * k), fonte("maquina", 30 * k)
        for i, ev in enumerate(eventos):
            y = (46 + i * 118) * k
            d.ellipse((x0 - 16 * k, y, x0 + 16 * k, y + 32 * k), fill=VERMELHO, outline=PRETO, width=int(3 * k))
            d.text((x0 + 42 * k, y - 8 * k), str(ev.get("data", "")), font=fo_d, fill=PRETO)
            d.text((x0 + 42 * k, y + 40 * k), str(ev.get("texto", "")), font=fo_t, fill=GRAFITE)
            linhas_pos.append((x0 + 42 * k, y - 8 * k, x0 + 42 * k + fo_d.getlength(str(ev.get("data", ""))), y + 38 * k))
        im = _texturizar(im, seed, 7, xerox=True)
    elif tipo == "grafico":
        barras = spec.get("barras", [])
        alt = int(w * spec.get("proporcao", 0.8))
        im = Image.new("RGB", (w, alt), BRANCO)
        d = ImageDraw.Draw(im)
        fo_t, fo_r = fonte("maquina", 38 * k), fonte("maquina", 30 * k)
        if spec.get("titulo"):
            d.text((36 * k, 26 * k), spec["titulo"], font=fo_t, fill=PRETO)
        base = alt - 76 * k
        d.line([(36 * k, base), (w - 36 * k, base)], fill=PRETO, width=int(5 * k))
        im = _texturizar(im, seed, 7)
    elif tipo == "data":
        fo = fonte("jornal", 96 * k)
        tx = str(spec.get("data", ""))
        w = int(fo.getlength(tx) + 90 * k)
        alt = int(160 * k)
        im = Image.new("RGB", (w, alt), AMARELO)
        ImageDraw.Draw(im).text((w / 2, alt / 2), tx, font=fo, fill=PRETO, anchor="mm")
        im = _texturizar(im, seed, 8)
    elif tipo == "tira":
        fo = fonte("impacto", spec.get("tam", 72) * k)
        tx = str(spec.get("texto", ""))
        w = int(fo.getlength(tx) + 76 * k)
        alt = int(spec.get("tam", 72) * k * 1.6)
        fundo = spec.get("cor", PRETO)
        im = Image.new("RGB", (w, alt), fundo)
        ImageDraw.Draw(im).text((w / 2, alt / 2), tx, font=fo, fill=BRANCO if fundo in (PRETO, VERMELHO) else PRETO, anchor="mm")
        linhas_pos.append((38 * k, alt * 0.12, w - 38 * k, alt * 0.88))
        im = _texturizar(im, seed, 7)
    else:  # papel
        alt = int(w * spec.get("proporcao", 1.3))
        im = _texturizar(Image.new("RGB", (w, alt), spec.get("cor", BEGE)), seed, 10)
    margem = int(14 * k)
    tela = Image.new("RGBA", (w + margem * 2, alt + margem * 2), (0, 0, 0, 0))
    tela.paste(im, (margem, margem))
    mascara = _borda_rasgada(tela.width, tela.height, seed, 8, spec.get("rasgo", {"jornal": "bd", "documento": "b", "ficha": "", "foto": "", "tira": "de", "data": "e"}.get(tipo, "b")))
    tela.putalpha(mascara)
    claro = mascara.filter(ImageFilter.MinFilter(5))  # fibra branca na borda, como em papel de verdade
    fibra = ImageChops.subtract(mascara, claro)
    tela.paste((248, 244, 234, 255), (0, 0), fibra)
    linhas_pos = [(a + margem, b + margem, c + margem, e + margem) for a, b, c, e in linhas_pos]
    sprite = Sprite(tela, tela.width / 2, tela.height / 2, k)
    sombra_im = Image.new("RGBA", (tela.width // 3 + 12, tela.height // 3 + 12), (0, 0, 0, 0))
    sombra_a = mascara.resize((tela.width // 3, tela.height // 3), Image.BILINEAR)
    sombra_im.paste((0, 0, 0, 165), (6, 6), sombra_a)
    sombra_im = sombra_im.filter(ImageFilter.GaussianBlur(4))
    sombra = Sprite(sombra_im, sombra_im.width / 2, sombra_im.height / 2, k / 3)
    return Peca(sprite, sombra, linhas_pos, tela.width / k, tela.height / k)


@lru_cache(maxsize=None)
def _fita(largura, seed):
    """Fita adesiva translúcida, com pontas serrilhadas."""
    w, h = int(largura * DENS), int(46 * DENS)
    base = _texturizar(Image.new("RGB", (w, h), "#E9D98F"), seed, 6)
    m = _borda_rasgada(w, h, seed, 4, "de").point(lambda v: int(v * 0.72))
    base = base.convert("RGBA")
    base.putalpha(m)
    return Sprite(base, 0, h / 2, DENS)


@lru_cache(maxsize=256)
def _marca_texto(larg_px, alt_px, seed):
    rng = random.Random(seed)
    w, h = max(2, int(larg_px)), max(2, int(alt_px))
    a = np.full((h, w, 4), 0, "uint8")
    cor = tuple(int(AMARELO[i:i + 2], 16) for i in (1, 3, 5))
    a[..., 0], a[..., 1], a[..., 2] = cor
    for x in range(w):
        topo = int(h * 0.04 + 3 * math.sin(x * 0.02 + seed) + rng.uniform(-1, 1))
        base = int(h * 0.96 + 3 * math.sin(x * 0.017 + seed * 2) + rng.uniform(-1, 1))
        a[max(0, topo):min(h, base), x, 3] = 128
    return Image.fromarray(a)


@lru_cache(maxsize=128)
def _carimbo(texto_, cor, seed):
    fo = fonte("impacto", 84 * DENS)
    largura = int(fo.getlength(texto_) + 96 * DENS)
    alt = int(150 * DENS)
    im = Image.new("L", (largura, alt), 0)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8 * DENS, 8 * DENS, largura - 8 * DENS, alt - 8 * DENS), radius=int(16 * DENS), outline=255, width=int(9 * DENS))
    d.text((largura / 2, alt / 2), texto_, font=fo, fill=255, anchor="mm")
    rng = np.random.default_rng(seed)  # tinta falhada: carimbo não sai uniforme
    ruido = np.asarray(Image.fromarray(rng.random((alt // 3, largura // 3)).astype("float32")).resize((largura, alt), Image.BICUBIC))
    a = np.asarray(im, dtype="float32") * np.clip((ruido + 0.32) * 1.6, 0.0, 0.95)
    saida = Image.new("RGBA", (largura, alt), cor)
    saida.putalpha(Image.fromarray(a.astype("uint8")))
    return Sprite(saida, largura / 2, alt / 2)


@lru_cache(maxsize=128)
def _folha_transicao(tipo):
    cor = BEGE
    w, h = W + 220, H + 220
    base = _texturizar(Image.new("RGB", (w // 2, h // 2), cor), 13, 9, xerox=True).convert("RGBA")
    if tipo == "recorte":
        base.putalpha(_borda_rasgada(w // 2, h // 2, 14, 22, "tdbe"))
    return Sprite(base, w / 4, h / 4, 0.5)


# ---------- animação de cada recorte ----------
def _pouso(tipo, lt, t0, abertura, lado):
    """(dx, dy, escala, giro extra, sombra, revelação 0-1). A sombra se abre com o papel ainda no ar e fecha ao pousar."""
    if abertura and t0 <= 0:
        return (0, 0, 1, 0, 1.0, 1.0)
    if lt < t0:
        return None
    x = (lt - t0) / 0.42
    if tipo == "corte" or x >= 1:
        return (0, 0, 1, 0, 1.0, 1.0)
    if tipo == "pousa":
        e = saida_rapida(x)
        return (0, -90 * (1 - e), 1 + 0.32 * (1 - e), 7 * (1 - e) * lado, 2.6 - 1.6 * e, 1.0)
    if tipo == "desliza":
        e = mola(x)
        return ((1 - e) * 1000 * lado, 26 * (1 - e), 1.0, 5 * (1 - e) * lado, 1.6 - 0.6 * e, 1.0)
    if tipo == "rasga":
        return (0, 0, 1, 0, 1.0, suave(x))
    raise ValueError(tipo)


def _rasgar(sprite, rev, seed):
    """Revela o papel com uma frente irregular, como se a folha de cima estivesse sendo rasgada."""
    im = sprite.im
    w, h = im.size
    rng = random.Random(seed)
    frente = rev * (w + h * 0.35)
    pts = [(0, 0)]
    n = 26
    for i in range(n + 1):
        y = h * i / n
        pts.append((frente - y * 0.35 + rng.uniform(-13, 13), y))
    pts.append((0, h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    a = ImageChops.multiply(im.getchannel("A"), m)
    saida = im.copy()
    saida.putalpha(a)
    borda = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(13)), m)
    papel = Image.new("RGBA", (w, h), (248, 244, 234, 255))
    papel.putalpha(ImageChops.multiply(borda, im.getchannel("A")))
    saida.alpha_composite(papel)
    return Sprite(saida, sprite.ox, sprite.oy, sprite.dens)


def _matriz_recorte(cam, r, an):
    dx, dy, esc, giro, *_ = an
    p = PARALLAX.get(r.get("camada", "meio"), 0.9)
    return compor(cam.matriz(p), mover(r.get("x", 540) + dx, r.get("y", 960) + dy), girar(r.get("rot", 0) + giro), escalar(esc))


def _camera(cena, lt, dur):
    c = cena.get("camera") or {}
    v = chave_em(c.get("chaves"), lt, {"x": W / 2, "y": H / 2, "zoom": 1.0, "rot": 0.0})
    if not c.get("chaves"):  # sem chaves, um travelling lento: o mural nunca fica parado
        v["zoom"] = 1.0 + 0.05 * lt / max(dur, 0.1)
        v["y"] += 34 * lt / max(dur, 0.1)
    else:  # depois da última chave a câmera não para de vez: papel parado por um segundo parece imagem congelada
        fim = max(ch.get("t", 0) for ch in c["chaves"])
        if lt > fim:
            v["zoom"] *= 1 + 0.018 * (lt - fim)
            v["y"] += 7 * (lt - fim)
    dx, dy = tremida(c.get("tremidas"), lt)
    for k in cena.get("carimbos", ()):  # o carimbo bate na mesa: pequeno impacto automático
        t = lt - k.get("t", 0)
        if 0 <= t < 0.2:
            amp = 12 * (1 - t / 0.2) ** 2
            dx += amp * math.sin(t * 90)
            dy += amp * math.sin(t * 73)
    return Camera(v["x"], v["y"], v["zoom"], v["rot"], dx, dy)


def _ponto(cam, recortes, ident, anima):
    r = recortes.get(ident)
    if not r:
        return None
    return aplicar(_matriz_recorte(cam, r, anima.get(ident, (0, 0, 1, 0))), r.get("ax", 0), r.get("ay", 0))


def _desenhar_conexao(quadro, a, b, x, cor=VERMELHO):
    """Barbante: uma curva com leve barriga, que cresce de um ponto ao outro. Desenhado com superamostragem só na área dele."""
    if x <= 0:
        return
    n = 24
    meio = math.dist(a, b) * 0.08
    pts = []
    for i in range(int(n * x) + 1):
        t = i / n
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + meio * math.sin(t * math.pi)))
    if len(pts) < 2:
        return
    x0, y0 = max(0, int(min(p[0] for p in pts)) - 30), max(0, int(min(p[1] for p in pts)) - 30)
    x1, y1 = min(W, int(max(p[0] for p in pts)) + 30), min(H, int(max(p[1] for p in pts)) + 30)
    if x1 <= x0 or y1 <= y0:
        return
    g = 2
    im = Image.new("RGBA", ((x1 - x0) * g, (y1 - y0) * g), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tela = [((px - x0) * g, (py - y0) * g) for px, py in pts]
    d.line([(px + 3 * g, py + 5 * g) for px, py in tela], fill=(0, 0, 0, 90), width=6 * g, joint="curve")
    d.line(tela, fill=cor, width=6 * g, joint="curve")
    for (px, py) in (tela[0], tela[-1]):
        d.ellipse((px - 12 * g, py - 12 * g, px + 12 * g, py + 12 * g), fill=cor, outline=PRETO, width=2 * g)
    quadro.alpha_composite(im.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))


@lru_cache(maxsize=128)
def _anotacao_sprite(texto_, cor):
    return texto_sprite(texto_, "mao", 62, cor)


def compor_cena(cena, lt, dur, abertura=False):
    quadro = Image.new("RGBA", (W, H), PRETO)
    cam = _camera(cena, lt, dur)
    sup = cena.get("superficie", "mesa_preta")
    _mesa(sup).colar(quadro, cam.matriz(0.32), filtro=Image.BILINEAR)
    for s, x, y, rot in _retalhos(sup):
        s.colar(quadro, compor(cam.matriz(0.52), mover(x, y), girar(rot)), filtro=Image.BILINEAR)
    recortes = {r["id"]: r for r in cena.get("recortes", ())}
    anima = {}
    lado = {}
    for i, r in enumerate(cena.get("recortes", ())):
        lado[r["id"]] = 1 if r.get("x", 540) > W / 2 else -1
        an = _pouso(r.get("entrada", "pousa"), lt, r.get("t", 0), abertura, lado[r["id"]])
        if an is None:
            continue
        anima[r["id"]] = an
    ordem = sorted(cena.get("recortes", ()), key=lambda r: {"fundo": 0, "meio": 1, "frente": 2}.get(r.get("camada", "meio"), 1))
    for r in ordem:
        an = anima.get(r["id"])
        if not an:
            continue
        peca = peca_de(r)
        m = _matriz_recorte(cam, r, an)
        solta = an[4]
        m_sombra = compor(mover(8 * solta, 12 * solta), m, escalar(1 + 0.02 * (solta - 1)))
        if an[5] >= 1:
            peca.sombra.colar(quadro, m_sombra, alfa=clamp(0.95 - 0.16 * (solta - 1)), filtro=Image.BILINEAR)
        sprite = peca.sprite if an[5] >= 1 else _rasgar(peca.sprite, an[5], len(r["id"]))
        sprite.colar(quadro, m)
        if r["tipo"] == "grafico":
            _barras_grafico(quadro, m, r, lt, peca, abertura)
        for d_ in cena.get("destaques", ()):
            if d_.get("em") == r["id"]:
                _marcar(quadro, m, peca, d_, lt)
        if r.get("fita"):
            _fitas(quadro, m, r, peca, lt, abertura)
    for c in cena.get("conexoes", ()):
        if c["de"] in anima and c["para"] in anima:
            a, b = _ponto(cam, recortes, c["de"], anima), _ponto(cam, recortes, c["para"], anima)
            _desenhar_conexao(quadro, a, b, saida_rapida((lt - c.get("t", 0)) / max(0.05, c.get("dur", 0.5))), c.get("cor", VERMELHO))
    for k in cena.get("carimbos", ()):
        t = lt - k.get("t", 0)
        if t < 0 and not (abertura and k.get("t", 0) <= 0):
            continue
        esc = 1.0 if abertura and k.get("t", 0) <= 0 else 1 + 1.3 * (1 - saida_rapida(t / 0.14))
        alfa = 1.0 if t > 0.1 or abertura else clamp(t / 0.1)
        _carimbo(k["texto"], k.get("cor", VERMELHO), len(k["texto"])).colar(quadro, compor(cam.matriz(1.0), mover(k.get("x", 540), k.get("y", 960)), girar(k.get("rot", -10)), escalar(esc)), alfa=alfa)
    for n in cena.get("anotacoes", ()):
        t = lt - n.get("t", 0)
        if t < 0:
            continue
        _anotar(quadro, cam, n, t)
    for t_ in cena.get("textos", ()):
        if "ate" in t_ and lt > t_["ate"]:
            continue
        an = _pouso(t_.get("entrada", "pousa"), lt, t_.get("t", 0), abertura, 1)
        if an is None:
            continue
        p = peca_de({"tipo": "tira", "texto": t_["texto"], "tam": t_.get("tam", 72), "cor": t_.get("cor", PRETO), "id": "tx"})
        m = compor(cam.matriz(1.08), mover(t_.get("x", 540) + an[0], t_.get("y", 400) + an[1]), girar(t_.get("rot", -1.5) + an[3]), escalar(an[2]))
        p.sombra.colar(quadro, compor(mover(6, 8), m), filtro=Image.BILINEAR)
        p.sprite.colar(quadro, m)
    return quadro


def _barras_grafico(quadro, m, r, lt, peca, abertura):
    barras = r.get("barras", [])
    if not barras:
        return
    maior = max(b["valor"] for b in barras) or 1
    alt_area = peca.alt * 0.56
    base = peca.alt / 2 - 62
    passo = (peca.larg - 110) / len(barras)
    x0 = -peca.larg / 2 + 55 + passo / 2
    for k, b in enumerate(barras):
        f = 1.0 if abertura and r.get("t", 0) <= 0 else saida_rapida((lt - r.get("t", 0) - 0.3 - 0.16 * k) / 0.6)
        if f <= 0:
            continue
        cor = [VERMELHO, PRETO, AMARELO][k % 3]
        h_ = max(1.0, alt_area * b["valor"] / maior * f)
        _barra_papel(cor).colar(quadro, compor(m, mover(x0 + k * passo, base), escalar(passo * 0.6 / 100, h_ / 100)))
        if f > 0.6:
            texto_sprite(str(b.get("texto", b["valor"])), "maquina", 40, PRETO).colar(quadro, compor(m, mover(x0 + k * passo, base - h_ - 28)))
        if b.get("rotulo"):
            texto_sprite(str(b["rotulo"]), "maquina", 28, GRAFITE).colar(quadro, compor(m, mover(x0 + k * passo, base + 28)))


@lru_cache(maxsize=None)
def _barra_papel(cor):
    im = _texturizar(Image.new("RGB", (100, 100), cor), 5, 8).convert("RGBA")
    return Sprite(im, 50, 100, 1.0)


def _marcar(quadro, m, peca, d_, lt):
    """O marca-texto percorre a linha da esquerda para a direita, por cima do papel e na rotação dele."""
    x = saida_rapida((lt - d_.get("t", 0)) / max(0.05, d_.get("dur", 0.5)))
    i = d_.get("linha", 0)
    if x <= 0 or i >= len(peca.linhas):
        return
    x0, y0, x1, y1 = peca.linhas[i]
    im = _marca_texto(x1 - x0 + 24, y1 - y0 + 14, i + 3)
    corte = im.crop((0, 0, max(1, int(im.width * x)), im.height))
    s = Sprite(corte, 0, 0, peca.sprite.dens)
    s.colar(quadro, compor(m, mover((x0 - 12 - peca.sprite.ox) / peca.sprite.dens, (y0 - 7 - peca.sprite.oy) / peca.sprite.dens)))


def _fitas(quadro, m, r, peca, lt, abertura):
    """A fita corre pela ponta do papel depois que ele pousa."""
    t0 = r.get("t", 0) + 0.3
    x = 1.0 if abertura and r.get("t", 0) <= 0 else saida_rapida((lt - t0) / 0.22)
    if x <= 0:
        return
    w_, h_ = peca.larg / 2, peca.alt / 2
    for sx, sy, giro in ((-1, -1, -36), (1, -1, 36)):
        s = _fita(190, int(sx + 5))
        corte = s.im.crop((0, 0, max(1, int(s.im.width * x)), s.im.height))
        pos = compor(m, mover(sx * (w_ - 34) - (84 if sx > 0 else 0) * math.cos(math.radians(giro)), sy * (h_ - 6)), girar(giro if sx < 0 else giro))
        Sprite(corte, 0, s.oy, s.dens).colar(quadro, pos)


def _anotar(quadro, cam, n, t):
    """Anotação à mão: a letra aparece da esquerda para a direita e a seta vem depois."""
    s = _anotacao_sprite(n["texto"], n.get("cor", VERMELHO))
    x = saida_rapida(t / 0.5)
    corte = s.im.crop((0, 0, max(1, int(s.im.width * x)), s.im.height))
    m = compor(cam.matriz(1.0), mover(n.get("x", 540), n.get("y", 960)), girar(n.get("rot", -3)))
    Sprite(corte, s.ox, s.oy, s.dens).colar(quadro, m)
    if n.get("seta_para") and t > 0.3:
        a = aplicar(m, 0, -44)
        b = aplicar(cam.matriz(1.0), *n["seta_para"])
        f = saida_rapida((t - 0.3) / 0.3)
        fim = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        _desenhar_seta(quadro, a, fim, n.get("cor", VERMELHO), f >= 0.98)


def _desenhar_seta(quadro, a, b, cor, ponta):
    x0, y0 = max(0, int(min(a[0], b[0])) - 50), max(0, int(min(a[1], b[1])) - 50)
    x1, y1 = min(W, int(max(a[0], b[0])) + 50), min(H, int(max(a[1], b[1])) + 50)
    if x1 <= x0 or y1 <= y0:
        return
    g = 2
    im = Image.new("RGBA", ((x1 - x0) * g, (y1 - y0) * g), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p0, p1 = ((a[0] - x0) * g, (a[1] - y0) * g), ((b[0] - x0) * g, (b[1] - y0) * g)
    pts = irregular([(p0[0] + (p1[0] - p0[0]) * k / 14, p0[1] + (p1[1] - p0[1]) * k / 14) for k in range(15)], 8, 3 * g)
    d.line(pts, fill=cor, width=7 * g, joint="curve")
    if ponta:
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for da in (2.55, -2.55):
            d.line([p1, (p1[0] + 40 * g * math.cos(ang + da), p1[1] + 40 * g * math.sin(ang + da))], fill=cor, width=7 * g)
    quadro.alpha_composite(im.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))


# ---------- transições: não dependem da cena vizinha, então reordenar no editor não quebra a emenda ----------
def _cobrir(quadro, tipo, x, saindo):
    """`x` vai de 0 a 1: em 1 a folha cobre a tela inteira."""
    if x <= 0:
        return quadro
    folha = _folha_transicao(tipo)
    saida = quadro.copy()
    e = suave(x)
    if tipo == "virada":
        # A folha gira na dobra da esquerda: chega estreita e escura, e se abre até cobrir.
        lx = max(0.02, e)
        ombra = Image.new("RGBA", (W, H), (0, 0, 0, int(120 * e)))
        saida.alpha_composite(ombra)
        m = compor(mover(0, H / 2), (lx, 0.0, 0.0, -0.12 * (1 - e) * (1 if saindo else -1), 1.0, 0.0), mover(W / 2 + 110 - 110, 0))
        folha.colar(saida, m, filtro=Image.BILINEAR)
    elif tipo == "recorte":
        folha.colar(saida, compor(mover(W / 2, H / 2 + (1 - e) * (H + 280)), girar((1 - e) * -7)), filtro=Image.BILINEAR)
    else:  # sobrepoe
        folha.colar(saida, compor(mover(W / 2 + (1 - e) * (W + 260) * (1 if saindo else -1), H / 2), girar((1 - e) * 5)), filtro=Image.BILINEAR)
    return saida


def quadro(cena, lt, dur, ctx):
    cenas, i = ctx["cenas"], ctx["i"]
    im = compor_cena(cena, lt, dur, abertura=i == 0)
    t = cena.get("transicao") or {}
    saida = t.get("saida", "corte")
    if saida == "loop":
        janela = dur - DUR_LOOP
        if lt > janela:
            primeiro = compor_cena(cenas[0], 0.0, 99.0, abertura=True)
            return fechar_loop(im, primeiro, (lt - janela) / max(DUR_LOOP - ctx.get("meio", 1 / 15), 0.01))
    elif saida != "corte" and lt > dur - DUR_TRANS:
        im = _cobrir(im, saida, (lt - (dur - DUR_TRANS)) / DUR_TRANS, True)
    entrada_ = t.get("entrada", "corte")
    if entrada_ != "corte" and i != 0 and lt < DUR_TRANS:
        im = _cobrir(im, entrada_, 1 - lt / DUR_TRANS, False)
    return im


# ---------- validação ----------
def _erro(onde, texto):
    raise ValueError(f"{onde}: {texto}")


def _na_lista(onde, campo, valor, lista):
    if valor not in lista:
        _erro(onde, f"{campo} '{valor}' não existe. Use: {', '.join(lista)}")


def validar(c, onde):
    if not isinstance(c.get("acao"), str) or not c["acao"].strip():
        _erro(onde, "falta a 'acao': o que a câmera revela nesta cena, em uma frase")
    _na_lista(onde, "superficie", c.get("superficie"), tuple(SUPERFICIES))
    recortes = c.get("recortes")
    if not isinstance(recortes, list) or not recortes:
        _erro(onde, "'recortes' é obrigatório: uma cena de colagem precisa de pelo menos um documento ou evidência")
    ids = set()
    for r in recortes:
        if not isinstance(r.get("id"), str) or not r["id"]:
            _erro(onde, "todo recorte precisa de 'id'")
        if r["id"] in ids:
            _erro(onde, f"recorte '{r['id']}' repetido")
        ids.add(r["id"])
        _na_lista(onde, "tipo de recorte", r.get("tipo"), TIPOS)
        _na_lista(onde, "entrada", r.get("entrada", "pousa"), ENTRADAS)
        if r.get("figura"):
            _na_lista(onde, "figura", r["figura"], FIGURAS)
        if r.get("arquivo"):
            arq = Path(str(r["arquivo"]))
            if arq.is_absolute() or ".." in arq.parts:
                _erro(onde, f"recorte '{r['id']}': 'arquivo' é um caminho dentro da pasta do projeto")
            if _PASTA["caminho"] and not (_PASTA["caminho"] / arq).is_file():
                _erro(onde, f"recorte '{r['id']}': não achei o arquivo {arq} na pasta do projeto")
        if r["tipo"] == "grafico" and not r.get("barras"):
            _erro(onde, f"recorte '{r['id']}': gráfico precisa de 'barras'")
        if r["tipo"] == "linha_tempo" and not r.get("eventos"):
            _erro(onde, f"recorte '{r['id']}': linha do tempo precisa de 'eventos'")
    for x in c.get("conexoes", []):
        for ponta in ("de", "para"):
            if x.get(ponta) not in ids:
                _erro(onde, f"conexão: '{x.get(ponta)}' não é um recorte desta cena")
    for d_ in c.get("destaques", []):
        if d_.get("em") not in ids:
            _erro(onde, f"destaque: '{d_.get('em')}' não é um recorte desta cena")
    for t in c.get("textos", []):
        if not isinstance(t.get("texto"), str) or not t["texto"].strip() or len(t["texto"]) > MAX_TEXTO:
            _erro(onde, f"texto inválido ou longo demais (máx. {MAX_TEXTO} caracteres): {t.get('texto')!r}")
        if not SEGURO_TOPO <= t.get("y", 400) <= SEGURO_BASE:
            _erro(onde, f"texto '{t['texto']}' fora da área segura (y entre {SEGURO_TOPO} e {SEGURO_BASE})")
        if fonte("impacto", t.get("tam", 72)).getlength(t["texto"]) > W - 110:
            _erro(onde, f"texto '{t['texto']}' não cabe na largura com tam {t.get('tam', 72)}: quebre em dois textos ou reduza")
    for k in c.get("carimbos", []):
        if not isinstance(k.get("texto"), str) or not k["texto"].strip() or len(k["texto"]) > 18:
            _erro(onde, "carimbo: 'texto' com até 18 caracteres")
    for n in c.get("anotacoes", []):
        if not isinstance(n.get("texto"), str) or not n["texto"].strip() or len(n["texto"]) > MAX_TEXTO:
            _erro(onde, f"anotação inválida ou longa demais (máx. {MAX_TEXTO} caracteres): {n.get('texto')!r}")
    for ch in (c.get("camera") or {}).get("chaves", []):
        if not (-400 <= ch.get("x", 540) <= 1500 and -300 <= ch.get("y", 960) <= 2200 and 1.0 <= ch.get("zoom", 1.0) <= 2.6):
            _erro(onde, "câmera: x entre -400 e 1500, y entre -300 e 2200, zoom entre 1 e 2,6")
    tr = c.get("transicao") or {}
    _na_lista(onde, "transição de entrada", tr.get("entrada", "corte"), TRANS_ENTRADA)
    _na_lista(onde, "transição de saída", tr.get("saida", "corte"), TRANS_SAIDA)


def textos(c):
    """O que aparece escrito na tela, para a conformidade e o Vini."""
    saida = list(c.get("rotulos", []))
    for r in c.get("recortes", []):
        for k in ("titulo", "manchete", "sub", "nome", "legenda", "data", "texto"):
            if r.get(k):
                saida.append(str(r[k]))
        saida += [str(x) for x in r.get("linhas", [])]
        for cp in r.get("campos", []):
            saida += [str(cp.get("rotulo", "")), str(cp.get("valor", ""))]
        for ev in r.get("eventos", []):
            saida += [str(ev.get("data", "")), str(ev.get("texto", ""))]
        for b in r.get("barras", []):
            saida += [str(b.get("rotulo", "")), str(b.get("texto", b.get("valor", "")))]
        saida += [str(p.get("rotulo", "")) for p in r.get("pinos", [])]
    saida += [k["texto"] for k in c.get("carimbos", [])]
    saida += [n["texto"] for n in c.get("anotacoes", [])]
    saida += [t["texto"] for t in c.get("textos", [])]
    return [x for x in saida if x]

