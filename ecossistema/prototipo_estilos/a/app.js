(function () {
  var esc = B.esc, ic = B.icon, tema = B.tema("tema-a", "claro");
  var sel = null;

  document.getElementById("app").innerHTML =
    '<a class="pular" href="#main">Ir para o conteúdo</a><div class="app"><aside class="nav" aria-label="Menu principal"><div class="marca"><span class="marca-sel" aria-hidden="true">C</span><div><b>Contexto Explica</b><small>Seu sistema único</small></div></div><nav id="menu"></nav><button class="tema" id="tema" type="button"></button></aside><main id="main" tabindex="-1"></main></div><div id="toast" class="toasts" role="status" aria-live="polite"></div>';
  var main = document.getElementById("main");

  function menu() {
    var r = B.rota(), n = B.pendentes().length;
    document.getElementById("menu").innerHTML = B.menu.map(function (m) {
      return '<a class="item" href="#/' + m.id + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 22) + "<span>" + m.nome + "</span>" +
        (m.id === "espera" && n ? '<span class="badge" aria-label="' + n + ' em aberto">' + n + "</span>" : "") + "</a>";
    }).join("");
    var t = document.getElementById("tema"), escuro = tema.get() === "escuro";
    t.innerHTML = ic(escuro ? "sun" : "moon", 22) + "<span>" + (escuro ? "Tema claro" : "Tema escuro") + "</span>";
    t.setAttribute("aria-label", escuro ? "Mudar para tema claro" : "Mudar para tema escuro");
  }

  /* ---------- Espera você ---------- */
  function espera() {
    var p = B.pendentes();
    if (!p.some(function (d) { return d.id === sel; })) sel = p.length ? p[0].id : null;
    var d = p.filter(function (x) { return x.id === sel; })[0];
    var urg = p.filter(function (x) { return x.urgente; }).length;
    var h = '<header class="cab"><div><h1>Espera você</h1><p class="sub">' +
      (p.length ? p.length + " decisões em aberto" + (urg ? ", " + urg + " urgentes" : "") + ". Uma de cada vez, a mais importante primeiro." : "Nada espera você agora. Os agentes seguem sozinhos.") + "</p></div></header>";
    h += d ? hero(d) : '<section class="card vazio">' + ic("check", 44) + "<h2>Tudo em dia</h2><p class=\"sub\" style=\"margin:8px auto 0\">Quando um agente precisar de você, a decisão aparece aqui.</p></section>";

    var resto = p.filter(function (x) { return x.id !== sel; });
    D.setores.forEach(function (s) {
      var l = resto.filter(function (x) { return x.setor === s.id; });
      if (!l.length) return;
      h += '<section class="grupo" aria-label="' + esc(s.nome) + '"><h3>' + esc(s.nome) + "<span>" + l.length + '</span></h3><ul class="grp">' + l.map(function (x) {
        return '<li><button class="row" type="button" data-sel="' + x.id + '">' + (x.urgente ? '<span class="pt" title="Urgente" aria-label="Urgente"></span>' : "") + '<span class="t"><b>' + esc(x.titulo) + "</b><small>" + esc(x.trava || x.ctx) + "</small></span>" + ic("chev", 20) + "</button></li>";
      }).join("") + "</ul></section>";
    });
    h += '<section class="grupo"><h3>Resolvido recentemente</h3><ul class="grp hist">' + B.historico().map(function (x) {
      return '<li><span class="q">' + esc(x.q) + "</span><span>" + esc(x.t) + "</span></li>";
    }).join("") + "</ul></section>";
    main.innerHTML = h;
  }

  function hero(d) {
    var s = B.setor(d.setor), pi = B.principal(d), a = d.acoes, h;
    h = '<article class="card hero" aria-labelledby="h-tit"><div class="hero-top"><span class="pill acc">' + esc(s.nome) + "</span>" + (d.urgente ? '<span class="pill warn">Urgente</span>' : "") + '<span class="cod">' + d.cod + "</span></div>";
    h += '<h2 id="h-tit">' + esc(d.titulo) + "</h2><p class=\"ctx\">" + esc(d.ctx) + "</p>";
    if (d.trava) h += '<p class="trava">' + ic(/externa|Ação/.test(d.trava) ? "alert" : "lock", 20) + "<span>" + esc(d.trava) + "</span></p>";
    if (d.det) h += '<div class="det">' + d.det + "</div>";
    if (d.edit) h += '<label class="edit"><span>' + esc(d.edit.campo) + '</span><textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>';
    h += '<div class="acoes">';
    var ordem = [pi].concat(a.map(function (_, i) { return i; }).filter(function (i) { return i !== pi; }));
    ordem.forEach(function (i, n) {
      var x = a[i], cls = n === 0 ? (x.k === "risco" ? "btn risco prim-slot" : "btn prim") : "btn sec";
      h += '<button class="' + cls + '" type="button" data-acao="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (x.k === "copiar" ? ic("copy", 20) : "") + esc(x.r) + "</button>";
      if (n === 0 && x.dono) h += '<p class="dono">' + esc(x.dono) + "</p>";
    });
    h += "</div>";
    if (d.recusa.length) h += '<div class="ajuste"><span>Pedir ajuste em</span>' + d.recusa.map(function (r) { return '<button class="chipbtn" type="button" data-aj="' + esc(r) + '">' + esc(r) + "</button>"; }).join("") + "</div>";
    return h + "</article>";
  }

  /* ---------- Canal ---------- */
  function canal() {
    var k = B.canalKpis(), s = B.setor("canal"), h;
    h = '<header class="cab"><div><h1>Canal</h1><p class="sub">' + esc(s.desc) + '</p></div><a class="btn prim" href="#/espera">' + ic("inbox", 22) + "Abrir Espera você" + (k.espera ? " · " + k.espera : "") + "</a></header>";
    h += '<div class="kpis">' +
      '<a class="card kpi link" href="#/espera"><span class="rot">Esperam você</span><span class="num">' + k.espera + '</span><span class="rod">Decisões do Canal em aberto</span></a>' +
      '<div class="card kpi"><span class="rot">Em produção</span><span class="num">' + k.ativos + "<small>de " + k.total + '</small></span><div class="rod"><span style="width:100%">' + '<span class="seg" aria-hidden="true">' + D.projetos.map(function (p) { return '<i class="' + (p.prog === 100 ? "ok" : p.est === "rodando" ? "rodando" : "") + '"></i>'; }).join("") + "</span></span></div></div>" +
      '<div class="card kpi"><span class="rot">Visualizações, 14 dias</span><span class="num">' + B.n(k.vis) + '</span><div class="rod"><span class="up">+' + k.delta + '% na semana</span><span class="sparkbox">' + B.spark(k.serie, 120, 44) + "</span></div></div>" +
      '<div class="card kpi"><span class="rot">Retenção média</span><span class="num">' + k.ret + '<small>%</small></span><span class="ringbox">' + B.ring(0, 64, 8, "Retenção média " + k.ret + "%") + '</span><div class="rod">Dos 5 últimos vídeos</div></div></div>';

    h += '<section class="card bloco" aria-labelledby="t-fluxo"><h2 id="t-fluxo">Um Short, do tema ao upload privado</h2><p class="nota">' + k.feitos + " de " + k.nos.length + " etapas prontas, em “A recessão de amizades entre homens”.</p>" +
      '<div class="seg" role="img" aria-label="' + k.feitos + " etapas prontas de " + k.nos.length + '">' + k.nos.map(function (n) { return '<i class="' + n.est + '"></i>'; }).join("") + "</div>" +
      '<ol class="passos">' + k.nos.map(function (n) {
        return '<li class="passo ' + n.est + '"><span class="bolha">' + (n.est === "ok" ? ic("check", 16) : n.t === "gate" && n.est !== "rodando" ? ic("user", 16) : "") + '</span><span><b>' + esc(n.r) + "</b><small>" + esc(n.a || "automático") + "</small></span></li>";
      }).join("") + "</ol></section>";

    var mx = Math.max.apply(null, D.metricas.map(function (m) { return m.vis; }));
    h += '<div class="cols"><section class="card" aria-labelledby="t-prod"><h2 id="t-prod">Produção</h2><p class="nota">Oito vídeos, do mais cedo ao mais perto de publicar.</p><ul class="lista-p">' + D.projetos.map(function (p) {
      var chip = p.est === "erro" ? "bad" : p.est === "espera" ? "warn" : p.est === "rodando" ? "acc" : "";
      var inner = "<b>" + esc(B.nomeProj(p.slug)) + '</b><span class="pill ' + chip + '">' + B.estLabel[p.est] + "</span><small>" + esc(p.tipo) + " · " + esc(p.etapa) + '</small><span class="barra"><i style="width:' + p.prog + '%"></i></span>';
      return "<li>" + (p.est === "espera" || p.est === "erro" ? '<a class="proj ' + p.est + '" href="#/espera">' + inner + "</a>" : '<div class="proj ' + p.est + '">' + inner + "</div>") + "</li>";
    }).join("") + '</ul></section><div class="stack"><section class="card" aria-labelledby="t-agora"><h2 id="t-agora">Agora</h2>' + D.jobs.filter(function (j) { return j.estado === "rodando" || j.estado === "erro"; }).map(function (j) {
      return '<div class="job"><b>' + esc(j.nome) + "</b><p>" + (j.estado === "erro" ? esc(j.log[1]) : esc(j.log[j.log.length - 1])) + " " + B.usd(j.custo) + " de " + B.usd(j.teto) + "</p>" + (j.estado === "erro" ? '<button class="btn sec" type="button" data-retry>' + ic("retry", 18) + "Tentar de novo</button>" : "") + "</div>";
    }).join("") + '</section><section class="card" aria-labelledby="t-desemp"><h2 id="t-desemp">Visualizações por vídeo</h2><div class="vbar">' + D.metricas.map(function (m) {
      return '<div><div class="l"><span>' + esc(m.v) + "</span><span>" + B.n(m.vis) + " · " + m.ret + '%</span></div><div class="b"><i style="width:' + (m.vis / mx * 100).toFixed(0) + '%"></i></div></div>';
    }).join("") + '</div><p class="nota" style="margin-top:14px">Barra: visualizações. Número depois do ponto: retenção.</p></section></div></div>';
    main.innerHTML = h;
    var rg = main.querySelector(".ringbox .rg-val");
    if (rg) { var c = parseFloat(rg.getAttribute("stroke-dasharray").split(" ")[1]); requestAnimationFrame(function () { requestAnimationFrame(function () { rg.setAttribute("stroke-dasharray", (c * k.ret / 100).toFixed(1) + " " + c.toFixed(1)); }); }); }
  }

  function stub(id) {
    var m = B.menu.filter(function (x) { return x.id === id; })[0], s = B.setor(id);
    main.innerHTML = '<header class="cab"><div><h1>' + m.nome + '</h1></div></header><section class="card stubbox"><h2>' + esc(s.chefe ? "Chefe: " + s.chefe : "") + "</h2><p>" + esc(s.desc) + " Esta tela não faz parte da comparação; o menu mostra a estrutura final de 8 grupos.</p><a class=\"btn prim\" href=\"#/espera\">Voltar para Espera você</a></section>";
  }

  function render() {
    var r = B.rota();
    menu();
    (r === "espera" ? espera : r === "canal" ? canal : function () { stub(r); })();
  }

  main.addEventListener("click", function (e) {
    var b;
    if ((b = e.target.closest("[data-sel]"))) { sel = b.dataset.sel; render(); window.scrollTo({ top: 0, behavior: B.suave() }); main.focus({ preventScroll: true }); return; }
    var d = B.pendentes().filter(function (x) { return x.id === sel; })[0];
    if ((b = e.target.closest("[data-acao]")) && d) { B.agir(b, d, +b.dataset.acao, render); return; }
    if ((b = e.target.closest("[data-aj]")) && d) { B.devolver(d, b.dataset.aj, render); return; }
    if (e.target.closest("[data-retry]")) B.toast("Nova rodada do Salah pedida.");
  });
  document.getElementById("tema").addEventListener("click", function () { tema.alternar(); menu(); });
  window.addEventListener("hashchange", function () { render(); window.scrollTo(0, 0); });
  render();
})();
