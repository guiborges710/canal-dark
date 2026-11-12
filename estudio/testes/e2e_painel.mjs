// Teste de ponta a ponta do Painel (Ecossistema do Guilherme): Chrome real, numa caixa descartável (nunca lê o repositório real).
// Uso: node estudio/testes/e2e_painel.mjs [pasta para capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8797, BASE = `http://127.0.0.1:${PORTA}`;
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "painel-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });
const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "painel-caixa-"));

const w = (rel, txt, mtime) => { const p = path.join(caixa, rel); fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, txt, "utf-8"); if (mtime) fs.utimesSync(p, mtime, mtime); return p; };
const agora = Math.floor(Date.now() / 1000);
w("programacao/antigo.md", "# Documento antigo\ncorpo antigo", agora - 86400 * 3);
w("programacao/meio.md", "# Documento do meio\ncorpo do meio", agora - 3600 * 5);
w("prompts/novo.md", "# Documento novo\ncorpo novo", agora - 60);
w("programacao/xss.md", "# Perigoso\n<img src=x onerror=\"window.__xss=1\"><script>window.__xss=2</script>\n<b>negrito</b>", agora - 120);
w("programacao/vazou.md", "# Com credencial\nsk-ant-abcdefghijklmnopqrstuv segredo", agora - 130);
w("produtividade/tarefas.md", "# Tarefas do Guilherme\n- pagar conta", agora - 2000);
w("produtividade/acessos.md", "# Acessos\nlista de contas", agora - 2001);
w("produtividade/.ronaldo_contexto.md", "# Contexto do Ronaldo\nconversa", agora - 2002);
w("produtividade/.ronaldo_historico.json", "{\"historico\": \"SEGREDO_HISTORICO\"}", agora - 5);
w("produtividade/.google_agenda_estado.json", "{\"x\": \"SEGREDO_GOOGLE\"}", agora - 5);
w("produtividade/.env", "SEGREDO_ENV=1", agora - 5);
w("financas/pendencias.md", "# Pendencias financeiras\n1", agora - 2003);
w("financas/saldos.csv", "conta,saldo\nx,1", agora - 2004);
const CORPO_ZICO = "\n# Zico\n\nVocê é o **Zico**, PO do setor de programação. Escreve o backlog.\n\n## Regras\n- Primeira regra com `codigo`.\n- Segunda regra.\n  - Sub-regra aninhada.\n\n## Tabela de decisão\n| Situação | Ação |\n|---|---|\n| Item sem critério | Recusar |\n| Item pronto | Aceitar |\n\n## Exemplo\n```json\n{\"a\": 1,\n\n \"b\": 2}\n```\n\n1. Primeiro passo\n2. Segundo passo\n\n> Citação importante.\n";
const FRONT_ZICO = "---\nname: zico-po-programacao\ndescription: PO do setor de programação: escreve o backlog e confere o aceite.\ntools: Read, Write\nmodel: sonnet\nentradas: briefing\n---\n";
w(".claude/agents/zico-po-programacao.md", (FRONT_ZICO + CORPO_ZICO).replace(/\n/g, "\r\n"), agora - 500);   // CRLF, como a maioria dos agentes reais
w(".claude/agents/solto-sem-setor.md", "# Solto\nSem setor.", agora - 400);
w("ecossistema/setores.json", JSON.stringify({ nomes_compostos: [], setores: [
  { id: "programacao", nome: "Programação", ativo: true, agentes: ["zico-po-programacao"] },
  { id: "acao", nome: "Ação", ativo: false, agentes: [] },
  { id: "pessoal", nome: "Produtividade pessoal", ativo: false, agentes: ["ronaldo-pessoal-teste"] }] }), agora - 700);
w(".claude/agents/ronaldo-pessoal-teste.md", "# Ronaldo pessoal\nPrompt do assistente pessoal.", agora - 450);
w("programacao/estado.json", JSON.stringify({ cartoes: { "PROG-1": { ultima: "2026-11-04T17:25:25", pedido: "", espera_humano: false } } }), agora - 86400 * 2);
w("programacao/titulo-repetido.md", "# Título repetido\n## Parte um\ncorpo", agora - 86400 * 2);

let servidor, pagina, navegador, passou = 0;
const falhas = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function subir() { servidor = spawn(PY, [path.join(AQUI, "subir_painel_caixa.py"), caixa, String(PORTA)], { cwd: REPO, stdio: "ignore" }); }
async function derrubar() { const fim = new Promise((r) => servidor.once("exit", r)); servidor.kill(); await fim; }
async function esperarServidor() { for (let i = 0; i < 80; i++) { try { if ((await fetch(`${BASE}/api/painel/resumo`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }
function confere(cond, nome, extra) {
  if (cond) { passou++; console.log(`  ok  ${nome}`); }
  else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 400)}` : ""}`); }
}
const captura = (n) => pagina.screenshot({ path: path.join(CAPTURAS, `${n}.png`) });
const texto = (sel) => pagina.evaluate((s) => document.querySelector(s)?.innerText ?? null, sel);
const existe = (sel) => pagina.evaluate((s) => !!document.querySelector(s), sel);
async function esperar(fn, ms = 15000, ...args) { try { await pagina.waitForFunction(fn, { timeout: ms, polling: 200 }, ...args); return true; } catch { return false; } }
const abrir = async (url) => { await pagina.goto(`${BASE}${url}`, { waitUntil: "domcontentloaded" }); };
const titulos = () => pagina.evaluate(() => [...document.querySelectorAll(".pn-item .pn-item-tit")].map((e) => e.textContent));

async function rotasEMarca() {
  console.log("\n[1] Rotas, marca e menu");
  for (const r of ["/painel", "/painel/resumo", "/painel/documentos", "/painel/agentes", "/painel/setores"]) {
    const res = await fetch(`${BASE}${r}`);
    confere(res.status === 200 && (await res.text()).includes("corte_painel.js"), `GET ${r} serve o painel.html`, res.status);
  }
  await abrir("/painel");
  await esperar(() => document.querySelector(".pn-cartao"));
  confere((await texto(".nav-marca")).includes("Ecossistema do Guilherme") && !/Corte/.test(await texto(".nav-marca")), "A marca no menu é 'Ecossistema do Guilherme'", await texto(".nav-marca"));
  confere((await pagina.title()).includes("Ecossistema do Guilherme"), "O título da aba cita Ecossistema do Guilherme", await pagina.title());
  confere(await existe("#pn-aba-dashboard[aria-current=page]"), "O item Dashboard do menu lateral está marcado como atual");
  confere((await pagina.evaluate(() => [...document.querySelectorAll(".pn-aba")].map((a) => a.textContent))).join() === "Dashboard,Resumo,Documentos,Agentes,Setores,Vídeos", "Abas na ordem pedida");
  await abrir("/");
  await esperar(() => document.querySelector("#nav-painel"));
  confere((await texto(".nav-marca")).includes("Ecossistema do Guilherme") && await existe("#nav-painel"), "Nas telas do Corte o menu também tem a marca nova e o item Painel");
  await pagina.click("#nav-painel");
  await esperar(() => location.pathname === "/painel" && document.querySelector(".pn-cartao"));
  confere(await existe(".pn-cartao"), "Clicar em 'Painel' no menu abre o painel");
}

async function dashboardEResumo() {
  console.log("\n[2] Dashboard e Resumo");
  await abrir("/painel");
  await esperar(() => document.querySelectorAll(".pn-cartao").length === 5);
  const n = await pagina.evaluate(() => document.querySelectorAll(".pn-cartao").length);
  confere(n === 5, "Dashboard tem 5 cartões", n);
  confere(await existe("#pn-c-docs") && /^[1-9]/.test(await texto("#pn-c-docs .pn-c-num")), "Cartão de documentos alterados hoje conta documentos", await texto("#pn-c-docs"));
  confere(await existe("#pn-resumo-mini"), "Dashboard traz o bloco 'Resumo agora'");
  confere(/Atualizado às \d\d:\d\d/.test(await texto("#pn-lido")), "Mostra 'Atualizado às hh:mm'", await texto("#pn-lido"));
  await captura("dashboard");
  await pagina.setViewport({ width: 1024, height: 900 });
  await abrir("/painel");
  await esperar(() => document.querySelector("#pn-c-sprint .pn-c-num"));
  const sprintNumero = await pagina.$eval("#pn-c-sprint .pn-c-num", (e) => ({ altura: e.getBoundingClientRect().height, linha: parseFloat(getComputedStyle(e).lineHeight) }));
  confere(sprintNumero.altura <= sprintNumero.linha * 1.2, "Em 1024 px, 'Sprint 01' fica em uma linha", sprintNumero);
  await pagina.setViewport({ width: 1440, height: 900 });
  await abrir("/painel");
  await esperar(() => document.querySelectorAll(".pn-cartao").length === 5);
  await pagina.click("#pn-aba-resumo");
  await esperar(() => document.querySelector("#pn-resumo"));
  const linhas = await pagina.evaluate(() => [...document.querySelectorAll("#pn-resumo .pn-linha")].map((e) => e.textContent));
  confere(linhas.length >= 1 && linhas.length <= 2 && linhas.every((l) => l.length <= 120), "Resumo tem no máximo 2 linhas de até 120 caracteres", linhas);
  confere(!/SEGREDO/.test(linhas.join(" ")), "Resumo não cita segredos", linhas);
  confere((await pagina.evaluate(() => location.pathname)) === "/painel/resumo", "A aba Resumo tem URL própria");
  await captura("resumo");
  await pagina.goBack();
  await esperar(() => location.pathname === "/painel" && document.querySelector(".pn-cartoes"));
  confere(await existe(".pn-cartoes"), "Voltar do navegador volta ao Dashboard");
  await pagina.focus("#pn-aba-dashboard");
  await pagina.keyboard.press("ArrowRight");
  await esperar(() => location.pathname === "/painel/resumo");
  confere((await pagina.evaluate(() => location.pathname)) === "/painel/resumo", "Seta para a direita troca de aba");
}

async function documentos() {
  console.log("\n[3] Documentos");
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  const t = await titulos();
  confere(t[0] === "Documento novo" && t.indexOf("Documento do meio") < t.indexOf("Documento antigo"), "Lista ordenada por alteração, mais recente no topo", t);
  confere(t.some((x) => /Tarefas do Guilherme/.test(x)) && t.some((x) => /Pendencias financeiras/.test(x)) && t.some((x) => /Contexto do Ronaldo/.test(x)), "Documentos de produtividade e finanças aparecem", t);
  confere(!(await pagina.evaluate(() => document.body.innerText)).includes("SEGREDO") && !(await existe('[data-caminho*=".env"], [data-caminho*="historico"], [data-caminho*="google_agenda"]')), "Segredos, históricos e estados ocultos não aparecem", t);
  const dica = await pagina.evaluate(() => document.querySelector(".pn-item time")?.title);
  confere(/\d{2}\/\d{2}\/\d{4} às \d\d:\d\d:\d\d/.test(dica || ""), "Data completa ao passar o mouse", dica);
  const rel = await pagina.evaluate(() => [...document.querySelectorAll(".pn-item time")].map((e) => e.textContent));
  confere(rel.some((x) => /^há \d+ min$|^agora$/.test(x)) && rel.some((x) => /^\d\d\/\d\d \d\d:\d\d$/.test(x)), "Datas relativas e curtas na lista", rel);
  const corpoTexto = await texto("#pn-corpo");
  confere(!/visto|Novo\b|Alterado|Desfazer/.test(corpoTexto), "Sem 'visto', 'Desfazer' nem etiquetas Novo/Alterado", corpoTexto.slice(0, 200));
  await captura("documentos");
  await pagina.evaluate(() => { window.__xss = 0; });
  confere(t.some((x) => /Ronaldo pessoal/.test(x)) && await existe('[data-caminho=".claude/agents/ronaldo-pessoal-teste.md"]'), "Prompt de agente pessoal aparece em Documentos", t);
  await pagina.click('.pn-item[data-caminho="programacao/titulo-repetido.md"]');
  await esperar(() => document.querySelector("#pn-texto"));
  const rep1 = await pagina.evaluate(() => ({ h2: [...document.querySelectorAll("#pn-texto .md-t")].map((e) => e.textContent), topo: document.querySelector(".pn-l-topo h2").textContent }));
  confere(rep1.topo === "Título repetido" && rep1.h2.join() === "Parte um", "O título do documento não se repete no corpo", rep1);
  await pagina.click('.pn-item[data-caminho="programacao/estado.json"]');
  await esperar(() => document.querySelector("#pn-texto"));
  const js = await texto("#pn-texto");
  confere(/Cartões:/.test(js) && /Última: 04\/11\/2026 às 17:25/.test(js) && /Pedido: —/.test(js) && /Espera humano: não/.test(js) && !/_|T17:25/.test(js), "JSON legível: rótulos em português, data formatada, vazio como traço", js.slice(0, 200));
  await pagina.click('.pn-item[data-caminho="programacao/xss.md"]');
  await esperar(() => document.querySelector("#pn-texto"));
  const dom = await pagina.evaluate(() => ({ img: !!document.querySelector("#pn-texto img, #pn-texto script, #pn-texto b, #pn-texto [onerror]"), txt: document.querySelector("#pn-texto").textContent, xss: window.__xss }));
  confere(!dom.img && dom.xss === 0 && dom.txt.includes("<script>"), "Texto do documento é escapado (nada executa)", dom);
  confere(/Somente leitura/.test(await texto(".pn-rodape")) && !(await existe("#pn-texto[contenteditable], textarea")), "Leitura é somente leitura");
  await pagina.click('.pn-item[data-caminho="programacao/vazou.md"]');
  await esperar(() => document.querySelector("#pn-omitido"));
  const om = await pagina.evaluate(() => document.body.innerText);
  confere(/Conteúdo omitido/.test(om) && !om.includes("sk-ant-"), "Documento com credencial mostra aviso e nenhum trecho", om.slice(0, 120));
  await abrir("/painel/documentos?caminho=produtividade%2F.ronaldo_historico.json");
  await esperar(() => document.querySelector("#pn-doc-sumiu"));
  confere(await existe("#pn-doc-sumiu") && !(await texto("#pn-corpo")).includes("SEGREDO_HISTORICO"), "Caminho proibido responde como 'apagado', sem revelar");
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  await pagina.type("#pn-busca", "meio.md");
  await esperar(() => document.querySelectorAll(".pn-item").length === 1);
  confere((await titulos()).join() === "Documento do meio", "Busca por texto filtra (com espera de digitação)", await titulos());
  await pagina.$eval("#pn-busca", (e) => { e.value = ""; e.dispatchEvent(new Event("input")); });
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  await pagina.select("#pn-area", "prompts");
  await esperar(() => document.querySelectorAll(".pn-item").length === 1);
  confere((await titulos()).join() === "Documento novo", "Filtro por área", [await titulos(), await pagina.evaluate(() => [document.getElementById("pn-area").value, document.getElementById("pn-status").textContent, T.area, T.busca, T.erro && T.erro.msg])]);
  await pagina.select("#pn-area", "");
  await pagina.type("#pn-busca", "zzzinexistentezzz");
  await esperar(() => document.querySelector("#pn-lista-vazia"));
  confere(/Nenhum documento combina com 'zzzinexistentezzz'/.test((await texto("#pn-lista-vazia")) || ""), "Estado vazio da busca explica e oferece 'Limpar busca'", await texto("#pn-lista-vazia"));
  await pagina.click("#pn-lista-vazia button");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  confere((await titulos()).length >= 5, "Limpar busca volta a lista");
}

async function polling() {
  console.log("\n[4] Atualização automática");
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  await pagina.click('.pn-item[data-caminho="programacao/meio.md"]');
  await esperar(() => document.querySelector("#pn-texto"));
  await pagina.evaluate(() => { window.__marca_pagina = "mesma"; window.__muts = 0; new MutationObserver((m) => { window.__muts += m.length; }).observe(document.getElementById("pn-lista"), { childList: true, subtree: true, characterData: true, attributes: true }); });
  await dormir(11000);
  const muts = await pagina.evaluate(() => window.__muts);
  confere(muts === 0, "Sem mudança no disco, a lista não pisca (0 mutações em 11 s)", muts);
  const t0 = Date.now();
  w("programacao/criado-agora.md", "# Criado durante o teste\ntexto");
  const subiu = await esperar(() => document.querySelector(".pn-item .pn-item-tit")?.textContent === "Criado durante o teste", 20000);
  confere(subiu, `Documento novo sobe ao topo sozinho (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
  confere(await pagina.evaluate(() => window.__marca_pagina === "mesma"), "Sem recarregar a página");
  await captura("polling");
  w("programacao/meio.md", "# Documento do meio\ncorpo MUDOU");
  const faixa = await esperar(() => document.querySelector("#pn-doc-mudou"), 20000);
  confere(faixa && /Este documento mudou\./.test(await texto("#pn-doc-mudou")), "Faixa 'Recarregar' quando o documento aberto muda", await texto("#pn-doc-faixa"));
  confere((await texto("#pn-texto")).includes("corpo do meio") && !(await texto("#pn-texto")).includes("MUDOU"), "O texto aberto não troca sozinho");
  await pagina.click("#pn-recarregar");
  await esperar(() => document.querySelector("#pn-texto")?.textContent.includes("MUDOU"));
  confere((await texto("#pn-texto")).includes("MUDOU") && !(await existe("#pn-doc-mudou")), "Recarregar mostra o texto novo e some a faixa");
}

async function agentesESetores() {
  console.log("\n[5] Agentes e Setores");
  await abrir("/painel/agentes");
  await esperar(() => document.querySelector("#pn-ag-tab"));
  const linhas = await pagina.evaluate(() => [...document.querySelectorAll("#pn-ag-tab [data-agente]")].map((r) => r.dataset.agente));
  confere(linhas.includes("zico-po-programacao") && linhas.includes("solto-sem-setor") && linhas.includes("ronaldo-pessoal-teste"), "Tabela lista os agentes", linhas);
  confere((await texto("#pn-ag-conta")) === "3 agentes · 0 ativos agora", "Contagem de agentes usa plural coerente", await texto("#pn-ag-conta"));
  confere(/sem setor/i.test((await texto("#pn-ag-aviso")) || ""), "Aviso de agente sem setor", await texto("#pn-ag-aviso"));
  confere(!(await existe("#pn-ag-editar")) && !(await existe('a[href="/agentes"]')) && !(await existe("#pn-ag-tab input, #pn-ag-tab textarea")), "O botão 'Editar agentes' que levava ao Corte saiu; a lista não tem campos de edição");
  confere(await existe('#pn-ag-tab a.pn-ag-link[href="/painel/agentes/zico-po-programacao"]'), "Cada agente da lista é um link para a página dele no painel");
  await pagina.type("#pn-ag-busca", "zico");
  await esperar(() => document.querySelectorAll("#pn-ag-tab [data-agente]").length === 1);
  confere((await pagina.evaluate(() => document.querySelectorAll("#pn-ag-tab [data-agente]").length)) === 1, "Busca de agente filtra");
  await pagina.$eval("#pn-ag-busca", (e) => { e.value = "nao-existe-xyz"; e.dispatchEvent(new Event("input")); });
  await esperar(() => document.querySelector("#pn-ag-vazio"));
  confere(await existe("#pn-ag-vazio"), "Estado vazio da busca de agentes");
  await captura("agentes");
  await abrir("/painel/setores");
  await esperar(() => document.querySelector(".pn-setor"));
  confere((await texto('#pn-sem-setor')).startsWith('1 agente sem setor:'), 'Aviso geral de um agente sem setor usa singular', await texto('#pn-sem-setor'));
  const set = await pagina.evaluate(() => [...document.querySelectorAll(".pn-setor")].map((s) => [s.dataset.setor, s.querySelector(".selo")?.textContent ?? null]));
  confere(JSON.stringify(set) === JSON.stringify([["programacao", "Ativo"], ["acao", "Inativo"], ["pessoal", "Inativo"]]), "Setores com Ativo/Inativo, inclusive o pessoal", set);
  const priv = await texto('.pn-setor[data-setor="pessoal"]');
  confere(/Produtividade pessoal/.test(priv) && /1 agente(?!s)/.test(priv) && /Ronaldo/.test(priv) && (await existe('.pn-setor[data-setor="pessoal"] a')), "Setor pessoal mostra nome real, agente e links como os demais", priv);
  confere(/Inativo: /.test((await texto('.pn-setor[data-setor="acao"]')) || ""), "Setor inativo diz por escrito que está inativo");
  confere(/Produtividade pessoal/.test(await texto("#pn-corpo")), "Setores mostram a produtividade pessoal");
  await captura("setores");
}

/* ---------- Página do agente e editor visual (sempre na caixa: nunca edita agente real) ---------- */
const ARQ_ZICO = path.join(caixa, ".claude", "agents", "zico-po-programacao.md");
const lerZico = () => fs.readFileSync(ARQ_ZICO, "utf-8");
const corpoDe = (t) => t.replace(/\r\n/g, "\n").replace(/^---\n[\s\S]*?\n---\n/, "");
let dialogos = [], decisaoDialogo = true;
const editorPronto = () => esperar(() => window.PainelAgente && window.PainelAgente.pronto() && document.querySelector(".toastui-editor-ww-container .ProseMirror"), 20000);
const salvarEEsperar = async (estado) => { await pagina.click("#pn-ag-salvar"); return esperar((e) => document.getElementById("pn-ag-status")?.dataset.estado === e, 15000, estado); };
async function digitarNoFim(seletor, textoNovo) {
  await pagina.click(seletor);
  await pagina.keyboard.press("End");
  await pagina.keyboard.type(textoNovo);
}

async function editorDoAgente() {
  console.log("\n[5b] Página do agente e editor visual");
  pagina.on("dialog", async (d) => { dialogos.push(d.message()); if (decisaoDialogo) await d.accept(); else await d.dismiss(); });
  const original = corpoDe(lerZico());
  const bytesAntes = fs.readFileSync(ARQ_ZICO);

  // abrir pela lista, com URL própria
  await abrir("/painel/agentes");
  await esperar(() => document.querySelector("#pn-ag-tab"));
  await pagina.click('a.pn-ag-link[href="/painel/agentes/zico-po-programacao"]');
  confere(await esperar(() => location.pathname === "/painel/agentes/zico-po-programacao" && document.querySelector("#pn-ag-nome")), "Clicar no agente abre /painel/agentes/<id> dentro do painel");
  confere(await editorPronto(), "O editor visual carrega (vendorizado, sem CDN)");
  confere((await texto("#pn-ag-nome")) === "Zico" && (await texto("#pn-ag-id")) === "zico-po-programacao", "Mostra o nome e o id do agente", await texto("#pn-ag-nome"));
  confere(/Setor: Programação/.test(await texto("#pn-ag-setor-chip")) && /Parado/.test(await texto("#pn-ag-estado")), "Mostra o setor e o estado", [await texto("#pn-ag-setor-chip"), await texto("#pn-ag-estado")]);
  confere(await existe("#pn-aba-agentes[aria-current=page]") && !(await existe("#pn-ag-editar")), "O menu mantém 'Agentes' marcado; sem botão que leva ao Corte");
  const nenhumaReqExterna = await pagina.evaluate(() => performance.getEntriesByType("resource").every((r) => r.name.startsWith(location.origin)));
  confere(nenhumaReqExterna, "Nenhum recurso vem de fora (sem CDN)");

  // visual: sem sintaxe markdown nem frontmatter como código
  const visual = await pagina.evaluate(() => {
    const c = document.querySelector(".toastui-editor-ww-container .toastui-editor-contents");
    return { h1: c.querySelector("h1")?.textContent, h2s: [...c.querySelectorAll("h2")].map((x) => x.textContent), li: c.querySelectorAll("ul li").length, ol: c.querySelectorAll("ol li").length, th: [...c.querySelectorAll("th")].map((x) => x.textContent), td: c.querySelectorAll("td").length, strong: c.querySelector("strong")?.textContent, pre: c.querySelector("pre")?.textContent, quote: !!c.querySelector("blockquote"), codeInline: c.querySelector("p code, li code")?.textContent, texto: c.innerText, pagina: document.getElementById("pn-corpo").innerText };
  });
  confere(visual.h1 === "Zico" && visual.h2s.length === 3 && visual.li >= 3 && visual.ol === 2 && visual.th.join() === "Situação,Ação" && visual.td === 4 && visual.strong === "Zico" && visual.quote && visual.codeInline === "codigo" && /"b": 2/.test(visual.pre || ""), "Títulos, listas, negrito, tabela, citação e blocos de código aparecem formatados", visual);
  confere(!/(^|\n)#{1,3} |\|---|```|\*\*Zico\*\*/.test(visual.texto), "O texto do editor não mostra sintaxe markdown", visual.texto.slice(0, 200));
  confere(!/(^|\n)(name|tools|model|description|entradas):/.test(visual.pagina) && !/---/.test(visual.pagina), "O frontmatter não aparece como código");
  const campos = await pagina.evaluate(() => ({ desc: document.getElementById("pn-ag-descricao").value, modelo: document.getElementById("pn-ag-modelo").value, ferr: [...document.querySelectorAll("#pn-ag-ferramentas input:checked")].map((i) => i.value), todas: [...document.querySelectorAll("#pn-ag-ferramentas input")].length }));
  confere(/^PO do setor de programação/.test(campos.desc) && campos.modelo === "sonnet" && campos.ferr.join() === "Read,Write" && campos.todas >= 9, "Descrição, modelo e ferramentas viram campos de formulário", campos);
  await captura("agente-editor");

  // ida e volta sem editar: o arquivo não muda
  confere((await texto("#pn-ag-status")) === "Sem alterações." && await pagina.$eval("#pn-ag-salvar", (b) => b.disabled), "Sem editar: 'Sem alterações' e o botão Salvar fica desligado");
  const semEdicao = await pagina.evaluate(() => window.PainelAgente.corpoParaSalvar().instrucoes);
  confere(semEdicao === original, "Ida e volta fiel: abrir e salvar sem editar devolve o texto original, byte a byte (tabela e bloco de código inclusos)", { tam: [semEdicao.length, original.length] });
  await dormir(600);
  confere(Buffer.compare(fs.readFileSync(ARQ_ZICO), bytesAntes) === 0, "O arquivo em disco não mudou");

  // editar um parágrafo: muda só ele
  await digitarNoFim('.toastui-editor-ww-container .ProseMirror p', " EDITADO PELO TESTE");
  confere(await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000), "Ao editar: 'Alterações não salvas'", await texto("#pn-ag-status"));
  confere(!(await pagina.$eval("#pn-ag-salvar", (b) => b.disabled)), "Ao editar: Salvar liga");
  const proposto = await pagina.evaluate(() => window.PainelAgente.corpoParaSalvar().instrucoes);
  const dif = proposto.split("\n").filter((l, i, a) => !original.split("\n").includes(l));
  confere(dif.length === 1 && /EDITADO PELO TESTE/.test(dif[0]) && proposto.split("\n").length === original.split("\n").length, "Editar um parágrafo muda só a linha dele (o resto do arquivo fica como estava)", dif);
  const cobertura = await pagina.evaluate(() => { const b = document.getElementById("pn-ag-salvar"); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2); return e && e.id; });
  confere(cobertura === "pn-ag-salvar", "O botão Salvar fica sempre à vista e clicável (o editor não o cobre)", cobertura);
  const respostasSalvar = [];
  pagina.on("response", async (r) => { if (r.url().includes("/salvar")) respostasSalvar.push([r.status(), (await r.text().catch(() => "")).slice(0, 200)]); });
  confere(await salvarEEsperar("salvo"), "Salvar: passa por 'Salvando...' e termina em 'Salvo'", [respostasSalvar, await texto("#pn-ag-status")]);
  confere(/^Salvo às \d\d:\d\d\.$/.test(await texto("#pn-ag-status")), "Mostra 'Salvo às hh:mm'", await texto("#pn-ag-status"));
  const aposSalvar = lerZico();
  const corpoSalvo = corpoDe(aposSalvar);
  const esperado = original.replace(/^\n+/, "").split("\n");
  const salvoLinhas = corpoSalvo.split("\n");
  const difSalvo = salvoLinhas.filter((l) => !esperado.includes(l));
  confere(difSalvo.length === 1 && /EDITADO PELO TESTE/.test(difSalvo[0]) && salvoLinhas.length === esperado.length, "No disco: só o parágrafo editado mudou; tabela, código e listas intactos", difSalvo);
  confere(/^---\r?\nname: zico-po-programacao\r?\ndescription: PO do setor.*\r?\ntools: Read, Write\r?\nmodel: sonnet\r?\nentradas: briefing\r?\n---/.test(aposSalvar), "No disco: o frontmatter segue com name, description, tools, model e o campo que a tela não expõe (entradas)");
  confere(await pagina.$eval("#pn-ag-salvar", (b) => b.disabled) && /Versão 2|Versão \d+/.test(await texto("#pn-ag-versao")), "Depois de salvar: Salvar desliga e a versão sobe", await texto("#pn-ag-versao"));

  // descrição e ferramentas
  await pagina.$eval("#pn-ag-descricao", (e) => { e.value = "PO que escreve o backlog, agora com nova descrição."; e.dispatchEvent(new Event("input", { bubbles: true })); });
  await pagina.click('#pn-ag-ferramentas input[value="Grep"]');
  confere(await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000), "Mexer na descrição ou nas ferramentas também marca 'Alterações não salvas'");
  confere(await salvarEEsperar("salvo"), "Salvar descrição e ferramentas");
  confere(/description: PO que escreve o backlog, agora com nova descrição\./.test(lerZico()) && /tools: Read, Write, Grep/.test(lerZico()), "No disco: descrição e ferramentas novas");

  // versões anteriores
  await pagina.click("#pn-ag-versoes > summary");
  const versoes = await pagina.evaluate(() => [...document.querySelectorAll("#pn-ag-versoes-lista li")].map((li) => li.dataset.versao));
  confere(versoes.length >= 3, "Versões anteriores lista as versões guardadas", versoes);
  const primeira = versoes[versoes.length - 1];
  await pagina.click(`#pn-ag-versoes-lista li[data-versao="${primeira}"] button`);
  await esperar(() => /sonnet|Primeira/.test(document.getElementById("pn-corpo").innerText) && !/EDITADO PELO TESTE/.test(document.querySelector(".toastui-editor-ww-container .toastui-editor-contents")?.innerText || "x"), 15000);
  confere(!/EDITADO PELO TESTE/.test(lerZico()) && /Tabela de decisão/.test(lerZico()) && dialogos.some((m) => /Restaurar a versão/.test(m)), "Restaurar a versão inicial devolve o texto de antes (histórico mantido)", dialogos.slice(-1));
  confere(await editorPronto(), "Depois de restaurar a página recarrega o editor");

  // conflito: o arquivo muda por fora com a página aberta
  await digitarNoFim('.toastui-editor-ww-container .ProseMirror p', " MINHA EDICAO");
  await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000);
  fs.writeFileSync(ARQ_ZICO, lerZico().replace("Segunda regra.", "Segunda regra MUDOU POR FORA."), "utf-8");
  await pagina.click("#pn-ag-salvar");
  confere(await esperar(() => document.querySelector("#pn-ag-conflito"), 15000), "Arquivo mudou por fora: aparece o conflito");
  const msgConflito = await texto("#pn-ag-conflito");
  confere(/O arquivo mudou desde que você abriu: recarregar ou sobrescrever\?/.test(msgConflito) && await existe("#pn-ag-recarregar") && await existe("#pn-ag-sobrescrever"), "Conflito pergunta 'recarregar ou sobrescrever?' com os dois botões", msgConflito);
  confere(!/MINHA EDICAO/.test(lerZico()) && /MUDOU POR FORA/.test(lerZico()), "Enquanto há conflito, nada é gravado por cima");
  await captura("agente-conflito");
  await pagina.click("#pn-ag-recarregar");
  await esperar(() => !document.querySelector("#pn-ag-conflito") && window.PainelAgente.pronto() && /MUDOU POR FORA/.test(document.querySelector(".toastui-editor-ww-container .toastui-editor-contents")?.innerText || ""), 15000);
  confere(/MUDOU POR FORA/.test(await texto(".toastui-editor-ww-container .toastui-editor-contents")) && !/MINHA EDICAO/.test(await texto(".toastui-editor-ww-container .toastui-editor-contents")), "Recarregar mostra o texto novo e descarta a minha edição");
  // de novo, agora sobrescrevendo
  await digitarNoFim('.toastui-editor-ww-container .ProseMirror p', " MINHA EDICAO");
  await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000);
  fs.writeFileSync(ARQ_ZICO, lerZico().replace("Primeira regra", "Primeira regra ALTERADA FORA"), "utf-8");
  await pagina.click("#pn-ag-salvar");
  await esperar(() => document.querySelector("#pn-ag-sobrescrever"), 15000);
  await pagina.click("#pn-ag-sobrescrever");
  confere(await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "salvo", 15000), "Sobrescrever grava a minha versão");
  confere(/MINHA EDICAO/.test(lerZico()) && !/ALTERADA FORA/.test(lerZico()), "No disco: a minha versão ficou por cima; a anterior está em Versões anteriores");

  // erro de rede ao salvar
  await digitarNoFim('.toastui-editor-ww-container .ProseMirror p', " X");
  await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000);
  await pagina.setRequestInterception(true);
  const barrar = (r) => (r.method() === "POST" && r.url().includes("/salvar") ? r.abort() : r.continue());
  pagina.on("request", barrar);
  await pagina.click("#pn-ag-salvar");
  confere(await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "erro", 15000), "Falha ao salvar: mostra o erro");
  confere(/Não salvou: Não consegui falar com o servidor/.test(await texto("#pn-ag-status")) && /Tentar salvar de novo/.test(await texto("#pn-ag-salvar")), "O erro diz o que houve, que o texto continua na tela, e oferece tentar de novo", await texto("#pn-ag-status"));
  pagina.off("request", barrar);
  await pagina.setRequestInterception(false);
  confere(await salvarEEsperar("salvo"), "Tentar de novo funciona quando o servidor volta");

  // aviso ao sair com alterações
  await digitarNoFim('.toastui-editor-ww-container .ProseMirror p', " Y");
  await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000);
  dialogos = []; decisaoDialogo = false;
  await pagina.click("#pn-aba-resumo");
  await dormir(400);
  confere(dialogos.some((m) => /alterações não salvas/.test(m)) && (await pagina.evaluate(() => location.pathname)) === "/painel/agentes/zico-po-programacao", "Sair com alterações: avisa e, se o Guilherme recusar, fica na página", dialogos);
  const antesDeSair = await pagina.evaluate(() => { const e = new Event("beforeunload", { cancelable: true }); window.dispatchEvent(e); return e.defaultPrevented; });
  confere(antesDeSair, "Fechar a aba com alterações dispara o aviso do navegador");
  await pagina.goBack();
  await dormir(400);
  confere((await pagina.evaluate(() => location.pathname)) === "/painel/agentes/zico-po-programacao", "Botão voltar do navegador também pede confirmação e fica na página");
  decisaoDialogo = true;
  await pagina.click("#pn-aba-resumo");
  confere(await esperar(() => location.pathname === "/painel/resumo", 10000), "Confirmando, sai da página");
  confere(!/ Y(\r?\n|$)/.test(corpoDe(lerZico())), "Alterações descartadas ao sair não foram gravadas");

  // tema claro
  await abrir("/painel/agentes/zico-po-programacao");
  await editorPronto();
  confere(await existe(".toastui-editor-defaultUI.toastui-editor-dark"), "No tema escuro o editor usa o tema escuro");
  await pagina.click("#pn-tema");
  await dormir(300);
  confere(!(await existe(".toastui-editor-defaultUI.toastui-editor-dark")), "Trocar para o tema claro muda o editor junto");
  await captura("agente-claro");
  await pagina.click("#pn-tema");

  // estados vazios e de erro
  await abrir("/painel/agentes/nao-existe-xyz");
  confere(await esperar(() => document.querySelector("#pn-ag-naoachou"), 15000) && /Agente não encontrado/.test(await texto("#pn-ag-naoachou")), "Agente que não existe: mensagem clara e link para a lista", await texto("#pn-corpo"));
  await abrir("/painel/agentes/ronaldo-pessoal-teste");
  await editorPronto();
  confere(/Setor: Produtividade pessoal/.test(await texto("#pn-ag-setor-chip")), "Vale para os agentes do setor pessoal também");
  await pagina.click("#pn-ag-versoes > summary");
  confere(/Ainda não há versões anteriores/.test((await texto("#pn-ag-versoes-vazio")) || ""), "Sem versões anteriores: estado vazio explica o porquê");
  confere(/(Versão 1)/.test(await texto("#pn-ag-versao")) && (await pagina.$eval("#pn-ag-descricao", (e) => e.value)) === "", "Agente sem frontmatter: campo de descrição vazio");
  await digitarNoFim(".toastui-editor-ww-container .ProseMirror p", " mais");
  await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "sujo", 5000);
  await pagina.click("#pn-ag-salvar");
  confere(await esperar(() => document.getElementById("pn-ag-status")?.dataset.estado === "erro", 5000) && /escreva uma descrição/.test(await texto("#pn-ag-status")), "Sem descrição: explica por que não salva e leva o foco ao campo", await texto("#pn-ag-status"));
  decisaoDialogo = true;

  // links vindos de Setores e de Documentos
  await abrir("/painel/setores");
  await esperar(() => document.querySelector('.pn-setor a.pn-nome-ag[data-agente="zico-po-programacao"]'));
  await pagina.click('.pn-setor a.pn-nome-ag[data-agente="zico-po-programacao"]');
  confere(await esperar(() => location.pathname === "/painel/agentes/zico-po-programacao" && document.querySelector("#pn-ag-nome"), 15000), "Em Setores, o nome do agente abre a página dele");
  decisaoDialogo = true;
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  const href = await pagina.evaluate(() => { const it = [...document.querySelectorAll(".pn-item")].find((x) => /Zico/.test(x.innerText)); if (it) it.click(); return !!it; });
  await esperar(() => document.querySelector("#pn-abrir-agentes"), 8000);
  confere(await pagina.evaluate(() => document.querySelector("#pn-abrir-agentes")?.getAttribute("href")) === "/painel/agentes/zico-po-programacao", "Em Documentos, o agente tem 'Abrir e editar este agente' apontando para a página dele", href);
  await abrir("/painel/agentes/zico-po-programacao");
  await editorPronto();
  await pagina.setViewport({ width: 390, height: 800 });
  await dormir(300);
  confere(await pagina.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "Janela estreita: a página do agente não rola para o lado");
  await captura("agente-estreito");
  await pagina.setViewport({ width: 1440, height: 900 });
}

async function celularEVazio() {
  console.log("\n[6] Janela estreita");
  await pagina.setViewport({ width: 390, height: 800 });
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  await pagina.click(".pn-item");
  await esperar(() => document.querySelector("#pn-voltar") && getComputedStyle(document.querySelector("#pn-voltar")).display !== "none");
  confere(await pagina.evaluate(() => getComputedStyle(document.querySelector(".pn-col-lista")).display === "none"), "Janela estreita: a leitura abre por cima da lista");
  await pagina.click("#pn-voltar");
  confere(await pagina.evaluate(() => getComputedStyle(document.querySelector(".pn-col-lista")).display !== "none"), "'Voltar à lista' funciona");
  confere(await pagina.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), "Sem rolagem lateral na janela estreita");
  await captura("estreito");
  await pagina.setViewport({ width: 1440, height: 900 });
}

async function erros() {
  console.log("\n[7] Erro e servidor fora");
  const p2 = await navegador.newPage();
  await p2.setRequestInterception(true);
  p2.on("request", (r) => (r.url().includes("/api/painel/visao") ? r.abort() : r.continue()));
  await p2.goto(`${BASE}/painel`, { waitUntil: "domcontentloaded" });
  await p2.waitForSelector("#pn-erro-geral", { timeout: 15000 }).catch(() => {});
  const msg = await p2.evaluate(() => document.querySelector("#pn-erro-geral")?.innerText || "");
  confere(/Não consegui ler o ecossistema/.test(msg) && /Tentar de novo/.test(msg), "Erro sem dados: mensagem clara com 'Tentar de novo'", msg);
  await p2.close();
  await abrir("/painel/documentos");
  await esperar(() => document.querySelectorAll(".pn-item").length >= 5);
  await derrubar();
  const parada = await esperar(() => document.querySelector("#pn-parada"), 30000);
  confere(parada, "Servidor fechado: faixa 'Atualização parada'");
  confere(parada && /Última leitura às \d\d:\d\d/.test(await texto("#pn-parada")), "A faixa informa a última leitura", await texto("#pn-parada"));
  confere(await pagina.evaluate(() => !document.getElementById("pn-velho").hidden && document.querySelectorAll(".pn-item").length >= 5), "Dados antigos continuam visíveis, marcados 'Desatualizado'");
  await captura("erro");
  subir(); await esperarServidor();
  const voltou = await esperar(() => !document.querySelector("#pn-parada"), 30000);
  confere(voltou, "Servidor volta: a faixa de erro some sozinha");
}

async function principal() {
  subir();
  await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox", "--window-size=1440,900"], defaultViewport: { width: 1440, height: 900 } });
  pagina = await navegador.newPage();
  const errosPagina = [];
  pagina.on("pageerror", (e) => errosPagina.push(e.message));
  pagina.on("console", (m) => { if (m.type() === "error" && !/status of 40[349]|Failed to load resource|ERR_/.test(m.text())) errosPagina.push(m.text()); });
  try {
    await rotasEMarca();
    await dashboardEResumo();
    await documentos();
    await polling();
    await agentesESetores();
    await editorDoAgente();
    await celularEVazio();
    await erros();
    confere(errosPagina.length === 0, "nenhum erro de JavaScript na página", errosPagina.slice(0, 5));
  } catch (e) {
    falhas.push(`interrompido: ${e.message}`);
    console.log(`\nINTERROMPIDO: ${e.stack}`);
    await captura("erro-teste").catch(() => {});
  }
  await navegador.close();
  try { await derrubar(); } catch { /* já fechado */ }
  console.log(`\n${passou} verificações ok, ${falhas.length} falhas. Capturas em ${CAPTURAS}`);
  if (falhas.length) { console.log(falhas.map((f) => ` - ${f}`).join("\n")); process.exitCode = 1; }
  else fs.rmSync(caixa, { recursive: true, force: true });
}
principal();


