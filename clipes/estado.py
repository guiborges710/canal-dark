"""Estado do fluxo de um projeto de clipes (alimenta o painel visual).

Cada projeto tem clipes_out/<slug>/estado.json:
  {"nos": {no: {"status", "msg", "agente", "ini", "fim"}}, "eventos": [{"t","no","status","msg"}]}

Quem muda o estado: o código do pipeline (automático) e os agentes do setor, pelo comando
  python -m clipes estado <slug> <no> <status> "mensagem" [--agente zidane]
Status: pendente | trabalhando | concluido | espera_voce | bloqueado | falhou
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

STATUS = ("pendente", "trabalhando", "concluido", "espera_voce", "bloqueado", "falhou")

# Fluxo do setor: id, agente responsável (craque), título, nó anterior (para as setas).
FLUXO = [
    {"id": "fonte", "agente": "Salah", "titulo": "Achar e registrar a fonte", "de": None},
    {"id": "autorizacao", "agente": "Salah", "titulo": "Confirmar a autorização", "de": "fonte"},
    {"id": "transcricao", "agente": "Código", "titulo": "Transcrever a fala", "de": "autorizacao"},
    {"id": "triagem", "agente": "Rivaldo", "titulo": "Avaliar se a fonte vale clipar", "de": "transcricao"},
    {"id": "momentos", "agente": "Kaká", "titulo": "Escolher os melhores momentos", "de": "triagem"},
    {"id": "comentario", "agente": "Zidane", "titulo": "Escrever o comentário próprio", "de": "momentos"},
    {"id": "gancho", "agente": "Figo", "titulo": "Achar o gancho e abrir o corte com ele", "de": "comentario"},
    {"id": "corte", "agente": "Código", "titulo": "Cortar em 9:16 com legenda", "de": "gancho"},
    {"id": "potencial", "agente": "Totti", "titulo": "Avaliar o potencial de cada corte", "de": "corte"},
    {"id": "originalidade", "agente": "Buffon", "titulo": "Auditar originalidade e regras", "de": "potencial"},
    {"id": "embalagem", "agente": "Lewandowski", "titulo": "Título, descrição e hashtags", "de": "originalidade"},
    {"id": "aprovacao", "agente": "Guilherme", "titulo": "Aprovar e postar (manual)", "de": "embalagem"},
    {"id": "saida", "agente": "Pelé", "titulo": "Pacote pronto", "de": "aprovacao"},
]
NOS = {n["id"]: n for n in FLUXO}
# V2: etapas do catálogo configurável (clipes/etapas.py) também são nós válidos.
from .etapas import CATALOGO as _CAT  # noqa: E402

for _e in _CAT:
    NOS.setdefault(_e["id"], {"id": _e["id"], "agente": _e["agente"], "titulo": _e["titulo"], "de": None})
_trava = threading.Lock()


def _caminho(d: Path) -> Path:
    return Path(d) / "estado.json"


def ler(d: Path) -> dict:
    p = _caminho(d)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return {"nos": {n["id"]: {"status": "pendente", "msg": "", "agente": n["agente"]} for n in FLUXO},
            "eventos": []}


def marcar(d: Path, no: str, status: str, msg: str = "", agente: str | None = None,
           detalhe: list[str] | None = None, resolver: str = "", progresso: float | None = None) -> None:
    """`detalhe` e `resolver` explicam um bloqueio ou falha (o painel mostra na caixa de Problemas).
    `progresso` (0 a 1) só deve ser informado quando o andamento é medido de verdade; sem ele o painel
    mostra um indicador indeterminado."""
    if no not in NOS:
        raise SystemExit(f"nó desconhecido: {no!r}. Use: {', '.join(NOS)}")
    if status not in STATUS:
        raise SystemExit(f"status inválido: {status!r}. Use: {', '.join(STATUS)}")
    with _trava:
        e = ler(d)
        agora = time.time()
        n = e["nos"].setdefault(no, {"agente": NOS[no]["agente"]})
        if status == "trabalhando" and n.get("status") != "trabalhando":
            n["ini"] = agora
        if status in ("concluido", "bloqueado", "falhou"):
            n["fim"] = agora
        n.update(status=status, msg=msg, agente=agente or n.get("agente") or NOS[no]["agente"])
        if status == "trabalhando" and progresso is not None:
            n["progresso"] = round(max(0.0, min(1.0, float(progresso))), 3)
        else:
            n.pop("progresso", None)
        if status in ("bloqueado", "falhou"):
            n["detalhe"], n["resolver"] = list(detalhe or []), resolver
        else:
            n.pop("detalhe", None)
            n.pop("resolver", None)
        e["eventos"].append({"t": agora, "no": no, "status": status, "msg": msg,
                             "agente": n["agente"], **({"detalhe": detalhe} if detalhe else {})})
        e["eventos"] = e["eventos"][-200:]
        tmp = _caminho(d).with_suffix(".tmp")
        tmp.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, _caminho(d))
