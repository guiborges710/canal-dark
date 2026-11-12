import random
from PIL import ImageDraw
from media.sketch_lib import *

# Pair programming (LinkedIn, v5): duas pessoas, o mesmo problema, papéis que alternam.
# Convenção: pessoa A = traço azul (esquerda), pessoa B = traço laranja (direita).
XA, XB = 250, 830
VERDE_OK = (60, 150, 90)


def tela(d, cx, cy, w, h, seed, frac=1.0):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
    traco(d, c, seed, frac, w=7, amp=2, fechado=True)
    traco(d, [(cx - 70, y1 + 40), (cx + 70, y1 + 40)], seed + 1, frac, w=7, amp=2)
    traco(d, [(cx, y1), (cx, y1 + 40)], seed + 2, frac, w=7, amp=2)


def codigo(d, cx, cy, w, h, lt, t0, cores, seed, passo=0.35):
    """Linhas de código que aparecem em sequência dentro da tela; `cores` = cor de cada linha."""
    rng = random.Random(seed)
    n = len(cores)
    x0 = cx - w / 2 + 40
    for i, cor in enumerate(cores):
        y = cy - h / 2 + 55 + i * (h - 90) / max(1, n - 1 if n > 1 else 1)
        recuo = 50 * (i % 3 == 1)
        comp = rng.uniform(0.45, 0.85) * (w - 80 - recuo)
        traco(d, [(x0 + recuo, y), (x0 + recuo + comp, y)], seed + i, entra(lt, t0 + i * passo, 0.3), w=9, amp=1.5, col=cor)


def teclado(d, cx, cy, seed, frac=1.0):
    c = [(cx - 85, cy - 38), (cx + 85, cy - 38), (cx + 85, cy + 38), (cx - 85, cy + 38)]
    if frac >= 0.99:
        preencher(d, c, GELO)
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if frac >= 0.99:
        for r in range(2):
            for k in range(5):
                circ_pts = circ(cx - 60 + k * 30, cy - 12 + r * 28, 5, 8)
                preencher(d, circ_pts, INK)


def papel_etiqueta(d, x, y, s, cor, frac=1.0):
    if frac > 0:
        texto(d, x, y, s, 52, cor)


def cena_0(lt, dur):
    """Gancho: duas pessoas só olhando para a tela, riscadas com um X vermelho."""
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 320, "pair programming", 68)
    tela(d, 540, 800, 560, 380, seed=3)
    codigo(d, 540, 800, 560, 380, lt, 0.0, [FERRO] * 5, 4, passo=0.12)
    pessoa(d, XA, 1200, s=1.5 * mola(lt, 0.0), seed=10, cor=AZUL)
    pessoa(d, XB, 1200, s=1.5 * mola(lt, 0.15), seed=20, cor=LARANJA)
    if lt > 1.4:
        cruz(d, 540, 800, s=3.6 * mola(lt, 1.4, 0.35), seed=30)
        texto(d, 540, 1420, "não é isso", 60, VERMELHO)
    return im


def cena_1(lt, dur):
    """Duas pessoas, o mesmo problema, perguntas indo e voltando."""
    im = papel()
    d = ImageDraw.Draw(im)
    caixa = [(390, 910), (690, 910), (690, 1090), (390, 1090)]
    f = entra(lt, 0.0, 0.4)
    if f >= 0.99:
        preencher(d, caixa, GELO)
    traco(d, caixa, 5, f, w=7, amp=2, fechado=True)
    if lt > 0.3:
        texto(d, 540, 975, "o mesmo", 46)
        texto(d, 540, 1030, "problema", 46)
    pessoa(d, XA, 1000, s=1.4 * mola(lt, 0.1), seed=11, cor=AZUL)
    pessoa(d, XB, 1000, s=1.4 * mola(lt, 0.25), seed=21, cor=LARANJA)
    balao(d, 330, 560, 440, 190, ["e se a gente", "tentar isso?"], seed=31, frac=entra(lt, 0.9, 0.4), tam=50, cauda=None)
    balao(d, 760, 790, 400, 150, ["por que assim?"], seed=41, frac=entra(lt, 2.2, 0.4), tam=50, cauda=None)
    if lt > 3.2:
        k = pulso(lt, vel=4, amp=0.12)
        texto(d, 470, 820, "?", int(130 * k), LARANJA)
    return im


def _papeis(d, lt, p, base_y=1050):
    """Teclado e lupa trocam de dono; p vai de 0 (A escreve) a 1 (B escreve)."""
    import math
    arco = math.sin(math.pi * p)
    xt = XA + (XB - XA) * p
    xl = XB + (XA - XB) * p
    teclado(d, xt, 1330 - 90 * arco, seed=60)
    lupa(d, xl, 1310 + 90 * arco, s=0.8, seed=61)
    escreve_a = p < 0.5
    papel_etiqueta(d, XA, 1445, "escreve" if escreve_a else "revisa e sugere", AZUL)
    papel_etiqueta(d, XB, 1445, "revisa e sugere" if escreve_a else "escreve", LARANJA)


def cena_2(lt, dur):
    """A escreve, B revisa e sugere."""
    im = papel()
    d = ImageDraw.Draw(im)
    tela(d, 540, 640, 520, 340, seed=6, frac=entra(lt, 0.0, 0.4))
    codigo(d, 540, 640, 520, 340, lt, 0.3, [AZUL] * 5, 7)
    pessoa(d, XA, 1050, s=1.5 * mola(lt, 0.0), seed=12, cor=AZUL)
    pessoa(d, XB, 1050, s=1.5 * mola(lt, 0.15), seed=22, cor=LARANJA)
    if lt > 0.5:
        _papeis(d, lt, 0.0)
    if lt > 2.0:
        f = entra(lt, 2.0, 0.35)
        traco(d, [(340, 705), (340 + 300 * f, 705)], 8, 1.0, w=7, amp=1.5, col=LARANJA)
        texto(d, 700, 560, "?", int(90 * pulso(lt, 4, 0.12)), LARANJA)
    return im


def cena_3(lt, dur):
    """Troca de papéis: o teclado vai para B e a lupa vai para A."""
    import math
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 320, "troca de papel", 62)
    tela(d, 540, 640, 520, 340, seed=6)
    p = entra(lt, 0.9, 1.0)
    codigo(d, 540, 640, 520, 340, 99, 0.0, [AZUL] * 3 + [LARANJA] * 2, 7)
    pessoa(d, XA, 1050, s=1.5, seed=12, cor=AZUL)
    pessoa(d, XB, 1050, s=1.5, seed=22, cor=LARANJA)
    _papeis(d, lt, p)
    seta(d, 400, 930, 700, 930, seed=70, frac=entra(lt, 0.7, 0.4), cor=INK, w=7)
    seta(d, 700, 1000, 400, 1000, seed=75, frac=entra(lt, 0.9, 0.4), cor=INK, w=7)
    return im


def cena_4(lt, dur):
    """A solução cresce linha a linha, uma cor de cada pessoa."""
    im = papel()
    d = ImageDraw.Draw(im)
    tela(d, 540, 700, 660, 500, seed=8, frac=entra(lt, 0.0, 0.4))
    cores = [AZUL, LARANJA, AZUL, LARANJA, AZUL, LARANJA]
    codigo(d, 540, 700, 660, 500, lt, 0.3, cores, 9, passo=0.4)
    pessoa(d, 230, 1230, s=1.2 * mola(lt, 0.0), seed=13, cor=AZUL)
    pessoa(d, 850, 1230, s=1.2 * mola(lt, 0.15), seed=23, cor=LARANJA)
    if lt > 0.5:
        texto(d, 540, 1090, "solução em conjunto", 54)
    if lt > 2.6:
        check(d, 540, 1230, s=2.4 * mola(lt, 2.6), seed=80, cor=VERDE_OK)
        im = brilho(im, 540, 1230, 150, VERDE_OK, k=0.35)
    return im


def cena_5(lt, dur):
    """Três ganhos: contexto, conhecimento e decisão."""
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 330, "pair programming é:", 62)
    tempos = [dur * 0.18, dur * 0.42, dur * 0.68]
    # contexto: dois círculos que se sobrepõem
    t = tempos[0]
    traco(d, circ(240, 640, 62 * mola(lt, t), 40), 90, entra(lt, t, 0.4), w=7, col=AZUL, fechado=True)
    traco(d, circ(320, 640, 62 * mola(lt, t + 0.1), 40), 91, entra(lt, t + 0.1, 0.4), w=7, col=LARANJA, fechado=True)
    if lt > t:
        texto(d, 450, 640, "contexto", 76, ancora="lm")
    # conhecimento: seta de ida e volta entre duas cabeças
    t = tempos[1]
    traco(d, circ(210, 960, 40 * mola(lt, t), 32), 92, entra(lt, t, 0.4), w=7, col=AZUL, fechado=True)
    traco(d, circ(350, 960, 40 * mola(lt, t + 0.1), 32), 93, entra(lt, t + 0.1, 0.4), w=7, col=LARANJA, fechado=True)
    seta(d, 255, 945, 305, 945, seed=94, frac=entra(lt, t + 0.2, 0.3), cor=AZUL, w=6)
    seta(d, 305, 985, 255, 985, seed=96, frac=entra(lt, t + 0.3, 0.3), cor=LARANJA, w=6)
    if lt > t:
        texto(d, 450, 960, "conhecimento", 76, ancora="lm")
    # decisão: check dentro de um círculo
    t = tempos[2]
    traco(d, circ(280, 1280, 70 * mola(lt, t), 40), 97, entra(lt, t, 0.4), w=7, col=VERDE_OK, fechado=True)
    check(d, 280, 1280, s=1.0 * mola(lt, t + 0.15), seed=98, cor=VERDE_OK)
    if lt > t:
        texto(d, 450, 1280, "decisão", 76, ancora="lm")
    return im


def cena_6(lt, dur):
    """Pergunta de volta ao público."""
    im = papel()
    d = ImageDraw.Draw(im)
    balao(d, 540, 520, 820, 200, ["já fez", "pair programming?"], seed=50, frac=entra(lt, 0.2, 0.45), tam=62, cauda=None)
    balao(d, 540, 800, 760, 200, ["o que você", "aprendeu?"], seed=55, frac=entra(lt, dur * 0.5, 0.45), tam=62, cauda=None)
    pessoa(d, 540, 1260, s=1.5 * mola(lt, 0.0), seed=14, cor=INK)
    if lt > 0.8:
        texto(d, 540, 1000, "?", int(130 * pulso(lt, 4, 0.1)), LARANJA)
    return im
