# Ecossistema do Guilherme · Mapa vivo

Mantido por **Luiz Henrique** (`luiz-henrique-ecossistema`). Toda criação, mudança ou remoção de agente ou setor é registrada aqui, com data. É a primeira leitura de quem precisa do contexto geral.

## Visão geral

O ecossistema é o braço direito do Guilherme (desenvolvedor iOS). Hoje tem dois blocos:

1. **Contexto Explica**: a empresa do canal dark (YouTube, pt-BR, Shorts de análise de comportamento social e gerações). Detalhes em `CLAUDE.md`.
2. **Produtividade profissional**: setor novo, para organizar o trabalho do Guilherme como dev iOS (tarefas, horas, acessos, LinkedIn). Sem código de app: o código dele é feito na IA da empresa.

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
| **Olise** | olise-diretor-arte |
| **Barcola** | barcola-diretor-horizontal |
| **Mbappé** | mbappe-editor-metadados |
| **Vini** | vini-auditor-conformidade |
| **Sidorf** | sidorf-thumbnail-estrategista |
| **Kane** | kane-narrador |
| **Messi** | messi-estrategista-angulo |
| **Cristiano** | cristiano-otimizador-viral |
| **Haaland** | haaland-pesquisador-nicho |
| **Memphis** | memphis-social-media |
| **Dembelé** | dembele-reels-instagram (Instagram, separado do canal) |
| **De Bruyne** | debruyne-orquestrador |

### Setor de inteligência
Contrato em `inteligencia/README.md`. Chefe do setor: **De Bruyne**. Equipe: **Hugo Souza**, **Fagner**, **André Carrillo**, **Raniele**, **Yuri Alberto**, **Vitinho**. Setor de ação do canal: ainda não existe.

### Setor de produtividade profissional (criado em 2026-10-30)
Contrato em `produtividade/README.md`. Responde a **Luiz Henrique**. Chefe do setor: **Guardiola**.

| Craque | id técnico | Função |
|---|---|---|
| **Ronaldo** | ronaldo-assistente | Assistente pessoal: planejamento do dia, agenda, único que fala com o Guilherme no Telegram |
| **Guardiola** | guardiola-po-agilista | PO e agilista: quadro Kanban, prioridade, WIP; sincronizado com o Trello (o Guilherme manda) |
| **Pedri** | pedri-gestor-tarefas | Tarefas e projetos, prioridades do dia |
| **Rodri** | rodri-apontamento-horas | Apontamento e fechamento de horas |
| **Kroos** | kroos-acessos-seguranca | Calendário de troca de senhas e acessos (nunca guarda senha) |
| **Lamine Yamal** | lamine-yamal-linkedin | Rascunhos de posts do LinkedIn (nunca publica) |

### Setor de finanças pessoais (criado em 2026-10-30)
Contrato em `financas/README.md`. Dados só locais. Chefe do setor: **Casemiro** (único agente).

| Craque | id técnico | Função |
|---|---|---|
| **Casemiro** | casemiro-financeiro | Recebimentos, gastos e gastos futuros; dados em `financas/` (base: `contexto.md`); dashboard local (`dashboard.html` no computador, `dashboard.png` para o celular) gerado por script sem token. No Telegram, escrever "dashboard" para o **Ronaldo** recebe a imagem na hora |

## Regras do ecossistema

- Cada agente escreve só na própria pasta. Ninguém reescreve arquivo de outro.
- **Só o Ronaldo fala com o Guilherme no Telegram.** Qualquer agente de qualquer setor que precise avisá-lo passa o pedido ao **Ronaldo** (formato em `produtividade/README.md`).
- Nenhum agente guarda senha, token ou chave. Credencial fica no `.env` ou no gerenciador de senhas do Guilherme.
- Ação externa (publicar, enviar, lançar, trocar) é sempre do Guilherme. Os agentes preparam.
- Só Claude: não manter arquivos de outras ferramentas de IA.
- Nomes de craques em mensagens: inicial maiúscula e em negrito. Ids técnicos ficam em crases.
- Nenhum agente assume nicho, tema ou ferramenta que o Guilherme não tenha dito. Se faltar, pergunta com opções.

## Pendências

- Confirmar que ferramenta de gestão de tarefas e de horas a empresa usa (Jira, Azure DevOps, Notion, planilha...), para o formato dos arquivos de `produtividade/` combinar com ela.
- Definir se o setor de produtividade terá um agente de dicas técnicas de iOS (só orientação, sem código).
- Setor de ação do canal: indefinido.
- Confirmar com o Guilherme se os títulos dos cartões devem ser genéricos, por causa de dado confidencial do trabalho.
- **Casemiro**: pendências de conciliação em `financas/pendencias.md` (banco do salário, saldo total, emissor do cartão, contas já pagas, próximo salário, despesas essenciais, autorização da planilha).
- Se a sessão não reconhecer os agentes novos, reiniciar o Claude Code.

## Infraestrutura compartilhada

- **Avisos no celular:** `produtividade/avisar.py` + `produtividade/lembretes.json`, via bot do Telegram. Qualquer setor pode cadastrar lembretes seguindo o formato descrito em `produtividade/README.md`. Estado (2026-10-30): bot `@ronaldo_r9_assistente_bot` criado, token e chat id no `.env`, teste enviado e tarefa `ContextoExplica-Avisos` registrada no Agendador do Windows (a cada minuto, só com o usuário logado).
- **Conversa com o Ronaldo pelo Telegram (texto e áudio):** `produtividade/ronaldo_telegram.py` + tarefa `ContextoExplica-Ronaldo` (ver `produtividade/README.md`). Depende do computador ligado e do Claude Code logado.
- **Trello:** quadro privado "Kanban Trabalho" (https://trello.com/b/EUTjJRqq/kanban-trabalho), sincronizado em mão dupla com `produtividade/kanban.md` por `produtividade/trello_sync.py` (tarefa `ContextoExplica-Trello`, a cada 10 minutos). **Regra do Guilherme: o que ele muda no Trello vale e nenhum agente desfaz.** Credenciais só no `.env` (`TRELLO_API_KEY`, `TRELLO_TOKEN`).
- **Agentes pelo Telegram:** além do **Ronaldo**, o Guilherme chama **Pedri**, **Rodri**, **Kroos**, **Lamine Yamal**, **Casemiro**, **Guardiola** e **Luiz Henrique** começando a mensagem pelo nome (texto ou áudio). **De Bruyne** também (desde 2026-10-30): roda em segundo plano (teto US$ 3,00 por pedido, sem publicar nem gastar), avisa e envia o vídeo pronto; frase com "De Bruyne" em qualquer ponto vai direto para ele. O **Ronaldo** não repassa recados a ninguém. **Remote Control** (`claude remote-control`, app do Claude no celular) serve para trabalho maior, com aprovação no celular.
- **Telegram do Ronaldo:** comandos sem custo `/hoje`, `/dashboard` e `/ajuda`; o resto é conversa livre (texto ou áudio). A lista do que ele faz e não faz está em `AJUDA` no `ronaldo_telegram.py`.
- **Google Agenda:** conectada em 2026-10-30 (conta pessoal do Guilherme, projeto Google próprio `optimum-sound-387200`, separado do do YouTube). `produtividade/google_agenda.py` sincroniza `agenda.json` com a Agenda em mão dupla, a cada 5 min (tarefa `ContextoExplica-GoogleAgenda`); o que o Guilherme muda no Google vale e nunca se apaga evento. App em modo "Testando": a autorização vence a cada 7 dias e o **Ronaldo** avisa no Telegram para reconectar (`python produtividade/google_pessoal.py`). Publicar exigiria links de página inicial e política de privacidade.
- **Google Planilhas:** não conectado (a API do Sheets não está ativada no projeto novo). A planilha oficial de finanças fica fora do alcance dos agentes por enquanto; `financas/planilha_ler.py` está pronto para quando a API for ativada.

## Histórico

- 2026-10-30: criado **Luiz Henrique**; criado o setor de produtividade com **Pedri**, **Rodri**, **Kroos** e **Lamine Yamal**; criado este mapa.
- 2026-10-30: criado **Ronaldo** (assistente pessoal e canal único do Telegram). Telegram ligado no mesmo dia (bot, teste e Agendador).
- 2026-10-30: resumo diário às 08:30 no Telegram (`resumo_dia`, a partir de `produtividade/agenda.json`); criados **Casemiro** (finanças) e **Guardiola** (PO/Kanban).
- 2026-10-30: **Ronaldo** passou a conversar pelo Telegram, por texto e áudio; resumo diário e respostas com emojis.
- 2026-10-30: **Casemiro** recebeu o handoff financeiro (dados em `financas/`), dashboard gerado e resumo com recomendações enviado pelo **Ronaldo**; avisos de vencimento cadastrados.
- 2026-10-30: principais agentes acessíveis pelo Telegram (roteamento por nome em `ronaldo_telegram.py`); Remote Control aberto no computador.
- 2026-10-30: Google Agenda conectada (mão dupla, a cada 5 min); aviso de 1h antes automático para todo compromisso.
- 2026-10-30: Trello ligado (quadro "Kanban Trabalho"), em mão dupla com `kanban.md`; mudança do Guilherme no Trello sempre vence.
- 2026-10-30: **Ronaldo** inventou que tinha mandado o pedido ao **De Bruyne** (não havia canal). Corrigido: **De Bruyne** no Telegram em segundo plano, **Ronaldo** proibido de afirmar repasses e passou ao modelo sonnet com histórico maior.
