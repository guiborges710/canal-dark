"""Setor de Pesquisa de vídeos longos: acha os mais vistos do dia, da semana e do mês sobre um tema.

    .venv\\Scripts\\python -m pesquisa_videos                      # GTA 6, dia/semana/mês
    .venv\\Scripts\\python -m pesquisa_videos --tema "gta 6" --min-minutos 20 --quantos 10

Só pesquisa: não baixa nem publica. Usa a YouTube Data API (YOUTUBE_API_KEY no .env; cota grátis,
cerca de 100 unidades por busca, 3 buscas por rodada). Grava em pesquisa_videos/saida/AAAA-MM-DD.md e .json.
Os vídeos aqui NÃO têm autorização para corte: quem confirma é o Salah, no setor de Clipes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = Path(__file__).parent / "saida"
YT = "https://www.googleapis.com/youtube/v3"
JANELAS = (("dia", 1), ("semana", 7), ("mes", 30))
NOMES = {"dia": "Últimas 24 horas", "semana": "Últimos 7 dias", "mes": "Últimos 30 dias"}


def _chave() -> str:
    k = os.environ.get("YOUTUBE_API_KEY", "")
    if not k:
        env = RAIZ / ".env"
        if env.exists():
            for linha in env.read_text(encoding="utf-8").splitlines():
                if linha.startswith("YOUTUBE_API_KEY="):
                    k = linha.split("=", 1)[1].strip().strip("\"'")
    if not k:
        sys.exit("YOUTUBE_API_KEY não está no .env.")
    return k


def _minutos(iso: str) -> float:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0.0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 60 + mi + s / 60


IDIOMAS = (("ptbr", "Português (BR)", "pt", "BR"), ("en", "Inglês", "en", "US"))


def buscar(tema: str, dias: int, quantos: int, min_min: float, regiao: str, key: str,
           idioma: str = "pt", minimo: int = 3) -> list[dict]:
    """Mais vistos dentro da janela (vídeos longos). Se sobrar menos que `minimo` depois do filtro
    de duração e idioma, busca mais páginas (até 3) antes de desistir."""
    apos = (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out: list[dict] = []
    pagina = None
    for _ in range(3):
        params = dict(part="snippet", q=tema, type="video", order="viewCount", maxResults=50,
                      videoDuration="long", regionCode=regiao, relevanceLanguage=idioma,
                      publishedAfter=apos, key=key)
        if pagina:
            params["pageToken"] = pagina
        r = requests.get(f"{YT}/search", timeout=30, params=params)
        r.raise_for_status()
        dados = r.json()
        ids = [i["id"]["videoId"] for i in dados.get("items", [])]
        if ids:
            r = requests.get(f"{YT}/videos", timeout=30, params=dict(
                part="snippet,statistics,contentDetails,status", id=",".join(ids), key=key))
            r.raise_for_status()
            for it in r.json().get("items", []):
                dur = _minutos(it["contentDetails"].get("duration", ""))
                if dur < min_min:
                    continue
                sn = it["snippet"]
                lg = (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "").lower()
                if lg and not lg.startswith(idioma):  # idioma declarado diferente do pedido
                    continue
                st = it.get("statistics", {})
                out.append({
                    "id": it["id"], "url": f"https://www.youtube.com/watch?v={it['id']}",
                    "titulo": sn["title"], "canal": sn["channelTitle"],
                    "publicado": sn["publishedAt"][:10], "minutos": round(dur),
                    "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                    "comentarios": int(st.get("commentCount", 0)),
                    "licenca": it.get("status", {}).get("license", ""),
                })
        pagina = dados.get("nextPageToken")
        if len(out) >= minimo or not pagina:
            break
    out.sort(key=lambda v: v["views"], reverse=True)
    return out[:quantos]


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m pesquisa_videos")
    ap.add_argument("--tema", default="GTA 6")
    ap.add_argument("--quantos", type=int, default=10, help="máximo por lista e janela")
    ap.add_argument("--minimo", type=int, default=3, help="mínimo por lista e janela (busca mais páginas)")
    ap.add_argument("--min-minutos", type=float, default=20, help="só vídeos longos")
    r = ap.parse_args()
    key = _chave()

    res: dict = {}
    for cod, nome_i, idioma, regiao in IDIOMAS:
        res[cod] = {}
        for nome, dias in JANELAS:
            res[cod][nome] = buscar(r.tema, dias, r.quantos, r.min_minutos, regiao, key, idioma, r.minimo)
            print(f"[pesquisa] {nome_i} / {NOMES[nome]}: {len(res[cod][nome])} vídeo(s)")

    hoje = datetime.now().strftime("%Y-%m-%d")
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / f"{hoje}.json").write_text(
        json.dumps({"tema": r.tema, "data": hoje, "listas": res}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    md = [f"# Vídeos longos mais vistos: {r.tema} ({hoje})",
          f"Vídeos de {r.min_minutos:.0f}+ min, ordenados por visualizações. Duas listas: português (BR) e inglês.\n"]
    for cod, nome_i, _, _ in IDIOMAS:
        md.append(f"# Lista: {nome_i}\n")
        for nome, _ in JANELAS:
            md.append(f"## {NOMES[nome]}")
            if not res[cod][nome]:
                md.append("_Nenhum vídeo encontrado._\n")
                continue
            md.append("| # | Views | Min | Canal | Título | Data | Link |\n|---|---|---|---|---|---|---|")
            for i, v in enumerate(res[cod][nome], 1):
                t = v["titulo"].replace("|", "/")
                vw = f"{v['views']:,}".replace(",", ".")
                md.append(f"| {i} | {vw} | {v['minutos']} | {v['canal']} | {t} | "
                          f"{v['publicado']} | {v['url']} |")
            md.append("")
    (SAIDA / f"{hoje}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[pesquisa] relatório em {SAIDA / (hoje + '.md')}")


if __name__ == "__main__":
    main()
