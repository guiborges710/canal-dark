"""Componentes NOVOS do video fim-dos-terceiros-lugares (proposta, AGUARDANDO APROVACAO DO GUILHERME).

Cada funcao desenha UM componente, parametrizado por posicao, escala e `frac`
(progresso do traco). Importa a biblioteca-base do canal; mesmo estilo e paleta.
Os icones basicos (pessoa, casa, copo, moeda, celular, relogio, seta, circ, traco,
preencher...) e as cores ja vivem em media/sketch_lib.py e NAO sao duplicados aqui.
Reuso do catalogo aprovado: `balao_fala` (media/sketch_componentes.py).

Cada componente tem uma funcao companheira `*_box(cx, cy, s, ...)` que devolve a
caixa ocupada como (x, y, w, h) com ancora no canto superior esquerdo. O Olise usa
as caixas para posicionar sem sobrepor boneco nem texto.

Convencao de cor deste video:
  - AZUL        = convivio / tempo com amigos / telas (tela fria)
  - LARANJA     = custo, gasto, hipotese (leitura nossa), destaque "jovens"
  - VERMELHO    = queda (seta das saidas -7,1%)
  - FERRO tracejado = o lugar que sumiu / o que nao existe (sem medida)
  - MADEIRA     = mobilia do terceiro lugar (mesa, cadeira, banco)

NAO promover para media/sketch_componentes.py nem catalogo.md sem aprovacao do Guilherme.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *

MADEIRA = (205, 170, 125)
CAFE = (120, 80, 50)
COURO = (170, 120, 80)
BRANCO = (255, 255, 255)


def _clareia(cor, k=0.55):
    """Mistura a cor com branco (k=0 cor cheia, k=1 branco)."""
    return tuple(round(c + (255 - c) * k) for c in cor)


def _lim(x):
    return max(0.0, min(1.0, x))


def _ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def tracejado(d, pts, seed, frac=1.0, w=5, col=FERRO, passo=28, vao=16, fechado=False, amp=1.5):
    """Linha tracejada a mao (o que sumiu / o que nao existe). Mesmo tremido estavel por seed."""
    if frac <= 0 or len(pts) < 2:
        return
    pts = list(pts) + ([pts[0]] if fechado else [])
    segs = list(zip(pts[:-1], pts[1:]))
    total = sum(math.dist(a, b) for a, b in segs)
    limite = total * min(1.0, frac)

    def ponto(l):
        acc = 0.0
        for a, b in segs:
            L = math.dist(a, b)
            if acc + L >= l and L > 0:
                t = (l - acc) / L
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            acc += L
        return pts[-1]

    pos, k = 0.0, 0
    while pos < limite:
        fim = min(pos + passo, limite)
        n = max(2, int((fim - pos) / 8))
        p = [ponto(pos + (fim - pos) * i / (n - 1)) for i in range(n)]
        traco(d, p, seed + k, 1.0, w=w, amp=amp, col=col)
        pos += passo + vao
        k += 1


# ---------------------------------------------------------------------------
# 1. Xicara de cafe (com vapor que ondula com t)
# ---------------------------------------------------------------------------
def xicara_cafe(d, cx, cy, s=1.0, seed=0, frac=1.0, vapor=True, t=0.0):
    """Xicara no pires. (cx, cy) = centro do corpo da xicara. `vapor` = cafe quente (ondula com t)."""
    corpo = [(cx - 60 * s, cy - 50 * s), (cx + 60 * s, cy - 50 * s), (cx + 45 * s, cy + 50 * s), (cx - 45 * s, cy + 50 * s)]
    if frac >= 0.99:
        preencher(d, corpo, BRANCO)
        preencher(d, [(cx - 57 * s, cy - 47 * s), (cx + 57 * s, cy - 47 * s), (cx + 54 * s, cy - 34 * s), (cx - 54 * s, cy - 34 * s)], CAFE)
    traco(d, corpo, seed, frac, w=6, amp=1.5 * s, fechado=True)
    # asa
    asa = [(cx + 52 * s + 22 * s * math.cos(a), cy - 8 * s + 24 * s * math.sin(a))
           for a in [-math.pi / 2 + k * math.pi / 12 for k in range(13)]]
    traco(d, asa, seed + 1, frac, w=6, amp=1.2 * s)
    # pires
    traco(d, [(cx - 92 * s, cy + 50 * s), (cx - 62 * s, cy + 62 * s), (cx + 62 * s, cy + 62 * s), (cx + 92 * s, cy + 50 * s)],
          seed + 2, frac, w=6, amp=1.2 * s)
    if vapor and frac >= 0.99:
        for k, dx in enumerate((-26, 0, 26)):
            pts = []
            for i in range(9):
                yy = cy - 62 * s - i * 11 * s
                xx = cx + dx * s + 9 * s * math.sin(i * 0.9 + t * 3 + k * 1.7)
                pts.append((xx, yy))
            traco(d, pts, seed + 10 + k, 1.0, w=4, amp=0.8, col=FERRO)


def xicara_cafe_box(cx, cy, s=1.0, vapor=True):
    top = cy - (152 * s if vapor else 54 * s)
    return (cx - 94 * s, top, 188 * s, cy + 66 * s - top)


# ---------------------------------------------------------------------------
# 2. Cadeira de bistro (vista de lado) e 3. Mesa de cafe com cadeiras
# ---------------------------------------------------------------------------
def cadeira_cafe(d, cx, cy, s=1.0, seed=0, frac=1.0, lado="esq", cor=INK):
    """Cadeira de bistro de lado. (cx, cy) = centro do assento. Encosto do lado `lado` (fora da mesa)."""
    sg = -1 if lado == "esq" else 1
    xe = cx + sg * 60 * s
    traco(d, [(cx - 62 * s, cy), (cx + 62 * s, cy)], seed, frac, w=8, amp=1.5 * s, col=cor)          # assento
    traco(d, [(xe, cy), (xe + sg * 10 * s, cy - 150 * s)], seed + 1, frac, w=7, amp=1.5 * s, col=cor)  # encosto
    traco(d, [(xe + sg * 10 * s, cy - 150 * s), (xe - sg * 26 * s, cy - 146 * s)], seed + 2, frac, w=7, amp=1.2 * s, col=cor)
    traco(d, [(xe + sg * 5 * s, cy - 75 * s), (xe - sg * 22 * s, cy - 73 * s)], seed + 3, frac, w=5, amp=1.2 * s, col=cor)
    traco(d, [(cx - 54 * s, cy), (cx - 66 * s, cy + 150 * s)], seed + 4, frac, w=6, amp=1.5 * s, col=cor)  # pernas
    traco(d, [(cx + 54 * s, cy), (cx + 66 * s, cy + 150 * s)], seed + 5, frac, w=6, amp=1.5 * s, col=cor)


def cadeira_cafe_box(cx, cy, s=1.0):
    return (cx - 74 * s, cy - 156 * s, 148 * s, 310 * s)


def mesa_cafe(d, cx, cy, s=1.0, seed=0, frac=1.0, cadeiras=2, xicaras=1, vapor=False, t=0.0):
    """Mesa redonda de cafe (vista de lado) com cadeiras vazias. (cx, cy) = topo do tampo.
    `cadeiras` 0..2 (esq, dir); `xicaras` 0..2 em cima da mesa; `vapor` = cafe quente."""
    tampo = _ret(cx - 150 * s, cy, cx + 150 * s, cy + 22 * s)
    if frac >= 0.99:
        preencher(d, tampo, MADEIRA)
    traco(d, tampo, seed, frac, w=6, amp=1.5 * s, fechado=True)
    traco(d, [(cx, cy + 22 * s), (cx, cy + 250 * s)], seed + 1, frac, w=9, amp=1.5 * s)
    traco(d, [(cx - 78 * s, cy + 250 * s), (cx + 78 * s, cy + 250 * s)], seed + 2, frac, w=8, amp=1.5 * s)
    if cadeiras >= 1:
        cadeira_cafe(d, cx - 225 * s, cy + 100 * s, s, seed + 10, frac, lado="esq")
    if cadeiras >= 2:
        cadeira_cafe(d, cx + 225 * s, cy + 100 * s, s, seed + 20, frac, lado="dir")
    sx = 0.5 * s
    xs = {0: [], 1: [cx - 55 * s], 2: [cx - 78 * s, cx + 78 * s]}[min(2, xicaras)]
    for k, x in enumerate(xs):
        xicara_cafe(d, x, cy - 64 * sx, sx, seed + 40 + 5 * k, frac, vapor=vapor, t=t + k)


def mesa_cafe_box(cx, cy, s=1.0, cadeiras=2, xicaras=1, vapor=False):
    sx = 0.5 * s
    top = cy - 6 * s
    if cadeiras:
        top = min(top, cy + 100 * s - 156 * s)
    if xicaras:
        top = min(top, cy - 64 * sx - (152 * sx if vapor else 54 * sx))
    meia = 225 * s + 74 * s if cadeiras else 150 * s
    return (cx - meia, top, 2 * meia, cy + 254 * s - top)


# ---------------------------------------------------------------------------
# 4. Pilha de livros (livraria)
# ---------------------------------------------------------------------------
def pilha_livros(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Tres livros deitados e empilhados. (cx, cy) = centro da pilha; altura ~140*s."""
    livros = [(0, 230, 50, AZUL), (12, 200, 46, LARANJA), (-8, 214, 44, VERDE)]
    y = cy + 70 * s
    for k, (dx, w, h, cor) in enumerate(livros):
        x0, x1 = cx + (dx - w / 2) * s, cx + (dx + w / 2) * s
        r = _ret(x0, y - h * s, x1, y)
        if frac >= 0.99:
            preencher(d, r, cor)
            preencher(d, _ret(x1 - 26 * s, y - h * s + 7 * s, x1 - 5 * s, y - 7 * s), BRANCO)
        traco(d, r, seed + k, frac, w=6, amp=1.5 * s, fechado=True)
        if frac >= 0.99:
            traco(d, [(x0 + 30 * s, y - h * s / 2), (x0 + 110 * s, y - h * s / 2)], seed + 10 + k, 1.0, w=4, amp=1, col=INK)
        y -= h * s


def pilha_livros_box(cx, cy, s=1.0):
    return (cx - 125 * s, cy - 74 * s, 250 * s, 148 * s)


# ---------------------------------------------------------------------------
# 5. Maleta (trabalho, o 2o lugar)
# ---------------------------------------------------------------------------
def maleta_trabalho(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=COURO):
    corpo = _ret(cx - 105 * s, cy - 60 * s, cx + 105 * s, cy + 75 * s)
    if frac >= 0.99:
        preencher(d, corpo, cor)
    traco(d, corpo, seed, frac, w=6, amp=1.5 * s, fechado=True)
    traco(d, [(cx - 36 * s, cy - 60 * s), (cx - 36 * s, cy - 95 * s), (cx + 36 * s, cy - 95 * s), (cx + 36 * s, cy - 60 * s)],
          seed + 1, frac, w=7, amp=1.5 * s)
    if frac >= 0.99:
        traco(d, [(cx - 105 * s, cy - 12 * s), (cx + 105 * s, cy - 12 * s)], seed + 2, 1.0, w=4, amp=1)
        fecho = _ret(cx - 16 * s, cy - 24 * s, cx + 16 * s, cy + 2 * s)
        preencher(d, fecho, SOL_AMARELO)
        traco(d, fecho, seed + 3, 1.0, w=4, amp=1, fechado=True)


def maleta_trabalho_box(cx, cy, s=1.0):
    return (cx - 108 * s, cy - 99 * s, 216 * s, 177 * s)


# ---------------------------------------------------------------------------
# 6. Selo de ordem ("1º", "2º", "3º")
# ---------------------------------------------------------------------------
def selo_numero(d, cx, cy, s=1.0, seed=0, frac=1.0, txt="3º", cor=LARANJA):
    r = 46 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_clareia(cor, 0.45))
    traco(d, circ(cx, cy, r, 32), seed, frac, w=6, amp=1.5 * s, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy + 2 * s, txt, int(50 * s))


def selo_numero_box(cx, cy, s=1.0):
    r = 50 * s
    return (cx - r, cy - r, 2 * r, 2 * r)


# ---------------------------------------------------------------------------
# 7. Coluna de relogios (horas por semana; o ultimo relogio parcial = "quase"/"menos de")
# ---------------------------------------------------------------------------
def coluna_relogios(d, cx, y_base, s=1.0, seed=0, frac=1.0, horas=6.8, cor=AZUL, t=0.0):
    """Empilha relogios de baixo para cima, um por hora. A parte fracionaria vira um relogio
    em fatia (contorno tracejado), lido como "quase" ou "menos de". `frac` faz a pilha crescer.
    (cx, y_base) = centro do chao da coluna. Ilustrativo: o numero exato vai no rotulo."""
    r = 46 * s
    passo = 2 * r + 10 * s
    n = int(math.ceil(horas - 1e-9))
    traco(d, [(cx - 80 * s, y_base), (cx + 80 * s, y_base)], seed, _lim(frac * 3), w=7, amp=1.5)
    claro = _clareia(cor, 0.5)
    for k in range(n):
        ap = _lim(frac * n - k)
        if ap <= 0:
            break
        y = y_base - 6 * s - r - k * passo
        parte = min(1.0, horas - k)
        if parte >= 0.999:
            if ap >= 0.99:
                d.ellipse([cx - r, y - r, cx + r, y + r], fill=claro)
            traco(d, circ(cx, y, r, 32), seed + 10 + k, ap, w=5, amp=1.2 * s, fechado=True)
            if ap >= 0.99:
                a = t * 1.2 + k - math.pi / 2
                traco(d, [(cx, y), (cx + 0.7 * r * math.cos(a), y + 0.7 * r * math.sin(a))], seed + 40 + k, 1.0, w=4, amp=0.6)
                traco(d, [(cx, y), (cx + 0.45 * r * math.cos(a / 12 - 1), y + 0.45 * r * math.sin(a / 12 - 1))], seed + 60 + k, 1.0, w=5, amp=0.6)
        else:
            if ap >= 0.99:
                d.pieslice([cx - r, y - r, cx + r, y + r], -90, -90 + 360 * parte, fill=claro)
                arco = [(cx + r * math.cos(math.radians(-90 + 360 * parte * i / 24)),
                         y + r * math.sin(math.radians(-90 + 360 * parte * i / 24))) for i in range(25)]
                traco(d, [(cx, y)] + arco + [(cx, y)], seed + 10 + k, 1.0, w=5, amp=1.0 * s)
            tracejado(d, circ(cx, y, r, 32), seed + 80, ap, w=4, col=FERRO, passo=14, vao=10, fechado=True)


def coluna_relogios_box(cx, y_base, s=1.0, horas=6.8):
    r = 46 * s
    n = int(math.ceil(horas - 1e-9))
    alt = 6 * s + n * (2 * r + 10 * s)
    return (cx - 82 * s, y_base - alt, 164 * s, alt + 6)


# ---------------------------------------------------------------------------
# 8. Cartao de variacao (icone + seta + numero grande + rotulo)
# ---------------------------------------------------------------------------
def _porta(d, cx, cy, s, seed, frac):
    """Porta aberta (saida). (cx, cy) = centro do batente; 80x130."""
    x0, x1, y0, y1 = cx - 40 * s, cx + 40 * s, cy - 65 * s, cy + 65 * s
    if frac >= 0.99:
        preencher(d, _ret(x0, y0, x1, y1), _clareia(SOL_AMARELO, 0.35))
        folha = [(x0, y0), (x0 + 46 * s, y0 + 16 * s), (x0 + 46 * s, y1 + 10 * s), (x0, y1)]
        preencher(d, folha, MADEIRA)
        traco(d, folha, seed + 1, 1.0, w=5, amp=1, fechado=True)
        d.ellipse([x0 + 34 * s, cy - 4 * s, x0 + 42 * s, cy + 4 * s], fill=INK)
    traco(d, _ret(x0, y0, x1, y1), seed, frac, w=6, amp=1.2 * s, fechado=True)


def cartao_variacao(d, cx, cy, s=1.0, seed=0, frac=1.0, valor="-7,1%", rotulo="saídas",
                    sentido=-1, cor=VERMELHO, icone="porta"):
    """Cartao branco com icone (porta = saidas, moeda = gasto), seta de subida/queda,
    numero grande colorido e rotulo. Numeros e rotulos vem do roteiro (nao inventar)."""
    w, h = 380 * s, 440 * s
    c = _ret(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    if frac >= 0.99:
        preencher(d, c, BRANCO)
    traco(d, c, seed, frac, w=6, amp=1.5 * s, fechado=True)
    ix, iy = cx - 70 * s, cy - 105 * s
    if icone == "porta":
        _porta(d, ix, iy, s, seed + 5, frac)
    else:
        moeda(d, ix, iy, s=0.8 * s, seed=seed + 5, frac=frac)
    if frac >= 0.99:
        ya, yb = (cy - 170 * s, cy - 45 * s) if sentido < 0 else (cy - 45 * s, cy - 170 * s)
        seta(d, cx + 85 * s, ya, cx + 85 * s, yb, seed=seed + 9, cor=cor, w=9)
        texto(d, cx, cy + 50 * s, valor, int(96 * s), cor)
        texto(d, cx, cy + 160 * s, rotulo, int(44 * s))


def cartao_variacao_box(cx, cy, s=1.0):
    w, h = 380 * s, 440 * s
    return (cx - w / 2, cy - h / 2, w, h)


# ---------------------------------------------------------------------------
# 9. Relogio sem medida (Brasil nao tem a pesquisa de uso do tempo)
# ---------------------------------------------------------------------------
def relogio_sem_medida(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0):
    """Relogio so em tracejado, sem ponteiros, com '?' no lugar: a medida que nao existe."""
    r = 110 * s
    tracejado(d, circ(cx, cy, r, 48), seed, frac, w=6, col=FERRO, passo=24, vao=14, fechado=True)
    if frac >= 0.99:
        for k in range(12):
            a = math.tau * k / 12
            traco(d, [(cx + 0.82 * r * math.cos(a), cy + 0.82 * r * math.sin(a)),
                      (cx + 0.92 * r * math.cos(a), cy + 0.92 * r * math.sin(a))], seed + 10 + k, 1.0, w=4, amp=0.5, col=FERRO)
        texto(d, cx, cy + 6 * s, "?", int(150 * s * (1 + 0.05 * math.sin(t * 5))), LARANJA)


def relogio_sem_medida_box(cx, cy, s=1.0):
    r = 116 * s
    return (cx - r, cy - r, 2 * r, 2 * r)


# ---------------------------------------------------------------------------
# 10. Banco de praca (o lugar de graca); sumindo = tracejado cinza
# ---------------------------------------------------------------------------
def banco_praca(d, cx, cy, s=1.0, seed=0, frac=1.0, sumindo=False, etiqueta="grátis"):
    """Banco de praca de frente. (cx, cy) = topo do assento. Etiqueta pendurada acima.
    `sumindo=True`: tudo em tracejado cinza (o lugar gratuito que some)."""
    col = FERRO if sumindo else INK
    linha = (lambda p, sd, f, w=6, fech=False: tracejado(d, p, sd, f, w=w, col=col, fechado=fech)) if sumindo else \
            (lambda p, sd, f, w=6, fech=False: traco(d, p, sd, f, w=w, amp=1.5 * s, col=col, fechado=fech))
    tabuas = [_ret(cx - 180 * s, cy, cx + 180 * s, cy + 24 * s),
              _ret(cx - 170 * s, cy - 110 * s, cx + 170 * s, cy - 86 * s),
              _ret(cx - 170 * s, cy - 70 * s, cx + 170 * s, cy - 46 * s)]
    if frac >= 0.99 and not sumindo:
        for tb in tabuas:
            preencher(d, tb, MADEIRA)
    for k, tb in enumerate(tabuas):
        linha(tb, seed + k, frac, 6, True)
    for k, x in enumerate((-130, 130)):
        linha([(cx + x * s, cy - 46 * s), (cx + x * s, cy)], seed + 5 + k, frac)
        linha([(cx + (x * 1.15) * s, cy + 24 * s), (cx + (x * 1.22) * s, cy + 108 * s)], seed + 8 + k, frac, 7)
    if etiqueta and frac >= 0.99:
        tam = int(46 * s)
        lg = fonte(tam).getlength(etiqueta) + 40 * s
        ty = cy - 178 * s
        tag = _ret(cx - lg / 2, ty - 32 * s, cx + lg / 2, ty + 32 * s)
        preencher(d, tag, BRANCO)
        linha(tag, seed + 20, 1.0, 5, True)
        linha([(cx, ty + 32 * s), (cx, cy - 110 * s)], seed + 21, 1.0, 4)
        texto(d, cx, ty, etiqueta, tam, FERRO if sumindo else (60, 150, 90))


def banco_praca_box(cx, cy, s=1.0, etiqueta="grátis"):
    top = cy - (214 * s if etiqueta else 114 * s)
    return (cx - 184 * s, top, 368 * s, cy + 112 * s - top)


# ---------------------------------------------------------------------------
# 11. Recibo de orcamento (ver amigo vira item de orcamento)
# ---------------------------------------------------------------------------
def recibo_orcamento(d, cx, cy, s=1.0, seed=0, frac=1.0, titulo="orçamento",
                     itens=("aluguel", "mercado", "ver amigo"), destaque=2):
    """Comanda/recibo com borda de baixo em serrilha. O item `destaque` sai em laranja,
    marcado com marca-texto. Sem valores: so 'R$' e um traco (nada de numero inventado)."""
    w, h = 420 * s, 440 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    serra = []
    n = 10
    for i in range(n + 1):
        serra.append((x1 - i * w / n, y1 - (18 * s if i % 2 else 0)))
    corpo = [(x0, y0), (x1, y0)] + serra[:-1] + [(x0, y1)]
    if frac >= 0.99:
        preencher(d, corpo, BRANCO)
    traco(d, corpo, seed, frac, w=6, amp=1.5 * s, fechado=True)
    if frac < 0.99:
        return
    texto(d, cx, y0 + 58 * s, titulo, int(52 * s))
    tracejado(d, [(x0 + 24 * s, y0 + 106 * s), (x1 - 24 * s, y0 + 106 * s)], seed + 3, 1.0, w=4, col=FERRO, passo=16, vao=10)
    for i, item in enumerate(itens):
        y = y0 + 168 * s + i * 86 * s
        cor = INK
        if i == destaque:
            preencher(d, _ret(x0 + 16 * s, y - 34 * s, x1 - 16 * s, y + 34 * s), _clareia(SOL_AMARELO, 0.35))
            cor = LARANJA
        texto(d, x0 + 34 * s, y, item, int(46 * s), cor, ancora="lm")
        texto(d, x1 - 104 * s, y, "R$", int(40 * s), cor, ancora="rm")
        traco(d, [(x1 - 94 * s, y + 14 * s), (x1 - 34 * s, y + 14 * s)], seed + 10 + i, 1.0, w=4, amp=1, col=cor)


def recibo_orcamento_box(cx, cy, s=1.0):
    w, h = 420 * s, 440 * s
    return (cx - w / 2 - 3, cy - h / 2 - 3, w + 6, h + 6)


# ---------------------------------------------------------------------------
# 12. Selo "hipotese, nao prova" (carimbo com borda dupla)
# ---------------------------------------------------------------------------
def selo_hipotese(d, cx, cy, s=1.0, seed=0, frac=1.0, txt="hipótese, não prova", cor=LARANJA):
    tam = int(48 * s)
    lg = fonte(tam).getlength(txt) + 70 * s
    hh = 96 * s
    externo = _ret(cx - lg / 2, cy - hh / 2, cx + lg / 2, cy + hh / 2)
    interno = _ret(cx - lg / 2 + 10 * s, cy - hh / 2 + 10 * s, cx + lg / 2 - 10 * s, cy + hh / 2 - 10 * s)
    if frac >= 0.99:
        preencher(d, externo, BRANCO)
    traco(d, externo, seed, frac, w=6, amp=1.5 * s, col=cor, fechado=True)
    traco(d, interno, seed + 1, frac, w=3, amp=1.0 * s, col=cor, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy + 2 * s, txt, tam, cor)


def selo_hipotese_box(cx, cy, s=1.0, txt="hipótese, não prova"):
    lg = fonte(int(48 * s)).getlength(txt) + 70 * s
    hh = 96 * s
    return (cx - lg / 2 - 3, cy - hh / 2 - 3, lg + 6, hh + 6)


# ---------------------------------------------------------------------------
# 13. TV com streaming (tela com texto coerente: "continuar assistindo?")
# ---------------------------------------------------------------------------
def tv_streaming(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0, linhas=("continuar", "assistindo?")):
    """TV de pe. Tela gelo com botao de play, texto generico de streaming (sem marca) e barra
    de progresso que anda com t. (cx, cy) = centro da TV."""
    w, h = 460 * s, 290 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    tela = _ret(x0 + 18 * s, y0 + 18 * s, x1 - 18 * s, y1 - 18 * s)
    if frac >= 0.99:
        preencher(d, _ret(x0, y0, x1, y1), (70, 72, 82))
        preencher(d, tela, GELO)
    traco(d, _ret(x0, y0, x1, y1), seed, frac, w=7, amp=1.5 * s, fechado=True)
    traco(d, [(cx - 70 * s, y1), (cx - 100 * s, y1 + 50 * s)], seed + 1, frac, w=7, amp=1.5 * s)
    traco(d, [(cx + 70 * s, y1), (cx + 100 * s, y1 + 50 * s)], seed + 2, frac, w=7, amp=1.5 * s)
    if frac < 0.99:
        return
    traco(d, tela, seed + 3, 1.0, w=4, amp=1, fechado=True)
    px, py, pr = cx - 140 * s, cy - 20 * s, 50 * s
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=BRANCO)
    traco(d, circ(px, py, pr, 28), seed + 4, 1.0, w=5, amp=1, fechado=True)
    preencher(d, [(px - 16 * s, py - 24 * s), (px + 26 * s, py), (px - 16 * s, py + 24 * s)], INK)
    tam = int(40 * s)
    texto_multilinha(d, cx + 70 * s, cy - 44 * s, list(linhas), tam, espaco=1.2)
    yb = y1 - 48 * s
    xa, xb = x0 + 44 * s, x1 - 44 * s
    p = 0.45 + 0.25 * _lim(t / 6)
    traco(d, [(xa, yb), (xb, yb)], seed + 5, 1.0, w=8, amp=0.6, col=FERRO)
    traco(d, [(xa, yb), (xa + (xb - xa) * p, yb)], seed + 6, 1.0, w=9, amp=0.6, col=AZUL)
    d.ellipse([xa + (xb - xa) * p - 10 * s, yb - 10 * s, xa + (xb - xa) * p + 10 * s, yb + 10 * s], fill=AZUL)


def tv_streaming_box(cx, cy, s=1.0):
    w, h = 460 * s, 290 * s
    return (cx - w / 2 - 3, cy - h / 2 - 3, w + 6, h + 56 * s)


# ---------------------------------------------------------------------------
# 14. Celular com video (tela com texto coerente: "próximo / em 5 s")
# ---------------------------------------------------------------------------
def celular_video(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0, linhas=("próximo", "em 5 s")):
    """Celular da lib com um video na tela e o aviso de reproducao automatica (generico, sem marca)."""
    celular(d, cx, cy, s=s, seed=seed, frac=frac)
    if frac < 0.99:
        return
    v = _ret(cx - 60 * s, cy - 100 * s, cx + 60 * s, cy - 20 * s)
    preencher(d, v, (95, 100, 115))
    traco(d, v, seed + 7, 1.0, w=3, amp=0.8, fechado=True)
    preencher(d, [(cx - 14 * s, cy - 78 * s), (cx + 20 * s, cy - 60 * s), (cx - 14 * s, cy - 42 * s)], BRANCO)
    texto_multilinha(d, cx, cy + 18 * s, list(linhas), int(28 * s), espaco=1.25)


def celular_video_box(cx, cy, s=1.0):
    return (cx - 88 * s, cy - 143 * s, 176 * s, 286 * s)


# ---------------------------------------------------------------------------
# 15. Boneco sozinho no sofa (o tempo sozinho cresceu)
# ---------------------------------------------------------------------------
def sofa_sozinho(d, cx, cy, s=1.0, seed=0, frac=1.0, cor_sofa=None, cor=INK):
    """Sofa de frente com um boneco sentado sozinho. (cx, cy) = topo do assento."""
    cs = cor_sofa or _clareia(AZUL, 0.5)
    encosto = _ret(cx - 170 * s, cy - 120 * s, cx + 170 * s, cy)
    bracos = [_ret(cx - 205 * s, cy - 60 * s, cx - 150 * s, cy + 70 * s),
              _ret(cx + 150 * s, cy - 60 * s, cx + 205 * s, cy + 70 * s)]
    assento = _ret(cx - 150 * s, cy, cx + 150 * s, cy + 70 * s)
    partes = [encosto, assento] + bracos
    if frac >= 0.99:
        for p in partes:
            preencher(d, p, cs)
    for k, p in enumerate(partes):
        traco(d, p, seed + k, frac, w=6, amp=1.5 * s, fechado=True)
    for k, x in enumerate((-180, 180)):
        traco(d, [(cx + x * s, cy + 70 * s), (cx + x * s, cy + 96 * s)], seed + 6 + k, frac, w=7, amp=1)
    # boneco sentado (desenhado por cima do sofa; faz parte do mesmo componente)
    sk = lambda pts, sd: traco(d, pts, seed + 20 + sd, frac, w=6, amp=2.0 * s, col=cor)
    if frac >= 0.99:
        d.ellipse([cx - 36 * s, cy - 212 * s, cx + 36 * s, cy - 140 * s], fill=PAPEL)
    sk(circ(cx, cy - 176 * s, 36 * s, 36), 1)
    sk([(cx, cy - 140 * s), (cx, cy + 6 * s)], 2)
    sk([(cx, cy - 104 * s), (cx - 46 * s, cy - 30 * s), (cx - 22 * s, cy + 14 * s)], 3)
    sk([(cx, cy - 104 * s), (cx + 46 * s, cy - 30 * s), (cx + 22 * s, cy + 14 * s)], 4)
    sk([(cx, cy + 6 * s), (cx - 32 * s, cy + 44 * s), (cx - 36 * s, cy + 150 * s)], 5)
    sk([(cx, cy + 6 * s), (cx + 32 * s, cy + 44 * s), (cx + 36 * s, cy + 150 * s)], 6)


def sofa_sozinho_box(cx, cy, s=1.0):
    return (cx - 208 * s, cy - 216 * s, 416 * s, 372 * s)


# ---------------------------------------------------------------------------
# 16. Mistura de causas (dois circulos: "lugar e custo" x "telas")
# ---------------------------------------------------------------------------
def mistura_causas(d, cx, cy, s=1.0, seed=0, frac=1.0, rot_a=("lugar e", "custo"), rot_b=("telas",)):
    """Dois circulos que se cruzam (laranja = lugar e custo; azul = telas); a interseccao
    hachurada e a 'mistura das duas coisas'. Rotulos dentro de cada lado."""
    r = 170 * s
    ca, cb = cx - 110 * s, cx + 110 * s
    if frac >= 0.99:
        xi = ca + r - 2 * 110 * s  # = cb - r
        x = xi + 14 * s
        k = 0
        while x < ca + r - 8 * s:
            ha = math.sqrt(max(0.0, r * r - (x - ca) ** 2))
            hb = math.sqrt(max(0.0, r * r - (x - cb) ** 2))
            hh = min(ha, hb) - 10 * s
            if hh > 6:
                traco(d, [(x, cy - hh), (x, cy + hh)], seed + 50 + k, 1.0, w=3, amp=0.8, col=_clareia(INK, 0.55))
            x += 20 * s
            k += 1
    traco(d, circ(ca, cy, r, 56), seed, frac, w=7, amp=1.8 * s, col=LARANJA, fechado=True)
    traco(d, circ(cb, cy, r, 56), seed + 1, frac, w=7, amp=1.8 * s, col=AZUL, fechado=True)
    if frac >= 0.99:
        tam = int(48 * s)
        texto_multilinha(d, cx - 178 * s, cy - (len(rot_a) - 1) * tam * 0.62, list(rot_a), tam, LARANJA)
        texto_multilinha(d, cx + 178 * s, cy - (len(rot_b) - 1) * tam * 0.62, list(rot_b), tam, AZUL)


def mistura_causas_box(cx, cy, s=1.0):
    return (cx - 284 * s, cy - 174 * s, 568 * s, 348 * s)


# ---------------------------------------------------------------------------
# 17. Fila de idades (queda forte nos jovens, mas nao so neles)
# ---------------------------------------------------------------------------
def fila_idades(d, cx, cy, s=1.0, seed=0, frac=1.0, n=4, destaque=0, rotulo="jovens", bengala=True):
    """Fila de bonecos; o `destaque` (jovem) em laranja com seta de queda grande, os demais
    com seta menor em cinza (tambem cairam). O ultimo com bengala (mais velho)."""
    passo = 170 * s
    ps = 0.9 * s
    x0 = cx - (n - 1) * passo / 2
    for k in range(n):
        x = x0 + k * passo
        cor = LARANJA if k == destaque else INK
        pessoa(d, x, cy, ps, seed + 10 * k, frac, cor)
        if bengala and k == n - 1:
            traco(d, [(x + 50 * ps, cy + 5 * ps), (x + 58 * ps, cy + 125 * ps)], seed + 90, frac, w=5, amp=1)
            traco(d, [(x + 50 * ps, cy + 5 * ps), (x + 40 * ps, cy - 6 * ps)], seed + 91, frac, w=5, amp=1)
        if frac >= 0.99:
            fim = cy - 146 * ps - 26 * s
            comp = 150 * s if k == destaque else 80 * s
            seta(d, x, fim - comp, x, fim, seed=seed + 100 + k, cor=(VERMELHO if k == destaque else FERRO),
                 w=(9 if k == destaque else 6))
    if rotulo and frac >= 0.99:
        texto(d, x0 + destaque * passo, cy + 125 * ps + 52 * s, rotulo, int(48 * s), LARANJA)


def fila_idades_box(cx, cy, s=1.0, n=4, rotulo="jovens", destaque=0):
    passo = 170 * s
    ps = 0.9 * s
    x0 = cx - (n - 1) * passo / 2
    top = cy - 146 * ps - 26 * s - 150 * s - 6
    base = cy + 125 * ps + (52 * s + 30 * s if rotulo else 4)
    esq = x0 - 56 * ps
    dirx = x0 + (n - 1) * passo + 62 * ps
    if rotulo:
        meia = fonte(int(48 * s)).getlength(rotulo) / 2 + 4
        xr = x0 + destaque * passo
        esq, dirx = min(esq, xr - meia), max(dirx, xr + meia)
    return (esq, top, dirx - esq, base - top)
