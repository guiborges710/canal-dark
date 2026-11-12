# Casos de teste · PROG-011 · Cronograma de postagem
Autora: **Alisson**. Escritos a partir dos critérios de `backlog.md`; depende do PROG-012 e da regra de horários/cadência do Guilherme (impedimento aberto). Fixar "hoje" por parâmetro (relógio injetável) e usar pastas temporárias.

| Caso | Critério | Dado | Esperado |
|---|---|---|---|
| T1 | 1,9 | Fila com 3 slugs (A, B, C) e cadência definida | 3 linhas por data, com slug e título (de `metadados.json`), na ordem A, B, C |
| T2 | 1 | Reordenar a fila no arquivo | cronograma reflete a nova ordem |
| T3 | 1 | Slug sem `metadados.json` | mostra o slug e "sem título", sem erro |
| T4 | 2 | Mudar o dia de um item | persiste após recarregar e após reiniciar o servidor; `fila_postagem.txt` inalterado |
| T5 | 2 | Trocar a ordem de dois itens | persiste; confirmar com o **Zico** se a troca grava na fila (a planning disse "só sugere; nunca reordena sozinho") |
| T6 | 3 | Cada item | rótulo de status em texto (os 7 do PROG-012), não só cor; verificar texto no DOM |
| T7 | 4 | Próximo da fila auditado e com vídeo | indicador "Pronto para postar" |
| T8 | 4 | Próximo da fila sem auditoria | "Sem vídeo pronto para DD/MM", citando "falta auditoria APROVADA" |
| T9 | 4 | Próximo sem `video.mp4` | "Sem vídeo pronto para DD/MM", citando "falta o vídeo" |
| T10 | 5 | Hoje 01/12, postagem 02/12 sem vídeo pronto | alerta destacado |
| T11 | 5 | Fronteira de "menos de 2 dias": 1 dia, 2 dias, 3 dias, sem vídeo | 1 dia = alerta; 2 e 3 dias = sem alerta (confirmar a fronteira com o **Zico**) |
| T12 | 5 | Postagem em 1 dia com vídeo pronto | sem alerta |
| T13 | 6 | Ações do Kanban/cronograma | nenhuma publica nem muda privacidade; hash de `output/` e `upload.json` inalterado; `publish` continua recusando sem `auditoria.md` APROVADA |
| T14 | 7 | `e2e_celular.mjs` (viewport de celular, `--rede`) | cronograma legível, sem rolagem horizontal, indicador visível |
| T15 | 8 | Fila vazia | estado "Nenhum vídeo na fila", sem erro |
| T16 | 8 | Slug na fila sem pasta em `output/` | linha com aviso "vídeo não encontrado", sem exceção |
| T17 | 8 | Data prevista no passado | marcada como data passada em texto, sem erro nem alerta falso de "próxima" |
| T18 | 9 | Suíte inteira | cobre ao menos: fila com vários vídeos (T1), fila vazia (T15), vídeo sem auditoria (T8), alerta de prazo (T10 a T12) |

## Casos adicionados na revisão
| Caso | Critério | Dado | Esperado |
|---|---|---|---|
| T19 | 5 | Virada de mês/ano (hoje 31/12, postagem 01/01) | contagem de dias correta |
| T20 | 5 | Postagem hoje (0 dias) sem vídeo | alerta (mais urgente que T11) |
| T21 | 1 | Fila com 1 item e fila com 50 itens | sem erro, ordem preservada |
| T22 | 2 | Dois itens no mesmo dia | ambos listados, ordem estável |
| T23 | 3 | `metadados.json` inválido | "sem título", sem exceção |
| T24 | 7 | Celular: item com título longo | quebra de linha, sem rolagem horizontal |
| T25 | 6 | Chamada a `/api` sem token vindo de outro site | recusada como nas demais rotas |

## Status de execução (2026-11-03)
Todos BLOQUEADOS: nenhum testável agora. T1-T5, T7-T12, T15-T25 dependem de PROG-012 (status) e da regra de horários e cadência do Guilherme; T11 e T20 também da fronteira do **Zico**; T6, T14 e T24 da tela do **Iniesta**. T13 pode ser escrito logo que a ação exista. Nada executado.

Bloqueios para testar: regra de horários e cadência (Guilherme), PROG-012 pronto, tela do **Iniesta** (T6, T14).
