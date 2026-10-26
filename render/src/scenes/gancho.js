// Tipo "gancho": a ideia mais forte logo no início. Dois números, a explicação e a pergunta com tremor.
// Campos do cenas.json: numeros (2 textos), cores (2 nomes), legenda, pergunta, rodape.
const SCENA_GANCHO = {
  draw(t, s) {
    const cores = s.cores || ['azul', 'laranja'];
    let o = '';
    o += springCard(t, 0, { x: 290, y: 560, w: 400, h: 260, fill: cor(cores[0]), lines: [s.numeros[0]], size: 160, color: cor('branco') });
    o += arrow({ x: 540, y: 560, s: spring(t, 12).s, op: spring(t, 12).op });
    o += springCard(t, 16, { x: 790, y: 560, w: 400, h: 260, fill: cor(cores[1]), lines: [s.numeros[1]], size: 160 });
    o += springCard(t, 30, { x: 540, y: 830, w: 960, h: 200, fill: cor('branco'), lines: s.legenda, size: 58 });
    const tremor = shake(t, 66, 30, 22);
    o += springCard(t, 62, { x: 540 + tremor, y: 1130, w: 980, h: 330, fill: cor('amarelo'), lines: s.pergunta, size: 96, rot: -2 });
    const pulso = 1 + 0.03 * Math.sin(t * 0.6);
    o += springCard(t, 96, { x: 540, y: 1600, w: 760, h: 150, fill: cor('azul-claro'), lines: s.rodape || [], size: 58, s: pulso });
    return o;
  },
  // Frames relativos ao início da cena: impacto de entrada, dings nas revelações, tremor com impacto.
  sfx() {
    return [[0, 'impact'], [10, 'ding'], [16, 'ding'], [30, 'ding'], [62, 'whoosh'], [66, 'impact'], [96, 'ding']];
  },
};
