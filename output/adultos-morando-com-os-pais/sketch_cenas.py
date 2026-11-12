"""Cenas do adultos-morando-com-os-pais (componentes do Raphinha aprovados pelo Guilherme).

Fonte das posicoes/escalas: componentes.md (layout_cenas() de gerar_componentes.py).
Componentes do video: componentes_video.py (nesta pasta). Catalogo: media/sketch_componentes.py.
Convencao de cor: AZUL=filho adulto/2012; INK=pais/neutro/media UE; LARANJA=custo, duvida, Italia;
VERMELHO=so o risco sobre o rotulo; dourado=aliancas, lampada, "o contexto explica"; VERDE=barra dos EUA.

Regras: nada cobre boneco nem texto (exceto o risco vermelho aprovado; o boneco pisa a linha da regua
na cena 2, aprovado); tudo entre SEGURO_TOPO e SEGURO_BASE; sem legenda na base; sem nome de instituto
na tela; Brasil, UE e EUA nunca no mesmo grafico. Os tempos de entrada sao fracoes de `dur`, para
acompanhar a fala qualquer que seja a duracao real da narracao.
"""
import importlib.util
import math
import os

from PIL import ImageDraw
from media.sketch_lib import *
from media.sketch_componentes import boneco_pensando

_AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("componentes_video_adultos", os.path.join(_AQUI, "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

DOURADO = (200, 140, 20)
CINZA = (90, 90, 100)
AZUL_CLARO = (160, 195, 235)


def _txt_mola(d, x, y, s, tam, cor, lt, t0):
    """Texto que entra com estouro (mola) a partir de t0."""
    k = mola(lt, t0)
    if k > 0.05:
        texto(d, x, y, s, max(10, int(tam * k)), cor)


def _parcial(lt, t0=0.0, dur=0.5, minimo=0.35):
    """Contorno ja comecado no quadro 0 (nada de papel em branco) e completo em `dur` s."""
    return minimo + (1 - minimo) * entra(lt, t0, dur)


# ---------------------------------------------------------------------------
# CENA 0 - gancho: "preguica?" riscada + casa com pai e filho adulto + balao "?"
# ---------------------------------------------------------------------------
def cena_0(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    t_risco = 0.58 * dur  # "Os dados apontam outra explicacao"
    s_et = pulso(lt, vel=2.0, amp=0.03) if lt < t_risco else 1.0
    C.etiqueta_riscada(d, 540, 420, "preguiça?", s=s_et, seed=11, frac=1.0,
                       risco=entra(lt, t_risco, 0.45), tam=100)
    C.casa_familia(d, 560, 1250, s=1.85, seed=20, frac=_parcial(lt, 0.0, 0.6))
    k = mola(lt, 0.25)
    if k > 0.05:
        balao(d, 870, 790, 230 * k, 170 * k, ["?"], seed=50, frac=1.0,
              tam=max(10, int(110 * k * pulso(lt, vel=2.5, amp=0.08))))
    return im


# ---------------------------------------------------------------------------
# CENA 1 - Brasil (25 a 34 anos): 2002 20% -> 2012 24%, "via imprensa" e a barra-lacuna "hoje" com "?"
# ---------------------------------------------------------------------------
def cena_1(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 290, "Brasil", 76)
    texto(d, 540, 378, "jovens de 25 a 34 anos", 54, CINZA)
    yb, larg, alt_max = 1330, 210, 700
    xs = [240, 540, 840]
    traco(d, [(xs[0] - larg / 2 - 40, yb), (xs[-1] + larg / 2 + 40, yb)], 30, _parcial(lt, 0.0, 0.5), w=7)
    h02 = alt_max * 20 / 24
    # 2002 ("vinte por cento dos jovens ... em dois mil e dois")
    f02 = entra(lt, 0.04 * dur, 0.7)
    if f02 > 0:
        C._barra(d, xs[0], yb, larg, h02 * f02, AZUL_CLARO, "20%" if f02 > 0.95 else None, "2002", 38)
    # 2012 ("Em dois mil e doze, vinte e quatro por cento")
    t12 = 0.45 * dur
    f12 = entra(lt, t12, 0.7)
    if f12 > 0:
        C._barra(d, xs[1], yb, larg, alt_max * f12, AZUL, "24%" if f12 > 0.95 else None, "2012", 37)
    # seta curta de subida, entre os topos (depois das duas barras)
    fs = entra(lt, t12 + 0.75, 0.4)
    if fs > 0:
        seta(d, xs[0] + larg / 2 + 14, yb - h02 + 20, xs[1] - larg / 2 - 14, yb - alt_max + 50,
             seed=70, frac=fs, cor=LARANJA, w=7)
    # ressalva "Dado do IBGE, via imprensa" (sem nome do instituto na tela), sob os anos das barras reais
    _txt_mola(d, (xs[0] + xs[1]) / 2, 1440, "via imprensa", 44, CINZA, lt, 0.74 * dur)
    # lacuna "hoje" ("Nao vale para hoje")
    fl = entra(lt, 0.87 * dur, 0.5)
    if fl > 0:
        C.barra_lacuna(d, xs[2], yb, larg, alt_max, s=pulso(lt, vel=2.5, amp=0.08), rotulo="hoje", seed=90, frac=fl)
    return im


# ---------------------------------------------------------------------------
# CENA 2 - UE: regua de idades (rotulos embaixo) e boneco andando EM CIMA da linha
# ---------------------------------------------------------------------------
_MARCAS_FALA = [C.MARCAS_UE[1], C.MARCAS_UE[0], C.MARCAS_UE[2]]  # ordem da fala: 26,2 -> 21,4 -> 30,1


def cena_2(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 290, "idade ao sair de casa", 70)
    texto(d, 540, 375, "em 2024", 54, CINZA)
    yr, sr, sb = 1180, 1.1, 1.8
    cues = [0.31 * dur, 0.66 * dur, 0.86 * dur]  # 26,2 / Finlandia / Italia
    n = sum(1 for c in cues if lt >= c)
    C.regua_idades(d, 540, yr, s=sr, marcas=_MARCAS_FALA, seed=600, frac=_parcial(lt, 0.0, 0.5, 0.3),
                   n_marcas=n, tam_num=62, tam_lugar=48, abaixo=True)
    xa, xm, xi = (C.regua_x(540, v, sr) for v in (21.4, 26.2, 30.1))
    yb = yr - 6 - 125 * sb  # pes pisando a linha
    if lt < cues[0]:
        p = lt / cues[0]
        x, fase = xa + (xm - xa) * p, lt * 6
    elif lt < cues[2]:
        x, fase = xm, 0.35 * math.sin(lt * 2.5)
    else:
        p = entra(lt, cues[2], 1.0)
        x = xm + (xi - xm) * p
        fase = lt * 9 if p < 0.99 else 0.35 * math.sin(lt * 2.5)
    C.boneco_andando(d, x, yb, s=sb, seed=650, frac=1.0, cor=AZUL, fase=fase)
    return im


# ---------------------------------------------------------------------------
# CENA 3 - "nossa leitura": regua mini, "rotulo" riscado, lampada acende
# ---------------------------------------------------------------------------
_MARCAS_SO_NUM = [(v, num, None, cor) for v, num, _, cor in C.MARCAS_UE]


def cena_3(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 238, "nossa leitura", 56, CINZA)
    # "mesma epoca, paises diferentes, idades diferentes": regua mini, marcas uma a uma
    fr = entra(lt, 0.12 * dur, 0.4)
    if fr > 0:
        n = sum(1 for c in (0.22, 0.30, 0.38) if lt >= c * dur)
        C.regua_idades(d, 540, 1370, s=0.9, marcas=_MARCAS_SO_NUM, seed=700, frac=fr, n_marcas=n, tam_num=62)
    # "O rotulo nao explica"
    t_et = 0.52 * dur
    fe = entra(lt, t_et, 0.25)
    if fe > 0:
        C.etiqueta_riscada(d, 540, 370, "rótulo", s=1.0, seed=710, frac=fe,
                           risco=entra(lt, 0.68 * dur, 0.4), tam=92)
    # "O contexto explica": a lampada acende
    t_luz = 0.84 * dur
    im = C.lampada(im, d, 540, 790, s=1.7, seed=720, frac=_parcial(lt, 0.0, 0.7, 0.3),
                   acesa=entra(lt, t_luz, 0.3), t=lt)
    d = ImageDraw.Draw(im)
    _txt_mola(d, 540, 1120, "o contexto explica", 74, DOURADO, lt, t_luz + 0.1)
    return im


# ---------------------------------------------------------------------------
# CENA 4 - virada "nao e so dinheiro" (moeda + ?) e, em seguida, EUA 2014: barra unica 32,1%
#          (18 a 34 anos) e, em "casamento adiado", alianca + relogio
# ---------------------------------------------------------------------------
def cena_4(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    t_eua = 0.18 * dur  # "Nos Estados Unidos"
    # parte 1: a virada. Tudo sai (encolhe) antes de a barra entrar: nada cobre texto.
    sai = 1 - entra(lt, t_eua - 0.3, 0.3)
    if sai > 0.02:
        texto(d, 540, 300, "não é só dinheiro", max(10, int(84 * max(0.6, mola(lt, 0.0, 0.35)) * sai)))
        m = mola(lt, 0.0, 0.4) * sai
        if m > 0.05:
            moeda(d, 330, 860, s=2.0 * max(0.3, m), seed=800, frac=_parcial(lt, 0.0, 0.4))
        k = mola(lt, 0.5) * sai
        if k > 0.05:
            texto(d, 590, 860, "+", max(10, int(160 * k)), INK)
        k = mola(lt, 0.8) * sai
        if k > 0.05:
            texto(d, 820, 860, "?", max(10, int(240 * k * pulso(lt, vel=3.0, amp=0.08))), LARANJA)
    if lt < t_eua:
        return im
    # parte 2: EUA
    _txt_mola(d, 540, 290, "moravam com os pais", 70, INK, lt, t_eua)
    _txt_mola(d, 540, 378, "jovens de 18 a 34 anos", 54, CINZA, lt, t_eua + 0.15)
    yb, alt, larg = 1320, 700, 230
    t_bar = t_eua + 0.1
    t_slide = 0.80 * dur
    cx = 540 - 240 * entra(lt, t_slide, 0.5)
    C.barra_unica(d, cx, yb, None, "EUA, 2014", None, alt=alt, larg=larg, cor=VERDE, seed=400, lt=lt, t0=t_bar)
    if lt > max(t_bar + 1.05, 0.39 * dur):  # "trinta e dois virgula um por cento"
        texto(d, cx, yb - alt - 66, "32,1%", int(76 * pulso(lt, vel=2.0, amp=0.04)))
    t_al = t_slide + 0.45
    m = mola(lt, t_al)
    if m > 0.05:
        C.alianca_relogio(d, 775, 860, s=1.25 * m, seed=410, frac=entra(lt, t_al, 0.4), t=lt)
    _txt_mola(d, 775, 1110, "casamento adiado", 56, INK, lt, t_al + 0.3)
    return im


# ---------------------------------------------------------------------------
# CENA 5 - pergunta de volta: duas portas, nenhuma abre; boneco pensando
# ---------------------------------------------------------------------------
def cena_5(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 280, "escolha ou conta?", int(80 * pulso(lt, vel=1.5, amp=0.03)))
    C.duas_portas(d, 540, 720, s=1.2, seed=500, frac=_parcial(lt, 0.0, 0.7, 0.3))
    boneco_pensando(d, 540, 1330, s=1.3, seed=14, frac=_parcial(lt, 0.1, 0.6, 0.3), t=lt)
    return im
