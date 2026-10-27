"""Vídeo por animação vetorial (estilo do canal): valida o cenas.json, renderiza com o motor em render/,
gera os efeitos sonoros e codifica o MP4. A miniatura é um frame do próprio vídeo (sem imagem gerada por IA).

Cada cena do cenas.json tem "tipo" e "duracao" (segundos). Tipos e campos: ver SPEC_TIPOS abaixo.
"""
import json
import shutil
import subprocess
from pathlib import Path

from . import sfx, voz
from .util import run

ROOT = Path(__file__).resolve().parent.parent
RENDER = ROOT / "render"
MAX_LINHA = 26  # caracteres por linha de texto; acima disso o cartão fica pequeno demais para ler no celular

CORES = {"azul", "azul-claro", "amarelo", "laranja", "branco", "grafite"}
TEXTOS = {"titulo", "legenda", "pergunta", "rodape", "subtitulo", "destaque", "conclusao",
          "negacao", "afirmacao", "reforco"}

SPEC_TIPOS = {
    "gancho": {"campos": ["numeros", "legenda", "pergunta"], "opcionais": ["cores", "rodape"], "min": 4},
    "barras": {"campos": ["titulo", "barras", "escala_max"], "opcionais": ["unidade", "rodape", "rodape_cor"], "min": 4},
    "barras_horizontais": {"campos": ["titulo", "barras"], "opcionais": ["subtitulo", "destaque", "conclusao"], "min": 4},
    "fechamento": {"campos": ["negacao", "afirmacao", "reforco", "pergunta"], "opcionais": [], "min": 8},
}


class SpecErro(SystemExit):
    pass


def _linhas(valor, onde):
    if isinstance(valor, str):
        valor = [valor]
    if not isinstance(valor, list) or not valor or not all(isinstance(x, str) and x.strip() for x in valor):
        raise SpecErro(f"{onde}: esperado texto ou lista de textos não vazios")
    for x in valor:
        if len(x) > MAX_LINHA:
            raise SpecErro(f"{onde}: linha longa demais ({len(x)} > {MAX_LINHA}): \"{x}\". Quebre em mais linhas.")
    return valor


def validate(cenas):
    """Confere o cenas.json antes de renderizar. Erro aponta a cena e o campo."""
    if not isinstance(cenas, list) or not cenas:
        raise SpecErro("cenas.json: lista vazia ou não é uma lista")
    total = 0.0
    for i, c in enumerate(cenas, 1):
        onde = f"cena {i}"
        tipo = c.get("tipo")
        if tipo not in SPEC_TIPOS:
            raise SpecErro(f"{onde}: tipo '{tipo}' desconhecido (use {', '.join(SPEC_TIPOS)})")
        regra = SPEC_TIPOS[tipo]
        dur = c.get("duracao")
        if not isinstance(dur, (int, float)) or dur < regra["min"]:
            raise SpecErro(f"{onde} ({tipo}): duracao deve ser número >= {regra['min']} s")
        total += dur
        for campo in regra["campos"]:
            if campo not in c:
                raise SpecErro(f"{onde} ({tipo}): falta o campo '{campo}'")
        permitidos = set(regra["campos"]) | set(regra["opcionais"]) | {"tipo", "duracao", "fala"}
        extras = set(c) - permitidos
        if extras:
            raise SpecErro(f"{onde} ({tipo}): campos que este tipo não usa: {sorted(extras)}")
        for campo in regra["campos"] + regra["opcionais"]:
            if campo in TEXTOS and campo in c:
                _linhas(c[campo], f"{onde}.{campo}")
        if "cores" in c and not (isinstance(c["cores"], list) and len(c["cores"]) == 2
                                 and all(x in CORES for x in c["cores"])):
            raise SpecErro(f"{onde}: 'cores' precisa ter 2 nomes válidos (use {sorted(CORES)})")
        if tipo == "gancho":
            if not (isinstance(c["numeros"], list) and len(c["numeros"]) == 2):
                raise SpecErro(f"{onde}: 'numeros' precisa ter exatamente 2 textos (ex.: [\"3%\", \"15%\"])")
            for x in c["numeros"]:
                if len(x) > 8:
                    raise SpecErro(f"{onde}: número \"{x}\" longo demais para o cartão")
        if tipo in ("barras", "barras_horizontais"):
            barras = c["barras"]
            limite = 3 if tipo == "barras" else 2  # acima disso os rótulos e as barras se sobrepõem no layout
            if not (isinstance(barras, list) and 1 <= len(barras) <= limite):
                raise SpecErro(f"{onde}: 'barras' precisa ter de 1 a {limite} itens")
            for b in barras:
                if not isinstance(b.get("valor"), (int, float)) or b["valor"] < 0:
                    raise SpecErro(f"{onde}: cada barra precisa de 'valor' numérico >= 0")
                if b.get("cor", "azul") not in CORES:
                    raise SpecErro(f"{onde}: cor de barra inválida: {b.get('cor')}")
                _linhas(b.get("rotulo", ""), f"{onde}.barras.rotulo")
            if tipo == "barras":
                if not c["escala_max"] or c["escala_max"] <= 0:
                    raise SpecErro(f"{onde}: 'escala_max' precisa ser > 0")
                for b in barras:
                    if b["valor"] > c["escala_max"]:
                        raise SpecErro(f"{onde}: valor {b['valor']} acima de escala_max {c['escala_max']}")
            else:
                for b in barras:
                    if b["valor"] > 100:
                        raise SpecErro(f"{onde}: em barras_horizontais o valor vai de 0 a 100")
    if not 20 <= total <= 60:
        raise SpecErro(f"duração total {total:.1f} s fora do formato Short (20 a 60 s)")
    return total


def render(out, cenas_path=None, voz_cfg=None):
    """Narra (se houver campo 'fala'), renderiza frames, gera o áudio e codifica out/video.mp4.
    A duração de cada cena passa a ser a da fala quando ela é maior que a duracao escrita."""
    cenas_path = Path(cenas_path or out / "cenas.json")
    cenas = json.loads(cenas_path.read_text(encoding="utf-8"))
    validate(cenas)

    falas = {}
    if voz.tem_falas(cenas):
        print("   narrando as cenas (Chatterbox, CPU; leva alguns minutos)...", flush=True)
        falas = voz.gerar(out, cenas_path, voz_cfg)
    spec = []
    for i, c in enumerate(cenas):
        d = float(c["duracao"])
        if str(i) in falas:
            d = max(d, falas[str(i)]["dur"] + 0.6)  # 0,6 s de respiro depois da fala
        spec.append({**c, "duracao": round(d, 3)})
    total_s = validate(spec)
    spec_path = out / "cenas_render.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")

    _node_render(spec_path, out)
    eventos = json.loads((out / "eventos.json").read_text(encoding="utf-8"))
    inicios, t = [], 0.0
    for c in spec:
        inicios.append(t)
        t += c["duracao"]
    falas_mix = [(inicios[int(k)] + 0.3, v["wav"]) for k, v in falas.items()]
    sfx.build(eventos["eventos"], eventos["total"], eventos["fps"], out / "audio.wav", falas=falas_mix)
    video = _encode(out, eventos["total"], eventos["fps"])
    _thumbnail(out)
    shutil.rmtree(out / "frames", ignore_errors=True)  # os PNGs ocupam muito espaço; o MP4 é o que importa
    print(f"   vídeo: {video.name} ({total_s:.0f} s, {eventos['total']} frames, {eventos['fps']} fps"
          f"{', com narração' if falas else ''})")
    return video


def _node_render(cenas_path, out):
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Node.js não encontrado no PATH. Instale o Node para renderizar o vídeo.")
    if not (RENDER / "node_modules").exists():
        raise SystemExit(f"Dependências do motor não instaladas. Rode: cd {RENDER} && npm install")
    run(["node", "render.mjs", "--spec", str(cenas_path.resolve()), "--out", str(out.resolve())], cwd=RENDER)


def _encode(out, total_frames, fps):
    video = out / "video.mp4"
    dur = total_frames / fps
    run(["ffmpeg", "-y", "-framerate", str(fps), "-i", str(out / "frames" / "%04d.png"),
         "-i", str(out / "audio.wav"),
         "-map", "0:v", "-map", "1:a",
         "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-t", f"{dur:.3f}", "-movflags", "+faststart", str(video)], cwd=out)
    return video


def _thumbnail(out):
    """Miniatura = o frame 1,5 s (a ideia do gancho já na tela), convertido para JPEG."""
    src = out / "frames" / "0045.png"
    if src.exists():
        run(["ffmpeg", "-y", "-i", str(src), "-q:v", "3", str(out / "thumbnail.jpg")], cwd=out)
