import subprocess
from concurrent.futures import ThreadPoolExecutor


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Falha ao rodar: " + " ".join(map(str, cmd)) + "\n" + r.stderr[-1500:])
    return r.stdout


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def parallel(fn, items, workers=4):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
