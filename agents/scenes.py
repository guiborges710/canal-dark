"""Divide o roteiro em cenas (por código, sem inventar texto) e pede prompts de imagem ao Claude."""
import json
import re

from .common import prompt


def split_scenes(script, min_words=10):
    sents = [s for s in re.split(r"(?<=[.!?…])\s+", script.replace("\n", " ").strip()) if s]
    scenes, cur = [], []
    for s in sents:
        cur.append(s)
        if sum(len(x.split()) for x in cur) >= min_words:
            scenes.append(" ".join(cur))
            cur = []
    if cur:
        rest = " ".join(cur)
        if scenes and len(rest.split()) < 5:
            scenes[-1] += " " + rest
        else:
            scenes.append(rest)
    return scenes


def _norm(item, topic):
    """Aceita o formato novo (objeto com queries e prompt) e o antigo (só texto)."""
    if isinstance(item, dict):
        p = str(item.get("prompt") or item.get("image_prompt") or f"illustration related to: {topic}")
        q = [str(x) for x in (item.get("queries") or []) if str(x).strip()]
        return p, q[:3]
    return str(item), []


def image_prompts(llm, cfg, texts, topic, batch=30):
    """Devolve, por cena, {'image_prompt', 'search'}. Pede em lotes; se a lista vier com tamanho errado,
    tenta de novo e, por fim, usa um prompt genérico (sem busca de imagem real)."""
    lang = cfg["channel"]["language"]
    style = cfg["channel"]["visual_style"]
    out = []
    for start in range(0, len(texts), batch):
        chunk = texts[start:start + batch]
        system = prompt("scenes", language=lang, n=len(chunk))
        user = (f"Tema do vídeo: {topic}\nEstilo visual do canal: {style}\n\n"
                + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(chunk)))
        mock = json.dumps([{"queries": [f"mock query {start + i + 1}"], "prompt": f"mock scene {start + i + 1}, abstract"}
                           for i in range(len(chunk))])
        got = None
        for _ in range(2):
            res = llm.ask_json("scenes", system, user, max_tokens=6000, mock_reply=mock)
            if isinstance(res, list) and len(res) == len(chunk):
                got = [_norm(x, topic) for x in res]
                break
        if got is None:
            got = [(f"illustration related to: {topic}", []) for _ in chunk]
        out.extend(got)
    return [{"image_prompt": f"{p}, {style}", "search": q} for p, q in out]
