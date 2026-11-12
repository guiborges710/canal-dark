/* Estilo D: Command center. Teclado primeiro: Ctrl+K, 1-8 troca de grupo, J/K move, A aprova, R pede ajuste. */
(function () {
  var app = document.getElementById("app");
  var T = B.tema("tema-d", "escuro");
  var S = { sel: null, filtro: "todas", motivos: false, foco: false };
  var esc = B.esc, ic = B.icon;
  var uid = 0;

  function setorChip(id) { return '<span class="set" data-s="' + id + '">' + esc(B.setor(id).nome) + "</span>"; }
  function estTxt(e) { return B.estLabel[e] || e; }

  /* ---------- casca ---------- */
  function contagem(id) { return id === "espera" ? B.pendentes().length : 0; }
  function nav(lado) {
    var r = B.rota();
    return B.menu.map(function (m, i) {
      var c = contagem(m.id);
      return '<a class="nv" href="#/' + m.id + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 18) + '<span class="nome">' + esc(m.nome) + "</span>" + (c ? '<span class="cont" aria-label="' + c + ' pendentes">' + c + "</span>" : "") + (lado ? "<kbd>" + (i + 1) + "</kbd>" : "") + "</a>";
    }).join("");
  }
  function casca(corpo) {
    return '<div class="shell"><aside class="rail"><div class="marca"><span class="logo" aria-hidden="true">CE</span><b>Contexto Explica</b></div>' +
      '<button class="busca" type="button" data-paleta aria-label="Abrir a paleta de comandos">' + '<svg class="ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg><span>Buscar</span><kbd>Ctrl K</kbd></button>' +
      '<nav class="nav" aria-label="Grupos">' + nav(true) + "</nav>" +
      '<div class="rail-fim"><div class="sistema"><i class="pt"></i>PC ligado, 3 servidores no ar</div><button class="tema-b" type="button" data-tema>' + ic(T.get() === "escuro" ? "sun" : "moon", 18) + "<span>Tema " + (T.get() === "escuro" ? "claro" : "escuro") + "</span></button></div></aside>" +
      '<main id="principal" tabindex="-1">' + corpo + '</main><nav class="mobile-bar" aria-label="Grupos">' + nav(false).replace(/<span class="nome">/g, '<span class="nome">') + "</nav></div>";
  }

  /* ---------- métricas ---------- */
  function met(rot, val, sub, extra) { return '<div class="m"><div class="rot">' + rot + '</div><div class="val">' + val + '</div><div class="sub">' + sub + "</div>" + (extra || "") + "</div>"; }

  /* ---------- Espera você ---------- */
  function listaFiltrada() {
    var p = B.pendentes();
    return S.filtro === "todas" ? p : p.filter(function (d) { return d.setor === S.filtro; });
  }
  function selecionada() {
    var l = listaFiltrada();
    if (!l.some(function (d) { return d.id === S.sel; })) S.sel = l.length ? l[0].id : null;
    return l.filter(function (d) { return d.id === S.sel; })[0] || null;
  }
  function detalhe(d) {
    var pi = B.principal(d), ordem = d.acoes.map(function (a, i) { return i; }).sort(function (a, b) { return (a === pi ? -1 : 0) - (b === pi ? -1 : 0); });
    var bts = ordem.map(function (i) {
      var a = d.acoes[i];
      return '<button class="bt' + (i === pi ? " pri" : "") + '" type="button" data-ac="' + i + '"' + (a.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + esc(a.r) + (i === pi ? "<kbd>A</kbd>" : "") + "</button>";
    }).join("");
    var rec = d.recusa.length ? '<button class="bt fant" type="button" data-rec aria-expanded="' + S.motivos + '">Pedir ajuste<kbd>R</kbd></button>' : "";
    return '<div class="det-in"><div class="cab"><span class="cod">' + d.cod + "</span>" + setorChip(d.setor) + (d.urgente ? '<span class="urg">Urgente</span>' : "") + "</div>" +
      "<h2>" + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>" +
      (d.trava ? '<div class="trava">' + ic("lock", 18) + "<span>" + esc(d.trava) + "</span></div>" : "") +
      '<div class="corpo">' + d.det + "</div>" +
      (d.edit ? '<label>' + esc(d.edit.campo) + '<textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>' : "") + "</div>" +
      '<div class="acoes">' + bts + rec + "</div>" +
      '<div class="motivos' + (S.motivos ? " on" : "") + '"><span>O que não está certo?</span>' + d.recusa.map(function (m) { return '<button class="mot" type="button" data-mot="' + esc(m) + '">' + esc(m) + "</button>"; }).join("") + "</div>";
  }
  function ligar(raiz, d, depois) {
    raiz.querySelectorAll("[data-ac]").forEach(function (b) { b.onclick = function () { B.agir(b, d, +b.dataset.ac, depois); }; });
    raiz.querySelectorAll("[data-mot]").forEach(function (b) { b.onclick = function () { S.motivos = false; B.devolver(d, b.dataset.mot, depois); }; });
    var r = raiz.querySelector("[data-rec]");
    if (r) r.onclick = function () { S.motivos = !S.motivos; raiz.querySelector(".motivos").classList.toggle("on", S.motivos); r.setAttribute("aria-expanded", S.motivos); };
  }
  function espera() {
    var P = B.pendentes(), urg = P.filter(function (d) { return d.urgente; }).length, trava = P.filter(function (d) { return d.trava; }).length;
    var feitas = B.historico().filter(function (h) { return h.q === "Agora"; }).length;
    var setores = ["todas"].concat(D.setores.map(function (s) { return s.id; }).filter(function (id) { return P.some(function (d) { return d.setor === id; }); }));
    var fil = setores.map(function (id) {
      var n = id === "todas" ? P.length : P.filter(function (d) { return d.setor === id; }).length;
      return '<button class="fil" type="button" data-fil="' + id + '" aria-pressed="' + (S.filtro === id) + '">' + (id === "todas" ? "Todas" : esc(B.setor(id).nome)) + '<span class="n">' + n + "</span></button>";
    }).join("");
    var L = listaFiltrada(), sel = selecionada();
    var linhas = L.map(function (d) {
      return '<button class="lin" type="button" role="option" data-id="' + d.id + '" aria-selected="' + (d.id === S.sel) + '"><span class="cod">' + d.cod + '</span><span class="tt">' + esc(d.titulo) + '</span><span class="meta">' + setorChip(d.setor) + (d.urgente ? '<span class="urg">Urgente</span>' : "") + "</span></button>";
    }).join("");
    var bl = B.bloqueadas.map(function (d) { return '<div class="lin bloq-l" style="cursor:default"><span class="cod">' + d.cod + '</span><span class="tt">' + esc(d.titulo) + '</span><span class="meta"><span class="trava-m">' + ic("lock", 14) + " " + esc(d.trava) + "</span></span></div>"; }).join("");
    var h = B.historico().map(function (x) { return '<li><span class="q mono">' + esc(x.q) + "</span><span>" + esc(x.t) + '</span><span class="cod">' + esc(x.c) + "</span></li>"; }).join("");
    return '<div class="topo"><div><h1>Espera você</h1><p>Cada item destrava um agente. Resolva de cima para baixo ou aperte <kbd>Ctrl K</kbd> para pular direto.</p></div></div>' +
      leg5() + '<section class="met" aria-label="Resumo">' +
      met("Esperando você", '<span>' + P.length + "</span>", "<b>" + trava + "</b> travam um fluxo", '<div class="bar-mini"><i style="width:' + Math.round(P.length / (P.length + 4 + feitas) * 100) + '%"></i></div>') +
      met("Urgentes", '<span>' + urg + "</span>", '<span class="' + (urg ? "down" : "up") + '">' + (urg ? "resolver primeiro" : "nenhuma") + "</span>") +
      met("Resolvidas hoje", '<span>' + (3 + feitas) + "</span>", '<span class="up">+' + feitas + "</span> nesta sessão", B.spark([1, 2, 2, 3, 3, 4 + feitas], 70, 26)) +
      met("Tempo médio de resposta", '<span>14</span><small>min</small>', '<span class="up">-6 min</span> vs. semana passada', B.spark([31, 26, 22, 20, 17, 14], 70, 26)) +
      "</section>" +
      '<div class="filtros" role="group" aria-label="Filtrar por setor">' + fil + "</div>" +
      '<div class="duas"><div><div class="lista" role="listbox" aria-label="Decisões pendentes"><h2><span>Pendentes</span><span class="mono">' + L.length + "</span></h2>" + (linhas || '<div class="vazio"><b>Fila zerada.</b>Nada espera você neste filtro.</div>') + "</div>" +
      (bl ? '<div class="lista" style="margin-top:12px"><h2><span>Bloqueadas por um agente</span><span class="mono">' + B.bloqueadas.length + "</span></h2>" + bl + "</div>" : "") + "</div>" +
      '<div class="det pane" id="painel">' + (sel ? detalhe(sel) : '<div class="vazio"><b>Tudo em dia.</b>Os agentes seguem sozinhos até a próxima decisão.</div>') + "</div></div>" +
      '<section class="hist"><h2 style="margin:0;padding:12px 16px;font-size:12.5px;font-weight:600;color:var(--mudo);border-bottom:1px solid var(--linha)">Decidido recentemente</h2><ul>' + h + "</ul></section>";
  }
  function ligarEspera() {
    app.querySelectorAll("[data-fil]").forEach(function (b) { b.onclick = function () { S.filtro = b.dataset.fil; S.motivos = false; render(); }; });
    app.querySelectorAll(".lin[data-id]").forEach(function (b) {
      b.onclick = function () {
        S.sel = b.dataset.id; S.motivos = false;
        if (B.estreito(1100)) abrirFolha(); else render();
      };
    });
    var d = selecionada(), p = document.getElementById("painel");
    if (d && p) ligar(p, d, render);
    if (S.foco) { S.foco = false; var el = app.querySelector('.lin[data-id="' + S.sel + '"]'); if (el) { el.focus({ preventScroll: true }); el.scrollIntoView({ block: "nearest" }); } }
  }
  function abrirFolha() {
    var d = selecionada(); if (!d) return;
    var f = B.sheet();
    f.innerHTML = '<div class="sheet-x"><button type="button" data-fechar aria-label="Fechar">' + ic("close", 18) + '</button></div><div class="det">' + detalhe(d) + "</div>";
    ligar(f, d, function () { f.close(); render(); });
    f.showModal();
  }

  /* ---------- Canal ---------- */
  function leg5() {
    return '<ul class="l5" aria-label="Legenda de status"><li><i class="s s-ok"></i>Deu certo</li><li><i class="s s-erro"></i>Deu erro</li><li><i class="s s-pend"></i>Pendente (espera você)</li><li><i class="s s-back"></i>Em backlog</li><li><i class="s s-run"></i>Rodando</li></ul>';
  }
  function carga(pct, rot) { return '<div class="carga" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '" aria-label="' + esc(rot) + '"><i style="width:' + pct + '%"></i></div>'; }
    function area(v, w, h) {
    var id = "gD", pl = 34, pb = 20, pt = 24, pr = 10, mx = 600, iw = w - pl - pr, ih = h - pb - pt, x = function (i) { return pl + i * iw / (v.length - 1); }, y = function (k) { return pt + ih - k / mx * ih; };
    var pts = v.map(function (k, i) { return x(i).toFixed(1) + " " + y(k).toFixed(1); }), g = "";
    [0, 200, 400, 600].forEach(function (k) { g += '<line class="ar-g" x1="' + pl + '" x2="' + (w - pr) + '" y1="' + y(k) + '" y2="' + y(k) + '"/><text class="ar-t" x="' + (pl - 6) + '" y="' + (y(k) + 4) + '" text-anchor="end">' + k + "</text>"; });
    var dias = ["29/10", "", "", "", "", "", "04/11", "", "", "", "", "", "", "11/11"], t = "";
    dias.forEach(function (s, i) { if (s) t += '<text class="ar-t" x="' + x(i) + '" y="' + (h - 4) + '" text-anchor="' + (i === 0 ? "start" : i === dias.length - 1 ? "end" : "middle") + '">' + s + "</text>"; });
    var u = v.length - 1;
    return '<svg class="area" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="Visualizações por dia nos últimos 14 dias: de ' + v[0] + " a " + v[u] + '"><defs><linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--ac)" stop-opacity=".35"/><stop offset="1" stop-color="var(--ac)" stop-opacity="0"/></linearGradient></defs>' + g + t +
      '<path class="ar-f" d="M' + pts.join("L") + "L" + x(u) + " " + y(0) + "L" + x(0) + " " + y(0) + 'Z"/><path class="ar-l" d="M' + pts.join("L") + '"/><circle class="ar-d" cx="' + x(u) + '" cy="' + y(v[u]) + '" r="4.5"/><text class="ar-t" style="fill:var(--tx);font-weight:600" x="' + (x(u) - 10) + '" y="' + (y(v[u]) - 10) + '" text-anchor="end">' + v[u] + "</text></svg>";
  }
  function canal() {
    var K = B.canalKpis(), j = D.jobs.filter(function (x) { return /Olise|Salah|Vitinho/.test(x.nome); });
    var fases = B.fases.map(function (f) {
      var ns = f.ids.map(function (id) { return K.nos.filter(function (n) { return n.id === id; })[0]; });
      var ok = ns.filter(function (n) { return n.est === "ok"; }).length;
      return '<div class="fase"><h3><span>' + f.nome + '</span><span class="mono">' + ok + "/" + ns.length + '</span></h3><ol>' + ns.map(function (n) {
        var est = n.est === "ok" ? "ok" : n.est === "rodando" ? "rodando" : "bloq";
        return '<li class="' + (est === "rodando" ? "rod" : "") + '"><i class="st ' + est + '"></i><span class="nm" title="' + esc(n.r + (n.a ? " · " + n.a : "")) + '">' + esc(n.r) + "</span>" + (n.t === "gate" ? '<span class="gate">você</span>' : "") + "</li>";
      }).join("") + "</ol></div>";
    }).join("");
    var linhas = D.projetos.map(function (p) {
      return '<tr><td><div class="nm">' + esc(B.nomeProj(p.slug)) + '</div><div class="tp">' + esc(p.tipo) + " · " + p.ver + "</div></td><td>" + esc(p.etapa) + '</td><td><div class="pg' + (p.est === "rodando" ? " run" : "") + '"><span class="tr"><i style="width:' + p.prog + '%"></i></span><b>' + p.prog + '%</b></div></td><td><span class="ebd ' + p.est + '">' + estTxt(p.est) + '</span></td><td><button class="abre" type="button" data-abre="' + esc(B.nomeProj(p.slug)) + '" aria-label="Abrir ' + esc(B.nomeProj(p.slug)) + '">Abrir</button></td></tr>';
    }).join("");
    var jobs = j.map(function (x) {
      var pc = x.teto ? Math.round(x.custo / x.teto * 100) : 0;
      return '<div class="job"><div class="l1"><b>' + esc(x.nome) + '</b><span class="ebd ' + (x.estado === "ok" ? "ok" : x.estado === "erro" ? "erro" : "rodando") + '">' + (x.estado === "ok" ? "Concluído" : x.estado === "erro" ? "Com erro" : "Rodando") + '</span></div>' + (x.estado === "rodando" ? carga(50, "Olise: cena 3 de 6") + '<div class="mono pequeno mudo">cena 3 de 6 · 50%</div>' : "") + '<div class="tbar' + (x.estado === "erro" ? " err" : pc > 60 ? " alto" : "") + '" role="img" aria-label="Custo ' + pc + '% do teto"><i style="width:' + pc + '%"></i></div><div class="nums"><span><b>' + B.n(x.tok) + "</b> tokens</span><span><b>" + B.usd(x.custo) + "</b> de " + B.usd(x.teto) + "</span><span>" + x.modelo + " · " + x.ini + "</span></div></div>";
    }).join("");
    var fila = D.fila.map(function (s, i) { return '<div><span class="n">' + (i + 1) + "</span><span>" + esc(B.nomeProj(s)) + '</span><span class="quando">' + (i ? "amanhã 18:00" : "hoje 18:00") + "</span></div>"; }).join("");
    return '<div class="topo"><div><h1>Canal</h1><p>Contexto Explica, Shorts de 30 a 60 s. De Bruyne coordena; cada etapa com gate espera você.</p></div><button class="bt pri" type="button" data-ir="espera">' + K.espera + " esperam você" + "<kbd>1</kbd></button></div>" +
      leg5() + '<section class="met" aria-label="Resumo do canal">' +
      met("Visualizações em 14 dias", "<span>" + B.n(K.vis) + "</span>", '<span class="up">+' + K.delta + "%</span> vs. 7 dias antes", B.spark(K.serie, 70, 26)) +
      met("Retenção média", "<span>" + K.ret + "</span><small>%</small>", "5 vídeos medidos") +
      met("Em produção", "<span>" + K.ativos + "</span><small>de " + K.total + "</small>", K.feitos + " de " + K.nos.length + " etapas do atual") +
      met("Custo dos jobs", "<span>" + B.usd(K.custo).replace("US$ ", "") + "</span><small>US$</small>", "teto " + B.usd(K.teto), '<div class="bar-mini"><i style="width:' + Math.round(K.custo / K.teto * 100) + '%"></i></div>') +
      met("Fila de postagem", "<span>" + K.fila + "</span>", "próximo: hoje 18:00, privado") +
      "</section>" +
      '<div class="gr"><section class="bloc"><h2><span>Visualizações por dia</span><span class="d mono">últimos 14 dias</span></h2><div class="corpo2">' + area(K.serie, 640, 230) + '</div></section>' +
      '<section class="bloc"><h2><span>Consumo dos jobs de agentes</span><span class="d mono">hoje</span></h2><div class="jobs">' + jobs + "</div></section></div>" +
      '<section class="bloc" style="margin-bottom:16px"><h2><span>Pipeline do Short atual</span><span class="d">a recessão de amizades entre homens</span></h2><div class="fases">' + fases + '</div><div class="leg"><span><i class="st ok"></i>feito</span><span><i class="st rodando"></i>rodando</span><span><i class="st bloq"></i>aguarda</span><span><span class="gate">você</span>gate de aprovação</span></div></section>' +
      '<div class="gr gr2"><section class="bloc"><h2><span>Projetos</span><span class="d mono">' + D.projetos.length + "</span></h2><table class=\"proj\"><thead><tr><th>Vídeo</th><th>Etapa</th><th>Progresso</th><th>Estado</th><th><span class=\"sr\"></span></th></tr></thead><tbody>" + linhas + '</tbody></table></section>' +
      '<section class="bloc"><h2><span>Fila de postagem</span><span class="d mono">privado</span></h2><div class="fila">' + fila + '</div></section></div>';
  }
  function stub(id) {
    var s = B.setor(id);
    return '<div class="topo"><div><h1>' + esc(s.nome || id) + "</h1><p>Chefe: " + esc(s.chefe || "Guilherme") + '</p></div></div><div class="cartao-stub"><b>Fora desta comparação</b>' + esc(s.desc || "") + " As telas desenhadas neste estilo são Espera você e Canal.</div>";
  }

  /* ---------- render ---------- */
  function render() {
    var r = B.rota();
    app.innerHTML = casca(r === "espera" ? espera() : r === "canal" ? canal() : stub(r));
    app.querySelectorAll("[data-paleta]").forEach(function (b) { b.onclick = paleta; });
    app.querySelectorAll("[data-tema]").forEach(function (b) { b.onclick = function () { T.alternar(); render(); }; });
    app.querySelectorAll("[data-ir]").forEach(function (b) { b.onclick = function () { location.hash = "#/" + b.dataset.ir; }; });
    app.querySelectorAll("[data-abre]").forEach(function (b) { b.onclick = function () { B.toast("No protótipo completo abre o projeto: " + b.dataset.abre); }; });
    if (r === "espera") ligarEspera();
    document.title = (B.menu.filter(function (m) { return m.id === r; })[0] || {}).nome + " · Contexto Explica (D)";
  }
  window.addEventListener("hashchange", function () { S.motivos = false; render(); window.scrollTo(0, 0); });

  /* ---------- paleta Ctrl+K ---------- */
  var pal, palIdx = 0, palItens = [];
  function comandos() {
    var c = B.menu.map(function (m, i) { return { g: "Ir para", t: m.nome, k: "go", run: function () { location.hash = "#/" + m.id; }, tecla: String(i + 1) }; });
    B.pendentes().forEach(function (d) { c.push({ g: "Decisões", t: d.titulo, cod: d.cod, run: function () { S.filtro = "todas"; S.sel = d.id; if (B.rota() !== "espera") location.hash = "#/espera"; else render(); } }); });
    var s = selecionada();
    if (s && s.acoes.length) { var a = s.acoes[B.principal(s)]; c.unshift({ g: "Ação", t: a.r + " (" + s.cod + ")", tecla: "A", run: function () { var b = document.querySelector('#painel [data-ac="' + B.principal(s) + '"]'); if (b) b.click(); else B.agir(document.createElement("button"), s, B.principal(s), render); } }); }
    c.push({ g: "Ação", t: "Alternar tema claro e escuro", run: function () { T.alternar(); render(); } });
    return c;
  }
  function paleta() {
    if (!pal) {
      pal = document.createElement("dialog"); pal.className = "pal"; pal.setAttribute("aria-label", "Paleta de comandos");
      pal.innerHTML = '<div class="pal-in"><svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/></svg><input type="text" role="combobox" aria-expanded="true" aria-controls="pal-l" aria-label="Buscar comando, decisão ou grupo" placeholder="Digite um grupo, um código (C5) ou uma ação" autocomplete="off"><kbd>Esc</kbd></div><div class="pal-l" id="pal-l" role="listbox"></div><div class="pal-r"><span><kbd>↑</kbd> <kbd>↓</kbd> navegar</span><span><kbd>Enter</kbd> executar</span></div>';
      document.body.appendChild(pal);
      var inp = pal.querySelector("input");
      inp.addEventListener("input", function () { palIdx = 0; filtrar(); });
      inp.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown") { e.preventDefault(); palIdx = Math.min(palIdx + 1, palItens.length - 1); marcar(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); palIdx = Math.max(palIdx - 1, 0); marcar(); }
        else if (e.key === "Enter") { e.preventDefault(); exec(palIdx); }
      });
      pal.addEventListener("click", function (e) { if (e.target === pal) pal.close(); });
    }
    pal.querySelector("input").value = ""; palIdx = 0; filtrar(); pal.showModal(); pal.querySelector("input").focus();
  }
  function filtrar() {
    var q = pal.querySelector("input").value.trim().toLowerCase(), all = comandos();
    palItens = all.filter(function (c) { return !q || (c.t + " " + (c.cod || "") + " " + c.g).toLowerCase().indexOf(q) >= 0; }).slice(0, 14);
    var h = "", g = "";
    palItens.forEach(function (c, i) {
      if (c.g !== g) { g = c.g; h += '<div class="pal-g">' + g + "</div>"; }
      h += '<button class="pal-i" type="button" role="option" id="pi' + i + '" data-i="' + i + '" aria-selected="' + (i === palIdx) + '">' + (c.cod ? '<span class="cod">' + c.cod + "</span>" : "") + '<span class="t">' + esc(c.t) + "</span>" + (c.tecla ? "<kbd>" + c.tecla + "</kbd>" : "") + "</button>";
    });
    var l = pal.querySelector(".pal-l");
    l.innerHTML = h || '<div class="pal-vz">Nada encontrado. Tente o código da decisão, como C5.</div>';
    l.querySelectorAll("[data-i]").forEach(function (b) { b.onclick = function () { exec(+b.dataset.i); }; });
    marcar();
  }
  function marcar() {
    pal.querySelectorAll(".pal-i").forEach(function (b, i) { b.setAttribute("aria-selected", i === palIdx); if (i === palIdx) b.scrollIntoView({ block: "nearest" }); });
    var a = pal.querySelector("#pi" + palIdx); if (a) pal.querySelector("input").setAttribute("aria-activedescendant", "pi" + palIdx);
  }
  function exec(i) { var c = palItens[i]; if (!c) return; pal.close(); c.run(); }

  /* ---------- teclado ---------- */
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); paleta(); return; }
    var t = e.target, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || e.ctrlKey || e.metaKey || e.altKey || document.querySelector("dialog[open]")) return;
    var k = e.key.toLowerCase();
    if (/^[1-8]$/.test(k)) { location.hash = "#/" + B.menu[+k - 1].id; return; }
    if (k === "/") { e.preventDefault(); paleta(); return; }
    if (B.rota() !== "espera") return;
    var L = listaFiltrada(), i = L.map(function (d) { return d.id; }).indexOf(S.sel);
    if ((k === "j" || e.key === "ArrowDown") && tag !== "BUTTON" || (k === "j")) { if (L.length) { S.sel = L[Math.min(i + 1, L.length - 1)].id; S.motivos = false; S.foco = true; render(); e.preventDefault(); } }
    else if (k === "k") { if (L.length) { S.sel = L[Math.max(i - 1, 0)].id; S.motivos = false; S.foco = true; render(); } }
    else if (k === "a") { var b = document.querySelector("#painel .bt.pri"); if (b) b.click(); }
    else if (k === "r") { var r = document.querySelector("#painel [data-rec]"); if (r) r.click(); }
  });

  if (!location.hash) location.hash = "#/espera"; else render();
  if (!app.innerHTML) render();
})();
