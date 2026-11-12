# Direção viral: check que pulou de linha (SwiftUI)

Formato: short de 30 a 45 s, estilo sketch (caderno pautado, ícones simples), sem legenda na base, um desenho por cena. 7 cenas, cerca de 100 palavras faladas.

## Gancho e retenção
- Frame 0: lista de 3 linhas com caixas de seleção; o check está na linha 2, uma linha é riscada e o check pula para a linha seguinte. Movimento já no primeiro frame.
- Virada na cena 6 ("Mas isso é só uma causa possível"): reabre a atenção e dá honestidade.
- Fecho em pergunta aberta aos devs iOS, sem "inscreva-se" e sem resposta pronta.

## Narração

**Tom:** colega de time explicando, calmo, curioso, sem arrogância. Hipótese dita como hipótese.
**Ritmo:** cerca de 2,8 palavras por segundo. Pausa curta depois de "Hipótese" e depois da pergunta final.
**Ênfases:** marcadas com *palavra*.
**Código:** falar "ForEach", "id ponto self", "Identifiable", "let id igual a UUID" como no roteiro.

**Falas por cena (texto exato do campo `fala`):**

1. gancho | Fala: "Removi um item da lista, e o *check* pulou para outra linha." | Visual: lista de 3 linhas com caixa de seleção; o check salta de uma linha para a de baixo após um item ser riscado. | Tela: "O check pulou"

2. sketch | Fala: "Quem *navega* pergunta: como a lista identifica cada linha?" | Visual: dois bonecos palito diante de um quadro; o da esquerda, com balão de interrogação, aponta para o quadro (navegador); o outro, no notebook (piloto). | Tela: "Como identifica?"

3. sketch | Fala: "Quem *digita* responde: ForEach sobre os índices, com id ponto self." | Visual: notebook com uma linha de código escrita à mão: ForEach(items.indices, id: \.self). | Tela: "id: \.self"

4. sketch | Fala: "Então a identidade é a *posição*. Hipótese: o estado da linha pertence ao lugar, não ao item." | Visual: três caixas numeradas 0, 1, 2 com o check preso na caixa 1; um item sai e os números continuam, check no mesmo número. | Tela: "Hipótese: posição"

5. sketch | Fala: "Quem digita testa um id *único*, criado junto com o item, que nunca muda. Pode ser Identifiable, com let id igual a UUID, ou o id do banco." | Visual: cada item com uma etiqueta presa a ele; ao remover um item, a etiqueta e o check seguem o item certo. | Tela: "id único e estável"

6. sketch | Fala: "Identidade deve representar o *item*, não a posição dele. Mas isso é só uma causa *possível*, para investigar. O estado pode estar no lugar errado, ou o problema pode estar no modelo." | Visual: etiqueta ligada ao item; depois uma lupa sobre três pistas com interrogação (posição, estado, modelo). | Tela: "Uma causa possível"

7. fechamento | Fala: "Como vocês investigam problemas parecidos?" | Visual: boneco palito com balão de interrogação, folha de caderno vazia abaixo. | Tela: "Como você investiga?"

Para a Olise: sem fonte, sem logo, sem nome de site na tela. Rótulos com até 26 caracteres. Mostrar o trecho de código só como rabisco curto. Pair programming é só enquadramento; nada na tela promete rapidez.
