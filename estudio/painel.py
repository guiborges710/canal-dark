"""Ecossistema do Guilherme (PROG-018 a 023): back-end do painel dentro do Corte. Só lê; nunca escreve no projeto.
Não grava nada em disco (índice só em memória).

Transparência (decisão do Guilherme, 2026-11-09): o painel mostra tudo do ecossistema, inclusive produtividade/ e financas/. Segue fora só o que é segredo
(credenciais, chaves, .env, estado de Telegram/Google, logs/históricos/offsets do Ronaldo), mídia, voz/falas e estudio/dados.
Lista de PERMISSÃO (RAIZES_OK/RAIZ_ARQUIVOS) com bloqueio por cima (PROIBIDO_*); corpo que pareça credencial é omitido.
O endpoint de documento só serve caminho que está no índice; nunca abre pelo texto recebido."""
import hashlib
import json
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path

from . import config

RAIZ = config.REPO  # os testes trocam por uma pasta temporária
EXTENSOES = {".md", ".txt", ".json"}
LIMITE_TEXTO = 60_000  # caracteres servidos por documento
LIMITE_HASH = 2_000_000  # bytes lidos para o hash/varredura de credencial
CACHE_VARREDURA_S = 2.0
CACHE_RESUMO_S = 5.0

# Lista de permissão.
RAIZ_ARQUIVOS = {"CLAUDE.md": "raiz", "README.md": "raiz", "AUDITORIA_E_ARQUITETURA.md": "raiz",
                 "output/messi_assinatura_canal.md": "raiz", "estudio/README.md": "raiz"}
RAIZES_OK = {"ecossistema": "ecossistema", "programacao": "programacao", "inteligencia": "inteligencia", "componentes": "componentes",
             "prompts": "prompts", "produtividade": "produtividade", "financas": "financas", "pesquisa_videos": "pesquisa_videos", "clipes": "clipes", "clipes_out": "clipes", "contas": "contas", "reels": "reels", "tiktok": "reels", "thumbnails": "thumbnails", "referencias": "referencias", "research_notes": "referencias", "reports": "referencias", ".claude/agents": "agentes", ".claude/skills": "skills"}
# Áreas em que só entram documentos de texto (.md e .txt): o .json de estado e de transcrição fica fora.
SO_TEXTO = {"pesquisa_videos", "clipes", "contas", "reels", "thumbnails", "referencias"}
# Bloqueio por cima de tudo (partes do caminho, nome e trechos de nome).
PROIBIDO_PARTES = {"dados", "voz", "falas", ".venv", ".git", "node_modules", "__pycache__", "corte_assets",
                   "_entrada", "_trabalho", "blobs", "jobs", "memory"}
PROIBIDO_NOME = ("client_secret", "token", "senha", "password", "segredo", "credencial")
PROIBIDO_SUFIXO = (".pem", ".key", ".p12", ".pfx")
HIDDEN_OK = re.compile(r"^\.ronaldo_contexto[a-z_]*\.md$")
AREAS = ["raiz", "ecossistema", "programacao", "inteligencia", "produtividade", "financas", "componentes", "prompts", "agentes", "skills", "videos", "pesquisa_videos", "clipes", "contas", "reels", "thumbnails", "referencias"]
CREDENCIAL = re.compile(r"sk-ant-|AIza[0-9A-Za-z_\-]{20,}|Bearer\s+[A-Za-z0-9._\-]{20,}|chat_id\s*[:=]\s*[\"']?-?\d{5,}|token\s*=\s*\S{8,}|senha\s*:\s*\S+|(?:api[_-]?key|secret)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}", re.I)

_trava = threading.RLock()
_cache = {"em": 0.0, "indice": None, "resumo_em": 0.0, "resumo": None}


def _agora():
    return time.time()


def _iso(t):
    return datetime.fromtimestamp(t).isoformat(timespec="seconds") if t else None


# ----------------------------------------------------------------------------- regra de permissão

def area_de(rel):
    """Área do documento se o caminho (relativo, com '/') é permitido; senão None. Função única de confidencialidade."""
    if not rel or "\\" in rel or (rel.startswith(("/", ".")) and not rel.startswith(".claude/")) or ".." in rel.split("/") or ":" in rel:
        return None
    partes = rel.split("/")
    nome = partes[-1].lower()
    if any(p.lower() in PROIBIDO_PARTES for p in partes[:-1]) or nome.startswith(".env"):
        return None
    if any(t in nome for t in PROIBIDO_NOME) or nome.endswith(PROIBIDO_SUFIXO):
        return None
    if any(t in p.lower() for p in partes[:-1] for t in PROIBIDO_NOME):
        return None
    suf = Path(nome).suffix
    if suf not in EXTENSOES and not (suf == ".csv" and partes[0] == "financas"):
        return None
    if any(p.startswith(".") and p != ".claude" for p in partes[:-1]):
        return None  # pasta oculta
    if nome.startswith(".") and not (partes[0] == "produtividade" and len(partes) == 2 and HIDDEN_OK.match(nome)):
        return None  # oculto: só o contexto .md do Ronaldo; logs, offsets, históricos e estados ficam fora
    if rel in RAIZ_ARQUIVOS:
        return RAIZ_ARQUIVOS[rel]
    for pref, area in RAIZES_OK.items():
        if rel.startswith(pref + "/"):
            if area == "agentes" and (len(partes) != 3 or not nome.endswith(".md")):
                return None
            if area in SO_TEXTO and suf not in (".md", ".txt"):
                return None  # só documentos de texto; .json de estado e transcrição ficam fora
            return area
    if partes[0] == "output" and len(partes) == 3:  # output/<slug>/<texto>: só o topo da pasta, nunca mídia nem subpastas
        return "videos"
    return None


def _e_link(p):
    """Link simbólico ou junction/reparse point do Windows (islink antigo não pega junction)."""
    try:
        if os.path.islink(p):
            return True
        return bool(getattr(os.lstat(p), "st_file_attributes", 0) & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except OSError:
        return True


def _candidatos(raiz):
    """Caminhos relativos permitidos, por varredura só das pastas da lista (sem seguir link simbólico)."""
    achados = []
    for rel in RAIZ_ARQUIVOS:
        p = raiz / rel
        if p.is_file() and not _e_link(p):
            achados.append(rel)
    pastas = [raiz / k for k in RAIZES_OK]
    saida = raiz / "output"
    if saida.is_dir():
        try:
            pastas += [d for d in saida.iterdir() if d.is_dir() and not _e_link(d)]
        except OSError:
            pass
    for base in pastas:
        for dp, dns, fns in os.walk(base, followlinks=False):
            dns[:] = [d for d in dns if d.lower() not in PROIBIDO_PARTES and not _e_link(os.path.join(dp, d))]
            if base.parent == saida:  # slug de output: nada de subpasta
                dns[:] = []
            for fn in fns:
                full = Path(dp) / fn
                if _e_link(full):
                    continue
                try:
                    rel = full.relative_to(raiz).as_posix()
                except ValueError:
                    continue
                if area_de(rel):
                    achados.append(rel)
    return sorted(set(achados))


# ----------------------------------------------------------------------------- índice

_docs = {}  # só em memória: {caminho: registro}. Nada é gravado em disco por este módulo.


def _ler_bytes(p):
    with open(p, "rb") as f:
        return f.read(LIMITE_HASH)


def invalidar():
    with _trava:
        _cache["em"] = 0.0
        _cache["resumo_em"] = 0.0


def varrer(forcar=False, raiz=None):
    """Índice {caminho: registro}. mtime+tamanho decidem se relê; o hash decide se a data de alteração muda (touch e checkout não contam)."""
    raiz = Path(raiz) if raiz else RAIZ
    with _trava:
        if not forcar and _cache["indice"] is not None and time.monotonic() - _cache["em"] < CACHE_VARREDURA_S and _cache.get("raiz") == str(raiz):
            return _cache["indice"]
        if _cache.get("raiz") != str(raiz):
            _docs.clear()
        docs = _docs
        presentes = set()
        for rel in _candidatos(raiz):
            p = raiz / rel
            try:
                st = p.stat()
            except OSError:
                continue
            presentes.add(rel)
            r = docs.get(rel)
            if r and r.get("mtime_ns") == st.st_mtime_ns and r.get("tam") == st.st_size:
                continue
            try:
                dados = _ler_bytes(p)
            except OSError:
                continue  # sendo escrito agora: tenta na próxima rodada
            sha = hashlib.sha1(dados).hexdigest()
            texto = dados.decode("utf-8", "replace")
            omitido = bool(CREDENCIAL.search(texto))
            titulo = rel.rsplit("/", 1)[-1]
            if not omitido:
                m = re.search(r"^#\s+(.+)$", texto, re.M)
                if m:
                    titulo = m.group(1).strip()[:120]
            if r is None:
                docs[rel] = {"sha": sha, "mtime_ns": st.st_mtime_ns, "tam": st.st_size, "alterado_em": st.st_mtime, "titulo": titulo, "omitido": omitido}
            elif r.get("sha") == sha:
                r.update(mtime_ns=st.st_mtime_ns, tam=st.st_size)  # touch: conteúdo igual, data de alteração fica
            else:
                r.update(sha=sha, mtime_ns=st.st_mtime_ns, tam=st.st_size, alterado_em=st.st_mtime, titulo=titulo, omitido=omitido)
        for rel in list(docs):
            if rel not in presentes:
                del docs[rel]  # apagado
        indice = {rel: dict(r, area=area_de(rel), slug=(rel.split("/")[1] if rel.startswith("output/") and rel.count("/") == 2 else None))
                  for rel, r in docs.items()}
        _cache.update(em=time.monotonic(), indice=indice, raiz=str(raiz))
        return indice


def _publico(rel, r):
    return {"caminho": rel, "titulo": r["titulo"], "area": r["area"], "slug": r["slug"], "tamanho": r["tam"],
            "alterado_em": _iso(r["alterado_em"]), "alterado_em_epoch": r["alterado_em"], "omitido": r["omitido"]}


def marca(indice=None):
    ind = indice if indice is not None else varrer()
    if not ind:
        return "0:0:0"
    mx = max(r["mtime_ns"] for r in ind.values())
    h = hashlib.sha1("".join(f"{k}{r['sha']}" for k, r in sorted(ind.items())).encode()).hexdigest()[:8]
    return f"{mx}:{len(ind)}:{h}"


def documentos(area=None, q=None, limite=100, offset=0):
    ind = varrer()
    itens = [(rel, r) for rel, r in ind.items() if (not area or r["area"] == area)]
    if q:
        q = q.lower()
        itens = [(rel, r) for rel, r in itens if q in rel.lower() or q in r["titulo"].lower()]
    itens.sort(key=lambda x: (-x[1]["alterado_em"], x[0]))
    limite = max(1, min(int(limite), 500))
    offset = max(0, int(offset))
    contagem = {a: sum(1 for r in ind.values() if r["area"] == a) for a in AREAS}
    return {"gerado_em": _iso(_agora()), "marca": marca(ind), "total": len(itens), "limite": limite,
            "offset": offset, "areas": contagem,
            "documentos": [_publico(rel, r) for rel, r in itens[offset:offset + limite]]}


def documento(caminho):
    """Conteúdo de um documento do índice. Devolve (dict, codigo). Caminho fora do índice = 404, sem dizer o motivo."""
    ind = varrer()
    r = ind.get(caminho) if isinstance(caminho, str) else None
    if r is None or area_de(caminho) is None:
        return {"erro": ["Documento não encontrado."]}, 404
    base = {k: v for k, v in _publico(caminho, r).items()}
    if r["omitido"]:
        return {**base, "conteudo": None, "motivo_omitido": "conteúdo omitido: parece conter credencial"}, 200
    p = (RAIZ / caminho)
    try:
        real = p.resolve()
        real.relative_to(RAIZ.resolve())
        if _e_link(p):
            raise ValueError
        texto = real.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return {"erro": ["Documento não encontrado."]}, 404
    if CREDENCIAL.search(texto):  # mudou depois da varredura
        return {**base, "conteudo": None, "motivo_omitido": "conteúdo omitido: parece conter credencial"}, 200
    cortado = len(texto) > LIMITE_TEXTO
    return {**base, "conteudo": texto[:LIMITE_TEXTO], "cortado": cortado}, 200


def mudancas(desde=None):
    """Barato, para o polling: 'igual' enquanto a marca não muda."""
    ind = varrer()
    atual = marca(ind)
    if desde == atual:
        return {"marca": atual, "mudou": False, "caminhos": []}
    try:
        corte_ns = int(str(desde).split(":")[0])
    except (ValueError, IndexError):
        corte_ns = None
    caminhos = [] if corte_ns is None else sorted((rel for rel, r in ind.items() if r["mtime_ns"] > corte_ns), key=lambda k: -ind[k]["alterado_em"])
    return {"marca": atual, "mudou": True, "caminhos": caminhos[:200], "gerado_em": _iso(_agora())}


# ----------------------------------------------------------------------------- setores e agentes

def _setores_arquivo():
    try:
        d = json.loads((RAIZ / "ecossistema" / "setores.json").read_text(encoding="utf-8"))
        return d if isinstance(d.get("setores"), list) else {"setores": [], "nomes_compostos": []}
    except (OSError, ValueError):
        return {"setores": [], "nomes_compostos": []}


def _nome(ident, compostos):
    partes = ident.split("-")
    n = 2 if "-".join(partes[:2]) in compostos else 1
    return " ".join(w.capitalize() for w in partes[:n])


def setores():
    """Setores da fonte única + agentes reais de .claude/agents. Agente sem setor aparece em 'sem_setor' (alerta). """
    d = _setores_arquivo()
    comp = set(d.get("nomes_compostos", []))
    reais = {}
    pasta = RAIZ / ".claude" / "agents"
    try:
        for p in pasta.glob("*.md"):
            reais[p.stem] = p.stat().st_mtime
    except OSError:
        pass
    listados = set()
    saida = []
    for s in d["setores"]:
        ids = [a["id"] if isinstance(a, dict) else a for a in s.get("agentes", [])]
        listados.update(ids)
        item = {"id": s["id"], "nome": s["nome"], "ativo": bool(s.get("ativo")), 
                "agentes_total": len(ids), "agentes_sem_arquivo": sorted(i for i in ids if i not in reais)}
        item["agentes"] = [{"id": i, "nome": _nome(i, comp), "atualizado_em": _iso(reais.get(i))} for i in ids]
        saida.append(item)
    sem = sorted(i for i in reais if i not in listados)
    return {"setores": saida, "sem_setor": [{"id": i, "nome": _nome(i, comp)} for i in sem]}


# ----------------------------------------------------------------------------- resumo (regra, sem IA, sem custo)

VERBO = {"Em refinamento técnico": "refinou", "Fazendo": "implementou", "Em teste": "testou", "Code Review": "revisou",
         "Pronto para aceite": "conferiu", "Bloqueado": "tratou bloqueio de", "Feito": "fechou"}


def _cortar(txt, n=120):
    txt = " ".join(str(txt).split())
    return txt if len(txt) <= n else txt[: n - 1].rstrip() + "…"


def _rotulo_hora(t):
    d = datetime.fromtimestamp(t)
    hoje = datetime.now().date()
    return d.strftime("%H:%M") if d.date() == hoje else d.strftime("%d/%m %H:%M")


def _acoes_decisoes(raiz):
    out = []
    pasta = raiz / "programacao" / "maestro" / "decisoes"
    try:
        arqs = list(pasta.glob("*.json"))
    except OSError:
        return out
    for p in arqs:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            t = p.stat().st_mtime
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        out.append({"t": t, "id": d.get("id") or p.stem, "acao": d.get("acao") or "", "status": d.get("status") or "",
                    "precisa": bool(d.get("precisa_do_guilherme")), "pedido": d.get("pedido_ao_guilherme") or ""})
    return out


def _acoes_log(raiz):
    """Linhas 'X terminou' de maestro/log.md, casadas com o 'chamando X para [itens] em <coluna>' anterior."""
    try:
        linhas = (raiz / "programacao" / "maestro" / "log.md").read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
    except OSError:
        return []
    out, chamadas = [], {}
    for ln in linhas:
        m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) chamando (.+?) para \[(.*?)\] em (.+)$", ln)
        if m:
            chamadas[m.group(2)] = (re.findall(r"PROG-\d+", m.group(3)), m.group(4).strip())
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+?) terminou \(.*?erro=(True|False)", ln)
        if m:
            try:
                t = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").timestamp()
            except ValueError:
                continue
            itens, coluna = chamadas.get(m.group(2), ([], ""))
            out.append({"t": t, "agente": m.group(2), "itens": itens, "coluna": coluna, "falhou": m.group(3) == "True"})
    return out


def _acoes_jobs():
    try:
        from .banco import varios
        rows = varios("SELECT craque, titulo, status, terminado_em FROM jobs WHERE terminado_em IS NOT NULL ORDER BY id DESC LIMIT 20")
    except Exception:  # noqa: BLE001 - banco ausente/ilegível: o resumo segue com as outras fontes
        return []
    out = []
    for j in rows:
        try:
            t = datetime.fromisoformat(j["terminado_em"]).timestamp()
        except (TypeError, ValueError):
            continue
        out.append({"t": t, "craque": j["craque"] or "Corte", "titulo": j["titulo"], "status": j["status"]})
    return out


def _linha1(raiz):
    cand = []
    for a in _acoes_log(raiz):
        itens = ", ".join(a["itens"][:3]) or "tarefa"
        verbo = VERBO.get(a["coluna"], "trabalhou em")
        cand.append((a["t"], f"{_rotulo_hora(a['t'])} · {a['agente']} falhou em {itens}" if a["falhou"] else f"{_rotulo_hora(a['t'])} · {a['agente']} {verbo} {itens}", "log"))
    for d in _acoes_decisoes(raiz):
        base = f"{_rotulo_hora(d['t'])} · {d['id']}: {d['status']}"
        cand.append((d["t"], f"Espera você: {base}" if d["precisa"] else base, "decisao"))
    for j in _acoes_jobs():
        verbo = "falhou" if j["status"] == "falhou" else j["status"]
        cand.append((j["t"], f"{_rotulo_hora(j['t'])} · {j['craque']}: {j['titulo']} ({verbo})", "job"))
    if not cand:
        return "Nada executado ainda", None, None
    t, txt, fonte = max(cand, key=lambda c: c[0])
    return _cortar(txt), t, fonte


def _linha2(ind):
    if not ind:
        return "Nenhum documento no índice ainda"
    ordem = sorted(ind.items(), key=lambda x: -x[1]["alterado_em"])
    top = ordem[:2]
    hoje = datetime.now().date()
    hoje_n = sum(1 for _, r in ordem if datetime.fromtimestamp(r["alterado_em"]).date() == hoje)
    nomes = ", ".join(rel.rsplit("/", 1)[-1] for rel, _ in top)
    extra = f" (+{hoje_n - 2} hoje)" if hoje_n > 2 else ""
    return _cortar(f"Atualizados: {nomes}{extra}")


def resumo(raiz=None):
    """Duas linhas, no máximo 120 caracteres cada, sem custo. Linha 1: última ação de agente. Linha 2: os 2 documentos alterados mais recentes."""
    raiz = Path(raiz) if raiz else RAIZ
    with _trava:
        if _cache["resumo"] is not None and time.monotonic() - _cache["resumo_em"] < CACHE_RESUMO_S and _cache.get("resumo_raiz") == str(raiz):
            return _cache["resumo"]
        l1, t1, fonte = _linha1(raiz)
        ind = varrer()
        base = max([t for t in [t1, max((r["alterado_em"] for r in ind.values()), default=None)] if t] or [None], default=None) if (t1 or ind) else None
        out = {"linhas": [l1, _linha2(ind)], "fonte_linha1": fonte, "base_em": _iso(base), "gerado_em": _iso(_agora()), "custo_usd": 0}
        _cache.update(resumo=out, resumo_em=time.monotonic(), resumo_raiz=str(raiz))
        return out


# ----------------------------------------------------------------------------- dashboard

def _pendentes(raiz, feitos):
    out = []
    for d in _acoes_decisoes(raiz):
        if d["precisa"] and d["id"] not in feitos:
            out.append({"id": d["id"], "pedido": _cortar(d["pedido"] or d["status"], 200), "status": _cortar(d["status"], 200), "em": _iso(d["t"])})
    out.sort(key=lambda x: x["em"] or "", reverse=True)
    return out


def visao():
    """Dashboard: vídeos em andamento, agentes ativos, sprint, decisões pendentes e documentos alterados hoje. Cada bloco falha sozinho."""
    from . import ao_vivo, central, status_video
    ind = varrer()
    hoje = datetime.now().date()
    out = {"gerado_em": _iso(_agora()), "app": "Ecossistema do Guilherme"}
    try:
        vs = status_video.todos()["videos"]
        andamento = [{"slug": v["slug"], "status": v["status"], "status_texto": v["status_texto"]} for v in vs if v["status"] in ("em_producao", "sem_roteiro")]
        out["videos"] = {"total": len(vs), "em_andamento": andamento[:30], "em_andamento_total": len(andamento)}
    except Exception as e:  # noqa: BLE001
        out["videos"] = {"erro": f"indisponível ({type(e).__name__})"}
    try:
        av = ao_vivo.montar()
        ativos = [{"id": a["id"], "craque": a["craque"], "estado": a["estado"], "estado_texto": a["estado_texto"]} for a in av["agentes"]]
        out["agentes_ativos"] = {"resumo": av["resumo"], "agentes": ativos[:30]}
    except Exception as e:  # noqa: BLE001
        out["agentes_ativos"] = {"erro": f"indisponível ({type(e).__name__})"}
    try:
        q = central.quadro()
        feitos = {it["id"] for c in q["colunas"] if c["nome"] == "Feito" for it in c["itens"]}
        out["sprint"] = {**central.sprint_ativa(), "quadro": {c["nome"]: c["n"] for c in q["colunas"]}}
    except Exception as e:  # noqa: BLE001
        feitos = set()
        out["sprint"] = {"erro": f"indisponível ({type(e).__name__})"}
    out["decisoes_pendentes"] = _pendentes(RAIZ, feitos)
    hoje_docs = sorted(((rel, r) for rel, r in ind.items() if datetime.fromtimestamp(r["alterado_em"]).date() == hoje), key=lambda x: -x[1]["alterado_em"])
    out["documentos_hoje"] = {"total": len(hoje_docs),
                              "recentes": [_publico(rel, r) for rel, r in hoje_docs[:10]]}
    s = setores()
    out["setores"] = s["setores"]
    out["sem_setor"] = s["sem_setor"]
    return out
