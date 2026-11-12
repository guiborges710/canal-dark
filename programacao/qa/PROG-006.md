# PROG-006 · QA · Alisson · 2026-11-05

Veredito: **DEVOLVIDO** ao **Endrick** (1 critério falha, correção pequena).

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Motor em texto (Claude/Codex) na etapa/versão | PASSOU | `e2e_motor.mjs`: chips nas 3 telas (lista, execução, faixas) |
| 2 | Nota aparece; sem nota nada vazio/"undefined" | PASSOU | `e2e_motor.mjs`: motor com nota, sem nota, nota vazia |
| 3 | Job antigo sem `motor` não quebra | PASSOU | `e2e_motor.mjs`: "trabalho antigo", sem erro de JS |
| 4 | Computador e celular sem quebrar layout | PASSOU | `e2e_motor.mjs` bloco celular 390x844; `e2e_celular.mjs` 63 ok |
| 5 | Teste automatizado cobre os 3 casos | PASSOU | `E2E_PORTA=8811 node estudio/testes/e2e_motor.mjs` → 29 ok, 0 falhas |
| 6 (refin.) | Motor desconhecido aparece como "motor não informado" | **FALHOU** | `corte_nav.js:75` mostra `Outro: <valor>` (ex.: "Outro: gemini"); o texto exigido não existe no código |
| 7 (refin.) | Mesma exibição vinda de um único componente | PASSOU | `seloMotor` único, usado nas telas de versão/execução/lista |

Regressão (uma por vez): `e2e_interface.mjs` 150 ok, 0 falhas; `e2e_celular.mjs` 63 ok, 0 falhas. Não rodei `e2e_corte` (a entrega já mostra 152 ok e não tocou nessas telas além do alvo).

## Bug/desvio
- Passos: abrir job com `motor: "gemini"`. Esperado (backlog, refinamento 6): "motor não informado". Obtido: "Outro: gemini".
- Correção: trocar o texto para "Motor não informado" (pode manter o valor no `title`) e ajustar o teste do `e2e_motor.mjs`. Se o **Iniesta**/**Zico** preferirem "Outro: <valor>", o **Zico** atualiza o critério e re-aceito na hora.

## Reteste (Alisson, 2026-11-05, após ajuste do Endrick)
Veredito final: **APROVADO** (critérios 1 a 7 PASSOU).
- 6: `corte_nav.js:75` → "Motor não informado"; `e2e_motor.mjs` exige o texto e recusa "Outro:" e o valor cru. PASSOU.
- Rodado agora, uma por vez: `e2e_motor.mjs` 29 ok, 0 falhas; `e2e_interface.mjs` 150 ok, 0 falhas; `e2e_celular.mjs` 63 ok, 0 falhas.
- Critérios 1-5 e 7: sem mudança de código além do texto; reconfirmados pelos mesmos 29 testes.
