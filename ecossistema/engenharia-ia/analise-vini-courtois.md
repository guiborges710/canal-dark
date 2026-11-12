# Análise de Vini e Courtois (2026-11-03)

Fontes: `.claude/agents/vini-auditor-conformidade.md` (2.093 B), `.claude/agents/courtois-revisor-fatos.md` (1.329 B), `compliance.py` (12.123 B), `media/roteiro.py`, e as saídas reais em `output/*/` (`revisao.md`, `auditoria_texto.md`, `auditoria.md`). As definições são curtas; os "muitos filtros" estão na **prática**: o **Vini** escreve 17 itens no TEXTO e 12 por passe no FINAL, e o **Courtois** 18. A maior parte repete verificação que já existe em outro lugar.

Nada aqui corta política do YouTube, monetização, tom com vítimas, regra de 3+ fontes, congelamento do roteiro ou ação externa. Onde o filtro toca nessas regras, a proposta é **mover o dono**, não apagar a checagem.

## A. O que o código já cobre (`compliance.py` e `media/`)

| Verificação | Onde | Observação |
|---|---|---|
| 3+ domínios distintos em `notas.md` | `compliance.py` seção 1 | Conta domínios, não qualidade da fonte |
| Ângulo existe e tem 60+ palavras | seção 2 | |
| Texto copiado das notas (shingles de 7 palavras, limite 12%) | seção 3 | |
| Abertura e fecho repetidos entre vídeos (Jaccard das 25 primeiras/últimas palavras) | seção 4 | Mesmo cálculo que **Vini** faz lendo todos os roteiros |
| Cadência por 24 h | seção 4 | |
| `cenas.json` válido, narração completa | seção 5 | |
| Números (máx. 2) e gráficos (máx. 1) | `media/roteiro.py` via `avisos_de_roteiro` | |
| Sem imagem de terceiros/IA, sons por código | seção 5 e 7 | **Tautologia**: sempre devolve OK |
| Aviso de voz sintética | seção 5 | |
| Título: tamanho, CAIXA ALTA, lista `CLICKBAIT` | seção 6 | |
| Termos sensíveis em título/miniatura | seção 6 (`SENSITIVE`) | |
| Aviso de animação por computador na descrição, "Fontes:" | seção 6 | |
| Formato 1080x1920/30 fps, duração 30-60 s | `media/sketch.py`, `limites()` e o encode | Validado no render; o **Vini** refaz com `ffprobe` |

Lacuna real do código: **não há** checagem de "pelo menos 1/3 de comentário próprio", nem de fato contra nota (isso é julgamento, e é o trabalho do **Courtois**).

## B. Courtois: filtro a filtro

| # | Filtro (definição + prática) | O que pega de verdade | Coberto por | Veredito | Proposta | Risco real |
|---|---|---|---|---|---|---|
| C1 | Remover/reescrever o que não tem apoio nas notas | Sim. No vídeo `jovens-bebendo-menos`: 7 correções reais (faixa "18 a 34" sem 3 fontes, "liga" causal, "mudou mais do que sumiu") | Nada | **MANTER (núcleo)** | Dono único de fato contra nota. Escrever só as exceções | Cortar = fato errado no ar |
| C2 | Apontar exageros e número sem fonte | Mesmo item de C1, pela outra face | C1 | **FUNDIR em C1** | Uma linha: "afirmação sem apoio, exagerada ou com número sem fonte" | Nenhum |
| C3 | Apontar trechos copiados das fontes | Pouco: o roteiro é paráfrase e o `compliance.py` mede 7-gramas | `compliance.py` seção 3 | **CORTAR** | Remover do **Courtois**; vale o aviso do `check` | Baixo: se o `check` avisar, o **Courtois** só reescreve a frase marcada (antes do congelamento) |
| C4 | Marcar frases difíceis de ler na tela | Pouco: o canal sketch não tem legenda; o que sobra é pronúncia na voz sintética e números por extenso | Olise/voz e prévia | **CORTAR, deixar só risco de pronúncia** | "Só se uma palavra puder ser lida errado pela voz (ex.: 'Gen Z'), sugerir a forma falada" | Baixo (dá para ouvir antes de publicar; áudio é congelado depois do render) |
| C5 | Gancho não promete mais do que o vídeo entrega | Sim, pega: "a queda não é só dela" e `Gancho: OK` em quase todo vídeo | **Neymar** (regra b/c do canal) e **Vini** (título) | **MANTER em um só lugar: Courtois** | Retirar do **Vini** o item de gancho; **Vini** olha só título/miniatura contra o `roteiro.txt` | Baixo se **Courtois** tiver a linha; monetização/clickbait é regra do dono (2026-10-27), então a checagem fica, só muda o dono |
| C6 | 1/3 de comentário próprio | Sim, e é a proteção contra "conteúdo inautêntico". Calibra 33-38% em vários vídeos | Nada no código | **MANTER** | Pedir ao **Neymar** a contagem em `roteiro_notas.md`; **Courtois** só confere se estiver abaixo de 40% (não reconta todo vídeo) | Cortar = risco de política de conteúdo inautêntico. **Não cortar** |
| C7 | Máx. 2 números, nenhum na abertura (regra de `tipos_de_roteiro.md`) | Pega, mas `media/roteiro.py` conta de forma determinística | `media/roteiro.py` | **MOVER para código** | Dar `Bash` ao **Courtois** para rodar a contagem (uma linha), e remover a leitura de `tipos_de_roteiro.md` (4,5 KB) da etapa dele | Baixo; a contagem por texto "pode errar por um ou dois" (palavras do próprio módulo) |
| C8 | Sobrescrever `roteiro.txt` inteiro | Funciona, é curto (<1 KB) | — | **MANTER** | Nada a poupar em bytes | — |
| C9 (prática) | Tabela de 18 itens, 11 deles "OK" | Os "OK" não mudam nenhuma decisão | — | **ENXUGAR** | `revisao.md` só com exceções + 3 linhas fixas (veredito, fontes, % próprio) | Nenhum: "OK" some, o que importa continua |
| C10 (prática) | Alinhar `roteiro.txt` x `## Narração` x `cenas.json` palavra por palavra | É consistência mecânica | Dá para código | **MOVER para código** | Ver P3 em `propostas-reformulacao.md` | Baixo |

Leitura do `Courtois` hoje: `roteiro.txt` + `notas.md` (10 KB, até 37 KB) + `tipos_de_roteiro.md` (4,5 KB) + às vezes `angulo.md` e `direcao_viral.md`. Depois do corte: `roteiro.txt` + `notas.md` + `roteiro_notas.md`.

## C. Vini TEXTO: item a item (17 itens do vídeo `jovens-bebendo-menos`)

| # | Item | Quem já cobre | Veredito | Proposta | Risco real |
|---|---|---|---|---|---|
| V1 | Números/ano/fonte contra `notas.md` (itens 1, 2, 3, 5, 6, 11) | **Courtois** (itens 1 a 11 da `revisao.md` tratam as mesmas frases) | **CORTAR (duplicado)** | **Vini** confia na `revisao.md`; não relê `notas.md` | Fato errado passa. Mitigação: **Courtois** marca "NÃO verificado na origem" (já faz) e o **Vini** lê só essa seção. Regra de fonte 3+ continua no `compliance.py` |
| V2 | Ressalvas de fonte secundária e conflito entre fontes (item 8, 7) | **Courtois** + **Modric** (lacunas em `notas.md`) | **CORTAR** (virou recomendação, nunca infração) | Ficar em `revisao.md` | Baixo |
| V3 | Texto próprio ≥ 1/3 (item 9) | **Courtois** (C6) | **CORTAR do Vini** | O **Vini** só confirma a linha da `revisao.md` | Mesmo risco de C6, só muda de dono |
| V4 | Gancho entrega (item 10) | **Courtois** (C5) | **CORTAR do Vini** | **Vini** só compara título/miniatura | Baixo |
| V5 | Saúde/tom/sensível (item 13) | `compliance.py` `SENSITIVE` + **Courtois** (tom) | **MANTER curto**: é o único julgamento de política de verdade | Uma pergunta: "há algo aqui que limite anúncio ou ofenda vítimas?" | Cortar = monetização/tom com vítimas. **Não cortar** |
| V6 | Originalidade, abertura/fecho vs outros roteiros (item 12) | `compliance.py` seção 4 (Jaccard) | **CORTAR leitura** de todos os outros `roteiro.txt` | Ler só o aviso do `check` | Baixo; nunca foi bloqueio |
| V7 | Conformidade YouTube: inautêntico/repetitivo/reutilizado (item 15) | Parte no `compliance.py` (ângulo, cópia, repetição) | **MANTER curto** | Uma linha de risco, sem tabela | Política de conteúdo inautêntico. **Não cortar a decisão**, só o texto |
| V8 | Descrição: aviso de animação, "Fontes:", tags (item 14) | `compliance.py` seção 6 | **CORTAR** | Ler `CONFORMIDADE.md` | Nenhum |
| V9 | Rótulos do `cenas.json` x `previa.jpg` (item 16) | **Olise** (confere a prévia) e `validate()` | **CORTAR** | — | Texto errado na tela: já foi checado contra `roteiro.txt` por **Courtois**; baixo |
| V10 | Duração e pronúncia (item 17) | `media/sketch.py` (limites) | **CORTAR** | — | Nenhum: nem é de texto |
| V11 | `sketch_cenas.py` e `previa.jpg` lidos | Nada precisa deles no modo TEXTO | **CORTAR** (5 a 14 KB + imagem) | **Vini** TEXTO lê só texto | Baixo |
| V12 | Descrição: lembrete "marcar conteúdo sintético no Studio" | Repete em toda auditoria | **MOVER** para `PUBLICAR.txt`/checklist de **Memphis** (uma vez) | — | Perder o lembrete = falha de divulgação. Deve ficar no checklist de upload, não sumir |

Resumo do **Vini** TEXTO: de 17 itens, 3 são julgamento próprio (V5, V7, título/miniatura). O resto é conferência de algo que o **Courtois** ou o código já fez.

## D. Vini FINAL: item a item (12 itens do vídeo, mais passes de v2 e v3)

A regra do Guilherme (2026-11-03) já limita o FINAL: depois do render só `titulo`, `descricao`, `tags` e miniatura podem bloquear. Todo o resto é "observação" que não muda nada. Então boa parte do FINAL é custo sem decisão.

| # | Item | Veredito | Proposta | Risco |
|---|---|---|---|---|
| F1 | Formato, duração, áudio (ffprobe, pico, silêncio) | **MOVER para código** | Já existe encode e `limites()`; acrescentar leitura do `ffprobe` ao `check` (item para **Rodrygo**/**Thiago Silva**) | Nenhum |
| F2 | Quadros cortados/sobrepostos (contato, prévia, 8 quadros extras) | **CORTAR ou reduzir a 1 imagem** | Observação opcional, um só `contato.jpg`; não bloqueia, não muda nada | A regra do dono diz que audiovisual é observação. Cortar = perder um aviso que ninguém pode agir (congelado) |
| F3 | Sem legenda na base, sem imagem de IA/terceiros | **CORTAR** | Tautologia (`compliance.py` sempre OK) | Nenhum |
| F4 | Rótulos x `cenas.json`, números nas barras x notas | **CORTAR** | Já passou por **Courtois**; no FINAL nada pode mudar | Nenhum |
| F5 | Narração: ritmo, palavras por segundo | **CORTAR** | Observação sem ação possível | Nenhum |
| F6 | Conteúdo sensível na imagem | **MANTER 1 linha** | Parte do V5, uma vez só | Cortar = monetização. **Não cortar** |
| F7 | Título/descrição/tags/miniatura vs conteúdo (**o único poder de bloqueio**) | **MANTER** | É o FINAL real: ler `metadados.json`, `thumbnail.jpg` e o `CONFORMIDADE.md` | Cortar = título enganoso ou isca |
| F8 | Re-auditorias v2 e v3 inteiras (31 itens no total) | **CORTAR** | Só re-auditar se `metadados.json` ou a miniatura mudaram; em nova versão de vídeo (autorizada pelo Guilherme) auditar só o diff | Nenhum |
| F9 | Engagement bait ("Comenta aqui", enquete) | **MANTER no TEXTO/METADADOS** | É texto/descrição/comentário fixado, entra em metadados | Política de spam/isca. **Não cortar** |

Resumo do **Vini** FINAL: de 12 itens, 2 a 3 têm poder de decisão. Lembrando: nesta análise eu **não** cortei nada do que a regra do Guilherme já protege.

## E. Recomendação direta

1. **Courtois = dono único de fato, gancho e % de comentário próprio.** Saída curta (só exceções).
2. **Vini TEXTO = 5 perguntas** (política de conteúdo inautêntico, sensível/tom com vítimas, título e miniatura contra o roteiro, engagement bait, o que o `CONFORMIDADE.md` marcou). Lê: `CONFORMIDADE.md`, `revisao.md`, `roteiro.txt`, `metadados.json`, tese do `angulo.md`. Não lê `notas.md`, `sketch_cenas.py` nem outros roteiros.
3. **Vini FINAL = metadados e miniatura**, com leitura de 1 imagem. Verificações de ffprobe saem para o código.
4. **Re-auditoria só se metadados mudarem.**

Estimativa de economia (tokens, **estimado**): **Vini** TEXTO cai de ~16 mil de entrada (inclui `CLAUDE.md`) para ~8 mil, e a saída de ~7 KB para ~1 KB. **Vini** FINAL cai de 3-10 KB de saída e várias imagens por passe para ~1 KB e 1 imagem. Em um vídeo com 3 passes FINAL (como `jovens-bebendo-menos`) a redução é de aproximadamente 70 a 80% do que o **Vini** consome naquele vídeo. Esses percentuais são cálculo por tamanho de arquivo, não medida de uso real.

## F. Dúvidas que dependem do Guilherme
- Se ele quiser que o modo FINAL deixe de existir como agente (virar só `run.py check` mais um `ffprobe`), a única coisa perdida é o parecer humano-like sobre título/miniatura; hoje isso cabe no TEXTO se `thumbnail_texto` já existe nos metadados. Decisão do dono.
- Hoje `run.py publish` exige `auditoria.md` APROVADA. Qualquer mudança no formato (por exemplo, uma linha `APROVADO` gerada no fim do TEXTO) precisa que **Thiago Silva**/**Rodrygo** ajustem o gate.
