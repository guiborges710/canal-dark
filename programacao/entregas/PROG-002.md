# Entrega PROG-002 · "Iniciar cenas" (2ª rodada, após devolução do Thiago Silva)

Data: 2026-11-04. Responsável: **Endrick**. Pronto para nova validação do **Alisson** e do **Thiago Silva**.

## O que mudou em `app.js` (versão única, igual ao QA)
O clique em `#iniciar` já funcionava: **nenhuma lógica de disparo foi corrigida**. O que o PROG-002 acrescentou ao `app.js` (já no código antes desta rodada) é só texto: `orientarInicio` junta ao motivo do servidor o que fazer, e o aviso `semPorque` aparece quando o botão está bloqueado sem motivo. Nesta rodada **o `app.js` não foi alterado** (conferido byte a byte após a mutação). Só testes mudaram.

O "Iniciar cenas" do desktop usa o mesmo `onclick` do `#iniciar` das outras etapas (narração, render); agora também há clique real nele.

## Arquivos
- `estudio/testes/e2e_interface.mjs` (novo bloco `[1d]`, funções `copiarSemCenas`, `esperarVersao0`, `tirarCenas`, `iniciarCenasReal`)
- `estudio/testes/e2e_celular.mjs`, `estudio/testes/testar_prog001_002.py` (sem mudança nesta rodada)

## Os três itens da devolução
**(a) Texto de orientação no DOM** (bloco `[1d]`, servidor real + resposta de estado trocada só na leitura da tela):
- Bloqueio real (roteiro sem aprovação, sem cenas): botão `disabled`, motivo "Aprove o roteiro (v1)." visível, clique no botão bloqueado não cria trabalho.
- "Falta o roteiro." → "…Gere e aprove o roteiro antes de iniciar cenas."; "roteiro … não aprovado" → "Abra a etapa Roteiro e aprove a versão atual."; "outra etapa rodando" → "Aguarde esse trabalho terminar e tente novamente."; "Falta a pesquisa" → "Abra a etapa pendente e conclua a ação indicada…".
- Caso vazio (`semPorque`): "o sistema não informou o motivo… trabalho em andamento ou etapa anterior pendente", botão desabilitado, sem sucesso falso.

**Clique real no desktop** (sem fetch simulado): produção com roteiro aprovado e sem cenas; estado real "Iniciar cenas (Olise)" habilitado; clique duplo → aviso "Trabalho iniciado", **1 único trabalho** de cenas, termina `ok`, cenas aparecem como nova versão.

**(b) Mutação**: troquei o `onclick` do `#iniciar` por no-op.
- `e2e_celular`: **60 ok, 3 falhas** (toque mostra retorno imediato; toque dispara cenas uma vez; CTA do topo).
- `e2e_interface`: **96 ok, 8 falhas**, incluindo as 4 do clique real em "Iniciar cenas" (retorno, 1 trabalho, término, nova versão) e as de narração/render que usam o mesmo botão.
- `app.js` restaurado: `cmp` com a cópia original sem diferença; marca da mutação ausente.

**(c)** Entrega e `qa/PROG-002.md` agora dizem o mesmo (acima).

## Resultado real após restaurar
- `node estudio/testes/e2e_interface.mjs` → 150 verificações ok, 0 falhas (eram 133; +17 do bloco [1d]).
- `node estudio/testes/e2e_celular.mjs` → 63 ok, 0 falhas.
- `.venv\Scripts\python.exe estudio\testes\testar_prog001_002.py` → Tudo passou.
- Não rodei de novo `e2e_corte` e `e2e_estilos` (nenhum arquivo deles ou de produção mudou nesta rodada).

Limite honesto: no celular o POST continua simulado (o servidor real é provado no desktop, mesmo handler).
