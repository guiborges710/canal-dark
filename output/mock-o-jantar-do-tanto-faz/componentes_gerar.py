"""Gera previews fiéis usando exclusivamente media.cartoon_lib."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

from media.cartoon_lib import compor_cena, validar
from media.camadas import fonte

OUT = Path(__file__).with_name("componentes")
OUT.mkdir(parents=True, exist_ok=True)
PALETA = "tijolo"
ROTULOS_CONTATO = {
    "elenco_bia": "ELENCO BIA",
    "elenco_teo": "ELENCO TEO",
    "cenario_sala": "CENÁRIO SALA",
    "cenario_escritorio": "CENÁRIO ESCRITÓRIO",
    "celular_pedir_jantar": "CELULAR",
    "caixa_pizza": "CAIXA PIZZA",
    "sinais_rejeicao": "SINAIS",
    "textos_chave": "TEXTOS-CHAVE",
}


def base(nome, cenario="liso", personagens=None, objetos=None, textos=None):
    return {
        "tipo": "cartoon_alive",
        "desenho": nome,
        "fala": "Preview de componentes.",
        "duracao": 3.0,
        "paleta": PALETA,
        "acao": "Preview fiel dos componentes escolhidos para o vídeo.",
        "cenario": cenario,
        "personagens": personagens or [],
        "objetos": objetos or [],
        "textos": textos or [],
        "transicao": {"entrada": "corte", "saida": "corte"},
    }


def ator(ident, x, pose, expressao, escala=0.9, olha="dir", segura=None, fala=False):
    spec = {
        "id": ident,
        "x": x,
        "y": 1440,
        "escala": escala,
        "olha": olha,
        "fala": fala,
        "poses": [{"t": 0, "pose": pose, "expressao": expressao}],
    }
    if segura:
        spec["segura"] = segura
    return spec


def txt(texto, x, y, tam=88, cor="destaque"):
    return {"texto": texto, "x": x, "y": y, "tam": tam, "t": 0, "entrada": "corte", "cor": cor}


COMPONENTES = {
    "elenco_bia": base(
        "preview_bia",
        personagens=[
            ator("bia", 190, "aponta", "brava", .72),
            ator("bia", 540, "segura", "pensativa", .72),
            ator("bia", 890, "medo", "medo", .72),
        ],
        textos=[txt("BRAVA", 190, 300, 60), txt("DECIDINDO", 540, 300, 60), txt("PESO", 890, 300, 60)],
    ),
    "elenco_teo": base(
        "preview_teo",
        personagens=[
            ator("teo", 190, "ombros", "surpresa", .70),
            ator("teo", 540, "pensando", "pensativa", .70),
            ator("teo", 890, "medo", "medo", .70),
        ],
        textos=[txt("TANTO FAZ", 190, 300, 56), txt("REJEITA", 540, 300, 60), txt("OFENDIDO", 890, 300, 56)],
    ),
    "cenario_sala": base("preview_sala", cenario="sala", textos=[txt("SALA", 540, 300, 110)]),
    "cenario_escritorio": base("preview_escritorio", cenario="escritorio", textos=[txt("ENTREVISTA", 540, 300, 96)]),
    "celular_pedir_jantar": base(
        "preview_celular",
        objetos=[{"tipo": "celular", "x": 540, "y": 950, "escala": 1.8, "t": 0, "entrada": "corte", "texto": "PEDIR JANTAR"}],
        textos=[txt("CELULAR", 540, 300, 94)],
    ),
    "caixa_pizza": base(
        "preview_caixa",
        objetos=[{"tipo": "caixa", "x": 540, "y": 980, "escala": 2.0, "t": 0, "entrada": "corte", "rot": -12}],
        textos=[txt("PIZZA", 540, 430, 120)],
    ),
    "sinais_rejeicao": base(
        "preview_sinais",
        objetos=[
            {"tipo": "raio", "x": 250, "y": 930, "escala": 1.0, "t": 0, "entrada": "corte"},
            {"tipo": "exclamacao", "x": 540, "y": 930, "escala": 1.0, "t": 0, "entrada": "corte"},
            {"tipo": "interrogacao", "x": 830, "y": 930, "escala": .85, "t": 0, "entrada": "corte"},
        ],
        textos=[txt("REJEIÇÕES", 540, 300, 96)],
    ),
    "textos_chave": base(
        "preview_textos",
        textos=[
            txt("TANTO FAZ", 540, 520, 112),
            txt("REPROVADO", 540, 850, 112, "claro"),
            txt("PIZZA", 540, 1180, 122, "apoio"),
        ],
    ),
}


CENAS = [
    base(
        "cena_1",
        "sala",
        [ator("bia", 330, "aponta", "brava", 1.05, "dir", fala=True), ator("teo", 800, "neutra", "surpresa", 1.02, "esq")],
        [{"tipo": "exclamacao", "x": 760, "y": 670, "escala": .65, "t": 0, "entrada": "corte"}],
        [txt("TANTO FAZ", 540, 300, 108)],
    ),
    base(
        "cena_2",
        "sala",
        [
            ator("bia", 320, "segura", "pensativa", 1.0, "dir", {"tipo": "celular", "texto": "PEDIR JANTAR", "escala": .9}, fala=True),
            ator("teo", 800, "ombros", "brava", 1.0, "esq"),
        ],
        [{"tipo": "raio", "x": 540, "y": 670, "escala": .55, "t": 0, "entrada": "corte"}],
        [txt("PIZZA?", 540, 300, 118)],
    ),
    base(
        "cena_3",
        "liso",
        [ator("bia", 280, "aponta", "brava", .95, "dir", fala=True), ator("teo", 810, "medo", "medo", 1.02, "esq")],
        [{"tipo": "raio", "x": 540, "y": 760, "escala": .48, "t": 0, "entrada": "corte"}],
        [txt("JAPONÊS?", 540, 280, 86), txt("HAMBÚRGUER?", 540, 500, 80, "claro")],
    ),
    base(
        "cena_4",
        "sala",
        [ator("bia", 320, "maos_cintura", "brava", 1.02, "dir", fala=True), ator("teo", 800, "ombros", "surpresa", 1.02, "esq")],
        [{"tipo": "coracao", "x": 540, "y": 620, "escala": .48, "t": 0, "entrada": "corte"}],
        [txt("TANTO FAZ", 540, 300, 112)],
    ),
    base(
        "cena_5",
        "escritorio",
        [ator("bia", 280, "maos_cintura", "brava", .92, "dir", fala=True), ator("teo", 810, "pensando", "medo", .94, "esq")],
        [{"tipo": "interrogacao", "x": 820, "y": 680, "escala": .48, "t": 0, "entrada": "corte"}],
        [txt("REPROVADO", 540, 300, 106)],
    ),
    base(
        "cena_6",
        "sala",
        [ator("bia", 220, "medo", "medo", .98, "dir", fala=True), ator("teo", 860, "aponta", "brava", .98, "esq")],
        [
            {"tipo": "caixa", "x": 540, "y": 1290, "escala": 1.1, "t": 0, "entrada": "corte", "rot": -12},
            {"tipo": "exclamacao", "x": 540, "y": 650, "escala": .50, "t": 0, "entrada": "corte"},
        ],
        [txt("PIZZA", 540, 300, 118)],
    ),
]


def render(spec, nome, tempo=2.2):
    validar(spec, nome)
    im = compor_cena(spec, tempo, spec["duracao"], abertura=True, paleta=PALETA).convert("RGB")
    im.save(OUT / f"{nome}.png", quality=95)
    return im


def grade(itens, destino, colunas, thumb=(360, 640)):
    linhas = (len(itens) + colunas - 1) // colunas
    faixa = 54
    folha = Image.new("RGB", (thumb[0] * colunas, (thumb[1] + faixa) * linhas), "#241518")
    d = ImageDraw.Draw(folha)
    fo = fonte("pesada", 28)
    for idx, (nome, im) in enumerate(itens):
        x = (idx % colunas) * thumb[0]
        y = (idx // colunas) * (thumb[1] + faixa)
        folha.paste(im.resize(thumb, Image.Resampling.LANCZOS), (x, y))
        rotulo = ROTULOS_CONTATO.get(nome, nome.replace("_", " ").upper())
        d.text((x + thumb[0] / 2, y + thumb[1] + faixa / 2), rotulo, font=fo, fill="#FFF1DC", anchor="mm")
    folha.save(OUT / destino, quality=92)


def main():
    imagens = [(nome, render(spec, nome)) for nome, spec in COMPONENTES.items()]
    grade(imagens, "contato.jpg", 4)
    cenas = [(f"cena_{i}", render(spec, f"_layout_cena_{i}")) for i, spec in enumerate(CENAS, 1)]
    grade(cenas, "cenas_exemplo.jpg", 3)
    for i in range(1, 7):
        (OUT / f"_layout_cena_{i}.png").unlink(missing_ok=True)
    print(f"Gerados {len(imagens)} previews e {len(cenas)} layouts em {OUT}")


if __name__ == "__main__":
    main()
