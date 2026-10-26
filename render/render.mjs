// Renderiza um cenas.json em frames PNG e grava a linha de eventos de som.
// Uso: node render.mjs --spec <cenas.json> --out <pasta-do-video>
// Saída: <out>/frames/0000.png ... e <out>/eventos.json (frames de som, para o media/sfx.py).
// Chrome é o local (CHROME_PATH sobrepõe o padrão). Nada é baixado.
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { mkdirSync, readFileSync, writeFileSync, rmSync, existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, all) => {
  if (v.startsWith('--')) acc.push([v.slice(2), all[i + 1]]);
  return acc;
}, []));
if (!args.spec || !args.out) {
  console.error('uso: node render.mjs --spec <cenas.json> --out <pasta>');
  process.exit(2);
}

const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
if (!existsSync(CHROME)) {
  console.error(`Chrome não encontrado em ${CHROME}. Defina CHROME_PATH.`);
  process.exit(2);
}

const spec = JSON.parse(readFileSync(args.spec, 'utf-8'));
const out = path.resolve(args.out);
const framesDir = path.join(out, 'frames');
rmSync(framesDir, { recursive: true, force: true });
mkdirSync(framesDir, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--no-sandbox', '--font-render-hinting=none'],
});
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(here, 'index.html')).href, { waitUntil: 'load' });
  await page.evaluate((s) => window.setSpec(s), spec);
  const { total, fps, eventos } = await page.evaluate(() => window.getTimeline());
  writeFileSync(path.join(out, 'eventos.json'), JSON.stringify({ total, fps, eventos }, null, 1), 'utf-8');

  for (let f = 0; f < total; f++) {
    await page.evaluate((n) => window.renderFrame(n), f);
    await page.screenshot({ path: path.join(framesDir, `${String(f).padStart(4, '0')}.png`), type: 'png' });
  }
  console.log(`frames: ${total} (${(total / fps).toFixed(1)} s a ${fps} fps)`);
} finally {
  await browser.close();
}
