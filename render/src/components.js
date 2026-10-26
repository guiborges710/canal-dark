// Componentes reutilizáveis: cartões com contorno grafite e sombra sólida, entrada por mola,
// barras animadas, fundo em movimento e flash entre cenas. Retornam strings SVG.

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
// Progresso de 0 a 1 a partir de `start` (em frames) durante `dur` frames.
const prog = (f, start, dur) => clamp((f - start) / dur);
const easeOutBack = (t) => {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};
const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

// Mola: escala de 0.2 até 1 com ultrapassagem (overshoot). Opacidade sobe em 4 frames a partir do início.
function spring(f, start) {
  const t = prog(f, start, 18);
  return { s: lerp(0.2, 1, easeOutBack(t)), op: clamp((f - start + 4) / 4) };
}

// Tremor que decai: determinístico, só depende de f.
function shake(f, start, dur, amp) {
  const k = prog(f, start, dur);
  return f < start ? 0 : amp * (1 - k) * Math.sin(f * 1.9);
}

// Medida de texto com a mesma fonte do SVG. Reduz o corpo até caber na largura máxima.
const _medidor = document.createElement('canvas').getContext('2d');
function ajustaTamanho(linhas, tamanho, larguraMax) {
  let s = tamanho;
  for (; s > 24; s -= 2) {
    _medidor.font = `${s}px ${FONT}`;
    const maior = Math.max(...linhas.map((l) => _medidor.measureText(l).width));
    if (maior <= larguraMax) break;
  }
  return s;
}

// Cartão: retângulo com contorno grafite, sombra sólida deslocada e texto em uma ou mais linhas.
// x, y é o centro do cartão. Texto que não cabe é reduzido, nunca transborda.
function card({ x, y, w, h, fill, lines, size = 80, color = '#1F2937', s = 1, op = 1, rot = 0, lineGap = 1.15 }) {
  const sombra = 14;
  const corpo = ajustaTamanho(lines, size, w - 70);
  const n = lines.length;
  const bloco = corpo * lineGap;
  const primeiroY = -((n - 1) * bloco) / 2 + corpo * 0.36;
  const textos = lines
    .map((t, i) => `<text x="0" y="${(primeiroY + i * bloco).toFixed(1)}" text-anchor="middle" font-family="${FONT}" font-size="${corpo}" fill="${color}">${t}</text>`)
    .join('');
  return `<g opacity="${op.toFixed(3)}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot.toFixed(2)}) scale(${s.toFixed(4)})">
    <rect x="${-w / 2 + sombra}" y="${-h / 2 + sombra}" width="${w}" height="${h}" rx="28" fill="${cor('grafite')}"/>
    <rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="28" fill="${fill}" stroke="${cor('grafite')}" stroke-width="10"/>
    ${textos}
  </g>`;
}

// Cartão com a mola de entrada já aplicada. `start` é relativo ao início da cena.
function springCard(f, start, opts) {
  const { s, op } = spring(f, start);
  return card({ ...opts, s: (opts.s || 1) * s, op: op * (opts.op ?? 1) });
}

// Barra com contorno e sombra. `len` é o tamanho em pixels; `vertical` controla a direção.
function bar({ x, y, w, len, fill, vertical = false, grow = 1 }) {
  const sombra = 12;
  const L = len * grow;
  if (vertical) {
    return `<rect x="${x + sombra}" y="${y - L + sombra}" width="${w}" height="${L}" fill="${cor('grafite')}"/>
    <rect x="${x}" y="${y - L}" width="${w}" height="${L}" fill="${fill}" stroke="${cor('grafite')}" stroke-width="10"/>`;
  }
  return `<rect x="${x + sombra}" y="${y + sombra}" width="${L}" height="${w}" fill="${cor('grafite')}"/>
    <rect x="${x}" y="${y}" width="${L}" height="${w}" fill="${fill}" stroke="${cor('grafite')}" stroke-width="10"/>`;
}

// Seta desenhada com formas (não depende de glifo de fonte).
function arrow({ x, y, s = 1, op = 1, fill = cor('amarelo') }) {
  const forma = 'M -70 -24 L 10 -24 L 10 -60 L 90 0 L 10 60 L 10 24 L -70 24 Z';
  return `<g opacity="${op.toFixed(3)}" transform="translate(${x} ${y}) scale(${s.toFixed(4)})">
    <path d="${forma}" fill="${cor('grafite')}" transform="translate(12 12)"/>
    <path d="${forma}" fill="${fill}" stroke="${cor('grafite')}" stroke-width="10" stroke-linejoin="round"/>
  </g>`;
}

// Fundo: faixas diagonais e formas que se movem a cada frame, e barra de progresso.
function background(f, total) {
  let s = `<rect width="${W}" height="${H}" fill="${FUNDO}"/>`;
  for (let i = -6; i < 12; i++) {
    const x = i * 220 + ((f * 3) % 220);
    s += `<polygon points="${x},0 ${x + 90},0 ${x + 90 - 700},${H} ${x - 700},${H}" fill="${LISTRA}"/>`;
  }
  const paleta = [cor('azul-claro'), cor('amarelo'), cor('laranja'), cor('azul')];
  for (let i = 0; i < 9; i++) {
    const cx = ((i * 257 + f * 1.4) % (W + 200)) - 100;
    const cy = (i * 431 + 80 * Math.sin(f / 25 + i)) % H;
    const r = 26 + (i % 3) * 14;
    if (i % 2 === 0) {
      s += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r}" fill="${paleta[i % 4]}" stroke="${cor('grafite')}" stroke-width="6" opacity="0.55"/>`;
    } else {
      const lado = r * 1.4;
      s += `<rect x="${(cx - lado / 2).toFixed(1)}" y="${(cy - lado / 2).toFixed(1)}" width="${lado}" height="${lado}" transform="rotate(${(f * 2 + i * 30) % 360} ${cx.toFixed(1)} ${cy.toFixed(1)})" fill="${paleta[i % 4]}" stroke="${cor('grafite')}" stroke-width="6" opacity="0.55"/>`;
    }
  }
  s += `<rect x="60" y="1860" width="960" height="18" rx="9" fill="${cor('branco')}" stroke="${cor('grafite')}" stroke-width="5"/>`;
  s += `<rect x="60" y="1860" width="${(960 * f) / total}" height="18" rx="9" fill="${cor('amarelo')}"/>`;
  return s;
}

// Flash branco curto no corte entre cenas (6 frames de decaimento).
function flash(f, corte) {
  if (f < corte || f >= corte + 6) return '';
  const k = clamp(1 - (f - corte) / 6);
  return `<rect width="${W}" height="${H}" fill="#FFFFFF" opacity="${(0.9 * k).toFixed(3)}"/>`;
}

// Contador: número que sobe de 0 até `alvo` com easing. Valor inteiro mostra sem casa decimal;
// valor com decimal mostra uma casa, com vírgula (ex.: 27,7), para não arredondar o dado.
function counter(f, start, dur, alvo, unidade = '%') {
  const v = alvo * easeOutCubic(prog(f, start, dur));
  const txt = Number.isInteger(alvo) ? String(Math.round(v)) : (Math.round(v * 10) / 10).toFixed(1).replace('.', ',');
  return `${txt}${unidade}`;
}
