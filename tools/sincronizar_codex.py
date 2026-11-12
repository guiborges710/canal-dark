"""Espelha os agentes e as skills do Claude para o Codex (reserva quando o Claude esgota).

Fonte de verdade: .claude/agents/<id>.md e .claude/skills/<nome>/. Este script só ESCREVE:
  .codex/agents/<id>.toml            (name, description, model_reasoning_effort, developer_instructions)
  .agents/skills/<nome>/...          (as skills citadas por algum agente no cabeçalho `skills:`)
Não apaga nada, não chama o Codex nem a rede.

Uso:
  python tools/sincronizar_codex.py              grava o que estiver defasado
  python tools/sincronizar_codex.py --verificar  só diz se está defasado (saída 1 se estiver), sem escrever
"""
import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTES = RAIZ / ".claude" / "agents"
SKILLS = RAIZ / ".claude" / "skills"
DESTINO_AGENTES = RAIZ / ".codex" / "agents"
DESTINO_SKILLS = RAIZ / ".agents" / "skills"

# Ferramentas e modelo do Claude (tools:, model:) não têm equivalente direto no Codex (o sandbox define o que ele pode e o modelo vem da conta): omitidos.
# `effort:` vira model_reasoning_effort.
ESFORCO = {"low": "low", "medium": "medium", "high": "high", "xhigh": "high", "max": "high"}

AVISO = ("Você está rodando no Codex, como RESERVA do Claude Code. Onde o texto abaixo citar ferramentas do Claude (Read, Write, Edit, Glob, Grep, Bash, WebSearch) "
         "ou a ferramenta Agent (subagentes), use o equivalente do Codex e faça você mesmo o trabalho do subagente. As regras do projeto estão em CLAUDE.md.\n\n")


def lf(texto):
    return texto.replace("\r\n", "\n").replace("\r", "\n")


def ler_agente(arq):
    texto = lf(arq.read_text(encoding="utf-8-sig"))
    m = re.match(r"---\n(.*?)\n---\n?(.*)$", texto, re.S)
    if not m:
        raise ValueError(f"{arq.name}: sem cabeçalho ---")
    meta = {}
    for linha in m.group(1).split("\n"):
        if ":" in linha and not linha.startswith((" ", "\t")):
            k, v = linha.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, m.group(2).strip()


def _basica(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\t", "\\t")
    return '"' + re.sub(r"[\x00-\x1f\x7f]", lambda c: "\\u%04x" % ord(c.group()), s) + '"'


def toml_do_agente(arq):
    meta, corpo = ler_agente(arq)
    nome = meta.get("name") or arq.stem
    corpo = AVISO + corpo
    linhas = [f"# GERADO por tools/sincronizar_codex.py a partir de .claude/agents/{arq.name}. Não edite aqui: edite o .md e rode o script.",
              f"name = {_basica(nome)}", f"description = {_basica(meta.get('description', ''))}"]
    if meta.get("effort") in ESFORCO:
        linhas.append(f"model_reasoning_effort = {_basica(ESFORCO[meta['effort']])}")
    if "'''" not in corpo and not any(ord(c) < 32 and c not in "\n\t" for c in corpo):
        linhas.append("developer_instructions = '''\n" + corpo + "\n'''")  # literal: sem escapes, o texto fica igual ao .md
    else:
        seguro = corpo.replace("\\", "\\\\").replace('"""', '""\\"')
        linhas.append('developer_instructions = """\n' + seguro + '\n"""')
    return "\n".join(linhas) + "\n"


def skills_usadas():
    usadas = set()
    for arq in AGENTES.glob("*.md"):
        meta, _ = ler_agente(arq)
        usadas.update(s.strip() for s in meta.get("skills", "").split(",") if s.strip())
    return sorted(usadas)


def _texto_ou_bytes(arq):
    dados = arq.read_bytes()
    try:
        return lf(dados.decode("utf-8-sig")).encode("utf-8")
    except UnicodeDecodeError:
        return dados


def planejar():
    """Lista (caminho, conteúdo em bytes) de tudo o que deveria existir."""
    plano = []
    for arq in sorted(AGENTES.glob("*.md")):
        plano.append((DESTINO_AGENTES / f"{arq.stem}.toml", toml_do_agente(arq).encode("utf-8")))
    for nome in skills_usadas():
        origem = SKILLS / nome
        if not origem.is_dir():
            print(f"AVISO: skill '{nome}' citada por um agente mas não existe em {origem}", file=sys.stderr)
            continue
        for f in sorted(p for p in origem.rglob("*") if p.is_file()):
            plano.append((DESTINO_SKILLS / nome / f.relative_to(origem), _texto_ou_bytes(f)))
    return plano


def sincronizar(verificar=False):
    """Devolve (defasados, atualizados, orfaos). Com verificar=False, grava os defasados."""
    defasados, atualizados = [], []
    for destino, conteudo in planejar():
        atual = destino.read_bytes() if destino.exists() else None
        if atual == conteudo:
            atualizados.append(destino)
            continue
        defasados.append(destino)
        if not verificar:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(conteudo)  # bytes: LF garantido, sem conversão do Windows
    esperados = {d.name for d, _ in planejar() if d.parent == DESTINO_AGENTES}
    orfaos = sorted(p.name for p in DESTINO_AGENTES.glob("*.toml") if p.name not in esperados) if DESTINO_AGENTES.is_dir() else []
    return defasados, atualizados, orfaos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verificar", action="store_true", help="só confere se está defasado (sem escrever); saída 1 se estiver")
    args = ap.parse_args(argv)
    defasados, atualizados, orfaos = sincronizar(args.verificar)
    verbo = "DEFASADO" if args.verificar else "gravado"
    for d in defasados:
        print(f"{verbo}: {d.relative_to(RAIZ)}")
    print(f"{len(atualizados)} em dia, {len(defasados)} {'defasados' if args.verificar else 'gravados'}.")
    if orfaos:
        print("Sem agente correspondente em .claude/agents (não mexi): " + ", ".join(orfaos))
    if args.verificar and defasados:
        print("Rode: python tools/sincronizar_codex.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
