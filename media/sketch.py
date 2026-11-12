"""Vídeo desenhado quadro a quadro em Python, conduzido pela narração: estilo sketch (papel de caderno, traço à mão) e os estilos
por dados de media/estilos.py (cena descrita no próprio cenas.json, sem sketch_cenas.py).

Entrada, em output/<slug>/:
- cenas.json: lista de cenas {"tipo": "sketch", "fala": "...", "duracao": N, "desenho": "cena_0", "rotulos": [...], "sons": [...]}.
  `duracao` é só o MÍNIMO: a cena dura o que a fala dura (+ respiro). `desenho` é o nome da função em sketch_cenas.py.
- sketch_cenas.py: as funções de desenho (escritas pelo Olise com media/sketch_lib.py), `def cena_N(lt, dur)`.

Saída: video.mp4, thumbnail.jpg, audio.wav, eventos.json, cenas_render.json (mesmo contrato do motor SVG).
O áudio vem primeiro: a narração é gerada antes dos quadros, e cada cena é desenhada no tempo da fala.

Formato: o `render` do config decide (vertical = Short 1080x1920 em config_shorts.yaml; horizontal = 1920x1080 em
config_horizontal.yaml). A faixa de duração total também vem do config (render.duracao_min_s / duracao_max_s).

Uso direto:  python -m media.sketch --slug <pasta> [--formato horizontal] [--previa] [--sem-voz]
  --previa   só desenha 3 quadros por cena e monta previa.jpg (sem voz, sem vídeo): serve para conferir o desenho.
  --sem-voz  estima a duração pelo texto e gera o vídeo mudo (teste do desenho; o canal sempre narra).
"""
import argparse
import importlib.util
import json
import multiprocessing as mp
import shutil
from pathlib import Path

import yaml
from PIL import Image

from . import estilos, motion, sfx, sketch_lib, voz
from .sketch_lib import definir_formato

ROOT = Path(__file__).resolve().parent.parent
MAX_LINHA = 26  # caracteres por rótulo na tela (mesmo limite do estilo SVG)
PALAVRAS_POR_S = 3.0  # só para estimar a duração quando não há voz (--sem-voz e --previa)
PERMITIDOS = {"tipo", "fala", "duracao", "desenho", "rotulos", "sons"}
SONS_OK = {"impact", "ding", "whoosh"}
CONFIGS = {"vertical": "config_shorts.yaml", "horizontal": "config_horizontal.yaml"}
LIMITES_PADRAO = (20.0, 60.0)  # Short: 20 a 60 s


def carregar_config(formato="vertical"):
    """Config do formato: o do Short é a base; o horizontal sobrepõe só o que muda (um nível: render, channel...)."""
    cfg = yaml.safe_load(open(ROOT / CONFIGS["vertical"], encoding="utf-8"))
    if formato != "vertical":
        for chave, valor in yaml.safe_load(open(ROOT / CONFIGS[formato], encoding="utf-8")).items():
            cfg[chave] = {**cfg.get(chave, {}), **valor} if isinstance(valor, dict) else valor
    return cfg


def limites(render_cfg=None):
    """Faixa (mín, máx) da duração total, em segundos, para o formato do config."""
    r = render_cfg or {}
    return float(r.get("duracao_min_s", LIMITES_PADRAO[0])), float(r.get("duracao_max_s", LIMITES_PADRAO[1]))


class SpecErro(SystemExit):
    pass


def _estimar(c):
    return len(c["fala"].split()) / PALAVRAS_POR_S + 0.2


def validate(cenas, limite=LIMITES_PADRAO):
    """Confere o cenas.json do estilo sketch. Devolve a duração total estimada (s). Erro aponta cena e campo.
    `limite` = (mín, máx) da duração total do formato (ver limites())."""
    if not isinstance(cenas, list) or not cenas:
        raise SpecErro("cenas.json: lista vazia ou não é uma lista")
    total = 0.0
    ident = estilos.do_tipo(cenas[0].get("tipo"))
    por_dados = estilos.por_dados(ident)
    biblioteca = estilos.lib(ident) if por_dados else None
    for i, c in enumerate(cenas, 1):
        onde = f"cena {i}"
        if por_dados:
            if c.get("tipo") != ident:
                raise SpecErro(f"{onde}: todas as cenas do vídeo devem ter o tipo '{ident}' (veio '{c.get('tipo')}')")
            extras = set(c) - PERMITIDOS - biblioteca.CAMPOS
            if extras:
                raise SpecErro(f"{onde}: campos que o estilo {ident} não usa: {sorted(extras)}")
            try:
                biblioteca.validar(c, onde)
            except ValueError as ex:
                raise SpecErro(str(ex))
        else:
            if c.get("tipo") != "sketch":
                raise SpecErro(f"{onde}: tipo deve ser 'sketch' (veio '{c.get('tipo')}')")
            extras = set(c) - PERMITIDOS
            if extras:
                raise SpecErro(f"{onde}: campos que o estilo sketch não usa: {sorted(extras)}")
        if not isinstance(c.get("fala"), str) or not c["fala"].strip():
            raise SpecErro(f"{onde}: falta a 'fala' (a narração é obrigatória em todo vídeo)")
        dur = c.get("duracao")
        if not isinstance(dur, (int, float)) or dur < 2.5:
            raise SpecErro(f"{onde}: 'duracao' (mínimo da cena) deve ser número >= 2.5 s")
        if not isinstance(c.get("desenho"), str) or not c["desenho"].isidentifier():
            raise SpecErro(f"{onde}: 'desenho' deve ser o nome de uma função em sketch_cenas.py (ex.: \"cena_0\")")
        for r in c.get("rotulos", []):
            if not isinstance(r, str) or not r.strip() or len(r) > MAX_LINHA:
                raise SpecErro(f"{onde}: rótulo inválido ou longo demais (máx. {MAX_LINHA} caracteres): {r!r}")
        for s in c.get("sons", []):
            if s.get("tipo") not in SONS_OK or not isinstance(s.get("t"), (int, float)):
                raise SpecErro(f"{onde}: 'sons' aceita {{\"t\": segundos, \"tipo\": {sorted(SONS_OK)}}}")
        total += max(dur, _estimar(c))
    if por_dados and len({c["desenho"] for c in cenas}) != len(cenas):
        raise SpecErro("cenas.json: 'desenho' é o id da cena e não pode repetir")
    lo, hi = limite
    if not lo <= total <= hi + 2:
        raise SpecErro(f"duração estimada {total:.0f} s fora do formato (de {lo:.0f} a {hi:.0f} s)")
    return total


def fonte_desenho(out, cenas):
    """De onde vêm as funções `cena_N`: do sketch_cenas.py ou, nos estilos por dados, do próprio cenas.json."""
    out = Path(out)
    return out / "cenas.json" if estilos.por_dados(estilos.das_cenas(cenas)) else out / "sketch_cenas.py"


def _variante(out):
    """A variação escolhida no projeto. Projeto antigo não tem estilo.json: nada muda."""
    e = estilos.ler(out) or {}
    return (e.get("variante"), e.get("opcoes")) if e.get("estilo") == "sketch" else (None, None)


def _carregar(caminho):
    caminho = Path(caminho)
    if caminho.suffix == ".json":
        return estilos.modulo_dados(caminho)
    spec = importlib.util.spec_from_file_location("sketch_cenas", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_G = {}


def _iniciar(caminho, tabela, fps, pasta, formato, variante=(None, None)):
    definir_formato(formato)  # antes de carregar: sketch_cenas.py importa a biblioteca com W e H do formato
    sketch_lib.definir_variante(*variante)
    _G.update(mod=_carregar(caminho), tabela=tabela, fps=fps, pasta=Path(pasta))


def _quadro(f):
    t = f / _G["fps"]
    nome, ini, dur = _G["tabela"][-1]
    for n, i, d in _G["tabela"]:
        if t < i + d:
            nome, ini, dur = n, i, d
            break
    im = getattr(_G["mod"], nome)(max(0.0, t - ini), dur)
    if im.size != (sketch_lib.W, sketch_lib.H):
        raise SpecErro(f"{nome}: a função deve devolver imagem {sketch_lib.W}x{sketch_lib.H}, devolveu {im.size}")
    im.convert("RGB").save(_G["pasta"] / f"{f + 1:04d}.png", compress_level=1)
    return f


def _falas_salvas(out, cenas):
    """Narração já gerada para exatamente estas falas (falas/textos.json igual): refazer só o desenho
    não gera a voz de novo, e cada cena mantém a duração."""
    pasta = out / "falas"
    try:
        textos = json.loads((pasta / "textos.json").read_text(encoding="utf-8"))
        falas = json.loads((pasta / "falas.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if textos != [c["fala"] for c in cenas]:
        return {}
    if not all(str(i) in falas and Path(falas[str(i)]["wav"]).exists() for i in range(len(cenas))):
        return {}
    return falas


def _tabela(cenas, durs):
    tabela, t = [], 0.0
    for c, d in zip(cenas, durs):
        tabela.append((c["desenho"], t, d))
        t += d
    return tabela


def previa(out, cenas_path=None, formato="vertical", render_cfg=None):
    """3 quadros por cena (25%, 60%, 95%) numa folha de contato: previa.jpg. Sem voz, sem vídeo."""
    out = Path(out)
    cenas_path = Path(cenas_path or out / "cenas.json")
    cenas = json.loads(cenas_path.read_text(encoding="utf-8"))
    validate(cenas, limites(render_cfg))
    definir_formato(formato)
    sketch_lib.definir_variante(*_variante(out))
    mod = _carregar(fonte_desenho(out, cenas))
    durs = [max(float(c["duracao"]), _estimar(c)) for c in cenas]
    miniatura = (sketch_lib.W // 5, sketch_lib.H // 5)
    colunas = 6  # duas cenas por linha
    linhas = (len(cenas) + 1) // 2
    folha = Image.new("RGB", (miniatura[0] * colunas, miniatura[1] * linhas), (255, 255, 255))
    for i, (c, d) in enumerate(zip(cenas, durs)):
        for k, p in enumerate((0.25, 0.60, 0.95)):
            im = getattr(mod, c["desenho"])(d * p, d).convert("RGB").resize(miniatura, Image.LANCZOS)
            col = (i % 2) * 3 + k
            folha.paste(im, (col * miniatura[0], (i // 2) * miniatura[1]))
    destino = out / "previa.jpg"
    folha.save(destino, quality=88)
    print(f"   prévia: {destino} ({len(cenas)} cenas, 3 quadros cada)")
    return destino


def render(out, cenas_path=None, voz_cfg=None, fps=30, sem_voz=False, render_cfg=None):
    """Narra primeiro, mede cada fala, desenha cada cena no tempo dela e codifica out/video.mp4.
    `render_cfg` (bloco `render` do config) define o formato (`formato`: vertical ou horizontal) e a faixa de duração."""
    out = Path(out)
    formato = (render_cfg or {}).get("formato", "vertical")
    definir_formato(formato)
    cenas_path = Path(cenas_path or out / "cenas.json")
    cenas = json.loads(cenas_path.read_text(encoding="utf-8"))
    lo, hi = limites(render_cfg)
    validate(cenas, (lo, hi))
    variante = _variante(out)
    sketch_lib.definir_variante(*variante)
    codigo = fonte_desenho(out, cenas)
    if not codigo.exists():
        raise SpecErro(f"Falta {codigo}. Peça ao Olise (Short) ou ao Barcola (horizontal) as funções de desenho.")
    mod = _carregar(codigo)
    for i, c in enumerate(cenas, 1):
        if not callable(getattr(mod, c["desenho"], None)):
            raise SpecErro(f"cena {i}: a função '{c['desenho']}' não existe em {codigo.name}")

    falas = {}
    if not sem_voz:
        falas = _falas_salvas(out, cenas)
        if falas:
            print("   reaproveitando a narração já gerada (as falas não mudaram)", flush=True)
        else:
            print("   narrando as cenas (Chatterbox, CPU; leva alguns minutos)...", flush=True)
            falas = voz.gerar(out, cenas_path, voz_cfg)
            (out / "falas" / "textos.json").write_text(
                json.dumps([c["fala"] for c in cenas], ensure_ascii=False, indent=1), encoding="utf-8")
    inicio_s = float((voz_cfg or {}).get("inicio_s", 0.05))
    respiro_s = float((voz_cfg or {}).get("respiro_s", 0.12))
    durs = []
    for i, c in enumerate(cenas):
        fala_s = falas[str(i)]["dur"] if str(i) in falas else _estimar(c)
        durs.append(round(max(float(c["duracao"]), inicio_s + fala_s + respiro_s), 3))
    total_s = sum(durs)
    if not lo <= total_s <= hi:
        raise SpecErro(f"duração total {total_s:.1f} s fora do formato (de {lo:.0f} a {hi:.0f} s). Ajuste as falas.")
    (out / "cenas_render.json").write_text(
        json.dumps([{**c, "duracao": d} for c, d in zip(cenas, durs)], ensure_ascii=False, indent=1), encoding="utf-8")

    tabela = _tabela(cenas, durs)
    total_frames = round(total_s * fps)
    frames = out / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir()
    print(f"   desenhando {total_frames} quadros ({total_s:.1f} s, {fps} fps)...", flush=True)
    with mp.Pool(min(8, mp.cpu_count()), initializer=_iniciar, initargs=(str(codigo), tabela, fps, str(frames), formato, variante)) as pool:
        for n, _ in enumerate(pool.imap_unordered(_quadro, range(total_frames), chunksize=8), 1):
            if n % 300 == 0:
                print(f"   {n}/{total_frames}", flush=True)

    eventos = []
    for i, (c, (_, ini, _)) in enumerate(zip(cenas, tabela)):
        if i > 0:
            eventos.append({"frame": round(ini * fps), "kind": "whoosh"})  # corte seco entre cenas
        for s in c.get("sons", []):
            eventos.append({"frame": round((ini + s["t"]) * fps), "kind": s["tipo"]})
    eventos = [e for e in eventos if 0 <= e["frame"] < total_frames]
    (out / "eventos.json").write_text(json.dumps({"total": total_frames, "fps": fps, "eventos": eventos}, indent=1), encoding="utf-8")
    falas_mix = [(tabela[int(k)][1] + inicio_s, v["wav"]) for k, v in falas.items()]
    sfx.build(eventos, total_frames, fps, out / "audio.wav", falas=falas_mix)
    video = motion._encode(out, total_frames, fps)
    motion._thumbnail(out)
    shutil.rmtree(frames, ignore_errors=True)
    print(f"   vídeo: {video.name} ({total_s:.0f} s, {total_frames} frames, {fps} fps"
          f"{', com narração' if falas else ', mudo (teste)'})")
    return video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--formato", choices=sorted(CONFIGS), default="vertical")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-voz", action="store_true")
    a = ap.parse_args()
    cfg = carregar_config(a.formato)
    out = ROOT / "output" / a.slug
    if a.previa:
        previa(out, formato=a.formato, render_cfg=cfg["render"])
    else:
        render(out, voz_cfg=cfg.get("voz"), fps=cfg["render"]["fps"], sem_voz=a.sem_voz, render_cfg=cfg["render"])


if __name__ == "__main__":
    main()
