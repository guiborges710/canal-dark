# Auditoria de TEXTO (Vini) - swiftui-identidade-lista

**APROVADO** (nenhuma infração; 3 riscos/recomendações abaixo)

## Verificado
- Falas do cenas.json (8 cenas, concatenadas) batem palavra por palavra com roteiro.txt (enxugado). direcao_viral.md "## Narração" ignorada, como instruído.
- Ressalva "uma causa possível": presente no corpo (cena 6, "Mas é só uma causa possível. Pode haver outras, que eu não verifiquei.") e na descrição. Rótulos da cena 6 reforçam.
- Base nas notas: índice como identidade (notas 1.5, 1.6), id estável/UUID/id de banco (1.3, 1.4, 1.8, seção 2). "Hipótese nossa, coerente com a documentação" e "Minha leitura" rotulam corretamente a dedução (notas, seção 5). Sem número, versão de iOS, frequência nem alegação sobre pair programming. Nada sem base.
- Título e descrição: honestos, sem isca; descrição hedgeia ("hipótese", "causa possível, não a explicação de todo caso"), cita 5 fontes das notas. thumbnail_texto "O check foi para outra linha?" coerente com o conteúdo.
- Aviso de animação por computador e voz sintética (IA, voz do autor): presente na descrição.
- Rótulos: todos <= 26 caracteres (maior: "struct Item: Identifiable", 25).
- Duração: 106 palavras, ~35-42 s de fala; soma das duracao = 32,5 s (a duração real virá do áudio). Dentro de 30-60 s.
- Comentário próprio: cenas 3, 5, 6 e 7 (hipótese, leitura, ressalva, pergunta) somam bem mais de 1/3. Fecho é pergunta sem resposta pronta.
- Tema fora do nicho: pedido direto do dono; não é infração. Sem conteúdo sensível, sem terceiros/IA de imagem no texto.

## Riscos / recomendações (não bloqueiam)
1. RISCO (baixo): cena_3 tem som em t=7.5 e cena_4 em t=5.3, acima das duracao declaradas (6 e 5). Como o sketch usa a duração da fala, provavelmente é coberto, mas **Olise** deve conferir que os sons caem dentro da cena após o áudio; senão ficam sem efeito.
2. RISCO (baixo): 106 palavras em 32,5 s nominais seria ritmo alto; se a narração real passar de ~45 s, não é problema de política, só de ritmo. Conferir na auditoria final.
3. RECOMENDAÇÃO: "o estado fica preso a ela" / "o check fica no lugar" supõe que o check está em estado da linha (notas, seção 5 diz não coberto). Já está enquadrado como "Hipótese nossa"; manter esse rótulo visível (cena 3 tem). Não remover.

## Incertezas
- Não abri as fontes de novo; confiei nas notas do **Courtois**/**Modric** (página Identifiable da Apple não lida, informado nas notas).
- Imagem, som e voz reais só serão avaliados na auditoria FINAL.
