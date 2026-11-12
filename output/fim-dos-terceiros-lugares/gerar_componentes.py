"""Gera os assets do video fim-dos-terceiros-lugares (so deste slug):
 - componentes/<nome>.png                 (fundo de papel, 1 por componente)
 - componentes/transparentes/<nome>.png   (RGBA, fundo transparente)
 - componentes/contato.jpg                (todos juntos, rotulados)
 - componentes/cenas_exemplo.jpg          (cada cena composta nas posicoes do componentes.md)
E roda a verificacao automatica de sobreposicao (caixas de boneco/texto x outros),
da area segura vertical (SEGURO_TOPO..SEGURO_BASE) e horizontal (margem do caderno x=150 .. 1060).
Nao renderiza video nem gera narracao.

Rodar da raiz:  python output/fim-dos-terceiros-lugares/gerar_componentes.py
"""
import os
import sys
import math
import importlib.util
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)

from media.sketch_lib import *  # noqa: E402
from media import sketch_componentes as SC  # noqa: E402  (reuso do catalogo: balao_fala)

_AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("componentes_video_terceiros", os.path.join(_AQUI, "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

PASTA = os.path.join(_AQUI, "componentes")
PASTA_T = os.path.join(PASTA, "transparentes")
os.makedirs(PASTA_T, exist_ok=True)

X_MIN, X_MAX = 150, 1060
VERDE_OK = (60, 150, 90)


# ---------------------------------------------------------------------------
# 1) PNG isolado de cada componente (papel + transparente)
# ---------------------------------------------------------------------------
COMPONENTES = [
    ("mesa_cafe", lambda im, d: C.mesa_cafe(d, 540, 820, s=1.4, cadeiras=2, xicaras=2, vapor=True, t=0.6)),
    ("cadeira_cafe", lambda im, d: C.cadeira_cafe(d, 540, 900, s=1.8)),
    ("xicara_cafe", lambda im, d: C.xicara_cafe(d, 540, 860, s=1.8, vapor=True, t=0.4)),
    ("pilha_livros", lambda im, d: C.pilha_livros(d, 540, 860, s=1.8)),
    ("maleta_trabalho", lambda im, d: C.maleta_trabalho(d, 540, 860, s=1.6)),
    ("selo_numero", lambda im, d: (C.selo_numero(d, 380, 860, s=1.6, txt="1º", cor=FERRO),
                                   C.selo_numero(d, 540, 860, s=1.6, txt="2º", cor=FERRO),
                                   C.selo_numero(d, 700, 860, s=1.6, txt="3º", cor=LARANJA))),
    ("coluna_relogios", lambda im, d: (C.coluna_relogios(d, 400, 1240, s=1.0, horas=6.8, cor=AZUL, t=0.5),
                                       C.coluna_relogios(d, 680, 1240, s=1.0, horas=2.7, cor=AZUL, t=0.5))),
    ("cartao_variacao", lambda im, d: (C.cartao_variacao(d, 350, 860, s=1.0, valor="-7,1%", rotulo="saídas",
                                                         sentido=-1, cor=VERMELHO, icone="porta"),
                                       C.cartao_variacao(d, 770, 860, s=1.0, valor="+28,3%", rotulo="gasto por saída",
                                                         sentido=1, cor=LARANJA, icone="moeda"))),
    ("relogio_sem_medida", lambda im, d: C.relogio_sem_medida(d, 540, 860, s=1.6)),
    ("banco_praca", lambda im, d: (C.banco_praca(d, 540, 800, s=1.2, sumindo=False),
                                   C.banco_praca(d, 540, 1230, s=1.2, sumindo=True))),
    ("recibo_orcamento", lambda im, d: C.recibo_orcamento(d, 540, 860, s=1.3)),
    ("selo_hipotese", lambda im, d: C.selo_hipotese(d, 540, 860, s=1.3)),
    ("tv_streaming", lambda im, d: C.tv_streaming(d, 540, 860, s=1.3, t=2.0)),
    ("celular_video", lambda im, d: C.celular_video(d, 540, 860, s=2.0)),
    ("sofa_sozinho", lambda im, d: C.sofa_sozinho(d, 540, 900, s=1.5)),
    ("mistura_causas", lambda im, d: C.mistura_causas(d, 540, 860, s=1.4)),
    ("fila_idades", lambda im, d: C.fila_idades(d, 540, 900, s=1.25)),
]


def _desenha(fn):
    base = papel()
    d = ImageDraw.Draw(base)
    r = fn(base, d)
    return r if isinstance(r, Image.Image) else base


def _transparente(im):
    rgba = im.convert("RGBA")
    px = rgba.load()
    p = PAPEL
    pauta = PAUTA
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, _ = px[x, y]
            if (abs(r - p[0]) <= 7 and abs(g - p[1]) <= 7 and abs(b - p[2]) <= 7) or \
               (abs(r - pauta[0]) <= 6 and abs(g - pauta[1]) <= 6 and abs(b - pauta[2]) <= 6):
                px[x, y] = (r, g, b, 0)
    return rgba


def gerar_isolados(transparentes=True):
    pngs = {}
    for nome, fn in COMPONENTES:
        im = _desenha(fn)
        im.save(os.path.join(PASTA, nome + ".png"))
        if transparentes:
            _transparente(im).save(os.path.join(PASTA_T, nome + ".png"))
        pngs[nome] = im
    print(f"  {len(pngs)} componentes (papel{' + transparente' if transparentes else ''})")
    return pngs


def gerar_contato(pngs):
    cols, cw = 4, 300
    nomes = [n for n, _ in COMPONENTES]
    lin = math.ceil(len(nomes) / cols)
    y_ini, y_fim = 0.24, 0.72          # recorte vertical (a parte com desenho)
    ch = int(cw * H / W * (y_fim - y_ini))
    folha = Image.new("RGB", (cols * (cw + 14) + 14, lin * (ch + 44) + 14), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    ft = fonte(26, True)
    for i, nome in enumerate(nomes):
        c, r = i % cols, i // cols
        x0, y0 = 14 + c * (cw + 14), 14 + r * (ch + 44)
        dd.text((x0, y0), f"{i + 1}. {nome}", font=ft, fill=INK)
        mini = pngs[nome].resize((cw, int(cw * H / W)), Image.LANCZOS)
        folha.paste(mini.crop((0, int(mini.height * y_ini), cw, int(mini.height * y_ini) + ch)), (x0, y0 + 36))
        dd.rectangle([x0, y0 + 36, x0 + cw - 1, y0 + 36 + ch - 1], outline=(200, 200, 200))
    folha.save(os.path.join(PASTA, "contato.jpg"), quality=90)
    print("  contato.jpg")


# ---------------------------------------------------------------------------
# 2) Posicoes por cena (FONTE UNICA; o componentes.md reflete isto)
# ---------------------------------------------------------------------------
def T(nome, x, y, s, tam, cor=INK, ancora="mm"):
    """Elemento de texto com caixa medida pela fonte real."""
    l, t, r, b = fonte(tam).getbbox(s, anchor=ancora)
    return {"nome": nome, "tipo": "texto", "box": (x + l, y + t, r - l, b - t),
            "draw": lambda im, d: texto(d, x, y, s, tam, cor, ancora)}


def O(nome, tipo, box, draw):
    return {"nome": nome, "tipo": tipo, "box": box, "draw": draw}


def layout_cenas():
    cenas = {}

    # ----- CENA 1: gancho (mesa de cafe vazia) -----
    m1 = (540, 880, 1.28)
    cenas["1"] = [
        T("titulo", 540, 300, "seu 3º lugar sumiu", 74),
        O("mesa_cafe", "obj", C.mesa_cafe_box(m1[0], m1[1], m1[2], cadeiras=2, xicaras=1, vapor=False),
          lambda im, d: C.mesa_cafe(d, m1[0], m1[1], s=m1[2], cadeiras=2, xicaras=1, vapor=False)),
    ]

    # ----- CENA 2: definicao (casa 1º, trabalho 2º, terceiro lugar = cafe, bar, livraria) -----
    ca2, ml2 = (330, 560, 0.75), (760, 580, 0.85)
    sel2 = (540, 800, 1.2)
    xi2, cp2, lv2 = (300, 1070, 1.0), (540, 1070, 0.72), (790, 1070, 1.0)
    cenas["2"] = [
        T("titulo", 540, 290, "o terceiro lugar", 70),
        O("casa", "obj", (ca2[0] - 125 * ca2[2], ca2[1] - 132 * ca2[2], 250 * ca2[2], 234 * ca2[2]),
          lambda im, d: casa(d, ca2[0], ca2[1], s=ca2[2], seed=3, cor=_cl(FERRO))),
        T("rot_casa", 330, 690, "1º casa", 46, FERRO),
        O("maleta_trabalho", "obj", C.maleta_trabalho_box(*ml2),
          lambda im, d: C.maleta_trabalho(d, ml2[0], ml2[1], s=ml2[2])),
        T("rot_trab", 760, 690, "2º trabalho", 46, FERRO),
        O("selo_3", "texto", C.selo_numero_box(*sel2),
          lambda im, d: C.selo_numero(d, sel2[0], sel2[1], s=sel2[2], txt="3º", cor=LARANJA)),
        O("xicara_cafe", "obj", C.xicara_cafe_box(*xi2, vapor=True),
          lambda im, d: C.xicara_cafe(d, xi2[0], xi2[1], s=xi2[2], vapor=True, t=0.5)),
        O("copo_bar", "obj", (cp2[0] - 82 * cp2[2], cp2[1] - 118 * cp2[2], 164 * cp2[2], 236 * cp2[2]),
          lambda im, d: copo(d, cp2[0], cp2[1], s=cp2[2], seed=8)),
        O("pilha_livros", "obj", C.pilha_livros_box(*lv2),
          lambda im, d: C.pilha_livros(d, lv2[0], lv2[1], s=lv2[2])),
        T("rot_cafe", 300, 1235, "café", 48),
        T("rot_bar", 540, 1235, "bar", 48),
        T("rot_livraria", 790, 1235, "livraria", 48),
        T("rot_oldenburg", 540, 1380, "sociólogo Ray Oldenburg", 50, AZUL),
    ]

    # ----- CENA 3: EUA, horas por semana com amigos -----
    c13, c21, yb3 = 360, 720, 1250
    cenas["3"] = [
        T("titulo", 540, 270, "EUA (pesquisa ATUS)", 64),
        T("subtitulo", 540, 350, "horas/semana com amigos", 50, AZUL),
        T("rot_quase7", c13, 470, "quase 7 h", 58),
        O("coluna_2013", "obj", C.coluna_relogios_box(c13, yb3, 1.0, 6.8),
          lambda im, d: C.coluna_relogios(d, c13, yb3, s=1.0, horas=6.8, cor=AZUL, t=0.5)),
        T("rot_menos3", c21, 880, "menos de 3 h", 58, LARANJA),
        O("coluna_2021", "obj", C.coluna_relogios_box(c21, yb3, 1.0, 2.7),
          lambda im, d: C.coluna_relogios(d, c21, yb3, s=1.0, horas=2.7, cor=AZUL, t=0.5, seed=20)),
        T("ano_2013", c13, 1315, "até 2013", 52),
        T("ano_2021", c21, 1315, "2021", 52),
    ]

    # ----- CENA 4a: Brasil nao tem essa medida -----
    r4 = (540, 800, 1.6)
    cenas["4a"] = [
        T("titulo", 540, 290, "e no Brasil?", 72),
        O("relogio_sem_medida", "obj", C.relogio_sem_medida_box(*r4),
          lambda im, d: C.relogio_sem_medida(d, r4[0], r4[1], s=r4[2])),
        T("rotulo", 540, 1120, "sem essa medida", 60, FERRO),
    ]

    # ----- CENA 4b: Brasil, consumo (-7,1% e +28,3%) -----
    k1, k2 = (350, 860, 1.0), (770, 860, 1.0)
    cenas["4b"] = [
        T("titulo", 540, 280, "Brasil: consumo", 70),
        T("subtitulo", 540, 360, "1º tri 2026 x 1º tri 2025", 46, FERRO),
        O("cartao_saidas", "texto", C.cartao_variacao_box(*k1),
          lambda im, d: C.cartao_variacao(d, k1[0], k1[1], s=k1[2], valor="-7,1%", rotulo="saídas",
                                          sentido=-1, cor=VERMELHO, icone="porta")),
        O("cartao_gasto", "texto", C.cartao_variacao_box(*k2),
          lambda im, d: C.cartao_variacao(d, k2[0], k2[1], s=k2[2], valor="+28,3%", rotulo="gasto por saída",
                                          sentido=1, cor=LARANJA, icone="moeda")),
    ]

    # ----- CENA 5: hipotese (lugar de graca some -> ver amigo vira orcamento) -----
    b5, r5, h5 = (540, 610, 1.15), (540, 1070, 1.0), (540, 1400, 1.0)
    cenas["5"] = [
        T("titulo", 540, 280, "nossa leitura", 66, LARANJA),
        O("banco_praca", "obj", C.banco_praca_box(*b5),
          lambda im, d: C.banco_praca(d, b5[0], b5[1], s=b5[2], sumindo=True)),
        O("seta", "obj", (540 - 30, 748, 60, 76),
          lambda im, d: seta(d, 540, 750, 540, 820, seed=55, cor=LARANJA, w=8)),
        O("recibo_orcamento", "texto", C.recibo_orcamento_box(*r5),
          lambda im, d: C.recibo_orcamento(d, r5[0], r5[1], s=r5[2])),
        O("selo_hipotese", "texto", C.selo_hipotese_box(*h5),
          lambda im, d: C.selo_hipotese(d, h5[0], h5[1], s=h5[2])),
    ]

    # ----- CENA 6: contraexemplo (as telas) -----
    tv6, sf6, cl6 = (540, 660, 1.2), (410, 1190, 0.95), (820, 1185, 1.35)
    cenas["6"] = [
        T("titulo", 540, 270, "e as telas?", 80),
        T("subtitulo", 540, 360, "economista Bryce Ward", 46, AZUL),
        O("tv_streaming", "obj", C.tv_streaming_box(*tv6),
          lambda im, d: C.tv_streaming(d, tv6[0], tv6[1], s=tv6[2], t=2.0)),
        O("sofa_sozinho", "boneco", C.sofa_sozinho_box(*sf6),
          lambda im, d: C.sofa_sozinho(d, sf6[0], sf6[1], s=sf6[2])),
        O("celular_video", "obj", C.celular_video_box(*cl6),
          lambda im, d: C.celular_video(d, cl6[0], cl6[1], s=cl6[2])),
        T("rotulo", 540, 1420, "tempo sozinho cresceu", 52),
    ]

    # ----- CENA 7a: pode ser uma mistura -----
    mx7 = (540, 820, 1.3)
    cenas["7a"] = [
        T("titulo", 540, 290, "pode ser uma mistura", 66),
        O("mistura_causas", "texto", C.mistura_causas_box(*mx7),
          lambda im, d: C.mistura_causas(d, mx7[0], mx7[1], s=mx7[2])),
    ]

    # ----- CENA 7b: queda forte nos jovens, mas nao so deles -----
    fi7 = (560, 880, 1.25)
    cenas["7b"] = [
        T("titulo", 540, 290, "EUA: queda forte", 68),
        O("fila_idades", "boneco", C.fila_idades_box(*fi7),
          lambda im, d: C.fila_idades(d, fi7[0], fi7[1], s=fi7[2])),
        T("rotulo", 540, 1360, "não parece ser só deles", 54),
    ]

    # ----- CENA 8: pergunta de volta (cadeira vazia na ultima imagem) -----
    m8 = (540, 960, 1.28)
    cenas["8"] = [
        O("balao_pergunta", "texto", SC.balao_fala_box(540, 400, larg=760, alt=250),
          lambda im, d: SC.balao_fala(d, 540, 400, ["qual encontro você", "deixou de fazer?"],
                                      larg=760, alt=250, tam=60, cor_borda=LARANJA)),
        O("mesa_cafe", "obj", C.mesa_cafe_box(m8[0], m8[1], m8[2], cadeiras=2, xicaras=0),
          lambda im, d: C.mesa_cafe(d, m8[0], m8[1], s=m8[2], cadeiras=2, xicaras=0)),
    ]
    return cenas


def _cl(cor, k=0.55):
    return tuple(round(c + (255 - c) * k) for c in cor)


def _cruzam(a, b, folga=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + folga <= bx or bx + bw + folga <= ax or ay + ah + folga <= by or by + bh + folga <= ay)


def verificar(cenas):
    problemas = []
    for n, elems in cenas.items():
        for i, e in enumerate(elems):
            x, y, w, h = e["box"]
            if y < SEGURO_TOPO - 2 or y + h > SEGURO_BASE + 2:
                problemas.append(f"cena {n}: '{e['nome']}' fora do seguro vertical (y={y:.0f}..{y + h:.0f})")
            if x < X_MIN - 2 or x + w > X_MAX + 2:
                problemas.append(f"cena {n}: '{e['nome']}' fora do seguro horizontal (x={x:.0f}..{x + w:.0f})")
            for j, o in enumerate(elems):
                if j <= i:
                    continue
                if e["tipo"] in ("boneco", "texto") or o["tipo"] in ("boneco", "texto"):
                    if _cruzam(e["box"], o["box"], folga=6):
                        problemas.append(f"cena {n}: '{e['nome']}' cruza '{o['nome']}'")
    return problemas


def gerar_cenas_exemplo(cenas, caixas=False):
    chaves = list(cenas)
    cols = 5
    lin = math.ceil(len(chaves) / cols)
    esc = 0.3
    cw, ch = int(W * esc), int(H * esc)
    folha = Image.new("RGB", (cols * (cw + 16) + 16, lin * (ch + 44) + 16), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    ft = fonte(28, True)
    for pos, k in enumerate(chaves):
        im = papel()
        d = ImageDraw.Draw(im)
        for e in cenas[k]:
            r = e["draw"](im, d)
            if isinstance(r, Image.Image):
                im, d = r, ImageDraw.Draw(r)
        if caixas:
            for e in cenas[k]:
                x, y, w, h = e["box"]
                cor = {"boneco": (220, 0, 0), "texto": (0, 120, 220)}.get(e["tipo"], (0, 160, 0))
                d.rectangle([x, y, x + w, y + h], outline=cor, width=3)
            d.line([(0, SEGURO_TOPO), (W, SEGURO_TOPO)], fill=(220, 0, 220), width=3)
            d.line([(0, SEGURO_BASE), (W, SEGURO_BASE)], fill=(220, 0, 220), width=3)
        c, r = pos % cols, pos // cols
        x0, y0 = 16 + c * (cw + 16), 16 + r * (ch + 44)
        dd.text((x0, y0), f"cena {k}", font=ft, fill=INK)
        folha.paste(im.resize((cw, ch), Image.LANCZOS), (x0, y0 + 38))
    nome = "cenas_exemplo_caixas.jpg" if caixas else "cenas_exemplo.jpg"
    folha.save(os.path.join(PASTA, nome), quality=90)
    print("  " + nome)


if __name__ == "__main__":
    so_layout = "--so-layout" in sys.argv
    print("Gerando assets...")
    if not so_layout:
        pngs = gerar_isolados(transparentes="--sem-transparentes" not in sys.argv)
        gerar_contato(pngs)
    cenas = layout_cenas()
    gerar_cenas_exemplo(cenas)
    gerar_cenas_exemplo(cenas, caixas=True)
    probs = verificar(cenas)
    print("\nVerificacao de sobreposicao e area segura:")
    if probs:
        for p in probs:
            print("  [X]", p)
    else:
        print("  [OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.")
