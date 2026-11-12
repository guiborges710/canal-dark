# 07. Fichas de avatar (57 retratos): Luiz Henrique

Data: 2026-11-11. Autor: **Luiz Henrique**. Base: `06_assets_firmino_H.md` (estilo e prioridades), `03_elenco_agentes.md` e `05_pesquisa_jogadores_valverde.md`. Nenhuma imagem foi gerada; o prompt-mestre é do **Valverde**.

## Regras que valem para todas as fichas

- Decisão de segurança adotada por padrão (o Guilherme ainda pode mudar): caricatura cartoon "inspirada", SEM semelhança facial, sem nome de jogador, clube, escudo, número ou marca. Nenhuma ficha cita essas coisas; o texto de "ficha" pode ser colado direto no prompt.
- Cada ficha dá só: corpo/postura, pose da época, camisa/uniforme em termos genéricos, cabelo/barba/acessório, expressão e gesto, e um objeto da função. Tudo já pensado para busto até o peito, cabeça central (06, seção 3.2).
- Cores de camisa citadas são cores de roupa, não de paleta do estilo: se o ChatGPT achar "vermelho" forte demais, usar vermelho-tijolo; o acento âmbar do `[[ESTILO]]` fica em 1 detalhe pequeno (já escolhido como o objeto de função onde possível).
- Fundo = cor chapada do setor. Cuidado: em Clipes (laranja `#D9542D`) as camisas vermelhas e amarelas pedem contorno azul-marinho firme para não se fundir; em Produtividade (`#E0AA1E`) idem para camisas amarelas.
- Slug = `GH.slug(nome)`; arquivo final `avatar_<slug>_ver_1024x1536.png`.
- Onde o 03 estava "[CONFERIR FONTE]" a ficha usa só traço visual genérico de época (não afirma fato), então não carrega risco de erro factual. Marcação **[padrão adotado, pode mudar]** só onde há escolha pendente do Guilherme.

Cores de fundo: canal `#2F7DE1`, clipes `#D9542D`, inteligência `#7C5FDB`, trabalho (produtividade) `#E0AA1E`, finanças `#1FA37B`, programação `#D14B93`, ecossistema `#5B7283`, você `#0B63E5`.

---

# P0 (4)

### 1. `casemiro`
- Setor/fundo: Finanças, `#1FA37B`
- Ficha: Volante forte e largo, postura firme de peito aberto, queixo levemente erguido. Camisa branca lisa de gola redonda, cabelo escuro bem curto e barba cheia aparada, sobrancelhas marcadas. Expressão séria e confiante, braço direito ao peito como quem protege; segura uma calculadora pequena com o acento âmbar no visor.
- Função: recebimentos, gastos e dashboard financeiro.

### 2. `ronaldo`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Atacante potente, ombros largos, pose de corrida contida, sorriso de dentes grandes e olhar alegre. Camisa amarela canarinho de gola verde (sem escudo), cabelo raspado nas laterais com um pequeno triângulo no alto da frente, o penteado marcante da época. Dedo apontando para o alto; um celular com notificação em âmbar na mão esquerda.
- Função: central de controle pessoal e Telegram.

### 3. `de_bruyne`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Meia armador de porte alto e magro, postura de quem vai fazer o passe longo, pescoço levemente inclinado. Camisa azul-celeste lisa, cabelo ruivo-loiro curto penteado de lado e barba rala ruiva, sardas simples. Expressão calma e concentrada, uma sobrancelha levemente erguida; segura uma prancheta com setas de passes desenhadas.
- Função: coordena a produção do canal de ponta a ponta.

### 4. `luiz_henrique`
- Setor/fundo: Ecossistema, `#5B7283`
- Ficha: Treinador de meia-idade, magro e atlético, postura de pé com braços cruzados ou uma mão na cintura. Agasalho de treino azul-marinho com zíper fechado até o pescoço (ou terno escuro sem gravata), cabelo grisalho curtíssimo, queixo marcado, barba por fazer. Olhar firme e sorriso discreto de quem tem o plano; segura um mapa de metrô dobrado com um ponto âmbar. **[padrão adotado, pode mudar]** (fase "bicampeão", roupa de treinador moderna; a escolha da temporada não muda a ficha visual.)
- Função: cabeça do ecossistema; cria agentes e setores e mantém o mapa.

---

# P1 (22 + você)

### 5. `olise`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Ponta ágil e esguio, ombros caídos, postura de drible curto com o corpo levemente de lado. Camisa vermelho-tijolo de gola em V, cabelo escuro curto com degradê, expressão de quem esconde a jogada, sorriso de canto. Segura uma pequena paleta de cores com um toque âmbar.
- Função: cenas animadas do canal (`cenas.json`).

### 6. `valverde`
- Setor/fundo: Ecossistema, `#5B7283`
- Ficha: Meio-campista atlético de corrida, peito aberto, postura inclinada para frente como quem parte em velocidade. Camisa branca lisa, cabelo castanho médio penteado para trás, barba curta, olhar determinado. Segura um chip/circuito simples com um detalhe âmbar.
- Função: engenharia de IA e do sistema.

### 7. `alisson`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Goleiro alto, ombros largos, postura de prontidão com as duas mãos à frente. Uniforme de goleiro amarelo-limão de mangas longas, luvas brancas com detalhe azul, cabelo curto escuro, barba curta e cheia. Olhar atento, sorriso mínimo; uma lupa pequena sobre uma luva.
- Função: QA, testa e procura falhas.

### 8. `salah`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Ponta de corpo leve e rápido, ombros estreitos, postura de arrancada. Camisa vermelho-tijolo lisa, cabelo preto bem cacheado volumoso, barba preta aparada, sorriso largo e simpático. Segura uma lupa grande sobre uma tela de vídeo.
- Função: acha fontes e confirma a autorização dos clipes.

### 9. `vini`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Ponta magro e explosivo, postura de drible com um ombro à frente, pequenos passos de dança. Camisa branca com gola azul-marinho fina, cabelo preto curto com um desenho raspado de linha lateral, sorriso largo de desafio. Segura um carimbo de aprovação com o acento âmbar.
- Função: auditor de conformidade do texto e do vídeo final.

### 10. `neymar`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Ponta esquerdo de corpo magro e ágil, postura de quem vai driblar, pé sobre a bola imaginária. Camisa listrada vertical azul e grená, calção azul, cabelo curto com topete clareado e brinco pequeno, sorriso confiante e brincalhão. Segura um bloco de roteiro com uma caneta âmbar.
- Função: ângulo, roteiro e direção viral.

### 11. `raphinha`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Ponta canhoto, baixo e musculoso, postura de chute com o pé esquerdo recuado. Camisa listrada vertical azul e grená, cabelo curto escuro com topete leve, expressão intensa, sorriso curto. Segura um lápis e uma régua com uma peça de componente em âmbar.
- Função: curador e desenhista de componentes visuais.

### 12. `seedorf`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Meio-campista de físico muito forte, ombros enormes, postura imponente com o peito para frente. Camisa listrada vertical vermelho-tijolo e preta, cabeça raspada, brinco pequeno, sorriso amplo e olhar sábio. Segura uma moldura de miniatura de vídeo com o acento âmbar.
- Função: prompt de miniatura (thumbnail), sem gerar a imagem.

### 13. `memphis`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Atacante expressivo, postura relaxada com atitude, corrente fina no pescoço. Camisa vermelha e branca em faixas largas, cabelo curto com topete descolorido, barba cheia aparada e tatuagens estilizadas nos antebraços. Sorriso de lado, um dedo apontando para fora do quadro; segura um celular com o gráfico subindo em âmbar.
- Função: referências virais e postagem manual.

### 14. `rivaldo`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Canhoto esguio e alto, postura descontraída, ombros caídos. Camisa listrada vertical azul e grená, cabelo raspado curtíssimo, queixo fino, olhar de quem avalia. Segura uma pequena placa de nota com visto em âmbar.
- Função: nota de qualidade da fonte do vídeo.

### 15. `kaka`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Meia elegante e alto, postura de aceleração com a cabeça erguida. Camisa listrada vertical vermelho-escuro e preta, cabelo castanho bem curto, rosto limpo e simpático, sorriso sereno. Segura uma tesoura de corte ligada a uma fita de vídeo âmbar.
- Função: escolhe os melhores trechos.

### 16. `zidane`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Meia alto e elegante, postura de controle de bola no peito, movimento suave. Camisa azul-royal lisa de gola redonda, careca com testa ampla, sobrancelhas retas, expressão calma e dominante. Segura uma claquete com marca âmbar.
- Função: gancho e fecho de cada corte.

### 17. `zico`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Meia clássico, postura de cobrar falta, uma mão no quadril. Camisa listrada horizontal vermelho-tijolo e preta, cabelo castanho ondulado médio, sobrancelhas grossas, sorriso de líder. Segura um backlog (quadro de cartões) com um cartão âmbar.
- Função: PO de programação; backlog e aceite.

### 18. `lamine_yamal`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Ponta jovem e magro, postura leve de drible, olhar atrevido de adolescente. Camisa listrada vertical azul e grená, cabelo preto curto com tranças curtas no alto, corrente fina. Sorriso de quem está se divertindo; segura um celular com um post em âmbar.
- Função: rascunhos de LinkedIn (aprovação do Guilherme).

### 19. `modric`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Meia baixo e magro, postura de passe curto de peito aberto, ombros estreitos. Camisa xadrez vermelha e branca em quadros grandes (não um escudo), cabelo loiro mais comprido caindo na testa, olhar aguçado e sorriso curto. Segura um livro de notas e uma lupa âmbar.
- Função: pesquisa o tema e grava `notas.md`.

### 20. `courtois`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Goleiro muito alto e magro, postura de braços abertos cobrindo o gol, cabeça um pouco inclinada. Uniforme de goleiro verde-limão de mangas longas, luvas brancas, cabelo castanho curto, barba rala. Expressão séria e atenta; segura uma lista de checagem com um visto âmbar.
- Função: confere o roteiro contra as notas.

### 21. `mbappe`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Atacante jovem e explosivo, postura de arrancada, corpo inclinado e pernas fortes. Camisa azul-marinho lisa de gola redonda, cabelo preto bem curto, queixo marcado, sorriso confiante. Segura uma etiqueta de título com um raio âmbar.
- Função: título, descrição, tags e miniatura.

### 22. `vitinho`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Atacante de porte médio e ágil, postura de quem faz o corte para dentro. Camisa listrada horizontal vermelho-tijolo e preta, cabelo escuro curto com degradê, barba curta, sorriso de canto. Segura uma prancheta de resumo com o acento âmbar. **[padrão adotado, pode mudar]** (Flamengo 2019/20, camisa listrada; alternativa: Internacional 2015/16, camisa vermelha lisa.)
- Função: consolida o ciclo do setor de inteligência.

### 23. `rodrygo`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Ponta magro e rápido, postura de arrancada. Camisa branca lisa de gola em V, cabelo escuro curto, sorriso aberto, olhar travesso. Segura uma engrenagem com um detalhe âmbar.
- Função: dev back-end.

### 24. `endrick`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Centroavante jovem e forte, ombros largos, postura de finalização com sorriso de moleque. Camisa verde-escura lisa, cabelo curto crespo e barba rala de adolescente. Segura um monitor com uma janela de código em âmbar. **[padrão adotado, pode mudar]** (Palmeiras 2023, camisa verde; alternativa: Lyon 2026.)
- Função: dev front-end.

### 25. `thiago_silva`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Zagueiro capitão, físico forte, ombros largos, postura de comando. Camisa azul-marinho lisa com braçadeira de capitão amarelo-âmbar no braço, cabelo castanho curto com entradas, barba rala grisalha, olhar sereno. Segura um diagrama de arquitetura (caixas ligadas).
- Função: tech lead e arquiteto.

### 26. `marquinhos`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Zagueiro capitão firme, ombros largos, postura de liderança. Camisa azul-marinho lisa, cabelo castanho curtíssimo, barba curta e rala, sorriso humilde. Segura um foguete pequeno de lançamento com um detalhe âmbar.
- Função: DevOps e release.

### 27. `voce`
- Setor/fundo: Você, `#0B63E5`
- Ficha: Busto de pessoa genérica e neutra, sem rosto individualizado: cabeça lisa com apenas dois olhos redondos pequenos, uma curva de sorriso, sem cabelo definido e sem traços reconhecíveis. Camisa lisa branco-frio de gola redonda, postura relaxada de quem decide. Segura um carimbo de "aprovar" com um visto âmbar.
- Função: o Guilherme (dono); pontos de decisão, menu de usuário, estações de aprovação.

---

# P2 (30)

### 28. `haaland`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Centroavante gigante e muito forte, postura de peito estufado e olhar fixo. Camisa azul-celeste lisa, cabelo loiro comprido preso em coque ou rabo, sem barba, expressão de foco intenso. Segura uma bússola com o acento âmbar.
- Função: nicho e ideias de pauta.

### 29. `messi`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Baixo e compacto, ombros caídos, postura de condução de bola de cabeça baixa. Camisa listrada vertical azul e grená, cabelo castanho curto, barba rala, olhar de calma e foco. Segura um papel com uma tese de uma frase e um sublinhado âmbar.
- Função: tese, pergunta e comentário próprio de cada vídeo.

### 30. `cristiano`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Atacante atlético de tronco largo, postura de herói com o queixo erguido. Camisa vermelho-tijolo lisa de gola alta, cabelo preto penteado para trás com gel, sobrancelhas retas, sorriso confiante. Segura um gráfico de barras subindo com a barra final âmbar.
- Função: eleva o roteiro para viralizar.

### 31. `barcola`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Ponta esguio e ágil, postura de arrancada para a esquerda. Camisa azul-marinho lisa de gola redonda, cabelo preto curto com degradê, sorriso discreto. Segura uma moldura horizontal 16:9 com o acento âmbar.
- Função: cenas sketch dos vídeos horizontais 16:9.

### 32. `kane`
- Setor/fundo: Canal, `#2F7DE1`
- Ficha: Centroavante alto e robusto, queixo marcado, postura de finalizador. Camisa branca lisa de gola em V, cabelo castanho-claro curto penteado de lado, barba rala, expressão serena. Segura um microfone com a espuma âmbar.
- Função: narra os vídeos com a voz do Guilherme.

### 33. `hugo_souza`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Goleiro jovem e alto, braços abertos, postura de prontidão. Uniforme de goleiro cinza-chumbo de mangas longas, luvas brancas, cabelo castanho curto, rosto franco. Segura um catálogo de pastas com uma pasta âmbar.
- Função: cataloga canais dark.

### 34. `fagner`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Lateral direito rápido e forte, postura de quem sobe pela direita, braçadeira de capitão em âmbar. Camisa listrada vertical branca e preta, cabelo escuro curto, barba curta, sorriso tranquilo. Segura um bloco de títulos com uma tag âmbar.
- Função: títulos, descrições e tags dos canais catalogados.

### 35. `andre_carrillo`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Ponta rápido e de porte médio, postura de drible, olhar vivo. Camisa listrada horizontal verde e branca, cabelo preto liso penteado para trás, barba curta. Segura uma tela de miniatura com um quadro âmbar. **[padrão adotado, pode mudar]** (fase do ponta com camisa verde e branca; traço de rosto genérico.)
- Função: analisa thumbnails de canais catalogados.

### 36. `raniele`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Volante forte e de passo largo, postura de marcação, ombros fortes. Camisa listrada vertical branca e preta, cabelo escuro curto com degradê, expressão de concentração. Segura um relógio de produção com ponteiro âmbar. **[padrão adotado, pode mudar]** (fase escolhida sem fonte; traço genérico.)
- Função: como os canais produzem (ritmo, formato, cadência).

### 37. `yuri_alberto`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Centroavante forte e alto, ombros largos, postura de finalização. Camisa listrada vertical branca e preta, cabelo escuro curto com topete discreto, sobrancelhas retas, sorriso de convicção. Segura um painel com linha de métrica subindo em âmbar.
- Função: métricas do canal próprio.

### 38. `garro`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Meia criativo e franzino, postura de passe de calcanhar, olhar de visão. Camisa listrada vertical branca e preta, cabelo castanho médio ondulado, barba rala, sorriso levemente travesso. Segura um chip com antena e um brilho âmbar.
- Função: ferramentas de IA para a produção (scout de tecnologia).

### 39. `busquets`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Volante alto e magro, postura de pivô de braços ligeiramente abertos, ombros caídos. Camisa listrada vertical azul e grená, cabelo escuro curto, sobrancelhas grossas, olhar frio e atento. Segura uma tela de estudo de vídeo com um play âmbar.
- Função: aprendiz, estuda vídeos dos canais dark.

### 40. `xabi_alonso`
- Setor/fundo: Inteligência, `#7C5FDB`
- Ficha: Treinador alto e elegante, postura reta de braços cruzados à beira do campo. Terno ou casaco escuro fechado sem gravata (roupa de treinador), cabelo castanho curto, barba rala aparada, olhar calmo. Segura uma pasta de referências com marcador âmbar.
- Função: curador de referências para estudo.

### 41. `pele`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Atacante atlético e sorridente, postura de comemoração com um punho erguido. Camisa amarela canarinho de gola verde, calção azul, cabelo preto bem curto, sorriso enorme. Segura uma faixa de chefe com a estrela âmbar.
- Função: chefe do setor de clipes.

### 42. `figo`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Ponta alto e elegante, postura altiva com o peito aberto. Camisa branca lisa de gola redonda, cabelo castanho médio-longo preso atrás, barba rala, olhar intenso. Segura um claquete com marca âmbar.
- Função: escolhe a frase mais forte e o teaser.

### 43. `totti`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Meia-atacante de porte médio, postura de ousadia, olhar de artista. Camisa vinho e amarela em duas cores lisas, cabelo castanho curto penteado com topete, barba curta, sorriso brincalhão. Segura uma balança de nota com um peso âmbar.
- Função: nota de potencial de cada corte.

### 44. `buffon`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Goleiro forte e compacto, peito largo, postura de líder atrás das luvas. Uniforme de goleiro preto de mangas longas, luvas brancas, cabelo escuro curto, mandíbula larga, olhar sério. Segura um selo de aprovação com a borda âmbar.
- Função: gate de originalidade dos clipes.

### 45. `lewandowski`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Centroavante de corpo atlético e alto, postura de finalizador contido. Camisa vermelho-tijolo lisa, cabelo castanho curto penteado de lado, barba curta, sorriso medido. Segura um bloco de legenda com uma hashtag âmbar sem texto.
- Função: legenda e hashtags para cada plataforma.

### 46. `roberto_carlos`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Lateral esquerdo baixo e extremamente forte, coxas largas, postura de chute potente. Camisa branca lisa, cabelo preto raspado curto, sorriso largo. Segura um celular com perfil novo aberto e um destaque âmbar.
- Função: gestor de perfis novos de TikTok e Instagram.

### 47. `pirlo`
- Setor/fundo: Clipes, `#D9542D`
- Ficha: Meia armador calmo e elegante, postura de passe longo com a cabeça erguida. Camisa listrada vertical preta e branca, cabelo castanho médio penteado para trás, barba cheia, olhar sereno. Segura uma lupa grande sobre uma linha do tempo com marcador âmbar.
- Função: acha vídeos longos para cortar.

### 48. `guardiola`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Treinador careca e magro, postura de gesticular à beira do campo. Colete e camisa social escuros (roupa de treinador), sem cabelo, sobrancelhas fortes, expressão intensa. Segura um quadro de Kanban com um cartão âmbar.
- Função: PO, Kanban e Trello.

### 49. `pedri`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Meia jovem e magro, postura leve de condução, olhar calmo. Camisa listrada vertical azul e grená, cabelo castanho escuro curto despenteado, rosto de adolescente. Segura uma lista de tarefas com um visto âmbar.
- Função: tarefas e projetos.

### 50. `rodri`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Volante alto e robusto, postura de comando, ombros largos. Camisa azul-celeste lisa (fase anterior, sem escudo), cabelo escuro curto, barba rala, expressão tranquila. Segura um relógio de ponto com ponteiro âmbar.
- Função: apontamento de horas.

### 51. `kroos`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Meio-campista alto e frio, postura reta de passe preciso, braços relaxados. Camisa branca lisa, cabelo loiro penteado de lado com risca, rosto limpo, expressão impassível. Segura um chaveiro de cadeado com a chave âmbar (sem senha visível).
- Função: calendário de senhas e acessos (sem guardar segredo).

### 52. `bellingham`
- Setor/fundo: Produtividade, `#E0AA1E`
- Ficha: Meia jovem e atlético, postura de comemoração de braços abertos. Camisa branca lisa de gola em V, cabelo preto curto com degradê, sorriso largo. Segura um celular com a maçã estilizada genérica em âmbar (sem logotipo).
- Função: dicas conceituais de iOS.

### 53. `xavi`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Meia baixo e inteligente, postura de cabeça erguida olhando em volta. Camisa listrada vertical azul e grená, cabelo castanho curto com entradas, olhar atento e sorriso mediano. Segura um quadro de sprint com um marcador âmbar.
- Função: Scrum Master.

### 54. `ancelotti`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Treinador corpulento e tranquilo, postura de braços cruzados e uma sobrancelha arqueada. Terno escuro ou casaco de treino azul-marinho, cabelo grisalho curto, rosto sereno e cético. Segura uma xícara de café com vapor âmbar. **[padrão adotado, pode mudar]** (fase "Real Madrid 2021/22"; só a roupa de treinador entra, nenhuma referência ao clube.)
- Função: coach de processo ágil.

### 55. `iniesta`
- Setor/fundo: Programação, `#D14B93`
- Ficha: Meia franzino e de rosto delicado, postura de controle de bola, olhar sereno e humilde. Camisa listrada vertical azul e grená, cabelo castanho bem ralo e curto, sorriso tímido. Segura uma prancheta de wireframe com um traço âmbar.
- Função: UX do Corte.

### 56. `dembele`
- Setor/fundo: Canal (Reels), `#2F7DE1`
- Ficha: Ponta veloz e magro, postura de arrancada, dribla com os dois pés. Camisa azul-marinho lisa com acabamento vermelho-tijolo na gola, cabelo curto com degradê e barba rala. Sorriso de canto; segura um celular em pé (formato vertical) com a tela em âmbar.
- Função: mini-fluxo de Reels do Instagram.

### 57. `firmino`
- Setor/fundo: Ecossistema, `#5B7283`
- Ficha: Atacante de movimentos suaves e braços soltos, postura de falso 9 recuado. Camisa vermelho-tijolo lisa, cabelo preto curto com topete trançado leve e barba cheia aparada, sorriso largo e contagiante (o sorrisão). Segura um pincel de design com a ponta âmbar.
- Função: atalho para a skill de design de front-end.

---

## Pendências

1. O 03 e o 06 contam 56 agentes mais "você" (57 retratos); o mapa 01 fala em 57 agentes. A diferença de 1 segue a conferir (já registrada no 03).
2. As marcas **[padrão adotado, pode mudar]**: Luiz Henrique, Vitinho, Endrick, Raniele, Carrillo, Ancelotti. Mudar de temporada altera só a cor/padrão da camisa na ficha.
3. Se o Guilherme não aceitar a caricatura "inspirada" e quiser semelhança, as fichas mudam: o risco de imagem e de marca é dele (aviso do 03).
4. Segurança: nenhuma ficha cita nome, clube, escudo, número ou marca. O **Valverde** deve conferir o prompt-mestre com a mesma regra (o objeto de função não deve ter logotipo, e o celular da ficha do Bellingham é genérico).
