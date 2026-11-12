# Revisão PROG-016 · Catálogo com estado por agente (Thiago Silva, 2026-11-09)

**Veredito: APROVADO.**

Código revisado: `estudio/web/corte_agentes.js` (`estadoDe` 228-244, `marcarEstados` 246-267, `desenharLista` 268-283, erro em `carregar` 211-214, ouvinte do `Vivo` 182), `corte_nav.js:60` (`ocioso`, `verificando`), `corte.css`/`celular.css`. Servidor e `ao_vivo.py` intocados, como a nota técnica pedia.

## O que conferi
- **Mesma fonte da aba Ao vivo** (critério 4): `estadoDe` lê só `Vivo.dados.agentes`; ausente = ocioso. Sem segundo cálculo, sem rota nova, sem polling novo (critério 5).
- **Sem apagar digitação/edição**: o ouvinte chama `marcarEstados()`, que troca só selo, linha de detalhe e rodapé no lugar; `desenharLista` não roda por polling. Selo só é trocado se a chave mudou.
- **Antes da primeira resposta** mostra "Verificando", nunca "Ocioso" (risco 5). Erro de consulta mantém selos e avisa "(desatualizado)" (risco 2). Desativado + estado convivem (risco 3).
- Ocioso: detalhe vazio e `hidden` (critérios 2 e 3). Texto sempre junto do ícone, ícone `aria-hidden` (critério 1).
- **Asserções do e2e não são frouxas** (a dúvida que o **Alisson** deixou): comparam texto exato do rodapé, `aria-label` completo, "+2", ausência de `Falhou|há N|undefined|null|NaN`, marca no DOM provando que a lista não foi refeita, contagem de pedidos no ciclo, geometria em 390 px (rolagem, uma coluna, ≥ 44 px, selo dentro da tela).

## Evidência (rodada por mim agora, uma por vez)
- `E2E_PORTA=8803 node estudio/testes/e2e_agentes_catalogo.mjs` → **47 ok, 0 falhas**.
- `python estudio/testes/testar_ao_vivo.py` → **49 ok, 0 falhas**; 50 jobs + 30 produções: rota em 40 ms (limite 200 ms; critério 7 pede < 1 s).
- Regressões (`e2e_agentes_ao_vivo` 91, `e2e_celular` 64, `e2e_interface` 150, todas 0 falhas) vêm do QA do **Alisson** (`qa/PROG-016.md`), não as repeti.

## Ressalvas (não bloqueiam)
1. `testar_ao_vivo.py` ainda não tem o caso "agente do catálogo ausente de `agentes` = ocioso" (pedido ao **Rodrygo** na nota técnica). O e2e cobre pelo lado da tela, então o contrato está fixado; fica como dívida pequena.
2. O quinto estado "Espera você" aparece no Catálogo: **Zico** confirma no aceite.
3. A medição dos 50 jobs usa 3 agentes com jobs; o complemento "ausente = ocioso" é feito no navegador, sem custo no servidor.
