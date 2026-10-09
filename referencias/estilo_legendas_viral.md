# Estilo de legenda viral — referências e receita

> **Para o Cristiano:** transforme a seção "RECEITA RECOMENDADA" (no fim) em spec técnica para o engenheiro (`media/captions.py`, `caption_size`, `caption_y`, cores, fonte).
> **Coleta:** 2026-10-09 (**Memphis**). Números mudam; re-coletar a cada rodada.

## Aviso de método (leia antes de usar)
Nesta rodada eu **não consegui inspecionar frames dos vídeos** (sem download, sem visão de vídeo; só WebSearch/WebFetch). Por isso:
- **Métricas (views/likes):** vêm do acervo já coletado com `yt-dlp` em 2026-10-08 (`referencias/referencias_nicho.md`). Onde não há número público confiável, está "n/d".
- **Detalhes de legenda:** vêm de tutoriais/documentação das ferramentas que criam esses estilos (CapCut, Submagic, Kapwing, guias de fontes) e de convenções do gênero. Cada item está marcado: **[FONTE]** = descrito em material consultado; **[CONVENÇÃO]** = padrão comum do gênero, não confirmado em frame; **[VERIFICAR]** = precisa de 5 prints do vídeo real para confirmar.
- Não há spec oficial do Hormozi: tudo é engenharia reversa de terceiros, e as fontes divergem em alguns pontos (indicado abaixo).

---

## Referências

### 1. Estilo "Hormozi" (internacional, referência canônica)
| Campo | Valor |
|---|---|
| Nome do vídeo | Shorts do canal (clipes recortados de conteúdo longo; sem vídeo único eleito) |
| Perfil | @AlexHormozi |
| Views / Likes | n/d por vídeo (análise de terceiros estima 4,3 mi de inscritos e ~1,1 bi de views no canal; Shorts ~91% das views, estimativa) |
| Link | https://www.youtube.com/@AlexHormozi/shorts |

Estilo da legenda:
- **Palavras por vez:** 2-4 (maioria das fontes); uma fonte cita até 4-6 em 2 linhas. Palavra única usada como ênfase. **[FONTE, divergente]** Adotar 2-3.
- **Karaokê:** sim, a palavra falada/chave muda de cor; texto base branco. Realce em **amarelo** (ex.: #F7C204), **verde** (dinheiro/ganho) e **vermelho** (erro/alerta). **[FONTE]**
- **Fonte:** The Bold Font (clássico), Montserrat Black/ExtraBold 900 ou Anton (versão mais nova); **MAIÚSCULA**. **[FONTE, divergente na família]**
- **Contorno/sombra:** branco com contorno preto grosso OU sombra forte sem contorno (versão clássica: sombra, sem obrigação de contorno). Sombra CapCut citada: opacidade 100%, blur 70%, distância 14%. **[FONTE]**
- **Posição:** meio/meio-inferior do quadro, longe da UI (Kapwing: "lower-middle", canvas 1080x1920). **[FONTE]**
- **Animação:** pop-in (escala/baixo para cima) a cada bloco; palavra-ênfase 2-4 pt maior; emoji animado ocasional; "swoosh" sonoro baixo no início da animação. **[FONTE]**
- **Largura:** ~70-85% da largura útil, 2 linhas no máximo (Premiere: ~15 caracteres por linha). **[FONTE/CONVENÇÃO]**
- **Por que retém:** o olho segue a palavra colorida, que reafirma o ritmo da fala e impede a "cegueira de bloco de texto".

### 2. CapCut "karaokê" por palavra (internacional, técnica)
| Campo | Valor |
|---|---|
| Nome do vídeo | Tutorial/template "Hormozi captions" CapCut (guia, não Short viral) |
| Perfil | n/d (guia de terceiros, Lilys/CapCut) |
| Views / Likes | n/d |
| Link | https://lilys.ai/en/notes/create-youtube-shorts-20260115/capcut-hormozi-captions |

Estilo da legenda (specs mais concretas que achei):
- **Palavras por vez:** 2-3, "mais se necessário"; palavras soltas para ênfase. **[FONTE]**
- **Karaokê:** legenda dividida por palavra falada, cada palavra estilizada. Base **branca**; ênfase **amarela ou verde**, +2 a +4 pt de tamanho. **[FONTE]**
- **Fonte:** fonte bold (estilo The Bold Font), tamanho 20 no CapCut. **[FONTE]**
- **Contorno/sombra:** contorno preto (desktop) ou brilho preto intensidade ~65/alcance ~55 (mobile); sombra padrão ligada. **[FONTE]**
- **Posição:** centro/meio-inferior, ajustada caso a caso (algumas legendas sobem/descem). **[FONTE]**
- **Animação:** zoom-out na primeira legenda; "jiggle" em loop só em momentos-chave; rotação leve de -3 a +3 graus em algumas legendas. **[FONTE]**
- **Largura:** legenda curta ampliada (palavra curta fica maior), logo a largura varia com o tamanho da palavra. **[FONTE]**

### 3. Gen Z Vs Millennials, Apparently (internacional, faceless animado, viral comprovado)
| Campo | Valor |
|---|---|
| Nome do vídeo | Gen Z Vs Millennials, Apparently |
| Perfil | @PinkiemachineStudios |
| Views / Likes | 4.170.248 / 360.261 (coleta 2026-10-08) |
| Link | https://www.youtube.com/shorts/fkf4myBkHDw |

Estilo da legenda: **[VERIFICAR]** — não confirmei em frame. Hipótese de trabalho (gênero animação-meme): 1-3 palavras, fonte display grossa em caixa alta ou alta/baixa, contorno preto, posição centro-inferior, pop curto. Pegar 5 prints antes de copiar qualquer detalhe. Valor da referência: prova de nicho (faceless escala), não de tipografia.

### 4. Entender a Geração Z virou um desafio real! (pt-BR, faceless ilustrado, viral comprovado)
| Campo | Valor |
|---|---|
| Nome do vídeo | Entender a Geração Z virou um desafio real! |
| Perfil | @piadadesenhada |
| Views / Likes | 1.757.781 / 120.702 (coleta 2026-10-08) |
| Link | https://www.youtube.com/shorts/e4JBukMT4lQ |

Estilo da legenda: **[VERIFICAR]** — transcrição existe em `referencias/transcricoes/`, mas legenda visual não foi inspecionada. Melhor referência pt-BR de formato (sem rosto, ilustrado, 165s). Pedir print de 5 frames ao Guilherme/**Cristiano** para fechar fonte, cor e posição.

### 5. Referência de tipografia: lista de fontes de Shorts (apoio, não vídeo)
| Campo | Valor |
|---|---|
| Nome | 18 Best YouTube Shorts Fonts (guia) |
| Perfil | n/d (Virlo) |
| Views / Likes | n/d |
| Link | https://virlo.ai/blog/youtube-shorts-fonts |

Resumo útil: Montserrat (geométrica, legível sobre fundo movimentado), Impact (meme, linhas curtas), Bebas Neue (alta, caixa alta), The Bold Font (condensada, mensagens intensas), Oswald (condensada, cabe mais texto), Rubik ExtraBold (menos comum, visual fresco), Komika Axis (cartoon, humor). Orientação do guia: fonte grande e legível em tela de celular, contorno ou caixa de fundo para contraste, **evitar a borda inferior** (botões do app), fade/bounce/slide simples, "re-hook" visual a cada 3-5s.

---

## Quadro comparativo
| Atributo | Hormozi clássico | CapCut karaokê | Guia de fontes |
|---|---|---|---|
| Palavras/vez | 2-4 (4-6 em 2 linhas) | 2-3 | n/d |
| Cor ativa | amarelo/verde/vermelho | amarelo/verde | alto contraste |
| Cor base | branco | branco | n/d |
| Fonte | The Bold Font / Montserrat Black / Anton | bold estilo The Bold Font | Montserrat, Bebas, Impact... |
| Caixa alta | sim | sim | depende |
| Contorno/sombra | contorno preto grosso ou sombra forte | contorno preto + sombra | contorno ou caixa |
| Posição | meio/meio-inferior | meio/meio-inferior | longe da borda inferior |
| Animação | pop-in curto, ênfase maior | zoom-out, jiggle raro | fade/bounce simples |

---

## RECEITA RECOMENDADA (para o Cristiano especificar)

1. **2-3 palavras por tela, nunca mais de 2 linhas, e blocos casados com a pausa da fala.** O ponto de maior consenso entre as fontes (2-3 no CapCut, 2-4 em Hormozi). Palavras soltas só para ênfase. Quebrar sempre em fronteira de frase/vírgula, jamais separar artigo de substantivo.
2. **Karaokê com um único acento de cor: base branca, palavra ativa/chave em amarelo (#F7C204 a #FFD700).** Usar verde só para ganho/dado positivo e vermelho só para alerta, e apenas se o canal quiser semântica de cor (opcional; amarelo sozinho já é a escolha mais consistente). Palavra ativa +2-4 pt (~10-15%) maior que as demais.
3. **Fonte pesada, CAIXA ALTA, contorno preto grosso + sombra suave.** Prioridade: Montserrat ExtraBold/Black (gratuita, boa com acentos do pt-BR); alternativas: Anton, Bebas Neue. Conferir cobertura de acentos (Ç, Ã, Õ) antes de adotar qualquer fonte de nicho. O contorno é o que garante leitura sobre imagem gerada movimentada.
4. **Posição no terço médio-inferior (~55-70% da altura), fora da zona de UI do app (último ~20% e margem lateral), com pop curto (~80-120 ms, escala ~85%->105%->100%).** Largura ~70-85% da área útil. Isso conversa com o ajuste já registrado no projeto (`caption_size 0.045` / `caption_y 0.46`): o `caption_y 0.46` já fica no meio; confirmar se queremos subir o texto de volta ao terço inferior ou manter no centro (decisão para o **Cristiano**).

## Pendências / próximos passos
- **Verificação visual:** capturar 5 frames de @piadadesenhada (e1: `e4JBukMT4lQ`) e @PinkiemachineStudios (`fkf4myBkHDw`) para confirmar fonte/cor/posição reais, já que estes são os dois virais de nicho comprovados.
- Achar 1-2 canais dark pt-BR de psicologia/história com legenda karaokê e métricas públicas (não encontrei com a busca desta rodada).
- Ao terminar: o **Cristiano** deve transformar a receita acima em spec e reanalisar `referencias/analise_viral.md`.

## Fontes consultadas
- https://lilys.ai/en/notes/create-youtube-shorts-20260115/capcut-hormozi-captions
- https://www.submagic.co/pl/blog/how-to-make-alex-hormozi-captions
- https://www.kapwing.com/explore/hormozi-style-captions-template
- https://flixier.com/create/alex-hormozi-video-captions
- https://virlo.ai/blog/youtube-shorts-fonts
- https://outlierkit.com/channel/alexhormozi
- `referencias/referencias_nicho.md` (métricas de 2026-10-08)
