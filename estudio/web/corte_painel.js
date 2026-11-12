"use strict";
/* Painel do Ecossistema do Guilherme: Dashboard, Resumo, Documentos, Agentes e Setores. Só no computador. Só a página de um agente edita (corte_painel_agente.js).
   Todo texto vindo de arquivo entra por textContent (função h), nunca como HTML. Sem "visto", sem etiquetas Novo/Alterado (decisão do Guilherme). */

/* ---------- Auxiliares (esta página não carrega o app.js) ---------- */
function h(tag, attrs, ...filhos) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "html") throw new Error("sem HTML cru");
    else if (k in el && k !== "list") el[k] = v;
    else el.setAttribute(k, v);
  }
  for (const f of filhos.flat(Infinity)) {
    if (f === null || f === undefined || f === false) continue;
    el.append(f.nodeType ? f : String(f));
  }
  return el;
}
async function api(metodo, url) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), 15000);
  try {
    const r = await fetch(url, { method: metodo, cache: "no-store", signal: ctl.signal });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error((d.erro || ["Falha na requisição."]).join(" ")); e.status = r.status; throw e; }
    return d;
  } finally { clearTimeout(t); }
}
function aviso(texto, erro) {
  const a = h("div", { class: "aviso" + (erro ? " erro" : "") }, texto);
  document.getElementById("avisos").append(a);
  setTimeout(() => a.remove(), erro ? 7000 : 3500);
}
function ir(url) { if (url.startsWith("/painel")) PainelTela.ir(url); else location.assign(url); }

/* Nesta página replaceChildren aceita listas e ignora null/false, como a função h (senão "null" apareceria como texto). */
const _rc = Element.prototype.replaceChildren;
Element.prototype.replaceChildren = function (...filhos) { return _rc.apply(this, filhos.flat(Infinity).filter((x) => x !== null && x !== undefined && x !== false)); };

/* ---------- Tema claro/escuro (padrão escuro; lembra a escolha) ---------- */
const Tema = {
  atual() { try { return localStorage.getItem("painel-tema") === "claro" ? "claro" : "escuro"; } catch { return "escuro"; } },
  aplicar(t) { document.documentElement.dataset.tema = t; },
  alternar() { const t = this.atual() === "claro" ? "escuro" : "claro"; try { localStorage.setItem("painel-tema", t); } catch { /* sem armazenamento: vale só nesta aba */ } this.aplicar(t); Tema._sessao = t; Corte.desenharNav(); },
  efetivo() { return Tema._sessao || this.atual(); },
};
Tema.aplicar(Tema.atual());

const pad = (n) => String(n).padStart(2, "0");
const MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"];
const dataCurta = (d) => `${pad(d.getDate())} ${MESES[d.getMonth()]} ${d.getFullYear()}`;
const hhmm = (d) => `${pad(d.getHours())}:${pad(d.getMinutes())}`;
function relativo(iso) {
  const d = new Date(iso);
  if (!iso || isNaN(d)) return "–";
  const ag = new Date(), min = Math.floor((ag - d) / 60000);
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  if (d.toDateString() === ag.toDateString()) return `hoje ${hhmm(d)}`;
  const ontem = new Date(ag); ontem.setDate(ag.getDate() - 1);
  if (d.toDateString() === ontem.toDateString()) return `ontem ${hhmm(d)}`;
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)} ${hhmm(d)}`;
}
function completa(iso) {
  const d = new Date(iso);
  if (!iso || isNaN(d)) return "";
  return `${d.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" })} às ${hhmm(d)}:${pad(d.getSeconds())}`;
}
const dataHora = (iso) => { const d = new Date(iso); return isNaN(d) ? "–" : `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} às ${hhmm(d)}`; };
const cortar = (s, n) => { s = String(s ?? ""); return s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s; };
const NOME_AREA = { programacao: "Programação", inteligencia: "Inteligência", agentes: "Agentes", videos: "Vídeos", componentes: "Componentes", prompts: "Prompts", raiz: "Raiz", ecossistema: "Ecossistema", produtividade: "Produtividade", financas: "Finanças", skills: "Skills", pesquisa_videos: "Pesquisa de vídeos", clipes: "Clipes", contas: "Contas", reels: "Reels e TikTok", thumbnails: "Thumbnails", referencias: "Referências" };
const nomeArea = (a) => NOME_AREA[a] || a;
const emBloco = (b) => b && !b.erro;
const motivoCurto = (b) => cortar((b && b.erro) || "sem resposta", 80);

/* id, nome no menu, caminho, etiqueta do topo, título (parte normal + palavra final em destaque) */
const ABAS = [["dashboard", "Dashboard", "/painel", "VISÃO GERAL / 01", ["Agora, em um", "olhar"]], ["resumo", "Resumo", "/painel/resumo", "RESUMO / 02", ["O que", "aconteceu"]], ["documentos", "Documentos", "/painel/documentos", "CONHECIMENTO / 03", ["", "Documentos"]], ["agentes", "Agentes", "/painel/agentes", "TIME / 04", ["Seu time em", "campo"]], ["setores", "Setores", "/painel/setores", "ESTRUTURA / 05", ["Cada frente, um", "propósito"]], ["videos", "Vídeos", "/painel/videos", "ESTÚDIO / 06", ["Da ideia ao", "vídeo"]]];
const abaDe = (caminho) => { const m = caminho.replace(/\/+$/, "").match(/^\/painel(?:\/(\w+))?(?:\/[\w-]+)?$/); const id = m && m[1]; return ABAS.find((a) => a[0] === id) ? id : "dashboard"; };

/* ---------- Estado e ciclo de leitura ---------- */
const T = { aba: null, dados: {}, assin: {}, lido: null, erro: null, marca: null, timer: null, ciclo: 0, lendo: false, rolouEm: 0, pendenteLista: null, lim: 100, busca: "", area: "", doc: null, epocas: {}, banner: null };

const PainelTela = {
  ir(url, substituir) {
    const antes = location.pathname + location.search;
    if (antes !== url && !confirmarSaida()) return;   // agente com alterações não salvas
    if (antes !== url) (substituir ? history.replaceState : history.pushState).call(history, {}, "", url);
    this.montar();
  },
  montar() {
    const aba = abaDe(location.pathname);
    document.title = `${ABAS.find((a) => a[0] === aba)[1]} · Painel · Ecossistema do Guilherme`;
    T.aba = aba; T.assin = {}; T.ciclo = 0; T.doc = null; T.docEstado = null; T.banner = null;
    T.agenteId = aba === "agentes" ? agenteDe(location.pathname) : null; T.urlAtual = location.pathname + location.search;
    if (!T.agenteId) { AG.id = null; AG.dados = null; desmontarEditor(); }
    Corte.desenharNav();
    montarCasca();
    if (aba === "documentos") montarDocumentos();
    else if (aba === "agentes") (T.agenteId ? montarAgente : montarAgentes)();
    carregar(true);
  },
};
addEventListener("popstate", () => {
  if (!confirmarSaida()) { history.pushState({}, "", T.urlAtual || "/painel/agentes"); return; }   // fica na página do agente
  PainelTela.montar();
});

/* O que cada aba precisa da API. */
async function buscarAba(aba) {
  const lista = (nome, url) => api("GET", url).then((d) => [nome, d]);
  const ped = {
    dashboard: () => [lista("visao", "/api/painel/visao"), lista("resumo", "/api/painel/resumo")],
    resumo: () => [lista("resumo", "/api/painel/resumo")],
    documentos: () => [lista("docs", `/api/painel/documentos?${new URLSearchParams({ area: T.area, q: T.busca, limite: T.lim, offset: 0 })}`)],
    videos: () => [lista("visao", "/api/painel/visao")],
    agentes: () => [lista("setores", "/api/painel/setores"), lista("visao", "/api/painel/visao")],
    setores: () => [lista("setores", "/api/painel/setores"), lista("visao", "/api/painel/visao")],
  }[aba]();
  return Object.fromEntries(await Promise.all(ped));
}

async function carregar(forcar) {
  if (T.lendo && !forcar) return;
  T.lendo = true;
  const aba = T.aba, meu = (T.seq = (T.seq || 0) + 1);  // resposta atrasada de um pedido antigo (outro filtro) é descartada
  try {
    const novo = await buscarAba(aba);
    if (aba !== T.aba || meu !== T.seq) return;
    Object.assign(T.dados, novo);
    const voltou = !!T.erro;
    T.erro = null; T.lido = new Date();
    if (novo.docs) T.marca = novo.docs.marca;
    desenhar();
    if (voltou) avisarVolta();
  } catch (e) {
    if (aba !== T.aba || meu !== T.seq) return;
    T.erro = { msg: e.message || String(e), rede: e instanceof TypeError || e.name === "AbortError" };
    desenhar();
  } finally { if (meu === T.seq) { T.lendo = false; agendar(); } }
}

function agendar() {
  clearTimeout(T.timer);
  T.timer = setTimeout(tick, T.erro ? 15000 : 5000);
}
async function tick() {
  if (document.hidden) return agendar();
  T.ciclo++;
  if (T.erro) return carregar(true);
  if (T.aba === "documentos") {
    try {
      const m = await api("GET", `/api/painel/mudancas?desde=${encodeURIComponent(T.marca || "")}`);
      if (m.mudou) { T.mudados = m.caminhos || []; return carregar(true); }
      T.lido = new Date(); atualizarLido();
    } catch (e) { T.erro = { msg: e.message, rede: e instanceof TypeError }; desenhar(); }
    return agendar();
  }
  if (T.ciclo % 2 === 0) return carregar(true);  // demais abas: a cada ~10 s
  agendar();
}
document.addEventListener("visibilitychange", () => { if (!document.hidden && T.aba) carregar(true); });
setInterval(() => document.querySelectorAll("[data-iso]").forEach((el) => { el.textContent = relativo(el.dataset.iso); }), 30000);

/* ---------- Casca: abas, hora da leitura, faixas ---------- */
function montarCasca() {
  const app = document.getElementById("app");
  const bloqueado = !["localhost", "127.0.0.1"].includes(location.hostname);
  if (bloqueado) {
    app.replaceChildren(h("main", { class: "pn" }, h("div", { class: "faixa falha", id: "pn-bloqueio", role: "alert" },
      h("b", {}, "O painel do ecossistema abre só no computador onde o Corte está rodando."),
      h("p", {}, "Motivo: ele mostra textos internos dos agentes e do projeto, e não deve trafegar pelo Wi-Fi. Abra http://127.0.0.1:8765/painel neste computador."))));
    T.bloqueado = true;
    return;
  }
  T.bloqueado = false;
  const info = ABAS.find((x) => x[0] === T.aba);
  const botao = h("button", { class: "btn mini", id: "pn-atualizar", type: "button", onclick: async (e) => {
    const b = e.currentTarget; b.disabled = true; b.textContent = "Atualizando...";
    await carregar(true);
    setTimeout(() => { b.disabled = false; b.textContent = "Atualizar agora"; }, 600);
  } }, "Atualizar agora");
  app.replaceChildren(h("main", { class: "pn" },
    h("div", { class: "pn-meta" }, h("span", { class: "pn-etiqueta" }, info[3]), h("span", { class: "pn-fio", "aria-hidden": "true" }), h("span", { class: "pn-data" }, dataCurta(new Date())), h("span", { class: "pn-barra", "aria-hidden": "true" }, "|"),
      h("span", { class: "mini", id: "pn-lido", "aria-live": "off" }, "Lendo..."), h("span", { class: "selo aguardando", id: "pn-velho", hidden: true }, "Desatualizado")),
    h("header", { class: "pn-topo" }, h("h1", { class: "pn-titulo" }, info[4][0] ? info[4][0] + " " : "", h("span", { class: "pn-dest" }, info[4][1]), h("span", { class: "pn-ponto" }, ".")), h("span", { class: "espaco" }), botao),
    h("div", { id: "pn-faixa" }),
    h("div", { id: "pn-corpo", class: "pn-corpo", role: "region", "aria-label": info[1], "aria-live": "polite" }),
    h("footer", { class: "pn-pe" }, h("span", {}, "Seu espaço. Seu ritmo."), h("span", { class: "pn-barras", "aria-hidden": "true" }, "///"))));
  desenharCorpoCarregando();
}

function atualizarLido() {
  const l = document.getElementById("pn-lido"), v = document.getElementById("pn-velho");
  if (!l) return;
  l.textContent = T.lido ? `Atualizado às ${hhmm(T.lido)}` : "Lendo...";
  v.hidden = !(T.erro && T.lido);
}

function avisarVolta() {
  const f = document.getElementById("pn-faixa");
  if (!f) return;
  f.replaceChildren(h("div", { class: "faixa andando", id: "pn-voltou", role: "status" }, "Voltou a atualizar."));
  setTimeout(() => { if (!T.erro) f.replaceChildren(); }, 3000);
}

function desenharCorpoCarregando() {
  const c = document.getElementById("pn-corpo");
  if (!c || T.aba === "documentos" || T.agenteId) return;
  c.replaceChildren(h("div", { class: "pn-carregando", id: "pn-carregando" }, h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }),
    h("p", { class: "mudo" }, T.aba === "resumo" ? "Lendo o último registro..." : "Lendo o ecossistema...")));
}

/* Redesenha só quando o conteúdo mudou: nada pisca no polling. */
function desenhar() {
  if (T.bloqueado) return;
  atualizarLido();
  const faixa = document.getElementById("pn-faixa");
  const tem = Object.keys(T.dados).length > 0 && dadosDaAba();
  if (T.erro && tem) {
    faixa.replaceChildren(h("div", { class: "faixa falha", id: "pn-parada", role: "alert" }, h("b", {}, "Atualização parada. "), `Última leitura às ${T.lido ? hhmm(T.lido) : "—"}. `, h("button", { class: "btn mini", id: "pn-tentar", onclick: () => carregar(true) }, "Tentar agora")));
  } else if (!T.erro && faixa.querySelector("#pn-parada")) faixa.replaceChildren();
  if (T.erro && !tem) return desenharErroGeral();
  if (!tem) return;
  ({ dashboard: desenharDashboard, resumo: desenharResumo, documentos: desenharDocumentos, agentes: () => (T.agenteId ? desenharPaginaAgente() : desenharAgentes()), videos: desenharVideos, setores: desenharSetores })[T.aba]();
}
function dadosDaAba() {
  const n = { dashboard: ["visao"], resumo: ["resumo"], documentos: ["docs"], agentes: ["setores"], videos: ["visao"], setores: ["setores"] }[T.aba];
  return n.every((k) => T.dados[k]);
}
function desenharErroGeral() {
  const corpo = document.getElementById(T.aba === "documentos" ? "pn-lista" : "pn-corpo") || document.getElementById("pn-corpo");
  corpo.replaceChildren(h("div", { class: "faixa falha", id: "pn-erro-geral", role: "alert" },
    h("b", {}, "Não consegui ler o ecossistema."),
    h("p", {}, "O servidor do Ecossistema pode ter sido fechado ou travou. Próximo passo: tentar de novo; se continuar, reabra com python -m corte."),
    h("button", { class: "btn mini", id: "pn-tentar", onclick: () => carregar(true) }, "Tentar de novo"),
    h("details", { class: "mini" }, h("summary", {}, "Ver detalhe"), h("span", {}, T.erro.msg))));
}
function trocarSeMudou(chave, valor, el, fn) {
  const a = JSON.stringify(valor);
  if (T.assin[chave] === a) return false;
  T.assin[chave] = a; fn(el); return true;
}

/* ---------- Dashboard ---------- */
function cartao(id, titulo, numero, apoio, url, extra) {
  return h("a", { class: "pn-cartao" + (extra ? " " + extra : ""), id: `pn-c-${id}`, href: url, onclick: (e) => { e.preventDefault(); ir(url); } },
    h("span", { class: "pn-c-tit" }, titulo), h("span", { class: "pn-c-num" }, numero), h("span", { class: "pn-c-apoio" }, apoio));
}
function cartaoIndisponivel(id, titulo, bloco, url) {
  return cartao(id, titulo, "—", `Não consegui ler: ${motivoCurto(bloco)}. Tente Atualizar agora.`, url, "indisp");
}
function desenharDashboard() {
  const v = T.dados.visao, r = T.dados.resumo;
  const el = document.getElementById("pn-corpo");
  trocarSeMudou("dash", [v, r && r.linhas], el, () => {
    const cartoes = [];
    const vid = v.videos;
    cartoes.push(emBloco(vid) ? cartao("videos", "Vídeos em andamento", vid.em_andamento_total ?? 0,
      vid.em_andamento_total ? `${vid.em_andamento_total} em produção ou esperando você` : "Nenhum vídeo em andamento", "/") : cartaoIndisponivel("videos", "Vídeos em andamento", vid, "/"));
    const ag = v.agentes_ativos;
    if (emBloco(ag)) {
      const n = (ag.resumo && ag.resumo.trabalhando) || 0, nomes = (ag.agentes || []).filter((a) => a.estado === "trabalhando").slice(0, 2).map((a) => a.craque || a.id);
      const extras = [];
      if (ag.resumo && ag.resumo.falhou) extras.push(`${ag.resumo.falhou} falhou`);
      if (ag.resumo && ag.resumo.espera_voce) extras.push(`${ag.resumo.espera_voce} espera você`);
      cartoes.push(cartao("agentes", "Agentes ativos agora", n, [n ? nomes.join(", ") : "Nenhum agente trabalhando agora", extras.length ? ` · ${extras.join(" · ")}` : ""].join(""), "/painel/agentes"));
    } else cartoes.push(cartaoIndisponivel("agentes", "Agentes ativos agora", ag, "/painel/agentes"));
    const sp = v.sprint;
    if (emBloco(sp) && sp.nome) {
      const q = sp.quadro || {};
      cartoes.push(cartao("sprint", "Sprint", sp.nome, `${sp.estado || ""}${sp.inicio ? ` · ${sp.inicio} a ${sp.fim}` : ""} · Fazendo ${q.Fazendo ?? 0}, Em teste ${q["Em teste"] ?? 0}, Feito ${q.Feito ?? 0}`, "/painel/setores"));
    } else if (emBloco(sp)) cartoes.push(cartao("sprint", "Sprint", "0", "Sem sprint ativa", "/painel/setores"));
    else cartoes.push(cartaoIndisponivel("sprint", "Sprint", sp, "/painel/setores"));
    const dec = v.decisoes_pendentes;
    if (Array.isArray(dec)) {
      const ids = dec.slice(0, 3).map((d) => d.id).join(", ") + (dec.length > 3 ? ` +${dec.length - 3}` : "");
      cartoes.push(cartao("decisoes", "Decisões pendentes suas", dec.length, dec.length ? ids : "Nada esperando você", "#pn-exige", dec.length ? "destaque" : "ok"));
    } else cartoes.push(cartaoIndisponivel("decisoes", "Decisões pendentes suas", dec, "/painel"));
    const dh = v.documentos_hoje;
    cartoes.push(emBloco(dh) ? cartao("docs", "Documentos alterados hoje", dh.total ?? 0, dh.total ? `Mais recente: ${cortar(((dh.recentes || [])[0] || {}).titulo || "", 40)}` : "Nenhum documento mudou hoje", "/painel/documentos") : cartaoIndisponivel("docs", "Documentos alterados hoje", dh, "/painel/documentos"));
    const exige = Array.isArray(dec) && dec.length ? h("section", { class: "pn-exige", id: "pn-exige", "aria-label": "O que exige você" }, h("h2", {}, "O que exige você"),
      h("ul", {}, dec.map((d) => h("li", {}, h("b", {}, d.id), ` · precisa da sua escolha: ${cortar(d.pedido, 100)} `, h("a", { class: "btn mini", href: `/painel/documentos?q=${encodeURIComponent(d.id)}`, onclick: (e) => { e.preventDefault(); ir(`/painel/documentos?q=${encodeURIComponent(d.id)}`); } }, "Abrir"))))) : null;
    el.replaceChildren(h("div", { class: "pn-cartoes" }, cartoes), exige, blocoResumo(r));
  });
}
function blocoResumo(r) {
  return h("section", { class: "pn-resumo-mini", id: "pn-resumo-mini" }, h("h2", {}, "Resumo agora"), linhasResumo(r), h("a", { href: "/painel/resumo", onclick: (e) => { e.preventDefault(); ir("/painel/resumo"); } }, "Ver resumo"));
}
function linhasResumo(r) {
  if (!r || r.erro) return h("p", { class: "mudo" }, `Não consegui ler o resumo: ${motivoCurto(r)}.`);
  const l = (r.linhas || []).slice(0, 2);
  if (!l.length) return h("p", { class: "pn-linha" }, "Nada executado ainda.");
  return h("div", { class: "pn-linhas" }, l.map((t, i) => h("p", { class: "pn-linha", "data-linha": i + 1 }, t)));
}

/* ---------- Resumo ---------- */
function desenharResumo() {
  const r = T.dados.resumo, el = document.getElementById("pn-corpo");
  trocarSeMudou("resumo", r, el, () => {
    el.replaceChildren(h("section", { class: "pn-resumo", id: "pn-resumo" }, linhasResumo(r),
      h("p", { class: "mini mudo" }, `Base lida às ${r && r.base_em ? hhmm(new Date(r.base_em)) : "—"} · atualiza sozinho a cada 10 s`)));
  });
}

/* ---------- Documentos ---------- */
let listaEl, painelEl, areaSel, statusEl, buscaEl;
function montarDocumentos() {
  const q = new URLSearchParams(location.search);
  T.busca = q.get("q") || ""; T.area = q.get("area") || ""; T.lim = 100; T.epocas = {}; T.mudados = [];
  let esp = null;
  buscaEl = h("input", { type: "search", id: "pn-busca", placeholder: "Buscar documentos", "aria-label": "Buscar por título ou caminho", value: T.busca, oninput: (e) => {
    clearTimeout(esp); esp = setTimeout(() => { T.busca = e.target.value.trim(); T.lim = 100; carregar(true); }, 300);
  } });
  areaSel = h("select", { id: "pn-area", "aria-label": "Filtrar por área", onchange: (e) => { T.area = e.target.value; T.lim = 100; carregar(true); } }, h("option", { value: "" }, "Todas as áreas"));
  statusEl = h("p", { class: "mini mudo", id: "pn-status", "aria-live": "polite" }, "Mais recentes primeiro");
  listaEl = h("div", { id: "pn-lista", class: "pn-lista", role: "list", onscroll: () => { T.rolouEm = Date.now(); } },
    h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }));
  painelEl = h("div", { id: "pn-leitura", class: "pn-leitura" });
  const anuncio = h("div", { id: "pn-anuncio", class: "so-leitor", "aria-live": "polite" });
  const corpo = document.getElementById("pn-corpo");
  corpo.replaceChildren(h("div", { class: "pn-docs" }, h("div", { class: "pn-col-lista" }, h("div", { class: "pn-ferr" }, buscaEl, areaSel), statusEl, listaEl), painelEl), anuncio);
  corpo.classList.remove("lendo");
  mostrarLeituraVazia();
  const cam = q.get("caminho");
  if (cam) abrirDoc(cam);
}
function mostrarLeituraVazia() { painelEl.replaceChildren(h("p", { class: "vazio-texto", id: "pn-sem-selecao" }, "Escolha um documento na lista para ler aqui.")); }

function desenharDocumentos() {
  const d = T.dados.docs;
  if (!listaEl || !listaEl.isConnected) return;
  const opcoes = Object.keys(d.areas || {});
  trocarSeMudou("areas", opcoes, areaSel, () => {
    areaSel.replaceChildren(h("option", { value: "" }, "Todas as áreas"), ...opcoes.map((a) => h("option", { value: a }, `${nomeArea(a)} (${d.areas[a]})`)));
    areaSel.value = T.area;
  });
  statusEl.textContent = `Mais recentes primeiro · ${d.total} documento${d.total === 1 ? "" : "s"}${T.busca || T.area ? " na busca" : ""}`;
  checarDocAberto(d);
  const aplicar = () => {
    T.pendenteLista = null;
    const sobem = [];
    for (const x of d.documentos) { const antes = T.epocas[x.caminho]; if (antes !== undefined && x.alterado_em_epoch > antes) sobem.push(x); T.epocas[x.caminho] = x.alterado_em_epoch; }
    const mudou = trocarSeMudou("lista", d.documentos.map((x) => [x.caminho, x.alterado_em_epoch, x.titulo]).concat([[T.lim, d.total]]), listaEl, () => {
      const itens = d.documentos.map((x) => itemDoc(x, sobem.some((s) => s.caminho === x.caminho)));
      let conteudo = itens;
      if (!d.documentos.length) {
        conteudo = [h("p", { class: "vazio-texto", id: "pn-lista-vazia" }, T.busca || T.area
          ? [`Nenhum documento combina com '${T.busca || nomeArea(T.area)}'. `, h("button", { class: "btn mini", onclick: () => { buscaEl.value = ""; areaSel.value = ""; T.busca = ""; T.area = ""; carregar(true); } }, "Limpar busca")]
          : "Nenhum documento encontrado. O painel lê as pastas do ecossistema permitidas; se isso é novo, avise o Rodrygo.")];
      } else if (d.total > d.documentos.length) {
        conteudo = itens.concat([h("button", { class: "btn mini", id: "pn-mais", onclick: () => { T.lim += 100; carregar(true); } }, `Ver mais 100 (de ${d.total})`)]);
      }
      listaEl.replaceChildren(...conteudo);
    });
    if (mudou && sobem.length) document.getElementById("pn-anuncio").textContent = `Documento atualizado: ${sobem[0].titulo}`;
  };
  if (Date.now() - T.rolouEm < 1000) {  // quem está rolando a lista não perde o lugar: espera 1 s parado
    if (!T.pendenteLista) T.pendenteLista = setTimeout(() => { T.pendenteLista = null; if (T.aba === "documentos") desenharDocumentos(); }, 1000);
    return;
  }
  aplicar();
}
function itemDoc(x, destaque) {
  const url = `/painel/documentos?caminho=${encodeURIComponent(x.caminho)}`;
  return h("button", { type: "button", role: "listitem", class: "pn-item" + (destaque ? " destaque" : "") + (T.doc && T.doc.caminho === x.caminho ? " sel" : ""), "data-caminho": x.caminho, onclick: () => { history.replaceState({}, "", url); abrirDoc(x.caminho); } },
    h("span", { class: "pn-item-tit" }, x.titulo),
    h("span", { class: "pn-item-cam" }, x.caminho),
    h("span", { class: "pn-item-meta mini mudo" }, nomeArea(x.area), h("span", { class: "pn-bar", "aria-hidden": "true" }, "|"),
      h("time", { class: "pn-quando", "data-iso": x.alterado_em, title: completa(x.alterado_em), datetime: x.alterado_em }, relativo(x.alterado_em))));
}

async function abrirDoc(caminho) {
  document.getElementById("pn-corpo").classList.add("lendo");
  T.doc = { caminho }; T.banner = null;
  document.querySelectorAll(".pn-item").forEach((b) => b.classList.toggle("sel", b.dataset.caminho === caminho));
  painelEl.replaceChildren(h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("p", { class: "mudo" }, "Abrindo o documento..."));
  try {
    const d = await api("GET", `/api/painel/documento?caminho=${encodeURIComponent(caminho)}`);
    if (!T.doc || T.doc.caminho !== caminho) return;
    T.doc = d;
    desenharLeitura();
  } catch (e) {
    if (!T.doc || T.doc.caminho !== caminho) return;
    if (e.status === 404) painelEl.replaceChildren(voltar(), h("div", { class: "faixa velha", id: "pn-doc-sumiu" }, "Este documento foi apagado ou saiu da lista permitida.", " ", h("button", { class: "btn mini", onclick: fecharDoc }, "Voltar à lista")));
    else painelEl.replaceChildren(voltar(), h("div", { class: "faixa falha", id: "pn-doc-erro", role: "alert" }, "Não consegui abrir este documento. Pode estar sendo salvo agora. ", h("button", { class: "btn mini", onclick: () => abrirDoc(caminho) }, "Tentar de novo")));
  }
}
function fecharDoc() { T.doc = null; document.getElementById("pn-corpo").classList.remove("lendo"); history.replaceState({}, "", "/painel/documentos"); document.querySelectorAll(".pn-item.sel").forEach((b) => b.classList.remove("sel")); mostrarLeituraVazia(); }
const voltar = () => h("button", { class: "btn leve mini pn-voltar", id: "pn-voltar", onclick: fecharDoc }, "← Voltar à lista");

function desenharLeitura() {
  const d = T.doc;
  const copiar = h("button", { class: "btn mini", id: "pn-copiar", type: "button", onclick: async (e) => {
    const b = e.currentTarget;
    try { await navigator.clipboard.writeText(d.caminho); b.textContent = "Copiado"; } catch { b.textContent = "Não consegui copiar"; }
    setTimeout(() => { b.textContent = "Copiar caminho"; }, 2000);
  } }, "Copiar caminho");
  const corpo = d.conteudo === null || d.conteudo === undefined
    ? h("div", { class: "faixa velha", id: "pn-omitido" }, "Conteúdo omitido: parece conter credencial. Abra o arquivo direto no seu editor.")
    : leituraDom(d.caminho, d.conteudo, d.titulo);
  painelEl.replaceChildren(voltar(),
    h("div", { class: "pn-l-topo" }, h("h2", {}, d.titulo), h("p", { class: "pn-l-meta" }, d.caminho, " · Atualizado em ", h("time", { title: completa(d.alterado_em) }, dataHora(d.alterado_em)))),
    h("div", { class: "linha-flex" }, copiar, /^\.claude\/agents\//.test(d.caminho) ? h("a", { class: "btn mini", href: `/painel/agentes/${d.caminho.split("/").pop().replace(/\.md$/, "")}`, id: "pn-abrir-agentes", onclick: (e) => { e.preventDefault(); ir(e.currentTarget.getAttribute("href")); } }, "Abrir e editar este agente") : null),
    h("div", { id: "pn-doc-faixa" }),
    corpo,
    d.cortado ? h("p", { class: "mini mudo" }, "Documento longo: mostrando só o começo.") : null,
    h("p", { class: "mini mudo pn-rodape" }, "Somente leitura. Para editar, use o editor ou a tela Agentes."));
}
/* Documento aberto mudou: faixa com Recarregar; o texto não troca sozinho (a rolagem fica onde está). */
function checarDocAberto(lista) {
  if (!T.doc || !T.doc.alterado_em_epoch) return;
  const x = lista.documentos.find((i) => i.caminho === T.doc.caminho);
  const mudou = x && x.alterado_em_epoch > T.doc.alterado_em_epoch;
  const f = document.getElementById("pn-doc-faixa");
  if (!f || !mudou || f.querySelector("#pn-recarregar")) return;
  f.replaceChildren(h("div", { class: "faixa velha", id: "pn-doc-mudou", role: "status" }, "Este documento mudou. ", h("button", { class: "btn mini", id: "pn-recarregar", onclick: () => abrirDoc(T.doc.caminho) }, "Recarregar")));
}

/* ---------- Leitura limpa: markdown vira DOM (sem innerHTML; tudo por textContent; links só http/https/relativos) ---------- */
function linkSeguro(u) { u = String(u || "").trim(); return /^(https?:\/\/|\/(?!\/)|\.{0,2}\/|#)/i.test(u) || /^[\w.-]+(\/[\w./#%-]*)?$/.test(u) ? u : null; }
function inline(t) {
  const out = [], re = /`([^`]+)`|\*\*([^*]+)\*\*|__([^_]+)__|\*([^*\s][^*]*)\*|\[([^\]]+)\]\(([^)\s]+)\)/g;
  let i = 0, m;
  t = String(t);
  while ((m = re.exec(t))) {
    if (m.index > i) out.push(t.slice(i, m.index));
    if (m[1] !== undefined) out.push(h("code", { class: "md-cod" }, m[1]));
    else if (m[2] !== undefined || m[3] !== undefined) out.push(h("strong", {}, inline(m[2] ?? m[3])));
    else if (m[4] !== undefined) out.push(h("em", {}, inline(m[4])));
    else {
      const u = linkSeguro(m[6]);
      if (u && /^https?:/i.test(u)) out.push(h("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, m[5]));
      else if (u && u[0] === "#") out.push(m[5]);
      else out.push(m[5]);  // relativo ou inseguro: só o texto (o arquivo não abre fora do painel)
    }
    i = re.lastIndex;
  }
  if (i < t.length) out.push(t.slice(i));
  return out;
}
function mdParaDom(texto, titulo) {
  const L = String(texto || "").replace(/\r/g, "").split("\n");
  let i = 0;
  if (L[0] && L[0].trim() === "---") { const fim = L.indexOf("---", 1); if (fim > 0) i = fim + 1; }  // cabeçalho técnico (front matter) não interessa
  const o = [], item = /^\s*([-*+]|\d+[.)])\s+/, linhaTab = /^\s*\|.*\|\s*$/;
  while (i < L.length) {
    const l = L[i];
    if (/^\s*```/.test(l)) { const b = []; i++; while (i < L.length && !/^\s*```/.test(L[i])) b.push(L[i++]); i++; o.push(h("pre", { class: "md-bloco" }, b.join("\n"))); continue; }
    const t = l.match(/^(#{1,6})\s+(.*)/);
    if (t) {
      if (!o.length && t[1].length === 1 && titulo && t[2].trim() === titulo) { i++; continue; }  // o título já aparece no topo da leitura
      o.push(h("h" + Math.min(t[1].length + 1, 4), { class: "md-t" }, inline(t[2]))); i++; continue;
    }
    if (linhaTab.test(l) && i + 1 < L.length && /^\s*\|[\s:|-]+\|\s*$/.test(L[i + 1])) {
      const lin = (r) => r.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const cab = lin(l); i += 2; const rs = [];
      while (i < L.length && linhaTab.test(L[i])) rs.push(lin(L[i++]));
      o.push(h("div", { class: "md-tabela" }, h("table", {}, h("thead", {}, h("tr", {}, cab.map((c) => h("th", { scope: "col" }, inline(c))))), h("tbody", {}, rs.map((r) => h("tr", {}, r.map((c) => h("td", {}, inline(c)))))))));
      continue;
    }
    if (item.test(l)) {
      const ord = /^\s*\d/.test(l), its = [];
      while (i < L.length && item.test(L[i])) its.push(h("li", {}, inline(L[i++].replace(item, ""))));
      o.push(h(ord ? "ol" : "ul", {}, its)); continue;
    }
    if (/^\s*>/.test(l)) { const q = []; while (i < L.length && /^\s*>/.test(L[i])) q.push(L[i++].replace(/^\s*>\s?/, "")); o.push(h("blockquote", {}, inline(q.join(" ")))); continue; }
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(l)) { o.push(h("hr")); i++; continue; }
    if (!l.trim()) { i++; continue; }
    const p = [l]; i++;
    while (i < L.length && L[i].trim() && !/^(\s*#{1,6}\s|\s*```|\s*>|\s*\|)/.test(L[i]) && !item.test(L[i])) p.push(L[i++]);
    o.push(h("p", {}, inline(p.join(" ")))); 
  }
  return h("div", { class: "md", id: "pn-texto" }, o.length ? o : h("p", { class: "mudo" }, "Documento vazio."));
}
function jsonParaDom(texto) {
  let v;
  try { v = JSON.parse(texto); } catch { return h("div", { class: "md", id: "pn-texto" }, h("p", { class: "mudo" }, "Não consegui ler este arquivo como dados organizados."), h("pre", { class: "md-bloco" }, texto)); }
  const ACENTOS = { ultima: "última", cartoes: "cartões", acao: "ação", decisao: "decisão", decisoes: "decisões" };
  const rot = (k) => typeof k === "number" ? `Item ${k}` : (s => s.charAt(0).toUpperCase() + s.slice(1))(ACENTOS[k] || String(k).replace(/_/g, " "));
  const folha = (x) => x === null || x === "" ? "—" : typeof x === "boolean" ? (x ? "sim" : "não") : typeof x === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(x) ? dataHora(x) : String(x);
  const no = (x, n) => {
    if (x === null || typeof x !== "object") return h("span", {}, folha(x));
    const e = Array.isArray(x) ? x.map((y, k) => [k + 1, y]) : Object.entries(x);
    if (!e.length) return h("span", { class: "mudo" }, "(vazio)");
    if (n > 4) return h("span", { class: "mudo" }, "(…)");
    return h("ul", { class: "md-json" }, e.map(([k, y]) => h("li", {}, Array.isArray(x) && (y === null || typeof y !== "object") ? null : h("strong", {}, rot(k), ": "), no(y, n + 1))));
  };
  return h("div", { class: "md", id: "pn-texto" }, no(v, 0));
}
function leituraDom(caminho, texto, titulo) {
  if (/\.json$/i.test(caminho)) return jsonParaDom(texto);
  if (/\.md$/i.test(caminho)) return mdParaDom(texto, titulo);
  return h("div", { class: "md", id: "pn-texto" }, String(texto).split(/\n{2,}/).map((p) => h("p", { class: "md-txt" }, p.trim())));
}

function desenharVideos() {
  const v = T.dados.visao && T.dados.visao.videos, el = document.getElementById("pn-corpo");
  trocarSeMudou("videos", v, el, () => {
    if (!emBloco(v)) return el.replaceChildren(h("p", { class: "vazio-texto", id: "pn-videos-vazio" }, `Não consegui ler os vídeos: ${motivoCurto(v)}. Tente Atualizar agora.`));
    const l = v.em_andamento || [];
    const num = (n, t) => h("div", { class: "pn-num" }, h("span", { class: "pn-num-n" }, pad(n)), h("span", { class: "pn-num-t" }, t));
    el.replaceChildren(
      h("div", { class: "pn-numeros", id: "pn-videos-num" }, num(v.em_andamento_total ?? 0, "Em andamento"), num(v.total ?? 0, "Vídeos no total")),
      h("p", { class: "mini mudo" }, "Aqui você só acompanha. Para editar ou aprovar, use o Corte."),
      l.length ? h("ul", { class: "pn-videos", id: "pn-videos" }, l.map((x) => h("li", { class: "pn-video" }, h("b", { class: "pn-video-slug" }, x.slug), h("span", { class: "pn-etapa" }, x.status_texto))))
        : h("p", { class: "vazio-texto", id: "pn-videos-vazio" }, "Nenhum vídeo em andamento agora."));
  });
}

/* ---------- Agentes e Setores (a página de cada agente, com o editor, fica em corte_painel_agente.js) ---------- */
let agBusca = "", agSetor = "";
function montarAgentes() {
  const q = new URLSearchParams(location.search);
  agSetor = q.get("setor") || ""; agBusca = "";
}
function agentesDe(s, v) {
  const estados = {};
  if (emBloco(v && v.agentes_ativos)) (v.agentes_ativos.agentes || []).forEach((a) => { estados[a.id] = a.estado_texto || a.estado; });
  const out = [];
  for (const st of s.setores || []) for (const a of st.agentes || []) out.push({ ...a, setor: st.nome, setorId: st.id, ativoSetor: st.ativo, estado: estados[a.id] || "Parado" });
  for (const a of s.sem_setor || []) { const id = typeof a === "string" ? a : a.id; out.push({ id, nome: (a && a.nome) || id, setor: null, setorId: "", atualizado_em: a && a.atualizado_em, estado: estados[id] || "Parado" }); }
  return out;
}
function desenharAgentes() {
  const s = T.dados.setores, v = T.dados.visao, el = document.getElementById("pn-corpo");
  if (!el.querySelector("#pn-ag-barra")) {
    T.assin.ag = null;
    el.replaceChildren(h("div", { class: "pn-ferr", id: "pn-ag-barra" },
      h("input", { type: "search", id: "pn-ag-busca", placeholder: "Buscar agentes", "aria-label": "Buscar agente", value: agBusca, oninput: (e) => { agBusca = e.target.value.trim().toLowerCase(); T.assin.ag = null; desenharAgentes(); } }),
      h("select", { id: "pn-ag-setor", "aria-label": "Filtrar por setor", onchange: (e) => { agSetor = e.target.value; T.assin.ag = null; desenharAgentes(); } },
        h("option", { value: "" }, "Todos os setores"), (s.setores || []).map((x) => h("option", { value: x.id }, x.nome)), h("option", { value: "__sem" }, "Sem setor"))),
      h("p", { class: "mini mudo pn-ag-nota", id: "pn-ag-nota" }, "Clique em um agente para ver os dados dele e editar as instruções aqui mesmo."),
      h("div", { id: "pn-ag-lista" }));
    el.querySelector("#pn-ag-setor").value = agSetor;
  }
  const todos = agentesDe(s, v);
  const lista = todos.filter((a) => (!agBusca || `${a.nome} ${a.id}`.toLowerCase().includes(agBusca)) && (!agSetor || (agSetor === "__sem" ? !a.setorId : a.setorId === agSetor)));
  trocarSeMudou("ag", [lista, todos.length, (s.sem_setor || []).length], el, () => {
    const alvo = el.querySelector("#pn-ag-lista");
    const mapa = new Map();
    for (const a of lista) { const k = a.setor || "Sem setor"; if (!mapa.has(k)) mapa.set(k, []); mapa.get(k).push(a); }
    const grupos = [...mapa.entries()];
    const ativos = todos.filter((a) => a.estado === "Trabalhando").length;
    const semSetor = (s.sem_setor || []).length;
    alvo.replaceChildren(
      h("p", { class: "mini mudo", id: "pn-ag-conta" }, `${todos.length} agente${todos.length === 1 ? "" : "s"} · ${ativos} ativo${ativos === 1 ? "" : "s"} agora`),
      semSetor ? h("div", { class: "faixa velha", id: "pn-ag-aviso" }, `${semSetor} agente${semSetor > 1 ? "s" : ""} sem setor: não estão em ecossistema/setores.json.`) : null,
      !todos.length ? h("p", { class: "vazio-texto", id: "pn-ag-vazio" }, "Nenhum agente encontrado em .claude/agents.")
        : !lista.length ? h("p", { class: "vazio-texto", id: "pn-ag-vazio" }, "Nenhum agente combina com a busca.")
        : h("div", { class: "pn-ag-grupos", id: "pn-ag-tab" }, grupos.map(([nome, ags], i) => h("section", { class: "pn-ag-grupo", "aria-label": nome },
          h("h2", { class: "pn-ag-cab" }, h("span", { class: "pn-ag-n" }, pad(i + 1)), nome, h("span", { class: "pn-ag-qtd" }, String(ags.length))),
          h("ul", { class: "pn-ag-ul" }, ags.map((a) => h("li", { class: "pn-ag", "data-agente": a.id },
            h("a", { class: "pn-ag-link", href: `/painel/agentes/${a.id}`, "aria-label": `Abrir e editar ${a.nome}`, onclick: (e) => { e.preventDefault(); ir(e.currentTarget.getAttribute("href")); } },
              h("span", { class: "pn-ag-av", "aria-hidden": "true" }, (a.nome || a.id).charAt(0).toUpperCase()),
              h("span", { class: "pn-ag-txt" }, h("b", {}, a.nome), h("span", { class: "pn-ag-id" }, a.id)),
              h("span", { class: "pn-ag-est" + (a.estado === "Trabalhando" ? " on" : "") }, h("span", { class: "pn-pt", "aria-hidden": "true" }), a.estado === "Trabalhando" ? "Ativo" : a.estado === "Parado" ? "Parado" : a.estado)))))))));
  });
}
function desenharPaginaAgente() {
  if (!AG.dados) return;      // ainda abrindo: o carregamento do agente desenha a página
  atualizarEstadoAgente();
}
function desenharSetores() {
  const s = T.dados.setores, v = T.dados.visao, el = document.getElementById("pn-corpo");
  trocarSeMudou("setores", [s, v && v.sprint], el, () => {
    if (!(s.setores || []).length) return el.replaceChildren(h("p", { class: "vazio-texto", id: "pn-setores-vazio" }, "Nenhum setor cadastrado. Peça ao Luiz Henrique para criar ecossistema/setores.json."));
    const sp = v && emBloco(v.sprint) && v.sprint.nome ? `${v.sprint.nome} · ${v.sprint.estado || ""}` : null;
    el.replaceChildren(
      h("p", { class: "mini mudo" }, "Clique no nome de um agente para ver os dados dele e editar as instruções aqui mesmo."),
      h("div", { class: "pn-setores" }, s.setores.map((st, i) => {
        const ativos = (st.agentes || []).filter((a) => a.estado === "trabalhando").length;
        const url = `/painel/agentes?setor=${encodeURIComponent(st.id)}`;
        return h("section", { class: "pn-setor" + (st.ativo ? "" : " inativo"), "data-setor": st.id, "aria-label": st.nome },
          h("span", { class: "pn-set-n", "aria-hidden": "true" }, pad(i + 1)), h("div", { class: "linha-flex" }, h("h2", {}, st.nome), h("span", { class: "espaco" }), h("span", { class: "selo " + (st.ativo ? "aprovada" : "") }, st.ativo ? "Ativo" : "Inativo")),
          h("p", { class: "mini mudo" }, `${st.agentes_total} agente${st.agentes_total === 1 ? "" : "s"}${ativos ? ` · ${ativos} ativos agora` : ""}`),
          !st.ativo ? h("p", { class: "mini" }, "Inativo: sem trabalho em andamento neste setor agora.") : null,
          st.id === "programacao" && sp ? h("p", { class: "mini" }, `Sprint: ${sp}`) : null,
          (st.agentes_sem_arquivo || []).length ? h("p", { class: "mini" }, `${st.agentes_sem_arquivo.length} agente(s) sem arquivo em .claude/agents.`) : null,
          h("p", { class: "pn-nomes" }, (st.agentes || []).slice(0, 8).map((a, i) => [i ? ", " : "", h("a", { class: "pn-nome-ag", href: `/painel/agentes/${a.id}`, "data-agente": a.id, onclick: (e) => { e.preventDefault(); ir(e.currentTarget.getAttribute("href")); } }, a.nome)]), (st.agentes || []).length > 8 ? ` +${st.agentes.length - 8}` : ""),
          h("a", { class: "btn mini", href: url, onclick: (e) => { e.preventDefault(); ir(url); } }, "Ver agentes do setor"), " ",
          h("a", { class: "btn mini", href: "/painel/documentos", onclick: (e) => { e.preventDefault(); ir(`/painel/documentos${["programacao", "inteligencia"].includes(st.id) ? `?area=${st.id}` : st.id === "pessoal" ? "?area=produtividade" : ""}`); } }, "Ver documentos"));
      })),
      (s.sem_setor || []).length ? h("div", { class: "faixa velha", id: "pn-sem-setor" }, `${s.sem_setor.length} agente${s.sem_setor.length === 1 ? "" : "s"} sem setor: não estão em ecossistema/setores.json.`) : null);
  });
}

/* ---------- Menu lateral (só nesta página; as telas do Corte seguem com o menu de cima) ---------- */
Corte.desenharNav = function () {
  Vivo.iniciar();
  const c = location.pathname.replace(/\/+$/, ""), atual = c.startsWith("/painel") ? abaDe(c) : "";
  const item = ([id, nome, url]) => h("a", { class: "pn-aba nav-item" + (id === atual ? " ativa ativo" : ""), href: url, id: `pn-aba-${id}`, "aria-current": id === atual ? "page" : null,
    onclick: (e) => { e.preventDefault(); PainelTela.ir(url); },
    onkeydown: (e) => {
      const i = ABAS.findIndex((a) => a[0] === id), d = ["ArrowRight", "ArrowDown"].includes(e.key) ? 1 : ["ArrowLeft", "ArrowUp"].includes(e.key) ? -1 : 0;
      if (d) { e.preventDefault(); const p = ABAS[(i + d + ABAS.length) % ABAS.length]; PainelTela.ir(p[2]); document.getElementById(`pn-aba-${p[0]}`).focus(); }
    } }, nome);
  const claro = Tema.efetivo() === "claro";
  trocar(document.getElementById("nav"),
    h("a", { class: "nav-marca", href: "/painel", onclick: (e) => { e.preventDefault(); PainelTela.ir("/painel"); } },
      logoSvg(), h("span", { class: "nav-marca-nome" }, "Ecossistema do Guilherme")),
    h("span", { class: "pn-espaco-pessoal" }, "ESPAÇO PESSOAL"),
    h("div", { class: "pn-menu", role: "navigation", "aria-label": "Seções do painel" }, ABAS.filter((a) => a[0] !== "videos").map(item), h("hr", { class: "pn-sep" }), item(ABAS.find((a) => a[0] === "videos"))),
    h("a", { class: "pn-corte", id: "nav-corte", href: "/" }, "Abrir o Corte ↗"),
    h("span", { class: "espaco" }),
    h("div", { class: "pn-pe-nav" }, h("span", { class: "pn-avatar", "aria-hidden": "true" }, "GB"), h("span", { class: "pn-usuario" }, "Guilherme Borges"),
      h("button", { type: "button", class: "pn-tema", id: "pn-tema", "aria-pressed": String(claro), "aria-label": claro ? "Tema claro ativo. Mudar para o escuro" : "Tema escuro ativo. Mudar para o claro", title: claro ? "Mudar para o tema escuro" : "Mudar para o tema claro", onclick: () => Tema.alternar() }, claro ? "☾" : "☀")));
};
function logoSvg() {
  const NS = "http://www.w3.org/2000/svg", s = document.createElementNS(NS, "svg"), p = document.createElementNS(NS, "path");
  s.setAttribute("class", "nav-logo"); s.setAttribute("viewBox", "0 0 32 32"); s.setAttribute("aria-hidden", "true"); s.setAttribute("focusable", "false");
  p.setAttribute("d", "M4 4h20l4 4v8h-8v-4h-8v8h12v12H8l-4-4z"); p.setAttribute("fill", "currentColor");
  s.append(p);
  return s;
}

/* ---------- Início ---------- */
Corte.desenharNav();
PainelTela.montar();

