/* Dados de exemplo do protótipo. Nomes de agentes, setores, etapas e regras vêm dos documentos
   do Luiz Henrique e do Valverde. Valores (notas, custos, horários) são ilustrativos.
   Nada aqui é segredo: sem chaves, tokens, senhas nem IDs de conta. */
window.D = {};

D.hoje = "2026-11-11";

D.setores = [
  { id: "canal", nome: "Canal", chefe: "De Bruyne", ativo: true, desc: "Shorts do Contexto Explica, do tema ao upload privado." },
  { id: "clipes", nome: "Clipes", chefe: "Pelé", ativo: true, desc: "Cortes 9:16 de vídeos de terceiros para Instagram e TikTok." },
  { id: "inteligencia", nome: "Inteligência", chefe: "De Bruyne", ativo: false, desc: "Métricas e mercado dark. Não produz nem publica." },
  { id: "trabalho", nome: "Trabalho", chefe: "Guardiola", ativo: true, desc: "Agenda, tarefas, horas e acessos do dev iOS." },
  { id: "financas", nome: "Finanças", chefe: "Casemiro", ativo: true, desc: "Recebimentos, gastos e vencimentos, só locais." },
  { id: "programacao", nome: "Programação", chefe: "Thiago Silva", ativo: true, desc: "Evolui o Corte, o pipeline e o render em sprints de uma semana." },
  { id: "ecossistema", nome: "Ecossistema", chefe: "Luiz Henrique", ativo: true, desc: "Agentes, setores, fluxos, consumo e engenharia de IA." }
];

/* id, nome, setor, modelo, kit de ferramentas, descrição, escreve em */
D.TOOLKIT = {
  e: ["Read", "Write", "Edit", "Glob", "Grep"],
  p: ["Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"],
  r: ["Read", "Write", "Edit", "Glob", "Grep", "Bash(python run.py *)"],
  s: ["Read", "Write", "Edit", "Glob", "Grep", "Bash(python -m media.sketch *)", "Bash(ls *)"],
  o: ["Agent", "Read", "Write", "Edit", "Glob", "Grep", "Bash(python run.py *)", "Bash(ls *)"],
  l: ["Read", "Glob", "Grep", "Write"]
};
D.FERRAMENTAS_PERMITIDAS = ["Agent", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch", "Bash(python run.py *)", "Bash(python -m media.sketch *)", "Bash(ls *)", "Bash(dir *)"];
D.MODELOS = ["haiku", "sonnet", "opus"];

D.agentesBase = [
  ["debruyne-orquestrador", "De Bruyne", "canal", "sonnet", "o", "Coordena a produção ponta a ponta e dispara de uma vez todos os agentes cujo insumo já existe.", "output/<slug>/ (estado do fluxo)"],
  ["modric-pesquisador-tema", "Modric", "canal", "sonnet", "p", "Pesquisa o tema e entrega notas com 3 ou mais fontes.", "output/<slug>/notas.md"],
  ["memphis-social-media", "Memphis", "canal", "sonnet", "p", "Levanta referências virais (cerca de 1 vez por semana) e cuida da postagem manual.", "referencias/referencias_virais.md"],
  ["haaland-pesquisador-nicho", "Haaland", "canal", "sonnet", "p", "Pesquisa o nicho e propõe lotes de ideias. Só sob demanda.", "referencias/referencias_nicho.md"],
  ["messi-estrategista-angulo", "Messi", "canal", "sonnet", "e", "Define tese, pergunta e comentário próprio. O Neymar já absorve isso no diário.", "output/<slug>/angulo.md"],
  ["neymar-roteirista", "Neymar", "canal", "sonnet", "e", "Escolhe o tipo de roteiro e escreve o texto de 30 a 60 s com a direção viral.", "angulo.md, roteiro.txt, direcao_viral.md"],
  ["courtois-revisor-fatos", "Courtois", "canal", "sonnet", "e", "Confere o roteiro contra as notas. Só fato com fonte passa.", "output/<slug>/revisao.md"],
  ["cristiano-otimizador-viral", "Cristiano", "canal", "sonnet", "e", "Eleva o roteiro para retenção e compartilhamento. Só sob demanda.", "roteiro_notas.md"],
  ["raphinha-curador-componentes", "Raphinha", "canal", "opus", "s", "Desenha os componentes visuais nos quatro estilos e aprende com o Guilherme.", "componentes.md, componentes/aprendizados.md"],
  ["olise-diretor-arte", "Olise", "canal", "sonnet", "s", "Transforma o texto em cenas animadas seguindo a direção viral e os componentes.", "cenas.json, sketch_cenas.py"],
  ["barcola-diretor-horizontal", "Barcola", "canal", "sonnet", "s", "Cenas sketch dos vídeos horizontais 16:9.", "cenas.json (horizontal)"],
  ["mbappe-editor-metadados", "Mbappé", "canal", "sonnet", "e", "Escreve título, descrição, tags e texto da miniatura.", "metadados.json"],
  ["vini-auditor-conformidade", "Vini", "canal", "sonnet", "e", "Audita o texto antes do render e o pacote final depois. Só metadados bloqueiam a publicação.", "auditoria_texto.md, auditoria.md"],
  ["sidorf-thumbnail-estrategista", "Seedorf", "canal", "sonnet", "e", "Escreve o prompt da thumbnail para o ChatGPT. Não gera imagem.", "prompt_thumbnail.txt"],
  ["kane-narrador", "Kane", "canal", "sonnet", "e", "Narra vídeos enviados com a voz do Guilherme.", "videos-kane/"],
  ["dembele-reels-instagram", "Dembelé", "canal", "sonnet", "e", "Mini-fluxo de Reels do outro Instagram, separado do canal.", "reels/projetos/<slug>/"],
  ["pele-chefe-clipes", "Pelé", "clipes", "sonnet", "e", "Coordena o fluxo de Clipes e entrega o pacote para o Guilherme postar.", "clipes_out/<slug>/estado.json"],
  ["salah-scout-fontes", "Salah", "clipes", "sonnet", "p", "Acha fontes e confirma autorização.", "clipes_out/<slug>/fonte.mp4"],
  ["rivaldo-avaliador-fonte", "Rivaldo", "clipes", "sonnet", "e", "Dá nota de 0 a 100 à fonte depois da transcrição. Abaixo de 45, o fluxo para.", "triagem.json, triagem.md"],
  ["kaka-cacador-momentos", "Kaká", "clipes", "sonnet", "e", "Escolhe trechos de 20 a 55 s que funcionam sozinhos.", "momentos.json"],
  ["zidane-editor-cortes", "Zidane", "clipes", "sonnet", "e", "Escreve gancho e fecho próprios e dispara o corte 9:16.", "selecao.json"],
  ["figo-diretor-ganchos", "Figo", "clipes", "sonnet", "e", "Acha a frase mais forte e decide se abre com teaser. Não altera o texto aprovado.", "selecao.json"],
  ["totti-avaliador-potencial", "Totti", "clipes", "sonnet", "e", "Dá nota de 0 a 100 a cada corte pronto.", "clipes/NN.json"],
  ["buffon-auditor-originalidade", "Buffon", "clipes", "sonnet", "e", "Gate final: autorização, crédito, comentário próprio, duração, marca d'água.", "check.md"],
  ["lewandowski-embalagem-plataformas", "Lewandowski", "clipes", "sonnet", "e", "Legenda, descrição e hashtags por plataforma.", "publicar/NN_instagram.txt, NN_tiktok.txt"],
  ["roberto-carlos-gestor-perfis", "Roberto Carlos", "clipes", "sonnet", "e", "Criação, aquecimento e cadência dos perfis novos.", "contas/"],
  ["pirlo-pesquisador-videos", "Pirlo", "clipes", "sonnet", "p", "Lista os vídeos longos mais vistos para alimentar os Clipes.", "pesquisa_videos/saida/AAAA-MM-DD.md"],
  ["hugo-souza-pesquisador-canais", "Hugo Souza", "inteligencia", "sonnet", "p", "Cataloga canais dark do nicho.", "inteligencia/canais/"],
  ["fagner-analista-titulos", "Fagner", "inteligencia", "sonnet", "e", "Analisa títulos, descrições e tags dos canais catalogados.", "inteligencia/titulos/"],
  ["andre-carrillo-analista-thumbnails", "André Carrillo", "inteligencia", "sonnet", "e", "Analisa as thumbnails dos canais catalogados.", "inteligencia/thumbnails/"],
  ["raniele-analista-producao", "Raniele", "inteligencia", "sonnet", "e", "Descobre como os canais produzem.", "inteligencia/producao/"],
  ["yuri-alberto-analista-metricas", "Yuri Alberto", "inteligencia", "sonnet", "r", "Analisa as métricas do canal próprio.", "inteligencia/metricas/"],
  ["garro-scout-tecnologia-ia", "Garro", "inteligencia", "sonnet", "p", "Procura ferramentas de IA para produção, custo zero primeiro.", "inteligencia/tecnologia/"],
  ["vitinho-consolidador", "Vitinho", "inteligencia", "sonnet", "e", "Consolida o ciclo: fatos, hipóteses e lacunas.", "relatorios/, briefing_acao.md, destaques.md"],
  ["busquets-aprendiz-canais-dark", "Busquets", "inteligencia", "sonnet", "e", "Estuda os vídeos que o Guilherme sobe em aprendiz/_entrada/.", "inteligencia/aprendiz/AAAA-MM-DD/"],
  ["xabi-alonso-curador-referencias", "Xabi Alonso", "inteligencia", "sonnet", "p", "Lista vídeos para estudo.", "referencias_estudo/, aprendiz/fila.md"],
  ["ronaldo-assistente", "Ronaldo", "trabalho", "haiku", "e", "Central de controle pessoal. Único que fala com o Guilherme no Telegram.", "agenda.json, agenda.md, lembretes.json"],
  ["guardiola-po-agilista", "Guardiola", "trabalho", "sonnet", "e", "PO e Kanban pessoal, com WIP e Trello.", "produtividade/kanban.md"],
  ["pedri-gestor-tarefas", "Pedri", "trabalho", "haiku", "e", "Tarefas, projetos e prioridade do dia.", "produtividade/tarefas.md"],
  ["rodri-apontamento-horas", "Rodri", "trabalho", "haiku", "e", "Apontamento e fechamento de horas.", "produtividade/horas.md"],
  ["kroos-acessos-seguranca", "Kroos", "trabalho", "haiku", "e", "Calendário de troca de senhas. Nunca guarda senha.", "produtividade/acessos.md"],
  ["lamine-yamal-linkedin", "Lamine Yamal", "trabalho", "sonnet", "e", "Rascunhos de LinkedIn. Nunca publica.", "produtividade/linkedin/rascunhos.md"],
  ["bellingham-dicas-ios", "Bellingham", "trabalho", "sonnet", "e", "Dicas conceituais de iOS. Uso raro, nunca recebe código do trabalho.", "produtividade/dicas_ios/dicas.md"],
  ["casemiro-financeiro", "Casemiro", "financas", "sonnet", "e", "Recebimentos, gastos, vencimentos e dashboard. Não paga nada.", "financas/movimentos.csv, saldos.csv, pendencias.md"],
  ["zico-po-programacao", "Zico", "programacao", "sonnet", "e", "PO: backlog e recomendação de aceite.", "programacao/backlog.md"],
  ["xavi-scrum-master", "Xavi", "programacao", "sonnet", "e", "Quadro, cerimônias e WIP.", "programacao/quadro.md"],
  ["ancelotti-agile-coach", "Ancelotti", "programacao", "sonnet", "e", "Coach de processo.", "programacao/melhoria.md"],
  ["thiago-silva-tech-lead", "Thiago Silva", "programacao", "sonnet", "e", "Refinamento, arquitetura e code review.", "tecnico/, revisoes/"],
  ["rodrygo-dev-back", "Rodrygo", "programacao", "sonnet", "r", "Dev Python.", "programacao/entregas/"],
  ["endrick-dev-front", "Endrick", "programacao", "sonnet", "r", "Dev web do Corte.", "programacao/entregas/"],
  ["iniesta-ux-corte", "Iniesta", "programacao", "sonnet", "e", "UX da interface do Corte.", "programacao/ux/"],
  ["alisson-qa", "Alisson", "programacao", "sonnet", "r", "QA: roda as baterias e registra.", "programacao/qa/"],
  ["marquinhos-devops-release", "Marquinhos", "programacao", "sonnet", "e", "DevOps e notas de release.", "programacao/release/"],
  ["luiz-henrique-ecossistema", "Luiz Henrique", "ecossistema", "sonnet", "e", "Cria e organiza agentes e setores e mantém o mapa do ecossistema.", "ecossistema/README.md, setores.json"],
  ["valverde-engenheiro-ia", "Valverde", "ecossistema", "sonnet", "l", "Engenharia de IA: diagnostica consumo de token e fluxos. Só propõe.", "ecossistema/engenharia-ia/"],
  ["firmino-frontend-design", "Firmino", "ecossistema", "sonnet", "e", "Atalho da skill frontend-design. Serve ao ecossistema inteiro.", "ecossistema/prototipo/"]
];

D.agentePrompt = function (a) {
  return "Você é o " + a[1] + " (" + a[0] + "), do setor " + (D.setores.find(function (s) { return s.id === a[2]; }) || {}).nome + ".\n\n" +
    a[5] + "\n\nRegras:\n- Leia só o que o fluxo entregou. Não assuma nicho nem tema.\n- Grave o resultado em: " + a[6] + ".\n- Chaves e tokens ficam só no .env; nunca em texto ou código.\n- Nomes de colegas em negrito; ids técnicos em crases.\n- Se faltar informação indispensável, pare e registre a pergunta como \"espera você\".";
};

/* ---------- fluxos (nós: id, rótulo, tipo agent|code|gate, agente, depende de) ---------- */
D.fluxos = {
  canal: { nome: "Canal: produção de um Short", nos: [
    { id: "brief", t: "code", r: "Briefing e tema", a: "", d: [] },
    { id: "modric", t: "agent", r: "Pesquisa", a: "Modric", d: ["brief"] },
    { id: "neymar", t: "agent", r: "Ângulo e roteiro", a: "Neymar", d: ["modric"] },
    { id: "courtois", t: "agent", r: "Revisão de fatos", a: "Courtois", d: ["neymar"] },
    { id: "g_roteiro", t: "gate", r: "Aprovar roteiro", a: "você", d: ["courtois"] },
    { id: "raphinha", t: "agent", r: "Componentes", a: "Raphinha", d: ["g_roteiro"] },
    { id: "mbappe", t: "agent", r: "Metadados", a: "Mbappé", d: ["g_roteiro"] },
    { id: "g_comp", t: "gate", r: "Aprovar componentes", a: "você", d: ["raphinha"] },
    { id: "olise", t: "agent", r: "Cenas", a: "Olise", d: ["g_comp"] },
    { id: "g_cenas", t: "gate", r: "Aprovar cenas", a: "você", d: ["olise"] },
    { id: "vini_t", t: "agent", r: "Auditoria de texto", a: "Vini", d: ["g_cenas", "mbappe"] },
    { id: "narr", t: "code", r: "Narração", a: "Chatterbox", d: ["vini_t"] },
    { id: "g_narr", t: "gate", r: "Aprovar narração", a: "você", d: ["narr"] },
    { id: "render", t: "code", r: "Render", a: "run.py video", d: ["g_narr"] },
    { id: "vini_f", t: "agent", r: "Auditoria final", a: "Vini", d: ["render"] },
    { id: "g_video", t: "gate", r: "Aprovar vídeo", a: "você", d: ["vini_f"] },
    { id: "sidorf", t: "agent", r: "Prompt da thumbnail", a: "Seedorf", d: ["g_video"] },
    { id: "g_pub", t: "gate", r: "Publicar (privado)", a: "você", d: ["sidorf"] }
  ] },
  clipes: { nome: "Clipes: de um vídeo longo a um pacote", nos: [
    { id: "fonte", t: "agent", r: "Fonte", a: "Salah", d: [] },
    { id: "aut", t: "gate", r: "Autorização", a: "você", d: ["fonte"] },
    { id: "transc", t: "code", r: "Transcrição", a: "Whisper local", d: ["aut"] },
    { id: "triagem", t: "agent", r: "Triagem da fonte", a: "Rivaldo", d: ["transc"] },
    { id: "g_tri", t: "gate", r: "Continuar mesmo assim", a: "você", d: ["triagem"] },
    { id: "momentos", t: "code", r: "Momentos", a: "perfil", d: ["g_tri"] },
    { id: "cura", t: "agent", r: "Curadoria", a: "Kaká", d: ["momentos"] },
    { id: "g_rev", t: "gate", r: "Aceitar sugestões", a: "você", d: ["cura"] },
    { id: "coment", t: "agent", r: "Gancho, fecho e CTA", a: "Zidane", d: ["g_rev"] },
    { id: "g_txt", t: "gate", r: "Aprovar texto", a: "você", d: ["coment"] },
    { id: "figo", t: "agent", r: "Gancho de abertura", a: "Figo", d: ["g_txt"] },
    { id: "corte", t: "code", r: "Corte 9:16", a: "ffmpeg", d: ["figo"] },
    { id: "totti", t: "agent", r: "Potencial", a: "Totti", d: ["corte"] },
    { id: "buffon", t: "agent", r: "Originalidade", a: "Buffon", d: ["corte"] },
    { id: "embal", t: "agent", r: "Embalagem", a: "Lewandowski", d: ["totti", "buffon"] },
    { id: "g_fim", t: "gate", r: "Aprovação final", a: "você", d: ["embal"] }
  ] },
  inteligencia: { nome: "Inteligência: um ciclo", nos: [
    { id: "hugo", t: "agent", r: "Catálogo de canais", a: "Hugo Souza", d: [] },
    { id: "garro", t: "agent", r: "Ferramentas de IA", a: "Garro", d: [] },
    { id: "yuri", t: "agent", r: "Métricas do canal", a: "Yuri Alberto", d: [] },
    { id: "fagner", t: "agent", r: "Títulos", a: "Fagner", d: ["hugo"] },
    { id: "andre", t: "agent", r: "Thumbnails", a: "André Carrillo", d: ["hugo"] },
    { id: "raniele", t: "agent", r: "Produção", a: "Raniele", d: ["hugo"] },
    { id: "vitinho", t: "agent", r: "Relatório do ciclo", a: "Vitinho", d: ["fagner", "andre", "raniele", "garro", "yuri"] },
    { id: "brief", t: "code", r: "briefing_acao.md", a: "sem executor", d: ["vitinho"] }
  ] },
  programacao: { nome: "Programação: um cartão PROG-NNN", nos: [
    { id: "pedido", t: "agent", r: "Pedido no backlog", a: "Zico", d: [] },
    { id: "ref", t: "agent", r: "Refinamento", a: "Thiago Silva", d: ["pedido"] },
    { id: "faz", t: "agent", r: "Fazendo", a: "Rodrygo / Endrick", d: ["ref"] },
    { id: "teste", t: "agent", r: "Em teste", a: "Alisson", d: ["faz"] },
    { id: "rev", t: "agent", r: "Code review", a: "Thiago Silva", d: ["teste"] },
    { id: "aceite", t: "gate", r: "Aceite", a: "você", d: ["rev"] },
    { id: "feito", t: "agent", r: "Release", a: "Marquinhos", d: ["aceite"] }
  ] },
  trabalho: { nome: "Trabalho: central do Ronaldo", nos: [
    { id: "gui", t: "gate", r: "Pedido (Telegram ou painel)", a: "você", d: [] },
    { id: "ron", t: "agent", r: "Roteia pelo nome", a: "Ronaldo", d: ["gui"] },
    { id: "ag", t: "agent", r: "Tarefas, horas, acessos", a: "Pedri / Rodri / Kroos", d: ["ron"] },
    { id: "lin", t: "agent", r: "Rascunho de LinkedIn", a: "Lamine Yamal", d: ["ron"] },
    { id: "lem", t: "code", r: "lembretes.json", a: "Ronaldo", d: ["ag"] },
    { id: "avi", t: "code", r: "avisar.py (1 min)", a: "sem token", d: ["lem"] },
    { id: "ok", t: "gate", r: "Você confirma e executa", a: "você", d: ["lin"] }
  ] },
  financas: { nome: "Finanças: do que você disse ao dashboard", nos: [
    { id: "gui", t: "gate", r: "\"Recebi\" ou \"gastei\"", a: "você", d: [] },
    { id: "cas", t: "agent", r: "Registra e concilia", a: "Casemiro", d: ["gui"] },
    { id: "csv", t: "code", r: "movimentos.csv", a: "Casemiro", d: ["cas"] },
    { id: "dash", t: "code", r: "dashboard.py", a: "sem Claude", d: ["csv"] },
    { id: "pag", t: "gate", r: "Marcar como pago", a: "você", d: ["cas"] }
  ] },
  ecossistema: { nome: "Ecossistema: mudar um agente", nos: [
    { id: "ped", t: "gate", r: "Pedido ou proposta", a: "você", d: [] },
    { id: "val", t: "agent", r: "Diagnóstico", a: "Valverde", d: ["ped"] },
    { id: "luiz", t: "agent", r: "Rascunho da mudança", a: "Luiz Henrique", d: ["val"] },
    { id: "ap", t: "gate", r: "Aprovar diff", a: "você", d: ["luiz"] },
    { id: "cod", t: "code", r: "sincronizar_codex.py", a: "espelho", d: ["ap"] }
  ] }
};
/* andamento de exemplo por nó, só para o diagrama do canal */
D.andamentoCanal = { brief: "ok", modric: "ok", neymar: "ok", courtois: "ok", g_roteiro: "ok", raphinha: "ok", mbappe: "ok", g_comp: "ok", olise: "rodando", g_cenas: "bloq", vini_t: "bloq", narr: "bloq", g_narr: "bloq", render: "bloq", vini_f: "bloq", g_video: "bloq", sidorf: "bloq", g_pub: "bloq" };
D.andamentoClipes = { fonte: "ok", aut: "ok", transc: "ok", triagem: "ok", g_tri: "espera", momentos: "bloq", cura: "bloq", g_rev: "bloq", coment: "bloq", g_txt: "bloq", figo: "bloq", corte: "bloq", totti: "bloq", buffon: "bloq", embal: "bloq", g_fim: "bloq" };

/* ---------- decisões que esperam o Guilherme ---------- */
D.decisoes = [
  { id: "c5", cod: "C5", setor: "canal", ordem: 1, titulo: "Vini bloqueou o texto de \"fim dos terceiros lugares\"",
    ctx: "A auditoria de texto apontou 2 correções antes do render: um dado sem fonte confirmada e um título que promete mais do que o roteiro entrega.",
    trava: "Trava a narração e o render deste vídeo.", urgente: true,
    det: "<p><b>Roteiro (Neymar):</b> \"Linha 4 cita que 7 em cada 10 jovens perderam o hábito, sem fonte nas notas.\"</p><p><b>Metadados (Mbappé):</b> título promete \"a verdade sobre\", e o vídeo só levanta hipóteses.</p><p class=\"mudo pequeno\">Se dispensar o escopo, fica registrado \"APROVADO COM DISPENSA DO GUILHERME\" e o risco passa a ser seu.</p>",
    acoes: [{ k: "ok", r: "Encaminhar correções", dono: "Neymar e Mbappé corrigem; o Vini reaudita só o que mudou" }, { k: "risco", r: "Dispensar escopo", risco: true }], recusa: ["Texto", "Fato", "Gancho"], },
  { id: "c1", cod: "C1", setor: "canal", ordem: 2, titulo: "Aprovar roteiro v2: \"a recessão de amizades entre homens\"",
    ctx: "Tipo de roteiro diferente dos últimos 3 vídeos. 2 números e 1 gráfico. Courtois conferiu contra as 4 fontes das notas e não achou problema.",
    trava: "Libera Raphinha e Mbappé em paralelo.", urgente: true,
    det: "<div class=\"trecho\">Domingo à tarde. Ele abre o celular, vê o nome de um amigo de 2019 e fecha de novo.\nNão foi briga. Ninguém decidiu se afastar.\nO que mudou foi o tempo livre, a mudança de cidade, o trabalho remoto.\nGeração é rótulo; contexto é explicação.</div><p class=\"pequeno mudo\">Diff contra v1: gancho trocado (sem estatística no frame 0), fecho reescrito. Depois de aprovado, o roteiro fica congelado.</p>",
    acoes: [{ k: "ok", r: "Aprovar roteiro v2" }], recusa: ["Texto", "Fato", "Gancho", "Ritmo"], edit: { campo: "Comentário para o Neymar", dica: "O que você quer mudar no texto?" } },
  { id: "c8", cod: "C8", setor: "canal", ordem: 3, titulo: "Aprovar vídeo final: \"geração Z não quer filhos ou não pode ter\"",
    ctx: "Render pronto (47 s, 1080x1920). Auditoria final do Vini: aprovada, sem ressalvas de metadados. Custo do vídeo: US$ 0,00.",
    trava: "Libera o prompt da thumbnail e a fila de postagem.",
    det: "<p>Player e CONFORMIDADE.md abririam aqui. Depois da aprovação, o pacote audiovisual fica congelado: nova versão só com sua autorização explícita (C9).</p>",
    acoes: [{ k: "ok", r: "Aprovar vídeo" }], recusa: ["Imagem", "Som", "Narração", "Texto"] },
  { id: "c11", cod: "C11", setor: "canal", ordem: 4, titulo: "Subir como privado: \"mulheres não pararam de ter filhos, adiaram\"",
    ctx: "Primeiro da fila_postagem.txt. auditoria.md aprovada, thumbnail.jpg e metadados.json presentes. Sugestão de data: hoje 18:00.",
    trava: "Ação externa: sobe para o YouTube. Tornar público continua passo manual no Studio.", urgente: false,
    det: "<ul class=\"lista\"><li>auditoria.md: APROVADA pelo Vini</li><li>thumbnail.jpg: enviada em 10/11</li><li>Posição na fila: 1 de 2</li><li>Cadência: 1 vídeo por dia às 18:00 (limite de 2 por dia)</li></ul>",
    acoes: [{ k: "risco", r: "Subir como privado", risco: true, externa: true }], recusa: ["Metadados", "Miniatura"], },
  { id: "c2", cod: "C2", setor: "canal", ordem: 5, titulo: "Raphinha pede validação de 3 componentes (fase aprendendo)",
    ctx: "Celular com conversa, copo e casa vazia. Regra proposta: celular sempre com texto coerente com a cena.",
    trava: "Olise espera para desenhar as cenas.",
    det: "<p>Cada correção sua vira regra permanente em <code>componentes/aprendizados.md</code>.</p><div class=\"linha\"><span class=\"chip\">celular com chat</span><span class=\"chip\">copo</span><span class=\"chip\">casa vazia</span></div>",
    acoes: [{ k: "ok", r: "Aprovar os 3" }], recusa: ["Desenho", "Texto na tela", "Layout"] },
  { id: "c3", cod: "C3", setor: "canal", ordem: 6, titulo: "Aprovar 6 cenas do vídeo \"adultos morando com os pais\"",
    ctx: "Prévia gerada. Nenhum elemento cobre boneco nem texto (regra do Raphinha conferida).",
    trava: "Libera a auditoria de texto.", det: "<p>Previa.jpg com as 6 cenas, fala e texto na tela de cada uma.</p>",
    acoes: [{ k: "ok", r: "Aprovar cenas" }], recusa: ["Desenho", "Texto na tela", "Animação"] },
  { id: "c10", cod: "C10", setor: "canal", ordem: 7, titulo: "Thumbnail de \"jovens bebendo menos\": copiar prompt e enviar imagem",
    ctx: "Seedorf escreveu o prompt para o ChatGPT. A imagem é feita fora do sistema e enviada de volta.",
    det: "<div class=\"trecho\">Fundo azul-claro, boneco de palito sozinho à mesa, copo cheio intocado. Texto grande: \"NINGUÉM BEBEU\". Estilo sketch, sem rostos reais.</div>",
    acoes: [{ k: "copiar", r: "Copiar prompt" }, { k: "ok", r: "Já enviei a imagem" }], recusa: [] },
  { id: "c14", cod: "C14", setor: "canal", ordem: 20, titulo: "Referências virais com 9 dias: rodar o Memphis?",
    ctx: "A regra do fluxo é atualizar cerca de 1 vez por semana. Usa o plano do Claude.", det: "<p>Última rodada: 02/11/2026. Teto estimado de uso: 1 job de agente.</p>",
    acoes: [{ k: "ok", r: "Rodar o Memphis" }], recusa: [] },
  { id: "l1", cod: "L1", setor: "clipes", ordem: 8, titulo: "Triagem baixa: continuar mesmo assim?",
    ctx: "Rivaldo deu nota 38 à fonte (mínimo do projeto: 45). Muita conversa fora do assunto; 3 momentos promissores.", trava: "O fluxo de Clipes parou na triagem.", urgente: true,
    det: "<p><b>Motivos:</b> áudio com ruído nos primeiros 12 min; tema mistura 3 assuntos.</p><p><b>Momentos promissores:</b> 14:20 a 14:58, 31:05 a 31:40, 48:10 a 48:52.</p><p class=\"mudo pequeno\">Autorização da fonte: tipo livre, risco assumido e registrado.</p>",
    acoes: [{ k: "ok", r: "Continuar mesmo assim" }], recusa: ["Descartar fonte"] },
  { id: "l3", cod: "L3", setor: "clipes", ordem: 9, titulo: "Aprovar e editar o texto do Zidane (corte 02)",
    ctx: "Gancho, fecho e CTA escritos. Depois da sua aprovação o Figo não pode mudar o texto.", trava: "Trava o gancho de abertura e o corte.",
    det: "<div class=\"trecho\">Gancho: \"Ninguém te conta isso sobre o primeiro dia.\"\nFecho: \"O resto está no vídeo completo, crédito na legenda.\"\nCTA: \"Segue pra ver o próximo corte.\"</div>",
    acoes: [{ k: "ok", r: "Aprovar texto" }], recusa: ["Reescrever"], edit: { campo: "Gancho", dica: "Edite o gancho; o texto editado vale como está." } },
  { id: "l2", cod: "L2", setor: "clipes", ordem: 10, titulo: "Aceitar ou rejeitar 5 momentos sugeridos pelo Kaká",
    ctx: "Notas de 61 a 84. Dois exigem contexto antes do trecho.", det: "<ul class=\"lista\"><li>14:20 nota 84</li><li>31:05 nota 77</li><li>48:10 nota 72 (contexto necessário)</li><li>52:40 nota 66</li><li>59:02 nota 61 (contexto necessário)</li></ul>",
    acoes: [{ k: "ok", r: "Aceitar os 5" }], recusa: ["Revisar um a um"] },
  { id: "p1", cod: "P1", setor: "programacao", ordem: 11, titulo: "Aceite de PROG-013: painel unificado, versão inicial",
    ctx: "QA aprovou (Alisson), review aprovado (Thiago Silva). Zico recomenda aceitar. Review da sprint em 14/11.", trava: "Sem aceite, o maestro não move o cartão para Feito.",
    det: "<p>Critérios: 5 de 5 atendidos. Evidência em <code>qa/PROG-013.md</code> e <code>revisoes/PROG-013.md</code>.</p>", acoes: [{ k: "ok", r: "Aceitar PROG-013" }], recusa: ["Falta critério", "Bug", "Outro"] },
  { id: "p2", cod: "P2", setor: "programacao", ordem: 25, titulo: "Maestro da sprint pausado desde 05/11: religar?",
    ctx: "Só volta se você mandar. Verificar no agendador antes de afirmar o estado.", det: "<p>Tarefa <code>ContextoExplica-Sprint</code>. Religar passa a mover cartões sozinho.</p>",
    acoes: [{ k: "risco", r: "Religar o maestro", risco: true }], recusa: ["Manter pausado"] },
  { id: "a1", cod: "A1", setor: "trabalho", ordem: 12, titulo: "Rascunho de LinkedIn pronto: confirmar antes de publicar",
    ctx: "Lamine Yamal escreveu em inglês, tom humano. O sistema nunca publica por você.", trava: "Ação sensível: você publica à mão no LinkedIn.",
    det: "<div class=\"trecho\">Shipping a small thing every week taught me more about SwiftUI than any long course. Here is what stuck.</div>",
    acoes: [{ k: "copiar", r: "Copiar texto" }, { k: "risco", r: "Já publiquei, confirmo", risco: true }], recusa: ["Reescrever"], edit: { campo: "Rascunho", dica: "Edite o texto do post." } },
  { id: "a3", cod: "A3", setor: "ecossistema", ordem: 13, titulo: "Reconectar o Google Agenda (vence em 2 dias)",
    ctx: "O app Google está em modo Testando: a autorização vence a cada 7 dias. A consulta de agenda para de funcionar no vencimento.", trava: "Agenda e avisos do Ronaldo ficam defasados se vencer.",
    det: "<p>O consentimento acontece no navegador. Comando: <code>python produtividade/google_pessoal.py</code></p>", acoes: [{ k: "copiar", r: "Copiar comando" }, { k: "ok", r: "Já reconectei" }], recusa: [] },
  { id: "a2", cod: "A2", setor: "financas", ordem: 14, titulo: "Marcar conta de internet como paga",
    ctx: "Vencimento em 12/11, R$ 119,90. Casemiro só marca com sua confirmação e nunca paga nada.", det: "<p>O pagamento é feito por você no banco.</p>",
    acoes: [{ k: "ok", r: "Confirmar pagamento" }], recusa: [], edit: { campo: "Valor pago", dica: "Se o valor mudou, corrija aqui." } },
  { id: "a6", cod: "A6", setor: "ecossistema", ordem: 15, titulo: "Valverde propõe enxugar o prompt do Raphinha",
    ctx: "O arquivo tem 6.958 caracteres e é carregado em todo job. A proposta remove 3 trechos repetidos do CLAUDE.md.", det: "<p>O diff aparece antes de gravar. Vale para os próximos jobs; sincronizar o espelho do Codex em seguida.</p>",
    acoes: [{ k: "ver", r: "Abrir no editor", rota: "#/ecossistema/agentes" }], recusa: ["Recusar proposta"] },
  { id: "a4", cod: "A4", setor: "inteligencia", ordem: 16, titulo: "Liberar o escopo yt-analytics.readonly (retenção e CTR)?",
    ctx: "Hoje a Yuri Alberto só vê visualizações e inscritos. Com o escopo, ganha retenção e CTR; muda o consentimento OAuth.", det: "<p>Só leitura. Sem ele, CTR segue manual em <code>ctr_manual.csv</code>.</p>",
    acoes: [{ k: "ok", r: "Liberar o escopo" }], recusa: ["Manter como está", "Decidir depois"] },
  { id: "a5", cod: "A5", setor: "inteligencia", ordem: 17, titulo: "Agendar o ciclo de 24 h da Inteligência?",
    ctx: "Hoje nada roda sozinho. Duas opções: rotina agendada (gasta token a cada execução) ou ciclo manual.", det: "<p>Teto diário do setor: US$ 1,10. Custo por execução ainda não medido.</p>",
    acoes: [{ k: "ok", r: "Agendar (com teto diário)" }], recusa: ["Manter manual"] },
  { id: "a9", cod: "A9", setor: "trabalho", ordem: 18, titulo: "Cadastrar o lembrete da daily das 10:30",
    ctx: "A daily da programação não tem lembrete recorrente. O Ronaldo cadastra em lembretes.json.", det: "<p>Dias propostos: segunda a sexta.</p>",
    acoes: [{ k: "ok", r: "Cadastrar de segunda a sexta" }], recusa: [], edit: { campo: "Dias e horário", dica: "Ex.: seg, qua, sex às 10:30" } },
  { id: "c6", cod: "C6", setor: "canal", ordem: 30, titulo: "Narração de \"cnh aos 16 anos\" aguarda a auditoria de texto",
    ctx: "Nenhum render sem auditoria_texto.md aprovado. O botão libera sozinho quando o Vini aprovar.", bloqueada: true, trava: "Bloqueado: auditoria de texto ainda não rodou.", det: "", acoes: [], recusa: [] }
];

D.historicoDecisoes = [
  { q: "Ontem 21:14", t: "Aprovou roteiro v1 de \"jovens trocam de emprego\"", c: "C1" },
  { q: "Ontem 18:02", t: "Subiu como privado \"gen z frugal\"", c: "C11" },
  { q: "Ontem 09:40", t: "Aceitou PROG-012", c: "P1" }
];

/* ---------- jobs do console ---------- */
D.jobs = [
  { id: "j1", nome: "Olise: cenas de \"a recessão de amizades entre homens\"", tipo: "agente", estado: "rodando", motor: "Claude", modelo: "sonnet", tok: 18400, custo: 0.21, teto: 1.0, ini: "13:02", log: ["[13:02] Lendo roteiro.txt, direcao_viral.md e componentes.md", "[13:02] Estilo: sketch (padrão)", "[13:03] Escrevendo sketch_cenas.py cena 1 de 6"] },
  { id: "j2", nome: "python run.py video --topic \"cnh aos 16 anos\"", tipo: "pesado", estado: "espera", motor: "código", modelo: "-", tok: 0, custo: 0, teto: 0, ini: "-", log: ["Aguardando: auditoria_texto.md ainda não está APROVADO.", "O render só começa depois da auditoria."] },
  { id: "j3", nome: "Salah: buscar fonte (URL do vídeo longo)", tipo: "agente", estado: "erro", motor: "Claude", modelo: "sonnet", tok: 4200, custo: 0.05, teto: 0.5, ini: "12:41", log: ["[12:41] Baixando fonte com yt-dlp", "[12:41] ERRO 403: o site recusou o download.", "Sugestão: tentar de novo ou enviar o arquivo à mão em clipes_out/."] },
  { id: "j4", nome: "Vitinho: relatório semanal", tipo: "agente", estado: "ok", motor: "Claude", modelo: "sonnet", tok: 31200, custo: 0.38, teto: 0.5, ini: "09:15", log: ["[09:15] Lendo canais, titulos, thumbnails, producao e metricas", "[09:19] relatorios/semana_2026-11-09.md gravado", "[09:19] destaques.md atualizado", "Concluído."] }
];
D.comandos = [
  { id: "c_run", rot: "python run.py video --topic ...", pesado: true, gasta: false, arg: "tema" },
  { id: "c_check", rot: "python run.py check --topic ...", pesado: false, gasta: false, arg: "tema" },
  { id: "c_metr", rot: "python inteligencia/coletar_metricas.py", pesado: false, gasta: false },
  { id: "c_dash", rot: "python financas/dashboard.py", pesado: false, gasta: false },
  { id: "c_prev", rot: "python -m media.sketch --slug ... --previa", pesado: false, gasta: false, arg: "slug" },
  { id: "c_clip", rot: "python -m clipes tudo <URL> --autorizacao livre", pesado: true, gasta: false, arg: "URL" },
  { id: "c_sync", rot: "python tools/sincronizar_codex.py --verificar", pesado: false, gasta: false },
  { id: "c_pirlo", rot: "python -m pesquisa_videos --tema ... --min-minutos 20", pesado: false, gasta: false, arg: "tema" }
];

/* ---------- Canal ---------- */
D.projetos = [
  { slug: "a-recessao-de-amizades-entre-homens", tipo: "Situação e virada", etapa: "Cenas (Olise)", prog: 55, est: "rodando", ver: "v2" },
  { slug: "fim-dos-terceiros-lugares", tipo: "Pergunta aberta", etapa: "Auditoria de texto", prog: 62, est: "erro", ver: "v1" },
  { slug: "adultos-morando-com-os-pais", tipo: "Contraste de gerações", etapa: "Aprovar cenas", prog: 66, est: "espera", ver: "v1" },
  { slug: "cnh-aos-16-anos", tipo: "Mito e contexto", etapa: "Narração", prog: 68, est: "bloq", ver: "v1" },
  { slug: "jovens-bebendo-menos", tipo: "Situação e virada", etapa: "Thumbnail", prog: 92, est: "espera", ver: "v1" },
  { slug: "geracao-z-nao-quer-filhos-ou-nao-pode-ter", tipo: "Pergunta aberta", etapa: "Aprovar vídeo final", prog: 90, est: "espera", ver: "v1" },
  { slug: "mulheres-nao-pararam-de-ter-filhos-adiaram", tipo: "Contraste de gerações", etapa: "Pronto, na fila", prog: 100, est: "ok", ver: "v1" },
  { slug: "jovens-trocam-de-emprego", tipo: "Mito e contexto", etapa: "Pronto, na fila", prog: 100, est: "ok", ver: "v1" }
];
D.versoes = [
  { v: "v2", q: "10/11 21:05", t: "Gancho sem estatística; fecho reescrito", e: "Aguardando você", d: ["+ Domingo à tarde. Ele abre o celular e fecha de novo.", "- Em 2024, 4 em cada 10 homens relataram não ter amigos próximos.", "  Ninguém decidiu se afastar.", "+ Geração é rótulo; contexto é explicação."] },
  { v: "v1", q: "09/11 16:30", t: "Primeira versão do Neymar", e: "Substituída", d: ["- Em 2024, 4 em cada 10 homens relataram não ter amigos próximos.", "  Ninguém decidiu se afastar."] }
];
D.fila = ["mulheres-nao-pararam-de-ter-filhos-adiaram", "geracao-z-nao-quer-filhos-ou-nao-pode-ter"];
D.estilos = [
  { id: "sketch", nome: "Sketch", d: "Folha de caderno pautada, traço de caneta tremido. Padrão do canal.", padrao: true },
  { id: "cartoes", nome: "Cartões (SVG)", d: "Cartões com contorno grafite e sombra sólida. Só se o pedido disser \"estilo cartões\"." },
  { id: "cartoon_alive", nome: "Cartoon Vivo", d: "Cena descrita em dados, desenhada por camadas." },
  { id: "documentary_collage", nome: "Colagem Documental", d: "Recortes em camadas, descrita em dados." }
];
D.reels = [
  { slug: "atendimento-whatsapp-01", est: "ok", n: "reel.mp4 montado" }, { slug: "vendas-whatsapp-02", est: "espera", n: "faltam imagens em imagens/" },
  { slug: "vendas-whatsapp-03", est: "fila", n: "prompt_imagens.txt pronto, copiar" }
];

/* ---------- Clipes ---------- */
D.cortes = [
  { n: "01", t: "Primeiro dia sem plano", dur: 38, nota: 82, est: "ok", perfil: "geral" },
  { n: "02", t: "O que ninguém conta", dur: 44, nota: 71, est: "espera", perfil: "geral" },
  { n: "03", t: "Trailer: o detalhe que quase passou", dur: 29, nota: 66, est: "fila", perfil: "gta6" }
];
D.perfis = [
  { id: "geral", nome: "Geral", d: "Método único para qualquer vídeo. Padrão.", ver: 4, min: 45 },
  { id: "gta6", nome: "GTA 6", d: "Apartado para o lançamento de 19/11/2026.", ver: 2, min: 50 }
];
D.pesquisaVideos = [
  { t: "Tudo sobre o trailer 3 do GTA 6, análise cena a cena", c: "Canal A", dur: "34 min", v: "2,1 mi", j: "semana" },
  { t: "Como funciona a economia do Brasil em 40 minutos", c: "Canal B", dur: "41 min", v: "880 mil", j: "mês" },
  { t: "O que mudou no mercado de trabalho jovem", c: "Canal C", dur: "27 min", v: "410 mil", j: "dia" }
];
D.contas = [
  { p: "TikTok", est: "Não criada", p2: "Dia D-8 do lançamento" }, { p: "Instagram", est: "Não criada", p2: "Dia D-8 do lançamento" }
];

/* ---------- Inteligência ---------- */
D.metricas = [
  { v: "jovens trocam de emprego", vis: 3100, ret: 71 }, { v: "gen z frugal", vis: 2450, ret: 64 }, { v: "esquema de pirâmide", vis: 1820, ret: 58 },
  { v: "cnh aos 16 anos", vis: 1240, ret: 52 }, { v: "recessão de amizades", vis: 980, ret: 49 }
];
D.canaisDark = [
  { n: "Canal dark A", nicho: "Comportamento", inscritos: "412 mil", ritmo: "5 por semana" },
  { n: "Canal dark B", nicho: "Economia pessoal", inscritos: "188 mil", ritmo: "3 por semana" },
  { n: "Canal dark C", nicho: "Sociedade e gerações", inscritos: "96 mil", ritmo: "daily" }
];
D.ferramentas = [{ n: "Whisper local", s: "em uso, custo zero" }, { n: "Chatterbox (voz clonada)", s: "em uso, CPU" }, { n: "Biblioteca de sons por código", s: "em uso" }];
D.aprendiz = [{ q: "Na fila", t: "Vídeo de referência sobre retenção em Shorts" }, { q: "Estudado em 07/11", t: "Canal dark C: estrutura de gancho" }];

/* ---------- Trabalho ---------- */
D.agenda = [
  { h: "10:30", t: "Daily da programação", o: "Padrão (sem lembrete)" }, { h: "14:00", t: "Reunião de alinhamento do app", o: "Google Agenda" }, { h: "17:30", t: "Fechar horas do dia", o: "Ronaldo" }
];
D.tarefas = [
  { t: "Revisar PR da tela de login", p: "alta", e: false }, { t: "Enviar horas da semana", p: "média", e: false }, { t: "Atualizar dependências do projeto", p: "baixa", e: true }
];
D.avisos = ["Google Agenda vence em 2 dias", "Troca de senha do repositório em 5 dias (Kroos)", "Resumo diário enviado às 08:30"];
D.kanbanTrab = [
  { c: "A fazer", cards: ["Refatorar camada de rede", "Estudar Swift Concurrency"] }, { c: "Fazendo", cards: ["Tela de perfil do usuário"] }, { c: "Em revisão", cards: ["Correção do teclado no formulário"] }, { c: "Feito", cards: ["Ajuste de cores do tema escuro"] }
];
D.horas = [{ d: "Seg", h: 8 }, { d: "Ter", h: 7.5 }, { d: "Qua", h: 6 }, { d: "Qui", h: 0 }, { d: "Sex", h: 0 }];
D.acessos = [{ s: "Repositório de código", dias: 5 }, { s: "VPN", dias: 18 }, { s: "Ferramenta de tarefas", dias: 41 }];
D.linkedin = [{ t: "Shipping a small thing every week...", e: "Rascunho pronto" }, { t: "What I learned from a failed release", e: "Em ideia" }];
D.clima = { cidade: "Jundiaí", t: "24 °C", d: "Nublado. Chuva fraca à tarde." };

/* ---------- Finanças ---------- */
D.fin = {
  saldo: 4820.5, entradas: 6200, saidas: 3115.4,
  mov: [{ d: "10/11", t: "Salário", v: 6200, k: "in" }, { d: "09/11", t: "Mercado", v: -312.4, k: "out" }, { d: "08/11", t: "Assinatura Claude", v: -110, k: "out" }, { d: "07/11", t: "Aluguel", v: -1850, k: "out" }],
  venc: [{ d: "12/11", t: "Internet", v: 119.9 }, { d: "15/11", t: "Cartão", v: 842.3 }, { d: "20/11", t: "Condomínio", v: 410 }],
  pend: ["Confirmar saldo do banco principal", "Autorizar a planilha Google (API do Sheets não ativada)"],
  serie: [3100, 3400, 3050, 3300, 3115]
};

/* ---------- Programação ---------- */
D.sprint = { n: 14, ini: "09/11", fim: "15/11", aceite: "14/11", maestro: "pausa" };
D.quadro = [
  { c: "Backlog da sprint", cards: [{ id: "PROG-016", t: "Cronograma na tela de publicação", d: "Zico" }] },
  { c: "Fazendo", cards: [{ id: "PROG-015", t: "Fila \"Espera você\" única", d: "Endrick" }, { id: "PROG-014", t: "Registro único de jobs", d: "Rodrygo" }] },
  { c: "Em teste", cards: [{ id: "PROG-013b", t: "SSE do painel de Clipes embutido", d: "Alisson" }] },
  { c: "Code review", cards: [] },
  { c: "Pronto para aceite", cards: [{ id: "PROG-013", t: "Painel unificado, versão inicial", d: "aguarda você", destaque: true }] },
  { c: "Feito", cards: [{ id: "PROG-012", t: "Aprovação por versão no Corte", d: "aceito 10/11" }] }
];
D.backlog = [{ id: "PROG-017", t: "Tela de cronograma do Corte", p: "média" }, { id: "PROG-018", t: "Lock de escrita entre servidores", p: "alta" }];

/* ---------- Ecossistema ---------- */
D.consumo = [
  { n: "Raphinha (opus)", v: 2.4 }, { n: "Olise", v: 1.7 }, { n: "Neymar", v: 0.9 }, { n: "Ronaldo (haiku)", v: 0.4 }, { n: "Vitinho", v: 0.38 }, { n: "Outros", v: 1.1 }
];
D.tetos = [{ n: "Mensagem comum do Ronaldo", v: "US$ 0,30" }, { n: "De Bruyne pelo Telegram", v: "US$ 3,00" }, { n: "Inteligência por dia", v: "US$ 1,10" }, { n: "Teste de agente", v: "US$ 1,00" }, { n: "Canal por vídeo (--allow-paid)", v: "US$ 0,00" }];
D.conexoes = [
  { n: "Claude Code (login)", e: "ok", d: "Conta logada. Sem login, nenhum agente roda." },
  { n: "Telegram (Ronaldo)", e: "ok", d: "Só o seu chat. Único canal fora de casa." },
  { n: "Google Agenda", e: "espera", d: "Autorização vence em 2 dias (modo Testando)." },
  { n: "Trello (Kanban Trabalho)", e: "ok", d: "Mão dupla a cada 10 min. O que você muda vale." },
  { n: "YouTube OAuth", e: "ok", d: "Escopo de leitura. Retenção e CTR dependem do yt-analytics (A4)." },
  { n: "Slack", e: "bloq", d: "NÃO CONECTADO, por decisão." }, { n: "E-mail", e: "bloq", d: "NÃO CONECTADO." }, { n: "Casa e IoT", e: "bloq", d: "NÃO CONECTADO, por decisão." }
];
D.limites = [
  ["Claude logado", "Os agentes rodam com o login do Claude Code nesta máquina. Sem login, nada executa."],
  ["PC ligado e acordado", "Telegram, avisos, agendador e servidores precisam do computador ligado e sem suspender."],
  ["Sem acesso de fora de casa", "O sistema só abre na rede local (modo --rede, HTTP, com senha). Fora de casa só o Telegram funciona."],
  ["Agente não conversa no meio da tarefa", "Cada job termina a rodada. Quando falta informação, vira uma decisão em \"Espera você\" e nova rodada."],
  ["Limites do plano", "Limite de 5 horas e semanal. O Codex só entra como reserva quando o Claude acaba."],
  ["Um render por vez", "No máximo 3 agentes juntos e 1 render ou narração por vez."],
  ["Windows", "Agendador, janelas e encerramento de processo dependem do Windows."],
  ["Conectores do claude.ai desligados nos jobs", "Taplio e ElevenLabs não estão disponíveis para os agentes; integrações são por script local."],
  ["Escrita sem lock entre servidores", "Corte, Clipes, Ronaldo e Telegram gravam em arquivos sem lock comum. O servidor único precisa ser o único a gravar."]
];
D.propostas = [{ id: "A6", t: "Enxugar o prompt do Raphinha", d: "Remover 3 trechos repetidos do CLAUDE.md", e: "Aguardando você" }, { id: "V2", t: "Casar agente por id completo na central", d: "Bug de nomes compostos (thiago-silva)", e: "Virou cartão em Programação" }];

D.yaml = "budget:\n  max_usd_per_video: 0\n  max_retries_per_step: 2\npublish:\n  privacy: private\ncompliance:\n  max_videos_per_day: 2\nvoz:\n  velocidade: 1.0\ncronograma:\n  hora: \"18:00\"\n  videos_por_dia: 1\n";
D.claudeSecoes = [
  { id: "formato", n: "Formato", inegociavel: false, t: "SHORTS APENAS (30 a 60 segundos, 1080x1920, 30 fps). Estilo visual: sketch é o padrão; cartões só se o pedido disser." },
  { id: "regras", n: "Regras do canal", inegociavel: true, t: "Cada vídeo precisa de ângulo próprio e pelo menos 1/3 de comentário original. Fatos só das notas (3+ fontes). Tom respeitoso com vítimas. Seguir TODAS as políticas do YouTube." },
  { id: "congelamento", n: "Congelamento", inegociavel: true, t: "Depois da aprovação do Vini, roteiro.txt é imutável. Depois do vídeo final, o pacote audiovisual fica congelado. Só o Guilherme autoriza nova versão." },
  { id: "autonomia", n: "Autonomia", inegociavel: false, t: "Pedir \"produza um vídeo sobre X\" autoriza todo o fluxo com recursos gratuitos e dentro do budget. Pare só por falta de informação indispensável, conflito editorial, gasto acima do orçamento ou publicação." }
];
D.saude = { servidores: [{ n: "Corte", p: 8765, e: "ok" }, { n: "Painel do Ronaldo", p: 8766, e: "ok" }, { n: "Painel de Clipes", p: 8767, e: "ok" }], agendador: [{ n: "ContextoExplica-Avisos", i: "1 min", e: "ok" }, { n: "ContextoExplica-Ronaldo", i: "5 min", e: "ok" }, { n: "ContextoExplica-Trello", i: "10 min", e: "ok" }, { n: "ContextoExplica-GoogleAgenda", i: "5 min", e: "ok" }, { n: "ContextoExplica-Sprint", i: "desligada", e: "pausa" }] };
