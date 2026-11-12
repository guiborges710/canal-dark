"""Hook do Claude Code: regenera o espelho do sistema quando um .md/.txt é criado ou alterado.

Ligado em .claude/settings.local.json (PostToolUse Write|Edit e Stop). Lê o JSON do hook no stdin.
Várias escritas seguidas (agentes em paralelo) não rodam o gerador ao mesmo tempo: quem chega
com outra execução em andamento só marca "pendente", e a execução atual roda mais uma vez no fim.
Nunca falha o fluxo do agente: qualquer erro termina em silêncio.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GERADOR = RAIZ / "tools" / "gerar_espelho.py"
TMP = Path(tempfile.gettempdir())
LOCK = TMP / "contexto_explica_espelho.lock"
PEND = TMP / "contexto_explica_espelho.pendente"
EVENTOS_SEMPRE = {"Stop", "SubagentStop"}


def deve_rodar(dados: dict) -> bool:
    if dados.get("hook_event_name") in EVENTOS_SEMPRE:
        return True
    ti = dados.get("tool_input") or {}
    tr = dados.get("tool_response") or {}
    f = ti.get("file_path") or (tr.get("filePath") if isinstance(tr, dict) else None)
    if not f:
        return False
    p = Path(f)
    if p.suffix.lower() not in (".md", ".txt"):
        return False
    try:
        p.resolve().relative_to(RAIZ)
    except ValueError:
        return False  # fora do projeto
    return True


def main():
    try:
        dados = json.load(sys.stdin)
    except Exception:
        dados = {}
    if not deve_rodar(dados):
        return
    try:
        fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        try:
            if time.time() - LOCK.stat().st_mtime > 120:  # trava velha de uma execução que morreu
                LOCK.unlink()
            else:
                PEND.touch()
        except Exception:
            pass
        return
    try:
        while True:
            try:
                PEND.unlink()
            except FileNotFoundError:
                pass
            subprocess.run([sys.executable, str(GERADOR)], cwd=str(RAIZ), capture_output=True, timeout=180)
            if not PEND.exists():
                break
    except Exception:
        pass
    finally:
        try:
            LOCK.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    main()
