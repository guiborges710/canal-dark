/* Versão H (Profissional): ilha escura com números grandes, estações de metrô, Ctrl K e teclado.
   Feita para uso diário intenso. */
(function () {
  var app = document.getElementById("app");
  var S = { sel: null, filtro: "todas", motivos: false, feat: "olise-diretor-arte", fSetor: "todos", busca: "" };
  var esc = B.esc, CHAVE = "ce_h_tema";
  var ic = function (n, s) {
    if (n === "search") return '<svg class="ic" width="' + (s || 20) + '" height="' + (s || 20) + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>';
    return B.icon(n, s);
  };
  GH.tema(CHAVE, "claro");
  var kbd = function (k) { return '<kbd aria-hidden="true">' + k + "</kbd>"; };
  var ESTREITO = 900;

  /* em que estação do fluxo cada decisão está parada (dados de exemplo) */
  var DEC_NO = { c5: ["canal", "vini_t"], c1: ["canal", "g_roteiro"], c2: ["canal", "g_comp"], c3: ["canal", "g_cenas"], c8: ["canal", "g_video"], c10: ["canal", "sidorf"], c11: ["canal", "g_pub"],
    l1: ["clipes", "g_tri"], l2: ["clipes", "g_rev"], l3: ["clipes", "g_txt"], p1: ["programacao", "aceite"], a6: ["ecossistema", "ap"] };

  function href(id) { return id === "ecossistema" ? "#/ecossistema/agentes" : "#/" + id; }
  function ir(h) { if (location.hash === h) render(); else location.hash = h; }
  function filtrada() { var p = B.pendentes(); return S.filtro === "todas" ? p : p.filter(function (d) { return d.setor === S.filtro; }); }
  function atual() {
    var l = filtrada();
    if (!l.some(function (d) { return d.id === S.sel; })) S.sel = l.length ? l[0].id : null;
    return l.filter(function (d) { return d.id === S.sel; })[0] || null;
  }
  function norm(s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function agVisiveis() {
    return GH.agentes.filter(function (a) {
      return (S.fSetor === "todos" || a.setor === S.fSetor) && (!S.busca || norm(a.nome + " " + a.id + " " + a.desc + " " + B.setor(a.setor).nome).indexOf(norm(S.busca)) >= 0);
    });
  }

  /* ---------- ilha: marca, busca, abas, números e legenda ---------- */
  function ilha() {
    var r = B.rota(), P = B.pendentes(), n = P.length, urg = P.filter(function (d) { return d.urgente; }).length, c = GH.contagem(), k = B.canalKpis();
    var rod = GH.agentes.filter(function (a) { return a.est === "rodando"; }), err = GH.agentes.filter(function (a) { return a.est === "erro"; });
    var escuro = document.documentElement.dataset.tema === "escuro";
    return '<header class="ilha"><div class="i-in"><div class="i-top"><div class="marca">' + GH.slot({ n: "logo_contexto_explica", k: "logo", px: 34 }) + "<span>Ecossistema do Guilherme</span></div>" +
      '<button class="busca" type="button" id="abrir-paleta" aria-label="Buscar ou comandar (Ctrl K)">' + ic("search", 18) + "<span>Buscar agente, decisão ou tela</span>" + kbd("Ctrl K") + "</button>" +
      '<div class="i-ferr"><button class="bt-i" type="button" data-slots-btn aria-pressed="' + (document.documentElement.dataset.slots === "1") + '" title="Atalho: S">Ver slots<span class="so-l"> de assets</span></button>' +
      '<button class="bt-i ic1" type="button" id="atalhos" aria-label="Atalhos de teclado" title="Atalhos (?)">?</button>' +
      '<button class="bt-i ic1" type="button" id="tema" aria-label="Tema ' + (escuro ? "claro" : "escuro") + '" title="Tema (T)">' + ic(escuro ? "sun" : "moon", 20) + "</button></div></div>" +
      '<nav class="i-nav" aria-label="Grupos">' + B.menu.map(function (m, i) {
        return '<a class="aba" href="' + href(m.id) + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 18) + "<span>" + esc(m.nome) + "</span>" + (m.id === "espera" && n ? '<b class="bdg">' + n + "</b>" : "") + kbd(i + 1) + "</a>";
      }).join("") + "</nav>" +
      '<div class="i-nums"><a class="nm" href="#/espera">' + GH.ico("pendente", 18) + '<span class="nr">Esperam você</span><span class="nn">' + n + '</span><span class="ns">' + urg + " urgentes</span></a>" +
      '<a class="nm" href="#/ecossistema/agentes">' + GH.ico("rodando", 18) + '<span class="nr">Rodando agora</span><span class="nn">' + rod.length + '</span><span class="ns">' + rod.map(function (a) { return esc(a.nome); }).join(", ") + '</span><span class="mini">' + rod.map(function (a) { return GH.barra("rodando", a.prog, a.nome + " " + a.prog + "%"); }).join("") + "</span></a>" +
      '<a class="nm" href="#/ecossistema/agentes">' + GH.ico("erro", 18) + '<span class="nr">Com erro</span><span class="nn">' + err.length + '</span><span class="ns">' + err.map(function (a) { return esc(a.nome) + ": " + esc(a.tarefa); }).join(" | ") + "</span></a>" +
      '<a class="nm" href="#/canal"><span class="nr">Custo hoje</span><span class="nn">' + B.usd(k.custo).replace("US$ ", "") + '<small>US$</small></span><span class="ns">teto dos jobs: ' + B.usd(k.teto) + '</span><span class="mini"><span class="meter" role="img" aria-label="Custo de ' + B.usd(k.custo) + " de " + B.usd(k.teto) + '"><i style="width:' + Math.round(k.custo / k.teto * 100) + '%"></i></span></span></a></div>' +
      '<div class="i-leg"><span class="i-lt">Agentes agora</span>' + GH.legenda(c, "leg-h") + "</div></div></header>";
  }

  /* ---------- estações de metrô ---------- */
  function estacao(n, atual) {
    var a = GH.agentes.filter(function (x) { return x.nome === n.a; })[0], e = n.est;
    return '<li class="est-n e-' + e + (atual ? " aqui" : "") + '"' + (atual ? ' aria-current="step"' : "") + ">" + '<span class="pt">' + GH.ico(e, 22) + "</span>" +
      '<span class="lb">' + esc(n.r) + "</span>" + (a ? '<span class="ag-m">' + GH.av(a, "rd", 22) + esc(a.nome) + "</span>" : '<span class="ag-m">' + (n.t === "gate" ? ic("user", 16) + "você" : esc(n.a)) + "</span>") + "</li>";
  }
  function metroDecisao(d) {
    var m = DEC_NO[d.id]; if (!m) return '<p class="avulsa">Ação avulsa: não está parada em nenhum fluxo de setor.</p>';
    var nos = D.fluxos[m[0]].nos, k = nos.map(function (n) { return n.id; }).indexOf(m[1]);
    var L = nos.map(function (n, i) { return { r: n.r, a: n.a, t: n.t, est: i < k ? "ok" : i === k ? (d.id === "c5" ? "erro" : "pendente") : "backlog" }; });
    return '<div class="metro" aria-label="Fluxo: ' + esc(D.fluxos[m[0]].nome) + '"><div class="mt-cab">' + esc(D.fluxos[m[0]].nome) + "<span>estação " + (k + 1) + " de " + nos.length + '</span></div><ol class="linha-m" data-aqui="' + k + '">' + L.map(function (n, i) { return estacao(n, i === k); }).join("") + "</ol></div>";
  }

  /* ---------- Espera você ---------- */
  function detalhe(d, folha) {
    var a = GH.autorDe(d), pi = B.principal(d), prim = d.acoes[pi], resto = "";
    d.acoes.forEach(function (x, i) { if (i !== pi) resto += '<button class="bt ' + (x.risco ? "risco" : "") + '" type="button" data-ac="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + esc(x.r) + "</button>"; });
    return (folha ? '<button class="bt fechar" type="button" data-fechar>Fechar</button>' : "") + metroDecisao(d) + '<div class="d-cab"><div class="d-quem">' + GH.av(a, "rd", 56) + "<div><strong>" + esc(a.nome) + "</strong><span>" + esc(GH.funcao(a)) + '</span></div></div><div class="d-tags"><span class="cod">' + d.cod + '</span><span class="tag" data-s="' + d.setor + '">' + esc(B.setor(d.setor).nome) + "</span>" + (d.urgente ? '<span class="tag urg">Urgente</span>' : "") + GH.chip("pendente") + "</div></div>" +
      "<h2>" + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>" + (d.trava ? '<div class="trava">' + ic("lock", 18) + "<span>" + esc(d.trava) + "</span></div>" : "") + '<div class="det">' + d.det + "</div>" +
      (d.edit ? '<label class="edit"><span>' + esc(d.edit.campo) + '</span><textarea rows="2" placeholder="' + esc(d.edit.dica) + '"></textarea></label>' : "") +
      '<div class="mots' + (S.motivos ? " on" : "") + '"><span>O que não está certo?</span>' + d.recusa.map(function (m) { return '<button class="mot" type="button" data-mot="' + esc(m) + '">' + esc(m) + "</button>"; }).join("") + "</div>" +
      '<div class="barra-ac"><div class="ba-esq">' + resto + (d.recusa.length ? '<button class="bt" type="button" data-rec aria-expanded="' + S.motivos + '">Pedir ajuste ' + kbd("R") + "</button>" : "") + "</div>" +
      (prim ? '<button class="bt prim ' + (prim.risco ? "risco" : "ok") + '" type="button" data-ac="' + pi + '"' + (prim.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (prim.risco ? "" : ic("check", 22)) + esc(prim.r) + " " + kbd("A") + "</button>" : "") + "</div>";
  }
  function ligarDet(raiz, d, depois) {
    raiz.querySelectorAll("[data-ac]").forEach(function (b) { b.onclick = function () { B.agir(b, d, +b.dataset.ac, depois); }; });
    raiz.querySelectorAll("[data-mot]").forEach(function (b) { b.onclick = function () { S.motivos = false; B.devolver(d, b.dataset.mot, depois); }; });
    var r = raiz.querySelector("[data-rec]"); if (r) r.onclick = function () { S.motivos = !S.motivos; raiz.querySelector(".mots").classList.toggle("on", S.motivos); r.setAttribute("aria-expanded", S.motivos); };
  }
  function espera() {
    var P = B.pendentes(), L = filtrada(), d = atual();
    var ids = D.setores.map(function (s) { return s.id; }).filter(function (id) { return P.some(function (x) { return x.setor === id; }); });
    var chips = ["todas"].concat(ids).map(function (id) {
      var n = id === "todas" ? P.length : P.filter(function (x) { return x.setor === id; }).length;
      return '<button class="cf" type="button" data-fil="' + id + '" aria-pressed="' + (S.filtro === id) + '">' + (id === "todas" ? "Todas" : esc(B.setor(id).nome)) + " <b>" + n + "</b></button>";
    }).join("");
    var rows = L.map(function (x) {
      var a = GH.autorDe(x);
      return '<li><button class="lin q" type="button" data-q="' + x.id + '"' + (x.id === S.sel ? ' aria-current="true"' : "") + ">" + GH.av(a, "rd", 40) + '<span class="qt"><span class="qc"><b>' + x.cod + "</b> " + esc(B.setor(x.setor).nome) + (x.urgente ? ' <i class="urg">Urgente</i>' : "") + '</span><span class="qn">' + esc(x.titulo) + "</span></span></button></li>";
    }).join("");
    var bl = B.bloqueadas.map(function (x) { return '<div class="bl">' + GH.ico("backlog", 18) + "<span><b>" + x.cod + "</b> " + esc(x.titulo) + "</span></div>"; }).join("");
    var vazio = '<div class="vazio">' + GH.slot({ n: "vazio_espera", k: "vz", cls: "vz-h" }) + "<h2>Fila zerada</h2><p>Os agentes seguem sozinhos. Você volta quando algum precisar de decisão.</p></div>";
    return '<div class="pag-cab"><h1 class="pag">Espera você</h1><p class="sub">Uma decisão sua destrava um agente. ' + kbd("J") + " " + kbd("K") + " navegam, " + kbd("A") + " aprova.</p></div>" +
      '<div class="duo"><section class="col-l" aria-label="Fila"><div class="chips-f" role="group" aria-label="Filtrar por setor">' + chips + '</div><ul class="lista" id="lista">' + rows + "</ul>" + (bl ? '<div class="bls"><h2>Esperam outra coisa</h2>' + bl + "</div>" : "") + "</section>" +
      '<section class="col-r" id="foco" aria-label="Decisão selecionada">' + (d ? (B.estreito(ESTREITO) ? '<p class="mudo toque">Toque em uma decisão para abrir.</p>' : detalhe(d)) : vazio) + "</section></div>";
  }

  /* ---------- Canal ---------- */
  function canal() {
    var k = B.canalKpis(), nos = k.nos;
    var linhas = B.fases.map(function (f, fi) {
      var ls = f.ids.map(function (id) { var n = nos.filter(function (x) { return x.id === id; })[0]; var e = GH.mapa(n.est); return { r: n.r, a: n.a, t: n.t, est: e }; });
      var ok = ls.filter(function (n) { return n.est === "ok"; }).length;
      return '<div class="linha-b l' + fi + '"><div class="lh"><b>' + esc(f.nome) + "</b><span>" + ok + " de " + ls.length + '</span></div><ol class="linha-m">' + ls.map(function (n) { return estacao(n, n.est === "rodando"); }).join("") + "</ol></div>";
    }).join("");
    var projs = D.projetos.map(function (p) {
      var a = GH.agente(GH.etapaAgente[p.etapa] || "debruyne-orquestrador"), e = GH.mapa(p.est);
      return '<li class="pr">' + GH.av(a, "rd", 36) + '<span class="pr-t"><b>' + esc(B.nomeProj(p.slug)) + "</b><span>" + esc(p.tipo) + " · " + esc(p.etapa) + " · " + p.ver + '</span></span><span class="pr-e">' + GH.chip(e) + '</span><span class="pr-b">' + GH.barra(e, p.prog, B.nomeProj(p.slug)) + "<em>" + p.prog + "%</em></span></li>";
    }).join("");
    var rings = D.metricas.map(function (m) { return '<li class="rg">' + B.ring(m.ret, 76, 9, "Retenção de " + m.v + ": " + m.ret + "%") + '<span class="rg-n">' + m.ret + '%</span><span class="rg-t">' + esc(m.v) + "<em>" + B.n(m.vis) + " views</em></span></li>"; }).join("");
    return '<div class="pag-cab"><h1 class="pag">Canal</h1><p class="sub">Shorts do Contexto Explica, do tema ao upload privado.</p></div>' +
      '<section class="cartao" aria-label="Esteira do Short"><h2>Esteira de um Short<span>' + k.feitos + " de " + nos.length + " estações concluídas</span></h2><div class=\"metro-b\">" + linhas + "</div></section>" +
      '<div class="duo2"><section class="cartao"><h2>Em produção<span>' + k.ativos + " de " + k.total + '</span></h2><ul class="prs">' + projs + "</ul></section>" +
      '<div class="pilha"><section class="cartao"><h2>Retenção por vídeo<span>média ' + k.ret + '%</span></h2><ul class="rgs">' + rings + '</ul></section><section class="cartao"><h2>Visualizações em 14 dias<span>' + (k.delta >= 0 ? "+" : "") + k.delta + "% na semana</span></h2><div class=\"vv\"><b>" + B.n(k.vis) + "</b>" + B.barsV(k.serie, 360, 80, "Visualizações por dia, últimos 14 dias") + "</div></section></div></div>";
  }

  /* ---------- Ecossistema > Agentes ---------- */
  function agDet(a, folha) {
    return (folha ? '<button class="bt fechar" type="button" data-fechar>Fechar</button>' : "") + '<div class="ad-av">' + GH.av(a, "rt", 168) + '<div class="ad-f"><span>Formatos do avatar</span><div>' + GH.av(a, "rd", 56) + GH.av(a, "sq", 72) + "</div></div></div>" +
      '<div class="ad-t"><span class="tag" data-s="' + a.setor + '">' + esc(B.setor(a.setor).nome) + "</span><span class=\"tag\">" + esc(a.modelo) + "</span></div><h2>" + esc(a.nome) + '</h2><p class="ctx">' + esc(a.desc) + '</p><div class="ad-st">' + GH.chip(a.est) + "<span>" + esc(a.tarefa) + "</span></div>" + GH.barra(a.est, a.prog, a.nome + ": " + GH.rot(a.est)) + "<dl><dt>Escreve em</dt><dd>" + esc(a.escreve) + "</dd><dt>Ferramentas</dt><dd>" + a.kit.map(function (x) { return '<span class="chip">' + esc(x) + "</span>"; }).join("") + "</dd><dt>id</dt><dd><code>" + esc(a.id) + "</code></dd></dl>";
  }
  function agentes() {
    var vis = agVisiveis(), todos = GH.agentes;
    if (!vis.some(function (a) { return a.id === S.feat; }) && vis.length) S.feat = vis[0].id;
    var f = GH.agente(S.feat);
    var setores = ["todos"].concat(D.setores.map(function (s) { return s.id; }));
    var chips = setores.map(function (id) { var n = id === "todos" ? todos.length : todos.filter(function (a) { return a.setor === id; }).length; return '<button class="cf" type="button" data-fs="' + id + '" aria-pressed="' + (S.fSetor === id) + '">' + (id === "todos" ? "Todos" : esc(B.setor(id).nome)) + " <b>" + n + "</b></button>"; }).join("");
    var rows = vis.map(function (a) {
      return '<li><button class="lin ag" type="button" data-ag="' + a.id + '" data-s="' + a.setor + '"' + (a.id === S.feat ? ' aria-current="true"' : "") + ">" + GH.av(a, "rd", 40) + '<span class="ln"><b>' + esc(a.nome) + '</b><span class="fn">' + esc(GH.funcao(a)) + '</span></span><span class="ls">' + esc(B.setor(a.setor).nome) + '</span><span class="lm">' + esc(a.modelo) + '</span><span class="le">' + GH.chip(a.est) + GH.barra(a.est, a.prog, a.nome + ": " + GH.rot(a.est)) + "</span></button></li>";
    }).join("");
    return '<div class="pag-cab"><h1 class="pag">Agentes</h1><p class="sub">' + todos.length + " agentes em " + D.setores.length + " setores. Estados de exemplo.<span class=\"dica\"> " + kbd("/") + " busca.</span></p></div>" +
      '<div class="ferr-l"><div class="chips-f" role="group" aria-label="Filtrar por setor">' + chips + '</div><label class="campo"><span class="so">Filtrar agentes</span>' + ic("search", 18) + '<input id="busca-ag" type="search" placeholder="Filtrar por nome ou função" value="' + esc(S.busca) + '" autocomplete="off"></label></div>' +
      '<div class="duo ag-duo"><section class="col-l" aria-label="Lista de agentes">' + (vis.length ? '<ul class="lista">' + rows + "</ul>" : '<div class="vazio">' + GH.slot({ n: "vazio_agentes", k: "vz", cls: "vz-h" }) + "<h2>Nenhum agente encontrado</h2><p>Limpe o filtro para ver todos.</p></div>") + "</section>" +
      '<aside class="col-r sticky" id="foco" aria-label="Ficha do agente">' + (f && !B.estreito(ESTREITO) ? agDet(f) : '<p class="mudo toque">Toque em um agente para abrir a ficha.</p>') + "</aside></div>";
  }
  function setorPag(id) {
    var s = B.setor(id); S.fSetor = id;
    return '<section class="setor-h" data-s="' + id + '">' + GH.icSetor(id, 56) + "<div><h1 class=\"pag\">" + esc(s.nome) + "</h1><p class=\"sub\">" + esc(s.desc) + " Chefe: " + esc(s.chefe) + ". Esta tela completa vem depois da escolha.</p></div></section>" + agentes().replace(/<div class="pag-cab">.*?<\/div>/, "");
  }
  function tela() {
    var r = B.rota();
    if (r === "espera") return espera();
    if (r === "canal") return canal();
    if (r === "ecossistema") { return agentes(); }
    return setorPag(r);
  }

  /* ---------- paleta Ctrl K e atalhos ---------- */
  var pal = document.createElement("dialog"); pal.className = "paleta"; pal.setAttribute("aria-label", "Buscar ou comandar");
  pal.innerHTML = '<div class="p-in"><input id="p-q" type="text" role="combobox" aria-expanded="true" aria-controls="p-l" aria-autocomplete="list" placeholder="Buscar agente, decisão ou tela" autocomplete="off"><ul id="p-l" role="listbox"></ul><p class="p-d">' + kbd("↑") + kbd("↓") + " escolhe " + kbd("Enter") + " abre " + kbd("Esc") + " fecha</p></div>";
  document.body.appendChild(pal);
  var atal = document.createElement("dialog"); atal.className = "paleta atal"; atal.setAttribute("aria-label", "Atalhos de teclado");
  atal.innerHTML = '<div class="p-in"><h2>Atalhos de teclado</h2><dl>' + [["Ctrl K  ou  /", "Buscar agente, decisão ou tela"], ["1 a 8", "Ir para o grupo"], ["J  e  K", "Próxima e anterior, na fila ou na lista"], ["A", "Aprovar (ação principal da decisão)"], ["R", "Pedir ajuste"], ["S", "Ver slots de assets"], ["T", "Trocar o tema"], ["?", "Mostrar esta lista"]].map(function (x) { return "<div><dt>" + x[0].replace(/(\S+)/g, function (m) { return /^(e|ou|a)$/.test(m) ? "<i>" + m + "</i>" : "<kbd>" + m + "</kbd>"; }) + "</dt><dd>" + x[1] + "</dd></div>"; }).join("") + '</dl><button class="bt" type="button" data-x>Fechar</button></div>';
  document.body.appendChild(atal);
  atal.querySelector("[data-x]").onclick = function () { atal.close(); };
  [pal, atal].forEach(function (dlg) { dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); }); });
  var palSel = 0, palItens = [];
  function palConstruir(q) {
    var nq = norm(q), it = [];
    B.menu.forEach(function (m, i) { it.push({ g: "Ir para", r: m.nome + (m.id === "ecossistema" ? " > Agentes" : ""), s: "tecla " + (i + 1), ic: m.ic, f: function () { ir(href(m.id)); } }); });
    GH.agentes.forEach(function (a) { it.push({ g: "Agentes", r: a.nome, s: B.setor(a.setor).nome + " · " + GH.rot(a.est), av: a, k: a.id + " " + a.desc, f: function () { S.feat = a.id; S.fSetor = "todos"; S.busca = ""; ir("#/ecossistema/agentes"); } }); });
    B.pendentes().forEach(function (d) { it.push({ g: "Decisões", r: d.cod + "  " + d.titulo, s: B.setor(d.setor).nome, ic: "inbox", f: function () { S.sel = d.id; S.filtro = "todas"; ir("#/espera"); } }); });
    palItens = it.filter(function (x) { return !nq || norm(x.r + " " + (x.k || "") + " " + x.s).indexOf(nq) >= 0; }).slice(0, nq ? 12 : 9);
    palSel = 0; palDesenhar();
  }
  function palDesenhar() {
    var ul = pal.querySelector("#p-l"), ult = "";
    ul.innerHTML = palItens.length ? palItens.map(function (x, i) {
      var cab = x.g !== ult ? '<li class="p-g" role="presentation">' + x.g + "</li>" : ""; ult = x.g;
      return cab + '<li role="option" id="p-o' + i + '" data-i="' + i + '" aria-selected="' + (i === palSel) + '">' + (x.av ? GH.av(x.av, "rd", 28) : ic(x.ic, 20)) + "<span>" + esc(x.r) + "</span><em>" + esc(x.s) + "</em></li>";
    }).join("") : '<li class="p-g" role="presentation">Nada encontrado. Tente o nome de um agente ou de uma tela.</li>';
    ul.querySelectorAll("[data-i]").forEach(function (li) { li.onclick = function () { palSel = +li.dataset.i; palAbrir(); }; });
    var q = pal.querySelector("#p-q"), o = ul.querySelector("#p-o" + palSel);
    q.setAttribute("aria-activedescendant", o ? o.id : ""); if (o) o.scrollIntoView({ block: "nearest" });
  }
  function palAbrir() { var x = palItens[palSel]; if (!x) return; pal.close(); x.f(); }
  pal.querySelector("#p-q").addEventListener("input", function (e) { palConstruir(e.target.value); });
  pal.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); palSel = Math.min(palItens.length - 1, palSel + 1); palDesenhar(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); palSel = Math.max(0, palSel - 1); palDesenhar(); }
    else if (e.key === "Enter") { e.preventDefault(); palAbrir(); }
  });
  function abrirPaleta() { pal.querySelector("#p-q").value = ""; palConstruir(""); if (!pal.open) pal.showModal(); pal.querySelector("#p-q").focus(); }

  /* ---------- atalhos globais ---------- */
  function mover(delta) {
    var r = B.rota();
    if (r === "espera") { var L = filtrada(), i = L.map(function (x) { return x.id; }).indexOf(S.sel); if (!L.length) return; S.sel = L[Math.max(0, Math.min(L.length - 1, i + delta))].id; S.motivos = false; render(true); }
    else if (r !== "canal") { var V = agVisiveis(), j = V.map(function (x) { return x.id; }).indexOf(S.feat); if (!V.length) return; S.feat = V[Math.max(0, Math.min(V.length - 1, j + delta))].id; render(true); }
  }
  document.addEventListener("keydown", function (e) {
    var alvo = e.target, digitando = /^(INPUT|TEXTAREA|SELECT)$/.test(alvo.tagName) || alvo.isContentEditable;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); abrirPaleta(); return; }
    if (digitando || e.ctrlKey || e.metaKey || e.altKey || pal.open || atal.open || document.querySelector("dialog.sheet[open]")) return;
    var k = e.key.toLowerCase();
    if (k === "/") { e.preventDefault(); if (B.rota() === "ecossistema") { var b = document.getElementById("busca-ag"); if (b) { b.focus(); return; } } abrirPaleta(); }
    else if (k === "?") atal.showModal();
    else if (/^[1-8]$/.test(k)) ir(href(B.menu[+k - 1].id));
    else if (k === "j") mover(1); else if (k === "k") mover(-1);
    else if (k === "t") document.getElementById("tema").click();
    else if (k === "s") GH.slotsModo();
    else if (k === "a" && B.rota() === "espera") { var p = document.querySelector(".barra-ac .prim"); if (p) p.click(); }
    else if (k === "r" && B.rota() === "espera") { var r = document.querySelector("[data-rec]"); if (r) r.click(); }
  });

  /* ---------- montagem ---------- */
  function abrirFolha(html, ligar) {
    var f = B.sheet(); f.innerHTML = html; ligar(f); f.showModal(); f.querySelectorAll(".linha-m[data-aqui]").forEach(function (ol) { var e = ol.querySelector(".aqui"); if (e) ol.scrollLeft = e.offsetLeft - ol.clientWidth / 2 + e.offsetWidth / 2; });
    var x = f.querySelector("[data-fechar]"); if (x) x.onclick = function () { f.close(); };
  }
  function render(manter) {
    var ls = document.getElementById("lista"), st = ls ? ls.scrollTop : 0, ant = document.activeElement && document.activeElement.dataset && (document.activeElement.dataset.q || document.activeElement.dataset.ag);
    app.innerHTML = ilha() + '<main id="principal" class="papel" tabindex="-1">' + tela() + "</main>";
    var nome = (B.menu.filter(function (m) { return m.id === B.rota(); })[0] || {}).nome;
    document.title = "H (Profissional): " + nome;
    document.getElementById("tema").onclick = function () {
      var n = document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro";
      document.documentElement.dataset.tema = n; try { localStorage.setItem(CHAVE, n); } catch (e) {} render(); document.getElementById("tema").focus();
    };
    document.getElementById("abrir-paleta").onclick = abrirPaleta;
    document.getElementById("atalhos").onclick = function () { atal.showModal(); };
    document.querySelector("[data-slots-btn]").onclick = function () { GH.slotsModo(); };
    var r = B.rota(), novo = document.getElementById("lista");
    if (novo) novo.scrollTop = st;
    if (r === "espera") {
      var d = atual(), raiz = document.getElementById("foco");
      if (d && !B.estreito(ESTREITO)) ligarDet(raiz, d, function () { S.motivos = false; render(); });
      app.querySelectorAll("[data-fil]").forEach(function (b) { b.onclick = function () { S.filtro = b.dataset.fil; render(); var x = app.querySelector('[data-fil="' + S.filtro + '"]'); if (x) x.focus(); }; });
      app.querySelectorAll("[data-q]").forEach(function (b) {
        b.onclick = function () {
          S.sel = b.dataset.q; S.motivos = false;
          if (B.estreito(ESTREITO)) { var dd = atual(); render(); abrirFolha(detalhe(dd, true), function (f) { ligarDet(f, dd, function () { f.close(); S.motivos = false; render(); }); }); }
          else { render(); var x = app.querySelector('[data-q="' + S.sel + '"]'); if (x) x.focus({ preventScroll: true }); }
        };
      });
    } else if (r !== "canal") {
      app.querySelectorAll("[data-fs]").forEach(function (b) { b.onclick = function () { S.fSetor = b.dataset.fs; render(); var x = app.querySelector('[data-fs="' + S.fSetor + '"]'); if (x) x.focus(); }; });
      var bi = document.getElementById("busca-ag");
      if (bi) bi.oninput = function () { S.busca = bi.value; var pos = bi.selectionStart; render(); var n = document.getElementById("busca-ag"); n.focus(); n.setSelectionRange(pos, pos); };
      app.querySelectorAll("[data-ag]").forEach(function (b) {
        b.onclick = function () {
          S.feat = b.dataset.ag;
          if (B.estreito(ESTREITO)) { var a = GH.agente(S.feat); render(); abrirFolha(agDet(a, true), function () {}); }
          else { render(); var x = app.querySelector('[data-ag="' + S.feat + '"]'); if (x) x.focus({ preventScroll: true }); }
        };
      });
    }
    /* metro: leva a estação atual para o meio */
    app.querySelectorAll(".linha-m[data-aqui]").forEach(function (ol) { var e = ol.querySelector(".aqui"); if (e) ol.scrollLeft = e.offsetLeft - ol.clientWidth / 2 + e.offsetWidth / 2; });
    if (manter) {
      var sel = app.querySelector('[aria-current="true"][data-q], [aria-current="true"][data-ag]');
      if (sel) { sel.focus({ preventScroll: true }); sel.scrollIntoView({ block: "nearest" }); }
    }
    GH.slotsAtualizar();
  }
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); });
  render();
  GH.slotsLigar();
  if (GH.q("paleta") === "1") abrirPaleta();
  if (GH.q("atalhos") === "1") atal.showModal();
})();
