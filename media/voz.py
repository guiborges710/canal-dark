"""Narração: chama o worker do Chatterbox no ambiente separado (.venv-voz) e devolve as falas por cena.

Configuração em config_shorts.yaml (seção voz):
  amostra: caminho de um áudio da SUA voz (10 s a 2 min, em português, sem ruído). Vazio = voz padrão do modelo.
  threads: threads de CPU do modelo.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_VOZ = ROOT / ".venv-voz" / "Scripts" / "python.exe"
WORKER = Path(__file__).resolve().parent / "voz_worker.py"


def tem_falas(cenas):
    return any((c.get("fala") or "").strip() for c in cenas)


def gerar(out, cenas_path, cfg):
    """Gera as falas de todas as cenas que têm o campo 'fala'. Devolve {índice: {"wav", "dur"}}."""
    if not PY_VOZ.exists():
        raise SystemExit(
            f"Ambiente da voz não encontrado em {PY_VOZ}. Crie com: py -3.13 -m venv .venv-voz && "
            ".venv-voz\\Scripts\\python -m pip install chatterbox-tts \"setuptools<81\"")
    amostra = (cfg or {}).get("amostra") or ""
    if not amostra:
        # Regra do canal: a narração é SEMPRE com a voz do Guilherme. Sem a amostra, nada é gerado com voz padrão.
        raise SystemExit("Falta a amostra da sua voz. Grave o texto de voz/roteiro_para_gravar.md, salve como "
                         "voz/amostra.wav e aponte em config_shorts.yaml (voz.amostra).")
    if not (ROOT / amostra).exists() and not Path(amostra).exists():
        raise SystemExit(f"Amostra de voz não encontrada: {amostra}. Confira voz.amostra no config_shorts.yaml.")
    threads = str((cfg or {}).get("threads", 8))
    cmd = [str(PY_VOZ), str(WORKER), "--cenas", str(cenas_path), "--out", str(out), "--threads", threads]
    if amostra:
        cmd += ["--amostra", str(ROOT / amostra if not Path(amostra).is_absolute() else amostra)]
    r = subprocess.run(cmd, capture_output=True)  # bytes: a barra de progresso do modelo não é UTF-8 puro
    if r.returncode != 0:
        raise SystemExit(f"Falha na narração (Chatterbox), código {r.returncode}:\n"
                         + r.stderr.decode("utf-8", "replace")[-1500:])
    for linha in r.stdout.decode("utf-8", "replace").splitlines():
        if linha.strip():
            print(linha, flush=True)
    return json.loads((Path(out) / "falas" / "falas.json").read_text(encoding="utf-8"))
