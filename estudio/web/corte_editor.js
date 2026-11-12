"use strict";
/* Editor de vídeo. O estado é o corte.json; toda alteração passa pelo servidor, que devolve a linha do tempo compilada. A prévia desenha
   exatamente essa compilação com o Compositor, o mesmo do export. Nada de cálculo de tempo paralelo aqui além do retorno visual durante um arraste. */
const Editor = {
  slug: null, v: null, est: null, comp: null, sel: null, f: 0, zoom: 0, tocando: false, desfazer: [], refazer: [], mostrandoSeguras: true, imagens: {}, videos: new Map(), salvando: false, pendente: null, token: 0,

  montar(m) {
    Object.assign(this, { slug: m[1], v: null, est: null, comp: null, sel: null, f: 0, zoom: 0, tocando: false, desfazer: [], refazer: [], imagens: {}, salvando: false, pendente: null, assin: {} });
    this.videos.forEach((el) => el.remove());
    this.videos = new Map();
    document.title = "Editor · Corte";
    trocar(app, h("div", { class: "editor", id: "editor" },
      h("header", { class: "barra", id: "ed-barra" }, h("span", { class: "mudo" }, "Carregando o corte…")),
      h("aside", { class: "ed-esq", id: "ed-esq" }),
      h("main", { class: "ed-palco", id: "ed-palco" },
        h("div", { class: "ed-canvas-caixa", id: "ed-caixa" }, h("canvas", { id: "ed-tela" }), h("div", { class: "seguras", id: "seguras" }, h("div", { class: "zona topo" }, "Interface do app"), h("div", { class: "zona base" }, "Interface do app"), h("div", { class: "faixa-lado" }))),
        h("div", { class: "ed-comandos", id: "ed-comandos" })),
      h("aside", { class: "ed-inspetor", id: "ed-inspetor" }),
      h("section", { class: "ed-timeline", id: "ed-timeline" })),
      h("audio", { id: "ed-audio", preload: "auto", class: "oculto" }), h("div", { id: "ed-videos", class: "oculto" }));
    this.tela = document.getElementById("ed-tela");
    this.ctx = this.tela.getContext("2d");
    this.audio = document.getElementById("ed-audio");
    this.ligarTeclado();
    this.ligarArrasteCanvas();
    this.carregar(new URLSearchParams(location.search).get("t"));
  },

  sair() {
    this.pausar();
    removeEventListener("keydown", this.teclado);
    clearInterval(this.relogioFontes);
  },

  async carregar(t) {
    const v = await api("GET", `/api/producoes/${this.slug}/corte`).catch((e) => { trocar(document.getElementById("ed-barra"), h("a", { class: "voltar", href: `/estudio/${this.slug}`, onclick: (ev) => { ev.preventDefault(); ir(`/estudio/${this.slug}`); } }, "← Estúdio"), h("span", {}, e.message)); });
    if (!v) return;
    await Compositor.iniciar("/fontes");
    this.aplicarVista(v);
    if (t != null) this.f = Math.min(this.comp.total_f - 1, Math.max(0, Math.round(Number(t) * this.comp.fps)));
    this.desenharTudo();
    this.mostrar(this.f);
    this.conferirFontes();
  },

  aplicarVista(v) {
    this.v = v;
    this.est = v.estado;
    this.comp = v.compilado;
    if (this.tela.width !== this.comp.w) { this.tela.width = this.comp.w; this.tela.height = this.comp.h; }
    document.getElementById("ed-caixa").classList.toggle("horizontal", this.comp.w > this.comp.h);
    this.prepararMidia();
  },

  /* Um <video> por segmento, cada um já parado no ponto dele: o corte entre cenas não espera busca. */
  prepararMidia() {
    const caixa = document.getElementById("ed-videos");
    const vivos = new Set();
    for (const s of this.comp.segmentos) {
      if (!s.fonte_sha) continue;
      vivos.add(s.cena);
      let el = this.videos.get(s.cena);
      const src = `/blob/${s.fonte_sha}?nome=clipe.mp4`;
      if (!el || el.dataset.src !== src) {
        if (el) el.remove();
        el = h("video", { muted: true, preload: "auto", playsInline: true });
        el.dataset.src = src;
        el.src = src;
        caixa.append(el);
        this.videos.set(s.cena, el);
      }
      if (s.midia && !this.imagens[s.midia.sha]) {
        const im = new Image();
        im.onload = () => { this.imagens[s.midia.sha] = im; this.mostrar(this.f); };
        im.src = `/blob/${s.midia.sha}?nome=${encodeURIComponent(s.midia.nome || "a.png")}`;
      }
    }
    this.videos.forEach((el, k) => { if (!vivos.has(k)) { el.remove(); this.videos.delete(k); } });
  },

  conferirFontes() {
    clearInterval(this.relogioFontes);
    if (!this.comp.fontes_faltando.length) return;
    api("POST", `/api/producoes/${this.slug}/corte_fontes`, {}).catch((e) => aviso(e.message, true));
    this.relogioFontes = setInterval(async () => {
      const v = await api("GET", `/api/producoes/${this.slug}/corte`).catch(() => null);
      if (!v || !app.querySelector("#editor")) return clearInterval(this.relogioFontes);
      this.est = this.pendente || this.est;
      this.comp = v.compilado;
      this.prepararMidia();
      this.desenharEsq();
      this.mostrar(this.f);
      if (!v.compilado.fontes_faltando.length) { clearInterval(this.relogioFontes); this.desenharTimeline(); aviso("Fontes prontas."); }
    }, 1500);
  },

  atualizar() {
    /* Polling só para o estado da exportação: o corte em si muda por aqui. */
    return api("GET", `/api/producoes/${this.slug}`).then((e) => {
      const job = (e.fila || []).find((j) => j.etapa === "video");
      const b = document.getElementById("exportar");
      if (b) { b.disabled = !!job; b.textContent = job ? (job.status === "fila" ? "Na fila…" : "Exportando…") : "⤓ Exportar"; }
      const vid = e.etapas.find((x) => x.id === "video");
      if (this.ultimoJob && !job) {
        this.ultimoJob = null;
        api("GET", `/api/producoes/${this.slug}/corte`).then((v) => { this.v.situacao = v.situacao; this.desenharBarra(); });
        if (vid.falha) aviso(`A exportação falhou: ${vid.falha.erro}`, true);
        else aviso(`Exportado: vídeo final v${vid.versao}. Ele entra em revisão.`);
      }
      if (job) this.ultimoJob = job.id;
    }).catch(() => {});
  },

  /* ---------- Salvamento: cada alteração grava na hora; se outra já está indo, a mais nova entra depois ---------- */
  alterar(fn, rotulo) {
    const antes = JSON.stringify(this.est);
    const novo = JSON.parse(antes);
    fn(novo);
    if (JSON.stringify(novo) === antes) return;
    this.desfazer.push(antes);
    if (this.desfazer.length > 200) this.desfazer.shift();
    this.refazer = [];
    this.est = novo;
    this.gravar(novo);
  },
  async gravar(estado) {
    this.pendente = estado;
    if (this.salvando) return;
    this.salvando = true;
    this.marcarSalvo("Salvando…");
    try {
      while (this.pendente) {
        const atual = this.pendente;
        this.pendente = null;
        const v = await api("POST", `/api/producoes/${this.slug}/corte_salvar`, { estado: atual, rev: this.est.rev });
        this.est.rev = v.estado.rev;
        if (this.pendente) { this.pendente.rev = v.estado.rev; continue; }
        const sel = this.sel;
        this.aplicarVista(v);
        this.sel = sel;
        this.f = Math.min(this.f, this.comp.total_f - 1);
        this.desenharTudo();
        this.mostrar(this.f);
        this.conferirFontes();
      }
      this.marcarSalvo("Salvo");
    } catch (e) {
      aviso(e.message, true);
      this.marcarSalvo("Não salvo");
      const v = await api("GET", `/api/producoes/${this.slug}/corte`).catch(() => null);
      if (v) { this.aplicarVista(v); this.desenharTudo(); this.mostrar(this.f); }
    } finally { this.salvando = false; }
  },
  marcarSalvo(t) { const m = document.getElementById("ed-salvo"); if (m) m.textContent = t; },
  voltar(pilhaA, pilhaB) {
    if (!pilhaA.length) return;
    pilhaB.push(JSON.stringify(this.est));
    const antigo = JSON.parse(pilhaA.pop());
    antigo.rev = this.est.rev;
    this.est = antigo;
    this.gravar(antigo);
    this.atualizarBotoesPilha();
  },
  atualizarBotoesPilha() {
    const a = document.getElementById("desfazer"), b = document.getElementById("refazer");
    if (a) a.disabled = !this.desfazer.length;
    if (b) b.disabled = !this.refazer.length;
  },

  /* ---------- Prévia ---------- */
  async mostrar(f) {
    if (!this.comp || !this.comp.total_f) return;
    this.f = f = Math.max(0, Math.min(this.comp.total_f - 1, Math.round(f)));
    this.atualizarCursor();
    const r = Compositor.resolver(this.comp, f);
    const el = this.videos.get(r.seg.cena);
    const token = ++this.token;
    if (el) {
      if (el.readyState < 1) await new Promise((ok) => el.addEventListener("loadedmetadata", ok, { once: true }));
      if (token !== this.token) return;
      if (Math.abs(el.currentTime - r.baseT) > 0.001) {
        const buscou = new Promise((ok) => el.addEventListener("seeked", ok, { once: true }));
        el.currentTime = r.baseT;
        await buscou;
        if (token !== this.token) return;
      }
      if (el.readyState < 2) await new Promise((ok) => el.addEventListener("canplay", ok, { once: true }));
      if (token !== this.token) return;
    }
    Compositor.desenhar(this.ctx, this.comp, r, el, this.imagens);
    this.tela.dataset.quadro = f;
    this.tela.dataset.pronto = "1";
  },
  tocar() {
    if (this.tocando) return this.pausar();
    if (this.comp.fontes_faltando.length) return aviso("Espere as fontes de imagem ficarem prontas.", true);
    const src = `/api/producoes/${this.slug}/corte/audio?a=${this.comp.assinatura.slice(0, 16)}`;
    if (this.audio.dataset.src !== src) { this.audio.dataset.src = src; this.audio.src = src; }
    if (this.f >= this.comp.total_f - 1) this.f = 0;
    this.audio.currentTime = this.f / this.comp.fps;
    this.tocando = true;
    this.desenharComandos();
    this.audio.play().catch((e) => { aviso(`Não foi possível tocar o áudio: ${e.message}`, true); this.pausar(); });
    this.segTocando = null;
    const passo = () => {
      if (!this.tocando) return;
      const t = this.audio.currentTime, f = Math.floor(t * this.comp.fps);
      if (f >= this.comp.total_f || this.audio.ended) { this.pausar(); this.mostrar(this.comp.total_f - 1); return; }
      this.f = f;
      this.atualizarCursor();
      const r = Compositor.resolver(this.comp, f), el = this.videos.get(r.seg.cena);
      if (el) {
        if (this.segTocando !== r.seg.cena) {
          this.videos.get(this.segTocando)?.pause();
          this.segTocando = r.seg.cena;
          el.currentTime = r.baseT;
          if (f - r.seg.f0 < r.seg.quadros_fonte) el.play().catch(() => {});
        } else if (f - r.seg.f0 >= r.seg.quadros_fonte - 1) el.pause();  // quadro congelado
        else if (Math.abs(el.currentTime - r.baseT) > 0.15) el.currentTime = r.baseT;
        Compositor.desenhar(this.ctx, this.comp, r, el, this.imagens);
      }
      this.rafTocar = requestAnimationFrame(passo);
    };
    passo();
  },
  pausar() {
    if (!this.tocando) { this.audio && this.audio.pause(); return; }
    this.tocando = false;
    this.audio.pause();
    cancelAnimationFrame(this.rafTocar);
    this.videos.forEach((el) => el.pause());
    this.desenharComandos();
    this.mostrar(this.f);
  },

  /* ---------- Teclado e arraste no canvas ---------- */
  ligarTeclado() {
    this.teclado = (e) => {
      if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      if (e.key === " ") { e.preventDefault(); this.tocar(); }
      else if (e.key === "ArrowRight") { e.preventDefault(); this.pausar(); this.mostrar(this.f + (e.shiftKey ? this.comp.fps : 1)); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); this.pausar(); this.mostrar(this.f - (e.shiftKey ? this.comp.fps : 1)); }
      else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") { e.preventDefault(); e.shiftKey ? this.voltar(this.refazer, this.desfazer) : this.voltar(this.desfazer, this.refazer); }
      else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") { e.preventDefault(); this.voltar(this.refazer, this.desfazer); }
    };
    addEventListener("keydown", this.teclado);
  },
  ligarArrasteCanvas() {
    const pos = (e) => { const r = this.tela.getBoundingClientRect(); return { x: (e.clientX - r.left) * this.comp.w / r.width, y: (e.clientY - r.top) * this.comp.h / r.height }; };
    let arr = null;
    this.tela.addEventListener("pointerdown", (e) => {
      if (!this.comp) return;
      this.pausar();
      const p = pos(e);
      const r = Compositor.resolver(this.comp, this.f);
      const leg = r.legendas.slice().reverse().find((l) => Math.abs(l.y - p.y) < 90 && Math.abs(l.x - p.x) < this.comp.w * 0.45);
      if (leg) {
        this.selecionar({ tipo: "legenda", id: leg.id });
        arr = { tipo: "legenda", id: leg.id, dx: leg.x - p.x, dy: leg.y - p.y, alvo: leg };
      } else if (r.seg.midia) {
        this.selecionar({ tipo: "cena", id: r.seg.cena });
        arr = { tipo: "midia", id: r.seg.cena, dx: r.seg.midia.x - p.x, dy: r.seg.midia.y - p.y, alvo: r.seg.midia };
      } else return;
      this.tela.setPointerCapture(e.pointerId);
    });
    this.tela.addEventListener("pointermove", (e) => {
      if (!arr) return;
      const p = pos(e);
      arr.x = Math.round(p.x + arr.dx); arr.y = Math.round(p.y + arr.dy);
      arr.alvo.x = arr.x; arr.alvo.y = arr.y;
      this.mostrar(this.f);
    });
    this.tela.addEventListener("pointerup", () => {
      const a = arr; arr = null;
      if (!a || a.x == null) return;
      this.alterar((n) => {
        const alvo = a.tipo === "legenda" ? n.legendas.itens.find((l) => l.id === a.id) : n.cenas.find((c) => c.id === a.id).midia;
        alvo.x = a.x; alvo.y = a.y;
        if (a.tipo === "legenda") alvo.manual = true;
      });
    });
  },

  /* ---------- Tela ---------- */
  desenharTudo() { this.desenharBarra(); this.desenharEsq(); this.desenharComandos(); this.desenharTimeline(); this.desenharInspetor(); this.atualizarBotoesPilha(); },
  desenharBarra() {
    const s = this.v.situacao;
    trocar(document.getElementById("ed-barra"), ...[
      h("a", { class: "voltar", href: `/estudio/${this.slug}`, onclick: (e) => { e.preventDefault(); ir(`/estudio/${this.slug}`); } }, "← Estúdio"),
      h("span", { class: "titulo" }, "Editar vídeo"), h("span", { class: "mini mudo num" }, this.slug),
      this.v.estilo_projeto ? h("span", { class: "selo", id: "ed-estilo", title: "Estilo deste projeto. Para trocar, volte ao Estúdio." }, `🎨 ${this.v.estilo_projeto.nome}`) : null,
      h("span", { class: "selo", id: "ed-salvo", "aria-live": "polite" }, this.v.salvo ? "Salvo" : "Sem edição ainda"),
      s ? h("span", { class: `selo ${s.em_dia ? "aprovada" : "aguardando"}`, id: "ed-situacao", title: s.motivo || "" }, s.em_dia ? "✓ Este corte já está no vídeo" : "✎ Corte alterado: nova revisão") : null,
      h("span", { class: "espaco" }),
      h("button", { class: "btn mini", id: "desfazer", onclick: () => this.voltar(this.desfazer, this.refazer), title: "Ctrl+Z" }, "↶ Desfazer"),
      h("button", { class: "btn mini", id: "refazer", onclick: () => this.voltar(this.refazer, this.desfazer), title: "Ctrl+Y" }, "↷ Refazer"),
      h("button", { class: "btn mini", id: "nova-versao", onclick: () => this.novaVersao() }, "＋ Nova versão de corte"),
      this.v.versoes.length ? h("select", { class: "seletor-versao", id: "versoes-corte", "aria-label": "Versões de corte", onchange: (e) => { if (e.target.value) this.restaurarVersao(Number(e.target.value)); } }, h("option", { value: "" }, `${this.v.versoes.length} ${this.v.versoes.length > 1 ? "versões" : "versão"} de corte`), this.v.versoes.map((x) => h("option", { value: x.numero }, `Restaurar v${x.numero} · ${quando(x.criada_em)}${x.nota ? ` · ${x.nota}` : ""}`))) : null,
      h("button", { class: "btn principal mini", id: "exportar", onclick: () => this.exportar() }, "⤓ Exportar")].filter(Boolean));
  },
  async novaVersao() {
    const r = await api("POST", `/api/producoes/${this.slug}/corte_versao`, {}).catch((e) => aviso(e.message, true));
    if (!r) return;
    aviso(r.novo ? `Versão de corte v${r.numero} guardada.` : `Nada mudou desde a v${r.numero}.`);
    const v = await api("GET", `/api/producoes/${this.slug}/corte`);
    this.aplicarVista(v); this.desenharBarra();
  },
  async restaurarVersao(n) {
    this.desfazer.push(JSON.stringify(this.est));
    const v = await api("POST", `/api/producoes/${this.slug}/corte_restaurar`, { numero: n, rev: this.est.rev }).catch((e) => aviso(e.message, true));
    if (v) { this.aplicarVista(v); this.desenharTudo(); this.mostrar(this.f); aviso(`Corte v${n} restaurado. Dá para desfazer.`); }
  },
  async exportar() {
    const alertas = this.comp.avisos.filter((a) => a.nivel === "alerta");
    const enviar = async (conf) => {
      const r = await api("POST", `/api/producoes/${this.slug}/corte_exportar`, { confirmado: conf });
      this.ultimoJob = r.job;
      aviso(r.novo ? "Exportação iniciada. Você pode fechar esta página." : "Esta exportação já estava em andamento.");
      this.atualizar();
    };
    const nota = "Quando terminar, o MP4 vira nova versão do vídeo final, precisa da sua revisão, e o Vini audita o render, como depois de todo render.";
    if (alertas.length) {
      dialogo("Antes de exportar", h("div", { id: "confirmar-export" }, h("p", { class: "pequeno", style: "margin:8px 0" }, "Este corte tem:"), h("ul", { class: "motivos" }, alertas.map((a) => h("li", {}, a.texto))), h("p", { class: "mini mudo", style: "margin-top:8px" }, nota)), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Voltar e ajustar"), h("button", { class: "btn principal", id: "exportar-assim", onclick: async () => { fechar(); await enviar(true).catch((e) => aviso(e.message, true)); } }, "Exportar assim mesmo")]);
    } else {
      dialogo("Exportar o corte", h("p", { class: "pequeno", id: "confirmar-export", style: "margin:10px 0" }, nota), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Cancelar"), h("button", { class: "btn principal", id: "exportar-assim", onclick: async () => { fechar(); await enviar(false).catch((e) => aviso(e.message, true)); } }, "Exportar")]);
    }
  },
  desenharEsq() {
    const v = this.v, c = this.comp, partes = [];
    if (v.faltam && v.faltam.length) partes.push(h("section", { class: "faixa velha", id: "so-mp4" }, h("b", {}, "Só o MP4 achatado. "), "Dá para aparar, ajustar o volume e pôr legendas. ", v.faltam.join(" ")));
    if (c.fontes_faltando.length) partes.push(h("section", { class: "faixa andando", id: "fontes-faltando" }, h("b", {}, "Preparando as fontes de imagem"), h("div", { class: "pequeno" }, `Faltam ${c.fontes_faltando.length} de ${c.segmentos.length} cenas. Cada cena é desenhada uma vez só.`)));
    if (v.conflitos.length) {
      const marcas = {};
      partes.push(h("section", { id: "conflitos" }, h("h3", {}, "Mudanças de agentes"), h("p", { class: "mini mudo", style: "margin:4px 0" }, "O corte continua usando o que já estava. Aplique só o que quiser. Legendas à mão e enquadramentos ficam."),
        v.conflitos.map((x) => { const box = h("input", { type: "checkbox", checked: x.aplicavel, disabled: !x.aplicavel, "data-conflito": x.id }); marcas[x.id] = box; return h("label", { class: `conflito ${x.ressincronizar ? "alerta" : ""}` }, box, h("span", { class: "pequeno" }, x.texto), x.tipo === "texto" ? h("span", { class: "mini" }, h("span", { class: "saiu" }, x.antes), " ", h("span", { class: "entrou" }, x.depois)) : null); }),
        v.conflitos.some((x) => x.aplicavel) ? h("button", { class: "btn principal mini", id: "aplicar-conflitos", style: "margin-top:6px", onclick: async () => {
          const ids = Object.entries(marcas).filter(([, b]) => b.checked).map(([i]) => i);
          const r = await api("POST", `/api/producoes/${this.slug}/corte_aplicar`, { ids, rev: this.est.rev }).catch((e) => aviso(e.message, true));
          if (!r) return;
          this.desfazer.push(JSON.stringify(this.est));
          this.aplicarVista(r); this.desenharTudo(); this.mostrar(this.f); this.conferirFontes();
          aviso(r.ressincronizar.length ? `Aplicado. Ressincronize: ${r.ressincronizar.join(", ")}.` : "Aplicado.");
        } }, "Aplicar marcadas") : h("button", { class: "btn mini", style: "margin-top:6px", onclick: async () => { const r = await api("POST", `/api/producoes/${this.slug}/corte_recomecar`, {}); this.aplicarVista(r); this.desenharTudo(); this.mostrar(0); this.conferirFontes(); } }, "Começar corte novo (guarda o atual)")));
    }
    partes.push(h("section", { id: "avisos-corte" }, h("h3", {}, c.avisos.length ? `Avisos (${c.avisos.length})` : "Avisos"), c.avisos.length ? c.avisos.map((a) => h("button", { class: `aviso-item ${a.nivel}`, "data-aviso": a.tipo, onclick: () => { if (a.cena) { const s = c.segmentos.find((x) => x.cena === a.cena); this.selecionar({ tipo: "cena", id: a.cena }); if (s) { this.pausar(); this.mostrar(s.f1 - 1); } } } }, h("span", { "aria-hidden": "true" }, a.nivel === "alerta" ? "⚠ " : "ⓘ "), a.texto)) : h("p", { class: "mini mudo", style: "margin-top:4px" }, "Nenhuma fala cortada nem sobreposição.")));
    partes.push(h("section", {}, h("h3", {}, "Legendas do projeto"), h("select", { class: "seletor-versao", id: "preset-legenda", "aria-label": "Estilo das legendas do projeto", style: "width:100%;margin-top:6px", onchange: (e) => this.alterar((n) => { n.legendas.preset = e.target.value; }) }, Object.entries(v.presets).map(([id, p]) => h("option", { value: id, selected: this.est.legendas.preset === id }, p.nome))), h("p", { class: "mini mudo", style: "margin-top:4px" }, v.presets[this.est.legendas.preset]?.detalhe || ""), h("button", { class: "btn mini", id: "nova-legenda", style: "margin-top:6px", onclick: () => this.novaLegenda() }, "＋ Legenda no cursor")));
    trocar(document.getElementById("ed-esq"), ...partes);
  },
  novaLegenda() {
    const r = Compositor.resolver(this.comp, this.f), t = this.f / this.comp.fps, id = `le-m-${Date.now().toString(36)}`;
    const rel = t - r.seg.ini;
    this.sel = { tipo: "legenda", id };
    this.alterar((n) => { n.legendas.itens.push({ id, cena: r.seg.cena, ini: +rel.toFixed(3), fim: +Math.min(rel + 2, r.seg.fim - r.seg.ini).toFixed(3), texto: "Nova legenda", x: this.comp.w / 2, y: this.comp.h > this.comp.w ? 1380 : this.comp.h - 170, estilo: n.legendas.preset !== "nenhum" ? n.legendas.preset : "caderno", manual: true }); });
  },
  desenharComandos() {
    const c = this.comp;
    const tc = (f) => { const s = f / c.fps; return `${tempo(s)}`; };
    const entrada = h("input", { id: "ed-tempo", class: "num", type: "number", step: "0.033", min: 0, max: c.total_s, value: (this.f / c.fps).toFixed(3), "aria-label": "Tempo em segundos", onchange: (e) => { this.pausar(); this.mostrar(Number(e.target.value) * c.fps); } });
    trocar(document.getElementById("ed-comandos"), 
      h("button", { class: "btn mini", id: "quadro-menos", title: "Quadro anterior (←)", onclick: () => { this.pausar(); this.mostrar(this.f - 1); } }, "◀ 1 quadro"),
      h("button", { class: "btn principal mini", id: "tocar", onclick: () => this.tocar() }, this.tocando ? "❚❚ Pausar" : "▶ Tocar"),
      h("button", { class: "btn mini", id: "quadro-mais", title: "Próximo quadro (→)", onclick: () => { this.pausar(); this.mostrar(this.f + 1); } }, "1 quadro ▶"),
      h("label", { class: "linha-flex mini" }, "Tempo", entrada, "s"), h("span", { class: "num mini", id: "ed-marca" }, `${tc(this.f)} / ${tc(c.total_f)}`), h("span", { class: "mini mudo num", id: "ed-quadro" }, `Quadro ${this.f + 1} de ${c.total_f}`),
      h("label", { class: "linha-flex mini" }, h("input", { type: "checkbox", id: "ver-seguras", checked: this.mostrandoSeguras, onchange: (e) => { this.mostrandoSeguras = e.target.checked; document.getElementById("seguras").classList.toggle("oculto", !e.target.checked); } }), "Áreas seguras"));
  },
  atualizarCursor() {
    const c = this.comp;
    if (!c) return;
    const m = document.getElementById("ed-marca"); if (m) m.textContent = `${tempo(this.f / c.fps)} / ${tempo(c.total_f / c.fps)}`;
    const q = document.getElementById("ed-quadro"); if (q) q.textContent = `Quadro ${this.f + 1} de ${c.total_f}`;
    const t = document.getElementById("ed-tempo"); if (t && document.activeElement !== t) t.value = (this.f / c.fps).toFixed(3);
    const cur = document.getElementById("cursor"); if (cur) cur.style.left = `${(this.f / c.fps) * this.escala()}px`;
  },
  escala() {
    if (!this.zoom) {
      const larg = document.getElementById("ed-timeline")?.clientWidth || 900;
      this.zoom = Math.max(4, (larg - 120) / Math.max(1, this.comp.total_s));
    }
    return this.zoom;
  },
  desenharTimeline() {
    const c = this.comp, e = this.escala(), largura = c.total_s * e + 40;
    const regua = h("div", { class: "regua", id: "regua", style: `width:${largura}px` });
    const passo = e > 60 ? 1 : e > 25 ? 2 : e > 10 ? 5 : 10;
    for (let t = 0; t <= c.total_s; t += passo) regua.append(h("span", { class: "marca-regua", style: `left:${t * e}px` }, tempoCurto(t)));
    const arrastaCursor = (ev) => {
      const r = regua.getBoundingClientRect();
      const mover = (x) => { this.pausar(); this.mostrar(((x - r.left) / e) * c.fps); };
      mover(ev.clientX);
      const m = (k) => mover(k.clientX);
      const u = () => { removeEventListener("pointermove", m); removeEventListener("pointerup", u); };
      addEventListener("pointermove", m); addEventListener("pointerup", u);
    };
    regua.addEventListener("pointerdown", arrastaCursor);
    const cenas = c.segmentos.map((s, i) => this.clipeCena(s, i, e));
    const narr = c.audio.map((a) => this.blocoAudio(a, e));
    const leg = c.legendas.map((l) => this.blocoLegenda(l, e));
    const faixas = h("div", { class: "faixas", style: `width:${largura}px` },
      h("div", { class: "faixa-t", id: "faixa-cenas" }, cenas), h("div", { class: "faixa-t audio", id: "faixa-narracao" }, narr), h("div", { class: "faixa-t legendas", id: "faixa-legendas" }, leg),
      h("div", { class: "cursor", id: "cursor", style: `left:${(this.f / c.fps) * e}px` }));
    const rolagem = document.querySelector(".tl-rolo")?.scrollLeft || 0;
    const rolo = h("div", { class: "tl-rolo" }, regua, faixas);
    trocar(document.getElementById("ed-timeline"), 
      h("div", { class: "tl-rotulos" }, h("div", { class: "tl-zoom" }, h("button", { class: "btn mini", id: "zoom-menos", "aria-label": "Diminuir zoom", onclick: () => { this.zoom = Math.max(3, e / 1.4); this.desenharTimeline(); } }, "−"), h("span", { class: "mini mudo" }, "Zoom"), h("button", { class: "btn mini", id: "zoom-mais", "aria-label": "Aumentar zoom", onclick: () => { this.zoom = Math.min(400, e * 1.4); this.desenharTimeline(); } }, "+")), h("div", { class: "tl-rotulo" }, "Cenas"), h("div", { class: "tl-rotulo" }, "Narração"), h("div", { class: "tl-rotulo" }, "Legendas")), rolo);
    rolo.scrollLeft = rolagem;
  },
  clipeCena(s, i, e) {
    const c = this.comp, cena = this.est.cenas.find((x) => x.id === s.cena);
    const dur = s.fim - s.ini;
    const reordena = this.v.operacoes.reordenar;
    const el = h("div", { class: `clipe${this.sel && this.sel.tipo === "cena" && this.sel.id === s.cena ? " sel" : ""}${s.midia ? " com-midia" : ""}${c.avisos.some((a) => a.cena === s.cena && a.nivel === "alerta") ? " alerta" : ""}`, "data-cena": s.cena, style: `left:${s.ini * e}px;width:${dur * e}px` },
      s.fonte_sha ? h("img", { src: `/quadro/${s.fonte_sha}?t=${(s.base_ini + Math.min(0.6 * dur, dur - 0.05)).toFixed(2)}&l=108`, alt: "", draggable: false, loading: "lazy" }) : null,
      h("span", { class: "clipe-txt" }, s.rotulo, ` · ${dur.toFixed(2)} s`),
      h("span", { class: "alca esq", "data-alca": "in", title: "Aparar o início" }), h("span", { class: "alca dir", "data-alca": "out", title: "Aparar o fim" }));
    el.addEventListener("pointerdown", (ev) => {
      ev.preventDefault();
      this.selecionar({ tipo: "cena", id: s.cena });
      const alca = ev.target.dataset.alca, x0 = ev.clientX;
      let delta = 0;
      el.setPointerCapture(ev.pointerId);
      const mover = (m) => {
        delta = (m.clientX - x0) / e;
        if (alca === "in") { el.style.left = `${(s.ini + Math.max(-cena.in, Math.min(delta, dur - 0.1))) * e}px`; el.style.width = `${(dur - Math.max(-cena.in, Math.min(delta, dur - 0.1))) * e}px`; }
        else if (alca === "out") el.style.width = `${Math.max(0.1, dur + delta) * e}px`;
        else if (reordena) { el.style.transform = `translateX(${m.clientX - x0}px)`; el.style.zIndex = 5; }
      };
      const soltar = () => {
        el.removeEventListener("pointermove", mover); el.removeEventListener("pointerup", soltar);
        if (Math.abs(delta) < 0.02) { this.pausar(); this.mostrar(((x0 - document.getElementById("regua").getBoundingClientRect().left) / e) * c.fps); return; }
        const quadro = 1 / c.fps;
        if (alca === "in") this.alterar((n) => { const k = n.cenas.find((x) => x.id === s.cena); k.in = +Math.max(0, Math.min(k.in + delta, k.out - quadro)).toFixed(3); });
        else if (alca === "out") this.definirDuracao(s.cena, dur + delta);
        else if (reordena) {
          const centro = s.ini + dur / 2 + delta;
          const outros = c.segmentos.filter((x) => x.cena !== s.cena);
          let pos = outros.findIndex((x) => (x.ini + x.fim) / 2 > centro);
          if (pos < 0) pos = outros.length;
          this.moverCena(s.cena, pos);
        }
      };
      el.addEventListener("pointermove", mover); el.addEventListener("pointerup", soltar);
    });
    return el;
  },
  moverCena(id, pos) {
    this.alterar((n) => { const i = n.cenas.findIndex((x) => x.id === id); const [k] = n.cenas.splice(i, 1); n.cenas.splice(pos, 0, k); });
    if (!this.salvando && !this.pendente) this.desenharTimeline();
  },
  definirDuracao(id, d) {
    this.alterar((n) => {
      const k = n.cenas.find((x) => x.id === id);
      const quadro = 1 / n.fps;
      d = Math.max(quadro, d);
      const cabe = k.fonte.dur - k.in;
      if (d <= cabe) { k.out = +(k.in + d).toFixed(3); k.congela = 0; }
      else { k.out = k.fonte.dur; k.congela = +(d - cabe).toFixed(3); }
    });
  },
  blocoAudio(a, e) {
    const n = this.est.narracao.itens.find((x) => x.id === a.id);
    const cortada = n && a.dur < n.dur - 0.02;
    return h("div", { class: `bloco-audio${this.sel && this.sel.tipo === "narracao" && this.sel.id === a.id ? " sel" : ""}${cortada ? " cortada" : ""}${a.vinculada ? "" : " solta"}`, "data-narracao": a.id, style: `left:${a.pos * e}px;width:${a.dur * e}px`, onclick: () => { this.selecionar({ tipo: "narracao", id: a.id }); } }, h("span", { class: "mini" }, (a.vinculada ? "🔗 " : "") + a.rotulo), cortada ? h("span", { class: "mini" }, ` ⚠ corta ${(n.dur - a.dur).toFixed(1)} s`) : null);
  },
  blocoLegenda(l, e) {
    const c = this.comp;
    const el = h("div", { class: `bloco-legenda${this.sel && this.sel.tipo === "legenda" && this.sel.id === l.id ? " sel" : ""}${l.manual ? " manual" : ""}`, "data-legenda": l.id, title: l.texto, style: `left:${l.ini * e}px;width:${Math.max(4, (l.fim - l.ini) * e)}px` }, h("span", { class: "mini" }, l.texto), h("span", { class: "alca esq", "data-alca": "ini" }), h("span", { class: "alca dir", "data-alca": "fim" }));
    el.addEventListener("pointerdown", (ev) => {
      ev.preventDefault();
      this.selecionar({ tipo: "legenda", id: l.id });
      const alca = ev.target.dataset.alca, x0 = ev.clientX;
      let delta = 0;
      el.setPointerCapture(ev.pointerId);
      const mover = (m) => {
        delta = (m.clientX - x0) / e;
        if (!alca) el.style.transform = `translateX(${delta * e}px)`;
        else if (alca === "fim") el.style.width = `${Math.max(4, (l.fim - l.ini + delta) * e)}px`;
        else { el.style.left = `${(l.ini + delta) * e}px`; el.style.width = `${Math.max(4, (l.fim - l.ini - delta) * e)}px`; }
      };
      const soltar = () => {
        el.removeEventListener("pointermove", mover); el.removeEventListener("pointerup", soltar);
        if (Math.abs(delta) < 0.02) return;
        this.alterar((n) => {
          const x = n.legendas.itens.find((k) => k.id === l.id);
          if (alca !== "fim") x.ini = +Math.max(0, x.ini + delta).toFixed(3);
          if (alca !== "ini") x.fim = +Math.max(x.ini + 1 / c.fps, x.fim + delta).toFixed(3);
          x.manual = true;
        });
      };
      el.addEventListener("pointermove", mover); el.addEventListener("pointerup", soltar);
    });
    return el;
  },
  selecionar(s) {
    this.sel = s;
    document.querySelectorAll(".clipe,.bloco-audio,.bloco-legenda").forEach((el) => {
      el.classList.toggle("sel", (s.tipo === "cena" && el.dataset.cena === s.id) || (s.tipo === "narracao" && el.dataset.narracao === s.id) || (s.tipo === "legenda" && el.dataset.legenda === s.id));
    });
    this.desenharInspetor();
  },
  desenharInspetor() {
    const alvo = document.getElementById("ed-inspetor"), s = this.sel;
    if (!s) { trocar(alvo, h("h3", {}, "Inspetor"), h("p", { class: "mudo pequeno", style: "margin-top:6px" }, "Selecione uma cena, uma fala ou uma legenda na linha do tempo. Arraste a legenda direto na imagem para mover.")); return; }
    if (s.tipo === "cena") return this.inspetorCena(alvo, s.id);
    if (s.tipo === "narracao") return this.inspetorNarracao(alvo, s.id);
    return this.inspetorLegenda(alvo, s.id);
  },
  inspetorCena(alvo, id) {
    const k = this.est.cenas.find((x) => x.id === id), seg = this.comp.segmentos.find((x) => x.cena === id);
    if (!k) return trocar(alvo);
    const alt = (fn) => this.alterar((n) => fn(n.cenas.find((x) => x.id === id)));
    const n = this.est.narracao.itens.find((x) => x.cena === id);
    const legs = this.est.legendas.itens.filter((x) => x.cena === id);
    const dur = k.out - k.in + (k.congela || 0);
    const efeito = h("div", { class: "efeito", id: "efeito-duracao" });
    const mostrarEfeito = (d) => {
      const partes = [];
      if (n) { const precisa = n.desloc - k.in + n.dur; partes.push(n.vinculada ? (d < precisa - 0.02 ? `⚠ A fala (${n.dur.toFixed(2)} s) perde ${(precisa - d).toFixed(2)} s do fim.` : "A fala cabe inteira.") : "A fala está solta: não acompanha a cena."); }
      const fora = legs.filter((l) => l.fim > d + 0.02);
      partes.push(legs.length ? (fora.length ? `⚠ ${fora.length} de ${legs.length} legendas ficam cortadas ou somem.` : `${legs.length} legendas continuam dentro da cena.`) : "Sem legendas nesta cena.");
      const sons = (k.sons || []).filter((x) => x.t >= k.in + d);
      if (sons.length) partes.push(`⚠ ${sons.length} efeito(s) sonoro(s) saem do corte.`);
      partes.push(`As cenas seguintes andam ${(d - dur >= 0 ? "+" : "")}${(d - dur).toFixed(2)} s.`);
      if (d > k.fonte.dur - k.in) partes.push(`O último quadro fica parado por ${(d - (k.fonte.dur - k.in)).toFixed(2)} s.`);
      trocar(efeito, h("b", { class: "mini" }, "Efeito nos itens ligados"), ...partes.map((t) => h("div", { class: "mini" }, t)));
    };
    mostrarEfeito(dur);
    const m = k.midia;
    const podeAsset = this.v.operacoes.trocar_asset;
    trocar(alvo, h("h3", {}, k.rotulo), k.fala ? h("p", { class: "mini mudo", style: "margin:4px 0 8px" }, k.fala) : null,
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Tempo"),
        numero("Duração", dur.toFixed(3), (v) => this.definirDuracao(id, v), { id: "cena-duracao", unidade: "s", min: 0.04, aoDigitar: (e) => { const v = Number(e.target.value); if (v > 0) mostrarEfeito(v); } }),
        numero("Aparar início", k.in.toFixed(3), (v) => alt((c) => { c.in = Math.max(0, Math.min(v, c.out - 1 / 30)); }), { id: "cena-in", unidade: "s", min: 0 }),
        numero("Fim na fonte", k.out.toFixed(3), (v) => alt((c) => { c.out = Math.max(c.in + 1 / 30, Math.min(v, c.fonte.dur)); }), { id: "cena-out", unidade: "s", min: 0, max: k.fonte.dur }),
        h("div", { class: "mini mudo" }, `Fonte: ${k.fonte.dur.toFixed(2)} s · ${k.fonte.tipo === "sketch" ? `desenho ${k.fonte.desenho}` : "recorte do vídeo"}`), efeito,
        n ? h("label", { class: "linha-flex mini", style: "margin-top:6px" }, h("input", { type: "checkbox", id: "cena-vinculada", checked: n.vinculada, onchange: (e) => this.alterar((x) => { const it = x.narracao.itens.find((z) => z.cena === id); it.vinculada = e.target.checked; it.inicio = e.target.checked ? null : +((seg ? seg.ini : 0) + it.desloc).toFixed(3); }) }), "A fala acompanha a cena") : null),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Enquadramento da cena"), numero("Escala", k.quadro.escala, (v) => alt((c) => { c.quadro.escala = v; }), { id: "cena-escala", passo: 0.01, min: 0.2, max: 5 }), numero("Posição X", k.quadro.x, (v) => alt((c) => { c.quadro.x = v; }), { id: "cena-x", passo: 1, unidade: "px" }), numero("Posição Y", k.quadro.y, (v) => alt((c) => { c.quadro.y = v; }), { id: "cena-y", passo: 1, unidade: "px" })),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Ilustração"), !podeAsset ? h("p", { class: "mini mudo" }, "Trocar asset exige o projeto por cenas.") : m ? h("div", {}, h("div", { class: "linha-flex" }, h("img", { class: "mini-asset", src: `/blob/${m.sha}?nome=${encodeURIComponent(m.nome)}`, alt: "" }), h("span", { class: "mini", id: "asset-nome" }, m.nome), h("span", { class: "espaco" }), h("button", { class: "btn leve mini", id: "asset-remover", onclick: () => alt((c) => { c.midia = null; }) }, "Remover")),
        h("select", { class: "seletor-versao", id: "asset-modo", style: "margin:6px 0;width:100%", onchange: (e) => alt((c) => { c.midia.modo = e.target.value; }) }, h("option", { value: "cobre", selected: m.modo === "cobre" }, "Substitui o desenho da cena"), h("option", { value: "sobre", selected: m.modo === "sobre" }, "Fica por cima do desenho")),
        numero("Escala", m.escala, (v) => alt((c) => { c.midia.escala = v; }), { id: "asset-escala", passo: 0.01, min: 0.05, max: 8 }), numero("Posição X", m.x, (v) => alt((c) => { c.midia.x = v; }), { id: "asset-x", passo: 1, unidade: "px" }), numero("Posição Y", m.y, (v) => alt((c) => { c.midia.y = v; }), { id: "asset-y", passo: 1, unidade: "px" }), h("button", { class: "btn mini", onclick: () => this.abrirGaleria(id) }, "Trocar")) : h("div", { class: "linha-flex" }, h("button", { class: "btn mini", id: "trocar-asset", onclick: () => this.abrirGaleria(id) }, "Trocar ilustração")), h("p", { class: "mini mudo", style: "margin-top:6px" }, "O desenho original continua no projeto. A troca fica só neste corte.")));
  },
  async abrirGaleria(id) {
    const usar = (it) => { const esc = Math.min(1, (this.comp.w * 0.9) / it.w, (this.comp.h * 0.7) / it.h); this.alterar((n) => { const k = n.cenas.find((x) => x.id === id); k.midia = { sha: it.sha, nome: it.nome, origem: it.origem, w: it.w, h: it.h, escala: k.midia ? k.midia.escala : +esc.toFixed(3), x: k.midia ? k.midia.x : this.comp.w / 2, y: k.midia ? k.midia.y : this.comp.h * 0.45, modo: k.midia ? k.midia.modo : "cobre" }; }); };
    const lista = (await api("GET", `/api/producoes/${this.slug}/corte/galeria`)).itens;
    const dl = dialogo("Escolher ilustração", h("div", { id: "galeria" }, h("div", { class: "linha-flex", style: "margin:8px 0" }, Corte.botaoArquivo("＋ Enviar arquivo local", `/api/producoes/${this.slug}/enviar/asset`, (it) => { dl.fechar(); usar(it); })), lista.length ? h("div", { class: "galeria-grade" }, lista.map((it) => h("button", { class: "galeria-item", "data-asset": it.nome, onclick: () => { dl.fechar(); usar(it); } }, h("img", { src: it.url, alt: it.nome, loading: "lazy" }), h("span", { class: "mini" }, it.nome), h("span", { class: "mini mudo" }, it.grupo)))) : h("p", { class: "mudo" }, "Este projeto ainda não tem componentes. Envie um arquivo local.")), null, 720);
  },
  inspetorNarracao(alvo, id) {
    const it = this.est.narracao.itens.find((x) => x.id === id);
    if (!it) return trocar(alvo);
    const alt = (fn) => this.alterar((n) => fn(n.narracao.itens.find((x) => x.id === id), n));
    trocar(alvo, h("h3", {}, "Narração"), h("p", { class: "mini mudo", style: "margin:4px 0 8px" }, `${it.arquivo} · ${it.dur.toFixed(2)} s`),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Volume"), numero("Toda a narração", this.est.narracao.volume_db, (v) => this.alterar((n) => { n.narracao.volume_db = v; }), { id: "narr-volume", passo: 0.5, unidade: "dB", min: -60, max: 12 }), numero("Só esta fala", it.volume_db, (v) => alt((x) => { x.volume_db = v; }), { id: "fala-volume", passo: 0.5, unidade: "dB", min: -60, max: 12 })),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Posição"), h("label", { class: "linha-flex mini" }, h("input", { type: "checkbox", id: "fala-vinculada", checked: it.vinculada, onchange: (e) => alt((x) => { x.vinculada = e.target.checked; const s = this.comp.segmentos.find((z) => z.cena === x.cena); x.inicio = e.target.checked ? null : +((s ? s.ini : 0) + x.desloc).toFixed(3); }) }), "Acompanha a cena"),
        it.vinculada ? numero("Começa depois do início da cena", it.desloc, (v) => alt((x) => { x.desloc = v; }), { id: "fala-desloc", unidade: "s", passo: 0.01 }) : numero("Começa em (linha do tempo)", it.inicio ?? 0, (v) => alt((x) => { x.inicio = v; }), { id: "fala-inicio", unidade: "s", min: 0 }),
        h("p", { class: "mini mudo" }, it.vinculada ? "Ao mover ou encurtar a cena, a fala vai junto e para quando a cena acaba." : "Solta: fica neste tempo mesmo se as cenas mudarem. Pode sobrepor outra fala.")));
  },
  inspetorLegenda(alvo, id) {
    const l = this.est.legendas.itens.find((x) => x.id === id);
    if (!l) return trocar(alvo);
    const alt = (fn) => this.alterar((n) => { const x = n.legendas.itens.find((k) => k.id === id); fn(x); x.manual = true; });
    trocar(alvo, h("h3", {}, "Legenda"), h("p", { class: "mini mudo", style: "margin:4px 0" }, l.manual ? "Editada à mão: não é refeita por um agente." : "Automática: vira manual ao editar."),
      h("label", { class: "campo", style: "margin-top:6px" }, h("span", {}, "Texto"), h("textarea", { id: "legenda-texto", value: l.texto, onchange: (e) => alt((x) => { x.texto = e.target.value; }) })),
      h("label", { class: "campo" }, h("span", {}, "Estilo"), h("select", { id: "legenda-estilo", onchange: (e) => alt((x) => { x.estilo = e.target.value; }) }, Object.entries(Compositor.ESTILOS).map(([k, e]) => h("option", { value: k, selected: l.estilo === k }, e.nome)))),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, "Posição"), numero("X", l.x, (v) => alt((x) => { x.x = v; }), { id: "legenda-x", passo: 1, unidade: "px" }), numero("Y", l.y, (v) => alt((x) => { x.y = v; }), { id: "legenda-y", passo: 1, unidade: "px" })),
      h("div", { class: "grupo-campos" }, h("b", { class: "mini" }, l.cena ? "Intervalo dentro da cena" : "Intervalo no vídeo"), numero("Início", l.ini, (v) => alt((x) => { x.ini = v; }), { id: "legenda-ini", unidade: "s", min: 0 }), numero("Fim", l.fim, (v) => alt((x) => { x.fim = v; }), { id: "legenda-fim", unidade: "s", min: 0 })),
      h("button", { class: "btn perigo mini", id: "legenda-remover", onclick: () => { this.sel = null; this.alterar((n) => { n.legendas.itens = n.legendas.itens.filter((x) => x.id !== id); }); } }, "Remover legenda"));
  },
};
Corte.registrar(/^\/editor\/([\w.-]+)/, Editor);
