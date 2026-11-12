"""Fluxos como grafo: rascunho, validação, versões publicadas e o executor que obedece ao grafo publicado.

O fluxo fixo de fluxo.py continua valendo para as produções que não nasceram de um grafo. Aqui cada execução guarda a foto do grafo e dos
agentes com que começou: publicar outra versão ou editar um agente não muda o que já está andando. O trabalho pesado continua na mesma
fila (jobs), que já recusa duplicata; a transição de estado de cada nó é condicional, então clique duplo não dispara nada duas vezes.
"""
import json
import re
import threading
from collections import deque

from media import estilos

from . import agentes as AG, fluxo, materiais as M, prompts
from .banco import agora, con, evento, faz, um, varios
from .fluxo import Recusado

PADRAO = "canal"
TIPOS = {
    "entrada": {"nome": "Briefing", "cor": "entrada", "ajuda": "Começo do fluxo: o tema ou briefing do projeto."},
    "agente": {"nome": "Agente", "cor": "agente", "ajuda": "Um agente de .claude/agents faz a tarefa."},
    "aprovacao": {"nome": "Aprovação humana", "cor": "aprovacao", "ajuda": "Para e espera sua decisão sobre uma versão."},
    "condicao": {"nome": "Condição", "cor": "condicao", "ajuda": "Escolhe um caminho (sim ou não) pelo estado do projeto."},
    "juncao": {"nome": "Junção", "cor": "juncao", "ajuda": "Espera todos os caminhos ativos que chegam nela."},
    "render": {"nome": "Render", "cor": "render", "ajuda": "Narração, render ou exportação do corte. Só ações já existentes."},
    "saida": {"nome": "Saída", "cor": "saida", "ajuda": "Fim de um caminho do fluxo."},
}
ARTEFATOS = {
    "briefing": {"nome": "Briefing", "tipo": "texto", "material": None, "arquivo": None},
    "notas": {"nome": "Notas de pesquisa", "tipo": "texto", "material": "pesquisa", "arquivo": "notas.md"},
    "angulo": {"nome": "Ângulo", "tipo": "texto", "material": "pesquisa", "arquivo": "angulo.md"},
    "roteiro": {"nome": "Roteiro", "tipo": "texto", "material": "roteiro", "arquivo": "roteiro.txt"},
    "direcao_viral": {"nome": "Direção e narração", "tipo": "texto", "material": "roteiro", "arquivo": "direcao_viral.md"},
    "revisao": {"nome": "Revisão de fatos", "tipo": "texto", "material": None, "arquivo": "revisao.md"},
    "componentes": {"nome": "Componentes", "tipo": "imagens", "material": "componentes", "arquivo": "componentes.md"},
    "cenas": {"nome": "Cenas", "tipo": "cenas", "material": "cenas", "arquivo": "cenas.json"},
    "metadados": {"nome": "Metadados", "tipo": "metadados", "material": "metadados", "arquivo": "metadados.json"},
    "auditoria_texto": {"nome": "Parecer de texto", "tipo": "parecer", "material": "auditoria_texto", "arquivo": "auditoria_texto.md"},
    "narracao": {"nome": "Narração", "tipo": "audio", "material": "narracao", "arquivo": "falas/falas.json"},
    "video": {"nome": "Vídeo", "tipo": "video", "material": "video", "arquivo": "video.mp4"},
    "auditoria_final": {"nome": "Parecer final", "tipo": "parecer", "material": "auditoria_final", "arquivo": "auditoria.md"},
    "thumbnail": {"nome": "Thumbnail", "tipo": "texto", "material": "thumbnail", "arquivo": None},
}
# Tarefas que o estúdio sabe pedir (prompts.py) e o que cada uma consome e entrega. "livre" usa o contrato do agente e as instruções do nó.
TAREFAS = {
    "pesquisa": {"nome": "Pesquisar o tema", "entradas": ["briefing"], "saidas": ["notas"]},
    "roteiro": {"nome": "Escrever o roteiro", "entradas": ["notas"], "saidas": ["angulo", "roteiro", "direcao_viral"]},
    "courtois": {"nome": "Conferir os fatos", "entradas": ["notas", "roteiro"], "saidas": ["revisao"]},
    "componentes": {"nome": "Desenhar os componentes", "entradas": ["roteiro"], "saidas": ["componentes"]},
    "cenas": {"nome": "Montar e desenhar as cenas", "entradas": ["roteiro", "direcao_viral?", "componentes?"], "saidas": ["cenas"]},
    "metadados": {"nome": "Título, descrição e tags", "entradas": ["roteiro"], "saidas": ["metadados"]},
    "auditoria_texto": {"nome": "Auditar o texto", "entradas": ["roteiro", "notas", "cenas", "metadados"], "saidas": ["auditoria_texto"]},
    "auditoria_final": {"nome": "Auditar o render", "entradas": ["video"], "saidas": ["auditoria_final"]},
    "thumbnail": {"nome": "Prompt da thumbnail", "entradas": ["video"], "saidas": ["thumbnail"]},
    "livre": {"nome": "Instruções deste nó", "entradas": [], "saidas": []},
}
ACOES = {
    "narracao": {"nome": "Gerar narração (Chatterbox)", "entradas": ["roteiro", "cenas?"], "saidas": ["narracao"], "etapa": "narracao"},
    "video": {"nome": "Renderizar (run.py video)", "entradas": ["cenas", "narracao", "metadados"], "saidas": ["video"], "etapa": "video"},
    "corte": {"nome": "Exportar o corte editado", "entradas": ["video"], "saidas": ["video"], "etapa": "video"},
}
CONDICOES = {
    "parecer:auditoria_texto": {"nome": "Parecer da auditoria de texto", "valores": ["APROVADO", "BLOQUEADO"]},
    "parecer:auditoria_final": {"nome": "Parecer da auditoria final", "valores": ["APROVADO", "BLOQUEADO"]},
    "estilo": {"nome": "Estilo do vídeo", "valores": [*estilos.ESTILOS, "3d"]},
    "formato": {"nome": "Formato do vídeo", "valores": ["vertical", "horizontal"]},
}
MATERIAIS_APROVAVEIS = {"roteiro": "Roteiro", "componentes": "Componentes", "cenas": "Cenas", "metadados": "Metadados", "narracao": "Narração", "video": "Vídeo final", "pesquisa": "Pesquisa"}
STATUS = {"pendente": "Na espera", "aguardando_inicio": "Aguarda você iniciar", "rodando": "Em execução", "aguardando": "Aguarda sua aprovação", "concluido": "Concluído", "ignorado": "Fora do caminho", "falhou": "Falhou"}
TERMINAIS = ("concluido", "ignorado")
_lock = threading.RLock()


# ---------- O fluxo real do repositório ----------

def _no(ident, tipo, nome, col, lin, **config):
    return {"id": ident, "tipo": tipo, "nome": nome, "x": 60 + col * 250, "y": 60 + lin * 130, "desativado": False, "config": config}


def _ligar(*pares):
    saida = []
    for p in pares:
        de, para, *porta = p
        saida.append({"id": f"{de}->{para}", "de": de, "porta": porta[0] if porta else None, "para": para, "mapa": []})
    return saida


def grafo_real():
    """O fluxo enxuto do CLAUDE.md, com as etapas e os gatilhos que estão em fluxo.py (ETAPAS e GATILHOS). É a primeira coisa que o editor mostra."""
    nos = [
        _no("briefing", "entrada", "Briefing", 0, 1),
        _no("pesquisa", "agente", "Pesquisa", 1, 1, agente="modric-pesquisador-tema", tarefa="pesquisa"),
        _no("roteiro", "agente", "Roteiro", 2, 1, agente="neymar-roteirista", tarefa="roteiro"),
        _no("fatos", "agente", "Revisão de fatos", 3, 1, agente="courtois-revisor-fatos", tarefa="courtois"),
        _no("ap_roteiro", "aprovacao", "Aprovar roteiro", 4, 1, material="roteiro"),
        _no("componentes", "agente", "Componentes", 0, 3, agente="raphinha-curador-componentes", tarefa="componentes"),
        _no("ap_componentes", "aprovacao", "Aprovar componentes", 1, 3, material="componentes"),
        _no("se_vertical", "condicao", "Formato vertical?", 2, 4, campo="formato", valor="vertical"),
        _no("cenas_v", "agente", "Cenas (Short)", 3, 3, agente="olise-diretor-arte", tarefa="cenas"),
        _no("cenas_h", "agente", "Cenas (horizontal)", 3, 5, agente="barcola-diretor-horizontal", tarefa="cenas"),
        _no("ap_cenas", "aprovacao", "Aprovar cenas", 4, 4, material="cenas"),
        _no("metadados", "agente", "Metadados", 5, 2, agente="mbappe-editor-metadados", tarefa="metadados"),
        _no("j_texto", "juncao", "Texto pronto", 5, 4),
        _no("aud_texto", "agente", "Auditoria de texto", 6, 4, agente="vini-auditor-conformidade", tarefa="auditoria_texto"),
        _no("se_texto", "condicao", "Texto aprovado?", 0, 7, campo="parecer:auditoria_texto", valor="APROVADO"),
        _no("narracao", "render", "Narração", 1, 6, acao="narracao", inicio="manual"),
        _no("ap_narracao", "aprovacao", "Aprovar narração", 2, 6, material="narracao"),
        _no("video", "render", "Render", 3, 6, acao="video", inicio="manual"),
        _no("aud_final", "agente", "Auditoria final", 4, 6, agente="vini-auditor-conformidade", tarefa="auditoria_final"),
        _no("se_final", "condicao", "Render aprovado?", 5, 6, campo="parecer:auditoria_final", valor="APROVADO"),
        _no("ap_video", "aprovacao", "Aprovar vídeo final", 6, 6, material="video"),
        _no("thumb", "agente", "Thumbnail", 5, 8, agente="sidorf-thumbnail-estrategista", tarefa="thumbnail", inicio="manual"),
        _no("fim", "saida", "Pronto para publicar", 6, 8),
        _no("fim_bloqueio", "saida", "Bloqueado pelo Vini", 2, 8),
    ]
    arestas = _ligar(("briefing", "pesquisa"), ("pesquisa", "roteiro"), ("roteiro", "fatos"), ("fatos", "ap_roteiro"), ("ap_roteiro", "componentes"), ("ap_roteiro", "metadados"),
                     ("componentes", "ap_componentes"), ("ap_componentes", "se_vertical"),
                     ("se_vertical", "cenas_v", "sim"), ("se_vertical", "cenas_h", "nao"), ("cenas_v", "ap_cenas"), ("cenas_h", "ap_cenas"), ("ap_cenas", "j_texto"), ("metadados", "j_texto"),
                     ("j_texto", "aud_texto"), ("aud_texto", "se_texto"), ("se_texto", "narracao", "sim"), ("se_texto", "fim_bloqueio", "nao"), ("narracao", "ap_narracao"), ("ap_narracao", "video"),
                     ("video", "aud_final"), ("aud_final", "se_final"), ("se_final", "ap_video", "sim"), ("se_final", "fim_bloqueio", "nao"), ("ap_video", "thumb"), ("thumb", "fim"))
    return {"nos": nos, "arestas": arestas}


def _sem_se_sketch(g):
    """O fluxo antigo só fazia componentes no estilo sketch (nó se_sketch). Devolve o mesmo grafo com componentes para todos os estilos, ou None se não for esse desenho."""
    nos = {n["id"]: n for n in g.get("nos", [])}
    n = nos.get("se_sketch")
    if not n or (n.get("config") or {}).get("campo") != "estilo":
        return None
    ent = [a for a in g["arestas"] if a["para"] == "se_sketch"]
    sim = [a for a in g["arestas"] if a["de"] == "se_sketch" and a.get("porta") == "sim"]
    if not ent or not sim:
        return None
    novo = json.loads(json.dumps(g))
    novo["nos"] = [x for x in novo["nos"] if x["id"] != "se_sketch"]
    novo["arestas"] = [a for a in novo["arestas"] if "se_sketch" not in (a["de"], a["para"])]
    for e in ent:
        for s in sim:
            novo["arestas"].append({"id": f"{e['de']}->{s['para']}", "de": e["de"], "porta": e.get("porta"), "para": s["para"], "mapa": []})
    return novo


def _atualizar_padrao():
    """Decisão do dono (2026-11-03): componentes para os quatro estilos. Publica uma versão nova do fluxo padrão sem o se_sketch; as execuções
    em andamento continuam presas à versão delas (migrar_execucao é um passo à parte). Só mexe se o desenho ainda é o antigo."""
    u = um("SELECT numero, grafo FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", PADRAO)
    if not u:
        return
    novo = _sem_se_sketch(json.loads(u["grafo"]))
    if not novo:
        return
    faz("INSERT OR IGNORE INTO fluxo_versoes (fluxo, numero, grafo, nota, publicada_em) VALUES (?,?,?,?,?)", PADRAO, u["numero"] + 1, json.dumps(novo, ensure_ascii=False), "Componentes (Raphinha) para os quatro estilos: sem o nó Estilo sketch?", agora())
    f = um("SELECT rascunho FROM fluxos WHERE id=?", PADRAO)
    if f and _sem_posicao(json.loads(f["rascunho"])) == _sem_posicao(json.loads(u["grafo"])):
        faz("UPDATE fluxos SET rascunho=?, atualizado_em=? WHERE id=?", json.dumps(novo, ensure_ascii=False), agora(), PADRAO)


def garantir_padrao():
    """Na primeira abertura o fluxo real já aparece publicado como v1. Só cria uma vez: depois disso as mudanças são do Guilherme."""
    if um("SELECT id FROM fluxos WHERE id=?", PADRAO):
        _atualizar_padrao()
        return
    g = grafo_real()
    ag = {a["id"] for a in AG.catalogo()}
    if not ag:
        return  # .claude/agents ausente (caixa de teste do fluxo antigo): sem catálogo não há grafo para validar
    faz("INSERT OR IGNORE INTO fluxos (id, nome, rascunho, atualizado_em) VALUES (?,?,?,?)", PADRAO, "Canal: fluxo enxuto", json.dumps(g, ensure_ascii=False), agora())
    if not um("SELECT id FROM fluxo_versoes WHERE fluxo=?", PADRAO):
        faz("INSERT OR IGNORE INTO fluxo_versoes (fluxo, numero, grafo, nota, publicada_em) VALUES (?,1,?,?,?)", PADRAO, json.dumps(g, ensure_ascii=False), "Equivalente ao fluxo fixo descoberto no repositório", agora())


# ---------- Contratos e dados ----------

def _base(x):
    return x.rstrip("?")


def contrato(no, agentes=None):
    """(entradas, saidas) do nó. O contrato declarado no agente vale; quem não declarou usa o da tarefa."""
    tipo = no["tipo"]
    c = no.get("config") or {}
    if tipo == "entrada":
        return [], ["briefing"]
    if tipo == "render":
        a = ACOES.get(c.get("acao"))
        return (a["entradas"], a["saidas"]) if a else ([], [])
    if tipo != "agente":
        return [], []
    t = TAREFAS.get(c.get("tarefa") or "livre", TAREFAS["livre"])
    ag = (agentes or {}).get(c.get("agente"))
    if ag and (c.get("tarefa") or "livre") == "livre":
        return ag["contrato"]["entradas"], [_base(s) for s in ag["contrato"]["saidas"] if not s.endswith("?")]
    if ag and ag["contrato"].get("declarado") and not any(s.endswith("?") for s in ag["contrato"]["saidas"]):
        return ag["contrato"]["entradas"], ag["contrato"]["saidas"]
    return t["entradas"], t["saidas"]


def _indices(g):
    nos = {n["id"]: n for n in g.get("nos", [])}
    entrada, saida = {i: [] for i in nos}, {i: [] for i in nos}
    for a in g.get("arestas", []):
        if a.get("de") in nos and a.get("para") in nos:
            saida[a["de"]].append(a)
            entrada[a["para"]].append(a)
    return nos, entrada, saida


def _ordem(g):
    """Ordem topológica. Devolve (ordem, nós presos num ciclo)."""
    nos, entrada, saida = _indices(g)
    graus = {i: len(entrada[i]) for i in nos}
    fila = deque(sorted(i for i in nos if graus[i] == 0))
    ordem = []
    while fila:
        i = fila.popleft()
        ordem.append(i)
        for a in saida[i]:
            graus[a["para"]] -= 1
            if graus[a["para"]] == 0:
                fila.append(a["para"])
    return ordem, [i for i in nos if i not in ordem]


def _disponiveis(g, agentes):
    """Artefato -> quem entrega, para cada nó. Tudo que veio de antes continua disponível (os dados ficam em arquivo). Nó desativado não entrega nada."""
    nos, entrada, _ = _indices(g)
    ordem, _ciclo = _ordem(g)
    disp = {}
    for i in ordem:
        d = {}
        for a in entrada[i]:
            p = nos[a["de"]]
            d.update(disp.get(a["de"], {}))
            if not p.get("desativado"):
                for s in contrato(p, agentes)[1]:
                    d[_base(s)] = a["de"]
            for m in a.get("mapa") or []:  # mapeamento: a saída de um nó entra com outro nome no seguinte
                if m.get("saida") in d and m.get("entrada"):
                    d[m["entrada"]] = d[m["saida"]]
        disp[i] = d
    return disp


def validar(g, agentes=None):
    """Tudo que impede publicar (nivel=erro) ou merece atenção (nivel=aviso). Cada item aponta o nó ou a conexão."""
    agentes = {a["id"]: a for a in AG.catalogo()} if agentes is None else agentes
    p = []

    def erro(no, texto, aresta=None):
        p.append({"no": no, "aresta": aresta, "nivel": "erro", "texto": texto})

    def aviso(no, texto):
        p.append({"no": no, "aresta": None, "nivel": "aviso", "texto": texto})

    nos, entrada, saida = _indices(g)
    idsvistos = set()
    for n in g.get("nos", []):
        if n.get("id") in idsvistos:
            erro(n.get("id"), "Identificador de nó repetido.")
        idsvistos.add(n.get("id"))
        if n.get("tipo") not in TIPOS:
            erro(n.get("id"), f"Tipo de nó desconhecido: {n.get('tipo')}.")
    for a in g.get("arestas", []):
        if a.get("de") not in nos or a.get("para") not in nos:
            erro(a.get("de") if a.get("de") in nos else a.get("para"), "Conexão aponta para um nó que não existe.", a.get("id"))
    if not any(n["tipo"] == "entrada" and not n.get("desativado") for n in nos.values()):
        p.append({"no": None, "aresta": None, "nivel": "erro", "texto": "O fluxo precisa de um nó de briefing ativo."})
    if not any(n["tipo"] == "saida" for n in nos.values()):
        p.append({"no": None, "aresta": None, "nivel": "erro", "texto": "O fluxo precisa de um nó de saída."})
    _ordem_, ciclo = _ordem(g)
    for i in ciclo:
        erro(i, "Este nó está em um ciclo. O executor roda em uma direção só: para refazer, use o pedido de ajuste na aprovação.")
    # Quem chega de um briefing
    alcance, fila = set(), deque(i for i, n in nos.items() if n["tipo"] == "entrada")
    while fila:
        i = fila.popleft()
        if i in alcance:
            continue
        alcance.add(i)
        fila.extend(a["para"] for a in saida[i])
    for i, n in nos.items():
        if i not in alcance and i not in ciclo:
            erro(i, "Nó inacessível: nenhum caminho sai do briefing até aqui.")
        if n["tipo"] == "entrada" and entrada[i]:
            erro(i, "O briefing é o começo do fluxo: não recebe conexões.")
        if n["tipo"] == "saida" and saida[i]:
            erro(i, "A saída é o fim de um caminho: não tem conexões de saída.")
        if n["tipo"] not in ("entrada", "saida") and not saida[i]:
            aviso(i, "Nada depois deste nó: o caminho termina aqui sem uma saída.")
    disp = _disponiveis(g, agentes) if not ciclo else {}
    for i, n in nos.items():
        c = n.get("config") or {}
        t = n["tipo"]
        if t == "agente":
            ag = agentes.get(c.get("agente"))
            if not c.get("agente"):
                erro(i, "Escolha o agente que executa esta etapa.")
            elif not ag:
                erro(i, f"O agente {c.get('agente')} não existe em .claude/agents.")
            elif not ag["ativo"]:
                erro(i, f"O agente {c.get('agente')} está desativado.")
            if c.get("agente_versao") and not um("SELECT 1 x FROM agente_versoes WHERE agente=? AND numero=?", c.get("agente"), c["agente_versao"]):
                erro(i, f"O agente {c.get('agente')} não tem a versão {c['agente_versao']}.")
            if (c.get("tarefa") or "livre") not in TAREFAS:
                erro(i, f"Tarefa desconhecida: {c.get('tarefa')}.")
            if (c.get("tarefa") or "livre") == "livre" and not str(c.get("instrucoes") or "").strip():
                erro(i, "Na tarefa livre, escreva as instruções deste nó.")
        elif t == "aprovacao":
            if c.get("material") not in MATERIAIS_APROVAVEIS:
                erro(i, "Escolha o material que esta aprovação decide.")
            elif disp and not any(ARTEFATOS[x]["material"] == c["material"] for x in disp.get(i, {}) if x in ARTEFATOS):
                erro(i, f"Nenhum nó antes deste produz {MATERIAIS_APROVAVEIS[c['material']].lower()}.")
        elif t == "condicao":
            campo = CONDICOES.get(c.get("campo"))
            if not campo:
                erro(i, "Escolha o que esta condição confere.")
            elif c.get("valor") not in campo["valores"]:
                erro(i, f"Valor inválido para a condição: {c.get('valor')}.")
            portas = {a.get("porta") for a in saida[i]}
            for ausente in {"sim", "nao"} - portas:
                aviso(i, f"O caminho “{'sim' if ausente == 'sim' else 'não'}” não vai a lugar nenhum: nesse caso o fluxo para aqui.")
            for a in saida[i]:
                if a.get("porta") not in ("sim", "nao"):
                    erro(i, "Toda conexão de saída da condição precisa sair de “sim” ou “não”.", a.get("id"))
        elif t == "render" and c.get("acao") not in ACOES:
            erro(i, "Escolha uma ação de render existente.")
        elif t == "juncao" and len(entrada[i]) < 2:
            aviso(i, "Uma junção só faz sentido com dois caminhos ou mais.")
        if t in ("agente", "render") and i in disp:
            for ent in contrato(n, agentes)[0]:
                if not ent.endswith("?") and _base(ent) not in disp[i]:
                    erro(i, f"Entrada obrigatória sem origem: {ARTEFATOS.get(_base(ent), {}).get('nome', ent)}. Conecte um nó que a produza ou mapeie um campo compatível.")
        for a in entrada[i]:
            for m in a.get("mapa") or []:
                orig, dest = ARTEFATOS.get(m.get("saida")), ARTEFATOS.get(m.get("entrada"))
                if not orig:
                    erro(i, f"Mapeamento usa uma saída desconhecida: {m.get('saida')}.", a.get("id"))
                elif a.get("de") in disp and m.get("saida") not in disp.get(a["de"], {}) and m.get("saida") not in [_base(s) for s in contrato(nos[a["de"]], agentes)[1]]:
                    erro(i, f"Mapeamento: {orig['nome']} não chega por esta conexão.", a.get("id"))
                if dest and orig and dest["tipo"] != orig["tipo"]:
                    erro(i, f"Tipos incompatíveis no mapeamento: {orig['nome']} ({orig['tipo']}) não pode virar {dest['nome']} ({dest['tipo']}).", a.get("id"))
                if not m.get("entrada"):
                    erro(i, "Mapeamento sem o campo de entrada.", a.get("id"))
    return p


def impacto_desativar(g, no):
    """Antes de desativar: quem depende deste nó e como cada dependência será atendida."""
    agentes = {a["id"]: a for a in AG.catalogo()}
    g2 = json.loads(json.dumps(g))
    for n in g2["nos"]:
        if n["id"] == no:
            n["desativado"] = True
    nos, _, _ = _indices(g)
    if no not in nos:
        raise Recusado("Nó não encontrado.", 404)
    entrega = [_base(s) for s in contrato(nos[no], agentes)[1]]
    com, sem = _disponiveis(g, agentes), _disponiveis(g2, agentes)
    saida = []
    for i, n in nos.items():
        if i == no:
            continue
        for ent in contrato(n, agentes)[0]:
            b = _base(ent)
            if com.get(i, {}).get(b) == no:
                outro = sem.get(i, {}).get(b)
                saida.append({"no": i, "nome": n["nome"], "entrada": b, "entrada_nome": ARTEFATOS.get(b, {}).get("nome", b), "opcional": ent.endswith("?"), "atendida_por": nos[outro]["nome"] if outro else None})
    return {"entrega": entrega, "dependentes": saida}


# ---------- Rascunho e publicação ----------

def _limpar_grafo(g):
    """O canvas só guarda dados conhecidos. Instruções viram texto de prompt; nada aqui vira comando."""
    if not isinstance(g, dict) or not isinstance(g.get("nos"), list) or not isinstance(g.get("arestas"), list):
        raise Recusado("Grafo inválido.", 400)
    nos = []
    for n in g["nos"]:
        if not re.fullmatch(r"[\w.-]{1,60}", str(n.get("id") or "")):
            raise Recusado("Identificador de nó inválido.", 400)
        if n.get("tipo") not in TIPOS:
            raise Recusado(f"Tipo de nó desconhecido: {n.get('tipo')}.", 400)
        c = n.get("config") or {}
        config = {k: c[k] for k in ("agente", "agente_versao", "tarefa", "instrucoes", "inicio", "material", "campo", "valor", "acao") if c.get(k) not in (None, "")}
        for k in ("agente", "tarefa", "inicio", "material", "campo", "valor", "acao"):
            if k in config and not isinstance(config[k], str):
                raise Recusado(f"Configuração inválida: {k}.", 400)
        if "agente_versao" in config:
            config["agente_versao"] = int(config["agente_versao"])
        if "inicio" in config and config["inicio"] not in ("auto", "manual"):
            raise Recusado("Início inválido.", 400)
        nos.append({"id": n["id"], "tipo": n["tipo"], "nome": str(n.get("nome") or TIPOS[n["tipo"]]["nome"])[:80], "x": round(float(n.get("x", 0))), "y": round(float(n.get("y", 0))), "desativado": bool(n.get("desativado")), "config": config})
    arestas = []
    for a in g["arestas"]:
        mapa = [{"saida": str(m.get("saida") or ""), "entrada": str(m.get("entrada") or "")} for m in a.get("mapa") or []]
        arestas.append({"id": str(a.get("id") or f"{a.get('de')}->{a.get('para')}")[:130], "de": a.get("de"), "porta": a.get("porta"), "para": a.get("para"), "mapa": mapa})
    return {"nos": nos, "arestas": arestas}


def listar():
    garantir_padrao()
    saida = []
    for f in varios("SELECT * FROM fluxos ORDER BY atualizado_em DESC"):
        v = um("SELECT numero, publicada_em FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", f["id"])
        pub = um("SELECT grafo FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", f["id"])
        ativas = um("SELECT COUNT(*) n FROM execucoes WHERE fluxo=? AND status='ativa'", f["id"])["n"]
        saida.append({"id": f["id"], "nome": f["nome"], "atualizado_em": f["atualizado_em"], "publicada": v["numero"] if v else None, "publicada_em": v["publicada_em"] if v else None, "rascunho_alterado": bool(pub) and _sem_posicao(json.loads(pub["grafo"])) != _sem_posicao(json.loads(f["rascunho"])), "execucoes_ativas": ativas, "nos": len(json.loads(f["rascunho"])["nos"])})
    return saida


def _sem_posicao(g):
    """Mover um nó é só visual: não conta como mudança de execução."""
    return {"nos": sorted(({k: v for k, v in n.items() if k not in ("x", "y")} for n in g["nos"]), key=lambda n: n["id"]), "arestas": sorted(g["arestas"], key=lambda a: str(a["id"]))}


def detalhe(fluxo_id):
    garantir_padrao()
    f = um("SELECT * FROM fluxos WHERE id=?", fluxo_id)
    if not f:
        raise Recusado("Fluxo não encontrado.", 404)
    g = json.loads(f["rascunho"])
    versoes = varios("SELECT numero, nota, publicada_em FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC", fluxo_id)
    catalogo = AG.catalogo()
    return {"id": fluxo_id, "nome": f["nome"], "grafo": g, "atualizado_em": f["atualizado_em"], "versoes": versoes, "problemas": validar(g, {a["id"]: a for a in catalogo}), "agentes": [{"id": a["id"], "craque": a["craque"], "descricao": a["descricao"], "ativo": a["ativo"], "versao": a["versao"], "contrato": a["contrato"]} for a in catalogo],
            "catalogo": {"tipos": TIPOS, "artefatos": ARTEFATOS, "tarefas": TAREFAS, "acoes": ACOES, "condicoes": CONDICOES, "materiais": MATERIAIS_APROVAVEIS}, "execucoes": varios("SELECT id, slug, fluxo_numero, status, criada_em FROM execucoes WHERE fluxo=? ORDER BY id DESC LIMIT 10", fluxo_id)}


def salvar_rascunho(fluxo_id, g, nome=None):
    g = _limpar_grafo(g)
    if not um("SELECT id FROM fluxos WHERE id=?", fluxo_id):
        raise Recusado("Fluxo não encontrado.", 404)
    faz("UPDATE fluxos SET rascunho=?, atualizado_em=?, nome=COALESCE(?, nome) WHERE id=?", json.dumps(g, ensure_ascii=False), agora(), nome, fluxo_id)
    return {"problemas": validar(g), "atualizado_em": agora()}


def criar_fluxo(nome, copiar_de=None):
    nome = str(nome or "").strip()
    if len(nome) < 3:
        raise Recusado("Dê um nome ao fluxo.", 400)
    garantir_padrao()
    ident = fluxo.slugify(nome)
    base, n = ident, 2
    while um("SELECT id FROM fluxos WHERE id=?", ident):
        ident, n = f"{base}-{n}", n + 1
    if copiar_de:
        o = um("SELECT rascunho FROM fluxos WHERE id=?", copiar_de)
        if not o:
            raise Recusado("Fluxo de origem não encontrado.", 404)
        rascunho = o["rascunho"]
    else:
        rascunho = json.dumps({"nos": [_no("briefing", "entrada", "Briefing", 0, 1), _no("fim", "saida", "Saída", 3, 1)], "arestas": []}, ensure_ascii=False)
    faz("INSERT INTO fluxos (id, nome, rascunho, atualizado_em) VALUES (?,?,?,?)", ident, nome, rascunho, agora())
    return {"id": ident}


def publicar(fluxo_id, nota=None):
    f = um("SELECT * FROM fluxos WHERE id=?", fluxo_id)
    if not f:
        raise Recusado("Fluxo não encontrado.", 404)
    g = json.loads(f["rascunho"])
    problemas = validar(g)
    erros = [p for p in problemas if p["nivel"] == "erro"]
    if erros:
        e = Recusado([f"{p['texto']}" for p in erros])
        e.problemas = problemas
        raise e
    u = um("SELECT numero, grafo FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", fluxo_id)
    if u and _sem_posicao(json.loads(u["grafo"])) == _sem_posicao(g):
        faz("UPDATE fluxo_versoes SET grafo=? WHERE fluxo=? AND numero=?", json.dumps(g, ensure_ascii=False), fluxo_id, u["numero"])  # só posição: mesma versão
        return {"numero": u["numero"], "novo": False}
    numero = (u["numero"] if u else 0) + 1
    faz("INSERT INTO fluxo_versoes (fluxo, numero, grafo, nota, publicada_em) VALUES (?,?,?,?,?)", fluxo_id, numero, json.dumps(g, ensure_ascii=False), (nota or "")[:200], agora())
    return {"numero": numero, "novo": True}


def restaurar_rascunho(fluxo_id, numero):
    v = um("SELECT grafo FROM fluxo_versoes WHERE fluxo=? AND numero=?", fluxo_id, numero)
    if not v:
        raise Recusado("Versão não encontrada.", 404)
    faz("UPDATE fluxos SET rascunho=?, atualizado_em=? WHERE id=?", v["grafo"], agora(), fluxo_id)
    return detalhe(fluxo_id)


def usos_do_agente(ident):
    garantir_padrao()
    saida = []
    for f in varios("SELECT * FROM fluxos"):
        for origem, g in [("rascunho", json.loads(f["rascunho"]))] + [(f"v{v['numero']}", json.loads(v["grafo"])) for v in varios("SELECT numero, grafo FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", f["id"])]:
            for n in g["nos"]:
                if n["tipo"] == "agente" and (n.get("config") or {}).get("agente") == ident:
                    saida.append({"fluxo": f["id"], "fluxo_nome": f["nome"], "origem": origem, "no": n["id"], "no_nome": n["nome"]})
    return saida


def ensaiar(g, slug):
    """Teste com um projeto de exemplo: percorre o grafo olhando o que existe no projeto, sem acionar agente nenhum. Mostra a ordem real, em quais passos há paralelismo e o que seria reaproveitado."""
    fluxo.garantir_producao(slug)
    fluxo.sincronizar(slug, forcar=True)
    ctx = fluxo.Contexto(slug)
    agentes = {a["id"]: a for a in AG.catalogo()}
    problemas = validar(g, agentes)
    if any(p["nivel"] == "erro" and p["no"] and p["texto"].startswith("Este nó está em um ciclo") for p in problemas):
        return {"problemas": problemas, "passos": []}
    nos, entrada, _saida = _indices(g)
    ordem, _ = _ordem(g)
    nivel, porta, estado = {}, {}, {}
    for i in ordem:
        n = nos[i]
        chegam = [a for a in entrada[i] if estado.get(a["de"]) != "ignorado" and (porta.get(a["de"]) is None or porta[a["de"]] == a.get("porta"))]
        if entrada[i] and not chegam:
            estado[i] = "ignorado"
            nivel[i] = max((nivel.get(a["de"], 0) for a in entrada[i]), default=0)
            continue
        nivel[i] = max((nivel.get(a["de"], 0) + 1 for a in chegam), default=0)
        estado[i] = "ativo"
        if n["tipo"] == "condicao" and not n.get("desativado"):
            valor = _valor_condicao(ctx, (n.get("config") or {}).get("campo"))
            porta[i] = "sim" if valor == (n.get("config") or {}).get("valor") else "nao"
    passos = {}
    for i in ordem:
        n = nos[i]
        ents, sais = contrato(n, agentes)
        existe = [s for s in sais if _existe(ctx, _base(s))]
        faltam = [e for e in ents if not e.endswith("?") and _base(e) != "briefing" and not _existe(ctx, _base(e))]
        passos.setdefault(nivel[i], []).append({"no": i, "nome": n["nome"], "tipo": n["tipo"], "estado": "fora do caminho" if estado[i] == "ignorado" else "desativado" if n.get("desativado") else "ativo", "porta": porta.get(i),
                                                "ja_existe": existe, "faltam": faltam, "faria": ("reaproveitar" if sais and len(existe) == len(sais) else "rodar") if n["tipo"] in ("agente", "render") else None})
    return {"problemas": problemas, "passos": [passos[k] for k in sorted(passos)], "slug": slug}


# ---------- Execução ----------

def _existe(ctx, artefato):
    a = ARTEFATOS.get(artefato)
    if not a:
        return False
    if artefato == "briefing":
        return True
    if a["material"] and ctx.versoes.get(a["material"]) and (not a["arquivo"] or a["tipo"] == "imagens"):
        return True
    return bool(a["arquivo"]) and (ctx.pasta / a["arquivo"]).exists()


def _valor_condicao(ctx, campo):
    if campo == "estilo":
        return ctx.estilo
    if campo == "formato":
        return ctx.formato
    if campo and campo.startswith("parecer:"):
        v = ctx.versoes.get(campo.split(":", 1)[1])
        return M.status_auditoria(M.ler_blob_texto(next(iter(v["manifesto"]["arquivos"].values())))) if v else None
    return None


def execucao_de(slug):
    """A execução que manda neste projeto: a ativa, ou a última."""
    e = um("SELECT * FROM execucoes WHERE slug=? ORDER BY status='ativa' DESC, id DESC LIMIT 1", slug)
    if e:
        e["grafo"] = json.loads(e["grafo"])
        e["agentes"] = json.loads(e["agentes"])
    return e


def iniciar_execucao(slug, fluxo_id, forcar=False):
    """Prende a execução à versão publicada e à foto dos agentes de agora. Se já há uma ativa, recusa em vez de disparar outra."""
    garantir_padrao()
    fluxo.garantir_producao(slug)
    v = um("SELECT * FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", fluxo_id)
    if not v:
        raise Recusado("Este fluxo ainda não tem versão publicada. Publique antes de executar.")
    with _lock:
        ativa = um("SELECT id FROM execucoes WHERE slug=? AND status='ativa'", slug)
        if ativa:
            raise Recusado(f"Este projeto já tem uma execução em andamento (#{ativa['id']}).")
        g = json.loads(v["grafo"])
        fotos = {}
        for n in g["nos"]:
            c = n.get("config") or {}
            if n["tipo"] == "agente" and c.get("agente"):
                f = AG.foto(c["agente"])
                if c.get("agente_versao") and c["agente_versao"] != f["versao"]:
                    t = AG.texto_da_versao(c["agente"], c["agente_versao"])
                    campos, corpo = AG.analisar(t["texto"])
                    f.update(versao=t["numero"], sha=t["sha"], corpo=corpo, modelo=campos.get("model") or "", ferramentas=AG.lista_csv(campos.get("tools", "")))
                fotos[n["id"]] = f
        cur = faz("INSERT INTO execucoes (slug, fluxo, fluxo_versao, fluxo_numero, grafo, agentes, status, criada_em) VALUES (?,?,?,?,?,?, 'ativa', ?)", slug, fluxo_id, v["id"], v["numero"], v["grafo"], json.dumps(fotos, ensure_ascii=False), agora())
        ex = cur.lastrowid
        for n in g["nos"]:
            faz("INSERT INTO exec_nos (exec_id, no, status, forcar, atualizado_em) VALUES (?,?, 'pendente', ?, ?)", ex, n["id"], int(bool(forcar)), agora())
    evento(slug, f"Execução #{ex} iniciada: fluxo {fluxo_id} v{v['numero']}")
    avancar(ex)
    return ex


def _nos_da_execucao(ex):
    return {r["no"]: r for r in varios("SELECT * FROM exec_nos WHERE exec_id=?", ex)}


def _marcar(ex, no, de, para, **campos):
    """Transição condicional: só uma chamada ganha. É o que transforma clique duplo em uma ação só."""
    extras = "".join(f", {k}=?" for k in campos)
    cur = faz(f"UPDATE exec_nos SET status=?, atualizado_em=?{extras} WHERE exec_id=? AND no=? AND status=?", para, agora(), *campos.values(), ex, no, de)
    return cur.rowcount == 1


def _hash_entrada(ctx, ents, foto_):
    partes = {}
    for x in ents:
        b = _base(x)
        a = ARTEFATOS.get(b) or {}
        v = ctx.versoes.get(a.get("material")) if a.get("material") else None
        partes[b] = v["hash"] if v else (M.sha_arquivo(ctx.pasta / a["arquivo"]) if a.get("arquivo") and (ctx.pasta / a["arquivo"]).is_file() else None)
    return M.sha_texto(json.dumps([partes, (foto_ or {}).get("sha")], sort_keys=True))


def _esta_aprovado(ctx, material, v):
    e = next((x for x in fluxo.ETAPAS if x["material"] == material), None)
    if material == "componentes" and ctx.fase == "pronto":
        return True  # mesma regra do fluxo fixo: fora da fase "aprendendo", o Guilherme não precisa validar
    if e and e["gate"] == "itens" and v["manifesto"]["itens"]:
        return not ctx.pendentes(material)
    return v["id"] in ctx.aprovadas


def _spec_no(ctx, ex, no, foto_, hash_):
    from .fluxo import _prod
    c = no.get("config") or {}
    marca = {"id": ex["id"], "no": no["id"], "hash": hash_}
    if no["tipo"] == "render":
        acao = c.get("acao")
        if acao == "corte":
            return {"tipo": "comando", "comando": ["-m", "estudio.corte_export", "--slug", ctx.slug], "raia": "pesado", "real": True, "craque": "Render", "titulo": f"{no['nome']}: exportando o corte", "materiais": ["video"], "origem": "grafo", "exec": marca}
        s = fluxo.spec_etapa(ctx, acao, fluxo._escopo_narracao(ctx) if acao == "narracao" else None)
        return {**s, "titulo": f"{no['nome']}: {s['titulo']}", "origem": "grafo", "exec": marca}
    tarefa = c.get("tarefa") or "livre"
    ents = contrato(no, {foto_["id"]: foto_} if foto_ else {})[0]
    cab = prompts.cabecalho(_prod(ctx), tarefa)
    fa = " --formato horizontal" if ctx.formato == "horizontal" else ""
    gravar = None
    if tarefa in prompts.ETAPA:
        corpo = prompts.ETAPA[tarefa].format(slug=ctx.slug, formato_arg=fa, topico=fluxo._topico(ctx))
    elif tarefa in prompts.AUDITORIA:
        corpo = prompts.AUDITORIA[tarefa].format(slug=ctx.slug, formato_arg=fa, topico=fluxo._topico(ctx)) + prompts.FIM_AUDITORIA
        gravar = {"auditoria_texto": "auditoria_texto.md", "auditoria_final": "auditoria.md"}[tarefa]
    else:
        corpo = "Faça a tarefa abaixo nesta produção."
    linhas = [f"- {ARTEFATOS[_base(x)]['nome']}: output/{ctx.slug}/{ARTEFATOS[_base(x)]['arquivo']}" for x in ents if _base(x) in ARTEFATOS and ARTEFATOS[_base(x)]["arquivo"]]
    # Campos mapeados no grafo: o nó recebe o arquivo da saída com o nome que a entrada dele espera.
    grafo = ex["grafo"]
    for a in grafo["arestas"]:
        if a.get("para") == no["id"]:
            for m in a.get("mapa") or []:
                o = ARTEFATOS.get(m.get("saida"))
                if o and o.get("arquivo"):
                    linhas.append(f"- {m.get('entrada')}: output/{ctx.slug}/{o['arquivo']} (vem de {o['nome']})")
    extra = ("\nEntradas deste passo:\n" + "\n".join(dict.fromkeys(linhas)) if linhas else "") + (f"\n\nInstruções deste nó:\n{c['instrucoes']}" if c.get("instrucoes") else "")
    sais = contrato(no, {foto_["id"]: foto_} if foto_ else {})[1]
    materiais = sorted({ARTEFATOS[_base(s)]["material"] for s in sais if _base(s) in ARTEFATOS and ARTEFATOS[_base(s)]["material"]})
    spec = {"tipo": "agente", "agente": c.get("agente"), "prompt": cab + "\n" + corpo + extra, "raia": "agente", "craque": foto_["craque"] if foto_ else None, "titulo": f"{foto_['craque'] if foto_ else ''}: {no['nome']}", "materiais": materiais, "origem": "grafo", "exec": marca,
            "sistema": {"corpo": foto_["corpo"], "modelo": foto_["modelo"], "ferramentas": foto_["ferramentas"], "versao": foto_["versao"], "sha": foto_["sha"]} if foto_ else None}
    if gravar:
        spec.update(gravar_em=gravar, veredito=True)
    return spec


def _integracao(no):
    from . import trabalhos
    d = trabalhos.integracoes()
    c = no.get("config") or {}
    if no["tipo"] == "agente":
        return [] if d["claude"]["ok"] else [d["claude"]["detalhe"]]
    if c.get("acao") == "narracao":
        return [] if d["voz"]["ok"] else [d["voz"]["detalhe"]]
    if c.get("acao") in ("video", "corte"):
        return [] if d["ffmpeg"]["ok"] else [d["ffmpeg"]["detalhe"]]
    return []


def _iniciar_no(ctx, ex, no, r):
    """Decide entre reaproveitar e rodar. Roda só o que depende do que mudou."""
    c = no.get("config") or {}
    foto_ = ex["agentes"].get(no["id"])
    ents, sais = contrato(no, {foto_["id"]: foto_} if foto_ else {})
    h = _hash_entrada(ctx, ents, foto_)
    i = no["id"]
    if not r["forcar"]:
        tem_tudo = bool(sais) and all(_existe(ctx, _base(s)) for s in sais if not s.endswith("?"))
        if c.get("acao") in ("narracao", "video") and tem_tudo and not ctx.obsoleto(ACOES[c["acao"]]["saidas"][0]):
            return _marcar(ex["id"], i, "pendente", "concluido", entrada_hash=h, nota="Já está em dia com as entradas: nada a refazer.")
        if c.get("acao") == "corte" and tem_tudo:
            from . import corte
            s = corte.situacao(ctx.slug)
            if s is None or s["em_dia"]:
                return _marcar(ex["id"], i, "pendente", "concluido", entrada_hash=h, nota="O vídeo já contém o corte atual." if s else "Não há edição de corte neste projeto.")
        if no["tipo"] == "agente" and tem_tudo and (r["entrada_hash"] == h or not r["entrada_hash"]):
            return _marcar(ex["id"], i, "pendente", "concluido", entrada_hash=h, nota="Entradas iguais: nada a refazer." if r["entrada_hash"] else "Já existia no projeto: reaproveitado.")
    faltas = _integracao(no)
    if faltas:
        return _marcar(ex["id"], i, "pendente", "falhou", nota=" ".join(faltas))
    if c.get("inicio") == "manual" and not r["liberado"]:
        return _marcar(ex["id"], i, "pendente", "aguardando_inicio")
    spec = _spec_no(ctx, ex, no, foto_, h)
    if not _marcar(ex["id"], i, "pendente", "rodando", nota=None, job_id=None):  # sem o job de uma tentativa anterior
        return False
    job, _novo = fluxo.inserir_job(ctx.slug, f"g{ex['id']}:{i}", spec, assinatura=f"g{ex['id']}:{i}:{h}")
    faz("UPDATE exec_nos SET job_id=?, forcar=0 WHERE exec_id=? AND no=?", job["id"], ex["id"], i)
    evento(ctx.slug, f"Iniciado pelo fluxo: {spec['titulo']}" + (f" (agente v{foto_['versao']})" if foto_ else ""))
    return True


def _reiniciar_dependentes(ex, no, _nos=None):
    """Só o que vem depois deste nó volta a esperar. Os outros ramos, com suas aprovações, ficam como estão."""
    _, _ent, saida = _indices(ex["grafo"])
    vistos, fila = set(), deque(a["para"] for a in saida.get(no, []))
    while fila:
        i = fila.popleft()
        if i in vistos:
            continue
        vistos.add(i)
        fila.extend(a["para"] for a in saida.get(i, []))
    for i in vistos:
        faz("UPDATE exec_nos SET status='pendente', porta=NULL, atualizado_em=? WHERE exec_id=? AND no=? AND status NOT IN ('rodando','pendente')", agora(), ex["id"], i)
    return vistos


def _conferir_aprovacoes(ctx, ex, estados):
    """Aprovação vale para uma versão. Se o material mudou, ela volta a esperar decisão, e o que dependia dela também."""
    for n in ex["grafo"]["nos"]:
        if n["tipo"] != "aprovacao" or n.get("desativado"):
            continue
        r = estados.get(n["id"])
        material = (n.get("config") or {}).get("material")
        v = ctx.versoes.get(material)
        if not r or not v or r["status"] not in ("aguardando", "concluido") or not r["versao_id"]:
            continue
        if ctx.job_ativo(f"g{ex['id']}:{n['id']}") or any(j["status"] in fluxo.ATIVOS and material in json.loads(j["spec"]).get("materiais", []) for j in ctx.jobs):
            continue
        if r["versao_id"] == v["id"]:
            continue
        aprovada = _esta_aprovado(ctx, material, v) and not ctx.obsoleto(material)
        if r["status"] == "aguardando":
            if aprovada:
                _marcar(ex["id"], n["id"], "aguardando", "concluido", versao_id=v["id"], nota=f"v{v['numero']}: os itens já estavam aprovados.")
            else:
                faz("UPDATE exec_nos SET versao_id=?, atualizado_em=? WHERE exec_id=? AND no=?", v["id"], agora(), ex["id"], n["id"])
        elif aprovada:
            faz("UPDATE exec_nos SET versao_id=?, atualizado_em=? WHERE exec_id=? AND no=?", v["id"], agora(), ex["id"], n["id"])
        elif _marcar(ex["id"], n["id"], "concluido", "aguardando", versao_id=v["id"], nota=f"O material mudou: agora é a v{v['numero']}."):
            _reiniciar_dependentes(ex, n["id"])
            evento(ctx.slug, f"Aprovação reaberta: {n['nome']} (nova versão v{v['numero']})")


def _resolver_por_fora(ctx, ex, estados):
    """Nó que falhou, mas cujo trabalho foi refeito e concluído fora do grafo (mesmo agente, ou mesma etapa de render), com as saídas no projeto:
    o nó passa a concluído, citando o trabalho. Sem isso o grafo ficava parado num nó que já não está falho."""
    for n in ex["grafo"]["nos"]:
        r = estados.get(n["id"])
        if not r or r["status"] != "falhou" or n["tipo"] not in ("agente", "render") or n.get("desativado"):
            continue
        c = n.get("config") or {}
        foto_ = ex["agentes"].get(n["id"])
        ents, sais = contrato(n, {foto_["id"]: foto_} if foto_ else {})
        if not sais or not all(_existe(ctx, _base(s)) for s in sais if not s.endswith("?")):
            continue
        for j in ctx.jobs:  # do mais novo para o mais antigo
            if j["status"] != "ok" or j["id"] <= (r["job_id"] or 0) or (j["terminado_em"] or "") < (r["atualizado_em"] or ""):
                continue
            spec = json.loads(j["spec"])
            if spec.get("exec"):
                continue
            if n["tipo"] == "agente":
                igual = bool(c.get("agente")) and spec.get("agente") == c.get("agente")
            else:
                igual = j["etapa"] == (ACOES.get(c.get("acao")) or {}).get("etapa")
            if not igual:
                continue
            saidas = {s: ctx.versoes[ARTEFATOS[_base(s)]["material"]]["numero"] for s in sais if ARTEFATOS.get(_base(s), {}).get("material") in ctx.versoes}
            if _marcar(ex["id"], n["id"], "falhou", "concluido", entrada_hash=_hash_entrada(ctx, ents, foto_), saidas=json.dumps(saidas), job_id=j["id"],
                       nota=f"Concluído pelo trabalho #{j['id']}, feito fora do fluxo (a tentativa do fluxo tinha falhado)."):
                evento(ctx.slug, f"Fluxo: {n['nome']} resolvido pelo trabalho #{j['id']}, concluído fora do grafo")
            break


def avancar(ex_id):
    """Passa pelo grafo e dá o próximo passo em tudo que já pode andar. Chamar duas vezes não faz nada a mais."""
    with _lock:
        ex = um("SELECT * FROM execucoes WHERE id=?", ex_id)
        if not ex or ex["status"] != "ativa":
            return []
        ex["grafo"], ex["agentes"] = json.loads(ex["grafo"]), json.loads(ex["agentes"])
        slug = ex["slug"]
        fluxo.sincronizar(slug, forcar=True, assentar=False)
        ctx = fluxo.Contexto(slug)
        _resolver_por_fora(ctx, ex, _nos_da_execucao(ex_id))
        _conferir_aprovacoes(ctx, ex, _nos_da_execucao(ex_id))
        nos, entrada, _saida = _indices(ex["grafo"])
        ordem, _ = _ordem(ex["grafo"])
        iniciados = []
        mudou = True
        while mudou:
            mudou = False
            est = _nos_da_execucao(ex_id)
            for i in ordem:
                r = est[i]
                if r["status"] != "pendente":
                    continue
                if any(est[a["de"]]["status"] not in TERMINAIS for a in entrada[i]):
                    continue
                ativas = [a for a in entrada[i] if est[a["de"]]["status"] == "concluido" and (est[a["de"]]["porta"] is None or est[a["de"]]["porta"] == a.get("porta"))]
                n = nos[i]
                if entrada[i] and not ativas:
                    mudou |= _marcar(ex_id, i, "pendente", "ignorado", nota="Nenhum caminho ativo chega aqui.")
                elif n.get("desativado"):
                    mudou |= _marcar(ex_id, i, "pendente", "concluido", nota="Nó desativado: o fluxo passa direto.", porta=None)
                elif n["tipo"] in ("entrada", "juncao", "saida"):
                    mudou |= _marcar(ex_id, i, "pendente", "concluido", nota=None)
                elif n["tipo"] == "condicao":
                    c = n.get("config") or {}
                    valor = _valor_condicao(ctx, c.get("campo"))
                    mudou |= _marcar(ex_id, i, "pendente", "concluido", porta="sim" if valor == c.get("valor") else "nao", nota=f"{CONDICOES.get(c.get('campo'), {}).get('nome', '')}: {valor or 'sem valor'}")
                elif n["tipo"] == "aprovacao":
                    material = (n.get("config") or {}).get("material")
                    v = ctx.versoes.get(material)
                    if not v:
                        mudou |= _marcar(ex_id, i, "pendente", "falhou", nota=f"Não há {MATERIAIS_APROVAVEIS.get(material, material).lower()} para aprovar: o agente anterior não gerou o arquivo.")
                    elif _esta_aprovado(ctx, material, v) and not ctx.obsoleto(material):
                        mudou |= _marcar(ex_id, i, "pendente", "concluido", versao_id=v["id"], nota=f"v{v['numero']} já estava aprovada.")
                    else:
                        mudou |= _marcar(ex_id, i, "pendente", "aguardando", versao_id=v["id"], nota=None)
                else:
                    r2 = um("SELECT * FROM exec_nos WHERE exec_id=? AND no=?", ex_id, i)
                    feito = _iniciar_no(ctx, ex, n, r2)
                    mudou |= bool(feito)
                    if feito and um("SELECT status FROM exec_nos WHERE exec_id=? AND no=?", ex_id, i)["status"] == "rodando":
                        iniciados.append(i)
                if mudou:
                    break  # recalcula a foto: o nó concluído pode liberar o seguinte
        est = _nos_da_execucao(ex_id)
        if all(r["status"] in TERMINAIS for r in est.values()):
            faz("UPDATE execucoes SET status='concluida', terminada_em=? WHERE id=? AND status='ativa'", agora(), ex_id)
            evento(slug, f"Execução #{ex_id} concluída")
        return iniciados


def job_terminou(job, spec, erro):
    """Chamado por fluxo.concluir_job. Só aqui um nó de agente ou render muda de estado depois de iniciado."""
    with _lock:
        _job_terminou(job, spec, erro)


def _job_terminou(job, spec, erro):
    marca = spec["exec"]
    ex_id, no = marca["id"], marca["no"]
    ex = um("SELECT * FROM execucoes WHERE id=?", ex_id)
    if not ex:
        return
    grafo = json.loads(ex["grafo"])
    fotos = json.loads(ex["agentes"])
    n = next(x for x in grafo["nos"] if x["id"] == no)
    fluxo.sincronizar(ex["slug"], forcar=True, assentar=False)
    ctx = fluxo.Contexto(ex["slug"])
    if not erro:
        foto_ = fotos.get(no)
        faltando = [ARTEFATOS[_base(s)]["nome"] for s in contrato(n, {foto_["id"]: foto_} if foto_ else {})[1] if not s.endswith("?") and _base(s) in ARTEFATOS and not _existe(ctx, _base(s))]
        if faltando:
            erro = f"{job['craque'] or n['nome']} terminou sem gerar: {', '.join(faltando)}."
    if erro:
        _marcar(ex_id, no, "rodando", "falhou", nota=erro)
    else:
        saidas = {s: ctx.versoes[ARTEFATOS[_base(s)]["material"]]["numero"] for s in contrato(n, {fotos[no]["id"]: fotos[no]} if no in fotos else {})[1] if ARTEFATOS.get(_base(s), {}).get("material") in ctx.versoes}
        foto_ = fotos.get(no)
        h = _hash_entrada(ctx, contrato(n, {foto_["id"]: foto_} if foto_ else {})[0], foto_)
        _marcar(ex_id, no, "rodando", "concluido", entrada_hash=h, saidas=json.dumps(saidas), nota=None)
    avancar(ex_id)


def depois_de_job(slug):
    """Um ajuste pedido na tela de revisão terminou fora de um nó: confere se alguma aprovação precisa reabrir."""
    e = um("SELECT id FROM execucoes WHERE slug=? AND status='ativa'", slug)
    if e:
        avancar(e["id"])


def reconciliar():
    """Rodada da fila: trabalho cancelado ou que sumiu não pode deixar o nó preso em execução. Com o lock, nunca vê um nó entre
    "rodando" e o job dele ser gravado (_iniciar_no faz os dois passos dentro de avancar); job_id nulo aqui é queda no meio disso."""
    with _lock:
        for r in varios("SELECT n.exec_id, n.no, n.job_id, j.status js, j.erro je FROM exec_nos n JOIN execucoes e ON e.id=n.exec_id LEFT JOIN jobs j ON j.id=n.job_id WHERE n.status='rodando' AND e.status='ativa'"):
            if r["js"] in ("cancelado", "falhou") or r["js"] is None:
                _marcar(r["exec_id"], r["no"], "rodando", "falhou", nota=r["je"] or "O trabalho deste nó foi interrompido.")


def aprovar_no(ex_id, no, versao_id):
    """Aprova o material na versão vista. Aprovar duas vezes é uma aprovação só."""
    from . import fluxo as F
    with _lock:
        ex = um("SELECT * FROM execucoes WHERE id=?", ex_id)
        if not ex:
            raise Recusado("Execução não encontrada.", 404)
        grafo = json.loads(ex["grafo"])
        n = next((x for x in grafo["nos"] if x["id"] == no and x["tipo"] == "aprovacao"), None)
        if not n:
            raise Recusado("Este nó não é uma aprovação.", 404)
        r = um("SELECT * FROM exec_nos WHERE exec_id=? AND no=?", ex_id, no)
        if r["status"] != "aguardando":
            return {"iniciados": [], "ja": True, "status": r["status"]}
        material = n["config"]["material"]
        F.sincronizar(ex["slug"], forcar=True)
        v = F.ultima_versao(ex["slug"], material)
        if not v or v["id"] != versao_id:
            raise Recusado("Esta versão não é mais a atual: revise a versão nova antes de decidir.")
        ctx = F.Contexto(ex["slug"])
        if F.feedback_rascunhos(ex["slug"], material, versao_id):
            raise Recusado("Envie ou remova os ajustes anotados nesta versão antes de aprovar.")
        if ctx.obsoleto(material):
            raise Recusado(f"Esta versão está desatualizada: {ctx.obsoleto(material)['motivo']}")
        F.registrar_aprovacao(ex["slug"], material, v)
        if not _marcar(ex_id, no, "aguardando", "concluido", versao_id=v["id"], nota=f"Aprovada a v{v['numero']}."):
            return {"iniciados": [], "ja": True, "status": "concluido"}
        evento(ex["slug"], f"Aprovado no fluxo: {n['nome']} (v{v['numero']})")
        return {"iniciados": avancar(ex_id), "ja": False, "status": "concluido"}


def ao_aprovar(slug, material, versao_id):
    """A aprovação veio da tela de revisão (versão inteira ou último item): conclui o nó que estava esperando por ela."""
    ex = um("SELECT * FROM execucoes WHERE slug=? AND status='ativa'", slug)
    if not ex:
        return []
    with _lock:
        for n in json.loads(ex["grafo"])["nos"]:
            if n["tipo"] == "aprovacao" and (n.get("config") or {}).get("material") == material:
                _marcar(ex["id"], n["id"], "aguardando", "concluido", versao_id=versao_id, nota="Aprovada na revisão.")
        return avancar(ex["id"])


def ao_editar_manual(slug, material):
    """O Guilherme editou o material à mão. Não reabre nem inicia agente. Só um nó de agente que tinha FALHADO em gerar este material
    passa a concluído (a edição é o resultado válido dele), sem avançar o grafo: quem segue é a ação de reauditar."""
    ex = execucao_de(slug)
    if not ex or ex["status"] != "ativa":
        return
    with _lock:
        ctx = fluxo.Contexto(slug)
        est = _nos_da_execucao(ex["id"])
        for n in ex["grafo"]["nos"]:
            r = est.get(n["id"])
            if not r or r["status"] != "falhou" or n["tipo"] != "agente" or n.get("desativado"):
                continue
            foto_ = ex["agentes"].get(n["id"])
            ents, sais = contrato(n, {foto_["id"]: foto_} if foto_ else {})
            if any(ARTEFATOS.get(_base(s), {}).get("material") == material for s in sais) and all(_existe(ctx, _base(s)) for s in sais if not s.endswith("?")):
                if _marcar(ex["id"], n["id"], "falhou", "concluido", entrada_hash=_hash_entrada(ctx, ents, foto_), nota="Editado à mão pelo Guilherme."):
                    evento(slug, f"Fluxo: {n['nome']} concluído pela edição direta")


def reauditar_de(slug):
    """{no, execucao} do nó da auditoria de texto, para o botão "rodar a auditoria de novo" (POST /api/execucoes/<execucao>/repetir {no}).
    None se a produção não está num grafo com esse nó."""
    ex = execucao_de(slug)
    if not ex:
        return None
    for n in ex["grafo"]["nos"]:
        if n["tipo"] == "agente" and not n.get("desativado") and (n.get("config") or {}).get("tarefa") == "auditoria_texto":
            return {"no": n["id"], "execucao": ex["id"]}
    return None


def liberar_no(ex_id, no):
    """Início manual: o botão de iniciar. Só uma chamada sai de aguardando_inicio."""
    with _lock:
        if not _marcar(ex_id, no, "aguardando_inicio", "pendente", liberado=1):
            return {"iniciados": [], "ja": True}
        return {"iniciados": avancar(ex_id), "ja": False}


def repetir_no(ex_id, no):
    """Tenta de novo depois de uma falha, ou refaz de propósito. Só esse nó e o que depende dele."""
    with _lock:
        ex = um("SELECT * FROM execucoes WHERE id=?", ex_id)
        if not ex:
            raise Recusado("Execução não encontrada.", 404)
        r = um("SELECT * FROM exec_nos WHERE exec_id=? AND no=?", ex_id, no)
        if not r:
            raise Recusado("Nó não encontrado.", 404)
        if r["status"] == "rodando":
            return {"iniciados": [], "ja": True}
        if ex["status"] != "ativa":
            faz("UPDATE execucoes SET status='ativa', terminada_em=NULL WHERE id=?", ex_id)
        faz("UPDATE exec_nos SET status='pendente', forcar=1, liberado=1, porta=NULL, nota=NULL, atualizado_em=? WHERE exec_id=? AND no=?", agora(), ex_id, no)
        ex["grafo"] = json.loads(ex["grafo"])
        _reiniciar_dependentes(ex, no)
        return {"iniciados": avancar(ex_id), "ja": False}


def _bloqueio_de(grafo, est, no):
    """Quem segura este nó: o ancestral que falhou (primeiro) ou que espera decisão, início ou trabalho. None se nada o segura."""
    nos, entrada, _ = _indices(grafo)
    vistos, fila, achados = {no}, deque(a["de"] for a in entrada[no]), []
    while fila:
        i = fila.popleft()
        if i in vistos:
            continue
        vistos.add(i)
        if est[i]["status"] in ("falhou", "aguardando", "aguardando_inicio", "rodando") and not nos[i].get("desativado"):
            achados.append(i)
            continue  # o que está antes dele já passou
        fila.extend(a["de"] for a in entrada[i])
    achados.sort(key=lambda i: est[i]["status"] != "falhou")
    return achados[0] if achados else None


def bloqueios(slug):
    """Para a tela: {"execucao": id, "por_material": {material: {execucao, no, nome, status, nota}}}.
    Vale para etapas ainda não iniciadas (nó pendente) ou falhas (o próprio nó). Vazio se a produção não está num grafo ativo."""
    ex = execucao_de(slug)
    if not ex:
        return {"execucao": None, "ativa": False, "por_material": {}}
    est = _nos_da_execucao(ex["id"])
    saida = {}
    if ex["status"] == "ativa":
        for n in ex["grafo"]["nos"]:
            if n["tipo"] not in ("agente", "render") or n.get("desativado"):
                continue
            r = est[n["id"]]
            if r["status"] == "falhou":
                b = n["id"]
            elif r["status"] == "pendente":
                b = _bloqueio_de(ex["grafo"], est, n["id"])
            else:
                continue
            if not b:
                continue
            foto_ = ex["agentes"].get(n["id"])
            materiais = {ARTEFATOS[_base(s)]["material"] for s in contrato(n, {foto_["id"]: foto_} if foto_ else {})[1] if ARTEFATOS.get(_base(s), {}).get("material")}
            acao = (n.get("config") or {}).get("acao")
            if n["tipo"] == "render" and acao in ACOES:
                materiais.add(ACOES[acao]["saidas"][0])
            bn = next(x for x in ex["grafo"]["nos"] if x["id"] == b)
            info = {"execucao": ex["id"], "no": b, "nome": bn["nome"], "status": est[b]["status"], "nota": est[b]["nota"]}
            for m in materiais:
                if m not in saida or info["status"] == "falhou":
                    saida[m] = info
    return {"execucao": ex["id"], "ativa": ex["status"] == "ativa", "por_material": saida}


def migrar_execucao(slug, numero=None):
    """Passa uma execução ativa para outra versão publicada do mesmo fluxo (por padrão a mais nova), sem perder o que já aconteceu:
    nós com o mesmo id mantêm o estado; nós novos entram pendentes; nós que sumiram saem. Recusa se algum nó que sai está rodando.
    Não dispara nada: quem decide o próximo passo continua sendo avancar()."""
    with _lock:
        ex = um("SELECT * FROM execucoes WHERE slug=? AND status='ativa'", slug)
        if not ex:
            raise Recusado("Este projeto não tem execução ativa.")
        v = um("SELECT * FROM fluxo_versoes WHERE fluxo=? AND numero=?", ex["fluxo"], numero) if numero else um("SELECT * FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", ex["fluxo"])
        if not v or v["numero"] == ex["fluxo_numero"]:
            raise Recusado("Não há versão diferente para migrar.")
        novo = json.loads(v["grafo"])
        ids_novos = {n["id"] for n in novo["nos"]}
        est = _nos_da_execucao(ex["id"])
        for i, r in est.items():
            if i not in ids_novos and r["status"] == "rodando":
                raise Recusado(f"O nó {i} está rodando e não existe na versão {v['numero']}: espere terminar.")
        fotos = json.loads(ex["agentes"])
        for n in novo["nos"]:
            c = n.get("config") or {}
            if n["tipo"] == "agente" and c.get("agente") and n["id"] not in fotos:
                fotos[n["id"]] = AG.foto(c["agente"])
        for i in est:
            if i not in ids_novos:
                faz("DELETE FROM exec_nos WHERE exec_id=? AND no=?", ex["id"], i)
        for i in ids_novos - set(est):
            faz("INSERT INTO exec_nos (exec_id, no, status, forcar, atualizado_em) VALUES (?,?, 'pendente', 0, ?)", ex["id"], i, agora())
        faz("UPDATE execucoes SET fluxo_versao=?, fluxo_numero=?, grafo=?, agentes=? WHERE id=?", v["id"], v["numero"], v["grafo"], json.dumps(fotos, ensure_ascii=False), ex["id"])
        evento(slug, f"Execução #{ex['id']} migrada do fluxo v{ex['fluxo_numero']} para v{v['numero']}")
        return {"execucao": ex["id"], "de": ex["fluxo_numero"], "para": v["numero"], "removidos": sorted(set(est) - ids_novos), "novos": sorted(ids_novos - set(est))}


def ao_trocar_estilo(slug, materiais, estilo_mudou):
    """Reabre só o que o novo estilo invalida: a condição de estilo e os nós que produzem esses materiais, com o que vem depois deles."""
    ex = execucao_de(slug)
    if not ex:
        return []
    with _lock:
        estados = _nos_da_execucao(ex["id"])
        alvos = []
        for n in ex["grafo"]["nos"]:
            c = n.get("config") or {}
            if n["tipo"] == "condicao" and c.get("campo") == "estilo" and estilo_mudou:
                alvos.append(n["id"])
            elif n["tipo"] in ("agente", "render"):
                sais = contrato(n, {})[1]
                if {ARTEFATOS[_base(x)]["material"] for x in sais if _base(x) in ARTEFATOS} & set(materiais):
                    alvos.append(n["id"])
        alvos = [i for i in alvos if estados[i]["status"] not in ("pendente", "rodando")]
        if not alvos:
            return []
        faz("UPDATE execucoes SET status='ativa', terminada_em=NULL WHERE id=?", ex["id"])
        for i in alvos:
            faz("UPDATE exec_nos SET status='pendente', porta=NULL, nota=NULL, atualizado_em=? WHERE exec_id=? AND no=? AND status<>'rodando'", agora(), ex["id"], i)
            _reiniciar_dependentes(ex, i)
        faz("UPDATE exec_nos SET liberado=0 WHERE exec_id=? AND status='pendente'", ex["id"])  # render e narração voltam a esperar o clique
        evento(slug, "Fluxo reaberto pela troca de estilo: " + ", ".join(alvos))
        avancar(ex["id"])
        return alvos


def devolver(ex_id, no, texto, cena=None, tempo_s=None, categoria=None, item=None):
    """Pedir ajuste numa aprovação: o comentário vai para quem é dono do material. Só este ramo volta a esperar; o outro continua com as aprovações dele."""
    with _lock:
        ex = um("SELECT * FROM execucoes WHERE id=?", ex_id)
        if not ex:
            raise Recusado("Execução não encontrada.", 404)
        ex["grafo"] = json.loads(ex["grafo"])
        n = next((x for x in ex["grafo"]["nos"] if x["id"] == no and x["tipo"] == "aprovacao"), None)
        if not n:
            raise Recusado("Este nó não é uma aprovação.", 404)
        r = um("SELECT * FROM exec_nos WHERE exec_id=? AND no=?", ex_id, no)
        if r["status"] not in ("aguardando", "concluido"):
            raise Recusado("Esta aprovação ainda não chegou à sua vez.")
        material = n["config"]["material"]
        fluxo.sincronizar(ex["slug"], forcar=True)
        v = fluxo.ultima_versao(ex["slug"], material)
        if not v:
            raise Recusado("Não há material para ajustar.")
        if item is None and cena is not None and material in ("narracao", "cenas") and f"cena_{cena}" in v["manifesto"]["itens"]:
            item = f"cena_{cena}"
        fb = fluxo.anotar_feedback(ex["slug"], material, v["id"], texto, item, cena, tempo_s, categoria)
        faz("UPDATE feedback SET no=? WHERE id=?", no, fb["id"])
        jobs = fluxo.enviar_ajustes(ex["slug"], material, v["id"])
        if r["status"] == "concluido":
            _marcar(ex_id, no, "concluido", "aguardando", versao_id=v["id"], nota="Ajuste pedido: espera a nova versão.")
        _reiniciar_dependentes(ex, no)
        evento(ex["slug"], f"Ajuste pedido em {n['nome']}: só este ramo volta a esperar.")
        return {"jobs": [j["id"] for j in jobs]}


def agente_de_no_para(slug, dono_material):
    """Ajuste pedido na revisão: quem atende é o agente do nó daquele material, na versão da execução."""
    ex = execucao_de(slug)
    if not ex or ex["status"] != "ativa":
        return None
    for n in ex["grafo"]["nos"]:
        if n["tipo"] == "agente" and not n.get("desativado") and ex["agentes"].get(n["id"]):
            sais = contrato(n, {ex["agentes"][n["id"]]["id"]: ex["agentes"][n["id"]]})[1]
            est = um("SELECT status FROM exec_nos WHERE exec_id=? AND no=?", ex["id"], n["id"])
            if est and est["status"] == "ignorado":
                continue
            if any(ARTEFATOS.get(_base(s), {}).get("material") == dono_material for s in sais):
                return ex["agentes"][n["id"]]
    return None


# ---------- Visões para as telas ----------

def _funcao(no):
    c = no.get("config") or {}
    if no["tipo"] == "agente":
        return TAREFAS.get(c.get("tarefa") or "livre", TAREFAS["livre"])["nome"]
    if no["tipo"] == "render":
        return ACOES.get(c.get("acao"), {}).get("nome", "Render")
    if no["tipo"] == "aprovacao":
        return f"Sua decisão sobre {MATERIAIS_APROVAVEIS.get(c.get('material'), '').lower()}"
    return TIPOS[no["tipo"]]["ajuda"]


def visao_execucao(slug):
    from . import trabalhos
    ex = execucao_de(slug)
    if not ex:
        return None
    if ex["status"] == "ativa":
        reconciliar()
    est = _nos_da_execucao(ex["id"])
    ctx = fluxo.Contexto(slug)
    atual_v = um("SELECT numero FROM fluxo_versoes WHERE fluxo=? ORDER BY numero DESC LIMIT 1", ex["fluxo"])
    ordem, _ = _ordem(ex["grafo"])
    nos = {n["id"]: n for n in ex["grafo"]["nos"]}
    linhas = []
    for i in ordem:
        n, r = nos[i], est.get(i)
        if not r:
            continue
        foto_ = ex["agentes"].get(i)
        job = um("SELECT * FROM jobs WHERE id=?", r["job_id"]) if r["job_id"] else None
        progresso = trabalhos.progresso(job, ctx) if job and job["status"] == "rodando" else None
        ents, sais = contrato(n, {foto_["id"]: foto_} if foto_ else {})
        versao = None
        if n["tipo"] == "aprovacao" and r["versao_id"]:
            v = um("SELECT id, numero FROM versoes WHERE id=?", r["versao_id"])
            versao = {"id": v["id"], "numero": v["numero"]} if v else None
        linhas.append({"no": i, "nome": n["nome"], "tipo": n["tipo"], "funcao": _funcao(n), "status": r["status"], "status_texto": STATUS[r["status"]], "nota": r["nota"], "atualizado_em": r["atualizado_em"], "job": fluxo.status_job_publico(job) if job else None, "progresso": progresso,
                       "agente": foto_["id"] if foto_ else None, "craque": foto_["craque"] if foto_ else None, "agente_versao": foto_["versao"] if foto_ else None, "agente_sha": foto_["sha"][:10] if foto_ else None,
                       "entradas": ents, "saidas": sais, "saidas_versoes": json.loads(r["saidas"]) if r["saidas"] else {}, "material": (n.get("config") or {}).get("material"), "versao": versao, "manual": (n.get("config") or {}).get("inicio") == "manual"})
    return {"id": ex["id"], "fluxo": ex["fluxo"], "fluxo_numero": ex["fluxo_numero"], "fluxo_atual": atual_v["numero"] if atual_v else None, "status": ex["status"], "criada_em": ex["criada_em"], "linhas": linhas, "grafo": ex["grafo"]}
