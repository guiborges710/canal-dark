# Relatório Sidorf: swiftui-identidade-lista

## Identificação
- Arquivo: output/swiftui-identidade-lista/video.mp4 (frames em thumbnails/sidorf/swiftui-identidade-lista/frames/)
- Título: SwiftUI: por que o check pula de linha ao remover um item?
- Duração: cerca de 39 s, estilo sketch (caderno pautado)
- Tema: identidade de linha em listas SwiftUI (ForEach com índice e id: \.self). Fora do nicho de gerações, pedido direto do Guilherme.
- Resumo: ao remover um item, o check aparece em outra linha. Hipótese (não verdade universal): o índice é a identidade, então o estado fica preso à posição. Teste: id único e estável (Identifiable com UUID ou id do banco). O vídeo ressalva que é só uma causa possível.

## Diagnóstico
- Gancho: o check na linha errada depois de remover um item.
- Emoção: curiosidade técnica e reconhecimento ("já vi isso").
- Elemento recomendado: lista de 3 linhas de tarefas, com o check na linha errada e uma seta curva mostrando o "pulo".
- Público provável: devs iOS/SwiftUI iniciantes e intermediários, brasileiros.
- Estilo: variante sketch da identidade (papel bege pautado, traço grafite, vermelho marcador #B91C1C, âmbar #F2B13C, check verde como no vídeo), para manter o reconhecimento entre vídeo e capa.
- Honestidade: a capa não promete solução garantida. Usa pergunta e o selo SWIFTUI, sem "resolvido" nem "o erro que todo dev comete".

## Conceitos
1. Curiosidade: três linhas de tarefa, uma removida (riscada em vermelho) e o check na linha seguinte, com seta curva. Texto: "O CHECK PULOU?". Selo: SWIFTUI. Legível em tela pequena (um objeto, uma pergunta). Coerente com a cena 0 do vídeo.
2. Impacto: um check verde grande saltando no ar entre duas linhas, com X vermelho sobre a linha removida. Forte visualmente, mas perde o contexto de lista; o assunto fica menos claro.
3. Clareza: duas colunas, ÍNDICE vs ITEM, cada uma com a lista e o check. Texto: "ÍNDICE OU ITEM?". Explica a tese, mas é mais densa e entrega a resposta, reduzindo a curiosidade.

## Escolha final
Principal: conceito 1. Um elemento dominante, pergunta visual simples, fiel ao frame de abertura e ao título; o ponto de interrogação sinaliza dúvida em vez de veredito, o que combina com o tom de hipótese do vídeo. Alternativa: conceito 3, com composição diferente (duas colunas), para quem prefere clareza do assunto.

## Prompt definitivo para ChatGPT
```
Crie uma thumbnail vertical para um YouTube Short, proporção 9:16, exatamente 1080 x 1920 pixels, formato PNG. Não faça perguntas, gere direto.

ASSUNTO: um problema comum em listas do SwiftUI: depois de remover um item da lista, o check (marcação de concluído) aparece em outra linha. É uma pergunta visual, não uma solução.

ESTILO: ilustração 2D estilo caderno / sketch educativo. Fundo de folha de caderno bege (#F5F3EA) com linhas horizontais azul-acinzentadas finas e uma margem vermelha clara vertical à esquerda. Traço de caneta grafite (#1F2937) levemente tremido, contornos definidos, sombras sólidas discretas. Poucas cores vibrantes: vermelho de marcador #B91C1C, âmbar #F2B13C, verde de check #2E9E55, branco, grafite.

ELEMENTO PRINCIPAL (dominante, no centro, grande): três cartões brancos horizontais empilhados, cada um com uma caixinha de seleção à esquerda e uma linha de texto desenhada como rabisco (sem texto legível). O cartão do meio está riscado em vermelho, com um pequeno X vermelho, como item removido. Um check verde grande e grosso está sobre a caixinha do cartão de baixo, fora do lugar esperado, com uma seta curva vermelha mostrando que o check "pulou" de uma linha para outra. O check deve ser bem visível em tela de celular.

EXPRESSÃO: sem personagens, sem rostos, sem pessoas. A emoção vem da seta e do check fora do lugar (estranhamento, curiosidade).

TEXTO (exato, com acento e pontuação):
1) Texto principal: "O CHECK PULOU?" em maiúsculas, sans-serif extra pesada (estilo Arial Black / Montserrat Black), cor vermelho #B91C1C com contorno grafite fino, tamanho grande (cerca de 80% da largura da imagem), logo acima do elemento principal, dentro da área segura.
2) Selo pequeno em formato de etiqueta âmbar (#F2B13C) com contorno grafite e o texto "SWIFTUI" em grafite, maiúsculas, peso pesado, tamanho pequeno, no canto superior direito do elemento principal.
Nenhum outro texto. Nenhum código legível.

COMPOSIÇÃO E ÁREAS SEGURAS: deixe livres os 15% superiores e os 20% inferiores da imagem (só fundo de caderno, sem texto nem elementos importantes), pois a interface do YouTube cobre essas áreas. Todo o conteúdo importante fica na faixa central. Hierarquia: 1) lista com check fora do lugar, 2) texto "O CHECK PULOU?", 3) selo "SWIFTUI". Alto contraste, legível em tela pequena de smartphone.

PROIBIDO: texto extra, marca d'água, logotipos (inclusive Apple, Swift ou Xcode), pessoas reais ou rostos, emojis, bandeiras, elementos copiados de outros canais, números, promessas como "resolvido" ou "solução". Não gerar proporção horizontal ou quadrada.

CRITÉRIOS DE QUALIDADE: texto sem erros de ortografia, exatamente como especificado; traços limpos; apenas um elemento dominante; entendível em 1 segundo mesmo em miniatura; 9:16, 1080x1920.
```

## Prompt alternativo
```
Crie uma thumbnail vertical para um YouTube Short, proporção 9:16, exatamente 1080 x 1920 pixels, formato PNG. Não faça perguntas, gere direto.

ASSUNTO: comparação visual entre identificar as linhas de uma lista de app pelo ÍNDICE (posição) ou pelo ITEM. É a hipótese de que, ao remover um item, o check fica preso à posição e não ao item.

ESTILO: ilustração 2D estilo caderno / sketch educativo. Fundo de folha de caderno bege (#F5F3EA) com linhas azul-acinzentadas finas e margem vermelha clara à esquerda. Traço grafite (#1F2937) levemente tremido, contornos definidos, sombras sólidas discretas. Cores: vermelho de marcador #B91C1C, âmbar #F2B13C, verde de check #2E9E55, branco, grafite.

COMPOSIÇÃO: duas colunas lado a lado no centro da imagem, separadas por um traço vertical fino. Cada coluna tem 3 cartões brancos empilhados com caixinha de seleção e rabisco de texto (sem texto legível).
- Coluna esquerda: etiqueta "ÍNDICE" (âmbar, texto grafite). O check verde está em uma linha que não corresponde ao item original, com seta curva vermelha e um pequeno X vermelho.
- Coluna direita: etiqueta "ITEM" (âmbar, texto grafite). O check verde acompanha o mesmo cartão, que tem uma pequena etiqueta de ID desenhada como rabisco (sem texto legível), com um visto verde de confirmação ao lado.

TEXTO (exato, com acento): "ÍNDICE OU ITEM?" em maiúsculas, sans-serif extra pesada (Arial Black / Montserrat Black), grafite #1F2937 sobre faixa âmbar #F2B13C com contorno grafite, tamanho grande (cerca de 80% da largura), logo acima das duas colunas. Selo pequeno "SWIFTUI" em carimbo vermelho #B91C1C com texto branco, menor, no canto de uma das colunas. Etiquetas das colunas: "ÍNDICE" e "ITEM". Nenhum outro texto, nenhum código legível.

ÁREAS SEGURAS: 15% superior e 20% inferior livres (só fundo de caderno). Conteúdo na faixa central. Hierarquia: 1) as duas listas, 2) "ÍNDICE OU ITEM?", 3) selo. Alto contraste, legível em celular.

PROIBIDO: texto extra, marca d'água, logotipos (Apple, Swift, Xcode), pessoas ou rostos, emojis, números, promessas de solução garantida, elementos copiados de outros canais, formato horizontal ou quadrado.

QUALIDADE: ortografia exata, traços limpos, assunto claro em 1 segundo em miniatura, 9:16, 1080x1920.
```

## Checklist
- [x] Vertical 9:16, 1080x1920, PNG
- [x] Adequada para smartphone (um elemento, texto grande)
- [x] Coerente com o vídeo (cenas 0 e 4; tom de hipótese, sem promessa falsa)
- [x] Identidade consistente (variante sketch registrada no yaml)
- [x] Texto revisado (acentos corretos: "O CHECK PULOU?", "SWIFTUI"; alternativo "ÍNDICE OU ITEM?")
- [x] Nenhum elemento copiado de terceiros, sem logotipos Apple/Swift
- [x] Prompt pronto para colar
- [x] Nenhuma imagem gerada
