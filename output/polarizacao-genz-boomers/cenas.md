# Cenas: quem lucra com a polarização geracional (Gen Z vs boomers)

Formato: SHORT vertical 9:16, ~55 s, 5 cenas. Fonte do texto: roteiro.md (só a parte narrada).

## Estilo visual do canal (sufixo fixo, colar no final de TODO prompt)

STYLE_SUFFIX = "vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration"

Regras comuns:
- Pessoas só de costas, de perfil distante, em silhueta ou com rosto fora de quadro. Nenhuma pessoa real identificável.
- Telas de celular e monitores mostram apenas formas abstratas (blocos de cor, linhas), nunca texto legível.
- Textos ("hipótese nossa", fontes, números) entram na edição como overlay, não no Flux (modelos de imagem erram texto).
- Nenhuma cena ataca ou ridiculariza uma geração. Idades variadas aparecem em pé de igualdade.

## Sinalização de conteúdo sintético
TODAS as 5 cenas são geradas por IA (Flux). As cenas 1, 2, 3 e 5 parecem fotos reais de situações genéricas, então marcar "conteúdo alterado ou sintético" no upload do YouTube. A cena 4 é uma montagem conceitual. Nenhuma cena retrata um evento real específico. Se a busca no Wikimedia Commons achar imagem livre adequada (ver `search`), ela pode substituir a gerada, e então aquela cena deixa de ser sintética.

---

## Cena 1: Gancho (0 a 6 s)
Trecho: "Quem pode ganhar quando você acha que a Geração Z e os boomers estão em guerra?"
Enquadramento: wide shot, simétrico.
Sintética: sim.

search:
1. "generation gap family dinner"
2. "people of different ages talking"
3. "smartphone social media user"

image_prompt:
Wide shot of two silhouetted people, one young adult and one older adult, standing apart on opposite sides of a quiet city plaza at dusk, each looking at a glowing smartphone, a wide empty gap of paving stones between them, long shadows, calm tense mood, seen from behind. vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration

## Cena 2: Estudo de 2025 (6 a 15 s)
Trecho: "Um estudo de dois mil e vinte e cinco mostrou que o ranking por engajamento no Twitter amplifica conteúdo emotivo e hostil ao grupo oposto."
Enquadramento: close-up / over-the-shoulder.
Sintética: sim.

search:
1. "Twitter social media feed smartphone"
2. "social media algorithm"
3. "person scrolling smartphone"

image_prompt:
Over-the-shoulder close-up of a person's hand scrolling a smartphone in a dim room, the screen showing only abstract stacked cards in red and blue tones with no readable text, a faint glow on the fingers, a laptop blurred in the background, atmosphere of constant attention and rising tension. vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration

## Cena 3: Mercado de consultoria (15 a 24 s)
Trecho: "E há um mercado: em dois mil e quinze, uma estimativa citada pela Fortune apontou de sessenta a setenta milhões de dólares gastos nos Estados Unidos com consultoria sobre millennials."
Enquadramento: medium shot, ambiente corporativo.
Sintética: sim.

search:
1. "business consulting meeting conference room"
2. "corporate workshop presentation"
3. "office meeting generations"

image_prompt:
Medium shot through a glass wall into a modern office meeting room, a small group of consultants of mixed ages seen from behind around a table, a presenter at a screen showing only an abstract bar chart with no labels, laptops and coffee cups, overcast daylight, neutral professional mood, American corporate setting, no faces visible. vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration

## Cena 4: Contraexemplo e hipótese (24 a 42 s)
Trecho: "Isso mostra incentivos, não prova uma guerra entre idades. O estudo fala de polarização política, não de idade, e nenhuma fonte que achamos mostra alguém coordenando esse conflito. Nossa hipótese: o mecanismo pode funcionar com qualquer rótulo."
Enquadramento: detail / top-down (conceitual, sugere "hipótese").
Sintética: sim, claramente conceitual (montagem de mesa de investigação). Mais fácil de perceber como ilustração, mas manter a marca.

Overlay obrigatório na edição (pedido do revisor): texto "hipótese nossa" na tela a partir de "Nossa hipótese", em fonte sóbria, canto inferior, ~4 s. Não gerar no Flux. Deixar o terço inferior do quadro livre.

search:
1. "blank labels stickers on boxes"
2. "magnifying glass on documents desk"
3. "sorting colored cards"

image_prompt:
Top-down detail shot of a clean wooden desk where many identical blank cardboard tags in different muted colors are being swapped over the same row of identical small gray figures, a hand placing one tag, a notebook and a magnifying glass at the edge, lower third of the frame left calm and empty, thoughtful investigative mood, soft window light. vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration

## Cena 5: Pergunta de volta (42 a 55 s)
Trecho: "Da próxima vez que um rótulo de geração te irritar, pergunte: o problema é a idade dessa pessoa, ou a situação em que ela vive?"
Enquadramento: medium-wide, humano e acolhedor; fecho do vídeo.
Sintética: sim.

search:
1. "grandparent and grandchild together"
2. "people of different ages working together"
3. "person looking out window thoughtful"

image_prompt:
Medium-wide shot of a young adult and an older adult sitting side by side on a small apartment balcony at golden hour, seen from behind and slightly from the side, both looking at the city skyline, one holding a coffee mug, warm light on their shoulders, quiet reflective mood, shared situation rather than conflict. vertical 9:16 composition, photorealistic documentary photography, 35mm lens, natural soft light with cool teal shadows and warm amber highlights, muted desaturated palette, shallow depth of field, fine film grain, no text, no letters, no logos, no watermark, no faces of real people, not anime, not cartoon, not illustration

---

## Resumo de tempo e estrutura

| Cena | Tempo | Bloco | Enquadramento | Sintética |
|---|---|---|---|---|
| 1 | 0-6 s | Gancho | wide | sim |
| 2 | 6-15 s | Insight (estudo) | close-up | sim |
| 3 | 15-24 s | Insight (mercado) | medium | sim |
| 4 | 24-42 s | Contraexemplo + hipótese | top-down detail | sim (conceitual) |
| 5 | 42-55 s | Pergunta de volta | medium-wide | sim |

Observações:
- Os tempos seguem os blocos do roteiro (0-5, 5-22, 22-42, 42-52) e se estendem até ~55 s para a pausa final. Ajustar após a gravação da voz.
- Se a narração passar de 60 s, o roteiro manda cortar a frase da Fortune; nesse caso remover a cena 3 e estender a cena 2 até 22 s.
- Contagem dos prompts: cada image_prompt tem entre 40 e 70 palavras na parte descritiva mais o sufixo de estilo; se a API limitar o tamanho, colar o sufixo como `style` separado.
- Cenas 2 e 3 não mostram marca (Twitter/X, Fortune); a fonte aparece só na fala e em overlay.
