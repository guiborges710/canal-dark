// As demonstrações de aceite do Corte, em Chrome real, clicando na interface, numa cópia descartável de produções reais.
// Export, compositor, ffmpeg e a comparação com a prévia são reais. Agentes e narração são simulados (sem rede, sem custo).
// Uso: node estudio/testes/e2e_corte.mjs [pasta para capturas]
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
const PORTA = Number(process.env.E2E_PORTA) || 8798, BASE = `http://127.0.0.1:${PORTA}`, SLUG = "fim-dos-terceiros-lugares";
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "corte-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "corte-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });
const pastaProd = path.join(caixa, "output", SLUG);

let servidor, pagina, navegador, passou = 0;
const falhas = [], errosJs = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function subir() { servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" }); }
async function esperarServidor() { for (let i = 0; i < 120; i++) { try { if ((await fetch(`${BASE}/api/fluxos`)).ok) return; } catch { /* subindo */ } await dormir(250); } throw new Error("servidor não subiu"); }
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 500)}` : ""}`); } }
const captura = (n) => pagina.screenshot({ path: path.join(CAPTURAS, `${n}.png`) });
const get = async (u) => (await fetch(BASE + u)).json();
const post = async (u, c) => { const r = await fetch(BASE + u, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(c || {}) }); return { status: r.status, d: await r.json().catch(() => ({})) }; };
const sel = (s, ms = 25000) => pagina.waitForSelector(s, { timeout: ms });
const clicar = async (s) => { await pagina.waitForSelector(`${s}:not([disabled])`, { timeout: 20000 }); await pagina.click(s); };
const texto = (s) => pagina.evaluate((x) => document.querySelector(x)?.innerText ?? null, s);
const definir = async (s, v) => { await sel(s); await pagina.evaluate((x, val) => { const e = document.querySelector(x); e.value = val; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); }, s, String(v)); };
const salvo = () => pagina.waitForFunction(() => document.querySelector("#ed-salvo")?.innerText === "Salvo", { timeout: 20000 });
const sqlite = (sql) => JSON.parse(execFileSync(PY, ["-c", `import json,os,sqlite3;c=sqlite3.connect(os.environ['ESTUDIO_DADOS']+'/estudio.db');c.row_factory=sqlite3.Row;print(json.dumps([dict(r) for r in c.execute(${JSON.stringify(sql)})]))`], { encoding: "utf-8", env: { ...process.env, ...ambiente } }));
async function ate(fn, nome, ms = 90000) { const fim = Date.now() + ms; let v; while (Date.now() < fim) { v = await fn(); if (v) return v; await dormir(300); } throw new Error(`tempo esgotado: ${nome}`); }
const noDe = async (slug, no) => (await get(`/api/producoes/${slug}/estudio`)).linhas.find((x) => x.no === no);
const statusNo = async (slug, no, st, ms) => {
  try { return await ate(async () => { const n = await noDe(slug, no); return n && st.includes(n.status) ? n : null; }, `${no} em ${st}`, ms); }
  catch (e) { const v = await get(`/api/producoes/${slug}/estudio`); throw new Error(`${e.message}; nós: ${JSON.stringify((v.linhas || []).map((x) => [x.no, x.status, x.nota]))} ${v.erro || ""}`); }
};

function grafoBase() {
  const n = (id, tipo, nome, col, lin, config = {}) => ({ id, tipo, nome, x: 60 + col * 260, y: 60 + lin * 150, desativado: false, config });
  return { n, liga: (de, para, porta) => ({ id: `${de}${porta ? `.${porta}` : ""}->${para}`, de, porta: porta || null, para, mapa: [] }) };
}

async function uma_produção_antiga_abre() {
  console.log("\n[1] Um projeto anterior abre, e o que existia continua");
  const antes = fs.readFileSync(path.join(pastaProd, "video.mp4")).length;
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await sel(`[data-estudio="${SLUG}"]`);
  await captura("01-projetos");
  await pagina.click(`[data-estudio="${SLUG}"]`);
  await sel("#e-agentes .agente-linha");
  await sel(".e-cena img");
  await dormir(600);
  const agentes = await pagina.$$eval(".agente-linha b", (x) => x.map((e) => e.innerText));
  confere(agentes.includes("Modric") && agentes.includes("Neymar") && agentes.includes("Vini"), "Estúdio mostra os agentes reais", agentes);
  confere(!(await pagina.$(".agente-linha.rodando")), "Nenhum agente aparece ativo sem trabalho rodando");
  confere((await texto("#selo-fluxo")).includes("Fluxo fixo antigo"), "Projeto antigo continua no fluxo antigo");
  confere((await pagina.$$(".e-cena")).length === 10, "As 10 cenas aparecem na tira");
  await pagina.click('.e-cena[data-i="2"]');
  await dormir(500);
  const t = await pagina.evaluate(() => document.getElementById("e-video").currentTime);
  confere(Math.abs(t - 12.21) < 0.2, "Clicar na cena posiciona a prévia", t);
  confere(/cena 3/i.test(await texto("#e-direcao")), "Direção visual da cena selecionada");
  confere((await texto("#e-aprovando")).includes("versão que você aprova"), "Diz qual versão está sendo vista e aprovada");
  await pagina.click('.agente-linha[data-no="roteiro"]');
  await sel("#painel-execucao");
  confere((await texto("#painel-execucao")).includes("neymar-roteirista"), "Clicar no agente abre a execução");
  await captura("02-estudio");
  await pagina.keyboard.press("Escape");
  confere(!fs.existsSync(path.join(pastaProd, "corte.json")), "Abrir o projeto não cria corte.json");
  confere(fs.readFileSync(path.join(pastaProd, "video.mp4")).length === antes, "Abrir o projeto não mexe no vídeo");
}

async function editar_e_exportar() {
  console.log("\n[2] Editar legenda, trocar ilustração, encurtar a cena; reabrir; o MP4 confere com a prévia");
  await pagina.goto(`${BASE}/editor/${SLUG}`, { waitUntil: "networkidle2" });
  await sel("#fontes-faltando", 15000).catch(() => {});
  await pagina.waitForFunction(() => !document.querySelector("#fontes-faltando") && document.querySelector("#ed-tela")?.dataset.pronto === "1", { timeout: 180000 });
  confere(true, "Fontes de imagem desenhadas do sketch_cenas.py");
  const antes = await get(`/api/producoes/${SLUG}/corte`);
  confere(antes.estado.modo === "cenas" && antes.compilado.segmentos[0].fonte_tipo === "sketch", "Editor conectado à composição anterior ao render, não ao MP4");
  await captura("03-editor-aberto");

  // quadro a quadro e cursor
  await clicar("#quadro-mais");
  await pagina.waitForFunction(() => document.querySelector("#ed-quadro").innerText.startsWith("Quadro 2 "), { timeout: 8000 });
  confere(true, "Avança quadro a quadro");
  await definir("#ed-tempo", "5");
  await pagina.waitForFunction(() => document.querySelector("#ed-tela").dataset.quadro === "150", { timeout: 8000 });
  confere(true, "Digitar o tempo posiciona o cursor");

  // Legenda na cena 3
  const seg = antes.compilado.segmentos[2];
  await pagina.click(`.clipe[data-cena="${seg.cena}"]`);
  await sel("#cena-duracao");
  await definir("#ed-tempo", (seg.ini + 1).toFixed(3));
  await pagina.waitForFunction((f) => Number(document.querySelector("#ed-tela").dataset.quadro) === f, { timeout: 8000 }, Math.round((seg.ini + 1) * 30));
  await clicar("#nova-legenda");
  await sel("#legenda-texto");
  await salvo();
  await definir("#legenda-texto", "Legenda feita à mão");
  await salvo();
  await definir("#legenda-estilo", "viral");
  await salvo();
  await definir("#legenda-y", "700");
  await salvo();
  await definir("#legenda-fim", "6");
  await salvo();

  // Trocar a ilustração por arquivo local
  await pagina.click(`.clipe[data-cena="${seg.cena}"]`);
  await clicar("#trocar-asset");
  await sel("#galeria .galeria-item");
  const png = path.join(os.tmpdir(), `corte-teste-${process.pid}.png`);
  execFileSync(PY, ["-c", `from PIL import Image,ImageDraw;i=Image.new('RGB',(800,600),(255,196,0));d=ImageDraw.Draw(i);d.ellipse((100,50,700,550),fill=(20,20,20));i.save(r'${png}')`]);
  await (await pagina.$('#galeria input[type=file]')).uploadFile(png);
  await pagina.waitForFunction(() => document.querySelector("#asset-nome")?.innerText.includes("corte-teste"), { timeout: 15000 });
  await salvo();
  confere(true, "Trocou a ilustração por um arquivo local");
  await definir("#asset-escala", "1");
  await salvo();
  await definir("#asset-y", "1000");
  await salvo();

  // Encurtar
  const durAntes = seg.fim - seg.ini;
  await sel("#cena-duracao");
  await pagina.evaluate(() => { const e = document.querySelector("#cena-duracao"); e.value = "4"; e.dispatchEvent(new Event("input", { bubbles: true })); });
  const efeito = await texto("#efeito-duracao");
  confere(/perde/.test(efeito), "Mostra o efeito na fala antes de aplicar", efeito);
  await definir("#cena-duracao", "4");
  await salvo();
  const depois = await get(`/api/producoes/${SLUG}/corte`);
  const seg2 = depois.compilado.segmentos[2];
  confere(Math.abs((seg2.fim - seg2.ini) - 4) < 0.04, "A cena ficou com 4 s", seg2.fim - seg2.ini);
  confere(depois.compilado.total_s < antes.compilado.total_s - (durAntes - 4) + 0.1, "As cenas seguintes andaram");
  confere(depois.compilado.avisos.some((a) => a.tipo === "corte_fala" && a.cena === seg.cena), "Sinaliza o corte de fala");
  confere(await pagina.evaluate(() => !!document.querySelector('[data-aviso="corte_fala"]')), "O aviso aparece na tela");
  await captura("04-editor-editado");

  // Desfazer e refazer
  await clicar("#desfazer"); await dormir(300); await salvo();
  const desfeito = await get(`/api/producoes/${SLUG}/corte`);
  confere(Math.abs((desfeito.compilado.segmentos[2].fim - desfeito.compilado.segmentos[2].ini) - durAntes) < 0.05, "Desfazer volta a duração");
  await clicar("#refazer"); await dormir(300); await salvo();

  // Reabrir
  await pagina.goto(`${BASE}/editor/${SLUG}?t=${(seg.ini + 1).toFixed(3)}`, { waitUntil: "networkidle2" });
  await sel("#ed-tela");
  const f = Math.round((seg.ini + 1) * 30);
  await pagina.waitForFunction((q) => Number(document.querySelector("#ed-tela").dataset.quadro) === q && document.querySelector("#ed-tela").dataset.pronto === "1", { timeout: 20000 }, f);
  await dormir(800);
  const reaberto = await get(`/api/producoes/${SLUG}/corte`);
  const leg = reaberto.estado.legendas.itens.find((x) => x.texto === "Legenda feita à mão");
  const cn = reaberto.estado.cenas.find((x) => x.id === seg.cena);
  confere(leg && leg.manual && leg.y === 700, "Reabrir: a legenda continua", leg);
  confere(cn.midia && cn.midia.nome.includes("corte-teste"), "Reabrir: a ilustração continua");
  confere(Math.abs(cn.out - cn.in + cn.congela - 4) < 0.01, "Reabrir: a duração continua");

  // Prévia desse quadro
  await pagina.evaluate(() => { const c = document.getElementById("ed-tela"); window.__p = c.toDataURL("image/png"); });
  const previa = path.join(CAPTURAS, "previa_quadro.png");
  fs.writeFileSync(previa, Buffer.from((await pagina.evaluate(() => window.__p)).split(",")[1], "base64"));
  // quadro sem edição, depois do corte
  const seg5 = reaberto.compilado.segmentos[5];
  const f5 = seg5.f0 + 40;
  await definir("#ed-tempo", (f5 / 30 + 0.001).toFixed(3));
  await pagina.waitForFunction((q) => Number(document.querySelector("#ed-tela").dataset.quadro) === q, { timeout: 20000 }, f5);
  await dormir(400);
  const previa5 = path.join(CAPTURAS, "previa_quadro_5.png");
  fs.writeFileSync(previa5, Buffer.from((await pagina.evaluate(() => document.getElementById("ed-tela").toDataURL("image/png"))).split(",")[1], "base64"));
  const audioPrevia = path.join(CAPTURAS, "previa_audio.wav");
  fs.writeFileSync(audioPrevia, Buffer.from(await (await fetch(`${BASE}/api/producoes/${SLUG}/corte/audio`)).arrayBuffer()));

  // Exportar: pede confirmação porque há corte de fala
  await clicar("#exportar");
  await sel("#confirmar-export");
  confere((await texto("#confirmar-export")).includes("corta"), "Antes de exportar, lista o corte de fala");
  await captura("05-confirmar-export");
  const recusa = await post(`/api/producoes/${SLUG}/corte_exportar`, {});
  confere(recusa.status === 409, "Servidor recusa exportar sem a confirmação", recusa.status);
  const jobsAntes = sqlite(`SELECT COUNT(*) n FROM jobs WHERE titulo='Exportando o corte'`)[0].n;
  await pagina.click("#exportar-assim");
  const dupla = await Promise.all([post(`/api/producoes/${SLUG}/corte_exportar`, { confirmado: true }), post(`/api/producoes/${SLUG}/corte_exportar`, { confirmado: true })]);
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE titulo='Exportando o corte'`)[0].n === jobsAntes + 1, "Clique duplo em exportar vira um trabalho só", dupla.map((x) => x.d));
  const fim = await ate(async () => { const r = sqlite(`SELECT status, erro FROM jobs WHERE titulo='Exportando o corte' ORDER BY id DESC LIMIT 1`)[0]; return r.status === "rodando" || r.status === "fila" ? null : r; }, "exportação", 420000);
  confere(fim.status === "ok", "A exportação terminou", fim);
  const mp4 = path.join(pastaProd, "video.mp4");
  const dur = Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", mp4], { encoding: "utf-8" }));
  confere(Math.abs(dur - reaberto.compilado.total_s) < 0.1, "A duração do MP4 é a da linha do tempo", [dur, reaberto.compilado.total_s]);
  const codec = execFileSync("ffprobe", ["-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_name,width,height,pix_fmt,color_range,r_frame_rate", "-of", "csv=p=0", mp4], { encoding: "utf-8" }).trim();
  confere(codec.includes("h264,1080,1920,yuv420p,tv"), "H.264, 1080×1920, yuv420p, faixa TV", codec);

  const conf = JSON.parse(execFileSync(PY, [path.join(AQUI, "comparar_midia.py"), mp4, previa, String(f), previa5, String(f5), audioPrevia, String(reaberto.compilado.fps)], { encoding: "utf-8" }));
  console.log("     ", JSON.stringify(conf));
  confere(conf.psnr_editado > 34, `Quadro com legenda e ilustração confere com a prévia (${conf.psnr_editado} dB)`);
  confere(conf.psnr_sem_edicao > 34, `Quadro depois do corte confere com a prévia (${conf.psnr_sem_edicao} dB)`);
  confere(conf.audio_correl > 0.98 && Math.abs(conf.audio_atraso_ms) <= 45, `Áudio confere no timecode (correlação ${conf.audio_correl}, ${conf.audio_atraso_ms} ms)`);
  confere(conf.quadro_errado_psnr < conf.psnr_sem_edicao, "A conferência distingue quadros diferentes", conf);

  // Revisão final: vira nova versão; move legenda: áudio, assets e aprovações ficam
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=video`, { waitUntil: "networkidle2" });
  await sel("#barra-video");
  confere((await texto("#barra-video")).includes("Saiu do editor"), "O vídeo exportado entra em revisão como versão do editor");
  await sel("#comparar-versoes");
  await pagina.click("#comparar-versoes");
  await sel(".comparar video");
  confere((await pagina.$$(".comparar video")).length === 2, "Compara versões do vídeo");
  await captura("06-comparar");
  await pagina.keyboard.press("Escape");
  await pagina.click("#editar-no-ponto");
  await pagina.waitForFunction(() => location.pathname.startsWith("/editor/"), { timeout: 8000 });
  confere(true, "Do vídeo final, abre o editor no ponto");

  const itensAntes = JSON.stringify(sqlite(`SELECT material, sha, decisao FROM itens WHERE slug='${SLUG}' ORDER BY id`));
  const narrAntes = sqlite(`SELECT COUNT(*) n FROM versoes WHERE slug='${SLUG}' AND material='narracao'`)[0].n;
  await sel("#ed-salvo");
  await dormir(1000);
  const e3 = await get(`/api/producoes/${SLUG}/corte`);
  confere(e3.situacao.em_dia, "Depois de exportar, o corte está em dia");
  const novo = JSON.parse(JSON.stringify(e3.estado));
  novo.legendas.itens.find((x) => x.texto === "Legenda feita à mão").y = 720;
  const r3 = await post(`/api/producoes/${SLUG}/corte_salvar`, { estado: novo, rev: e3.estado.rev });
  confere(r3.status === 200 && !r3.d.situacao.em_dia, "Mover a legenda marca o corte para nova revisão", r3.d.situacao);
  confere(JSON.stringify(sqlite(`SELECT material, sha, decisao FROM itens WHERE slug='${SLUG}' ORDER BY id`)) === itensAntes, "Mover a legenda preserva as aprovações de assets e narração");
  confere(sqlite(`SELECT COUNT(*) n FROM versoes WHERE slug='${SLUG}' AND material='narracao'`)[0].n === narrAntes, "Mover a legenda não cria nova narração");
  const velha = await post(`/api/producoes/${SLUG}/corte_salvar`, { estado: novo, rev: e3.estado.rev });
  confere(velha.status === 409, "Gravar sobre uma revisão velha é recusado", velha.status);
  const est = await get(`/api/producoes/${SLUG}`);
  confere(est.etapas.find((x) => x.id === "video").status === "desatualizada", "O vídeo final fica desatualizado até nova exportação");
  const v = await post(`/api/producoes/${SLUG}/corte_versao`, { nota: "teste" });
  confere(v.d.numero === 1, "Nova versão de corte", v.d);
}

async function aprovacao_no_fluxo() {
  console.log("\n[3] Editor de fluxos: grafo real, canvas, validação; aprovação entre roteiro e narração; aprovar duas vezes");
  await pagina.goto(`${BASE}/fluxos/canal`, { waitUntil: "networkidle2" });
  await sel('.fx-no[data-no="ap_roteiro"]');
  await dormir(300);
  const g0 = (await get("/api/fluxos/canal")).grafo;
  confere(g0.nos.some((n) => n.id === "cenas_v" && n.config.agente === "olise-diretor-arte") && g0.nos.some((n) => n.id === "aud_final"), "A primeira abertura mostra o grafo do fluxo real");
  confere((await texto("#fx-erros")).includes("Sem erros"), "O fluxo real valida sem erros", await texto("#fx-erros"));
  await captura("07-fluxo-real");
  const criado = await post("/api/fluxos", { nome: "Com aprovação no meio", copiar_de: null });
  const id = criado.d.id;
  await pagina.goto(`${BASE}/fluxos/${id}`, { waitUntil: "networkidle2" });
  await sel('.fx-no[data-no="briefing"]');

  // Paleta e configuração pela interface
  const adiciona = async (tipo, x, y) => {
    const antes = await pagina.$$eval(".fx-no", (e) => e.map((k) => k.dataset.no));
    await pagina.click(`[data-paleta="${tipo}"]`);
    await pagina.waitForFunction((n) => document.querySelectorAll(".fx-no").length === n + 1, { timeout: 5000 }, antes.length);
    const novo = (await pagina.$$eval(".fx-no", (e) => e.map((k) => k.dataset.no))).find((k) => !antes.includes(k));
    await pagina.evaluate((i, nx, ny) => { const n = Fluxos.g.nos.find((k) => k.id === i); n.x = nx; n.y = ny; Fluxos.desenharGrafo(); Fluxos.mudou(); }, novo, x, y);
    return novo;
  };
  const modric = await adiciona("agente", 340, 60);
  await definir("#no-agente", "modric-pesquisador-tema");
  await definir("#no-tarefa", "pesquisa");
  const neymar = await adiciona("agente", 620, 60);
  await definir("#no-agente", "neymar-roteirista");
  await definir("#no-tarefa", "roteiro");
  const aprov = await adiciona("aprovacao", 900, 60);
  await definir("#no-material", "roteiro");
  const narr = await adiciona("render", 1180, 60);
  await definir("#no-acao", "narracao");
  await definir("#no-inicio", "auto");

  // Arrastar muda só a posição
  await pagina.evaluate(() => { const f = Fluxos.g.nos.find((k) => k.id === "fim"); f.x = 1460; f.y = 60; Fluxos.desenharGrafo(); Fluxos.enquadrar(); }); await dormir(100);
  const yAntes = (await pagina.evaluate((i) => Fluxos.g.nos.find((k) => k.id === i).y, aprov));
  const box = await (await pagina.$(`.fx-no[data-no="${aprov}"]`)).boundingBox();
  await pagina.mouse.move(box.x + 100, box.y + 40); await pagina.mouse.down(); await pagina.mouse.move(box.x + 100, box.y + 120, { steps: 5 }); await pagina.mouse.up();
  await pagina.waitForFunction(() => document.querySelector("#fx-salvo")?.innerText === "Rascunho salvo", { timeout: 6000 });
  const g1 = (await get(`/api/fluxos/${id}`)).grafo;
  confere(g1.nos.find((n) => n.id === aprov).y > yAntes + 20, "Arrastar o nó persiste a posição", [yAntes, g1.nos.find((n) => n.id === aprov).y]);

  // Reconectar pela porta
  const liga = async (de, para, porta = "") => {
    const p = await pagina.$(`.fx-no[data-no="${de}"] .porta.saida${porta ? `.${porta}` : ""}`);
    const b = await p.boundingBox(), a = await (await pagina.$(`.fx-no[data-no="${para}"]`)).boundingBox();
    await pagina.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await pagina.mouse.down(); await pagina.mouse.move(a.x + a.width / 2, a.y + a.height / 2, { steps: 6 }); await pagina.mouse.up();
    await dormir(100);
  };
  const enq = () => pagina.evaluate(() => Fluxos.enquadrar());
  await enq(); await dormir(100);
  await liga("briefing", modric); await liga(modric, neymar); await liga(neymar, aprov); await liga(aprov, narr); await liga(narr, "fim");
  await pagina.waitForFunction(() => document.querySelector("#fx-salvo")?.innerText === "Rascunho salvo", { timeout: 6000 });
  await dormir(400);
  const g2 = (await get(`/api/fluxos/${id}`)).grafo;
  confere(g2.arestas.length === 5, "Conexões pelas portas persistem", g2.arestas.map((a) => a.id));

  // Validação no nó: inacessível, referência inexistente, ciclo, tipos
  const conf = async (g, teste, nome) => { const r = await post(`/api/fluxos/${id}/salvar`, { grafo: g }); confere(r.d.problemas.some(teste), nome, r.d.problemas); };
  const clone = () => JSON.parse(JSON.stringify(g2));
  let c = clone(); c.nos.push({ id: "solto", tipo: "juncao", nome: "Solta", x: 0, y: 0, config: {} });
  await conf(c, (p) => p.no === "solto" && /inacessível/.test(p.texto), "Valida nó inacessível");
  c = clone(); c.arestas.push({ id: "volta", de: narr, para: neymar, porta: null, mapa: [] });
  await conf(c, (p) => p.nivel === "erro" && /ciclo/.test(p.texto), "Valida ciclo");
  c = clone(); c.nos.find((n) => n.id === neymar).config.agente = "agente-que-nao-existe";
  await conf(c, (p) => p.no === neymar && /não existe/.test(p.texto), "Valida referência inexistente");
  c = clone(); c.arestas = c.arestas.filter((a) => a.de !== modric); c.arestas.push({ id: "b->n", de: "briefing", para: neymar, porta: null, mapa: [] });
  await conf(c, (p) => p.no === neymar && /obrigatória/.test(p.texto), "Valida entrada obrigatória");
  c = clone(); c.arestas.find((a) => a.para === aprov).mapa = [{ saida: "roteiro", entrada: "cenas" }];
  await conf(c, (p) => /incompatíveis/.test(p.texto), "Valida compatibilidade de dados");

  // Erro aparece no nó, e publicar é recusado
  await post(`/api/fluxos/${id}/salvar`, { grafo: (() => { const k = clone(); k.nos.find((n) => n.id === neymar).config.agente = "agente-que-nao-existe"; return k; })() });
  await pagina.goto(`${BASE}/fluxos/${id}`, { waitUntil: "networkidle2" });
  await sel(`.fx-no[data-no="${neymar}"].com-erro`);
  confere(true, "O erro aparece no nó correspondente");
  await captura("08-fluxo-erro");
  confere((await post(`/api/fluxos/${id}/publicar`, {})).status === 409, "Publicar com erro é recusado");
  await post(`/api/fluxos/${id}/salvar`, { grafo: g2 });
  await pagina.goto(`${BASE}/fluxos/${id}`, { waitUntil: "networkidle2" });
  await sel(`.fx-no[data-no="${neymar}"]`);

  // Desativar mostra dependências
  await pagina.click(`.fx-no[data-no="${modric}"]`);
  await clicar("#no-desativar");
  await sel("#impacto-desativar");
  confere((await texto("#impacto-desativar")).includes("fica sem origem"), "Desativar mostra quem fica sem entrada", await texto("#impacto-desativar"));
  await captura("09-impacto-desativar");
  await pagina.keyboard.press("Escape");

  // Teste com projeto de exemplo
  await clicar("#fx-testar");
  await sel("#ensaio-projeto");
  await pagina.select("#ensaio-projeto", "esquema-de-piramide");
  await clicar("#ensaio-rodar");
  await sel(".ensaio-passo");
  confere((await pagina.$$(".ensaio-passo")).length >= 5, "Testa com um projeto de exemplo, sem acionar agente");
  await pagina.keyboard.press("Escape");

  await clicar("#fx-publicar");
  await pagina.waitForFunction(() => document.querySelector("#fx-publicada")?.innerText.includes("v1"), { timeout: 8000 });
  confere(true, "Publicou a v1");
  await captura("10-fluxo-publicado");

  // Execução
  await pagina.goto(BASE, { waitUntil: "networkidle2" });
  await clicar("#novo");
  await sel("#tema");
  await pagina.type("#tema", "teste aprovação no meio");
  await pagina.select("#fluxo", id);
  await pagina.evaluate(() => { document.querySelectorAll(".amostra").forEach((b) => { if (b.dataset.valor === "viral") b.click(); }); });
  await captura("11-novo-projeto");
  await pagina.click(".novo .botoes .principal");
  await pagina.waitForFunction(() => location.pathname.startsWith("/estudio/"), { timeout: 10000 });
  const slug = "teste-aprovacao-no-meio";
  const aguardando = await statusNo(slug, aprov, ["aguardando"]);
  confere(aguardando.versao, "A execução para na aprovação inserida", aguardando);
  confere((await noDe(slug, narr)).status === "pendente", "A narração aguarda a decisão");
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:${narr}'`)[0].n === 0, "Nenhuma narração foi iniciada antes de aprovar");
  await sel(`[data-aprovar-no="${aprov}"]`);
  await captura("12-aguardando-aprovacao");

  // Aprovar duas vezes: clique na tela e pedidos simultâneos
  const exId = (await get(`/api/producoes/${slug}/estudio`)).execucao.id;
  const corpo = { no: aprov, versao_id: aguardando.versao.id };
  const [a, b] = await Promise.all([post(`/api/execucoes/${exId}/aprovar`, corpo), post(`/api/execucoes/${exId}/aprovar`, corpo)]);
  const c3 = await post(`/api/execucoes/${exId}/aprovar`, corpo);
  confere([a, b, c3].filter((x) => x.d.ja === false).length === 1, "Três pedidos de aprovar, uma aprovação", [a.d, b.d, c3.d]);
  await statusNo(slug, narr, ["concluido"]);
  const n = sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:${narr}'`)[0].n;
  confere(n === 1, "A narração iniciou uma vez só", n);
  const ex = (await get(`/api/producoes/${slug}/estudio`)).execucao;
  confere(ex.status === "concluida", "A execução segue até a saída", ex);
  return { id, neymar };
}

async function fluxo_real() {
  console.log("\n[3b] O fluxo real do canal, publicado, de ponta a ponta no executor; bloqueio do Vini");
  const opcoes = await get("/api/opcoes");
  confere(opcoes.fluxos.some((f) => f.id === "canal" && f.publicada === 1), "O fluxo real já vem publicado como v1");
  const slug = (await post("/api/producoes", { tema: "teste fluxo real", fluxo: "canal", legenda: "caderno", duracao: 30, briefing: "Foco em dados do Brasil." })).d.slug;
  const pedidos = () => fs.readFileSync(path.join(caixa, "output", slug, ".pedidos_recebidos.txt"), "utf-8");
  const aprovar = async (no) => { const n = await statusNo(slug, no, ["aguardando"]); const e = (await get(`/api/producoes/${slug}/estudio`)).execucao.id; const r = await post(`/api/execucoes/${e}/aprovar`, { no, versao_id: n.versao.id }); confere(r.status === 200 && r.d.ja === false, `Aprovou ${no}`, r.d); return e; };
  const ex = await aprovar("ap_roteiro");
  confere(pedidos().includes("Duração alvo: 30 s") && pedidos().includes("Foco em dados do Brasil."), "O pedido leva o briefing e a duração alvo");
  await aprovar("ap_componentes");
  await aprovar("ap_cenas");
  const lib = await statusNo(slug, "narracao", ["aguardando_inicio"]);
  confere(lib.manual, "A narração espera o botão, como no fluxo fixo");
  await statusNo(slug, "aud_texto", ["concluido"]);
  const [l1, l2] = await Promise.all([post(`/api/execucoes/${ex}/liberar`, { no: "narracao" }), post(`/api/execucoes/${ex}/liberar`, { no: "narracao" })]);
  confere([l1, l2].filter((x) => x.d.ja === false).length === 1, "Iniciar duas vezes vira um início");
  await aprovar("ap_narracao");
  await statusNo(slug, "video", ["aguardando_inicio"]);
  await post(`/api/execucoes/${ex}/liberar`, { no: "video" });
  await aprovar("ap_video");
  await statusNo(slug, "thumb", ["aguardando_inicio"]);
  await post(`/api/execucoes/${ex}/liberar`, { no: "thumb" });
  await ate(async () => (await get(`/api/producoes/${slug}/estudio`)).execucao.status === "concluida", "fim do fluxo real");
  const lin = (await get(`/api/producoes/${slug}/estudio`));
  confere(lin.linhas.find((x) => x.no === "cenas_h").status === "ignorado" && lin.linhas.find((x) => x.no === "cenas_v").status === "concluido", "A condição escolhe Olise no vertical, sem acionar o Barcola", lin.linhas.find((x) => x.no === "cenas_h"));
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND status='falhou'`)[0].n === 0, "Sem falhas no fluxo real");
  const est = await get(`/api/producoes/${slug}`);
  confere(est.etapas.find((x) => x.id === "video").aprovada, "A aprovação fica presa à versão do vídeo");
  // Vini bloqueia: o fluxo não chega à narração
  const slug2 = "teste-vini-bloqueia";
  fs.mkdirSync(path.join(caixa, "output", slug2), { recursive: true });
  fs.writeFileSync(path.join(caixa, "output", slug2, ".vini_bloqueia"), "");
  fs.writeFileSync(path.join(caixa, "output", slug2, "notas.md"), "# Notas\nFato. Fonte: a.com\n");
  const ex2 = (await post(`/api/producoes/${slug2}/executar`, { fluxo: "canal" })).d.execucao;
  const ap = async (no) => { const n = await statusNo(slug2, no, ["aguardando"]); await post(`/api/execucoes/${ex2}/aprovar`, { no, versao_id: n.versao.id }); };
  await ap("ap_roteiro");
  const linhas2 = (await get(`/api/producoes/${slug2}/estudio`)).linhas.map((x) => x.no);  // o fluxo publicado não tem mais o nó se_sketch
  const semSketch = !linhas2.includes("se_sketch") && linhas2.includes("narracao");
  // Tolerado de propósito: neste projeto o nó de componentes pode não parar para aprovação (etapa que não se aplica); o que importa é conferido nas asserções abaixo.
  await ap("ap_componentes").catch(() => {});
  await ap("ap_cenas");
  await statusNo(slug2, "aud_texto", ["concluido"]);
  await ate(async () => (await get(`/api/producoes/${slug2}/estudio`)).execucao.status === "concluida", "bloqueio");
  const b = (await get(`/api/producoes/${slug2}/estudio`)).linhas;
  confere(b.find((x) => x.no === "narracao").status === "ignorado", "Com o parecer BLOQUEADO, a narração nem começa", b.find((x) => x.no === "narracao"));
  confere(semSketch, "O fluxo padrão não tem mais o nó se_sketch", linhas2);
  confere((await noDe(slug2, "pesquisa")).status !== "falhou", "Projeto existente executa pelo fluxo, reaproveitando o que já tem", (await noDe(slug2, "pesquisa")).nota);
}

async function paralelo() {
  console.log("\n[4] Grafo com ramos em paralelo; devolver a narração; só esse ramo pende");
  const { n, liga } = grafoBase();
  const g = { nos: [n("briefing", "entrada", "Briefing", 0, 1), n("p", "agente", "Pesquisa", 1, 1, { agente: "modric-pesquisador-tema", tarefa: "pesquisa" }), n("r", "agente", "Roteiro", 2, 1, { agente: "neymar-roteirista", tarefa: "roteiro" }), n("ar", "aprovacao", "Aprovar roteiro", 3, 1, { material: "roteiro" }),
    n("narr", "render", "Narração", 4, 0, { acao: "narracao" }), n("ilu", "agente", "Ilustração", 4, 2, { agente: "olise-diretor-arte", tarefa: "cenas" }), n("an", "aprovacao", "Aprovar narração", 5, 0, { material: "narracao" }), n("ac", "aprovacao", "Aprovar cenas", 5, 2, { material: "cenas" }),
    n("met", "agente", "Metadados", 4, 3, { agente: "mbappe-editor-metadados", tarefa: "metadados" }), n("j", "juncao", "Os dois aprovados", 6, 1), n("v", "render", "Render", 7, 1, { acao: "video" }), n("fim", "saida", "Fim", 8, 1)],
  arestas: [liga("briefing", "p"), liga("p", "r"), liga("r", "ar"), liga("ar", "narr"), liga("ar", "ilu"), liga("ar", "met"), liga("narr", "an"), liga("ilu", "ac"), liga("an", "j"), liga("ac", "j"), liga("met", "j"), liga("j", "v"), liga("v", "fim")] };
  const id = (await post("/api/fluxos", { nome: "Narracao e ilustracao em paralelo" })).d.id;
  g.arestas.find((a) => a.id === "ar->ilu").mapa = [{ saida: "roteiro", entrada: "direcao_viral" }];
  g.nos.push(n("rev", "agente", "Revisão (desativada)", 2, 3, { agente: "courtois-revisor-fatos", tarefa: "courtois" }));
  g.nos.find((x) => x.id === "rev").desativado = true;
  g.arestas.splice(g.arestas.findIndex((a) => a.id === "r->ar"), 1, liga("r", "rev"), liga("rev", "ar"));
  const r = await post(`/api/fluxos/${id}/salvar`, { grafo: g });
  confere(!r.d.problemas.some((p) => p.nivel === "erro"), "Grafo em paralelo valida", r.d.problemas);
  confere((await post(`/api/fluxos/${id}/publicar`, {})).status === 201, "Publicou");
  const slug = (await post("/api/producoes", { tema: "teste ramos paralelos", fluxo: id })).d.slug;
  const ar = await statusNo(slug, "ar", ["aguardando"]);
  const ex = (await get(`/api/producoes/${slug}/estudio`)).execucao.id;
  await post(`/api/execucoes/${ex}/aprovar`, { no: "ar", versao_id: ar.versao.id });
  confere((await noDe(slug, "rev")).status === "concluido" && sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:rev'`)[0].n === 0, "Nó desativado: o fluxo passa direto, sem rodar", (await noDe(slug, "rev")).nota);
  const inicio = sqlite(`SELECT etapa, iniciado_em FROM jobs WHERE slug='${slug}' AND (etapa LIKE '%:narr' OR etapa LIKE '%:ilu')`);
  confere(JSON.parse(sqlite(`SELECT spec FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:ilu'`)[0].spec).prompt.includes(`direcao_viral: output/${slug}/roteiro.txt (vem de Roteiro)`), "O campo mapeado chega ao agente");
  confere(inicio.length === 2, "Depois da aprovação do roteiro, narração e ilustração foram disparadas juntas", inicio);
  const an = await statusNo(slug, "an", ["aguardando"]), ac = await statusNo(slug, "ac", ["aguardando"]);
  confere((await noDe(slug, "v")).status === "pendente", "O render espera as duas aprovações");
  await post(`/api/execucoes/${ex}/aprovar`, { no: "ac", versao_id: ac.versao.id });
  await dormir(300);
  confere((await noDe(slug, "v")).status === "pendente", "Só uma aprovação: o render continua esperando");
  const versaoAc = (await noDe(slug, "ac")).versao.id;

  // Devolver a narração: só o ramo dela
  await pagina.goto(`${BASE}/estudio/${slug}`, { waitUntil: "networkidle2" });
  await sel(`[data-devolver="an"]`);
  await captura("13-paralelo");
  const nJobsIlu = sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:ilu'`)[0].n;
  const dv = await post(`/api/execucoes/${ex}/devolver`, { no: "an", texto: "O número está sendo lido errado", cena: 0, categoria: "Narração" });
  confere(dv.status === 201 && dv.d.jobs.length === 1, "O pedido de ajuste vai para o responsável", dv.d);
  const fb = sqlite(`SELECT cena, texto, status, no FROM feedback WHERE slug='${slug}' ORDER BY id DESC LIMIT 1`)[0];
  confere(fb.cena === 0 && fb.no === "an", "O comentário fica registrado com a cena e o nó", fb);
  await ate(async () => !(await get(`/api/producoes/${slug}`)).fila.length, "ajuste terminar");
  const anDepois = await statusNo(slug, "an", ["aguardando"]);
  confere(anDepois.versao.numero > an.versao.numero, "A narração volta a pedir aprovação, em versão nova", [an.versao, anDepois.versao]);
  const acDepois = await noDe(slug, "ac");
  confere(acDepois.status === "concluido" && acDepois.versao.id === versaoAc, "A aprovação da ilustração continua de pé", acDepois.status);
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:ilu'`)[0].n === nJobsIlu, "A ilustração não rodou de novo");
  confere((await noDe(slug, "v")).status === "pendente", "O render segue aguardando");
  await post(`/api/execucoes/${ex}/aprovar`, { no: "an", versao_id: anDepois.versao.id });
  await statusNo(slug, "v", ["concluido", "falhou"]);
  const fim = await noDe(slug, "v");
  confere(fim.status === "concluido", "Com as duas aprovações, o render roda", fim);
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug}' AND etapa LIKE '%:v'`)[0].n === 1, "O render rodou uma vez");

  // Falha e retomada sem duplicar
  const slug2 = (await post("/api/producoes", { tema: "teste falha no fluxo", fluxo: id })).d.slug;
  fs.writeFileSync(path.join(caixa, "output", slug2, ".falhar_neymar-roteirista"), "");
  const falhou = await statusNo(slug2, "r", ["falhou"]);
  confere(/Falha simulada/.test(falhou.nota || ""), "Falha do agente aparece no nó, com a mensagem", falhou.nota);
  fs.rmSync(path.join(caixa, "output", slug2, ".falhar_neymar-roteirista"));
  const ex2 = (await get(`/api/producoes/${slug2}/estudio`)).execucao.id;
  const n0 = sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug2}' AND etapa LIKE '%:r'`)[0].n;
  await Promise.all([post(`/api/execucoes/${ex2}/repetir`, { no: "r" }), post(`/api/execucoes/${ex2}/repetir`, { no: "r" })]);
  await statusNo(slug2, "ar", ["aguardando"]);
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug2}' AND etapa LIKE '%:r'`)[0].n === n0 + 1, "“Tentar de novo” duas vezes roda uma vez");
  confere(sqlite(`SELECT COUNT(*) n FROM jobs WHERE slug='${slug2}' AND etapa LIKE '%:p'`)[0].n === 1, "A pesquisa, que não dependia da falha, não rodou de novo");
  return id;
}

async function agentes_e_versoes() {
  console.log("\n[5] Duplicar agente, alterar, testar, atribuir a um nó; execução antiga fica com a original");
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });  // /agentes agora abre Ao vivo (PROG-003)
  await sel('[data-agente="neymar-roteirista"]');
  const n = await pagina.$$eval(".ag-item", (x) => x.length);
  confere(n === fs.readdirSync(path.join(caixa, ".claude", "agents")).length, "O catálogo mostra os agentes descobertos", n);
  await pagina.click('[data-agente="neymar-roteirista"]');
  await sel("#ag-duplicar");
  confere((await texto("#ag-usos")).includes("Canal"), "Mostra quais fluxos usam o agente", await texto("#ag-usos"));
  await captura("14-agente");
  await pagina.click("#ag-duplicar");
  const copia = "neymar-roteirista-copia";
  await sel(`.ag-item.ativo[data-agente="${copia}"]`);
  await pagina.waitForFunction(() => document.querySelector("#ag-titulo") && !document.querySelector("#ag-editar").dataset.ocupado, { timeout: 8000 });
  await dormir(300);
  const arq = path.join(caixa, ".claude", "agents", `${copia}.md`);
  confere(fs.existsSync(arq) && fs.readFileSync(arq, "utf-8").includes(`name: ${copia}`), "A cópia está no formato nativo em .claude/agents");
  await clicar("#ag-editar");
  await sel("#ag-instrucoes");
  await pagina.evaluate(() => { const e = document.querySelector("#ag-instrucoes"); e.value = "MARCA-DA-COPIA. Escreva o roteiro mais curto possível.\n" + e.value; });
  await pagina.click("#ag-salvar");
  await pagina.waitForFunction(() => document.querySelector("#ag-duplicar"), { timeout: 8000 });
  confere(fs.readFileSync(arq, "utf-8").includes("MARCA-DA-COPIA"), "Salvar escreve no arquivo do agente");
  const cp = await get(`/api/agentes/${copia}`);
  confere(cp.versao === 2, "Salvar criou a v2 no histórico", cp.versao);
  const ferr = await post(`/api/agentes/${copia}/salvar`, { descricao: cp.descricao, instrucoes: cp.instrucoes, ferramentas: ["Read", "Bash(rm -rf *)"], modelo: "sonnet", versao_vista: cp.versao });
  confere(ferr.status === 400, "Comando de shell novo como ferramenta é recusado", ferr.d);
  confere((await post(`/api/agentes/${copia}/salvar`, { descricao: cp.descricao, instrucoes: cp.instrucoes, ferramentas: ["Read"], modelo: "gpt-9", versao_vista: cp.versao })).status === 400, "Modelo indisponível é recusado");

  // Testar
  await sel("#teste-entrada");
  await pagina.type("#teste-entrada", "Tema de exemplo: jovens e amizade.");
  await clicar("#testar");
  await sel(".saida-teste", 30000);
  const saida = await texto(".saida-teste");
  confere(saida.includes("MARCA-DA-COPIA"), "O teste rodou com as instruções alteradas", saida.slice(0, 120));
  confere(!fs.existsSync(path.join(caixa, "output", "exemplo")), "O teste não toca em nenhum projeto");
  await captura("15-teste-agente");

  // Comparar e restaurar
  await sel("#comparar-agente");
  await clicar("#comparar-agente");
  await pagina.waitForFunction(() => document.querySelector("#ag-diff .entrou"), { timeout: 5000 });
  confere((await texto("#ag-diff .entrou")).includes("MARCA"), "Compara versões do agente");

  // Fluxo com 2 nós do mesmo tipo: trocar em um só
  const { n: no, liga } = grafoBase();
  const g = { nos: [no("briefing", "entrada", "Briefing", 0, 0), no("p", "agente", "Pesquisa", 1, 0, { agente: "modric-pesquisador-tema", tarefa: "pesquisa" }), no("r", "agente", "Roteiro", 2, 0, { agente: "neymar-roteirista", tarefa: "roteiro" }), no("ar", "aprovacao", "Aprovar", 3, 0, { material: "roteiro" }), no("m", "agente", "Metadados", 4, 0, { agente: "mbappe-editor-metadados", tarefa: "metadados" }), no("fim", "saida", "Fim", 5, 0)],
    arestas: [liga("briefing", "p"), liga("p", "r"), liga("r", "ar"), liga("ar", "m"), liga("m", "fim")] };
  const id = (await post("/api/fluxos", { nome: "Fluxo do teste de agente" })).d.id;
  await post(`/api/fluxos/${id}/salvar`, { grafo: g });
  await post(`/api/fluxos/${id}/publicar`, {});
  const antiga = (await post("/api/producoes", { tema: "execucao antiga", fluxo: id })).d.slug;
  await statusNo(antiga, "ar", ["aguardando"]);
  const specAntigo = JSON.parse(sqlite(`SELECT spec FROM jobs WHERE slug='${antiga}' AND etapa LIKE '%:r'`)[0].spec);

  // Atribui a cópia a um único nó, pela interface
  await pagina.goto(`${BASE}/fluxos/${id}`, { waitUntil: "networkidle2" });
  await sel('.fx-no[data-no="r"]');
  await pagina.click('.fx-no[data-no="r"]');
  await definir("#no-agente", copia);
  await pagina.waitForFunction(() => document.querySelector("#fx-salvo")?.innerText === "Rascunho salvo", { timeout: 6000 });
  await clicar("#fx-publicar");
  await pagina.waitForFunction(() => document.querySelector("#fx-publicada")?.innerText.includes("v2"), { timeout: 8000 });
  const nova = (await post("/api/producoes", { tema: "execucao nova", fluxo: id })).d.slug;
  const rNova = await statusNo(nova, "ar", ["aguardando"]);
  const jobs = sqlite(`SELECT spec FROM jobs WHERE slug='${nova}' AND etapa LIKE '%:r'`);
  const specNovo = JSON.parse(jobs[0].spec);
  confere(specNovo.agente === copia && specNovo.sistema.versao === cp.versao && specNovo.sistema.corpo.includes("MARCA-DA-COPIA"), "A nova execução registra a cópia e a versão dela", { a: specNovo.agente, v: specNovo.sistema.versao });
  const vis = await noDe(nova, "r");
  confere(vis.agente === copia && vis.agente_versao === cp.versao, "O Estúdio mostra agente e versão do nó", [vis.agente, vis.agente_versao]);
  const mNova = await noDe(nova, "ar");
  await post(`/api/execucoes/${(await get(`/api/producoes/${nova}/estudio`)).execucao.id}/aprovar`, { no: "ar", versao_id: mNova.versao.id });
  await statusNo(nova, "m", ["concluido"]);
  confere(JSON.parse(sqlite(`SELECT spec FROM jobs WHERE slug='${nova}' AND etapa LIKE '%:m'`)[0].spec).agente === "mbappe-editor-metadados", "Os outros nós continuam com os agentes deles");

  // A execução antiga mantém a configuração original
  const vAntiga = await get(`/api/producoes/${antiga}/estudio`);
  confere(vAntiga.execucao.fluxo_numero === 1 && vAntiga.execucao.fluxo_atual === 2, "A execução anterior continua presa à v1 do fluxo", vAntiga.execucao);
  const rAntigo = vAntiga.linhas.find((x) => x.no === "r");
  confere(rAntigo.agente === "neymar-roteirista" && !specAntigo.sistema.corpo.includes("MARCA-DA-COPIA"), "A execução anterior manteve o agente original", rAntigo.agente);
  // Editar o agente original durante a execução anterior não muda o que ela usa
  const neymar = await get("/api/agentes/mbappe-editor-metadados");
  await post("/api/agentes/mbappe-editor-metadados/salvar", { descricao: neymar.descricao, instrucoes: "ALTERADO-DEPOIS\n" + neymar.instrucoes, ferramentas: neymar.ferramentas, modelo: neymar.modelo, versao_vista: neymar.versao });
  const apAntiga = vAntiga.linhas.find((x) => x.no === "ar");
  await post(`/api/execucoes/${vAntiga.execucao.id}/aprovar`, { no: "ar", versao_id: apAntiga.versao.id });
  await statusNo(antiga, "m", ["concluido"]);
  const specM = JSON.parse(sqlite(`SELECT spec FROM jobs WHERE slug='${antiga}' AND etapa LIKE '%:m'`)[0].spec);
  confere(!specM.sistema.corpo.includes("ALTERADO-DEPOIS") && specM.sistema.versao === neymar.versao, "Agente editado depois: a execução em andamento usa a foto de quando começou", specM.sistema.versao);
  // Restaurar e desativar
  const rest = await post(`/api/agentes/${copia}/restaurar`, { numero: 1 });
  confere(rest.d.versao === 3 && !fs.readFileSync(arq, "utf-8").includes("MARCA-DA-COPIA"), "Restaurar volta o conteúdo no arquivo, como versão nova", rest.d.versao);
  await pagina.goto(`${BASE}/agentes/${copia}`, { waitUntil: "networkidle2" });
  await clicar("#ag-ativar");
  await sel("#confirmar-desativar");
  confere((await texto("#confirmar-desativar")).includes("Fluxo do teste de agente"), "Antes de desativar, mostra quem usa");
  await clicar("#desativar-sim");
  await pagina.waitForFunction(() => document.querySelector("#ag-ativar")?.innerText.includes("Reativar"), { timeout: 8000 });
  confere(!fs.existsSync(arq) && fs.existsSync(path.join(caixa, ".claude", "agents_desativados", `${copia}.md`)), "Desativar tira o arquivo de .claude/agents");
  confere((await post(`/api/fluxos/${id}/publicar`, {})).status === 409 || (await get(`/api/fluxos/${id}`)).problemas.some((p) => /desativado/.test(p.texto)), "O fluxo que usa o agente desativado aponta o erro");
  const sec = await fetch(`${BASE}/.env`);
  confere((await sec.text()).includes("<!doctype html>") === false || sec.status === 404, "O navegador não acessa o .env", sec.status);
  const trilha = await fetch(`${BASE}/api/producoes/%2E%2E/corte/galeria`);
  confere(trilha.status === 400 || trilha.status === 404, "Slug com .. é recusado", trilha.status);
  const cat = JSON.stringify(await get("/api/agentes"));
  confere(!/ANTHROPIC_API_KEY=|sk-ant/.test(cat), "Nenhum segredo no catálogo");
}

async function ajuste_na_narracao() {
  console.log("\n[6] Ajuste na narração: assets aprovados e legenda manual ficam; informa a ressincronização");
  const e = await get(`/api/producoes/${SLUG}/corte`);
  const seg = e.compilado.segmentos[2];
  const legAntes = e.estado.legendas.itens.find((x) => x.texto === "Legenda feita à mão");
  const midiaAntes = JSON.stringify(e.estado.cenas.find((x) => x.id === seg.cena).midia);
  const comp = await get(`/api/producoes/${SLUG}/material/componentes`);
  const itens = comp.versao ? comp.dados.grupos.flatMap((g) => g.itens) : [];
  for (const it of itens.slice(0, 2)) await post(`/api/producoes/${SLUG}/item`, { material: "componentes", versao_id: comp.versao.id, item: it.item, decisao: "aprovado" });
  const aprovadosAntes = JSON.stringify(sqlite(`SELECT sha FROM itens WHERE slug='${SLUG}' AND material='componentes' ORDER BY sha`));

  fs.writeFileSync(path.join(pastaProd, ".dur_narracao"), "9.5");  // a nova tomada é mais longa do que a cena
  const narr = await get(`/api/producoes/${SLUG}/material/narracao`);
  const anot = await post(`/api/producoes/${SLUG}/feedback`, { material: "narracao", versao_id: narr.versao.id, texto: "Ler o número devagar", item: `cena_${seg.i}`, cena: seg.i, categoria: "Ritmo" });
  confere(anot.status === 201, "Comentário no trecho da narração", anot.d.erro);
  const env = await post(`/api/producoes/${SLUG}/enviar_ajustes`, { material: "narracao", versao_id: narr.versao.id });
  confere(env.status === 201, "O ajuste foi enviado", env.d);
  await ate(async () => { const k = await get(`/api/producoes/${SLUG}`); return !k.fila.length && k.etapas.find((x) => x.id === "narracao").versao > narr.versao.numero; }, "nova narração");
  const pedido = fs.readFileSync(path.join(pastaProd, ".pedidos_recebidos.txt"), "utf-8");
  confere(pedido.includes("Ler o número devagar") && pedido.includes(`cena ${seg.i + 1}`), "O pedido chega ao responsável com a cena");

  await pagina.goto(`${BASE}/editor/${SLUG}`, { waitUntil: "networkidle2" });
  await sel("#conflitos");
  const texConf = await texto("#conflitos");
  confere(texConf.includes("exige ressincronizar"), "O editor informa que a nova duração exige ressincronização", texConf);
  await captura("16-conflito-narracao");
  const v1 = await get(`/api/producoes/${SLUG}/corte`);
  const it1 = v1.estado.narracao.itens.find((x) => x.cena === seg.cena);
  confere(Math.abs(it1.dur - 9.5) > 0.5, "Até escolher, o corte continua com a fala antiga", it1.dur);
  confere(v1.conflitos.filter((x) => x.tipo === "narracao").length === 1, "Só a fala pedida mudou", v1.conflitos.map((x) => x.id));
  await pagina.evaluate(() => [...document.querySelectorAll("[data-conflito]")].forEach((b) => { b.checked = b.dataset.conflito.startsWith("narracao:"); }));
  await clicar("#aplicar-conflitos");
  await pagina.waitForFunction(() => !document.querySelector("#conflitos"), { timeout: 8000 });
  const v2 = await get(`/api/producoes/${SLUG}/corte`);
  const leg2 = v2.estado.legendas.itens.find((x) => x.texto === "Legenda feita à mão");
  confere(leg2 && leg2.y === legAntes.y && leg2.manual, "A legenda manual sobrevive ao reprocessamento");
  confere(JSON.stringify(v2.estado.cenas.find((x) => x.id === seg.cena).midia) === midiaAntes, "O asset trocado sobrevive");
  confere(Math.abs(v2.estado.narracao.itens.find((x) => x.cena === seg.cena).dur - 9.5) < 0.01, "A fala nova entrou");
  confere(v2.compilado.avisos.some((a) => a.tipo === "corte_fala" && a.cena === seg.cena && a.segundos > 5), "O corte de fala fica sinalizado para resolver", v2.compilado.avisos);
  confere(JSON.stringify(sqlite(`SELECT sha FROM itens WHERE slug='${SLUG}' AND material='componentes' ORDER BY sha`)) === aprovadosAntes, "Os assets aprovados continuam aprovados");
  const outras = v2.estado.narracao.itens.filter((x) => x.cena !== seg.cena);
  confere(outras.every((x) => x.sha === e.estado.narracao.itens.find((k) => k.id === x.id).sha), "As outras falas não mudaram");
  // Reordenar pela linha do tempo
  const a = await (await pagina.$(`.clipe[data-cena="${v2.compilado.segmentos[0].cena}"]`)).boundingBox();
  await pagina.mouse.move(a.x + a.width / 2, a.y + 28); await pagina.mouse.down(); await pagina.mouse.move(a.x + a.width * 8, a.y + 28, { steps: 8 }); await pagina.mouse.up();
  await pagina.waitForFunction((id) => { const b = document.querySelector(`.clipe[data-cena="${id}"]`); return b && parseFloat(b.style.left) > 1; }, { timeout: 8000 }, v2.compilado.segmentos[0].cena);
  const v3 = await get(`/api/producoes/${SLUG}/corte`);
  confere(v3.estado.cenas[0].id !== v2.estado.cenas[0].id, "Arrastar reordena as cenas");
  const rel = (v) => v.compilado.legendas.find((l) => l.id === leg2.id).f0 - v.compilado.segmentos.find((k) => k.cena === seg.cena).f0;
  confere(v3.compilado.legendas.find((l) => l.id === leg2.id).f0 !== v2.compilado.legendas.find((l) => l.id === leg2.id).f0 && rel(v3) === rel(v2), "A legenda acompanha a cena reordenada", [rel(v2), rel(v3)]);
  // Volume
  await pagina.click(".bloco-audio");
  await sel("#narr-volume");
  await definir("#narr-volume", "-6");
  await salvo();
  const v4 = await get(`/api/producoes/${SLUG}/corte`);
  confere(Math.abs(v4.compilado.audio[0].ganho - 0.501) < 0.01, "O volume da narração entra na compilação", v4.compilado.audio[0].ganho);
  await pagina.waitForFunction(() => document.querySelector("#ed-situacao")?.innerText.includes("alterado"), { timeout: 5000 });
  await captura("17-editor-final");
}

async function so_mp4() {
  console.log("\n[7] Entrada antiga só com MP4: só o que é viável, e diz o que falta");
  const pasta = path.join(caixa, "output", "so-mp4");
  fs.mkdirSync(pasta);
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=1080x1920:rate=30:duration=4", "-f", "lavfi", "-i", "sine=frequency=330:duration=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", path.join(pasta, "video.mp4")]);
  await pagina.goto(`${BASE}/editor/so-mp4`, { waitUntil: "networkidle2" });
  await sel("#so-mp4");
  confere((await texto("#so-mp4")).includes("cenas.json"), "Diz o material necessário para o resto");
  await pagina.click(".clipe");
  await sel("#cena-duracao");
  confere((await texto("#ed-inspetor")).includes("exige o projeto por cenas"), "Trocar asset fica indisponível, com o motivo");
  confere(!(await pagina.$("#trocar-asset")), "Não há botão de troca que não funcione");
  const v = await get("/api/producoes/so-mp4/corte");
  const novo = JSON.parse(JSON.stringify(v.estado));
  novo.cenas[0].out = 3;
  novo.legendas.itens.push({ id: "le-x", cena: null, ini: 0.5, fim: 2, texto: "Só MP4", x: 540, y: 900, estilo: "cartao", manual: true });
  const s = await post("/api/producoes/so-mp4/corte_salvar", { estado: novo, rev: v.estado.rev });
  confere(s.status === 200, "Apara e legenda funcionam no MP4 antigo", s.d.erro);
  await post("/api/producoes/so-mp4/corte_exportar", { confirmado: true });
  const fim = await ate(async () => { const r = sqlite(`SELECT status, erro FROM jobs WHERE slug='so-mp4' AND etapa='video' ORDER BY id DESC LIMIT 1`)[0]; return r && !["rodando", "fila"].includes(r.status) ? r : null; }, "export so-mp4", 180000);
  confere(fim.status === "ok", "Exporta o MP4 aparado", fim);
  const d = Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", path.join(pasta, "video.mp4")], { encoding: "utf-8" }));
  confere(Math.abs(d - 3) < 0.1, "O MP4 ficou com 3 s", d);
}

async function revisao_edita() {
  console.log("\n[8] Revisão: editar fala e direção, trocar arquivo, tomadas, reinício do servidor");
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=roteiro`, { waitUntil: "networkidle2" });
  await pagina.waitForFunction(() => [...document.querySelectorAll(".aba")].some((a) => a.innerText === "Por cena"), { timeout: 10000 });
  await pagina.evaluate(() => [...document.querySelectorAll(".aba")].find((a) => a.innerText === "Por cena").click());
  await sel('[data-editar="fala:1"]');
  await pagina.click('[data-editar="direcao:1"]');
  await sel('[data-caixa="direcao:1"]');
  await dormir(2500);  // o polling não pode apagar a edição
  confere(!!(await pagina.$('[data-caixa="direcao:1"]')), "O polling não apaga o campo em edição");
  await pagina.type('[data-caixa="direcao:1"]', "Mais espaço em branco. ");
  await pagina.click('[data-salvar="direcao:1"]');
  await dormir(500);
  confere(fs.readFileSync(path.join(pastaProd, "direcao_viral.md"), "utf-8").includes("Cena 2:"), "A direção visual vai para o direcao_viral.md");
  await captura("18-revisao-roteiro");
  await pagina.goto(`${BASE}/producao/${SLUG}?etapa=componentes`, { waitUntil: "networkidle2" });
  await sel("#thumb-bloco");
  confere((await texto("#thumb-bloco")).includes("thumbnail.jpg"), "A galeria mostra a thumbnail");
  await captura("19-revisao-assets");
  await pagina.click("#thumb-aprovar");
  await dormir(600);
  confere((await get(`/api/producoes/${SLUG}/thumbnail`)).thumbnail.decisao === "aprovado", "Aprova a thumbnail individualmente");
  const comp = await get(`/api/producoes/${SLUG}/material/componentes`);
  const item = comp.dados.grupos.flatMap((g) => g.itens)[0];
  const outros = comp.dados.grupos.flatMap((g) => g.itens).filter((x) => x.item !== item.item && x.decisao === "aprovado").map((x) => x.item);
  const png = path.join(os.tmpdir(), `corte-comp-${process.pid}.png`);
  execFileSync(PY, ["-c", `from PIL import Image;Image.new('RGB',(300,300),(255,196,0)).save(r'${png}')`]);
  const up = await fetch(`${BASE}/api/producoes/${SLUG}/enviar/componente?item=${item.item}`, { method: "POST", body: fs.readFileSync(png) });
  confere(up.status === 201, "Substitui um componente por arquivo local");
  const naoImagem = await fetch(`${BASE}/api/producoes/${SLUG}/enviar/componente?item=${item.item}`, { method: "POST", body: Buffer.from("isto não é imagem") });
  confere(naoImagem.status === 400, "Arquivo que não é imagem é recusado");
  const comp2 = await get(`/api/producoes/${SLUG}/material/componentes`);
  const todos = comp2.dados.grupos.flatMap((g) => g.itens);
  confere(todos.filter((x) => outros.includes(x.item)).every((x) => x.decisao === "aprovado") && todos.find((x) => x.item === item.item).decisao !== "aprovado", "Só o substituído volta para revisão");
  const tom = await get(`/api/producoes/${SLUG}/tomadas?cena=2`);
  confere(tom.tomadas.length >= 2, "Lista as tomadas existentes da fala", tom.tomadas.length);
  const antiga = tom.tomadas.find((t) => !t.atual);
  const us = await post(`/api/producoes/${SLUG}/usar_tomada`, { cena: 2, sha: antiga.sha });
  confere(us.status === 200 && (await get(`/api/producoes/${SLUG}/tomadas?cena=2`)).tomadas.find((t) => t.sha === antiga.sha).atual, "Volta uma tomada antiga");
  // Reiniciar o servidor: nada se perde
  const fim = new Promise((r) => servidor.once("exit", r));
  servidor.kill();
  await fim;
  subir();
  await esperarServidor();
  const v = await get(`/api/producoes/${SLUG}/corte`);
  confere(v.estado.legendas.itens.some((x) => x.texto === "Legenda feita à mão"), "O corte sobrevive a reiniciar o servidor");
  confere(!errosJs.length, "Nenhum erro de JavaScript nas telas", errosJs.slice(0, 5));
}

try {
  subir();
  await esperarServidor();
  navegador = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--autoplay-policy=no-user-gesture-required"], defaultViewport: { width: 1600, height: 1000 } });
  pagina = await navegador.newPage();
  pagina.on("pageerror", (e) => errosJs.push(e.message));
  await uma_produção_antiga_abre();
  await editar_e_exportar();
  await aprovacao_no_fluxo();
  await fluxo_real();
  await paralelo();
  await agentes_e_versoes();
  await ajuste_na_narracao();
  await so_mp4();
  await revisao_edita();
} catch (e) {
  falhas.push(`exceção: ${e.message}`);
  console.log(`  FALHOU  ${e.stack}`);
  if (pagina) await captura("erro").catch(() => {});
} finally {
  if (navegador) await navegador.close().catch(() => {});
  if (servidor) servidor.kill();
  await dormir(500);
  fs.rmSync(caixa, { recursive: true, force: true });
}
console.log(`\n${passou} verificações ok, ${falhas.length} falhas. Capturas em ${CAPTURAS}`);
if (falhas.length) { console.log(falhas.map((f) => ` - ${f}`).join("\n")); process.exit(1); }
