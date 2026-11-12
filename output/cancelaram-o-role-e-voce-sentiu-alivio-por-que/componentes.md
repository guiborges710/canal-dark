# Componentes: Cancelaram o rolê e você sentiu alívio

Status: **aguardando validação do Guilherme** (fase "aprendendo"; o **Olise** só começa depois da aprovação).
Estilo: `cartoon_alive`. Paleta única: `noite`, em todas as cenas.

- Ver todos os componentes: `componentes/contato.jpg`
- Ver o layout de cada momento: `componentes/cenas_exemplo.jpg`
- Refazer as imagens e o checador: `.venv\Scripts\python output\cancelaram-o-role-e-voce-sentiu-alivio-por-que\componentes_gerar.py`

Tudo sai de `media/cartoon_lib.py`, o mesmo código do render. O `cenas.json` usa os nomes da biblioteca, não os PNGs. As specs exatas de cada cena estão em `LAYOUT`, no `componentes_gerar.py`. Os `t` de lá são exemplos: acerte pelo áudio.

## Decisões a confirmar

1. **A fala vem do `roteiro.txt`, não da `## Narração`.** O `roteiro.txt` aprovado é mais novo que a `direcao_viral.md` e tem outro texto na abertura, no rótulo e no fim. Principal diferença: a pergunta final é "alívio pra descansar, ou de ver pessoas?", e a direção ainda diz "descansar ou fugir?". Por isso não uso o texto "descansar ou fugir?" nem o ícone de porta. A skill manda tirar a `fala` da `## Narração`, então esse conflito precisa ser resolvido antes do `cenas.json`.
2. **Grafia de "rolê".** O `roteiro.txt` traz "role", sem acento. Na tela vale "rolê". O roteiro está congelado e não foi alterado.
3. **Elenco trocado.** Léo e Duda, da direção, não existem na biblioteca. Léo vira `teo` e Duda vira `bia`. O nome nunca aparece na tela nem na fala.
4. **Paleta `noite`.** É a única em que o `teo` veste amarelo, como a direção pede. Combina com a hora do rolê e a janela fica acesa. A parede é azul-escura, então o "tom quente" fica só na janela, no sofá e na camiseta. Se o tom quente pesar mais, a alternativa é `tijolo`, com `teo` de camiseta azul-petróleo.
5. **Falta na biblioteca, com substituto:**

| A direção pede | Não existe | Uso no lugar |
|---|---|---|
| Jaqueta, pijama, cobertor | figurino por cena | Mesma camiseta; a mudança fica na pose e na expressão |
| Sentado no sofá | pose sentada | Em pé na frente do sofá do cenário `sala` |
| Polegar digitando | mão em close | `teo` segurando o celular, com a mensagem legível |
| Copo na mão | objeto copo | Balão "bora!" com a pose `comemora` |
| Balão de pensamento desinflando | balão de pensamento | Balão de fala comum |
| Agenda cheia da Duda | objeto agenda | `relogio` (última hora) e `raio` (impulso) |
| Ícones de sofá e porta | ícones soltos | `casa` (descansar) e `bia` + `zeca` pequenos (ver pessoas) |

6. **Textos além da lista da direção.** Propostos para o vídeo se sustentar sem som, todos com palavras do roteiro: `ALÍVIO`, `UFA!`, `NÃO EXPLICA TUDO` e os balões "ficar de fora", "ansiedade social" e "cansaço e ansiedade". São ilustrativos, sem número e sem dado novo: "bora!" e as mensagens do celular.
7. **Duração.** O roteiro tem 127 palavras, então deve passar bem dos 30 s pedidos (na revisão do **Courtois**, cerca de 110 palavras davam ~35 s). Dentro do limite de 60 s, mas fora do alvo. O corte não é meu: o layout está dividido por frase e acompanha o áudio.

## Paleta fixa `noite` (6 cores)

| Papel | Cor | Onde aparece |
|---|---|---|
| `fundo` | `#24305E` | Parede |
| `claro` | `#F4F1E8` | Chão, balões, tela do celular |
| `contorno` | `#10101C` | Traço, calça do `teo` |
| `pele` | `#E9A178` | Pele |
| `destaque` | `#FF5A5F` | Sofá, cabelo do `teo`, roupa da `bia`, texto principal |
| `apoio` | `#FFB627` | Camiseta do `teo`, janela, suor |

## Elenco (personagens originais do canal)

| Papel | `id` | Pose + expressão (imagem em `componentes/`) |
|---|---|---|
| Protagonista, "você" | `teo` | `segura`+`feliz` (`elenco_teo_pronto`); `ombros`+`risada` (`elenco_teo_alivio`); `maos_cintura`+`pensativa` (`elenco_teo_desconfiado`); `segura`+`neutra` (`elenco_teo_digita`); `comemora`+`risada` (`elenco_teo_empolgado`); `triste`+`triste` (`elenco_teo_peso`); `medo`+`medo` (`elenco_teo_ansioso`); `neutra`+`triste` (`elenco_teo_cansado`); `neutra`+`feliz` (`elenco_teo_sereno`); `ombros`+`neutra` (`elenco_teo_de_ombros`); `pensando`+`pensativa` (`elenco_teo_pensando`) |
| Amiga; quem adia e se distrai | `bia` | `neutra`+`feliz` (`elenco_bia_amiga`); `pensando`+`pensativa` (`elenco_bia_distraida`); `medo`+`medo` (`elenco_bia_apressada`) |
| Vizinho que rotula | `zeca` | `aponta`+`brava` (`elenco_zeca_aponta`); `neutra`+`feliz` (`elenco_zeca_neutro`) |

## Cenários e objetos

| Componente | Nome na biblioteca | Parâmetro exato | Imagem |
|---|---|---|---|
| Sala, base do vídeo | cenário `sala` | | `cenario_sala` |
| Rua, cena do rótulo | cenário `rua` | | `cenario_rua` |
| Quarto, cena da mensagem | cenário `quarto` | | `cenario_quarto` |
| Fundo limpo, cena do "contexto" | cenário `liso` | | `cenario_liso` |
| Celular: convite | `segura` tipo `celular` | `texto: "hoje tem rolê!"`, `escala: 0.95` | `celular_convite` |
| Celular: cancelamento | `segura` tipo `celular` | `texto: "galera, hoje não rola"`, `escala: 0.95` | `celular_cancelou` |
| Celular: desculpa | `segura` tipo `celular` | `texto: "não vou, foi mal"`, `escala: 0.95` | `celular_desmarca` |
| Calendário | `calendario` | `texto: "hoje"` (em minúsculas: "HOJE" encosta na borda) | `objeto_calendario` |
| Suor, relógio, raio, coração, casa | `suor`, `relogio`, `raio`, `coracao`, `casa` | | `objeto_*` |

`cenario_escritorio` foi testado e descartado: a tela de fundo disputava com o texto da cena do "contexto". `lu` não entra.

## Layout por cena

Pés sempre em `y: 1440`. A primeira coluna é a ordem das cenas no vídeo. Na cena 2 a pose muda em "alívio" e nas cenas com seta muda na palavra indicada.

| # | Fala (`roteiro.txt`) | Cenário | Personagens: x, escala, pose + expressão | Objetos, balões e textos |
|---|---|---|---|---|
| 1 | Chegou na hora do rolê! | `sala` | `teo` x=300, 1.3, `segura`+`feliz`, com celular convite | Sem objeto solto; tremida da câmera (`forca` ~22) desde o início, para o celular vibrar já no frame 0 |
| 2 | Aí alguém cancelou... e o que bateu foi alívio. | `sala` | `teo` x=300, 1.3, `segura`+`surpresa` → `ombros`+`risada`, com celular cancelamento | `ALÍVIO` x=540, y=290, tam=130, `destaque`, entra com a palavra |
| 3 | Andam dizendo que essa geração não sabe o que é compromisso. | `rua` | `teo` x=250, 1.05, `maos_cintura`+`pensativa`; `zeca` x=830, 1.05, olha `esq`, `aponta`+`brava` | Balão de `zeca` "sem compromisso?" x=640, y=620 |
| 4 | Não é bem isso. Primeiro: hoje desmarcar custa quase nada. Uma mensagem, sem ligar. | `quarto` | `teo` x=300, 1.3, `segura`+`neutra` → `segura`+`feliz`, com celular desculpa | Nenhum |
| 5 | E dizer sim também é fácil: muita gente aceita no impulso e só sente o peso quando o dia chega. | `sala` | `teo` x=400, 1.1, `comemora`+`risada` → `triste`+`triste` em "peso" | Balão "bora!" x=770, y=860, sai antes do calendário; `calendario` x=400, y=440, 1.25, entrada `queda`; `suor` x=700, y=880, 1.8 |
| 6 | Segundo: o alívio. Um estudo com adultos ligou o prazer de ficar de fora à ansiedade social. | `sala` | `teo` x=360, 1.1, `neutra`+`feliz` → `medo`+`medo` em "ansiedade" | Balão "ficar / de fora" x=790, y=830, sai; balão "ansiedade / social" no mesmo lugar; `suor` x=105, y=950, 1.8 |
| 7 | Nossa leitura: muitas vezes é cansaço e ansiedade, não desprezo pelos amigos. | `sala` | `teo` x=290, 1.05, `neutra`+`triste` → `neutra`+`feliz` em "amigos"; `bia` x=800, 1.05, olha `esq`, `neutra`+`feliz` | Balão "cansaço / e ansiedade" x=540, y=300; `coracao` x=545, y=760, 0.7, em "amigos" |
| 8 | Mas contexto não explica tudo. Outro estudo, com jovens, ligou cancelar de última hora à impulsividade e a empurrar decisões. | `liso` | `bia` x=290, 1.0, `pensando`+`pensativa` → `medo`+`medo` em "impulsividade"; `teo` x=800, 1.0, olha `esq`, `ombros`+`neutra` | `CONTEXTO` y=270, tam=112, `destaque`; `NÃO EXPLICA TUDO` y=390, tam=88, `claro`; `relogio` x=170, y=775, 0.55, em "última hora"; `raio` x=410, y=775, 0.55, em "impulsividade" |
| 9 | Então volte à cena. O celular vibra... galera, hoje não rola. Ufa que alívio. | `sala` | `teo` x=300, 1.3, `segura`+`feliz` → `ombros`+`risada` em "ufa", com celular cancelamento | `UFA!` x=540, y=290, tam=130, `apoio`; tremida da câmera (`forca` ~22) em "vibra" |
| 10 | Agora a pergunta é: alívio pra descansar, ou de ver pessoas? | `sala` | `teo` x=470, 1.05, `pensando`+`pensativa`; `bia` x=780, 0.6, olha `esq`, `neutra`+`feliz`; `zeca` x=985, 0.6, olha `esq`, `neutra`+`feliz` | `ALÍVIO PRA DESCANSAR` y=235, tam=88, `claro`; `OU DE VER PESSOAS?` y=355, tam=88, `destaque`; `casa` x=130, y=1360, 0.55 |

Som e transição (sugestão): impacto no cancelamento (cena 2) e na queda do calendário (cena 5); corte seco entre as cenas, como pede a direção. A cena 10 pode fechar em `"saida": "loop"`, porque a cena 1 tem o mesmo cenário.

## Regras de composição

Do `componentes/aprendizados.md`, valendo para este vídeo:
- **Nada cobre personagem.** Tela, texto, seta ou balão não tapam boneco.
- **Nada cobre texto.** Se um elemento novo entra no mesmo lugar, o anterior sai antes (use `ate`). Vale para os balões das cenas 5 e 6.
- **Celular sempre com texto coerente com a cena.** Nunca tela vazia.
- **Método aprovado:** contato rotulado, `cenas_exemplo.jpg` e checador de sobreposição.

Deste vídeo:
- **Área do texto livre:** `y` de 190 a 460 só para textos e balão, sem objeto nem personagem. Exceção: o `calendario` da cena 5, que não divide o espaço com texto.
- Texto sempre entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500).
- No máximo uma ideia visual por momento.
- **Celular na mão, nunca solto:** `escala: 0.95` com `teo` a 1.3. Com o aparelho maior, ele encosta na cabeça. O texto do `segura` não muda dentro da cena, por isso o convite e o cancelamento são cenas separadas.
- **Suor em fundo azul:** o `suor` é âmbar e some em cima da janela, também âmbar. Mantenha as posições da tabela.
- **Zoom:** o checador rodou com a câmera parada. Texto e balão acompanham a câmera em ritmos diferentes, então só use zoom nas cenas 1 e 4, que não têm texto. Em qualquer outra, confira a `previa.jpg`.

## Conferência

O checador isola cada elemento por diferença de pixels entre quadros reais da biblioteca, com folga de 8 px, nos 18 momentos de `cenas_exemplo.jpg`. Resultado: **0 sobreposições** entre personagem, objeto, balão e texto, e nenhum celular encostando na cabeça. Todas as cenas passaram no `validar` da biblioteca.

Limites: as entradas animadas (como a queda do calendário) e os movimentos de câmera não foram testados, e a fala real pode mudar os tempos. O botão do celular sai um pouco irregular; isso vem da biblioteca, não fui eu que alterei, e é pequeno na tela.
