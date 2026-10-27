#!/usr/bin/env python3
"""Sobe UM vídeo pendente por execução, como PRIVADO, para o YouTube. Pensado para o Agendador de Tarefas do Windows.

A fila é explícita: só entra o slug listado em output/fila_postagem.txt (um por linha, na ordem de envio).
Além disso, o vídeo precisa:
  - ter video.mp4, thumbnail.jpg e metadados.json em output/<slug>/;
  - ter auditoria.md com APROVADO (e sem BLOQUEADO), dada pelo Vini;
  - ainda não ter publicado.json (não foi enviado antes).

Não publica como público: o vídeo fica privado para você revisar e publicar no Studio.
Limite: um vídeo por execução, para não virar produção em massa.

Uso:
  python postar_pendentes.py            # sobe o próximo pendente
  python postar_pendentes.py --listar   # só mostra a fila, não envia
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def aprovado(out):
    audit = out / "auditoria.md"
    if not audit.exists():
        return False
    txt = audit.read_text(encoding="utf-8").upper()
    return "APROVADO" in txt and "BLOQUEADO" not in txt


FILA = ROOT / "output" / "fila_postagem.txt"


def pendentes():
    """Slugs da fila, na ordem do arquivo, que ainda não foram enviados e estão prontos e aprovados."""
    if not FILA.exists():
        return []
    fila = []
    for linha in FILA.read_text(encoding="utf-8").splitlines():
        slug = linha.strip()
        if not slug or slug.startswith("#"):
            continue
        out = ROOT / "output" / slug
        if not out.is_dir():
            print(f"   (fila) {slug}: pasta não encontrada; pulado")
            continue
        if not all((out / f).exists() for f in ("video.mp4", "thumbnail.jpg", "metadados.json")):
            print(f"   (fila) {slug}: falta video.mp4, thumbnail.jpg ou metadados.json; pulado")
            continue
        if (out / "publicado.json").exists():
            continue
        if not aprovado(out):
            print(f"   (fila) {slug}: sem auditoria APROVADA do Vini; pulado")
            continue
        fila.append(out)
    return fila


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true", help="só mostra a fila, sem enviar")
    a = ap.parse_args()

    fila = pendentes()
    if a.listar or not fila:
        print("Fila de upload pronta:" if fila else "Nenhum vídeo pronto na fila.")
        for out in fila:
            print(f"  - {out.name}")
        return

    cfg = yaml.safe_load(open(ROOT / "config_shorts.yaml", encoding="utf-8"))
    out = fila[0]
    print(f"Enviando {out.name} como PRIVADO (um por execução).", flush=True)
    from media import youtube
    try:
        res = youtube.upload(cfg, out, ROOT, privacy="private")
    except SystemExit as e:
        print(f"Não enviado: {e}")
        return
    registro = {"enviado_em": datetime.now().isoformat(timespec="seconds"), "privacidade": res["privacy"],
                "url": res["url"], "studio": res["studio_url"]}
    (out / "publicado.json").write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Enviado como privado: {res['url']}")
    print(f"Revise e publique no Studio: {res['studio_url']}")


if __name__ == "__main__":
    main()
