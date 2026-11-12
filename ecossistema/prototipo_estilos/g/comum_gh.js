/* Núcleo das versões G e H: os 5 estados (forma + cor), agentes derivados de dados.js,
   slots de assets nomeados e o modo "ver slots". Não desenha telas. Sem segredos. */
(function () {
  var GH = window.GH = {};
  var esc = B.esc;

  GH.q = function (k) { var m = location.search.match(new RegExp("[?&]" + k + "=([^&]*)")); return m ? decodeURIComponent(m[1]) : ""; };

  /* ---------- os 5 estados: cada um tem forma própria, além da cor ---------- */
  GH.ESTADOS = [
    { id: "ok", rot: "Deu certo", d: "Terminou e entregou" },
    { id: "erro", rot: "Deu erro", d: "Falhou e precisa de ajuda" },
    { id: "pendente", rot: "Pendente", d: "Espera uma decisão sua" },
    { id: "backlog", rot: "Backlog", d: "Na fila, sem tarefa agora" },
    { id: "rodando", rot: "Rodando", d: "Trabalhando neste momento" }
  ];
  var SVG = {
    ok: '<circle cx="10" cy="10" r="9" fill="currentColor"/><path d="m5.8 10.3 2.8 2.8 5.6-5.8" fill="none" stroke="var(--ico-fg,#fff)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
    erro: '<path d="M10 1.6 19 17.6H1z" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M10 7.4v5M10 14.6v.01" stroke="var(--ico-fg,#fff)" stroke-width="2.2" stroke-linecap="round"/>',
    pendente: '<path d="M10 .8 19.2 10 10 19.2.8 10z" fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M8.2 6.8v6.4M11.8 6.8v6.4" stroke="var(--ico-fg,#fff)" stroke-width="2" stroke-linecap="round"/>',
    backlog: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3.2 3.2"/>',
    rodando: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-opacity=".28" stroke-width="3"/><path class="spin" d="M10 2a8 8 0 0 1 8 8" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'
  };
  GH.rot = function (id) { return GH.ESTADOS.filter(function (e) { return e.id === id; })[0].rot; };
  GH.ico = function (id, s) { s = s || 18; return '<svg class="eico e-' + id + '" width="' + s + '" height="' + s + '" viewBox="0 0 20 20" aria-hidden="true">' + SVG[id] + "</svg>"; };
  GH.chip = function (id, extra) { return '<span class="est e-' + id + '">' + GH.ico(id, 16) + "<span>" + GH.rot(id) + (extra ? " " + extra : "") + "</span></span>"; };
  GH.mapa = function (e) { return { ok: "ok", erro: "erro", espera: "pendente", bloq: "backlog", fila: "backlog", rodando: "rodando", pendente: "pendente", backlog: "backlog" }[e] || "backlog"; };
  GH.barra = function (est, pct, rotulo) {
    return '<div class="pb e-' + est + '" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '" aria-label="' + esc(rotulo || GH.rot(est)) + '"><i style="width:' + pct + '%"></i></div>';
  };
  GH.legenda = function (cont, cls) {
    return '<ul class="legenda ' + (cls || "") + '" aria-label="Legenda dos estados">' + GH.ESTADOS.map(function (e) {
      return '<li class="e-' + e.id + '" title="' + esc(e.d) + '">' + GH.ico(e.id, 18) + "<span>" + e.rot + "</span>" + (cont ? "<b>" + (cont[e.id] || 0) + "</b>" : "") + "</li>";
    }).join("") + "</ul>";
  };

  /* ---------- agentes (nome, id e função vêm de dados.js; estados são exemplo) ---------- */
  GH.slug = function (nome) { return nome.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, ""); };
  GH.ini = function (nome) {
    var p = nome.split(/\s+/);
    return (p.length > 1 ? p[0][0] + p[p.length - 1][0] : nome.slice(0, 2)).toUpperCase();
  };
  var EXEMPLO = {
    "olise-diretor-arte": ["rodando", 55, "Cenas de \"a recessão de amizades\", cena 3 de 6"],
    "valverde-engenheiro-ia": ["rodando", 40, "Diagnóstico de consumo do Raphinha"],
    "alisson-qa": ["rodando", 72, "Bateria de testes do PROG-013b"],
    "salah-scout-fontes": ["erro", 30, "Erro 403 ao baixar a fonte (J3)"],
    "vini-auditor-conformidade": ["pendente", 62, "Auditoria de texto aponta 2 correções (C5)"],
    "neymar-roteirista": ["pendente", 100, "Roteiro v2 espera sua aprovação (C1)"],
    "raphinha-curador-componentes": ["pendente", 80, "3 componentes esperam validação (C2)"],
    "sidorf-thumbnail-estrategista": ["pendente", 100, "Prompt da thumbnail pronto (C10)"],
    "memphis-social-media": ["pendente", 90, "Subir como privado (C11)"],
    "rivaldo-avaliador-fonte": ["pendente", 100, "Triagem nota 38 (L1)"],
    "kaka-cacador-momentos": ["pendente", 100, "5 momentos sugeridos (L2)"],
    "zidane-editor-cortes": ["pendente", 100, "Texto do corte 02 (L3)"],
    "zico-po-programacao": ["pendente", 100, "Aceite do PROG-013 (P1)"],
    "lamine-yamal-linkedin": ["pendente", 100, "Rascunho de LinkedIn (A1)"],
    "casemiro-financeiro": ["pendente", 100, "Conta de internet vence 12/11 (A2)"],
    "ronaldo-assistente": ["ok", 100, "Resumo diário enviado às 08:30"],
    "modric-pesquisador-tema": ["ok", 100, "notas.md de \"jovens bebendo menos\""],
    "courtois-revisor-fatos": ["ok", 100, "Revisão do roteiro v2 sem problemas"],
    "mbappe-editor-metadados": ["ok", 100, "metadados.json de 3 vídeos"],
    "vitinho-consolidador": ["ok", 100, "Relatório semanal (09:19)"],
    "rodrygo-dev-back": ["ok", 100, "PROG-014 entregue ao teste"],
    "endrick-dev-front": ["ok", 100, "PROG-015 em andamento, pronto para teste"],
    "thiago-silva-tech-lead": ["ok", 100, "Review do PROG-013 aprovado"],
    "debruyne-orquestrador": ["ok", 100, "Disparou Olise e Mbappé em paralelo"],
    "marquinhos-devops-release": ["ok", 100, "Notas de release do PROG-012"]
  };
  GH.agentes = D.agentesBase.map(function (a) {
    var ex = EXEMPLO[a[0]], est = ex ? ex[0] : "backlog";
    return { id: a[0], nome: a[1], setor: a[2], modelo: a[3], kit: D.TOOLKIT[a[4]], desc: a[5], escreve: a[6], est: est, prog: ex ? ex[1] : 0, tarefa: ex ? ex[2] : "Sem tarefa agora. Entra quando o fluxo chamar.", slug: GH.slug(a[1]), ini: GH.ini(a[1]) };
  });
  GH.agente = function (id) { return GH.agentes.filter(function (a) { return a.id === id || a.slug === id; })[0]; };
  GH.contagem = function (lista) {
    var c = {}; (lista || GH.agentes).forEach(function (a) { c[a.est] = (c[a.est] || 0) + 1; }); return c;
  };
  GH.funcao = function (a) { return a.desc.split(/\. /)[0].replace(/\.$/, ""); };
  /* quem entrega cada decisão */
  GH.autor = { c5: "vini-auditor-conformidade", c1: "neymar-roteirista", c8: "vini-auditor-conformidade", c11: "memphis-social-media", c2: "raphinha-curador-componentes", c3: "olise-diretor-arte", c10: "sidorf-thumbnail-estrategista", c14: "memphis-social-media", l1: "rivaldo-avaliador-fonte", l3: "zidane-editor-cortes", l2: "kaka-cacador-momentos", p1: "zico-po-programacao", p2: "xavi-scrum-master", a1: "lamine-yamal-linkedin", a3: "ronaldo-assistente", a2: "casemiro-financeiro", a6: "valverde-engenheiro-ia", a4: "yuri-alberto-analista-metricas", a5: "vitinho-consolidador", a9: "ronaldo-assistente" };
  GH.autorDe = function (d) { return GH.agente(GH.autor[d.id] || "debruyne-orquestrador"); };
  GH.etapaAgente = { "Cenas (Olise)": "olise-diretor-arte", "Auditoria de texto": "vini-auditor-conformidade", "Aprovar cenas": "olise-diretor-arte", "Narração": "kane-narrador", "Thumbnail": "sidorf-thumbnail-estrategista", "Aprovar vídeo final": "vini-auditor-conformidade", "Pronto, na fila": "memphis-social-media" };

  /* ---------- slots de assets ---------- */
  GH.TIPOS = {
    rd: { size: "256", uso: "Avatar redondo (lista, conversa, estações)" },
    sq: { size: "512", uso: "Avatar quadrado (cartão do agente)" },
    rt: { size: "640x800", uso: "Avatar retangular 4:5 (ficha do agente)" },
    ic: { size: "128", uso: "Ícone de setor ou de menu" },
    vz: { size: "960x640", uso: "Ilustração de estado vazio" },
    hero: { size: "1600x700", uso: "Fundo ou hero de tela" },
    logo: { size: "256", uso: "Marca do produto" }
  };
  var SIL = '<svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMax slice" aria-hidden="true"><circle cx="50" cy="36" r="17"/><path d="M14 100c2-27 16-39 36-39s34 12 36 39z"/></svg>';
  var VAZIO = '<svg viewBox="0 0 240 160" aria-hidden="true"><rect x="40" y="52" width="160" height="86" rx="16"/><path d="M40 96h56a24 24 0 0 0 48 0h56" fill="none" stroke-width="5"/><circle cx="64" cy="28" r="7"/><circle cx="188" cy="36" r="5"/><path d="M120 12v22M109 23h22" stroke-width="5" stroke-linecap="round"/></svg>';
  /* o: {n: nome do slot, k: tipo, px: largura de tela, ini, s: setor, g: grupo, cls, ic} */
  GH.slot = function (o) {
    var T = GH.TIPOS[o.k], inner = "";
    if (o.k === "rd") inner = "<b>" + esc(o.ini || "?") + "</b>";
    else if (o.k === "sq") inner = SIL + "<b>" + esc(o.ini || "?") + "</b>";
    else if (o.k === "rt") inner = SIL + "<b>" + esc(o.ini || "") + "</b>";
    else if (o.k === "ic") inner = B.icon(o.ic || "ecossistema", 22);
    else if (o.k === "vz") inner = VAZIO;
    else if (o.k === "hero") inner = '<svg viewBox="0 0 400 160" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><circle cx="330" cy="40" r="90"/><circle cx="60" cy="150" r="70"/><circle cx="210" cy="110" r="36"/></svg>';
    else if (o.k === "logo") inner = "<b>CE</b>";
    var tam = o.size || T.size;
    return '<span class="slot sl-' + o.k + " " + (o.cls || "") + '" data-asset="' + esc(o.n) + '" data-size="' + tam + '" data-forma="' + o.k + '" data-grupo="' + esc(o.g || o.n) + '" data-uso="' + esc(o.uso || T.uso) + '"' + (o.s ? ' data-s="' + o.s + '"' : "") + ' title="' + esc(o.n + " (" + tam + ")") + '" style="--px:' + (o.px || 48) + 'px">' + inner + "</span>";
  };
  GH.av = function (a, k, px, cls) {
    var tipo = k || "rd";
    return GH.slot({ n: "avatar_" + a.slug + "_" + tipo, g: "avatar_{agente}_" + tipo, k: tipo, px: px, ini: a.ini, s: a.setor, cls: cls });
  };
  GH.icSetor = function (id, px) {
    var m = B.menu.filter(function (x) { return x.id === id; })[0];
    return GH.slot({ n: "icone_setor_" + id, k: "ic", px: px || 40, ic: m ? m.ic : "ecossistema", s: id });
  };

  /* ---------- modo "ver slots" e painel com a lista ---------- */
  var painel = null;
  function coletar() {
    var map = {}, ordem = [];
    document.querySelectorAll("#app .slot, .slot-fixo").forEach(function (el) {
      var g = el.dataset.grupo;
      if (!map[g]) { map[g] = { g: g, size: el.dataset.size, uso: el.dataset.uso, n: 0 }; ordem.push(g); }
      map[g].n++;
    });
    return ordem.map(function (g) { return map[g]; });
  }
  function tamLabel(s) { return /x/.test(s) ? s + " px" : s + " × " + s + " px"; }
  GH.slotsTexto = function () {
    return coletar().map(function (x) { return x.g + " | " + tamLabel(x.size) + " | " + x.uso + " | " + x.n + " nesta tela"; }).join("\n");
  };
  GH.slotsAtualizar = function () {
    if (!painel) return;
    var L = coletar(), tot = L.reduce(function (a, x) { return a + x.n; }, 0);
    painel.querySelector(".sp-corpo").innerHTML = '<p class="sp-res"><b>' + L.length + "</b> tipos de imagem, <b>" + tot + "</b> slots nesta tela.</p><ul>" + L.map(function (x) {
      return '<li tabindex="0" data-g="' + esc(x.g) + '"><code>' + esc(x.g) + "</code><span>" + tamLabel(x.size) + "</span><em>" + esc(x.uso) + "</em><b>" + x.n + "</b></li>";
    }).join("") + "</ul>";
    painel.querySelectorAll("li").forEach(function (li) {
      function on(v) { document.querySelectorAll(".slot").forEach(function (s) { s.classList.toggle("hl", v && s.dataset.grupo === li.dataset.g); }); }
      li.onmouseenter = li.onfocus = function () { on(true); }; li.onmouseleave = li.onblur = function () { on(false); };
    });
  };
  GH.slotsLigar = function (botoes) {
    painel = document.createElement("aside");
    painel.id = "slots-painel"; painel.className = "slots-painel"; painel.setAttribute("aria-label", "Lista de slots de assets");
    painel.innerHTML = '<header><strong>Slots de assets</strong><button type="button" data-cp>Copiar lista</button><button type="button" data-x aria-label="Fechar o modo slots">Fechar</button></header><div class="sp-corpo"></div>';
    document.body.appendChild(painel);
    painel.querySelector("[data-cp]").onclick = function (e) {
      try { navigator.clipboard.writeText(GH.slotsTexto()); } catch (x) {}
      e.target.textContent = "Copiado"; setTimeout(function () { e.target.textContent = "Copiar lista"; }, 1600);
    };
    painel.querySelector("[data-x]").onclick = function () { GH.slotsModo(false); };
    GH.slotsModo(GH.q("slots") === "1");
  };
  GH.slotsModo = function (v) {
    if (v === undefined) v = document.documentElement.dataset.slots !== "1";
    document.documentElement.dataset.slots = v ? "1" : "";
    document.querySelectorAll("[data-slots-btn]").forEach(function (b) { b.setAttribute("aria-pressed", v); });
    if (painel) { painel.hidden = !v; if (v) GH.slotsAtualizar(); }
    return v;
  };
  GH.tema = function (chave, padrao) {
    var t = B.tema(chave, padrao), q = GH.q("tema");
    if (q) document.documentElement.dataset.tema = q;
    return t;
  };
})();
