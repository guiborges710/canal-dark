"""Legenda estilo 'viral' (CapCut / Hormozi): poucas palavras, fonte pesada, contorno grosso,
palavra falada em destaque (karaokê) e *pop* de escala na entrada de cada bloco.

ANTES: um PNG do tamanho do quadro por bloco, cada um virando um input + um overlay no ffmpeg.
Isso estourava a memória quando havia muitos blocos (por isso o caption_max_words tinha subido
para 7, matando o visual viral).

AGORA: rendemos uma SEQUÊNCIA de frames (um PNG por frame do vídeo) em captions/frames/ e o
render.py compõe tudo com UM único input (`image2`) + UM único `overlay`. Memória constante,
e com controle de pixel para karaokê + animação (não precisa de libass/drawtext no build).
O captions.srt continua sendo gerado à parte por render.build_srt.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Fontes pesadas que dão o visual "viral". A primeira que existir é usada.
# Montserrat ExtraBold (fonte variável, peso fixado em 800) é o padrão recomendado (receita viral).
FONT_CANDIDATES = [
    "assets/fonts/Montserrat-ExtraBold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def caps_cfg(cfg):
    """Lê os ajustes de estilo do bloco render do config, com padrões de Short vertical viral."""
    r = cfg["render"]
    return {
        "size": r.get("caption_size", 0.072),              # altura da fonte como fração da altura
        "y": r.get("caption_y", 0.68),                     # centro vertical do texto (fração)
        "font": r.get("caption_font"),                     # caminho .ttf opcional
        "stroke": r.get("caption_stroke", 0.14),           # contorno como fração da fonte
        "color": r.get("caption_color", "#FFFFFF"),        # palavra normal
        "active_color": r.get("caption_active_color", "#FFD700"),  # palavra falada (karaokê)
        "stroke_color": r.get("caption_stroke_color", "#000000"),
        "shadow": r.get("caption_shadow", True),           # sombra para descolar do fundo
        "uppercase": r.get("caption_uppercase", True),
        "max_words": r.get("caption_max_words", 3),        # palavras por bloco (poucas = viral)
        "pop": r.get("caption_pop", 0.12),                 # duração do pop de entrada (s)
        "pop_scale": r.get("caption_pop_scale", 1.18),     # escala inicial do pop
    }


def _load_font(path, size):
    for p in ([path] if path else []) + FONT_CANDIDATES:
        if p and Path(p).exists():
            try:
                f = ImageFont.truetype(p, size)
                try:  # fonte variável: fixa o peso em ExtraBold (800)
                    f.set_variation_by_axes([800])
                except Exception:
                    pass
                return f
            except Exception:
                continue
    return ImageFont.load_default()


# --- Conversão de números falados (pt-BR) para dígitos, SÓ na legenda ---------------
# O áudio continua dizendo "vinte e três" (soa melhor); a legenda mostra "23".
import unicodedata

_UNIT = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4,
         "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11,
         "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14, "quinze": 15,
         "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19}
_TENS = {"vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "cincoenta": 50,
         "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90}
_HUND = {"cem": 100, "cento": 100, "duzentos": 200, "duzentas": 200, "trezentos": 300,
         "trezentas": 300, "quatrocentos": 400, "quatrocentas": 400, "quinhentos": 500,
         "quinhentas": 500, "seiscentos": 600, "seiscentas": 600, "setecentos": 700,
         "setecentas": 700, "oitocentos": 800, "oitocentas": 800, "novecentos": 900,
         "novecentas": 900}
_SCALE = {"mil": 1000, "milhao": 1_000_000, "milhoes": 1_000_000,
          "bilhao": 1_000_000_000, "bilhoes": 1_000_000_000}
_AMBIG = {"um", "uma", "uns", "umas"}  # artigo sozinho não vira número


def _norm(w):
    """minúsculo, sem acento, sem pontuação nas pontas."""
    w = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode()
    return w.strip(".,!?;:\"'()—–…").lower()


def _is_num(n):
    return n in _UNIT or n in _TENS or n in _HUND or n in _SCALE


def _parse_value(nums):
    """Lista de palavras-número normalizadas (sem 'e') -> inteiro."""
    total = cur = 0
    for n in nums:
        if n in _UNIT:
            cur += _UNIT[n]
        elif n in _TENS:
            cur += _TENS[n]
        elif n in _HUND:
            cur += _HUND[n]
        elif n in _SCALE:
            cur = (cur or 1) * _SCALE[n]
            if _SCALE[n] >= 1000:
                total += cur
                cur = 0
    return total + cur


def _fmt_compact(n):
    """23 -> '23'; 23000 -> '23 mil'; 230000 -> '230 mil'; 2300000 -> '2,3 milhões'."""
    def base(b):
        return str(int(b)) if b == int(b) else f"{b:.1f}".replace(".", ",").rstrip("0").rstrip(",")
    if n >= 1_000_000_000:
        b = n / 1_000_000_000
        return f"{base(b)} {'bilhão' if b == 1 else 'bilhões'}"
    if n >= 1_000_000:
        b = n / 1_000_000
        return f"{base(b)} {'milhão' if b == 1 else 'milhões'}"
    if n >= 1000:
        return f"{base(n / 1000)} mil"
    return str(int(n))


def _digitize(raw):
    """Troca sequências de números falados por dígitos, devolvendo uma lista de
    (texto, peso) onde o peso = nº de palavras faladas originais que o token cobre
    (para o tempo da legenda acompanhar a voz)."""
    out, i = [], 0
    while i < len(raw):
        # "por cento" / "por cem" = porcentagem, não o número 100 — não converte.
        if _norm(raw[i]) in ("cento", "cem") and i > 0 and _norm(raw[i - 1]) == "por":
            out.append((raw[i], 1))
            i += 1
            continue
        # tenta consumir uma sequência de palavras-número (com 'e' interno)
        j, nums = i, []
        while j < len(raw):
            nw = _norm(raw[j])
            if _is_num(nw):
                nums.append(nw)
                j += 1
            elif nw == "e" and j + 1 < len(raw) and _is_num(_norm(raw[j + 1])) and nums:
                j += 1  # 'e' liga dois números; não entra na conta
            else:
                break
        run_len = j - i
        # descarta: nada, ou só um artigo ambíguo (um/uma)
        if run_len == 0 or (len(nums) == 1 and nums[0] in _AMBIG and nums[0] not in _TENS):
            out.append((raw[i], 1))
            i += 1
            continue
        value = _parse_value(nums)
        disp = _fmt_compact(value)
        # "<número> por cento" -> "<número>%": cola o % e absorve as 2 palavras faladas.
        pct = (j + 1 < len(raw) and _norm(raw[j]) == "por"
               and _norm(raw[j + 1]) in ("cento", "cem"))
        end = j + 2 if pct else j
        total_w = (end - i)                      # palavras faladas que este trecho cobre
        # preserva pontuação final da última palavra original consumida
        tail = raw[end - 1]
        trail = tail[len(tail.rstrip(".,!?;:\"')—–…")):]
        parts = disp.split()
        if pct:
            parts[-1] += "%"
        if trail:
            parts[-1] += trail
        for p in parts:                          # divide o peso do trecho entre os tokens gerados
            out.append((p, total_w / len(parts)))
        i = end
    return out


def build_word_cues(scenes, durs, pause, max_words=3):
    """Divide cada cena em blocos curtos e, dentro do bloco, dá um instante a cada palavra.

    Devolve uma lista de blocos:
      {"start", "end", "words": [palavra, ...], "word_times": [(ini, fim), ...]}
    Números falados viram dígitos na legenda (23 em vez de "vinte e três"), mantendo o
    tempo que a voz leva para falá-los. Alinhado ao mesmo tempo da narração do render.
    """
    t, blocks = 0.0, []
    for sc, d in zip(scenes, durs):
        raw = sc["text"].split()
        if not raw:
            t += d
            continue
        speak = max(0.1, d - pause)          # tempo realmente falado nesta cena
        per_word = speak / len(raw)          # duração média de uma palavra FALADA
        toks = _digitize(raw)                # [(texto, peso em palavras faladas), ...]
        cur = t
        for g in range(0, len(toks), max_words):
            group = toks[g:g + max_words]
            words = [tx for tx, _ in group]
            wt, w0 = [], cur
            for _, weight in group:
                dur = per_word * weight
                wt.append((w0, w0 + dur))
                w0 += dur
            blocks.append({"start": cur, "end": w0, "words": words, "word_times": wt})
            cur = w0
        t += d
    return blocks


def _wrap(draw, words, font, max_w):
    """Quebra a lista de palavras em linhas que cabem na largura. Devolve lista de linhas,
    cada uma como lista de índices (globais) das palavras — para sabermos qual destacar."""
    lines, cur, cur_idx = [], "", []
    for i, w in enumerate(words):
        trial = (cur + " " + w).strip()
        if not cur or draw.textlength(trial, font=font) <= max_w:
            cur, cur_idx = trial, cur_idx + [i]
        else:
            lines.append(cur_idx)
            cur, cur_idx = w, [i]
    if cur_idx:
        lines.append(cur_idx)
    return lines


def _draw_block(words, active, path, width, height, style, scale=1.0):
    """Desenha um frame: todas as palavras do bloco, com a palavra `active` em destaque.
    `scale` aplica o pop (escala a fonte do bloco inteiro)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    base = max(12, int(height * style["size"]))
    size = max(12, int(base * scale))
    font = _load_font(style["font"], size)
    disp = [w.upper() if style["uppercase"] else w for w in words]
    margin = int(width * 0.07)
    stroke = max(2, int(size * style["stroke"]))
    space = d.textlength(" ", font=font)
    asc, desc = font.getmetrics()
    line_h = asc + desc + int(size * 0.14)

    lines = _wrap(d, disp, font, width - 2 * margin)
    total_h = line_h * len(lines)
    y0 = int(height * style["y"]) - total_h // 2

    for li, idxs in enumerate(lines):
        line_w = sum(d.textlength(disp[i], font=font) for i in idxs) + space * (len(idxs) - 1)
        x = (width - line_w) // 2
        y = y0 + li * line_h
        for i in idxs:
            word = disp[i]
            fill = style["active_color"] if i == active else style["color"]
            if style["shadow"]:
                off = max(2, int(size * 0.05))
                d.text((x + off, y + off), word, font=font, fill=(0, 0, 0, 170),
                       stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
            d.text((x, y), word, font=font, fill=fill,
                   stroke_width=stroke, stroke_fill=style["stroke_color"])
            x += d.textlength(word, font=font) + space
    img.save(path)


def render_caption_frames(cfg, blocks, outdir, fps, total):
    """Renderiza um PNG por frame do vídeo (transparente onde não há legenda) e devolve
    (dir_frames, fps, n_frames). O render.py compõe com um único overlay de sequência.

    Faz cache: frames idênticos (mesmo bloco, mesma palavra ativa, sem pop) reusam o mesmo
    arquivo via hardlink/cópia, então não re-desenhamos 15 frames iguais à toa.
    """
    style = caps_cfg(cfg)
    d = outdir / "captions" / "frames"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.png"):
        old.unlink()
    w, h = cfg["render"]["width"], cfg["render"]["height"]
    n = int(round(total * fps))
    blank = d / "blank.png"
    Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(blank)
    cache = {}  # chave de estado -> caminho já renderizado

    def active_block(t):
        for b in blocks:
            if b["start"] <= t < b["end"]:
                return b
        return None

    for f in range(n):
        t = f / fps
        frame = d / f"{f:05}.png"
        b = active_block(t)
        if not b:
            _link(blank, frame)
            continue
        active = 0
        for wi, (ws, we) in enumerate(b["word_times"]):
            if ws <= t < we:
                active = wi
                break
            if t >= we:
                active = wi
        # Com 1 palavra por bloco não há "resto" para contrastar: mostra em branco (sem destaque).
        if len(b["words"]) == 1:
            active = -1
        # pop: escala decaindo nos primeiros style["pop"] s do bloco
        prog = (t - b["start"]) / max(0.01, style["pop"])
        if prog < 1.0:
            scale = style["pop_scale"] + (1.0 - style["pop_scale"]) * prog
            key = (id(b), active, round(scale, 2))
        else:
            scale = 1.0
            key = (id(b), active, 1.0)
        if key in cache:
            _link(cache[key], frame)
        else:
            _draw_block(b["words"], active, frame, w, h, style, scale)
            cache[key] = frame
    return d, fps, n


def _link(src, dst):
    """Reaproveita um PNG já renderizado sem duplicar bytes (hardlink; cópia se falhar)."""
    try:
        if dst.exists():
            dst.unlink()
        import os
        os.link(src, dst)
    except Exception:
        import shutil
        shutil.copy(src, dst)
