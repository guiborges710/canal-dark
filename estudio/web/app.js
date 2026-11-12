"use strict";
/* Corte: Projetos e Revisão ficam aqui; Estúdio, Editor, Agentes e Fluxos, nos corte_*.js. Sem framework e sem build: o servidor só entrega estes arquivos.
   Todo texto vindo de arquivo entra por textContent (função h), nunca como HTML. */

const app = document.getElementById("app");
const S = { tela: null, slug: null, etapa: null, est: null, cont: null, versao: null, aba: {}, alvo: null, categoria: null, assinaturas: {}, timer: null, filtro: "todos", ouvirTudo: false, trecho: null };

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

async function api(metodo, url, corpo) {
  const r = await fetch(url, { method: metodo, headers: corpo ? { "Content-Type": "application/json" } : {}, body: corpo ? JSON.stringify(corpo) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) { const e = new Error((d.erro || ["Falha na requisição."]).join(" ")); e.motivos = d.erro; throw e; }
  return d;
}

function aviso(texto, erro) {
  const a = h("div", { class: "aviso" + (erro ? " erro" : "") }, texto);
  document.getElementById("avisos").append(a);
  setTimeout(() => a.remove(), erro ? 7000 : 3500);
}

/* Trava o botão até a resposta voltar: um clique duplo vira um clique só, e o servidor também recusa duplicata. */
function acao(fn) {
  return async (ev) => {
    const b = ev.currentTarget;
    if (b && b.dataset.ocupado) return;
    if (b) { b.dataset.ocupado = "1"; b.disabled = true; }
    try { await fn(ev); } catch (e) { aviso(e.message, true); }
    if (b) { delete b.dataset.ocupado; b.disabled = false; }
    atualizar();
  };
}

const tempo = (s) => { s = Math.max(0, Number(s) || 0); const m = Math.floor(s / 60); return `${String(m).padStart(2, "0")}:${(s - m * 60).toFixed(1).padStart(4, "0")}`; };
const tempoCurto = (s) => { s = Math.round(Number(s) || 0); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };

function quando(iso) {
  if (!iso) return "–";
  const d = new Date(iso), agora = new Date(), min = Math.round((agora - d) / 60000);
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  if (d.toDateString() === agora.toDateString()) return `hoje, ${d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
  const ontem = new Date(agora); ontem.setDate(agora.getDate() - 1);
  if (d.toDateString() === ontem.toDateString()) return `ontem, ${d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

/* Só redesenha quando os dados mudaram. É isso que deixa o polling não atrapalhar o player nem o texto digitado. */
function seMudou(chave, valor, fn) {
  const a = JSON.stringify(valor);
  if (S.assinaturas[chave] === a) return;
  S.assinaturas[chave] = a;
  fn();
}

/* ---------- Rotas ---------- */
function ir(url) { history.pushState({}, "", url); rotear(); }
addEventListener("popstate", rotear);

function rotear() {
  const p = location.pathname.match(/^\/producao\/([\w.-]+)/);
  S.assinaturas = {};
  Corte.desenharNav();
  if (Corte.rotear(location.pathname)) { S.tela = "corte"; S.slug = null; atualizar(); return; }
  if (p) {
    const q = new URLSearchParams(location.search);
    const mudou = S.slug !== p[1];
    S.tela = "revisao"; S.slug = p[1]; S.etapa = q.get("etapa");
    S.versao = q.get("versao") ? Number(q.get("versao")) : null;
    if (mudou) { S.est = null; S.cont = null; S.alvo = null; S.categoria = null; }
    montarRevisao();
  } else {
    S.tela = "producoes"; S.slug = null; S.est = null;
    montarProducoes();
  }
  atualizar();
}

function agendar() {
  clearTimeout(S.timer);
  S.timer = setTimeout(atualizar, S.tela === "producoes" ? 4000 : 2000);
}

let buscando = false;
async function atualizar() {
  if (buscando) return;
  buscando = true;
  try {
    if (document.hidden) return;
    if (S.tela === "corte") await Corte.atualizar();
    else if (S.tela === "revisao") await atualizarRevisao();
    else await atualizarProducoes();
  } catch (e) {
    if (S.tela === "producoes" || !S.est) mostrarErroGeral(e.message);
  } finally {
    buscando = false;
    agendar();
  }
}
document.addEventListener("visibilitychange", () => { if (!document.hidden) atualizar(); });

function mostrarErroGeral(texto) {
  const alvo = document.getElementById("erro-geral");
  if (alvo) alvo.replaceChildren(h("div", { class: "alerta erro" }, texto));
}

/* ---------- Tela: Produções ---------- */
function montarProducoes() {
  document.title = "Projetos · Corte";
  app.replaceChildren(h("div", { class: "pagina" },
    h("div", { class: "topo-pagina" }, h("h1", { class: "marca" }, "Projetos"), h("span", { class: "espaco" }),
      h("button", { class: "btn principal", id: "novo", onclick: () => Corte.abrirNovo() }, "＋ Novo projeto")),
    h("div", { id: "erro-geral" }), h("div", { id: "integracoes" }), h("div", { id: "lista" })));
}

function linhaFila(p) {
  return (p.fila || []).length ? h("span", { class: "selo executando" }, "Em execução") : null;
}

function cartaoRevisao(p) {
  const url = `/producao/${p.slug}?etapa=${p.proxima.etapa}`;
  return h("a", { class: "cartao-revisao", href: url, onclick: (e) => { e.preventDefault(); ir(url); } },
    h("div", { style: "flex:1;min-width:0" }, h("div", { class: "t" }, p.titulo), h("div", { class: "mudo pequeno" }, `${p.proxima.texto} · atualizado ${quando(p.atualizado_em)}`)),
    linhaFila(p), Corte.linkEstudio(p.slug), h("span", { class: "seta" }, "Revisar →"));
}

async function atualizarProducoes() {
  const d = await api("GET", "/api/producoes");
  if (S.tela !== "producoes") return;
  mostrarErroGeral("") ;
  const eg = document.getElementById("erro-geral"); if (eg) eg.replaceChildren();
  seMudou("integracoes", d.integracoes, () => {
    const faltam = Object.values(d.integracoes).filter((i) => !i.ok);
    document.getElementById("integracoes").replaceChildren(...faltam.map((i) => h("div", { class: "alerta" }, h("b", {}, "Indisponível: "), i.detalhe)));
  });
  seMudou("lista", d.grupos, () => desenharLista(d.grupos));
}

function desenharLista(g) {
  const n = g.aguardando.length;
  const titulo = n === 0 ? "Nenhum vídeo aguardando sua revisão" : n === 1 ? "1 vídeo aguardando sua revisão" : `${n} vídeos aguardando sua revisão`;
  const destaque = h("section", { class: "destaque" + (n ? "" : " vazio") }, h("h1", {}, titulo),
    n ? g.aguardando.map(cartaoRevisao) : h("p", { class: "mudo" }, g.andamento.length ? "O que está em andamento segue abaixo." : "Comece um vídeo novo pelo botão acima."));
  const tabela = g.andamento.length ? h("table", { class: "lista" },
    h("thead", {}, h("tr", {}, ["Vídeo", "Etapa atual", "Atualizado", "Próxima ação", ""].map((t) => h("th", {}, t)))),
    h("tbody", {}, g.andamento.map((p) => h("tr", { onclick: () => ir(`/producao/${p.slug}`) },
      h("td", {}, h("a", { class: "titulo", href: `/producao/${p.slug}`, style: "color:inherit", onclick: (e) => { e.preventDefault(); ir(`/producao/${p.slug}`); } }, p.titulo)),
      h("td", {}, p.etapa_nome, " ", linhaFila(p)),
      h("td", { class: "mudo" }, quando(p.atualizado_em)),
      h("td", {}, p.proxima.texto),
      h("td", {}, Corte.linkEstudio(p.slug)))))) : h("div", { class: "vazio-texto" }, "Nada em andamento agora.");
  const arquivadas = h("details", { class: "dobra secao", open: S.arquivosAberto, ontoggle: (e) => { S.arquivosAberto = e.target.open; } },
    h("summary", {}, `Publicados e arquivados (${g.arquivadas.length})`),
    g.arquivadas.length ? h("table", { class: "lista", style: "margin-top:8px" },
      h("tbody", {}, g.arquivadas.map((p) => h("tr", { onclick: () => ir(`/producao/${p.slug}`) },
        h("td", { class: "titulo" }, p.titulo), h("td", {}, p.publicado ? h("span", { class: "selo concluida" }, "Enviado ao YouTube") : h("span", { class: "selo" }, "Arquivado")),
        h("td", { class: "mudo" }, quando(p.atualizado_em)), h("td", {}, Corte.linkEstudio(p.slug)))))) : null);
  document.getElementById("lista").replaceChildren(destaque, h("div", { class: "secao" }, h("div", { class: "cabeca" }, h("h2", {}, "Em andamento")), tabela), arquivadas);
}

/* ---------- Tela: Revisão ---------- */
function montarRevisao() {
  app.replaceChildren(h("div", { class: "revisao" },  // estudio: tela de revisão por etapa
    h("header", { class: "barra", id: "barra" }, h("span", { class: "mudo" }, "Carregando…")),
    h("div", { class: "colunas" },
      h("nav", { class: "trilho", id: "trilho", "aria-label": "Etapas" }),
      h("main", { class: "centro" }, h("div", { class: "centro-cabeca", id: "c-cabeca" }), h("div", { class: "centro-corpo" }, h("div", { id: "c-faixas" }), h("div", { id: "c-corpo" }))),
      h("aside", { class: "lado" }, h("section", { id: "l-decisao" }), h("section", { id: "l-feedback" }), h("section", { id: "l-lista" }), h("section", { id: "l-tecnico" }))),
    // No celular a decisão fica depois do material, que pode ser longo: este botão leva até ela. No computador não aparece.
    h("button", { class: "btn principal so-celular ir-decisao", id: "ir-decisao", onclick: () => document.getElementById("l-decisao").scrollIntoView({ behavior: "smooth", block: "start" }) }, "Decisão ↓")));
}

const etapaAtual = () => S.est && S.est.etapas.find((e) => e.id === S.etapa);

async function atualizarRevisao() {
  const slug = S.slug;
  const est = await api("GET", `/api/producoes/${slug}`);
  if (S.slug !== slug || S.tela !== "revisao") return;
  S.est = est;
  document.title = `${est.titulo} · Revisão`;
  if (!S.etapa || !est.etapas.some((e) => e.id === S.etapa)) S.etapa = est.resumo.etapa_atual;
  const e = etapaAtual();
  const versaoPedida = S.versao || e.versao_id;
  let cont = S.cont;
  if (e.versao_id || !cont || cont.material !== e.material) {
    cont = await api("GET", `/api/producoes/${slug}/material/${e.material}${versaoPedida ? `?versao=${versaoPedida}` : ""}`);
    if (S.slug !== slug || etapaAtual().material !== e.material) return;
    S.cont = cont;
  }
  seMudou("barra", [est.titulo, est.resumo, est.arquivada, est.publicado, est.simulado], desenharBarra);
  seMudou("trilho", [est.etapas.map((x) => [x.id, x.status, x.status_texto, x.versao]), S.etapa], desenharTrilho);
  seMudou("cabeca", [e.id, cont.versoes, cont.versao, S.versao], desenharCabeca);
  seMudou("faixas", [e.job, e.progresso, e.falha, e.obsoleto, e.status, cont.e_atual, S.versao, cont.versao && cont.versao.numero], desenharFaixas);
  if (!Corte.editando) seMudou("corpo", [e.id, e.status === "executando" && !cont.versao, cont.versao && cont.versao.id, cont.dados, S.aba[e.id], S.filtro, S.editandoMat, e.reauditar, e.editavel, e.status], desenharCorpo);
  seMudou("decisao", [e.acoes, e.status, e.status_texto, e.id, cont.e_atual, e.obsoleto, cont.dados && cont.dados.download, cont.dados && cont.dados.parecer, cont.dados && cont.dados.parecer_vini, e.pendentes, e.total_itens], desenharDecisao);
  seMudou("feedback-comp", [e.id, cont.e_atual, !!cont.versao, S.est.etapas.length], desenharComposer);
  seMudou("feedback-lista", [cont.feedback, cont.versao && cont.versao.id], desenharListaFeedback);
  seMudou("tecnico", [e.id], desenharTecnico);
}

function desenharBarra() {
  const est = S.est, r = est.resumo;
  const prontas = r.prontas.length, decisoes = r.decisao.length;
  document.getElementById("barra").replaceChildren(...[
    h("a", { class: "voltar", href: `/estudio/${est.slug}`, id: "voltar-estudio", onclick: (e) => { e.preventDefault(); ir(`/estudio/${est.slug}`); } }, "← Estúdio"),
    h("span", { class: "titulo", title: est.titulo }, est.titulo),
    est.simulado ? h("span", { class: "selo" }, "Simulação") : null,
    est.publicado ? h("a", { class: "selo concluida", href: est.publicado.url, target: "_blank", rel: "noreferrer" }, "Enviado ao YouTube") : null,
    h("span", { class: "prox pequeno" },
      h("span", { class: "mudo" }, `${prontas} ${prontas === 1 ? "pronta" : "prontas"} · ${decisoes ? `${decisoes} com você · ` : ""}`),
      r.proxima.tipo === "voce" ? h("a", { href: "#", id: "ir-proxima", onclick: acao(async (e) => {
        e.preventDefault();
        if (r.proxima.acao === "resolver_parecer") {
          const resultado = await api("POST", `/api/producoes/${est.slug}/resolver_parecer`, {});
          const nomes = [...new Set((resultado.jobs || []).map((j) => j.craque).filter(Boolean))];
          if (!nomes.length) throw new Error("Nao encontrei uma tarefa enviada para este parecer. Confira o painel de trabalhos.");
          aviso(`${resultado.ja ? "Este parecer ja havia sido encaminhado" : "Parecer encaminhado"} para ${nomes.join(", ")}.`);
        } else if (r.proxima.acao === "iniciar") {
          const iniciado = await iniciar(r.proxima.etapa, false);
          if (!iniciado) return;
          if (S.etapa !== r.proxima.etapa || S.versao) selecionar(r.proxima.etapa);
          await atualizar();
        } else await abrirProxima(r.proxima.etapa);
      }) }, h("b", {}, r.proxima.texto)) : h("b", {}, r.proxima.texto)),
    h("button", { class: "btn leve mini", onclick: acao(async () => { await api("POST", `/api/producoes/${est.slug}/arquivar`, { arquivada: !est.arquivada }); aviso(est.arquivada ? "Voltou para em andamento." : "Arquivado."); S.assinaturas.barra = null; }) }, est.arquivada ? "Trazer para em andamento" : "Arquivar")].filter(Boolean));
}

function selecionar(id) {
  if (id === S.etapa && !S.versao) return;
  Corte.editando = false;
  S.editandoMat = null; Corte.editando = false; S.etapa = id; S.versao = null; S.cont = null; S.alvo = null; S.categoria = null; S.ouvirTudo = false; S.trecho = null;
  history.replaceState({}, "", `/producao/${S.slug}?etapa=${id}`);
  S.assinaturas = {};
  atualizar();
}

async function abrirProxima(id) {
  const etapa = S.est.etapas.find((e) => e.id === id);
  if (!etapa) throw new Error("A etapa indicada não existe nesta produção.");
  if (id !== S.etapa || S.versao) selecionar(id);

  const limite = Date.now() + 5000;
  while (Date.now() < limite) {
    const botaoEtapa = document.querySelector(`[data-etapa="${CSS.escape(id)}"]`);
    if (S.etapa === id && botaoEtapa?.classList.contains("ativa")) break;
    await new Promise((resolve) => requestAnimationFrame(resolve));
  }

  const painel = document.getElementById("l-decisao");
  const botaoEtapa = document.querySelector(`[data-etapa="${CSS.escape(id)}"].ativa`);
  if (!botaoEtapa || !painel) throw new Error("Não consegui abrir a etapa para revisão. Tente novamente.");
  painel.scrollIntoView({ behavior: "smooth", block: "start" });
  const acaoDisponivel = painel.querySelector("button:not(:disabled), a[href]");
  if (acaoDisponivel) acaoDisponivel.focus({ preventScroll: true });
  else { painel.tabIndex = -1; painel.focus({ preventScroll: true }); }
  aviso(`Etapa aberta: ${etapa.nome}. Confira o painel Decisão.`);
}

function desenharTrilho() {
  document.getElementById("trilho").replaceChildren(...S.est.etapas.map((e) => h("button", {
    class: `etapa-botao ${e.status}${e.id === S.etapa ? " ativa" : ""}`, onclick: () => selecionar(e.id), "aria-current": e.id === S.etapa ? "step" : null, "data-etapa": e.id },
    h("span", { class: "nome" }, h("span", { class: `pino ${e.status}` }), e.nome, e.versao ? h("span", { class: "mudo mini num", style: "font-weight:400;margin-left:auto" }, `v${e.versao}`) : null),
    h("span", { class: "st" }, e.status_texto))));
}

function desenharCabeca() {
  const e = etapaAtual(), c = S.cont;
  const seletor = c.versoes.length ? h("select", { class: "seletor-versao", id: "versao", "aria-label": "Versão", onchange: (ev) => {
    const id = Number(ev.target.value);
    S.versao = id === c.versoes[0].id ? null : id;
    history.replaceState({}, "", `/producao/${S.slug}?etapa=${e.id}${S.versao ? `&versao=${S.versao}` : ""}`);
    atualizar();
  } }, c.versoes.map((v, i) => h("option", { value: v.id, selected: c.versao && v.id === c.versao.id },
    `v${v.numero}${i === 0 ? " (atual)" : ""}${v.aprovada ? " · aprovada" : ""} · ${quando(v.criada_em)}`))) : null;
  document.getElementById("c-cabeca").replaceChildren(h("div", { class: "linha-flex" },
    h("h1", { style: "font-size:1.25rem" }, e.nome), seletor,
    h("span", { class: "mudo pequeno" }, e.craque)));
}

function desenharFaixas() {
  const e = etapaAtual(), c = S.cont, alvo = document.getElementById("c-faixas");
  const faixas = [];
  if (c.versao && !c.e_atual) {
    faixas.push(h("div", { class: "faixa antiga linha-flex" }, h("span", {}, `Você está vendo a v${c.versao.numero}, que não é a atual. Só a versão atual pode ser aprovada.`), h("span", { class: "espaco" }),
      h("button", { class: "btn mini", onclick: () => { S.versao = null; history.replaceState({}, "", `/producao/${S.slug}?etapa=${e.id}`); atualizar(); } }, "Ver a atual")));
  }
  if (e.job) {
    const p = e.progresso || {};
    const na_fila = e.job.status === "fila";
    faixas.push(h("div", { class: "faixa andando", id: "faixa-execucao" },
      h("div", { class: "linha-flex" }, h("b", {}, na_fila ? `Na fila: ${e.job.titulo}` : e.job.titulo), p.porcentagem != null ? h("span", { class: "num" }, `${p.porcentagem}%`) : null, h("span", { class: "espaco" }),
        h("button", { class: "btn mini", onclick: () => verLog(e.job.id) }, "Ver log"),
        h("button", { class: "btn mini", onclick: acao(async () => { await api("POST", `/api/jobs/${e.job.id}/cancelar`); aviso("Cancelado."); }) }, "Cancelar")),
      seloMotor(e.job),
      !na_fila && p.detalhe ? h("div", { class: "mudo pequeno", style: "overflow-wrap:anywhere" }, p.passo ? `${p.passo} · ${p.detalhe}` : p.detalhe) : null,
      na_fila ? h("div", { class: "mudo pequeno" }, "Render e narração rodam um por vez. Você pode fechar esta página: o trabalho continua.") : null,
      p.porcentagem != null ? h("div", { class: "progresso" }, h("i", { style: `width:${p.porcentagem}%` })) : null));
  }
  if (e.falha) {
    faixas.push(h("div", { class: "faixa falha", id: "faixa-falha" },
      h("b", {}, `Falhou: ${e.falha.titulo}`), seloMotor(e.falha), h("div", { class: "erro-texto", id: "erro-texto" }, e.falha.erro || "Sem mensagem."),
      h("div", { class: "linha-flex" },
        h("button", { class: "btn principal", id: "tentar", onclick: acao(async () => { await api("POST", `/api/jobs/${e.falha.id}/tentar`); aviso("Tentando de novo."); }) }, "Tentar novamente"),
        h("button", { class: "btn", onclick: () => verLog(e.falha.id) }, "Ver log"),
        h("button", { class: "btn leve", onclick: acao(async () => { await api("POST", `/api/jobs/${e.falha.id}/dispensar`); }) }, "Dispensar aviso"))));
  }
  if (e.obsoleto && c.e_atual) {
    const cenas = e.obsoleto.cenas || [];
    faixas.push(h("div", { class: "faixa velha", id: "faixa-velha" }, h("b", {}, "Desatualizada. "), e.obsoleto.motivo, cenas.length && e.id === "video" ? ` (${cenas.length === 1 ? "cena" : "cenas"} ${cenas.map((i) => i + 1).join(", ")})` : ""));
  }
  alvo.replaceChildren(...faixas);
}

function verLog(id) {
  const pre = h("pre", { class: "log" }, "Carregando…");
  const fechar = () => { clearInterval(t); d.close(); d.remove(); };
  const d = h("dialog", { oncancel: fechar }, h("div", { class: "modal", style: "width:760px" }, h("div", { class: "linha-flex" }, h("h2", {}, "Log do trabalho"), h("span", { class: "espaco" }), h("button", { class: "btn mini", onclick: fechar }, "Fechar")), pre));
  const ler = async () => { const r = await api("GET", `/api/jobs/${id}/log`).catch(() => ({ log: "" })); const fim = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 30; pre.textContent = r.log || "(sem saída ainda)"; if (fim) pre.scrollTop = pre.scrollHeight; };
  const t = setInterval(ler, 2000);
  document.body.append(d); d.showModal(); ler();
}

function desenharCorpo() {
  const e = etapaAtual(), c = S.cont, alvo = document.getElementById("c-corpo");
  if (!c.versao) {
    const comoAplicar = proximoPassoNaoAplica(e);
    const msg = e.status === "executando" || e.status === "fila" ? [`${e.craque} está trabalhando nisto.`, "O material aparece aqui quando ficar pronto."]
      : e.status === "nao_aplica" ? ["Esta etapa não é usada neste vídeo.", e.motivo_nao_aplica || "Ela não faz parte do fluxo desta produção."]
        : e.status === "bloqueada" ? ["Ainda não pode começar.", "As dependências estão no painel ao lado."] : ["Ainda não foi gerado.", "Inicie pelo painel ao lado."];
    alvo.replaceChildren(h("div", { class: "vazio-etapa" }, h("b", {}, msg[0]), h("div", {}, msg[1]), comoAplicar ? h("div", { class: "proximo-passo" }, comoAplicar) : null));
    return;
  }
  const vistas = { roteiro: vistaRoteiro, narracao: vistaNarracao, componentes: vistaAssets, cenas: vistaAssets, video: vistaVideo };
  alvo.replaceChildren((vistas[e.material] || vistaTexto)(e, c.dados));
  Corte.complementarRevisao(e, c, alvo);
}

function proximoPassoNaoAplica(e) {
  if (e.status !== "nao_aplica") return null;
  const motivo = e.motivo_nao_aplica || "";
  if (e.id === "componentes" && /simulada|--mock/i.test(motivo)) return "Para usar esta etapa, crie a produção normal pelo Corte, sem --mock.";
  if (e.id === "componentes" && /fora do estúdio|terminal/i.test(motivo)) return "Para usar esta etapa, inicie uma nova produção pelo Corte; pastas importadas do terminal não chamam o Raphinha.";
  if (/^auditoria/.test(e.id) && /simulada|--mock/i.test(motivo)) return "Para passar pela auditoria, crie a produção normal pelo Corte, sem --mock.";
  if (e.id === "narracao" && /formato antigo|sem campo fala/i.test(motivo)) return "Para narrar, atualize o cenas.json para o formato atual e informe a fala de cada cena.";
  if (e.id === "narracao" && /nenhuma cena tem fala/i.test(motivo)) return "Para narrar, adicione a fala de cada cena ao cenas.json.";
  return null;
}

/* --- Roteiro --- */
function vistaRoteiro(e, d) {
  const abas = [];
  if (d.mudancas) abas.push(["mudancas", `O que mudou desde v${d.mudancas.de}`]);
  if (d.cenas.length && S.cont.e_atual) abas.push(["cenas", "Por cena"]);  // o cenas.json é o de agora: não vale para a versão antiga
  abas.push(["texto", "Texto"]);
  if (d.direcao_geral || d.revisao) abas.push(["direcao", "Direção e revisão"]);
  const atual = S.aba[e.id] && abas.some((a) => a[0] === S.aba[e.id]) ? S.aba[e.id] : abas[0][0];
  const corpo = atual === "cenas" ? listaCenas(d) : atual === "mudancas" ? blocoMudancas(d.mudancas)
    : atual === "direcao" ? h("div", {}, d.direcao_geral ? h("div", { class: "folha texto", style: "margin-bottom:12px" }, d.direcao_geral) : null, d.revisao ? h("div", { class: "folha texto" }, d.revisao) : null)
      : emEdicao(e) ? formRoteiro(e, d) : h("div", {}, caixaReauditar(e), botaoEditar(e), h("div", { class: "folha leitura" }, d.paragrafos.map((p) => h("p", {}, p))));
  return h("div", {}, h("div", { class: "abas", role: "tablist" }, abas.map(([id, t]) => h("button", { class: "aba" + (id === atual ? " ativa" : ""), role: "tab", onclick: () => { S.aba[e.id] = id; atualizar(); } }, t))), corpo);
}

function blocoMudancas(m) {
  return h("div", { class: "folha leitura", id: "mudancas", style: "white-space:pre-wrap" }, m.ops.map(([t, x]) => t === "igual" ? x : h("span", { class: t }, x)));
}

function listaCenas(d) {
  return h("div", {}, h("div", { class: "cena-cabeca" }, h("span", {}, d.cenas[0] && d.cenas[0].tempo_exato ? "Tempo" : "Tempo (est.)"), h("span", {}, "Narração"), h("span", {}, "Texto na tela"), h("span", { class: "c-dir" }, "Direção visual")),
    d.cenas.map((c) => h("article", { class: "cena" + (c.afetada ? " afetada" : ""), "data-cena": c.i },
      h("div", { class: "tc" }, h("b", {}, `Cena ${c.i + 1}`), tempoCurto(c.inicio), "–", tempoCurto(c.inicio + c.dur), h("div", {}, h("button", { class: "btn leve mini", style: "padding:0;margin-top:3px", onclick: () => mirar({ cena: c.i, rotulo: `Cena ${c.i + 1}` }) }, "Comentar"))),
      h("div", { class: "fala" }, Corte.campoCena(c, "fala", c.fala), c.afetada ? h("div", { class: "mini", style: "color:var(--decisao);font-weight:600;margin-top:3px" }, "Afetada pela mudança no roteiro") : null),
      h("div", { class: "tela" }, c.tela.length ? c.tela.map((t) => h("span", {}, t)) : h("em", { class: "mudo mini" }, "Sem texto na tela")),
      h("div", { class: "dir" }, Corte.campoCena(c, "direcao", c.direcao)))));
}

/* --- Narração --- */
function vistaNarracao(e, d) {
  const audio = h("audio", { controls: true, preload: "metadata", id: "audio", onended: () => { if (S.ouvirTudo) proximoTrecho(d); }, ontimeupdate: () => atualizarMarcaAudio(), onpause: () => atualizarMarcaAudio(true) });
  const rotuloAtual = h("span", { id: "trecho-atual", class: "pequeno" }, "Escolha um trecho");
  const lista = h("div", { id: "trechos" });
  const busca = h("input", { class: "busca", type: "search", id: "busca", placeholder: "Buscar um trecho pelo texto", oninput: () => desenharTrechos(d, busca.value) });
  const player = h("div", { class: "player-narracao" },
    h("div", { class: "linha-flex" }, rotuloAtual, h("span", { class: "espaco" }), d.total ? h("span", { class: "mudo pequeno num" }, `Total ${tempoCurto(d.total)}`) : null,
      h("button", { class: "btn mini", id: "repetir", onclick: () => { audio.currentTime = 0; audio.play(); } }, "Ouvir novamente"),
      d.trechos.length > 1 ? h("button", { class: "btn mini", id: "ouvir-tudo", onclick: () => { S.ouvirTudo = true; tocarTrecho(d, d.trechos[0]); } }, "Ouvir tudo") : null),
    audio);
  setTimeout(() => { desenharTrechos(d, ""); if (S.trecho == null && d.trechos[0]) selecionarTrecho(d.trechos.find((t) => t.desatualizado || t.decisao !== "aprovado") || d.trechos[0]); else { const t = d.trechos.find((x) => x.item === S.trecho); if (t) selecionarTrecho(t); } }, 0);
  return h("div", {}, player, d.trechos.length > 1 ? busca : null, lista);
}

function selecionarTrecho(t) {
  S.trecho = t.item;
  const a = document.getElementById("audio");
  if (a && a.dataset.src !== t.url) { a.src = t.url; a.dataset.src = t.url; a.load(); }
  const r = document.getElementById("trecho-atual");
  if (r) r.textContent = t.i != null ? `Cena ${t.i + 1}${t.dur ? ` · ${tempoCurto(t.dur)}` : ""}` : "Áudio do vídeo";
  document.querySelectorAll(".trecho").forEach((x) => x.classList.toggle("tocando", x.dataset.item === t.item));
  if (t.i != null) mirar({ item: t.item, cena: t.i, rotulo: `Cena ${t.i + 1}` }, true);
  else mirar({ item: t.item, rotulo: "Áudio único" }, true);
}

function tocarTrecho(d, t) {
  selecionarTrecho(t);
  const a = document.getElementById("audio");
  if (a) a.play().catch(() => {});
}

function proximoTrecho(d) {
  const i = d.trechos.findIndex((t) => t.item === S.trecho);
  if (i >= 0 && i + 1 < d.trechos.length) tocarTrecho(d, d.trechos[i + 1]); else S.ouvirTudo = false;
}

function destacar(texto, q) {
  if (!q) return texto;
  const i = texto.toLowerCase().indexOf(q.toLowerCase());
  return i < 0 ? texto : [texto.slice(0, i), h("mark", {}, texto.slice(i, i + q.length)), texto.slice(i + q.length)];
}

function desenharTrechos(d, q) {
  const alvo = document.getElementById("trechos");
  if (!alvo) return;
  const atuais = S.cont && S.cont.e_atual;
  const visiveis = d.trechos.filter((t) => !q || t.texto.toLowerCase().includes(q.toLowerCase()));
  alvo.replaceChildren(...(visiveis.length ? visiveis.map((t) => h("article", { class: `trecho${t.item === S.trecho ? " tocando" : ""}${t.desatualizado ? " velho" : ""}`, "data-item": t.item },
    h("button", { class: "tocar", "aria-label": `Tocar ${t.i != null ? `cena ${t.i + 1}` : "áudio"}`, onclick: () => { S.ouvirTudo = false; tocarTrecho(d, t); } }, "▶"),
    h("div", { style: "cursor:pointer", onclick: () => selecionarTrecho(t) },
      h("div", { class: "mudo mini linha-flex" }, t.i != null ? h("b", {}, `Cena ${t.i + 1}`) : null, t.dur ? h("span", { class: "num" }, `${tempoCurto(t.inicio)} · ${t.dur.toFixed(1)} s`) : null,
        t.desatualizado ? h("span", { class: "selo desatualizada" }, "Desatualizado") : t.decisao === "aprovado" ? h("span", { class: "selo aprovada" }, "Aprovado") : h("span", { class: "selo aguardando" }, "A revisar")),
      h("div", { class: "texto-t" }, destacar(t.texto, q))),
    atuais ? h("div", { class: "acoes-t" },
      t.decisao !== "aprovado" && !t.desatualizado ? h("button", { class: "btn mini", "data-aprovar": t.item, onclick: acao(async () => { await decidirItem(t.item, "aprovado"); }) }, "Aprovar") : null,
      h("button", { class: "btn leve mini", onclick: () => { selecionarTrecho(t); document.getElementById("fb-texto")?.focus(); } }, "Pedir ajuste"),
      t.i != null && !S.est.em_grafo ? h("button", { class: "btn leve mini", "data-refazer": t.item, onclick: acao(async () => { await iniciar("narracao", true, [t.i]); }) }, "Gerar de novo") : null,
      t.i != null ? h("button", { class: "btn leve mini", "data-tomadas": t.item, onclick: () => Corte.abrirTomadas(t) }, "Tomadas") : null) : null))
    : [h("div", { class: "vazio-texto" }, "Nenhum trecho com esse texto.")]));
}

function atualizarMarcaAudio(aoPausar) {
  const a = document.getElementById("audio");
  if (!a || !S.alvo) return;
  if (aoPausar && a.currentTime > 0 && !a.ended) { S.alvo.tempo_s = a.currentTime; desenharAlvo(); }
}

async function decidirItem(item, decisao) {
  const r = await api("POST", `/api/producoes/${S.slug}/item`, { material: S.cont.material, versao_id: S.cont.versao.id, item, decisao });
  if (r.iniciados && r.iniciados.length) aviso("Tudo aprovado: a próxima etapa começou.");
}

/* --- Assets --- */
function vistaAssets(e, d) {
  const atuais = S.cont.e_atual;
  if (!d.grupos.length) {
    return h("div", {}, d.cenas && d.cenas.length ? h("div", {}, h("p", { class: "mudo pequeno", style: "margin-bottom:10px" }, d.estilo !== "cartoes" ? "Sem previa.jpg: rode a prévia para revisar o desenho de cada cena." : "Este estilo não gera prévia por cena: os cartões são revisados no vídeo final."), listaCenas(d)) : h("div", { class: "vazio-etapa" }, h("b", {}, "Nenhuma prévia encontrada.")));
  }
  const aprovadas = d.total - d.pendentes;
  const fase = e.id === "componentes" && d.fase === "pronto" ? h("span", { class: "mudo pequeno" }, "Fase “pronto”: revisão opcional") : null;
  const filtros = [["todos", "Todos"], ["pendentes", "A revisar"], ["aprovados", "Aprovados"]];
  const contador = h("div", { class: "contador", id: "contador" },
    d.pendentes ? h("b", {}, `${d.pendentes} de ${d.total} ainda ${d.pendentes === 1 ? "precisa" : "precisam"} de revisão`) : h("b", { style: "color:var(--ok)" }, `Os ${d.total} estão aprovados`),
    fase, h("span", { class: "espaco" }), h("span", { class: "mudo pequeno num" }, `${aprovadas} aprovados`),
    h("div", { class: "chips", style: "margin:0" }, filtros.map(([id, t]) => h("button", { class: "chip" + (S.filtro === id ? " on" : ""), onclick: () => { S.filtro = id; atualizar(); } }, t))));
  const passa = (it) => S.filtro === "todos" || (S.filtro === "pendentes" ? it.decisao !== "aprovado" : it.decisao === "aprovado");
  const todos = d.grupos.flatMap((g) => g.itens);
  const grupos = d.grupos.map((g) => {
    const itens = g.itens.filter(passa);
    if (!itens.length) return null;
    return h("section", {}, h("div", { class: "grupo-titulo" }, h("h2", {}, g.titulo), g.fala ? h("span", { class: "mudo pequeno", style: "overflow:hidden;white-space:nowrap;text-overflow:ellipsis" }, g.fala) : null),
      h("div", { class: "grade" + (itens[0].largo ? " larga" : "") }, itens.map((it) => cartaoAsset(it, todos, atuais, d))));
  });
  return h("div", {}, contador, grupos);
}

function pedidosDoItem(item) {
  return (S.cont.feedback || []).filter((f) => f.item === item && f.versao_id === S.cont.versao.id && f.status === "rascunho");
}

function rotuloItem(it) { return it.i != null ? `Cena ${it.i + 1}` : it.item.replace(/_/g, " "); }

function cartaoAsset(it, todos, atuais, d) {
  const pedido = pedidosDoItem(it.item).length > 0;
  const estado = pedido ? h("span", { class: "selo aguardando" }, "Substituição anotada") : it.decisao === "aprovado" ? h("span", { class: "selo aprovada" }, "Aprovado") : h("span", { class: "selo" }, "A revisar");
  const afetada = d.afetadas && d.afetadas.includes(it.i);
  return h("article", { class: `asset${it.decisao === "aprovado" ? " aprovado" : ""}${pedido || afetada ? " pedido" : ""}`, "data-item": it.item },
    h("button", { class: "img", "aria-label": `Ampliar ${rotuloItem(it)}`, onclick: () => ampliar(it, todos, atuais) }, h("img", { src: it.url, alt: rotuloItem(it), loading: "lazy" })),
    h("div", { class: "info" }, h("div", { class: "linha-flex" }, h("span", { class: "nome" }, rotuloItem(it)), estado),
      it.fala ? h("div", { class: "fala-item" }, it.fala) : null,
      it.cenas ? h("div", { class: "mini mudo" }, it.cenas.length ? `Usado ${it.cenas.length > 1 ? "nas cenas" : "na cena"} ${it.cenas.map((c) => c + 1).join(", ")}` : "Uso em cena não indicado no componentes.md") : null,
      afetada ? h("div", { class: "mini", style: "color:var(--decisao);font-weight:600" }, "O texto desta cena mudou") : null,
      atuais ? h("div", { class: "botoes" },
        it.decisao !== "aprovado" ? h("button", { class: "btn mini", "data-aprovar": it.item, onclick: acao(async () => { await decidirItem(it.item, "aprovado"); }) }, "Aprovar") : h("button", { class: "btn leve mini", onclick: acao(async () => { await decidirItem(it.item, "pendente"); }) }, "Desfazer"),
        h("button", { class: "btn leve mini", "data-substituir": it.item, onclick: () => pedirSubstituicao(it) }, "Pedir refazer"),
        e_componente(it) ? Corte.botaoArquivo("Trocar arquivo", `/api/producoes/${S.slug}/enviar/componente?item=${encodeURIComponent(it.item)}`, () => { S.assinaturas.corpo = null; atualizar(); }) : null) : null));
}

const e_componente = (it) => S.etapa === "componentes" && it.i === undefined;

function pedirSubstituicao(it) {
  mirar({ item: it.item, cena: it.i != null ? it.i : null, rotulo: rotuloItem(it) });
}

function ampliar(it, todos, atuais) {
  let i = todos.findIndex((x) => x.item === it.item);
  const img = h("img", { alt: "" }), nome = h("b", {}), fala = h("span", { class: "pequeno", style: "opacity:.8;flex:1;min-width:0" });
  const fechar = () => { d.close(); d.remove(); };
  const mostrar = () => { const x = todos[i]; img.src = x.url; img.alt = rotuloItem(x); nome.textContent = rotuloItem(x); fala.textContent = x.fala || ""; };
  const passar = (n) => { i = (i + n + todos.length) % todos.length; mostrar(); };
  const d = h("dialog", { class: "ampliado", id: "ampliado", onclick: (e) => { if (e.target === d) fechar(); }, onkeydown: (e) => { if (e.key === "ArrowRight") passar(1); if (e.key === "ArrowLeft") passar(-1); } },
    img, h("div", { class: "botoes" }, nome, fala,
      h("button", { class: "btn", onclick: () => passar(-1) }, "←"), h("button", { class: "btn", onclick: () => passar(1) }, "→"),
      atuais ? h("button", { class: "btn aprovar", onclick: acao(async () => { await decidirItem(todos[i].item, "aprovado"); todos[i].decisao = "aprovado"; aviso(`${rotuloItem(todos[i])} aprovado.`); if (todos.length > 1) passar(1); }) }, "Aprovar") : null,
      atuais ? h("button", { class: "btn", onclick: () => { const x = todos[i]; fechar(); pedirSubstituicao(x); } }, "Pedir substituição") : null,
      h("button", { class: "btn", onclick: fechar }, "Fechar")));
  document.body.append(d); mostrar(); d.showModal();
}

/* --- Vídeo final --- */
function vistaVideo(e, d) {
  const video = h("video", { controls: true, preload: "metadata", src: d.url, id: "video", playsInline: true,
    onpause: (ev) => { if (!ev.target.ended) marcarTempoVideo(); },
    onseeked: (ev) => { if (ev.target.paused) marcarTempoVideo(); },
    ontimeupdate: (ev) => realcarCena(ev.target.currentTime, d) });
  const vertical = d.formato !== "horizontal";
  const cenas = d.cenas.length ? h("div", { class: "cenas-video", id: "cenas-video" }, h("h3", { style: "margin:0 0 5px 9px" }, d.tempos_exatos ? "Cenas" : "Cenas (tempos estimados)"), d.cenas.map((c) => h("button", { class: "cena-tempo", "data-c": c.i, onclick: () => { video.currentTime = c.inicio + 0.05; video.pause(); } }, h("span", { class: "num mudo" }, tempoCurto(c.inicio)), h("span", {}, c.fala)))) : null;
  return h("div", {}, Corte.barraVideo(d, video), h("div", { class: "palco" + (vertical ? "" : " horizontal") }, h("div", { class: "video-caixa" + (vertical ? "" : " horizontal") }, video), cenas));
}

function cenaNoTempo(t, d) {
  let achada = null;
  for (const c of (d && d.cenas) || []) if (t >= c.inicio) achada = c;
  return achada;
}

function marcarTempoVideo() {
  const v = document.getElementById("video");
  if (!v) return;
  const c = cenaNoTempo(v.currentTime, S.cont.dados);
  S.alvo = { tempo_s: v.currentTime, cena: c ? c.i : null, rotulo: c ? `Cena ${c.i + 1}` : "Vídeo" };
  desenharAlvo();
}

function realcarCena(t, d) {
  const c = cenaNoTempo(t, d);
  document.querySelectorAll(".cena-tempo").forEach((b) => b.classList.toggle("atual", !!c && Number(b.dataset.c) === c.i));
}

/* --- Textos de apoio --- */
/* Edição direta (sem chamar o agente): botão "Editar eu mesmo", motivo se houver trabalho rodando e botão de reauditar. */
const ocupadoComAgente = (e) => e.status === "executando" || e.status === "fila";
const emEdicao = (e) => S.editandoMat === e.id && S.cont && S.cont.e_atual;

/* Ao abrir a edição, a tela é desenhada na hora: o laço de atualização não redesenha o corpo enquanto Corte.editando está ligado
   (para não apagar o que se digita), então esperar por ele deixaria o clique sem efeito. */
function iniciarEdicao(e, v) {
  S.editandoMat = v ? e.id : null; Corte.editando = !!v; S.assinaturas.corpo = null;
  if (v) desenharCorpo();
  atualizar();
}

function botaoEditar(e) {
  if (!S.cont || !S.cont.e_atual) return h("p", { class: "mini mudo" }, "Volte para a versão atual para editar.");
  const ocupado = ocupadoComAgente(e), semPermissao = e.editavel === false;
  const motivo = ocupado ? `${e.craque || "O agente"} está trabalhando neste material agora; espere terminar para não sobrescrever o trabalho dele.`
    : semPermissao ? "Esta etapa não pode ser editada à mão neste momento." : "";
  return h("div", { class: "edicao-direta" },
    h("button", { class: "btn principal", id: "editar-eu-mesmo", disabled: !!motivo, onclick: () => iniciarEdicao(e, true) }, "✎ Editar eu mesmo"),
    h("span", { class: "mini mudo" }, motivo || "Mude o texto direto aqui; o botão de pedir ajuste ao agente continua ao lado."));
}

function caixaReauditar(e) {
  const r = (S.reaud && S.reaud[`${S.slug}:${e.id}`]) || e.reauditar;
  if (!r || !r.no || !r.execucao || !S.cont || !S.cont.e_atual) return null;
  return h("div", { class: "faixa reauditar", id: "reauditar" },
    h("button", { class: "btn principal", id: "reauditar-vini", onclick: acao(async () => {
      await api("POST", `/api/execucoes/${r.execucao}/repetir`, { no: r.no });
      if (S.reaud) delete S.reaud[`${S.slug}:${e.id}`];
      aviso("O Vini vai conferir o texto de novo.");
    }) }, "Reauditar texto (Vini)"),
    h("span", { class: "mini" }, "Você editou direto; o Vini confere de novo, sem chamar o agente."));
}

async function salvarEdicao(e, rota, corpo, msg) {
  const r = await api("POST", `/api/producoes/${S.slug}/${rota}`, corpo);
  const extra = [].concat(r.aviso || r.avisos || []).filter(Boolean).join(" ");
  if (r.reauditar && r.reauditar.no) { S.reaud = S.reaud || {}; S.reaud[`${S.slug}:${e.id}`] = r.reauditar; }
  aviso(`${msg}${extra ? " " + extra : ""}`);
  iniciarEdicao(e, false);
}

function formMetadados(e, m) {
  const campo = (id, rot, el, dica) => h("div", { class: "meta-bloco" }, h("label", { for: id }, h("h3", {}, rot)), el, dica);
  const estilo = "width:100%;box-sizing:border-box;font:inherit;min-height:40px";
  const titulo = h("input", { type: "text", id: "ed-titulo", style: estilo, maxLength: 200 }); titulo.value = m.titulo || "";
  const cont = h("div", { class: "mini", id: "ed-titulo-cont" });
  const medir = () => { const n = titulo.value.length; cont.textContent = `${n} de 100 caracteres${n > 100 ? ": passou do limite do YouTube, encurte." : ""}`; cont.style.color = n > 100 ? "var(--erro)" : ""; };
  titulo.addEventListener("input", medir); medir();
  const desc = h("textarea", { id: "ed-descricao", style: estilo + ";min-height:160px" }); desc.value = m.descricao || "";
  const tags = h("textarea", { id: "ed-tags", style: estilo + ";min-height:70px" }); tags.value = (m.tags || []).join(", ");
  const lista = () => tags.value.split(/[,\n]/).map((t) => t.trim()).filter(Boolean);
  const previa = h("div", { class: "meta-bloco tags", id: "ed-tags-previa", style: "margin-top:6px" });
  const pintar = () => previa.replaceChildren(...lista().map((t) => h("span", {}, t)));
  tags.addEventListener("input", pintar); pintar();
  const thumb = h("input", { type: "text", id: "ed-thumb", style: estilo }); thumb.value = m.thumbnail_texto || "";
  return h("div", { class: "folha edicao" },
    campo("ed-titulo", "Título", titulo, cont),
    campo("ed-descricao", "Descrição", desc),
    campo("ed-tags", "Tags (separadas por vírgula)", tags, previa),
    campo("ed-thumb", "Texto da thumbnail", thumb),
    h("div", { class: "linha-flex botoes-edicao" },
      h("button", { class: "btn principal", id: "ed-salvar", onclick: acao(async () => {
        if (titulo.value.length > 100) throw new Error("O título tem mais de 100 caracteres. Encurte antes de salvar.");
        await salvarEdicao(e, "editar_metadados", { titulo: titulo.value.trim(), descricao: desc.value, tags: lista(), thumbnail_texto: thumb.value.trim() }, "Metadados salvos.");
      }) }, "Salvar"),
      h("button", { class: "btn", id: "ed-cancelar", onclick: () => iniciarEdicao(e, false) }, "Cancelar")));
}

function formRoteiro(e, d) {
  const caixa = h("textarea", { id: "ed-roteiro", style: "width:100%;box-sizing:border-box;font:inherit;min-height:320px" }); caixa.value = (d.paragrafos || []).join("\n\n");
  return h("div", { class: "folha edicao" }, h("label", { for: "ed-roteiro" }, h("h3", {}, "Texto do roteiro")),
    h("p", { class: "mini mudo" }, "Separe os parágrafos com uma linha em branco. Depois de salvar, a narração e as cenas que usam este texto ficam desatualizadas."), caixa,
    h("div", { class: "linha-flex botoes-edicao", style: "margin-top:8px" },
      h("button", { class: "btn principal", id: "ed-salvar", onclick: acao(async () => { await salvarEdicao(e, "editar_roteiro", { texto: caixa.value }, "Roteiro salvo."); }) }, "Salvar"),
      h("button", { class: "btn", id: "ed-cancelar", onclick: () => iniciarEdicao(e, false) }, "Cancelar")));
}

function vistaTexto(e, d) {
  if (d.metadados) {
    const m = d.metadados;
    if (emEdicao(e)) return formMetadados(e, m);
    return h("div", {}, caixaReauditar(e), botaoEditar(e), h("div", { class: "folha" }, h("div", { class: "meta-bloco" }, h("h3", {}, "Título"), h("div", { style: "font-size:1.2rem;font-weight:600" }, m.titulo || "–")),
      m.thumbnail_texto ? h("div", { class: "meta-bloco" }, h("h3", {}, "Texto da thumbnail"), m.thumbnail_texto) : null,
      h("div", { class: "meta-bloco" }, h("h3", {}, "Descrição"), h("div", { style: "white-space:pre-wrap" }, m.descricao || "–")),
      h("div", { class: "meta-bloco tags" }, h("h3", {}, "Tags"), (m.tags || []).map((t) => h("span", {}, t)))));
  }
  return h("div", {}, d.partes.map((p) => h("div", { class: "folha texto", style: "margin-bottom:12px" }, d.partes.length > 1 ? h("h3", { style: "margin-bottom:8px" }, p.nome) : null, p.texto)));
}

/* ---------- Painel lateral ---------- */
async function iniciar(etapa, forcar, escopo) {
  const r = await api("POST", `/api/producoes/${S.slug}/iniciar`, { etapa, forcar, escopo });
  if (r.novo) { aviso("Trabalho iniciado."); return true; }
  const por = [].concat(r.motivo || r.motivos || r.aviso || []).filter(Boolean).join(" ");
  aviso(`Nada foi disparado. ${por || "Já existe um trabalho desta etapa na fila ou em andamento; se não houver, veja o painel de trabalhos."}`, true);
  return false;
}

/* Diz quem está segurando a etapa e, se for uma falha, oferece repetir o nó. */
const VERBO_BLOQUEIO = { falhou: "falhou", falha: "falhou", aguardando: "aguarda aprovação", aguardando_aprovacao: "aguarda aprovação", bloqueio: "foi bloqueado pelo Vini", rodando: "ainda está rodando", fila: "está na fila", pendente: "ainda não começou", desatualizada: "está desatualizada" };
function caixaBloqueio(b, execucao) {
  if (!b) return null;
  const nome = b.nome || b.no || "uma etapa anterior";
  const verbo = VERBO_BLOQUEIO[b.status] || (b.status ? `está em “${String(b.status).replace(/_/g, " ")}”` : "não terminou");
  const exec = b.execucao || b.execucao_id || execucao;
  const falhou = b.status === "falhou" || b.status === "falha";
  return h("div", { class: "faixa falha bloqueio", id: "bloqueio" },
    h("b", {}, `Esta etapa está esperando ${nome}, que ${verbo}.`),
    b.nota ? h("div", { class: "erro-texto" }, String(b.nota).length > 280 ? String(b.nota).slice(0, 280) + "…" : b.nota) : null,
    falhou && exec && b.no ? h("button", { class: "btn mini", id: "tentar-de-novo", onclick: acao(async () => { await api("POST", `/api/execucoes/${exec}/repetir`, { no: b.no }); aviso(`${nome} foi enviado para rodar de novo.`); }) }, "Tentar de novo") : null);
}

function desenharDecisao() {
  const e = etapaAtual(), c = S.cont, alvo = document.getElementById("l-decisao"), a = e.acoes, partes = [];
  if (e.id === "cenas" && e.obsoleto) {
    partes.push(h("div", { class: "faixa aviso", id: "opcoes-cenas-desatualizadas" },
      h("b", {}, "As cenas aprovadas ainda podem ser mantidas."),
      h("p", { class: "pequeno" }, "Escolha: restaurar o roteiro exato que foi usado nelas, sem mexer nas cenas; ou pedir cenas novas para o roteiro atual."),
      h("button", { class: "btn aprovar largo", id: "manter-cenas-aprovadas", onclick: acao(async () => {
        await api("POST", `/api/producoes/${S.slug}/manter_cenas_aprovadas`, {});
        aviso("Roteiro compatível restaurado. As cenas aprovadas foram preservadas.");
        await atualizar();
      }) }, "Manter roteiro e cenas aprovadas"),
      h("button", { class: "btn largo", id: "criar-cenas-novas", style: "margin-top:6px", onclick: acao(async () => { await iniciar("cenas", true); }) }, "Criar cenas novas para o roteiro atual")));
  }
  if (a.pular_vini && !a.pular_vini.dispensada) {
    const nomes = { roteiro: "roteiro", cenas: "cenas", metadados: "metadados" };
    partes.push(h("div", { class: "faixa", id: "controles-pular-vini", style: "margin-bottom:9px" },
      h("b", {}, "Controle do parecer do Vini · por escopo"),
      h("p", { class: "mini mudo" }, "Pular registra sua decisão para esta versão exata; não marca o parecer como aprovado."),
      a.pular_vini.escopos.map((escopo) => h("button", { class: "btn leve mini", type: "button", disabled: a.pular_vini.pulados.includes(escopo), style: "margin:3px 4px 0 0", onclick: acao(async () => {
        if (!confirm(`Pular a auditoria do ${nomes[escopo] || escopo} nesta versão? A decisão ficará registrada.`)) return;
        await api("POST", `/api/producoes/${S.slug}/pular_vini`, { etapa: e.id, escopo });
        aviso(`Auditoria do ${nomes[escopo] || escopo} dispensada nesta versão.`);
        await atualizar();
      }) }, a.pular_vini.pulados.includes(escopo) ? `✓ ${nomes[escopo] || escopo} dispensado` : `Pular auditoria do ${nomes[escopo] || escopo}`))));
  } else if (a.pular_vini?.dispensada) {
    partes.push(h("p", { class: "faixa", id: "vini-dispensado" }, "Auditoria do Vini pulada por decisão sua para os escopos/versões registrados."));
  }
  const titulo = h("div", { class: "linha-flex", style: "margin-bottom:9px" }, h("h3", {}, "Decisão"), h("span", { class: "espaco" }), h("span", { class: `selo ${e.status}`, id: "status-etapa" }, e.status_texto));
  partes.push(titulo);
  if (c.versao && !c.e_atual) partes.push(h("p", { class: "mudo pequeno" }, "Volte para a versão atual para decidir."));
  else {
    if (a.enviar) partes.push(h("div", { style: "margin-bottom:9px" }, h("button", { class: "btn principal largo", id: "enviar-ajustes", disabled: !a.enviar.habilitado, onclick: acao(async () => { await api("POST", `/api/producoes/${S.slug}/enviar_ajustes`, { material: e.material, versao_id: a.enviar.versao_id }); aviso(`Enviado para ${a.enviar.quem}.`); }) }, a.enviar.rotulo), listaMotivos(a.enviar.motivos)));
    if (a.aprovar) {
      if (a.aprovar.ja && !e.obsoleto) partes.push(h("div", { class: "feito", id: "ja-aprovado" }, `✓ ${e.nome} v${a.aprovar.numero} aprovada`));
      else {
        partes.push(h("button", { class: "btn aprovar largo", id: "aprovar", disabled: !a.aprovar.habilitado, onclick: acao(async () => {
          const r = await api("POST", `/api/producoes/${S.slug}/aprovar`, { material: e.material, versao_id: a.aprovar.versao_id });
          aviso(r.iniciados && r.iniciados.length ? "Aprovado. A próxima etapa começou." : "Aprovado.");
        }) }, a.aprovar.rotulo));
        if (a.aprovar.motivos.length) partes.push(listaMotivos(a.aprovar.motivos));
        else if (a.aprovar.frase) partes.push(h("p", { class: "consequencia", id: "consequencia" }, a.aprovar.frase));
        if (a.aprovar.ainda && a.aprovar.ainda.length) partes.push(listaMotivos(a.aprovar.ainda));
      }
    }
    if (c.dados && c.dados.download && e.id === "video") partes.push(h("div", { class: "baixar" }, h("a", { class: "btn aprovar largo", id: "baixar", href: c.dados.download, download: "" }, `Baixar vídeo final v${c.versao.numero}`), h("span", { class: "mini mudo" }, "Publicar continua pelo terminal, e exige o parecer do Vini:"), h("code", { class: "mini", style: "overflow-wrap:anywhere" }, c.dados.publicar)));
    if (e.id === "video" && c.dados && c.versao) partes.push(h("p", { class: "mudo pequeno", style: "margin-top:8px" }, "Vini (auditoria final): ", h("b", {}, c.dados.parecer_vini || "ainda sem parecer")));
    if (c.dados && c.dados.parecer) partes.push(h("p", { class: "pequeno" }, "Parecer do Vini: ", h("b", { style: `color:var(--${c.dados.parecer === "APROVADO" ? "ok" : "erro"})` }, c.dados.parecer)));
    if (a.iniciar) {
      const secundario = a.iniciar.refazer;
      const motivos = (a.iniciar.motivos || []).map((m) => orientarInicio(e, m));
      const bloq = a.iniciar.bloqueio || e.bloqueio || null;
      const semPorque = !a.iniciar.habilitado && !motivos.length && !bloq;
      partes.push(h("div", { style: a.aprovar || a.enviar ? "margin-top:12px;padding-top:12px;border-top:1px solid var(--linha)" : "" },
        !secundario && a.aprovar ? h("h3", { style: "margin-bottom:6px" }, "Passo seguinte") : null,
        caixaBloqueio(bloq, S.execucao || (S.est && S.est.execucao)),
        h("button", { class: `btn largo ${secundario ? "" : "principal"}`, id: "iniciar", disabled: !a.iniciar.habilitado, onclick: acao(async () => { await iniciar(e.id, a.iniciar.refazer); }) }, a.iniciar.rotulo),
        motivos.length ? listaMotivos(motivos) : null,
        semPorque ? listaMotivos(["Este botão está indisponível agora, mas o sistema não informou o motivo. Veja se há trabalho em andamento ou etapa anterior pendente."]) : null));
    }
    else if (e.bloqueio) partes.push(caixaBloqueio(e.bloqueio, S.execucao || (S.est && S.est.execucao)));
    if (partes.length === 1) partes.push(h("p", { class: "mudo pequeno" }, e.status === "executando" || e.status === "fila" ? "Quando terminar, a decisão aparece aqui." : e.gate ? "Nada a decidir nesta etapa agora." : `Esta etapa é conferida por ${e.craque}, sem aprovação sua.`));
  }
  alvo.replaceChildren(...partes);
}

function orientarInicio(e, motivo) {
  const texto = String(motivo || "");
  if (/falta o roteiro/i.test(texto)) return `${texto} Gere e aprove o roteiro antes de iniciar ${e.nome.toLowerCase()}.`;
  if (/roteiro.+não.+aprov/i.test(texto)) return `${texto} Abra a etapa Roteiro e aprove a versão atual.`;
  if (/outra etapa|trabalho.+(?:fila|andamento|rodando|executando)/i.test(texto)) return `${texto} Aguarde esse trabalho terminar e tente novamente.`;
  if (/falta|pendente|bloquead|aguarda/i.test(texto) && !/faça|abra|aprove|termine|aguarde|inicie|gere/i.test(texto)) return `${texto} Abra a etapa pendente e conclua a ação indicada antes de tentar novamente.`;
  return texto;
}

function listaMotivos(m) {
  return m && m.length ? h("ul", { class: "motivos" }, m.map((x) => h("li", {}, x))) : null;
}

function mirar(alvo, silencioso) {
  S.alvo = alvo;
  desenharAlvo();
  if (!silencioso) document.getElementById("fb-texto")?.focus();
}

const TITULOS_FB = { componentes: "Pedir substituição", cenas: "Pedir substituição", video: "Registrar correção", narracao: "Pedir ajuste", roteiro: "Pedir ajuste" };

function desenharComposer() {
  const e = etapaAtual(), c = S.cont, alvo = document.getElementById("l-feedback");
  if (!c.versao || !c.e_atual) { alvo.replaceChildren(); alvo.classList.add("oculto"); return; }
  alvo.classList.remove("oculto");
  if (!S.categoria || !e.categorias.includes(S.categoria)) S.categoria = e.categorias[0] || null;
  const texto = h("textarea", { id: "fb-texto", placeholder: e.material === "video" ? "Pause no ponto e descreva a correção" : e.material === "narracao" ? "Ex.: ‘IBGE’ está sendo lido como palavra" : e.material === "roteiro" ? "Descreva a mudança" : "O que precisa mudar?",
    oninput: (ev) => { try { localStorage.setItem(chaveRascunho(), ev.target.value); } catch (x) { /* sem armazenamento, sem rascunho */ } } });
  try { texto.value = localStorage.getItem(chaveRascunho()) || ""; } catch (x) { /* idem */ }
  const chips = e.categorias.length > 1 ? h("div", { class: "chips", id: "fb-cats" }, e.categorias.map((k) => h("button", { class: "chip" + (k === S.categoria ? " on" : ""), type: "button", onclick: (ev) => { S.categoria = k; ev.currentTarget.parentNode.querySelectorAll(".chip").forEach((x) => x.classList.toggle("on", x === ev.currentTarget)); } }, k))) : null;
  alvo.replaceChildren(h("h3", { style: "margin-bottom:7px" }, TITULOS_FB[e.material] || "Pedir ajuste"), h("div", { class: "alvo", id: "fb-alvo" }), chips, texto,
    h("button", { class: "btn largo", id: "anotar", style: "margin-top:7px", onclick: acao(async () => {
      if (!texto.value.trim()) { texto.focus(); throw new Error("Escreva o que precisa mudar."); }
      const a = S.alvo || {};
      await api("POST", `/api/producoes/${S.slug}/feedback`, { material: e.material, versao_id: S.cont.versao.id, texto: texto.value, item: a.item || null, cena: a.cena ?? null, tempo_s: a.tempo_s ?? null, categoria: S.categoria });
      texto.value = "";
      try { localStorage.removeItem(chaveRascunho()); } catch (x) { /* idem */ }
      if (e.material !== "narracao" && e.material !== "video") S.alvo = null;
      desenharAlvo(); S.assinaturas.corpo = null;
      aviso("Anotado. Envie quando terminar de revisar.");
    }) }, "Anotar ajuste"),
    h("p", { class: "mudo mini", style: "margin-top:5px" }, "Os ajustes anotados seguem juntos quando você enviar. Nada é enviado antes disso."));
  desenharAlvo();
}

const chaveRascunho = () => { const e = etapaAtual(); return `fb:${S.slug}:${e ? e.material : ""}`; };

function desenharAlvo() {
  const box = document.getElementById("fb-alvo"), e = etapaAtual(), d = S.cont && S.cont.dados;
  if (!box || !e) return;
  const a = S.alvo;
  const partes = [];
  if (e.material === "video") {
    partes.push(a && a.tempo_s != null ? [h("span", { class: "mudo pequeno" }, "Neste instante:"), h("span", { class: "marca-tempo", id: "marca-tempo" }, tempo(a.tempo_s)), a.rotulo ? h("span", { class: "selo" }, a.rotulo) : null] : h("span", { class: "mudo pequeno" }, "Pause o vídeo para marcar o instante."));
  } else if (e.material === "roteiro" && d && d.cenas && d.cenas.length) {
    partes.push(h("span", { class: "mudo pequeno" }, "Sobre:"), h("select", { id: "fb-cena", onchange: (ev) => { const v = ev.target.value; S.alvo = v === "" ? null : { cena: Number(v), rotulo: `Cena ${Number(v) + 1}` }; } },
      h("option", { value: "" }, "O roteiro todo"), d.cenas.map((c) => h("option", { value: c.i, selected: a && a.cena === c.i }, `Cena ${c.i + 1}: ${c.fala.slice(0, 38)}…`))));
  } else if (e.material === "narracao") {
    if (a) {
      partes.push(h("span", { class: "selo" }, a.rotulo), a.tempo_s != null ? h("span", { class: "marca-tempo" }, tempo(a.tempo_s)) : null,
        h("button", { class: "btn leve mini", id: "marcar-audio", onclick: () => { const x = document.getElementById("audio"); if (x) { S.alvo.tempo_s = x.currentTime; desenharAlvo(); } } }, "Marcar tempo atual"));
    }
  } else if (a && a.rotulo) {
    partes.push(h("span", { class: "mudo pequeno" }, "Sobre:"), h("span", { class: "selo aguardando" }, a.rotulo), h("button", { class: "btn leve mini", onclick: () => { S.alvo = null; desenharAlvo(); } }, "Limpar"));
  }
  box.replaceChildren(...partes.flat().filter(Boolean));
}

const STATUS_FB = { rascunho: "Anotado, não enviado", enviado: "Enviado", atendido: "Atendido" };

function desenharListaFeedback() {
  const c = S.cont, alvo = document.getElementById("l-lista");
  const lista = (c.feedback || []).slice().sort((a, b) => (a.status === "rascunho" ? 0 : 1) - (b.status === "rascunho" ? 0 : 1) || b.id - a.id);
  if (!lista.length) { alvo.replaceChildren(); alvo.classList.add("oculto"); return; }
  alvo.classList.remove("oculto");
  alvo.replaceChildren(h("h3", {}, "Ajustes"), h("div", { id: "lista-feedback" }, lista.map((f) => h("div", { class: `fb ${f.status}`, "data-fb": f.status },
    h("div", { class: "meta" }, h("span", {}, `v${f.versao_numero}`), f.cena != null ? h("span", {}, `· Cena ${f.cena + 1}`) : null, f.item && !String(f.item).startsWith("cena_") ? h("span", {}, `· ${f.item}`) : null,
      f.tempo_s != null ? h("button", { class: "tempo", onclick: () => saltar(f.tempo_s, f) }, tempo(f.tempo_s)) : null, f.categoria ? h("span", {}, `· ${f.categoria}`) : null,
      h("span", {}, `· ${f.status === "enviado" && f.job_craque ? `Com ${f.job_craque}` : STATUS_FB[f.status] || f.status}`),
      f.status === "rascunho" ? h("button", { class: "x", "aria-label": "Remover", title: "Remover", onclick: acao(async () => { await api("POST", `/api/producoes/${S.slug}/remover_feedback`, { id: f.id }); S.assinaturas.corpo = null; }) }, "×") : null),
    f.texto))));
}

function saltar(t, f) {
  const v = document.getElementById("video");
  if (v) { v.currentTime = t; v.pause(); return; }
  const a = document.getElementById("audio");
  if (a) {
    const d = S.cont.dados, tr = d.trechos && d.trechos.find((x) => x.item === f.item);
    if (tr) selecionarTrecho(tr);
    a.currentTime = t;
  }
}

function desenharTecnico() {
  const alvo = document.getElementById("l-tecnico");
  const corpo = h("div", {}, h("span", { class: "mudo pequeno" }, "Carregando…"));
  const ler = async () => {
    const d = await api("GET", `/api/producoes/${S.slug}/detalhes`);
    corpo.replaceChildren(h("div", { class: "mini mudo", style: "overflow-wrap:anywhere;margin:4px 0" }, d.pasta),
      d.jobs.length ? h("div", { style: "margin-top:8px" }, h("h3", {}, "Trabalhos"), d.jobs.slice(0, 10).map((j) => h("div", { class: "linha-flex mini", style: "margin-top:3px" }, h("span", { class: `selo ${j.status === "ok" ? "concluida" : j.status === "falhou" ? "falhou" : j.status === "rodando" ? "executando" : ""}` }, j.status), h("span", { style: "flex:1;min-width:120px" }, j.titulo), j.custo_usd != null ? h("span", { class: "num mudo" }, `US$ ${j.custo_usd.toFixed(2)}`) : null, h("button", { class: "btn leve mini", onclick: () => verLog(j.id) }, "Log")))) : null,
      h("div", { style: "margin-top:8px" }, h("h3", {}, "Histórico"), d.eventos.slice(0, 25).map((x) => h("div", { class: "evento" }, h("span", { class: "mudo" }, quando(x.criada_em)), x.texto))));
  };
  alvo.replaceChildren(h("details", { class: "dobra", id: "tecnico", ontoggle: (ev) => { if (ev.target.open) ler(); } }, h("summary", {}, "Logs e detalhes técnicos"), corpo));
}

rotear();
