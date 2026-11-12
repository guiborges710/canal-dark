# Casos de teste · PROG-012 · Status automático de cada vídeo
Autora: **Alisson**. Escritos a partir dos critérios de `backlog.md`; ainda sem código (item no Backlog da sprint). Todos em pasta temporária (nada de `output/` real), critério 8. A regra única de derivação sai de `tecnico/decisoes.md` (**Thiago Silva**); a precedência abaixo é a que o teste vai exigir, a confirmar.

Entrada: pasta temp com combinações de `roteiro.txt`, `video.mp4`, `auditoria.md`, `fila_postagem.txt`, `upload.json` (privacy private/public). Saída: um status por slug.

| Caso | Critério | Dado | Esperado |
|---|---|---|---|
| C1 | 1 | Pasta só com `notas.md` | "sem roteiro" |
| C2 | 1 | `roteiro.txt`, sem `video.mp4` | "em produção" |
| C3 | 1,2 | `roteiro.txt` + `video.mp4`, sem auditoria | "vídeo pronto" |
| C4 | 1,3 | + `auditoria.md` com APROVADO | "auditado" |
| C5 | 3 | `auditoria.md` com REPROVADO | "vídeo pronto" |
| C6 | 3 | `auditoria.md` vazio ou sem veredito | "vídeo pronto" |
| C7 | 1 | C4 + slug em `fila_postagem.txt` | "na fila de postagem" |
| C8 | 1,4 | `upload.json` com privacy=private | "publicado (privado)" |
| C9 | 4 | privacy=public sem confirmação de fonte nem marcação manual | continua "publicado (privado)" |
| C10 | 4 | privacy=public com marcação manual do Guilherme (formato definido por **Rodrygo**) | "público" |
| C11 | 5 | slug na fila sem `video.mp4` | aviso em português ("está na fila, mas não tem vídeo"); status não é "na fila de postagem" |
| C12 | 5 | `upload.json` sem `video.mp4`; fila com slug sem pasta | aviso, sem exceção |
| C13 | 5 | auditoria APROVADA, mas vídeo mais novo que a auditoria | aviso ou "vídeo pronto", conforme a regra de decisoes.md (a definir) |
| C14 | 2 | Criar `video.mp4`, depois `auditoria.md`, entre duas leituras | status muda sozinho, sem edição manual |
| C15 | 1 | Para todo slug, o status pertence ao conjunto dos 7 e é um só | propriedade verificada em C1 a C14 |
| C16 | 6 | Lista com vários vídeos | todos listados com status; "há vídeo pronto para a próxima postagem" = sim quando o 1º da fila está auditado, não caso contrário |
| C17 | 6 | Fila vazia | resposta "não" com texto, sem erro |
| C18 | 7 | Hash de `fila_postagem.txt`, `upload.json` e lista de arquivos antes e depois de gerar a visão | idênticos (nada publicado, movido ou editado) |
| C19 | 7 | Procurar na rota/ação da visão chamadas a `publish`, `postar_pendentes` ou escrita em `output/` | nenhuma (revisão de código, mais o hash do C18) |
| C20 | 8 | Suíte rodada com `ESTUDIO_RAIZ` temporário | `git status` de `output/` real igual antes e depois |

## Casos adicionados na revisão (fronteiras, erro, celular)
| Caso | Critério | Dado | Esperado |
|---|---|---|---|
| C21 | 1 | `roteiro.txt` vazio (0 bytes) | tratado como "sem roteiro" |
| C22 | 1 | `video.mp4` de 0 bytes | não conta como vídeo pronto; aviso |
| C23 | 3 | `auditoria.md` com "APROVADO" e "REPROVADO" no mesmo texto | não aprova (conservador); aviso |
| C24 | 3 | "aprovado" em minúsculas / "APROVADO COM RESSALVAS" | regra fixa definida em decisoes.md; teste da regra escolhida |
| C25 | 4 | `upload.json` JSON inválido ou sem `privacy` | aviso em português, sem exceção, status não sobe |
| C26 | 5 | Slug repetido ou com espaços em `fila_postagem.txt`, linhas em branco | sem duplicar, sem erro |
| C27 | 1 | Pasta com nome inexistente na fila, caracteres acentuados no slug | funciona no Windows (UTF-8) |
| C28 | 6 | Celular (`e2e_celular.mjs`): lista de vídeos com status | texto do status visível, sem rolagem horizontal. BLOQUEADO por tela (**Iniesta**/**Endrick**) |

## Status de execução (2026-11-03)
C1-C27: camada de dados, testáveis sem tela e sem render, mas NÃO escritos como código: BLOQUEADO pelo contrato/regra única de **Thiago Silva** (`tecnico/decisoes.md`; nome da função e precedência). C10: BLOQUEADO por definição do **Zico** (fonte da confirmação de público). C13 e C24: BLOQUEADOS pela regra a definir. C28: BLOQUEADO por tela. Regressão e e2e completo: não rodados.

Pendência para o **Zico**: o critério 4 exige definir a "fonte" da confirmação de público (registro de publicação ou marcação manual); sem isso C10 não é testável.
