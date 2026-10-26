// Tipo "barras": barras verticais que crescem, com contador e rótulo abaixo de cada uma.
// Campos do cenas.json: titulo (linhas), barras [{rotulo, valor, cor}], escala_max, unidade, rodape (linhas), rodape_cor.
const SCENA_BARRAS = {
  draw(t, s) {
    const barras = s.barras;
    const unidade = s.unidade ?? '%';
    const k = 840 / s.escala_max; // altura máxima = 840 px
    const base = 1420;
    const xs = barras.map((_, i) => 540 + (i - (barras.length - 1) / 2) * 340);
    let o = '';
    o += springCard(t, 0, { x: 540, y: 300, w: 960, h: 200, fill: cor('azul-claro'), lines: s.titulo, size: 58 });
    barras.forEach((b, i) => {
      const inicio = 10 + i * 20;
      const g = easeOutCubic(prog(t, inicio, 40));
      o += bar({ x: xs[i] - 110, y: base, w: 220, len: b.valor * k, fill: cor(b.cor), vertical: true, grow: g });
      o += `<text x="${xs[i]}" y="${(base - b.valor * k * g - 50).toFixed(1)}" text-anchor="middle" font-family="${FONT}" font-size="96" fill="${cor('grafite')}">${counter(t, inicio, 40, b.valor, unidade)}</text>`;
      o += springCard(t, inicio - 2, { x: xs[i], y: base + 90, w: 260, h: 120, fill: cor('branco'), lines: [b.rotulo], size: 64 });
    });
    if (s.rodape) {
      o += springCard(t, 70, { x: 540, y: 1660, w: 1000, h: 160, fill: cor(s.rodape_cor || 'amarelo'), lines: s.rodape, size: 46 });
    }
    return o;
  },
  sfx(s) {
    const ev = [[0, 'ding']];
    s.barras.forEach((_, i) => ev.push([10 + i * 20, 'ding']));
    if (s.rodape) ev.push([70, 'ding']);
    return ev;
  },
};
