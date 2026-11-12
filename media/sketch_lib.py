"""Biblioteca do estilo sketch: papel de caderno pautado, traço de caneta tremido e ícones simples, tudo original.

Usada pelo `output/<slug>/sketch_cenas.py` (escrito pelo Olise ou pelo Barcola) e pelo `media/sketch.py` (que renderiza).
Contrato de cada cena: `def cena_N(lt, dur)` devolve uma `PIL.Image` RGB no tamanho do formato (`W` x `H`), onde `lt` é o
tempo local da cena em segundos e `dur` é a duração dela. A função só depende de `lt`: o mesmo `lt` dá sempre o mesmo quadro.

Os ícones recebem o `ImageDraw` (`d`), o centro (`cx`, `cy`), a escala `s`, uma `seed` (o tremido de cada
elemento é fixo entre os quadros) e `frac` (0 a 1: quanto do contorno já foi desenhado; use `entra()`).
Mantenha o conteúdo entre SEGURO_TOPO e SEGURO_BASE: o topo e a base ficam cobertos pela interface do app.

Formatos: `vertical` (1080x1920, Short) é o padrão. `horizontal` (1920x1080, vídeo longo) é ativado com
`definir_formato("horizontal")` antes de desenhar; o `media/sketch.py` faz isso sozinho.

Variação: `definir_variante("caderno_pautado", {"papel": "bege", "traco": "grafite"})`, também antes de carregar o sketch_cenas.py.
Sem variação, cada quadro sai idêntico ao de sempre.
"""
import math
import os
import random
from functools import lru_cache

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FORMATOS = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}
W, H = FORMATOS["vertical"]
SEGURO_TOPO, SEGURO_BASE = 190, 1500

PAPEL = (246, 244, 236)
PAUTA = (190, 206, 226)
MARGEM = (232, 150, 150)
INK = (28, 28, 34)
VERMELHO = (176, 40, 40)
GELO = (205, 232, 250)
FERRO = (150, 150, 155)
SOL_AMARELO = (255, 200, 80)
LARANJA = (240, 110, 40)
AZUL = (90, 150, 220)
CERVEJA = (240, 175, 55)
VERDE = (110, 180, 120)

# Kalam (manuscrita, licença OFL, em media/fonts/) combina com o traço de caneta; Arial só como reserva.
_DIR_FONTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_FONTES = {
    True: [os.path.join(_DIR_FONTES, "Kalam-Bold.ttf"),
           "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    False: [os.path.join(_DIR_FONTES, "Kalam-Regular.ttf"),
            "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}


@lru_cache(maxsize=None)
def _fonte_de(inicio, tam, negrito):
    for caminho in _FONTES[negrito][inicio:]:
        try:
            return ImageFont.truetype(caminho, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def fonte(tam, negrito=True):
    return _fonte_de(0, tam, negrito)


def _reserva(tam, negrito=True):
    """Fonte sem a Kalam, para os símbolos que ela não tem (ex.: ↔)."""
    return _fonte_de(1, tam, negrito)


@lru_cache(maxsize=None)
def _tem_glifo(ch, negrito):
    """A Kalam desenha um quadrado (.notdef) para o que não tem; compara com um caractere de uso privado."""
    f = fonte(60, negrito)
    return ch.isspace() or bytes(f.getmask(ch)) != bytes(f.getmask(""))


_PAPEL = None
_INK_PADRAO = INK
_TINTA = {"cor": INK, "w": 1.0, "amp": 1.0, "op_margem": 0.28}
_PAPEIS = {"bege": (243, 232, 208), "branco": (252, 252, 249)}
_TRACOS = {"grafite": {"cor": (66, 66, 72), "w": 0.85, "amp": 1.35}, "marcador": {"cor": (24, 30, 58), "w": 1.55, "amp": 0.75}}
_ORIGINAIS = {"PAPEL": PAPEL, "PAUTA": PAUTA, "MARGEM": MARGEM, "INK": INK}
MARCADOR_AMARELO, MARCADOR_ROSA, MARCADOR_AZUL = (255, 232, 110), (255, 170, 190), (150, 215, 245)


def definir_variante(nome=None, opcoes=None):
    """Troca papel, pauta e traço. As constantes mudam antes do `from media.sketch_lib import *` do sketch_cenas.py."""
    global PAPEL, PAUTA, MARGEM, INK, _PAPEL
    _PAPEL = None
    if nome is None:
        PAPEL, PAUTA, MARGEM, INK = (_ORIGINAIS[k] for k in ("PAPEL", "PAUTA", "MARGEM", "INK"))
        _TINTA.update(cor=INK, w=1.0, amp=1.0, op_margem=0.28)
        return
    if nome != "caderno_pautado":
        raise ValueError(f"variação desconhecida: {nome}")
    o = opcoes or {}
    tr = _TRACOS[o.get("traco", "grafite")]
    PAPEL, PAUTA, MARGEM, INK = _PAPEIS[o.get("papel", "bege")], (150, 200, 235), (214, 60, 60), tr["cor"]
    _TINTA.update(cor=tr["cor"], w=tr["w"], amp=tr["amp"], op_margem=0.9)


def definir_formato(nome):
    """Troca o tamanho do quadro e a área segura. Chamar antes de carregar sketch_cenas.py (ou de desenhar)."""
    global W, H, SEGURO_TOPO, SEGURO_BASE, _PAPEL
    W, H = FORMATOS[nome]
    if H > W:  # vertical: a interface do celular cobre topo e base
        SEGURO_TOPO, SEGURO_BASE = 190, 1500
    else:  # horizontal: margem menor; a tela de fim do YouTube ocupa a base nos últimos segundos
        SEGURO_TOPO, SEGURO_BASE = 90, 960
    _PAPEL = None


def papel():
    """Folha de caderno: fundo off-white, pauta azul a cada 64 px a partir de y=140, margem vermelha em x=150."""
    global _PAPEL
    if _PAPEL is None:
        im = Image.new("RGB", (W, H), PAPEL)
        d = ImageDraw.Draw(im)
        for y in range(140, H, 64):
            d.line([(0, y), (W, y)], fill=PAUTA, width=3)
        op = _TINTA["op_margem"]
        cor_margem = tuple(round(p + (m - p) * op) for p, m in zip(PAPEL, MARGEM))
        d.line([(150, 0), (150, H)], fill=cor_margem, width=3)
        _PAPEL = im
    return _PAPEL.copy()


# ---------- tempo ----------
def _clamp(x):
    return max(0.0, min(1.0, x))


def entra(lt, t0, dur=0.4):
    """0 antes de t0, sobe suave até 1 em `dur` s. Use como `frac` do contorno ou como fator de altura."""
    x = _clamp((lt - t0) / dur)
    return 1 - (1 - x) ** 3


def mola(lt, t0, dur=0.45):
    """Escala de entrada com leve estouro (0 -> 1.12 -> 1). Multiplique pela escala `s` do ícone."""
    x = _clamp((lt - t0) / dur)
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    c1 = 1.70158  # easeOutBack
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pulso(lt, vel=3.0, amp=0.06):
    return 1 + amp * math.sin(lt * vel * math.tau / 2)


def tremer(lt, vel=11.0, base=0.9, amp=0.1):
    """Brilho de chama/luz: 0.9 + 0.1 * sin(t * 11)."""
    return base + amp * math.sin(lt * vel)


# ---------- traço ----------
def circ(cx, cy, r, n=48):
    return [(cx + r * math.cos(math.tau * k / n), cy + r * math.sin(math.tau * k / n)) for k in range(n)]


def traco(d, pts, seed, frac=1.0, w=6, amp=2.5, col=INK, fechado=False):
    """Linha de caneta: amostra um ponto a cada ~10 px e treme cada um ±amp px (seed fixa = tremido estável)."""
    if frac <= 0 or len(pts) < 2:
        return
    if col == _INK_PADRAO:  # os ícones trazem INK como valor padrão: é aqui que seguem o traço da variação
        col = _TINTA["cor"]
    w, amp = max(1, round(w * _TINTA["w"])), amp * _TINTA["amp"]
    rng = random.Random(seed)
    if fechado:
        pts = list(pts) + [pts[0]]
    denso = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(2, int(math.dist((x0, y0), (x1, y1)) / 10))
        for k in range(n):
            t = k / n
            denso.append((x0 + (x1 - x0) * t + rng.uniform(-amp, amp), y0 + (y1 - y0) * t + rng.uniform(-amp, amp)))
    denso.append((pts[-1][0], pts[-1][1]))
    d.line(denso[:max(2, int(len(denso) * min(1.0, frac)))], fill=col, width=w, joint="curve")


def preencher(d, pts, cor):
    d.polygon(pts, fill=cor)


def brilho(im, cx, cy, r, cor, k=1.0):
    """Halo suave: elipse numa camada 1/4 do tamanho, borrada, redimensionada e somada ao quadro."""
    pequeno = Image.new("RGB", (W // 4, H // 4), (0, 0, 0))
    dp = ImageDraw.Draw(pequeno)
    rr = r / 4
    dp.ellipse([cx / 4 - rr, cy / 4 - rr, cx / 4 + rr, cy / 4 + rr], fill=tuple(min(255, int(c * k)) for c in cor))
    pequeno = pequeno.filter(ImageFilter.GaussianBlur(max(1, rr * 0.5)))
    return ImageChops.add(im, pequeno.resize((W, H), Image.BILINEAR))


# ---------- texto ----------
def texto(d, x, y, s, tam=50, cor=INK, ancora="mm", negrito=True):
    if cor == _INK_PADRAO:
        cor = _TINTA["cor"]
    if all(_tem_glifo(ch, negrito) for ch in s):
        d.text((x, y), s, font=fonte(tam, negrito), fill=cor, anchor=ancora)
        return
    # Trechos que a Kalam não tem saem na fonte reserva, lado a lado, respeitando a âncora horizontal.
    trechos = []
    for ch in s:
        f = fonte(tam, negrito) if _tem_glifo(ch, negrito) else _reserva(tam, negrito)
        if trechos and trechos[-1][1] is f:
            trechos[-1][0] += ch
        else:
            trechos.append([ch, f])
    larg = sum(f.getlength(t) for t, f in trechos)
    x -= {"l": 0, "m": larg / 2, "r": larg}.get(ancora[0], 0)
    for t, f in trechos:
        d.text((x, y), t, font=f, fill=cor, anchor="l" + ancora[1])
        x += f.getlength(t)


def texto_multilinha(d, x, y, linhas, tam=50, cor=INK, espaco=1.25, negrito=True):
    for i, linha in enumerate(linhas):
        texto(d, x, y + i * tam * espaco, linha, tam, cor, "mm", negrito)


# ---------- ícones (todos originais, traço à mão) ----------
def pessoa(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=INK):
    """Boneco de palito. (cx, cy) = centro do tronco; altura total ~ 260*s."""
    sk = lambda pts, sd: traco(d, pts, seed + sd, frac, w=6, amp=2.5 * s, col=cor)
    sk(circ(cx, cy - 110 * s, 36 * s, 36), 1)
    sk([(cx, cy - 74 * s), (cx, cy + 40 * s)], 2)
    sk([(cx, cy - 40 * s), (cx - 50 * s, cy + 5 * s)], 3)
    sk([(cx, cy - 40 * s), (cx + 50 * s, cy + 5 * s)], 4)
    sk([(cx, cy + 40 * s), (cx - 35 * s, cy + 125 * s)], 5)
    sk([(cx, cy + 40 * s), (cx + 35 * s, cy + 125 * s)], 6)


def grupo_pessoas(d, cx, cy, n, s=0.6, seed=0, frac=1.0, passo=130, cores=None):
    """Fila de `n` bonecos. `cores`: lista opcional de cores de traço (uma por boneco)."""
    x0 = cx - (n - 1) * passo * s / 2 * 1.0
    for i in range(n):
        pessoa(d, x0 + i * passo * s, cy, s, seed + 10 * i, frac, (cores[i] if cores else INK))


def copo(d, cx, cy, s=1.0, seed=0, frac=1.0, nivel=0.7, cor=CERVEJA):
    """Copo (tipo de cerveja). `nivel` 0..1 = quanto está cheio. (cx, cy) = centro; altura ~ 230*s."""
    lt_, lb = 80 * s, 62 * s
    top, bot = cy - 115 * s, cy + 115 * s
    contorno = [(cx - lt_, top), (cx + lt_, top), (cx + lb, bot), (cx - lb, bot)]
    if nivel > 0 and frac >= 0.99:
        y = bot - (bot - top) * nivel
        larg = lb + (lt_ - lb) * ((bot - y) / (bot - top))
        preencher(d, [(cx - larg, y), (cx + larg, y), (cx + lb - 4, bot - 4), (cx - lb + 4, bot - 4)], cor)
        traco(d, [(cx - larg, y), (cx + larg, y)], seed + 9, 1.0, w=4, amp=1.5)
    traco(d, contorno, seed, frac, w=6, amp=2 * s, fechado=True)


def garrafa(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=VERDE):
    """Garrafa com rótulo. Altura ~ 300*s."""
    c = [(cx - 40 * s, cy + 150 * s), (cx - 40 * s, cy - 20 * s), (cx - 14 * s, cy - 70 * s), (cx - 14 * s, cy - 150 * s),
         (cx + 14 * s, cy - 150 * s), (cx + 14 * s, cy - 70 * s), (cx + 40 * s, cy - 20 * s), (cx + 40 * s, cy + 150 * s)]
    if frac >= 0.99:
        preencher(d, c, cor)
        preencher(d, [(cx - 40 * s, cy + 20 * s), (cx + 40 * s, cy + 20 * s), (cx + 40 * s, cy + 90 * s), (cx - 40 * s, cy + 90 * s)], PAPEL)
    traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        traco(d, [(cx - 40 * s, cy + 20 * s), (cx + 40 * s, cy + 20 * s), (cx + 40 * s, cy + 90 * s), (cx - 40 * s, cy + 90 * s)],
              seed + 3, 1.0, w=4, amp=1.5, fechado=True)


def casa(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=None):
    """Casa simples. (cx, cy) = centro do corpo; altura total ~ 260*s."""
    corpo = [(cx - 100 * s, cy + 100 * s), (cx - 100 * s, cy - 30 * s), (cx + 100 * s, cy - 30 * s), (cx + 100 * s, cy + 100 * s)]
    telhado = [(cx - 125 * s, cy - 30 * s), (cx, cy - 130 * s), (cx + 125 * s, cy - 30 * s)]
    if cor and frac >= 0.99:
        preencher(d, corpo, cor)
    traco(d, corpo, seed, frac, w=6, amp=2 * s, fechado=True)
    traco(d, telhado, seed + 1, frac, w=6, amp=2 * s)
    traco(d, [(cx - 22 * s, cy + 100 * s), (cx - 22 * s, cy + 30 * s), (cx + 22 * s, cy + 30 * s), (cx + 22 * s, cy + 100 * s)],
          seed + 2, frac, w=5, amp=1.5 * s)


def moeda(d, cx, cy, s=1.0, seed=0, frac=1.0, simbolo="R$"):
    r = 70 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOL_AMARELO)
    traco(d, circ(cx, cy, r, 40), seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        texto(d, cx, cy, simbolo, int(54 * s))


def celular(d, cx, cy, s=1.0, seed=0, frac=1.0, tela=GELO):
    """Celular em pé. Altura ~ 280*s."""
    c = [(cx - 85 * s, cy - 140 * s), (cx + 85 * s, cy - 140 * s), (cx + 85 * s, cy + 140 * s), (cx - 85 * s, cy + 140 * s)]
    if frac >= 0.99:
        preencher(d, [(cx - 72 * s, cy - 112 * s), (cx + 72 * s, cy - 112 * s), (cx + 72 * s, cy + 100 * s), (cx - 72 * s, cy + 100 * s)], tela)
    traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
    traco(d, [(cx - 72 * s, cy - 112 * s), (cx + 72 * s, cy - 112 * s), (cx + 72 * s, cy + 100 * s), (cx - 72 * s, cy + 100 * s)],
          seed + 1, frac, w=4, amp=1.5 * s, fechado=True)
    traco(d, [(cx - 14 * s, cy + 122 * s), (cx + 14 * s, cy + 122 * s)], seed + 2, frac, w=5, amp=1)


def relogio(d, cx, cy, s=1.0, seed=0, frac=1.0, t=0.0):
    """Relógio de parede. `t` em segundos gira o ponteiro grande (use `lt`)."""
    r = 80 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
    traco(d, circ(cx, cy, r, 44), seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        a = t * 1.2 - math.pi / 2
        traco(d, [(cx, cy), (cx + 0.78 * r * math.cos(a), cy + 0.78 * r * math.sin(a))], seed + 1, 1.0, w=5, amp=1)
        traco(d, [(cx, cy), (cx + 0.5 * r * math.cos(a / 12 - 1.0), cy + 0.5 * r * math.sin(a / 12 - 1.0))], seed + 2, 1.0, w=7, amp=1)


def coracao(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=(225, 90, 100)):
    pts = []
    for k in range(40):
        a = math.tau * k / 40
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * 5.5 * s, cy + y * 5.5 * s))
    if frac >= 0.99:
        preencher(d, pts, cor)
    traco(d, pts, seed, frac, w=6, amp=2 * s, fechado=True)


def sol(d, cx, cy, s=1.0, seed=0, lt=0.0, frac=1.0):
    """Sol com raios que pulsam para fora."""
    r = 62 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SOL_AMARELO)
    traco(d, circ(cx, cy, r, 36), seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        for k in range(12):
            a = math.tau * k / 12
            r0 = r + 20 * s + 8 * s * math.sin(lt * 4 + k)
            r1 = r0 + 34 * s + 10 * s * math.sin(lt * 4 + k)
            traco(d, [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                  seed + 20 + k, 1.0, w=5, amp=1)


def seta(d, x0, y0, x1, y1, seed=0, frac=1.0, cor=INK, w=7):
    """Seta de (x0, y0) até (x1, y1). Aponta para baixo/cima/lado conforme as coordenadas."""
    traco(d, [(x0, y0), (x1, y1)], seed, frac, w=w, amp=2, col=cor)
    if frac >= 0.99:
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            traco(d, [(x1, y1), (x1 + 44 * math.cos(a + da), y1 + 44 * math.sin(a + da))], seed + 5, 1.0, w=w, amp=1.5, col=cor)


def cruz(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=VERMELHO):
    traco(d, [(cx - 45 * s, cy - 45 * s), (cx + 45 * s, cy + 45 * s)], seed, frac, w=10, amp=2, col=cor)
    traco(d, [(cx + 45 * s, cy - 45 * s), (cx - 45 * s, cy + 45 * s)], seed + 1, max(0, frac * 2 - 1), w=10, amp=2, col=cor)


def check(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=(60, 150, 90)):
    traco(d, [(cx - 50 * s, cy), (cx - 15 * s, cy + 40 * s), (cx + 55 * s, cy - 45 * s)], seed, frac, w=11, amp=2, col=cor)


def lupa(d, cx, cy, s=1.0, seed=0, frac=1.0):
    r = 60 * s
    if frac >= 0.99:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GELO)
    traco(d, circ(cx, cy, r, 36), seed, frac, w=7, amp=2 * s, fechado=True)
    traco(d, [(cx + r * 0.72, cy + r * 0.72), (cx + r * 1.75, cy + r * 1.75)], seed + 1, frac, w=12, amp=2)


def calendario(d, cx, cy, s=1.0, seed=0, frac=1.0, titulo=""):
    c = [(cx - 100 * s, cy - 90 * s), (cx + 100 * s, cy - 90 * s), (cx + 100 * s, cy + 100 * s), (cx - 100 * s, cy + 100 * s)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
        preencher(d, [(cx - 100 * s, cy - 90 * s), (cx + 100 * s, cy - 90 * s), (cx + 100 * s, cy - 40 * s), (cx - 100 * s, cy - 40 * s)], (225, 90, 100))
    traco(d, c, seed, frac, w=6, amp=2 * s, fechado=True)
    if frac >= 0.99:
        for k in range(3):
            traco(d, [(cx - 100 * s, cy - 10 * s + k * 38 * s), (cx + 100 * s, cy - 10 * s + k * 38 * s)], seed + 3 + k, 1.0, w=3, amp=1)
        if titulo:
            texto(d, cx, cy - 65 * s, titulo, int(36 * s), (255, 255, 255))


def balao(d, cx, cy, larg, alt, linhas, seed=0, frac=1.0, tam=44, cauda="esq"):
    """Balão de fala com texto curto (linhas = lista de strings). cauda=None omite o triângulo."""
    x0, x1, y0, y1 = cx - larg / 2, cx + larg / 2, cy - alt / 2, cy + alt / 2
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if frac >= 0.99:
        preencher(d, c, (255, 255, 255))
    traco(d, c, seed, frac, w=6, amp=2, fechado=True)
    if cauda is not None:
        tx = x0 + 60 if cauda == "esq" else x1 - 60
        cauda_pts = [(tx - 20, y1), (tx + (-30 if cauda == "esq" else 30), y1 + 50), (tx + 25, y1)]
        if frac >= 0.99:
            preencher(d, cauda_pts, (255, 255, 255))
        traco(d, cauda_pts, seed + 1, frac, w=6, amp=2)
    if frac >= 0.99:
        texto_multilinha(d, cx, cy - (len(linhas) - 1) * tam * 0.62, linhas, tam)


def barras(d, x, y_base, itens, larg=170, alt_max=700, escala_max=None, lt=0.0, t0=0.0, seed=0, passo=None, tam_rotulo=40):
    """Gráfico de barras desenhado à mão. itens = [{"rotulo": "2023", "valor": 62, "cor": AZUL, "texto": "62%"}, ...].
    As barras crescem em sequência a partir de t0. `x` = centro do gráfico; `y_base` = linha do chão."""
    n = len(itens)
    passo = passo or larg + 60
    escala_max = escala_max or max(i["valor"] for i in itens)
    x_ini = x - (n - 1) * passo / 2
    traco(d, [(x_ini - passo * 0.7, y_base), (x_ini + (n - 1) * passo + passo * 0.7, y_base)], seed, entra(lt, t0, 0.5), w=7)
    for k, it in enumerate(itens):
        f = entra(lt, t0 + 0.25 + k * 0.28, 0.7)
        cx = x_ini + k * passo
        h = alt_max * it["valor"] / escala_max * f
        if h > 4:
            b = [(cx - larg / 2, y_base), (cx - larg / 2, y_base - h), (cx + larg / 2, y_base - h), (cx + larg / 2, y_base)]
            preencher(d, b, it.get("cor", AZUL))
            traco(d, b, seed + 7 + k, 1.0, w=6, amp=2, fechado=True)
            texto(d, cx, y_base - h - 40, it.get("texto", f"{it['valor']}"), 54)
        texto(d, cx, y_base + 50, it.get("rotulo", ""), tam_rotulo)


# ---------- anotações de caderno ----------
def marcador(d, x0, y, x1, cor=None, alt=46):
    """Faixa de marca-texto, atrás do texto: desenhe antes dele."""
    d.rectangle([x0, y - alt / 2, x1, y + alt / 2], fill=cor or MARCADOR_AMARELO)


def anotacao(d, x, y, s, seta_para=None, tam=44, cor=None, seed=0, frac=1.0):
    """Nota à mão, com seta opcional para o que ela comenta."""
    cor = cor or VERMELHO
    if frac >= 0.99:
        texto(d, x, y, s, tam, cor)
    if seta_para:
        seta(d, x, y - tam * 0.8, seta_para[0], seta_para[1], seed=seed, frac=frac, cor=cor, w=5)
