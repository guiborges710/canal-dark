"use strict";
/* Editor de fluxos: canvas com zoom e pan, portas, conexões e inspetor. Mover nó é visual; reconectar muda a execução. As duas coisas persistem no rascunho. */
const Fluxos = {
  lista: null,
  montar(m) {
    this.ident = m[1] || null; this.d = null; this.g = null; this.sel = null; this.ligando = null; this.vista = { x: 20, y: 20, z: 0.7 };
    document.title = "Fluxos · Corte";
    if (!this.ident) {
      trocar(app, h("div", { class: "pagina", id: "fluxos-lista" }, h("div", { class: "topo-pagina" }, h("h1", { class: "marca" }, "Fluxos"), h("span", { class: "espaco" }), h("button", { class: "btn principal", id: "novo-fluxo", onclick: () => this.novo() }, "＋ Novo fluxo")), h("div", { id: "lista-fluxos" })));
      this.carregarLista();
      return;
    }
    trocar(app, h("div", { class: "fluxo-editor", id: "fluxo-editor" },
      h("header", { class: "barra", id: "fx-barra" }, h("span", { class: "mudo" }, "Carregando…")),
      h("aside", { class: "fx-paleta", id: "fx-paleta" }),
      h("main", { class: "fx-canvas", id: "fx-canvas", tabindex: 0 }, h("div", { class: "fx-mundo", id: "fx-mundo" }, h("svg", { id: "fx-svg-pl" })), h("div", { class: "fx-zoom", id: "fx-zoom" })),
      h("aside", { class: "fx-inspetor", id: "fx-inspetor" }),
      h("section", { class: "fx-problemas", id: "fx-problemas" })));
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.id = "fx-svg";
    document.getElementById("fx-svg-pl").replaceWith(svg);
    this.svg = svg;
    this.ligarCanvas();
    this.carregar();
  },
  sair() { clearTimeout(this.tSalvar); removeEventListener("keydown", this.tecla); },
  async carregarLista() {
    const r = await api("GET", "/api/fluxos");
    trocar(document.getElementById("lista-fluxos"), h("table", { class: "lista" }, h("thead", {}, h("tr", {}, ["Fluxo", "Publicada", "Rascunho", "Execuções ativas", "Nós"].map((t) => h("th", {}, t)))), h("tbody", {}, r.fluxos.map((f) => h("tr", { "data-fluxo": f.id, onclick: () => ir(`/fluxos/${f.id}`) }, h("td", { class: "titulo" }, f.nome), h("td", {}, f.publicada ? `✓ v${f.publicada} · ${quando(f.publicada_em)}` : "Nunca publicado"), h("td", {}, f.rascunho_alterado ? "✎ Com alterações" : "Igual ao publicado"), h("td", { class: "num" }, f.execucoes_ativas), h("td", { class: "num" }, f.nos))))));
  },
  novo() {
    const nome = h("input", { type: "text", id: "fluxo-nome" });
    const base = h("label", { class: "linha-flex mini", style: "margin-top:8px" }, h("input", { type: "checkbox", id: "fluxo-copia", checked: true }), "Começar como cópia do fluxo do canal");
    dialogo("Novo fluxo", h("div", {}, h("label", { class: "campo" }, h("span", {}, "Nome"), nome), base), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Cancelar"), h("button", { class: "btn principal", id: "fluxo-criar", onclick: acao(async () => { const r = await api("POST", "/api/fluxos", { nome: nome.value, copiar_de: base.querySelector("input").checked ? "canal" : null }); fechar(); ir(`/fluxos/${r.id}`); }) }, "Criar")]);
  },
  async carregar() {
    this.d = await api("GET", `/api/fluxos/${this.ident}`).catch((e) => { trocar(document.getElementById("fx-barra"), h("a", { class: "voltar", href: "/fluxos", onclick: (ev) => { ev.preventDefault(); ir("/fluxos"); } }, "← Fluxos"), h("span", {}, e.message)); return null; });
    if (!this.d) return;
    this.g = this.d.grafo; this.problemas = this.d.problemas; this.cat = this.d.catalogo;
    this.enquadrar();
    this.desenharTudo();
  },
  atualizar() {},
  enquadrar() {
    const c = document.getElementById("fx-canvas"), nos = this.g.nos;
    if (!nos.length) return;
    const xs = nos.map((n) => n.x), ys = nos.map((n) => n.y);
    const lg = Math.max(...xs) - Math.min(...xs) + 260, al = Math.max(...ys) - Math.min(...ys) + 150;
    const z = Math.max(0.28, Math.min(1, Math.min((c.clientWidth - 40) / lg, (c.clientHeight - 40) / al)));
    this.vista = { z, x: 20 - Math.min(...xs) * z, y: 20 - Math.min(...ys) * z };
    this.aplicarVista();
  },
  aplicarVista() {
    const v = this.vista;
    document.getElementById("fx-mundo").style.transform = `translate(${v.x}px, ${v.y}px) scale(${v.z})`;
    const z = document.getElementById("fx-zoom");
    if (z) trocar(z, h("button", { class: "btn mini", id: "fx-zoom-menos", "aria-label": "Diminuir zoom", onclick: () => this.mudarZoom(0.8) }, "−"), h("span", { class: "mini num", id: "fx-zoom-valor" }, `${Math.round(v.z * 100)}%`), h("button", { class: "btn mini", id: "fx-zoom-mais", "aria-label": "Aumentar zoom", onclick: () => this.mudarZoom(1.25) }, "+"), h("button", { class: "btn mini", id: "fx-enquadrar", onclick: () => this.enquadrar() }, "Enquadrar"));
  },
  mudarZoom(k, cx, cy) {
    const c = document.getElementById("fx-canvas").getBoundingClientRect(), v = this.vista;
    cx = cx ?? c.width / 2; cy = cy ?? c.height / 2;
    const z = Math.max(0.2, Math.min(2, v.z * k));
    v.x = cx - ((cx - v.x) * z) / v.z; v.y = cy - ((cy - v.y) * z) / v.z; v.z = z;
    this.aplicarVista();
  },
  ligarCanvas() {
    const c = document.getElementById("fx-canvas");
    c.addEventListener("wheel", (e) => { e.preventDefault(); const r = c.getBoundingClientRect(); this.mudarZoom(e.deltaY < 0 ? 1.1 : 0.9, e.clientX - r.left, e.clientY - r.top); }, { passive: false });
    c.addEventListener("pointerdown", (e) => {
      if (e.target !== c && e.target.id !== "fx-mundo" && e.target !== this.svg) return;
      this.sel = null; this.desenharSelecao();
      const x0 = e.clientX, y0 = e.clientY, vx = this.vista.x, vy = this.vista.y;
      c.setPointerCapture(e.pointerId);
      c.classList.add("arrastando");
      const m = (k) => { this.vista.x = vx + k.clientX - x0; this.vista.y = vy + k.clientY - y0; this.aplicarVista(); };
      const u = () => { c.removeEventListener("pointermove", m); c.removeEventListener("pointerup", u); c.classList.remove("arrastando"); };
      c.addEventListener("pointermove", m); c.addEventListener("pointerup", u);
    });
    c.addEventListener("dragover", (e) => e.preventDefault());
    c.addEventListener("drop", (e) => {
      e.preventDefault();
      const tipo = e.dataTransfer.getData("text/tipo");
      if (!tipo) return;
      const r = c.getBoundingClientRect(), v = this.vista;
      this.adicionar(tipo, (e.clientX - r.left - v.x) / v.z - 100, (e.clientY - r.top - v.y) / v.z - 40);
    });
    this.tecla = (e) => {
      if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      if ((e.key === "Delete" || e.key === "Backspace") && this.sel) { e.preventDefault(); this.sel.tipo === "no" ? this.removerNo(this.sel.id) : this.removerAresta(this.sel.id); }
    };
    addEventListener("keydown", this.tecla);
  },
  mudou() {
    clearTimeout(this.tSalvar);
    const m = document.getElementById("fx-salvo"); if (m) m.textContent = "Salvando…";
    this.tSalvar = setTimeout(() => this.salvar(), 250);
  },
  async salvar() {
    clearTimeout(this.tSalvar);
    const r = await api("POST", `/api/fluxos/${this.ident}/salvar`, { grafo: this.g }).catch((e) => { aviso(e.message, true); return null; });
    const m = document.getElementById("fx-salvo");
    if (!r) { if (m) m.textContent = "Não salvo"; return false; }
    this.problemas = r.problemas;
    if (m) m.textContent = "Rascunho salvo";
    this.desenharMarcas(); this.desenharProblemas(); this.desenharBarra();
    return true;
  },
  /* ---------- Operações ---------- */
  novoId(base) {
    let i = 1, id;
    do { id = `${base}_${i++}`; } while (this.g.nos.some((n) => n.id === id));
    return id;
  },
  adicionar(tipo, x, y) {
    const padrao = { agente: { tarefa: "livre" }, aprovacao: { material: "roteiro" }, render: { acao: "narracao", inicio: "manual" }, condicao: { campo: "estilo", valor: "sketch" } }[tipo] || {};
    const n = { id: this.novoId(tipo), tipo, nome: this.cat.tipos[tipo].nome, x: Math.round(x), y: Math.round(y), desativado: false, config: { ...padrao } };
    this.g.nos.push(n);
    this.sel = { tipo: "no", id: n.id };
    this.desenharGrafo(); this.desenharInspetor(); this.mudou();
  },
  duplicar(id) {
    const o = this.g.nos.find((n) => n.id === id);
    const n = { ...JSON.parse(JSON.stringify(o)), id: this.novoId(o.tipo), nome: `${o.nome} (cópia)`, x: o.x + 30, y: o.y + 90 };
    this.g.nos.push(n);
    this.sel = { tipo: "no", id: n.id };
    this.desenharGrafo(); this.desenharInspetor(); this.mudou();
  },
  removerNo(id) {
    this.g.nos = this.g.nos.filter((n) => n.id !== id);
    this.g.arestas = this.g.arestas.filter((a) => a.de !== id && a.para !== id);
    this.sel = null;
    this.desenharGrafo(); this.desenharInspetor(); this.mudou();
  },
  removerAresta(id) {
    this.g.arestas = this.g.arestas.filter((a) => a.id !== id);
    this.sel = null;
    this.desenharGrafo(); this.desenharInspetor(); this.mudou();
  },
  conectar(de, porta, para) {
    if (de === para) return;
    const id = `${de}${porta ? `.${porta}` : ""}->${para}`;
    if (this.g.arestas.some((a) => a.id === id)) return;
    this.g.arestas.push({ id, de, porta: porta || null, para, mapa: [] });
    this.sel = { tipo: "aresta", id };
    this.desenharGrafo(); this.desenharInspetor(); this.mudou();
  },
  async alternarNo(n) {
    if (n.desativado) { n.desativado = false; this.desenharGrafo(); this.desenharInspetor(); this.mudou(); return; }
    const r = await api("POST", `/api/fluxos/${this.ident}/impacto`, { grafo: this.g, no: n.id }).catch((e) => { aviso(e.message, true); return null; });
    if (!r) return;
    dialogo(`Desativar ${n.nome}`, h("div", { id: "impacto-desativar" }, h("p", { class: "pequeno", style: "margin:8px 0" }, r.entrega.length ? `Este nó entrega: ${r.entrega.join(", ")}. Desativado, o fluxo passa direto por ele.` : "O fluxo passa direto por este nó."),
      r.dependentes.length ? h("ul", { class: "motivos" }, r.dependentes.map((x) => h("li", { "data-dep": x.no }, `${x.nome} precisa de ${x.entrada_nome}: `, x.atendida_por ? `atendido por ${x.atendida_por}.` : x.opcional ? "é opcional, segue sem." : h("b", { style: "color:var(--erro)" }, "fica sem origem, e o fluxo não publica assim.")))) : h("p", { class: "mini mudo" }, "Nenhum nó depende do que ele entrega.")), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Cancelar"), h("button", { class: "btn principal", id: "confirmar-desativar-no", onclick: () => { n.desativado = true; fechar(); this.desenharGrafo(); this.desenharInspetor(); this.mudou(); } }, "Desativar nó")]);
  },
  /* ---------- Desenho ---------- */
  desenharTudo() { this.desenharBarra(); this.desenharPaleta(); this.desenharGrafo(); this.desenharInspetor(); this.desenharProblemas(); this.aplicarVista(); },
  desenharBarra() {
    const d = this.d, erros = (this.problemas || []).filter((p) => p.nivel === "erro").length;
    trocar(document.getElementById("fx-barra"), ...[
      h("a", { class: "voltar", href: "/fluxos", onclick: (e) => { e.preventDefault(); ir("/fluxos"); } }, "← Fluxos"),
      h("input", { class: "fx-nome", id: "fx-nome", value: d.nome, "aria-label": "Nome do fluxo", onchange: async (e) => { await api("POST", `/api/fluxos/${this.ident}/salvar`, { grafo: this.g, nome: e.target.value }).catch((x) => aviso(x.message, true)); d.nome = e.target.value; } }),
      h("span", { class: "selo", id: "fx-salvo" }, "Rascunho salvo"),
      d.versoes.length ? h("span", { class: "selo", id: "fx-publicada" }, `✓ Publicada: v${d.versoes[0].numero}`) : h("span", { class: "selo aguardando" }, "Nunca publicado"),
      erros ? h("span", { class: "selo falhou", id: "fx-erros" }, `✕ ${erros} ${erros > 1 ? "erros" : "erro"}`) : h("span", { class: "selo", id: "fx-erros" }, "✓ Sem erros"),
      h("span", { class: "espaco" }),
      d.versoes.length > 1 ? h("select", { class: "seletor-versao", id: "fx-versoes", onchange: async (e) => { if (!e.target.value) return; const r = await api("POST", `/api/fluxos/${this.ident}/restaurar`, { numero: Number(e.target.value) }).catch((x) => aviso(x.message, true)); if (r) { this.d = r; this.g = r.grafo; this.problemas = r.problemas; this.desenharTudo(); aviso(`Rascunho agora é igual à v${e.target.value}.`); } } }, h("option", { value: "" }, "Voltar rascunho para…"), d.versoes.map((v) => h("option", { value: v.numero }, `v${v.numero} · ${quando(v.publicada_em)}`))) : null,
      h("button", { class: "btn mini", id: "fx-testar", onclick: () => this.testar() }, "▶ Testar com um projeto"),
      h("button", { class: "btn principal mini", id: "fx-publicar", onclick: acao(async () => {
        await this.salvar();
        const r = await api("POST", `/api/fluxos/${this.ident}/publicar`, {});
        aviso(r.novo ? `Publicado: v${r.numero}. Execuções em andamento continuam na versão delas.` : `Nada mudou na execução: continua v${r.numero}.`);
        this.d = await api("GET", `/api/fluxos/${this.ident}`); this.desenharBarra();
      }) }, "Publicar versão")].filter(Boolean));
  },
  desenharPaleta() {
    trocar(document.getElementById("fx-paleta"), h("h3", {}, "Paleta"), h("p", { class: "mini mudo", style: "margin:4px 0 8px" }, "Arraste para o canvas ou clique."), Object.entries(this.cat.tipos).map(([id, t]) => h("button", { class: `paleta-item ${t.cor}`, draggable: true, "data-paleta": id, title: t.ajuda, ondragstart: (e) => e.dataTransfer.setData("text/tipo", id), onclick: () => { const c = document.getElementById("fx-canvas"), v = this.vista; this.adicionar(id, (c.clientWidth / 2 - v.x) / v.z - 100, (c.clientHeight / 2 - v.y) / v.z - 40); } }, h("span", { class: "ic", "aria-hidden": "true" }, { entrada: "✎", agente: "◉", aprovacao: "✓", condicao: "◇", juncao: "⋈", render: "▶", saida: "⏹" }[id]), h("span", {}, h("b", { class: "pequeno" }, t.nome), h("span", { class: "mini mudo", style: "display:block" }, t.ajuda)))));
  },
  portasSaida(n) {
    if (n.tipo === "saida") return [];
    if (n.tipo === "condicao") return ["sim", "nao"];
    return [null];
  },
  desenharGrafo() {
    const mundo = document.getElementById("fx-mundo");
    mundo.querySelectorAll(".fx-no").forEach((x) => x.remove());
    for (const n of this.g.nos) mundo.append(this.elementoNo(n));
    this.desenharArestas();
    this.desenharMarcas();
  },
  rotuloNo(n) {
    const c = n.config || {};
    if (n.tipo === "agente") { const a = this.d.agentes.find((x) => x.id === c.agente); return (a ? a.craque : c.agente || "Sem agente") + (c.agente_versao ? ` v${c.agente_versao}` : ""); }
    if (n.tipo === "aprovacao") return this.cat.materiais[c.material] || "Escolha o material";
    if (n.tipo === "render") return this.cat.acoes[c.acao]?.nome || "Escolha a ação";
    if (n.tipo === "condicao") return `${this.cat.condicoes[c.campo]?.nome || "?"} = ${c.valor || "?"}`;
    return this.cat.tipos[n.tipo].ajuda;
  },
  elementoNo(n) {
    const el = h("div", { class: `fx-no ${n.tipo}${n.desativado ? " desativado" : ""}${this.sel && this.sel.tipo === "no" && this.sel.id === n.id ? " sel" : ""}`, "data-no": n.id, style: `left:${n.x}px;top:${n.y}px` },
      n.tipo !== "entrada" ? h("span", { class: "porta entrada", "data-entrada": n.id, title: "Entrada" }) : null,
      h("div", { class: "fx-no-tipo mini" }, this.cat.tipos[n.tipo].nome, n.desativado ? " · desativado" : "", (n.config || {}).inicio === "manual" ? " · início manual" : ""),
      h("div", { class: "fx-no-nome" }, n.nome), h("div", { class: "mini mudo fx-no-sub" }, this.rotuloNo(n)), h("div", { class: "fx-no-marca", "data-marca": n.id }),
      this.portasSaida(n).map((p, i, todas) => h("span", { class: `porta saida ${p || ""}`, "data-saida": n.id, "data-porta": p || "", title: p === "sim" ? "Sim" : p === "nao" ? "Não" : "Saída", style: todas.length > 1 ? `top:${28 + i * 34}px` : "" }, p ? (p === "sim" ? "sim" : "não") : "")));
    el.addEventListener("pointerdown", (e) => {
      if (e.target.classList.contains("porta")) return this.iniciarLigacao(e, n);
      e.stopPropagation();
      this.sel = { tipo: "no", id: n.id };
      this.desenharSelecao();
      const x0 = e.clientX, y0 = e.clientY, nx = n.x, ny = n.y;
      let moveu = false;
      el.setPointerCapture(e.pointerId);
      const m = (k) => { n.x = Math.round(nx + (k.clientX - x0) / this.vista.z); n.y = Math.round(ny + (k.clientY - y0) / this.vista.z); moveu = true; el.style.left = `${n.x}px`; el.style.top = `${n.y}px`; this.desenharArestas(); };
      const u = () => { el.removeEventListener("pointermove", m); el.removeEventListener("pointerup", u); if (moveu) this.mudou(); };
      el.addEventListener("pointermove", m); el.addEventListener("pointerup", u);
    });
    return el;
  },
  pontoSaida(n, porta) {
    const ps = this.portasSaida(n), i = Math.max(0, ps.indexOf(porta || null));
    return [n.x + 200, n.y + (ps.length > 1 ? 34 + i * 34 : 42)];
  },
  iniciarLigacao(e, n) {
    e.stopPropagation(); e.preventDefault();
    const alvo = e.target;
    if (alvo.dataset.entrada) return;
    const porta = alvo.dataset.porta || null;
    const c = document.getElementById("fx-canvas").getBoundingClientRect();
    this.ligando = { de: n.id, porta, x: 0, y: 0 };
    const m = (k) => { const v = this.vista; this.ligando.x = (k.clientX - c.left - v.x) / v.z; this.ligando.y = (k.clientY - c.top - v.y) / v.z; this.desenharArestas(); };
    const u = (k) => {
      removeEventListener("pointermove", m); removeEventListener("pointerup", u);
      const sob = document.elementFromPoint(k.clientX, k.clientY);
      const no = sob && sob.closest(".fx-no");
      const liga = this.ligando; this.ligando = null;
      if (no && no.dataset.no !== liga.de && !no.classList.contains("entrada")) this.conectar(liga.de, liga.porta, no.dataset.no);
      else this.desenharArestas();
    };
    addEventListener("pointermove", m); addEventListener("pointerup", u);
    m(e);
  },
  desenharArestas() {
    const NS = "http://www.w3.org/2000/svg", svg = this.svg, nos = Object.fromEntries(this.g.nos.map((n) => [n.id, n]));
    const pts = this.g.nos.flatMap((n) => [[n.x, n.y], [n.x + 240, n.y + 120]]);
    const mx = Math.max(0, ...pts.map((p) => p[0])) + 400, my = Math.max(0, ...pts.map((p) => p[1])) + 400;
    svg.setAttribute("width", mx); svg.setAttribute("height", my);
    trocar(svg);
    const defs = document.createElementNS(NS, "defs");
    defs.innerHTML = '<marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#8b8e97"/></marker><marker id="seta-sel" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#FFC400"/></marker>';
    svg.append(defs);
    const curva = (x1, y1, x2, y2) => { const d = x2 < x1 ? 70 : Math.max(40, (x2 - x1) / 2); return `M${x1} ${y1} C${x1 + d} ${y1},${x2 - d} ${y2},${x2} ${y2}`; };
    for (const a of this.g.arestas) {
      const de = nos[a.de], para = nos[a.para];
      if (!de || !para) continue;
      const [x1, y1] = this.pontoSaida(de, a.porta);
      const sel = this.sel && this.sel.tipo === "aresta" && this.sel.id === a.id;
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", curva(x1, y1, para.x, para.y + 42));
      p.setAttribute("class", `fx-aresta${sel ? " sel" : ""}${(a.mapa || []).length ? " mapeada" : ""}`);
      p.setAttribute("marker-end", `url(#${sel ? "seta-sel" : "seta"})`);
      p.dataset.aresta = a.id;
      const larga = document.createElementNS(NS, "path");
      larga.setAttribute("d", p.getAttribute("d")); larga.setAttribute("class", "fx-aresta-alvo"); larga.dataset.alvoAresta = a.id;
      larga.addEventListener("pointerdown", (e) => { e.stopPropagation(); this.sel = { tipo: "aresta", id: a.id }; this.desenharSelecao(); });
      svg.append(p, larga);
    }
    if (this.ligando) {
      const [x1, y1] = this.pontoSaida(nos[this.ligando.de], this.ligando.porta);
      const p = document.createElementNS(NS, "path");
      p.setAttribute("d", curva(x1, y1, this.ligando.x, this.ligando.y)); p.setAttribute("class", "fx-aresta sel");
      svg.append(p);
    }
  },
  desenharSelecao() {
    document.querySelectorAll(".fx-no").forEach((el) => el.classList.toggle("sel", !!this.sel && this.sel.tipo === "no" && el.dataset.no === this.sel.id));
    this.desenharArestas(); this.desenharInspetor();
  },
  desenharMarcas() {
    document.querySelectorAll(".fx-no-marca").forEach((m) => {
      const ps = (this.problemas || []).filter((p) => p.no === m.dataset.marca);
      const erros = ps.filter((p) => p.nivel === "erro");
      m.closest(".fx-no").classList.toggle("com-erro", erros.length > 0);
      trocar(m, ...(ps.length ? [h("span", { class: `mini marca-erro ${erros.length ? "erro" : "aviso"}`, title: ps.map((p) => p.texto).join(" ") }, erros.length ? `✕ ${erros[0].texto}` : `ⓘ ${ps[0].texto}`)] : []));
    });
  },
  desenharProblemas() {
    const ps = this.problemas || [];
    trocar(document.getElementById("fx-problemas"), h("h3", {}, `Validação (${ps.filter((p) => p.nivel === "erro").length} erros, ${ps.filter((p) => p.nivel === "aviso").length} avisos)`), ps.length ? h("div", { class: "fx-problemas-lista" }, ps.map((p) => h("button", { class: `problema ${p.nivel}`, "data-problema-no": p.no || "", onclick: () => { if (p.no) { this.sel = { tipo: "no", id: p.no }; this.desenharSelecao(); this.focar(p.no); } } }, `${p.nivel === "erro" ? "✕" : "ⓘ"} ${p.no ? `${(this.g.nos.find((n) => n.id === p.no) || {}).nome || p.no}: ` : ""}${p.texto}`))) : h("p", { class: "mini mudo", style: "margin-top:4px" }, "Tudo certo para publicar."));
  },
  focar(id) {
    const n = this.g.nos.find((x) => x.id === id), c = document.getElementById("fx-canvas");
    if (!n) return;
    this.vista.x = c.clientWidth / 2 - (n.x + 100) * this.vista.z;
    this.vista.y = c.clientHeight / 2 - (n.y + 40) * this.vista.z;
    this.aplicarVista();
  },
  atualizarNo(n, fn) {
    fn(n);
    const el = document.querySelector(`.fx-no[data-no="${n.id}"]`);
    if (el) el.replaceWith(this.elementoNo(n));
    this.desenharArestas(); this.desenharMarcas(); this.mudou();
  },
  desenharInspetor() {
    const alvo = document.getElementById("fx-inspetor"), s = this.sel;
    if (!s) { trocar(alvo, h("h3", {}, "Inspetor"), h("p", { class: "mini mudo", style: "margin-top:6px" }, "Selecione um nó ou uma conexão. Arraste de uma porta (à direita do nó) até outro nó para ligar. Delete remove o que está selecionado.")); return; }
    if (s.tipo === "aresta") return this.inspetorAresta(alvo, s.id);
    const n = this.g.nos.find((x) => x.id === s.id);
    if (!n) return trocar(alvo);
    const c = n.config = n.config || {};
    const campos = [h("label", { class: "campo" }, h("span", {}, "Nome"), h("input", { type: "text", id: "no-nome", value: n.nome, onchange: (e) => this.atualizarNo(n, (x) => { x.nome = e.target.value; }) }))];
    const sel = (rotulo, id, valor, opcoes, fn) => h("label", { class: "campo" }, h("span", {}, rotulo), h("select", { id, onchange: (e) => { this.atualizarNo(n, (x) => fn(x, e.target.value)); this.desenharInspetor(); } }, opcoes.map(([v, t]) => h("option", { value: v, selected: valor === v }, t))));
    if (n.tipo === "agente") {
      campos.push(sel("Agente que executa", "no-agente", c.agente || "", [["", "Escolha…"], ...this.d.agentes.map((a) => [a.id, `${a.craque} (${a.id})${a.ativo ? "" : " · desativado"}`])], (x, v) => { x.config.agente = v; delete x.config.agente_versao; }));
      const ag = this.d.agentes.find((a) => a.id === c.agente);
      if (ag) campos.push(h("p", { class: "mini mudo" }, ag.descricao), h("a", { class: "btn leve mini", href: `/agentes/${ag.id}`, onclick: (e) => { e.preventDefault(); ir(`/agentes/${ag.id}`); } }, "Abrir agente →"), numero("Fixar versão do agente (vazio = a atual ao iniciar)", c.agente_versao || "", (v) => this.atualizarNo(n, (x) => { if (v) x.config.agente_versao = v; else delete x.config.agente_versao; }), { id: "no-agente-versao", passo: 1, min: 0 }));
      campos.push(sel("Tarefa", "no-tarefa", c.tarefa || "livre", Object.entries(this.cat.tarefas).map(([k, t]) => [k, t.nome]), (x, v) => { x.config.tarefa = v; }));
      campos.push(h("label", { class: "campo" }, h("span", {}, "Instruções deste nó"), h("textarea", { id: "no-instrucoes", value: c.instrucoes || "", onchange: (e) => this.atualizarNo(n, (x) => { x.config.instrucoes = e.target.value; }) })));
      campos.push(sel("Início", "no-inicio", c.inicio || "auto", [["auto", "Automático"], ["manual", "Espera eu iniciar"]], (x, v) => { x.config.inicio = v; }));
    } else if (n.tipo === "aprovacao") {
      campos.push(sel("O que esta aprovação decide", "no-material", c.material || "", Object.entries(this.cat.materiais), (x, v) => { x.config.material = v; }));
    } else if (n.tipo === "render") {
      campos.push(sel("Ação", "no-acao", c.acao || "", Object.entries(this.cat.acoes).map(([k, a]) => [k, a.nome]), (x, v) => { x.config.acao = v; }));
      campos.push(sel("Início", "no-inicio", c.inicio || "auto", [["auto", "Automático"], ["manual", "Espera eu iniciar"]], (x, v) => { x.config.inicio = v; }));
    } else if (n.tipo === "condicao") {
      campos.push(sel("Conferir", "no-campo", c.campo || "", Object.entries(this.cat.condicoes).map(([k, v]) => [k, v.nome]), (x, v) => { x.config.campo = v; x.config.valor = this.cat.condicoes[v].valores[0]; }));
      campos.push(sel("Sai por “sim” quando for", "no-valor", c.valor || "", (this.cat.condicoes[c.campo]?.valores || []).map((v) => [v, v]), (x, v) => { x.config.valor = v; }));
    }
    const ps = (this.problemas || []).filter((p) => p.no === n.id);
    trocar(alvo, h("div", { class: "linha-flex" }, h("h3", {}, this.cat.tipos[n.tipo].nome), h("span", { class: "espaco" }), h("span", { class: "mini mudo num" }, n.id)), ps.length ? h("ul", { class: "motivos" }, ps.map((p) => h("li", {}, p.texto))) : null, campos,
      h("div", { class: "linha-flex", style: "margin-top:12px" }, h("button", { class: "btn mini", id: "no-duplicar", onclick: () => this.duplicar(n.id) }, "⧉ Duplicar"), h("button", { class: "btn mini", id: "no-desativar", onclick: () => this.alternarNo(n) }, n.desativado ? "⏻ Reativar" : "⏻ Desativar"), h("button", { class: "btn perigo mini", id: "no-remover", onclick: () => this.removerNo(n.id) }, "✕ Remover")));
  },
  inspetorAresta(alvo, id) {
    const a = this.g.arestas.find((x) => x.id === id);
    if (!a) return trocar(alvo);
    const de = this.g.nos.find((n) => n.id === a.de), para = this.g.nos.find((n) => n.id === a.para);
    const arts = Object.entries(this.cat.artefatos);
    const redesenha = () => { this.desenharArestas(); this.inspetorAresta(alvo, id); this.mudou(); };
    trocar(alvo, h("h3", {}, "Conexão"), h("p", { class: "pequeno", style: "margin:6px 0" }, `${de?.nome || a.de}${a.porta ? ` (${a.porta === "nao" ? "não" : a.porta})` : ""} → ${para?.nome || a.para}`),
      h("h3", { style: "margin-top:12px" }, "Mapear campos"), h("p", { class: "mini mudo", style: "margin:4px 0" }, "Campos de mesmo nome passam sozinhos. Mapeie quando a saída tem outro nome na entrada, como cenas → roteiro do ilustrador."),
      (a.mapa || []).map((m, i) => h("div", { class: "mapa-linha", "data-mapa": i },
        h("select", { "aria-label": "Saída", "data-mapa-saida": i, onchange: (e) => { m.saida = e.target.value; redesenha(); } }, arts.map(([k, x]) => h("option", { value: k, selected: m.saida === k }, x.nome))), "→",
        h("select", { "aria-label": "Entrada", "data-mapa-entrada": i, onchange: (e) => { m.entrada = e.target.value; redesenha(); } }, arts.map(([k, x]) => h("option", { value: k, selected: m.entrada === k }, x.nome))),
        h("button", { class: "btn leve mini", "aria-label": "Remover mapeamento", onclick: () => { a.mapa.splice(i, 1); redesenha(); } }, "×"))),
      h("button", { class: "btn mini", id: "mapa-novo", style: "margin-top:6px", onclick: () => { (a.mapa = a.mapa || []).push({ saida: arts[1][0], entrada: arts[1][0] }); redesenha(); } }, "＋ Mapear campo"),
      h("div", { style: "margin-top:12px" }, h("button", { class: "btn perigo mini", id: "aresta-remover", onclick: () => this.removerAresta(id) }, "✕ Remover conexão")));
  },
  async testar() {
    const lista = await api("GET", "/api/producoes");
    const todos = [...lista.grupos.aguardando, ...lista.grupos.andamento, ...lista.grupos.arquivadas];
    const sel = h("select", { id: "ensaio-projeto" }, todos.map((p) => h("option", { value: p.slug }, p.titulo)));
    const res = h("div", { id: "ensaio-resultado" });
    dialogo("Testar com um projeto de exemplo", h("div", {}, h("p", { class: "mini mudo", style: "margin:6px 0" }, "Percorre o rascunho contra os arquivos do projeto: mostra a ordem, o que correria em paralelo, o que seria reaproveitado e o que falta. Nenhum agente é acionado aqui."), h("label", { class: "campo" }, h("span", {}, "Projeto"), sel), res), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Fechar"), h("button", { class: "btn principal", id: "ensaio-rodar", onclick: acao(async () => {
      const r = await api("POST", `/api/fluxos/${this.ident}/ensaiar`, { grafo: this.g, slug: sel.value });
      trocar(res, h("div", { class: "ensaio" }, r.passos.map((grupo, i) => h("div", { class: "ensaio-passo", "data-passo": i }, h("b", { class: "mini" }, `Passo ${i + 1}${grupo.filter((x) => x.estado === "ativo" && x.faria).length > 1 ? " · em paralelo" : ""}`), grupo.map((x) => h("div", { class: `mini ensaio-no ${x.estado === "ativo" ? "" : "mudo"}`, "data-ensaio-no": x.no }, h("b", {}, x.nome), ` · ${x.estado}`, x.faria ? ` · ${x.faria}` : "", x.porta ? ` · caminho ${x.porta === "nao" ? "não" : x.porta}` : "", x.faltam.length ? ` · falta no projeto: ${x.faltam.join(", ")}` : ""))))));
    }) }, "Percorrer")], 620);
  },
};
Corte.registrar(/^\/fluxos(?:\/([\w-]+))?\/?$/, Fluxos);
