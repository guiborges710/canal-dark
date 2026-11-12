// Renderiza um spec 3D em PNGs (um por quadro), em vários navegadores em paralelo.
// Uso: node render3d.mjs --spec <spec.json> --out <pasta/frames> [--workers 4] [--frames 12,40,90]
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { mkdirSync, readFileSync, existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, all) => {
  if (v.startsWith('--')) acc.push([v.slice(2), all[i + 1]]);
  return acc;
}, []));
if (!args.spec || !args.out) { console.error('uso: node render3d.mjs --spec <spec.json> --out <pasta>'); process.exit(2); }
const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
if (!existsSync(CHROME)) { console.error(`Chrome não encontrado em ${CHROME}.`); process.exit(2); }

const spec = JSON.parse(readFileSync(args.spec, 'utf-8'));
const out = path.resolve(args.out);
mkdirSync(out, { recursive: true });
const workers = Number(args.workers || 4);

async function abrir() {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
      '--allow-file-access-from-files', '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  page.on('pageerror', (e) => console.error('erro na página:', e.message));
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(here, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction('window.ready === true', { timeout: 30000 });
  const info = await page.evaluate((s) => window.setSpec(s), spec);
  return { browser, page, info };
}

const first = await abrir();
const total = first.info.total;
const lista = args.frames ? args.frames.split(',').map(Number) : Array.from({ length: total }, (_, i) => i);
console.log(`quadros: ${lista.length} de ${total} (${(total / spec.fps).toFixed(1)} s)`);

let next = 0, feitos = 0;
async function trabalhar(w) {
  while (true) {
    const i = next++; if (i >= lista.length) break;
    const f = lista[i];
    await w.page.evaluate((n) => window.renderFrame(n), f);
    await w.page.screenshot({ path: path.join(out, `${String(f + 1).padStart(4, '0')}.png`), type: 'png' });
    if (++feitos % 100 === 0) console.log(`  ${feitos}/${lista.length}`);
  }
}
const ws = [first];
for (let i = 1; i < Math.min(workers, lista.length); i++) ws.push(await abrir());
await Promise.all(ws.map(trabalhar));
await Promise.all(ws.map((w) => w.browser.close()));
console.log('ok');
