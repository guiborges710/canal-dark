"""Componentes NOVOS do video esquema-de-piramide (proposta, aguardando aprovacao).

Cada funcao desenha UM componente, parametrizado por posicao, escala e `frac`
(progresso do traco). Importa a biblioteca-base do canal; mesmo estilo e paleta.
Os icones basicos (pessoa, moeda, casa, seta, cruz, check, circ, traco, preencher...)
e as cores (INK, AZUL, LARANJA, VERDE, GELO, SOL_AMARELO, VERMELHO) ja vivem em
media/sketch_lib.py e NAO sao duplicados aqui.

Cada componente tem uma funcao companheira `*_box(cx, cy, s, ...)` que devolve a
caixa ocupada como (x, y, w, h) com ancora no canto superior esquerdo. O Olise usa
as caixas para posicionar sem sobrepor boneco nem texto.

Convencao de cor deste video:
  - AZUL   = pessoa / confianca / multinivel legal (venda real)
  - LARANJA= dinheiro em movimento / adesao / alerta de recrutamento
  - VERDE  = produto real / check
  - VERMELHO = colapso, condenacao, negacao
  - SOL_AMARELO = moeda / cifrao

NAO promover para media/sketch_componentes.py nem catalogo.md sem aprovacao do Guilherme.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *

VERDE_OK = (60, 150, 90)


# ---------------------------------------------------------------------------
# 1. Piramide de pessoas (degraus com bonequinhos; dinheiro sobe ao topo)
# ---------------------------------------------------------------------------
def piramide_pessoas(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=INK, dinheiro=False,
                     colapso=False):
    """Piramide de 4 degraus de bonequinhos simples (cabeca + tronco), base larga.
    `dinheiro=True`: setas amarelas sobem da base ao topo (o dinheiro vai pra cima).
    `colapso=True`: a base fica vermelha e uma rachadura corta a piramide."""
    niveis = [1, 2, 3, 4]              # topo -> base
    alt_lin = 150 * s
    y_topo = cy - 300 * s
    passo_x = 150 * s
    r = 26 * s
    centros = []                       # (x, y) da cabeca de cada boneco por linha
    for i, n in enumerate(niveis):
        y = y_topo + i * alt_lin
        x0 = cx - (n - 1) * passo_x / 2
        linha = []
        for k in range(n):
            x = x0 + k * passo_x
            cor_b = VERMELHO if (colapso and i == len(niveis) - 1) else cor
            # cabeca
            traco(d, circ(x, y, r, 28), seed + 100 * i + k, frac, w=5, amp=1.6 * s,
                  col=cor_b, fechado=True)
            # tronco em triangulo (ombros)
            traco(d, [(x - 24 * s, y + r + 70 * s), (x, y + r + 6 * s),
                      (x + 24 * s, y + r + 70 * s)], seed + 100 * i + k + 50, frac,
                  w=5, amp=1.6 * s, col=cor_b)
            linha.append((x, y))
        centros.append(linha)
    if dinheiro and frac >= 0.99:
        # tres setas amarelas da base ao topo
        for dx in (-passo_x, 0, passo_x):
            seta(d, cx + dx * 0.9, cy + 250 * s, cx, y_topo - 10 * s,
                 seed=seed + 300, cor=SOL_AMARELO, w=7)
    if colapso and frac >= 0.99:
        # rachadura em zigue-zague do topo a base
        zig = [(cx, y_topo - 20 * s), (cx + 30 * s, cy - 120 * s),
               (cx - 30 * s, cy + 20 * s), (cx + 25 * s, cy + 260 * s)]
        traco(d, zig, seed + 400, 1.0, w=8, amp=2, col=VERMELHO)


def piramide_pessoas_box(cx, cy, s=1.0, dinheiro=False):
    w = 4 * 150 * s + 80 * s
    y0 = cy - 300 * s - 30 * s
    y1 = cy + 300 * s + 70 * s
    if dinheiro:
        y1 = cy + 250 * s + 40 * s
        y0 = min(y0, cy - 300 * s - 20 * s)
    return (cx - w / 2, y0, w, y1 - y0)


# ---------------------------------------------------------------------------
# 2. Pilha de dinheiro (notas empilhadas + cifrao) - o "topo" que ganha
# ---------------------------------------------------------------------------
def pilha_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Tres notas empilhadas com cifrao na de cima."""
    w, h = 170 * s, 62 * s
    for i in range(3):
        y = cy + i * 26 * s
        c = [(cx - w / 2, y - h / 2), (cx + w / 2, y - h / 2),
             (cx + w / 2, y + h / 2), (cx - w / 2, y + h / 2)]
        if frac >= 0.99:
            preencher(d, c, VERDE)
        traco(d, c, seed + i, frac, w=5, amp=1.6 * s, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy - h / 2 + 2 * s, "R$", int(44 * s), INK)


def pilha_dinheiro_box(cx, cy, s=1.0):
    w, h = 170 * s, 62 * s
    return (cx - w / 2, cy - h / 2, w, h + 2 * 26 * s)


# ---------------------------------------------------------------------------
# 3. Bloco venda real x adesao (contraexemplo do multinivel legal)
#    desenha UM dos dois lados conforme `modo`
# ---------------------------------------------------------------------------
def fonte_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0, modo="venda"):
    """modo='venda': caixa/produto verde -> moeda (vem de venda real).
       modo='adesao': bonequinhos entrando -> moeda (vem so de adesao)."""
    if modo == "venda":
        # caixa de produto
        w, h = 150 * s, 130 * s
        c = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
             (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
        if frac >= 0.99:
            preencher(d, c, VERDE)
        traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
        if frac >= 0.99:
            # fita da caixa
            traco(d, [(cx, cy - h / 2), (cx, cy + h / 2)], seed + 1, 1.0, w=4, amp=1, col=INK)
            traco(d, [(cx - w / 2, cy), (cx + w / 2, cy)], seed + 2, 1.0, w=4, amp=1, col=INK)
            seta(d, cx + w / 2 + 10 * s, cy, cx + w / 2 + 120 * s, cy, seed=seed + 3,
                 cor=VERDE_OK, w=6)
            moeda(d, cx + w / 2 + 185 * s, cy, s=0.62 * s, seed=seed + 4)
    else:
        # tres cabecas entrando (recrutados) -> moeda
        for k in range(3):
            x = cx - 70 * s + k * 70 * s
            traco(d, circ(x, cy, 24 * s, 26), seed + 10 + k, frac, w=5, amp=1.6 * s,
                  col=LARANJA, fechado=True)
        if frac >= 0.99:
            seta(d, cx + 110 * s, cy, cx + 215 * s, cy, seed=seed + 20,
                 cor=LARANJA, w=6)
            moeda(d, cx + 280 * s, cy, s=0.62 * s, seed=seed + 21)


def fonte_dinheiro_box(cx, cy, s=1.0, modo="venda"):
    if modo == "venda":
        x0 = cx - 150 * s / 2
        x1 = cx + 150 * s / 2 + 185 * s + 70 * 0.62 * s
        h = 130 * s
    else:
        x0 = cx - 70 * s - 24 * s
        x1 = cx + 280 * s + 70 * 0.62 * s
        h = 140 * s
    return (x0, cy - h / 2, x1 - x0, h)


# ---------------------------------------------------------------------------
# 4. Mensageiro de confianca (boneco passando um convite/envelope a outro)
# ---------------------------------------------------------------------------
def convite_confianca(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Dois bonecos proximos; o da esquerda (azul) estende um envelope ao da direita.
    Representa 'o convite chega pela pessoa em quem voce confia'."""
    dist = 300 * s
    xa, xb = cx - dist / 2, cx + dist / 2
    pessoa(d, xa, cy, s=1.1 * s, seed=seed, frac=frac, cor=AZUL)
    pessoa(d, xb, cy, s=1.1 * s, seed=seed + 20, frac=frac, cor=INK)
    if frac >= 0.99:
        # envelope entre os dois
        ex, ey = cx, cy - 20 * s
        w, h = 90 * s, 60 * s
        c = [(ex - w / 2, ey - h / 2), (ex + w / 2, ey - h / 2),
             (ex + w / 2, ey + h / 2), (ex - w / 2, ey + h / 2)]
        preencher(d, c, (255, 255, 255))
        traco(d, c, seed + 40, 1.0, w=5, amp=1.5, fechado=True)
        traco(d, [(ex - w / 2, ey - h / 2), (ex, ey + 6 * s), (ex + w / 2, ey - h / 2)],
              seed + 41, 1.0, w=4, amp=1.2)
        # coracao pequeno de confianca acima do envelope
        coracao(d, ex, ey - h / 2 - 50 * s, s=0.5 * s, seed=seed + 42, cor=(225, 90, 100))


def convite_confianca_box(cx, cy, s=1.0):
    dist = 300 * s
    larg = dist + 120 * 1.1 * s
    top = cy - 146 * 1.1 * s - 90 * s     # inclui o coracao acima
    base = cy + 125 * 1.1 * s
    return (cx - larg / 2, top, larg, base - top)


# ---------------------------------------------------------------------------
# 5. Icones de "fachada" dos casos: avestruz, gado (boi), bitcoin
# ---------------------------------------------------------------------------
def icone_avestruz(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Avestruz estilizado: corpo ovalado, pescoco longo, cabeca, duas pernas."""
    # corpo
    traco(d, circ(cx, cy + 10 * s, 70 * s, 32), seed, frac, w=6, amp=2 * s, fechado=True)
    # pescoco
    traco(d, [(cx + 30 * s, cy - 40 * s), (cx + 70 * s, cy - 150 * s)], seed + 1, frac, w=6, amp=2 * s)
    # cabeca
    if frac >= 0.99:
        traco(d, circ(cx + 75 * s, cy - 165 * s, 20 * s, 20), seed + 2, 1.0, w=5, amp=1.5 * s, fechado=True)
        # bico
        traco(d, [(cx + 92 * s, cy - 165 * s), (cx + 120 * s, cy - 158 * s)], seed + 3, 1.0, w=5, amp=1.2)
    # pernas
    traco(d, [(cx - 20 * s, cy + 75 * s), (cx - 24 * s, cy + 150 * s)], seed + 4, frac, w=6, amp=2 * s)
    traco(d, [(cx + 20 * s, cy + 75 * s), (cx + 24 * s, cy + 150 * s)], seed + 5, frac, w=6, amp=2 * s)


def icone_avestruz_box(cx, cy, s=1.0):
    return (cx - 90 * s, cy - 190 * s, 230 * s, 350 * s)


def icone_gado(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Boi estilizado: corpo retangular arredondado, cabeca com dois chifres, 4 patas."""
    w, h = 170 * s, 110 * s
    corpo = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
             (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    traco(d, corpo, seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        # cabeca a esquerda, afastada do corpo com um pescoco curto
        hx = cx - w / 2 - 54 * s
        traco(d, [(cx - w / 2, cy), (hx + 32 * s, cy - 6 * s)], seed + 8, 1.0, w=6, amp=1.5 * s)
        traco(d, circ(hx, cy - 8 * s, 34 * s, 26), seed + 1, 1.0, w=6, amp=2 * s, fechado=True)
        # chifres
        traco(d, [(hx - 18 * s, cy - 36 * s), (hx - 34 * s, cy - 66 * s)], seed + 2, 1.0, w=5, amp=1.2)
        traco(d, [(hx + 18 * s, cy - 36 * s), (hx + 34 * s, cy - 66 * s)], seed + 3, 1.0, w=5, amp=1.2)
        # patas
        for dx in (-w / 2 + 24 * s, w / 2 - 24 * s):
            traco(d, [(cx + dx, cy + h / 2), (cx + dx, cy + h / 2 + 60 * s)], seed + 4, 1.0, w=6, amp=1.5)
        # cauda
        traco(d, [(cx + w / 2, cy - 20 * s), (cx + w / 2 + 40 * s, cy + 30 * s)], seed + 7, 1.0, w=5, amp=1.2)


def icone_gado_box(cx, cy, s=1.0):
    w, h = 170 * s, 110 * s
    return (cx - w / 2 - 92 * s, cy - h / 2 - 70 * s, w + 92 * s + 40 * s, h + 70 * s + 60 * s)


def icone_bitcoin(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Moeda com um 'B' cortado por duas hastes (bitcoin generico, sem logo de marca)."""
    r = 70 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOL_AMARELO)
    traco(d, circ(cx, cy, r, 40), seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy, "B", int(70 * s), INK)
        # duas hastes verticais atravessando o B
        traco(d, [(cx - 6 * s, cy - 48 * s), (cx - 6 * s, cy + 48 * s)], seed + 1, 1.0, w=4, amp=1, col=INK)
        traco(d, [(cx + 16 * s, cy - 48 * s), (cx + 16 * s, cy + 48 * s)], seed + 2, 1.0, w=4, amp=1, col=INK)


def icone_bitcoin_box(cx, cy, s=1.0):
    r = 70 * s
    return (cx - r, cy - r, 2 * r, 2 * r)


# ---------------------------------------------------------------------------
# 6. Martelo de juiz (condenacao) + rotulo de anos
# ---------------------------------------------------------------------------
def martelo_juiz(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Martelo de juiz (cabeca cilindrica + cabo) batendo numa base."""
    # cabeca do martelo (retangulo inclinado)
    w, h = 150 * s, 56 * s
    ang = -0.35
    def rot(px, py):
        return (cx + (px) * math.cos(ang) - (py) * math.sin(ang),
                cy + (px) * math.sin(ang) + (py) * math.cos(ang))
    cab = [rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)]
    if frac >= 0.99:
        preencher(d, cab, (210, 180, 140))
    traco(d, cab, seed, frac, w=6, amp=2 * s, fechado=True)
    # faixas nas pontas
    if frac >= 0.99:
        traco(d, [rot(-w / 2 + 28 * s, -h / 2), rot(-w / 2 + 28 * s, h / 2)], seed + 1, 1.0, w=4, amp=1, col=INK)
        traco(d, [rot(w / 2 - 28 * s, -h / 2), rot(w / 2 - 28 * s, h / 2)], seed + 2, 1.0, w=4, amp=1, col=INK)
    # cabo
    traco(d, [rot(0, h / 2), (cx + 70 * s, cy + 150 * s)], seed + 3, frac, w=9, amp=2 * s)
    # base (bloco)
    if frac >= 0.99:
        bw = 120 * s
        by = cy + 190 * s
        base = [(cx - bw / 2, by), (cx + bw / 2, by), (cx + bw / 2, by + 34 * s), (cx - bw / 2, by + 34 * s)]
        preencher(d, base, (210, 180, 140))
        traco(d, base, seed + 4, 1.0, w=6, amp=2 * s, fechado=True)


def martelo_juiz_box(cx, cy, s=1.0):
    return (cx - 130 * s, cy - 110 * s, 300 * s, 360 * s)


# ---------------------------------------------------------------------------
# 7. Caixa de caso (nome + ano + pena) - cartao resumo de um caso real
# ---------------------------------------------------------------------------
def caixa_caso(d, cx, cy, s=1.0, seed=0, frac=1.0, nome="", ano="", pena=""):
    """Cartao com nome do caso, ano e pena. Textos vem das notas (nao inventar)."""
    w, h = 460 * s, 210 * s
    c = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
         (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
    traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy - 62 * s, nome, int(50 * s), INK)
        if ano:
            texto(d, cx, cy - 4 * s, ano, int(46 * s), LARANJA)
        if pena:
            texto(d, cx, cy + 58 * s, pena, int(42 * s), VERMELHO)


def caixa_caso_box(cx, cy, s=1.0):
    w, h = 460 * s, 210 * s
    return (cx - w / 2, cy - h / 2, w, h)


# ---------------------------------------------------------------------------
# 8. Pessoa x cifrao (a pergunta de volta: confere a pessoa ou o dinheiro?)
# ---------------------------------------------------------------------------
def pessoa_ou_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Lado esquerdo: boneco (a pessoa). Lado direito: cifrao em moeda (o dinheiro).
    Separados por uma linha vertical (a escolha)."""
    pessoa(d, cx - 220 * s, cy, s=1.0 * s, seed=seed, frac=frac, cor=AZUL)
    moeda(d, cx + 220 * s, cy - 20 * s, s=1.0 * s, seed=seed + 10, frac=frac)
    if frac >= 0.99:
        # linha divisoria pontilhada (a decisao)
        y = cy - 170 * s
        while y < cy + 150 * s:
            traco(d, [(cx, y), (cx, y + 26 * s)], seed + 30 + int(y), 1.0, w=5, amp=1, col=FERRO)
            y += 56 * s


def pessoa_ou_dinheiro_box(cx, cy, s=1.0):
    return (cx - 220 * s - 60 * s, cy - 170 * s, 440 * s + 140 * s, 340 * s)
