// Tipo "fechamento": a pergunta de volta. Primeiro risca o rótulo, depois troca pela pergunta sobre o lugar.
// Campos do cenas.json: negacao (linhas), afirmacao (linhas), reforco (linhas), pergunta (linhas).
// Precisa de pelo menos 8 s: o convite final entra aos 240 frames.
const SCENA_FECHAMENTO = {
  draw(t, s) {
    let o = '';
    if (t < 90) {
      o += springCard(t, 0, { x: 540, y: 700, w: 960, h: 340, fill: cor('azul'), lines: s.negacao, size: 76, color: cor('branco') });
      const risco = easeOutCubic(prog(t, 40, 30));
      o += `<line x1="120" y1="700" x2="${(120 + 840 * risco).toFixed(1)}" y2="700" stroke="${cor('amarelo')}" stroke-width="22" stroke-linecap="round"/>`;
    } else {
      o += springCard(t - 90, 0, { x: 540, y: 700, w: 960, h: 340, fill: cor('amarelo'), lines: s.afirmacao, size: 88 });
    }
    o += springCard(t, 180, { x: 540, y: 1080, w: 980, h: 300, fill: cor('laranja'), lines: s.reforco, size: 68 });
    o += springCard(t, 240, { x: 540, y: 1420, w: 980, h: 300, fill: cor('branco'), lines: s.pergunta, size: 76 });
    return o;
  },
  sfx() {
    return [[0, 'impact'], [40, 'whoosh'], [90, 'whoosh'], [90, 'impact'], [180, 'ding'], [240, 'ding']];
  },
};
