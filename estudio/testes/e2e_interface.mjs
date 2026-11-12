// Teste de ponta a ponta pela interface: Chrome real, clicando nos botões, numa cópia descartável de produções reais.
// Agentes e comandos pesados são simulados (sem rede e sem custo). Uso: node estudio/testes/e2e_interface.mjs [pasta para capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8799, BASE = `http://127.0.0.1:${PORTA}`, SLUG = "fim-dos-terceiros-lugares";
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "estudio-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "estudio-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
const pastaProd = path.join(caixa, "output", SLUG);

let servidor, pagina, navegador, passou = 0;
const falhas = [];

function subirServidor() {
  servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" });
}
async function derrubarServidor() {
  const fim = new Promise((r) => servidor.once("exit", r));
  servidor.kill();
  await fim;
}
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
async function esperarServidor() {
  for (let i = 0; i < 80; i++) {
    try { if ((await fetch(`${BASE}/api/producoes`)).ok) return; } catch { /* ainda subindo */ }
    await dormir(250);
  }
  throw new Error("servidor não subiu");
}

function ok(nome) { passou++; console.log(`  ok  ${nome}`); }
function confere(cond, nome, extra) {
  if (cond) ok(nome);
  else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 400)}` : ""}`); }
}
async function captura(nome) { await pagina.screenshot({ path: path.join(CAPTURAS, `${nome}.png`) }); }

const texto = (sel) => pagina.evaluate((s) => document.querySelector(s)?.innerText ?? null, sel);
const existe = (sel) => pagina.evaluate((s) => !!document.querySelector(s), sel);
const desabilitado = (sel) => pagina.evaluate((s) => document.querySelector(s)?.disabled, sel);
async function esperarTexto(sel, re, ms = 25000) {
  const fonte = re.source, flags = re.flags;
  try {
    await pagina.waitForFunction((s, f, g) => { const e = document.querySelector(s); return e && new RegExp(f, g).test(e.innerText); }, { timeout: ms, polling: 200 }, sel, fonte, flags);
    return true;
  } catch { return false; }
}
async function esperar(sel, ms = 25000) { try { await pagina.waitForSelector(sel, { timeout: ms }); return true; } catch { return false; } }
async function sumir(sel, ms = 25000) { try { await pagina.waitForFunction((s) => !document.querySelector(s), { timeout: ms, polling: 200 }, sel); return true; } catch { return false; } }
async function clicar(sel) { await pagina.waitForSelector(`${sel}:not([disabled])`, { timeout: 15000 }); await pagina.click(sel); }
async function etapa(id) { await pagina.click(`[data-etapa=${id}]`); await pagina.waitForFunction((i) => document.querySelector(`[data-etapa=${i}]`)?.classList.contains("ativa"), {}, id); await dormir(500); }
async function estado(slug = SLUG) { return (await fetch(`${BASE}/api/producoes/${slug}`)).json(); }
async function etapaApi(id, slug = SLUG) { return (await estado(slug)).etapas.find((e) => e.id === id); }
async function esperarStatus(id, status, slug = SLUG, ms = 30000) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) { const e = await etapaApi(id, slug); if (status.includes(e.status)) return e; await dormir(300); }
  return etapaApi(id, slug);
}
// Espera a versão nova existir, sem job ativo: o status antigo também é "aguardando", e esperar só por ele daria corrida.
async function esperarVersao(id, versao, slug = SLUG, ms = 30000) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) { const e = await etapaApi(id, slug); if (e.versao >= versao && !e.job && !["fila", "executando"].includes(e.status)) return e; await dormir(300); }
  return etapaApi(id, slug);
}
const pedidos = (slug = SLUG) => { const f = path.join(caixa, "output", slug, ".pedidos_recebidos.txt"); return fs.existsSync(f) ? fs.readFileSync(f, "utf-8") : ""; };
async function digitar(sel, t) { await pagina.click(sel); await pagina.type(sel, t); }
async function anotar(t) {
  await digitar("#fb-texto", t);
  await clicar("#anotar");
  await pagina.waitForFunction(() => document.querySelector("#fb-texto").value === "", { timeout: 8000 }).catch(async () => { throw new Error(`não anotou: ${await texto("#avisos")}`); });
}

async function telaProducoes() {
  console.log("\n[1] Tela de Produções");
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await esperar(".destaque h1");
  confere(/Nenhum vídeo aguardando/.test(await texto(".destaque h1")), "pasta antiga sem decisão não vira alarme de revisão", await texto(".destaque h1"));
  const corpo = await texto("#lista");
  confere(/Seu terceiro lugar sumiu/.test(corpo) && /Abrir para revisar roteiro/.test(corpo), "lista título, etapa e próxima ação");
  confere(/Publicados e arquivados \(1\)/.test(corpo), "publicado vai para a lista recolhida");
  await captura("01-producoes");
  await pagina.evaluate((s) => [...document.querySelectorAll("table.lista a.titulo")].find((a) => /terceiro lugar/.test(a.innerText)).click(), SLUG);
  confere(await esperarTexto(".barra .titulo", /terceiro lugar/), "abre a produção real com um clique");
  confere(await esperar("[data-etapa=roteiro].ativa"), "abre direto na etapa que precisa de decisão");
}

async function resolverParecerVini() {
  console.log("\n[1b] Parecer bloqueado: encaminhar para o agente responsavel");
  const slug = "e2e-parecer-mbappe";
  const pasta = path.join(caixa, "output", slug);
  fs.cpSync(pastaProd, pasta, { recursive: true });
  const meta = JSON.parse(fs.readFileSync(path.join(pasta, "metadados.json"), "utf-8"));
  meta.titulo = "Teste isolado do parecer para Mbappe";
  fs.writeFileSync(path.join(pasta, "metadados.json"), JSON.stringify(meta), "utf-8");
  fs.writeFileSync(path.join(pasta, "auditoria_texto.md"), "**BLOQUEADO**\n\n### Correções obrigatórias\n\n1. Alta — Corrigir a descrição em metadados.json para não prometer uma informação que o vídeo não confirma.\n\n### Riscos e recomendações\n\nNenhum outro ajuste obrigatório.\n", "utf-8");
  await pagina.goto(`${BASE}/producao/${slug}`, { waitUntil: "networkidle2" });
  await esperarTexto("#ir-proxima", /Resolver o parecer do Vini/);
  const chamada = await texto("#ir-proxima");
  confere(/Resolver o parecer do Vini/i.test(chamada || ""), "parecer bloqueado apresenta a acao de resolucao", chamada);
  await clicar("#ir-proxima");
  const enviado = await esperarTexto("#avisos", /Parecer encaminhado para Mbappé/);
  confere(enviado, "clique envia o parecer para Mbappé", await texto("#avisos"));
  confere(await esperarTexto(".barra .prox", /Mbappé/) && !/Resolver o parecer/.test(await texto(".barra .prox")), "depois do envio o topo diz quem está cuidando, em vez de repetir a ação", await texto(".barra .prox"));
  await pagina.reload({ waitUntil: "networkidle2" });
  confere(await esperarTexto(".barra .prox", /Mbappé/) && !(await existe("#ir-proxima")), "o encaminhamento continua visível depois de recarregar a página", await texto(".barra .prox"));
  const resumoApi = (await estado(slug)).resumo.proxima;
  confere(/Mbappé/.test(resumoApi.texto) && resumoApi.acao !== "resolver_parecer", "a API também informa que o parecer já foi encaminhado", resumoApi);
  const detalhes = await (await fetch(`${BASE}/api/producoes/${slug}/detalhes`)).json();
  const mbappes = detalhes.jobs.filter((j) => /Mbappé/.test(j.craque || ""));
  confere(mbappes.length === 1, "envio criou um trabalho real e unico para Mbappé", detalhes.jobs);
  const repetido = await (await fetch(`${BASE}/api/producoes/${slug}/resolver_parecer`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" })).json();
  const aposRepetir = await (await fetch(`${BASE}/api/producoes/${slug}/detalhes`)).json();
  confere(repetido.ja && aposRepetir.jobs.filter((j) => /Mbappé/.test(j.craque || "")).length === 1, "repetir o pedido nao duplica o job do agente");
  await fetch(`${BASE}/api/producoes/${slug}/arquivar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ arquivada: true }) });

  const slugErro = "e2e-parecer-sem-destino";
  const pastaErro = path.join(caixa, "output", slugErro);
  fs.cpSync(pastaProd, pastaErro, { recursive: true });
  fs.writeFileSync(path.join(pastaErro, "auditoria_texto.md"), "**BLOQUEADO**\n\n### Correções obrigatórias\n\n1. Confirme a mudanca no assunto antes de seguir.\n", "utf-8");
  await pagina.goto(`${BASE}/producao/${slugErro}`, { waitUntil: "networkidle2" });
  await esperarTexto("#ir-proxima", /Resolver o parecer do Vini/);
  await clicar("#ir-proxima");
  confere(await esperarTexto("#avisos", /Nao consegui identificar com seguranca/), "quando nao consegue atribuir o apontamento, explica e nao mostra sucesso");
  const semDestino = await (await fetch(`${BASE}/api/producoes/${slugErro}/detalhes`)).json();
  confere(semDestino.jobs.length === 0, "parecer ambiguo nao dispara agente por adivinhacao");
  await fetch(`${BASE}/api/producoes/${slugErro}/arquivar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ arquivada: true }) });
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await esperar("[data-etapa=roteiro].ativa");
}

async function ctaIniciarReal() {
  console.log("\n[1c] CTA 'Iniciar ...' no topo: dispara a operação real (sem fetch simulado)");
  const slug = "e2e-cta-iniciar";
  const pasta = path.join(caixa, "output", slug);
  fs.cpSync(path.join(caixa, "output", "esquema-de-piramide"), pasta, { recursive: true });
  const post = (rota, corpo) => fetch(`${BASE}/api/producoes/${slug}/${rota}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) }).then((r) => r.json());
  for (const material of ["roteiro", "cenas"]) {
    const e = await etapaApi(material, slug);
    await post("aprovar", { material, versao_id: e.versao_id });
  }
  const fim = Date.now() + 20000;
  let prox = (await estado(slug)).resumo.proxima;
  while (prox.acao !== "iniciar" && Date.now() < fim) { await dormir(300); prox = (await estado(slug)).resumo.proxima; }
  confere(prox.acao === "iniciar" && prox.etapa === "narracao" && /^Gerar narração/.test(prox.texto), "estado real: a próxima ação do topo é gerar a narração", prox);
  const jobsNarracao = async () => (await (await fetch(`${BASE}/api/producoes/${slug}/detalhes`)).json()).jobs.filter((j) => j.etapa === "narracao");
  confere((await jobsNarracao()).length === 0, "antes do clique não existe trabalho de narração");

  await pagina.goto(`${BASE}/producao/${slug}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await esperarTexto("#ir-proxima", /Gerar narração/);
  fs.writeFileSync(path.join(pasta, ".segurar_narracao"), "");
  await pagina.evaluate(() => { const b = document.querySelector("#ir-proxima"); b.click(); b.click(); });
  confere(await esperarTexto("#avisos", /Trabalho iniciado/), "CTA só confirma depois da resposta real da API", await texto("#avisos"));
  const depois = await jobsNarracao();
  confere(depois.length === 1 && ["fila", "rodando"].includes(depois[0].status), "CTA criou a narração de verdade e o clique duplo não duplicou", depois);
  confere(await esperar("[data-etapa=narracao].ativa"), "a tela abriu a etapa da narração que está rodando");
  await pagina.reload({ waitUntil: "networkidle2" });
  confere(await esperar("#faixa-execucao"), "o andamento continua visível depois de recarregar");

  // novo=false de verdade: outra aba ainda mostra o CTA antigo; o servidor recusa (já há narração ativa) e a tela não finge sucesso
  const velho = JSON.parse(JSON.stringify(await estado(slug)));
  velho.resumo.proxima = prox;
  const aba2 = await navegador.newPage();
  await aba2.setRequestInterception(true);
  aba2.on("request", (rq) => {
    if (rq.url() === `${BASE}/api/producoes/${slug}`) rq.respond({ status: 200, contentType: "application/json", body: JSON.stringify(velho) });
    else rq.continue();
  });
  await aba2.goto(`${BASE}/producao/${slug}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await aba2.waitForSelector("#ir-proxima", { timeout: 15000 });
  await aba2.click("#ir-proxima");
  await aba2.waitForFunction(() => /Nada foi disparado/.test(document.querySelector("#avisos")?.innerText || ""), { timeout: 15000 }).catch(() => {});
  const avisoAba2 = await aba2.evaluate(() => document.querySelector("#avisos")?.innerText || "");
  confere(/Nada foi disparado/.test(avisoAba2) && !/Trabalho iniciado/.test(avisoAba2), "servidor devolve novo=false e a tela explica sem mostrar sucesso", avisoAba2);
  confere((await jobsNarracao()).filter((j) => ["fila", "rodando"].includes(j.status)).length === 1, "o pedido repetido não criou outra narração");
  await aba2.close();
  fs.rmSync(path.join(pasta, ".segurar_narracao"));
  const fim2 = Date.now() + 30000;
  while (Date.now() < fim2 && (await jobsNarracao()).some((j) => ["fila", "rodando"].includes(j.status))) await dormir(300);
  confere((await jobsNarracao()).some((j) => j.status === "ok"), "a narração terminou depois de solta", await jobsNarracao());

  // falha real: a etapa fica sem destino no servidor e a tela mostra o motivo
  const resp = await fetch(`${BASE}/api/producoes/${slug}/iniciar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ etapa: "etapa-que-nao-existe" }) });
  confere(resp.status >= 400, "etapa inexistente é recusada pela API", resp.status);
  await fetch(`${BASE}/api/producoes/${slug}/arquivar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ arquivada: true }) });
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await esperar("[data-etapa=roteiro].ativa");
}

/* PROG-002: monta uma produção em que as cenas ainda não existem (arquivos e versões apagados), no servidor real. */
function copiarSemCenas(slug) {
  const pasta = path.join(caixa, "output", slug);
  fs.cpSync(path.join(caixa, "output", "esquema-de-piramide"), pasta, { recursive: true });
  return pasta;
}
async function esperarVersao0(slug, id, ms = 30000) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) { const e = await etapaApi(id, slug).catch(() => null); if (e && e.versao_id) return e; await dormir(300); }
  return null;
}
function tirarCenas(slug, pasta) {
  for (const f of ["cenas.json", "cenas_render.json", "sketch_cenas.py"]) fs.rmSync(path.join(pasta, f), { force: true });
  execFileSync(PY, ["-c", `import os,sqlite3;c=sqlite3.connect(os.environ['ESTUDIO_DADOS']+'/estudio.db');c.execute("DELETE FROM versoes WHERE slug=? AND material='cenas'",(${JSON.stringify(slug)},));c.commit()`], { env: { ...process.env, ...ambiente } });
}

async function iniciarCenasReal() {
  console.log("\n[1d] PROG-002: 'Iniciar cenas' no computador, com clique real e com o botão bloqueado");
  const post = (slug, rota, corpo) => fetch(`${BASE}/api/producoes/${slug}/${rota}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) }).then((r) => r.json());
  const jobsCenas = async (slug) => (await (await fetch(`${BASE}/api/producoes/${slug}/detalhes`)).json()).jobs.filter((j) => j.etapa === "cenas");

  // --- bloqueado: roteiro ainda sem aprovação e sem cenas
  const bloq = "e2e-cenas-bloqueada";
  const pastaB = copiarSemCenas(bloq);
  const rb = await esperarVersao0(bloq, "roteiro");
  confere(!!rb, "produção de teste do botão bloqueado foi reconhecida pelo servidor");
  tirarCenas(bloq, pastaB);
  const cenasB = await etapaApi("cenas", bloq);
  confere(cenasB.acoes.iniciar && cenasB.acoes.iniciar.habilitado === false && /Iniciar cenas/.test(cenasB.acoes.iniciar.rotulo), "estado real: 'Iniciar cenas' existe e está bloqueado sem o roteiro aprovado", cenasB.acoes.iniciar);
  await pagina.goto(`${BASE}/producao/${bloq}?etapa=cenas`, { waitUntil: "networkidle2" });
  await esperar("#iniciar");
  confere(await desabilitado("#iniciar") === true, "tela: o botão 'Iniciar cenas' está desabilitado");
  const motivoReal = await pagina.evaluate(() => [...document.querySelectorAll("ul.motivos li")].map((x) => x.innerText).join(" | "));
  confere(/Aprove o roteiro/.test(motivoReal), "tela: o motivo real aparece ao lado do botão bloqueado", motivoReal);
  const antes = (await jobsCenas(bloq)).length;
  await pagina.evaluate(() => document.querySelector("#iniciar").click());
  await dormir(600);
  confere((await jobsCenas(bloq)).length === antes, "clicar no botão bloqueado não cria trabalho");

  // texto de orientação, no DOM, com o motivo que o servidor mandar (o estado é trocado só na resposta lida pela tela)
  const trocar = (acoes) => pagina.evaluate((slug, novo) => {
    const original = window.__fetchOriginal || (window.__fetchOriginal = window.fetch.bind(window));
    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input.url;
      const r = await original(input, init);
      if (url === `/api/producoes/${slug}` && (!init.method || init.method === "GET")) {
        const body = await r.clone().json();
        const c = body.etapas.find((e) => e.id === "cenas");
        c.acoes.iniciar = novo.iniciar; c.bloqueio = null;
        return new Response(JSON.stringify(body), { status: r.status, headers: { "Content-Type": "application/json" } });
      }
      return r;
    };
    return atualizar();
  }, bloq, acoes);
  const lerMotivos = () => pagina.evaluate(() => [...document.querySelectorAll("#iniciar ~ ul.motivos li")].map((x) => x.innerText).join(" | "));
  const casos = [
    [["Falta o roteiro."], /Falta o roteiro\. Gere e aprove o roteiro antes de iniciar cenas\./, "'Falta o roteiro' diz para gerar e aprovar o roteiro"],
    [["O roteiro ainda não foi aprovado."], /Abra a etapa Roteiro e aprove a versão atual\./, "roteiro sem aprovação diz onde aprovar"],
    [["Há outra etapa rodando."], /Aguarde esse trabalho terminar e tente novamente\./, "outra etapa rodando diz para aguardar"],
    [["Falta a pesquisa (notas.md)."], /Abra a etapa pendente e conclua a ação indicada/, "'falta' genérico manda concluir a etapa pendente"],
  ];
  for (const [motivos, re, nome] of casos) {
    await trocar({ iniciar: { rotulo: "Iniciar cenas (Olise)", habilitado: false, motivos, refazer: false, principal: true } });
    await dormir(400);
    const m = await lerMotivos();
    confere(re.test(m) && await desabilitado("#iniciar") === true, `orientação na tela: ${nome}`, m);
  }
  await trocar({ iniciar: { rotulo: "Iniciar cenas (Olise)", habilitado: false, motivos: [], refazer: false, principal: true } });
  await dormir(400);
  const semMotivo = await lerMotivos();
  confere(/o sistema não informou o motivo/.test(semMotivo) && /trabalho em andamento ou etapa anterior pendente/.test(semMotivo) && await desabilitado("#iniciar") === true, "estado vazio: sem motivo do servidor, a tela admite e orienta, sem sucesso falso", semMotivo);

  // --- clique real: roteiro aprovado, cenas ainda inexistentes e nenhum trabalho em andamento
  const real = "e2e-cenas-clique";
  const pastaR = copiarSemCenas(real);
  const rr = await esperarVersao0(real, "roteiro");
  confere(!!rr, "produção de teste do clique real foi reconhecida pelo servidor");
  await post(real, "aprovar", { material: "roteiro", versao_id: rr.versao_id });
  await dormir(1500);
  tirarCenas(real, pastaR);
  const cenasR = await etapaApi("cenas", real);
  confere(cenasR.acoes.iniciar && cenasR.acoes.iniciar.habilitado === true && /^Iniciar cenas/.test(cenasR.acoes.iniciar.rotulo), "estado real: 'Iniciar cenas' está habilitado (roteiro aprovado, sem cenas)", cenasR.acoes.iniciar);
  confere((await jobsCenas(real)).length === 0, "antes do clique não existe trabalho de cenas");
  await pagina.goto(`${BASE}/producao/${real}?etapa=cenas`, { waitUntil: "networkidle2" });
  await esperar("#iniciar:not([disabled])");
  await pagina.evaluate(() => { const b = document.querySelector("#iniciar"); b.click(); b.click(); });
  confere(await esperarTexto("#avisos", /Trabalho iniciado/), "clique real: a tela mostra retorno imediato depois da resposta do servidor", await texto("#avisos"));
  const criados = await jobsCenas(real);
  confere(criados.length === 1, "clique real (e clique duplo): o servidor criou um único trabalho de cenas", criados);
  const fim = Date.now() + 30000;
  while (Date.now() < fim && (await jobsCenas(real)).some((j) => ["fila", "rodando"].includes(j.status))) await dormir(300);
  const final = await jobsCenas(real);
  confere(final.length === 1 && final[0].status === "ok", "o trabalho de cenas terminou e o resultado voltou à tela", final);
  await pagina.reload({ waitUntil: "networkidle2" });
  confere((await etapaApi("cenas", real)).versao_id != null, "as cenas aparecem como nova versão");
  await post(bloq, "arquivar", { arquivada: true });
  await post(real, "arquivar", { arquivada: true });
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await esperar("[data-etapa=roteiro].ativa");
}

async function fluxoRoteiro() {
  console.log("\n[2] Roteiro: pedir ajuste, nova versão, aprovar");
  confere(/Abrir para revisar roteiro/i.test(await texto("#ir-proxima")), "banner deixa claro que abre a etapa");
  await clicar("#ir-proxima");
  confere(await esperarTexto("#avisos", /Etapa aberta: Roteiro/), "CTA confirma que abriu o painel de decisão");
  confere(await pagina.evaluate(() => document.activeElement?.closest("#l-decisao") !== null), "CTA leva o foco para uma ação no painel de decisão");
  await esperar(".cena");
  await pagina.evaluate(() => [...document.querySelectorAll(".aba")].find((a) => /Por cena/.test(a.innerText))?.click());
  await esperar(".cena[data-cena='2']");
  const cena = await texto(".cena[data-cena='2']");
  confere(/7 horas/.test(cena) && /Cena 3/.test(cena) && /\d:\d\d/.test(cena), "cena mostra tempo e narração", cena);
  confere(/quase 7 h/.test(cena), "cena mostra o texto na tela", cena);
  confere(/coluna_relogios|relógio/i.test(cena), "cena mostra a direção visual", cena);
  await captura("02-roteiro-cenas");
  confere(/Aprovar roteiro v1 e liberar componentes/.test(await texto("#aprovar")), "botão diz a consequência real da aprovação", await texto("#aprovar"));

  const v1 = await etapaApi("roteiro");
  await pagina.select("#fb-cena", "2");
  await anotar("Troque 'tempo semanal' por uma frase mais direta.");
  await esperarTexto("#lista-feedback", /mais direta/);
  confere(/Cena 3/.test(await texto("#lista-feedback")), "pedido fica ligado à cena");
  await esperar("#enviar-ajustes");
  confere(await desabilitado("#aprovar"), "com ajuste anotado, aprovar fica travado");
  confere(/Enviar 1 ajuste para Neymar/.test(await texto("#enviar-ajustes")), "envio nomeia o agente responsável", await texto("#enviar-ajustes"));

  await pagina.reload({ waitUntil: "networkidle2" });
  await esperar("#lista-feedback");
  confere(/mais direta/.test(await texto("#lista-feedback")), "ajuste anotado sobrevive a recarregar a página");

  await pagina.evaluate(() => { const b = document.querySelector("#enviar-ajustes"); b.click(); b.click(); });
  confere(await esperarTexto("#faixa-execucao", /Neymar|Courtois/), "mostra o agente em execução");
  await captura("03-roteiro-agente-rodando");
  const fila = await (await fetch(`${BASE}/api/producoes/${SLUG}/detalhes`)).json();
  confere(fila.jobs.filter((j) => /Neymar/.test(j.titulo)).length === 1, "clique duplo em enviar criou um trabalho só", fila.jobs);
  await pagina.reload({ waitUntil: "domcontentloaded" });
  const depois = await (await fetch(`${BASE}/api/producoes/${SLUG}/detalhes`)).json();
  confere(depois.jobs.filter((j) => /Neymar/.test(j.titulo)).length === 1, "recarregar durante a execução não dispara de novo");

  confere(await esperarVersao("roteiro", 2).then((e) => e.versao === 2 && e.status === "aguardando"), "correção volta para revisão como v2");
  const recebido = pedidos();
  confere(recebido.includes("mais direta") && recebido.includes("roteiro v1") && recebido.includes(v1.versao_id ? "cena 3" : "") && /=== neymar-roteirista/.test(recebido), "agente recebeu comentário, material, versão e cena", recebido.slice(0, 500));
  confere(/=== courtois-revisor-fatos/.test(recebido), "Courtois conferiu depois do Neymar (fluxo real)");
  await esperarTexto(".etapa-botao.ativa", /v2/);
  await dormir(600);
  confere(await esperar("#mudancas .entrou"), "mostra o que mudou desde a v1");
  await captura("04-roteiro-v2-mudancas");
  const opcoes = await pagina.$$eval("#versao option", (o) => o.map((x) => x.value));
  confere(opcoes.length === 2, "as duas versões ficam disponíveis", opcoes);
  await pagina.select("#versao", opcoes[1]);
  confere(await esperarTexto("#c-faixas", /v1, que não é a atual/), "dá para consultar a versão anterior");
  await pagina.evaluate(() => [...document.querySelectorAll(".aba")].find((a) => /Texto/.test(a.innerText))?.click());
  confere(await esperarTexto(".folha.leitura", /tempo semanal/), "versão anterior mostra o texto antigo");
  confere(!(await existe("#aprovar")), "versão anterior não pode ser aprovada");
  await clicar("#c-faixas .btn");
  await esperarTexto("#aprovar", /v2/);

  confere(/Aprovar roteiro v2 e liberar componentes/.test(await texto("#aprovar")), "rótulo acompanha a nova versão", await texto("#aprovar"));
  await clicar("#aprovar");
  confere(await esperar("#ja-aprovado"), "aprovação registrada na v2");
  await pagina.reload({ waitUntil: "networkidle2" });
  await esperar("[data-etapa=roteiro]");
  await etapa("roteiro");
  confere(await esperar("#ja-aprovado"), "aprovação sobrevive a recarregar a página");
}

async function fluxoServidorReinicia() {
  console.log("\n[3] Fechar e voltar");
  await derrubarServidor();
  subirServidor();
  await esperarServidor();
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  confere(await esperar("#ja-aprovado"), "decisão continua depois de reiniciar o servidor");
  const opcoes = await pagina.$$eval("#versao option", (o) => o.length);
  confere(opcoes === 2, "versões continuam depois de reiniciar");
  const l = await (await fetch(`${BASE}/api/producoes`)).json();
  confere(l.grupos.aguardando.some((p) => p.slug === SLUG), "com decisão registrada, entra nos que aguardam você");
}

async function fluxoDependencias() {
  console.log("\n[4] Dependências depois de mudar o roteiro");
  const nar = await etapaApi("narracao");
  confere(nar.status === "desatualizada" && (nar.obsoleto.cenas || []).join() === "2", "só a narração da cena alterada fica desatualizada", nar.obsoleto);
  const vid = await etapaApi("video");
  confere(vid.status === "desatualizada", "render fica desatualizado", vid.obsoleto);
  confere(nar.acoes.iniciar && !nar.acoes.iniciar.habilitado, "narração não inicia com dependência pendente", nar.acoes.iniciar);
  const r = await fetch(`${BASE}/api/producoes/${SLUG}/iniciar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ etapa: "video" }) });
  confere(r.status === 409, "o servidor também recusa render com dependência pendente", r.status);
  confere((await etapaApi("metadados")).status === "concluida", "o que não depende da frase continua valendo");
  // PROG-002: etapa que não pode iniciar diz por quê na tela, em vez de ficar muda.
  await etapa("narracao");
  confere(await desabilitado("#iniciar") === true, "botão bloqueado na tela quando falta dependência");
  const porque = await pagina.evaluate(() => [...document.querySelectorAll("#c-painel .motivos li, .painel .motivos li, ul.motivos li")].map((x) => x.innerText).join(" | "));
  confere(porque.trim().length > 15 && !/não informou o motivo/.test(porque), "bloqueio mostra o motivo em português, sem cair no aviso genérico", porque);
  confere(/faça|abra|aprove|termine|aguarde|inicie|gere|atualize/i.test(porque), "bloqueio também diz o que fazer para liberar a etapa", porque);
}

async function fluxoNaoSeAplica() {
  console.log("\n[10] Etapa que não se aplica explica o motivo (PROG-001)");
  const sim = await (await fetch(`${BASE}/api/producoes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tema: "Teste simulado de etapa sem uso", simulado: true }) })).json();
  confere(!!sim.slug, "produção simulada criada para o teste", sim);
  const comp = await etapaApi("componentes", sim.slug);
  confere(comp.status === "nao_aplica" && /simulada/.test(comp.motivo_nao_aplica || ""), "a API traz o motivo real da regra (produção simulada)", comp);
  await pagina.goto(`${BASE}/producao/${sim.slug}?etapa=componentes`, { waitUntil: "networkidle2" });
  await esperar("#c-corpo .vazio-etapa");
  const t = await texto("#c-corpo");
  confere(/Esta etapa não é usada neste vídeo/.test(t) && /Produção simulada \(--mock\)/.test(t), "a tela mostra o aviso e o motivo na própria etapa", t);
  confere(/Para usar esta etapa/.test(t) && /sem --mock/.test(t), "a tela explica o que fazer para a etapa passar a se aplicar", t);
  confere(!/Ela não faz parte do fluxo desta produção/.test(t), "não cai no texto genérico quando há motivo", t);
  await captura("15-nao-se-aplica");
  // Etapa que se aplica não mostra o aviso (estado normal).
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=componentes`, { waitUntil: "networkidle2" });
  await esperar("#c-corpo");
  confere(!/não é usada neste vídeo/.test(await texto("#c-corpo") || ""), "etapa aplicável não mostra o aviso de não se aplica");
}

async function fluxoAssets() {
  console.log("\n[5] Assets: aprovar, substituir e preservar os aprovados");
  await etapa("componentes");
  await esperar("#contador");
  confere(/17 de 17 ainda precisam de revisão/.test(await texto("#contador")), "mostra quantos itens faltam", await texto("#contador"));
  confere(await existe(".grupo-titulo"), "assets agrupados por cena");
  await captura("05-assets");
  await clicar("[data-aprovar=mesa_cafe]");
  await esperarTexto("#contador", /16 de 17/);
  await clicar("[data-aprovar=xicara_cafe]");
  confere(await esperarTexto("#contador", /15 de 17/), "aprova um item e o contador desce");
  await pagina.click("article[data-item=pilha_livros] .img");
  confere(await esperar("#ampliado img"), "amplia o item");
  await captura("06-asset-ampliado");
  await pagina.keyboard.press("Escape");
  await sumir("dialog[open]");
  await clicar("[data-substituir=pilha_livros]");
  await anotar("Os livros estão pequenos, aumente.");
  await esperar("article[data-item=pilha_livros].pedido");
  confere(await esperarTexto("#enviar-ajustes", /Raphinha/), "substituição vai para o Raphinha");
  await clicar("#enviar-ajustes");
  const e = await esperarVersao("componentes", 2);
  confere(e.versao === 2, "substituição gera nova versão dos assets", e.versao);
  confere(pedidos().includes("item pilha_livros"), "pedido apontou o item para o agente");
  await dormir(2200);
  await esperar("article[data-item=mesa_cafe]");
  confere(/Aprovado/.test(await texto("article[data-item=mesa_cafe]")), "item aprovado continua aprovado depois da substituição", await texto("article[data-item=mesa_cafe]"));
  confere(/A revisar/.test(await texto("article[data-item=pilha_livros]")), "item substituído volta para revisão");
  confere(/15 de 17/.test(await texto("#contador")), "contador preserva o que já foi aprovado", await texto("#contador"));
  confere(/Aprovar os 15 restantes e iniciar cenas \(Olise\)/.test(await texto("#aprovar")), "botão diz que o Olise começa em seguida", await texto("#aprovar"));
  await clicar("#aprovar");
  confere(await esperarVersao("cenas", 2).then((x) => x.versao === 2), "aprovação disparou o Olise de verdade, com o roteiro novo");
  confere(pedidos().includes("afeta") || /Afetadas: cena 3/.test(pedidos()), "Olise recebeu só a cena afetada", pedidos().slice(-400));
  const aud = await esperarVersao("auditoria_texto", 2);
  confere(aud.status === "aprovada" && aud.versao === 2, "auditoria de texto refeita sozinha depois do texto mudar", aud.status);
  await etapa("cenas");
  await esperar("#contador");
  await captura("07-cenas-previas");
  await clicar("[data-aprovar=cena_0]");
  await esperarTexto("#contador", /9 de 10/);
  await clicar("#aprovar");
  await esperarStatus("cenas", ["aprovada"]);
  confere((await etapaApi("cenas")).status === "aprovada", "cenas aprovadas com o resto de uma vez");
}

async function fluxoNarracao() {
  console.log("\n[6] Narração por cena");
  await etapa("narracao");
  await esperar("#audio");
  confere(/Desatualizado/.test(await texto("article[data-item=cena_2]")), "trecho da frase alterada marcado como desatualizado");
  confere(/Gerar narração de cena 3/.test(await texto("#iniciar")), "gera só o trecho afetado", await texto("#iniciar"));
  await captura("08-narracao-desatualizada");
  await clicar("#iniciar");
  let e = await esperarVersao("narracao", 2);
  confere(e.versao === 2 && !e.obsoleto, "só a cena alterada foi regerada", e);
  await dormir(600);
  await pagina.waitForFunction(() => document.querySelector("#audio")?.duration > 0, { timeout: 8000 }).catch(() => {});
  await pagina.type("#busca", "Ray Oldenburg");
  const visiveis = await pagina.$$eval(".trecho", (t) => t.length);
  confere(visiveis === 1 && (await existe(".trecho mark")), "busca por trecho encontra e destaca", visiveis);
  await pagina.evaluate(() => { const b = document.querySelector("#busca"); b.value = ""; b.dispatchEvent(new Event("input")); });
  await pagina.click("article[data-item=cena_0] .tocar");
  await pagina.waitForFunction(() => { const a = document.querySelector("#audio"); return a && a.duration > 0 && a.currentTime > 0.2; }, { timeout: 8000 });
  ok("player toca o trecho real");
  await pagina.evaluate(() => { const a = document.querySelector("#audio"); a.pause(); a.currentTime = 1.2; });
  const seek = await pagina.evaluate(() => new Promise((r) => { const a = document.querySelector("#audio"); setTimeout(() => r(a.currentTime), 400); }));
  confere(Math.abs(seek - 1.2) < 0.2, "busca no áudio funciona (servidor com Range)", seek);
  await clicar("[data-aprovar=cena_0]");
  confere(await esperarTexto("article[data-item=cena_0]", /Aprovado/), "aprova um trecho sozinho");
  await pagina.click("article[data-item=cena_1] .texto-t");
  await dormir(300);
  await clicar("#marcar-audio");
  await pagina.evaluate(() => [...document.querySelectorAll("#fb-cats .chip")].find((c) => /Pronúncia/.test(c.innerText)).click());
  await anotar("Oldenburg está saindo errado.");
  await esperarTexto("#enviar-ajustes", /Neymar/);
  await clicar("#enviar-ajustes");
  e = await esperarVersao("narracao", 3);
  confere(e.versao === 3, "ajuste de pronúncia gerou a v3 da narração", e.versao);
  const ajustes = JSON.parse(fs.readFileSync(path.join(pastaProd, "voz_ajustes.json"), "utf-8"));
  confere(ajustes["1"] && ajustes["1"].dizer, "ajuste ficou em voz_ajustes.json, sem mudar a fala oficial", ajustes);
  await dormir(2200);
  await esperar("article[data-item=cena_0]");
  confere(/Aprovado/.test(await texto("article[data-item=cena_0]")), "trecho aprovado continua aprovado", await texto("article[data-item=cena_0]"));
  const t = await texto("#aprovar");
  confere(/Aprovar os 9 restantes e liberar vídeo final/.test(t), "botão separa aprovar de iniciar o render", t);
  await captura("09-narracao");
  await clicar("#aprovar");
  await esperarStatus("narracao", ["aprovada"]);
  confere((await etapaApi("narracao")).status === "aprovada", "narração aprovada");
}

async function fluxoVideo() {
  console.log("\n[7] Vídeo final, falha e correção");
  await etapa("video");
  confere(/Renderizar nova versão/.test(await texto("#iniciar")), "render é uma ação separada", await texto("#iniciar"));
  confere(!(await desabilitado("#iniciar")), "com tudo aprovado, render liberado");
  fs.writeFileSync(path.join(pastaProd, ".falhar_render"), "");
  await pagina.evaluate(() => { const b = document.querySelector("#iniciar"); b.click(); b.click(); });
  await esperar("#faixa-execucao, #faixa-falha");
  confere(await esperar("#faixa-falha", 20000), "falha aparece na etapa certa");
  confere(/fora do formato/.test(await texto("#erro-texto")), "mostra a mensagem relevante", await texto("#erro-texto"));
  await captura("10-video-falha");
  const det = await (await fetch(`${BASE}/api/producoes/${SLUG}/detalhes`)).json();
  confere(det.jobs.filter((j) => j.etapa === "video").length === 1, "clique duplo em gerar criou um render só", det.jobs.filter((j) => j.etapa === "video"));
  await pagina.reload({ waitUntil: "networkidle2" });
  confere(await esperar("#faixa-falha"), "falha continua visível depois de recarregar");
  fs.rmSync(path.join(pastaProd, ".falhar_render"));
  await clicar("#tentar");
  let e = await esperarVersao("video", 2);
  confere(e.versao === 2, "tentar novamente gerou a nova versão", e);
  const baixaAntes = await fetch(`${BASE}/download/${SLUG}?versao=${e.versao_id}`);
  confere(baixaAntes.status === 403, "sem aprovação, download recusado", baixaAntes.status);
  confere((await esperarVersao("auditoria_final", 2)).versao === 2, "Vini auditou o render novo sozinho");
  await dormir(600);
  await esperar("#video");
  await pagina.waitForFunction(() => document.querySelector("#video")?.duration > 0, { timeout: 10000 });
  const medida = await pagina.evaluate(() => { const r = document.querySelector(".video-caixa").getBoundingClientRect(), v = document.querySelector("#video"); return { p: r.width / r.height, d: v.duration, w: v.videoWidth, h: v.videoHeight }; });
  confere(Math.abs(medida.p - 9 / 16) < 0.01, "player preserva o 9:16", medida);
  await pagina.evaluate(async () => { const v = document.querySelector("#video"); v.muted = true; await v.play(); });
  await dormir(500);
  const tocou = await pagina.evaluate(() => document.querySelector("#video").currentTime);
  confere(tocou > 0, "render real toca no player", tocou);
  await pagina.evaluate(() => { const v = document.querySelector("#video"); v.pause(); v.currentTime = 2.5; });
  confere(await esperarTexto("#marca-tempo", /00:02\.[45]/), "pausar marca o instante do feedback", await texto("#fb-alvo"));
  await captura("11-video");
  await anotar("Logo aqui o som entra atrasado.");
  await esperarTexto("#lista-feedback", /atrasado/);
  confere(/00:02\.[45]/.test(await texto("#lista-feedback")), "feedback guarda o instante");
  await clicar("#enviar-ajustes");
  e = await esperarVersao("cenas", 3);
  await dormir(800);
  confere(pedidos().includes("em 00:02."), "o agente recebeu o instante", pedidos().slice(-300));
  const v = await esperarStatus("video", ["desatualizada"]);
  confere(v.status === "desatualizada", "correção deixa o render anterior desatualizado", v.status);
  confere((await etapaApi("cenas")).status === "aprovada", "cenas não redesenhadas seguem aprovadas");
  await pagina.reload({ waitUntil: "networkidle2" });
  await etapa("video");
  await clicar("#iniciar");
  e = await esperarVersao("video", 3);
  confere(e.versao === 3, "nova versão do vídeo volta para revisão", e.versao);
  const auditada = await esperarStatus("auditoria_final", ["aprovada"]);
  confere(auditada.status === "aprovada", "auditoria repetida com o mesmo parecer não fica desatualizada", auditada);
  await dormir(2200);
  await esperar("#aprovar");
  confere(/Aprovar vídeo final v3 e liberar download/.test(await texto("#aprovar")), "botão diz o que a aprovação final faz", await texto("#aprovar"));
  await clicar("#aprovar");
  confere(await esperar("#baixar"), "download aparece depois de aprovar");
  const href = await pagina.$eval("#baixar", (a) => a.href);
  const baixa = await fetch(href);
  const bytes = (await baixa.arrayBuffer()).byteLength;
  confere(baixa.status === 200 && /video\/mp4/.test(baixa.headers.get("content-type")) && bytes > 1000, "arquivo final baixado de verdade", [baixa.status, bytes]);
  await captura("12-video-aprovado");
  const antiga = await pagina.$$eval("#versao option", (o) => o.map((x) => x.value));
  await pagina.select("#versao", antiga[antiga.length - 1]);
  await esperarTexto("#c-faixas", /v1, que não é a atual/);
  await esperar("#video");
  confere(await pagina.evaluate(() => /\/blob\//.test(document.querySelector("#video").src)), "o vídeo antigo continua disponível");

  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=video`, { waitUntil: "networkidle2" });
  await pagina.evaluate((slug) => {
    const original = window.fetch.bind(window);
    window.__ctaIniciar = [];
    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input.url;
      if (url === `/api/producoes/${slug}/iniciar` && init.method === "POST") {
        window.__ctaIniciar.push(JSON.parse(init.body));
        return new Response(JSON.stringify({ job: 999, novo: true }), { status: 201, headers: { "Content-Type": "application/json" } });
      }
      const response = await original(input, init);
      if (url === `/api/producoes/${slug}` && (!init.method || init.method === "GET")) {
        const body = await response.clone().json();
        body.resumo.proxima = { texto: "Iniciar vídeo final", etapa: "video", tipo: "voce", acao: "iniciar" };
        return new Response(JSON.stringify(body), { status: response.status, headers: { "Content-Type": "application/json" } });
      }
      return response;
    };
  }, SLUG);
  confere(await esperarTexto("#ir-proxima", /Iniciar vídeo final/), "ação pronta mantém o rótulo de iniciar", await texto("#ir-proxima"));
  await clicar("#ir-proxima");
  confere(await esperarTexto("#avisos", /Trabalho iniciado/), "CTA de início dá confirmação depois do retorno da API", await texto("#avisos"));
  const chamadaCta = await pagina.evaluate(() => window.__ctaIniciar);
  confere(chamadaCta.length === 1 && chamadaCta[0].etapa === "video", "CTA inicia a etapa indicada em vez de apenas abrir o painel", chamadaCta);
}

async function fluxoNovoVideo() {
  console.log("\n[8] Novo vídeo pela interface");
  const tema = "Por que os jovens saem menos de casa";
  const slug = "por-que-os-jovens-saem-menos-de-casa";
  fs.mkdirSync(path.join(caixa, "output", slug));
  fs.writeFileSync(path.join(caixa, "output", slug, ".falhar_modric-pesquisador-tema"), "");
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await clicar("#novo");
  await esperar("#tema");
  await pagina.type("#tema", tema);
  await captura("13-novo-video");
  await pagina.click("dialog .botoes .btn.principal");
  confere(await esperarTexto(".barra .titulo", /saem menos/), "cria a produção e abre a revisão");
  confere(await esperar("#faixa-falha", 20000), "falha do agente aparece com a etapa");
  confere(/não abriu/.test(await texto("#erro-texto")), "mostra a mensagem do agente", await texto("#erro-texto"));
  fs.rmSync(path.join(caixa, "output", slug, ".falhar_modric-pesquisador-tema"));
  await clicar("#tentar");
  const e = await esperarVersao("roteiro", 1, slug);
  confere(e.versao === 1, "Modric, Neymar e Courtois rodaram em sequência e o roteiro aguarda você", e);
  const rec = pedidos(slug);
  confere(rec.indexOf("=== modric") < rec.indexOf("=== neymar") && rec.indexOf("=== neymar") < rec.indexOf("=== courtois"), "ordem real do fluxo");
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await esperar(".cartao-revisao");
  confere(/^1 vídeo aguardando sua revisão/.test(await texto(".destaque h1")), "tela inicial conta só o que ainda aguarda: o aprovado saiu da conta", await texto(".destaque h1"));
  await captura("14-producoes-final");
  const dup = await fetch(`${BASE}/api/producoes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tema }) });
  confere(dup.status === 409, "tema repetido não abre produção duplicada", dup.status);
  const [a, b] = await Promise.all([1, 2].map(() => fetch(`${BASE}/api/producoes/${slug}/iniciar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ etapa: "roteiro", forcar: true }) }).then((r) => r.json())));
  confere(a.job === b.job && [a.novo, b.novo].filter(Boolean).length === 1, "dois pedidos simultâneos viram um trabalho só", [a, b]);
  const fora = await fetch(`${BASE}/api/producoes/${slug}/aprovar`, { method: "POST", headers: { "Content-Type": "application/json", Origin: "https://exemplo.com" }, body: "{}" });
  confere(fora.status === 403, "outro site não consegue chamar a API", fora.status);
  await fluxoResiliencia(slug);
}

const lerPid = (slug) => execFileSync(PY, ["-c", `import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute("SELECT pid FROM jobs WHERE slug=? AND status='rodando' ORDER BY id DESC",(sys.argv[2],)).fetchone()[0])`, path.join(ambiente.ESTUDIO_DADOS, "estudio.db"), slug], { encoding: "utf-8" }).trim();
async function esperarRodando(id, slug, ms = 15000) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) { if ((await etapaApi(id, slug)).status === "executando") return true; await dormir(200); }
  return false;
}

async function fluxoResiliencia(slug) {
  console.log("\n[9] Reinício, processo morto e cancelamento");
  await esperarVersao("roteiro", 1, slug);
  const marca = path.join(caixa, "output", slug, ".lento");
  const post = (etapaId) => fetch(`${BASE}/api/producoes/${slug}/iniciar`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ etapa: etapaId, forcar: true }) });

  fs.writeFileSync(marca, "");
  await post("pesquisa");
  await esperarRodando("pesquisa", slug);
  await derrubarServidor();
  fs.rmSync(marca);
  subirServidor();
  await esperarServidor();
  const durante = await etapaApi("pesquisa", slug);
  confere(["executando", "concluida"].includes(durante.status), "trabalho continua depois de reiniciar o servidor", durante.status);

  // Cancelamento pela interface: o agente simulado está dormindo; sem a marca, a próxima vez já não dorme.
  await esperarStatus("pesquisa", ["concluida", "falhou"], slug, 130000);
  fs.writeFileSync(marca, "");
  await post("pesquisa");
  await esperarRodando("pesquisa", slug);
  await pagina.goto(`${BASE}/producao/${slug}?etapa=pesquisa`, { waitUntil: "networkidle2" });
  await esperar("#faixa-execucao");
  await pagina.evaluate(() => [...document.querySelectorAll("#faixa-execucao .btn")].find((b) => /Cancelar/.test(b.innerText)).click());
  confere((await esperarStatus("pesquisa", ["concluida"], slug)).status === "concluida", "cancelar encerra o trabalho e a versão anterior continua");

  // Processo morto sem avisar: o batimento para e a etapa vira falha, com ação de tentar de novo.
  await post("pesquisa");
  await esperarRodando("pesquisa", slug);
  execFileSync("taskkill", ["/T", "/F", "/PID", lerPid(slug)], { stdio: "ignore" });
  fs.rmSync(marca);
  const morta = await esperarStatus("pesquisa", ["falhou"], slug, 45000);
  confere(morta.status === "falhou" && /parou sem terminar/.test(morta.falha?.erro || ""), "processo morto vira falha explicada", morta.falha);
  await pagina.goto(`${BASE}/producao/${slug}?etapa=pesquisa`, { waitUntil: "networkidle2" });
  confere(await esperar("#tentar"), "falha oferece tentar novamente");
  await clicar("#tentar");
  confere((await esperarStatus("pesquisa", ["concluida"], slug)).status === "concluida", "nova tentativa conclui");
}

async function principal() {
  subirServidor();
  await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required", "--window-size=1440,900"], defaultViewport: { width: 1440, height: 900 } });
  pagina = await navegador.newPage();
  const errosPagina = [];
  pagina.on("pageerror", (e) => errosPagina.push(e.message));
  pagina.on("console", (m) => { if (m.type() === "error" && !/status of 40[39]|Failed to load resource/.test(m.text())) errosPagina.push(m.text()); });
  pagina.on("dialog", (d) => d.accept());
  try {
    await telaProducoes();
    await resolverParecerVini();
    await ctaIniciarReal();
    await iniciarCenasReal();
    await fluxoRoteiro();
    await fluxoServidorReinicia();
    await fluxoDependencias();
    await fluxoAssets();
    await fluxoNarracao();
    await fluxoVideo();
    await fluxoNovoVideo();
    await fluxoNaoSeAplica();
    confere(errosPagina.length === 0, "nenhum erro de JavaScript na página", errosPagina.slice(0, 5));
  } catch (e) {
    falhas.push(`interrompido: ${e.message}`);
    console.log(`\nINTERROMPIDO: ${e.stack}`);
    await captura("erro").catch(() => {});
    console.log(await pagina.evaluate(() => document.body.innerText.slice(0, 1500)).catch(() => ""));
  }
  await navegador.close();
  await derrubarServidor();
  console.log(`\n${passou} verificações ok, ${falhas.length} falhas. Capturas em ${CAPTURAS}`);
  if (falhas.length) { console.log(falhas.map((f) => ` - ${f}`).join("\n")); process.exitCode = 1; }
  else fs.rmSync(caixa, { recursive: true, force: true });
}

principal();
