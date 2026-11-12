"""Componentes da Colagem Documental deste vídeo (Raphinha).

Estilo por dados: cada componente é um recorte (spec do `media/colagem_lib.py`), um carimbo, uma tira ou uma anotação, sem código por cena.
As figuras que a biblioteca não tem (adolescente de perfil, robô, ferramenta...) nascem aqui, por código, em tons de cinza: entram pelo
campo `arquivo`, passam pela mesma retícula e ficam em `componentes/figuras/`. Nenhuma é foto, mídia externa ou pessoa real.

Uso no cenas.json: copie o spec de RECORTES (com x, y, rot, t, entrada) ou o bloco inteiro da cena em CENAS.
"""
from pathlib import Path

from PIL import Image, ImageDraw

from media.camadas import aplicar, compor, girar, mover
from media.colagem_lib import AMARELO, BRANCO, DENS, PRETO, VERMELHO, _anotacao_sprite, _carimbo, fonte

PASTA = Path(__file__).resolve().parent
FIGURAS_DIR = "componentes/figuras"
S = 1000
SS = 2


# ---------- figuras em cinza: tom puro fica liso na retícula, tom médio vira ponto ----------
def _fundo(w=S, h=S, topo=222, base=168):
    im = Image.new("L", (w * SS, h * SS), topo)
    d = ImageDraw.Draw(im)
    for y in range(h * SS):
        d.line([(0, y), (w * SS, y)], fill=int(topo + (base - topo) * y / (h * SS)))
    return im, d


def _reduzir(im):
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)


def _p(*pts):
    return [(x * SS, y * SS) for x, y in pts]


def _caixa(x0, y0, x1, y1):
    return (x0 * SS, y0 * SS, x1 * SS, y1 * SS)


def fig_adolescente_celular():
    """Adolescente de perfil, de capuz, olhando o celular. Sem rosto; o celular está de lado, então não há tela vazia."""
    im, d = _fundo()
    d.ellipse(_caixa(150, 130, 480, 480), fill=26)  # capuz
    d.ellipse(_caixa(250, 170, 510, 440), fill=26)  # cabeça, inclinada para o celular
    d.polygon(_p((495, 285), (548, 365), (490, 385)), fill=26)  # nariz: é o que faz ler como perfil
    d.polygon(_p((70, 1000), (110, 640), (220, 460), (410, 440), (520, 600), (560, 1000)), fill=26)  # tronco
    d.line(_p((400, 720), (560, 850), (790, 700)), fill=26, width=88 * SS, joint="curve")  # braço, na altura do peito
    d.ellipse(_caixa(745, 650, 840, 745), fill=26)  # mão
    d.polygon(_p((770, 500), (812, 490), (872, 720), (830, 730)), fill=10)  # celular de lado, longe do rosto
    for x0, y0, x1, y1 in ((745, 515, 600, 440), (760, 590, 620, 545)):  # dois traços de luz da tela para o rosto
        d.line(_p((x0, y0), (x1, y1)), fill=250, width=12 * SS)
    return _reduzir(im)


def fig_robo():
    """Robô genérico, de traço próprio."""
    im, d = _fundo()
    d.line(_p((500, 240), (500, 130)), fill=26, width=26 * SS)
    d.ellipse(_caixa(455, 80, 545, 170), fill=26)
    d.rectangle(_caixa(190, 370, 250, 520), fill=26)
    d.rectangle(_caixa(750, 370, 810, 520), fill=26)
    d.rounded_rectangle(_caixa(245, 235, 755, 650), radius=70 * SS, fill=26)
    for x in (375, 625):
        d.ellipse(_caixa(x - 62, 355, x + 62, 479), fill=250)
        d.ellipse(_caixa(x - 26, 391, x + 26, 443), fill=20)
    d.rounded_rectangle(_caixa(350, 535, 650, 590), radius=14 * SS, fill=250)
    for x in (425, 500, 575):
        d.rectangle(_caixa(x - 7, 535, x + 7, 590), fill=26)
    d.rectangle(_caixa(440, 650, 560, 710), fill=26)
    d.rounded_rectangle(_caixa(170, 705, 830, 1060), radius=70 * SS, fill=26)
    d.rounded_rectangle(_caixa(390, 770, 610, 880), radius=16 * SS, fill=250)
    d.ellipse(_caixa(475, 800, 525, 850), fill=26)
    return _reduzir(im)


def fig_ferramenta():
    """Chave de boca: é o 'ferramenta' do dado."""
    camada = Image.new("L", (S * SS, S * SS), 0)
    d = ImageDraw.Draw(camada)
    d.rounded_rectangle(_caixa(425, 300, 575, 880), radius=50 * SS, fill=255)
    d.ellipse(_caixa(300, 90, 700, 490), fill=255)
    d.polygon(_p((420, 40), (580, 40), (570, 290), (430, 290)), fill=0)  # boca da chave
    d.ellipse(_caixa(462, 760, 538, 836), fill=0)  # furo do cabo
    mascara = camada.rotate(-42, resample=Image.BICUBIC, center=(S * SS / 2, S * SS / 2))
    im, _ = _fundo()
    im.paste(26, (0, 0), mascara)
    return _reduzir(im)


def fig_controle():
    """Controle de videogame genérico: diversão."""
    im, d = _fundo()
    d.ellipse(_caixa(90, 340, 470, 840), fill=26)
    d.ellipse(_caixa(530, 340, 910, 840), fill=26)
    d.rounded_rectangle(_caixa(190, 300, 810, 660), radius=150 * SS, fill=26)
    d.rectangle(_caixa(265, 395, 315, 565), fill=250)
    d.rectangle(_caixa(205, 455, 375, 505), fill=250)
    for x, y in ((680, 400), (680, 520), (620, 460), (740, 460)):
        d.ellipse(_caixa(x - 34, y - 34, x + 34, y + 34), fill=250)
    return _reduzir(im)


def fig_lupa():
    """Lupa com interrogação: curiosidade."""
    im, d = _fundo()
    d.line(_p((640, 640), (880, 880)), fill=26, width=92 * SS)
    d.ellipse(_caixa(120, 120, 720, 720), fill=26)
    d.ellipse(_caixa(190, 190, 650, 650), fill=250)
    d.text((420 * SS, 420 * SS), "?", font=fonte("impacto", 340 * SS), fill=26, anchor="mm")
    return _reduzir(im)


def _pessoa(d, cx, base, r, tom):
    d.ellipse(_caixa(cx - r, base - 3.1 * r, cx + r, base - 1.1 * r), fill=tom)
    d.rounded_rectangle(_caixa(cx - 1.75 * r, base - 0.95 * r, cx + 1.75 * r, base + 2 * r), radius=int(0.8 * r) * SS, fill=tom)


def fig_um_em_cada_tres():
    """Três figuras, uma cheia: mostra o 'um em cada três' sem virar gráfico."""
    im, d = _fundo(1500, 930, 250, 250)
    _pessoa(d, 260, 660, 120, 150)
    _pessoa(d, 750, 660, 120, 12)
    _pessoa(d, 1240, 660, 120, 150)
    return _reduzir(im)


def fig_com_quem():
    """Contorno vazio com interrogação: a pessoa que falta na pergunta final."""
    im, d = _fundo()
    cx, r = 500, 165
    cab = (cx - r, 170, cx + r, 500)
    d.ellipse(_caixa(*cab), fill=250)
    d.rounded_rectangle(_caixa(cx - 310, 530, cx + 310, 1090), radius=130 * SS, fill=250)
    for a in range(0, 360, 20):  # tracejado da cabeça
        d.arc(_caixa(*cab), a, a + 11, fill=26, width=15 * SS)
    tracos = [((x, 530), (x + 42, 530)) for x in range(cx - 230, cx + 200, 72)]
    tracos += [((x, 530 + 130), (x, 530 + 172)) for x in (cx - 310, cx + 310)] + [((x, 760), (x, 802)) for x in (cx - 310, cx + 310)] + [((x, 880), (x, 922)) for x in (cx - 310, cx + 310)]
    for a_, b_ in tracos:
        d.line(_p(a_, b_), fill=26, width=15 * SS)
    d.text((cx * SS, 335 * SS), "?", font=fonte("impacto", 230 * SS), fill=26, anchor="mm")
    return _reduzir(im)



FIGURAS = {
    "adolescente_celular": fig_adolescente_celular, "robo": fig_robo, "ferramenta": fig_ferramenta, "controle": fig_controle,
    "lupa": fig_lupa, "um_em_cada_tres": fig_um_em_cada_tres, "com_quem": fig_com_quem,
}


def gerar_figuras():
    d = PASTA / FIGURAS_DIR
    d.mkdir(parents=True, exist_ok=True)
    for nome, fn in FIGURAS.items():
        fn().save(d / f"{nome}.png")


def _arq(nome):
    return f"{FIGURAS_DIR}/{nome}.png"


# ---------- recortes (textos só do roteiro.txt e das notas) ----------
RECORTES = {
    "foto_adolescente_celular": {"tipo": "foto", "arquivo": _arq("adolescente_celular"), "larg": 350, "proporcao": 1.0, "legenda": "seu filho"},
    "foto_amigos": {"tipo": "foto", "figura": "grupo", "larg": 350, "proporcao": 0.92, "legenda": "os amigos"},
    "foto_robo": {"tipo": "foto", "arquivo": _arq("robo"), "larg": 270, "proporcao": 0.85, "legenda": "um robô?"},
    "foto_ferramenta": {"tipo": "foto", "arquivo": _arq("ferramenta"), "larg": 500, "proporcao": 0.85, "legenda": "ferramenta"},
    "foto_diversao": {"tipo": "foto", "arquivo": _arq("controle"), "larg": 520, "proporcao": 0.72, "legenda": "diversão"},
    "foto_curiosidade": {"tipo": "foto", "arquivo": _arq("lupa"), "larg": 400, "proporcao": 0.9, "legenda": "curiosidade"},
    "foto_amigos_de_verdade": {"tipo": "foto", "figura": "grupo", "larg": 640, "proporcao": 0.72, "legenda": "amigos de verdade"},
    "foto_um_em_cada_tres": {"tipo": "foto", "arquivo": _arq("um_em_cada_tres"), "larg": 640, "proporcao": 0.56, "legenda": "entre quem usa"},
    "foto_com_quem": {"tipo": "foto", "arquivo": _arq("com_quem"), "larg": 400, "proporcao": 1.1, "legenda": "com quem?"},
    "foto_ia": {"tipo": "foto", "arquivo": _arq("robo"), "larg": 300, "proporcao": 0.95, "legenda": "a IA"},
    "foto_gente": {"tipo": "foto", "figura": "grupo", "larg": 300, "proporcao": 0.95, "legenda": "gente"},
    "doc_pesquisa": {"tipo": "documento", "larg": 860, "titulo": "PESQUISA NACIONAL", "linhas": ["Estados Unidos, 2025", "Adolescentes de verdade", "Ilustração do canal"]},
    "doc_como_veem": {"tipo": "documento", "larg": 860, "titulo": "COMO ELES VEEM", "linhas": ["Ferramenta, não amiga"]},
    "doc_assunto_serio": {"tipo": "documento", "larg": 860, "titulo": "ASSUNTO SÉRIO", "linhas": ["Falou com a IA,", "e não com alguém"]},
    "doc_ia": {"tipo": "documento", "larg": 570, "titulo": "A IA", "linhas": ["Responde na hora", "Não julga"]},
    "doc_gente": {"tipo": "documento", "larg": 570, "titulo": "GENTE", "linhas": ["Conversar dá", "mais trabalho"]},
    "selo_um_em_cada_tres": {"tipo": "data", "data": "1 EM CADA 3"},
    "mapa_eua": {"tipo": "mapa", "larg": 470, "pinos": [{"x": 0.42, "y": 0.48}]},
    "mapa_brasil": {"tipo": "mapa", "larg": 470, "pinos": [{"x": 0.56, "y": 0.52}]},
    "jornal_aviso": {"tipo": "jornal", "larg": 900, "manchete": "Empresa anuncia o fim do chat aberto para menores", "sub": "Ilustração do canal"},
}
CARIMBOS = {
    "carimbo_quase_o_contrario": {"texto": "QUASE O CONTRÁRIO"},
    "carimbo_atencao": {"texto": "ATENÇÃO"},
    "carimbo_dados_dos_eua": {"texto": "DADOS DOS EUA"},
    "carimbo_anunciado": {"texto": "ANUNCIADO"},
}
# Tiras: o texto grande de cada cena. `textos` da biblioteca, sempre por cima de tudo.
TIRAS = {
    "tira_trocou": {"texto": "TROCOU OS AMIGOS", "tam": 80},
    "tira_robo": {"texto": "POR UM ROBÔ?", "tam": 80},
    "tira_americana": {"texto": "A PESQUISA É AMERICANA", "tam": 84},
    "tira_eua": {"texto": "EUA", "tam": 96},
    "tira_quase_metade": {"texto": "QUASE METADE", "tam": 118},
    "tira_motivo": {"texto": "O MOTIVO MAIS CITADO", "tam": 88},
    "tira_maioria": {"texto": "A MAIORIA DIZ", "tam": 84},
    "tira_mais_tempo": {"texto": "MAIS TEMPO COM AMIGOS", "tam": 84},
    "tira_leitura": {"texto": "LEITURA DO CANAL", "tam": 96, "cor": VERMELHO},
    "tira_nao_e_defeito": {"texto": "NÃO É DEFEITO DE GERAÇÃO", "tam": 72},
    "tira_atencao": {"texto": "E ATENÇÃO", "tam": 96, "cor": VERMELHO},
    "tira_brasil": {"texto": "BRASIL?", "tam": 96},
    "tira_com_quem": {"texto": "COM QUEM ELES FALAM", "tam": 84},
    "tira_pesa": {"texto": "QUANDO O ASSUNTO PESA", "tam": 84, "cor": VERMELHO},
}
# Anotações v3: bilhete amarelo, caneta preta, frase inteira em até duas linhas. Cada linha é uma anotação da biblioteca (até 26 caracteres).
ANOTACOES = {
    "nota_depois": {"linhas": ["e depois..."]},
    "nota_menos_tempo": {"linhas": ["menos tempo", "com a IA"]},
    "nota_nao_da": {"linhas": ["não dá para dizer", "que o Brasil é igual"]},
    "nota_nao_e_se_usam": {"linhas": ["a pergunta não é", "se eles usam"]},
}
PASSO_LINHA = 82


def rec(nome, id_=None, **pos):
    """Recorte pronto para o cenas.json, com posição e entrada."""
    return {"id": id_ or nome, **RECORTES[nome], **pos}


def car(nome, **pos):
    return {**CARIMBOS[nome], **pos}


def tira(nome, **pos):
    return {**TIRAS[nome], **pos}


def postit(nome, x, y, t, rot=-3, seta_para=None):
    """Bilhete pronto: o papel amarelo (vai em `recortes`) e uma anotação por linha (vão em `anotacoes`), escritas em sequência."""
    linhas = ANOTACOES[nome]["linhas"]
    m = compor(mover(x, y), girar(rot))
    anotacoes, larg = [], 0
    for i, texto in enumerate(linhas):
        px, py = aplicar(m, 0, (i - (len(linhas) - 1) / 2) * PASSO_LINHA)
        anotacoes.append({"texto": texto, "cor": PRETO, "x": round(px), "y": round(py), "rot": rot, "t": round(t + i * 0.45, 2)})
        s = _anotacao_sprite(texto, PRETO)
        larg = max(larg, s.im.width / DENS)
    if seta_para:
        anotacoes[0]["seta_para"] = seta_para
    larg += 80
    alt = len(linhas) * PASSO_LINHA + 66
    papel = {"id": f"papel_{nome}", "tipo": "papel", "cor": AMARELO, "larg": round(larg), "proporcao": alt / larg, "x": x, "y": y, "rot": rot, "t": max(0, t - 0.2), "entrada": "corte", "rasgo": ""}
    return {"papel": papel, "anotacoes": anotacoes}


def _apoio(id_, w, h, c, folga):
    """Papel claro sob carimbo ou anotação: tinta vermelha direto na mesa e nos retalhos do fundo perde leitura."""
    larg = w + folga
    return {"id": id_, "tipo": "papel", "cor": BRANCO, "larg": larg, "proporcao": (h + folga * 0.5) / larg, "x": c["x"], "y": c["y"], "rot": c.get("rot", -3), "t": max(0, c["t"] - 0.15), "entrada": "corte", "rasgo": "de"}


def apoio_de(rotulo):
    """Id do papel de apoio de um elemento ('carimbo:TEXTO' ou 'nota:LINHA')."""
    tipo, texto = rotulo.split(":", 1)
    if tipo == "nota":
        return next(f"papel_{nome}" for nome, spec in ANOTACOES.items() if texto in spec["linhas"])
    return "papel_" + texto


def apoio_carimbo(c):
    s = _carimbo(c["texto"], VERMELHO, len(c["texto"]))
    return _apoio(apoio_de("carimbo:" + c["texto"]), s.im.width / DENS, s.im.height / DENS, {**c, "rot": c.get("rot", -10)}, 40)


# ---------- layout sugerido: uma ideia visual por cena. "3a/3b/3c" e "5a/5b" são frases separadas do roteiro ----------
def _cena(n, rotulo, fala, superficie, recortes, postits=(), **resto):
    apoios = [apoio_carimbo(k) for k in resto.get("carimbos", ())] + [b["papel"] for b in postits]
    if postits:
        resto["anotacoes"] = [a for b in postits for a in b["anotacoes"]]
    return {"tipo": "documentary_collage", "desenho": f"cena_{n}", "rotulo_raphinha": rotulo, "fala": fala, "duracao": 5, "acao": rotulo, "superficie": superficie, "recortes": apoios + recortes, **resto}


CENAS = [
    _cena(0, "1 gancho", "Seu filho trocou os amigos por um robô? A pesquisa diz quase o contrário.", "mesa_preta", [
        rec("foto_adolescente_celular", x=210, y=715, rot=-3, t=0, entrada="corte", ax=150, ay=200),
        rec("foto_amigos", x=860, y=705, rot=3, t=0, entrada="corte", ax=-150, ay=190),
        rec("foto_robo", x=540, y=1115, rot=-2, t=0.6, entrada="pousa", ay=-170),
    ], conexoes=[{"de": "foto_adolescente_celular", "para": "foto_robo", "t": 0.9, "dur": 0.4}, {"de": "foto_amigos", "para": "foto_robo", "t": 1.1, "dur": 0.4}],
        textos=[tira("tira_trocou", x=540, y=265, t=0, entrada="corte"), tira("tira_robo", x=540, y=395, t=0, entrada="corte")],
        carimbos=[car("carimbo_quase_o_contrario", x=540, y=1412, rot=-3, t=3.0)]),
    _cena(1, "2 pesquisa", "A pesquisa é americana, feita com adolescentes de verdade.", "kraft", [
        rec("doc_pesquisa", x=540, y=640, rot=-2, t=0, fita=True),
        rec("mapa_eua", larg=430, x=275, y=1280, rot=-3, t=0.8, entrada="desliza", ax=205),
        rec("foto_amigos", id_="foto_adolescentes", legenda="adolescentes", larg=390, x=790, y=1185, rot=4, t=1.3, entrada="desliza", ax=-185),
    ], conexoes=[{"de": "mapa_eua", "para": "foto_adolescentes", "t": 1.8, "dur": 0.4}],
        textos=[tira("tira_americana", x=540, y=300, t=0.1), tira("tira_eua", tam=72, x=275, y=962, t=0.9)], destaques=[{"em": "doc_pesquisa", "linha": 0, "t": 1.2, "dur": 0.5}]),
    _cena(2, "3a ferramenta", "Quase metade vê a companhia de IA como ferramenta, não como amiga.", "mesa_preta", [
        rec("foto_ferramenta", x=540, y=720, rot=-3, t=0.3),
        rec("doc_como_veem", x=540, y=1230, rot=2, t=1.2, entrada="desliza", fita=True),
    ], textos=[tira("tira_quase_metade", x=540, y=300, t=0)], destaques=[{"em": "doc_como_veem", "linha": 0, "t": 2.2, "dur": 0.6}]),
    _cena(3, "3b motivos", "O motivo mais citado é diversão. Depois, curiosidade.", "papel_bege", [
        rec("foto_diversao", x=390, y=690, rot=-3, t=0.2, ax=120, ay=240),
        rec("foto_curiosidade", x=720, y=1170, rot=4, t=1.8, entrada="desliza", ay=-250),
    ], conexoes=[{"de": "foto_diversao", "para": "foto_curiosidade", "t": 1.6, "dur": 0.4}],
        textos=[tira("tira_motivo", x=540, y=285, t=0)], postits=[postit("nota_depois", x=270, y=1130, t=1.6, seta_para=[500, 1060])]),
    _cena(4, "3c amigos", "E a maioria diz passar mais tempo com amigos de verdade.", "kraft", [
        rec("foto_amigos_de_verdade", x=540, y=810, rot=-2, t=0.3, fita=True),
        rec("foto_robo", id_="foto_robo_pequena", legenda="a IA", larg=240, x=840, y=1290, rot=5, t=1.6, entrada="desliza"),
    ], textos=[tira("tira_maioria", x=540, y=265, t=0), tira("tira_mais_tempo", x=540, y=405, t=0.5)],
        postits=[postit("nota_menos_tempo", x=320, y=1385, t=2.2, seta_para=[690, 1255])]),
    _cena(5, "4 virada", "Só que tem coisa que ninguém devia ignorar. Entre quem usa, um em cada três já escolheu falar de assunto sério com a IA, e não com alguém.", "mesa_preta", [
        rec("selo_um_em_cada_tres", x=540, y=305, rot=-2, t=1.4),
        rec("foto_um_em_cada_tres", x=540, y=655, rot=1.5, t=1.0),
        rec("doc_assunto_serio", x=540, y=1095, rot=-2, t=2.6, entrada="desliza", fita=True),
    ], destaques=[{"em": "doc_assunto_serio", "linha": 0, "t": 3.6, "dur": 0.6}],
        carimbos=[car("carimbo_atencao", x=540, y=1405, rot=-4, t=0.2)]),
    _cena(6, "5a leitura do canal", "Na nossa leitura, isso não é defeito de uma geração. A IA responde na hora e não julga. E conversar com gente dá mais trabalho.", "papel_bege", [
        rec("foto_ia", x=205, y=600, rot=-3, t=1.4),
        rec("doc_ia", x=715, y=600, rot=1.5, t=1.6, entrada="desliza"),
        rec("foto_gente", x=205, y=1040, rot=3, t=2.8),
        rec("doc_gente", x=715, y=1040, rot=-1.5, t=3.0, entrada="desliza"),
    ], textos=[tira("tira_leitura", x=540, y=285, t=0), tira("tira_nao_e_defeito", x=540, y=1370, t=0.6)]),
    _cena(7, "5b ressalva", "E atenção: a pesquisa é dos Estados Unidos. Não dá para dizer que o Brasil é igual.", "folha_branca", [
        rec("mapa_eua", x=275, y=810, rot=-3, t=0.1),
        rec("mapa_brasil", x=805, y=810, rot=3, t=1.6, entrada="desliza"),
    ], textos=[tira("tira_atencao", x=540, y=265, t=0), tira("tira_eua", x=275, y=445, t=0.2), tira("tira_brasil", x=805, y=445, t=1.7)],
        carimbos=[car("carimbo_dados_dos_eua", x=540, y=1185, rot=-5, t=0.9)], postits=[postit("nota_nao_da", x=540, y=1420, t=2.2)]),
    _cena(8, "6 empresa", "Já há empresa anunciando o fim do chat aberto para menores.", "kraft", [
        rec("jornal_aviso", x=540, y=760, rot=-2, t=0.1, fita=True),
    ], destaques=[{"em": "jornal_aviso", "linha": 1, "t": 1.2, "dur": 0.6}], carimbos=[car("carimbo_anunciado", x=540, y=1350, rot=-7, t=2.0)]),
    _cena(9, "7 pergunta final", "Então a pergunta não é se eles usam. É com quem falam quando o assunto pesa.", "mesa_preta", [
        rec("foto_adolescente_celular", larg=400, x=285, y=850, rot=-3, t=0.2, ax=170, ay=0),
        rec("foto_com_quem", x=800, y=850, rot=3, t=1.6, entrada="desliza", ax=-170, ay=0),
    ], conexoes=[{"de": "foto_adolescente_celular", "para": "foto_com_quem", "t": 2.2, "dur": 0.5}],
        textos=[tira("tira_com_quem", x=540, y=265, t=1.6), tira("tira_pesa", x=540, y=405, t=2.2)],
        postits=[postit("nota_nao_e_se_usam", x=540, y=1310, t=0.3)]),
]
