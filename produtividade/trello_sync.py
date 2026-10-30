"""Sincroniza produtividade/kanban.md (Guardiola) com o quadro "Kanban Trabalho" do Trello.

Mão dupla, e o Guilherme sempre ganha: o que ele mexe no Trello (mover, renomear,
criar, arquivar cartão, criar coluna) vale e é copiado para o kanban.md; os agentes
nunca desfazem isso. O que o agente muda no kanban.md (cartão novo ou cartão movido)
só vai para o Trello se o Guilherme não tiver mexido naquele cartão desde a última
rodada. Em conflito, vale o Trello.

Garantias:
- nunca apaga cartão no Trello (nem arquiva); nunca altera descrição, etiqueta, prazo
  ou comentário de cartão; só cria cartão novo e move coluna quando o agente pediu;
- nunca mexe em outro quadro da conta;
- cartão arquivado/excluído no Trello sai do kanban.md e não é recriado.

Estado da última rodada: .trello_quadro.json (cartão por id: título e coluna).
Credenciais só no .env: TRELLO_API_KEY e TRELLO_TOKEN (ou TRELLO_API_TOKEN).

Uso:
  python produtividade/trello_sync.py             sincroniza
  python produtividade/trello_sync.py --simular   mostra o que faria, sem alterar nada
"""
import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

import avisar
from avisar import PASTA

KANBAN = PASTA / "kanban.md"
BACKUP = PASTA / ".kanban.bak.md"
ESTADO = PASTA / ".trello_quadro.json"
NOME_QUADRO = "Kanban Trabalho"
COLUNAS_INICIAIS = ["Backlog", "Pronto para fazer", "Fazendo", "Bloqueado", "Feito"]
SECAO_NAO_COLUNA = "Recados"


def api(metodo, caminho, **params):
    params = {"key": os.environ["TRELLO_API_KEY"],
              "token": os.environ.get("TRELLO_TOKEN") or os.environ["TRELLO_API_TOKEN"], **params}
    dados = urllib.parse.urlencode(params)
    if metodo == "GET":
        req = urllib.request.Request(f"https://api.trello.com/1/{caminho}?{dados}")
    else:
        req = urllib.request.Request(f"https://api.trello.com/1/{caminho}", data=dados.encode(), method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Trello recusou {metodo} {caminho}: {e.code} {e.read()[:150]!r}")


def ler_kanban():
    """(cabecalho, {coluna: [(titulo, desc)]}, extras) do kanban.md. extras = seções que não são coluna."""
    cabecalho, colunas, extras, atual, no_extra = [], {}, [], None, False
    for linha in KANBAN.read_text(encoding="utf-8").splitlines():
        if linha.startswith("## "):
            nome = linha[3:].strip()
            if nome == SECAO_NAO_COLUNA:
                atual, no_extra = None, True
                extras.append(linha)
            else:
                atual, no_extra = nome, False
                colunas.setdefault(nome, [])
        elif no_extra:
            extras.append(linha)
        elif atual is None:
            cabecalho.append(linha)
        elif linha.startswith("- ") and linha[2:].strip():
            titulo, _, resto = linha[2:].strip().partition(" · ")
            colunas[atual].append((titulo.strip(), resto.strip()))
    return cabecalho, colunas, extras


def escrever_kanban(cabecalho, colunas, extras):
    saida = list(cabecalho)
    while saida and not saida[-1].strip():
        saida.pop()
    for nome, cartoes in colunas.items():
        saida += ["", f"## {nome}"] + [f"- {t}" + (f" · {d}" if d else "") for t, d in cartoes]
    saida += [""] + (extras or [f"## {SECAO_NAO_COLUNA}"])
    KANBAN.write_text("\n".join(saida).rstrip() + "\n", encoding="utf-8")


def garantir_quadro(simular):
    estado = avisar.ler_json(ESTADO, {})
    if estado.get("board"):
        return estado
    if simular:
        sys.exit(f"(simulação) o quadro '{NOME_QUADRO}' ainda não existe; rode sem --simular uma vez")
    b = api("POST", "boards/", name=NOME_QUADRO, defaultLists="false", prefs_permissionLevel="private")
    for c in COLUNAS_INICIAIS:
        api("POST", f"boards/{b['id']}/lists", name=c, pos="bottom")
    estado = {"board": b["id"], "url": b["url"], "cartoes": {}}
    ESTADO.write_text(json.dumps(estado, indent=1), encoding="utf-8")
    print("quadro criado:", b["url"])
    return estado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args()
    sim = args.simular
    avisar.carregar_env()
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")

    estado = garantir_quadro(sim)
    board = estado["board"]
    listas_abertas = api("GET", f"boards/{board}/lists", filter="open", fields="name")
    id_da_lista = {l["name"]: l["id"] for l in listas_abertas}
    nome_da_lista = {l["id"]: l["name"] for l in listas_abertas}
    todos = api("GET", f"boards/{board}/cards", filter="all", fields="name,idList,closed,desc")
    abertos = [c for c in todos if not c["closed"] and c["idList"] in nome_da_lista]
    nomes_fechados = {c["name"] for c in todos if c["closed"]}
    anterior = estado.get("cartoes", {})
    nomes_conhecidos = {v["titulo"] for v in anterior.values()}

    cabecalho, colunas_md, extras = ler_kanban()
    md = {}  # titulo -> (coluna, desc)
    for col, cartoes in colunas_md.items():
        for titulo, desc in cartoes:
            md[titulo] = (col, desc)
    usados = set()
    novo = {l["name"]: [] for l in listas_abertas}  # na ordem das colunas do Trello
    novo_estado = {}

    for c in abertos:
        col_t = nome_da_lista[c["idList"]]
        ant = anterior.get(c["id"])
        chave = next((k for k in ([ant["titulo"]] if ant else []) + [c["name"]] if k in md), None)
        final, desc = col_t, " ".join(c["desc"].split())[:200]
        if chave:
            usados.add(chave)
            col_md, desc_md = md[chave]
            desc = desc_md or desc
            if ant and col_t == ant["coluna"] and col_md != ant["coluna"] and col_md in id_da_lista:
                final = col_md  # o agente moveu e o Guilherme não mexeu: vale o agente
                print(f"mover no Trello '{c['name']}' de {col_t} para {final}")
                if not sim:
                    api("PUT", f"cards/{c['id']}", idList=id_da_lista[final])
        elif ant and ant["titulo"] != c["name"]:
            print(f"renomeado no Trello: '{ant['titulo']}' -> '{c['name']}'")
        novo[final].append((c["name"], desc))
        novo_estado[c["id"]] = {"titulo": c["name"], "coluna": final}

    for titulo, (col, desc) in md.items():
        if titulo in usados:
            continue
        if titulo in nomes_conhecidos or titulo in nomes_fechados:
            print(f"'{titulo}' saiu do Trello (arquivado/excluído): sai do kanban.md, não será recriado")
            continue
        destino = col if col in id_da_lista else ("Backlog" if "Backlog" in id_da_lista else next(iter(id_da_lista)))
        print(f"criar no Trello '{titulo}' em {destino}")
        if sim:
            novo[destino].append((titulo, desc))
        else:
            novo_card = api("POST", "cards", idList=id_da_lista[destino], name=titulo, desc=desc)
            novo[destino].append((titulo, desc))
            novo_estado[novo_card["id"]] = {"titulo": titulo, "coluna": destino}

    if sim:
        return
    antes = KANBAN.read_text(encoding="utf-8")
    shutil.copyfile(KANBAN, BACKUP)
    escrever_kanban(cabecalho, novo, extras)
    if KANBAN.read_text(encoding="utf-8") != antes:
        print("kanban.md atualizado a partir do Trello")
    estado["cartoes"] = novo_estado
    ESTADO.write_text(json.dumps(estado, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
