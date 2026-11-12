"""Gera os assets do video adultos-morando-com-os-pais (Raphinha):
 - componentes/<nome>.png                 (fundo de papel, 1 por componente)
 - componentes/transparentes/<nome>.png   (RGBA, fundo transparente)
 - componentes/contato.jpg                (todos juntos, rotulados; recorte pela caixa *_box)
 - componentes/cenas_exemplo.jpg          (cada cena composta nas posicoes do componentes.md)
E roda a verificacao automatica de sobreposicao (caixas de boneco/texto x outros + area segura).
Nao renderiza video nem gera narracao. Rodar da raiz:  .venv/Scripts/python output/adultos-morando-com-os-pais/gerar_componentes.py
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
from media import sketch_componentes as SC  # noqa: E402  (catalogo aprovado: boneco_pensando)

_spec = importlib.util.spec_from_file_location("componentes_video_adultos", os.path.join(AQUI, "componentes_video.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

PASTA = os.path.join(AQUI, "componentes")
PASTA_T = os.path.join(PASTA, "transparentes")
os.makedirs(PASTA_T, exist_ok=True)

BRASIL = [{"rotulo": "2002", "valor": 20, "texto": "20%", "cor": (160, 195, 235)},
          {"rotulo": "2012", "valor": 24, "texto": "24%", "cor": AZUL}]
MARCAS_SEM_LUGAR = [(v, n, None, c) for v, n, _, c in C.MARCAS_UE]


def _balao_box(cx, cy, larg, alt):
    return (cx - larg / 2 - 4, cy - alt / 2 - 4, larg + 8, alt + 58)


# ---------------------------------------------------------------------------
# 1) Componentes isolados: (nome, novo?, desenho(im, d) -> im, caixa)
# ---------------------------------------------------------------------------
def _w(fn):
    """Embrulha funcoes que nao devolvem im."""
    def f(im, d):
        r = fn(im, d)
        return r if r is not None else im
    return f


COMPONENTES = [
    ("casa_familia", True, _w(lambda im, d: C.casa_familia(d, 560, 1000, s=1.6)), C.casa_familia_box(560, 1000, 1.6)),
    ("etiqueta_preguica", True, _w(lambda im, d: C.etiqueta_riscada(d, 540, 900, "preguiça?")),
     C.etiqueta_riscada_box(540, 900, "preguiça?")),
    ("etiqueta_rotulo", True, _w(lambda im, d: C.etiqueta_riscada(d, 540, 900, "rótulo")),
     C.etiqueta_riscada_box(540, 900, "rótulo")),
    ("grafico_lacuna_brasil", True, _w(lambda im, d: C.grafico_lacuna(d, 540, 1200, BRASIL)),
     C.grafico_lacuna_box(540, 1200, BRASIL)),
    ("barra_unica_eua", True,
     _w(lambda im, d: C.barra_unica(d, 540, 1200, "32,1%", "EUA, 2014", "18 a 34 anos", alt=500)),
     C.barra_unica_box(540, 1200, "32,1%", "EUA, 2014", "18 a 34 anos", alt=500)),
    ("icone_livro", True, _w(lambda im, d: C.icone_livro(d, 540, 900, s=1.4)), C.icone_livro_box(540, 900, 1.4)),
    ("custo_moradia", True, _w(lambda im, d: C.custo_moradia(d, 540, 900, s=1.4)), C.custo_moradia_box(540, 900, 1.4)),
    ("icone_alianca", True, _w(lambda im, d: C.icone_alianca(d, 540, 900, s=1.4)), C.icone_alianca_box(540, 900, 1.4)),
    ("alianca_relogio", True, _w(lambda im, d: C.alianca_relogio(d, 540, 900, s=1.2, t=1.0)),
     C.alianca_relogio_box(540, 900, 1.2)),
    ("regua_idades", True, _w(lambda im, d: C.regua_idades(d, 540, 1000, s=1.1, abaixo=True)),
     C.regua_idades_box(540, 1000, 1.1, abaixo=True)),
    ("boneco_andando", True, _w(lambda im, d: C.boneco_andando(d, 540, 900, s=1.3, fase=1.2)),
     C.boneco_andando_box(540, 900, 1.3)),
    ("lampada_acesa", True, lambda im, d: C.lampada(im, d, 540, 900, s=1.4, t=0.5), C.lampada_box(540, 900, 1.4)),
    ("duas_portas", True, _w(lambda im, d: C.duas_portas(d, 540, 900)), C.duas_portas_box(540, 900)),
    ("boneco_pensando", False, _w(lambda im, d: SC.boneco_pensando(d, 540, 1000, s=1.4, t=0.3)),
     SC.boneco_pensando_box(540, 1000, 1.4)),
    ("balao_interrogacao", False, _w(lambda im, d: balao(d, 540, 900, 220, 160, ["?"], seed=50, tam=96)),
     _balao_box(540, 900, 220, 160)),
]


def _transparente(fn):
    plano = Image.new("RGB", (W, H), PAPEL)
    plano = fn(plano, ImageDraw.Draw(plano))
    a = np.asarray(plano).astype(np.int16)
    dif = np.abs(a - np.array(PAPEL, dtype=np.int16)).max(axis=2)
    alfa = np.clip((dif - 4) * 32, 0, 255).astype(np.uint8)
    rgba = np.dstack([np.asarray(plano), alfa])
    return Image.fromarray(rgba, "RGBA")


def gerar_isolados():
    imgs = {}
    for nome, _novo, fn, _box in COMPONENTES:
        im = papel()
        im = fn(im, ImageDraw.Draw(im))
        im.save(os.path.join(PASTA, nome + ".png"))
        _transparente(fn).save(os.path.join(PASTA_T, nome + ".png"))
        imgs[nome] = im
    print(f"  {len(imgs)} componentes (papel + transparente)")
    return imgs


def gerar_contato(imgs):
    cols, cw, ch, topo = 4, 360, 330, 46
    linhas = math.ceil(len(COMPONENTES) / cols)
    folha = Image.new("RGB", (cols * cw + 20, linhas * (ch + topo) + 20), PAPEL)
    dd = ImageDraw.Draw(folha)
    for i, (nome, novo, _fn, box) in enumerate(COMPONENTES):
        c, r = i % cols, i // cols
        x0, y0 = 10 + c * cw, 10 + r * (ch + topo)
        x, y, w, h = box
        pad = 30
        rec = imgs[nome].crop((int(max(0, x - pad)), int(max(0, y - pad)), int(min(W, x + w + pad)), int(min(H, y + h + pad))))
        k = min((cw - 16) / rec.width, (ch - 10) / rec.height)
        rec = rec.resize((max(1, int(rec.width * k)), max(1, int(rec.height * k))), Image.LANCZOS)
        folha.paste(rec, (x0 + (cw - rec.width) // 2, y0 + topo + (ch - 10 - rec.height) // 2))
        dd.rectangle([x0 + 2, y0 + topo - 2, x0 + cw - 6, y0 + topo + ch - 8], outline=(200, 200, 205), width=2)
        dd.text((x0 + 6, y0 + 6), f"{i + 1}. {nome}", font=fonte(24, True), fill=INK)
        dd.text((x0 + cw - 10, y0 + 8), "NOVO" if novo else "reuso", font=fonte(22, True),
                fill=LARANJA if novo else (60, 150, 90), anchor="ra")
    folha.save(os.path.join(PASTA, "contato.jpg"), quality=90)
    print("  contato.jpg")


# ---------------------------------------------------------------------------
# 2) Posicoes por cena (FONTE UNICA; o componentes.md reflete isto)
# ---------------------------------------------------------------------------
def T(nome, x, y, s, tam, cor=INK):
    return {"nome": nome, "tipo": "texto", "box": C.caixa_texto(x, y, s, tam),
            "draw": lambda im, d: texto(d, x, y, s, tam, cor)}


def layout_cenas():
    cenas = {}

    # CENA 1: gancho - "preguica?" riscada + casa com pai e filho adulto + balao "?"
    cenas[1] = [
        {"nome": "etiqueta 'preguiça?'", "tipo": "texto", "box": C.etiqueta_riscada_box(540, 420, "preguiça?", 1.0, 100),
         "draw": lambda im, d: C.etiqueta_riscada(d, 540, 420, "preguiça?", tam=100)},
        {"nome": "balao '?'", "tipo": "texto", "box": _balao_box(870, 790, 230, 170),
         "draw": lambda im, d: balao(d, 870, 790, 230, 170, ["?"], seed=50, tam=110)},
        {"nome": "casa_familia", "tipo": "boneco", "box": C.casa_familia_box(560, 1250, 1.85),
         "draw": lambda im, d: C.casa_familia(d, 560, 1250, s=1.85)},
    ]

    # CENA 2: Brasil 2002 -> 2012 + lacuna "hoje"
    G2 = dict(alt_max=700, larg=210, passo=300)
    cenas[2] = [
        T("titulo", 540, 300, "Brasil, 25 a 34 anos", 68),
        {"nome": "grafico_lacuna", "tipo": "texto", "box": C.grafico_lacuna_box(540, 1330, BRASIL, **G2),
         "draw": lambda im, d: C.grafico_lacuna(d, 540, 1330, BRASIL, **G2)},
    ]

    # CENA 3: explicacoes da epoca -> casa
    setas3 = [((265, 1010), (440, 815)), ((545, 1000), (545, 830)), ((825, 1010), (650, 815))]

    def _setas3(im, d):
        for k, ((a, b), (c, e)) in enumerate(setas3):
            seta(d, a, b, c, e, seed=300 + 10 * k, cor=FERRO, w=6)
    cenas[3] = [
        T("titulo", 540, 300, "explicações em 2012", 70),
        {"nome": "casa", "tipo": "obj", "box": (540 - 190, 640 - 198, 380, 352),
         "draw": lambda im, d: casa(d, 540, 640, s=1.5, seed=200)},
        {"nome": "setas", "tipo": "obj", "box": (240, 780, 610, 235), "draw": _setas3},
        {"nome": "icone_livro", "tipo": "obj", "box": C.icone_livro_box(235, 1140, 1.15),
         "draw": lambda im, d: C.icone_livro(d, 235, 1140, s=1.15, seed=210)},
        {"nome": "custo_moradia", "tipo": "obj", "box": C.custo_moradia_box(550, 1140, 1.2),
         "draw": lambda im, d: C.custo_moradia(d, 550, 1140, s=1.2, seed=220)},
        {"nome": "icone_alianca", "tipo": "obj", "box": C.icone_alianca_box(850, 1140, 1.2),
         "draw": lambda im, d: C.icone_alianca(d, 850, 1140, s=1.2, seed=230)},
        T("rot estudo", 235, 1330, "estudo", 60, AZUL),
        T("rot custo", 550, 1330, "custo", 60, LARANJA),
        T("rot casamento", 850, 1330, "casamento", 60, (200, 140, 20)),
    ]

    # CENA 4: regua de idades (UE) com rotulos embaixo + boneco andando EM CIMA da linha, de 21,4 a 30,1
    R4 = dict(s=1.1, abaixo=True, tam_num=62, tam_lugar=48)
    yr = 1180
    sb = 1.8
    yb = yr - 6 - 125 * sb          # pes do boneco pisando a linha
    xa = C.regua_x(540, 21.4, 1.1)
    xb = C.regua_x(540, 30.1, 1.1)
    cenas[4] = [
        T("titulo", 540, 300, "idade ao sair de casa", 70),
        {"nome": "boneco_andando (trajeto)", "tipo": "boneco", "box": C.boneco_andando_box(xa, yb, sb, x_fim=xb),
         "draw": lambda im, d: C.boneco_andando(d, C.regua_x(540, 26.2, 1.1) + 60, yb, s=sb, fase=1.0)},
        {"nome": "regua (linha)", "tipo": "piso", "box": C.regua_idades_linha_box(540, yr, 1.1),
         "draw": lambda im, d: None},
        {"nome": "regua (rotulos)", "tipo": "texto", "box": C.regua_idades_rotulos_box(540, yr, **R4),
         "draw": lambda im, d: C.regua_idades(d, 540, yr, **R4)},
    ]

    # CENA 5: rotulo riscado -> lampada (contexto) sobre a regua
    def _lamp5(im, d):
        return C.lampada(im, d, 540, 790, s=1.7, t=0.4)
    cenas[5] = [
        {"nome": "etiqueta 'rótulo'", "tipo": "texto", "box": C.etiqueta_riscada_box(540, 370, "rótulo", 1.0, 92),
         "draw": lambda im, d: C.etiqueta_riscada(d, 540, 370, "rótulo", tam=92)},
        {"nome": "lampada", "tipo": "obj", "box": C.lampada_box(540, 790, 1.7), "draw": _lamp5},
        T("rot contexto", 540, 1120, "o contexto explica", 74, (200, 140, 20)),
        {"nome": "regua mini", "tipo": "texto",
         "box": C.regua_idades_box(540, 1370, 0.9, marcas=MARCAS_SEM_LUGAR, tam_num=62),
         "draw": lambda im, d: C.regua_idades(d, 540, 1370, s=0.9, marcas=MARCAS_SEM_LUGAR, tam_num=62)},
    ]

    # CENA 6: virada - EUA 2014 32,1% + alianca com relogio (casamento adiado)
    B6 = dict(alt=700, larg=230)
    cenas[6] = [
        T("titulo", 540, 300, "não é só dinheiro", 76),
        {"nome": "barra_unica EUA", "tipo": "texto",
         "box": C.barra_unica_box(300, 1320, "32,1%", "EUA, 2014", "18 a 34 anos", **B6),
         "draw": lambda im, d: C.barra_unica(d, 300, 1320, "32,1%", "EUA, 2014", "18 a 34 anos", seed=400, **B6)},
        {"nome": "alianca_relogio", "tipo": "obj", "box": C.alianca_relogio_box(775, 860, 1.25),
         "draw": lambda im, d: C.alianca_relogio(d, 775, 860, s=1.25, seed=410, t=1.0)},
        T("rot casamento adiado", 775, 1110, "casamento adiado", 56),
    ]

    # CENA 7: pergunta de volta - duas portas + boneco pensando
    cenas[7] = [
        T("titulo", 540, 280, "escolha ou conta?", 80),
        {"nome": "duas_portas", "tipo": "texto", "box": C.duas_portas_box(540, 720, 1.2),
         "draw": lambda im, d: C.duas_portas(d, 540, 720, s=1.2, seed=500)},
        {"nome": "boneco_pensando", "tipo": "boneco", "box": SC.boneco_pensando_box(540, 1330, 1.3),
         "draw": lambda im, d: SC.boneco_pensando(d, 540, 1330, s=1.3, t=0.3)},
    ]
    return cenas


def _cruzam(a, b, folga=0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + folga <= bx or bx + bw + folga <= ax or ay + ah + folga <= by or by + bh + folga <= ay)


def verificar(cenas):
    problemas = []
    for n, elems in cenas.items():
        for i, e in enumerate(elems):
            x, y, w, h = e["box"]
            if y < SEGURO_TOPO - 2 or y + h > SEGURO_BASE + 2 or x < 0 or x + w > W:
                problemas.append(f"cena {n}: '{e['nome']}' fora do seguro (x={x:.0f}..{x+w:.0f}, y={y:.0f}..{y+h:.0f})")
            for j, o in enumerate(elems):
                # "piso" = linha de chao que o boneco pisa (regua da cena 4); nao e texto nem boneco: fica de fora
                if "piso" in (e["tipo"], o["tipo"]):
                    continue
                if i < j and (e["tipo"] in ("boneco", "texto") or o["tipo"] in ("boneco", "texto")):
                    if _cruzam(e["box"], o["box"], folga=8):
                        problemas.append(f"cena {n}: '{e['nome']}' cruza '{o['nome']}'")
    return problemas


def gerar_cenas_exemplo(cenas, caixas=False):
    cols, esc = 4, 0.33
    cw, ch = int(W * esc), int(H * esc)
    linhas = math.ceil(len(cenas) / cols)
    folha = Image.new("RGB", (cols * (cw + 16) + 16, linhas * (ch + 44) + 16), (255, 255, 255))
    dd = ImageDraw.Draw(folha)
    for pos, idx in enumerate(sorted(cenas)):
        im = papel()
        d = ImageDraw.Draw(im)
        for e in cenas[idx]:
            r = e["draw"](im, d)
            if r is not None:
                im = r
                d = ImageDraw.Draw(im)
        if caixas:
            for e in cenas[idx]:
                x, y, w, h = e["box"]
                d.rectangle([x, y, x + w, y + h], outline=(255, 0, 255) if e["tipo"] in ("texto", "boneco") else (0, 170, 0), width=3)
            d.line([(0, SEGURO_TOPO), (W, SEGURO_TOPO)], fill=(255, 0, 0), width=3)
            d.line([(0, SEGURO_BASE), (W, SEGURO_BASE)], fill=(255, 0, 0), width=3)
        c, r = pos % cols, pos // cols
        x0, y0 = 16 + c * (cw + 16), 16 + r * (ch + 44)
        dd.text((x0, y0), f"cena {idx}", font=fonte(28, True), fill=INK)
        folha.paste(im.resize((cw, ch), Image.LANCZOS), (x0, y0 + 36))
    nome = "cenas_exemplo_caixas.jpg" if caixas else "cenas_exemplo.jpg"
    folha.save(os.path.join(PASTA, nome), quality=90)
    print("  " + nome)


if __name__ == "__main__":
    print("Gerando assets (adultos-morando-com-os-pais)...")
    imgs = gerar_isolados()
    gerar_contato(imgs)
    cenas = layout_cenas()
    gerar_cenas_exemplo(cenas)
    gerar_cenas_exemplo(cenas, caixas=True)
    probs = verificar(cenas)
    print("\nVerificacao de sobreposicao:")
    if probs:
        for p in probs:
            print("  [X]", p)
    else:
        print("  [OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.")
