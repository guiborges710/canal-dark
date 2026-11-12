"""Gera as imagens de validação e confere a sobreposição. Da raiz: .venv/Scripts/python output/<slug>/componentes_gerar.py

Saída em componentes/: um PNG por componente sobre papel kraft, transparentes/ (RGBA), figuras/, contato.jpg e cenas_exemplo.jpg.
As cenas de exemplo saem do compositor real (`compor_cena`), então mostram o que o render vai desenhar.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
sys.path[:0] = [str(RAIZ), str(PASTA)]

from media import colagem_lib as C  # noqa: E402
from media.camadas import SEGURO_BASE, SEGURO_TOPO, H, W, aplicar, compor, fonte, girar, mover  # noqa: E402
import componentes_video as V  # noqa: E402

SAIDA = PASTA / "componentes"
TRANSP = SAIDA / "transparentes"
KRAFT = C.SUPERFICIES["kraft"]


def sprite_tira(spec):
    return C.peca_de({"tipo": "tira", "texto": spec["texto"], "tam": spec.get("tam", 72), "cor": spec.get("cor", C.PRETO), "id": "tx"}).sprite


def imagens():
    """nome -> sprite de cada componente."""
    saida = {}
    for nome in V.RECORTES:
        saida[nome] = C.peca_de(V.rec(nome)).sprite
    for nome, spec in V.CARIMBOS.items():
        saida[nome] = C._carimbo(spec["texto"], C.VERMELHO, len(spec["texto"]))
    return saida


def folha_textos(specs, desenha, altura_linha):
    """Tiras e anotações saem numa folha só: são texto, e revisar item a item não ajuda."""
    im = Image.new("RGBA", (1060, altura_linha * len(specs) + 40), KRAFT)
    for i, s in enumerate(specs.values()):
        spr = desenha(s)
        pedaco = spr.im.resize((int(spr.im.width / spr.dens), int(spr.im.height / spr.dens)), Image.LANCZOS)
        im.alpha_composite(pedaco, ((im.width - pedaco.width) // 2, 20 + i * altura_linha + (altura_linha - pedaco.height) // 2))
    return im


def folha_anotacoes():
    """Os bilhetes como aparecem na cena: papel, linhas e seta, sobre kraft."""
    quadro = Image.new("RGBA", (W, H), KRAFT)
    pos = {"nota_depois": (400, 110, [800, 28]), "nota_menos_tempo": (400, 325, [800, 205]), "nota_nao_da": (400, 590, None), "nota_nao_e_se_usam": (400, 835, None)}
    cam = C._camera({}, 0, 5)  # lt=0: sem o travelling
    for nome, (x, y, seta) in pos.items():
        b = V.postit(nome, x, y, 0, seta_para=seta)
        peca = C.peca_de(b["papel"])
        m = compor(mover(x, y), girar(b["papel"]["rot"]))
        peca.sombra.colar(quadro, compor(mover(8, 12), m), filtro=Image.BILINEAR)
        peca.sprite.colar(quadro, m)
        for n in b["anotacoes"]:
            C._anotar(quadro, cam, n, 5)
    return quadro.crop((0, 0, 1060, 980))


def sobre_papel(spr, margem=40):
    p = spr.im.resize((int(spr.im.width / spr.dens), int(spr.im.height / spr.dens)), Image.LANCZOS)
    fundo = Image.new("RGBA", (p.width + margem * 2, p.height + margem * 2), KRAFT)
    fundo.alpha_composite(p, (margem, margem))
    return fundo


def contato(itens):
    col, cel_w, cel_h = 5, 380, 400
    linhas = math.ceil(len(itens) / col)
    folha = Image.new("RGB", (col * cel_w, linhas * cel_h), "#EFE9DA")
    d = ImageDraw.Draw(folha)
    fo = fonte("pesada", 21)
    for i, (nome, im) in enumerate(itens):
        x, y = (i % col) * cel_w, (i // col) * cel_h
        m = im.copy().convert("RGB")
        m.thumbnail((cel_w - 24, cel_h - 56), Image.LANCZOS)
        folha.paste(m, (x + (cel_w - m.width) // 2, y + 10 + (cel_h - 56 - m.height) // 2))
        d.text((x + cel_w / 2, y + cel_h - 22), nome, font=fo, fill="#141312", anchor="mm")
    folha.save(SAIDA / "contato.jpg", quality=90)


def cenas_exemplo():
    n, col = len(V.CENAS), 5
    esc = 0.36
    w_, h_ = int(W * esc), int(H * esc)
    folha = Image.new("RGB", (col * (w_ + 12) + 12, math.ceil(n / col) * (h_ + 44) + 12), "#EFE9DA")
    d = ImageDraw.Draw(folha)
    fo = fonte("pesada", 22)
    for i, c in enumerate(V.CENAS):
        im = C.compor_cena(c, c["duracao"], c["duracao"]).convert("RGB").resize((w_, h_), Image.LANCZOS)
        x, y = 12 + (i % col) * (w_ + 12), 12 + (i // col) * (h_ + 44)
        folha.paste(im, (x, y))
        d.text((x + w_ / 2, y + h_ + 16), c["rotulo_raphinha"], font=fo, fill="#141312", anchor="mm")
    folha.save(SAIDA / "cenas_exemplo.jpg", quality=90)


# ---------- checador: nenhuma peça cobre outra, então nada cobre figura nem texto ----------
def _poligono(x, y, rot, w_, h_):
    m = compor(mover(x, y), girar(rot))
    return [aplicar(m, sx * w_ / 2, sy * h_ / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _mascara(pts, largura=None):
    im = Image.new("1", (W // 2, H // 2 + 400), 0)
    d = ImageDraw.Draw(im)
    pp = [(a / 2, b / 2) for a, b in pts]
    if largura:
        d.line(pp, fill=1, width=largura)
    else:
        d.polygon(pp, fill=1)
    return np.asarray(im)


def elementos(c):
    saida = []
    for r in c["recortes"]:
        p = C.peca_de(r)
        saida.append((r["id"], _poligono(r["x"], r["y"], r.get("rot", 0), p.larg - 16, p.alt - 16), "recorte", r))
    for k in c.get("carimbos", ()):
        s = C._carimbo(k["texto"], C.VERMELHO, len(k["texto"]))
        saida.append((f"carimbo:{k['texto']}", _poligono(k["x"], k["y"], k.get("rot", -10), s.im.width / s.dens, s.im.height / s.dens), "carimbo", k))
    for n in c.get("anotacoes", ()):
        s = C._anotacao_sprite(n["texto"], n.get("cor", C.VERMELHO))
        saida.append((f"nota:{n['texto']}", _poligono(n["x"], n["y"], n.get("rot", -3), s.im.width / s.dens, s.im.height / s.dens), "anotacao", n))
    for t in c.get("textos", ()):
        s = sprite_tira(t)
        saida.append((f"tira:{t['texto']}", _poligono(t["x"], t["y"], t.get("rot", -1.5), s.im.width / s.dens - 28, s.im.height / s.dens - 28), "tira", t))
    return saida


def conferir():
    problemas = []
    for c in V.CENAS:
        C.validar(c, c["rotulo_raphinha"])
        els = elementos(c)
        mascaras = {e[0]: _mascara(e[1]) for e in els}
        nomes = list(mascaras)
        for i, a in enumerate(nomes):
            for b in nomes[i + 1:]:
                area = int((mascaras[a] & mascaras[b]).sum())
                if a.startswith("papel_") and b.split(":")[0] in ("carimbo", "nota") and V.apoio_de(b) == a:
                    continue  # o papel de apoio existe para ficar embaixo do próprio carimbo ou anotação
                if area > 0:
                    problemas.append(f"{c['rotulo_raphinha']}: {a} x {b} ({area * 4} px²)")
        for nome, pts, tipo, _ in els:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if min(xs) < 12 or max(xs) > W - 12:
                problemas.append(f"{c['rotulo_raphinha']}: {nome} sai da largura ({min(xs):.0f}..{max(xs):.0f})")
            if tipo != "recorte" or C.peca_de(next(r for r in c["recortes"] if r["id"] == nome)).linhas:
                if min(ys) < SEGURO_TOPO - 20 or max(ys) > SEGURO_BASE + 20:
                    problemas.append(f"{c['rotulo_raphinha']}: {nome} fora da área segura ({min(ys):.0f}..{max(ys):.0f})")
        # Setas e barbantes não podem cruzar peça que não é a deles.
        pos = {r["id"]: r for r in c["recortes"]}
        for x in c.get("conexoes", ()):
            a, b = pos[x["de"]], pos[x["para"]]
            pa = aplicar(compor(mover(a["x"], a["y"]), girar(a.get("rot", 0))), a.get("ax", 0), a.get("ay", 0))
            pb = aplicar(compor(mover(b["x"], b["y"]), girar(b.get("rot", 0))), b.get("ax", 0), b.get("ay", 0))
            lin = _mascara([pa, pb], 3)
            for nome in nomes:
                if nome not in (x["de"], x["para"]) and (lin & mascaras[nome]).any():
                    problemas.append(f"{c['rotulo_raphinha']}: barbante {x['de']}>{x['para']} cruza {nome}")
        for n in c.get("anotacoes", ()):
            if n.get("seta_para"):
                lin = _mascara([(n["x"], n["y"]), tuple(n["seta_para"])], 3)
                for nome in nomes:
                    if nome not in (f"nota:{n['texto']}", V.apoio_de(f"nota:{n['texto']}")) and (lin & mascaras[nome]).any():
                        problemas.append(f"{c['rotulo_raphinha']}: seta de '{n['texto']}' entra em {nome}")
    return problemas


def so_anotacoes():
    """Refaz só anotacoes_a_mao.png e as duas folhas de conferência; os PNGs dos demais componentes não são regravados."""
    C.definir_pasta(PASTA)
    itens = [(nome, sobre_papel(spr)) for nome, spr in imagens().items()]
    notas = folha_anotacoes()
    notas.convert("RGB").save(SAIDA / "anotacoes_a_mao.png")
    itens += [("tiras_de_texto", folha_textos(V.TIRAS, sprite_tira, 150)), ("anotacoes_a_mao", notas)]
    contato(itens)
    cenas_exemplo()
    problemas = conferir()
    print("\n".join(problemas) if problemas else "Sobreposição: nenhum problema")


def main():
    TRANSP.mkdir(parents=True, exist_ok=True)
    for velho in list(SAIDA.glob("*.png")) + list(TRANSP.glob("*.png")):  # componente que saiu da lista não pode sobrar para revisão
        velho.unlink()
    V.gerar_figuras()
    C.definir_pasta(PASTA)
    itens = []
    for nome, spr in imagens().items():
        spr.im.save(TRANSP / f"{nome}.png")
        im = sobre_papel(spr)
        im.convert("RGB").save(SAIDA / f"{nome}.png")
        itens.append((nome, im))
    tiras = folha_textos(V.TIRAS, sprite_tira, 150)
    notas = folha_anotacoes()
    tiras.convert("RGB").save(SAIDA / "tiras_de_texto.png")
    notas.convert("RGB").save(SAIDA / "anotacoes_a_mao.png")
    itens += [("tiras_de_texto", tiras), ("anotacoes_a_mao", notas)]
    contato(itens)
    cenas_exemplo()
    problemas = conferir()
    print(f"{len(itens)} imagens; {len(V.CENAS)} cenas de exemplo")
    print("\n".join(problemas) if problemas else "Sobreposição: nenhum problema")


if __name__ == "__main__":
    so_anotacoes() if "--so-anotacoes" in sys.argv else main()
