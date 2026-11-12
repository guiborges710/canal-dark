import math
from PIL import ImageDraw
from media.sketch_lib import *


def _tit(d, y, s, tam=64, lt=0.0, t0=0.0):
    k = mola(lt, t0, 0.4)
    if k > 0:
        texto(d, 540, y, s, int(tam * (0.85 + 0.15 * k)))


def _idades(d, y_pe, lt, t0, seed, escalas, xs, cor=INK):
    for i, (e, x) in enumerate(zip(escalas, xs)):
        m = mola(lt, t0 + i * 0.25)
        if m > 0:
            pessoa(d, x, y_pe - 125 * e * m + 4 * math.sin(lt * 4 + i), e * m, seed + 10 * i, 1.0, cor)


def cena_0(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    nivel = max(0.0, 0.85 - 0.22 * lt)
    p = pulso(lt, 4, 0.05)
    copo(d, 360, 880, 2.1, 3, 1.0, nivel)
    cruz(d, 360, 880, 2.6, 8, entra(lt, 0.1, 0.5))
    seta(d, 520, 880, 660, 880, 20, entra(lt, 0.3, 0.5))
    pessoa(d, 800, 900, 1.7 * p, 30)
    texto(d, 800, 1210, "?", int(150 * mola(lt, 0.8)) + 1, VERMELHO)
    _tit(d, 270, "Gen Z parou de beber?", 66, lt, 0.0)
    return im


def cena_1(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 290, "Adultos nos EUA que bebem", 56, lt, 0.0)
    itens = [{"rotulo": "2023", "valor": 62, "texto": "62%", "cor": AZUL},
             {"rotulo": "2024", "valor": 58, "texto": "58%", "cor": GELO},
             {"rotulo": "2025", "valor": 54, "texto": "54%", "cor": LARANJA}]
    barras(d, 540, 1380, itens, larg=210, alt_max=900, escala_max=70, lt=lt, t0=0.3, seed=5, passo=290)
    f = entra(lt, 2.6, 0.6)
    if f > 0:
        h = 900 * 54 / 70
        traco(d, circ(830, 1380 - h - 40, 100 * pulso(lt, 4, 0.04), 40), 77, f, w=7, col=VERMELHO)
    return im


def cena_2(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 290, "Adultos jovens: 59% → 50%", 54, lt, 0.0)
    itens = [{"rotulo": "antes", "valor": 59, "texto": "59%", "cor": AZUL},
             {"rotulo": "depois", "valor": 50, "texto": "50%", "cor": LARANJA}]
    barras(d, 540, 1380, itens, larg=260, alt_max=900, escala_max=70, lt=lt, t0=0.3, seed=9, passo=420)
    f = entra(lt, 1.4, 0.6)
    seta(d, 470, 620 + 20 * math.sin(lt * 5), 620 + 0, 0, 0) if False else None
    if f > 0:
        seta(d, 450, 640, 450 + 100 * f, 640 + 150 * f, 40, f, VERMELHO, 10)
    return im


def cena_3(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 270, "53%: moderação faz mal", 60, lt, 0.0)
    f = entra(lt, 0.3, 0.9)
    x0, x1, y0, y1 = 200, 880, 400, 520
    traco(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 3, 1.0, fechado=True)
    xf = x0 + (x1 - x0) * 0.53 * f
    if f > 0.02:
        preencher(d, [(x0 + 4, y0 + 4), (xf, y0 + 4), (xf, y1 - 4), (x0 + 4, y1 - 4)], LARANJA)
    texto(d, 380, 680, "53%", int(190 * (0.9 + 0.1 * mola(lt, 0.5))), INK)
    m = mola(lt, 0.9)
    copo(d, 290, 1130, 1.6, 6, 1.0, 0.5)
    if m > 0:
        s = 1.4 * m * pulso(lt, 5, 0.06)
        tri = [(430, 1010 - 90 * s), (430 + 80 * s, 1010 + 50 * s), (430 - 80 * s, 1010 + 50 * s)]
        preencher(d, tri, SOL_AMARELO); traco(d, tri, 11, 1.0, fechado=True, col=VERMELHO)
        texto(d, 430, 1010 + 10 * s, "!", int(90 * s), VERMELHO)
    pessoa(d, 770, 1180, 1.7, 15)
    if lt > 2.3:
        k = mola(lt, 2.3)
        g = tremer(lt)
        im = brilho(im, 770, 780, 110 * k, SOL_AMARELO, 0.7 * g)
        d = ImageDraw.Draw(im)
        traco(d, circ(770, 780, 52 * k, 30), 21, 1.0, w=6)
        traco(d, [(745, 835 * 1.0), (795, 835)], 22, 1.0, w=6)
        traco(d, [(748, 850), (792, 850)], 23, 1.0, w=6)
        for a in range(-60, 61, 30):
            r = math.radians(a - 90)
            traco(d, [(770 + 80 * math.cos(r), 780 + 80 * math.sin(r)), (770 + 115 * math.cos(r), 780 + 115 * math.sin(r))], 30 + a, 1.0, w=5)
    return im


def cena_4(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 270, "Queda em todas as idades", 60, lt, 0.0)
    _idades(d, 760, lt, 0.2, 100, [0.7, 1.0, 1.3, 1.0, 0.8], [260, 420, 590, 750, 900])
    f = entra(lt, 1.2, 0.6)
    if f > 0:
        seta(d, 540, 830, 540, 830 + 170 * f, 50, f, VERMELHO, 12)
    m = mola(lt, 2.6)
    if m > 0:
        garrafa(d, 270, 1280, 1.3 * m, 60, 1.0)
        traco(d, [(500, 1255), (600, 1255)], 61, 1.0, w=9)
        traco(d, [(500, 1305), (600, 1305)], 62, 1.0, w=9)
        copo(d, 810, 1290, 1.5 * m, 63, 1.0, 0.75)
    return im


def cena_5(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 270, "Brasil: sem número único", 58, lt, 0.0)
    rel = [(-50, -330), (120, -300), (300, -220), (350, -80), (250, 60), (180, 200), (60, 330), (-60, 300),
           (-130, 150), (-250, 60), (-330, -60), (-250, -200), (-120, -230)]
    k = mola(lt, 0.1, 0.6)
    pts = [(540 + x * 1.35 * k, 880 + y * 1.35 * k) for x, y in rel]
    if k > 0.05:
        preencher(d, pts, VERDE)
        traco(d, pts, 7, entra(lt, 0.1, 0.8), w=7, fechado=True)
    pos = [(400, 760), (720, 860), (520, 1160)]
    for i, (x, y) in enumerate(pos):
        m = mola(lt, 1.0 + i * 0.9)
        if m > 0:
            lupa(d, x + 14 * math.sin(lt * 2.5 + i * 2), y + 12 * math.cos(lt * 2 + i), 1.3 * m, 80 + i * 5)
    return im


def cena_6(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _tit(d, 270, "Coisa de uma geração?", 64, lt, 0.0)
    p = pulso(lt, 3.5, 0.07)
    m = mola(lt, 0.2)
    if m > 0:
        balao(d, 540, 640, 420 * m * p, 330 * m * p, ["?"], 5, 1.0, tam=int(260 * m * p), cauda="esq")
    _idades(d, 1320, lt, 0.8, 120, [0.8, 1.1, 1.5, 1.1, 0.8], [250, 400, 570, 740, 890])
    return im
