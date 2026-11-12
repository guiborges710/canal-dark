/* Estilo E: Action center. Uma decisão por vez, com o trabalho do agente à mostra; conversa embutida no rodapé. */
(function () {
  var app = document.getElementById("app");
  var T = B.tema("tema-e", "claro");
  var S = { i: 0, motivos: false, pausado: false, resp: "" };
  var esc = B.esc, ic = B.icon;

  /* "Mostrar o trabalho": de onde veio, confiança, custo e o que mudou. Valores ilustrativos. */
  var EVID = {
    c5: { ag: "Vini", ft: ["roteiro.txt, linha 4", "metadados.json, título", "notas.md (4 fontes)"], cf: 94, us: 0.06, mud: "2 apontamentos novos desde a v1." },
    c1: { ag: "Courtois", ft: ["notas.md: 4 fontes conferidas", "angulo.md", "roteiro.txt v2"], cf: 96, us: 0.07, mud: "Gancho trocado e fecho reescrito." },
    c8: { ag: "Vini", ft: ["CONFORMIDADE.md", "auditoria.md", "video.mp4 (47 s)"], cf: 91, us: 0.0, mud: "Render novo, sem ressalvas de metadados." },
    c11: { ag: "Memphis", ft: ["fila_postagem.txt", "auditoria.md", "thumbnail.jpg"], cf: 98, us: 0.0, mud: "Primeiro da fila; data sugerida hoje 18:00." },
    c2: { ag: "Raphinha", ft: ["componentes/aprendizados.md", "3 desenhos novos"], cf: 78, us: 0.31, mud: "Regra nova: celular sempre com texto." },
    c3: { ag: "Olise", ft: ["previa.jpg (6 cenas)", "direcao_viral.md"], cf: 88, us: 0.42, mud: "Nenhum elemento cobre boneco nem texto." },
    c10: { ag: "Seedorf", ft: ["prompt_thumbnail.txt", "metadados.json"], cf: 90, us: 0.04, mud: "Prompt novo para o ChatGPT." },
    l1: { ag: "Rivaldo", ft: ["triagem.json", "transcrição (Whisper local)"], cf: 72, us: 0.09, mud: "Nota 38, abaixo do mínimo de 45." },
    l3: { ag: "Zidane", ft: ["momentos.json", "transcrição, 14:20 a 14:58"], cf: 83, us: 0.11, mud: "Gancho, fecho e CTA escritos." },
    p1: { ag: "Zico", ft: ["qa/PROG-013.md", "revisoes/PROG-013.md"], cf: 95, us: 0.52, mud: "5 de 5 critérios atendidos." },
    a3: { ag: "Ronaldo", ft: ["google_pessoal.py", "token com validade de 7 dias"], cf: 99, us: 0.01, mud: "Vence em 2 dias." }
  };
  function evid(d) { return EVID[d.id] || { ag: B.setor(d.setor).chefe || "Agente", ft: ["Registro do fluxo do setor " + B.setor(d.setor).nome], cf: 90, us: 0.03, mud: "Pedido novo desde ontem." }; }
  function ini(n) { return esc((n || "?").charAt(0)); }
  function pend() { return B.pendentes(); }
  function atual() { var P = pend(); if (S.i >= P.length) S.i = 0; return P[S.i] || null; }

  /* ---------- casca ---------- */
  function casca(corpo) {
    var r = B.rota(), n = pend().length;
    return '<header class="topbar"><div class="marca"><i aria-hidden="true">CE</i><span>Contexto Explica</span></div><nav class="pilulas" aria-label="Grupos">' +
      B.menu.map(function (m) { return '<a class="pil" href="#/' + m.id + '"' + (m.id === r ? ' aria-current="page"' : "") + ">" + ic(m.ic, 18) + esc(m.nome) + (m.id === "espera" && n ? '<span class="n">' + n + "</span>" : "") + "</a>"; }).join("") +
      '</nav><button class="tb" type="button" data-tema aria-label="Mudar para tema ' + (T.get() === "escuro" ? "claro" : "escuro") + '">' + ic(T.get() === "escuro" ? "sun" : "moon", 20) + "</button></header>" +
      '<main id="principal" tabindex="-1">' + corpo + "</main>" + conversa();
  }

  /* ---------- decisão em foco ---------- */
  function trabalho(d) {
    var e = evid(d);
    return '<details class="trab"><summary><span class="avatar" aria-hidden="true">' + ini(e.ag) + '</span>Mostrar o trabalho de ' + esc(e.ag) + '<span class="conf">' + e.cf + '% de confiança</span></summary><div class="trab-in"><dl>' +
      "<dt>De onde veio</dt><dd><ul>" + e.ft.map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("") + "</ul></dd>" +
      '<dt>Confiança</dt><dd><div class="cfb"><span class="tr"><i style="width:' + e.cf + '%"></i></span><b>' + e.cf + "%</b></div></dd>" +
      "<dt>O que mudou</dt><dd>" + esc(e.mud) + "</dd><dt>Custo</dt><dd>" + (e.us ? B.usd(e.us) : "US$ 0,00, sem gasto") + "</dd></dl></div></details>";
  }
  function acoes(d, comPular) {
    var pi = B.principal(d), a = d.acoes;
    var bts = a.map(function (x, i) {
      var cl = i === pi ? (x.risco ? "risco" : "ok") : (x.risco ? "risco" : "");
      return '<button class="bt ' + cl + '" type="button" data-ac="' + i + '"' + (x.k === "copiar" ? ' data-copia="' + esc(d.titulo) + '"' : "") + ">" + (i === pi && !x.risco ? ic("check", 22) : "") + esc(x.r) + "</button>";
    });
    var ord = bts.length ? bts : [];
    return '<div class="acao-b">' + ord.join("") + (d.recusa.length ? '<button class="bt ajuste" type="button" data-rec aria-expanded="' + S.motivos + '">Pedir ajuste</button>' : "") + "</div>" +
      '<div class="mots' + (S.motivos ? " on" : "") + '"><span>O que não está certo?</span>' + d.recusa.map(function (m) { return '<button class="mot" type="button" data-mot="' + esc(m) + '">' + esc(m) + "</button>"; }).join("") + "</div>" +
      (comPular ? '<div class="seg-b"><button class="lk" type="button" data-pular>Deixar para depois</button><button class="lk" type="button" data-parar>Pausar os agentes</button></div>' : "");
  }
  function foco(d, pos, total, folha) {
    return '<article class="cartao foco-c" aria-label="Decisão em foco"><div class="pos"><span class="passo">Decisão ' + pos + " de " + total + '<span class="pbar" aria-hidden="true"><i style="width:' + Math.round(pos / total * 100) + '%"></i></span></span><span class="etqs">' + (d.urgente ? '<span class="etq urg">Urgente</span>' : "") + '<span class="etq set">' + esc(B.setor(d.setor).nome) + '</span><span class="etq">' + d.cod + "</span></span></div>" +
      '<div class="corpo-d"><h2>' + esc(d.titulo) + '</h2><p class="ctx">' + esc(d.ctx) + "</p>" +
      (d.trava ? '<div class="efeito"><b>O que trava</b><span>' + esc(d.trava) + "</span></div>" : "") + '<div class="det-t">' + d.det + "</div></div>" +
      trabalho(d) +
      (d.edit ? '<label class="edit-l">' + esc(d.edit.campo) + '<textarea placeholder="' + esc(d.edit.dica) + '"></textarea></label>' : "") +
      acoes(d, !folha) + "</article>";
  }
  function ligar(raiz, d, depois) {
    raiz.querySelectorAll("[data-ac]").forEach(function (b) { b.onclick = function () { B.agir(b, d, +b.dataset.ac, depois); }; });
    raiz.querySelectorAll("[data-mot]").forEach(function (b) { b.onclick = function () { S.motivos = false; B.devolver(d, b.dataset.mot, depois); }; });
    var r = raiz.querySelector("[data-rec]"); if (r) r.onclick = function () { S.motivos = !S.motivos; raiz.querySelector(".mots").classList.toggle("on", S.motivos); r.setAttribute("aria-expanded", S.motivos); };
    var p = raiz.querySelector("[data-pular]"); if (p) p.onclick = function () { S.i = S.i + 1; S.motivos = false; render(); };
    var q = raiz.querySelector("[data-parar]"); if (q) q.onclick = function () { S.pausado = !S.pausado; B.toast(S.pausado ? "Agentes pausados. Nada novo começa até você retomar." : "Agentes retomados."); render(); };
  }

  /* ---------- atividade ---------- */
  var ATIV = [
    { ag: "Olise", c: "c", q: "13:03", t: "escreve a cena 1 de 6 de \"a recessão de amizades entre homens\"", us: 0.21, tok: 18400, log: D.jobs[0].log },
    { ag: "Salah", c: "e", q: "12:41", t: "não conseguiu baixar a fonte: o site recusou (erro 403)", us: 0.05, tok: 4200, log: D.jobs[2].log },
    { ag: "Vitinho", c: "o", q: "09:19", t: "concluiu o relatório semanal", us: 0.38, tok: 31200, log: D.jobs[3].log },
    { ag: "Courtois", c: "o", q: "08:52", t: "conferiu o roteiro v2 contra as 4 fontes e não achou problema", us: 0.07, cf: 96 },
    { ag: "Ronaldo", c: "o", q: "08:30", t: "enviou o resumo diário no Telegram", us: 0.01 }
  ];
  function atividade(max) {
    return '<section class="cartao"><h2><span>O que os agentes fizeram</span><span class="d">hoje</span></h2><div class="ctrl"><span class="estado' + (S.pausado ? " pausa" : "") + '"><i></i>' + (S.pausado ? "Pausados por você" : "3 agentes ativos") + '</span><button class="bt peq" type="button" data-parar>' + (S.pausado ? "Retomar" : "Pausar os agentes") + '</button></div><ol class="tl">' +
      ATIV.slice(0, max || 5).map(function (a) {
        return '<li><span class="avatar st-' + a.c + '" aria-hidden="true">' + ini(a.ag) + '</span><div class="tx"><b>' + esc(a.ag) + "</b> " + esc(a.t) + '<div class="meta"><span>' + a.q + "</span><span>" + B.usd(a.us) + "</span>" + (a.tok ? "<span>" + B.n(a.tok) + " tokens</span>" : "") + (a.cf ? '<span class="cf">' + a.cf + "% de confiança</span>" : "") + "</div>" +
          (a.c === "c" ? carga(50, "Olise: cena 3 de 6") + '<div class="meta"><span>cena 3 de 6 · 50%</span></div>' : "") + (a.log ? '<details><summary>Ver o passo a passo</summary><div class="log">' + a.log.map(function (l) { return "<span>" + esc(l) + "</span>"; }).join("") + "</div></details>" : "") + "</div></li>";
      }).join("") + "</ol></section>";
  }

  /* ---------- Espera você ---------- */
  function espera() {
    var P = pend(), d = atual(), urg = P.filter(function (x) { return x.urgente; }).length, trav = P.filter(function (x) { return x.trava; }).length;
    var min = Math.max(1, Math.round(P.length * 1.4));
    var dep = P.map(function (x, i) { return { x: x, i: i }; }).filter(function (o) { return o.i !== S.i; }).slice(0, 7);
    return '<section class="faixa"><div><h1>' + (P.length ? "Bom dia, Guilherme. " + P.length + " decisões esperam você." : "Tudo em dia. Os agentes seguem sozinhos.") + "</h1><p>" + (P.length ? "Decida uma de cada vez. Cada resposta destrava um agente na hora." : "A próxima decisão aparece aqui assim que um agente precisar de você.") + '</p></div><div class="chips" aria-label="Resumo">' +
      '<div class="mt"><span class="v">' + P.length + '</span><span class="l">esperam você</span></div>' +
      '<div class="mt"><span class="v">' + urg + '</span><span class="l">urgentes</span></div>' +
      '<div class="mt"><span class="v">' + trav + '</span><span class="l">travam um fluxo</span></div>' +
      '<div class="mt"><span class="v">' + min + "<small>min</small></span><span class=\"l\">para zerar a fila</span>" + B.spark([34, 30, 27, 24, 21, 19, min], 120, 26) + "</div></div></section>" +
      leg5() + '<div class="cols"><div class="col" id="coluna">' + (d ? '<div id="foco">' + foco(d, S.i + 1, P.length) + "</div>" : '<div class="vz"><b>Fila zerada.</b>Nada espera você agora.</div>') +
      (dep.length ? '<div><h3 class="tt" style="margin-top:6px"><span>Depois</span><span class="mudo">' + dep.length + ' de ' + (P.length - 1) + '</span></h3><div class="depois">' + dep.map(function (o) { var x = o.x; return '<button class="dep" type="button" data-ir="' + o.i + '"><span class="cod">' + x.cod + '</span><span class="t">' + esc(x.titulo) + "</span>" + (x.urgente ? '<span class="etq urg">Urgente</span>' : '<span class="etq set">' + esc(B.setor(x.setor).nome) + "</span>") + '<span class="ir">' + ic("chev", 18) + "</span></button>"; }).join("") + "</div></div>" : "") + "</div>" +
      '<aside class="col" aria-label="Atividade">' + atividade(5) + "</aside></div>";
  }
  function ligarEspera() {
    var d = atual(), f = document.getElementById("foco");
    if (d && f) ligar(f, d, render);
    var a = app.querySelector(".tl"); app.querySelectorAll("[data-parar]").forEach(function (b) { if (!f || !f.contains(b)) b.onclick = function () { S.pausado = !S.pausado; B.toast(S.pausado ? "Agentes pausados. Nada novo começa até você retomar." : "Agentes retomados."); render(); }; });
    app.querySelectorAll("[data-ir]").forEach(function (b) {
      b.onclick = function () {
        S.i = +b.dataset.ir; S.motivos = false;
        if (B.estreito(700)) { var sh = B.sheet(), x = atual(); sh.innerHTML = '<div class="sheet-x"><button type="button" data-fechar aria-label="Fechar">' + ic("close", 20) + "</button></div>" + foco(x, S.i + 1, pend().length, true); ligar(sh, x, function () { sh.close(); render(); }); sh.showModal(); }
        else { render(); var el = document.getElementById("foco"); if (el) el.scrollIntoView({ behavior: B.suave(), block: "start" }); }
      };
    });
  }

  /* ---------- Canal ---------- */
  function leg5() {
    return '<ul class="l5" aria-label="Legenda de status"><li><i class="s s-ok"></i>Deu certo</li><li><i class="s s-erro"></i>Deu erro</li><li><i class="s s-pend"></i>Pendente (espera você)</li><li><i class="s s-back"></i>Em backlog</li><li><i class="s s-run"></i>Rodando</li></ul>';
  }
  function carga(pct, rot) { return '<div class="carga" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '" aria-label="' + esc(rot) + '"><i style="width:' + pct + '%"></i></div>'; }
    function area(v, w, h) {
    var pl = 30, pb = 22, pt = 26, pr = 12, mx = 600, iw = w - pl - pr, ih = h - pb - pt, x = function (i) { return pl + i * iw / (v.length - 1); }, y = function (k) { return pt + ih - k / mx * ih; };
    var pts = v.map(function (k, i) { return x(i).toFixed(1) + " " + y(k).toFixed(1); }), g = "", u = v.length - 1;
    [0, 300, 600].forEach(function (k) { g += '<line class="ar-g" x1="' + pl + '" x2="' + (w - pr) + '" y1="' + y(k) + '" y2="' + y(k) + '"/><text class="ar-t" x="' + (pl - 6) + '" y="' + (y(k) + 4) + '" text-anchor="end">' + k + "</text>"; });
    return '<svg class="area" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="Visualizações por dia nos últimos 14 dias: de ' + v[0] + " a " + v[u] + '"><defs><linearGradient id="gE" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--prim)" stop-opacity=".28"/><stop offset="1" stop-color="var(--prim)" stop-opacity="0"/></linearGradient></defs>' + g +
      '<text class="ar-t" x="' + pl + '" y="' + (h - 4) + '">29/10</text><text class="ar-t" x="' + (w - pr) + '" y="' + (h - 4) + '" text-anchor="end">11/11</text><path class="ar-f" d="M' + pts.join("L") + "L" + x(u) + " " + y(0) + "L" + x(0) + " " + y(0) + 'Z"/><path class="ar-l" d="M' + pts.join("L") + '"/><circle class="ar-d" cx="' + x(u) + '" cy="' + y(v[u]) + '" r="5"/><text class="ar-t" style="fill:var(--tx);font-weight:700;font-size:13px" x="' + (x(u) - 10) + '" y="' + (y(v[u]) - 10) + '" text-anchor="end">' + v[u] + "</text></svg>";
  }
  function canal() {
    var K = B.canalKpis(), P = pend().filter(function (x) { return x.setor === "canal"; }), urg = P.filter(function (x) { return x.urgente; }).length;
    var acs = P.map(function (x) {
      var i = B.principal(x), a = x.acoes[i];
      return '<div class="ac-c' + (x.urgente ? " urg" : "") + '"><div class="t">' + esc(x.titulo) + '</div><div class="s">' + x.cod + (x.trava ? " · " + esc(x.trava) : "") + "</div>" + (a ? '<button class="bt ' + (a.risco ? "risco" : "ok") + '" type="button" data-q="' + x.id + '">' + (a.risco ? "" : ic("check", 20)) + esc(a.r) + "</button>" : "") + "</div>";
    }).join("");
    var etapas = B.fases.map(function (f) {
      var ns = f.ids.map(function (id) { return K.nos.filter(function (n) { return n.id === id; })[0]; });
      return '<div class="e-f"><b><span>' + f.nome + '</span><span class="mono">' + ns.filter(function (n) { return n.est === "ok"; }).length + "/" + ns.length + '</span></b><div class="seg" role="img" aria-label="' + f.nome + ": " + ns.filter(function (n) { return n.est === "ok"; }).length + " de " + ns.length + ' etapas feitas">' + ns.map(function (n) { return '<i class="' + (n.est === "ok" ? "ok" : n.est === "rodando" ? "rodando" : "") + '" title="' + esc(n.r) + '"></i>'; }).join("") + "</div></div>";
    }).join("");
    var prj = D.projetos.map(function (p) {
      return '<div class="pj"><div><div class="n">' + esc(B.nomeProj(p.slug)) + '</div><div class="e">' + esc(p.etapa) + " · " + esc(p.tipo) + '</div></div><span class="est ' + p.est + '">' + B.estLabel[p.est] + '</span><div class="bar ' + p.est + '" role="img" aria-label="' + p.prog + '% concluído"><i style="width:' + p.prog + '%"></i></div></div>';
    }).join("");
    var jobs = [D.jobs[0], D.jobs[2], D.jobs[3]].map(function (j) {
      var pc = Math.round(j.custo / j.teto * 100);
      return '<div class="cst"><div class="l1"><b>' + esc(j.nome.split(":")[0]) + "</b><span>" + B.usd(j.custo) + " de " + B.usd(j.teto) + '</span></div><div class="tr' + (j.estado === "erro" ? " err" : pc > 60 ? " alto" : "") + '"><i style="width:' + pc + '%"></i></div><div class="l2">' + B.n(j.tok) + " tokens · " + j.modelo + "</div></div>";
    }).join("");
    return '<section class="faixa"><div><h1>' + (P.length ? "No Canal, " + P.length + " ações são suas." : "O Canal não precisa de você agora.") + "</h1><p>Contexto Explica: Shorts de 30 a 60 s. " + (urg ? urg + " urgentes: o <b>Vini</b> bloqueou um texto antes do render." : "Os agentes seguem o fluxo.") + '</p></div><div class="chips" aria-label="Resumo do canal">' +
      '<div class="mt"><span class="v">' + B.n(K.vis) + '</span><span class="l">visualizações em 14 dias, +' + K.delta + "%</span>" + B.spark(K.serie, 120, 26) + "</div>" +
      '<div class="mt"><span class="v">' + K.ret + '<small>%</small></span><span class="l">retenção média</span></div>' +
      '<div class="mt"><span class="v">' + K.ativos + "<small>de " + K.total + '</small></span><span class="l">vídeos em produção</span></div>' +
      '<div class="mt"><span class="v">' + K.fila + '</span><span class="l">na fila de postagem</span></div></div></section>' +
      leg5() + '<div class="cols"><div class="col"><section class="cartao"><h2><span>Ações para você</span><span class="d">' + P.length + " no Canal</span></h2><div class=\"acs\">" + (acs || '<p class="mudo">Nada espera você aqui.</p>') + "</div></section>" +
      '<section class="cartao"><h2><span>Short em andamento</span><span class="d">a recessão de amizades entre homens</span></h2><div class="etapas">' + etapas + '</div><p class="mudo" style="margin:10px 22px 18px;font-size:14px">' + K.feitos + " de " + K.nos.length + " etapas feitas. Agora: o <b>Olise</b> desenha as cenas.</p></section>" +
      '<section class="cartao"><h2><span>Todos os vídeos</span><span class="d">' + D.projetos.length + '</span></h2><div class="prj">' + prj + "</div></section></div>" +
      '<aside class="col" aria-label="Números"><section class="cartao"><h2><span>Visualizações por dia</span><span class="d">14 dias</span></h2><div class="graf">' + area(K.serie, 420, 200) + "</div></section>" +
      '<section class="cartao"><h2><span>Retenção por vídeo</span></h2><div class="rg">' + B.ring(K.ret, 92, 11, "Retenção média " + K.ret + "%") + '<div class="tx"><b>' + K.ret + '%</b>média de 5 vídeos</div></div></section>' +
      '<section class="cartao"><h2><span>Custo dos agentes</span><span class="d">hoje</span></h2><div class="job-l">' + jobs + "</div></section>" + atividade(3) + "</aside></div>";
  }
  function ligarCanal() {
    app.querySelectorAll("[data-q]").forEach(function (b) {
      b.onclick = function () { var x = B.todas.filter(function (d) { return d.id === b.dataset.q; })[0]; B.agir(b, x, B.principal(x), render); };
    });
    app.querySelectorAll("[data-parar]").forEach(function (b) { b.onclick = function () { S.pausado = !S.pausado; B.toast(S.pausado ? "Agentes pausados. Nada novo começa até você retomar." : "Agentes retomados."); render(); }; });
  }
  function stub(id) {
    var s = B.setor(id);
    return '<section class="faixa"><div><h1>' + esc(s.nome || id) + '</h1><p>Chefe: ' + esc(s.chefe || "Guilherme") + '</p></div></section><div class="stub"><b>Fora desta comparação</b>' + esc(s.desc || "") + " As telas desenhadas neste estilo são Espera você e Canal.</div>";
  }

  /* ---------- conversa ---------- */
  var SUG = ["O que está travando?", "Quanto gastei hoje?", "Como estão os vídeos?"];
  function conversa() {
    return '<section class="conv" aria-label="Conversa com o De Bruyne"><div class="conv-in"><div class="resp' + (S.resp ? " on" : "") + '" id="resp" aria-live="polite">' + S.resp + '</div><div class="sug">' + SUG.map(function (s) { return '<button type="button" data-sug="' + esc(s) + '">' + esc(s) + "</button>"; }).join("") +
      '</div><form class="cx" id="cx"><span class="avatar av" aria-hidden="true">D</span><input id="q" type="text" aria-label="Pergunte ao De Bruyne" placeholder="Pergunte ao De Bruyne" autocomplete="off"><button class="bt" type="submit">Enviar</button></form></div></section>';
  }
  function responder(q) {
    var t = q.toLowerCase(), P = pend(), h;
    if (/trav|urgen|bloque|espera/.test(t)) {
      var l = P.filter(function (x) { return x.urgente || x.trava; }).slice(0, 4);
      h = "<b>De Bruyne:</b> " + P.filter(function (x) { return x.urgente; }).length + " urgentes e " + P.filter(function (x) { return x.trava; }).length + " que travam um fluxo. Comece por:<ul>" + l.map(function (x) { return "<li>" + x.cod + ": " + esc(x.titulo) + "</li>"; }).join("") + "</ul>";
    } else if (/gast|custo|token|us\$|dinheiro/.test(t)) {
      var c = D.jobs.reduce(function (a, j) { return a + j.custo; }, 0);
      h = "<b>De Bruyne:</b> Hoje os jobs somam " + B.usd(c) + " e " + B.n(D.jobs.reduce(function (a, j) { return a + j.tok; }, 0)) + " tokens. Nenhum passou do teto. O Salah falhou (erro 403) e custou " + B.usd(0.05) + ".";
    } else if (/v[ií]deo|canal|short|produ/.test(t)) {
      h = "<b>De Bruyne:</b> " + D.projetos.filter(function (p) { return p.prog < 100; }).length + " Shorts em produção e " + D.fila.length + " na fila de postagem. O mais adiantado é \"" + esc(B.nomeProj(D.projetos[5].slug)) + "\", esperando sua aprovação.";
    } else if (/par|paus/.test(t)) {
      h = "<b>De Bruyne:</b> Para parar tudo, use \"Pausar os agentes\" na coluna de atividade. Nada novo começa até você retomar.";
    } else {
      h = "<b>De Bruyne:</b> Hoje há " + P.length + " decisões suas. Pergunte sobre o que trava, custos ou vídeos, ou diga o que quer decidir.";
    }
    S.resp = h; var r = document.getElementById("resp"); r.innerHTML = h; r.classList.add("on");
  }
  function ligarConversa() {
    var f = document.getElementById("cx"), q = document.getElementById("q");
    f.onsubmit = function (e) { e.preventDefault(); if (q.value.trim()) { responder(q.value); q.value = ""; } };
    app.querySelectorAll("[data-sug]").forEach(function (b) { b.onclick = function () { responder(b.dataset.sug); }; });
  }

  function render() {
    var r = B.rota();
    app.innerHTML = casca(r === "espera" ? espera() : r === "canal" ? canal() : stub(r));
    app.querySelectorAll("[data-tema]").forEach(function (b) { b.onclick = function () { T.alternar(); render(); }; });
    if (r === "espera") ligarEspera(); else if (r === "canal") ligarCanal();
    ligarConversa();
    document.title = (B.menu.filter(function (m) { return m.id === r; })[0] || {}).nome + " · Contexto Explica (E)";
  }
  window.addEventListener("hashchange", function () { S.motivos = false; S.i = 0; render(); window.scrollTo(0, 0); });
  if (!location.hash) location.hash = "#/espera"; else render();
  if (!app.innerHTML) render();
})();
