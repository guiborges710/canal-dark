"""Gera os assets de componentes do video divisao-politica-jovens-homens-mulheres:
 - componentes/<nome>.png                 (fundo de papel, 1 por componente, 1080x1920)
 - componentes/transparentes/<nome>.png   (RGBA, fundo transparente)
 - componentes/contato.jpg                (todos juntos, recortados e rotulados)
 - componentes/cenas_exemplo.jpg          (cada cena composta nas posicoes do componentes.md)
E roda o checador de sobreposicao (caixa de boneco/texto x qualquer outro elemento, area segura).
Nao renderiza video nem gera narracao.
Rodar da raiz:  .venv/Scripts/python.exe output/divisao-politica-jovens-homens-mulheres/componentes_gerar.py
"""
import importlib.util
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)

from media.sketch_lib import *  # noqa: E402,F401
from media.sketch_lib import fonte  # noqa: E402
import media.sketch_componentes as SC  # noqa: E402

_spec = importlib.util.spec_from_file_location("componentes_video_divisao", os.path.join(AQUI, "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

PASTA = os.path.join(AQUI, "componentes")
PASTA_T = os.path.join(PASTA, "transparentes")
os.makedirs(PASTA_T, exist_ok=True)


# ---------------------------------------------------------------------------
# 1) Componentes isolados: (nome, desenhar(d), caixa)
# ---------------------------------------------------------------------------
COMPONENTES = [
    ("boneco_ela", lambda d: C.boneco_ela(d, 540, 900, s=1.8, olha=+1), C.boneco_ela_box(540, 900, 1.8)),
    ("boneco_ele", lambda d: C.boneco_ele(d, 540, 900, s=1.8, olha=-1), C.boneco_ele_box(540, 900, 1.8)),
    ("dupla_distante", lambda d: C.dupla_distante(d, 540, 900, s=1.3, dist=380), C.dupla_distante_box(540, 900, 1.3, 380)),
    ("etiqueta_rotulo", lambda d: C.etiqueta_rotulo(d, 540, 900, "liberal", s=1.4), C.etiqueta_rotulo_box(540, 900, "liberal", 1.4)),
    ("barras_grupos", lambda d: C.barras_grupos(d, 540, 1080, s=1.0), C.barras_grupos_box(540, 1080, 1.0)),
    ("vao_3_pontos", lambda d: C.vao_pontos(d, 540, 1100, 28, 25, s=1.0, rotulo="3 pontos", periodo="2001-07"),
     C.vao_pontos_box(540, 1100, 28, 25, 1.0, rotulo="3 pontos")),
    ("vao_15_pontos", lambda d: C.vao_pontos(d, 540, 1100, 40, 25, s=1.0, rotulo="15 pontos", periodo="2017-24"),
     C.vao_pontos_box(540, 1100, 40, 25, 1.0, rotulo="15 pontos")),
    ("linhas_trajetoria", lambda d: C.linhas_trajetoria(d, 560, 900, s=1.0), C.linhas_trajetoria_box(560, 900, 1.0)),
    ("cartao_base_7", lambda d: C.cartao_base(d, 540, 900, s=1.0, numero="7", ano="2022", legenda="perto de 7 pontos, 2022", seed=3),
     C.cartao_base_box(540, 900, 1.0, "perto de 7 pontos, 2022")),
    ("cartao_base_plano", lambda d: C.cartao_base(d, 540, 900, s=1.0, legenda="sem evidência de alta", seed=8),
     C.cartao_base_box(540, 900, 1.0, "sem evidência de alta")),
    ("regua", lambda d: C.regua(d, 540, 900, comp=700, s=1.0, ang=-0.06), C.regua_box(540, 900, 700, 1.0, -0.06)),
    ("manchete_cresce", lambda d: C.manchete(d, 540, 900, s=1.2, titulo=("diferença", "cresce")), C.manchete_box(540, 900, 1.2)),
    ("manchete_estavel", lambda d: C.manchete(d, 540, 900, s=1.2, titulo=("diferença", "estável")), C.manchete_box(540, 900, 1.2)),
    ("geracao_dois_ritmos", lambda d: C.geracao_dois_ritmos(d, 540, 900, s=1.1), C.geracao_dois_ritmos_box(540, 900, 1.1)),
    ("regua_pergunta", lambda d: C.regua_pergunta(d, 540, 900, s=1.0), C.regua_pergunta_box(540, 900, 1.0)),
]


def _transparente(fn):
    base = Image.new("RGB", (W, H), PAPEL)
    fn(ImageDraw.Draw(base))
    a = np.array(base).astype(int)
    papel_px = (np.abs(a - np.array(PAPEL)).max(axis=2) <= 6)
    alfa = np.where(papel_px, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([np.array(base), alfa]), "RGBA")


def gerar_isolados():
    ims = {}
    for nome, fn, _ in COMPONENTES:
        im = papel()
        fn(ImageDraw.Draw(im))
        im.save(os.path.join(PASTA, nome + ".png"))
        _transparente(fn).save(os.path.join(PASTA_T, nome + ".png"))
        ims[nome] = im
    print(f"  {len(ims)} componentes (papel + transparente)")
    return ims


def checar_isolados():
    """Confere se o desenho cabe na caixa declarada (nada vaza para fora do *_box)."""
    probs = []
    for nome, fn, (bx, by, bw, bh) in COMPONENTES:
        im = Image.new("RGB", (W, H), PAPEL)
        fn(ImageDraw.Draw(im))
        a = np.array(im).astype(int)
        tinta = np.abs(a - np.array(PAPEL)).max(axis=2) > 10
        ys, xs = np.nonzero(tinta)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        folga = 6
        if x0 < bx - folga or y0 < by - folga or x1 > bx + bw + folga or y1 > by + bh + folga:
            probs.append(f"{nome}: desenho ({x0},{y0})-({x1},{y1}) sai da caixa ({bx:.0f},{by:.0f})-({bx+bw:.0f},{by+bh:.0f})")
    return probs


def gerar_contato(ims):
    cols, cell, rot = 4, 330, 40
    linhas = math.ceil(len(COMPONENTES) / cols)
    folha = Image.new("RGB", (cols * cell + 50, linhas * (cell + rot) + 40), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    ft = fonte(26)
    for i, (nome, _, (bx, by, bw, bh)) in enumerate(COMPONENTES):
        c, r = i % cols, i // cols
        x0, y0 = 20 + c * (cell + 3), 20 + r * (cell + rot)
        m = 30
        crop = ims[nome].crop((int(max(0, bx - m)), int(max(0, by - m)), int(min(W, bx + bw + m)), int(min(H, by + bh + m))))
        k = min((cell - 10) / crop.width, (cell - 10) / crop.height)
        crop = crop.resize((max(1, int(crop.width * k)), max(1, int(crop.height * k))), Image.LANCZOS)
        fundo = Image.new("RGB", (cell - 6, cell - 6), PAPEL)
        fundo.paste(crop, ((fundo.width - crop.width) // 2, (fundo.height - crop.height) // 2))
        folha.paste(fundo, (x0, y0 + rot))
        dd.rectangle([x0, y0 + rot, x0 + cell - 7, y0 + rot + cell - 7], outline=(200, 200, 200), width=2)
        dd.text((x0 + 4, y0 + 4), f"{i + 1}. {nome}", font=ft, fill=INK)
    folha.save(os.path.join(PASTA, "contato.jpg"), quality=90)
    print("  contato.jpg")


# ---------------------------------------------------------------------------
# 2) Layout por cena (FONTE UNICA de posicoes; o componentes.md reflete isto)
# ---------------------------------------------------------------------------
def T(nome, x, y, txt, tam, cor=INK, ancora="mm"):
    return {"nome": nome, "tipo": "texto", "box": C.caixa_texto(x, y, txt, tam, ancora),
            "draw": lambda d: texto(d, x, y, txt, tam, cor, ancora)}


def O(nome, tipo, box, draw):
    return {"nome": nome, "tipo": tipo, "box": box, "draw": draw}


def layout_cenas():
    cenas = {}
    # CENA 1 - gancho: de costas, linha tracejada, lupa
    cenas["1"] = [
        T("titulo", 540, 290, "Mais distantes?", 84),
        T("subtitulo", 540, 385, "jovens dos EUA", 52),
        O("dupla_distante", "boneco", C.dupla_distante_box(540, 1010, 1.4, 400),
          lambda d: C.dupla_distante(d, 540, 1010, s=1.4, dist=400)),
        T("rotulo", 540, 1340, "depende da pesquisa", 56),
    ]
    # CENA 2 - a serie (barras em dois grupos)
    cenas["2"] = [
        O("etiqueta", "texto", C.etiqueta_rotulo_box(540, 280, "liberal", 1.2),
          lambda d: C.etiqueta_rotulo(d, 540, 280, "liberal", s=1.2)),
        T("subtitulo", 540, 392, "18 a 29 anos, EUA", 50),
        O("barras_grupos", "boneco", C.barras_grupos_box(540, 1080, 1.0),
          lambda d: C.barras_grupos(d, 540, 1080, s=1.0)),
        T("rodape", 540, 1400, "3 períodos, 2001 a 2024", 46),
    ]
    # CENA 3 - a diferenca: 3 -> 15 pontos
    cenas["3"] = [
        T("titulo", 540, 290, "a diferença", 76),
        O("vao_3", "texto", C.vao_pontos_box(310, 1180, 28, 25, 1.0, rotulo="3 pontos"),
          lambda d: C.vao_pontos(d, 310, 1180, 28, 25, s=1.0, rotulo="3 pontos", periodo="2001-07")),
        O("seta", "obj", (445, 840, 200, 200),
          lambda d: seta(d, 450, 1030, 635, 850, seed=5, cor=INK, w=8)),
        O("vao_15", "texto", C.vao_pontos_box(770, 1180, 40, 25, 1.0, rotulo="15 pontos"),
          lambda d: C.vao_pontos(d, 770, 1180, 40, 25, s=1.0, rotulo="15 pontos", periodo="2017-24")),
    ]
    # CENA 4 - quem se mexeu (no rotulo liberal)
    cenas["4"] = [
        T("titulo", 540, 285, "Quem se mexeu?", 76),
        O("etiqueta", "texto", C.etiqueta_rotulo_box(540, 410, "liberal", 1.0),
          lambda d: C.etiqueta_rotulo(d, 540, 410, "liberal", s=1.0)),
        O("linhas_trajetoria", "boneco", C.linhas_trajetoria_box(560, 860, 1.0),
          lambda d: C.linhas_trajetoria(d, 560, 860, s=1.0)),
        T("rot_elas", 300, 1330, "elas subiram", 50, C.ELAS),
        T("rot_eles", 780, 1330, "eles, parados", 50, C.ELES),
    ]
    # CENA 5 - outras bases: linha plana
    cenas["5"] = [
        T("titulo", 540, 285, "outras bases: linha plana", 60),
        O("cartao_7", "texto", C.cartao_base_box(540, 610, 1.15, "perto de 7 pontos, 2022"),
          lambda d: C.cartao_base(d, 540, 610, s=1.15, numero="7", ano="2022", legenda="perto de 7 pontos, 2022", seed=3)),
        O("cartao_plano", "texto", C.cartao_base_box(540, 1100, 1.15, "sem evidência de alta"),
          lambda d: C.cartao_base(d, 540, 1100, s=1.15, legenda="sem evidência de alta", seed=8)),
    ]
    # CENA 6 - fechamento em 4 batidas (uma ideia por vez; a anterior sai antes da proxima)
    cenas["6a"] = [
        T("titulo", 540, 290, "E o porquê?", 80),
        O("boneco_pensando", "boneco", SC.boneco_pensando_box(540, 930, 1.8),
          lambda d: SC.boneco_pensando(d, 540, 930, s=1.8, t=0.0)),
        T("rotulo", 540, 1270, "nenhuma delas prova", 60),
    ]
    cenas["6b"] = [
        T("tag", 540, 285, "nossa leitura", 64),
        O("manchete", "texto", C.manchete_box(540, 640, 1.2),
          lambda d: C.manchete(d, 540, 640, s=1.2, titulo=("diferença", "cresce"))),
        O("regua", "obj", C.regua_box(540, 1080, 680, 1.0, -0.06),
          lambda d: C.regua(d, 540, 1080, comp=680, s=1.0, ang=-0.06)),
        T("rotulo", 540, 1250, "depende da régua", 60),
    ]
    cenas["6c"] = [
        O("geracao_dois_ritmos", "boneco", C.geracao_dois_ritmos_box(540, 820, 1.1),
          lambda d: C.geracao_dois_ritmos(d, 540, 820, s=1.1)),
        T("rotulo", 540, 1250, "dois grupos, dois ritmos", 58),
    ]
    cenas["6d"] = [
        T("titulo", 540, 290, "Qual é a régua?", 80),
        O("regua_pergunta", "boneco", C.regua_pergunta_box(540, 890, 1.15),
          lambda d: C.regua_pergunta(d, 540, 890, s=1.15)),
    ]
    return cenas


def _cruzam(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def verificar(cenas):
    probs = []
    for n, elems in cenas.items():
        for i, e in enumerate(elems):
            x, y, w, h = e["box"]
            if y < SEGURO_TOPO - 2 or y + h > SEGURO_BASE + 2:
                probs.append(f"cena {n}: '{e['nome']}' fora do seguro (y={y:.0f}..{y + h:.0f})")
            if x < 30 or x + w > W - 30:
                probs.append(f"cena {n}: '{e['nome']}' encosta na borda (x={x:.0f}..{x + w:.0f})")
            for o in elems[i + 1:]:
                if (e["tipo"] in ("boneco", "texto") or o["tipo"] in ("boneco", "texto")) and _cruzam(e["box"], o["box"]):
                    probs.append(f"cena {n}: '{e['nome']}' cruza '{o['nome']}'")
    return probs


def gerar_cenas_exemplo(cenas, caixas=False):
    cols, esc = 5, 0.3
    cw, ch = int(W * esc), int(H * esc)
    linhas = math.ceil(len(cenas) / cols)
    folha = Image.new("RGB", (cols * (cw + 16) + 16, linhas * (ch + 44) + 16), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    ft = fonte(28)
    for pos, n in enumerate(cenas):
        im = papel()
        d = ImageDraw.Draw(im)
        for e in cenas[n]:
            e["draw"](d)
        if caixas:
            for e in cenas[n]:
                x, y, w, h = e["box"]
                cor = {"boneco": (200, 0, 160), "texto": (0, 140, 200)}.get(e["tipo"], (120, 120, 120))
                d.rectangle([x, y, x + w, y + h], outline=cor, width=3)
            d.line([(0, SEGURO_TOPO), (W, SEGURO_TOPO)], fill=(255, 0, 0), width=3)
            d.line([(0, SEGURO_BASE), (W, SEGURO_BASE)], fill=(255, 0, 0), width=3)
        c, r = pos % cols, pos // cols
        x0, y0 = 16 + c * (cw + 16), 16 + r * (ch + 44)
        dd.text((x0, y0), f"cena {n}", font=ft, fill=INK)
        folha.paste(im.resize((cw, ch), Image.LANCZOS), (x0, y0 + 36))
    nome = "cenas_exemplo_caixas.jpg" if caixas else "cenas_exemplo.jpg"
    folha.save(os.path.join(PASTA, nome), quality=90)
    print("  " + nome)


if __name__ == "__main__":
    print("Gerando componentes...")
    ims = gerar_isolados()
    gerar_contato(ims)
    cenas = layout_cenas()
    gerar_cenas_exemplo(cenas)
    gerar_cenas_exemplo(cenas, caixas="--caixas" in sys.argv)
    print("\nDesenho dentro da caixa *_box:")
    pi = checar_isolados()
    print("\n".join("  [X] " + p for p in pi) if pi else "  [OK] todos os desenhos cabem nas caixas declaradas.")
    print("\nVerificacao de sobreposicao:")
    pv = verificar(cenas)
    print("\n".join("  [X] " + p for p in pv) if pv else "  [OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.")
