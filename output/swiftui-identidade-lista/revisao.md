# Revisão de fatos: swiftui-identidade-lista

Veredito: APROVADO após correções. Conferido contra notas.md e angulo.md.

## Problemas e correções
1. "Então a identidade é a posição" estava como fato. As notas (seção 5) dizem que o sintoma exato não tem fonte literal; é dedução. Reescrito: índice vira identidade (nota 1.6), estado ligado à identidade (nota 1.5), e a conclusão marcada como "hipótese nossa, coerente com a documentação".
2. "O estado pode estar no lugar errado, ou o problema pode estar no modelo": outras causas não têm fonte (notas 5). Trocado por "o problema pode estar em outro ponto, que eu não verifiquei", sem listar causas sem apoio.
3. "id... que nunca muda": ajustado para "criado uma vez só" (nota 3: estável e único; id aleatório recalculado é erro).
4. Ressalva reforçada com o contraponto de Sundell: se o array só cresce no fim, índice pode funcionar (nota 1.6, seção 5). A ressalva "causa possível, não universal" permanece.
5. "Identidade deve representar o item" é interpretação: marcada como "Minha leitura".
6. `let id = UUID()` é aplicação do princípio (notas, seção 2), não texto literal de fonte; formulação mantida como sugestão de teste, não como citação.

## Itens verificados sem problema
- Sem números, versões de iOS ou frequência de bug.
- Nenhuma promessa de que pair programming acelera ou resolve depuração (notas 5). Piloto/navegador é só dramatização de quem testa e quem levanta a hipótese.
- Sem trecho copiado das fontes.
- Gancho promete o check pulando e a explicação provável; o vídeo entrega como hipótese, sem prometer mais.

## Leitura na tela
- "id ponto self" e "let id igual a UUID" ficam como fala; as cenas devem mostrar o código escrito.
- Frases curtas; uma ideia por bloco.

## Regra de 1/3 de comentário
Comentário próprio: hipótese do estado preso ao lugar, "minha leitura", ressalva e pergunta final. Cerca de 45% do texto. OK.

## Duração
Cerca de 115 palavras, em torno de 38 a 42 s de fala. Dentro de 30 a 45 s.
