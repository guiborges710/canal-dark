"""Gera o dashboard financeiro a partir de movimentos.csv e saldos.csv.

Saídas (zero token, só leitura local):
  financas/dashboard.html   para o computador (abre com duplo clique; tema claro/escuro; tabela)
  financas/dashboard.png    para o celular (o Ronaldo manda no Telegram)

Os dados não saem do computador. Uso: python financas/dashboard.py
"""
import csv
import html
import sys
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PASTA = Path(__file__).resolve().parent
HOJE = date.today()

# paleta de referência do skill dataviz (azul = categoria 1; vermelho = status crítico)
AZUL, CRITICO, OK = "#2a78d6", "#d03b3b", "#0ca30c"
SUPERFICIE, PAGINA = "#fcfcfb", "#f9f9f7"
TINTA, TINTA2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dia(d):
    return d.strftime("%d/%m")


def carregar():
    movs = []
    with (PASTA / "movimentos.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            r["valor"] = float(r["valor"])
            r["data"] = datetime.strptime(r["data"], "%Y-%m-%d").date()
            movs.append(r)
    saldos = list(csv.DictReader((PASTA / "saldos.csv").open(encoding="utf-8", newline="")))
    return movs, saldos


def metricas(movs):
    entradas = [m for m in movs if m["tipo"] == "recebido"]
    pagos = [m for m in movs if m["tipo"] == "gasto" and m["status"] == "pago"]
    pend = sorted((m for m in movs if m["tipo"] == "gasto" and m["status"] == "a pagar"), key=lambda m: m["data"])
    ultimo = max(entradas, key=lambda m: m["data"]) if entradas else None
    t_ent, t_pag, t_pend = (round(sum(m["valor"] for m in x), 2) for x in (entradas, pagos, pend))
    return {
        "entradas": t_ent, "saidas": t_pag, "pendentes": t_pend, "pend": pend,
        "resultado": round(t_ent - t_pag, 2), "apos_pend": round(t_ent - t_pag - t_pend, 2),
        "ultimo": ultimo, "sobra": round(ultimo["valor"] - t_pend, 2) if ultimo else None,
        "vencidas": round(sum(m["valor"] for m in pend if m["data"] < HOJE), 2),
    }


def situacao(m):
    d = (m["data"] - HOJE).days
    if d < 0:
        return f"VENCIDA há {-d} dia{'s' if -d != 1 else ''}", True
    return ("vence hoje", False) if d == 0 else (f"vence em {d} dia{'s' if d != 1 else ''}", False)


# ---------------------------------------------------------------- PNG (celular)

def fonte(tam, negrito=False):
    for nome in ("segoeuib.ttf" if negrito else "segoeui.ttf", "arialbd.ttf" if negrito else "arial.ttf"):
        try:
            return ImageFont.truetype(rf"C:\Windows\Fonts\{nome}", tam)
        except OSError:
            continue
    return ImageFont.load_default()


def quebrar(d, texto, f, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if d.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    return linhas + [atual]


def gerar_png(m, saldos):
    W, M = 1080, 48
    img = Image.new("RGB", (W, 2600), PAGINA)
    d = ImageDraw.Draw(img)
    y = M

    d.text((M, y), "Finanças", font=fonte(54, True), fill=TINTA)
    d.text((W - M, y + 22), f"atualizado em {HOJE:%d/%m/%Y}", font=fonte(28), fill=MUDO, anchor="ra")
    y += 100

    # hero
    d.rounded_rectangle((M, y, W - M, y + 250), 28, fill=SUPERFICIE, outline=GRADE, width=2)
    d.text((M + 36, y + 28), "Sobra após as contas pendentes", font=fonte(30), fill=TINTA2)
    if m["sobra"] is not None:
        d.text((M + 36, y + 70), brl(m["sobra"]), font=fonte(88, True), fill=TINTA)
        sub = f"{brl(m['ultimo']['valor'])} recebidos em {dia(m['ultimo']['data'])} menos {brl(m['pendentes'])} em contas"
        d.text((M + 36, y + 186), sub, font=fonte(26), fill=TINTA2)
    y += 250 + 24

    # tiles 2x2
    tiles = [("Entradas", m["entradas"]), ("Saídas pagas", m["saidas"]),
             ("Resultado das movimentações", m["resultado"]), ("Contas a pagar", m["pendentes"])]
    larg = (W - 2 * M - 24) // 2
    for i, (rot, val) in enumerate(tiles):
        x0 = M + (i % 2) * (larg + 24)
        y0 = y + (i // 2) * (170 + 24)
        d.rounded_rectangle((x0, y0, x0 + larg, y0 + 170), 24, fill=SUPERFICIE, outline=GRADE, width=2)
        d.text((x0 + 28, y0 + 26), rot, font=fonte(26), fill=TINTA2)
        d.text((x0 + 28, y0 + 74), brl(val), font=fonte(48, True), fill=TINTA)
    y += 2 * 170 + 24 + 40

    # contas a pagar por vencimento
    d.text((M, y), "Contas a pagar, por vencimento", font=fonte(38, True), fill=TINTA)
    y += 70
    maximo = max((p["valor"] for p in m["pend"]), default=1)
    barra_x0, barra_larg = M, W - 2 * M
    for p in m["pend"]:
        texto, vencida = situacao(p)
        cor = CRITICO if vencida else AZUL
        d.text((barra_x0, y), p["descricao"].split(" (")[0], font=fonte(30, True), fill=TINTA)
        d.text((W - M, y + 2), f"{dia(p['data'])} · {texto}", font=fonte(26, vencida), fill=CRITICO if vencida else TINTA2, anchor="ra")
        w = max(int(barra_larg * 0.80 * p["valor"] / maximo), 10)
        d.rounded_rectangle((barra_x0, y + 52, barra_x0 + w, y + 88), 8, fill=cor)
        d.text((barra_x0 + w + 16, y + 52), brl(p["valor"]), font=fonte(30, True), fill=TINTA)
        y += 120
    y += 4
    d.line((M, y, W - M, y), fill=GRADE, width=2)
    y += 28

    # aviso de saldo
    saldo = saldos[0] if saldos else None
    aviso = ("Saldo bancário real: NÃO CONFIRMADO. "
             + (f"Último saldo informado: {saldo['conta']} {brl(float(saldo['saldo']))} em "
                f"{datetime.strptime(saldo['data'], '%Y-%m-%d'):%d/%m} (histórico). " if saldo else "")
             + "A sobra acima não inclui alimentação, transporte, juros nem multas.")
    fa = fonte(27)
    linhas = quebrar(d, aviso, fa, W - 2 * M - 100)
    alt = 40 + len(linhas) * 38
    d.rounded_rectangle((M, y, W - M, y + alt), 22, fill=SUPERFICIE, outline="#eda100", width=3)
    d.text((M + 28, y + 18), "!", font=fonte(40, True), fill="#eda100")
    for i, ln in enumerate(linhas):
        d.text((M + 76, y + 20 + i * 38), ln, font=fa, fill=TINTA)
    y += alt + 28
    d.text((M, y), "Soma contábil das movimentações; não é saldo em banco.", font=fonte(23), fill=MUDO)
    y += 60

    img.crop((0, 0, W, y)).save(PASTA / "dashboard.png", optimize=True)


# ---------------------------------------------------------------- HTML (computador)

def gerar_html(m, movs, saldos):
    e = html.escape
    maximo = max((p["valor"] for p in m["pend"]), default=1)
    barras = ""
    for p in m["pend"]:
        texto, vencida = situacao(p)
        barras += f"""
      <div class="linha" title="{e(p['descricao'])}: {brl(p['valor'])}, {dia(p['data'])} ({texto})">
        <div class="cab"><strong>{e(p['descricao'].split(' (')[0])}</strong>
          <span class="{'venc' if vencida else ''}">{'⚠ ' if vencida else ''}{dia(p['data'])} · {texto}</span></div>
        <div class="trilho"><div class="barra {'critica' if vencida else ''}" style="width:{max(p['valor'] / maximo * 80, 2):.1f}%"></div>
          <span class="val">{brl(p['valor'])}</span></div>
      </div>"""
    linhas = "".join(
        f"<tr><td>{r['data']:%d/%m/%Y}</td><td>{e(r['tipo'])}</td><td>{e(r['categoria'])}</td>"
        f"<td>{e(r['descricao'])}</td><td class='n'>{brl(r['valor'])}</td><td>{e(r['status'])}</td></tr>"
        for r in sorted(movs, key=lambda r: r["data"]))
    tiles = "".join(
        f"<div class='tile'><span>{e(r)}</span><b>{brl(v)}</b></div>"
        for r, v in [("Entradas", m["entradas"]), ("Saídas pagas", m["saidas"]),
                     ("Resultado das movimentações", m["resultado"]), ("Contas a pagar", m["pendentes"])])
    hero = ""
    if m["sobra"] is not None:
        hero = (f"<div class='hero'><span>Sobra após as contas pendentes</span><b>{brl(m['sobra'])}</b>"
                f"<small>{brl(m['ultimo']['valor'])} recebidos em {dia(m['ultimo']['data'])} menos {brl(m['pendentes'])} em contas</small></div>")
    s = saldos[0] if saldos else None
    aviso = ("Saldo bancário real: <b>NÃO CONFIRMADO</b>. "
             + (f"Último saldo informado: {e(s['conta'])} {brl(float(s['saldo']))} em {s['data'][8:]}/{s['data'][5:7]} (histórico). " if s else "")
             + "A sobra não inclui alimentação, transporte, juros nem multas.")
    (PASTA / "dashboard.html").write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Finanças</title>
<style>
:root{{color-scheme:light;--bg:#f9f9f7;--sf:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mudo:#898781;--grade:#e1e0d9;--azul:#2a78d6;--crit:#d03b3b;--aviso:#eda100}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{color-scheme:dark;--bg:#0d0d0d;--sf:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grade:#2c2c2a;--azul:#3987e5;--crit:#e66767}}}}
:root[data-theme="dark"]{{color-scheme:dark;--bg:#0d0d0d;--sf:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grade:#2c2c2a;--azul:#3987e5;--crit:#e66767}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:760px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:28px;margin:0 0 4px}} .data{{color:var(--mudo);margin-bottom:20px}}
.hero,.tile,.aviso,.grafico{{background:var(--sf);border:1px solid var(--grade);border-radius:16px;padding:18px 20px}}
.hero span,.tile span{{color:var(--ink2);display:block}} .hero b{{font-size:44px;display:block;margin:4px 0}} .hero small{{color:var(--ink2)}}
.tiles{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0 20px}} .tile b{{font-size:24px}}
h2{{font-size:20px;margin:24px 0 10px}} .grafico{{display:grid;gap:14px}}
.cab{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}} .cab span{{color:var(--ink2)}} .cab .venc{{color:var(--crit);font-weight:700}}
.trilho{{display:flex;align-items:center;gap:10px;margin-top:6px}} .barra{{height:18px;border-radius:4px;background:var(--azul)}} .barra.critica{{background:var(--crit)}}
.val{{font-weight:700}} .aviso{{border-color:var(--aviso);border-width:2px;margin-top:20px}}
details{{margin-top:24px}} summary{{cursor:pointer;font-weight:700}} table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}
td,th{{padding:6px 8px;border-bottom:1px solid var(--grade);text-align:left}} .n{{text-align:right;white-space:nowrap}}
.rodape{{color:var(--mudo);font-size:13px;margin-top:20px}}
</style></head><body><main>
<h1>Finanças</h1><div class="data">atualizado em {HOJE:%d/%m/%Y}</div>
{hero}
<div class="tiles">{tiles}</div>
<h2>Contas a pagar, por vencimento</h2>
<div class="grafico">{barras}</div>
<div class="aviso">⚠ {aviso}</div>
<details><summary>Ver todas as movimentações (tabela)</summary>
<table><tr><th>Data</th><th>Tipo</th><th>Categoria</th><th>Descrição</th><th class="n">Valor</th><th>Status</th></tr>{linhas}</table></details>
<div class="rodape">Soma contábil das movimentações; não é saldo em banco. Dados só neste computador.</div>
</main></body></html>""", encoding="utf-8")


def main():
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    movs, saldos = carregar()
    m = metricas(movs)
    gerar_png(m, saldos)
    gerar_html(m, movs, saldos)
    print(f"entradas {brl(m['entradas'])} | saídas {brl(m['saidas'])} | resultado {brl(m['resultado'])} | "
          f"pendentes {brl(m['pendentes'])} | após pendências {brl(m['apos_pend'])} | sobra {brl(m['sobra'])}")


if __name__ == "__main__":
    main()
