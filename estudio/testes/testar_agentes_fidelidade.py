"""Salvar agente sem mudar nada devolve o arquivo byte a byte (todos os agentes reais, copiados para pasta temporária).
Cobre: linha em branco após o frontmatter, ordem das chaves, LF/CRLF. Uso: .venv\Scripts\python estudio\testes\testar_agentes_fidelidade.py"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="agfid_"))
os.environ["ESTUDIO_RAIZ"] = str(TMP / "raiz")
os.environ["ESTUDIO_DADOS"] = str(TMP / "dados")
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import agentes as A  # noqa: E402

(TMP / "dados").mkdir()
A.ATIVOS = TMP / "raiz" / ".claude" / "agents"
A.DESATIVADOS = TMP / "raiz" / ".claude" / "agents_desativados"
A.RAIZ = TMP / "raiz"
shutil.copytree(REPO / ".claude" / "agents", A.ATIVOS)
falhas, n = [], 0


def confere(cond, nome, extra=""):
    global n
    n += 1
    if not cond:
        falhas.append(nome)
        print(f"  FALHOU {nome} {extra}", flush=True)


def corpo_do(ident, v, **mud):
    c = v["contrato"]
    d = {"id": ident, "descricao": v["descricao"], "ferramentas": v["ferramentas"], "modelo": v["modelo"], "instrucoes": v["instrucoes"], "contrato": {"entradas": c["entradas"], "saidas": c["saidas"]}}
    d.update(mud)
    return d


reais = sorted(A.ATIVOS.glob("*.md"))
confere(len(reais) > 10, "agentes reais copiados")
for arq in reais:
    ident = arq.stem
    antes = arq.read_bytes()
    A.salvar(ident, corpo_do(ident, A._visao(ident, arq, True)), None)
    confere(arq.read_bytes() == antes, f"byte a byte (sem alterar): {ident}")
    # só a descrição muda: ordem das chaves e o resto ficam como estavam
    v = A._visao(ident, arq, True)
    A.salvar(ident, corpo_do(ident, v, descricao=v["descricao"] + " extra"), None)
    depois = arq.read_bytes()
    confere(depois.count(b"\r\n") == antes.count(b"\r\n"), f"quebra de linha preservada: {ident}")
    ca, _ = A.analisar(antes.decode("utf-8-sig"))
    cd, _ = A.analisar(depois.decode("utf-8-sig"))
    confere(list(ca) == list(cd), f"ordem das chaves: {ident}", (list(ca), list(cd)))
    confere(cd["description"].endswith(" extra") and {k: x for k, x in ca.items() if k != "description"} == {k: x for k, x in cd.items() if k != "description"}, f"só a descrição mudou: {ident}")

# CRLF continua CRLF, com e sem linha em branco após o frontmatter
for rotulo, bruto in (("crlf com linha em branco", "---\nname: x-teste\ndescription: descricao longa\nmodel: opus\ntools: Read, Write\n---\n\nCorpo\nsegunda\n"), ("crlf sem linha em branco", "---\nname: x-teste\ndescription: descricao longa\ntools: Read\nmodel: sonnet\n---\nCorpo\n")):
    arq = A.ATIVOS / "x-teste.md"
    arq.write_bytes(bruto.replace("\n", "\r\n").encode())
    antes = arq.read_bytes()
    A.salvar("x-teste", corpo_do("x-teste", A._visao("x-teste", arq, True)), None)
    confere(arq.read_bytes() == antes, f"byte a byte: {rotulo}")
    v = A._visao("x-teste", arq, True)
    A.salvar("x-teste", corpo_do("x-teste", v, modelo="haiku"), None)
    novo = arq.read_bytes()
    confere(b"\n" not in novo.replace(b"\r\n", b"") and b"model: haiku\r\n" in novo and novo.index(b"tools") != novo.index(b"model") , f"{rotulo}: muda só o valor e mantém CRLF")
    confere(novo.index(b"model") < novo.index(b"tools") if b"model: haiku" in novo and bruto.index("model") < bruto.index("tools") else novo.index(b"tools") < novo.index(b"model"), f"{rotulo}: ordem mantida")
    arq.unlink()

print(f"{n - len(falhas)}/{n} verificações ok")
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(1 if falhas else 0)
