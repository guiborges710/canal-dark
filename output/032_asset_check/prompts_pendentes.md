# PROG-032 — prompts de reposição revisados

Base: `output/032_asset_check/validacao_revisada/relatorio.md` e `reposicao.txt` (validação de 11/11, prioridades P0 e P1). Gere cada item abaixo em arquivo separado, no tamanho indicado, com o nome exato. Não combinar imagens numa prancha.

## Estilo e regras comuns

Ilustração vetorial cartoon plana, limpa e profissional, formas geométricas simples e cantos arredondados. Contorno azul-marinho `#0E1A24`, uniforme, cerca de 1% da largura. Cores chapadas, até dois níveis de sombra cel-shading, sem degradê, brilho especular, ruído ou textura. Luz de cima à esquerda; sombra projetada à direita e abaixo. Paleta visual: azul-marinho `#0E1A24`/`#162838`, branco frio `#EFF3F1`, cinza-azulado `#4B5E6A`, detalhe âmbar `#FFB703`; cores de camisa podem seguir a ficha. Sem texto, letras, números, logotipos, escudos, marcas, marca d'água ou assinatura.

Avatares: caricatura cartoon reconhecível do jogador real indicado, não fotografia nem fotorrealismo. Busto até o peito; cabeça grande moderada (cerca de 1/3 da altura do busto), olhos redondos grandes, nariz e boca simplificados, expressão natural. Cabeça ocupa 50–55% da largura; topo a 8% do quadro; rosto centralizado. Mesmo enquadramento, proporção, contorno e luz em todo o conjunto. Fundo completamente opaco, plano e uniforme no hex exato indicado, sem padrão, xadrez, transparência, moldura ou sombra. Para evitar o falso positivo do validador, garantir que os quatro cantos superiores (área externa ao retrato) mostrem somente o hex de fundo: cabelo, orelhas, roupa e acessórios não podem tocar os cantos superiores. Ombros podem chegar à base. Uniforme sem escudo, patrocinador, número ou logo.

Ilustrações de estado: objeto único central, margem livre de 12%, adesivo com contorno interno `#0E1A24` e borda fina `#EFF3F1`; fundo chapado `#FF00FF`, sem sombra, degradê ou xadrez. Nenhum magenta/rosa/roxo no objeto, sem personagens.

## Lote 1 — P0 para desbloquear a entrega

### `avatar_casemiro_ver_1024x1536.png` — 1024×1536, vertical 2:3

Caricatura reconhecível do jogador real Casemiro. Volante forte e largo, peito aberto, postura firme e queixo levemente erguido. Camisa branca lisa de gola redonda; cabelo escuro bem curto, barba cheia aparada, sobrancelhas marcadas; expressão séria e confiante. Braço direito junto ao peito como quem protege; segura calculadora pequena com um detalhe âmbar no visor. Fundo totalmente opaco `#1FA37B` (Finanças). Manter o rosto inteiro no quadrado central superior 1024×1024 e no recorte 4:5 do topo; preservar os cantos superiores livres e na cor do fundo.

### `avatar_ronaldo_ver_1024x1536.png` — 1024×1536, vertical 2:3

Regenerar o avatar de Ronaldo porque o arquivo atual foi reprovado: o fundo mediu desvio 191 do hex setorial. Caricatura reconhecível do jogador real Ronaldo, na fase do corte de cabelo com laterais raspadas e pequeno triângulo de cabelo no alto da frente. Atacante potente, ombros largos, corrida contida, sorriso aberto de dentes grandes e olhar alegre. Camisa amarela canarinho com gola verde, sem escudo; dedo apontando para cima e celular na mão esquerda com símbolo abstrato âmbar de notificação, sem letras/algarismos. Fundo opaco uniforme exatamente `#E0AA1E` (Trabalho). Os quatro cantos superiores devem permanecer integralmente nesse hex; rosto central e seguro para os recortes.

### `avatar_de_bruyne_ver_1024x1536.png` — 1024×1536, vertical 2:3

Caricatura reconhecível do jogador real Kevin De Bruyne. Meia armador alto e magro preparando um passe longo, pescoço levemente inclinado. Camisa azul-celeste lisa; cabelo ruivo-loiro curto penteado de lado, barba ruiva rala e sardas simples. Expressão calma e concentrada, uma sobrancelha levemente erguida; segura prancheta com setas abstratas de passe, sem escrita ou números. Fundo opaco uniforme `#2F7DE1` (Canal). Rosto central; cantos superiores totalmente planos e sem elementos.

### `avatar_luiz_henrique_ver_1024x1536.png` — 1024×1536, vertical 2:3

Caricatura reconhecível do treinador real Luiz Henrique, na fase moderna de treinador descrita na ficha. Homem de meia-idade, magro e atlético; postura em pé, braços cruzados ou mão na cintura. Agasalho de treino azul-marinho fechado até o pescoço (ou terno escuro sem gravata), cabelo grisalho curtíssimo, queixo marcado e barba por fazer. Olhar firme e sorriso discreto; segura mapa de metrô dobrado com linhas simples e ponto âmbar. Fundo opaco uniforme `#5B7283` (Ecossistema). Rosto central; cantos superiores sem cabelo ou acessório e no hex exato.

### `vazio_espera_ret_1536x1024.png` — 1536×1024, horizontal 3:2

Bandeja de entrada de papéis vazia com um grande check verde-menta `#1FBF8A`, mensagem visual “tudo em dia”. Objeto único central ocupando cerca de 60% da largura, margem segura de 12%, sem personagem. Fundo magenta chapado `#FF00FF`, sem sombra ou degradê; contorno adesivo azul-marinho `#0E1A24` e filete branco `#EFF3F1`.

## Lote 2 — P1 faltantes e reprovados

### `avatar_olise_ver_1024x1536.png` — 1024×1536, vertical 2:3 — faltante

Caricatura reconhecível do jogador real Michael Olise. Ponta ágil e esguio, ombros caídos, corpo levemente de lado em postura de drible curto; camisa vermelho-tijolo lisa de gola em V, cabelo escuro curto com degradê, sorriso de canto e expressão astuta. Segura pequena paleta de cores com um detalhe âmbar. Fundo opaco `#2F7DE1` (Canal); cantos superiores limpos e no hex.

### `avatar_vini_ver_1024x1536.png` — 1024×1536, vertical 2:3 — faltante

Caricatura reconhecível do jogador real Vinícius Júnior. Ponta magro e explosivo, ombro à frente em postura de drible e pequenos passos de dança; camisa branca com gola azul-marinho fina, cabelo preto curto com uma linha raspada lateral, sorriso largo de desafio. Segura carimbo com visto âmbar, sem palavra. Fundo opaco `#2F7DE1` (Canal); cantos superiores limpos e no hex.

### `avatar_neymar_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Neymar. Ponta esquerdo magro e ágil, postura de drible, pé sobre bola imaginária; camisa listrada vertical azul e grená, calção azul, cabelo curto com topete clareado e brinco pequeno, sorriso confiante e brincalhão. Segura bloco de roteiro e caneta âmbar. Fundo integralmente opaco `#2F7DE1` (Canal), corrigindo o desvio 145 do arquivo atual; cantos superiores sem elementos e exatamente no hex.

### `avatar_raphinha_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Raphinha. Ponta canhoto, baixo e musculoso, postura de chute com o pé esquerdo recuado; camisa listrada vertical azul e grená, cabelo curto escuro com topete leve, expressão intensa e sorriso curto. Segura lápis e régua com uma peça de componente âmbar. Fundo integralmente opaco `#2F7DE1` (Canal), corrigindo desvio 139; cantos superiores uniformes, sem cabelo/objeto sobre o fundo.

### `avatar_seedorf_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Seedorf. Meio-campista muito forte, ombros enormes, peito à frente em postura imponente; camisa listrada vertical vermelho-tijolo e preta, cabeça raspada, brinco pequeno, sorriso amplo e olhar sábio. Segura moldura de miniatura de vídeo com detalhe âmbar. Fundo opaco uniforme `#2F7DE1` (Canal), corrigindo desvio 121; cantos superiores vazios e no hex exato.

### `avatar_memphis_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Memphis Depay. Atacante expressivo, postura relaxada com atitude, corrente fina; camisa vermelha e branca em faixas largas, cabelo curto com topete descolorido, barba cheia aparada e tatuagens estilizadas nos antebraços. Sorriso de lado, dedo apontando para fora do quadro; segura celular com gráfico ascendente âmbar, sem números. Fundo opaco uniforme `#2F7DE1` (Canal), corrigindo desvio 161; cantos superiores sem elementos.

### `avatar_lamine_yamal_ver_1024x1536.png` — 1024×1536, vertical 2:3 — faltante

Caricatura reconhecível do jogador real Lamine Yamal, jovem e magro, postura leve de drible e olhar atrevido; camisa listrada vertical azul e grená, cabelo preto curto com tranças curtas no alto e corrente fina. Sorriso divertido, segura celular com post abstrato âmbar, sem texto. Fundo opaco `#E0AA1E` (Trabalho); cantos superiores limpos e no hex.

### `avatar_modric_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Luka Modrić. Meia baixo e magro, ombros estreitos, peito aberto em postura de passe curto; camisa xadrez vermelha e branca em quadros grandes (padrão de tecido, sem escudo), cabelo loiro mais comprido caindo na testa, olhar aguçado e sorriso curto. Segura livro de notas e lupa âmbar. Fundo opaco uniforme `#2F7DE1` (Canal), corrigindo desvio 182; manter os cantos superiores planos.

### `avatar_courtois_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do goleiro real Thibaut Courtois, muito alto e magro, braços abertos cobrindo o gol e cabeça um pouco inclinada. Uniforme verde-limão de mangas longas, luvas brancas, cabelo castanho curto e barba rala; expressão séria e atenta. Segura lista de checagem com visto âmbar. Fundo opaco uniforme `#2F7DE1` (Canal), corrigindo desvio 168; não deixar luvas/cabelo tocarem os cantos superiores.

### `avatar_mbappe_ver_1024x1536.png` — 1024×1536, vertical 2:3 — refazer fundo

Caricatura reconhecível do jogador real Kylian Mbappé, jovem e explosivo em postura de arrancada, corpo inclinado e pernas fortes. Camisa azul-marinho lisa de gola redonda, cabelo preto bem curto, queixo marcado e sorriso confiante. Segura etiqueta de título com raio âmbar, sem letras. Fundo opaco `#2F7DE1` (Canal), corrigindo desvio 113; cantos superiores sem elementos.

### `avatar_vitinho_ver_1024x1536.png` — 1024×1536, vertical 2:3 — faltante

Caricatura reconhecível do jogador real Vitinho na fase Flamengo 2019/20 (padrão adotado na ficha). Atacante ágil de porte médio, postura de corte para dentro; camisa listrada horizontal vermelho-tijolo e preta, cabelo escuro curto com degradê, barba curta e sorriso de canto. Segura prancheta de resumo com detalhe âmbar. Fundo opaco `#7C5FDB` (Inteligência); cantos superiores livres e uniformes.

### `avatar_endrick_ver_1024x1536.png` — 1024×1536, vertical 2:3 — faltante

Caricatura reconhecível do jogador real Endrick na fase Palmeiras 2023 (padrão adotado na ficha). Centroavante jovem e forte, ombros largos, postura de finalização e sorriso juvenil; camisa verde-escura lisa, cabelo curto crespo e barba adolescente rala. Segura monitor com janela de código abstrata âmbar, sem texto legível. Fundo opaco `#D14B93` (Programação); cantos superiores livres e uniformes.

### `fundo_hero_ilha_hor_1536x1024.png` — 1536×1024, horizontal 3:2 — faltante

Fundo opaco de baixa intensidade: geometria abstrata de linhas de metrô e pequenas estações circulares, curvas suaves, azul-marinho profundo. Contraste de apenas 3–6% em relação à ilha escura; centro discreto e sem elemento chamativo para manter os números da interface legíveis. Nenhum texto, logotipo, pessoa ou objeto. Composição segura para recorte horizontal 16:7 central.

## Estado dos outros itens

A validação revisada não pede reposição para os demais assets P0/P1. `vazio_financas`, `erro_geral`, `vazio_generico` e `vazio_agentes` estão OK; o logo está OK e o validador redimensionará o arquivo 1254×1254. O relatório revisado exigiu apenas P0 e P1; a última validação anterior de P2 marcou os itens P2 como OK, então não há prompt P2 aberto neste lote.
