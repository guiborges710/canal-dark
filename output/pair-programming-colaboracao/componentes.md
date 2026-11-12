# Componentes do vídeo — pair-programming-colaboracao

Proposta do **Raphinha** (curadoria de componentes). **Assets definitivos (2ª rodada)**: os 4 problemas de layout da rodada anterior já estão corrigidos no código e nas posições abaixo. Imagens em `output/pair-programming-colaboracao/componentes/`; versões RGBA (fundo transparente) em `componentes/transparentes/`. Código em `componentes_video.py`; gerador e verificação em `gerar_componentes.py`.

Convenção de cor (mesma do vídeo): **pessoa A = AZUL** (escreve primeiro), **pessoa B = LARANJA** (revisa). Verde = acerto/decisão. Vermelho = negação.

## Como o Olise usa (fonte única de posição)

A verdade das posições está em `gerar_componentes.py` → `layout_cenas()`. Cada componente tem uma função companheira `*_box(cx, cy, s, ...)` em `componentes_video.py` que devolve a caixa ocupada **(x, y, largura, altura)** com âncora no canto superior esquerdo. A verificação automática (`verificar()`) confirma que nenhuma caixa de **boneco** ou **texto** é cruzada por outro elemento e que tudo cai entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500). Rodando o gerador: `[OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.`

## Componentes por cena — posição, escala e caixa (x, y, w, h)

| Cena | Componentes | Posição (cx, cy) / escala | Caixa (x, y, w, h) |
|---|---|---|---|
| **0** negação | título "pair programming" | (540, 290) | (300, 258, 480, 64) |
|  | `tela_riscada` | (540, 620) s=1.0 | (260, 430, 560, 420) |
|  | rótulo "não é isso" (vermelho) | (540, 940) | (400, 913, 280, 54) |
|  | `dupla_pair` | (540, 1250) s=1.35 dist=300 | (309, 1053, 462, 366) |
| **1** discussão | `balao_fala` A ("e se a gente tentar isso?") | (320, 420) 420×180 | (110, 330, 420, 180) |
|  | `balao_fala` B ("por que assim?") | (760, 650) 420×150 | (550, 575, 420, 150) |
|  | `dupla_pair` | (540, 1000) s=1.3 dist=340 | (292, 810, 496, 352) |
|  | `caixa_problema` | (540, 1350) s=0.95 | (398, 1264, 285, 171) |
| **2** papéis | `tela_codigo` (linhas AZUL) | (540, 560) s=0.95 | (274, 380, 532, 399) |
|  | `dupla_pair` | (540, 980) s=1.35 dist=440 | (239, 783, 602, 366) |
|  | `teclado` (sob A) | (320, 1300) s=1.3 | (210, 1251, 221, 99) |
|  | `lupa_revisao` (sob B) | (760, 1290) s=1.0 | (700, 1230, 165, 165) |
|  | rótulo "escreve" / "revisa e sugere" | (320/760, 1450) | (220, 1428, 200, 44) / (610, 1428, 300, 44) |
| **3** troca | título "troca de papel" | (540, 300) | (330, 268, 420, 64) |
|  | `dupla_pair` | (540, 820) s=1.3 dist=440 | (242, 630, 596, 352) |
|  | `setas_troca` | (540, 1130) s=1.3 dist=360 | (316, 1040, 448, 179) |
| **4** solução | `tela_codigo` (AZUL/LARANJA alternadas) | (540, 560) s=0.9 | (288, 389, 504, 378) |
|  | `dupla_pair` (afastados) | (540, 1000) s=1.25 dist=620 | (155, 818, 770, 339) |
|  | rótulo "solução em conjunto" (verde) | (540, 1200) | (300, 1174, 480, 52) |
|  | `check_solucao` | (540, 1350) s=2.6 | (410, 1233, 273, 221) |
| **5** três ganhos | título "pair programming é:" | (540, 300) | (300, 268, 480, 64) |
|  | `ganho_contexto` | (300, 640) s=1.0 | (198, 564, 608, 152) |
|  | `ganho_conhecimento` | (300, 940) s=1.0 | (160, 864, 834, 152) |
|  | `ganho_decisao` | (300, 1240) s=1.0 | (230, 1164, 534, 152) |
| **6** pergunta | `balao_fala` A ("já fez pair programming?") | (540, 420) 620×170 | (230, 335, 620, 170) |
|  | `balao_fala` B ("o que você aprendeu?") | (540, 640) 560×150 | (260, 565, 560, 150) |
|  | `boneco_pensando` | (540, 1280) s=1.5 | (405, 815, 270, 652) |

## As 4 correções desta rodada

1. **Cena 2 — teclado/lupa não encostam mais nos pés.** Os pés dos bonecos (dupla s=1.35) terminam em y≈1149; teclado em cy=1300 e lupa em cy=1290 começam em y≥1230, com ~80 px de folga livre. Rótulos de papel em y=1450, dentro do seguro (1500).
2. **Cena 0 — o X não invade as cabeças.** A `tela_riscada` subiu (cy=620, s=1.0) e a cruz foi reduzida (de 3.6·s para 2.9·s, presa dentro da moldura — `tela_codigo(..., riscada=True)`). A dupla desceu para cy=1250; entre a base da tela (y≈850) e o topo das cabeças (y≈1053) há o rótulo "não é isso" em faixa livre.
3. **Cena 5 — "conhecimento" com respiro.** Em `ganho_conhecimento` as cabeças foram afastadas (dx 70→100·s) e as setas de ida/volta agora ocupam todo o vão entre as bordas internas, sem espremer; o rótulo foi para a direita das cabeças.
4. **Cena 4 — rótulo e check em alturas distintas.** "solução em conjunto" em cy=1200 (caixa termina em y≈1226); `check_solucao` em cy=1350 (começa em y≈1233). Não competem mais pela mesma altura.

## Catálogo de funções (em `componentes_video.py`)

Cada uma tem a companheira `*_box(...)` com a caixa ocupada.

- `tela_codigo(d, cx, cy, s, seed, frac, cores, riscada)` — monitor + pé, linhas de código por autor; `riscada=True` aplica o X dentro da tela.
- `tela_riscada(d, cx, cy, s, seed, frac, cores)` — atalho nomeado para a cena 0.
- `boneco_autor(d, cx, cy, s, seed, frac, cor, papel, cor_rotulo)` — boneco + rótulo de papel opcional.
- `dupla_pair(d, cx, cy, s, seed, frac, dist, papeis)` — os dois bonecos (A azul esq, B laranja dir); `papeis=(rotA, rotB)`.
- `caixa_problema(d, cx, cy, s, seed, frac, linhas)` — caixa azul-gelo "o mesmo problema".
- `balao_fala(d, cx, cy, linhas, larg, alt, seed, frac, tam, cor_borda)` — balão sem cauda; cor da borda diferencia A/B.
- `teclado(d, cx, cy, s, seed, frac)` — teclado (quem escreve).
- `lupa_revisao(d, cx, cy, s, seed, frac)` — lupa (quem revisa).
- `setas_troca(d, cx, cy, s, seed, frac, dist)` — setas azul (ida) e laranja (volta).
- `check_solucao(im, d, cx, cy, s, seed, frac)` — check verde grande com brilho; devolve a imagem.
- `ganho_contexto` / `ganho_conhecimento` / `ganho_decisao(d, cx, cy, s, seed, frac, rotulo)` — os três ícones do fechamento, rótulo à direita.
- `boneco_pensando(d, cx, cy, s, seed, frac, t)` — boneco preto com "?" pulsando.

## Regras de composição (para o Olise)

- **Nada cobre boneco** (aprendizado). Teclado/lupa, setas, rótulos e caixas ficam SEMPRE fora da caixa do `dupla_pair`/`boneco_pensando`. Use os `*_box()` e a verificação antes de fechar a cena.
- **Nada cobre texto** (aprendizado). Se um elemento novo ocupa o lugar de um balão/rótulo, o anterior sai antes do novo entrar.
- **Texto e componentes dentro de `SEGURO_TOPO` (190) .. `SEGURO_BASE` (1500).** Todas as caixas acima já respeitam isso (rótulos de papel da cena 2 em y≤1472).
- **Uma ideia visual por cena.** Foco: negação (0), discussão (1), papéis (2), troca (3), solução (4), três ganhos (5), pergunta (6).
- **Tela sempre com conteúdo coerente** (memória/aprendizado): `tela_codigo` nunca sai vazia — linhas de código na cor de quem escreveu.
- **Entradas escalonadas, corte seco entre cenas** (estilo sketch padrão).

## Validação visual

- `componentes/contato.jpg` — os 13 componentes isolados, rotulados, em fundo de papel.
- `componentes/cenas_exemplo.jpg` — cada cena já composta nas posições desta tabela (só para validar layout; NÃO é o render final).
- `componentes/transparentes/<nome>.png` — cada componente em RGBA (fundo transparente), para uso como asset solto.
