# PROG-006 · Code Review · Thiago Silva · 2026-11-05

**Veredito: APROVADO.**

Código lido: `estudio/web/corte_nav.js` (69-97), `corte_estudio.js` (230, 318), `app.js` (310, 317), `corte.css` (84-90).

## O que conferi
- Um único componente `seloMotor` serve as três telas (lista de agentes, diálogo de execução, faixas da revisão). Sem duplicação.
- Entrada defensiva: `typeof job.motor === "string"`, `trim().toLowerCase()`; sem motor devolve `null`, então job antigo, comando ou sem job não mostra nada e não gera "undefined" (linha 70-71).
- Nota vazia ou só espaços vale como sem nota (linha 72).
- Motor desconhecido mostra "Motor não informado" (linha 75), como pede o critério 6.
- Texto da nota entra por `h(...)` como conteúdo de texto, sem `innerHTML`, então uma nota com HTML não injeta nada.
- Acessibilidade: `role`, `aria-label` completo, `aria-expanded` no chip Codex; o toque abre a explicação sem depender de hover (celular).
- CSS com `overflow-wrap: anywhere` e `min-width: 0`, sem estouro em 390 px.
- O back-end não foi tocado, então não há risco de contrato.

## Evidência
- `E2E_PORTA=8821 node estudio/testes/e2e_motor.mjs`: **29 ok, 0 falhas** (rodado por mim agora).
- Resultados do **Alisson** em `qa/PROG-006.md`: interface 150 ok, celular 63 ok.

## Observações (não bloqueiam)
- Motor desconhecido não guarda o valor cru no `title`. Pode ajudar o diagnóstico no PROG-003.
- O "Detalhes" recolhido do desenho do **Iniesta** ficou de fora; o **Zico** decide se vira item.
