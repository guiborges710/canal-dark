"""Faz o papel dos comandos pesados nos testes: narração e render. Gera arquivos reais e tocáveis, em segundos, sem Chatterbox.
Falha sob encomenda: crie output/<slug>/.falhar_render ou .falhar_narracao. Para segurar o render em andamento: .segurar_render ou .segurar_narracao."""
import json
import subprocess
import sys
import time
import wave
from pathlib import Path

args = sys.argv[1:]


def opcao(nome, padrao=None):
    return args[args.index(nome) + 1] if nome in args else padrao


def wav(destino, segundos, nota):
    import math
    amostras = int(48000 * segundos)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"".join(int(9000 * math.sin(2 * math.pi * nota * i / 48000)).to_bytes(2, "little", signed=True) for i in range(amostras)))


def narrar():
    p = Path("output") / opcao("--slug")
    if (p / ".falhar_narracao").exists():
        print("Falha na narração (Chatterbox), código 3:\nsimulação: memória insuficiente", flush=True)
        sys.exit(3)
    if (p / "cenas.json").exists():
        cenas = json.loads((p / "cenas.json").read_text(encoding="utf-8"))
    else:  # mesma regra do estudio/narrar.py: sem cenas ainda, cada parágrafo da seção ## Narração é uma fala
        import re
        m = re.search(r"^## *Narra[cç][aã]o[^\n]*\n(.*?)(?=^## |\Z)", (p / "direcao_viral.md").read_text(encoding="utf-8"), re.S | re.M)
        cenas = [{"fala": x.strip()} for x in re.split(r"\n\s*\n", m.group(1)) if x.strip()]
    indices = [int(x) for x in opcao("--cenas", "").split(",") if x] or list(range(len(cenas)))
    d = p / "falas"
    d.mkdir(exist_ok=True)
    tabela = json.loads((d / "falas.json").read_text(encoding="utf-8")) if (d / "falas.json").exists() else {}
    textos_arq = d / "textos.json"
    textos = json.loads(textos_arq.read_text(encoding="utf-8")) if textos_arq.exists() else [None] * len(cenas)
    textos += [None] * (len(cenas) - len(textos))
    semente = int(time.time() * 10) % 200
    dur = float((p / ".dur_narracao").read_text()) if (p / ".dur_narracao").exists() else 1.0  # o teste escolhe: fala que não cabe na cena
    for _ in range(300):  # o teste segura a narração para provar o estado "em andamento" (máx. 30 s)
        if not (Path("output") / opcao("--slug") / ".segurar_narracao").exists():
            break
        time.sleep(0.1)
    for i in indices:
        print(f"   fala {i + 1}: {dur} s (2.5 palavras/s)", flush=True)
        destino = d / f"{i:02d}.wav"
        wav(destino, dur, 300 + semente + i * 20)
        tabela[str(i)] = {"wav": str(destino), "dur": dur}
        textos[i] = cenas[i]["fala"]
        time.sleep(0.2)
    (d / "falas.json").write_text(json.dumps(tabela, ensure_ascii=False, indent=1), encoding="utf-8")
    textos_arq.write_text(json.dumps(textos, ensure_ascii=False, indent=1), encoding="utf-8")


def render():
    slug = opcao("--topic")
    p = Path("output") / slug
    print("▶ 4/6 Renderizando a animação", flush=True)
    if (p / ".falhar_render").exists():
        print("cenas.json: duração total 75.0 s fora do formato (de 20 a 60 s). Ajuste as falas.", flush=True)
        sys.exit(1)
    for _ in range(300):  # o teste segura o render para provar o estado "em andamento" (máx. 30 s)
        if not (p / ".segurar_render").exists():
            break
        time.sleep(0.1)
    (p / "frames").mkdir(exist_ok=True)
    for i in range(1, 4):
        print(f"   {i * 100}/300", flush=True)
        time.sleep(0.2)
    (p / "frames").rmdir()
    tom = int(time.time()) % 200 + 300
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=size=540x960:rate=30:duration=4", "-f", "lavfi", "-i", f"sine=frequency={tom}:duration=4",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(p / "video.tmp.mp4")], check=True)
    (p / "video.tmp.mp4").replace(p / "video.mp4")
    print("▶ 6/6 Conformidade e custo", flush=True)


if args[:1] == ["-m"] and args[1] == "estudio.narrar":
    narrar()
elif args[:1] == ["-m"] and args[1] == "media.sketch":
    pass  # a prévia já vem do agente simulado
elif args[:2] == ["run.py", "video"]:
    render()
else:
    print(f"comando não simulado: {args}", flush=True)
    sys.exit(2)
