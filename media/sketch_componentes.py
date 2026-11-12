"""Componentes reutilizaveis do canal (aprovados pelo Guilherme).

Cada funcao desenha UM componente, parametrizado por posicao, escala e `frac`
(progresso do traco). Importa a biblioteca-base do canal; mesmo estilo e paleta.
Os icones basicos (pessoa, lupa, check, cruz, seta, circ, traco, preencher...) e
as cores (INK, AZUL, LARANJA, VERDE, GELO) ja vivem em media/sketch_lib.py e NAO
sao duplicados aqui.

Cada componente tem uma funcao companheira `*_box(cx, cy, s, ...)` que devolve a
caixa ocupada como (x, y, w, h) com ancora no canto superior esquerdo. O Olise usa
as caixas para posicionar sem sobrepor boneco nem texto.

Convencao de cor: pessoa A = AZUL (escreve primeiro), pessoa B = LARANJA (revisa).
Verde = acerto/decisao. Vermelho = negacao.

Aprovados em 2026-10-30 (video pair-programming-colaboracao, sem correcoes).
Assinaturas identicas as da proposta original; nao alterar sem revalidar com o Guilherme.
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
    `cores`: lista de cores (uma por linha). `riscada`: desenha um X vermelho por cima."""
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
        cruz(d, cx, cy, s=2.9 * s, seed=seed + 50)


def tela_codigo_box(cx, cy, s=1.0):
    """Caixa da tela INCLUINDO o pe do monitor (para o Olise nao encostar nada nos pes)."""
    w, h = 560 * s, 380 * s
    return (cx - w / 2, cy - h / 2, w, h + 40 * s)


# ---------------------------------------------------------------------------
# 1b. Tela riscada (atalho nomeado)
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
    return (cx - 50 * s, cy - 45 * s, 105 * s, 85 * s)


# ---------------------------------------------------------------------------
# 9. Tres ganhos: contexto / conhecimento / decisao
# ---------------------------------------------------------------------------
def ganho_contexto(d, cx, cy, s=1.0, seed=90, frac=1.0, rotulo="contexto"):
    """Dois circulos sobrepostos (interseccao = contexto compartilhado)."""
    traco(d, circ(cx - 40 * s, cy, 62 * s, 40), seed, frac, w=7, col=AZUL_A, fechado=True)
    traco(d, circ(cx + 40 * s, cy, 62 * s, 40), seed + 1, frac, w=7, col=LARANJA_B, fechado=True)
    if frac >= 0.99:
        texto(d, cx + 170 * s, cy, rotulo, 76, ancora="lm")


def ganho_conhecimento(d, cx, cy, s=1.0, seed=92, frac=1.0, rotulo="conhecimento"):
    """Duas cabecas com seta de ida e volta entre elas."""
    dx = 100 * s
    r = 40 * s
    traco(d, circ(cx - dx, cy, r, 32), seed, frac, w=7, col=AZUL_A, fechado=True)
    traco(d, circ(cx + dx, cy, r, 32), seed + 1, frac, w=7, col=LARANJA_B, fechado=True)
    if frac >= 0.99:
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
    top = cy - 240 * s - 70 * s
    base = cy + 125 * s
    return (cx - 90 * s, top, 180 * s, base - top)


# ===========================================================================
# Video esquema-de-piramide (aprovado em 2026-10-31, "pode seguir", sem correcoes).
# Convencao de cor: AZUL=pessoa/multinivel legal; LARANJA=dinheiro em movimento/
# recrutamento; VERDE=produto real; VERMELHO=colapso/condenacao; SOL_AMARELO=moeda.
# Assinaturas identicas as da proposta; nao alterar sem revalidar com o Guilherme.
# ===========================================================================


# ---------------------------------------------------------------------------
# 11. Piramide de pessoas (degraus com bonequinhos; dinheiro sobe ao topo)
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
# 12. Pilha de dinheiro (notas empilhadas + cifrao) - o "topo" que ganha
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
# 13. Fonte de dinheiro: venda real x adesao (contraexemplo do multinivel legal)
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
# 14. Convite de confianca (boneco passando um envelope a outro)
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
# 15. Icone avestruz (fachada de um caso real)
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


# ---------------------------------------------------------------------------
# 16. Icone gado (boi) - fachada de um caso real
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 17. Icone bitcoin (moeda generica, sem logo de marca) - fachada cripto
# ---------------------------------------------------------------------------
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
# 18. Martelo de juiz (condenacao)
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
# 19. Caixa de caso (nome + ano + pena) - cartao resumo de um caso real
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
# 20. Pessoa x cifrao (pergunta de volta: confere a pessoa ou o dinheiro?)
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
