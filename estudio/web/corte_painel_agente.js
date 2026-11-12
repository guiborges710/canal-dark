"use strict";
/* Página do agente dentro do painel (/painel/agentes/<id>): descrição, modelo e ferramentas como campos de formulário, e o texto das
   instruções num editor visual (Toast UI Editor, modo WYSIWYG, vendorizado em /web/vendor): o Guilherme vê títulos, listas e tabelas
   prontos e edita direto, sem ver markdown. Salva pela API que já existe (POST /api/agentes/<id>/salvar). Todo texto vindo de arquivo
   entra por textContent (função h) ou pelo editor, que higieniza o que renderiza. Só no computador (o servidor já responde 403 pela rede). */

const VENDOR_EDITOR = "/web/vendor/toastui-editor-3.2.2/";
const ID_AGENTE = /^\/painel\/agentes\/([a-z0-9]+(?:-[a-z0-9]+)*)\/?$/;
const agenteDe = (caminho) => { const m = caminho.match(ID_AGENTE); return m ? m[1] : null; };

/* Estado da página aberta (um agente por vez). */
const AG = { id: null, seq: 0, dados: null, ed: null, base: "", original: "", campos: null, status: "limpo", salvoEm: null, conflito: null, erro: null, salvando: false, timer: null, obs: null };

const agenteSujo = () => !!(AG.id && AG.dados && (AG.status === "sujo" || AG.status === "erro" || AG.status === "conflito" || mudouAlgo()));
function mudouAlgo() {
  if (!AG.dados || !AG.campos) return false;
  const c = lerCampos();
  return c.descricao !== AG.campos.descricao || c.modelo !== AG.campos.modelo || c.ferramentas.join("|") !== AG.campos.ferramentas.join("|") || corpoMudou();
}
const corpoMudou = () => !!AG.ed && AG.ed.getMarkdown() !== AG.base;

function confirmarSaida() {
  if (!agenteSujo()) return true;
  return confirm("Você tem alterações não salvas neste agente. Sair mesmo assim e perder essas alterações?");
}
window.addEventListener("beforeunload", (e) => { if (agenteSujo()) { e.preventDefault(); e.returnValue = ""; } });

/* ---------- API (JSON; a página principal só tinha GET) ---------- */
async function apiJson(metodo, url, corpo) {
  const ctl = new AbortController();
  const t = setTimeout(() => ctl.abort(), 20000);
  try {
    const r = await fetch(url, { method: metodo, cache: "no-store", signal: ctl.signal, headers: corpo ? { "Content-Type": "application/json" } : undefined, body: corpo ? JSON.stringify(corpo) : undefined });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error((d.erro || ["Falha na requisição."]).join(" ")); e.status = r.status; throw e; }
    return d;
  } catch (e) {
    if (e.status) throw e;
    const x = new Error("Não consegui falar com o servidor do Ecossistema. Seu texto continua aqui; tente salvar de novo em instantes.");
    x.rede = true;
    throw x;
  } finally { clearTimeout(t); }
}

/* ---------- Carregar o editor sob demanda ---------- */
let _editorPronto = null;
function carregarEditor() {
  if (window.toastui && window.toastui.Editor) return Promise.resolve();
  if (_editorPronto) return _editorPronto;
  const css = (href, id) => new Promise((ok, falha) => { const l = h("link", { rel: "stylesheet", href, id }); l.onload = ok; l.onerror = () => falha(new Error(`Não consegui carregar ${href}`)); document.head.append(l); });
  const js = (src) => new Promise((ok, falha) => { const s = h("script", { src }); s.onload = ok; s.onerror = () => falha(new Error(`Não consegui carregar ${src}`)); document.head.append(s); });
  _editorPronto = Promise.all([css(VENDOR_EDITOR + "toastui-editor.css"), css(VENDOR_EDITOR + "toastui-editor-dark.css"), js(VENDOR_EDITOR + "toastui-editor-bundle.js")]).catch((e) => { _editorPronto = null; throw e; });
  return _editorPronto;
}

/* ---------- Montagem da página ---------- */
function montarAgente() {
  AG.seq++;
  desmontarEditor();
  Object.assign(AG, { id: T.agenteId, dados: null, base: "", original: "", campos: null, status: "limpo", salvoEm: null, conflito: null, erro: null, salvando: false });
  carregarAgente();
}
function desmontarEditor() {
  if (AG.obs) { AG.obs.disconnect(); AG.obs = null; }
  if (AG.ed) { try { AG.ed.destroy(); } catch { /* já destruído */ } AG.ed = null; }
}

async function carregarAgente() {
  const meu = AG.seq, id = AG.id;
  const corpo = document.getElementById("pn-corpo");
  if (!corpo) return;
  corpo.replaceChildren(h("div", { class: "pn-carregando", id: "pn-carregando" }, h("div", { class: "pn-esq" }), h("div", { class: "pn-esq" }), h("p", { class: "mudo" }, "Abrindo o agente...")));
  try {
    const [dados, painel] = await Promise.all([apiJson("GET", `/api/agentes/${encodeURIComponent(id)}`), buscarAba("agentes"), carregarEditor()]);
    if (meu !== AG.seq) return;
    Object.assign(T.dados, painel);   // setor e estado vêm do painel
    AG.dados = dados;
    desenharAgente(dados);
  } catch (e) {
    if (meu !== AG.seq) return;
    const nao = e.status === 404;
    corpo.replaceChildren(h("div", { class: "faixa falha", id: nao ? "pn-ag-naoachou" : "pn-ag-erro-abrir", role: "alert" },
      h("b", {}, nao ? "Agente não encontrado." : "Não consegui abrir este agente."),
      h("p", {}, nao ? `Não existe .claude/agents/${id}.md (nem desativado). Próximo passo: voltar à lista e escolher outro agente.` : e.message),
      nao ? null : h("button", { class: "btn mini", id: "pn-ag-de-novo", type: "button", onclick: () => carregarAgente() }, "Tentar de novo"), " ",
      h("a", { class: "btn mini", href: "/painel/agentes", onclick: (ev) => { ev.preventDefault(); ir("/painel/agentes"); } }, "Voltar à lista")));
  }
}

function infoSetor(id) {
  const s = T.dados.setores;
  if (!s) return null;
  for (const st of s.setores || []) for (const a of st.agentes || []) if (a.id === id) return { nome: st.nome, id: st.id, ativoSetor: st.ativo, nomeAgente: a.nome };
  return { nome: null, id: "", ativoSetor: false, nomeAgente: ((s.sem_setor || []).find((a) => a.id === id) || {}).nome };
}
function estadoDoAgente(dados) {
  if (!dados.ativo) return { texto: "Desativado", classe: "" };
  const v = T.dados.visao, achado = emBloco(v && v.agentes_ativos) ? (v.agentes_ativos.agentes || []).find((a) => a.id === dados.id) : null;
  if (achado) return { texto: "Trabalhando agora", classe: " on" };
  return { texto: "Parado", classe: "" };
}
const ORIGENS = { disco: "arquivo", existente: "versão inicial", corte: "salva pelo painel ou pelo Corte" };
const origemTexto = (o) => ORIGENS[o] || o || "";

const lerCampos = () => ({
  descricao: (document.getElementById("pn-ag-descricao")?.value ?? "").replace(/\s+/g, " ").trim(),
  modelo: document.getElementById("pn-ag-modelo")?.value ?? "",
  ferramentas: [...document.querySelectorAll("#pn-ag-ferramentas input:checked")].map((i) => i.value),
});

function desenharAgente(d) {
  const corpo = document.getElementById("pn-corpo");
  const set = infoSetor(d.id), est = estadoDoAgente(d);
  const nome = (set && set.nomeAgente) || d.craque || d.id;
  AG.campos = { descricao: (d.descricao || "").replace(/\s+/g, " ").trim(), modelo: d.modelo || "", ferramentas: [...d.ferramentas] };
  AG.original = (d.instrucoes || "").replace(/\r\n/g, "\n");
  const ops = d.opcoes || { ferramentas: [], modelos: [] };
  const ferrTodas = [...ops.ferramentas, ...d.ferramentas.filter((f) => !ops.ferramentas.includes(f))];
  const modelos = [...ops.modelos, ...(d.modelo && !ops.modelos.includes(d.modelo) ? [d.modelo] : [])];
  const titulo = document.querySelector(".pn-titulo");
  if (titulo) titulo.replaceChildren(nome, h("span", { class: "pn-ponto" }, "."));
  document.title = `${nome} · Painel · Ecossistema do Guilherme`;

  corpo.replaceChildren(
    h("a", { class: "pn-ag-voltar", id: "pn-ag-voltar", href: set && set.id ? `/painel/agentes?setor=${encodeURIComponent(set.id)}` : "/painel/agentes", onclick: (e) => { e.preventDefault(); ir(e.currentTarget.getAttribute("href")); } }, "← ", set && set.nome ? `Agentes de ${set.nome}` : "Todos os agentes"),
    h("section", { class: "pn-ag-cartao", id: "pn-ag-cabeca", "aria-label": "Identificação do agente" },
      h("span", { class: "pn-ag-av grande", "aria-hidden": "true" }, nome.charAt(0).toUpperCase()),
      h("div", { class: "pn-ag-ident" },
        h("h2", { id: "pn-ag-nome" }, nome),
        h("p", { class: "pn-ag-id", id: "pn-ag-id" }, d.id),
        h("p", { class: "pn-ag-chips" },
          h("span", { class: "pn-chip", id: "pn-ag-setor-chip" }, "Setor: ", set && set.nome ? set.nome : "sem setor"),
          h("span", { class: "pn-chip pn-ag-est" + est.classe, id: "pn-ag-estado" }, h("span", { class: "pn-pt", "aria-hidden": "true" }), est.texto),
          h("span", { class: "pn-chip mudo", id: "pn-ag-versao" }, `Versão ${d.versao}`)),
        h("p", { class: "mini mudo" }, "Arquivo: ", h("code", {}, d.arquivo)),
        !d.ativo ? h("p", { class: "mini", id: "pn-ag-desativado" }, "Este agente está desativado: o arquivo fica em .claude/agents_desativados e o Claude Code não o chama. Você pode editar o texto mesmo assim.") : null)),
    h("div", { id: "pn-ag-faixa" }),
    h("section", { class: "pn-ag-cartao col", "aria-label": "Sobre o agente" },
      h("label", { class: "pn-campo" }, h("span", { class: "pn-campo-nome" }, "Descrição"),
        h("textarea", { id: "pn-ag-descricao", rows: 3, value: AG.campos.descricao, oninput: () => marcarMudanca() }),
        h("span", { class: "mini mudo" }, "É por ela que o Claude Code decide quando chamar este agente. Escreva em uma ou duas frases.")),
      h("label", { class: "pn-campo curto" }, h("span", { class: "pn-campo-nome" }, "Modelo"),
        h("select", { id: "pn-ag-modelo", onchange: () => marcarMudanca() }, h("option", { value: "" }, "Padrão do Claude Code"), modelos.map((m) => h("option", { value: m }, m))),
        h("span", { class: "mini mudo" }, "Qual modelo de IA faz o trabalho deste agente.")),
      h("fieldset", { class: "pn-campo", id: "pn-ag-ferramentas" }, h("legend", { class: "pn-campo-nome" }, "Ferramentas permitidas"),
        h("div", { class: "pn-ferr-lista" }, ferrTodas.map((f, i) => h("label", { class: "pn-ferr-item" }, h("input", { type: "checkbox", value: f, checked: d.ferramentas.includes(f), id: `pn-ag-f-${i}`, onchange: () => marcarMudanca() }), h("span", {}, f)))),
        h("span", { class: "mini mudo" }, "O que o agente pode fazer: ler, escrever e editar arquivos, buscar na web, chamar outros agentes. Comandos novos de terminal não entram por aqui."))),
    h("section", { class: "pn-ag-cartao col", "aria-label": "Instruções do agente" },
      h("h3", { class: "pn-ag-sub" }, "Instruções"),
      h("p", { class: "mini mudo" }, "O texto que o agente lê antes de trabalhar. Edite direto, como em um documento: títulos, listas, negrito e tabelas aparecem prontos."),
      h("div", { id: "pn-ag-editor", class: "pn-editor" })),
    h("div", { class: "pn-ag-barra", id: "pn-ag-rodape", role: "region", "aria-label": "Salvar" },
      h("span", { id: "pn-ag-status", class: "pn-ag-status", role: "status", "aria-live": "polite" }),
      h("span", { class: "espaco" }),
      h("button", { class: "btn mini", id: "pn-ag-descartar", type: "button", onclick: () => descartar() }, "Descartar alterações"),
      h("button", { class: "btn principal", id: "pn-ag-salvar", type: "button", onclick: () => salvar() }, "Salvar")),
    h("details", { class: "pn-ag-cartao col", id: "pn-ag-versoes" }, h("summary", {}, "Versões anteriores"), h("div", { id: "pn-ag-versoes-lista" })));

  document.getElementById("pn-ag-modelo").value = AG.campos.modelo;
  criarEditor();
  desenharVersoes();
  atualizarStatus();
  document.getElementById("pn-ag-descricao").addEventListener("keydown", (e) => { if (e.key === "Enter") e.preventDefault(); });
}

function criarEditor() {
  const el = document.getElementById("pn-ag-editor");
  const claro = Tema.efetivo() === "claro";
  AG.ed = new toastui.Editor({
    el, initialEditType: "wysiwyg", hideModeSwitch: true, usageStatistics: false, language: "pt-BR", height: "auto", minHeight: "420px",
    theme: claro ? "light" : "dark", initialValue: MesclaAgente.paraEditor(AG.original), autofocus: false,
    toolbarItems: [["heading", "bold", "italic", "strike"], ["hr", "quote"], ["ul", "ol", "task"], ["table", "link"], ["code", "codeblock"]],
  });
  AG.base = AG.ed.getMarkdown();     // o que o editor devolve sem o Guilherme mexer: a referência para saber o que mudou
  let adiado = null;
  AG.ed.on("change", () => { clearTimeout(adiado); adiado = setTimeout(marcarMudanca, 120); });
  // tema claro/escuro do painel vale também para o editor
  const aplicar = () => { const ui = el.querySelector(".toastui-editor-defaultUI"); if (ui) ui.classList.toggle("toastui-editor-dark", Tema.efetivo() !== "claro"); };
  aplicar();
  AG.obs = new MutationObserver(aplicar);
  AG.obs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-tema"] });
}

/* ---------- Estado de edição ---------- */
function marcarMudanca() {
  if (!AG.dados || AG.salvando) return;
  if (AG.status === "conflito") return atualizarStatus();
  AG.status = mudouAlgo() ? "sujo" : (AG.salvoEm ? "salvo" : "limpo");
  atualizarStatus();
}

function atualizarStatus() {
  const st = document.getElementById("pn-ag-status"), bs = document.getElementById("pn-ag-salvar"), bd = document.getElementById("pn-ag-descartar");
  if (!st) return;
  const sujo = AG.status === "sujo" || AG.status === "erro" || AG.status === "conflito";
  const texto = {
    limpo: "Sem alterações.", sujo: "Alterações não salvas.", salvando: "Salvando...",
    salvo: AG.salvoEm ? `Salvo às ${hhmm(AG.salvoEm)}.` : "Salvo.", erro: `Não salvou: ${AG.erro || "erro desconhecido"}`, conflito: "Conflito: o arquivo mudou desde que você abriu. Veja o aviso no topo da página.",
  }[AG.status];
  st.textContent = texto;
  st.dataset.estado = AG.status;
  st.className = `pn-ag-status st-${AG.status}`;   // prefixo: ".conflito" e ".erro" já existem nas telas do Corte
  bs.disabled = !(sujo && AG.status !== "conflito") || AG.salvando;
  bs.textContent = AG.salvando ? "Salvando..." : AG.status === "erro" ? "Tentar salvar de novo" : "Salvar";
  bd.disabled = !sujo || AG.salvando;
  const faixa = document.getElementById("pn-ag-faixa");
  if (faixa && AG.status !== "conflito" && faixa.querySelector("#pn-ag-conflito")) faixa.replaceChildren();
}

function descartar() {
  if (!agenteSujo()) return;
  if (!confirm("Descartar o que você editou e voltar ao texto que está no arquivo?")) return;
  carregarAgente();
}

/* ---------- Salvar ---------- */
function corpoParaSalvar() {
  const c = lerCampos();
  return { descricao: c.descricao, modelo: c.modelo, ferramentas: c.ferramentas, instrucoes: MesclaAgente.mesclar(AG.original, AG.base, AG.ed.getMarkdown()) };
}

async function salvar(sobrescrever) {
  if (AG.salvando || !AG.ed) return;
  const meu = AG.seq;
  const c = lerCampos();
  if (c.descricao.length < 5) { AG.status = "erro"; AG.erro = "escreva uma descrição (é por ela que o Claude Code decide quando usar o agente)."; atualizarStatus(); document.getElementById("pn-ag-descricao").focus(); return; }
  const md = AG.ed.getMarkdown();
  const dados = { ...corpoParaSalvar(), versao_vista: AG.dados.versao };
  AG.salvando = true; AG.status = "salvando"; AG.erro = null; atualizarStatus();
  try {
    if (sobrescrever) dados.versao_vista = (await apiJson("GET", `/api/agentes/${encodeURIComponent(AG.id)}`)).versao;
    const r = await apiJson("POST", `/api/agentes/${encodeURIComponent(AG.id)}/salvar`, dados);
    if (meu !== AG.seq) return;
    AG.dados = r;
    AG.original = (r.instrucoes || "").replace(/\r\n/g, "\n");
    AG.base = md;
    AG.campos = { descricao: (r.descricao || "").replace(/\s+/g, " ").trim(), modelo: r.modelo || "", ferramentas: [...r.ferramentas] };
    AG.salvoEm = new Date(); AG.conflito = null; AG.salvando = false;
    AG.status = mudouAlgo() ? "sujo" : "salvo";
    const v = document.getElementById("pn-ag-versao"); if (v) v.textContent = `Versão ${r.versao}`;
    desenharVersoes();
    atualizarStatus();
  } catch (e) {
    if (meu !== AG.seq) return;
    AG.salvando = false;
    if (e.status === 409 && /mudou por fora/.test(e.message)) { AG.status = "conflito"; AG.conflito = e.message; atualizarStatus(); desenharConflito(); }
    else { AG.status = "erro"; AG.erro = e.message; atualizarStatus(); }
  }
}

function desenharConflito() {
  const f = document.getElementById("pn-ag-faixa");
  if (!f) return;
  f.replaceChildren(h("div", { class: "faixa falha", id: "pn-ag-conflito", role: "alert" },
    h("b", {}, "O arquivo mudou desde que você abriu: recarregar ou sobrescrever?"),
    h("p", {}, "Alguém (ou o terminal) alterou este agente enquanto a página estava aberta. Recarregar mostra a versão nova e descarta o que você editou aqui. Sobrescrever grava a sua versão por cima da nova; a versão nova continua guardada em Versões anteriores."),
    h("button", { class: "btn mini", id: "pn-ag-recarregar", type: "button", onclick: () => { AG.status = "limpo"; carregarAgente(); } }, "Recarregar (perder o que editei)"), " ",
    h("button", { class: "btn mini principal", id: "pn-ag-sobrescrever", type: "button", onclick: () => { AG.status = "sujo"; salvar(true); } }, "Sobrescrever com a minha versão")));
  const faixa = f.querySelector("#pn-ag-conflito");
  faixa.tabIndex = -1;
  faixa.scrollIntoView({ block: "center" });   // o botão Salvar fica lá embaixo: o aviso precisa vir até o Guilherme
  faixa.focus({ preventScroll: true });
}

/* ---------- Versões anteriores (a API já guarda e restaura) ---------- */
function desenharVersoes() {
  const alvo = document.getElementById("pn-ag-versoes-lista");
  if (!alvo) return;
  const vs = (AG.dados && AG.dados.versoes) || [];
  alvo.replaceChildren(vs.length <= 1
    ? h("p", { class: "mini mudo", id: "pn-ag-versoes-vazio" }, "Ainda não há versões anteriores: este agente só tem a versão atual. Cada vez que você salva, a versão de antes fica guardada aqui.")
    : h("ul", { class: "pn-ag-versoes" }, vs.map((v) => h("li", { "data-versao": v.numero },
      h("b", {}, `Versão ${v.numero}`), h("span", { class: "mini mudo" }, ` · ${dataHora(v.criada_em)} · ${origemTexto(v.origem)}`),
      v.numero === AG.dados.versao ? h("span", { class: "pn-chip" }, "atual") : h("button", { class: "btn mini", type: "button", onclick: () => restaurarVersao(v.numero) }, "Restaurar esta versão")))));
}

async function restaurarVersao(numero) {
  const aviso_ = agenteSujo() ? " As alterações não salvas desta página serão perdidas." : "";
  if (!confirm(`Restaurar a versão ${numero}? Ela volta como a versão mais recente e nada do histórico é apagado.${aviso_}`)) return;
  try {
    const r = await apiJson("POST", `/api/agentes/${encodeURIComponent(AG.id)}/restaurar`, { numero });
    aviso(`Versão ${numero} restaurada.`);
    AG.seq++; desmontarEditor();
    AG.dados = r; AG.status = "limpo"; AG.salvoEm = null; AG.conflito = null;
    desenharAgente(r);
  } catch (e) { aviso(`Não consegui restaurar: ${e.message}`, true); }
}

/* Redesenho periódico da aba: só o estado (Trabalhando/Parado); nunca mexe no editor. */
function atualizarEstadoAgente() {
  if (!AG.dados) return;
  const e = document.getElementById("pn-ag-estado");
  if (!e) return;
  const est = estadoDoAgente(AG.dados);
  e.className = "pn-chip pn-ag-est" + est.classe;
  e.replaceChildren(h("span", { class: "pn-pt", "aria-hidden": "true" }), est.texto);
}

/* Para os testes: o texto que seria gravado agora, sem gravar. */
window.PainelAgente = { corpoParaSalvar: () => (AG.ed ? corpoParaSalvar() : null), estado: () => AG.status, pronto: () => !!AG.ed };
