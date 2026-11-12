# O que está comendo token à toa (2026-11-03)

Ordem: economia estimada (alta, média, baixa) e viabilidade (fácil = só texto de agente; médio = pede script pequeno; difícil = muda contrato). Tokens são estimativa (bytes / 3,8).

| # | Desperdício | Evidência medida | Economia | Viabilidade | Proposta |
|---|---|---|---|---|---|
| 1 | **Vini FINAL relê e reaudita tudo, inclusive v2 e v3**; imagem, áudio e animação que, pela regra do dono, não podem mais bloquear nem mudar nada | `jovens-bebendo-menos/auditoria.md`: 10 KB, 31 itens, 3 passes. 21 `auditoria.md` no total | **Alta** | Fácil | P1 |
| 2 | **Vini TEXTO refaz o trabalho do Courtois** (fato x nota, 1/3 próprio, gancho) e relê `notas.md` (mediana 10 KB, máx. 37 KB), `sketch_cenas.py` (5 a 14 KB), `previa.jpg` e outros roteiros | `auditoria_texto.md`, itens 1-3, 5, 6, 9, 10, 11 espelham `revisao.md` | **Alta** | Fácil | P2 |
| 3 | **`notas.md` inchado** e lido 4 a 5 vezes por vídeo. O **Modric** escreve 23 a 37 KB em alguns temas | `cnh-aos-16-anos/notas.md` 37 KB; `jovens-bebendo-menos` 23,6 KB; mediana ~10 KB | **Alta** | Fácil | P4 |
| 4 | **`CLAUDE.md` (19 KB) carregado em cada chamada**, com 4,3 KB de "Arquitetura do código" e 1,9 KB de "Comandos" que só o dev usa, e o Fluxo duplicado no **De Bruyne** | seções medidas com `awk` | **Alta** (se o `CLAUDE.md` entra em todo subagente: **a confirmar**) | Médio (arquivo do dono) | P6 |
| 5 | **Backlog de 34 KB lido inteiro** para tratar um item; `ecossistema/README.md` (15 KB) lido por ~12 agentes de programação e pessoais | `programacao/backlog.md` 339 linhas; README 15.057 B | **Alta** | Médio | P7 |
| 6 | **Três cópias da fala** (`roteiro.txt`, `direcao_viral.md` `## Narração`, `cenas.json` `fala`), conferidas por **Courtois**, **Olise** e **Vini** | `revisao.md`: "alinhados palavra por palavra" | Média | Médio (script) | P3 |
| 7 | **Olise e Raphinha em opus com effort high**, relendo ~28 KB de biblioteca/skill (`sketch_lib.py` 20 KB, skill 8 KB, `estilos.py` 13 KB) a cada vídeo | Definições dos dois | Média (preço por token do opus é maior; **não medi** o preço aplicado) | Médio | P8 |
| 8 | **Revisão e auditorias escritas em tabela com 70% de "OK"** | 11 de 18 itens "OK" no Courtois, 13 de 17 no Vini TEXTO | Média | Fácil | P1, P2 |
| 9 | **Passes duplicados (Messi e Cristiano)**: já absorvidos pelo **Neymar**, mas o **De Bruyne** ainda lista os dois entre as ferramentas e o fluxo cita "reforço pontual" | `debruyne-orquestrador.md` | Baixa (só custa se forem chamados) | Fácil | P9 |
| 10 | **Handoffs do De Bruyne** repetem, a cada agente, caminhos e instruções que o próprio agente já tem na definição; definição dele tem 9,4 KB e é carregada a cada turno | `debruyne-orquestrador.md` | Média | Fácil | P5 |
| 11 | **Vitinho lê todas as pastas do ciclo**; **Fagner**, **André Carrillo** e **Raniele** leem as mesmas 17 fichas de canal cada um | Definições; `inteligencia/canais/` com 17 fichas | Média | Médio | P10 |
| 12 | **`inteligencia/fontes.md` (24 KB)** é registro de URLs; **Hugo Souza** o reescreve/ acrescenta | 24.392 B | Baixa a média | Fácil | P10 |
| 13 | **Ronaldo** lê mapa e README setorial (~20 KB) a cada mensagem do Telegram | `ecossistema/README.md` + `produtividade/README.md` | Média (muitas chamadas/dia) | Médio | P7 |
| 14 | **Sidorf** lê `cenas.json`, `roteiro.txt` e `angulo.md` só para gerar um prompt de thumbnail, e roda depois de tudo | Definição | Baixa | Fácil | P9 |
| 15 | **Lembrete "marcar conteúdo sintético"** repetido em toda auditoria | `auditoria.md` de vários slugs | Baixa | Fácil | P1 |
| 16 | **Barcola** e **Dembélé** (opus e 7,9 KB) são fora do fluxo diário | Definições | Zero se não são chamados | — | Sem ação |

## Ranking por economia + viabilidade (o que fazer primeiro)
1. P2 (**Vini** TEXTO enxuto): alta economia, só texto de agente.
2. P1 (**Vini** FINAL em metadados): alta economia, só texto de agente.
3. P4 (`notas.md` com teto): alta economia, texto de **Modric**.
4. P3 (fala em fonte única): média economia, pede script (**Rodrygo**).
5. P6 e P7 (enxugar `CLAUDE.md`, backlog e README): alta economia, mas arquivos do dono e do setor de programação.
6. P5, P8, P9, P10: médios e baixos.

## O que não é desperdício (deixe como está)
- **Mbappé** em haiku, **Haaland** em haiku.
- Render e voz: custo zero de tokens.
- `compliance.py`: roda sem tokens e já pega mais coisa do que o **Vini** faz à mão.
- **Courtois** em sonnet: o trabalho dele é julgamento de fato, e é onde o risco de erro público mora.
