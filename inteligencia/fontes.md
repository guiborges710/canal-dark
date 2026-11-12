# Log de fontes

Mantido por **Hugo Souza**. Toda URL aberta na pesquisa entra aqui, com a data de acesso e o que ela é. Sem esta linha, a ficha do canal não vale.

Todas as linhas: data de acesso 2026-10-29. Notas de método:
- A chave `YOUTUBE_API_KEY` do `.env` está vazia; a YouTube Data API NÃO foi usada. Dados de data, duração e views vieram de: (a) feed RSS público do canal (`https://www.youtube.com/feeds/videos.xml?channel_id=<id>`), (b) endpoint público oEmbed do YouTube (autor do vídeo), (c) leitura pontual da página pública do vídeo (data e duração) e (d) miniaturas públicas (`i.ytimg.com`) para ver o estilo visual. Sem download de vídeo, sem coleta em massa (cerca de 30 páginas de vídeo no total).
- WebFetch em páginas do YouTube devolveu só o rodapé (sem dados). Anotado, não contornado.
- Áudio não foi ouvido: voz humana ou IA fica como "não verificado".

## Buscas web (WebSearch)
| Data | Consulta | Resultado |
|---|---|---|
| 2026-10-29 | canal dark gerações geração Z análise comportamento social Shorts YouTube | Só artigos acadêmicos e de marketing; nenhum canal. |
| 2026-10-29 | canal YouTube nem-nem jovens geração Z boomers millennials explicado | Artigos gerais; nenhum canal. |
| 2026-10-29 | canal faceless comportamento social psicologia sociedade YouTube Brasil animação | Guias de canal dark; menção a canais de psicologia. |
| 2026-10-29 | youtube.com (filtro de domínio) várias consultas: geração Z x boomers; gerações e sociologia; nem-nem; psicologia dark; filhos e casa própria; Shorts Z x millennials; solidão; burnout; jovens bebendo menos; sociedade e consumo; Shorts Z e trabalho; boneco de palito; economia do dia a dia; quiet quitting; animação de psicologia; nostalgia anos 2000; solidão e redes | Listas de vídeos, usadas para achar canais. |

## Páginas de vídeo e canal abertas (oEmbed/meta/feed)
| URL | O que é | Usada em |
|---|---|---|
| https://www.youtube.com/@futuroeconomicomedia | Página e feed RSS do canal Futuro Econômico | futuro-economico.md |
| https://www.youtube.com/watch?v=1ycBO3I3m78 | Vídeo "Por Que A Geração Z Desistiu De Ter Filhos?" | futuro-economico.md |
| https://www.youtube.com/watch?v=gNtU8oTuMwk | Vídeo Futuro Econômico (empresas e Geração Z) | futuro-economico.md |
| https://www.youtube.com/watch?v=jHUn5bYcRfY | Vídeo Futuro Econômico (casa própria) | futuro-economico.md |
| https://www.youtube.com/watch?v=0MkHxyPejWU | Vídeo Futuro Econômico (apartamentos minúsculos) | futuro-economico.md |
| https://www.youtube.com/watch?v=yLEyJk3_ce4 | Vídeo Futuro Econômico (empregos e experiência) | futuro-economico.md |
| https://www.youtube.com/watch?v=vrhgX4Xa3e0 | Vídeo Futuro Econômico (IA e classe média) | futuro-economico.md |
| https://www.youtube.com/watch?v=vccaq4HNrGM | Short Futuro Econômico | futuro-economico.md |
| https://www.youtube.com/@ipedipe | Página e feed RSS do canal ipe | ipe.md |
| https://www.youtube.com/watch?v=-TyansQKaL0 | Vídeo ipe | ipe.md |
| https://www.youtube.com/watch?v=Kp_RCFoVMfY | Vídeo ipe | ipe.md |
| https://www.youtube.com/watch?v=yCqI5v_isNM | Vídeo ipe (oEmbed) | ipe.md |
| https://www.youtube.com/watch?v=nLoCblJcD1I | Vídeo ipe | ipe.md |
| https://www.youtube.com/watch?v=1oAO3WPP7Sw | Vídeo ipe | ipe.md |
| https://www.youtube.com/watch?v=tVzswC17kxI | Vídeo ipe | ipe.md |
| https://www.youtube.com/@showdeinformacoes-infographics | Página e feed RSS do Show de Informações | show-de-informacoes.md |
| https://www.youtube.com/watch?v=KqufTiO9VIk | Vídeo Show de Informações (Z x Millennials) | show-de-informacoes.md |
| https://www.youtube.com/watch?v=7EbFWCWUrUQ | Vídeo Show de Informações | show-de-informacoes.md |
| https://www.youtube.com/watch?v=MhqJ6LZhvQs | Short Show de Informações | show-de-informacoes.md |
| https://www.youtube.com/watch?v=rvCC1G_8_ps | Vídeo Show de Informações | show-de-informacoes.md |
| https://www.youtube.com/@ProductivePeter | Página e feed RSS do Productive Peter | productive-peter.md |
| https://www.youtube.com/watch?v=jtrzGLDmIKA | Vídeo Productive Peter | productive-peter.md |
| https://www.youtube.com/watch?v=j5XiWNvwN6k | Vídeo Productive Peter | productive-peter.md |
| https://www.youtube.com/watch?v=NrX2IDx-3Xc | Short Productive Peter | productive-peter.md |
| https://www.youtube.com/watch?v=Agx18Dgykzk | Short Productive Peter | productive-peter.md |
| https://www.youtube.com/@psicologiaanimada | Página e feed RSS do Psicología Animada | psicologia-animada.md |
| https://www.youtube.com/watch?v=m_WGETZPFRE | Vídeo Psicología Animada | psicologia-animada.md |
| https://www.youtube.com/watch?v=JyeG24KhTwc | Vídeo Psicología Animada | psicologia-animada.md |
| https://www.youtube.com/watch?v=7x2B0lPLy8c | Vídeo Psicología Animada | psicologia-animada.md |
| https://www.youtube.com/watch?v=u340BpmUaJ4 | Vídeo Psicología Animada | psicologia-animada.md |
| https://www.youtube.com/@MinutosPsi | Página e feed RSS do Minutos Psi | minutos-psi.md |
| https://www.youtube.com/watch?v=R_2_Ask5JLA | Vídeo Minutos Psi | minutos-psi.md |
| https://www.youtube.com/watch?v=cZUKgvUvn7M | Vídeo Minutos Psi | minutos-psi.md |
| https://www.youtube.com/watch?v=lzUkxCCsbgo | Vídeo Minutos Psi | minutos-psi.md |
| https://www.youtube.com/@webpedia | Página e feed RSS do WebPedia | webpedia.md |
| https://www.youtube.com/watch?v=s8hG2Mkbm_c | Short WebPedia | webpedia.md |
| https://www.youtube.com/watch?v=bZHq0JNjuro | Short WebPedia | webpedia.md |
| https://www.youtube.com/watch?v=tcvYRfJWFBs | Vídeo WebPedia | webpedia.md |
| https://www.youtube.com/@Valorestradicional | Página e feed RSS de Valores modernos (miniaturas UsfxJzjcnwY, LtC8aXJxd14) | _indice.md (descartado) |
| https://www.youtube.com/@ideiasradicais | Página e feed RSS de Ideias Radicais; vídeo 3fT0WIraZyo (meta) | _indice.md (descartado) |
| https://www.youtube.com/@colunas.tortas | Página e feed RSS de Colunas Tortas | _indice.md (descartado) |
| https://www.youtube.com/@Mentalizei | Página e feed RSS de Mentalizei | _indice.md (descartado) |
| https://www.youtube.com/@CanalTop10 | Página e feed RSS de Canal Top10; vídeo vPwfjl3EXbA (meta), miniatura 61Dy2PxZ-os | _indice.md (descartado) |
| https://www.youtube.com/@historiasdejulia | Página e feed RSS de Julia Leivas | _indice.md (descartado) |
| https://www.youtube.com/@Estudio5elemento | Página e feed RSS (resultou em "Cortes do 5º Elemento", sem itens; não catalogado) | nenhuma |
| https://www.youtube.com/@CanalDarkBrasil-e8f | Página retornou HTTP 404; canal não catalogado | nenhuma |

## Vídeos consultados só via oEmbed (nome do canal) a partir das buscas
Usados para identificar canais e descartar veículos de imprensa. IDs em https://www.youtube.com/watch?v=<id>: Uym51bMGGVE, ao4hu3I9JKM, _attxSTKPNE, 681T6KDQS4k, R-EFEK2xdaw, WN9jtTir7fU, RkDT2ZVL10s, m0iR0vGrAVg, MTQ2IeWIflE, 3gZYALErPrY, nPLkoW8ZeFE, LC6w7JgLmRE, v9ykE0EpEH8, B0KesGygbRA, eIJUsN66B-w, yJO3eWWEaK4, ujW5LM1H31k, Gbso7pwXt3c, 6--lF5iSBf4, l3Cn2nGEYFA, OdssFHZfsm0, CKQkMYF6SKs, k3X39y3KbmE, spvubHoDNIs, x1LEKGgMDvQ, T_h0I4tvQVk, 6RhVMnatyxo, A_9I73cIFK4, RgnW3mP8ArQ, wMvWh6AM03s, m6STvgYZWnU, T-6j8ex2bbU, n48Ycoy_ANM, dKPR9GLoA3M, kgplFijNmDY, F25e7PLM4Sg, 2VhiQ0XFQhs, zNZOElkCCgY, wlh-j2lJFYw, UH_C8UgijbM, Gouwhy01jFE, p9JjEOxVNQM, aRGjUkANG_M, juVFXtkdf-g, CkCHWWFtZV4, HTlCfmuK-cQ, Nrjs2P5FUOg, zlIg_TbOIb8, -UCpneW_EpA, 55feahd2ufM, XdOgIFlbgiU. Falhas de oEmbed (vídeo indisponível ou bloqueado): ewPytephkCc, OiOf2xEyo4s, 2t22lCHVlvE, acigPkul9Xw; anotado, não contornado.

Fetch por WebFetch que falhou (só rodapé): https://www.youtube.com/shorts/Uym51bMGGVE, https://www.youtube.com/watch?v=ao4hu3I9JKM, https://www.youtube.com/watch?v=KqufTiO9VIk, https://www.youtube.com/@showdeinformacoes-infographics.

---

## Ciclo 2026-10-31 (Hugo Souza)

Foco do ciclo: canais dark pt-BR em estilo desenho/caderno/animação simples e temas de golpes/finanças/comportamento (apoio ao vídeo "esquema de pirâmide"). Data de acesso de todas as linhas abaixo: **2026-10-31**.

Método (igual ao ciclo anterior): `YOUTUBE_API_KEY` do `.env` continua **vazia**; a YouTube Data API NÃO foi usada. Dados vieram de: (a) feed RSS público do canal, (b) endpoint oEmbed público (autor/título), (c) `<meta itemprop="duration">` e `channelId`/`externalId` da página pública do vídeo/canal, (d) miniaturas públicas (`i.ytimg.com`) para ver o estilo visual. Sem download de vídeo, sem coleta em massa. WebFetch em páginas do YouTube seguiu devolvendo só o rodapé (anotado, não contornado). Áudio não ouvido: voz humana/IA fica "não verificado".

### Buscas web (WebSearch) — 2026-10-31
| Consulta | Resultado |
|---|---|
| canal YouTube Shorts golpes esquema de pirâmide finanças explicado animação desenho pt-BR | Artigos e notícias; nenhum canal dark direto. |
| canal dark faceless Shorts educação financeira golpes economia animação quadro branco brasileiro | Só guias de "como fazer canal dark". |
| (domínio youtube.com) como funciona esquema de pirâmide Shorts animação boneco palito pt-BR | Tutoriais de animação stickman; nenhum canal do nicho. |
| (domínio youtube.com) educação financeira animada Shorts juros dívida golpe explicado desenho simples canal | Achou "Animated Finance" (inglês) e "Economista Sincero" (tem rosto). |
| (domínio youtube.com) canal Shorts comportamento social sociedade explicado animação quadro caderno brasileiro faceless | Achou "AnimaClip" (francês, inativo). |
| Economista Sincero canal YouTube shorts educação financeira | Confirmado: apresentador (Charles Mendlowicz) com rosto — não é dark. |
| (domínio youtube.com) canal YouTube Shorts psicologia comportamento humano sociedade animação pt-BR sem rosto narração | Achou "Segundo a Psicologia". |
| (domínio youtube.com) canal Shorts curiosidades sociedade gerações dinheiro consumo animação quadro branco brasileiro | Resultados genéricos de Shorts. |
| (domínio youtube.com) como funciona pirâmide financeira golpe Ponzi explicado desenho animado Shorts canal brasileiro sem rosto | Achou "Mais Retorno" (portal com apresentadores) e vídeos avulsos. |
| (domínio youtube.com) canal dark Shorts economia comportamento consumo capitalismo animação simples narração IA brasileiro novo 2026 | Só tutoriais de "canal dark com IA". |
| (domínio youtube.com) canal YouTube Shorts "por que" sociedade brasileira dinheiro trabalho geração animação minimalista... | Resultados avulsos; nenhum canal confirmado. |
| (domínio youtube.com) canal animação econômica explicada Shorts inflação consumo endividamento brasileiro desenho giz lousa faceless | Achou "Rascunhos Econômicos" (desenho em papel) e "Economia Animada" (= Canal do Por Quê?). |
| (domínio youtube.com) canal Shorts "você sabia" vieses psicologia dinheiro comportamento consumidor animação pt-BR sem rosto narração IA | Fraca: artigos acadêmicos; nenhum canal. |

### Páginas de canal e vídeo abertas (RSS/oEmbed/meta/miniatura) — 2026-10-31
| URL | O que é | Usada em |
|---|---|---|
| https://www.youtube.com/@RascunhosEconomicos | Página e feed RSS do Rascunhos Econômicos (externalId UCyTpvFRG2v9kuzJZwUZ8M2Q) | rascunhos-economicos.md |
| https://www.youtube.com/watch?v=a4iJX8-qYaQ | Vídeo Rascunhos (patrimônio); duração + miniatura (estilo rascunho em papel) | rascunhos-economicos.md |
| https://www.youtube.com/watch?v=5Axgv3zAoiY | Vídeo Rascunhos (economia vai melhorar); duração | rascunhos-economicos.md |
| https://www.youtube.com/watch?v=3ogRSYzelM4 | Vídeo Rascunhos (Lula Day); duração | rascunhos-economicos.md |
| https://www.youtube.com/watch?v=qjJktgraWQo | Vídeo Rascunhos (resposta a tweet); miniatura (screenshot de tweet) | rascunhos-economicos.md |
| https://www.youtube.com/@canaldoporque | Página e feed RSS do Canal do Por Quê? (externalId UCqWMwhpW-rggQZtfNXIqkrw) | canal-do-porque.md |
| https://www.youtube.com/watch?v=UTFAihriQ_8 | Vídeo "O que é inflação | Economia Animada" (oEmbed → autor Canal do Por Quê?) | canal-do-porque.md |
| https://www.youtube.com/watch?v=sOwwLRLqBC8 | Vídeo Canal do Por Quê? (juros); duração | canal-do-porque.md |
| https://www.youtube.com/watch?v=tDMAJ02teog | Vídeo Canal do Por Quê? (dólar a R$0,83); duração + miniatura | canal-do-porque.md |
| https://www.youtube.com/watch?v=5Qgvw49Fxbc | Short Canal do Por Quê? (liquidez); duração | canal-do-porque.md |
| https://www.youtube.com/watch?v=eD0M8a9ACCQ | Short Canal do Por Quê? (tributação); duração | canal-do-porque.md |
| https://www.youtube.com/watch?v=VICuzkQemaU | Vídeo Canal do Por Quê? (IA e economia); duração | canal-do-porque.md |
| https://www.youtube.com/@segundoapsicologia | Página e feed RSS do Segundo a Psicologia (externalId UCiP-49xzeSW4hLA7xThHAWw) | segundo-a-psicologia.md |
| https://www.youtube.com/watch?v=k0dS4FojiUw | Vídeo Segundo a Psicologia; duração (38:53) | segundo-a-psicologia.md |
| https://www.youtube.com/watch?v=6AYN12Kj2XE | Vídeo Segundo a Psicologia; duração (50:42) + miniatura | segundo-a-psicologia.md |
| https://www.youtube.com/watch?v=5kpARPH84rU | Vídeo Segundo a Psicologia; duração (31:57) + miniatura | segundo-a-psicologia.md |
| https://www.youtube.com/channel/UCc3VGpQoifksnkVwXiYVKhw | Página e feed RSS do Animated Finance (inglês, inativo desde 2023) | animated-finance.md |
| https://www.youtube.com/channel/UC2PwknGihxlKZnw8ZS-jjCw | Feed RSS do ANIMACLIP (francês, inativo 2008-2009) | _indice.md (descartado) |
| https://www.youtube.com/@MaisRetorno | Portal de finanças com apresentadores (via oEmbed do vídeo edyIyH4GDJg) | _indice.md (descartado) |
| https://www.youtube.com/@canaldoporque (via oEmbed UTFAihriQ_8) | Confirmação de que "Economia Animada" é o Canal do Por Quê? | canal-do-porque.md |

Nota: o WebFetch de @segundoapsicologia/shorts devolveu só rodapé (anotado, não contornado). Miniaturas baixadas para inspeção visual em pasta temporária local (não versionada) e apagadas após a análise.

---

## Ciclo 2026-11-01 (Hugo Souza)

Foco: canais dark de gerações e comportamento social, BR e exterior, ainda não fichados. Data de acesso de todas as linhas: **2026-11-01**.

Método: `YOUTUBE_API_KEY` do `.env` segue **vazia**; a YouTube Data API NÃO foi usada. Dados vieram de feed RSS público (inclui views), oEmbed, `<meta itemprop>` da página do vídeo e miniatura pública (`i.ytimg.com`, vista uma a uma). Sem download de vídeo e sem coleta em massa. Áudio não ouvido. Resultado: o nicho em pt-BR segue sem canal dark claro; as buscas devolvem sobretudo Shorts avulsos de empresas e veículos.

### Buscas web (WebSearch)
| Consulta | Resultado |
|---|---|
| (youtube.com) canal Shorts gerações Z millennials boomers animação sem rosto | Shorts avulsos; achou "Millennial vs Gen Z Shorts", BlobbyClips e Shorts de marketing/gestão. |
| (youtube.com) canal Shorts solidão jovens comportamento social animação | Vídeos avulsos (DW Brasil, ROW Podcast); nenhum canal dark. |
| (youtube.com) faceless Gen Z behavior sociology animated Shorts stick figure | Tutoriais de stickman; vídeos sobre o "Gen Z stare"; achou Koo Psychology e Peter Reitano. |
| canal dark brasileiro comportamento humano sociedade geração Z Shorts desenho | Só guias e artigos; nenhum canal. |
| Psychology Explained with Stickman Animations YouTube channel | Anúncios de freelancer; canal não localizado. Citou Practical Psychology (inativo, via página de terceiros, não aberta por mim). |
| (youtube.com) Shorts geração Z jovens não saem de casa não namoram trabalho desenho | Shorts avulsos; achou GoKursos e DishIsh (não aberto). |

### Páginas abertas
| URL | O que é | Usada em |
|---|---|---|
| https://www.youtube.com/@KooPsychology | Página e feed RSS do Koo Psychology (UCWhS0dkpQcB76Pdusz78leg) | koo-psychology.md |
| https://www.youtube.com/watch?v=LdaKexFSZkY | Vídeo Koo Psychology; duração, data; miniatura | koo-psychology.md |
| https://www.youtube.com/watch?v=2NDI3_LEZHA | Vídeo Koo Psychology; duração, data; miniatura | koo-psychology.md |
| https://www.youtube.com/watch?v=Fgo4u21IzgY | Vídeo Koo Psychology; duração | koo-psychology.md |
| https://www.youtube.com/@BlobbyClips | Página e feed RSS (Minecraft) | _indice.md (descartado) |
| https://www.youtube.com/@Peter_Reitano | Página e feed RSS (marketing e relógios) | _indice.md (descartado) |
| https://www.youtube.com/@GoKursos | Página e feed RSS (cursos/carreira) | _indice.md (descartado) |
| https://www.youtube.com/channel/UCa-cpdQc-EnH1JswGEYgiMw | Feed RSS do Millennial vs Gen Z Shorts (inativo desde 2021) | _indice.md (descartado) |

Vídeos só via oEmbed (autor): wMvWh6AM03s (Productive Peter, já fichado), KoDs4XgbmlY, -4L1Tfv_fDs, jfSZVM7E0CA (Bruno Peres, marketing, não dark), m6STvgYZWnU (Carol Costa, gestão, não dark), cz1fsNgfUjg, XvYV1hmCTWA, 8egnC4lgguE, fjfxIQ6xqQU (Nanda Guardian, comentário com rosto, título ofensivo), e0dzDqDYtso (memes), YXxBpGhlAeY, EugrZ406vIk (News4JAX, imprensa), kTZiKhLMvoo, FkhPHa_FUKs (ROW Podcast), DxSBpg_lprU (DW Brasil). Miniaturas de Koo Psychology baixadas para inspeção em pasta temporária local, não versionada.

---

## Ciclo 2026-11-03 (Hugo Souza): estrutura de roteiro e papel de dados em Shorts do nicho

Data de acesso de todas as linhas: **2026-11-03**. Entregável: `canais/roteiros_2026-11-03.md`.

Método: desta vez a `YOUTUBE_API_KEY` do `.env` estava preenchida e a **YouTube Data API foi usada** (`search.list`, `videos.list`, `channels.list`, `playlistItems.list`; cerca de 17 buscas mais consultas pontuais, dentro da cota; chave nunca exibida). Legendas públicas lidas com `yt-dlp --skip-download` (só legenda, um vídeo por vez, com pausa). O YouTube respondeu **HTTP 429** várias vezes; parei e **não contornei**. Miniaturas públicas (`i.ytimg.com`, `mqdefault`) vistas em montagem para checar se há rosto. Sem download de vídeo e sem coleta em massa. Áudio não ouvido.

### Buscas na API (YouTube search, regionCode BR, pt, vídeos curtos)
geração Z comportamento sociedade explicado; por que as pessoas psicologia comportamento social; boomers millennials geração Z diferenças; psicologia dark comportamento humano curiosidade; por que os jovens estão sozinhos solidão sociedade; geração Z trabalho jovens sociedade; geração X millennials baby boomers explicado; o que ninguém te conta sobre a sociedade comportamento; efeito psicologia social experimento animação; sociedade moderna redes sociais comportamento ninguém fala; viés cognitivo explicado animação psicologia; geração Z shorts animação; nostalgia geração anos 90 shorts; efeito manada psicologia; psicologia social sociedade curiosidades; geração Z vs millennials. Algumas buscas (antigamente x hoje; classe média; jovens sem sair de casa) voltaram vazias.

### Vídeos com legenda lida (https://www.youtube.com/watch?v=<id>)
uWdqOmShxZ0 (Manipulação Oculta), m6W1VxF485s (Mente Que Enriquece), qo6VWgAZkhg e Tu1cxlgymmk (Psicologia do Poder), bUbgmSDL9kw (FOX Facts 239), gn0HZaodP4c (RETROANOS 80 e 90; legenda automática ruim), m1y5nNYGrWM (Geração Antiga), H2iIIwIW-ZY (Antes da internet), FWsY6wqIxtQ (Super Histórico), s8hG2Mkbm_c (WebPedia).

### Vídeos lidos só por título, descrição e dados da API (legenda não obtida)
fGvfZJf-_tE (Mente Que Enriquece), J0f45RWxlHw (FOX Facts 239; legenda não tentada), DtxxkM7Pq5g (Antes da internet; legenda bloqueada, 429), yOVMZ-bcPVs (Respire Conhecimento; 429), YqPXtEvyyXQ (Escrita Negra; sem legenda), WLp_W4ZWbp4 (Fatos ignotos; legenda não tentada), NRUIoFv688Q (Nathyy; legenda não tentada), NrX2IDx-3Xc e Agx18Dgykzk (Productive Peter), vccaq4HNrGM (Futuro Econômico), MhqJ6LZhvQs (Show de Informações).

### Canais cujos últimos 38 a 50 envios foram consultados na API (views, duração, datas)
Manipulação Oculta, Mente Que Enriquece, Psicologia do Poder, Respire Conhecimento, Escrita Negra, Fatos ignotos, RETROANOS 80 e 90, FOX Facts 239, Geração Antiga, Antes da internet, Super Histórico, WebPedia (todos via `playlistItems` do canal).

### Vídeos só vistos na lista de busca (título, canal, views) e excluídos por rosto/apresentador ou fora do formato
nhv0Vn7KlaA (Prof. Leandro), n-hAH8K7BNQ (O Codigo Bilionario), SpnXJuV1ENE (KhasTeoria), 94vXhRi5KIQ (Bruno Braio), pF8-n1CSCgc (Mentalidade Aprendiz), 7ni8YMiakZk (Café com Clonazepam), hNI2Ou_4fzk (Treinador de Líderes), luVeT1NjqbE e gjQady_u6dQ (trechos de experimento com pessoas), wGtYIzxxysI (Universo da Psicologia), ZjdyidFeE8g e GwEw8s7tmaY (cortes de podcast), mais Shorts de humor com rosto sobre gerações (Jarrod Benson, The Famileigh, Stanimus, JesssFam, Mac Macha e outros) e veículos de imprensa (Band, UOL, Jovem Pan, CartaCapital, TV Cultura).

Falhas: `yt-dlp` legenda HTTP 429 em yOVMZ-bcPVs (3 tentativas) e DtxxkM7Pq5g; anotado, não contornado.

---

## Ciclo 2026-11-03 noite (Hugo Souza): ampliação do catálogo

Data de acesso de todas as linhas: **2026-11-03**. YouTube Data API (`search.list` de canais e de vídeos, `channels.list`, `playlistItems.list`, `videos.list`; cerca de 15 buscas, dentro da cota; chave não exibida). Miniaturas públicas `i.ytimg.com/vi/<id>/mqdefault.jpg` de 8 vídeos vistas a partir de pasta temporária, não versionada. WebFetch em https://www.youtube.com/@economiaprimitiva_oficial voltou sem conteúdo (só rodapé); anotado, sem contorno. Áudio não ouvido.

| URL | O que é | Onde usada |
|---|---|---|
| https://www.youtube.com/@economiaprimitiva_oficial | Canal Economia Primitiva (API; página sem conteúdo no WebFetch) | canais/economia-primitiva.md |
| https://www.youtube.com/watch?v=8vKB5K2sW8s | Short Economia Primitiva (API e miniatura) | ficha |
| LvIjFyyIcmQ, OUOo-2px6nE, XAIDtqWcTEw, nnzf48E4hqo, m0badE22xQ4 (youtube.com/watch?v=) | Vídeos Economia Primitiva (API; miniatura de m0badE22xQ4 e LvIjFyyIcmQ baixadas) | ficha |
| https://www.youtube.com/channel/UCaWiNRTQZ-k-4oo1bgAD2LA | Canal Psicologia Sombria | canais/psicologia-sombria.md |
| lN3ItKn53mQ, kmsng25rZ_Q, Vg1-t1UPlco, HqGumAy5ZvY (youtube.com/watch?v=) | Vídeos Psicologia Sombria (API; miniatura de lN3ItKn53mQ e kmsng25rZ_Q) | ficha |
| https://www.youtube.com/channel/UCYd3a1qWe_yftL0ukSgbGJg | Canal Psicologia Desenrolada | canais/psicologia-desenrolada.md |
| MCUYcVZBXSQ, w5GE-OStlzM, gRiftzt3X-8, 6Vrg0aOAgGg (youtube.com/watch?v=) | Vídeos Psicologia Desenrolada (API; miniatura de MCUYcVZBXSQ e gRiftzt3X-8) | ficha |
| https://www.youtube.com/channel/UCpOsDCmvft_VGvVY7EP-GXA | Canal Sticktac | canais/sticktac.md |
| qioDHGsakCI, tjF2WZdpU30, d8NbpmJ21Fw (youtube.com/watch?v=) | Vídeos Sticktac (API; miniatura de qioDHGsakCI) | ficha |
| https://www.youtube.com/channel/UCugb1YKl4IgY5nM2JO-KVqQ | Sociologia Animada (API) | _indice.md (descartado) |
| https://www.youtube.com/@psicologiadosanimes | Psicologia dos Animes (API) | _indice.md (descartado) |
| https://www.youtube.com/@minutospsiquicos | Minutos Psíquicos (API) | _indice.md (descartado) |
| https://www.youtube.com/channel/UCRqDD6PTH86SxbvlDqwMaOg | Ansiedade Explicada (API) | _indice.md (descartado) |
| https://www.youtube.com/channel/UCnQKXxthY3vYwWvf45BQFjg | Pílula Empreendedora (API) | _indice.md (descartado) |
| https://www.youtube.com/channel/UC3Z2XdKUu21_KtMsohZedOQ | A Cara da Riqueza (API) | _indice.md (descartado) |
| https://www.youtube.com/channel/UC5EXj9Jfgcunyhp3kmMnx8Q | Janela da Alma Psicanalise (API) | _indice.md (descartado) |

Buscas feitas (regionCode BR, pt). Canais: sociologia animada explicada; comportamento social curiosidades animação; por que a sociedade mudou gerações; psicologia social experimentos explicados; história do consumo explicada desenho; economia comportamental animada; por que fazemos isso psicologia animação; cultura da internet explicada; fenômenos sociais explicados curtos. Shorts: gasto e status, amizade e geração, solidão moderna, redes sociais comparação, expectativa social aos 30. A maioria dos resultados foi cortes de podcast, imprensa, religião ou canais com zero a poucas dezenas de inscritos.

---

## Ciclo 2026-11-09 (Hugo Souza): foco em produção (animação, ritmo, voz)

Data de acesso de todas as linhas: **2026-11-09**. YouTube Data API usada (`search.list` de vídeos e canais, `channels.list`, `playlistItems.list`, `videos.list`; cerca de 20 chamadas, dentro da cota; chave não exibida). Miniaturas públicas `i.ytimg.com/vi/<id>/mqdefault.jpg` de 5 vídeos vistas a partir de pasta temporária, não versionada. Nenhuma página do YouTube aberta por WebFetch. Áudio não ouvido. Sem download de vídeo.

Buscas (regionCode BR, pt; Shorts desde 2026-05-01): geração Z millennials por que explicado; o que mudou entre gerações; psicologia social explicada animação; comportamento dos jovens hoje sociedade; por que ninguém mais; solidão moderna jovens; ninguém te conta sobre a vida adulta; geração Z e o dinheiro; millennials nostalgia anos 2000 animação; por que os jovens não querem mais. Canais: sociedade comportamento animação desenho explicado; gerações sociologia curiosidades; stickman psicologia social português; psicologia da sociedade moderna animada; cultura e comportamento social explicado. A maioria dos resultados foi cortes de podcast, imprensa, humor com rosto e canais minúsculos.

| URL | O que é | Usada em |
|---|---|---|
| https://www.youtube.com/@sr.stickmann | Canal Sr. Stickman (API) | canais/sr-stickman.md |
| 2XhkMfTG4SQ, mBhfyhU6EsY, 3L2_2y5mIQs, sZhfa0kbIfc, Qe_3DCgfuTs (youtube.com/watch?v=) | Vídeos Sr. Stickman (API; miniaturas de 2XhkMfTG4SQ e mBhfyhU6EsY) | ficha |
| https://www.youtube.com/@menteprimitiva1 | Canal Mente Primitiva (API) | canais/mente-primitiva.md |
| 8gyHhIPc4Ew, YNIY0w7ZYKM, CMAOfXuuo_A, vw1wnzueI9w (youtube.com/watch?v=) | Vídeos Mente Primitiva (API; miniatura de 8gyHhIPc4Ew) | ficha |
| https://www.youtube.com/@theskeletonsciences | Canal Skeleton Science (API) | canais/skeleton-science.md |
| JlrRHe5_HAY, JSDjuzotO7g, a53kVE9PMsA, doPdzgNvcdM, 3FpXbyu9KJA (youtube.com/watch?v=) | Vídeos Skeleton Science (API; miniatura de 3FpXbyu9KJA) | ficha |
| https://www.youtube.com/@storytoon-us | Canal Story Toon (API) | canais/story-toon.md |
| l3ftbjXSbG8, piM-caj0bNE, B21-mebmLEQ, CIOMD4Z8mEM (youtube.com/watch?v=) | Vídeos Story Toon (API; miniatura de CIOMD4Z8mEM) | ficha |
| https://www.youtube.com/@stickmansneedle | Stickman's Needle (API) | _indice.md (descartado) |
| https://www.youtube.com/@roxocurioso | Roxo Curioso (API) | _indice.md (descartado) |
| https://www.youtube.com/@amaralexplica | Amaral Explica (API) | _indice.md (descartado) |
| https://www.youtube.com/channel/UCxdDzkfLXqabuk55_zE6T1g | Smart Sketches (API) | _indice.md (descartado) |
| https://www.youtube.com/@infiniteimagination732 | Infinite Imagination (API) | _indice.md (descartado) |
| UC6aE3Xey0Dflgw51LmSMrpw, UCT0ZPVVqPJraf97j2J3lpaQ, UChWBI5CDaPCqsGkRiSrMuZQ (youtube.com/channel/) | Conhecimento Ilustrado, ALGORITMO FINAL, Análise Social BR (API) | _indice.md (descartado) |

Vídeos vistos só na lista de busca e excluídos (veículos, rosto, cortes): QhBcgL1Pbts (Ponto de Corte), OhjvyC3udQs (S7), W0VaCoo81wg (Economista Sincero, apresentador), vnMF6wJMsQc (VidaCaixa, institucional) e outros Shorts com rosto. Falha: uma chamada `playlistItems` com ID de canal truncado voltou HTTP 400 (erro meu); anotado.
