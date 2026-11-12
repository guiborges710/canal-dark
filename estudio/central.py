"""Central de Programação (MVP): lê programacao/quadro.md e sprints/sprint-NN.md, cruza com os jobs do Corte e registra pedidos.
Não executa agentes: os botões gravam um pedido em programacao/pedidos.jsonl (quem roda é o Xavi/Guilherme)."""
import json
import re
from datetime import datetime

from .banco import varios
from .config import REPO

PROG = REPO / "programacao"
PEDIDOS = PROG / "pedidos.jsonl"
PAUSAS = PROG / "pausas.json"
SETORES = [
    {"id": "programacao", "nome": "Programação", "ativo": True},
    {"id": "inteligencia", "nome": "Inteligência", "ativo": False},
    {"id": "producao", "nome": "Produção", "ativo": False},
    {"id": "pessoal", "nome": "Pessoal", "ativo": False},
]
AGENTES = ["zico-po-programacao", "xavi-scrum-master", "ancelotti-agile-coach", "thiago-silva-tech-lead", "rodrygo-dev-back",
           "endrick-dev-front", "iniesta-ux-corte", "alisson-qa", "marquinhos-devops-release"]


def _da_fonte_unica():
    """Fonte única: ecossistema/setores.json. Se faltar ou estiver quebrado, valem as listas acima (comportamento de antes)."""
    global SETORES, AGENTES
    try:
        d = json.loads((REPO / "ecossistema" / "setores.json").read_text(encoding="utf-8"))
        setores = [{"id": s["id"], "nome": s["nome"], "ativo": bool(s.get("ativo"))} for s in d["setores"]]
        prog = next(s for s in d["setores"] if s["id"] == "programacao")
        agentes_prog = [a["id"] if isinstance(a, dict) else a for a in prog["agentes"]]
        if setores and agentes_prog:
            SETORES, AGENTES = setores, agentes_prog
    except (OSError, ValueError, KeyError, TypeError, StopIteration):
        pass


_da_fonte_unica()
COLUNAS = ["Fazendo", "Em teste", "Bloqueado", "Feito"]
ACOES = {"rodar_daily": "Rodar Daily", "abrir_planning": "Abrir Planning"}


def _ler(p):
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def _pausas():
    try:
        return json.loads(_ler(PAUSAS) or "{}")
    except ValueError:
        return {}


def sprint_ativa():
    arqs = sorted((PROG / "sprints").glob("sprint-[0-9]*.md"))
    if not arqs:
        return {"erro": "Nenhuma sprint encontrada."}
    t = _ler(arqs[-1])
    nome = (re.match(r"#\s*(.+)", t) or [None, arqs[-1].stem])[1].strip()
    estado = re.search(r"Estado:\s*\*\*([^*]+)\*\*", t)
    per = re.search(r"\((\d{2}/\d{2}) a (\d{2}/\d{2})", t)
    meta = re.search(r"## Meta\s+(.+)", t)
    return {"nome": nome, "estado": estado.group(1) if estado else "?", "inicio": per.group(1) if per else None,
            "fim": per.group(2) if per else None, "meta": meta.group(1).strip() if meta else "", "arquivo": arqs[-1].name}


def quadro():
    t = _ler(PROG / "quadro.md")
    pausas = _pausas()
    cols = {c: [] for c in COLUNAS}
    for m in re.finditer(r"^## ([^\n(]+?)\s*(?:\(.*)?$\n(.*?)(?=^## |\Z)", t, re.S | re.M):
        nome = m.group(1).strip()
        if nome not in cols:
            continue
        for ln in m.group(2).splitlines():
            it = re.match(r"-\s*\[(PROG-\d+)\]\s*(.*)", ln)
            if it:
                pessoas = sorted(set(re.findall(r"\*\*([A-ZÀ-Ú][\wÀ-ú ]+)\*\*", it.group(2))))
                cols[nome].append({"id": it.group(1), "texto": it.group(2), "pessoas": pessoas, "pausado": it.group(1) in pausas})
    wip = {"Fazendo": "2 por dev", "Em teste": "3 no total"}
    return {"colunas": [{"nome": c, "wip": wip.get(c), "n": len(cols[c]), "itens": cols[c]} for c in COLUNAS], "pausas": pausas}


def agentes():
    """Estado por agente a partir dos jobs do Corte (craque). 'autorizacao' e 'prompt' só existem se o job os registrar."""
    jobs = varios("SELECT id, craque, titulo, status, spec, motor, criada_em, iniciado_em, terminado_em FROM jobs ORDER BY id DESC LIMIT 400")
    saida = []
    for ident in AGENTES:
        curto = ident.split("-")[0]
        meus = [j for j in jobs if j["craque"] and curto in j["craque"].lower().replace(" ", "-")]
        ult = meus[0] if meus else None
        ativo = next((j for j in meus if j["status"] in ("rodando", "fila")), None)
        estado = "parado"
        if ativo:
            estado = "rodando" if ativo["status"] == "rodando" else "esperando (fila)"
        saida.append({"id": ident, "estado": estado, "job": (ativo or ult or {}).get("id"), "titulo": (ativo or ult or {}).get("titulo"),
                      "motor": (ativo or ult or {}).get("motor"), "atualizado": (ult or {}).get("terminado_em") or (ult or {}).get("iniciado_em"),
                      "precisa_autorizar": False})
    return saida


def agente(ident):
    base = next((a for a in agentes() if a["id"] == ident), None)
    if not base:
        return {"erro": "Agente fora do setor."}
    prompt = None
    if base["job"]:
        j = varios("SELECT spec FROM jobs WHERE id=?", base["job"])
        try:
            spec = json.loads(j[0]["spec"]) if j else {}
            prompt = spec.get("prompt") or spec.get("entrada") or json.dumps(spec, ensure_ascii=False)[:2000]
        except (ValueError, TypeError):
            prompt = None
    return {**base, "prompt": prompt, "pedidos": [p for p in pedidos() if p.get("agente") in (None, ident)][-5:], "agora": datetime.now().isoformat(timespec="seconds")}


def pedidos():
    out = []
    for ln in _ler(PEDIDOS).splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def _registrar(tipo, **extra):
    PROG.mkdir(exist_ok=True)
    p = {"tipo": tipo, "em": datetime.now().isoformat(timespec="seconds"), "status": "pendente", **extra}
    with PEDIDOS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")
    return p


def acao(tipo, d):
    if tipo in ACOES:
        return _registrar(tipo, rotulo=ACOES[tipo], agente="xavi-scrum-master")
    if tipo in ("pausar", "retomar"):
        item = str(d.get("item", ""))
        if not re.fullmatch(r"PROG-\d+", item):
            raise ValueError("Item inválido.")
        pausas = _pausas()
        if tipo == "pausar":
            pausas[item] = datetime.now().isoformat(timespec="seconds")
        else:
            pausas.pop(item, None)
        PAUSAS.write_text(json.dumps(pausas, ensure_ascii=False, indent=1), encoding="utf-8")
        return _registrar(tipo, item=item, status="aplicado")
    raise ValueError("Ação desconhecida.")
