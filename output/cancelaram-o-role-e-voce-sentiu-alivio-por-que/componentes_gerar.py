"""Componentes do vídeo no estilo Cartoon Vivo: tudo sai de media.cartoon_lib, o mesmo código do render.

Gera, em componentes/:
- um PNG por componente, mais contato.jpg (rotulado) e cenas_exemplo.jpg (layout de cada momento);
- o checador de sobreposição: isola cada elemento pela diferença de pixels entre dois quadros reais e acusa
  qualquer encontro entre personagem, objeto, balão e texto, nos momentos listados em cada cena.

Uso, na raiz do projeto: .venv\\Scripts\\python output\\<slug>\\componentes_gerar.py
"""
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))

from media.camadas import fonte  # noqa: E402
from media.cartoon_lib import ELENCO, PALETAS, compor_cena, validar  # noqa: E402

OUT = Path(__file__).with_name("componentes")
PALETA = "noite"
COR = PALETAS[PALETA]
MARGEM = 8  # folga do checador, em pixels do quadro: cobre a deriva da câmera e a respiração


# ---------- blocos de spec ----------
def cena(nome, cenario, personagens=(), objetos=(), textos=(), baloes=(), acao="Prévia de componente."):
    return {"tipo": "cartoon_alive", "desenho": nome, "fala": "Prévia.", "duracao": 6.0, "paleta": PALETA, "acao": acao, "cenario": cenario,
            "personagens": list(personagens), "objetos": list(objetos), "textos": list(textos), "baloes": list(baloes),
            "camera": {"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}]}, "transicao": {"entrada": "corte", "saida": "corte"}}


def ator(ident, x, poses, escala=1.1, olha="dir", y=1440, segura=None):
    if isinstance(poses, tuple):
        poses = [(0, *poses)]
    a = {"id": ident, "x": x, "y": y, "escala": escala, "olha": olha, "entrada": "corte", "poses": [{"t": t, "pose": p, "expressao": e} for t, p, e in poses]}
    if segura:
        a["segura"] = segura
    return a


def celular_mao(texto, escala=0.95):
    return {"tipo": "celular", "texto": texto, "escala": escala}


def obj(tipo, x, y, escala=1.0, t=0, ate=None, texto=None, rot=None):
    o = {"tipo": tipo, "x": x, "y": y, "escala": escala, "t": t, "entrada": "corte", "balanco": 0}
    if ate is not None:
        o["ate"] = ate
    if texto:
        o["texto"] = texto
    if rot is not None:
        o["rot"] = rot
    return o


def txt(texto, y, tam=110, cor="destaque", t=0, ate=None, x=540):
    d = {"texto": texto, "x": x, "y": y, "tam": tam, "t": t, "entrada": "corte", "cor": cor}
    if ate is not None:
        d["ate"] = ate
    return d


def balao(de, linhas, t=0, ate=None, **pos):
    b = {"de": de, "linhas": linhas, "t": t, **pos}
    if ate is not None:
        b["ate"] = ate
    return b


# ---------- componentes isolados ----------
MSG_CONVITE, MSG_CANCELOU, MSG_DESMARCA = "hoje tem rolê!", "galera, hoje não rola", "não vou, foi mal"


def _pose(ident, pose, expr):
    return cena("c", "liso", [ator(ident, 540, (pose, expr), 1.3)])


def _objeto(tipo, escala=1.5, texto=None):
    return cena("c", "liso", objetos=[obj(tipo, 540, 960, escala, texto=texto)])


COMPONENTES = {
    "elenco_teo_pronto": cena("c", "liso", [ator("teo", 400, ("segura", "feliz"), 1.3, segura=celular_mao(MSG_CONVITE))]),
    "elenco_teo_alivio": cena("c", "liso", [ator("teo", 400, ("ombros", "risada"), 1.3, segura=celular_mao(MSG_CANCELOU))]),
    "elenco_teo_desconfiado": _pose("teo", "maos_cintura", "pensativa"),
    "elenco_teo_digita": cena("c", "liso", [ator("teo", 400, ("segura", "neutra"), 1.3, segura=celular_mao(MSG_DESMARCA))]),
    "elenco_teo_empolgado": _pose("teo", "comemora", "risada"),
    "elenco_teo_peso": _pose("teo", "triste", "triste"),
    "elenco_teo_ansioso": _pose("teo", "medo", "medo"),
    "elenco_teo_cansado": _pose("teo", "neutra", "triste"),
    "elenco_teo_sereno": _pose("teo", "neutra", "feliz"),
    "elenco_teo_de_ombros": _pose("teo", "ombros", "neutra"),
    "elenco_teo_pensando": _pose("teo", "pensando", "pensativa"),
    "elenco_bia_amiga": _pose("bia", "neutra", "feliz"),
    "elenco_bia_distraida": _pose("bia", "pensando", "pensativa"),
    "elenco_bia_apressada": _pose("bia", "medo", "medo"),
    "elenco_zeca_aponta": _pose("zeca", "aponta", "brava"),
    "elenco_zeca_neutro": _pose("zeca", "neutra", "feliz"),
    "cenario_sala": cena("c", "sala"),
    "cenario_rua": cena("c", "rua"),
    "cenario_quarto": cena("c", "quarto"),
    "cenario_liso": cena("c", "liso"),
    "celular_convite": _objeto("celular", 2.0, MSG_CONVITE),
    "celular_cancelou": _objeto("celular", 2.0, MSG_CANCELOU),
    "celular_desmarca": _objeto("celular", 2.0, MSG_DESMARCA),
    "objeto_calendario": _objeto("calendario", 1.5, "hoje"),
    "objeto_relogio": _objeto("relogio"),
    "objeto_raio": _objeto("raio"),
    "objeto_suor": _objeto("suor", 2.5),
    "objeto_coracao": _objeto("coracao"),
    "objeto_casa": _objeto("casa"),
    "balao_sem_compromisso": cena("c", "liso", baloes=[balao(None, ["sem compromisso?"], x=540, y=960)]),
    "balao_bora": cena("c", "liso", baloes=[balao(None, ["bora!"], x=540, y=960)]),
    "balao_ficar_de_fora": cena("c", "liso", baloes=[balao(None, ["ficar", "de fora"], x=540, y=960)]),
    "balao_ansiedade_social": cena("c", "liso", baloes=[balao(None, ["ansiedade", "social"], x=540, y=960)]),
    "balao_cansaco": cena("c", "liso", baloes=[balao(None, ["cansaço", "e ansiedade"], x=540, y=960)]),
    "texto_alivio": cena("c", "liso", textos=[txt("ALÍVIO", 960, 150)]),
    "texto_ufa": cena("c", "liso", textos=[txt("UFA!", 960, 150, "apoio")]),
    "texto_contexto": cena("c", "liso", textos=[txt("CONTEXTO", 900, 118), txt("NÃO EXPLICA TUDO", 1040, 92, "claro")]),
    "texto_pergunta": cena("c", "liso", textos=[txt("ALÍVIO PRA DESCANSAR", 900, 92, "claro"), txt("OU DE VER PESSOAS?", 1030, 92)]),
}


# ---------- layout sugerido: uma entrada por momento da fala (os `t` são de exemplo; o Olise acerta pelo áudio) ----------
def _c(nome, cenario, acao, personagens, objetos=(), textos=(), baloes=(), momentos=()):
    return {"spec": cena(nome, cenario, personagens, objetos, textos, baloes, acao), "momentos": momentos}


TEO_E, TEO_D, TEO_MAO = 290, 800, 300
LAYOUT = [
    _c("cena_1", "sala", "Téo, pronto para sair, olha o convite do grupo no celular.",
       [ator("teo", TEO_MAO, ("segura", "feliz"), 1.3, segura=celular_mao(MSG_CONVITE))],
       momentos=(("convite", 0.7),)),
    _c("cena_2", "sala", "Chega o cancelamento: susto, e logo ele solta o ar, aliviado.",
       [ator("teo", TEO_MAO, [(0, "segura", "surpresa"), (1.5, "ombros", "risada")], 1.3, segura=celular_mao(MSG_CANCELOU))],
       textos=[txt("ALÍVIO", 290, 130, t=1.5)],
       momentos=(("cancelou", 0.8), ("alivio", 3.0))),
    _c("cena_3", "rua", "Seu Zeca aponta e rotula; Téo olha de lado, desconfiado.",
       [ator("teo", 250, ("maos_cintura", "pensativa"), 1.05), ator("zeca", 830, ("aponta", "brava"), 1.05, "esq")],
       baloes=[balao("zeca", ["sem compromisso?"], x=640, y=620)],
       momentos=(("rotulo", 1.0),)),
    _c("cena_4", "quarto", "Téo manda a desculpa pelo celular: uma mensagem, sem ligar.",
       [ator("teo", TEO_MAO, [(0, "segura", "neutra"), (2.5, "segura", "feliz")], 1.3, segura=celular_mao(MSG_DESMARCA))],
       momentos=(("mensagem", 1.0), ("sem_custo", 3.5))),
    _c("cena_5", "sala", "Téo aceita no impulso; quando o dia chega, o calendário pesa e ele se curva.",
       [ator("teo", 400, [(0, "comemora", "risada"), (2.5, "triste", "triste")], 1.1)],
       [obj("calendario", 400, 440, 1.25, t=2.5, texto="hoje"), obj("suor", 700, 880, 1.8, t=3)],
       baloes=[balao("teo", ["bora!"], 0, 2.3, x=770, y=860)],
       momentos=(("bora", 1.0), ("peso", 4.0))),
    _c("cena_6", "sala", "O prazer de ficar de fora vira, no rosto de Téo, ansiedade social.",
       [ator("teo", 360, [(0, "neutra", "feliz"), (2.5, "medo", "medo")], 1.1)],
       [obj("suor", 105, 950, 1.8, t=2.5)],
       baloes=[balao("teo", ["ficar", "de fora"], 0, 2.3, x=790, y=830), balao("teo", ["ansiedade", "social"], 2.5, x=790, y=830)],
       momentos=(("fora", 1.0), ("ansiedade", 4.0))),
    _c("cena_7", "sala", "Cansaço e ansiedade, não desprezo: o coração aparece entre Téo e Bia.",
       [ator("teo", TEO_E, [(0, "neutra", "triste"), (3, "neutra", "feliz")], 1.05), ator("bia", TEO_D, ("neutra", "feliz"), 1.05, "esq")],
       [obj("coracao", 545, 760, .7, t=3)],
       baloes=[balao("teo", ["cansaço", "e ansiedade"], 0, x=540, y=300)],
       momentos=(("cansaco", 1.0), ("amigos", 4.0))),
    _c("cena_8", "liso", "Bia, na correria, deixa para a última hora; Téo dá de ombros.",
       [ator("bia", TEO_E, [(0, "pensando", "pensativa"), (3, "medo", "medo")], 1.0), ator("teo", TEO_D, ("ombros", "neutra"), 1.0, "esq")],
       [obj("relogio", 170, 775, .55, t=1.5), obj("raio", 410, 775, .55, t=3)],
       [txt("CONTEXTO", 270, 112), txt("NÃO EXPLICA TUDO", 390, 88, "claro")],
       momentos=(("contexto", 1.0), ("ultima_hora", 2.2), ("impulso", 4.0))),
    _c("cena_9", "sala", "Volta à cena do começo: o celular vibra e Téo solta o ar de novo.",
       [ator("teo", TEO_MAO, [(0, "segura", "feliz"), (2, "ombros", "risada")], 1.3, segura=celular_mao(MSG_CANCELOU))],
       textos=[txt("UFA!", 290, 130, "apoio", t=2)],
       momentos=(("celular", 1.0), ("ufa", 3.0))),
    _c("cena_10", "sala", "Téo pensa nas duas saídas: a casa, para descansar, ou as pessoas que ele ia ver.",
       [ator("teo", 470, ("pensando", "pensativa"), 1.05), ator("bia", 780, ("neutra", "feliz"), .6, "esq"), ator("zeca", 985, ("neutra", "feliz"), .6, "esq")],
       [obj("casa", 130, 1360, .55)],
       [txt("ALÍVIO PRA DESCANSAR", 235, 88, "claro"), txt("OU DE VER PESSOAS?", 355, 88)],
       momentos=(("pergunta", 2.0),)),
]


# ---------- checador de sobreposição ----------
def _sem_elementos(spec, **fica):
    return {**spec, "personagens": fica.get("personagens", []), "objetos": fica.get("objetos", []), "textos": fica.get("textos", []), "baloes": fica.get("baloes", [])}


def _mascara(com, sem, lt, folga=True):
    a = compor_cena(com, lt, 6.0, paleta=PALETA).convert("RGB")
    b = compor_cena(sem, lt, 6.0, paleta=PALETA).convert("RGB")
    m = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 10 else 0)
    m = m.resize((270, 480), Image.NEAREST)
    return m.filter(ImageFilter.MaxFilter(2 * (MARGEM // 4) + 1)) if folga else m


def _celular_na_cabeca(spec, lt):
    """O celular na mão faz parte do personagem, mas não pode encostar na cabeça: compara o boneco com e sem ele, da mão para cima."""
    problemas = []
    for p in spec["personagens"]:
        if not p.get("segura"):
            continue
        sem_cel = {k: v for k, v in p.items() if k != "segura"}
        cel = _mascara(_sem_elementos(spec, personagens=[p]), _sem_elementos(spec, personagens=[sem_cel]), lt, folga=False)
        boneco = _mascara(_sem_elementos(spec, personagens=[sem_cel]), _sem_elementos(spec), lt, folga=False)
        ombro = int((p["y"] - p["escala"] * ELENCO[p["id"]]["escala"] * 360) / 4)  # linha acima da mão que segura: o que passa dela é rosto
        if ImageChops.multiply(cel, boneco).crop((0, 0, 270, ombro)).getbbox():
            problemas.append(f"celular encosta na cabeça de {p['id']}")
    return problemas


def _elementos(spec, lt):
    """Cada elemento visível em lt, com a máscara dele. O balão precisa do dono na cena para cair no lugar certo."""
    saida = {}
    for p in spec["personagens"]:
        saida[f"personagem {p['id']}"] = _mascara(_sem_elementos(spec, personagens=[p]), _sem_elementos(spec), lt)
    for chave, rotulo, nome in (("objetos", "objeto", lambda o: o["tipo"]), ("textos", "texto", lambda t_: t_["texto"]), ("baloes", "balão", lambda b: b["linhas"][0])):
        for el in spec[chave]:
            if lt < el.get("t", 0) or ("ate" in el and lt > el["ate"]):
                continue
            donos = [p for p in spec["personagens"] if p["id"] == el.get("de")]
            saida[f"{rotulo} {nome(el)}"] = _mascara(_sem_elementos(spec, personagens=donos, **{chave: [el]}), _sem_elementos(spec, personagens=donos), lt)
    return saida


def checar():
    problemas = []
    for item in LAYOUT:
        spec = item["spec"]
        validar(spec, spec["desenho"])
        for nome_m, lt in item["momentos"]:
            problemas += [f"{spec['desenho']} ({nome_m}, t={lt}): {x}" for x in _celular_na_cabeca(spec, lt)]
            els = _elementos(spec, lt)
            nomes = list(els)
            for i, a in enumerate(nomes):
                for b in nomes[i + 1:]:
                    if ImageChops.multiply(els[a], els[b]).getbbox():
                        problemas.append(f"{spec['desenho']} ({nome_m}, t={lt}): {a} encosta em {b}")
    return problemas


# ---------- imagens ----------
def grade(itens, destino, colunas, thumb):
    faixa = 44
    linhas = (len(itens) + colunas - 1) // colunas
    folha = Image.new("RGB", (thumb[0] * colunas, (thumb[1] + faixa) * linhas), COR["contorno"])
    d = ImageDraw.Draw(folha)
    fo = fonte("pesada", 17)
    for k, (nome, im) in enumerate(itens):
        x, y = (k % colunas) * thumb[0], (k // colunas) * (thumb[1] + faixa)
        folha.paste(im.resize(thumb, Image.LANCZOS), (x, y))
        d.text((x + thumb[0] / 2, y + thumb[1] + faixa / 2), nome, font=fo, fill=COR["claro"], anchor="mm")
    folha.save(OUT / destino, quality=90)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    fichas = []
    for nome, spec in COMPONENTES.items():
        if spec["personagens"] or spec["objetos"] or spec["textos"]:  # cenário ou balão sozinho é só prévia: o validador pede cena completa
            validar(spec, nome)
        im = compor_cena(spec, 2.0, 6.0, paleta=PALETA).convert("RGB")
        im.save(OUT / f"{nome}.png")
        fichas.append((nome, im))
    grade(fichas, "contato.jpg", 8, (240, 427))
    quadros = []
    for item in LAYOUT:
        spec = item["spec"]
        for nome_m, lt in item["momentos"]:
            quadros.append((f"{spec['desenho']} {nome_m}", compor_cena(spec, lt, 6.0, paleta=PALETA).convert("RGB")))
    grade(quadros, "cenas_exemplo.jpg", 6, (320, 569))
    problemas = checar()
    print(f"{len(fichas)} componentes, {len(quadros)} momentos de layout, {len(problemas)} sobreposições")
    for p in problemas:
        print(" -", p)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
