// Acesso pelo celular: senha, recusas e layout, em Chrome com tela e toque de celular, chamando pelo IP do computador na rede (não por localhost).
// Numa cópia descartável; agentes simulados. Uso: node estudio/testes/e2e_celular.mjs [pasta para capturas]
import { spawn, execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "..", "..");
const require = createRequire(path.join(REPO, "render", "package.json"));
const puppeteer = require("puppeteer-core");
const PY = path.join(REPO, ".venv", "Scripts", "python.exe");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORTA = Number(process.env.E2E_PORTA) || 8801, SENHA = "teste-7k3mq", SLUG = "fim-dos-terceiros-lugares";
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "celular-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const ips = Object.values(os.networkInterfaces()).flat().filter((i) => i.family === "IPv4" && !i.internal && /^(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))/.test(i.address)).map((i) => i.address);
if (!ips.length) { console.log("Sem endereço de rede privada neste computador: não dá para testar o acesso pela rede."); process.exit(2); }
const LAN = ips[0], BASE = `http://${LAN}:${PORTA}`, LOCAL = `http://127.0.0.1:${PORTA}`;

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "celular-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });

let servidor, navegador, pagina, passou = 0;
const falhas = [], errosJs = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 400)}` : ""}`); } }
const captura = (n) => pagina.screenshot({ path: path.join(CAPTURAS, `${n}.png`) });
function subir(...args) { servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir", ...args], { cwd: REPO, env: { ...process.env, ...ambiente, ESTUDIO_SENHA: SENHA }, stdio: "ignore" }); }
async function esperar(base) { for (let i = 0; i < 120; i++) { try { await fetch(`${base}/api/fluxos`); return; } catch { await dormir(250); } } throw new Error("servidor não subiu"); }
async function parar() { if (servidor) { servidor.kill(); servidor = null; await dormir(900); } }
/* fetch com Host e Origin à escolha (o fetch do Node não deixa trocar o Host) */
const bruto = (url, { metodo = "GET", host, origem, cookie, corpo } = {}) => new Promise((ok, erro) => {
  const u = new URL(url);
  const h = { ...(host ? { Host: host } : {}), ...(origem ? { Origin: origem } : {}), ...(cookie ? { Cookie: cookie } : {}), ...(corpo ? { "Content-Type": "application/x-www-form-urlencoded", "Content-Length": Buffer.byteLength(corpo) } : {}) };
  const r = http.request({ hostname: u.hostname, port: u.port, path: u.pathname + u.search, method: metodo, headers: h, agent: false }, (res) => { let b = ""; res.on("data", (c) => { b += c; }); res.on("end", () => ok({ status: res.statusCode, headers: res.headers, corpo: b })); });
  r.on("error", erro); r.setTimeout(8000, () => r.destroy(new Error("tempo"))); if (corpo) r.write(corpo); r.end();
});
const entrar = (senha, extra = {}) => bruto(`${BASE}/acesso/entrar`, { metodo: "POST", corpo: `senha=${encodeURIComponent(senha)}`, ...extra });
const sqlite = (sql) => JSON.parse(execFileSync(PY, ["-c", `import json,os,sqlite3;c=sqlite3.connect(os.environ['ESTUDIO_DADOS']+'/estudio.db');c.row_factory=sqlite3.Row;print(json.dumps([dict(r) for r in c.execute(${JSON.stringify(sql)})]))`], { encoding: "utf-8", env: { ...process.env, ...ambiente } }));

async function sem_rede() {
  console.log(`\n[1] Sem --rede, o servidor não aceita ninguém da rede (testando ${LAN})`);
  subir();
  await esperar(LOCAL);
  let recusou = false;
  try { await bruto(`${BASE}/api/fluxos`); } catch (e) { recusou = /ECONNREFUSED|ECONNRESET|tempo/.test(String(e)); }
  confere(recusou, "A porta não abre para o IP da rede");
  confere((await bruto(`${LOCAL}/api/fluxos`)).status === 200, "No próprio computador continua funcionando");
  await parar();
}

async function senha_e_recusas() {
  console.log("\n[2] Com --rede: tudo exige senha, menos o computador");
  subir("--rede");
  await esperar(LOCAL);
  const pg = await bruto(`${BASE}/`);
  confere(pg.status === 401 && pg.corpo.includes('name="senha"') && !pg.corpo.includes("app.js"), "Sem senha, só a tela de entrada aparece", pg.status);
  for (const rota of ["/api/producoes", "/api/opcoes", "/api/temas", "/web/app.js", "/web/corte.css", `/api/producoes/${SLUG}/estudio`, "/blob/" + "a".repeat(64), "/quadro/" + "a".repeat(64), "/fontes/Kalam-Bold.ttf", `/download/${SLUG}?versao=1`]) {
    const r = await bruto(`${BASE}${rota}`);
    confere(r.status === 401, `Sem senha, ${rota.slice(0, 40)} responde 401`, r.status);
  }
  const jobsAntes = sqlite("SELECT COUNT(*) n FROM jobs")[0].n;
  const p1 = await bruto(`${BASE}/api/temas/gerar`, { metodo: "POST", corpo: "{}" });
  const p2 = await bruto(`${BASE}/api/producoes`, { metodo: "POST", corpo: "{}" });
  confere(p1.status === 401 && p2.status === 401 && sqlite("SELECT COUNT(*) n FROM jobs")[0].n === jobsAntes, "Sem senha, nada pode ser acionado", [p1.status, p2.status]);
  confere((await bruto(`${LOCAL}/api/producoes`)).status === 200, "No próprio computador, sem senha, continua igual");

  const err = await entrar("senha-errada");
  confere(err.status === 303 && err.headers.location === "/?acesso=erro" && !err.headers["set-cookie"], "Senha errada não entra e não dá cookie", err.headers);
  confere((await bruto(`${BASE}/?acesso=erro`)).corpo.includes("Senha incorreta"), "A tela de entrada diz que a senha está errada");
  const fora = await entrar(SENHA, { origem: "https://site-de-fora.example" });
  confere(fora.status === 403, "Entrar a partir de outro site é recusado, mesmo com a senha certa", fora.status);
  const hostRuim = await entrar(SENHA, { host: "site-de-fora.example" });
  confere(hostRuim.status === 403, "Nome de site de fora no Host é recusado (DNS rebinding)", hostRuim.status);

  const ok = await entrar(SENHA.toUpperCase());
  const cookie = (ok.headers["set-cookie"] || [""])[0];
  confere(ok.status === 303 && ok.headers.location === "/" && /corte_sessao=/.test(cookie), "Senha certa entra (sem diferenciar maiúscula)", ok.headers);
  confere(/HttpOnly/i.test(cookie) && /SameSite=Strict/i.test(cookie), "O cookie é HttpOnly e SameSite=Strict", cookie);
  const c = cookie.split(";")[0];
  confere((await bruto(`${BASE}/`, { cookie: c })).status === 200, "Com a sessão, a interface abre");
  confere((await bruto(`${BASE}/api/producoes`, { cookie: c })).status === 200, "Com a sessão, a API responde");
  confere((await bruto(`${BASE}/api/producoes`, { cookie: "corte_sessao=inventado" })).status === 401, "Sessão inventada não vale");
  confere((await bruto(`${BASE}/api/producoes`, { cookie: c, host: "site-de-fora.example" })).status === 403, "Com sessão, mas com Host de fora: recusado");
  const post = await bruto(`${BASE}/api/temas/gerar`, { metodo: "POST", cookie: c, corpo: "{}", origem: "https://site-de-fora.example" });
  confere(post.status === 403, "Com sessão, um POST vindo de outro site é recusado", post.status);
  const trav = await bruto(`${BASE}/web/..%2Fdados%2Fsenha_rede.txt`, { cookie: c });
  confere(![200, 206].includes(trav.status) && !trav.corpo.includes(SENHA), "A senha não vaza por caminho com ..", trav.status);
  const dados = await bruto(`${BASE}/web/../../estudio/dados/senha_rede.txt`, { cookie: c });
  confere(!dados.corpo.includes(SENHA), "Nem por .. direto");
  return c;
}

async function celular() {
  console.log("\n[3] No celular (390 x 844, toque): entrar e usar cada tela");
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required"] });
  pagina = await navegador.newPage();
  await pagina.setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1");
  await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  pagina.on("pageerror", (e) => errosJs.push(e.message));
  await pagina.goto(`${BASE}/`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#senha");
  await captura("01-entrar");
  confere(await pagina.evaluate(() => document.documentElement.scrollWidth <= innerWidth), "A tela de entrada cabe na largura do celular");
  await pagina.type("#senha", "senha-errada");
  await Promise.all([pagina.waitForNavigation({ waitUntil: "networkidle2" }), pagina.tap("button[type=submit]")]);
  confere((await pagina.evaluate(() => document.body.innerText)).includes("Senha incorreta"), "Senha errada mostra o aviso no celular");
  await pagina.type("#senha", SENHA);
  await Promise.all([pagina.waitForNavigation({ waitUntil: "networkidle2" }), pagina.tap("button[type=submit]")]);
  await pagina.waitForSelector("#novo");
  confere(true, "Digitando a senha, entra na interface");
  confere(await pagina.$eval("#nav-local", (e) => getComputedStyle(e).display === "none"), "O rótulo da barra superior some no celular, para dar lugar às telas");

  const cabe = async (nome) => {
    const m = await pagina.evaluate(() => { const a = document.getElementById("app"); return { app: a.scrollWidth - a.clientWidth, doc: document.documentElement.scrollWidth - innerWidth }; });
    confere(m.app <= 1 && m.doc <= 1, `${nome}: nada passa da largura da tela`, m);
  };
  await dormir(500);
  await cabe("Projetos");
  await captura("02-projetos");
  const linhas = await pagina.$$eval("table.lista tbody tr", (t) => t.map((r) => r.getBoundingClientRect().width));
  confere(linhas.length > 0 && linhas.every((w) => w <= 390), "Projetos: cada linha vira um cartão que cabe", linhas);

  await pagina.tap("#novo");
  await pagina.waitForSelector(".novo .estilo-cartao");
  await dormir(500);
  const dlg = await pagina.$eval(".novo", (e) => { const r = e.getBoundingClientRect(); return { l: r.left, r: r.right }; });
  confere(dlg.l >= 0 && dlg.r <= 390, "Novo projeto: a janela cabe", dlg);
  const grade = await pagina.$$eval(".estilo-cartao", (x) => x.map((e) => Math.round(e.getBoundingClientRect().width)));
  confere(grade.length === 4 && grade.every((w) => w >= 120 && w <= 190), "Novo projeto: os quatro estilos em duas colunas", grade);
  await captura("03-novo-projeto");
  await pagina.evaluate(() => document.querySelector("#tema").scrollIntoView());
  await pagina.tap("#gerar-tema");
  confere(true, "Novo projeto: o botão de gerar tema recebe toque");
  await pagina.evaluate(() => { const d = document.querySelector("dialog[open]"); d.close(); d.remove(); });

  // PROG-001: a explicação de "não se aplica" também precisa ser útil e caber no celular.
  const sim = await pagina.evaluate(async () => (await fetch("/api/producoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tema: "Teste celular de etapa sem uso", simulado: true }),
  })).json());
  await pagina.goto(`${BASE}/producao/${sim.slug}?etapa=componentes`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#c-corpo .vazio-etapa");
  const naoAplica = await pagina.$eval("#c-corpo", (e) => e.innerText);
  confere(/Produção simulada \(--mock\)/.test(naoAplica) && /Para aplicar/.test(naoAplica) && /sem --mock/.test(naoAplica), "PROG-001: motivo e próximo passo aparecem no celular", naoAplica);
  await cabe("PROG-001 no celular");

  // PROG-002/015: exercita com toque o mesmo disparo real usado pelo botão da etapa e pelo CTA do topo.
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=cenas`, { waitUntil: "networkidle2" });
  await pagina.evaluate((slug) => {
    const original = window.fetch.bind(window);
    window.__iniciosCelular = [];
    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input.url;
      if (url === `/api/producoes/${slug}/iniciar` && init.method === "POST") {
        window.__iniciosCelular.push(JSON.parse(init.body));
        return new Response(JSON.stringify({ job: 902, novo: true }), { status: 201, headers: { "Content-Type": "application/json" } });
      }
      const response = await original(input, init);
      if (url === `/api/producoes/${slug}` && (!init.method || init.method === "GET")) {
        const body = await response.clone().json();
        const cenas = body.etapas.find((e) => e.id === "cenas");
        cenas.acoes.iniciar = { rotulo: "Iniciar cenas", habilitado: true, motivos: [], refazer: false };
        body.resumo.proxima = { texto: "Iniciar cenas", etapa: "cenas", tipo: "voce", acao: "iniciar" };
        return new Response(JSON.stringify(body), { status: response.status, headers: { "Content-Type": "application/json" } });
      }
      return response;
    };
    atualizar();
  }, SLUG);
  await pagina.waitForSelector("#iniciar:not([disabled])");
  await pagina.tap("#iniciar");
  confere(await pagina.waitForFunction(() => /Trabalho iniciado/.test(document.querySelector("#avisos")?.innerText || "")).then(() => true).catch(() => false), "PROG-002: toque em Iniciar cenas mostra retorno imediato");
  let inicios = await pagina.evaluate(() => window.__iniciosCelular);
  confere(inicios.length === 1 && inicios[0].etapa === "cenas", "PROG-002: toque dispara a etapa cenas uma vez", inicios);
  await pagina.tap("#ir-proxima");
  await dormir(300);
  inicios = await pagina.evaluate(() => window.__iniciosCelular);
  confere(inicios.length === 2 && inicios[1].etapa === "cenas", "PROG-015: CTA do topo dispara a ação real no celular", inicios);
  await cabe("CTAs no celular");

  for (const [nome, url, espera] of [
    ["Estúdio", `/estudio/${SLUG}`, "#e-video"],
    ["Revisão", `/producao/${SLUG}?etapa=roteiro`, ".trilho"],
    ["Agentes (Catálogo)", "/agentes?aba=catalogo", ".ag-lista"],
    ["Agentes (Ao vivo)", "/agentes", ".ag-resumo"],
    ["Fluxos", "/fluxos/canal", ".fx-canvas"],
    ["Editor", `/editor/${SLUG}`, "#ed-tela"],
  ]) {
    await pagina.goto(`${BASE}${url}`, { waitUntil: "networkidle2" });
    await pagina.waitForSelector(espera, { timeout: 30000 });
    await dormir(700);
    await cabe(nome);
    await captura(`04-${nome.toLowerCase().replace("ú", "u")}`);
  }
  // Editor: o que o dedo precisa alcançar
  const ed = await pagina.evaluate(() => { const t = document.querySelector("#ed-tela").getBoundingClientRect(), x = document.querySelector("#exportar").getBoundingClientRect(); return { tela: [Math.round(t.left), Math.round(t.right), Math.round(t.height)], exportarVisivel: x.width > 0 && x.right <= innerWidth && x.left >= 0 }; });
  confere(ed.tela[0] >= 0 && ed.tela[1] <= 390 && ed.tela[2] > 300, "Editor: a prévia aparece inteira", ed);
  confere(ed.exportarVisivel, "Editor: o botão Exportar cabe na barra");

  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector(".trilho");
  const trilho = await pagina.$eval(".trilho", (e) => ({ rola: e.scrollWidth > e.clientWidth, h: Math.round(e.getBoundingClientRect().height) }));
  confere(trilho.rola && trilho.h < 130, "Revisão: as etapas viram uma faixa que rola de lado", trilho);
  await pagina.tap(".etapa-botao:nth-child(5)");
  await dormir(900);
  const titulo = await pagina.$eval(".centro-cabeca", (e) => e.innerText);
  confere(titulo.length > 3, "Revisão: tocar numa etapa abre o material", titulo.slice(0, 40));
  const botoes = await pagina.$$eval(".lado button", (b) => b.map((x) => { const r = x.getBoundingClientRect(); return { t: x.innerText.slice(0, 20), ok: r.left >= 0 && r.right <= innerWidth, h: Math.round(r.height) }; }).filter((x) => x.t));
  confere(botoes.length > 0 && botoes.every((b) => b.ok), "Revisão: os botões de decisão cabem na tela", botoes);
  confere(botoes.every((b) => b.h >= 36), "Revisão: os botões têm tamanho de dedo", botoes);
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#l-decisao button");  // o roteiro é uma etapa que espera a sua aprovação
  await dormir(500);
  const antes = await pagina.evaluate(() => document.getElementById("l-decisao").getBoundingClientRect().top);
  confere(antes > 844, "Revisão: sem o botão, a decisão ficaria fora da tela, depois do material", antes);
  await pagina.tap("#ir-decisao");
  await dormir(1200);
  const depois = await pagina.evaluate(() => { const t = document.getElementById("l-decisao").getBoundingClientRect(); const bs = [...document.querySelectorAll("#l-decisao button")].map((x) => x.getBoundingClientRect()); return { topo: Math.round(t.top), botoesNaTela: bs.length > 0 && bs.every((r) => r.top >= 0 && r.bottom <= innerHeight) }; });
  confere(depois.topo >= 0 && depois.topo < 700 && depois.botoesNaTela, "Revisão: o botão Decisão traz a aprovação, com os botões inteiros, para a tela", depois);
  await captura("05-revisao-decisao");
  await pagina.setViewport({ width: 1500, height: 1000 });
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector(".trilho");
  confere(await pagina.$eval("#ir-decisao", (e) => getComputedStyle(e).display === "none"), "No computador o botão Decisão não aparece");
  await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });

  // O computador não mudou: a mesma página em tela larga
  await pagina.setViewport({ width: 1500, height: 1000 });
  await pagina.goto(`${BASE}/estudio/${SLUG}`, { waitUntil: "networkidle2" });
  await pagina.waitForSelector("#e-agentes .agente-linha");
  const larga = await pagina.evaluate(() => ({ colunas: getComputedStyle(document.querySelector(".estudio")).gridTemplateColumns.split(" ").length, rotulo: document.querySelector("#nav-local").innerText }));
  confere(larga.colunas === 3 && larga.rotulo.includes("Rede de casa"), "Em tela larga o Estúdio continua em três colunas", larga);
  confere(errosJs.length === 0, "Nenhum erro de JavaScript", errosJs);
  await navegador.close();
  navegador = null;
}

async function bloqueio() {
  console.log("\n[4] Tentativas demais bloqueiam o aparelho");
  await parar();
  subir("--rede");
  await esperar(LOCAL);
  let ultimo;
  for (let i = 0; i < 5; i++) ultimo = await entrar("chute-" + i);
  confere(ultimo.headers.location === "/?acesso=bloqueado", "Na quinta tentativa errada, bloqueia", ultimo.headers.location);
  const certa = await entrar(SENHA);
  confere(certa.headers.location === "/?acesso=bloqueado" && !certa.headers["set-cookie"], "Bloqueado, nem a senha certa entra", certa.headers);
  confere((await bruto(`${BASE}/?acesso=bloqueado`)).corpo.includes("5 minutos"), "A tela diz quanto esperar");
  confere((await bruto(`${LOCAL}/api/producoes`)).status === 200, "O computador não é afetado pelo bloqueio");
}

try {
  await sem_rede();
  await senha_e_recusas();
  await celular();
  await bloqueio();
} catch (e) {
  falhas.push(`exceção: ${e.message}`);
  console.log(`  FALHOU  ${e.stack}`);
  if (pagina) await captura("erro").catch(() => {});
} finally {
  if (navegador) await navegador.close().catch(() => {});
  await parar();
  try { fs.rmSync(caixa, { recursive: true, force: true, maxRetries: 8, retryDelay: 400 }); } catch { /* o Windows segura a pasta por um instante: é uma cópia descartável */ }
}
console.log(`\n${passou} verificações ok, ${falhas.length} falhas. Capturas em ${CAPTURAS}`);
if (falhas.length) { console.log(falhas.map((f) => ` - ${f}`).join("\n")); process.exit(1); }
