"""Cenas do fim-dos-terceiros-lugares (componentes do Raphinha aprovados pelo Guilherme).

Fonte de verdade das posicoes/escalas/caixas: componentes.md (layout_cenas() de gerar_componentes.py).
Componentes novos: componentes_video.py (deste slug). Reuso do catalogo: balao_fala (media/sketch_componentes.py).
Convencao de cor: AZUL=convivio/telas/fonte; LARANJA=custo/hipotese/jovens; VERMELHO=queda;
FERRO tracejado=o que sumiu ou nao existe; MADEIRA=mobilia do terceiro lugar.

Decisoes aprovadas: cena 6 sem TV cobrindo a mesa (a mesa nao aparece; a virada vem do corte e do
estouro da TV); cenas 4 e 7 do roteiro divididas em duas cenas cada (aqui cena_3/cena_4 e cena_7/cena_8).
Regras firmes: nada cobre boneco nem texto; tudo entre SEGURO_TOPO..SEGURO_BASE e x >= 150;
sem legenda na base; numeros em algarismos; entradas escalonadas; nada parado.

Tempos: os momentos ligados a fala sao fracoes de `dur` (a cena dura o que a fala dura).
"""
import importlib.util
import math
import os

from PIL import ImageDraw

from media.sketch_lib import *
from media import sketch_componentes as SC

_AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("componentes_video_terceiros", os.path.join(_AQUI, "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def _cl(cor, k=0.55):
    return tuple(round(c + (255 - c) * k) for c in cor)


def _txt(d, lt, t0, x, y, s, tam, cor=INK):
    """Texto que entra com mola (cresce com leve estouro) a partir de t0."""
    m = mola(lt, t0, 0.35)
    if m > 0.15:
        texto(d, x, y, s, max(8, int(tam * m)), cor)


# ---------------------------------------------------------------------------
# cena_0 . gancho: mesa de cafe vazia ja no quadro 0; a xicara "some" (vira tracejado)
# ---------------------------------------------------------------------------
def cena_0(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    tam = int(74 * (1 + 0.04 * math.sin(lt * 5)))
    texto(d, 540, 300, "seu 3º lugar sumiu", tam)
    lg = fonte(74).getlength("seu 3º lugar sumiu")
    traco(d, [(540 - lg / 2, 372), (540 + lg / 2, 368)], 7, entra(lt, 0.35, 0.5), w=6, col=VERMELHO)

    cx, cy, s = 540, 880, 1.28
    C.mesa_cafe(d, cx, cy, s=s, seed=1, frac=1.0, cadeiras=0, xicaras=0)
    C.cadeira_cafe(d, cx - 225 * s, cy + 100 * s, s, 11, entra(lt, 0.1, 0.6), lado="esq")
    C.cadeira_cafe(d, cx + 225 * s, cy + 100 * s, s, 21, entra(lt, 0.3, 0.6), lado="dir")
    # xicara: cheia no comeco; no "e voce nem percebeu" vira contorno tracejado (sumiu)
    sx = 0.5 * s
    xx, yx = cx - 55 * s, cy - 64 * sx
    if lt < dur * 0.5:
        C.xicara_cafe(d, xx, yx, sx, 41, 1.0, vapor=False)
    else:
        corpo = [(xx - 60 * sx, yx - 50 * sx), (xx + 60 * sx, yx - 50 * sx), (xx + 45 * sx, yx + 50 * sx), (xx - 45 * sx, yx + 50 * sx)]
        f = entra(lt, dur * 0.5, 0.5)
        C.tracejado(d, corpo, 43, f, w=4, col=FERRO, passo=14, vao=10, fechado=True)
        C.tracejado(d, [(xx - 92 * sx, yx + 50 * sx), (xx - 62 * sx, yx + 62 * sx), (xx + 62 * sx, yx + 62 * sx),
                        (xx + 92 * sx, yx + 50 * sx)], 44, f, w=4, col=FERRO, passo=14, vao=10)
    return im


# ---------------------------------------------------------------------------
# cena_1 . definicao: 1º casa, 2º trabalho (cinza), 3º = cafe, bar, livraria; Oldenburg
# ---------------------------------------------------------------------------
def cena_1(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 290, "o terceiro lugar", 70)

    t_casa, t_mal, t_3 = dur * 0.15, dur * 0.27, dur * 0.42
    t_cafe, t_bar, t_liv, t_old = dur * 0.56, dur * 0.62, dur * 0.68, dur * 0.80

    m = mola(lt, t_casa)
    if m > 0.1:
        casa(d, 330, 560, s=0.75 * m, seed=3, frac=entra(lt, t_casa, 0.4), cor=_cl(FERRO))
    _txt(d, lt, t_casa + 0.2, 330, 690, "1º casa", 46, FERRO)

    m = mola(lt, t_mal)
    if m > 0.1:
        C.maleta_trabalho(d, 760, 580, s=0.85 * m, seed=5, frac=entra(lt, t_mal, 0.4), cor=_cl(FERRO, 0.35))
    _txt(d, lt, t_mal + 0.2, 760, 690, "2º trabalho", 46, FERRO)

    m = mola(lt, t_3)
    if m > 0.1:
        C.selo_numero(d, 540, 800, s=1.2 * m * pulso(lt, 1.2, 0.03), seed=9, frac=1.0, txt="3º", cor=LARANJA)

    m = mola(lt, t_cafe)
    if m > 0.1:
        C.xicara_cafe(d, 300, 1070, s=1.0 * m, seed=12, frac=1.0, vapor=True, t=lt)
    m = mola(lt, t_bar)
    if m > 0.1:
        copo(d, 540, 1070, s=0.72 * m, seed=8, nivel=0.7)
    m = mola(lt, t_liv)
    if m > 0.1:
        C.pilha_livros(d, 790, 1070, s=1.0 * m, seed=15)
    _txt(d, lt, t_cafe + 0.15, 300, 1235, "café", 48)
    _txt(d, lt, t_bar + 0.15, 540, 1235, "bar", 48)
    _txt(d, lt, t_liv + 0.15, 790, 1235, "livraria", 48)
    _txt(d, lt, t_old, 540, 1380, "sociólogo Ray Oldenburg", 50, AZUL)
    return im


# ---------------------------------------------------------------------------
# cena_2 . EUA: coluna de relogios "quase 7 h" (ate 2013) x "menos de 3 h" (2021)
# ---------------------------------------------------------------------------
def cena_2(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 270, "EUA (pesquisa ATUS)", 64)
    _txt(d, lt, 0.25, 540, 350, "horas/semana com amigos", 50, AZUL)

    c13, c21, yb = 360, 720, 1250
    f13 = entra(lt, dur * 0.10, dur * 0.40)
    C.coluna_relogios(d, c13, yb, s=1.0, seed=1, frac=f13, horas=6.8, cor=AZUL, t=lt)
    if f13 > 0:
        _txt(d, lt, dur * 0.12, c13, 1315, "até 2013", 52)
    _txt(d, lt, dur * 0.52, c13, 470, "quase 7 h", 58)

    t21 = dur * 0.70
    f21 = entra(lt, t21, dur * 0.14)
    C.coluna_relogios(d, c21, yb, s=1.0, seed=20, frac=f21, horas=2.7, cor=AZUL, t=lt)
    if f21 > 0:
        _txt(d, lt, t21, c21, 1315, "2021", 52)
    _txt(d, lt, dur * 0.85, c21, 880, "menos de 3 h", 58, LARANJA)
    return im


# ---------------------------------------------------------------------------
# cena_3 . Brasil: nao existe essa medida (relogio tracejado com "?")
# ---------------------------------------------------------------------------
def cena_3(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 290, "e no Brasil?", 72)
    C.relogio_sem_medida(d, 540, 800, s=1.6, seed=3, frac=entra(lt, 0.05, 0.8), t=lt)
    _txt(d, lt, dur * 0.42, 540, 1120, "sem essa medida", 60, FERRO)
    return im


# ---------------------------------------------------------------------------
# cena_4 . Brasil, consumo: -7,1% saidas e +28,3% gasto por saida
# ---------------------------------------------------------------------------
def cena_4(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 280, "Brasil: consumo", 70)
    _txt(d, lt, dur * 0.12, 540, 360, "1º tri 2026 x 1º tri 2025", 46, FERRO)

    t1, t2 = dur * 0.16, dur * 0.62
    f1 = entra(lt, t1, dur * 0.14)
    if f1 > 0:
        s1 = 1.0 if f1 < 0.99 else pulso(lt, 1.0, 0.015)
        C.cartao_variacao(d, 350, 860, s=s1, seed=31, frac=f1, valor="-7,1%", rotulo="saídas",
                          sentido=-1, cor=VERMELHO, icone="porta")
    f2 = entra(lt, t2, dur * 0.14)
    if f2 > 0:
        s2 = 1.0 if f2 < 0.99 else pulso(lt + 0.7, 1.0, 0.015)
        C.cartao_variacao(d, 770, 860, s=s2, seed=41, frac=f2, valor="+28,3%", rotulo="gasto por saída",
                          sentido=1, cor=LARANJA, icone="moeda")
    return im


# ---------------------------------------------------------------------------
# cena_5 . hipotese: banco "gratis" sumindo -> recibo com "ver amigo" -> selo "hipotese, nao prova"
# ---------------------------------------------------------------------------
def cena_5(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 280, "nossa leitura", 66, LARANJA)

    C.banco_praca(d, 540, 610, s=1.15, seed=51, frac=entra(lt, 0.05, dur * 0.28), sumindo=True)
    seta(d, 540, 750, 540, 820, seed=55, frac=entra(lt, dur * 0.36, 0.35), cor=LARANJA, w=8)

    fr = entra(lt, dur * 0.42, dur * 0.12)
    if fr > 0:
        C.recibo_orcamento(d, 540, 1070, s=1.0, seed=61, frac=fr)

    m = mola(lt, dur * 0.74)
    if m > 0.15:
        C.selo_hipotese(d, 540, 1400, s=m * pulso(lt, 1.2, 0.02), seed=71, frac=1.0)
    return im


# ---------------------------------------------------------------------------
# cena_6 . contraexemplo: as telas (TV estoura; sofa sozinho; celular). A mesa NAO aparece.
# ---------------------------------------------------------------------------
def cena_6(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    m = mola(lt, 0.0, 0.4)
    if m > 0.15:
        texto(d, 540, 270, "e as telas?", max(8, int(80 * m)))
    _txt(d, lt, dur * 0.18, 540, 360, "economista Bryce Ward", 46, AZUL)

    m = mola(lt, 0.0, 0.4)
    if m > 0.1:
        C.tv_streaming(d, 540, 660, s=1.2 * m, seed=81, frac=1.0, t=lt)

    t_sofa = dur * 0.64
    fs = entra(lt, t_sofa, 0.6)
    if fs > 0:
        C.sofa_sozinho(d, 410, 1190, s=0.95, seed=91, frac=fs)
    _txt(d, lt, dur * 0.72, 540, 1420, "tempo sozinho cresceu", 52)

    t_cel = dur * 0.84
    m = mola(lt, t_cel)
    if m > 0.1:
        seg = max(1, 5 - int(max(0.0, lt - t_cel)))
        C.celular_video(d, 820, 1185, s=1.35 * m, seed=95, frac=1.0, t=lt, linhas=("próximo", f"em {seg} s"))
    return im


# ---------------------------------------------------------------------------
# cena_7 . pode ser uma mistura: circulo "lugar e custo", depois "telas", depois a intersecao
# ---------------------------------------------------------------------------
def cena_7(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 290, "pode ser uma mistura", 66)

    cx, cy, s, seed = 540, 820, 1.3, 101
    r = 170 * s
    ca, cb = cx - 110 * s, cx + 110 * s
    tam = int(48 * s)
    fa, fb = entra(lt, 0.05, 0.55), entra(lt, 0.45, 0.55)
    t_mix = 1.05
    if lt >= t_mix:
        k = pulso(lt - t_mix, 1.0, 0.015)
        C.mistura_causas(d, cx, cy, s=s * k, seed=seed, frac=1.0)
        return im
    traco(d, circ(ca, cy, r, 56), seed, fa, w=7, amp=1.8 * s, col=LARANJA, fechado=True)
    traco(d, circ(cb, cy, r, 56), seed + 1, fb, w=7, amp=1.8 * s, col=AZUL, fechado=True)
    if fa >= 0.99:
        texto_multilinha(d, cx - 178 * s, cy - tam * 0.62, ["lugar e", "custo"], tam, LARANJA)
    if fb >= 0.99:
        texto(d, cx + 178 * s, cy, "telas", tam, AZUL)
    return im


# ---------------------------------------------------------------------------
# cena_8 . EUA: queda forte nos jovens (seta vermelha primeiro), mas nao so deles (setas cinza depois)
# ---------------------------------------------------------------------------
def cena_8(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    _txt(d, lt, 0.0, 540, 290, "EUA: queda forte", 68)

    cx, cy, s, n, seed = 560, 880, 1.25, 4, 111
    passo, ps = 170 * s, 0.9 * s
    x0 = cx - (n - 1) * passo / 2
    fim = cy - 146 * ps - 26 * s
    for k in range(n):
        x = x0 + k * passo
        f = entra(lt, 0.05 + 0.15 * k, 0.45)
        pessoa(d, x, cy, ps, seed + 10 * k, f, LARANJA if k == 0 else INK)
        if k == n - 1:
            traco(d, [(x + 50 * ps, cy + 5 * ps), (x + 58 * ps, cy + 125 * ps)], seed + 90, f, w=5, amp=1)
            traco(d, [(x + 50 * ps, cy + 5 * ps), (x + 40 * ps, cy - 6 * ps)], seed + 91, f, w=5, amp=1)
    # seta vermelha grande do jovem (queda forte)
    t_j = dur * 0.30
    seta(d, x0, fim - 150 * s, x0, fim, seed=seed + 100, frac=entra(lt, t_j, 0.35), cor=VERMELHO, w=9)
    _txt(d, lt, t_j + 0.2, x0, cy + 125 * ps + 52 * s, "jovens", int(48 * s), LARANJA)
    # setas cinza menores nos outros (tambem cairam), junto do "nao parece ser so deles"
    t_o = dur * 0.62
    for k in range(1, n):
        x = x0 + k * passo
        seta(d, x, fim - 80 * s, x, fim, seed=seed + 100 + k, frac=entra(lt, t_o + 0.12 * k, 0.3), cor=FERRO, w=6)
    _txt(d, lt, t_o, 540, 1360, "não parece ser só deles", 54)
    return im


# ---------------------------------------------------------------------------
# cena_9 . pergunta de volta: mesa com as cadeiras vazias + balao (sem resposta pronta)
# ---------------------------------------------------------------------------
def cena_9(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    C.mesa_cafe(d, 540, 960, s=1.28, seed=121, frac=entra(lt, 0.0, 0.5), cadeiras=2, xicaras=0)
    m = mola(lt, 0.35)
    if m > 0.15:
        k = min(m, 1.02) * (pulso(lt, 0.8, 0.01) if m >= 1 else 1.0)
        SC.balao_fala(d, 540, 400, ["qual encontro você", "deixou de fazer?"],
                      larg=760 * k, alt=250 * k, seed=131, tam=max(8, int(60 * k)), cor_borda=LARANJA)
    return im
