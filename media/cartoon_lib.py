"""Estilo Cartoon Vivo: desenho animado 2D feito por código, com elenco recorrente e animação limitada.

Não há código por cena: o `cenas.json` descreve cenário, personagens com poses e expressões, objetos, textos, câmera e transição,
e este módulo compõe as camadas a cada quadro. Personagem é um boneco articulado de verdade: pernas, tronco, cabeça, olhos, boca,
sobrancelhas e os dois segmentos de cada braço são sprites separados, recolocados por matriz.

Contrato de uma cena (px no quadro de 1080x1920; `t` em segundos da cena):
{"tipo": "cartoon_alive", "desenho": "cena_0", "fala": "...", "duracao": 4, "paleta": "sol", "acao": "o que acontece, em uma frase",
 "cenario": "rua",
 "personagens": [{"id": "bia", "x": 360, "y": 1440, "escala": 1.1, "olha": "dir", "entrada": "salto", "t": 0.1, "fala": true,
                  "poses": [{"t": 0, "pose": "neutra", "expressao": "feliz"}, {"t": 1.4, "pose": "aponta", "expressao": "surpresa"}]}],
 "objetos": [{"tipo": "celular", "x": 760, "y": 900, "escala": 1.2, "t": 0.6, "entrada": "pop", "texto": "54%"}],
 "textos": [{"texto": "54%", "x": 540, "y": 420, "tam": 170, "t": 0.2, "ate": 3.0, "entrada": "pop", "cor": "destaque"}],
 "baloes": [{"de": "bia", "linhas": ["sério?"], "t": 1.2, "ate": 3.0}],
 "camera": {"chaves": [{"t": 1.4, "x": 540, "y": 800, "zoom": 1.0}, {"t": 1.6, "x": 400, "y": 700, "zoom": 1.35, "curva": "rapida"}],
            "tremidas": [{"t": 1.6, "forca": 26}]},
 "transicao": {"entrada": "corte", "saida": "chicote"}, "rotulos": [...], "sons": [...]}
"""
import math
from functools import lru_cache

from PIL import Image

from .camadas import (DENS, SEGURO_BASE, SEGURO_TOPO, H, W, Camera, Sprite, aplicar, chave_em, circulo, clamp, compor, desenhar, entrada, escalar, fechar_loop, fonte, forma, girar, mola, mover,
                      retangulo, saida_rapida, suave, texto_sprite, tremida)

MAX_TEXTO = 26
CHAO = 1460
CAMPOS = {"paleta", "acao", "cenario", "personagens", "objetos", "textos", "baloes", "camera", "transicao"}

# Cada paleta tem exatamente 6 cores, e nada no vídeo usa outras (fora o antisserrilhado).
PALETAS = {
    "sol": {"fundo": "#FFC83D", "claro": "#FFF6E0", "contorno": "#1E1B2E", "pele": "#F2A36B", "destaque": "#E6392F", "apoio": "#2B6CE0"},
    "noite": {"fundo": "#24305E", "claro": "#F4F1E8", "contorno": "#10101C", "pele": "#E9A178", "destaque": "#FF5A5F", "apoio": "#FFB627"},
    "menta": {"fundo": "#8FE0C4", "claro": "#FBFBF2", "contorno": "#1B2430", "pele": "#E7A27C", "destaque": "#F2542D", "apoio": "#5B3FD6"},
    "tijolo": {"fundo": "#E8704A", "claro": "#FFF1DC", "contorno": "#241518", "pele": "#F4B98A", "destaque": "#FFD23F", "apoio": "#1F6F8B"},
}
ELENCO = {  # personagens originais do canal; a cor vem do papel na paleta, então combinam com qualquer vídeo
    "bia": {"nome": "Bia", "cabelo": "chanel", "cor_cabelo": "contorno", "roupa": "destaque", "calca": "apoio", "escala": 1.0},
    "teo": {"nome": "Téo", "cabelo": "topete", "cor_cabelo": "destaque", "roupa": "apoio", "calca": "contorno", "escala": 1.04, "oculos": True},
    "lu": {"nome": "Dona Lu", "cabelo": "coque", "cor_cabelo": "claro", "roupa": "apoio", "calca": "destaque", "escala": 0.94, "oculos": True},
    "zeca": {"nome": "Seu Zeca", "cabelo": "careca", "cor_cabelo": "contorno", "roupa": "claro", "calca": "apoio", "escala": 1.0, "bigode": True},
}
# Ângulos em graus: f = braço da frente, t = braço de trás, c* = cotovelos, q* = quadris, cab = cabeça, tr = tronco, y = descida do corpo.
POSES = {
    "neutra": {"f": 12, "cf": 8, "t": 12, "ct": 8},
    "aponta": {"f": 96, "cf": 4, "t": 12, "ct": 10, "cab": 5, "tr": 3},
    "bracos_cima": {"f": 152, "cf": 14, "t": 152, "ct": 14, "cab": -3, "y": -10},
    "pensando": {"f": 42, "cf": 128, "t": 18, "ct": 6, "cab": -8},
    "ombros": {"f": 62, "cf": 72, "t": 62, "ct": 72, "cab": 7},
    "triste": {"f": 4, "cf": 0, "t": 4, "ct": 0, "cab": 13, "tr": 5, "y": 10},
    "comemora": {"f": 158, "cf": 10, "t": 58, "ct": 94, "cab": -5, "y": -14},
    "maos_cintura": {"f": 52, "cf": -104, "t": 52, "ct": -104},
    "segura": {"f": 58, "cf": 74, "t": 14, "ct": 8, "cab": 7},
    "medo": {"f": 112, "cf": 102, "t": 112, "ct": 102, "cab": 4, "tr": -3, "y": 6},
    "caminha": {"f": 14, "cf": 26, "t": 14, "ct": 26, "tr": 3},
}
EXPRESSOES = {
    "neutra": {"olho": "normal", "boca": "reta", "sob": 0, "sob_y": 0},
    "feliz": {"olho": "normal", "boca": "sorriso", "sob": -8, "sob_y": -4},
    "risada": {"olho": "alegre", "boca": "risada", "sob": -12, "sob_y": -8},
    "surpresa": {"olho": "arregalado", "boca": "aberta", "sob": -16, "sob_y": -20},
    "triste": {"olho": "caido", "boca": "triste", "sob": 20, "sob_y": -4},
    "brava": {"olho": "caido", "boca": "dentes", "sob": -26, "sob_y": 10},
    "pensativa": {"olho": "normal", "boca": "lado", "sob": 10, "sob_y": -10, "olhar": (-6, -9)},
    "medo": {"olho": "arregalado", "boca": "dentes", "sob": 22, "sob_y": -18},
}
OBJETOS = ("celular", "nota", "moeda", "casa", "relogio", "coracao", "calendario", "grafico", "caixa", "lampada", "predio", "seta", "exclamacao", "interrogacao", "estrela", "raio", "suor")
CENARIOS = ("rua", "sala", "quarto", "escritorio", "escola", "cidade", "liso", "explosao")
ENTRADAS = ("corte", "pop", "salto", "queda", "deslize")
TRANS_ENTRADA = ("corte", "chicote", "zoom", "continua")
TRANS_SAIDA = ("corte", "chicote", "zoom", "continua", "loop")
DUR_TRANS = 0.24
DUR_LOOP = 0.5


def _cor(paleta, papel):
    return PALETAS[paleta][papel]


# ---------- personagem ----------
def _capsula(x0, y0, x1, y1, larg, cheio, contorno, seed, w=7):
    def fn(d, f, esc):
        a = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(a) * larg / 2, math.cos(a) * larg / 2
        pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny)]
        pts += [(x1 + larg / 2 * math.cos(a + math.pi / 2 - math.pi * k / 6), y1 + larg / 2 * math.sin(a + math.pi / 2 - math.pi * k / 6)) for k in range(1, 6)]
        pts += [(x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
        pts += [(x0 - larg / 2 * math.cos(a + math.pi / 2 - math.pi * k / 6), y0 - larg / 2 * math.sin(a + math.pi / 2 - math.pi * k / 6)) for k in range(1, 6)]
        forma(d, f, esc, pts, cheio, contorno, w, seed, 1.0)
    m = larg + 16
    return desenhar(min(x0, x1) - m, min(y0, y1) - m, max(x0, x1) + m, max(y0, y1) + m, fn)


@lru_cache(maxsize=None)
def _partes(ident, paleta):
    e = ELENCO[ident]
    c = lambda p: _cor(paleta, p)
    base = sum(ord(x) for x in ident)
    roupa, calca, pele, cont, claro = c(e["roupa"]), c(e["calca"]), c("pele"), c("contorno"), c("claro")
    p = {}

    def tronco(d, f, esc):
        forma(d, f, esc, [(-74, -178), (74, -178), (88, -70), (80, 6), (-80, 6), (-88, -70)], roupa, cont, 8, base + 1, 1.4)
        if e["roupa"] == "claro":
            forma(d, f, esc, [(0, -176), (0, 0)], None, cont, 4, base + 2, 1.0, fechado=False)
    p["tronco"] = desenhar(-110, -200, 110, 26, tronco)
    p["braco_f"] = _capsula(0, 0, 0, 96, 44, roupa, cont, base + 3)
    p["braco_t"] = _capsula(0, 0, 0, 96, 44, roupa, cont, base + 4)

    def ante(d, f, esc):
        forma(d, f, esc, retangulo(-17, -6, 17, 86), pele, cont, 7, base + 5, 1.0, curva=False)
        forma(d, f, esc, circulo(0, 98, 27), pele, cont, 7, base + 6, 1.0)
    p["ante"] = desenhar(-44, -26, 44, 140, ante)

    def perna(d, f, esc):
        forma(d, f, esc, retangulo(-30, -6, 30, 128), calca, cont, 8, base + 7, 1.2, curva=False)
        forma(d, f, esc, [(-34, 124), (34, 124), (62, 146), (58, 166), (-34, 166)], c("claro") if e["calca"] != "claro" else c("destaque"), cont, 8, base + 8, 1.0)
    p["perna"] = desenhar(-56, -24, 86, 186, perna)

    def cabeca(d, f, esc):
        if e["cabelo"] == "chanel":
            forma(d, f, esc, [(-136, -30), (-112, -112), (-30, -146), (56, -138), (124, -82), (136, 10), (118, 86), (-118, 86), (-140, 40)], c(e["cor_cabelo"]), cont, 8, base + 10, 1.5)
        if e["cabelo"] == "coque":
            forma(d, f, esc, circulo(-6, -158, 48), c(e["cor_cabelo"]), cont, 8, base + 10, 1.4)
        forma(d, f, esc, circulo(0, 0, 120, 116, 16), pele, cont, 9, base + 11, 1.6)
        forma(d, f, esc, circulo(126, 8, 18, 24, 10), pele, cont, 7, base + 12, 0.8)
        if e["cabelo"] == "chanel":
            forma(d, f, esc, [(-124, -18), (-96, -96), (-20, -124), (64, -116), (116, -56), (52, -74), (-30, -66), (-88, -24)], c(e["cor_cabelo"]), cont, 7, base + 13, 1.2)
        elif e["cabelo"] == "topete":
            forma(d, f, esc, [(-110, -44), (-90, -118), (-20, -154), (70, -170), (128, -112), (96, -86), (24, -86), (-58, -66)], c(e["cor_cabelo"]), cont, 8, base + 13, 1.6)
        elif e["cabelo"] == "coque":
            forma(d, f, esc, [(-118, -28), (-92, -96), (-14, -122), (72, -110), (118, -38), (52, -74), (-44, -78)], c(e["cor_cabelo"]), cont, 7, base + 13, 1.2)
        elif e["cabelo"] == "careca":
            forma(d, f, esc, [(-122, -6), (-112, -44), (-92, -30), (-94, 18)], cont, cont, 4, base + 13, 0.8)
    p["cabeca"] = desenhar(-170, -220, 170, 150, cabeca)

    for nome, rx, ry in (("normal", 31, 37), ("arregalado", 40, 47), ("caido", 31, 25)):
        def olho(d, f, esc, rx=rx, ry=ry, nome=nome):
            forma(d, f, esc, circulo(0, 0, rx, ry, 12), claro, cont, 6, base + 20, 0.7)
            if nome == "caido":
                forma(d, f, esc, [(-rx - 3, -ry - 2), (rx + 3, -ry - 2), (rx + 3, -5), (-rx - 3, -5)], pele, cont, 5, base + 21, 0.5, curva=False)
        p["olho_" + nome] = desenhar(-58, -62, 58, 62, olho)
    p["pupila"] = desenhar(-24, -24, 24, 24, lambda d, f, esc: forma(d, f, esc, circulo(0, 0, 15, n=20), cont, None, amp=0.15))
    p["olho_fechado"] = desenhar(-50, -30, 50, 30, lambda d, f, esc: forma(d, f, esc, [(-32, -2), (0, 10), (32, -2)], None, cont, 7, base + 22, 0.5, fechado=False))
    p["olho_alegre"] = desenhar(-50, -30, 50, 30, lambda d, f, esc: forma(d, f, esc, [(-32, 10), (0, -14), (32, 10)], None, cont, 8, base + 23, 0.5, fechado=False))
    p["sobrancelha"] = desenhar(-50, -20, 50, 20, lambda d, f, esc: forma(d, f, esc, [(-34, 2), (0, -6), (34, 2)], None, cont, 11, base + 24, 0.5, fechado=False))

    bocas = {
        "reta": lambda d, f, esc: forma(d, f, esc, [(-36, 0), (36, 2)], None, cont, 8, base + 30, 0.5, fechado=False, curva=False),
        "sorriso": lambda d, f, esc: forma(d, f, esc, [(-46, -12), (-22, 12), (22, 12), (46, -12)], None, cont, 8, base + 31, 0.5, fechado=False),
        "triste": lambda d, f, esc: forma(d, f, esc, [(-40, 14), (-16, -8), (16, -8), (40, 14)], None, cont, 8, base + 32, 0.5, fechado=False),
        "lado": lambda d, f, esc: forma(d, f, esc, [(-30, 6), (6, 6), (40, -10)], None, cont, 8, base + 33, 0.5, fechado=False),
        "aberta": lambda d, f, esc: forma(d, f, esc, circulo(0, 4, 26, 30, 14), c("destaque") if e["roupa"] != "destaque" else cont, cont, 7, base + 34, 0.4),
        "risada": lambda d, f, esc: (forma(d, f, esc, [(-58, -22), (58, -22), (40, 34), (0, 52), (-40, 34)], c("destaque") if e["roupa"] != "destaque" else cont, cont, 8, base + 35, 0.7), forma(d, f, esc, [(-48, -20), (48, -20), (42, -4), (-42, -4)], claro, None, 0, base + 36, 0.3, curva=False)),
        "dentes": lambda d, f, esc: (forma(d, f, esc, retangulo(-48, -22, 48, 24), claro, cont, 8, base + 37, 0.7, curva=False), forma(d, f, esc, [(-48, 1), (48, 1)], None, cont, 5, base + 38, 0.3, fechado=False, curva=False), [forma(d, f, esc, [(x, -22), (x, 24)], None, cont, 4, base + 39 + x, 0.2, fechado=False, curva=False) for x in (-18, 18)]),
    }
    for nome, fn in bocas.items():
        p["boca_" + nome] = desenhar(-76, -60, 76, 70, fn)
    if e.get("oculos"):
        def oculos(d, f, esc):
            for x in (-46, 54):
                forma(d, f, esc, circulo(x, 0, 48, 50, 14), None, cont, 7, base + 40 + x, 0.5)
            forma(d, f, esc, [(2, -4), (8, -4)], None, cont, 7, base + 44, 0.2, fechado=False, curva=False)
        p["oculos"] = desenhar(-110, -66, 118, 66, oculos)
    if e.get("bigode"):
        p["bigode"] = desenhar(-90, -36, 90, 40, lambda d, f, esc: forma(d, f, esc, [(0, -12), (42, -18), (72, 14), (34, 18), (0, 4), (-34, 18), (-72, 14), (-42, -18)], cont, cont, 3, base + 45, 0.5))
    return p


def _pose_em(poses, lt):
    """Mistura as poses com um golpe curto e leve exagero; devolve (ângulos, expressão, tempo desde a última mudança)."""
    atual = poses[0]
    anterior = None
    for k in poses[1:]:
        if lt >= k.get("t", 0):
            anterior, atual = atual, k
    alvo = POSES[atual["pose"]]
    desde = lt - atual.get("t", 0)
    if anterior is None or desde >= 0.32:
        return dict(alvo), atual["expressao"], desde if anterior else 9.0, atual["pose"]
    e = mola(desde / 0.32)
    base = POSES[anterior["pose"]]
    return {k: base.get(k, 0) + (alvo.get(k, 0) - base.get(k, 0)) * e for k in set(base) | set(alvo)}, atual["expressao"], desde, atual["pose"]


def _piscando(ident, lt):
    fase = (sum(ord(x) for x in ident) * 0.37) % 2.2
    ciclo = (lt + fase) % 3.1
    return ciclo < 0.11 or 1.3 < ciclo < 1.38 and sum(ord(x) for x in ident) % 2 == 0


def desenhar_personagem(quadro, m_camera, spec, lt, paleta, itens_em_mao=None):
    """Compõe o personagem por camadas. Devolve o ponto da mão da frente e o centro da cabeça, na tela."""
    ident = spec["id"]
    e = ELENCO[ident]
    p = _partes(ident, paleta)
    t0 = spec.get("t", 0)
    if lt < t0:
        return None
    dx, dy, sx_e, sy_e, _ = entrada(spec.get("entrada", "corte"), lt, t0, 0.55, 1 if spec.get("x", 540) > W / 2 else -1)
    ang, expr, desde, pose = _pose_em(spec["poses"], lt)
    fase = sum(ord(x) for x in ident) * 0.9
    respira = math.sin(lt * 2.3 + fase)
    batida = (1 - clamp(desde / 0.22)) if desde < 0.22 else 0.0  # o corpo reage à troca de pose: squash curto
    sx = sx_e * (1 + 0.028 * batida) * (1 + 0.006 * respira)
    sy = sy_e * (1 - 0.04 * batida) * (1 - 0.006 * respira + 0.012 * respira)
    espelho = -1 if spec.get("olha", "dir") == "esq" else 1
    esc = spec.get("escala", 1.0) * e["escala"]
    raiz = compor(m_camera, mover(spec.get("x", 540) + dx, spec.get("y", CHAO) + dy), escalar(esc * espelho * sx, esc * sy))
    balanco = math.sin(lt * 8.2 + fase) if pose == "caminha" else 0.0
    quadril_y = -128 + ang.get("y", 0) + abs(balanco) * -8
    for lado, ang_q in ((-34, -24 * balanco), (34, 24 * balanco)):
        p["perna"].colar(quadro, compor(raiz, mover(lado, quadril_y), girar(ang_q)))
    corpo = compor(raiz, mover(0, quadril_y), girar(ang.get("tr", 0) + 1.2 * respira), escalar(1, 1 + 0.018 * respira))
    braco_y = -162
    balanco_braco = 30 * balanco
    m_t = compor(corpo, mover(-74, braco_y), girar(ang.get("t", 0) + balanco_braco + 2 * respira))
    p["ante"].colar(quadro, compor(m_t, mover(0, 96), girar(ang.get("ct", 0))))
    p["braco_t"].colar(quadro, m_t)
    p["tronco"].colar(quadro, corpo)
    # cabeça, com olhos, sobrancelhas e boca em sprites próprios
    pop_expr = 1 + 0.07 * (1 - clamp(desde / 0.2)) if desde < 0.2 else 1.0
    cab = compor(corpo, mover(0, -270), girar(ang.get("cab", 0) + 1.8 * math.sin(lt * 1.7 + fase)), escalar(pop_expr))
    p["cabeca"].colar(quadro, cab)
    ex = EXPRESSOES[expr]
    olhar = ex.get("olhar", (9, 2))
    for lado in (-46, 54):
        pos = compor(cab, mover(lado, -6))
        if _piscando(ident, lt):
            p["olho_fechado"].colar(quadro, pos)
        elif ex["olho"] == "alegre":
            p["olho_alegre"].colar(quadro, pos)
        else:
            p["olho_" + ex["olho"]].colar(quadro, pos)
            p["pupila"].colar(quadro, compor(pos, mover(olhar[0], olhar[1] + (9 if ex["olho"] == "caido" else 0))))
        lado_sob = -1 if lado < 0 else 1
        p["sobrancelha"].colar(quadro, compor(cab, mover(lado, -68 + ex["sob_y"]), girar(ex["sob"] * lado_sob)))
    if "oculos" in p:
        p["oculos"].colar(quadro, compor(cab, mover(0, -6)))
    boca = ex["boca"]
    if spec.get("fala") and int(lt * 7.5) % 2 == 1 and boca in ("reta", "sorriso", "triste", "lado"):
        boca = "aberta"
    p["boca_" + boca].colar(quadro, compor(cab, mover(8, 74)))
    if "bigode" in p:
        p["bigode"].colar(quadro, compor(cab, mover(8, 44)))
    m_f = compor(corpo, mover(74, braco_y), girar(-(ang.get("f", 0) + balanco_braco * -1 + 2 * respira)))
    ante_m = compor(m_f, mover(0, 96), girar(-ang.get("cf", 0)))
    p["ante"].colar(quadro, ante_m)
    p["braco_f"].colar(quadro, m_f)
    segurado = spec.get("segura")
    if segurado:
        mao = aplicar(ante_m, 0, 98)
        sp = _objeto_sprite(segurado["tipo"], paleta, segurado.get("texto"))
        sp.colar(quadro, compor(mover(*mao), mover(espelho * 40 * esc, -40 * esc), escalar(segurado.get("escala", 1.0) * esc), girar(-6 * espelho)))
    return aplicar(cab, 0, -150)


# ---------- objetos, símbolos e balões ----------
@lru_cache(maxsize=None)
def _objeto_sprite(tipo, paleta, texto=None):
    c = lambda p: _cor(paleta, p)
    cont, claro, dest, apoio, fundo = c("contorno"), c("claro"), c("destaque"), c("apoio"), c("fundo")
    seed = sum(ord(x) for x in tipo)
    if tipo == "celular":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-96, -180, 96, 180), cont, cont, 8, seed, 1, curva=False)
            forma(d, f, esc, retangulo(-78, -150, 78, 138), claro, None, 0, seed + 1, 0.4, curva=False)
            forma(d, f, esc, retangulo(-78, -150, 78, -112), apoio, None, 0, seed + 2, 0.2, curva=False)
            forma(d, f, esc, circulo(0, 158, 11), claro)
        s = desenhar(-120, -204, 120, 204, fn)
        if texto:
            s = _com_texto(s, _quebrar_tela(texto, 30, 146), (0, -6), 30, cont)
        return s
    if tipo == "nota":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-150, -76, 150, 76), apoio, cont, 8, seed, 1.4, curva=False)
            forma(d, f, esc, circulo(0, 0, 50, 50), claro, cont, 6, seed + 1, 0.8)
        return _com_texto(desenhar(-172, -98, 172, 98, fn), [texto or "R$"], (0, 0), 46, cont)
    if tipo == "moeda":
        fn = lambda d, f, esc: (forma(d, f, esc, circulo(0, 0, 90), dest, cont, 9, seed, 1.2), forma(d, f, esc, circulo(0, 0, 66), None, cont, 5, seed + 1, 0.8))
        return _com_texto(desenhar(-112, -112, 112, 112, fn), [texto or "R$"], (0, 0), 56, claro)
    if tipo == "casa":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-130, -60, 130, 150), claro, cont, 9, seed, 1.5, curva=False)
            forma(d, f, esc, [(-170, -50), (0, -190), (170, -50)], dest, cont, 9, seed + 1, 1.5, curva=False)
            forma(d, f, esc, retangulo(-34, 40, 34, 150), apoio, cont, 7, seed + 2, 0.8, curva=False)
        return desenhar(-192, -214, 192, 172, fn)
    if tipo == "relogio":
        def fn(d, f, esc):
            forma(d, f, esc, circulo(0, 0, 120), claro, cont, 10, seed, 1.2)
            for k in range(12):
                a = math.tau * k / 12
                forma(d, f, esc, [(92 * math.cos(a), 92 * math.sin(a)), (106 * math.cos(a), 106 * math.sin(a))], None, cont, 6, seed + k, 0.1, fechado=False, curva=False)
        return desenhar(-142, -142, 142, 142, fn)
    if tipo == "ponteiro":
        return desenhar(-16, -100, 16, 16, lambda d, f, esc: forma(d, f, esc, [(0, 6), (0, -86)], None, dest, 11, 3, 0.2, fechado=False, curva=False))
    if tipo == "coracao":
        pts = [(5.8 * 16 * math.sin(math.tau * k / 24) ** 3, -5.8 * (13 * math.cos(math.tau * k / 24) - 5 * math.cos(2 * math.tau * k / 24) - 2 * math.cos(3 * math.tau * k / 24) - math.cos(4 * math.tau * k / 24))) for k in range(24)]
        return desenhar(-120, -110, 120, 120, lambda d, f, esc: forma(d, f, esc, pts, dest, cont, 9, seed, 1.2))
    if tipo == "calendario":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-140, -120, 140, 130), claro, cont, 9, seed, 1.2, curva=False)
            forma(d, f, esc, retangulo(-140, -120, 140, -52), dest, cont, 9, seed + 1, 1.0, curva=False)
        return _com_texto(desenhar(-162, -142, 162, 152, fn), [texto or ""], (0, 40), 90, cont)
    if tipo == "caixa":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-130, -80, 130, 120), fundo if fundo != claro else apoio, cont, 9, seed, 1.5, curva=False)
            forma(d, f, esc, retangulo(-150, -120, 150, -60), apoio, cont, 9, seed + 1, 1.3, curva=False)
        return desenhar(-172, -142, 172, 142, fn)
    if tipo == "lampada":
        def fn(d, f, esc):
            forma(d, f, esc, circulo(0, -40, 90), claro, cont, 9, seed, 1.0)
            forma(d, f, esc, retangulo(-38, 50, 38, 104), apoio, cont, 8, seed + 1, 0.7, curva=False)
        return desenhar(-112, -152, 112, 126, fn)
    if tipo == "predio":
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-120, -320, 120, 320), apoio, cont, 9, seed, 1.5, curva=False)
            for lin in range(5):
                for col in (-58, 58):
                    forma(d, f, esc, retangulo(col - 30, -270 + lin * 110, col + 30, -200 + lin * 110), claro, cont, 5, seed + lin + col, 0.5, curva=False)
        return desenhar(-142, -342, 142, 342, fn)
    if tipo == "seta":
        return desenhar(-170, -90, 170, 90, lambda d, f, esc: forma(d, f, esc, [(-150, -30), (40, -30), (40, -74), (150, 0), (40, 74), (40, 30), (-150, 30)], dest, cont, 9, seed, 1.0, curva=False))
    if tipo == "exclamacao":
        fn = lambda d, f, esc: (forma(d, f, esc, [(-34, -130), (34, -130), (18, 40), (-18, 40)], dest, cont, 8, seed, 1.0, curva=False), forma(d, f, esc, circulo(0, 96, 28), dest, cont, 8, seed + 1, 0.6))
        return desenhar(-56, -150, 56, 142, fn)
    if tipo == "interrogacao":
        return texto_sprite("?", "impacto", 260, dest, cont, 8)
    if tipo == "estrela":
        pts = [((160 if k % 2 == 0 else 78) * math.cos(math.tau * k / 16), (160 if k % 2 == 0 else 78) * math.sin(math.tau * k / 16)) for k in range(16)]
        return desenhar(-182, -182, 182, 182, lambda d, f, esc: forma(d, f, esc, pts, claro, cont, 9, seed, 1.0, curva=False))
    if tipo == "raio":
        return desenhar(-90, -170, 90, 170, lambda d, f, esc: forma(d, f, esc, [(20, -150), (-62, 16), (-6, 16), (-34, 150), (66, -30), (8, -30)], dest, cont, 8, seed, 0.8, curva=False))
    if tipo == "suor":
        return desenhar(-34, -56, 34, 44, lambda d, f, esc: forma(d, f, esc, [(0, -46), (22, 2), (0, 28), (-22, 2)], apoio, cont, 5, seed, 0.3))
    raise ValueError(f"objeto desconhecido: {tipo}")


def _quebrar_tela(texto_, tam, larg):
    fo = fonte("pesada", tam)
    linhas, atual = [], ""
    for p in texto_.split():
        tentativa = f"{atual} {p}".strip()
        if fo.getlength(tentativa) > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = tentativa
    return linhas + ([atual] if atual else [])


def _com_texto(s, linhas, centro, tam, cor):
    from PIL import ImageDraw
    im = s.im.copy()
    d = ImageDraw.Draw(im)
    linhas = [x for x in linhas if x]
    fo = fonte("pesada", tam * DENS)
    cx, cy = s.ox + centro[0] * DENS, s.oy + centro[1] * DENS
    passo = tam * DENS * 1.2
    for i, x in enumerate(linhas):
        d.text((cx, cy + (i - (len(linhas) - 1) / 2) * passo), x, font=fo, fill=cor, anchor="mm")
    return Sprite(im, s.ox, s.oy, s.dens)


@lru_cache(maxsize=256)
def _balao_sprite(linhas, paleta, cauda):
    cont, claro = _cor(paleta, "contorno"), _cor(paleta, "claro")
    fo = fonte("pesada", 50 * DENS)
    larg = max(fo.getlength(x) for x in linhas) / DENS + 90
    alt = 66 * len(linhas) + 66

    def fn(d, f, esc):
        x, y = larg / 2, alt / 2
        forma(d, f, esc, [(-x, -y), (x, -y), (x, y), (-x, y)], claro, cont, 8, 21, 1.5)
        tx = -x * 0.35 * cauda
        forma(d, f, esc, [(tx - 34, y - 6), (tx + 30 * cauda, y + 66), (tx + 34, y - 6)], claro, None, 0, 22, 0.5, curva=False)
        forma(d, f, esc, [(tx - 34, y + 1), (tx + 30 * cauda, y + 66), (tx + 34, y + 1)], None, cont, 8, 23, 0.5, fechado=False, curva=False)
    s = desenhar(-larg / 2 - 30, -alt / 2 - 30, larg / 2 + 30, alt / 2 + 90, fn)
    return _com_texto(s, list(linhas), (0, 0), 50, cont)


# ---------- cenários: cada elemento tem seu parallax ----------
@lru_cache(maxsize=None)
def _ceu(paleta, tom):
    return Sprite(Image.new("RGB", (int((W + 800) * 0.5), int((H + 800) * 0.5)), _cor(paleta, tom)), (W + 800) * 0.25 + -W * 0.25, (H + 800) * 0.25 - H * 0.25, 0.5)


@lru_cache(maxsize=None)
def _chao_sprite(paleta, cor):
    c = _cor(paleta, cor)
    cont = _cor(paleta, "contorno")

    def fn(d, f, esc):
        forma(d, f, esc, [(-500, 0), (W + 500, 0), (W + 500, 900), (-500, 900)], c, None, curva=False)
        forma(d, f, esc, [(-500, 0), (W + 500, 0)], None, cont, 9, 5, 2.5, fechado=False, curva=False)
    return desenhar(-500, -12, W + 500, 700, fn, dens=0.75)


@lru_cache(maxsize=None)
def _cenario(nome, paleta):
    """Lista de (parallax, sprite, x, y, gira), do mais distante ao mais próximo."""
    c = lambda p: _cor(paleta, p)
    cont, claro, dest, apoio, fundo = c("contorno"), c("claro"), c("destaque"), c("apoio"), c("fundo")
    cam = []

    def bloco(px, x, y, fn, caixa):
        cam.append((px, desenhar(*caixa, fn, dens=1.0), x, y))

    def nuvem(d, f, esc):
        forma(d, f, esc, [(-120, 30), (-90, -24), (-20, -46), (60, -34), (120, 0), (90, 40)], claro, cont, 7, 31, 1.5)

    def predio_fundo(larg, alt, cor, seed):
        def fn(d, f, esc):
            forma(d, f, esc, retangulo(-larg / 2, 0, larg / 2, alt), cor, cont, 8, seed, 1.5, curva=False)
            for lin in range(int(alt // 120)):
                for col in (-1, 1):
                    forma(d, f, esc, retangulo(col * larg / 4 - 22, 40 + lin * 120, col * larg / 4 + 22, 100 + lin * 120), fundo if cor != fundo else claro, cont, 5, seed + lin * 3 + col, 0.5, curva=False)
        return fn

    if nome in ("rua", "cidade"):
        bloco(0.18, 240, 330, nuvem, (-140, -60, 140, 60))
        bloco(0.26, 820, 470, nuvem, (-140, -60, 140, 60))
        for k, (x, larg, alt, cor) in enumerate(((60, 280, 760, apoio), (360, 240, 960, claro), (690, 300, 680, dest), (1020, 260, 900, apoio))):
            y = CHAO - alt
            bloco(0.5 if nome == "rua" else 0.38, x, y, predio_fundo(larg, alt, cor, 40 + k), (-larg / 2 - 12, -12, larg / 2 + 12, alt + 12))
        if nome == "rua":
            def poste(d, f, esc):
                forma(d, f, esc, [(0, 0), (0, 680), (0, 680)], None, cont, 14, 50, 0.5, fechado=False, curva=False)
                forma(d, f, esc, circulo(0, -20, 34), claro, cont, 8, 51, 0.6)
            bloco(0.82, 940, CHAO - 660, poste, (-50, -66, 50, 700))
        return cam, (apoio if nome == "cidade" else claro)
    if nome == "sala":
        def janela(d, f, esc):
            forma(d, f, esc, retangulo(-170, -220, 170, 220), apoio, cont, 10, 60, 1.5, curva=False)
            forma(d, f, esc, [(0, -220), (0, 220)], None, cont, 8, 61, 0.8, fechado=False, curva=False)
            forma(d, f, esc, [(-170, 0), (170, 0)], None, cont, 8, 62, 0.8, fechado=False, curva=False)
        bloco(0.45, 280, 660, janela, (-190, -240, 190, 240))

        def quadro_(d, f, esc):
            forma(d, f, esc, retangulo(-110, -140, 110, 140), claro, cont, 9, 63, 1.2, curva=False)
            forma(d, f, esc, circulo(0, 0, 60), dest, cont, 7, 64, 1.0)
        bloco(0.6, 800, 560, quadro_, (-130, -160, 130, 160))

        def sofa(d, f, esc):
            forma(d, f, esc, retangulo(-340, -170, 340, 40), dest, cont, 10, 65, 2, curva=False)
            forma(d, f, esc, retangulo(-390, -60, 390, 120), dest, cont, 10, 66, 2, curva=False)
        bloco(0.8, 700, CHAO - 120, sofa, (-410, -190, 410, 140))
        return cam, claro
    if nome == "quarto":
        def cama(d, f, esc):
            forma(d, f, esc, retangulo(-320, -180, -270, 150), cont, cont, 4, 70, 0.8, curva=False)
            forma(d, f, esc, retangulo(-290, -30, 340, 120), claro, cont, 10, 71, 2, curva=False)
            forma(d, f, esc, retangulo(-280, -74, -110, 0), apoio, cont, 8, 72, 1.3)
        bloco(0.82, 650, CHAO - 130, cama, (-340, -200, 360, 170))

        def janela(d, f, esc):
            forma(d, f, esc, retangulo(-150, -180, 150, 180), apoio, cont, 10, 73, 1.5, curva=False)
            forma(d, f, esc, circulo(60, -70, 44), claro, cont, 7, 74, 0.8)
        bloco(0.42, 300, 620, janela, (-170, -200, 170, 200))
        return cam, dest
    if nome == "escritorio":
        def tela(d, f, esc):
            forma(d, f, esc, retangulo(-280, -190, 280, 190), apoio, cont, 10, 80, 1.4, curva=False)
            for k in range(3):
                forma(d, f, esc, retangulo(-220, -120 + k * 90, 40 + k * 60, -70 + k * 90), claro, None, 0, 81 + k, 0.8, curva=False)
        bloco(0.4, 420, 560, tela, (-300, -210, 300, 210))

        def mesa(d, f, esc):
            forma(d, f, esc, retangulo(-430, -14, 430, 34), dest, cont, 10, 85, 1.5, curva=False)
            for x in (-370, 370):
                forma(d, f, esc, [(x, 34), (x, 300)], None, cont, 18, 86 + x, 0.5, fechado=False, curva=False)
        bloco(0.82, 640, CHAO - 280, mesa, (-450, -34, 450, 320))
        return cam, claro
    if nome == "escola":
        def lousa(d, f, esc):
            forma(d, f, esc, retangulo(-400, -230, 400, 230), cont, apoio, 14, 90, 1.5, curva=False)
            for k in range(3):
                forma(d, f, esc, [(-320, -120 + k * 110), (-40 + k * 90, -130 + k * 110)], None, claro, 7, 91 + k, 2, fechado=False)
        bloco(0.45, 540, 620, lousa, (-420, -250, 420, 250))
        return cam, apoio
    if nome == "liso":
        def faixa(d, f, esc):
            forma(d, f, esc, [(-900, -70), (900, -110), (900, 110), (-900, 70)], claro, None, curva=False)
        bloco(0.3, 540, 560, faixa, (-900, -120, 900, 120))
        return cam, apoio
    if nome == "explosao":
        return cam, cont
    raise ValueError(f"cenário desconhecido: {nome}")


@lru_cache(maxsize=None)
def _raios(paleta):
    claro = _cor(paleta, "claro")

    def fn(d, f, esc):
        for k in range(14):
            a0, a1 = math.tau * k / 14, math.tau * (k + 0.5) / 14
            forma(d, f, esc, [(0, 0), (1700 * math.cos(a0), 1700 * math.sin(a0)), (1700 * math.cos(a1), 1700 * math.sin(a1))], claro, None, curva=False)
    return desenhar(-1500, -1500, 1500, 1500, fn, dens=0.4)


# ---------- quadro ----------
def _camera(cena, lt, dur):
    c = cena.get("camera") or {}
    base = {"x": W / 2, "y": H / 2, "zoom": 1.0, "rot": 0.0}
    v = chave_em(c.get("chaves"), lt, base)
    if not c.get("chaves"):  # sem câmera definida, deriva pouco: é o que mostra o parallax entre as camadas
        lado = -1 if cena.get("desenho", "cena_0")[-1] in "13579" else 1
        v["x"] += lado * (lt / max(dur, 0.1) - 0.5) * 70
        v["zoom"] = 1.0 + 0.035 * lt / max(dur, 0.1)
    dx, dy = tremida(c.get("tremidas"), lt)
    t = cena.get("transicao") or {}
    if t.get("entrada") == "zoom" and lt < DUR_TRANS * 1.6:
        v["zoom"] *= 1 + 0.65 * (1 - saida_rapida(lt / (DUR_TRANS * 1.6)))
    if t.get("saida") == "zoom" and lt > dur - DUR_TRANS:
        v["zoom"] *= 1 + 0.9 * suave((lt - (dur - DUR_TRANS)) / DUR_TRANS) ** 2
    if t.get("entrada") == "continua" and lt < 0.6:
        v["x"] += 170 * (1 - saida_rapida(lt / 0.6))
    if t.get("saida") == "continua" and lt > dur - 0.6:
        v["x"] -= 170 * suave((lt - (dur - 0.6)) / 0.6) ** 2
    return Camera(v["x"], v["y"], v["zoom"], v["rot"], dx, dy)


def _nasce(el, lt, abertura, chave="entrada", dur=0.45, lado=1):
    """Na primeira cena o que entra em t=0 já está na tela no quadro 0: o gancho não começa vazio."""
    t0 = el.get("t", 0)
    if abertura and t0 <= 0:
        return (0.0, 0.0, 1.0, 1.0, 1.0)
    return entrada(el.get(chave, "pop"), lt, t0, dur, lado)


def compor_cena(cena, lt, dur, abertura=False, paleta=None):
    paleta = paleta or cena.get("paleta", "sol")
    quadro = Image.new("RGBA", (W, H), _cor(paleta, "fundo"))
    cam = _camera(cena, lt, dur)
    nome = cena.get("cenario", "liso")
    elementos, cor_chao = _cenario(nome, paleta)
    if nome == "explosao":
        _raios(paleta).colar(quadro, compor(cam.matriz(0.25), mover(W / 2, H * 0.4), girar(lt * 14)), filtro=Image.BILINEAR)
    for p, s, x, y in elementos:
        s.colar(quadro, compor(cam.matriz(p), mover(x, y)), filtro=Image.BILINEAR)
    if nome != "explosao":
        _chao_sprite(paleta, _papel_de(paleta, cor_chao)).colar(quadro, compor(cam.matriz(0.92), mover(0, CHAO)), filtro=Image.BILINEAR)
    m = cam.matriz(1.0)
    atras = [o for o in cena.get("objetos", ()) if o.get("atras")]
    for o in atras:
        _colar_objeto(quadro, m, o, lt, paleta, abertura)
    cabecas = {}
    for sp in cena.get("personagens", ()):
        s_ = _sem_entrada(sp) if abertura and sp.get("t", 0) <= 0 else sp
        topo = desenhar_personagem(quadro, m, s_, lt, paleta)
        if topo:
            cabecas[sp["id"]] = (sp, topo)
    for o in cena.get("objetos", ()):
        if not o.get("atras"):
            _colar_objeto(quadro, m, o, lt, paleta, abertura)
    for b in cena.get("baloes", ()):
        if lt < b.get("t", 0) or ("ate" in b and lt > b["ate"]):
            continue
        origem = cabecas.get(b.get("de"))
        cauda = -1 if origem and origem[0].get("x", 540) > W / 2 else 1
        s = _balao_sprite(tuple(b["linhas"]), paleta, cauda)
        x = b.get("x", (origem[0].get("x", 540) + cauda * 130) if origem else 540)
        y = b.get("y", (origem[1][1] - 150) if origem else 500)
        _, _, sx, sy, _ = entrada("pop", lt, b.get("t", 0), 0.28)
        s.colar(quadro, compor(m, mover(x, y), escalar(sx, sy)) if not origem or "y" in b else compor(mover(x, y), escalar(sx, sy)))
    for t_ in cena.get("textos", ()):
        if "ate" in t_ and lt > t_["ate"]:
            continue
        dx, dy, sx, sy, _ = _nasce(t_, lt, abertura, dur=0.32)
        if sx <= 0:
            continue
        cor = _cor(paleta, t_.get("cor", "claro"))
        s = texto_sprite(t_["texto"], "impacto", t_.get("tam", 110), cor, _cor(paleta, "contorno"), max(5, t_.get("tam", 110) * 0.075), _cor(paleta, "contorno"), max(5, t_.get("tam", 110) * 0.075))
        s.colar(quadro, compor(cam.matriz(0.16), mover(t_.get("x", 540) + dx, t_.get("y", 400) + dy), girar(t_.get("rot", 0)), escalar(sx * (1 + t_.get("pulsa", 0.0) * math.sin(lt * 5)), sy * (1 + t_.get("pulsa", 0.0) * math.sin(lt * 5)))))
    return quadro


def _papel_de(paleta, cor):
    for k, v in PALETAS[paleta].items():
        if v == cor:
            return k
    return "apoio"


def _sem_entrada(sp):
    return {**sp, "entrada": "corte"}


def _colar_objeto(quadro, m, o, lt, paleta, abertura):
    if "ate" in o and lt > o["ate"]:
        return
    dx, dy, sx, sy, _ = _nasce(o, lt, abertura, lado=1 if o.get("x", 540) > W / 2 else -1)
    if sx <= 0:
        return
    esc = o.get("escala", 1.0)
    respira = 1 + 0.02 * math.sin(lt * 3.1 + o.get("x", 0) * 0.01)
    rot = o.get("rot", 0) + o.get("balanco", 2.0) * math.sin(lt * 2.4 + o.get("y", 0) * 0.01)
    mat = compor(m, mover(o.get("x", 540) + dx, o.get("y", 800) + dy), girar(rot), escalar(esc * sx * respira, esc * sy * respira))
    if o["tipo"] == "grafico":
        _grafico(quadro, mat, o, lt, paleta)
        return
    _objeto_sprite(o["tipo"], paleta, o.get("texto")).colar(quadro, mat)
    if o["tipo"] == "relogio":
        _objeto_sprite("ponteiro", paleta).colar(quadro, compor(mat, girar(lt * 150)))


def _grafico(quadro, mat, o, lt, paleta):
    """Barras crescem: cada uma é uma camada, ancorada na base."""
    barras = o.get("barras", [])
    if not barras:
        return
    maior = max(b["valor"] for b in barras) or 1
    passo = 170
    x0 = -(len(barras) - 1) * passo / 2
    for k, b in enumerate(barras):
        f = mola((lt - o.get("t", 0) - 0.15 * k) / 0.6)
        if f <= 0:
            continue
        s = _barra(paleta, ["destaque", "apoio", "claro"][k % 3])
        alt = 380 * b["valor"] / maior * f
        s.colar(quadro, compor(mat, mover(x0 + k * passo, 0), escalar(1, max(0.01, alt / 100))))
        texto_sprite(b.get("texto", str(b["valor"])), "impacto", 58, _cor(paleta, "claro"), _cor(paleta, "contorno"), 5).colar(quadro, compor(mat, mover(x0 + k * passo, -alt - 46)))
        if b.get("rotulo"):
            texto_sprite(b["rotulo"], "pesada", 36, _cor(paleta, "contorno")).colar(quadro, compor(mat, mover(x0 + k * passo, 42)))


@lru_cache(maxsize=None)
def _barra(paleta, papel):
    return desenhar(-66, -104, 66, 4, lambda d, f, esc: forma(d, f, esc, retangulo(-58, -100, 58, 0), _cor(paleta, papel), _cor(paleta, "contorno"), 7, 3, 0.6, curva=False))


def quadro(cena, lt, dur, ctx):
    """Um quadro da cena. `ctx`: lista de cenas e índice desta, para abertura e loop."""
    cenas, i = ctx["cenas"], ctx["i"]
    paleta = cenas[0].get("paleta", "sol")
    im = compor_cena(cena, lt, dur, abertura=i == 0, paleta=paleta)
    t = cena.get("transicao") or {}
    if t.get("saida") == "loop":
        janela = dur - DUR_LOOP
        if lt > janela:
            primeiro = compor_cena(cenas[0], 0.0, 99.0, abertura=True, paleta=paleta)
            return fechar_loop(im, primeiro, (lt - janela) / max(DUR_LOOP - ctx.get("meio", 1 / 15), 0.01))
    elif t.get("saida") == "chicote" and lt > dur - DUR_TRANS:
        im = _chicote(im, suave((lt - (dur - DUR_TRANS)) / DUR_TRANS) ** 2, -1, paleta)
    if t.get("entrada") == "chicote" and lt < DUR_TRANS and not (i == 0):
        im = _chicote(im, (1 - saida_rapida(lt / DUR_TRANS)), 1, paleta)
    return im


def _chicote(im, x, lado, paleta):
    """Giro rápido de câmera, sem depender da cena vizinha: o editor pode reordenar sem emenda quebrada."""
    desloc = int(x * W * 1.05) * lado
    fundo = Image.new("RGBA", (W, H), _cor(paleta, "contorno"))
    fundo.paste(im, (desloc, 0))
    if x > 0.02:
        rastro = Image.new("RGBA", (W, H), _cor(paleta, "contorno"))
        rastro.paste(im, (desloc - int(90 * x) * lado, 0))
        return Image.blend(fundo, rastro, 0.5)
    return fundo


# ---------- validação ----------
def _erro(onde, texto):
    raise ValueError(f"{onde}: {texto}")


def _na_lista(onde, campo, valor, lista):
    if valor not in lista:
        _erro(onde, f"{campo} '{valor}' não existe. Use: {', '.join(lista)}")


def validar(c, onde):
    """Erro aponta cena e campo. Cobre tudo que quebraria o desenho ou o contrato do canal."""
    if not isinstance(c.get("acao"), str) or not c["acao"].strip():
        _erro(onde, "falta a 'acao': a ação principal da cena, em uma frase")
    _na_lista(onde, "paleta", c.get("paleta", "sol"), tuple(PALETAS))
    _na_lista(onde, "cenario", c.get("cenario"), CENARIOS)
    atores = c.get("personagens", [])
    if not atores and not c.get("objetos") and not c.get("textos"):
        _erro(onde, "cena vazia: precisa de personagem, objeto ou texto")
    for a in atores:
        _na_lista(onde, "personagem", a.get("id"), tuple(ELENCO))
        _na_lista(onde, "entrada", a.get("entrada", "corte"), ENTRADAS)
        poses = a.get("poses")
        if not isinstance(poses, list) or not poses:
            _erro(onde, f"{a['id']}: 'poses' deve ser lista de {{t, pose, expressao}}")
        for k in poses:
            _na_lista(onde, "pose", k.get("pose"), tuple(POSES))
            _na_lista(onde, "expressao", k.get("expressao"), tuple(EXPRESSOES))
        if [k.get("t", 0) for k in poses] != sorted(k.get("t", 0) for k in poses):
            _erro(onde, f"{a['id']}: as poses devem estar em ordem de tempo")
        if a.get("segura"):
            _objeto_valido(a["segura"], onde)
    for o in c.get("objetos", []):
        _objeto_valido(o, onde)
        _na_lista(onde, "entrada", o.get("entrada", "pop"), ENTRADAS)
    for t in c.get("textos", []):
        if not isinstance(t.get("texto"), str) or not t["texto"].strip() or len(t["texto"]) > MAX_TEXTO:
            _erro(onde, f"texto inválido ou longo demais (máx. {MAX_TEXTO} caracteres): {t.get('texto')!r}")
        if not SEGURO_TOPO <= t.get("y", 400) <= SEGURO_BASE:
            _erro(onde, f"texto '{t['texto']}' fora da área segura (y entre {SEGURO_TOPO} e {SEGURO_BASE})")
        _na_lista(onde, "cor do texto", t.get("cor", "claro"), ("claro", "destaque", "apoio", "fundo", "contorno"))
        _na_lista(onde, "entrada", t.get("entrada", "pop"), ENTRADAS)
        largura = fonte("impacto", t.get("tam", 110)).getlength(t["texto"])
        if largura > W - 60:
            _erro(onde, f"texto '{t['texto']}' não cabe na largura com tam {t.get('tam', 110)}: quebre em dois textos ou reduza")
    for b in c.get("baloes", []):
        if not isinstance(b.get("linhas"), list) or not b["linhas"] or any(not isinstance(x, str) or len(x) > 22 for x in b["linhas"]):
            _erro(onde, "balão: 'linhas' é uma lista de frases com até 22 caracteres")
        if b.get("de") and b["de"] not in {a.get("id") for a in atores}:
            _erro(onde, f"balão de '{b['de']}', que não está nesta cena")
    tr = c.get("transicao") or {}
    _na_lista(onde, "transição de entrada", tr.get("entrada", "corte"), TRANS_ENTRADA)
    _na_lista(onde, "transição de saída", tr.get("saida", "corte"), TRANS_SAIDA)


def _objeto_valido(o, onde):
    _na_lista(onde, "objeto", o.get("tipo"), OBJETOS)
    if o["tipo"] == "celular":
        if not (isinstance(o.get("texto"), str) and o["texto"].strip()):
            _erro(onde, "celular precisa de 'texto' coerente com a cena: tela vazia não passa")
        if len(_quebrar_tela(o["texto"], 30, 146)) > 6 or any(fonte("pesada", 30).getlength(x) > 146 for x in _quebrar_tela(o["texto"], 30, 146)):
            _erro(onde, f"o texto do celular não cabe na tela: {o['texto']!r}. Use palavras curtas, até 6 linhas")
    if o["tipo"] == "grafico" and not o.get("barras"):
        _erro(onde, "gráfico precisa de 'barras' [{rotulo, valor, texto}]")


def textos(c):
    """O que aparece escrito na tela, para a conformidade e o Vini."""
    saida = list(c.get("rotulos", []))
    saida += [t["texto"] for t in c.get("textos", [])]
    for b in c.get("baloes", []):
        saida += b.get("linhas", [])
    for a in c.get("personagens", []):
        if (a.get("segura") or {}).get("texto"):
            saida.append(a["segura"]["texto"])
    for o in c.get("objetos", []):
        if o.get("texto"):
            saida.append(o["texto"])
        saida += [b.get("rotulo") or b.get("texto") or "" for b in o.get("barras", [])]
    return [x for x in saida if x]

