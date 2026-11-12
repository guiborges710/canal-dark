// PROG-003 (entrega 1): aba Agentes > Ao vivo. Chrome real, servidor numa cópia descartável com o claude simulado (sem rede, sem custo).
// Parte com o servidor de verdade (estado vazio, job falho e job concluído gravados no banco temporário); os demais casos usam
// respostas roteirizadas da mesma rota, para controlar estados, falhas e o relógio. Uso: node estudio/testes/e2e_agentes_ao_vivo.mjs [pasta de capturas]
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
const CAPTURAS = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "ao-vivo-capturas-"));
fs.mkdirSync(CAPTURAS, { recursive: true });

const caixa = fs.mkdtempSync(path.join(os.tmpdir(), "ao-vivo-caixa-"));
fs.rmSync(caixa, { recursive: true });
const ambiente = JSON.parse(execFileSync(PY, [path.join(AQUI, "preparar_caixa.py"), caixa], { encoding: "utf-8" }));
fs.cpSync(path.join(REPO, ".claude", "agents"), path.join(caixa, ".claude", "agents"), { recursive: true });
// Agentes de cada etapa vêm do fluxo, nunca de ids fixos.
const [OLISE, NEYMAR, MBAPPE] = JSON.parse(execFileSync(PY, ["-c", "import json;from estudio import fluxo;print(json.dumps([fluxo.POR_ID[i]['agente'] for i in ('cenas','roteiro','metadados')]))"], { cwd: REPO, encoding: "utf-8", env: { ...process.env, ...ambiente } }));

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

function gravarJobs(jobs) {
  const codigo = "import os,sqlite3,json,sys\nfrom datetime import datetime, timedelta\nc=sqlite3.connect(os.environ['ESTUDIO_DADOS']+'/estudio.db')\nn=datetime.now()\nts=lambda s:(n-timedelta(seconds=s)).isoformat(timespec='seconds') if s is not None else None\n"
    + "for j in json.loads(sys.argv[1]):\n c.execute(\"INSERT INTO jobs (slug,etapa,raia,titulo,craque,assinatura,status,spec,erro,dispensado,criada_em,iniciado_em,terminado_em) VALUES (?,?,?,?,?,?,?,?,?,0,?,?,?)\",(j['slug'],j['etapa'],'agente',j['titulo'],'X',j['titulo']+str(j['ini']),j['status'],json.dumps({'tipo':'agente','raia':'agente','agente':j['agente']}),j.get('erro'),ts(j['ini']),ts(j['ini']),ts(j.get('term'))))\nc.commit()";
  execFileSync(PY, ["-c", codigo, JSON.stringify(jobs)], { env: { ...process.env, ...ambiente } });
}

// ---- respostas roteirizadas da rota (mesmo contrato do back) ----
const TEXTO = { trabalhando: "Trabalhando", fila: "Na fila", falhou: "Falhou", espera_voce: "Espera você" };
const trab = (o = {}) => ({ job_id: 1, slug: SLUG, titulo_video: "Fim dos terceiros lugares", etapa_id: "cenas", etapa_nome: "Cenas", estado: "trabalhando", motor: "claude", motor_nota: null, segundos_na_tarefa: 128, aguarda_s: null, posicao_fila: null, erro_curto: null, origem: "grafo", alerta_longo: false, ...o });
const ag = (id, craque, estado, trabalhos, extra = {}) => ({ id, craque, ativo: true, estado, estado_texto: TEXTO[estado], trabalhos, ...extra });
function resp(agentes, concl = [], extra = {}) {
  const resumo = { trabalhando: 0, fila: 0, falhou: 0, espera_voce: 0, ignorados: 0 };
  agentes.forEach((a) => { resumo[a.estado]++; });
  return { gerado_em: "1999-01-01T00:00:00", servidor_s: 1, resumo, agentes, concluidos_1h: concl, frescor: "ok", ...extra };
}
const MISTO = () => resp([
  ag(OLISE, "Olise", "falhou", [trab({ job_id: 5, estado: "falhou", segundos_na_tarefa: null, erro_curto: "Tempo esgotado no motor", motor: "claude" })]),
  ag(NEYMAR, "Neymar", "espera_voce", [trab({ job_id: null, etapa_id: "roteiro", etapa_nome: "Roteiro", estado: "espera_voce", segundos_na_tarefa: null, aguarda_s: 300, motor: null })]),
  ag(MBAPPE, "Mbappé", "trabalhando", [trab({ job_id: 7, etapa_id: "metadados", etapa_nome: "Metadados", motor: "codex", motor_nota: "Executado pelo Codex: o Claude estava no limite.", segundos_na_tarefa: 55 })], { ativo: false }),
  ag("vini-auditor-conformidade", "Vini", "fila", [trab({ job_id: 8, etapa_id: "auditoria_texto", etapa_nome: "Auditoria de texto", estado: "fila", segundos_na_tarefa: null, aguarda_s: 40, posicao_fila: 2 })]),
], [{ agente: NEYMAR, craque: "Neymar", slug: SLUG, etapa_nome: "Notas", motor: "claude", terminou_ha_s: 900 }]);
async function usar(corpo) { modo = corpo ? { tipo: "json", corpo } : { tipo: "real" }; await agora(); await dormir(150); }

async function porRota() {
  console.log("\n[1] Servidor de verdade: vazio, falhou e concluído");
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.querySelector("#ag-vazio"), null), "Sem trabalho: aparece 'Nenhum agente trabalhando agora.'");
  confere((await txt("#ag-vazio")).includes("Quando uma produção rodar, ela aparece aqui sozinha."), "Estado vazio explica o que acontece depois");
  confere((await txt("#ag-vazio")).includes("Ir para Projetos") && (await txt("#ag-vazio")).includes("Ver o Catálogo"), "Estado vazio oferece Projetos e Catálogo");
  confere(await pagina.evaluate(() => !document.querySelector(".ag-cartao") && !/undefined|null|NaN/.test(document.getElementById("ag-vivo").innerText)), "Vazio: nenhum cartão e nenhum 'undefined/null/NaN'");
  confere((await txt("#ag-resumo")) === "Nenhum agente em atividade.", "Resumo do vazio", await txt("#ag-resumo"));
  confere(await pagina.evaluate(() => document.getElementById("nav-agentes-selo").classList.contains("vazio")), "Menu: sem selo quando não há nada");
  confere(await pagina.evaluate(() => document.getElementById("ag-resumo").getAttribute("aria-live") === "polite"), "Resumo é região aria-live polite");

  gravarJobs([{ slug: SLUG, etapa: "cenas", titulo: "Cenas", status: "falhou", agente: OLISE, erro: "Tempo esgotado no motor\nlinha dois que não deve aparecer", ini: 300, term: 200 },
    { slug: SLUG, etapa: "roteiro", titulo: "Roteiro", status: "ok", agente: NEYMAR, ini: 700, term: 600 }]);
  confere(await espera(() => document.querySelector('[data-agente-vivo][data-estado="falhou"]'), null, 7000), "Atualiza sozinho, sem recarregar: job falho gravado no banco aparece");
  const c = await txt('[data-estado="falhou"]');
  confere(c.includes("Falhou em Cenas: Tempo esgotado no motor") && !c.includes("linha dois"), "Falhou: etapa e só a primeira linha do motivo", c);
  confere(c.includes("Ver o que houve"), "Falhou: botão 'Ver o que houve'");
  confere(await pagina.evaluate(() => document.querySelector("#nav-agentes-selo .nav-selo-marca").innerText.trim() === "!"), "Menu: selo '!' e texto para leitor de tela");
  confere(await pagina.evaluate(() => document.getElementById("nav-agentes-selo").textContent.includes("Agentes: 1 falhou")), "Menu: texto de leitor de tela 'Agentes: 1 falhou'", await txt("#nav-agentes-selo"));
  confere((await txt("#ag-concluidos summary")).includes("Concluídos na última hora (1)"), "Concluídos na última hora (1)");
  confere(await pagina.evaluate(() => document.getElementById("ag-concluidos").open === false), "Concluídos começa recolhido");
  confere((await txt("#aba-ao-vivo")) === "Ao vivo (!)", "Aba com indicador '(!)'", await txt("#aba-ao-vivo"));
}

async function estados() {
  console.log("\n[2] Estados, seções e motor");
  await usar(MISTO());
  confere(await espera(() => document.querySelectorAll(".ag-cartao").length === 4, null), "Quatro cartões (um por agente)", await contar(".ag-cartao"));
  confere((await contar("#ag-sec-atencao .ag-cartao")) === 2 && (await contar("#ag-sec-agora .ag-cartao")) === 2, "Atenção (falhou + espera você) e Agora (trabalhando + fila)");
  confere(await pagina.evaluate(() => [...document.querySelectorAll("#ag-sec-atencao .ag-cartao")].map((x) => x.dataset.estado).join() === "falhou,espera_voce"), "Atenção: falhou antes de espera você");
  confere(await pagina.evaluate(() => [...document.querySelectorAll("#ag-sec-agora .ag-cartao")].map((x) => x.dataset.estado).join() === "trabalhando,fila"), "Agora: trabalhando antes da fila");
  confere((await txt("#ag-resumo")) === "1 trabalhando · 1 na fila · 1 falhou · 1 espera você", "Resumo, sem zeros", await txt("#ag-resumo"));
  const estadosTxt = await pagina.evaluate(() => [...document.querySelectorAll(".ag-cartao .estado")].map((e) => e.innerText.trim()).join("|"));
  confere(["Falhou", "Espera você", "Trabalhando", "Na fila"].every((t) => estadosTxt.includes(t)), "Cada estado tem ícone e palavra", estadosTxt);
  const espera_ = await txt('[data-estado="espera_voce"]');
  confere(espera_.includes("Abrir para decidir") && espera_.includes("aguardando você há 5 min") && !/Motor/.test(espera_), "Espera você: botão, tempo desde o fim do último job, sem motor inventado", espera_);
  const trabalhando = await txt('[data-estado="trabalhando"]');
  confere(trabalhando.includes("Etapa: Metadados") && trabalhando.includes("há 55 s") && trabalhando.includes("Codex") && trabalhando.includes("Desativado: termina o trabalho atual"), "Trabalhando: etapa, tempo, motor Codex e aviso de desativado", trabalhando);
  confere(trabalhando.includes("o Claude estava no limite"), "Nota do motor aparece (seloMotor do PROG-006)");
  confere(await existe('[data-estado="trabalhando"] .selo-motor.codex button.chip-motor'), "Chip Codex é um botão tocável");
  const fila = await txt('[data-estado="fila"]');
  confere(fila.includes("2º da fila") && fila.includes("aguarda há 40 s"), "Fila: posição e espera", fila);
  confere(await pagina.evaluate(() => !!document.querySelector("[data-agente-vivo][aria-label]") && /Mbappé, trabalhando, vídeo .*, etapa Metadados.*Codex/.test(document.querySelector('[data-estado="trabalhando"]').getAttribute("aria-label"))), "Cartão tem aria-label completo", await pagina.evaluate(() => document.querySelector('[data-estado="trabalhando"]').getAttribute("aria-label")));
  confere(await pagina.evaluate(() => !/undefined|\bnull\b|NaN/.test(document.getElementById("ag-vivo").innerText)), "Nenhum 'undefined', 'null' ou 'NaN' na tela");
  confere(await pagina.evaluate(() => { const d = document.getElementById("ag-concluidos"); return d && !d.open && d.innerText.includes("Concluídos na última hora (1)"); }), "Concluídos recolhido, com contagem");
  await pagina.click("#ag-concluidos summary");
  confere((await txt("#ag-concluidos")).includes("Neymar: Notas") && (await txt("#ag-concluidos")).includes("há 15 min"), "Concluídos expandido: quem, etapa e há quanto tempo");
  confere(await pagina.evaluate(() => document.getElementById("nav-agentes-selo").textContent.includes("1 trabalhando · 1 na fila · 1 falhou · 1 espera você")), "Menu: leitor de tela lê o resumo completo");
  confere(await pagina.evaluate(() => { const s = document.getElementById("nav-agentes-selo"); return s.getAttribute("aria-live") === "polite" && s.querySelector(".nav-selo-marca").innerText.trim() === "!"; }), "Menu: selo aria-live polite e '!' visível quando algo falhou");
  await pagina.screenshot({ path: path.join(CAPTURAS, "ao-vivo-misto.png") });

  console.log("  -- vários vídeos para o mesmo agente");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab({ job_id: 1, slug: "um", titulo_video: "Vídeo um" }), trab({ job_id: 2, slug: "dois", titulo_video: "Vídeo dois", etapa_nome: "Cenas" })])]));
  await espera(() => document.querySelectorAll(".ag-trabalho").length === 2, null);
  confere((await contar(".ag-cartao")) === 1 && (await txt(".ag-cartao")).includes("Trabalhando em 2 vídeos"), "Dois vídeos: um cartão com lista", await txt(".ag-cartao"));
  confere((await contar('.ag-trabalho a[data-estudio]')) === 2, "Cada vídeo tem o seu 'Abrir no Estúdio'");

  console.log("  -- teste de agente");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab({ slug: "__agentes__", titulo_video: "__agentes__", etapa_id: "teste", etapa_nome: "Teste de agente", origem: "teste_agente" })])]));
  await espera(() => document.querySelector("[data-ver-teste]"), null);
  confere((await txt(".ag-cartao")).includes("Teste de agente") && !(await existe("[data-estudio]")), "Teste de agente: rotulado 'teste' e sem link para um Estúdio que não existe", await txt(".ag-cartao"));

  console.log("  -- alerta de tempo longo e job antigo sem motor");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab({ segundos_na_tarefa: 960, alerta_longo: true, motor: null })])]));
  const longo = await txt(".ag-cartao");
  confere(longo.includes("há 16 min: mais que o normal") && await existe(".ag-tempo.longo"), "Depois de 15 min: 'mais que o normal'", longo);
  confere(!/Claude|Codex/.test(longo), "Job antigo sem motor: nenhum selo e nenhum 'undefined'", longo);
}

async function contadorEAtualizacao() {
  console.log("\n[3] Contador local e atualização sem recarregar");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab({ segundos_na_tarefa: 55 })])]));
  const antes = await txt(".ag-tempo"), pedidosAntes = pedidos;
  await dormir(2600);
  const depois = await txt(".ag-tempo");
  confere(antes === "há 55 s" && depois !== antes && /^há (5[7-9]|1) ?(s|min)/.test(depois) && pedidos === pedidosAntes, "O tempo avança sozinho, sem nova consulta ao servidor", { antes, depois, novasConsultas: pedidos - pedidosAntes });
  confere(await pagina.evaluate(() => !/1999/.test(document.body.innerText)), "A tela não interpreta datas do servidor (gerado_em de 1999 não aparece)");

  console.log("  -- atualização pelo polling de 4 s, sem recarregar");
  modo = { tipo: "json", corpo: resp([ag(NEYMAR, "Neymar", "trabalhando", [trab({ job_id: 9, etapa_id: "roteiro", etapa_nome: "Roteiro", segundos_na_tarefa: 3 })])]) };
  const marca = await pagina.evaluate(() => { window.__marca = "mesma-pagina"; return true; });
  confere(await espera(() => document.querySelector('[data-agente-vivo] b')?.textContent === "Neymar", null, 7000), "Mudança de estado aparece em até um ciclo de polling");
  confere(await pagina.evaluate(() => window.__marca === "mesma-pagina") && marca, "Sem recarregar a página");

  console.log("  -- não redesenha se nada mudou");
  await usar(resp([ag(NEYMAR, "Neymar", "trabalhando", [trab({ job_id: 9, etapa_id: "roteiro", etapa_nome: "Roteiro", segundos_na_tarefa: 3 })])]));
  await pagina.evaluate(() => { document.querySelector(".ag-cartao").dataset.marca = "x"; });
  await agora(); await dormir(150);
  confere(await pagina.evaluate(() => document.querySelector(".ag-cartao").dataset.marca === "x"), "Mesma resposta (só o relógio muda): o cartão não é refeito");
}

async function falhaDeConsulta() {
  console.log("\n[4] Consulta com erro: mantém o último estado");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab({ segundos_na_tarefa: 100 })])]));
  modo = { tipo: "500" };
  await agora();
  confere(await espera(() => document.querySelector("#ag-faixa-msg")?.innerText.includes("Sem atualização desde"), null), "Faixa 'Sem atualização desde ...'", await txt("#ag-faixa"));
  const f = await txt("#ag-faixa");
  confere(f.includes("Mostrando o último estado conhecido.") && f.includes("Tentar agora"), "Faixa explica e oferece 'Tentar agora'", f);
  confere(/Sem atualização desde \d\d:\d\d \(há \d+ s\)/.test(f), "Faixa traz a hora e há quanto tempo", f);
  confere(await existe('[data-agente-vivo][data-estado="trabalhando"]'), "O último estado conhecido continua na tela");
  const t1 = await txt(".ag-tempo");
  confere(t1.includes("(pode ter mudado)"), "Contador ganha '(pode ter mudado)'", t1);
  await dormir(2200);
  confere((await txt(".ag-tempo")) === t1, "Contador para de avançar enquanto está desatualizado", [t1, await txt(".ag-tempo")]);
  confere(await pagina.evaluate(() => document.getElementById("ag-faixa-msg").classList.contains("ag-faixa-velha") && !document.getElementById("ag-faixa-msg").classList.contains("ag-faixa-falha")), "Desatualizada é âmbar, não vermelha");
  await pagina.screenshot({ path: path.join(CAPTURAS, "ao-vivo-desatualizado.png") });

  console.log("  -- volta ao normal");
  modo = { tipo: "json", corpo: resp([ag(OLISE, "Olise", "trabalhando", [trab({ segundos_na_tarefa: 110 })])]) };
  await pagina.click("#ag-tentar");
  confere(await espera(() => document.querySelector("#ag-faixa-msg")?.innerText.trim() === "Atualizado.", null, 3000), "Ao voltar: faixa verde 'Atualizado.'");
  confere(await espera(() => !document.querySelector("#ag-faixa-msg"), null, 5000), "A faixa verde some em cerca de 3 s");
  confere(!(await txt(".ag-tempo")).includes("pode ter mudado"), "O sufixo some e o contador volta a andar");

  console.log("  -- servidor fora do ar");
  modo = { tipo: "queda" };
  await agora();
  confere(await espera(() => document.querySelector("#ag-faixa-msg")?.innerText.includes("Sem atualização"), null), "Queda curta: ainda a faixa âmbar");
  await pagina.evaluate(() => { Vivo.redeDesde = Date.now() - 31000; });
  confere(await espera(() => document.querySelector("#ag-faixa-msg.ag-faixa-falha"), null, 3000), "Mais de 30 s sem resposta: faixa vermelha");
  confere((await txt("#ag-faixa-msg")).includes("O Corte não responde. Verifique se a janela do Corte ainda está aberta no computador."), "Texto da faixa vermelha", await txt("#ag-faixa-msg"));
  confere(await existe('[data-agente-vivo]'), "Mesmo fora do ar, o último estado continua visível");
  modo = { tipo: "json", corpo: resp([]) };
  await pagina.click("#ag-tentar");
  confere(await espera(() => document.querySelector("#ag-vazio"), null, 3000), "Servidor de volta: a tela atualiza");
  modo = { tipo: "real" };
}

async function primeiraFalha() {
  console.log("\n[5] Primeira consulta com erro (sem estado anterior)");
  modo = { tipo: "500" };
  await pagina.evaluate(() => { Vivo.dados = null; Vivo.recebido = 0; Vivo.ultimoOk = 0; });
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.querySelector("#ag-sem-dados"), null), "Sem dados e com erro: mensagem honesta, sem dizer 'ninguém trabalhando'");
  confere(!(await existe("#ag-vazio")) && (await txt("#ag-faixa")).includes("Tentar agora"), "Não afirma 'Nenhum agente trabalhando' e oferece tentar de novo", await txt("#ag-faixa"));
  modo = { tipo: "real" };
}

async function parcial() {
  console.log("\n[6] Frescor parcial e muitos trabalhos");
  await usar(resp([ag(OLISE, "Olise", "trabalhando", [trab()])], [], { frescor: "parcial" }));
  await espera(() => document.getElementById("ag-faixa")?.innerText.includes("incompleta"), null, 5000);
  confere((await txt("#ag-faixa")).includes("pode estar incompleta"), "Frescor 'parcial' avisa que 'Espera você' pode estar incompleto", await txt("#ag-faixa"));
  const muitos = Array.from({ length: 22 }, (_, i) => ag(`agente-${i}`, `Agente ${i}`, "fila", [trab({ job_id: 100 + i, slug: `video-${i}`, titulo_video: `Vídeo ${i}`, estado: "fila", segundos_na_tarefa: null, aguarda_s: 10 + i, posicao_fila: i + 1 })]));
  await usar(resp(muitos));
  confere((await contar("#ag-sec-agora .ag-cartao")) === 10, "50 trabalhos: no máximo 10 cartões por seção", await contar("#ag-sec-agora .ag-cartao"));
  confere((await txt("[data-ver-todos]")) === "+12 na fila, ver todos", "Botão '+12 na fila, ver todos'", await txt("[data-ver-todos]"));
  await pagina.click("[data-ver-todos]");
  confere((await contar("#ag-sec-agora .ag-cartao")) === 22 && !(await existe("[data-ver-todos]")), "'Ver todos' expande a lista inteira");
}

async function navegacao() {
  console.log("\n[7] Cliques, abas e rotas");
  await usar(MISTO());
  await pagina.click('[data-estado="trabalhando"] [data-estudio]');
  confere(await espera((s) => location.pathname === `/estudio/${s}`, SLUG, 4000), "Clicar em 'Abrir no Estúdio' leva ao Estúdio do vídeo", await pagina.evaluate(() => location.pathname));
  confere(await espera(() => document.querySelector("#e-agentes .agente-linha"), null, 8000), "O Estúdio abre de verdade");
  confere((await pagina.evaluate(() => location.search)) === "?etapa=metadados", "O clique leva o id da etapa na URL (?etapa=metadados)", await pagina.evaluate(() => location.search));
  const foco = await espera(() => { const b = document.querySelector('#e-agentes [data-no="metadados"]'); return b && b.classList.contains("em-foco") && b.getAttribute("aria-current") === "step" && document.activeElement === b; }, null, 8000);
  confere(foco, "Critério 6: o Estúdio abre com o nó da etapa (metadados) em foco e destacado", await pagina.evaluate(() => document.querySelector("#e-agentes .em-foco")?.dataset.no || "nenhum nó em foco"));
  confere((await pagina.evaluate(() => document.querySelectorAll("#e-agentes .em-foco").length)) === 1, "Só um nó fica em foco");

  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  await usar(MISTO());
  await pagina.click('[data-estado="falhou"] [data-estudio]');
  confere(await espera((s) => location.pathname === `/estudio/${s}`, SLUG, 4000), "'Ver o que houve' também leva ao Estúdio");

  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  await usar(MISTO());
  await pagina.click('[data-estado="trabalhando"] [data-ficha]');
  confere(await espera((i) => location.pathname === `/agentes/${i}` && document.getElementById("ag-titulo")?.innerText === "Mbappé", MBAPPE, 5000), "'Ver ficha do agente' abre a ficha no Catálogo", await pagina.evaluate(() => location.pathname));

  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  confere((await pagina.evaluate(() => document.getElementById("aba-ao-vivo").getAttribute("aria-selected"))) === "true" && (await existe("#ag-vivo")), "/agentes abre Ao vivo");
  confere(!(await existe("#novo-agente")), "Ao vivo não tem '＋ Novo'");
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.querySelector("#ag-lista .ag-item"), null, 6000) && (await existe("#novo-agente")) && (await existe("#busca-agente")), "/agentes?aba=catalogo abre o Catálogo de hoje (lista, busca e '＋ Novo')");
  confere((await pagina.evaluate(() => document.getElementById("aba-catalogo").getAttribute("aria-selected"))) === "true", "Aba Catálogo marcada");
  await pagina.goto(`${BASE}/agentes/${OLISE}`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.getElementById("ag-titulo")?.innerText === "Olise", null, 6000) && (await existe("#ag-editar")) && (await existe("#ag-duplicar")), "/agentes/<id> segue abrindo a ficha (editar e duplicar presentes)");
  confere(await pagina.evaluate(() => document.getElementById("nav-agentes").classList.contains("ativo")), "Item Agentes do menu fica ativo");

  console.log("  -- abas por teclado");
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  await pagina.focus("#aba-ao-vivo");
  await pagina.keyboard.press("ArrowRight");
  confere(await espera(() => location.search === "?aba=catalogo" && document.activeElement?.id === "aba-catalogo", null, 3000), "Seta para a direita troca para o Catálogo e mantém o foco na aba");
  await pagina.keyboard.press("ArrowLeft");
  confere(await espera(() => location.pathname === "/agentes" && !location.search && document.activeElement?.id === "aba-ao-vivo", null, 3000), "Seta para a esquerda volta para Ao vivo");
  confere(await pagina.evaluate(() => document.getElementById("aba-catalogo").getAttribute("tabindex") === "-1" && document.querySelector('[role="tablist"]') !== null), "Abas com role tablist e tabindex roving");

  console.log("  -- tela de outro lugar também mostra o selo do menu");
  await usar(MISTO());
  await pagina.goto(`${BASE}/fluxos`, { waitUntil: "networkidle2" });
  confere(await espera(() => document.getElementById("nav-agentes-selo")?.textContent.includes("falhou"), null, 6000), "Fora da aba Agentes o selo do menu continua vivo");
  confere((await existe("#ag-vivo")) === false, "Nenhum resto da aba Ao vivo em outra tela");
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  await espera(() => /\(!\)/.test(document.getElementById("aba-ao-vivo")?.textContent), null, 6000);
  confere((await txt("#aba-ao-vivo")) === "Ao vivo (!)", "No Catálogo, a aba Ao vivo mostra '(!)' para a atividade não ficar escondida", await txt("#aba-ao-vivo"));
}

async function aba_oculta() {
  console.log("\n[8] Polling para quando a aba do navegador fica oculta");
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  await usar(resp([]));
  await pagina.evaluate(() => { Object.defineProperty(document, "hidden", { configurable: true, get: () => true }); document.dispatchEvent(new Event("visibilitychange")); });
  await dormir(400);
  const base = pedidos;
  await dormir(9500);
  confere(pedidos - base <= 1, "Com a aba oculta não há novas consultas (no máximo a que já estava agendada)", pedidos - base);
  await pagina.evaluate(() => { delete document.hidden; document.dispatchEvent(new Event("visibilitychange")); });
  confere(await espera((n) => true, null, 100) && (await dormir(300), pedidos - base) >= 1, "Ao voltar, consulta na hora");
  const n1 = pedidos; await dormir(4600);
  confere(pedidos - n1 >= 1, "E o polling de 4 s retoma", pedidos - n1);
}

async function celular() {
  console.log("\n[9] Celular (390 px)");
  await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await pagina.goto(`${BASE}/agentes`, { waitUntil: "networkidle2" });
  await usar(MISTO());
  await espera(() => document.querySelectorAll(".ag-cartao").length === 4, null);
  const m = await pagina.evaluate(() => {
    const cartoes = [...document.querySelectorAll(".ag-cartao")].map((c) => c.getBoundingClientRect());
    const botoes = [...document.querySelectorAll(".ag-cartao .btn")].map((b) => b.getBoundingClientRect().height);
    return { dentro: cartoes.every((r) => r.left >= 0 && r.right <= innerWidth + 1), rolagemLateral: document.documentElement.scrollWidth > innerWidth || document.getElementById("app").scrollWidth > innerWidth + 1, menorBotao: Math.min(...botoes), aba: document.getElementById("aba-ao-vivo").getBoundingClientRect().height, colunas: new Set(cartoes.map((r) => Math.round(r.left))).size };
  });
  confere(m.dentro && !m.rolagemLateral, "Cartões dentro da largura, sem rolagem lateral", m);
  confere(m.colunas === 1, "Uma coluna só", m);
  confere(m.menorBotao >= 44 && m.aba >= 44, "Botões e abas com pelo menos 44 px de altura", m);
  await pagina.tap('[data-estado="trabalhando"] button.chip-motor');
  confere((await txt('[data-estado="trabalhando"] .motor-dica')).includes("O Claude estava no limite"), "Tocar no chip Codex abre a explicação");
  await pagina.screenshot({ path: path.join(CAPTURAS, "ao-vivo-celular.png") });
  await pagina.goto(`${BASE}/agentes?aba=catalogo`, { waitUntil: "networkidle2" });
  await espera(() => document.querySelector("#ag-lista .ag-item"), null);
  confere(await pagina.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.getElementById("app").scrollWidth <= innerWidth + 1), "Catálogo no celular sem rolagem lateral");
  await pagina.setViewport({ width: 1500, height: 1000 });
}

try {
  servidor = spawn(PY, ["-m", "estudio", "--porta", String(PORTA), "--nao-abrir"], { cwd: REPO, env: { ...process.env, ...ambiente }, stdio: "ignore" });
  await esperarServidor();
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
      if (modo.tipo === "queda") return req.abort("failed");
    }
    req.continue();
  });
  await porRota();
  await estados();
  await contadorEAtualizacao();
  await falhaDeConsulta();
  await primeiraFalha();
  await parcial();
  await navegacao();
  await aba_oculta();
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
