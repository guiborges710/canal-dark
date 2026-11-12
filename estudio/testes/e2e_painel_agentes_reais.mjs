// Ida e volta fiel do editor visual com os agentes REAIS do repositório (PROG fora do quadro, pedido do Guilherme em 2026-11-09).
// Os arquivos reais só são LIDOS: são copiados para uma caixa temporária e é nela que o Corte sobe e que os testes salvam.
// Uso: node estudio/testes/e2e_painel_agentes_reais.mjs
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "..", "..");
const require = createRequire(path.join(REPO, "render", "package.json"));
const puppeteer = require("puppeteer-core");
const Mescla = createRequire(import.meta.url)(path.join(REPO, "estudio", "web", "corte_agente_merge.js"));
const PY = path.join(REPO, ".venv", "Scripts", "python.exe");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORTA = Number(process.env.E2E_PORTA) || 8799, BASE = `http://127.0.0.1:${PORTA}`;
const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "painel-reais-"));
const origem = path.join(REPO, ".claude", "agents");
const destino = path.join(caixa, ".claude", "agents");
fs.mkdirSync(destino, { recursive: true });
const ids = fs.readdirSync(origem).filter((f) => f.endsWith(".md")).map((f) => f.slice(0, -3)).filter((i) => !process.env.SO || i === process.env.SO);   // SO=<id> roda um só
for (const id of ids) fs.copyFileSync(path.join(origem, id + ".md"), path.join(destino, id + ".md"));

async function fimDoPrimeiroParagrafo(texto) {
  await pg.click(".toastui-editor-ww-container .ProseMirror > p");
  await pg.evaluate(() => { const p = document.querySelector(".toastui-editor-ww-container .ProseMirror > p"); const sel = getSelection(); sel.selectAllChildren(p); sel.collapseToEnd(); });
  await pg.keyboard.type(texto);
}
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const corpoDe = (t) => t.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/^---\n[\s\S]*?\n---\n?/, "");
let passou = 0; const falhas = [];
const confere = (c, n, extra) => { if (c) passou++; else { falhas.push(n); console.log(`  FALHOU  ${n}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, Number(process.env.VER) || 300)}` : ""}`); } };

const servidor = spawn(PY, [path.join(AQUI, "subir_painel_caixa.py"), caixa, String(PORTA)], { cwd: REPO, stdio: "ignore" });
for (let i = 0; i < 80; i++) { try { if ((await fetch(`${BASE}/api/painel/resumo`)).ok) break; } catch { /* subindo */ } await dormir(250); }
const nav = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"], defaultViewport: { width: 1440, height: 900 } });
const pg = await nav.newPage();
const erros = [];
pg.on("pageerror", (e) => erros.push(e.message));
pg.on("dialog", (d) => d.accept());
let comTabela = 0, comCodigo = 0, editados = 0;
try {
  for (const id of ids) {
    const bruto = fs.readFileSync(path.join(origem, id + ".md"), "utf-8");
    const original = corpoDe(bruto);
    await pg.goto(`${BASE}/painel/agentes/${id}`, { waitUntil: "domcontentloaded" });
    await pg.waitForFunction(() => window.PainelAgente && window.PainelAgente.pronto(), { timeout: 20000 });
    if (/^\|.*\|\s*$/m.test(original) && /^\|[\s:-]+\|/m.test(original)) comTabela++;
    if (/^```/m.test(original)) comCodigo++;
    // 1) abrir e salvar sem editar: o texto que iria para o disco é o original, byte a byte
    const semEdicao = await pg.evaluate(() => window.PainelAgente.corpoParaSalvar().instrucoes);
    confere(semEdicao === original, `${id}: ida e volta sem editar`, [semEdicao.length, original.length]);
    confere(await pg.$eval("#pn-ag-salvar", (b) => b.disabled), `${id}: Salvar desligado sem edição`);
    // 2) editar o fim do primeiro parágrafo: só essa linha muda
    const temP = await pg.evaluate(() => !!document.querySelector(".toastui-editor-ww-container .ProseMirror > p"));
    if (temP) {
      await fimDoPrimeiroParagrafo(" EDITADO");
      await pg.waitForFunction(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", { timeout: 5000 });
      const novo = await pg.evaluate(() => window.PainelAgente.corpoParaSalvar().instrucoes);
      // compara por linha lógica (um parágrafo ou item de lista quebrado em várias linhas no arquivo conta como uma)
      const a = Mescla.analisar(original).linhas.map((l) => l.t), b = Mescla.analisar(novo).linhas.map((l) => l.t);
      const mudadas = b.filter((l, i) => l !== a[i]);
      const primeira = a.find((l) => !/^(#|[-*+>|`]|\d+[.)] |\s)/.test(l));
      const ok = b.length === a.length && mudadas.length === 1 && mudadas[0] === primeira + " EDITADO";
      confere(ok, `${id}: editar um parágrafo muda só essa linha, sem mexer no resto`, { linhas: [a.length, b.length], difs: a.map((l, i) => [i, l.slice(0, 80), (b[i] || "").slice(0, 80)]).filter((x) => x[1] !== x[2]).slice(1, 5), esperado: primeira.slice(0, 30) });
      editados++;
    }
  }
  // 3) salvar de verdade (na cópia) o agente com mais tabela/código: o disco muda só onde foi editado
  const ref = ids.find((i) => /^\|[\s:-]+\|/m.test(corpoDe(fs.readFileSync(path.join(origem, i + ".md"), "utf-8"))) && /^```/m.test(corpoDe(fs.readFileSync(path.join(origem, i + ".md"), "utf-8")))) || ids.find((i) => /^```/m.test(corpoDe(fs.readFileSync(path.join(origem, i + ".md"), "utf-8"))));
  if (ref) {
    const copia = path.join(destino, ref + ".md");
    const antes = corpoDe(fs.readFileSync(copia, "utf-8"));
    await pg.goto(`${BASE}/painel/agentes/${ref}`, { waitUntil: "domcontentloaded" });
    await pg.waitForFunction(() => window.PainelAgente && window.PainelAgente.pronto(), { timeout: 20000 });
    await fimDoPrimeiroParagrafo(" SALVO NA COPIA");
    await pg.waitForFunction(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", { timeout: 5000 });
    await pg.click("#pn-ag-salvar");
    await pg.waitForFunction(() => document.getElementById("pn-ag-status")?.dataset.estado === "salvo", { timeout: 15000 });
    const depois = corpoDe(fs.readFileSync(copia, "utf-8"));
    const A = antes.split("\n"), B = depois.split("\n");
    const mudadas = B.filter((l) => !A.includes(l));
    confere(B.length === A.length && mudadas.length === 1 && /SALVO NA COPIA/.test(mudadas[0]), `${ref}: salvo na cópia, só o parágrafo editado mudou no disco`, { linhas: [A.length, B.length], mudadas: mudadas.slice(0, 3) });
    const bruto = fs.readFileSync(copia, "utf-8").replace(/\r\n/g, "\n");
    const frontAntes = fs.readFileSync(path.join(origem, ref + ".md"), "utf-8").replace(/\r\n/g, "\n").match(/^---\n([\s\S]*?)\n---/)[1].split("\n").sort().join("\n");
    const frontDepois = bruto.match(/^---\n([\s\S]*?)\n---/)[1].split("\n").sort().join("\n");
    confere(frontAntes === frontDepois, `${ref}: o frontmatter salvo tem os mesmos campos`, [frontAntes.slice(0, 200), frontDepois.slice(0, 200)]);
  } else confere(false, "nenhum agente real com bloco de código para o teste de salvar");
  confere(erros.length === 0, "nenhum erro de JavaScript", erros.slice(0, 3));
} catch (e) { falhas.push(`interrompido: ${e.message}`); console.log(e.stack); }
await nav.close();
servidor.kill();
console.log(`${ids.length} agentes reais abertos (${comTabela} com tabela, ${comCodigo} com bloco de código, ${editados} editados em memória). ${passou} verificações ok, ${falhas.length} falhas.`);
if (falhas.length) process.exitCode = 1; else fs.rmSync(caixa, { recursive: true, force: true });
