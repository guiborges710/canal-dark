# Componentes do vídeo: adultos-morando-com-os-pais

**AGUARDANDO APROVAÇÃO DO GUILHERME** (fase "aprendendo"). O **Olise** só começa as cenas depois do OK do Guilherme.

Proposta do **Raphinha**. Imagens em `output/adultos-morando-com-os-pais/componentes/` e versões com fundo transparente em `componentes/transparentes/`. O código dos componentes novos está em `componentes_video.py`. O gerador e a verificação de sobreposição estão em `gerar_componentes.py`. Nada foi promovido para `media/sketch_componentes.py` nem para o catálogo: isso só acontece depois da aprovação.

**Texto de referência:** use o `roteiro.txt` **revisado** pelo **Courtois**. As falas da `## Narração` em `direcao_viral.md` são de antes da revisão. Valem as versões corrigidas: "Os dados apontam outra explicação", "que encontramos", "em grandes cidades", "Na União Europeia" e "o Pew Research apontou". Os rótulos de tela abaixo já seguem o texto revisado.

## Convenção de cor deste vídeo
- **AZUL**: o filho adulto, quem mora com os pais (e a barra de 2012).
- **INK**: os pais, neutro, média da UE.
- **LARANJA**: custo, dúvida ("?" da lacuna, "hoje"), Itália.
- **VERMELHO**: só o risco sobre o rótulo ("preguiça?", "rótulo").
- **SOL_AMARELO / dourado (200,140,20)**: alianças, lâmpada acesa, "o contexto explica".
- **VERDE**: barra dos EUA. A cor é própria para não parecer continuação das barras do Brasil.

## Componentes NOVOS (em `componentes_video.py`, cada um com `*_box`)
| # | Função | O que é | Parâmetros-chave |
|---|---|---|---|
| 1 | `casa_familia(d, cx, cy, s, seed, frac)` | casa com janela + pai (tinta) e filho adulto (azul) em pé ao lado, no mesmo chão; os bonecos ficam fora da casa | `s` |
| 2 | `etiqueta_riscada(d, cx, cy, palavra, s, seed, frac, risco, tam)` | etiqueta de papel com furo e a palavra; `risco` 0..1 passa o traço vermelho (a palavra continua legível) | `palavra`, `risco` (animar com `entra`) |
| 3 | `grafico_lacuna(d, cx, y_base, itens, lacuna, alt_max, larg, passo, seed, lt, t0, seta_subida)` | barras que crescem em sequência, seta laranja curta entre a 1ª e a 2ª, e a **barra-lacuna** tracejada com "?" e "hoje" | `itens` no formato do `barras()` da lib |
| 3b | `barra_lacuna(d, cx, y_base, larg, alt, s, rotulo, seed, frac)` | só a barra tracejada com "?" (dado que não existe) | `rotulo` |
| 4 | `barra_unica(d, cx, y_base, txt, rotulo, sub, alt, larg, cor, seed, lt, t0)` | uma barra isolada com valor, rótulo e sub-rótulo (sem comparação) | `sub` = faixa etária |
| 5 | `icone_livro(d, cx, cy, s, seed, frac)` | livro aberto (estudo) | `s` |
| 6 | `custo_moradia(d, cx, cy, s, seed, frac)` | casinha laranja-clara + moeda R$ (custo de morar sozinho) | `s` |
| 7 | `icone_alianca(d, cx, cy, s, seed, frac)` | duas alianças douradas entrelaçadas (casamento) | `s` |
| 8 | `alianca_relogio(d, cx, cy, s, seed, frac, t)` | alianças + relógio de pulso (casamento adiado); `t` gira o ponteiro | `t = lt` |
| 9 | `regua_idades(d, cx, cy, s, marcas, ini, fim, larg, seed, frac, n_marcas, tam_num, tam_lugar, abaixo)` | régua de 20 a 32 anos com pinos coloridos, número e lugar. `abaixo=True` põe tudo embaixo da linha (o boneco anda em cima); `n_marcas` faz as marcas entrarem uma por vez | `MARCAS_UE` (21,4 Finlândia / 26,2 média UE / 30,1 Itália) |
| 10 | `boneco_andando(d, cx, cy, s, seed, frac, cor, fase)` | boneco de palito com passada; `fase = lt*9` enquanto anda | `fase` |
| 11 | `lampada(im, d, cx, cy, s, seed, frac, acesa, t)` | lâmpada com rosca; `acesa` pinta, soma brilho e solta raios que pulsam. **Recebe e devolve `im`** | `acesa`, `t = lt` |
| 12 | `duas_portas(d, cx, cy, s, seed, frac, rotulos, cores, fundos, dist, tam)` | duas portas com placa "escolha" (azul) e "conta" (laranja); nenhuma vem destacada | `rotulos` |
| util | `caixa_texto(x, y, s, tam)` | caixa exata de um texto na fonte Kalam (para posicionar sem cruzar) | |

## Componentes REUTILIZADOS
- `boneco_pensando` (catálogo, `media/sketch_componentes.py`): fechamento, cena 7.
- Da lib `media/sketch_lib.py`: `casa` (cena 3), `balao` com "?" (cena 1), `seta`, `pessoa` (dentro de `casa_familia`), `moeda`, `relogio`, `brilho`.

## Componentes por cena (posição e escala; fonte única = `gerar_componentes.py` → `layout_cenas()`)
| Cena | Componentes | Posição (cx, cy) / escala | Observação |
|---|---|---|---|
| **1** gancho | `etiqueta_riscada("preguiça?", tam=100)` | (540, 420) | o risco entra com `risco=entra(lt, 0.6)`; frame 0 já mostra casa + etiqueta |
|  | `balao` 230×170, "?" tam 110, cauda esq | (870, 790) | acima do boneco azul, sem tocá-lo |
|  | `casa_familia` | (560, 1250) s=1.85 | pai tinta + filho azul |
| **2** Brasil | título "Brasil, 25 a 34 anos" tam 68 | (540, 300) | |
|  | `grafico_lacuna` (2002 20% / 2012 24% / "hoje" ?) | cx=540, y_base=1330, alt_max=700, larg=210, passo=300 | barras crescem; a lacuna entra quando a fala diz "não dá para falar de hoje" |
| **3** explicações | título "explicações em 2012" tam 70 | (540, 300) | |
|  | `casa` (lib) | (540, 640) s=1.5 | |
|  | 3 `seta` cinza (FERRO) dos ícones para a casa | (265,1010)→(440,815); (545,1000)→(545,830); (825,1010)→(650,815) | uma seta por ícone, na ordem da fala |
|  | `icone_livro` / `custo_moradia` / `icone_alianca` | (235,1140) s=1.15 / (550,1140) s=1.2 / (850,1140) s=1.2 | entram em sequência: estudo, custo, casamento |
|  | rótulos "estudo" (azul) / "custo" (laranja) / "casamento" (dourado) tam 60 | y=1330, x = 235 / 550 / 850 | |
| **4** UE | título "idade ao sair de casa" tam 70 | (540, 300) | |
|  | `regua_idades(abaixo=True, s=1.1, tam_num=62, tam_lugar=48)` | (540, 1180) | marcas entram na ordem da fala: 26,2 → 21,4 → 30,1 |
|  | `boneco_andando` s=1.8 | pés na linha (cy = 1180-6-125·1.8 = 949); x anda de `regua_x(540,21.4,1.1)` até `regua_x(540,30.1,1.1)` | anda por cima da linha, sem descer para os rótulos |
| **5** leitura | `etiqueta_riscada("rótulo", tam=92)` | (540, 370) | risco entra em "O rótulo não explica" |
|  | `lampada` s=1.7 | (540, 790) | acende (`acesa` 0→1) em "O contexto explica" |
|  | "o contexto explica" dourado tam 74 | (540, 1120) | |
|  | `regua_idades` mini s=0.9, só números (sem lugar), tam_num=62 | (540, 1370) | lembra a régua da cena 4 |
| **6** virada | título "não é só dinheiro" tam 76 | (540, 300) | entra primeiro (pattern interrupt) |
|  | `barra_unica("32,1%", "EUA, 2014", "18 a 34 anos", alt=700, larg=230)` verde | cx=300, y_base=1320 | sozinha; nunca ao lado das barras do Brasil |
|  | `alianca_relogio` s=1.25 | (775, 860) | entra em "casamento adiado"; ponteiro gira com `t=lt` |
|  | "casamento adiado" tam 56 | (775, 1110) | |
| **7** pergunta | título "escolha ou conta?" tam 80 | (540, 280) | |
|  | `duas_portas` s=1.2 | (540, 720) | |
|  | `boneco_pensando` s=1.3 | (540, 1330) | "?" pulsa com `t=lt`; sem resposta pronta: nenhuma porta abre |

`componentes/cenas_exemplo_caixas.jpg` mostra cada caixa: magenta = texto ou boneco (nada pode cruzar), verde = objeto, linhas vermelhas = `SEGURO_TOPO`/`SEGURO_BASE`. O checador imprime: `[OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.`

## Regras de composição (para o Olise)
- **Nada cobre boneco** (aprendizado 2026-10-30). Na cena 1, o balão fica acima do boneco azul, e a cauda para antes da cabeça. Na cena 7, as portas terminam acima do "?" do boneco. Única exceção, intencional: na cena 4 o boneco **pisa** a linha da régua (é o chão). Por isso os pinos, números e países ficam **embaixo** da linha (`abaixo=True`) e o boneco nunca desce até eles.
- **Nada cobre texto** (aprendizado 2026-10-30). Se algo novo entra no lugar de um texto, o anterior sai antes. O risco vermelho das etiquetas é a exceção de propósito: é fino e inclinado, e a palavra continua legível.
- **Texto e componentes entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500).** Todas as posições acima respeitam isso.
- **Uma ideia visual por cena:** rótulo "preguiça" negado (1), alta com lacuna (2), três explicações (3), idades por país (4), rótulo × contexto (5), não é só dinheiro (6), escolha ou conta (7).
- **Elemento que entra não tapa o que já está na tela.** Nas cenas 3 e 4, ícones e marcas entram em sequência, cada um no seu lugar, sem trocar de posição.
- **Não juntar Brasil, UE e EUA num mesmo gráfico** (faixas etárias diferentes, `direcao_viral.md` e `revisao.md`). Cada um tem cena, componente e cor próprios.
- **Sem fonte, sem logo e sem nome de instituto na tela** (nada de "IBGE", "Eurostat" ou "Pew"). "média UE" e os nomes de país podem aparecer, porque são o dado, não a fonte.
- **Números em algarismos e com vírgula decimal:** "20%", "24%", "21,4", "26,2", "30,1", "32,1%", "2002", "2012", "2014". São só os do `roteiro.txt` e de `notas.md`. Nenhum dado de "hoje": a barra "hoje" é só "?".
- **Rótulos com até 26 caracteres.** O maior é "idade ao sair de casa" (21).
- **Linha vermelha da margem com opacidade baixa** (~28%). Já sai de `papel()`; não usar a cor cheia.
- **Tom respeitoso:** o boneco azul nunca aparece deitado, encolhido ou caricato. O vídeo nega o estereótipo, não o reforça.
- **Movimento:** contorno com `frac=entra(lt, t0)`, escala com `mola`; barras crescem; boneco anda com `fase=lt*9`; lâmpada pulsa com `t=lt`; ponteiro gira. Corte seco entre cenas.

## Validação visual
- `componentes/contato.jpg`: os 15 componentes, rotulados NOVO ou reuso.
- `componentes/cenas_exemplo.jpg`: as 7 cenas compostas nas posições desta tabela. Serve só para validar o layout; não é o render.
- `componentes/cenas_exemplo_caixas.jpg`: as mesmas cenas com as caixas do checador.
- `componentes/<nome>.png`: cada componente em papel. `componentes/transparentes/<nome>.png`: o mesmo em RGBA.
