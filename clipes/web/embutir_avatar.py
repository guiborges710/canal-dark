"""Embute a foto de um agente no painel de Clipes.

  python clipes/web/embutir_avatar.py Rivaldo C:\\caminho\\rivaldo.png

- Corta no centro até ficar quadrada, reduz para 240x240 e grava `avatares/<id>.jpg` (o original reduzido).
- Troca (ou acrescenta) a entrada do nome em `const FOTOS={...}` de `index.html`, em base64.
- O nome é o que aparece no fluxo (ex.: "Rivaldo", "Kaká"). A foto nova vale ao recarregar a página (Ctrl+F5).
"""
from __future__ import annotations

import argparse
import base64
import io
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
TAM = 240


def slug(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "agente"


def reduzir(origem: Path) -> bytes:
    im = Image.open(origem).convert("RGB")
    w, h = im.size
    lado = min(w, h)
    im = im.crop(((w - lado) // 2, (h - lado) // 2, (w + lado) // 2, (h + lado) // 2)).resize((TAM, TAM), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88, optimize=True)
    return buf.getvalue()


def embutir(nome: str, origem: Path, html: Path, pasta: Path) -> Path:
    jpg = reduzir(origem)
    pasta.mkdir(exist_ok=True)
    destino = pasta / f"{slug(nome)}.jpg"
    destino.write_bytes(jpg)
    texto = html.read_text(encoding="utf-8")
    m = re.search(r"const FOTOS=\{(.*?)\};", texto, re.S)
    if not m:
        raise SystemExit("não achei `const FOTOS={...};` no index.html")
    entradas = re.findall(r'"([^"]+)":"(data:image/jpeg;base64,[A-Za-z0-9+/=]+)"', m.group(1))
    fotos = dict(entradas)
    if len(fotos) != m.group(1).count('":"data:image'):
        raise SystemExit("o bloco FOTOS tem entrada fora do padrão; não vou mexer para não corromper o arquivo")
    fotos[nome] = "data:image/jpeg;base64," + base64.b64encode(jpg).decode()
    novo = "const FOTOS={" + ",".join(f'"{k}":"{v}"' for k, v in fotos.items()) + "};"
    tmp = html.with_suffix(".tmp")
    tmp.write_text(texto[: m.start()] + novo + texto[m.end():], encoding="utf-8")
    tmp.replace(html)
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nome", help="nome do agente como aparece no fluxo (ex.: Rivaldo)")
    ap.add_argument("imagem", help="PNG/JPG gerado")
    ap.add_argument("--html", default=str(AQUI / "index.html"), help="só para teste")
    a = ap.parse_args()
    origem = Path(a.imagem)
    if not origem.is_file():
        raise SystemExit(f"imagem não encontrada: {origem}")
    d = embutir(a.nome, origem, Path(a.html), AQUI / "avatares")
    print(f"ok: {a.nome} embutido (original reduzido em {d.name}). Recarregue o painel com Ctrl+F5.")


if __name__ == "__main__":
    sys.exit(main())
