# 08. Prompt único para gerar os assets (estilo H) no ChatGPT

Data: 2026-11-11. Autor: **Valverde**. Insumos: `04_modelo_prompt_unico_valverde.md` (atualizado hoje), `06_assets_firmino_H.md` (estilo, nomes, mapa), `07_fichas_avatar_luiz_henrique.md` (fichas). Nenhuma imagem foi gerada aqui.

Legenda: [FATO] = medido ou confirmado. [DEDUÇÃO] = inferência minha, a testar.

## 0. Resumo para o Guilherme

- São **66 imagens**: 57 avatares (um retrato 1024x1536 por agente, mais o "você"), 5 ilustrações de estado vazio/erro, 1 logo, 2 fundos e 1 capa. Prioridade: P0 = 9, P1 = 25, P2 = 32.
- [DEDUÇÃO] O ChatGPT provavelmente **não** vai gerar 66 imagens de uma vez nem montar o zip inteiro. O prompt-mestre (seção 1) está pronto para tentar, mas **recomendo FORTEMENTE começar pelo LOTE 1 (9 imagens P0)**, só para testar estilo, nomes e limites (seção 2).
- Depois de baixar, rode o script `organizar_e_validar.py` (seção 2.4). Ele confere nomes, tamanhos, fundo, converte para WebP e recorta os avatares.
- Os nomes de arquivo carregam os nomes dos agentes (`seedorf`, `de_bruyne`...), porque o protótipo usa o slug do nome exibido. O texto do prompt não cita jogador, clube, escudo, número nem marca; só os rótulos de arquivo trazem o apelido. Veja o risco 1 na seção 5.

## 1. PROMPT-MESTRE (os 66 itens, copiar e colar)

Copie tudo o que está dentro do bloco abaixo, do início ao fim (cerca de 26 mil caracteres). Se o ChatGPT recusar por tamanho ou travar, use os lotes da seção 2.

```text

Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Vou entregar um bloco de ESTILO fixo, as REGRAS DE SAÍDA e uma TABELA de 66 itens. Gere as imagens um item de cada vez, na ordem da tabela (prioridade P0, depois P1, depois P2), e no fim monte um único arquivo .zip. Use o MESMO estilo em todas as imagens e releia o bloco de estilo a cada item para o estilo não derivar. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_sistema_v1.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (colunas separadas por " | ": nº | arquivo | pasta | tamanho em px | forma | fundo | descrição). Prioridade P0 = itens 01 a 09; P1 = itens 10 a 34; P2 = itens 35 a 66.

01 | avatar_casemiro_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #1FA37B | Avatar. Ficha: Volante forte e largo, postura firme de peito aberto, queixo levemente erguido. Camisa branca lisa de gola redonda, cabelo escuro bem curto e barba cheia aparada, sobrancelhas marcadas. Expressão séria e confiante, braço direito ao peito como quem protege; segura uma calculadora pequena com o acento âmbar no visor.
02 | avatar_ronaldo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Atacante potente, ombros largos, pose de corrida contida, sorriso de dentes grandes e olhar alegre. Camisa amarela canarinho de gola verde (sem escudo), cabelo raspado nas laterais com um pequeno triângulo no alto da frente, o penteado marcante da época. Dedo apontando para o alto; um celular com notificação em âmbar na mão esquerda.
03 | avatar_de_bruyne_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meia armador de porte alto e magro, postura de quem vai fazer o passe longo, pescoço levemente inclinado. Camisa azul-celeste lisa, cabelo ruivo-loiro curto penteado de lado e barba rala ruiva, sardas simples. Expressão calma e concentrada, uma sobrancelha levemente erguida; segura uma prancheta com setas de passes desenhadas.
04 | avatar_luiz_henrique_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Treinador de meia-idade, magro e atlético, postura de pé com braços cruzados ou uma mão na cintura. Agasalho de treino azul-marinho com zíper fechado até o pescoço (ou terno escuro sem gravata), cabelo grisalho curtíssimo, queixo marcado, barba por fazer. Olhar firme e sorriso discreto de quem tem o plano; segura um mapa de metrô dobrado com um ponto âmbar.
05 | vazio_espera_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma caixa de entrada (bandeja de papéis) vazia, com um grande sinal de check em verde-menta #1FBF8A. Mensagem visual: tudo em dia. Objeto único, sem personagem.
06 | vazio_financas_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma carteira (ou cofrinho) aberta e vazia, com uma única moeda pequena em âmbar #FFB703 ao lado. Objeto único, sem personagem.
07 | erro_geral_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de erro: um cabo de tomada desconectado, plugue e tomada separados por um pequeno espaço, com uma faísca pequena em âmbar #FFB703. Objeto único, sem personagem.
08 | vazio_generico_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma prancheta vazia com um sinal de mais grande no centro da folha, detalhe em âmbar #FFB703. Objeto único, sem personagem.
09 | logo_contexto_explica_sq_1024x1024.png | icones | 1024x1024 | quadrada | magenta chapado #FF00FF | Marca (símbolo, sem nenhuma letra): um balão de fala redondo com uma linha de metrô saindo dele e uma estação circular na ponta em âmbar #FFB703. Formas geométricas, cabe num círculo inscrito, ocupa cerca de 65% do quadro.
10 | avatar_olise_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta ágil e esguio, ombros caídos, postura de drible curto com o corpo levemente de lado. Camisa vermelho-tijolo de gola em V, cabelo escuro curto com degradê, expressão de quem esconde a jogada, sorriso de canto. Segura uma pequena paleta de cores com um toque âmbar.
11 | avatar_valverde_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Meio-campista atlético de corrida, peito aberto, postura inclinada para frente como quem parte em velocidade. Camisa branca lisa, cabelo castanho médio penteado para trás, barba curta, olhar determinado. Segura um chip/circuito simples com um detalhe âmbar.
12 | avatar_alisson_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Goleiro alto, ombros largos, postura de prontidão com as duas mãos à frente. Uniforme de goleiro amarelo-limão de mangas longas, luvas brancas com detalhe azul, cabelo curto escuro, barba curta e cheia. Olhar atento, sorriso mínimo; uma lupa pequena sobre uma luva.
13 | avatar_salah_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Ponta de corpo leve e rápido, ombros estreitos, postura de arrancada. Camisa vermelho-tijolo lisa, cabelo preto bem cacheado volumoso, barba preta aparada, sorriso largo e simpático. Segura uma lupa grande sobre uma tela de vídeo.
14 | avatar_vini_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta magro e explosivo, postura de drible com um ombro à frente, pequenos passos de dança. Camisa branca com gola azul-marinho fina, cabelo preto curto com um desenho raspado de linha lateral, sorriso largo de desafio. Segura um carimbo de aprovação com o acento âmbar.
15 | avatar_neymar_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta esquerdo de corpo magro e ágil, postura de quem vai driblar, pé sobre a bola imaginária. Camisa listrada vertical azul e grená, calção azul, cabelo curto com topete clareado e brinco pequeno, sorriso confiante e brincalhão. Segura um bloco de roteiro com uma caneta âmbar.
16 | avatar_raphinha_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta canhoto, baixo e musculoso, postura de chute com o pé esquerdo recuado. Camisa listrada vertical azul e grená, cabelo curto escuro com topete leve, expressão intensa, sorriso curto. Segura um lápis e uma régua com uma peça de componente em âmbar.
17 | avatar_seedorf_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meio-campista de físico muito forte, ombros enormes, postura imponente com o peito para frente. Camisa listrada vertical vermelho-tijolo e preta, cabeça raspada, brinco pequeno, sorriso amplo e olhar sábio. Segura uma moldura de miniatura de vídeo com o acento âmbar.
18 | avatar_memphis_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante expressivo, postura relaxada com atitude, corrente fina no pescoço. Camisa vermelha e branca em faixas largas, cabelo curto com topete descolorido, barba cheia aparada e tatuagens estilizadas nos antebraços. Sorriso de lado, um dedo apontando para fora do quadro; segura um celular com o gráfico subindo em âmbar.
19 | avatar_rivaldo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Canhoto esguio e alto, postura descontraída, ombros caídos. Camisa listrada vertical azul e grená, cabelo raspado curtíssimo, queixo fino, olhar de quem avalia. Segura uma pequena placa de nota com visto em âmbar.
20 | avatar_kaka_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia elegante e alto, postura de aceleração com a cabeça erguida. Camisa listrada vertical vermelho-escuro e preta, cabelo castanho bem curto, rosto limpo e simpático, sorriso sereno. Segura uma tesoura de corte ligada a uma fita de vídeo âmbar.
21 | avatar_zidane_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia alto e elegante, postura de controle de bola no peito, movimento suave. Camisa azul-royal lisa de gola redonda, careca com testa ampla, sobrancelhas retas, expressão calma e dominante. Segura uma claquete com marca âmbar.
22 | avatar_zico_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia clássico, postura de cobrar falta, uma mão no quadril. Camisa listrada horizontal vermelho-tijolo e preta, cabelo castanho ondulado médio, sobrancelhas grossas, sorriso de líder. Segura um backlog (quadro de cartões) com um cartão âmbar.
23 | avatar_lamine_yamal_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Ponta jovem e magro, postura leve de drible, olhar atrevido de adolescente. Camisa listrada vertical azul e grená, cabelo preto curto com tranças curtas no alto, corrente fina. Sorriso de quem está se divertindo; segura um celular com um post em âmbar.
24 | avatar_modric_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meia baixo e magro, postura de passe curto de peito aberto, ombros estreitos. Camisa xadrez vermelha e branca em quadros grandes (não um escudo), cabelo loiro mais comprido caindo na testa, olhar aguçado e sorriso curto. Segura um livro de notas e uma lupa âmbar.
25 | avatar_courtois_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Goleiro muito alto e magro, postura de braços abertos cobrindo o gol, cabeça um pouco inclinada. Uniforme de goleiro verde-limão de mangas longas, luvas brancas, cabelo castanho curto, barba rala. Expressão séria e atenta; segura uma lista de checagem com um visto âmbar.
26 | avatar_mbappe_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante jovem e explosivo, postura de arrancada, corpo inclinado e pernas fortes. Camisa azul-marinho lisa de gola redonda, cabelo preto bem curto, queixo marcado, sorriso confiante. Segura uma etiqueta de título com um raio âmbar.
27 | avatar_vitinho_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Atacante de porte médio e ágil, postura de quem faz o corte para dentro. Camisa listrada horizontal vermelho-tijolo e preta, cabelo escuro curto com degradê, barba curta, sorriso de canto. Segura uma prancheta de resumo com o acento âmbar.
28 | avatar_rodrygo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Ponta magro e rápido, postura de arrancada. Camisa branca lisa de gola em V, cabelo escuro curto, sorriso aberto, olhar travesso. Segura uma engrenagem com um detalhe âmbar.
29 | avatar_endrick_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Centroavante jovem e forte, ombros largos, postura de finalização com sorriso de moleque. Camisa verde-escura lisa, cabelo curto crespo e barba rala de adolescente. Segura um monitor com uma janela de código em âmbar.
30 | avatar_thiago_silva_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Zagueiro capitão, físico forte, ombros largos, postura de comando. Camisa azul-marinho lisa com braçadeira de capitão amarelo-âmbar no braço, cabelo castanho curto com entradas, barba rala grisalha, olhar sereno. Segura um diagrama de arquitetura (caixas ligadas).
31 | avatar_marquinhos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Zagueiro capitão firme, ombros largos, postura de liderança. Camisa azul-marinho lisa, cabelo castanho curtíssimo, barba curta e rala, sorriso humilde. Segura um foguete pequeno de lançamento com um detalhe âmbar.
32 | avatar_voce_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #0B63E5 | Avatar. Ficha: Busto de pessoa genérica e neutra, sem rosto individualizado: cabeça lisa com apenas dois olhos redondos pequenos, uma curva de sorriso, sem cabelo definido e sem traços reconhecíveis. Camisa lisa branco-frio de gola redonda, postura relaxada de quem decide. Segura um carimbo de "aprovar" com um visto âmbar.
33 | vazio_agentes_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma lupa grande sobre uma fila vazia de peões de tabuleiro (só os espaços tracejados onde os peões ficariam), cabo da lupa em âmbar #FFB703. Sem personagem humano.
34 | fundo_hero_ilha_hor_1536x1024.png | fundos | 1536x1024 | horizontal | cena (opaco, sem transparência) | Fundo de tela: linhas de metrô abstratas com estações em círculos pequenos, azul-marinho profundo, contraste de 3 a 6%, faixa útil no miolo (a imagem será recortada em 16:7), nada nas bordas superior e inferior, nenhum elemento chamativo.
35 | avatar_haaland_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Centroavante gigante e muito forte, postura de peito estufado e olhar fixo. Camisa azul-celeste lisa, cabelo loiro comprido preso em coque ou rabo, sem barba, expressão de foco intenso. Segura uma bússola com o acento âmbar.
36 | avatar_messi_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Baixo e compacto, ombros caídos, postura de condução de bola de cabeça baixa. Camisa listrada vertical azul e grená, cabelo castanho curto, barba rala, olhar de calma e foco. Segura um papel com uma tese de uma frase e um sublinhado âmbar.
37 | avatar_cristiano_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante atlético de tronco largo, postura de herói com o queixo erguido. Camisa vermelho-tijolo lisa de gola alta, cabelo preto penteado para trás com gel, sobrancelhas retas, sorriso confiante. Segura um gráfico de barras subindo com a barra final âmbar.
38 | avatar_barcola_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta esguio e ágil, postura de arrancada para a esquerda. Camisa azul-marinho lisa de gola redonda, cabelo preto curto com degradê, sorriso discreto. Segura uma moldura horizontal 16:9 com o acento âmbar.
39 | avatar_kane_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Centroavante alto e robusto, queixo marcado, postura de finalizador. Camisa branca lisa de gola em V, cabelo castanho-claro curto penteado de lado, barba rala, expressão serena. Segura um microfone com a espuma âmbar.
40 | avatar_hugo_souza_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Goleiro jovem e alto, braços abertos, postura de prontidão. Uniforme de goleiro cinza-chumbo de mangas longas, luvas brancas, cabelo castanho curto, rosto franco. Segura um catálogo de pastas com uma pasta âmbar.
41 | avatar_fagner_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Lateral direito rápido e forte, postura de quem sobe pela direita, braçadeira de capitão em âmbar. Camisa listrada vertical branca e preta, cabelo escuro curto, barba curta, sorriso tranquilo. Segura um bloco de títulos com uma tag âmbar.
42 | avatar_andre_carrillo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Ponta rápido e de porte médio, postura de drible, olhar vivo. Camisa listrada horizontal verde e branca, cabelo preto liso penteado para trás, barba curta. Segura uma tela de miniatura com um quadro âmbar.
43 | avatar_raniele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Volante forte e de passo largo, postura de marcação, ombros fortes. Camisa listrada vertical branca e preta, cabelo escuro curto com degradê, expressão de concentração. Segura um relógio de produção com ponteiro âmbar.
44 | avatar_yuri_alberto_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Centroavante forte e alto, ombros largos, postura de finalização. Camisa listrada vertical branca e preta, cabelo escuro curto com topete discreto, sobrancelhas retas, sorriso de convicção. Segura um painel com linha de métrica subindo em âmbar.
45 | avatar_garro_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Meia criativo e franzino, postura de passe de calcanhar, olhar de visão. Camisa listrada vertical branca e preta, cabelo castanho médio ondulado, barba rala, sorriso levemente travesso. Segura um chip com antena e um brilho âmbar.
46 | avatar_busquets_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Volante alto e magro, postura de pivô de braços ligeiramente abertos, ombros caídos. Camisa listrada vertical azul e grená, cabelo escuro curto, sobrancelhas grossas, olhar frio e atento. Segura uma tela de estudo de vídeo com um play âmbar.
47 | avatar_xabi_alonso_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Treinador alto e elegante, postura reta de braços cruzados à beira do campo. Terno ou casaco escuro fechado sem gravata (roupa de treinador), cabelo castanho curto, barba rala aparada, olhar calmo. Segura uma pasta de referências com marcador âmbar.
48 | avatar_pele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Atacante atlético e sorridente, postura de comemoração com um punho erguido. Camisa amarela canarinho de gola verde, calção azul, cabelo preto bem curto, sorriso enorme. Segura uma faixa de chefe com a estrela âmbar.
49 | avatar_figo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Ponta alto e elegante, postura altiva com o peito aberto. Camisa branca lisa de gola redonda, cabelo castanho médio-longo preso atrás, barba rala, olhar intenso. Segura um claquete com marca âmbar.
50 | avatar_totti_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia-atacante de porte médio, postura de ousadia, olhar de artista. Camisa vinho e amarela em duas cores lisas, cabelo castanho curto penteado com topete, barba curta, sorriso brincalhão. Segura uma balança de nota com um peso âmbar.
51 | avatar_buffon_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Goleiro forte e compacto, peito largo, postura de líder atrás das luvas. Uniforme de goleiro preto de mangas longas, luvas brancas, cabelo escuro curto, mandíbula larga, olhar sério. Segura um selo de aprovação com a borda âmbar.
52 | avatar_lewandowski_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Centroavante de corpo atlético e alto, postura de finalizador contido. Camisa vermelho-tijolo lisa, cabelo castanho curto penteado de lado, barba curta, sorriso medido. Segura um bloco de legenda com uma hashtag âmbar sem texto.
53 | avatar_roberto_carlos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Lateral esquerdo baixo e extremamente forte, coxas largas, postura de chute potente. Camisa branca lisa, cabelo preto raspado curto, sorriso largo. Segura um celular com perfil novo aberto e um destaque âmbar.
54 | avatar_pirlo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia armador calmo e elegante, postura de passe longo com a cabeça erguida. Camisa listrada vertical preta e branca, cabelo castanho médio penteado para trás, barba cheia, olhar sereno. Segura uma lupa grande sobre uma linha do tempo com marcador âmbar.
55 | avatar_guardiola_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Treinador careca e magro, postura de gesticular à beira do campo. Colete e camisa social escuros (roupa de treinador), sem cabelo, sobrancelhas fortes, expressão intensa. Segura um quadro de Kanban com um cartão âmbar.
56 | avatar_pedri_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meia jovem e magro, postura leve de condução, olhar calmo. Camisa listrada vertical azul e grená, cabelo castanho escuro curto despenteado, rosto de adolescente. Segura uma lista de tarefas com um visto âmbar.
57 | avatar_rodri_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Volante alto e robusto, postura de comando, ombros largos. Camisa azul-celeste lisa (fase anterior, sem escudo), cabelo escuro curto, barba rala, expressão tranquila. Segura um relógio de ponto com ponteiro âmbar.
58 | avatar_kroos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meio-campista alto e frio, postura reta de passe preciso, braços relaxados. Camisa branca lisa, cabelo loiro penteado de lado com risca, rosto limpo, expressão impassível. Segura um chaveiro de cadeado com a chave âmbar (sem senha visível).
59 | avatar_bellingham_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meia jovem e atlético, postura de comemoração de braços abertos. Camisa branca lisa de gola em V, cabelo preto curto com degradê, sorriso largo. Segura um celular com um ícone genérico de fruta em âmbar, sem logotipo.
60 | avatar_xavi_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia baixo e inteligente, postura de cabeça erguida olhando em volta. Camisa listrada vertical azul e grená, cabelo castanho curto com entradas, olhar atento e sorriso mediano. Segura um quadro de sprint com um marcador âmbar.
61 | avatar_ancelotti_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Treinador corpulento e tranquilo, postura de braços cruzados e uma sobrancelha arqueada. Terno escuro ou casaco de treino azul-marinho, cabelo grisalho curto, rosto sereno e cético. Segura uma xícara de café com vapor âmbar.
62 | avatar_iniesta_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia franzino e de rosto delicado, postura de controle de bola, olhar sereno e humilde. Camisa listrada vertical azul e grená, cabelo castanho bem ralo e curto, sorriso tímido. Segura uma prancheta de wireframe com um traço âmbar.
63 | avatar_dembele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta veloz e magro, postura de arrancada, dribla com os dois pés. Camisa azul-marinho lisa com acabamento vermelho-tijolo na gola, cabelo curto com degradê e barba rala. Sorriso de canto; segura um celular em pé (formato vertical) com a tela em âmbar.
64 | avatar_firmino_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Atacante de movimentos suaves e braços soltos, postura de falso 9 recuado. Camisa vermelho-tijolo lisa, cabelo preto curto com topete trançado leve e barba cheia aparada, sorriso largo e contagiante (o sorrisão). Segura um pincel de design com a ponta âmbar.
65 | fundo_splash_ver_1024x1536.png | fundos | 1024x1536 | vertical | cena (opaco, sem transparência) | Fundo de tela vertical, mesma linguagem do fundo de linhas de metrô: azul-marinho profundo, contraste de 3 a 6%, curvas suaves, estações em círculos pequenos, centro limpo, sem texto.
66 | extra_og_capa_hor_1536x1024.png | extras | 1536x1024 | horizontal | cena (opaco, sem transparência) | Capa de vitrine: o mesmo símbolo da marca (balão de fala com linha de metrô e estação âmbar, sem letras) ao centro, sobre linhas de metrô em azul-marinho profundo, centro limpo, sem texto.

Comece agora pelo item 01 e siga até o 66. Ao terminar, entregue o .zip, a contagem de arquivos e a lista de itens que faltaram (se houver).

```

## 2. Como usar

### 2.1 Passo a passo recomendado (lotes)

1. **Abra uma conversa nova** no ChatGPT (modelo com geração de imagem). Cole o **LOTE 1** (seção 2.3). São 9 imagens: 4 avatares, 4 ilustrações e o logo.
2. Quando terminar, abra as imagens e confira com os olhos: o contorno é uniforme? A cabeça tem o mesmo tamanho nos 4 avatares? O fundo dos avatares é uma cor chapada? O fundo das ilustrações e do logo é um magenta uniforme (sem xadrez)? Não há texto, escudo nem número em nenhuma?
3. Baixe o `.zip` (ou as imagens soltas) e rode o validador (seção 2.4). Ele diz o que falta e o que reprovou.
4. Se o estilo estiver bom, guarde 1 a 3 imagens aprovadas como **âncora** (sugestão: um avatar de cada cor de fundo diferente e uma ilustração).
5. Nos lotes seguintes (2 a 8): **abra conversa nova a cada lote** [DEDUÇÃO: conversa longa faz o estilo derivar], **anexe 1 a 3 imagens âncora** e cole o prompt do lote. Todos os prompts de lote já repetem o MESMO bloco de estilo, byte a byte.
6. Se o ChatGPT parar no meio de um lote (limite de imagens do plano), peça só os itens que faltam: copie as linhas da tabela dos itens que faltaram para um prompt de reposição (modelo na seção 4) ou cole de novo o lote inteiro dizendo "gere só os itens 05 a 09".
7. No fim, junte todos os zips descompactados em UMA pasta e rode o validador com `--prio P0,P1,P2`. Ele monta `assets/<pasta>/<slot>.webp` prontos para o protótipo.

Sobre quantidade por conversa [DEDUÇÃO, não achei limite oficial]: se o lote de 9 a 11 imagens parar antes do fim, divida em duas conversas de 4 a 6 imagens (os prompts de lote aceitam isso: é só apagar as linhas que não vai pedir agora).

Ordem sugerida: LOTE 1, depois 2, 3, 4 (P1, 25 imagens) e só então os lotes 5 a 8 (P2, 32 imagens). Os P2 só aparecem na lista de Agentes e na ficha, então podem esperar.

### 2.2 Regras que valem em todo lote

- O bloco `[[ESTILO]] ... [[/ESTILO]]` não pode ser editado: nem resumir, nem reescrever.
- Nunca peça "gere todos em uma folha" nem "faça um sheet": o script espera um arquivo por item.
- Não acrescente o nome real de jogador, clube, escudo, número ou marca em nenhum pedido, nem para "corrigir" parecença.
- Âncora: 1 a 3 imagens já aprovadas. Mais que isso aumenta a chance de o ChatGPT copiar o personagem em vez do estilo.

### 2.3 Prompts dos lotes (prontos para colar)


#### LOTE 1 (P0, teste)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 1 (P0, teste): 9 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote1.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

01 | avatar_casemiro_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #1FA37B | Avatar. Ficha: Volante forte e largo, postura firme de peito aberto, queixo levemente erguido. Camisa branca lisa de gola redonda, cabelo escuro bem curto e barba cheia aparada, sobrancelhas marcadas. Expressão séria e confiante, braço direito ao peito como quem protege; segura uma calculadora pequena com o acento âmbar no visor.
02 | avatar_ronaldo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Atacante potente, ombros largos, pose de corrida contida, sorriso de dentes grandes e olhar alegre. Camisa amarela canarinho de gola verde (sem escudo), cabelo raspado nas laterais com um pequeno triângulo no alto da frente, o penteado marcante da época. Dedo apontando para o alto; um celular com notificação em âmbar na mão esquerda.
03 | avatar_de_bruyne_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meia armador de porte alto e magro, postura de quem vai fazer o passe longo, pescoço levemente inclinado. Camisa azul-celeste lisa, cabelo ruivo-loiro curto penteado de lado e barba rala ruiva, sardas simples. Expressão calma e concentrada, uma sobrancelha levemente erguida; segura uma prancheta com setas de passes desenhadas.
04 | avatar_luiz_henrique_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Treinador de meia-idade, magro e atlético, postura de pé com braços cruzados ou uma mão na cintura. Agasalho de treino azul-marinho com zíper fechado até o pescoço (ou terno escuro sem gravata), cabelo grisalho curtíssimo, queixo marcado, barba por fazer. Olhar firme e sorriso discreto de quem tem o plano; segura um mapa de metrô dobrado com um ponto âmbar.
05 | vazio_espera_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma caixa de entrada (bandeja de papéis) vazia, com um grande sinal de check em verde-menta #1FBF8A. Mensagem visual: tudo em dia. Objeto único, sem personagem.
06 | vazio_financas_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma carteira (ou cofrinho) aberta e vazia, com uma única moeda pequena em âmbar #FFB703 ao lado. Objeto único, sem personagem.
07 | erro_geral_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de erro: um cabo de tomada desconectado, plugue e tomada separados por um pequeno espaço, com uma faísca pequena em âmbar #FFB703. Objeto único, sem personagem.
08 | vazio_generico_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma prancheta vazia com um sinal de mais grande no centro da folha, detalhe em âmbar #FFB703. Objeto único, sem personagem.
09 | logo_contexto_explica_sq_1024x1024.png | icones | 1024x1024 | quadrada | magenta chapado #FF00FF | Marca (símbolo, sem nenhuma letra): um balão de fala redondo com uma linha de metrô saindo dele e uma estação circular na ponta em âmbar #FFB703. Formas geométricas, cabe num círculo inscrito, ocupa cerca de 65% do quadro.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote1.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 2 (P1, parte 1: canal, estado vazio de agentes e fundo da ilha)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 2 (P1, parte 1: canal, estado vazio de agentes e fundo da ilha): 11 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 imagens aprovadas do lote 1 (por exemplo avatar_de_bruyne_ver_1024x1536.png, avatar_casemiro_ver_1024x1536.png e vazio_espera_ret_1536x1024.png) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote2.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

10 | avatar_olise_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta ágil e esguio, ombros caídos, postura de drible curto com o corpo levemente de lado. Camisa vermelho-tijolo de gola em V, cabelo escuro curto com degradê, expressão de quem esconde a jogada, sorriso de canto. Segura uma pequena paleta de cores com um toque âmbar.
14 | avatar_vini_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta magro e explosivo, postura de drible com um ombro à frente, pequenos passos de dança. Camisa branca com gola azul-marinho fina, cabelo preto curto com um desenho raspado de linha lateral, sorriso largo de desafio. Segura um carimbo de aprovação com o acento âmbar.
15 | avatar_neymar_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta esquerdo de corpo magro e ágil, postura de quem vai driblar, pé sobre a bola imaginária. Camisa listrada vertical azul e grená, calção azul, cabelo curto com topete clareado e brinco pequeno, sorriso confiante e brincalhão. Segura um bloco de roteiro com uma caneta âmbar.
16 | avatar_raphinha_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta canhoto, baixo e musculoso, postura de chute com o pé esquerdo recuado. Camisa listrada vertical azul e grená, cabelo curto escuro com topete leve, expressão intensa, sorriso curto. Segura um lápis e uma régua com uma peça de componente em âmbar.
17 | avatar_seedorf_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meio-campista de físico muito forte, ombros enormes, postura imponente com o peito para frente. Camisa listrada vertical vermelho-tijolo e preta, cabeça raspada, brinco pequeno, sorriso amplo e olhar sábio. Segura uma moldura de miniatura de vídeo com o acento âmbar.
18 | avatar_memphis_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante expressivo, postura relaxada com atitude, corrente fina no pescoço. Camisa vermelha e branca em faixas largas, cabelo curto com topete descolorido, barba cheia aparada e tatuagens estilizadas nos antebraços. Sorriso de lado, um dedo apontando para fora do quadro; segura um celular com o gráfico subindo em âmbar.
24 | avatar_modric_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Meia baixo e magro, postura de passe curto de peito aberto, ombros estreitos. Camisa xadrez vermelha e branca em quadros grandes (não um escudo), cabelo loiro mais comprido caindo na testa, olhar aguçado e sorriso curto. Segura um livro de notas e uma lupa âmbar.
25 | avatar_courtois_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Goleiro muito alto e magro, postura de braços abertos cobrindo o gol, cabeça um pouco inclinada. Uniforme de goleiro verde-limão de mangas longas, luvas brancas, cabelo castanho curto, barba rala. Expressão séria e atenta; segura uma lista de checagem com um visto âmbar.
26 | avatar_mbappe_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante jovem e explosivo, postura de arrancada, corpo inclinado e pernas fortes. Camisa azul-marinho lisa de gola redonda, cabelo preto bem curto, queixo marcado, sorriso confiante. Segura uma etiqueta de título com um raio âmbar.
33 | vazio_agentes_ret_1536x1024.png | ilustracoes | 1536x1024 | retangular | magenta chapado #FF00FF | Ilustração de estado vazio: uma lupa grande sobre uma fila vazia de peões de tabuleiro (só os espaços tracejados onde os peões ficariam), cabo da lupa em âmbar #FFB703. Sem personagem humano.
34 | fundo_hero_ilha_hor_1536x1024.png | fundos | 1536x1024 | horizontal | cena (opaco, sem transparência) | Fundo de tela: linhas de metrô abstratas com estações em círculos pequenos, azul-marinho profundo, contraste de 3 a 6%, faixa útil no miolo (a imagem será recortada em 16:7), nada nas bordas superior e inferior, nenhum elemento chamativo.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote2.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 3 (P1, parte 2: clipes, ecossistema, inteligência, produtividade e você)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 3 (P1, parte 2: clipes, ecossistema, inteligência, produtividade e você): 8 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 imagens aprovadas (por exemplo avatar_luiz_henrique_ver_1024x1536.png, avatar_ronaldo_ver_1024x1536.png e 1 avatar do lote 2) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote3.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

13 | avatar_salah_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Ponta de corpo leve e rápido, ombros estreitos, postura de arrancada. Camisa vermelho-tijolo lisa, cabelo preto bem cacheado volumoso, barba preta aparada, sorriso largo e simpático. Segura uma lupa grande sobre uma tela de vídeo.
19 | avatar_rivaldo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Canhoto esguio e alto, postura descontraída, ombros caídos. Camisa listrada vertical azul e grená, cabelo raspado curtíssimo, queixo fino, olhar de quem avalia. Segura uma pequena placa de nota com visto em âmbar.
20 | avatar_kaka_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia elegante e alto, postura de aceleração com a cabeça erguida. Camisa listrada vertical vermelho-escuro e preta, cabelo castanho bem curto, rosto limpo e simpático, sorriso sereno. Segura uma tesoura de corte ligada a uma fita de vídeo âmbar.
21 | avatar_zidane_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia alto e elegante, postura de controle de bola no peito, movimento suave. Camisa azul-royal lisa de gola redonda, careca com testa ampla, sobrancelhas retas, expressão calma e dominante. Segura uma claquete com marca âmbar.
11 | avatar_valverde_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Meio-campista atlético de corrida, peito aberto, postura inclinada para frente como quem parte em velocidade. Camisa branca lisa, cabelo castanho médio penteado para trás, barba curta, olhar determinado. Segura um chip/circuito simples com um detalhe âmbar.
27 | avatar_vitinho_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Atacante de porte médio e ágil, postura de quem faz o corte para dentro. Camisa listrada horizontal vermelho-tijolo e preta, cabelo escuro curto com degradê, barba curta, sorriso de canto. Segura uma prancheta de resumo com o acento âmbar.
23 | avatar_lamine_yamal_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Ponta jovem e magro, postura leve de drible, olhar atrevido de adolescente. Camisa listrada vertical azul e grená, cabelo preto curto com tranças curtas no alto, corrente fina. Sorriso de quem está se divertindo; segura um celular com um post em âmbar.
32 | avatar_voce_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #0B63E5 | Avatar. Ficha: Busto de pessoa genérica e neutra, sem rosto individualizado: cabeça lisa com apenas dois olhos redondos pequenos, uma curva de sorriso, sem cabelo definido e sem traços reconhecíveis. Camisa lisa branco-frio de gola redonda, postura relaxada de quem decide. Segura um carimbo de "aprovar" com um visto âmbar.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote3.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 4 (P1, parte 3: programação)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 4 (P1, parte 3: programação): 6 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 avatares já aprovados (um de cada lote anterior) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote4.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

12 | avatar_alisson_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Goleiro alto, ombros largos, postura de prontidão com as duas mãos à frente. Uniforme de goleiro amarelo-limão de mangas longas, luvas brancas com detalhe azul, cabelo curto escuro, barba curta e cheia. Olhar atento, sorriso mínimo; uma lupa pequena sobre uma luva.
22 | avatar_zico_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia clássico, postura de cobrar falta, uma mão no quadril. Camisa listrada horizontal vermelho-tijolo e preta, cabelo castanho ondulado médio, sobrancelhas grossas, sorriso de líder. Segura um backlog (quadro de cartões) com um cartão âmbar.
28 | avatar_rodrygo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Ponta magro e rápido, postura de arrancada. Camisa branca lisa de gola em V, cabelo escuro curto, sorriso aberto, olhar travesso. Segura uma engrenagem com um detalhe âmbar.
29 | avatar_endrick_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Centroavante jovem e forte, ombros largos, postura de finalização com sorriso de moleque. Camisa verde-escura lisa, cabelo curto crespo e barba rala de adolescente. Segura um monitor com uma janela de código em âmbar.
30 | avatar_thiago_silva_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Zagueiro capitão, físico forte, ombros largos, postura de comando. Camisa azul-marinho lisa com braçadeira de capitão amarelo-âmbar no braço, cabelo castanho curto com entradas, barba rala grisalha, olhar sereno. Segura um diagrama de arquitetura (caixas ligadas).
31 | avatar_marquinhos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Zagueiro capitão firme, ombros largos, postura de liderança. Camisa azul-marinho lisa, cabelo castanho curtíssimo, barba curta e rala, sorriso humilde. Segura um foguete pequeno de lançamento com um detalhe âmbar.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote4.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 5 (P2, parte 1: canal restante, splash e capa de vitrine)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 5 (P2, parte 1: canal restante, splash e capa de vitrine): 8 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 imagens aprovadas (avatares, o logo e o fundo da ilha) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote5.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

35 | avatar_haaland_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Centroavante gigante e muito forte, postura de peito estufado e olhar fixo. Camisa azul-celeste lisa, cabelo loiro comprido preso em coque ou rabo, sem barba, expressão de foco intenso. Segura uma bússola com o acento âmbar.
36 | avatar_messi_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Baixo e compacto, ombros caídos, postura de condução de bola de cabeça baixa. Camisa listrada vertical azul e grená, cabelo castanho curto, barba rala, olhar de calma e foco. Segura um papel com uma tese de uma frase e um sublinhado âmbar.
37 | avatar_cristiano_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Atacante atlético de tronco largo, postura de herói com o queixo erguido. Camisa vermelho-tijolo lisa de gola alta, cabelo preto penteado para trás com gel, sobrancelhas retas, sorriso confiante. Segura um gráfico de barras subindo com a barra final âmbar.
38 | avatar_barcola_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta esguio e ágil, postura de arrancada para a esquerda. Camisa azul-marinho lisa de gola redonda, cabelo preto curto com degradê, sorriso discreto. Segura uma moldura horizontal 16:9 com o acento âmbar.
39 | avatar_kane_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Centroavante alto e robusto, queixo marcado, postura de finalizador. Camisa branca lisa de gola em V, cabelo castanho-claro curto penteado de lado, barba rala, expressão serena. Segura um microfone com a espuma âmbar.
63 | avatar_dembele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #2F7DE1 | Avatar. Ficha: Ponta veloz e magro, postura de arrancada, dribla com os dois pés. Camisa azul-marinho lisa com acabamento vermelho-tijolo na gola, cabelo curto com degradê e barba rala. Sorriso de canto; segura um celular em pé (formato vertical) com a tela em âmbar.
65 | fundo_splash_ver_1024x1536.png | fundos | 1024x1536 | vertical | cena (opaco, sem transparência) | Fundo de tela vertical, mesma linguagem do fundo de linhas de metrô: azul-marinho profundo, contraste de 3 a 6%, curvas suaves, estações em círculos pequenos, centro limpo, sem texto.
66 | extra_og_capa_hor_1536x1024.png | extras | 1536x1024 | horizontal | cena (opaco, sem transparência) | Capa de vitrine: o mesmo símbolo da marca (balão de fala com linha de metrô e estação âmbar, sem letras) ao centro, sobre linhas de metrô em azul-marinho profundo, centro limpo, sem texto.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote5.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 6 (P2, parte 2: inteligência)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 6 (P2, parte 2: inteligência): 8 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 avatares já aprovados como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote6.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

40 | avatar_hugo_souza_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Goleiro jovem e alto, braços abertos, postura de prontidão. Uniforme de goleiro cinza-chumbo de mangas longas, luvas brancas, cabelo castanho curto, rosto franco. Segura um catálogo de pastas com uma pasta âmbar.
41 | avatar_fagner_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Lateral direito rápido e forte, postura de quem sobe pela direita, braçadeira de capitão em âmbar. Camisa listrada vertical branca e preta, cabelo escuro curto, barba curta, sorriso tranquilo. Segura um bloco de títulos com uma tag âmbar.
42 | avatar_andre_carrillo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Ponta rápido e de porte médio, postura de drible, olhar vivo. Camisa listrada horizontal verde e branca, cabelo preto liso penteado para trás, barba curta. Segura uma tela de miniatura com um quadro âmbar.
43 | avatar_raniele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Volante forte e de passo largo, postura de marcação, ombros fortes. Camisa listrada vertical branca e preta, cabelo escuro curto com degradê, expressão de concentração. Segura um relógio de produção com ponteiro âmbar.
44 | avatar_yuri_alberto_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Centroavante forte e alto, ombros largos, postura de finalização. Camisa listrada vertical branca e preta, cabelo escuro curto com topete discreto, sobrancelhas retas, sorriso de convicção. Segura um painel com linha de métrica subindo em âmbar.
45 | avatar_garro_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Meia criativo e franzino, postura de passe de calcanhar, olhar de visão. Camisa listrada vertical branca e preta, cabelo castanho médio ondulado, barba rala, sorriso levemente travesso. Segura um chip com antena e um brilho âmbar.
46 | avatar_busquets_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Volante alto e magro, postura de pivô de braços ligeiramente abertos, ombros caídos. Camisa listrada vertical azul e grená, cabelo escuro curto, sobrancelhas grossas, olhar frio e atento. Segura uma tela de estudo de vídeo com um play âmbar.
47 | avatar_xabi_alonso_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #7C5FDB | Avatar. Ficha: Treinador alto e elegante, postura reta de braços cruzados à beira do campo. Terno ou casaco escuro fechado sem gravata (roupa de treinador), cabelo castanho curto, barba rala aparada, olhar calmo. Segura uma pasta de referências com marcador âmbar.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote6.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 7 (P2, parte 3: clipes)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 7 (P2, parte 3: clipes): 7 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 avatares já aprovados (inclua 1 de fundo laranja, para a camisa não se fundir ao fundo) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote7.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

48 | avatar_pele_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Atacante atlético e sorridente, postura de comemoração com um punho erguido. Camisa amarela canarinho de gola verde, calção azul, cabelo preto bem curto, sorriso enorme. Segura uma faixa de chefe com a estrela âmbar.
49 | avatar_figo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Ponta alto e elegante, postura altiva com o peito aberto. Camisa branca lisa de gola redonda, cabelo castanho médio-longo preso atrás, barba rala, olhar intenso. Segura um claquete com marca âmbar.
50 | avatar_totti_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia-atacante de porte médio, postura de ousadia, olhar de artista. Camisa vinho e amarela em duas cores lisas, cabelo castanho curto penteado com topete, barba curta, sorriso brincalhão. Segura uma balança de nota com um peso âmbar.
51 | avatar_buffon_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Goleiro forte e compacto, peito largo, postura de líder atrás das luvas. Uniforme de goleiro preto de mangas longas, luvas brancas, cabelo escuro curto, mandíbula larga, olhar sério. Segura um selo de aprovação com a borda âmbar.
52 | avatar_lewandowski_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Centroavante de corpo atlético e alto, postura de finalizador contido. Camisa vermelho-tijolo lisa, cabelo castanho curto penteado de lado, barba curta, sorriso medido. Segura um bloco de legenda com uma hashtag âmbar sem texto.
53 | avatar_roberto_carlos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Lateral esquerdo baixo e extremamente forte, coxas largas, postura de chute potente. Camisa branca lisa, cabelo preto raspado curto, sorriso largo. Segura um celular com perfil novo aberto e um destaque âmbar.
54 | avatar_pirlo_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D9542D | Avatar. Ficha: Meia armador calmo e elegante, postura de passe longo com a cabeça erguida. Camisa listrada vertical preta e branca, cabelo castanho médio penteado para trás, barba cheia, olhar sereno. Segura uma lupa grande sobre uma linha do tempo com marcador âmbar.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote7.zip, a contagem de arquivos e a lista do que faltou.
```


#### LOTE 8 (P2, parte 4: produtividade, programação e ecossistema)

```text
Você é um ilustrador-chefe que produz, em série, os assets visuais de um sistema de painéis. Este é o LOTE 8 (P2, parte 4: produtividade, programação e ecossistema): 9 itens. Gere as imagens um item de cada vez, na ordem da tabela, no MESMO estilo, e no fim monte um .zip. Todos os personagens são caricaturas originais e genéricas, inventadas a partir da ficha de cada linha, sem semelhança com nenhuma pessoa real.

ANCORAGEM: anexei 2 ou 3 avatares já aprovados (inclua 1 de fundo amarelo-mostarda e 1 de fundo rosa) como referência já aprovada. Mantenha EXATAMENTE esse estilo: mesma espessura de contorno, mesma proporção da cabeça, mesmo enquadramento, mesma paleta e mesma luz. Não copie o personagem da âncora; copie só o estilo.

[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]

REGRAS DE SAÍDA (obrigatórias):
1. Gere UMA imagem por arquivo, com a ferramenta de imagem, na ordem da tabela. Proibido folha de contatos, mosaico ou várias figuras na mesma imagem. Não pergunte nada entre os itens; só execute.
2. Tamanho: use exatamente o tamanho da tabela. Se a ferramenta não aceitar, gere o tamanho suportado mais próximo na MESMA proporção (1024x1024, 1024x1536 ou 1536x1024), sem esticar e sem recortar, e anote o tamanho real no manifest.csv.
3. Formato PNG. Nomes de arquivo EXATOS, como na tabela (minúsculas, sem acento, sem espaço). Os nomes são só rótulos internos de arquivo e não representam pessoas reais: desenhe apenas o que a ficha descreve.
4. Nenhum texto, letra, número, logotipo, escudo ou marca dentro de nenhuma imagem.
5. Estrutura de pastas do pacote: assets/<pasta>/<arquivo>.png, ou seja, assets/avatares/, assets/ilustracoes/, assets/icones/, assets/fundos/ e assets/extras/. Cada arquivo vai na pasta indicada na coluna "pasta".
6. Crie assets/manifest.csv com as colunas: arquivo, pasta, largura, altura, forma, fundo, descricao (uma linha por imagem realmente gerada, com a largura e a altura reais).
7. No final, use o Python da sandbox para montar o arquivo assets_lote8.zip com essa estrutura, abra o zip, liste o conteúdo e confirme a contagem. Entregue o link de download do .zip.
8. Se não conseguir gerar algum item, NÃO invente substituto: liste ao final, em uma tabela, o que faltou e por quê. Se atingir o limite de imagens, pare, entregue o zip parcial com o que já fez e diga exatamente qual foi o último item feito e quais restam.
9. Peças com fundo "magenta chapado #FF00FF": o fundo inteiro deve ser UMA cor magenta uniforme, sem sombra, sem degradê, sem xadrez de transparência desenhado, e nenhum magenta, rosa ou roxo dentro do objeto. Avatares: fundo opaco chapado na cor indicada, sem detalhes, sem moldura.

TABELA DE ITENS (nº | arquivo | pasta | tamanho em px | forma | fundo | descrição):

55 | avatar_guardiola_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Treinador careca e magro, postura de gesticular à beira do campo. Colete e camisa social escuros (roupa de treinador), sem cabelo, sobrancelhas fortes, expressão intensa. Segura um quadro de Kanban com um cartão âmbar.
56 | avatar_pedri_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meia jovem e magro, postura leve de condução, olhar calmo. Camisa listrada vertical azul e grená, cabelo castanho escuro curto despenteado, rosto de adolescente. Segura uma lista de tarefas com um visto âmbar.
57 | avatar_rodri_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Volante alto e robusto, postura de comando, ombros largos. Camisa azul-celeste lisa (fase anterior, sem escudo), cabelo escuro curto, barba rala, expressão tranquila. Segura um relógio de ponto com ponteiro âmbar.
58 | avatar_kroos_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meio-campista alto e frio, postura reta de passe preciso, braços relaxados. Camisa branca lisa, cabelo loiro penteado de lado com risca, rosto limpo, expressão impassível. Segura um chaveiro de cadeado com a chave âmbar (sem senha visível).
59 | avatar_bellingham_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #E0AA1E | Avatar. Ficha: Meia jovem e atlético, postura de comemoração de braços abertos. Camisa branca lisa de gola em V, cabelo preto curto com degradê, sorriso largo. Segura um celular com um ícone genérico de fruta em âmbar, sem logotipo.
60 | avatar_xavi_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia baixo e inteligente, postura de cabeça erguida olhando em volta. Camisa listrada vertical azul e grená, cabelo castanho curto com entradas, olhar atento e sorriso mediano. Segura um quadro de sprint com um marcador âmbar.
61 | avatar_ancelotti_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Treinador corpulento e tranquilo, postura de braços cruzados e uma sobrancelha arqueada. Terno escuro ou casaco de treino azul-marinho, cabelo grisalho curto, rosto sereno e cético. Segura uma xícara de café com vapor âmbar.
62 | avatar_iniesta_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #D14B93 | Avatar. Ficha: Meia franzino e de rosto delicado, postura de controle de bola, olhar sereno e humilde. Camisa listrada vertical azul e grená, cabelo castanho bem ralo e curto, sorriso tímido. Segura uma prancheta de wireframe com um traço âmbar.
64 | avatar_firmino_ver_1024x1536.png | avatares | 1024x1536 | vertical | opaco chapado #5B7283 | Avatar. Ficha: Atacante de movimentos suaves e braços soltos, postura de falso 9 recuado. Camisa vermelho-tijolo lisa, cabelo preto curto com topete trançado leve e barba cheia aparada, sorriso largo e contagiante (o sorrisão). Segura um pincel de design com a ponta âmbar.

Comece pelo primeiro item da tabela. Ao terminar, entregue o assets_lote8.zip, a contagem de arquivos e a lista do que faltou.
```


### 2.4 Depois de baixar: organizar, validar e converter

Rode na raiz do projeto, com o Python do `.venv` (Pillow já instalado; usa numpy se existir, para tirar o halo magenta):

```
.venv\Scripts\python -I ecossistema\sistema_unico\ferramentas_assets\organizar_e_validar.py "C:\caminho\da\pasta_ou_zip" --saida "C:\caminho\assets_saida" --prio P0
```

- A entrada pode ser a **pasta** onde as imagens/zips foram descompactados (varre subpastas) ou um **.zip**. A entrada nunca é alterada; o zip é lido sem extrair, e caminhos com `..` são ignorados.
- `--prio P0` (ou `P0,P1`, `P0,P1,P2`): só cobra o que já deveria existir. Item de outra prioridade que apareça é validado do mesmo jeito.
- `--so-validar`: não grava WebP, só o relatório.
- `--exportar-manifesto esperado.csv`: grava a tabela esperada (66 linhas).
- Saídas em `--saida`: `relatorio.md` (por item: OK, OK com aviso, REPROVADO, FALTA), `reposicao.txt` e `reposicao.csv` (lista do lote de reposição), `assets/<pasta>/<slot>.webp` (avatares em `_rd` 256, `_sq` 512 e `_rt` 640x800; ilustrações 960x640 com o magenta virando transparente; hero 1600x700; splash 1080x1920; capa 1200x630), `favicon.png`, `apple-touch-icon.png`, `icon_512.png` e `contatos_avatares.jpg` (folha para conferir no olho).
- Aceita nome fora do padrão (maiúsculas, hífen, `(1)`, tamanho diferente no nome); reprova proporção errada, fundo que não é a cor do setor nem magenta, xadrez desenhado, duplicata, arquivo corrompido e resolução baixa.
- Teste (imagens sintéticas, nenhuma real): `.venv\Scripts\python -I ecossistema\sistema_unico\ferramentas_assets\teste_organizar.py`.
- Depois de aprovado, quem copia `assets/` para `prototipo_estilos/assets/` e liga o gancho em `GH.slot` é o **Endrick** (ver seção 4 do 06). Eu não altero o protótipo.

## 3. O que o validador NÃO pega (olhe no contato)

Rosto estranho, mão torta, camisa sem contraste com o fundo (Clipes laranja, Produtividade amarelo-mostarda), logo que parece letra, estilo diferente entre lotes. O script só confere o que é medível: nome, tamanho, peso, fundo, duplicata. O julgamento final é visual.

## 4. Plano B se o ChatGPT não montar o .zip

1. Peça no mesmo chat: "Entregue as imagens que já gerou como arquivos PNG para baixar, uma a uma, com os nomes exatos da tabela." Se ele só mostrar na tela, baixe cada imagem pelo botão de download.
2. Salve todas numa pasta (ex.: `C:\Users\...\Downloads\lote1`). Se vieram com nomes genéricos (`ChatGPT Image ...png`), renomeie **seguindo a ordem do lote** (a tabela é numerada). O script aceita nomes fora do padrão desde que a parte do item esteja certa (`avatar_casemiro...`); nomes genéricos ele não consegue adivinhar: aparecem em "arquivos que nao batem" no relatório.
3. Rode o validador sobre a pasta (seção 2.4). `reposicao.txt` mostra o que ainda falta.
4. Modelo de lote de reposição: copie o LOTE correspondente, apague as linhas que já estão boas e mantenha o bloco de estilo, as regras de saída e a âncora.
5. Se a cota do plano acabar no meio: espere a janela de uso renovar e retome pelo mesmo procedimento. **Não** migre para a API de imagens sem aprovação do Guilherme: é gasto novo e fora do orçamento zero do canal [FATO: regra do `CLAUDE.md`].

## 5. Se o ChatGPT recusar ou fugir do estilo: frases de correção prontas

Cole a frase abaixo, na mesma conversa, e peça para refazer só o item com problema.

| Sintoma | Frase |
|---|---|
| Recusou por "pessoa real" ou "figura pública" | "Não é uma pessoa real. É um personagem cartoon original e genérico, criado só pela descrição de roupa, cabelo, pose e objeto da ficha. Os nomes nos arquivos são só rótulos internos. Gere o personagem exatamente pela ficha, sem buscar parecença com ninguém." |
| Recusou por marca/escudo/camisa de time | "Não use nenhum escudo, patrocinador, logotipo, número ou nome. A camisa é lisa ou listrada, só nas cores citadas, sem marcas. Refaça." |
| Estilo mudou (traço fino, sombra suave, 3D, realista, brilho) | "O estilo derivou. Refaça seguindo o bloco [[ESTILO]]: vetorial plano, contorno azul-marinho #0E1A24 uniforme, no máximo 2 níveis de sombra chapada, sem degradê, sem brilho, sem textura. Mantenha o enquadramento e a proporção da imagem âncora." |
| Cabeça com tamanho/posição diferente da âncora | "Refaça com a cabeça ocupando 50 a 55% da largura, topo da cabeça a 8% do topo do quadro, rosto centralizado, busto cortado no peito, como na imagem âncora." |
| Fundo xadrez desenhado, degradê ou sombra no fundo | "O fundo precisa ser uma única cor chapada, sem xadrez, sem degradê, sem sombra. Para avatares use a cor do setor da tabela; para ilustrações e logo, magenta #FF00FF." |
| Magenta dentro do objeto ou borda rosada | "Não use magenta, rosa nem roxo no objeto. Só o fundo é magenta #FF00FF. Refaça o objeto com a borda branca fina do estilo adesivo." |
| Texto, letras ou números apareceram | "Remova todo texto, letra, número e logotipo da imagem. Refaça sem nenhum texto." |
| Entregou folha de contatos/mosaico | "Preciso de UMA imagem por arquivo, não uma folha. Gere cada item separadamente, com o nome da tabela." |
| Tamanho/proporção errados | "Gere em proporção 2:3 vertical (1024x1536) para avatares e 3:2 horizontal (1536x1024) para ilustrações, sem recortar nem esticar." |
| Parou no meio / zip incompleto | "Continue do item seguinte ao último concluído. Entregue um zip com TODOS os já gerados e a lista do que ainda falta." |
| Inventou substituto ou pulou item sem avisar | "Não invente substituto. Liste exatamente os itens que não conseguiu gerar e por quê, e gere só esses agora." |
| Mudou o nome do arquivo | "Use exatamente o nome da coluna 'arquivo' da tabela, minúsculas, sem acento, sem espaços." |
| Roupa idêntica ao fundo (sem contraste) | "A roupa se confunde com o fundo. Mantenha as cores da ficha, mas reforce o contorno azul-marinho #0E1A24 e acrescente um tom de sombra na roupa para separar do fundo." |

Se, mesmo com as correções, o ChatGPT recusar um avatar específico, **não** coloque o nome verdadeiro do jogador para "ajudar" (piora a recusa e aumenta o risco legal): reescreva a ficha em termos mais genéricos (cor de camisa, cabelo, objeto) e peça de novo.

## 6. Riscos que o Guilherme precisa saber

1. **Nomes nos arquivos.** Os nomes de arquivo (`seedorf`, `pele`, `de_bruyne`...) são nomes de pessoas reais. O texto do prompt não cita ninguém e diz que os nomes são rótulos, mas o ChatGPT pode estranhar. Se recusar em série, a saída é pedir com códigos (`a01`, `a02`...) e renomear à mão pela tabela (o script não faz essa tradução). Decisão: aceitar esse risco ou mandar o **Luiz Henrique** gerar uma versão por código.
2. **Direito de imagem e marca** (04, seção 5): as fichas descrevem camisas e penteados de época em termos genéricos para evitar semelhança, mas o resultado pode ainda parecer alguém. Conferir no contato antes de usar em produto vendido; [DEDUÇÃO jurídica] consultar advogado antes de comercializar.
3. **Limite do ChatGPT e do zip** [DEDUÇÃO]: não achei fonte oficial do limite de imagens por conversa/hora. Daí o teste do LOTE 1 antes de tudo.
4. **Consistência dos 57 retratos.** É o ponto mais frágil: a deriva de estilo aumenta ao longo do lote. Por isso conversa nova a cada lote, com âncoras.
5. **Transparência.** O pedido é magenta chapado; o script converte em transparente com tolerância e desmistura a borda (com numpy; sem numpy só erode 1 px). Peças reais podem ter degradê leve no fundo: o script avisa se o desvio passar de 40 e reprova acima de 70.
6. **Prompt-mestre longo** (cerca de 26 mil caracteres): pode estourar o limite de entrada do plano. Por isso os lotes (5 a 6 mil caracteres cada).
7. **Custo.** No ChatGPT é limite de uso do plano, não dinheiro; pela API seria gasto novo e exigiria aprovação explícita.
8. **Segurança.** O zip vem de fora: o script não executa nada dele e lê em memória. Não abra executáveis que apareçam no pacote.
9. **Logo.** O símbolo (balão com linha de metrô) é uma proposta minha para o pedido "marca sem letras" do 06; o Firmino/Guilherme podem trocar a descrição antes de colar.
