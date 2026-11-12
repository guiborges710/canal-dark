/* Versão G (Vitrine): bento vibrante + "mostrar o trabalho". Feita para o print que vende. */
(function () {
  var app = document.getElementById("app");
  var S = { sel: null, filtro: "todas", motivos: false, feat: "olise-diretor-arte", fSetor: "todos" };
  var esc = B.esc, ic = B.icon;
  var CHAVE = "ce_g_tema";
  GH.tema(CHAVE, "claro");

  function filtrada() { var p = B.pendentes(); return S.filtro === "todas" ? p : p.filter(function (d) { return d.setor === S.filtro; }); }
  function atual() {
    var l = filtrada();
    if (!l.some(function (d) { return d.id === S.sel; })) S.sel = l.length ? l[0].id : null;
    return l.filter(function (d) { return d.id === S.sel; })[0] || null;
  }
  function href(id) { return id === "ecossistema" ? "#/ecossistema/agentes" : "#/" + id; }

  function casca(corpo) {
    var r = B.rota(), n = B.pendentes().length, esc_ = document.documentElement.dataset.tema === "escuro";
    return '<header class="cab"><div class="marca">' + GH.slot({ n: "logo_contexto_explica", k: "logo", px: 44 }) + "<span>Contexto Explica</span></div>" +
      '<div class="ferr"><button class="bt-f" type="button" data-slots-btn aria-pressed="' + (document.documentElement.dataset.slots === "1") + '">Ver slots de assets</button>' +
      '<button class="bt-f ic-only" type="button" id="tema" aria-label="Tema ' + (esc_ ? "claro" : "escuro") + '" title="Tema ' + (esc_ ? "claro" : "escuro") + '">' + ic(esc_ ? "sun" : "moon", 22) + "</button></div></header>" +
      '<nav class="nav" aria-label="Grupos">' + B.menu.map(function (m) {
        return '<a class="nv" href="' + href(m.id) + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 22) + "<span>" + esc(m.nome) + "</span>" + (m.id === "espera" && n ? '<b class="bdg" aria-label="' + n + ' pendentes">' + n + "</b>" : "") + "</a>";
      }).join("") + '</nav><main id="principal" tabindex="-1">' + corpo + "</main>";
  }

  function nome2(a) { return '<b>' + esc(a.nome) + "</b>"; }

  /* ---------- peças reutilizáveis ---------- */
  function rodandoTile() {
    var R = GH.agentes.filter(function (a) { return a.est === "rodando"; });
    return '<section class="t t-ink a-rod" aria-label="Trabalhando agora"><h2 class="rot">Trabalhando agora<span class="pill">' + R.length + " agentes</span></h2><ul class=\"rod\">" + R.map(function (a) {
      return "<li>" + GH.av(a, "rd", 44) + '<div><div class="l1">' + nome2(a) + "<span>" + a.prog + "%</span></div><div class=\"l2\">" + esc(a.tarefa) + "</div>" + GH.barra("rodando", a.prog, a.nome + ": " + a.tarefa) + "</div></li>";
    }).join("") + "</ul></section>";
  }
  function pagina(titulo, sub, cont) {
    return '<div class="pag-cab"><h1 class="pag">' + titulo + "</h1>" + (sub ? '<p class="sub">' + sub + "</p>" : "") + "</div>" + GH.legenda(cont, "leg-g");
  }

  /* ---------- Espera você ---------- */
  function card(d) {
    var a = GH.autorDe(d), pi = B.principal(d), eAut = d.urgente ? "pendente" : "pendente";
    var bts = d.acoes.map(function (x, i) {
      var cls = i === pi ? (x.risco ? "risco" : "ok") : (x.risco ? "risco" : "");
      return '<button class="bt ' + (i === pi ? "grande " : "") + cls + '" type="button" data-ac="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (i === pi && !x.risco ? ic("check", 28) : "") + esc(x.r) + "</button>";
    }).join("");
    var principal = d.acoes.length ? bts.split("</button>")[pi] + "</button>" : "";
    var resto = d.acoes.map(function (x, i) { return i === pi ? "" : bts.split("</button>")[i] + "</button>"; }).join("");
    return '<div class="cd-top" data-s="' + d.setor + '"><span class="cod">' + d.cod + '</span><span class="pill">' + esc(B.setor(d.setor).nome) + "</span>" + (d.urgente ? '<span class="pill urg">Urgente</span>' : "") + "<span class=\"cd-est\">" + GH.chip(eAut) + "</span></div>" +
      '<div class="cd-quem">' + GH.av(a, "sq", 76) + "<div><strong>" + esc(a.nome) + '</strong><span>' + esc(GH.funcao(a)) + "</span></div></div>" +
      "<h2>" + esc(d.titulo) + "</h2>" +
      '<div class="chat"><div class="msg">' + GH.av(a, "rd", 40) + '<div class="bolha">' + esc(d.ctx) + "</div></div>" +
      (d.trava ? '<div class="msg">' + GH.av(a, "rd", 40) + '<div class="bolha trava">' + ic("lock", 18) + "<span>" + esc(d.trava) + "</span></div></div>" : "") + "</div>" +
      '<div class="trabalho"><div class="tr-cab">' + ic("check", 16) + "<span>O trabalho de " + esc(a.nome) + '</span><em>' + esc(a.escreve) + '</em></div><div class="det">' + d.det + "</div></div>" +
      '<label class="resp"><span>' + esc(d.edit ? d.edit.campo : "Recado para " + a.nome) + '</span><textarea rows="2" placeholder="' + esc(d.edit ? d.edit.dica : "Opcional. Vai junto se você pedir ajuste.") + '"></textarea></label>' +
      '<div class="acoes">' + principal + '<div class="sec-ac">' + resto + (d.recusa.length ? '<button class="bt" type="button" data-rec aria-expanded="' + S.motivos + '">Pedir ajuste</button>' : "") + '</div><div class="mots' + (S.motivos ? " on" : "") + '"><span>O que não está certo?</span>' + d.recusa.map(function (m) { return '<button class="mot" type="button" data-mot="' + esc(m) + '">' + esc(m) + "</button>"; }).join("") + "</div></div>";
  }
  function ligarCard(raiz, d, depois) {
    raiz.querySelectorAll("[data-ac]").forEach(function (b) { b.onclick = function () { B.agir(b, d, +b.dataset.ac, depois); }; });
    raiz.querySelectorAll("[data-mot]").forEach(function (b) { b.onclick = function () { S.motivos = false; B.devolver(d, b.dataset.mot, depois); }; });
    var r = raiz.querySelector("[data-rec]"); if (r) r.onclick = function () { S.motivos = !S.motivos; raiz.querySelector(".mots").classList.toggle("on", S.motivos); r.setAttribute("aria-expanded", S.motivos); };
  }
  function espera() {
    var P = B.pendentes(), L = filtrada(), d = atual();
    var urg = P.filter(function (x) { return x.urgente; }).length, trav = P.filter(function (x) { return x.trava; }).length, min = Math.max(1, Math.round(P.length * 1.4));
    var ids = D.setores.map(function (s) { return s.id; }).filter(function (id) { return P.some(function (x) { return x.setor === id; }); });
    var chips = ["todas"].concat(ids).map(function (id) {
      var n = id === "todas" ? P.length : P.filter(function (x) { return x.setor === id; }).length;
      return '<button class="cf" type="button" data-fil="' + id + '" aria-pressed="' + (S.filtro === id) + '">' + (id === "todas" ? "Todas" : esc(B.setor(id).nome)) + " <b>" + n + "</b></button>";
    }).join("");
    var seen = {}, cluster = P.map(function (x) { return GH.autorDe(x); }).filter(function (a) { if (seen[a.id]) return false; seen[a.id] = 1; return true; }).slice(0, 6);
    var fila = L.map(function (x) {
      var a = GH.autorDe(x);
      return '<li><button class="q" type="button" data-q="' + x.id + '"' + (x.id === S.sel ? ' aria-current="true"' : "") + ">" + GH.av(a, "rd", 44) + '<span class="qt"><span class="qc">' + x.cod + " · " + esc(B.setor(x.setor).nome) + (x.urgente ? ' <i class="urg">Urgente</i>' : "") + '</span><span class="qn">' + esc(x.titulo) + "</span></span></button></li>";
    }).join("");
    var bl = B.bloqueadas.map(function (x) { return '<div class="bl">' + GH.ico("backlog", 20) + "<span><b>" + x.cod + "</b> " + esc(x.titulo) + "</span><span class=\"mudo\">" + esc(x.trava) + "</span></div>"; }).join("");
    var h = B.historico().slice(0, 4).map(function (x) { return "<li><span class=\"q2\">" + esc(x.q) + "</span><span>" + esc(x.t) + '</span><span class="c2">' + esc(x.c) + "</span></li>"; }).join("");
    var vazio = '<div class="vazio">' + GH.slot({ n: "vazio_espera", k: "vz", cls: "vz-g" }) + "<h2>Fila zerada</h2><p>Os agentes seguem sozinhos. Você volta quando algum precisar de decisão.</p></div>";
    return pagina("Espera você", "Cada decisão destrava um agente.", GH.contagem()) + '<div class="bento">' +
      '<section class="t t-azul a-res" aria-label="Resumo">' + GH.slot({ n: "hero_espera", k: "hero", cls: "hero-fill" }) + '<div class="rot">Decisões pendentes<span class="pill">' + urg + ' urgentes</span></div><div class="num">' + P.length + '</div><p class="leg-t">' + trav + " travam um agente. Cerca de " + min + ' min para zerar.</p><div class="cluster" aria-label="Quem espera você">' + cluster.map(function (a) { return GH.av(a, "rd", 44); }).join("") + "</div></section>" +
      '<section class="t t-card a-card" id="foco" aria-label="Decisão da vez">' + (d ? card(d) : vazio) + "</section>" +
      '<section class="t t-surf a-fila" aria-label="Fila"><div class="chips-f" role="group" aria-label="Filtrar por setor">' + chips + '</div><ul class="fila" tabindex="-1">' + fila + "</ul></section>" +
      rodandoTile() +
      (bl ? '<section class="t t-surf a-bl"><h2 class="rot">Esperam outra coisa</h2>' + bl + "</section>" : "") +
      '<section class="t t-surf a-hist"><h2 class="rot">Você decidiu</h2><ul class="hist">' + h + "</ul></section></div>";
  }

  /* ---------- Canal ---------- */
  function canal() {
    var k = B.canalKpis(), nos = k.nos;
    var proj = D.projetos.map(function (p) {
      var a = GH.agente(GH.etapaAgente[p.etapa] || "debruyne-orquestrador"), e = GH.mapa(p.est);
      return '<li class="proj"><div class="pj-top">' + GH.av(a, "rd", 44) + '<div class="pj-t"><strong>' + esc(B.nomeProj(p.slug)) + "</strong><span>" + esc(p.tipo) + " · " + esc(p.etapa) + " · " + p.ver + "</span></div>" + GH.chip(e) + "</div>" + GH.barra(e, p.prog, B.nomeProj(p.slug)) + '<div class="pj-pct">' + p.prog + "%</div></li>";
    }).join("");
    var fases = B.fases.map(function (f) {
      var ls = f.ids.map(function (id) { return nos.filter(function (n) { return n.id === id; })[0]; }), ok = ls.filter(function (n) { return n.est === "ok"; }).length;
      var est = ls.some(function (n) { return n.est === "rodando"; }) ? "rodando" : ok === ls.length ? "ok" : ok === 0 ? "backlog" : "pendente";
      return '<section class="t t-surf fase"><div class="rot">' + esc(f.nome) + "<span>" + ok + " de " + ls.length + "</span></div>" + GH.barra(est, Math.round(ok / ls.length * 100), f.nome) + '<ol class="est-l">' + ls.map(function (n) {
        var e = GH.mapa(n.est); if (n.est === "rodando") e = "rodando"; if (n.t === "gate" && n.est === "bloq") e = "backlog";
        return '<li class="e-' + e + '">' + GH.ico(e, 18) + "<span>" + esc(n.r) + "</span><em>" + (n.t === "gate" ? "você" : esc(n.a)) + "</em></li>";
      }).join("") + "</ol></section>";
    }).join("");
    var cont = {}; D.projetos.forEach(function (p) { var e = GH.mapa(p.est); cont[e] = (cont[e] || 0) + 1; });
    return pagina("Canal", "Shorts do Contexto Explica, do tema ao upload privado.", cont) + '<div class="bento b-canal">' +
      '<section class="t t-azul c-vis"><div class="rot">Visualizações em 14 dias</div><div class="num">' + B.n(k.vis) + '</div><p class="leg-t">' + (k.delta >= 0 ? "+" : "") + k.delta + "% sobre a semana anterior</p>" + B.spark(k.serie, 300, 56) + "</section>" +
      '<section class="t t-menta c-ret"><div class="rot">Retenção média</div><div class="anel">' + B.ring(k.ret, 132, 16, "Retenção média " + k.ret + "%") + '<span class="num m"><span>' + k.ret + '<small>%</small></span></span></div></section>' +
      '<section class="t t-sol c-cus"><div class="rot">Custo hoje</div><div class="num m">' + B.usd(k.custo) + '</div><div class="meter" role="img" aria-label="Custo ' + B.usd(k.custo) + " de um teto de " + B.usd(k.teto) + '"><i style="width:' + Math.round(k.custo / k.teto * 100) + '%"></i></div><p class="leg-t">teto dos jobs de hoje: ' + B.usd(k.teto) + "</p></section>" +
      '<section class="t t-ink c-esp"><div class="rot">Esperam você no Canal</div><div class="num m">' + k.espera + '</div><a class="bt ok grande" href="#/espera">' + ic("inbox", 24) + "Abrir a fila</a><ul>" + B.pendentes().filter(function (x) { return x.setor === "canal"; }).slice(0, 3).map(function (x) { return "<li><b>" + x.cod + "</b><span>" + esc(x.titulo) + "</span></li>"; }).join("") + "</ul></section>" +
      '<section class="t t-surf c-proj"><h2 class="rot">Em produção<span>' + k.ativos + " de " + k.total + "</span></h2><ul class=\"projs\">" + proj + "</ul></section>" +
      '<div class="fases">' + fases + "</div></div>";
  }

  /* ---------- Ecossistema > Agentes ---------- */
  function agCard(a) {
    return '<button class="ag" type="button" data-ag="' + a.id + '" data-s="' + a.setor + '"' + (a.id === S.feat ? ' aria-current="true"' : "") + ">" + GH.av(a, "sq", 88) + '<span class="ag-t"><b>' + esc(a.nome) + "</b><span>" + esc(GH.funcao(a)) + "</span></span>" + '<span class="ag-f">' + GH.chip(a.est) + "</span>" + GH.barra(a.est, a.prog, a.nome + ": " + GH.rot(a.est)) + "</button>";
  }
  function feat(a) {
    return '<section class="t feat" data-s="' + a.setor + '" aria-label="Agente em destaque">' + GH.av(a, "rt", 220, "feat-av") + '<div class="ft"><div class="rot">' + esc(B.setor(a.setor).nome) + '<span class="pill">' + esc(a.modelo) + '</span></div><h2>' + esc(a.nome) + '</h2><p class="ft-d">' + esc(a.desc) + "</p>" + '<div class="ft-st">' + GH.chip(a.est) + "<span>" + esc(a.tarefa) + "</span></div>" + GH.barra(a.est, a.prog, a.nome) +
      '<dl class="fatos"><div><dt>Escreve em</dt><dd>' + esc(a.escreve) + "</dd></div><div><dt>Ferramentas</dt><dd>" + a.kit.map(function (x) { return '<span class="chip">' + esc(x) + "</span>"; }).join("") + "</dd></div><div><dt>id</dt><dd><code>" + esc(a.id) + '</code></dd></div></dl><div class="formatos"><span>Como o avatar aparece</span>' + GH.av(a, "rd", 48) + GH.av(a, "sq", 64) + "</div></div></section>";
  }
  function agentes(lista, titulo, sub, mostrarFeat) {
    var todos = lista || GH.agentes, setores = ["todos"].concat(D.setores.map(function (s) { return s.id; }).filter(function (id) { return todos.some(function (a) { return a.setor === id; }); }));
    var vis = S.fSetor === "todos" || !lista ? todos.filter(function (a) { return S.fSetor === "todos" || a.setor === S.fSetor; }) : todos;
    var chips = lista ? "" : '<div class="chips-f" role="group" aria-label="Filtrar por setor">' + setores.map(function (id) { var n = id === "todos" ? todos.length : todos.filter(function (a) { return a.setor === id; }).length; return '<button class="cf" type="button" data-fs="' + id + '" aria-pressed="' + (S.fSetor === id) + '">' + (id === "todos" ? "Todos" : esc(B.setor(id).nome)) + " <b>" + n + "</b></button>"; }).join("") + "</div>";
    var f = GH.agente(S.feat) || todos[0];
    return pagina(titulo, sub, GH.contagem(todos)) + (mostrarFeat ? feat(f) : "") + chips + '<div class="grade">' + vis.map(agCard).join("") + "</div>";
  }
  function setorPag(id) {
    var s = B.setor(id), lista = GH.agentes.filter(function (a) { return a.setor === id; });
    return '<section class="t t-azul setor-h" data-s="' + id + '">' + GH.icSetor(id, 64) + "<div><h1 class=\"pag\">" + esc(s.nome) + "</h1><p>" + esc(s.desc) + " Chefe: " + esc(s.chefe) + ".</p></div></section><p class=\"nota\">Esta tela completa vem depois da escolha. Abaixo, os agentes do setor.</p>" + agentes(lista, "Agentes do setor", "", false).replace(/<div class="pag-cab">.*?<\/div>/, "");
  }

  function tela() {
    var r = B.rota();
    if (r === "espera") return espera();
    if (r === "canal") return canal();
    if (r === "ecossistema") return agentes(null, "Agentes", GH.agentes.length + " agentes em " + D.setores.length + " setores. Estados de exemplo.", true);
    return setorPag(r);
  }

  function render(foco) {
    app.innerHTML = casca(tela());
    document.title = "G (Vitrine): " + (B.menu.filter(function (m) { return m.id === B.rota(); })[0] || {}).nome;
    document.getElementById("tema").onclick = function () {
      var n = document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro";
      document.documentElement.dataset.tema = n; try { localStorage.setItem(CHAVE, n); } catch (e) {} render();
      document.getElementById("tema").focus();
    };
    document.querySelector("[data-slots-btn]").onclick = function () { GH.slotsModo(); };
    var r = B.rota();
    if (r === "espera") {
      var d = atual(), raiz = document.getElementById("foco");
      if (d) ligarCard(raiz, d, function () { S.motivos = false; render(); });
      app.querySelectorAll("[data-fil]").forEach(function (b) { b.onclick = function () { S.filtro = b.dataset.fil; render(); var x = app.querySelector('[data-fil="' + S.filtro + '"]'); if (x) x.focus(); }; });
      app.querySelectorAll("[data-q]").forEach(function (b) { b.onclick = function () { S.sel = b.dataset.q; S.motivos = false; render(); var rr = document.getElementById("foco"); if (B.estreito(980)) rr.scrollIntoView({ behavior: B.suave(), block: "start" }); var x = app.querySelector('[data-q="' + S.sel + '"]'); if (x) x.focus({ preventScroll: true }); }; });
    } else {
      app.querySelectorAll("[data-ag]").forEach(function (b) { b.onclick = function () { S.feat = b.dataset.ag; render(); if (r === "ecossistema") { var f = app.querySelector(".feat"); if (f) f.scrollIntoView({ behavior: B.suave(), block: "nearest" }); } var x = app.querySelector('[data-ag="' + S.feat + '"]'); if (x) x.focus({ preventScroll: true }); }; });
      app.querySelectorAll("[data-fs]").forEach(function (b) { b.onclick = function () { S.fSetor = b.dataset.fs; render(); var x = app.querySelector('[data-fs="' + S.fSetor + '"]'); if (x) x.focus(); }; });
    }
    GH.slotsAtualizar();
  }
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); document.getElementById("principal").focus({ preventScroll: true }); });
  render();
  GH.slotsLigar();
})();
