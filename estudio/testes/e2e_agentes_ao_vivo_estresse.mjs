// PROG-003 (QA, Alisson): tentativas de quebrar a aba Ao vivo. Servidor de verdade numa caixa descartável (claude simulado).
// Cobre: troca rápida de abas, aba oculta/visível em rajada, servidor MORTO de verdade e de volta, consulta que devolve lixo.
// Uso: node estudio/testes/e2e_agentes_ao_vivo_estresse.mjs
import { spawn, execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "..", "..");
const require = createRequire(path.join(REPO, "render", "package.json"));
const puppeteer = require("puppeteer-core");
const PY = path.join(REPO, ".venv", "Scripts", "python.exe");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORTA = Number(process.env.E2E_PORTA) || 8802, BASE = `http://127.0.0.1:${PORTA}`;
const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "ao-vivo-estresse-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
let passou = 0, servidor, navegador, pagina, lixo = false;
const falhas = [], errosJs = [];
const confere = (c, n, e) => { if (c) { passou++; console.log(`  ok  ${n}`); } else { falhas.push(n); console.log(`  FALHOU  ${n}${e !== undefined ? " -> " + JSON.stringify(e).slice(0, 400) : ""}`); } };
const sobe = () => { servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" }); };
async function esperarServidor() { for (let i = 0; i < 120; i++) { try { if ((await fetch(`${BASE}/api/fluxos`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }
const txt = (s) => pagina.evaluate((x) => document.querySelector(x)?.innerText ?? null, s);

try {
  sobe(); await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  pagina = await navegador.newPage();
  pagina.on("pageerror", (e) => errosJs.push(String(e)));
  await pagina.setRequestInterception(true);
  pagina.on("request", (r) => { if (lixo && /\/api\/agentes\/ao-vivo$/.test(r.url())) return r.respond({ status: 200, contentType: "application/json", body: "{\"agentes\": 7, \"resumo\": null}" }); r.continue(); });
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });

  console.log("\n[A] Troca rápida de abas (teclas e cliques, 60 trocas sem pausa)");
  for (let i = 0; i < 30; i++) {
    await pagina.evaluate(() => { document.getElementById("aba-catalogo")?.click(); document.getElementById("aba-ao-vivo")?.click(); });
  }
  for (let i = 0; i < 10; i++) { await pagina.keyboard.press("ArrowRight"); await pagina.keyboard.press("ArrowLeft"); }
  await dormir(1500);
  confere(errosJs.length === 0, "Troca rápida: nenhum erro de JavaScript", errosJs);
  confere(await pagina.evaluate(() => document.querySelectorAll("#ag-vivo").length <= 1 && document.querySelectorAll("#ag-lista").length <= 1), "Troca rápida: sem DOM duplicado");
  await pagina.evaluate(() => document.getElementById("aba-ao-vivo")?.click());
  await dormir(500);
  confere(!!(await txt("#ag-vazio")), "Volta ao Ao vivo com estado vazio correto");

  console.log("\n[B] Catálogo -> Ao vivo -> ficha -> Ao vivo, navegando pelo histórico");
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  for (let i = 0; i < 5; i++) { await pagina.goBack(); await pagina.goForward(); }
  await dormir(800);
  confere(errosJs.length === 0, "Voltar/avançar rápido: nenhum erro de JavaScript", errosJs);

  console.log("\n[C] Aba oculta e visível em rajada");
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  let pedidos = 0; pagina.on("request", (r) => { if (/ao-vivo$/.test(r.url())) pedidos++; });
  await pagina.evaluate(() => { for (let i = 0; i < 30; i++) { Object.defineProperty(document, "hidden", { configurable: true, get: () => i % 2 === 0 }); document.dispatchEvent(new Event("visibilitychange")); } Object.defineProperty(document, "hidden", { configurable: true, get: () => true }); document.dispatchEvent(new Event("visibilitychange")); });
  await dormir(500); pedidos = 0; await dormir(9000);
  confere(pedidos <= 1, "Oculta: 9 s sem consultas novas (no máximo 1 já agendada)", pedidos);
  await pagina.evaluate(() => { delete document.hidden; document.dispatchEvent(new Event("visibilitychange")); });
  await dormir(1000);
  confere(pedidos >= 1, "Ao voltar, consulta na hora", pedidos);

  console.log("\n[D] Servidor MORTO de verdade e de volta");
  servidor.kill(); try { execFileSync("taskkill", ["/F", "/T", "/PID", String(servidor.pid)], { stdio: "ignore" }); } catch { /* já morreu */ }
  await dormir(10000);
  const faixa = await pagina.evaluate(() => document.body.innerText);
  confere(/Sem atualização/.test(faixa), "Servidor morto: faixa 'Sem atualização' aparece", faixa.slice(0, 200));
  confere(!/undefined|NaN/.test(faixa), "Servidor morto: sem 'undefined/NaN'");
  confere(errosJs.length === 0, "Servidor morto: nenhum erro de JavaScript", errosJs);
  await dormir(25000);
  confere(/no computador/i.test(await pagina.evaluate(() => document.body.innerText)), "Mais de 30 s fora: faixa vermelha com orientação");
  sobe(); await esperarServidor(); await dormir(6000);
  confere(/Atualizado|^(?!.*Sem atualização)/s.test(await pagina.evaluate(() => document.body.innerText)) && !(await pagina.evaluate(() => /Sem atualização desde/.test(document.body.innerText))), "Servidor de volta: faixa de erro some");

  console.log("\n[E] Resposta com formato inesperado (200 com lixo)");
  lixo = true; await dormir(6000);
  const t = await pagina.evaluate(() => document.body.innerText);
  confere(errosJs.length === 0, "Resposta malformada: nenhum erro de JavaScript", errosJs);
  confere(!/undefined|NaN/.test(t), "Resposta malformada: sem 'undefined/NaN'", t.slice(0, 300));
  lixo = false; await dormir(6000);
  confere(errosJs.length === 0, "Fim: nenhum erro de JavaScript", errosJs);
} catch (e) {
  falhas.push(`exceção: ${e.message}`); console.log("  ERRO", e.stack || e.message);
} finally {
  try { if (navegador) await navegador.close(); } catch { /* fechado */ }
  try { if (servidor) servidor.kill(); } catch { /* ok */ }
  console.log(`\n${passou} verificações ok, ${falhas.length} falhas.`);
  process.exit(falhas.length ? 1 : 0);
}
