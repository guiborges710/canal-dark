# Componentes do vídeo: fim-dos-terceiros-lugares

**AGUARDANDO APROVAÇÃO DO GUILHERME** (fase "aprendendo"). O **Olise** só começa depois do ok do Guilherme.

Proposta do **Raphinha**. Imagens em `output/fim-dos-terceiros-lugares/componentes/` e versões RGBA (fundo transparente) em `componentes/transparentes/`. O código dos componentes novos está em `componentes_video.py` deste slug. O gerador e a verificação de sobreposição estão em `gerar_componentes.py` (rodar da raiz: `python output/fim-dos-terceiros-lugares/gerar_componentes.py`).

Nenhum componente foi promovido para `media/sketch_componentes.py` nem para `componentes/catalogo.md`. Isso só acontece depois da aprovação.

## Atenção: texto da tela x narração
A seção `## Narração` da `direcao_viral.md` ainda está na versão **anterior** à revisão do **Courtois**. Os textos de tela abaixo seguem o `roteiro.txt` **revisado**:
- "livraria" (não "praça") como exemplo de terceiro lugar;
- "quase 7 h" (não "perto de 7");
- "pode ser uma mistura" (não "provavelmente são as duas coisas");
- "não parece ser só deles"; "Bryce Ward" nomeado; "1º tri 2026 x 1º tri 2025".
A `## Narração` precisa ser alinhada ao `roteiro.txt` (tarefa do **Neymar**) antes do `cenas.json`. Se a narração for alterada, as cenas 2, 3, 6 e 7 mudam junto.

## Convenção de cor deste vídeo
- **AZUL**: convívio, tempo com amigos, telas (tela fria), fonte citada.
- **LARANJA**: custo, gasto, hipótese (leitura nossa), destaque "jovens".
- **VERMELHO**: queda (seta das saídas -7,1%, seta dos jovens).
- **FERRO tracejado**: o que sumiu ou não existe (banco grátis sumindo, relógio sem medida).
- **MADEIRA**: mobília do terceiro lugar (mesa, cadeira, banco).

## Componentes NOVOS (17), em `componentes_video.py`, cada um com `*_box(...)`
| # | Função | O que é |
|---|---|---|
| 1 | `mesa_cafe(d, cx, cy, s, seed, frac, cadeiras=2, xicaras=1, vapor=False, t=0)` | mesa de bistrô de lado, cadeiras vazias; `cy` = topo do tampo |
| 2 | `cadeira_cafe(d, cx, cy, s, seed, frac, lado="esq")` | cadeira solta; `cy` = assento |
| 3 | `xicara_cafe(d, cx, cy, s, seed, frac, vapor=True, t=0)` | xícara no pires; vapor ondula com `t` |
| 4 | `pilha_livros(d, cx, cy, s, seed, frac)` | três livros (livraria) |
| 5 | `maleta_trabalho(d, cx, cy, s, seed, frac)` | maleta (2º lugar: trabalho) |
| 6 | `selo_numero(d, cx, cy, s, seed, frac, txt="3º", cor=LARANJA)` | selo redondo "1º/2º/3º" |
| 7 | `coluna_relogios(d, cx, y_base, s, seed, frac, horas, cor, t)` | 1 relógio por hora; fração = relógio em fatia tracejado ("quase"/"menos de"); `frac` faz a pilha crescer |
| 8 | `cartao_variacao(d, cx, cy, s, seed, frac, valor, rotulo, sentido, cor, icone="porta"/"moeda")` | cartão com ícone, seta, número grande e rótulo |
| 9 | `relogio_sem_medida(d, cx, cy, s, seed, frac, t)` | relógio tracejado com "?" (Brasil sem a medida) |
| 10 | `banco_praca(d, cx, cy, s, seed, frac, sumindo=False, etiqueta="grátis")` | banco com etiqueta "grátis"; `sumindo=True` = tracejado cinza |
| 11 | `recibo_orcamento(d, cx, cy, s, seed, frac, titulo, itens, destaque=2)` | recibo "orçamento" com "ver amigo" marcado; **sem valores** (só "R$ __") |
| 12 | `selo_hipotese(d, cx, cy, s, seed, frac, txt="hipótese, não prova")` | carimbo de borda dupla, laranja |
| 13 | `tv_streaming(d, cx, cy, s, seed, frac, t)` | TV com play, "continuar assistindo?" e barra que anda com `t` (sem marca) |
| 14 | `celular_video(d, cx, cy, s, seed, frac, t)` | celular com vídeo e "próximo em 5 s" (tela com texto, sem marca) |
| 15 | `sofa_sozinho(d, cx, cy, s, seed, frac)` | boneco sentado sozinho no sofá (**é boneco**) |
| 16 | `mistura_causas(d, cx, cy, s, seed, frac)` | dois círculos: "lugar e custo" (laranja) × "telas" (azul), interseção hachurada |
| 17 | `fila_idades(d, cx, cy, s, seed, frac, destaque=0, rotulo="jovens")` | 4 bonecos; jovem laranja com seta vermelha grande, os outros com seta cinza menor, o último com bengala (**é boneco**) |

Auxiliar: `tracejado(d, pts, seed, frac, ...)` (linha tracejada à mão).

**Reusados**: `casa` e `copo` (de `media/sketch_lib.py`), `balao_fala` (catálogo, `media/sketch_componentes.py`).

## Componentes por cena: posição, escala e caixa
Quem manda nas posições é `gerar_componentes.py` → `layout_cenas()`. As caixas `(x, y, w, h)` saem das funções `*_box`, e as dos textos são medidas pela fonte real. Resultado do checador: `[OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro`. Ele confere a faixa vertical 190..1500 e a horizontal 150..1060, que fica à direita da margem do caderno.

| Cena | Fala (roteiro.txt) | Componentes | Posição (cx, cy) / escala |
|---|---|---|---|
| **1** gancho | "Seu terceiro lugar sumiu..." | título "seu 3º lugar sumiu" (74) | (540, 300) |
|  |  | `mesa_cafe` cadeiras=2, xicaras=1, vapor=False | (540, 880) s=1.28 |
| **2** definição | "fora de casa e do trabalho... café, bar, livraria... Ray Oldenburg" | título "o terceiro lugar" (70) | (540, 290) |
|  |  | `casa` (preench. ferro claro) + "1º casa" (46, FERRO) | (330, 560) s=0.75 / rótulo (330, 690) |
|  |  | `maleta_trabalho` + "2º trabalho" (46, FERRO) | (760, 580) s=0.85 / rótulo (760, 690) |
|  |  | `selo_numero` "3º" laranja | (540, 800) s=1.2 |
|  |  | `xicara_cafe` vapor / `copo` / `pilha_livros` | (300, 1070) s=1.0 / (540, 1070) s=0.72 / (790, 1070) s=1.0 |
|  |  | "café" / "bar" / "livraria" (48) | y=1235, mesmos x |
|  |  | "sociólogo Ray Oldenburg" (50, AZUL) | (540, 1380) |
| **3** EUA | "quase 7 horas até 2013. Em 2021, menos de 3." | título "EUA (pesquisa ATUS)" (64) + "horas/semana com amigos" (50, AZUL) | (540, 270) / (540, 350) |
|  |  | "quase 7 h" (58) + `coluna_relogios` horas=6.8 | rótulo (360, 470) / coluna (360, y_base=1250) s=1.0 |
|  |  | "menos de 3 h" (58, LARANJA) + `coluna_relogios` horas=2.7 seed=20 | rótulo (720, 880) / coluna (720, 1250) s=1.0 |
|  |  | "até 2013" / "2021" (52) | (360, 1315) / (720, 1315) |
| **4a** Brasil | "No Brasil não existe essa medida." | título "e no Brasil?" (72) | (540, 290) |
|  |  | `relogio_sem_medida` | (540, 800) s=1.6 |
|  |  | "sem essa medida" (60, FERRO) | (540, 1120) |
| **4b** consumo | "saídas caíram 7,1% contra um ano antes... gasto por saída subiu 28,3%" | título "Brasil: consumo" (70) + "1º tri 2026 x 1º tri 2025" (46, FERRO) | (540, 280) / (540, 360) |
|  |  | `cartao_variacao` "-7,1%" "saídas" porta, sentido=-1, VERMELHO | (350, 860) s=1.0 |
|  |  | `cartao_variacao` "+28,3%" "gasto por saída" moeda, sentido=1, LARANJA | (770, 860) s=1.0 |
| **5** hipótese | "se o lugar de graça some, ver amigo vira item de orçamento. É hipótese, não prova." | título "nossa leitura" (66, LARANJA) | (540, 280) |
|  |  | `banco_praca` sumindo=True | (540, 610) s=1.15 |
|  |  | `seta` laranja (de cima para baixo) | (540, 750) → (540, 820) |
|  |  | `recibo_orcamento` (destaque "ver amigo") | (540, 1070) s=1.0 |
|  |  | `selo_hipotese` | (540, 1400) s=1.0 |
| **6** contraexemplo | "Bryce Ward... as telas. O tempo sozinho cresceu, com TV, celular e streaming." | título "e as telas?" (80) + "economista Bryce Ward" (46, AZUL) | (540, 270) / (540, 360) |
|  |  | `tv_streaming` | (540, 660) s=1.2 |
|  |  | `sofa_sozinho` (boneco) | (410, 1190) s=0.95 |
|  |  | `celular_video` | (820, 1185) s=1.35 |
|  |  | "tempo sozinho cresceu" (52) | (540, 1420) |
| **7a** mistura | "Pode ser uma mistura das duas coisas." | título "pode ser uma mistura" (66) | (540, 290) |
|  |  | `mistura_causas` | (540, 820) s=1.3 |
| **7b** jovens | "nos EUA a queda foi forte entre os jovens, mas não parece ser só deles." | título "EUA: queda forte" (68) | (540, 290) |
|  |  | `fila_idades` (boneco, rótulo "jovens") | (560, 880) s=1.25 |
|  |  | "não parece ser só deles" (54) | (540, 1360) |
| **8** pergunta | "Qual encontro com amigos você deixou de fazer sem nunca ter decidido isso?" | `balao_fala` (catálogo) ["qual encontro você", "deixou de fazer?"], larg=760, alt=250, tam=60, cor_borda=LARANJA | (540, 400) |
|  |  | `mesa_cafe` cadeiras=2, xicaras=0 (cadeira vazia na última imagem) | (540, 960) s=1.28 |

As cenas 4 e 7 têm duas frases e duas ideias, por isso vêm divididas em a/b. Se o **Olise** preferir uma cena só, a parte "a" sai antes de a "b" entrar, sem as duas na tela ao mesmo tempo.

## Movimento sugerido (no estilo sketch)
- 1: mesa já desenhada no quadro 0 (gancho). As cadeiras entram com `frac`. Nada mais entra.
- 2: casa e maleta primeiro (em cinza, o "não é isso"), depois o "3º" com `mola`, depois café, bar e livraria escalonados (0,3 s cada) e por último Oldenburg.
- 3: a coluna de 2013 cresce (`frac` de 0 a 1 em ~1 s) e depois a de 2021. O rótulo de cada uma só aparece quando a coluna termina. Ding no "menos de 3 h".
- 4b: os cartões entram com `mola`, um de cada vez. Ding em cada número.
- 5: o banco aparece já tracejado (sumindo), a seta é desenhada e o recibo entra. O selo "hipótese, não prova" entra **por último**, junto da fala "É hipótese".
- 6 (*pattern interrupt*): corte seco. A TV entra com `mola` e estouro. A direção pede que a tela "cubra a mesa", mas isso fere a regra de não tapar o que está na tela: **a mesa não aparece nesta cena**, e a virada vem do corte e do estouro da TV. A barra de progresso anda com `t`. Sofá e celular entram depois.
- 7a: os dois círculos são desenhados com `frac`, um depois do outro. A hachura aparece no fim.
- 7b: os bonecos entram escalonados. A seta vermelha do jovem vem primeiro e as cinzas depois, junto do "não parece ser só deles".
- 8: a mesa vazia aparece primeiro e o balão entra com `mola`. Termina parado na mesa com as cadeiras vazias (o vapor não existe: xicaras=0).

## Regras de composição (para o Olise)
- **Nada cobre boneco** (aprendizado 2026-10-30). `sofa_sozinho` e `fila_idades` são bonecos. TV, celular e rótulos ficam fora das caixas deles, o que já foi verificado.
- **Nada cobre texto** (aprendizado 2026-10-30). Cartões, recibo, selo, `mistura_causas` e balão contam como texto. Se algo novo entra no lugar de um deles, o anterior sai antes.
- **Texto e componentes dentro de `SEGURO_TOPO` (190) .. `SEGURO_BASE` (1500)** e à direita da margem do caderno (x ≥ 150). Todas as posições acima respeitam isso.
- **Uma ideia visual por cena**: lugar vazio (1), definição (2), queda de horas (3), sem medida (4a), consumo (4b), hipótese (5), telas (6), mistura (7a), não é só uma idade (7b), pergunta (8).
- **Elemento que entra não tapa o que já está na tela** sem que o anterior saia (ver a cena 6).
- **Telas sempre com texto coerente** (aprendizado 2026-10-30): a TV mostra "continuar assistindo?" e o celular mostra "próximo em 5 s". Nunca usar tela vazia nem marca de streaming.
- **Linha vermelha da margem com opacidade baixa** (~28%): já sai de `papel()`, não usar a cor cheia.
- **Números exatamente como no roteiro.txt e nas notas**: "quase 7 h", "menos de 3 h", "até 2013", "2021", "-7,1%", "+28,3%", "1º tri 2026 x 1º tri 2025". As colunas de relógio são ilustrativas (6,8 e 2,7 relógios) e o número que vale é o do rótulo. Não escrever "6,8 h" nem "2,7 h".
- **O recibo não tem valores**: "aluguel", "mercado" e "ver amigo" são categorias ilustrativas da hipótese, não dados. Não pôr números nele.
- **Origem do dado na tela**: "EUA (pesquisa ATUS)" na cena 3 (sugestão do **Courtois**) e "economista Bryce Ward" na cena 6.
- **Banco de praça só como "lugar de graça"** (cena 5), nunca como exemplo de Oldenburg. O **Courtois** tirou "praça" da definição. A cena 2 usa café, bar e livraria.
- **Acentuação correta** em todo texto de tela (a Kalam tem acentos e "º"). Cada rótulo tem até 26 caracteres, e todos os acima cabem.
- **Sem legenda na base**, corte seco entre cenas e entradas escalonadas.

## Validação visual
- `componentes/contato.jpg`: os 17 componentes isolados e rotulados.
- `componentes/cenas_exemplo.jpg`: as 10 cenas montadas nas posições desta tabela. Serve só para validar o layout e não é o render.
- `componentes/cenas_exemplo_caixas.jpg`: as mesmas cenas com as caixas do checador (vermelho = boneco, azul = texto, verde = objeto, magenta = limites seguros).
- `componentes/<nome>.png`: cada componente em papel. `componentes/transparentes/<nome>.png`: em RGBA.
