"""Gera os assets do video esquema-de-piramide:
 - componentes/<nome>.png                 (fundo de papel, 1 por componente)
 - componentes/transparentes/<nome>.png   (RGBA, fundo transparente)
 - componentes/contato.jpg                (todos juntos, rotulados)
 - componentes/cenas_exemplo.jpg          (cada cena composta nas posicoes do componentes.md)
E roda a verificacao automatica de sobreposicao (caixas de boneco/texto x outros).
Nao renderiza video nem gera narracao.
"""
import os
import sys
import math
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)

from media.sketch_lib import *  # noqa: E402
import importlib.util  # noqa: E402

_cv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "componentes_video.py")
spec = importlib.util.spec_from_file_location("componentes_video", _cv)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "componentes")
PASTA_T = os.path.join(PASTA, "transparentes")
os.makedirs(PASTA_T, exist_ok=True)

VERDE_OK = (60, 150, 90)


# ---------------------------------------------------------------------------
# 1) PNG isolado de cada componente (papel + transparente)
# ---------------------------------------------------------------------------
def _fundo_transparente(fn):
    base = papel()
    d = ImageDraw.Draw(base)
    im = fn(base, d)
    im = im or base
    rgba = im.convert("RGBA")
    px = rgba.load()
    pap = PAPEL
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if abs(r - pap[0]) <= 7 and abs(g - pap[1]) <= 7 and abs(b - pap[2]) <= 7:
                px[x, y] = (r, g, b, 0)
    return im, rgba


def comp_piramide_dinheiro(base, d):
    C.piramide_pessoas(d, 540, 780, s=1.0, dinheiro=True)
    return base

def comp_piramide_colapso(base, d):
    C.piramide_pessoas(d, 540, 780, s=1.0, colapso=True)
    return base

def comp_pilha_dinheiro(base, d):
    C.pilha_dinheiro(d, 540, 740, s=1.6)
    return base

def comp_fonte_venda(base, d):
    C.fonte_dinheiro(d, 420, 760, s=1.2, modo="venda")
    return base

def comp_fonte_adesao(base, d):
    C.fonte_dinheiro(d, 380, 760, s=1.2, modo="adesao")
    return base

def comp_convite_confianca(base, d):
    C.convite_confianca(d, 540, 820, s=1.3)
    return base

def comp_icone_avestruz(base, d):
    C.icone_avestruz(d, 540, 780, s=1.4)
    return base

def comp_icone_gado(base, d):
    C.icone_gado(d, 540, 760, s=1.4)
    return base

def comp_icone_bitcoin(base, d):
    C.icone_bitcoin(d, 540, 760, s=1.8)
    return base

def comp_martelo_juiz(base, d):
    C.martelo_juiz(d, 540, 740, s=1.4)
    return base

def comp_caixa_caso(base, d):
    C.caixa_caso(d, 540, 760, s=1.1, nome="Avestruz Master",
                 ano="2005", pena="12 a 13 anos e meio")
    return base

def comp_pessoa_ou_dinheiro(base, d):
    C.pessoa_ou_dinheiro(d, 540, 780, s=1.3)
    return base


COMPONENTES = [
    ("piramide_dinheiro", comp_piramide_dinheiro),
    ("piramide_colapso", comp_piramide_colapso),
    ("pilha_dinheiro", comp_pilha_dinheiro),
    ("fonte_venda", comp_fonte_venda),
    ("fonte_adesao", comp_fonte_adesao),
    ("convite_confianca", comp_convite_confianca),
    ("icone_avestruz", comp_icone_avestruz),
    ("icone_gado", comp_icone_gado),
    ("icone_bitcoin", comp_icone_bitcoin),
    ("martelo_juiz", comp_martelo_juiz),
    ("caixa_caso", comp_caixa_caso),
    ("pessoa_ou_dinheiro", comp_pessoa_ou_dinheiro),
]


def gerar_isolados():
    pngs = {}
    for nome, fn in COMPONENTES:
        im, rgba = _fundo_transparente(fn)
        im.convert("RGB").save(os.path.join(PASTA, nome + ".png"), quality=92)
        rgba.save(os.path.join(PASTA_T, nome + ".png"))
        pngs[nome] = im
    print(f"  {len(pngs)} componentes (papel + transparente)")
    return pngs


def gerar_contato(pngs):
    cols, cell = 4, 254
    nomes = [n for n, _ in COMPONENTES]
    linhas = math.ceil(len(nomes) / cols)
    folha = Image.new("RGB", (cols * cell + 40, linhas * (cell + 30) + 40), PAPEL)
    dd = ImageDraw.Draw(folha)
    from media.sketch_lib import fonte as _f
    ft = _f(22, True)
    for i, nome in enumerate(nomes):
        c, r = i % cols, i // cols
        x0 = 20 + c * cell
        y0 = 20 + r * (cell + 30)
        dd.text((x0, y0), nome, font=ft, fill=INK)
        mini = pngs[nome].resize((cell - 10, int((cell - 10) * H / W)))
        crop = mini.crop((0, int(mini.height * 0.26), mini.width, int(mini.height * 0.64)))
        folha.paste(crop, (x0, y0 + 26))
    folha.save(os.path.join(PASTA, "contato.jpg"), quality=88)
    print("  contato.jpg")


# ---------------------------------------------------------------------------
# 2) Posicoes por cena (FONTE UNICA; o componentes.md reflete isto).
# ---------------------------------------------------------------------------
def layout_cenas():
    cenas = {}

    # ----- CENA 1: gancho (a pergunta) -----
    tit1 = (540, 300)
    pir1 = (540, 950, 1.0)
    cenas[1] = [
        {"nome": "titulo", "tipo": "texto", "box": (160, 230, 760, 160),
         "draw": lambda im, d: texto_multilinha(d, 540, 300, ["o que é", "esquema de pirâmide?"], 68)},
        {"nome": "piramide_dinheiro", "tipo": "obj",
         "box": C.piramide_pessoas_box(pir1[0], pir1[1], pir1[2], dinheiro=True),
         "draw": lambda im, d: C.piramide_pessoas(d, pir1[0], pir1[1], s=pir1[2], dinheiro=True)},
    ]

    # ----- CENA 2: o que e (dinheiro sobe / base perde tudo) -----
    tit2 = (540, 300)
    pir2 = (540, 900, 1.0)
    rot2 = (540, 1340)
    cenas[2] = [
        {"nome": "titulo", "tipo": "texto", "box": (210, 270, 660, 60),
         "draw": lambda im, d: texto(d, *tit2, "quando para de entrar", 56)},
        {"nome": "piramide_colapso", "tipo": "obj",
         "box": C.piramide_pessoas_box(pir2[0], pir2[1], pir2[2]),
         "draw": lambda im, d: C.piramide_pessoas(d, pir2[0], pir2[1], s=pir2[2], colapso=True)},
        {"nome": "rotulo", "tipo": "texto", "box": (260, 1312, 560, 56),
         "draw": lambda im, d: texto(d, *rot2, "a base perde tudo", 56, VERMELHO)},
    ]

    # ----- CENA 3: a diferenca (venda real x adesao) -----
    tit3 = (540, 280)
    fv3 = (380, 640, 1.1)
    rotv3 = (420, 500)
    fa3 = (360, 1120, 1.1)
    rota3 = (420, 980)
    cenas[3] = [
        {"nome": "titulo", "tipo": "texto", "box": (210, 250, 660, 60),
         "draw": lambda im, d: texto(d, *tit3, "de onde vem o dinheiro", 52)},
        {"nome": "rot_venda", "tipo": "texto", "box": (160, 474, 560, 52),
         "draw": lambda im, d: texto(d, *rotv3, "multinível: venda real", 50, VERDE_OK, ancora="lm")},
        {"nome": "fonte_venda", "tipo": "obj",
         "box": C.fonte_dinheiro_box(fv3[0], fv3[1], fv3[2], "venda"),
         "draw": lambda im, d: C.fonte_dinheiro(d, fv3[0], fv3[1], s=fv3[2], modo="venda")},
        {"nome": "rot_adesao", "tipo": "texto", "box": (160, 954, 560, 52),
         "draw": lambda im, d: texto(d, *rota3, "pirâmide: só adesão", 50, LARANJA, ancora="lm")},
        {"nome": "fonte_adesao", "tipo": "obj",
         "box": C.fonte_dinheiro_box(fa3[0], fa3[1], fa3[2], "adesao"),
         "draw": lambda im, d: C.fonte_dinheiro(d, fa3[0], fa3[1], s=fa3[2], modo="adesao")},
    ]

    # ----- CENA 4: confianca (convite pela pessoa) -----
    tit4 = (540, 300)
    conv4 = (540, 820, 1.3)
    rot4 = (540, 1220)
    cenas[4] = [
        {"nome": "titulo", "tipo": "texto", "box": (210, 270, 660, 60),
         "draw": lambda im, d: texto(d, *tit4, "o convite vem de quem", 54)},
        {"nome": "convite_confianca", "tipo": "boneco",
         "box": C.convite_confianca_box(conv4[0], conv4[1], conv4[2]),
         "draw": lambda im, d: C.convite_confianca(d, conv4[0], conv4[1], s=conv4[2])},
        {"nome": "rotulo", "tipo": "texto", "box": (300, 1194, 480, 52),
         "draw": lambda im, d: texto(d, *rot4, "voce confia", 54, AZUL)},
    ]

    # ----- CENA 5: casos reais (cartao do caso + martelo) -----
    caso5 = (540, 650, 1.1)
    mart5 = (540, 1080, 1.0)
    cenas[5] = [
        {"nome": "caixa_caso", "tipo": "texto",
         "box": C.caixa_caso_box(caso5[0], caso5[1], caso5[2]),
         "draw": lambda im, d: C.caixa_caso(d, caso5[0], caso5[1], s=caso5[2],
                                            nome="Avestruz Master", ano="2005",
                                            pena="12 a 13 anos e meio")},
        {"nome": "martelo_juiz", "tipo": "obj",
         "box": C.martelo_juiz_box(mart5[0], mart5[1], mart5[2]),
         "draw": lambda im, d: C.martelo_juiz(d, mart5[0], mart5[1], s=mart5[2])},
    ]

    # ----- CENA 6: mesma mecanica (gado / avestruz / bitcoin) -----
    tit6 = (540, 300)
    g6 = (260, 760, 0.9)
    a6 = (540, 760, 0.9)
    b6 = (820, 760, 1.0)
    rot6 = (540, 1200)
    cenas[6] = [
        {"nome": "titulo", "tipo": "texto", "box": (240, 270, 600, 60),
         "draw": lambda im, d: texto(d, *tit6, "muda a fachada", 60)},
        {"nome": "icone_gado", "tipo": "obj", "box": C.icone_gado_box(g6[0], g6[1], g6[2]),
         "draw": lambda im, d: C.icone_gado(d, g6[0], g6[1], s=g6[2])},
        {"nome": "icone_avestruz", "tipo": "obj", "box": C.icone_avestruz_box(a6[0], a6[1], a6[2]),
         "draw": lambda im, d: C.icone_avestruz(d, a6[0], a6[1], s=a6[2])},
        {"nome": "icone_bitcoin", "tipo": "obj", "box": C.icone_bitcoin_box(b6[0], b6[1], b6[2]),
         "draw": lambda im, d: C.icone_bitcoin(d, b6[0], b6[1], s=b6[2])},
        {"nome": "rotulo", "tipo": "texto", "box": (210, 1174, 660, 52),
         "draw": lambda im, d: texto(d, *rot6, "a mecânica se repete", 54)},
    ]

    # ----- CENA 7: pergunta de volta -----
    tit7 = (540, 300)
    pod7 = (540, 820, 1.3)
    rot7 = (540, 1240)
    cenas[7] = [
        {"nome": "titulo", "tipo": "texto", "box": (190, 270, 700, 60),
         "draw": lambda im, d: texto(d, *tit7, "o que você confere?", 56)},
        {"nome": "pessoa_ou_dinheiro", "tipo": "boneco",
         "box": C.pessoa_ou_dinheiro_box(pod7[0], pod7[1], pod7[2]),
         "draw": lambda im, d: C.pessoa_ou_dinheiro(d, pod7[0], pod7[1], s=pod7[2])},
        {"nome": "rot_pessoa", "tipo": "texto", "box": (180, 1214, 300, 52),
         "draw": lambda im, d: texto(d, 320, 1240, "a pessoa", 50, AZUL)},
        {"nome": "rot_dinheiro", "tipo": "texto", "box": (600, 1214, 320, 52),
         "draw": lambda im, d: texto(d, 760, 1240, "ou o dinheiro", 50, INK)},
    ]
    return cenas


def _cruzam(a, b, folga=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + folga <= bx or bx + bw + folga <= ax or
                ay + ah + folga <= by or by + bh + folga <= ay)


def verificar(cenas):
    problemas = []
    for n, elems in cenas.items():
        for i, e in enumerate(elems):
            x, y, w, h = e["box"]
            if y < SEGURO_TOPO - 2 or y + h > SEGURO_BASE + 2:
                problemas.append(f"cena {n}: '{e['nome']}' fora do seguro (y={y:.0f}..{y+h:.0f})")
            for j, o in enumerate(elems):
                if i >= j:
                    continue
                if e["tipo"] in ("boneco", "texto") or o["tipo"] in ("boneco", "texto"):
                    if _cruzam(e["box"], o["box"]):
                        problemas.append(f"cena {n}: '{e['nome']}' cruza '{o['nome']}'")
    return problemas


def gerar_cenas_exemplo(cenas):
    cols = 4
    linhas = math.ceil(len(cenas) / cols)
    esc = 0.33
    cw, ch = int(W * esc), int(H * esc)
    folha = Image.new("RGB", (cols * (cw + 16) + 16, linhas * (ch + 40) + 16), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    from media.sketch_lib import fonte as _f
    ft = _f(26, True)
    for pos, idx in enumerate(sorted(cenas)):
        im = papel()
        d = ImageDraw.Draw(im)
        for e in cenas[idx]:
            r = e["draw"](im, d)
            if r is not None:
                im = r
                d = ImageDraw.Draw(im)
        c, r = pos % cols, pos // cols
        x0 = 16 + c * (cw + 16)
        y0 = 16 + r * (ch + 40)
        dd.text((x0, y0), f"cena {idx}", font=ft, fill=INK)
        folha.paste(im.resize((cw, ch)), (x0, y0 + 32))
    folha.save(os.path.join(PASTA, "cenas_exemplo.jpg"), quality=88)
    print("  cenas_exemplo.jpg")


if __name__ == "__main__":
    print("Gerando assets...")
    pngs = gerar_isolados()
    gerar_contato(pngs)
    cenas = layout_cenas()
    probs = verificar(cenas)
    gerar_cenas_exemplo(cenas)
    print("\nVerificacao de sobreposicao:")
    if probs:
        for p in probs:
            print("  [X]", p)
    else:
        print("  [OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.")
