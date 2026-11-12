import math

from PIL import ImageDraw
from media.sketch_lib import *
import media.sketch_lib as _lib

definir_formato("horizontal")
W, H = _lib.W, _lib.H
CX, CY = W // 2, H // 2


def _num(d, lt, x, y, s, tam, t0, cor=INK):
    """Texto que cresce com mola a partir de t0 (só aparece depois de t0)."""
    if lt < t0:
        return
    texto(d, x, y, s, max(20, int(tam * mola(lt, t0, 0.5))), cor)


def _titulo(d, lt, s):
    if lt > 0.2:
        texto(d, CX, 150, s, 60)


def cena_0(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    pessoa(d, 800, 560, s=2.2, seed=1, frac=entra(lt, 0.0, 0.5))
    lupa(d, 1230 + int(6 * math.sin(lt * 2)), 520, s=2.2, seed=20, frac=entra(lt, 0.4, 0.5))
    balao(d, 1480, 240, 620, 170, ["A mais solitária?"], seed=40, frac=entra(lt, 0.9, 0.5), tam=56)
    return im


def cena_1(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    itens = [
        {"rotulo": "Gen Z", "valor": 67, "texto": "67%", "cor": LARANJA},
        {"rotulo": "Millennials", "valor": 65, "texto": "65%", "cor": AZUL},
        {"rotulo": "Gen X", "valor": 60, "texto": "60%", "cor": AZUL},
        {"rotulo": "Boomers", "valor": 44, "texto": "44%", "cor": FERRO},
    ]
    barras(d, CX, 840, itens, larg=220, alt_max=600, escala_max=70, lt=lt, t0=0.3,
           seed=5, passo=330, tam_rotulo=44)
    # círculo em volta do 67% entra na fala do número (6 s)
    cx, cy = 465, 226
    k = pulso(lt, 2.0, 0.03)
    pts = [(cx + 118 * k * math.cos(math.tau * i / 40), cy + 56 * k * math.sin(math.tau * i / 40)) for i in range(40)]
    traco(d, pts, 77, entra(lt, 6.0, 0.5), w=6, amp=2, fechado=True, col=INK)
    return im


def cena_2(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    texto(d, CX, 210, "2 pontos", max(20, int(170 * mola(lt, 0.1, 0.5))))
    itens = [
        {"rotulo": "Gen Z", "valor": 67, "texto": "67%", "cor": LARANJA},
        {"rotulo": "Millennials", "valor": 65, "texto": "65%", "cor": AZUL},
    ]
    barras(d, CX, 880, itens, larg=260, alt_max=480, escala_max=70, lt=lt, t0=0.6,
           seed=9, passo=420, tam_rotulo=44)
    if lt >= 1.0:
        texto(d, CX, 640, "?", int(200 * pulso(lt, 2.0, 0.05)))
    return im


def cena_3(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _titulo(d, lt, "Resposta, não diagnóstico")
    # formulário: quadro, cabeçalho e três linhas com caixas
    traco(d, [(380, 290), (1000, 290), (1000, 800), (380, 800)], 3, entra(lt, 0.2, 0.6), w=6, fechado=True)
    traco(d, [(380, 360), (1000, 360)], 4, entra(lt, 0.6, 0.3), w=5)
    for i, y in enumerate((430, 560, 690)):
        t0 = 1.0 + 0.4 * i
        traco(d, [(430, y - 30), (490, y - 30), (490, y + 30), (430, y + 30)], 10 + i, entra(lt, t0, 0.3), w=5, fechado=True)
        traco(d, [(540, y), (950, y)], 20 + i, entra(lt, t0 + 0.2, 0.4), w=5)
        if i != 1:
            check(d, 460, y, s=0.5, seed=30 + i, frac=entra(lt, t0 + 0.4, 0.3))
    # boneco com balão "Estou só?"
    pessoa(d, 1420, 640, s=1.6, seed=60, frac=entra(lt, 0.8, 0.5))
    balao(d, 1450, 300, 300, 120, ["Estou só?"], seed=70, frac=entra(lt, 1.6, 0.5), tam=46)
    return im


def cena_4(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _titulo(d, lt, "Idade ou geração?")
    # calendário com "20" no centro
    traco(d, [(260, 340), (660, 340), (660, 720), (260, 720)], 10, entra(lt, 0.0, 0.6), w=6, fechado=True)
    if lt > 0.3:
        preencher(d, [(262, 342), (658, 342), (658, 420), (262, 420)], (225, 90, 100))
        traco(d, [(262, 342), (658, 342), (658, 420), (262, 420)], 11, 1.0, w=5, amp=1.5, fechado=True)
    traco(d, [(350, 310), (350, 370)], 12, entra(lt, 0.4, 0.3), w=7)
    traco(d, [(570, 310), (570, 370)], 13, entra(lt, 0.4, 0.3), w=7)
    _num(d, lt, 460, 560, "20", 190, 0.6)
    # setas para casa, pasta de trabalho e bonecos (mudança)
    seta(d, 700, 330, 1200, 300, seed=30, frac=entra(lt, 1.0, 0.5))
    seta(d, 700, 520, 1200, 540, seed=31, frac=entra(lt, 1.5, 0.5))
    seta(d, 700, 690, 1200, 780, seed=32, frac=entra(lt, 2.0, 0.5))
    casa(d, 1400, 300, s=1.2, seed=40, frac=entra(lt, 1.2, 0.5))
    traco(d, [(1290, 500), (1510, 500), (1510, 600), (1290, 600)], 41, entra(lt, 1.7, 0.5), w=6, fechado=True)
    traco(d, [(1355, 500), (1355, 470), (1445, 470), (1445, 500)], 42, entra(lt, 1.8, 0.4), w=5)
    grupo_pessoas(d, 1400, 780, 2, s=1.1, seed=70, frac=entra(lt, 2.4, 0.5), passo=130)
    return im


def cena_5(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _num(d, lt, 520, 380, "7 mil", 180, 0.2)
    if lt > 0.8:
        texto(d, 520, 500, "adultos", int(56 * entra(lt, 0.8, 0.4)) or 20)
    _num(d, lt, 1400, 380, "9 anos", 180, 2.2)
    # linha do tempo com nove marcas
    traco(d, [(200, 700), (1720, 700)], 80, entra(lt, 0.8, 2.0), w=7)
    for k in range(9):
        x = 200 + k * 190
        traco(d, [(x, 670), (x, 730)], 81 + k, entra(lt, 1.0 + 0.2 * k, 0.3), w=5, amp=1.5)
    if lt > 1.0:
        texto(d, 200, 790, "início", 46)
        texto(d, 1720, 790, "fim", 46)
    return im


def cena_6(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _titulo(d, lt, "Passiva ou ativa: solidão")
    celular(d, 500, 520, s=1.6, seed=10, frac=entra(lt, 0.0, 0.5), tela=GELO)
    # caminho passivo: seta para o olho
    seta(d, 660, 430, 880, 330, seed=21, frac=entra(lt, 0.8, 0.5))
    traco(d, circ(1000, 300, 100, 40), 22, entra(lt, 1.2, 0.5), w=6, fechado=True)
    if lt >= 1.7:
        preencher(d, circ(1000, 300, 22, 20), INK)
    seta(d, 1100, 320, 1400, 440, seed=23, frac=entra(lt, 1.8, 0.5))
    # caminho ativo: seta para o balão de conversa
    seta(d, 660, 630, 880, 720, seed=24, frac=entra(lt, 2.4, 0.5))
    balao(d, 1000, 780, 220, 130, ["..."], seed=25, frac=entra(lt, 3.0, 0.5), tam=60)
    seta(d, 1120, 760, 1420, 680, seed=26, frac=entra(lt, 3.4, 0.5))
    # boneco de destino, com traço mais grosso (pessoa desenhada com pequenos deslocamentos)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        pessoa(d, 1540 + dx, 600 + dy, s=1.5, seed=60, frac=entra(lt, 0.4, 0.5))
    # nuvem de chuva sobre o boneco
    if lt > 4.5:
        f = entra(lt, 4.5, 0.6)
        traco(d, circ(1490, 262, 42, 30), 90, f, w=7, amp=1.5, fechado=True)
        traco(d, circ(1545, 240, 55, 36), 91, f, w=7, amp=1.5, fechado=True)
        traco(d, circ(1600, 265, 40, 30), 92, f, w=7, amp=1.5, fechado=True)
        for i, x in enumerate((1490, 1540, 1590)):
            traco(d, [(x, 320), (x - 8, 355)], 95 + i, entra(lt, 5.0 + 0.2 * i, 0.3), w=5, amp=1.5)
    return im


def cena_7(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _titulo(d, lt, "Vai e volta")
    pessoa(d, 480, 560, s=2.0, seed=1, frac=entra(lt, 0.0, 0.5))
    celular(d, 1440, 560, s=2.0, seed=10, frac=entra(lt, 0.2, 0.5), tela=GELO)
    seta(d, 640, 470, 1200, 470, seed=30, frac=entra(lt, 1.0, 0.6), w=8)
    seta(d, 1200, 610, 640, 610, seed=31, frac=entra(lt, 1.8, 0.6), w=8)
    if lt >= 3.0:
        k = 0.6 * entra(lt, 3.0, 1.0) * pulso(lt, 2.0, 0.1)
        im = brilho(im, 1440, 560, 380, (150, 190, 255), k=k)
    return im


def cena_8(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    _titulo(d, lt, "O que ela não perguntou?")
    # lupa sobre a palavra "manchete"
    lupa(d, 520, 380, s=2.6, seed=10, frac=entra(lt, 0.0, 0.6))
    if lt >= 0.6:
        texto(d, 520, 380, "manchete", 56)
    # ponto de interrogação grande
    if lt >= 1.0:
        texto(d, 1400, 400, "?", int(460 * pulso(lt, 2.0, 0.04)))
    # três ícones: régua (medido), questionário (perguntado), duas pessoas (comparado)
    x = 420
    traco(d, [(x - 150, 755), (x + 150, 755), (x + 150, 845), (x - 150, 845)], 40, entra(lt, 1.2, 0.5), w=6, fechado=True)
    for k in range(7):
        tx = x - 150 + k * 50
        traco(d, [(tx, 845), (tx, 810 if k % 2 else 825)], 41 + k, entra(lt, 1.4, 0.4), w=4, amp=1)
    x = 800
    traco(d, [(x - 110, 690), (x + 110, 690), (x + 110, 910), (x - 110, 910)], 50, entra(lt, 1.8, 0.5), w=6, fechado=True)
    for i, y in enumerate((745, 800, 855)):
        traco(d, [(x - 70, y), (x + 60, y)], 51 + i, entra(lt, 2.0 + 0.2 * i, 0.3), w=5)
    check(d, x + 60, 745, s=0.35, seed=55, frac=entra(lt, 2.4, 0.3))
    grupo_pessoas(d, 1180, 800, 2, s=1.0, seed=60, frac=entra(lt, 2.6, 0.5), passo=170)
    return im
