# Pendências do setor de Clipes

Dono: **Pelé**. Quem registra aqui: quem criar a pendência. Aviso ao Guilherme: só pelo **Ronaldo**, via linha `PARA RONALDO` na seção "Recados".

## Abertas

### 1. Melhorar a transcrição (decidido em 2026-11-10, fazer em 2026-11-11)
A transcrição é local (Whisper `small`, CPU, sem token) e erra em nomes, gírias, fala rápida ou cruzada e idioma coloquial. Erro na transcrição aparece **escrito na legenda do Short** e pode enganar a seleção. A fazer:
- Ligar por padrão o **refino** (`transcricao.refino`, modelo `medium`) só nos cortes escolhidos, nos projetos novos. Custo: tempo e cerca de 5 GB de RAM livre; sem token.
- **Pré-triagem antes de baixar e transcrever**, com dados públicos do YouTube (título, duração, views, curtidas, comentários, legenda automática), para o **Rivaldo** dar uma nota prévia e o fluxo nem baixar fonte fraca. Pergunta já respondida pelo Guilherme: deve PARAR e perguntar quando a nota for baixa (a confirmar).
- Pensar em modelo menor (`tiny`/`base`) só para triagem.

### 2. Ranking por momento no Rivaldo
Hoje `triagem.json` traz `momentos_promissores` **sem nota por momento e sem ordem definida** (só `ini`, `fim`, `por_que`, `serie`). Fazer: nota de 0 a 100 por momento (régua do **Totti**), lista ordenada da maior para a menor, validação exigindo isso, e o **Kaká** recebendo primeiro os de maior nota. Ficou combinado em 2026-11-10; aguarda o Guilherme mandar.

### 3. Pequenos ajustes conhecidos
- `perguntas_reais` em `triagem_dados.json` conta só falas que **terminam** em "?" e sai 0 em vídeo de perguntas e respostas (a pergunta vem emendada na resposta). Contar por "?" dentro do segmento.
- Regressão completa (`testar_fluxo`, `testar_perfis`, `testar_editorial`, `testar_avaliar`) **não foi concluída** depois que a etapa `triagem` entrou no fluxo padrão (o Guilherme pediu para parar os testes por causa do gasto). Rodar uma vez, quando ele autorizar.
- Cortes de série: início da Parte 1 pode trazer fala de outro assunto (não apara o começo).

## Recados
PARA RONALDO | clipes-transcricao-2026-11-11 | 2026-11-11 09:00 | nunca | Clipes: hoje é dia de melhorar a transcrição (refino nos cortes e pré-triagem do Rivaldo). Detalhes em clipes/pendencias.md.
