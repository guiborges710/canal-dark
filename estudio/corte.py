"""Editor de vídeo: o estado do corte (output/<slug>/corte.json), a compilação numa linha do tempo e os conflitos com o que os agentes geram.

Só existe uma compilação: `compilar()`. A prévia e o export recebem o mesmo resultado, em quadros, e desenham com o mesmo
web/compositor.js; o áudio sai do mesmo `mixar()`. É isso que faz o MP4 conferir com a prévia no mesmo timecode.

O corte aponta para os originais por conteúdo (sha): o que um agente refizer só entra quando o Guilherme aplicar. Sem edição
não existe corte.json: abrir o editor lê o projeto sem gravar nada nele, e o `run.py` nunca lê este arquivo.
"""
import ast
import hashlib
import json
import re
import subprocess
import tempfile
import wave
from pathlib import Path

from media import estilos

from . import materiais as M
from .banco import agora, faz, um, varios
from .config import DADOS, REPO, SAIDA
from .fluxo import Recusado, slugify

ARQUIVO = "corte.json"
PASTA_ASSETS = "corte_assets"
MINIATURAS = DADOS / "miniaturas"
AUDIOS = DADOS / "audios_previa"
SCHEMA = 1
ESTILOS_LEGENDA = {"viral", "caderno", "cartao"}
PRESETS_LEGENDA = {
    "nenhum": {"nome": "Sem legenda", "detalhe": "Padrão do estilo sketch: o texto já faz parte do desenho."},
    "viral": {"nome": "Viral", "detalhe": "Poucas palavras, fonte pesada e contorno grosso (o mesmo de media/captions.py).", "palavras": 3},
    "caderno": {"nome": "Caderno", "detalhe": "Letra Kalam, a mesma do traço do sketch.", "palavras": 6},
    "cartao": {"nome": "Cartão", "detalhe": "Cartão branco com contorno grafite e sombra sólida, como o motor SVG.", "palavras": 5},
}
Y_LEGENDA = 1380  # dentro de SEGURO_BASE (media/sketch_lib.py): a base da tela fica coberta pela interface do app
FAIXAS_ESTADO = ("cenas", "narracao", "legendas")


def _cfg(slug):
    from media.sketch import carregar_config
    p = um("SELECT formato FROM producoes WHERE slug=?", slug) or {}
    return carregar_config(p.get("formato") or "vertical")


def caminho(slug):
    return M.pasta(slug) / ARQUIVO


def assinatura(estado):
    """O que importa para o resultado: `rev` e `atualizado_em` não mudam o vídeo."""
    limpo = {k: v for k, v in estado.items() if k not in ("rev", "atualizado_em")}
    return M.sha_texto(json.dumps(limpo, sort_keys=True, ensure_ascii=False))


# ---------- Fontes: de onde vem a imagem e o som de cada cena ----------

def _funcoes(fonte_py):
    """{função: hash do código} e o hash do resto do arquivo. É assim que mudar uma cena não invalida as outras."""
    try:
        arvore = ast.parse(fonte_py)
    except SyntaxError:
        return {}, M.sha_texto(fonte_py)
    funcoes, resto = {}, []
    for no in arvore.body:
        trecho = ast.get_source_segment(fonte_py, no) or ""
        if isinstance(no, ast.FunctionDef) and re.fullmatch(r"cena_\w+", no.name):
            funcoes[no.name] = M.sha_texto(trecho)
        else:
            resto.append(trecho)
    return funcoes, M.sha_texto("\n".join(resto))


def _hash_desenhos(slug):
    p = M.pasta(slug)
    cenas = M.ler_cenas(slug)
    ident = estilos.das_cenas(cenas)
    if estilos.por_dados(ident):  # a função da cena é a própria cena: muda se ela mudar, ou se a biblioteca que desenha mudar
        loop = estilos.assinatura_cena(cenas[0])  # só quem fecha em loop mostra a primeira cena
        funcoes = {c["desenho"]: M.sha_texto(estilos.assinatura_cena(c) + (loop if (c.get("transicao") or {}).get("saida") == "loop" else "")) for c in cenas}
        libs = estilos.obter(ident)["lib"].split(".")[-1]
        return funcoes, M.sha_texto(M.ler_texto(REPO / "media" / f"{libs}.py") + M.ler_texto(REPO / "media" / "camadas.py"))
    f = p / "sketch_cenas.py"
    if not f.exists():
        return {}, None
    funcoes, resto = _funcoes(M.ler_texto(f))
    extra = p / "componentes_video.py"
    variacao = estilos.ler(p) or {}
    return funcoes, M.sha_texto(resto + (M.ler_texto(extra) if extra.exists() else "") + (json.dumps([variacao["variante"], variacao.get("opcoes")], sort_keys=True) if variacao.get("variante") else ""))


def chave_fonte(slug, desenho, dur, fps, formato, funcoes=None, resto=None):
    """Identifica o clipe desenhado. Mudar outra cena do sketch_cenas.py não muda esta chave."""
    if funcoes is None:
        funcoes, resto = _hash_desenhos(slug)
    if desenho not in funcoes:
        return None
    return M.sha_texto(json.dumps([funcoes[desenho], resto, round(float(dur), 3), fps, formato]))


def _wav_conforme(origem, de=None, dur=None):
    """Guarda como WAV 48 kHz mono, o formato que o media/sfx.py mistura. Devolve o sha. O wav de fala do Chatterbox já vem assim."""
    origem = Path(origem)
    if de is None and origem.suffix.lower() == ".wav":
        try:
            with wave.open(str(origem), "rb") as w:
                if w.getframerate() == 48000 and w.getnchannels() == 1 and w.getsampwidth() == 2:
                    sha = M.sha_arquivo(origem)
                    M.guardar_blob(origem, sha)
                    return sha
        except wave.Error:
            pass
    with tempfile.TemporaryDirectory() as d:
        destino = Path(d) / "a.wav"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(origem), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(destino)]
        r = subprocess.run(cmd, capture_output=True, creationflags=0x08000000)
        if r.returncode != 0 or not destino.exists():
            return None
        sha = M.sha_arquivo(destino)
        M.guardar_blob(destino, sha)
    return sha


def _dur_midia(caminho_arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(caminho_arq)],
                       capture_output=True, text=True, creationflags=0x08000000)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _id_cena(c, i, usados):
    base = "cn-" + (c.get("desenho") or f"{i}-{slugify(str(c.get('tipo') or 'cena'))}")
    novo, n = base, 2
    while novo in usados:
        novo, n = f"{base}-{n}", n + 1
    usados.add(novo)
    return novo


def _item_narracao(id_cena, sha, arquivo, dur, desloc, fonte_ini=0.0):
    return {"id": "na-" + id_cena[3:], "cena": id_cena, "sha": sha, "arquivo": arquivo, "dur": round(float(dur), 3), "desloc": desloc, "fonte_ini": round(float(fonte_ini), 3),
            "vinculada": True, "inicio": None, "volume_db": 0.0}


def importar(slug):
    """Monta o corte inicial a partir do que o projeto tem, sem gravar nada em output/. Procura primeiro a composição anterior ao
    render (cenas, sketch_cenas.py e falas). Só o MP4 achatado permite só as operações sobre o vídeo inteiro: `faltam` diz o que abriria as outras."""
    from .fluxo import garantir_producao
    prod = garantir_producao(slug)
    p = M.pasta(slug)
    cfg = _cfg(slug)
    r, voz = cfg["render"], cfg.get("voz") or {}
    fps, w, h, formato = int(r["fps"]), int(r["width"]), int(r["height"]), r.get("formato", "vertical")
    cenas = M.ler_cenas(slug)
    video = p / "video.mp4"
    video_sha = None
    if video.exists():
        video_sha = M.sha_arquivo(video)
        M.guardar_blob(video, video_sha)
    falas = M.falas(slug)
    feitas = M.ler_json(p / "cenas_render.json", None)
    tempos, exato = M.tempos_cenas(slug, cenas) if cenas else ([], False)
    if isinstance(feitas, list) and cenas and len(feitas) == len(cenas) and estilos.por_quadros(M.estilo_das_cenas(slug)):
        exato = exato or all(c.get("fala") == x.get("fala") for c, x in zip(cenas, feitas))
    funcoes, resto = _hash_desenhos(slug)
    e_sketch = estilos.por_quadros(M.estilo_das_cenas(slug)) and bool(funcoes) and all(c.get("desenho") in funcoes for c in cenas)
    video_dur = _dur_midia(video) if video.exists() else 0.0
    if cenas and video_sha and not e_sketch and tempos and abs(sum(t["dur"] for t in tempos) - video_dur) > 0.6:
        exato = False  # a soma não bate com o vídeo: recortar por cena cairia em lugar errado
    estado = {"schema": SCHEMA, "rev": 0, "slug": slug, "w": w, "h": h, "fps": fps, "formato": formato, "modo": "cenas", "faltam": [], "video_base": video_sha,
              "cenas": [], "narracao": {"volume_db": 0.0, "itens": []}, "legendas": {"preset": prod.get("legenda") or "nenhum", "itens": []}, "pins": {}}
    if not cenas or not (e_sketch or (video_sha and exato)):
        return _importar_video_unico(estado, slug, video, video_sha, video_dur, bool(cenas))
    usados = set()
    inicio_voz = float(voz.get("inicio_s", 0.05))
    audio_inteiro = None
    if not falas and (p / "audio.wav").exists() and not e_sketch:
        audio_inteiro = _wav_conforme(p / "audio.wav")
    elif not falas and video_sha and not e_sketch:
        audio_inteiro = _wav_conforme(video)
    for i, c in enumerate(cenas):
        ident = _id_cena(c, i, usados)
        dur = round(float(tempos[i]["dur"]), 3)
        if e_sketch:
            fonte = {"tipo": "sketch", "desenho": c["desenho"], "chave": chave_fonte(slug, c["desenho"], dur, fps, formato, funcoes, resto), "dur": dur,
                     "video": video_sha, "ini": tempos[i]["inicio"] if exato else None}
        else:
            fonte = {"tipo": "video", "sha": video_sha, "ini": tempos[i]["inicio"], "dur": dur}
        estado["cenas"].append({"id": ident, "i": i, "rotulo": f"Cena {i + 1}", "fala": M.fala_de(c), "fonte": fonte, "in": 0.0, "out": dur, "congela": 0.0,
                                "midia": None, "quadro": {"escala": 1.0, "x": 0.0, "y": 0.0}, "sons": [s for s in c.get("sons", []) if isinstance(s, dict)] if e_sketch else []})
        if i in falas:
            sha = _wav_conforme(falas[i]["arquivo"])
            if sha:
                estado["narracao"]["itens"].append(_item_narracao(ident, sha, falas[i]["arquivo"].name, falas[i]["dur"] or _dur_midia(falas[i]["arquivo"]), inicio_voz))
        elif audio_inteiro:  # cartões sem falas por cena: o som da cena é o trecho dela no áudio do vídeo
            estado["narracao"]["itens"].append(_item_narracao(ident, audio_inteiro, "audio.wav", dur, 0.0, tempos[i]["inicio"]))
    estado["som_cortes"] = e_sketch  # o whoosh entre cenas é do sketch; no áudio inteiro ele já está gravado
    _gerar_legendas(estado)
    estado["pins"] = pins_atuais(slug)
    return estado


def _importar_video_unico(estado, slug, video, sha, dur, tem_cenas):
    if not sha:
        raise Recusado("Este projeto ainda não tem material para editar: falta o cenas.json com sketch_cenas.py ou um video.mp4.", 409)
    estado["modo"] = "video_unico"
    estado["faltam"] = ["Reordenar cenas, trocar asset e separar a fala por cena exigem cenas.json com a duração real de cada cena"
                        + (" (o que existe aqui não bate com o vídeo, ou é de formato antigo)" if tem_cenas else "") + " e falas/falas.json."]
    ident = "cn-video"
    fonte = {"tipo": "video", "sha": sha, "ini": 0.0, "dur": round(dur, 3)}
    estado["cenas"].append({"id": ident, "i": 0, "rotulo": "Vídeo inteiro", "fala": "", "fonte": fonte, "in": 0.0, "out": round(dur, 3), "congela": 0.0, "midia": None,
                            "quadro": {"escala": 1.0, "x": 0.0, "y": 0.0}, "sons": []})
    audio = _wav_conforme(video)
    if audio:
        estado["narracao"]["itens"].append(_item_narracao(ident, audio, "video.mp4", dur, 0.0))
    estado["som_cortes"] = False
    estado["pins"] = {"video": sha}
    return estado


def pins_atuais(slug):
    """Foto do que o projeto tem agora. A diferença para a foto guardada no corte é o que os agentes mudaram depois."""
    funcoes, resto = _hash_desenhos(slug)
    falas = M.falas(slug)
    return {"falas": {str(i): v["sha"] for i, v in falas.items()}, "textos": [M.fala_de(c) for c in M.ler_cenas(slug)], "desenhos": funcoes, "aux": resto}


def _gerar_legendas(estado):
    """Só as legendas automáticas: a que o Guilherme tocou fica com manual=True e nunca é refeita."""
    preset = estado["legendas"].get("preset") or "nenhum"
    manuais = [x for x in estado["legendas"]["itens"] if x.get("manual")]
    if preset == "nenhum":
        estado["legendas"]["itens"] = manuais
        return
    por_cena = {n["cena"]: n for n in estado["narracao"]["itens"]}
    palavras = PRESETS_LEGENDA[preset]["palavras"]
    novos = []
    cenas_manuais = {x.get("cena") for x in manuais}
    for c in estado["cenas"]:
        if c["id"] in cenas_manuais or not c.get("fala"):
            continue
        n = por_cena.get(c["id"])
        falado = float(n["dur"]) if n else (c["out"] - c["in"])
        ini = float(n["desloc"]) if n else 0.0
        texto = c["fala"].split()
        blocos = [texto[k:k + palavras] for k in range(0, len(texto), palavras)]
        cur = ini
        for k, bloco in enumerate(blocos):
            d = falado * len(bloco) / len(texto)  # mesma conta de media/captions.py build_cues: sem tempo por palavra, o tempo é proporcional
            novos.append({"id": f"le-{c['id'][3:]}-{k}", "cena": c["id"], "ini": round(cur, 3), "fim": round(cur + d, 3), "texto": " ".join(bloco), "x": estado["w"] / 2,
                          "y": Y_LEGENDA if estado["h"] > estado["w"] else estado["h"] - 170, "estilo": preset, "manual": False})
            cur += d
    estado["legendas"]["itens"] = manuais + novos


# ---------- Leitura, gravação e validação ----------

def carregar(slug):
    """O corte salvo, ou o inicial se ainda não houve edição."""
    f = caminho(slug)
    if f.exists():
        e = M.ler_json(f, None)
        if isinstance(e, dict) and e.get("schema") == SCHEMA:
            return e
        raise Recusado(f"{f.name} está ilegível ou é de outra versão. Restaure uma versão de corte ou apague o arquivo para recomeçar.")
    return importar(slug)


def _numero(v, nome, minimo=None, maximo=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise Recusado(f"{nome}: valor inválido.", 400)
    v = float(v)
    if minimo is not None:
        v = max(minimo, v)
    if maximo is not None:
        v = min(maximo, v)
    return round(v, 3)


def _validar(novo, base):
    """O navegador só pode mudar decisões de edição. De onde vem cada arquivo (sha, fonte) continua sendo o que o servidor conhece."""
    if not isinstance(novo, dict):
        raise Recusado("Corte inválido.", 400)
    cenas_base = {c["id"]: c for c in base["cenas"]}
    ids = [c.get("id") for c in novo.get("cenas", [])]
    if sorted(ids) != sorted(cenas_base):
        raise Recusado("O corte precisa ter as mesmas cenas: elas se reordenam, não somem. Para tirar uma cena, reduza a duração ou peça o ajuste ao agente.", 400)
    if base["modo"] == "video_unico" and len(ids) != 1:
        raise Recusado("Este projeto só tem o MP4 achatado.", 400)
    saida = dict(base)
    saida["cenas"] = []
    for c in novo["cenas"]:
        b = cenas_base[c["id"]]
        dur_fonte = float(b["fonte"]["dur"])
        ent = _numero(c.get("in", 0), "início", 0, max(0, dur_fonte - 1 / base["fps"]))
        sai = _numero(c.get("out", dur_fonte), "fim", ent + 1 / base["fps"], dur_fonte)
        cong = _numero(c.get("congela", 0), "quadro congelado", 0, 120)
        q = c.get("quadro") or {}
        quadro = {"escala": _numero(q.get("escala", 1), "escala", 0.2, 5), "x": _numero(q.get("x", 0), "x", -4000, 4000), "y": _numero(q.get("y", 0), "y", -4000, 4000)}
        midia = None
        if c.get("midia"):
            m = c["midia"]
            sha = str(m.get("sha") or "")
            if not re.fullmatch(r"[0-9a-f]{64}", sha) or not M.caminho_blob(sha).exists():
                raise Recusado(f"{b['rotulo']}: o asset escolhido não existe no projeto.", 400)
            if base["modo"] == "video_unico":
                raise Recusado("Trocar asset exige o projeto por cenas.", 400)
            midia = {"sha": sha, "nome": str(m.get("nome") or "")[:120], "origem": str(m.get("origem") or "")[:200], "w": _numero(m.get("w", 0), "largura", 0, 20000), "h": _numero(m.get("h", 0), "altura", 0, 20000),
                     "escala": _numero(m.get("escala", 1), "escala do asset", 0.05, 8), "x": _numero(m.get("x", base["w"] / 2), "x do asset", -4000, 6000), "y": _numero(m.get("y", base["h"] / 2), "y do asset", -4000, 6000),
                     "modo": "cobre" if m.get("modo") == "cobre" else "sobre"}
        saida["cenas"].append({**b, "in": ent, "out": sai, "congela": cong, "quadro": quadro, "midia": midia})
    na = novo.get("narracao") or {}
    itens_base = {n["id"]: n for n in base["narracao"]["itens"]}
    itens = []
    for n in na.get("itens", []):
        b = itens_base.get(n.get("id"))
        if not b:
            raise Recusado("Item de narração desconhecido.", 400)
        vinc = bool(n.get("vinculada", True))
        itens.append({**b, "vinculada": vinc, "inicio": None if vinc else _numero(n.get("inicio") or 0, "início da narração", 0, 3600), "desloc": _numero(n.get("desloc", b["desloc"]), "deslocamento", -30, 60),
                      "volume_db": _numero(n.get("volume_db", 0), "volume", -60, 12)})
    if {n["id"] for n in itens} != set(itens_base):
        raise Recusado("A narração precisa ter os mesmos trechos.", 400)
    saida["narracao"] = {"volume_db": _numero(na.get("volume_db", 0), "volume da narração", -60, 12), "itens": itens}
    le = novo.get("legendas") or {}
    preset = le.get("preset", "nenhum")
    if preset not in PRESETS_LEGENDA:
        raise Recusado("Estilo de legenda não suportado.", 400)
    legendas, vistos = [], set()
    for x in le.get("itens", []):
        lid = str(x.get("id") or "")
        if not re.fullmatch(r"[\w.-]{1,80}", lid) or lid in vistos:
            raise Recusado("Legenda com identificador inválido.", 400)
        vistos.add(lid)
        ini = _numero(x.get("ini", 0), "início da legenda", 0, 3600)
        fim = _numero(x.get("fim", ini + 1), "fim da legenda", ini + 1 / base["fps"], 3700)
        cena = x.get("cena")
        if cena is not None and cena not in cenas_base:
            raise Recusado("Legenda ligada a uma cena que não existe.", 400)
        if x.get("estilo") not in ESTILOS_LEGENDA:
            raise Recusado("Estilo de legenda não suportado.", 400)
        texto = str(x.get("texto") or "")
        if len(texto) > 300:
            raise Recusado("Legenda longa demais (máximo 300 caracteres).", 400)
        legendas.append({"id": lid, "cena": cena, "ini": ini, "fim": fim, "texto": texto, "x": _numero(x.get("x", base["w"] / 2), "x da legenda", -500, 5000), "y": _numero(x.get("y", Y_LEGENDA), "y da legenda", -500, 5000),
                         "estilo": x["estilo"], "manual": bool(x.get("manual"))})
    saida["legendas"] = {"preset": preset, "itens": legendas}
    return saida


def salvar(slug, novo, rev):
    """Salvamento automático. `rev` é a revisão em que a edição foi feita: duas abas não se sobrescrevem em silêncio."""
    base = carregar(slug)
    if rev != base.get("rev", 0):
        raise Recusado("Este corte mudou em outra aba ou por outra ação. Recarregue o editor para continuar.")
    regen = novo.get("legendas", {}).get("preset") != base["legendas"].get("preset")
    e = _validar(novo, base)
    if regen:
        _gerar_legendas(e)
    return _gravar(slug, e)


def _gravar(slug, e):
    e["rev"] = int(e.get("rev", 0)) + 1
    e["atualizado_em"] = agora()
    f = caminho(slug)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(f)
    return e


# ---------- Compilação: a mesma linha do tempo para prévia e render ----------

def duracao_cena(c):
    return round(c["out"] - c["in"] + c.get("congela", 0), 3)


def compilar(estado):
    """Resolve o corte em quadros. Tudo aqui é derivado do estado: não grava nada."""
    fps = estado["fps"]
    segs, f = [], 0
    por_id = {}
    for c in estado["cenas"]:
        n = max(1, round(duracao_cena(c) * fps))
        fonte = c["fonte"]
        sha, base_ini = _resolver_fonte(fonte)
        seg = {"cena": c["id"], "rotulo": c["rotulo"], "i": c["i"], "fala": c.get("fala", ""), "f0": f, "f1": f + n, "ini": round(f / fps, 4), "fim": round((f + n) / fps, 4), "fonte_sha": sha,
               "fonte_ok": bool(sha), "fonte_tipo": fonte["tipo"], "base_ini": round(round((base_ini + c["in"]) * fps) / fps, 4), "quadros_fonte": max(1, round((c["out"] - c["in"]) * fps)), "quadro": c.get("quadro") or {"escala": 1, "x": 0, "y": 0}, "midia": c.get("midia")}
        segs.append(seg)
        por_id[c["id"]] = seg
        f += n
    total_f = f
    total_s = total_f / fps
    avisos = []
    ganho_geral = float(estado["narracao"].get("volume_db", 0))
    audio = []
    for n in estado["narracao"]["itens"]:
        seg = por_id.get(n["cena"])
        c = next((x for x in estado["cenas"] if x["id"] == n["cena"]), None)
        dur = float(n["dur"])
        ganho = 10 ** ((ganho_geral + float(n.get("volume_db", 0))) / 20)
        if n.get("vinculada", True) and seg:
            # A fala acompanha a cena: aparar o início da cena corta o começo da fala, e ela para quando a cena acaba.
            rel = float(n["desloc"]) - c["in"]
            pos = seg["ini"] + max(0.0, rel)
            de = max(0.0, -rel)
            cabe = seg["fim"] - pos
            fala = max(0.0, dur - de)
            toca = min(fala, max(0.0, cabe))
            if de > 0.02:
                avisos.append({"tipo": "corte_fala", "cena": c["id"], "nivel": "alerta", "segundos": round(de, 2), "texto": f"{c['rotulo']}: o início aparado corta {de:.1f} s do começo da fala."})
            if fala - toca > 0.02:
                avisos.append({"tipo": "corte_fala", "cena": c["id"], "nivel": "alerta", "segundos": round(fala - toca, 2), "texto": f"{c['rotulo']}: a duração corta {fala - toca:.1f} s do fim da fala. Aumente a cena para {duracao_cena(c) + fala - toca:.2f} s para caber."})
        else:
            pos = float(n.get("inicio") or 0.0)
            de = 0.0
            toca = max(0.0, min(dur, total_s - pos))
            if dur - toca > 0.02:
                avisos.append({"tipo": "corte_fala", "cena": n["cena"], "nivel": "alerta", "segundos": round(dur - toca, 2), "texto": f"A narração de {seg['rotulo'] if seg else n['cena']} (solta da cena) passa do fim do vídeo em {dur - toca:.1f} s."})
        if toca > 0:
            audio.append({"id": n["id"], "cena": n["cena"], "sha": n["sha"], "pos": round(pos, 4), "de": round(float(n.get("fonte_ini", 0)) + de, 4), "dur": round(toca, 4), "ganho": round(ganho, 5), "vinculada": n.get("vinculada", True), "rotulo": seg["rotulo"] if seg else ""})
    fala_ordem = sorted(audio, key=lambda a: a["pos"])
    for a, b in zip(fala_ordem, fala_ordem[1:]):
        sobra = a["pos"] + a["dur"] - b["pos"]
        if sobra > 0.02:
            avisos.append({"tipo": "sobreposicao", "cena": b["cena"], "nivel": "alerta", "segundos": round(sobra, 2), "texto": f"{a['rotulo']} e {b['rotulo']}: {sobra:.1f} s de falas sobrepostas."})
    eventos = []
    for k, c in enumerate(estado["cenas"]):
        seg = por_id[c["id"]]
        if k > 0 and estado.get("som_cortes", True):
            eventos.append({"frame": seg["f0"], "kind": "whoosh"})
        for s in c.get("sons", []):
            t = float(s.get("t", 0))
            if c["in"] <= t < c["out"]:
                eventos.append({"frame": seg["f0"] + round((t - c["in"]) * fps), "kind": s.get("tipo")})
    eventos = [e for e in eventos if 0 <= e["frame"] < total_f]
    legendas = []
    for x in estado["legendas"]["itens"]:
        seg = por_id.get(x.get("cena")) if x.get("cena") else None
        ini = (seg["ini"] if seg else 0.0) + x["ini"]
        fim = (seg["ini"] if seg else 0.0) + x["fim"]
        limite = seg["fim"] if seg else total_s
        if fim - limite > 0.02 and ini < limite:
            avisos.append({"tipo": "legenda_cortada", "cena": x.get("cena"), "legenda": x["id"], "nivel": "aviso", "segundos": round(fim - limite, 2), "texto": f"A legenda “{x['texto'][:30]}” termina depois da cena e foi cortada em {fim - limite:.1f} s."})
        fim = min(fim, limite)
        if ini >= limite or not x["texto"].strip():
            if x["texto"].strip():
                avisos.append({"tipo": "legenda_fora", "cena": x.get("cena"), "legenda": x["id"], "nivel": "alerta", "segundos": 0, "texto": f"A legenda “{x['texto'][:30]}” ficou fora do tempo da cena e não aparece."})
            continue
        legendas.append({"id": x["id"], "cena": x.get("cena"), "f0": round(ini * fps), "f1": max(round(ini * fps) + 1, round(fim * fps)), "ini": round(ini, 4), "fim": round(fim, 4), "texto": x["texto"], "x": x["x"], "y": x["y"], "estilo": x["estilo"], "manual": x.get("manual")})
    ordem = sorted(legendas, key=lambda z: z["f0"])
    for a, b in zip(ordem, ordem[1:]):
        if a["f1"] > b["f0"] and abs(a["y"] - b["y"]) < 90:
            avisos.append({"tipo": "legendas_sobrepostas", "cena": b.get("cena"), "legenda": b["id"], "nivel": "aviso", "segundos": round((a["f1"] - b["f0"]) / fps, 2), "texto": f"Duas legendas aparecem juntas no mesmo lugar em {b['ini']:.1f} s."})
    faltando = [s["rotulo"] for s in segs if not s["fonte_ok"]]
    return {"fps": fps, "w": estado["w"], "h": estado["h"], "total_f": total_f, "total_s": round(total_s, 4), "segmentos": segs, "audio": audio, "eventos": eventos, "legendas": legendas, "avisos": avisos, "fontes_faltando": faltando, "assinatura": assinatura(estado), "rev": estado.get("rev", 0)}


def _resolver_fonte(fonte):
    """Clipe de imagem da cena e onde a cena começa nele."""
    if fonte["tipo"] == "video":
        return fonte["sha"], float(fonte.get("ini") or 0.0)
    r = um("SELECT sha FROM fontes WHERE chave=?", fonte.get("chave") or "")
    if r and M.caminho_blob(r["sha"]).exists():
        return r["sha"], 0.0
    return None, 0.0


def mixar(compilado, destino):
    """O mesmo áudio da prévia e do MP4: as falas (stems) na posição da linha do tempo e os efeitos do media/sfx.py."""
    from media import sfx
    falas = [(a["pos"], str(M.caminho_blob(a["sha"])), a["de"], a["dur"], a["ganho"]) for a in compilado["audio"]]
    return sfx.build(compilado["eventos"], compilado["total_f"], compilado["fps"], destino, falas=falas)


def audio_previa(slug):
    e = carregar(slug)
    c = compilar(e)
    AUDIOS.mkdir(parents=True, exist_ok=True)
    chave = M.sha_texto(json.dumps([c["audio"], c["eventos"], c["total_f"], c["fps"]], sort_keys=True))
    f = AUDIOS / f"{chave}.wav"
    if not f.exists():
        mixar(c, f)
    return f


def quadro_de(sha, t, largura=216):
    """Miniatura de um clipe, guardada: a linha do tempo e a tira de cenas pedem a mesma várias vezes."""
    origem = M.caminho_blob(sha)
    if not origem.exists():
        raise Recusado("Arquivo não encontrado.", 404)
    MINIATURAS.mkdir(parents=True, exist_ok=True)
    f = MINIATURAS / f"{sha[:24]}_{round(float(t) * 30)}_{int(largura)}.jpg"
    if not f.exists():
        tmp = f.with_suffix(f".{hashlib.md5(str(f).encode()).hexdigest()[:6]}.tmp.jpg")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{float(t):.3f}", "-i", str(origem), "-frames:v", "1", "-vf", f"scale={int(largura)}:-2", "-q:v", "4", str(tmp)], capture_output=True, creationflags=0x08000000)
        if r.returncode != 0 or not tmp.exists():
            raise Recusado("Não foi possível extrair o quadro.", 500)
        tmp.replace(f)
    return f


# ---------- Conflitos: o que os agentes mudaram depois da edição ----------

def conflitos(slug, estado):
    """O que o projeto tem de diferente do que o corte usa. Nada se aplica sozinho: o Guilherme escolhe, item a item."""
    if estado.get("modo") != "cenas" or not caminho(slug).exists():
        return []
    saida = []
    cenas_disco = M.ler_cenas(slug)
    falas = M.falas(slug)
    funcoes, resto = _hash_desenhos(slug)
    if len(cenas_disco) != len(estado["cenas"]):
        saida.append({"id": "estrutura", "tipo": "estrutura", "texto": f"O projeto agora tem {len(cenas_disco)} cenas, e este corte tem {len(estado['cenas'])}. Isso não dá para aplicar por partes: comece um corte novo para usar a estrutura nova.", "aplicavel": False})
        return saida
    itens = {n["cena"]: n for n in estado["narracao"]["itens"]}
    pins = estado.get("pins") or {}
    for c in estado["cenas"]:
        i = c["i"]
        n = itens.get(c["id"])
        if i in falas and n and n["arquivo"] != "audio.wav" and falas[i]["sha"] != n["sha"]:
            nova = float(falas[i]["dur"] or _dur_midia(falas[i]["arquivo"]))
            depois = float(n["desloc"]) - c["in"] + nova
            saida.append({"id": f"narracao:{c['id']}", "tipo": "narracao", "cena": c["id"], "rotulo": c["rotulo"], "dur_antes": n["dur"], "dur_depois": round(nova, 3), "dur_cena": duracao_cena(c), "ressincronizar": depois > duracao_cena(c) + 0.02, "aplicavel": True,
                          "texto": f"{c['rotulo']}: nova narração com {nova:.2f} s (antes {n['dur']:.2f} s)." + (f" Não cabe nos {duracao_cena(c):.2f} s da cena: exige ressincronizar." if depois > duracao_cena(c) + 0.02 else " Cabe na duração atual da cena.")})
        texto = M.fala_de(cenas_disco[i])
        if texto != c.get("fala"):
            saida.append({"id": f"texto:{c['id']}", "tipo": "texto", "cena": c["id"], "rotulo": c["rotulo"], "antes": c.get("fala"), "depois": texto, "aplicavel": True, "texto": f"{c['rotulo']}: a fala mudou no cenas.json."})
        fonte = c["fonte"]
        if fonte["tipo"] == "sketch":
            chave = chave_fonte(slug, fonte["desenho"], fonte["dur"], estado["fps"], estado["formato"], funcoes, resto)
            if chave != fonte.get("chave"):
                saida.append({"id": f"desenho:{c['id']}", "tipo": "desenho", "cena": c["id"], "rotulo": c["rotulo"], "aplicavel": True, "chave": chave,
                              "texto": f"{c['rotulo']}: o desenho mudou em sketch_cenas.py" + (" (a própria cena)." if funcoes.get(fonte["desenho"]) != (pins.get("desenhos") or {}).get(fonte["desenho"]) else " (uma função auxiliar).")})
    return saida


def aplicar_conflitos(slug, ids, rev):
    """Aplica só o que foi escolhido. Legendas manuais, enquadramentos, volumes e assets continuam como estão."""
    e = carregar(slug)
    if rev != e.get("rev"):
        raise Recusado("Este corte mudou em outra aba. Recarregue o editor.")
    disponiveis = {x["id"]: x for x in conflitos(slug, e)}
    falas = M.falas(slug)
    cenas_disco = M.ler_cenas(slug)
    aplicados, ressync = [], []
    for ident in ids:
        x = disponiveis.get(ident)
        if not x or not x.get("aplicavel"):
            raise Recusado(f"Mudança não disponível: {ident}. Recarregue o editor.")
        c = next(k for k in e["cenas"] if k["id"] == x["cena"])
        if x["tipo"] == "narracao":
            n = next(k for k in e["narracao"]["itens"] if k["cena"] == c["id"])
            sha = _wav_conforme(falas[c["i"]]["arquivo"])
            if not sha:
                raise Recusado(f"{c['rotulo']}: não foi possível ler a nova narração.")
            n.update(sha=sha, dur=x["dur_depois"], arquivo=falas[c["i"]]["arquivo"].name)
            if x["ressincronizar"]:
                ressync.append(c["rotulo"])
        elif x["tipo"] == "texto":
            c["fala"] = x["depois"]
        else:
            c["fonte"]["chave"] = x["chave"]
        aplicados.append(ident)
    _gerar_legendas(e)
    e["pins"] = pins_atuais(slug) if len(aplicados) == len(disponiveis) else e.get("pins")
    e = _gravar(slug, e)
    return {"estado": e, "aplicados": aplicados, "ressincronizar": ressync, "tambem": [x["id"] for x in conflitos(slug, e)]}


# ---------- Versões de corte e assets ----------

def nova_versao(slug, nota=None):
    e = carregar(slug)
    if not caminho(slug).exists():
        e = _gravar(slug, e)
    corpo = json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha = M.sha_bytes(corpo)
    M.guardar_blob(corpo, sha)
    ass = assinatura(e)
    ultimo = um("SELECT numero, assinatura FROM cortes WHERE slug=? ORDER BY numero DESC LIMIT 1", slug)
    if ultimo and ultimo["assinatura"] == ass:
        return {"numero": ultimo["numero"], "novo": False}
    numero = (ultimo["numero"] if ultimo else 0) + 1
    faz("INSERT INTO cortes (slug, numero, assinatura, sha, nota, criada_em) VALUES (?,?,?,?,?,?)", slug, numero, ass, sha, (nota or "")[:200], agora())
    return {"numero": numero, "novo": True}


def restaurar_versao(slug, numero, rev):
    v = um("SELECT sha FROM cortes WHERE slug=? AND numero=?", slug, numero)
    if not v:
        raise Recusado("Versão de corte não encontrada.", 404)
    atual = carregar(slug)
    if rev != atual.get("rev"):
        raise Recusado("Este corte mudou em outra aba. Recarregue o editor.")
    e = json.loads(M.ler_blob_texto(v["sha"]))
    e["rev"] = atual.get("rev", 0)
    return _gravar(slug, e)


def versoes(slug):
    return varios("SELECT numero, assinatura, nota, criada_em FROM cortes WHERE slug=? ORDER BY numero DESC", slug)


def exportacao_do_video(slug, video_sha):
    return um("SELECT * FROM exportacoes WHERE slug=? AND video_sha=? ORDER BY id DESC LIMIT 1", slug, video_sha)


def situacao(slug):
    """O corte salvo já está no vídeo atual? É o que marca o corte alterado para nova revisão."""
    f = caminho(slug)
    if not f.exists():
        return None
    e = M.ler_json(f, None)
    if not isinstance(e, dict):
        return None
    ass = assinatura(e)
    v = M.pasta(slug) / "video.mp4"
    if not v.exists():
        return {"em_dia": False, "assinatura": ass, "motivo": "O corte ainda não foi exportado."}
    exp = exportacao_do_video(slug, M.sha_arquivo(v))
    if not exp:
        return {"em_dia": False, "assinatura": ass, "motivo": "O vídeo atual não contém as edições do corte: exporte o corte para gerar a versão com elas."}
    if exp["assinatura"] != ass:
        return {"em_dia": False, "assinatura": ass, "motivo": "O corte foi alterado depois desta exportação: exporte de novo e revise."}
    return {"em_dia": True, "assinatura": ass, "motivo": None}


def adicionar_asset(slug, nome, corpo):
    """Arquivo enviado pelo Guilherme. Só imagem de verdade (o conteúdo decide, não a extensão)."""
    import io

    from PIL import Image
    if len(corpo) > 30 << 20:
        raise Recusado("Imagem grande demais (máximo 30 MB).", 400)
    try:
        im = Image.open(io.BytesIO(corpo))
        im.verify()
        im = Image.open(io.BytesIO(corpo))
        w, h = im.size
        tipo = im.format
    except Exception:
        raise Recusado("O arquivo não é uma imagem válida.", 400)
    if tipo not in ("PNG", "JPEG", "WEBP"):
        raise Recusado("Envie PNG, JPEG ou WebP.", 400)
    if tipo == "WEBP":  # o compositor lê qualquer um, mas o restante do canal trabalha com PNG e JPEG
        buf = io.BytesIO()
        im.convert("RGBA").save(buf, "PNG")
        corpo, tipo = buf.getvalue(), "PNG"
    sha = M.sha_bytes(corpo)
    M.guardar_blob(corpo, sha)
    pasta = M.pasta(slug) / PASTA_ASSETS
    pasta.mkdir(exist_ok=True)
    ext = ".png" if tipo == "PNG" else ".jpg"
    arquivo = pasta / f"{re.sub(r'[^a-z0-9_-]+', '-', Path(nome or 'asset').stem.lower())[:40] or 'asset'}-{sha[:8]}{ext}"
    if not arquivo.exists():
        arquivo.write_bytes(corpo)
    return {"sha": sha, "nome": arquivo.name, "origem": f"{PASTA_ASSETS}/{arquivo.name}", "w": w, "h": h, "url": f"/blob/{sha}?nome={arquivo.name}"}


def galeria(slug):
    """O que pode entrar numa cena: componentes do Raphinha e os arquivos enviados no editor."""
    from PIL import Image
    saida = []
    p = M.pasta(slug)
    uploads = sorted((p / PASTA_ASSETS).glob("*")) if (p / PASTA_ASSETS).is_dir() else []
    for f, origem, grupo in [(x, f"componentes/{x.name}", "Componentes") for x in M.imagens_componentes(slug)] + [(x, f"{PASTA_ASSETS}/{x.name}", "Enviados") for x in uploads if x.is_file()]:
        try:
            sha = M.sha_arquivo(f)
            M.guardar_blob(f, sha)
            with Image.open(f) as im:
                w, h = im.size
        except OSError:
            continue
        saida.append({"sha": sha, "nome": f.name, "origem": origem, "w": w, "h": h, "grupo": grupo, "url": f"/blob/{sha}?nome={f.name}"})
    return saida


def vista(slug):
    """Tudo que o editor precisa ao abrir ou depois de salvar."""
    e = carregar(slug)
    c = compilar(e)
    from .troca_estilo import descrever
    return {"estilo_projeto": descrever(slug), "estado": e, "compilado": c, "conflitos": conflitos(slug, e), "versoes": versoes(slug), "situacao": situacao(slug), "salvo": caminho(slug).exists(), "presets": PRESETS_LEGENDA,
            "operacoes": {"reordenar": e["modo"] == "cenas", "trocar_asset": e["modo"] == "cenas", "por_cena": e["modo"] == "cenas"}, "faltam": e.get("faltam", [])}


# ---------- Trabalhos pesados: seguem a mesma fila, então clique duplo não duplica ----------

def pedir_fontes(slug):
    e = carregar(slug)
    if not compilar(e)["fontes_faltando"]:
        return {"job": None, "novo": False}
    from .fluxo import inserir_job
    job, novo = inserir_job(slug, "corte_fontes", {"tipo": "comando", "comando": ["-m", "estudio.corte_export", "--slug", slug, "--fontes"], "raia": "pesado", "real": True, "craque": "Render", "titulo": "Preparando as fontes de imagem do editor", "materiais": [], "origem": "corte"}, assinatura=f"fontes:{slug}")
    return {"job": job["id"], "novo": novo}


def pedir_exportacao(slug, confirmado=False):
    """Exporta o corte salvo. O que corta fala ou sobrepõe aparece antes: só segue com a confirmação."""
    from .fluxo import inserir_job
    if not caminho(slug).exists():
        _gravar(slug, importar(slug))  # exportar sem edição também vale: fica claro qual estado gerou o vídeo
    e = carregar(slug)
    c = compilar(e)
    alertas = [a["texto"] for a in c["avisos"] if a["nivel"] == "alerta"]
    if alertas and not confirmado:
        raise Recusado(["Confirme para exportar assim:"] + alertas)
    job, novo = inserir_job(slug, "video", {"tipo": "comando", "comando": ["-m", "estudio.corte_export", "--slug", slug], "raia": "pesado", "real": True, "craque": "Render", "titulo": "Exportando o corte", "materiais": ["video"], "origem": "corte"}, assinatura=f"corte:{c['assinatura']}")
    return {"job": job["id"], "novo": novo}


def recomecar(slug):
    """Descarta o corte de trabalho e importa de novo. A versão atual fica guardada antes, e pode ser restaurada."""
    if caminho(slug).exists():
        nova_versao(slug, "Antes de recomeçar")
        rev = carregar(slug).get("rev", 0)
        e = importar(slug)
        e["rev"] = rev
        _gravar(slug, e)
    return vista(slug)
