"""Cenas do pair-programming (refeito com os 13 componentes APROVADOS pelo Guilherme).

Fonte de verdade das posicoes/escalas/caixas: componentes.md (layout_cenas()).
Componentes: media/sketch_componentes.py. Biblioteca-base: media/sketch_lib.py.
Convencao: pessoa A = AZUL (escreve), pessoa B = LARANJA (revisa). Verde = decisao. Vermelho = negacao.

Regras firmes: nada cobre boneco; nada cobre texto; tudo dentro de SEGURO_TOPO..SEGURO_BASE;
sem legenda na base. Entradas escalonadas (entra/mola), nada parado.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *
from media.sketch_componentes import *


def cena_0(lt, dur):
    """Negacao: 'nao e isso' -- duas pessoas so olhando para a tela riscada."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 290)
    texto(d, 540, 290, "pair programming", 66, cor=INK)
    # tela riscada (540, 620) s=1.0 -- o X entra depois (negacao)
    riscada = lt > 1.4
    tela_codigo(d, 540, 620, s=1.0, seed=3, frac=entra(lt, 0.0, 0.4),
                cores=[FERRO] * 5, riscada=riscada)
    # rotulo vermelho (540, 940)
    if lt > 1.5:
        texto(d, 540, 940, "não é isso", 54, cor=VERMELHO)
    # dupla (540, 1250) s=1.35 dist=300 -- entra com mola escalonada
    dupla_pair(d, 540, 1250, s=1.35 * mola(lt, 0.2), seed=10, dist=300)
    return im


def cena_1(lt, dur):
    """Discussao: duas pessoas, o mesmo problema, perguntas indo e voltando."""
    im = papel()
    d = ImageDraw.Draw(im)
    # dupla (540, 1000) s=1.3 dist=340
    dupla_pair(d, 540, 1000, s=1.3 * mola(lt, 0.1), seed=11, dist=340)
    # caixa_problema (540, 1350) s=0.95
    caixa_problema(d, 540, 1350, s=0.95, seed=5, frac=entra(lt, 0.4, 0.4))
    # balao A (320, 420) 420x180
    balao_fala(d, 320, 420, ["e se a gente", "tentar isso?"], larg=420, alt=180,
               seed=31, frac=entra(lt, 0.9, 0.4), tam=50, cor_borda=AZUL)
    # balao B (760, 650) 420x150
    balao_fala(d, 760, 650, ["por que assim?"], larg=420, alt=150,
               seed=41, frac=entra(lt, 2.2, 0.4), tam=50, cor_borda=LARANJA)
    return im


def cena_2(lt, dur):
    """Papeis: uma escreve (teclado, azul), a outra revisa e sugere (lupa)."""
    im = papel()
    d = ImageDraw.Draw(im)
    # tela_codigo (540, 560) s=0.95, linhas AZUL
    tela_codigo(d, 540, 560, s=0.95, seed=6, frac=entra(lt, 0.0, 0.4),
                cores=[AZUL] * 5)
    # dupla (540, 980) s=1.35 dist=440 com rotulos de papel
    dupla_pair(d, 540, 980, s=1.35 * mola(lt, 0.1), seed=12, dist=440,
               papeis=("escreve", "revisa e sugere") if lt > 0.6 else None)
    # teclado sob A (320, 1300) s=1.3
    teclado(d, 320, 1300, s=1.3, seed=60, frac=entra(lt, 0.7, 0.35))
    # lupa sob B (760, 1290) s=1.0
    lupa_revisao(d, 760, 1290, s=1.0, seed=61, frac=entra(lt, 1.0, 0.35))
    return im


def cena_3(lt, dur):
    """Troca de papel: as setas de ida e volta."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300)
    texto(d, 540, 300, "troca de papel", 62, cor=INK)
    # dupla (540, 820) s=1.3 dist=440
    dupla_pair(d, 540, 820, s=1.3 * mola(lt, 0.0), seed=12, dist=440)
    # setas_troca (540, 1130) s=1.3 dist=360
    setas_troca(d, 540, 1130, s=1.3, seed=70, frac=entra(lt, 0.8, 0.5), dist=360)
    return im


def cena_4(lt, dur):
    """Solucao em conjunto: a tela com linhas das duas cores + check verde."""
    im = papel()
    d = ImageDraw.Draw(im)
    # tela_codigo (540, 560) s=0.9, cores alternadas A/B
    cores = [AZUL, LARANJA, AZUL, LARANJA, AZUL, LARANJA]
    tela_codigo(d, 540, 560, s=0.9, seed=8, frac=entra(lt, 0.0, 0.4), cores=cores)
    # dupla afastados (540, 1000) s=1.25 dist=620
    dupla_pair(d, 540, 1000, s=1.25 * mola(lt, 0.1), seed=13, dist=620)
    # rotulo verde (540, 1200)
    if lt > 0.6:
        texto(d, 540, 1200, "solução em conjunto", 52, cor=VERDE_OK)
    # check_solucao (540, 1350) s=2.6
    if lt > 2.6:
        im = check_solucao(im, d, 540, 1350, s=2.6 * mola(lt, 2.6), seed=80)
    return im


def cena_5(lt, dur):
    """Tres ganhos: contexto, conhecimento, decisao."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300)
    texto(d, 540, 300, "pair programming é:", 62, cor=INK)
    tempos = [0.6, 2.1, 3.7]
    # ganho_contexto (300, 640)
    ganho_contexto(d, 300, 640, s=1.0, seed=90, frac=entra(lt, tempos[0], 0.4))
    # ganho_conhecimento (300, 940)
    ganho_conhecimento(d, 300, 940, s=1.0, seed=92, frac=entra(lt, tempos[1], 0.4))
    # ganho_decisao (300, 1240)
    ganho_decisao(d, 300, 1240, s=1.0, seed=97, frac=entra(lt, tempos[2], 0.4), rotulo="decisão")
    return im


def cena_6(lt, dur):
    """Pergunta de volta ao publico."""
    im = papel()
    d = ImageDraw.Draw(im)
    # balao A (540, 420) 620x170
    balao_fala(d, 540, 420, ["ja fez", "pair programming?"], larg=620, alt=170,
               seed=50, frac=entra(lt, 0.2, 0.45), tam=58, cor_borda=AZUL)
    # balao B (540, 640) 560x150
    balao_fala(d, 540, 640, ["o que voce aprendeu?"], larg=560, alt=150,
               seed=55, frac=entra(lt, dur * 0.5, 0.45), tam=50, cor_borda=LARANJA)
    # boneco_pensando (540, 1280) s=1.5 com ? pulsando
    boneco_pensando(d, 540, 1280, s=1.5 * mola(lt, 0.0), seed=14, frac=1.0, t=lt)
    return im
