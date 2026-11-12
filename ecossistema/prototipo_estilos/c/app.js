(function () {
  var esc = B.esc, ic = B.icon, tema = B.tema("tema-c", "claro");
  var sel = null, filtro = "todas";

  document.getElementById("app").innerHTML =
    '<a class="pular" href="#main">Ir para o conteúdo</a><header class="slab"><div class="topbar"><div class="marca"><i aria-hidden="true"></i><span>Contexto Explica</span></div><nav id="menu" aria-label="Menu principal"></nav><button class="tema" id="tema" type="button"></button></div><div id="cab"></div></header><main id="main" tabindex="-1"></main><div id="toast" class="toasts" role="status" aria-live="polite"></div>';
  var main = document.getElementById("main"), cab = document.getElementById("cab");

  function menu() {
    var r = B.rota(), n = B.pendentes().length;
    document.getElementById("menu").innerHTML = B.menu.map(function (m) {
      return '<a class="item" href="#/' + m.id + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 20) + "<span>" + m.nome + "</span>" + (m.id === "espera" && n ? '<span class="cnt" aria-label="' + n + ' em aberto">' + n + "</span>" : "") + "</a>";
    }).join("");
    var t = document.getElementById("tema"), escuro = tema.get() === "escuro";
    t.innerHTML = ic(escuro ? "sun" : "moon", 20);
    t.setAttribute("aria-label", escuro ? "Mudar para tema claro" : "Mudar para tema escuro");
  }

  function titulo(h1, sub, acao) {
    return '<div class="titulo"><div><h1>' + h1 + "</h1><p>" + sub + "</p></div>" + (acao || "") + "</div>";
  }

  function detalhe(d, sheet) {
    var s = B.setor(d.setor), pi = B.principal(d), a = d.acoes;
    var h = sheet ? '<div class="sh-fim"><button type="button" data-fechar aria-label="Fechar">' + ic("close", 22) + "</button></div>" : "";
    h += '<div class="dp-c"><div class="dp-top"><span class="pill acc">' + esc(s.nome) + "</span>" + (d.urgente ? '<span class="pill warn">Urgente</span>' : "") + "<span>" + d.cod + "</span></div><h2>" + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>";
    if (d.trava) h += '<p class="trava">' + ic("lock", 20) + "<span>" + esc(d.trava) + "</span></p>";
    if (d.det) h += '<div class="det">' + d.det + "</div>";
    if (d.edit) h += '<label class="edit"><span>' + esc(d.edit.campo) + '</span><textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>';
    if (d.recusa.length) h += '<div class="ajuste"><span>Pedir ajuste:</span>' + d.recusa.map(function (r) { return '<button class="chipbtn" type="button" data-aj="' + esc(r) + '">' + esc(r) + "</button>"; }).join("") + "</div>";
    h += '</div><div class="dp-pe">';
    [pi].concat(a.map(function (_, i) { return i; }).filter(function (i) { return i !== pi; })).forEach(function (i, n) {
      var x = a[i];
      h += '<button class="btn ' + (n === 0 ? "prim" + (x.k === "risco" ? " risco" : "") : "") + '" type="button" data-acao="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (x.k === "copiar" ? ic("copy", 18) : "") + esc(x.r) + "</button>";
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
    cab.innerHTML = titulo("Espera você", "Os agentes seguem sozinhos até aqui. O que está abaixo só anda com a sua decisão.") +
      '<div class="metr" style="--n:4"><div class="m"><span class="ml">Em aberto</span><span class="mv">' + todas.length + '</span><span class="ms">' + B.bloqueadas.length + " bloqueada pelo Vini</span></div>" +
      '<div class="m"><span class="ml">Urgentes</span><span class="mv">' + urg + '</span><span class="ms">Travam narração, render ou fila</span></div>' +
      '<div class="m"><span class="ml">Seguram outra etapa</span><span class="mv">' + trava + "<small>de " + todas.length + '</small></span><span class="ms"><span class="mini"><i style="width:' + (todas.length ? trava / todas.length * 100 : 0).toFixed(0) + '%"></i></span></span></div>' +
      '<div class="m"><span class="ml">Resolvidas</span><span class="mv">' + (hoje + 3) + '</span><span class="ms">' + hoje + " agora, 3 desde ontem</span></div></div>";
    var por = D.setores.map(function (s) { return { s: s, n: todas.filter(function (x) { return x.setor === s.id; }).length }; }).filter(function (x) { return x.n; });
    var h = '<div class="seg" role="group" aria-label="Filtrar por setor"><button class="sg" type="button" data-fil="todas" aria-pressed="' + (filtro === "todas") + '">Tudo <b>' + todas.length + "</b></button>" + por.map(function (x) {
      return '<button class="sg" type="button" data-fil="' + x.s.id + '" aria-pressed="' + (filtro === x.s.id) + '">' + esc(x.s.nome) + " <b>" + x.n + "</b></button>";
    }).join("") + "</div>";
    h += '<div class="duas"><section class="cards" aria-label="Decisões">' + (vis.length ? vis.map(function (x) {
      return '<button class="it' + (x.urgente ? " urg" : "") + '" type="button" data-sel="' + x.id + '" aria-current="' + (x.id === sel) + '"><span class="cod">' + x.cod + "</span><b>" + esc(x.titulo) + "</b><small>" + esc(x.trava || x.ctx) + "</small>" + ic("chev", 20) + "</button>";
    }).join("") : '<div class="card vazio">' + ic("check", 40) + "<p>Nada em aberto neste filtro.</p></div>") + "</section>";
    h += '<aside class="card dp" aria-label="Detalhe">' + (d ? detalhe(d) : '<div class="vazio">' + ic("check", 40) + "<p>Selecione uma decisão.</p></div>") + "</aside></div>";
    main.innerHTML = h;
  }

  function canal() {
    var k = B.canalKpis(), s = B.setor("canal"), por = {}, mx = Math.max.apply(null, D.metricas.map(function (m) { return m.vis; }));
    k.nos.forEach(function (n) { por[n.id] = n; });
    cab.innerHTML = titulo("Canal", esc(s.desc), '<a class="btn prim" href="#/espera">' + ic("inbox", 22) + "Abrir Espera você" + (k.espera ? " · " + k.espera : "") + "</a>") +
      '<div class="metr" style="--n:6">' +
      '<a class="m" href="#/espera"><span class="ml">Esperam você</span><span class="mv">' + k.espera + '</span><span class="ms">Decisões do Canal</span></a>' +
      '<div class="m"><span class="ml">Em produção</span><span class="mv">' + k.ativos + "<small>de " + k.total + '</small></span><span class="ms">' + k.fila + " na fila de postagem</span></div>" +
      '<div class="m"><span class="ml">Visualizações, 14 dias</span><span class="mv">' + B.n(k.vis) + '</span><span class="ms"><span class="up">+' + k.delta + '%</span><span class="sb">' + B.spark(k.serie, 110, 34) + "</span></span></div>" +
      '<div class="m"><span class="ml">Retenção média</span><span class="mv">' + k.ret + '<small>%</small></span><span class="mring">' + B.ring(k.ret, 46, 6, "Retenção média " + k.ret + "%") + '</span><span class="ms">5 últimos vídeos</span></div>' +
      '<div class="m"><span class="ml">Custo dos jobs hoje</span><span class="mv">' + B.usd(k.custo).replace("US$ ", "") + "<small>US$</small></span>" + '<span class="ms"><span class="mini" role="img" aria-label="' + B.usd(k.custo) + " de " + B.usd(k.teto) + '"><i style="width:' + (k.custo / k.teto * 100).toFixed(0) + '%"></i></span></span></div>' +
      '<div class="m"><span class="ml">Etapas do vídeo atual</span><span class="mv">' + k.feitos + "<small>de " + k.nos.length + '</small></span><span class="ms"><span class="mini"><i style="width:' + (k.feitos / k.nos.length * 100).toFixed(0) + '%"></i></span></span></div></div>';

    var h = '<section class="card" aria-labelledby="t-fl"><h2 id="t-fl">Um Short, do tema ao upload privado</h2><p class="nota">“A recessão de amizades entre homens”: ' + k.feitos + " de " + k.nos.length + " etapas prontas.</p><div class=\"metro-box\"><div class=\"fases\">" + B.fases.map(function (f) {
      return '<div class="fase" style="--q:' + f.ids.length + '"><h3>' + f.nome + '</h3><ol class="trilho">' + f.ids.map(function (i) {
        var n = por[i];
        return '<li class="' + n.est + (n.t === "gate" ? " gate" : "") + '" title="' + esc(n.r) + '"><span class="dot"></span><span class="sr">' + esc(n.r) + ", " + B.estLabel[n.est] + (n.t === "gate" ? ", sua aprovação" : "") + "</span></li>";
      }).join("") + "</ol></div>";
    }).join("") + '</div></div><div class="agora"><b>Agora: Olise desenha as cenas</b><span>Depois disso, a etapa “Aprovar cenas” espera você.</span></div><p class="legenda"><span><i></i>pronto</span><span><i class="g"></i>sua aprovação</span><span><i class="v"></i>ainda não começou</span></p></section>';

    h += '<div class="grid2"><section class="card" aria-labelledby="t-pr"><h2 id="t-pr">Produção</h2><p class="nota">Oito vídeos, do mais cedo ao mais perto de publicar.</p><div class="listaP">' + D.projetos.map(function (p) {
      var inner = "<b>" + esc(B.nomeProj(p.slug)) + '</b><span class="pill ' + (p.est === "erro" ? "bad" : p.est === "espera" ? "warn" : p.est === "rodando" ? "acc" : "") + '">' + B.estLabel[p.est] + "</span><small>" + esc(p.tipo) + " · " + esc(p.etapa) + '</small><span class="barra"><i style="width:' + p.prog + '%"></i></span>';
      return (p.est === "espera" || p.est === "erro") ? '<a class="pr ' + p.est + '" href="#/espera">' + inner + "</a>" : '<div class="pr ' + p.est + '">' + inner + "</div>";
    }).join("") + '</div></section><div class="col"><section class="card" aria-labelledby="t-vd"><h2 id="t-vd">Visualizações por dia</h2><p class="nota">Dado de exemplo, 14 dias.</p>' + B.barsV(k.serie, 360, 110, "Visualizações por dia, 14 dias") + '<div class="eixo"><span>há 14 dias</span><span>hoje: ' + B.n(k.serie[k.serie.length - 1]) + '</span></div></section><section class="card" aria-labelledby="t-rt"><h2 id="t-rt">Retenção por vídeo</h2><div class="aneis">' + D.metricas.map(function (m) {
      return '<div><span style="position:relative;display:block">' + B.ring(m.ret, 56, 7, m.v + ": " + m.ret + "% de retenção") + "<b aria-hidden=\"true\">" + m.ret + "</b></span><span>" + esc(m.v) + "</span></div>";
    }).join("") + '</div></section><section class="card" aria-labelledby="t-ag"><h2 id="t-ag">Precisa de atenção</h2>' + D.jobs.filter(function (j) { return j.estado === "erro"; }).map(function (j) {
      return '<div class="job"><b>' + esc(j.nome) + "</b><p>" + esc(j.log[1]) + '</p><button class="btn" type="button" data-retry>' + ic("retry", 18) + "Tentar de novo</button></div>";
    }).join("") + "</section></div></div>";
    main.innerHTML = h;
  }

  function stub(id) {
    var m = B.menu.filter(function (x) { return x.id === id; })[0], s = B.setor(id);
    cab.innerHTML = titulo(m.nome, esc(s.desc) + " Chefe: " + esc(s.chefe) + ".");
    main.innerHTML = '<section class="card"><p class="nota" style="margin:0 0 16px">Fora da comparação. O menu mostra a estrutura final de 8 grupos.</p><a class="btn prim" href="#/espera">Voltar para Espera você</a></section>';
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
      if (B.estreito(1180)) { var sh = B.sheet(); sh.innerHTML = detalhe(atual(), true); sh.showModal(); }
      else { var nb = main.querySelector('[data-sel="' + sel + '"]'); if (nb) nb.focus(); }
      return;
    }
    d = atual();
    if ((b = e.target.closest("[data-acao]")) && d) { B.agir(b, d, +b.dataset.acao, render); return; }
    if ((b = e.target.closest("[data-aj]")) && d) { B.devolver(d, b.dataset.aj, render); return; }
    if (e.target.closest("[data-retry]")) B.toast("Nova rodada do Salah pedida.");
  });
  document.getElementById("tema").addEventListener("click", function () { tema.alternar(); menu(); });
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); });
  render();
})();
