"""PROG-003 (fatia B): quem está trabalhando agora, só leitura. Alimenta GET /api/agentes/ao-vivo.

Custo (nota técnica do Thiago Silva): UMA query em `jobs` por pedido, sem ler log nem `trabalhos.progresso()`.
"Espera você" precisa olhar as produções, então fica em cache de 3 s com trava única (vários clientes não multiplicam o custo).
O tempo vai em segundos calculados aqui; o navegador soma o que passou desde que recebeu e nunca interpreta datas.
"""
import json
import threading
import time
from datetime import datetime

from . import fluxo, materiais as M
from .banco import agora, varios

LIMITE_LONGO_S = 900          # 15 min: decisão 4 da ata
JANELA_CONCLUIDOS_S = 3600    # última hora
CACHE_ESPERA_S = 3.0
MAX_CONCLUIDOS = 30
PRIORIDADE = {"falhou": 0, "espera_voce": 1, "trabalhando": 2, "fila": 3}
TEXTO = {"falhou": "Falhou", "espera_voce": "Espera você", "trabalhando": "Trabalhando", "fila": "Na fila"}
CRAQUE = {e["agente"]: e["craque"] for e in fluxo.ETAPAS if e["agente"]} | {fluxo.BARCOLA[0]: fluxo.BARCOLA[1]}

_trava = threading.Lock()
_cache = {"em": None, "dados": None}


def invalidar_cache():
    with _trava:
        _cache["em"] = None
        _cache["dados"] = None


def _segundos(desde, ref):
    """Segundos entre um carimbo do banco (hora local sem fuso) e `ref` (datetime local). None se não houver ou for ilegível."""
    if not desde:
        return None
    try:
        return max(0, int((ref - datetime.fromisoformat(desde)).total_seconds()))
    except (ValueError, TypeError):
        return None


def _craque(agente, j=None):
    from . import agentes
    return CRAQUE.get(agente) or (j or {}).get("craque") or agentes.nome_curto(agente)


def _ativo(agente):
    from . import agentes
    return (agentes.ATIVOS / f"{agente}.md").exists()


def _titulo_video(slug, tema=None):
    meta = M.ler_json(M.pasta(slug) / "metadados.json", {}) or {}
    t = meta.get("titulo") if isinstance(meta, dict) else None
    return t or tema or slug.replace("-", " ").capitalize()


def _etapa_nome(etapa, origem):
    if origem == "teste_agente":
        return "Teste de agente"
    e = fluxo.POR_ID.get(etapa)
    return e["nome"] if e else etapa


def _jobs(agora_dt):
    """A única consulta: ativos, falhos ainda abertos e concluídos na última hora."""
    corte = datetime.fromtimestamp(agora_dt.timestamp() - JANELA_CONCLUIDOS_S).isoformat(timespec="seconds")
    return varios(
        "SELECT j.id, j.slug, j.etapa, j.titulo, j.craque, j.status, j.spec, j.erro, j.motor, j.motor_nota, j.criada_em, j.iniciado_em, j.terminado_em, "
        "p.tema AS tema, (SELECT 1 FROM execucoes e WHERE e.slug = j.slug LIMIT 1) AS em_grafo "
        "FROM jobs j LEFT JOIN producoes p ON p.slug = j.slug "
        "WHERE j.status IN ('fila', 'rodando') "
        "OR (j.status = 'falhou' AND j.dispensado = 0 AND NOT EXISTS (SELECT 1 FROM jobs k WHERE k.slug = j.slug AND k.etapa = j.etapa "
        "AND k.id > j.id AND k.status IN ('ok', 'falhou', 'cancelado'))) "
        "OR (j.status = 'ok' AND j.terminado_em > ?) "
        "ORDER BY j.id", corte)


def _trabalho(j, spec, estado, ref, posicao=None):
    origem = spec.get("origem")
    segundos = _segundos(j["iniciado_em"], ref) if estado == "trabalhando" else None
    erro = None
    if estado == "falhou" and j["erro"]:
        erro = (str(j["erro"]).strip().splitlines() or [""])[0][:160] or None
    return {
        "job_id": j["id"], "slug": j["slug"], "titulo_video": _titulo_video(j["slug"], j["tema"]), "etapa_id": j["etapa"],
        "etapa_nome": _etapa_nome(j["etapa"], origem), "estado": estado, "motor": _motor(j), "motor_nota": j["motor_nota"] or None,
        "segundos_na_tarefa": segundos, "aguarda_s": _segundos(j["criada_em"], ref) if estado == "fila" else None,
        "posicao_fila": posicao, "erro_curto": erro,
        "origem": "teste_agente" if origem == "teste_agente" else ("grafo" if j["em_grafo"] else "estudio"),
        "alerta_longo": segundos is not None and segundos >= LIMITE_LONGO_S}


def _motor(j):
    """Mesma regra de status_job_publico, sem ler disco quando o job já traz o motor (job antigo sem motor: None, nunca texto)."""
    if j["motor"]:
        return j["motor"]
    try:
        from . import trabalhos
        return trabalhos.motor_do_job(j)
    except Exception:
        return None


def _espera_voce(ref):
    """{agente: [trabalho]} das etapas que aguardam decisão. Em cache de 3 s, com trava única."""
    with _trava:
        agora_m = time.monotonic()
        if _cache["em"] is not None and agora_m - _cache["em"] < CACHE_ESPERA_S:
            return _cache["dados"]
        saida, parcial = {}, False
        for p in varios("SELECT slug, tema FROM producoes WHERE arquivada = 0"):
            try:
                ctx = fluxo.Contexto(p["slug"])
                for e in fluxo.ETAPAS:
                    if ctx.etapa_status(e) != "aguardando":
                        continue
                    ultimo = next((j for j in ctx.jobs if j["etapa"] == e["id"]), None)
                    spec = {}
                    try:
                        spec = json.loads(ultimo["spec"]) if ultimo else {}
                    except ValueError:
                        pass
                    agente = spec.get("agente") or fluxo._agente_de(ctx, e)[0]
                    if not agente:
                        continue
                    base = ultimo or {"id": None, "slug": p["slug"], "etapa": e["id"], "craque": None, "erro": None, "motor": None, "motor_nota": None, "criada_em": None, "iniciado_em": None, "terminado_em": None, "tema": p["tema"], "em_grafo": ctx.em_grafo, "spec": "{}"}
                    base = dict(base, tema=p["tema"], em_grafo=ctx.em_grafo)
                    t = _trabalho(base, spec, "espera_voce", ref)
                    t["aguarda_s"] = _segundos(base["terminado_em"], ref)
                    saida.setdefault(agente, []).append(t)
            except Exception:
                parcial = True  # uma produção ilegível não derruba o painel
        _cache["em"], _cache["dados"] = agora_m, (saida, parcial)
        return _cache["dados"]


def montar(agora_dt=None):
    ref = agora_dt or datetime.now()
    jobs = _jobs(ref)
    trabalhos_por_agente, concluidos, ignorados = {}, [], 0
    fila = [j for j in jobs if j["status"] == "fila"]
    posicao = {j["id"]: i + 1 for i, j in enumerate(fila)}
    for j in jobs:
        try:
            spec = json.loads(j["spec"])
        except ValueError:
            spec = {}
        agente = spec.get("agente")
        if not agente:
            ignorados += 1
            continue
        if j["status"] == "ok":
            ha = _segundos(j["terminado_em"], ref)
            concluidos.append({"agente": agente, "craque": _craque(agente, j), "slug": j["slug"], "etapa_nome": _etapa_nome(j["etapa"], spec.get("origem")),
                               "motor": _motor(j), "terminou_ha_s": ha, "_ordem": j["id"]})
            continue
        estado = {"fila": "fila", "rodando": "trabalhando", "falhou": "falhou"}[j["status"]]
        trabalhos_por_agente.setdefault(agente, []).append(_trabalho(j, spec, estado, ref, posicao.get(j["id"])))
    espera, parcial = _espera_voce(ref)
    for agente, itens in espera.items():
        trabalhos_por_agente.setdefault(agente, []).extend(dict(t) for t in itens)
    agentes = []
    for agente, ts in trabalhos_por_agente.items():
        estado = min((t["estado"] for t in ts), key=PRIORIDADE.__getitem__)
        ts.sort(key=lambda t: (PRIORIDADE[t["estado"]], t["job_id"] or 0))
        agentes.append({"id": agente, "craque": _craque(agente), "ativo": _ativo(agente), "estado": estado, "estado_texto": TEXTO[estado], "trabalhos": ts})
    agentes.sort(key=lambda a: (PRIORIDADE[a["estado"]], a["craque"]))
    concluidos.sort(key=lambda c: c.pop("_ordem"), reverse=True)
    resumo = {k: sum(1 for a in agentes if a["estado"] == k) for k in ("trabalhando", "fila", "falhou", "espera_voce")} | {"ignorados": ignorados}
    return {"gerado_em": agora(), "servidor_s": time.time(), "resumo": resumo, "agentes": agentes, "concluidos_1h": concluidos[:MAX_CONCLUIDOS],
            "frescor": "parcial" if parcial else "ok"}
