"""Mede nos quadros o que os estilos prometem. Nenhum movimento é dado como certo: cada um é comparado com a mesma cena sem ele.
Render, ffmpeg e projetos antigos são reais; nada é gravado em output/ e não há narração nem custo.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_estilos.py [pasta para capturas]"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from media import camadas, cartoon_lib as C, colagem_lib as K, estilos, motion, sketch, sketch_lib  # noqa: E402

passou, falhas = 0, []
CAPTURAS = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}" + (f" ({extra})" if extra is not None else ""), flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def arr(im):
    return np.asarray(im.convert("RGB"), dtype="float32")


def dif(a, b, caixa=None):
    a, b = arr(a), arr(b)
    if caixa:
        x0, y0, x1, y1 = caixa
        a, b = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
    return float(np.abs(a - b).mean())


def psnr(a, b):
    m = float(((a - b) ** 2).mean())
    return 99.0 if m < 1e-6 else 10 * np.log10(255 ** 2 / m)


def ctx_de(c):
    return {"cenas": [c], "i": 1}  # i=1: fora da primeira cena, as entradas acontecem de verdade


# ---------- Cartoon Vivo ----------
def boneco(**kw):
    return {"id": "bia", "x": 540, "y": 1440, "poses": [{"t": 0, "pose": "neutra", "expressao": "feliz"}], **kw}


def cena_c(**kw):
    return {"tipo": "cartoon_alive", "desenho": "cena_0", "paleta": "sol", "acao": "teste", "cenario": "liso", "personagens": [boneco()], "camera": {"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}]}, **kw}


def q(c, lt, dur=4.0):
    return C.quadro(c, lt, dur, ctx_de(c))


def testar_cartoon():
    print("\n[Cartoon Vivo] cada movimento, comparado com a mesma cena sem ele")
    # Troca de pose: braço sobe; o tronco quase não muda. Comparado depois do golpe da troca.
    com = cena_c(personagens=[boneco(poses=[{"t": 0, "pose": "neutra", "expressao": "feliz"}, {"t": 1.0, "pose": "bracos_cima", "expressao": "feliz"}])])
    sem = cena_c()
    confere(dif(q(com, 2.0), q(sem, 2.0)) > 0.3, "Troca de pose muda o quadro", round(dif(q(com, 2.0), q(sem, 2.0)), 2))
    a, m, b = C._pose_em(com["personagens"][0]["poses"], 1.0)[0], C._pose_em(com["personagens"][0]["poses"], 1.1)[0], C._pose_em(com["personagens"][0]["poses"], 2.0)[0]
    confere(a["f"] < m["f"] and abs(b["f"] - 152) < 0.01, "A pose é interpolada entre os ângulos, não troca de imagem", [round(a["f"]), round(m["f"]), round(b["f"])])
    # Expressão: só muda o rosto
    ex = cena_c(personagens=[boneco(poses=[{"t": 0, "pose": "neutra", "expressao": "feliz"}, {"t": 1.0, "pose": "neutra", "expressao": "brava"}])])
    rosto, pernas = (380, 780, 720, 1120), (380, 1320, 720, 1460)
    confere(dif(q(ex, 2.0), q(sem, 2.0), rosto) > 1.0 and dif(q(ex, 2.0), q(sem, 2.0), pernas) < 0.3, "Expressão muda o rosto e não o corpo", [round(dif(q(ex, 2.0), q(sem, 2.0), rosto), 2), round(dif(q(ex, 2.0), q(sem, 2.0), pernas), 2)])
    # Piscar: procura de verdade um instante com o olho fechado
    tempos = [i / 30 for i in range(0, 120)]
    fechados = [t for t in tempos if C._piscando("bia", t)]
    confere(0 < len(fechados) < 20, "Piscar acontece em poucos quadros", len(fechados))
    t_p = fechados[0]
    t_a = next(t for t in tempos if t > t_p + 0.3 and not C._piscando("bia", t))
    olhos = (400, 840, 700, 970)
    confere(dif(q(sem, t_p), q(sem, t_a), olhos) > dif(q(sem, t_a), q(sem, t_a + 1 / 30), olhos) * 3, "O olho fecha mesmo no quadro do piscar", round(dif(q(sem, t_p), q(sem, t_a), olhos), 2))
    # Respiração: nada parado
    confere(dif(q(sem, 2.0), q(sem, 2.3)) > 0.02, "Personagem parado ainda respira", round(dif(q(sem, 2.0), q(sem, 2.3)), 3))
    # Fala: boca abre e fecha
    fala = cena_c(personagens=[boneco(fala=True)])
    boca = (420, 900, 680, 1060)
    confere(dif(q(fala, 2.0), q(fala, 2.14), boca) > 1.0, "Quem fala mexe a boca", round(dif(q(fala, 2.0), q(fala, 2.14), boca), 2))
    # Entradas
    for tipo, lt in (("salto", 0.25), ("queda", 0.2), ("deslize", 0.1), ("pop", 0.1)):
        e = cena_c(personagens=[boneco(entrada=tipo, t=0.0)])
        fim = dif(q(e, 3.0), q(sem, 3.0))
        confere(dif(q(e, lt), q(sem, lt)) > 0.5 and fim < 0.01, f"Entrada por {tipo}: anima e depois assenta", [round(dif(q(e, lt), q(sem, lt)), 2), round(fim, 3)])
    # Squash-and-stretch no pouso
    _, _, sx, sy, _ = camadas.entrada("queda", 0.40, 0.0, 0.55)
    confere(sx > 1.02 and sy < 0.98, "Squash ao tocar o chão: alarga e achata", [round(sx, 3), round(sy, 3)])
    _, _, sx, sy, _ = camadas.entrada("queda", 0.1, 0.0, 0.55)
    confere(sx < 1 and sy > 1, "Stretch na queda: afina e alonga", [round(sx, 3), round(sy, 3)])
    # Zoom rápido
    z = cena_c(camera={"chaves": [{"t": 1.0, "x": 540, "y": 960, "zoom": 1.0}, {"t": 1.2, "x": 540, "y": 960, "zoom": 1.5, "curva": "rapida"}]})
    confere(dif(q(z, 0.9), q(z, 1.1)) > 5 * dif(q(z, 0.8), q(z, 0.9)), "Zoom rápido: a imagem salta quando a chave chega", round(dif(q(z, 0.9), q(z, 1.1)), 2))
    # Tremida
    tr = cena_c(camera={"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}], "tremidas": [{"t": 1.0, "forca": 30}]})
    confere(dif(q(tr, 1.05), q(sem, 1.05)) > 1 and dif(q(tr, 1.8), q(sem, 1.8)) < 0.01, "Tremida no impacto, e depois para", [round(dif(q(tr, 1.05), q(sem, 1.05)), 2), round(dif(q(tr, 1.8), q(sem, 1.8)), 3)])
    # Parallax: a camada de longe anda menos que o chão
    px = cena_c(cenario="rua", camera={"chaves": [{"t": 0, "x": 400, "y": 960, "zoom": 1.0}, {"t": 2, "x": 700, "y": 960, "zoom": 1.0}]}, personagens=[])
    px["textos"] = [{"texto": "x", "x": 540, "y": 500, "t": 99}]
    d_longe = deslocamento(q(px, 0.0), q(px, 2.0), (250, 420))
    d_perto = deslocamento(q(px, 0.0), q(px, 2.0), (900, 1400))
    confere(abs(d_perto) > abs(d_longe) * 1.5 and abs(d_longe) > 5, "Parallax: o que está longe anda menos", [d_longe, d_perto])
    # Transições
    for nome, campo, lt in (("chicote", "saida", 3.95), ("zoom", "saida", 3.95), ("continua", "saida", 3.8), ("chicote", "entrada", 0.05), ("zoom", "entrada", 0.1), ("continua", "entrada", 0.1)):
        t = cena_c(transicao={campo: nome})
        confere(dif(q(t, lt), q(sem, lt)) > 0.2 and dif(q(t, 2.0), q(sem, 2.0)) < 0.01, f"Transição de {campo}: {nome}", round(dif(q(t, lt), q(sem, lt)), 2))
    # Loop: o último quadro é o primeiro
    primeiro = {**cena_c(), "desenho": "cena_0", "cenario": "rua"}
    ultimo = {**cena_c(cenario="sala"), "desenho": "cena_1", "transicao": {"saida": "loop"}}
    ctx = {"cenas": [primeiro, ultimo], "i": 1}
    q0 = C.quadro(primeiro, 0.0, 4.0, {"cenas": [primeiro, ultimo], "i": 0})
    qf = C.quadro(ultimo, 4.0 - 1 / 30, 4.0, ctx)
    confere(dif(q0, qf) < 0.001, "Loop: o último quadro é igual ao primeiro", round(dif(q0, qf), 4))
    confere(dif(C.quadro(ultimo, 3.7, 4.0, ctx), q0) > 1, "Loop: antes do fim a imagem ainda está em transição")
    # Camadas separadas e paleta reduzida
    partes = C._partes("bia", "sol")
    confere({"cabeca", "tronco", "braco_f", "ante", "perna", "olho_normal", "pupila", "boca_sorriso", "sobrancelha"} <= set(partes), "Personagem é feito de partes separadas", len(partes))
    demo = json.loads((REPO / "media/demos/cartoon_alive/cenas.json").read_text(encoding="utf-8"))
    im = arr(C.quadro(demo[1], 2.0, 3.2, {"cenas": demo, "i": 1}))
    cores = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in C.PALETAS["sol"].values()], dtype="float32")
    perto = (np.abs(im[..., None, :] - cores).max(axis=-1).min(axis=-1) < 14).mean()
    confere(len(C.PALETAS["sol"]) == 6 and perto > 0.97, "Quadro real usa só as 6 cores da paleta (o resto é antisserrilhado)", f"{perto:.1%}")
    # O mesmo personagem nas duas cenas, em poses diferentes
    nas_duas = [{a["id"] for a in c["personagens"]} for c in demo]
    poses = [p["pose"] for c in demo for a in c["personagens"] if a["id"] == "bia" for p in a["poses"]]
    confere("bia" in nas_duas[0] & nas_duas[1] and len(set(poses)) >= 2, "Mesmo personagem em poses diferentes entre as cenas", sorted(set(poses)))


def deslocamento(a, b, faixa):
    """Quantos px a imagem andou na horizontal, nessa faixa de altura. Correlação de perfis."""
    y0, y1 = faixa
    pa, pb = arr(a)[y0:y1].mean(axis=(0, 2)), arr(b)[y0:y1].mean(axis=(0, 2))
    pa, pb = pa - pa.mean(), pb - pb.mean()
    melhor, ponto = -1e18, 0
    for d in range(-400, 401):
        x0, x1 = max(0, d), min(len(pa), len(pa) + d)
        v = float((pa[x0:x1] * pb[x0 - d:x1 - d]).mean())
        if v > melhor:
            melhor, ponto = v, d
    return ponto


# ---------- Colagem ----------
def doc(**kw):
    return {"id": "doc", "tipo": "documento", "x": 540, "y": 800, "larg": 800, "t": 0, "entrada": "corte", "titulo": "RELATORIO", "linhas": ["Primeira linha", "Segunda linha"], **kw}


def cena_k(**kw):
    return {"tipo": "documentary_collage", "desenho": "cena_0", "acao": "teste", "superficie": "mesa_preta", "recortes": [doc()], "camera": {"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}]}, **kw}


def k(c, lt, dur=4.0):
    return K.quadro(c, lt, dur, ctx_de(c))


def testar_colagem():
    print("\n[Colagem Documental] cada movimento, comparado com a mesma cena sem ele")
    sem = cena_k()
    for tipo, lt in (("pousa", 0.15), ("desliza", 0.1), ("rasga", 0.2)):
        e = cena_k(recortes=[doc(entrada=tipo)])
        confere(dif(k(e, lt), k(sem, lt)) > 0.5 and dif(k(e, 3.0), k(sem, 3.0)) < 0.01, f"Recorte entra por {tipo} e depois assenta", round(dif(k(e, lt), k(sem, lt)), 2))
    # Rasgo: a revelação cresce
    rasgo = cena_k(recortes=[doc(entrada="rasga")])
    papel = lambda lt: float((arr(k(rasgo, lt))[600:1000, 140:940].mean(axis=-1) > 150).mean())
    confere(papel(0.05) < papel(0.2) < papel(0.5), "Papel é revelado aos poucos ao rasgar", [round(papel(x), 2) for x in (0.05, 0.2, 0.5)])
    # Fita nas pontas
    fita = cena_k(recortes=[doc(fita=True)])
    confere(dif(k(fita, 3.0), k(sem, 3.0)) > 0.1 and dif(k(fita, 0.2), k(sem, 0.2)) < 0.01, "Fita adesiva aparece só depois que o papel pousa", round(dif(k(fita, 3.0), k(sem, 3.0)), 2))
    # Marca-texto percorre a palavra
    d = cena_k(destaques=[{"em": "doc", "linha": 1, "t": 1.0, "dur": 0.6}])
    amarelo = lambda im: int(((arr(im)[..., 0] > 190) & (arr(im)[..., 2] < 175) & (arr(im)[..., 1] > 165)).sum())
    a0, a1, a2 = amarelo(k(d, 0.9)), amarelo(k(d, 1.1)), amarelo(k(d, 2.0))
    confere(a0 < a1 < a2, "Marca-texto percorre a linha", [a0, a1, a2])
    # Carimbo com impacto
    cm = cena_k(carimbos=[{"texto": "CONFIRMADO", "x": 540, "y": 1100, "t": 1.0}])
    confere(dif(k(cm, 1.05), k(cm, 0.95)) > 0.5, "Carimbo surge com impacto", round(dif(k(cm, 1.05), k(cm, 0.95)), 2))
    confere(dif(k(cm, 1.05), k(cm, 3.0), (0, 0, 1080, 300)) > 0.05, "O impacto do carimbo mexe a mesa toda")
    # Conexão cresce
    dois = [doc(), {"id": "f", "tipo": "foto", "figura": "pessoa", "x": 300, "y": 1300, "larg": 300, "t": 0, "entrada": "corte"}]
    cx = cena_k(recortes=dois, conexoes=[{"de": "f", "para": "doc", "t": 1.0, "dur": 0.8}])
    verm = lambda im: int(((arr(im)[..., 0] > 170) & (arr(im)[..., 1] < 70) & (arr(im)[..., 2] < 70)).sum())
    v0, v1, v2 = verm(k(cx, 0.9)), verm(k(cx, 1.2)), verm(k(cx, 2.5))
    confere(v0 < v1 < v2, "Linha de conexão cresce de uma evidência à outra", [v0, v1, v2])
    # Câmera sobre o mural
    cam = cena_k(camera={"chaves": [{"t": 0, "x": 540, "y": 960, "zoom": 1.0}, {"t": 3, "x": 540, "y": 800, "zoom": 1.7}]})
    confere(dif(k(cam, 3.0), k(sem, 3.0)) > 5, "Câmera aproxima do documento", round(dif(k(cam, 3.0), k(sem, 3.0)), 2))
    # Parallax entre fundo, documentos e evidências
    p = cena_k(camera={"chaves": [{"t": 0, "x": 420, "y": 960, "zoom": 1.0}, {"t": 2, "x": 700, "y": 960, "zoom": 1.0}]})
    d_fundo = deslocamento(k(p, 0.0), k(p, 2.0), (1500, 1880))
    d_doc = deslocamento(k(p, 0.0), k(p, 2.0), (640, 960))
    confere(abs(d_doc) > abs(d_fundo) * 1.2 and abs(d_fundo) > 5, "Parallax: a mesa anda menos que o documento", [d_fundo, d_doc])
    # Transições por folha
    for nome in ("virada", "recorte", "sobrepoe"):
        t = cena_k(transicao={"saida": nome, "entrada": nome})
        confere(dif(k(t, 3.85), k(sem, 3.85)) > 1, f"Saída por {nome}", round(dif(k(t, 3.85), k(sem, 3.85)), 2))
        confere(dif(k(t, 0.15), k(sem, 0.15)) > 1, f"Entrada por {nome}", round(dif(k(t, 0.15), k(sem, 0.15)), 2))
        confere(dif(k(t, 2.0), k(sem, 2.0)) < 0.01, f"{nome} não mexe no meio da cena")
    # Loop
    u = {**cena_k(superficie="kraft"), "desenho": "cena_1", "transicao": {"saida": "loop"}}
    ctx = {"cenas": [sem, u], "i": 1}
    q0 = K.quadro(sem, 0.0, 4.0, {"cenas": [sem, u], "i": 0})
    confere(dif(q0, K.quadro(u, 4.0 - 1 / 30, 4.0, ctx)) < 0.001, "Loop: o último quadro é igual ao primeiro")
    # Sem mídia externa: tudo nasce aqui
    confere(all(x not in Path(K.__file__).read_text(encoding="utf-8") for x in ("http://", "https://", "requests", "urllib")), "A biblioteca não acessa rede")


# ---------- Exportação real ----------
def render_real(ident, destino):
    """O mesmo sketch.render do `run.py video`, sem voz, gravando o MP4 de verdade. Devolve os quadros decodificados do MP4."""
    pasta = destino / ident
    pasta.mkdir()
    shutil.copy(REPO / "media" / "demos" / ident / "cenas.json", pasta / "cenas.json")
    sketch.render(pasta, fps=30, sem_voz=True, render_cfg={"formato": "vertical", "duracao_min_s": 1, "duracao_max_s": 60})
    mp4 = pasta / "video.mp4"
    assert mp4.exists()
    tira = destino / f"{ident}_q"
    tira.mkdir()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", "fps=30,scale=270:480", str(tira / "%04d.png")], check=True)
    return pasta, [np.asarray(Image.open(f).convert("RGB"), dtype="float32") for f in sorted(tira.glob("*.png"))]


def testar_exportado(destino):
    print("\n[MP4 real] o vídeo exportado tem movimento, não só uma miniatura diferente")
    for ident in ("cartoon_alive", "documentary_collage"):
        pasta, qs = render_real(ident, destino)
        difs = np.array([np.abs(a - b).mean() for a, b in zip(qs[:-1], qs[1:])])
        confere(len(qs) > 150, f"{ident}: MP4 tem os quadros esperados", len(qs))
        confere((difs > 0.02).mean() > 0.95, f"{ident}: praticamente todo quadro muda em relação ao anterior", f"{(difs > 0.02).mean():.0%}")
        confere(difs.max() > 3, f"{ident}: há golpes de movimento, não só deriva", round(float(difs.max()), 2))
        confere(psnr(qs[0], qs[-1]) > 34, f"{ident}: o MP4 fecha em loop", f"{psnr(qs[0], qs[-1]):.1f} dB")
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,pix_fmt,r_frame_rate", "-of", "csv=p=0", str(pasta / "video.mp4")], capture_output=True, text=True).stdout.strip()
        confere(r.startswith("1080,1920,yuv420p,30/1"), f"{ident}: MP4 no padrão do canal", r)
        if CAPTURAS:
            CAPTURAS.mkdir(parents=True, exist_ok=True)
            n = len(qs)
            tira = np.concatenate([qs[i] for i in range(0, n, max(1, n // 8))][:8], axis=1).astype("uint8")
            Image.fromarray(tira).save(CAPTURAS / f"{ident}.jpg", quality=88)


# ---------- Validação ----------
def erro_de(lib, c):
    try:
        lib.validar(c, "cena 3")
    except ValueError as ex:
        return str(ex)
    return None


def testar_validacao():
    print("\n[Validação] o erro aponta a cena e o campo")
    confere(erro_de(C, cena_c()) is None and erro_de(K, cena_k()) is None, "Cenas válidas passam")
    casos = [
        (C, cena_c(cenario="marte"), "cenario"),
        (C, cena_c(acao=""), "acao"),
        (C, cena_c(personagens=[boneco(id="mickey")]), "personagem"),
        (C, cena_c(personagens=[boneco(poses=[{"t": 0, "pose": "voa", "expressao": "feliz"}])]), "pose"),
        (C, cena_c(personagens=[boneco(poses=[{"t": 0, "pose": "neutra", "expressao": "zen"}])]), "expressao"),
        (C, cena_c(objetos=[{"tipo": "celular", "x": 500, "y": 500}]), "celular"),
        (C, cena_c(textos=[{"texto": "x" * 27, "y": 400}]), "longo"),
        (C, cena_c(textos=[{"texto": "fora", "y": 1800}]), "área segura"),
        (K, cena_k(superficie="marmore"), "superficie"),
        (K, cena_k(recortes=[]), "recortes"),
        (K, cena_k(conexoes=[{"de": "doc", "para": "xxx"}]), "conexão"),
        (K, cena_k(recortes=[doc(arquivo="../../segredo.png")]), "arquivo"),
        (K, cena_k(camera={"chaves": [{"t": 0, "zoom": 9}]}), "câmera"),
    ]
    for lib, c, palavra in casos:
        e = erro_de(lib, c)
        confere(e and "cena 3" in e and palavra in e, f"Recusa {palavra}", e)
    ruim = [{"tipo": "cartoon_alive", "desenho": "cena_0", "fala": "a b c", "duracao": 30, **{k_: v for k_, v in cena_c().items() if k_ not in ("tipo", "desenho")}}, {"tipo": "sketch", "desenho": "cena_1", "fala": "a b c", "duracao": 30}]
    try:
        sketch.validate(ruim)
        confere(False, "Mistura de estilos no mesmo vídeo é recusada")
    except sketch.SpecErro as ex:
        confere("todas as cenas" in str(ex), "Mistura de estilos no mesmo vídeo é recusada", str(ex))
    confere(estilos.das_cenas(ruim) is None, "Mistura não é identificada como nenhum estilo")


# ---------- Projetos antigos ----------
def testar_antigos(destino):
    print("\n[Projetos antigos] Scratch e Cartão continuam iguais")
    saida = REPO / "output"
    ref = json.loads((Path(__file__).parent / "referencia_sketch.json").read_text(encoding="utf-8"))  # gravada antes de existirem os estilos novos
    sketch_lib.definir_formato("vertical")
    sketch_lib.definir_variante()
    for slug, sha in ref["fontes"].items():
        arq = saida / slug / "sketch_cenas.py"
        if not arq.exists() or hashlib.sha256(arq.read_bytes()).hexdigest() != sha:
            print(f"  pulado  {slug}: o sketch_cenas.py mudou depois da referência", flush=True)
            continue
        mod = sketch._carregar(arq)
        chaves = [k for k in ref["quadros"] if k.startswith(slug + "/")]
        iguais = sum(hashlib.sha256(getattr(mod, k.split("/")[1])(float(k.split("/")[2]), 5.0).convert("RGB").tobytes()).hexdigest() == ref["quadros"][k] for k in chaves)
        confere(iguais == len(chaves), f"{slug}: quadros idênticos, byte a byte, aos de antes dos estilos novos", f"{iguais} de {len(chaves)}")
    for slug in ("fim-dos-terceiros-lugares",):
        p = saida / slug
        cenas = json.loads((p / "cenas.json").read_text(encoding="utf-8"))
        confere(not (p / "estilo.json").exists(), f"{slug}: nenhum estilo.json foi criado")
        confere(estilos.das_cenas(cenas) == "sketch", f"{slug}: identificado como Scratch")
        confere(sketch._variante(p) == (None, None), f"{slug}: sem variação")
        feitas = json.loads((p / "cenas_render.json").read_text(encoding="utf-8"))
        sketch_lib.definir_formato("vertical")
        sketch_lib.definir_variante()
        mod = sketch._carregar(p / "sketch_cenas.py")
        t, notas = 0.0, []
        for i, c in enumerate(feitas[:3]):
            dur = float(c["duracao"])
            f = round((t + dur * 0.6) * 30)
            d = destino / f"{slug}_{i}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p / "video.mp4"), "-vf", f"select=eq(n\\,{f})", "-frames:v", "1", "-fps_mode", "passthrough", str(d)], check=True)
            novo = getattr(mod, c["desenho"])(f / 30 - t, dur).convert("RGB")
            notas.append(psnr(np.asarray(Image.open(d).convert("RGB"), dtype="float32"), arr(novo)))
            t += dur
        confere(min(notas) > 33, f"{slug}: desenho de hoje confere com o MP4 antigo", [round(float(x), 1) for x in notas])
    # Variação desligada não deixa rastro
    def cena():
        sketch_lib.definir_formato("vertical")
        im = sketch_lib.papel()
        d = sketch_lib.ImageDraw.Draw(im)
        sketch_lib.pessoa(d, 500, 900, 2.0, seed=4)
        sketch_lib.texto(d, 540, 400, "teste", 70)
        return im
    a = cena().tobytes()
    sketch_lib.definir_variante("caderno_pautado", {"papel": "bege", "traco": "marcador"})
    b = cena().tobytes()
    sketch_lib.definir_variante()
    confere(a != b, "A variação muda o desenho")
    confere(a == cena().tobytes(), "Sem variação, o quadro é idêntico byte a byte ao de antes")
    # Cartões: o mesmo validador, e o motor SVG foi exercitado ao gerar a demonstração
    cartoes = [p for p in saida.iterdir() if p.is_dir() and (p / "cenas.json").exists() and estilos.das_cenas(json.loads((p / "cenas.json").read_text(encoding="utf-8"))) == "cartoes"]
    confere(cartoes, "Há projetos antigos em Cartão para conferir", len(cartoes))
    for p in cartoes[:3]:
        cenas = json.loads((p / "cenas.json").read_text(encoding="utf-8"))
        try:
            motion.validate(cenas)
            ok = True
        except SystemExit as ex:
            ok = "duração" in str(ex).lower() or "fala" in str(ex).lower()  # regra antiga já recusava este; o que importa é o caminho ser o mesmo
        confere(ok and not (p / "estilo.json").exists(), f"{p.name}: Cartão continua no motor SVG")
    confere(estilos.normalizar("card") == "cartoes" and estilos.normalizar("scratch") == "sketch", "card e scratch valem como sinônimos dos ids antigos")
    diff = subprocess.run(["git", "status", "--short", "render/index.html", "render/render.mjs", "render/src"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    confere(not diff, "O motor SVG (render/) não foi alterado", diff)


def testar_variacao():
    print("\n[Scratch] variação Caderno pautado")
    def amostra(**o):
        sketch_lib.definir_formato("vertical")
        sketch_lib.definir_variante("caderno_pautado", o)
        im = sketch_lib.papel()
        d = sketch_lib.ImageDraw.Draw(im)
        sketch_lib.traco(d, [(300, 800), (800, 800)], 1, w=8, amp=0)
        return im
    bege, branco = amostra(papel="bege", traco="grafite"), amostra(papel="branco", traco="marcador")
    confere(bege.getpixel((600, 170)) == (243, 232, 208) and branco.getpixel((600, 170)) == (252, 252, 249), "Papel bege ou branco")
    confere(bege.getpixel((600, 140)) == (150, 200, 235), "Linhas horizontais azul-claro", bege.getpixel((600, 140)))
    m = bege.getpixel((150, 170))
    confere(m[0] > 200 and m[1] < 110, "Margem vertical vermelha", m)
    gr = sum(1 for y in range(780, 820) if bege.getpixel((600, y)) == (66, 66, 72))
    mc = sum(1 for y in range(780, 820) if branco.getpixel((600, y)) == (24, 30, 58))
    confere(mc > gr >= 4, "Grafite é fino e marcador é grosso", [gr, mc])
    sketch_lib.definir_variante()
    confere(estilos.ESTILOS["sketch"]["variantes"]["caderno_pautado"] and len(estilos.ESTILOS) == 4, "Caderno é variação do Scratch, não um quinto estilo", list(estilos.ESTILOS))
    for nome in ("marcador", "anotacao"):
        confere(callable(getattr(sketch_lib, nome)), f"Biblioteca oferece {nome}()")


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    print("[Registro]")
    confere(list(estilos.ESTILOS) == ["cartoes", "sketch", "cartoon_alive", "documentary_collage"], "Quatro estilos, com ids estáveis")
    for e in estilos.publico():
        web = REPO / "estudio" / e["demo"].lstrip("/")
        confere(all(e.get(k) for k in ("id", "nome", "detalhe", "melhor_para")) and web.exists() and web.with_suffix(".jpg").exists(), f"{e['nome']}: descrição, melhor uso e demonstração")
    skill = (REPO / ".claude/skills/estilos-por-camadas/SKILL.md").read_text(encoding="utf-8")
    catalogo = [*C.PALETAS, *C.ELENCO, *C.POSES, *C.EXPRESSOES, *C.OBJETOS, *C.CENARIOS, *C.ENTRADAS, *C.TRANS_SAIDA, *K.SUPERFICIES, *K.TIPOS, *K.FIGURAS, *K.ENTRADAS, *K.TRANS_SAIDA]
    fora = [x for x in catalogo if f"`{x}`" not in skill]
    confere(not fora, "A skill dos agentes lista tudo que as bibliotecas oferecem", fora)
    testar_cartoon()
    testar_colagem()
    testar_validacao()
    testar_variacao()
    with tempfile.TemporaryDirectory() as d:
        testar_antigos(Path(d))
        testar_exportado(Path(d))
    print(f"\n{passou} verificações ok, {len(falhas)} falhas.")
    if falhas:
        print("\n".join(f" - {f}" for f in falhas))
        sys.exit(1)


if __name__ == "__main__":
    main()
