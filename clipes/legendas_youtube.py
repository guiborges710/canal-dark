"""Transcrição RÁPIDA pela legenda automática do YouTube (sem Whisper, sem token): segundos em vez de horas.

  python -m clipes legendas <slug> [--lang pt-orig] [--forcar]

Baixa a legenda automática (json3, com tempo por palavra), converte para o mesmo formato de `transcricao.json` e marca a
etapa como concluída. Serve para vídeo muito longo: a triagem do Rivaldo e a escolha dos momentos usam esta transcrição, e
o Whisper (etapa `transcricao.refino`) retranscreve só os trechos ESCOLHIDOS, que é o que aparece na legenda do corte.

Limites: depende de o vídeo ter legenda automática; a qualidade é a do YouTube (pode errar nomes e gírias; algumas
legendas vêm sem pontuação, o que enfraquece os critérios de início e fim de frase do código).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import estado as E

PAUSA_SEGMENTO = 0.6   # pausa que fecha um trecho
MAX_PALAVRAS = 28      # trecho nunca passa disso


def baixar(d: Path, url: str, lang: str = "pt-orig") -> Path:
    pasta = Path(d) / "legenda_youtube"
    pasta.mkdir(exist_ok=True)
    alvo = next(pasta.glob("*.json3"), None)
    if alvo:
        return alvo
    subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", "--skip-download", "--write-auto-subs",
                    "--sub-langs", lang, "--sub-format", "json3", "-o", str(pasta / "leg"), url],
                   check=False, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    alvo = next(pasta.glob("*.json3"), None)
    if not alvo:
        raise SystemExit(f"este vídeo não tem legenda automática '{lang}'. Use a transcrição normal (Whisper).")
    return alvo


def converter(j3: dict) -> list[dict]:
    """json3 do YouTube -> segmentos {ini, fim, texto, palavras} (o mesmo formato do Whisper)."""
    palavras: list[dict] = []
    for ev in j3.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        base = ev.get("tStartMs", 0)
        fim_ev = (base + ev.get("dDurationMs", 0)) / 1000
        for s in segs:
            t = s.get("utf8", "")
            if not t.strip():  # "\n" e vazios
                continue
            palavras.append({"ini": (base + s.get("tOffsetMs", 0)) / 1000, "t": t.strip(), "_fim_ev": fim_ev})
    palavras.sort(key=lambda w: w["ini"])
    limpas: list[dict] = []
    for w in palavras:  # legenda "rolante" às vezes repete a mesma palavra quase no mesmo instante
        if limpas and limpas[-1]["t"] == w["t"] and w["ini"] - limpas[-1]["ini"] < 0.25:
            continue
        limpas.append(w)
    for k, w in enumerate(limpas):
        prox = limpas[k + 1]["ini"] if k + 1 < len(limpas) else w["_fim_ev"]
        w["fim"] = round(min(max(prox, w["ini"] + 0.08), w["ini"] + 1.2), 3)
        w["ini"] = round(w["ini"], 3)
        del w["_fim_ev"]
    segmentos: list[dict] = []
    atual: list[dict] = []

    def fecha() -> None:
        if atual:
            segmentos.append({"ini": atual[0]["ini"], "fim": atual[-1]["fim"], "texto": " ".join(w["t"] for w in atual),
                              "palavras": [dict(w) for w in atual]})
            atual.clear()

    for w in limpas:
        if atual and (w["ini"] - atual[-1]["fim"] >= PAUSA_SEGMENTO or atual[-1]["t"][-1:] in ".?!"
                      or len(atual) >= MAX_PALAVRAS):
            fecha()
        atual.append(w)
    fecha()
    return segmentos


def importar(d: Path, lang: str = "pt-orig", forcar: bool = False) -> dict:
    d = Path(d)
    alvo = d / "transcricao.json"
    if alvo.exists() and not forcar:
        raise SystemExit("este projeto já tem transcricao.json (use --forcar para trocar pela legenda do YouTube).")
    fonte = json.loads((d / "fonte.json").read_text(encoding="utf-8"))
    url = fonte.get("origem", "")
    if not url.startswith(("http://", "https://")):
        raise SystemExit("a fonte não é um link do YouTube; não há legenda para baixar.")
    E.marcar(d, "transcricao", "trabalhando", "baixando a legenda automática do YouTube", "Código", progresso=0.3)
    arq = baixar(d, url, lang)
    segs = converter(json.loads(arq.read_text(encoding="utf-8")))
    if not segs:
        raise SystemExit("a legenda veio vazia.")
    out = {"idioma": "pt" if lang.startswith("pt") else lang.split("-")[0], "origem": f"legenda_youtube_{lang}",
           "segmentos": segs}
    alvo.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    minutos = segs[-1]["fim"] / 60
    E.marcar(d, "transcricao", "concluido",
             f"legenda automática do YouTube: {len(segs)} trechos, {minutos:.0f} min (Whisper só nos cortes escolhidos)")
    print(f"[legendas] {len(segs)} trechos, {minutos:.1f} min, idioma {out['idioma']}.")
    return out
