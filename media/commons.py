"""Imagens reais de arquivo, livres, via Wikimedia Commons (sem chave de API).

Para cada cena, tenta de 1 a 3 consultas (campo "search" em cenas.json), filtra por licença livre,
baixa em até 1920 px de largura e enquadra em 16:9 (corte, ou fundo desfocado quando a proporção
é muito diferente). Ao lado de cada imagem fica um .json com o crédito (autor, licença, link),
usado depois no PUBLICAR.txt. Se nada servir, devolve False e o pipeline usa o provedor de reserva.

Licenças aceitas por padrão: domínio público, CC0 e CC BY. CC BY-SA só se commons.allow_share_alike: true.
Nunca aceita NC, ND nem marcadas como não livres.
"""
import html
import json
import re
import threading
import time
from io import BytesIO

import numpy as np
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

API = "https://commons.wikimedia.org/w/api.php"
_API_LOCK = threading.Lock()
_PICK_LOCK = threading.Lock()
_LAST = [0.0]

BAD_TITLE = re.compile(r"\.(svg|tif|tiff|gif|pdf|webm|ogv|ogg|djvu)$|logo|flag of|coat of arms|stamp|banknote|screenshot", re.I)
PD = re.compile(r"^(public domain|pd\b|pd-|cc0|no restrictions)", re.I)
CCBY = re.compile(r"^cc[- ]by\b", re.I)


def _clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _val(meta, key):
    return _clean((meta.get(key) or {}).get("value", ""))


def _license_class(meta, allow_sa):
    """Devolve 'pd', 'by' ou None (não utilizável)."""
    if _val(meta, "NonFree").lower() in ("true", "1", "yes"):
        return None
    lic = _val(meta, "LicenseShortName")
    if not lic:
        return None
    low = lic.lower()
    if re.search(r"(^|[\s-])(nc|nd)([\s-]|$)", low):
        return None
    if PD.match(lic):
        return "pd"
    if CCBY.match(lic):
        if "sa" in re.split(r"[\s-]", low) and not allow_sa:
            return None
        return "by"
    return None


def _api(cfg, params):
    c = cfg.get("commons", {})
    url = c.get("api_url", API)
    ua = c.get("user_agent", "canal-dark-pipeline/0.1 (projeto pessoal)")
    with _API_LOCK:  # no máximo ~2 requisições por segundo, como o Commons pede
        wait = 0.5 - (time.time() - _LAST[0])
        if wait > 0:
            time.sleep(wait)
        r = requests.get(url, params=params, headers={"User-Agent": ua}, timeout=30)
        _LAST[0] = time.time()
    r.raise_for_status()
    return r.json()


def search(cfg, query):
    c = cfg.get("commons", {})
    min_w = c.get("min_width", 1280)
    allow_sa = c.get("allow_share_alike", False)
    data = _api(cfg, {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": 25, "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1920,
        "iiextmetadatafilter": "LicenseShortName|Artist|Credit|NonFree", "uselang": "en"})
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 999)):
        info = (p.get("imageinfo") or [None])[0]
        title = p.get("title", "")
        if not info or BAD_TITLE.search(title) or info.get("mime") not in ("image/jpeg", "image/png"):
            continue
        w, h = info.get("width", 0), info.get("height", 0)
        if w < min_w or not h or not (0.6 <= w / h <= 3.0):
            continue
        meta = info.get("extmetadata") or {}
        cls = _license_class(meta, allow_sa)
        if not cls:
            continue
        out.append({"title": title, "url": info.get("thumburl") or info["url"], "page": info.get("descriptionurl", ""),
                    "width": w, "height": h, "license": _val(meta, "LicenseShortName"),
                    "artist": _val(meta, "Artist") or _val(meta, "Credit") or "autor desconhecido", "class": cls})
    out.sort(key=lambda x: x["class"] != "pd")  # domínio público primeiro (ordem de relevância preservada)
    return out


def _frame(img, w=1920, h=1080):
    img = ImageOps.exif_transpose(img).convert("RGB")
    ar = img.width / img.height
    if 1.45 <= ar <= 2.1:  # quase 16:9: corta
        s = max(w / img.width, h / img.height)
        big = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
        x, y = (big.width - w) // 2, int((big.height - h) * 0.4)
        return big.crop((x, y, x + w, y + h))
    s = max(w / img.width, h / img.height)  # fundo desfocado + imagem inteira no centro
    bg = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x, y = (bg.width - w) // 2, (bg.height - h) // 2
    bg = bg.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(38))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    s = min(w * 0.94 / img.width, h * 0.94 / img.height)
    fg = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    return bg


def _tone(img):
    """Contraste e cor leves, aplicados na imagem original (antes do enquadramento)."""
    img = ImageOps.autocontrast(img.convert("RGB"), cutoff=0.5)
    return ImageEnhance.Color(img).enhance(0.88)


def _vignette(img):
    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    arr = arr * (1 - 0.30 * np.clip(d - 0.5, 0, 1) ** 1.6)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def fetch(cfg, queries, out_path):
    """Escolhe e baixa a primeira imagem livre e ainda não usada. Devolve True se salvou a imagem."""
    sidecar = out_path.with_suffix(".json")
    with _PICK_LOCK:
        used = set()
        for f in out_path.parent.glob("*.json"):
            if f != sidecar:
                try:
                    used.add(json.loads(f.read_text(encoding="utf-8"))["title"])
                except Exception:
                    pass
        for q in queries[:3]:
            cands = [c for c in search(cfg, q) if c["title"] not in used]
            for c in cands[:3]:
                try:
                    r = requests.get(c["url"], headers={"User-Agent": cfg.get("commons", {}).get(
                        "user_agent", "canal-dark-pipeline/0.1 (projeto pessoal)")}, timeout=60)
                    r.raise_for_status()
                    img = Image.open(BytesIO(r.content))
                    img.load()
                except Exception:
                    continue
                grade = cfg.get("commons", {}).get("grade", True)
                final = _frame(_tone(img) if grade else img)
                if grade:
                    final = _vignette(final)
                final.save(out_path, "JPEG", quality=92)
                sidecar.write_text(json.dumps({**{k: c[k] for k in ("title", "page", "license", "artist")}, "query": q},
                                              ensure_ascii=False), encoding="utf-8")
                return True
    return False


def credits(images_dir):
    """Linhas de crédito de todas as imagens reais da pasta, sem repetir."""
    lines, seen = [], set()
    for f in sorted(images_dir.glob("*.json")):
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if m["title"] in seen:
            continue
        seen.add(m["title"])
        title = m["title"].replace("File:", "")
        lines.append(f'"{title}" - {m["artist"]} ({m["license"]}). {m["page"]}')
    return lines
