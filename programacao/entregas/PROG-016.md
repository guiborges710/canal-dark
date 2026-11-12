# PROG-016 · Catálogo com estado por agente · Entrega (Endrick)

Data: 2026-11-09. Nota técnica: `tecnico/PROG-016.md`. Desenho: `ux/prog-016-catalogo-ocioso.md`.

## O que mudou na tela (Catálogo, `/agentes?aba=catalogo`)
- Cada agente da lista ganha um selo de estado à direita do nome: **○ Ocioso**, **◐ Trabalhando**, **⏳ Na fila**, **✕ Falhou** e **❚❚ Espera você** (o quinto vem da tela Ao vivo, para não divergir). Sempre ícone + texto; o ícone é `aria-hidden`.
- Quando há trabalho, uma linha embaixo: `vídeo · etapa · há N min` (trabalhando), `vídeo · etapa` (fila e espera você), `vídeo · falhou em etapa` (falhou). Vários vídeos: primeiro + ` · +N`. Ocioso não mostra vídeo, etapa nem tempo.
- "Desativado" continua ao lado do selo de estado.
- Antes da primeira resposta: "… Verificando" (nunca "Ocioso"). Consulta com erro: mantém os selos e o rodapé avisa "(desatualizado) Não consegui atualizar os estados...". Todos ociosos: rodapé "Ninguém trabalhando agora...". Busca sem resultado e catálogo vazio têm frase própria. Erro ao carregar a lista: mensagem + botão "Tentar de novo".
- Atualização no lugar (`marcarEstados`), sem refazer a lista: busca digitada, item selecionado e edição aberta sobrevivem. Usa o `Vivo` (polling de 4 s que já existia); nenhuma rota nem consulta nova.
- Celular: itens com no mínimo 44 px, selo quebra de linha em vez de cortar, sem rolagem lateral.

Arquivos: `estudio/web/corte_agentes.js` (`estadoDe`, `marcarEstados`, `desenharLista`, erro em `carregar`), `corte_nav.js` (`ocioso`, `verificando` em `ICONES_ESTADO`), `corte.css`, `celular.css`. Servidor e `ao_vivo.py` intocados.

## Testes
Novo `estudio/testes/e2e_agentes_catalogo.mjs` (Chrome real, servidor em cópia descartável, claude simulado, agentes do catálogo real, sem ids fixos).
Observação honesta: escrevi o código e o teste na mesma rodada; a primeira execução achou um erro do meu teste (o "Desativado" vem do catálogo, não do Ao vivo), corrigido desativando um agente de verdade na cópia.

Comandos e resultado real (uma bateria por vez):
- `E2E_PORTA=8803 node estudio/testes/e2e_agentes_catalogo.mjs` → **47 ok, 0 falhas**
  - cobre: todos ociosos (estado vazio, sem "Falhou"/tempo para quem não tem histórico), os quatro estados + espera você com vídeo/etapa, "+2", Desativado junto, mesmo estado que a aba Ao vivo (comparação lado a lado), atualização sem recarregar em 1 ciclo e sem consulta nova, busca/edição/seleção sobrevivendo ao ciclo, "Verificando", erro de consulta (caso de erro), erro da lista, busca sem resultado, rota `/agentes/<id>` + Editar, 390 px (sem rolagem lateral, uma coluna, ≥ 44 px, texto do selo visível), zero erro de JS.
- Regressão: `e2e_agentes_ao_vivo.mjs` → 91 ok, 0 falhas · `e2e_celular.mjs` → 64 ok, 0 falhas · `e2e_interface.mjs` → 150 ok, 0 falhas.
- `testar_ao_vivo.py` (rodei só para ver, é do **Rodrygo**) → 49 ok, 0 falhas; 50 jobs: rota em 41 ms (limite 200 ms).

## O que falta
- **Rodrygo**: acrescentar em `testar_ao_vivo.py` o caso "agente do catálogo ausente de `agentes` = ocioso" e gravar `qa/PROG-016.md` com a medição dos 50 jobs (critério 7). Não toquei no teste dele.
- **Alisson**: QA e aceite. **Zico**: confirmar que "Espera você" aparece no Catálogo como quinto estado.
