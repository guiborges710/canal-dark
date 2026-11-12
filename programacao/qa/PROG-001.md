# QA · PROG-001 · Etapa "não se aplica" sem motivo (RODRYGO + ALISSON, 2026-11-04)

Rodado: `node estudio/testes/e2e_interface.mjs` (133 ok, 0 falhas) + `node estudio/testes/e2e_celular.mjs` (63 ok, 0 falhas). Correções aplicadas em `fluxo.py` (motivo_nao_aplica) e `e2e_celular.mjs` (regex).

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Etapa "não se aplica" mostra o motivo na própria etapa | ✅ PASSOU | e2e_interface [10]: "a tela mostra o aviso e o motivo na própria etapa" (linha 14). |
| 2 | Motivo cita a regra real | ✅ PASSOU | Textos atualizados: "Produção simulada (--mock)", "Esta pasta veio de fora do estúdio", "formato antigo", "Nenhuma cena tem fala". |
| 3 | Diz o que fazer para a etapa se aplicar | ✅ PASSOU | e2e_interface [10]: "a tela explica o que fazer para a etapa passar a se aplicar" (linha 15). Textos em fluxo.py agora incluem "Para aplicar:" com ações concretas. |
| 4 | Vale no computador e no celular | ✅ PASSOU | e2e_interface 133 ok + e2e_celular 63 ok. Celular: "PROG-001: motivo e próximo passo aparecem no celular" + "nada passa da largura da tela". |
| 5 | Teste automatizado cobre o motivo | ✅ PASSOU | e2e_interface [10] + e2e_celular confere motivo visível. |
| 6 | Etapas aplicáveis não mostram aviso | ✅ PASSOU | e2e_interface [10]: "etapa aplicável não mostra o aviso de não se aplica" (linha 17). |

**Veredito: APROVADO pelo QA.** Todos os 6 critérios passaram. Rodrygo corrigiu critérios 3 e 4, Alisson validou. Pronto para **Thiago Silva** code review e aceite final do Guilherme.
