"use strict";
/* Novo projeto, a tela do Estúdio e os complementos das telas de revisão. */

/* ---------- Novo projeto ---------- */
Corte.abrirNovo = async function () {
  const op = await api("GET", "/api/opcoes");
  const est = { formato: op.padrao.formato, estilo: op.padrao.estilo, legenda: op.padrao.legenda, variante: null, opcoes: {} };
  const erro = h("div", { class: "alerta erro oculto", style: "margin-top:12px" });
  const tema = h("input", { type: "text", id: "tema", required: true, minLength: 3, placeholder: "Ex.: por que os jovens estão morando mais com os pais", autofocus: true });
  const briefing = h("textarea", { id: "briefing", placeholder: "Opcional: ângulo, fontes, o que evitar", style: "min-height:58px" });
  const duracao = h("input", { type: "number", id: "duracao", value: op.padrao.duracao, min: 20, max: 60, step: 1 });
  const fluxoSel = h("select", { id: "fluxo" }, op.fluxos.map((f) => h("option", { value: f.id }, `${f.nome} (publicado v${f.publicada})`)), h("option", { value: "" }, "Fluxo fixo antigo (sem grafo)"));
  const simulado = h("input", { type: "checkbox", id: "simulado" });
  const formato = h("select", { id: "formato", class: "oculto" }, op.formatos.map((x) => h("option", { value: x.id }, x.nome)));
  const estilo = h("select", { id: "estilo", class: "oculto" }, op.estilos.map((x) => h("option", { value: x.id }, x.nome)));
  const cartoes = (lista, chave, sel, amostra) => h("div", { class: "amostras", role: "radiogroup" }, lista.map((x) => h("button", { type: "button", class: "amostra" + (est[chave] === x.id ? " on" : ""), role: "radio", "aria-checked": est[chave] === x.id, "data-valor": x.id, onclick: (e) => {
    est[chave] = x.id; if (sel) sel.value = x.id;
    e.currentTarget.parentNode.querySelectorAll(".amostra").forEach((b) => { b.classList.toggle("on", b === e.currentTarget); b.setAttribute("aria-checked", b === e.currentTarget); });
    aviso_estilo();
  } }, amostra(x), h("b", {}, est[chave] === x.id ? `✓ ${x.nome}` : x.nome), h("span", { class: "mini mudo" }, x.detalhe))));
  const aviso_h = h("p", { class: "mini mudo", id: "aviso-formato" });
  const aviso_estilo = () => {
    const e = op.estilos.find((x) => x.id === est.estilo);
    aviso_h.textContent = !e.formatos.includes(est.formato) ? `O formato ${est.formato} não existe no estilo ${e.nome}.` : "";
  };
  const legendas = Object.entries(op.legendas).map(([id, l]) => ({ id, nome: l.nome, detalhe: l.detalhe }));
  const seletorEstilo = Corte.seletorEstilo(op.estilos, est, (id) => { estilo.value = id; aviso_estilo(); });
  const dlg = h("dialog", {}, h("form", { class: "modal novo", onsubmit: async (e) => {
    e.preventDefault();
    const b = e.submitter; b.disabled = true;
    try {
      const r = await api("POST", "/api/producoes", { tema: tema.value, briefing: briefing.value, formato: formato.value, estilo: est.estilo, variante: est.variante, opcoes: est.opcoes, legenda: est.legenda, duracao: Number(duracao.value), fluxo: fluxoSel.value || null, simulado: simulado.checked });
      fechar(); ir(fluxoSel.value && !simulado.checked ? `/estudio/${r.slug}` : `/producao/${r.slug}`);
    } catch (ex) { erro.textContent = ex.message; erro.classList.remove("oculto"); b.disabled = false; }
  } },
    h("h2", {}, "Novo projeto"),
    h("label", { class: "campo" }, h("span", {}, "Tema"), tema),
    Corte.blocoTemas(tema, briefing, () => fechar()),
    h("label", { class: "campo" }, h("span", {}, "Briefing"), briefing),
    h("div", { class: "campo" }, h("span", {}, "Estilo do vídeo"), seletorEstilo),
    h("div", { class: "campo" }, h("span", {}, "Legenda"), cartoes(legendas, "legenda", null, (x) => amostraLegenda(x.id))),
    h("div", { class: "campo" }, h("span", {}, "Formato"), cartoes(op.formatos, "formato", formato, (x) => h("div", { class: `mini-formato ${x.id}`, "aria-hidden": "true" })), aviso_h),
    h("div", { class: "linha-flex", style: "margin-top:12px;align-items:flex-end" },
      h("label", { class: "campo", style: "margin:0;flex:1" }, h("span", {}, "Fluxo"), fluxoSel),
      h("label", { class: "campo", style: "margin:0;width:120px" }, h("span", {}, "Duração alvo (s)"), duracao),
      h("label", { class: "campo", style: "margin:0;width:90px" }, h("span", {}, "Idioma"), h("input", { type: "text", value: op.padrao.idioma, disabled: true }))),
    formato, estilo,
    h("label", { class: "campo linha-flex" }, simulado, h("span", { style: "margin:0;font-weight:500" }, "Simular o texto, sem agentes (run.py --mock). Bom para testar o pipeline.")),
    erro,
    h("div", { class: "botoes" }, h("button", { type: "button", class: "btn", onclick: () => fechar() }, "Cancelar"), h("button", { class: "btn principal" }, "Criar e iniciar"))));
  function fechar() { if (dlg.parar) dlg.parar(); dlg.close(); dlg.remove(); }
  dlg.addEventListener("close", () => { if (dlg.parar) dlg.parar(); });
  document.body.append(dlg);
  dlg.parar = Corte.pararTemas;
  dlg.showModal();
};

/* ---------- Temas que já estão separados e não têm vídeo ---------- */
Corte.blocoTemas = function (tema, briefing, fecharDialogo) {
  const alvo = h("div", { class: "temas", id: "temas-prontos" }, h("span", { class: "mini mudo" }, "Procurando temas…"));
  let assinatura = null, relogio = null;
  const pinta = (d) => {
    const nova = JSON.stringify(d);
    if (nova === assinatura) return;
    assinatura = nova;
    const lista = d.temas.map((t) => h("article", { class: "tema", "data-tema": t.id },
      h("div", { class: "tema-texto" }, h("b", {}, t.titulo), t.descricao ? h("span", { class: "mini mudo" }, t.descricao) : null, h("span", { class: "mini mudo" }, `Separado por ${t.origem}${t.projeto ? " · já tem projeto começado" : ""}`)),
      t.projeto
        ? h("button", { type: "button", class: "btn mini", "data-abrir-tema": t.id, onclick: () => { fecharDialogo(); ir(`/estudio/${t.projeto}`); } }, "Abrir projeto")
        : h("button", { type: "button", class: "btn mini", "data-usar-tema": t.id, onclick: (e) => {
          tema.value = t.titulo;
          briefing.value = [t.arquivo ? `Tema separado em output/${t.arquivo}: use o que já foi levantado ali como ponto de partida e confira as fontes.` : "", t.angulo ? `Direção inicial: ${t.angulo}` : ""].filter(Boolean).join("\n");
          alvo.querySelectorAll(".tema").forEach((x) => x.classList.toggle("on", x.contains(e.currentTarget)));
        } }, "Usar este tema")));
    const vazio = !d.temas.length;
    const botao = h("button", { type: "button", class: `btn mini${vazio ? " principal" : ""}`, id: "gerar-tema", disabled: d.gerando, onclick: acao(async () => { await api("POST", "/api/temas/gerar"); atualizar(); }) }, d.gerando ? "Modric pesquisando…" : "✦ Gerar um tema");
    trocar(alvo,
      h("div", { class: "linha-flex" }, h("span", { class: "mini" }, h("b", {}, vazio ? "Nenhum tema separado sem vídeo." : `Ou escolha um tema sem vídeo (${d.temas.length})`)), h("span", { class: "espaco" }), botao),
      h("div", { class: "mini mudo", id: "temas-nota" }, d.gerando ? "O Modric está pesquisando de verdade, com fontes. Leva alguns minutos; o tema aparece aqui." : d.erro_geracao ? `O Modric não conseguiu: ${d.erro_geracao}` : "Gerar aciona o Modric com o seu login do Claude e traz um tema só."),
      lista.length ? h("div", { class: "tema-lista" }, lista) : null);
  };
  const atualizar = async () => {
    try { pinta(await api("GET", "/api/temas")); } catch (ex) { trocar(alvo, h("span", { class: "mini mudo" }, `Não foi possível ler os temas: ${ex.message}`)); }
  };
  atualizar();
  relogio = setInterval(atualizar, 4000);
  Corte.pararTemas = () => { clearInterval(relogio); };
  return alvo;
};

/* ---------- Escolha de estilo: os mesmos cartões na criação e na troca ---------- */
Corte.seletorEstilo = function (lista, est, aoMudar) {
  const grade = h("div", { class: "estilos", role: "radiogroup", "aria-label": "Estilo do vídeo" });
  const variacoes = h("div", { id: "estilo-variacoes" });
  const escolher = (id) => {
    est.estilo = id; est.variante = null; est.opcoes = {};
    if (aoMudar) aoMudar(id);
    pinta();
  };
  const pintaVariacoes = () => {
    const e = lista.find((x) => x.id === est.estilo);
    const vars = Object.entries(e.variantes || {});
    if (!vars.length) { trocar(variacoes); return; }
    const sel = h("select", { id: "estilo-variante", "aria-label": "Variação", onchange: (ev) => { est.variante = ev.target.value || null; est.opcoes = {}; if (est.variante) { for (const [c, vs] of Object.entries(e.variantes[est.variante].opcoes)) est.opcoes[c] = Object.keys(vs)[0]; } pintaVariacoes(); } },
      h("option", { value: "" }, `${e.nome} padrão`), vars.map(([id, v]) => h("option", { value: id, selected: est.variante === id }, v.nome)));
    const v = e.variantes[est.variante];
    trocar(variacoes, h("div", { class: "linha-flex estilo-var" }, h("span", { class: "mini" }, "Variação"), sel,
      v ? Object.entries(v.opcoes).map(([campo, valores]) => h("select", { id: `estilo-opcao-${campo}`, "aria-label": campo, onchange: (ev) => { est.opcoes[campo] = ev.target.value; } }, Object.entries(valores).map(([k, n]) => h("option", { value: k, selected: est.opcoes[campo] === k }, n)))) : null,
      v ? h("span", { class: "mini mudo" }, v.detalhe) : null));
  };
  const pinta = () => {
    trocar(grade, ...lista.map((x) => {
      const ligado = est.estilo === x.id;
      return h("div", { class: "estilo-cartao" + (ligado ? " on" : ""), role: "radio", tabindex: 0, "aria-checked": ligado, "data-estilo": x.id, onclick: () => escolher(x.id), onkeydown: (e) => { if (e.key === " " || e.key === "Enter") { e.preventDefault(); escolher(x.id); } } },
        h("video", { class: "estilo-video", src: x.demo, poster: x.poster, muted: true, loop: true, autoplay: true, playsInline: true, preload: "metadata", "aria-hidden": "true" }),
        h("b", {}, ligado ? `✓ ${x.nome}` : x.nome),
        h("span", { class: "mini mudo" }, x.detalhe),
        h("span", { class: "mini" }, h("b", {}, "Melhor para: "), x.melhor_para),
        h("button", { type: "button", class: "btn leve mini", "data-demo": x.id, onclick: (e) => { e.stopPropagation(); Corte.verDemo(x); } }, "▶ Ver demonstração"));
    }));
    pintaVariacoes();
  };
  pinta();
  return h("div", {}, grade, variacoes);
};

Corte.verDemo = function (x) {
  dialogo(`${x.nome}: demonstração`, h("div", { id: "demo-estilo" }, h("video", { class: "demo-grande", src: x.demo, controls: true, autoplay: true, loop: true, muted: true, playsInline: true }),
    h("p", { class: "mini mudo", style: "margin-top:6px" }, "Saída real do renderizador deste estilo, reduzida. Sem narração.")), null, 420);
};

/* Troca de estilo: mostra o que será refeito antes de confirmar. */
Corte.trocarEstilo = async function (slug) {
  const d = await api("GET", `/api/producoes/${slug}/estilo`);
  const est = { estilo: d.atual.estilo, variante: d.atual.variante || null, opcoes: d.atual.opcoes || {} };
  const conteudo = h("div", { id: "troca-estilo" });
  const passo1 = () => {
    trocar(conteudo, Corte.seletorEstilo(d.estilos, est), h("div", { class: "botoes" }, h("button", { class: "btn", onclick: () => dl.fechar() }, "Cancelar"), h("button", { class: "btn principal", id: "estilo-continuar", onclick: acao(passo2) }, "Continuar")));
  };
  const passo2 = async () => {
    const im = await api("POST", `/api/producoes/${slug}/estilo/impacto`, est);
    if (im.igual) { aviso("O projeto já está neste estilo."); dl.fechar(); return; }
    const linha = (x) => h("li", {}, h("b", {}, x.nome), x.versao ? ` (v${x.versao}${x.aprovada ? ", aprovada" : ""})` : "", `: ${x.motivo}`);
    trocar(conteudo, h("p", {}, `De ${im.atual} para ${im.nome}.`),
      im.bloqueios.length ? h("div", { class: "alerta erro", id: "estilo-bloqueios" }, im.bloqueios.map((b) => h("div", {}, b))) : null,
      im.refazer.length ? h("section", { id: "estilo-refazer" }, h("h3", {}, "Precisará ser refeito"), h("ul", { class: "lista-impacto" }, im.refazer.map(linha))) : h("p", { class: "pequeno", id: "estilo-livre" }, "Nada foi produzido que dependa do estilo: a troca não invalida nenhuma etapa."),
      im.mantem.length ? h("section", { id: "estilo-mantem" }, h("h3", {}, "Continua valendo"), h("ul", { class: "lista-impacto" }, im.mantem.map(linha))) : null,
      im.refazer.length ? h("p", { class: "mini mudo" }, "Nada é apagado: os arquivos antigos ficam em _troca_estilo/ dentro da pasta do projeto e as versões continuam no histórico.") : null,
      h("div", { class: "botoes" }, h("button", { class: "btn", onclick: () => passo1() }, "Voltar"),
        im.bloqueios.length ? null : h("button", { class: "btn principal", id: "estilo-confirmar", onclick: acao(async () => {
          const r = await api("POST", `/api/producoes/${slug}/estilo`, { ...est, confirmar: im.assinatura });
          if (r.precisa_confirmar) { await passo2(); aviso("O projeto mudou enquanto você lia: confira de novo."); return; }
          aviso(r.refazendo && r.refazendo.length ? "Estilo trocado. As etapas afetadas foram reabertas." : "Estilo trocado.");
          dl.fechar();
          if (Corte.atual && Corte.atual.assin) Corte.atual.assin = {};
          atualizar();
        }) }, im.refazer.length ? "Confirmar e invalidar essas etapas" : "Trocar o estilo")));
  };
  const dl = dialogo("Trocar o estilo", conteudo, null, 780);
  passo1();
};

/* Desenha com o mesmo compositor do vídeo: a amostra é a legenda que sai no MP4. */
function amostraLegenda(id) {
  const c = h("canvas", { width: 540, height: 300, class: "amostra-tela legenda" });
  const x = c.getContext("2d");
  const pinta = () => {
    x.setTransform(1, 0, 0, 1, 0, 0);
    x.fillStyle = "#F6F4EC"; x.fillRect(0, 0, 540, 300);
    x.strokeStyle = "#BECEE2"; for (let i = 26; i < 300; i += 26) { x.beginPath(); x.moveTo(0, i); x.lineTo(540, i); x.stroke(); }
    if (id === "nenhum") { x.fillStyle = "#8b8e97"; x.font = "26px sans-serif"; x.textAlign = "center"; x.fillText("sem texto por cima", 270, 160); return; }
    x.scale(0.5, 0.5);
    Compositor.desenharLegenda(x, { texto: "seu terceiro lugar", x: 540, y: 300, estilo: id }, 1080);
  };
  (document.fonts.load("700 76px Kalam").catch(() => {})).then(pinta);
  pinta();
  return c;
}
Compositor.iniciar("/fontes");

/* ---------- Tela: Estúdio ---------- */
const Estudio = {
  slug: null, dados: null, cena: null, versaoVendo: null,
  montar(m) {
    this.etapaFoco = new URLSearchParams(location.search).get("etapa"); this.focado = false;
    this.slug = m[1]; this.dados = null; this.cena = null; this.versaoVendo = null; this.assin = {};
    document.title = "Estúdio · Corte";
    trocar(app, h("div", { class: "estudio", id: "estudio" },
      h("header", { class: "barra", id: "e-barra" }, h("span", { class: "mudo" }, "Carregando…")),
      h("aside", { class: "e-agentes", id: "e-agentes", "aria-label": "Agentes" }),
      h("main", { class: "e-centro", id: "e-centro" }),
      h("aside", { class: "e-lado", id: "e-lado" }),
      h("section", { class: "e-cenas", id: "e-cenas", "aria-label": "Sequência de cenas" })));
  },
  async atualizar() {
    const slug = this.slug;
    const d = await api("GET", `/api/producoes/${slug}/estudio`);
    if (this.slug !== slug) return;
    this.dados = d;
    document.title = `${d.estado.titulo} · Estúdio`;
    const muda = (k, v, fn) => { const a = JSON.stringify(v); if (this.assin[k] !== a) { this.assin[k] = a; fn(); } };
    muda("barra", [d.estado.titulo, d.execucao, d.corte, d.estado.resumo.proxima, d.estado.estilo_nome], () => this.barra());
    muda("agentes", d.linhas, () => this.agentes());
    muda("centro", [d.videos.map((v) => v.id), this.versaoVendo], () => this.centro());
    muda("cenas", [d.cenas, d.videos[0] && d.videos[0].id, this.cena], () => this.cenas());
    muda("lado", [d.decisoes, this.cena, d.cenas, d.corte, this.versaoVendo, d.videos.map((v) => [v.id, v.aprovada])], () => this.lado());
  },
  barra() {
    const d = this.dados, ex = d.execucao, slug = this.slug;
    trocar(document.getElementById("e-barra"), ...[
      h("a", { class: "voltar", href: "/", onclick: (e) => { e.preventDefault(); ir("/"); } }, "← Projetos"),
      h("span", { class: "titulo", title: d.estado.titulo }, d.estado.titulo),
      ex ? h("a", { class: "selo", id: "selo-fluxo", href: `/fluxos/${ex.fluxo}`, title: "Esta execução fica presa a esta versão do fluxo", onclick: (e) => { e.preventDefault(); ir(`/fluxos/${ex.fluxo}`); } }, `⛓ Fluxo ${ex.fluxo} v${ex.fluxo_numero}${ex.fluxo_atual !== ex.fluxo_numero ? ` (já existe v${ex.fluxo_atual})` : ""}`) : h("span", { class: "selo", id: "selo-fluxo" }, "Fluxo fixo antigo"),
      d.corte && !d.corte.em_dia ? h("span", { class: "selo aguardando", title: d.corte.motivo }, "✎ Corte alterado: nova revisão") : null,
      h("button", { class: "selo selo-botao", id: "selo-estilo", title: "Estilo deste projeto. Clique para trocar.", onclick: acao(() => Corte.trocarEstilo(slug)) }, `🎨 ${d.estado.estilo_nome}`),
      h("span", { class: "espaco" }),
      !ex ? h("button", { class: "btn mini", id: "executar-fluxo", onclick: acao(async () => { await api("POST", `/api/producoes/${slug}/executar`, { fluxo: "canal" }); aviso("Execução iniciada. O que já existe é reaproveitado."); }) }, "Executar pelo fluxo") : null,
      h("a", { class: "btn mini", id: "ir-revisao", href: `/producao/${slug}`, onclick: (e) => { e.preventDefault(); ir(`/producao/${slug}`); } }, "Revisar"),
      h("a", { class: "btn principal mini", id: "editar-video", href: `/editor/${slug}`, onclick: (e) => { e.preventDefault(); ir(`/editor/${slug}`); } }, "✂ Editar vídeo")].filter(Boolean));
  },
  agentes() {
    const d = this.dados;
    const linhas = d.linhas.filter((x) => x.tipo !== "aprovacao");
    trocar(document.getElementById("e-agentes"), h("h3", {}, "Agentes"), h("div", { class: "lista-agentes" }, linhas.map((x) => {
      const prog = x.progresso || {};
      const tarefa = x.status === "rodando" ? (x.job && x.job.titulo) || x.funcao : x.funcao;
      return h("button", { class: `agente-linha ${x.status}`, "data-no": x.no, onclick: () => this.abrirExecucao(x) },
        h("span", { class: "agente-topo" }, h("b", {}, x.craque || x.nome), x.agente_versao ? h("span", { class: "mini mudo num" }, `v${x.agente_versao}`) : null, h("span", { class: "espaco" }), seloEstado(x.status, x.legado ? x.status_texto : null)),
        h("span", { class: "mini mudo" }, x.craque ? x.nome : "Sem agente: comando do projeto"),
        h("span", { class: "pequeno" }, tarefa),
        seloMotor(x.job, { interativo: false }),
        prog.contador ? h("span", { class: "mini contador-cena", "data-contador": "1" }, prog.contador) : null,
        prog.porcentagem != null ? h("span", { class: "progresso" }, h("i", { style: `width:${prog.porcentagem}%` })) : null,
        x.nota ? h("span", { class: "mini mudo nota" }, x.nota) : null,
        h("span", { class: "mini mudo" }, x.atualizado_em ? `Atualizado ${quando(x.atualizado_em)}` : "Sem registro ainda"));
    })));
    this.focarEtapa();
  },
  /* PROG-003: vindo da aba Agentes > Ao vivo (?etapa=<id>), destaca o nó da etapa e leva o foco até ele (uma vez). */
  focarEtapa() {
    if (!this.etapaFoco) return;
    const b = document.querySelector(`#e-agentes [data-no="${CSS.escape(this.etapaFoco)}"]`);
    if (!b) return;
    b.classList.add("em-foco"); b.setAttribute("aria-current", "step");
    if (!this.focado) { this.focado = true; b.scrollIntoView({ block: "center" }); b.focus({ preventScroll: true }); }
  },
  videoAtual() {
    const v = this.dados.videos;
    return (this.versaoVendo && v.find((x) => x.id === this.versaoVendo)) || v[0] || null;
  },
  centro() {
    const v = this.videoAtual(), d = this.dados, alvo = document.getElementById("e-centro");
    if (!v) {
      trocar(alvo, h("div", { class: "vazio-etapa" }, h("b", {}, "Ainda não há vídeo renderizado."), "A prévia aparece aqui quando o render terminar."));
      return;
    }
    const el = h("video", { id: "e-video", controls: true, preload: "metadata", src: `/blob/${v.sha}?nome=video.mp4`, playsInline: true, ontimeupdate: (ev) => this.realcar(ev.target.currentTime) });
    trocar(alvo, h("div", { class: `e-preview ${d.estado.formato}` }, el),
      h("div", { class: "linha-flex e-versao" }, h("span", { class: "mudo pequeno" }, "Você está vendo"),
        h("select", { class: "seletor-versao", id: "e-versao", "aria-label": "Versão que você está vendo", onchange: (ev) => { this.versaoVendo = Number(ev.target.value); this.assin.centro = null; this.atualizar(); } }, d.videos.map((x, i) => h("option", { value: x.id, selected: x.id === v.id }, `v${x.numero}${i === 0 ? " (atual)" : ""}${x.aprovada ? " · aprovada" : ""}${x.origem === "estudio" ? "" : ` · ${x.origem}`}`))),
        h("span", { class: "mudo pequeno", id: "e-aprovando" }, v.id === d.videos[0].id ? "é a versão que você aprova" : `para aprovar, volte à v${d.videos[0].numero}`)));
  },
  realcar(t) {
    const c = this.dados.cenas;
    let at = null;
    for (const x of c) if (t >= x.inicio) at = x;
    document.querySelectorAll(".e-cena").forEach((b) => b.classList.toggle("tocando", !!at && Number(b.dataset.i) === at.i));
  },
  cenas() {
    const d = this.dados, v = d.videos[0];
    trocar(document.getElementById("e-cenas"), d.cenas.length ? h("div", { class: "tira" }, d.cenas.map((c, n) => h("button", { class: `e-cena${this.cena === c.i ? " ativa" : ""}`, "data-i": c.i, onclick: () => {
      this.cena = c.i;
      const el = document.getElementById("e-video");
      if (el) { el.currentTime = c.inicio + 0.05; el.pause(); }
      document.querySelectorAll(".e-cena").forEach((b) => b.classList.toggle("ativa", Number(b.dataset.i) === c.i));
      this.lado();
    } }, v ? h("img", { src: `/quadro/${v.sha}?t=${(c.inicio + Math.min(c.dur * 0.6, c.dur - 0.05)).toFixed(2)}`, alt: "", loading: "lazy" }) : h("span", { class: "sem-imagem" }, "Sem render"),
      h("span", { class: "mini" }, h("b", {}, `Cena ${c.i + 1}`), ` · ${tempoCurto(c.inicio)}`), h("span", { class: "mini mudo tira-fala" }, c.fala)))) : h("p", { class: "mudo pequeno" }, "As cenas aparecem aqui quando o cenas.json existir."));
  },
  lado() {
    const d = this.dados, c = d.cenas.find((x) => x.i === this.cena), ex = d.execucao, slug = this.slug;
    const direcao = c ? h("section", { id: "e-direcao" }, h("h3", {}, `Direção visual · Cena ${c.i + 1}`), h("p", { class: "pequeno", style: "white-space:pre-wrap;margin-top:6px" }, c.direcao || "Sem direção registrada para esta cena."), h("p", { class: "mini mudo", style: "margin-top:6px" }, c.fala),
      (c.tela || []).length ? h("div", { class: "mini", style: "margin-top:6px" }, c.tela.map((t) => h("span", { class: "etiqueta" }, t))) : null,
      h("div", { class: "linha-flex", style: "margin-top:8px" }, h("a", { class: "btn mini", href: `/producao/${slug}?etapa=roteiro`, onclick: (e) => { e.preventDefault(); ir(`/producao/${slug}?etapa=roteiro`); } }, "Editar na revisão"), h("a", { class: "btn mini", href: `/editor/${slug}?t=${c.inicio}`, onclick: (e) => { e.preventDefault(); ir(`/editor/${slug}?t=${c.inicio}`); } }, "✂ Abrir no editor"))) : h("section", { id: "e-direcao" }, h("h3", {}, "Direção visual"), h("p", { class: "mudo pequeno", style: "margin-top:6px" }, "Clique numa cena abaixo para ver a direção dela."));
    const vendo = this.videoAtual();
    const decisoes = h("section", { id: "e-decisoes" }, h("h3", {}, "Aprovações"), d.decisoes.length ? d.decisoes.map((x) => {
      const url = `/producao/${slug}?etapa=${x.material}`;
      return h("article", { class: `decisao ${x.status}`, "data-decisao": x.no },
        h("div", { class: "linha-flex" }, h("b", {}, x.nome), h("span", { class: "espaco" }), seloEstado(x.status, x.status_texto)),
        x.versao ? h("div", { class: "mini mudo" }, `Aprovando v${x.versao.numero}${x.material === "video" && vendo ? ` · vendo v${vendo.numero}` : ""}`) : null,
        x.nota ? h("div", { class: "mini mudo" }, x.nota) : null,
        h("div", { class: "linha-flex", style: "margin-top:5px" },
          h("a", { class: "btn mini", href: url, onclick: (e) => { e.preventDefault(); ir(url); } }, "Revisar"),
          x.exec && x.status === "aguardando" && x.versao ? h("button", { class: "btn aprovar mini", "data-aprovar-no": x.no, onclick: acao(async () => { const r = await api("POST", `/api/execucoes/${x.exec}/aprovar`, { no: x.no, versao_id: x.versao.id }); aviso(r.ja ? "Já estava aprovado: nada foi disparado de novo." : r.iniciados.length ? "Aprovado. O próximo passo começou." : "Aprovado."); }) }, `✓ Aprovar v${x.versao.numero}`) : null,
          x.exec && (x.status === "aguardando" || x.status === "concluido") ? h("button", { class: "btn leve mini", "data-devolver": x.no, onclick: () => this.pedirAjuste(x) }, "Pedir ajuste") : null));
    }) : h("p", { class: "mudo pequeno" }, "Este fluxo não tem aprovação."));
    const cortado = d.corte && !d.corte.em_dia ? h("section", {}, h("h3", {}, "Corte"), h("p", { class: "pequeno", style: "margin-top:5px" }, d.corte.motivo)) : null;
    const ativos = ex ? d.linhas.filter((x) => x.status === "aguardando_inicio") : [];
    const iniciar = ativos.length ? h("section", {}, h("h3", {}, "Esperando você iniciar"), ativos.map((x) => h("div", { class: "linha-flex", style: "margin-top:6px" }, h("span", { class: "pequeno" }, x.nome), h("span", { class: "espaco" }), h("button", { class: "btn principal mini", "data-liberar": x.no, onclick: acao(async () => { const r = await api("POST", `/api/execucoes/${ex.id}/liberar`, { no: x.no }); aviso(r.ja ? "Já tinha sido iniciado." : "Iniciado."); }) }, "▶ Iniciar")))) : null;
    trocar(document.getElementById("e-lado"), ...[direcao, iniciar, decisoes, cortado].filter(Boolean));
  },
  pedirAjuste(x) {
    const d = this.dados;
    const texto = h("textarea", { id: "ajuste-texto", placeholder: "O que precisa mudar" });
    const cena = h("select", { id: "ajuste-cena" }, h("option", { value: "" }, "Todo o material"), d.cenas.map((c) => h("option", { value: c.i, selected: this.cena === c.i }, `Cena ${c.i + 1}: ${c.fala.slice(0, 40)}…`)));
    dialogo(`Pedir ajuste: ${x.nome}`, h("div", {}, h("p", { class: "mudo pequeno", style: "margin:6px 0" }, "Só este ramo volta a esperar. O que está em outro ramo, com as aprovações dele, fica como está."), h("label", { class: "campo" }, h("span", {}, "Trecho"), cena), h("label", { class: "campo" }, h("span", {}, "Comentário"), texto)), (fechar) => [h("button", { class: "btn", onclick: fechar }, "Cancelar"), h("button", { class: "btn principal", id: "ajuste-enviar", onclick: acao(async () => {
      await api("POST", `/api/execucoes/${x.exec}/devolver`, { no: x.no, texto: texto.value, cena: cena.value === "" ? null : Number(cena.value), categoria: x.material === "narracao" ? "Narração" : null });
      fechar(); aviso("Ajuste enviado ao responsável.");
    }) }, "Enviar ao responsável")]);
  },
  abrirExecucao(x) {
    const ex = this.dados.execucao;
    const pre = h("pre", { class: "log" }, "Sem trabalho iniciado neste nó.");
    const j = x.job;
    let t = null;
    if (j) {
      const ler = async () => { const r = await api("GET", `/api/jobs/${j.id}/log`).catch(() => ({ log: "" })); pre.textContent = r.log || "(sem saída ainda)"; pre.scrollTop = pre.scrollHeight; };
      ler(); t = setInterval(ler, 2000);
    }
    const linha = (a, b) => h("div", { class: "ficha" }, h("span", { class: "mudo" }, a), h("span", {}, b));
    const dl = dialogo(x.craque ? `${x.craque} · ${x.nome}` : x.nome, h("div", { id: "painel-execucao" },
      h("div", { style: "margin:10px 0" }, seloEstado(x.status, x.status_texto)),
      linha("Projeto", this.slug), linha("Nó", x.no), x.agente ? linha("Agente", `${x.agente}${x.agente_versao ? ` v${x.agente_versao} (${x.agente_sha})` : ""}`) : null,
      ex ? linha("Fluxo", `${ex.fluxo} v${ex.fluxo_numero}, execução #${ex.id}`) : linha("Fluxo", "Fluxo fixo antigo"),
      x.entradas ? linha("Entrada", x.entradas.length ? x.entradas.join(", ") : "–") : null,
      x.saidas ? linha("Saída", x.saidas.length ? x.saidas.map((s) => `${s}${x.saidas_versoes && x.saidas_versoes[s] ? ` (v${x.saidas_versoes[s]})` : ""}`).join(", ") : "–") : null,
      x.nota ? linha("Nota", x.nota) : null,
      seloMotor(j) ? linha("Motor", seloMotor(j)) : j && x.agente ? h("p", { class: "mini mudo" }, "Motor: não registrado (trabalho antigo).") : null,
      j && j.custo_usd != null ? linha("Custo", `US$ ${j.custo_usd.toFixed(2)}`) : null,
      j && j.erro ? h("div", { class: "faixa falha erro-texto", style: "margin-top:8px" }, j.erro) : null, pre,
      h("div", { class: "linha-flex", style: "margin-top:10px" },
        ex && x.status === "aguardando_inicio" ? h("button", { class: "btn principal", onclick: acao(async () => { await api("POST", `/api/execucoes/${ex.id}/liberar`, { no: x.no }); dl.fechar(); }) }, "▶ Iniciar") : null,
        ex && ["falhou", "concluido"].includes(x.status) && x.tipo !== "aprovacao" ? h("button", { class: x.status === "falhou" ? "btn principal" : "btn", id: "repetir-no", onclick: acao(async () => { await api("POST", `/api/execucoes/${ex.id}/repetir`, { no: x.no }); dl.fechar(); aviso("Refazendo este nó e o que depende dele."); }) }, x.status === "falhou" ? "Tentar de novo" : "Refazer este passo") : null,
        !ex && x.material ? h("a", { class: "btn", href: `/producao/${this.slug}?etapa=${x.no}`, onclick: (e) => { e.preventDefault(); dl.fechar(); ir(`/producao/${this.slug}?etapa=${x.no}`); } }, "Abrir a etapa") : null)), null, 720);
    dl.d.addEventListener("close", () => clearInterval(t));
  },
};
Corte.registrar(/^\/estudio\/([\w.-]+)/, Estudio);

/* ---------- Complementos das telas de revisão ---------- */
Corte.campoCena = function (c, campo, valor) {
  const tela = h("span", { style: "white-space:pre-wrap" }, valor || h("em", { class: "mudo" }, campo === "direcao" ? "Sem direção por cena" : "Sem fala"));
  if (!S.cont || !S.cont.e_atual) return tela;
  const editar = h("button", { class: "btn leve mini", "data-editar": `${campo}:${c.i}`, style: "padding:0 4px;margin-left:5px", onclick: () => {
    const caixa = h("textarea", { value: valor || "", style: "margin-top:4px;min-height:70px", "data-caixa": `${campo}:${c.i}` });
    const envolto = h("div", {}, caixa, h("div", { class: "linha-flex", style: "margin-top:4px" },
      h("button", { class: "btn principal mini", "data-salvar": `${campo}:${c.i}`, onclick: acao(async () => { await api("POST", `/api/producoes/${S.slug}/editar_cena`, { cena: c.i, campo, valor: caixa.value }); aviso(campo === "fala" ? "Fala salva: só a narração desta cena fica desatualizada." : "Direção salva."); Corte.editando = false; S.assinaturas.corpo = null; }) }, "Salvar"),
      h("button", { class: "btn mini", onclick: () => { envolto.replaceWith(tudo); Corte.editando = false; } }, "Cancelar")));
    tudo.replaceWith(envolto);
    Corte.editando = true;  // o polling não redesenha enquanto há texto sendo digitado
  } }, "✎ Editar eu mesmo");
  const tudo = h("span", {}, tela, editar);
  return tudo;
};

Corte.complementarRevisao = function (e, c, alvo) {
  if (e.material === "componentes") Corte.blocoThumbnail(alvo);
};

Corte.blocoThumbnail = async function (alvo) {
  const r = await api("GET", `/api/producoes/${S.slug}/thumbnail`);
  const secao = h("section", { id: "thumb-bloco", style: "margin-top:8px" }, h("div", { class: "grupo-titulo" }, h("h2", {}, "Thumbnail")));
  const t = r.thumbnail;
  const refazer = () => { S.assinaturas.corpo = null; atualizar(); };
  if (!t) secao.append(h("p", { class: "mudo pequeno" }, "Este projeto ainda não tem thumbnail.jpg. O Seedorf entrega o prompt; a imagem é gerada fora daqui e pode ser enviada abaixo."), Corte.botaoArquivo("Enviar thumbnail", `/api/producoes/${S.slug}/enviar/thumbnail`, refazer));
  else secao.append(h("div", { class: "grade" }, h("article", { class: "asset" + (t.decisao === "aprovado" ? " aprovado" : "") }, h("span", { class: "img" }, h("img", { src: t.url, alt: "Thumbnail" })), h("div", { class: "info" }, h("div", { class: "linha-flex" }, h("span", { class: "nome" }, "thumbnail.jpg"), t.decisao === "aprovado" ? h("span", { class: "selo aprovada" }, "✓ Aprovada") : h("span", { class: "selo" }, "A revisar")), h("div", { class: "mini mudo" }, "Usada na publicação do vídeo"),
    h("div", { class: "botoes" }, h("button", { class: "btn mini", id: "thumb-aprovar", onclick: acao(async () => { await api("POST", `/api/producoes/${S.slug}/decidir_thumbnail`, { decisao: t.decisao === "aprovado" ? "pendente" : "aprovado" }); refazer(); }) }, t.decisao === "aprovado" ? "Desfazer" : "Aprovar"), Corte.botaoArquivo("Trocar arquivo", `/api/producoes/${S.slug}/enviar/thumbnail`, refazer))))));
  document.getElementById("thumb-bloco")?.remove();
  alvo.append(secao);
};

Corte.abrirTomadas = async function (t) {
  const r = await api("GET", `/api/producoes/${S.slug}/tomadas?cena=${t.i}`);
  dialogo(`Tomadas da cena ${t.i + 1}`, h("div", { id: "lista-tomadas" }, h("p", { class: "mudo pequeno", style: "margin:6px 0" }, t.texto),
    r.tomadas.length ? r.tomadas.map((x) => h("div", { class: "tomada" }, h("div", { class: "linha-flex" }, h("b", {}, `Da narração v${x.versao}`), x.dur ? h("span", { class: "mini mudo num" }, `${x.dur.toFixed(2)} s`) : null, x.atual ? h("span", { class: "selo aprovada" }, "✓ Em uso") : null), h("audio", { controls: true, preload: "none", src: x.url }),
      !x.atual ? h("button", { class: "btn mini", onclick: acao(async () => { await api("POST", `/api/producoes/${S.slug}/usar_tomada`, { cena: t.i, sha: x.sha }); aviso("Tomada recolocada: nova versão da narração."); S.assinaturas.corpo = null; }) }, "Usar esta tomada") : null)) : h("p", { class: "mudo" }, "Só existe esta tomada."),
    h("p", { class: "mini mudo", style: "margin-top:8px" }, "O Chatterbox não informa o tempo de cada palavra, então a transcrição sincroniza por trecho, não por palavra.")), null, 560);
};

Corte.barraVideo = function (d, video) {
  const comparar = () => Corte.compararVideos(d);
  return h("div", { class: "linha-flex", id: "barra-video", style: "margin-bottom:8px" },
    d.do_corte ? h("span", { class: "selo" }, "✂ Saiu do editor") : null,
    d.corte && !d.corte.em_dia ? h("span", { class: "selo aguardando" }, d.corte.motivo) : null,
    h("span", { class: "espaco" }),
    S.cont.versoes.length > 1 ? h("button", { class: "btn mini", id: "comparar-versoes", onclick: comparar }, "Comparar versões") : null,
    h("button", { class: "btn mini", id: "editar-no-ponto", onclick: () => ir(`/editor/${S.slug}?t=${video.currentTime.toFixed(3)}`) }, "✂ Abrir o editor neste ponto"));
};

Corte.compararVideos = function () {
  const vs = S.cont.versoes;
  const urlDe = async (id) => (await api("GET", `/api/producoes/${S.slug}/material/video?versao=${id}`)).dados.url;
  const ladoA = h("video", { controls: true, playsInline: true, muted: true }), ladoB = h("video", { controls: true, playsInline: true });
  const escolher = (el, inicial) => h("select", { class: "seletor-versao", onchange: async (e) => { el.src = await urlDe(Number(e.target.value)); } }, vs.map((v) => h("option", { value: v.id, selected: v.id === inicial }, `v${v.numero}${v.aprovada ? " · aprovada" : ""}`)));
  urlDe(vs[0].id).then((u) => { ladoB.src = u; });
  urlDe(vs[1].id).then((u) => { ladoA.src = u; });
  const juntos = (fn) => h("button", { class: "btn mini", onclick: () => fn() }, fn === parar ? "❚❚ Pausar" : "▶ Tocar juntas");
  function tocar() { ladoA.currentTime = ladoB.currentTime; ladoA.play(); ladoB.play(); }
  function parar() { ladoA.pause(); ladoB.pause(); }
  dialogo("Comparar versões", h("div", {}, h("div", { class: "comparar" }, h("div", {}, escolher(ladoA, vs[1].id), ladoA), h("div", {}, escolher(ladoB, vs[0].id), ladoB)), h("div", { class: "linha-flex", style: "margin-top:8px" }, juntos(tocar), juntos(parar))), null, 860);
};
