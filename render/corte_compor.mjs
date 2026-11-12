// Passa pelo compositor do editor só os quadros do corte que têm legenda, asset ou enquadramento. Os outros já estão prontos em --frames.
// Uso: node corte_compor.mjs --compilado <compilado.json> --frames <pasta>
// Chrome é o local (CHROME_PATH sobrepõe o padrão), como no render.mjs. O desenho é o mesmo web/compositor.js da prévia.
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, all) => {
  if (v.startsWith('--')) acc.push([v.slice(2), all[i + 1]]);
  return acc;
}, []));
const CHROME = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
if (!existsSync(CHROME)) {
  console.error(`Chrome não encontrado em ${CHROME}. Defina CHROME_PATH.`);
  process.exit(2);
}
const comp = JSON.parse(readFileSync(args.compilado, 'utf-8'));
const pagina = pathToFileURL(path.join(here, '..', 'estudio', 'web', 'compositor.html')).href;
const fontes = pathToFileURL(path.join(here, '..', 'media', 'fonts')).href;

const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox', '--font-render-hinting=none', '--allow-file-access-from-files'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: comp.w, height: comp.h, deviceScaleFactor: 1 });
  await page.goto(pagina, { waitUntil: 'load' });
  const lista = await page.evaluate(async (c, urlFontes) => {
    await Compositor.iniciar(urlFontes);
    const canvas = document.getElementById('c');
    canvas.width = c.w; canvas.height = c.h;
    window.CTX = canvas.getContext('2d');
    window.C = c;
    window.IMAGENS = {};
    await Promise.all(Object.entries(c.recursos).map(([sha, url]) => new Promise((ok, erro) => {
      const im = new Image();
      im.onload = () => { window.IMAGENS[sha] = im; ok(); };
      im.onerror = () => erro(new Error(`asset ilegível: ${sha}`));
      im.src = url;
    })));
    const usaKalam = c.legendas.some((l) => l.estilo === 'caderno');
    if (usaKalam && !document.fonts.check("700 76px Kalam")) throw new Error('fonte Kalam não carregou');
    const saida = [];
    for (let f = 0; f < c.total_f; f++) if (Compositor.precisaCompor(Compositor.resolver(c, f))) saida.push(f);
    return saida;
  }, comp, fontes);
  for (const f of lista) {
    const arq = path.join(args.frames, `${String(f + 1).padStart(4, '0')}.png`);
    const url = pathToFileURL(arq).href;
    await page.evaluate(async (fr, u) => {
      const base = new Image();
      await new Promise((ok, erro) => { base.onload = ok; base.onerror = () => erro(new Error(`quadro ilegível: ${u}`)); base.src = u; });
      Compositor.desenhar(window.CTX, window.C, Compositor.resolver(window.C, fr), base, window.IMAGENS);
    }, f, url);
    await page.screenshot({ path: arq, type: 'png' });
  }
  console.log(`compostos: ${lista.length} de ${comp.total_f} quadros`);
} finally {
  await browser.close();
}
