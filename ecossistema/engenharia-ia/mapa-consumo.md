# Mapa de consumo (2026-11-03)

Método: tamanhos em bytes medidos com `wc -c` em `.claude/agents/`, `CLAUDE.md`, `prompts/`, `output/*/` (28 pastas de vídeo, 25 com `video.mp4`). Tokens = bytes / 3,8 (**estimativa**). Não medi o uso real de tokens por chamada (o Claude Code não grava isso em `custo.json`). "Leituras" são o que a definição de cada agente manda ler, mais o que as auditorias existentes mostram que foi lido.

## 1. Custo fixo por chamada (vale para todo agente)

| Item | Bytes | Tokens est. | Observação |
|---|---|---|---|
| `CLAUDE.md` | 18.952 | ~5.000 | Estimativa: subagentes do projeto carregam o `CLAUDE.md`. **Confirmar** (não medi). Se for verdade, é o maior custo fixo do ecossistema. |
| Seção "Arquitetura do código" | 4.330 | ~1.100 | Só serve a quem programa. Vai para Modric, Neymar, Ronaldo, Pedri, Casemiro etc. sem uso. |
| Seção "Fluxo" | 3.535 | ~930 | Duplica `debruyne-orquestrador.md` (9.444 B). |
| Seção "Comandos" | 1.950 | ~510 | Só serve a dev e ao Debruyne. |
| `ecossistema/README.md` | 15.057 | ~3.960 | Lido por ~15 agentes (setor de programação e pessoal), em toda chamada. |
| `programacao/README.md` | 6.661 | ~1.750 | Todo agente de programação. |
| `programacao/backlog.md` | 33.963 (339 linhas) | ~8.900 | Zico, Alisson e Iniesta leem; só um item interessa a cada vez. |
| `estudio/README.md` | 16.090 | ~4.200 | Thiago Silva, Rodrygo, Iniesta, Marquinhos. |

## 2. Definições dos agentes (tamanho do prompt)

| Agente | Modelo | Bytes | Tokens est. |
|---|---|---|---|
| **De Bruyne** | sonnet | 9.444 | ~2.500 |
| **Dembélé** (Reels, fora do fluxo) | sonnet | 7.912 | ~2.100 |
| **Raphinha** | opus (effort high) | 6.958 | ~1.800 |
| **Ronaldo** | sonnet | 6.155 | ~1.600 |
| **Sidorf** | sonnet | 5.959 | ~1.600 |
| **Olise** | opus (effort high) | 5.822 | ~1.500 |
| **Memphis** | sonnet | 5.638 | ~1.500 |
| **Barcola** (horizontal, fora do fluxo) | opus | 4.712 | ~1.250 |
| **Casemiro** | sonnet | 4.387 | ~1.150 |
| **Cristiano** | sonnet | 4.307 | ~1.130 |
| **Guardiola** | sonnet | 3.827 | ~1.000 |
| **Kroos** | sonnet | 3.230 | ~850 |
| **Yuri Alberto**, **Pedri**, **Rodri**, **Lamine Yamal**, **Hugo Souza** | sonnet | 2.400 a 2.800 | ~650 a 740 |
| **Vini** | sonnet | 2.093 | ~550 |
| **Neymar** | sonnet | 1.971 | ~520 |
| **Courtois** | sonnet | 1.329 | ~350 |
| **Mbappé** | haiku | 1.139 | ~300 |
| **Modric**, **Messi**, **Haaland** | sonnet/sonnet/haiku | 676 a 804 | ~180 a 210 |
| Demais (programação e inteligência) | sonnet | 1.360 a 2.350 | ~360 a 620 |

Observação: as definições de **Vini** e **Courtois** são pequenas. O peso deles não está no prompt, está no que leem e no que escrevem (seção 4).

## 3. Fluxo diário de um Short: o que cada etapa lê

Tamanhos típicos medidos nas pastas existentes: `notas.md` mediana ~10 KB (mínimo 3,7 KB, máximo 37 KB em `cnh-aos-16-anos` e 23,6 KB em `jovens-bebendo-menos`); `angulo.md` 3 a 7 KB; `roteiro.txt` 0,5 a 0,9 KB; `direcao_viral.md` 3 a 4,5 KB; `cenas.json` 2 a 5 KB; `metadados.json` 1,6 a 2,5 KB; `revisao.md` 4,5 a 5,4 KB; `sketch_cenas.py` 5 a 14 KB.

| Etapa | Modelo | Lê (além do `CLAUDE.md`) | Escreve | Pesos |
|---|---|---|---|---|
| **Memphis** (semanal) | sonnet | WebSearch/WebFetch (volume não medido) | `referencias_virais.md` 4,2 KB | Busca web domina |
| **Modric** | sonnet | WebSearch/WebFetch, 3+ fontes | `notas.md` ~10 KB (até 37 KB) | **Gera o arquivo que todos releem** |
| **Neymar** | sonnet | `notas.md`, `angulo.md`, `messi_assinatura_canal.md` 4,8 KB, `prompts/writer.md` 1,6 KB, `tipos_de_roteiro.md` 4,5 KB, `referencias_virais.md` 4,2 KB, outros `roteiro.txt` | `angulo.md`, `roteiro.txt`, `direcao_viral.md`, `roteiro_notas.md` | ~10 KB notas + ~16 KB de contexto fixo |
| **Courtois** | sonnet | `roteiro.txt`, `notas.md`, `tipos_de_roteiro.md` (4,5 KB), por vezes `direcao_viral.md`, `angulo.md` | `roteiro.txt` reescrito, `revisao.md` 4,5 a 5,4 KB | `notas.md` de novo |
| **Raphinha** | **opus high** | `aprendizados.md` 3,7 KB, `catalogo.md` 4,9 KB, roteiro, `direcao_viral.md`, `media/estilos.py` 13 KB, `sketch_lib.py` 20 KB, skill 8 KB | `componentes.md`, imagens, `componentes_video.py` | Maior leitura de código do fluxo, em opus |
| **Olise** | **opus high** | `direcao_viral.md`, `roteiro.txt`, `componentes.md`, `aprendizados.md`, skill sketch 8 KB (+ skill camadas 6 KB), `sketch_lib.py` 20 KB; até 3 rodadas de `previa.jpg` (imagem) | `cenas.json`, `sketch_cenas.py` 5 a 14 KB | Leitura de ~28 KB de biblioteca/skill repetida em todo vídeo, mais imagens |
| **Mbappé** | haiku | `roteiro.txt`, `angulo.md`, metadados anteriores | `metadados.json` | Barato, adequado |
| **Vini, TEXTO** | sonnet | `notas.md`, `angulo.md`, `roteiro.txt`, `metadados.json`, `cenas.json`, `revisao.md`, `previa.jpg`, `sketch_cenas.py`, roteiros de todos os outros vídeos (abertura/fecho), `CONFORMIDADE.md` via `run.py check` | `auditoria_texto.md` 3,9 a 7,2 KB (17 itens no exemplo) | ~35 KB de leitura (~9 mil tokens) + saída |
| Render | nenhum (código) | — | — | Custo zero de tokens |
| **Vini, FINAL** | sonnet | `video.mp4` (quadros), `contato.jpg`, `previa.jpg`, `thumbnail.jpg`, `ffprobe`, `CONFORMIDADE.md`, descrição | `auditoria.md` 3,9 a 10 KB | Imagens, e só pode bloquear por metadados |
| **Sidorf** | sonnet | `identidade_visual.yaml` 4,2 KB, `metadados.json`, `roteiro.txt`, `cenas.json`, `angulo.md` | relatório da thumbnail | Roda depois de tudo, sem bloquear |
| **De Bruyne** | sonnet | Os handoffs: cada briefing repete caminhos e instruções; confere arquivos com Glob/Read | Updates | A definição (~2.500 tokens) é carregada a cada turno do orquestrador |

Releituras medidas no fluxo (arquivo, quantas vezes é aberto por vídeo):
- `notas.md`: **4 a 5** (Neymar, Courtois, Vini TEXTO, mais Cristiano/Messi quando chamados). Com 10 KB, ~11 mil tokens de releitura; com 37 KB, ~38 mil.
- `roteiro.txt`: 7 ou mais, mas é pequeno (<1 KB), não pesa.
- `direcao_viral.md` (`## Narração`): a fala existe em **três cópias** (`roteiro.txt`, `direcao_viral.md`, `cenas.json` campo `fala`) e **Courtois**, **Olise** e **Vini** conferem uma contra a outra.
- `prompts/tipos_de_roteiro.md` (4,5 KB): Neymar e Courtois.

## 4. Vini e Courtois em números (de uma pasta real, `jovens-bebendo-menos`)

| Documento | Itens | Bytes | Observação |
|---|---|---|---|
| `revisao.md` (Courtois) | 18 | 4.502 | 7 itens "Corrigido", 11 "OK" |
| `auditoria_texto.md` (Vini TEXTO) | 17 | 7.223 | 2 ações recomendadas, 13 "OK", 1 informativo |
| `auditoria.md` (Vini FINAL) | 31 (3 passes: v1, v2, v3) | 10.036 | Só 1 item relevante para decisão; o resto "OK" |

Nesse vídeo o **Vini** rodou **4 vezes** (1 TEXTO + 3 FINAL). Nos 28 vídeos: 10 `auditoria_texto.md`, 21 `auditoria.md`. Bloqueios reais no TEXTO: `geracao-z-a-mais-solitaria` (3 na rodada 1), `companhias-de-ia` (editorial e fidelidade às fontes, o próprio parecer diz "não identifiquei infração explícita das políticas do YouTube"), `divisao-politica` e `cnh` (seção "Infrações" existente). Os que tenho como confirmados eram de **fidelidade de fato**, trabalho do **Courtois**. Ver `analise-vini-courtois.md`.

## 5. Setores fora do canal (peso por chamada, estimativa)

| Setor | Padrão de leitura | Peso fixo/chamada | Ponto de atenção |
|---|---|---|---|
| Inteligência (**Hugo Souza**, **Fagner**, **André Carrillo**, **Raniele**, **Yuri Alberto**, **Vitinho**) | `inteligencia/README.md` 5,3 KB + `canais/_indice.md` + fichas (17 fichas) | ~1.400 tokens + fichas | **Vitinho** lê todas as pastas do ciclo; `inteligencia/fontes.md` tem 24 KB. Hugo, Memphis e André/Raniele usam WebSearch/WebFetch. Fagner, André e Raniele leem as mesmas fichas, três vezes. |
| Programação (**Xavi**, **Zico**, **Thiago Silva**, **Rodrygo**, **Endrick**, **Alisson**, **Iniesta**, **Marquinhos**, **Ancelotti**) | `ecossistema/README.md` 15 KB (alguns), `programacao/README.md` 6,7 KB, `estudio/README.md` 16 KB, `backlog.md` 34 KB | 3 a 17 mil tokens só de contexto | **Backlog de 34 KB** é lido inteiro para achar um item. `melhoria.md` (8 KB) é só do **Ancelotti**. |
| Pessoal (**Ronaldo**, **Pedri**, **Guardiola**, **Rodri**, **Kroos**, **Casemiro**, **Lamine Yamal**) | `ecossistema/README.md` 15 KB + `produtividade/README.md` 5 KB, mais os arquivos do dia (`tarefas.md`, `agenda.json`, `lembretes.json`, `kanban.md` 5,2 KB) | ~5.300 tokens fixos, mais ~3 mil dos arquivos | **Ronaldo** responde a mensagens do Telegram, então roda muitas vezes por dia: o custo fixo se multiplica. Sync do Trello a cada 10 min é código, sem token. |

## 6. Limites desta medição
- Não tenho log de tokens reais por chamada. Tudo em tokens é estimativa por tamanho de arquivo.
- Não medi o volume de WebSearch/WebFetch de **Modric**, **Memphis** e **Hugo Souza**.
- Não confirmei se o `CLAUDE.md` e o `ecossistema/README.md` entram em cada subagente. Se `CLAUDE.md` não entrar, a economia da proposta P6 cai a zero para esse item, mas as demais não mudam.
