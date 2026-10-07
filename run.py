#!/usr/bin/env python3
"""Orquestrador do canal dark.

Uso:
  python run.py video --topic "tema do vídeo" [--mock]
  python run.py ideas [--mock]
  python run.py voices
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agents.llm import LLM  # noqa: E402
from agents import research, script as scriptmod, scenes as scenesmod, metadata as metamod  # noqa: E402
from media import tts, images, render  # noqa: E402
from media.util import duration, parallel  # noqa: E402


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


def make_video(cfg, topic, mock):
    llm = LLM(cfg, mock=mock)
    out = ROOT / "output" / (("mock-" if mock else "") + slugify(topic))
    for d in ("audio", "images", "clips"):
        (out / d).mkdir(parents=True, exist_ok=True)
    print(f"Pasta do vídeo: {out}")

    # 1. Pesquisa do tema
    step("1/8 Pesquisando o tema")
    f = out / "notas.md"
    if not f.exists():
        f.write_text(research.research_topic(llm, cfg, topic), encoding="utf-8")
    notes = f.read_text(encoding="utf-8")

    # 1b. Ângulo editorial (ponto de vista próprio, definido antes do roteiro)
    f = out / "angulo.md"
    if not f.exists():
        if mock or os.environ.get("ANTHROPIC_API_KEY"):
            f.write_text(research.make_angle(llm, cfg, topic, notes), encoding="utf-8")
        else:
            print("   ⚠ sem angulo.md e sem ANTHROPIC_API_KEY: seguindo sem ângulo editorial (o verificador vai apontar)")
    angle = f.read_text(encoding="utf-8") if f.exists() else ""

    # 2. Roteiro + revisão
    step("2/8 Escrevendo e revisando o roteiro")
    f = out / "roteiro.txt"
    if not f.exists():
        draft = scriptmod.write_script(llm, cfg, topic, notes, angle)
        (out / "roteiro_rascunho.txt").write_text(draft, encoding="utf-8")
        final, review = scriptmod.review_script(llm, cfg, notes, draft, angle)
        (out / "revisao.json").write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding="utf-8")
        f.write_text(final, encoding="utf-8")
    script = f.read_text(encoding="utf-8")
    words = len(script.split())
    target = scriptmod.target_words(cfg)
    print(f"   {words} palavras (alvo ~{target})")
    if words < target * 0.7:
        print("   ⚠ roteiro bem abaixo do alvo; o vídeo ficará mais curto que o planejado")

    # 3. Cenas e prompts de imagem
    step("3/8 Dividindo em cenas e criando prompts de imagem")
    f = out / "cenas.json"
    if not f.exists():
        texts = scenesmod.split_scenes(script, cfg["scenes"]["min_words"])
        prompts = scenesmod.image_prompts(llm, cfg, texts, topic)
        f.write_text(json.dumps([{"text": t, **p} for t, p in zip(texts, prompts)],
                                ensure_ascii=False, indent=1), encoding="utf-8")
    scenes = json.loads(f.read_text(encoding="utf-8"))
    print(f"   {len(scenes)} cenas")

    # 4. Narração
    step("4/8 Gerando a narração")
    audio = [out / "audio" / f"{i:03}.mp3" for i in range(len(scenes))]
    parallel(lambda a: tts.synth(cfg, scenes[a[0]]["text"], a[1], mock), list(enumerate(audio)))

    # 5. Imagens
    step("5/8 Gerando as imagens")
    imgs = [out / "images" / f"{i:03}.jpg" for i in range(len(scenes))]
    workers = 1 if cfg["images"].get("provider") == "commons" else 4
    parallel(lambda a: images.generate(cfg, scenes[a[0]]["image_prompt"], a[1], mock,
                                       queries=scenes[a[0]].get("search")), list(enumerate(imgs)), workers=workers)
    real = len(list((out / "images").glob("*.json")))
    if cfg["images"].get("provider") == "commons":
        print(f"   {real} de {len(scenes)} cenas com imagem real de arquivo; as demais usam a reserva "
              f"({cfg['images'].get('fallback', 'local_art')})")

    # 6. Edição
    step("6/8 Editando o vídeo")
    pause = cfg["tts"]["pause_seconds"]
    durs = [duration(a) + pause for a in audio]
    clips = [out / "clips" / f"{i:03}.mp4" for i in range(len(scenes))]
    for i in range(len(scenes)):
        if not clips[i].exists():
            render.scene_clip(cfg, imgs[i], audio[i], durs[i], clips[i], i)
    srt = render.build_srt(scenes, durs, pause)
    final = render.assemble(cfg, clips, out, srt_text=srt, total=sum(durs))
    total = duration(final)
    print(f"   Vídeo pronto: {final.name} ({total / 60:.1f} min)")

    # 7. Metadados e thumbnail
    step("7/8 Criando título, descrição, tags e thumbnail")
    f = out / "metadados.json"
    if not f.exists():
        f.write_text(json.dumps(metamod.make_metadata(llm, cfg, script), ensure_ascii=False, indent=1),
                     encoding="utf-8")
    meta = json.loads(f.read_text(encoding="utf-8"))
    thumb = out / "thumbnail.jpg"
    images.generate(cfg, meta["thumbnail_prompt"] + ", " + cfg["channel"]["visual_style"], thumb, mock)
    from media import commons
    credit_lines = commons.credits(out / "images")
    credit_block = ""
    if credit_lines:
        credit_block = ("CRÉDITOS DAS IMAGENS (cole no fim da descrição; várias licenças exigem a atribuição):\n"
                        + "\n".join(credit_lines) + "\n\n")
    if real < len(scenes):
        credit_block += "Obs.: as cenas sem registro histórico usam ilustrações geradas por computador; diga isso na descrição.\n\n"
    (out / "creditos.txt").write_text(credit_block, encoding="utf-8")
    (out / "PUBLICAR.txt").write_text(
        f"TÍTULO:\n{meta['titulo']}\n\nDESCRIÇÃO:\n{meta['descricao']}\n\n{credit_block}"
        f"TAGS (separadas por vírgula):\n{', '.join(meta['tags'])}\n\n"
        f"TEXTO SUGERIDO PARA A THUMBNAIL: {meta.get('thumbnail_texto', '')}\n"
        f"ARQUIVOS: video.mp4 e thumbnail.jpg\n\n"
        "ANTES DE PUBLICAR:\n"
        "- Assista ao vídeo inteiro e confira os fatos principais contra as fontes em notas.md.\n"
        "- No upload, responda a pergunta sobre conteúdo alterado ou sintético: imagens geradas por IA que pareçam reais\n"
        "  (cenas de um evento real que não foram registradas) exigem a divulgação. Confira a regra atual no YouTube Studio.\n"
        "- A política de conteúdo inautêntico pesa contra vídeos em molde repetido e sem comentário próprio: "
        "o roteiro precisa ter ponto de vista e pesquisa originais.\n",
        encoding="utf-8")

    # Verificação de conformidade com as políticas do YouTube
    from compliance import check as compliance_check
    report, counts = compliance_check(out, cfg)
    (out / "CONFORMIDADE.md").write_text(report, encoding="utf-8")
    print(f"   Conformidade: {counts['OK']} ok, {counts['ATENÇÃO']} atenção, {counts['FALTA']} faltando (veja CONFORMIDADE.md)")

    # 8. Custo estimado
    step("8/8 Custo estimado deste vídeo (apenas chamadas novas desta execução)")
    p = cfg["prices"]
    chars = sum(len(s["text"]) for s in scenes)
    tts_cost = 0 if (mock or cfg["tts"].get("provider") == "kokoro") else chars / 1e6 * p["tts_per_mchar"]
    prov = cfg["images"].get("provider")
    paid_provider = cfg["images"].get("fallback") if prov == "commons" else prov
    n_paid = (len(scenes) - real if prov == "commons" else len(scenes)) + 1  # +1 da thumbnail
    img_cost = 0 if (mock or paid_provider != "fal") else n_paid * p["image_each"]
    llm_cost = llm.cost_usd()
    cost = {"claude_usd": llm_cost, "voz_usd": round(tts_cost, 4), "imagens_usd": round(img_cost, 4),
            "total_usd": round(llm_cost + tts_cost + img_cost, 4)}
    (out / "custo.json").write_text(json.dumps(cost, indent=1), encoding="utf-8")
    print("  ", cost)
    print(f"\n✔ Pronto. Suba manualmente o vídeo usando {out / 'PUBLICAR.txt'}")


def main():
    for stream in (sys.stdout, sys.stderr):  # evita erro de acentos/símbolos no terminal do Windows
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    load_env()
    ap = argparse.ArgumentParser(description="Orquestrador do canal dark")
    ap.add_argument("command", choices=["video", "ideas", "voices", "check"])
    ap.add_argument("--topic", help="tema do vídeo (comando video)")
    ap.add_argument("--mock", action="store_true", help="simula tudo, sem APIs e sem custo")
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    if a.mock:  # teste rápido em resolução menor
        cfg["render"].update(width=1280, height=720, fps=24)

    if a.command == "voices":
        print("\n".join(tts.list_voices(cfg)))
    elif a.command == "check":
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
    else:
        if not a.topic:
            ap.error("use --topic \"tema do vídeo\"")
        make_video(cfg, a.topic, a.mock)


if __name__ == "__main__":
    main()
