# Ângulo: o check que pulou de linha (SwiftUI)

Nota: tema fora do nicho de gerações, pedido direto do Guilherme. A tese de gerações não é usada. Mantém-se a assinatura de método: separar o que as fontes dizem da nossa leitura, mostrar contraexemplo e fechar com pergunta.

## Tese
Identidade deve representar o ITEM, não a posição dele. [INTERPRETAÇÃO apoiada nas notas 1.3, 1.5, 1.6, 1.8]

## Pergunta-gancho
Por que o check foi parar em outra linha depois de remover um item?

## Estrutura (gancho, insight, contraexemplo, pergunta)
1. Gancho: o check pulando de linha.
2. Insight: dupla piloto/navegador levanta a hipótese: a lista usa índice como id (`ForEach(items.indices, id: \.self)` ou `id: \.offset`), então o estado fica ligado à posição. Teste: id único e estável, criado com o item.
3. Contraexemplo/ressalva: é UMA causa possível; estado no lugar errado ou modelo são só possibilidades, sem fonte nas notas. Índice pode funcionar se o array só cresce no fim (Sundell).
4. Pergunta de volta: como vocês investigam problemas parecidos?

## Comentário próprio (mais de 1/3 do texto)
- A hipótese de que o estado "pertence ao lugar" é nossa dedução (notas, seção 5, primeiro item): consistente com a documentação, não citada literalmente.
- A moldura piloto/navegador é só dramatização de quem testa e quem levanta a hipótese; não afirmamos que pair programming acelera depuração.
- A ressalva honesta e o fecho aberto.

## Três ideias próprias
1. Perguntar "o que muda de lugar quando o array muda?" antes de mexer no código.
2. Tratar o diagnóstico como hipótese testável, não veredito.
3. Regra mental: o id acompanha o item, nunca o lugar.

## Limites (de notas.md, seção 5)
Sem número, sem versão de iOS, sem frequência do bug. Sem afirmar que é a causa universal. Sem alegar que o check está em @State (se estivesse no modelo, outro caminho). UUID: aplicação do princípio, não texto literal das fontes.
