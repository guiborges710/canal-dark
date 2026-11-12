#!/usr/bin/env python
"""Teste do organizar_e_validar.py com imagens SINTETICAS geradas na hora (nenhuma imagem real).

Rodar (raiz do projeto):
  .venv\\Scripts\\python -I ecossistema\\sistema_unico\\ferramentas_assets\\teste_organizar.py
"""
import importlib.util
import io
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("organizar", AQUI / "organizar_e_validar.py")
org = importlib.util.module_from_spec(spec)
sys.modules["organizar"] = org
spec.loader.exec_module(org)


def png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def avatar(cor, size=(1024, 1536)):
    im = Image.new("RGB", size, org.hex_rgb(cor))
    d = ImageDraw.Draw(im)
    d.ellipse((312, 130, 712, 600), fill=(240, 200, 160), outline=(14, 26, 36), width=10)
    d.rectangle((150, 1000, 874, 1536), fill=(239, 243, 241))
    return im


def objeto_magenta(size=(1536, 1024), fundo=(255, 0, 255), borda=True):
    im = Image.new("RGB", size, fundo)
    d = ImageDraw.Draw(im)
    cx, cy = size[0] // 2, size[1] // 2
    d.ellipse((cx - 320, cy - 320, cx + 320, cy + 320), fill=(239, 243, 241))        # borda branca "adesivo"
    d.ellipse((cx - 300, cy - 300, cx + 300, cy + 300), fill=(14, 26, 36))
    d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), fill=(255, 183, 3))
    # antialias simulado: reduz e amplia a imagem para borrar a borda com o magenta
    return im.resize((size[0] // 2, size[1] // 2), Image.LANCZOS).resize(size, Image.BILINEAR)


def logo_sintetico():
    im = objeto_magenta((1024, 1024))
    ImageDraw.Draw(im).rectangle((480, 480, 540, 540), fill=(11, 99, 229))
    return im


def xadrez(size=(1536, 1024)):
    im = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], 16):
        for x in range(0, size[0], 16):
            if (x // 16 + y // 16) % 2:
                d.rectangle((x, y, x + 15, y + 15), fill=(200, 200, 200))
    return im


def fundo_cena(size=(1536, 1024)):
    return Image.new("RGB", size, (14, 26, 36))


def checar(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        checar.falhas += 1


checar.falhas = 0


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        zpath = tmp / "entrada.zip"
        magenta = png(objeto_magenta())
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("assets_sistema_v1/avatares/Avatar-Casemiro_ver_1024x1536.PNG", png(avatar("1FA37B")))  # nome fora do padrao, aceito
            zf.writestr("assets_sistema_v1/avatares/avatar_ronaldo_ver_1024x1536.png", png(avatar("FFFFFF")))   # fundo errado
            # de_bruyne e luiz_henrique: faltando
            zf.writestr("assets_sistema_v1/ilustracoes/vazio_espera_ret_1536x1024.png", magenta)                # ok
            zf.writestr("assets_sistema_v1/ilustracoes/vazio_financas_ret_1536x1024.png", magenta)              # duplicata
            zf.writestr("assets_sistema_v1/ilustracoes/erro_geral_ret_1536x1024.png", png(xadrez()))            # xadrez
            zf.writestr("assets_sistema_v1/ilustracoes/vazio_generico_ret_1024x1024.png", png(objeto_magenta((1024, 1024))))  # proporcao errada
            zf.writestr("assets_sistema_v1/icones/logo_contexto_explica_sq_1024x1024.png", png(logo_sintetico()))
            zf.writestr("assets_sistema_v1/fundos/fundo_hero_ilha_hor_1536x1024.png", png(fundo_cena()))
            zf.writestr("assets_sistema_v1/ilustracoes/vazio_agentes_ret_1536x1024.png", png(objeto_magenta(fundo=(200, 30, 200))))  # magenta com leve desvio
            zf.writestr("assets_sistema_v1/extras/qualquer_coisa.png", png(fundo_cena((64, 64))))               # extra
            zf.writestr("../evil.png", png(fundo_cena((64, 64))))                                               # caminho suspeito
            zf.writestr("assets_sistema_v1/avatares/avatar_olise_ver_1024x1536.png", b"isto nao e imagem")      # corrompido
            zf.writestr("assets_sistema_v1/manifest.csv", "arquivo,pasta\navatar_casemiro_ver_1024x1536.png,avatares\n")

        for usar_numpy in (True, False):
            print(f"\n== rodada com numpy={'sim' if usar_numpy and org.np is not None else 'nao'} ==")
            saved = org.np
            if not usar_numpy:
                org.np = None
            saida = tmp / f"saida_{int(usar_numpy)}"
            rc = org.main([str(zpath), "--saida", str(saida), "--prio", "P0,P1"])
            org.np = saved

            rel = (saida / "relatorio.md").read_text(encoding="utf-8")
            rep = (saida / "reposicao.txt").read_text(encoding="utf-8")
            checar(rc == 1, "codigo de saida 1 (ha reposicao)")
            checar("avatar_casemiro" in rel and "| OK" in rel, "casemiro aceito apesar do nome fora do padrao")
            checar("avatar_ronaldo_ver_1024x1536.png\tP0\tfundo diferente" in rep, "ronaldo reprovado por fundo")
            checar("avatar_de_bruyne_ver_1024x1536.png\tP0\tfaltou" in rep, "de_bruyne listado como faltante")
            checar("erro_geral_ret_1536x1024.png\tP0\tfundo com padrao/xadrez" in rep, "xadrez detectado")
            checar("vazio_generico_ret_1536x1024.png\tP0\tproporcao errada" in rep, "proporcao errada detectada")
            checar("duplicata" in rep and "vazio_financas" in rep, "duplicata detectada")
            checar("avatar_olise_ver_1024x1536.png\tP1\tnao abriu" in rep, "arquivo corrompido reprovado")
            checar("caminho suspeito" in rel, "caminho '..' do zip ignorado")
            checar("qualquer_coisa.png" in rel, "arquivo extra listado")
            checar("magenta com desvio" in rel, "desvio leve de magenta so avisa")

            a = saida / "assets"
            esp = [
                a / "avatares/avatar_casemiro_rd.webp", a / "avatares/avatar_casemiro_sq.webp",
                a / "avatares/avatar_casemiro_rt.webp", a / "ilustracoes/vazio_espera.webp",
                a / "icones/logo_contexto_explica.webp", a / "fundos/fundo_hero_ilha.webp",
                saida / "favicon.png", saida / "apple-touch-icon.png", saida / "icon_512.png",
                a / "ilustracoes/vazio_agentes.webp", saida / "contatos_avatares.jpg",
            ]
            for f in esp:
                checar(f.exists(), f"gerado {f.relative_to(saida)}")
            checar(not (a / "avatares/avatar_ronaldo_rd.webp").exists(), "reprovado nao e convertido")
            if (a / "avatares/avatar_casemiro_rd.webp").exists():
                checar(Image.open(a / "avatares/avatar_casemiro_rd.webp").size == (256, 256), "rd 256x256")
                checar(Image.open(a / "avatares/avatar_casemiro_sq.webp").size == (512, 512), "sq 512x512")
                checar(Image.open(a / "avatares/avatar_casemiro_rt.webp").size == (640, 800), "rt 640x800")
            if (a / "ilustracoes/vazio_espera.webp").exists():
                im = Image.open(a / "ilustracoes/vazio_espera.webp").convert("RGBA")
                checar(im.size == (960, 640), "ilustracao 960x640")
                checar(im.getpixel((2, 2))[3] == 0, "canto magenta ficou transparente")
                checar(im.getpixel((480, 320))[3] == 255, "centro do objeto ficou opaco")
                # halo: pixels semi-transparentes nao podem ser rosados (R e B altos com G baixo)
                rosados = sum(1 for p in im.getdata() if 0 < p[3] < 255 and p[0] > 200 and p[2] > 200 and p[1] < 120)
                checar(rosados < 50 if org.np is not None else True, f"halo rosado: {rosados} px")
            if (a / "fundos/fundo_hero_ilha.webp").exists():
                checar(Image.open(a / "fundos/fundo_hero_ilha.webp").size == (1600, 700), "hero 1600x700")
            if (saida / "favicon.png").exists():
                checar(Image.open(saida / "favicon.png").size == (32, 32), "favicon 32")

        # modo exportar manifesto
        csvp = tmp / "esperado.csv"
        org.main(["--exportar-manifesto", str(csvp)])
        linhas = csvp.read_text(encoding="utf-8").strip().splitlines()
        checar(len(linhas) == 67, f"manifesto esperado com 66 itens (+cabecalho): {len(linhas)}")
        m = org.construir_manifesto()
        por = {p: sum(1 for i in m if i["prio"] == p) for p in ("P0", "P1", "P2")}
        checar(por == {"P0": 9, "P1": 25, "P2": 32}, f"prioridades P0/P1/P2 = {por}")

    print("\nRESULTADO:", "TUDO OK" if checar.falhas == 0 else f"{checar.falhas} FALHA(S)")
    return 1 if checar.falhas else 0


if __name__ == "__main__":
    sys.exit(main())
