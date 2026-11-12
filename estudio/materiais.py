"""Lê o que a squad e o run.py gravaram em output/<slug>/ e transforma em materiais versionáveis.

Só lê: o contrato de arquivos continua sendo o do CLAUDE.md. Cada versão é um manifesto de arquivos guardados por conteúdo
em estudio/dados/blobs, então uma versão antiga continua consultável mesmo depois de o arquivo ser sobrescrito.
"""
import hashlib
import io
import json
import re
import shutil
import sys
import threading
import time
from pathlib import Path

from .config import ASSENTAR_S, DADOS, RAIZ, REPO, SAIDA

sys.path.insert(0, str(REPO))
from media import estilos  # noqa: E402

BLOBS = DADOS / "blobs"
FORA_DA_REVISAO = {"contato.jpg", "cenas_exemplo.jpg", "cenas_exemplo_caixas.jpg"}
CAMPOS_NAO_TELA = {"tipo", "fala", "cor", "cores", "rodape_cor", "desenho", "duracao", "sons", "unidade", "escala_max",
                   "env", "camera", "atores", "objetos", "valor", "text", "image_prompt", "search"}
_lock = threading.Lock()
_cache_sha = {}
_cache_recortes = {}


def pasta(slug):
    return SAIDA / slug


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_texto(t):
    return sha_bytes(t.encode("utf-8"))


def sha_arquivo(p):
    p = Path(p)
    st = p.stat()
    chave = (str(p), st.st_size, st.st_mtime_ns)
    with _lock:
        if chave in _cache_sha:
            return _cache_sha[chave]
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    valor = h.hexdigest()
    with _lock:
        _cache_sha[chave] = valor
    return valor


def caminho_blob(sha):
    return BLOBS / sha[:2] / sha


def guardar_blob(origem, sha):
    """`origem` é um Path ou bytes. Grava atômico e não repete conteúdo já guardado."""
    destino = caminho_blob(sha)
    if destino.exists():
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(f".{threading.get_ident()}.tmp")
    if isinstance(origem, (bytes, bytearray)):
        tmp.write_bytes(origem)
    else:
        shutil.copyfile(origem, tmp)
    tmp.replace(destino)


def ler_blob_texto(sha):
    p = caminho_blob(sha)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def ler_texto(p):
    try:
        return Path(p).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def ler_json(p, padrao=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return padrao


def e_producao(p):
    return p.is_dir() and any((p / n).exists() for n in ("notas.md", "roteiro.txt", "cenas.json", "cenas3d.json", "video.mp4"))


def ultima_mudanca(p):
    """Mais recente entre os arquivos do topo da pasta (epoch). Sem varrer falas/ e frames/: é a lista inicial."""
    try:
        return max((f.stat().st_mtime for f in p.iterdir() if f.is_file()), default=p.stat().st_mtime)
    except OSError:
        return 0


def arquivo_cenas(slug):
    for nome in ("cenas.json", "cenas3d.json"):
        if (pasta(slug) / nome).exists():
            return pasta(slug) / nome
    return None


def ler_cenas(slug):
    f = arquivo_cenas(slug)
    cenas = ler_json(f, None) if f else None
    return cenas if isinstance(cenas, list) else []


def estilo_das_cenas(slug):
    f = arquivo_cenas(slug)
    if not f:
        return None
    if f.name == "cenas3d.json":
        return "3d"
    cenas = ler_cenas(slug)
    return (estilos.das_cenas(cenas) or "antigo") if cenas else None


def fala_de(c):
    return (c.get("fala") or c.get("text") or "").strip()  # `text`: pastas antigas, de antes do campo fala


def textos_tela(c):
    """Texto que aparece na tela, em qualquer um dos estilos."""
    if estilos.por_dados(estilos.do_tipo(c.get("tipo"))):
        return estilos.lib(estilos.do_tipo(c.get("tipo"))).textos(c)
    saida = []

    def juntar(v):
        if isinstance(v, str):
            if v.strip():
                saida.append(v.strip())
        elif isinstance(v, list):
            for x in v:
                juntar(x)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in CAMPOS_NAO_TELA:
                    juntar(x)

    for k, v in c.items():
        if k not in CAMPOS_NAO_TELA:
            juntar(v)
    return saida


def narracao_do_roteiro(slug):
    """A seção `## Narração` do direcao_viral.md: é dali que sai a `fala` das cenas."""
    m = re.search(r"^## *Narra[cç][aã]o[^\n]*\n(.*?)(?=^## |\Z)", ler_texto(pasta(slug) / "direcao_viral.md"), re.S | re.M)
    return m.group(1).strip() if m else ""


def falas(slug):
    """Trechos de narração por cena: {índice: {arquivo, dur, sha}}."""
    p = pasta(slug) / "falas"
    tabela = ler_json(p / "falas.json", {}) or {}
    saida = {}
    for k, v in tabela.items():
        wav = p / Path(str(v.get("wav", "")).replace("\\", "/")).name
        if wav.exists():
            saida[int(k)] = {"arquivo": wav, "dur": v.get("dur"), "sha": sha_arquivo(wav)}
    return saida


def textos_narrados(slug):
    t = ler_json(pasta(slug) / "falas" / "textos.json", None)
    return t if isinstance(t, list) else None


def tempos_cenas(slug, cenas):
    """Início e duração de cada cena. `exato` quando vem do render ou das falas medidas; senão é estimativa pelo texto."""
    feitas = ler_json(pasta(slug) / "cenas_render.json", None)
    if isinstance(feitas, list) and len(feitas) == len(cenas) and all(
            isinstance(c.get("duracao"), (int, float)) and c.get("fala") == x.get("fala") for c, x in zip(feitas, cenas)):
        durs, exato = [float(c["duracao"]) for c in feitas], True
    else:
        medidas = falas(slug)
        exato = bool(medidas) and len(medidas) == len(cenas)
        durs = []
        for i, c in enumerate(cenas):
            if i in medidas and medidas[i]["dur"]:
                durs.append(max(float(c.get("duracao") or 0), 0.05 + float(medidas[i]["dur"]) + 0.12))
            else:
                durs.append(max(float(c.get("duracao") or 0), len(fala_de(c).split()) / 3.0 + 0.2))
    saida, t = [], 0.0
    for d in durs:
        saida.append({"inicio": round(t, 2), "dur": round(d, 2)})
        t += d
    return saida, exato


def direcao_por_cena(slug):
    """Direção visual e componentes por cena, da tabela do componentes.md do Raphinha. {índice: {componentes, direcao}}."""
    saida, atual = {}, None
    em_tabela = False
    for linha in ler_texto(pasta(slug) / "componentes.md").splitlines():
        if not linha.startswith("|"):
            em_tabela = False
            continue
        cols = [c.strip() for c in linha.strip().strip("|").split("|")]
        if cols and cols[0].lower().startswith("cena"):
            em_tabela = True
            continue
        if not em_tabela or len(cols) < 3 or (cols[0] and set(cols[0]) <= set("-: ")):
            continue
        m = re.match(r"\*{0,2}(\d+)\*{0,2}", cols[0])
        if m:
            atual = int(m.group(1)) - 1
            saida[atual] = {"partes": [], "funcoes": set()}
        if atual is None:
            continue
        descricao = " · ".join(c.replace("`", "") for c in cols[-2:] if c)
        saida[atual]["partes"].append(descricao)
        saida[atual]["funcoes"].update(re.findall(r"`([a-z_0-9]+)", linha))
    return {k: {"direcao": "; ".join(v["partes"]), "funcoes": sorted(v["funcoes"])} for k, v in saida.items()}


def recortes_previa(slug, cenas):
    """Recorta previa.jpg (3 quadros por cena, 2 cenas por linha, ver media/sketch.py previa()) em um item por cena.
    Devolve {item: (jpeg, hash_visual)}. O hash é da imagem reduzida: reexportar a folha não derruba a aprovação de quem não mudou."""
    f = pasta(slug) / "previa.jpg"
    if not f.exists() or not cenas:
        return {}
    chave = (sha_arquivo(f), len(cenas))
    with _lock:
        if _cache_recortes.get(slug, (None,))[0] == chave:
            return _cache_recortes[slug][1]
    from PIL import Image
    folha = Image.open(f).convert("RGB")
    w, h = folha.size
    linhas = (len(cenas) + 1) // 2
    mw, mh = w / 6, h / linhas
    saida = {}
    if abs(mh / mw - 16 / 9) < 0.15 or abs(mh / mw - 9 / 16) < 0.1:
        for i in range(len(cenas)):
            x, y = (i % 2) * 3 * mw, (i // 2) * mh
            recorte = folha.crop((round(x), round(y), round(x + 3 * mw), round(y + mh)))
            buf = io.BytesIO()
            recorte.save(buf, "JPEG", quality=88)
            reduzida = recorte.convert("L").resize((81, 48))
            saida[f"cena_{i}"] = (buf.getvalue(), "v" + sha_bytes(bytes(p // 24 for p in reduzida.tobytes())))
    else:  # folha de outro formato (ex.: 3D antigo): revisa inteira
        saida["previa"] = (f.read_bytes(), sha_arquivo(f))
    with _lock:
        _cache_recortes[slug] = (chave, saida)
    return saida


def imagens_componentes(slug):
    d = pasta(slug) / "componentes"
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg")
                  and p.name not in FORA_DA_REVISAO)


def hash_cenas_texto(cenas):
    return sha_texto(json.dumps([[fala_de(c), textos_tela(c)] for c in cenas], ensure_ascii=False))


def manifesto(slug, material):
    """Estado atual do material em disco. Devolve (arquivos, itens) ou None se não existe.
    arquivos = {nome: Path|bytes}; itens = {item: sha} (o que é revisado um a um)."""
    p = pasta(slug)
    if material == "pesquisa":
        arquivos = {n: p / n for n in ("notas.md", "angulo.md") if (p / n).exists()}
        return (arquivos, {}) if "notas.md" in arquivos else None
    if material == "roteiro":
        if not (p / "roteiro.txt").exists():
            return None
        arquivos = {"roteiro.txt": p / "roteiro.txt"}
        narr = narracao_do_roteiro(slug)
        if narr:
            arquivos["narracao.txt"] = narr.encode("utf-8")
        return arquivos, {}
    if material == "componentes":
        imgs = imagens_componentes(slug)
        return ({f.name: f for f in imgs}, {f.stem: sha_arquivo(f) for f in imgs}) if imgs else None
    if material == "cenas":
        f = arquivo_cenas(slug)
        if not f:
            return None
        arquivos = {f.name: f}
        if (p / "sketch_cenas.py").exists():
            arquivos["sketch_cenas.py"] = p / "sketch_cenas.py"
        itens = {}
        for item, (jpeg, h) in recortes_previa(slug, ler_cenas(slug)).items():
            arquivos[item + ".jpg"] = jpeg
            itens[item] = h
        return arquivos, itens
    if material == "metadados":
        return ({"metadados.json": p / "metadados.json"}, {}) if (p / "metadados.json").exists() else None
    if material == "auditoria_texto":
        return ({"auditoria_texto.md": p / "auditoria_texto.md"}, {}) if (p / "auditoria_texto.md").exists() else None
    if material == "auditoria_final":
        return ({"auditoria.md": p / "auditoria.md"}, {}) if (p / "auditoria.md").exists() else None
    if material == "narracao":
        medidas = falas(slug)
        if medidas:
            arquivos = {f"cena_{i}.wav": v["arquivo"] for i, v in medidas.items()}
            for nome in ("textos.json", "falas.json"):  # para a versão antiga mostrar o texto e a duração dela
                if (p / "falas" / nome).exists():
                    arquivos[nome] = p / "falas" / nome
            return arquivos, {f"cena_{i}": v["sha"] for i, v in medidas.items()}
        if (p / "audio.wav").exists() and not (p / "video.mp4").exists():
            return {"audio.wav": p / "audio.wav"}, {"audio": sha_arquivo(p / "audio.wav")}
        return None
    if material == "video":
        return ({"video.mp4": p / "video.mp4"}, {}) if (p / "video.mp4").exists() else None
    if material == "thumbnail":
        f = RAIZ / "thumbnails" / "sidorf" / slug / "relatorio.md"
        return ({"relatorio.md": f}, {}) if f.exists() else None
    raise ValueError(material)


def fingerprint(arquivos, itens):
    """Hash da versão: os recortes de prévia entram pelo hash visual, os demais pelo conteúdo."""
    partes = {}
    for nome, origem in arquivos.items():
        if (nome.endswith(".jpg") and Path(nome).stem in itens) or nome in ("falas.json", "textos.json"):
            continue  # recortes entram pelo hash visual; as tabelas da narração descrevem os .wav, não mudam o áudio
        partes[nome] = sha_bytes(origem) if isinstance(origem, (bytes, bytearray)) else sha_arquivo(origem)
    return sha_texto(json.dumps({"a": partes, "i": itens}, sort_keys=True))


def assentado(arquivos):
    """Falso se algum arquivo mudou há pouco (um render pelo terminal, por exemplo, ainda escrevendo)."""
    limite = time.time() - ASSENTAR_S
    for origem in arquivos.values():
        if isinstance(origem, Path):
            try:
                if origem.stat().st_mtime > limite:
                    return False
            except OSError:
                return False
    return True


def guardar_versao(arquivos):
    """Copia os arquivos para o depósito e devolve {nome: sha}."""
    saida = {}
    for nome, origem in arquivos.items():
        sha = sha_bytes(origem) if isinstance(origem, (bytes, bytearray)) else sha_arquivo(origem)
        guardar_blob(origem, sha)
        saida[nome] = sha
    return saida


def status_auditoria(texto):
    """Mesmo critério do `run.py publish`."""
    t = (texto or "").upper()
    if "BLOQUEADO" in t:
        return "BLOQUEADO"
    return "APROVADO" if "APROVADO" in t else None


def fase_componentes():
    m = re.search(r"Fase:\s*(\w+)", ler_texto(RAIZ / "componentes" / "aprendizados.md"))
    return (m.group(1).lower() if m else "aprendendo")


def mudancas_entre(texto_antigo, texto_novo):
    """Frases que saíram do texto (normalizadas)."""
    return [f for f in _frases(texto_antigo) if f not in set(_frases(texto_novo))]


def _frases(texto):
    return [" ".join(p.lower().split()) for p in re.split(r"(?<=[.!?])\s+|\n+", texto or "") if p.strip()]


def cenas_com_frases(frases_alteradas, cenas):
    """Cenas cuja fala contém (com aproximação) alguma das frases alteradas. A fala nem sempre é cópia literal do roteiro
    (números por extenso, ajustes do Courtois), por isso comparação aproximada em vez de igualdade."""
    from difflib import SequenceMatcher
    afetadas = set()
    for i, c in enumerate(cenas):
        for parte in _frases(fala_de(c)):
            if any(parte == a or SequenceMatcher(None, parte, a).ratio() >= 0.6 for a in frases_alteradas):
                afetadas.add(i)
                break
    return sorted(afetadas)


def diff_palavras(antigo, novo):
    """Lista de [tipo, texto] com tipo = igual/saiu/entrou. Para mostrar o que mudou entre duas versões."""
    from difflib import SequenceMatcher
    a, b = re.findall(r"\s+|[^\s]+", antigo or ""), re.findall(r"\s+|[^\s]+", novo or "")
    saida = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            saida.append(["igual", "".join(a[i1:i2])])
        else:
            if i2 > i1:
                saida.append(["saiu", "".join(a[i1:i2])])
            if j2 > j1:
                saida.append(["entrou", "".join(b[j1:j2])])
    return saida
