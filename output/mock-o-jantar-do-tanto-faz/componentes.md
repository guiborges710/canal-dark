# Componentes — O jantar do tanto faz

Status: aguardando validação do Guilherme  
Estilo: `cartoon_alive` por camadas  
Paleta única: `tijolo`

## Paleta fixa (6 cores)

| Papel | Cor |
|---|---|
| `fundo` | `#E8704A` |
| `claro` | `#FFF1DC` |
| `contorno` | `#241518` |
| `pele` | `#F4B98A` |
| `destaque` | `#FFD23F` |
| `apoio` | `#1F6F8B` |

Todos os nomes abaixo existem em `media/cartoon_lib.py`. Não há desenho externo, mídia de terceiros nem componente de sketch.

## Elenco recorrente original

| Papel na história | Nome exato da biblioteca | Poses | Expressões | Direção de atuação |
|---|---|---|---|---|
| Pessoa que tenta escolher o jantar | `bia` | `aponta`, `segura`, `maos_cintura`, `medo` | `brava`, `pensativa`, `medo`, `risada` | Cansaço virando irritação; é quem ameaça pedir comida com o ex e dá a resposta final. |
| Pessoa do “tanto faz” | `teo` | `ombros`, `pensando`, `medo`, `aponta` | `surpresa`, `brava`, `pensativa`, `medo` | Rejeita cada opção como ataque pessoal e termina ofendido com a pizza. |

Usar `bia` e `teo` nas seis cenas, sem trocar o elenco. `fala: true` somente no personagem da fala em curso; piscar e respirar ficam por conta da biblioteca.

## Cenários e objetos

| Componente | Nome exato | Uso |
|---|---|---|
| Sala do casal | cenário `sala` | Base das cenas 1, 2, 4 e 6. Cenário simples; janela, quadro e sofá já vêm da biblioteca. |
| Bancada de entrevista | cenário `escritorio` | Cena 5; a mesa nativa vira a bancada de avaliação. |
| Insert acelerado | cenário `liso` | Cena 3; fundo limpo para as rejeições rápidas. |
| Celular com pedido | objeto `celular` | Cena 2, segurado por `bia`, sempre com `texto: "PEDIR JANTAR"`. |
| Caixa de pizza | objeto `caixa` | Cena 6; caixa grande, inclinada, acompanhada do texto curto `PIZZA`. É a representação permitida pela biblioteca. |
| Sinais de rejeição | objetos `raio`, `exclamacao`, `interrogacao` | Pontuam a ameaça, as recusas e a pausa antes de “Nada”. |
| Ironia com carinho | objeto `coracao` | Cena 4, pequeno e afastado dos rostos. |
| Textos-chave | camada `textos` | Somente `TANTO FAZ`, `REPROVADO`, `PIZZA`, `JAPONÊS?` e `HAMBÚRGUER?`; todos com até 26 caracteres. |

Observação: `media/cartoon_lib.py` não possui pratos nem campainha. Para não inventar arte fora da biblioteca, as opções são inserts tipográficos com sinais gráficos; a campainha é tratada no som e por `exclamacao`.

## Layout por cena para o Olise

Coordenadas em pixels no quadro 1080×1920. Personagens ficam com os pés em `y: 1440`; textos ficam entre `y: 190` e `y: 1500`.

| Cena | Componentes exatos | Posição e escala sugeridas | Regra de composição e movimento |
|---|---|---|---|
| 1 — Gancho | `sala`; `bia` (`aponta` + `brava`); `teo` (`neutra` + `surpresa`); `exclamacao`; texto `TANTO FAZ` | `bia` x=330, escala=1.05, olha=`dir`; `teo` x=800, escala=1.02, olha=`esq`; texto x=540,y=300,tam=108; `exclamacao` x=760,y=670,escala=.65 | Começar já com os dois na tela. Zoom brusco no rosto de `teo` após a ameaça, sem o texto descer sobre as cabeças. |
| 2 — A fome | `sala`; `bia` (`segura` + `pensativa`), segurando `celular`; `teo` (`ombros` + `brava`); texto `PIZZA?`; `raio` | `bia` x=320, escala=1.0; `teo` x=800, escala=1.0; celular com `texto: "PEDIR JANTAR"`; `PIZZA?` x=540,y=300,tam=118; `raio` x=540,y=670,escala=.55 | O celular fica junto à mão de `bia`, nunca solto sobre o corpo. A palavra `PIZZA?` sai antes do corte. |
| 3 — Rejeições | `liso`; `bia` (`aponta` + `brava`); `teo` alterna `pensando`/`medo` e `pensativa`/`medo`; textos `JAPONÊS?` e `HAMBÚRGUER?`; `raio` | `bia` x=280, escala=.95; `teo` x=810, escala=1.02; textos x=540,y=280 e x=540,y=500,tam=86; `raio` x=540,y=760,escala=.48 | Mostrar uma opção por vez: `JAPONÊS?` deve sair antes de `HAMBÚRGUER?` entrar. Whoosh em cada troca; nenhum texto sobre os rostos. |
| 4 — A armadilha | `sala`; `bia` (`maos_cintura`/`aponta` + `brava`); `teo` (`ombros` + `feliz`→`surpresa`); texto `TANTO FAZ`; `coracao` | `bia` x=320, escala=1.02; `teo` x=800, escala=1.02; texto x=540,y=300,tam=112; coração x=540,y=620,escala=.48 | O coração entra e sai rápido como ironia. Manter o centro livre depois dele para a troca de pose. |
| 5 — A entrevista | `escritorio`; `bia` (`maos_cintura` + `brava`); `teo` (`pensando` + `pensativa`→`medo`); texto `REPROVADO`; `interrogacao` | `bia` x=280, escala=.92; `teo` x=810, escala=.94; `REPROVADO` x=540,y=300,tam=106; `interrogacao` x=820,y=680,escala=.48 | A mesa nativa é a bancada. Segurar pausa antes de “Nada”; `interrogacao` sai antes do carimbo visual `REPROVADO`. |
| 6 — A entrega | `sala`; `bia` (`medo` + `medo`→`brava`), `teo` (`aponta` + `surpresa`→`brava`); `caixa`; texto `PIZZA`; `exclamacao` | `bia` x=220, escala=.98; `teo` x=860, escala=.98; `caixa` x=540,y=1290,escala=1.1,rot=-12; `PIZZA` x=540,y=300,tam=118; `exclamacao` x=540,y=650,escala=.5 | A caixa fica entre os dois, sem cobrir rostos ou troncos. Inclinar a caixa e deslocar `bia` alguns pixels para baixo sugere o peso. Terminar seco na pose final; `saida: loop` só se a retomada para o gancho ficar limpa. |

## Regras obrigatórias de composição

- Nada cobre personagem; objetos e textos ficam fora das caixas de cabeça e tronco.
- Nada cobre texto ainda em leitura. Um elemento novo só ocupa a mesma região depois que o anterior sair.
- No máximo uma ideia visual dominante por cena.
- Textos ficam dentro da área segura (`SEGURO_TOPO` até `SEGURO_BASE`) e usam frases curtas.
- Manter a paleta `tijolo` em todas as cenas; nenhuma cor externa.
- Manter `bia` e `teo` nas seis cenas; variar apenas pose e expressão.
- O celular nunca pode aparecer vazio: usar exatamente `PEDIR JANTAR`.
- Cortes rápidos entre falas; pequenos zooms e trocas de pose mantêm movimento constante.
- A caixa da cena 6 não pode tapar `bia`, `teo` nem `PIZZA`.

## Arquivos de validação

- Contato geral: `output/mock-o-jantar-do-tanto-faz/componentes/contato.jpg`
- Layout das seis cenas: `output/mock-o-jantar-do-tanto-faz/componentes/cenas_exemplo.jpg`
- Previews isolados: `elenco_bia.png`, `elenco_teo.png`, `cenario_sala.png`, `cenario_escritorio.png`, `celular_pedir_jantar.png`, `caixa_pizza.png`, `sinais_rejeicao.png`, `textos_chave.png`

Fase atual em `componentes/aprendizados.md`: `aprendendo`. **Olise** deve aguardar a validação do Guilherme antes de montar `cenas.json`.
