"""Componentes do video adultos-morando-com-os-pais (proposta do Raphinha, AGUARDANDO APROVACAO DO GUILHERME).

Cada funcao desenha UM componente, parametrizado por posicao (cx, cy), escala `s`, `seed` e `frac`
(progresso do traco; use `entra(lt, t0)`). Cada uma tem a companheira `*_box(...)` que devolve a caixa
ocupada (x, y, w, h), ancora no canto superior esquerdo, incluindo rotulos, pes, raios e caudas.

Convencao de cor deste video:
  AZUL      = o filho adulto / jovem (quem mora com os pais)
  INK       = os pais / neutro
  LARANJA   = custo, dinheiro, duvida ("?")
  VERMELHO  = rotulo riscado (negacao do estereotipo)
  SOL_AMARELO = alianca, moeda, lampada acesa (o contexto que ilumina)
  VERDE     = barra dos EUA (cor propria: nao comparar com as barras do Brasil)

Reusa da lib: pessoa, casa, moeda, relogio, seta, balao, circ, traco, preencher, brilho, texto.
Reusa do catalogo (media/sketch_componentes.py): boneco_pensando.
"""
import math

from media.sketch_lib import *

VERDE_OK = (60, 150, 90)
LARANJA_CLARO = (255, 222, 196)
BRANCO = (255, 255, 255)


# ---------------------------------------------------------------------------
# utilitario: caixa exata de um texto (mesma fonte Kalam do texto())
# ---------------------------------------------------------------------------
def caixa_texto(x, y, s, tam=50, ancora="mm", negrito=True):
    l, t, r, b = fonte(tam, negrito).getbbox(s, anchor=ancora)
    return (x + l, y + t, r - l, b - t)


def _uniao(*caixas):
    x0 = min(c[0] for c in caixas)
    y0 = min(c[1] for c in caixas)
    x1 = max(c[0] + c[2] for c in caixas)
    y1 = max(c[1] + c[3] for c in caixas)
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------
# 1. Casa da familia: casa + pai (tinta) e filho adulto (azul) do lado da porta
# ---------------------------------------------------------------------------
def casa_familia(d, cx, cy, s=1.0, seed=0, frac=1.0):
    """Casa a esquerda (com janela) e dois bonecos adultos em pe ao lado, no mesmo chao.
    O boneco tinta e o pai/mae; o azul e o filho adulto. Os bonecos ficam FORA da casa (nada os cobre)."""
    hx = cx - 130 * s
    casa(d, hx, cy, s=s, seed=seed, frac=frac)
    # janela
    j = [(hx + 45 * s, cy - 5 * s), (hx + 85 * s, cy - 5 * s), (hx + 85 * s, cy + 35 * s), (hx + 45 * s, cy + 35 * s)]
    if frac >= 0.99:
        preencher(d, j, GELO)
    traco(d, j, seed + 3, frac, w=4, amp=1.2 * s, fechado=True)
    # chao
    traco(d, [(hx - 150 * s, cy + 100 * s), (cx + 240 * s, cy + 100 * s)], seed + 4, frac, w=5, amp=1.5 * s)
    # bonecos (pes no chao): pessoa tem pes em cy+125*sb
    sb = 0.75 * s
    by = cy + 100 * s - 125 * sb
    pessoa(d, cx + 60 * s, by, s=sb, seed=seed + 10, frac=frac, cor=INK)
    pessoa(d, cx + 170 * s, by, s=sb, seed=seed + 30, frac=frac, cor=AZUL)


def casa_familia_box(cx, cy, s=1.0):
    hx = cx - 130 * s
    sb = 0.75 * s
    by = cy + 100 * s - 125 * sb
    x0 = hx - 150 * s
    x1 = cx + 240 * s
    y0 = min(cy - 135 * s, by - 146 * sb)
    y1 = cy + 106 * s
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------
# 2. Etiqueta riscada: etiqueta de papel com uma palavra e um risco vermelho
# ---------------------------------------------------------------------------
def etiqueta_riscada(d, cx, cy, palavra, s=1.0, seed=0, frac=1.0, risco=1.0, tam=78):
    """Etiqueta (tag com furo) com `palavra`; `risco` (0..1) desenha o risco vermelho por cima.
    O risco e fino e inclinado: a palavra continua legivel (e o rotulo sendo negado)."""
    tm = int(tam * s)
    _, _, tw, th = caixa_texto(0, 0, palavra, tm)
    w = tw + 120 * s
    h = max(th + 50 * s, 110 * s)
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    c = [(x0 + 40 * s, y0), (x1, y0), (x1, y1), (x0 + 40 * s, y1), (x0, cy)]
    if frac >= 0.99:
        preencher(d, c, BRANCO)
    traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
    traco(d, circ(x0 + 42 * s, cy, 9 * s, 14), seed + 1, frac, w=4, amp=1, fechado=True)
    if frac >= 0.99:
        tx = cx + 20 * s
        texto(d, tx, cy, palavra, tm)
        if risco > 0:
            traco(d, [(tx - tw / 2 - 20 * s, cy + 14 * s), (tx + tw / 2 + 20 * s, cy - 10 * s)],
                  seed + 2, risco, w=max(4, int(7 * s)), amp=1.5, col=VERMELHO)


def etiqueta_riscada_box(cx, cy, palavra, s=1.0, tam=78):
    tm = int(tam * s)
    _, _, tw, th = caixa_texto(0, 0, palavra, tm)
    w = tw + 120 * s
    h = max(th + 50 * s, 110 * s)
    return (cx - w / 2 - 4, cy - h / 2 - 4, w + 8, h + 8)


# ---------------------------------------------------------------------------
# 3. Grafico com lacuna: barras com ano + uma barra tracejada "?" (dado que nao existe)
# ---------------------------------------------------------------------------
def _barra(d, cx, y_base, larg, h, cor, txt, rot, seed, sub=None):
    if h > 4:
        b = [(cx - larg / 2, y_base), (cx - larg / 2, y_base - h), (cx + larg / 2, y_base - h), (cx + larg / 2, y_base)]
        preencher(d, b, cor)
        traco(d, b, seed, 1.0, w=6, amp=2, fechado=True)
        if txt:
            texto(d, cx, y_base - h - 44, txt, 58)
    if rot:
        texto(d, cx, y_base + 52, rot, 46)
    if sub:
        texto(d, cx, y_base + 106, sub, 40, (90, 90, 100))


def barra_lacuna(d, cx, y_base, larg=180, alt=500, s=1.0, rotulo="hoje", seed=0, frac=1.0):
    """Barra so com contorno tracejado e um '?' laranja: o dado que nao temos."""
    x0, x1, y0 = cx - larg / 2, cx + larg / 2, y_base - alt
    lados = [((x0, y_base), (x0, y0)), ((x0, y0), (x1, y0)), ((x1, y0), (x1, y_base))]
    k = 0
    for (ax, ay), (bx, by) in lados:
        comp = math.dist((ax, ay), (bx, by))
        n = int(comp // 44)
        for i in range(n):
            t0, t1 = i / n, (i + 0.55) / n
            if (k + i) / 40 > frac:
                break
            traco(d, [(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)],
                  seed + k + i, 1.0, w=5, amp=1.2, col=FERRO)
        k += n
    if frac >= 0.99:
        texto(d, cx, y_base - alt / 2, "?", int(120 * s), LARANJA)
        if rotulo:
            texto(d, cx, y_base + 52, rotulo, 46, LARANJA)


def barra_lacuna_box(cx, y_base, larg=180, alt=500, s=1.0, rotulo="hoje"):
    caixas = [(cx - larg / 2 - 4, y_base - alt - 4, larg + 8, alt + 8)]
    if rotulo:
        caixas.append(caixa_texto(cx, y_base + 52, rotulo, 46))
    return _uniao(*caixas)


def grafico_lacuna(d, cx, y_base, itens, lacuna="hoje", alt_max=500, larg=180, passo=280,
                   seed=0, lt=99.0, t0=0.0, seta_subida=True):
    """Barras que crescem em sequencia (itens = [{"rotulo","valor","texto","cor"}]) + a barra-lacuna no fim.
    `seta_subida`: seta curta entre o topo da 1a e da 2a barra. A barra-lacuna tem a altura da ultima barra."""
    n = len(itens) + (1 if lacuna else 0)
    xs = [cx - (n - 1) * passo / 2 + k * passo for k in range(n)]
    esc = max(i["valor"] for i in itens)
    traco(d, [(xs[0] - larg / 2 - 40, y_base), (xs[-1] + larg / 2 + 40, y_base)], seed, entra(lt, t0, 0.5), w=7)
    alturas = []
    for k, it in enumerate(itens):
        f = entra(lt, t0 + 0.25 + k * 0.35, 0.7)
        h = alt_max * it["valor"] / esc
        alturas.append(h)
        _barra(d, xs[k], y_base, larg, h * f, it.get("cor", AZUL), it.get("texto") if f > 0.95 else None,
               it.get("rotulo"), seed + 7 + k)
    t_fim = t0 + 0.25 + len(itens) * 0.35 + 0.4
    if seta_subida and len(itens) >= 2 and lt >= t_fim:
        xa = xs[0] + larg / 2 + 14
        xb = xs[1] - larg / 2 - 14
        ya = y_base - alturas[0] + 20
        yb = y_base - alturas[1] + 50
        seta(d, xa, ya, xb, yb, seed=seed + 40, frac=entra(lt, t_fim, 0.4), cor=LARANJA, w=7)
    if lacuna:
        barra_lacuna(d, xs[-1], y_base, larg, alturas[-1], rotulo=lacuna, seed=seed + 60,
                     frac=entra(lt, t_fim + 0.3, 0.6))


def grafico_lacuna_box(cx, y_base, itens, lacuna="hoje", alt_max=500, larg=180, passo=280):
    n = len(itens) + (1 if lacuna else 0)
    xs = [cx - (n - 1) * passo / 2 + k * passo for k in range(n)]
    esc = max(i["valor"] for i in itens)
    caixas = [(xs[0] - larg / 2 - 44, y_base - 6, xs[-1] - xs[0] + larg + 88, 12)]
    for k, it in enumerate(itens):
        h = alt_max * it["valor"] / esc
        caixas.append((xs[k] - larg / 2 - 4, y_base - h - 4, larg + 8, h + 8))
        caixas.append(caixa_texto(xs[k], y_base - h - 44, it.get("texto", ""), 58))
        caixas.append(caixa_texto(xs[k], y_base + 52, it.get("rotulo", ""), 46))
    if lacuna:
        h = alt_max * itens[-1]["valor"] / esc
        caixas.append(barra_lacuna_box(xs[-1], y_base, larg, h, rotulo=lacuna))
    return _uniao(*caixas)


# ---------------------------------------------------------------------------
# 4. Barra unica com rotulo e sub-rotulo (dado isolado, sem comparacao)
# ---------------------------------------------------------------------------
def barra_unica(d, cx, y_base, txt, rotulo, sub=None, alt=520, larg=200, cor=VERDE, seed=0, lt=99.0, t0=0.0):
    traco(d, [(cx - larg / 2 - 60, y_base), (cx + larg / 2 + 60, y_base)], seed, entra(lt, t0, 0.5), w=7)
    f = entra(lt, t0 + 0.25, 0.8)
    _barra(d, cx, y_base, larg, alt * f, cor, txt if f > 0.95 else None, rotulo, seed + 7, sub)


def barra_unica_box(cx, y_base, txt, rotulo, sub=None, alt=520, larg=200):
    caixas = [(cx - larg / 2 - 64, y_base - alt - 4, larg + 128, alt + 10),
              caixa_texto(cx, y_base - alt - 44, txt, 58),
              caixa_texto(cx, y_base + 52, rotulo, 46)]
    if sub:
        caixas.append(caixa_texto(cx, y_base + 106, sub, 38))
    return _uniao(*caixas)


# ---------------------------------------------------------------------------
# 5. Icone livro aberto (estudo)
# ---------------------------------------------------------------------------
def icone_livro(d, cx, cy, s=1.0, seed=0, frac=1.0):
    w, h = 110 * s, 140 * s
    esq = [(cx, cy - h / 2 + 12 * s), (cx - w, cy - h / 2), (cx - w, cy + h / 2), (cx, cy + h / 2 + 12 * s)]
    dir_ = [(cx, cy - h / 2 + 12 * s), (cx + w, cy - h / 2), (cx + w, cy + h / 2), (cx, cy + h / 2 + 12 * s)]
    if frac >= 0.99:
        preencher(d, esq, BRANCO)
        preencher(d, dir_, GELO)
    traco(d, esq, seed, frac, w=6, amp=2 * s, fechado=True)
    traco(d, dir_, seed + 1, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        for i in range(4):
            y = cy - h / 2 + 34 * s + i * 26 * s
            traco(d, [(cx - w + 20 * s, y), (cx - 18 * s, y + 6 * s)], seed + 5 + i, 1.0, w=3, amp=1, col=FERRO)
            traco(d, [(cx + 18 * s, y + 6 * s), (cx + w - 20 * s, y)], seed + 9 + i, 1.0, w=3, amp=1, col=FERRO)


def icone_livro_box(cx, cy, s=1.0):
    w, h = 110 * s, 140 * s
    return (cx - w - 4, cy - h / 2 - 4, 2 * w + 8, h + 20 * s + 4)


# ---------------------------------------------------------------------------
# 6. Custo de moradia (casinha + moeda ao lado)
# ---------------------------------------------------------------------------
def custo_moradia(d, cx, cy, s=1.0, seed=0, frac=1.0):
    casa(d, cx - 55 * s, cy, s=0.62 * s, seed=seed, frac=frac, cor=LARANJA_CLARO)
    moeda(d, cx + 95 * s, cy + 30 * s, s=0.62 * s, seed=seed + 5, frac=frac)


def custo_moradia_box(cx, cy, s=1.0):
    x0 = cx - 55 * s - 125 * 0.62 * s - 4
    x1 = cx + 95 * s + 70 * 0.62 * s + 4
    y0 = cy - 130 * 0.62 * s - 4
    y1 = cy + 100 * 0.62 * s + 4
    y1 = max(y1, cy + 30 * s + 70 * 0.62 * s + 4)
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------
# 7. Aliancas (casamento): duas aliancas douradas entrelacadas
# ---------------------------------------------------------------------------
def _anel(d, cx, cy, r, esp, seed, frac):
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOL_AMARELO)
        d.ellipse([cx - r + esp, cy - r + esp, cx + r - esp, cy + r - esp], fill=PAPEL)
    traco(d, circ(cx, cy, r, 40), seed, frac, w=5, amp=1.5, fechado=True)
    traco(d, circ(cx, cy, r - esp, 34), seed + 1, frac, w=4, amp=1.2, fechado=True)


def icone_alianca(d, cx, cy, s=1.0, seed=0, frac=1.0):
    r, esp = 58 * s, 16 * s
    _anel(d, cx - 36 * s, cy, r, esp, seed, frac)
    _anel(d, cx + 36 * s, cy, r, esp, seed + 3, frac)
    if frac >= 0.99:
        # entrelace: o anel da esquerda passa por cima do da direita num trecho
        a0, a1 = -0.75, 0.75
        pts_o = [(cx - 36 * s + r * math.cos(a), cy + r * math.sin(a)) for a in [a0 + (a1 - a0) * k / 10 for k in range(11)]]
        pts_i = [(cx - 36 * s + (r - esp) * math.cos(a), cy + (r - esp) * math.sin(a)) for a in [a1 - (a1 - a0) * k / 10 for k in range(11)]]
        preencher(d, pts_o + pts_i, SOL_AMARELO)
        traco(d, pts_o, seed + 7, 1.0, w=5, amp=1.2)
        traco(d, pts_i, seed + 8, 1.0, w=4, amp=1.0)


def icone_alianca_box(cx, cy, s=1.0):
    r = 58 * s
    return (cx - 36 * s - r - 4, cy - r - 4, 72 * s + 2 * r + 8, 2 * r + 8)


# ---------------------------------------------------------------------------
# 8. Alianca + relogio de pulso (casamento adiado)
# ---------------------------------------------------------------------------
def alianca_relogio(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0):
    icone_alianca(d, cx - 110 * s, cy, s=0.95 * s, seed=seed, frac=frac)
    rx = cx + 120 * s
    # pulseira (em cima e embaixo do mostrador)
    for sg in (-1, 1):
        p = [(rx - 34 * s, cy + sg * 62 * s), (rx + 34 * s, cy + sg * 62 * s),
             (rx + 30 * s, cy + sg * 130 * s), (rx - 30 * s, cy + sg * 130 * s)]
        if frac >= 0.99:
            preencher(d, p, (190, 150, 110))
        traco(d, p, seed + 20 + sg, frac, w=5, amp=1.5, fechado=True)
    relogio(d, rx, cy, s=0.85 * s, seed=seed + 30, frac=frac, t=t)


def alianca_relogio_box(cx, cy, s=1.0):
    a = icone_alianca_box(cx - 110 * s, cy, 0.95 * s)
    r = (cx + 120 * s - 70 * s, cy - 134 * s, 140 * s, 268 * s)
    return _uniao(a, r)


# ---------------------------------------------------------------------------
# 9. Regua de idades: linha de 20 a 32 anos com marcadores (numero em cima, lugar embaixo)
# ---------------------------------------------------------------------------
MARCAS_UE = [(21.4, "21,4", "Finlândia", AZUL), (26.2, "26,2", "média UE", INK), (30.1, "30,1", "Itália", LARANJA)]


def regua_x(cx, valor, s=1.0, ini=20, fim=32, larg=800):
    L = larg * s
    return cx - L / 2 + (valor - ini) / (fim - ini) * L


def _regua_pos(cy, s, abaixo):
    """Posicoes verticais do pino, numero e lugar. `abaixo=True`: tudo embaixo da linha (o boneco anda em cima)."""
    if abaixo:
        return (cy + 16 * s, cy + 58 * s), cy + 108 * s, cy + 178 * s
    return (cy - 16 * s, cy - 58 * s), cy - 100 * s, cy + 58 * s


def regua_idades(d, cx, cy, s=1.0, marcas=None, ini=20, fim=32, larg=800, seed=0, frac=1.0, n_marcas=None,
                 tam_num=56, tam_lugar=42, abaixo=False):
    """Regua horizontal (anos). `marcas` = [(valor, "texto do numero", "lugar" ou None, cor)].
    `n_marcas` limita quantas marcas aparecem (para entrar uma por vez).
    `abaixo=False`: numero em cima, lugar embaixo. `abaixo=True`: pino, numero e lugar embaixo da linha,
    deixando a linha livre para um boneco andar em cima dela."""
    marcas = MARCAS_UE if marcas is None else marcas
    L = larg * s
    x0 = cx - L / 2
    traco(d, [(x0, cy), (x0 + L, cy)], seed, frac, w=7, amp=1.5)
    if frac < 0.99:
        return
    for k, ano in enumerate(range(ini, fim + 1)):
        x = regua_x(cx, ano, s, ini, fim, larg)
        alto = 22 * s if ano % 5 == 0 else 12 * s
        traco(d, [(x, cy - alto), (x, cy + alto)], seed + 3 + k, 1.0, w=4, amp=0.8)
    (yp, yb), ynum, ylug = _regua_pos(cy, s, abaixo)
    for k, (v, num, lugar, cor) in enumerate(marcas[: (len(marcas) if n_marcas is None else n_marcas)]):
        x = regua_x(cx, v, s, ini, fim, larg)
        tri = [(x - 18 * s, yb), (x + 18 * s, yb), (x, yp)]  # pino apontando para a linha
        preencher(d, tri, cor)
        traco(d, tri, seed + 40 + k, 1.0, w=4, amp=1, fechado=True)
        texto(d, x, ynum, num, int(tam_num * s), cor)
        if lugar:
            texto(d, x, ylug, lugar, int(tam_lugar * s), INK)


def regua_idades_linha_box(cx, cy, s=1.0, larg=800):
    """So a linha com os tracinhos (pode ser pisada por um boneco)."""
    L = larg * s
    return (cx - L / 2 - 4, cy - 26 * s, L + 8, 52 * s)


def regua_idades_rotulos_box(cx, cy, s=1.0, marcas=None, ini=20, fim=32, larg=800, tam_num=56, tam_lugar=42,
                             abaixo=False):
    """So os pinos + numeros + lugares (texto: nada pode cobrir)."""
    marcas = MARCAS_UE if marcas is None else marcas
    (yp, yb), ynum, ylug = _regua_pos(cy, s, abaixo)
    caixas = []
    for v, num, lugar, cor in marcas:
        x = regua_x(cx, v, s, ini, fim, larg)
        caixas.append((x - 20 * s, min(yp, yb), 40 * s, abs(yb - yp)))
        caixas.append(caixa_texto(x, ynum, num, int(tam_num * s)))
        if lugar:
            caixas.append(caixa_texto(x, ylug, lugar, int(tam_lugar * s)))
    return _uniao(*caixas)


def regua_idades_box(cx, cy, s=1.0, marcas=None, ini=20, fim=32, larg=800, tam_num=56, tam_lugar=42, abaixo=False):
    return _uniao(regua_idades_linha_box(cx, cy, s, larg),
                  regua_idades_rotulos_box(cx, cy, s, marcas, ini, fim, larg, tam_num, tam_lugar, abaixo))


# ---------------------------------------------------------------------------
# 10. Boneco andando (pernas e bracos balancam com `fase`)
# ---------------------------------------------------------------------------
def boneco_andando(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=AZUL, fase=0.0):
    """Igual ao `pessoa` da lib, mas com passada. Use fase = lt * 9 enquanto anda; fase fixa quando para."""
    sk = lambda pts, sd: traco(d, pts, seed + sd, frac, w=6, amp=2.5 * s, col=cor)
    p = 32 * s * math.sin(fase)
    sk(circ(cx, cy - 110 * s, 36 * s, 36), 1)
    sk([(cx, cy - 74 * s), (cx, cy + 40 * s)], 2)
    sk([(cx, cy - 40 * s), (cx - 40 * s - p, cy + 10 * s)], 3)
    sk([(cx, cy - 40 * s), (cx + 40 * s + p, cy + 10 * s)], 4)
    sk([(cx, cy + 40 * s), (cx + p, cy + 125 * s)], 5)
    sk([(cx, cy + 40 * s), (cx - p, cy + 125 * s)], 6)


def boneco_andando_box(cx, cy, s=1.0, x_fim=None):
    """Com `x_fim`, a caixa cobre todo o trajeto de cx ate x_fim."""
    xa, xb = (cx, cx) if x_fim is None else (min(cx, x_fim), max(cx, x_fim))
    return (xa - 75 * s, cy - 150 * s, xb - xa + 150 * s, 280 * s)


# ---------------------------------------------------------------------------
# 11. Lampada (acende: contexto explica)
# ---------------------------------------------------------------------------
def lampada(im, d, cx, cy, s=1.0, seed=0, frac=1.0, acesa=1.0, t=0.0):
    """Lampada com rosca. `acesa` 0..1 pinta o bulbo, soma brilho e solta raios que pulsam com `t`.
    Recebe e DEVOLVE `im` (por causa do brilho); redesenhe com o ImageDraw do retorno."""
    bx, by, r = cx, cy - 30 * s, 80 * s
    if acesa > 0.5 and frac >= 0.99:
        im = brilho(im, bx, by, 150 * s, SOL_AMARELO, k=0.3 * acesa)
        d = ImageDraw.Draw(im)
    bulbo = circ(bx, by, r, 44)
    if frac >= 0.99:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=SOL_AMARELO if acesa > 0.5 else BRANCO)
    traco(d, bulbo, seed, frac, w=6, amp=2 * s, fechado=True)
    # rosca
    base = [(cx - 38 * s, cy + 46 * s), (cx + 38 * s, cy + 46 * s), (cx + 34 * s, cy + 112 * s), (cx - 34 * s, cy + 112 * s)]
    if frac >= 0.99:
        preencher(d, base, FERRO)
    traco(d, base, seed + 1, frac, w=6, amp=1.5, fechado=True)
    if frac >= 0.99:
        for k in range(2):
            y = cy + 68 * s + k * 22 * s
            traco(d, [(cx - 36 * s, y), (cx + 36 * s, y)], seed + 2 + k, 1.0, w=4, amp=1)
        traco(d, [(cx - 16 * s, cy + 112 * s), (cx, cy + 132 * s), (cx + 16 * s, cy + 112 * s)], seed + 5, 1.0, w=5, amp=1)
        # filamento: duas hastes e uma molinha no meio
        traco(d, [(cx - 20 * s, cy + 46 * s), (cx - 20 * s, by + 14 * s)], seed + 6, 1.0, w=4, amp=0.8)
        traco(d, [(cx + 20 * s, cy + 46 * s), (cx + 20 * s, by + 14 * s)], seed + 7, 1.0, w=4, amp=0.8)
        mola_pts = [(cx - 20 * s + 40 * s * k / 24, by + 14 * s - 9 * s * math.sin(k / 24 * 4 * math.tau)) for k in range(25)]
        d.line(mola_pts, fill=INK, width=4, joint="curve")
        if acesa > 0.5:
            for k in range(9):
                a = -math.pi + (k + 0.5) / 9 * math.pi  # leque de raios para cima
                r0 = r + 22 * s
                r1 = r0 + (34 + 10 * math.sin(t * 5 + k)) * s
                traco(d, [(bx + r0 * math.cos(a), by + r0 * math.sin(a)), (bx + r1 * math.cos(a), by + r1 * math.sin(a))],
                      seed + 20 + k, 1.0, w=5, amp=1, col=(200, 140, 20))
    return im


def lampada_box(cx, cy, s=1.0):
    r = 80 * s
    top = cy - 30 * s - r - 22 * s - 44 * s
    return (cx - r - 66 * s, top, 2 * r + 132 * s, cy + 136 * s - top)


# ---------------------------------------------------------------------------
# 12. Duas portas (pergunta de volta: escolha ou conta)
# ---------------------------------------------------------------------------
def duas_portas(d, cx, cy, s=1.0, seed=0, frac=1.0, rotulos=("escolha", "conta"), cores=(AZUL, LARANJA),
                fundos=(GELO, LARANJA_CLARO), dist=340, tam=58):
    """Duas portas lado a lado com placa em cima. Nenhum dos lados vem destacado (sem resposta pronta)."""
    w, h = 200 * s, 320 * s
    for k, sg in enumerate((-1, 1)):
        x = cx + sg * dist * s / 2
        p = [(x - w / 2, cy + h / 2), (x - w / 2, cy - h / 2), (x + w / 2, cy - h / 2), (x + w / 2, cy + h / 2)]
        if frac >= 0.99:
            preencher(d, p, fundos[k])
        traco(d, p, seed + 10 * k, frac, w=7, amp=2 * s, col=INK)
        if frac >= 0.99:
            # batente interno e macaneta
            q = [(x - w / 2 + 22 * s, cy + h / 2), (x - w / 2 + 22 * s, cy - h / 2 + 22 * s),
                 (x + w / 2 - 22 * s, cy - h / 2 + 22 * s), (x + w / 2 - 22 * s, cy + h / 2)]
            traco(d, q, seed + 10 * k + 1, 1.0, w=4, amp=1.2, col=cores[k])
            mx = x + sg * (-1) * (w / 2 - 44 * s)
            d.ellipse([mx - 10 * s, cy - 10 * s, mx + 10 * s, cy + 10 * s], fill=INK)
            texto(d, x, cy - h / 2 - 50 * s, rotulos[k], int(tam * s), cores[k])
    traco(d, [(cx - dist * s / 2 - w / 2 - 40 * s, cy + h / 2), (cx + dist * s / 2 + w / 2 + 40 * s, cy + h / 2)],
          seed + 30, frac, w=5, amp=1.5)


def duas_portas_box(cx, cy, s=1.0, rotulos=("escolha", "conta"), dist=340, tam=58):
    w, h = 200 * s, 320 * s
    caixas = [(cx - dist * s / 2 - w / 2 - 44 * s, cy - h / 2 - 4, dist * s + w + 88 * s, h + 10)]
    for k, sg in enumerate((-1, 1)):
        x = cx + sg * dist * s / 2
        caixas.append(caixa_texto(x, cy - h / 2 - 50 * s, rotulos[k], int(tam * s)))
    return _uniao(*caixas)
