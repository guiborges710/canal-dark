from PIL import ImageDraw
from media.sketch_lib import *

# Pair programming — LinkedIn
# 4 cenas, ~15 segundos total
# Dois bonecos de palito lado a lado, setas de knowledge transfer


def cena_0(lt, dur):
    """Dois devs lado a lado com seta dupla entre eles — a premissa do pair programming."""
    im = papel()
    d = ImageDraw.Draw(im)

    # Título no topo
    f_titulo = entra(lt, 0.0, 0.35)
    texto(d, 540, 310, "pair programming", 58, ancora="mm")

    # Boneco da esquerda (driver)
    f1 = mola(lt, 0.15)
    pessoa(d, 320, 1000, s=1.8 * f1, seed=1)

    # Boneco da direita (navigator)
    f2 = mola(lt, 0.35)
    pessoa(d, 760, 1000, s=1.8 * f2, seed=10)

    # Seta esq → dir (aparece primeiro)
    f_seta1 = entra(lt, 0.5, 0.45)
    seta(d, 420, 960, 650, 960, seed=20, frac=f_seta1, cor=AZUL, w=8)
    # Seta dir → esq (aparece depois com pulso)
    f_seta2 = entra(lt, 0.7, 0.45)
    p = pulso(lt, vel=3.0, amp=0.06) if lt > 1.0 else 1.0
    seta(d, 650, 1010, 420, 1010, seed=25, frac=f_seta2 * p, cor=LARANJA, w=8)

    # Rótulos sob os bonecos (abaixo das pernas que terminam em ~y=1225)
    if lt > 0.6:
        texto(d, 320, 1310, "driver", 44, cor=AZUL, ancora="mm")
        texto(d, 760, 1310, "navigator", 44, cor=LARANJA, ancora="mm")

    return im


def cena_1(lt, dur):
    """Balão de fala saindo dos dois bonecos ao mesmo tempo — o raciocínio em tempo real."""
    im = papel()
    d = ImageDraw.Draw(im)

    # Bonecos menores, mais alto na tela
    f1 = mola(lt, 0.0)
    f2 = mola(lt, 0.1)
    pessoa(d, 280, 920, s=1.5 * f1, seed=2)
    pessoa(d, 800, 920, s=1.5 * f2, seed=12)

    # Balão esquerdo — ensina (sem triângulo, acima da cabeça)
    f_bal1 = entra(lt, 0.3, 0.45)
    balao(d, 280, 530, 300, 140, ["ensina"], seed=30, frac=f_bal1, tam=46, cauda=None)

    # Balão direito — aprende (sem triângulo)
    f_bal2 = entra(lt, 0.5, 0.45)
    balao(d, 800, 530, 300, 140, ["aprende"], seed=40, frac=f_bal2, tam=46, cauda=None)

    # Seta de troca no centro (abaixo das pernas que terminam em ~y=1108)
    f_seta = entra(lt, 0.8, 0.4)
    seta(d, 430, 1200, 670, 1200, seed=50, frac=f_seta, cor=AZUL, w=9)
    seta(d, 670, 1260, 430, 1260, seed=55, frac=f_seta, cor=LARANJA, w=9)

    # Rótulo central
    if lt > 1.1:
        texto(d, 540, 1360, "ensina ↔ aprende", 48, ancora="mm")

    return im


def cena_2(lt, dur):
    """Seta larga fluindo da esquerda para a direita — o knowledge transfer na prática."""
    im = papel()
    d = ImageDraw.Draw(im)

    # Título
    texto(d, 540, 340, "knowledge transfer", 54, ancora="mm")

    # Boneco esquerdo (origem do conhecimento)
    f1 = mola(lt, 0.0)
    pessoa(d, 220, 950, s=1.6 * f1, seed=3)

    # Seta grande no centro — o conhecimento fluindo
    f_seta = entra(lt, 0.3, 0.6)
    seta(d, 370, 930, 720, 930, seed=60, frac=f_seta, cor=AZUL, w=14)

    # Boneco direito (receptor)
    f2 = mola(lt, 0.7)
    pessoa(d, 860, 950, s=1.6 * f2, seed=13)

    # Rótulos contextuais
    if lt > 0.9:
        f_rt = entra(lt, 0.9, 0.35)
        texto(d, 540, 1130, "no código", 46, cor=AZUL, ancora="mm")
        texto(d, 540, 1200, "no erro", 46, cor=LARANJA, ancora="mm")
        texto(d, 540, 1270, "em tempo real", 46, ancora="mm")

    # Brilho na seta que cresce com o tempo
    if lt > 0.5:
        k = min(0.9, 0.4 + (lt - 0.5) * 0.5)
        im = brilho(im, 540, 930, 220, AZUL, k=k)

    return im


def cena_3(lt, dur):
    """Check grande — conclusão limpa."""
    im = papel()
    d = ImageDraw.Draw(im)

    # Bonecos entram escalonados (esquerdo primeiro, direito depois)
    f_p1 = mola(lt, 0.0)
    f_p2 = mola(lt, 0.2)
    pessoa(d, 380, 780, s=1.3 * f_p1, seed=4)
    pessoa(d, 700, 780, s=1.3 * f_p2, seed=14)

    # Check grande no centro — entra com mola em vez de linear
    f_check = mola(lt, 0.4)
    check(d, 540, 1080, s=3.5 * f_check, seed=70, cor=(60, 150, 90))

    # Rótulos entram em sequência
    if lt > 0.85:
        texto(d, 540, 1280, "onboarding", 58, cor=(60, 150, 90), ancora="mm")
    if lt > 1.05:
        texto(d, 540, 1360, "mais eficiente", 50, ancora="mm")

    # Brilho suave no check quando estabiliza
    if lt > 1.1:
        im = brilho(im, 540, 1080, 180, (60, 150, 90), k=0.5)

    return im
