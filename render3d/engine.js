// Motor 3D do estilo "bonecos low-poly" (three.js, renderizado no Chrome local).
// Entrada: window.setSpec(spec) e window.renderFrame(n). Determinístico: só depende do frame.
import * as THREE from 'three';

const W = 1080, H = 1920;
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 200);

// ---------- utilidades ----------
const C = (h) => new THREE.Color(h);
const mats = new Map();
function mat(color, o = {}) {
  const k = color + JSON.stringify(o);
  if (!mats.has(k)) {
    mats.set(k, new THREE.MeshStandardMaterial({
      color, flatShading: o.flat !== false, roughness: o.rough ?? 0.78, metalness: o.metal ?? 0,
      emissive: o.emissive ?? 0x000000, emissiveIntensity: o.ei ?? 1, transparent: !!o.alpha, opacity: o.alpha ?? 1,
    }));
  }
  return mats.get(k);
}
function mesh(geo, m, o = {}) {
  const me = new THREE.Mesh(geo, m);
  me.castShadow = o.cast !== false; me.receiveShadow = o.recv !== false;
  if (o.pos) me.position.set(...o.pos);
  if (o.rot) me.rotation.set(...o.rot);
  if (o.scale) me.scale.set(...o.scale);
  return me;
}
const box = (w, h, d, m, o) => mesh(new THREE.BoxGeometry(w, h, d), m, o);
const cyl = (rt, rb, h, seg, m, o) => mesh(new THREE.CylinderGeometry(rt, rb, h, seg), m, o);
const sph = (r, ws, hs, m, o) => mesh(new THREE.SphereGeometry(r, ws, hs), m, o);
const ease = (x) => x * x * (3 - 2 * x);
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const lerp = (a, b, t) => a + (b - a) * t;
const outBack = (x) => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

function textTex(lines, o = {}) {
  const w = o.w || 512, h = o.h || 256;
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const g = cv.getContext('2d');
  if (o.bg) { g.fillStyle = o.bg; g.fillRect(0, 0, w, h); }
  g.fillStyle = o.fg || '#111'; g.textAlign = 'center'; g.textBaseline = 'middle';
  const arr = Array.isArray(lines) ? lines : [lines];
  const size = o.size || Math.floor(h / (arr.length + 0.6));
  g.font = `900 ${size}px 'Arial Black', Arial, sans-serif`;
  arr.forEach((ln, i) => g.fillText(ln, w / 2, h * (i + 1) / (arr.length + 1), w * 0.94));
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}
function gradTex(c1, c2) {
  const cv = document.createElement('canvas'); cv.width = 4; cv.height = 256;
  const g = cv.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, c1); gr.addColorStop(1, c2); g.fillStyle = gr; g.fillRect(0, 0, 4, 256);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
}

// ---------- personagens ----------
const PERSONAGENS = {
  jovem: { skin: 0xf2a25c, shirt: 0x2f9e6e, pants: 0x34405c, hair: 'bone', hairColor: 0xe5202e },
  pai:   { skin: 0xe89a58, shirt: 0xe9e4da, pants: 0x3a3f4d, hair: 'careca', hairColor: 0x3b2a1e, oculos: true },
  mae:   { skin: 0xf2b078, shirt: 0xe0587a, pants: 0x3a3f4d, hair: 'coque', hairColor: 0xd9a65a },
  tio:   { skin: 0xd68a4c, shirt: 0xf2c230, pants: 0x2d3a63, hair: 'tufo', hairColor: 0x1d1612 },
  amigo: { skin: 0xf2a25c, shirt: 0xf08a24, pants: 0x34405c, hair: 'tufo', hairColor: 0x1d1612 },
};

const EXPR = {
  // [sobrancelha esq (ângulo), dir, altura, boca, abertura dos olhos]
  neutro:   [0, 0, 0, 'linha', 1],
  feliz:    [0.1, -0.1, 0.03, 'sorriso', 1],
  bravo:    [-0.45, 0.45, -0.03, 'linha', 0.85],
  triste:   [0.4, -0.4, 0.03, 'triste', 0.9],
  surpreso: [0.1, -0.1, 0.1, 'o', 1.25],
  duvida:   [0.35, 0.05, 0.05, 'linha', 1],
  cansado:  [0.15, -0.15, -0.02, 'linha', 0.45],
  falando:  [0.05, -0.05, 0.02, 'fala', 1],
};
// braço = [balanço p/ frente, abertura lateral, flexão do cotovelo]
const POSES = {
  neutro:   { L: [0.0, 0.12, 0.12], R: [0.0, 0.12, 0.12] },
  relax:    { L: [0.05, 0.2, 0.25], R: [0.05, 0.2, 0.25] },
  aponta:   { L: [0.0, 0.12, 0.12], R: [1.5, 0.1, 0.1] },
  encolhe:  { L: [0.5, 0.55, 1.25], R: [0.5, 0.55, 1.25] },
  comemora: { L: [0.2, 2.5, 0.3], R: [0.2, 2.5, 0.3] },
  pensa:    { L: [0.0, 0.12, 0.12], R: [0.9, -0.1, 2.3] },
  cruzado:  { L: [0.35, -0.5, 2.1], R: [0.35, -0.5, 2.1] },
  segura:   { L: [0.9, 0.15, 0.9], R: [0.9, 0.15, 0.9] },
  volante:  { L: [0.85, 0.35, 0.7], R: [0.85, 0.35, 0.7] },
  mostra:   { L: [0.0, 0.12, 0.12], R: [0.7, 0.55, 0.9] },
  maos_alto:{ L: [1.0, 0.6, 0.4], R: [1.0, 0.6, 0.4] },
  cabeca:   { L: [0.0, 0.12, 0.12], R: [0.6, 0.6, 2.4] },
  quadril:  { L: [0.1, 0.75, 1.3], R: [0.1, 0.75, 1.3] },
  gesto_l:  { L: [0.6, 0.6, 1.0], R: [0.0, 0.12, 0.12] },
};

function makeChar(nome, extra = {}) {
  const P = { ...(PERSONAGENS[nome] || PERSONAGENS.jovem), ...extra };
  const skin = mat(P.skin, { flat: false, rough: 0.7 }), shirt = mat(P.shirt), pants = mat(P.pants), shoe = mat(0x23232b);
  const hairM = mat(P.hairColor);
  const root = new THREE.Group();
  const hip = new THREE.Group(); hip.position.y = 0.95; root.add(hip);
  const A = { root, hip, arms: {}, legs: {} };

  // pernas
  for (const s of [-1, 1]) {
    const th = new THREE.Group(); th.position.set(s * 0.19, 0, 0); hip.add(th);
    th.add(cyl(0.135, 0.12, 0.5, 8, pants, { pos: [0, -0.25, 0] }));
    const kn = new THREE.Group(); kn.position.y = -0.5; th.add(kn);
    kn.add(cyl(0.12, 0.105, 0.45, 8, pants, { pos: [0, -0.225, 0] }));
    kn.add(box(0.2, 0.1, 0.34, shoe, { pos: [0, -0.5, 0.07] }));
    A.legs[s] = { th, kn };
  }
  // tronco
  const torso = new THREE.Group(); hip.add(torso); A.torso = torso;
  torso.add(cyl(0.4, 0.43, 0.88, 9, shirt, { pos: [0, 0.44, 0] }));
  torso.add(cyl(0.5, 0.41, 0.3, 9, shirt, { pos: [0, 0.78, 0] }));
  torso.add(sph(0.13, 8, 6, skin, { pos: [0, 0.98, 0] }));
  // cabeça
  const head = new THREE.Group(); head.position.y = 1.0; torso.add(head); A.head = head;
  const hd = sph(0.52, 28, 20, skin, { pos: [0, 0.5, 0] }); head.add(hd);
  const face = new THREE.Group(); face.position.set(0, 0.5, 0); head.add(face);
  const R = 0.52, black = mat(0x14141a, { flat: false });
  A.eyes = [];
  for (const s of [-1, 1]) {
    const x = s * 0.2, y = 0.06, z = Math.sqrt(R * R - x * x - y * y);
    const e = sph(0.062, 12, 10, black, { pos: [x, y, z - 0.005], scale: [1, 1.3, 0.35], cast: false });
    e.lookAt(x * 2, y * 2, z * 2); face.add(e); A.eyes.push(e);
    const bx = x, by = y + 0.16, bz = Math.sqrt(R * R - bx * bx - by * by);
    const br = new THREE.Group(); br.position.set(bx, by, bz - 0.01); br.lookAt(bx * 2, by * 2, bz * 2);
    br.add(box(0.15, 0.032, 0.025, black, { cast: false })); face.add(br); (A.brows ||= []).push(br);
  }
  const mY = -0.17, mZ = Math.sqrt(R * R - mY * mY) - 0.01;
  const mouth = new THREE.Group(); mouth.position.set(0, mY, mZ); mouth.lookAt(0, mY * 2, mZ * 2); face.add(mouth); A.mouth = mouth;
  const dark = mat(0x3a0e12, { flat: false });
  A.mLinha = box(0.17, 0.03, 0.02, black, { cast: false });
  A.mAberta = sph(0.1, 12, 10, dark, { scale: [1, 0.55, 0.25], cast: false });
  A.mSorriso = mesh(new THREE.TorusGeometry(0.1, 0.019, 6, 16, Math.PI), black, { rot: [0, 0, Math.PI], cast: false, pos: [0, 0.05, 0] });
  A.mTriste = mesh(new THREE.TorusGeometry(0.09, 0.019, 6, 16, Math.PI), black, { cast: false, pos: [0, -0.04, 0] });
  A.mO = sph(0.055, 10, 8, dark, { scale: [1, 1.2, 0.3], cast: false });
  mouth.add(A.mLinha, A.mAberta, A.mSorriso, A.mTriste, A.mO);
  // cabelo / acessórios
  const hy = 0.5;
  if (P.hair === 'tufo') {
    for (const dx of [-0.07, 0, 0.07]) {
      const t = mesh(new THREE.TorusGeometry(0.07, 0.014, 5, 10, Math.PI * 0.8), hairM, { pos: [dx, hy + 0.52, 0.05], rot: [0.2, 0, dx * 4 + 0.4], cast: false });
      head.add(t);
    }
  } else if (P.hair === 'coque') {
    head.add(mesh(new THREE.IcosahedronGeometry(0.58, 1), hairM, { pos: [0, hy + 0.06, -0.08], scale: [1, 1, 0.95] }));
    head.add(mesh(new THREE.IcosahedronGeometry(0.2, 1), hairM, { pos: [0, hy + 0.62, -0.1] }));
    // franja: recorte frontal em pele para aparecer o rosto
    head.add(sph(0.5, 24, 16, skin, { pos: [0, hy - 0.02, 0.1], scale: [0.82, 0.86, 0.8], cast: false }));
    face.position.z = 0.0;
  } else if (P.hair === 'bone') {
    const cap = mesh(new THREE.SphereGeometry(0.545, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.36), mat(P.hairColor), { pos: [0, hy + 0.02, -0.03], rot: [-0.22, 0, 0] });
    head.add(cap);
    head.add(box(0.5, 0.045, 0.34, mat(P.hairColor), { pos: [0, hy + 0.36, 0.4], rot: [0.25, 0, 0] }));
  } else if (P.hair === 'careca') {
    for (const dx of [-0.06, 0.06]) head.add(mesh(new THREE.TorusGeometry(0.06, 0.012, 5, 8, Math.PI * 0.8), hairM, { pos: [dx, hy + 0.52, 0.04], rot: [0.2, 0, dx * 5 + 0.4], cast: false }));
  }
  if (P.oculos) {
    const gm = mat(0x1a1a22, { flat: false });
    for (const s of [-1, 1]) {
      const x = s * 0.2, y = 0.06, z = Math.sqrt(R * R - x * x - y * y);
      const ring = mesh(new THREE.TorusGeometry(0.115, 0.014, 6, 18), gm, { pos: [x, y, z + 0.01], cast: false });
      ring.lookAt(x * 2, y * 2, z * 2); face.add(ring);
    }
    face.add(box(0.1, 0.015, 0.015, gm, { pos: [0, 0.07, R - 0.005], cast: false }));
  }
  // braços
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 0.55, 0.82, 0); torso.add(sh);
    sh.add(sph(0.14, 8, 6, shirt, { cast: true }));
    sh.add(cyl(0.105, 0.095, 0.46, 8, shirt, { pos: [0, -0.23, 0] }));
    const el = new THREE.Group(); el.position.y = -0.46; sh.add(el);
    el.add(cyl(0.09, 0.08, 0.4, 8, skin, { pos: [0, -0.2, 0] }));
    el.add(sph(0.115, 10, 8, skin, { pos: [0, -0.46, 0], scale: [1, 1.1, 0.8] }));
    A.arms[s] = { sh, el };
  }
  root.traverse((o) => { if (o.isMesh) { o.castShadow = true; } });
  A.cur = { L: [0, 0.12, 0.12], R: [0, 0.12, 0.12] };
  return A;
}

function poseAt(lista, t, tabela, def) {
  // lista: 'nome' | [[t, 'nome'], ...] -> valor interpolado entre o par de chaves (mistura de 0,3 s)
  if (!lista) return tabela[def];
  if (typeof lista === 'string') return tabela[lista];
  let i = 0;
  for (let k = 0; k < lista.length; k++) if (t >= lista[k][0]) i = k;
  const atual = tabela[lista[i][1]], ant = i > 0 ? tabela[lista[i - 1][1]] : atual;
  const m = i > 0 ? ease(clamp01((t - lista[i][0]) / 0.3)) : 1;
  return { __mix: [ant, atual, m] };
}
function mixArm(p, lado) {
  if (p.__mix) { const [a, b, m] = p.__mix; return a[lado].map((v, i) => lerp(v, b[lado][i], m)); }
  return p[lado];
}

function animChar(A, a, t, env) {
  const seed = a._seed;
  const p = poseAt(a.pose, t, POSES, 'neutro');
  const speak = a.fala ? env : 0;
  const breath = Math.sin(t * 2.2 + seed) * 0.012;
  A.torso.scale.y = 1 + breath;
  // braços (L = lado -x, R = lado +x)
  for (const [lado, s] of [['L', -1], ['R', 1]]) {
    const v = mixArm(p, lado), arm = A.arms[s];
    const wob = a.fala ? Math.sin(t * 7 + seed + s) * 0.08 * speak : Math.sin(t * 1.5 + seed + s) * 0.02;
    arm.sh.rotation.x = -(v[0] + wob);
    arm.sh.rotation.z = s * v[1];
    arm.el.rotation.x = -(v[2] + wob * 0.8);
  }
  // pernas
  for (const s of [-1, 1]) {
    const lg = A.legs[s];
    if (a.sentado) { lg.th.rotation.x = -Math.PI / 2; lg.kn.rotation.x = Math.PI / 2; }
    else { lg.th.rotation.x = 0; lg.kn.rotation.x = 0; }
  }
  A.root.position.y = (a.sentado ? -0.95 * (a.esc || 1) : 0) + (a.pos ? a.pos[1] : 0) + (a.salta ? Math.abs(Math.sin(t * 6)) * 0.12 : 0);
  // cabeça: olhar + balanço da fala
  const ol = a.olhar || [0, 0];
  A.head.rotation.y = ol[0] + Math.sin(t * 0.9 + seed) * 0.03;
  A.head.rotation.x = -ol[1] + Math.sin(t * 1.3 + seed) * 0.015 + speak * 0.04 * Math.sin(t * 9);
  A.head.rotation.z = (a.inclina || 0) + Math.sin(t * 0.7 + seed) * 0.015;
  // expressão
  let ex = poseAt(a.expr, t, EXPR, 'neutro');
  let ev = ex.__mix ? ex.__mix[1].map((v, i) => typeof v === 'number' ? lerp(ex.__mix[0][i], v, ex.__mix[2]) : v) : ex;
  if (ex.__mix && ex.__mix[2] < 0.5) ev[3] = ex.__mix[0][3];
  A.brows[0].rotation.z = ev[0] * -1; A.brows[1].rotation.z = ev[1] * -1;
  A.brows.forEach((b) => { b.position.y = 0.06 + 0.16 + ev[2]; });
  const blink = (Math.sin(t * 1.9 + seed * 3) > 0.985 || ((t + seed) % 3.4) < 0.12) ? 0.12 : 1;
  A.eyes.forEach((e) => { e.scale.y = 1.3 * ev[4] * blink; });
  let tipo = ev[3];
  if (a.fala) tipo = 'fala';
  A.mLinha.visible = tipo === 'linha'; A.mSorriso.visible = tipo === 'sorriso'; A.mTriste.visible = tipo === 'triste';
  A.mO.visible = tipo === 'o'; A.mAberta.visible = tipo === 'fala';
  if (tipo === 'fala') { A.mAberta.scale.set(1.0, 0.18 + 0.75 * speak, 0.25); A.mAberta.position.y = 0; }
  if (a.fala && ev[3] === 'sorriso' && speak < 0.12) { A.mAberta.visible = false; A.mSorriso.visible = true; }
}

// ---------- objetos ----------
function makeObj(o) {
  const g = new THREE.Group();
  const cor = o.cor ?? 0xe5202e;
  switch (o.tipo) {
    case 'carro': {
      const body = mat(cor, { rough: 0.5 }), glass = mat(0x9ad4ff, { rough: 0.2, metal: 0.2 }), tire = mat(0x1b1b20);
      g.add(box(2.2, 0.55, 1.0, body, { pos: [0, 0.5, 0] }));
      if (o.aberto) {
        g.add(box(0.08, 0.5, 0.95, glass, { pos: [0.45, 1.0, 0], rot: [0, 0, -0.5] }));
        g.add(box(0.5, 0.3, 0.9, mat(0x3a3f4d), { pos: [-0.55, 0.9, 0] }));
        g.add(box(0.5, 0.18, 0.4, mat(0x3a3f4d), { pos: [-0.05, 0.84, 0.3] })); g.add(box(0.5, 0.18, 0.4, mat(0x3a3f4d), { pos: [-0.05, 0.84, -0.3] }));
      } else {
        g.add(box(1.2, 0.5, 0.92, body, { pos: [-0.05, 0.98, 0] }));
        g.add(box(1.05, 0.34, 0.94, glass, { pos: [-0.05, 1.0, 0] }));
      }
      g.add(box(0.1, 0.18, 0.2, mat(0xfff2b0, { emissive: 0xffe9a0, ei: 0.6 }), { pos: [1.1, 0.55, 0.33] }));
      g.add(box(0.1, 0.18, 0.2, mat(0xfff2b0, { emissive: 0xffe9a0, ei: 0.6 }), { pos: [1.1, 0.55, -0.33] }));
      for (const [x, z] of [[-0.7, 0.5], [0.7, 0.5], [-0.7, -0.5], [0.7, -0.5]]) {
        const w = cyl(0.26, 0.26, 0.18, 12, tire, { pos: [x, 0.26, z], rot: [Math.PI / 2, 0, 0] }); w.name = 'roda'; g.add(w);
      }
      break;
    }
    case 'moto': {
      const body = mat(cor, { rough: 0.5 }), tire = mat(0x1b1b20);
      for (const x of [-0.55, 0.55]) { const w = cyl(0.3, 0.3, 0.12, 12, tire, { pos: [x, 0.3, 0], rot: [Math.PI / 2, 0, 0] }); w.name = 'roda'; g.add(w); }
      g.add(box(1.0, 0.18, 0.2, body, { pos: [0, 0.55, 0] }));
      g.add(box(0.5, 0.2, 0.28, mat(0x222228), { pos: [-0.15, 0.78, 0] }));
      g.add(box(0.12, 0.5, 0.12, body, { pos: [0.5, 0.65, 0], rot: [0, 0, -0.3] }));
      g.add(box(0.1, 0.1, 0.5, mat(0x222228), { pos: [0.6, 0.9, 0] }));
      break;
    }
    case 'cnh': {
      const t = textTex(o.linhas || ['CNH'], { w: 512, h: 320, bg: '#f4f1e8', fg: '#1a3b8c' });
      const card = box(1.0, 0.64, 0.04, mat(0xf4f1e8, { flat: false })); g.add(card);
      const face = new THREE.Mesh(new THREE.PlaneGeometry(0.96, 0.6), new THREE.MeshBasicMaterial({ map: t })); face.position.z = 0.022; g.add(face);
      break;
    }
    case 'placa': { // quadro com texto
      const w = o.w || 1.8, h = o.h || 1.0;
      const t = textTex(o.linhas || ['?'], { w: 640, h: Math.round(640 * h / w), bg: o.bg || '#ffffff', fg: o.fg || '#111122', size: o.size });
      g.add(box(w + 0.1, h + 0.1, 0.06, mat(o.moldura ?? 0x1b2a4a, { flat: false })));
      const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: t })); face.position.z = 0.032; g.add(face);
      if (o.poste) g.add(box(0.1, o.poste, 0.08, mat(0x555a66), { pos: [0, -(h / 2 + o.poste / 2), -0.03] }));
      break;
    }
    case 'notas': { // pilha de cédulas
      const n = o.n || 4;
      for (let i = 0; i < n; i++) g.add(box(0.7, 0.06, 0.34, mat(i % 2 ? 0x2f9e6e : 0x3bb37e), { pos: [(i % 2) * 0.03, 0.03 + i * 0.062, 0], rot: [0, (i - n / 2) * 0.05, 0] }));
      break;
    }
    case 'chave': {
      const m = mat(0xf2c230, { metal: 0.4, rough: 0.35 });
      g.add(mesh(new THREE.TorusGeometry(0.16, 0.05, 6, 14), m, { rot: [Math.PI / 2, 0, 0] }));
      g.add(box(0.5, 0.07, 0.07, m, { pos: [0.4, 0, 0] })); g.add(box(0.08, 0.07, 0.14, m, { pos: [0.55, 0, -0.07] }));
      break;
    }
    case 'barra': { // barra 3D que cresce (escala Y controlada por o.h)
      const b = box(o.w || 0.9, 1, o.d || 0.9, mat(cor)); b.geometry.translate(0, 0.5, 0); b.scale.y = o.h || 1; b.name = 'barra'; g.add(b);
      break;
    }
    case 'rotulo': { // texto solto (cartela plana)
      const t = textTex(o.linhas || ['?'], { w: 640, h: o.hpx || 200, fg: o.fg || '#ffffff', size: o.size });
      const p = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 2.4, (o.w || 2.4) * (o.hpx || 200) / 640), new THREE.MeshBasicMaterial({ map: t, transparent: true }));
      g.add(p);
      break;
    }
    case 'calendario': {
      const t = textTex(o.linhas || ['16'], { w: 400, h: 400, bg: '#ffffff', fg: '#e5202e' });
      g.add(box(1.2, 1.2, 0.08, mat(0xe5202e)));
      const f = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.0), new THREE.MeshBasicMaterial({ map: t })); f.position.set(0, -0.06, 0.045); g.add(f);
      break;
    }
    case 'volante': {
      const m = mat(0x1b1b20);
      g.add(mesh(new THREE.TorusGeometry(0.4, 0.06, 8, 20), m)); g.add(cyl(0.1, 0.1, 0.1, 8, m, { rot: [Math.PI / 2, 0, 0] }));
      g.add(box(0.8, 0.07, 0.07, m));
      break;
    }
    case 'urna': {
      g.add(box(0.9, 0.9, 0.7, mat(0x8e949f), { pos: [0, 0.45, 0] }));
      g.add(box(0.7, 0.3, 0.05, mat(0x1b1b20), { pos: [0, 0.62, 0.36], rot: [-0.3, 0, 0] }));
      g.add(box(0.6, 0.2, 0.03, mat(0x7fe0a0, { emissive: 0x4fc080, ei: 0.7 }), { pos: [0, 0.62, 0.385], rot: [-0.3, 0, 0] }));
      g.add(box(0.7, 0.25, 0.3, mat(0xf2f2ea), { pos: [0, 0.25, 0.3] }));
      break;
    }
    case 'cone': {
      g.add(cyl(0.02, 0.28, 0.7, 10, mat(0xff7a1a), { pos: [0, 0.35, 0] })); g.add(box(0.7, 0.06, 0.7, mat(0x222228), { pos: [0, 0.03, 0] }));
      g.add(cyl(0.12, 0.17, 0.12, 10, mat(0xffffff), { pos: [0, 0.34, 0] }));
      break;
    }
    case 'arvore': {
      g.add(cyl(0.12, 0.16, 0.8, 7, mat(0x7a5232), { pos: [0, 0.4, 0] }));
      g.add(mesh(new THREE.IcosahedronGeometry(0.7, 0), mat(0x3a9a5a), { pos: [0, 1.2, 0] }));
      break;
    }
    case 'predio': {
      const w = o.w || 2, h = o.h || 4, d = o.d || 2;
      g.add(box(w, h, d, mat(cor, { flat: true }), { pos: [0, h / 2, 0] }));
      for (let y = 0.8; y < h - 0.4; y += 0.9) for (let x = -w / 2 + 0.45; x < w / 2 - 0.2; x += 0.7)
        g.add(box(0.36, 0.5, 0.05, mat(0xffe9a8, { emissive: 0xffd878, ei: 0.4 }), { pos: [x, y, d / 2 + 0.01], cast: false }));
      break;
    }
    case 'cadeira': {
      const m = mat(cor ?? 0x6b4a2b);
      g.add(box(0.9, 0.1, 0.9, m, { pos: [0, 0.5, 0] }));
      for (const [x, z] of [[-0.38, -0.38], [0.38, -0.38], [-0.38, 0.38], [0.38, 0.38]]) g.add(box(0.08, 0.5, 0.08, m, { pos: [x, 0.25, z] }));
      g.add(box(0.9, 0.8, 0.08, m, { pos: [0, 0.95, -0.41] }));
      break;
    }
    case 'sofa': {
      const m = mat(cor ?? 0x7a3f8f);
      g.add(box(2.6, 0.5, 1.0, m, { pos: [0, 0.25, 0] })); g.add(box(2.6, 0.7, 0.25, m, { pos: [0, 0.75, -0.4] }));
      g.add(box(0.25, 0.65, 1.0, m, { pos: [-1.3, 0.45, 0] })); g.add(box(0.25, 0.65, 1.0, m, { pos: [1.3, 0.45, 0] }));
      break;
    }
    case 'lupa': {
      const m = mat(0x1b1b20);
      g.add(mesh(new THREE.TorusGeometry(0.3, 0.05, 8, 20), m)); g.add(cyl(0.04, 0.04, 0.5, 6, m, { pos: [0.24, -0.5, 0], rot: [0, 0, 0.5] }));
      g.add(mesh(new THREE.CircleGeometry(0.28, 20), mat(0xbfe6ff, { flat: false, alpha: 0.35 })));
      break;
    }
    case 'escudo': {
      g.add(cyl(0.5, 0.5, 0.12, 6, mat(0x2f6fe0), { rot: [Math.PI / 2, 0, 0] }));
      g.add(box(0.14, 0.46, 0.05, mat(0xffffff), { pos: [0, 0, 0.08] })); g.add(box(0.46, 0.14, 0.05, mat(0xffffff), { pos: [0, 0, 0.08] }));
      break;
    }
    default: throw new Error('objeto desconhecido: ' + o.tipo);
  }
  return g;
}

// ---------- cenários ----------
function makeEnv(nome) {
  const g = new THREE.Group(); const cfg = { bg: null, fundo: ['#2b4a9a', '#16224f'], luz: 1 };
  const floorY = 0;
  const addFloor = (cor, w = 40, d = 40) => g.add(box(w, 0.2, d, mat(cor, { flat: false, rough: 0.9 }), { pos: [0, -0.1, 0], cast: false }));
  if (nome === 'sala') {
    cfg.fundo = ['#4068c4', '#2a4590'];
    g.add(box(24, 9, 0.3, mat(0x4068c4, { flat: false }), { pos: [0, 4.5, -3.2], cast: false }));
    g.add(box(24, 0.35, 0.2, mat(0xf0e8d8, { flat: false }), { pos: [0, 0.18, -3.02], cast: false }));
    addFloor(0xc98a4b);
    // janela
    g.add(box(2.2, 2.6, 0.12, mat(0xf0e8d8, { flat: false }), { pos: [3.2, 3.6, -3.0], cast: false }));
    g.add(box(1.9, 2.3, 0.14, mat(0x7fb6ff, { flat: false, emissive: 0x4a7fd0, ei: 0.5 }), { pos: [3.2, 3.6, -2.98], cast: false }));
    // abajur
    g.add(box(0.9, 0.9, 0.7, mat(0xb86a2c, { flat: false }), { pos: [-3.0, 0.45, -2.5] }));
    g.add(cyl(0.3, 0.45, 0.6, 10, mat(0xfff0c8, { emissive: 0xffd48a, ei: 1.0 }), { pos: [-3.0, 1.2, -2.5], cast: false }));
  } else if (nome === 'rua') {
    cfg.bg = '#8cc8ff'; cfg.fundo = ['#6fb6ff', '#cfe9ff'];
    g.add(box(60, 0.1, 6, mat(0x3a3d46, { flat: false }), { pos: [0, -0.05, 0], cast: false }));
    g.add(box(60, 0.18, 4, mat(0xb9b6ac, { flat: false }), { pos: [0, 0.0, -5], cast: false }));
    g.add(box(60, 0.1, 20, mat(0x7ac98a, { flat: false }), { pos: [0, -0.06, -17], cast: false }));
    for (let x = -28; x < 28; x += 2.6) g.add(box(1.2, 0.02, 0.14, mat(0xf2f2ea), { pos: [x, 0.01, 0], cast: false }));
    const cores = [0xf2b266, 0x8fb4f2, 0xe887a0, 0xf2e07a, 0xa3d9a0, 0xc9a7f0];
    for (let i = 0; i < 14; i++) {
      const b = makeObj({ tipo: 'predio', w: 2.4 + (i * 7 % 5) * 0.3, h: 4 + (i * 11 % 6), d: 2.4, cor: cores[i % cores.length] });
      b.position.set(-26 + i * 4.1, 0, -9 - (i % 3) * 1.2); g.add(b);
    }
    for (let x = -12; x <= 12; x += 6) { const t = makeObj({ tipo: 'arvore' }); t.position.set(x + 1.5, 0, -5.8); g.add(t); }
  } else if (nome === 'mesa') {
    cfg.fundo = ['#4a86e0', '#1e3f94'];
    g.add(box(30, 0.4, 14, mat(0xd9893a, { flat: false, rough: 0.5 }), { pos: [0, -0.2, 1], cast: false }));
  } else { // estudio
    cfg.fundo = ['#4a86e0', '#1e3f94'];
    addFloor(0x2c4fa8);
  }
  g.traverse((o) => { if (o.isMesh) o.receiveShadow = true; });
  return { g, cfg };
}

// ---------- luz ----------
const hemi = new THREE.HemisphereLight(0xd8e4ff, 0xb07a50, 1.55); scene.add(hemi);
const key = new THREE.DirectionalLight(0xffe3b8, 1.7);
key.position.set(-4, 7, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 30 }); key.shadow.bias = -0.0006;
scene.add(key); scene.add(key.target);
const rim = new THREE.DirectionalLight(0x8fb0ff, 0.9); rim.position.set(5, 4, -4); scene.add(rim);

// ---------- timeline ----------
let SPEC = null; let SHOTS = [];
const elLeg = document.getElementById('leg');

function chunkLegenda(txt) {
  // palavras com *destaque*; 2 linhas de até ~17 caracteres por bloco
  let on = false;
  const ws = txt.trim().split(/\s+/).map((w) => {
    if (w.startsWith('*')) on = true;
    const d = on; if (w.endsWith('*') || /\*[.,!?:;…]*$/.test(w)) on = false;
    return { t: w.replace(/\*/g, ''), d };
  });
  const chunks = []; let cur = { lines: [[]], len: [0] };
  for (const w of ws) {
    const L = cur.lines.length - 1;
    if (cur.len[L] + w.t.length + 1 > 17 && cur.lines[L].length) {
      if (cur.lines.length === 2) { chunks.push(cur); cur = { lines: [[]], len: [0] }; }
      else { cur.lines.push([]); cur.len.push(0); }
    }
    const k = cur.lines.length - 1; cur.lines[k].push(w); cur.len[k] += w.t.length + 1;
  }
  if (cur.lines[0].length) chunks.push(cur);
  chunks.forEach((c) => { c.peso = c.lines.flat().reduce((s, w) => s + w.t.length + 1, 0); });
  return chunks;
}
function htmlChunk(c) {
  return c.lines.map((ln) => '<span class="l">' + ln.map((w) => w.d ? `<span class="t d">${w.t}</span>` : `<span class="t">${w.t}</span>`).join(' ') + '</span>').join('');
}

window.setSpec = (spec) => {
  SPEC = spec; SHOTS = []; let t0 = 0;
  const envs = {};
  for (const sh of spec.cenas) {
    const g = new THREE.Group(); g.visible = false; scene.add(g);
    if (!envs[sh.env]) envs[sh.env] = makeEnv(sh.env);
    const E = makeEnv(sh.env); g.add(E.g);
    const atores = (sh.atores || []).map((a, i) => {
      const A = makeChar(a.quem || 'jovem', a.visual || {});
      A.root.position.set(...(a.pos || [0, 0, 0])); A.root.position.y = 0;
      A.root.rotation.y = a.rotY || 0; A.root.scale.setScalar(a.esc || 1);
      g.add(A.root); return { A, a: { ...a, _seed: i * 1.7 + 0.3 } };
    });
    const objs = (sh.objetos || []).map((o) => {
      const og = makeObj(o); og.position.set(...(o.pos || [0, 0, 0])); og.rotation.set(...(o.rot || [0, 0, 0]));
      const sc = o.esc || 1; og.scale.setScalar(sc); g.add(og); return { og, o, sc };
    });
    SHOTS.push({ sh, g, atores, objs, t0, dur: sh.dur, E, chunks: chunkLegenda(sh.legenda || '') });
    t0 += sh.dur;
  }
  return { total: Math.round(t0 * spec.fps), fps: spec.fps };
};

function kfVal(kf, t, base) {
  if (!kf) return base;
  let a = kf[0], b = kf[kf.length - 1];
  if (t <= a[0]) return a[1];
  for (let i = 0; i < kf.length - 1; i++) if (t >= kf[i][0] && t <= kf[i + 1][0]) { a = kf[i]; b = kf[i + 1]; }
  if (t >= b[0] && a === b) return b[1];
  const m = ease(clamp01((t - a[0]) / Math.max(1e-6, b[0] - a[0])));
  return a[1].map((v, i) => lerp(v, b[1][i], m));
}

window.renderFrame = (n) => {
  const t = n / SPEC.fps;
  let S = SHOTS[SHOTS.length - 1];
  for (const s of SHOTS) if (t < s.t0 + s.dur) { S = s; break; }
  SHOTS.forEach((s) => { s.g.visible = s === S; });
  const lt = Math.min(t - S.t0, S.dur);
  const sh = S.sh;
  // fundo
  const E = S.E.cfg;
  scene.background = E.bg ? C(E.bg) : gradTex(E.fundo[0], E.fundo[1]);
  // envelope da fala (mouth)
  const envArr = sh.env_fala || [];
  const fi = Math.floor(lt * SPEC.fps);
  const env = envArr.length ? (envArr[Math.min(envArr.length - 1, Math.max(0, fi - Math.round((sh.fala_ini || 0) * SPEC.fps)))] || 0) : 0;
  for (const { A, a } of S.atores) {
    const kp = kfVal(a.kf, lt, a.pos || [0, 0, 0]);
    A.root.position.x = kp[0]; A.root.position.z = kp[2];
    animChar(A, { ...a, pos: kp }, lt, env);
    if (a.kfRot) A.root.rotation.y = kfVal(a.kfRot, lt, [a.rotY || 0])[0];
  }
  for (const { og, o, sc } of S.objs) {
    const p = kfVal(o.kf, lt, o.pos || [0, 0, 0]); og.position.set(...p);
    if (o.kfRot) og.rotation.set(...kfVal(o.kfRot, lt, o.rot || [0, 0, 0]));
    const ent = o.entra ?? 0; const m = clamp01((lt - ent) / 0.35);
    og.visible = lt >= ent && (o.sai == null || lt < o.sai);
    og.scale.setScalar(sc * (m >= 1 ? 1 : Math.max(0.001, outBack(m))));
    if (o.tipo === 'barra') { const b = og.getObjectByName('barra'); b.scale.y = (o.h || 1) * ease(clamp01((lt - ent) / 0.6)) + 0.001; }
    og.traverse((c) => { if (c.name === 'roda') c.rotation.x += 0; });
    if (o.gira) og.rotation.y = (o.rot ? o.rot[1] : 0) + lt * o.gira;
    if (o.balanca) og.position.y = p[1] + Math.sin(lt * 4) * o.balanca;
  }
  // câmera
  const cam = sh.camera;
  const push = (cam.push || 0) * ease(clamp01(lt / S.dur));
  const pos = kfVal(cam.kf, lt, cam.pos).map((v, i) => v);
  const look = cam.look;
  const dir = [look[0] - pos[0], look[1] - pos[1], look[2] - pos[2]];
  camera.position.set(pos[0] + dir[0] * push + Math.sin(lt * 0.7) * 0.015, pos[1] + dir[1] * push, pos[2] + dir[2] * push);
  camera.lookAt(...look); camera.fov = cam.fov || 35; camera.updateProjectionMatrix();
  key.target.position.set(look[0], 0.5, look[2]); key.position.set(look[0] - 4, 7, look[2] + 6);
  // luz do cenário
  hemi.intensity = sh.luz ?? 1.55;
  renderer.render(scene, camera);
  // legenda
  if (S.chunks.length) {
    const ini = sh.fala_ini ?? 0.05, fim = sh.fala_fim ?? S.dur;
    const tot = S.chunks.reduce((s, c) => s + c.peso, 0); let acc = ini, idx = 0;
    for (let i = 0; i < S.chunks.length; i++) { const d = (fim - ini) * S.chunks[i].peso / tot; if (lt >= acc) idx = i; acc += d; }
    const c = S.chunks[idx]; if (elLeg.dataset.k !== n + '') { /* sempre atualiza */ }
    elLeg.innerHTML = htmlChunk(c);
    elLeg.style.display = (lt >= ini - 0.02 && !sh.sem_legenda) ? 'block' : 'none';
  } else elLeg.style.display = 'none';
  return true;
};
window.ready = true;
