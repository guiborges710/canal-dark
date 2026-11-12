(function () {
  var esc = B.esc, ic = B.icon, tema = B.tema("tema-b", "escuro");
  var sel = null, filtro = "todas";
  var COR = { canal: "#6aa7ff", clipes: "#b69cff", inteligencia: "#4fd1b8", trabalho: "#f2b441", programacao: "#ff9d6a", financas: "#8ad06a", ecossistema: "#9aa2ad" };

  document.getElementById("app").innerHTML =
    '<a class="pular" href="#main">Ir para o conteúdo</a><div class="app"><aside class="rail" aria-label="Menu principal"><div class="marca"><i aria-hidden="true"></i>Contexto Explica</div><nav id="menu"></nav><div class="rail-fim"><div class="srv" id="srv"></div><button class="tema" id="tema" type="button"></button></div></aside><main id="main" tabindex="-1"></main></div><div id="toast" class="toasts" role="status" aria-live="polite"></div>';
  var main = document.getElementById("main");

  function menu() {
    var r = B.rota(), n = B.pendentes().length;
    document.getElementById("menu").innerHTML = B.menu.map(function (m) {
      return '<a class="item" href="#/' + m.id + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 20) + "<span>" + m.nome + "</span>" + (m.id === "espera" && n ? '<span class="cnt" aria-label="' + n + ' em aberto">' + n + "</span>" : "") + "</a>";
    }).join("");
    document.getElementById("srv").innerHTML = D.saude.servidores.map(function (s) { return "<span><i></i>" + esc(s.n) + " :" + s.p + "</span>"; }).join("") + '<span class="pausa"><i></i>Maestro da sprint pausado</span>';
    var t = document.getElementById("tema"), escuro = tema.get() === "escuro";
    t.innerHTML = ic(escuro ? "sun" : "moon", 20) + "<span>" + (escuro ? "Tema claro" : "Tema escuro") + "</span>";
    t.setAttribute("aria-label", escuro ? "Mudar para tema claro" : "Mudar para tema escuro");
  }

  function detalhe(d, sheet) {
    var s = B.setor(d.setor), pi = B.principal(d), a = d.acoes;
    var h = (sheet ? '<div class="sh-fim"><button type="button" data-fechar aria-label="Fechar">' + ic("close", 22) + "</button></div>" : "");
    h += '<div class="dp-corpo"><div class="dp-top"><span class="pill">' + esc(s.nome) + "</span>" + (d.urgente ? '<span class="pill warn">Urgente</span>' : "") + "<span>" + d.cod + "</span></div><h2>" + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>";
    if (d.trava) h += '<p class="trava">' + ic("lock", 18) + "<span>" + esc(d.trava) + "</span></p>";
    if (d.det) h += '<div class="det">' + d.det + "</div>";
    if (d.edit) h += '<label class="edit"><span>' + esc(d.edit.campo) + '</span><textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>';
    if (d.recusa.length) h += '<div class="ajuste"><span>Pedir ajuste:</span>' + d.recusa.map(function (r) { return '<button class="chipbtn" type="button" data-aj="' + esc(r) + '">' + esc(r) + "</button>"; }).join("") + "</div>";
    h += '</div><div class="dp-pe">';
    [pi].concat(a.map(function (_, i) { return i; }).filter(function (i) { return i !== pi; })).forEach(function (i, n) {
      var x = a[i];
      h += '<button class="btn ' + (n === 0 ? "prim" + (x.k === "risco" ? " risco" : "") : "sec") + '" type="button" data-acao="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (x.k === "copiar" ? ic("copy", 18) : "") + esc(x.r) + "</button>";
      if (n === 0 && x.dono) h += '<p class="dono">' + esc(x.dono) + "</p>";
    });
    if (!a.length) h += '<p class="dono">Sem ação disponível.</p>';
    return h + "</div>";
  }

  function espera() {
    var todas = B.pendentes();
    var vis = todas.filter(function (d) { return filtro === "todas" || d.setor === filtro; });
    if (!vis.some(function (d) { return d.id === sel; })) sel = vis.length ? vis[0].id : null;
    var d = vis.filter(function (x) { return x.id === sel; })[0];
    var urg = todas.filter(function (x) { return x.urgente; }).length, trava = todas.filter(function (x) { return x.trava; }).length;
    var hoje = B.historico().filter(function (x) { return x.q === "Agora"; }).length;
    var por = D.setores.map(function (s) { return { s: s, n: todas.filter(function (x) { return x.setor === s.id; }).length }; }).filter(function (x) { return x.n; });
    var h = '<div class="topo"><div><h1>Espera você</h1><p>' + todas.length + " decisões em aberto de " + por.length + " setores. Use ↑ e ↓ para percorrer a lista.</p></div></div>";
    h += '<div class="tiles t5">' +
      '<div class="tile"><span class="tl">Em aberto</span><span class="tv">' + todas.length + '</span><span class="ts">' + B.bloqueadas.length + " bloqueada aguardando o Vini</span></div>" +
      '<div class="tile"><span class="tl">Urgentes</span><span class="tv amb">' + urg + '</span><span class="ts">Travam narração, render ou fila</span></div>' +
      '<div class="tile"><span class="tl">Seguram outra etapa</span><span class="tv">' + trava + "<small>de " + todas.length + '</small></span><span class="ts"><span class="meter"><i style="width:' + (todas.length ? trava / todas.length * 100 : 0).toFixed(0) + '%;background:var(--amb)"></i></span></span></div>' +
      '<div class="tile"><span class="tl">Por setor</span><span class="stk" role="img" aria-label="Decisões por setor">' + por.map(function (x) { return '<i style="flex:' + x.n + ";background:" + COR[x.s.id] + '"></i>'; }).join("") + '</span><span class="leg">' + por.map(function (x) { return '<span style="--c:' + COR[x.s.id] + '">' + esc(x.s.nome) + " " + x.n + "</span>"; }).join("") + "</span></div>" +
      '<div class="tile"><span class="tl">Resolvidas</span><span class="tv">' + (hoje + 3) + '</span><span class="ts">' + hoje + " agora, 3 desde ontem</span></div></div>";
    h += '<div class="filtros" role="group" aria-label="Filtrar por setor"><button class="fil" type="button" data-fil="todas" aria-pressed="' + (filtro === "todas") + '">Tudo <b>' + todas.length + "</b></button>" + por.map(function (x) {
      return '<button class="fil" type="button" data-fil="' + x.s.id + '" aria-pressed="' + (filtro === x.s.id) + '">' + esc(x.s.nome) + " <b>" + x.n + "</b></button>";
    }).join("") + "</div>";
    h += '<div class="split"><section class="panel lista" aria-label="Decisões" id="lista">' + (vis.length ? vis.map(function (x) {
      return '<button class="lr' + (x.urgente ? " urg" : "") + '" type="button" data-sel="' + x.id + '" aria-current="' + (x.id === sel) + '"><span class="cod">' + x.cod + "</span><b>" + esc(x.titulo) + "</b><small>" + esc(x.trava || x.ctx) + '</small><span class="tag">' + esc(B.setor(x.setor).nome) + "</span></button>";
    }).join("") : '<div class="vazio">' + ic("check", 36) + "<p>Nada em aberto neste filtro.</p></div>") + "</section>";
    h += '<aside class="panel det-panel" aria-label="Detalhe">' + (d ? detalhe(d) : '<div class="vazio">' + ic("check", 36) + "<p>Selecione uma decisão.</p></div>") + "</aside></div>";
    main.innerHTML = h;
  }

  function canal() {
    var k = B.canalKpis(), s = B.setor("canal"), mx = Math.max.apply(null, D.metricas.map(function (m) { return m.vis; }));
    var h = '<div class="topo"><div><h1>Canal</h1><p>' + esc(s.desc) + '</p></div><a class="btn prim" href="#/espera">' + ic("inbox", 20) + "Abrir Espera você" + (k.espera ? " (" + k.espera + ")" : "") + "</a></div>";
    h += '<div class="tiles">' +
      '<a class="tile" href="#/espera"><span class="tl">Esperam você</span><span class="tv amb">' + k.espera + '</span><span class="ts">Decisões do Canal</span></a>' +
      '<div class="tile"><span class="tl">Em produção</span><span class="tv">' + k.ativos + "<small>de " + k.total + '</small></span><span class="ts">' + k.fila + " na fila de postagem</span></div>" +
      '<div class="tile"><span class="tl">Visualizações, 14 dias</span><span class="tv">' + B.n(k.vis) + '</span><span class="ts"><span class="up">+' + k.delta + '%</span><span class="sparkbox">' + B.spark(k.serie, 110, 34) + "</span></span></div>" +
      '<div class="tile"><span class="tl">Retenção média</span><span class="tv">' + k.ret + '<small>%</small></span><span class="ringpos">' + B.ring(k.ret, 48, 6, "Retenção média " + k.ret + "%") + '</span><span class="ts">5 últimos vídeos</span></div>' +
      '<div class="tile"><span class="tl">Custo dos jobs hoje</span><span class="tv">' + B.usd(k.custo).replace("US$ ", "") + "<small>US$</small></span>" + '<span class="ts"><span class="meter" role="img" aria-label="' + B.usd(k.custo) + " de " + B.usd(k.teto) + '"><i style="width:' + (k.custo / k.teto * 100).toFixed(0) + '%"></i></span></span></div>' +
      '<div class="tile"><span class="tl">Etapas do vídeo atual</span><span class="tv">' + k.feitos + "<small>de " + k.nos.length + '</small></span><span class="ts"><span class="meter"><i style="width:' + (k.feitos / k.nos.length * 100).toFixed(0) + '%;background:var(--azu)"></i></span></span></div></div>';

    h += '<div class="g2"><section class="panel"><div class="ph"><h2>Visualizações por dia</h2><span>Dado de exemplo, 14 dias</span></div><div class="pb">' + B.barsV(k.serie, 560, 120, "Visualizações por dia nos últimos 14 dias") + '<div class="eixo"><span>há 14 dias</span><span>hoje: ' + B.n(k.serie[k.serie.length - 1]) + "</span></div></div></section>" +
      '<section class="panel"><div class="ph"><h2>Retenção por vídeo</h2><span>visualizações · retenção</span></div><div class="pb ret">' + D.metricas.map(function (m) {
        return '<div class="ret-l"><span class="n">' + esc(m.v) + '</span><span class="v">' + B.n(m.vis) + '</span><span class="r">' + m.ret + '%</span><span class="meter m" role="img" aria-label="' + m.ret + '% de retenção"><i style="width:' + m.ret + "%;background:" + (m.ret >= 60 ? "var(--ver)" : m.ret >= 50 ? "var(--azu)" : "var(--amb)") + '"></i></span></div>';
      }).join("") + "</div></section></div>";

    var por = {}; k.nos.forEach(function (n) { por[n.id] = n; });
    h += '<section class="panel" style="margin-bottom:10px"><div class="ph"><h2>Fluxo de um Short</h2><span>“A recessão de amizades entre homens”. Linha tracejada: sua aprovação.</span></div><div class="lanes">' + B.fases.map(function (f) {
      var ok = f.ids.filter(function (i) { return por[i].est === "ok"; }).length;
      return '<div class="lane"><h3><span>' + f.nome + "</span><span>" + ok + "/" + f.ids.length + "</span></h3>" + f.ids.map(function (i) {
        var n = por[i];
        return '<div class="nd ' + n.est + (n.t === "gate" ? " gate" : "") + '"><span class="p"></span><span><b>' + esc(n.r) + "</b><small>" + esc(n.a || "automático") + " · " + B.estLabel[n.est] + "</small></span></div>";
      }).join("") + "</div>";
    }).join("") + "</div></section>";

    h += '<div class="bottom"><section class="panel"><div class="ph"><h2>Produção</h2><span>' + D.projetos.length + ' vídeos</span></div><table class="tabela-p"><thead><tr><th>Vídeo</th><th>Estado</th><th>Progresso</th></tr></thead><tbody>' + D.projetos.map(function (p) {
      var c = p.est === "erro" ? "bad" : p.est === "espera" ? "warn" : p.est === "rodando" ? "run" : p.est === "ok" ? "ok" : "";
      var m = p.est === "erro" ? "erro" : p.est === "rodando" ? "run" : p.est === "espera" ? "esp" : "";
      var nome = (p.est === "espera" || p.est === "erro") ? '<a class="irl" href="#/espera">' + esc(B.nomeProj(p.slug)) + "</a>" : esc(B.nomeProj(p.slug));
      return "<tr><td>" + nome + '<span class="mt">' + esc(p.tipo) + " · " + esc(p.etapa) + '</span></td><td><span class="pill ' + c + '">' + B.estLabel[p.est] + '</span></td><td><div class="prog"><span class="meter ' + m + '"><i style="width:' + p.prog + '%"></i></span><span>' + p.prog + "%</span></div></td></tr>";
    }).join("") + "</tbody></table></section>";
    var j1 = D.jobs[0], j3 = D.jobs[2];
    h += '<div class="col"><section class="panel"><div class="ph"><h2>Agora</h2><span>' + B.usd(j1.custo) + " de " + B.usd(j1.teto) + '</span></div><div class="jobbar"><b>' + esc(j1.nome) + '</b><span class="pill run">Rodando</span></div><pre class="term" tabindex="0" aria-label="Log do job">' + j1.log.map(esc).join("\n") + '</pre><div class="jobbar"><b>' + esc(j3.nome) + '</b><span class="pill bad">Com erro</span></div><pre class="term" tabindex="0" aria-label="Log do erro">' + j3.log.map(function (l, i) { return i === 1 ? '<span class="e">' + esc(l) + "</span>" : esc(l); }).join("\n") + '</pre><div style="padding:0 14px 14px"><button class="btn" type="button" data-retry>' + ic("retry", 18) + "Tentar de novo</button></div></section></div></div>";
    main.innerHTML = h;
  }

  function stub(id) {
    var m = B.menu.filter(function (x) { return x.id === id; })[0], s = B.setor(id);
    main.innerHTML = '<div class="topo"><div><h1>' + m.nome + "</h1><p>" + esc(s.desc) + " Chefe: " + esc(s.chefe) + '.</p></div></div><section class="panel"><div class="pb"><p style="color:var(--mut);margin-bottom:14px">Fora da comparação. O menu mostra a estrutura final de 8 grupos.</p><a class="btn prim" href="#/espera">Voltar para Espera você</a></div></section>';
  }

  function render() {
    var r = B.rota(), y = window.scrollY;
    menu();
    (r === "espera" ? espera : r === "canal" ? canal : function () { stub(r); })();
    window.scrollTo(0, y);
    var sh = B.sheet();
    if (sh.open) sh.close();
  }

  function atual() { return B.pendentes().filter(function (x) { return x.id === sel; })[0]; }
  document.addEventListener("click", function (e) {
    var b, d;
    if ((b = e.target.closest("[data-fil]"))) { filtro = b.dataset.fil; render(); return; }
    if ((b = e.target.closest("[data-sel]"))) {
      sel = b.dataset.sel; render();
      if (B.estreito(1100)) { var sh = B.sheet(); sh.innerHTML = detalhe(atual(), true); sh.showModal(); }
      else { var nb = main.querySelector('[data-sel="' + sel + '"]'); if (nb) nb.focus(); }
      return;
    }
    d = atual();
    if ((b = e.target.closest("[data-acao]")) && d) { B.agir(b, d, +b.dataset.acao, render); return; }
    if ((b = e.target.closest("[data-aj]")) && d) { B.devolver(d, b.dataset.aj, render); return; }
    if (e.target.closest("[data-retry]")) B.toast("Nova rodada do Salah pedida.");
  });
  main.addEventListener("keydown", function (e) {
    var b = e.target.closest(".lr");
    if (!b || (e.key !== "ArrowDown" && e.key !== "ArrowUp")) return;
    e.preventDefault();
    var l = Array.prototype.slice.call(main.querySelectorAll(".lr")), i = l.indexOf(b) + (e.key === "ArrowDown" ? 1 : -1);
    if (i < 0 || i >= l.length) return;
    sel = l[i].dataset.sel; render();
    main.querySelector('[data-sel="' + sel + '"]').focus();
  });
  document.getElementById("tema").addEventListener("click", function () { tema.alternar(); menu(); });
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); });
  render();
})();
