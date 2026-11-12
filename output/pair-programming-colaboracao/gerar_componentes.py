"""Gera os assets definitivos do video pair-programming-colaboracao:
 - componentes/<nome>.png            (fundo de papel, 1 por componente)
 - componentes/transparentes/<nome>.png  (RGBA, fundo transparente)
 - componentes/contato.jpg           (todos juntos, rotulados)
 - componentes/cenas_exemplo.jpg     (cada cena composta nas posicoes do componentes.md)
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
    """Desenha fn(d, im) sobre papel, depois extrai so os pixels != papel para RGBA."""
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


# cada entrada: nome -> (funcao de desenho no centro do quadro, caixa crop opcional)
def comp_tela_codigo(base, d):
    C.tela_codigo(d, 540, 760, s=1.1)
    return base

def comp_tela_riscada(base, d):
    C.tela_riscada(d, 540, 760, s=1.1)
    texto(d, 540, 1060, "nao e isso", 54, VERMELHO)
    return base

def comp_dupla_pair(base, d):
    C.dupla_pair(d, 540, 900, s=1.5, dist=240, papeis=("escreve", "revisa e sugere"))
    return base

def comp_caixa_problema(base, d):
    C.caixa_problema(d, 540, 760, s=1.3)
    return base

def comp_balao_fala(base, d):
    C.balao_fala(d, 540, 640, ["e se a gente", "tentar isso?"], larg=440, alt=200, cor_borda=AZUL)
    C.balao_fala(d, 540, 940, ["por que assim?"], larg=440, alt=160, cor_borda=LARANJA, seed=33)
    return base

def comp_teclado(base, d):
    C.teclado(d, 540, 760, s=1.6)
    return base

def comp_lupa_revisao(base, d):
    C.lupa_revisao(d, 540, 740, s=1.2)
    return base

def comp_setas_troca(base, d):
    C.setas_troca(d, 540, 760, s=1.4, dist=380)
    return base

def comp_check_solucao(base, d):
    return C.check_solucao(base, d, 540, 760, s=3.0)

def comp_ganho_contexto(base, d):
    C.ganho_contexto(d, 360, 760, s=1.3)
    return base

def comp_ganho_conhecimento(base, d):
    C.ganho_conhecimento(d, 340, 760, s=1.3)
    return base

def comp_ganho_decisao(base, d):
    C.ganho_decisao(d, 360, 760, s=1.3)
    return base

def comp_boneco_pensando(base, d):
    C.boneco_pensando(d, 540, 900, s=1.7, t=0.3)
    return base


COMPONENTES = [
    ("tela_codigo", comp_tela_codigo),
    ("tela_riscada", comp_tela_riscada),
    ("dupla_pair", comp_dupla_pair),
    ("caixa_problema", comp_caixa_problema),
    ("balao_fala", comp_balao_fala),
    ("teclado", comp_teclado),
    ("lupa_revisao", comp_lupa_revisao),
    ("setas_troca", comp_setas_troca),
    ("check_solucao", comp_check_solucao),
    ("ganho_contexto", comp_ganho_contexto),
    ("ganho_conhecimento", comp_ganho_conhecimento),
    ("ganho_decisao", comp_ganho_decisao),
    ("boneco_pensando", comp_boneco_pensando),
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
        # recorta a faixa central vertical (onde o componente foi desenhado)
        crop = mini.crop((0, int(mini.height * 0.30), mini.width, int(mini.height * 0.62)))
        folha.paste(crop, (x0, y0 + 26))
    folha.save(os.path.join(PASTA, "contato.jpg"), quality=88)
    print("  contato.jpg")


# ---------------------------------------------------------------------------
# 2) Posicoes por cena (FONTE UNICA; o componentes.md reflete isto).
#    Cada item: (chave, kwargs_de_desenho, caixa (x,y,w,h), eh_boneco_ou_texto)
# ---------------------------------------------------------------------------
def layout_cenas():
    """Devolve dict cena -> lista de elementos. Cada elemento:
       {'nome','box','tipo'('boneco'|'texto'|'obj'),'draw'(callable(im,d)->im|None)}."""
    cenas = {}

    # ----- CENA 0: negacao -----
    titulo0 = (540, 290)
    tela0 = (540, 620, 1.0)                        # FIX2: tela menor e mais alta; X cabe dentro dela
    rot0 = (540, 940)                              # FIX2: rotulo na faixa livre entre tela e bonecos
    dupla0 = (540, 1250, 1.35, 300)                # FIX2: bonecos bem abaixo, sem o X perto das cabecas
    cenas[0] = [
        {"nome": "titulo", "tipo": "texto", "box": (300, 258, 480, 64),
         "draw": lambda im, d: texto(d, *titulo0, "pair programming", 70)},
        {"nome": "tela_riscada", "tipo": "obj", "box": C.tela_riscada_box(tela0[0], tela0[1], tela0[2]),
         "draw": lambda im, d: C.tela_riscada(d, tela0[0], tela0[1], s=tela0[2])},
        {"nome": "rotulo_nao", "tipo": "texto", "box": (400, 913, 280, 54),
         "draw": lambda im, d: texto(d, *rot0, "nao e isso", 54, VERMELHO)},
        {"nome": "dupla_pair", "tipo": "boneco", "box": C.dupla_pair_box(dupla0[0], dupla0[1], dupla0[2], dupla0[3]),
         "draw": lambda im, d: C.dupla_pair(d, dupla0[0], dupla0[1], s=dupla0[2], dist=dupla0[3])},
    ]

    # ----- CENA 1: discussao -----
    bA = (320, 420)                     # balao A no alto-esq
    bB = (760, 650)                     # balao B abaixo-dir, escalonado, sem cruzar o A
    dupla1 = (540, 1000, 1.3, 340)      # dupla no meio-baixo
    caixa1 = (540, 1350, 0.95)          # caixa 'o mesmo problema' na base, abaixo dos pes
    cenas[1] = [
        {"nome": "balao_A", "tipo": "texto", "box": C.balao_fala_box(bA[0], bA[1], 420, 180),
         "draw": lambda im, d: C.balao_fala(d, bA[0], bA[1], ["e se a gente", "tentar isso?"], larg=420, alt=180, cor_borda=AZUL)},
        {"nome": "balao_B", "tipo": "texto", "box": C.balao_fala_box(bB[0], bB[1], 420, 150),
         "draw": lambda im, d: C.balao_fala(d, bB[0], bB[1], ["por que assim?"], larg=420, alt=150, cor_borda=LARANJA, seed=33)},
        {"nome": "dupla_pair", "tipo": "boneco", "box": C.dupla_pair_box(dupla1[0], dupla1[1], dupla1[2], dupla1[3]),
         "draw": lambda im, d: C.dupla_pair(d, dupla1[0], dupla1[1], s=dupla1[2], dist=dupla1[3])},
        {"nome": "caixa_problema", "tipo": "obj", "box": C.caixa_problema_box(caixa1[0], caixa1[1], caixa1[2]),
         "draw": lambda im, d: C.caixa_problema(d, caixa1[0], caixa1[1], s=caixa1[2])},
    ]

    # ----- CENA 2: papeis (FIX1: teclado/lupa bem abaixo dos pes) -----
    tela2 = (540, 560, 0.95)
    dupla2 = (540, 980, 1.35, 440)
    tecl2 = (320, 1300, 1.3)     # FIX1: y 1300, longe dos pes (~1149)
    lupa2 = (760, 1290, 1.0)
    cenas[2] = [
        {"nome": "tela_codigo", "tipo": "obj", "box": C.tela_codigo_box(tela2[0], tela2[1], tela2[2]),
         "draw": lambda im, d: C.tela_codigo(d, tela2[0], tela2[1], s=tela2[2], cores=[AZUL, AZUL, AZUL, AZUL])},
        {"nome": "dupla_pair", "tipo": "boneco", "box": C.dupla_pair_box(dupla2[0], dupla2[1], dupla2[2], dupla2[3]),
         "draw": lambda im, d: C.dupla_pair(d, dupla2[0], dupla2[1], s=dupla2[2], dist=dupla2[3])},
        {"nome": "teclado", "tipo": "obj", "box": C.teclado_box(tecl2[0], tecl2[1], tecl2[2]),
         "draw": lambda im, d: C.teclado(d, tecl2[0], tecl2[1], s=tecl2[2])},
        {"nome": "lupa_revisao", "tipo": "obj", "box": C.lupa_revisao_box(lupa2[0], lupa2[1], lupa2[2]),
         "draw": lambda im, d: C.lupa_revisao(d, lupa2[0], lupa2[1], s=lupa2[2])},
        {"nome": "rot_escreve", "tipo": "texto", "box": (220, 1428, 200, 44),
         "draw": lambda im, d: texto(d, 320, 1450, "escreve", 44, AZUL)},
        {"nome": "rot_revisa", "tipo": "texto", "box": (610, 1428, 300, 44),
         "draw": lambda im, d: texto(d, 760, 1450, "revisa e sugere", 44, LARANJA)},
    ]

    # ----- CENA 3: troca -----
    titulo3 = (540, 300)
    dupla3 = (540, 820, 1.3, 440)
    setas3 = (540, 1130, 1.3, 360)
    cenas[3] = [
        {"nome": "titulo", "tipo": "texto", "box": (330, 268, 420, 64),
         "draw": lambda im, d: texto(d, *titulo3, "troca de papel", 70)},
        {"nome": "dupla_pair", "tipo": "boneco", "box": C.dupla_pair_box(dupla3[0], dupla3[1], dupla3[2], dupla3[3]),
         "draw": lambda im, d: C.dupla_pair(d, dupla3[0], dupla3[1], s=dupla3[2], dist=dupla3[3])},
        {"nome": "setas_troca", "tipo": "obj", "box": C.setas_troca_box(setas3[0], setas3[1], setas3[2], setas3[3]),
         "draw": lambda im, d: C.setas_troca(d, setas3[0], setas3[1], s=setas3[2], dist=setas3[3])},
    ]

    # ----- CENA 4: solucao (FIX4: rotulo e check em alturas distintas) -----
    tela4 = (540, 560, 0.9)
    dupla4 = (540, 1000, 1.25, 620)   # bonecos afastados
    rot4 = (540, 1200)                # FIX4: rotulo acima
    check4 = (540, 1350, 2.6)         # FIX4: check bem abaixo do rotulo, no vao entre bonecos
    cenas[4] = [
        {"nome": "tela_codigo", "tipo": "obj", "box": C.tela_codigo_box(tela4[0], tela4[1], tela4[2]),
         "draw": lambda im, d: C.tela_codigo(d, tela4[0], tela4[1], s=tela4[2],
                                             cores=[AZUL, LARANJA, AZUL, LARANJA, AZUL])},
        {"nome": "dupla_pair", "tipo": "boneco", "box": C.dupla_pair_box(dupla4[0], dupla4[1], dupla4[2], dupla4[3]),
         "draw": lambda im, d: C.dupla_pair(d, dupla4[0], dupla4[1], s=dupla4[2], dist=dupla4[3])},
        {"nome": "rot_solucao", "tipo": "texto", "box": (300, 1174, 480, 52),
         "draw": lambda im, d: texto(d, *rot4, "solucao em conjunto", 52, VERDE_OK)},
        {"nome": "check_solucao", "tipo": "obj", "box": C.check_solucao_box(check4[0], check4[1], check4[2]),
         "draw": lambda im, d: C.check_solucao(im, d, check4[0], check4[1], s=check4[2])},
    ]

    # ----- CENA 5: tres ganhos (FIX3 ja no componente) -----
    titulo5 = (540, 300)
    g1 = (300, 640, 1.0)
    g2 = (300, 940, 1.0)
    g3 = (300, 1240, 1.0)
    cenas[5] = [
        {"nome": "titulo", "tipo": "texto", "box": (300, 268, 480, 64),
         "draw": lambda im, d: texto(d, *titulo5, "pair programming e:", 66)},
        {"nome": "ganho_contexto", "tipo": "obj", "box": C.ganho_contexto_box(g1[0], g1[1], g1[2]),
         "draw": lambda im, d: C.ganho_contexto(d, g1[0], g1[1], s=g1[2])},
        {"nome": "ganho_conhecimento", "tipo": "obj", "box": C.ganho_conhecimento_box(g2[0], g2[1], g2[2]),
         "draw": lambda im, d: C.ganho_conhecimento(d, g2[0], g2[1], s=g2[2])},
        {"nome": "ganho_decisao", "tipo": "obj", "box": C.ganho_decisao_box(g3[0], g3[1], g3[2]),
         "draw": lambda im, d: C.ganho_decisao(d, g3[0], g3[1], s=g3[2])},
    ]

    # ----- CENA 6: pergunta -----
    bA6 = (540, 420)
    bB6 = (540, 640)
    bon6 = (540, 1280, 1.5)
    cenas[6] = [
        {"nome": "balao_A", "tipo": "texto", "box": C.balao_fala_box(bA6[0], bA6[1], 620, 170),
         "draw": lambda im, d: C.balao_fala(d, bA6[0], bA6[1], ["ja fez pair programming?"], larg=620, alt=170, tam=48, cor_borda=AZUL)},
        {"nome": "balao_B", "tipo": "texto", "box": C.balao_fala_box(bB6[0], bB6[1], 560, 150),
         "draw": lambda im, d: C.balao_fala(d, bB6[0], bB6[1], ["o que voce aprendeu?"], larg=560, alt=150, tam=48, cor_borda=LARANJA, seed=35)},
        {"nome": "boneco_pensando", "tipo": "boneco", "box": C.boneco_pensando_box(bon6[0], bon6[1], bon6[2]),
         "draw": lambda im, d: C.boneco_pensando(d, bon6[0], bon6[1], s=bon6[2], t=0.3)},
    ]
    return cenas


def _cruzam(a, b, folga=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + folga <= bx or bx + bw + folga <= ax or
                ay + ah + folga <= by or by + bh + folga <= ay)


def verificar(cenas):
    """Boneco e texto nao podem ser cruzados por nenhum outro elemento. Fora do seguro tambem reporta."""
    problemas = []
    for n, elems in cenas.items():
        for i, e in enumerate(elems):
            x, y, w, h = e["box"]
            if y < SEGURO_TOPO - 2 or y + h > SEGURO_BASE + 2:
                problemas.append(f"cena {n}: '{e['nome']}' fora do seguro (y={y:.0f}..{y+h:.0f})")
            for j, o in enumerate(elems):
                if i >= j:
                    continue
                # so e violacao se um dos dois for boneco ou texto
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
    for idx in sorted(cenas):
        im = papel()
        d = ImageDraw.Draw(im)
        for e in cenas[idx]:
            r = e["draw"](im, d)
            if r is not None:
                im = r
                d = ImageDraw.Draw(im)
        c, r = idx % cols, idx // cols
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
