"""Cenas do jovens-trocam-de-emprego (estilo sketch).

Componentes do catalogo reutilizados: balao (sketch_lib) e boneco_pensando nao entram; o resto e combinacao
de traco/circ da biblioteca, desenhado aqui (porta, caixa de papelao, cracha, escada, predio, livro).
Convencao de cor: AZUL = a mesma pessoa ao longo da vida (o colega, o "povo estavel" quando jovem);
INK = quem solta o rotulo; SEPIA = o jovem de decadas atras; LARANJA = troca/queda; VERMELHO = risco do rotulo.

Regras: nada cobre boneco nem texto; tudo entre SEGURO_TOPO e SEGURO_BASE; sem legenda na base; numeros
na tela so os 2 do roteiro ("mais de 5", "quase 3 anos"); sem celular. Tempos de entrada em fracoes de `dur`,
para acompanhar a fala qualquer que seja a duracao real da narracao.
"""
import math

from PIL import ImageDraw
from media.sketch_lib import *

KRAFT = (214, 170, 115)
SEPIA = (140, 100, 60)
CINZA = (90, 90, 100)
GRISALHO = (165, 165, 172)
BRANCO = (255, 255, 255)
LUZ = (255, 236, 170)
PORTA_COR = (226, 214, 192)


# ---------------------------------------------------------------------------
# utilitarios
# ---------------------------------------------------------------------------
def _parcial(lt, t0=0.0, dur=0.5, minimo=0.35):
    """Contorno ja comecado no quadro 0 (nada de papel em branco) e completo em `dur` s."""
    return minimo + (1 - minimo) * entra(lt, t0, dur)


def _txt_mola(d, x, y, s, tam, cor, lt, t0):
    k = mola(lt, t0)
    if k > 0.05:
        texto(d, x, y, s, max(10, int(tam * k)), cor)


def _ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ---------------------------------------------------------------------------
# pecas desenhadas para este video
# ---------------------------------------------------------------------------
def caixa_papelao(d, cx, cy, s, seed, frac=1.0, planta=True):
    """Caixa de mudanca (quem sai do emprego). (cx, cy) = centro; ~110x80 * s, com planta saindo."""
    x0, x1, y0, y1 = cx - 55 * s, cx + 55 * s, cy - 40 * s, cy + 40 * s
    if planta and frac >= 0.99:
        traco(d, [(cx + 20 * s, y0), (cx + 22 * s, y0 - 55 * s)], seed + 5, 1.0, w=5, amp=1, col=(60, 130, 70))
        for k, (dx, dy) in enumerate(((-14, -40), (16, -52), (-6, -62))):
            px, py = cx + 22 * s + dx * s, y0 + dy * s
            d.ellipse([px - 13 * s, py - 7 * s, px + 13 * s, py + 7 * s], fill=VERDE)
    if frac >= 0.99:
        preencher(d, _ret(x0, y0, x1, y1), KRAFT)
    traco(d, _ret(x0, y0, x1, y1), seed, frac, w=6, amp=1.8, fechado=True)
    if frac >= 0.99:
        traco(d, [(x0, y0), (x0 - 18 * s, y0 - 22 * s)], seed + 1, 1.0, w=5, amp=1)
        traco(d, [(x1, y0), (x1 + 18 * s, y0 - 22 * s)], seed + 2, 1.0, w=5, amp=1)
        traco(d, [(cx - 22 * s, cy), (cx + 22 * s, cy)], seed + 3, 1.0, w=4, amp=1)


def boneco(d, cx, cy, s=1.5, seed=0, frac=1.0, cor=INK, fase=None, caixa=False, grisalho=0,
           bengala=False, chapeu=False, gravata=False):
    """Boneco de palito da lib, com pernas que andam (`fase`), caixa nos bracos, cabelo grisalho (0, 1, 2),
    bengala, chapeu e gravata. (cx, cy) = centro do tronco; pes em cy + ~125*s."""
    sk = lambda pts, sd, w=6, col=cor: traco(d, pts, seed + sd, frac, w=w, amp=2.5 * s, col=col)
    hy = cy - 110 * s
    sk(circ(cx, hy, 36 * s, 36), 1)
    sk([(cx, cy - 74 * s), (cx, cy + 40 * s)], 2)
    if fase is None:
        a1, a2 = 0.39, -0.39
    else:
        sw = 0.42 * math.sin(fase)
        a1, a2 = 0.1 + sw, -0.1 - sw
    for k, a in enumerate((a1, a2)):
        sk([(cx, cy + 40 * s), (cx + 92 * s * math.sin(a), cy + 40 * s + 92 * s * math.cos(a))], 5 + k)
    if caixa:
        sk([(cx, cy - 40 * s), (cx + 40 * s, cy - 18 * s)], 3)
        sk([(cx, cy - 36 * s), (cx + 40 * s, cy + 12 * s)], 4)
    else:
        sk([(cx, cy - 40 * s), (cx - 50 * s, cy + 5 * s)], 3)
        sk([(cx, cy - 40 * s), (cx + 50 * s, cy + 5 * s)], 4)
    if gravata and frac >= 0.99:
        g = [(cx - 9 * s, cy - 70 * s), (cx + 9 * s, cy - 70 * s), (cx + 12 * s, cy - 28 * s), (cx, cy - 14 * s), (cx - 12 * s, cy - 28 * s)]
        preencher(d, g, LARANJA)
        traco(d, g, seed + 40, 1.0, w=3, amp=0.8, fechado=True)
    if grisalho and frac >= 0.99:
        r = 42 * s
        a0, a1_ = (math.radians(235), math.radians(305)) if grisalho == 1 else (math.radians(190), math.radians(350))
        arco = [(cx + r * math.cos(a0 + (a1_ - a0) * k / 12), hy + r * math.sin(a0 + (a1_ - a0) * k / 12)) for k in range(13)]
        traco(d, arco, seed + 41, 1.0, w=int(10 * s), amp=1.2, col=GRISALHO)
    if bengala and frac >= 0.99:
        bx = cx + 52 * s
        traco(d, [(bx, cy + 2 * s), (bx + 8 * s, cy + 125 * s)], seed + 42, 1.0, w=6, amp=1, col=SEPIA)
        traco(d, [(bx, cy + 2 * s), (bx - 4 * s, cy - 14 * s), (bx - 18 * s, cy - 16 * s)], seed + 43, 1.0, w=6, amp=1, col=SEPIA)
    if chapeu and frac >= 0.99:
        top = hy - 30 * s
        coroa = _ret(cx - 26 * s, top - 34 * s, cx + 26 * s, top)
        preencher(d, coroa, SEPIA)
        traco(d, coroa, seed + 44, 1.0, w=4, amp=1, fechado=True, col=SEPIA)
        traco(d, [(cx - 50 * s, top), (cx + 50 * s, top)], seed + 45, 1.0, w=7, amp=1, col=SEPIA)
    if caixa:
        caixa_papelao(d, cx + 95 * s, cy - 4 * s, s, seed + 60, frac)


def porta(d, cx, base, s, seed, frac=1.0, aberta=0.0, im=None, lt=0.0):
    """Porta de escritorio. `aberta` 0..1 abre a folha (dobradica a esquerda) e mostra luz atras.
    Devolve `im` (a luz soma brilho)."""
    w, h = 150 * s, 330 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, base - h, base
    if frac >= 0.99:
        if aberta > 0.01:
            preencher(d, _ret(x0, y0, x1, y1), LUZ)
        else:
            preencher(d, _ret(x0, y0, x1, y1), PORTA_COR)
    traco(d, _ret(x0, y0, x1, y1), seed, frac, w=7, amp=2, fechado=True)
    if frac < 0.99:
        return im
    if aberta > 0.01:
        lw = w * (1 - 0.75 * aberta)
        folha = [(x0, y0), (x0 + lw, y0 + 18 * s * aberta), (x0 + lw, y1 - 10 * s * aberta), (x0, y1)]
        preencher(d, folha, PORTA_COR)
        traco(d, folha, seed + 3, 1.0, w=6, amp=1.5, fechado=True)
        if im is not None:
            im = brilho(im, cx + w * 0.15, base - h / 2, 170 * s, (60, 50, 10), 0.8 * aberta * tremer(lt, 3, 0.9, 0.1))
    else:
        vid = _ret(cx - w * 0.3, y0 + 30 * s, cx + w * 0.3, y0 + 110 * s)
        preencher(d, vid, GELO)
        traco(d, vid, seed + 1, 1.0, w=4, amp=1, fechado=True)
        kx, ky = x1 - 24 * s, base - h * 0.48
        d.ellipse([kx - 9 * s, ky - 9 * s, kx + 9 * s, ky + 9 * s], fill=INK)
    return im


def cracha(d, cx, cy, s, seed, frac=1.0, cor=AZUL):
    """Cracha de emprego: cartao branco, faixa colorida, foto e duas linhas. ~90x120 * s."""
    x0, x1, y0, y1 = cx - 45 * s, cx + 45 * s, cy - 60 * s, cy + 60 * s
    if frac >= 0.99:
        preencher(d, _ret(x0, y0, x1, y1), BRANCO)
        preencher(d, _ret(x0, y0, x1, y0 + 30 * s), cor)
    traco(d, _ret(x0, y0, x1, y1), seed, frac, w=5, amp=1.5, fechado=True)
    if frac >= 0.99:
        traco(d, _ret(cx - 14 * s, y0 - 12 * s, cx + 14 * s, y0 + 6 * s), seed + 1, 1.0, w=4, amp=0.8, fechado=True)
        traco(d, circ(cx, cy + 2 * s, 17 * s, 20), seed + 2, 1.0, w=4, amp=1, fechado=True)
        traco(d, [(cx - 28 * s, cy + 32 * s), (cx + 28 * s, cy + 32 * s)], seed + 3, 1.0, w=4, amp=1)
        traco(d, [(cx - 20 * s, cy + 46 * s), (cx + 20 * s, cy + 46 * s)], seed + 4, 1.0, w=4, amp=1)


CORES_CRACHA = [AZUL, LARANJA, VERDE, SOL_AMARELO, (225, 90, 100)]


def pilha_crachas(d, cx, base, n, s, seed, lt, t0, passo=0.12):
    """`n` crachas empilhados de baixo para cima, cada um entra com mola."""
    for i in range(n):
        k = mola(lt, t0 + i * passo, 0.35)
        if k > 0.05:
            cracha(d, cx, base - 60 * s - i * 46 * s, s * k, seed + 10 * i, entra(lt, t0 + i * passo, 0.3), CORES_CRACHA[i % 5])


def calendario_folheando(d, cx, cy, s, seed, lt, frac=1.0):
    """Calendario sem datas com a folha de cima virando sem parar (o tempo passando)."""
    calendario(d, cx, cy, s, seed, frac)
    if frac < 0.99:
        return
    p = (lt * 1.6) % 1.0
    topo, alto = cy - 40 * s, 140 * s
    yb = topo + alto * math.cos(p * math.pi)
    folha = [(cx - 100 * s, topo), (cx + 100 * s, topo), (cx + 100 * s, yb), (cx - 100 * s, yb)]
    if abs(yb - topo) > 4:
        preencher(d, folha, BRANCO)
        traco(d, folha, seed + 20, 1.0, w=4, amp=1, fechado=True)


def etiqueta_riscada(d, cx, cy, s_txt, tam, seed, frac=1.0, risco=0.0):
    """Etiqueta (rotulo) com furo, e um risco vermelho que a atravessa."""
    larg = len(s_txt) * tam * 0.52 + 90
    alt = tam * 1.5
    x0, x1, y0, y1 = cx - larg / 2, cx + larg / 2, cy - alt / 2, cy + alt / 2
    c = [(x0 + 40, y0), (x1, y0), (x1, y1), (x0 + 40, y1), (x0, cy)]
    if frac >= 0.99:
        preencher(d, c, (255, 248, 220))
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if frac >= 0.99:
        traco(d, circ(x0 + 38, cy, 9, 14), seed + 1, 1.0, w=4, amp=0.5, fechado=True)
        texto(d, cx + 18, cy, s_txt, tam)
    if risco > 0:
        traco(d, [(x0 - 20, cy + alt * 0.35), (x1 + 20, cy - alt * 0.35)], seed + 2, risco, w=12, amp=2, col=VERMELHO)


def livro(d, cx, cy, s, seed, frac=1.0):
    c = _ret(cx - 48 * s, cy - 60 * s, cx + 48 * s, cy + 60 * s)
    if frac >= 0.99:
        preencher(d, c, AZUL)
    traco(d, c, seed, frac, w=6, amp=1.5, fechado=True)
    if frac >= 0.99:
        traco(d, [(cx - 32 * s, cy - 60 * s), (cx - 32 * s, cy + 60 * s)], seed + 1, 1.0, w=4, amp=1)
        pag = _ret(cx - 18 * s, cy - 30 * s, cx + 34 * s, cy - 6 * s)
        preencher(d, pag, BRANCO)
        traco(d, pag, seed + 2, 1.0, w=3, amp=0.6, fechado=True)


def contrato_curto(d, cx, cy, s, seed, frac=1.0):
    """Folha de contrato cortada pela metade (a vaga curta): borda de baixo picotada, tesoura de risco."""
    x0, x1, y0 = cx - 70 * s, cx + 70 * s, cy - 90 * s
    yc = cy + 20 * s
    zig = [(x1, yc)] + [(x1 - k * 20 * s, yc + (10 * s if k % 2 else -6 * s)) for k in range(1, 8)]
    c = [(x0, y0), (x1, y0)] + zig + [(x0, yc)]
    if frac >= 0.99:
        preencher(d, c, BRANCO)
    traco(d, c, seed, frac, w=6, amp=1.5, fechado=True)
    if frac >= 0.99:
        for k in range(3):
            traco(d, [(x0 + 20 * s, y0 + 30 * s + k * 28 * s), (x1 - 20 * s - 18 * k * s, y0 + 30 * s + k * 28 * s)], seed + 3 + k, 1.0, w=4, amp=1)
        # pedaco que caiu
        resto = [(x0 + 10 * s, yc + 40 * s), (x1 - 30 * s, yc + 48 * s), (x1 - 34 * s, yc + 80 * s), (x0 + 6 * s, yc + 74 * s)]
        traco(d, resto, seed + 9, 1.0, w=4, amp=1.5, fechado=True, col=FERRO)


def predio(d, cx, base, s, seed, frac=1.0):
    w, h = 250 * s, 400 * s
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    c = _ret(x0, y0, x1, base)
    if frac >= 0.99:
        preencher(d, c, (232, 232, 236))
    traco(d, c, seed, frac, w=7, amp=2, fechado=True)
    if frac >= 0.99:
        for r in range(4):
            for k in range(3):
                jx, jy = x0 + 45 * s + k * 80 * s, y0 + 45 * s + r * 70 * s
                j = _ret(jx - 20 * s, jy - 18 * s, jx + 20 * s, jy + 18 * s)
                preencher(d, j, GELO)
                traco(d, j, seed + 10 + r * 3 + k, 1.0, w=3, amp=0.8, fechado=True)
        pt = _ret(cx - 32 * s, base - 85 * s, cx + 32 * s, base)
        preencher(d, pt, FERRO)
        traco(d, pt, seed + 30, 1.0, w=5, amp=1, fechado=True)


def escada(d, x0, base, n, larg, alt, seed, frac=1.0):
    """Escada subindo para a direita a partir de (x0, base). Devolve a lista de (x_centro, y_topo) dos degraus."""
    pts = [(x0, base)]
    topos = []
    for k in range(n):
        y = base - alt * (k + 1)
        pts += [(x0 + larg * k, y), (x0 + larg * (k + 1), y)]
        topos.append((x0 + larg * (k + 0.5), y))
    pts.append((x0 + larg * n, base))
    if frac >= 0.99:
        preencher(d, pts, (236, 228, 210))
    traco(d, pts, seed, frac, w=7, amp=2)
    traco(d, [(x0 - 260, base), (x0 + larg * n + 20, base)], seed + 1, frac, w=6, amp=2)
    return topos


# ---------------------------------------------------------------------------
# CENA 0 - gancho: o colega sai com a caixa; o outro solta o rotulo
# ---------------------------------------------------------------------------
def cena_0(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    chao = 1420
    traco(d, [(40, chao), (1040, chao)], 900, _parcial(lt, 0.0, 0.4, 0.5), w=6)
    im = porta(d, 215, chao, 1.45, 910, _parcial(lt, 0.0, 0.4, 0.4), im=im)
    d = ImageDraw.Draw(im)
    # o colega anda saindo, com a caixa
    x = 420 + 120 * entra(lt, 0.0, dur * 0.9)
    boneco(d, x, chao - 125 * 1.55, 1.55, 920, _parcial(lt, 0.0, 0.35, 0.5), AZUL, fase=lt * 7, caixa=True)
    # quem solta o rotulo
    k = mola(lt, 0.15)
    if k > 0.05:
        boneco(d, 900, chao - 125 * 1.55, 1.55, 940, entra(lt, 0.15, 0.4), INK)
    # "poucos meses": calendario folheando
    tc = 0.22 * dur
    fc = entra(lt, tc, 0.35)
    if fc > 0:
        calendario_folheando(d, 300, 330, 0.8, 960, lt, fc)
        _txt_mola(d, 670, 330, "poucos meses", 66, INK, lt, tc + 0.1)
    # o rotulo
    tb = 0.48 * dur
    kb = mola(lt, tb)
    if kb > 0.05:
        balao(d, 580, 640, 780 * kb, 240 * kb, ["essa geração não", "segura emprego"], seed=970,
              tam=max(10, int(58 * kb * pulso(lt, vel=2.0, amp=0.025))), cauda="dir")
    return im


# ---------------------------------------------------------------------------
# CENA 1 - EUA: a mesma pessoa acompanhada por decadas (jovem -> pais e avos)
# ---------------------------------------------------------------------------
def cena_1(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    k = max(0.6, mola(lt, 0.0, 0.35))
    texto(d, 540, 290, "EUA", int(120 * k))
    yb = 1220
    boneco(d, 240, yb, 1.5, 100, _parcial(lt, 0.0, 0.4, 0.4), AZUL)
    # linha do tempo: seta crescendo e lupa acompanhando
    ts = 0.12 * dur
    fs = entra(lt, ts, 0.55 * dur)
    if fs > 0:
        x1 = 360 + 340 * fs
        seta(d, 360, 1130, x1, 1130, seed=110, frac=1.0 if fs > 0.98 else fs, cor=LARANJA)
        if fs < 0.98:
            lupa(d, x1 - 10, 1010, 0.6, 120)
    calendario_folheando(d, 540, 800, 1.1, 130, lt, entra(lt, ts, 0.4))
    _txt_mola(d, 540, 420, "as mesmas pessoas", 62, CINZA, lt, 0.4 * dur)
    tv = 0.12 * dur + 0.55 * dur
    kv = mola(lt, tv)
    if kv > 0.05:
        boneco(d, 830, yb, 1.5 * kv, 140, entra(lt, tv, 0.35), AZUL, grisalho=2, bengala=True, gravata=True)
    _txt_mola(d, 830, 1450, "pais e avós", 56, INK, lt, 0.8 * dur)
    return im


# ---------------------------------------------------------------------------
# CENA 2 - o "povo estavel" de hoje, quando jovem: mais de 5 crachas
# ---------------------------------------------------------------------------
def cena_2(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    yb = 1230
    # hoje: estavel, grisalho, de gravata (a esquerda)
    boneco(d, 220, yb, 1.2, 200, _parcial(lt, 0.0, 0.4, 0.4), AZUL, grisalho=2, bengala=True, gravata=True)
    _txt_mola(d, 220, 1450, "hoje", 54, CINZA, lt, 0.05)
    # volta no tempo: o mesmo, jovem
    tj = 0.3 * dur
    fa = entra(lt, tj - 0.3, 0.4)
    if fa > 0:
        seta(d, 330, 1150, 330 + 150 * fa, 1150, seed=210, frac=fa, cor=LARANJA, w=6)
    kj = mola(lt, tj)
    if kj > 0.05:
        boneco(d, 680, yb, 1.6 * kj, 220, entra(lt, tj, 0.35), AZUL)
    # os crachas, um por emprego (5, ate "cinco")
    tn = 0.55 * dur
    pos = [(400, 860), (530, 760), (680, 720), (830, 760), (960, 860)]
    passo = max(0.12, (tn - tj - 0.2) / 5)
    for i, (px, py) in enumerate(pos):
        t0 = tj + 0.15 + i * passo
        k = mola(lt, t0, 0.35)
        if k > 0.05:
            cracha(d, px, py, 1.2 * k, 230 + 10 * i, entra(lt, t0, 0.3), CORES_CRACHA[i])
    kn = mola(lt, tn)
    if kn > 0.05:
        texto(d, 540, 320, "mais de 5 empregos", max(10, int(96 * kn * pulso(lt, vel=2.0, amp=0.03))))
    _txt_mola(d, 680, 1450, "começo da vida adulta", 48, INK, lt, 0.72 * dur)
    return im


# ---------------------------------------------------------------------------
# CENA 3 - a troca cai com a idade: tres fases da mesma pessoa, pilhas 5 -> 3 -> 1
# ---------------------------------------------------------------------------
def cena_3(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    chao, s = 1420, 1.2
    cy = chao - 125 * s
    fases = [(230, 5, 0, False), (540, 3, 1, False), (850, 1, 2, True)]
    for i, (x, n, gris, beng) in enumerate(fases):
        t0 = i * 0.26 * dur
        fr = _parcial(lt, 0.0, 0.4, 0.4) if i == 0 else entra(lt, t0, 0.35)
        if fr > 0:
            boneco(d, x, cy, s, 300 + 20 * i, fr, AZUL, grisalho=gris, bengala=beng, gravata=(i > 0))
            pilha_crachas(d, x, 1010, n, 1.1, 340 + 50 * i, lt, t0 if i else -1.0, passo=0.08)
    fs = entra(lt, 0.62 * dur, 0.4)
    if fs > 0:
        seta(d, 320, 610, 900, 800, seed=390, frac=fs, cor=LARANJA, w=8)
    texto(d, 540, 320, "a troca cai com a idade", int(72 * max(0.6, mola(lt, 0.0, 0.35))))
    return im


# ---------------------------------------------------------------------------
# CENA 4 - hoje ~ decadas atras: quase 3 anos no emprego
# ---------------------------------------------------------------------------
def cena_4(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    yb = 1230
    boneco(d, 280, yb, 1.6, 400, _parcial(lt, 0.0, 0.4, 0.4), AZUL)
    _txt_mola(d, 280, 1450, "hoje", 56, INK, lt, 0.05)
    tn = 0.35 * dur
    kn = mola(lt, tn)
    if kn > 0.05:
        texto(d, 540, 310, "quase 3 anos", max(10, int(120 * kn * pulso(lt, vel=2.0, amp=0.03))))
    _txt_mola(d, 540, 430, "no emprego", 58, CINZA, lt, tn + 0.25)
    fc = entra(lt, 0.0, 0.5)
    calendario_folheando(d, 280, 800, 1.0, 410, lt, max(0.35, fc))
    ta = 0.62 * dur
    ka = mola(lt, ta)
    if ka > 0.05:
        boneco(d, 800, yb, 1.6 * ka, 420, entra(lt, ta, 0.35), SEPIA, chapeu=True)
        calendario_folheando(d, 800, 800, 1.0, 430, lt + 0.3, entra(lt, ta, 0.35))
    _txt_mola(d, 800, 1450, "décadas atrás", 56, SEPIA, lt, ta + 0.2)
    _txt_mola(d, 540, 1130, "≈", 150, LARANJA, lt, ta + 0.4)
    return im


# ---------------------------------------------------------------------------
# CENA 5 - Brasil: sem comparacao entre geracoes; o que aparece e mercado
# ---------------------------------------------------------------------------
def cena_5(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 430, 300, "Brasil", int(104 * max(0.6, mola(lt, 0.0, 0.35))))
    lx = 760 + 26 * math.sin(lt * 2.4)
    lupa(d, lx, 280, 0.85, 500, _parcial(lt, 0.0, 0.4, 0.4))
    if lt > 0.25:
        texto(d, lx, 280, "?", int(80 * pulso(lt, vel=2.5, amp=0.08)), LARANJA)
    # as tres causas do mercado
    t_v, t_s, t_h = 0.36 * dur, 0.47 * dur, 0.56 * dur
    # "nao achei essa comparacao entre geracoes": jovem ? avo, sai antes da empresa entrar
    te = 0.76 * dur
    sai = 1 - entra(lt, te - 0.45, 0.35)
    if sai > 0.03:
        cyc = 1400 - 125 * 1.35
        boneco(d, 280, cyc, 1.35 * sai, 540, _parcial(lt, 0.0, 0.4, 0.4), AZUL)
        boneco(d, 800, cyc, 1.35 * sai, 545, _parcial(lt, 0.1, 0.4, 0.4), AZUL, grisalho=2, bengala=True, gravata=True)
        kq = mola(lt, 0.15 * dur) * sai
        if kq > 0.05:
            texto(d, 540, 1180, "?", max(10, int(200 * kq * pulso(lt, vel=2.5, amp=0.08))), LARANJA)
    k = mola(lt, t_v)
    if k > 0.05:
        contrato_curto(d, 220, 650, 1.3 * k, 510, entra(lt, t_v, 0.3))
        texto_multilinha(d, 220, 860, ["vaga", "curta"], 48)
    k = mola(lt, t_s)
    if k > 0.05:
        moeda(d, 510, 650, 1.1 * k, 520, entra(lt, t_s, 0.3))
        seta(d, 625, 580, 625, 720, seed=525, frac=entra(lt, t_s + 0.2, 0.3), cor=VERMELHO, w=7)
        texto_multilinha(d, 540, 860, ["salário", "baixo"], 48)
    k = mola(lt, t_h)
    if k > 0.05:
        relogio(d, 790, 650, 0.75 * k, 530, entra(lt, t_h, 0.3), t=lt * 3)
        livro(d, 940, 650, 1.0 * k, 535, entra(lt, t_h, 0.3))
        if k > 0.9:
            raio = [(872, 590), (856, 640), (880, 652), (862, 705)]
            traco(d, raio, 538, entra(lt, t_h + 0.2, 0.3), w=6, amp=1, col=VERMELHO)
        texto_multilinha(d, 865, 860, ["horário x", "escola"], 48)
    # a empresa dispensa
    fe = entra(lt, te, 0.35)
    if fe > 0:
        predio(d, 290, 1400, 1.0, 560, fe)
        fs = entra(lt, te + 0.3, 0.35)
        if fs > 0:
            seta(d, 440, 1220, 440 + 160 * fs, 1220, seed=570, frac=fs, cor=LARANJA)
        x = 760 + 70 * entra(lt, te + 0.3, max(0.5, dur - te - 0.3))
        boneco(d, x, 1400 - 125 * 1.35, 1.35, 580, fe, AZUL, fase=lt * 7 if lt > te + 0.3 else None, caixa=True)
        _txt_mola(d, 540, 1460, "decisão da empresa", 54, INK, lt, te + 0.4)
    return im


# ---------------------------------------------------------------------------
# CENA 6 - tese: esta comecando (o primeiro degrau), nao e geracao (rotulo riscado)
# ---------------------------------------------------------------------------
def cena_6(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 240, "nossa leitura", 54, CINZA)
    base = 1420
    topos = escada(d, 350, base, 5, 130, 105, 600, _parcial(lt, 0.0, 0.5, 0.4))
    # bandeira no alto, com brilho
    xb, yb = topos[-1]
    if lt > 0.35:
        im = brilho(im, xb + 30, yb - 120, 120, (50, 40, 0), 0.9 * tremer(lt, 4, 0.85, 0.15))
        d = ImageDraw.Draw(im)
        traco(d, [(xb, yb), (xb, yb - 180)], 610, entra(lt, 0.35, 0.3), w=6)
        ondula = 8 * math.sin(lt * 5)
        band = [(xb, yb - 180), (xb + 90, yb - 155 + ondula), (xb, yb - 125)]
        if lt > 0.6:
            preencher(d, band, SOL_AMARELO)
            traco(d, band, 611, 1.0, w=5, amp=1, fechado=True)
    # o jovem no primeiro passo
    sub = entra(lt, 0.3 * dur, 0.6)
    x = 230 + 185 * sub
    y_pe = base if sub < 0.6 else base - 105 * entra(lt, 0.3 * dur + 0.35, 0.25)
    boneco(d, x, y_pe - 125 * 1.5, 1.5, 620, _parcial(lt, 0.0, 0.4, 0.4), AZUL,
           fase=lt * 7 if 0.02 < sub < 0.98 else None)
    _txt_mola(d, 540, 370, "está começando", 92, AZUL, lt, 0.4 * dur)
    tg = 0.66 * dur
    fg = entra(lt, tg, 0.3)
    if fg > 0:
        etiqueta_riscada(d, 540, 560, "geração", 76, 640, fg, risco=entra(lt, 0.82 * dur, 0.35))
    return im


# ---------------------------------------------------------------------------
# CENA 7 - volta ao colega: sai de uma porta, entra em outra (a fase de trocar)
# ---------------------------------------------------------------------------
def cena_7(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    chao = 1420
    traco(d, [(40, chao), (1040, chao)], 700, 1.0, w=6)
    im = porta(d, 200, chao, 1.4, 710, 1.0, im=im)
    ab = entra(lt, 0.1 * dur, 0.6)
    im = porta(d, 880, chao, 1.4, 720, max(0.35, entra(lt, 0.0, 0.3)), aberta=ab, im=im, lt=lt)
    d = ImageDraw.Draw(im)
    x = 400 + 240 * entra(lt, 0.0, dur * 0.85)
    boneco(d, x, chao - 125 * 1.5, 1.5, 730, 1.0, AZUL, fase=lt * 6, caixa=True)
    _txt_mola(d, 540, 420, "fase de trocar", 96, AZUL, lt, 0.5 * dur)
    if lt > 0.5 * dur + 0.3:
        setas_y = 560
        f = entra(lt, 0.5 * dur + 0.3, 0.4)
        seta(d, 330, setas_y, 330 + 420 * f, setas_y, seed=740, frac=f, cor=LARANJA, w=7)
    return im
