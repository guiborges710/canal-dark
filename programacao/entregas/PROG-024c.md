# PROG-024c: painel dos 4 números da ilha de Finanças (Fluxo 1)

Autor: **Endrick**. Origem: Fluxo 1 de `programacao/ux/PROG-financa-detalhes.md` (**Iniesta**). Registro: `programacao/backlog.md`, item PROG-024c, liberado fora do quadro pelo Guilherme em 2026-11-12 (registrado pelo **Zico**). Fora do escopo, como o backlog manda: Fluxo 2 (alertas e pendências) e o botão "Marcar como pago".

## O que mudou na tela
- Os 4 cards (Saldo disponível, Recebido, Gasto pago, A pagar) são `<button>` com o `aria-label` da spec, chevron "›", dica "Ver movimentos" ao passar o mouse ou focar, foco visível, Enter e Espaço abrem. O card de gasto ganhou a legenda "só o que já foi pago".
- Clique abre um `<dialog>`: painel lateral de 480 px no desktop; folha de tela inteira com "Voltar" no celular (390 px). Esc fecha, o foco vai ao título ao abrir e volta ao card ao fechar. A tela de trás não rola.
- Conteúdo: resumo "Novembro de 2026 · 2 movimentos · Total R$ ...", seletor de mês, busca (descrição e categoria, no navegador), ordenação, agrupamento por dia ("Hoje, 12/11", "Ontem", dd/mm). A pagar agrupa em Vencidos, Vencem em até 3 dias e Mais adiante, com contagem, soma e situação em texto ("Venceu há 3 dias", "Vence hoje", "Vence em dd/mm"). Entradas com "+", saídas com "−", sempre com texto de status.
- Saldo: contas no topo (com "fora do disponível" e "atualizado em dd/mm") e o texto "O saldo do banco não é a soma destes movimentos...".
- Aviso em texto quando a soma da lista não bate com o card, com atalho "Veja Alertas".
- "Editar" em cada linha chama `editarMovimento()` sem alterá-lo; depois de salvar o painel recarrega a lista e os cards. O aviso "Lançamento atualizado." fica dentro do painel (a camada do `<dialog>` cobriria o toast).
- Âncora `#/financas/saldo|recebido|gasto|a-pagar`: o botão voltar do navegador fecha o painel; abrir a URL já abre o painel.
- Estados: carregando (esqueleto de 5 linhas só se passar de 300 ms; antes disso nada pisca), vazio (um texto por painel, com "Ver outro mês" / "Abrir A pagar"), erro (sem valor antigo, "Tentar de novo" com "Tentando…", mensagem de segunda falha, "Ver detalhes" recolhido), sem permissão ("Finanças só abre neste computador" + "Entendi"; cards com `aria-disabled` e "Bloqueado: abra no computador"), dados velhos (mais de 3 dias, "Atualizar leitura").
- "Ocultar valores" mascara tudo no painel (resumo, soma, grupos, aria-label).

## Arquivos
- `ecossistema/app/financas.js` (cards em botão, painel `pn*`, hashchange)
- `ecossistema/app/financas.css` (cards, painel, responsivo)
- `ecossistema/app/README.md` (seção do painel)
- `estudio/testes/e2e_financas.mjs` (função `painelDetalhes`, fixture inventada `fixPN`; nenhum valor real)

## Testes (teste primeiro)
- Antes de implementar: `node estudio/testes/e2e_financas.mjs` falhou nos casos novos (cards não eram botões; exceção ao clicar).
- Depois: `node estudio/testes/e2e_financas.mjs` -> **289 ok, 2 falhas**. Os 90 casos novos passam. Cobertura: 4 painéis, soma que bate e que não bate, busca (com e sem resultado), ordenação, mês, vazio de cada tipo, Editar, carregando, erro (duas falhas seguidas e recuperação), dados velhos, sem permissão, ocultar valores, âncora e voltar do navegador, 1440 e 390 (alvos de 44 px, sem rolagem lateral, valor visível, mês e busca em duas linhas).
- As 2 falhas restantes **não são desta entrega**: "gastos aparecem em vermelho" no tema claro e escuro (esperam `rgb(198, 40, 40)` e `rgb(255, 107, 99)`; a tela usa `rgb(196, 48, 29)` e `rgb(255, 123, 110)` de `estilo.css`). Falhavam igual antes das minhas mudanças; é a devolução da **Alisson** no PROG-024. Não mexi nisso.
- Não rodei `e2e_interface.mjs`, `e2e_corte.mjs` nem `e2e_celular.mjs`: esta tela é do app de Finanças e não toca o Corte.
- Capturas (inventadas, fora do git) em `%TEMP%\cap_pn2`: `painel_recebido_1440`, `painel_carregando_1440`, `painel_erro_1440`, `painel_velho_1440`, `painel_a_pagar_390`, `painel_saldo_390`.

## Casos pedidos
- Erro: painel com "Não consegui carregar os movimentos", sem valor antigo, "Tentar de novo" e "Ver detalhes".
- Estado vazio: texto por painel, por exemplo "Nada recebido em setembro" com "Ver outro mês".

## Decisões e limites (para **Thiago Silva** e **Zico**)
- Mês inicial do painel = mês escolhido na tela (não sempre o mês atual), para a lista bater com o número do card clicado.
- "Sem permissão": sem rota nova, o app detecta acesso fora do computador pelo endereço (`hostname` diferente de localhost, 127.0.0.1 ou file). Não há resposta 403 real na tela, nem o caso 401 ("Entrar"). `?acesso=remoto` simula, só para teste. Se o **Rodrygo** expuser 403/401 de leitura, ligar aqui.
- "Atualizar leitura" só relê `dados/financas.js`; não há endpoint que regenere os dados. Se continuar velho, o painel diz para rodar `python estudio/dados/gerar_financas.py`.
- Sem `meses` no arquivo (leitura antiga), a lista usa os 20 movimentos recentes e o aviso de soma diz isso.
- Gasto no painel usa o mesmo vermelho dos movimentos da tela (a spec dizia azul; o 024b e os testes usam vermelho). Decisão de cor fica com o **Iniesta**.
- Perguntas abertas ao Guilherme (a) renomear o card e (b) Finanças no celular seguem com a assunção do backlog.
- Já existia: o toast de "falha ao salvar" aparece atrás do modal de edição; não toquei no modal.
- Nada commitado, nada publicado, sem gasto de API.
