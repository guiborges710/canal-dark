/* Núcleo compartilhado pelas três variantes: dados derivados, gráficos SVG, estado das decisões.
   Não desenha nenhuma tela: cada variante tem seu próprio HTML, CSS e JS. Sem segredos. */
(function () {
  var B = window.B = {};

  B.esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  B.n = function (v) { return new Intl.NumberFormat("pt-BR").format(v); };
  B.usd = function (v) { return "US$ " + v.toFixed(2).replace(".", ","); };

  /* ---------- ícones finos (traço 1,5) ---------- */
  var P = {
    inbox: '<path d="M4 13.5 6.4 6.2A2 2 0 0 1 8.3 5h7.4a2 2 0 0 1 1.9 1.2L20 13.5"/><path d="M4 13.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3.5h-4.2a1.3 1.3 0 0 0-1.2.8 3 3 0 0 1-5.2 0 1.3 1.3 0 0 0-1.2-.8z"/>',
    canal: '<rect x="3" y="5" width="18" height="14" rx="3.5"/><path d="m10.5 9.5 4 2.5-4 2.5z"/>',
    clipes: '<circle cx="6" cy="7" r="2.5"/><circle cx="6" cy="17" r="2.5"/><path d="M8 8.5 20 17M8 15.5 20 7"/>',
    inteligencia: '<path d="M5 19v-8M12 19V5M19 19v-5"/>',
    trabalho: '<rect x="3.5" y="7.5" width="17" height="12" rx="2.5"/><path d="M9 7.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v1.5M3.5 12.5h17"/>',
    financas: '<rect x="3.5" y="6" width="17" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.5"/>',
    programacao: '<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4M13.5 6l-3 12"/>',
    ecossistema: '<circle cx="12" cy="5.5" r="2.2"/><circle cx="5.5" cy="17.5" r="2.2"/><circle cx="18.5" cy="17.5" r="2.2"/><path d="M11 7.5 6.5 15.5M13 7.5l4.5 8M7.7 17.5h8.6"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    chev: '<path d="m9 5.5 6.5 6.5L9 18.5"/>',
    sun: '<circle cx="12" cy="12" r="3.8"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4"/>',
    moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>',
    alert: '<path d="M12 4 3 19.5h18z"/><path d="M12 10v4.5M12 17.2v.01"/>',
    lock: '<rect x="5" y="10.5" width="14" height="9.5" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>',
    user: '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 19.5c.8-3.5 3.6-5.5 7-5.5s6.2 2 7 5.5"/>',
    close: '<path d="M6 6l12 12M18 6 6 18"/>',
    copy: '<rect x="8.5" y="8.5" width="11" height="11" rx="2.5"/><path d="M15.5 8.5V6.5A2 2 0 0 0 13.5 4.5h-7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2"/>',
    retry: '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3M19.5 4.5v4h-4"/>'
  };
  B.icon = function (n, s) {
    s = s || 20;
    return '<svg class="ic" width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (P[n] || "") + "</svg>";
  };

  /* ---------- menu: 8 grupos ---------- */
  B.menu = [
    { id: "espera", nome: "Espera você", ic: "inbox" },
    { id: "canal", nome: "Canal", ic: "canal" },
    { id: "clipes", nome: "Clipes", ic: "clipes" },
    { id: "inteligencia", nome: "Inteligência", ic: "inteligencia" },
    { id: "trabalho", nome: "Trabalho", ic: "trabalho" },
    { id: "financas", nome: "Finanças", ic: "financas" },
    { id: "programacao", nome: "Programação", ic: "programacao" },
    { id: "ecossistema", nome: "Ecossistema", ic: "ecossistema" }
  ];
  B.rota = function () {
    var r = (location.hash.replace(/^#\/?/, "").split("/")[0]) || "espera";
    return B.menu.some(function (m) { return m.id === r; }) ? r : "espera";
  };
  B.setor = function (id) { return D.setores.filter(function (s) { return s.id === id; })[0] || { nome: id, chefe: "", desc: "" }; };

  /* ---------- gráficos em SVG inline ---------- */
  B.spark = function (v, w, h) {
    w = w || 120; h = h || 36;
    var pad = 3, mx = Math.max.apply(null, v), mn = Math.min.apply(null, v), sx = (w - pad * 2) / (v.length - 1);
    var pts = v.map(function (x, i) { return [pad + i * sx, h - pad - (x - mn) / ((mx - mn) || 1) * (h - pad * 2)]; });
    var line = "M" + pts.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join("L");
    var area = line + "L" + pts[pts.length - 1][0].toFixed(1) + " " + h + "L" + pts[0][0].toFixed(1) + " " + h + "Z";
    var l = pts[pts.length - 1];
    return '<svg class="spark" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="Tendência: de ' + B.n(v[0]) + " a " + B.n(v[v.length - 1]) + '"><path class="sp-area" d="' + area + '"/><path class="sp-line" d="' + line + '"/><circle class="sp-dot" cx="' + l[0].toFixed(1) + '" cy="' + l[1].toFixed(1) + '" r="2.6"/></svg>';
  };
  B.ring = function (pct, size, sw, label) {
    size = size || 84; sw = sw || 9;
    var r = (size - sw) / 2, c = 2 * Math.PI * r;
    return '<svg class="ring" width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + " " + size + '" role="img" aria-label="' + B.esc(label || pct + "%") + '"><circle class="rg-track" cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke-width="' + sw + '"/><circle class="rg-val" cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke-width="' + sw + '" stroke-linecap="round" stroke-dasharray="' + (c * pct / 100).toFixed(1) + " " + c.toFixed(1) + '" transform="rotate(-90 ' + size / 2 + " " + size / 2 + ')"/></svg>';
  };
  B.barsV = function (v, w, h, desc) {
    w = w || 280; h = h || 90;
    var mx = Math.max.apply(null, v), g = 5, bw = (w - g * (v.length - 1)) / v.length, o = "";
    v.forEach(function (x, i) {
      var bh = Math.max(3, x / mx * (h - 4));
      o += '<rect class="bar' + (i === v.length - 1 ? " bar-hi" : "") + '" x="' + (i * (bw + g)).toFixed(1) + '" y="' + (h - bh).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + bh.toFixed(1) + '" rx="' + Math.min(4, bw / 2).toFixed(1) + '"/>';
    });
    return '<svg class="barsv" viewBox="0 0 ' + w + " " + h + '" role="img" aria-label="' + B.esc(desc || "Gráfico de barras") + '">' + o + "</svg>";
  };

  /* ---------- tema claro/escuro ---------- */
  B.tema = function (chave, padrao) {
    var t = padrao;
    try { t = localStorage.getItem(chave) || padrao; } catch (e) {}
    document.documentElement.dataset.tema = t;
    return {
      get: function () { return document.documentElement.dataset.tema; },
      alternar: function () {
        t = t === "escuro" ? "claro" : "escuro";
        document.documentElement.dataset.tema = t;
        try { localStorage.setItem(chave, t); } catch (e) {}
        return t;
      }
    };
  };

  /* ---------- decisões (Espera você) ---------- */
  var feitas = {}, ordemFeitas = [];
  B.todas = D.decisoes.filter(function (d) { return !d.bloqueada; }).sort(function (a, b) { return a.ordem - b.ordem; });
  B.bloqueadas = D.decisoes.filter(function (d) { return d.bloqueada; });
  B.pendentes = function () { return B.todas.filter(function (d) { return !feitas[d.id]; }); };
  B.resolver = function (id, rotulo) { feitas[id] = rotulo; ordemFeitas.unshift(id); };
  B.desfazer = function (id) { delete feitas[id]; ordemFeitas = ordemFeitas.filter(function (x) { return x !== id; }); };
  B.historico = function () {
    var novas = ordemFeitas.map(function (id) {
      var d = B.todas.filter(function (x) { return x.id === id; })[0];
      return { q: "Agora", t: feitas[id] + ": " + d.titulo, c: d.cod };
    });
    return novas.concat(D.historicoDecisoes).slice(0, 5);
  };
  B.principal = function (d) {
    var a = d.acoes, i = -1, k;
    for (k = 0; k < a.length; k++) if (a[k].k === "ok") { i = k; break; }
    if (i < 0) for (k = 0; k < a.length; k++) if (a[k].k === "risco") { i = k; break; }
    return i < 0 ? 0 : i;
  };
  B.motivoPrincipal = function (d) { return d.acoes.length ? d.acoes[B.principal(d)] : null; };

  /* Trata o clique num botão de ação. Ação de risco pede um segundo clique. */
  B.agir = function (btn, d, i, depois) {
    var a = d.acoes[i];
    if (a.k === "copiar") {
      try { navigator.clipboard.writeText(btn.dataset.copia || d.titulo); } catch (e) {}
      btn.textContent = "Copiado";
      return;
    }
    if (a.k === "ver") { B.toast("No protótipo completo isto abre o editor."); return; }
    if (a.risco && btn.dataset.armado !== "1") {
      btn.dataset.armado = "1";
      btn.dataset.rotulo = btn.textContent;
      btn.textContent = "Confirmar: " + a.r;
      btn.classList.add("armado");
      setTimeout(function () { if (btn.isConnected && btn.dataset.armado === "1") { btn.dataset.armado = ""; btn.textContent = btn.dataset.rotulo; btn.classList.remove("armado"); } }, 4500);
      return;
    }
    B.resolver(d.id, a.r);
    B.toast(a.r + " (" + d.cod + ")", function () { B.desfazer(d.id); depois(); });
    depois();
  };
  B.devolver = function (d, motivo, depois) {
    B.resolver(d.id, "Pediu ajuste (" + motivo + ")");
    B.toast("Devolvido: " + motivo + " (" + d.cod + ")", function () { B.desfazer(d.id); depois(); });
    depois();
  };

  B.toast = function (msg, desfazer) {
    var box = document.getElementById("toast");
    if (!box) return;
    var t = document.createElement("div");
    t.className = "toast";
    t.innerHTML = '<span>' + B.esc(msg) + "</span>" + (desfazer ? '<button type="button">Desfazer</button>' : "");
    if (desfazer) t.querySelector("button").onclick = function () { desfazer(); t.remove(); };
    box.appendChild(t);
    setTimeout(function () { t.remove(); }, 6000);
  };

  /* folha de detalhe (celular): <dialog> nativo, com foco preso e Esc */
  B.sheet = function () {
    var d = document.getElementById("sheet");
    if (!d) {
      d = document.createElement("dialog");
      d.id = "sheet"; d.className = "sheet"; d.setAttribute("aria-label", "Detalhe da decisão");
      document.body.appendChild(d);
      d.addEventListener("click", function (e) { if (e.target === d || e.target.closest("[data-fechar]")) d.close(); });
    }
    return d;
  };
  B.estreito = function (px) { return window.matchMedia("(max-width:" + px + "px)").matches; };
  B.suave = function () { return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"; };

  /* ---------- Canal ---------- */
  B.nomesProj = {
    "a-recessao-de-amizades-entre-homens": "A recessão de amizades entre homens",
    "fim-dos-terceiros-lugares": "Fim dos terceiros lugares",
    "adultos-morando-com-os-pais": "Adultos morando com os pais",
    "cnh-aos-16-anos": "CNH aos 16 anos",
    "jovens-bebendo-menos": "Jovens bebendo menos",
    "geracao-z-nao-quer-filhos-ou-nao-pode-ter": "Geração Z não quer filhos ou não pode ter",
    "mulheres-nao-pararam-de-ter-filhos-adiaram": "Mulheres não pararam de ter filhos, adiaram",
    "jovens-trocam-de-emprego": "Jovens trocam de emprego"
  };
  B.estLabel = { rodando: "Rodando", erro: "Com erro", espera: "Espera você", bloq: "Bloqueado", ok: "Pronto", fila: "Na fila" };
  /* série ilustrativa de visualizações por dia (o protótipo não traz série diária) */
  B.viasDia = [212, 248, 236, 301, 288, 342, 415, 398, 377, 452, 501, 468, 530, 584];
  B.fluxoCanal = function () {
    return D.fluxos.canal.nos.map(function (n) { return { id: n.id, t: n.t, r: n.r, a: n.a, est: D.andamentoCanal[n.id] || "bloq" }; });
  };
  B.fases = [
    { nome: "Texto", ids: ["brief", "modric", "neymar", "courtois", "g_roteiro"] },
    { nome: "Visual", ids: ["raphinha", "mbappe", "g_comp", "olise", "g_cenas"] },
    { nome: "Auditoria e voz", ids: ["vini_t", "narr", "g_narr"] },
    { nome: "Render e entrega", ids: ["render", "vini_f", "g_video", "sidorf", "g_pub"] }
  ];
  B.canalKpis = function () {
    var s = B.viasDia, ult = s.slice(7).reduce(function (a, b) { return a + b; }, 0), pri = s.slice(0, 7).reduce(function (a, b) { return a + b; }, 0);
    var ret = Math.round(D.metricas.reduce(function (a, m) { return a + m.ret; }, 0) / D.metricas.length);
    var custo = D.jobs.reduce(function (a, j) { return a + j.custo; }, 0), teto = D.jobs.reduce(function (a, j) { return a + j.teto; }, 0);
    var nos = B.fluxoCanal(), feitos = nos.filter(function (n) { return n.est === "ok"; }).length;
    return {
      espera: B.pendentes().filter(function (d) { return d.setor === "canal"; }).length,
      ativos: D.projetos.filter(function (p) { return p.prog < 100; }).length, total: D.projetos.length,
      vis: s.reduce(function (a, b) { return a + b; }, 0), delta: Math.round((ult / pri - 1) * 100), serie: s,
      ret: ret, custo: custo, teto: teto, fila: D.fila.length, nos: nos, feitos: feitos
    };
  };
  B.nomeProj = function (slug) { return B.nomesProj[slug] || slug; };
  B.stub = function (id) { var s = B.setor(id); return s; };
})();
