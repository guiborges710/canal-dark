# PROG-016 · Catálogo com estado por agente (ocioso, trabalhando, na fila, falhou) · Nota técnica

Autor: **Thiago Silva** · 2026-11-09 · Quem faz: **Endrick** (tela, quase tudo) e **Rodrygo** (teste de dados e medição). Desenho: **Iniesta** (antes de codar, ver "Pendência de desenho").

## Abordagem (decisão: juntar no navegador, sem rota nova)
O estado de cada agente já existe em `GET /api/agentes/ao-vivo` (`estudio/ao_vivo.py`), consultado a cada 4 s por `Vivo` (`corte_nav.js:104`) em qualquer tela, inclusive no Catálogo. A lista de todos os agentes já vem de `GET /api/agentes`. O Catálogo faz o cruzamento no navegador:

- `Vivo.dados.agentes` tem só quem **não** está livre. Logo: agente do catálogo presente ali = estado dele (`estado`, `trabalhos`); ausente = **ocioso**.
- Isso cumpre por construção o critério 4 (mesma fonte da tela Ao vivo, não há segundo cálculo para divergir), o 5 (polling existente, nenhum novo) e o 7 (a resposta já é medida em `testar_ao_vivo.py`, 50 jobs, limite 200 ms).
- Critério 3: sem job e sem histórico, o agente cai em "ocioso" sem vídeo, etapa ou tempo. Critério 2: ocioso mostra só o texto "Ocioso".
- Rejeitado: acrescentar `estado` em `/api/agentes`. Faria cada abertura do Catálogo recalcular "Espera você" (olha produções) e criaria uma segunda fonte que pode divergir.

## Contrato
Sem mudança de API. Atenção: o estado "Espera você" (`espera_voce`) existe no Ao vivo; o Catálogo mostra também, para não divergir (critério 4). O critério 1 lista quatro estados; "Espera você" é o quinto, herdado. **Zico** confirma no aceite (não muda escopo, só espelha a tela Ao vivo).

## Arquivos
- `estudio/web/corte_agentes.js`: `desenharLista` (linha ~222) ganha, em cada `.ag-item`, um selo de estado (`seloEstado(...)`, ícone + texto) e, se trabalhando/fila/falhou, uma linha curta com vídeo e etapa do primeiro trabalho. `Agentes.montar` já registra `Vivo.ouvir(...)`; no ouvinte, quando `aba === "catalogo"`, chamar um `marcarEstados()` que **só atualiza os selos** (sem refazer a lista, para não apagar a busca digitada nem a edição em curso; padrão `seMudou`, não agir se `this.editando`).
- `estudio/web/corte_nav.js`: acrescentar `ocioso: ["○", "Ocioso"]` em `ICONES_ESTADO`.
- `estudio/web/corte.css` e `celular.css`: classe `.estado.ocioso` discreta (cinza, com texto); em 390 px, selo e linha de vídeo quebram dentro do `.ag-item`, sem rolagem lateral.
- Não mexer em `ao_vivo.py` nem `servidor.py`.

## Riscos
1. **Redesenho apagando digitação/edição**: o ouvinte do `Vivo` roda a cada 4 s. Atualizar selos in place; nunca chamar `desenharLista` por polling.
2. Dado velho: se `Vivo.erro`, manter o último estado e mostrar "(desatualizado)" no rodapé da lista, como na Ao vivo.
3. Agente do catálogo desativado (`ativo=false`) com job rodando: mostra o estado e o selo "Desativado" juntos.
4. Agente com job mas sem arquivo no catálogo: simplesmente não aparece (o Catálogo é a fonte da lista).
5. Estado antes da primeira resposta do `Vivo` (`dados` nulo): mostrar "…" discreto, nunca "Ocioso" (mentiria).

## Pendência de desenho
Não há desenho do **Iniesta** para o selo no item do Catálogo (o `prog-003-006-agentes-desenho-b.md` só diz "o Catálogo só atualiza os selos", linha 101). **Iniesta** entrega em `programacao/ux/prog-016-catalogo.md`: posição do selo, texto do ocioso, aparência desativado+estado, e a ordem opcional (ativos primeiro?). Sem isso o **Endrick** não começa a parte visual; o cruzamento de dados e o teste dele podem começar.

## Testes exigidos
- Novo `estudio/testes/e2e_agentes_catalogo.mjs` (com `claude_simulado`, porta própria via `E2E_PORTA`): quatro estados no Catálogo (ocioso, trabalhando, fila, falhou) + espera_voce; ocioso sem vídeo/etapa/tempo; agente sem histórico sem "falhou"; mesmo estado que a aba Ao vivo para o mesmo agente (compara os dois); atualização sem recarregar (muda o job, espera ≤ 1 ciclo); busca digitada e edição aberta sobrevivem a um ciclo; 390 px sem rolagem lateral (`document.documentElement.scrollWidth <= innerWidth`) e uma coluna.
- `testar_ao_vivo.py` (já cobre ocioso/50 jobs): **Rodrygo** só acrescenta um caso "agente do catálogo ausente de `agentes` = ocioso" para fixar o contrato que o Catálogo usa, e roda para medir os 50 jobs (resultado em `qa/PROG-016.md`).
- Regressão: `e2e_agentes_ao_vivo.mjs`, `e2e_interface.mjs` (edição e rotas `/agentes/<id>`), `e2e_celular.mjs`. Uma bateria e2e por vez. `e2e_interface.mjs` ainda tem pendência do PROG-005 (`se_sketch`); **Alisson** registra o que já estava vermelho antes.
- Fixtures derivam agentes de `agentes.catalogo()`, nunca ids fixos (D-004).

## Ordem
1. **Iniesta**: desenho curto. 2. **Rodrygo**: caso de teste de contrato + medição (rápido, paralelo). 3. **Endrick**: tela + e2e. 4. Revisão minha. Estimativa: P-M.
