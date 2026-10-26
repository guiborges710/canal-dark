// Tipo "barras_horizontais": barras que crescem na horizontal (escala 0 a 100), com subtítulo, destaque e conclusão.
// Campos do cenas.json: titulo, subtitulo, barras [{rotulo, valor (0-100), cor}], destaque, conclusao.
const SCENA_BARRAS_HORIZONTAIS = {
  draw(t, s) {
    let o = '';
    o += springCard(t, 0, { x: 540, y: 330, w: 960, h: 200, fill: cor('azul-claro'), lines: s.titulo, size: 54 });
    if (s.subtitulo) {
      o += springCard(t, 20, { x: 540, y: 620, w: 960, h: 110, fill: cor('branco'), lines: s.subtitulo, size: 42 });
    }
    const unidade = 800; // comprimento da barra com 100%
    s.barras.forEach((b, i) => {
      const linha = 790 + i * 290;
      const inicio = 30 + i * 30;
      const g = easeOutCubic(prog(t, inicio, 50));
      const comp = (unidade * b.valor) / 100;
      o += `<text x="100" y="${linha}" font-family="${FONT}" font-size="46" fill="${cor('grafite')}">${b.rotulo}</text>`;
      o += bar({ x: 100, y: linha + 40, w: 90, len: comp, fill: cor(b.cor), grow: g });
      o += `<text x="${(100 + comp * g + 40).toFixed(1)}" y="${linha + 150}" font-family="${FONT}" font-size="90" fill="${cor('grafite')}">${counter(t, inicio, 50, b.valor)}</text>`;
    });
    if (s.destaque) o += springCard(t, 100, { x: 540, y: 1420, w: 1000, h: 200, fill: cor('amarelo'), lines: s.destaque, size: 56 });
    if (s.conclusao) o += springCard(t, 140, { x: 540, y: 1660, w: 1000, h: 170, fill: cor('laranja'), lines: s.conclusao, size: 50 });
    return o;
  },
  sfx(s) {
    const ev = [[0, 'ding']];
    s.barras.forEach((_, i) => ev.push([30 + i * 30, 'ding']));
    if (s.destaque) ev.push([100, 'ding']);
    return ev;
  },
};
