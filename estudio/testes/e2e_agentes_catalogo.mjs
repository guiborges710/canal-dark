// PROG-016: aba Agentes > Catálogo com selo de estado por agente. Chrome real, servidor numa cópia descartável com o claude simulado.
// O servidor é de verdade (lista de agentes e estado vazio); os demais casos usam respostas roteirizadas de /api/agentes/ao-vivo
// (mesmo contrato do back) para controlar estados, falhas e relógio. Agentes vêm do catálogo real, nunca de ids fixos (D-004).
// Uso: E2E_PORTA=8803 node estudio/testes/e2e_agentes_catalogo.mjs [pasta de capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8803, BASE = `http://127.0.0.1:${PORTA}`, SLUG = "fim-dos-terceiros-lugares";
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "catalogo-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "catalogo-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });

let servidor, navegador, pagina, passou = 0, pedidos = 0, modo = { tipo: "real" };
const falhas = [], errosJs = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 500)}` : ""}`); } }
async function esperarServidor() { for (let i = 0; i < 120; i++) { try { if ((await fetch(`${BASE}/api/fluxos`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }
const txt = (sel) => pagina.evaluate((s) => document.querySelector(s)?.innerText ?? null, sel);
const existe = (sel) => pagina.evaluate((s) => !!document.querySelector(s), sel);
const contar = (sel) => pagina.evaluate((s) => document.querySelectorAll(s).length, sel);
const espera = (fn, arg, ms = 6000) => pagina.waitForFunction(fn, { timeout: ms }, arg).then(() => true, () => false);
const agora = () => pagina.evaluate(() => Vivo.buscar());
const item = (id) => `.ag-item[data-agente="${id}"]`;
const selo = (id) => txt(`${item(id)} [data-selo]`);
const detalhe = (id) => pagina.evaluate((s) => { const e = document.querySelector(s); return e && !e.hidden ? e.innerText : ""; }, `${item(id)} [data-detalhe]`);

let A, B, C, D, E, TODOS;  // falhou, espera você, trabalhando (desativado), fila, vários vídeos

const TEXTO = { trabalhando: "Trabalhando", fila: "Na fila", falhou: "Falhou", espera_voce: "Espera você" };
const trab = (o = {}) => ({ job_id: 1, slug: SLUG, titulo_video: "Fim dos terceiros lugares", etapa_id: "cenas", etapa_nome: "Cenas", estado: "trabalhando", motor: "claude", motor_nota: null, segundos_na_tarefa: 128, aguarda_s: null, posicao_fila: null, erro_curto: null, origem: "grafo", alerta_longo: false, ...o });
const ag = (id, estado, trabalhos, extra = {}) => ({ id, craque: id, ativo: true, estado, estado_texto: TEXTO[estado], trabalhos, ...extra });
function resp(agentes, extra = {}) {
  const resumo = { trabalhando: 0, fila: 0, falhou: 0, espera_voce: 0, ignorados: 0 };
  agentes.forEach((a) => { resumo[a.estado]++; });
  return { gerado_em: "1999-01-01T00:00:00", servidor_s: 1, resumo, agentes, concluidos_1h: [], frescor: "ok", ...extra };
}
const MISTO = () => resp([
  ag(A, "falhou", [trab({ job_id: 5, estado: "falhou", segundos_na_tarefa: null, erro_curto: "Tempo esgotado" })]),
  ag(B, "espera_voce", [trab({ job_id: null, etapa_id: "roteiro", etapa_nome: "Roteiro", estado: "espera_voce", segundos_na_tarefa: null, aguarda_s: 300 })]),
  ag(C, "trabalhando", [trab({ job_id: 7, etapa_id: "metadados", etapa_nome: "Metadados", segundos_na_tarefa: 130 })], ),
  ag(D, "fila", [trab({ job_id: 8, etapa_id: "auditoria_texto", etapa_nome: "Auditoria de texto", estado: "fila", segundos_na_tarefa: null, aguarda_s: 40, posicao_fila: 2 })]),
  ag(E, "trabalhando", [trab({ job_id: 9, slug: "um", titulo_video: "Vídeo um" }), trab({ job_id: 10, slug: "dois", titulo_video: "Vídeo dois" }), trab({ job_id: 11, slug: "tres", titulo_video: "Vídeo três" })]),
]);
async function usar(corpo) { modo = corpo ? { tipo: "json", corpo } : { tipo: "real" }; await agora(); await dormir(150); }
async function abrirCatalogo() {
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  await espera(() => document.querySelector("#ag-lista .ag-item"), null, 8000);
}

async function ociosos() {
  console.log("\n[1] Servidor de verdade, sem trabalho: todos ociosos");
  await abrirCatalogo();
  const n = await contar("#ag-lista .ag-item");
  confere(n === TODOS.length && n >= 5, "O Catálogo lista todos os agentes do servidor", { n, esperado: TODOS.length });
  confere(await espera(() => [...document.querySelectorAll(".ag-item [data-selo]")].every((s) => /Ocioso/.test(s.innerText)), null), "Cada agente mostra '○ Ocioso' (ícone e texto)");
  confere(await pagina.evaluate(() => [...document.querySelectorAll(".ag-item [data-selo] .ic")].every((i) => i.getAttribute("aria-hidden") === "true")), "O ícone do selo é aria-hidden; o texto fica visível");
  confere((await contar(".ag-item [data-detalhe]:not([hidden])")) === 0, "Ocioso: nenhuma linha de vídeo, etapa ou tempo");
  confere(await pagina.evaluate(() => !/Falhou|há \d|undefined|\bnull\b|NaN/.test(document.getElementById("ag-lista").innerText)), "Sem histórico: nenhum 'Falhou', nenhum tempo, nenhum 'undefined'");
  confere((await txt("#ag-estado-rodape")) === "Ninguém trabalhando agora. Para acompanhar quem estiver em ação, use a aba Ao vivo.", "Todos ociosos: rodapé explica e aponta a aba Ao vivo", await txt("#ag-estado-rodape"));
  confere((await pagina.evaluate((s) => document.querySelector(s).getAttribute("aria-label"), item(A))).endsWith(", Ocioso"), "aria-label do item termina em 'Ocioso'");
}

async function estados() {
  console.log("\n[2] Quatro estados (mais 'espera você') no Catálogo");
  await usar(MISTO());
  confere(await espera((s) => /Falhou/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`), "Falhou: '✕ Falhou'", await selo(A));
  confere((await detalhe(A)) === "Fim dos terceiros lugares · falhou em Cenas", "Falhou: vídeo e etapa onde falhou", await detalhe(A));
  confere((await selo(B)) === "❚❚Espera você" || /Espera você/.test(await selo(B)), "Espera você: selo", await selo(B));
  confere((await detalhe(B)) === "Fim dos terceiros lugares · Roteiro", "Espera você: vídeo e etapa, sem tempo", await detalhe(B));
  confere(/Trabalhando/.test(await selo(C)) && /Desativado/.test(await txt(`${item(C)} .ag-item-topo`)), "Trabalhando + Desativado aparecem juntos", await txt(`${item(C)} .ag-item-topo`));
  confere(/^Fim dos terceiros lugares · Metadados · há (2 min|130 s|2\d? s|\d+ min)/.test(await detalhe(C)), "Trabalhando: vídeo, etapa e 'há N min'", await detalhe(C));
  confere(/Na fila/.test(await selo(D)) && (await detalhe(D)) === "Fim dos terceiros lugares · Auditoria de texto", "Na fila: vídeo e etapa, sem tempo", await detalhe(D));
  confere((await detalhe(E)).endsWith(" · +2"), "Vários vídeos: mostra o primeiro e ' · +2'", await detalhe(E));
  const ociosoOutro = TODOS.find((i) => ![A, B, C, D, E].includes(i));
  confere(/Ocioso/.test(await selo(ociosoOutro)) && (await detalhe(ociosoOutro)) === "", "Quem não está no Ao vivo continua ocioso e sem detalhe", await selo(ociosoOutro));
  confere((await pagina.evaluate((s) => document.querySelector(s).getAttribute("aria-label"), item(C))).includes("Trabalhando, vídeo Fim dos terceiros lugares, etapa Metadados"), "aria-label lê estado, vídeo e etapa");
  confere((await txt("#ag-estado-rodape")) === "", "Com gente trabalhando, o rodapé de 'ninguém' some", await txt("#ag-estado-rodape"));
  confere(await pagina.evaluate(() => !/undefined|\bnull\b|NaN/.test(document.getElementById("ag-lista").innerText)), "Nenhum 'undefined', 'null' ou 'NaN'");
  await pagina.screenshot({ path: path.join(CAPTURAS, "catalogo-estados.png") });

  console.log("  -- mesmo estado que a aba Ao vivo");
  const noCatalogo = await pagina.evaluate((ids) => Object.fromEntries(ids.map((i) => [i, document.querySelector(`.ag-item[data-agente="${i}"] [data-selo]`).innerText.replace(/^\S+\s*/, "").trim()])), [A, B, C, D, E]);
  await pagina.click("#aba-ao-vivo");
  await espera(() => document.querySelectorAll(".ag-cartao").length === 5, null);
  const noVivo = await pagina.evaluate((ids) => Object.fromEntries(ids.map((i) => [i, document.querySelector(`[data-agente-vivo="${i}"] .estado`).innerText.replace(/^\S+\s*/, "").trim()])), [A, B, C, D, E]);
  confere(JSON.stringify(noCatalogo) === JSON.stringify(noVivo), "Catálogo e Ao vivo mostram o mesmo estado para cada agente", { noCatalogo, noVivo });
  await pagina.click("#aba-catalogo");
  await espera(() => document.querySelector("#ag-lista .ag-item"), null);
}

async function atualizacao() {
  console.log("\n[3] Atualiza sozinho, sem recarregar");
  await abrirCatalogo();
  await usar(resp([]));
  confere(/Ocioso/.test(await selo(A)), "Começa ocioso");
  await pagina.evaluate(() => { window.__marca = "mesma-pagina"; document.querySelector(".ag-item").dataset.marca = "x"; });
  modo = { tipo: "json", corpo: resp([ag(A, "trabalhando", [trab({ segundos_na_tarefa: 5 })])]) };
  confere(await espera((s) => /Trabalhando/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`, 7000), "Mudança aparece em até um ciclo de polling (4 s)", await selo(A));
  confere(await pagina.evaluate(() => window.__marca === "mesma-pagina" && document.querySelector(".ag-item").dataset.marca === "x"), "Sem recarregar a página e sem refazer a lista");
  const reqs = pedidos;
  await dormir(4500);
  confere(pedidos - reqs <= 2, "Só o polling de 4 s do Corte (nenhuma consulta nova inventada pelo Catálogo)", pedidos - reqs);
  modo = { tipo: "json", corpo: resp([ag(A, "falhou", [trab({ estado: "falhou", segundos_na_tarefa: null })])]) };
  confere(await espera((s) => /Falhou/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`, 7000), "Trabalhando vira Falhou sozinho");
  modo = { tipo: "json", corpo: resp([]) };
  confere(await espera((s) => /Ocioso/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`, 7000) && (await detalhe(A)) === "", "E volta a Ocioso, sem sobra de vídeo ou etapa");
}

async function sobrevive() {
  console.log("\n[4] Busca digitada e edição aberta sobrevivem ao ciclo");
  await abrirCatalogo();
  await usar(resp([ag(A, "trabalhando", [trab()])]));
  await pagina.type("#busca-agente", A.slice(0, 5));
  const antes = await contar("#ag-lista .ag-item");
  await pagina.click(item(A));
  await espera(() => document.getElementById("ag-titulo"), null);
  await pagina.click("#ag-editar");
  await espera(() => document.getElementById("ag-instrucoes"), null);
  await pagina.type("#ag-descricao", " RASCUNHO-NAO-SALVO");
  modo = { tipo: "json", corpo: resp([ag(A, "fila", [trab({ estado: "fila", segundos_na_tarefa: null, aguarda_s: 3 })])]) };
  confere(await espera((s) => /Na fila/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`, 7000), "O selo mudou durante a edição");
  confere((await pagina.evaluate(() => document.getElementById("busca-agente").value)) === A.slice(0, 5) && (await contar("#ag-lista .ag-item")) === antes, "A busca digitada continua, com a mesma lista filtrada");
  confere((await pagina.evaluate(() => document.getElementById("ag-descricao").value)).includes("RASCUNHO-NAO-SALVO"), "A edição em curso não foi apagada");
  confere(await existe(`${item(A)}.ativo`), "O item selecionado continua selecionado");

  console.log("  -- busca sem resultado");
  await pagina.evaluate(() => { const i = document.getElementById("busca-agente"); i.value = "zzzz-nada"; i.dispatchEvent(new Event("input")); });
  confere((await txt("#ag-lista-vazia")) === "Nenhum agente encontrado. Limpe a busca para ver todos.", "Busca sem resultado: mensagem em português", await txt("#ag-lista-vazia"));
}

async function carregandoEErro() {
  console.log("\n[5] Antes da primeira resposta e com erro na consulta");
  modo = { tipo: "pendente" };
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "domcontentloaded" });
  await espera(() => document.querySelector("#ag-lista .ag-item"), null, 8000);
  confere(await pagina.evaluate(() => [...document.querySelectorAll(".ag-item [data-selo]")].every((s) => /Verificando/.test(s.innerText) && !/Ocioso/.test(s.innerText))), "Antes da primeira resposta: '… Verificando', nunca 'Ocioso'");
  confere((await txt("#ag-estado-rodape")) === "", "E sem afirmar que ninguém trabalha", await txt("#ag-estado-rodape"));

  console.log("  -- erro com estado anterior");
  await usar(resp([ag(A, "trabalhando", [trab()])]));
  await abrirCatalogo();
  await espera((s) => /Trabalhando/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`);
  modo = { tipo: "500" };
  await agora();
  confere(await espera(() => /\(desatualizado\)/.test(document.getElementById("ag-estado-rodape")?.innerText || ""), null), "Rodapé '(desatualizado) Não consegui atualizar os estados...'", await txt("#ag-estado-rodape"));
  confere(/Trabalhando/.test(await selo(A)), "Mantém os últimos selos");
  modo = { tipo: "json", corpo: resp([]) };
  await agora();
  confere(await espera(() => !/desatualizado/.test(document.getElementById("ag-estado-rodape")?.innerText || ""), null), "Quando volta, o aviso some");

  console.log("  -- lista de agentes não carrega");
  modo = { tipo: "lista500" };
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.querySelector("#ag-erro-lista"), null), "Erro na lista: mensagem clara e botão 'Tentar de novo'", await txt("#ag-lista"));
  confere((await txt("#ag-erro-lista")).includes("Não consegui carregar os agentes."), "Texto do erro em português");
  modo = { tipo: "real" };
  await pagina.click("#ag-tentar-lista");
  confere(await espera(() => document.querySelector("#ag-lista .ag-item"), null), "'Tentar de novo' recarrega a lista");
}

async function regressao() {
  console.log("\n[6] Edição e rotas seguem funcionando");
  await usar(resp([ag(A, "trabalhando", [trab()])]));
  await pagina.goto(`${BASE}/agentes/${A}`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.getElementById("ag-titulo") && document.getElementById("ag-editar") && document.getElementById("ag-duplicar"), null), "/agentes/<id> abre a ficha com Editar e Duplicar");
  confere(await existe(`${item(A)}.ativo`) && /Trabalhando/.test(await selo(A)), "O item aberto mostra o selo de estado");
  await pagina.click("#ag-editar");
  confere(await espera(() => document.getElementById("ag-salvar"), null), "Editar abre o formulário");
}

async function celular() {
  console.log("\n[7] Celular (390 px)");
  await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await usar(MISTO());
  await abrirCatalogo();
  await espera((s) => /Falhou/.test(document.querySelector(s)?.innerText || ""), `${item(A)} [data-selo]`);
  const m = await pagina.evaluate(() => {
    const itens = [...document.querySelectorAll("#ag-lista .ag-item")].map((e) => e.getBoundingClientRect());
    return { rolagem: document.documentElement.scrollWidth > innerWidth || document.getElementById("app").scrollWidth > innerWidth + 1, dentro: itens.every((r) => r.left >= 0 && r.right <= innerWidth + 1), colunas: new Set(itens.map((r) => Math.round(r.left))).size, menor: Math.min(...itens.map((r) => r.height)), selosVisiveis: [...document.querySelectorAll(".ag-item [data-selo]")].every((s) => s.innerText.trim().length > 2 && s.getBoundingClientRect().right <= innerWidth + 1) };
  });
  confere(!m.rolagem && m.dentro, "Sem rolagem lateral e itens dentro da largura", m);
  confere(m.colunas === 1, "Uma coluna só", m);
  confere(m.menor >= 44, "Alvo de toque do item com pelo menos 44 px", m);
  confere(m.selosVisiveis, "O texto do selo aparece em todos os itens (não só o ícone)", m);
  await pagina.screenshot({ path: path.join(CAPTURAS, "catalogo-celular.png") });
  await pagina.setViewport({ width: 1500, height: 1000 });
}

try {
  servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" });
  await esperarServidor();
  const r = await (await fetch(`${BASE}/api/agentes`)).json();
  TODOS = r.agentes.map((a) => a.id);
  [A, B, C, D, E] = TODOS.slice(0, 5);
  // O selo "Desativado" vem do catálogo, não do Ao vivo: desativa C de verdade (na cópia descartável).
  const des = await fetch(`${BASE}/api/agentes/${C}/ativar`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ativo: false }) });
  if (!des.ok) throw new Error(`não consegui desativar ${C}: ${des.status}`);
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox"] });
  pagina = await navegador.newPage();
  await pagina.setViewport({ width: 1500, height: 1000 });
  pagina.on("pageerror", (e) => errosJs.push(String(e)));
  await pagina.setRequestInterception(true);
  pagina.on("request", (req) => {
    if (/\/api\/agentes\/ao-vivo$/.test(req.url())) {
      pedidos++;
      if (modo.tipo === "json") return req.respond({ status: 200, contentType: "application/json", body: JSON.stringify(modo.corpo) });
      if (modo.tipo === "500") return req.respond({ status: 500, contentType: "application/json", body: JSON.stringify({ erro: ["Não foi possível ler o estado agora."] }) });
      if (modo.tipo === "pendente") return;  // nunca responde: simula a espera da primeira resposta
    }
    if (modo.tipo === "lista500" && /\/api\/agentes$/.test(req.url())) return req.respond({ status: 500, contentType: "application/json", body: JSON.stringify({ erro: ["falhou"] }) });
    req.continue();
  });
  await ociosos();
  await estados();
  await atualizacao();
  await sobrevive();
  await carregandoEErro();
  await regressao();
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
console.log(`\n${passou} verificações ok, ${falhas.length} falha(s). Capturas: ${CAPTURAS}`);
process.exit(falhas.length ? 1 : 0);
