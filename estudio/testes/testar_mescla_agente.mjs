// Testes da mesclagem fiel do editor visual do painel (estudio/web/corte_agente_merge.js), sem navegador.
// Uso: node estudio/testes/testar_mescla_agente.mjs
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const M = createRequire(import.meta.url)(path.join(AQUI, "..", "web", "corte_agente_merge.js"));
let ok = 0; const falhas = [];
const igual = (a, b, nome) => { if (a === b) ok++; else { falhas.push(nome); console.log(`  FALHOU  ${nome}\n    esperado: ${JSON.stringify(b)}\n    obtido:   ${JSON.stringify(a)}`); } };

const original = "\n# Título\n\nTexto com `codigo` e pasta output/<slug>/.\nSegunda linha do mesmo parágrafo.\n\n- item um\n- item dois\n  continuação do item dois\n\n|a|b|\n|--|--|\n|1|2|\n\n~~~text\nbloco\n\n  recuado\n~~~\n";
// o que o editor devolveria sem ninguém mexer (forma canônica dele)
const base = "# Título\n\nTexto com `codigo` e pasta output/\\<slug>/. Segunda linha do mesmo parágrafo.\n\n* item um\n* item dois continuação do item dois\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n\n```text\nbloco\n\n  recuado\n```\n";

igual(M.mesclar(original, base, base), original, "sem editar: o arquivo volta idêntico");
igual(M.paraEditor(original).includes("\\<slug>") && M.paraEditor(original).includes("Texto com `codigo` e pasta output/\\<slug>/. Segunda linha"), true, "paraEditor protege <slug> e une a linha quebrada");
igual(M.paraEditor("use `<slug>` aqui\n\n```\n<slug>\n```\n"), "use `<slug>` aqui\n\n```\n<slug>\n```\n", "paraEditor não mexe em código inline nem em bloco de código");

const editado = base.replace("* item um", "* item UM editado");
igual(M.mesclar(original, base, editado), original.replace("- item um", "* item UM editado".replace("* ", "- ")), "item de lista editado: só ele muda e mantém o marcador do arquivo");

const tabela = base.replace("| 1 | 2 |", "| 1 | 99 |");
igual(M.mesclar(original, base, tabela), original.replace("|1|2|", "| 1 | 99 |"), "célula de tabela editada: o resto da tabela fica como estava");

const novoPar = base.replace("# Título\n", "# Título\n\nParágrafo novo.\n");
igual(M.mesclar(original, base, novoPar), original.replace("# Título\n", "# Título\n\nParágrafo novo.\n"), "parágrafo inserido entra no lugar certo");

const semItem = base.replace("* item um\n", "");
igual(M.mesclar(original, base, semItem), original.replace("- item um\n", ""), "item removido some, o resto fica");

const paragrafo = base.replace("Segunda linha do mesmo parágrafo.", "Segunda linha MUDADA.");
const r = M.mesclar(original, base, paragrafo);
igual(r.includes("output/<slug>/") && !r.includes("\\<") && r.includes("Segunda linha MUDADA."), true, "parágrafo editado: <slug> volta como estava no arquivo, sem barra");

igual(M.mesclar("a\n", "a\n", "b\n"), "b\n", "texto simples");
igual(M.mesclar("a\r\nb\r\n", "a\n\nb\n", "a\n\nb\n"), "a\nb\n", "CRLF é normalizado para LF (a gravação cuida do resto)");
console.log(`${ok} verificações ok, ${falhas.length} falhas.`);
if (falhas.length) process.exitCode = 1;
