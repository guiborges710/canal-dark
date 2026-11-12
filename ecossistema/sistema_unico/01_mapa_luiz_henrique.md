# Sistema único · Mapa do ecossistema (Luiz Henrique)

Data: 2026-11-11. Insumo para o **Firmino** desenhar o protótipo do app local que une todo o ecossistema. Complementa o trabalho do **Valverde** (fluxos, contratos de arquivos, pontos de autorização, interfaces existentes).

Convenção: tudo que não tem marca vem de arquivo lido (READMEs, `CLAUDE.md`, `.claude/agents/*.md`, `ecossistema/setores.json`, pastas). **[DEDUÇÃO]** marca inferência minha. **[LACUNA]** marca ausência confirmada.

Fontes: `ecossistema/README.md`, `CLAUDE.md`, memória do projeto, `ecossistema/setores.json` (fonte única de setores e agentes lida por `estudio/painel.py` e `estudio/central.py`), README de cada setor, descrição de cada agente.

Contagem real: 57 arquivos em `.claude/agents/` hoje (o mapa diz 42 em 2026-11-09; cresceu com Clipes, Pirlo, Firmino etc.; ver seção 5).

---

## 1. Setores

`setores.json` lista 7 grupos (programacao, inteligencia, producao, clipes, pesquisa_videos, pessoal, ecossistema). O mapa e os READMEs agrupam de outro jeito (finanças e produtividade separadas). Abaixo uso a divisão dos READMEs, indicando a correspondência.

### 1.1 Canal dark · Contexto Explica (grupo `producao` em `setores.json`)

- **Objetivo:** Shorts de YouTube pt-BR (30-60 s, 1080x1920) sem rosto, nicho "Análise de Comportamento Social e Gerações", monetizável.
- **Chefe:** **De Bruyne** (CEO do canal), sob **Luiz Henrique**. Quem posta: **Memphis** (manual).
- **Agentes** (`.claude/agents/`):

| Nome | id | Função |
|---|---|---|
| **De Bruyne** | `debruyne-orquestrador` | Coordena produção ponta a ponta, dispara agentes em paralelo |
| **Modric** | `modric-pesquisador-tema` | Pesquisa do tema, `notas.md` (3+ fontes) |
| **Memphis** | `memphis-social-media` | Referências virais (~1x/semana); responsável pela postagem manual |
| **Haaland** | `haaland-pesquisador-nicho` | Nicho e ideias de pauta (sob demanda) |
| **Messi** | `messi-estrategista-angulo` | Tese, pergunta, comentário próprio (sob demanda; o Neymar absorve no diário) |
| **Neymar** | `neymar-roteirista` | Ângulo + roteiro 30-60 s + `direcao_viral.md` |
| **Courtois** | `courtois-revisor-fatos` | Confere roteiro contra notas |
| **Cristiano** | `cristiano-otimizador-viral` | Eleva roteiro para viralizar (sob demanda) |
| **Raphinha** | `raphinha-curador-componentes` | Desenha componentes visuais; Guilherme valida por imagem; aprende em `componentes/aprendizados.md` |
| **Olise** | `olise-diretor-arte` | Cenas animadas (`cenas.json`) nos 4 estilos |
| **Barcola** | `barcola-diretor-horizontal` | Cenas sketch 16:9 (`--formato horizontal`) |
| **Mbappé** | `mbappe-editor-metadados` | Título, descrição, tags, texto da miniatura |
| **Vini** | `vini-auditor-conformidade` | Auditoria TEXTO (antes do render) e FINAL (só metadados bloqueiam) |
| **Seedorf** | `sidorf-thumbnail-estrategista` | Prompt de thumbnail para o ChatGPT (não gera imagem) |
| **Kane** | `kane-narrador` | Narra vídeo enviado com a voz do Guilherme |
| **Dembelé** | `dembele-reels-instagram` | Mini-fluxo de Reels do outro Instagram (separado; ver 1.8) |

- **Entradas:** briefing "produza um vídeo sobre X" (Guilherme/Telegram/Corte).
- **Saídas** em `output/<slug>/`: `notas.md`, `angulo.md`, `roteiro.txt`, `cenas.json`, `sketch_cenas.py`, `estilo.json`, `metadados.json`, `direcao_viral.md`, `auditoria_texto.md`, `auditoria.md`, `video.mp4`, `thumbnail.jpg`, `prompt_thumbnail.txt`, `PUBLICAR.txt`, `CONFORMIDADE.md`, `custo.json`, `eventos.json`, `corte.json`. Também `output/fila_postagem.txt`, `output/messi_assinatura_canal.md`, `componentes/` (`catalogo.md`, `aprendizados.md`), `prompts/` (`writer.md`, `angle.md`, `reviewer.md`, `metadata.md`, `research_*.md`, `tipos_de_roteiro.md`), `referencias/` (`referencias_nicho.md`, `analise_viral.md`), `voz/amostra.wav`, `config_shorts.yaml`.
- **Comandos:** `python run.py video --topic "..."` (único de produção; `--mock`, `--allow-paid`), `run.py check`, `run.py ideas`, `run.py publish --slug` (PRIVADO por padrão; exige `auditoria.md` APROVADA), `postar_pendentes.py`, `python -m corte` (interface web), `python -m media.estilos_demo`, `python -m media.sketch --slug <pasta> --previa`.
- **Regras relevantes ao app:** congelamento do roteiro depois da aprovação do **Vini**; nenhum render sem `auditoria_texto.md` APROVADO; publicar é passo manual do Guilherme.

### 1.2 Inteligência (grupo `inteligencia`)

- **Objetivo:** métricas, análises e atualização de mercado dark; sem produzir e sem publicar.
- **Chefe:** **De Bruyne**. Contrato: `inteligencia/README.md`.
- **Agentes:**

| Nome | id | Função | Escreve em |
|---|---|---|---|
| **Hugo Souza** | `hugo-souza-pesquisador-canais` | Cataloga canais dark do nicho | `canais/`, `fontes.md` |
| **Fagner** | `fagner-analista-titulos` | Títulos, descrições, tags | `titulos/` |
| **André Carrillo** | `andre-carrillo-analista-thumbnails` | Thumbnails dos canais catalogados | `thumbnails/` |
| **Raniele** | `raniele-analista-producao` | Como os canais produzem | `producao/` |
| **Yuri Alberto** | `yuri-alberto-analista-metricas` | Métricas do canal próprio | `metricas/` |
| **Garro** | `garro-scout-tecnologia-ia` | Ferramentas de IA para produção, custo zero primeiro | `tecnologia/` |
| **Vitinho** | `vitinho-consolidador` | Relatório por ciclo, briefing de ação, destaques | `relatorios/`, `briefing_acao.md`, `destaques.md` |
| **Busquets** | `busquets-aprendiz-canais-dark` | Estuda vídeos que o Guilherme sobe em `aprendiz/_entrada/` | `aprendiz/AAAA-MM-DD/` |
| **Xabi Alonso** | `xabi-alonso-curador-referencias` | Lista vídeos para estudo | `referencias_estudo/`, `aprendiz/fila.md` |

- **Entradas:** YouTube Data API (chave no `.env`), coletor OAuth do canal próprio, vídeos que o Guilherme coloca em `aprendiz/_entrada/`.
- **Saídas:** `inteligencia/destaques.md` (ponto de entrada do Guilherme), `relatorios/semana_AAAA-MM-DD.md` (+ `.html`), `briefing_acao.md`, `metricas/videos.csv` (+ `analytics_*.csv`, `ctr_manual.csv`, `slugs_manuais.csv`), `canais/_indice.md` e fichas, `tecnologia/ferramentas.md`, `aprendiz/estudados.md`, `fila.md`, `historico.jsonl`.
- **Comandos:** `python inteligencia/coletar_metricas.py`; `python inteligencia/aprendiz/rodar.py aprendiz` e `... curador`. Os demais agentes são chamados por **De Bruyne**/Claude Code, sem script.
- **Cadência:** hoje nada agendado ("Escala de 24 horas": decisão pendente). Ciclo: Hugo+Garro → Fagner/André/Raniele → Yuri → Vitinho. Busquets e Xabi Alonso fora do ciclo, sob demanda.
- **Observação:** `setores.json` marca `"ativo": false` para quase todos os setores; só `programacao` está `true`. Significado exato do campo não está documentado **[DEDUÇÃO: flag de "setor em rodada ativa" do painel]**.

### 1.3 Clipes (grupo `clipes`)

- **Objetivo:** cortes 9:16 de vídeos de terceiros para Instagram e TikTok, com gancho/fecho próprios, legenda palavra a palavra e crédito. Separado do canal e do Corte (não usa `output/`, `run.py`, `estudio/`).
- **Chefe:** **Pelé** (`pele-chefe-clipes`). Nada é publicado: o Guilherme posta à mão.
- **Agentes** (todos em `setores.json`):

| Nome | id | Função |
|---|---|---|
| **Pelé** | `pele-chefe-clipes` | Coordena fluxo, entrega o pacote |
| **Salah** | `salah-scout-fontes` | Acha fontes e confirma autorização/prova |
| **Rivaldo** | `rivaldo-avaliador-fonte` | Nota 0-100 da FONTE depois da transcrição; abaixo do mínimo (45) para o fluxo e pergunta |
| **Kaká** | `kaka-cacador-momentos` | Escolhe trechos que funcionam sozinhos (20-55 s) |
| **Zidane** | `zidane-editor-cortes` | Gancho e fecho próprios; dispara o corte 9:16 |
| **Figo** | `figo-diretor-ganchos` | Acha a frase mais forte; decide se abre com teaser |
| **Totti** | `totti-avaliador-potencial` | Nota 0-100 por corte pronto |
| **Buffon** | `buffon-auditor-originalidade` | Gate: autorização, crédito, comentário próprio, duração, marca d'água |
| **Lewandowski** | `lewandowski-embalagem-plataformas` | Legenda, descrição, hashtags por plataforma |
| **Roberto Carlos** | `roberto-carlos-gestor-perfis` | Criação/aquecimento/cadência dos perfis novos (pasta `contas/`) |

- **Entradas:** URL ou arquivo de vídeo longo, `--autor`, `--autorizacao` (`livre` sem prova desde 2026-11-10), perfil (`geral` padrão, `gta6`).
- **Saídas** em `clipes_out/<slug>/` (gitignored): `fonte.mp4`, `transcricao.json`, `triagem_dados.json`, `triagem.json/.md`, `momentos.json`, `selecao.json`, `perfil.json`, `clipes/NN.mp4` + `NN.json`, `publicar/NN_instagram.txt` e `NN_tiktok.txt`, `estado.json`, `processo.log`. Perfis em `clipes/perfis/<id>.json` (+ `_historico/`). Pendências em `clipes/pendencias.md`.
- **Comandos:** `.venv\Scripts\python -m clipes painel` (http://127.0.0.1:8767/), `tudo <URL> --autor ... --autorizacao livre [--perfil gta6]`, `momentos`, `cortar`, `ajustar`, `legendas` (legenda do YouTube em vez de Whisper), `refinar`, `triagem-dados`, `avaliar`, `check`, `embalar`, `perfis [mostrar|duplicar]`, `estado`. Testes em `clipes/testes/`.
- **Limite conhecido:** o painel mostra a vez dos subagentes mas não os dispara; no modo `--rede` é só leitura.

### 1.4 Pesquisa de vídeos longos (grupo `pesquisa_videos`)

- **Objetivo:** alimentar o Clipes com vídeos longos mais vistos (dia, semana, mês).
- **Agente único:** **Pirlo** (`pirlo-pesquisador-videos`).
- **Entrada:** tema/região/duração mínima (padrão GTA 6, 20+ min). YouTube Data API (cota ~100 unidades por busca).
- **Saída:** `pesquisa_videos/saida/AAAA-MM-DD.md/.json` (e variantes por tema: moda, casais, tiktok-*).
- **Comando:** `.venv\Scripts\python -m pesquisa_videos [--tema ... --min-minutos 20 --quantos 10 --regiao BR]`.
- **Contas (Clipes):** `contas/` (README, `identidade.md`, `checklist_hoje.md`, `plano.md`, `plano_completo.md`, `pesquisa*.md`) pertence a **Roberto Carlos**; estado: nenhuma conta criada (TikTok/Instagram "não"); lançamento do GTA 6 em 19/11/2026 (fonte: README de `contas/`).

### 1.5 Produtividade profissional (parte de `pessoal` em `setores.json`)

- **Objetivo:** organizar o trabalho do Guilherme como dev iOS (tarefas, horas, acessos, LinkedIn). Não escreve código de app; não executa nada fora daqui.
- **Chefe:** **Guardiola** (README do mapa) / responsável **Luiz Henrique** (README do setor).
- **Agentes:**

| Nome | id | Função | Escreve em |
|---|---|---|---|
| **Ronaldo** | `ronaldo-assistente` | Central de controle pessoal; único que fala com o Guilherme no Telegram; painel de 8 cartões | `agenda.json`, `agenda.md`, `lembretes.json` |
| **Guardiola** | `guardiola-po-agilista` | PO/Kanban pessoal, WIP, Trello | `kanban.md` |
| **Pedri** | `pedri-gestor-tarefas` | Tarefas e projetos, prioridade do dia | `tarefas.md` |
| **Rodri** | `rodri-apontamento-horas` | Apontamento e fechamento de horas | `horas.md` |
| **Kroos** | `kroos-acessos-seguranca` | Calendário de troca de senhas (nunca guarda senha); "acessos da empresa" fora de escopo | `acessos.md` |
| **Lamine Yamal** | `lamine-yamal-linkedin` | Rascunhos de LinkedIn (nunca publica) | `linkedin/rascunhos.md` |
| **Bellingham** | `bellingham-dicas-ios` | Dicas conceituais de iOS; uso raro | `dicas_ios/dicas.md` |

- **Entradas:** pedidos por Telegram (texto/áudio), caixa de comando do painel, Google Agenda (mão dupla), Trello "Kanban Trabalho" (mão dupla, mudança do Guilherme vence).
- **Saídas:** arquivos acima + `lembretes.json`, `.ronaldo_custo.jsonl`, `.ronaldo_painel_ordens.jsonl`, `.estado_avisos.json`. Clima via Open-Meteo (cidade padrão Jundiaí, suposição).
- **Comandos/serviços:** `produtividade\painel.bat` (http://127.0.0.1:8766/); tarefas do Agendador do Windows `ContextoExplica-Avisos` (a cada minuto), `-Ronaldo` (Telegram), `-Trello` (10 min), `-GoogleAgenda` (5 min); `python produtividade/google_pessoal.py` (reconectar Google a cada 7 dias); `avisar.py`, `trello_sync.py`, `kanban_programacao.py`.
- **Cadências:** resumo diário 08:30 (Telegram), aviso 1 h antes de cada compromisso, daily 10:30 da programação (lembrete ainda não cadastrado).
- **Conexões marcadas `NÃO CONECTADO` no painel:** segurança, casa/IoT, Slack, e-mail.

### 1.6 Finanças pessoais (parte de `pessoal` em `setores.json`)

- **Objetivo:** recebimentos, gastos, gastos futuros e vencimentos; dashboard local.
- **Agente único e chefe:** **Casemiro** (`casemiro-financeiro`). Avisos passam pelo **Ronaldo**.
- **Entradas:** o que o Guilherme diz ("recebi X", "gastei Y") por chat ou Telegram.
- **Saídas** em `financas/`: `contexto.md`, `movimentos.csv`, `saldos.csv`, `pendencias.md`, `dashboard.html`, `dashboard.png`.
- **Comando:** `python financas/dashboard.py`; no Telegram, "dashboard" ao **Ronaldo** devolve a imagem.
- **Regras:** dados só locais; sem número de cartão, CPF, senha; não paga nada; planilha Google oficial fora do alcance (API do Sheets não ativada, `planilha_ler.py` pronto).

### 1.7 Programação (grupo `programacao`, único com `ativo: true`)

- **Objetivo:** evoluir o código deste repositório (Corte em `estudio/`, `media/`, `run.py`, `render/`) em sprints de 1 semana. Não é código de app do trabalho.
- **Chefe técnico:** **Thiago Silva**; responde a **Luiz Henrique**. Aceite sempre do Guilherme.
- **Agentes:**

| Nome | id | Função |
|---|---|---|
| **Zico** | `zico-po-programacao` | PO: backlog, aceite (`backlog.md`) |
| **Xavi** | `xavi-scrum-master` | Quadro, cerimônias, WIP (`quadro.md`) |
| **Ancelotti** | `ancelotti-agile-coach` | Coach de processo (`melhoria.md`) |
| **Thiago Silva** | `thiago-silva-tech-lead` | Refinamento, arquitetura, code review (`tecnico/`, `revisoes/`) |
| **Rodrygo** | `rodrygo-dev-back` | Dev Python (`entregas/`) |
| **Endrick** | `endrick-dev-front` | Dev web do Corte (`entregas/`) |
| **Iniesta** | `iniesta-ux-corte` | UX da interface (`ux/`) |
| **Alisson** | `alisson-qa` | QA (`qa/`) |
| **Marquinhos** | `marquinhos-devops-release` | DevOps e notas de release (`release/`) |

- **Entradas:** pedidos do Guilherme ao **Zico**; quadro Trello "Kanban Trabalho" (cartões `[PROG-NNN]`) como única fonte de trabalho.
- **Saídas:** `programacao/backlog.md`, `quadro.md`, `sprints/sprint-NN.md`, `entregas/`, `qa/`, `revisoes/`, `aceites/PROG-NNN.md`, `release/`, `maestro/decisoes/PROG-NNN.json`, `pedidos.jsonl`, `pausas.json`; propostas: `PROP-RONALDO-DASHBOARD.md`, `refinamento-painel-unificado.md` (**relevante a este projeto**).
- **Comandos:** `programacao/maestro.py` (tarefa `ContextoExplica-Sprint`, **PAUSADO** desde 2026-11-05; só volta se o Guilherme mandar); baterias em `estudio/testes/`.
- **Cadências:** sprint 1 semana; daily 10:30; planning, review e retro no começo/fim (próximo aceite marcado 14/11).

### 1.8 Reels (Instagram, outro perfil) (dentro de `producao` em `setores.json`)

- **Objetivo:** mini-fluxo separado do canal; imagens vêm de outra IA (ChatGPT), montagem local.
- **Agente:** **Dembelé** (`dembele-reels-instagram`).
- **Entradas:** briefing; imagens que o Guilherme gera fora e salva em `reels/projetos/<slug>/imagens/`.
- **Saídas:** `cenas.json`, `prompt_imagens.txt`, `reel.mp4` em `reels/projetos/<slug>/`; config em `reels/config.yaml`.
- **Comandos:** `python reels/make_reel.py novo <slug>`, `... <slug>`, `... <slug> --mock`, `--vozes`.
- Há 8 projetos de Reels em `reels/projetos/` (atendimento/vendas por WhatsApp, pelo que mostram os slugs **[DEDUÇÃO]** sobre o tema).

### 1.9 Ecossistema / transversal (grupo `ecossistema`)

| Nome | id | Função |
|---|---|---|
| **Luiz Henrique** | `luiz-henrique-ecossistema` | Cabeça: cria/organiza agentes e setores, mantém `ecossistema/README.md` |
| **Valverde** | `valverde-engenheiro-ia` | Engenharia de IA: diagnostica consumo de token e fluxos; só propõe (`ecossistema/engenharia-ia/`) |
| **Firmino** | `firmino-frontend-design` | Atalho para a skill `frontend-design`, serve ao ecossistema inteiro (não consta no mapa nem em `setores.json`) |

- **Interface do Corte (transversal ao canal):** `python -m corte` (http://127.0.0.1:8765/, `--rede` para celular com senha). Telas: Projetos, Estúdio, Revisão, Editor, Agentes (editor que grava em `.claude/agents/<id>.md`), Fluxos (grafo editável); `/api/agentes/ao-vivo`. Detalhes no README de `estudio/` e na análise do **Valverde**.
- **Infra:** espelho `espelho_sistema.html` (`tools/gerar_espelho.py`, regenerado por hook `tools/hook_espelho.py`), `ecossistema/dashboard-setores.html`, `tools/sincronizar_codex.py` (reserva Codex).

---

## 2. Dados/telas por setor e ações que o Guilherme precisa disparar sem VS Code

Onde marcado **[JÁ EXISTE]** há tela hoje; o resto é o que o app único precisaria cobrir **[DEDUÇÃO a partir dos fluxos documentados]**.

| Setor | Dados a mostrar | Ações a disparar |
|---|---|---|
| **Canal** | Fila de projetos e etapa de cada slug; quem está trabalhando/esperando (**[JÁ EXISTE]** no Corte); roteiro, auditorias (texto e final), vídeo, thumbnail, metadados; custo por vídeo; fila de postagem; referências virais; componentes do **Raphinha** (imagens para validar); estilos | Novo vídeo por tema (inclui temas do **Modric**); aprovar/pedir ajuste por versão; validar componentes; editar vídeo e exportar; subir PRIVADO (`publish`, só com `auditoria.md` APROVADA); copiar prompt de thumbnail; marcar publicação manual; autorizar nova versão (decisão exclusiva dele) |
| **Inteligência** | `destaques.md`, relatório semanal, métricas por vídeo (CSV), fichas de canais, ferramentas de IA (Garro), fila e relatórios do Busquets, avisos de pendência (escopo `yt-analytics`) | Rodar ciclo; rodar `coletar_metricas`; subir vídeo em `_entrada/`; rodar Busquets/Xabi Alonso; refazer consentimento OAuth |
| **Clipes** | Fluxo de agentes com status e progresso, cortes com nota do Totti, triagem do Rivaldo, editor de ajuste, eventos (**[JÁ EXISTE]** em :8767) | Colar link e iniciar; "Continuar mesmo assim" na triagem; ajustar/avaliar corte; criar/editar perfis; aprovar pacote (postar é manual) |
| **Pesquisa de vídeos / Contas** | Lista por janela, perfis TikTok/Instagram (estado, checklist do dia, plano D-n) | Rodar pesquisa; marcar passo do aquecimento feito |
| **Produtividade** | Agenda, tarefas, avisos, Kanban, horas, acessos a vencer, rascunhos LinkedIn, dicas iOS, clima, consumo, conexões (**[JÁ EXISTE]** no painel :8766) | Ordem a qualquer agente; criar/marcar tarefa, compromisso, lembrete; resumo do dia; copiar texto de horas para o sistema da empresa; aprovar rascunho de LinkedIn (publicar é manual) |
| **Finanças** | Dashboard, movimentos, saldos, pendências, vencimentos | "Recebi/gastei/paguei" em linguagem natural; regenerar dashboard; responder pendência de conciliação |
| **Programação** | Quadro por coluna, sprint, backlog, aceites pendentes, entregas/QA/revisão, estado do maestro (pausado) | Registrar pedido (**Zico**); aceitar/recusar em `aceites/PROG-NNN.md`; religar/pausar maestro; abrir/fechar sprint; "faz já, fora do quadro" |
| **Reels** | Projetos, prompt em lote, imagens por cena, `reel.mp4` | Novo projeto; copiar prompt de imagens; montar reel |
| **Ecossistema** | Mapa, agentes por setor, pendências, histórico, consumo, propostas do **Valverde** | Criar/editar/desativar agente e setor; "dados do ecossistema"; disparar **Valverde**; sincronizar Codex |

Ações transversais que o app deve concentrar: central de aprovações (todos os "espera você"), central de avisos (substitui o Telegram só para leitura; o **Ronaldo** segue como canal do Telegram), consumo/custo por agente e por dia (hoje `custo.json`, `.ronaldo_custo.jsonl` e tetos de US$ 1,10 por dia no setor de inteligência), e conexões (Telegram, Google Agenda, Trello, YouTube OAuth: validade e estado).

---

## 3. O que é editável pelo Guilherme e o que é só leitura

**Editável (pelo app, com salvamento nos arquivos de origem):**
- **Agentes:** frontmatter e corpo de `.claude/agents/<id>.md` (já editável no Corte; desativar move para `.claude/agents_desativados/`; ferramentas e modelos só entre os existentes). Depois de mudar, rodar `tools/sincronizar_codex.py`.
- **Fluxos:** grafo de produção do canal (Corte, tela Fluxos; versões publicadas e foto por execução).
- **Prompts do canal:** `prompts/*.md` e `prompts/tipos_de_roteiro.md` **[DEDUÇÃO: são arquivos do pipeline, tratados como editáveis]**; `config_shorts.yaml` (voz, orçamento, ritmo).
- **Perfis do Clipes:** criar/editar/duplicar/arquivar, com versionamento em `perfis/_historico`.
- **Cadências e lembretes:** `produtividade/lembretes.json`, `agenda.json`, compromissos (sincroniza com Google Agenda; o que o Guilherme muda vale), cidade do clima (`.ronaldo_painel_local.json`), configuração de etapas do Clipes (porcentagem dos destaques, nota mínima da triagem).
- **Trabalho:** tarefas, horas, kanban (o Trello do Guilherme vence), backlog, aceites (`programacao/aceites/PROG-NNN.md` é dele), `financas/movimentos.csv` e `pendencias`.
- **Decisões estratégicas:** nicho, assinatura do canal, estilos de vídeo, regras de autorização do Clipes.
- **Edição de vídeo:** `corte.json` pela tela Editor (exportar vira nova versão que o **Vini** audita).

**Só leitura (no app):**
- Entregas de agentes de análise: `inteligencia/*` (relatórios, fichas, métricas), `ecossistema/engenharia-ia/*`, `auditoria*.md`, `CONFORMIDADE.md`, `revisoes/`, `qa/`, `entregas/`.
- **Congelado por regra (decisão do Guilherme, 2026-11-03):** `roteiro.txt` depois da aprovação do **Vini** e o pacote audiovisual depois do render; só o Guilherme autoriza nova versão.
- `custo.json`, `eventos.json`, `.ronaldo_custo.jsonl`, `.estado_avisos.json`, `estado.json`, logs.
- `CLAUDE.md` do canal e `ecossistema/README.md` (mexe quem tem autoridade: o **Luiz Henrique** no mapa; `CLAUDE.md` só com pedido explícito).
- Modo `--rede` (celular): painel do Clipes é só leitura; acompanhar e aprovar no Corte é permitido.
- Segredos: `.env`, `client_secret.json`, `.youtube_token.json`, `estudio/dados/senha_rede.txt` não aparecem nem são editáveis no app (nenhum agente guarda credencial).

**Ações que o app nunca deve executar sozinho** (cabe ao Valverde detalhar os pontos de autorização): publicar vídeo/post, lançar horas, enviar mensagem a terceiros, trocar senha, pagar conta, commit/push, tornar vídeo público no Studio, gasto com `--allow-paid`.

---

## 4. Sugestão de navegação (grupos e menu)

Princípio: o app abre em **Hoje** e agrupa por intenção do Guilherme, não por pasta. Cada setor continua dono dos próprios arquivos.

1. **Hoje** (início)
   - Agora (agentes ao vivo, o que espera aprovação dele, o que falhou)
   - Agenda e tarefas do dia, avisos, clima (cartões do painel do **Ronaldo**)
   - Caixa de ordem ao **Ronaldo** e aos agentes
2. **Canal Contexto Explica**
   - Projetos e fila (Shorts)
   - Estúdio / Revisão / Editor (Corte)
   - Componentes (**Raphinha**) e Estilos
   - Publicar e fila de postagem
   - Referências virais e Reels (**Dembelé**) como subitem separado
3. **Clipes**
   - Painel de fluxo e cortes
   - Perfis de conteúdo
   - Pesquisa de vídeos longos (**Pirlo**)
   - Contas TikTok/Instagram (**Roberto Carlos**)
4. **Inteligência**
   - Destaques
   - Métricas do canal
   - Concorrência (canais, títulos, thumbnails, produção)
   - Tecnologia de IA
   - Aprendiz (fila, estudados)
5. **Trabalho** (produtividade)
   - Tarefas e Kanban
   - Horas
   - Acessos
   - LinkedIn (rascunhos)
   - Dicas iOS
6. **Finanças**
   - Dashboard, movimentos, pendências
7. **Programação**
   - Quadro da sprint e backlog
   - Aceites (pendentes do Guilherme em destaque)
   - Releases e melhoria
8. **Ecossistema**
   - Agentes (catálogo + editor) e Fluxos
   - Mapa e pendências
   - Consumo e custos
   - Conexões (Telegram, Google, Trello, YouTube)
   - Engenharia de IA (propostas do **Valverde**)
   - Reserva Codex

Observações de navegação **[DEDUÇÃO]**: finanças e trabalho são pessoais e ficam separados do bloco "empresa" (canal, clipes, inteligência) para facilitar um futuro modo "só pessoal"; a memória do projeto diz que o painel do ecossistema mostra tudo, inclusive pessoal, e só segredos ficam fora (`painel-transparencia-total.md`).

---

## 5. Lacunas

Agentes que existem sem pasta/dado/entrada no mapa:
- **Firmino** (`firmino-frontend-design`): existe como agente, mas não está no `ecossistema/README.md` nem em `setores.json`.
- **Pirlo**, **Totti**, **Figo**, **Roberto Carlos**: existem em `.claude/agents/` e em `setores.json`, mas **não estão listados no mapa** do `ecossistema/README.md` (apenas **Rivaldo** aparece, no histórico). `pesquisa_videos/` e `contas/` também não aparecem no mapa.
- **Kane**, **Dembelé**, **Memphis**, **Valverde**: sem contrato de pasta próprio no mapa (pendência já registrada). Dembelé tem `reels/README.md`; Valverde escreve em `ecossistema/engenharia-ia/`; Kane e Memphis: Memphis tem `referencias/`, Kane não tem pasta de saída documentada.
- **Contagem desatualizada:** o mapa diz 42 agentes (2026-11-09); há 57 arquivos hoje.
- **Setor de ação do canal:** não existe (briefing em `inteligencia/briefing_acao.md` sem executor).
- **Setor LinkedIn próprio:** planejado via **Zico**, não criado; **Lamine Yamal** segue em produtividade.
- **Casemiro:** pendências de conciliação em `financas/pendencias.md` (banco, saldo, cartão, contas, salário, despesas essenciais, autorização da planilha); Google Sheets não conectado.
- **Kroos:** "acessos da empresa" fora de escopo; `acessos.md` cobre só acessos pessoais.
- **Rodri/Pedri:** ferramenta de tarefas e horas da empresa não confirmada (pendência no mapa); títulos de cartão genéricos por confidencialidade também pendente.
- **Inteligência sem agendamento:** nada automatizado; métricas de retenção e CTR dependem do escopo `yt-analytics.readonly` (decisão do Guilherme). Existe `metricas/analytics_*.csv` e `ctr_manual.csv`, o que sugere coleta manual **[DEDUÇÃO]**.
- **Espelho Codex** de **Valverde**, **Garro** e **Bellingham** não gerado; o do **Firmino** e dos agentes de Clipes não verificados (git mostra `.codex/agents` modificado/adicionado, estado atual não conferido).
- **Maestro da sprint pausado**; daily 10:30 sem lembrete cadastrado.
- **Painel do Ronaldo:** faltam aba "Agora" com agentes ao vivo, status do canal e bloqueios (proposta em `programacao/PROP-RONALDO-DASHBOARD.md`); e-mail, voz e acesso pelo celular em aberto; casa/IoT/Slack/segurança não conectados por decisão.
- **Clipes:** transcrição a melhorar, nota e ordem por momento do **Rivaldo** (`clipes/pendencias.md`).
- **Falta de fonte única de dados do app:** não há API unificada; cada setor tem servidor ou arquivos próprios (Corte :8765, Ronaldo :8766, Clipes :8767), `estudio/central.py` e `estudio/painel.py` já leem `setores.json` **[DEDUÇÃO: ponto de partida natural para o app único; Valverde cobre as interfaces]**.
- **Acesso fora de casa:** o Corte só funciona na rede local (sem Tailscale ou similar).
- **Navegação de documentos:** o Guilherme prefere ler em `espelho_sistema.html`; o app único precisa cobrir isso (renderização de `.md`).

Resultado: o app único é viável **sem novas pastas**; falta principalmente (a) corrigir o mapa e `setores.json` (Firmino, setor Reels separado, Finanças separada de Produtividade), (b) um índice de dados por setor, e (c) decidir o que fazer com as pendências acima.
