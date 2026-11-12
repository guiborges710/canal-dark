"use strict";
/* Catálogo e editor de agentes. Tudo o que se salva aqui vai para .claude/agents/<id>.md. */
/* Aba "Ao vivo" (PROG-003): só leitura, alimentada por Vivo (corte_nav.js). Não mexe no Catálogo. */
const LIMITE_CARTOES = 10, ALERTA_LONGO_S = 900;
const AoVivo = {
  expandido: {}, tempos: {}, tick: null, assin: null,
  montar(corpo) {
    this.assin = null; this.tempos = {};
    trocar(corpo, h("section", { class: "ag-vivo", id: "ag-vivo" },
      h("h1", { class: "marca" }, "Agentes ao vivo"),
      h("div", { id: "ag-faixa" }),
      h("p", { class: "ag-resumo", id: "ag-resumo", "aria-live": "polite" }),
      h("div", { id: "ag-secoes" }),
      h("p", { class: "mini mudo", id: "ag-rodape" })));
    this.desenhar();
    this.passo();
    clearInterval(this.tick);
    this.tick = setInterval(() => this.passo(), 1000);
    if (!Vivo.recebido || Date.now() - Vivo.recebido > 2000) Vivo.buscar();
  },
  parar() { clearInterval(this.tick); this.tick = null; },

  chave(a, t) { return `${a.id}|${t.job_id ?? t.etapa_id}|${t.slug}|${t.estado}`; },
  /* O que o contador mostra: a base que veio do servidor mais o que passou aqui. */
  textoTempo(modo, base) {
    const s = Vivo.seg(base);
    if (s === null) return "";
    const velho = Vivo.erro ? " (pode ter mudado)" : "";
    if (modo === "trabalhando") return `há ${duracao(s)}${s >= ALERTA_LONGO_S ? ": mais que o normal" : ""}${velho}`;
    if (modo === "fila") return `aguarda há ${duracao(s)}${velho}`;
    if (modo === "espera_voce") return `aguardando você há ${duracao(s)}${velho}`;
    return `há ${duracao(s)}`;
  },
  tempo(modo, chave, base) {
    if (base === null || base === undefined) return null;
    this.tempos[chave] = base;
    const s = Vivo.seg(base);
    return h("span", { class: `ag-tempo${modo === "trabalhando" && s >= ALERTA_LONGO_S ? " longo" : ""}`, "data-chave": chave, "data-modo": modo }, this.textoTempo(modo, base));
  },

  botaoDestino(a, t) {
    const ficha = `/agentes/${a.id}`;
    if (t.origem === "teste_agente") return h("a", { class: "btn mini", href: ficha, "data-ver-teste": a.id, onclick: (e) => { e.preventDefault(); ir(ficha); } }, "Ver o teste");
    const url = `/estudio/${t.slug}${t.etapa_id ? `?etapa=${encodeURIComponent(t.etapa_id)}` : ""}`;
    const rotulo = t.estado === "falhou" ? "Ver o que houve" : t.estado === "espera_voce" ? "Abrir para decidir" : "Abrir no Estúdio";
    return h("a", { class: `btn mini${t.estado === "falhou" || t.estado === "espera_voce" ? " principal" : ""}`, href: url, "data-estudio": t.slug, onclick: (e) => {
      e.preventDefault();
      const b = e.currentTarget;
      if (b.getAttribute("aria-disabled")) return;
      b.setAttribute("aria-disabled", "true"); b.textContent = "Abrindo…";
      ir(url);
    } }, rotulo);
  },
  linha(a, t, varias) {
    const chave = this.chave(a, t);
    const base = t.estado === "trabalhando" ? t.segundos_na_tarefa : t.aguarda_s;
    const teste = t.origem === "teste_agente";
    const video = teste ? "Teste de agente" : (t.titulo_video || t.slug);
    const motor = seloMotor({ ...t, status: t.estado === "trabalhando" ? "rodando" : t.estado === "fila" ? "fila" : t.estado });
    return h("div", { class: `ag-trabalho ${t.estado}`, "data-job": t.job_id ?? t.etapa_id },
      varias ? h("div", {}, seloEstado(t.estado)) : null,
      h("div", { class: "ag-video" }, video, !teste && t.titulo_video && t.titulo_video !== t.slug ? h("span", { class: "mini mudo" }, ` · ${t.slug}`) : null),
      t.estado === "falhou"
        ? h("div", { class: "ag-erro pequeno" }, `Falhou em ${t.etapa_nome}: ${t.erro_curto || "sem mensagem registrada"}`)
        : h("div", { class: "pequeno" }, `Etapa: ${t.etapa_nome}`, t.estado === "fila" && t.posicao_fila ? ` · ${t.posicao_fila}º da fila` : ""),
      this.tempo(t.estado, chave, base),
      motor,
      h("div", { class: "linha-flex ag-acoes" }, this.botaoDestino(a, t), varias ? h("a", { class: "btn leve mini", href: `/agentes/${a.id}`, onclick: (e) => { e.preventDefault(); ir(`/agentes/${a.id}`); } }, "Ver ficha do agente") : null));
  },
  cartao(a) {
    const ts = a.trabalhos || [];
    const varias = ts.length > 1;
    const t0 = ts[0] || {};
    const nomeMotor = t0.motor === "codex" ? "Codex" : t0.motor === "claude" ? "Claude" : t0.motor ? "não informado" : "";
    const aria = [a.craque, (a.estado_texto || a.estado).toLowerCase(), varias ? `${ts.length} vídeos` : `vídeo ${t0.titulo_video || t0.slug || ""}, etapa ${t0.etapa_nome || ""}`].join(", ") + (nomeMotor ? `, motor ${nomeMotor}` : "") + ".";
    return h("article", { class: `ag-cartao ${a.estado}`, "data-agente-vivo": a.id, "data-estado": a.estado, "aria-label": aria },
      h("div", { class: "ag-cartao-topo" }, seloEstado(a.estado, a.estado_texto),
        a.ativo === false ? h("span", { class: "selo" }, a.estado === "trabalhando" ? "⏻ Desativado: termina o trabalho atual" : "⏻ Desativado") : null),
      h("div", { class: "ag-nome" }, h("b", {}, a.craque), h("span", { class: "mini mudo" }, ` ${a.id}`)),
      varias ? h("div", { class: "pequeno mudo" }, `${a.estado === "espera_voce" ? "Esperando você em" : a.estado === "falhou" ? "Com problema em" : "Trabalhando em"} ${ts.length} vídeos`) : null,
      ts.map((t) => this.linha(a, t, varias)),
      !varias ? h("div", { class: "linha-flex" }, h("a", { class: "btn leve mini", href: `/agentes/${a.id}`, "data-ficha": a.id, onclick: (e) => { e.preventDefault(); ir(`/agentes/${a.id}`); } }, "Ver ficha do agente")) : null);
  },
  secao(id, titulo, lista) {
    if (!lista.length) return null;
    const mostra = this.expandido[id] ? lista : lista.slice(0, LIMITE_CARTOES);
    const resto = lista.length - mostra.length;
    const soFila = lista.slice(LIMITE_CARTOES).every((a) => a.estado === "fila");
    return h("section", { class: `ag-secao ${id}`, id: `ag-sec-${id}` }, h("h2", { class: "ag-secao-titulo" }, `${titulo} `, h("span", { class: "mudo num" }, String(lista.length))),
      h("div", { class: "ag-grade" }, mostra.map((a) => this.cartao(a))),
      resto > 0 ? h("button", { class: "btn mini", "data-ver-todos": id, onclick: () => { this.expandido[id] = true; this.assin = null; this.desenhar(); } }, `+${resto} ${soFila ? "na fila" : "agentes"}, ver todos`) : null);
  },

  desenhar() {
    const corpo = document.getElementById("ag-secoes");
    if (!corpo) return;
    const d = Vivo.dados;
    const assin = JSON.stringify([d, !!Vivo.erro, this.expandido], (k, v) => ["gerado_em", "servidor_s", "segundos_na_tarefa", "aguarda_s", "terminou_ha_s"].includes(k) ? undefined : v);
    if (assin === this.assin) { this.atualizarBases(); this.passo(); return; }
    this.assin = assin;
    this.tempos = {};
    const abertoConcl = document.getElementById("ag-concluidos")?.open;
    let conteudo;
    if (!d) {
      conteudo = Vivo.erro
        ? h("div", { class: "ag-vazio", id: "ag-sem-dados" }, h("b", {}, "Ainda não foi possível ver quem está trabalhando."), h("p", { class: "mudo pequeno" }, "Assim que o Corte responder, esta tela se completa sozinha."))
        : h("div", { id: "ag-carregando" }, h("p", { class: "mudo" }, "Buscando quem está trabalhando…"), h("div", { class: "ag-grade" }, [1, 2, 3].map(() => h("div", { class: "ag-cartao esqueleto", "aria-hidden": "true" }))));
    } else {
      const ordem = { falhou: 0, espera_voce: 1, trabalhando: 2, fila: 3 };
      const ags = [...(d.agentes || [])].sort((x, y) => (ordem[x.estado] ?? 9) - (ordem[y.estado] ?? 9));
      const atencao = ags.filter((a) => a.estado === "falhou" || a.estado === "espera_voce");
      const agora = ags.filter((a) => a.estado === "trabalhando" || a.estado === "fila");
      const concl = d.concluidos_1h || [];
      conteudo = [
        !ags.length ? h("div", { class: "ag-vazio", id: "ag-vazio" }, h("b", {}, "Nenhum agente trabalhando agora."), h("p", { class: "mudo pequeno" }, "Quando uma produção rodar, ela aparece aqui sozinha."),
          h("div", { class: "linha-flex", style: "margin-top:8px" }, h("a", { class: "btn mini principal", href: "/", onclick: (e) => { e.preventDefault(); ir("/"); } }, "Ir para Projetos"), h("a", { class: "btn mini", href: "/agentes?aba=catalogo", onclick: (e) => { e.preventDefault(); ir("/agentes?aba=catalogo"); } }, "Ver o Catálogo"))) : null,
        this.secao("atencao", "Atenção", atencao), this.secao("agora", "Agora", agora),
        concl.length ? h("details", { class: "ag-concluidos", id: "ag-concluidos", open: !!abertoConcl }, h("summary", {}, `Concluídos na última hora (${concl.length})`),
          h("ul", { class: "ag-concl-lista" }, concl.map((c, i) => h("li", { class: "pequeno" }, h("span", { class: "estado concluido" }, h("span", { class: "ic", "aria-hidden": "true" }, "✓"), "Concluído"), ` ${c.craque}: ${c.etapa_nome}`, c.slug ? h("span", { class: "mudo" }, ` · ${c.slug}`) : null, " ", this.tempo("concluido", `c|${i}|${c.agente}|${c.slug}|${c.etapa_nome}`, c.terminou_ha_s), c.motor ? seloMotor({ motor: c.motor, status: "ok" }, { interativo: false }) : null)))) : null];
    }
    trocar(corpo, conteudo);
    this.passo();
  },
  /* Sem redesenhar: o servidor mandou novos segundos, o contador local parte deles. */
  atualizarBases() {
    const d = Vivo.dados;
    if (!d) return;
    (d.agentes || []).forEach((a) => (a.trabalhos || []).forEach((t) => { this.tempos[this.chave(a, t)] = t.estado === "trabalhando" ? t.segundos_na_tarefa : t.aguarda_s; }));
    (d.concluidos_1h || []).forEach((c, i) => { this.tempos[`c|${i}|${c.agente}|${c.slug}|${c.etapa_nome}`] = c.terminou_ha_s; });
  },

  faixa() {
    const alvo = document.getElementById("ag-faixa");
    if (!alvo) return;
    const agora = Date.now(), e = Vivo.erro;
    let tipo = "", texto = "", botao = false;
    if (e && e.rede && Vivo.redeDesde && agora - Vivo.redeDesde >= 30000) {
      tipo = "falha"; botao = true;
      texto = `O Corte não responde. Verifique se a janela do Corte ainda está aberta no computador${["localhost", "127.0.0.1"].includes(location.hostname) ? "" : " de casa"}.`;
    } else if (e) {
      tipo = "velha"; botao = true;
      texto = Vivo.ultimoOk
        ? `Sem atualização desde ${new Date(Vivo.ultimoOk).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })} (há ${duracao((agora - Vivo.ultimoOk) / 1000)}). Mostrando o último estado conhecido.`
        : "Não foi possível consultar quem está trabalhando. Vou tentar de novo.";
    } else if (Vivo.voltouEm && agora - Vivo.voltouEm < 3000) {
      tipo = "ok"; texto = "Atualizado.";
    } else if (Vivo.dados && Vivo.dados.frescor === "parcial") {
      tipo = "velha"; texto = "Parte das produções não pôde ser lida agora; a lista de quem espera você pode estar incompleta.";
    }
    const chave = `${tipo}|${texto}`;
    if (alvo.dataset.chave === chave) return;
    alvo.dataset.chave = chave;
    trocar(alvo, tipo ? h("div", { class: `faixa ${tipo === "ok" ? "andando" : tipo} ag-faixa-${tipo} linha-flex`, id: "ag-faixa-msg", role: tipo === "falha" ? "alert" : "status" }, h("span", {}, texto), botao ? h("button", { class: "btn mini", id: "ag-tentar", onclick: () => Vivo.buscar() }, "Tentar agora") : null) : null);
  },
  passo() {
    if (document.hidden) return;
    document.querySelectorAll("#ag-secoes .ag-tempo").forEach((el) => {
      const txt = this.textoTempo(el.dataset.modo, this.tempos[el.dataset.chave]);
      if (el.textContent !== txt) el.textContent = txt;
      el.classList.toggle("longo", el.dataset.modo === "trabalhando" && txt.includes("mais que o normal"));
    });
    this.faixa();
    const r = document.getElementById("ag-resumo");
    if (r) { const t = Vivo.dados ? (Vivo.textoResumo() || "Nenhum agente em atividade.") : ""; if (r.textContent !== t) r.textContent = t; }
    const ro = document.getElementById("ag-rodape");
    if (ro) {
      const s = Vivo.recebido ? Math.floor((Date.now() - Vivo.recebido) / 1000) : null;
      const t = s === null ? "" : s < 5 ? "Atualizado agora" : `Atualizado há ${duracao(s)}`;
      if (ro.textContent !== t) ro.textContent = t;
    }
  },
};

const Agentes = {
  lista: null, atual: null, filtro: "", aba: "ao-vivo", desouvir: null,
  montar(m) {
    this.lista = null; this.atual = null; this.ident = m[1] || null; this.editando = false; this.assinTeste = null;
    this.aba = (m[1] || new URLSearchParams(location.search).get("aba") === "catalogo") ? "catalogo" : "ao-vivo";
    document.title = this.aba === "catalogo" ? "Agentes · Corte" : "Agentes ao vivo · Corte";
    if (this.desouvir) this.desouvir();
    AoVivo.parar();
    this.desouvir = Vivo.ouvir(() => { this.marcarAbas(); if (this.aba === "ao-vivo") AoVivo.desenhar(); else this.marcarEstados(); });
    trocar(app, h("div", { class: "ag-pagina", id: "ag-pagina" }, this.desenharAbas(), h("div", { class: "ag-corpo", id: "ag-corpo", role: "tabpanel", "aria-labelledby": `aba-${this.aba}` })));
    const corpo = document.getElementById("ag-corpo");
    if (this.aba === "ao-vivo") { AoVivo.montar(corpo); return; }
    trocar(corpo, h("div", { class: "agentes", id: "agentes" }, h("aside", { class: "ag-lista", id: "ag-lista" }), h("main", { class: "ag-detalhe", id: "ag-detalhe" }, h("div", { class: "vazio-etapa" }, h("b", {}, "Escolha um agente"), "Ou crie um novo. O que você salvar vai para o arquivo nativo em .claude/agents."))));
    this.carregar();
  },
  sair() { AoVivo.parar(); if (this.desouvir) { this.desouvir(); this.desouvir = null; } },
  rotuloAbaVivo() {
    const m = Vivo.marca();
    return { texto: m ? `Ao vivo (${m})` : "Ao vivo", aria: m === "!" ? "Ao vivo: algo falhou" : m ? `Ao vivo: ${m} em atividade` : "Ao vivo" };
  },
  marcarAbas() {
    const b = document.getElementById("aba-ao-vivo");
    if (!b) return;
    const r = this.rotuloAbaVivo();
    if (b.textContent !== r.texto) b.textContent = r.texto;
    b.setAttribute("aria-label", r.aria);
  },
  desenharAbas() {
    const abas = [["ao-vivo", this.rotuloAbaVivo(), "/agentes"], ["catalogo", { texto: "Catálogo", aria: "Catálogo" }, "/agentes?aba=catalogo"]];
    const trocarPara = (i, foco) => { const [id, , url] = abas[i]; if (id === this.aba) return; ir(url); if (foco) document.getElementById(`aba-${id}`)?.focus(); };
    return h("div", { class: "ag-abas", role: "tablist", "aria-label": "Agentes" }, abas.map(([id, r], i) => h("button", { class: `aba${id === this.aba ? " ativa" : ""}`, id: `aba-${id}`, role: "tab", type: "button", "aria-selected": String(id === this.aba), "aria-controls": "ag-corpo", tabindex: id === this.aba ? "0" : "-1", "aria-label": r.aria,
      onclick: () => trocarPara(i, false),
      onkeydown: (e) => { if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); trocarPara((i + 1) % abas.length, true); } } }, r.texto)));
  },
  async carregar() {
    const r = await api("GET", "/api/agentes").catch(() => null);
    if (!document.getElementById("ag-lista")) return;  // trocou de aba ou de tela enquanto carregava
    if (!r) {
      trocar(document.getElementById("ag-lista"), h("div", { class: "faixa falha", id: "ag-erro-lista", role: "alert" }, h("p", {}, "Não consegui carregar os agentes. Recarregue a página; se continuar, veja se o Corte está aberto no computador."), h("button", { class: "btn mini", id: "ag-tentar-lista", onclick: () => this.carregar() }, "Tentar de novo")));
      return;
    }
    this.lista = r.agentes; this.opcoes = r.opcoes;
    this.desenharLista();
    if (this.ident) this.abrir(this.ident);
  },
  async atualizar() {
    if (!this.atual) return;
    const pendente = (this.atual.testes || []).some((t) => t.status === "fila");
    if (!pendente) return;
    const d = await api("GET", `/api/agentes/${this.atual.id}`);
    if (this.atual && d.id === this.atual.id) { this.atual.testes = d.testes; this.desenharTestes(); }
  },
  /* PROG-016: estado de cada agente do Catálogo, cruzado com a mesma consulta da aba Ao vivo (Vivo.dados).
     Quem não está em Vivo.dados.agentes está ocioso; antes da primeira resposta não se sabe, então "verificando". */
  estadoDe(id) {
    const d = Vivo.dados;
    if (!d) return { estado: "verificando", detalhe: "", aria: "Verificando" };
    const a = (d.agentes || []).find((x) => x.id === id);
    if (!a) return { estado: "ocioso", detalhe: "", aria: "Ocioso" };
    const ts = a.trabalhos || [], t = ts[0] || {};
    const video = t.origem === "teste_agente" ? "Teste de agente" : (t.titulo_video || t.slug || "");
    const mais = ts.length > 1 ? ` · +${ts.length - 1}` : "";
    let detalhe = "";
    if (a.estado === "trabalhando") {
      const s = Vivo.seg(t.segundos_na_tarefa);
      detalhe = [video, t.etapa_nome, s === null ? null : `há ${duracao(s)}`].filter(Boolean).join(" · ") + mais;
    } else if (a.estado === "falhou") detalhe = `${video} · falhou em ${t.etapa_nome || "uma etapa"}${mais}`;
    else detalhe = [video, t.etapa_nome].filter(Boolean).join(" · ") + mais;
    const rotulo = a.estado_texto || (ICONES_ESTADO[a.estado] || [, a.estado])[1];
    return { estado: a.estado, texto: rotulo, detalhe, aria: `${rotulo}${video ? `, vídeo ${video}` : ""}${t.etapa_nome ? `, etapa ${t.etapa_nome}` : ""}` };
  },
  /* Só atualiza selos, detalhes e rodapé no lugar: nunca refaz a lista (busca, rolagem e edição ficam como estão). */
  marcarEstados() {
    const lista = document.getElementById("ag-lista");
    if (!lista || !this.lista) return;
    let ativos = 0;
    lista.querySelectorAll(".ag-item[data-agente]").forEach((item) => {
      const id = item.dataset.agente, e = this.estadoDe(id);
      if (e.estado !== "ocioso" && e.estado !== "verificando") ativos++;
      const selo = item.querySelector("[data-selo]"), det = item.querySelector("[data-detalhe]");
      const chave = `${e.estado}|${e.texto || ""}`;
      if (selo && selo.dataset.chave !== chave) { selo.dataset.chave = chave; trocar(selo, seloEstado(e.estado, e.texto)); }
      if (det) { if (det.textContent !== e.detalhe) det.textContent = e.detalhe; det.hidden = !e.detalhe; }
      const nome = item.querySelector("b")?.textContent || id;
      const aria = `${nome}, ${e.aria}`;
      if (item.getAttribute("aria-label") !== aria) item.setAttribute("aria-label", aria);
    });
    const ro = document.getElementById("ag-estado-rodape");
    if (!ro) return;
    let t = "";
    if (Vivo.erro) t = "(desatualizado) Não consegui atualizar os estados. Tentando de novo a cada poucos segundos.";
    else if (Vivo.dados && !ativos) t = "Ninguém trabalhando agora. Para acompanhar quem estiver em ação, use a aba Ao vivo.";
    if (ro.textContent !== t) ro.textContent = t;
  },
  desenharLista() {
    const f = this.filtro.toLowerCase();
    const visiveis = this.lista.filter((a) => !f || a.id.includes(f) || a.descricao.toLowerCase().includes(f));
    trocar(document.getElementById("ag-lista"),
      h("div", { class: "linha-flex" }, h("h1", { class: "marca" }, "Agentes"), h("span", { class: "espaco" }), h("button", { class: "btn principal mini", id: "novo-agente", onclick: () => this.novo() }, "＋ Novo")),
      h("input", { class: "busca", type: "search", id: "busca-agente", style: "margin-top:8px", placeholder: "Buscar", value: this.filtro, oninput: (e) => { this.filtro = e.target.value; this.desenharLista(); document.getElementById("busca-agente").focus(); } }),
      h("p", { class: "mini mudo" }, `${this.lista.length} agentes em .claude/agents`),
      h("div", {}, visiveis.map((a) => h("a", { class: `ag-item${this.atual && this.atual.id === a.id ? " ativo" : ""}${a.ativo ? "" : " parado"}`, href: `/agentes/${a.id}`, "data-agente": a.id, onclick: (e) => { e.preventDefault(); history.pushState({}, "", `/agentes/${a.id}`); this.abrir(a.id); } },
        h("span", { class: "linha-flex ag-item-topo" }, h("b", {}, a.craque), h("span", { class: "mini mudo num" }, `v${a.versao}`), h("span", { class: "espaco" }), a.ativo ? null : h("span", { class: "selo" }, "⏻ Desativado"), h("span", { class: "ag-selo", "data-selo": "" })),
        h("span", { class: "mini mudo" }, a.id), h("span", { class: "mini ag-desc" }, a.descricao),
        h("span", { class: "mini ag-job", "data-detalhe": "", hidden: true }),
        a.usos.length ? h("span", { class: "mini" }, `⛓ ${a.usos.join(", ")}`) : h("span", { class: "mini mudo" }, "Fora dos fluxos")))),
      !visiveis.length ? h("p", { class: "pequeno mudo", id: "ag-lista-vazia" }, this.lista.length ? "Nenhum agente encontrado. Limpe a busca para ver todos." : "Nenhum agente cadastrado ainda.") : null,
      h("p", { class: "mini mudo", id: "ag-estado-rodape", "aria-live": "polite" }));
    this.marcarEstados();
  },
  async abrir(id) {
    this.atual = await api("GET", `/api/agentes/${id}`).catch((e) => { aviso(e.message, true); return null; });
    if (!this.atual || !document.getElementById("ag-detalhe")) return;
    this.desenharLista();
    this.desenharDetalhe();
  },
  novo() {
    this.atual = null;
    this.desenharForm({ id: "", nome: "", descricao: "", ferramentas: ["Read", "Write"], modelo: "sonnet", instrucoes: "", contrato: { entradas: [], saidas: [] } }, true);
  },
  desenharForm(a, novo) {
    const alvo = document.getElementById("ag-detalhe");
    const op = this.opcoes;
    const ident = h("input", { type: "text", id: "ag-id", value: a.id, placeholder: "ex.: neymar-roteirista-curto" });
    const desc = h("textarea", { id: "ag-descricao", value: a.descricao, style: "min-height:64px" });
    const inst = h("textarea", { id: "ag-instrucoes", value: a.instrucoes, class: "codigo", style: "min-height:260px" });
    const ent = h("input", { type: "text", id: "ag-entradas", value: (a.contrato.entradas || []).join(", ") });
    const sai = h("input", { type: "text", id: "ag-saidas", value: (a.contrato.saidas || []).join(", ") });
    const modelo = h("select", { id: "ag-modelo" }, h("option", { value: "" }, "Herdar da sessão"), op.modelos.map((m) => h("option", { value: m, selected: a.modelo === m }, m)));
    const marcas = op.ferramentas.map((f) => ({ f, box: h("input", { type: "checkbox", checked: a.ferramentas.includes(f), "data-ferramenta": f }) }));
    const pegar = () => ({ id: ident.value.trim(), descricao: desc.value, instrucoes: inst.value, modelo: modelo.value, ferramentas: marcas.filter((x) => x.box.checked).map((x) => x.f), contrato: { entradas: ent.value.split(",").map((x) => x.trim()).filter(Boolean), saidas: sai.value.split(",").map((x) => x.trim()).filter(Boolean) } });
    const usos = a.usos || [];
    const conteudo = [
      h("div", { class: "linha-flex" }, h("h2", {}, novo ? "Novo agente" : "Editar agente"), h("span", { class: "espaco" }), !novo ? h("button", { class: "btn mini", onclick: () => this.desenharDetalhe() }, "Cancelar") : null,
        h("button", { class: "btn principal mini", id: "ag-salvar", onclick: acao(async () => {
          const corpo = pegar();
          const d = novo ? await api("POST", "/api/agentes", corpo) : await api("POST", `/api/agentes/${a.id}/salvar`, { ...corpo, versao_vista: a.versao });
          aviso(`Salvo em .claude/agents/${d.id}.md (v${d.versao}).`);
          history.replaceState({}, "", `/agentes/${d.id}`);
          this.atual = d; this.ident = d.id;
          const r = await api("GET", "/api/agentes"); this.lista = r.agentes; this.opcoes = r.opcoes;
          this.desenharLista(); this.desenharDetalhe();
        }) }, "Salvar")),
      usos.length ? h("div", { class: "faixa velha pequeno", id: "ag-aviso-usos", style: "margin-top:8px" }, h("b", {}, "Quem usa este agente: "), usos.map((u) => `${u.fluxo_nome} (${u.origem}, nó ${u.no_nome})`).join("; "), ". Execuções em andamento continuam com a versão com que começaram; as próximas pegam esta.") : null,
      h("label", { class: "campo" }, h("span", {}, "Nome (identificador e nome do arquivo)"), ident),
      h("label", { class: "campo" }, h("span", {}, "Descrição: é por ela que o Claude Code decide quando usar"), desc),
      h("div", { class: "campo" }, h("span", {}, "Ferramentas autorizadas"), h("div", { class: "marcas" }, marcas.map((x) => h("label", { class: "marca-ferramenta" }, x.box, x.f)))),
      h("label", { class: "campo" }, h("span", {}, "Modelo"), modelo),
      h("div", { class: "linha-flex", style: "align-items:flex-start" }, h("label", { class: "campo", style: "flex:1" }, h("span", {}, "Entradas (com ? é opcional)"), ent), h("label", { class: "campo", style: "flex:1" }, h("span", {}, "Saídas"), sai)),
      h("p", { class: "mini mudo", style: "margin-top:3px" }, "Campos conhecidos pelo fluxo: notas, angulo, roteiro, direcao_viral, revisao, componentes, cenas, metadados, auditoria_texto, narracao, video, auditoria_final, thumbnail, briefing."),
      h("label", { class: "campo" }, h("span", {}, "Instruções"), inst)];
    trocar(alvo, h("div", { class: "folha-agente" }, conteudo));
  },
  desenharDetalhe() {
    const a = this.atual, alvo = document.getElementById("ag-detalhe");
    trocar(alvo, h("div", { class: "folha-agente" },
      h("div", { class: "linha-flex" }, h("h2", { id: "ag-titulo" }, a.craque), h("span", { class: "mini mudo num" }, `${a.id} · v${a.versao}`), a.ativo ? null : h("span", { class: "selo" }, "⏻ Desativado"), h("span", { class: "espaco" }),
        h("button", { class: "btn mini", id: "ag-editar", onclick: () => this.desenharForm(a, false) }, "✎ Editar"),
        h("button", { class: "btn mini", id: "ag-duplicar", onclick: acao(async () => { const d = await api("POST", `/api/agentes/${a.id}/duplicar`, {}); aviso(`Criado ${d.id}.`); history.replaceState({}, "", `/agentes/${d.id}`); this.atual = d; const r = await api("GET", "/api/agentes"); this.lista = r.agentes; this.desenharLista(); this.desenharDetalhe(); }) }, "⧉ Duplicar"),
        h("button", { class: "btn mini", id: "ag-ativar", onclick: () => this.alternar() }, a.ativo ? "⏻ Desativar" : "⏻ Reativar")),
      h("p", { class: "pequeno", style: "margin-top:6px" }, a.descricao),
      h("div", { class: "ficha" }, h("span", { class: "mudo" }, "Arquivo"), h("code", {}, a.arquivo)),
      h("div", { class: "ficha" }, h("span", { class: "mudo" }, "Modelo"), a.modelo || "herda da sessão"),
      h("div", { class: "ficha" }, h("span", { class: "mudo" }, "Ferramentas"), a.ferramentas.join(", ") || "padrão"),
      h("div", { class: "ficha" }, h("span", { class: "mudo" }, "Entradas"), a.contrato.entradas.join(", ") || "–"),
      h("div", { class: "ficha" }, h("span", { class: "mudo" }, "Saídas"), a.contrato.saidas.join(", ") || "–"),
      h("div", { class: "ficha", id: "ag-usos" }, h("span", { class: "mudo" }, "Usado em"), a.usos.length ? a.usos.map((u) => `${u.fluxo_nome} (${u.origem}: ${u.no_nome})`).join("; ") : "nenhum fluxo"),
      h("details", { class: "dobra", style: "margin-top:10px" }, h("summary", {}, "Instruções"), h("pre", { class: "log", style: "max-height:320px" }, a.instrucoes)),
      h("div", { id: "ag-testes-bloco" }), h("div", { id: "ag-versoes" })));
    this.desenharTestes();
    this.desenharVersoes();
  },
  alternar() {
    const a = this.atual;
    const fazer = async () => { const d = await api("POST", `/api/agentes/${a.id}/ativar`, { ativo: !a.ativo }); this.atual = d; const r = await api("GET", "/api/agentes"); this.lista = r.agentes; this.desenharLista(); this.desenharDetalhe(); aviso(d.ativo ? "Reativado." : "Desativado: o arquivo saiu de .claude/agents e vale também no terminal."); };
    if (a.ativo && a.usos.length) {
      dialogo("Desativar agente", h("div", { id: "confirmar-desativar" }, h("p", { class: "pequeno", style: "margin:8px 0" }, "Estes fluxos usam este agente e não vão mais poder ser publicados assim:"), h("ul", { class: "motivos" }, a.usos.map((u) => h("li", {}, `${u.fluxo_nome} (${u.origem}): ${u.no_nome}`))), h("p", { class: "mini mudo", style: "margin-top:6px" }, "Execuções em andamento continuam com a foto do agente.")), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Cancelar"), h("button", { class: "btn perigo", id: "desativar-sim", onclick: acao(async () => { fechar(); await fazer(); }) }, "Desativar")]);
    } else acao(fazer)({ currentTarget: null });
  },
  desenharTestes() {
    const a = this.atual, alvo = document.getElementById("ag-testes-bloco");
    if (!alvo) return;
    const ass = JSON.stringify(a.testes);
    if (alvo.dataset.ass === ass && alvo.childElementCount) return;
    alvo.dataset.ass = ass;
    const rascunho = alvo.querySelector("#teste-entrada")?.value;
    const entrada = h("textarea", { id: "teste-entrada", placeholder: "Ex.: tema “jovens e amizade”. Escreva a saída do seu contrato.", value: rascunho || "" });
    const projeto = h("input", { type: "text", id: "teste-projeto", placeholder: "Opcional: slug de um projeto; copia as entradas do contrato para a pasta do teste" });
    trocar(alvo, h("h3", { style: "margin-top:16px" }, "Testar isoladamente"), h("p", { class: "mini mudo", style: "margin:4px 0" }, "Roda o agente de verdade, com seu login do Claude Code e teto de US$ 1,00, numa pasta só para o teste. Nenhum projeto é tocado."), entrada, projeto,
      h("button", { class: "btn principal mini", id: "testar", style: "margin-top:6px", onclick: acao(async () => { const r = await api("POST", `/api/agentes/${a.id}/testar`, { entrada: entrada.value, projeto: projeto.value.trim() || null }); aviso(`Teste de v${r.versao} iniciado.`); this.atual = await api("GET", `/api/agentes/${a.id}`); this.desenharTestes(); }) }, "▶ Testar esta versão"),
      a.testes.length ? h("div", { id: "lista-testes", style: "margin-top:10px" }, a.testes.map((t) => h("article", { class: "teste", "data-teste": t.id }, h("div", { class: "linha-flex" }, h("b", {}, `Teste #${t.id} · v${t.versao}`), seloEstado(t.status === "ok" ? "concluido" : t.status === "falhou" ? "falhou" : "rodando", t.status === "ok" ? "Saída real" : t.status === "falhou" ? "Falhou" : "Rodando"), t.custo_usd != null ? h("span", { class: "mini mudo num" }, `US$ ${t.custo_usd.toFixed(3)}`) : null, h("span", { class: "espaco" }), t.job_id ? h("button", { class: "btn leve mini", onclick: () => verLog(t.job_id) }, "Log") : null),
        t.erro ? h("div", { class: "faixa falha erro-texto" }, t.erro) : null, t.saida ? h("pre", { class: "log saida-teste", style: "max-height:220px" }, t.saida) : null,
        (JSON.parse(t.arquivos || "[]")).map((f) => h("details", { class: "dobra" }, h("summary", { class: "mini" }, `Arquivo gerado: ${f.nome} (${f.bytes} bytes)`), f.texto != null ? h("pre", { class: "log" }, f.texto) : null))))) : null);
  },
  desenharVersoes() {
    const a = this.atual, alvo = document.getElementById("ag-versoes");
    if (a.versoes.length < 1) return;
    const diff = h("div", { id: "ag-diff" });
    const antes = h("select", { class: "seletor-versao", id: "ver-a" }, a.versoes.map((v, i) => h("option", { value: v.numero, selected: i === 1 }, `v${v.numero}`)));
    const depois = h("select", { class: "seletor-versao", id: "ver-b" }, a.versoes.map((v, i) => h("option", { value: v.numero, selected: i === 0 }, `v${v.numero}`)));
    trocar(alvo, h("h3", { style: "margin-top:16px" }, "Versões"), a.versoes.map((v) => h("div", { class: "linha-flex mini", style: "margin-top:3px" }, h("b", { class: "num" }, `v${v.numero}`), h("span", { class: "mudo" }, `${v.origem} · ${quando(v.criada_em)}`), h("span", { class: "espaco" }), v.numero !== a.versao ? h("button", { class: "btn leve mini", "data-restaurar": v.numero, onclick: acao(async () => { this.atual = await api("POST", `/api/agentes/${a.id}/restaurar`, { numero: v.numero }); aviso(`v${v.numero} restaurada como v${this.atual.versao}.`); this.desenharDetalhe(); }) }, "Restaurar") : h("span", { class: "mudo" }, "atual"))),
      a.versoes.length > 1 ? h("div", { class: "linha-flex", style: "margin-top:8px" }, antes, "→", depois, h("button", { class: "btn mini", id: "comparar-agente", onclick: acao(async () => { const r = await api("GET", `/api/agentes/${a.id}/comparar?a=${antes.value}&b=${depois.value}`); const mudou = r.ops.filter(([t]) => t !== "igual").length; trocar(diff, h("p", { class: "mini mudo", style: "margin:6px 0" }, mudou ? `${mudou} trechos diferentes` : "Sem diferença"), h("div", { class: "folha texto", style: "max-height:300px;overflow:auto;max-width:none" }, r.ops.map(([t, x]) => t === "igual" ? x : h("span", { class: t }, x)))); }) }, "Comparar")) : null, diff);
  },
};
Corte.registrar(/^\/agentes(?:\/([\w-]+))?\/?$/, Agentes);
