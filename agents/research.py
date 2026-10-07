"""Agentes de pesquisa: (1) ideias de pauta a partir do YouTube; (2) notas factuais de um tema."""
import json
import os
from datetime import datetime, timedelta, timezone

import requests

from . import mocks
from .common import prompt

YT = "https://www.googleapis.com/youtube/v3"


def youtube_outliers(cfg):
    """Busca vídeos de alto desempenho no nicho (custa cota da API do YouTube: ~100 unidades por busca)."""
    key = os.environ["YOUTUBE_API_KEY"]
    rc = cfg["research"]
    after = (datetime.now(timezone.utc) - timedelta(days=rc["days_back"])).strftime("%Y-%m-%dT00:00:00Z")
    lang2 = cfg["channel"]["language"].split("-")[0]
    ids = {}
    for q in rc["youtube_queries"]:
        r = requests.get(f"{YT}/search", timeout=30, params=dict(
            part="snippet", q=q, type="video", order="viewCount", maxResults=rc["max_results"],
            regionCode=rc["region"], relevanceLanguage=lang2, publishedAfter=after, key=key))
        r.raise_for_status()
        for it in r.json().get("items", []):
            ids[it["id"]["videoId"]] = True
    out, idlist, now = [], list(ids), datetime.now(timezone.utc)
    for i in range(0, len(idlist), 50):
        r = requests.get(f"{YT}/videos", timeout=30, params=dict(
            part="statistics,snippet", id=",".join(idlist[i:i + 50]), key=key))
        r.raise_for_status()
        for it in r.json().get("items", []):
            views = int(it["statistics"].get("viewCount", 0))
            pub = datetime.fromisoformat(it["snippet"]["publishedAt"].replace("Z", "+00:00"))
            age = max(1, (now - pub).days)
            out.append({"titulo": it["snippet"]["title"], "canal": it["snippet"]["channelTitle"],
                        "views": views, "views_por_dia": round(views / age), "dias": age})
    out.sort(key=lambda x: x["views_por_dia"], reverse=True)
    return out[:30]


def generate_ideas(llm, cfg):
    ch = cfg["channel"]
    if llm.mock:
        videos = [{"titulo": "vídeo simulado", "canal": "x", "views": 1, "views_por_dia": 1, "dias": 1}]
    else:
        if not cfg["research"]["youtube_queries"]:
            raise SystemExit("Preencha research.youtube_queries no config.yaml (termos de busca do nicho).")
        videos = youtube_outliers(cfg)
    system = prompt("research_ideas", niche=ch["niche"], language=ch["language"])
    user = json.dumps(videos, ensure_ascii=False, indent=1)
    return llm.ask_json("ideas", system, user, max_tokens=3000, mock_reply=mocks.IDEAS), videos


def research_topic(llm, cfg, topic):
    system = prompt("research_topic", topic=topic, language=cfg["channel"]["language"])
    return llm.ask("research", system, f"Tema: {topic}", max_tokens=4000, web=True, mock_reply=mocks.NOTES)


def make_angle(llm, cfg, topic, notes):
    """Ponto de vista próprio do vídeo, definido antes do roteiro (exigência prática da política de conteúdo inautêntico)."""
    system = prompt("angle", language=cfg["channel"]["language"])
    return llm.ask("angle", system, f"Tema: {topic}\n\nNOTAS:\n{notes}", max_tokens=1500,
                   mock_reply=mocks.ANGLE).strip()
