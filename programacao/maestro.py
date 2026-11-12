"""Maestro da sprint: chama sozinho o agente dono de cada coluna do quadro enquanto a sprint está ABERTA.

A cada rodada (tarefa agendada ContextoExplica-Sprint, de 15 em 15 min) ele vê os cartões de programacao/quadro.md,
chama em modo headless o dono da coluna de cada cartão devido, lê a decisão que o agente grava em
programacao/maestro/decisoes/PROG-NNN.json, move o cartão no quadro, sincroniza o Trello (coluna, "Status atual",
comentário, checks de critérios) e avisa o Guilherme no Telegram. Os agentes nunca movem cartão nem editam o quadro.

Uso:
  python programacao/maestro.py              uma rodada
  python programacao/maestro.py --simular    mostra quem seria chamado, sem chamar nem escrever
  python programacao/maestro.py --forcar PROG-005   chama o dono desse cartão agora, mesmo sem mudança
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "produtividade"))
import avisar  # noqa: E402
import kanban_programacao as kp  # noqa: E402
import trello_sync as ts  # noqa: E402

PROG = RAIZ / "programacao"
QUADRO = PROG / "quadro.md"
BACKUP = PROG / ".quadro.bak.md"
BACKLOG = PROG / "backlog.md"
MAESTRO = PROG / "maestro"
DECISOES = MAESTRO / "decisoes"
RESPOSTAS = MAESTRO / "respostas"
ACEITES = PROG / "aceites"
ESTADO = MAESTRO / "estado.json"
LOG = MAESTRO / "log.md"
LOCK = MAESTRO / ".lock"
NOTAS_RELEASE = PROG / "release" / "notas-sprint-01.md"

JANELA = (7, 23)  # horas do dia em que o maestro trabalha
REENVIO = timedelta(minutes=90)
MAX_MANTIDOS = 3
MAX_DEVOLUCOES = 2
MAX_GRUPOS_POR_RODADA = 4
LIMITE_DIA_USD = 30.0
ACEITE_DO_GUILHERME = True  # Pronto para aceite -> Feito só com programacao/aceites/PROG-NNN.md
NO_WINDOW = 0x08000000

DONOS = {
    "Pronto para aceite": ("zico-po-programacao", "Zico"),
    "Code Review": ("thiago-silva-tech-lead", "Thiago Silva"),
    "Em teste": ("alisson-qa", "Alisson"),
    "Fazendo": (None, None),  # o dev dono do item
    "Bloqueado": ("xavi-scrum-master", "Xavi"),
    "Backlog da sprint": ("xavi-scrum-master", "Xavi"),
    "Em refinamento técnico": ("thiago-silva-tech-lead", "Thiago Silva"),
    "Feito": ("marquinhos-devops-release", "Marquinhos"),
}
DEVS = {"Rodrygo": ("rodrygo-dev-back", "Rodrygo"), "Endrick": ("endrick-dev-front", "Endrick")}
SAIDAS = {
    "Backlog da sprint": {"Fazendo"},
    "Em refinamento técnico": {"Backlog da sprint"},
    "Fazendo": {"Em teste"},
    "Em teste": {"Code Review", "Fazendo"},
    "Code Review": {"Pronto para aceite", "Fazendo"},
    "Pronto para aceite": {"Feito", "Fazendo"},
    "Bloqueado": {"Fazendo", "Backlog da sprint"},
    "Feito": set(),
}
DEVOLUCAO_DE = {"Em teste", "Code Review", "Pronto para aceite"}
PODE_MARCAR_CRITERIOS = {"Alisson", "Thiago Silva", "Zico"}
CARTAO = re.compile(r"^(?:- |\d+\. )\[(PROG-\d+)\]")
MARCA = re.compile(r" · Maestro: .*$")
BLOCO_TRELLO = re.compile(r"\A## Status atual \(maestro\)\n.*?\n\n(?=## |\Z)", re.S)
BASH_TESTE = ["Bash(node estudio/testes/*)", "Bash(.venv/Scripts/python.exe -X utf8 estudio/testes/*)",
              "Bash(.venv/Scripts/python.exe estudio/testes/*)"]
BASH_GIT = ["Bash(git status*)", "Bash(git diff*)", "Bash(git log*)", "Bash(git show*)"]
FERRAMENTAS = {
    "rodrygo-dev-back": BASH_TESTE + BASH_GIT, "endrick-dev-front": BASH_TESTE + BASH_GIT,
    "alisson-qa": BASH_TESTE + BASH_GIT, "thiago-silva-tech-lead": BASH_GIT, "marquinhos-devops-release": BASH_GIT,
}
PROIBIDO = ["Read(./.env*)", "Edit(./.env*)", "Write(./.env*)", "Read(./**/*token*.json)", "Read(./client_secret*)",
            "Edit(./programacao/quadro.md)", "Write(./programacao/quadro.md)", "Edit(./programacao/maestro.py)",
            "Write(./programacao/maestro.py)", "Edit(./programacao/maestro/estado.json)", "Write(./programacao/maestro/estado.json)",
            "Edit(./programacao/maestro/log.md)", "Write(./programacao/maestro/log.md)", "Edit(./.claude/**)", "Write(./.claude/**)",
            "Edit(./CLAUDE.md)", "Write(./CLAUDE.md)", "Edit(./programacao/aceites/**)", "Write(./programacao/aceites/**)",
            # Com bypassPermissions o Bash fica livre; estas travas seguram segredo, commit/publicação e destruição.
            "Bash(*.env*)", "Bash(*client_secret*)", "Bash(*token*.json*)", "Bash(git commit*)", "Bash(git push*)",
            "Bash(git reset*)", "Bash(git checkout*)", "Bash(git clean*)", "Bash(git stash*)", "Bash(git rebase*)",
            "Bash(rm -rf*)", "Bash(rm -r *)", "Bash(rmdir*)", "Bash(del *)", "Bash(rd *)", "Bash(Remove-Item*)",
            "Bash(*postar_pendentes*)", "Bash(python run.py publish*)", "Bash(*programacao/quadro.md*)",
            "Bash(*programacao/maestro/estado.json*)", "Bash(*programacao/maestro.py*)"]
PERFIL = {  # teto em US$ e tempo em minutos por chamada
    "rodrygo-dev-back": ("4.00", 60), "endrick-dev-front": ("4.00", 60), "alisson-qa": ("3.00", 45),
}


def agora():
    return datetime.now()


def agora_txt():
    return f"{agora():%d/%m %H:%M}"


def log(msg):
    MAESTRO.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{agora():%Y-%m-%d %H:%M:%S} {msg}\n")
    print(msg)


def avisar_guilherme(texto):
    try:
        avisar.enviar(texto)
        return True
    except (SystemExit, Exception) as e:  # noqa: BLE001
        log(f"Telegram falhou: {e!r}")
        return False


def nome_secao(l):
    return l[3:].split("(")[0].strip()


def secao(linhas, titulo):
    ini = next(i for i, l in enumerate(linhas) if l.startswith("## ") and nome_secao(l) == titulo) + 1
    fim = next((i for i in range(ini, len(linhas)) if linhas[i].startswith("## ")), len(linhas))
    return ini, fim


def id_da_linha(l):
    m = CARTAO.match(l)
    return m.group(1) if m else None


def ler_cartoes(linhas):
    cartoes = []
    for col in DONOS:
        try:
            ini, fim = secao(linhas, col)
        except StopIteration:
            continue
        for i in range(ini, fim):
            if id_da_linha(linhas[i]):
                cartoes.append({"id": id_da_linha(linhas[i]), "coluna": col, "linha": linhas[i]})
    return cartoes


def dev_do_item(linha, id_):
    m = re.search(r"\*\*(Rodrygo|Endrick)\*\*", linha)
    if m:
        return m.group(1)
    try:
        bloco = re.search(rf"## {id_} ·.*?(?=\n## PROG-|\Z)", BACKLOG.read_text(encoding="utf-8"), re.S).group(0)
        dono = re.search(r"\*\*Dono:\*\*\s*(\w+)", bloco)
        if dono and dono.group(1) in DEVS:
            return dono.group(1)
        if re.search(r"tela|interface|aba |front|botão", bloco, re.I):
            return "Endrick"
    except (AttributeError, OSError):
        pass
    return "Rodrygo"


def agente_do_cartao(c):
    return DEVS[dev_do_item(c["linha"], c["id"])] if c["coluna"] == "Fazendo" else DONOS[c["coluna"]]


def contar_wip_cartoes(cartoes):
    wip = Counter(dev_do_item(c["linha"], c["id"]) for c in cartoes if c["coluna"] == "Fazendo")
    return {d: wip[d] for d in DEVS}


def assinatura(c, wip):
    partes = [c["coluna"], MARCA.sub("", c["linha"])]
    for pasta in ("qa", "entregas", "revisoes", "maestro/respostas"):
        p = PROG / pasta / f"{c['id']}.md"
        partes.append(str(p.stat().st_mtime_ns) if p.exists() else "-")
    partes.append((ACEITES / f"{c['id']}.md").exists().__str__())
    if c["coluna"] == "Backlog da sprint":
        partes.append(json.dumps(wip, sort_keys=True))
    return hashlib.sha1("|".join(partes).encode("utf-8")).hexdigest()


def sprint_aberta(texto):
    return bool(re.search(r"Sprint \d+, ABERTA", texto))


def estado_ler():
    e = avisar.ler_json(ESTADO, {})
    for k in ("cartoes", "custo", "avisos"):
        e.setdefault(k, {})
    return e


def estado_salvar(e):
    MAESTRO.mkdir(parents=True, exist_ok=True)
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, ESTADO)


def pid_vivo(pid):
    try:
        return str(pid) in subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
    except Exception:  # noqa: BLE001
        return False


def pegar_lock():
    MAESTRO.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        d = avisar.ler_json(LOCK, {})
        if time.time() - d.get("t", 0) < 4 * 3600 and pid_vivo(d.get("pid")):
            return False
    LOCK.write_text(json.dumps({"pid": os.getpid(), "t": time.time()}), encoding="utf-8")
    return True


def devido(c, est, forcar, wip):
    if c["id"] in forcar:
        return True
    r = est["cartoes"].get(c["id"])
    if c["coluna"] == "Feito":
        return NOTAS_RELEASE.exists() and c["id"] not in NOTAS_RELEASE.read_text(encoding="utf-8") and (not r or r.get("mantidos", 0) < MAX_MANTIDOS)
    if not r or r.get("assinatura") != assinatura(c, wip):
        return True
    if r.get("espera_humano") or r.get("mantidos", 0) >= MAX_MANTIDOS:
        return False
    return agora() - datetime.fromisoformat(r["ultima"]) >= REENVIO


def montar_grupos(cartoes, est, forcar):
    wip = contar_wip_cartoes(cartoes)
    grupos = []
    for col in DONOS:
        doscol = [c for c in cartoes if c["coluna"] == col]
        if col == "Backlog da sprint":
            if not (doscol and any(wip[d] < 2 for d in DEVS)):
                continue
            doscol = doscol[:1]
        due = [c for c in doscol if devido(c, est, forcar, wip)]
        if not due:
            continue
        if col == "Fazendo":
            grupos += [(*agente_do_cartao(c), col, [c]) for c in due]
        else:
            ag, nome = DONOS[col]
            grupos += [(ag, nome, col, due[i:i + 3]) for i in range(0, len(due), 3)]
    return grupos, wip


def contexto_git():
    pastas = ["estudio", "produtividade", "programacao", "tools", "media"]
    s = subprocess.run(["git", "status", "--short", "--", *pastas], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    return s.stdout[:2500]


def montar_pedido(nome, col, cards, wip):
    saidas = sorted(SAIDAS[col]) or ["(nenhuma)"]
    ids = [c["id"] for c in cards]
    linhas_cards = "\n".join(f"- {c['linha']}" for c in cards)
    extra = ""
    if col == "Fazendo":
        extra = ("\nNesta coluna você implementa: teste primeiro, código, bateria rodada e `programacao/entregas/<ID>.md` com resultados REAIS. "
                 "Só mova para Em teste quando tudo estiver verde e a entrega gravada; se ainda falta, grave 'manter' com o que já foi feito e o que falta.\n")
    if col == "Pronto para aceite" and ACEITE_DO_GUILHERME:
        extra = ("\nO aceite final é do Guilherme. Confira os critérios do item contra qa/ e revisoes/. Se TODOS têm evidência, grave 'manter' com "
                 "precisa_do_guilherme true e pedido_ao_guilherme 'Aceitar <ID>? Se sim, diga \"aceito <ID>\" ao Claude'. Se algum critério não tem evidência, "
                 "mova para Fazendo dizendo exatamente o que falta.\n")
    return f"""Você é {nome} e foi chamado pelo maestro da Sprint 01 porque é o dono da coluna "{col}" do quadro de programação (programacao/quadro.md, espelhado no Trello, que o Guilherme acompanha pelo celular).

Cartões que dependem de você agora ({', '.join(ids)}):
{linhas_cards}

WIP em Fazendo: Rodrygo {wip['Rodrygo']}/2, Endrick {wip['Endrick']}/2.
Saídas permitidas desta coluna: {', '.join(saidas)}{'; qualquer cartão pode ir também para Bloqueado se faltar algo que só outra pessoa resolve' if col not in ('Feito', 'Bloqueado') else ''}.
{extra}
Trabalhe DE VERDADE: faça o que o seu papel exige para cada cartão agora (código com teste, validação, revisão, aceite ou registro de release), com evidência real (comandos rodados e resultados), seguindo o CLAUDE.md e a sua definição de agente. Leia programacao/backlog.md (critérios do item), entregas/, qa/ e revisoes/ do cartão.

Depois, para CADA cartão, grave `programacao/maestro/decisoes/<ID>.json` (ex.: programacao/maestro/decisoes/PROG-005.json) com exatamente:
{{"id": "PROG-005", "acao": "mover" ou "manter", "para": "<coluna de saída, só se mover>", "status": "o que está acontecendo agora, 1 ou 2 frases simples", "motivo": "por que o cartão está nesta coluna / por que vai para a próxima, 1 ou 2 frases", "criterios_ok": [números dos critérios do backlog.md que você COMPROVOU; só Alisson, Thiago Silva e Zico preenchem], "precisa_do_guilherme": false, "pedido_ao_guilherme": "o que ele precisa fazer, só se precisar"}}

Regras:
- O Guilherme lê "status" e "motivo" no Trello: escreva claro, sem jargão, dizendo o que foi feito e o que falta.
- "mover" só se a condição de saída é verdadeira e comprovada. Na dúvida, "manter" e diga o que falta. Nunca declare pronto sem teste rodado ou relatório gravado.
- Não mova cartão e não edite programacao/quadro.md: o maestro aplica a sua decisão. Não commite, não publique, não gaste dinheiro, não leia nem mostre o .env.
- Rode uma bateria e2e por vez (E2E_PORTA se precisar de porta própria).
- Se depende do Guilherme, use precisa_do_guilherme true e diga exatamente o que ele precisa fazer.
- Termine com um resumo de uma linha por cartão.

Mudanças não commitadas no repositório (para você achar os arquivos):
{contexto_git()}
"""


def chamar_agente(ag_id, pedido):
    """Devolve (custo_usd, texto, erro, quota)."""
    teto, minutos = PERFIL.get(ag_id, ("2.00", 30))
    env = dict(os.environ)
    for linha in (RAIZ / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.lstrip().startswith("#"):
            env.pop(linha.split("=", 1)[0].strip(), None)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    ferr = ["Read", "Write", "Edit", "Glob", "Grep"] + FERRAMENTAS.get(ag_id, [])
    model = os.environ.get("MAESTRO_MODEL", "haiku")
    cmd = [shutil.which("claude") or "claude", "-p", "--agent", ag_id, "--model", model, "--setting-sources", "user,project",
           "--permission-mode", "bypassPermissions", "--allowedTools", ",".join(ferr), "--disallowedTools", ",".join(PROIBIDO),
           "--name", f"maestro-{ag_id}", "--max-budget-usd", teto, "--output-format", "json"]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                         cwd=RAIZ, env=env, creationflags=NO_WINDOW)
    try:
        out, err = p.communicate(pedido, timeout=minutos * 60)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        p.communicate()
        return 0.0, f"passou de {minutos} minutos e foi interrompido", True, False
    try:
        d = json.loads(out)
    except ValueError:
        return 0.0, f"claude saiu com código {p.returncode}: {(err or out)[:200]}", True, False
    texto = (d.get("result") or "").strip()
    erro = bool(d.get("is_error")) or p.returncode != 0
    quota = erro and bool(re.search(r"limit|quota|usage|rate", texto, re.I))
    return float(d.get("total_cost_usd") or 0), texto, erro, quota


def ler_decisao(id_):
    arq = DECISOES / f"{id_}.json"
    if not arq.exists():
        return None
    try:
        d = json.loads(arq.read_text(encoding="utf-8"))
    except ValueError:
        return None
    if not (isinstance(d, dict) and d.get("id") == id_ and d.get("acao") in ("mover", "manter")):
        return None
    if d["acao"] == "mover" and not isinstance(d.get("para"), str):
        return None
    if not isinstance(d.get("criterios_ok") or [], list):
        d["criterios_ok"] = []
    return d


def mover_linha(linhas, id_, origem, destino, nova_linha):
    ini, fim = secao(linhas, origem)
    i = next(k for k in range(ini, fim) if id_da_linha(linhas[k]) == id_)
    linhas.pop(i)
    ini, fim = secao(linhas, destino)
    linhas[ini:fim] = [l for l in linhas[ini:fim] if not l.startswith("(vazio")]
    ini, fim = secao(linhas, destino)
    ultimo = max([k for k in range(ini, fim) if id_da_linha(linhas[k])] or [ini - 1]) + 1
    linhas.insert(ultimo, nova_linha)
    ini, fim = secao(linhas, origem)
    if not any(id_da_linha(l) for l in linhas[ini:fim]) and not any(l.startswith("(vazio") for l in linhas[ini:fim]):
        linhas.insert(ini, "(vazio)")


def aplicar(linhas, c, d, nome, r):
    """Aplica a decisão no quadro (em memória). Devolve (coluna_final, mudou, motivo_recusa)."""
    id_, col = c["id"], c["coluna"]
    atual = next(l for l in linhas if id_da_linha(l) == id_)
    base = MARCA.sub("", atual)
    status = " ".join(str(d.get("status", "")).split())[:220]
    marca = f" · Maestro: {status} ({nome}, {agora_txt()})"
    destino = d.get("para") if d["acao"] == "mover" else None
    if destino == col:
        destino = None
    if destino:
        pode_bloquear = destino == "Bloqueado" and col not in ("Bloqueado", "Feito")
        if not pode_bloquear and destino not in SAIDAS[col]:
            return col, False, f"saída {destino!r} não é permitida a partir de {col!r}"
        if col == "Backlog da sprint" and destino == "Fazendo":
            wip = contar_wip_cartoes(ler_cartoes(linhas))
            if wip[dev_do_item(atual, id_)] >= 2:
                return col, False, "o dev dono já tem 2 itens em Fazendo"
        if destino == "Fazendo" and col in DEVOLUCAO_DE:
            r["devolucoes"] = r.get("devolucoes", 0) + 1
            if r["devolucoes"] > MAX_DEVOLUCOES:
                destino = "Bloqueado"
                d["status"] = f"Devolvido {r['devolucoes']} vezes sem fechar. {d.get('status', '')}"
                d["precisa_do_guilherme"] = True
                d["pedido_ao_guilherme"] = "Este item voltou várias vezes; decida se muda o escopo ou quem faz."
                marca = f" · Maestro: {' '.join(d['status'].split())[:220]} ({nome}, {agora_txt()})"
        nova = re.sub(r"^\d+\. ", "- ", base) + marca
        mover_linha(linhas, id_, col, destino, nova)
        return destino, True, None
    linhas[linhas.index(atual)] = base + marca
    return col, False, None


def atualizar_contagem(linhas):
    wip = contar_wip_cartoes(ler_cartoes(linhas))
    for i, l in enumerate(linhas):
        if l.startswith("Contagem por dev:"):
            linhas[i] = f"Contagem por dev: **Rodrygo** {wip['Rodrygo']}/2; **Endrick** {wip['Endrick']}/2."


def gravar_quadro(linhas):
    shutil.copyfile(QUADRO, BACKUP)
    tmp = QUADRO.with_suffix(".tmp")
    tmp.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    os.replace(tmp, QUADRO)


def trello(*a, **k):
    try:
        return ts.api(*a, **k)
    except (SystemExit, Exception) as e:  # noqa: BLE001
        log(f"Trello falhou ({a[:2]}): {e}")
        return None


def empurrar_trello(est, ids, movimentos, marcados):
    estado = avisar.ler_json(ts.ESTADO, {})
    board = estado.get("board")
    if not board:
        return
    cards = trello("GET", f"boards/{board}/cards", filter="open", fields="name,desc")
    if cards is None:
        return
    por_id = {kp.id_do_titulo(c["name"]): c for c in cards}
    cartoes = {c["id"]: c for c in ler_cartoes(QUADRO.read_text(encoding="utf-8").splitlines())}
    for id_ in ids:
        c, r, card = cartoes.get(id_), est["cartoes"].get(id_), por_id.get(id_)
        if not (c and r and card):
            continue
        texto = (f"**Coluna:** {c['coluna']} · **Responsável:** {r['agente']}\n"
                 f"**Status:** {r.get('status') or '(sem informação)'}\n"
                 f"**Por que está aqui:** {r.get('motivo') or '(sem informação)'}\n")
        if r.get("espera_humano"):
            texto += f"**Precisa de você:** {r.get('pedido') or 'ver o motivo acima'}\n"
        texto += f"_Atualizado em {r['quando']} pelo maestro da sprint._"
        desc = card.get("desc", "")
        novo = f"## Status atual (maestro)\n{texto}\n\n{BLOCO_TRELLO.sub('', desc, count=1).lstrip()}"
        if novo != desc:
            trello("PUT", f"cards/{card['id']}", desc=novo)
        if r.get("decidido") and r.get("status") and r.get("status") != r.get("publicado"):
            trello("POST", f"cards/{card['id']}/actions/comments", text=f"{r['agente']} ({r['quando']}): {r['status']}")
            r["publicado"] = r["status"]
    for id_, de, para, nome, motivo in movimentos:
        card = por_id.get(id_)
        if card:
            trello("POST", f"cards/{card['id']}/actions/comments", text=f"Movido de {de} para {para} por {nome} em {agora_txt()}. Motivo: {motivo}")
    for id_, numeros in marcados.items():
        card = por_id.get(id_)
        if not card:
            continue
        cks = trello("GET", f"cards/{card['id']}/checklists") or []
        ck = next((k for k in cks if k["name"].lower().startswith("crit")), cks[0] if cks else None)
        if not ck:
            continue
        itens = sorted(ck["checkItems"], key=lambda i: i["pos"])
        for n in numeros:
            if 1 <= n <= len(itens) and itens[n - 1]["state"] != "complete":
                trello("PUT", f"cards/{card['id']}/checkItem/{itens[n - 1]['id']}", state="complete")
    estado_salvar(est)


def registrar(linhas, c, d, nome, est, acc, hoje):
    """Aplica uma decisão e atualiza estado/acumuladores. Levanta exceção se algo vier malformado."""
    r = est["cartoes"].get(c["id"], {})
    if nome == "Guilherme":
        proprio = "Guilherme"
    else:
        proprio = nome
    destino, mudou, recusa = aplicar(linhas, c, d, proprio, r)
    if recusa:
        log(f"{c['id']}: decisão recusada ({recusa})")
        d = dict(d, acao="manter", status=f"{d.get('status', '')} (o maestro recusou a movimentação: {recusa})")
        destino, mudou, _ = aplicar(linhas, c, d, proprio, r)
    nova_linha = next(l for l in linhas if id_da_linha(l) == c["id"])
    novo_resp = proprio
    if mudou:
        acc["movimentos"].append((c["id"], c["coluna"], destino, proprio, d.get("motivo", "")))
        acc["resumo"].append(f"{c['id']}: {c['coluna']} → {destino} ({proprio}). {d.get('motivo', '')[:120]}")
        novo_resp = (DEVS[dev_do_item(nova_linha, c["id"])] if destino == "Fazendo" else DONOS[destino])[1]
    if proprio in PODE_MARCAR_CRITERIOS:
        num = [n for n in d.get("criterios_ok") or [] if isinstance(n, int)]
        if num:
            acc["marcados"][c["id"]] = num
    pedido = bool(d.get("precisa_do_guilherme"))
    r.update(agente=novo_resp, quando=agora_txt(), ultima=agora().isoformat(timespec="seconds"), status=d.get("status", ""),
             motivo=d.get("motivo", ""), espera_humano=pedido, pedido=d.get("pedido_ao_guilherme", ""), decidido=True,
             mantidos=0 if mudou else (r.get("mantidos", 0) + (0 if c["coluna"] == "Backlog da sprint" else 1)))
    r["assinatura"] = "" if mudou else None
    est["cartoes"][c["id"]] = r
    if pedido and est["avisos"].get(c["id"]) != hoje:
        acc["pedidos"].append((c["id"], d.get("pedido_ao_guilherme") or d.get("motivo", "")))


def rodada(simular, forcar):
    avisar.carregar_env()
    texto = QUADRO.read_text(encoding="utf-8")
    if not forcar and not sprint_aberta(texto):
        print("sprint não está ABERTA: nada a fazer")
        return
    if not forcar and not (JANELA[0] <= agora().hour < JANELA[1]):
        print("fora da janela de trabalho")
        return
    est = estado_ler()
    hoje = f"{agora():%Y-%m-%d}"
    if est.get("pausa_ate") and datetime.fromisoformat(est["pausa_ate"]) > agora():
        print(f"maestro em pausa até {est['pausa_ate']} (limite de uso do Claude)")
        return
    if est["custo"].get(hoje, 0) >= LIMITE_DIA_USD:
        if est["avisos"].get("custo") != hoje and not simular and avisar_guilherme(
                f"Maestro da sprint parou: gastou US$ {est['custo'][hoje]:.2f} hoje (limite US$ {LIMITE_DIA_USD:.0f})."):
            est["avisos"]["custo"] = hoje
            estado_salvar(est)
        return

    linhas = texto.splitlines()
    cartoes = ler_cartoes(linhas)
    aceitos = [c for c in cartoes if c["coluna"] == "Pronto para aceite" and (ACEITES / f"{c['id']}.md").exists()]
    grupos, wip = montar_grupos([c for c in cartoes if c not in aceitos], est, set(forcar))
    if simular:
        for c in aceitos:
            print(f"moveria {c['id']} para Feito (aceite do Guilherme registrado)")
        for ag, nome, col, cards in grupos[:MAX_GRUPOS_POR_RODADA]:
            print(f"chamaria {nome} ({ag}) para {[c['id'] for c in cards]} em {col}")
        print(f"(grupos devidos: {len(grupos)}; WIP {wip})")
        return
    if not pegar_lock():
        print("já há uma rodada em andamento")
        return

    acc = {"movimentos": [], "marcados": {}, "resumo": [], "pedidos": []}
    try:
        if aceitos:
            linhas = QUADRO.read_text(encoding="utf-8").splitlines()
            for c in aceitos:
                d = {"id": c["id"], "acao": "mover", "para": "Feito", "status": "Aceito pelo Guilherme.",
                     "motivo": f"Aceite do Guilherme registrado em programacao/aceites/{c['id']}.md."}
                copia = list(linhas)
                try:
                    registrar(linhas, c, d, "Guilherme", est, acc, hoje)
                except Exception as e:  # noqa: BLE001
                    linhas[:] = copia
                    log(f"{c['id']}: falha ao registrar o aceite: {e!r}")
            atualizar_contagem(linhas)
            gravar_quadro(linhas)
            estado_salvar(est)
            if acc["movimentos"]:
                subprocess.run([sys.executable, str(RAIZ / "produtividade" / "trello_sync.py")], cwd=RAIZ, capture_output=True, creationflags=NO_WINDOW)
            empurrar_trello(est, [m[0] for m in acc["movimentos"]], acc["movimentos"], {})
            acc["movimentos"] = []
        for ag, nome, col, cards in grupos[:MAX_GRUPOS_POR_RODADA]:
            if est["custo"].get(hoje, 0) >= LIMITE_DIA_USD:
                break
            DECISOES.mkdir(parents=True, exist_ok=True)
            for c in cards:
                (DECISOES / f"{c['id']}.json").unlink(missing_ok=True)
            log(f"chamando {nome} para {[c['id'] for c in cards]} em {col}")
            custo, saida, erro, quota = chamar_agente(ag, montar_pedido(nome, col, cards, wip))
            est["custo"][hoje] = est["custo"].get(hoje, 0) + custo
            log(f"{nome} terminou (US$ {custo:.2f}, erro={erro}): {saida[:300]!r}")
            if erro:
                if quota:
                    est["pausa_ate"] = (agora() + timedelta(hours=1)).isoformat(timespec="seconds")
                    avisar_guilherme("Maestro da sprint em pausa por 1 hora: o Claude chegou ao limite de uso.")
                for c in cards:
                    r = est["cartoes"].get(c["id"], {})
                    r.update(agente=nome, quando=agora_txt(), ultima=agora().isoformat(timespec="seconds"), decidido=False,
                             status="O responsável não conseguiu rodar nesta rodada.", motivo=saida[:160],
                             espera_humano=False, pedido="")
                    est["cartoes"][c["id"]] = r
                estado_salvar(est)
                if quota:
                    break
                continue
            linhas = QUADRO.read_text(encoding="utf-8").splitlines()
            ids_antes = {c["id"] for c in ler_cartoes(linhas)}
            acc_grupo = {"movimentos": [], "marcados": {}, "resumo": [], "pedidos": []}
            for c in cards:
                atual = next((x for x in ler_cartoes(linhas) if x["id"] == c["id"]), None)
                if atual is None:
                    continue
                copia = list(linhas)
                d = ler_decisao(c["id"])
                try:
                    if d is None:
                        r = est["cartoes"].get(c["id"], {})
                        r.update(mantidos=r.get("mantidos", 0) + 1, agente=nome, quando=agora_txt(), decidido=False,
                                 ultima=agora().isoformat(timespec="seconds"), espera_humano=False, pedido="",
                                 status="O responsável foi chamado mas não registrou decisão.",
                                 motivo=f"{nome} não gravou a decisão desta rodada; o maestro tenta de novo.")
                        est["cartoes"][c["id"]] = r
                    else:
                        registrar(linhas, atual, d, nome, est, acc_grupo, hoje)
                except Exception as e:  # noqa: BLE001
                    linhas[:] = copia
                    log(f"{c['id']}: decisão com problema ({e!r}); mantido onde está")
                    r = est["cartoes"].get(c["id"], {})
                    r.update(mantidos=r.get("mantidos", 0) + 1, ultima=agora().isoformat(timespec="seconds"), agente=nome, quando=agora_txt(),
                             status="A decisão do responsável veio malformada.", motivo=str(e)[:160], decidido=False)
                    est["cartoes"][c["id"]] = r
            atualizar_contagem(linhas)
            if {c["id"] for c in ler_cartoes(linhas)} != ids_antes:
                log("o quadro perderia cartões; mantido como estava")
            else:
                gravar_quadro(linhas)
            wip_depois = contar_wip_cartoes(ler_cartoes(linhas))
            for c in ler_cartoes(linhas):
                r = est["cartoes"].get(c["id"])
                if r and r.get("assinatura") is None and any(x["id"] == c["id"] for x in cards):
                    r["assinatura"] = assinatura(c, wip_depois)
            estado_salvar(est)
            if acc_grupo["movimentos"]:
                subprocess.run([sys.executable, str(RAIZ / "produtividade" / "trello_sync.py")], cwd=RAIZ, capture_output=True, creationflags=NO_WINDOW)
            empurrar_trello(est, [c["id"] for c in cards], acc_grupo["movimentos"], acc_grupo["marcados"])
            for k in ("movimentos", "resumo", "pedidos"):
                acc[k] += acc_grupo[k]
            acc["marcados"].update(acc_grupo["marcados"])
    finally:
        for r in est["cartoes"].values():
            if r.get("assinatura") is None:
                r["assinatura"] = ""
        LOCK.unlink(missing_ok=True)
        estado_salvar(est)

    depois = ler_cartoes(QUADRO.read_text(encoding="utf-8").splitlines())
    novos = []
    for c in depois:  # cartão sem registro ainda ganha status automático (o Trello nunca fica mudo)
        if c["id"] not in est["cartoes"] and c["coluna"] != "Feito":
            fila = c["coluna"] == "Backlog da sprint"
            est["cartoes"][c["id"]] = {
                "agente": agente_do_cartao(c)[1], "quando": agora_txt(), "assinatura": "", "mantidos": 0, "espera_humano": False,
                "pedido": "", "decidido": False, "ultima": agora().isoformat(timespec="seconds"),
                "status": "Na fila da sprint, ainda não começou." if fila else "Aguardando a primeira chamada do responsável.",
                "motivo": ("Entra quando abrir vaga: cada dev trabalha em no máximo 2 itens por vez." if fila
                           else f"Está na coluna {c['coluna']}; o responsável é chamado a cada 15 minutos.")}
            novos.append(c["id"])
    if novos:
        estado_salvar(est)
        empurrar_trello(est, novos, [], {})
    if acc["resumo"] and avisar_guilherme("Sprint andou: " + str(len(acc["resumo"])) + " cartão(ões) mudaram de coluna.\n\n" + "\n".join(acc["resumo"])):
        pass
    if acc["pedidos"] and avisar_guilherme("Preciso de você na sprint:\n\n" + "\n".join(f"{i}: {t}" for i, t in acc["pedidos"])):
        for i, _ in acc["pedidos"]:
            est["avisos"][i] = hoje
        estado_salvar(est)


if __name__ == "__main__":
    args = sys.argv[1:]
    forc = [a for a in args[args.index("--forcar") + 1:] if a.startswith("PROG-")] if "--forcar" in args else []
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    rodada("--simular" in args, forc)
