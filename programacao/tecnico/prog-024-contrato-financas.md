# PROG-024a: contrato de `financas.js` / `financas.json`

Gerador: `python estudio/dados/gerar_financas.py` (opções `--entrada`, `--saida`). Local, sem rede, sem token; só lê `financas/*.csv` e `pendencias.md`, nunca escreve neles.
Saída: `ecossistema/app/dados/financas.js` (`window.FINANCAS = {...};`) e `financas.json`. A pasta está no `.gitignore` e nunca vai ao git.
Testes: `python estudio/testes/testar_financas.py` (fixture inventada). Exit code 1 e mensagem em stderr se faltar `movimentos.csv`/`saldos.csv` ou o cabeçalho estiver errado; nesse caso nada é gravado (a tela deve mostrar o estado de erro e manter a última leitura).

Regras: dinheiro em **centavos inteiros** (formatar só na tela); datas ISO `AAAA-MM-DD`; meses `AAAA-MM`. Valores abaixo são inventados.

```json
{
  "gerado_em": "2026-03-15T09:00:00",
  "moeda": "BRL", "unidade": "centavos", "mes_atual": "2026-03",
  "saldos": {
    "contas": [{"conta": "Banco A", "data": "2026-03-14", "saldo": 50000, "observacao": "...",
                "nao_confirmado": false, "historico": false, "idade_dias": 1}],
    "disponivel": 50000,
    "contas_fora_do_disponivel": ["Banco B"],
    "observacao": "Saldo bancario informado; nao e o resultado das movimentacoes."
  },
  "recebido": {"mes": 300000, "previsto_mes": 50000, "total_6m": 300000, "previsto_6m": 50000},
  "gastos": {"pagos_mes": 125050, "a_pagar_mes": 22000, "pagos_6m": 226050, "a_pagar_6m": 22000},
  "serie_mensal": [{"mes": "2026-03", "recebido": 0, "previsto": 0, "gasto_pago": 0, "gasto_a_pagar": 0}],
  "receitas_x_gastos": {"mes": "2026-03", "receitas": 300000, "gastos": 125050},
  "categorias": [{"categoria": "moradia", "valor": 100000, "percentual": 68.0}],
  "vencimentos": [{"data": "2026-03-10", "descricao": "...", "categoria": "contas", "valor": 10000,
                   "dias_restantes": -5, "atrasado": true, "status": "vencido"}],
  "movimentos_recentes": [{"data": "2026-03-03", "tipo": "gasto", "categoria": "mercado",
                           "descricao": "...", "valor": 25050, "status": "pago"}],
  "alertas": [{"tipo": "saldo_nao_confirmado", "mensagem": "...", "origem": "saldos.csv"}],
  "pendencias": {"abertas": ["..."], "resolvidas": 1, "arquivo_ausente": false},
  "fonte": {"arquivos": {"movimentos.csv": "2026-03-15T08:00:00", "saldos.csv": "...",
                         "transferencias.csv": null, "pendencias.md": "..."},
            "contagens": {"movimentos": 9, "contas": 2, "vencimentos": 3}}
}
```

## Bloco `meses` (seletor de mês, só acrescenta; o formato acima não muda)

`meses_disponiveis`: lista ordenada `AAAA-MM`, faixa contínua do primeiro lançamento até o mês atual (meses sem lançamento entram vazios; o mês atual sempre entra). `meses`: objeto indexado por `AAAA-MM`, todos os meses (não só 6). Valores inventados:

```json
"meses_disponiveis": ["2026-02", "2026-03"],
"meses": {
  "2026-02": {
    "mes": "2026-02", "recebido": 200000, "previsto": 30000, "gasto_pago": 0, "gasto_a_pagar": 0,
    "saldo_do_mes": 200000,
    "saldo_do_mes_rotulo": "Resultado das movimentacoes do mes (recebido menos gasto pago); nao e saldo bancario.",
    "categorias": [{"categoria": "moradia", "valor": 100000, "percentual": 100.0}],
    "movimentos": [{"data": "2026-02-05", "tipo": "recebido", "categoria": "salario",
                    "descricao": "...", "valor": 200000, "status": "pago"}],
    "vencimentos": [{"data": "2026-02-10", "descricao": "...", "categoria": "contas", "valor": 10000,
                     "dias_restantes": -33, "atrasado": true, "status": "vencido"}]
  }
}
```
- `saldo_do_mes` = `recebido` − `gasto_pago` (resultado das movimentações; a tela deve usar o rótulo e nunca chamá-lo de saldo bancário).
- `categorias`: gastos pagos e a pagar do mês, com valor e percentual. `movimentos`: todos os lançamentos do mês, por data (mais antigo primeiro), centavos inteiros. `vencimentos`: só gastos "a pagar" do mês.
- Para o mês corrente, `meses[mes_atual]` bate com `recebido.mes/previsto_mes`, `gastos.*_mes` e `categorias` da raiz (`vencimentos` da raiz continua com todos os meses). Nada é marcado como pago; fatura de cartão segue o que está no CSV (o gerador não cria despesa nem corrige).

## Semântica
- `saldos.contas`: último saldo por conta (maior data). `disponivel` soma só contas não marcadas "NÃO CONFIRMADO" nem "histórico"; as demais ficam em `contas_fora_do_disponivel` (a tela deve dizer que o total é parcial). Saldo bancário informado não é o resultado das movimentações; não há cálculo de saldo por movimentos.
- `recebido` conta `status = pago`; `previsto` conta recebimentos ainda não pagos ("a receber"). Gastos separam `pagos` e `a_pagar`. Janela de 6 meses inclui o mês atual. `categorias` considera os gastos (pagos e a pagar) do mês atual, ordenados por valor; lista vazia = estado vazio.
- `vencimentos`: só gastos "a pagar", por data. `status` em texto: `vencido` (dias < 0), `vence hoje`, `a pagar`. "pago" aparece só em `movimentos_recentes`. O gerador nunca marca nada como pago.
- `movimentos_recentes`: até 20, mais novos primeiro.
- `alertas[].tipo`: `saldo_nao_confirmado`, `saldo_velho` (> 7 dias), `saldo_divergente` (extrato citado na observação difere do informado), `pago_sem_lancamento` (descrição diz "pago em", status ainda "a pagar"), `valor_estimado`, `pendencia_aberta`, `linha_invalida` (linha de CSV ignorada, com arquivo e número). Sinaliza, não corrige.
- `fonte.arquivos`: data de modificação (ISO) ou `null` se ausente; mostrar junto de `gerado_em` como "última leitura".
