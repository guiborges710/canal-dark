// PROG-024b (+ seletor de mês): tela de Finanças do app (ecossistema/app/index.html), Chrome headless, abrindo por file:// (sem servidor).
// Usa só DADOS INVENTADOS (fixture montada aqui, em cópia descartável do app). Com --real, roda UMA vez com ecossistema/app/dados/
// (gerado a partir dos CSV reais) e salva capturas em ecossistema/app/dados/capturas/: não imprime nenhum valor.
// Uso: node estudio/testes/e2e_financas.mjs [--real] [pasta para capturas dos cenários inventados]
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(AQUI, "..", "..");
const require = createRequire(path.join(REPO, "render", "package.json"));
const puppeteer = require("puppeteer-core");
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PY = path.join(REPO, ".venv", "Scripts", "python.exe");
const APP = path.join(REPO, "ecossistema", "app");
const REAL = process.argv.includes("--real");
const CAPT = process.argv.slice(2).find((a) => !a.startsWith("--")) || fs.mkdtempSync(path.join(os.tmpdir(), "financas-capturas-"));
fs.mkdirSync(CAPT, { recursive: true });

let passou = 0;
const falhas = [];
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
function confere(cond, nome, extra) { if (cond) { passou++; console.log(`  ok  ${nome}`); } else { falhas.push(nome); console.log(`  FALHOU  ${nome}${extra !== undefined ? ` -> ${JSON.stringify(extra).slice(0, 300)}` : ""}`); } }

/* ---------- fixture inventada (centavos; datas relativas a hoje) ---------- */
const iso = (d) => { const x = new Date(); x.setHours(12, 0, 0, 0); x.setDate(x.getDate() + d); return `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, "0")}-${String(x.getDate()).padStart(2, "0")}`; };
const agora = (dd = 0) => `${iso(dd)}T09:30:00`;
const mesAtual = () => iso(0).slice(0, 7);
const mesesAtras = (n) => { const x = new Date(); x.setDate(1); x.setMonth(x.getMonth() - n); return `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, "0")}`; };
const MARCA = { saldo: 987654, recebido: 1234567, gasto: 765432, apagar: 111111 }; // números "assinatura" para provar o ocultar
function base() {
  const serie = [5, 4, 3, 2, 1, 0].map((n, i) => ({ mes: mesesAtras(n), recebido: 900000 + i * 40000, previsto: n === 0 ? 50000 : 0, gasto_pago: 500000 + i * 30000, gasto_a_pagar: n === 0 ? MARCA.apagar : 0 }));
  serie[5].recebido = MARCA.recebido; serie[5].gasto_pago = MARCA.gasto;
  return {
    gerado_em: agora(0), moeda: "BRL", unidade: "centavos", mes_atual: mesAtual(),
    saldos: {
      contas: [
        { conta: "Banco Alfa", data: iso(-1), saldo: MARCA.saldo, observacao: "saldo do app", nao_confirmado: false, historico: false, idade_dias: 1 },
        { conta: "Banco Beta", data: iso(-2), saldo: 22222, observacao: "NÃO CONFIRMADO", nao_confirmado: true, historico: false, idade_dias: 2 },
      ],
      disponivel: MARCA.saldo, contas_fora_do_disponivel: ["Banco Beta"], observacao: "Saldo bancario informado; nao e o resultado das movimentacoes.",
    },
    recebido: { mes: MARCA.recebido, previsto_mes: 50000, total_6m: 6000000, previsto_6m: 50000 },
    gastos: { pagos_mes: MARCA.gasto, a_pagar_mes: MARCA.apagar, pagos_6m: 3000000, a_pagar_6m: MARCA.apagar },
    serie_mensal: serie,
    receitas_x_gastos: { mes: mesAtual(), receitas: MARCA.recebido, gastos: MARCA.gasto },
    categorias: [["moradia", 300000, 39.2], ["mercado", 200000, 26.1], ["contas", 100000, 13.1], ["lazer", 80000, 10.4], ["saude", 40000, 5.2], ["transporte", 20000, 2.6], ["assinaturas", 15000, 2], ["educacao", 6000, 0.8], ["xpto estranha", 4432, 0.6]]
      .map(([categoria, valor, percentual]) => ({ categoria, valor, percentual })),
    vencimentos: [
      { data: iso(2), descricao: "Internet ficticia", categoria: "contas", valor: 11111, dias_restantes: 2, atrasado: false, status: "a pagar" },
      { data: iso(20), descricao: "Seguro ficticio", categoria: "outros", valor: 55555, dias_restantes: 20, atrasado: false, status: "a pagar" },
    ],
    movimentos_recentes: [
      { linha_csv: 2, data: iso(-1), tipo: "gasto", categoria: "mercado", descricao: "Mercado ficticio", valor: 25050, status: "pago" },
      { linha_csv: 3, data: iso(-2), tipo: "recebido", categoria: "salario", descricao: "Salario ficticio", valor: 300000, status: "pago" },
      { linha_csv: 4, data: iso(5), tipo: "recebido", categoria: "freelance", descricao: "Freela ficticio", valor: 50000, status: "a receber" },
      { linha_csv: 5, data: iso(2), tipo: "gasto", categoria: "contas", descricao: "Internet ficticia", valor: 11111, status: "a pagar" },
    ],
    alertas: [{ tipo: "saldo_nao_confirmado", mensagem: "Conta 'Banco Beta' sem saldo confirmado", origem: "saldos.csv" }, { tipo: "pendencia_aberta", mensagem: "Item ficticio", origem: "pendencias.md" }],
    pendencias: { abertas: ["Item ficticio, confirmar R$ 123,45 com o banco"], resolvidas: 2, arquivo_ausente: false },
    fonte: { arquivos: { "movimentos.csv": agora(0), "saldos.csv": agora(0), "transferencias.csv": null, "pendencias.md": agora(0) }, contagens: { movimentos: 9, contas: 2, vencimentos: 2 } },
  };
}
const CEN = {
  normal: (d) => d,
  atrasado: (d) => { d.vencimentos = [{ data: iso(-5), descricao: "Luz ficticia", categoria: "contas", valor: 33333, dias_restantes: 999, atrasado: false, status: "a pagar" }, { data: iso(0), descricao: "Agua ficticia", categoria: "contas", valor: 4444, dias_restantes: -42, atrasado: true, status: "vencido" }, ...d.vencimentos]; return d; },
  divergente: (d) => { d.alertas.unshift({ tipo: "saldo_divergente", mensagem: "Conta 'Banco Alfa': saldo do extrato difere do saldo informado (diferenca de 54321 centavos)", origem: "saldos.csv" }, { tipo: "pago_sem_lancamento", mensagem: "'Boleto ficticio' diz que foi pago, mas segue 'a pagar'", origem: "movimentos.csv" }, { tipo: "linha_invalida", mensagem: "movimentos.csv linha 7 ignorada: valor invalido", origem: "movimentos.csv" }); d.saldos.contas[0].observacao = "extrato: 1234.56"; return d; },
  sem_vencimentos: (d) => { d.vencimentos = []; d.gastos.a_pagar_mes = 0; d.gastos.a_pagar_6m = 0; d.serie_mensal[5].gasto_a_pagar = 0; return d; },
  velho: (d) => { d.gerado_em = agora(-5); return d; },
  vazio: () => ({
    gerado_em: agora(0), moeda: "BRL", unidade: "centavos", mes_atual: mesAtual(),
    saldos: { contas: [], disponivel: 0, contas_fora_do_disponivel: [], observacao: "" }, recebido: { mes: 0, previsto_mes: 0, total_6m: 0, previsto_6m: 0 },
    gastos: { pagos_mes: 0, a_pagar_mes: 0, pagos_6m: 0, a_pagar_6m: 0 },
    serie_mensal: [5, 4, 3, 2, 1, 0].map((n) => ({ mes: mesesAtras(n), recebido: 0, previsto: 0, gasto_pago: 0, gasto_a_pagar: 0 })),
    receitas_x_gastos: { mes: mesAtual(), receitas: 0, gastos: 0 }, categorias: [], vencimentos: [], movimentos_recentes: [], alertas: [],
    pendencias: { abertas: [], resolvidas: 0, arquivo_ausente: false },
    fonte: { arquivos: { "movimentos.csv": agora(0), "saldos.csv": agora(0), "transferencias.csv": null, "pendencias.md": null }, contagens: { movimentos: 0, contas: 0, vencimentos: 0 } },
  }),
};
/* ---------- bloco `meses` (seletor de mês), tudo inventado ---------- */
const NOMES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
const longo = (m) => `${NOMES[+m.slice(5, 7) - 1]} ${m.slice(0, 4)}`;
const ROT = "Resultado das movimentacoes do mes (recebido menos gasto pago); nao e saldo bancario.";
const mesFix = (mes, o = {}) => ({ mes, recebido: o.rec || 0, previsto: o.prev || 0, gasto_pago: o.pago || 0, gasto_a_pagar: o.apagar || 0, saldo_do_mes: (o.rec || 0) - (o.pago || 0), saldo_do_mes_rotulo: ROT, categorias: o.cats || [], movimentos: o.movs || [], vencimentos: o.venc || [] });
const PASSADO = { rec: 777777, desc: "Salario antigo ficticio" };
function comMeses(d, { lista, atualVazio = false, atual } = {}) {
  const ls = lista || [7, 6, 5, 4, 3, 2, 1, 0].map(mesesAtras);
  const ma = atual || d.mes_atual;
  d.mes_atual = ma; d.receitas_x_gastos.mes = ma;
  d.meses_disponiveis = ls; d.meses = {};
  ls.forEach((m) => { d.meses[m] = mesFix(m); });
  if (!atualVazio) {
    d.meses[ma] = mesFix(ma, { rec: MARCA.recebido, prev: 50000, pago: MARCA.gasto, apagar: MARCA.apagar, cats: d.categorias, movs: d.movimentos_recentes.slice().reverse(), venc: d.vencimentos });
  } else { d.recebido = { mes: 0, previsto_mes: 0, total_6m: 0, previsto_6m: 0 }; d.gastos = { pagos_mes: 0, a_pagar_mes: 0, pagos_6m: 0, a_pagar_6m: 0 }; d.receitas_x_gastos.receitas = 0; d.receitas_x_gastos.gastos = 0; d.categorias = []; d.vencimentos = []; d.movimentos_recentes = []; }
  const p1 = ls[ls.indexOf(ma) - 1];
  if (p1) d.meses[p1] = mesFix(p1, { rec: PASSADO.rec, movs: [{ data: `${p1}-05`, tipo: "recebido", categoria: "salario", descricao: PASSADO.desc, valor: PASSADO.rec, status: "pago" }] });
  const p2 = ls[ls.indexOf(ma) - 2];
  if (p2) d.meses[p2] = mesFix(p2, { pago: 8500, cats: [{ categoria: "mercado", valor: 8500, percentual: 100 }], movs: Array.from({ length: 85 }, (_, i) => ({ data: `${p2}-${String(1 + (i % 28)).padStart(2, "0")}`, tipo: "gasto", categoria: "mercado", descricao: `Compra ${i + 1} ficticia`, valor: 100, status: "pago" })) });
  return d;
}
CEN.meses = (d) => comMeses(d);
CEN.mes_vazio = (d) => comMeses(d, { atualVazio: true });
CEN.virada = (d) => { d.gerado_em = "2026-01-04T09:30:00"; return comMeses(d, { lista: ["2025-11", "2025-12", "2026-01"], atual: "2026-01" }); };
const emJs = (d) => `window.FINANCAS = ${JSON.stringify(d, null, 2)};\n`;

/* ---------- cópia descartável do app ---------- */
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "financas-app-"));
for (const f of fs.readdirSync(APP)) if (f !== "dados" && f !== "testes" && fs.statSync(path.join(APP, f)).isFile()) fs.copyFileSync(path.join(APP, f), path.join(tmp, f));
fs.mkdirSync(path.join(tmp, "dados"));
const DADOS = path.join(tmp, "dados", "financas.js");
const url = (q = "") => pathToFileURL(path.join(tmp, "index.html")).href + q;

let nav, pg, errosJs = [];
async function abrir(largura, q = "", { toque = false, tema } = {}) {
  if (pg) await pg.close();
  pg = await nav.newPage();
  errosJs = [];
  pg.on("pageerror", (e) => errosJs.push(String(e.message || e)));
  pg.on("console", (m) => { if (m.type() === "error" && !/Failed to load resource/.test(m.text())) errosJs.push(m.text()); });
  await pg.setViewport({ width: largura, height: largura < 600 ? 844 : 900, deviceScaleFactor: 1, isMobile: toque, hasTouch: toque });
  await pg.evaluateOnNewDocument(() => { try { if (!sessionStorage.getItem("_t")) { localStorage.removeItem("ce_h_fin_mes"); sessionStorage.setItem("_t", "1"); } } catch (e) {} });
  if (tema) await pg.evaluateOnNewDocument((t) => { try { localStorage.setItem("ce_h_tema", t); } catch (e) {} }, tema);
  await pg.goto(url(q), { waitUntil: "load" });
  await pg.waitForFunction(() => !document.querySelector("[aria-busy=true]"), { timeout: 5000 }).catch(() => {});
  await dormir(250);
}
const texto = () => pg.evaluate(() => document.body.innerText);
const html = () => pg.evaluate(() => document.getElementById("app").innerHTML);
const overflow = () => pg.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
const cap = (n) => pg.screenshot({ path: path.join(CAPT, `${n}.png`), fullPage: true });

async function cenario(nome, fazer, { esperaErroJs = false } = {}) {
  console.log(`\n== ${nome}`);
  fs.writeFileSync(DADOS, emJs(CEN[nome](base())));
  for (const L of [1440, 390]) {
    await abrir(L);
    confere(!errosJs.length || esperaErroJs, `${nome} ${L}px: sem erro de JS`, errosJs);
    confere((await overflow()) <= 0, `${nome} ${L}px: sem rolagem lateral`, await overflow());
    if (nome === "normal") confere(await pg.evaluate(() => getComputedStyle(document.querySelector(".nav-dica")).display !== "none") === (L === 390), `${nome} ${L}px: dica de rolagem dos grupos no celular`);
    if (L === 1440) await fazer();
    await cap(`${nome}_${L}`);
  }
}

async function principal() {
  nav = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox", "--allow-file-access-from-files"] });
  try {
    await cenario("normal", async () => {
      const t = await texto();
      const idx = fs.readFileSync(path.join(tmp, "index.html"), "utf8");
      confere(!/ecossistema123|type="password"|localStorage\.getItem\("ecossistema_auth"\)/.test(idx), "normal: index.html é a Finanças, sem login nem senha/valores fixos no código");
      confere(/financas\.js/.test(idx) && !/R\$\s*\d/.test(idx), "normal: index.html carrega financas.js e não tem valor em reais fixo");
      for (const h of ["Alertas", "Últimos 6 meses", "Receitas e gastos", "Contas", "Gastos por categoria", "Vencimentos", "Movimentos recentes", "Fontes dos dados"]) confere(t.includes(h), `normal: seção "${h}"`);
      confere(t.includes("12.345,67"), "normal: recebido do mês formatado em reais");
      confere(t.includes("Lido hoje"), "normal: selo diz Lido hoje (idade calculada de gerado_em)");
      confere(/Parcial: 1 conta fora do total/.test(t), "normal: aviso de total parcial");
      confere(/Recebido/.test(t) && /Pago/.test(t) && /A receber/.test(t) && /A pagar/.test(t), "normal: movimentos com tipo e status (recebido, gasto; pago, a pagar, a receber)");
      await pg.evaluate(() => { document.documentElement.dataset.tema = "claro"; });
      const vermelhoClaro = await pg.$eval(".mv-v.neg", (e) => getComputedStyle(e).color);
      confere(vermelhoClaro === "rgb(198, 40, 40)", "normal: gastos aparecem em vermelho no tema claro", vermelhoClaro);
      await pg.evaluate(() => { document.documentElement.dataset.tema = "escuro"; });
      const vermelhoEscuro = await pg.$eval(".mv-v.neg", (e) => getComputedStyle(e).color);
      confere(vermelhoEscuro === "rgb(255, 107, 99)", "normal: gastos aparecem em vermelho suave no tema escuro", vermelhoEscuro);
      await pg.evaluate(() => { document.documentElement.dataset.tema = "claro"; });
      confere(/Vence em 2 dias/.test(t), "normal: vence em 2 dias vem da data, não do texto do JSON");
      const hrefs = await pg.$$eval("a[href]", (l) => l.map((a) => a.getAttribute("href")));
      confere(hrefs.every((h) => h.startsWith("#")), "normal: links só dentro da página (nada aponta para fora de app/)", hrefs);
      confere(await pg.evaluate(() => !!document.querySelector("#serie-box svg rect")), "normal: gráfico desenhado");
      const srcs = await pg.$$eval("script[src], link[href]", (l) => l.map((e) => e.getAttribute("src") || e.getAttribute("href")));
      confere(srcs.every((s) => !s.includes("..") && !s.includes("prototipo")), "normal: não depende da pasta de protótipos", srcs);
      // categorias: mostra 8 e libera todas
      confere((await pg.$$(".cats .cat")).length === 8, "normal: 8 categorias por padrão");
      await pg.evaluate(() => {
        window.__edicaoFetch = null;
        window.fetch = async (url, opts) => {
          window.__edicaoFetch = { url, body: JSON.parse(opts.body) };
          return { ok: true, json: async () => ({ ok: true, gerado_em: new Date().toISOString() }) };
        };
      });
      await pg.click(".editar-mov");
      await pg.$eval('.edicao-mov [name="descricao"]', (e) => { e.value = "Transporte ficticio"; });
      await pg.$eval('.edicao-mov [name="categoria"]', (e) => { e.value = "transporte"; });
      await pg.$eval('.edicao-mov [name="valor"]', (e) => { e.value = "42,50"; });
      await pg.click("#salvar-edicao");
      await pg.waitForFunction(() => !document.querySelector(".edicao-mov"), { timeout: 3000 });
      const envio = await pg.evaluate(() => window.__edicaoFetch);
      confere(envio?.url === "/api/financas/movimentos/editar" && envio.body.linha_csv === 2, "editar: envia a linha selecionada à rota local");
      confere(envio?.body.alterado.descricao === "Transporte ficticio" && envio.body.alterado.categoria === "transporte" && envio.body.alterado.valor === "42.50", "editar: envia os campos e normaliza valor decimal");
      await pg.click("#ver-todas"); confere((await pg.$$(".cats .cat")).length === 9, "normal: 'Mostrar todas' abre as 9");
      confere(/Xpto estranha/.test(await texto()), "normal: categoria desconhecida mantém o rótulo original");
      // Ctrl K
      await pg.keyboard.down("Control"); await pg.keyboard.press("k"); await pg.keyboard.up("Control"); await dormir(150);
      const pal = await pg.evaluate(() => document.querySelector("dialog.paleta")?.open && document.querySelector("#p-l").innerText);
      confere(pal && /Finanças\s+aberto/.test(pal) && /Canal/.test(pal) && /Ir para grupo/.test(pal), "Ctrl K: abre com a área atual e os demais grupos", pal);
      await pg.keyboard.press("Escape"); await dormir(100);
      const grupos = await pg.$$eval("a.aba", (links) => links.map((a) => ({ href: a.getAttribute("href"), nome: a.querySelector("span")?.innerText })));
      confere(grupos.length === 8, "shell: mostra os oito grupos do ecossistema");
      for (const grupo of grupos) {
        await pg.click(`a.aba[href="${grupo.href}"]`); await dormir(80);
        const titulo = await pg.$eval("main h1", (e) => e.innerText);
        confere(titulo === grupo.nome, `shell: abre ${grupo.nome}`);
        if (grupo.href !== "#/financas") confere(/Tela ainda nao conectada/.test(await texto()), `shell: ${grupo.nome} explica que a tela ainda não foi conectada`);
      }
      await pg.click('a[href="#/financas"]'); await dormir(100);
      // tema escuro
      await pg.keyboard.press("t"); await dormir(150);
      confere(await pg.evaluate(() => document.documentElement.dataset.tema) === "escuro", "tecla T alterna o tema");
      await pg.keyboard.press("t"); await dormir(100);
    });

    // ocultar valores
    console.log("\n== ocultar valores");
    fs.writeFileSync(DADOS, emJs(CEN.divergente(base())));
    await abrir(1440);
    confere((await texto()).includes("9.876,54"), "ocultar: antes, o saldo aparece");
    await pg.keyboard.press("o"); await dormir(200);
    let t = await texto(), h = await html();
    const vazou = [/R\$\s?\d/, /\d\.\d{3},\d{2}/, /\d+,\d{2}/, /\b54321\b/, /\b987654\b/, /1234[.,]56/, /123,45/].filter((r) => r.test(t) || r.test(h.replace(/data-[a-z]+="[^"]*"/g, "")));
    confere(!vazou.length, "ocultar: nenhum valor em texto, aria-label ou tooltip (mensagens, observação e 'centavos' mascarados)", vazou.map(String));
    confere(await pg.evaluate(() => !document.querySelector("#serie-box svg rect") && /escondido junto/.test(document.getElementById("serie-box").innerText)), "ocultar: gráfico some, com explicação");
    confere(await pg.evaluate(() => !document.querySelector(".ilha .pb") && !document.querySelector(".rg2 .pb")), "ocultar: barras que dariam valor somem (ilha e receitas x gastos)");
    confere(/\d+(,\d)?%/.test(t), "ocultar: percentuais de categoria continuam");
    confere(await pg.evaluate(() => document.getElementById("ocultar").getAttribute("aria-pressed")) === "true", "ocultar: botão marcado");
    await cap("normal_oculto_1440");
    await pg.reload({ waitUntil: "load" }); await dormir(400);
    confere(!/R\$\s?\d/.test(await texto()), "ocultar: a escolha persiste depois de recarregar");
    await pg.click("#ocultar"); await dormir(150);
    confere((await texto()).includes("9.876,54"), "ocultar: botão volta a mostrar");
    await abrir(390); await pg.keyboard.press("o"); await dormir(200);
    confere((await overflow()) <= 0, "ocultar 390px: sem rolagem lateral");
    await pg.evaluate(() => localStorage.clear());

    await cenario("atrasado", async () => {
      const t = await texto();
      confere(/Vencido há 5 dias/.test(t), "atrasado: dias de atraso recalculados pela data (JSON dizia 999)");
      confere(/Vence hoje/.test(t) && !/Vencido há 42/.test(t), "atrasado: 'vence hoje' vem da data (JSON dizia vencido há 42)");
      confere(/1 atrasado/.test(t), "atrasado: contagem de atrasados na ilha");
      confere(await pg.evaluate(() => !!document.querySelector(".vc.e-erro .est")), "atrasado: vencido com chip de erro (texto + forma)");
    });
    await cenario("divergente", async () => {
      const t = await texto();
      confere(/diferença de 543,21|diferenca de 54321 centavos/.test(t), "divergente: mensagem do gerador mostrada");
      confere(/Inconsistência/.test(t) && /O que fazer/.test(t), "divergente: diz o que fazer");
      confere(/3 inconsistências/.test(t), "divergente: conta as 3 inconsistências", t.match(/\d inconsist[^\n]*/)?.[0]);
    });
    await cenario("sem_vencimentos", async () => {
      const t = await texto();
      confere(/Nenhum vencimento a pagar/.test(t), "sem vencimentos: cartão explica");
      confere(await pg.evaluate(() => !document.querySelector(".nm:nth-child(4) .pb")), "sem vencimentos: sem barra em A pagar");
    });
    await cenario("velho", async () => {
      confere(/Dados velhos há 5 dias/.test(await texto()), "velho: selo calcula 5 dias de gerado_em");
      confere(await pg.evaluate(() => !!document.querySelector(".selo .e-erro")), "velho: selo em erro (mais de 3 dias)");
    });
    await cenario("vazio", async () => {
      const t = await texto();
      confere(/Ainda não há lançamentos/.test(t), "vazio: mensagem de estado vazio");
      confere(/movimentos\.csv/.test(t) && /Casemiro/.test(t), "vazio: diz o que fazer");
    });

    // erro: arquivo ausente, inválido, sintaxe quebrada, e "tentar de novo" sem recarregar a página
    for (const [nome, conteudo] of [["ausente", null], ["invalido", "window.FINANCAS = { saldos: {} };\n"], ["quebrado", "window.FINANCAS = {{{ ;\n"], ["lixo", 'window.FINANCAS = "texto";\n']]) {
      console.log(`\n== erro (${nome})`);
      if (conteudo === null) fs.rmSync(DADOS, { force: true }); else fs.writeFileSync(DADOS, conteudo);
      for (const L of [1440, 390]) {
        await abrir(L);
        const t = await texto();
        confere(/Não consegui ler os dados de Finanças/.test(t), `erro ${nome} ${L}px: mensagem clara`);
        confere(/python estudio\/dados\/gerar_financas\.py/.test(t), `erro ${nome} ${L}px: diz o comando do gerador`);
        confere(/Tentar de novo/.test(t), `erro ${nome} ${L}px: botão Tentar de novo`);
        confere(!/R\$\s?\d/.test(t), `erro ${nome} ${L}px: nenhum valor antigo na tela`);
        confere((await overflow()) <= 0, `erro ${nome} ${L}px: sem rolagem lateral`);
        confere(!errosJs.some((e) => !/SyntaxError|Unexpected|FINANCAS/.test(e)), `erro ${nome} ${L}px: sem erro de JS além do arquivo quebrado`, errosJs);
        await cap(`erro_${nome}_${L}`);
      }
    }
    console.log("\n== erro, depois corrigido: Tentar de novo");
    fs.rmSync(DADOS, { force: true });
    await abrir(1440);
    fs.writeFileSync(DADOS, emJs(base()));
    await pg.click("#tentar"); await pg.waitForSelector(".cats", { timeout: 4000 }).catch(() => {});
    confere((await texto()).includes("Lido hoje"), "Tentar de novo: lê o arquivo novo sem recarregar a página");

    // carregando
    console.log("\n== carregando");
    fs.writeFileSync(DADOS, emJs(base()));
    pg && await pg.close(); pg = await nav.newPage(); await pg.setViewport({ width: 1440, height: 900 });
    await pg.goto(url("?atraso=2500"), { waitUntil: "load" }); await dormir(300);
    confere(await pg.evaluate(() => !!document.querySelector("[aria-busy=true]") && document.querySelectorAll(".sk").length > 4), "carregando: esqueleto aparece enquanto o dado não existe");
    confere(!/R\$\s?\d/.test(await texto()), "carregando: sem número nenhum");
    await cap("carregando_1440");
    await pg.waitForSelector(".cats", { timeout: 6000 }).catch(() => {});
    confere((await texto()).includes("Lido hoje"), "carregando: troca pelo conteúdo quando o dado chega");

    await seletorMes();
    await painelDetalhes();
    if (REAL) await real();
  } finally { await nav.close(); }
}

const selMes = () => pg.evaluate(() => document.querySelector(".mb-chip.sel")?.dataset.mes);
const ilhaTxt =() => pg.evaluate(() => document.querySelector(".ilha").innerText.replace(/\s+,/g, ","));
const chipsN = () => pg.evaluate(() => document.querySelectorAll(".mb-chip").length);
const lsMes = () => pg.evaluate(() => localStorage.getItem("ce_h_fin_mes"));

async function seletorMes() {
  const AT = mesAtual(), P1 = mesesAtras(1), P2 = mesesAtras(2);
  // ---- seletor com vários meses
  fs.writeFileSync(DADOS, emJs(CEN.meses(base())));
  console.log("\n== seletor de mês: mês atual, passado só com recebimento, teclado, gráfico");
  await abrir(1440);
  confere(await selMes() === AT, "meses: abre no mês atual");
  confere(await chipsN() === 8, "meses: um chip por mês disponível", await chipsN());
  confere(await pg.evaluate(() => /atual/i.test(document.querySelector(".mb-chip.sel").innerText)), "meses: o mês atual vem marcado como 'atual'");
  confere((await pg.evaluate(() => document.querySelector(".mb-chip[data-mes]").innerText)).includes(longo(mesesAtras(7))), "meses: chip com mês e ano por extenso", longo(mesesAtras(7)));
  let it = await ilhaTxt();
  confere(it.includes("12.345,67") && it.includes("9.876,54"), "meses: mês atual mostra recebido e saldo");
  confere(/resultado das movimentações/i.test(it) && /não é saldo bancário/i.test(it), "meses: resultado do mês rotulado como não sendo saldo bancário");
  confere(/não muda com o mês/.test(it), "meses: saldo das contas rotulado como fixo");
  await pg.click(`.mb-chip[data-mes="${P1}"]`); await dormir(200);
  it = await ilhaTxt(); let t = await texto();
  confere(await selMes() === P1, "clique no chip: troca de mês");
  confere(it.includes("7.777,77") && !it.includes("12.345,67"), "mês passado: recebido do mês antigo na ilha, o do mês atual some");
  confere(it.includes("9.876,54"), "mês passado: saldo das contas continua o de hoje");
  confere(/Salario antigo ficticio/.test(t) && !/Mercado ficticio/.test(t), "mês passado: movimentos são os do mês escolhido");
  confere(/Nenhum gasto lançado em/.test(t) && /Nenhum vencimento a pagar em/.test(t), "mês passado só com recebimento: gastos zerados e explicados");
  confere(/Sobra/.test(t), "mês passado: resultado positivo");
  confere(/Saldo informado até|saldo informado até/.test(t) && /Banco Alfa/.test(t), "mês passado: contas continuam na tela");
  confere(/Alertas/.test(t) && /da leitura toda/.test(t), "mês passado: alertas rotulados como não sendo do mês");
  confere((await pg.evaluate(() => location.hash)) === `#mes=${P1}` && await lsMes() === P1, "clique no chip: URL e localStorage guardam o mês");
  confere(await pg.evaluate(() => !!document.querySelector(".sel-bg") && document.querySelector("g.sg[data-mes]") !== null), "gráfico: mês escolhido destacado");
  await cap("meses_passado_1440");
  // recarregar lembra; hash tem prioridade
  await pg.reload({ waitUntil: "load" }); await dormir(400);
  confere(await selMes() === P1, "recarregar: lembra o mês escolhido");
  await abrir(1440, `#mes=${P2}`);
  confere(await selMes() === P2, "URL #mes=AAAA-MM abre o mês pedido");
  confere(/Mostrar mais 40/.test(await texto()) && (await pg.$$(".mvs .mv")).length === 40, "mês com 85 lançamentos: lista pagina em 40");
  await pg.click("#ver-mais-mov"); await dormir(150); await pg.click("#ver-mais-mov"); await dormir(150);
  confere((await pg.$$(".mvs .mv")).length === 85 && !(await pg.$("#ver-mais-mov")), "mês com 85 lançamentos: 'mostrar mais' chega ao fim");
  await abrir(1440, "#mes=1999-01");
  confere(await selMes() === AT && !errosJs.length, "URL com mês inexistente: cai no mês atual sem erro", errosJs);
  // teclado
  await abrir(1440);
  await pg.focus(`.mb-chip[data-mes="${AT}"]`);
  await pg.keyboard.press("ArrowLeft"); await dormir(200);
  confere(await selMes() === P1 && await pg.evaluate(() => document.activeElement?.dataset?.mes) === P1, "teclado: seta esquerda vai ao mês anterior e mantém o foco");
  await pg.keyboard.press("ArrowLeft"); await dormir(150); await pg.keyboard.press("ArrowRight"); await dormir(150);
  confere(await selMes() === P1, "teclado: seta direita volta um mês");
  await pg.keyboard.press("ArrowRight"); await dormir(150); await pg.keyboard.press("ArrowRight"); await dormir(150);
  confere(await selMes() === AT, "teclado: no último mês, seta direita não passa do fim");
  confere(await pg.evaluate(() => document.getElementById("mes-prox").disabled), "seta próximo desabilitada no último mês");
  await pg.click("#mes-ant"); await dormir(150);
  confere(await selMes() === P1, "seta anterior (clique) troca de mês");
  // Ctrl K
  await pg.keyboard.down("Control"); await pg.keyboard.press("k"); await pg.keyboard.up("Control"); await dormir(150);
  await pg.keyboard.type("mes"); await dormir(150);
  const lista = await pg.evaluate(() => document.querySelector("#p-l").innerText);
  confere(lista.includes("Ir para " + longo(AT)) && lista.includes("Ir para " + longo(P2)), "Ctrl K: 'Ir para mês...' lista os meses", lista.slice(0, 200));
  await pg.evaluate(() => { document.querySelector("#p-q").value = ""; });
  await pg.keyboard.type("Ir para " + longo(P2)); await dormir(150); await pg.keyboard.press("Enter"); await dormir(200);
  confere(await selMes() === P2, "Ctrl K: escolher um mês troca a tela");
  // gráfico
  await pg.click(`g.sg[data-mes="${P1}"] .hit`); await dormir(200);
  confere(await selMes() === P1, "gráfico: clicar numa barra seleciona o mês");
  // ocultar valores num mês antigo
  await pg.keyboard.press("o"); await dormir(200);
  t = await texto(); const h = await html();
  const vz = [/R\$\s?\d/, /\d\.\d{3},\d{2}/, /\d+,\d{2}\b/, /7777/, /987654/].filter((r) => r.test(t) || r.test(h.replace(/data-[a-z]+="[^"]*"/g, "")));
  confere(!vz.length && /Salario antigo ficticio/.test(t), "ocultar no mês antigo: nenhum valor, nem nos movimentos listados", vz.map(String));
  await pg.click(`.mb-chip[data-mes="${P2}"]`); await dormir(200);
  t = await texto();
  confere(!/R\$\s?\d/.test(t) && !/\d\.\d{3},\d{2}/.test(t), "ocultar continua valendo ao trocar de mês");
  await cap("meses_oculto_1440");
  await pg.keyboard.press("o"); await dormir(100);
  // tema escuro
  await pg.keyboard.press("t"); await dormir(150);
  confere(await pg.evaluate(() => getComputedStyle(document.querySelector(".mb-chip.sel")).backgroundColor) !== "", "tema escuro: seletor desenha");
  await cap("meses_escuro_1440"); await pg.keyboard.press("t");

  // ---- celular: chips rolam na horizontal
  await abrir(390, `#mes=${P1}`, { toque: true });
  const m = await pg.evaluate(() => { const c = document.getElementById("mb-chips"); return { rola: c.scrollWidth > c.clientWidth, ov: getComputedStyle(c).overflowX, sel: c.querySelector(".sel").getBoundingClientRect().right <= innerWidth + 1 }; });
  confere(m.rola && /auto|scroll/.test(m.ov), "390px: chips viram rolagem horizontal", m);
  confere(m.sel && (await overflow()) <= 0 && !errosJs.length, "390px: mês escolhido visível, sem rolagem lateral da página", errosJs);
  const alvo = await pg.evaluate(() => Math.min(...[...document.querySelectorAll(".mb-chip, .mb-seta")].map((b) => b.getBoundingClientRect().height)));
  confere(alvo >= 44, "390px: alvos de toque com 44px ou mais", alvo);
  await cap("meses_passado_390");

  // ---- mês atual vazio: estado vazio e atalho para o último com lançamentos
  console.log("\n== mês atual vazio");
  fs.writeFileSync(DADOS, emJs(CEN.mes_vazio(base())));
  for (const L of [1440, 390]) {
    await abrir(L);
    t = await texto();
    confere(new RegExp("Nenhum lançamento em " + longo(AT)).test(t), `mês vazio ${L}px: diz que não há lançamento no mês`);
    confere(await pg.evaluate(() => !!document.getElementById("ir-ultimo")) && t.includes("Ver " + longo(P1)), `mês vazio ${L}px: oferece o último mês com lançamentos`);
    confere((await overflow()) <= 0 && !errosJs.length, `mês vazio ${L}px: sem rolagem lateral nem erro`, errosJs);
    await cap(`mes_vazio_${L}`);
  }
  await pg.click("#ir-ultimo"); await dormir(250);
  confere(await selMes() === P1 && (await ilhaTxt()).includes("7.777,77"), "mês vazio: o botão leva ao último mês com lançamentos");
  await pg.click(`.mb-chip[data-mes="${mesesAtras(7)}"]`); await dormir(200);
  t = await texto();
  confere(/Nenhum lançamento em/.test(t) && !(await pg.evaluate(() => !!document.getElementById("ir-ultimo"))), "mês antigo vazio: estado vazio sem sugestão (só o mês atual sugere)");

  // ---- virada de ano
  console.log("\n== virada de ano");
  fs.writeFileSync(DADOS, emJs(CEN.virada(base())));
  await abrir(1440);
  confere(await selMes() === "2026-01" && /Janeiro 2026/.test(await ilhaTxt()), "virada: abre em Janeiro 2026");
  await pg.focus('.mb-chip[data-mes="2026-01"]'); await pg.keyboard.press("ArrowLeft"); await dormir(200);
  confere(await selMes() === "2025-12" && /Dezembro 2025/.test(await ilhaTxt()), "virada: seta esquerda de Janeiro 2026 vai a Dezembro 2025");
  confere((await ilhaTxt()).includes("7.777,77"), "virada: Dezembro 2025 traz os números do próprio mês");
  confere(!errosJs.length, "virada: sem erro de JS", errosJs);

  // ---- arquivo antigo, sem `meses`: só o mês atual, sem erro
  console.log("\n== arquivo sem `meses`");
  fs.writeFileSync(DADOS, emJs(base()));
  await abrir(1440);
  t = await texto();
  confere(await chipsN() === 1 && await selMes() === AT && !errosJs.length, "sem meses: um único chip, o mês atual, sem erro", errosJs);
  confere(/só traz o mês atual/.test(t) && t.includes("12.345,67"), "sem meses: explica a limitação e mostra o mês atual");
  confere((await pg.$$(".mvs .mv")).length === 4 && /Movimentos recentes/.test(t), "sem meses: movimentos recentes como antes");
  await pg.keyboard.press("Tab"); await pg.focus(".mb-chip"); await pg.keyboard.press("ArrowLeft"); await dormir(100);
  confere(await selMes() === AT && !errosJs.length, "sem meses: setas não fazem nada nem dão erro");
  // meses malformado: cai para o comportamento antigo
  const torto = base(); torto.meses_disponiveis = ["2020-01"]; torto.meses = { "2020-01": { recebido: "x" } };
  fs.writeFileSync(DADOS, emJs(torto)); await abrir(1440);
  confere(await chipsN() === 1 && !errosJs.length && /Receitas e gastos/.test(await texto()), "meses torto: ignora o bloco e mostra o mês atual", errosJs);
}

/* ---------- PROG-024c, Fluxo 1: os 4 cards da ilha abrem o painel com a lista de movimentos (dados inventados) ---------- */
const PN = { rec: 640000, pago: 32500, apagar: 92540 };
function fixPN() {
  const d = base(), AT = mesAtual();
  const lista = [ // mais antigo primeiro, como em meses[mes].movimentos
    { linha_csv: 2, data: iso(-2), tipo: "recebido", categoria: "salario", descricao: "Salario ficticio", valor: 520000, status: "pago" },
    { linha_csv: 3, data: iso(0), tipo: "recebido", categoria: "renda", descricao: "Reembolso ficticio", valor: 120000, status: "pago" },
    { linha_csv: 4, data: iso(5), tipo: "recebido", categoria: "freelance", descricao: "Freela ficticio", valor: 50000, status: "a receber" },
    { linha_csv: 5, data: iso(-1), tipo: "gasto", categoria: "mercado", descricao: "Mercado ficticio", valor: 25050, status: "pago" },
    { linha_csv: 6, data: iso(0), tipo: "gasto", categoria: "saude", descricao: "Farmacia ficticia", valor: 7450, status: "pago" },
    { linha_csv: 7, data: iso(-3), tipo: "gasto", categoria: "contas", descricao: "Luz ficticia", valor: 21430, status: "a pagar" },
    { linha_csv: 8, data: iso(0), tipo: "gasto", categoria: "contas", descricao: "Internet ficticia", valor: 11111, status: "a pagar" },
    { linha_csv: 9, data: iso(2), tipo: "gasto", categoria: "contas", descricao: "Agua ficticia", valor: 4444, status: "a pagar" },
    { linha_csv: 10, data: iso(20), tipo: "gasto", categoria: "outros", descricao: "Seguro ficticio", valor: 55555, status: "a pagar" },
  ];
  d.recebido = { mes: PN.rec, previsto_mes: 50000, total_6m: PN.rec, previsto_6m: 50000 };
  d.gastos = { pagos_mes: PN.pago, a_pagar_mes: PN.apagar, pagos_6m: PN.pago, a_pagar_6m: PN.apagar };
  d.receitas_x_gastos = { mes: AT, receitas: PN.rec, gastos: PN.pago };
  d.serie_mensal[5] = { ...d.serie_mensal[5], recebido: PN.rec, previsto: 50000, gasto_pago: PN.pago, gasto_a_pagar: PN.apagar };
  d.movimentos_recentes = lista.slice().reverse();
  d.vencimentos = lista.filter((m) => m.status === "a pagar").map(({ data, descricao, categoria, valor }) => ({ data, descricao, categoria, valor, dias_restantes: 0, atrasado: false, status: "a pagar" }));
  comMeses(d);
  d.meses[AT] = mesFix(AT, { rec: PN.rec, prev: 50000, pago: PN.pago, apagar: PN.apagar, cats: d.categorias, movs: lista, venc: d.vencimentos });
  return d;
}
const NOMES_ISO = (m) => `${NOMES[+m.slice(5, 7) - 1]} de ${m.slice(0, 4)}`;
const dmIso = (d) => iso(d).slice(8, 10) + "/" + iso(d).slice(5, 7);

async function painelDetalhes() {
  const AT = mesAtual(), P1 = mesesAtras(1), P2 = mesesAtras(2);
  const pnAberto = () => pg.evaluate(() => !!document.querySelector("dialog.painel-mov[open]"));
  const pnTxt = () => pg.evaluate(() => (document.querySelector("dialog.painel-mov") || { innerText: "" }).innerText.replace(/[ \t]+\n/g, "\n"));
  const linhas = () => pg.$$eval("dialog.painel-mov .pm", (l) => l.map((e) => e.innerText.replace(/\s+/g, " ")));
  const abrirCard = async (t) => { await pg.click(`.nm[data-pn="${t}"]`); await dormir(200); };
  const fechar = async () => { await pg.keyboard.press("Escape"); await dormir(150); };
  console.log("\n== PROG-024c: painel dos 4 cards (1440)");
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await pg.evaluate(() => localStorage.clear()).catch(() => {});
  await abrir(1440);
  confere(!errosJs.length, "painel: sem erro de JS ao abrir a tela", errosJs);
  const ROTS = { saldo: "Saldo disponível: ver movimentos que o compõem", recebido: "Recebido no mês: ver movimentos", gasto: "Gasto pago no mês: ver movimentos", "a-pagar": "A pagar no mês: ver movimentos" };
  const bts = await pg.$$eval(".ilha .i-nums button.nm", (l) => l.map((b) => ({ pn: b.dataset.pn, aria: b.getAttribute("aria-label"), tipo: b.getAttribute("type"), chevron: !!b.querySelector(".nm-seta"), dica: /Ver movimentos/.test(b.innerText) })));
  confere(bts.length === 4 && bts.every((b) => ROTS[b.pn] === b.aria && b.tipo === "button"), "cards: os 4 viram <button> com o aria-label da spec", bts);
  confere(bts.length === 4 && bts.every((b) => b.chevron && b.dica), "cards: chevron e dica 'Ver movimentos'", bts);
  confere(await pg.evaluate(() => !document.querySelector(".ilha .i-nums div, .ilha .i-nums p, .ilha .i-nums article")), "cards: sem bloco dentro do botão (HTML válido)");
  // resposta em até 100 ms e foco no título
  const ms = await pg.evaluate(() => { const t0 = performance.now(), b = document.querySelector('.nm[data-pn="recebido"]'); b.click(); return { ms: performance.now() - t0, aberto: !!document.querySelector("dialog.painel-mov[open]") }; });
  confere(ms.aberto && ms.ms < 100, "cards: o clique abre o painel na hora (menos de 100 ms)", ms);
  await dormir(200);
  confere(await pg.evaluate(() => document.activeElement && document.activeElement.id === "pn-t"), "painel: o foco vai ao título ao abrir");
  confere(await pg.evaluate(() => location.hash) === "#/financas/recebido", "painel: a URL ganha #/financas/recebido");
  const geo = await pg.evaluate(() => { const r = document.querySelector("dialog.painel-mov").getBoundingClientRect(); return { w: Math.round(r.width), dir: Math.round(innerWidth - r.right), alt: Math.round(r.height), ih: innerHeight }; });
  confere(geo.w === 480 && geo.dir === 0 && geo.alt === geo.ih, "painel desktop: lateral à direita com 480 px de largura", geo);
  await pg.evaluate(() => { document.querySelector("dialog.painel-mov .pn-corpo"); });
  let t = await pnTxt();
  confere(/Recebido no mês/.test(t) && new RegExp(`${NOMES_ISO(AT)} · 2 movimentos · Total R\\$ 6\\.400,00`).test(t), "recebido: título e resumo com mês, contagem e total", t.slice(0, 200));
  let L = await linhas();
  confere(L.length === 2 && /Salario ficticio/.test(L.join()) && /Reembolso ficticio/.test(L.join()) && !/Freela/.test(L.join()), "recebido: só receitas com status recebido (a receber fica de fora)", L);
  confere(L.every((x) => /\+\s*R\$/.test(x) && /Recebido em \d\d\/\d\d/i.test(x)), "recebido: sinal + e texto 'recebido em dd/mm' (não só cor)", L);
  confere(new RegExp(`Hoje, ${dmIso(0)}`).test(t) && new RegExp(dmIso(-2)).test(t), "recebido: agrupa por dia (Hoje, dd/mm)", t);
  confere(await pg.evaluate(() => !document.querySelector(".pn-soma")) && !/Marcar como pago/.test(t), "recebido: soma bate com o card (sem aviso) e sem 'Marcar como pago'");
  confere(/Fonte: movimentos\.csv, lido hoje/.test(t), "painel: rodapé com a fonte e a hora da leitura", t.slice(-120));
  confere(await pg.evaluate(() => getComputedStyle(document.body).overflow === "hidden"), "painel: a tela de trás não rola");
  await cap("painel_recebido_1440");
  // Esc fecha e devolve o foco ao card
  await fechar();
  confere(!(await pnAberto()) && await pg.evaluate(() => document.activeElement && document.activeElement.dataset.pn) === "recebido", "painel: Esc fecha e o foco volta ao card");
  confere(!/#\/financas\//.test(await pg.evaluate(() => location.hash)), "painel: fechar limpa a âncora da URL");
  // teclado: Enter e Espaço
  await pg.focus('.nm[data-pn="gasto"]'); await pg.keyboard.press("Enter"); await dormir(150);
  confere(await pnAberto() && /Gasto pago no mês/.test(await pnTxt()), "teclado: Enter abre o painel do card focado");
  await fechar();
  await pg.focus('.nm[data-pn="gasto"]'); await pg.keyboard.press("Space"); await dormir(150);
  confere(await pnAberto(), "teclado: Espaço abre o painel do card focado");
  t = await pnTxt(); L = await linhas();
  confere(/Gasto pago no mês/.test(t) && L.length === 2 && /Mercado ficticio/.test(L.join()) && /Farmacia ficticia/.test(L.join()) && !/Luz ficticia/.test(L.join()), "gasto: só gastos com status pago", L);
  confere(/Total R\$ 325,00/.test(t) && L.every((x) => /−\s*R\$/.test(x) && /Pago em \d\d\/\d\d/i.test(x)), "gasto: total, sinal − e 'pago em dd/mm'", t.slice(0, 160));
  confere(new RegExp(`Hoje, ${dmIso(0)}`).test(t) && new RegExp(`Ontem, ${dmIso(-1)}`).test(t), "gasto: grupos Hoje e Ontem");
  await fechar();
  // A pagar: grupos e situação em texto
  await abrirCard("a-pagar");
  t = await pnTxt(); L = await linhas();
  confere(L.length === 4 && /Total R\$ 925,40/.test(t), "a pagar: 4 contas e total 925,40", t.slice(0, 200));
  const grupos = await pg.$$eval("dialog.painel-mov .pm-g", (l) => l.map((e) => e.innerText.replace(/\s+/g, " ")));
  confere(grupos.length === 3 && /^Vencidos \(1\)/.test(grupos[0]) && /^Vencem em até 3 dias \(2\)/.test(grupos[1]) && /^Mais adiante \(1\)/.test(grupos[2]), "a pagar: Vencidos, Vencem em até 3 dias e Mais adiante, cada um com contagem", grupos);
  confere(/R\$ 214,30/.test(grupos[0]) && /R\$ 155,55/.test(grupos[1]) && /R\$ 555,55/.test(grupos[2]), "a pagar: cada grupo mostra a soma", grupos);
  confere(/Venceu há 3 dias/.test(t) && /Vence hoje/.test(t) && /Vence em 2 dias/.test(t) && new RegExp(`Vence em ${dmIso(20)}`).test(t), "a pagar: situação em texto (venceu há, vence hoje, vence em N dias, vence em dd/mm)", t);
  confere(await pg.evaluate(() => !!document.querySelector(".pm .est.e-erro") && !!document.querySelector(".pm .est.e-pendente") && !!document.querySelector(".pm .est.e-backlog")), "a pagar: chips com ícone e texto em erro, pendente e backlog");
  confere(!/Marcar como pago/.test(t) && (await pg.$$("dialog.painel-mov .pm-ed")).length === 4, "a pagar: só 'Editar' em cada linha (Marcar como pago fica para outra entrega)");
  confere(/Nenhum pagamento é feito por este app/.test(t), "a pagar: avisa que nenhum pagamento é feito");
  await fechar();
  // Saldo
  await abrirCard("saldo");
  t = await pnTxt(); L = await linhas();
  confere(/Movimentos do saldo/.test(t) && L.length === 4 && !/Luz ficticia|Freela/.test(L.join()), "saldo: recebidos e gastos pagos do mês (4 linhas)", L);
  confere(L.filter((x) => /\+\s*R\$/.test(x)).length === 2 && L.filter((x) => /−\s*R\$/.test(x)).length === 2, "saldo: entradas com + e saídas com −", L);
  confere(/Banco Alfa/.test(t) && /Banco Beta/.test(t) && /fora do disponível/i.test(t) && /atualizado em/i.test(t), "saldo: contas no topo, com a etiqueta 'fora do disponível'", t.slice(0, 400));
  confere(/O saldo do banco não é a soma destes movimentos\. Esta lista mostra só o que você lançou como pago ou recebido\./.test(t), "saldo: texto fixo explicando que o saldo do banco não é a soma");
  confere(await pg.evaluate(() => !document.querySelector(".pn-soma")), "saldo: sem aviso de soma (o card vem do banco)");
  await fechar();

  // busca e ordenação
  console.log("\n== painel: busca, ordenação, mês, âncora");
  await abrirCard("gasto");
  await pg.type("#pn-q", "farm"); await dormir(100);
  L = await linhas();
  confere(L.length === 1 && /Farmacia/.test(L[0]) && /1 de 2/.test(await pnTxt()), "busca: filtra por descrição no navegador e diz 'Mostrando 1 de 2'", L);
  await pg.$eval("#pn-q", (e) => { e.value = ""; }); await pg.type("#pn-q", "mercado"); await dormir(100);
  confere((await linhas()).length === 1, "busca: também filtra pela categoria");
  await pg.$eval("#pn-q", (e) => { e.value = ""; }); await pg.type("#pn-q", "zzz"); await dormir(100);
  t = await pnTxt();
  confere(/Nenhum movimento com “zzz”\. Limpe a busca para ver todos\./.test(t) && /Limpar busca/.test(t), "busca sem resultado: mensagem e botão Limpar busca", t.slice(-200));
  await pg.click("#pn-limpar"); await dormir(100);
  confere((await linhas()).length === 2 && await pg.$eval("#pn-q", (e) => e.value) === "", "Limpar busca: volta a lista toda");
  await pg.select("#pn-ord", "valor"); await dormir(100);
  L = await linhas();
  confere(/Mercado/.test(L[0]) && /Farmacia/.test(L[1]), "ordenar por valor: o maior primeiro", L);
  await pg.select("#pn-ord", "data-asc"); await dormir(100);
  L = await linhas();
  confere(/Mercado/.test(L[0]), "ordenar por data (mais antiga primeiro): ontem antes de hoje", L);
  // mês
  const meses = await pg.$$eval("#pn-mes option", (o) => o.map((x) => x.value));
  confere(meses.length === 8 && await pg.$eval("#pn-mes", (e) => e.value) === AT, "mês: seletor lista os meses disponíveis e abre no mês da tela", meses);
  await pg.select("#pn-mes", P2); await dormir(150);
  t = await pnTxt();
  confere(new RegExp(NOMES_ISO(P2) + " · 85 movimentos · Total R\\$ 85,00").test(t), "mês: trocar mostra o resumo do outro mês", t.slice(0, 160));
  confere(await pg.evaluate(() => !document.querySelector(".pn-soma")), "mês: soma do mês antigo bate com o card");
  await fechar();
  // vazio por tipo
  await abrir(1440, `#mes=${P2}`);
  await abrirCard("recebido");
  t = await pnTxt();
  const mesLower = NOMES[+P2.slice(5, 7) - 1].toLowerCase();
  confere(t.includes(`Nada recebido em ${mesLower}`) && /Ainda não há receitas com status recebido neste mês\. Se você já recebeu algo, confira o status do lançamento\./.test(t), "vazio recebido: título e texto da spec", t.slice(0, 300));
  confere(await pg.evaluate(() => [...document.querySelectorAll("dialog.painel-mov button")].some((b) => b.innerText.trim() === "Ver outro mês")), "vazio recebido: botão Ver outro mês (há outros meses com dados)");
  confere(await pg.evaluate(() => !!document.querySelector("dialog.painel-mov .pn-vazio .slot")), "vazio: usa o slot vazio_financas");
  await pg.click("#pn-outro"); await dormir(100);
  confere(await pg.evaluate(() => document.activeElement && document.activeElement.id === "pn-mes"), "vazio: Ver outro mês leva o foco ao seletor de mês");
  await fechar(); if (await pnAberto()) await fechar(); // o 1º Esc pode só fechar a lista de meses que o botão abriu
  await abrirCard("a-pagar");
  confere((await pnTxt()).includes(`Nada a pagar em ${mesLower}`) && /Todas as contas deste mês estão pagas ou ainda não foram lançadas\./.test(await pnTxt()), "vazio a pagar: título e texto da spec");
  await fechar();
  await abrir(1440, `#mes=${P1}`);
  await abrirCard("gasto");
  t = await pnTxt();
  confere(t.includes(`Nenhum gasto pago em ${NOMES[+P1.slice(5, 7) - 1].toLowerCase()}`) && /Gastos ainda não pagos aparecem em “A pagar”\./.test(t), "vazio gasto pago: título e texto da spec", t.slice(0, 300));
  await pg.click("#pn-apagar"); await dormir(150);
  confere(/A pagar no mês/.test(await pnTxt()) && await pg.evaluate(() => location.hash) === "#/financas/a-pagar", "vazio gasto pago: 'Abrir A pagar' troca de painel");
  await fechar();
  await abrirCard("saldo");
  confere((await pnTxt()).includes("Sem movimentos neste mês") === false, "saldo do mês com movimento não mostra vazio");
  await fechar();

  // soma que não bate com o card (fixture antiga: números do card ≠ lista)
  console.log("\n== painel: soma divergente, âncora, voltar do navegador");
  fs.writeFileSync(DADOS, emJs(CEN.meses(base())));
  await abrir(1440);
  await abrirCard("recebido");
  t = await pnTxt();
  confere(await pg.evaluate(() => !!document.querySelector(".pn-soma.e-erro")) && /A soma desta lista \(R\$ 3\.000,00\) não bate com o card \(R\$ 12\.345,67\)\. Veja Alertas\./.test(t), "soma divergente: aviso em texto com os dois valores", t.slice(0, 400));
  await pg.goBack(); await dormir(200);
  confere(!(await pnAberto()), "voltar do navegador fecha o painel");
  confere(await pg.evaluate(() => !document.querySelector("dialog.painel-mov[open]")) && !errosJs.length, "voltar do navegador: sem erro de JS", errosJs);
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await abrir(1440, "#/financas/a-pagar");
  confere(await pnAberto() && /A pagar no mês/.test(await pnTxt()), "âncora: abrir a URL #/financas/a-pagar já abre o painel");
  await fechar();
  confere(!/#\/financas\//.test(await pg.evaluate(() => location.hash)), "âncora aberta por URL: Esc limpa a âncora sem sair da página");
  await abrir(1440, "#/financas/nada");
  confere(!(await pnAberto()) && !errosJs.length, "âncora inválida: ignora sem erro", errosJs);

  // Editar reaproveita o modal que já existe; depois de salvar, o painel recarrega e continua aberto
  console.log("\n== painel: Editar, carregando, erro, dados velhos, sem permissão");
  await abrir(1440);
  await abrirCard("gasto");
  await pg.evaluate(() => { window.__env = null; window.fetch = async (u, o) => { window.__env = { u, b: JSON.parse(o.body) }; return { ok: true, json: async () => ({ ok: true }) }; }; });
  await pg.click('dialog.painel-mov .pm-ed[data-linha="6"]'); await dormir(150);
  confere(await pg.evaluate(() => { const d = document.querySelector(".edicao-mov"); return !!d && d.open && /Editar movimento/.test(d.innerText) && d.querySelector("[name=descricao]").value === "Farmacia ficticia"; }), "editar: abre o modal de edição que já existe, com os dados da linha");
  await pg.$eval('.edicao-mov [name="descricao"]', (e) => { e.value = "Farmacia ajustada"; });
  await pg.click("#salvar-edicao"); await dormir(700);
  const env = await pg.evaluate(() => window.__env);
  confere(env && env.u === "/api/financas/movimentos/editar" && env.b.linha_csv === 6 && env.b.alterado.descricao === "Farmacia ajustada", "editar: envia a linha certa à rota existente", env);
  confere(await pnAberto() && !(await pg.$(".edicao-mov")), "editar: o modal fecha e o painel continua aberto");
  confere(await pg.evaluate(() => { const t = document.getElementById("toast"); return !!t.closest("dialog.painel-mov") && /Lançamento atualizado/.test(t.innerText); }), "editar: o aviso 'Lançamento atualizado.' aparece sobre o painel");
  confere(await pg.evaluate(() => document.activeElement && document.activeElement.dataset.linha) === "6", "editar: o foco volta ao botão Editar da mesma linha");
  await fechar();

  // carregando: esqueleto só depois de 300 ms; sem Editar enquanto isso
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await abrir(1440, "?atraso=1500");
  await abrirCard("gasto");
  await pg.evaluate(() => { window.fetch = async () => ({ ok: true, json: async () => ({ ok: true }) }); });
  await pg.click('dialog.painel-mov .pm-ed[data-linha="5"]'); await dormir(150);
  await pg.click("#salvar-edicao"); await dormir(120);
  confere(await pg.evaluate(() => !document.querySelector(".pn-sk")) && (await linhas()).length === 2, "carregando: antes de 300 ms o painel não pisca nem mostra esqueleto");
  await dormir(500);
  confere(await pg.evaluate(() => document.querySelectorAll(".pn-sk .sk").length >= 5 && !document.querySelector(".pm-ed, .pm .pm-ed") && /Carregando movimentos…/.test(document.querySelector(".pn-sk").closest("dialog").innerText) && document.querySelector("dialog.painel-mov [aria-live=polite]")), "carregando: esqueleto com 5 linhas, texto 'Carregando movimentos…' e sem botão Editar");
  confere(new RegExp(NOMES_ISO(AT)).test(await pnTxt()) && await pg.evaluate(() => !!document.querySelector("dialog.painel-mov [data-fechar]")), "carregando: cabeçalho com o mês e botão Fechar continuam");
  await cap("painel_carregando_1440");
  await pg.waitForFunction(() => !document.querySelector(".pn-sk"), { timeout: 4000 });
  confere((await linhas()).length === 2 && await pnAberto(), "carregando: a lista volta quando a leitura termina");
  await fechar();

  // erro: arquivo some depois de aberto; Tentar de novo duas vezes; Ver detalhes; sem valor antigo
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await abrir(1440);
  await abrirCard("gasto");
  await pg.evaluate(() => { window.fetch = async () => ({ ok: true, json: async () => ({ ok: true }) }); });
  fs.rmSync(DADOS, { force: true });
  await pg.click('dialog.painel-mov .pm-ed[data-linha="5"]'); await dormir(150);
  await pg.click("#salvar-edicao"); await dormir(700);
  t = await pnTxt();
  confere(/Não consegui carregar os movimentos/.test(t) && /A leitura dos dados falhou\. Nenhum valor antigo é mostrado aqui para você não confundir com o atual\./.test(t), "erro: título e texto da spec", t.slice(0, 300));
  confere(!/R\$\s?\d/.test(t) && (await linhas()).length === 0, "erro: nenhum valor antigo no painel");
  confere(await pg.evaluate(() => [...document.querySelectorAll("dialog.painel-mov button")].some((b) => /Tentar de novo/.test(b.innerText)) && [...document.querySelectorAll("dialog.painel-mov button")].some((b) => b.innerText.trim() === "Fechar")), "erro: botões Tentar de novo e Fechar");
  confere(await pg.evaluate(() => { const d = document.querySelector("dialog.painel-mov details"); return !!d && !d.open && /Ver detalhes/.test(d.innerText) && /ausente|invalido/.test(d.textContent); }), "erro: 'Ver detalhes' recolhido, com o código do erro");
  await cap("painel_erro_1440");
  await pg.click("#pn-tentar"); await dormir(700);
  t = await pnTxt();
  confere(/Continua sem carregar\. Verifique se o Corte está aberto neste computador e tente de novo em alguns segundos\./.test(t), "erro: se falhar de novo, diz o que verificar", t.slice(0, 400));
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await pg.click("#pn-tentar"); await dormir(700);
  confere(await pnAberto() && (await linhas()).length === 2 && !/Continua sem carregar/.test(await pnTxt()), "erro: Tentar de novo com o arquivo de volta mostra a lista");
  await fechar();

  // dados velhos
  const velho = fixPN(); velho.gerado_em = agora(-5);
  fs.writeFileSync(DADOS, emJs(velho));
  await abrir(1440);
  await abrirCard("recebido");
  t = await pnTxt();
  confere(/Dados de 5 dias atrás\. Os valores podem estar desatualizados\./.test(t) && /Atualizar leitura/.test(t), "dados velhos: faixa com os dias e botão Atualizar leitura", t.slice(0, 240));
  await pg.click("#pn-atualizar"); await dormir(600);
  confere(/Dados de 5 dias atrás/.test(await pnTxt()) && /gerar_financas\.py/.test(await pnTxt()), "dados velhos: se a leitura continua velha, diz como gerar dados novos");
  await cap("painel_velho_1440");
  await fechar();
  fs.writeFileSync(DADOS, emJs(fixPN()));
  await abrir(1440);
  await abrirCard("recebido");
  confere(!/Dados de \d+ dias atrás/.test(await pnTxt()), "dados de hoje: sem faixa de dados velhos");
  await fechar();

  // sem permissão (acesso por rede)
  await abrir(1440, "?acesso=remoto");
  const bl = await pg.$$eval(".ilha .i-nums button.nm", (l) => l.map((b) => ({ d: b.getAttribute("aria-disabled"), t: /Bloqueado: abra no computador/.test(b.innerText) })));
  confere(bl.length === 4 && bl.every((b) => b.d === "true" && b.t), "sem permissão: os 4 cards ficam aria-disabled com 'Bloqueado: abra no computador'", bl);
  await pg.click('.nm[data-pn="gasto"]'); await dormir(150);
  t = await pnTxt();
  confere(/Finanças só abre neste computador/.test(t) && /Por segurança, os movimentos não aparecem quando o Corte é aberto pela rede \(celular, por exemplo\)\. Abra o Corte direto no computador para ver e editar\./.test(t), "sem permissão: título e texto da spec", t.slice(0, 300));
  confere(await pg.evaluate(() => { const b = [...document.querySelectorAll("dialog.painel-mov button")].map((x) => x.innerText.trim()); return b.includes("Entendi") && !b.some((x) => /Tentar de novo/.test(x)) && !document.querySelector(".pm"); }), "sem permissão: só 'Entendi' (não adianta tentar de novo) e nenhuma linha");
  await pg.click("#pn-entendi"); await dormir(150);
  confere(!(await pnAberto()), "sem permissão: Entendi fecha o painel");
  // erro/carregando da tela: cards desabilitados, não abrem
  fs.rmSync(DADOS, { force: true });
  await abrir(1440);
  confere(await pg.evaluate(() => [...document.querySelectorAll(".ilha .i-nums .nm")].every((b) => b.getAttribute("aria-disabled") === "true")), "sem leitura: os cards ficam desabilitados (nada para listar)");
  fs.writeFileSync(DADOS, emJs(fixPN()));

  // ocultar valores: nada vaza no painel
  console.log("\n== painel: ocultar valores");
  await abrir(1440);
  await pg.keyboard.press("o"); await dormir(150);
  for (const tp of ["saldo", "recebido", "gasto", "a-pagar"]) {
    await abrirCard(tp);
    t = await pnTxt(); const h = await pg.evaluate(() => document.querySelector("dialog.painel-mov").innerHTML.replace(/data-[a-z-]+="[^"]*"/g, ""));
    const vz = [/R\$\s?\d/, /\d\.\d{3},\d{2}/, /\d+,\d{2}\b/, /\b640000\b/, /\b92540\b/, /\b21430\b/].filter((r) => r.test(t) || r.test(h));
    confere(!vz.length && /R\$ ••••/.test(t), `ocultar (${tp}): nenhum valor no painel (texto, aria-label, cabeçalho e soma)`, vz.map(String));
    await fechar();
  }
  await pg.evaluate(() => localStorage.clear());

  // celular 390
  console.log("\n== painel: celular 390");
  await abrir(390, "", { toque: true });
  confere(await pg.evaluate(() => [...document.querySelectorAll(".ilha .i-nums button.nm")].every((b) => b.getBoundingClientRect().height >= 44)), "390: os cards têm alvo de toque de 44 px ou mais");
  await pg.tap('.nm[data-pn="a-pagar"]'); await dormir(250);
  const g = await pg.evaluate(() => { const r = document.querySelector("dialog.painel-mov").getBoundingClientRect(), c = document.querySelector("dialog.painel-mov .pn-corpo"); return { x: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height), ih: innerHeight, iw: innerWidth, rolaLado: c.scrollWidth - c.clientWidth, doc: document.documentElement.scrollWidth - innerWidth }; });
  confere(g.x === 0 && g.w === g.iw && g.h === g.ih && g.rolaLado <= 0 && g.doc <= 0, "390: folha de tela inteira, sem rolagem lateral", g);
  confere(await pg.evaluate(() => { const b = document.querySelector("dialog.painel-mov .pn-volta"); const r = b.getBoundingClientRect(); return getComputedStyle(b).display !== "none" && r.height >= 44 && /Voltar/.test(b.innerText); }), "390: botão Voltar grande no topo");
  const alvos = await pg.$$eval("dialog.painel-mov .pm-ed, dialog.painel-mov .pn-x", (l) => l.map((b) => { const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; }));
  confere(alvos.length >= 5 && alvos.every(([w, h]) => w >= 44 && h >= 44), "390: Editar (lápis) e Fechar com 44x44 px ou mais", alvos);
  confere(await pg.evaluate(() => [...document.querySelectorAll("dialog.painel-mov .pm-ed")].every((b) => /^Editar .+/.test(b.getAttribute("aria-label")))), "390: Editar tem aria-label com a descrição");
  confere(await pg.evaluate(() => { const a = document.querySelector("#pn-mes").getBoundingClientRect(), b = document.querySelector("#pn-q").getBoundingClientRect(); return b.top >= a.bottom - 1; }), "390: mês e busca ficam em duas linhas");
  confere(await pg.evaluate(() => [...document.querySelectorAll("dialog.painel-mov .pm-v")].every((v) => { const r = v.getBoundingClientRect(), p = v.closest(".pm").getBoundingClientRect(); return r.right <= p.right + 1 && r.left >= p.left; })), "390: valor sempre visível à direita da linha");
  await cap("painel_a_pagar_390");
  await pg.click("dialog.painel-mov .pn-volta"); await dormir(150);
  confere(!(await pnAberto()), "390: Voltar fecha o painel");
  await pg.tap('.nm[data-pn="saldo"]'); await dormir(250);
  confere((await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth)) <= 0, "390 saldo: sem rolagem lateral");
  await cap("painel_saldo_390");
  await pg.goBack(); await dormir(200);
  confere(!(await pnAberto()), "390: o botão voltar do sistema fecha o painel");
  confere(!errosJs.length, "painel 390: sem erro de JS", errosJs);
  await pg.evaluate(() => localStorage.clear());
}

async function real() {
  console.log("\n== dados REAIS (nenhum valor é impresso)");
  const out = path.join(APP, "dados", "capturas");
  fs.mkdirSync(out, { recursive: true });
  let ok = true;
  try { execFileSync(PY, [path.join(REPO, "estudio", "dados", "gerar_financas.py")], { stdio: "ignore" }); } catch { ok = false; }
  confere(ok, "real: gerador rodou");
  const meses = JSON.parse(fs.readFileSync(path.join(APP, "dados", "financas.json"), "utf8")).meses_disponiveis || [""];
  confere(meses.length >= 1, `real: ${meses.length} mês(es) disponível(is) no arquivo`);
  for (const mes of meses) for (const L of [1440, 390]) {
    if (pg) await pg.close();
    pg = await nav.newPage(); errosJs = [];
    pg.on("pageerror", (e) => errosJs.push(String(e.message || e)));
    pg.on("console", (m) => { if (m.type() === "error") errosJs.push(m.text()); });
    await pg.setViewport({ width: L, height: L < 600 ? 844 : 900 });
    await pg.goto(pathToFileURL(path.join(APP, "index.html")).href + (mes ? `#mes=${mes}` : ""), { waitUntil: "load" }); await dormir(700);
    const secoes = await pg.evaluate(() => document.querySelectorAll("main section.cartao").length);
    const ok2 = mes ? await selMes() === mes : true;
    confere(errosJs.length === 0, `real ${mes} ${L}px: sem erro de JS`, errosJs);
    confere(ok2 && secoes >= 3 && !(await texto()).includes("Não consegui ler"), `real ${mes} ${L}px: tela renderizou o mês (${secoes} seções)`);
    confere((await overflow()) <= 0, `real ${mes} ${L}px: sem rolagem lateral`);
    await pg.screenshot({ path: path.join(out, `financas_real_${mes || "unico"}_${L}.png`), fullPage: true });
  }
  console.log(`  capturas reais em ${out}`);
}

try { await principal(); } catch (e) { console.log("ERRO no teste:", e); falhas.push("exceção"); }
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`\n${passou} ok, ${falhas.length} falhas. Capturas dos cenários inventados: ${CAPT}`);
if (falhas.length) { console.log("Falhas:\n- " + falhas.join("\n- ")); process.exit(1); }
