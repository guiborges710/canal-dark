// E2E da etapa 3 no painel de Clipes (Chrome real): fluxo V2, revisão das sugestões, agentes simulados,
// falha + "Tentar de novo", configuração de etapas e ajuste do perfil do projeto.
// Tudo em pastas temporárias (CLIPES_SAIDA, CLIPES_PERFIS); agentes pelo simulador (CLIPES_CLAUDE).
// Uso: node clipes/testes/e2e_fluxo.mjs [pasta para capturas]
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
const PORTA = 8799, BASE = `http://127.0.0.1:${PORTA}`;
const CAPT = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "clipes-capt-"));
fs.mkdirSync(CAPT, { recursive: true });
const SAIDA = fs.mkdtempSync(path.join(os.tmpdir(), "clipes-saida-"));
const PERFIS = fs.mkdtempSync(path.join(os.tmpdir(), "clipes-perfis-"));
for (const f of fs.readdirSync(path.join(REPO, "clipes", "perfis"))) if (f.endsWith(".json")) fs.copyFileSync(path.join(REPO, "clipes", "perfis", f), path.join(PERFIS, f));
const SLUG = "e2e-revisao", D = path.join(SAIDA, SLUG);
const env = { ...process.env, CLIPES_SAIDA: SAIDA, CLIPES_PERFIS: PERFIS, PYTHONIOENCODING: "utf-8",
  CLIPES_CLAUDE: JSON.stringify([PY, path.join(AQUI, "claude_simulado.py")]), CLIPES_SIM_FALHA: "totti-avaliador-potencial" };
execFileSync(PY, ["-m", "clipes.testes.preparar_e2e", SAIDA, SLUG], { cwd: REPO, env });

const falhas = [];
const ok = (c, m) => { console.log((c ? "  ok   " : "  FALHA ") + m); if (!c) falhas.push(m); };
const espera = ms => new Promise(r => setTimeout(r, ms));
const json = f => JSON.parse(fs.readFileSync(path.join(D, f), "utf-8"));
const clica = async (pg, sel) => { await pg.waitForSelector(sel + ":not([disabled])", { timeout: 15000 }); await pg.$eval(sel, b => b.click()); };
const no = (pg, id) => pg.$eval(`#fluxo li[data-id="${id}"]`, e => e.className).catch(() => "");
const esperaNo = (pg, id, st, ms = 240000) => pg.waitForFunction((i, s) => { const e = document.querySelector(`#fluxo li[data-id="${i}"]`); return e && e.classList.contains(s); }, { timeout: ms, polling: 500 }, id, st);

const srv = spawn(PY, ["-m", "clipes", "painel", "--porta", String(PORTA), "--sem-navegador"], { cwd: REPO, env, stdio: "ignore" });
let nav;
try {
  for (let i = 0; i < 40; i++) { try { await fetch(BASE + "/api/perfis"); break; } catch { await espera(250); } }
  nav = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"], protocolTimeout: 900000 });
  const pg = await nav.newPage();
  const erros = [];
  pg.on("pageerror", e => erros.push(String(e)));
  pg.on("dialog", d => d.accept());
  await pg.setViewport({ width: 1366, height: 900 });
  await pg.goto(BASE + "/", { waitUntil: "networkidle2" });
  await pg.waitForFunction(() => document.querySelector('#fluxo li[data-id="curadoria"]'), { timeout: 15000 });
  const ids = await pg.$$eval("#fluxo li", ls => ls.map(l => l.dataset.id));
  ok(ids.includes("curadoria") && ids.includes("revisao") && ids.at(-1) === "saida", "painel mostra o fluxo do projeto (com curadoria e revisão)");

  await pg.waitForSelector("#btnContinuar:not([hidden])", { timeout: 15000 });
  await pg.click("#btnContinuar");
  await esperaNo(pg, "revisao", "espera_voce");
  ok((await no(pg, "curadoria")).includes("concluido"), "Kaká (curadoria) concluído pelo painel");
  await pg.waitForSelector("#sugestoes:not([hidden]) li.sug");
  await pg.waitForSelector("#btnRefazerSug:not([disabled])", { timeout: 20000 });  // processamento terminou
  const nSug = await pg.$$eval("#listaSug li.sug", l => l.length);
  ok(nSug === 2, `sugestões aparecem (${nSug})`);
  const motivo = await pg.$eval("#listaSug li.sug .motivo", e => e.textContent);
  ok(motivo.length > 10 && !/viral/i.test(motivo), "cada sugestão mostra o motivo, sem prometer viralização");
  ok(/no original/.test(await pg.$eval("#listaSug li.sug .sug-cab", e => e.textContent)), "intervalo no vídeo original visível");
  ok(await pg.$eval("#btnContinuarSug", b => b.disabled), "Continuar fica travado sem decisão");
  await pg.screenshot({ path: path.join(CAPT, "fluxo_sugestoes.png"), fullPage: false });

  const [id1, id2] = await pg.$$eval("#listaSug li.sug", l => l.map(x => +x.dataset.id));
  const m1 = json("momentos.json").find(m => m.id === id1);
  await clica(pg, `li.sug[data-id="${id1}"] button[data-acao="aceito"]`);
  await pg.waitForFunction(i => document.querySelector(`li.sug[data-id="${i}"]`).classList.contains("aceito"), {}, id1);
  await clica(pg, `li.sug[data-id="${id2}"] button[data-acao="rejeitado"]`);
  await pg.waitForFunction(i => document.querySelector(`li.sug[data-id="${i}"]`).classList.contains("rejeitado"), {}, id2);
  await clica(pg, `li.sug[data-id="${id1}"] button[data-acao="ajustar"]`);
  await pg.waitForSelector("#limIni");
  await pg.$eval("#limIni", (e, v) => { e.value = String(v); e.dispatchEvent(new Event("input", { bubbles: true })); }, Math.round((m1.ini + 1) * 10) / 10);
  await clica(pg, `li.sug[data-id="${id1}"] button[data-acao="salvar-lim"]`);
  await pg.waitForFunction(() => /Limites salvos/.test(document.getElementById("msgSug").textContent), { timeout: 8000 })
    .catch(async e => { console.log("msgSug:", await pg.$eval("#msgSug", x => x.textContent), "| limIni:", await pg.$eval("#limIni", x => x.value).catch(() => "(sem campo)")); throw e; });
  const m1b = json("momentos.json").find(m => m.id === id1);
  ok(Math.abs(m1b.ini - (m1.ini + 1)) < 0.11 && m1b.ini_original === m1.ini, "limite ajustado salvo, com o original guardado");
  ok(json("momentos.json").find(m => m.id === id2).status === "rejeitado", "rejeição salva");

  await pg.waitForFunction(() => !document.getElementById("btnContinuarSug").disabled, { timeout: 8000 });
  await clica(pg, "#btnContinuarSug");
  await esperaNo(pg, "potencial", "falhou");
  ok(true, "falha do Totti aparece no nó dele");
  ok(fs.existsSync(path.join(D, "clipes", String(id1).padStart(2, "0") + ".mp4")), "corte da sugestão aceita gerado");
  ok(!fs.existsSync(path.join(D, "clipes", String(id2).padStart(2, "0") + ".mp4")), "sugestão rejeitada não virou corte");
  const tCorte = fs.statSync(path.join(D, "clipes", String(id1).padStart(2, "0") + ".mp4")).mtimeMs;
  await pg.waitForSelector('#fluxo li[data-id="potencial"] button[data-acao="rodar"]');
  await pg.screenshot({ path: path.join(CAPT, "fluxo_falha.png") });
  await clica(pg, '#fluxo li[data-id="potencial"] button[data-acao="rodar"]');
  await esperaNo(pg, "aprovacao", "espera_voce");
  ok(fs.statSync(path.join(D, "clipes", String(id1).padStart(2, "0") + ".mp4")).mtimeMs === tCorte, "tentar de novo não refez o corte");
  ok((await no(pg, "originalidade")).includes("concluido") && (await no(pg, "embalagem")).includes("concluido"), "check e embalagem concluídos");
  const corte = JSON.parse(fs.readFileSync(path.join(D, "clipes", String(id1).padStart(2, "0") + ".json"), "utf-8"));
  ok(Math.abs(corte.ini - m1b.ini) < 0.01 && corte.gancho === `GANCHO ${id1}`, "corte usa o limite ajustado e o gancho do Zidane");
  await clica(pg, '#fluxo li[data-id="aprovacao"] button[data-acao="aprovar"]');
  await esperaNo(pg, "saida", "concluido", 15000);
  ok(true, "aprovar fecha o fluxo");

  // configurar etapas
  await clica(pg, "#btnEtapas");
  await pg.waitForSelector("#dlgEtapas[open] #etLista li");
  const iCom = await pg.$$eval("#etLista li", ls => ls.findIndex(l => /comentário próprio/.test(l.textContent)));
  await pg.click(`#etLista li:nth-child(${iCom + 1}) input[data-ativa]`);
  ok(/precisa da etapa/.test(await pg.$eval("#etErro", e => e.textContent)) && await pg.$eval("#etSalvar", b => b.disabled), "desligar o comentário com o check ligado avisa e trava o salvar");
  await pg.click(`#etLista li:nth-child(${iCom + 1}) input[data-ativa]`);
  const iFigo = await pg.$$eval("#etLista li", ls => ls.findIndex(l => /gancho \(teaser\)/.test(l.textContent)));
  await pg.click(`#etLista button[data-sobe="${iFigo}"]`);
  await pg.select("#f_transcricao_modelo", "base");
  ok(!(await pg.$eval("#etSalvar", b => b.disabled)), "Figo antes do Zidane é aceito");
  await pg.screenshot({ path: path.join(CAPT, "fluxo_etapas.png") });
  await pg.click("#etSalvar");
  await pg.waitForFunction(() => /Salvo no projeto/.test(document.getElementById("etMsg").textContent), { timeout: 8000 });
  const fl = json("fluxo.json").etapas.map(e => e.id);
  ok(fl.indexOf("gancho") < fl.indexOf("comentario") && json("fluxo.json").etapas.find(e => e.id === "transcricao").ferramentas.modelo === "base", "ordem e ferramenta salvas no fluxo.json");
  await pg.click("#etFechar");

  // ajustar perfil só do projeto
  await clica(pg, "#btnPerfilProj");
  await pg.waitForSelector("#dlgPerfis[open] #pf_quantidade");
  ok(await pg.$eval("#dlgPerfis .pf-lista", e => e.hidden), "modo projeto esconde a lista de perfis");
  await pg.$eval("#pf_quantidade", e => { e.value = "3"; e.dispatchEvent(new Event("input", { bubbles: true })); });
  await pg.click("#pfSalvar");
  await pg.waitForFunction(() => /só neste projeto/.test(document.getElementById("pfMsg").textContent), { timeout: 8000 });
  ok(json("perfil.json").quantidade === 3 && json("perfil.json").ajustado_no_projeto, "perfil do projeto ajustado");
  ok(JSON.parse(fs.readFileSync(path.join(PERFIS, "geral.json"), "utf-8")).quantidade === 5, "perfil-base Geral não mudou");
  await pg.click("#pfFechar");
  ok(erros.length === 0, "sem erro de JavaScript" + (erros.length ? ": " + erros[0] : ""));
} catch (e) {
  ok(false, "exceção: " + e.message);
  try { const st = JSON.parse(fs.readFileSync(path.join(D, "estado.json"), "utf-8")); console.log(Object.entries(st.nos).map(([k, v]) => k + "=" + v.status + " " + (v.msg || "") + (v.detalhe ? "\n   >> " + v.detalhe.join(" | ") : "")).join("\n")); } catch {}
  try { console.log(fs.readFileSync(path.join(D, "processo.log"), "utf-8").slice(-1500)); } catch {}
} finally {
  if (nav) await nav.close();
  srv.kill();
  await espera(500);
  fs.rmSync(SAIDA, { recursive: true, force: true });
  fs.rmSync(PERFIS, { recursive: true, force: true });
}
console.log(`\n${falhas.length ? falhas.length + " FALHA(S)" : "TUDO OK"}  (capturas em ${CAPT})`);
process.exit(falhas.length ? 1 : 0);
