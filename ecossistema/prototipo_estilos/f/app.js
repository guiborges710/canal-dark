/* Estilo F: Bento colorido. Números enormes, cartões de cor chapada, dock flutuante. */
(function () {
  var app = document.getElementById("app");
  var S = { sel: null, filtro: "todas", motivos: false };
  var esc = B.esc, ic = B.icon;
  var MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];

  function filtrada() { var p = B.pendentes(); return S.filtro === "todas" ? p : p.filter(function (d) { return d.setor === S.filtro; }); }
  function atual() {
    var l = filtrada();
    if (!l.some(function (d) { return d.id === S.sel; })) S.sel = l.length ? l[0].id : null;
    return l.filter(function (d) { return d.id === S.sel; })[0] || null;
  }

  function casca(corpo) {
    var r = B.rota(), n = B.pendentes().length;
    return '<header class="cab"><div class="marca"><i aria-hidden="true">CE</i>Contexto Explica</div><span class="data">Quarta-feira, 11 de ' + MESES[10] + "</span></header>" +
      '<main id="principal" tabindex="-1">' + corpo + '</main><nav class="dock" aria-label="Grupos">' +
      B.menu.map(function (m) { return '<a class="dk" href="#/' + m.id + '" title="' + esc(m.nome) + '" aria-label="' + esc(m.nome) + (m.id === "espera" ? ", " + n + " pendentes" : "") + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 22) + '<span class="nm">' + esc(m.nome) + "</span>" + (m.id === "espera" && n ? '<span class="bdg" aria-hidden="true">' + n + "</span>" : "") + "</a>"; }).join("") + "</nav>";
  }

  /* ---------- Espera você ---------- */
  function decisao(d, folha) {
    var pi = B.principal(d);
    var bts = d.acoes.map(function (a, i) {
      return '<button class="bt ' + (i === pi ? (a.risco ? "risco" : "ok") : (a.risco ? "risco" : "")) + '" type="button" data-ac="' + i + '"' + (a.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (i === pi && !a.risco ? ic("check", 24) : "") + esc(a.r) + "</button>";
    }).join("");
    return '<div class="topl"><span class="cod">' + d.cod + '</span><span class="pill">' + esc(B.setor(d.setor).nome) + "</span>" + (d.urgente ? '<span class="pill" style="background:var(--coral);color:var(--ink)">Urgente</span>' : "") + "</div>" +
      "<h2>" + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>" +
      (d.trava ? '<div class="trava">' + ic("lock", 20) + "<span>" + esc(d.trava) + "</span></div>" : "") +
      '<div class="det">' + d.det + "</div>" +
      (d.edit ? "<label>" + esc(d.edit.campo) + '<textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>' : "") +
      '<div class="btns">' + bts + (d.recusa.length ? '<button class="bt" type="button" data-rec aria-expanded="' + S.motivos + '">Pedir ajuste</button>' : "") + "</div>" +
      '<div class="mots' + (S.motivos ? " on" : "") + '"><span>O que não está certo?</span>' + d.recusa.map(function (m) { return '<button class="mot" type="button" data-mot="' + esc(m) + '">' + esc(m) + "</button>"; }).join("") + "</div>";
  }
  function ligarDec(raiz, d, depois) {
    raiz.querySelectorAll("[data-ac]").forEach(function (b) { b.onclick = function () { B.agir(b, d, +b.dataset.ac, depois); }; });
    raiz.querySelectorAll("[data-mot]").forEach(function (b) { b.onclick = function () { S.motivos = false; B.devolver(d, b.dataset.mot, depois); }; });
    var r = raiz.querySelector("[data-rec]"); if (r) r.onclick = function () { S.motivos = !S.motivos; raiz.querySelector(".mots").classList.toggle("on", S.motivos); r.setAttribute("aria-expanded", S.motivos); };
  }
  function espera() {
    var P = B.pendentes(), urg = P.filter(function (d) { return d.urgente; }).length, trav = P.filter(function (d) { return d.trava; }).length, min = Math.max(1, Math.round(P.length * 1.4));
    var ids = D.setores.map(function (s) { return s.id; }).filter(function (id) { return P.some(function (d) { return d.setor === id; }); });
    var barra = ids.map(function (id) { var n = P.filter(function (d) { return d.setor === id; }).length; return '<i data-s="' + id + '" style="flex:' + n + ';background:var(--b)" title="' + esc(B.setor(id).nome) + ": " + n + '"></i>'; }).join("");
    var chips = ["todas"].concat(ids).map(function (id) {
      var n = id === "todas" ? P.length : P.filter(function (d) { return d.setor === id; }).length;
      return '<button class="cf" type="button" data-fil="' + id + '" aria-pressed="' + (S.filtro === id) + '">' + (id === "todas" ? "Todas" : esc(B.setor(id).nome)) + " <b>" + n + "</b></button>";
    }).join("");
    var d = atual(), L = filtrada();
    var tiles = L.map(function (x) {
      return '<button class="q" type="button" data-s="' + x.setor + '" data-q="' + x.id + '"' + (x.id === S.sel ? ' aria-current="true"' : "") + '><span class="cd"><span>' + x.cod + "</span>" + (x.urgente ? '<span class="urg">Urgente</span>' : "") + '</span><span class="tt">' + esc(x.titulo) + '</span><span class="sb"><span>' + esc(B.setor(x.setor).nome) + "</span><span>Abrir</span></span></button>";
    }).join("");
    var bl = B.bloqueadas.map(function (x) { return '<div class="bl"><span class="mono"><b>' + x.cod + '</b></span><span><b>' + esc(x.titulo) + "</b></span><span>" + ic("lock", 16) + " " + esc(x.trava) + "</span></div>"; }).join("");
    var h = B.historico().slice(0, 4).map(function (x) { return '<li><span class="q2">' + esc(x.q) + "</span><span>" + esc(x.t) + '</span><span class="c2">' + esc(x.c) + "</span></li>"; }).join("");
    return '<h1 class="pag">Espera você</h1>' + leg5() + '<div class="bento">' +
      '<section class="t t-azul a-azul" aria-label="Total pendente"><div class="rot">Decisões pendentes<span class="pill">' + urg + ' urgentes</span></div><div class="num">' + P.length + '</div><div class="leg-t">esperam você. Cada uma destrava um agente.</div><div class="chips-f" role="group" aria-label="Filtrar por setor">' + chips + '</div><div class="setor-bar" style="margin-top:18px" role="img" aria-label="Pendências por setor">' + barra + "</div></section>" +
      '<section class="t t-lima a-lima"><div class="rot">Travam um fluxo</div><div class="num m">' + trav + '</div><div class="leg-t dim">agentes parados esperando você</div></section>' +
      '<section class="t t-sol a-sol"><div class="rot">Para zerar</div><div class="num m">' + min + "<small>min</small></div></section>" +
      '<section class="t t-ink dec a-dec" id="foco" aria-label="Decisão da vez">' + (d ? decisao(d) : '<div class="vazio-t">Fila zerada.<div style="font-size:16px;font-weight:500;color:#b9bddb;margin-top:8px">Os agentes seguem sozinhos.</div></div>') + "</section>" +
      '<h2 class="sec">Na fila<span>' + L.length + " " + (S.filtro === "todas" ? "decisões" : esc(B.setor(S.filtro).nome)) + "</span></h2>" + tiles + bl +
      '<section class="t t-branco hist-t"><div class="rot">Decidido recentemente</div><ul>' + h + "</ul></section></div>";
  }
  function ligarEspera() {
    var d = atual(), f = document.getElementById("foco");
    if (d && f) ligarDec(f, d, render);
    app.querySelectorAll("[data-fil]").forEach(function (b) { b.onclick = function () { S.filtro = b.dataset.fil; S.motivos = false; render(); }; });
    app.querySelectorAll("[data-q]").forEach(function (b) {
      b.onclick = function () {
        S.sel = b.dataset.q; S.motivos = false;
        if (B.estreito(1100)) { var x = atual(), sh = B.sheet(); sh.innerHTML = '<div class="sheet-x"><button type="button" data-fechar aria-label="Fechar">' + ic("close", 20) + '</button></div><div class="t t-ink dec" style="border-radius:0">' + decisao(x, true) + "</div>"; ligarDec(sh, x, function () { sh.close(); render(); }); sh.showModal(); }
        else { render(); window.scrollTo({ top: 0, behavior: B.suave() }); }
      };
    });
  }

  /* ---------- Canal ---------- */
  function leg5() {
    return '<ul class="l5" aria-label="Legenda de status"><li><i class="s s-ok"></i>Deu certo</li><li><i class="s s-erro"></i>Deu erro</li><li><i class="s s-pend"></i>Pendente (espera você)</li><li><i class="s s-back"></i>Em backlog</li><li><i class="s s-run"></i>Rodando</li></ul>';
  }
  function carga(pct, rot) { return '<div class="carga" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '" aria-label="' + esc(rot) + '"><i style="width:' + pct + '%"></i></div>'; }
    function area(v, w, h) {
    var pl = 32, pb = 22, pt = 30, pr = 10, mx = 600, iw = w - pl - pr, ih = h - pb - pt, x = function (i) { return pl + i * iw / (v.length - 1); }, y = function (k) { return pt + ih - k / mx * ih; };
    var pts = v.map(function (k, i) { return x(i).toFixed(1) + " " + y(k).toFixed(1); }), g = "", u = v.length - 1;
    [0, 300, 600].forEach(function (k) { g += '<line class="ar-g" x1="' + pl + '" x2="' + (w - pr) + '" y1="' + y(k) + '" y2="' + y(k) + '"/><text class="ar-t" x="' + (pl - 6) + '" y="' + (y(k) + 4) + '" text-anchor="end">' + k + "</text>"; });
    return '<svg class="area" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="Visualizações por dia nos últimos 14 dias, de ' + v[0] + " a " + v[u] + '"><defs><linearGradient id="gF" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>' + g +
      '<text class="ar-t" x="' + pl + '" y="' + (h - 4) + '">29/10</text><text class="ar-t" x="' + (w - pr) + '" y="' + (h - 4) + '" text-anchor="end">11/11</text><path class="ar-f" d="M' + pts.join("L") + "L" + x(u) + " " + y(0) + "L" + x(0) + " " + y(0) + 'Z"/><path class="ar-l" d="M' + pts.join("L") + '"/><circle class="ar-d" cx="' + x(u) + '" cy="' + y(v[u]) + '" r="6"/><text class="ar-t" style="font-size:14px;font-weight:800;fill:#fff" x="' + (x(u) - 12) + '" y="' + (y(v[u]) - 12) + '" text-anchor="end">' + v[u] + "</text></svg>";
  }
  function canal() {
    var K = B.canalKpis(), P = B.pendentes().filter(function (d) { return d.setor === "canal"; });
    var dots = K.nos.map(function (n) { return '<i class="' + (n.est === "ok" ? "ok" : n.est === "rodando" ? "rodando" : "") + (n.t === "gate" ? " gate" : "") + '" title="' + esc(n.r) + '"></i>'; }).join("");
    var fi = D.fila.map(function (s, i) { return "<div><b>" + esc(B.nomeProj(s)) + "</b><span>" + (i ? "amanhã" : "hoje") + " 18:00</span></div>"; }).join("");
    var pj = D.projetos.map(function (p) {
      return '<article class="pj ' + p.est + '"><span class="etq ' + p.est + '">' + B.estLabel[p.est] + '</span><div class="n">' + esc(B.nomeProj(p.slug)) + '</div><div class="e">' + esc(p.etapa) + " · " + esc(p.tipo) + '</div><div class="p"><span class="tr" role="img" aria-label="' + p.prog + '% concluído"><i style="width:' + p.prog + '%"></i></span><b>' + p.prog + "%</b></div></article>";
    }).join("");
    return '<h1 class="pag">Canal</h1>' + leg5() + '<div class="bento">' +
      '<section class="t t-azul c-views" aria-label="Visualizações"><div class="rot">Visualizações em 14 dias<span class="pill">+' + K.delta + "% vs. 7 dias antes</span></div><div class=\"num\">" + B.n(K.vis) + "</div>" + area(K.serie, 560, 250) + "</section>" +
      '<section class="t t-ink c-acoes"><div class="rot">Ações suas no Canal</div><div class="num m" style="color:var(--lima)">' + P.length + '</div><div class="leg-t dim" style="max-width:none">' + P.filter(function (d) { return d.urgente; }).length + ' urgentes. O Vini bloqueou um texto antes do render.</div><div class="btns" style="margin-top:auto;padding-top:14px;grid-template-columns:1fr"><button class="bt ok" type="button" data-ir="espera">' + ic("check", 22) + "Resolver agora</button></div></section>" +
      '<section class="t t-lima c-ret"><div>' + B.ring(K.ret, 104, 14, "Retenção média " + K.ret + "%") + '</div><div><div class="rot">Retenção média</div><div class="num m">' + K.ret + "<small>%</small></div><div class=\"leg-t dim\">5 vídeos medidos</div></div></section>" +
      '<section class="t t-lilas c-pipe"><div class="rot">Short em andamento</div><div class="num m">' + K.feitos + "<small>de " + K.nos.length + " etapas</small></div><div class=\"leg-t dim\">Agora: o Olise desenha as cenas (cena 3 de 6).</div>" + carga(50, "Olise: cena 3 de 6") + "<div class=\"grid-dots\" role=\"img\" aria-label=\"" + K.feitos + " de " + K.nos.length + ' etapas feitas">' + dots + "</div></section>" +
      '<section class="t t-sol c-cost"><div class="rot">Custo dos jobs</div><div class="num m" style="font-size:clamp(36px,4vw,56px)">' + B.usd(K.custo).replace("US$ ", "") + "<small>US$</small></div><div class=\"leg-t dim\">teto de " + B.usd(K.teto) + '</div><div class="medidor" role="img" aria-label="' + Math.round(K.custo / K.teto * 100) + '% do teto"><i style="width:' + Math.round(K.custo / K.teto * 100) + '%"></i></div></section>' +
      '<section class="t t-coral c-fila"><div class="rot">Fila de postagem<span class="pill">privado</span></div><div class="num m">' + K.fila + '</div><div class="fi">' + fi + "</div></section>" +
      '<h2 class="sec">Todos os vídeos<span>' + D.projetos.length + "</span></h2>" + pj + "</div>";
  }
  function stub(id) {
    var s = B.setor(id);
    return '<h1 class="pag">' + esc(s.nome || id) + '</h1><div class="bento"><div class="stub"><b>Fora desta comparação</b>' + esc(s.desc || "") + " As telas desenhadas neste estilo são Espera você e Canal.</div></div>";
  }

  function render() {
    var r = B.rota();
    app.innerHTML = casca(r === "espera" ? espera() : r === "canal" ? canal() : stub(r));
    if (r === "espera") ligarEspera();
    app.querySelectorAll("[data-ir]").forEach(function (b) { b.onclick = function () { location.hash = "#/" + b.dataset.ir; }; });
    document.title = (B.menu.filter(function (m) { return m.id === r; })[0] || {}).nome + " · Contexto Explica (F)";
  }
  window.addEventListener("hashchange", function () { S.motivos = false; render(); window.scrollTo(0, 0); });
  if (!location.hash) location.hash = "#/espera"; else render();
  if (!app.innerHTML) render();
})();
