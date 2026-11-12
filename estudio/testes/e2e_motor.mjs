// PROG-006: o motor (Claude/Codex) e a nota aparecem na tela, em texto, no computador e no celular.
// Chrome real, servidor numa cópia descartável (sem rede, sem custo). Uso: node estudio/testes/e2e_motor.mjs [pasta de capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8801, BASE = `http://127.0.0.1:${PORTA}`, SLUG = "fim-dos-terceiros-lugares";
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "motor-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "motor-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });

let servidor, navegador, pagina, passou = 0;
const falhas = [], errosJs = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 500)}` : ""}`); } }
async function esperarServidor() { for (let i = 0; i < 120; i++) { try { if ((await fetch(`${BASE}/api/fluxos`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }

// Casos do desenho do Iniesta (ux/prog-003-006-agentes-desenho-b.md, tabela "Motor e nota").
const CASOS = {
  claude: { motor: "claude", motor_nota: null },
  claude_com_nota: { motor: "claude", motor_nota: "Rodou direto, sem troca." },
  codex_nota: { motor: "codex", motor_nota: "Executado pelo Codex: o Claude estava no limite." },
  codex_sem_nota: { motor: "codex", motor_nota: null },
  codex_nota_vazia: { motor: "codex", motor_nota: "   " },
  antigo: { id: 1 },
  motor_nulo: { motor: null, motor_nota: null },
  desconhecido: { motor: "gemini", motor_nota: null },
  comando: null,
};

async function casos() {
  console.log("\n[1] seloMotor: cada linha da tabela do desenho");
  await pagina.goto(`${BASE}/estudio/${SLUG}`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#e-agentes .agente-linha");
  const r = await pagina.evaluate((casos) => {
    const saida = {};
    for (const [k, j] of Object.entries(casos)) {
      const el = seloMotor(j);
      saida[k] = el ? { texto: el.innerText, html: el.outerHTML, aria: el.getAttribute("aria-label"), titulo: el.querySelector("[title]")?.title || el.title || null } : null;
    }
    return saida;
  }, CASOS);
  const t = (k) => (r[k] ? r[k].texto : null);
  confere(/Claude/.test(t("claude")) && !/Codex|undefined|null/.test(t("claude")), "Claude sem nota: só o chip 'Claude'", r.claude);
  confere(!/\n/.test(t("claude").trim()), "Claude sem nota: nenhuma linha extra", t("claude"));
  confere(t("claude_com_nota").includes("Claude") && t("claude_com_nota").includes("Rodou direto, sem troca."), "Claude com nota: mostra a nota", r.claude_com_nota);
  confere(t("codex_nota").includes("Codex") && t("codex_nota").includes("o Claude estava no limite"), "Codex com nota: chip e a nota", r.codex_nota);
  confere(!t("codex_nota").includes("reserva usada quando"), "Codex com nota: não repete a frase padrão", t("codex_nota"));
  confere(t("codex_sem_nota").includes("Codex") && t("codex_sem_nota").includes("reserva usada quando o Claude esgota o limite"), "Codex sem nota: frase padrão", r.codex_sem_nota);
  confere(t("codex_nota_vazia").includes("reserva usada quando o Claude esgota o limite"), "Nota só com espaços vale como sem nota", r.codex_nota_vazia);
  confere(r.antigo === null && r.motor_nulo === null && r.comando === null, "Job antigo, motor nulo e comando: nenhum selo (e nenhum erro)", [r.antigo, r.motor_nulo, r.comando]);
  confere(t("desconhecido").includes("Motor não informado") && !t("desconhecido").includes("gemini") && !t("desconhecido").includes("Outro:"), "Motor desconhecido aparece como 'Motor não informado'", r.desconhecido);
  for (const [k, v] of Object.entries(r)) if (v) confere(!/undefined|\bnull\b/.test(v.html), `Sem 'undefined' nem 'null' no selo (${k})`, v.html);
  confere(/mot[o]r/i.test(r.codex_nota.aria || "") && /Codex/.test(r.codex_nota.aria || ""), "Selo tem rótulo para leitor de tela", r.codex_nota.aria);
}

async function nasTelas() {
  console.log("\n[2] O selo aparece nas telas do Estúdio (lista de agentes, execução, faixas)");
  await pagina.goto(`${BASE}/estudio/${SLUG}`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#e-agentes .agente-linha");
  // Lista de agentes: um nó com job codex ganha o chip; os demais não mostram nada.
  const lista = await pagina.evaluate(() => {
    const d = Estudio.dados;
    const antes = document.querySelectorAll("#e-agentes .selo-motor").length;
    const alvo = d.linhas.find((x) => x.tipo !== "aprovacao");
    alvo.job = { id: 999, titulo: "Teste", status: "ok", motor: "codex", motor_nota: "Executado pelo Codex: o Claude estava no limite." };
    Estudio.agentes();
    const linha = document.querySelector(`#e-agentes .agente-linha[data-no="${alvo.no}"]`);
    return { antes, depois: document.querySelectorAll("#e-agentes .selo-motor").length, texto: linha.innerText, nome: alvo.no, tagFilho: linha.querySelector(".selo-motor")?.tagName };
  });
  confere(lista.antes === 0, "Lista de agentes sem job de agente: nenhum selo", lista.antes);
  confere(lista.depois === 1 && lista.texto.includes("Codex"), "Lista de agentes: o chip Codex aparece na linha do nó", lista);
  confere(lista.tagFilho !== "BUTTON", "O chip dentro da linha (que já é botão) não é outro botão", lista.tagFilho);

  // Diálogo de execução: linha 'Motor'.
  const dlg = await pagina.evaluate(() => {
    const d = Estudio.dados;
    const a = d.linhas.find((x) => x.tipo !== "aprovacao");
    const base = { ...a, agente: a.agente || "neymar-roteirista" };
    const abrir = (job) => { Estudio.abrirExecucao({ ...base, job }); const t = document.querySelector("#painel-execucao").innerText; document.querySelector("dialog").remove(); return t; };
    return {
      codex: abrir({ id: 998, titulo: "x", status: "ok", motor: "codex", motor_nota: "Executado pelo Codex: o Claude estava no limite." }),
      claude: abrir({ id: 997, titulo: "x", status: "ok", motor: "claude", motor_nota: null }),
      antigo: abrir({ id: 996, titulo: "x", status: "ok" }),
      semJob: abrir(null),
    };
  });
  confere(/Motor\s*\n?\s*Codex/.test(dlg.codex) && dlg.codex.includes("o Claude estava no limite"), "Execução: 'Motor: Codex' com a nota", dlg.codex);
  confere(/Motor\s*\n?\s*Claude/.test(dlg.claude), "Execução: 'Motor: Claude'", dlg.claude);
  confere(dlg.antigo.includes("Motor: não registrado (trabalho antigo).") && !/undefined|null/.test(dlg.antigo), "Execução de trabalho antigo: 'não registrado', sem undefined", dlg.antigo);
  confere(!/Motor/.test(dlg.semJob), "Execução sem job: nada sobre motor", dlg.semJob);

  // Faixa de execução e de falha na revisão (app.js).
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector(".trilho");
  const faixas = await pagina.evaluate(() => {
    const e = etapaAtual();
    e.job = { id: 995, titulo: "Escrevendo o roteiro", status: "rodando", motor: "codex", motor_nota: null };
    e.falha = { id: 994, titulo: "Cenas", erro: "boom", motor: "claude", motor_nota: null };
    desenharFaixas();
    return { exec: document.querySelector("#faixa-execucao")?.innerText, falha: document.querySelector("#faixa-falha")?.innerText };
  });
  confere(faixas.exec && faixas.exec.includes("Codex"), "Faixa 'em execução' mostra o motor", faixas.exec);
  confere(faixas.falha && faixas.falha.includes("Claude"), "Faixa 'falhou' mostra o motor", faixas.falha);
}

async function celular() {
  console.log("\n[3] Celular: o chip cabe na tela e abre a explicação ao toque");
  await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector(".trilho");
  await pagina.evaluate(() => {
    const e = etapaAtual();
    e.job = { id: 993, titulo: "Escrevendo o roteiro", status: "rodando", motor: "codex", motor_nota: "Executado pelo Codex: o Claude estava no limite, e a reserva assumiu o trabalho inteiro para não perder o que já tinha sido feito." };
    desenharFaixas();
  });
  const m = await pagina.evaluate(() => {
    const chip = document.querySelector("#faixa-execucao .selo-motor");
    const r = chip.getBoundingClientRect();
    const faixa = document.querySelector("#faixa-execucao").getBoundingClientRect();
    const botao = chip.matches("button") ? chip : chip.querySelector("button");
    return { dentro: r.left >= 0 && r.right <= innerWidth && faixa.right <= innerWidth + 1, rolagemLateral: document.documentElement.scrollWidth > innerWidth, alto: botao ? botao.getBoundingClientRect().height : 0, temBotao: !!botao };
  });
  confere(m.dentro && !m.rolagemLateral, "Celular: chip e faixa dentro da largura, sem rolagem lateral", m);
  confere(m.temBotao && m.alto >= 32, "Celular: o chip Codex é tocável", m);
  await pagina.tap("#faixa-execucao .selo-motor button, #faixa-execucao button.selo-motor");
  const aberto = await pagina.evaluate(() => document.querySelector("#faixa-execucao .motor-dica")?.innerText || "");
  confere(aberto.includes("O Claude estava no limite; este trabalho"), "Celular: tocar no chip abre a explicação (sem depender de hover)", aberto);
  await pagina.screenshot({ path: path.join(CAPTURAS, "motor-celular.png") });
}

try {
  servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" });
  await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  pagina = await navegador.newPage();
  await pagina.setViewport({ width: 1500, height: 1000 });
  pagina.on("pageerror", (e) => errosJs.push(String(e)));
  await casos();
  await nasTelas();
  await celular();
  confere(errosJs.length === 0, "Nenhum erro de JavaScript", errosJs);
} catch (e) {
  falhas.push(`exceção: ${e.message}`);
  console.log("  ERRO", e.stack || e.message);
} finally {
  try { if (navegador) await navegador.close(); } catch { /* fechado */ }
  if (servidor) servidor.kill();
  try { fs.rmSync(caixa, { recursive: true, force: true }); } catch { /* em uso */ }
}
console.log(`\n${passou} verificações ok, ${falhas.length} falha(s).`);
process.exit(falhas.length ? 1 : 0);
