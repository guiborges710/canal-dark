# Setor de Produtividade Profissional

Função: **ajudar o Guilherme a se organizar no trabalho como desenvolvedor iOS**. Tarefas, horas, acessos e presença no LinkedIn. O setor **não escreve código** (o código é feito na IA da empresa) e **não executa nada fora daqui**: prepara, lembra e organiza; o Guilherme aprova e faz.

Responsável: **Luiz Henrique** (`luiz-henrique-ecossistema`).

## Equipe

| Craque | id técnico | Escreve em |
|---|---|---|
| **Ronaldo** | `ronaldo-assistente` | `agenda.json`, `agenda.md` e `lembretes.json` |
| **Guardiola** | `guardiola-po-agilista` | `kanban.md` |
| **Pedri** | `pedri-gestor-tarefas` | `tarefas.md` |
| **Rodri** | `rodri-apontamento-horas` | `horas.md` |
| **Kroos** | `kroos-acessos-seguranca` | `acessos.md` |
| **Lamine Yamal** | `lamine-yamal-linkedin` | `linkedin/rascunhos.md` |
| **Bellingham** | `bellingham-dicas-ios` | `dicas_ios/dicas.md` (dicas conceituais de iOS; uso raro; nunca recebe código, projeto ou dado do trabalho) |

## Como se falam

Pela troca de arquivos, como no setor de inteligência. **Rodri** lê `tarefas.md` do **Pedri** para saber o projeto de cada hora. **Pedri** abre uma tarefa quando **Kroos** avisa de uma troca de senha. **Lamine Yamal** lê as tarefas concluídas do **Pedri** para achar assunto de post. Cada um só escreve no próprio arquivo; recado para outro vai no fim do arquivo próprio, em "Recados".

## Avisos no celular (Telegram)

- **O único que fala com o Guilherme no Telegram é o Ronaldo.** Os outros agentes deixam pedidos na seção "Recados" do próprio arquivo, no formato `PARA RONALDO | <id> | <quando> | <repete> | <texto>`. O **Ronaldo** lê os pedidos, transforma em lembrete e é o único que escreve em `lembretes.json`. Campos: `id`, `agente`, `texto`, `quando` (`HH:MM` se recorrente, `AAAA-MM-DD HH:MM` se único), `repete` (`dias_uteis`, `diario` ou `nunca`) e `grupo` (opcional).
- `avisar.py` roda a cada minuto pelo Agendador de Tarefas do Windows, manda o que venceu e lê a resposta "feito" no chat para silenciar o resto do dia do grupo. Não usa o Claude, não gasta token.
- **Conversa pelo Telegram (texto e áudio):** `ronaldo_telegram.py` fica ouvindo o bot (tarefa `ContextoExplica-Ronaldo`, reiniciada a cada 5 min se cair). Só atende o chat do Guilherme. Áudio é transcrito localmente com faster-whisper (modelo `small`; o primeiro uso baixa o modelo). Cada mensagem chama o Claude Code em modo headless com a persona do **Ronaldo**, modelo `haiku`, poucas ferramentas e edição só dentro de `produtividade/`; custo medido em `.ronaldo_custo.jsonl` (cerca de US$ 0,01 a 0,02 por mensagem, no uso do plano). Se um JSON ficar inválido depois da resposta, o backup é restaurado. Só este programa lê o `getUpdates`; o `avisar.py` só envia.
- **Outros agentes pelo Telegram:** começando a mensagem pelo nome ("Pedri, ...", "/casemiro ...", "Luiz Henrique, ...") o `ronaldo_telegram.py` chama aquele agente em modo headless, com permissão de edição só nas pastas dele. Disponíveis: **Pedri** (haiku), **Rodri** (haiku), **Kroos** (haiku), **Lamine Yamal** (sonnet), **Casemiro** (sonnet), **Guardiola** (sonnet), **Luiz Henrique** (sonnet). Ficam de fora o **De Bruyne** e a produção do canal (longa e cara). Custo por mensagem em `.ronaldo_custo.jsonl`.
- **Google Agenda:** `google_agenda.py` (tarefa `ContextoExplica-GoogleAgenda`, a cada 5 min) mantém os compromissos de `agenda.json` e os eventos do Google iguais, e o Guilherme sempre ganha. O aviso de 1 hora antes de cada compromisso com hora sai sozinho do `avisar.py`.
- **Resumo diário 08:30:** emojis e marcadores (⏳ pendente, ✅ feito) montados pelo `avisar.py` a partir de `agenda.json`.
- Credenciais só no `.env`: `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`. O estado local fica em `.estado_avisos.json` (ignorado pelo git).
- O computador precisa ficar ligado e sem suspender.

## Painel do Ronaldo (navegador, desde 2026-11-04)

Central de controle local, no estilo da referência "AETHER" do Guilherme. Abrir: `produtividade\painel.bat` (ou `python produtividade/painel.py`) e acessar http://127.0.0.1:8766/. Arquivos: `painel.py` (servidor, só biblioteca padrão), `painel.html` (a tela).

- **Mostra** o que já existe, lido dos arquivos a cada 6 s: agenda e tarefas (`agenda.json`), próximos avisos (`lembretes.json`), finanças (`financas/movimentos.csv`), sprint (`programacao/quadro.md`), consumo (`.ronaldo_custo.jsonl`) e estado das conexões (Telegram, Google Agenda, Trello). **Clima** (desde 2026-11-04): previsão do Open-Meteo (grátis, sem chave), atualizada a cada 10 min em segundo plano, com temperatura, sensação, umidade, vento, chuva de hoje e amanhã, próximas 12 h e nascer/pôr do sol. Só as coordenadas da cidade saem do computador. Cidade padrão: **Jundiaí** (suposição, pela conta de água); para trocar, crie `produtividade/.ronaldo_painel_local.json` com `{"nome": "Cidade", "lat": -00.0000, "lon": -00.0000}` (ignorado pelo git). Sem internet, o cartão mostra o último dado como `DESATUALIZADO` ou `OFFLINE`. O **Ronaldo** no Telegram não enxerga o clima (não tem internet): quem lê é o painel. Casa/IoT, segurança, Slack e e-mail aparecem como **NÃO CONECTADO**: nunca se inventa status.
- **Controla**: caixa de comando com o mesmo roteamento do Telegram (`@Pedri ...`, "Casemiro, ..."), mesmos agentes, permissões, orçamento por mensagem e histórico de conversa (cada ordem gasta uma chamada do Claude; **De Bruyne** continua só pelo Claude Remote). Sem Claude e sem custo: marcar tarefa/compromisso como feito, criar tarefa, compromisso ou lembrete (gravados direto em `agenda.json` e `lembretes.json`, com `origem` "Painel") e o "Resumo do dia" (mesmo texto das 08:30).
- **Segurança**: só ouve em `127.0.0.1`; recusa `Host` e `Origin` de fora e POST sem o cabeçalho `X-Painel`; não envia nada ao Telegram nem a terceiros; não guarda senha, token ou chave. O histórico das ordens fica em `.ronaldo_painel_ordens.jsonl` (ignorado pelo git).
- **Limites**: precisa do computador ligado; uma ordem por vez (a segunda recebe aviso); sem voz por enquanto (o áudio continua pelo Telegram); não abre pelo celular (para isso, só pelo Telegram ou pelo Claude Remote).

## Kanban geral (trabalho + projeto do canal)

O quadro "Kanban Trabalho" (espelhado em `kanban.md`) é um só: trabalho do Guilherme **e** o setor de programação. `kanban_programacao.py` (chamado pelo `trello_sync.py` antes de sincronizar, ou rodável à parte com `--simular`) lê `programacao/backlog.md` e `programacao/quadro.md` e cria/atualiza os cartões `[PROG-NNN] título` (candidatos ainda sem id: `[PROG-C-01]`). O id entre colchetes identifica o cartão; o título não muda depois de criado. Quem move esses cartões é o **Xavi** (e o **Zico**), pelos arquivos de `programacao/`; o **Guardiola** não os move nem os repriorizam, e o Guilherme continua ganhando no Trello. Mapa de colunas (o estado fino fica no texto do cartão, `estado: Em teste`):

| Quadro do Xavi | Kanban geral |
|---|---|
| Backlog da sprint, Em refinamento técnico | Backlog |
| Fazendo, Em teste, Pronto para aceite | Fazendo |
| Feito | Feito |
| Bloqueado | Bloqueado |

## Regras

- Nada de senha, token, chave, código-fonte ou dado de cliente nestes arquivos.
- Nada confidencial da empresa nos posts de LinkedIn.
- Nenhum post é publicado e nenhuma hora é lançada sem o Guilherme.
- Não inventar prazo, projeto, hora ou experiência. Falta dado: perguntar.
