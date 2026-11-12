"use strict";
/* Navegação principal, rotas das telas novas, estados com ícone e rótulo. As telas se registram em Corte.telas. */
const Corte = {
  telas: [], atual: null,
  registrar(padrao, tela) { this.telas.push({ padrao, tela }); },

  desenharNav() {
    const c = location.pathname;
    const item = (url, icone, texto, ativo, id, extra) => h("a", { class: "nav-item" + (ativo ? " ativo" : ""), href: url, id, "aria-current": ativo ? "page" : null, onclick: (e) => { e.preventDefault(); ir(url); } }, h("span", { "aria-hidden": "true" }, icone), texto, extra);
    Vivo.iniciar();
    trocar(document.getElementById("nav"), 
      h("a", { class: "nav-marca", href: "/", onclick: (e) => { e.preventDefault(); ir("/"); } }, h("span", { class: "nav-logo", "aria-hidden": "true" }, "▶"), "Ecossistema do Guilherme"),
      item("/", "▦", "Projetos", c === "/" || c.startsWith("/producao/") || c.startsWith("/estudio/") || c.startsWith("/editor/"), "nav-projetos"),
      item("/agentes", "◉", "Agentes", c.startsWith("/agentes"), "nav-agentes", Vivo.elNav()),
      item("/fluxos", "⛓", "Fluxos", c.startsWith("/fluxos"), "nav-fluxos"),
      ["localhost", "127.0.0.1"].includes(location.hostname) ? h("a", { class: "nav-item" + (c.startsWith("/painel") ? " ativo" : ""), href: "/painel", id: "nav-painel", "aria-current": c.startsWith("/painel") ? "page" : null, onclick: (e) => { e.preventDefault(); if (typeof PainelTela !== "undefined") PainelTela.ir("/painel"); else location.assign("/painel"); } }, h("span", { "aria-hidden": "true" }, "◫"), "Painel") : null,
      h("span", { class: "espaco" }), h("span", { class: "mini mudo", id: "nav-local" }, ["localhost", "127.0.0.1"].includes(location.hostname) ? "Local: só nesta máquina" : "Rede de casa, com senha"));
  },

  rotear(caminho) {
    if (this.atual && this.atual.sair) this.atual.sair();
    this.atual = null;
    for (const { padrao, tela } of this.telas) {
      const m = caminho.match(padrao);
      if (m) { this.atual = tela; tela.montar(m); return true; }
    }
    return false;
  },
  atualizar() { return this.atual && this.atual.atualizar ? this.atual.atualizar() : null; },

  linkEstudio(slug) {
    const url = `/estudio/${slug}`;
    return h("a", { class: "btn mini", href: url, "data-estudio": slug, onclick: (e) => { e.preventDefault(); e.stopPropagation(); ir(url); } }, "Abrir no Estúdio");
  },

  /* Envio de arquivo local. O corpo vai cru; quem confere se é imagem é o servidor. */
  botaoArquivo(rotulo, url, depois) {
    const entrada = h("input", { type: "file", accept: "image/png,image/jpeg,image/webp", class: "oculto", onchange: async (ev) => {
      const arq = ev.target.files[0];
      if (!arq) return;
      try {
        const r = await fetch(url + (url.includes("?") ? "&" : "?") + `nome=${encodeURIComponent(arq.name)}`, { method: "POST", body: arq });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error((d.erro || ["Falha no envio."]).join(" "));
        aviso("Arquivo enviado.");
        depois && depois(d);
      } catch (e) { aviso(e.message, true); }
      ev.target.value = "";
    } });
    return h("label", { class: "btn leve mini arquivo" }, rotulo, entrada);
  },
};

/* replaceChildren que aceita listas e ignora o que não existe, como a função h. */
function trocar(el, ...filhos) { el.replaceChildren(...filhos.flat(Infinity).filter((x) => x !== null && x !== undefined && x !== false)); }

const ICONES_ESTADO = {
  pendente: ["○", "Na espera"], aguardando_inicio: ["▷", "Aguarda você iniciar"], rodando: ["◐", "Em execução"], aguardando: ["❚❚", "Aguarda sua aprovação"],
  concluido: ["✓", "Concluído"], ignorado: ["–", "Fora do caminho"], falhou: ["✕", "Falhou"],
  trabalhando: ["◐", "Trabalhando"], fila: ["⏳", "Na fila"], espera_voce: ["❚❚", "Espera você"],
  ocioso: ["○", "Ocioso"], verificando: ["…", "Verificando"],  // PROG-016: só o Catálogo usa
};

function seloEstado(status, texto) {
  const [ic, padrao] = ICONES_ESTADO[status] || ["○", status];
  return h("span", { class: `estado ${status}` }, h("span", { class: "ic", "aria-hidden": "true" }, ic), texto || padrao);
}

/* PROG-006: quem trabalhou num job (Claude ou Codex), sempre em texto, e a nota do motivo.
   Um único componente para todas as telas. Devolve null quando não há o que mostrar (job antigo, comando, sem job).
   opcoes.interativo = false: sem botão (dentro de uma linha que já é botão); a explicação vai no title. */
const FRASE_CODEX = "Este trabalho rodou no Codex, a reserva usada quando o Claude esgota o limite.";
function seloMotor(job, opcoes = {}) {
  const motor = job && typeof job.motor === "string" ? job.motor.trim().toLowerCase() : "";
  if (!motor) return null;
  const nota = job.motor_nota && String(job.motor_nota).trim() ? String(job.motor_nota).trim() : null;
  const andando = job.status === "rodando" || job.status === "fila";
  const codex = motor === "codex";
  const nome = codex ? "Codex" : motor === "claude" ? "Claude" : "Motor não informado";
  const dica = codex ? (andando ? "O Claude estava no limite; este trabalho está rodando no Codex." : "O Claude estava no limite; este trabalho rodou no Codex.") : null;
  const interativo = opcoes.interativo !== false && codex;
  const conteudo = [codex ? h("span", { class: "ponto-motor", "aria-hidden": "true" }) : null, nome];
  const aria = `Motor: ${nome}.${codex ? ` ${nota || FRASE_CODEX}` : nota ? ` ${nota}` : ""}`;
  const raiz = h("span", { class: `selo-motor ${codex ? "codex" : motor === "claude" ? "claude" : "outro"}`, role: "group", "aria-label": aria });
  if (interativo) {
    const caixa = h("span", { class: "motor-dica mini", role: "note", hidden: true }, dica);
    const botao = h("button", { type: "button", class: "chip-motor", "aria-expanded": "false", title: dica, onclick: (e) => {
      e.stopPropagation();
      const abrir = caixa.hidden;
      caixa.hidden = !abrir;
      botao.setAttribute("aria-expanded", String(abrir));
    } }, conteudo);
    raiz.append(botao);
    if (nota || codex) raiz.append(h("span", { class: "motor-nota mini mudo" }, nota || FRASE_CODEX));
    raiz.append(caixa);
  } else {
    raiz.append(h("span", { class: "chip-motor", title: dica || undefined }, conteudo));
    if (nota || codex) raiz.append(h("span", { class: "motor-nota mini mudo" }, nota || FRASE_CODEX));
  }
  return raiz;
}

/* PROG-003: quem está trabalhando agora. Uma única consulta a cada 4 s (GET /api/agentes/ao-vivo) alimenta o selo do menu e a aba Ao vivo.
   Para quando a aba do navegador está oculta e consulta de novo ao voltar. O tempo vem em segundos do servidor; o navegador só soma o que
   passou desde que recebeu (Date.now()), sem interpretar datas, por causa do fuso do celular. */
const Vivo = {
  dados: null, recebido: 0, ultimoOk: 0, erro: null, redeDesde: 0, congeladoEm: 0, voltouEm: 0,
  ouvintes: new Set(), timer: null, buscando: false, iniciado: false, el: null,
  ouvir(fn) { this.ouvintes.add(fn); return () => this.ouvintes.delete(fn); },
  iniciar() {
    if (this.iniciado) return;
    this.iniciado = true;
    document.addEventListener("visibilitychange", () => { if (!document.hidden) this.buscar(); });
    this.buscar();
  },
  agendar() { clearTimeout(this.timer); if (document.hidden) return; this.timer = setTimeout(() => this.buscar(), 4000); },
  async buscar() {
    if (this.buscando) return;
    this.buscando = true;
    try {
      const d = await api("GET", "/api/agentes/ao-vivo");
      if (this.erro) this.voltouEm = Date.now();
      this.dados = d; this.recebido = Date.now(); this.ultimoOk = this.recebido; this.erro = null; this.redeDesde = 0; this.congeladoEm = 0;
    } catch (e) {
      const rede = e instanceof TypeError;  // fetch recusado: o servidor não respondeu
      if (!this.erro) { this.erro = { desde: Date.now(), msg: e.message }; this.congeladoEm = Date.now(); }
      this.erro.rede = rede;
      this.redeDesde = rede ? (this.redeDesde || Date.now()) : 0;
    } finally {
      this.buscando = false;
      this.desenharNav();
      this.ouvintes.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
      this.agendar();
    }
  },
  /* Segundos a mostrar: o que o servidor mandou mais o que passou desde que chegou; parado quando a tela está desatualizada. */
  seg(base) {
    if (base === null || base === undefined) return null;
    const ate = this.congeladoEm || Date.now();
    return Math.max(0, Math.floor(base + (ate - this.recebido) / 1000));
  },
  resumo() { return (this.dados && this.dados.resumo) || { trabalhando: 0, fila: 0, falhou: 0, espera_voce: 0 }; },
  textoResumo(r = this.resumo()) {
    return [[r.trabalhando, "trabalhando"], [r.fila, "na fila"], [r.falhou, "falhou"], [r.espera_voce, "espera você"]].filter(([n]) => n > 0).map(([n, t]) => `${n} ${t}`).join(" · ");
  },
  /* Marca curta para o menu e a aba: número de quem trabalha ou espera, ou ! quando algo falhou. */
  marca() {
    const r = this.resumo();
    if (r.falhou > 0) return "!";
    const n = r.trabalhando + r.fila + r.espera_voce;
    return n > 0 ? String(n) : "";
  },
  elNav() {
    if (!this.el) this.el = h("span", { class: "nav-selo-vivo", id: "nav-agentes-selo", "aria-live": "polite", "aria-atomic": "true" });
    this.desenharNav();
    return this.el;
  },
  desenharNav() {
    if (!this.el) return;
    const m = this.marca(), r = this.resumo();
    const leitura = m ? `${this.textoResumo(r)}` : "";
    const chave = `${m}|${leitura}`;
    if (this.el.dataset.chave === chave) return;
    this.el.dataset.chave = chave;
    this.el.classList.toggle("falhou", m === "!");
    this.el.classList.toggle("vazio", !m);
    trocar(this.el, m ? h("span", { class: "nav-selo-marca", "aria-hidden": "true" }, m) : null, m ? h("span", { class: "so-leitor" }, `Agentes: ${leitura}`) : null);
  },
};

/* "há 40 s", "há 2 min", "há 1 h 10 min". */
function duracao(s) {
  s = Math.max(0, Math.floor(Number(s) || 0));
  if (s < 60) return `${s} s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} min`;
  const hh = Math.floor(m / 60), r = m % 60;
  return r ? `${hh} h ${r} min` : `${hh} h`;
}

function dialogo(titulo, corpo, botoes, largura) {
  const d = h("dialog", { oncancel: () => fechar() });
  const fechar = () => { d.close(); d.remove(); };
  d.append(h("div", { class: "modal", style: largura ? `width:${largura}px` : "" }, h("div", { class: "linha-flex" }, h("h2", {}, titulo), h("span", { class: "espaco" }), h("button", { class: "btn leve mini", "aria-label": "Fechar", onclick: fechar }, "× Fechar")), corpo, botoes ? h("div", { class: "botoes" }, botoes(fechar)) : null));
  document.body.append(d);
  d.showModal();
  return { fechar, d };
}

/* Campo que só grava ao sair ou confirmar: o polling não pode apagar o que está sendo digitado. */
function numero(rotulo, valor, aoMudar, opcoes = {}) {
  const i = h("input", { type: "number", value: valor, step: opcoes.passo ?? 0.01, min: opcoes.min, max: opcoes.max, disabled: opcoes.desabilitado, id: opcoes.id, onchange: (e) => { const n = Number(e.target.value); if (!Number.isNaN(n)) aoMudar(n); }, oninput: opcoes.aoDigitar });
  return h("label", { class: "campo-num" }, h("span", {}, rotulo), i, opcoes.unidade ? h("em", {}, opcoes.unidade) : null);
}
