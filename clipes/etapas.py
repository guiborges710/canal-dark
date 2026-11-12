"""Catálogo de etapas e ferramentas do setor de Clipes (V2) e o fluxo configurável de cada projeto.

Cada etapa diz quem executa (código, agente do Claude Code ou você), se é obrigatória, de quais
etapas depende (`depende`: precisam estar ativas e antes) e quais etapas, se ativas, precisam vir
antes dela (`depois_de`). O fluxo do projeto fica em clipes_out/<slug>/fluxo.json:

  {"versao": 2, "etapas": [{"id": "curadoria", "ativa": true, "ferramentas": {...}}, ...]}

A ordem da lista é a ordem de execução. Projeto sem fluxo.json (anterior à V2) usa o fluxo da V1:
só as etapas de código rodam sozinhas; os agentes continuam pelo Pelé.

Ferramentas: só capacidades implementadas aqui (CAPACIDADES). Adicionar uma nova exige integração
real no código; o painel não instala nada.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

PADRAO = Path(__file__).resolve().parent / "fluxo_padrao.json"

# executor: "codigo" (Python/ffmpeg), "agente" (claude -p --agent), "humano" (espera você no painel)
CATALOGO = [
    {"id": "fonte", "agente": "Salah", "titulo": "Baixar e registrar a fonte", "executor": "codigo",
     "obrigatoria": True, "depende": [], "depois_de": []},
    {"id": "autorizacao", "agente": "Salah", "titulo": "Registrar a autorização", "executor": "codigo",
     "obrigatoria": True, "depende": ["fonte"], "depois_de": []},
    {"id": "transcricao", "agente": "Código", "titulo": "Transcrever a fala", "executor": "codigo",
     "obrigatoria": True, "depende": ["fonte"], "depois_de": ["autorizacao"]},
    {"id": "triagem", "agente": "Rivaldo", "titulo": "Avaliar se a fonte vale clipar", "executor": "agente",
     "agente_id": "rivaldo-avaliador-fonte", "obrigatoria": False, "depende": ["transcricao"], "depois_de": []},
    {"id": "momentos", "agente": "Código", "titulo": "Sugerir momentos pelo perfil", "executor": "codigo",
     "obrigatoria": True, "depende": ["transcricao"], "depois_de": ["triagem"]},
    {"id": "curadoria", "agente": "Kaká", "titulo": "Revisar as sugestões (agente)", "executor": "agente",
     "agente_id": "kaka-cacador-momentos", "obrigatoria": False, "depende": ["momentos"], "depois_de": []},
    {"id": "revisao", "agente": "Guilherme", "titulo": "Aceitar ou rejeitar as sugestões", "executor": "humano",
     "obrigatoria": False, "depende": ["momentos"], "depois_de": ["curadoria"]},
    {"id": "comentario", "agente": "Zidane", "titulo": "Escrever o comentário próprio", "executor": "agente",
     "agente_id": "zidane-editor-cortes", "obrigatoria": False, "depende": ["momentos"],
     "depois_de": ["curadoria", "revisao"]},
    {"id": "revisao_texto", "agente": "Guilherme", "titulo": "Aprovar e editar o texto do Zidane", "executor": "humano",
     "obrigatoria": False, "depende": ["comentario"], "depois_de": ["comentario"]},
    {"id": "gancho", "agente": "Figo", "titulo": "Achar o gancho (teaser)", "executor": "agente",
     "agente_id": "figo-diretor-ganchos", "obrigatoria": False, "depende": ["momentos"],
     "depois_de": ["curadoria", "revisao", "revisao_texto"]},
    {"id": "corte", "agente": "Código", "titulo": "Gerar os cortes", "executor": "codigo",
     "obrigatoria": True, "depende": ["momentos"], "depois_de": ["curadoria", "revisao", "comentario", "revisao_texto", "gancho"]},
    {"id": "potencial", "agente": "Totti", "titulo": "Avaliar o potencial (estimativa)", "executor": "agente",
     "agente_id": "totti-avaliador-potencial", "obrigatoria": False, "depende": ["corte"], "depois_de": []},
    {"id": "originalidade", "agente": "Buffon", "titulo": "Conferir crédito e comentário próprio", "executor": "codigo",
     "obrigatoria": False, "depende": ["corte", "comentario"], "depois_de": ["potencial"]},
    {"id": "embalagem", "agente": "Lewandowski", "titulo": "Textos de postagem", "executor": "codigo",
     "obrigatoria": False, "depende": ["originalidade"], "depois_de": []},
    {"id": "aprovacao", "agente": "Guilherme", "titulo": "Aprovar e postar (manual)", "executor": "humano",
     "obrigatoria": False, "depende": ["corte"], "depois_de": ["potencial", "originalidade", "embalagem"]},
]
POR_ID = {e["id"]: e for e in CATALOGO}

# Capacidades implementadas, por etapa. "escolha": uma entre as opções; "opcional": liga/desliga.
CAPACIDADES = {
    "triagem": [
        {"id": "nota_minima", "nome": "Parar e perguntar a você se a nota da fonte ficar abaixo de", "tipo": "escolha",
         "opcoes": ["0", "30", "45", "60"], "padrao": "45",
         "nota": "0 = nunca parar. O Rivaldo só avalia a fonte; quem decide continuar com uma nota baixa é você."},
        {"id": "melhores_pct", "nome": "Seguir o fluxo só com a MELHOR parte dos destaques da triagem (% deles)", "tipo": "escolha",
         "opcoes": ["0", "20", "30", "50"], "padrao": "30",
         "nota": "O Rivaldo dá nota a cada destaque; seguem só os de maior nota, nessa porcentagem (30% de 10 destaques = 3; no mínimo 1). 0 = não usar a triagem para escolher (o seletor geral decide)."},
    ],
    "transcricao": [
        {"id": "modelo", "nome": "Modelo do Whisper (local, CPU)", "tipo": "escolha",
         "opcoes": ["tiny", "base", "small", "medium"], "padrao": "small",
         "nota": "Maior = mais preciso e mais lento. medium precisa de ~5 GB de RAM livre; não medimos o tempo nesta máquina."},
        {"id": "refino", "nome": "Refinar só os trechos escolhidos com outro modelo", "tipo": "opcional",
         "padrao": False, "opcoes": ["small", "medium"], "nota": "Roda depois da curadoria/revisão, antes do corte."},
    ],
    "momentos": [
        {"id": "energia", "nome": "Medir o volume do áudio (sinal pico de áudio)", "tipo": "opcional", "padrao": True,
         "nota": "Desligado, o pico de áudio não conta (útil em podcast com música alta)."},
        {"id": "termos", "nome": "Contar termos do perfil (palavras-chave, entidades, termos técnicos)",
         "tipo": "opcional", "padrao": True},
    ],
    "corte": [
        {"id": "legenda", "nome": "Legenda palavra a palavra (ASS, queimada no vídeo)", "tipo": "opcional", "padrao": True},
        {"id": "audio", "nome": "Áudio original", "tipo": "opcional", "padrao": True},
    ],
}

# Fluxo V1 (projetos sem fluxo.json): mesmas etapas e ordem de antes; agentes não são disparados.
V1 = ["fonte", "autorizacao", "transcricao", "momentos", "comentario", "gancho", "corte", "potencial",
      "originalidade", "embalagem", "aprovacao"]


def _ferr_padrao(eid: str) -> dict:
    return {c["id"]: c["padrao"] for c in CAPACIDADES.get(eid, [])}


def padrao() -> dict:
    """Fluxo para projetos novos: clipes/fluxo_padrao.json (se houver) ou todas as etapas ativas."""
    if PADRAO.exists():
        try:
            f = json.loads(PADRAO.read_text(encoding="utf-8"))
            if not validar(f):
                return normalizar(f)
        except (OSError, ValueError):
            pass
    return normalizar({"etapas": [{"id": e["id"], "ativa": True} for e in CATALOGO]})


def legado() -> dict:
    f = normalizar({"etapas": [{"id": i, "ativa": True} for i in V1]})
    f["etapas"] = [e for e in f["etapas"] if e["id"] in V1]  # curadoria/revisao não existiam
    f["legado"] = True
    return f


def normalizar(f: dict) -> dict:
    """Completa etapas que faltam (inativas, no lugar do catálogo) e ferramentas com o padrão."""
    vistos, out = set(), []
    for e in (f or {}).get("etapas", []):
        if isinstance(e, dict) and e.get("id") in POR_ID and e["id"] not in vistos:
            vistos.add(e["id"])
            fe = _ferr_padrao(e["id"])
            fe.update({k: v for k, v in (e.get("ferramentas") or {}).items() if k in fe})
            out.append({"id": e["id"], "ativa": bool(e.get("ativa", True)) or POR_ID[e["id"]]["obrigatoria"],
                        "ferramentas": fe})
    for i, c in enumerate(CATALOGO):  # etapa ausente entra logo depois da anterior do catálogo
        if c["id"] not in vistos:
            pos = next((k + 1 for k, e in enumerate(out) if i and e["id"] == CATALOGO[i - 1]["id"]), len(out))
            out.insert(pos, {"id": c["id"], "ativa": c["obrigatoria"], "ferramentas": _ferr_padrao(c["id"])})
    return {"versao": 2, "etapas": out, **({"legado": True} if f.get("legado") else {})}


def validar(f: dict) -> list[str]:
    """Erros em português; lista vazia = fluxo válido."""
    erros = []
    try:
        etapas = normalizar(f)["etapas"]
    except (TypeError, AttributeError):
        return ["Fluxo inválido."]
    ativas = [e["id"] for e in etapas if e["ativa"]]
    pos = {eid: k for k, eid in enumerate(ativas)}
    for eid in ativas:
        c = POR_ID[eid]
        for dep in c["depende"]:
            if dep not in pos:
                erros.append(f"“{c['titulo']}” precisa da etapa “{POR_ID[dep]['titulo']}” ativa.")
            elif pos[dep] > pos[eid]:
                erros.append(f"“{c['titulo']}” precisa vir depois de “{POR_ID[dep]['titulo']}”.")
        for ant in c["depois_de"]:
            if ant in pos and pos[ant] > pos[eid]:
                erros.append(f"“{c['titulo']}” precisa vir depois de “{POR_ID[ant]['titulo']}”.")
    for e in etapas:
        for cap in CAPACIDADES.get(e["id"], []):
            v = e["ferramentas"].get(cap["id"])
            if cap["tipo"] == "escolha" and v not in cap["opcoes"]:
                erros.append(f"{cap['nome']}: escolha uma das opções.")
            if cap["tipo"] == "opcional" and not isinstance(v, bool) and v not in cap.get("opcoes", []):
                erros.append(f"{cap['nome']}: valor inválido.")
    return erros


# ------------------------------------------------------------------ projeto
def do_projeto(d: Path) -> dict:
    p = Path(d) / "fluxo.json"
    if p.exists():
        try:
            return normalizar(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return legado()


def gravar(d: Path, f: dict) -> dict:
    erros = validar(f)
    if erros:
        raise ValueError(erros)
    f = normalizar(f)
    f.pop("legado", None)
    p = Path(d) / "fluxo.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(f, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)
    return f


def gravar_padrao(f: dict) -> dict:
    erros = validar(f)
    if erros:
        raise ValueError(erros)
    f = normalizar(f)
    f.pop("legado", None)
    PADRAO.write_text(json.dumps(f, ensure_ascii=False, indent=2), encoding="utf-8")
    return f


def ativas(d: Path) -> list[dict]:
    """Etapas ativas do projeto, na ordem, com os dados do catálogo e as ferramentas escolhidas."""
    return [{**POR_ID[e["id"]], "ferramentas": e["ferramentas"]} for e in do_projeto(d)["etapas"] if e["ativa"]]


def ativa(d: Path, eid: str) -> bool:
    return any(e["id"] == eid for e in ativas(d))


def ferramenta(d: Path, eid: str, cap: str):
    for e in do_projeto(d)["etapas"]:
        if e["id"] == eid:
            return e["ferramentas"].get(cap, _ferr_padrao(eid).get(cap))
    return _ferr_padrao(eid).get(cap)


def para_painel(d: Path) -> list[dict]:
    """Fluxo no formato do painel (id, agente, titulo, de), só etapas ativas, + 'saida'."""
    out, ant = [], None
    for e in ativas(d):
        out.append({"id": e["id"], "agente": e["agente"], "titulo": e["titulo"], "de": ant, "executor": e["executor"]})
        ant = e["id"]
    out.append({"id": "saida", "agente": "Pelé", "titulo": "Pacote pronto", "de": ant, "executor": "codigo"})
    return out


def catalogo_publico() -> dict:
    return {"etapas": copy.deepcopy(CATALOGO), "capacidades": copy.deepcopy(CAPACIDADES)}
