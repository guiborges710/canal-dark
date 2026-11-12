"""Componentes NOVOS do video divisao-politica-jovens-homens-mulheres (proposta do Raphinha,
AGUARDANDO APROVACAO DO GUILHERME).

Cada funcao desenha UM componente, parametrizado por posicao, escala e `frac`
(progresso do traco/crescimento, 0..1). Importa a biblioteca-base do canal; mesmo estilo
e paleta. Icones basicos (pessoa, lupa, seta, balao, circ, traco, preencher...) ficam em
media/sketch_lib.py; componentes ja aprovados (ex.: boneco_pensando) em
media/sketch_componentes.py. Nada disso e duplicado aqui.

Cada componente tem uma companheira `*_box(...)` que devolve a caixa ocupada
(x, y, w, h), ancora no canto superior esquerdo, incluindo rotulos e legendas.

VISUAL NEUTRO (tema politico). Convencao de cor deste video:
  - ELAS = LARANJA (240,110,40)   jovens mulheres
  - ELES = LILAS   (130,105,185)  jovens homens
  - DIF  = amarelo claro / ambar   a diferenca (o "vao") entre os dois
  - INK  = tudo o que e metodo (regua, lupa, manchete, cartoes das bases)
Evitados de proposito: azul x vermelho (cores dos dois partidos dos EUA),
verde + amarelo juntos (leitura partidaria no Brasil), rosa x azul (estereotipo de genero).
Nenhum simbolo, bandeira, logo, nome de instituto ou figura politica.

NAO promover para media/sketch_componentes.py nem catalogo.md sem aprovacao do Guilherme.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *

ELAS = LARANJA
ELES = (130, 105, 185)
ELAS_CLARO = (250, 196, 160)
ELES_CLARO = (205, 194, 232)
DIF = (255, 228, 140)
DIF_LINHA = (205, 150, 30)
BRANCO = (255, 255, 255)
MADEIRA = (240, 222, 170)


# ---------------------------------------------------------------------------
# auxiliares
# ---------------------------------------------------------------------------
def _ef(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def larg_texto(s, tam):
    return fonte(tam).getlength(s)


def caixa_texto(x, y, s, tam, ancora="mm"):
    """Caixa (x, y, w, h) de um texto desenhado com texto(d, x, y, s, tam, ancora=...)."""
    w = larg_texto(s, tam)
    h = tam * 1.05
    dx = {"l": 0, "m": w / 2, "r": w}[ancora[0]]
    return (x - dx - 4, y - h / 2 - 4, w + 8, h + 8)


def tracejado(d, p0, p1, seed=0, w=5, col=FERRO, traco_px=22, vao_px=14):
    """Linha tracejada a mao de p0 a p1."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.dist(p0, p1)
    if L < 1:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t, k = 0.0, 0
    while t < L:
        t2 = min(L, t + traco_px)
        traco(d, [(x0 + ux * t, y0 + uy * t), (x0 + ux * t2, y0 + uy * t2)], seed + k, 1.0, w=w, amp=1, col=col)
        t += traco_px + vao_px
        k += 1


def _olho(d, cx, cy, s, olha, seed, cor):
    """Olho + nariz curto: mostra para que lado o boneco olha (-1 esq, +1 dir)."""
    if not olha:
        return
    ex, ey = cx + olha * 15 * s, cy - 116 * s
    d.ellipse([ex - 5 * s, ey - 5 * s, ex + 5 * s, ey + 5 * s], fill=cor)
    traco(d, [(cx + olha * 35 * s, cy - 110 * s), (cx + olha * 47 * s, cy - 102 * s),
              (cx + olha * 34 * s, cy - 97 * s)], seed, 1.0, w=4, amp=0.8, col=cor)


# ---------------------------------------------------------------------------
# 1. Boneco ELA (cabelo comprido + saia em triangulo)
# ---------------------------------------------------------------------------
def boneco_ela(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=ELAS, olha=0):
    """Boneco de palito feminino. (cx, cy) = centro do tronco (mesma ancora de `pessoa`).
    `olha`: -1 olha para a esquerda, +1 para a direita, 0 de frente."""
    sk = lambda pts, sd, fechado=False: traco(d, pts, seed + sd, frac, w=6, amp=2.2 * s, col=cor, fechado=fechado)
    sk(circ(cx, cy - 110 * s, 36 * s, 36), 1, True)
    # cabelo comprido caindo dos dois lados
    sk([(cx - 22 * s, cy - 142 * s), (cx - 42 * s, cy - 120 * s), (cx - 47 * s, cy - 90 * s), (cx - 50 * s, cy - 58 * s)], 2)
    sk([(cx + 22 * s, cy - 142 * s), (cx + 42 * s, cy - 120 * s), (cx + 47 * s, cy - 90 * s), (cx + 50 * s, cy - 58 * s)], 3)
    sk([(cx, cy - 74 * s), (cx, cy - 22 * s)], 4)
    saia = [(cx, cy - 26 * s), (cx - 48 * s, cy + 52 * s), (cx + 48 * s, cy + 52 * s)]
    if frac >= 0.99:
        preencher(d, saia, ELAS_CLARO if cor == ELAS else PAPEL)
    sk(saia, 5, True)
    sk([(cx, cy - 44 * s), (cx - 52 * s, cy + 2 * s)], 6)
    sk([(cx, cy - 44 * s), (cx + 52 * s, cy + 2 * s)], 7)
    sk([(cx - 18 * s, cy + 52 * s), (cx - 26 * s, cy + 125 * s)], 8)
    sk([(cx + 18 * s, cy + 52 * s), (cx + 26 * s, cy + 125 * s)], 9)
    if frac >= 0.99:
        _olho(d, cx, cy, s, olha, seed + 20, cor)


def boneco_ela_box(cx, cy, s=1.0):
    return (cx - 58 * s, cy - 150 * s, 116 * s, 280 * s)


# ---------------------------------------------------------------------------
# 2. Boneco ELE (boneco simples + topete curto)
# ---------------------------------------------------------------------------
def boneco_ele(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=ELES, olha=0):
    """Boneco de palito masculino simples. Mesma ancora e tamanho de `boneco_ela`."""
    pessoa(d, cx, cy, s=s, seed=seed, frac=frac, cor=cor)
    for k, dx in enumerate((-16, 0, 16)):
        traco(d, [(cx + dx * s, cy - 144 * s), (cx + (dx + 6) * s, cy - 158 * s)], seed + 30 + k, frac, w=5, amp=1, col=cor)
    if frac >= 0.99:
        _olho(d, cx, cy, s, olha, seed + 20, cor)


def boneco_ele_box(cx, cy, s=1.0):
    return (cx - 58 * s, cy - 162 * s, 116 * s, 292 * s)


# ---------------------------------------------------------------------------
# 3. Dupla distante (gancho): de costas, linha tracejada, lupa em cima
# ---------------------------------------------------------------------------
def dupla_distante(d, cx, cy, s=1.3, seed=0, frac=1.0, dist=380, com_lupa=True):
    """Ela a esquerda olhando para fora, ele a direita olhando para fora, separados por uma
    linha tracejada vertical; lupa em cima da linha. Anime `dist` (ex.: 200 -> 380) para
    'se afastarem'."""
    boneco_ela(d, cx - dist / 2, cy, s=s, seed=seed, frac=frac, olha=-1)
    boneco_ele(d, cx + dist / 2, cy, s=s, seed=seed + 50, frac=frac, olha=+1)
    if frac >= 0.99:
        tracejado(d, (cx, cy - 190 * s), (cx, cy + 130 * s), seed=seed + 80, w=5, col=FERRO)
        if com_lupa:
            lupa(d, cx, cy - 285 * s, s=0.75 * s, seed=seed + 90)


def dupla_distante_box(cx, cy, s=1.3, dist=380):
    x0 = cx - dist / 2 - 58 * s
    x1 = cx + dist / 2 + 58 * s
    return (x0, cy - 335 * s, x1 - x0, 335 * s + 130 * s)


# ---------------------------------------------------------------------------
# 4. Etiqueta (o "rotulo" literal: liberal)
# ---------------------------------------------------------------------------
def etiqueta_rotulo(d, cx, cy, txt="liberal", s=1.0, seed=0, frac=1.0, cor_txt=INK):
    """Etiqueta de pendurar (ponta a esquerda + furo) com uma palavra. Mostra que o dado
    e um rotulo que a pessoa escolhe para si."""
    tam = int(48 * s)
    tw = larg_texto(txt, tam)
    h = 86 * s
    wtot = tw + 110 * s
    x0 = cx - wtot / 2
    x1 = x0 + wtot
    c = [(x0, cy), (x0 + 44 * s, cy - h / 2), (x1, cy - h / 2), (x1, cy + h / 2), (x0 + 44 * s, cy + h / 2)]
    if frac >= 0.99:
        preencher(d, c, (255, 250, 228))
    traco(d, c, seed, frac, w=6, amp=1.8, fechado=True)
    if frac >= 0.99:
        traco(d, circ(x0 + 34 * s, cy, 9 * s, 14), seed + 1, 1.0, w=4, amp=0.6, fechado=True)
        texto(d, x0 + 44 * s + (wtot - 44 * s) / 2 + 4 * s, cy - 2 * s, txt, tam, cor_txt)


def etiqueta_rotulo_box(cx, cy, txt="liberal", s=1.0):
    tw = larg_texto(txt, int(48 * s))
    wtot = tw + 110 * s
    return (cx - wtot / 2 - 4, cy - 43 * s - 4, wtot + 8, 86 * s + 8)


# ---------------------------------------------------------------------------
# 5. Barras em dois grupos (elas x eles, tres periodos)
# ---------------------------------------------------------------------------
def _barras_geo(cx, s):
    bw, gi, gg = 88 * s, 24 * s, 100 * s
    gw = 3 * bw + 2 * gi
    x0 = cx - (2 * gw + gg) / 2
    return bw, gi, gg, gw, x0


def barras_grupos(d, cx, y_base, s=1.0, seed=0, frac=1.0, frac_elas=None, frac_eles=None,
                  elas=(28, 32, 40), eles=(25, 27, 25), periodos=("01-07", "08-16", "17-24"),
                  app=13, legenda=True):
    """Dois grupos de 3 barras (elas a esquerda, eles a direita), valor em % no topo,
    periodo embaixo e legenda (bonequinho + palavra). `app` = pixels por ponto percentual.
    `frac` desenha o chao; `frac_elas`/`frac_eles` crescem cada grupo (use entra(lt, t) no
    momento em que a fala diz os numeros de cada grupo). As 3 barras do grupo crescem em sequencia."""
    bw, gi, gg, gw, x0 = _barras_geo(cx, s)
    fe = frac if frac_elas is None else frac_elas
    fm = frac if frac_eles is None else frac_eles
    traco(d, [(x0 - 30 * s, y_base), (x0 + 2 * gw + gg + 30 * s, y_base)], seed, _ef(frac * 3), w=7)
    tam_v, tam_p = int(44 * s), int(32 * s)
    for g, (vals, fg, cor) in enumerate(((elas, fe, ELAS), (eles, fm, ELES))):
        gx = x0 + g * (gw + gg)
        for k, v in enumerate(vals):
            f = _ef(fg * 3 - k)
            bx = gx + k * (bw + gi) + bw / 2
            h = v * app * s * f
            if h > 4:
                b = [(bx - bw / 2, y_base), (bx - bw / 2, y_base - h), (bx + bw / 2, y_base - h), (bx + bw / 2, y_base)]
                preencher(d, b, cor)
                traco(d, b, seed + 10 + 5 * g + k, 1.0, w=5, amp=1.6, fechado=True)
            if f >= 0.99:
                texto(d, bx, y_base - h - 34 * s, f"{v}%", tam_v)
            if frac >= 0.99:
                texto(d, bx, y_base + 34 * s, periodos[k], tam_p)
        if legenda and frac >= 0.99:
            mx = gx + gw / 2
            if g == 0:
                boneco_ela(d, mx - 66 * s, y_base + 150 * s, s=0.5 * s, seed=seed + 70)
            else:
                boneco_ele(d, mx - 66 * s, y_base + 150 * s, s=0.5 * s, seed=seed + 75)
            texto(d, mx - 24 * s, y_base + 150 * s, "elas" if g == 0 else "eles", int(48 * s), cor, ancora="lm")


def barras_grupos_box(cx, y_base, s=1.0, elas=(28, 32, 40), eles=(25, 27, 25), app=13):
    bw, gi, gg, gw, x0 = _barras_geo(cx, s)
    vmax = max(max(elas), max(eles))
    top = y_base - vmax * app * s - 34 * s - 26 * s
    base = y_base + 150 * s + 130 * 0.5 * s
    return (x0 - 30 * s, top, 2 * gw + gg + 60 * s, base - top)


# ---------------------------------------------------------------------------
# 6. Vao em pontos (par elas/eles com a diferenca destacada)
# ---------------------------------------------------------------------------
def vao_pontos(d, cx, y_base, v_ela, v_ele, s=1.0, seed=0, frac=1.0, app=13,
               rotulo="", periodo=""):
    """Duas barras lado a lado (ela laranja, ele lilas). O pedaco que falta na barra dele para
    alcancar a dela vira um bloco amarelo tracejado: a diferenca. `rotulo` (ex.: '15 pontos')
    vai em cima. frac: 0..0.6 barras crescem; 0.6..0.9 o vao aparece; >=0.95 rotulo."""
    bw, gap = 90 * s, 14 * s
    xa, xb = cx - (bw + gap) / 2, cx + (bw + gap) / 2
    fb = _ef(frac / 0.6)
    ha_cheio, hb_cheio = v_ela * app * s, v_ele * app * s
    for x, v, cor, sd in ((xa, v_ela, ELAS, 1), (xb, v_ele, ELES, 2)):
        h = v * app * s * fb
        if h > 4:
            b = [(x - bw / 2, y_base), (x - bw / 2, y_base - h), (x + bw / 2, y_base - h), (x + bw / 2, y_base)]
            preencher(d, b, cor)
            traco(d, b, seed + sd, 1.0, w=5, amp=1.6, fechado=True)
    traco(d, [(cx - bw - gap / 2 - 24 * s, y_base), (cx + bw + gap / 2 + 24 * s, y_base)], seed + 3, _ef(frac * 3), w=7)
    fv = _ef((frac - 0.6) / 0.3)
    if fv > 0.02 and ha_cheio > hb_cheio:
        yb, ya = y_base - hb_cheio, y_base - hb_cheio - (ha_cheio - hb_cheio) * fv
        preencher(d, [(xb - bw / 2, yb), (xb - bw / 2, ya), (xb + bw / 2, ya), (xb + bw / 2, yb)], DIF)
        pts = [(xb - bw / 2, yb), (xb - bw / 2, ya), (xb + bw / 2, ya), (xb + bw / 2, yb)]
        for i in range(3):
            tracejado(d, pts[i], pts[i + 1], seed=seed + 10 + 7 * i, w=4, col=DIF_LINHA, traco_px=12, vao_px=8)
    if frac >= 0.95:
        if rotulo:
            texto(d, cx, y_base - ha_cheio - 52 * s, rotulo, int(56 * s))
    if frac >= 0.99:
        texto(d, xa, y_base + 32 * s, "elas", int(30 * s), ELAS)
        texto(d, xb, y_base + 32 * s, "eles", int(30 * s), ELES)
        if periodo:
            texto(d, cx, y_base + 84 * s, periodo, int(36 * s))


def vao_pontos_box(cx, y_base, v_ela, v_ele, s=1.0, app=13, rotulo=""):
    bw, gap = 90 * s, 14 * s
    meia = bw + gap / 2 + 24 * s
    if rotulo:
        meia = max(meia, larg_texto(rotulo, int(56 * s)) / 2 + 4)
    top = y_base - max(v_ela, v_ele) * app * s - 52 * s - 34 * s
    return (cx - meia, top, 2 * meia, y_base + 84 * s + 24 * s - top)


# ---------------------------------------------------------------------------
# 7. Trajetorias (quem se mexeu: linha delas sobe, a deles fica reta)
# ---------------------------------------------------------------------------
def _traj_geo(cx, cy, s, vmin=20, vmax=44):
    X = [cx - 360 * s, cx - 100 * s, cx + 160 * s]
    Y = lambda v: cy + 260 * s - (v - vmin) / (vmax - vmin) * 520 * s
    return X, Y


def linhas_trajetoria(d, cx, cy, s=1.0, seed=0, frac=1.0, elas=(28, 32, 40), eles=(25, 27, 25),
                      periodos=("2001-07", "2008-16", "2017-24"), bonecos=True):
    """Grafico de linhas com 3 pontos por grupo. Linha delas (laranja) sobe e termina em seta;
    linha deles (lilas) fica reta e termina num '='. frac: 0..0.45 linha delas; 0.45..0.85
    linha deles; >=0.9 '=' e bonequinhos no fim de cada linha."""
    X, Y = _traj_geo(cx, cy, s)
    traco(d, [(cx - 410 * s, cy + 300 * s), (cx + 210 * s, cy + 300 * s)], seed, _ef(frac * 4), w=6, col=INK)
    if frac >= 0.99:
        for k, p in enumerate(periodos):
            texto(d, X[k], cy + 342 * s, p, int(30 * s))
    for vals, f0, f1, cor, dy, sd in ((elas, 0.0, 0.45, ELAS, -44, 10), (eles, 0.45, 0.85, ELES, 48, 30)):
        fl = _ef((frac - f0) / (f1 - f0))
        pts = [(X[k], Y(v)) for k, v in enumerate(vals)]
        nseg = fl * 2
        for k in range(2):
            fk = max(0.0, min(1.0, nseg - k))
            if fk <= 0:
                continue
            (xa, ya), (xb, yb) = pts[k], pts[k + 1]
            xe, ye = xa + (xb - xa) * fk, ya + (yb - ya) * fk
            if k == 1 and fk >= 0.99 and cor == ELAS:
                seta(d, xa, ya, xb, yb, seed=seed + sd + k, cor=cor, w=8)
            else:
                traco(d, [(xa, ya), (xe, ye)], seed + sd + k, 1.0, w=8, amp=1.5, col=cor)
        for k, (px, py) in enumerate(pts):
            if fl * 2 >= k - 0.01:
                d.ellipse([px - 12 * s, py - 12 * s, px + 12 * s, py + 12 * s], fill=cor, outline=INK, width=3)
                texto(d, px, py + dy * s, f"{vals[k]}%", int(40 * s), cor)
    if frac >= 0.9:
        ye = Y(eles[-1])
        for dy in (-10, 10):
            traco(d, [(cx + 214 * s, ye + dy * s), (cx + 250 * s, ye + dy * s)], seed + 60 + dy, 1.0, w=7, amp=0.8, col=ELES)
        if bonecos:
            boneco_ela(d, cx + 310 * s, Y(elas[-1]) + 20 * s, s=0.5 * s, seed=seed + 70, olha=-1)
            boneco_ele(d, cx + 310 * s, ye + 10 * s, s=0.5 * s, seed=seed + 80, olha=-1)


def linhas_trajetoria_box(cx, cy, s=1.0, elas=(28, 32, 40)):
    X, Y = _traj_geo(cx, cy, s)
    top = min(Y(max(elas)) - 44 * s - 26 * s, Y(max(elas)) + 20 * s - 162 * 0.5 * s)
    return (cx - 420 * s, top, 770 * s, cy + 362 * s - top)


# ---------------------------------------------------------------------------
# 8. Cartao de base (outra pesquisa: linha quase plana, lupa, numero circulado)
# ---------------------------------------------------------------------------
def cartao_base(d, cx, cy, s=1.0, seed=0, frac=1.0, numero=None, ano=None, legenda="",
                w=600, h=300):
    """Cartao branco com um grafico minimo: a linha da diferenca ao longo do tempo, quase plana.
    `numero` (ex.: '7') aparece circulado num ponto perto do fim, com `ano` em cima.
    `legenda` vai embaixo do cartao. Lupa no canto superior esquerdo."""
    W_, H_ = w * s, h * s
    x0, x1, y0, y1 = cx - W_ / 2, cx + W_ / 2, cy - H_ / 2, cy + H_ / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, BRANCO)
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if frac < 0.99:
        return
    traco(d, [(x0 + 40 * s, y1 - 40 * s), (x1 - 40 * s, y1 - 40 * s)], seed + 1, 1.0, w=4, amp=1, col=FERRO)
    yl = cy + 30 * s
    n = 12
    pts = [(x0 + 60 * s + k * (W_ - 120 * s) / (n - 1), yl + 9 * s * math.sin(k * 1.9 + seed)) for k in range(n)]
    traco(d, pts, seed + 2, 1.0, w=7, amp=1.2, col=DIF_LINHA)
    lupa(d, x0 + 72 * s, y0 + 72 * s, s=0.55 * s, seed=seed + 3)
    if numero:
        px, py = pts[9]
        r = 46 * s
        d.ellipse([px - r, py - r, px + r, py + r], fill=BRANCO)
        traco(d, circ(px, py, r, 30), seed + 4, 1.0, w=6, amp=1.5, fechado=True)
        texto(d, px, py - 2 * s, str(numero), int(56 * s))
        if ano:
            texto(d, px, py - r - 26 * s, str(ano), int(32 * s))
    if legenda:
        texto(d, cx, y1 + 50 * s, legenda, int(44 * s))


def cartao_base_box(cx, cy, s=1.0, legenda="", w=600, h=300):
    W_, H_ = w * s, h * s
    alt = H_ + (80 * s if legenda else 0)
    larg = max(W_, larg_texto(legenda, int(44 * s)) + 8 if legenda else 0)
    return (cx - larg / 2, cy - H_ / 2, larg, alt)


# ---------------------------------------------------------------------------
# 9. Regua
# ---------------------------------------------------------------------------
def _rot(cx, cy, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)


def regua(d, cx, cy, comp=600, s=1.0, seed=0, frac=1.0, ang=0.0):
    """Regua de madeira clara com marcacoes (sem numeros, para nao parecer dado).
    `comp` em px (ja na escala); `ang` em radianos (inclinar ou animar)."""
    R = _rot(cx, cy, ang)
    hh = 40 * s
    c = [R(-comp / 2, -hh), R(comp / 2, -hh), R(comp / 2, hh), R(-comp / 2, hh)]
    if frac >= 0.99:
        preencher(d, c, MADEIRA)
    traco(d, c, seed, frac, w=6, amp=1.8, fechado=True)
    if frac >= 0.99:
        n = 24
        for k in range(1, n):
            x = -comp / 2 + k * comp / n
            L = 34 * s if k % 4 == 0 else 18 * s
            traco(d, [R(x, -hh), R(x, -hh + L)], seed + 10 + k, 1.0, w=4 if k % 4 else 5, amp=0.6)


def regua_box(cx, cy, comp=600, s=1.0, ang=0.0):
    R = _rot(cx, cy, ang)
    hh = 40 * s
    pts = [R(-comp / 2, -hh), R(comp / 2, -hh), R(comp / 2, hh), R(-comp / 2, hh)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - 4, min(ys) - 4, max(xs) - min(xs) + 8, max(ys) - min(ys) + 8)


# ---------------------------------------------------------------------------
# 10. Manchete (jornal generico com a frase que muda conforme a regua)
# ---------------------------------------------------------------------------
def manchete(d, cx, cy, s=1.0, seed=0, frac=1.0, titulo=("diferença", "cresce")):
    """Folha de jornal generica (sem nome de veiculo): cabecalho 'notícias', manchete em
    ate 2 linhas e linhas de texto cinza. Troque `titulo` para mostrar que a manchete
    depende da regua (ex.: ('diferença','cresce') -> ('diferença','estável'))."""
    w, h = 520 * s, 380 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, BRANCO)
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if frac < 0.99:
        return
    texto(d, cx, y0 + 34 * s, "notícias", int(30 * s), FERRO)
    traco(d, [(x0 + 24 * s, y0 + 60 * s), (x1 - 24 * s, y0 + 60 * s)], seed + 1, 1.0, w=5, amp=1)
    for i, linha in enumerate(titulo[:2]):
        texto(d, cx, y0 + 112 * s + i * 64 * s, linha, int(58 * s))
    yb = y0 + 112 * s + len(titulo[:2]) * 64 * s + 10 * s
    for i in range(3):
        y = yb + i * 30 * s
        if y > y1 - 22 * s:
            break
        traco(d, [(x0 + 34 * s, y), (x1 - 34 * s - (60 * s if i == 2 else 0), y)], seed + 5 + i, 1.0, w=5, amp=0.8, col=FERRO)


def manchete_box(cx, cy, s=1.0):
    w, h = 520 * s, 380 * s
    return (cx - w / 2, cy - h / 2, w, h)


# ---------------------------------------------------------------------------
# 11. "Geracao": um rotulo que junta dois grupos em ritmos diferentes
# ---------------------------------------------------------------------------
def geracao_dois_ritmos(d, cx, cy, s=1.0, seed=0, frac=1.0, rotulo='"geração"', f_setas=None):
    """Moldura tracejada com o rotulo em cima; dentro, ela (linha de cima) e ele (linha de
    baixo), cada um com uma seta de comprimento diferente: dois ritmos sob o mesmo rotulo.
    `f_setas` (0..1) faz as setas crescerem; padrao = frac."""
    w, h = 720 * s, 520 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    if frac >= 0.99:
        for p0, p1, k in (((x0, y0), (x1, y0), 0), ((x1, y0), (x1, y1), 1), ((x1, y1), (x0, y1), 2), ((x0, y1), (x0, y0), 3)):
            tracejado(d, p0, p1, seed=seed + 100 * k, w=5, col=INK, traco_px=26, vao_px=16)
        tam = int(50 * s)
        tw = larg_texto(rotulo, tam)
        d.rectangle([cx - tw / 2 - 16 * s, y0 - 30 * s, cx + tw / 2 + 16 * s, y0 + 30 * s], fill=PAPEL)
        texto(d, cx, y0 - 2 * s, rotulo, tam)
    yA, yB = cy - 105 * s, cy + 135 * s
    boneco_ela(d, cx - 250 * s, yA, s=0.62 * s, seed=seed + 10, frac=frac, olha=+1)
    boneco_ele(d, cx - 250 * s, yB, s=0.62 * s, seed=seed + 40, frac=frac, olha=+1)
    fs = frac if f_setas is None else f_setas
    if fs > 0.02:
        xa0 = cx - 170 * s
        seta(d, xa0, yA - 20 * s, xa0 + (470 * s) * _ef(fs), yA - 20 * s, seed=seed + 70, frac=1.0 if fs >= 0.99 else 0.98, cor=ELAS, w=8)
        seta(d, xa0, yB - 20 * s, xa0 + (190 * s) * _ef(fs), yB - 20 * s, seed=seed + 80, frac=1.0 if fs >= 0.99 else 0.98, cor=ELES, w=8)


def geracao_dois_ritmos_box(cx, cy, s=1.0):
    w, h = 720 * s, 520 * s
    return (cx - w / 2 - 4, cy - h / 2 - 34 * s, w + 8, h + 38 * s)


# ---------------------------------------------------------------------------
# 12. Regua + pergunta (fechamento): os dois olham para a mesma regua
# ---------------------------------------------------------------------------
def regua_pergunta(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0):
    """Balao redondo com '?' (pulsa com `t`), regua levemente inclinada no meio e, embaixo,
    ela e ele lado a lado olhando para a regua (rima com o gancho, onde estavam de costas)."""
    bx, by, r = cx, cy - 330 * s, 95 * s
    if frac >= 0.99:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=BRANCO)
    traco(d, circ(bx, by, r, 40), seed, frac, w=6, amp=2, fechado=True)
    if frac >= 0.99:
        texto(d, bx, by - 6 * s, "?", int(140 * s * (1 + 0.08 * math.sin(t * 6))))
        for (px, py, pr), k in (((cx - 40 * s, cy - 205 * s, 15 * s), 1), ((cx - 58 * s, cy - 168 * s, 9 * s), 2)):
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=BRANCO)
            traco(d, circ(px, py, pr, 16), seed + 10 + k, 1.0, w=4, amp=0.6, fechado=True)
    regua(d, cx, cy - 60 * s, comp=600 * s, s=s, seed=seed + 20, frac=frac, ang=-0.08)
    boneco_ela(d, cx - 200 * s, cy + 205 * s, s=1.0 * s, seed=seed + 40, frac=frac, olha=+1)
    boneco_ele(d, cx + 200 * s, cy + 205 * s, s=1.0 * s, seed=seed + 60, frac=frac, olha=-1)


def regua_pergunta_box(cx, cy, s=1.0):
    return (cx - 310 * s, cy - 430 * s, 620 * s, 430 * s + 205 * s + 130 * s)
