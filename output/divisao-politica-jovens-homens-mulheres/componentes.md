# Componentes do vídeo: divisao-politica-jovens-homens-mulheres

**STATUS: AGUARDANDO APROVAÇÃO DO GUILHERME** (fase "aprendendo"). O **Olise** só começa as cenas depois do "ok" do Guilherme, repassado pelo **De Bruyne**.

Proposta do **Raphinha**. Método aprovado em 2026-10-30 e 2026-10-31: componentes isolados, função `*_box`, checador automático, PNGs e contato rotulado.
- Código dos componentes novos: `output/divisao-politica-jovens-homens-mulheres/componentes_video.py`. Cada um tem a companheira `*_box(...)`, que devolve `(x, y, w, h)` com âncora no canto superior esquerdo, incluindo legendas e rótulos.
- Gerador + checador: `componentes_gerar.py`. Rodar da raiz: `.venv/Scripts/python.exe output/divisao-politica-jovens-homens-mulheres/componentes_gerar.py --caixas`.
  - Resultado: `[OK] todos os desenhos cabem nas caixas declaradas` e `[OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro`.
- A posição de cada cena vem de uma fonte só: `layout_cenas()` em `componentes_gerar.py`. A tabela abaixo repete esses valores.
- Nada foi promovido para `media/sketch_componentes.py` nem para o `catalogo.md`; isso só acontece depois da aprovação.

## Visual neutro (tema político)
- **ELAS = LARANJA** (240,110,40) e **ELES = LILÁS** (130,105,185). O **vão** (a diferença) é amarelo-claro tracejado, e a linha da diferença é âmbar. Tudo o que é método (régua, lupa, manchete, cartões) fica em tinta preta.
- **Proibido neste vídeo:**
  - azul × vermelho (são as cores dos dois partidos dos EUA);
  - verde e amarelo juntos (leitura partidária no Brasil);
  - rosa × azul (estereótipo de gênero);
  - bandeiras, símbolos, logos, nome de instituto ou de pesquisa na tela, figuras políticas, a palavra "Brasil".
- Ela e ele se distinguem pela forma e pela cor: cabelo comprido e saia nela, topete curto nele.
- Nenhum dos dois é desenhado como "certo" ou "errado". Na cena 4 a linha deles termina num **"="** (parados), nunca num X ou risco: riscar daria juízo de valor.

## Componentes NOVOS (15 imagens, 12 funções)
| # | Função | O que é |
|---|---|---|
| 1 | `boneco_ela(d, cx, cy, s, seed, frac, cor=ELAS, olha=0)` | boneco palito com cabelo comprido e saia; `olha` = -1 esq / +1 dir (olho e nariz) |
| 2 | `boneco_ele(d, cx, cy, s, seed, frac, cor=ELES, olha=0)` | boneco palito com topete curto; mesma âncora e tamanho |
| 3 | `dupla_distante(d, cx, cy, s, seed, frac, dist=380, com_lupa=True)` | os dois de costas, linha tracejada no meio, lupa em cima; anime `dist` |
| 4 | `etiqueta_rotulo(d, cx, cy, txt="liberal", s, seed, frac)` | etiqueta de pendurar: o "rótulo liberal" é literal |
| 5 | `barras_grupos(d, cx, y_base, s, seed, frac, frac_elas, frac_eles, ...)` | 2 grupos × 3 barras com %, período e legenda |
| 6-7 | `vao_pontos(d, cx, y_base, v_ela, v_ele, s, seed, frac, rotulo, periodo)` | par de barras; o que falta na dele vira bloco amarelo = a diferença |
| 8 | `linhas_trajetoria(d, cx, cy, s, seed, frac, ...)` | linha delas sobe com seta; a deles reta com "="; bonequinhos no fim |
| 9-10 | `cartao_base(d, cx, cy, s, seed, frac, numero, ano, legenda)` | cartão de "outra base": linha quase plana, lupa, número circulado opcional |
| 11 | `regua(d, cx, cy, comp, s, seed, frac, ang)` | régua de madeira clara, só com marcações (sem números, para não parecer dado) |
| 12-13 | `manchete(d, cx, cy, s, seed, frac, titulo=(l1, l2))` | jornal genérico ("notícias"), manchete em 2 linhas trocável |
| 14 | `geracao_dois_ritmos(d, cx, cy, s, seed, frac, rotulo, f_setas)` | moldura tracejada "geração" com ela e ele e setas de tamanhos diferentes |
| 15 | `regua_pergunta(d, cx, cy, s, seed, frac, t)` | balão "?" (pulsa com `t`), régua, e os dois **lado a lado olhando a régua** (rima com o gancho, onde estavam de costas) |

**Reutilizados do catálogo:**
- `boneco_pensando`, de `media/sketch_componentes.py`, na cena 6a;
- `lupa` e `seta`, de `media/sketch_lib.py`.

O "?" do `boneco_pensando` é laranja (componente aprovado, não mexi). Fica o aviso: se ele parecer "cor delas", o **Olise** pode desenhar o `?` à parte em tinta.

## Componentes por cena: posição, escala e caixa
Os textos de tela seguem o `roteiro.txt` revisado (ver "Atenção" no fim). Todos os rótulos têm 26 caracteres ou menos. Números em algarismos.

| Cena (fala) | Componente | Posição / escala | Caixa (x, y, w, h) |
|---|---|---|---|
| **1** gancho | título "Mais distantes?" (84) | (540, 290) | (234, 242, 611, 96) |
| | subtítulo "jovens dos EUA" (52) | (540, 385) | (362, 354, 355, 63) |
| | `dupla_distante` | (540, 1010) s=1.4, `dist` 200→400 | (259, 541, 562, 651) |
| | rótulo "depende da pesquisa" (56) | (540, 1340) | (279, 1307, 522, 67); entra na 2ª frase |
| **2** a série | `etiqueta_rotulo` "liberal" | (540, 280) s=1.2 | (392, 224, 295, 111) |
| | subtítulo "18 a 29 anos, EUA" (50) | (540, 392) | centro |
| | `barras_grupos` | y_base=1080, s=1.0; `frac_elas` na fala "Mulheres...", `frac_eles` em "Homens..." | (148, 500, 784, 795) |
| | rodapé "3 períodos, 2001 a 2024" (46) | (540, 1400) | centro |
| **3** a diferença | título "a diferença" (76) | (540, 290) | centro |
| | `vao_pontos` 28/25 "3 pontos", período "2001-07" | cx=310, y_base=1180 | (189, 730, 242, 558) |
| | `seta` (tinta) | (450,1030) → (635,850) | entre os pares, não toca texto |
| | `vao_pontos` 40/25 "15 pontos", período "2017-24" | cx=770, y_base=1180 | (649, 574, 242, 714); o vão amarelo entra junto com "15" |
| **4** quem se mexeu | título "Quem se mexeu?" (76) | (540, 285) | centro |
| | `etiqueta_rotulo` "liberal" | (540, 410) s=1.0 | marca o "no rótulo liberal" |
| | `linhas_trajetoria` | (560, 860) s=1.0 | (140, 617, 770, 605) |
| | "elas subiram" (laranja, 50) / "eles, parados" (lilás, 50) | (300, 1330) / (780, 1330) | abaixo do gráfico |
| **5** outras bases | título "outras bases: linha plana" (60) | (540, 285) | 25 caracteres |
| | `cartao_base` número "7", ano "2022", legenda "perto de 7 pontos, 2022" | (540, 610) s=1.15 | (195, 438, 690, 437) |
| | `cartao_base` legenda "sem evidência de alta" | (540, 1100) s=1.15 | (195, 928, 690, 437); entra na frase "Na outra..." |
| **6a** "E o porquê? Nenhuma delas prova." | título "E o porquê?" (80) | (540, 290) | |
| | `boneco_pensando` (catálogo) | (540, 930) s=1.8 | (378, 372, 324, 783) |
| | rótulo "nenhuma delas prova" (60) | (540, 1270) | |
| **6b** "Nossa leitura: a manchete depende da régua" | "nossa leitura" (64) | (540, 285) | marca que é opinião |
| | `manchete` ("diferença"/"cresce") | (540, 640) s=1.2 | (228, 412, 624, 456) |
| | `regua` comp=680, ang=-0.06 | (540, 1080) | (194, 1016, 692, 129); gira ou desliza; quando a régua muda, a manchete troca para ("diferença"/"estável") |
| | rótulo "depende da régua" (60) | (540, 1250) | |
| **6c** "geração junta dois grupos..." | `geracao_dois_ritmos` | (540, 820) s=1.1; `f_setas` cresce na fala "ritmos diferentes" | (140, 497, 800, 614) |
| | rótulo "dois grupos, dois ritmos" (58) | (540, 1250) | 24 caracteres |
| **6d** pergunta final | título "Qual é a régua?" (80) | (540, 290) | |
| | `regua_pergunta` | (540, 890) s=1.15; `t=lt` para o "?" pulsar | (184, 396, 713, 880) |

A cena 6 tem uma fala longa (cerca de 15 s), por isso vai em **4 batidas**: 6a → 6b → 6c → 6d. Cada batida troca o quadro inteiro, e o anterior sai antes do próximo entrar. Se o **Olise** preferir dividir em cenas separadas no `cenas.json`, as posições continuam valendo.

## Regras de composição (para o Olise)
- **Nada cobre boneco** (aprendizado de 2026-10-30). Contam como boneco: `dupla_distante`, `barras_grupos` (tem a legenda com bonequinhos), `linhas_trajetoria`, `geracao_dois_ritmos`, `regua_pergunta` e `boneco_pensando`. Nenhum texto, seta ou balão entra nessas caixas (checado).
- **Nada cobre texto** (aprendizado de 2026-10-30). Rótulos, cartões e manchete não são cobertos. Quando um elemento novo entra no lugar de outro, o anterior sai antes. Na 6b, a manchete troca o texto no mesmo lugar (sai "cresce", entra "estável"), sem as duas palavras juntas.
- **Tudo entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500)**, e x entre 30 e 1050. Todas as caixas acima respeitam isso.
- **Uma ideia visual por cena:**
  1. distância (de costas);
  2. a série;
  3. o vão de 3 para 15;
  4. quem se mexeu;
  5. bases planas;
  6. porquê / régua / dois ritmos / pergunta, uma batida de cada vez.
- **Linha vermelha da margem com opacidade baixa** (~28%): já sai de `papel()`; não usar a cor cheia (aprendizado de 2026-10-30).
- **Tela de celular ou chat:** não há neste vídeo. Se o **Olise** puser uma, ela vai com texto coerente com a cena (aprendizado de 2026-10-30).
- **Movimento:**
  - as barras crescem em sequência, sincronizadas com a fala (elas primeiro, eles depois);
  - na cena 3, o bloco amarelo do vão cresce (`frac` de 0,6 a 0,9);
  - na cena 4, a linha delas é traçada antes da linha deles;
  - na cena 1, `dist` cresce de 200 para 400;
  - na cena 6d, o "?" pulsa;
  - corte seco entre as cenas.
- **Acentuação correta** em todo texto de tela (a Kalam tem acentos).

## Atenção (para o De Bruyne repassar)
A seção `## Narração` de `direcao_viral.md` ainda traz as falas **anteriores à revisão do Courtois**. Pelo `revisao.md`, o `roteiro.txt` foi corrigido e a narração não:
- cena 1: falta "Nos Estados Unidos";
- cena 2: falta "da Gallup… entre 2001 e 2024";
- cena 4: falta "no rótulo liberal";
- cena 5: ainda diz "outras duas bases… sem tendência de alta… não há evidência de crescimento".

Os componentes e os rótulos acima seguem o **roteiro revisado**: "jovens dos EUA", etiqueta "liberal" nas cenas 2 e 4, e "3 períodos, 2001 a 2024". Cabe ao **Neymar** (ou a quem o **De Bruyne** indicar) alinhar as `fala` antes do **Olise** escrever o `cenas.json`. O nome do instituto é dito na narração, mas não aparece na tela (pedido da `direcao_viral.md`).

## Imagens para validação
- `componentes/contato.jpg`: os 15 componentes, recortados e numerados.
- `componentes/cenas_exemplo.jpg`: as 9 composições (cenas 1 a 5 e as batidas 6a a 6d) nas posições desta tabela. Serve só para validar o layout; não é o render.
- `componentes/cenas_exemplo_caixas.jpg`: o mesmo, com as caixas do checador desenhadas (magenta = boneco, azul = texto, linhas vermelhas = área segura).
- `componentes/<nome>.png`: cada componente em papel, 1080×1920.
- `componentes/transparentes/<nome>.png`: cada componente em RGBA, para compor sem fundo.
