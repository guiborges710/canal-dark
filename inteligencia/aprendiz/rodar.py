"""Roda o Busquets (aprendiz) ou o Xabi Alonso (curador), com teto de gasto e registro. Nada aqui é agendado.

  python inteligencia/aprendiz/rodar.py aprendiz    estuda até 3 vídeos de _entrada/ (sem arquivo, não chama o Claude)
  python inteligencia/aprendiz/rodar.py curador     monta a lista de referências e alimenta a fila
  python inteligencia/aprendiz/rodar.py aprendiz --simular    mostra o que faria, sem preparar, chamar nem escrever

Decisões do Guilherme (2026-11-05): os vídeos vêm só de arquivos que ele sobe (nada de download automático)
e os agentes só rodam quando alguém chama. Ver inteligencia/aprendiz/README.md.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))
import preparar_video as pv  # noqa: E402

RAIZ = PASTA.parent.parent
ENTRADA = PASTA / "_entrada"
TRABALHO = PASTA / "_trabalho"
FILA = PASTA / "fila.md"
ESTUDADOS = PASTA / "estudados.md"
HISTORICO = PASTA / "historico.jsonl"
LISTAS = PASTA.parent / "referencias_estudo"

MAX_VIDEOS_RODADA = 3
TETOS = {"aprendiz": 0.30, "curador": 0.20}  # US$ por execução (valor equivalente informado pelo Claude Code)
TETO_DIA = 1.10
MINUTOS = 15
EXTENSOES = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
PROIBIDO = ["Read(./.env*)", "Edit(./.env*)", "Write(./.env*)", "Read(./**/*token*.json)", "Read(./client_secret*)",
            "Edit(./.claude/**)", "Write(./.claude/**)", "Edit(./output/**)", "Write(./output/**)",
            "Edit(./CLAUDE.md)", "Write(./CLAUDE.md)"]
AGENTES = {
    "aprendiz": ("busquets-aprendiz-canais-dark", "Read,Write,Glob,Grep"),
    "curador": ("xabi-alonso-curador-referencias", "Read,Write,Glob,Grep,WebSearch,WebFetch"),
}


def rel(caminho):
    return Path(caminho).resolve().relative_to(Path(RAIZ).resolve()).as_posix()


def id_seguro(nome):
    return re.sub(r"[^\w-]+", "-", nome, flags=re.UNICODE).strip("-")[:80] or "video"


def ler_tabela(arquivo):
    """Linhas de dados de uma tabela markdown, como listas de células sem espaços."""
    if not arquivo.exists():
        return []
    linhas = []
    for l in arquivo.read_text(encoding="utf-8").splitlines():
        if l.lstrip().startswith("|") and not re.match(r"^\s*\|[\s:|-]+\|\s*$", l):
            linhas.append([c.strip() for c in l.strip().strip("|").split("|")])
    return linhas[1:]  # a primeira linha é o cabeçalho


def ler_fila():
    colunas = ["ordem", "id", "link", "canal", "nicho", "aprender", "fonte"]
    return [dict(zip(colunas, c)) for c in ler_tabela(FILA) if len(c) >= 2 and c[1]]


def ids_estudados():
    return {c[0] for c in ler_tabela(ESTUDADOS) if c}


def arquivos_entrada():
    """{id: arquivo} dos vídeos em _entrada/. O id é o nome do arquivo sem a extensão."""
    if not ENTRADA.is_dir():
        return {}
    return {id_seguro(a.stem): a for a in sorted(ENTRADA.iterdir()) if a.is_file() and a.suffix.lower() in EXTENSOES}


def montar_rodada():
    """(a estudar, aguardando arquivo). Vídeo com arquivo vem primeiro; arquivo fora da fila também é estudado."""
    estudados = ids_estudados()
    arquivos = arquivos_entrada()
    fila = [i for i in ler_fila() if i["id"] not in estudados]
    na_fila = {i["id"] for i in fila}
    com_arquivo = [{**i, "arquivo": arquivos[i["id"]]} for i in fila if i["id"] in arquivos]
    avulsos = [{"id": k, "link": "não informado", "canal": "não informado", "nicho": "não informado", "arquivo": a}
               for k, a in arquivos.items() if k not in na_fila and k not in estudados]
    aguardando = [i for i in fila if i["id"] not in arquivos][:MAX_VIDEOS_RODADA]
    return (com_arquivo + avulsos)[:MAX_VIDEOS_RODADA], aguardando


def proximo_relatorio(hoje):
    pasta = PASTA / hoje.isoformat()
    numeros = [int(m.group(1)) for a in pasta.glob("rodada-*.md") if (m := re.match(r"rodada-(\d+)$", a.stem))] if pasta.is_dir() else []
    n = max(numeros, default=0) + 1
    return n, pasta / f"rodada-{n}.md"


def gasto_hoje(hoje):
    if not HISTORICO.exists():
        return 0.0
    total = 0.0
    for l in HISTORICO.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(l)
        except ValueError:
            continue
        if str(r.get("quando", "")).startswith(hoje.isoformat()):
            total += float(r.get("custo_usd") or 0)
    return total


def registrar(agente, resultado, custo, detalhe):
    reg = {"quando": f"{datetime.now():%Y-%m-%dT%H:%M:%S}", "agente": agente, "resultado": resultado,
           "custo_usd": round(custo, 4), "detalhe": detalhe[:300]}
    with HISTORICO.open("a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")


def chamar_claude(chave, pedido, teto):
    """Devolve (custo, texto, erro?). Nenhuma chave do .env chega ao agente."""
    agente, ferramentas = AGENTES[chave]
    env = dict(os.environ)
    arq_env = RAIZ / ".env"
    if arq_env.exists():
        for linha in arq_env.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.lstrip().startswith("#"):
                env.pop(linha.split("=", 1)[0].strip(), None)
    env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] = "1"  # as regras que valem estão na definição do agente
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    cmd = [shutil.which("claude") or "claude", "-p", "--agent", agente, "--model", "sonnet", "--effort", "medium",
           "--permission-mode", "acceptEdits", "--tools", ferramentas, "--allowedTools", ferramentas,
           "--disallowedTools", ",".join(PROIBIDO), "--disable-slash-commands", "--strict-mcp-config",
           "--no-session-persistence", "--max-budget-usd", f"{teto:.2f}", "--output-format", "json"]
    try:
        r = subprocess.run(cmd, input=pedido, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           cwd=RAIZ, env=env, timeout=MINUTOS * 60)
    except subprocess.TimeoutExpired:
        return 0.0, f"passou de {MINUTOS} minutos e foi interrompido", True
    except OSError as e:
        return 0.0, f"não consegui iniciar o Claude: {e}", True
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return 0.0, f"o Claude saiu com código {r.returncode}: {(r.stderr or r.stdout)[:200]}", True
    custo = float(d.get("total_cost_usd") or 0)
    if d.get("subtype") == "error_max_budget_usd":
        return custo, f"parou ao atingir o teto de US$ {teto:.2f} desta execução", True
    return custo, (d.get("result") or "").strip(), bool(d.get("is_error")) or r.returncode != 0


def linha_aguardando(i):
    return (f"- {i['id']} ({i.get('link') or 'sem link'}): não assistido. Para eu estudar, salve o vídeo como "
            f"`{rel(ENTRADA)}/{i['id']}.mp4`. Só o arquivo: nada de senha, cookie ou login.")


def relatorio_sem_claude(destino, n, hoje, titulo, itens, falhas=()):
    destino.parent.mkdir(parents=True, exist_ok=True)
    corpo = [f"# Rodada {n} · {hoje.isoformat()}", "", titulo, ""]
    if falhas:
        corpo += ["## Falhas na preparação", *[f"- {i['id']} ({i.get('link') or 'sem link'}): não assistido. {erro}." for i, erro in falhas], ""]
    if itens:
        corpo += ["## Não assistidos", *[linha_aguardando(i) for i in itens], ""]
    destino.write_text("\n".join(corpo), encoding="utf-8")


def marcar_estudados(videos, relatorio, n, hoje):
    """Só marca o vídeo que o relatório realmente traz; os outros voltam na próxima rodada."""
    texto = relatorio.read_text(encoding="utf-8") if relatorio.exists() else ""
    if not ESTUDADOS.exists():
        ESTUDADOS.write_text("# Vídeos já estudados pelo Busquets\n\nMantido por `rodar.py`.\n\n| id | data | relatório | nível de acesso |\n|---|---|---|---|\n", encoding="utf-8")
    marcados = []
    with ESTUDADOS.open("a", encoding="utf-8") as f:
        for v in videos:
            if re.search(rf"^## Vídeo:.*{re.escape(v['id'])}", texto, re.M):
                f.write(f"| {v['id']} | {hoje.isoformat()} | {hoje.isoformat()}/rodada-{n}.md | {v['manifesto']['nivel_acesso']} |\n")
                marcados.append(v["id"])
    return marcados


def rodar_aprendiz(simular=False, hoje=None, chamar=chamar_claude):
    hoje = hoje or date.today()
    videos, aguardando = montar_rodada()
    n, relatorio = proximo_relatorio(hoje)
    if simular:
        print(f"Estudaria: {[v['id'] for v in videos] or 'nada'}. Aguardando arquivo: {[i['id'] for i in aguardando] or 'nada'}.")
        return 0
    gasto = gasto_hoje(hoje)
    if videos and gasto >= TETO_DIA:
        print(f"Parei antes de começar: o gasto de hoje (US$ {gasto:.2f}) já atingiu o teto do dia (US$ {TETO_DIA:.2f}).")
        registrar("aprendiz", "teto do dia", 0, f"gasto de hoje US$ {gasto:.2f}")
        return 0

    prontos, falhas = [], []
    for v in videos:
        print(f"Preparando {v['id']} (quadros e fala; pode levar alguns minutos)...", flush=True)
        try:
            prontos.append({**v, "manifesto": pv.preparar(v["arquivo"], TRABALHO / v["id"])})
        except pv.ErroPreparo as e:
            falhas.append((v, str(e)))
        except Exception as e:  # noqa: BLE001  # um vídeo ruim não derruba o resto da rodada
            falhas.append((v, f"erro inesperado: {str(e)[:150]}"))

    if not prontos:
        titulo = "Nenhum vídeo estudado: não há arquivo utilizável em `_entrada/`. O Claude não foi chamado (custo zero)."
        if not aguardando and not falhas:
            titulo = "Nada a estudar: a fila está vazia e não há arquivo em `_entrada/`. O Claude não foi chamado (custo zero)."
        relatorio_sem_claude(relatorio, n, hoje, titulo, aguardando, falhas)
        registrar("aprendiz", "sem vídeo", 0, f"aguardando {len(aguardando)}, falhas {len(falhas)}")
        print(f"Relatório: {rel(relatorio)}\n{titulo}")
        for i in aguardando:
            print(linha_aguardando(i))
        return 0

    pedido = [f"Rodada {n} de {hoje.isoformat()}. Grave o relatório em `{rel(relatorio)}`.", "", "Vídeos para estudar:"]
    pedido += [f"- id `{v['id']}`, link {v.get('link')}, canal {v.get('canal')}, nicho {v.get('nicho')}: pasta `{rel(TRABALHO / v['id'])}`" for v in prontos]
    if aguardando or falhas:
        pedido += ["", "Para a seção `## Não assistidos`, copie:"]
        pedido += [linha_aguardando(i) for i in aguardando]
        pedido += [f"- {i['id']} ({i.get('link') or 'sem link'}): não assistido. {erro}." for i, erro in falhas]
    relatorio.parent.mkdir(parents=True, exist_ok=True)
    print(f"Chamando o Busquets (teto de US$ {TETOS['aprendiz']:.2f})...", flush=True)
    custo, texto, erro = chamar("aprendiz", "\n".join(pedido), TETOS["aprendiz"])
    if erro and not relatorio.exists():
        relatorio_sem_claude(relatorio, n, hoje, f"A rodada falhou e nada foi estudado: {texto}.", aguardando, falhas)
    elif not relatorio.exists():
        erro, texto = True, "o Busquets terminou sem gravar o relatório"
        relatorio_sem_claude(relatorio, n, hoje, f"A rodada falhou: {texto}.", aguardando, falhas)
    marcados = marcar_estudados(prontos, relatorio, n, hoje)
    registrar("aprendiz", "falha" if erro else "ok", custo, f"estudados {marcados}; {texto}")
    print(f"Relatório: {rel(relatorio)}\nEstudados: {marcados or 'nenhum'}. Custo: US$ {custo:.2f}.\n{texto}")
    return 1 if erro else 0


def rodar_curador(simular=False, hoje=None, chamar=chamar_claude):
    hoje = hoje or date.today()
    n = 1
    lista = LISTAS / f"{hoje.isoformat()}.md"
    while lista.exists():
        n += 1
        lista = LISTAS / f"{hoje.isoformat()}-{n}.md"
    if simular:
        print(f"Gravaria {rel(lista)} e alimentaria {rel(FILA)}.")
        return 0
    gasto = gasto_hoje(hoje)
    if gasto >= TETO_DIA:
        print(f"Parei antes de começar: o gasto de hoje (US$ {gasto:.2f}) já atingiu o teto do dia (US$ {TETO_DIA:.2f}).")
        registrar("curador", "teto do dia", 0, f"gasto de hoje US$ {gasto:.2f}")
        return 0
    LISTAS.mkdir(parents=True, exist_ok=True)
    pedido = f"Entrega de {hoje.isoformat()}. Grave a lista em `{rel(lista)}` e atualize `{rel(FILA)}`."
    print(f"Chamando o Xabi Alonso (teto de US$ {TETOS['curador']:.2f})...", flush=True)
    custo, texto, erro = chamar("curador", pedido, TETOS["curador"])
    if not lista.exists():
        erro = True
        lista.write_text(f"# Referências · {hoje.isoformat()}\n\nSem lista nesta execução: {texto or 'o agente terminou sem gravar'}.\n", encoding="utf-8")
    registrar("curador", "falha" if erro else "ok", custo, texto)
    print(f"Lista: {rel(lista)}. Custo: US$ {custo:.2f}.\n{texto}")
    return 1 if erro else 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Roda o aprendiz ou o curador, com teto de gasto.")
    ap.add_argument("quem", choices=sorted(AGENTES))
    ap.add_argument("--simular", action="store_true", help="mostra o que faria, sem preparar, chamar nem escrever")
    a = ap.parse_args()
    return (rodar_aprendiz if a.quem == "aprendiz" else rodar_curador)(simular=a.simular)


if __name__ == "__main__":
    sys.exit(main())
