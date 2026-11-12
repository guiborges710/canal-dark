"use strict";
/* Mesclagem fiel do texto do agente (painel). O editor visual devolve markdown "canônico" (`*` nas listas, linhas em branco entre blocos,
   tabelas alinhadas...), que quase nunca é igual ao que está no arquivo. Para que abrir e salvar não mude nada, e para que editar um
   parágrafo mude só aquele parágrafo, a gravação parte do ORIGINAL do arquivo e aplica só as diferenças entre:
     base  = o que o editor devolveu logo ao abrir (sem o usuário mexer)
     novo  = o que o editor devolve agora
   Sem mudança (novo === base) o resultado é o original, byte a byte. Sem DOM: roda também no Node (testes).
   Duas adaptações para o que o editor entende mal (o texto vai ao editor por `paraEditor`):
     - "<slug>" parece tag HTML e o editor a apagaria: vai como "\<slug>" (texto) e volta como "<slug>";
     - parágrafo quebrado em várias linhas no arquivo (recuo de lista, linha longa) é unido com espaço, senão o editor cola as palavras. */
(function (raiz) {
  const ehBranca = (t) => t.trim() === "";
  const chave = (t) => /^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(t) ? "---" : /^\s{0,3}(`{3,}|~{3,})/.test(t) ? "cerca " + t.replace(/^\s{0,3}(`{3,}|~{3,})\s*/, "").trim() : t.trim().replace(/^(?:[-*+]|\d+[.)])\s+/, "L ").replace(/[*_`\\]/g, "").replace(/-{2,}/g, "-").replace(/\s*\|\s*/g, "|").replace(/\s+/g, " ").trim();
  const CERCA = /^\s{0,3}(`{3,}|~{3,})/;
  const INICIO_DE_BLOCO = /^(\s*([-*+]|\d+[.)])\s|\s{0,3}#{1,6}(\s|$)|\s{0,3}>|\s*\||\s{0,3}([-*_])(\s*\4){2,}\s*$)/;
  const NAO_JUNTA = /^(\s{0,3}#{1,6}(\s|$)|\s{0,3}>|\s*\||\s{0,3}([-*_])(\s*\3){2,}\s*$)/;   // linha que não aceita continuação

  /* Linhas lógicas (parágrafo ou item de lista = uma linha, mesmo se quebrado no arquivo), cada uma com as linhas em branco que vinham
     antes (`gap`), as linhas físicas (`raws`) e o resto final do texto (`cauda`). */
  function analisar(texto) {
    const t = String(texto || "").replace(/\r\n/g, "\n");
    const cauda0 = t.match(/\n*$/)[0];
    const corpo = t.slice(0, t.length - cauda0.length);
    const linhas = [];
    let gap = [], cerca = null, recuado = false;
    if (corpo !== "") for (const l of corpo.split("\n")) {
      const f = l.match(CERCA);
      let emCodigo = !!cerca || !!f;                      // dentro de um bloco de código (ou na linha da cerca)
      if (f && !cerca) cerca = f[1][0];
      else if (f && cerca === f[1][0]) cerca = null;
      if (ehBranca(l)) { gap.push(l); continue; }
      const ant = linhas[linhas.length - 1];
      if (!emCodigo) {                                    // código recuado (4 espaços), depois de linha em branco e fora de item de lista
        const recua = /^( {4,}|\t)/.test(l);
        if (recuado && recua) emCodigo = true;
        else if (!recuado && recua && gap.length && !(ant && /^\s*([-*+]|\d+[.)])\s/.test(ant.raws[0].t))) { recuado = true; emCodigo = true; }
        else recuado = false;
      }
      const junta = ant && !gap.length && !emCodigo && !ant.cod && !INICIO_DE_BLOCO.test(l) && !NAO_JUNTA.test(ant.raws[0].t) && !/(\s{2,}|\\)$/.test(ant.raws[ant.raws.length - 1].t)
        && !(/\s\|\s/.test(l) || /\s\|\s/.test(ant.t));
      if (junta) { ant.raws.push({ t: l, gap: [] }); ant.t = ant.t + " " + l.trim(); ant.k = chave(ant.t); }
      else linhas.push({ t: l, gap, k: chave(l), cod: emCodigo, raws: [{ t: l, gap }] });
      gap = [];
    }
    return { linhas, cauda: gap.length ? gap.join("\n") + cauda0 : cauda0 };
  }

  /* Aplica `fn` só ao que está fora de `código inline`. */
  const foraDeCodigoInline = (linha, fn) => linha.split(/(`+[^`]*`+)/).map((p, i) => (i % 2 ? p : fn(p))).join("");
  const escapa = (p) => p.replace(/(^|[^\\])<(?=[A-Za-z\/!?])/g, "$1\\<").replace(/(^|[^\\])<(?=[A-Za-z\/!?])/g, "$1\\<");
  const desescapar = (l) => (l.cod ? l.t : foraDeCodigoInline(l.t, (p) => p.replace(/\\</g, "<")));

  /* O texto como o editor deve recebê-lo. */
  function paraEditor(md) {
    const A = analisar(md);
    const saida = [];
    for (const l of A.linhas) saida.push(...l.gap, l.cod ? l.t : foraDeCodigoInline(l.t, escapa));
    return saida.join("\n") + A.cauda;
  }

  /* Subsequência comum mais longa entre dois vetores de textos: devolve pares [i, j]. */
  function lcs(a, b) {
    const n = a.length, m = b.length;
    const tab = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) tab[i][j] = a[i] === b[j] ? tab[i + 1][j + 1] + 1 : Math.max(tab[i + 1][j], tab[i][j + 1]);
    const pares = [];
    let i = 0, j = 0;
    while (i < n && j < m) {
      if (a[i] === b[j]) { pares.push([i, j]); i++; j++; }
      else if (tab[i + 1][j] >= tab[i][j + 1]) i++;
      else j++;
    }
    return pares;
  }

  function marcadorDominante(linhas) {
    const c = { "-": 0, "*": 0, "+": 0 };
    for (const l of linhas) { const m = l.t.match(/^\s*([-*+])\s/); if (m) c[m[1]]++; }
    const top = Object.entries(c).sort((x, y) => y[1] - x[1])[0];
    return top[1] ? top[0] : null;
  }

  function mesclar(original, base, novo) {
    original = String(original ?? "").replace(/\r\n/g, "\n"); base = String(base ?? "").replace(/\r\n/g, "\n"); novo = String(novo ?? "").replace(/\r\n/g, "\n");
    if (novo === base) return original;                       // nada editado: o arquivo fica como estava
    const O = analisar(original), B = analisar(base), N = analisar(novo);
    if (!N.linhas.length) return novo;
    // quem de B corresponde a qual linha de O (por chave normalizada: ignora marcador de lista, recuo e ênfase)
    const parBO = new Map(lcs(O.linhas.map((l) => l.k), B.linhas.map((l) => l.k)).map(([o, b]) => [b, o]));
    const pares = lcs(B.linhas.map((l) => l.t), N.linhas.map((l) => l.t));
    const dom = marcadorDominante(O.linhas);
    const gapDe = (l) => l.gap.join("\n");
    const saida = [];
    const novaLinha = (l) => {
      let t = desescapar(l);
      if (dom && dom !== "*") t = t.replace(/^(\s*)\*(\s)/, `$1${dom}$2`);
      t = t.replace(/(\w)\\_(?=\w)/g, "$1_");              // o editor escreve YOUTUBE\_API\_KEY; entre letras o "_" não precisa de escape
      saida.push(...l.gap, t);
    };
    let j = 0, bAnt = -1;
    const ate = (jFim) => { while (j < jFim) novaLinha(N.linhas[j++]); };
    for (const [bi, nj] of pares) {
      const novas = nj - j;
      ate(nj);                                               // linhas novas antes desta
      // linhas apagadas entre a anterior e esta: a separação que elas tinham passa para esta (não cola a lista no parágrafo de cima)
      let herdada = [];
      if (!novas) for (let k = bAnt + 1; k < bi; k++) { const ok = parBO.get(k); if (ok !== undefined) { herdada = O.linhas[ok].gap; break; } }
      bAnt = bi;
      const oi = parBO.get(bi);
      const b = B.linhas[bi], n = N.linhas[nj];
      if (oi === undefined) {
        // sem par no arquivo: o editor transforma código recuado (4 espaços) em bloco com cerca; a cerca é invenção dele, não entra
        if (!CERCA.test(n.t)) saida.push(...n.gap, desescapar(n));
      }
      else {
        const o = O.linhas[oi];
        const gapProprio = gapDe(b) === gapDe(n) ? o.gap : n.gap;
        saida.push(...(herdada.length > gapProprio.length ? herdada : gapProprio), o.raws[0].t);   // a linha como estava no arquivo...
        for (const r of o.raws.slice(1)) saida.push(r.t);                       // ...com as suas quebras
      }
      j = nj + 1;
    }
    ate(N.linhas.length);
    return saida.join("\n") + O.cauda;
  }

  const api = { mesclar, analisar, chave, paraEditor };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else raiz.MesclaAgente = api;
})(typeof self !== "undefined" ? self : globalThis);
