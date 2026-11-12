# QA PROG-014 · Curador de referências (Xabi Alonso) · por Alisson, 2026-11-05

**Veredito: APROVADO** (com ressalvas abaixo).

Evidência: `testar_aprendiz.py` → **50/50** (inclui curador: sucesso, não sobrescrever, falha legível, limites escritos). Entregas lidas: `inteligencia/referencias_estudo/2026-11-05.md` e `2026-11-05-2.md`; `inteligencia/aprendiz/fila.md` (8 itens); `historico.jsonl`.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Agente com limites (só pesquisa; sem baixar em massa) | PASSOU | `xabi-alonso-curador-referencias.md` tools: Read, Write, Glob, Grep, WebSearch, WebFetch (sem Bash); teste de limites ok |
| 2 | Lista datada em duas partes | PASSOU | as 2 entregas têm "Nicho aberto" e "Nosso nicho" |
| 3 | Link do vídeo e do canal, nicho, formato, por que serve, o que aprender | PASSOU | 3 + 5 referências, todos os campos presentes |
| 4 | Declara a fonte; só dark | PASSOU, com ressalva | cada item cita Memphis/Hugo; formato dark vem das fichas, voz "não verificada", e itens duvidosos foram para "Fora da lista" |
| 5 | Curta, priorizada, sem repetir estudado | PASSOU | ≤5 por entrega, numeradas; entrega 2 não repete as 3 do Memphis; `estudados.md` só tem o vídeo próprio |
| 6 | Fila legível pelo aprendiz | PASSOU | `fila.md` com 8 linhas (ordem, id, link, canal, nicho, aprender, fonte); `rodar.py` leu 3 delas na rodada-1 |
| 7 | Roda quando chamado, teto US$0,20, registro | PASSOU | `TETOS["curador"]=0.20`; `historico.jsonl`: 0,1557 e 0,1899; teste de teto ok |
| 8 | Só links e metadados públicos | PASSOU | sem baixar nem raspar; sem download no código |
| 9 | Sem resultado útil: texto claro, sem inventar | PASSOU | entrega 1 "Nicho aberto: nenhuma referência" com motivo; entrega 2 "nosso nicho" idem |
| 10 | Alisson confere entrega real contra 2–6 | PASSOU | tabela acima |

## Ressalvas (não bloqueiam)
- Nenhum link foi aberto para confirmar que está no ar (declarado na entrega).
- O formato dark e a voz não foram vistos; a primeira rodada do aprendiz poderá desmentir.
- Fila tem vídeos longos (até 19 min), que o Busquets só analisa por cortes e 10 min de fala.
- Autoria pelo Claude Code, por pedido do Guilherme.

Nenhum bug novo.
