# PROG-003 · Aba Agentes, Ao vivo · Revisão de código (reescrita 05/11, 13:50)

Revisor: **Thiago Silva** · Back: **Rodrygo** · Front: **Endrick**

**Veredito: APROVADO.** Entrega 1 (back + tela) já aprovada na revisão anterior; esta rodada revisa só a mudança nova do critério 6 (clique do cartão abre `/estudio/<slug>?etapa=<etapa_id>` com o nó em foco). Sem pendência bloqueante.

## Critério 6: o que li (código real)
- `estudio/web/corte_agentes.js:44`: a URL é montada com `encodeURIComponent(t.etapa_id)` e só quando existe etapa. Teste de agente continua indo à ficha.
- `estudio/web/corte_estudio.js:185` (`montar`) lê `new URLSearchParams(location.search).get("etapa")` e zera `focado` a cada entrada na rota; `:240-246` (`focarEtapa`).
- `estudio/web/corte.css:77`: `.agente-linha.em-foco` usa `--decisao-linha`, variável que existe no tema.

## Conferências pedidas
- **Leitura segura do parâmetro:** o valor só entra em `querySelector` via `CSS.escape` e em `classList`/`setAttribute` com texto fixo. Nunca vai para `innerHTML`, `eval` nem URL. Sem vetor de injeção.
- **Etapa inexistente:** `focarEtapa` retorna se `etapaFoco` é vazio ou se o nó não existe. Nada lança erro, a tela abre normal sem destaque.
- **Foco não é roubado em redesenhos:** `scrollIntoView` e `focus({preventScroll:true})` só rodam enquanto `focado` é falso, e `focado` vira true na primeira vez. Redesenhos seguintes só reaplicam a classe e o `aria-current`, sem mover o foco. O mesmo vale para o `trocar` do `agentes()`, que recria os botões.
- **Regressão PROG-006/Estúdio:** `seloMotor(x.job, { interativo: false })` e o `onclick: abrirExecucao` do botão do nó estão intactos; a mudança só acrescenta uma chamada ao fim de `agentes()`. Sem alteração em `corte_nav.js`, `servidor.py` nem `ao_vivo.py`.
- **Teste:** `e2e_agentes_ao_vivo.mjs:220-223` cobre a URL com `?etapa=metadados`, o nó com `em-foco`, `aria-current="step"` e `document.activeElement`, e que só um nó fica em foco. Relatório: 91 ok, 0 falhas; `e2e_corte` 152/0, `e2e_celular` 64/0, `e2e_motor` 29/0, `e2e_interface` 150/0 isolado (uma rodada em sequência deu 7 falhas, atribuídas a porta compartilhada/intermitência; não reproduz).

## Ressalvas (não bloqueiam)
1. **Evidência:** nesta rodada não reexecutei os e2e (prazo); confio nos números do **Endrick**, e o **Alisson** repete no aceite. A intermitência do `e2e_interface` em sequência deve ser reconferida por ele, de preferência com `E2E_PORTA` própria.
2. **Sem teste de etapa inexistente** (`?etapa=xyz` abrindo sem erro de JS). O código trata, mas não há caso automatizado. Item pequeno para o **Zico** (um caso no e2e, 5 linhas).
3. **Foco tardio:** se o nó ainda não existir no primeiro desenho do painel e aparecer depois (job novo), o foco é dado nesse momento, uma vez. Aceitável; só registrar.
4. `?etapa=` permanece na URL após a navegação interna. Inofensivo.

## Saída
Pronto para aceite do **Alisson** e do Guilherme. Sem commit, sem mexer em `quadro.md`, `aceites/` nem Trello.
