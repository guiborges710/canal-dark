// Motor: recebe o cenas.json (via setSpec), monta a linha do tempo e desenha cada frame.
// renderFrame(f) é chamado pelo render.mjs para cada frame. Não há aleatoriedade.
const TIPOS = {
  gancho: SCENA_GANCHO,
  barras: SCENA_BARRAS,
  barras_horizontais: SCENA_BARRAS_HORIZONTAIS,
  fechamento: SCENA_FECHAMENTO,
};
const FPS_MOTOR = 30;
let linha = []; // [{tipo, s, inicio, fim}] em frames absolutos
let total = 0;

function setSpec(spec) {
  linha = [];
  let cursor = 0;
  for (const s of spec) {
    if (!TIPOS[s.tipo]) throw new Error(`tipo de cena desconhecido: ${s.tipo}`);
    const n = Math.round(s.duracao * FPS_MOTOR);
    linha.push({ tipo: s.tipo, s, inicio: cursor, fim: cursor + n });
    cursor += n;
  }
  total = cursor;
  return { total };
}

// Eventos de som em frames absolutos: impacto + whoosh na entrada de cada cena (exceto a primeira),
// e os eventos próprios de cada tipo de cena.
function getTimeline() {
  const eventos = [];
  linha.forEach((c, i) => {
    if (i > 0) {
      eventos.push({ frame: c.inicio, kind: 'whoosh' });
      eventos.push({ frame: c.inicio, kind: 'impact' });
    }
    for (const [dt, kind] of TIPOS[c.tipo].sfx(c.s)) {
      eventos.push({ frame: c.inicio + dt, kind });
    }
  });
  eventos.sort((a, b) => a.frame - b.frame);
  return { total, fps: FPS_MOTOR, eventos };
}

function renderFrame(f) {
  const c = linha.find((x) => f >= x.inicio && f < x.fim) || linha[linha.length - 1];
  let o = background(f, total);
  o += TIPOS[c.tipo].draw(f - c.inicio, c.s);
  for (const x of linha.slice(1)) o += flash(f, x.inicio);
  document.getElementById('stage').innerHTML = o;
}
window.setSpec = setSpec;
window.getTimeline = getTimeline;
window.renderFrame = renderFrame;
