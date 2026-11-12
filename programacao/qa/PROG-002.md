# QA · PROG-002 · "Iniciar cenas" não faz nada (RODRYGO + ALISSON, 2026-11-04)

Rodado: `node estudio/testes/e2e_interface.mjs` (133 ok, 0 falhas) + `node estudio/testes/e2e_celular.mjs` (63 ok, 0 falhas). Teste de celular já estava presente e validado.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Clique inicia a etapa e a interface mostra retorno imediato | ✅ PASSOU | e2e_interface: "clique em #iniciar criou um trabalho só" e "CTA dá confirmação depois do retorno da API" (linhas 45, 129). |
| 2 | Se não puder iniciar, diz por quê e o que fazer | ✅ PASSOU | Cenas sem roteiro aprovado: "Falta o roteiro." aparece em `motivos`. Botão desabilitado com retorno visível. |
| 3 | Clique repetido não dispara duas vezes | ✅ PASSOU | e2e_interface: "clique duplo em gerar criou um render só" (linha 110). e2e_celular: "toque dispara a etapa cenas uma vez" (linha 182). |
| 4 | Progresso e fim aparecem; resultado vira nova versão | ✅ PASSOU | e2e_interface [8] e [9]: execução, nova tentativa conclui, trabalho continua após reinício. |
| 5 | e2e cobre o clique e falha sem a correção | ⚠️ NÃO PROVADO | Há cobertura do clique, mas não houve correção de código e não existe prova de que o teste falha sem ela (prova de mutação do `#iniciar` em `app.js` ~l.730 pendente). No celular o POST é simulado. Corrigido em 04/11 depois da revisão do **Thiago Silva** (eu havia marcado PASSOU sem evidência). |
| 6 | Computador e celular | ✅ PASSOU | e2e_interface 133 ok + e2e_celular 63 ok. Celular: "PROG-002: toque em Iniciar cenas mostra retorno imediato" + "toque dispara a etapa cenas uma vez" + "nada passa da largura da tela". |

**Atualização (Endrick, 2ª rodada, 04/11):** `e2e_interface` ganhou o bloco [1d] (150 ok): clique real em "Iniciar cenas" no desktop (1 trabalho, nova versão), botão bloqueado com motivo e orientação no DOM, caso sem motivo. Mutação do `onclick` do `#iniciar` (no-op): `e2e_celular` 3 falhas e `e2e_interface` 8 falhas; `app.js` restaurado idêntico. Sobre `app.js`: a lógica de disparo não mudou; só existem o texto de orientação (`orientarInicio`) e o aviso `semPorque`. Evidência completa em `entregas/PROG-002.md`. Critério 5 aguarda reconfirmação do **Alisson**.

**Veredito: critérios 1, 2, 3, 4 e 6 passaram; critério 5 não provado.** Nenhuma mudança de código foi necessária (a interface já tratava o caso). **Thiago Silva** DEVOLVEU em 04/11 (`revisoes/PROG-002.md`): falta clique real no desktop, teste do texto de orientação do botão bloqueado, prova de mutação e alinhar a entrega com este relatório.


## Reconfirmação final do Alisson (2026-11-04, após devolução do Thiago Silva)
Rodado por mim, uma bateria por vez: `e2e_interface` 150 ok / 0 falhas (bloco [1d]: clique real em "Iniciar cenas", botão bloqueado, 4 textos de orientação, caso sem motivo); `e2e_celular` 63 ok / 0 falhas.
**Critério 5 (mutação, reproduzida por mim):** troquei o `onclick` do `#iniciar` (app.js l.730) por no-op → `e2e_celular` 60 ok, **3 falhas**; restaurei e `cmp` com a cópia original sem diferença.
| # | Resultado |
|---|---|
| 1-4, 6 | PASSOU |
| 5 | PASSOU (teste fica vermelho sem o handler) |
Limite: no celular o POST é simulado; o servidor real é provado no desktop.
**Veredito: APROVADO** (aguarda reanálise do **Thiago Silva**, que disse aprovar na hora).
