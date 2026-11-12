# QA PROG-016 · Catálogo com estado por agente (Alisson, 2026-11-09)

Veredito: **APROVADO** (segue para Code Review).

Baterias executadas por mim, uma por vez, nesta sessão:
- `E2E_PORTA=8803 node estudio/testes/e2e_agentes_catalogo.mjs` → 47 ok, 0 falhas
- `python estudio/testes/testar_ao_vivo.py` → 49 ok, 0 falhas (50 jobs + 30 produções: rota em 44 ms no pior de 5; montar() 5-32 ms; limite 200 ms)
- Regressão: `e2e_agentes_ao_vivo.mjs` 91 ok · `e2e_celular.mjs` 64 ok · `e2e_interface.mjs` 150 ok, todas 0 falhas.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Todos os agentes com estado + texto | PASSOU | e2e_agentes_catalogo, seções 1-2 (selo com ícone e texto) |
| 2 | Ocioso sem vídeo/etapa/tempo | PASSOU | e2e_agentes_catalogo, caso todos ociosos |
| 3 | Sem job e sem histórico não mostra "falhou"/tempo | PASSOU | idem |
| 4 | Mesmo estado da aba Ao vivo | PASSOU | comparação lado a lado no e2e; e2e_agentes_ao_vivo 91 ok |
| 5 | Atualiza sozinho, polling existente | PASSOU | teste de 1 ciclo sem recarregar e sem consulta nova |
| 6 | Celular 390 px | PASSOU | seção 7: sem rolagem lateral, uma coluna, ≥ 44 px; e2e_celular 64 ok |
| 7 | 50 jobs < 1 s | PASSOU | rota 44 ms (testar_ao_vivo.py) |
| 8 | Edição e rotas /agentes/<id> | PASSOU | seção 6 + e2e_interface 150 ok |
| 9 | Teste cobre os 4 estados; resultado aqui | PASSOU | este arquivo; e2e novo roda em estudio/testes/ |

## Observações (não bloqueiam)
- A medição dos 50 jobs usa 3 agentes com jobs; o front completa o catálogo localmente (agente ausente = ocioso), sem custo no servidor. **Rodrygo** ainda pode acrescentar em `testar_ao_vivo.py` o caso "agente do catálogo ausente = ocioso" (o e2e já cobre pelo lado da tela).
- O quinto estado "Espera você" aparece no Catálogo; **Zico** confirma no aceite.
- Endrick registrou que escreveu código e teste na mesma rodada; **Thiago Silva** deve conferir na revisão que as asserções não são frouxas.
