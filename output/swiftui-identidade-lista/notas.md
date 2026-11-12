# Notas: identidade em lista SwiftUI + pair programming (slug swiftui-identidade-lista)

Pesquisa em 2026-10-30. Texto em minhas palavras. Fonte ao lado de cada item.
Observação: as páginas de documentação da Apple (developer.apple.com/documentation) carregam por JavaScript; consegui ler o conteúdo de ForEach pelo endpoint JSON da própria Apple. A página de Identifiable não foi lida (só o título), então NADA aqui é atribuído a ela.

## 1. Fatos sobre identidade em ForEach / List

1. ForEach monta views sob demanda a partir de uma coleção. Cada elemento precisa ser Identifiable ou receber um parâmetro `id`; é essa identidade que permite ao SwiftUI acompanhar cada elemento entre atualizações.
   Fonte (primária, Apple): https://developer.apple.com/documentation/swiftui/foreach (lido via https://developer.apple.com/tutorials/data/documentation/swiftui/foreach.json)

2. No WWDC21 "Demystify SwiftUI": em ForEach sobre faixa constante, o deslocamento (offset) é a identidade; faixa dinâmica gera erro, e naquele ano passou a haver aviso para faixa não constante.
   Fonte (primária, Apple): https://developer.apple.com/videos/play/wwdc2021/10022/

3. Mesma sessão: o identificador precisa ser estável (não muda com o tempo) e único (duas views não compartilham). Cuidado com ids aleatórios, principalmente em propriedade computada.
   Fonte: https://developer.apple.com/videos/play/wwdc2021/10022/

4. Mesma sessão, exemplo de índice como identidade: inserir na posição zero desloca a identidade de todos os outros itens, e a animação da inserção aparece no fim da lista. O palestrante recomenda id persistente, como id de banco de dados ou derivado de propriedades estáveis. (Esse exemplo é de animação, não de check trocado de linha.)
   Fonte: https://developer.apple.com/videos/play/wwdc2021/10022/

5. Mesma sessão: o estado (@State, @StateObject) fica atrelado à identidade da view. Quando a identidade muda, o estado é substituído; a identidade de cada elemento do ForEach delimita o tempo de vida das views e do estado dele. Esta é a ponte conceitual para "o check foi parar em outra linha": se a identidade é a posição, o estado pertence à posição, não ao item.
   Fonte: https://developer.apple.com/videos/play/wwdc2021/10022/

6. Swift by Sundell: ForEach sobre `indices` com `id: \.self` silencia o aviso, mas faz o índice virar a identidade da view. O SwiftUI passa a tratar o índice como estável, embora ele não continue ligado à mesma nota quando itens são inseridos, removidos ou reordenados. O autor diz que pode funcionar, mas alerta para comportamento estranho ou crash se o array mudar rápido. A correção proposta: dar identidade única a cada elemento (os ids do próprio modelo ou uma coleção de índices identificáveis).
   Fonte: https://swiftbysundell.com/articles/bindable-swiftui-list-elements

7. Hacking with Swift: SwiftUI precisa distinguir cada view dinâmica. Três formas: tipo Identifiable (usa a propriedade `id`), key path para propriedade única (ex.: ISBN), ou `\.self` (usa o hash; exige Hashable). Valores de conteúdo idêntico geram o mesmo hash, o que pode causar problemas de animação.
   Fonte: https://www.hackingwithswift.com/books/ios-swiftui/why-does-self-work-for-foreach

8. Nil Coalescing (livro "The SwiftUI Way"): modelos devem ser Identifiable com identificador armazenado e único (UUID ou chave primária inteira), que não muda quando outras propriedades são editadas. Usar o valor inteiro (`\.self`) é ruim porque qualquer edição parece remoção de uma linha e inserção de outra. A página NÃO fala de índice/offset; a conclusão de que índice é mau id por esse critério é inferência minha.
   Fonte: https://books.nilcoalescing.com/the-swiftui-way/building-a-performant-and-stable-interface/maximizing-the-performance-of-dynamic-lists/
   (Um resumo de busca atribuiu ao Nil Coalescing a frase de que nem offset nem índice devem ser id em coleção mutável, mas isso vem de outro texto do mesmo site, https://nilcoalescing.com/blog/UsingEnumeratedWithListAndForEach, que NÃO abri; não usar sem conferir.)

## 2. Sobre a correção (UUID criado junto com o item)

- O exemplo da Apple em ForEach usa um `id` computado a partir do nome, e os materiais da sessão WWDC21 e do Nil Coalescing recomendam id persistente (banco/UUID/chave primária) e estável. Ou seja: `let id = UUID()` atribuído uma única vez na criação do item é coerente com as fontes (itens 3, 4, 8). A forma exata `let id = UUID()` em código não aparece literalmente nas páginas que li; é aplicação do princípio.
- Contraponto importante (WWDC21 e item 3): id aleatório gerado de novo a cada leitura (propriedade computada) é erro, porque quebra a estabilidade.

## 3. Pair programming: piloto/navegador

- Driver (piloto): fica no teclado, foca numa meta pequena e imediata e deve falar o que faz enquanto digita. Navigator (navegador): observa, revisa o código conforme sai, mantém a visão geral (bugs, próximos passos, obstáculos) e anota ideias para discutir depois, sem interromper o fluxo do piloto. Tese do artigo: uma pessoa só dificilmente combina o pensamento tático e o estratégico.
- Dicas do artigo: uma meta minúscula por vez (teste, mensagem de commit ou post-it); trocar de papel regularmente; navegador não dita tecla por tecla; esperar uns cinco segundos antes de corrigir; piloto não monopoliza o teclado.
- Autoria: Birgitta Böckeler e Nina Siessegger (publicado no site de Martin Fowler; Fowler NÃO é o autor do artigo).
  Fonte: https://martinfowler.com/articles/on-pair-programming.html

## 4. Onde as fontes divergem ou diferem

- Nível de severidade: Sundell fala em "estranho ou crash" com índice; WWDC21 mostra apenas efeito de animação/identidade deslocada. Não são contraditórias, mas descrevem sintomas diferentes.
- `id: \.self`: Hacking with Swift o apresenta como válido quando os valores são únicos (strings, inteiros); Nil Coalescing o desaconselha em modelos editáveis; Sundell o mostra como o que torna o índice a identidade. Depende do que é o valor (conteúdo vs. índice).
- Data/versão: a sessão WWDC21 menciona aviso "neste ano" para faixa não constante; o comportamento atual de avisos/erros em versões recentes do SwiftUI NÃO foi verificado.

## 5. O que NÃO dá para afirmar

- Que o sintoma "o check aparece em OUTRA linha ao remover" tenha uma fonte que o descreva literalmente. Nenhuma fonte lida mostra esse caso exato; é uma dedução coerente do item 5 (estado ligado à identidade) com índice como identidade. Apresentar como "hipótese consistente com a documentação", não como fato citado.
- Que isso seja a causa universal. As fontes lidas não enumeram outras causas do mesmo sintoma (estado no lugar errado, modelo mutável compartilhado etc.); qualquer lista disso seria conhecimento meu, sem fonte aqui. Sugestão para o vídeo: dizer "uma causa possível, comum" sem listar as outras, ou listar marcando como não verificado.
- Que o estado "concluído" esteja em @State da linha; se o check estivesse no modelo (array de structs), a troca de linha seguiria outro caminho. Não coberto pelas fontes.
- Qualquer número, estatística de frequência do bug ou versão de iOS em que o comportamento muda.
- Que `ForEach(items.indices, id: \.self)` sempre falha: com array imutável ou só anexando ao fim pode funcionar (Sundell: "pode funcionar").
- O texto exato da página Apple de Identifiable (não lida).
- Que pair programming resolve ou acelera a depuração (o artigo descreve papéis e práticas, não mede resultado; não li estudo acadêmico).

## 6. Fontes (resumo)
1. Apple, ForEach: https://developer.apple.com/documentation/swiftui/foreach
2. Apple WWDC21, Demystify SwiftUI: https://developer.apple.com/videos/play/wwdc2021/10022/
3. Swift by Sundell: https://swiftbysundell.com/articles/bindable-swiftui-list-elements
4. Hacking with Swift: https://www.hackingwithswift.com/books/ios-swiftui/why-does-self-work-for-foreach
5. Nil Coalescing: https://books.nilcoalescing.com/the-swiftui-way/building-a-performant-and-stable-interface/maximizing-the-performance-of-dynamic-lists/
6. Böckeler e Siessegger, martinfowler.com: https://martinfowler.com/articles/on-pair-programming.html
