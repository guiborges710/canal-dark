"use strict";
/* Desenha um quadro do corte num canvas 1080x1920. O mesmo arquivo roda na prévia do editor e no export (render/corte_compor.mjs):
   é isso que garante o mesmo enquadramento, a mesma posição e a mesma legenda nos dois. Só recebe o que o servidor compilou. */
const Compositor = (() => {
  const ESTILOS = {
    viral: { fonte: "900 86px 'Arial Black', 'Segoe UI Black', Arial, sans-serif", caixa: true, cor: "#FFFFFF", contorno: "#000000", traco: 16, linha: 100, nome: "Viral" },
    caderno: { fonte: "700 76px Kalam, 'Segoe Print', cursive", cor: "#1C1C22", contorno: "#F6F4EC", traco: 12, linha: 88, nome: "Caderno" },
    cartao: { fonte: "900 58px 'Arial Black', 'Segoe UI Black', Arial, sans-serif", cor: "#1F2937", cartao: true, linha: 72, nome: "Cartão" },
  };
  const GRAFITE = "#1F2937", MARGEM = 86;

  async function iniciar(urlFontes) {
    try {
      const f = new FontFace("Kalam", `url(${urlFontes}/Kalam-Bold.ttf)`, { weight: "700" });
      await f.load();
      document.fonts.add(f);
    } catch (e) { /* sem a fonte, o navegador usa a alternativa; o export falha alto se a fonte sumir (ver corte_compor.mjs) */ }
  }

  function quebrar(ctx, texto, largura) {
    const linhas = [];
    for (const paragrafo of String(texto).split("\n")) {
      let atual = "";
      for (const p of paragrafo.split(/\s+/).filter(Boolean)) {
        const teste = atual ? `${atual} ${p}` : p;
        if (!atual || ctx.measureText(teste).width <= largura) atual = teste;
        else { linhas.push(atual); atual = p; }
      }
      if (atual) linhas.push(atual);
    }
    return linhas;
  }

  function desenharLegenda(ctx, l, W) {
    const e = ESTILOS[l.estilo] || ESTILOS.viral;
    ctx.save();
    ctx.font = e.fonte;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.lineJoin = "round";
    const texto = e.caixa ? String(l.texto).toUpperCase() : l.texto;
    const linhas = quebrar(ctx, texto, W - 2 * MARGEM);
    const y0 = l.y - ((linhas.length - 1) * e.linha) / 2;
    if (e.cartao) {
      const larg = Math.max(...linhas.map((t) => ctx.measureText(t).width)) + 76, alt = linhas.length * e.linha + 44;
      const x = l.x - larg / 2, y = l.y - alt / 2;
      ctx.fillStyle = GRAFITE;
      caixa(ctx, x + 12, y + 12, larg, alt);
      ctx.fill();
      ctx.fillStyle = "#FFFFFF"; ctx.strokeStyle = GRAFITE; ctx.lineWidth = 10;
      caixa(ctx, x, y, larg, alt);
      ctx.fill(); ctx.stroke();
    }
    linhas.forEach((t, i) => {
      const y = y0 + i * e.linha;
      if (e.contorno) { ctx.strokeStyle = e.contorno; ctx.lineWidth = e.traco; ctx.strokeText(t, l.x, y); }
      ctx.fillStyle = e.cor;
      ctx.fillText(t, l.x, y);
    });
    ctx.restore();
  }

  function caixa(ctx, x, y, w, h) {
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 24);
  }

  /* Devolve o que vale no quadro `f`: o segmento, o tempo dentro do clipe e as legendas. */
  function resolver(c, f) {
    f = Math.max(0, Math.min(c.total_f - 1, Math.floor(f)));
    let seg = c.segmentos[c.segmentos.length - 1];
    for (const s of c.segmentos) if (f < s.f1) { seg = s; break; }
    const local = Math.min(f - seg.f0, seg.quadros_fonte - 1);
    return { f, seg, local, baseT: seg.base_ini + (local + 0.5) / c.fps, legendas: c.legendas.filter((l) => f >= l.f0 && f < l.f1) };
  }

  /* `base` é o <video> (prévia) ou a <img> do quadro (export). `imagens` é {sha: imagem carregada}. */
  function desenhar(ctx, c, r, base, imagens) {
    const W = c.w, H = c.h, q = r.seg.quadro || { escala: 1, x: 0, y: 0 }, m = r.seg.midia;
    ctx.save();
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    if (base && !(m && m.modo === "cobre")) {
      const e = q.escala || 1;
      ctx.drawImage(base, (W - W * e) / 2 + (q.x || 0), (H - H * e) / 2 + (q.y || 0), W * e, H * e);
    } else if (m && m.modo === "cobre") {
      ctx.fillStyle = "#F6F4EC";  // PAPEL de media/sketch_lib.py
      ctx.fillRect(0, 0, W, H);
    }
    const img = m && imagens[m.sha];
    if (img) {
      const iw = m.w || img.naturalWidth, ih = m.h || img.naturalHeight, e = m.escala || 1;
      ctx.drawImage(img, m.x - (iw * e) / 2, m.y - (ih * e) / 2, iw * e, ih * e);
    }
    ctx.restore();
    for (const l of r.legendas) desenharLegenda(ctx, l, W);
  }

  /* O quadro é igual ao clipe? Então o export não precisa passar pelo navegador. */
  function precisaCompor(r) {
    const q = r.seg.quadro || {};
    return r.legendas.length > 0 || !!r.seg.midia || (q.escala ?? 1) !== 1 || (q.x || 0) !== 0 || (q.y || 0) !== 0;
  }

  return { ESTILOS, iniciar, resolver, desenhar, desenharLegenda, precisaCompor };
})();
if (typeof window !== "undefined") window.Compositor = Compositor;
