"""Cenas sketch: swiftui-identidade-lista (o check que pulou de linha). Desenho original, Olise."""
import math

from PIL import ImageDraw

from media.sketch_lib import *

BRANCO = (255, 255, 255)
VERDE_OK = (60, 150, 90)


# ---------- peças próprias deste vídeo ----------
def ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def moldura(d, pts, seed, frac=1.0, fundo=None, w=6):
    if fundo and frac >= 0.99:
        preencher(d, pts, fundo)
    traco(d, pts, seed, frac, w=w, amp=2, fechado=True)


def caixa_sel(d, cx, cy, seed, marcada=0.0, lado=70):
    """Caixa de seleção; `marcada` 0..1 desenha o check aos poucos."""
    h = lado / 2
    moldura(d, ret(cx - h, cy - h, cx + h, cy + h), seed, 1.0, BRANCO, w=5)
    if marcada > 0:
        check(d, cx + 4, cy - 4, 0.75, seed + 50, marcada)


def linha_lista(d, x0, x1, y, rotulo, seed, marcada=0.0, risco=0.0, tam=52, cor_box=None):
    moldura(d, ret(x0, y - 62, x1, y + 62), seed, 1.0, cor_box or BRANCO, w=5)
    caixa_sel(d, x0 + 70, y, seed + 3, marcada)
    texto(d, x0 + 135, y, rotulo, tam, ancora="lm")
    if risco > 0:
        traco(d, [(x0 + 20, y), (x0 + 20 + (x1 - x0 - 40) * risco, y)], seed + 9, 1.0, w=9, amp=2, col=VERMELHO)


def notebook(d, cx, cy, larg, alt, linhas, seed, frac=1.0, tam=40, mostrar=None, lt=0.0):
    """Notebook aberto: tela (cx, cy = centro da tela) com código escrito; `mostrar` = nº de caracteres já digitados."""
    x0, x1, y0, y1 = cx - larg / 2, cx + larg / 2, cy - alt / 2, cy + alt / 2
    moldura(d, ret(x0, y0, x1, y1), seed, frac, (40, 44, 56))
    base = [(x0 - 40, y1 + 50), (x1 + 40, y1 + 50), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, base, (215, 215, 220))
    traco(d, base, seed + 1, frac, w=6, amp=2, fechado=True)
    if frac < 0.99:
        return
    resto = 10 ** 6 if mostrar is None else mostrar
    y = y0 + 30 + tam * 0.6
    ult = (x0 + 30, y)
    for ln in linhas:
        if resto <= 0:
            break
        parte = ln[:resto]
        resto -= len(ln)
        texto(d, x0 + 30, y, parte, tam, (200, 235, 210), "lm")
        ult = (x0 + 30 + fonte(tam).getlength(parte), y)
        y += tam * 1.35
    if math.sin(lt * 8) > 0:  # cursor piscando
        d.rectangle([ult[0] + 6, ult[1] - tam * 0.45, ult[0] + 20, ult[1] + tam * 0.45], fill=(200, 235, 210))


def titulo(d, y, s, tam, lt, t0=0.0, cor=INK, caixa=None, seed=900):
    k = mola(lt, t0)
    if k <= 0:
        return
    t = max(10, int(tam * k))
    if caixa:
        larg = fonte(t).getlength(s) + 70
        moldura(d, ret(540 - larg / 2, y - t * 0.75, 540 + larg / 2, y + t * 0.75), seed, 1.0, caixa)
    texto(d, 540, y, s, t, cor)


def etiqueta(d, x, y, s, seed, tam=34):
    """Etiqueta de bagagem presa ao item por um fio (x, y = centro da etiqueta)."""
    larg = fonte(tam).getlength(s) + 50
    pts = [(x - larg / 2 + 25, y - 34), (x + larg / 2, y - 34), (x + larg / 2, y + 34), (x - larg / 2 + 25, y + 34), (x - larg / 2, y)]
    preencher(d, pts, SOL_AMARELO)
    traco(d, pts, seed, 1.0, w=5, amp=1.5, fechado=True)
    d.ellipse([x - larg / 2 + 14, y - 7, x - larg / 2 + 28, y + 7], fill=INK)
    texto(d, x + 12, y, s, tam)


# ---------- cena 0: gancho, o check pula de linha ----------
def cena_0(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    titulo(d, 265, "O check pulou", 92, lt, -0.25, VERMELHO)
    # celular grande desenhado à mão
    moldura(d, ret(170, 360, 910, 1340), 1, 1.0, None, w=7)
    moldura(d, ret(200, 410, 880, 1270), 2, 1.0, GELO, w=4)
    traco(d, [(500, 1305), (580, 1305)], 3, 1.0, w=6)
    texto(d, 540, 470, "Tarefas", 58)
    traco(d, [(260, 520), (820, 520)], 4, 1.0, w=4)
    ys = [650, 860, 1070]
    itens = ["Comprar pão", "Pagar conta", "Ligar p/ mãe"]
    risco = entra(lt, 0.0, 0.7)
    sai = lt >= 0.9
    sobe = entra(lt, 0.9, 0.4)
    if not sai:
        linha_lista(d, 225, 855, ys[0], itens[0], 10, 0.0, risco, tam=60)
        linha_lista(d, 225, 855, ys[1], itens[1], 20, 0.0, tam=60)
        linha_lista(d, 225, 855, ys[2], itens[2], 30, 0.0, tam=60)
    else:
        linha_lista(d, 225, 855, ys[1] - 210 * sobe, itens[1], 20, 0.0, tam=60)
        linha_lista(d, 225, 855, ys[2] - 210 * sobe, itens[2], 30, 0.0, tam=60)
    # o check fica preso na 2ª posição, não no item
    k = pulso(lt, 2.5, 0.08)
    check(d, 295, ys[1] - 4, 0.75 * k, 77, 1.0)
    if lt >= 1.4:
        a = entra(lt, 1.4, 0.4)
        k = pulso(lt, 2, 0.02)
        oval = [(540 + 345 * k * math.cos(t), ys[1] + 95 * k * math.sin(t)) for t in [math.tau * i / 60 for i in range(60)]]
        traco(d, oval, 88, a, w=7, amp=3, col=VERMELHO, fechado=True)
        seta(d, 540, 1150, 540, ys[1] + 110, 89, entra(lt, 1.7, 0.3), VERMELHO)
        if a >= 0.99:
            texto(d, 540, 1205, "?", int(120 * pulso(lt, 3, 0.1)), VERMELHO)
    return im


# ---------- cena 1: navegador pergunta ----------
def cena_1(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    f1, f2 = entra(lt, 0.0, 0.5), entra(lt, 0.25, 0.5)
    pessoa(d, 270, 1060, 2.0 * max(0.01, mola(lt, 0.0)), 5, f1)
    # braço apontando para o notebook
    if f1 >= 0.99:
        traco(d, [(270, 980), (420, 900 + 12 * math.sin(lt * 4))], 9, 1.0, w=6)
    texto(d, 270, 1400, "navegador", 52)
    notebook(d, 640, 960, 360, 250, ["List {", "ForEach(...)", "}"], 20, f2, tam=46, lt=lt)
    pessoa(d, 935, 1060, 1.8 * max(0.01, mola(lt, 0.25)), 30, f2)
    texto(d, 935, 1400, "piloto", 52)
    fb = entra(lt, 0.6, 0.4)
    balao(d, 540, 480, 760, 270, ["Como identifica", "cada linha?"], 40, fb, 72, "esq")
    if fb >= 0.99:
        texto(d, 880, 690, "?", int(120 * pulso(lt, 3, 0.12)), VERMELHO)
    return im


# ---------- cena 2: o código com id: \.self ----------
def cena_2(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    codigo = ["ForEach(items.indices,", "   id: \\.self) { i in", "  Linha(item: items[i])", "}"]
    total = sum(len(c) for c in codigo)
    digitados = int(total * entra(lt, 0.1, 2.0))
    notebook(d, 540, 860, 860, 440, codigo, 50, entra(lt, 0.0, 0.3), tam=56, mostrar=digitados, lt=lt)
    if lt >= 2.2:
        titulo(d, 300, "id: \\.self", 120, lt, 2.2, VERMELHO, BRANCO)
        a = entra(lt, 2.2, 0.4)
        x0 = 110 + 30 + fonte(56).getlength("   ")
        x1 = x0 + fonte(56).getlength("id: \\.self")
        y = 640 + 30 + 56 * 0.6 + 56 * 1.35
        pts = [(x0 - 20 + (x1 - x0 + 40) / 2 + (x1 - x0 + 40) / 2 * math.cos(t), y + 42 * math.sin(t))
               for t in [math.tau * k / 40 for k in range(40)]]
        traco(d, pts, 61, a, w=7, amp=3, col=SOL_AMARELO, fechado=True)
        seta(d, 540, 400, x0 + 60, y - 60, 62, entra(lt, 2.5, 0.3), VERMELHO)
    return im


# ---------- cena 3: hipótese, o check fica no lugar ----------
def cena_3(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    titulo(d, 280, "índice = identidade", 82, lt, 0.0, INK, GELO)
    ys = [560, 760, 960]
    itens = ["Comprar pão", "Pagar conta", "Ligar p/ mãe"]
    for k, y in enumerate(ys):
        e = mola(lt, 0.2 + 0.25 * k)
        if e > 0:
            r = 48 * e
            d.ellipse([235 - r, y - r, 235 + r, y + r], fill=SOL_AMARELO)
            traco(d, circ(235, y, r, 30), 100 + k, 1.0, w=5)
            texto(d, 235, y, str(k), int(60 * e))
    t_rem = 0.45 * dur
    risco = entra(lt, t_rem, 0.5)
    sobe = entra(lt, t_rem + 0.6, 0.5)
    ent = entra(lt, 0.3, 0.5)
    if ent > 0:
        if lt < t_rem + 0.6:
            linha_lista(d, 320, 900, ys[0], itens[0], 110, 0.0, risco)
            linha_lista(d, 320, 900, ys[1], itens[1], 120, 0.0)
            linha_lista(d, 320, 900, ys[2], itens[2], 130, 0.0)
        else:
            linha_lista(d, 320, 900, ys[1] - 200 * sobe, itens[1], 120, 0.0)
            linha_lista(d, 320, 900, ys[2] - 200 * sobe, itens[2], 130, 0.0)
        # check preso ao índice 1 por um fio
        traco(d, [(283, ys[1]), (355, ys[1])], 140, 1.0, w=5, col=VERMELHO)
        check(d, 394, ys[1] - 4, 0.75 * pulso(lt, 2.5, 0.08), 141, entra(lt, 0.8, 0.4))
    if lt >= t_rem + 1.0:
        texto(d, 540, 1130, "check fica no lugar", int(66 * mola(lt, t_rem + 1.0)) or 1, VERMELHO)
    if lt >= 0.75 * dur:
        k = mola(lt, 0.75 * dur)
        t = max(10, int(78 * k))
        larg = fonte(t).getlength("Hipótese nossa") + 80
        traco(d, ret(540 - larg / 2, 1310 - t * 0.8, 540 + larg / 2, 1310 + t * 0.8), 150, 1.0, w=8, col=VERMELHO, fechado=True)
        texto(d, 540, 1310, "Hipótese nossa", t, VERMELHO)
    return im


# ---------- cena 4: a correção, id acompanha o item ----------
def cena_4(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    # troca de código: o velho é riscado, o novo entra
    titulo(d, 270, "id: \\.self -> id: \\.id", 70, lt, 0.0, INK, BRANCO)
    if lt >= 0.6:
        x0 = 540 - fonte(70).getlength("id: \\.self -> id: \\.id") / 2
        x1 = x0 + fonte(70).getlength("id: \\.self")
        traco(d, [(x0 - 5, 275), (x0 - 5 + (x1 - x0 + 10) * entra(lt, 0.6, 0.4), 275)], 201, 1.0, w=8, col=VERMELHO)
    if lt >= 0.3 * dur:
        k = entra(lt, 0.3 * dur, 0.4)
        moldura(d, ret(190, 380, 890, 560), 210, k, (40, 44, 56))
        if k >= 0.99:
            texto(d, 220, 435, "struct Item: Identifiable", 46, (200, 235, 210), "lm")
            texto(d, 260, 505, "let id = UUID()", 46, (200, 235, 210), "lm")
    ys = [760, 950, 1140]
    itens = [("Comprar pão", "id: 7F3A"), ("Pagar conta", "id: B21C"), ("Ligar p/ mãe", "id: 9E04")]
    t_rem = 0.6 * dur
    risco = entra(lt, t_rem, 0.5)
    sobe = entra(lt, t_rem + 0.6, 0.5)
    for k, (nome, idt) in enumerate(itens):
        e = entra(lt, 0.2 + 0.2 * k, 0.4)
        if e <= 0:
            continue
        if k == 0 and lt >= t_rem + 0.6:
            continue
        y = ys[k] - (190 * sobe if k > 0 and lt >= t_rem + 0.6 else 0)
        linha_lista(d, 180, 760, y, nome, 220 + 10 * k, 1.0 if k == 1 else 0.0, risco if k == 0 else 0.0, tam=54)
        traco(d, [(760, y), (790, y - 10)], 260 + k, 1.0, w=4)
        etiqueta(d, 905, y - 10, idt, 270 + k, 38)
    if lt >= t_rem + 1.1:
        k = mola(lt, t_rem + 1.1)
        texto(d, 540, 1360, "check segue o item", max(10, int(70 * k)), VERDE_OK)
    return im


# ---------- cena 5: minha leitura ----------
def cena_5(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    titulo(d, 270, "Minha leitura", 70, lt, 0.0, AZUL)
    titulo(d, 400, "id acompanha o item", 76, lt, 0.3, INK, GELO, 901)
    # item que passeia e a etiqueta vai junto
    dx = 120 * math.sin(lt * 1.6)
    e = entra(lt, 0.5, 0.4)
    if e > 0:
        linha_lista(d, 210 + dx, 690 + dx, 680, "Pagar conta", 300, 1.0, tam=48)
        traco(d, [(690 + dx, 680), (730 + dx, 670)], 305, 1.0, w=4)
        etiqueta(d, 830 + dx, 670, "id: B21C", 306, 32)
    # item x lugar
    a, b = mola(lt, 0.9), mola(lt, 1.3)
    if a > 0:
        moldura(d, ret(200, 900, 500, 1300), 310, 1.0, BRANCO)
        texto(d, 350, 960, "item", 60)
        check(d, 350, 1150, 1.4 * a * pulso(lt, 2.5, 0.06), 311, 1.0)
    if b > 0:
        moldura(d, ret(580, 900, 880, 1300), 320, 1.0, BRANCO)
        texto(d, 730, 960, "lugar", 60)
        cruz(d, 730, 1150, 1.1 * b, 321, 1.0)
    return im


# ---------- cena 6: ressalva, uma causa possível ----------
def cena_6(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    k = pulso(lt, 2, 0.04)
    titulo(d, 285, "Uma causa possível", int(80 * k), lt, 0.0, VERMELHO, BRANCO)
    # a pista que vimos: índice como id
    e1 = entra(lt, 0.15, 0.4)
    if e1 > 0:
        moldura(d, ret(190, 470, 890, 650), 400, e1, BRANCO)
        if e1 >= 0.99:
            texto(d, 500, 560, "índice como id", 60)
            check(d, 790, 555, 0.8 * pulso(lt, 2.5, 0.06), 401, entra(lt, 0.5, 0.3))
    # outras causas possíveis, não verificadas
    t2 = 0.35 * dur
    e2 = entra(lt, t2, 0.4)
    if e2 > 0:
        moldura(d, ret(150, 760, 930, 980), 410, e2, (255, 250, 225))
        if e2 >= 0.99:
            texto(d, 540, 830, "pode haver outras causas", 54)
            texto(d, 540, 915, "não verificado", 48, VERMELHO)
    # pistas em aberto: três interrogações que surgem e pulsam
    for i, x in enumerate([300, 540, 780]):
        m = mola(lt, t2 + 0.5 + 0.25 * i)
        if m > 0:
            r = 90 * m
            d.ellipse([x - r, 1230 - r, x + r, 1230 + r], fill=(255, 250, 225))
            traco(d, circ(x, 1230, r, 34), 420 + i, 1.0, w=5)
            texto(d, x, 1230, "?", max(10, int(110 * m * pulso(lt + i, 3, 0.1))), VERMELHO)
    # lupa que vai da primeira pista para as abertas
    if lt < t2 + 0.5:
        xl, yl = 930, 520
    else:
        u = entra(lt, t2 + 0.5, 0.8)
        xl, yl = 930 - 390 * u, 520 + 600 * u
        xl += 240 * math.sin(lt * 1.5) * u
    lupa(d, xl, yl + 10 * math.sin(lt * 3), 0.9, 450, entra(lt, 0.2, 0.4))
    return im


# ---------- cena 7: pergunta de volta ----------
def cena_7(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    pessoa(d, 270, 1060, 2.0 * max(0.01, mola(lt, 0.0)), 500, entra(lt, 0.0, 0.5))
    texto(d, 270, 1400, "dev", 52)
    notebook(d, 720, 1000, 440, 280, ["// check pulou", "// 1: índice?", "// 2: ?"], 510,
             entra(lt, 0.2, 0.4), tam=48, lt=lt)
    fb = entra(lt, 0.3, 0.4)
    balao(d, 540, 500, 700, 300, ["Como você", "investiga?"], 520, fb, 86, "esq")
    if fb >= 0.99:
        texto(d, 930, 760, "?", int(140 * pulso(lt, 3, 0.14)), VERMELHO)
    return im
