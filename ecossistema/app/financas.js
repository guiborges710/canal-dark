/* Tela de Finanças do app (PROG-024b). Lê dados/financas.js (window.FINANCAS, contrato PROG-024a, centavos),
   gerado por: python estudio/dados/gerar_financas.py. Abre por duplo clique: o dado entra por <script>, sem servidor.
   Sem rede, sem segredos. Nenhum valor financeiro vive neste código. */
(function () {
  var app = document.getElementById("app"), esc = B.esc;
  var KO = "ce_h_fin_ocultar", KT = "ce_h_tema", KM = "ce_h_fin_mes";
  GH.tema(KT, "claro");
  /* fase: carregando | pronto | erro. F é a leitura já conferida e ajustada ao dia de hoje. */
  /* bloqueado: a tela não está aberta no próprio computador (rotas de Finanças só aceitam loopback). ?acesso=remoto só serve para teste. */
  function acessoLocal() { if (GH.q("acesso") === "remoto") return false; return location.protocol === "file:" || /^(localhost|127\.0\.0\.1|\[?::1\]?)$/.test(location.hostname); }
  var S = { ocultar: false, todas: false, entrou: false, fase: "carregando", F: null, motivo: "", mes: "", movN: 40, area: "financas", bloqueado: !acessoLocal() };
  /* painel dos 4 cards (PROG-024c): estado próprio, o <dialog> fica fora de #app para sobreviver a render() */
  var P = { tipo: "", mes: "", q: "", ord: "data-desc", dlg: null, empurrou: false, ignorar: false, tentou: false, atualizou: false, timer: 0, focoLinha: null };
  var rotaInicial = (location.hash || "").replace(/^#\/?/, "").split("/")[0]; if (B.menu.some(function (m) { return m.id === rotaInicial; })) S.area = rotaInicial;
  try { S.ocultar = localStorage.getItem(KO) === "1"; } catch (e) {}
  var MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
  var MESL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  var DIA = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
  var kbd = function (k) { return '<kbd aria-hidden="true">' + k + "</kbd>"; };

  /* ---------- formatação (só aqui; o JSON traz centavos) ---------- */
  function partes(c) { var a = Math.abs(Math.round(c)), cc = a % 100; return { neg: c < 0, r: B.n(Math.floor(a / 100)), c: (cc < 10 ? "0" : "") + cc }; }
  function T(c) { if (S.ocultar) return "valor oculto"; var p = partes(c); return (p.neg ? "−" : "") + "R$ " + p.r + "," + p.c; }
  var MASK = '<span class="vo" aria-hidden="true">R$ ••••</span><span class="so">valor oculto</span>';
  function R(c) { return S.ocultar ? MASK : esc(T(c)); }
  function RG(c) {
    if (S.ocultar) return '<span class="vo" aria-hidden="true">••••</span><span class="so">valor oculto</span>';
    var p = partes(c); return '<small class="rs">' + (p.neg ? "−" : "") + "R$</small>" + p.r + "<small>," + p.c + "</small>";
  }
  function K(c) { if (S.ocultar) return ""; return new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 }).format(c / 100); }
  /* Texto livre do CSV e mensagens do gerador podem conter valores ("R$ 10,00", "1234.56", "diferença de 500 centavos",
     "extrato: 1500"). Ao ocultar, todos viram "••••". */
  function mt(s) {
    s = String(s == null ? "" : s);
    if (!S.ocultar) return s;
    return s.replace(/R\$\s?[\d.]+(?:,\d{1,2})?/g, "R$ ••••").replace(/\d[\d.]*\s+centavos/gi, "•••• centavos")
      .replace(/(extrato\s*:?\s*)[\d.,]+/gi, "$1••••").replace(/\b\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?\b|\b\d+[,.]\d{1,2}\b/g, "••••");
  }
  function pct(p) { return String(p).replace(".", ",") + "%"; }
  function plural(n, a, b) { return n + " " + (n === 1 ? a : b); }
  function dm(iso) { var p = String(iso).slice(0, 10).split("-"); return p[2] + "/" + p[1]; }
  function hm(iso) { return dm(iso) + " às " + String(iso).slice(11, 16); }
  function dsem(iso) { var p = iso.slice(0, 10).split("-"); return DIA[new Date(+p[0], +p[1] - 1, +p[2]).getDay()]; }
  function dif(iso) { var p = String(iso).slice(0, 10).split("-"), n = new Date(), h = new Date(n.getFullYear(), n.getMonth(), n.getDate()); return Math.round((h - new Date(+p[0], +p[1] - 1, +p[2])) / 864e5); }
  function diasDesde(iso) { return Math.max(0, dif(iso)); }
  function mesAbrev(m) { return MES[+m.slice(5, 7) - 1]; }
  function mesLongo(m) { return MESL[+m.slice(5, 7) - 1] + " " + m.slice(0, 4); }
  function mesCurto(m) { return mesAbrev(m) + "/" + m.slice(0, 4); }
  function clamp(v) { return Math.max(0, Math.min(100, v)); }
  function frac(a, b) { return b > 0 ? clamp(Math.round(a * 100 / b)) : 0; }

  /* ---------- ícones de categoria (14, traço 1,5, currentColor). Candidatos a entrar em base.js ---------- */
  var CAT = {
    moradia: '<path d="M4 11 12 4l8 7M6 10v9.5h12V10M10 19.5v-5h4v5"/>',
    mercado: '<path d="M3.5 5h2.2l2 10h9.6l2-7.5H7"/><circle cx="9.5" cy="19" r=".9"/><circle cx="16.5" cy="19" r=".9"/>',
    restaurantes: '<path d="M7 4v6.5M10 4v6.5M7 10.5a1.5 1.5 0 0 0 3 0M8.5 12v8M17 20V4c-2.2 1-3.2 3.6-3.2 7H17"/>',
    transporte: '<path d="M4 15v-3l2.2-5h11.6L20 12v3zM4 15v2.5M20 15v2.5M8 12v.01M16 12v.01M4 15h16"/>',
    contas_servicos: '<path d="M13 3 6 13.2h5L10 21l7-10.2h-5z"/>',
    saude: '<path d="M10 4h4v6h6v4h-6v6h-4v-6H4v-4h6z"/>',
    lazer: '<path d="M4 8.5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2V10a2 2 0 0 0 0 4v1.5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V14a2 2 0 0 0 0-4zM14.5 7v10"/>',
    assinaturas: '<path d="M17 7H8.5A4.5 4.5 0 0 0 4 11.5M17 7l-2.5-2.5M17 7l-2.5 2.5M7 17h8.5a4.5 4.5 0 0 0 4.5-4.5M7 17l2.5-2.5M7 17l2.5 2.5"/>',
    educacao: '<path d="m2.5 9.5 9.5-4.5 9.5 4.5-9.5 4.5zM6.5 11.8v4.2c0 1 2.5 2.5 5.5 2.5s5.5-1.5 5.5-2.5v-4.2M21.5 9.5V15"/>',
    impostos: '<path d="M7 3.5h7.5l3.5 3.5v13.5H7zM14.5 3.5V7H18M10 17l5-5M10.5 12v.01M14.5 17v.01"/>',
    cartao: '<rect x="3.5" y="5.5" width="17" height="13" rx="2.5"/><path d="M3.5 10h17M7 14.5h3.5"/>',
    renda: '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19.5h14"/>',
    investimento: '<path d="M4 18.5 9.5 12.5l3.5 3.5L20 7.5M15 7.5h5v5"/>',
    outros: '<circle cx="6.5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="17.5" cy="12" r="1.3"/>'
  };
  var CATROT = { moradia: "Moradia", mercado: "Mercado", restaurantes: "Restaurantes", transporte: "Transporte", contas_servicos: "Contas e serviços", saude: "Saúde", lazer: "Lazer", assinaturas: "Assinaturas", educacao: "Educação", impostos: "Impostos", cartao: "Cartão", renda: "Renda", investimento: "Investimento", outros: "Outros" };
  var ALIAS = { contas: "contas_servicos", servicos: "contas_servicos", luz: "contas_servicos", agua: "contas_servicos", energia: "contas_servicos", internet: "contas_servicos", telefone: "contas_servicos", restaurante: "restaurantes", delivery: "restaurantes", supermercado: "mercado", feira: "mercado", alimentacao: "mercado", aluguel: "moradia", condominio: "moradia", casa: "moradia", combustivel: "transporte", carro: "transporte", uber: "transporte", farmacia: "saude", medico: "saude", academia: "saude", streaming: "assinaturas", assinatura: "assinaturas", faculdade: "educacao", curso: "educacao", escola: "educacao", imposto: "impostos", iptu: "impostos", ipva: "impostos", fatura: "cartao", salario: "renda", receita: "renda", freelance: "renda", investimentos: "investimento" };
  function catKey(n) {
    var k = String(n || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
    k = ALIAS[k] || k; return CAT[k] ? k : "outros";
  }
  function catRot(n) { var k = catKey(n); if (k !== "outros" || /^outros?$/i.test(n)) return CATROT[k]; var s = String(n || "sem categoria"); return s.charAt(0).toUpperCase() + s.slice(1); }
  function catIco(n, px) { return '<span class="cat-i" aria-hidden="true"><svg viewBox="0 0 24 24" width="' + (px || 20) + '" height="' + (px || 20) + '" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' + CAT[catKey(n)] + "</svg></span>"; }
  var EYE = '<svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg>';
  var EYEOFF = '<svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4l16 16M9.9 5.8A9 9 0 0 1 12 5.5c6 0 9.5 6.5 9.5 6.5a16 16 0 0 1-3 3.6M6.3 7.6A15.8 15.8 0 0 0 2.5 12S6 18.5 12 18.5a8.7 8.7 0 0 0 3.2-.6M10 10a3 3 0 0 0 4 4"/></svg>';
  var ICO_GASTO = '<svg class="eico e-gasto" width="18" height="18" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="currentColor"/><path d="m6.8 6.8 6.4 6.4M13.2 8.4v4.8H8.4" fill="none" stroke="var(--ico-fg,#fff)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  /* ---------- estado e derivados ---------- */
  function ehInt(v) { return typeof v === "number" && isFinite(v); }
  function ehLista(v) { return Array.isArray(v); }
  /* Confere o contrato antes de desenhar: se algo essencial faltar ou vier com tipo errado, é erro (nunca número antigo ou torto). */
  function valido(F) {
    try {
      if (!F || typeof F !== "object" || typeof F.gerado_em !== "string" || !/^\d{4}-\d{2}-\d{2}/.test(F.gerado_em) || !/^\d{4}-\d{2}$/.test(F.mes_atual || "")) return false;
      var s = F.saldos, r = F.recebido, g = F.gastos, x = F.receitas_x_gastos;
      if (!s || !ehLista(s.contas) || !ehInt(s.disponivel) || !r || !ehInt(r.mes) || !ehInt(r.previsto_mes) || !g || !ehInt(g.pagos_mes) || !ehInt(g.a_pagar_mes)) return false;
      if (!x || !ehInt(x.receitas) || !ehInt(x.gastos) || !ehLista(F.serie_mensal) || !ehLista(F.categorias) || !ehLista(F.vencimentos) || !ehLista(F.movimentos_recentes) || !ehLista(F.alertas)) return false;
      if (!F.pendencias || !ehLista(F.pendencias.abertas) || !F.fonte || !F.fonte.arquivos || !F.fonte.contagens) return false;
      var ok = s.contas.every(function (c) { return c && ehInt(c.saldo) && /^\d{4}-\d{2}-\d{2}/.test(c.data || ""); }) &&
        F.serie_mensal.every(function (m) { return m && /^\d{4}-\d{2}$/.test(m.mes || "") && ehInt(m.recebido) && ehInt(m.previsto) && ehInt(m.gasto_pago) && ehInt(m.gasto_a_pagar); }) &&
        F.categorias.every(function (c) { return c && ehInt(c.valor) && ehInt(c.percentual); }) &&
        F.vencimentos.every(function (v) { return v && ehInt(v.valor) && /^\d{4}-\d{2}-\d{2}/.test(v.data || ""); }) &&
        F.movimentos_recentes.every(function (m) { return m && ehInt(m.valor) && /^\d{4}-\d{2}-\d{2}/.test(m.data || ""); });
      return !!ok;
    } catch (e) { return false; }
  }
  /* Bloco opcional `meses` (seletor de mês). Se faltar ou vier torto, a tela cai para o comportamento de um mês só. */
  function mesesOk(F) {
    try {
      var d = F.meses_disponiveis, m = F.meses;
      if (!ehLista(d) || !d.length || !m || typeof m !== "object") return false;
      return d.every(function (k) {
        var x = m[k];
        return /^\d{4}-\d{2}$/.test(k) && x && ehInt(x.recebido) && ehInt(x.previsto) && ehInt(x.gasto_pago) && ehInt(x.gasto_a_pagar) && ehLista(x.categorias || []) && ehLista(x.movimentos || []) && ehLista(x.vencimentos || []) &&
          (x.categorias || []).every(function (c) { return c && ehInt(c.valor); }) && (x.movimentos || []).every(function (q) { return q && ehInt(q.valor) && /^\d{4}-\d{2}-\d{2}/.test(q.data || ""); }) &&
          (x.vencimentos || []).every(function (v) { return v && ehInt(v.valor) && /^\d{4}-\d{2}-\d{2}/.test(v.data || ""); });
      }) && d.indexOf(F.mes_atual) >= 0;
    } catch (e) { return false; }
  }
  function listaMeses(F) { return F && F.meses_disponiveis ? F.meses_disponiveis.slice() : F ? [F.mes_atual] : []; }
  function temLanc(F, k) { var x = F.meses && F.meses[k]; return x ? (x.movimentos || []).length > 0 : k === F.mes_atual && (F.movimentos_recentes || []).length > 0; }
  /* Visão do mês escolhido: tudo que a tela mostra "do mês" sai daqui. */
  function visao(F, m) {
    var x = F.meses && F.meses[m];
    if (x) {
      return { mes: m, recebido: x.recebido, previsto: x.previsto, pagos: x.gasto_pago, apagar: x.gasto_a_pagar, resultado: ehInt(x.saldo_do_mes) ? x.saldo_do_mes : x.recebido - x.gasto_pago,
        categorias: x.categorias || [], vencimentos: x.vencimentos || [], movimentos: (x.movimentos || []).slice().reverse(), completo: true };
    }
    return { mes: F.mes_atual, recebido: F.recebido.mes, previsto: F.recebido.previsto_mes, pagos: F.gastos.pagos_mes, apagar: F.gastos.a_pagar_mes, resultado: F.receitas_x_gastos.receitas - F.receitas_x_gastos.gastos,
      categorias: F.categorias, vencimentos: F.vencimentos, movimentos: F.movimentos_recentes, completo: false };
  }
  function mesInicial(F) {
    var ls = listaMeses(F), h = /^#mes=(\d{4}-\d{2})$/.exec(location.hash || ""), g = "";
    try { g = localStorage.getItem(KM) || ""; } catch (e) {}
    return h && ls.indexOf(h[1]) >= 0 ? h[1] : ls.indexOf(g) >= 0 ? g : F.mes_atual;
  }
  function escolherMes(m, foco) {
    if (!S.F || listaMeses(S.F).indexOf(m) < 0) return;
    if (m !== S.mes) { S.mes = m; S.movN = 40; S.todas = false; }
    try { localStorage.setItem(KM, m); } catch (e) {}
    try { history.replaceState(null, "", "#mes=" + m); } catch (e) {}
    render();
    if (foco) { var c = document.querySelector('.mb-chip[data-mes="' + m + '"]'); if (c) c.focus({ preventScroll: true }); }
  }
  function vizinho(d) { var ls = listaMeses(S.F), i = ls.indexOf(S.mes) + d; return i >= 0 && i < ls.length ? ls[i] : null; }

  /* Ajusta ao dia de hoje o que o gerador congelou na hora em que rodou (dias até o vencimento, idade dos saldos). */
  function normalizar(F) {
    var c = JSON.parse(JSON.stringify(F));
    function vv(v) { var d = -dif(v.data); v.dias_restantes = d; v.atrasado = d < 0; v.status = d < 0 ? "vencido" : d === 0 ? "vence hoje" : "a pagar"; }
    if (!mesesOk(c)) { delete c.meses; delete c.meses_disponiveis; } else Object.keys(c.meses).forEach(function (k) { (c.meses[k].vencimentos || []).forEach(vv); });
    c.vencimentos.forEach(function (v) { var d = -dif(v.data); v.dias_restantes = d; v.atrasado = d < 0; v.status = d < 0 ? "vencido" : d === 0 ? "vence hoje" : "a pagar"; });
    c.saldos.contas.forEach(function (a) { a.idade_dias = diasDesde(a.data); });
    return c;
  }
  function estado(F) {
    if (S.fase === "carregando") return "carregando";
    if (S.fase === "erro" || !F) return "erro";
    var c = (F.fonte && F.fonte.contagens) || {};
    if (!c.movimentos && !c.contas && !(F.saldos.contas || []).length && !(F.movimentos_recentes || []).length) return "vazio";
    return "ok";
  }
  function estVenc(v) { return v.atrasado || v.dias_restantes < 0 ? "erro" : v.dias_restantes <= 3 ? "pendente" : "backlog"; }
  function textoVenc(v) {
    var d = v.dias_restantes;
    if (d < 0) return "Vencido há " + plural(-d, "dia", "dias");
    if (d === 0) return "Vence hoje";
    if (d === 1) return "Vence amanhã";
    return "Vence em " + d + " dias";
  }
  function chip(e, t) { return '<span class="est e-' + e + '">' + GH.ico(e, 16) + "<span>" + esc(t) + "</span></span>"; }
  /* Chip de status sem ícone: só a cor diferencia (Pago vermelho, Recebido verde). */
  function chipCor(e, t, cor) { return '<span class="est est-so e-' + e + (cor ? " " + cor : "") + '"><span>' + esc(t) + "</span></span>"; }
  /* Barra que dá ideia de valor (proporção entre valores): some quando os valores estão ocultos. */
  function barraV(e, p, rot, cls) { return S.ocultar ? "" : barra(e, p, rot, cls); }
  function barra(e, p, rot, cls) { return '<div class="pb e-' + e + " " + (cls || "") + '" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + p + '" aria-label="' + esc(mt(rot)) + '"><i style="width:' + p + '%"></i></div>'; }

  /* ---------- ilha ---------- */
  var AINDA = "Esta tela ainda não existe neste app. Ela chega com a casca completa do sistema.";
  function href(id) { return "#principal"; }
  /* PROG-024c: cada número da ilha é um botão que abre o painel com os movimentos que o formam.
     Dentro de <button> só cabe conteúdo de texto corrido (sem <div>): as barras viram <span>. */
  var PNID = ["saldo", "recebido", "gasto", "a-pagar"];
  var PNROT = { saldo: "Saldo disponível: ver movimentos que o compõem", recebido: "Recebido no mês: ver movimentos", gasto: "Gasto pago no mês: ver movimentos", "a-pagar": "A pagar no mês: ver movimentos" };
  function celula(cls, ico, rot, nn, ns, mini, pn, off) {
    var m = (mini || "").replace(/<div /g, "<span ").replace(/<\/div>/g, "</span>");
    return '<button type="button" class="nm ' + cls + '" data-pn="' + pn + '" aria-label="' + PNROT[pn] + '" aria-describedby="nn-' + pn + '"' + (off ? ' aria-disabled="true"' : "") + ">" + ico + '<span class="nr">' + rot + '</span><span class="nn" id="nn-' + pn + '">' + nn + "</span>" + ns +
      (S.bloqueado ? '<span class="ns bloq">Bloqueado: abra no computador</span>' : "") + (m ? '<span class="mini">' + m + "</span>" : "") +
      '<span class="nm-go" aria-hidden="true"><span class="nm-dica">Ver movimentos</span><span class="nm-seta">›</span></span></button>';
  }
  function numeros(F, est) {
    var sk = '<span class="sk sk-n"></span>', sk2 = '<span class="ns"><span class="sk sk-t"></span></span>', nd = '<span class="nd">—</span>';
    var ics = [B.icon("financas", 18), GH.ico("ok", 18), ICO_GASTO, GH.ico("pendente", 18)];
    var cls = ["saldo", "", "", ""];
    var mc = F && S.mes ? mesCurto(S.mes) : "mês";
    var rots = ["Saldo disponível", "Recebido em " + mc, "Gasto pago em " + mc, "A pagar em " + mc];
    if (est === "carregando" || !F || !F.saldos) {
      var t = est === "carregando" ? sk : nd, ns = est === "carregando" ? sk2 : '<span class="ns">sem leitura</span>';
      return [0, 1, 2, 3].map(function (i) { return celula(cls[i], ics[i], rots[i], t, ns, "", PNID[i], true); }).join("");
    }
    var sd = F.saldos, V = visao(F, S.mes), vs = V.vencimentos;
    var fora = (sd.contas_fora_do_disponivel || []).length;
    var datas = sd.contas.map(function (c) { return c.data; }).sort(), ult = datas.length ? dm(datas[datas.length - 1]) : "";
    var c1 = celula("saldo", ics[0], rots[0], RG(sd.disponivel),
      '<span class="ns">' + (sd.contas.length ? plural(sd.contas.length, "conta", "contas") + ", saldo informado até " + ult : "nenhuma conta informada") + "</span>" +
      '<span class="ns fixo">Saldo de hoje: não muda com o mês escolhido</span>' +
      (fora ? '<span class="ns parc">Parcial: ' + plural(fora, "conta fora", "contas fora") + " do total</span>" : ""), "", "saldo", S.bloqueado);
    var c2 = celula("", ics[1], rots[1], RG(V.recebido), '<span class="ns">mais ' + R(V.previsto) + " a receber</span>",
      barraV("ok", frac(V.recebido, V.recebido + V.previsto), "Recebido: " + T(V.recebido) + " de " + T(V.recebido + V.previsto) + " previstos em " + mesLongo(S.mes), "fx"), "recebido", S.bloqueado);
    var c3 = celula("", ics[2], rots[2], RG(V.pagos), '<span class="ns">pago; mais ' + R(V.apagar) + " a pagar</span>" + '<span class="ns">só o que já foi pago</span>',
      barraV("gasto", frac(V.pagos, V.pagos + V.apagar), "Gasto pago: " + T(V.pagos) + " de " + T(V.pagos + V.apagar) + " em " + mesLongo(S.mes), "fx"), "gasto", S.bloqueado);
    var atr = vs.filter(function (v) { return v.atrasado || v.dias_restantes < 0; }), hoje = vs.filter(function (v) { return v.dias_restantes === 0; });
    var urg = soma(atr) + soma(hoje), ie = atr.length ? "erro" : "pendente";
    var ns4 = '<span class="ns">' + (vs.length ? plural(vs.length, "vencimento", "vencimentos") : "nenhum vencimento") + (atr.length ? ' · <b class="atr">' + plural(atr.length, "atrasado", "atrasados") + "</b>" : "") + "</span>";
    var c4 = celula("", GH.ico(ie, 18), rots[3], RG(V.apagar), ns4, V.apagar > 0 && vs.length ? barraV(ie, frac(urg, V.apagar), "Parte já vencida ou vencendo hoje: " + T(urg) + " de " + T(V.apagar), "fx") : "", "a-pagar", S.bloqueado);
    return c1 + c2 + c3 + c4;
  }
  /* Seletor de mês: setas + chips (rolagem horizontal), com o resultado do mês logo abaixo. */
  function seletor(F, est) {
    if (est !== "ok" || !F) return "";
    var ls = listaMeses(F), V = visao(F, S.mes), ant = vizinho(-1), prox = vizinho(1), sobra = V.resultado >= 0;
    var chips = ls.map(function (m) {
      var sel = m === S.mes;
      return '<button type="button" class="mb-chip' + (sel ? " sel" : "") + '" data-mes="' + m + '" aria-pressed="' + sel + '" tabindex="' + (sel ? 0 : -1) + '">' + esc(mesLongo(m)) + (m === F.mes_atual ? '<em class="mb-at">atual</em>' : "") + "</button>";
    }).join("");
    var seta = function (id, m, rot, d) { return '<button type="button" class="bt-i ic1 mb-seta" id="' + id + '"' + (m ? ' data-mes="' + m + '"' : " disabled") + ' aria-label="' + rot + (m ? ": " + mesLongo(m) : " (não há)") + '" title="' + rot + '">' + d + "</button>"; };
    var L = '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>';
    var Rr = '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>';
    return '<div class="mes-bar" id="mes-bar" role="group" aria-label="Escolher o mês (setas do teclado trocam de mês)"><span class="mb-t">Mês</span>' + seta("mes-ant", ant, "Mês anterior", L) +
      '<div class="mb-chips" id="mb-chips">' + chips + "</div>" + seta("mes-prox", prox, "Próximo mês", Rr) + "</div>" +
      '<p class="mb-res" aria-live="polite"><b>' + esc(mesLongo(S.mes)) + ":</b> resultado das movimentações " + (sobra ? "sobra " : "falta ") + '<b class="' + (sobra ? "pos" : "neg") + '">' + R(Math.abs(V.resultado)) + "</b> (recebido menos gasto pago; não é saldo bancário)." + (F.meses ? "" : " Esta leitura só traz o mês atual.") + "</p>";
  }
  function soma(l) { return l.reduce(function (a, v) { return a + v.valor; }, 0); }

  function selo(F, est) {
    if (est === "carregando") return '<div class="selo">' + chip("rodando", "Lendo os dados") + "</div>";
    if (!F || est === "erro") return '<div class="selo">' + chip("erro", "Sem leitura") + '<span class="s-t">' + esc(S.motivo === "invalido" ? "dados/financas.js inválido" : "dados/financas.js não encontrado") + "</span></div>";
    var idade = diasDesde(F.gerado_em), arq = (F.fonte && F.fonte.arquivos) || {}, ks = Object.keys(arq), ok = ks.filter(function (k) { return arq[k]; }).length;
    var c = idade === 0 ? chip("ok", "Lido hoje") : chip(idade > 3 ? "erro" : "pendente", "Dados velhos há " + plural(idade, "dia", "dias"));
    return '<div class="selo" role="group" aria-label="Última leitura">' + c + '<span class="s-t">Gerado em ' + hm(F.gerado_em) + " · " + ok + " de " + ks.length + " fontes</span></div>";
  }
  function legenda() {
    var L = [["ok", "Pago ou recebido", "Dinheiro que já entrou ou saiu"], ["erro", "Vencido ou inconsistente", "Passou do prazo ou os dados se contradizem"], ["pendente", "Vence em até 3 dias", "Pede atenção agora"], ["backlog", "A pagar ou previsto", "Ainda não aconteceu"], ["rodando", "Lendo os dados", "Atualizando a leitura"]];
    return '<ul class="legenda leg-h" aria-label="Legenda dos estados">' + L.map(function (x) { return '<li class="e-' + x[0] + '" title="' + esc(x[2]) + '">' + GH.ico(x[0], 18) + "<span>" + x[1] + "</span></li>"; }).join("") + "</ul>";
  }
  function ilha(F, est) {
    var escuro = document.documentElement.dataset.tema === "escuro", financeiro = S.area === "financas";
    var nav = B.menu.map(function (m, i) { return '<a class="aba" href="#/' + m.id + '"' + (S.area === m.id ? ' aria-current="page"' : "") + '>' + B.icon(m.ic, 18) + "<span>" + esc(m.nome) + "</span>" + kbd(i + 1) + "</a>"; }).join("");
    return '<header class="ilha"><div class="i-in"><div class="i-top"><div class="marca">' + GH.slot({ n: "logo_contexto_explica", k: "logo", px: 34 }) + "<span>Ecossistema do Guilherme</span></div>" +
      '<button class="busca" type="button" id="abrir-paleta" aria-label="Buscar ou comandar (Ctrl K)">Buscar tela ou comando <kbd>Ctrl K</kbd></button>' +
      '<div class="i-ferr">' + (financeiro ? '<button class="bt-i" type="button" id="ocultar" aria-pressed="' + S.ocultar + '">' + (S.ocultar ? EYEOFF : EYE) + '<span class="bl">' + (S.ocultar ? "Mostrar valores" : "Ocultar valores") + "</span></button>" : "") +
      '<button class="bt-i ic1" type="button" id="tema" aria-label="Alternar tema">' + B.icon(escuro ? "sun" : "moon", 20) + "</button></div></div>" +
      '<nav class="i-nav" aria-label="Grupos">' + nav + "</nav>" +
      '<p class="nav-dica" aria-hidden="true">Deslize para ver todos os grupos <span>→</span></p>' +
      (financeiro ? seletor(F, est) + '<div class="i-nums" aria-label="Resumo do mes">' + numeros(F, est) + "</div>" + '<div class="i-leg">' + legenda() + selo(F, est) + "</div>" : "") + "</div></header>";
  }
  /* ---------- seções ---------- */
  var SEV = { saldo_divergente: "erro", pago_sem_lancamento: "erro", linha_invalida: "erro", saldo_nao_confirmado: "pendente", saldo_velho: "pendente", valor_estimado: "pendente" };
  var FAZER = {
    saldo_divergente: "Compare com o extrato citado e peça ao Casemiro para corrigir o saldo em saldos.csv.",
    pago_sem_lancamento: "Se já pagou, peça ao Casemiro para marcar como pago. Nada é marcado sozinho.",
    linha_invalida: "Corrija a linha indicada no CSV. Ela foi ignorada nesta leitura.",
    saldo_nao_confirmado: "Confirme o saldo no app do banco e informe ao Casemiro. Ele fica fora do total até lá.",
    saldo_velho: "Informe o saldo de hoje ao Casemiro.",
    valor_estimado: "Troque pelo valor real quando a cobrança chegar."
  };
  var SEVROT = { erro: "Inconsistência", pendente: "Atenção" };
  function secAlertas(F) {
    var al = (F.alertas || []).filter(function (a) { return a.tipo !== "pendencia_aberta"; }).sort(function (a, b) { return (SEV[a.tipo] === "erro" ? 0 : 1) - (SEV[b.tipo] === "erro" ? 0 : 1); });
    var pe = F.pendencias || { abertas: [], resolvidas: 0 }, ne = al.filter(function (a) { return SEV[a.tipo] === "erro"; }).length;
    var rot = al.length || pe.abertas.length ? (ne ? plural(ne, "inconsistência", "inconsistências") + ", " : "") + plural(al.length - ne + pe.abertas.length, "atenção", "atenções") : "tudo conferido";
    if (!al.length && !pe.abertas.length) {
      return '<section class="cartao ok-linha" id="alertas" aria-label="Alertas"><h2>Alertas<span>' + rot + '</span></h2><p class="nada">' + GH.ico("ok", 18) + "<span>Nada fora do lugar nesta leitura. Saldos, lançamentos e pendências estão consistentes.</span></p></section>";
    }
    var li = al.map(function (a) {
      var e = SEV[a.tipo] || "pendente";
      return '<li class="al e-' + e + '"><span class="al-i">' + GH.ico(e, 20) + '</span><div class="al-c"><p class="al-m">' + esc(mt(a.mensagem)) + '</p><p class="al-o">Origem: <code>' + esc(a.origem) + '</code></p><p class="al-f"><b>O que fazer:</b> ' + esc(FAZER[a.tipo] || "Confira a origem indicada.") + "</p></div>" + chip(e, SEVROT[e]) + "</li>";
    }).join("");
    var pl = pe.abertas.map(function (t) { return '<li class="al e-pendente"><span class="al-i">' + GH.ico("pendente", 20) + '</span><div class="al-c"><p class="al-m">' + esc(mt(t)) + "</p></div></li>"; }).join("");
    return '<section class="cartao" id="alertas" aria-label="Alertas"><h2>Alertas<span>' + rot + ' · da leitura toda, não só do mês</span></h2>' +
      '<div class="al-g' + (al.length ? "" : " solo") + '">' + (al.length ? '<div><h3 class="sub-h">Inconsistências dos dados</h3><ul class="als">' + li + "</ul></div>" : "") +
      '<div class="al-p"><h3 class="sub-h">Pendências abertas<span>' + pe.resolvidas + " resolvidas</span></h3>" +
      (pe.abertas.length ? '<ul class="als">' + pl + "</ul>" : '<p class="mudo pq">Nenhuma pendência aberta.</p>') +
      (pe.arquivo_ausente ? '<p class="mudo pq">pendencias.md não foi encontrado.</p>' : "") + "</div></div></section>";
  }

  function secSerie(F) {
    var sm = F.serie_mensal;
    var tab = '<table class="so"><caption>Série dos últimos 6 meses, em reais</caption><thead><tr><th>Mês</th><th>Recebido</th><th>Previsto</th><th>Gasto pago</th><th>A pagar</th></tr></thead><tbody>' +
      sm.map(function (m) { return "<tr><th>" + mesAbrev(m.mes) + "</th><td>" + T(m.recebido) + "</td><td>" + T(m.previsto) + "</td><td>" + T(m.gasto_pago) + "</td><td>" + T(m.gasto_a_pagar) + "</td></tr>"; }).join("") + "</tbody></table>";
    var lg = '<ul class="ser-leg"><li><i class="sw sw-ok"></i>Recebido</li><li><i class="sw sw-prev"></i>Previsto</li><li><i class="sw sw-gas"></i>Gasto pago</li><li><i class="sw sw-prev"></i>A pagar</li></ul>';
    return '<section class="cartao" aria-label="Série mensal"><h2>Últimos 6 meses<span>' + (sm.length ? "até " + mesAbrev(sm[sm.length - 1].mes) : "") + '</span></h2>' + lg + '<div id="serie-box" class="serie-box"></div><p class="obs">Toque ou clique numa barra para ver aquele mês por inteiro. Mês escolhido: <b>' + esc(mesLongo(S.mes)) + "</b>.</p>" + tab + "</section>";
  }
  function desenharSerie() {
    var box = document.getElementById("serie-box"), F = S.F;
    if (!box || !F) return;
    box.innerHTML = "";
    if (S.ocultar) { box.innerHTML = '<p class="nada oculto-g">' + GH.ico("backlog", 18) + "<span>Gráfico escondido junto com os valores: a altura das barras mostraria quanto é. Toque em Mostrar valores (ou tecle O) para vê-lo.</span></p>"; return; }
    var sm = F.serie_mensal, W = Math.max(280, box.clientWidth), Hh = Math.max(236, Math.min(400, box.clientHeight)), pt = 24, pb = 28, px = 4, n = sm.length;
    var max = Math.max.apply(null, [1].concat(sm.map(function (m) { return Math.max(m.recebido + m.previsto, m.gasto_pago + m.gasto_a_pagar); })));
    function y(v) { return pt + (Hh - pt - pb) * (1 - v / max); }
    var gw = (W - px * 2) / n, bw = Math.min(36, gw * .36), gap = 4, o = "", g = "";
    [0, .5, 1].forEach(function (f) { var yy = y(max * f); g += '<line class="grade" x1="0" x2="' + W + '" y1="' + yy.toFixed(1) + '" y2="' + yy.toFixed(1) + '"/>'; });
    function barra(x, v, cls, tit, i) {
      if (v <= 0) return "";
      return '<rect class="sbar ' + cls + '" style="--i:' + i + '" x="' + x.toFixed(1) + '" y="' + y(v).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(2, Hh - pb - y(v)).toFixed(1) + '" rx="3"><title>' + esc(tit) + "</title></rect>";
    }
    function emp(x, base, v, cls, tit, i) { // trecho tracejado empilhado
      if (v <= 0) return "";
      return '<rect class="sbar ' + cls + '" style="--i:' + i + '" x="' + (x + .75).toFixed(1) + '" y="' + y(base + v).toFixed(1) + '" width="' + (bw - 1.5).toFixed(1) + '" height="' + Math.max(2, y(base) - y(base + v)).toFixed(1) + '" rx="3"><title>' + esc(tit) + "</title></rect>";
    }
    sm.forEach(function (m, i) {
      var cx = px + gw * i + gw / 2, xr = cx - gap / 2 - bw, xg = cx + gap / 2, atual = m.mes === S.mes, pode = listaMeses(F).indexOf(m.mes) >= 0;
      o += '<g class="sg' + (pode ? " pode" : "") + '" data-mes="' + m.mes + '">' + (atual ? '<rect class="sel-bg" x="' + (px + gw * i + 2).toFixed(1) + '" y="2" width="' + (gw - 4).toFixed(1) + '" height="' + (Hh - 4) + '" rx="8"/>' : "") + '<rect class="hit" x="' + (px + gw * i).toFixed(1) + '" y="0" width="' + gw.toFixed(1) + '" height="' + Hh + '"/>';
      o += barra(xr, m.recebido, "b-rec", "Recebido em " + mesAbrev(m.mes) + ": " + T(m.recebido), i) + emp(xr, m.recebido, m.previsto, "b-prev", "Previsto em " + mesAbrev(m.mes) + ": " + T(m.previsto), i);
      o += barra(xg, m.gasto_pago, "b-gas", "Gasto pago em " + mesAbrev(m.mes) + ": " + T(m.gasto_pago), i) + emp(xg, m.gasto_pago, m.gasto_a_pagar, "b-prev", "A pagar em " + mesAbrev(m.mes) + ": " + T(m.gasto_a_pagar), i);
      if (atual && !S.ocultar) {
        if (m.recebido > 0) o += '<text class="vl-t" x="' + (cx - 2).toFixed(1) + '" y="' + (y(m.recebido + m.previsto) - 6).toFixed(1) + '" text-anchor="end">' + K(m.recebido) + "</text>";
        if (m.gasto_pago > 0) o += '<text class="vl-t" x="' + (cx + 2).toFixed(1) + '" y="' + (y(m.gasto_pago + m.gasto_a_pagar) - 6).toFixed(1) + '" text-anchor="start">' + K(m.gasto_pago) + "</text>";
      }
      o += '<text class="mes' + (atual ? " mes-a" : "") + '" x="' + cx.toFixed(1) + '" y="' + (Hh - 8) + '" text-anchor="middle">' + mesAbrev(m.mes) + "</text></g>";
    });
    box.innerHTML = '<svg class="serie' + (S.entrou ? "" : " entra") + '" viewBox="0 0 ' + W + " " + Hh + '" width="' + W + '" height="' + Hh + '" role="img" aria-label="Barras por mês: recebido ao lado do gasto pago, com previsto e a pagar tracejados. Os valores estão na tabela abaixo. Clique numa barra para escolher o mês.">' + g + '<line class="base" x1="0" x2="' + W + '" y1="' + (Hh - pb) + '" y2="' + (Hh - pb) + '"/>' + o + "</svg>";
    S.entrou = true;
    box.querySelectorAll("g.sg.pode").forEach(function (g) { g.onclick = function () { escolherMes(g.getAttribute("data-mes"), false); }; });
  }

  function secRxG(F, V) {
    var mx = Math.max(V.recebido, V.pagos, 1), sobra = V.recebido - V.pagos, proj = V.recebido + V.previsto - V.pagos - V.apagar;
    function ln(rot, v, e, cls) { return '<div class="rg2"><div class="rg2-t"><span>' + rot + "</span><b>" + R(v) + "</b></div>" + barraV(e, frac(v, mx), rot + ": " + T(v), "grosso " + cls) + "</div>"; }
    function res(rot, v) { var p = v >= 0; return "<div><dt>" + rot + "</dt><dd class=\"" + (p ? "pos" : "neg") + '">' + (p ? "Sobra " : "Falta ") + R(Math.abs(v)) + "</dd></div>"; }
    return '<section class="cartao" aria-label="Receitas e gastos de ' + esc(mesLongo(V.mes)) + '"><h2>Receitas e gastos<span>' + esc(mesLongo(V.mes)) + "</span></h2>" + ln("Receitas", V.recebido, "ok", "") + ln("Gastos pagos", V.pagos, "gasto", "") +
      "<dl class=\"res\">" + res("Resultado das movimentações do mês (recebido menos gasto pago; não é saldo bancário)", sobra) + res("Se o previsto e o a pagar acontecerem", proj) + "</dl></section>";
  }

  function secContas(F) {
    var sd = F.saldos, fora = sd.contas_fora_do_disponivel || [];
    var li = sd.contas.map(function (c) {
      var fl = "";
      if (c.nao_confirmado) fl += chip("pendente", "Não confirmado");
      if (c.historico) fl += chip("backlog", "Histórico");
      if (c.idade_dias > 7) fl += chip("pendente", "Saldo de há " + c.idade_dias + " dias");
      if (fora.indexOf(c.conta) >= 0) fl += '<span class="est fora"><span>Fora do total</span></span>';
      return '<li class="cta"><div class="cta-t"><b>' + esc(c.conta) + '</b><span class="mudo">informado em ' + dm(c.data) + (c.idade_dias ? " (há " + plural(c.idade_dias, "dia", "dias") + ")" : " (hoje)") + (c.observacao && !c.nao_confirmado && !c.historico ? " · " + esc(mt(c.observacao)) : "") + '</span></div><span class="cta-v">' + R(c.saldo) + '</span><div class="cta-f">' + fl + "</div></li>";
    }).join("");
    return '<section class="cartao" aria-label="Saldo por conta"><h2>Contas<span>saldo de hoje, não depende do mês · total ' + R(sd.disponivel) + "</span></h2>" + (li ? '<ul class="ctas">' + li + "</ul>" : '<p class="mudo pq">Nenhuma conta informada ainda.</p>') +
      (fora.length ? '<p class="parcial">' + GH.ico("pendente", 16) + "<span>O total é parcial: " + esc(fora.join(", ")) + (fora.length > 1 ? " ficam" : " fica") + " de fora.</span></p>" : "") +
      '<p class="obs">' + esc(sd.observacao || "") + "</p></section>";
  }

  function secCategorias(F, V) {
    var cs = V.categorias || [], mx = cs.length ? cs[0].valor : 1, vis = S.todas ? cs : cs.slice(0, 8);
    if (!cs.length) return '<section class="cartao" aria-label="Gastos por categoria"><h2>Gastos por categoria<span>' + esc(mesLongo(V.mes)) + '</span></h2><p class="mudo pq">Nenhum gasto lançado em ' + esc(mesLongo(V.mes)) + '.</p></section>';

    /* Detecta categorias duplicadas (mesmo nome, ortografia diferente) */
    var catNoms = cs.map(function (c) { return catRot(c.categoria); });
    var dups = catNoms.filter(function (nom, i) { return catNoms.indexOf(nom) !== i; });
    var avDup = dups.length ? '<div class="al" style="background:color-mix(in srgb, var(--c-erro) 10%, transparent);border-left-color:var(--c-erro);margin:12px 0;padding:10px;border-radius:4px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="flex-shrink:0;margin-right:8px;"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16v.01"/></svg><span style="flex:1;"><b>Categorias duplicadas:</b> ' + esc(Array.from(new Set(dups)).join(", ")) + '. Clique em uma categoria para editar seus movimentos e unificá-las.</span></div>' : '';

    var li = vis.map(function (c) {
      return '<li class="cat" data-categoria="' + esc(c.categoria) + '" style="cursor:pointer;">' + catIco(c.categoria, 20) + '<span class="cat-n">' + esc(catRot(c.categoria)) + '</span><span class="cat-p">' + pct(c.percentual) + '</span><span class="cat-v">' + R(c.valor) + "</span>" + barra("gasto", frac(c.valor, mx), catRot(c.categoria) + ": " + pct(c.percentual) + " dos gastos do mês", "cat-b") + "</li>";
    }).join("");
    return '<section class="cartao" aria-label="Gastos por categoria"><h2>Gastos por categoria<span>' + esc(mesLongo(V.mes)) + ", pagos e a pagar</span></h2>" + avDup + "<ul class=\"cats\">" + li + "</ul>" +
      (cs.length > 8 ? '<button class="bt mais" type="button" id="ver-todas" aria-expanded="' + S.todas + '">' + (S.todas ? "Mostrar só as 8 maiores" : "Mostrar todas (" + cs.length + ")") + "</button>" : "") + "</section>";
  }

  function secVenc(F, V) {
    var vs = V.vencimentos || [], atr = vs.filter(function (v) { return v.atrasado || v.dias_restantes < 0; }).length;
    var rot = vs.length ? plural(vs.length, "a pagar", "a pagar") + (atr ? ", " + plural(atr, "atrasado", "atrasados") : "") : "";
    if (!vs.length) return '<section class="cartao" aria-label="Vencimentos"><h2>Vencimentos<span>' + esc(mesLongo(V.mes)) + ': nenhum</span></h2><p class="nada">' + GH.ico("ok", 18) + "<span>Nenhum vencimento a pagar em " + esc(mesLongo(V.mes)) + ". Quando o Casemiro lançar um gasto como a pagar, ele aparece aqui com os dias restantes.</span></p></section>";
    var li = vs.map(function (v) {
      var e = estVenc(v), p = v.dias_restantes < 0 ? 100 : clamp(Math.round((30 - v.dias_restantes) * 100 / 30));
      return '<li class="vc e-' + e + '">' + catIco(v.categoria, 20) + '<div class="vc-t"><b>' + esc(mt(v.descricao)) + '</b><span class="mudo">' + dsem(v.data) + ", " + dm(v.data) + " · " + esc(catRot(v.categoria)) + '</span></div><span class="vc-v">' + R(v.valor) + '</span><div class="vc-s">' + chip(e, textoVenc(v)) + barra(e, p, textoVenc(v) + ", " + T(v.valor), "") + "</div></li>";
    }).join("");
    return '<section class="cartao" aria-label="Vencimentos"><h2>Vencimentos<span>' + esc(mesLongo(V.mes)) + ": " + rot + '</span></h2><ul class="vcs">' + li + "</ul>" + '<p class="obs">A barra enche conforme o prazo se aproxima (janela de 30 dias).</p></section>';
  }

  function secMov(F, V) {
    var ms = V.movimentos || [], nome = esc(mesLongo(V.mes));
    if (!ms.length) return '<section class="cartao" aria-label="Movimentos"><h2>Movimentos<span>nenhum</span></h2><p class="mudo pq">Sem movimentos em ' + nome + ".</p></section>";
    var vis = ms.slice(0, S.movN);
    var li = vis.map(function (m) {
      var rec = m.tipo !== "gasto", pago = m.status === "pago", venc = !rec && !pago && dif(m.data) > 0, e = pago ? "ok" : venc ? "erro" : "backlog";
      var rot = pago ? (rec ? "Recebido" : "Pago") : venc ? "Vencido" : (rec ? "A receber" : "A pagar");
      var alerta = venc ? '<svg class="mv-alerta" role="img" aria-label="Vencido há ' + plural(dif(m.data), "dia", "dias") + '" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><title>Vencido há ' + plural(dif(m.data), "dia", "dias") + '</title><path d="M12 3.5 2.8 19.5h18.4z"/><path d="M12 10v4.5M12 17.2v.01"/></svg>' : "";
      return '<li class="mv' + (venc ? " mv-venc" : "") + '"><time class="mv-d" datetime="' + esc(m.data) + '">' + dm(m.data) + "</time>" + catIco(m.categoria, 18) + '<div class="mv-t"><b>' + alerta + esc(mt(m.descricao)) + '</b><span class="mudo">' + esc(catRot(m.categoria)) + '</span></div><span class="mv-s">' + chipCor(e, rot, pago ? (rec ? "st-recebido" : "st-pago") : "") + '</span><span class="mv-v ' + (rec ? "pos" : "neg") + '">' + (rec ? "+ " : "− ") + R(m.valor) + '</span><button class="editar-mov" type="button" data-linha="' + esc(m.linha_csv) + '" aria-label="Editar movimento" title="Editar"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg></button></li>';
    }).join("");
    var mais = ms.length > vis.length ? '<button class="bt mais" type="button" id="ver-mais-mov">Mostrar mais ' + Math.min(40, ms.length - vis.length) + " (faltam " + (ms.length - vis.length) + ")</button>" : "";
    var tit = V.completo ? "Movimentos de " + nome : "Movimentos recentes", sub = V.completo ? plural(ms.length, "lançamento", "lançamentos") + " do Casemiro, do mais novo ao mais antigo" : ms.length + " mais novos, lançados pelo Casemiro";
    return '<section class="cartao" id="movimentos" aria-label="' + tit + '"><h2>' + tit + "<span>" + sub + '</span></h2><ul class="mvs">' + li + "</ul>" + mais + "</section>";
  }

  /* mês sem nenhum lançamento: diz que está vazio e, se for o atual, oferece o último que tem */
  function editarMovimento(m) {
    var rec = m.tipo !== "gasto", d = document.createElement("dialog"); d.className = "edicao-mov";
    d.innerHTML = '<form method="dialog" class="edicao-corpo"><h2>Editar movimento</h2><label>Data<input name="data" type="date" required value="' + esc(m.data) + '"></label><label>Descri\u00e7\u00e3o<input name="descricao" maxlength="200" required value="' + esc(m.descricao) + '"></label><label>Categoria<input name="categoria" maxlength="80" required value="' + esc(m.categoria === "sem categoria" ? "" : m.categoria) + '"></label><label>Valor (R$)<input name="valor" inputmode="decimal" required value="' + (Number(m.valor) / 100).toFixed(2).replace(".", ",") + '"></label><label>Status<select name="status"><option value="pago">' + (rec ? "Recebido" : "Pago") + '</option><option value="' + (rec ? "a receber" : "a pagar") + '">' + (rec ? "A receber" : "A pagar") + '</option></select></label><p class="obs">Salve para atualizar o arquivo local de movimentos.</p><div class="edicao-acoes"><button class="bt" value="cancelar">Cancelar</button><button class="bt prim" id="salvar-edicao" type="button">Salvar altera\u00e7\u00e3o</button></div></form>';
    document.body.appendChild(d); d.showModal(); d.querySelector("[name=status]").value = m.status;
    d.querySelector("#salvar-edicao").onclick = async function () {
      var b = this, fd = new FormData(d.querySelector("form")), valor = String(fd.get("valor")).trim().replace(/\s/g, "");
      if (valor.indexOf(",") >= 0) valor = valor.replace(/\./g, "").replace(",", ".");
      b.disabled = true; b.textContent = "Salvando...";
      try {
        var resp = await fetch("/api/financas/movimentos/editar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ linha_csv: m.linha_csv, original: { data: m.data, tipo: m.tipo, categoria: m.categoria, descricao: m.descricao, valor: m.valor, status: m.status }, alterado: { data: fd.get("data"), descricao: fd.get("descricao"), categoria: fd.get("categoria"), valor: valor, status: fd.get("status") } }) });
        var json = await resp.json(); if (!resp.ok) throw new Error((json.erro || ["Falha ao salvar."])[0]);
        d.close(); carregar(); B.toast("Lan\u00e7amento atualizado.");
      } catch (e) { B.toast(e.message || "Falha ao salvar."); b.disabled = false; b.textContent = "Salvar altera\u00e7\u00e3o"; }
    };
    d.addEventListener("close", function () { d.remove(); });
  }

  function secMesVazio(F, V) {
    var ls = listaMeses(F), ult = "";
    ls.forEach(function (k) { if (k !== V.mes && temLanc(F, k) && k < V.mes) ult = k; });
    if (!ult) ls.forEach(function (k) { if (k !== V.mes && temLanc(F, k)) ult = k; });
    var acao = V.mes === F.mes_atual && ult ? '<button class="bt prim" type="button" id="ir-ultimo" data-mes="' + ult + '">Ver ' + esc(mesLongo(ult)) + " (último mês com lançamentos)</button>" : "";
    return '<section class="cartao estado" id="mes-vazio" aria-label="Mês sem lançamentos"><div class="vazio"><h2>Nenhum lançamento em ' + esc(mesLongo(V.mes)) + "</h2><p>" +
      (V.mes === F.mes_atual ? "Neste mês ainda não entrou nenhum recebimento nem gasto nos arquivos do Casemiro. " : "Não há recebimentos, gastos nem vencimentos neste mês nos arquivos do Casemiro. ") + "Os números acima ficam zerados, e o saldo das contas continua o de hoje.</p>" + acao + "</div></section>";
  }

  function secFonte(F) {
    var arq = (F.fonte && F.fonte.arquivos) || {}, c = (F.fonte && F.fonte.contagens) || {};
    var li = Object.keys(arq).map(function (k) { return "<li><code>" + esc(k) + "</code><span>" + (arq[k] ? "alterado em " + hm(arq[k]) : "não encontrado") + "</span></li>"; }).join("");
    return '<section class="cartao fonte" aria-label="Fontes desta leitura"><h2>Fontes dos dados<span>' + (c.movimentos || 0) + " movimentos, " + (c.contas || 0) + " contas, " + (c.vencimentos || 0) + ' vencimentos</span></h2><ul class="fontes">' + li + '</ul><p class="obs">Dados locais. Edicoes ficam neste computador; nenhum pagamento e feito por aqui.</p></section>';
  }

  /* ---------- estados vazio, erro e carregando ---------- */
  function bloco(tipo, titulo, texto, acao) {
    return '<section class="cartao estado" aria-label="' + esc(titulo) + '"><div class="vazio">' + GH.slot({ n: tipo, k: "vz", cls: "vz-h" }) + "<h2>" + esc(titulo) + "</h2><p>" + texto + "</p>" + (acao || "") + "</div></section>";
  }
  function esqueleto() {
    var c = function (h) { return '<section class="cartao"><span class="sk sk-h"></span><span class="sk" style="height:' + h + 'px;margin-top:14px"></span><span class="sk sk-t" style="margin-top:12px"></span></section>'; };
    return '<div class="fin-g b" role="status" aria-busy="true"><span class="so">Lendo os dados de finanças</span>' + c(200) + c(150) + "</div>" + '<div class="fin-g c">' + c(170) + c(170) + "</div>";
  }
  function corpo(F, est) {
    if (est === "carregando") return esqueleto();
    if (est === "erro") return bloco("erro_geral", "Não consegui ler os dados de Finanças", (S.motivo === "invalido" ? "O arquivo <code>dados/financas.js</code> existe, mas está incompleto ou fora do formato esperado" : "O arquivo <code>dados/financas.js</code> não existe ainda") + ", então não mostro números antigos como se fossem de agora. Rode <code>python estudio/dados/gerar_financas.py</code> e toque em Tentar de novo. Se faltar <code>movimentos.csv</code> ou <code>saldos.csv</code>, o gerador avisa qual.", '<button class="bt prim risco" type="button" id="tentar">' + B.icon("retry", 20) + " Tentar de novo</button>");
    if (est === "vazio") return bloco("vazio_financas", "Ainda não há lançamentos", "Os arquivos foram lidos, mas <code>movimentos.csv</code> e <code>saldos.csv</code> não têm linhas. Peça ao Casemiro para lançar o primeiro saldo e os primeiros recebimentos e gastos, depois gere de novo.") + secFonte(F);
    var V = visao(F, S.mes), vazio = !V.movimentos.length && !V.recebido && !V.previsto && !V.pagos && !V.apagar && !V.vencimentos.length;
    if (vazio) return secAlertas(F) + '<div class="fin-g b">' + secSerie(F) + '<div class="pilha">' + secMesVazio(F, V) + secContas(F) + "</div></div>" + '<div class="fin-g">' + secFonte(F) + "</div>";
    return secAlertas(F) + '<div class="fin-g b">' + secSerie(F) + '<div class="pilha">' + secRxG(F, V) + secContas(F) + "</div></div>" +
      '<div class="fin-g c">' + secCategorias(F, V) + secVenc(F, V) + "</div>" + '<div class="fin-g">' + secMov(F, V) + "</div>" + '<div class="fin-g">' + secFonte(F) + "</div>";
  }

  /* ---------- paleta Ctrl K ---------- */
  function norm(s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  var pal = document.createElement("dialog"); pal.className = "paleta"; pal.setAttribute("aria-label", "Buscar ou comandar");
  pal.innerHTML = '<div class="p-in"><input id="p-q" type="text" role="combobox" aria-expanded="true" aria-controls="p-l" aria-autocomplete="list" placeholder="Buscar tela ou comando" autocomplete="off"><ul id="p-l" role="listbox"></ul><p class="p-d">' + kbd("↑") + kbd("↓") + " escolhe " + kbd("Enter") + " abre " + kbd("Esc") + " fecha</p></div>";
  document.body.appendChild(pal);
  pal.addEventListener("click", function (e) { if (e.target === pal) pal.close(); });
  var palSel = 0, palIt = [];
  function palConstruir(q) {
    var nq = norm(q), it = [];
    B.menu.forEach(function (m, i) { it.push({ g: "Ir para grupo", r: m.nome, s: m.id === S.area ? "aberto" : "tecla " + (i + 1), ic: m.ic, f: function () { if (m.id === S.area) { window.scrollTo(0, 0); document.getElementById("principal").focus(); } else location.hash = "#/" + m.id; } }); });
    if (S.F && S.fase === "pronto") listaMeses(S.F).slice().reverse().forEach(function (k) { it.push({ g: "Ir para mês...", r: "Ir para " + mesLongo(k), s: "mês" + (k === S.F.mes_atual ? " atual" : "") + (k === S.mes ? ", escolhido" : ""), ic: "financas", f: function () { S.area = "financas"; escolherMes(k, false); } }); });
    it.push({ g: "Nesta tela", r: S.ocultar ? "Mostrar valores" : "Ocultar valores", s: "tecla O", ic: "lock", f: alternarOcultar });
    it.push({ g: "Nesta tela", r: "Alternar tema claro e escuro", s: "tecla T", ic: "sun", f: alternarTema });
    it.push({ g: "Nesta tela", r: "Ler os dados de novo", s: "recarrega financas.js", ic: "retry", f: function () { carregar(); } });
    palIt = it.filter(function (x) { return !nq || norm(x.r + " " + x.s + " " + x.g).indexOf(nq) >= 0; }).slice(0, 30); palSel = 0; palDesenhar();
  }
  function palDesenhar() {
    var ul = pal.querySelector("#p-l"), ult = "";
    ul.innerHTML = palIt.length ? palIt.map(function (x, i) {
      var cab = x.g !== ult ? '<li class="p-g" role="presentation">' + x.g + "</li>" : ""; ult = x.g;
      return cab + '<li role="option" id="p-o' + i + '" data-i="' + i + '" aria-selected="' + (i === palSel) + '">' + B.icon(x.ic, 20) + "<span>" + esc(x.r) + "</span><em>" + esc(x.s) + "</em></li>";
    }).join("") : '<li class="p-g" role="presentation">Nada encontrado. Tente o nome de uma tela, como Finanças.</li>';
    ul.querySelectorAll("[data-i]").forEach(function (li) { li.onclick = function () { palSel = +li.dataset.i; palAbrir(); }; });
    var q = pal.querySelector("#p-q"), o = ul.querySelector("#p-o" + palSel); q.setAttribute("aria-activedescendant", o ? o.id : ""); if (o) o.scrollIntoView({ block: "nearest" });
  }
  function palAbrir() { var x = palIt[palSel]; if (!x) return; pal.close(); x.f(); }
  pal.querySelector("#p-q").addEventListener("input", function (e) { palConstruir(e.target.value); });
  pal.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); palSel = Math.min(palIt.length - 1, palSel + 1); palDesenhar(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); palSel = Math.max(0, palSel - 1); palDesenhar(); }
    else if (e.key === "Enter") { e.preventDefault(); palAbrir(); }
  });
  function abrirPaleta() { pal.querySelector("#p-q").value = ""; palConstruir(""); if (!pal.open) pal.showModal(); pal.querySelector("#p-q").focus(); }

  /* ---------- painel dos 4 cards (PROG-024c, Fluxo 1 de programacao/ux/PROG-financa-detalhes.md) ----------
     Lê só o que a tela já tem (S.F). Editar reaproveita editarMovimento() sem mexer nele. Nada aqui paga nem grava. */
  var PNT = { saldo: "Movimentos do saldo", recebido: "Recebido no mês", gasto: "Gasto pago no mês", "a-pagar": "A pagar no mês", cat: window.CAT_ATUAL ? catRot(window.CAT_ATUAL) : "Categoria" };
  var LAPIS = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>';
  var SETAE = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>';
  var XICO = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  function mesDe(m) { return MESL[+m.slice(5, 7) - 1] + " de " + m.slice(0, 4); }
  function mesNome(m) { return MESL[+m.slice(5, 7) - 1].toLowerCase(); }
  function pnHash() { var h = /^#\/financas\/(saldo|recebido|gasto|a-pagar)$/.exec(location.hash || ""); return h ? h[1] : ""; }
  function pnFiltrar(l, tipo) {
    if (tipo === "cat" && window.CAT_ATUAL) {
      return l.filter(function (m) { return catKey(m.categoria) === catKey(window.CAT_ATUAL); });
    }
    return l.filter(function (m) {
      var rec = m.tipo !== "gasto", pago = m.status === "pago";
      return tipo === "recebido" ? rec && pago : tipo === "gasto" ? !rec && pago : tipo === "a-pagar" ? !rec && !pago : pago;
    });
  }
  function pnCard(V, tipo) { return tipo === "recebido" ? V.recebido : tipo === "gasto" ? V.pagos : tipo === "a-pagar" ? V.apagar : null; }
  function pnDia(iso) { var d = dif(iso); return d === 0 ? "Hoje, " + dm(iso) : d === 1 ? "Ontem, " + dm(iso) : dm(iso); }
  /* Situação de uma conta a pagar, sempre em texto (a cor só reforça). */
  function pnVenc(m) {
    var d = -dif(m.data);
    if (d < 0) return { e: "erro", t: "Venceu há " + plural(-d, "dia", "dias") };
    if (d === 0) return { e: "pendente", t: "Vence hoje" };
    if (d === 1) return { e: "pendente", t: "Vence amanhã" };
    if (d <= 3) return { e: "pendente", t: "Vence em " + d + " dias" };
    return { e: "backlog", t: "Vence em " + dm(m.data) };
  }
  function pnOrdenar(l, tipo, ord) {
    var c = l.slice(), ln = function (m) { return Number(m.linha_csv) || 0; };
    if (tipo === "a-pagar") c.sort(function (a, b) { return a.data === b.data ? ln(a) - ln(b) : a.data < b.data ? -1 : 1; });
    else if (ord === "valor") c.sort(function (a, b) { return b.valor - a.valor; });
    else { var s = ord === "data-asc" ? 1 : -1; c.sort(function (a, b) { return a.data === b.data ? s * (ln(a) - ln(b)) : a.data < b.data ? -s : s; }); }
    return c;
  }
  function pnLinha(m, tipo) {
    var rec = m.tipo !== "gasto", pago = m.status === "pago", cat = esc(catRot(m.categoria)), sub, extra = "";
    if (tipo === "a-pagar") { var v = pnVenc(m); sub = cat; extra = '<span class="pm-s">' + chip(v.e, v.t) + "</span>"; }
    else sub = cat + " · " + (pago ? (rec ? "recebido" : "pago") : (rec ? "a receber" : "a pagar")) + " em " + dm(m.data);
    var ed = m.linha_csv != null ? '<button type="button" class="pm-ed" data-linha="' + esc(m.linha_csv) + '" aria-label="Editar ' + esc(mt(m.descricao)) + '" title="Editar">' + LAPIS + '<span class="pm-edl">Editar</span></button>' : "";
    return '<li class="pm">' + catIco(m.categoria, 18) + '<div class="pm-t"><b>' + esc(mt(m.descricao)) + '</b><span class="mudo">' + sub + '</span></div><span class="pm-v ' + (rec ? "pos" : "neg") + '">' + (rec ? "+ " : "− ") + R(m.valor) + "</span>" + ed + extra + "</li>";
  }
  function pnVazio(F) {
    var m = mesNome(P.mes), outro = listaMeses(F).some(function (k) { return k !== P.mes && temLanc(F, k); });
    var T = {
      recebido: ["Nada recebido em " + m, "Ainda não há receitas com status recebido neste mês. Se você já recebeu algo, confira o status do lançamento.", outro ? '<button class="bt" type="button" id="pn-outro">Ver outro mês</button>' : ""],
      gasto: ["Nenhum gasto pago em " + m, "Não há gastos com status pago neste mês. Gastos ainda não pagos aparecem em “A pagar”.", '<button class="bt" type="button" id="pn-apagar">Abrir A pagar</button>'],
      "a-pagar": ["Nada a pagar em " + m, "Todas as contas deste mês estão pagas ou ainda não foram lançadas.", outro ? '<button class="bt" type="button" id="pn-outro">Ver outro mês</button>' : ""],
      saldo: ["Sem movimentos neste mês", "O saldo mostrado vem das contas. Ainda não há lançamentos pagos ou recebidos em " + m + ".", outro ? '<button class="bt" type="button" id="pn-outro">Ver outro mês</button>' : ""]
    }[P.tipo];
    return '<div class="vazio pn-vazio">' + GH.slot({ n: "vazio_financas", k: "vz", cls: "vz-h" }) + "<h3>" + esc(T[0]) + "</h3><p>" + esc(T[1]) + "</p>" + T[2] + "</div>";
  }
  /* Só a lista (e a contagem da busca): a busca digita aqui sem refazer o painel nem perder o foco. */
  function pnLista() {
    var box = document.getElementById("pn-lista"), cont = document.getElementById("pn-cont"), F = S.F;
    if (!box || !F) return;
    var todos = pnFiltrar(visao(F, P.mes).movimentos, P.tipo), q = P.q.trim(), nq = norm(q);
    var f = q ? todos.filter(function (m) { return norm(m.descricao + " " + m.categoria + " " + catRot(m.categoria)).indexOf(nq) >= 0; }) : todos;
    if (cont) cont.textContent = q && todos.length ? "Mostrando " + f.length + " de " + todos.length : "";
    if (!todos.length) { box.innerHTML = pnVazio(F); return; }
    if (!f.length) { box.innerHTML = '<div class="pn-busca-vazia"><p>Nenhum movimento com “' + esc(q) + "”. Limpe a busca para ver todos.</p>" + '<button class="bt" type="button" id="pn-limpar">Limpar busca</button></div>'; return; }
    var o = pnOrdenar(f, P.tipo, P.ord), gr = [];
    if (P.tipo === "a-pagar") {
      [["erro", "Vencidos"], ["pendente", "Vencem em até 3 dias"], ["backlog", "Mais adiante"]].forEach(function (g) {
        var it = o.filter(function (m) { return pnVenc(m).e === g[0]; }); if (it.length) gr.push({ e: g[0], h: g[1], it: it });
      });
    } else if (P.ord === "valor") gr.push({ h: "", it: o });
    else o.forEach(function (m) { var u = gr[gr.length - 1]; if (u && u.k === m.data) u.it.push(m); else gr.push({ k: m.data, h: pnDia(m.data), it: [m] }); });
    box.innerHTML = gr.map(function (g) {
      var cab = g.h ? '<h3 class="pm-g' + (g.e ? " e-" + g.e : "") + '">' + (g.e ? GH.ico(g.e, 16) : "") + "<span>" + esc(g.h) + (g.e ? " (" + g.it.length + ")" : "") + "</span>" + (g.e ? "<b>" + R(soma(g.it)) + "</b>" : "") + "</h3>" : "";
      return '<section class="pm-grupo">' + cab + '<ul class="pm-ul">' + g.it.map(function (m) { return pnLinha(m, P.tipo); }).join("") + "</ul></section>";
    }).join("");
  }
  function pnContas(F) {
    var sd = F.saldos, fora = sd.contas_fora_do_disponivel || [];
    var li = sd.contas.map(function (c) {
      var f = fora.indexOf(c.conta) >= 0;
      return '<li class="pn-cta"><b>' + esc(c.conta) + '</b><span class="pn-cta-v">' + R(c.saldo) + '</span><span class="mudo">atualizado em ' + dm(c.data) + (c.observacao ? " · " + esc(mt(c.observacao)) : "") + "</span>" + (f ? '<span class="est fora"><span>fora do disponível</span></span>' : "") + "</li>";
    }).join("");
    return '<section class="pn-contas" aria-label="Contas">' + (li ? '<ul class="pn-ctas">' + li + "</ul>" : '<p class="mudo pq">Nenhuma conta informada ainda.</p>') +
      '<p class="obs">O saldo do banco não é a soma destes movimentos. Esta lista mostra só o que você lançou como pago ou recebido.</p></section>';
  }
  function pnOk(F) {
    var V = visao(F, P.mes), todos = pnFiltrar(V.movimentos, P.tipo), tot = soma(todos), card = pnCard(V, P.tipo);
    var ent = soma(todos.filter(function (m) { return m.tipo !== "gasto"; })), sai = tot - ent;
    var resumo = esc(mesDe(P.mes)) + " · " + plural(todos.length, "movimento", "movimentos") + " · " + (P.tipo === "saldo" ? "Entradas " + R(ent) + " · Saídas " + R(sai) : "Total " + R(tot));
    var aviso = card != null && card !== tot ? '<p class="pn-soma al e-erro" role="status">' + GH.ico("erro", 18) + "<span>A soma desta lista (" + R(tot) + ") não bate com o card (" + R(card) + "). " + '<button type="button" class="pn-link" data-alertas>Veja Alertas.</button>' + (V.completo ? "" : " Esta leitura traz só os movimentos mais recentes.") + "</span></p>" : "";
    var idade = diasDesde(F.gerado_em), velho = "";
    if (idade > 3) velho = '<div class="pn-velho e-pendente" role="status">' + GH.ico("pendente", 18) + "<div><p>Dados de " + idade + " dias atrás. Os valores podem estar desatualizados.</p>" +
      (P.atualizou ? "<p>A leitura continua antiga. Gere dados novos com <code>python estudio/dados/gerar_financas.py</code> e toque em Atualizar leitura de novo.</p>" : "") + '</div><button class="bt" type="button" id="pn-atualizar">Atualizar leitura</button></div>';
    var opMes = listaMeses(F).slice().reverse().map(function (k) { return '<option value="' + k + '"' + (k === P.mes ? " selected" : "") + ">" + esc(mesLongo(k)) + (k === F.mes_atual ? " (atual)" : "") + "</option>"; }).join("");
    var ord = P.tipo === "a-pagar" ? "" : '<label class="pn-l pn-ord">Ordenar<select id="pn-ord"><option value="data-desc"' + (P.ord === "data-desc" ? " selected" : "") + ">Data (mais nova primeiro)</option><option value=\"data-asc\"" + (P.ord === "data-asc" ? " selected" : "") + ">Data (mais antiga primeiro)</option><option value=\"valor\"" + (P.ord === "valor" ? " selected" : "") + ">Valor (maior primeiro)</option></select></label>";
    var ctl = '<div class="pn-ctl"><label class="pn-l">Mês<select id="pn-mes">' + opMes + '</select></label><label class="pn-l">Buscar na lista<input id="pn-q" type="search" placeholder="Descrição ou categoria" autocomplete="off" value="' + esc(P.q) + '"></label>' + ord + "</div>";
    var q = idade === 0 ? "hoje" : idade === 1 ? "ontem" : "em " + dm(F.gerado_em);
    return velho + (P.tipo === "a-pagar" ? '<p class="obs pn-nota">Esta lista é só de leitura. Para corrigir uma conta, use Editar. Nenhum pagamento é feito por este app.</p>' : "") +
      '<p class="pn-res">' + resumo + "</p>" + aviso + (P.tipo === "saldo" ? pnContas(F) : "") + ctl + '<p class="pn-cont mudo" id="pn-cont" aria-live="polite"></p><div id="pn-lista"></div>' +
      '<p class="pn-pe">Fonte: movimentos.csv, lido ' + q + " às " + esc(String(F.gerado_em).slice(11, 16)) + "</p>";
  }
  function pnCarregando() {
    return '<p class="pn-res">' + esc(P.mes ? mesDe(P.mes) : "") + '</p><div class="pn-sk" role="status" aria-live="polite" aria-busy="true"><p class="mudo">Carregando movimentos…</p>' + [1, 2, 3, 4, 5].map(function () { return '<span class="sk pn-skl"></span>'; }).join("") + "</div>";
  }
  function pnErro() {
    var det = S.motivo === "invalido" ? "invalido: dados/financas.js existe, mas está incompleto ou fora do formato esperado" : "ausente: dados/financas.js não encontrado";
    return '<div class="pn-erro e-erro" role="alert">' + GH.ico("erro", 22) + "<h3>Não consegui carregar os movimentos</h3><p>A leitura dos dados falhou. Nenhum valor antigo é mostrado aqui para você não confundir com o atual.</p>" +
      (P.tentou ? "<p><b>Continua sem carregar.</b> Verifique se o Corte está aberto neste computador e tente de novo em alguns segundos.</p>" : "") +
      '<div class="pn-acoes"><button class="bt prim" type="button" id="pn-tentar">Tentar de novo</button><button class="bt" type="button" data-fechar>Fechar</button></div>' +
      "<details><summary>Ver detalhes</summary><p>Código: <code>" + esc(det.split(":")[0]) + "</code><br>Mensagem: " + esc(det.split(": ").slice(1).join(": ")) + "</p><p class=\"mudo\">Copie e mande ao Rodrygo, se continuar.</p></details></div>";
  }
  function pnBloq() {
    return '<div class="pn-bloq"><h3>Finanças só abre neste computador</h3><p>Por segurança, os movimentos não aparecem quando o Corte é aberto pela rede (celular, por exemplo). Abra o Corte direto no computador para ver e editar.</p><button class="bt prim" type="button" id="pn-entendi">Entendi</button></div>';
  }
  function pnDlg() {
    if (P.dlg) return P.dlg;
    var d = document.createElement("dialog"); d.className = "painel-mov"; d.setAttribute("aria-labelledby", "pn-t"); d.innerHTML = '<div class="pn-in"></div>';
    document.body.appendChild(d); P.dlg = d;
    d.addEventListener("close", pnAoFechar);
    d.addEventListener("click", function (e) {
      if (e.target === d) { d.close(); return; }
      var b = e.target.closest && e.target.closest("button"); if (!b) return;
      if (b.hasAttribute("data-fechar") || b.id === "pn-entendi") d.close();
      else if (b.classList.contains("pm-ed")) {
        var m = S.F && visao(S.F, P.mes).movimentos.filter(function (x) { return String(x.linha_csv) === b.getAttribute("data-linha"); })[0];
        if (m) { P.focoLinha = m.linha_csv; editarMovimento(m); }
      }
      else if (b.id === "pn-limpar") { P.q = ""; var q = d.querySelector("#pn-q"); if (q) { q.value = ""; q.focus(); } pnLista(); }
      else if (b.id === "pn-outro") { var s = d.querySelector("#pn-mes"); if (s) { s.focus(); try { s.showPicker && s.showPicker(); } catch (x) {} } }
      else if (b.id === "pn-apagar") pnTrocar("a-pagar");
      else if (b.id === "pn-tentar" || b.id === "pn-atualizar") { if (b.id === "pn-tentar") P.tentou = true; else P.atualizou = true; b.disabled = true; b.textContent = b.id === "pn-tentar" ? "Tentando…" : "Atualizando…"; carregar(); }
      else if (b.hasAttribute("data-alertas")) { d.close(); var al = document.getElementById("alertas"); if (al) al.scrollIntoView({ block: "start", behavior: B.suave() }); }
    });
    d.addEventListener("input", function (e) { if (e.target.id === "pn-q") { P.q = e.target.value; pnLista(); } });
    d.addEventListener("change", function (e) {
      if (e.target.id === "pn-mes") { P.mes = e.target.value; P.q = ""; pnDesenhar(); var s = d.querySelector("#pn-mes"); if (s) s.focus(); }
      else if (e.target.id === "pn-ord") { P.ord = e.target.value; pnLista(); }
    });
    return d;
  }
  function pnDesenhar(foco) {
    var d = pnDlg(), F = S.F, tit = PNT[P.tipo], corpo;
    if (F && listaMeses(F).indexOf(P.mes) < 0) P.mes = listaMeses(F).indexOf(S.mes) >= 0 ? S.mes : F.mes_atual;
    var rol = (d.querySelector(".pn-corpo") || {}).scrollTop || 0, ok = false;
    if (S.bloqueado) corpo = pnBloq(); else if (S.fase === "carregando") corpo = pnCarregando(); else if (S.fase === "erro" || !F) corpo = pnErro(); else { corpo = pnOk(F); ok = true; }
    d.querySelector(".pn-in").innerHTML = '<header class="pn-cab"><button type="button" class="pn-volta" data-fechar>' + SETAE + '<span>Voltar</span></button><h2 id="pn-t" tabindex="-1">' + esc(tit) + '</h2><button type="button" class="pn-x" data-fechar aria-label="Fechar painel">' + XICO + '</button></header><div class="pn-corpo">' + corpo + "</div>";
    if (ok) { P.tentou = false; pnLista(); }
    var c = d.querySelector(".pn-corpo"); if (c && rol) c.scrollTop = rol;
    var at = document.activeElement, dentro = at && at !== document.body && d.contains(at) && at !== d;
    if (foco) d.querySelector("#pn-t").focus({ preventScroll: true });
    else if (!dentro) { var b = P.focoLinha != null && d.querySelector('.pm-ed[data-linha="' + P.focoLinha + '"]'); if (b) { b.focus({ preventScroll: true }); P.focoLinha = null; } else d.querySelector("#pn-t").focus({ preventScroll: true }); }
  }
  function pnAbrir(tipo, empurrar) {
    if (!PNT[tipo]) return;
    var d = pnDlg();
    if (d.open) { pnTrocar(tipo); return; }
    P.tipo = tipo; P.q = ""; P.ord = "data-desc"; P.tentou = false; P.atualizou = false; P.focoLinha = null; P.empurrou = false;
    P.mes = S.F ? (listaMeses(S.F).indexOf(S.mes) >= 0 ? S.mes : S.F.mes_atual) : "";
    if (empurrar) { try { history.pushState(null, "", "#/financas/" + tipo); P.empurrou = true; } catch (e) {} }
    pnDesenhar(true);
    d.showModal(); document.body.classList.add("pn-aberto");
    var tb = document.getElementById("toast"); if (tb) d.appendChild(tb); /* o aviso fica dentro do painel: a camada superior do <dialog> cobriria o toast */
    d.querySelector("#pn-t").focus({ preventScroll: true });
  }
  function pnTrocar(tipo) {
    P.tipo = tipo; P.q = ""; P.ord = "data-desc"; P.focoLinha = null;
    try { history.replaceState(null, "", "#/financas/" + tipo); } catch (e) {}
    pnDesenhar(true);
  }
  function pnAoFechar() {
    document.body.classList.remove("pn-aberto");
    var tb = document.getElementById("toast"); if (tb && tb.parentNode !== document.body) document.body.appendChild(tb);
    if (P.timer) { clearTimeout(P.timer); P.timer = 0; }
    if (pnHash()) {
      if (P.empurrou) { P.ignorar = true; P.empurrou = false; try { history.back(); } catch (e) {} setTimeout(function () { P.ignorar = false; }, 600); }
      else { try { history.replaceState(null, "", "#/financas"); } catch (e) {} }
    }
    var c = document.querySelector('.nm[data-pn="' + P.tipo + '"]'); if (c) c.focus({ preventScroll: true });
  }
  /* Chamado no fim de cada render(): mantém o painel em dia com a leitura e abre pela âncora #/financas/... */
  function pnRender() {
    var d = P.dlg;
    if (!d || !d.open) {
      var t = pnHash();
      if (t && !P.ignorar && S.fase !== "carregando" && S.area === "financas") pnAbrir(t, false);
      return;
    }
    if (S.fase === "carregando" && !S.bloqueado) { /* esqueleto só se a leitura passar de 300 ms: antes disso o painel não pisca */
      if (!P.timer) P.timer = setTimeout(function () { P.timer = 0; if (S.fase === "carregando" && P.dlg && P.dlg.open) pnDesenhar(); }, 300);
      return;
    }
    if (P.timer) { clearTimeout(P.timer); P.timer = 0; }
    pnDesenhar();
  }

  /* ---------- ações e montagem ---------- */
  function alternarOcultar() {
    S.ocultar = !S.ocultar; try { localStorage.setItem(KO, S.ocultar ? "1" : "0"); } catch (e) {}
    render(); var b = document.getElementById("ocultar"); if (b) b.focus();
    B.toast(S.ocultar ? "Valores ocultos. Eu lembro disso na próxima abertura." : "Valores visíveis.");
  }
  function alternarTema() {
    var n = document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro";
    document.documentElement.dataset.tema = n; try { localStorage.setItem(KT, n); } catch (e) {} render(); var b = document.getElementById("tema"); if (b) b.focus();
  }
  document.addEventListener("keydown", function (e) {
    var a = e.target, dig = /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName) || a.isContentEditable;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); abrirPaleta(); return; }
    if (dig || e.ctrlKey || e.metaKey || e.altKey || pal.open) return;
    var k = e.key.toLowerCase();
    if (k === "/") { e.preventDefault(); abrirPaleta(); }
    else if (k === "o") alternarOcultar();
    else if (k === "t") alternarTema();
    else if (/^[1-8]$/.test(k)) { var m = B.menu[+k - 1]; if (m) location.hash = "#/" + m.id; }
  });

  function render() {
    var F = S.F, est = estado(F), y = window.scrollY;
    if (S.area === "financas") {
      app.innerHTML = ilha(F, est) + '<main id="principal" class="papel" tabindex="-1"><div class="pag-cab"><h1 class="pag">Finan\u00e7as</h1><p class="sub">Dados locais do Casemiro. Edite um movimento pelo botao ao lado; salvar atualiza o CSV neste computador.</p></div>' + corpo(F, est) + "</main>";
      document.title = "Finan\u00e7as: Ecossistema do Guilherme";
    } else {
      var grupo = B.menu.filter(function (m) { return m.id === S.area; })[0];
      app.innerHTML = ilha(F, est) + '<main id="principal" class="papel pagina-vazia" tabindex="-1"><div class="pag-cab"><h1 class="pag">' + esc(grupo ? grupo.nome : "Ecossistema") + '</h1><p class="sub">Esta area esta na casca do Ecossistema. A tela entra conforme os itens da sprint forem entregues.</p></div><section class="cartao estado"><div class="vazio"><h2>Tela ainda nao conectada</h2><p>A navegacao e o tema ja funcionam. Os dados desta area aparecerao aqui quando sua tarefa entrar na casca.</p></div></section></main>';
      document.title = (grupo ? grupo.nome : "Ecossistema") + ": Ecossistema do Guilherme";
    }
    document.getElementById("abrir-paleta").onclick = abrirPaleta;
    var ocultar = document.getElementById("ocultar"); if (ocultar) ocultar.onclick = alternarOcultar;
    document.getElementById("tema").onclick = alternarTema;
    document.querySelectorAll(".ilha .nm[data-pn]").forEach(function (b) { b.onclick = function () { if (b.getAttribute("aria-disabled") === "true" && !S.bloqueado) return; pnAbrir(b.getAttribute("data-pn"), true); }; });
    document.querySelectorAll("[data-ainda]").forEach(function (el) { el.onclick = function () { B.toast(AINDA); }; el.onkeydown = function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); B.toast(AINDA); } }; });
    var t = document.getElementById("tentar"); if (t) t.onclick = function () { carregar(); };
    var vt = document.getElementById("ver-todas"); if (vt) vt.onclick = function () { S.todas = !S.todas; render(); var n = document.getElementById("ver-todas"); if (n) n.focus({ preventScroll: true }); };
    if (est === "ok" && S.area === "financas") {
      desenharSerie();
      document.querySelectorAll(".mb-chip, .mb-seta[data-mes], #ir-ultimo").forEach(function (b) { b.onclick = function () { escolherMes(b.getAttribute("data-mes"), b.classList.contains("mb-chip")); if (b.id === "ir-ultimo") window.scrollTo(0, 0); }; });
      var mb = document.getElementById("mes-bar"), ch = document.getElementById("mb-chips"), sl = document.querySelector(".mb-chip.sel");
      if (ch && sl) ch.scrollLeft = Math.max(0, sl.offsetLeft - (ch.clientWidth - sl.offsetWidth) / 2);
      if (mb) mb.onkeydown = function (e) {
        var d = e.key === "ArrowLeft" ? -1 : e.key === "ArrowRight" ? 1 : 0, m = d ? vizinho(d) : null;
        if (d) { e.preventDefault(); if (m) escolherMes(m, true); }
      };
      var vm = document.getElementById("ver-mais-mov"); if (vm) vm.onclick = function () { S.movN += 40; render(); var n = document.getElementById("ver-mais-mov"); if (n) n.focus({ preventScroll: true }); };
      document.querySelectorAll(".editar-mov").forEach(function (b) { b.onclick = function () { var linha = Number(b.dataset.linha), lista = (S.F.movimentos_recentes || []).slice(); Object.keys(S.F.meses || {}).forEach(function (k) { lista = lista.concat(S.F.meses[k].movimentos || []); }); var m = lista.find(function (x) { return Number(x.linha_csv) === linha; }); if (m) editarMovimento(m); }; });
      document.querySelectorAll(".cats .cat").forEach(function (cat) { cat.onclick = function (e) { e.preventDefault(); window.CAT_ATUAL = cat.dataset.categoria; pnAbrir("cat", true); }; });
    }
    window.scrollTo(0, y);
    try { pnRender(); } catch (e) { if (window.console) console.error("painel de movimentos: " + (e && e.message)); }
  }
  var rz; window.addEventListener("resize", function () { cancelAnimationFrame(rz); rz = requestAnimationFrame(function () { if (document.getElementById("serie-box")) desenharSerie(); }); });

  /* ---------- leitura do arquivo gerado ---------- */
  var ATRASO = +(GH.q("atraso") || 0); /* só para teste: segura o esqueleto por N ms */
  function carregar() {
    S.fase = "carregando"; S.F = null; S.motivo = ""; S.entrou = false;
    try { delete window.FINANCAS; } catch (e) { window.FINANCAS = undefined; }
    render();
    var vel = document.getElementById("dados-fin"); if (vel) vel.remove();
    var sc = document.createElement("script"); sc.id = "dados-fin";
    function fim(achou) {
      setTimeout(function () {
        var F = window.FINANCAS;
        if (!achou) { S.fase = "erro"; S.motivo = "ausente"; }
        else if (!valido(F)) { S.fase = "erro"; S.motivo = "invalido"; }
        else { try { S.F = normalizar(F); S.mes = mesInicial(S.F); S.fase = "pronto"; } catch (e) { S.fase = "erro"; S.motivo = "invalido"; } }
        try { render(); } catch (e) { S.fase = "erro"; S.motivo = "invalido"; S.F = null; render(); }
      }, ATRASO);
    }
    sc.onload = function () { fim(true); }; sc.onerror = function () { fim(false); };
    sc.src = "dados/financas.js?v=" + Date.now();
    document.head.appendChild(sc);
  }
  window.addEventListener("hashchange", function () {
    var hash = location.hash || "", area = hash.charAt(0) === "#" ? hash.slice(1).replace(/^\//, "") : "";
    var pt = pnHash();
    if (pt) { /* #/financas/saldo|recebido|gasto|a-pagar: abre (ou troca) o painel; o botão voltar do navegador tira a âncora e fecha */
      P.ignorar = false;
      if (P.dlg && P.dlg.open) { if (P.tipo !== pt) pnTrocar(pt); } else if (S.fase !== "carregando") pnAbrir(pt, false);
      return;
    }
    P.ignorar = false;
    if (P.dlg && P.dlg.open) { P.empurrou = false; P.dlg.close(); }
    if (B.menu.some(function (m) { return m.id === area; }) && area !== S.area) { S.area = area; render(); return; }
    var h = /^#mes=(\d{4}-\d{2})$/.exec(hash);
    if (h && S.F && h[1] !== S.mes && listaMeses(S.F).indexOf(h[1]) >= 0) { S.area = "financas"; S.mes = h[1]; S.movN = 40; try { localStorage.setItem(KM, h[1]); } catch (e) {} render(); }
  });
  carregar();
})();
