// E2E da etapa 2 (perfis) no painel de Clipes, com Chrome real.
// Perfis numa pasta temporária (CLIPES_PERFIS); os projetos de clipes_out/ são só lidos.
// Uso: node clipes/testes/e2e_perfis.mjs [pasta para capturas]
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
const PY = path.join(REPO, ".venv", "Scripts", "python.exe");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORTA = 8798, BASE = `http://127.0.0.1:${PORTA}`;
const CAPT = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "clipes-capt-"));
fs.mkdirSync(CAPT, { recursive: true });
const PERFIS = fs.mkdtempSync(path.join(os.tmpdir(), "clipes-perfis-"));
for (const f of fs.readdirSync(path.join(REPO, "clipes", "perfis"))) if (f.endsWith(".json")) fs.copyFileSync(path.join(REPO, "clipes", "perfis", f), path.join(PERFIS, f));

const falhas = [];
const ok = (c, m) => { console.log((c ? "  ok   " : "  FALHA ") + m); if (!c) falhas.push(m); };
const espera = ms => new Promise(r => setTimeout(r, ms));

const srv = spawn(PY, ["-m", "clipes", "painel", "--porta", String(PORTA), "--sem-navegador"],
  { cwd: REPO, env: { ...process.env, CLIPES_PERFIS: PERFIS, PYTHONIOENCODING: "utf-8" }, stdio: "ignore" });
let nav;
try {
  for (let i = 0; i < 40; i++) { try { await fetch(BASE + "/api/perfis"); break; } catch { await espera(250); } }
  nav = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  const pg = await nav.newPage();
  const erros = [];
  pg.on("pageerror", e => erros.push(String(e)));
  pg.on("dialog", d => d.accept());
  await pg.setViewport({ width: 1366, height: 900 });
  await pg.goto(BASE + "/", { waitUntil: "networkidle2" });
  await pg.waitForFunction(() => document.querySelectorAll("#selPerfil option").length >= 2);
  const opcoes = await pg.$$eval("#selPerfil option", os => os.map(o => o.value));
  ok(opcoes.includes("geral") && opcoes.includes("gta6"), "seletor lista Geral e GTA 6");
  ok(await pg.$eval("#selPerfil", e => e.value) === "geral", "Geral vem escolhido por padrão");
  ok((await pg.$eval("#perfilDesc", e => e.textContent)).length > 10, "descrição do perfil escolhido aparece");
  await pg.waitForFunction(() => document.getElementById("tPerfil").textContent !== "–", { timeout: 8000 }).catch(() => {});
  ok(/v\d/.test(await pg.$eval("#tPerfil", e => e.textContent)), "topo mostra o perfil do projeto ativo");

  // criar perfil personalizado pela interface
  await pg.click("#btnPerfis");
  await pg.waitForSelector("#dlgPerfis[open] #pf_nome");
  await pg.click("#pfNovo");
  await pg.type("#pf_nome", "Xadrez ao vivo");
  await pg.type("#pf_palavras_chave", "xeque\nmate\nsacrifício");
  await pg.$eval("#pf_duracao_min", e => { e.value = "15"; e.dispatchEvent(new Event("input", { bubbles: true })); });
  await pg.click("#pfSalvar");
  await pg.waitForFunction(() => /criado/.test(document.getElementById("pfMsg").textContent), { timeout: 8000 });
  const arq = path.join(PERFIS, "xadrez-ao-vivo.json");
  ok(fs.existsSync(arq), "perfil gravado em disco");
  const salvo = JSON.parse(fs.readFileSync(arq, "utf-8"));
  ok(salvo.palavras_chave.join("|") === "xeque|mate|sacrifício" && salvo.duracao.min === 15 && salvo.versao === 1, "campos salvos como digitados");
  await pg.screenshot({ path: path.join(CAPT, "perfis_gerenciador.png") });

  // editar gera versão 2
  await pg.$eval("#pf_quantidade", e => { e.value = "7"; e.dispatchEvent(new Event("input", { bubbles: true })); });
  await pg.click("#pfSalvar");
  await pg.waitForFunction(() => /versão 2/.test(document.getElementById("pfMsg").textContent), { timeout: 8000 });
  ok(fs.existsSync(path.join(PERFIS, "_historico", "xadrez-ao-vivo.v1.json")), "versão 1 guardada no histórico");

  // erro de validação aparece e nada é gravado
  await pg.$eval("#pf_duracao_max", e => { e.value = "5"; e.dispatchEvent(new Event("input", { bubbles: true })); });
  await pg.click("#pfSalvar");
  await pg.waitForFunction(() => document.getElementById("pfErro").textContent.length > 0, { timeout: 8000 });
  ok(JSON.parse(fs.readFileSync(arq, "utf-8")).versao === 2, "perfil inválido não é salvo e o erro aparece");

  // duplicar e arquivar
  await pg.click("#pfDuplicar");
  await pg.waitForFunction(() => /Cópia criada/.test(document.getElementById("pfMsg").textContent), { timeout: 8000 });
  ok(fs.existsSync(path.join(PERFIS, "xadrez-ao-vivo-cpia.json")) || fs.readdirSync(PERFIS).some(f => f.startsWith("xadrez-ao-vivo-") && f.endsWith(".json")), "duplicar cria outro arquivo");
  await pg.click("#pfArquivar");
  await pg.waitForFunction(() => /arquivado/.test(document.getElementById("pfMsg").textContent), { timeout: 8000 });
  await pg.click("#pfFechar");
  const depois = await pg.$$eval("#selPerfil option", os => os.map(o => o.value));
  ok(depois.includes("xadrez-ao-vivo") && !depois.some(v => v.startsWith("xadrez-ao-vivo-")), "novo perfil na escolha; o arquivado sai dela");

  // servidor recusa iniciar com perfil arquivado (sem baixar nada)
  const arquivado = fs.readdirSync(PERFIS).find(f => f.startsWith("xadrez-ao-vivo-")).replace(".json", "");
  const r = await pg.evaluate(async (pid) => { const x = await fetch("/api/iniciar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: "https://example.com/v", autor: "x", perfil: pid }) }); return [x.status, (await x.json()).erro]; }, arquivado);
  ok(r[0] === 400 && /arquivado/.test(r[1]), "iniciar com perfil arquivado é recusado");
  ok(erros.length === 0, "sem erro de JavaScript" + (erros.length ? ": " + erros[0] : ""));

  await pg.setViewport({ width: 390, height: 844 });
  await pg.click("#btnPerfis");
  await pg.waitForSelector("#dlgPerfis[open]");
  const larg = await pg.evaluate(() => document.getElementById("dlgPerfis").scrollWidth <= window.innerWidth + 1);
  ok(larg, "gerenciador cabe na largura do celular");
  await pg.screenshot({ path: path.join(CAPT, "perfis_celular.png") });
} catch (e) {
  ok(false, "exceção: " + e.message);
} finally {
  if (nav) await nav.close();
  srv.kill();
  fs.rmSync(PERFIS, { recursive: true, force: true });
}
console.log(`\n${falhas.length ? falhas.length + " FALHA(S)" : "TUDO OK"}  (capturas em ${CAPT})`);
process.exit(falhas.length ? 1 : 0);
