"""PROG-024a: confere estudio/dados/gerar_financas.py com FIXTURE INVENTADA em pasta temporaria.
Nunca le financas/ real. Uso: .venv\\Scripts\\python estudio\\testes\\testar_financas.py"""
import json
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "estudio" / "dados"))
import gerar_financas as G  # noqa: E402

passou, falhas = 0, []


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}")
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""))


HOJE = date(2026, 3, 15)
MOV = """data,tipo,categoria,descricao,valor,status
2026-03-01,recebido,salario,Salario ficticio,3000.00,pago
2026-03-20,recebido,extra,Freela ficticio,500.00,a receber
2026-03-02,gasto,moradia,Aluguel ficticio,1000.00,pago
2026-03-03,gasto,mercado,Mercado ficticio,250.50,pago
2026-03-10,gasto,contas,Luz ficticia (pago em 12/03),100.00,a pagar
2026-03-25,gasto,contas,Internet ficticia,80.00,a pagar
2026-03-15,gasto,lazer,Cinema estimado,40.00,a pagar
2026-02-05,gasto,moradia,Aluguel ficticio,1000.00,pago
2025-12-05,gasto,mercado,Mercado ficticio,10.00,pago
linha,quebrada
2026-03-04,gasto,mercado,Valor ruim,abc,pago
"""
SAL = """conta,data,saldo,observacao
Banco A,2026-03-01,10.00,antigo
Banco A,2026-03-14,500.00,Informado pelo dono (extrato: 520.00)
Banco B,2026-03-14,99.00,Saldo bancario real: NÃO CONFIRMADO
"""
PEND = "# P\n1. [ ] Qual o banco?\n2. [x] Resolvida\n"


def montar(mov=MOV, sal=SAL, pend=PEND):
    d = Path(tempfile.mkdtemp(prefix="financas_"))
    (d / "movimentos.csv").write_text(mov, encoding="utf-8")
    (d / "saldos.csv").write_text(sal, encoding="utf-8")
    if pend is not None:
        (d / "pendencias.md").write_text(pend, encoding="utf-8")
    return d


def tipos(r):
    return [a["tipo"] for a in r["alertas"]]


print("valores")
d = montar()
r = G.gerar(d, hoje=HOJE, agora=datetime(2026, 3, 15, 9, 0))
confere(r["gerado_em"] == "2026-03-15T09:00:00", "gerado_em")
confere(r["recebido"]["mes"] == 300000 and r["recebido"]["previsto_mes"] == 50000, "recebido e previsto separados", r["recebido"])
confere(r["gastos"]["pagos_mes"] == 125050, "gastos pagos do mes", r["gastos"])
confere(r["gastos"]["a_pagar_mes"] == 22000, "gastos a pagar do mes", r["gastos"])
confere(r["gastos"]["pagos_6m"] == 125050 + 100000 + 1000, "gastos pagos 6m (fev + dez + mar)", r["gastos"])
confere([s["mes"] for s in r["serie_mensal"]] == ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"], "serie 6 meses")
confere(r["receitas_x_gastos"] == {"mes": "2026-03", "receitas": 300000, "gastos": 125050}, "receitas x gastos")
confere(all(isinstance(c["valor"], int) for c in r["categorias"]), "centavos inteiros")
confere(r["fonte"]["contagens"] == {"movimentos": 9, "contas": 2, "vencimentos": 3}, "contagens", r["fonte"]["contagens"])
confere(set(r["fonte"]["arquivos"]) >= {"movimentos.csv", "saldos.csv"}, "fonte com datas de modificacao")

print("saldos")
a = next(c for c in r["saldos"]["contas"] if c["conta"] == "Banco A")
b = next(c for c in r["saldos"]["contas"] if c["conta"] == "Banco B")
confere(a["saldo"] == 50000 and a["data"] == "2026-03-14", "ultimo saldo por conta/data", a)
confere(b["nao_confirmado"] and not a["nao_confirmado"], "marca NAO CONFIRMADO")
confere(r["saldos"]["disponivel"] == 50000 and r["saldos"]["contas_fora_do_disponivel"] == ["Banco B"], "disponivel exclui nao confirmada")
confere("saldo_divergente" in tipos(r), "saldo divergente do extrato", tipos(r))
confere("saldo_nao_confirmado" in tipos(r), "alerta conta nao confirmada")

print("vencimentos e alertas")
v = r["vencimentos"]
confere([x["data"] for x in v] == ["2026-03-10", "2026-03-15", "2026-03-25"], "ordenado por data")
confere(v[0]["atrasado"] and v[0]["dias_restantes"] == -5 and v[0]["status"] == "vencido", "vencimento atrasado", v[0])
confere(v[1]["status"] == "vence hoje" and v[2]["dias_restantes"] == 10 and v[2]["status"] == "a pagar", "hoje e futuro")
confere("pago_sem_lancamento" in tipos(r), "pago sem lancamento sinalizado")
confere("valor_estimado" in tipos(r), "valor estimado sinalizado")
confere("pendencia_aberta" in tipos(r) and r["pendencias"]["resolvidas"] == 1, "pendencia aberta")
confere(tipos(r).count("linha_invalida") == 2, "linha mal formada e valor ruim viram alerta", tipos(r))
confere(all("origem" in a for a in r["alertas"]), "todo alerta tem origem")
confere(any(m["status"] == "a pagar" for m in r["movimentos_recentes"]) and len(r["movimentos_recentes"]) <= 20, "recentes")
confere(next(m for m in v if "Luz" in m["descricao"])["status"] != "pago", "nunca marca como pago")

print("categorias")
cats = {c["categoria"]: c for c in r["categorias"]}
confere(cats["moradia"]["valor"] == 100000 and cats["moradia"]["percentual"] == 68.0, "percentual calculado", cats["moradia"])
confere(abs(sum(c["percentual"] for c in r["categorias"]) - 100) < 0.5, "percentuais somam ~100")
vz = G.gerar(montar("data,tipo,categoria,descricao,valor,status\n", SAL), hoje=HOJE)
confere(vz["categorias"] == [] and vz["gastos"]["pagos_mes"] == 0 and vz["vencimentos"] == [], "categorias vazias sem erro")

print("erros")
for nome in ("movimentos.csv", "saldos.csv"):
    d2 = montar()
    (d2 / nome).unlink()
    try:
        G.gerar(d2, hoje=HOJE)
        confere(False, f"{nome} ausente deveria falhar")
    except G.ErroFinancas as e:
        confere(nome in str(e) and "nao encontrado" in str(e), f"{nome} ausente: erro claro", str(e))
try:
    G.gerar(montar("a,b\n1,2\n"), hoje=HOJE)
    confere(False, "cabecalho errado deveria falhar")
except G.ErroFinancas as e:
    confere("Cabecalho" in str(e), "cabecalho errado: erro claro")
confere(G.gerar(montar(pend=None), hoje=HOJE)["pendencias"]["arquivo_ausente"], "pendencias.md ausente tolerado")

print("gravacao e CLI")
d = montar()
mov_antes = (d / "movimentos.csv").read_bytes()
saida = Path(tempfile.mkdtemp(prefix="financas_out_"))
rc = G.main(["--entrada", str(d), "--saida", str(saida / "dados")])
js = (saida / "dados" / "financas.js").read_text(encoding="utf-8")
confere(rc == 0 and js.startswith("window.FINANCAS = ") and js.rstrip().endswith(";"), "financas.js")
confere(json.loads((saida / "dados" / "financas.json").read_text(encoding="utf-8"))["unidade"] == "centavos", "financas.json valido")
confere((d / "movimentos.csv").read_bytes() == mov_antes, "CSV intacto")
(d / "movimentos.csv").unlink()
confere(G.main(["--entrada", str(d), "--saida", str(saida / "x")]) == 1 and not (saida / "x").exists(), "CLI falha com codigo 1 sem gravar")

print("regerar muda")
d = montar()
a1 = G.gerar(d, hoje=HOJE)["gastos"]["pagos_mes"]
(d / "movimentos.csv").write_text(MOV + "2026-03-05,gasto,lazer,Novo,10.00,pago\n", encoding="utf-8")
confere(G.gerar(d, hoje=HOJE)["gastos"]["pagos_mes"] == a1 + 1000, "alterar fixture e regerar muda")

print("meses (seletor de mes)")
r = G.gerar(montar(), hoje=HOJE)
M = r["meses"]
confere(r["meses_disponiveis"] == ["2025-12", "2026-01", "2026-02", "2026-03"], "faixa continua ate o mes atual", r["meses_disponiveis"])
confere(list(M) == r["meses_disponiveis"], "meses e meses_disponiveis alinhados")
cur = M["2026-03"]
confere(cur["recebido"] == r["recebido"]["mes"] and cur["previsto"] == r["recebido"]["previsto_mes"], "mes corrente bate: recebido/previsto")
confere(cur["gasto_pago"] == r["gastos"]["pagos_mes"] and cur["gasto_a_pagar"] == r["gastos"]["a_pagar_mes"], "mes corrente bate: gastos")
confere(cur["categorias"] == r["categorias"], "mes corrente bate: categorias")
confere(cur["vencimentos"] == [x for x in r["vencimentos"] if x["data"].startswith("2026-03")], "mes corrente bate: vencimentos")
confere(cur["saldo_do_mes"] == 300000 - 125050 and "nao e saldo bancario" in cur["saldo_do_mes_rotulo"], "saldo_do_mes rotulado", cur["saldo_do_mes"])
confere([m["data"] for m in cur["movimentos"]] == sorted(m["data"] for m in cur["movimentos"]) and len(cur["movimentos"]) == 7, "movimentos do mes por data")
confere(all(isinstance(m["valor"], int) for x in M.values() for m in x["movimentos"]), "centavos inteiros nos movimentos")
confere(M["2026-02"]["gasto_pago"] == 100000 and M["2026-02"]["recebido"] == 0, "mes passado so com gasto")
confere(M["2026-01"]["movimentos"] == [] and M["2026-01"]["categorias"] == [] and M["2026-01"]["saldo_do_mes"] == 0, "mes sem lancamentos")
confere(next(m for m in cur["movimentos"] if "Luz" in m["descricao"])["status"] == "a pagar", "nao marca pago")

# mes so com recebimento (mes passado), mes corrente vazio
rc = G.gerar(montar("data,tipo,categoria,descricao,valor,status\n2026-02-05,recebido,salario,Salario ficticio,2000.00,pago\n2026-02-20,recebido,extra,Bico ficticio,300.00,a receber\n"), hoje=HOJE)
confere(rc["meses_disponiveis"] == ["2026-02", "2026-03"], "mes corrente vazio entra na lista", rc["meses_disponiveis"])
confere(rc["meses"]["2026-02"]["recebido"] == 200000 and rc["meses"]["2026-02"]["previsto"] == 30000 and rc["meses"]["2026-02"]["saldo_do_mes"] == 200000, "mes so com recebimento")
confere(rc["meses"]["2026-02"]["categorias"] == [] and len(rc["meses"]["2026-02"]["movimentos"]) == 2, "mes so com recebimento: sem categorias de gasto")
confere(rc["meses"]["2026-03"]["movimentos"] == [] and rc["meses"]["2026-03"]["recebido"] == 0, "mes corrente vazio")
# sem nenhum lancamento
rv = G.gerar(montar("data,tipo,categoria,descricao,valor,status\n"), hoje=HOJE)
confere(rv["meses_disponiveis"] == ["2026-03"] and rv["meses"]["2026-03"]["movimentos"] == [], "sem lancamentos: so o mes atual")
# virada de ano
ra = G.gerar(montar("data,tipo,categoria,descricao,valor,status\n2025-11-30,gasto,mercado,Mercado ficticio,10.00,pago\n2026-01-01,recebido,salario,Salario ficticio,50.00,pago\n"), hoje=date(2026, 1, 10))
confere(ra["meses_disponiveis"] == ["2025-11", "2025-12", "2026-01"], "virada de ano", ra["meses_disponiveis"])
confere(ra["meses"]["2025-12"]["movimentos"] == [] and ra["meses"]["2026-01"]["recebido"] == 5000, "virada de ano: valores")
# muitos meses (mais que 6)
linhas = "".join(f"{2024 + (i // 12)}-{i % 12 + 1:02d}-10,gasto,contas,Conta ficticia,{i + 1}.00,pago\n" for i in range(30))
rm = G.gerar(montar("data,tipo,categoria,descricao,valor,status\n" + linhas), hoje=date(2026, 6, 15))
confere(len(rm["meses_disponiveis"]) == 30 and len(rm["serie_mensal"]) == 6, "muitos meses: todos em meses, serie segue 6", len(rm["meses_disponiveis"]))
confere(rm["meses"]["2024-01"]["gasto_pago"] == 100 and rm["meses"]["2026-06"]["gasto_pago"] == 3000, "muitos meses: valores")
confere(rm["meses_disponiveis"] == sorted(rm["meses_disponiveis"]), "meses_disponiveis ordenada")

print(f"\n{passou} ok, {len(falhas)} falhas")
sys.exit(1 if falhas else 0)
