# Prompt de imagem — Squad do canal (escalação dos agentes)

Objetivo: uma imagem visual, estilo "escalação de time de futebol", mostrando cada agente do canal como um jogador real, com o rosto/foto real do craque e o papel dele na equipe.

> ⚠️ Uso pessoal/interno. A imagem usa semelhança de pessoas reais (jogadores). Não use para passar por conteúdo oficial de clube, seleção ou do jogador, nem para fins comerciais sem direitos.

---

## Mapa craque → papel na squad

| Posição tática | Craque | Agente | Papel no canal |
|---|---|---|---|
| Goleiro | Thibaut Courtois | courtois-revisor-fatos | Revisor de fatos (última defesa contra erro) |
| Zagueiro / Auditor | Vinícius Júnior | vini-auditor-conformidade | Auditor de conformidade YouTube |
| Volante criativo | Luka Modrić | modric-pesquisador-tema | Pesquisador de tema (fontes) |
| Lateral explorador | Erling Haaland | haaland-pesquisador-nicho | Pesquisador de nicho e pautas |
| Maestro / Armador | Kevin De Bruyne | debruyne-orquestrador | Orquestrador (comanda a jogada) |
| Meia camisa 10 | Lionel Messi | messi-estrategista-angulo | Estrategista de ângulo e tese |
| Meia-atacante | Michael Olise | olise-diretor-arte | Diretor de arte (cenas e imagens) |
| Ponta criativo | Neymar | neymar-roteirista | Roteirista |
| Ponta veloz | Kylian Mbappé | mbappe-editor-metadados | Editor de metadados (título, thumb, tags) |
| Centroavante / Finalizador | Cristiano Ronaldo | cristiano-otimizador-viral | Otimizador viral (deixa premium pra viralizar) |

---

## PROMPT (colar no gerador de imagem — Flux, Midjourney, etc.)

```
A premium sports-broadcast "starting eleven" lineup graphic for a faceless YouTube channel's AI agent team, vertical poster layout, dark cinematic studio background with subtle stadium bokeh and soft volumetric spotlights. Eleven realistic professional football player portraits arranged in a classic team formation (one goalkeeper at the bottom, a defensive line, a midfield line, and an attacking line at the top), each player shown from chest up with a photorealistic real-face portrait, confident studio lighting, shallow depth of field.

Each player sits inside a sleek glass-and-neon name card showing, in clean modern sans-serif:
- GK — Courtois — "Revisor de Fatos"
- DEF — Vini Jr — "Auditor de Conformidade"
- MID — Modric — "Pesquisador de Tema"
- MID — Haaland — "Pesquisador de Nicho"
- MID — De Bruyne — "Orquestrador" (captain armband, central, slightly larger)
- ATT — Messi — "Estrategista de Ângulo"
- ATT — Olise — "Diretor de Arte"
- ATT — Neymar — "Roteirista"
- ATT — Mbappé — "Editor de Metadados"
- ATT — Cristiano Ronaldo — "Otimizador Viral" (top center, hero spotlight, golden rim light)

Color grade: deep teal shadows, warm amber highlights, muted premium palette, fine film grain, high production value, 4k, sharp focus, realistic skin texture, esports/matchday poster aesthetic. Portuguese (pt-BR) role labels exactly as written, legible, no spelling errors, no watermark, no logos of real clubs.

Aspect ratio 9:16.
```

---

## Variações rápidas
- **Horizontal (capa/thumbnail):** troque a última linha por `Aspect ratio 16:9.`
- **Sem usar rostos reais (mais seguro):** troque `photorealistic real-face portrait` por `stylized silhouette / jersey with number, no recognizable real face` e remova os nomes dos jogadores, deixando só os papéis.
- **Com bola/escudo do canal:** acrescente `a central emblem reading "CANAL DARK" above the formation`.

## Observações
- Modelos de imagem erram texto. Se os rótulos saírem tortos, gere sem texto e adicione os nomes/papéis depois na edição (Canva/Figma).
- Semelhança de pessoas reais: para publicar algo público, prefira a variação "sem rostos reais".
