"""Publica no Trello ("Kanban Trabalho") os cartões completos do setor de programação.

Autorizado pelo Guilherme (2026-11-03): criar cartões [PROG-...], etiquetas do quadro,
descrição e checklist dos cartões que ESTE script cria, e anexar imagens neles.
Proibido (e o script não faz): apagar/arquivar cartão, mexer em cartão que não tenha id PROG,
tocar em outro quadro, mexer em etiqueta/descrição de cartão do Guilherme.

Fontes (só leitura): programacao/backlog.md, quadro.md, sprints/prep/{thiago-silva,alisson,iniesta}.md,
ux/prog-003-aba-agentes.md e produtividade/programacao_sprint.json (Sprint 01 x Backlog).
Idempotência: o cartão é reconhecido pelo id PROG-NNN em qualquer posição do título
(abertos e arquivados). Se existir, não cria outro; só completa etiquetas que faltem.
Com --atualizar, também acerta o prefixo [Sprint NN]/[Backlog] e a etiqueta de sprint
dos cartões PROG (para o Xavi/Zico depois da planning). Nunca remove etiqueta de outro tipo.

Uso:
  python produtividade/trello_programacao.py --simular     mostra o plano
  python produtividade/trello_programacao.py               cria o que falta
  python produtividade/trello_programacao.py --atualizar   idem + acerta sprint de cartões existentes
"""
import argparse
import json
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))
import avisar  # noqa: E402
import kanban_programacao as kp  # noqa: E402
import trello_sync as ts  # noqa: E402

RAIZ = PASTA.parent
PROG = RAIZ / "programacao"

CORES = {
    "Sprint 01": "blue_dark", "Backlog": "black_light", "Programação": "purple",
    "Bug": "red", "Melhoria": "green", "Dívida técnica": "orange", "Teste": "lime",
    "Prioridade alta": "red_dark", "Prioridade média": "yellow", "Prioridade baixa": "sky",
    "Dev back": "sky_dark", "Dev front": "pink", "QA": "lime_dark", "UX": "purple_light", "DevOps": "black",
    "Dono: Luiz Henrique": "yellow_light", "Dono: Rodrygo": "blue", "Dono: Alisson": "green_dark",
    "Dono: Iniesta": "pink_dark", "Dono: Endrick": "orange_dark", "Dono: Marquinhos": "sky_light",
    "Dono: Thiago Silva": "red_light", "Dono: Zico": "yellow_dark", "Dono: Xavi": "purple_dark",
    "Dono: Zico (a definir)": "yellow_dark",
}
AGENTES = ["Rodrygo", "Endrick", "Alisson", "Iniesta", "Marquinhos", "Thiago Silva", "Zico", "Xavi", "Luiz Henrique"]
TIPO = {"PROG-001": "Bug", "PROG-002": "Bug", "PROG-003": "Melhoria", "PROG-004": "Teste", "PROG-005": "Dívida técnica",
        "PROG-006": "Melhoria", "PROG-007": "Dívida técnica", "PROG-008": "Melhoria", "PROG-009": "Bug", "PROG-010": "Bug",
        "PROG-011": "Melhoria", "PROG-012": "Melhoria",
        "PROG-013": "Melhoria", "PROG-014": "Melhoria", "PROG-015": "Bug"}
PRIORIDADE = {"alta": "Prioridade alta", "média": "Prioridade média", "media": "Prioridade média", "baixa": "Prioridade baixa"}
# responsável principal (quem o Thiago Silva indica na coluna "Quem" de prep/thiago-silva.md)
RESP = {"PROG-001": ["QA"], "PROG-002": ["QA"], "PROG-003": ["Dev back", "Dev front", "UX"], "PROG-004": ["Dev back"],
        "PROG-005": ["QA", "Dev back"], "PROG-006": ["Dev front", "UX"], "PROG-007": ["Dev back"],
        "PROG-008": ["Dev front", "Dev back"], "PROG-009": ["Dev front"], "PROG-010": ["DevOps"],
        "PROG-011": ["Dev back", "Dev front", "UX"], "PROG-012": ["Dev back", "Dev front", "UX"],
        "PROG-013": [], "PROG-014": [], "PROG-015": ["Dev front", "Dev back"]}
RESP_TEXTO = {
    "PROG-001": "Validação: **Alisson** (QA) e o Guilherme. Atendido por **Rodrygo** (back) e **Endrick** (front).",
    "PROG-002": "Validação: **Alisson** (QA) e o Guilherme. Atendido por **Rodrygo** (back) e **Endrick** (front).",
    "PROG-003": "**Rodrygo** (back), **Endrick** (front), desenho do **Iniesta** (UX); **Alisson** (QA).",
    "PROG-004": "**Rodrygo**; **Alisson** valida; **Marquinhos** para o ambiente do Codex.",
    "PROG-005": "**Alisson** (diagnóstico) e **Rodrygo**/**Endrick** (ajuste); **Thiago Silva** confere as asserções.",
    "PROG-006": "**Iniesta** (desenho) e depois **Endrick**.",
    "PROG-007": "**Rodrygo**, após decisão do Guilherme.",
    "PROG-008": "**Iniesta**, depois **Endrick** e **Rodrygo**; **Alisson**.",
    "PROG-009": "**Thiago Silva** (causa) e depois **Endrick**; **Alisson** (e2e).",
    "PROG-010": "**Marquinhos** (dono provável).",
    "PROG-011": "**Rodrygo** (back), **Endrick** (front) e desenho do **Iniesta** (UX); a refinar pelo **Thiago Silva**.",
    "PROG-012": "**Rodrygo** (back), **Endrick** (front) e desenho do **Iniesta** (UX); a refinar pelo **Thiago Silva**.",
}
RESP_TEXTO["PROG-013"] = "**Luiz Henrique** (cria o agente e decide a estrutura); **Alisson** confere os relatórios; **Ronaldo** agenda; decisão de ferramentas do Guilherme."
RESP_TEXTO["PROG-014"] = "**Luiz Henrique** (cria o agente e decide a estrutura); **Alisson** confere uma entrega real; integra com o PROG-013."
RESP_TEXTO["PROG-015"] = "Refinamento de **Thiago Silva**; implementação proposta para **Endrick** (front) com apoio de **Rodrygo** (back); validação de **Alisson**."
RESP_PADRAO = ["Dev back"]
TEXTO_PADRAO = "A definir pelo **Xavi**/**Zico** na planning."
ANTIGO = {"C-01": "PROG-004", "C-02": "PROG-005", "C-03": "PROG-006", "C-04": "PROG-007",
          "C-05": "PROG-008", "C-06": "PROG-009", "C-07": "PROG-010"}
COMO_TESTAR_EXTRA = {
    "PROG-004": "`testar_reserva_codex.py` cobre o backend (`executor.py` 158-209): limite do Claude, escolha de motor, comando do codex (montado, nunca executado) e a nota \"não pôde rodar\"; não cobre o front. Validação sem código novo (**Thiago Silva**): rodar o teste simulado e um caso real controlado simulando a mensagem de limite, sem esgotar a conta de verdade.",
    "PROG-005": "Princípio de **Alisson**: executor simulado (`ESTUDIO_SIMULADOR`, `claude_simulado.py`, `comandos_simulados.py`), zero token, caixa descartável. Rodar `e2e_estilos`, `e2e_interface`, `e2e_corte` e os testes de contagem de nós; registrar o resultado real em `qa/PROG-005.md`. Falsos verdes a corrigir: `e2e_corte.mjs` l.419 (`.catch(() => true)`) e l.420 (`.catch(() => {})`). Estimativa de **Alisson** para deixar a regressão verde: M (1 a 2 dias), G se aparecer quebra além do mapeado.",
}
DESENHO_EXTRA = {
    "PROG-006": "Sem desenho separado: **Thiago Silva** recomenda um só desenho de **Iniesta** para PROG-003 e PROG-006 (selo do motor Claude/Codex e nota da reserva; ver o cartão do PROG-003).",
    "PROG-008": "Depende de desenho do **Iniesta** (botão com confirmação, listando o que muda). Ainda não desenhado.",
}


def _sec(texto, ini, fim):
    m = re.search(rf"^{re.escape(ini)}\s*$(.*?)(?=^{re.escape(fim)}|\Z)", texto, re.S | re.M)
    return m.group(1).strip() if m else ""


def dono_e_apoio(tag, corpo):
    """(dono, apoio[]) do item: campo `**Dono:**` do backlog.md; sem dono -> 'Zico (a definir)'."""
    m = re.search(r"^\*\*Dono:\*\*\s*(.+)$", corpo, re.M)
    dono = None
    if m:
        txt = re.sub(r"[*`]", "", m.group(1))
        dono = next((a for a in AGENTES if txt.startswith(a)), None) or re.split(r"\s*[(,;]", txt)[0].strip() or None
    if not dono:
        return "Zico (a definir)", []
    apoio = []
    for n in re.findall(r"\*\*(.+?)\*\*", RESP_TEXTO.get(tag, "")):
        if n in AGENTES and n != dono and n not in apoio:
            apoio.append(n)
    return dono, apoio


def linha_dono(dono, apoio):
    return f"**Dono:** {dono}" + (f" · Apoio: {', '.join(apoio)}" if apoio else "")


def com_linha_dono(desc, linha):
    resto = (desc or "").split("\n")
    if resto and resto[0].startswith("**Dono:**"):
        resto = resto[1:]
        while resto and not resto[0].strip():
            resto = resto[1:]
    return linha + "\n\n" + "\n".join(resto)


def _novo_id(txt):
    return re.sub(r"\bC-0(\d)\b", lambda m: ANTIGO.get(m.group(0), m.group(0)), txt)


def ler_blocos_backlog():
    texto = (PROG / "backlog.md").read_text(encoding="utf-8")
    blocos = {}
    for m in re.finditer(r"^## (PROG-\d+) · (.*?)\n(.*?)(?=^## |\Z)", texto, re.S | re.M):
        blocos[m.group(1)] = (m.group(2), m.group(3).strip())
    tabela = {}
    for linha in texto.splitlines():
        c = [x.strip() for x in linha.strip().strip("|").split("|")]
        if linha.startswith("|") and len(c) >= 7 and re.fullmatch(r"PROG-\d+", c[1]):
            tabela[c[1]] = {"valor": c[4], "classe": c[5], "porque": c[6]}
    return blocos, tabela


def ler_thiago():
    linhas = {}
    for linha in (PROG / "sprints/prep/thiago-silva.md").read_text(encoding="utf-8").splitlines():
        if not linha.startswith("| PROG-") and not linha.startswith("| C-"):
            continue
        c = [x.strip() for x in linha.strip().strip("|").split(" | ")]
        m = re.match(r"(PROG-\d+|C-\d+)", c[0])
        if m and len(c) >= 7:
            tag = ANTIGO.get(m.group(1), m.group(1))
            linhas[tag] = [_novo_id(x) for x in c]
    return linhas


def ler_alisson():
    texto = (PROG / "sprints/prep/alisson.md").read_text(encoding="utf-8")
    plano = {}
    for m in re.finditer(r"^\*\*(PROG-\d+) \((.*?)\)\*\*\n(.*?)(?=^\*\*PROG-|^## |\Z)", texto, re.S | re.M):
        plano[m.group(1)] = f"**{m.group(2)}**\n" + m.group(3).strip()
    return plano


def ler_ux003():
    t = (PROG / "sprints/prep/iniesta.md").read_text(encoding="utf-8")
    prop = _sec(t, "## Proposta", "## Alternativas")
    alt = _sec(t, "## Alternativas", "## Dúvidas")
    duv = _sec(t, "## Dúvidas", "## Outros")
    return (f"Proposta de **Iniesta** (detalhe completo em `programacao/ux/prog-003-aba-agentes.md`):\n{prop}\n\n"
            f"**Alternativas**\n{alt}\n\n**Dúvidas abertas para o Zico/Guilherme**\n{duv}")


def montar_cartoes():
    blocos, tabela = ler_blocos_backlog()
    thiago, alisson, ux003 = ler_thiago(), ler_alisson(), ler_ux003()
    backlog, quadro = kp.ler_backlog(), kp.ler_quadro()
    plano = []
    for tag, titulo, col, fino, _ in kp.montar(backlog, quadro):
        if tag not in blocos:
            continue
        cab, corpo = blocos[tag]
        prio = PRIORIDADE.get(backlog[tag]["prioridade"].lower(), "Prioridade média")
        criterios = re.findall(r"^\d+\. (.*)$", corpo, re.M)
        antes = corpo.split("**Critérios de aceite")[0]
        valor_linha = re.search(r"\*\*Valor:\*\*\s*(.*?)\.\s*(?:\*\*Depende de:\*\*\s*(.*))?$", antes, re.M)
        ctx = [l for l in antes.splitlines() if l.strip() and not l.startswith(("**Valor:**", "**Dono:**"))]
        contexto = "\n\n".join(ctx)
        t = tabela.get(tag, {})
        valor = {"A": "alto", "M": "médio", "B": "baixo"}.get(t.get("valor"), t.get("valor", ""))
        valor_txt = (f"Valor {valor_linha.group(1)}." if valor_linha else f"Valor {valor}.") if (valor_linha or valor) else ""
        if t.get("porque"):
            valor_txt += f" {t['porque']} (ordem de prioridade do Zico em `programacao/backlog.md`; quem decide é o Guilherme)."
        th = thiago.get(tag)
        if th:
            abord = (f"- **Abordagem:** {th[1]}\n- **Arquivos prováveis:** {th[2]}\n- **Risco:** {th[3]}\n"
                     f"- **Esforço:** {th[4]}  (P ≈ meio dia, M ≈ 1-2 dias, G ≈ 3+ dias; estimativa sem histórico de velocidade, **Thiago Silva**)\n"
                     f"- **Quem:** {th[5]}")
            deps = th[6]
        else:
            abord, deps = "Nota técnica: a refinar pelo **Thiago Silva**.", "nada registrado"
        if valor_linha and valor_linha.group(2):
            deps = f"{deps}. Backlog: {valor_linha.group(2)}"
        sprint = kp.sprint_do_item(tag)
        como = alisson.get(tag) or COMO_TESTAR_EXTRA.get(tag) or (
            "Plano de teste: a definir pelo **Alisson**." if tag not in thiago else "Sem plano de teste específico de **Alisson** no pré-planning; vale o critério de teste automatizado acima e as "
            "exigências gerais (relatório em `entregas/`, baterias verdes sem teste relaxado, zero token, nada commitado).")
        if tag in COMO_TESTAR_EXTRA and tag in alisson:
            como += "\n\n" + COMO_TESTAR_EXTRA[tag]
        desenho = ux003 if tag == "PROG-003" else DESENHO_EXTRA.get(tag, "Sem desenho: o item não tem proposta de UX no pré-planning.")
        if tag in ("PROG-001", "PROG-002"):
            status = (f"**{fino}.** Atendido por **Rodrygo** e **Endrick**; aguardando validação do Guilherme e de **Alisson**. "
                      "Falta o relatório do autor em `programacao/entregas/` (pendência apontada por **Alisson** e **Thiago Silva**).")
        elif fino in ("Fazendo", "Em teste", "Code Review", "Pronto para aceite", "Feito"):
            status = (f"Estado atual: **{fino}**. Relatórios de QA em `programacao/qa/` e revisão técnica em `programacao/revisoes/`; "
                      "a situação detalhada está em `programacao/quadro.md`.")
        else:
            status = f"Novo, no backlog (coluna do quadro: {fino}). " + (
                "Entra na Sprint 01 pela recomendação conjunta de Zico e Thiago Silva; a planning (16:50) confirma." if sprint != "Backlog"
                else "Fora da Sprint 01 recomendada por pelo menos um dos dois (ver `sprints/prep/zico.md` e `thiago-silva.md`); a planning decide.")
        dono, apoio = dono_e_apoio(tag, corpo)
        desc = f"""{linha_dono(dono, apoio)}

## Contexto
{contexto}

Cabeçalho do backlog: {cab.strip()}.

## Valor para o Guilherme
{valor_txt}

## Critérios de aceite
{len(criterios)} critérios, no checklist deste cartão (copiados de `programacao/backlog.md`).

## Abordagem técnica / risco / esforço (Thiago Silva)
{abord}

## Desenho / UX
{desenho}

## Como testar (Alisson)
{como}

## Dependências
{deps}

## Responsáveis
{RESP_TEXTO.get(tag, TEXTO_PADRAO)}

## Status atual
{status}

## Print
A anexar na validação (ainda não há captura fiel a este item).

_Fonte: `programacao/backlog.md`, `quadro.md`, `sprints/prep/*.md`. Quem move o item é o maestro da sprint (`programacao/maestro.py`), aplicando a decisão do agente dono da coluna; o cartão é mantido por `produtividade/trello_programacao.py`._
"""
        etiquetas = [sprint, "Programação", TIPO.get(tag, "Melhoria"), prio] + RESP.get(tag, RESP_PADRAO) + [f"Dono: {dono}"]
        plano.append({"tag": tag, "titulo": titulo, "lista": col, "etiquetas": etiquetas, "desc": desc, "criterios": criterios,
                      "estado": fino, "dono": dono, "apoio": apoio})
    return plano


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--atualizar", action="store_true")
    ap.add_argument("--dump", help="grava o plano em JSON (conferência)")
    a = ap.parse_args()
    sim = a.simular
    avisar.carregar_env()
    sys.stdout.reconfigure(encoding="utf-8")
    plano = montar_cartoes()
    if a.dump:
        Path(a.dump).write_text(json.dumps(plano, ensure_ascii=False, indent=1), encoding="utf-8")
    estado = avisar.ler_json(ts.ESTADO, {})
    board = estado["board"]
    listas = {l["name"]: l["id"] for l in ts.api("GET", f"boards/{board}/lists", filter="open", fields="name")}
    etiq = {l["name"].lower(): l for l in ts.api("GET", f"boards/{board}/labels", fields="name,color", limit=1000) if l["name"]}
    todos = ts.api("GET", f"boards/{board}/cards", filter="all", fields="name,idList,closed,idLabels,desc,url,shortUrl")
    por_id = {}
    for c in todos:
        i = kp.id_do_titulo(c["name"])
        if i:
            por_id.setdefault(i, c)
    for c in por_id:
        if c.startswith("PROG-C-"):
            print(f"AVISO: já existe cartão {c} no Trello; não mexo")
    precisa = sorted({e for p in plano for e in p["etiquetas"] if e.lower() not in etiq})
    for nome in precisa:
        print(f"criar etiqueta '{nome}' ({CORES[nome]})")
        if not sim:
            etiq[nome.lower()] = ts.api("POST", f"boards/{board}/labels", name=nome, color=CORES[nome])
    resumo, cartoes_estado = [], dict(estado.get("cartoes", {}))
    for p in plano:
        ids = [etiq[e.lower()]["id"] for e in p["etiquetas"] if e.lower() in etiq]
        c = por_id.get(p["tag"])
        if c is None:
            print(f"criar cartão {p['titulo']} em {p['lista']}  etiquetas={p['etiquetas']}")
            if sim:
                resumo.append((p, "(simulado)"))
                continue
            c = ts.api("POST", "cards", idList=listas[p["lista"]], name=p["titulo"], desc=p["desc"],
                       idLabels=",".join(ids), pos="bottom")
            ck = ts.api("POST", "checklists", idCard=c["id"], name="Critérios de aceite")
            for item in p["criterios"]:
                ts.api("POST", f"checklists/{ck['id']}/checkItems", name=item[:16000])
        else:
            falta = [i for i in ids if i not in c["idLabels"]]
            if a.atualizar and not sim:
                antigas_sprint = [etiq[n.lower()]["id"] for n in ("Sprint 01", "Backlog") if n.lower() in etiq]
                certa = [i for i in ids if i in antigas_sprint]
                sobra = [i for i in c["idLabels"] if i in antigas_sprint and i not in certa]
                novo_nome = c["name"]
                m = re.match(r"^\[(?:Sprint \d+|Backlog)\] ", novo_nome)
                if m and p["titulo"].split("] ")[0][1:] != novo_nome[1:m.end() - 2]:
                    novo_nome = p["titulo"].split("] ", 1)[0] + "] " + novo_nome[m.end():]
                if novo_nome != c["name"]:
                    ts.api("PUT", f"cards/{c['id']}", name=novo_nome)
                    print(f"renomeado {c['name']} -> {novo_nome}")
                    c["name"] = novo_nome
                for i in sobra:
                    ts.api("DELETE", f"cards/{c['id']}/idLabels/{i}")
            if "## Contexto" not in c.get("desc", ""):  # cartão criado pela ponte com descrição curta: completa as seções
                print(f"  {p['tag']}: descrição curta -> completa")
                c["desc"] = p["desc"]
                if not sim:
                    ts.api("PUT", f"cards/{c['id']}", desc=p["desc"])
                    if not ts.api("GET", f"cards/{c['id']}/checklists"):
                        ck = ts.api("POST", "checklists", idCard=c["id"], name="Critérios de aceite")
                        for item in p["criterios"]:
                            ts.api("POST", f"checklists/{ck['id']}/checkItems", name=item[:16000])
            nova_desc = com_linha_dono(c.get("desc", ""), linha_dono(p["dono"], p["apoio"]))
            if nova_desc != c.get("desc", "") and (a.atualizar or "**Dono:**" not in c.get("desc", "")):
                print(f"  descrição de {p['tag']}: linha de dono -> {linha_dono(p['dono'], p['apoio'])}")
                if not sim:
                    ts.api("PUT", f"cards/{c['id']}", desc=nova_desc)
            if falta and not sim:
                for i in falta:
                    ts.api("POST", f"cards/{c['id']}/idLabels", value=i)
            print(f"{p['tag']} já existe ({c['name']}): " + (f"{len(falta)} etiqueta(s) completada(s)" if falta else "ok"))
        if not sim:
            cartoes_estado[c["id"]] = {"titulo": c["name"], "coluna": p["lista"]}
        resumo.append((p, c.get("shortUrl") or c.get("url") or ""))
    if not sim:
        estado["cartoes"] = cartoes_estado
        ts.ESTADO.write_text(json.dumps(estado, indent=1), encoding="utf-8")
        # kanban.md e estado da ponte: o sincronizador não recria nem duplica
        cab, colunas, extras = ts.ler_kanban()
        ts_estado = kp.ESTADO_LER()
        for p, _ in resumo:
            nome = cartoes_estado and next((v["titulo"] for v in cartoes_estado.values() if kp.id_do_titulo(v["titulo"]) == p["tag"]), p["titulo"])
            achado = next(((cn, i) for cn, cs in colunas.items() for i, (t, _) in enumerate(cs) if kp.id_do_titulo(t) == p["tag"]), None)
            desc = f"projeto Canal dark (programação) · estado: {p['estado']} · cartão completo no Trello"
            if achado is None:
                colunas.setdefault(p["lista"], []).append((nome, desc))
            ts_estado[p["tag"]] = {"coluna": p["lista"], "estado": p["estado"]}
        ts.escrever_kanban(cab, colunas, extras)
        kp.salvar_estado(ts_estado)
    print("\nResumo (cartão -> lista -> etiquetas):")
    for p, url in resumo:
        print(f"- {p['titulo']} -> {p['lista']} -> {', '.join(p['etiquetas'])}  {url}")
    print("\nCartão -> dono -> lista:")
    for p, _ in resumo:
        print(f"- {p['tag']} -> {p['dono']} -> {p['lista']}")


if __name__ == "__main__":
    main()
