#!/usr/bin/env python
"""Organiza e valida as imagens que o ChatGPT devolveu (pasta ou .zip).

Uso (a partir da raiz do projeto, no .venv):
  .venv\\Scripts\\python -I ecossistema\\sistema_unico\\ferramentas_assets\\organizar_e_validar.py ENTRADA --saida SAIDA [--prio P0,P1] [--so-validar]

Faz: confere nomes contra o manifesto (66 itens do 06/08), tamanho, peso e fundo
(cor do setor opaca ou magenta #FF00FF), gera relatorio.md + reposicao.txt/csv,
converte para WebP em SAIDA/assets/<pasta>/<slot>.webp, recorta avatares em
rd 256, sq 512 e rt 640x800, e troca o magenta por transparente (com tolerancia).

Seguranca: o zip e dado nao confiavel. Nada e executado; nada e extraido para disco
(leitura em memoria); caminhos com '..' ou absolutos sao ignorados; limites de
quantidade, de peso e de pixels. A entrada nunca e alterada.
Sem segredos, sem rede. Requer Pillow; usa numpy (opcional) para tirar o halo magenta.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

from PIL import Image, ImageChops

try:  # opcional
    import numpy as np
except Exception:  # pragma: no cover
    np = None

Image.MAX_IMAGE_PIXELS = 40_000_000
LIMITE_ARQUIVOS = 400
LIMITE_BYTES_ARQUIVO = 40 * 1024 * 1024
LIMITE_BYTES_TOTAL = 1500 * 1024 * 1024
EXT_OK = {".png", ".jpg", ".jpeg", ".webp"}
MAGENTA = (255, 0, 255)

# ---------------------------------------------------------------- manifesto
# (slug, cor_do_setor, prioridade) conforme 06 e 07. Fonte unica: o 08 e gerado a partir daqui.
AVATARES = [
    ("casemiro", "1FA37B", "P0"), ("ronaldo", "E0AA1E", "P0"),
    ("de_bruyne", "2F7DE1", "P0"), ("luiz_henrique", "5B7283", "P0"),
    ("olise", "2F7DE1", "P1"), ("valverde", "5B7283", "P1"), ("alisson", "D14B93", "P1"),
    ("salah", "D9542D", "P1"), ("vini", "2F7DE1", "P1"), ("neymar", "2F7DE1", "P1"),
    ("raphinha", "2F7DE1", "P1"), ("seedorf", "2F7DE1", "P1"), ("memphis", "2F7DE1", "P1"),
    ("rivaldo", "D9542D", "P1"), ("kaka", "D9542D", "P1"), ("zidane", "D9542D", "P1"),
    ("zico", "D14B93", "P1"), ("lamine_yamal", "E0AA1E", "P1"), ("modric", "2F7DE1", "P1"),
    ("courtois", "2F7DE1", "P1"), ("mbappe", "2F7DE1", "P1"), ("vitinho", "7C5FDB", "P1"),
    ("rodrygo", "D14B93", "P1"), ("endrick", "D14B93", "P1"), ("thiago_silva", "D14B93", "P1"),
    ("marquinhos", "D14B93", "P1"), ("voce", "0B63E5", "P1"),
    ("haaland", "2F7DE1", "P2"), ("messi", "2F7DE1", "P2"), ("cristiano", "2F7DE1", "P2"),
    ("barcola", "2F7DE1", "P2"), ("kane", "2F7DE1", "P2"), ("hugo_souza", "7C5FDB", "P2"),
    ("fagner", "7C5FDB", "P2"), ("andre_carrillo", "7C5FDB", "P2"), ("raniele", "7C5FDB", "P2"),
    ("yuri_alberto", "7C5FDB", "P2"), ("garro", "7C5FDB", "P2"), ("busquets", "7C5FDB", "P2"),
    ("xabi_alonso", "7C5FDB", "P2"), ("pele", "D9542D", "P2"), ("figo", "D9542D", "P2"),
    ("totti", "D9542D", "P2"), ("buffon", "D9542D", "P2"), ("lewandowski", "D9542D", "P2"),
    ("roberto_carlos", "D9542D", "P2"), ("pirlo", "D9542D", "P2"), ("guardiola", "E0AA1E", "P2"),
    ("pedri", "E0AA1E", "P2"), ("rodri", "E0AA1E", "P2"), ("kroos", "E0AA1E", "P2"),
    ("bellingham", "E0AA1E", "P2"), ("xavi", "D14B93", "P2"), ("ancelotti", "D14B93", "P2"),
    ("iniesta", "D14B93", "P2"), ("dembele", "2F7DE1", "P2"), ("firmino", "5B7283", "P2"),
]

# pasta, chave (nome gerado sem sufixos), forma, WxH gerado, fundo, prio, descricao curta
OUTROS = [
    ("ilustracoes", "vazio_espera", "ret", (1536, 1024), "chave", "P0", "caixa de entrada vazia com um check"),
    ("ilustracoes", "vazio_financas", "ret", (1536, 1024), "chave", "P0", "carteira/cofrinho aberto e vazio"),
    ("ilustracoes", "erro_geral", "ret", (1536, 1024), "chave", "P0", "tomada/cabo desconectado"),
    ("ilustracoes", "vazio_generico", "ret", (1536, 1024), "chave", "P0", "prancheta vazia com sinal de mais"),
    ("icones", "logo_contexto_explica", "sq", (1024, 1024), "chave", "P0", "marca sem letras"),
    ("ilustracoes", "vazio_agentes", "ret", (1536, 1024), "chave", "P1", "lupa sobre fila vazia de peoes"),
    ("fundos", "fundo_hero_ilha", "hor", (1536, 1024), "cena", "P1", "linhas de metro abstratas, azul-marinho"),
    ("fundos", "fundo_splash", "ver", (1024, 1536), "cena", "P2", "mesma linguagem, vertical"),
    ("extras", "extra_og_capa", "hor", (1536, 1024), "cena", "P2", "vitrine com marca e linhas de metro"),
]

# Nomes descritivos usados nos primeiros lotes. Sao candidatos para o item
# canonico indicado; a validacao visual/tecnica continua obrigatoria.
ALIAS = {
    "ronaldo_com_grafico_ascendente": "avatar_ronaldo",
    "carteira_vazia_com_moeda_ambar": "vazio_financas",
    "plugue_e_tomada_com_faisca": "erro_geral",
    "prancheta_vazia_com_sinal_de_mais": "vazio_generico",
    "balao_de_conversa_com_linha_metroviaria": "logo_contexto_explica",
    "lupa_sobre_espacos_vazios_do_tabuleiro": "vazio_agentes",
    "avatar_com_carimbo_de_aprovacao": "avatar_voce",
    "avatar_de_pedri_com_checklist": "avatar_pedri",
    "barcola_correndo_com_moldura_vazia": "avatar_barcola",
    "busquets_em_avatar_azulgrana": "avatar_busquets",
    "capitao_marquinhos_com_foguete": "avatar_marquinhos",
    "capitao_thiago_silva_com_diagrama_arquitetonico": "avatar_thiago_silva",
    "caricatura_de_totti_com_balanca": "avatar_totti",
    "caricatura_de_zidane_com_claquete": "avatar_zidane",
    "caricatura_vetorial_de_lewandowski_no_bayern": "avatar_lewandowski",
    "courtois_com_luvas_e_checklist": "avatar_courtois",
    "dembele_driblando_com_celular_ambar": "avatar_dembele",
    "goleiro_italiano_com_selo_de_aprovacao": "avatar_buffon",
    "guardiola_com_quadro_kanban": "avatar_guardiola",
    "hugo_souza_em_estilo_cartunesco": "avatar_hugo_souza",
    "jude_bellingham_comemorando_com_smartphone": "avatar_bellingham",
    "kaka_com_tesoura_e_fita_de_video": "avatar_kaka",
    "lamine_yamal_jovem_driblador_com_celular": "avatar_lamine_yamal",
    "luis_figo_com_claquete": "avatar_figo",
    "mbappe_em_arrancada_relampago": "avatar_mbappe",
    "memphis_depay_em_vermelho_e_branco": "avatar_memphis",
    "modric_com_caderno_e_lupa": "avatar_modric",
    "neymar_driblando_com_caderno_na_mao": "avatar_neymar",
    "pirlo_lupa_e_passe_magistral": "avatar_pirlo",
    "raphinha_com_lapis_e_regua": "avatar_raphinha",
    "retrato_de_harry_kane_com_microfone": "avatar_kane",
    "rivaldo_em_retrato_azul_e_grena": "avatar_rivaldo",
    "roberto_carlos_chute_poderoso_e_smartphone": "avatar_roberto_carlos",
    "roberto_firmino_sorrindo_com_pincel": "avatar_firmino",
    "rodri_com_relogio_de_ponto": "avatar_rodri",
    "rodrigo_garro_em_versao_tecnologica": "avatar_garro",
    "rodrygo_em_estilo_cartoon_com_engrenagem": "avatar_rodrygo",
    "salah_com_lupa_e_tela": "avatar_salah",
    "seedorf_sorrindo_em_camisa_rossonera": "avatar_seedorf",
    "toni_kroos_com_chave_e_cadeado": "avatar_kroos",
    "valverde_com_chip_ambar": "avatar_valverde",
    "vini_jr_driblando_com_carimbo_de_aprovacao": "avatar_vini",
    "xabi_alonso_tecnico_do_leverkusen": "avatar_xabi_alonso",
    "xavi_hernandez_com_quadro_tatico": "avatar_xavi",
    "yuri_alberto_com_grafico_em_ascensao": "avatar_yuri_alberto",
    "zico_rubro_negro_com_quadro_de_tarefas": "avatar_zico",
}

PESO_MAX_KB = {"avatares": 3500, "ilustracoes": 3500, "icones": 3500, "fundos": 5000, "extras": 5000}


def construir_manifesto():
    itens = []
    for slug, cor, prio in AVATARES:
        itens.append(dict(pasta="avatares", chave=f"avatar_{slug}", slug=slug, forma="ver",
                          wh=(1024, 1536), fundo="opaco", cor=cor, prio=prio,
                          arquivo=f"avatar_{slug}_ver_1024x1536.png", desc=f"retrato do agente {slug}"))
    for pasta, chave, forma, wh, fundo, prio, desc in OUTROS:
        itens.append(dict(pasta=pasta, chave=chave, slug=chave, forma=forma, wh=wh, fundo=fundo,
                          cor="FF00FF" if fundo == "chave" else "", prio=prio,
                          arquivo=f"{chave}_{forma}_{wh[0]}x{wh[1]}.png", desc=desc))
    ordem = {"P0": 0, "P1": 1, "P2": 2}
    itens.sort(key=lambda i: ordem[i["prio"]])
    return itens


def normalizar_chave(nome: str) -> str:
    """avatar_De-Bruyne_ver_1024x1536 (1).PNG -> avatar_de_bruyne"""
    s = unicodedata.normalize("NFKD", Path(nome).stem.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s*\(\d+\)$", "", s)
    s = s.replace("-", "_").replace(" ", "_")
    s = re.sub(r"_\d+x\d+$", "", s)
    s = re.sub(r"_(ver|ret|sq|hor|rd|rt)$", "", s)
    return s


# ---------------------------------------------------------------- entrada
def listar_entrada(caminho: Path):
    """Devolve (lista de (nome_relativo, funcao_que_le_bytes), avisos)."""
    avisos, itens, total = [], [], 0
    if caminho.is_file() and caminho.suffix.lower() == ".zip":
        zf = zipfile.ZipFile(caminho)
        for info in zf.infolist():
            if info.is_dir():
                continue
            p = PurePosixPath(info.filename.replace("\\", "/"))
            if p.is_absolute() or ".." in p.parts:
                avisos.append(f"ignorado (caminho suspeito no zip): {info.filename}")
                continue
            if p.parts and p.parts[0] == "__MACOSX" or p.name.startswith("."):
                continue
            if info.file_size > LIMITE_BYTES_ARQUIVO:
                avisos.append(f"ignorado (arquivo grande demais): {info.filename}")
                continue
            total += info.file_size
            if total > LIMITE_BYTES_TOTAL or len(itens) >= LIMITE_ARQUIVOS:
                avisos.append("limite de quantidade/peso do zip atingido; o restante foi ignorado")
                break
            itens.append((str(p), (lambda i=info: zf.read(i))))
    elif caminho.is_dir():
        for f in sorted(caminho.rglob("*")):
            if not f.is_file() or f.is_symlink():
                continue
            if f.stat().st_size > LIMITE_BYTES_ARQUIVO:
                avisos.append(f"ignorado (arquivo grande demais): {f.name}")
                continue
            total += f.stat().st_size
            if total > LIMITE_BYTES_TOTAL or len(itens) >= LIMITE_ARQUIVOS:
                avisos.append("limite de quantidade/peso atingido; o restante foi ignorado")
                break
            itens.append((str(f.relative_to(caminho)).replace("\\", "/"), (lambda f=f: f.read_bytes())))
    else:
        raise SystemExit(f"Entrada nao encontrada (esperava pasta ou .zip): {caminho}")
    return itens, avisos


def ler_manifest_csv(itens):
    for nome, ler in itens:
        if PurePosixPath(nome).name.lower() == "manifest.csv":
            try:
                txt = ler().decode("utf-8-sig", "replace")
                return [r for r in csv.DictReader(io.StringIO(txt))]
            except Exception:
                return None
    return None


# ---------------------------------------------------------------- analise de imagem
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def amostra_cantos(img: Image.Image, n=48, so_superiores=False):
    """Cor mediana dos cantos (n x n); avatares usam os dois superiores, longe dos ombros."""
    w, h = img.size
    rgba = img.convert("RGBA")
    cantos = [(0, 0), (w - n, 0)] if so_superiores else [(0, 0), (w - n, 0), (0, h - n), (w - n, h - n)]
    cores, transp = [], 0
    for x, y in cantos:
        patch = rgba.crop((x, y, x + n, y + n))
        px = list(patch.getdata())
        if sum(1 for p in px if p[3] < 128) > len(px) / 2:
            transp += 1
            continue
        med = tuple(sorted(p[c] for p in px)[len(px) // 2] for c in range(3))
        # variacao interna (percentis 5-95): xadrez/ruido, imune a um pixel solto
        var = max(sorted(p[c] for p in px)[int(len(px) * .95)] - sorted(p[c] for p in px)[int(len(px) * .05)] for c in range(3))
        cores.append((med, var))
    return cores, transp


def chave_magenta(img: Image.Image, tol_baixa=40, tol_alta=225) -> Image.Image:
    """Magenta -> transparente. Rampa de alfa entre as tolerancias; tira o halo."""
    rgba = img.convert("RGBA")
    if np is not None:
        a = np.asarray(rgba).astype("float32")
        d = np.maximum.reduce([abs(a[..., 0] - 255), a[..., 1], abs(a[..., 2] - 255)])
        alfa = np.clip((d - tol_baixa) / float(tol_alta - tol_baixa), 0.0, 1.0)
        alfa = np.minimum(alfa, a[..., 3] / 255.0)
        out = a.copy()
        semi = (alfa > 0) & (alfa < 1)
        # desmistura a cor: c = (p - (1-a)*chave) / a
        for c, k in zip(range(3), MAGENTA):
            canal = out[..., c]
            canal[semi] = np.clip((canal[semi] - (1 - alfa[semi]) * k) / alfa[semi], 0, 255)
            out[..., c] = canal
        out[..., 3] = alfa * 255.0
        return Image.fromarray(out.round().astype("uint8"), "RGBA")
    # sem numpy: so Pillow (sem desmistura; erode 1 px o alfa para reduzir o halo)
    r, g, b, a0 = rgba.split()
    dr = ImageChops.difference(r, Image.new("L", rgba.size, 255))
    db = ImageChops.difference(b, Image.new("L", rgba.size, 255))
    d = ImageChops.lighter(ImageChops.lighter(dr, g), db)
    k = 255.0 / (tol_alta - tol_baixa)
    alfa = d.point(lambda v: 0 if v <= tol_baixa else min(255, int((v - tol_baixa) * k)))
    alfa = ImageChops.darker(alfa, a0)
    from PIL import ImageFilter
    alfa = alfa.filter(ImageFilter.MinFilter(3))
    rgba.putalpha(alfa)
    return rgba


def tem_xadrez(cores):
    return any(var > 40 for _, var in cores)


def razao(wh):
    return wh[0] / wh[1]


def corte_centro(img, rw, rh):
    """Recorte centralizado com a razao rw:rh, o maior possivel."""
    w, h = img.size
    if w / h > rw / rh:
        nw = round(h * rw / rh)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = round(w * rh / rw)
    y = (h - nh) // 2
    return img.crop((0, y, w, y + nh))


def salvar_webp(img, destino: Path, q=88):
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, "WEBP", quality=q, method=6)
    return destino.stat().st_size


# ---------------------------------------------------------------- processamento
def validar_item(item, img, bruto_len, hashes, tol_cor):
    """Devolve (status, [problemas], [avisos], info)."""
    prob, avis, info = [], [], {}
    w, h = img.size
    ew, eh = item["wh"]
    info["tamanho"] = f"{w}x{h}"
    if (w, h) != (ew, eh):
        if abs(razao((w, h)) - razao((ew, eh))) / razao((ew, eh)) > 0.03:
            prob.append(f"proporcao errada: veio {w}x{h}, esperado {ew}x{eh}")
        else:
            avis.append(f"tamanho {w}x{h} (esperado {ew}x{eh}); proporcao ok, sera redimensionado")
    if min(w, h) < 0.6 * min(ew, eh):
        prob.append(f"resolucao baixa demais ({w}x{h})")
    kb = bruto_len / 1024
    info["kb"] = round(kb)
    if kb > PESO_MAX_KB[item["pasta"]]:
        avis.append(f"arquivo pesado: {kb:.0f} KB")
    digest = hashlib.sha256(img.tobytes()).hexdigest()
    if digest in hashes:
        prob.append(f"imagem identica a {hashes[digest]} (duplicata)")
    else:
        hashes[digest] = item["chave"]
    cores, transp = amostra_cantos(img, so_superiores=item["fundo"] == "opaco")
    if item["fundo"] == "chave":
        if transp >= 3:
            info["fundo"] = "ja transparente"
            avis.append("ja veio com transparencia (confira se nao e xadrez desenhado)")
        elif tem_xadrez(cores):
            prob.append("fundo com padrao/xadrez desenhado nos cantos")
        else:
            d = max(dist(c, MAGENTA) for c, _ in cores) if cores else 999
            info["fundo"] = f"magenta d={d}"
            if d > 70:
                prob.append(f"fundo nao e magenta #FF00FF (desvio {d})")
            elif d > tol_cor:
                avis.append(f"magenta com desvio {d}")
    elif item["fundo"] == "opaco":
        alvo = hex_rgb(item["cor"])
        if transp:
            prob.append("avatar com cantos transparentes (esperado fundo opaco na cor do setor)")
        elif tem_xadrez(cores):
            prob.append("fundo com padrao/xadrez nos cantos")
        else:
            d = max(dist(c, alvo) for c, _ in cores)
            info["fundo"] = f"setor #{item['cor']} d={d}"
            if d > 70:
                prob.append(f"fundo diferente da cor do setor #{item['cor']} (desvio {d})")
            elif d > tol_cor:
                avis.append(f"fundo com desvio {d} da cor do setor")
    else:  # cena
        if transp:
            prob.append("fundo de tela veio com transparencia")
    return ("REPROVADO" if prob else ("OK*" if avis else "OK")), prob, avis, info


def converter(item, img, saida: Path):
    """Grava os WebP finais. Devolve lista de arquivos gravados (relativos a saida)."""
    gravados = []
    base = saida / "assets" / item["pasta"]
    ch = item["chave"]
    if item["pasta"] == "avatares":
        slug = item["slug"]
        w, h = img.size
        rgb = img.convert("RGB")
        quad = rgb.crop((0, 0, w, w))                       # topo quadrado
        ret = rgb.crop((0, 0, w, min(h, round(w * 1.25))))   # topo 4:5
        for sufixo, im, tam in (("rd", quad, (256, 256)), ("sq", quad, (512, 512)), ("rt", ret, (640, 800))):
            dest = base / f"avatar_{slug}_{sufixo}.webp"
            salvar_webp(im.resize(tam, Image.LANCZOS), dest)
            gravados.append(dest)
    elif item["fundo"] == "chave":
        rgba = chave_magenta(img)
        if ch == "logo_contexto_explica":
            salvar_webp(rgba.resize((256, 256), Image.LANCZOS), base / "logo_contexto_explica.webp")
            gravados.append(base / "logo_contexto_explica.webp")
            for nome, t in (("favicon.png", 32), ("apple-touch-icon.png", 180), ("icon_512.png", 512)):
                saida.mkdir(parents=True, exist_ok=True)
                rgba.resize((t, t), Image.LANCZOS).save(saida / nome)
                gravados.append(saida / nome)
        else:
            dest = base / f"{ch}.webp"
            salvar_webp(rgba.resize((960, 640), Image.LANCZOS), dest)
            gravados.append(dest)
    else:
        rgb = img.convert("RGB")
        if ch == "fundo_hero_ilha":
            im, tam, nome = corte_centro(rgb, 16, 7), (1600, 700), "fundo_hero_ilha"
        elif ch == "fundo_splash":
            im, tam, nome = corte_centro(rgb, 9, 16), (1080, 1920), "fundo_splash"
        else:
            im, tam, nome = corte_centro(rgb, 1200, 630), (1200, 630), "og_capa"
        dest = base / f"{nome}.webp"
        salvar_webp(im.resize(tam, Image.LANCZOS), dest, q=82)
        gravados.append(dest)
    return gravados


def folha_de_contatos(arquivos, destino: Path, lado=128, cols=10):
    if not arquivos:
        return
    linhas = (len(arquivos) + cols - 1) // cols
    folha = Image.new("RGB", (cols * lado, linhas * lado), (30, 30, 30))
    for i, f in enumerate(arquivos):
        im = Image.open(f).convert("RGBA")
        im.thumbnail((lado, lado))
        fundo = Image.new("RGBA", im.size, (200, 200, 200, 255))
        fundo.alpha_composite(im)
        folha.paste(fundo.convert("RGB"), ((i % cols) * lado, (i // cols) * lado))
    folha.save(destino, quality=85)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", nargs="?", help="pasta ou .zip baixado do ChatGPT")
    ap.add_argument("--saida", default="assets_saida", help="pasta de saida (padrao: assets_saida)")
    ap.add_argument("--prio", default="P0,P1,P2", help="prioridades a exigir, ex.: P0 ou P0,P1")
    ap.add_argument("--so-validar", action="store_true", help="nao grava WebP, so o relatorio")
    ap.add_argument("--tolerancia", type=int, default=40, help="desvio de cor aceito no fundo (0-255)")
    ap.add_argument("--exportar-manifesto", metavar="CSV", help="grava o manifesto esperado e sai")
    a = ap.parse_args(argv)

    manifesto = construir_manifesto()
    if a.exportar_manifesto:
        with open(a.exportar_manifesto, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["arquivo", "pasta", "largura", "altura", "forma", "fundo", "prio", "descricao"])
            for i in manifesto:
                fundo = {"opaco": f"opaco #{i['cor']}", "chave": "magenta #FF00FF", "cena": "cena"}[i["fundo"]]
                w.writerow([i["arquivo"], i["pasta"], i["wh"][0], i["wh"][1], i["forma"], fundo, i["prio"], i["desc"]])
        print(f"manifesto esperado gravado em {a.exportar_manifesto} ({len(manifesto)} itens)")
        return 0
    if not a.entrada:
        ap.error("informe a pasta ou o .zip de entrada")

    prios = {p.strip().upper() for p in a.prio.split(",")}
    saida = Path(a.saida)
    entrada = Path(a.entrada)
    itens_in, avisos = listar_entrada(entrada)
    mani_csv = ler_manifest_csv(itens_in)

    por_chave = {i["chave"]: i for i in manifesto}
    achados, extras = {}, []
    for nome, ler in itens_in:
        p = PurePosixPath(nome)
        if p.suffix.lower() not in EXT_OK:
            continue
        ch = normalizar_chave(p.name)
        ch = ALIAS.get(ch, ch)
        if ch in por_chave:
            achados.setdefault(ch, []).append((nome, ler))
        else:
            extras.append(nome)

    resultados, hashes, convertidos, avatares_out = [], {}, [], []
    for item in manifesto:
        ch = item["chave"]
        if item["prio"] not in prios and ch not in achados:
            continue
        r = dict(item=item, nomes=[], status="FALTA", prob=[], avis=[], info={})
        if ch in achados:
            achados[ch].sort(key=lambda candidato: normalizar_chave(PurePosixPath(candidato[0]).name) != ch)
            if len(achados[ch]) > 1:
                r["avis"].append(f"{len(achados[ch])} arquivos para o mesmo item; usado o primeiro: " + ", ".join(n for n, _ in achados[ch]))
            nome, ler = achados[ch][0]
            r["nomes"] = [nome]
            try:
                bruto = ler()
                img = Image.open(io.BytesIO(bruto))
                img.load()
                if (PurePosixPath(nome).name.lower() != item["arquivo"]):
                    r["avis"].append(f"nome fora do padrao (esperado {item['arquivo']}); aceito pela chave")
                st, prob, avis, info = validar_item(item, img, len(bruto), hashes, a.tolerancia)
                r.update(status=st, prob=prob, avis=r["avis"] + avis, info=info)
                if st != "REPROVADO" and not a.so_validar:
                    gravados = converter(item, img, saida)
                    convertidos += gravados
                    if item["pasta"] == "avatares":
                        avatares_out.append(gravados[1])
            except Exception as e:  # arquivo corrompido, etc.
                r.update(status="REPROVADO", prob=[f"nao abriu como imagem: {type(e).__name__}"])
        resultados.append(r)

    # relatorio
    saida.mkdir(parents=True, exist_ok=True)
    cont = {"OK": 0, "OK*": 0, "REPROVADO": 0, "FALTA": 0}
    for r in resultados:
        cont[r["status"]] += 1
    L = ["# Relatorio de validacao dos assets", "",
         f"Entrada: `{entrada}`. Prioridades exigidas: {', '.join(sorted(prios))}. Itens avaliados: {len(resultados)}.",
         f"OK: {cont['OK']} | OK com aviso: {cont['OK*']} | reprovados: {cont['REPROVADO']} | faltando: {cont['FALTA']}",
         ""]
    if avisos:
        L += ["## Avisos de seguranca/entrada"] + [f"- {x}" for x in avisos] + [""]
    L += ["## Itens", "", "| item | prio | status | tamanho | KB | fundo | observacoes |", "|---|---|---|---|---|---|---|"]
    for r in resultados:
        i = r["item"]
        obs = "; ".join(r["prob"] + r["avis"]) or ""
        L.append(f"| `{i['chave']}` | {i['prio']} | {r['status']} | {r['info'].get('tamanho', '')} | "
                 f"{r['info'].get('kb', '')} | {r['info'].get('fundo', '')} | {obs} |")
    if extras:
        L += ["", "## Arquivos que nao batem com nenhum item (ignorados)"] + [f"- `{x}`" for x in extras[:80]]
    if mani_csv is not None:
        nomes_man = {normalizar_chave(r.get("arquivo", "")) for r in mani_csv}
        sem_man = [c for c in achados if c not in nomes_man]
        if sem_man:
            L += ["", "## Imagens que estao no zip mas nao constam no manifest.csv dele"] + [f"- `{c}`" for c in sem_man]
    elif any(PurePosixPath(n).suffix.lower() in EXT_OK for n, _ in itens_in):
        L += ["", "Aviso: o zip/pasta nao trazia `manifest.csv`."]
    repor = [r for r in resultados if r["status"] in ("FALTA", "REPROVADO")]
    (saida / "relatorio.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(saida / "reposicao.txt", "w", encoding="utf-8") as fh:
        fh.write("# Itens para o lote de reposicao (cole estes nomes no ChatGPT, com o bloco de estilo)\n")
        for r in repor:
            i = r["item"]
            motivo = "faltou" if r["status"] == "FALTA" else "; ".join(r["prob"])
            fh.write(f"{i['arquivo']}\t{i['prio']}\t{motivo}\n")
    with open(saida / "reposicao.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["arquivo", "pasta", "largura", "altura", "prio", "motivo"])
        for r in repor:
            i = r["item"]
            w.writerow([i["arquivo"], i["pasta"], i["wh"][0], i["wh"][1], i["prio"],
                        "faltou" if r["status"] == "FALTA" else "; ".join(r["prob"])])
    if avatares_out and not a.so_validar:
        folha_de_contatos(avatares_out, saida / "contatos_avatares.jpg")

    print(f"OK {cont['OK']} | OK* {cont['OK*']} | reprovados {cont['REPROVADO']} | faltando {cont['FALTA']}")
    print(f"relatorio: {saida / 'relatorio.md'}")
    print(f"reposicao: {saida / 'reposicao.txt'} ({len(repor)} itens)")
    if not a.so_validar:
        print(f"WebP gravados: {len(convertidos)} em {saida / 'assets'}")
    return 0 if not repor else 1


if __name__ == "__main__":
    sys.exit(main())
