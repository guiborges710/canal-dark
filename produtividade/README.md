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

## Regras

- Nada de senha, token, chave, código-fonte ou dado de cliente nestes arquivos.
- Nada confidencial da empresa nos posts de LinkedIn.
- Nenhum post é publicado e nenhuma hora é lançada sem o Guilherme.
- Não inventar prazo, projeto, hora ou experiência. Falta dado: perguntar.
