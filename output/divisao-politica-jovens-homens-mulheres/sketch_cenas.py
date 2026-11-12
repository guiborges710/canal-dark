"""Cenas do vídeo divisao-politica-jovens-homens-mulheres (estilo sketch, Olise).

Componentes aprovados pelo Guilherme (proposta do Raphinha): componentes_video.py, nesta pasta,
e boneco_pensando de media/sketch_componentes.py. Posições e escalas de layout_cenas() em
componentes_gerar.py (fonte única), que já passaram no checador de sobreposição.

Visual neutro: ELAS = laranja, ELES = lilás; método (régua, lupa, manchete, cartões) em tinta.
Sem cores de partido, sem bandeiras, sem nome de instituto na tela.

Cada cena sincroniza com a fala pela fração do tempo da cena (p = lt / dur), estimada pela
posição das palavras na fala: a cena dura o que a fala dura.
"""
import importlib.util
import math
import os

from PIL import ImageDraw
from media.sketch_lib import *
import media.sketch_componentes as SC

_spec = importlib.util.spec_from_file_location(
    "componentes_video_divisao", os.path.join(os.path.dirname(os.path.abspath(__file__)), "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


# ---------------------------------------------------------------------------
# tempo
# ---------------------------------------------------------------------------
def _p(lt, dur):
    return lt / max(dur, 1e-6)


def faixa(p, a, b):
    """0 antes de a, 1 depois de b, linear no meio."""
    return max(0.0, min(1.0, (p - a) / (b - a)))


def surge(d, x, y, s, tam, f, cor=INK):
    """Texto que entra com estouro de mola (f = mola(...)); some enquanto f é pequeno."""
    t = int(tam * f)
    if t >= 10:
        texto(d, x, y, s, t, cor)


# ---------------------------------------------------------------------------
# 1. Gancho: os dois de costas, se afastando; a lupa examina a linha
# ---------------------------------------------------------------------------
def cena_0(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 290, "Mais distantes?", 84)
    surge(d, 540, 385, "jovens dos EUA", 52, mola(lt, 0.15))
    dist = 250 + 150 * entra(lt, 0.0, 2.4)
    C.dupla_distante(d, 540, 1010, s=1.4, seed=11, frac=1.0, dist=dist, com_lupa=False)
    # lupa varrendo a linha tracejada (mesma posição do componente, com leve vaivém)
    lx = 540 + 34 * math.sin(lt * 1.8)
    ly = 1010 - 285 * 1.4 + 8 * math.sin(lt * 3.1)
    lupa(d, lx, ly, s=0.75 * 1.4, seed=101)
    if p >= 0.64:
        surge(d, 540, 1340, "depende da pesquisa", 56, mola(lt, 0.64 * dur))
    return im


# ---------------------------------------------------------------------------
# 2. A série: etiqueta "liberal" + dois grupos de três barras
# ---------------------------------------------------------------------------
def cena_1(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    C.etiqueta_rotulo(d, 540, 280, "liberal", s=1.2 * pulso(lt, vel=1.2, amp=0.03), seed=21,
                      frac=entra(lt, 0.0, 0.5))
    if p >= 0.10:
        surge(d, 540, 392, "18 a 29 anos, EUA", 50, mola(lt, 0.10 * dur))
    f_chao = faixa(p, 0.14, 0.22)
    if f_chao > 0:
        C.barras_grupos(d, 540, 1080, s=1.0, seed=31, frac=f_chao,
                        frac_elas=faixa(p, 0.60, 0.80), frac_eles=faixa(p, 0.80, 0.96))
    if p >= 0.30:
        surge(d, 540, 1400, "3 períodos, 2001 a 2024", 46, mola(lt, 0.30 * dur))
    return im


# ---------------------------------------------------------------------------
# 3. A diferença: de 3 pontos para 15 (o vão amarelo cresce)
# ---------------------------------------------------------------------------
def cena_2(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 290, "a diferença", 76)
    C.vao_pontos(d, 310, 1180, 28, 25, s=1.0, seed=41, frac=faixa(p, 0.0, 0.45),
                 rotulo="3 pontos", periodo="2001-07")
    fs = faixa(p, 0.38, 0.52)
    if fs > 0:
        seta(d, 450, 1030, 635, 850, seed=5, frac=fs, cor=INK, w=8)
    f15 = faixa(p, 0.42, 0.80)
    if f15 > 0:
        C.vao_pontos(d, 770, 1180, 40, 25, s=1.0, seed=51, frac=f15, rotulo="15 pontos", periodo="2017-24")
    return im


# ---------------------------------------------------------------------------
# 4. Quem se mexeu: a linha delas sobe, a deles fica reta ("=")
# ---------------------------------------------------------------------------
def cena_3(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 285, "Quem se mexeu?", 76)
    C.etiqueta_rotulo(d, 540, 410, "liberal", s=1.0, seed=61, frac=entra(lt, 0.1, 0.4))
    f = faixa(p, 0.08, 0.90)
    C.linhas_trajetoria(d, 560, 860, s=1.0, seed=71, frac=f)
    if f >= 0.45:
        surge(d, 300, 1330, "elas subiram", 50, mola(lt, (0.08 + 0.45 * 0.82) * dur), C.ELAS)
    if f >= 0.88:
        surge(d, 780, 1330, "eles, parados", 50, mola(lt, (0.08 + 0.88 * 0.82) * dur), C.ELES)
    return im


# ---------------------------------------------------------------------------
# 5. Outras bases: dois cartões com linha quase plana
# ---------------------------------------------------------------------------
def cena_4(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 285, "outras bases: linha plana", 60)
    # "outras duas análises": os dois cartões são traçados juntos, vazios
    # "Numa...": o primeiro se completa; "7 pontos": o número circulado
    # "Na outra...": o segundo se completa
    f1 = min(0.985, entra(lt, 0.0, 0.8)) if p < 0.28 else 1.0
    C.cartao_base(d, 540, 610, s=1.15, seed=3, frac=f1, numero="7" if p >= 0.42 else None,
                  ano="2022", legenda="perto de 7 pontos, 2022")
    f2 = min(0.985, entra(lt, 0.35, 0.8)) if p < 0.74 else 1.0
    C.cartao_base(d, 540, 1100, s=1.15, seed=8, frac=f2, legenda="sem evidência de alta")
    return im


# ---------------------------------------------------------------------------
# 6a. E o porquê? Nenhuma delas prova.
# ---------------------------------------------------------------------------
def cena_5(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 290, "E o porquê?", 80)
    SC.boneco_pensando(d, 540, 930, s=1.8, frac=entra(lt, 0.0, 0.5), t=lt)
    if p >= 0.42:
        surge(d, 540, 1270, "nenhuma delas prova", 60, mola(lt, 0.42 * dur))
    return im


# ---------------------------------------------------------------------------
# 6b. Nossa leitura: a manchete depende da régua (a régua gira, a manchete troca)
# ---------------------------------------------------------------------------
def cena_6(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    texto(d, 540, 285, "nossa leitura", 64)
    titulo = ("diferença", "cresce") if p < 0.66 else ("diferença", "estável")
    C.manchete(d, 540, 640, s=1.2, seed=81, frac=entra(lt, 0.0, 0.4), titulo=titulo)
    ang = -0.06 + 0.12 * faixa(p, 0.52, 0.66)
    C.regua(d, 540, 1080, comp=680, s=1.0, seed=91, frac=entra(lt, 0.2, 0.5), ang=ang)
    if p >= 0.40:
        surge(d, 540, 1250, "depende da régua", 60, mola(lt, 0.40 * dur))
    return im


# ---------------------------------------------------------------------------
# 6c. "Geração" junta dois grupos em ritmos diferentes
# ---------------------------------------------------------------------------
def cena_7(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    p = _p(lt, dur)
    C.geracao_dois_ritmos(d, 540, 820, s=1.1, seed=111, frac=entra(lt, 0.0, 0.5),
                          f_setas=faixa(p, 0.40, 0.85))
    if p >= 0.30:
        surge(d, 540, 1250, "dois grupos, dois ritmos", 58, mola(lt, 0.30 * dur))
    return im


# ---------------------------------------------------------------------------
# 6d. Pergunta de volta: os dois, agora lado a lado, olhando a mesma régua
# ---------------------------------------------------------------------------
def cena_8(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    texto(d, 540, 290, "Qual é a régua?", 80)
    C.regua_pergunta(d, 540, 890, s=1.15, seed=121, frac=entra(lt, 0.0, 0.6), t=lt)
    return im
