"""Componentes isolados do video pair-programming-colaboracao (proposta do Raphinha).

ASSETS DEFINITIVOS (2a rodada). Cada funcao desenha UM componente, parametrizado por
posicao, escala e `frac` (progresso do traco). Importa a biblioteca do canal; mesmo estilo e paleta.
Nada aqui altera sketch_cenas.py.

Convencao de cor (a mesma do video): pessoa A = AZUL (escreve primeiro), pessoa B = LARANJA (revisa).
Verde = acerto/decisao. Vermelho = negacao.

Cada componente tem uma funcao companheira `*_box(cx, cy, s, ...)` que devolve a caixa
ocupada como (x, y, w, h) com ancora no canto superior esquerdo. O Olise usa as caixas
para posicionar sem sobrepor boneco nem texto (verificacao automatica em gerar_componentes.py).

As 4 correcoes desta rodada estao marcadas com  # FIX1..FIX4.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *

AZUL_A, LARANJA_B = AZUL, LARANJA
VERDE_OK = (60, 150, 90)


# ---------------------------------------------------------------------------
# 1. Tela de codigo (monitor com linhas de codigo, uma cor por autor)
# ---------------------------------------------------------------------------
def tela_codigo(d, cx, cy, s=1.0, seed=0, frac=1.0, cores=None, riscada=False):
    """Monitor em cima de um pe, com linhas de codigo coloridas por autor.
    `cores`: lista de cores (uma por linha). `riscada`: desenha um X vermelho por cima.
    FIX2: quando riscada, o X usa escala menor e preso DENTRO da tela, nunca invade o topo."""
    w, h = 560 * s, 380 * s
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
    traco(d, c, seed, frac, w=7, amp=2, fechado=True)
    # pe do monitor
    traco(d, [(cx - 70 * s, y1 + 40 * s), (cx + 70 * s, y1 + 40 * s)], seed + 1, frac, w=7, amp=2)
    traco(d, [(cx, y1), (cx, y1 + 40 * s)], seed + 2, frac, w=7, amp=2)
    # linhas de codigo
    cores = cores or [AZUL_A, LARANJA_B, AZUL_A, LARANJA_B, AZUL_A]
    if frac >= 0.99:
        n = len(cores)
        xcod = x0 + 40 * s
        for i, cor in enumerate(cores):
            y = y0 + 55 * s + i * (h - 90 * s) / max(1, n - 1)
            recuo = 50 * s * (i % 3 == 1)
            comp = (0.5 + 0.3 * ((i * 37) % 10) / 10) * (w - 80 * s - recuo)
            traco(d, [(xcod + recuo, y), (xcod + recuo + comp, y)], seed + 20 + i, 1.0, w=9, amp=1.5, col=cor)
    if riscada and frac >= 0.99:
        # FIX2: cruz menor (antes 3.6*s) e centrada na tela; o X cabe com folga dentro da moldura.
        cruz(d, cx, cy, s=2.9 * s, seed=seed + 50)


def tela_codigo_box(cx, cy, s=1.0):
    """Caixa da tela INCLUINDO o pe do monitor (para o Olise nao encostar nada nos pes)."""
    w, h = 560 * s, 380 * s
    return (cx - w / 2, cy - h / 2, w, h + 40 * s)


# ---------------------------------------------------------------------------
# 1b. Tela riscada (atalho nomeado para a cena 0)
# ---------------------------------------------------------------------------
def tela_riscada(d, cx, cy, s=1.0, seed=0, frac=1.0, cores=None):
    tela_codigo(d, cx, cy, s=s, seed=seed, frac=frac, cores=cores, riscada=True)


def tela_riscada_box(cx, cy, s=1.0):
    return tela_codigo_box(cx, cy, s)


# ---------------------------------------------------------------------------
# 2. Boneco (reusa pessoa da lib, com rotulo de papel opcional)
# ---------------------------------------------------------------------------
def boneco_autor(d, cx, cy, s=1.4, seed=0, frac=1.0, cor=AZUL_A, papel=None, cor_rotulo=None):
    """Boneco de palito colorido com rotulo de papel opcional embaixo ('escreve' / 'revisa e sugere')."""
    pessoa(d, cx, cy, s=s, seed=seed, frac=frac, cor=cor)
    if papel and frac >= 0.99:
        texto(d, cx, cy + 180 * s, papel, 44, cor_rotulo or cor)


def boneco_autor_box(cx, cy, s=1.4, papel=None):
    """Caixa do boneco (cabeca a pes). Se tiver rotulo, estende ate abaixo do texto."""
    top = cy - 146 * s          # topo da cabeca (circ raio 36 em cy-110)
    base = cy + 125 * s          # pes
    larg = 120 * s
    if papel:
        base = cy + 180 * s + 30
    return (cx - larg / 2, top, larg, base - top)


# ---------------------------------------------------------------------------
# 2b. Dupla pair (os dois bonecos, A azul a esquerda, B laranja a direita)
# ---------------------------------------------------------------------------
def dupla_pair(d, cx, cy, s=1.5, seed=0, frac=1.0, dist=200, papeis=None):
    """Par de bonecos. `papeis` = (rotulo_A, rotulo_B) opcional embaixo de cada um."""
    xa, xb = cx - dist / 2, cx + dist / 2
    ra, rb = (papeis or (None, None))
    boneco_autor(d, xa, cy, s=s, seed=seed, frac=frac, cor=AZUL_A, papel=ra)
    boneco_autor(d, xb, cy, s=s, seed=seed + 20, frac=frac, cor=LARANJA_B, papel=rb)


def dupla_pair_box(cx, cy, s=1.5, dist=200, papeis=None):
    xa, xb = cx - dist / 2, cx + dist / 2
    ra = (papeis or (None, None))[0]
    bax, bay, baw, bah = boneco_autor_box(xa, cy, s, ra)
    bbx, _, bbw, _ = boneco_autor_box(xb, cy, s, (papeis or (None, None))[1])
    x = bax
    w = (bbx + bbw) - bax
    return (x, bay, w, bah)


# ---------------------------------------------------------------------------
# 3. Caixa 'o mesmo problema'
# ---------------------------------------------------------------------------
def caixa_problema(d, cx, cy, s=1.0, seed=5, frac=1.0, linhas=("o mesmo", "problema")):
    w, h = 300 * s, 180 * s
    c = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    if frac >= 0.99:
        preencher(d, c, GELO)
    traco(d, c, seed, frac, w=7, amp=2, fechado=True)
    if frac >= 0.99:
        texto_multilinha(d, cx, cy - (len(linhas) - 1) * 46 * 0.62, list(linhas), 46)


def caixa_problema_box(cx, cy, s=1.0):
    w, h = 300 * s, 180 * s
    return (cx - w / 2, cy - h / 2, w, h)


# ---------------------------------------------------------------------------
# 4. Balao de fala (sem cauda, assinatura fixa deste video)
# ---------------------------------------------------------------------------
def balao_fala(d, cx, cy, linhas, larg=440, alt=190, seed=31, frac=1.0, tam=50, cor_borda=INK):
    """Balao com texto curto, sem cauda. cor_borda diferencia A/B."""
    x0, x1, y0, y1 = cx - larg / 2, cx + larg / 2, cy - alt / 2, cy + alt / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
    traco(d, c, seed, frac, w=6, amp=2, fechado=True, col=cor_borda)
    if frac >= 0.99:
        texto_multilinha(d, cx, cy - (len(linhas) - 1) * tam * 0.62, list(linhas), tam)


def balao_fala_box(cx, cy, larg=440, alt=190):
    return (cx - larg / 2, cy - alt / 2, larg, alt)


# ---------------------------------------------------------------------------
# 5. Teclado (quem escreve)
# ---------------------------------------------------------------------------
def teclado(d, cx, cy, s=1.0, seed=60, frac=1.0):
    c = [(cx - 85 * s, cy - 38 * s), (cx + 85 * s, cy - 38 * s), (cx + 85 * s, cy + 38 * s), (cx - 85 * s, cy + 38 * s)]
    if frac >= 0.99:
        preencher(d, c, GELO)
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if frac >= 0.99:
        for r in range(2):
            for k in range(5):
                preencher(d, circ(cx - 60 * s + k * 30 * s, cy - 12 * s + r * 28 * s, 5 * s, 8), INK)


def teclado_box(cx, cy, s=1.0):
    return (cx - 85 * s, cy - 38 * s, 170 * s, 76 * s)


# ---------------------------------------------------------------------------
# 6. Lupa (quem revisa e sugere)
# ---------------------------------------------------------------------------
def lupa_revisao(d, cx, cy, s=0.8, seed=61, frac=1.0):
    lupa(d, cx, cy, s=s, seed=seed, frac=frac)


def lupa_revisao_box(cx, cy, s=0.8):
    r = 60 * s
    cabo = r * 1.75
    # da ponta superior-esquerda do circulo ate a ponta do cabo (inferior-direita)
    x0 = cx - r
    y0 = cy - r
    x1 = cx + r * 1.75
    y1 = cy + r * 1.75
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------
# 7. Setas de troca de papel (ida e volta, uma de cada cor)
# ---------------------------------------------------------------------------
def setas_troca(d, cx, cy, s=1.0, seed=70, frac=1.0, dist=300):
    """Duas setas horizontais: a de cima azul (esq->dir), a de baixo laranja (dir->esq)."""
    esq, dirx = cx - dist / 2, cx + dist / 2
    seta(d, esq, cy - 35 * s, dirx, cy - 35 * s, seed=seed, frac=frac, cor=AZUL_A, w=7)
    seta(d, dirx, cy + 35 * s, esq, cy + 35 * s, seed=seed + 5, frac=frac, cor=LARANJA_B, w=7)


def setas_troca_box(cx, cy, s=1.0, dist=300):
    return (cx - dist / 2 - 44, cy - 35 * s - 44, dist + 88, 70 * s + 88)


# ---------------------------------------------------------------------------
# 8. Check de solucao em conjunto (check verde grande com brilho)
# ---------------------------------------------------------------------------
def check_solucao(im, d, cx, cy, s=2.4, seed=80, frac=1.0):
    """Desenha o check verde e devolve a imagem com o brilho somado."""
    check(d, cx, cy, s=s, seed=seed, frac=frac, cor=VERDE_OK)
    if frac >= 0.99:
        im = brilho(im, cx, cy, 150, VERDE_OK, k=0.35)
    return im


def check_solucao_box(cx, cy, s=2.4):
    # o check vai de (cx-50s, cy-45s) a (cx+55s, cy+40s)
    return (cx - 50 * s, cy - 45 * s, 105 * s, 85 * s)


# ---------------------------------------------------------------------------
# 9. Tres ganhos: contexto / conhecimento / decisao
#    FIX3: ganho_conhecimento com muito mais respiro entre as cabecas.
# ---------------------------------------------------------------------------
def ganho_contexto(d, cx, cy, s=1.0, seed=90, frac=1.0, rotulo="contexto"):
    """Dois circulos sobrepostos (interseccao = contexto compartilhado)."""
    traco(d, circ(cx - 40 * s, cy, 62 * s, 40), seed, frac, w=7, col=AZUL_A, fechado=True)
    traco(d, circ(cx + 40 * s, cy, 62 * s, 40), seed + 1, frac, w=7, col=LARANJA_B, fechado=True)
    if frac >= 0.99:
        texto(d, cx + 170 * s, cy, rotulo, 76, ancora="lm")


def ganho_conhecimento(d, cx, cy, s=1.0, seed=92, frac=1.0, rotulo="conhecimento"):
    """Duas cabecas com seta de ida e volta entre elas. FIX3: afasta as cabecas (70->100)
    e as setas ocupam o vao central inteiro, sem espremer."""
    dx = 100 * s   # FIX3: antes 70*s
    r = 40 * s
    traco(d, circ(cx - dx, cy, r, 32), seed, frac, w=7, col=AZUL_A, fechado=True)
    traco(d, circ(cx + dx, cy, r, 32), seed + 1, frac, w=7, col=LARANJA_B, fechado=True)
    if frac >= 0.99:
        # setas no vao entre as bordas internas (de cx-dx+r ate cx+dx-r)
        bi = cx - dx + r + 6
        bd = cx + dx - r - 6
        seta(d, bi, cy - 18 * s, bd, cy - 18 * s, seed=seed + 2, cor=AZUL_A, w=6)
        seta(d, bd, cy + 18 * s, bi, cy + 18 * s, seed=seed + 4, cor=LARANJA_B, w=6)
        texto(d, cx + dx + 90 * s, cy, rotulo, 76, ancora="lm")


def ganho_decisao(d, cx, cy, s=1.0, seed=97, frac=1.0, rotulo="decisao"):
    """Check dentro de um circulo verde."""
    traco(d, circ(cx, cy, 70 * s, 40), seed, frac, w=7, col=VERDE_OK, fechado=True)
    check(d, cx, cy, s=1.0 * s, seed=seed + 1, frac=frac, cor=VERDE_OK)
    if frac >= 0.99:
        texto(d, cx + 170 * s, cy, rotulo, 76, ancora="lm")


def _ganho_box(cx, cy, s, meia_largura_icone, rotulo, rot_x):
    """Caixa de um ganho: do icone (esq) ate o fim do texto (dir)."""
    larg_rot = len(rotulo) * 42 * s  # estimativa larga da fonte 76
    x0 = cx - meia_largura_icone
    x1 = rot_x + larg_rot
    r = 70 * s
    return (x0, cy - r - 6, x1 - x0, 2 * (r + 6))


def ganho_contexto_box(cx, cy, s=1.0, rotulo="contexto"):
    return _ganho_box(cx, cy, s, 40 * s + 62 * s, rotulo, cx + 170 * s)


def ganho_conhecimento_box(cx, cy, s=1.0, rotulo="conhecimento"):
    dx = 100 * s
    return _ganho_box(cx, cy, s, dx + 40 * s, rotulo, cx + dx + 90 * s)


def ganho_decisao_box(cx, cy, s=1.0, rotulo="decisao"):
    return _ganho_box(cx, cy, s, 70 * s, rotulo, cx + 170 * s)


# ---------------------------------------------------------------------------
# 10. Boneco pensando (fechamento, com ? pulsando)
# ---------------------------------------------------------------------------
def boneco_pensando(d, cx, cy, s=1.5, seed=14, frac=1.0, t=0.0):
    pessoa(d, cx, cy, s=s, seed=seed, frac=frac, cor=INK)
    if frac >= 0.99:
        texto(d, cx, cy - 240 * s, "?", int(130 * (1 + 0.1 * math.sin(t * 6))), LARANJA_B)


def boneco_pensando_box(cx, cy, s=1.5):
    # inclui o "?" acima da cabeca
    top = cy - 240 * s - 70 * s
    base = cy + 125 * s
    return (cx - 90 * s, top, 180 * s, base - top)
