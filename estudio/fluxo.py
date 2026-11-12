"""O fluxo real do canal (CLAUDE.md) como máquina de estados: etapas, dependências, versões, aprovações e consequências.

Nada aqui depende de a produção ter nascido no estúdio: o estado sai dos arquivos em output/<slug>/, então o que roda pelo
terminal aparece como nova versão. As decisões do Guilherme ficam presas à versão (ou ao conteúdo do item), nunca ao nome.
"""
import json
import re
import sqlite3
import threading
import time
import unicodedata
from datetime import datetime
from pathlib import Path

from media import estilos

from . import materiais as M, prompts
from .banco import agora, con, evento, faz, um, varios, versao_dict
from .config import DIAS_ATIVA, RAIZ, REPO, SAIDA

OLISE = ("olise-diretor-arte", "Olise")
BARCOLA = ("barcola-diretor-horizontal", "Barcola")

ETAPAS = [
    {"id": "pesquisa", "nome": "Pesquisa", "agente": "modric-pesquisador-tema", "craque": "Modric", "material": "pesquisa",
     "gate": None, "auto": True, "raia": "agente", "faz": "pesquisando o tema"},
    {"id": "roteiro", "nome": "Roteiro", "agente": "neymar-roteirista", "craque": "Neymar", "material": "roteiro",
     "gate": "versao", "auto": True, "raia": "agente", "faz": "escrevendo o roteiro"},
    {"id": "componentes", "nome": "Componentes", "agente": "raphinha-curador-componentes", "craque": "Raphinha",
     "material": "componentes", "gate": "itens", "auto": True, "raia": "agente", "faz": "desenhando os componentes"},
    {"id": "cenas", "nome": "Cenas", "agente": OLISE[0], "craque": OLISE[1], "material": "cenas", "gate": "itens",
     "auto": True, "raia": "agente", "faz": "desenhando as cenas"},
    {"id": "metadados", "nome": "Metadados", "agente": "mbappe-editor-metadados", "craque": "Mbappé", "material": "metadados",
     "gate": None, "auto": True, "raia": "agente", "faz": "escrevendo título e descrição"},
    {"id": "auditoria_texto", "nome": "Auditoria de texto", "agente": "vini-auditor-conformidade", "craque": "Vini",
     "material": "auditoria_texto", "gate": None, "auto": True, "raia": "agente", "faz": "auditando o texto"},
    {"id": "narracao", "nome": "Narração", "agente": None, "craque": "Voz do canal", "material": "narracao", "gate": "itens",
     "auto": False, "raia": "pesado", "faz": "gerando a narração"},
    {"id": "video", "nome": "Vídeo final", "agente": None, "craque": "Render", "material": "video", "gate": "versao",
     "auto": False, "raia": "pesado", "faz": "renderizando o vídeo"},
    {"id": "auditoria_final", "nome": "Auditoria final", "agente": "vini-auditor-conformidade", "craque": "Vini",
     "material": "auditoria_final", "gate": None, "auto": True, "raia": "agente", "faz": "auditando o render"},
    {"id": "thumbnail", "nome": "Thumbnail", "agente": "sidorf-thumbnail-estrategista", "craque": "Sidorf",
     "material": "thumbnail", "gate": None, "auto": False, "raia": "agente", "faz": "preparando a thumbnail"},
]
POR_ID = {e["id"]: e for e in ETAPAS}
ORDEM_VERSOES = ["pesquisa", "roteiro", "componentes", "cenas", "metadados", "auditoria_texto", "narracao", "video",
                 "auditoria_final", "thumbnail"]
# O que depende de quê, gravado em cada versão quando ela nasce. É assim que se sabe o que uma mudança invalida.
DEPS = {"cenas": ["roteiro"], "narracao": ["roteiro"], "video": ["cenas", "narracao"],
        "auditoria_texto": ["roteiro", "cenas_texto", "metadados"], "auditoria_final": ["video", "metadados"]}
# Depois que uma etapa termina ou é aprovada, só estas podem começar sozinhas. Abrir a produção nunca dispara agente.
GATILHOS = {"pesquisa": ["roteiro"], "roteiro": ["componentes", "cenas", "metadados"], "componentes": ["cenas"],
            "cenas": ["auditoria_texto"], "metadados": ["auditoria_texto"], "video": ["auditoria_final"]}
CATEGORIAS = {
    "roteiro": ["Texto", "Fato", "Gancho", "Ritmo"],
    "componentes": ["Desenho", "Texto na imagem", "Tamanho"],
    "cenas": ["Desenho", "Texto na tela", "Animação"],
    "narracao": ["Pronúncia", "Ritmo", "Entonação"],
    "video": ["Imagem e animação", "Som", "Narração", "Texto"],
    "metadados": ["Título", "Descrição", "Tags"],
    "auditoria_texto": ["Texto", "Cenas", "Metadados"],
    "auditoria_final": ["Imagem e animação", "Narração", "Texto"],
    "pesquisa": ["Fato", "Fonte"],
    "thumbnail": ["Thumbnail"],
}
ESCOPO_VINI = {"auditoria_texto": {"roteiro": "roteiro", "cenas": "cenas_texto", "metadados": "metadados"},
               "auditoria_final": {"metadados": "metadados"}}
NOME_MATERIAL = {"pesquisa": "a pesquisa", "roteiro": "o roteiro", "componentes": "os componentes", "cenas": "as cenas",
                 "metadados": "os metadados", "auditoria_texto": "a auditoria de texto", "narracao": "a narração",
                 "video": "o vídeo final", "auditoria_final": "a auditoria final", "thumbnail": "a thumbnail"}
ATIVOS = ("fila", "rodando")
_locks = {}
_locks_lock = threading.Lock()
_ultimo_sync = {}


class Recusado(Exception):
    """A ação não vale agora. `motivos` vai para a interface."""

    def __init__(self, motivos, codigo=409):
        self.motivos = [motivos] if isinstance(motivos, str) else list(motivos)
        self.codigo = codigo
        super().__init__("; ".join(self.motivos))


def fmt_tempo(s):
    m, r = divmod(float(s), 60)
    return f"{int(m):02d}:{r:04.1f}"


def lista_e(itens):
    itens = list(itens)
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1] if itens else ""


def nome_cenas(idx):
    idx = [i + 1 for i in idx]
    return f"cena {idx[0]}" if len(idx) == 1 else "cenas " + lista_e(str(i) for i in idx)


def _lock(slug):
    with _locks_lock:
        return _locks.setdefault(slug, threading.Lock())


def garantir_producao(slug):
    """Registra uma pasta existente de output/ na primeira vez que ela aparece. Publicada ou parada vira arquivada, para
    não encher a tela inicial de vídeos que ninguém está esperando revisar."""
    p = um("SELECT * FROM producoes WHERE slug=?", slug)
    if p:
        return p
    pasta = M.pasta(slug)
    if not M.e_producao(pasta):
        raise Recusado(f"Produção não encontrada: {slug}", 404)
    parada = time.time() - M.ultima_mudanca(pasta) > DIAS_ATIVA * 86400
    faz("INSERT OR IGNORE INTO producoes (slug, origem, arquivada, estilo, criada_em) VALUES (?, 'pasta', ?, ?, ?)", slug,
        int((pasta / "upload.json").exists() or parada), M.estilo_das_cenas(slug) or (estilos.ler(pasta) or {}).get("estilo"), agora())
    return um("SELECT * FROM producoes WHERE slug=?", slug)


def ultima_versao(slug, material):
    return versao_dict(um("SELECT * FROM versoes WHERE slug=? AND material=? ORDER BY numero DESC LIMIT 1", slug, material))


def _hash_dep(slug, chave):
    if chave == "cenas_texto":
        cenas = M.ler_cenas(slug)
        return M.hash_cenas_texto(cenas) if cenas else None
    v = um("SELECT hash FROM versoes WHERE slug=? AND material=? ORDER BY numero DESC LIMIT 1", slug, chave)
    return v["hash"] if v else None


def _arquivos_dep(slug, chave):
    p = M.pasta(slug)
    if chave == "roteiro":
        return [p / "roteiro.txt", p / "direcao_viral.md"]
    if chave == "narracao":
        return [v["arquivo"] for v in M.falas(slug).values()]
    if chave == "cenas":
        return [f for f in (M.arquivo_cenas(slug), p / "sketch_cenas.py") if f]
    if chave == "cenas_texto":
        return [f for f in (M.arquivo_cenas(slug),) if f]
    if chave == "metadados":
        return [p / "metadados.json"]
    if chave == "video":
        return [p / "video.mp4"]
    return []


def _deps_novas(slug, material, arquivos, job_id):
    """Grava o hash do que esta versão usou. Em pasta vinda do terminal, sem job, o relógio dos arquivos diz se o insumo mudou
    depois da saída: nesse caso a versão já nasce marcada como anterior ao insumo."""
    saida = {}
    fim = max((o.stat().st_mtime for o in arquivos.values() if isinstance(o, Path)), default=0)
    for chave in DEPS.get(material, []):
        atual = _hash_dep(slug, chave)
        if not job_id and fim and atual:
            for f in _arquivos_dep(slug, chave):
                if chave == "roteiro" and f.name == "direcao_viral.md":
                    continue  # o resto desse arquivo muda sem afetar a narração; o que importa é a seção, comparada por conteúdo
                try:
                    if f.exists() and f.stat().st_mtime > fim + 2:
                        atual = "anterior"
                        break
                except OSError:
                    pass
        saida[chave] = atual
    return saida


def sincronizar(slug, forcar=False, assentar=True):
    """Compara o disco com a última versão de cada material e registra o que mudou (feito por agente ou pelo terminal).
    `forcar` ignora o intervalo entre leituras. `assentar=False` só quando um trabalho nosso acabou de terminar: aí os
    arquivos recém-gravados já estão completos. Fora disso, espera assentar, porque um render pelo terminal pode estar escrevendo."""
    if not forcar and time.time() - _ultimo_sync.get(slug, 0) < 1.0:
        return
    with _lock(slug):
        _ultimo_sync[slug] = time.time()
        corte_estilo = json.loads((um("SELECT estilo_corte FROM producoes WHERE slug=?", slug) or {}).get("estilo_corte") or "{}")
        ocupados = set()
        for j in varios("SELECT spec FROM jobs WHERE slug=? AND status IN ('fila','rodando')", slug):
            ocupados.update(json.loads(j["spec"]).get("materiais", []))
        for material in ORDEM_VERSOES:
            if material in ocupados:
                continue  # quem está gerando ainda não terminou: registra quando acabar
            m = M.manifesto(slug, material)
            if not m:
                continue
            arquivos, itens = m
            if assentar and not M.assentado(arquivos):
                continue
            h = M.fingerprint(arquivos, itens)
            ultima = um("SELECT numero, hash FROM versoes WHERE slug=? AND material=? ORDER BY numero DESC LIMIT 1", slug, material)
            if ultima and ultima["hash"] == h and ultima["numero"] > corte_estilo.get(material, 0):
                continue
            guardados = M.guardar_versao(arquivos)
            job = _ultimo_job_do_material(slug, material)
            recente = job if job and _job_recente(job["id"]) else None
            numero = (ultima["numero"] if ultima else 0) + 1
            origem = "estudio" if recente else ("terminal" if ultima else "existente")
            faz("INSERT INTO versoes (slug, material, numero, hash, manifesto, deps, origem, job_id, criada_em) VALUES (?,?,?,?,?,?,?,?,?)",
                slug, material, numero, h, json.dumps({"arquivos": guardados, "itens": itens}),
                json.dumps(_deps_novas(slug, material, arquivos, recente["id"] if recente else None)), origem,
                recente["id"] if recente else None, agora())
            if ultima:
                evento(slug, f"Nova versão de {NOME_MATERIAL[material]}: v{numero}")


def _ultimo_job_do_material(slug, material):
    """Quem gerou esta versão. No grafo a etapa do job é o nó (g<execução>:<nó>), então o material vem do pedido."""
    for j in varios("SELECT id, craque, etapa, spec FROM jobs WHERE slug=? AND status='ok' ORDER BY id DESC LIMIT 12", slug):
        if j["etapa"] == material or (j["etapa"].startswith("g") and material in json.loads(j["spec"]).get("materiais", [])):
            return j
    return None


def _job_recente(job_id):
    j = um("SELECT terminado_em FROM jobs WHERE id=?", job_id)
    if not j or not j["terminado_em"]:
        return False
    return (datetime.now() - datetime.fromisoformat(j["terminado_em"])).total_seconds() < 15


class Contexto:
    """Foto do estado de uma produção. `extra` simula uma aprovação, para dizer o que ela liberaria antes do clique."""

    def __init__(self, slug, extra=None, base=None):
        self.slug = slug
        self.extra = set(extra or ())
        if base:
            self.__dict__.update({k: v for k, v in base.__dict__.items() if k != "extra"})
            return
        self.prod = garantir_producao(slug)
        self.versoes = {}
        corte_estilo = json.loads(self.prod.get("estilo_corte") or "{}")
        for v in varios("SELECT * FROM versoes WHERE slug=? ORDER BY numero", slug):
            if v["numero"] > corte_estilo.get(v["material"], 0):  # o que veio antes de uma troca de estilo fica só no histórico
                self.versoes[v["material"]] = versao_dict(v)
        self.aprovadas = {r["versao_id"] for r in varios("SELECT versao_id FROM aprovacoes WHERE slug=?", slug)}
        self.dispensas_vini = {(r["etapa"], r["escopo"], r["hash"]) for r in varios("SELECT etapa, escopo, hash FROM dispensas_vini WHERE slug=?", slug)}
        self.itens = {(r["material"], r["sha"]): r["decisao"] for r in varios("SELECT material, sha, decisao FROM itens WHERE slug=?", slug)}
        self.cenas = M.ler_cenas(slug)
        self.estilo = M.estilo_das_cenas(slug) or self.prod["estilo"] or "sketch"
        self.formato = self.prod["formato"] or "vertical"
        self.jobs = varios("SELECT * FROM jobs WHERE slug=? ORDER BY id DESC", slug)
        self.falas = M.falas(slug)
        self.textos = M.textos_narrados(slug)
        self.pasta = M.pasta(slug)
        self.fase = M.fase_componentes()
        self._obs = {}
        self.em_grafo = bool(um("SELECT 1 x FROM execucoes WHERE slug=? LIMIT 1", slug))

    def job_ativo(self, etapa):
        return next((j for j in self.jobs if j["etapa"] == etapa and j["status"] in ATIVOS), None)

    def falha(self, etapa):
        ultimo = next((j for j in self.jobs if j["etapa"] == etapa and j["status"] in ("ok", "falhou", "cancelado")), None)
        return ultimo if ultimo and ultimo["status"] == "falhou" and not ultimo["dispensado"] else None

    def aplicavel(self, e):
        i = e["id"]
        if i == "componentes":
            if self.versoes.get("componentes"):
                return True
            return not self.prod["simulado"] and self.prod["origem"] == "estudio"  # o Raphinha faz componentes dos quatro estilos
        if i.startswith("auditoria") and self.prod["simulado"]:
            return False  # --mock é teste do pipeline: nada dali vai ao ar, então não gasta o Vini
        if i == "narracao":
            if self.versoes.get("narracao"):
                return True
            return not self.cenas or (self.estilo != "antigo" and any(c.get("fala") for c in self.cenas))
        return True

    def motivo_nao_aplica(self, e):
        """Por que a etapa não se aplica a esta produção (texto para a tela). None se ela se aplica."""
        if self.aplicavel(e):
            return None
        i = e["id"]
        if i == "componentes":
            if self.prod["simulado"]:
                return "Produção simulada (--mock): é teste do pipeline e não passa pelo Raphinha. Para aplicar: crie a produção pelo Corte (sem --mock)."
            return "Esta pasta veio de fora do estúdio (terminal): os componentes não são pedidos aqui. Para aplicar: inicie a produção pelo Corte."
        if i.startswith("auditoria") and self.prod["simulado"]:
            return "Produção simulada (--mock): nada dali vai ao ar, então não gasta o Vini. Para aplicar: use produção real."
        if i == "narracao":
            if self.estilo == "antigo":
                return "Este cenas.json é do formato antigo, sem campo fala: o pipeline atual não narra. Atualize o cenas.json para o novo formato com campo fala."
            return "Nenhuma cena tem fala: não há o que narrar. Adicione o campo fala nas cenas para gerar narração."
        return "Ela não faz parte do fluxo desta produção."

    def itens_atuais(self, material):
        v = self.versoes.get(material)
        return v["manifesto"]["itens"] if v else {}

    def pendentes(self, material):
        return [k for k, sha in self.itens_atuais(material).items() if self.itens.get((material, sha)) != "aprovado"]

    def aprovado(self, material):
        e = POR_ID[material if material != "video" else "video"]
        if not self.aplicavel(e):
            return True
        if material.startswith("auditoria") and self.auditoria_pulada(material):
            return True
        v = self.versoes.get(material)
        if not v:
            return False
        if material in self.extra:
            return True
        if e["gate"] == "versao":
            return v["id"] in self.aprovadas
        if e["gate"] == "itens":
            if material == "componentes" and self.fase == "pronto":
                return True
            return not self.pendentes(material)
        if material.startswith("auditoria"):
            return M.status_auditoria(M.ler_blob_texto(next(iter(v["manifesto"]["arquivos"].values())))) == "APROVADO"
        return True

    def escopos_pulados(self, etapa):
        return [escopo for escopo, dep in ESCOPO_VINI.get(etapa, {}).items()
                if _hash_dep(self.slug, dep) and (etapa, escopo, _hash_dep(self.slug, dep)) in self.dispensas_vini]

    def auditoria_pulada(self, etapa):
        escopos = ESCOPO_VINI.get(etapa, {})
        return bool(escopos) and len(self.escopos_pulados(etapa)) == len(escopos)

    def cenas_afetadas(self, dep):
        """Compara a versão do roteiro usada pela saída com a atual. Devolve (índices, alcance_conhecido)."""
        atual = self.versoes.get("roteiro")
        antiga = None if dep == "anterior" else versao_dict(
            um("SELECT * FROM versoes WHERE slug=? AND material='roteiro' AND hash=? ORDER BY numero DESC LIMIT 1", self.slug, dep or ""))
        if not antiga or not atual:
            return list(range(len(self.cenas))), False

        def texto(v):
            return "\n".join(M.ler_blob_texto(s) for s in v["manifesto"]["arquivos"].values())

        saiu = M.mudancas_entre(texto(antiga), texto(atual))
        if not saiu:
            return [], True  # só entrou texto novo: nenhuma cena existente mudou
        afetadas = M.cenas_com_frases(saiu, self.cenas)
        return (afetadas, True) if afetadas else (list(range(len(self.cenas))), False)

    def obsoleto(self, material):
        """Se a versão atual ficou para trás do que ela usou: {motivo, cenas}. Senão, None."""
        if material not in self._obs:
            self._obs[material] = self._calcular_obsoleto(material)
        return self._obs[material]

    def _calcular_obsoleto(self, material):
        v = self.versoes.get(material)
        if not v:
            return None
        deps = v["deps"]
        rot = self.versoes.get("roteiro")
        if material == "cenas":
            if rot and deps.get("roteiro") not in (None, rot["hash"]):
                afetadas, conhecido = self.cenas_afetadas(deps["roteiro"])
                if afetadas and conhecido:
                    return {"motivo": f"O roteiro mudou e afeta {nome_cenas(afetadas)}.", "cenas": afetadas}
                return {"motivo": "O roteiro mudou depois destas cenas.", "cenas": afetadas if conhecido else []}
            return None
        if material == "narracao":
            cenas = set()
            motivos = []
            if self.textos is not None and self.cenas:
                dif = [i for i, c in enumerate(self.cenas) if i >= len(self.textos) or self.textos[i] != c.get("fala")]
                if dif:
                    cenas.update(dif)
                    motivos.append(f"A fala de {nome_cenas(dif)} mudou depois da narração.")
                if len(self.textos) != len(self.cenas):
                    motivos.append("O número de cenas mudou.")
            if rot and deps.get("roteiro") not in (None, rot["hash"]):
                afetadas, conhecido = self.cenas_afetadas(deps["roteiro"])
                novas = [i for i in afetadas if i not in cenas]
                if conhecido and afetadas:
                    cenas.update(afetadas)
                    if novas:
                        motivos.append(f"O roteiro mudou e afeta {nome_cenas(novas)}.")
                elif not conhecido:
                    motivos.append("O roteiro mudou depois desta narração.")
            return {"motivo": " ".join(motivos), "cenas": sorted(cenas)} if motivos else None
        if material == "video":
            motivos = []
            cenas = set()
            for dep, nome in (("cenas", "As cenas mudaram"), ("narracao", "A narração mudou")):
                atual = self.versoes.get(dep)
                if atual and deps.get(dep) not in (None, atual["hash"]):
                    motivos.append(f"{nome} depois deste render.")
            for dep, nome in (("narracao", "narração"), ("cenas", "cenas")):
                o = self.obsoleto(dep)
                if o:
                    cenas.update(o["cenas"])
                    motivos.append(f"As {nome} usadas estão desatualizadas." if dep == "cenas" else "A narração usada está desatualizada.")
            from . import corte
            s = corte.situacao(self.slug)
            if s and not s["em_dia"]:
                motivos.append(s["motivo"])
            return {"motivo": " ".join(dict.fromkeys(motivos)), "cenas": sorted(cenas)} if motivos else None
        if material == "auditoria_texto":
            mudou = [n for k, n in (("roteiro", "o roteiro"), ("cenas_texto", "o texto das cenas"), ("metadados", "os metadados"))
                     if k in deps and deps[k] != _hash_dep(self.slug, k)]
            return {"motivo": f"Depois desta auditoria mudou {lista_e(mudou)}.", "cenas": []} if mudou else None
        if material == "auditoria_final":
            atual = self.versoes.get("video")
            if atual and deps.get("video") != atual["hash"]:
                return {"motivo": "O vídeo mudou depois desta auditoria.", "cenas": []}
            if "metadados" in deps and deps.get("metadados") != _hash_dep(self.slug, "metadados"):
                return {"motivo": "Os metadados mudaram depois desta auditoria.", "cenas": []}
        return None

    def _req_ok(self, material, nome, faltas):
        e = POR_ID[material]
        if not self.aplicavel(e):
            return
        if material.startswith("auditoria") and self.auditoria_pulada(material):
            return
        v = self.versoes.get(material)
        if not v:
            faltas.append(f"Falta {nome}.")
        elif self.obsoleto(material):
            faltas.append(f"Atualize {nome} primeiro. {self.obsoleto(material)['motivo']}")
        elif not self.aprovado(material):
            if material.startswith("auditoria"):
                faltas.append(f"{nome[0].upper() + nome[1:]} não está APROVADA pelo Vini.")
            else:
                faltas.append(f"Aprove {nome} (v{v['numero']}).")

    def requisitos(self, etapa):
        """O que falta para INICIAR a etapa. Vazio = pode."""
        f = []
        if etapa == "roteiro" and not self.versoes.get("pesquisa"):
            f.append("Falta a pesquisa (notas.md).")
        elif etapa in ("componentes", "metadados"):
            self._req_ok("roteiro", "o roteiro", f)
        elif etapa == "cenas":
            self._req_ok("roteiro", "o roteiro", f)
            self._req_ok("componentes", "os componentes", f)
        elif etapa == "auditoria_texto":
            if not self.versoes.get("pesquisa"):
                f.append("Falta a pesquisa (notas.md).")
            self._req_ok("roteiro", "o roteiro", f)
            for m, n in (("cenas", "as cenas"), ("metadados", "os metadados")):
                if not self.versoes.get(m):
                    f.append(f"Falta {n}.")
            if self.obsoleto("cenas"):
                f.append(f"Atualize as cenas primeiro. {self.obsoleto('cenas')['motivo']}")
        elif etapa == "narracao":
            self._req_ok("roteiro", "o roteiro", f)
            if not self.cenas:
                f.append("Falta o cenas.json (é dele que sai a fala de cada cena).")
            elif self.obsoleto("cenas"):
                f.append(f"Atualize as cenas primeiro. {self.obsoleto('cenas')['motivo']}")
            self._req_ok("auditoria_texto", "a auditoria de texto", f)
            if self.estilo == "antigo":
                f.append("Este cenas.json é do formato antigo, sem campo fala: o pipeline atual não narra.")
        elif etapa == "video":
            self._req_ok("roteiro", "o roteiro", f)
            self._req_ok("cenas", "as cenas", f)
            self._req_ok("auditoria_texto", "a auditoria de texto", f)
            self._req_ok("narracao", "a narração", f)
            if not self.versoes.get("metadados"):
                f.append("Falta metadados.json.")
            if self.estilo == "antigo":
                f.append("Este cenas.json é do formato antigo: o run.py atual não renderiza.")
            for nome in (estilos.obter(self.estilo) or {}).get("precisa_arquivos", ()):
                if not (self.pasta / nome).exists():
                    f.append(f"Falta {nome}.")
            q = self.pasta / "frames"
            if q.is_dir() and time.time() - q.stat().st_mtime < 120 and not self.job_ativo("video"):
                f.append("Há um render desta pasta rodando pelo terminal.")
        elif etapa == "auditoria_final":
            if not self.versoes.get("video"):
                f.append("Falta o vídeo renderizado.")
            elif self.obsoleto("video"):
                f.append(f"Renderize o vídeo de novo primeiro. {self.obsoleto('video')['motivo']}")
        elif etapa == "thumbnail":
            self._req_ok("video", "o vídeo final", f)
            self._req_ok("auditoria_final", "a auditoria final", f)
        return f

    def requisitos_aprovacao(self, etapa):
        """O que falta para APROVAR: tudo de que aquele material depende de verdade."""
        f = []
        if self.em_grafo:
            return f  # quem decide a ordem é o grafo publicado (grafos.py)
        if etapa in ("componentes", "cenas", "narracao", "video"):
            self._req_ok("roteiro", "o roteiro", f)
        if etapa == "cenas":
            self._req_ok("componentes", "os componentes", f)
        if etapa == "video":
            self._req_ok("cenas", "as cenas", f)
            self._req_ok("narracao", "a narração", f)
        return f

    def precisa_rodar(self, etapa):
        e = POR_ID[etapa]
        return self.aplicavel(e) and (not self.versoes.get(e["material"]) or bool(self.obsoleto(e["material"])))

    def autos_apos(self, etapa):
        """Etapas que começariam sozinhas depois desta. É a mesma conta usada no rótulo do botão e na execução."""
        return [g for g in GATILHOS.get(etapa, []) if POR_ID[g]["auto"] and not self.job_ativo(g) and not self.falha(g)
                and self.precisa_rodar(g) and not self.requisitos(g)]

    def etapa_status(self, e):
        if not self.aplicavel(e):
            return "nao_aplica"
        if e["material"].startswith("auditoria") and self.auditoria_pulada(e["material"]):
            return "dispensada"
        ativo = self.job_ativo(e["id"])
        if ativo:
            return "executando" if ativo["status"] == "rodando" else "fila"
        if self.falha(e["id"]):
            return "falhou"
        material = e["material"]
        v = self.versoes.get(material)
        if not v:
            return "bloqueada" if self.requisitos(e["id"]) else "pronta"
        if self.obsoleto(material):
            return "desatualizada"
        if material.startswith("auditoria"):
            return "aprovada" if self.aprovado(material) else "bloqueio"
        if e["gate"] == "itens" and not self.itens_atuais(material):
            return "concluida"
        if e["gate"]:
            if material == "componentes" and self.fase == "pronto":
                return "concluida"
            return "aprovada" if self.aprovado(material) else "aguardando"
        return "concluida"


def consequencia(ctx, e):
    """Diz em palavras o que a aprovação faz, calculando sobre o estado real. Devolve (trecho do rótulo, frase, o que ainda falta)."""
    if e["id"] == "video":
        return "liberar download", "O arquivo final fica disponível para download.", []
    sim = Contexto(ctx.slug, extra={e["material"]}, base=ctx)
    sim._obs = ctx._obs
    autos = sim.autos_apos(e["id"])
    if autos:
        nomes = lista_e(POR_ID[a]["nome"].lower() for a in autos)
        craques = lista_e(dict.fromkeys(_agente_de(ctx, POR_ID[a])[1] for a in autos))
        return f"iniciar {nomes} ({craques})", f"{craques} começa{'m' if len(autos) > 1 else ''} em seguida, sem outro clique.", []
    liberadas = [s for s in ETAPAS if s["id"] != e["id"] and sim.aplicavel(s) and ctx.requisitos(s["id"]) and not sim.requisitos(s["id"])]
    # Etapas à frente que dependem de aprovação, mesmo já tendo arquivo: aprovar libera revisá-las.
    if liberadas:
        s = liberadas[0]
        return (f"liberar {s['nome'].lower()}",
                f"A etapa {s['nome']} fica liberada" + (", e você inicia quando quiser." if not s["auto"] else "."), [])
    frente = [s for s in ETAPAS if ETAPAS.index(s) > ETAPAS.index(e) and sim.aplicavel(s) and s["gate"]]
    for s in frente:
        if not sim.versoes.get(s["material"]) or sim.etapa_status(s) in ("aguardando", "desatualizada"):
            faltas = sim.requisitos_aprovacao(s["id"]) if sim.versoes.get(s["material"]) else sim.requisitos(s["id"])
            if faltas:
                return "", f"A etapa {s['nome']} ainda espera outra decisão:", faltas
            return f"liberar {s['nome'].lower()}", f"A etapa {s['nome']} fica liberada.", []
    return "", "", []


def _agente_de(ctx, e):
    if e["id"] == "cenas" and ctx.formato == "horizontal":
        return BARCOLA
    return e["agente"], e["craque"]


def rotulo_iniciar(ctx, e):
    tem = bool(ctx.versoes.get(e["material"]))
    if e["id"] == "narracao":
        obs = ctx.obsoleto("narracao")
        alvo = _escopo_narracao(ctx)
        if alvo:
            return f"Gerar narração de {nome_cenas(alvo)}"
        return "Gerar narração de novo" if tem and not obs else "Gerar narração"
    if e["id"] == "video":
        return "Renderizar nova versão" if tem else "Renderizar vídeo"
    if e["id"] == "thumbnail":
        return "Gerar prompt da thumbnail (Sidorf)"
    _, craque = _agente_de(ctx, e)
    return f"{'Refazer' if tem else 'Iniciar'} {e['nome'].lower()} ({craque})"


def _escopo_narracao(ctx):
    """Só o que ficou desatualizado, se dá para reaproveitar o resto."""
    obs = ctx.obsoleto("narracao")
    if not obs or not obs["cenas"] or ctx.textos is None or len(ctx.textos) != len(ctx.cenas):
        return None
    if not all(i in ctx.falas for i in range(len(ctx.cenas))):
        return None
    return obs["cenas"]


def feedback_rascunhos(slug, material, versao_id):
    return varios("SELECT * FROM feedback WHERE slug=? AND material=? AND versao_id=? AND status='rascunho' ORDER BY COALESCE(tempo_s, -1), id",
                  slug, material, versao_id)


def _dono_feedback(ctx, material, categoria):
    """Quem resolve cada pedido. Devolve a chave de TAREFA_AJUSTE: é ela que define agente, etapa e arquivos."""
    cat = (categoria or "").lower()
    if material in ("video", "auditoria_final"):
        if "narra" in cat:
            return "narracao"
        if "texto" in cat:
            return "roteiro"
        return "cenas"
    if material == "auditoria_texto":
        return {"cenas": "cenas", "metadados": "metadados", "componentes": "componentes"}.get(cat, "roteiro")
    return material


_MARCADOR_REPARO_VINI = "[RESOLVER_PARECER_VINI]"


def _destinos_parecer_vini(slug):
    """Separa correcoes obrigatorias do Vini pelos artefatos/agentes responsaveis."""
    caminho = M.pasta(slug) / "auditoria_texto.md"
    parecer = caminho.read_text(encoding="utf-8") if caminho.is_file() else ""
    if not re.search(r"\bBLOQUEADO\b", parecer[:1200], re.I):
        raise Recusado("O parecer atual do Vini nao esta marcado como BLOQUEADO.")

    bloco = re.search(
        r"(?ims)^\s*#{1,4}\s*(?:corre[cç][oõ]es? obrigat[oó]rias|ajustes? obrigat[oó]rios|pend[eê]ncias? obrigat[oó]rias)\s*\n(.*?)(?=^\s*#{1,4}\s*(?:riscos?|recomenda[cç][oõ]es?|verifica[cç][oõ]es?|limites?|pend[eê]ncias?)\b|\Z)",
        parecer,
    )
    if not bloco:
        raise Recusado("Nao encontrei a secao de correcoes obrigatorias no parecer do Vini.")
    itens = [x.strip() for x in re.split(r"(?m)^\s*\d+[.)]\s+", bloco.group(1)) if x.strip()]
    if not itens:
        raise Recusado("O parecer nao tem correcoes obrigatorias numeradas para encaminhar.")

    por_agente = {}
    for item in itens:
        normal = unicodedata.normalize("NFKD", item).encode("ascii", "ignore").decode().lower()
        donos = set()
        if re.search(r"metadados|descricao|titulo|tags|thumbnail|miniatura", normal):
            donos.add("metadados")
        if re.search(r"componentes|componente visual|arquivo de componente", normal):
            donos.add("componentes")
        if re.search(r"cenas?|cartoes?|rotulos?|legendas?|sketch_cenas|cenas\\.json", normal):
            donos.add("cenas")
        if re.search(r"roteiro|gancho|fechamento|abertura|frase|formulacao|analise original|enxugar|trocar|substituir|texto", normal):
            donos.add("roteiro")
        for dono in donos:
            por_agente.setdefault(dono, []).append(item)
    if not por_agente:
        raise Recusado("Nao consegui identificar com seguranca os artefatos afetados. Revise o parecer e encaminhe o ajuste manualmente.")

    categorias = {"roteiro": "Texto", "cenas": "Cenas", "metadados": "Metadados", "componentes": "Componentes"}
    return [(categorias[dono], dono, itens_dono) for dono, itens_dono in por_agente.items()]


def _parecer_encaminhado(slug, versao_id):
    """Trabalhos já criados para o parecer bloqueado desta versão (vazio se o clique ainda não foi atendido)."""
    if not versao_id:
        return []
    return varios(
        "SELECT f.status, f.job_id, j.craque, j.status AS job_status, j.titulo "
        "FROM feedback f LEFT JOIN jobs j ON j.id=f.job_id "
        "WHERE f.slug=? AND f.material='auditoria_texto' AND f.versao_id=? AND f.texto LIKE ? ORDER BY f.id",
        slug, versao_id, f"{_MARCADOR_REPARO_VINI}%",
    )


def resolver_parecer_vini(slug):
    """Encaminha as correcoes obrigatorias do parecer bloqueado aos agentes donos dos artefatos."""
    from . import trabalhos
    sincronizar(slug, forcar=True)
    v = ultima_versao(slug, "auditoria_texto")
    if not v:
        raise Recusado("Ainda nao existe um parecer de texto do Vini nesta producao.")

    # Idempotencia: re-cliques mostram os mesmos trabalhos, sem duplicar tarefas.
    enviados = _parecer_encaminhado(slug, v["id"])
    if enviados:
        return {"ja": True, "jobs": [{"id": x["job_id"], "craque": x["craque"], "status": x["job_status"], "titulo": x["titulo"]} for x in enviados if x["job_id"]]}

    destinos = _destinos_parecer_vini(slug)
    ctx = Contexto(slug)
    for _, dono, _ in destinos:
        material_dono = POR_ID[dono]["material"]
        if ctx.job_ativo(dono) or any(j["status"] in ATIVOS and material_dono in json.loads(j["spec"]).get("materiais", []) for j in ctx.jobs):
            raise Recusado(f"{POR_ID[dono]['nome']} ja esta trabalhando neste material. Aguarde antes de encaminhar o parecer.")

    for categoria, dono, correcoes in destinos:
        resumo = "\n".join(f"- {item}" for item in correcoes)
        texto = f"{_MARCADOR_REPARO_VINI} Encaminhamento automatico do parecer do Vini para {dono}:\n{resumo}\n\nAplique somente as correcoes do seu artefato. Preserve os demais materiais e nao marque o parecer como aprovado."
        anotar_feedback(slug, "auditoria_texto", v["id"], texto, categoria=categoria)

    jobs = enviar_ajustes(slug, "auditoria_texto", v["id"])
    return {"ja": False, "jobs": [{"id": j["id"], "craque": j["craque"], "status": j["status"], "titulo": j["titulo"]} for j in jobs]}


def _craque_dono(ctx, dono):
    if dono == "narracao":
        return "neymar-roteirista", "Neymar"  # dono da seção ## Narração. O kane-narrador é outro fluxo, fora de output/.
    return _agente_de(ctx, POR_ID[dono])


def acoes_etapa(ctx, e, bloqueio=None, via_fluxo=False):
    material, ident = e["material"], e["id"]
    v = ctx.versoes.get(material)
    status = ctx.etapa_status(e)
    saida = {"aprovar": None, "iniciar": None, "enviar": None, "pular_vini": None}
    if ident in ESCOPO_VINI:
        saida["pular_vini"] = {"escopos": list(ESCOPO_VINI[ident]), "pulados": ctx.escopos_pulados(ident),
                               "dispensada": ctx.auditoria_pulada(ident)}
    from . import trabalhos
    faltando = trabalhos.integracao_faltando(ident, ctx)

    if status != "nao_aplica" and (e["agente"] or ident in ("narracao", "video")) and not ctx.em_grafo:
        mostrar = not v or status in ("desatualizada", "falhou", "bloqueio") or ident in ("narracao", "video", "thumbnail")
        if status in ("executando", "fila"):
            mostrar = False
        if mostrar and not ctx.falha(ident):
            motivos = faltando + ctx.requisitos(ident)
            saida["iniciar"] = {"rotulo": rotulo_iniciar(ctx, e), "habilitado": not motivos, "motivos": motivos,
                                "principal": not v or status == "desatualizada", "refazer": bool(v) and status != "desatualizada"}

    elif bloqueio and status != "nao_aplica" and e["agente"] and not ctx.job_ativo(ident):
        # Produção conduzida por grafo: o botão não dispara nada por fora do grafo; diz quem está segurando e deixa o "tentar de novo" ao nó que falhou.
        acao_nome = {"falhou": "falhou", "aguardando": "espera sua aprovação", "aguardando_inicio": "espera você iniciar", "rodando": "ainda está rodando"}.get(bloqueio["status"], bloqueio["status"])
        saida["iniciar"] = {"rotulo": rotulo_iniciar(ctx, e), "habilitado": False, "motivos": [f"Esta etapa espera {bloqueio['nome']}, que {acao_nome}."],
                            "principal": not v, "refazer": False, "bloqueio": bloqueio}

    elif via_fluxo and e["agente"] and status in ("pronta", "bloqueada") and not v:
        # Nada segura o fluxo: o botão pede ao grafo que dê o próximo passo (servidor.iniciar chama grafos.avancar).
        saida["iniciar"] = {"rotulo": f"Continuar o fluxo ({_agente_de(ctx, e)[1]}: {e['nome'].lower()})", "habilitado": not faltando, "motivos": faltando, "principal": True, "refazer": False, "via_fluxo": True}

    if v and e["gate"] and status in ("aguardando", "desatualizada", "aprovada") and not (e["gate"] == "itens" and not v["manifesto"]["itens"]):
        pendentes = ctx.pendentes(material) if e["gate"] == "itens" else []
        ja = ctx.aprovado(material)
        motivos = list(ctx.requisitos_aprovacao(ident))
        rascunhos = feedback_rascunhos(ctx.slug, material, v["id"])
        if rascunhos:
            motivos.append("Envie ou remova os ajustes anotados nesta versão antes de aprovar.")
        if ctx.obsoleto(material):
            motivos.append("Esta versão está desatualizada: gere a nova antes de aprovar.")
        if ctx.falha(ident):
            motivos.append("Resolva a falha desta etapa antes de aprovar.")
        trecho, frase, ainda = consequencia(ctx, e)
        nome = NOME_MATERIAL[material].split(" ", 1)[1]
        total = len(v["manifesto"]["itens"])
        if e["gate"] == "itens" and pendentes and len(pendentes) < total:
            base = f"Aprovar {'os' if len(pendentes) > 1 else 'o'} {len(pendentes)} restante{'s' if len(pendentes) > 1 else ''}"
        else:
            base = f"Aprovar {nome} v{v['numero']}"
        saida["aprovar"] = {"rotulo": f"{base} e {trecho}" if trecho else base, "frase": frase, "ainda": ainda, "habilitado": not motivos and not ja,
                            "motivos": motivos, "ja": ja, "versao_id": v["id"], "numero": v["numero"]}

    if v:
        rascunhos = feedback_rascunhos(ctx.slug, material, v["id"])
        if rascunhos and status not in ("executando", "fila"):
            donos = {}
            for f in rascunhos:
                donos.setdefault(_craque_dono(ctx, _dono_feedback(ctx, material, f["categoria"]))[1], []).append(f)
            n = len(rascunhos)
            quem = lista_e(donos)
            pendencia = trabalhos.integracao_faltando("roteiro", ctx)
            saida["enviar"] = {"rotulo": f"Enviar {n} ajuste{'s' if n > 1 else ''} para {quem}", "habilitado": not pendencia, "motivos": pendencia,
                               "quem": quem, "versao_id": v["id"]}
    return saida


def status_job_publico(j):
    if not j:
        return None
    spec = json.loads(j["spec"])
    return {k: j[k] for k in ("id", "etapa", "titulo", "craque", "status", "erro", "resumo", "custo_usd", "criada_em", "iniciado_em", "terminado_em", "dispensado")} | {
        "origem": spec.get("origem"), "tipo": spec.get("tipo"), "motor": _motor(j), "motor_nota": j.get("motor_nota")}


def _motor(j):
    from . import trabalhos
    return trabalhos.motor_do_job(j)


STATUS_TEXTO = {
    "nao_aplica": "Não se aplica", "executando": "Em execução", "fila": "Na fila", "falhou": "Falhou",
    "bloqueada": "Aguarda etapas anteriores", "pronta": "Pronta para iniciar", "desatualizada": "Desatualizada",
    "bloqueio": "Bloqueada pelo Vini", "dispensada": "Pulada por você", "concluida": "Pronta", "aprovada": "Aprovada", "aguardando": "Aguardando você",
}


def estado(slug, sincroniza=True):
    if sincroniza:
        garantir_producao(slug)
        sincronizar(slug)
    ctx = Contexto(slug)
    from . import trabalhos
    etapas = []
    bl = {"execucao": None, "ativa": False, "por_material": {}}
    if ctx.em_grafo:
        from . import grafos
        bl = grafos.bloqueios(slug)
    aud_obs = ctx.obsoleto("auditoria_texto")
    reaud = None
    if aud_obs and ctx.em_grafo:
        from . import grafos
        reaud = grafos.reauditar_de(slug)
    for e in ETAPAS:
        material = e["material"]
        v = ctx.versoes.get(material)
        st = ctx.etapa_status(e)
        bloqueio = bl["por_material"].get(material) if st in ("pronta", "bloqueada", "falhou") else None
        ativo = ctx.job_ativo(e["id"])
        falha = ctx.falha(e["id"])
        itens = ctx.itens_atuais(material)
        pend = ctx.pendentes(material) if e["gate"] == "itens" else []
        obs = ctx.obsoleto(material)
        e2 = {"id": e["id"], "nome": e["nome"], "material": material, "craque": _agente_de(ctx, e)[1], "gate": e["gate"], "status": st,
              "status_texto": STATUS_TEXTO[st], "motivo_nao_aplica": ctx.motivo_nao_aplica(e), "versao": v["numero"] if v else None, "versao_id": v["id"] if v else None,
              "aprovada": bool(v) and ctx.aprovado(material) and bool(e["gate"]), "total_itens": len(itens), "pendentes": len(pend),
              "obsoleto": obs, "acoes": acoes_etapa(ctx, e, bloqueio, bool(bl.get("ativa")) and not bloqueio), "bloqueio": bloqueio, "categorias": CATEGORIAS.get(material, []),
              "job": status_job_publico(ativo) if ativo else None, "falha": status_job_publico(falha) if falha else None,
              "progresso": trabalhos.progresso(ativo, ctx) if ativo else None,
              # Edição direta (roteiro, cenas, metadados) e o atalho para reauditar o texto depois dela.
              "editavel": material in ("roteiro", "cenas", "metadados") and bool(v) and not ativo and not any(j["status"] in ATIVOS and material in json.loads(j["spec"]).get("materiais", []) for j in ctx.jobs),
              "reauditar": reaud if reaud and material in ("roteiro", "cenas", "metadados", "auditoria_texto") else None}
        if st == "aguardando" and pend and len(pend) < len(itens):
            e2["status_texto"] = f"Aguardando você · {len(pend)} de {len(itens)}"
        elif st == "aguardando" and pend:
            e2["status_texto"] = f"Aguardando você · {len(pend)}"
        etapas.append(e2)
    return {"slug": slug, "titulo": titulo(ctx), "tema": ctx.prod["tema"], "formato": ctx.formato, "estilo": ctx.estilo, "estilo_nome": estilos.rotulo(ctx.estilo, estilos.ler(ctx.pasta) if (estilos.ler(ctx.pasta) or {}).get("estilo") == ctx.estilo else None), "simulado": bool(ctx.prod["simulado"]),
            "arquivada": bool(ctx.prod["arquivada"]), "publicado": publicado(slug), "fase_componentes": ctx.fase, "execucao": bl["execucao"], "etapas": etapas, "resumo": resumo(etapas, ctx),
            "atualizado_em": ultima_atualizacao(slug), "fila": [status_job_publico(j) for j in ctx.jobs if j["status"] in ATIVOS], "em_grafo": ctx.em_grafo, "legenda": ctx.prod.get("legenda"), "duracao_alvo": ctx.prod.get("duracao_alvo")}


def titulo(ctx):
    t = (M.ler_json(ctx.pasta / "metadados.json", {}) or {}).get("titulo")
    return t or ctx.prod["tema"] or ctx.slug.replace("-", " ").capitalize()


def publicado(slug):
    u = M.ler_json(M.pasta(slug) / "upload.json", None)
    return {"url": u.get("url"), "privacidade": u.get("privacy")} if isinstance(u, dict) else None


def ultima_atualizacao(slug):
    # A data de registro da versão não entra: a primeira leitura de uma pasta antiga faria tudo parecer feito agora.
    linhas = [r for r in (um("SELECT MAX(COALESCE(terminado_em, iniciado_em, criada_em)) m FROM jobs WHERE slug=?", slug)["m"],
                          um("SELECT MAX(criada_em) m FROM aprovacoes WHERE slug=?", slug)["m"]) if r]
    t = M.ultima_mudanca(M.pasta(slug))
    linhas.append(datetime.fromtimestamp(t).isoformat(timespec="seconds"))
    return max(linhas)


def resumo(etapas, ctx):
    """As três respostas da tela: o que está pronto, o que precisa de decisão e qual é a próxima ação."""
    prontas = [e["nome"] for e in etapas if e["status"] in ("aprovada", "concluida")]
    decisao = [e for e in etapas if e["status"] in ("aguardando", "falhou", "bloqueio", "desatualizada")]
    rodando = [e for e in etapas if e["status"] in ("executando", "fila")]
    atual = next((e for e in etapas if e["status"] == "falhou"), None) \
        or next((e for e in etapas if e["id"] == "auditoria_texto" and e["status"] == "bloqueio"), None) \
        or next((e for e in etapas if e["status"] == "aguardando"), None) \
        or next((e for e in etapas if e["status"] == "bloqueio"), None) \
        or next((e for e in etapas if e["status"] == "desatualizada"), None)
    if atual:
        textos = {"falhou": f"Abrir para tentar novamente: {atual['nome'].lower()}", "aguardando": f"Abrir para revisar {atual['nome'].lower()}",
                  "bloqueio": f"Resolver o parecer do Vini ({atual['nome'].lower()})" if atual["id"] == "auditoria_texto" else f"Abrir para resolver o parecer do Vini ({atual['nome'].lower()})",
                  "desatualizada": f"Abrir para atualizar {atual['nome'].lower()}"}
        prox = {"texto": textos[atual["status"]], "etapa": atual["id"], "tipo": "voce"}
        if atual["id"] == "auditoria_texto" and atual["status"] == "bloqueio":
            enviados = _parecer_encaminhado(ctx.slug, (ctx.versoes.get("auditoria_texto") or {}).get("id"))
            if enviados:  # o clique já foi atendido: o topo mostra o andamento, não repete a ação
                nomes = lista_e(sorted({x["craque"] for x in enviados if x["craque"]})) or "o responsável"
                if any(x["job_status"] in ATIVOS for x in enviados):
                    prox = {"texto": f"Parecer do Vini encaminhado: {nomes} está corrigindo", "etapa": atual["id"], "tipo": "sistema"}
                else:
                    prox = {"texto": f"Abrir a auditoria de texto: {nomes} já recebeu o parecer do Vini", "etapa": atual["id"], "tipo": "voce", "encaminhado": True}
            else:
                prox["acao"] = "resolver_parecer"
    elif rodando:
        prox = {"texto": f"{rodando[0]['craque']}: {POR_ID[rodando[0]['id']]['faz']}", "etapa": rodando[0]["id"], "tipo": "sistema"}
    else:
        pronta = next((e for e in etapas if e["status"] == "pronta"), None)
        if pronta:
            prox = {"texto": pronta["acoes"]["iniciar"]["rotulo"] if pronta["acoes"]["iniciar"] else f"Iniciar {pronta['nome'].lower()}", "etapa": pronta["id"], "tipo": "voce", "acao": "iniciar"}
        elif next(e for e in etapas if e["id"] == "video")["status"] == "aprovada":
            prox = {"texto": "Vídeo aprovado: baixar ou publicar", "etapa": "video", "tipo": "fim"}
        else:
            prox = {"texto": "Sem ação pendente", "etapa": etapas[1]["id"], "tipo": "fim"}
    etapa_atual = rodando[0] if rodando else atual or next((e for e in etapas if e["status"] == "pronta"), None) or next(
        (e for e in reversed(etapas) if e["status"] in ("aprovada", "concluida")), etapas[0])
    return {"prontas": prontas, "decisao": [{"id": e["id"], "nome": e["nome"], "status": e["status"]} for e in decisao], "proxima": prox,
            "aguardando_voce": any(e["status"] in ("aguardando", "falhou", "bloqueio", "desatualizada") for e in etapas), "etapa_atual": etapa_atual["id"], "etapa_atual_nome": etapa_atual["nome"]}


def _so_ativos():
    """Pastas conhecidas ou novas em output/."""
    if not SAIDA.is_dir():
        return []
    return sorted(p.name for p in SAIDA.iterdir() if M.e_producao(p))


def listar():
    grupos = {"aguardando": [], "andamento": [], "arquivadas": []}
    for slug in _so_ativos():
        p = garantir_producao(slug)
        if p["arquivada"]:
            meta = M.ler_json(M.pasta(slug) / "metadados.json", {}) or {}
            grupos["arquivadas"].append({"slug": slug, "titulo": meta.get("titulo") or p["tema"] or slug.replace("-", " ").capitalize(),
                                         "publicado": publicado(slug), "atualizado_em": datetime.fromtimestamp(M.ultima_mudanca(M.pasta(slug))).isoformat(timespec="seconds")})
            continue
        try:
            est = estado(slug)
        except Exception as ex:  # noqa: BLE001
            grupos["andamento"].append({"slug": slug, "titulo": slug, "etapa_nome": "Erro ao ler", "atualizado_em": None, "proxima": {"texto": str(ex)[:120], "etapa": "pesquisa", "tipo": "voce"}})
            continue
        r = est["resumo"]
        linha = {"slug": slug, "titulo": est["titulo"], "etapa_nome": r["etapa_atual_nome"], "etapa": r["etapa_atual"], "atualizado_em": est["atualizado_em"],
                 "proxima": r["proxima"], "decisao": r["decisao"], "formato": est["formato"], "fila": est["fila"], "simulado": est["simulado"], "publicado": est["publicado"]}
        grupos["aguardando" if r["aguardando_voce"] and _entrou_no_fluxo(p) else "andamento"].append(linha)
    for g in grupos.values():
        g.sort(key=lambda x: x.get("atualizado_em") or "", reverse=True)
    return grupos


def _entrou_no_fluxo(p):
    """Pasta de antes do estúdio, sem nenhuma decisão ainda, não está esperando ninguém: fica em andamento até ser aberta e revisada."""
    if p["origem"] == "estudio":
        return True
    return any(um(f"SELECT 1 x FROM {t} WHERE slug=? LIMIT 1", p["slug"]) for t in ("aprovacoes", "itens", "feedback", "jobs"))


def criar_producao(tema, formato="vertical", estilo="sketch", simulado=False, fluxo_id=None, legenda=None, briefing=None, duracao_alvo=None, variante=None, opcoes=None):
    """Sem `fluxo_id`, nasce no fluxo fixo de sempre. Com ele, quem conduz é o grafo publicado (grafos.py)."""
    tema = (tema or "").strip()
    if len(tema) < 3:
        raise Recusado("Escreva o tema do vídeo.", 400)
    if formato not in ("vertical", "horizontal"):
        raise Recusado("Formato inválido.", 400)
    try:
        escolha = estilos.validar_escolha(estilo, variante, opcoes, formato)
    except ValueError as ex:
        raise Recusado(str(ex), 400)
    estilo = escolha["estilo"]
    from . import trabalhos
    slug = ("mock-" if simulado else "") + slugify(tema)
    if um("SELECT slug FROM producoes WHERE slug=?", slug) or M.e_producao(M.pasta(slug)):
        raise Recusado(f"Já existe uma produção com este tema: {slug}. Abra-a na lista.")
    faltas = trabalhos.integracao_faltando("pesquisa", None) if not simulado else []
    if faltas:
        raise Recusado(faltas)
    from . import corte
    if legenda and legenda not in corte.PRESETS_LEGENDA:
        raise Recusado("Estilo de legenda não suportado.", 400)
    M.pasta(slug).mkdir(parents=True, exist_ok=True)
    estilos.gravar(M.pasta(slug), escolha)
    faz("INSERT INTO producoes (slug, tema, formato, estilo, simulado, origem, arquivada, criada_em, briefing, legenda, duracao_alvo, idioma) VALUES (?,?,?,?,?, 'estudio', 0, ?, ?, ?, ?, 'pt-BR')",
        slug, tema, formato, estilo, int(simulado), agora(), (briefing or "").strip() or None, legenda, int(duracao_alvo) if duracao_alvo else None)
    evento(slug, f"Produção criada: {tema}")
    if fluxo_id and not simulado:
        from . import grafos
        grafos.iniciar_execucao(slug, fluxo_id)
    else:
        iniciar_etapa(slug, "pesquisa")
    return slug


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()  # mesma regra do run.py, para o --topic bater com a pasta
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "video"


def _prompt(ctx, chave, grupo=prompts.ETAPA, **extra):
    fa = " --formato horizontal" if ctx.formato == "horizontal" else ""
    return prompts.cabecalho(_prod(ctx), chave) + "\n" + grupo[chave].format(slug=ctx.slug, formato_arg=fa, topico=_topico(ctx), **extra)


def _prod(ctx):
    return {**ctx.prod, "estilo": ctx.estilo, "formato": ctx.formato, "escolha": estilos.ler(ctx.pasta)}


def _topico(ctx):
    return ctx.slug[len("mock-"):] if ctx.prod["simulado"] else ctx.slug


def _comando_video(ctx):
    if ctx.estilo == "3d":
        return ["-m", "media.clay3d", "--slug", ctx.slug]
    cmd = ["run.py", "video", "--topic", _topico(ctx)]
    if ctx.prod["simulado"]:
        cmd.append("--mock")
    if ctx.formato == "horizontal":
        cmd += ["--formato", "horizontal"]
    return cmd


def spec_etapa(ctx, etapa, escopo=None):
    """Como cada etapa roda de verdade. `comando` é relativo ao interpretador do projeto."""
    e = POR_ID[etapa]
    base = {"origem": "etapa", "materiais": [e["material"]]}
    if etapa == "pesquisa" and ctx.prod["simulado"]:
        return {**base, "tipo": "comando", "comando": _comando_video(ctx), "materiais": ORDEM_VERSOES, "raia": "pesado",
                "titulo": "Simulação completa (run.py --mock)", "craque": "run.py"}
    if etapa == "video":
        return {**base, "tipo": "comando", "comando": _comando_video(ctx), "raia": "pesado", "titulo": "Renderizando o vídeo", "craque": "Render", "materiais": ["video", "narracao"]}
    if etapa == "narracao":
        cmd = ["-m", "estudio.narrar", "--slug", ctx.slug, "--formato", ctx.formato]
        if escopo:
            cmd += ["--cenas", ",".join(str(i) for i in escopo)]
        return {**base, "tipo": "comando", "comando": cmd, "raia": "pesado", "craque": "Voz do canal", "escopo": escopo,
                "titulo": f"Gerando a narração de {nome_cenas(escopo)}" if escopo else "Gerando a narração"}
    agente, craque = _agente_de(ctx, e)
    if etapa.startswith("auditoria"):
        prompt = _prompt(ctx, etapa, prompts.AUDITORIA) + prompts.FIM_AUDITORIA
        pulados = ctx.escopos_pulados(etapa)
        if pulados:
            prompt += "\n\nDISPENSAS EXPLÍCITAS DO GUILHERME (não audite nem bloqueie por estes escopos): " + ", ".join(pulados) + ". Audite apenas os demais escopos e deixe claro no parecer quais foram dispensados."
        gravar = {"auditoria_texto": "auditoria_texto.md", "auditoria_final": "auditoria.md"}[etapa]
        return {**base, "tipo": "agente", "agente": agente, "prompt": prompt, "raia": "agente", "craque": craque,
                "titulo": f"{craque}: {e['faz']}", "gravar_em": gravar, "veredito": True}
    if etapa == "cenas" and ctx.versoes.get("cenas") and ctx.obsoleto("cenas"):
        o = ctx.obsoleto("cenas")
        alcance = f"Afetadas: {nome_cenas(o['cenas'])}." if o["cenas"] else "Compare o roteiro com as falas e ache o que mudou."
        prompt = prompts.cabecalho(_prod(ctx), "cenas") + "\n" + prompts.ATUALIZAR_CENAS.format(slug=ctx.slug, alcance=alcance, formato_arg=" --formato horizontal" if ctx.formato == "horizontal" else "")
        return {**base, "tipo": "agente", "agente": agente, "prompt": prompt, "raia": "agente", "craque": craque, "titulo": f"{craque}: atualizando {nome_cenas(o['cenas']) if o['cenas'] else 'as cenas'}"}
    spec = {**base, "tipo": "agente", "agente": agente, "prompt": _prompt(ctx, etapa), "raia": "agente", "craque": craque, "titulo": f"{craque}: {e['faz']}"}
    if etapa == "roteiro":
        spec["em_seguida"] = _spec_courtois(ctx)
    return spec


def _spec_courtois(ctx):
    return {"origem": "cadeia", "materiais": ["roteiro"], "tipo": "agente", "agente": "courtois-revisor-fatos", "prompt": _prompt(ctx, "courtois"), "raia": "agente", "craque": "Courtois",
            "titulo": "Courtois: conferindo os fatos"}


def assinatura_de(slug, etapa, spec):
    entradas = {k: _hash_dep(slug, k) for k in ("pesquisa", "roteiro", "cenas", "narracao", "metadados", "video") if k != POR_ID[etapa]["material"]}
    return M.sha_texto(json.dumps([etapa, spec.get("escopo"), spec.get("feedback_ids"), spec.get("prompt"), spec.get("comando"), entradas], sort_keys=True, ensure_ascii=False))


def inserir_job(slug, etapa, spec, assinatura=None, tentativa_de=None):
    """Grava na fila. Se já há um trabalho ativo nesta etapa, o índice único recusa e devolve o existente."""
    assinatura = assinatura or assinatura_de(slug, etapa, spec)
    if spec.get("exigir_mudanca"):
        spec = {**spec, "hash_antes": hash_ajustes(slug, spec["exigir_mudanca"])}
    try:
        cur = faz("INSERT INTO jobs (slug, etapa, raia, titulo, craque, assinatura, status, spec, tentativa_de, criada_em) VALUES (?,?,?,?,?,?, 'fila', ?, ?, ?)",
                  slug, etapa, spec["raia"], spec["titulo"], spec.get("craque"), assinatura, json.dumps(spec, ensure_ascii=False), tentativa_de, agora())
    except sqlite3.IntegrityError:
        return um("SELECT * FROM jobs WHERE slug=? AND etapa=? AND status IN ('fila','rodando')", slug, etapa), False
    return um("SELECT * FROM jobs WHERE id=?", cur.lastrowid), True


def iniciar_etapa(slug, etapa, forcar=False, escopo=None):
    if etapa not in POR_ID:
        raise Recusado("Etapa desconhecida.", 404)
    from . import trabalhos
    sincronizar(slug, forcar=True)
    ctx = Contexto(slug)
    e = POR_ID[etapa]
    ativo = ctx.job_ativo(etapa)
    if ativo:
        return ativo, False  # duplo clique ou recarga: é o mesmo trabalho
    if not ctx.aplicavel(e):
        raise Recusado(f"{e['nome']} não se aplica a esta produção.")
    faltas = trabalhos.integracao_faltando(etapa, ctx) + ctx.requisitos(etapa)
    if faltas and ctx.em_grafo:
        from . import grafos
        b = grafos.bloqueios(slug)["por_material"].get(e["material"])
        if b:
            faltas.append(f"O fluxo está parado em “{b['nome']}” ({b['status']}){': ' + str(b['nota'])[:160] if b.get('nota') else ''}. Resolva esse passo no fluxo (Tentar de novo, se falhou).")
    if faltas:
        raise Recusado(faltas)
    if etapa == "narracao" and escopo is None:
        escopo = _escopo_narracao(ctx)
    spec = spec_etapa(ctx, etapa, escopo)
    ass = assinatura_de(slug, etapa, spec)
    if not forcar and ctx.versoes.get(e["material"]) and not ctx.obsoleto(e["material"]):
        ja = um("SELECT * FROM jobs WHERE slug=? AND etapa=? AND assinatura=? AND status='ok' ORDER BY id DESC LIMIT 1", slug, etapa, ass)
        if ja:
            return ja, False  # mesmo pedido com as mesmas entradas já foi feito
    job, novo = inserir_job(slug, etapa, spec, ass)
    if novo:
        evento(slug, f"Iniciado: {spec['titulo']}")
        faz("UPDATE jobs SET dispensado=1 WHERE slug=? AND etapa=? AND status='falhou'", slug, etapa)
    return job, novo


def tentar_novamente(job_id):
    j = um("SELECT * FROM jobs WHERE id=?", job_id)
    if not j or j["status"] not in ("falhou", "cancelado"):
        raise Recusado("Este trabalho não pode ser repetido.")
    spec = json.loads(j["spec"])
    from . import trabalhos
    ctx = Contexto(j["slug"])
    if spec.get("origem") == "etapa":
        faltas = trabalhos.integracao_faltando(j["etapa"], ctx) + ctx.requisitos(j["etapa"])
        if faltas:
            raise Recusado(faltas)
    novo, criado = inserir_job(j["slug"], j["etapa"], spec, j["assinatura"], tentativa_de=j["id"])
    if criado:
        faz("UPDATE jobs SET dispensado=1 WHERE id=?", j["id"])
        faz("UPDATE feedback SET job_id=? WHERE job_id=?", novo["id"], j["id"])
        evento(j["slug"], f"Nova tentativa: {j['titulo']}")
    return novo, criado


def pular_auditoria_vini(slug, etapa, escopo):
    """Registra uma dispensa explícita do dono, presa ao hash exato que decidiu não auditar."""
    sincronizar(slug, forcar=True)
    dep = ESCOPO_VINI.get(etapa, {}).get(escopo)
    if not dep:
        raise Recusado("Escopo de auditoria desconhecido.", 400)
    h = _hash_dep(slug, dep)
    if not h:
        raise Recusado("Esse material ainda não existe para ser dispensado.")
    faz("INSERT OR IGNORE INTO dispensas_vini (slug, etapa, escopo, hash, criada_em) VALUES (?,?,?,?,?)", slug, etapa, escopo, h, agora())
    evento(slug, f"Guilherme dispensou auditoria do Vini: {etapa} / {escopo} ({h[:10]})")
    if etapa == "auditoria_final" and Contexto(slug).versoes.get("video"):
        M.pasta(slug).joinpath("auditoria.md").write_text(
            "**APROVADO COM DISPENSA DO GUILHERME**\n\nO Guilherme dispensou a auditoria final do Vini para os metadados desta versão. Este registro não afirma que o Vini auditou o vídeo.\n",
            encoding="utf-8")
        sincronizar(slug, forcar=True, assentar=False)
    return estado(slug, sincroniza=False)


def manter_cenas_aprovadas(slug):
    """Restaura o roteiro exato usado pela versão aprovada das cenas; preserva cenas e demais arquivos."""
    sincronizar(slug, forcar=True)
    ctx = Contexto(slug)
    cenas = ctx.versoes.get("cenas")
    if not cenas:
        raise Recusado("Ainda não há cenas para manter.")
    if ctx.pendentes("cenas"):
        raise Recusado("Só é possível manter esta versão depois que todas as cenas estiverem aprovadas.")
    dep = cenas.get("deps", {}).get("roteiro")
    roteiro = versao_dict(um("SELECT * FROM versoes WHERE slug=? AND material='roteiro' AND hash=? ORDER BY numero DESC LIMIT 1", slug, dep or ""))
    if not roteiro:
        raise Recusado("Não encontrei a versão exata do roteiro usada para criar estas cenas; nada foi alterado.")
    sha = roteiro["manifesto"]["arquivos"].get("roteiro.txt")
    texto = M.caminho_blob(sha).read_bytes() if sha and M.caminho_blob(sha).exists() else b""
    if not texto:
        raise Recusado("O histórico não contém o texto do roteiro; nada foi alterado.")
    nar_sha = roteiro["manifesto"]["arquivos"].get("narracao.txt")
    narracao = M.ler_blob_texto(nar_sha) if nar_sha else ""
    if not narracao:
        raise Recusado("O histórico não contém a narração usada pelas cenas; nada foi alterado.")
    destino = M.pasta(slug) / "roteiro.txt"
    direcao = M.pasta(slug) / "direcao_viral.md"
    conteudo_direcao = M.ler_texto(direcao)
    cabecalho = re.search(r"(?im)^##\s*Narra[^\n]*\n", conteudo_direcao)
    if not cabecalho:
        raise Recusado("Não encontrei a seção de narração para restaurar; nada foi alterado.")
    proximo = re.search(r"(?m)^##\s+", conteudo_direcao[cabecalho.end():])
    fim = cabecalho.end() + proximo.start() if proximo else len(conteudo_direcao)
    nova_direcao = conteudo_direcao[:cabecalho.end()] + "\n" + narracao.rstrip() + "\n\n" + conteudo_direcao[fim:]
    temporario = destino.with_name("roteiro.txt.restaurando")
    temp_direcao = direcao.with_name("direcao_viral.md.restaurando")
    temporario.write_bytes(texto)
    temp_direcao.write_text(nova_direcao, encoding="utf-8")
    temporario.replace(destino)
    temp_direcao.replace(direcao)
    sincronizar(slug, forcar=True, assentar=False)
    atual = ultima_versao(slug, "roteiro")
    if not atual or atual["hash"] != roteiro["hash"]:
        raise Recusado("Não consegui confirmar a restauração do roteiro; as cenas foram preservadas.")
    if atual["id"] not in Contexto(slug).aprovadas:
        registrar_aprovacao(slug, "roteiro", atual)
    # O clique mantém explicitamente o roteiro e as cenas já aprovados sem pedir nova auditoria desses escopos.
    for scope in ("roteiro", "cenas"):
        dep_hash = _hash_dep(slug, ESCOPO_VINI["auditoria_texto"][scope])
        faz("INSERT OR IGNORE INTO dispensas_vini (slug, etapa, escopo, hash, criada_em) VALUES (?,?,?,?,?)",
            slug, "auditoria_texto", scope, dep_hash, agora())
    evento(slug, f"Roteiro restaurado da versão usada pelas cenas aprovadas (v{roteiro['numero']}); cenas preservadas.")
    return estado(slug, sincroniza=False)


def dispensar_falha(job_id):
    """Fecha o aviso de falha. Os pedidos que estavam com esse trabalho voltam a ser rascunho: nada se perde."""
    faz("UPDATE jobs SET dispensado=1 WHERE id=? AND status IN ('falhou','cancelado')", job_id)
    faz("UPDATE feedback SET status='rascunho', job_id=NULL WHERE job_id=? AND status='enviado'", job_id)


def _exige_versao_atual(slug, material, versao_id):
    v = ultima_versao(slug, material)
    if not v or v["id"] != versao_id:
        raise Recusado("Esta versão não é mais a atual: revise a versão nova antes de decidir.")
    return v


def aprovar(slug, material, versao_id):
    sincronizar(slug, forcar=True)
    v = _exige_versao_atual(slug, material, versao_id)
    ctx = Contexto(slug)
    e = next(x for x in ETAPAS if x["material"] == material)
    if not e["gate"]:
        raise Recusado(f"{e['nome']} não tem aprovação sua: a etapa é conferida pelo {e['craque']}.")
    if ctx.job_ativo(e["id"]):
        raise Recusado(f"{e['craque']} ainda está trabalhando nesta etapa.")
    motivos = ctx.requisitos_aprovacao(e["id"])
    if feedback_rascunhos(slug, material, versao_id):
        motivos.append("Envie ou remova os ajustes anotados nesta versão antes de aprovar.")
    if ctx.obsoleto(material):
        motivos.append("Esta versão está desatualizada: gere a nova antes de aprovar.")
    if ctx.falha(e["id"]):
        motivos.append("Resolva a falha desta etapa antes de aprovar.")
    if motivos:
        raise Recusado(motivos)
    registrar_aprovacao(slug, material, v)
    return avancar(slug, e["id"])


def registrar_aprovacao(slug, material, v):
    """A versão e os itens dela ficam aprovados, tudo ou nada. Quem decide se pode é quem chama."""
    versao_id = v["id"]
    agora_ = agora()
    con().execute("BEGIN IMMEDIATE")
    try:
        for sha in v["manifesto"]["itens"].values():
            faz("INSERT INTO itens (slug, material, sha, decisao, versao_id, criada_em) VALUES (?,?,?,'aprovado',?,?) "
                "ON CONFLICT (slug, material, sha) DO UPDATE SET decisao='aprovado', versao_id=excluded.versao_id, criada_em=excluded.criada_em",
                slug, material, sha, versao_id, agora_)
        faz("INSERT OR IGNORE INTO aprovacoes (slug, material, versao_id, criada_em) VALUES (?,?,?,?)", slug, material, versao_id, agora_)
        con().execute("COMMIT")
    except Exception:
        con().execute("ROLLBACK")
        raise
    evento(slug, f"Aprovado: {NOME_MATERIAL[material]} v{v['numero']}")


def decidir_item(slug, material, versao_id, item, decisao):
    """Aprova um trecho ou asset. A decisão fica no conteúdo: quando o agente refaz só outro item, esta continua valendo."""
    if decisao not in ("aprovado", "pendente"):
        raise Recusado("Decisão inválida.", 400)
    sincronizar(slug, forcar=True)
    v = _exige_versao_atual(slug, material, versao_id)
    sha = v["manifesto"]["itens"].get(item)
    if not sha:
        raise Recusado(f"Item não encontrado nesta versão: {item}.", 404)
    ctx = Contexto(slug)
    e = next(x for x in ETAPAS if x["material"] == material)
    if decisao == "aprovado":
        motivos = ctx.requisitos_aprovacao(e["id"])
        if motivos:
            raise Recusado(motivos)
        faz("DELETE FROM feedback WHERE slug=? AND material=? AND versao_id=? AND item=? AND status='rascunho'", slug, material, versao_id, item)
        faz("INSERT INTO itens (slug, material, sha, decisao, versao_id, criada_em) VALUES (?,?,?,'aprovado',?,?) "
            "ON CONFLICT (slug, material, sha) DO UPDATE SET decisao='aprovado', versao_id=excluded.versao_id, criada_em=excluded.criada_em",
            slug, material, sha, versao_id, agora())
    else:
        faz("DELETE FROM itens WHERE slug=? AND material=? AND sha=?", slug, material, sha)
    ctx = Contexto(slug)
    if decisao == "aprovado" and not ctx.pendentes(material) and not feedback_rascunhos(slug, material, versao_id):
        faz("INSERT OR IGNORE INTO aprovacoes (slug, material, versao_id, criada_em) VALUES (?,?,?,?)", slug, material, versao_id, agora())
        evento(slug, f"Aprovado: {NOME_MATERIAL[material]} v{v['numero']} (todos os itens)")
        return avancar(slug, e["id"])
    if decisao != "aprovado":
        faz("DELETE FROM aprovacoes WHERE versao_id=?", versao_id)
    return []


def anotar_feedback(slug, material, versao_id, texto, item=None, cena=None, tempo_s=None, categoria=None):
    texto = (texto or "").strip()
    if not texto:
        raise Recusado("Escreva o que precisa mudar.", 400)
    v = _exige_versao_atual(slug, material, versao_id)
    if item and item not in v["manifesto"]["itens"]:
        raise Recusado(f"Item não encontrado nesta versão: {item}.", 404)
    if item and item.startswith("cena_") and cena is None:
        cena = int(item.split("_")[1])
    cur = faz("INSERT INTO feedback (slug, material, versao_id, item, cena, tempo_s, categoria, texto, criada_em) VALUES (?,?,?,?,?,?,?,?,?)",
              slug, material, versao_id, item, cena, tempo_s, categoria, texto, agora())
    if item:  # anotar um pedido sobre o item retira a aprovação que ele tinha
        sha = v["manifesto"]["itens"][item]
        faz("DELETE FROM itens WHERE slug=? AND material=? AND sha=?", slug, material, sha)
        faz("DELETE FROM aprovacoes WHERE versao_id=?", versao_id)
    return um("SELECT * FROM feedback WHERE id=?", cur.lastrowid)


def remover_feedback(slug, fid):
    faz("DELETE FROM feedback WHERE id=? AND slug=? AND status='rascunho'", fid, slug)


def enviar_ajustes(slug, material, versao_id):
    """Entrega os pedidos anotados ao agente responsável, com material, versão e o trecho apontado."""
    from . import trabalhos
    sincronizar(slug, forcar=True)
    v = _exige_versao_atual(slug, material, versao_id)
    rascunhos = feedback_rascunhos(slug, material, versao_id)
    if not rascunhos:
        raise Recusado("Não há ajuste anotado nesta versão.")
    ctx = Contexto(slug)
    faltas = trabalhos.integracao_faltando("roteiro", ctx)
    if faltas:
        raise Recusado(faltas)
    grupos = {}
    for f in rascunhos:
        grupos.setdefault(_dono_feedback(ctx, material, f["categoria"]), []).append(f)
    criados = []
    for dono, fs in grupos.items():
        if ctx.job_ativo(dono) or any(j["status"] in ATIVOS and POR_ID[dono]["material"] in json.loads(j["spec"]).get("materiais", []) for j in ctx.jobs):
            raise Recusado(f"{POR_ID[dono]['nome']} já está em execução: aguarde terminar para enviar novos ajustes.")
    for dono, fs in grupos.items():
        spec = _spec_ajuste(ctx, material, v, dono, fs)
        job, novo = inserir_job(slug, dono, spec)
        if novo:
            faz(f"UPDATE feedback SET status='enviado', job_id=? WHERE id IN ({','.join('?' * len(fs))})", job["id"], *[f["id"] for f in fs])
            evento(slug, f"{len(fs)} ajuste(s) enviado(s) para {spec['craque']} sobre {NOME_MATERIAL[material]} v{v['numero']}")
            criados.append(job)
    return criados


def _spec_ajuste(ctx, material, v, dono, fs):
    agente, craque = _craque_dono(ctx, dono)
    cfg_voz = _cfg_voz()
    fa = " --formato horizontal" if ctx.formato == "horizontal" else ""
    tarefa = prompts.TAREFA_AJUSTE[dono].format(slug=ctx.slug, formato_arg=fa, velocidade=cfg_voz.get("velocidade", 1.15), exaggeration=cfg_voz.get("exaggeration", 0.6))
    itens = "\n".join(prompts.descrever_feedback(f, fmt_tempo) for f in fs)
    prompt = prompts.cabecalho(_prod(ctx), dono) + "\n" + prompts.AJUSTE.format(material=NOME_MATERIAL[material].split(" ", 1)[1], versao=v["numero"], hash=v["hash"][:10], itens=itens, tarefa=tarefa)
    spec = {"tipo": "agente", "agente": agente, "prompt": prompt, "raia": "agente", "craque": craque, "origem": "ajuste", "materiais": [POR_ID[dono]["material"]],
            "feedback_ids": [f["id"] for f in fs], "titulo": f"{craque}: aplicando {len(fs)} ajuste{'s' if len(fs) > 1 else ''} em {NOME_MATERIAL[material]} v{v['numero']}", "exigir_mudanca": POR_ID[dono]["material"]}
    if ctx.em_grafo and dono != "narracao":
        from . import grafos
        foto = grafos.agente_de_no_para(ctx.slug, POR_ID[dono]["material"])
        if foto:  # a execução continua com o agente, e a versão dele, com que começou
            spec.update(agente=foto["id"], craque=foto["craque"], sistema={"corpo": foto["corpo"], "modelo": foto["modelo"], "ferramentas": foto["ferramentas"], "versao": foto["versao"], "sha": foto["sha"]})
            spec["titulo"] = f"{foto['craque']}: aplicando {len(fs)} ajuste{'s' if len(fs) > 1 else ''} em {NOME_MATERIAL[material]} v{v['numero']}"
    if dono == "roteiro":
        spec["em_seguida"] = _spec_courtois(ctx)
    elif dono == "narracao":
        cenas = sorted({f["cena"] for f in fs if f.get("cena") is not None})
        spec["exigir_mudanca"] = "voz_ajustes"
        spec["materiais"] = ["narracao"]
        cenas = cenas if all(f.get("cena") is not None for f in fs) else None  # pedido geral: refaz tudo
        spec["em_seguida"] = spec_etapa(ctx, "narracao", cenas) | {"origem": "cadeia"}
    return spec


def _cfg_voz():
    try:
        import yaml
        return yaml.safe_load(open(REPO / "config_shorts.yaml", encoding="utf-8")).get("voz", {})
    except Exception:  # noqa: BLE001
        return {}


def hash_ajustes(slug, mudanca):
    if mudanca == "voz_ajustes":
        p = M.pasta(slug) / "voz_ajustes.json"
        return M.sha_arquivo(p) if p.exists() else None
    m = M.manifesto(slug, mudanca)
    return M.fingerprint(*m) if m else None


def avancar(slug, etapa, assentar=True):
    """Dispara o que esta etapa libera. Só o que for automático por contrato (agentes de texto): narração e render ficam com botão."""
    sincronizar(slug, forcar=True, assentar=assentar)
    if um("SELECT 1 x FROM execucoes WHERE slug=? LIMIT 1", slug):
        from . import grafos
        material = POR_ID[etapa]["material"]
        return grafos.ao_aprovar(slug, material, (ultima_versao(slug, material) or {}).get("id"))
    criados = []
    ctx = Contexto(slug)
    for g in ctx.autos_apos(etapa):
        spec = spec_etapa(ctx, g)
        ja = um("SELECT id FROM jobs WHERE slug=? AND etapa=? AND assinatura=? AND status='ok'", slug, g, assinatura_de(slug, g, spec))
        if ja and not ctx.obsoleto(POR_ID[g]["material"]):
            continue
        from . import trabalhos
        if trabalhos.integracao_faltando(g, ctx):
            continue
        job, novo = inserir_job(slug, g, spec)
        if novo:
            evento(slug, f"Iniciado automaticamente: {spec['titulo']}")
            criados.append(job["id"])
    return criados


def concluir_job(job, resultado):
    """Chamado pelo monitor quando um trabalho termina. Confere se ele fez o que devia, e só então libera o próximo."""
    spec = json.loads(job["spec"])
    slug = job["slug"]
    erro = resultado.get("erro")
    if spec.get("origem") == "gerar_tema":
        faz("UPDATE jobs SET status=?, erro=?, resumo=?, custo_usd=?, terminado_em=? WHERE id=?", "falhou" if erro else "ok", erro, resultado.get("resumo"), resultado.get("custo_usd"), agora(), job["id"])
        return  # o tema aparece na lista porque o Modric gravou o arquivo dele
    if spec.get("origem") == "teste_agente":
        from . import agentes
        faz("UPDATE jobs SET status=?, erro=?, resumo=?, custo_usd=?, terminado_em=? WHERE id=?", "falhou" if erro else "ok", erro, resultado.get("resumo"), resultado.get("custo_usd"), agora(), job["id"])
        agentes.teste_terminou(spec, job, resultado)
        return
    if not erro and spec.get("exigir_mudanca") and spec.get("hash_antes") == hash_ajustes(slug, spec["exigir_mudanca"]):
        erro = f"{job['craque']} terminou sem alterar o material. Nada mudou, então a versão continua a mesma."
    status = "falhou" if erro else "ok"
    faz("UPDATE jobs SET status=?, erro=?, resumo=?, custo_usd=?, terminado_em=? WHERE id=?", status, erro, resultado.get("resumo"), resultado.get("custo_usd"), agora(), job["id"])
    if erro:
        evento(slug, f"Falhou: {job['titulo']}")
        if spec.get("exec"):
            from . import grafos
            grafos.job_terminou(job, spec, erro)
        return
    evento(slug, f"Concluído: {job['titulo']}")
    faz("UPDATE feedback SET status='atendido' WHERE job_id=?", job["id"])
    if spec.get("em_seguida"):
        proximo = dict(spec["em_seguida"])
        inserir_job(slug, job["etapa"], proximo)
        return  # a cadeia continua: a nova versão só aparece depois do último elo
    if spec.get("exec"):
        from . import grafos
        grafos.job_terminou(job, spec, None)
        return
    sincronizar(slug, forcar=True, assentar=False)
    if job["etapa"] == "corte_fontes":
        return  # preparar a imagem do editor não muda nenhum material do projeto
    _revalidar(slug, POR_ID[job["etapa"]]["material"])
    if job["etapa"] == "cenas" and _previa_antiga(slug):
        cmd = ["-m", "media.sketch", "--slug", slug] + (["--formato", "horizontal"] if (um("SELECT formato FROM producoes WHERE slug=?", slug) or {}).get("formato") == "horizontal" else []) + ["--previa"]
        inserir_job(slug, "cenas", {"tipo": "comando", "comando": cmd, "raia": "pesado", "craque": "Prévia", "titulo": "Atualizando a prévia das cenas", "materiais": ["cenas"], "origem": "cadeia"})
        return
    if um("SELECT 1 x FROM execucoes WHERE slug=? AND status='ativa'", slug):
        from . import grafos
        grafos.depois_de_job(slug)
        return
    avancar(slug, job["etapa"], assentar=False)


def _revalidar(slug, material):
    """O trabalho terminou sem mudar o conteúdo (ex.: o Vini repetiu o mesmo parecer): não há versão nova, mas a versão atual
    foi conferida contra os insumos de agora. Sem isso, ela ficaria desatualizada para sempre."""
    v = ultima_versao(slug, material)
    if v and material in DEPS:
        faz("UPDATE versoes SET deps=? WHERE id=?", json.dumps({k: _hash_dep(slug, k) for k in DEPS[material]}), v["id"])


def _previa_antiga(slug):
    p = M.pasta(slug)
    s, f = (p / "cenas.json" if estilos.por_dados(M.estilo_das_cenas(slug)) else p / "sketch_cenas.py"), p / "previa.jpg"
    return s.exists() and (not f.exists() or f.stat().st_mtime < s.stat().st_mtime - 1)


def arquivar(slug, arquivada):
    garantir_producao(slug)
    faz("UPDATE producoes SET arquivada=? WHERE slug=?", int(bool(arquivada)), slug)


# ---------- Conteúdo para as telas ----------

def _versao_por_id(slug, material, versao_id):
    if versao_id:
        return versao_dict(um("SELECT * FROM versoes WHERE slug=? AND material=? AND id=?", slug, material, versao_id))
    return ultima_versao(slug, material)


def blob_url(sha, nome):
    return f"/blob/{sha}?nome={nome}"


def conteudo(slug, material, versao_id=None):
    garantir_producao(slug)
    sincronizar(slug)
    ctx = Contexto(slug)
    v = _versao_por_id(slug, material, versao_id)
    versoes = varios("SELECT id, numero, origem, criada_em FROM versoes WHERE slug=? AND material=? ORDER BY numero DESC", slug, material)
    aprovadas = ctx.aprovadas
    for x in versoes:
        x["aprovada"] = x["id"] in aprovadas
    atual = versoes[0]["id"] if versoes else None
    saida = {"material": material, "versao": None, "versoes": versoes, "feedback": [], "dados": None, "e_atual": bool(v and v["id"] == atual)}
    if not v:
        return saida
    saida["versao"] = {"id": v["id"], "numero": v["numero"], "origem": v["origem"], "criada_em": v["criada_em"], "aprovada": v["id"] in aprovadas}
    saida["feedback"] = varios("SELECT f.*, v.numero AS versao_numero, j.craque AS job_craque, j.status AS job_status FROM feedback f JOIN versoes v ON v.id=f.versao_id "
                               "LEFT JOIN jobs j ON j.id=f.job_id WHERE f.slug=? AND f.material=? ORDER BY f.id DESC LIMIT 200", slug, material)
    arquivos = v["manifesto"]["arquivos"]
    fn = {"roteiro": _dados_roteiro, "narracao": _dados_narracao, "componentes": _dados_itens_componentes, "cenas": _dados_itens_cenas, "video": _dados_video}.get(material, _dados_texto)
    saida["dados"] = fn(ctx, v, arquivos)
    if material.startswith("auditoria") and ctx.auditoria_pulada(material):
        saida["dados"]["parecer"] = "PULADO PELO GUILHERME"
        saida["dados"]["escopos_pulados"] = ctx.escopos_pulados(material)
    return saida


def _cenas_visao(ctx, afetadas=()):
    direcao = M.direcao_por_cena(ctx.slug)
    tempos, exato = M.tempos_cenas(ctx.slug, ctx.cenas)
    return [{"i": i, "fala": M.fala_de(c), "tela": M.textos_tela(c), "direcao": direcao.get(i, {}).get("direcao") or c.get("acao") or c.get("desenho") or c.get("tipo") or "", "inicio": tempos[i]["inicio"],
             "dur": tempos[i]["dur"], "tempo_exato": exato, "afetada": i in afetadas} for i, c in enumerate(ctx.cenas)], exato


def _dados_roteiro(ctx, v, arquivos):
    texto = M.ler_blob_texto(arquivos.get("roteiro.txt", ""))
    narr = M.ler_blob_texto(arquivos["narracao.txt"]) if "narracao.txt" in arquivos else ""
    anterior = versao_dict(um("SELECT * FROM versoes WHERE slug=? AND material='roteiro' AND numero=? ", ctx.slug, v["numero"] - 1))
    mudancas = None
    if anterior:
        a = anterior["manifesto"]["arquivos"]
        base_nova, base_ant = (narr, M.ler_blob_texto(a["narracao.txt"])) if narr and "narracao.txt" in a else (texto, M.ler_blob_texto(a.get("roteiro.txt", "")))
        mudancas = {"de": anterior["numero"], "ops": M.diff_palavras(base_ant, base_nova)}
    obs = ctx.obsoleto("cenas")
    cenas, _ = _cenas_visao(ctx, obs["cenas"] if obs else ())
    from . import revisao
    manuais = revisao.direcoes_manuais(ctx.slug)
    for c in cenas:
        c["direcao_manual"] = c["i"] in manuais
        if c["i"] in manuais:
            c["direcao"] = manuais[c["i"]]
    atuais = M.ler_blob_texto(ctx.versoes["roteiro"]["manifesto"]["arquivos"].get("roteiro.txt", "")) if ctx.versoes.get("roteiro") else ""
    return {"texto": texto, "narracao": narr, "cenas": cenas, "paragrafos": [p.strip() for p in re.split(r"\n\s*\n", narr or texto) if p.strip()], "mudancas": mudancas,
            "direcao_geral": M.ler_texto(ctx.pasta / "direcao_viral.md"), "revisao": M.ler_texto(ctx.pasta / "revisao.md"), "cenas_versao_ok": atuais == texto}


def _dados_narracao(ctx, v, arquivos):
    itens = v["manifesto"]["itens"]
    obs = ctx.obsoleto("narracao") if v["id"] == ctx.versoes["narracao"]["id"] else None
    trechos = []
    textos = json.loads(M.ler_blob_texto(arquivos["textos.json"]) or "null") if "textos.json" in arquivos else ctx.textos
    durs = json.loads(M.ler_blob_texto(arquivos["falas.json"]) or "{}") if "falas.json" in arquivos else {}
    t = 0.0
    for nome, sha in sorted(itens.items(), key=lambda kv: (0, int(kv[0].split("_")[1])) if kv[0].startswith("cena_") else (1, 0)):
        if not nome.startswith("cena_"):
            trechos.append({"item": nome, "i": None, "sha": sha, "url": blob_url(arquivos["audio.wav"], "audio.wav"), "texto": "Áudio único do vídeo. Marque o tempo do que quer ajustar.", "decisao": ctx.itens.get(("narracao", sha))})
            continue
        i = int(nome.split("_")[1])
        c = ctx.cenas[i] if i < len(ctx.cenas) else {}
        dur = durs.get(str(i), {}).get("dur") or 0
        trechos.append({"item": nome, "i": i, "sha": sha, "url": blob_url(arquivos[nome + ".wav"], nome + ".wav"), "texto": (textos[i] if textos and i < len(textos) else M.fala_de(c)),
                        "dur": dur, "inicio": round(t, 2), "decisao": ctx.itens.get(("narracao", sha)), "desatualizado": bool(obs and i in obs["cenas"])})
        t += float(dur or 0)
    return {"trechos": trechos, "total": round(t, 2), "ajustes": M.ler_json(ctx.pasta / "voz_ajustes.json", {}) or {}}


def _dados_itens_componentes(ctx, v, arquivos):
    direcao = M.direcao_por_cena(ctx.slug)
    por_funcao = {}
    for i, d in direcao.items():
        for f in d["funcoes"]:
            por_funcao.setdefault(f, []).append(i)
    grupos = {}
    for nome, sha in v["manifesto"]["itens"].items():
        cenas = por_funcao.get(nome, [])
        arq = next((a for a in arquivos if a.rsplit(".", 1)[0] == nome), None)
        item = {"item": nome, "sha": sha, "url": blob_url(arquivos[arq], arq), "cenas": cenas, "decisao": ctx.itens.get(("componentes", sha))}
        chave = cenas[0] if cenas else -1
        grupos.setdefault(chave, []).append(item)
    saida = [{"titulo": f"Cena {k + 1}" if k >= 0 else "Sem cena definida", "cena": k if k >= 0 else None, "fala": M.fala_de(ctx.cenas[k]) if 0 <= k < len(ctx.cenas) else "", "itens": grupos[k]}
             for k in sorted(grupos, key=lambda x: (x < 0, x))]
    return {"grupos": saida, "total": len(v["manifesto"]["itens"]), "pendentes": sum(1 for sha in v["manifesto"]["itens"].values() if ctx.itens.get(("componentes", sha)) != "aprovado"),
            "fase": ctx.fase, "contato": None}


def _dados_itens_cenas(ctx, v, arquivos):
    itens = []
    for nome, sha in v["manifesto"]["itens"].items():
        i = int(nome.split("_")[1]) if nome.startswith("cena_") else None
        c = ctx.cenas[i] if i is not None and i < len(ctx.cenas) else {}
        itens.append({"item": nome, "sha": sha, "url": blob_url(arquivos[nome + ".jpg"], nome + ".jpg"), "i": i, "fala": M.fala_de(c), "tela": M.textos_tela(c), "decisao": ctx.itens.get(("cenas", sha)), "largo": True})
    itens.sort(key=lambda x: (x["i"] is None, x["i"] or 0))
    obs = ctx.obsoleto("cenas")
    return {"grupos": [{"titulo": "Cenas desenhadas (3 quadros de cada)", "itens": itens, "cena": None, "fala": ""}] if itens else [], "total": len(itens),
            "pendentes": sum(1 for x in itens if x["decisao"] != "aprovado"), "afetadas": obs["cenas"] if obs else [], "cenas": _cenas_visao(ctx, obs["cenas"] if obs else ())[0], "estilo": ctx.estilo}


def _dados_video(ctx, v, arquivos):
    aud = ctx.versoes.get("auditoria_final")
    parecer = M.status_auditoria(M.ler_blob_texto(next(iter(aud["manifesto"]["arquivos"].values())))) if aud else None
    cenas, exato = _cenas_visao(ctx)
    aprovada = v["id"] in ctx.aprovadas
    from . import corte
    exportada = corte.exportacao_do_video(ctx.slug, arquivos["video.mp4"])
    if exportada:  # o vídeo saiu do editor: os tempos das cenas são os do corte, não os do render
        segs = json.loads(exportada["compilado"])["segmentos"]
        cenas, exato = [{"i": s["i"], "fala": s["fala"], "tela": [], "direcao": "", "inicio": s["ini"], "dur": round(s["fim"] - s["ini"], 2), "tempo_exato": True, "afetada": False} for s in segs], True
    return {"url": blob_url(arquivos["video.mp4"], "video.mp4"), "video_sha": arquivos["video.mp4"], "do_corte": bool(exportada), "corte": corte.situacao(ctx.slug), "formato": ctx.formato, "cenas": cenas, "tempos_exatos": exato, "parecer_vini": parecer, "conformidade": M.ler_texto(ctx.pasta / "CONFORMIDADE.md"),
            "download": f"/download/{ctx.slug}?versao={v['id']}" if aprovada else None, "publicar": f"python run.py publish --slug {ctx.slug}",
            "metadados": M.ler_json(ctx.pasta / "metadados.json", {}) or {}, "publicado": publicado(ctx.slug), "custo": M.ler_json(ctx.pasta / "custo.json", None)}


def _dados_texto(ctx, v, arquivos):
    partes = [{"nome": n, "texto": M.ler_blob_texto(s)} for n, s in arquivos.items() if n.rsplit(".", 1)[-1] in ("md", "txt", "json")]
    meta = None
    if v["material"] == "metadados" and partes:
        try:
            meta = json.loads(partes[0]["texto"])
        except ValueError:
            pass
    parecer = M.status_auditoria(partes[0]["texto"]) if v["material"].startswith("auditoria") and partes else None
    return {"partes": partes, "metadados": meta, "parecer": parecer}


def detalhes(slug):
    """Logs e histórico, sob demanda."""
    return {"eventos": varios("SELECT texto, criada_em FROM eventos WHERE slug=? ORDER BY id DESC LIMIT 80", slug),
            "jobs": [status_job_publico(j) for j in varios("SELECT * FROM jobs WHERE slug=? ORDER BY id DESC LIMIT 30", slug)], "pasta": str(M.pasta(slug)), "raiz": str(RAIZ)}
