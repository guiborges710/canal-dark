# PROG-006 · Aba Agentes, fatia A: motor e nota na tela · Entrega

Autor: **Endrick** · 2026-11-05. Desenho: **Iniesta** (`ux/prog-003-006-agentes-desenho-b.md`, tabela "Motor e nota"). Nota técnica: **Thiago Silva** (`tecnico/PROG-003.md`, seção PROG-006 embutido).

## O que mudou na tela
Um componente só, `seloMotor(job, opcoes)` em `estudio/web/corte_nav.js` (ao lado de `seloEstado`), usado em três lugares:
1. **Lista de agentes do Estúdio** (`corte_estudio.js`, `agentes()`): chip em texto sob a tarefa. Sem botão, porque a linha já é botão; a explicação vai no `title`.
2. **Diálogo de execução** (`abrirExecucao`): linha "Motor" com chip e nota; trabalho de agente sem motor registrado mostra "Motor: não registrado (trabalho antigo)."
3. **Faixas da revisão** (`app.js`, "em execução" e "Falhou"): chip junto do título.

Regras (tabela do desenho): Claude sem nota = só o chip; Codex = chip com ponto âmbar + nota em cinza, ou a frase padrão "Este trabalho rodou no Codex, a reserva usada quando o Claude esgota o limite."; nota vazia ou só espaços vale como sem nota; motor desconhecido aparece como "Outro: <valor>"; sem `motor` (job antigo, comando, sem job) não aparece nada, nem "undefined". No chip Codex (fora da lista) o toque abre "O Claude estava no limite; este trabalho rodou no Codex." (ou "está rodando"), sem depender de hover; `aria-expanded` e `aria-label` completo ("Motor: Codex. <nota>").
CSS novo no fim de `corte.css` (`.selo-motor`, `.chip-motor`, `.motor-dica`), com `overflow-wrap` para não estourar no celular.

Arquivos: `estudio/web/corte_nav.js`, `corte_estudio.js`, `app.js`, `corte.css`, `estudio/README.md` (linha da nova bateria). Teste novo: `estudio/testes/e2e_motor.mjs`. Back-end não foi tocado (já entrega `motor` e `motor_nota`).

## Testes (teste primeiro)
Antes do código, `e2e_motor.mjs` falhou com `seloMotor is not defined`. Depois do código:
- `E2E_PORTA=8801 node estudio/testes/e2e_motor.mjs` → **29 verificações ok, 0 falhas** (cobre motor com nota, sem nota, job sem o campo, nota vazia, desconhecido, comando/nulo, as três telas, celular 390x844 com toque).
- Regressão, uma por vez: `e2e_interface.mjs` **150 ok, 0 falhas**; `e2e_celular.mjs` **63 ok, 0 falhas**; `e2e_corte.mjs` **152 ok, 0 falhas**.
- Não rodei `e2e_estilos.mjs` nem `testar_estilos.py` (não tocam as telas alteradas; fica para a regressão do **Alisson**).

Caso de erro: motor desconhecido ("gemini") vira "Outro: gemini"; job antigo (`{id:1}`) não gera selo nem erro de JS. Caso vazio: sem job, ou nó sem trabalho, não mostra nada sobre motor.

## Limites honestos
- Os testes injetam o `job` no estado da página (a tela é a mesma). O contrato real `status_job_publico` com motor codex/claude já é coberto por `testar_reserva_codex.py` (não rodei de novo, sem mudança de back).
- Não há ainda tela com histórico de versões do job; quando o PROG-003 criar a aba Ao vivo, reaproveita `seloMotor`.
- O desenho previa "Detalhes" recolhido para nota técnica em inglês; não implementei (as notas do `executor.py` já estão em português, exceto o erro bruto que vem no fim da nota de falha da reserva). Sugiro ao **Iniesta**/**Zico** decidir se vira item.

## Ajuste pós-QA (Endrick, 2026-11-05) — critério 6
O **Alisson** devolveu: motor desconhecido deve aparecer como "Motor não informado" (refinamento 6), não "Outro: <valor>". Teste primeiro: `e2e_motor.mjs` passou a exigir "Motor não informado" e a não mostrar o valor cru. Código: `seloMotor` em `corte_nav.js` agora usa "Motor não informado" para motor diferente de Claude/Codex.
Resultados reais: `e2e_motor.mjs` 29 ok, 0 falhas; `e2e_interface.mjs` 150 ok, 0 falhas; `e2e_celular.mjs` 63 ok, 0 falhas (uma por vez). Não rodei `e2e_corte.mjs` de novo (a mudança é só de texto do selo).
