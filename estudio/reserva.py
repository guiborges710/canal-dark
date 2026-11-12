"""Reserva com Codex: quando o Claude esgota (limite de 5 horas, semanal ou de uso), o MESMO trabalho de agente roda pelo Codex.

Regras (decisão do dono, 2026-11-03):
- Só entra se a falha do Claude for, de fato, o limite de uso (`e_limite_do_claude`). Erro comum, timeout, ferramenta ou conteúdo NÃO acionam.
- No máximo uma tentativa pelo Codex por trabalho; o Codex falhando não volta ao Claude. Trabalho novo sempre tenta o Claude primeiro.
- Mesmo agente (instruções vêm de .claude/agents/<id>.md, a fonte de verdade), mesmo pedido, mesma pasta; escreve só dentro da pasta de trabalho, sem rede de shell.
"""
import glob
import json
import os
import re
import shutil
from pathlib import Path

from .config import RAIZ, REPO

# Bem restritos de propósito: cada padrão descreve a mensagem de limite de uso do Claude Code, nunca um erro qualquer.
_LIMITE = [re.compile(p, re.I) for p in (
    r"you['’]?ve (hit|reached) your (\w+[- ]){0,3}limit",
    r"\b(5[- ]hour|five[- ]hour|weekly|session|usage|opus|sonnet|daily|monthly) limit (reached|hit|exceeded|will reset|resets?)",
    r"\busage limit (reached|exceeded|hit)",
    r"\blimit reached\b.{0,60}\bresets?\b",
    r"\bclaude (ai |max |pro )?usage limit\b",
    r"\byour limit will reset\b",
)]


def e_limite_do_claude(texto):
    """True só para a mensagem de limite de uso do plano do Claude (5 horas, semanal ou de uso)."""
    if not texto:
        return False
    t = str(texto)[:4000]
    return any(p.search(t) for p in _LIMITE)


def _de_dotenv(chave):
    arq = REPO / ".env"
    if arq.exists():
        for linha in arq.read_text(encoding="utf-8-sig").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#") and linha.split("=", 1)[0].strip() == chave:
                return linha.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def achar_codex():
    """Caminho do codex.exe: ESTUDIO_CODEX / CODEX (ambiente ou .env), PATH, depois a extensão do VS Code (openai.chatgpt-*)."""
    for v in (os.environ.get("ESTUDIO_CODEX"), os.environ.get("CODEX"), _de_dotenv("CODEX")):
        if v and Path(v).exists():
            return str(v)
    achou = shutil.which("codex")
    if achou:
        return achou
    home = Path(os.environ.get("USERPROFILE") or Path.home())
    candidatos = sorted(glob.glob(str(home / ".vscode" / "extensions" / "openai.chatgpt-*" / "bin" / "*" / "codex.exe")), reverse=True)
    candidatos += [str(Path(os.environ["APPDATA"]) / "npm" / "codex.cmd")] if os.environ.get("APPDATA") else []
    return next((c for c in candidatos if Path(c).exists()), None)


def logado():
    home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return (home / "auth.json").exists()


def instrucoes_do_agente(spec):
    """Corpo do agente (sem o cabeçalho). Agente preso a versão usa a foto guardada; senão, o .md atual."""
    if spec.get("sistema") and spec["sistema"].get("corpo"):
        return _sem_cabecalho(spec["sistema"]["corpo"])
    for base in (RAIZ, REPO):
        arq = base / ".claude" / "agents" / f"{spec['agente']}.md"
        if arq.exists():
            return _sem_cabecalho(arq.read_text(encoding="utf-8-sig"))
    raise FileNotFoundError(f"agente {spec['agente']} não encontrado em .claude/agents")


def _sem_cabecalho(texto):
    texto = texto.replace("\r\n", "\n")
    m = re.match(r"---\n.*?\n---\n", texto, re.S)
    return (texto[m.end():] if m else texto).strip()


def _quer_web(spec):
    ferramentas = (spec.get("sistema") or {}).get("ferramentas") or spec.get("ferramentas_aprovadas") or ""
    if isinstance(ferramentas, list):
        ferramentas = ",".join(ferramentas)
    if ferramentas:
        return "WebSearch" in ferramentas or "WebFetch" in ferramentas
    arq = RAIZ / ".claude" / "agents" / f"{spec.get('agente')}.md"
    if arq.exists():
        m = re.search(r"^tools:(.*)$", arq.read_text(encoding="utf-8-sig"), re.M)
        return bool(m and re.search(r"WebSearch|WebFetch", m.group(1)))
    return False


def montar_prompt(spec):
    """Tudo vai pelo stdin (sem limite de linha de comando do Windows): instruções do agente e depois o pedido."""
    return ("Você está rodando no Codex, como RESERVA do Claude Code (o limite de uso do Claude acabou). Assuma o papel do agente abaixo, exatamente como ele faria.\n"
            "- As regras do projeto estão em CLAUDE.md na raiz (ignore AGENTS.md, que pode estar defasado). Onde o texto citar ferramentas do Claude (Read, Write, Edit, Glob, Grep, Bash), use as equivalentes do Codex.\n"
            "- Não há subagentes: faça você mesmo o que o agente faria. Escreva só dentro da pasta de trabalho atual.\n\n"
            f"<instrucoes_do_agente nome=\"{spec.get('agente')}\">\n{instrucoes_do_agente(spec)}\n</instrucoes_do_agente>\n\n"
            f"<pedido>\n{spec['prompt']}\n</pedido>\n")


def montar_comando(spec, exe, cwd, arquivo_final):
    """`codex exec` não interativo. Sandbox workspace-write (escreve em `cwd`, sem rede de shell), sem aprovação, sem sessão salva, sem o config/hooks pessoais."""
    cmd = [exe, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules",
           "-s", "workspace-write", "-C", str(cwd), "-o", str(arquivo_final),
           "-c", 'windows.sandbox="elevated"', "-c", "sandbox_workspace_write.network_access=false",
           "-c", 'approval_policy="never"']
    if _quer_web(spec):  # só quem já tinha WebSearch/WebFetch no Claude
        cmd += ["-c", 'web_search="live"']
    modelo = os.environ.get("ESTUDIO_CODEX_MODELO") or _de_dotenv("CODEX_MODELO")
    if modelo:
        cmd += ["-m", modelo]
    return cmd + ["-"]


def linha_codex(linha):
    """Uma linha do `--json` do Codex vira texto de log. Devolve (texto, mensagem_final_ou_None). Tolerante a mudanças de formato."""
    try:
        ev = json.loads(linha)
    except ValueError:
        return linha.rstrip(), None
    if not isinstance(ev, dict):
        return None, None
    item = ev.get("item") if isinstance(ev.get("item"), dict) else (ev.get("msg") if isinstance(ev.get("msg"), dict) else ev)
    tipo = item.get("type")
    if tipo in ("agent_message", "assistant_message") and (item.get("text") or item.get("message")):
        texto = str(item.get("text") or item.get("message")).strip()
        return texto[:300], texto
    if tipo == "command_execution" and item.get("command") and ev.get("type") != "item.completed":
        return f"▸ {str(item['command'])[:140]}", None
    if tipo == "error" or ev.get("type") in ("error", "turn.failed"):
        return f"erro do Codex: {str(item.get('message') or ev.get('error') or '')[:300]}", None
    return None, None
