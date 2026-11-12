# Entrega PROG-015 · CTA da próxima etapa (Rodrygo, 2026-11-04)

Pronto para **Alisson** (QA) e revisão do **Thiago Silva**. Nada commitado. Esta entrega substitui a versão anterior (a de **Endrick**/Codex), que dizia "disparo real" mas só provava o CTA de início com `fetch` simulado.

## Devoluções do Thiago Silva e como cada uma foi atendida

1. **Faixa persistente após o envio do parecer.** Antes, o único retorno era um toast; depois de recarregar, o topo voltava a oferecer "Resolver o parecer do Vini". Agora `fluxo.resumo` consulta os trabalhos já criados para aquela versão do parecer (`_parecer_encaminhado`, a mesma consulta que dá a idempotência a `resolver_parecer_vini`) e o topo passa a dizer "Parecer do Vini encaminhado: Mbappé está corrigindo" (tipo `sistema`, sem link) ou, terminado o trabalho, "Abrir a auditoria de texto: Mbappé já recebeu o parecer do Vini" (navegação, com o verbo `Abrir`). O estado vem do servidor, então sobrevive a recarregar a página.
2. **Teste real de `/iniciar`.** Nova função `ctaIniciarReal` em `e2e_interface.mjs`: cópia de `esquema-de-piramide` na caixa, roteiro e cenas aprovados pela API, o topo passa a "Gerar narração" (`acao: iniciar`), clique no topo (duplo) contra o servidor real, sem `fetch` simulado. Confere pela API que existe exatamente 1 trabalho de narração, em fila/rodando.
3. **`novo: false` real.** Uma segunda aba mostra o CTA antigo (só a resposta de estado foi congelada para simular a aba desatualizada); o clique chega ao servidor de verdade, que devolve `novo=false`; a tela mostra "Nada foi disparado", sem "Trabalho iniciado", e a API continua com 1 trabalho ativo. Para segurar o trabalho "em andamento" de forma determinística, o simulador ganhou `.segurar_render` e `.segurar_narracao` (máx. 30 s).
4. **Prova de que o teste falha sem a correção.** Reintroduzi o bug original (a ramificação `acao === "iniciar"` do CTA desligada, caindo em "apenas abrir"): `e2e_interface` ficou com 125 ok e **8 falhas** (CTA só confirma depois da API, criou a narração, andamento visível, `novo=false`, pedido repetido, narração terminou, e os 2 do teste antigo com stub). `app.js` restaurado e conferido idêntico (diff). Para o item 1, a rodada vermelha anterior ao código novo falhou nos 3 testes de persistência (topo continuava "Abrir para revisar roteiro", API sem "Mbappé").
5. **Entrega inconsistente.** Este arquivo foi reescrito a partir do que foi rodado de fato nesta sessão.

## Arquivos alterados

- `estudio/fluxo.py`: `_parecer_encaminhado` (extraída), `resumo` usa o estado do encaminhamento; `resolver_parecer_vini` reaproveita a extração (comportamento igual).
- `estudio/testes/e2e_interface.mjs`: 3 testes de persistência no [1b] e o bloco novo [1c] (`ctaIniciarReal`).
- `estudio/testes/comandos_simulados.py`: `.segurar_render` e `.segurar_narracao`.
- `estudio/web/app.js`: sem mudança nesta entrega (o disparo de `iniciar` já estava no código; foi o teste que o provou).

## Comandos rodados e resultado real

- Vermelho antes do código: `node estudio/testes/e2e_interface.mjs` -> 120 ok, 9 falhas (3 de persistência, 6 do CTA real, o último por um estado de teste que corrigi depois).
- Verde: `node estudio/testes/e2e_interface.mjs` -> **133 ok, 0 falhas**.
- Sabotagem: mesmo comando, bug reintroduzido -> 125 ok, **8 falhas** (restaurado).
- `node estudio/testes/e2e_celular.mjs` -> 63 ok, 0 falhas.
- `node estudio/testes/e2e_corte.mjs` -> 152 ok, 0 falhas.
- `node estudio/testes/e2e_estilos.mjs` -> 98 ok, 0 falhas.
- `.venv\Scripts\python.exe estudio\testes\testar_estilos.py` -> 103 ok, 0 falhas.
- `.venv\Scripts\python.exe estudio\testes\testar_reserva_codex.py` -> Tudo certo (50 ok).

## Observações

- Rodar duas baterias e2e ao mesmo tempo gera falhas falsas (a primeira rodada de `e2e_interface` teve 4 falhas quando rodou junto com outro teste, e passou 120/120 isolada). Rodar uma por vez, ou usar `E2E_PORTA`.
- O CTA de início aparece só quando a etapa está `pronta`; quando está `desatualizada` o texto é "Abrir para atualizar ..." (navegação), como o critério 1 pede.
- Critério 7 (celular): `e2e_celular` continua verde; o novo bloco de CTA real roda só na bateria de desktop. O toque no celular segue coberto pelo teste anterior de 390x844.

## Pendente

Validação do **Alisson** (critérios 1 a 7) e revisão do **Thiago Silva**. Aceite final com o Guilherme.
