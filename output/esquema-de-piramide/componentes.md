# Componentes do vídeo — esquema-de-piramide

Proposta do **Raphinha** (curadoria de componentes), **aguardando validação do Guilherme** (fase "aprendendo"). Imagens em `output/esquema-de-piramide/componentes/`; versões RGBA (fundo transparente) em `componentes/transparentes/`. Código dos componentes novos em `componentes_video.py`; gerador e verificação de sobreposição em `gerar_componentes.py`.

Nenhum componente foi promovido para `media/sketch_componentes.py` nem para o catálogo: isso só acontece depois da aprovação.

Convenção de cor deste vídeo:
- **AZUL** = pessoa / confiança / multinível legal (venda real).
- **LARANJA** = dinheiro em movimento / adesão / recrutamento.
- **VERDE** = produto real / acerto.
- **VERMELHO** = colapso, condenação, negação.
- **SOL_AMARELO** = moeda / cifrão.

## Como o Olise usa (fonte única de posição)

A verdade das posições está em `gerar_componentes.py` → `layout_cenas()`. Cada componente tem a companheira `*_box(cx, cy, s, ...)` em `componentes_video.py` que devolve a caixa ocupada **(x, y, largura, altura)** com âncora no canto superior esquerdo. A verificação automática (`verificar()`) confirma que nenhuma caixa de **boneco** ou **texto** é cruzada por outro elemento e que tudo cai entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500). O gerador imprime: `[OK] nenhuma caixa de boneco/texto cruzada; tudo dentro do seguro.`

## Componentes NOVOS deste vídeo

Em `componentes_video.py`, cada um com a companheira `*_box(...)`:

- `piramide_pessoas(d, cx, cy, s, seed, frac, cor, dinheiro, colapso)` — pirâmide de 4 degraus de bonequinhos (cabeça + ombros). `dinheiro=True`: setas amarelas sobem da base ao topo. `colapso=True`: base vermelha + rachadura vermelha.
- `pilha_dinheiro(d, cx, cy, s, seed, frac)` — três notas verdes empilhadas com "R$" (o topo que ganha). (Reserva; não usada nas 7 cenas, disponível ao Olise.)
- `fonte_dinheiro(d, cx, cy, s, seed, frac, modo)` — `modo="venda"`: caixa de produto verde → seta → moeda (vem de venda real). `modo="adesao"`: três cabeças laranja entrando → seta → moeda (vem só de adesão).
- `convite_confianca(d, cx, cy, s, seed, frac)` — dois bonecos próximos; o azul estende um envelope ao outro, com coração pequeno (confiança). O convite chega por quem você confia.
- `icone_avestruz(d, cx, cy, s, seed, frac)` — avestruz estilizado (corpo oval, pescoço, cabeça, duas pernas).
- `icone_gado(d, cx, cy, s, seed, frac)` — boi estilizado (corpo, cabeça com chifres, patas, cauda).
- `icone_bitcoin(d, cx, cy, s, seed, frac)` — moeda amarela com "B" cortado por duas hastes. Genérico, **sem logo de marca**.
- `martelo_juiz(d, cx, cy, s, seed, frac)` — martelo de juiz + base (condenação).
- `caixa_caso(d, cx, cy, s, seed, frac, nome, ano, pena)` — cartão com nome, ano e pena de um caso. **Textos vêm das notas; não inventar.**
- `pessoa_ou_dinheiro(d, cx, cy, s, seed, frac)` — boneco azul (a pessoa) à esquerda, moeda à direita, divisória pontilhada (a escolha).

## Componentes por cena — posição, escala e caixa (x, y, w, h)

| Cena | Componentes | Posição (cx, cy) / escala | Caixa (x, y, w, h) |
|---|---|---|---|
| **1** gancho | título "o que é / esquema de pirâmide?" | (540, 300) duas linhas | (160, 230, 760, 160) |
|  | `piramide_pessoas` (dinheiro subindo) | (540, 950) s=1.0 `dinheiro=True` | (460, 630, 680, 310) |
| **2** o que é | título "quando para de entrar" | (540, 300) | (210, 270, 660, 60) |
|  | `piramide_pessoas` (colapso) | (540, 900) s=1.0 `colapso=True` | base vermelha + rachadura |
|  | rótulo "a base perde tudo" (vermelho) | (540, 1340) | (260, 1312, 560, 56) |
| **3** diferença | título "de onde vem o dinheiro" | (540, 280) | (210, 250, 660, 60) |
|  | rótulo "multinível: venda real" (verde) | (420, 500) âncora esq | (160, 474, 560, 52) |
|  | `fonte_dinheiro` modo="venda" | (380, 640) s=1.1 | caixa verde → moeda |
|  | rótulo "pirâmide: só adesão" (laranja) | (420, 980) âncora esq | (160, 954, 560, 52) |
|  | `fonte_dinheiro` modo="adesao" | (360, 1120) s=1.1 | cabeças → moeda |
| **4** confiança | título "o convite vem de quem" | (540, 300) | (210, 270, 660, 60) |
|  | `convite_confianca` | (540, 820) s=1.3 | dois bonecos + envelope |
|  | rótulo "você confia" (azul) | (540, 1220) | (300, 1194, 480, 52) |
| **5** casos | `caixa_caso` (Avestruz Master / 2005 / 12 a 13 anos e meio) | (540, 650) s=1.1 | cartão |
|  | `martelo_juiz` | (540, 1080) s=1.0 | martelo + base |
| **6** mesma mecânica | título "muda a fachada" | (540, 300) | (240, 270, 600, 60) |
|  | `icone_gado` | (260, 760) s=0.9 | esquerda |
|  | `icone_avestruz` | (540, 760) s=0.9 | centro |
|  | `icone_bitcoin` | (820, 760) s=1.0 | direita |
|  | rótulo "a mecânica se repete" | (540, 1200) | (210, 1174, 660, 52) |
| **7** pergunta | título "o que você confere?" | (540, 300) | (190, 270, 700, 60) |
|  | `pessoa_ou_dinheiro` | (540, 820) s=1.3 | boneco \| moeda |
|  | rótulo "a pessoa" (azul) | (320, 1240) | (180, 1214, 300, 52) |
|  | rótulo "ou o dinheiro" | (760, 1240) | (600, 1214, 320, 52) |

Observação: a **cena 5** usa só o caso do Avestruz Master como cartão-âncora no layout de exemplo. No render, o **Olise** pode repetir o mesmo molde `caixa_caso` para TelexFree (2013 / 12 anos e 6 meses cada) e Faraó dos Bitcoins (2025 / 19 anos e 2 meses), um por vez, cada um com seu `martelo_juiz` — **nunca dois cartões sobrepostos na tela ao mesmo tempo**. Os textos são os das notas; manter "segundo a acusação" perto de qualquer número do Faraó e não escrever o valor fechado da TelexFree (usar "bilhões") — ver `direcao_viral.md`.

## Regras de composição (para o Olise)

- **Nada cobre boneco** (aprendizado 2026-10-30). `convite_confianca` e `pessoa_ou_dinheiro` são bonecos: envelope, moeda, divisória e rótulos ficam fora das caixas dos bonecos (já verificado). Nenhum ícone/rótulo invade a caixa `*_box`.
- **Nada cobre texto** (aprendizado 2026-10-30). Se um elemento novo entra no lugar de um rótulo/cartão, o anterior sai antes. Na cena 5, troca de caso = o cartão antigo sai, o novo entra.
- **Texto e componentes dentro de `SEGURO_TOPO` (190) .. `SEGURO_BASE` (1500).** Todas as caixas acima respeitam isso.
- **Uma ideia visual por cena.** Foco: pergunta (1), colapso (2), venda real × adesão (3), confiança (4), caso + condenação (5), mesma mecânica (6), pergunta de volta (7).
- **Linha vermelha da margem com opacidade baixa** (~28%) — já sai de `papel()`; não usar a cor cheia.
- **Números em algarismos na tela** (aprendizado deste vídeo): "2005", "12 a 13 anos e meio" etc. A narração fala por extenso; a tela usa algarismos.
- **Sem instituição religiosa nomeada e sem logo/marca real.** A cena de confiança usa ícones genéricos (boneco, envelope, coração). Bitcoin é moeda genérica com "B", sem logo.
- **Acentuação e gramática corretas** em todo texto de tela (fonte Kalam suporta acentos).
- **Entradas escalonadas, corte seco entre cenas** (estilo sketch padrão). Pirâmide com dinheiro subindo, rachadura entrando na cena 2 e martelo batendo pedem movimento ao entrar.

## Validação visual

- `componentes/contato.jpg` — os 12 componentes isolados, rotulados, em fundo de papel.
- `componentes/cenas_exemplo.jpg` — as 7 cenas já compostas nas posições desta tabela (só para validar layout; NÃO é o render final).
- `componentes/<nome>.png` — cada componente em papel.
- `componentes/transparentes/<nome>.png` — cada componente em RGBA (fundo transparente), como asset solto.
