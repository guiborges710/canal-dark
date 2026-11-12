from media.sketch_lib import *


def cena_0(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    pessoa(d, 340, 980, 2.0, seed=1, frac=entra(lt, 0.0, 0.5))
    if lt > 0.5:
        celular(d, 730, 880, 1.4 * mola(lt, 0.5), seed=3)
    seta(d, 470, 760, 620, 800, seed=5, frac=entra(lt, 1.0, 0.4))
    texto(d, 540, 420, "todo mundo cancelou", 76)
    if lt > 0.7:
        texto(d, 730, 860, "hoje", 50)
        texto(d, 730, 920, "não", 50)
    return im


def cena_1(lt, dur):
    im = papel()
    d = ImageDraw.Draw(im)
    texto(d, 540, 420, "horas com amigos", 76)
    barras(d, 540, 1240, [{"rotulo": "2013", "valor": 7, "cor": AZUL, "texto": "7h"}, {"rotulo": "2021", "valor": 3, "cor": VERMELHO, "texto": "3h"}], lt=lt, t0=0.2, alt_max=560)
    return im
