/* Núcleo: estado, utilitários, roteador, decisões ("Espera você"), modais, console de jobs. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var clone = function (o) { return JSON.parse(JSON.stringify(o)); };
  var us = function (n) { return "US$ " + n.toFixed(2).replace(".", ","); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("ctx:" + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("ctx:" + k, JSON.stringify(v)); } catch (e) { /* abre por duplo clique: pode estar bloqueado */ } }
  };

  var ICON = {
    espera: '<path d="M4 5h16v11H8l-4 4z"/><path d="M12 8v4M12 14v.5"/>',
    hoje: '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
    canal: '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 17h2"/>',
    clipes: '<path d="M4 6l4 4M4 18l4-4M8 10l12-5M8 14l12 5"/><circle cx="6" cy="8" r="2"/><circle cx="6" cy="16" r="2"/>',
    inteligencia: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    trabalho: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2M3 13h18"/>',
    financas: '<circle cx="12" cy="12" r="9"/><path d="M14.5 9.2c-.6-.8-1.5-1.2-2.5-1.2-1.4 0-2.5.8-2.5 1.9 0 2.7 5 1.3 5 4 0 1.1-1.1 1.9-2.5 1.9-1.1 0-2-.5-2.6-1.3M12 6.5V8M12 16v1.5"/>',
    programacao: '<path d="M8 8l-5 4 5 4M16 8l5 4-5 4M14 5l-4 14"/>',
    ecossistema: '<circle cx="12" cy="5" r="2.2"/><circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="18" r="2.2"/><path d="M11 7l-5 9M13 7l5 9M7.2 18h9.6"/>',
    mais: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    console: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M13 15h4"/>',
    tema: '<path d="M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z"/>',
    fechar: '<path d="M6 6l12 12M18 6L6 18"/>'
  };
  var ic = function (n) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICON[n] || "") + "</svg>"; };

  var ROTULO = { rodando: "Rodando", espera: "Espera você", erro: "Erro", bloq: "Bloqueado", ok: "Concluído", fila: "Na fila", pausa: "Pausado" };
  var est = function (e, t) { return '<span class="estado ' + e + '">' + esc(t || ROTULO[e] || e) + "</span>"; };

  var S = window.S = {
    tema: store.get("tema", "auto"), demo: "normal", filtro: "todos",
    pendentes: clone(D.decisoes), adiadas: [], feitas: clone(D.historicoDecisoes), edicoes: {},
    jobs: clone(D.jobs), selJob: "j1", consoleAberto: false, rotaAtual: ""
  };
  var H = window.H = { $: $, $$: $$, esc: esc, clone: clone, us: us, store: store, ic: ic, est: est, ROTULO: ROTULO };

  /* ---------- diff de linhas ---------- */
  H.diff = function (a, b) {
    var A = a.split("\n"), B = b.split("\n"), n = A.length, m = B.length, t = [], i, j;
    for (i = 0; i <= n; i++) { t.push(new Array(m + 1).fill(0)); }
    for (i = n - 1; i >= 0; i--) for (j = m - 1; j >= 0; j--) t[i][j] = A[i] === B[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
    var o = []; i = 0; j = 0;
    while (i < n && j < m) {
      if (A[i] === B[j]) { o.push({ t: " ", s: A[i] }); i++; j++; }
      else if (t[i + 1][j] >= t[i][j + 1]) { o.push({ t: "-", s: A[i++] }); } else { o.push({ t: "+", s: B[j++] }); }
    }
    while (i < n) o.push({ t: "-", s: A[i++] }); while (j < m) o.push({ t: "+", s: B[j++] });
    return o;
  };
  H.diffHtml = function (a, b) {
    var d = H.diff(a, b), mud = d.filter(function (x) { return x.t !== " "; }).length;
    if (!mud) return '<p class="mudo">Nenhuma diferença.</p>';
    return '<div class="dif" role="group" aria-label="Diferenças">' + d.map(function (x) {
      return '<div class="' + (x.t === "+" ? "mais" : x.t === "-" ? "menos" : "") + '"><span class="vh">' + (x.t === "+" ? "Adicionado: " : x.t === "-" ? "Removido: " : "") + "</span>" + (x.t === " " ? "  " : x.t + " ") + esc(x.s) + "</div>";
    }).join("") + "</div>";
  };

  /* ---------- diagrama de fluxo (SVG gerado dos dados) ---------- */
  H.fluxoSvg = function (nos, andamento, opt) {
    opt = opt || {}; andamento = andamento || {};
    var W = 172, Hh = 54, GX = 34, GY = 22, byId = {}, camada = {};
    nos.forEach(function (n) { byId[n.id] = n; });
    var nivel = function (n, vis) {
      if (camada[n.id] != null) return camada[n.id];
      if (vis[n.id]) return 0; vis[n.id] = 1;
      var l = 0; n.d.forEach(function (d) { if (byId[d]) l = Math.max(l, nivel(byId[d], vis) + 1); });
      return (camada[n.id] = l);
    };
    nos.forEach(function (n) { nivel(n, {}); });
    var cols = {}, max = 0; nos.forEach(function (n) { (cols[camada[n.id]] = cols[camada[n.id]] || []).push(n); max = Math.max(max, camada[n.id]); });
    var maxLar = 0; Object.keys(cols).forEach(function (k) { maxLar = Math.max(maxLar, cols[k].length); });
    var vert = opt.dir ? opt.dir === "v" : (max + 1 > 8), pos = {}, w, h;
    Object.keys(cols).forEach(function (k) {
      cols[k].forEach(function (n, i) {
        if (vert) { pos[n.id] = { x: 10 + (i + (maxLar - cols[k].length) / 2) * (W + GX), y: 10 + k * (Hh + GY + 8) }; }
        else { pos[n.id] = { x: 10 + k * (W + GX), y: 10 + (i + (maxLar - cols[k].length) / 2) * (Hh + GY) }; }
      });
    });
    if (vert) { w = 20 + maxLar * (W + GX) - GX; h = 20 + (max + 1) * (Hh + GY + 8) - GY - 8; }
    else { w = 20 + (max + 1) * (W + GX) - GX; h = 20 + maxLar * (Hh + GY) - GY; }
    var cut = function (s, n) { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
    var arestas = "", gs = "";
    nos.forEach(function (n) {
      n.d.forEach(function (d) {
        var a = pos[d], b = pos[n.id]; if (!a || !b) return;
        if (vert) { var x1 = a.x + W / 2, y1 = a.y + Hh, x2 = b.x + W / 2, y2 = b.y, m = (y1 + y2) / 2; arestas += '<path class="aresta" d="M' + x1 + "," + y1 + " C" + x1 + "," + m + " " + x2 + "," + m + " " + x2 + "," + (y2 - 4) + '" marker-end="url(#seta)"/>'; }
        else { var xx1 = a.x + W, yy1 = a.y + Hh / 2, xx2 = b.x, yy2 = b.y + Hh / 2, mm = (xx1 + xx2) / 2; arestas += '<path class="aresta" d="M' + xx1 + "," + yy1 + " C" + mm + "," + yy1 + " " + mm + "," + yy2 + " " + (xx2 - 4) + "," + yy2 + '" marker-end="url(#seta)"/>'; }
      });
    });
    nos.forEach(function (n) {
      var p = pos[n.id], s = andamento[n.id] || "", cls = "no " + (n.t === "gate" ? "gate " : n.t === "code" ? "cod " : "") + s;
      var lab = n.r + ". " + (n.a ? n.a + ". " : "") + (s ? ROTULO[s] : "");
      gs += '<g class="' + cls + '" tabindex="0" role="button" aria-label="' + esc(lab) + '" data-act="no" data-id="' + esc(n.id) + '" data-fl="' + esc(opt.id || "") + '" transform="translate(' + p.x + "," + p.y + ')"><title>' + esc(lab) + '</title><rect width="' + W + '" height="' + Hh + '" rx="9"/><text x="12" y="23">' + esc(cut(n.r, 24)) + '</text><text class="sub" x="12" y="40">' + esc(cut((n.t === "gate" ? "Decisão sua" : n.a) + (s && s !== "ok" ? " · " + ROTULO[s] : ""), 30)) + "</text></g>";
    });
    return '<div class="fluxo"><svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + " " + h + '" role="group" aria-label="Diagrama do fluxo"><defs><marker id="seta" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor" style="color:var(--ink3)"/></marker></defs>' + arestas + gs + "</svg></div>" +
      '<div class="legenda" aria-hidden="true"><span><i></i>Agente</span><span><i class="c"></i>Código</span><span><i class="g"></i>Decisão sua</span><span><i class="o"></i>Concluído</span></div>';
  };

  /* ---------- modal ---------- */
  var dlg;
  H.modal = function (o) {
    dlg = dlg || $("#modal");
    var bts = (o.botoes || [{ r: "Fechar" }]);
    dlg.innerHTML = '<form method="dialog"><div class="m-cab"><h2>' + esc(o.titulo) + '</h2></div><div class="m-corpo">' + o.corpo + '</div><div class="m-pe"></div></form>';
    var pe = $(".m-pe", dlg);
    bts.forEach(function (b) {
      var el = document.createElement("button"); el.type = "button"; el.className = "btn " + (b.cls || ""); el.textContent = b.r;
      if (b.off) { el.disabled = true; el.id = b.off; }
      el.addEventListener("click", function () { if (b.fn) { var r = b.fn(dlg); if (r === false) return; } dlg.close(); });
      pe.appendChild(el);
    });
    if (!dlg.open) dlg.showModal();
    var f = $("input,textarea,select", dlg); if (f) f.focus(); else { var b0 = $(".m-pe .btn:last-child", dlg); if (b0) b0.focus(); }
    return dlg;
  };
  H.confirmar = function (o) {
    /* confirmação explícita: digitar "confirmo" */
    H.modal({ titulo: o.titulo, corpo: o.corpo + '<label class="campo">Digite <b>confirmo</b> para continuar<input type="text" id="conf-txt" autocomplete="off" aria-describedby="conf-ajuda"></label><p id="conf-ajuda" class="pequeno mudo">' + (o.ajuda || "Nada acontece sem esta confirmação.") + "</p>",
      botoes: [{ r: "Cancelar" }, { r: o.rotulo || "Confirmo", cls: "pri", off: "conf-ok", fn: o.fn }] });
    var inp = $("#conf-txt"), ok = $("#conf-ok");
    inp.addEventListener("input", function () { ok.disabled = inp.value.trim().toLowerCase() !== "confirmo"; });
  };
  H.toast = function (msg, desfazer) {
    var t = document.createElement("div"); t.className = "toast"; t.innerHTML = "<span>" + esc(msg) + "</span>";
    if (desfazer) { var b = document.createElement("button"); b.className = "btn"; b.textContent = "Desfazer"; b.onclick = function () { desfazer(); t.remove(); }; t.appendChild(b); }
    $("#toasts").appendChild(t); setTimeout(function () { t.remove(); }, desfazer ? 9000 : 4500);
  };
  H.copiar = function (txt, ok) {
    var fim = function () { H.toast(ok || "Copiado."); };
    try { navigator.clipboard.writeText(txt).then(fim, fim); } catch (e) { fim(); }
  };

  /* ---------- decisões ---------- */
  var ativas = function () { return S.pendentes.filter(function (d) { return !d.bloqueada; }); };
  H.contagem = ativas;
  H.atualizaContador = function () {
    var n = ativas().length;
    $$(".contador").forEach(function (c) { c.textContent = n; c.setAttribute("data-n", n); c.setAttribute("aria-label", n + " decisões esperam você"); });
    document.title = (n ? "(" + n + ") " : "") + "Contexto Explica";
  };
  var resolver = function (id, texto) {
    var i = S.pendentes.findIndex(function (d) { return d.id === id; }); if (i < 0) return;
    var d = S.pendentes.splice(i, 1)[0], h = { q: "Agora", t: texto + ": " + d.titulo, c: d.cod };
    S.feitas.unshift(h);
    var el = $('[data-dec="' + id + '"]');
    var fim = function () { H.atualizaContador(); H.rerender(); };
    if (el) { el.classList.add("saindo"); setTimeout(fim, 330); } else fim();
    H.toast(texto + ".", function () { S.pendentes.splice(i, 0, d); S.feitas.shift(); H.atualizaContador(); H.rerender(); });
  };
  var achar = function (id) { return S.pendentes.concat(S.adiadas).find(function (d) { return d.id === id; }); };

  H.decisaoHtml = function (d) {
    var pri = d.acoes[0], extra = d.acoes.slice(1), ed = S.edicoes[d.id];
    var corpo = d.bloqueada ? "" : "";
    var btns = d.bloqueada ? '<span class="estado bloq">Bloqueado, sem ação possível agora</span>' :
      d.acoes.map(function (a, i) {
        return '<button class="btn ' + (i === 0 ? "pri" : "") + '" data-act="dec" data-id="' + d.id + '" data-i="' + i + '">' + esc(a.r) + "</button>";
      }).join("") +
      (d.edit ? '<button class="btn" data-act="editar" data-id="' + d.id + '">Editar</button>' : "") +
      (d.recusa && d.recusa.length ? '<button class="btn" data-act="recusar" data-id="' + d.id + '">' + (d.recusa[0] === "Descartar fonte" ? "Descartar" : "Pedir ajuste") + "</button>" : "") +
      '<button class="btn fantasma" data-act="adiar" data-id="' + d.id + '">Adiar</button>';
    var sd = D.setores.find(function (s) { return s.id === d.setor; });
    return '<article class="cartao' + (d.urgente ? " urg" : "") + (d.bloqueada ? " bloqueada" : "") + '" data-dec="' + d.id + '" aria-labelledby="t-' + d.id + '">' +
      '<div class="cab-c"><span class="cod" title="Código da decisão no mapa do Valverde">' + d.cod + '</span><span class="chip">' + esc(sd ? sd.nome : d.setor) + "</span>" + (d.urgente ? '<span class="estado espera">Está travando fluxo</span>' : "") + (ed ? '<span class="chip">texto editado</span>' : "") + "</div>" +
      '<h3 id="t-' + d.id + '">' + esc(d.titulo) + "</h3><p class=\"mudo\" style=\"margin:0\">" + esc(d.ctx) + "</p>" +
      (d.trava ? '<p class="trava" style="margin:0">' + esc(d.trava) + "</p>" : "") +
      (d.det ? "<details><summary>Ver contexto completo</summary>" + d.det + (ed ? '<div class="trecho">' + esc(ed) + "</div>" : "") + "</details>" : "") +
      '<div class="acoes">' + btns + "</div></article>";
  };

  var viewEspera = function () {
    var filtro = S.filtro, lista = S.pendentes.filter(function (d) { return !d.bloqueada && (filtro === "todos" || d.setor === filtro); }).sort(function (a, b) { return (b.urgente ? 1 : 0) - (a.urgente ? 1 : 0) || a.ordem - b.ordem; });
    var bloq = S.pendentes.filter(function (d) { return d.bloqueada; }), n = ativas().length;
    var porSetor = {}; ativas().forEach(function (d) { porSetor[d.setor] = (porSetor[d.setor] || 0) + 1; });
    var chips = '<button class="chip" aria-pressed="' + (filtro === "todos") + '" data-act="filtro" data-v="todos">Todos (' + n + ")</button>" + D.setores.filter(function (s) { return porSetor[s.id]; }).map(function (s) {
      return '<button class="chip" aria-pressed="' + (filtro === s.id) + '" data-act="filtro" data-v="' + s.id + '">' + s.nome + " (" + porSetor[s.id] + ")</button>";
    }).join("");
    var urg = ativas().filter(function (d) { return d.urgente; }).length;
    var corpo;
    if (!n) corpo = '<div class="tela-estado"><h2>Nada espera você</h2><p>Todos os agentes seguem sozinhos. Quando algo precisar de você, aparece aqui e no número do menu.</p><button class="btn" data-act="restaurar-fila">Recarregar as decisões de exemplo</button></div>';
    else if (!lista.length) corpo = '<div class="tela-estado"><h2>Nada neste setor</h2><p>As decisões pendentes estão em outros setores.</p><button class="btn" data-act="filtro" data-v="todos">Ver todas</button></div>';
    else corpo = '<div class="fila">' + lista.map(H.decisaoHtml).join("") + "</div>";
    return '<div class="cab"><div><h1>Espera você</h1><p>' + (n ? n + (n === 1 ? " decisão pendente" : " decisões pendentes") + (urg ? ", " + urg + " travando fluxo. As que travam vêm primeiro." : ".") : "Tudo em dia.") + '</p></div><div class="filtros" role="group" aria-label="Filtrar por setor">' + chips + "</div></div>" + corpo +
      (bloq.length ? '<section class="adiadas" aria-label="Bloqueadas"><h2 style="margin-bottom:12px">Bloqueadas</h2><div class="fila">' + bloq.map(H.decisaoHtml).join("") + "</div></section>" : "") +
      (S.adiadas.length ? '<section class="adiadas" aria-label="Adiadas"><h2 style="margin-bottom:8px">Adiadas</h2><ul class="painel lista">' + S.adiadas.map(function (d) {
        return '<li><span class="cod mono">' + d.cod + '</span><span class="grow">' + esc(d.titulo) + '<br><span class="mudo pequeno">volta ' + esc(d.volta) + '</span></span><button class="btn peq" data-act="trazer" data-id="' + d.id + '">Trazer de volta</button></li>';
      }).join("") + "</ul></section>" : "") +
      '<section class="adiadas" aria-label="Resolvidas"><h2 style="margin-bottom:8px">Resolvidas há pouco</h2><ul class="painel lista">' + S.feitas.slice(0, 6).map(function (f) { return '<li><span class="cod mono">' + esc(f.c) + '</span><span class="grow">' + esc(f.t) + '</span><span class="mudo pequeno">' + esc(f.q) + "</span></li>"; }).join("") + "</ul></section>";
  };

  /* ---------- ações (delegação de cliques) ---------- */
  var ACT = {};
  ACT.filtro = function (a) { S.filtro = a.dataset.v; H.rerender(); };
  ACT["restaurar-fila"] = function () { S.pendentes = clone(D.decisoes); H.atualizaContador(); H.rerender(); };
  ACT.dec = function (a) {
    var d = achar(a.dataset.id), ac = d.acoes[+a.dataset.i];
    if (ac.k === "copiar") { H.copiar(d.det.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim() || ac.r, "Copiado para a área de transferência."); return; }
    if (ac.k === "ver") { location.hash = ac.rota; return; }
    if (ac.risco) {
      H.confirmar({ titulo: ac.r, corpo: '<div class="nota lj"><p><b>' + (ac.externa ? "Ação externa." : "Ação de risco.") + "</b> " + esc(d.trava || d.ctx) + "</p></div><p>" + esc(d.titulo) + "</p>", rotulo: ac.r, fn: function () { resolver(d.id, ac.r); } });
      return;
    }
    resolver(d.id, ac.r);
  };
  ACT.recusar = function (a) {
    var d = achar(a.dataset.id), cats = d.recusa, sel = cats[0];
    H.modal({ titulo: "Pedir ajuste", corpo: "<p>" + esc(d.titulo) + '</p><div class="linha" role="group" aria-label="Categoria">' + cats.map(function (c, i) { return '<button type="button" class="chip" data-cat="' + esc(c) + '" aria-pressed="' + (i === 0) + '">' + esc(c) + "</button>"; }).join("") + '</div><label class="campo">O que mudar<textarea rows="3" id="rec-nota" placeholder="Em uma frase, para o agente que vai refazer"></textarea></label><p class="pequeno mudo">Só o ramo afetado é refeito; o resto não gasta de novo.</p>',
      botoes: [{ r: "Cancelar" }, { r: "Enviar ajuste", cls: "pri", fn: function () { resolver(d.id, "Pediu ajuste (" + sel + ")"); } }] });
    $$(".chip[data-cat]", dlg).forEach(function (c) { c.onclick = function () { sel = c.dataset.cat; $$(".chip[data-cat]", dlg).forEach(function (x) { x.setAttribute("aria-pressed", x === c); }); }; });
  };
  ACT.editar = function (a) {
    var d = achar(a.dataset.id);
    H.modal({ titulo: d.edit.campo, corpo: '<label class="campo">' + esc(d.edit.dica) + '<textarea rows="5" id="ed-txt" class="cod">' + esc(S.edicoes[d.id] || "") + '</textarea></label><p class="pequeno mudo">A edição fica salva neste cartão. Depois é só aprovar.</p>',
      botoes: [{ r: "Cancelar" }, { r: "Salvar edição", cls: "pri", fn: function () { S.edicoes[d.id] = $("#ed-txt").value.trim(); H.rerender(); H.toast("Edição guardada."); } }] });
  };
  ACT.adiar = function (a) {
    var d = achar(a.dataset.id), op = ["amanhã de manhã", "sexta-feira", "semana que vem"];
    H.modal({ titulo: "Adiar até quando?", corpo: "<p>" + esc(d.titulo) + '</p><div class="pilha p">' + op.map(function (o, i) { return '<button type="button" class="btn" data-v="' + o + '">Voltar ' + o + "</button>"; }).join("") + "</div>", botoes: [{ r: "Cancelar" }] });
    $$("[data-v]", dlg).forEach(function (b) { b.onclick = function () { var i = S.pendentes.indexOf(d); if (i < 0) return; S.pendentes.splice(i, 1); d.volta = b.dataset.v; S.adiadas.push(d); dlg.close(); H.atualizaContador(); H.rerender(); H.toast("Adiado para " + b.dataset.v + ".", function () { S.adiadas.splice(S.adiadas.indexOf(d), 1); S.pendentes.splice(i, 0, d); H.atualizaContador(); H.rerender(); }); }; });
  };
  ACT.trazer = function (a) { var d = achar(a.dataset.id), i = S.adiadas.indexOf(d); S.adiadas.splice(i, 1); S.pendentes.push(d); H.atualizaContador(); H.rerender(); };
  ACT["ir"] = function (a) { location.hash = a.dataset.h; };
  ACT.tema = function () { var t = S.tema === "escuro" ? "claro" : S.tema === "claro" ? "auto" : "escuro"; S.tema = t; aplicaTema(); H.toast("Tema: " + t + "."); };
  ACT.menu = function () { $("#rail").classList.toggle("aberto"); };
  ACT.console = function () { S.consoleAberto = !S.consoleAberto; H.renderConsole(); };
  ACT.no = function (a) {
    var fl = D.fluxos[a.dataset.fl] || D.fluxos[(S.rotaAtual.split("/")[1] === "canal" ? "canal" : S.rotaAtual.split("/")[1])];
    var n = ((fl && fl.nos) || []).concat(H.nosExtra || []).find(function (x) { return x.id === a.dataset.id; }); if (!n) return;
    H.modal({ titulo: n.r, corpo: '<p>' + (n.t === "gate" ? "Decisão sua. A aprovação vale só para a versão que você viu." : n.t === "code" ? "Passo de código, sem agente. Não gasta token." : "Agente: <b>" + esc(n.a) + "</b>.") + '</p><p class="mudo">Depende de: ' + (n.d.length ? n.d.map(function (x) { var y = fl.nos.find(function (z) { return z.id === x; }); return esc(y ? y.r : x); }).join(", ") : "nada (começa sozinho)") + "</p>" });
  };
  H.ACT = ACT;

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-act]"); if (!t) { if ($("#rail").classList.contains("aberto") && !e.target.closest("#rail")) $("#rail").classList.remove("aberto"); return; }
    if (ACT[t.dataset.act]) { e.preventDefault(); ACT[t.dataset.act](t, e); }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches("g[data-act]")) { e.preventDefault(); ACT.no(e.target); }
    if (e.key === "Escape") { $("#rail").classList.remove("aberto"); }
  });
  document.addEventListener("change", function (e) { var t = e.target; if (t.dataset && t.dataset.chg && ACT[t.dataset.chg]) ACT[t.dataset.chg](t, e); });
  document.addEventListener("input", function (e) { var t = e.target; if (t.dataset && t.dataset.inp && ACT[t.dataset.inp]) ACT[t.dataset.inp](t, e); });

  /* ---------- tema ---------- */
  function aplicaTema() { var r = document.documentElement; if (S.tema === "auto") r.removeAttribute("data-theme"); else r.setAttribute("data-theme", S.tema); store.set("tema", S.tema); }

  /* ---------- console e jobs (simulado) ---------- */
  var SCRIPT = {
    agente: ["Lendo entradas do fluxo (por caminho e versão, sem colar arquivos)", "Conferindo regras do CLAUDE.md e do agente", "Trabalhando na tarefa…", "Gravando a saída em arquivo", "Conferindo o resultado contra o contrato", "Concluído."],
    pesado: ["Iniciando comando (raia pesada: 1 por vez)", "Etapa 1 de 4", "Etapa 2 de 4", "Etapa 3 de 4", "Etapa 4 de 4", "Concluído."],
    codigo: ["Executando…", "Lendo arquivos locais", "Gravando saída", "Concluído."]
  };
  var rodando = function (t) { return S.jobs.filter(function (j) { return j.estado === "rodando" && (!t || j.tipo === t); }); };
  H.novoJob = function (nome, tipo, motor, modelo, teto) {
    var j = { id: "j" + (S.jobs.length + 1) + Date.now() % 1000, nome: nome, tipo: tipo, estado: "fila", motor: motor, modelo: modelo, tok: 0, custo: 0, teto: teto, ini: "agora", log: ["Na fila."], passo: 0 };
    S.jobs.unshift(j); S.selJob = j.id; S.consoleAberto = true; H.renderConsole(); return j;
  };
  setInterval(function () {
    var mudou = false;
    S.jobs.forEach(function (j) {
      if (j.estado === "fila") {
        var cap = j.tipo === "pesado" ? (rodando("pesado").length < 1) : (rodando("agente").length < 3);
        if (cap) { j.estado = "rodando"; j.passo = 0; j.log.push("Começou."); mudou = true; }
      } else if (j.estado === "rodando" && j.passo != null) {
        var sc = SCRIPT[j.tipo === "agente" ? "agente" : j.tipo === "pesado" ? "pesado" : "codigo"];
        if (j.passo >= sc.length) return;
        j.log.push("[" + new Date().toTimeString().slice(0, 8) + "] " + sc[j.passo]); j.passo++;
        if (j.tipo === "agente") { j.tok += 2300 + Math.floor(Math.random() * 1500); j.custo = Math.min(j.teto, j.custo + 0.02 + Math.random() * 0.03); }
        if (j.passo >= sc.length) j.estado = "ok"; mudou = true;
      } else if (j.estado === "rodando" && j.id === "j1") { /* job inicial evolui devagar */
        if (Math.random() < 0.5) { j.log.push("[" + new Date().toTimeString().slice(0, 8) + "] Escrevendo sketch_cenas.py cena " + (2 + (j.log.length % 5)) + " de 6"); j.tok += 1900; j.custo += 0.02; mudou = true; }
      }
    });
    if (mudou) { H.atualizaPilula(); if (S.consoleAberto) H.renderConsole(true); }
  }, 1500);

  H.atualizaPilula = function () {
    var n = S.jobs.filter(function (j) { return j.estado === "rodando"; }).length, e = S.jobs.filter(function (j) { return j.estado === "erro"; }).length;
    var b = $("#pilula"); if (!b) return;
    b.innerHTML = ic("console") + '<span class="pilula">' + (n ? '<span class="estado rodando">' + n + " rodando</span>" : "Nenhum job") + (e ? ' <span class="estado erro">' + e + " com erro</span>" : "") + "</span>";
  };
  H.renderConsole = function (leve) {
    var c = $("#console"); c.classList.toggle("aberto", S.consoleAberto); H.atualizaPilula();
    if (!S.consoleAberto) return;
    var j = S.jobs.find(function (x) { return x.id === S.selJob; }) || S.jobs[0];
    var totC = S.jobs.reduce(function (s, x) { return s + x.custo; }, 0), totT = S.jobs.reduce(function (s, x) { return s + x.tok; }, 0);
    if (leve && $("#log")) {
      var lg = $("#log"), bottom = lg.scrollTop + lg.clientHeight >= lg.scrollHeight - 30;
      lg.innerHTML = logHtml(j); if (bottom) lg.scrollTop = lg.scrollHeight;
      $("#jobs-lista").innerHTML = jobsHtml(); $("#job-meta").innerHTML = metaHtml(j); $("#job-tot").textContent = "Hoje: " + us(totC) + ", " + Math.round(totT / 1000) + " mil tokens"; return;
    }
    var ags = D.agentesBase.map(function (a) { return '<option value="a:' + a[0] + '">' + a[1] + " (" + a[0] + ")</option>"; }).join("");
    var cms = D.comandos.map(function (a) { return '<option value="c:' + a.id + '">' + esc(a.rot) + "</option>"; }).join("");
    c.innerHTML = '<header><h2 style="font-size:1rem">Console</h2><span class="mudo pequeno grow" id="job-tot">Hoje: ' + us(totC) + ", " + Math.round(totT / 1000) + ' mil tokens</span><button class="btn peq icone" data-act="console" aria-label="Fechar console">' + ic("fechar") + '</button></header><div class="corpo"><div class="jobs" id="jobs-lista" role="list">' + jobsHtml() + '</div><div class="det"><div id="job-meta" style="padding:8px 12px">' + metaHtml(j) + '</div><pre class="log" id="log" tabindex="0" aria-live="off" aria-label="Log do job">' + logHtml(j) + '</pre><div class="disp"><div class="linha"><label class="vh" for="disp-alvo">O que disparar</label><select id="disp-alvo" style="flex:1;min-width:160px"><optgroup label="Agente">' + ags + '</optgroup><optgroup label="Comando">' + cms + '</optgroup></select><button class="btn pri" data-act="disparar">Disparar</button></div><label class="vh" for="disp-txt">Ordem ou argumento</label><input type="text" id="disp-txt" placeholder="Ordem ao agente, tema ou URL"><p class="pequeno mudo" style="margin:0" id="disp-aviso">Abrir uma tela nunca dispara agente. Só este botão gasta uso do plano, e o teto aparece aqui.</p></div></div></div>';
    var lg2 = $("#log"); lg2.scrollTop = lg2.scrollHeight;
    $("#disp-alvo").onchange = avisoDisp; avisoDisp();
  };
  function jobsHtml() { return S.jobs.map(function (j) { return '<button class="job" role="listitem" aria-pressed="' + (j.id === S.selJob) + '" data-act="job" data-id="' + j.id + '"><span class="pequeno" style="font-weight:600">' + esc(j.nome) + "</span>" + est(j.estado) + "</button>"; }).join(""); }
  function metaHtml(j) { return '<div class="linha entre">' + est(j.estado) + '<span class="pequeno mudo">Motor ' + esc(j.motor) + (j.modelo !== "-" ? ", " + j.modelo : "") + "</span></div>" + '<div class="linha pequeno mudo" style="margin-top:4px"><span>Tokens: ' + j.tok.toLocaleString("pt-BR") + "</span><span>Custo: " + us(j.custo) + (j.teto ? " de " + us(j.teto) : "") + "</span><span>Início: " + esc(j.ini) + "</span>" + (j.estado === "erro" ? '<button class="btn peq" data-act="tentar" data-id="' + j.id + '">Tentar de novo</button>' : "") + (j.estado === "rodando" || j.estado === "fila" ? '<button class="btn peq" data-act="cancelar" data-id="' + j.id + '">Cancelar</button>' : "") + "</div>"; }
  function logHtml(j) { return j.log.map(function (l) { var k = /ERRO/.test(l) ? "e" : /Conclu/.test(l) ? "o" : /^Aguardando|^Na fila/.test(l) ? "d" : ""; return '<span class="' + k + '">' + esc(l) + "</span>"; }).join("\n"); }
  function avisoDisp() {
    var v = $("#disp-alvo").value, el = $("#disp-aviso");
    if (v.indexOf("a:") === 0) { var a = D.agentesBase.find(function (x) { return x[0] === v.slice(2); }); el.innerHTML = "Agente <b>" + esc(a[1]) + "</b>: modelo " + a[3] + ", teto " + (a[3] === "opus" ? "US$ 1,00" : "US$ 0,50") + ". Usa o login do Claude Code; nunca a chave paga."; }
    else { var c = D.comandos.find(function (x) { return x.id === v.slice(2); }); el.innerHTML = "Comando de código: não gasta token." + (c.pesado ? " Raia pesada: 1 por vez, os outros esperam na fila." : ""); }
  }
  ACT.job = function (a) { S.selJob = a.dataset.id; H.renderConsole(); };
  ACT.tentar = function (a) { var j = S.jobs.find(function (x) { return x.id === a.dataset.id; }); j.estado = "fila"; j.passo = 0; j.log.push("Nova tentativa pedida por você."); H.renderConsole(); };
  ACT.cancelar = function (a) { var j = S.jobs.find(function (x) { return x.id === a.dataset.id; }); j.estado = "erro"; j.passo = null; j.log.push("ERRO: cancelado por você."); H.renderConsole(); };
  ACT.disparar = function () {
    var v = $("#disp-alvo").value, txt = $("#disp-txt").value.trim();
    if (v.indexOf("a:") === 0) { var a = D.agentesBase.find(function (x) { return x[0] === v.slice(2); }); H.novoJob(a[1] + ": " + (txt || "tarefa do fluxo"), "agente", "Claude", a[3], a[3] === "opus" ? 1 : 0.5); }
    else { var c = D.comandos.find(function (x) { return x.id === v.slice(2); }); H.novoJob(c.rot.replace(/\.\.\.|<URL>/, txt || "…"), c.pesado ? "pesado" : "codigo", "código", "-", 0); }
    $("#disp-txt").value = "";
  };

  /* ---------- roteador ---------- */
  var TITULO = { espera: "Espera você", hoje: "Hoje", canal: "Canal", clipes: "Clipes", inteligencia: "Inteligência", trabalho: "Trabalho", financas: "Finanças", programacao: "Programação", ecossistema: "Ecossistema" };
  H.TITULO = TITULO;
  H.abas = function (grupo, lista, atual) { return '<nav class="abas" aria-label="Seções de ' + TITULO[grupo] + '">' + lista.map(function (a) { return '<a href="#/' + grupo + "/" + a[0] + '"' + (a[0] === atual ? ' aria-current="page"' : "") + ">" + a[1] + "</a>"; }).join("") + "</nav>"; };
  H.rota = function () { var p = (location.hash || "#/espera").replace(/^#\//, "").split("/"); return { g: TITULO[p[0]] ? p[0] : "espera", s: p[1] || "" }; };
  H.views = { espera: viewEspera };

  function estadoTela(tipo, g) {
    var t = TITULO[g];
    if (tipo === "carregando") return '<div class="esqueleto" role="status" aria-label="Carregando"><i></i><i></i><i></i><i></i></div>';
    if (tipo === "vazio") return '<div class="tela-estado"><h2>Sem dados em ' + t + ' ainda</h2><p>Quando houver o primeiro projeto, ele aparece aqui. Comece pelo console ou pelo botão da barra.</p><button class="btn pri" data-act="console">Abrir o console</button></div>';
    if (tipo === "erro") return '<div class="tela-estado erro" role="alert"><h2>Não consegui ler os dados de ' + t + '</h2><p>O arquivo de origem não respondeu (por exemplo, <code>output/&lt;slug&gt;/estado.json</code> ausente). Nada foi perdido: confira se o servidor local está ligado e tente de novo.</p><button class="btn pri" data-act="demo-normal">Tentar de novo</button></div>';
    return '<div class="tela-estado bloq" role="status"><h2>' + t + ' está bloqueado agora</h2><p>Esta área depende de uma conexão que venceu ou de uma regra do canal (por exemplo, nenhum render sem auditoria de texto aprovada). Veja a causa em Ecossistema, Conexões.</p><a class="btn" href="#/ecossistema/conexoes">Ver conexões</a></div>';
  }
  ACT["demo-normal"] = function () { S.demo = "normal"; $("#demo-sel").value = "normal"; H.rerender(); };
  ACT.demo = function (a) { S.demo = a.value; H.rerender(); };

  H.rerender = function () {
    var r = H.rota(), main = $("#main"), key = r.g + "/" + r.s; S.rotaAtual = "/" + r.g + "/" + r.s;
    var st = S.demo, html;
    if (st !== "normal") html = '<div class="cab"><div><h1>' + TITULO[r.g] + '</h1><p class="mudo">Mostrando o estado "' + st + '" de demonstração.</p></div></div>' + estadoTela(st, r.g);
    else html = H.views[r.g](r.s);
    var y = window.scrollY; main.innerHTML = html;
    if (key === S.ultimaRota) window.scrollTo(0, y);
    S.ultimaRota = key;
    $$(".rail a.item").forEach(function (a) { a.removeAttribute("aria-current"); if (a.dataset.g === r.g) a.setAttribute("aria-current", "page"); });
    $$(".tabbar a").forEach(function (a) { a.removeAttribute("aria-current"); if (a.dataset.g === r.g) a.setAttribute("aria-current", "page"); });
    $("#titulo").textContent = TITULO[r.g];
    $("#rail").classList.remove("aberto");
    if (H.pos) H.pos();
  };
  window.addEventListener("hashchange", function () { H.rerender(); window.scrollTo(0, 0); $("#main").focus({ preventScroll: true }); });

  H.boot = function () {
    aplicaTema();
    var itens = Object.keys(TITULO);
    $("#nav").innerHTML = itens.map(function (g, i) { return (i === 2 ? '<div class="sep"></div>' : "") + '<a class="item" href="#/' + g + '" data-g="' + g + '">' + ic(g) + "<span>" + TITULO[g] + "</span>" + (g === "espera" ? '<span class="contador" data-n="0"></span>' : "") + "</a>"; }).join("");
    $("#tabbar").innerHTML = ["espera", "hoje", "canal", "clipes"].map(function (g) { return '<a href="#/' + g + '" data-g="' + g + '">' + ic(g) + "<span>" + TITULO[g] + "</span>" + (g === "espera" ? '<span class="contador" data-n="0"></span>' : "") + "</a>"; }).join("") + '<a href="#" data-act="menu" role="button">' + ic("mais") + "<span>Mais</span></a>";
    H.atualizaContador(); H.atualizaPilula();
    $("#main").innerHTML = '<div class="esqueleto" role="status" aria-label="Carregando"><i></i><i></i><i></i></div>';
    setTimeout(H.rerender, 450);
  };
})();
