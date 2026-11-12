# Sistema único · Elenco de agentes (base para avatares)

Data: 2026-11-11 (revisado com a pesquisa com fontes do **Valverde**, `05_pesquisa_jogadores_valverde.md`). Autor: **Luiz Henrique**. Ordem dos setores igual ao `01_mapa_luiz_henrique.md`. Origem dos agentes: `.claude/agents/` (56 arquivos, contados um a um; o mapa 01 e o pedido falam em 57, diferença de 1 a conferir). Os prompts de avatar NÃO foram gerados: o Guilherme os pedirá depois. Lista de assets do sistema também não entra aqui (só depois do protótipo escolhido).

## Aviso de risco (decisão do Guilherme, não minha)

O Guilherme pretende vender o sistema. Usar rosto ou semelhança de jogadores reais em avatares de um produto comercial tem risco de direito de imagem (e de marcas de clubes e fabricantes). **Fica como risco a decidir por ele.** Sugestão, só como sugestão: avatares "inspirados", caricatura sem semelhança facial, com camisa, cores, pose e traço típicos da época, sem nomes nem escudos de clubes ou marcas registradas. Nada foi decidido.

## Como ler as fichas

- **Uso das fichas:** só para direção visual (camisa, cores, pose, época). **Não são fato jornalístico.** Nenhum número, placar ou título daqui deve ir para texto público sem fonte.
- Identificação do jogador/treinador: **decisão do Guilherme**, vale como fato; a pesquisa do **Valverde** (`05`) a confirmou na maior parte (ver "Divergências").
- Marca **[CONFERIR FONTE]**: a identidade é certa, mas a "melhor fase" vem de conhecimento geral (nível B do `05`, página de referência não aberta) ou não tem fonte. Mantida só como referência visual.
- Sem marca: confirmado por busca na web (nível A do `05`) no que a ficha afirma.
- "Melhor fase" é julgamento (não dado oficial). Regra do Guilherme: se a melhor fase foi de jogador, ficha de jogador; se foi de treinador, ficha de treinador (a coluna "Papel" diz qual).
- Traços visuais: só os de que há confiança; onde não, a ficha não inventa e o avatar segue o traço de época mais genérico.
- Nomes de clubes aparecem só como referência de ficha interna; se valer a alternativa "inspirada", eles saem.

---

## 1. Canal dark · Contexto Explica

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **De Bruyne** | `debruyne-orquestrador` | Coordena a produção ponta a ponta | Kevin De Bruyne (jogador); hoje no Napoli (A) | Manchester City 2019/20, meia armador, camisa azul-celeste, cabelo ruivo-loiro curto, pose de passe longo de pé direito. Recorde de assistências na Premier League [CONFERIR FONTE]. |
| **Modric** | `modric-pesquisador-tema` | Pesquisa o tema e grava `notas.md` | Luka Modrić (jogador); hoje no AC Milan, contrato até 06/2027 (A) | Real Madrid 2017/18 e Copa 2018 (Croácia), meia, camisa branca ou xadrez vermelho e branco, cabelo loiro mais comprido, magro. Prêmios da época [CONFERIR FONTE]. |
| **Memphis** | `memphis-social-media` | Referências virais e postagem manual | Memphis Depay (jogador); saiu do Corinthians em 31/07/2026 (79 jogos, 20 gols), sem clube novo confirmado (A) | PSV 2014/15 (alternativa: Lyon 2020/21), atacante, camisa vermelha e branca, topete clareado, barba e tatuagens nos braços. Prêmios da época [CONFERIR FONTE]. |
| **Haaland** | `haaland-pesquisador-nicho` | Nicho e ideias de pauta | Erling Haaland (jogador) | Manchester City 2022/23, centroavante, camisa azul-celeste, cabelo loiro comprido preso. Recorde de gols e tríplice coroa [CONFERIR FONTE]. |
| **Messi** | `messi-estrategista-angulo` | Tese, pergunta e comentário próprio | Lionel Messi (jogador) | Barcelona 2011/12, camisa 10 blaugrana, cabelo curto, barba rala. Recorde de gols na temporada [CONFERIR FONTE]. |
| **Neymar** | `neymar-roteirista` | Ângulo, roteiro e direção viral | Neymar Jr. (jogador); Santos e convocado por Ancelotti para a Copa 2026 (A) | Barcelona 2014/15, trio MSN, camisa 11 blaugrana, ponta esquerdo, drible e pedaladas. Cabelo e acessórios da época não registrados. Tríplice coroa [CONFERIR FONTE]. |
| **Courtois** | `courtois-revisor-fatos` | Confere roteiro contra as notas | Thibaut Courtois, goleiro (jogador) | Real Madrid 2021/22, goleiro muito alto, uniforme de goleiro (cor livre), luvas. Final da Champions contra o Liverpool e Troféu Yashin 2022 confirmados (A). |
| **Cristiano** | `cristiano-otimizador-viral` | Eleva o roteiro para viralizar | Cristiano Ronaldo (jogador); Al-Nassr, contrato até 2027 (A) | Manchester United 2007/08, atacante, camisa 7 vermelha, cabelo penteado para trás com gel. Bola de Ouro, Champions e gols da temporada [CONFERIR FONTE]. |
| **Raphinha** | `raphinha-curador-componentes` | Desenha componentes visuais | Raphinha, atacante do Barcelona (jogador) | Barcelona 2024/25, ponta direito, canhoto, camisa blaugrana, cabelo curto. 34 gols na temporada pelo site do clube (A); assistências divergem entre fontes. |
| **Olise** | `olise-diretor-arte` | Cenas animadas (`cenas.json`) | Michael Olise (jogador); Bayern de Munique (A) | Bayern 2024/25, ponta direito, canhoto, drible curto, camisa vermelha. Líder de assistências da Bundesliga e jogador da temporada eleito pelos torcedores (A). Traços de cabelo não registrados. |
| **Barcola** | `barcola-diretor-horizontal` | Cenas sketch 16:9 | Bradley Barcola (jogador); **Liverpool desde ago/2026**, vindo do PSG (A, site do PSG) | Ficha de época: PSG 2024/25, ponta esquerdo, camisa azul-marinho, velocidade e arrancada, cabelo curto. Números da temporada [CONFERIR FONTE]. Hoje a camisa é vermelha (Liverpool). |
| **Mbappé** | `mbappe-editor-metadados` | Título, descrição, tags e miniatura | Kylian Mbappé (jogador) | França na Copa de 2018 (alternativa: PSG 2018/19), atacante, arrancada, camisa azul, cabelo curto. Título aos 19 anos [CONFERIR FONTE]. |
| **Vini** | `vini-auditor-conformidade` | Auditoria de texto e final | Vinícius Júnior (jogador); Real Madrid | Real Madrid 2023/24, ponta esquerdo, camisa branca, drible e dança na comemoração. Títulos da temporada [CONFERIR FONTE]. Gol da final de 2021/22 confirmado (A). |
| **Sidorf** (grafia certa: **Seedorf**) | `sidorf-thumbnail-estrategista` | Prompt da miniatura (sem gerar imagem) | Clarence Seedorf. **Técnico do Corinthians**, anunciado em 11/10/2026, contrato até dez/2027, no lugar de Fernando Diniz (A). Id técnico segue `sidorf-...`. | Ficha de **jogador** (a de treinador é recente e fraca): Milan 2002/03 a 2006/07, meio-campista, camisa 10 rubro-negra listrada, cabeça raspada, físico forte. Champions 2003 e 2007 [CONFERIR FONTE]. |
| **Kane** | `kane-narrador` | Narra com a voz do Guilherme | Harry Kane (jogador); clube atual não confirmado | Tottenham 2017/18, centroavante, camisa 10 branca. Artilharia da Premier League e Chuteira de Ouro 2018 [CONFERIR FONTE]. |

---

## 2. Inteligência

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Hugo Souza** | `hugo-souza-pesquisador-canais` | Cataloga canais dark | Hugo Souza, goleiro do Corinthians, contrato até 2029 (A) | Corinthians 2025, goleiro titular, uniforme de goleiro, camisa alvinegra. Campeão da Copa do Brasil em 21/12/2025 (2 a 1 no Vasco) e eleito craque da competição (A). |
| **Fagner** | `fagner-analista-titulos` | Títulos, descrições e tags | Fagner, lateral direito. Saiu do Corinthians em jan/2026 após 11 temporadas (578 jogos, 5 títulos); **hoje no Cruzeiro** (A) | Corinthians 2015 a 2017, lateral direito, camisa alvinegra, capitão frequente. Brasileiro 2015 e 2017, Paulista 2017, 2018 e 2019 (A). Sem Copa do Brasil pelo clube. |
| **André Carrillo** | `andre-carrillo-analista-thumbnails` | Thumbnails de canais catalogados | André Carrillo, ponta peruano, Corinthians desde set/2024, contrato até 31/12/2026 (A) | Sporting CP 2011 a 2016, drible e velocidade, camisa verde e branca listrada. Recorte da melhor temporada [CONFERIR FONTE]. Traço de rosto não registrado. |
| **Raniele** | `raniele-analista-producao` | Como os canais produzem | Raniele, volante, Corinthians desde jan/2024 (Copa do Brasil 2025, Supercopa 2026) (A) | Corinthians 2025, volante, camisa alvinegra. Escolha minha, sem fonte que a qualifique como "melhor" [CONFERIR FONTE]. |
| **Yuri Alberto** | `yuri-alberto-analista-metricas` | Métricas do canal próprio | Yuri Alberto, centroavante, camisa 9 do Corinthians, renovado até 2030 (A) | Corinthians 2023, camisa 9 alvinegra, força e finalização. Usar só "centroavante e artilheiro do time"; o "artilheiro do Brasileiro 2023" **não está confirmado** [CONFERIR FONTE]. |
| **Garro** | `garro-scout-tecnologia-ia` | Ferramentas de IA de produção | Rodrigo Garro, meia argentino do Corinthians (A) | Corinthians 2025 (Paulistão e Copa do Brasil), passe e visão, camisa alvinegra. Número da camisa (10 ou 8) e estatísticas **não confirmados** [CONFERIR FONTE]. |
| **Vitinho** | `vitinho-consolidador` | Consolida o ciclo da inteligência | Victor Vinícius Coelho dos Santos (n. 09/10/1993), atacante e meia ofensivo; Corinthians desde ago/2025, **camisa 11 em 2026** (usava a 29); veio do Al-Ettifaq (A) | Fase de ouro indicada pelo Valverde: **Flamengo 2019/20**, camisa rubro-negra listrada (Libertadores 2019, Brasileiro 2019 e 2020, Recopa 2020; o 05 dá nível A). Alternativa por números: Internacional 2015/16. Hoje: camisa 11 alvinegra. |
| **Busquets** | `busquets-aprendiz-canais-dark` | Estuda vídeos dos canais dark | Sergio Busquets (jogador); clube atual não pesquisado | Barcelona 2010/11 e 2011/12, volante, camisa 5 blaugrana, cabelo escuro, pivô de saída de bola [CONFERIR FONTE]. |
| **Xabi Alonso** | `xabi-alonso-curador-referencias` | Lista referências para estudo | Xabi Alonso (**treinador**); demitido do Real Madrid em 12/01/2026 (A); clube atual não confirmado | Ficha de treinador, Bayer Leverkusen 2023/24: terno ou agasalho, cabelo curto, barba rala. Campeão alemão, Copa e Supercopa da Alemanha confirmados (A); "invicto" **não confirmado em fonte** [CONFERIR FONTE]. |

---

## 3. Clipes

Todas as fichas abaixo são nível B no `05` (identidade certa, fase de conhecimento geral): usar só como direção visual [CONFERIR FONTE].

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Pelé** | `pele-chefe-clipes` | Chefe do setor | Pelé (jogador, falecido em 2022) | Seleção Brasileira, Copa de 1970, camisa 10 amarela, calção azul, sorriso largo [CONFERIR FONTE]. |
| **Salah** | `salah-scout-fontes` | Acha fontes e confirma autorização | Mohamed Salah (jogador); Liverpool não reconfirmado em 2026 | Liverpool 2017/18, ponta direito, camisa vermelha, cabelo cacheado e barba. Recorde de gols na Premier League [CONFERIR FONTE]. |
| **Rivaldo** | `rivaldo-avaliador-fonte` | Nota da fonte | Rivaldo (jogador, aposentado) | Barcelona 1998 a 2001, camisa blaugrana, canhoto, esguio, cabelo curtíssimo. Bola de Ouro 1999 [CONFERIR FONTE]. |
| **Kaká** | `kaka-cacador-momentos` | Escolhe trechos | Kaká (jogador, aposentado) | Milan 2006/07, meia, camisa listrada rubro-negra, número 22. Champions e Bola de Ouro 2007 [CONFERIR FONTE]. |
| **Zidane** | `zidane-editor-cortes` | Gancho e fecho do corte | Zinedine Zidane (jogador) | França 1998, meia, camisa 10 azul, careca, elegante no controle de bola. Dois gols de cabeça na final e Bola de Ouro 1998 [CONFERIR FONTE]. |
| **Figo** | `figo-diretor-ganchos` | Frase mais forte, teaser | Luís Figo (jogador, aposentado) | Real Madrid 2000/01, ponta direito, camisa branca, cabelo castanho médio-longo, às vezes preso. Bola de Ouro 2000 [CONFERIR FONTE]. |
| **Totti** | `totti-avaliador-potencial` | Nota de potencial por corte | Francesco Totti (jogador, aposentado) | Roma 2000/01, camisa 10 giallorossa (amarelo e vinho). Título italiano [CONFERIR FONTE]. |
| **Buffon** | `buffon-auditor-originalidade` | Gate de originalidade | Gianluigi Buffon (jogador); aposentadoria não pesquisada | Itália, Copa de 2006, goleiro, uniforme de goleiro, físico forte, cabelo curto. Título mundial [CONFERIR FONTE]. |
| **Lewandowski** | `lewandowski-embalagem-plataformas` | Legenda e hashtags | Robert Lewandowski (jogador); clube atual não pesquisado | Bayern 2019/20, camisa vermelha, centroavante, cabelo curto e barba. Tríplice coroa [CONFERIR FONTE]. |
| **Roberto Carlos** | `roberto-carlos-gestor-perfis` | Perfis novos de TikTok e Instagram | Roberto Carlos (jogador, aposentado) | Real Madrid 2001/02, lateral esquerdo, camisa branca, coxas fortes, chute forte, cabelo curto. Champions [CONFERIR FONTE]. |

---

## 4. Pesquisa de vídeos longos

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Pirlo** | `pirlo-pesquisador-videos` | Acha vídeos longos para cortar | Andrea Pirlo (jogador, aposentado) | Juventus 2012/13, meia armador de passe longo, barba cheia e cabelo mais comprido, camisa preta e branca [CONFERIR FONTE]. |

---

## 5. Produtividade profissional

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Ronaldo** | `ronaldo-assistente` | Central de controle pessoal e Telegram | Ronaldo Nazário, o Fenômeno (jogador, aposentado) | Seleção Brasileira, Copa de 2002, camisa 9 amarela, corte de cabelo triangular. 8 gols e título mundial [CONFERIR FONTE]. |
| **Guardiola** | `guardiola-po-agilista` | PO, Kanban e Trello | Pep Guardiola (**treinador**, careca); clube atual não reconfirmado | Ficha de treinador, Barcelona 2008/09, à beira do campo, careca, terno ou colete, gesticulando. Sextete [CONFERIR FONTE]. |
| **Pedri** | `pedri-gestor-tarefas` | Tarefas e projetos | Pedri (jogador); Barcelona | Barcelona 2020/21, meia, camisa blaugrana, cabelo curto escuro. Golden Boy 2021 [CONFERIR FONTE]. |
| **Rodri** | `rodri-apontamento-horas` | Apontamento de horas | Rodri Hernández, o mesmo do City; **Barcelona desde 18/08/2026**, contrato até 30/06/2030 (A) | Manchester City 2023/24, volante, camisa azul-celeste (fase do City). Bola de Ouro 2024 **não reconfirmada na busca** [CONFERIR FONTE]. |
| **Kroos** | `kroos-acessos-seguranca` | Calendário de senhas | Toni Kroos (jogador); aposentadoria em 2024 por conhecimento, não pesquisada | Real Madrid 2017/18, meio-campista, camisa branca, cabelo loiro penteado de lado, passe preciso. Champions [CONFERIR FONTE]. |
| **Lamine Yamal** | `lamine-yamal-linkedin` | Rascunhos de LinkedIn | Lamine Yamal, Barcelona (jogador); segundo na Bola de Ouro 2025, atrás de Dembélé (A, UEFA) | Barcelona 2024/25 e Euro 2024, ponta direito, camisa blaugrana, cabelo curto [CONFERIR FONTE]. |
| **Bellingham** | `bellingham-dicas-ios` | Dicas conceituais de iOS | Jude Bellingham, Real Madrid (jogador) | Real Madrid 2023/24, meia, camisa branca, camisa 5, comemoração de braços abertos [CONFERIR FONTE]. |

---

## 6. Finanças pessoais

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Casemiro** | `casemiro-financeiro` | Recebimentos, gastos e dashboard | Casemiro (jogador); deixa o Manchester United no fim de 2025/26 (A); clube atual não confirmado | Real Madrid 2017/18, volante, camisa branca, camisa 14, cabelo curto, barba. Champions [CONFERIR FONTE]. |

---

## 7. Programação

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Zico** | `zico-po-programacao` | PO: backlog e aceite | Zico (jogador, aposentado) | Flamengo 1981, camisa 10 rubro-negra listrada. Libertadores e Mundial [CONFERIR FONTE]. |
| **Xavi** | `xavi-scrum-master` | Scrum Master | Xavi Hernández (jogador) | Barcelona 2008 a 2012, meia, camisa 6 blaugrana (fase de jogador; a de treinador é menor) [CONFERIR FONTE]. |
| **Ancelotti** | `ancelotti-agile-coach` | Coach de processo | Carlo Ancelotti (**treinador da Seleção Brasileira** desde maio/2025; eliminado nas oitavas da Copa 2026, 2 a 1 para a Noruega; segue até 2030) (A) | Ficha de treinador, Real Madrid 2021/22 (alternativa: 2013/14, a Décima), cabelo grisalho curto, sobrancelha arqueada, terno ou agasalho. Títulos da temporada [CONFERIR FONTE]. |
| **Thiago Silva** | `thiago-silva-tech-lead` | Tech lead e arquiteto | Thiago Silva (jogador); deixou o Porto em 21/05/2026 (A); clube atual não confirmado | PSG 2012 a 2020, zagueiro e capitão, braçadeira, camisa 2 azul-marinho, cabelo curto, barba [CONFERIR FONTE]. |
| **Rodrygo** | `rodrygo-dev-back` | Dev back-end | Rodrygo (jogador); Real Madrid; lesão de ligamento em mar/2026, fora da Copa (A) | Real Madrid 2021/22, ponta, camisa branca, gols contra o Manchester City na Champions [CONFERIR FONTE]. |
| **Endrick** | `endrick-dev-front` | Dev front-end | Endrick, centroavante do Real Madrid; emprestado ao Lyon de jan a 06/2026 (A); situação em nov/2026 não confirmada | Palmeiras 2023, centroavante jovem, camisa 9 verde, 17 anos, título do Brasileiro [CONFERIR FONTE]. Alternativa recente: Lyon 2026 (números divergem entre fontes). |
| **Iniesta** | `iniesta-ux-corte` | UX do Corte | Andrés Iniesta (jogador, aposentado) | Barcelona 2009/10 e Copa de 2010, meia, camisa blaugrana, pouco cabelo. Gol da final [CONFERIR FONTE]. |
| **Alisson** | `alisson-qa` | QA | Alisson Becker, goleiro do Liverpool (jogador) | Liverpool 2018/19, uniforme de goleiro, cabelo curto e barba. Champions e primeiro Troféu Yashin (2019) confirmados (A). "Golden Glove" **não confirmado** [CONFERIR FONTE]. |
| **Marquinhos** | `marquinhos-devops-release` | DevOps e release | Marquinhos, zagueiro do PSG, contrato até 2028 (A) | PSG 2024/25, zagueiro e capitão, camisa 5 azul-marinho. Champions listada no FotMob (A); placar da final e capitania **não confirmados** [CONFERIR FONTE]. |

---

## 8. Reels (Instagram, outro perfil)

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Dembelé** | `dembele-reels-instagram` | Mini-fluxo de Reels | **Ousmane Dembélé** (o Guilherme escreveu "Usman"); PSG; Bola de Ouro 2025, entregue em 22/09/2025 (A) | PSG 2024/25, ponta, camisa azul-marinho. Gols e assistências da temporada divergem entre fontes (PSG: 35 e 16; UEFA: 37 e 15; outra: 33 e 13): não citar número (A, com divergência). |

---

## 9. Ecossistema / transversal

| Craque | id técnico | Função | Quem é | Melhor fase (ficha) |
|---|---|---|---|---|
| **Luiz Henrique** | `luiz-henrique-ecossistema` | Cabeça do ecossistema | Luis Enrique Martínez, **treinador do PSG**, contrato prorrogado até 2030 em set/2026 (A). O agente se chama "Luiz Henrique". | Ficha de treinador, **PSG 2024/25** (primeira Champions do clube) ou **PSG 2025/26** (a fonte TSN registra dois títulos europeus seguidos, 2025 e 2026): escolha ainda por decidir. À beira do campo, cabelo curto, agasalho ou terno. Alternativa: Barcelona 2014/15. Detalhes de cada título [CONFERIR FONTE]. |
| **Valverde** | `valverde-engenheiro-ia` | Engenharia de IA | Federico Valverde (jogador); Real Madrid não reconfirmado em 2026 | Real Madrid 2022 a 2024, meio-campista de muita corrida, camisa branca [CONFERIR FONTE]. |
| **Firmino** | `firmino-frontend-design` | Atalho para a skill `frontend-design` | Roberto Firmino, o do sorrisão; **hoje no Al-Sadd (Catar)** desde jul/2025, contrato até 2027 (A) | Fase de ouro no Liverpool 2017/18 a 2018/19, falso 9, camisa vermelha, sorriso largo [CONFERIR FONTE]. Hoje não está mais no Liverpool. |

---

## 10. Sem setor claro ou fora do mapa

**Em `.claude/agents/` e fora da tabela do `ecossistema/README.md`:** **Pirlo**, **Totti**, **Figo**, **Roberto Carlos**, **Rivaldo** (só no histórico) e **Firmino**. Estão em `setores.json` (menos **Firmino**).

**Sem setor claro:**
- **Kane** (narração), **Memphis** (referências e postagem), **Dembelé** (Reels, setor separado) e **Valverde** (transversal), como já registra a pendência do mapa.
- **Firmino**: atende o ecossistema inteiro.
- **Ronaldo** e **Guardiola** aparecem em Produtividade, mas respondem como centrais (Telegram e Kanban); o 01 já marca isso.
- **Roberto Carlos** fica em Clipes por critério do mapa 01, ainda que suas pastas (`contas/`) estejam em outra pesquisa.

---

## Divergências (resolvidas e abertas)

**Resolvidas pelo Guilherme ou pela pesquisa do Valverde (`05`):**

1. **Seedorf**: grafia correta com dois E; é técnico do Corinthians (A, 11/10/2026). Id `sidorf-thumbnail-estrategista` mantido.
2. **Vitinho**: é Victor Vinícius Coelho dos Santos, Corinthians camisa 11, ex-Al-Ettifaq (A). A ficha antiga ("ex-Botafogo 2024") estava errada; fase de ouro agora Flamengo 2019/20, indicada pelo Valverde.
3. **Barcola**: o Guilherme tinha razão, Liverpool desde ago/2026 (A). A ficha de época segue PSG.
4. **Rodri**: o Guilherme tinha razão, Barcelona desde 18/08/2026, e é o mesmo do City (A).
5. **Fagner**: Cruzeiro desde jan/2026; títulos corrigidos (Brasileiro 2015 e 2017, Paulista 2017, 2018 e 2019) (A).
6. **Hugo Souza, Raniele, Carrillo, Yuri Alberto, Garro**: confirmados como do Corinthians (A).
7. **Firmino**: hoje no Al-Sadd; a ficha é de época (Liverpool).
8. **Dembelé**: é Ousmane Dembélé (A).
9. **Luiz Henrique = Luis Enrique** (PSG, A). Resta escolher a temporada da ficha.
10. **Ancelotti**: treinador da Seleção Brasileira confirmado (A); ficha segue Real Madrid.
11. **Memphis**: saiu do Corinthians em 31/07/2026 (A); ficha é de época (PSV).
12. **Endrick**: ficha de 2023 mantida; empréstimo ao Lyon em 2026 registrado.
13. **Xabi Alonso**: demitido do Real Madrid em 01/2026 (A); ficha do Leverkusen sem "invicto".

**Abertas:**

- Itens marcados **[CONFERIR FONTE]** (nível B ou sem fonte): "invicto" do Leverkusen, Bola de Ouro 2024 do Rodri, Golden Glove do Alisson, "artilheiro do Brasileiro" do Yuri Alberto, número da camisa do Garro, placar e capitania de Marquinhos em 2024/25, e todas as fases de nível B do `05`.
- Clube atual não confirmado: Messi, Kane, Busquets, Lewandowski, Valverde, Salah, Guardiola, Mbappé, Haaland, Courtois, Bellingham, Pedri, Xabi Alonso, Casemiro, Thiago Silva, Endrick, Neymar (há um título solto sobre time nos EUA).

---

## Lista de [CONFIRMAR] (o que restou, para o Guilherme)

1. **Luiz Henrique**: ficha pela temporada PSG 2024/25 ou 2025/26 (ou Barcelona 2014/15).
2. **Vitinho**: aceitar Flamengo 2019/20 como fase de ouro, ou preferir Internacional 2015/16.
3. **Endrick**: ficha Palmeiras 2023 ou Lyon 2026.
4. **Raniele e Carrillo**: aceitar a fase escolhida sem fonte de "melhor fase".
5. **Contagem**: 56 arquivos conferidos contra 57 citados no pedido e no 01 (diferença de 1 a conferir).
6. Registro do `05`: o que ele confirmou está nas linhas marcadas (A) acima; o que não confirmou segue marcado [CONFERIR FONTE]. Risco de direito de imagem continua decisão do Guilherme.
