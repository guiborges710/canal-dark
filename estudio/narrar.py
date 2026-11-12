"""Gera a narração sem o render, para o Guilherme revisar antes de gastar tempo desenhando.

Usa o mesmo media/voz.py e grava o mesmo contrato (falas/falas.json e falas/textos.json) que o render do sketch reaproveita.
Com --cenas, refaz só esses trechos. voz_ajustes.json (opcional) ajusta um trecho sem mexer na fala oficial do cenas.json:
  {"2": {"dizer": "í bê gê é", "velocidade": 1.05, "exaggeration": 0.7, "cfg_weight": 0.4, "pausa_frase_s": 0.1, "pausa_max_s": 0.18}}

Uso:  python -m estudio.narrar --slug <pasta> [--cenas 2,5] [--formato vertical]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from media import voz  # noqa: E402
from media.sketch import carregar_config  # noqa: E402


def _ler(p, padrao):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def narrar(out, cfg_voz, indices=None):
    arq = out / "cenas3d.json" if (out / "cenas3d.json").exists() else out / "cenas.json"
    if arq.exists():
        cenas = json.loads(arq.read_text(encoding="utf-8-sig"))
    else:
        # Fluxo com narração em paralelo às cenas: "cada fala vira uma cena" (contrato do Olise), então a seção ## Narração já diz as falas.
        m = re.search(r"^## *Narra[cç][aã]o[^\n]*\n(.*?)(?=^## |\Z)", (out / "direcao_viral.md").read_text(encoding="utf-8-sig") if (out / "direcao_viral.md").exists() else "", re.S | re.M)
        cenas = [{"fala": p.strip()} for p in re.split(r"\n\s*\n", m.group(1)) if p.strip()] if m else []
        if not cenas:
            raise SystemExit("Sem cenas.json e sem a seção ## Narração em direcao_viral.md: nada para narrar.")
    falas_dir = out / "falas"
    tabela_antiga = _ler(falas_dir / "falas.json", {})
    textos = _ler(falas_dir / "textos.json", None)
    if textos is None or len(textos) != len(cenas) or len(tabela_antiga) != len(cenas):
        indices = None  # sem uma narração completa de mesmo tamanho não dá para refazer só um pedaço
    alvo = sorted(indices) if indices else [i for i, c in enumerate(cenas) if (c.get("fala") or "").strip()]
    if not alvo:
        raise SystemExit("Nenhuma cena com fala para narrar.")
    ajustes = _ler(out / "voz_ajustes.json", {})

    # Trechos com os mesmos parâmetros vão juntos: o worker recarrega o modelo a cada chamada.
    grupos = {}
    for i in alvo:
        a = ajustes.get(str(i), {})
        chave = json.dumps({k: a[k] for k in ("velocidade", "pausa_frase_s", "pausa_max_s", "exaggeration", "cfg_weight") if k in a}, sort_keys=True)
        grupos.setdefault(chave, []).append(i)

    tabela = dict(tabela_antiga) if indices else {}
    falas_dir.mkdir(exist_ok=True)
    tmp = out / ".cenas_narrar.json"
    try:
        for chave, idx in grupos.items():
            lista = [{"fala": ""} for _ in cenas]
            for i in idx:
                lista[i] = {"fala": ajustes.get(str(i), {}).get("dizer") or cenas[i]["fala"]}
            tmp.write_text(json.dumps(lista, ensure_ascii=False), encoding="utf-8")
            print(f"   narrando {len(idx)} trecho(s): {', '.join(str(i + 1) for i in idx)}", flush=True)
            tabela.update(voz.gerar(out, tmp, {**(cfg_voz or {}), **json.loads(chave)}))
    finally:
        tmp.unlink(missing_ok=True)
        if tabela:  # o worker sobrescreve falas.json só com o que gerou: devolve a tabela completa, mesmo se falhou no meio
            (falas_dir / "falas.json").write_text(json.dumps(tabela, ensure_ascii=False, indent=1), encoding="utf-8")
    # textos.json guarda a fala oficial, não o `dizer`: é a chave com que o render reaproveita a narração.
    novos = list(textos) if indices else [c.get("fala") for c in cenas]
    for i in alvo:
        novos[i] = cenas[i]["fala"]
    (falas_dir / "textos.json").write_text(json.dumps(novos, ensure_ascii=False, indent=1), encoding="utf-8")
    if not indices:
        for wav in falas_dir.glob("*.wav"):
            if wav.stem.isdigit() and int(wav.stem) >= len(cenas):
                wav.unlink()
    print(f"   narração pronta: {len(alvo)} trecho(s)", flush=True)


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--cenas", default="")
    ap.add_argument("--formato", choices=["vertical", "horizontal"], default="vertical")
    a = ap.parse_args()
    indices = [int(x) for x in a.cenas.split(",") if x.strip()] or None
    narrar(ROOT / "output" / a.slug, carregar_config(a.formato).get("voz"), indices)


if __name__ == "__main__":
    main()
