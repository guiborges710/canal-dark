// Estilos novos e seletor de temas, em Chrome real, numa cópia descartável. Agentes e narração são simulados; o desenho e o export são reais.
// Uso: node estudio/testes/e2e_estilos.mjs [pasta para capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8797, BASE = `http://127.0.0.1:${PORTA}`;
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "estilos-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });
const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "estilos-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });
const saida = path.join(caixa, "output");

let servidor, pagina, navegador, passou = 0;
const falhas = [], errosJs = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 600)}` : ""}`); } }
const captura = (n) => pagina.screenshot({ path: path.join(CAPTURAS, `${n}.png`) });
const get = async (u) => (await fetch(BASE + u)).json();
const post = async (u, c) => { const r = await fetch(BASE + u, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(c || {}) }); return { status: r.status, d: await r.json().catch(() => ({})) }; };
const sel = (s, ms = 25000) => pagina.waitForSelector(s, { timeout: ms });
const clicar = async (s) => { await pagina.waitForSelector(`${s}:not([disabled])`, { timeout: 20000 }); await pagina.click(s); };
const texto = (s) => pagina.evaluate((x) => document.querySelector(x)?.innerText ?? null, s);
const sqlite = (sql) => JSON.parse(execFileSync(PY, ["-c", `import json,os,sqlite3;c=sqlite3.connect(os.environ['ESTUDIO_DADOS']+'/estudio.db');c.row_factory=sqlite3.Row;print(json.dumps([dict(r) for r in c.execute(${JSON.stringify(sql)})]))`], { encoding: "utf-8", env: { ...process.env, ...ambiente } }));
async function ate(fn, nome, ms = 90000) { const fim = Date.now() + ms; let v; while (Date.now() < fim) { v = await fn(); if (v) return v; await dormir(300); } throw new Error(`tempo esgotado: ${nome}`); }
const noDe = async (slug, no) => (await get(`/api/producoes/${slug}/estudio`)).linhas.find((x) => x.no === no);
const statusNo = async (slug, no, st, ms) => {
  try { return await ate(async () => { const n = await noDe(slug, no); return n && st.includes(n.status) ? n : null; }, `${no} em ${st}`, ms); }
  catch (e) { const v = await get(`/api/producoes/${slug}/estudio`); throw new Error(`${e.message}; nós: ${JSON.stringify((v.linhas || []).map((x) => [x.no, x.status, x.nota]))}`); }
};
const pedidos = (slug) => fs.readFileSync(path.join(saida, slug, ".pedidos_recebidos.txt"), "utf-8");
const pedidoDe = (slug, agente) => pedidos(slug).split("=== ").filter((x) => x.startsWith(agente)).pop() || "";
const ler = (slug, nome) => JSON.parse(fs.readFileSync(path.join(saida, slug, nome), "utf-8"));

/* Mede o MP4 de verdade: quantos pares de quadros seguidos são diferentes, e o tamanho. */
function medirVideo(mp4) {
  const prog = "import json,subprocess,sys,tempfile,glob\nimport numpy as np\nfrom PIL import Image\nd=tempfile.mkdtemp()\nsubprocess.run(['ffmpeg','-y','-loglevel','error','-i',sys.argv[1],'-vf','fps=30,scale=135:240',d+'/%04d.png'],check=True)\nq=[np.asarray(Image.open(f).convert('RGB'),dtype='float32') for f in sorted(glob.glob(d+'/*.png'))]\nv=[float(np.abs(a-b).mean()) for a,b in zip(q[:-1],q[1:])]\nprint(json.dumps({'quadros':len(q),'mudam':sum(x>0.02 for x in v)/max(1,len(v)),'pico':max(v)}))";
  return JSON.parse(execFileSync(PY, ["-c", prog, mp4], { encoding: "utf-8" }));
}

async function abrirNovo() {
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await clicar("#novo");
  await sel(".novo .estilo-cartao");
}

async function escolha_de_estilo() {
  console.log("\n[1] Na criação aparecem os quatro estilos, com prévia real");
  await abrirNovo();
  const cartoes = await pagina.$$eval(".estilo-cartao", (x) => x.map((e) => ({ id: e.dataset.estilo, nome: e.querySelector("b").innerText, texto: e.innerText, demo: !!e.querySelector("[data-demo]"), video: !!e.querySelector("video") })));
  confere(cartoes.map((x) => x.id).join() === "cartoes,sketch,cartoon_alive,documentary_collage", "Quatro ids estáveis", cartoes.map((x) => x.id));
  for (const n of ["Cartão", "Scratch", "Cartoon Vivo", "Colagem Documental"]) confere(cartoes.some((x) => x.nome.includes(n)), `Estilo visível: ${n}`, cartoes.map((x) => x.nome));
  confere(cartoes.every((x) => x.demo && x.video && x.texto.includes("Melhor para:")), "Cada estilo tem descrição, melhor uso, prévia e botão de demonstração");
  await pagina.waitForFunction(() => [...document.querySelectorAll(".estilo-video")].every((v) => v.readyState >= 2 && v.videoWidth === 406), { timeout: 20000 });
  const t0 = await pagina.$$eval(".estilo-video", (x) => x.map((v) => v.currentTime));
  await dormir(900);
  const t1 = await pagina.$$eval(".estilo-video", (x) => x.map((v) => v.currentTime));
  confere(t1.every((t, i) => t !== t0[i]), "As quatro prévias estão tocando de verdade", [t0, t1]);
  await captura("01-novo-projeto");
  await pagina.click('[data-demo="cartoon_alive"]');
  await sel("#demo-estilo video");
  await pagina.waitForFunction(() => document.querySelector("#demo-estilo video").readyState >= 2 && document.querySelector("#demo-estilo video").duration > 5, { timeout: 15000 });
  confere(true, "Ver demonstração abre o vídeo real do renderizador");
  confere((await pagina.$eval('[data-estilo="sketch"]', (e) => e.getAttribute("aria-checked"))) === "true", "Abrir a demonstração não muda a escolha");
  await pagina.keyboard.press("Escape");
  await dormir(200);
  await pagina.evaluate(() => document.querySelectorAll("dialog[open]").forEach((d, i, l) => { if (i === l.length - 1 && d.querySelector("#demo-estilo")) { d.close(); d.remove(); } }));
  // Variação do Scratch
  await pagina.click('[data-estilo="sketch"]');
  await sel("#estilo-variante");
  confere((await pagina.$$eval("#estilo-variante option", (x) => x.map((o) => o.innerText))).includes("Caderno pautado"), "Caderno pautado é variação interna do Scratch");
  confere(!(await pagina.$('[data-estilo="caderno_pautado"]')), "Caderno não vira um quinto estilo");
  await pagina.select("#estilo-variante", "caderno_pautado");
  await sel("#estilo-opcao-papel");
  await pagina.select("#estilo-opcao-papel", "branco");
  await pagina.select("#estilo-opcao-traco", "marcador");
  await pagina.type("#tema", "teste caderno pautado");
  await pagina.select("#fluxo", "canal");
  await pagina.click('.novo .botoes .principal');
  await sel("#selo-estilo");
  await ate(async () => (await texto("#selo-estilo")) || null, "selo");
  confere((await texto("#selo-estilo")).includes("Scratch · Caderno pautado"), "A variação aparece no Estúdio", await texto("#selo-estilo"));
  const e = ler("teste-caderno-pautado", "estilo.json");
  confere(e.estilo === "sketch" && e.variante === "caderno_pautado" && e.opcoes.papel === "branco" && e.opcoes.traco === "marcador", "Variação gravada no projeto", e);
  await statusNo("teste-caderno-pautado", "ap_roteiro", ["aguardando"]);
  const r1 = await post(`/api/producoes`, { tema: "estilo que nao existe", estilo: "Cartoon Vivo" });
  confere(r1.status === 400, "Nome visível não vale como chave", r1.d);
  const r2 = await post(`/api/producoes`, { tema: "horizontal em cartoon", estilo: "cartoon_alive", formato: "horizontal" });
  confere(r2.status === 400, "Cartoon não aceita formato horizontal", r2.d);
}

async function temas() {
  console.log("\n[2] Temas sem vídeo e gerar um tema");
  await abrirNovo();
  await sel("#gerar-tema");
  confere((await texto("#temas-prontos")).includes("Nenhum tema separado"), "Sem temas, a janela diz isso", await texto("#temas-prontos"));
  confere(await pagina.$eval("#gerar-tema", (b) => b.classList.contains("principal")), "Sem temas, o botão de gerar fica em destaque");
  await captura("02-sem-temas");
  await pagina.click("#gerar-tema");
  const r = await post("/api/temas/gerar");
  confere(sqlite("SELECT COUNT(*) n FROM jobs WHERE etapa='gerar_tema'")[0].n === 1, "Clique duplo em gerar vira um trabalho só", r.d);
  await sel('[data-usar-tema]', 30000);
  const lista = await get("/api/temas");
  confere(lista.temas.length === 1 && lista.temas[0].origem === "Modric", "Gerar traz um tema só, do Modric", lista.temas);
  confere(fs.existsSync(path.join(saida, "modric_tema_dormir-menos.md")), "O tema fica no arquivo do agente, não numa lista à parte");
  confere(sqlite("SELECT spec FROM jobs WHERE etapa='gerar_tema'").every((j) => JSON.parse(j.spec).agente === "modric-pesquisador-tema"), "Quem gera é o Modric");
  await pagina.click('[data-usar-tema]');
  const campos = await pagina.evaluate(() => ({ tema: document.querySelector("#tema").value, briefing: document.querySelector("#briefing").value }));
  confere(campos.tema === "Por que os jovens estão dormindo menos" && campos.briefing.includes("modric_tema_dormir-menos.md") && campos.briefing.includes("Contexto, não preguiça"), "Escolher o tema preenche tema e briefing", campos);
  await captura("03-tema-gerado");
  await pagina.evaluate(() => { document.querySelector("dialog[open]").close(); document.querySelector("dialog")?.remove(); });
  // Temas da lista do Modric: quem já tem vídeo não aparece; quem tem projeto começado leva ao projeto.
  fs.writeFileSync(path.join(saida, "modric_10_temas.md"), `# 10 temas\n\n## 1. O fim dos terceiros lugares: por que os lugares somem\n\n**Descrição:** Tem vídeo pronto.\n\n## 2. Adolescentes e companhias de IA\n\n**Descrição:** Sem vídeo.\n\n**Direção de ângulo:** Olhar o contexto.\n\n## 3. Esquema de pirâmide nas redes\n\n**Descrição:** Projeto começado.\n`, "utf-8");
  fs.writeFileSync(path.join(saida, "ideias.json"), JSON.stringify({ ideias: [{ titulo: "Ideia simulada 1", angulo: "x" }, { titulo: "Geração que não aposenta", angulo: "Haaland", por_que_funciona: "demanda" }] }), "utf-8");
  const d = await get("/api/temas");
  const titulos = d.temas.map((x) => x.titulo);
  confere(!titulos.some((x) => x.includes("terceiros lugares")), "Tema com vídeo pronto não aparece", titulos);
  confere(titulos.some((x) => x.includes("companhias de IA")), "Tema sem vídeo aparece", titulos);
  confere(d.temas.find((x) => x.titulo.includes("pirâmide"))?.projeto === "esquema-de-piramide", "Tema com projeto começado aponta para o projeto", d.temas);
  confere(titulos.includes("Geração que não aposenta") && !titulos.some((x) => x.includes("simulada")), "Lê as ideias do Haaland, sem os exemplos do --mock", titulos);
  await abrirNovo();
  await sel('[data-abrir-tema]');
  confere(!(await pagina.$eval("#gerar-tema", (b) => b.classList.contains("principal"))), "Com temas na lista, gerar deixa de ser o destaque");
  await pagina.click('[data-abrir-tema]');
  await sel("#selo-estilo");
  confere(pagina.url().includes("/estudio/esquema-de-piramide"), "Abrir leva ao projeto começado, sem criar outro", pagina.url());
  // Falha do agente aparece com o motivo
  fs.writeFileSync(path.join(saida, ".falhar_tema"), "");
  await post("/api/temas/gerar");
  const fal = await ate(async () => { const x = await get("/api/temas"); return x.erro_geracao ? x : null; }, "erro ao gerar");
  confere(fal.erro_geracao.length > 3 && !fal.gerando, "Se o Modric falhar, a janela mostra o motivo", fal.erro_geracao);
  fs.rmSync(path.join(saida, ".falhar_tema"));
  fs.rmSync(path.join(saida, "modric_10_temas.md"));
  fs.rmSync(path.join(saida, "ideias.json"));
}

/* Do início até a narração aprovada, pelo grafo publicado. Devolve a execução. */
async function produzir(slug) {
  const ex = (await get(`/api/producoes/${slug}/estudio`)).execucao.id;
  const aprovar = async (no) => { const n = await statusNo(slug, no, ["aguardando"]); const r = await post(`/api/execucoes/${ex}/aprovar`, { no, versao_id: n.versao.id }); confere(r.status === 200, `${slug}: aprovou ${no}`, r.d); };
  await aprovar("ap_roteiro");
  await aprovar("ap_componentes");  // decisão de 2026-11-03: componentes para os quatro estilos, sem o nó se_sketch
  await aprovar("ap_cenas");
  await statusNo(slug, "aud_texto", ["concluido"]);
  await statusNo(slug, "narracao", ["aguardando_inicio"]);
  await post(`/api/execucoes/${ex}/liberar`, { no: "narracao" });
  await aprovar("ap_narracao");
  return ex;
}

async function exportarDeVerdade(slug) {
  fs.writeFileSync(path.join(saida, slug, ".dur_narracao"), "2.8");
  await pagina.goto(`${BASE}/editor/${slug}`, { waitUntil: "networkidle2" });
  await sel("#ed-estilo");
  const r = await post(`/api/producoes/${slug}/corte_exportar`, { confirmado: true });
  confere(r.status < 300, `${slug}: exportação aceita`, r.d);
  await ate(async () => { const j = sqlite(`SELECT status, erro FROM jobs WHERE slug='${slug}' AND titulo='Exportando o corte' ORDER BY id DESC LIMIT 1`)[0]; if (j && j.status === "falhou") throw new Error(`export falhou: ${j.erro}`); return j && j.status === "ok"; }, "export", 300000);
  return path.join(saida, slug, "video.mp4");
}

async function criarPelaTela(tema, estilo) {
  await abrirNovo();
  await pagina.click(`[data-estilo="${estilo}"]`);
  await pagina.type("#tema", tema);
  await pagina.select("#fluxo", "canal");
  await pagina.click(".novo .botoes .principal");
  await sel("#selo-estilo");
}

async function cartoon_e_colagem() {
  console.log("\n[3] Cartoon Vivo: da criação ao MP4 exportado");
  const c = "teste-cartoon";
  await criarPelaTela("teste cartoon", "cartoon_alive");
  await ate(async () => (await texto("#selo-estilo"))?.includes("Cartoon Vivo"), "selo cartoon");
  confere(true, "Estúdio mostra Cartoon Vivo");
  confere(ler(c, "estilo.json").estilo === "cartoon_alive" && sqlite(`SELECT estilo FROM producoes WHERE slug='${c}'`)[0].estilo === "cartoon_alive", "O id técnico fica gravado no projeto");
  await produzir(c);
  confere(pedidoDe(c, "neymar").includes("cena de desenho animado"), "A direção visual chegou ao agente de roteiro", pedidoDe(c, "neymar").slice(0, 400));
  confere(!pedidoDe(c, "modric").includes("desenho animado"), "A pesquisa não recebe direção visual");
  const olise = pedidoDe(c, "olise");
  confere(olise.includes("media/cartoon_lib.py") && olise.includes("use o elenco, as poses, as expressões"), "As regras de assets chegaram ao Olise");
  confere(olise.includes("estilos-por-camadas") && olise.includes("sem sketch_cenas.py"), "As regras de cena chegaram ao Olise");
  const raph = pedidoDe(c, "raphinha");  // decisão de 2026-11-03: Raphinha desenha componentes nos quatro estilos
  confere(raph !== "" && raph.includes("Estilo Cartoon Vivo: componentes são o elenco") && !raph.includes("Estilo Scratch"), "Raphinha é acionado e recebe as regras de componentes do Cartoon Vivo", raph.slice(0, 300));
  const cenas = ler(c, "cenas.json");
  confere(cenas.every((x) => x.tipo === "cartoon_alive"), "As cenas saem com o tipo do estilo");
  confere(!fs.existsSync(path.join(saida, c, "sketch_cenas.py")), "Não há código por cena");
  const bia = cenas.flatMap((x) => x.personagens.filter((p) => p.id === "bia").flatMap((p) => p.poses.map((k) => k.pose)));
  confere(cenas.length >= 2 && cenas.every((x) => x.personagens.some((p) => p.id === "bia")) && new Set(bia).size >= 2, "Duas cenas com o mesmo personagem em poses diferentes", bia);
  const mp4 = await exportarDeVerdade(c);
  const m = medirVideo(mp4);
  confere(m.quadros > 60 && m.mudam > 0.9 && m.pico > 1.5, "O MP4 exportado tem movimento real", m);
  console.log("    medição:", JSON.stringify(m));
  await captura("04-editor-cartoon");
  confere((await texto("#ed-estilo")).includes("Cartoon Vivo"), "O editor mostra o estilo", await texto("#ed-estilo"));

  console.log("\n[4] Colagem Documental: documento, recorte, conexão e câmera");
  const k = "teste-colagem";
  await criarPelaTela("teste colagem", "documentary_collage");
  await ate(async () => (await texto("#selo-estilo"))?.includes("Colagem Documental"), "selo colagem");
  confere(true, "Estúdio mostra Colagem Documental");
  await produzir(k);
  confere(pedidoDe(k, "neymar").includes("investigação"), "A direção da colagem chegou ao roteiro");
  confere(pedidoDe(k, "olise").includes("media/colagem_lib.py"), "As regras da colagem chegaram ao Olise");
  const ck = ler(k, "cenas.json")[0];
  const tipos = ck.recortes.map((x) => x.tipo);
  confere(tipos.includes("documento") && tipos.includes("foto") && ck.conexoes.length && ck.camera.chaves.length >= 2, "Cena com documento, recorte, conexão e câmera", tipos);
  const mk = medirVideo(await exportarDeVerdade(k));
  confere(mk.quadros > 60 && mk.mudam > 0.9 && mk.pico > 1.5, "O MP4 exportado tem movimento real", mk);
  console.log("    medição:", JSON.stringify(mk));
  await captura("05-editor-colagem");

  console.log("\n[5] Fechar e reabrir os dois");
  servidor.kill();
  await dormir(800);
  subir();
  await esperarServidor();
  for (const [slug, nome, id] of [[c, "Cartoon Vivo", "cartoon_alive"], [k, "Colagem Documental", "documentary_collage"]]) {
    await pagina.goto(`${BASE}/estudio/${slug}`, { waitUntil: "networkidle2" });
    await ate(async () => (await texto("#selo-estilo"))?.includes(nome), `selo ${nome}`);
    confere(true, `${nome} continua no Estúdio depois de reiniciar o servidor`);
    await pagina.goto(`${BASE}/editor/${slug}`, { waitUntil: "networkidle2" });
    await sel("#ed-estilo");
    confere((await texto("#ed-estilo")).includes(nome), `${nome} continua no editor`);
    const d = await get(`/api/producoes/${slug}`);
    confere(d.estilo === id, `${nome}: a API devolve ${id}`, d.estilo);
  }
}

async function trocar_estilo() {
  console.log("\n[6] Trocar o estilo");
  // Antes da produção: não invalida nada
  const a = (await post("/api/producoes", { tema: "troca antes", estilo: "cartoes", fluxo: "canal" })).d.slug;
  await pagina.goto(`${BASE}/estudio/${a}`, { waitUntil: "networkidle2" });
  await statusNo(a, "pesquisa", ["concluido"], 20000).catch(() => {});
  await clicar("#selo-estilo");
  await sel("#troca-estilo .estilo-cartao");
  await pagina.click('#troca-estilo [data-estilo="cartoon_alive"]');
  await clicar("#estilo-continuar");
  await sel("#estilo-confirmar");
  confere(await pagina.$("#estilo-livre"), "Sem cenas produzidas, avisa que nada é invalidado", await texto("#troca-estilo"));
  await pagina.click("#estilo-confirmar");
  await ate(async () => (await texto("#selo-estilo"))?.includes("Cartoon Vivo"), "selo troca antes");
  confere(ler(a, "estilo.json").estilo === "cartoon_alive", "A troca antes da produção vale");
  // Trocar enquanto a pesquisa ainda roda: o roteiro, que vem depois, já nasce com a direção nova.
  const b = (await post("/api/producoes", { tema: "troca cedo", estilo: "cartoes", fluxo: "canal" })).d.slug;
  const cedo = await post(`/api/producoes/${b}/estilo`, { estilo: "cartoon_alive" });
  confere(cedo.d.trocado, "Troca durante a pesquisa é aceita", cedo.d);
  await statusNo(b, "ap_roteiro", ["aguardando"]);
  confere(pedidoDe(b, "neymar").includes("desenho animado"), "O roteiro já recebe a direção do novo estilo");

  // Projeto já iniciado, com cenas e vídeo: a tela lista o que será refeito antes de confirmar.
  const c = "teste-cartoon";
  fs.writeFileSync(path.join(saida, c, "auditoria.md"), "**APROVADO**\n", "utf-8");
  await ate(async () => (await post(`/api/producoes/${c}/estilo/impacto`, { estilo: "documentary_collage" })).d.refazer.some((x) => x.etapa === "auditoria_final"), "auditoria entrar como versão", 30000);
  await pagina.goto(`${BASE}/estudio/${c}`, { waitUntil: "networkidle2" });
  await clicar("#selo-estilo");
  await sel("#troca-estilo .estilo-cartao");
  await pagina.click('#troca-estilo [data-estilo="documentary_collage"]');
  await clicar("#estilo-continuar");
  await sel("#estilo-refazer");
  const lista = await texto("#estilo-refazer");
  for (const nome of ["as cenas", "o vídeo final", "a auditoria de texto", "a auditoria final"]) confere(lista.includes(nome), `Avisa que precisa refazer ${nome}`, lista);
  const mantem = await texto("#estilo-mantem");
  confere(mantem.includes("o roteiro") && mantem.includes("a narração") && mantem.includes("os metadados"), "Avisa o que continua valendo", mantem);
  confere(fs.existsSync(path.join(saida, c, "cenas.json")) && ler(c, "estilo.json").estilo === "cartoon_alive", "Só mostrar o aviso não muda nada");
  await captura("06-aviso-troca");
  const semConfirmar = await post(`/api/producoes/${c}/estilo`, { estilo: "documentary_collage" });
  confere(semConfirmar.d.precisa_confirmar && !semConfirmar.d.trocado, "O servidor recusa invalidar sem a confirmação", semConfirmar.d);
  const assinaturaVelha = await post(`/api/producoes/${c}/estilo/impacto`, { estilo: "documentary_collage" });
  const velha = await post(`/api/producoes/${c}/estilo`, { estilo: "documentary_collage", confirmar: "outra-coisa" });
  confere(velha.d.precisa_confirmar, "Confirmação que não bate com o aviso não vale", assinaturaVelha.d.assinatura);
  const videoAntes = fs.statSync(path.join(saida, c, "video.mp4")).size;
  await pagina.click("#estilo-confirmar");
  await ate(async () => (await texto("#selo-estilo"))?.includes("Colagem Documental"), "selo depois da troca");
  confere(true, "Depois de confirmar, o Estúdio mostra o novo estilo");
  const guardado = fs.readdirSync(path.join(saida, c, "_troca_estilo"));
  const dentro = fs.readdirSync(path.join(saida, c, "_troca_estilo", guardado[0]));
  confere(dentro.includes("cenas.json") && dentro.includes("video.mp4") && fs.statSync(path.join(saida, c, "_troca_estilo", guardado[0], "video.mp4")).size === videoAntes, "Nada é apagado: o estilo antigo fica guardado", dentro);
  confere(fs.existsSync(path.join(saida, c, "roteiro.txt")) && fs.existsSync(path.join(saida, c, "falas")), "Roteiro e narração ficam na pasta");
  const ex = (await get(`/api/producoes/${c}/estudio`)).execucao;
  confere(ex.status === "ativa", "A execução reabre", ex.status);
  const compC = await statusNo(c, "ap_componentes", ["aguardando"]);  // o estilo novo refaz os componentes antes das cenas
  await post(`/api/execucoes/${ex.id}/aprovar`, { no: "ap_componentes", versao_id: compC.versao.id });
  await statusNo(c, "ap_cenas", ["aguardando"]);
  confere(ler(c, "cenas.json").every((x) => x.tipo === "documentary_collage"), "O Olise refez as cenas no novo estilo");
  confere(pedidoDe(c, "olise").includes("media/colagem_lib.py"), "O Olise recebeu as regras do novo estilo");
  confere((await noDe(c, "roteiro")).status === "concluido" && sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${c}' AND etapa LIKE '%:roteiro' `)[0].n === 1, "O roteiro não foi refeito");
  const vid = await get(`/api/producoes/${c}/estudio`);
  confere(vid.videos.length === 0, "O vídeo do estilo antigo deixa de ser o atual", vid.videos.map((v) => v.numero));
  confere(sqlite(`SELECT COUNT(*) n FROM versoes WHERE slug='${c}' AND material='video'`)[0].n >= 1, "O vídeo antigo continua no histórico");
  const v1 = await noDe(c, "video");
  confere(["pendente", "aguardando_inicio"].includes(v1.status), "O render não dispara sozinho", v1.status);

  // Só a variação: mantém as cenas
  const s = "teste-caderno-pautado";
  const ex2 = (await get(`/api/producoes/${s}/estudio`)).execucao.id;
  const n = await statusNo(s, "ap_roteiro", ["aguardando"]);
  await post(`/api/execucoes/${ex2}/aprovar`, { no: "ap_roteiro", versao_id: n.versao.id });
  await statusNo(s, "ap_componentes", ["aguardando"]);
  confere(pedidoDe(s, "raphinha").includes("Variação Caderno pautado") && pedidoDe(s, "raphinha").includes("papel = branco"), "As regras da variação chegam ao agente de assets");
  const comp = await noDe(s, "ap_componentes");
  await post(`/api/execucoes/${ex2}/aprovar`, { no: "ap_componentes", versao_id: comp.versao.id });
  await statusNo(s, "ap_cenas", ["aguardando"]);
  const im = (await post(`/api/producoes/${s}/estilo/impacto`, { estilo: "sketch", variante: "caderno_pautado", opcoes: { papel: "bege", traco: "grafite" } })).d;
  confere(!im.refazer.some((x) => x.etapa === "cenas") && im.mantem.some((x) => x.etapa === "cenas"), "Mudar só a variação não invalida as cenas", im);
  const tr = await post(`/api/producoes/${s}/estilo`, { estilo: "sketch", variante: "caderno_pautado", opcoes: { papel: "bege", traco: "grafite" }, confirmar: im.assinatura });
  confere(tr.d.trocado && ler(s, "estilo.json").opcoes.papel === "bege", "A variação muda", tr.d);
  // Bloqueado se estiver publicado
  const p = (await post(`/api/producoes/esquema-de-piramide/estilo/impacto`, { estilo: "cartoon_alive" })).d;
  confere(p.nova.estilo === "cartoon_alive", "O impacto também vale para projeto antigo", p);
  fs.writeFileSync(path.join(saida, "esquema-de-piramide", "upload.json"), "{}", "utf-8");
  const bl = await post(`/api/producoes/esquema-de-piramide/estilo`, { estilo: "cartoon_alive", confirmar: p.assinatura });
  confere(bl.status === 409, "Vídeo já publicado não troca de estilo", bl.d);
  fs.rmSync(path.join(saida, "esquema-de-piramide", "upload.json"));
}

async function antigos() {
  console.log("\n[7] Projetos antigos continuam iguais");
  const slug = "fim-dos-terceiros-lugares";
  const antes = fs.statSync(path.join(saida, slug, "video.mp4")).size;
  await pagina.goto(`${BASE}/estudio/${slug}`, { waitUntil: "networkidle2" });
  await ate(async () => (await texto("#selo-estilo"))?.includes("Scratch"), "selo antigo");
  confere(true, "Projeto antigo aparece como Scratch, pelo que as cenas dizem");
  confere((await pagina.$$(".e-cena")).length === 10, "As cenas continuam na tira");
  confere(!fs.existsSync(path.join(saida, slug, "estilo.json")), "Abrir não grava nada no projeto");
  await pagina.goto(`${BASE}/editor/${slug}`, { waitUntil: "networkidle2" });
  await sel("#ed-estilo");
  const c = await get(`/api/producoes/${slug}/corte`);
  confere(c.estado.modo === "cenas" && c.estado.cenas[0].fonte.tipo === "sketch", "O editor lê o projeto por cenas, como antes", c.estado.modo);
  confere(fs.statSync(path.join(saida, slug, "video.mp4")).size === antes && !fs.existsSync(path.join(saida, slug, "corte.json")), "O vídeo não muda e nenhum corte é criado");
  confere(sqlite(`SELECT estilo FROM producoes WHERE slug='${slug}'`)[0].estilo === "sketch", "O id antigo continua sendo o gravado");
  const fluxos = await get("/api/fluxos");
  confere(fluxos.condicoes ? fluxos.condicoes.estilo.valores.includes("cartoon_alive") : true, "Os fluxos oferecem os novos estilos na condição");
  // Mudar o estilo não altera a condição do fluxo publicado: sketch continua indo para o Raphinha
  const antigo = (await post("/api/producoes", { tema: "scratch de sempre", estilo: "scratch", fluxo: "canal" }));
  confere(antigo.status === 201 && ler(antigo.d.slug, "estilo.json").estilo === "sketch", "scratch é aceito e vira o id de sempre", antigo.d);
}

function subir() { servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" }); }
async function esperarServidor() { for (let i = 0; i < 120; i++) { try { if ((await fetch(`${BASE}/api/fluxos`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }

try {
  subir();
  await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required"], defaultViewport: { width: 1500, height: 1000 } });
  pagina = await navegador.newPage();
  pagina.on("pageerror", (e) => errosJs.push(e.message));
  await escolha_de_estilo();
  await temas();
  await cartoon_e_colagem();
  await trocar_estilo();
  await antigos();
  confere(errosJs.length === 0, "Nenhum erro de JavaScript", errosJs);
} catch (e) {
  falhas.push(`exceção: ${e.message}`);
  console.log(`  FALHOU  ${e.stack}`);
  if (pagina) await captura("erro").catch(() => {});
} finally {
  if (navegador) await navegador.close().catch(() => {});
  if (servidor) servidor.kill();
  await dormir(500);
  try { fs.rmSync(caixa, { recursive: true, force: true, maxRetries: 8, retryDelay: 400 }); } catch { /* o Windows segura a pasta por um instante: é uma cópia descartável */ }
}
console.log(`\n${passou} verificações ok, ${falhas.length} falhas. Capturas em ${CAPTURAS}`);
if (falhas.length) { console.log(falhas.map((f) => ` - ${f}`).join("\n")); process.exit(1); }
