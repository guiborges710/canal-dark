"""Espelha o backlog e o quadro do setor de programação no Kanban geral (kanban.md).

Fontes (lidas, nunca alteradas): programacao/backlog.md (Zico) e programacao/quadro.md (Xavi).
Destino: produtividade/kanban.md, que o trello_sync.py leva ao Trello ("Kanban Trabalho").

Regras:
- cada item vira um cartão `[Sprint 01] [PROG-NNN] título` (ou `[Backlog] ...`; sprint em programacao_sprint.json) (candidatos do quadro: `[PROG-C-01] ...`);
  o id PROG-NNN, em qualquer posição do título, identifica o cartão, então rodar de novo não duplica;
- o título do cartão não muda sozinho depois de criado (renomear Sprint/Backlog: trello_programacao.py --atualizar);
  o estado fino (Em teste, Pronto para aceite...) vai no texto do cartão, depois do " · ";
- só move a linha quando o ESTADO NO QUADRO mudou desde a última rodada (estado em
  .kanban_programacao.json); se o Guilherme moveu o cartão no Trello, isso não é desfeito;
- cartão que sumiu do kanban.md (arquivado pelo Guilherme) não é recriado;
- nunca apaga nada do kanban.md, nem cartões pessoais; só mexe em linhas cujo título tem um id PROG-.

Mapa de colunas (quadro do Xavi -> coluna do Kanban geral):
  Backlog da sprint        -> Backlog
  Em refinamento técnico   -> Backlog
  Fazendo                  -> Fazendo
  Em teste                 -> Em teste
  Code Review             -> Code Review
  Pronto para aceite       -> Pronto para aceite
  Feito                    -> Feito
  Bloqueado                -> Bloqueado
  (item só no backlog.md, fora do quadro -> Backlog)

Uso:
  python produtividade/kanban_programacao.py --simular   mostra o que faria, sem escrever
  python produtividade/kanban_programacao.py             atualiza o kanban.md (o trello_sync leva ao Trello)
O trello_sync.py também chama este módulo antes de sincronizar.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
BACKLOG = RAIZ / "programacao" / "backlog.md"
QUADRO = RAIZ / "programacao" / "quadro.md"
ESTADO = PASTA / ".kanban_programacao.json"
LIBERACAO = PASTA / ".liberar_programacao"  # trava: sem este arquivo, a ponte só simula e nada vai ao Kanban nem ao Trello
BACKUP = PASTA / ".kanban_programacao.bak.md"

MAPA = {
    "Backlog da sprint": "Backlog",
    "Em refinamento técnico": "Backlog",
    "Fazendo": "Fazendo",
    "Em teste": "Em teste",
    "Code Review": "Code Review",
    "Pronto para aceite": "Pronto para aceite",
    "Feito": "Feito",
    "Bloqueado": "Bloqueado",
}
PADRAO = "Backlog"
ID = r"(PROG-C-\d+|PROG-\d+|C-\d+)"
ID_NO_TITULO = re.compile(r"PROG-(?:C-)?\d+", re.I)
SPRINT_ARQ = PASTA / "programacao_sprint.json"  # {"PROG-001": "Sprint 01", ...}: o Xavi/Zico mudam depois da planning
SPRINT_PADRAO = "Backlog"


def id_do_titulo(titulo):
    """O id PROG-NNN em qualquer posição do título (ou None). É assim que o cartão é reconhecido."""
    m = ID_NO_TITULO.search(titulo or "")
    return m.group(0).upper() if m else None


def sprint_do_item(tag):
    try:
        mapa = json.loads(SPRINT_ARQ.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        mapa = {}
    return mapa.get(tag, SPRINT_PADRAO)


def titulo_do_cartao(tag, nome):
    return _limpo(f"[{sprint_do_item(tag)}] [{tag}] {nome}")


def _tag(i):
    return i if i.startswith("PROG-") else f"PROG-{i}"


def _limpo(t):
    return " ".join(t.replace(" · ", " - ").split())


def ler_backlog(caminho=BACKLOG):
    """{tag: {titulo, prioridade}}"""
    itens, atual = {}, None
    if not caminho.exists():
        return itens
    curtos = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():  # tabela de resumo: título curto de cartão do Zico
        c = [x.strip() for x in linha.strip().strip("|").split("|")]
        if linha.startswith("|") and len(c) >= 4 and re.fullmatch(r"PROG-\d+", c[1]):
            curtos[c[1]] = c[2].strip('"') if not c[2].startswith('"') or c[2].count('"') < 2 else c[2]
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        m = re.match(rf"^## {ID} · [^·]+ · Prioridade (\w+)", linha)
        if m:
            atual = _tag(m.group(1))
            itens[atual] = {"titulo": curtos.get(atual, ""), "prioridade": m.group(2)}
        elif linha.startswith("## "):
            atual = None
        elif atual and linha.startswith("**Título:**") and not itens[atual]["titulo"]:
            itens[atual]["titulo"] = linha.split(":**", 1)[1].strip().rstrip(".")
    return itens


def ler_quadro(caminho=QUADRO):
    """{tag: {coluna, texto}} com a coluna do Xavi."""
    itens, col = {}, None
    if not caminho.exists():
        return itens
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith("## "):
            nome = linha[3:].split("(")[0].strip()
            col = nome if nome in MAPA else None
        elif col and linha.startswith("- "):
            m = re.match(rf"^- \[?{ID}\]?(?: · |\s+)(.*)$", linha)
            if m:
                texto = re.sub(r"\s*\((alta|média|media|baixa)\)\.?.*$", "", m.group(2)).strip()
                itens[_tag(m.group(1))] = {"coluna": col, "texto": texto.rstrip(".")}
    return itens


def montar(backlog, quadro):
    """[(tag, titulo_do_cartao, coluna_geral, estado_fino, desc)] na ordem: backlog.md, depois só-quadro."""
    saida = []
    for tag in list(backlog) + [t for t in quadro if t not in backlog]:
        b, q = backlog.get(tag, {}), quadro.get(tag, {})
        nome = b.get("titulo") or q.get("texto") or tag
        estado = q.get("coluna", "Backlog da sprint" if tag.startswith("PROG-C-") else "novo")
        col = MAPA.get(estado, PADRAO)
        partes = ["projeto Canal dark (programação)", f"estado: {estado}"]
        if b.get("prioridade"):
            partes.append(f"prioridade {b['prioridade']}")
        partes.append("fonte: programacao/backlog.md e quadro.md (quem move é o Xavi/Zico)")
        saida.append((tag, titulo_do_cartao(tag, nome), col, estado, " · ".join(partes)))
    return saida


def mesclar(colunas, simular=False, backlog=None, quadro=None, estado_antigo=None):
    """Aplica os itens em `colunas` ({coluna: [(titulo, desc)]}), no lugar. Devolve o novo estado."""
    estado_antigo = ESTADO_LER() if estado_antigo is None else estado_antigo
    if not simular and not LIBERACAO.exists():
        print("[programação] ponte travada (falta produtividade/.liberar_programacao): nenhum cartão [PROG-...] será criado ainda")
        return estado_antigo
    backlog = ler_backlog() if backlog is None else backlog
    quadro = ler_quadro() if quadro is None else quadro
    novo_estado = dict(estado_antigo)
    for tag, titulo, col, fino, desc in montar(backlog, quadro):
        achado = next(((c, i) for c, cs in colunas.items() for i, (t, _) in enumerate(cs)
                       if id_do_titulo(t) == tag), None)
        if achado is None:
            if tag in estado_antigo:
                print(f"[programação] {tag} saiu do Kanban (arquivado/removido pelo Guilherme): não recrio")
                continue
            colunas.setdefault(col, []).append((titulo, desc))
            novo_estado[tag] = {"coluna": col, "estado": fino}
            print(f"[programação] novo cartão em {col}: {titulo}  ({fino})")
            continue
        c, i = achado
        t_atual, _ = colunas[c][i]
        ant = estado_antigo.get(tag)
        if ant and ant["coluna"] != col:
            # o quadro do Xavi mudou de coluna geral: move a linha (o Trello só acompanha se o Guilherme não mexeu)
            del colunas[c][i]
            colunas.setdefault(col, []).append((t_atual, desc))
            print(f"[programação] mover {tag}: {c} -> {col}  ({fino})")
        else:
            colunas[c][i] = (t_atual, desc)  # só o texto (estado fino) atualiza
            if ant and ant.get("estado") != fino:
                print(f"[programação] {tag}: estado fino agora '{fino}' (coluna {c} mantida)")
        novo_estado[tag] = {"coluna": col, "estado": fino}
    return novo_estado


def ESTADO_LER():
    try:
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def salvar_estado(estado):
    ESTADO.write_text(json.dumps(estado, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--kanban", help="outro kanban.md (testes)")
    ap.add_argument("--estado", help="outro arquivo de estado (testes)")
    args = ap.parse_args()
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(PASTA))
    import trello_sync as ts
    global ESTADO
    if args.estado:
        ESTADO = Path(args.estado)
    caminho = Path(args.kanban) if args.kanban else ts.KANBAN
    ts.KANBAN = caminho
    cab, colunas, extras = ts.ler_kanban()
    novo = mesclar(colunas)
    if args.simular:
        print("(simulação) nada foi escrito")
        return
    shutil.copyfile(caminho, BACKUP if not args.kanban else caminho.with_suffix(".bak"))
    ts.escrever_kanban(cab, colunas, extras)
    salvar_estado(novo)
    print("kanban.md atualizado; o trello_sync.py leva os cartões novos ao Trello")


if __name__ == "__main__":
    main()
