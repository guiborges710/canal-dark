# QA · PROG-012 · Status automático de cada vídeo
Autora: **Alisson** · 2026-11-05 · Veredito: **APROVADO** (com 1 divergência de critério para o **Zico** decidir)

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Um status em texto entre os 7 | PASSOU | `testar_status_video.py`: 45 ok (um caso por degrau); CLI real lista "Vídeo pronto", "Auditado", "Publicado (privado)" |
| 2 | Derivado dos arquivos, muda sozinho | PASSOU | teste de mudança entre duas leituras; CLI lê `output/` real |
| 3 | Auditado só com APROVADA | PASSOU | casos reprovada/vazia/ausente = vídeo pronto; real: "pair-programming-*" BLOQUEADA segue "Vídeo pronto" |
| 4 | Público só com confirmação | PASSOU | marcador manual `publico.json`; sem ele fica privado (quem cria o marcador segue pendente do Zico) |
| 5 | Contradição mostra aviso em português | PASSOU | real: "Está na fila de postagem, mas não tem auditoria APROVADA." |
| 6 | Visão lista tudo + "próxima postagem pronta" | PASSOU | rota `GET /api/videos/status` e CLI: "Próxima postagem pronta: não ..." (tela fica no PROG-011) |
| 7 | Nada publica/move/altera | PASSOU | testes de hash e data antes/depois, rota POST dá 404 |
| 8 | Teste com pastas temporárias | PASSOU | suíte usa pasta temporária; `output/` real só lido |
| 9 | Precedência | PASSOU | um teste por degrau |
| 10 | Contradições mínimas | PASSOU | fila sem vídeo, fila sem auditoria, publicado sem vídeo cobertos |
| 11 | "Sim" só se o PRIMEIRO da fila está pronto | **FALHOU (literal)** | Implementado conforme D-001: "sim" se ALGUM item da fila está pronto (o primeiro pronto, como `postar_pendentes` faz). Diverge do texto do backlog quando o 1º da fila está bloqueado e o 2º pronto. Não conto como comprovado: **Zico** deve ajustar o critério ao D-001 ou pedir mudança. |
| 12 | Pasta vazia = sem roteiro | PASSOU | caso C1/C21 |
| 13 | 100 pastas < 2 s, só leitura | PASSOU | 148-179 ms em 3 rodadas (limite interno 300 ms; 1ª rodada fria deu 513 ms, ainda < 2 s do backlog; teste interno é sensível a carga, sugiro limite 1 s) |

## Regressão
- `testar_status_video.py`: 45 ok (1ª rodada 44 ok/1 falha só no limite interno de 300 ms; 3 repetições 45/0).
- `testar_roteiro.py`: 29 ok, 0 falhas.
- `testar_estilos.py`: 103 ok, 0 falhas.
- `e2e_interface.mjs` (E2E_PORTA=8792): 150 ok, 0 falhas.

## Observações (não bloqueiam)
- Risco de reenvio: vídeo com `upload.json` sem `publicado.json` aparece como publicado, mas `postar_pendentes` o enviaria de novo (item para o Zico).
- `APROVADO`+`REPROVADO` juntos aprovam (regra igual ao `run.py publish`).
- C28 (celular) fica para o PROG-011.
