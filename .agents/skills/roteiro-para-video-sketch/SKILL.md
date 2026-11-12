---
name: roteiro-para-video-sketch
description: Transforma um roteiro (com falas por cena) num vídeo vertical no estilo sketch, desenhado à mão em folha de caderno pautada, sem legendas na base e conduzido pela narração. Use quando o Olise (ou o Guilherme) mandar um roteiro e quiser o vídeo nesse estilo. Turns a script into a vertical hand-drawn notebook-paper explainer video, timed to the narration.
---

# Roteiro para vídeo sketch

Esta skill transforma um roteiro num Short desenhado à mão: papel de caderno off-white pautado, traço de caneta tremido, ícones simples (objetos, boneco de palito, sol, gráficos de barras) e brilhos suaves. O resultado é **original**: nunca copie personagens, logos, quadros, música ou narração de outro vídeo. Desenhe objetos e personagens próprios.

No canal, quem usa esta skill é o **Olise** (`olise-diretor-arte`). O código que desenha e renderiza já existe no projeto; o Olise só escreve **o que desenhar em cada cena**.

## Peças do projeto (já prontas)

| Arquivo | Para quê |
|---|---|
| `media/sketch_lib.py` | Papel, traço tremido, brilho, texto e os ícones. É tudo o que o Olise importa. |
| `media/sketch.py` | Valida o `cenas.json`, **gera a narração primeiro**, mede cada fala, desenha cada cena no tempo dela e codifica o MP4. |
| `output/<slug>/cenas.json` | A lista de cenas (fala, mínimo de duração, nome da função de desenho, rótulos, sons). Contrato abaixo. |
| `output/<slug>/sketch_cenas.py` | As funções de desenho `cena_0`, `cena_1`... escritas pelo Olise. |

## Especificação de saída (fixa)

- Formato: 1080×1920 (vertical 9:16), **30 fps** (perfil do canal), H.264, yuv420p, crf 18, faststart, áudio AAC. A codificação é a mesma do estilo SVG (`media/motion.py`).
- **Sem legendas na base.** Nunca escreva uma frase ao longo da parte de baixo do quadro. O texto na tela é só rótulo curto (uma palavra-chave ou, onde o roteiro trouxer, um número) e, se o roteiro pedir, um título curto no topo. Cada rótulo tem no máximo 26 caracteres.
- **Narração obrigatória**, com a voz do Guilherme. O vídeo é feito **em cima do áudio**: a cena dura o que a fala dura. Esta skill nunca entrega vídeo mudo (o modo `--sem-voz` existe só para testar o desenho).
- Idioma dos rótulos: o do roteiro (pt-BR).
- Conteúdo fica entre `SEGURO_TOPO` (190) e `SEGURO_BASE` (1500): o topo e a base do Short ficam cobertos pela interface do app.

## Identidade visual

- Fundo: papel (246, 244, 236). Pauta azul (190, 206, 226) a cada 64 px, a partir de y=140, com 3 px. Margem vermelha (232, 150, 150) em x=150. Tudo isso já sai de `papel()`.
- Tinta: (28, 28, 34). Traço à mão: um ponto a cada ~10 px, tremido ±2,5 px, **seed fixa por elemento** (o tremido não pula entre quadros). Espessura 5 a 7 px.
- Preenchimentos chapados e claros: azul-gelo, ferro, amarelo-sol, laranja, e o âmbar da cerveja. Raios invisíveis e alertas em vermelho escuro.
- Brilhos: `brilho()` soma um halo suave; a força sobe com a temperatura ou a luz.
- Ícones grandes: o quadro tem 1080×1920 e o celular é pequeno. Use escalas de 1,3 a 2,5 e ocupe a área segura; ícone minúsculo some no feed.

## Regras de movimento

- Todo objeto entra escalonado (0,3 a 0,4 s), ou tem o contorno desenhado aos poucos (`frac`). Use `entra(lt, t0)` para o contorno e `mola(lt, t0)` para a escala com estouro.
- Raios e brilhos pulsam com `sin(tempo)`: o desenho precisa parecer vivo. Chamas e luzes: `tremer(lt)`.
- Gráfico no máximo uma vez por vídeo, só se a forma dele for a ideia (regra de `prompts/tipos_de_roteiro.md`). As barras crescem em sequência (`barras(...)` já faz isso).
- **Corte seco entre cenas**, sem fusão. O `sketch.py` põe um whoosh em cada corte; use `sons` para um ding quando um número aparecer.
- A primeira cena entra em movimento no quadro 0: a ideia mais forte do gancho já está desenhada, não um papel em branco. Nenhuma cena fica parada: sempre há algo entrando, crescendo ou pulsando.

Leia também `output/<slug>/componentes.md` (do **Raphinha**) quando existir: componentes aprovados e regras de layout (nada cobre boneco nem texto).

## Passo a passo (para o Olise)

1. **Leia** `direcao_viral.md` (seção `## Narração`, com a fala de cada cena e o ritmo), `roteiro.txt` e `angulo.md`. Cada fala vira uma cena. Uma ideia visual por cena. Um Short de 40 s tem 5 a 8 cenas; fale pouco por cena.
2. **Mapeie cada cena para um desenho original**: use os ícones da biblioteca para mostrar a situação (boneco fazendo a ação, copo para o hábito de beber, boneco para a geração, casa/moeda/celular/relógio para o contexto, balão para a pergunta de volta). O dado principal da cena aparece como número grande ou barra. Nada de legenda.
3. **Escreva `cenas.json`** (contrato abaixo). A `fala` é o texto exato da seção `## Narração`, sem alterar nada.
4. **Escreva `sketch_cenas.py`**: uma função `cena_N(lt, dur)` por cena, que devolve uma imagem. Comece com `from PIL import ImageDraw` e `from media.sketch_lib import *`. Veja o exemplo abaixo.
5. **Confira o desenho**: rode `python -m media.sketch --slug <slug> --previa`. Ele cria `output/<slug>/previa.jpg` (3 quadros por cena, duas cenas por linha). Abra e corrija: elemento cortado, rótulo sobre desenho, texto na base, ícone pequeno, cena vazia.
6. **Renderize** (quem faz é o orquestrador): `python run.py video --topic "<tema>"`. O `run.py` percebe o estilo sketch, gera a narração, desenha no tempo da fala e codifica.

## Contrato do `cenas.json`

```json
[
  {"tipo": "sketch", "desenho": "cena_0", "duracao": 3,
   "fala": "Texto exato da narração desta cena.",
   "rotulos": ["54%"],
   "sons": [{"t": 1.2, "tipo": "ding"}]}
]
```

- `tipo`: sempre `"sketch"`. `desenho`: nome da função em `sketch_cenas.py`.
- `duracao`: **mínimo** em segundos (≥ 2,5); a cena dura o que a fala dura, com respiro curto.
- `rotulos` (opcional): os textos que aparecem na tela, ≤ 26 caracteres cada (serve à auditoria do **Vini**).
- `sons` (opcional): `{"t": segundo dentro da cena, "tipo": "ding" | "impact" | "whoosh"}`.
- Duração total entre 20 e 60 s (alvo do canal: 30 a 60 s).

## Biblioteca (`media/sketch_lib.py`)

Tempo: `entra(lt, t0, dur)`, `mola(lt, t0)`, `pulso(lt)`, `tremer(lt)`. Base: `papel()`, `texto(d, x, y, s, tam)`, `texto_multilinha`, `traco`, `circ`, `brilho`. Ícones: `pessoa`, `grupo_pessoas`, `copo`, `garrafa`, `casa`, `moeda`, `celular`, `relogio`, `coracao`, `sol`, `seta`, `cruz`, `check`, `lupa`, `calendario`, `balao`, `barras`. Cores: `INK, AZUL, LARANJA, CERVEJA, VERDE, GELO, FERRO, SOL_AMARELO, VERMELHO`.

Se faltar um ícone para a ideia, **combine** os que existem com `traco(...)` e `circ(...)` direto na função da cena. Não copie desenho de personagem conhecido.

### Exemplo de cena

```python
from PIL import ImageDraw
from media.sketch_lib import *

def cena_1(lt, dur):
    im = papel(); d = ImageDraw.Draw(im)
    texto(d, 540, 300, "Adultos que bebem", 66)
    barras(d, 540, 1200, [{"rotulo": "2023", "valor": 62, "texto": "62%", "cor": AZUL},
                          {"rotulo": "2025", "valor": 54, "texto": "54%", "cor": LARANJA}],
           escala_max=70, lt=lt, t0=0.3, seed=5)
    return im
```

A função depende só de `lt` e `dur`: o mesmo `lt` dá sempre o mesmo quadro. Se usar `random`, sempre com seed fixa.

## Barra de qualidade

- Todo quadro tem papel, tinta e pelo menos um objeto desenhado. Nenhum quadro vazio, exceto nos primeiros 0,2 s de uma cena.
- Nenhuma legenda ou frase na base do quadro. Rótulos dentro do quadro e sem sobrepor o desenho.
- Os números na tela são exatamente os do `roteiro.txt` e de `notas.md`.
- O vídeo é original: nada de personagem, logo, quadro ou áudio copiado.
- O vídeo entrega o que o gancho promete e o tema é o do próprio vídeo (regra do canal).
