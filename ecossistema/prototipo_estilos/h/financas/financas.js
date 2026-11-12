/* Tela de Finanças no estilo H (PROG-024b). Consome window.FINANCAS (contrato PROG-024a, centavos).
   Reaproveita B (base.js) e GH (g/comum_gh.js) e o CSS do H sem editá-los. Sem rede, sem segredos. */
(function () {
  var app = document.getElementById("app"), esc = B.esc;
  var KO = "ce_h_fin_ocultar", KT = "ce_h_tema";
  GH.tema(KT, "claro");
  var S = { ocultar: false, todas: false, entrou: false };
  try { S.ocultar = localStorage.getItem(KO) === "1"; } catch (e) {}
  var MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
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
  function mt(s) { return S.ocultar ? String(s).replace(/R\$\s?[\d.]+(?:,\d{2})?/g, "R$ ••••") : String(s); }
  function pct(p) { return String(p).replace(".", ",") + "%"; }
  function plural(n, a, b) { return n + " " + (n === 1 ? a : b); }
  function dm(iso) { var p = String(iso).slice(0, 10).split("-"); return p[2] + "/" + p[1]; }
  function hm(iso) { return dm(iso) + " às " + String(iso).slice(11, 16); }
  function dsem(iso) { var p = iso.slice(0, 10).split("-"); return DIA[new Date(+p[0], +p[1] - 1, +p[2]).getDay()]; }
  function diasDesde(iso) { var p = String(iso).slice(0, 10).split("-"), n = new Date(), h = new Date(n.getFullYear(), n.getMonth(), n.getDate()); return Math.max(0, Math.round((h - new Date(+p[0], +p[1] - 1, +p[2])) / 864e5)); }
  function mesAbrev(m) { return MES[+m.slice(5, 7) - 1]; }
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
  function estado(F) {
    if (window.FINANCAS_ESTADO === "carregando") return "carregando";
    if (!F || typeof F !== "object" || !F.saldos || !F.serie_mensal) return "erro";
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
  function barra(e, p, rot, cls) { return '<div class="pb e-' + e + " " + (cls || "") + '" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + p + '" aria-label="' + esc(mt(rot)) + '"><i style="width:' + p + '%"></i></div>'; }

  /* ---------- ilha ---------- */
  function href(id) { return id === "financas" ? "#principal" : id === "ecossistema" ? "../index.html#/ecossistema/agentes" : "../index.html#/" + id; }
  function celula(cls, ico, rot, nn, ns, mini) {
    return '<article class="nm ' + cls + '">' + ico + '<span class="nr">' + rot + '</span><span class="nn">' + nn + "</span>" + ns + (mini ? '<span class="mini">' + mini + "</span>" : "") + "</article>";
  }
  function numeros(F, est) {
    var sk = '<span class="sk sk-n"></span>', sk2 = '<span class="ns"><span class="sk sk-t"></span></span>', nd = '<span class="nd">—</span>';
    var ics = [B.icon("financas", 18), GH.ico("ok", 18), ICO_GASTO, GH.ico("pendente", 18)];
    var rots = ["Saldo disponível", "Recebido no mês", "Gasto no mês", "A pagar no mês"], cls = ["saldo", "", "", ""];
    if (est === "carregando" || !F || !F.saldos) {
      var t = est === "carregando" ? sk : nd, ns = est === "carregando" ? sk2 : '<span class="ns">sem leitura</span>';
      return [0, 1, 2, 3].map(function (i) { return celula(cls[i], ics[i], rots[i], t, ns); }).join("");
    }
    var sd = F.saldos, rc = F.recebido, gs = F.gastos, vs = F.vencimentos || [];
    var fora = (sd.contas_fora_do_disponivel || []).length;
    var datas = sd.contas.map(function (c) { return c.data; }).sort(), ult = datas.length ? dm(datas[datas.length - 1]) : "";
    var c1 = celula("saldo", ics[0], rots[0], RG(sd.disponivel),
      '<span class="ns">' + (sd.contas.length ? plural(sd.contas.length, "conta", "contas") + ", saldo informado até " + ult : "nenhuma conta informada") + "</span>" +
      (fora ? '<span class="ns parc">Parcial: ' + plural(fora, "conta fora", "contas fora") + " do total</span>" : ""));
    var c2 = celula("", ics[1], rots[1], RG(rc.mes), '<span class="ns">mais ' + R(rc.previsto_mes) + " a receber</span>",
      barra("ok", frac(rc.mes, rc.mes + rc.previsto_mes), "Recebido: " + T(rc.mes) + " de " + T(rc.mes + rc.previsto_mes) + " previstos no mês", "fx"));
    var c3 = celula("", ics[2], rots[2], RG(gs.pagos_mes), '<span class="ns">pago; mais ' + R(gs.a_pagar_mes) + " a pagar</span>",
      barra("gasto", frac(gs.pagos_mes, gs.pagos_mes + gs.a_pagar_mes), "Gasto pago: " + T(gs.pagos_mes) + " de " + T(gs.pagos_mes + gs.a_pagar_mes) + " no mês", "fx"));
    var atr = vs.filter(function (v) { return v.atrasado || v.dias_restantes < 0; }), hoje = vs.filter(function (v) { return v.dias_restantes === 0; });
    var urg = soma(atr) + soma(hoje), ie = atr.length ? "erro" : "pendente";
    var ns4 = '<span class="ns">' + (vs.length ? plural(vs.length, "vencimento", "vencimentos") : "nenhum vencimento") + (atr.length ? ' · <b class="atr">' + plural(atr.length, "atrasado", "atrasados") + "</b>" : "") + "</span>";
    var c4 = celula("", GH.ico(ie, 18), rots[3], RG(gs.a_pagar_mes), ns4, gs.a_pagar_mes > 0 && vs.length ? barra(ie, frac(urg, gs.a_pagar_mes), "Parte já vencida ou vencendo hoje: " + T(urg) + " de " + T(gs.a_pagar_mes), "fx") : "");
    return c1 + c2 + c3 + c4;
  }
  function soma(l) { return l.reduce(function (a, v) { return a + v.valor; }, 0); }

  function selo(F, est) {
    if (est === "carregando") return '<div class="selo">' + chip("rodando", "Lendo os dados") + "</div>";
    if (!F || est === "erro") return '<div class="selo">' + chip("erro", "Sem leitura") + '<span class="s-t">financas.js não encontrado</span></div>';
    var idade = diasDesde(F.gerado_em), arq = (F.fonte && F.fonte.arquivos) || {}, ks = Object.keys(arq), ok = ks.filter(function (k) { return arq[k]; }).length;
    var c = idade === 0 ? chip("ok", "Lido hoje") : chip(idade > 3 ? "erro" : "pendente", "Dados velhos há " + plural(idade, "dia", "dias"));
    return '<div class="selo" role="group" aria-label="Última leitura">' + c + '<span class="s-t">Gerado em ' + hm(F.gerado_em) + " · " + ok + " de " + ks.length + " fontes</span></div>";
  }
  function legenda() {
    var L = [["ok", "Pago ou recebido", "Dinheiro que já entrou ou saiu"], ["erro", "Vencido ou inconsistente", "Passou do prazo ou os dados se contradizem"], ["pendente", "Vence em até 3 dias", "Pede atenção agora"], ["backlog", "A pagar ou previsto", "Ainda não aconteceu"], ["rodando", "Lendo os dados", "Atualizando a leitura"]];
    return '<ul class="legenda leg-h" aria-label="Legenda dos estados">' + L.map(function (x) { return '<li class="e-' + x[0] + '" title="' + esc(x[2]) + '">' + GH.ico(x[0], 18) + "<span>" + x[1] + "</span></li>"; }).join("") + "</ul>";
  }
  function ilha(F, est) {
    var escuro = document.documentElement.dataset.tema === "escuro";
    return '<header class="ilha"><div class="i-in"><div class="i-top"><div class="marca">' + GH.slot({ n: "logo_contexto_explica", k: "logo", px: 34 }) + "<span>Ecossistema do Guilherme</span></div>" +
      '<button class="busca" type="button" id="abrir-paleta" aria-label="Buscar ou comandar (Ctrl K)">' + '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>' + "<span>Buscar tela ou comando</span>" + kbd("Ctrl K") + "</button>" +
      '<div class="i-ferr"><button class="bt-i" type="button" id="ocultar" aria-pressed="' + S.ocultar + '" title="Atalho: O">' + (S.ocultar ? EYEOFF : EYE) + '<span class="bl">' + (S.ocultar ? "Mostrar valores" : "Ocultar valores") + "</span></button>" +
      '<button class="bt-i ic1" type="button" id="tema" aria-label="Tema ' + (escuro ? "claro" : "escuro") + '" title="Tema (T)">' + B.icon(escuro ? "sun" : "moon", 20) + "</button></div></div>" +
      '<nav class="i-nav" aria-label="Grupos">' + B.menu.map(function (m, i) {
        return '<a class="aba" href="' + href(m.id) + '"' + (m.id === "financas" ? ' aria-current="page"' : "") + ">" + B.icon(m.ic, 18) + "<span>" + esc(m.nome) + "</span>" + kbd(i + 1) + "</a>";
      }).join("") + "</nav>" +
      '<div class="i-nums" aria-label="Resumo do mês">' + numeros(F, est) + "</div>" +
      '<div class="i-leg">' + legenda() + selo(F, est) + "</div></div></header>";
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
    return '<section class="cartao" id="alertas" aria-label="Alertas"><h2>Alertas<span>' + rot + "</span></h2>" +
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
    return '<section class="cartao" aria-label="Série mensal"><h2>Últimos 6 meses<span>' + (sm.length ? "até " + mesAbrev(sm[sm.length - 1].mes) : "") + '</span></h2>' + lg + '<div id="serie-box" class="serie-box"></div>' + tab + "</section>";
  }
  function desenharSerie() {
    var box = document.getElementById("serie-box"), F = window.FINANCAS;
    if (!box || !F) return;
    box.innerHTML = "";
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
      var cx = px + gw * i + gw / 2, xr = cx - gap / 2 - bw, xg = cx + gap / 2, atual = i === n - 1;
      o += barra(xr, m.recebido, "b-rec", "Recebido em " + mesAbrev(m.mes) + ": " + T(m.recebido), i) + emp(xr, m.recebido, m.previsto, "b-prev", "Previsto em " + mesAbrev(m.mes) + ": " + T(m.previsto), i);
      o += barra(xg, m.gasto_pago, "b-gas", "Gasto pago em " + mesAbrev(m.mes) + ": " + T(m.gasto_pago), i) + emp(xg, m.gasto_pago, m.gasto_a_pagar, "b-prev", "A pagar em " + mesAbrev(m.mes) + ": " + T(m.gasto_a_pagar), i);
      if (atual && !S.ocultar) {
        if (m.recebido > 0) o += '<text class="vl-t" x="' + (cx - 2).toFixed(1) + '" y="' + (y(m.recebido + m.previsto) - 6).toFixed(1) + '" text-anchor="end">' + K(m.recebido) + "</text>";
        if (m.gasto_pago > 0) o += '<text class="vl-t" x="' + (cx + 2).toFixed(1) + '" y="' + (y(m.gasto_pago + m.gasto_a_pagar) - 6).toFixed(1) + '" text-anchor="start">' + K(m.gasto_pago) + "</text>";
      }
      o += '<text class="mes' + (atual ? " mes-a" : "") + '" x="' + cx.toFixed(1) + '" y="' + (Hh - 8) + '" text-anchor="middle">' + mesAbrev(m.mes) + "</text>";
    });
    box.innerHTML = '<svg class="serie' + (S.entrou ? "" : " entra") + '" viewBox="0 0 ' + W + " " + Hh + '" width="' + W + '" height="' + Hh + '" role="img" aria-label="Barras por mês: recebido ao lado do gasto pago, com previsto e a pagar tracejados. Os valores estão na tabela abaixo.">' + g + '<line class="base" x1="0" x2="' + W + '" y1="' + (Hh - pb) + '" y2="' + (Hh - pb) + '"/>' + o + "</svg>";
    S.entrou = true;
  }

  function secRxG(F) {
    var r = F.receitas_x_gastos, g = F.gastos, rc = F.recebido, mx = Math.max(r.receitas, r.gastos, 1);
    var sobra = r.receitas - r.gastos, proj = rc.mes + rc.previsto_mes - g.pagos_mes - g.a_pagar_mes;
    function ln(rot, v, e, cls) { return '<div class="rg2"><div class="rg2-t"><span>' + rot + "</span><b>" + R(v) + "</b></div>" + barra(e, frac(v, mx), rot + ": " + T(v), "grosso " + cls) + "</div>"; }
    function res(rot, v) { var p = v >= 0; return "<div><dt>" + rot + "</dt><dd class=\"" + (p ? "pos" : "neg") + '">' + (p ? "Sobra " : "Falta ") + R(Math.abs(v)) + "</dd></div>"; }
    return '<section class="cartao" aria-label="Receitas e gastos do mês"><h2>Receitas e gastos<span>' + mesAbrev(r.mes) + "</span></h2>" + ln("Receitas", r.receitas, "ok", "") + ln("Gastos pagos", r.gastos, "gasto", "") +
      "<dl class=\"res\">" + res("Resultado do mês, só o que já foi pago", sobra) + res("Se o previsto e o a pagar acontecerem", proj) + "</dl></section>";
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
    return '<section class="cartao" aria-label="Saldo por conta"><h2>Contas<span>total ' + R(sd.disponivel) + "</span></h2>" + (li ? '<ul class="ctas">' + li + "</ul>" : '<p class="mudo pq">Nenhuma conta informada ainda.</p>') +
      (fora.length ? '<p class="parcial">' + GH.ico("pendente", 16) + "<span>O total é parcial: " + esc(fora.join(", ")) + (fora.length > 1 ? " ficam" : " fica") + " de fora.</span></p>" : "") +
      '<p class="obs">' + esc(sd.observacao || "") + "</p></section>";
  }

  function secCategorias(F) {
    var cs = F.categorias || [], mx = cs.length ? cs[0].valor : 1, vis = S.todas ? cs : cs.slice(0, 8);
    if (!cs.length) return '<section class="cartao" aria-label="Gastos por categoria"><h2>Gastos por categoria<span>' + mesAbrev(F.mes_atual) + '</span></h2><p class="mudo pq">Nenhum gasto lançado neste mês.</p></section>';
    var li = vis.map(function (c) {
      return '<li class="cat">' + catIco(c.categoria, 20) + '<span class="cat-n">' + esc(catRot(c.categoria)) + '</span><span class="cat-p">' + pct(c.percentual) + '</span><span class="cat-v">' + R(c.valor) + "</span>" + barra("gasto", frac(c.valor, mx), catRot(c.categoria) + ": " + pct(c.percentual) + " dos gastos do mês", "cat-b") + "</li>";
    }).join("");
    return '<section class="cartao" aria-label="Gastos por categoria"><h2>Gastos por categoria<span>' + mesAbrev(F.mes_atual) + ", pagos e a pagar</span></h2><ul class=\"cats\">" + li + "</ul>" +
      (cs.length > 8 ? '<button class="bt mais" type="button" id="ver-todas" aria-expanded="' + S.todas + '">' + (S.todas ? "Mostrar só as 8 maiores" : "Mostrar todas (" + cs.length + ")") + "</button>" : "") + "</section>";
  }

  function secVenc(F) {
    var vs = F.vencimentos || [], atr = vs.filter(function (v) { return v.atrasado || v.dias_restantes < 0; }).length;
    var rot = vs.length ? plural(vs.length, "a pagar", "a pagar") + (atr ? ", " + plural(atr, "atrasado", "atrasados") : "") : "";
    if (!vs.length) return '<section class="cartao" aria-label="Vencimentos"><h2>Vencimentos<span>nenhum</span></h2><p class="nada">' + GH.ico("ok", 18) + "<span>Nenhum vencimento a pagar. Quando o Casemiro lançar um gasto como a pagar, ele aparece aqui com os dias restantes.</span></p></section>";
    var li = vs.map(function (v) {
      var e = estVenc(v), p = v.dias_restantes < 0 ? 100 : clamp(Math.round((30 - v.dias_restantes) * 100 / 30));
      return '<li class="vc e-' + e + '">' + catIco(v.categoria, 20) + '<div class="vc-t"><b>' + esc(mt(v.descricao)) + '</b><span class="mudo">' + dsem(v.data) + ", " + dm(v.data) + " · " + esc(catRot(v.categoria)) + '</span></div><span class="vc-v">' + R(v.valor) + '</span><div class="vc-s">' + chip(e, textoVenc(v)) + barra(e, p, textoVenc(v) + ", " + T(v.valor), "") + "</div></li>";
    }).join("");
    return '<section class="cartao" aria-label="Vencimentos"><h2>Vencimentos<span>' + rot + '</span></h2><ul class="vcs">' + li + "</ul>" + '<p class="obs">A barra enche conforme o prazo se aproxima (janela de 30 dias).</p></section>';
  }

  function secMov(F) {
    var ms = F.movimentos_recentes || [], av = GH.agente("casemiro-financeiro");
    if (!ms.length) return '<section class="cartao" aria-label="Movimentos recentes"><h2>Movimentos recentes<span>nenhum</span></h2><p class="mudo pq">Sem movimentos nesta leitura.</p></section>';
    var li = ms.map(function (m) {
      var rec = m.tipo !== "gasto", pago = m.status === "pago", e = pago ? (rec ? "ok" : "gasto") : "backlog";
      var rot = pago ? (rec ? "Recebido" : "Pago") : (rec ? "A receber" : "A pagar");
      return '<li class="mv"><time class="mv-d" datetime="' + esc(m.data) + '">' + dm(m.data) + "</time>" + catIco(m.categoria, 18) + '<div class="mv-t"><b>' + esc(mt(m.descricao)) + '</b><span class="mudo">' + esc(catRot(m.categoria)) + '</span></div><span class="mv-s">' + chip(e, rot) + '</span><span class="mv-v ' + (rec ? "pos" : "neg") + '">' + (rec ? "+ " : "− ") + R(m.valor) + '</span><span class="mv-a" title="Lançado pelo Casemiro">' + GH.av(av, "rd", 26) + "</span></li>";
    }).join("");
    return '<section class="cartao" aria-label="Movimentos recentes"><h2>Movimentos recentes<span>' + ms.length + ' mais novos, lançados pelo Casemiro</span></h2><ul class="mvs">' + li + "</ul></section>";
  }

  function secFonte(F) {
    var arq = (F.fonte && F.fonte.arquivos) || {}, c = (F.fonte && F.fonte.contagens) || {};
    var li = Object.keys(arq).map(function (k) { return "<li><code>" + esc(k) + "</code><span>" + (arq[k] ? "alterado em " + hm(arq[k]) : "não encontrado") + "</span></li>"; }).join("");
    return '<section class="cartao fonte" aria-label="Fontes desta leitura"><h2>De onde vêm estes números<span>' + (c.movimentos || 0) + " movimentos, " + (c.contas || 0) + " contas, " + (c.vencimentos || 0) + ' vencimentos</span></h2><ul class="fontes">' + li + '</ul><p class="obs">Leitura local dos arquivos do Casemiro. Esta tela só mostra: não paga, não marca como pago e não altera nenhum arquivo.</p></section>';
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
    if (est === "erro") return bloco("erro_geral", "Não consegui ler os dados de Finanças", "O arquivo <code>financas.js</code> não existe ou está ilegível, então não mostro números antigos como se fossem de agora. Rode <code>python estudio/dados/gerar_financas.py</code> e toque em Tentar de novo. Se faltar <code>movimentos.csv</code> ou <code>saldos.csv</code>, o gerador avisa qual.", '<button class="bt prim risco" type="button" id="tentar">' + B.icon("retry", 20) + " Tentar de novo</button>");
    if (est === "vazio") return bloco("vazio_financas", "Ainda não há lançamentos", "Os arquivos foram lidos, mas <code>movimentos.csv</code> e <code>saldos.csv</code> não têm linhas. Peça ao Casemiro para lançar o primeiro saldo e os primeiros recebimentos e gastos, depois gere de novo.") + secFonte(F);
    return secAlertas(F) + '<div class="fin-g b">' + secSerie(F) + '<div class="pilha">' + secRxG(F) + secContas(F) + "</div></div>" +
      '<div class="fin-g c">' + secCategorias(F) + secVenc(F) + "</div>" + '<div class="fin-g">' + secMov(F) + "</div>" + '<div class="fin-g">' + secFonte(F) + "</div>";
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
    B.menu.forEach(function (m, i) { it.push({ g: "Ir para", r: m.nome + (m.id === "financas" ? " (esta tela)" : ""), s: "tecla " + (i + 1), ic: m.ic, f: function () { if (m.id === "financas") { window.scrollTo(0, 0); document.getElementById("principal").focus(); } else location.href = href(m.id); } }); });
    it.push({ g: "Nesta tela", r: S.ocultar ? "Mostrar valores" : "Ocultar valores", s: "tecla O", ic: "lock", f: alternarOcultar });
    it.push({ g: "Nesta tela", r: "Alternar tema claro e escuro", s: "tecla T", ic: "sun", f: alternarTema });
    if (window.FINANCAS_MOCK) (window.FINANCAS_CENARIOS || []).forEach(function (c) { it.push({ g: "Cenário de exemplo", r: c[1], s: "mock inventado", ic: "financas", f: function () { location.search = "?cenario=" + c[0]; } }); });
    palIt = it.filter(function (x) { return !nq || norm(x.r + " " + x.s + " " + x.g).indexOf(nq) >= 0; }).slice(0, 14); palSel = 0; palDesenhar();
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
    else if (/^[1-8]$/.test(k)) { var m = B.menu[+k - 1]; if (m.id !== "financas") location.href = href(m.id); }
  });

  function render() {
    var F = window.FINANCAS, est = estado(F), y = window.scrollY;
    app.innerHTML = ilha(F, est) + '<main id="principal" class="papel" tabindex="-1"><div class="pag-cab"><h1 class="pag">Finanças</h1><p class="sub">Leitura local dos arquivos do Casemiro. Aqui só se olha: nada é pago nem alterado. ' + kbd("O") + " oculta os valores.</p></div>" + corpo(F, est) + "</main>";
    document.title = "Finanças: Ecossistema do Guilherme";
    document.getElementById("abrir-paleta").onclick = abrirPaleta;
    document.getElementById("ocultar").onclick = alternarOcultar;
    document.getElementById("tema").onclick = alternarTema;
    var t = document.getElementById("tentar"); if (t) t.onclick = function () { location.reload(); };
    var vt = document.getElementById("ver-todas"); if (vt) vt.onclick = function () { S.todas = !S.todas; render(); var n = document.getElementById("ver-todas"); if (n) n.focus({ preventScroll: true }); };
    if (est === "ok") desenharSerie();
    window.scrollTo(0, y);
  }
  var rz; window.addEventListener("resize", function () { cancelAnimationFrame(rz); rz = requestAnimationFrame(function () { if (document.getElementById("serie-box")) desenharSerie(); }); });
  render();
})();
