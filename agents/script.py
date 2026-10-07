"""Roteirista (modelo 'writer') + revisor (modelo 'reviewer')."""
from . import mocks
from .common import prompt


def target_words(cfg):
    return int(cfg["channel"]["minutes"] * 150)  # ~150 palavras por minuto de fala


def write_script(llm, cfg, topic, notes, angle=""):
    ch = cfg["channel"]
    system = prompt("writer", topic=topic, niche=ch["niche"], language=ch["language"],
                    minutes=ch["minutes"], words=target_words(cfg))
    user = f"NOTAS (fatos pesquisados):\n{notes}"
    if angle:
        user += f"\n\nÂNGULO EDITORIAL:\n{angle}"
    return llm.ask("writer", system, user, max_tokens=6000, mock_reply=mocks.SCRIPT).strip()


def review_script(llm, cfg, notes, script, angle=""):
    system = prompt("reviewer", words=target_words(cfg))
    user = f"NOTAS:\n{notes}\n\nÂNGULO EDITORIAL:\n{angle or '(não há)'}\n\nROTEIRO:\n{script}"
    res = llm.ask_json("reviewer", system, user, max_tokens=7000, mock_reply=mocks.REVIEW)
    final = (res.get("roteiro_revisado") or script).strip()
    return final, res
