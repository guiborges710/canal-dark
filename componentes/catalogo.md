# Catálogo de componentes aprovados

Mantido pelo **Raphinha**. Só entra aqui o que o Guilherme aprovou. Código reutilizável em `media/sketch_componentes.py`; os ícones básicos já existem em `media/sketch_lib.py`.

Todos os componentes abaixo têm função companheira `*_box(...)` que devolve a caixa ocupada `(x, y, w, h)` (âncora no canto superior esquerdo), usada pelo checador de sobreposição.

| Nome | Função | Parâmetros | Onde está | Aprovado em |
|---|---|---|---|---|
| Tela de código | `tela_codigo(d, cx, cy, s=1.0, seed=0, frac=1.0, cores=None, riscada=False)` | posição `cx,cy`; escala `s`; `cores` (1 por linha); `riscada` põe X vermelho | `media/sketch_componentes.py` | 2026-10-30 |
| Tela riscada | `tela_riscada(d, cx, cy, s=1.0, seed=0, frac=1.0, cores=None)` | atalho de `tela_codigo` com `riscada=True` | `media/sketch_componentes.py` | 2026-10-30 |
| Boneco autor | `boneco_autor(d, cx, cy, s=1.4, seed=0, frac=1.0, cor=AZUL, papel=None, cor_rotulo=None)` | `cor` (A=AZUL, B=LARANJA); `papel` = rótulo embaixo | `media/sketch_componentes.py` | 2026-10-30 |
| Dupla pair | `dupla_pair(d, cx, cy, s=1.5, seed=0, frac=1.0, dist=200, papeis=None)` | dois bonecos (A azul esq, B laranja dir); `dist`; `papeis=(rotA,rotB)` | `media/sketch_componentes.py` | 2026-10-30 |
| Caixa problema | `caixa_problema(d, cx, cy, s=1.0, seed=5, frac=1.0, linhas=("o mesmo","problema"))` | caixa gelo com texto em `linhas` | `media/sketch_componentes.py` | 2026-10-30 |
| Balão de fala | `balao_fala(d, cx, cy, linhas, larg=440, alt=190, seed=31, frac=1.0, tam=50, cor_borda=INK)` | balão sem cauda; `cor_borda` diferencia A/B | `media/sketch_componentes.py` | 2026-10-30 |
| Teclado | `teclado(d, cx, cy, s=1.0, seed=60, frac=1.0)` | posição e escala | `media/sketch_componentes.py` | 2026-10-30 |
| Lupa revisão | `lupa_revisao(d, cx, cy, s=0.8, seed=61, frac=1.0)` | posição e escala | `media/sketch_componentes.py` | 2026-10-30 |
| Setas de troca | `setas_troca(d, cx, cy, s=1.0, seed=70, frac=1.0, dist=300)` | ida azul / volta laranja; `dist` | `media/sketch_componentes.py` | 2026-10-30 |
| Check solução | `check_solucao(im, d, cx, cy, s=2.4, seed=80, frac=1.0)` | recebe e devolve `im` (soma brilho verde) | `media/sketch_componentes.py` | 2026-10-30 |
| Ganho contexto | `ganho_contexto(d, cx, cy, s=1.0, seed=90, frac=1.0, rotulo="contexto")` | dois círculos sobrepostos + rótulo | `media/sketch_componentes.py` | 2026-10-30 |
| Ganho conhecimento | `ganho_conhecimento(d, cx, cy, s=1.0, seed=92, frac=1.0, rotulo="conhecimento")` | duas cabeças com setas ida/volta + rótulo | `media/sketch_componentes.py` | 2026-10-30 |
| Ganho decisão | `ganho_decisao(d, cx, cy, s=1.0, seed=97, frac=1.0, rotulo="decisao")` | check em círculo verde + rótulo | `media/sketch_componentes.py` | 2026-10-30 |
| Boneco pensando | `boneco_pensando(d, cx, cy, s=1.5, seed=14, frac=1.0, t=0.0)` | fechamento; `?` laranja pulsa com `t` | `media/sketch_componentes.py` | 2026-10-30 |
| Pirâmide de pessoas | `piramide_pessoas(d, cx, cy, s=1.0, seed=0, frac=1.0, cor=INK, dinheiro=False, colapso=False)` | 4 degraus de bonequinhos; `dinheiro` = setas amarelas sobem ao topo; `colapso` = base vermelha + rachadura | `media/sketch_componentes.py` | 2026-10-31 |
| Pilha de dinheiro | `pilha_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0)` | três notas verdes empilhadas com "R$" | `media/sketch_componentes.py` | 2026-10-31 |
| Fonte de dinheiro | `fonte_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0, modo="venda")` | `modo="venda"` caixa→moeda (verde); `modo="adesao"` recrutados→moeda (laranja) | `media/sketch_componentes.py` | 2026-10-31 |
| Convite de confiança | `convite_confianca(d, cx, cy, s=1.0, seed=0, frac=1.0)` | boneco azul passa envelope a boneco tinta; coração acima | `media/sketch_componentes.py` | 2026-10-31 |
| Ícone avestruz | `icone_avestruz(d, cx, cy, s=1.0, seed=0, frac=1.0)` | avestruz estilizado (fachada de caso real) | `media/sketch_componentes.py` | 2026-10-31 |
| Ícone gado | `icone_gado(d, cx, cy, s=1.0, seed=0, frac=1.0)` | boi estilizado com chifres e patas | `media/sketch_componentes.py` | 2026-10-31 |
| Ícone bitcoin | `icone_bitcoin(d, cx, cy, s=1.0, seed=0, frac=1.0)` | moeda amarela com "B" (cripto genérico, sem logo de marca) | `media/sketch_componentes.py` | 2026-10-31 |
| Martelo de juiz | `martelo_juiz(d, cx, cy, s=1.0, seed=0, frac=1.0)` | martelo + base (condenação) | `media/sketch_componentes.py` | 2026-10-31 |
| Caixa de caso | `caixa_caso(d, cx, cy, s=1.0, seed=0, frac=1.0, nome="", ano="", pena="")` | cartão com nome/ano/pena (textos das notas, não inventar) | `media/sketch_componentes.py` | 2026-10-31 |
| Pessoa ou dinheiro | `pessoa_ou_dinheiro(d, cx, cy, s=1.0, seed=0, frac=1.0)` | boneco azul × moeda, separados por linha pontilhada (pergunta de volta) | `media/sketch_componentes.py` | 2026-10-31 |
