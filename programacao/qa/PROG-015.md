# QA PROG-015 · CTA da próxima etapa precisa funcionar (Alisson, 2026-11-04)

Execução: `node estudio/testes/e2e_interface.mjs` (CTA funcional) e `node estudio/testes/e2e_celular.mjs` (viewport celular).

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Para cada estado em que a chamada aparece, o rótulo descreve corretamente o efeito do clique | PASSOU | e2e: "CTA só confirma depois da resposta real da API", "CTA criou a narração de verdade", "servidor devolve novo=false e a tela explica sem mostrar sucesso". |
| 2 | Ao clicar, a interface dá retorno imediato e inequívoco | PASSOU | "CTA dá confirmação depois do retorno da API" (linha 129, e2e_interface); "CTA inicia a etapa indicada em vez de apenas abrir o painel" (linha 130). |
| 3 | Sucesso só aparece depois da confirmação do efeito real; o estado/resultado permanece visível após atualização da tela | PASSOU | "o andamento continua visível depois de recarregar a página" (linha 26); "parecer já foi encaminhado" persiste (linha 14). |
| 4 | Se a ação estiver bloqueada ou falhar, a interface explica o motivo e o próximo passo | PASSOU | "quando não consegue atribuir o apontamento, explica e não mostra sucesso" (linha 17); "etapa inexistente é recusada pela API" (linha 30). |
| 5 | Cliques repetidos não duplicam ações nem execuções | PASSOU | "clique duplo em gerar criou um render só" (linha 110); "repetir o pedido não criou outra narração" (linha 28); "clique duplo em enviar criou um trabalho só" (linha 45). |
| 6 | Teste e2e reproduz "Resolver o parecer do Vini" e um CTA de início, verifica a operação/API e o estado resultante; testa também erro/bloqueio | PASSOU | Bloco [1c] "CTA 'Iniciar ...' no topo: dispara a operação real" (linhas 20-30); "parecer bloqueado apresenta a ação de resolução" e encaminhamento (linhas 9-18); "etapa inexistente é recusada pela API" (linha 30). |
| 7 | Funciona nos tamanhos de tela em que a chamada aparece (computador e celular) | PASSOU | e2e_interface 133 ok; e2e_celular: "PROG-015: CTA do topo dispara a ação real no celular" e "CTAs no celular: nada passa da largura da tela". |

**Veredito: APROVADO pelo QA.** Todos os 7 critérios passaram. Entregas:
- e2e_interface: 133 ok, 0 falhas
- e2e_celular: 63 ok, 0 falhas

Pendente: revisão do **Thiago Silva** e aceite final do Guilherme.
