"""Catálogo de agentes: lê e escreve o formato nativo do Claude Code (.claude/agents/<id>.md, com frontmatter).

O arquivo é a definição: o que se salva aqui vale também para quem chama o agente pelo terminal, e o que muda pelo terminal aparece aqui
como versão nova. O banco guarda só o histórico. Desativar é tirar o arquivo de .claude/agents, porque isso é o que o runtime entende.
"""
import json
import re
import shutil

from . import materiais as M
from .banco import agora, faz, um, varios
from .config import DADOS, RAIZ, SAIDA
from .fluxo import Recusado

ATIVOS = RAIZ / ".claude" / "agents"
DESATIVADOS = RAIZ / ".claude" / "agents_desativados"
SANDBOX = DADOS / "testes_agente"
ID_OK = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Ferramentas nativas que os agentes do repositório já usam ou que o executor já autoriza (executor.FERRAMENTAS). Nada de comando livre.
FERRAMENTAS_BASE = ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebSearch", "WebFetch", "Agent"]
MODELOS_BASE = ["sonnet", "opus", "haiku"]
ACENTOS = {"mbappe": "Mbappé", "modric": "Modric", "dembele": "Dembelé", "andre": "André", "hugo": "Hugo Souza", "yuri": "Yuri Alberto", "luiz": "Luiz Henrique", "lamine": "Lamine Yamal", "debruyne": "De Bruyne"}
FERRAMENTAS_SANDBOX = {"Read", "Write", "Edit", "Glob", "Grep"}
EXEMPLOS_DE_ENTRADA = {"notas": "notas.md", "angulo": "angulo.md", "roteiro": "roteiro.txt", "direcao_viral": "direcao_viral.md", "cenas": "cenas.json", "metadados": "metadados.json", "revisao": "revisao.md"}
ORCAMENTO_TESTE = "1.00"

# Contrato de quem ainda não declarou o seu no frontmatter (`entradas:` e `saidas:`). Vem do "Contrato de arquivos" do CLAUDE.md. Entrada com ? é opcional.
CONTRATOS = {
    "modric-pesquisador-tema": ("briefing", "notas"),
    "messi-estrategista-angulo": ("notas", "angulo"),
    "neymar-roteirista": ("notas", "angulo, roteiro, direcao_viral"),
    "courtois-revisor-fatos": ("notas, roteiro", "revisao"),
    "cristiano-otimizador-viral": ("roteiro", "direcao_viral"),
    "raphinha-curador-componentes": ("roteiro", "componentes"),
    "olise-diretor-arte": ("roteiro, direcao_viral?, componentes?", "cenas"),
    "barcola-diretor-horizontal": ("roteiro, direcao_viral?, componentes?", "cenas"),
    "mbappe-editor-metadados": ("roteiro, angulo?", "metadados"),
    "vini-auditor-conformidade": ("roteiro, notas, cenas?, metadados?, video?", "auditoria_texto?, auditoria_final?"),
    "sidorf-thumbnail-estrategista": ("video", "thumbnail"),
}
CAMPOS_ORDEM = ["name", "description", "tools", "model", "entradas", "saidas"]


def nome_curto(ident):
    primeira = ident.split("-")[0]
    nome = ACENTOS.get(primeira, primeira.capitalize())
    return f"{nome} (cópia)" if re.search(r"-copia(-\d+)?$", ident) else nome


def analisar(texto):
    """Lê o frontmatter por linha, sem YAML: as descrições têm dois-pontos e aspas que o YAML recusaria, e o Claude Code aceita assim."""
    texto = texto.replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---\n?(.*)\Z", texto, re.S)
    if not m:
        return {}, texto
    campos = {}
    for linha in m.group(1).split("\n"):
        if ":" in linha and not linha.startswith((" ", "\t")):
            k, v = linha.split(":", 1)
            campos[k.strip()] = v.strip()
    return campos, m.group(2)


def montar(campos, corpo):
    linhas = [f"{k}: {campos[k]}" for k in CAMPOS_ORDEM if campos.get(k)]
    linhas += [f"{k}: {v}" for k, v in campos.items() if k not in CAMPOS_ORDEM and v]
    return "---\n" + "\n".join(linhas) + "\n---\n" + corpo.lstrip("\n")


def reescrever(original, campos, corpo):
    """Salvar sem mudar o que o usuario nao mexeu: parte do texto original (LF) e troca so as linhas de chave cujo valor mudou.
    Preserva a ordem das chaves, linhas de continuacao, a linha em branco depois do frontmatter e o fim do corpo."""
    m = re.match(r"---\n(.*?)\n---\n?(.*)\Z", original, re.S)
    if not m:
        return montar(campos, corpo)
    saida, vistas = [], set()
    for linha in m.group(1).split("\n"):
        if ":" in linha and not linha.startswith((" ", "\t")):
            k, v = linha.split(":", 1)
            k = k.strip()
            vistas.add(k)
            novo = campos.get(k)
            if novo is None or novo == "":
                continue
            saida.append(linha if v.strip() == novo else f"{k}: {novo}")
        else:
            saida.append(linha)
    saida += [f"{k}: {v}" for k, v in campos.items() if k not in vistas and v]
    antigo = m.group(2)
    abertura = antigo[:len(antigo) - len(antigo.lstrip("\n"))]
    fim = antigo[len(antigo.rstrip("\n")):]
    novo_corpo = corpo.lstrip("\n")
    if novo_corpo and novo_corpo == novo_corpo.rstrip("\n"):
        novo_corpo += fim
    return "---\n" + "\n".join(saida) + "\n---\n" + abertura + novo_corpo


def estilo_de(arq):
    """(crlf, bom) do arquivo existente; arquivo novo e LF sem BOM."""
    try:
        b = arq.read_bytes()
    except OSError:
        return False, False
    return b.count(b"\r\n") * 2 > b.count(b"\n"), b.startswith(b"\xef\xbb\xbf")


def lista_csv(v):
    """Separa por vírgula sem quebrar Agent(a, b, c), a forma nativa de limitar quem o agente pode chamar."""
    saida, atual, nivel = [], "", 0
    for ch in v or "":
        nivel += ch == "("
        nivel -= ch == ")"
        if ch == "," and not nivel:
            saida.append(atual.strip())
            atual = ""
        else:
            atual += ch
    if atual.strip():
        saida.append(atual.strip())
    return saida


def _arquivo(ident):
    if not ID_OK.fullmatch(ident or ""):
        raise Recusado("Identificador de agente inválido: use letras minúsculas, números e hífen.", 400)
    return ATIVOS / f"{ident}.md", DESATIVADOS / f"{ident}.md"


def _ler(ident):
    ativo, parado = _arquivo(ident)
    if ativo.exists():
        return ativo, True
    if parado.exists():
        return parado, False
    raise Recusado(f"Agente não encontrado: {ident}.", 404)


def registrar_versao(ident, texto, origem):
    """Compara com a última versão: mudança feita por fora (terminal, git) entra como versão nova, sem se perder."""
    texto = texto.replace("\r\n", "\n")
    sha = M.sha_texto(texto)
    u = um("SELECT numero, sha FROM agente_versoes WHERE agente=? ORDER BY numero DESC LIMIT 1", ident)
    if u and u["sha"] == sha:
        return u["numero"]
    numero = (u["numero"] if u else 0) + 1
    faz("INSERT OR IGNORE INTO agente_versoes (agente, numero, sha, texto, origem, criada_em) VALUES (?,?,?,?,?,?)", ident, numero, sha, texto, origem if u else "existente", agora())
    return numero


def _contrato(ident, campos):
    padrao = CONTRATOS.get(ident, ("", ""))
    return {"entradas": lista_csv(campos.get("entradas") if campos.get("entradas") is not None else padrao[0]), "saidas": lista_csv(campos.get("saidas") if campos.get("saidas") is not None else padrao[1]), "declarado": "entradas" in campos or "saidas" in campos}


def _visao(ident, arq, ativo):
    texto = arq.read_text(encoding="utf-8-sig")
    numero = registrar_versao(ident, texto, "disco")
    campos, corpo = analisar(texto)
    return {"id": ident, "nome": campos.get("name") or ident, "craque": nome_curto(ident), "descricao": campos.get("description", ""), "ferramentas": lista_csv(campos.get("tools", "")), "modelo": campos.get("model") or "", "instrucoes": corpo, "contrato": _contrato(ident, campos), "ativo": ativo, "versao": numero, "arquivo": str(arq.relative_to(RAIZ)).replace("\\", "/")}


def catalogo():
    saida = []
    for pasta, ativo in ((ATIVOS, True), (DESATIVADOS, False)):
        if pasta.is_dir():
            saida += [_visao(f.stem, f, ativo) for f in sorted(pasta.glob("*.md"))]
    return saida


def opcoes():
    """Só o que existe de fato: ferramentas e modelos que o catálogo usa, mais os nativos. Nada digitado vira comando."""
    ferr, mods = list(FERRAMENTAS_BASE), list(MODELOS_BASE)
    for a in catalogo():
        ferr += [f for f in a["ferramentas"] if f not in ferr]
        if a["modelo"] and a["modelo"] not in mods:
            mods.append(a["modelo"])
    return {"ferramentas": ferr, "modelos": mods}


def detalhe(ident):
    from . import grafos
    arq, ativo = _ler(ident)
    v = _visao(ident, arq, ativo)
    v["versoes"] = varios("SELECT numero, sha, origem, criada_em FROM agente_versoes WHERE agente=? ORDER BY numero DESC", ident)
    v["usos"] = grafos.usos_do_agente(ident)
    v["testes"] = varios("SELECT id, versao, entrada, status, saida, arquivos, erro, custo_usd, job_id, criada_em FROM agente_testes WHERE agente=? ORDER BY id DESC LIMIT 10", ident)
    return v


def _validar_campos(d):
    op = opcoes()
    desc = " ".join(str(d.get("descricao") or "").split())
    if len(desc) < 5:
        raise Recusado("Escreva uma descrição: é por ela que o Claude Code decide quando usar o agente.", 400)
    ferramentas = d.get("ferramentas") or []
    invalidas = [f for f in ferramentas if f not in op["ferramentas"]]
    if invalidas:
        raise Recusado(f"Ferramenta não disponível: {', '.join(invalidas)}. Comandos de shell novos não entram pela interface.", 400)
    if d.get("modelo") and d["modelo"] not in op["modelos"]:
        raise Recusado(f"Modelo não disponível: {d['modelo']}.", 400)
    if not str(d.get("instrucoes") or "").strip():
        raise Recusado("As instruções não podem ficar vazias.", 400)
    return desc, ferramentas


def _gravar(arq, texto, estilo=None):
    """Grava em bytes para nao deixar o Windows trocar LF por CRLF; `estilo` = (crlf, bom), por padrao o do arquivo que ja existe."""
    crlf, bom = estilo if estilo is not None else estilo_de(arq)
    texto = texto.replace("\r\n", "\n")
    if crlf:
        texto = texto.replace("\n", "\r\n")
    arq.parent.mkdir(parents=True, exist_ok=True)
    tmp = arq.with_suffix(".tmp")
    tmp.write_bytes((b"\xef\xbb\xbf" if bom else b"") + texto.encode("utf-8"))
    tmp.replace(arq)


def _campos_de(ident, d, base=None):
    desc, ferramentas = _validar_campos(d)
    campos = dict(base or {})
    campos.update(name=ident, description=desc, tools=", ".join(ferramentas), model=d.get("modelo") or "")
    contrato = d.get("contrato") or {}
    for chave in ("entradas", "saidas"):
        if chave in contrato:
            itens = [str(x).strip() for x in contrato[chave] if str(x).strip()]
            ruins = [x for x in itens if not re.fullmatch(r"\w+\??", x)]
            if ruins:
                raise Recusado(f"Campo de contrato inválido: {', '.join(ruins)}.", 400)
            if chave not in campos and itens == _contrato(ident, campos)[chave]:
                continue  # o contrato padrão (por id) não declarado no arquivo continua sem aparecer nele
            campos[chave] = ", ".join(itens)
    return campos


def criar(d):
    ident = str(d.get("id") or "").strip()
    ativo, parado = _arquivo(ident)
    if ativo.exists() or parado.exists():
        raise Recusado(f"Já existe um agente com o identificador {ident}.")
    _gravar(ativo, montar(_campos_de(ident, d), d["instrucoes"]))
    registrar_versao(ident, ativo.read_text(encoding="utf-8"), "corte")
    return detalhe(ident)


def duplicar(ident, novo=None):
    arq, _ = _ler(ident)
    texto = arq.read_text(encoding="utf-8-sig")
    campos, corpo = analisar(texto)
    novo = novo or f"{ident}-copia"
    n = 2
    base = novo
    while (ATIVOS / f"{novo}.md").exists() or (DESATIVADOS / f"{novo}.md").exists():
        novo, n = f"{base}-{n}", n + 1
    destino, _ = _arquivo(novo)
    campos["name"] = novo
    # O contrato padrão é pelo id: a cópia recebe o dele por escrito, para continuar valendo.
    contrato = _contrato(ident, campos)
    campos["entradas"], campos["saidas"] = ", ".join(contrato["entradas"]), ", ".join(contrato["saidas"])
    _gravar(destino, montar(campos, corpo), estilo_de(arq))
    registrar_versao(novo, destino.read_text(encoding="utf-8"), "corte")
    return detalhe(novo)


def salvar(ident, d, versao_vista):
    """`versao_vista` impede sobrescrever em silêncio uma mudança feita pelo terminal enquanto a tela estava aberta."""
    arq, ativo = _ler(ident)
    atual = _visao(ident, arq, ativo)
    if versao_vista is not None and versao_vista != atual["versao"]:
        raise Recusado(f"O agente mudou por fora (agora v{atual['versao']}). Recarregue antes de salvar.")
    original = arq.read_text(encoding="utf-8-sig").replace(chr(13) + chr(10), chr(10))
    estilo = estilo_de(arq)
    campos, _ = analisar(original)
    novo_id = str(d.get("id") or ident).strip()
    if novo_id != ident:
        from . import grafos
        usos = grafos.usos_do_agente(ident)
        if usos:
            raise Recusado("Este nome está em uso em: " + ", ".join(sorted({u["fluxo_nome"] for u in usos})) + ". Troque o agente nos nós antes de renomear.")
        destino, parado = _arquivo(novo_id)
        if destino.exists() or parado.exists():
            raise Recusado(f"Já existe um agente com o identificador {novo_id}.")
    campos = _campos_de(novo_id, d, campos)
    texto = reescrever(original, campos, d["instrucoes"])
    if novo_id != ident:
        destino = arq.with_name(f"{novo_id}.md")
        _gravar(destino, texto, estilo)
        arq.unlink()
        faz("UPDATE agente_versoes SET agente=? WHERE agente=?", novo_id, ident)
        registrar_versao(novo_id, texto, "corte")
        return detalhe(novo_id)
    _gravar(arq, texto)
    registrar_versao(ident, texto, "corte")
    return detalhe(ident)


def alternar(ident, ativo):
    arq, esta = _ler(ident)
    destino = (ATIVOS if ativo else DESATIVADOS) / f"{ident}.md"
    if esta != bool(ativo):
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(arq), str(destino))
    return detalhe(ident)


def texto_da_versao(ident, numero):
    v = um("SELECT * FROM agente_versoes WHERE agente=? AND numero=?", ident, numero)
    if not v:
        raise Recusado("Versão do agente não encontrada.", 404)
    return v


def comparar(ident, a, b):
    va, vb = texto_da_versao(ident, a), texto_da_versao(ident, b)
    return {"de": a, "para": b, "ops": M.diff_palavras(va["texto"], vb["texto"])}


def restaurar(ident, numero):
    """Restaurar não apaga história: a versão antiga volta como a mais nova."""
    v = texto_da_versao(ident, numero)
    arq, _ = _ler(ident)
    _gravar(arq, v["texto"])
    registrar_versao(ident, v["texto"], f"restaurada de v{numero}")
    return detalhe(ident)


def foto(ident):
    """O que uma execução guarda do agente ao começar: dali em diante ela usa esta foto, mesmo que o arquivo mude."""
    arq, ativo = _ler(ident)
    v = _visao(ident, arq, ativo)
    texto = arq.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return {"id": ident, "versao": v["versao"], "sha": M.sha_texto(texto), "corpo": v["instrucoes"], "modelo": v["modelo"], "ferramentas": v["ferramentas"], "craque": v["craque"], "ativo": ativo, "contrato": v["contrato"]}


def testar(ident, entrada, slug_exemplo=None, versao=None):
    """Roda o agente de verdade, em uma pasta só para o teste, sem tocar em nenhum projeto."""
    from . import fluxo, trabalhos
    entrada = str(entrada or "").strip()
    if len(entrada) < 3:
        raise Recusado("Escreva a entrada de exemplo.", 400)
    faltas = [] if trabalhos.integracoes()["claude"]["ok"] else [trabalhos.integracoes()["claude"]["detalhe"]]
    if faltas:
        raise Recusado(faltas)
    f = foto(ident)
    if versao is not None and versao != f["versao"]:
        v = texto_da_versao(ident, versao)
        campos, corpo = analisar(v["texto"])
        f.update(versao=versao, sha=v["sha"], corpo=corpo, modelo=campos.get("model") or "", ferramentas=lista_csv(campos.get("tools", "")))
    ferramentas = [x for x in f["ferramentas"] if x in FERRAMENTAS_SANDBOX] or ["Read", "Write"]
    cur = faz("INSERT INTO agente_testes (agente, versao, entrada, status, criada_em) VALUES (?,?,?,'fila',?)", ident, f["versao"], entrada, agora())
    teste = cur.lastrowid
    pasta = SANDBOX / str(teste)
    copiados = []
    (pasta / "output" / "exemplo").mkdir(parents=True, exist_ok=True)
    if slug_exemplo:
        origem = SAIDA / slug_exemplo
        if not re.fullmatch(r"[\w-][\w.-]*", slug_exemplo) or not M.e_producao(origem):
            faz("DELETE FROM agente_testes WHERE id=?", teste)
            raise Recusado(f"Projeto de exemplo não encontrado: {slug_exemplo}.", 404)
        for nome in dict.fromkeys(EXEMPLOS_DE_ENTRADA.get(x.rstrip("?")) for x in f["contrato"]["entradas"]):
            if nome and (origem / nome).is_file():
                shutil.copyfile(origem / nome, pasta / "output" / "exemplo" / nome)
                copiados.append(nome)
    prompt = (f"Este é um TESTE isolado do agente, sem produção real. Trabalhe só na pasta atual. A produção de exemplo é output/exemplo/"
              + (f", que já tem {', '.join(copiados)}" if copiados else "") + f". Não pergunte nada.\n\nEntrada de exemplo:\n{entrada}")
    spec = {"tipo": "agente", "agente": ident, "prompt": prompt, "raia": "agente", "craque": f["craque"], "origem": "teste_agente", "teste": teste, "materiais": [], "titulo": f"Teste de {ident} v{f['versao']}", "cwd": str(pasta), "orcamento": ORCAMENTO_TESTE, "ferramentas_aprovadas": ",".join(ferramentas),
            "sistema": {"corpo": f["corpo"], "modelo": f["modelo"], "ferramentas": ferramentas, "versao": f["versao"], "sha": f["sha"]}}
    job, _novo = fluxo.inserir_job("__agentes__", f"teste:{teste}", spec, assinatura=f"teste:{teste}")
    faz("UPDATE agente_testes SET job_id=? WHERE id=?", job["id"], teste)
    return {"teste": teste, "job": job["id"], "versao": f["versao"], "copiados": copiados}


def teste_terminou(spec, job, resultado):
    """Grava a saída real: o que o agente respondeu e os arquivos que ele criou na pasta do teste."""
    pasta = SANDBOX / str(spec["teste"])
    arquivos = []
    if pasta.is_dir():
        for f in sorted(pasta.rglob("*")):
            if f.is_file():
                rel = str(f.relative_to(pasta)).replace("\\", "/")
                arquivos.append({"nome": rel, "bytes": f.stat().st_size, "texto": M.ler_texto(f)[:6000] if f.suffix.lower() in (".md", ".txt", ".json", ".py") else None, "entrada": rel.startswith("output/exemplo/") and f.stat().st_mtime < _inicio_teste(job)})
    faz("UPDATE agente_testes SET status=?, saida=?, arquivos=?, erro=?, custo_usd=? WHERE id=?", "falhou" if resultado.get("erro") else "ok", resultado.get("saida") or resultado.get("resumo"), json.dumps([a for a in arquivos if not a["entrada"]], ensure_ascii=False), resultado.get("erro"), resultado.get("custo_usd"), spec["teste"])


def _inicio_teste(job):
    from datetime import datetime
    try:
        return datetime.fromisoformat(job["iniciado_em"]).timestamp()
    except (TypeError, ValueError):
        return 0
