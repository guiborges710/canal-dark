# Revisão PROG-015 · CTA da próxima etapa (Thiago Silva, 2026-11-04)

**Veredito: APROVADO.**

Método: leitura do código atual (sem shell nesta sessão, então sem `git diff`; conferido contra a entrega e o QA).

## O que li
- `estudio/fluxo.py` 652-661 (`_parecer_encaminhado`), 664-690 (`resolver_parecer_vini`), 848-886 (`resumo`).
- `estudio/web/app.js` 227-240 (CTA do topo), 653-659 (`iniciar`).
- `estudio/testes/e2e_interface.mjs` [1b] (101-143) e [1c] (145-201); `comandos_simulados.py` (`.segurar_*`) só pelo uso nos testes.

## Pontos aprovados
- A extração `_parecer_encaminhado` é a mesma consulta usada pela idempotência, então topo e servidor não divergem. `resolver_parecer_vini` mantém o comportamento.
- O estado vem do servidor, então sobrevive a recarregar (teste na linha 119 prova).
- O CTA `iniciar` só confirma depois da resposta da API e trata `novo=false` ("Nada foi disparado"), sem sucesso falso.
- [1c] usa servidor real, clique duplo e confere pela API que existe 1 só trabalho. O `novo=false` só congela a resposta de estado da aba velha; o POST é real. Há prova de sabotagem registrada (8 falhas sem a correção).
- Os dados de teste ficam em `caixa/` (pasta temporária), de acordo com D-004. Nenhuma referência a ids fixos de nó fora de `narracao`/`ap_*`, que vêm do contrato.

## Riscos (não bloqueiam)
1. `resumo` só olha `ATIVOS`: se o trabalho do agente terminar com erro e a versão do parecer continuar a mesma, o topo diz "já recebeu o parecer" sem avisar a falha. Mitigação existente: a etapa do agente passa a `falhou` e vira `atual` antes (ordem em 853). Não há teste dessa combinação. Sugiro um item de backlog ao **Zico**: caso "job do reparo falhou".
2. `x["job_id"]` nulo (feedback gravado sem job) cai em "o responsável". Comportamento herdado, mas vale teste.
3. Entrega diz "133 ok"; QA confirma 133/63. Consistente.

## Pendências
Nenhuma para o **Rodrygo**. **Zico** decide se abre o item do risco 1.
