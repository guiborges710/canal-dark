# Novo canal a partir de 4 Reels: análise e recomendação

Data: 2026-11-03. Autor: **Valverde**. Para: **Luiz Henrique** e Guilherme. Só análise e recomendação: nenhum agente ou canal foi criado, nenhum arquivo do sistema foi editado.

## 0. O que consegui ver (limite honesto)

O Instagram não entrega o vídeo sem login. O que medi:

- Metadados públicos de cada link (autor, legenda, curtidas, data), pela etiqueta `og:` da página.
- A imagem de capa de cada Reel (um quadro), que li visualmente.

O que **não** consegui ver: duração, voz e música, efeitos sonoros, cortes e transições, ritmo, final. Quando o relatório fala disso, está marcado como **hipótese**. Para fechar essas partes, o Guilherme precisa assistir aos 4 e responder o checklist da seção 7 (5 minutos).

## 1. Tema e nicho (observado)

| # | Autor (pela URL) | Legenda | Capa | Engajamento |
|---|---|---|---|---|
| 1 | `@beto.sofredor` | "Flores geralmente são encontradas na própria natureza, e vem com elas, cheiros muito agradáveis #casal #relacionamento" | Homem com cara cansada segurando buquê com etiqueta "R$ 80"; legenda "OITENTA CONTO..." | 36 mil curtidas, 815 comentários (02/11/2026) |
| 2 | `@ocaradafotoclt` | (sem legenda pública) | Homem de boné "AUTOPEÇAS", camisa "Corrida 5K 2014", suando; legenda "O DENTE VOLTOU... MAS O BONÉ QUASE CAIU" | não obtido |
| 3 | `@ocaradafotoclt` | (sem legenda pública) | Tela dividida: "FORMATURA 2018" com "?" amarelo; "ELA ACHA QUE É ESSE / MAS É ESSE", o homem do boné sem um dente | não obtido |
| 4 | `@beto.sofredor` | "Caminhada no parque é uma atividade relaxante. #casal #relacionamento" | Boneco no parque com um palito de picolé escrito "ME AJUDA"; legenda "VOCÊ." | 6,5 mil curtidas, 128 comentários (03/11/2026) |

Padrão: **humor de casal e relacionamento, em desenho animado 2D, com personagem recorrente e sofredor**. O vídeo 1 e o 4 são o mesmo personagem (verde, cara resignada). Os vídeos 2 e 3 usam outro personagem recorrente (o do boné, com dente faltando) e uma piada de contraste "o que ela acha x o que é". A legenda do post é uma frase seca e irônica que disfarça a piada ("caminhada no parque é relaxante"). Os comentários do 4 confirmam a leitura: piadas internas sobre o personagem, o vestido amarelo, o palito "me ajuda".

Não é conteúdo informativo. É **comédia de situação em quadrinhos animados**, com personagem-assinatura. Observação: os autores dos vídeos 2 e 3 são diferentes dos 1 e 4 pela URL; o estilo visual é parecido (flat cartoon, contorno grosso), mas não afirmo que seja a mesma equipe.

## 2. Formato

Observado nas capas:
- Vertical 9:16, desenho vetorial plano, contorno escuro grosso, cores saturadas e cenários domésticos simples (sala com sofá, parque, auditório de formatura).
- Legenda grande no terço inferior, fonte grossa, branca com palavra-chave em amarelo/dourado e contorno. No vídeo 3 a tela é dividida em dois quadros para o contraste.
- Cada personagem tem uma marca visual fixa (boné AUTOPEÇAS, palito "ME AJUDA", cara cansada).

Hipótese, não observado: duração entre 15 e 40 s; narração com voz (pela legenda palavra a palavra, estilo "karaokê"); efeitos sonoros de cartoon; cortes secos; animação de boca e gesto simples (personagem em poses, não quadro a quadro). O "Original audio" no vídeo 4 sugere áudio próprio do autor, não música em alta.

## 3. Estrutura

Observado: o gancho está na própria imagem (o preço "R$ 80" no buquê; o "?" amarelo gigante; a cara de desespero). Não há estatística. A piada vira na última linha da legenda de tela ("MAS É ESSE", "VOCÊ.").

Hipótese: situação em 1 frase, escalada em 2 a 3 cenas, virada no fim, sem encerramento explicativo (a piada fecha o vídeo e convida a comentar/marcar o parceiro). Ritmo de uma fala por imagem.

## 4. Dados e números

Observado: no máximo 1 número por vídeo, e é piada (R$ 80, 2014, 2018), nunca estatística. Zero gráfico. Isso é o oposto do que o canal atual já abandonou: encaixa na regra 1 a 3 de `prompts/tipos_de_roteiro.md`.

## 5. Tom

Humor, ironia e exagero, sensacionalismo de identificação ("isso é comigo/com meu parceiro"), viral por marcação e comentário. Zero educativo. Não há vítima real, é ficção; o risco de tom com vítimas do canal atual não se aplica, mas há risco de estereótipo de gênero (ver seção 8).

## 6. Recomendação: reutilizar o sistema

### 6.1 O que reutilizar (sem mudar código)

| Parte | Uso no novo canal | Observação |
|---|---|---|
| `media/estilos.py` + `media/cartoon_lib.py` + `media/camadas.py` (estilo `cartoon_alive`) | É o estilo mais próximo do visual dos 4 Reels: personagem por camadas, cena em dados no `cenas.json` | Dono já decidiu esse estilo em 2026-11-03. Verificar se o personagem aceita rosto cansado, boné, objeto na mão (hipótese: sim, via componentes) |
| `media/sketch.py` (narração primeiro, cena no tempo da fala, encode) | Motor comum a todos os estilos por dados | Reuso total |
| `media/voz.py` / Chatterbox | Narração. Para humor, subir `exaggeration` e `velocidade` no perfil novo | Voz do Guilherme clonada: decidir se o novo canal usa a mesma voz |
| `media/sfx.py` | Efeitos de cartoon (whoosh, ding, impacto) | Falta talvez "tá-dá", risada, trombone: poucos sons novos |
| `reels/make_reel.py` (Dembelé, Kokoro + legenda viral + música) | Já faz legenda estilo "viral" e vídeo 9:16 para Instagram | Alternativa mais barata se as imagens vierem de fora; mas perde o desenho por código |
| `estudio/` (Corte) | Acompanhar, aprovar, editar, exportar | Só precisa de um projeto/produção por canal; ver 6.3 |
| `compliance.py` | Parte técnica (animação válida, cadência, aviso de animação por computador) | Itens de "fontes" e "ângulo" não se aplicam a ficção: exigem desligar por perfil |
| `render/` (SVG/Chrome) | Não usar: é do estilo Cartão, feito de números | |

### 6.2 Que agentes adaptar (nenhum criado agora)

- **Neymar** (roteirista): passa a escrever piada de situação. Não precisa de agente novo se o tipo de roteiro vier de um arquivo de tipos separado (`prompts/tipos_humor.md`, proposta). Tipos a descrever: "contraste (o que ela acha x o que é)", "preço absurdo", "tarefa de casal sofrida", "legenda irônica". Cada um com 1 número no máximo e virada no último beat.
- **Raphinha** (componentes): desenha o personagem recorrente, os cenários (sala, parque, formatura) e os objetos-assinatura. Essa é a parte que mais dá valor: personagem fixo vira ativo do canal.
- **Olise**: cenas em dados (`cartoon_alive`), com a legenda de tela grande e animada como elemento da cena.
- **Mbappé** (metadados): título, descrição e tags para humor; no Instagram vale a legenda curta irônica, não SEO.
- **Courtois**: dispensável neste canal, não há fato a revisar (ficção humorística). Se alguma cena citar dado real, ele volta.
- **Vini**: manter modo TEXTO e FINAL, mas enxuto: monetização, estereótipo, conteúdo sexual/ofensivo, direitos de personagem e voz. Sem checagem de fontes e ângulo.
- **Modric, Messi, Cristiano, Haaland, Sidorf**: não entram. Para o nicho humor, o que importa é banco de piadas e referência de formato, tarefa que **Memphis**/**Hugo Souza** já sabem fazer em outro setor.
- **Dembelé**: só se o canal for feito pelo fluxo `reels/` (imagens externas).

Quando criar agente novo (quando o Guilherme pedir): provavelmente um "roteirista de humor" separado do **Neymar**, para não misturar o tom do canal sério com o do canal de piada. Não crio agora, conforme pedido.

### 6.3 Mudanças em configuração e código (pequenas)

1. **`config_shorts.yaml` não muda.** Criar `config_humor.yaml` (cópia com `channel.niche`, `audience`, `minutes: 0.4` para 15-30 s, `render.duracao_min_s: 12`, `voz.exaggeration` maior, `compliance.max_videos_per_day` ajustado). O `config_horizontal.yaml` já prova que o sistema aceita perfil sobreposto.
2. **`run.py`**: hoje diz "não há `--format`, o perfil é `config_shorts.yaml`". Verificar (não li o arquivo) se existe um parâmetro de perfil; se não, é um item pequeno: `--perfil humor` que escolhe o yaml e a pasta de saída. Estimativa: dezenas de linhas, não validado.
3. **Tipos de roteiro**: arquivo novo, `prompts/tipos_humor.md`, no mesmo formato de `tipos_de_roteiro.md`. As regras 1 a 3 do canal atual (situação antes de dado, sem estatística no gancho) já valem. A regra "tese em uma frase" vira "uma piada, uma virada".
4. **`media/roteiro.py` e `compliance.py`**: precisam de bandeira "canal de ficção" para não exigir notas com 3+ fontes, `angulo.md` e 1/3 de comentário original. Sem isso, todo vídeo do novo canal reprova na conformidade por regra que não se aplica.
5. **Pastas e identidade**: `output_humor/` (ou `output/<canal>/`), assinatura do canal em arquivo próprio no lugar de `messi_assinatura_canal.md`, e nunca misturar `fila_postagem.txt` dos dois canais.
6. **Publicação**: `run.py publish` é YouTube/OAuth. Instagram e TikTok são postagem manual hoje (**Memphis**/fluxo `reels/`). Sem código novo se continuar manual.

### 6.4 Reuso x novo (estimativa, não medida)

- Reuso direto, sem mudar: motor de render, voz, sons, Corte, validação, encode: cerca de **75 a 85%** do trabalho.
- Adaptação de texto (prompts, tipos de roteiro, instruções dos agentes, perfil yaml): cerca de **10 a 15%**.
- Novo de verdade: personagens e cenários originais, flag de ficção em `compliance.py`/`roteiro.py`, eventuais sons de humor: cerca de **5 a 10%**.
Esses percentuais são julgamento meu sobre o tamanho do que existe (cerca de 4,7 mil linhas em `media/` e 6,8 mil em `estudio/`), não uma medição.

## 7. Checklist para o Guilherme fechar o que eu não vi

Assistir aos 4 e anotar: (1) duração de cada um; (2) tem narração falada ou só legenda e áudio original? (3) quantos cortes em 15 s; (4) o que acontece no primeiro 1 s; (5) o final fecha com piada ou com chamada para comentar; (6) animação é só pose trocada ou há movimento real; (7) música e efeitos. Com isso eu fecho as seções 2 e 3 e confirmo se `cartoon_alive` dá conta.

## 8. Riscos

- **Cópia de estilo e personagem.** O estilo de desenho (flat, contorno grosso, personagem recorrente) é genérico, mas copiar personagem, bordão ou piada dos autores é risco de reclamação e de "conteúdo reutilizado". Criar personagens e piadas originais é regra, não opção.
- **Monetização no YouTube.** Humor repetitivo, mesmo molde e voz sintética em volume podem cair em "conteúdo repetitivo/produção em massa". Variar enredo e personagem, manter limite de postagens por dia (hoje `max_videos_per_day: 2`). Em Instagram a monetização é outra (bônus/afiliados), não pesquisada aqui.
- **Estereótipo de gênero.** Todas as piadas são "homem sofre com a mulher". Rende engajamento (36 mil curtidas) mas pode gerar reação negativa; definir limite de tom com o Guilherme.
- **Mistura de marca.** O canal atual tem tese ("Geração é rótulo; contexto é explicação"). Humor de casal é outro público; misturar no mesmo canal dilui. Recomendo canal e identidade separados.
- **Voz.** Reutilizar a voz clonada do Guilherme nos dois canais liga a identidade dos dois.
- **Dados limitados.** Uma amostra de 4 vídeos e 2 autores; os números (36 mil, 6,5 mil) são de um único dia e de um perfil grande. Não prova que o nicho funciona para um canal novo.

## 9. Custos

- Dinheiro: continua **zero** no render e nos sons (local). Texto feito pela squad no Claude Code, sem API (`budget.max_usd_per_video: 0`).
- Tokens (estimativa): piada de 15-30 s é bem menor que um Short informativo; sem **Modric**, **Courtois** e **Messi** o fluxo humor consome bem menos que o diário, provavelmente menos da metade, não medido.
- Tempo humano: a maior parte vai para criar e validar o elenco de personagens (**Raphinha** + Guilherme, fase "aprendendo" de `componentes/aprendizados.md`) e rodar a voz clonada em CPU.
- Pendência de decisão: plataforma-alvo (Instagram, TikTok, YouTube Shorts), nome e voz. Sem isso o perfil yaml não fecha.

## 10. Ordem sugerida (para o Guilherme aprovar)

1. Guilherme assiste e preenche a seção 7; define plataforma e tom.
2. Teste barato sem código: um piloto de 1 piada usando `cartoon_alive` e voz atual, com o fluxo manual, para ver se o estilo aguenta o humor.
3. Se o piloto servir: `config_humor.yaml`, `prompts/tipos_humor.md` e a bandeira de ficção na conformidade (aplicadores: **Luiz Henrique** para texto de agentes; dono do código para `compliance.py`, `media/roteiro.py` e `run.py`).
4. Só depois, decidir agente novo de humor.

Fontes: metadados públicos `og:` das 4 URLs e capas dos Reels (acesso em 2026-11-03); arquivos do repositório lidos: `CLAUDE.md`, `config_shorts.yaml`, `reels/README.md`, `reels/make_reel.py`, `media/estilos.py`, `prompts/tipos_de_roteiro.md`.
