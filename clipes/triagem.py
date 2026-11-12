"""Triagem da FONTE (Rivaldo): dados objetivos sobre o vídeo longo, medidos pelo código, antes de qualquer corte.

O agente Rivaldo lê `triagem_dados.json` (este módulo) + a transcrição e decide se o vídeo vale ser clipado,
gravando `triagem.json` (nota 0-100, recomendação, momentos promissores). Aqui só há medição; nenhum julgamento
editorial além do que o seletor editorial já faz. Nada depende de tema ou idioma (usa os pacotes do editorial).

  python -m clipes triagem-dados <slug>      # (re)calcula triagem_dados.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from . import editorial as ED
from . import perfis as PF

CAMPOS_TRIAGEM = ("nota", "veredito", "recomendacao", "formato", "motivos", "riscos", "sugestoes", "momentos_promissores")
RECOMENDACOES = ("seguir", "seguir_com_ressalvas", "nao_vale")


def _ler(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def coletar(d: Path) -> dict:
    """Mede a fonte e grava triagem_dados.json. Rápido (sem áudio, sem render)."""
    d = Path(d)
    tr = _ler(d / "transcricao.json")
    segs = tr["segmentos"]
    perfil = PF.do_projeto(d)
    fonte = _ler(d / "fonte.json") if (d / "fonte.json").exists() else {}
    dur = max((s["fim"] for s in segs), default=0.0)
    try:  # duração real do arquivo, se o vídeo estiver aí
        import subprocess
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(d / "fonte.mp4")], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                   check=True).stdout.strip())
    except Exception:  # noqa: BLE001 - a duração da transcrição basta
        pass
    palavras = sum(len(s["texto"].split()) for s in segs)
    fala_s = sum(max(s["fim"] - s["ini"], 0) for s in segs)
    pausas_longas = sum(1 for a, b in zip(segs, segs[1:]) if b["ini"] - a["fim"] >= 2.0)
    curtos = sum(1 for s in segs if len(s["texto"].split()) <= 3)
    ED._definir(tr.get("idioma"))
    us = ED.unidades(segs)
    janelas = [segs[i: i + 30] for i in range(0, len(segs), 30)]
    ruidosas = sum(1 for j in janelas if ED.ruidosa(" ".join(s["texto"] for s in j)))
    cota = 40  # amostra ampla de candidatos íntegros (não é a cota de cortes do perfil)
    momentos, rel = ED.selecionar(segs, perfil, np.zeros(1), cota, energia=False, usar_termos=True,
                                  dur_video=dur or None, idioma=tr.get("idioma"))
    assuntos: dict[str, list] = {}
    for m in momentos:
        assuntos.setdefault((m.get("serie") or {}).get("id") or f"u{m['id']}", []).append(m)
    top = sorted(assuntos.values(), key=lambda g: max(x["score"] for x in g), reverse=True)[:12]

    def texto(m: dict) -> str:
        ws = [w["t"] for s in segs for w in s.get("palavras", []) if m["ini"] <= w["ini"] < m["fim"]]
        return " ".join(ws)[:420]

    cand = []
    for g in top:
        m0 = g[0]
        cand.append({"ini": round(g[0]["ini"], 1), "fim": round(g[-1]["fim"], 1), "dur": round(g[-1]["fim"] - g[0]["ini"], 1),
                     "nota_codigo": round(max(x["score"] for x in g), 2), "partes": len(g) if m0.get("serie") else 1,
                     "avaliacao": m0["avaliacao"], "justificativa": m0["justificativa"], "texto": texto(m0)})
    minutos = max(dur / 60.0, 0.1)
    fortes = [c for c in cand if c["nota_codigo"] >= 0.65]
    dados = {
        "slug": d.name, "origem": fonte.get("origem"), "autor": fonte.get("autor"), "titulo_original": fonte.get("titulo_original"),
        "duracao_min": round(minutos, 1), "idioma": tr.get("idioma"), "perfil": {"id": perfil["id"], "nome": perfil["nome"]},
        "fala": {"palavras_por_min": round(palavras / minutos, 1), "fala_pct": round(100 * fala_s / max(dur, 1), 1),
                 "pausas_longas_2s": pausas_longas, "falas_picadas_pct": round(100 * curtos / max(len(segs), 1), 1),
                 "trechos_ruidosos_pct": round(100 * ruidosas / max(len(janelas), 1), 1),
                 "perguntas_reais": sum(1 for u in us if u["pergunta"])},
        "seletor": {"candidatos_integros": rel["candidatos_integros"], "assuntos_selecionados": len(assuntos),
                    "series_possiveis": rel.get("series", 0), "descartes": rel["descartes"],
                    "momentos_fortes": len(fortes), "momentos_fortes_por_10min": round(len(fortes) / minutos * 10, 2)},
        "candidatos": cand,
        "nota": "Medições do código (seletor editorial, sem áudio). Notas do código são heurísticas de comparação, "
                "não previsão de alcance; o julgamento do Rivaldo vem da leitura da transcrição.",
    }
    (d / "triagem_dados.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return dados


def validar(d: Path, desde: float = 0.0) -> str:
    """'' se triagem.json está completo e é desta rodada; senão o que falta (o orquestrador mostra no painel)."""
    p = Path(d) / "triagem.json"
    if not p.exists():
        return "triagem.json não foi gravado"
    if p.stat().st_mtime < desde - 1:
        return "triagem.json é de uma rodada anterior"
    try:
        t = _ler(p)
    except ValueError:
        return "triagem.json ilegível"
    falta = [c for c in CAMPOS_TRIAGEM if c not in t]
    if falta:
        return "triagem.json sem os campos " + ", ".join(falta)
    try:
        nota = float(t["nota"])
    except (TypeError, ValueError):
        return "nota não numérica"
    if not 0 <= nota <= 100:
        return "nota fora de 0 a 100"
    if t["recomendacao"] not in RECOMENDACOES:
        return "recomendacao deve ser " + "|".join(RECOMENDACOES)
    for m in t.get("momentos_promissores") or []:
        try:
            if not 0 <= float(m["nota"]) <= 100:
                return "cada momento promissor precisa de nota de 0 a 100 (passo 4 do Rivaldo)"
        except (KeyError, TypeError, ValueError):
            return "cada momento promissor precisa de nota de 0 a 100 (passo 4 do Rivaldo)"
        if not (isinstance(m, dict) and re.fullmatch(r"-?\d+(\.\d+)?", str(m.get("ini", ""))) and
                re.fullmatch(r"-?\d+(\.\d+)?", str(m.get("fim", ""))) and float(m["fim"]) > float(m["ini"])):
            return "momentos_promissores precisam de ini e fim em segundos (fim > ini)"
    return ""


def melhores(d: Path) -> list[dict]:
    """Momentos promissores ordenados da MAIOR nota para a menor (o código ordena; não depende da ordem do agente)."""
    t = _ler(Path(d) / "triagem.json")
    ms = [m for m in (t.get("momentos_promissores") or []) if isinstance(m, dict) and "nota" in m]
    return sorted(ms, key=lambda m: float(m["nota"]), reverse=True)
