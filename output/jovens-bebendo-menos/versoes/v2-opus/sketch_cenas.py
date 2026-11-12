"""Jovens bebendo menos: desenho v2 (Olise).

Cada cena recebe `dur` (duração real da fala + respiro) e sincroniza as entradas com a narração:
`quando(n, i, dur)` estima o instante em que a palavra i da fala da cena n é dita (peso pelo tamanho da
palavra, com folga nas pausas de pontuação). Tudo depende só de `lt`: o mesmo `lt` dá sempre o mesmo quadro.
"""
import math

from PIL import ImageDraw

from media.sketch_lib import *

# falas exatas do cenas.json (só para medir o tempo de cada palavra; não aparecem na tela)
FALAS = [
    "Dizem que a Gen Z parou de beber. Mas a queda não é só dela.",
    "Nos Estados Unidos, sessenta e dois por cento dos adultos bebiam em dois mil e vinte e três. Em dois mil e vinte e cinco, cinquenta e quatro. O menor número desde mil novecentos e trinta e nove.",
    "No mesmo período, entre adultos jovens, foi de cinquenta e nove para cinquenta por cento.",
    "A pesquisa associa isso à saúde: cinquenta e três por cento achavam que até beber com moderação faz mal. Nossa leitura: a informação parece pesar mais que o caráter de uma geração.",
    "Mas a queda aparece em todas as idades. E a bebida mudou, não sumiu: entre jovens adultos, destilado já empata com cerveja.",
    "No Brasil, as pesquisas sobre consumo pesado divergem: cada uma mede uma coisa.",
    "Se a queda aparece em todas as idades, ainda faz sentido chamar de coisa de uma geração?",
]
INICIO, RESPIRO = 0.05, 0.12


def _pesos(fala):
    ps = []
    for p in fala.split():
        w = len(p.strip(".,:?")) + 1
        if p[-1] in ".:?":
            w += 5
        elif p[-1] == ",":
            w += 3
        ps.append(w)
    return ps


# âncoras medidas nas pausas reais de falas/0N.wav (silencedetect): (índice da palavra, segundo local da cena).
# Entre duas âncoras, o tempo é distribuído pelo tamanho das palavras.
DUR_REAL = [4.07, 11.32, 5.12, 8.86, 8.20, 4.52, 4.69]
ANCORAS = [
    [(0, 0.48), (8, 2.45), (15, 3.75)],
    [(0, 0.05), (18, 5.19), (28, 8.73), (38, 11.04)],
    [(0, 0.05), (15, 5.0)],
    [(0, 0.05), (6, 1.85), (19, 5.05), (32, 8.6)],
    [(0, 0.2), (8, 3.0), (14, 5.3), (17, 6.53), (22, 8.08)],
    [(0, 0.05), (8, 3.25), (13, 4.4)],
    [(0, 0.05), (17, 4.57)],
]


def quando(n, i, dur):
    """Instante (s, tempo local da cena n) em que a palavra i (0 = primeira) começa a ser dita."""
    ps = _pesos(FALAS[n])
    anc = ANCORAS[n]
    k = 0
    while k < len(anc) - 2 and i >= anc[k + 1][0]:
        k += 1
    (i0, t0), (i1, t1) = anc[k], anc[k + 1]
    frac = sum(ps[i0:i]) / max(1, sum(ps[i0:i1]))
    return (t0 + (t1 - t0) * frac) * dur / DUR_REAL[n]


# ---------- peças à mão (originais) ----------
CERVEJA_ESC = (205, 140, 30)
DESTILADO = (196, 120, 62)
PAPEL_BRANCO = (255, 255, 255)


def _escurece(c, k=0.82):
    return tuple(int(v * k) for v in c)


def titulo(d, s, lt, t0=-1.0, y=262, tam=62, seed=900, cor_sub=LARANJA):
    """Título curto no topo com sublinhado à mão (o sublinhado se desenha depois do texto)."""
    k = mola(lt, t0, 0.4)
    if k <= 0:
        return
    texto(d, 540, y, s, max(1, int(tam * (0.82 + 0.18 * k))))
    larg = fonte(tam).getlength(s)
    f = entra(lt, t0 + 0.25, 0.5)
    n = 24
    pts = [(540 - larg / 2 + larg * i / n, y + tam * 0.66 + 5 * math.sin(i * 1.1 + 0.5)) for i in range(n + 1)]
    traco(d, pts, seed, f, w=6, amp=1.5, col=cor_sub)


def oval(d, cx, cy, rx, ry, seed, frac=1.0, col=VERMELHO, w=7, voltas=1.15, rot=-2.2):
    """Círculo de caneta em volta de um número: passa um pouco do ponto de partida, como à mão."""
    n = 64
    pts = []
    for i in range(int(n * voltas) + 1):
        a = rot + math.tau * i / n
        k = 1 + 0.03 * math.sin(i * 0.41) + 0.06 * i / n
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    traco(d, pts, seed, frac, w=w, amp=1.5, col=col)


def caixa(d, x0, y0, x1, y1, seed, frac=1.0, col=LARANJA, w=7, folga=0.0, r=60):
    """Retângulo de cantos redondos à mão (contorno de destaque); `folga` faz a caixa respirar."""
    x0, y0, x1, y1 = x0 - folga, y0 - folga, x1 + folga, y1 + folga
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        pts += [(cx + r * math.cos(a0 + math.pi / 2 * k / 6), cy + r * math.sin(a0 + math.pi / 2 * k / 6)) for k in range(7)]
    pts += [pts[0], (pts[1][0] + 14, pts[1][1] + 4)]
    traco(d, pts, seed, frac, w=w, amp=1.8, col=col)


def bezier(p0, pc, p1, n=28):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * pc[0] + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * pc[1] + t * t * p1[1]) for t in (k / n for k in range(n + 1))]


def seta_curva(d, p0, pc, p1, seed, frac=1.0, col=VERMELHO, w=8, ponta=42):
    pts = bezier(p0, pc, p1)
    traco(d, pts, seed, frac, w=w, amp=1.5, col=col)
    if frac >= 0.99:
        (xa, ya), (xb, yb) = pts[-3], pts[-1]
        a = math.atan2(yb - ya, xb - xa)
        for da in (2.55, -2.55):
            traco(d, [(xb, yb), (xb + ponta * math.cos(a + da), yb + ponta * math.sin(a + da))], seed + 5, 1.0, w=w, amp=1, col=col)


def tracejado(d, x0, y0, x1, y1, seed, frac=1.0, col=VERMELHO, w=5, passo=26, fase=0.0):
    """Linha tracejada; `fase` (0..1) faz os traços andarem (formiga)."""
    L = math.dist((x0, y0), (x1, y1))
    if L < 1 or frac <= 0:
        return
    n = int(L / passo)
    lim = L * frac
    for i in range(-1, n + 1):
        a = (i + fase) * passo * 2
        b = a + passo
        a, b = max(0, a), min(lim, b)
        if b <= a:
            continue
        ta, tb = a / L, b / L
        traco(d, [(x0 + (x1 - x0) * ta, y0 + (y1 - y0) * ta), (x0 + (x1 - x0) * tb, y0 + (y1 - y0) * tb)],
              seed + i, 1.0, w=w, amp=1, col=col)


def ret_tracejado(d, x0, y0, x1, y1, seed, fase=0.0, col=VERMELHO, w=5):
    tracejado(d, x0, y0, x1, y0, seed, 1, col, w, 18, fase)
    tracejado(d, x1, y0, x1, y1, seed + 40, 1, col, w, 18, fase)
    tracejado(d, x1, y1, x0, y1, seed + 80, 1, col, w, 18, fase)
    tracejado(d, x0, y1, x0, y0, seed + 120, 1, col, w, 18, fase)


def hachura(d, x0, y0, x1, y1, cor, seed, passo=34, w=3):
    """Hachura diagonal à mão dentro de um retângulo (textura de lápis)."""
    if x1 - x0 < 8 or y1 - y0 < 8:
        return
    c = x0 - (y1 - y0)
    k = 0
    while c < x1:
        # reta x - y = c - y0 ... segmento de 45 graus recortado no retângulo
        ax, ay = max(x0, c), y1 - (max(x0, c) - c)
        bx = min(x1, c + (y1 - y0))
        by = y1 - (bx - c)
        if ay > y1:
            ay = y1
        if by < y0:
            by = y0
        if bx - ax > 6:
            traco(d, [(ax, ay), (bx, by)], seed + k, 1.0, w=w, amp=1.2, col=cor)
        c += passo
        k += 1


def barra(d, cx, y_base, larg, h, cor, seed, hach=True):
    if h < 4:
        return
    x0, x1, y0 = cx - larg / 2, cx + larg / 2, y_base - h
    b = [(x0, y_base), (x0, y0), (x1, y0), (x1, y_base)]
    preencher(d, b, cor)
    if hach:
        hachura(d, x0 + 6, y0 + 6, x1 - 6, y_base - 6, _escurece(cor, 0.88), seed + 50)
    traco(d, b, seed, 1.0, w=6, amp=2, fechado=True)


def boneco(d, cx, cy, s=1.0, seed=0, lt=0.0, tipo="adulto", cor=INK, frac=1.0, fase=0.0, aceno=False):
    """Boneco de palito com braços que balançam e um traço de idade:
    jovem = boné; adulto = gravata; meia = óculos; idoso = coque e bengala. (cx, cy) = centro do tronco."""
    sw = 0.22 * math.sin(lt * 3.2 + fase)
    sk = lambda pts, sd, w=6: traco(d, pts, seed + sd, frac, w=w, amp=2.2 * s, col=cor)
    hx, hy, r = cx, cy - 110 * s, 36 * s
    sk(circ(hx, hy, r, 36), 1)
    sk([(cx, cy - 74 * s), (cx, cy + 40 * s)], 2)
    ombro = (cx, cy - 40 * s)

    def braco(lado, ang):
        bx, by = 50 * s * lado, 45 * s
        ca, sa = math.cos(ang), math.sin(ang)
        return (ombro[0] + bx * ca - by * sa, ombro[1] + bx * sa + by * ca)

    mao_e = braco(-1, sw)
    mao_d = braco(1, -2.1 + 0.35 * math.sin(lt * 7 + fase)) if aceno else braco(1, sw)
    sk([ombro, mao_e], 3)
    sk([ombro, mao_d], 4)
    sk([(cx, cy + 40 * s), (cx - 35 * s, cy + 125 * s)], 5)
    sk([(cx, cy + 40 * s), (cx + 35 * s, cy + 125 * s)], 6)
    if frac < 0.99:
        return
    if tipo == "jovem":
        aba = [(hx - 30 * s, hy - 14 * s), (hx + 70 * s, hy - 12 * s)]
        topo = [(hx - 34 * s, hy - 12 * s)] + [(hx + r * 1.02 * math.cos(a), hy - 12 * s + r * 0.95 * math.sin(a))
                                                for a in [math.pi + k * math.pi / 10 for k in range(11)]]
        preencher(d, topo, AZUL)
        traco(d, topo, seed + 20, 1.0, w=5, amp=1.2 * s, col=cor, fechado=True)
        traco(d, aba, seed + 21, 1.0, w=7, amp=1, col=cor)
    elif tipo == "adulto":
        g = [(cx, cy - 72 * s), (cx - 10 * s, cy - 50 * s), (cx, cy - 10 * s), (cx + 10 * s, cy - 50 * s)]
        preencher(d, g, VERMELHO)
        traco(d, g, seed + 22, 1.0, w=3, amp=0.8, col=cor, fechado=True)
    elif tipo == "meia":
        for dx in (-14, 14):
            traco(d, circ(hx + dx * s, hy - 2 * s, 11 * s, 16), seed + 23 + dx, 1.0, w=4, amp=0.8, col=cor, fechado=True)
        traco(d, [(hx - 3 * s, hy - 3 * s), (hx + 3 * s, hy - 3 * s)], seed + 25, 1.0, w=3, amp=0.5, col=cor)
    elif tipo == "idoso":
        cq = (hx + 6 * s, hy - r - 10 * s)
        d.ellipse([cq[0] - 15 * s, cq[1] - 13 * s, cq[0] + 15 * s, cq[1] + 13 * s], fill=FERRO)
        traco(d, circ(cq[0], cq[1], 14 * s, 18), seed + 26, 1.0, w=4, amp=0.8, col=cor, fechado=True)
        mx, my = mao_d
        chao = (mx + 12 * s, cy + 125 * s)
        traco(d, [(mx, my), chao], seed + 27, 1.0, w=6, amp=1, col=(120, 80, 50))
        traco(d, [(mx - 16 * s, my - 6 * s), (mx - 6 * s, my - 16 * s), (mx + 6 * s, my - 8 * s), (mx, my)],
              seed + 28, 1.0, w=6, amp=0.6, col=(120, 80, 50))


def copo_vivo(d, cx, cy, s, seed, lt, nivel, frac=1.0, bolhas=True, espuma=True):
    """Copo de cerveja com espuma e bolhas subindo (sobre o `copo` da biblioteca)."""
    copo(d, cx, cy, s, seed, frac, nivel)
    if frac < 0.99 or nivel <= 0.03:
        return
    top, bot = cy - 115 * s, cy + 115 * s
    y = bot - (bot - top) * nivel
    if bolhas:
        for k in range(7):
            ph = (lt * (0.45 + 0.07 * k) + k * 0.37) % 1.0
            by = bot - 18 * s - (bot - y - 30 * s) * ph
            if by < y + 10 * s:
                continue
            bx = cx + (k - 3) * 15 * s + 5 * s * math.sin(lt * 3 + k)
            rr = (4 + k % 3 * 2) * s
            d.ellipse([bx - rr, by - rr, bx + rr, by + rr], outline=(255, 240, 200), width=max(2, int(2 * s)))
    if espuma:
        larg = 62 * s + 18 * s * ((bot - y) / (bot - top))
        for k in range(6):
            fx = cx - larg + (k + 0.5) * (2 * larg / 6)
            rr = (17 + 4 * math.sin(lt * 2.5 + k)) * s * 0.75
            d.ellipse([fx - rr, y - rr * 1.1, fx + rr, y + rr * 0.5], fill=PAPEL_BRANCO)
            traco(d, circ(fx, y - rr * 0.3, rr, 14)[8:14] + circ(fx, y - rr * 0.3, rr, 14)[:1], seed + 60 + k, 1.0, w=3, amp=0.6)


def lampada(d, cx, cy, s, seed, frac=1.0, luz=0.0, lt=0.0):
    """Lâmpada desenhada; `luz` 0..1 acende o bulbo e solta raios pulsando."""
    r = 56 * s
    if frac >= 0.99:
        cor = tuple(int(PAPEL_BRANCO[i] + (SOL_AMARELO[i] - PAPEL_BRANCO[i]) * luz) for i in range(3))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cor)
        preencher(d, [(cx - 26 * s, cy + r * 0.8), (cx + 26 * s, cy + r * 0.8), (cx + 22 * s, cy + r + 46 * s), (cx - 22 * s, cy + r + 46 * s)], FERRO)
    traco(d, circ(cx, cy, r, 32)[:27] + [(cx - 26 * s, cy + r * 0.8)], seed, frac, w=6, amp=1.5 * s)
    traco(d, [(cx - 26 * s, cy + r * 0.8), (cx - 22 * s, cy + r + 46 * s), (cx + 22 * s, cy + r + 46 * s), (cx + 26 * s, cy + r * 0.8)],
          seed + 1, frac, w=6, amp=1.2)
    if frac >= 0.99:
        for k in range(3):
            yy = cy + r + 6 * s + k * 13 * s
            traco(d, [(cx - 22 * s, yy), (cx + 22 * s, yy)], seed + 2 + k, 1.0, w=3, amp=0.6)
        traco(d, [(cx - 14 * s, cy + r * 0.75), (cx - 10 * s, cy - 6 * s), (cx, cy + 6 * s), (cx + 10 * s, cy - 6 * s), (cx + 14 * s, cy + r * 0.75)],
              seed + 6, 1.0, w=3, amp=0.8, col=(120, 90, 40))
    if luz > 0.05:
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.48
            r0 = r + 18 * s + 6 * s * math.sin(lt * 6 + k)
            r1 = r0 + 36 * s * luz
            traco(d, [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                  seed + 30 + k, 1.0, w=6, amp=1, col=(215, 150, 20))


def alerta(d, cx, cy, s, seed, frac=1.0):
    tri = [(cx, cy - 70 * s), (cx + 66 * s, cy + 48 * s), (cx - 66 * s, cy + 48 * s)]
    if frac >= 0.99:
        preencher(d, tri, SOL_AMARELO)
    traco(d, tri, seed, frac, w=6, amp=1.5, col=VERMELHO, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy + 8 * s, "!", max(1, int(76 * s)), VERMELHO)


def prancheta(d, cx, cy, s, seed, frac=1.0):
    """Prancheta de pesquisa (folha com prendedor). Altura ~ 320*s."""
    x0, x1, y0, y1 = cx - 110 * s, cx + 110 * s, cy - 150 * s, cy + 160 * s
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, (222, 196, 150))
        preencher(d, [(x0 + 16 * s, y0 + 26 * s), (x1 - 16 * s, y0 + 26 * s), (x1 - 16 * s, y1 - 16 * s), (x0 + 16 * s, y1 - 16 * s)], PAPEL_BRANCO)
    traco(d, c, seed, frac, w=6, amp=1.8 * s, fechado=True)
    clip = [(cx - 46 * s, y0 - 18 * s), (cx + 46 * s, y0 - 18 * s), (cx + 46 * s, y0 + 22 * s), (cx - 46 * s, y0 + 22 * s)]
    if frac >= 0.99:
        preencher(d, clip, FERRO)
        traco(d, clip, seed + 1, 1.0, w=5, amp=1, fechado=True)
        for k in range(2):
            yy = y0 + 58 * s + k * 26 * s
            traco(d, [(x0 + 34 * s, yy), (x1 - 34 * s - k * 40 * s, yy)], seed + 2 + k, 1.0, w=4, amp=1, col=FERRO)


# ---------- cenas ----------
def cena_0(lt, dur):
    """Gancho: o copo já riscado no quadro 0, esvaziando; na virada ("Mas...") a Gen Z ganha companhia."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_mas = quando(0, 8, dur)
    titulo(d, "Gen Z parou de beber?", lt, t0=-1.0, tam=70, seed=901)

    # copo grande esvaziando, com X pulsando (já desenhado no quadro 0)
    nivel = max(0.12, 0.82 - 0.55 * lt / max(dur, 1))
    gx, gy = 540, 625
    im = brilho(im, gx, gy, 300, (40, 30, 0), 0.5 + 0.2 * math.sin(lt * 5))
    d = ImageDraw.Draw(im)
    copo_vivo(d, gx, gy, 2.05, 3, lt, nivel)
    p = pulso(lt, 3.0, 0.05)
    cruz(d, gx, gy + 10, 2.45 * p, 8, 1.0)

    # seta descendo do copo para as pessoas (balança)
    yo = 6 * math.sin(lt * 5)
    seta(d, 540, 885 + yo, 540, 955 + yo, 20, 1.0, VERMELHO, 9)

    # a Gen Z (boné), no centro, já no quadro 0
    bob = lambda i: 7 * math.sin(lt * 4 + i * 1.7)
    boneco(d, 540, 1250 + bob(0), 1.45, 30, lt, "jovem", LARANJA, aceno=lt < t_mas)
    # "não é só dela": outros adultos entram
    for i, (x, tipo, sd) in enumerate([(285, "adulto", 50), (795, "idoso", 70)]):
        m = mola(lt, t_mas + 0.15 + i * 0.22)
        if m > 0:
            boneco(d, x, 1250 + bob(i + 1) + (1 - m) * 60, 1.4 * m, sd, lt, tipo, fase=i * 2.1)
    f = entra(lt, t_mas + 0.75, 0.6)
    if f > 0:
        oval(d, 540, 1235, 405 * pulso(lt, 2.5, 0.015), 235, 99, f, VERMELHO, 7)
    return im


def cena_1(lt, dur):
    """62% (2023) -> 58% (2024) -> 54% (2025) -> o mais baixo da série: calendário voltando no tempo."""
    im = papel()
    d = ImageDraw.Draw(im)
    t62, t2023 = quando(1, 3, dur), quando(1, 12, dur)
    t_em25, t54 = quando(1, 18, dur), quando(1, 25, dur)
    t_menor, t_desde = quando(1, 29, dur), quando(1, 31, dur)

    titulo(d, "Adultos nos EUA que bebem", lt, t0=-0.2, tam=60, seed=902, cor_sub=AZUL)
    yb, larg, amax, esc = 1385, 220, 790, 70
    xs = [250, 540, 830]
    dados = [(62, "62%", "2023", AZUL, t62 - 0.5), (58, "58%", "2024", GELO, t_em25 - 0.1), (54, "54%", "2025", LARANJA, t54 - 0.45)]
    traco(d, [(140, yb), (940, yb)], 5, entra(lt, 0.0, 0.4), w=7)
    for k, (v, txt, ano, cor, t0) in enumerate(dados):
        x = xs[k]
        f = entra(lt, t0, 0.6)
        if f <= 0:
            # vaga ainda vazia: caixa tracejada com "?" pulsando
            if lt > 0.15:
                ret_tracejado(d, x - larg / 2 + 20, yb - 150, x + larg / 2 - 20, yb - 6, 300 + 10 * k, (lt * 0.8) % 1, FERRO, 4)
                texto(d, x, yb - 78, "?", int(80 * pulso(lt + k, 3, 0.08)), FERRO)
            continue
        h = amax * v / esc * f * (1 + 0.004 * math.sin(lt * 4 + k))
        barra(d, x, yb, larg, h, cor, 10 + 7 * k)
        m = mola(lt, t0 + 0.45)
        if m > 0:
            destaque = 1.0 + (0.08 * math.sin(lt * 6) if k == 2 and lt > t_menor else 0)
            texto(d, x, yb - h - 48, txt, max(1, int(70 * m * destaque)))
        texto(d, x, yb + 52, ano, 44)

    # "o menor número": círculo no 54% e linha tracejada do piso atravessando as outras barras
    h54 = amax * 54 / esc
    f = entra(lt, t_menor, 0.6)
    if f > 0:
        oval(d, xs[2], yb - h54 - 48, 128 * pulso(lt, 3, 0.03), 72, 77, f, VERMELHO, 8)
        tracejado(d, 150, yb - h54, xs[2] - larg / 2, yb - h54, 120, f, VERMELHO, 6, 24, (lt * 1.2) % 1)
    # "desde 1939": calendário perdendo folhas para trás (sem texto novo)
    m = mola(lt, t_desde)
    if m > 0:
        cx, cy, s = 830, 455, 0.92 * m
        for j in range(3):
            ph = ((lt - t_desde) * 1.4 + j / 3) % 1.0
            if lt - t_desde < j / 3 / 1.4:
                continue
            px = cx - 60 - 430 * ph
            py = cy - 10 - 30 * math.sin(ph * math.pi) + 30 * ph
            a = -ph * 2.2
            w2, h2 = 80 * (1 - 0.5 * ph), 70 * (1 - 0.5 * ph)
            pts = [(px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a))
                   for dx, dy in [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]]
            preencher(d, pts, PAPEL_BRANCO)
            traco(d, pts, 400 + j, 1.0, w=4, amp=1, fechado=True)
        calendario(d, cx, cy, s, 410, 1.0)
        seta_curva(d, (cx - 115, cy + 95), (cx - 330, cy + 150), (cx - 500, cy + 70), 420,
                   entra(lt, t_desde + 0.3, 0.5), VERMELHO, 7, 34)
    return im


def cena_2(lt, dur):
    """Adultos jovens: a barra sobe até 59% e cai para 50%; fica a marca tracejada do que sumiu."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_jov, t59 = quando(2, 5, dur), quando(2, 8, dur)
    t50 = quando(2, 12, dur)
    titulo(d, "Adultos jovens: 59% → 50%", lt, t0=-0.2, tam=60, seed=903)

    yb, larg, amax, esc = 1120, 270, 700, 65
    x1, x2 = 330, 750
    traco(d, [(150, yb), (930, yb)], 5, entra(lt, 0.0, 0.4), w=7)
    h59, h50 = amax * 59 / esc, amax * 50 / esc
    for k, x in enumerate((x1, x2)):
        if lt > 0.1 and (k == 0 and lt < t59 - 0.35 or k == 1 and lt < t50 - 0.55):
            ret_tracejado(d, x - larg / 2 + 20, yb - 170, x + larg / 2 - 20, yb - 6, 300 + 10 * k, (lt * 0.8) % 1, FERRO, 4)
            texto(d, x, yb - 88, "?", int(90 * pulso(lt + k, 3, 0.08)), FERRO)
    f1 = entra(lt, t59 - 0.35, 0.6)
    if f1 > 0:
        barra(d, x1, yb, larg, h59 * f1, AZUL, 21)
        m = mola(lt, t59)
        if m > 0:
            texto(d, x1, yb - h59 * f1 + 70, "59%", max(1, int(76 * m)))
    # segunda barra: sobe junto e depois despenca para 50%
    if lt > t50 - 0.55:
        sobe = entra(lt, t50 - 0.55, 0.3)
        cai = entra(lt, t50 - 0.1, 0.35)
        quique = 10 * math.sin((lt - t50 - 0.25) * 18) * math.exp(-(lt - t50 - 0.25) * 6) if lt > t50 + 0.25 else 0
        h = h59 * sobe - (h59 - h50) * cai + quique
        barra(d, x2, yb, larg, h, LARANJA, 28)
        if cai > 0.95:
            ret_tracejado(d, x2 - larg / 2, yb - h59, x2 + larg / 2, yb - h50 - 8, 500, (lt * 0.9) % 1, VERMELHO, 5)
            m = mola(lt, t50 + 0.2)
            texto(d, x2, yb - h50 + 70, "50%", max(1, int(76 * m)))
            fs = entra(lt, t50 + 0.3, 0.45)
            yo = 5 * math.sin(lt * 5)
            seta_curva(d, (x1 + larg / 2 + 10, yb - h59 - 40 + yo), (540, yb - h59 - 130 + yo),
                       (x2 - 20, yb - h59 - 20 + yo), 510, fs, VERMELHO, 9)
            fd = entra(lt, t50 + 0.6, 0.4)
            if fd > 0:
                seta(d, x2, yb - h59 + 16, x2, yb - h50 - 26, 520, fd, VERMELHO, 9)

    # os adultos jovens, embaixo do gráfico
    for i, x in enumerate([255, 435, 615, 795]):
        m = mola(lt, 0.0 + i * 0.12)
        if m > 0:
            boneco(d, x + 30, 1320 + 6 * math.sin(lt * 4 + i * 1.4) + (1 - m) * 40, 0.86 * m, 600 + 20 * i, lt,
                   "jovem", INK, fase=i * 1.3)
    return im


def cena_3(lt, dur):
    """53% acham que moderação faz mal; depois a balança: a informação pesa mais que a geração."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_saude, t53 = quando(3, 5, dur), quando(3, 6, dur)
    t_mod, t_nossa = quando(3, 16, dur), quando(3, 19, dur)
    t_info, t_pesar = quando(3, 22, dur), quando(3, 24, dur)
    t_ger = quando(3, 28, dur)

    titulo(d, "53%: moderação faz mal", lt, t0=-0.2, tam=62, seed=904)

    # linha de cima: coração (saúde) | 53% | copo com alerta
    m = mola(lt, 0.1)
    if m > 0:
        coracao(d, 225, 470, 0.95 * m * pulso(lt, 2.4, 0.08), 31)
    m = mola(lt, t53)
    if m > 0:
        texto(d, 540, 470, "53%", max(1, int(170 * m)))
        oval(d, 540, 472, 190, 105, 32, entra(lt, t53 + 0.5, 0.5), VERMELHO, 7)
    m = mola(lt, t_mod - 0.2)
    if m > 0:
        copo_vivo(d, 870, 470, 0.92 * m, 33, lt, 0.45, bolhas=m > 0.99)
        if m >= 1:
            alerta(d, 930, 545, 0.75 * pulso(lt, 4, 0.08), 34, entra(lt, t_mod + 0.2, 0.3))
    # barra horizontal: 53 de 100
    fb = entra(lt, 0.3, 0.5)
    if fb > 0:
        x0, x1, y0, y1 = 175, 905, 640, 712
        ff = entra(lt, t53 + 0.1, 0.9)
        xf = x0 + (x1 - x0) * 0.53 * ff
        if ff > 0.01:
            preencher(d, [(x0 + 4, y0 + 4), (xf, y0 + 4), (xf, y1 - 4), (x0 + 4, y1 - 4)], LARANJA)
            hachura(d, x0 + 8, y0 + 6, xf - 4, y1 - 6, _escurece(LARANJA, 0.88), 35, 26)
        traco(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 36, fb, w=6, fechado=True)
        if ff >= 1:
            traco(d, [(xf, y0 - 14), (xf, y1 + 14)], 37, 1.0, w=6, col=VERMELHO)

    # a balança (Nossa leitura)
    fz = entra(lt, 0.4, 1.2)  # a balança vazia já está montada; os pesos caem em "Nossa leitura"
    if fz > 0:
        px, py, L, corda = 540, 1020, 340, 280
        # antes: o lado da geração parece mais pesado; em "pesar mais", a informação desce
        x = _clamp((lt - t_pesar) / 0.9) if lt > t_pesar else 0.0
        cheio = entra(lt, t_nossa + 0.5, 0.6)
        th = -0.15 * cheio + 0.37 * (1 - (1 - x) ** 3)
        if lt > t_pesar:
            th += 0.06 * math.exp(-(lt - t_pesar) * 3) * math.sin((lt - t_pesar) * 9)
        th += 0.015 * math.sin(lt * 2.2)
        # base e poste
        base = [(450, 1465), (630, 1465), (590, 1410), (490, 1410)]
        if fz >= 1:
            preencher(d, base, FERRO)
        traco(d, base, 40, fz, w=6, fechado=True)
        traco(d, [(px, 1410), (px, py)], 41, fz, w=8)
        if fz >= 1:
            ex_e = (px - L * math.cos(th), py + L * math.sin(th))
            ex_d = (px + L * math.cos(th), py - L * math.sin(th))
            traco(d, [ex_e, ex_d], 42, 1.0, w=9)
            d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=INK)
            for lado, (ex, ey) in ((0, ex_e), (1, ex_d)):
                pan_y = ey + corda
                bowl = [(ex - 110 + 220 * k / 12, pan_y + 38 * math.sin(math.pi * k / 12)) for k in range(13)]
                preencher(d, bowl, GELO)
                traco(d, bowl + [bowl[0]], 43 + lado, 1.0, w=6)
                traco(d, [(ex, ey), (ex - 108, pan_y)], 45 + lado, 1.0, w=3, amp=1, col=FERRO)
                traco(d, [(ex, ey), (ex + 108, pan_y)], 47 + lado, 1.0, w=3, amp=1, col=FERRO)
                if lado == 0:
                    luz = entra(lt, t_info, 0.5)
                    sl = 1.45 * mola(lt, t_nossa + 0.3)
                    lampada(d, ex, pan_y - 105 * sl, sl, 50, 1.0, luz * tremer(lt, 9, 0.9, 0.1), lt)
                else:
                    for j, dx in enumerate((-50, 50)):
                        mj = mola(lt, t_nossa + 0.5 + j * 0.15)
                        if mj > 0:
                            boneco(d, ex + dx, pan_y - 125 * 0.74 * mj, 0.74 * mj, 60 + 20 * j, lt,
                                   ("jovem", "adulto")[j], INK, fase=j * 1.9)
            if lt > t_ger:
                fo = entra(lt, t_ger, 0.5)
                oval(d, ex_d[0], ex_d[1] + corda - 105, 150, 165, 55, fo, LARANJA, 6, 1.1)
    return im


def cena_4(lt, dur):
    """Todas as idades descem um degrau; depois a bebida troca: destilado = cerveja."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_todas = quando(4, 5, dur)
    t_beb, t_nao = quando(4, 10, dur), quando(4, 12, dur)
    t_dest, t_emp = quando(4, 17, dur), quando(4, 19, dur)
    t_cerv = quando(4, 21, dur)

    titulo(d, "Queda em todas as idades", lt, t0=-0.2, tam=62, seed=905)
    tipos = [("jovem", 1.3), ("adulto", 1.36), ("meia", 1.36), ("adulto", 1.33), ("idoso", 1.3)]
    xs = [215, 380, 545, 710, 875]
    for i, ((tipo, s), x) in enumerate(zip(tipos, xs)):
        m = mola(lt, 0.0 + i * 0.12)
        if m <= 0:
            continue
        cai = entra(lt, t_todas - 0.15 + i * 0.13, 0.45)
        topo = 820 + 62 * cai
        pedestal = [(x - 62, 905), (x - 62, topo), (x + 62, topo), (x + 62, 905)]
        preencher(d, pedestal, GELO)
        traco(d, pedestal, 700 + i, 1.0, w=5, amp=1.5, fechado=True)
        if cai > 0.6:
            yo = 4 * math.sin(lt * 6 + i)
            fa = entra(lt, t_todas + 0.15 + i * 0.13, 0.3)
            if fa > 0:
                traco(d, [(x - 44, 770 + yo), (x - 44, 830 + yo)], 730 + i, fa, w=6, col=VERMELHO)
                if fa >= 0.99:
                    traco(d, [(x - 60, 812 + yo), (x - 44, 834 + yo), (x - 28, 812 + yo)], 740 + i, 1.0, w=6, col=VERMELHO)
        boneco(d, x + 8, topo - 125 * s * m + 4 * math.sin(lt * 3.5 + i * 1.3), s * m, 750 + 20 * i, lt, tipo, fase=i * 1.2)
    traco(d, [(150, 905), (935, 905)], 760, entra(lt, 0.0, 0.4), w=7)

    # embaixo: a bebida mudou, não sumiu
    yy = 1225
    m = mola(lt, t_beb - 0.15)
    xc = 815
    if m > 0:
        copo_vivo(d, xc, yy + 15 + 6 * math.sin(lt * 3), 1.5 * m, 800, lt, 0.68 + 0.03 * math.sin(lt * 4))
    fr = entra(lt, t_nao - 0.1, 0.5)
    if fr > 0 and lt < t_emp:
        # setas de troca girando em volta do centro
        ang = lt * 0.9
        R = 140 + 6 * math.sin(lt * 3)
        for k in range(2):
            a0 = ang + k * math.pi
            arco = [(540 + R * math.cos(a0 + 0.2 + 2.3 * j / 14), yy + R * math.sin(a0 + 0.2 + 2.3 * j / 14)) for j in range(15)]
            traco(d, arco, 810 + k, fr, w=7, amp=1, col=AZUL)
            if fr >= 0.99:
                (xa, ya), (xb, yb2) = arco[-3], arco[-1]
                a = math.atan2(yb2 - ya, xb - xa)
                for da in (2.5, -2.5):
                    traco(d, [(xb, yb2), (xb + 34 * math.cos(a + da), yb2 + 34 * math.sin(a + da))], 815 + k, 1.0, w=7, amp=1, col=AZUL)
    m = mola(lt, t_dest - 0.1)
    if m > 0:
        garrafa(d, 265, yy + 5 * math.sin(lt * 3 + 1.6), 1.32 * m, 820, 1.0, DESTILADO)
    fe = entra(lt, t_emp, 0.4)
    if fe > 0:
        p = pulso(lt, 3, 0.06)
        traco(d, [(540 - 52 * p, yy - 22), (540 + 52 * p, yy - 22)], 830, fe, w=13, amp=1.5)
        traco(d, [(540 - 52 * p, yy + 22), (540 + 52 * p, yy + 22)], 831, entra(lt, t_emp + 0.15, 0.4), w=13, amp=1.5)
    if lt > t_cerv - 0.1:
        caixa(d, 165, 990, 960, 1462, 840, entra(lt, t_cerv - 0.1, 0.7), LARANJA, 7, 3 * math.sin(lt * 4))
    return im


def cena_5(lt, dur):
    """Brasil: cada pesquisa mede uma coisa, e os gráficos não batem."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_pesq, t_div = quando(5, 3, dur), quando(5, 7, dur)
    t_cada = quando(5, 8, dur)
    titulo(d, "Brasil: sem número único", lt, t0=-0.2, tam=62, seed=906, cor_sub=VERDE)

    # mancha verde genérica (não é o contorno do país), respirando
    rel = [(-50, -330), (120, -300), (300, -220), (350, -80), (250, 60), (180, 200), (60, 330), (-60, 300),
           (-130, 150), (-250, 60), (-330, -60), (-250, -200), (-120, -230)]
    k = mola(lt, 0.0, 0.5) * pulso(lt, 1.6, 0.02)
    cx, cy, e = 540, 600, 0.78
    pts = [(cx + x * e * k, cy + y * e * k) for x, y in rel]
    if k > 0.05:
        preencher(d, pts, VERDE)
        traco(d, pts, 7, entra(lt, 0.0, 0.6), w=7, fechado=True)
        # alvo pulsando no meio
        rr = 22 + 8 * math.sin(lt * 5)
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=PAPEL_BRANCO)
        traco(d, circ(cx, cy, rr, 20), 8, 1.0, w=4, amp=1, col=PAPEL_BRANCO, fechado=True)

    # três pranchetas, cada uma com um gráfico diferente
    xs = [235, 540, 845]
    yy = 1255
    alturas = [[0.85, 0.35, 0.55], [0.25, 0.5, 0.9], [0.6, 0.95, 0.3]]
    cores = [AZUL, LARANJA, SOL_AMARELO]
    for i, x in enumerate(xs):
        m = mola(lt, t_pesq - 0.2 + i * 0.18)
        if m <= 0:
            continue
        y = yy + 5 * math.sin(lt * 2.6 + i * 2)
        prancheta(d, x, y, 0.95 * m, 900 + 10 * i)
        if m < 1:
            continue
        for j, a in enumerate(alturas[i]):
            g = entra(lt, t_cada + i * 0.3 + j * 0.08, 0.5)
            h = 140 * a * g * (1 + 0.05 * math.sin(lt * 4 + i + j))
            bx = x - 55 + j * 55
            barra(d, bx, y + 128, 38, h, cores[i], 930 + 10 * i + j, hach=False)
        traco(d, [(x - 85, y + 128), (x + 85, y + 128)], 960 + i, 1.0, w=4, amp=1)
    # as setas divergem da mancha para cada pesquisa
    for i, x in enumerate(xs):
        f = entra(lt, t_div - 0.1 + i * 0.12, 0.45)
        if f > 0:
            yo = 5 * math.sin(lt * 4 + i)
            seta_curva(d, (540 + (i - 1) * 40, 905), (540 + (i - 1) * 160, 960), (x, 1060 + yo), 970 + 10 * i, f, INK, 7, 34)
    # sinais de diferente entre as pranchetas
    for i, x in enumerate((388, 692)):
        fe = entra(lt, t_cada + 0.6 + i * 0.25, 0.4)
        if fe > 0:
            p = pulso(lt + i, 3, 0.08)
            traco(d, [(x - 26 * p, yy - 14), (x + 26 * p, yy - 14)], 990 + i, fe, w=8, col=VERMELHO)
            traco(d, [(x - 26 * p, yy + 14), (x + 26 * p, yy + 14)], 992 + i, fe, w=8, col=VERMELHO)
            traco(d, [(x + 16, yy - 40), (x - 16, yy + 40)], 994 + i, fe, w=8, col=VERMELHO)
    # lupa passeando sobre as pranchetas
    if lt > t_cada:
        u = (lt - t_cada) * 0.7
        lx = 540 + 300 * math.sin(u * math.pi)
        ly = 1225 + 30 * math.sin(u * 7)
        lupa(d, lx - 50, ly - 30, 0.85 * mola(lt, t_cada), 999)
    return im


def cena_6(lt, dur):
    """Pergunta de volta: todas as idades ou uma geração? O balão fica no ar, sem resposta."""
    im = papel()
    d = ImageDraw.Draw(im)
    t_todas, t_ainda = quando(6, 5, dur), quando(6, 8, dur)
    t_ger = quando(6, 13, dur)
    titulo(d, "Coisa de uma geração?", lt, t0=-0.1, tam=70, seed=907)

    # balão com interrogação, pulsando e flutuando
    m = mola(lt, 0.05)
    if m > 0:
        p = pulso(lt, 2.5, 0.05) * m
        yb = 545 + 10 * math.sin(lt * 2.4)
        balao(d, 560, yb, 400 * p, 290 * p, ["?"], 5, 1.0, tam=max(1, int(230 * p)), cauda="esq")

    tipos = [("jovem", 1.3), ("adulto", 1.36), ("meia", 1.36), ("adulto", 1.32), ("idoso", 1.3)]
    xs = [205, 375, 545, 715, 880]
    for i, ((tipo, s), x) in enumerate(zip(tipos, xs)):
        mi = mola(lt, 0.0 + i * 0.1)
        if mi > 0:
            boneco(d, x, 1010 + 5 * math.sin(lt * 3.5 + i * 1.4) - (1 - mi) * 30, s * mi, 1100 + 20 * i, lt, tipo,
                   LARANJA if i == 0 else INK, fase=i * 1.1, aceno=(i == 2 and lt > t_ainda))
    # chave ligando todas as idades + seta de queda
    fc = entra(lt, t_todas - 0.1, 0.6)
    if fc > 0:
        yk = 1215
        pts = bezier((140, yk - 30), (150, yk + 10), (330, yk + 10)) + bezier((330, yk + 10), (520, yk + 10), (540, yk + 50))[1:] \
            + bezier((540, yk + 50), (560, yk + 10), (750, yk + 10))[1:] + bezier((750, yk + 10), (930, yk + 10), (940, yk - 30))[1:]
        traco(d, pts, 1200, fc, w=7, amp=1.5, col=INK)
        if fc >= 0.99:
            yo = 8 * math.sin(lt * 5)
            seta(d, 540, 1290 + yo, 540, 1440 + yo, 1210, entra(lt, t_todas + 0.4, 0.4), VERMELHO, 11)
    # "uma geração": contorno tracejado só em volta do mais jovem, pulsando
    if lt > t_ger - 0.1:
        k = mola(lt, t_ger - 0.1)
        rx, ry = 105 * k * pulso(lt, 3, 0.04), 215 * k * pulso(lt, 3, 0.04)
        n = 40
        for j in range(0, n, 2):
            a0 = math.tau * (j + lt * 1.5) / n
            a1 = math.tau * (j + 1 + lt * 1.5) / n
            traco(d, [(205 + rx * math.cos(a0), 985 + ry * math.sin(a0)), (205 + rx * math.cos(a1), 985 + ry * math.sin(a1))],
                  1300 + j, 1.0, w=6, amp=1, col=LARANJA)
    return im


def _clamp(x):
    return max(0.0, min(1.0, x))
