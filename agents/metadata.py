"""Título, descrição, tags e prompt da thumbnail."""
from . import mocks
from .common import prompt


def make_metadata(llm, cfg, script):
    system = prompt("metadata", language=cfg["channel"]["language"])
    return llm.ask_json("metadata", system, f"ROTEIRO:\n{script}", max_tokens=1500, mock_reply=mocks.METADATA)
