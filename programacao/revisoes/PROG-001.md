# Revisão PROG-001 · "Não se aplica" sem motivo (Thiago Silva, 2026-11-04)

**Veredito: APROVADO.**

Método: leitura do código atual (sem shell nesta sessão, então sem `git diff`).

## O que li
- `estudio/fluxo.py` 275-290 (`motivo_nao_aplica`).
- `estudio/web/app.js` 343 e 355 (exibição do motivo).
- `estudio/testes/e2e_celular.mjs` 144-153; `e2e_interface.mjs` 304-308; `testar_prog001_002.py` 46-79.

## Pontos aprovados
- Todos os ramos que podem devolver `nao_aplica` têm texto próprio e fecham com "Para aplicar: ...". O ramo genérico ("Ela não faz parte do fluxo...") continua legível.
- O motivo vem da mesma regra de `aplicavel` (o texto não inventa regra). Etapa aplicável devolve `None` (testado: critério 6).
- A regex do celular (linha 152) foi apertada, não afrouxada: exige o motivo, "Para aplicar" e "sem --mock". O conteúdo bate com o texto da linha 282.
- Os testes cobrem os 4 estilos e a origem de fora do estúdio.

## Ressalvas (não bloqueiam)
- "Para aplicar" só é afirmado no celular e só no ramo `componentes`/`--mock`. Os ramos `auditoria` e `narracao` são cobertos apenas pelo texto da API (`startswith("Produção simulada")`), não pela tela. Aceitável, pois a tela exibe `motivo_nao_aplica` sem transformação (app.js 343/355).
- A entrega lista `app.js` como alterado, mas o texto novo está em `fluxo.py`. Corrigir a lista de arquivos na entrega (documental).
