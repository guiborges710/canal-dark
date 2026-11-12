"""Cenas do esquema-de-piramide (12 componentes APROVADOS pelo Guilherme em 2026-10-31).

Fonte de verdade das posicoes/escalas/caixas: componentes.md (layout_cenas()).
Componentes: media/sketch_componentes.py. Biblioteca-base: media/sketch_lib.py.
Convencao de cor: AZUL=pessoa/multinivel legal; LARANJA=dinheiro em movimento/
recrutamento; VERDE=produto real; VERMELHO=colapso/condenacao; SOL_AMARELO=moeda.

Regras firmes: nada cobre boneco; nada cobre texto; tudo dentro de SEGURO_TOPO..SEGURO_BASE;
sem legenda na base; numeros em algarismos na tela. Entradas escalonadas, nada parado.
"""
import math
from PIL import ImageDraw
from media.sketch_lib import *
from media.sketch_componentes import *


def cena_0(lt, dur):
    """Gancho: a pergunta ja na tela no frame 0, piramide com dinheiro subindo."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300) duas linhas -- entra pulsando desde o frame 0
    tam = int(64 * (1 + 0.06 * math.sin(lt * 5)))
    texto_multilinha(d, 540, 258, ["o que é", "esquema de pirâmide?"], tam, cor=INK)
    # piramide com dinheiro subindo (540, 980) s=1.0 -- cresce com mola
    piramide_pessoas(d, 540, 980, s=1.0 * mola(lt, 0.1), seed=1,
                     frac=entra(lt, 0.0, 0.5), cor=INK, dinheiro=lt > 1.0)
    return im


def cena_1(lt, dur):
    """O que e: a piramide colapsa -- base vermelha + rachadura, 'a base perde tudo'."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300) -- aparece quando a fala chega no 'quando para de entrar'
    if lt > 3.0:
        texto(d, 540, 300, "quando para de entrar", 56, cor=INK)
    # piramide (540, 900) s=1.0 -- colapso entra depois (rachadura + base vermelha)
    colapso = lt > 3.5
    piramide_pessoas(d, 540, 900, s=1.0 * mola(lt, 0.1), seed=2,
                     frac=entra(lt, 0.0, 0.5), cor=INK, colapso=colapso)
    # rotulo vermelho (540, 1340)
    if lt > 4.0:
        texto(d, 540, 1340, "a base perde tudo", 54, cor=VERMELHO)
    return im


def cena_2(lt, dur):
    """Diferenca: venda real (verde, em cima) x so adesao (laranja, embaixo)."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 280)
    texto(d, 540, 280, "de onde vem o dinheiro", 56, cor=INK)
    # bloco de cima: multinivel legal = venda real
    if lt > 0.6:
        texto(d, 420, 500, "multinível: venda real", 48, cor=VERDE_OK, ancora="lm")
    fonte_dinheiro(d, 380, 660, s=1.1, seed=3, frac=entra(lt, 0.8, 0.45), modo="venda")
    # bloco de baixo: piramide = so adesao
    if lt > 3.0:
        texto(d, 420, 980, "pirâmide: só adesão", 48, cor=LARANJA, ancora="lm")
    fonte_dinheiro(d, 360, 1140, s=1.1, seed=4, frac=entra(lt, 3.2, 0.45), modo="adesao")
    return im


def cena_3(lt, dur):
    """Confianca: o convite vem de quem voce confia (envelope + coracao)."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300)
    texto(d, 540, 300, "o convite vem de quem", 56, cor=INK)
    # convite_confianca (540, 820) s=1.3 -- bonecos com mola, envelope depois
    convite_confianca(d, 540, 820, s=1.3 * mola(lt, 0.1), seed=5, frac=entra(lt, 0.0, 0.5))
    # rotulo azul (540, 1220)
    if lt > 1.2:
        texto(d, 540, 1220, "você confia", 58, cor=AZUL)
    return im


# Cada caso com nome, ano e o veredito que a fala realmente diz ("condenados").
# A fala enxugada nao cita penas exatas; o cartao segue a fala. "segundo a acusacao"
# so no Farao (como no roteiro aprovado).
_CASOS = [
    ("Avestruz Master", "2005", "condenados"),
    ("TelexFree", "2013", "condenados"),
    ("Faraó dos Bitcoins", "2025", "condenado"),
]


def cena_4(lt, dur):
    """Casos reais: um cartao por vez + martelo. Troca = o anterior sai antes do novo."""
    im = papel()
    d = ImageDraw.Draw(im)
    # tres janelas ao longo da fala; cada caso ocupa ~1/3 da cena
    janela = dur / 3.0
    idx = min(2, int(lt / janela))
    nome, ano, pena = _CASOS[idx]
    t_loc = lt - idx * janela          # tempo local dentro da janela do caso atual
    # cartao do caso (540, 650) s=1.1 -- entra; "segundo a acusacao" so no Farao
    frac_card = entra(t_loc, 0.0, 0.4)
    caixa_caso(d, 540, 650, s=1.1, seed=10 + idx, frac=frac_card,
               nome=nome, ano=ano, pena=pena)
    if idx == 2 and t_loc > 0.6:
        texto(d, 540, 790, "segundo a acusação", 38, cor=FERRO)
    # martelo (540, 1080) s=1.0 -- bate (mola) um pouco depois do cartao
    martelo_juiz(d, 540, 1080, s=1.0 * mola(t_loc, 0.5), seed=20 + idx,
                 frac=entra(t_loc, 0.4, 0.4))
    return im


def cena_5(lt, dur):
    """Mesma mecanica: gado, avestruz, bitcoin -- mudam a fachada."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300)
    texto(d, 540, 300, "muda a fachada", 60, cor=INK)
    # tres fachadas entram escalonadas, da esquerda para a direita
    icone_gado(d, 260, 760, s=0.9, seed=30, frac=entra(lt, 0.3, 0.35))
    icone_avestruz(d, 540, 760, s=0.9, seed=31, frac=entra(lt, 0.9, 0.35))
    icone_bitcoin(d, 820, 760, s=1.0, seed=32, frac=entra(lt, 1.5, 0.35))
    # rotulo (540, 1200)
    if lt > 2.0:
        texto(d, 540, 1200, "a mecânica se repete", 52, cor=VERMELHO)
    return im


def cena_6(lt, dur):
    """Pergunta de volta: a pessoa ou o dinheiro? (escolha pontilhada)."""
    im = papel()
    d = ImageDraw.Draw(im)
    # titulo (540, 300) pulsando
    tam = int(60 * (1 + 0.05 * math.sin(lt * 5)))
    texto(d, 540, 300, "o que você confere?", tam, cor=INK)
    # pessoa_ou_dinheiro (540, 820) s=1.3 -- bonecos/moeda com mola
    pessoa_ou_dinheiro(d, 540, 820, s=1.3 * mola(lt, 0.1), seed=40,
                       frac=entra(lt, 0.0, 0.5))
    # rotulos embaixo de cada lado
    if lt > 1.0:
        texto(d, 320, 1240, "a pessoa", 50, cor=AZUL)
    if lt > dur * 0.5:
        texto(d, 760, 1240, "ou o dinheiro", 50, cor=INK)
    return im
