# Auditoria de TEXTO: fim-dos-terceiros-lugares

**APROVADO** (modo texto, 2026-11-01). Nenhuma infração encontrada. Há 2 riscos e 3 recomendações, de texto barato de corrigir antes do render.

Escopo: notas.md, angulo.md, roteiro.txt, metadados.json, cenas.json (fala e rótulos). Não verifiquei imagem, som, animação nem miniatura (modo FINAL). Não rodei `run.py check`, que depende do vídeo renderizado.

## Infrações (bloqueiam)
Nenhuma.

## Riscos (atenção, corrigir se possível antes do render)
1. **Média: "No Brasil não existe essa medida"** (roteiro, cena_3, descrição "não há essa medida"). Nas notas, a ausência de pesquisa nacional de uso do tempo no Brasil vem de resumo de busca do Ipea, não verificado. A afirmação é absoluta. Sugestão: "Para o Brasil, não encontramos essa medida." Rótulo "sem essa medida" pode ficar.
2. **Baixa/média: o gancho promete "sumiu", mas o vídeo não traz dado de lugares.** A fala "Seu terceiro lugar sumiu, e você nem percebeu" é afirmação. O corpo mostra queda do tempo com amigos (EUA) e consumo (Brasil), não o desaparecimento de lugares. As notas (divergência 4) dizem que "terceiros lugares sumindo" não é consenso e que bares e cafés podem ter crescido. O fecho "hipótese, não prova" ajuda, mas o gancho não é hipótese. Sugestão: "Seu terceiro lugar sumiu?" (igual à miniatura) ou "E se o seu terceiro lugar tiver sumido, sem você perceber?". Isso mantém a regra (c) do canal, de entregar o que o gancho promete.

## Recomendações
- Título: "O que os dados de EUA e Brasil mostram" sugere dado equivalente nos dois países. No Brasil é só consumo. Alternativa: "Seu terceiro lugar sumiu? O que os dados mostram (e o que não mostram)".
- "sociólogo Ray Oldenburg" e "livraria": as notas não trazem "sociólogo" no PPS lido. "Livraria" vem só do catálogo do livro (busca). O risco é baixo, pois é fato conhecido. Se quiser fidelidade total, use "o pesquisador Ray Oldenburg" no rótulo e na fala, ou cite só café e bar (PPS lido).
- Medida de análise própria: a análise original estrita (cenas 5, 7 e 8, cerca de 27% das palavras) fica perto de 1/3. Somando gancho e pergunta passa de 40%. Se o checker apontar, acrescente uma frase de interpretação, por exemplo sobre quem ganha com o rótulo "geração isolada" (já está em angulo.md).

## O que verifiquei
- **Fatos vs notas (OK):** quase 7 h até 2013 e menos de 3 h em 2021 (Ward/The Ringer, fonte 3, única fonte para tempo com amigos); saídas -7,1% e gasto por saída +28,3%, 1º tri 2026 contra 1º tri 2025 (fonte 7, lida), tratados como consumo e não convívio; Ward atribui a queda a telas e tempo sozinho (fonte 3); queda forte em jovens (fonte 2). "Não parece ser só deles" está hedged e marcado como interpretação nas notas.
- **Honestidade dos dados:** a fala informa que os dados de tempo são dos EUA. A fala não diz "ficou mais caro" (as notas proíbem, sem série de preços). Não aparecem "110 mil bares", Gallup, Survey Center 3%/15% (já usados em outro vídeo) nem os números do Hedgeye/WaPo.
- **Fontes:** 4 listadas na descrição (PPS, PubMed, The Ringer, Meio & Mensagem). Atende 3+. O estudo de Kannan e Veazie foi lido só via resumo do PubMed e a descrição o cita sem número, o que é aceitável.
- **Conteúdo reutilizado/inautêntico:** nada copiado. Ponto de vista próprio explícito ("Nossa leitura", hipótese, contraexemplo tratado como explicação concorrente). Estrutura gancho, insight, contraexemplo, pergunta cumprida.
- **Linhas de tela <= 26 caracteres:** todos os rótulos passam. Os mais longos são "1º tri 2026 x 1º tri 2025" (25), "sociólogo Ray Oldenburg" (23), "horas/semana com amigos" (23) e "não parece ser só deles" (23). A miniatura tem 25 caracteres.
- **Rótulos fiéis às notas:** "EUA (pesquisa ATUS)", "-7,1%", "+28,3%", "tempo sozinho cresceu" conferem. Os rótulos de cena_6 ("continuar assistindo?", "próximo em 5 s") imitam interface de streaming genérica, sem logo de terceiros: OK, desde que o desenho não use marca real.
- **Aviso de animação e IA:** a descrição traz "animação feita por computador, sem gravação de pessoas" e "narração é gerada por IA". OK.
- **Duração prevista:** a soma das cenas é cerca de 45 s, dentro de 30-60 s. Como o vídeo segue o áudio, confirmar no render.
- **Sensibilidade:** tema não sensível. Não há pessoas reais retratadas, vítimas nem saúde ou política. Sem isca de assunto alheio.
- **Tags/descrição:** sem spam, sem promessa de ganho, com CTA simples.

## Incertezas que restam
- A voz é clone da amostra do Guilherme. Não confirmei na página oficial do YouTube se voz clonada realista exige o campo "conteúdo alterado/sintético" no Studio. Por prudência, marcar o campo ao publicar além do aviso na descrição. A regra atual deve ser conferida pela Memphis.
- Dados de tempo com amigos são dos EUA e de uma única fonte (definição de "amigo" própria da ATUS). O vídeo não prova que custo seja causa; as notas dizem isso e o roteiro respeita.
- O dado brasileiro vem de fonte comercial, sem margem de erro, e o aumento do gasto por saída pode refletir inflação ou mix.
- Nada aqui garante monetização nem ausência de risco. A decisão é do YouTube.

Próximo passo: aplicar os riscos 1 e 2 em roteiro.txt, cenas.json (campo "fala") e metadados.json, e seguir para o render. Se os textos mudarem além disso, reauditar.

## Ajuste pós-auditoria
Cena 3 e roteiro: 'No Brasil não existe essa medida' trocado por 'Para o Brasil, não encontramos essa medida' (recomendação do Vini, risco 1).

## Ajuste pós-render
Para caber em 60 s (render deu 61,5 s) cortei 'E tem o contraexemplo.', 'das duas coisas' e 'contra um ano antes' (comparação 1º tri 2026 x 2025 segue no rótulo da tela). Sem mudança de fatos.
