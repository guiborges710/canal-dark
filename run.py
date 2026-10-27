#!/usr/bin/env python3
"""Orquestrador do canal dark (Shorts, estilo de animação vetorial).

Uso:
  python run.py video --topic "tema do vídeo" [--mock] [--allow-paid]
  python run.py check --topic "tema do vídeo"
  python run.py ideas [--mock]
  python run.py publish --slug <pasta> [--privacy private|unlisted|public]

Cada etapa grava seu arquivo em output/<slug>/ e pula o que já existe. A squad (agentes do Claude Code)
escreve o conteúdo de graça; este script valida, renderiza e confere. --allow-paid só libera a geração
de texto pela API da Anthropic, usada quando a squad não está disponível.
"""
import argparse
import json
import os
import sys
import unicodedata
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agents.llm import LLM  # noqa: E402
from agents import research, script as scriptmod, metadata as metamod  # noqa: E402
from media import motion  # noqa: E402


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "video"


def step(msg):
    print(f"\n▶ {msg}", flush=True)


def need_creative(out_file, agent, mock, allow_paid):
    """Garante que um arquivo criativo exista antes de seguir. A squad (agentes do Claude) é quem os produz
    de graça; gerar por API da Anthropic custa, então só acontece com --allow-paid (ou --mock).
    Devolve True se o chamador deve gerar o arquivo agora; False se já existe."""
    if out_file.exists():
        return False
    if mock or allow_paid:
        return True
    raise SystemExit(
        f"Falta {out_file.name}. Gere com a squad (@{agent}) e salve em output/<slug>/, "
        "ou rode de novo com --allow-paid para gerar pela API.")


def make_video(cfg, topic, mock, allow_paid=False):
    llm = LLM(cfg, mock=mock)
    out = ROOT / "output" / (("mock-" if mock else "") + slugify(topic))
    out.mkdir(parents=True, exist_ok=True)
    print(f"Pasta do vídeo: {out}")

    # 1. Pesquisa do tema
    step("1/6 Pesquisando o tema")
    f = out / "notas.md"
    if need_creative(f, "modric-pesquisador-tema", mock, allow_paid):
        f.write_text(research.research_topic(llm, cfg, topic), encoding="utf-8")
    notes = f.read_text(encoding="utf-8")

    # 1b. Ângulo editorial
    f = out / "angulo.md"
    if need_creative(f, "messi-estrategista-angulo", mock, allow_paid):
        f.write_text(research.make_angle(llm, cfg, topic, notes), encoding="utf-8")

    # 2. Texto do vídeo (roteiro.txt: o que aparece nos cartões, em ordem)
    step("2/6 Escrevendo e revisando o texto")
    f = out / "roteiro.txt"
    if need_creative(f, "neymar-roteirista", mock, allow_paid):
        angle = (out / "angulo.md").read_text(encoding="utf-8") if (out / "angulo.md").exists() else ""
        draft = scriptmod.write_script(llm, cfg, topic, notes, angle)
        final, review = scriptmod.review_script(llm, cfg, notes, draft, angle)
        (out / "revisao.json").write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding="utf-8")
        f.write_text(final, encoding="utf-8")

    # 3. Cenas (cenas.json): a squad desenha a sequência de cartões e gráficos
    step("3/6 Montando as cenas da animação")
    f = out / "cenas.json"
    if need_creative(f, "olise-diretor-arte", mock, allow_paid):
        if mock:
            from agents import mocks
            f.write_text(json.dumps(mocks.CENAS, ensure_ascii=False, indent=1), encoding="utf-8")
        else:
            raise SystemExit("Geração de cenas pela API não existe neste estilo. Peça a @olise-diretor-arte.")
    cenas = json.loads(f.read_text(encoding="utf-8"))
    print(f"   {len(cenas)} cenas, {sum(c['duracao'] for c in cenas):.0f} s")

    # 4. Render: animação + efeitos sonoros + MP4 + miniatura (sem imagens, sem voz)
    step("4/6 Renderizando a animação")
    video = motion.render(out, cenas_path=f, voz_cfg=cfg.get("voz"))

    # 5. Metadados e publicação
    step("5/6 Criando título, descrição e tags")
    f = out / "metadados.json"
    if need_creative(f, "mbappe-editor-metadados", mock, allow_paid):
        roteiro = (out / "roteiro.txt").read_text(encoding="utf-8")
        f.write_text(json.dumps(metamod.make_metadata(llm, cfg, roteiro), ensure_ascii=False, indent=1),
                     encoding="utf-8")
    meta = json.loads(f.read_text(encoding="utf-8"))
    (out / "PUBLICAR.txt").write_text(
        f"TÍTULO:\n{meta['titulo']}\n\nDESCRIÇÃO:\n{meta['descricao']}\n\n"
        f"TAGS (separadas por vírgula):\n{', '.join(meta['tags'])}\n\n"
        f"TEXTO SUGERIDO PARA A THUMBNAIL: {meta.get('thumbnail_texto', '')}\n"
        f"ARQUIVOS: video.mp4 e thumbnail.jpg\n\n"
        "ANTES DE PUBLICAR:\n"
        "- Assista ao vídeo inteiro e confira os fatos principais contra as fontes em notas.md.\n"
        "- A descrição já diz que é animação feita por computador, com narração por IA a partir da voz do autor. Não há imagem de IA nem foto de terceiros.\n"
        "- A política de conteúdo inautêntico pesa contra vídeos em molde repetido e sem comentário próprio: "
        "o roteiro precisa ter ponto de vista e pesquisa originais.\n",
        encoding="utf-8")

    # 6. Conformidade e custo
    step("6/6 Conformidade e custo")
    from compliance import check as compliance_check
    report, counts = compliance_check(out, cfg)
    (out / "CONFORMIDADE.md").write_text(report, encoding="utf-8")
    print(f"   Conformidade: {counts['OK']} ok, {counts['ATENÇÃO']} atenção, {counts['FALTA']} faltando (veja CONFORMIDADE.md)")
    cost = {"claude_usd": llm.cost_usd(), "voz_usd": 0, "imagens_usd": 0, "total_usd": llm.cost_usd()}
    (out / "custo.json").write_text(json.dumps(cost, indent=1), encoding="utf-8")
    print("  ", cost)
    print(f"\n✔ Pronto: {video}. Suba manualmente usando {out / 'PUBLICAR.txt'}")


def publish_video(cfg, a, root):
    """Sobe um vídeo já produzido e AUDITADO para o YouTube (privado por padrão).
    Só publica depois de o Vini aprovar (auditoria.md com APROVADO)."""
    if not (a.slug or a.topic):
        raise SystemExit("use --slug <pasta> ou --topic \"tema do vídeo\" (o mesmo usado para gerar)")
    slug = a.slug or slugify(a.topic)
    out = root / "output" / slug
    if not out.is_dir():
        raise SystemExit(f"Pasta não encontrada: {out}. Gere o vídeo antes de publicar.")

    # Regra do canal: nada vai ao ar sem o Vini aprovar.
    audit = out / "auditoria.md"
    if not audit.exists():
        raise SystemExit(
            f"Falta {audit}. O Vini (vini-auditor-conformidade) precisa auditar o vídeo antes do upload.")
    txt = audit.read_text(encoding="utf-8").upper()
    if "APROVADO" not in txt or "BLOQUEADO" in txt:
        raise SystemExit(
            f"A auditoria em {audit} não está APROVADA (ou está BLOQUEADA). Resolva as pendências do Vini "
            "antes de publicar.")

    from media import youtube
    step("Publicando no YouTube")
    res = youtube.upload(cfg, out, root, privacy=a.privacy)
    print(f"\n✔ Enviado como {res['privacy']}.")
    print(f"   Assistir: {res['url']}")
    print(f"   Revisar/publicar no Studio: {res['studio_url']}")


def main():
    for stream in (sys.stdout, sys.stderr):  # evita erro de acentos/símbolos no terminal do Windows
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    load_env()
    ap = argparse.ArgumentParser(description="Orquestrador do canal dark")
    ap.add_argument("command", choices=["video", "ideas", "check", "publish"])
    ap.add_argument("--topic", help="tema do vídeo (video/check/publish)")
    ap.add_argument("--slug", help="pasta do vídeo em output/ (alternativa ao --topic no publish)")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], default=None,
                    help="visibilidade no publish; padrão = publish.privacy do config (private)")
    ap.add_argument("--mock", action="store_true", help="simula o texto (sem API); o render é real")
    ap.add_argument("--allow-paid", action="store_true", dest="allow_paid",
                    help="autoriza gerar texto pela API da Anthropic quando a squad não entregou")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(ROOT / "config_shorts.yaml", encoding="utf-8"))

    if a.command == "check":
        if not a.topic:
            ap.error("use --topic \"tema do vídeo\" (o mesmo usado para gerar)")
        from compliance import check as compliance_check
        d = ROOT / "output" / (("mock-" if a.mock else "") + slugify(a.topic))
        report, counts = compliance_check(d, cfg)
        (d / "CONFORMIDADE.md").write_text(report, encoding="utf-8")
        print(report)
    elif a.command == "ideas":
        ideas, videos = research.generate_ideas(LLM(cfg, mock=a.mock), cfg)
        out = ROOT / "output"
        out.mkdir(exist_ok=True)
        (out / "ideias.json").write_text(json.dumps({"ideias": ideas, "base": videos}, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
        for i, it in enumerate(ideas, 1):
            print(f"{i}. {it['titulo']} — {it['angulo']}")
        print(f"\nSalvo em {out / 'ideias.json'}")
    elif a.command == "publish":
        publish_video(cfg, a, ROOT)
    else:
        if not a.topic:
            ap.error("use --topic \"tema do vídeo\"")
        make_video(cfg, a.topic, a.mock, allow_paid=a.allow_paid)


if __name__ == "__main__":
    main()
