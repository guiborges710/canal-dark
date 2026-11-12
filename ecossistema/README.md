# Ecossistema do Guilherme · Mapa vivo

Mantido por **Luiz Henrique** (`luiz-henrique-ecossistema`). Toda criação, mudança ou remoção de agente ou setor é registrada aqui, com data. É a primeira leitura de quem precisa do contexto geral.

## Visão geral

O ecossistema é o braço direito do Guilherme (desenvolvedor iOS). Hoje tem cinco blocos (42 agentes em `.claude/agents`, conferido em 2026-11-09):

1. **Contexto Explica / canal dark**: a empresa do canal (YouTube, pt-BR, Shorts de análise de comportamento social e gerações). Detalhes em `CLAUDE.md`.
2. **Inteligência**: métricas, concorrência, tecnologia de IA e aprendizado de canais dark.
3. **Produtividade profissional**: organiza o trabalho do Guilherme como dev iOS (tarefas, horas, acessos, LinkedIn) e abriga o **Ronaldo** e o painel. Sem código de app.
4. **Finanças pessoais**: **Casemiro**.
5. **Programação**: evolução do Corte e do pipeline, em sprints.

Mais o agente transversal **Valverde** (engenharia de IA).

## Hierarquia

| Quem | Papel |
|---|---|
| **Luiz Henrique** | Cabeça do ecossistema. Cria agentes e setores, mantém este mapa, responde "dados do ecossistema". |
| **De Bruyne** | CEO do canal. Coordena a produção dos Shorts e o setor de inteligência. |
| **Guilherme** | Dono. Decide, aprova e executa tudo o que é externo (publicar, lançar horas, trocar senha). |

## Setores e equipes

### Canal dark (Contexto Explica)
Squad de produção, coordenada por **De Bruyne**. Fluxo e contrato em `CLAUDE.md`.

| Craque | id técnico |
|---|---|
| **Modric** | modric-pesquisador-tema |
| **Neymar** | neymar-roteirista |
| **Courtois** | courtois-revisor-fatos |
| **Raphinha** | raphinha-curador-componentes (criado em 2026-10-30; vem antes do Olise) |
| **Olise** | olise-diretor-arte |
| **Barcola** | barcola-diretor-horizontal |
| **Mbappé** | mbappe-editor-metadados |
| **Vini** | vini-auditor-conformidade |
| **Seedorf** | sidorf-thumbnail-estrategista |
| **Kane** | kane-narrador |
| **Messi** | messi-estrategista-angulo |
| **Cristiano** | cristiano-otimizador-viral |
| **Haaland** | haaland-pesquisador-nicho |
| **Memphis** | memphis-social-media |
| **Dembelé** | dembele-reels-instagram (Instagram, separado do canal) |
| **De Bruyne** | debruyne-orquestrador |

### Transversal
| Craque | id técnico | Função |
|---|---|---|
| **Valverde** | valverde-engenheiro-ia | Engenheiro de IA (criado em 2026-11-03): revisa fluxo e agentes para cortar consumo de token, com foco em **Vini** e **Courtois**; só diagnostica e propõe, escreve em `ecossistema/engenharia-ia/`. Responde a **Luiz Henrique**. Pronto, aguardando o Guilherme disparar |

### Setor de inteligência
Contrato em `inteligencia/README.md`. Chefe do setor: **De Bruyne**. Equipe: **Hugo Souza**, **Fagner**, **André Carrillo**, **Raniele**, **Yuri Alberto**, **Vitinho**, **Garro** (`garro-scout-tecnologia-ia`, criado em 2026-11-09: ferramentas de IA para produção, custo zero primeiro, pasta `inteligencia/tecnologia/`; alimenta o **Vitinho**), **Busquets** (`busquets-aprendiz-canais-dark`, estuda vídeos enviados pelo Guilherme) e **Xabi Alonso** (`xabi-alonso-curador-referencias`, lista o que estudar), estes dois desde 2026-11-05 e sem agendamento (`inteligencia/aprendiz/README.md`). Setor de ação do canal: ainda não existe.

### Setor de clipes (criado em 2026-11-10)
Contrato em `clipes/README.md`. **Separado do canal dark e do Corte** (não usa `output/`, `run.py` nem `estudio/`). Cortes de vídeos de terceiros, **só com autorização registrada**, em 9:16 para **Instagram e TikTok**; comentário próprio obrigatório (Instagram e TikTok rebaixam repost sem transformação). Chefe: **Pelé**. Painel visual do fluxo ao vivo: `python -m clipes painel` (http://127.0.0.1:8767/). Dados em `clipes_out/` (gitignored). Nada é publicado: o Guilherme posta à mão.

| Craque | id técnico | Função |
|---|---|---|
| **Pelé** | pele-chefe-clipes | Chefe: coordena o fluxo e entrega o pacote |
| **Salah** | salah-scout-fontes | Acha fontes e confirma autorização e prova |
| **Kaká** | kaka-cacador-momentos | Escolhe os trechos que funcionam sozinhos |
| **Zidane** | zidane-editor-cortes | Comentário próprio (gancho e fecho) e corte 9:16 |
| **Buffon** | buffon-auditor-originalidade | Gate: autorização, crédito, comentário próprio, duração |
| **Lewandowski** | lewandowski-embalagem-plataformas | Legenda, descrição e hashtags por plataforma |

### Setor de produtividade profissional (criado em 2026-10-30)
Contrato em `produtividade/README.md`. Responde a **Luiz Henrique**. Chefe do setor: **Guardiola**.

| Craque | id técnico | Função |
|---|---|---|
| **Ronaldo** | ronaldo-assistente | Central de controle pessoal (estilo J.A.R.V.I.S., desde 2026-11-04): painel de 8 cartões, planejamento do dia, agenda, único que fala com o Guilherme no Telegram |
| **Guardiola** | guardiola-po-agilista | PO e agilista: quadro Kanban, prioridade, WIP; sincronizado com o Trello (o Guilherme manda) |
| **Pedri** | pedri-gestor-tarefas | Tarefas e projetos, prioridades do dia |
| **Rodri** | rodri-apontamento-horas | Apontamento e fechamento de horas |
| **Kroos** | kroos-acessos-seguranca | Calendário de troca de senhas e acessos (nunca guarda senha) |
| **Lamine Yamal** | lamine-yamal-linkedin | Rascunhos de posts do LinkedIn (nunca publica). **Planejado:** o LinkedIn vira setor próprio via backlog do **Zico** (decisão do Guilherme, 2026-11-09); ainda não criado, **Lamine Yamal** segue aqui até lá |
| **Bellingham** | bellingham-dicas-ios | Dicas conceituais de iOS (Swift, boas práticas, ferramentas), criado em 2026-11-09. Uso raro; tools `Read`, `Write`, `WebSearch`; escreve só em `dicas_ios/dicas.md`; nunca pede nem recebe código, nome de projeto ou dado do trabalho |

### Setor de finanças pessoais (criado em 2026-10-30)
Contrato em `financas/README.md`. Dados só locais. Chefe do setor: **Casemiro** (único agente).

| Craque | id técnico | Função |
|---|---|---|
| **Casemiro** | casemiro-financeiro | Recebimentos, gastos e gastos futuros; dados em `financas/` (base: `contexto.md`); dashboard local (`dashboard.html` no computador, `dashboard.png` para o celular) gerado por script sem token. No Telegram, escrever "dashboard" para o **Ronaldo** recebe a imagem na hora |

### Setor de programação (criado em 2026-11-03)
Contrato em `programacao/README.md`. Responde a **Luiz Henrique**. Chefe técnico: **Thiago Silva**. Código-alvo: este repositório (Corte em `estudio/`, `media/`, `run.py`, `render/`). Ágil, sprint de 1 semana; só muda código com teste; sem commit sem o Guilherme pedir; nada publicado.

| Craque | id técnico | Função |
|---|---|---|
| **Zico** | zico-po-programacao | PO: backlog e aceite |
| **Xavi** | xavi-scrum-master | Scrum Master: quadro e cerimônias |
| **Ancelotti** | ancelotti-agile-coach | Agile Master: coach de processo |
| **Thiago Silva** | thiago-silva-tech-lead | Tech lead e arquiteto |
| **Rodrygo** | rodrygo-dev-back | Dev back-end (Python) |
| **Endrick** | endrick-dev-front | Dev front-end (web do Corte) |
| **Iniesta** | iniesta-ux-corte | UX da interface do Corte |
| **Alisson** | alisson-qa | QA |
| **Marquinhos** | marquinhos-devops-release | DevOps e release |

**Maestro da sprint** (**PAUSADO** desde 2026-11-05, confirmado em 2026-11-09; só volta se o Guilherme mandar). Desenho: `programacao/maestro.py`, tarefa `ContextoExplica-Sprint`, a cada 15 min com a Sprint aberta, 07h-23h; registrado em 2026-11-04: chama o agente dono de cada coluna do quadro, que grava a decisão em `programacao/maestro/decisoes/PROG-NNN.json`; só o maestro move o cartão (quadro.md e Trello). Para "Feito", exige o aceite do Guilherme em `programacao/aceites/PROG-NNN.md` (**Zico** confere e recomenda). Substituiu o antigo `monitor_cr.py`. Ver `ecossistema/engenharia-ia/INSTALACAO-MONITOR-CR.md`.

Backlog inicial (superado, hoje até PROG-016, ver Pendências): PROG-001 (etapa de componentes "não se aplica" sem explicação) e PROG-002 ("Iniciar cenas" não faz nada), em `programacao/backlog.md`.

## Regras do ecossistema

- Cada agente escreve só na própria pasta. Ninguém reescreve arquivo de outro.
- **Só o Ronaldo fala com o Guilherme no Telegram.** Qualquer agente de qualquer setor que precise avisá-lo passa o pedido ao **Ronaldo** (formato em `produtividade/README.md`).
- Nenhum agente guarda senha, token ou chave. Credencial fica no `.env` ou no gerenciador de senhas do Guilherme.
- Ação externa (publicar, enviar, lançar, trocar) é sempre do Guilherme. Os agentes preparam.
- Só Claude: não manter arquivos de outras ferramentas de IA.
- Nomes de craques em mensagens: inicial maiúscula e em negrito. Ids técnicos ficam em crases.
- **Espelho do sistema (regra do Guilherme, 2026-11-09):** ele prefere ler os documentos em `espelho_sistema.html` (gerado por `tools/gerar_espelho.py`). O espelho se regenera sozinho por hook sempre que um agente cria ou altera `.md` ou `.txt`, então nenhum agente precisa fazer nada. Todo documento novo deve ser `.md` legível.
- Nenhum agente assume nicho, tema ou ferramenta que o Guilherme não tenha dito. Se faltar, pergunta com opções.

## Pendências

- Confirmar que ferramenta de gestão de tarefas e de horas a empresa usa (Jira, Azure DevOps, Notion, planilha...), para o formato dos arquivos de `produtividade/` combinar com ela.
- ~~Agente de dicas de iOS~~: resolvido em 2026-11-09, criado **Bellingham**.
- **Acessos da empresa (Kroos):** fora de escopo, decisão do Guilherme em 2026-11-09. Não tratar como pendência do setor.
- **LinkedIn como setor próprio:** planejado, via backlog do **Zico**. Não criar agora.
- Setor de ação do canal: indefinido.
- Confirmar com o Guilherme se os títulos dos cartões devem ser genéricos, por causa de dado confidencial do trabalho.
- **Casemiro**: pendências de conciliação em `financas/pendencias.md` (banco do salário, saldo total, emissor do cartão, contas já pagas, próximo salário, despesas essenciais, autorização da planilha).
- **Busquets e Xabi Alonso** (PROG-013/014): aceitos pelo Guilherme em 2026-11-09 (`programacao/aceites/`). Tetos de custo **mantidos por decisão de 2026-11-09**: **Busquets** US$ 0,30 e **Xabi Alonso** US$ 0,20 (limite diário de US$ 1,10 inalterado).
- **Maestro da sprint: PAUSADO** (confirmado pelo Guilherme em 2026-11-09). A tarefa `ContextoExplica-Sprint` fica desligada e só volta quando ele mandar. A Sprint 01 anda por pedidos dele, sem o maestro de 15 em 15 min.
- **Sprint 01 em 2026-11-09:** backlog já vai até PROG-016 (o de "backlog inicial" abaixo está superado). Entrada em andamento: PROG-016 (Catálogo da aba Agentes) e PROG-015 (ação da próxima etapa); PROG-003 aceito; PROG-011 pausado; próximo aceite marcado para sexta 14/11. Fonte: `programacao/backlog.md` e `programacao/sprints/sprint-01.md`.
- **Agentes sem setor claro:** **Kane** (narrador), **Dembelé** (Reels), **Memphis** e **Valverde** estão listados em blocos do canal/transversal, mas nenhum tem contrato de pasta própria no mapa (`reels/README.md` existe para o Dembelé).
- **Daily das 10:30:** registrada como decisão; falta o **Ronaldo** cadastrar o lembrete recorrente (`produtividade/lembretes.json`) e o Guilherme confirmar dias da semana.
- **Codex: decidido em 2026-11-09.** O Codex é RESERVA: quando o Claude esgotar o limite, a produção pula para o Codex para não parar (conforme o `CLAUDE.md`). Enquanto o Claude estiver disponível, não se usa Codex. Resta apenas gerar o espelho em `.codex/agents` de **Valverde**, **Garro** e **Bellingham** (`python tools/sincronizar_codex.py`), quando o Guilherme pedir.
- **Ronaldo como central de controle (2026-11-04):** decisões do Guilherme: nenhum conector de casa por enquanto (iPhone, sem dispositivos para equipar), Slack não será ligado, e a tela principal é um painel no navegador igual à referência "AETHER" (feito, ver Infraestrutura). **Clima ligado em 2026-11-04** (Open-Meteo, cidade padrão Jundiaí por suposição; trocável em `produtividade/.ronaldo_painel_local.json`). SEGURANÇA, CASA/IOT, SLACK e E-MAIL ficam `NÃO CONECTADO` no painel e no agente. Em aberto: e-mail (não decidido), confirmar a cidade do clima, voz no painel e abrir o painel no celular (hoje só no computador; proposta de modo `--rede` com senha feita ao Guilherme).
- **PROP-RONALDO-DASHBOARD** (`programacao/PROP-RONALDO-DASHBOARD.md`, do **Valverde**): o painel do **Ronaldo** entregue em `produtividade/` cobre parte do que ela propõe (agenda, tarefas, ordens por agente, sprint). Faltam, se o Guilherme quiser: aba "Agora" com os agentes do Corte ao vivo, status do canal e bloqueios detalhados. **Zico** decide se a proposta segue, encolhe ou fecha; nenhum arquivo de `programacao/` foi alterado.
- **Clipes (registrado em 2026-11-10):** melhorar a transcrição (refino nos cortes escolhidos, pré-triagem do **Rivaldo** com dados públicos do YouTube) e dar nota e ordem por momento ao **Rivaldo**. Detalhes e outros ajustes em `clipes/pendencias.md`; aviso de amanhã pedido ao **Ronaldo**.
- Se a sessão não reconhecer os agentes novos, reiniciar o Claude Code.

## Infraestrutura compartilhada

- **Avisos no celular:** `produtividade/avisar.py` + `produtividade/lembretes.json`, via bot do Telegram. Qualquer setor pode cadastrar lembretes seguindo o formato descrito em `produtividade/README.md`. Estado (2026-10-30): bot `@ronaldo_r9_assistente_bot` criado, token e chat id no `.env`, teste enviado e tarefa `ContextoExplica-Avisos` registrada no Agendador do Windows (a cada minuto, só com o usuário logado).
- **Conversa com o Ronaldo pelo Telegram (texto e áudio):** `produtividade/ronaldo_telegram.py` + tarefa `ContextoExplica-Ronaldo` (ver `produtividade/README.md`). Depende do computador ligado e do Claude Code logado.
- **Trello:** quadro privado "Kanban Trabalho" (https://trello.com/b/EUTjJRqq/kanban-trabalho), sincronizado em mão dupla com `produtividade/kanban.md` por `produtividade/trello_sync.py` (tarefa `ContextoExplica-Trello`, a cada 10 minutos). **Regra do Guilherme: o que ele muda no Trello vale e nenhum agente desfaz.** Credenciais só no `.env` (`TRELLO_API_KEY`, `TRELLO_TOKEN`).
- **Agentes pelo Telegram:** além do **Ronaldo**, o Guilherme chama **Pedri**, **Rodri**, **Kroos**, **Lamine Yamal**, **Casemiro**, **Guardiola** e **Luiz Henrique** começando a mensagem pelo nome (texto ou áudio). **De Bruyne** também (desde 2026-10-30): roda em segundo plano (teto US$ 3,00 por pedido, sem publicar nem gastar), avisa e envia o vídeo pronto; frase com "De Bruyne" em qualquer ponto vai direto para ele. O **Ronaldo** não repassa recados a ninguém. **Remote Control** (`claude remote-control`, app do Claude no celular) serve para trabalho maior, com aprovação no celular.
- **Telegram do Ronaldo:** comandos sem custo `/hoje`, `/dashboard` e `/ajuda`; o resto é conversa livre (texto ou áudio). A lista do que ele faz e não faz está em `AJUDA` no `ronaldo_telegram.py`.
- **Painel do Ronaldo (2026-11-04):** `produtividade/painel.py` + `painel.html`, aberto por `produtividade\painel.bat` em http://127.0.0.1:8766/ (só local, só biblioteca padrão). Mostra agenda, tarefas, avisos, finanças, sprint, consumo e conexões; dá ordens aos agentes pelo mesmo roteamento do Telegram e cria/marca itens direto nos arquivos. Contrato e limites em `produtividade/README.md`. Fora do Agendador do Windows por enquanto: abre quando o Guilherme quiser.
- **Google Agenda:** conectada em 2026-10-30 (conta pessoal do Guilherme, projeto Google próprio `optimum-sound-387200`, separado do do YouTube). `produtividade/google_agenda.py` sincroniza `agenda.json` com a Agenda em mão dupla, a cada 5 min (tarefa `ContextoExplica-GoogleAgenda`); o que o Guilherme muda no Google vale e nunca se apaga evento. App em modo "Testando": a autorização vence a cada 7 dias e o **Ronaldo** avisa no Telegram para reconectar (`python produtividade/google_pessoal.py`). Publicar exigiria links de página inicial e política de privacidade.
- **Google Planilhas:** não conectado (a API do Sheets não está ativada no projeto novo). A planilha oficial de finanças fica fora do alcance dos agentes por enquanto; `financas/planilha_ler.py` está pronto para quando a API for ativada.

## Rotinas e turnos

- **2026-11-04:** maestro da sprint no setor de programação (ver o bloco do setor acima); registro de **Luiz Henrique**.

- **Daily diária às 10:30** (decisão de 2026-11-03, setor de programação): conduzida por **Xavi**, formato de `programacao/README.md` (estado por item, impedimentos, próximos passos). Antes valia "sob demanda". Agendamento pelo **Ronaldo**, pendente (ver Pendências).
- **Turno de 2h** (autorizado pelo Guilherme na noite de 2026-11-03): janela de trabalho autônomo dos agentes, sem publicar, sem gastar e sem commit. Neste turno **Luiz Henrique** atualizou o mapa e adiantou a proposta de PROG-013/014.

## Histórico

- 2026-11-09: criado **Bellingham** (`bellingham-dicas-ios`) no setor de produtividade: dicas conceituais de iOS, só `Read`, `Write` (para `produtividade/dicas_ios/dicas.md`) e `WebSearch`, modelo sonnet, uso raro; proibido receber código, projeto ou dado do trabalho. Suposições: nome escolhido por mim; WebSearch incluído para confirmar APIs atuais. Mapa corrigido: maestro **PAUSADO**; Codex **decisão pendente** (nada alterado, sem espelho); LinkedIn planejado como setor próprio via backlog do **Zico** (não criado); acessos da empresa fora de escopo. Total agora 42 agentes. Reiniciar o Claude Code se a sessão não reconhecer o **Bellingham**.
- 2026-11-09 (revisão do mapa): conferidos os 41 arquivos de `.claude/agents` contra este mapa: todos estão listados (nenhum agente sem registro, nenhum registro sem arquivo; `.claude/agents_desativados/` não existe). Atualizados o aceite de PROG-013/014 e o estado da Sprint 01 (ver Pendências). Nenhum agente ou setor criado ou removido.

- 2026-11-10: criado **Rivaldo** (`rivaldo-avaliador-fonte`), avaliador da FONTE no setor de Clipes: primeiro agente do fluxo, logo depois da transcrição e antes do **Kaká**. Lê o vídeo longo inteiro (dados medidos pelo código em `triagem_dados.json` + transcrição) e grava `triagem.json` (nota 0-100, recomendação, momentos promissores) e `triagem.md`. Funciona como o **Totti**, mas na fonte. Nota abaixo do mínimo do projeto (padrão 45, configurável) PARA o fluxo e pergunta ao Guilherme (botão "Continuar mesmo assim"); ele decide. Suposições: nome escolhido por **Luiz Henrique** (livre no mapa); fica DEPOIS da transcrição (precisa do texto) e não antes; ligado por padrão em projetos novos, desligado nos antigos.
- 2026-11-09: criado **Garro** (`garro-scout-tecnologia-ia`), scout de tecnologia de IA para produção no setor de inteligência (pasta `inteligencia/tecnologia/`, com `README.md`, `ferramentas.md` e um arquivo por ciclo). Entra no passo 1 do ciclo, junto do **Hugo Souza**. **Vitinho** atualizado: além de `relatorios/` e `briefing_acao.md` (mantidos), passa a escrever `inteligencia/destaques.md` (resumo curto e visual, só links, histórico curto no fim). Registrada a regra do espelho do sistema (ver Regras). Pendência: reiniciar o Claude Code para reconhecer o **Garro**; espelho Codex não sincronizado (regra "só Claude").
- 2026-11-04 (noite): cartão **CLIMA** no painel do **Ronaldo**, via Open-Meteo (sem chave, atualização em segundo plano a cada 10 min, cidade padrão Jundiaí). Testado com dados reais.
- 2026-11-04 (noite): **Luiz Henrique** construiu o painel do **Ronaldo** no navegador (`produtividade/painel.py`, `painel.html`, `painel.bat`), seguindo a imagem "AETHER" do Guilherme. Testado: leitura do estado real, criação e marcação de itens (em cópia dos arquivos), recusa de `Host`/`Origin` de fora e uma ordem real ao **Ronaldo** (14,6 s). Sem integração de casa, Slack, e-mail ou clima.
- 2026-11-09: Codex registrado como reserva (decisão do Guilherme, sai de pendência); tetos de **Busquets** (US$ 0,30) e **Xabi Alonso** (US$ 0,20) mantidos; maestro da sprint segue pausado.
- 2026-11-04: **Ronaldo** reescrito por **Luiz Henrique** a pedido do Guilherme: virou central de controle estilo J.A.R.V.I.S. (painel com 8 cartões, regra "verdade do painel", confirmação para ação sensível, estados `OFFLINE`/`NÃO CONECTADO`). Mantidos os arquivos que ele escreve, os recados, os avisos e as regras do Telegram. Sem integração de casa, Slack, e-mail ou clima por enquanto (ver Pendências). Espelho Codex não atualizado (ver Pendências do **Valverde**).
- 2026-11-03: criado **Valverde** (`valverde-engenheiro-ia`), engenheiro de IA para otimizar token no fluxo, com foco nos filtros de **Vini** e **Courtois**. Só propõe; quem aplica é o dono do arquivo, com aprovação do Guilherme. Espelho Codex não gerado (ver Pendências).
- 2026-11-03 (noite): **Luiz Henrique** registrou a daily das 10:30 e o turno de 2h; escreveu a proposta de estrutura de PROG-013/014 (aprendiz **Busquets** e curador **Xabi Alonso**, nomes sugeridos) em `ecossistema/proposta-prog-013-014.md`. Nenhum agente criado, aguardando o Guilherme.
- 2026-11-03: criado o setor de programação (**Zico**, **Xavi**, **Ancelotti**, **Thiago Silva**, **Rodrygo**, **Endrick**, **Iniesta**, **Alisson**, **Marquinhos**), contrato em `programacao/README.md`; backlog inicial com PROG-001 e PROG-002. Visão geral: agora são cinco blocos (canal, inteligência, produtividade, finanças, programação).

- 2026-10-30: criado **Raphinha** (curador de componentes visuais): desenha telas, textos, setas e ícones do vídeo, o Guilherme valida por imagem, e as regras de layout vão para o **Olise**. Aprende em `componentes/aprendizados.md` até o Guilherme dizer "pronto".
- 2026-10-30: criado **Luiz Henrique**; criado o setor de produtividade com **Pedri**, **Rodri**, **Kroos** e **Lamine Yamal**; criado este mapa.
- 2026-10-30: criado **Ronaldo** (assistente pessoal e canal único do Telegram). Telegram ligado no mesmo dia (bot, teste e Agendador).
- 2026-10-30: resumo diário às 08:30 no Telegram (`resumo_dia`, a partir de `produtividade/agenda.json`); criados **Casemiro** (finanças) e **Guardiola** (PO/Kanban).
- 2026-10-30: **Ronaldo** passou a conversar pelo Telegram, por texto e áudio; resumo diário e respostas com emojis.
- 2026-10-30: **Casemiro** recebeu o handoff financeiro (dados em `financas/`), dashboard gerado e resumo com recomendações enviado pelo **Ronaldo**; avisos de vencimento cadastrados.
- 2026-10-30: principais agentes acessíveis pelo Telegram (roteamento por nome em `ronaldo_telegram.py`); Remote Control aberto no computador.
- 2026-10-30: Google Agenda conectada (mão dupla, a cada 5 min); aviso de 1h antes automático para todo compromisso.
- 2026-10-30: Trello ligado (quadro "Kanban Trabalho"), em mão dupla com `kanban.md`; mudança do Guilherme no Trello sempre vence.
- 2026-10-30: **Ronaldo** inventou que tinha mandado o pedido ao **De Bruyne** (não havia canal). Corrigido: **De Bruyne** no Telegram em segundo plano, **Ronaldo** proibido de afirmar repasses e passou ao modelo sonnet com histórico maior.
- 2026-11-03: **Corte** (`python -m corte`, pacote `estudio/`): a interface do Estúdio virou também editor de vídeo, editor de fluxos em grafo e editor de agentes. Salvar um agente grava em `.claude/agents`, e desativar move o arquivo para `.claude/agents_desativados/`, então vale também no terminal. Detalhes em `estudio/README.md`.
- 2026-11-03: dois estilos novos, **Cartoon Vivo** e **Colagem Documental**, com a variação Caderno pautado no Scratch; registro único em `media/estilos.py` e skill `estilos-por-camadas`, usada pelo **Olise**. A janela de novo projeto lista os temas do **Modric** sem vídeo e pode acioná-lo para gerar um.
- 2026-11-03: roteiro refatorado: seis tipos em `prompts/tipos_de_roteiro.md`, no máximo 2 números e 1 gráfico por Short, situação concreta antes de dado (`media/roteiro.py` conta, a conformidade avisa). Base: pesquisa de **Hugo Souza** e **Yuri Alberto**.
- 2026-11-03: o Corte abre também no celular, no Wi-Fi de casa, com senha (`python -m corte --rede`). Fora de casa ainda não: pede uma rede privada entre os aparelhos.
- 2026-11-03: **Reserva com Codex**: os mesmos agentes (`.claude/agents`, fonte de verdade) rodam pelo Codex só quando o Claude esgota o limite, nos trabalhos do Corte. Espelho gerado por `python tools/sincronizar_codex.py` (`.codex/agents`, `.agents/skills`); **Luiz Henrique** roda a sincronização ao criar ou mudar agente. Detalhes em `estudio/README.md`.
- 2026-11-03: **Regra do quadro** no setor de programação: o Trello "Kanban Trabalho" é a única fonte de trabalho (só itens da sprint ativa, cartões PROG-NNN); sem cartão, o pedido volta ao **Zico**, salvo "faz já, fora do quadro" do Guilherme. Codex segue como reserva (regra antiga "só Claude" do setor revogada). Ver `programacao/README.md`.
