"""Roda um trabalho num processo próprio, destacado do servidor: fechar ou reiniciar o estúdio não derruba uma narração no meio.

Uso (só o estúdio chama):  python -m estudio.executor <pasta do job>
Na pasta: spec.json (entrada), log.txt (saída ao vivo), batimento (prova de vida), resultado.json (fim).
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from . import reserva
from .config import BATIMENTO_S, CLAUDE, PY, RAIZ, REPO, SIMULADOR, TEMPO_AGENTE_S, TEMPO_PESADO_S

# Mesma lista de permissões do De Bruyne no Telegram (produtividade/ronaldo_telegram.py).
FERRAMENTAS = "Agent,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Bash(python run.py *),Bash(python -m media.sketch *),Bash(ls *),Bash(dir *)"
CHAVES_ENV = REPO / ".env"


def ambiente_agente():
    """Nenhuma chave do .env vai para o agente: o `claude -p` usa o login, e nunca a ANTHROPIC_API_KEY paga."""
    env = dict(os.environ)
    if CHAVES_ENV.exists():
        for linha in CHAVES_ENV.read_text(encoding="utf-8-sig").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                env.pop(linha.split("=", 1)[0].strip(), None)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    return env


def comando_agente(spec, pasta=None):
    if spec.get("sistema"):
        # Agente preso a uma versão (execução de grafo ou teste): usa a foto guardada, não o arquivo de agora.
        s = spec["sistema"]
        arq = Path(pasta) / "agente_sistema.md"
        arq.write_text(s["corpo"], encoding="utf-8")
        cmd = [CLAUDE or "claude", "-p", "--system-prompt-file", str(arq), "--permission-mode", "acceptEdits", "--allowedTools", spec.get("ferramentas_aprovadas") or FERRAMENTAS,
               "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", spec.get("orcamento", "3.00"), "--output-format", "stream-json", "--verbose"]
        if s.get("ferramentas"):
            cmd += ["--tools", ",".join(re.sub(r"\(.*\)$", "", f) for f in s["ferramentas"])]
        if s.get("modelo"):
            cmd += ["--model", s["modelo"]]
        return cmd
    return [CLAUDE or "claude", "-p", "--agent", spec["agente"], "--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS,
            "--strict-mcp-config", "--no-session-persistence", "--max-budget-usd", spec.get("orcamento", "3.00"),
            "--output-format", "stream-json", "--verbose"]


def linha_legivel(linha):
    """Transforma o stream-json do Claude em uma linha para o log. Devolve (texto, evento final ou None)."""
    try:
        ev = json.loads(linha)
    except ValueError:
        return linha.rstrip(), None
    tipo = ev.get("type")
    if tipo == "result":
        return None, ev
    if tipo == "assistant":
        partes = []
        for bloco in ev.get("message", {}).get("content", []):
            if bloco.get("type") == "tool_use":
                entrada = bloco.get("input", {})
                alvo = entrada.get("file_path") or entrada.get("command") or entrada.get("pattern") or entrada.get("query") or entrada.get("description") or ""
                partes.append(f"▸ {bloco.get('name')} {str(alvo)[:140]}")
            elif bloco.get("type") == "text" and bloco.get("text", "").strip():
                partes.append(bloco["text"].strip()[:300])
        return "\n".join(partes) or None, None
    return None, None


def rodar(pasta):
    pasta = Path(pasta)
    spec = json.loads((pasta / "spec.json").read_text(encoding="utf-8"))
    log = (pasta / "log.txt").open("a", encoding="utf-8", buffering=1)
    fim = threading.Event()

    def bater():
        while not fim.is_set():
            (pasta / "batimento").write_text(str(time.time()), encoding="ascii")
            fim.wait(BATIMENTO_S)

    threading.Thread(target=bater, daemon=True).start()
    resultado = {"erro": None, "resumo": None, "custo_usd": None}
    agente = spec["tipo"] == "agente"
    if agente:
        (pasta / "motor.txt").write_text("claude", encoding="ascii")
    try:
        if agente:
            cmd, env, entrada, limite = comando_agente(spec, pasta), ambiente_agente(), spec["prompt"], TEMPO_AGENTE_S
            env["ESTUDIO_AGENTE"] = spec["agente"]
        else:
            cmd = [PY] + ([SIMULADOR] if SIMULADOR and not spec.get("real") else []) + spec["comando"]
            env, entrada, limite = dict(os.environ), None, TEMPO_PESADO_S
        env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        log.write(f"$ {' '.join(cmd[:6])}{' …' if len(cmd) > 6 else ''}\n")
        if spec.get("sistema"):
            log.write(f"agente {spec.get('agente')} v{spec['sistema'].get('versao')} ({str(spec['sistema'].get('sha'))[:10]})\n")
        proc = subprocess.Popen(cmd, cwd=spec.get("cwd") or str(RAIZ if agente or (SIMULADOR and not spec.get("real")) else REPO), env=env, stdin=subprocess.PIPE if entrada else subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace",
                                creationflags=0x08000000)  # CREATE_NO_WINDOW: sem janela piscando a cada agente
        if entrada:
            proc.stdin.write(entrada)
            proc.stdin.close()
        relogio = threading.Timer(limite, proc.kill)
        relogio.start()
        final, recentes = None, []
        try:
            for linha in proc.stdout:
                if agente:
                    texto, ev = linha_legivel(linha)
                    final = ev or final
                else:
                    texto = linha.rstrip()
                if texto:
                    log.write(texto + "\n")
                    recentes = (recentes + [texto])[-12:]
            codigo = proc.wait()
            vencido = not relogio.is_alive()
        finally:  # exceção na leitura não pode deixar o timer vivo (segurava o processo por 45 min)
            relogio.cancel()
            if proc.poll() is None:
                proc.kill()
        if vencido:
            resultado["erro"] = f"Passou do tempo limite de {limite // 60} minutos e foi interrompido."
        elif agente:
            final = final or {}
            resultado["custo_usd"] = final.get("total_cost_usd")
            resposta = (final.get("result") or "").strip()
            resultado["resumo"] = resposta[:2000]
            resultado["saida"] = resposta[:20000]
            if final.get("permission_denials"):
                log.write("Permissões negadas: " + json.dumps(final["permission_denials"], ensure_ascii=False)[:800] + "\n")
            if final.get("is_error") or codigo != 0 or not final:
                motivo = final.get("subtype") or ""
                if "budget" in motivo:
                    resultado["erro"] = f"O agente parou no teto de US$ {spec.get('orcamento', '3.00')} por trabalho."
                else:
                    resultado["erro"] = resposta[:600] or _ultimas(recentes) or f"claude saiu com código {codigo}."
                    if reserva.e_limite_do_claude(resposta + " " + " ".join(recentes)):
                        _tentar_codex(spec, pasta, log, resultado)
            elif spec.get("gravar_em"):
                resultado["erro"] = _gravar_parecer(spec, resposta)
        elif codigo != 0:
            resultado["erro"] = _ultimas(recentes) or f"O comando saiu com código {codigo}."
    except Exception as e:  # noqa: BLE001
        resultado["erro"] = f"Não foi possível rodar: {e}"
    log.write(f"\n[fim] {'falhou: ' + resultado['erro'] if resultado['erro'] else 'ok'}\n")
    log.close()
    fim.set()
    tmp = pasta / "resultado.tmp"
    tmp.write_text(json.dumps(resultado, ensure_ascii=False), encoding="utf-8")
    tmp.replace(pasta / "resultado.json")


def _tentar_codex(spec, pasta, log, resultado):
    """O Claude esgotou o limite de uso: uma única tentativa pelo Codex, com o mesmo agente e o mesmo pedido.
    Se a reserva não puder rodar ou falhar, a falha original do Claude continua em `erro`, com a nota do motivo."""
    original = resultado["erro"]
    resultado["motor_nota"] = None
    exe = reserva.achar_codex()
    if not exe:
        motivo = "o Codex não foi encontrado (instale-o ou defina CODEX=caminho do codex.exe no .env)"
    elif not reserva.logado():
        motivo = "o Codex não está logado (rode `codex login`)"
    else:
        motivo = None
    if motivo:
        resultado["motor_nota"] = f"O Claude estava no limite, mas a reserva com Codex não pôde rodar: {motivo}."
        resultado["erro"] = f"{original}\n[Reserva com Codex indisponível: {motivo}.]"
        log.write(f"Reserva com Codex indisponível: {motivo}\n")
        return
    log.write("O Claude está no limite de uso. Executando o mesmo trabalho pelo Codex (reserva).\n")
    (pasta / "motor.txt").write_text("codex", encoding="ascii")
    arq_final = pasta / "codex_ultima_mensagem.txt"
    try:
        cmd = reserva.montar_comando(spec, exe, spec.get("cwd") or RAIZ, arq_final)
        env = ambiente_agente()
        env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        log.write(f"$ {' '.join(cmd[:6])} …\n")
        proc = subprocess.Popen(cmd, cwd=spec.get("cwd") or str(RAIZ), env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                encoding="utf-8", errors="replace", creationflags=0x08000000)
        proc.stdin.write(reserva.montar_prompt(spec))
        proc.stdin.close()
        relogio = threading.Timer(TEMPO_AGENTE_S, proc.kill)
        relogio.start()
        ultima, recentes = None, []
        try:
            for linha in proc.stdout:
                texto, msg = reserva.linha_codex(linha)
                ultima = msg or ultima
                if texto:
                    log.write(texto + "\n")
                    recentes = (recentes + [texto])[-12:]
            codigo = proc.wait()
            vencido = not relogio.is_alive()
        finally:  # exceção na leitura não pode deixar o timer vivo (segurava o processo por 45 min)
            relogio.cancel()
            if proc.poll() is None:
                proc.kill()
        resposta = ""
        if arq_final.exists():
            resposta = arq_final.read_text(encoding="utf-8", errors="replace").strip()
        resposta = resposta or (ultima or "")
        if vencido:
            raise RuntimeError(f"passou do tempo limite de {TEMPO_AGENTE_S // 60} minutos")
        if codigo != 0 or not resposta:
            raise RuntimeError(_ultimas(recentes) or f"codex saiu com código {codigo}")
        resultado.update(erro=None, resumo=resposta[:2000], saida=resposta[:20000], custo_usd=None, motor="codex",
                         motor_nota="Executado pelo Codex: o Claude estava no limite.")
        if spec.get("gravar_em"):
            resultado["erro"] = _gravar_parecer(spec, resposta)
    except Exception as e:  # noqa: BLE001
        (pasta / "motor.txt").write_text("claude", encoding="ascii")
        resultado["motor_nota"] = f"O Claude estava no limite e a reserva com Codex também falhou: {e}"
        resultado["erro"] = f"{original}\n[Reserva com Codex falhou: {str(e)[:300]}]"
        log.write(f"Reserva com Codex falhou: {e}\n")


def _ultimas(linhas):
    """O trecho do log que explica o erro: a partir do último traceback, ou as últimas linhas, sem barras de progresso."""
    uteis = [x for x in linhas if x.strip() and "%|" not in x]
    return "\n".join(uteis[-4:])[:800]


def _gravar_parecer(spec, resposta):
    if not any(p in resposta.upper() for p in ("APROVADO", "BLOQUEADO")):
        return "O Vini terminou sem dar parecer (APROVADO ou BLOQUEADO). Nada foi gravado."
    destino = RAIZ / "output" / spec["slug"] / spec["gravar_em"]
    tmp = destino.with_suffix(".tmp")
    tmp.write_text(resposta + "\n", encoding="utf-8")
    tmp.replace(destino)
    return None


if __name__ == "__main__":
    rodar(sys.argv[1])
