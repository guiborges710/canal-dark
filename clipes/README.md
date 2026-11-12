# Setor de Clipes (Instagram e TikTok)

Setor **separado** do canal dark e do Corte (`estudio/`). Transforma vídeos de terceiros (autorização do criador não é requisito, ver Regras) em cortes verticais 9:16 (1080x1920, 30 fps) com gancho próprio, legenda palavra a palavra, fundo borrado e crédito ao criador. Tudo local e grátis (ffmpeg, faster-whisper, yt-dlp).

Equipe (chefe **Pelé**): **Salah** (fontes e autorização), **Kaká** (momentos), **Zidane** (comentário próprio e corte), **Buffon** (auditoria), **Lewandowski** (embalagem por plataforma). Agentes em `.claude/agents/`; registro em `ecossistema/setores.json`.

**De onde vêm os vídeos:** o setor `pesquisa_videos/` (agente **Pirlo**) lista os vídeos longos mais vistos do dia, da semana e do mês; o **Salah** registra a fonte (autorização só se existir; não é mais requisito).

**Layout do corte:** `cortar <slug> --layout zoom` põe a câmera do streamer em cima e o jogo ampliado embaixo (`--cam x:y:w:h` define a posição da câmera, `--cam nenhuma` se não houver). `refinar <slug>` retranscreve só os trechos escolhidos com o modelo `small`.

## Perfis de conteúdo (V2)

O processamento é o mesmo para qualquer nicho; o que muda vem do **perfil** (`clipes/perfis/<id>.json`): público, idioma da fala, temas, palavras-chave, entidades e termos técnicos (contam na seleção e entram como vocabulário no Whisper), assuntos desejados e a excluir, pesos dos sinais de seleção, critérios editoriais (para o Kaká), duração mínima e máxima, quantidade, contexto antes/depois, enquadramento padrão, estilo editorial, tema de pesquisa, hashtags e instruções por agente.

- **Dois perfis**: `geral` (método único para qualquer vídeo falado: fofoca, vlog, podcast, entrevista, react, aula, gameplay comentado; padrão de projetos novos) e `gta6` (apartado; a versão 1 são as regras fixas da V1). Dá para criar outros pelo painel, mas não é preciso: o Geral não depende de tema.
- **Criar/editar/duplicar/arquivar**: painel, botão **Perfis** ao lado da escolha do perfil. Salvar com mudanças cria nova versão; a anterior vai para `perfis/_historico/<id>.vN.json`.
- **Projeto congela o perfil**: `clipes_out/<slug>/perfil.json` guarda a versão usada; mudar o perfil depois não altera trabalhos antigos. Projeto sem esse arquivo (anterior à V2) usa o GTA 6 v1 e continua igual.
- **Sinais de seleção** (só os que o código mede): pico de áudio, termos do perfil ditos no trecho, abertura com pergunta/exclamação, densidade de fala e termos a excluir. **Não há detecção visual** (lance, jogada, rosto): isso fica para o julgamento do Kaká sobre a transcrição. Cada sugestão em `momentos.json` traz `sinais`, `criterios` e `motivo`; a nota é só ordenação, não previsão de alcance.

```
.venv\Scripts\python -m clipes perfis                       # lista (--todos inclui arquivados)
.venv\Scripts\python -m clipes perfis mostrar geral
.venv\Scripts\python -m clipes perfis duplicar gta6 --nome "GTA 6 em inglês"
.venv\Scripts\python -m clipes tudo <URL> --autor "Criador" --autorizacao livre             # perfil Geral
.venv\Scripts\python -m clipes tudo <URL> --autor "Criador" --autorizacao livre --perfil gta6
```

Testes: `.venv\Scripts\python -m clipes.testes.testar_perfis` (inclui a regressão do GTA 6 sobre o vídeo real `flow-games-fgn`) e `node clipes/testes/e2e_perfis.mjs` (Chrome real; perfis em pasta temporária).

## Seleção editorial (V3, `clipes/editorial.py`)

Projetos com perfil (Geral, GTA 6 e os do painel) usam a seleção V3; projeto sem `perfil.json` segue a V1 (regressão). Em vez de janelas cegas de segmentos, o código monta **unidades de pensamento** (pontuação + pausa), recupera a **premissa** quando o início depende de contexto ("isso", "ele", conector solto), exige **fim íntegro** (frase fechada, sem pergunta sem resposta, fala seguinte não colada) e exige **pausa real** para abrir ou fechar um corte (fala corrida no meio de um relato não é fronteira). Descarta transcrição ruidosa, conversa vazia e redundância; limites em tempo de **palavra**. Integridade vem antes da nota; corte íntegro maior que o máximo do perfil é descartado, não encurtado; se faltar momento bom, entrega menos que a cota.

Registro em `momentos.json`: `segmentos_origem`, `montagem` (ordem e trechos), `avaliacao` por critério, `justificativa`, `contexto_necessario`, `conclusao`, `problemas`/`correcoes`, `gancho_trecho_sugerido` (chamada inicial; só sugere). `selecao.json` conta os descartes por motivo. Ajuste manual e ajuste do Kaká são revalidados pelo mesmo código. `cortar` junta N trechos em ordem (chamada + corte) e **verifica o arquivo**: resolução, duração igual aos trechos aprovados, áudio com som e legenda (`verificacao` em `clipes/NN.json`; reprovado = erro). A transcrição em blocos de 10 min agora usa sobreposição de 30 s e cada frase fica com um só bloco. As notas são heurísticas de comparação, não previsão de alcance. Teste: `python -m clipes.testes.testar_editorial [--render]` (casos sintéticos rotulados; `--render` usa o vídeo real).

## Vídeo muito longo: legenda do YouTube em vez de Whisper (só desta vez, ou quando precisar)

O Whisper `small` roda a cerca de 0,57× o tempo do vídeo nesta máquina (medido: 25,5 min para 44 min), então 2h20 levam ~80 min. Para triagem rápida: `python -m clipes legendas <slug>` baixa a legenda automática do YouTube (com tempo por palavra), converte para `transcricao.json` em segundos e marca a etapa como concluída. Ligue `transcricao.refino` (Configurar etapas) para o Whisper retranscrever só os cortes escolhidos antes do corte (é o que vai na legenda do vídeo). Limites: o vídeo precisa ter legenda automática; a qualidade é a do YouTube.

## Triagem da fonte (Rivaldo): vale clipar esse vídeo?

Primeiro agente do fluxo, logo depois da transcrição e antes do **Kaká** (etapa `triagem`, ligada por padrão em projetos novos). O código mede a fonte (`python -m clipes triagem-dados <slug>` → `triagem_dados.json`: duração, ritmo, % de fala, falas picadas, trechos ruidosos, perguntas, quantos momentos íntegros e a densidade por 10 min, e os 12 melhores candidatos com tempo e texto). O **Rivaldo** lê isso e a transcrição e grava `triagem.json` (nota 0-100, veredito, recomendação `seguir|seguir_com_ressalvas|nao_vale`, formato, motivos, riscos, sugestões e até 8 `momentos_promissores` com tempo real) e `triagem.md`. A nota usa os critérios: densidade de momentos clipáveis 30%, autossuficiência e clareza 20%, tema quente e aderência ao perfil 20%, emoção/humor/compartilhamento 15%, risco e qualidade da fonte 10%, potencial de série 5%. É estimativa editorial, não previsão de alcance.

Só a **melhor parte dos destaques** segue (porcentagem em "Configurar etapas": 20, 30 padrão ou 50; 30% de 10 destaques = 3, mínimo 1). Nota abaixo do mínimo do projeto (padrão 45; opções 0, 30, 45 e 60 em "Configurar etapas"; 0 = nunca parar): o fluxo **para** em "espera você" e o painel mostra **Continuar mesmo assim**. Quem decide é o Guilherme; o código e o agente nunca descartam a fonte sozinhos. Continuar não reavalia a fonte. Refazer: "Refazer daqui" na etapa. Teste: `python -m clipes.testes.testar_triagem` e a seção "Triagem" de `testar_fluxo`.

## Séries em partes (assunto que não cabe em um vertical)

Se um assunto só fecha depois do máximo de duração do perfil, o corte não é mutilado: vira **Parte 1, Parte 2...** (até `PARTES_MAX` = 4 em `editorial.py`). O fim do assunto é um **fecho forte** (frase íntegra e pausa longa, ou queda de coesão do vocabulário raro entre as falas); o código divide no menor número de partes que cabem em `[min, max]`, cortando só em frase fechada (nunca numa pergunta sem a resposta nem em palavra de ligação), com durações equilibradas. Sem ponto de corte íntegro, ou assunto acima do máximo de partes, não divide (entrega menos). Cada parte é um corte normal em `momentos.json` com `serie` (`id`, `parte`, `de`) e `cta`. A série entra e sai da curadoria junta (parte órfã quebra o contexto) e a cota do perfil conta assuntos, não partes. No vídeo: "PARTE X/N" o tempo todo e CTA nos últimos 3,5 s ("tem mais, siga o perfil" / "fim, veja as outras partes"), na língua do perfil (pt, en, es); o **Zidane** pode reescrever `cta`. O `check` reprova parte sem CTA; a embalagem prefixa "Parte X/N".

## Avaliação de potencial (Totti)

O Totti roda no fluxo normal (etapa `potencial`). Plano B: botão **Avaliar potencial** em cada corte e **Avaliar os cortes sem nota** (painel), ou `python -m clipes avaliar <slug> [--ids 2 3]`, para quando a nota faltou ou a etapa falhou. Teste: `python -m clipes.testes.testar_avaliar`.

## Painel (central dos agentes + cortes)

```
.venv\Scripts\python -m clipes painel        # http://127.0.0.1:8767/
```

Primeira tela: link do vídeo (inicia o processamento), fluxo dos agentes com status, atividade, tempo e progresso, eventos recentes. Abaixo, os cortes à medida que ficam prontos (score do Totti, ordenar/filtrar) e o editor de ajuste (intervalo na linha do tempo do original, transcrição, prévia do original, legenda/enquadramento/áudio). O estado vem de `clipes_out/<slug>/estado.json`.

- **Ao vivo:** `/api/eventos` (SSE) avisa quando algo muda; sem ele a tela consulta a cada 1,5 s.
- **Ações (POST, só no computador local; no `--rede` o painel é só leitura):** `/api/iniciar` roda `python -m clipes tudo ...` (download, transcrição, momentos, cortes). `/api/ajustar/<slug>/<N>` roda `python -m clipes ajustar ...`, que refaz UM corte (guarda `NN.anterior.mp4` e restaura se falhar; a nota do Totti passa a "desatualizada"). Log em `clipes_out/<slug>/processo.log`.
- **Limite:** Kaká, Zidane, Figo, Totti, Buffon e Lewandowski são subagentes do Claude Code (via Pelé); o painel mostra a vez deles, mas não os dispara.
- **Progresso real:** `estado <slug> <no> trabalhando "msg" --progresso 0.4` (0 a 1). Sem ele a barra é indeterminada. O pipeline informa download e transcrição.
- Modo demonstração só em dev: `http://127.0.0.1:8767/?demo=1` (dados fictícios, faixa de aviso).

Reportar estado (agentes):
```
.venv\Scripts\python -m clipes estado <slug> <no> <status> "mensagem" --agente Zidane
```
Status: `pendente`, `trabalhando`, `concluido`, `espera_voce`, `bloqueado`, `falhou`.
Refazer um corte à mão: `python -m clipes ajustar <slug> --id 2 --ini 705 --fim 730 [--layout zoom] [--sem-legenda] [--sem-audio]`.

## Uso

```
.venv\Scripts\python -m clipes tudo <URL ou arquivo> --autor "Criador" --autorizacao permissao --prova "link do e-mail/DM" --titulo "Título original" --quantos 5
.venv\Scripts\python -m clipes momentos <slug> --quantos 8     # reescolhe os candidatos
.venv\Scripts\python -m clipes cortar <slug> --ids 2 4 --gancho "TEXTO"
.venv\Scripts\python -m clipes check <slug>                    # gate; se passar, gera publicar/
.venv\Scripts\python -m clipes embalar <slug>                  # textos Instagram e TikTok
```

Saída em `clipes_out/<slug>/` (gitignored): `fonte.mp4`, `transcricao.json`, `momentos.json`, `clipes/NN.mp4` + `NN.json`, `publicar/NN_instagram.txt` e `NN_tiktok.txt`, `estado.json`.

Para o corte ter comentário próprio, o **Zidane** acrescenta `"gancho"` e `"fecho"` a cada momento em `momentos.json` antes de `cortar` (ou usa `--gancho`).

## Regras (inegociáveis)

- **Autorização (decisão do Guilherme, 2026-11-10):** a pipeline não depende de autorização do criador. O tipo `livre` (`--autorizacao livre`, sem `--prova`) libera o corte de criador que não será consultado; o risco é assumido pelo Guilherme e fica registrado no estado. Os tipos `proprio`, `parceria`, `permissao` e `licenca` continuam valendo quando houver prova. `teste` é só prova técnica e nunca publica. O `check` segue exigindo crédito e comentário próprio (gancho e fecho), porque isso protege o perfil do filtro de originalidade.
- **Comentário próprio:** o `check` reprova corte sem gancho/fecho nossos. Pesquisa de 2026: o Instagram recomenda o original no lugar de reposts idênticos e não conta marca d'água ou mudança de velocidade como transformação. Confirmar as regras do TikTok nas políticas oficiais.
- **Crédito** ao criador na tela e na descrição; **sem marca d'água** de outro app.
- **Nunca publica:** postagem no Instagram e no TikTok é manual (o nó `aprovacao` fica "espera você").
- Duração: Reels rende melhor entre 15 e 45 s; TikTok até 60 s.
