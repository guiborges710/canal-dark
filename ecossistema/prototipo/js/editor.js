/* Ecossistema: mapa, editor de agentes, editor de fluxos, configuração, consumo, saúde e engenharia de IA. */
(function () {
  "use strict";
  var H = window.H, S = window.S, D = window.D, esc = H.esc, est = H.est, us = H.us, $ = H.$, $$ = H.$$, ACT = H.ACT, clone = H.clone;
  var painel = function (t, corpo, dir, cls) { return '<section class="painel ' + (cls || "") + '"><header><h2>' + t + "</h2>" + (dir || "") + "</header>" + corpo + "</section>"; };
  var btn = function (r, act, extra, cls) { return '<button class="btn ' + (cls || "") + '" data-act="' + act + '" ' + (extra || "") + ">" + r + "</button>"; };
  var hash = function (s) { var h = 5381, i; for (i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return (h >>> 0).toString(16).slice(0, 7); };
  var quando = function () { var d = new Date(); return "11/11 " + String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0"); };
  var SECRETO = /(sk-[A-Za-z0-9_-]{10,}|api[_-]?key\s*[:=]\s*\S+|token\s*[:=]\s*\S{6,}|senha\s*[:=]\s*\S+|password\s*[:=]\s*\S+)/i;

  var ABAS = [["mapa", "Mapa"], ["agentes", "Agentes"], ["fluxos", "Fluxos"], ["config", "Configuração"], ["consumo", "Consumo e custos"], ["conexoes", "Saúde e conexões"], ["engenharia", "Engenharia de IA"]];

  /* ---------- agentes: estado ---------- */
  var salvos = H.store.get("ag", {});
  var base = function (a) { return { desc: a[5], modelo: a[3], tools: D.TOOLKIT[a[4]].slice(), prompt: D.agentePrompt(a) }; };
  var agente = function (id) { return D.agentesBase.find(function (a) { return a[0] === id; }); };
  var atual = function (id) { var s = salvos[id]; return s ? s.versoes[s.versoes.length - 1].dados : base(agente(id)); };
  var versoes = function (id) { return salvos[id] ? salvos[id].versoes : [{ n: 1, q: "10/11 08:00", nota: "Versão do arquivo .claude/agents/" + id + ".md", dados: base(agente(id)) }]; };
  var rascunho = function (id) { S.rasc = S.rasc || {}; return (S.rasc[id] = S.rasc[id] || clone(atual(id))); };
  var texto = function (id, d) { return "---\nname: " + id + "\ndescription: " + d.desc + "\ntools: " + d.tools.join(", ") + "\nmodel: " + d.modelo + "\n---\n" + d.prompt; };
  var valida = function (d) {
    var e = [];
    if ((d.desc || "").trim().length < 5) e.push("A descrição precisa de pelo menos 5 caracteres.");
    if (!(d.prompt || "").trim()) e.push("As instruções (prompt) não podem ficar vazias.");
    if (D.MODELOS.indexOf(d.modelo) < 0) e.push("Modelo desconhecido. Use haiku, sonnet ou opus.");
    d.tools.forEach(function (t) { if (D.FERRAMENTAS_PERMITIDAS.indexOf(t) < 0) e.push("Ferramenta não permitida: " + t + "."); });
    if (SECRETO.test(d.desc + " " + d.prompt)) e.push("O texto contém algo que parece credencial. Chaves ficam só no .env.");
    return e;
  };
  var usos = function (nome) { var r = []; Object.keys(D.fluxos).forEach(function (k) { D.fluxos[k].nos.forEach(function (n) { if ((n.a || "").indexOf(nome) >= 0) r.push(D.fluxos[k].nome + ": " + n.r); }); }); return r; };

  var viewAgentes = function () {
    var f = (S.agBusca || "").toLowerCase(), st = S.agSetor || "todos", sel = S.agSel || "olise-diretor-arte";
    var lista = D.agentesBase.filter(function (a) { return (st === "todos" || a[2] === st) && (!f || (a[1] + a[0] + a[5]).toLowerCase().indexOf(f) >= 0); });
    var a = agente(sel), dr = rascunho(sel), vs = versoes(sel), sujo = JSON.stringify(dr) !== JSON.stringify(atual(sel)), errs = valida(dr), u = usos(a[1]);
    var esq = '<div class="pilha p"><div class="linha"><label class="vh" for="ag-b">Buscar agente</label><input id="ag-b" type="search" placeholder="Buscar por nome ou função" value="' + esc(S.agBusca || "") + '" data-inp="agBusca" style="flex:1"><label class="vh" for="ag-s">Setor</label><select id="ag-s" data-chg="agSetor" style="max-width:140px"><option value="todos">Todos</option>' + D.setores.map(function (s) { return '<option value="' + s.id + '"' + (s.id === st ? " selected" : "") + ">" + s.nome + "</option>"; }).join("") + '</select></div><div class="pilha p" style="max-height:640px;overflow:auto" id="ag-lista" role="list">' + lista.map(function (x) {
      return '<button class="agente" role="listitem" data-act="selAg" data-id="' + x[0] + '" aria-pressed="' + (x[0] === sel) + '"><span class="avatar" aria-hidden="true">' + x[1].split(" ").map(function (p) { return p[0]; }).join("").slice(0, 2) + '</span><span class="grow"><b>' + esc(x[1]) + '</b> <span class="chip">' + atual(x[0]).modelo + '</span><br><span class="mudo pequeno">' + esc(x[0]) + "</span></span></button>";
    }).join("") + (lista.length ? "" : '<div class="tela-estado"><h2>Nenhum agente encontrado</h2><p>Mude a busca ou o setor.</p></div>') + "</div></div>";
    var form = '<div class="pilha"><div class="linha entre"><div><h2>' + esc(a[1]) + '</h2><span class="mono mudo pequeno">.claude/agents/' + esc(a[0]) + '.md, base ' + hash(texto(sel, atual(sel))) + '</span></div><div class="linha">' + btn("Testar (teto US$ 1,00)", "testaAg", "", "peq") + btn("Duplicar", "dupAg", "", "peq") + btn("Desativar", "desAg", "", "peq perigo") + "</div></div>" +
      '<label class="campo">Descrição<textarea rows="2" data-inp="agCampo" data-c="desc">' + esc(dr.desc) + '</textarea></label>' +
      '<div class="campo">Modelo<div class="linha" role="group" aria-label="Modelo">' + D.MODELOS.map(function (m) { return '<button class="chip" type="button" data-act="agModelo" data-m="' + m + '" aria-pressed="' + (dr.modelo === m) + '">' + m + "</button>"; }).join("") + '<small>Só entre os modelos que já existem.</small></div></div>' +
      '<div class="campo">Ferramentas<div class="linha" role="group" aria-label="Ferramentas">' + D.FERRAMENTAS_PERMITIDAS.map(function (t) { return '<button class="chip mono" type="button" data-act="agTool" data-t="' + esc(t) + '" aria-pressed="' + (dr.tools.indexOf(t) >= 0) + '">' + esc(t) + "</button>"; }).join("") + "</div><small>Ferramentas novas (Bash com outros comandos) não entram por aqui.</small></div>" +
      '<label class="campo">Instruções (prompt)<textarea rows="12" class="cod" data-inp="agCampo" data-c="prompt">' + esc(dr.prompt) + "</textarea></label>" +
      '<div id="ag-val">' + valHtml(errs, sujo) + '</div><div class="linha"><button class="btn pri" id="ag-save" data-act="agSalvar"' + (sujo && !errs.length ? "" : " disabled") + ">Ver diferenças e salvar</button>" + btn("Descartar edição", "agDescarta", sujo ? "" : "disabled") + '</div><p class="pequeno mudo" style="margin:0">Vale para os próximos jobs. O que já está rodando usa a foto do agente de quando começou. Depois de salvar, rode a sincronização do Codex.</p>' +
      (u.length ? '<p class="pequeno mudo" style="margin:0">Em uso em: ' + u.map(esc).join("; ") + "</p>" : "") +
      painel("Versões (" + vs.length + ")", '<ul class="lista">' + vs.slice().reverse().map(function (v, i) { return "<li><b>v" + v.n + '</b><span class="grow"><span class="pequeno">' + esc(v.nota) + '</span><br><span class="mudo pequeno">' + v.q + '</span></span>' + (i ? btn("Comparar", "agComp", 'data-n="' + v.n + '"', "peq") + btn("Restaurar", "agRest", 'data-n="' + v.n + '"', "peq") : '<span class="chip">atual</span>') + "</li>"; }).join("") + "</ul>", "", "s") + "</div>";
    return '<div class="ed-grid">' + painel("Agentes (" + D.agentesBase.length + ")", esq, "", "s") + painel("Editor", form) + "</div>";
  };
  function valHtml(errs, sujo) { return errs.length ? '<div class="nota lj" role="alert"><p><b>Corrija antes de salvar:</b></p><ul style="margin:4px 0 0 18px;padding:0">' + errs.map(function (e) { return "<li>" + esc(e) + "</li>"; }).join("") + "</ul></div>" : sujo ? '<div class="nota am"><p>Mudanças não salvas. Nada vale até você salvar.</p></div>' : '<div class="nota"><p>Sem mudanças.</p></div>'; }
  var atualizaVal = function () { var id = S.agSel || "olise-diretor-arte", dr = rascunho(id), sujo = JSON.stringify(dr) !== JSON.stringify(atual(id)), errs = valida(dr); $("#ag-val").innerHTML = valHtml(errs, sujo); $("#ag-save").disabled = !(sujo && !errs.length); };
  ACT.agBusca = function (t) { S.agBusca = t.value; var pos = t.selectionStart; H.rerender(); var n = $("#ag-b"); if (n) { n.focus(); n.setSelectionRange(pos, pos); } };
  ACT.agSetor = function (t) { S.agSetor = t.value; H.rerender(); };
  ACT.agCampo = function (t) { rascunho(S.agSel || "olise-diretor-arte")[t.dataset.c] = t.value; atualizaVal(); };
  ACT.selAg = function (a) { S.agSel = a.dataset.id; H.rerender(); };
  ACT.agModelo = function (a) { rascunho(S.agSel || "olise-diretor-arte").modelo = a.dataset.m; H.rerender(); };
  ACT.agTool = function (a) { var d = rascunho(S.agSel || "olise-diretor-arte"), i = d.tools.indexOf(a.dataset.t); if (i >= 0) d.tools.splice(i, 1); else d.tools.push(a.dataset.t); H.rerender(); };
  ACT.agDescarta = function () { delete S.rasc[S.agSel || "olise-diretor-arte"]; H.rerender(); };
  var gravaAg = function (id, dados, nota) {
    var ant = salvos[id] ? clone(salvos[id]) : null, vs = versoes(id);
    salvos[id] = { versoes: vs.concat([{ n: vs.length + 1, q: quando(), nota: nota, dados: clone(dados) }]) }; H.store.set("ag", salvos); delete S.rasc[id];
    return function () { if (ant) salvos[id] = ant; else delete salvos[id]; H.store.set("ag", salvos); H.rerender(); };
  };
  ACT.agSalvar = function () {
    var id = S.agSel || "olise-diretor-arte", dr = rascunho(id);
    H.modal({ titulo: "Revisar mudanças em " + agente(id)[1], corpo: H.diffHtml(texto(id, atual(id)), texto(id, dr)) + '<label class="campo">Nota da versão<input type="text" id="ag-nota" placeholder="Por que mudou? (opcional)"></label><div class="nota"><p>Vale para os próximos jobs. Depois de salvar, <code>tools/sincronizar_codex.py</code> atualiza o espelho do Codex.</p></div>',
      botoes: [{ r: "Voltar" }, { r: "Salvar versão", cls: "pri", fn: function () { var u = gravaAg(id, dr, $("#ag-nota").value.trim() || "Edição pelo sistema"); H.rerender(); H.toast("Salvo como nova versão. Falta sincronizar o Codex.", function () { u(); }); } }] });
  };
  ACT.agComp = function (a) { var id = S.agSel || "olise-diretor-arte", v = versoes(id).find(function (x) { return x.n === +a.dataset.n; }); H.modal({ titulo: "Versão " + v.n + " contra a atual", corpo: H.diffHtml(texto(id, v.dados), texto(id, atual(id))) }); };
  ACT.agRest = function (a) { var id = S.agSel || "olise-diretor-arte", v = versoes(id).find(function (x) { return x.n === +a.dataset.n; }); H.modal({ titulo: "Restaurar versão " + v.n, corpo: "<p>Isso grava uma <b>nova</b> versão igual à antiga. O histórico não é apagado.</p>" + H.diffHtml(texto(id, atual(id)), texto(id, v.dados)), botoes: [{ r: "Cancelar" }, { r: "Restaurar", cls: "pri", fn: function () { var u = gravaAg(id, v.dados, "Restaurada a versão " + v.n); H.rerender(); H.toast("Versão " + v.n + " restaurada como nova versão.", function () { u(); }); } }] }); };
  ACT.testaAg = function () { var a = agente(S.agSel || "olise-diretor-arte"); H.novoJob(a[1] + ": teste isolado", "agente", "Claude", atual(a[0]).modelo, 1); };
  ACT.dupAg = function () { H.toast("Cópia criada como \"" + agente(S.agSel || "olise-diretor-arte")[1] + " (cópia)\", sem uso em fluxos."); };
  ACT.desAg = function () {
    var a = agente(S.agSel || "olise-diretor-arte"), u = usos(a[1]);
    if (u.length) { H.modal({ titulo: "Não dá para desativar " + a[1], corpo: '<div class="nota lj"><p>Está em uso em: ' + u.map(esc).join("; ") + ". Tire o agente dos fluxos antes.</p></div>" }); return; }
    H.confirmar({ titulo: "Desativar " + a[1], corpo: "<p>O arquivo vai para <code>.claude/agents_desativados/</code>.</p>", rotulo: "Desativar", fn: function () { H.toast("Agente desativado (simulado)."); } });
  };

  /* ---------- fluxos ---------- */
  S.fl = S.fl || {};
  var fl = function (id) { if (!S.fl[id]) { var n = clone(D.fluxos[id].nos); S.fl[id] = { rasc: clone(n), pub: n, vers: [{ n: 1, q: "10/11 08:00", nos: clone(n), nota: "Fluxo atual" }], undo: [] }; } return S.fl[id]; };
  var linhas = function (nos) { return nos.map(function (n) { return n.id + " | " + n.t + " | " + n.r + " | " + (n.a || "-") + " | depende: " + (n.d.join(",") || "nada"); }).join("\n"); };
  var nomesAg = function () { var r = { "você": 1, "": 1 }; D.agentesBase.forEach(function (a) { r[a[1]] = 1; }); return r; };
  var validaFl = function (nos) {
    var e = [], av = [], ids = {}, nomes = nomesAg();
    nos.forEach(function (n) { if (ids[n.id]) e.push("Passo repetido: " + n.id + "."); ids[n.id] = n; });
    nos.forEach(function (n) {
      n.d.forEach(function (d) { if (!ids[d]) e.push("\"" + n.r + "\" depende de um passo que não existe (" + d + ")."); });
      if (!n.r.trim()) e.push("Um passo está sem nome.");
      if (n.t === "agent") { (n.a || "").split(" / ").forEach(function (x) { if (!x.trim()) e.push("\"" + n.r + "\" é passo de agente e está sem agente."); else if (!nomes[x.trim()]) av.push("\"" + n.r + "\": " + x.trim() + " não existe em .claude/agents."); }); }
      if (n.t === "gate" && !n.d.length && nos.length > 1 && n.id !== "gui" && n.id !== "ped") av.push("A decisão \"" + n.r + "\" não tem passo anterior.");
    });
    var seen = {}, pilha = {}, ciclo = false;
    var dfs = function (id) { if (!ids[id]) return; if (pilha[id]) { ciclo = true; return; } if (seen[id]) return; seen[id] = 1; pilha[id] = 1; ids[id].d.forEach(dfs); pilha[id] = 0; };
    nos.forEach(function (n) { dfs(n.id); }); if (ciclo) e.push("O fluxo tem um ciclo: um passo depende dele mesmo.");
    var anc = function (n, f, vis) { vis = vis || {}; return n.d.some(function (d) { if (!ids[d] || vis[d]) return false; vis[d] = 1; return f(ids[d]) || anc(ids[d], f, vis); }); };
    if (!ciclo) nos.forEach(function (n) {
      if (n.a === "run.py video" && !anc(n, function (x) { return x.r === "Auditoria de texto"; })) e.push("Regra do canal: nenhum render sem a auditoria de texto aprovada antes (\"" + n.r + "\").");
      if (/Publicar/.test(n.r) && n.t === "gate" && !anc(n, function (x) { return x.r === "Auditoria final"; })) e.push("Regra do canal: publicar exige a auditoria final antes.");
    });
    nos.forEach(function (n) { if (nos.length > 1 && !n.d.length && !nos.some(function (m) { return m.d.indexOf(n.id) >= 0; })) av.push("\"" + n.r + "\" está solto, sem ligação com nenhum passo."); });
    return { e: e, av: av };
  };
  var paralelos = function (nos) {
    var cam = {}, byId = {}; nos.forEach(function (n) { byId[n.id] = n; });
    var nv = function (n, d) { if (d > 40) return 0; if (cam[n.id] != null) return cam[n.id]; var l = 0; n.d.forEach(function (x) { if (byId[x]) l = Math.max(l, nv(byId[x], d + 1) + 1); }); return (cam[n.id] = l); };
    nos.forEach(function (n) { nv(n, 0); }); var g = {}; nos.forEach(function (n) { (g[cam[n.id]] = g[cam[n.id]] || []).push(n.r); });
    return Object.keys(g).filter(function (k) { return g[k].length > 1; }).map(function (k) { return g[k]; });
  };
  var viewFluxos = function () {
    var id = S.flSel || "canal", f = fl(id), v = validaFl(f.rasc), sujo = linhas(f.rasc) !== linhas(f.pub), par = paralelos(f.rasc);
    var opcoesAg = Object.keys(nomesAg()).filter(Boolean).sort().map(function (n) { return '<option value="' + esc(n) + '">'; }).join("");
    var rows = f.rasc.map(function (n, i) {
      return "<tr><td><label class=\"vh\" for=\"r" + i + "\">Nome do passo " + (i + 1) + '</label><input id="r' + i + '" type="text" value="' + esc(n.r) + '" data-chg="flCampo" data-i="' + i + '" data-c="r"></td><td><label class="vh" for="t' + i + '">Tipo</label><select id="t' + i + '" data-chg="flCampo" data-i="' + i + '" data-c="t"><option value="agent"' + (n.t === "agent" ? " selected" : "") + '>Agente</option><option value="code"' + (n.t === "code" ? " selected" : "") + '>Código</option><option value="gate"' + (n.t === "gate" ? " selected" : "") + '>Decisão sua</option></select></td><td><label class="vh" for="a' + i + '">Agente</label><input id="a' + i + '" type="text" list="dl-ag" value="' + esc(n.a) + '" data-chg="flCampo" data-i="' + i + '" data-c="a"' + (n.t === "gate" ? " disabled" : "") + '></td><td><details><summary>' + (n.d.length ? n.d.length + " passo(s)" : "nada") + "</summary>" + f.rasc.filter(function (m) { return m.id !== n.id; }).map(function (m) { return '<label class="linha pequeno" style="font-weight:400"><input type="checkbox" style="width:16px;height:16px" data-chg="flDep" data-i="' + i + '" data-d="' + m.id + '"' + (n.d.indexOf(m.id) >= 0 ? " checked" : "") + ">" + esc(m.r) + "</label>"; }).join("") + '</details></td><td><button class="btn peq perigo" data-act="flRem" data-i="' + i + '" aria-label="Remover passo ' + esc(n.r) + '">Remover</button></td></tr>';
    }).join("");
    return '<div class="pilha g"><div class="linha"><label for="fl-sel" class="vh">Fluxo</label><select id="fl-sel" data-chg="flSel" style="max-width:380px">' + Object.keys(D.fluxos).map(function (k) { return '<option value="' + k + '"' + (k === id ? " selected" : "") + ">" + D.fluxos[k].nome + "</option>"; }).join("") + "</select>" + (sujo ? '<span class="estado espera">Rascunho com mudanças</span>' : '<span class="estado ok">Igual ao publicado (v' + f.vers.length + ")</span>") + "</div>" +
      painel("Diagrama do rascunho", H.fluxoSvg(f.rasc, {}, { id: id }), par.length ? '<span class="pequeno mudo">Em paralelo: ' + par.map(function (g) { return g.map(esc).join(" + "); }).join("; ") + "</span>" : "") +
      painel("Passos", '<datalist id="dl-ag">' + opcoesAg + '</datalist><div class="rolar"><table><thead><tr><th>Passo</th><th>Tipo</th><th>Agente</th><th>Depende de</th><th></th></tr></thead><tbody>' + rows + '</tbody></table></div><div class="linha" style="margin-top:10px">' + btn("Adicionar passo", "flAdd", "", "peq") + btn("Desfazer", "flDesfaz", f.undo.length ? "" : "disabled", "peq") + '</div><p class="pequeno mudo" style="margin:8px 0 0">Passos que dependem dos mesmos anteriores rodam em paralelo. A ordem vem das dependências.</p>') +
      painel("Validação", (v.e.length ? '<div class="nota lj" role="alert"><p><b>Erros (impedem publicar):</b></p><ul style="margin:4px 0 0 18px;padding:0">' + v.e.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : '<div class="nota"><p>Nenhum erro.</p></div>') + (v.av.length ? '<div class="nota am" style="margin-top:8px"><p><b>Avisos:</b></p><ul style="margin:4px 0 0 18px;padding:0">' + v.av.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : ""), '<div class="linha">' + btn("Ver diferenças e publicar", "flPub", v.e.length || !sujo ? "disabled" : "", "pri") + "</div>") +
      painel("Versões publicadas", '<ul class="lista">' + f.vers.slice().reverse().map(function (x, i) { return "<li><b>v" + x.n + '</b><span class="grow"><span class="pequeno">' + esc(x.nota) + '</span><br><span class="mudo pequeno">' + x.q + "</span></span>" + (i ? btn("Restaurar no rascunho", "flRest", 'data-n="' + x.n + '"', "peq") : '<span class="chip">atual</span>') + "</li>"; }).join("") + '</ul><p class="pequeno mudo" style="margin:8px 0 0">Uma execução em andamento guarda a foto do fluxo de quando começou: a edição vale para as próximas.</p>', "", "s") + "</div>";
  };
  var snap = function (f) { f.undo.push(clone(f.rasc)); if (f.undo.length > 30) f.undo.shift(); };
  ACT.flSel = function (t) { S.flSel = t.value; H.rerender(); };
  ACT.flCampo = function (t) { var f = fl(S.flSel || "canal"), n = f.rasc[+t.dataset.i]; snap(f); n[t.dataset.c] = t.value; if (t.dataset.c === "t" && t.value === "gate") n.a = "você"; H.rerender(); };
  ACT.flDep = function (t) { var f = fl(S.flSel || "canal"), n = f.rasc[+t.dataset.i], i = n.d.indexOf(t.dataset.d); snap(f); if (t.checked && i < 0) n.d.push(t.dataset.d); if (!t.checked && i >= 0) n.d.splice(i, 1); H.rerender(); };
  ACT.flAdd = function () { var f = fl(S.flSel || "canal"); snap(f); var ult = f.rasc[f.rasc.length - 1]; f.rasc.push({ id: "n" + Date.now() % 100000, t: "agent", r: "Novo passo", a: "", d: ult ? [ult.id] : [] }); H.rerender(); };
  ACT.flRem = function (a) { var f = fl(S.flSel || "canal"), n = f.rasc[+a.dataset.i]; snap(f); f.rasc.splice(+a.dataset.i, 1); f.rasc.forEach(function (m) { m.d = m.d.filter(function (x) { return x !== n.id; }); }); H.rerender(); };
  ACT.flDesfaz = function () { var f = fl(S.flSel || "canal"); if (f.undo.length) { f.rasc = f.undo.pop(); H.rerender(); H.toast("Última mudança desfeita."); } };
  ACT.flPub = function () {
    var id = S.flSel || "canal", f = fl(id);
    H.modal({ titulo: "Publicar nova versão do fluxo", corpo: H.diffHtml(linhas(f.pub), linhas(f.rasc)) + '<label class="campo">Nota<input type="text" id="fl-nota" placeholder="O que mudou?"></label><p class="pequeno mudo">Vale para as próximas produções. As que estão rodando seguem no fluxo antigo até você migrar.</p>', botoes: [{ r: "Voltar" }, { r: "Publicar", cls: "pri", fn: function () { var ant = { pub: clone(f.pub), vers: clone(f.vers) }; f.pub = clone(f.rasc); f.vers.push({ n: f.vers.length + 1, q: quando(), nos: clone(f.rasc), nota: $("#fl-nota").value.trim() || "Edição pelo sistema" }); D.fluxos[id].nos = clone(f.rasc); H.rerender(); H.toast("Fluxo publicado como v" + f.vers.length + ".", function () { f.pub = ant.pub; f.vers = ant.vers; f.rasc = clone(ant.pub); D.fluxos[id].nos = clone(ant.pub); H.rerender(); }); } }] });
  };
  ACT.flRest = function (a) { var f = fl(S.flSel || "canal"), v = f.vers.find(function (x) { return x.n === +a.dataset.n; }); snap(f); f.rasc = clone(v.nos); H.rerender(); H.toast("Versão " + v.n + " carregada no rascunho. Publique para valer."); };

  /* ---------- configuração ---------- */
  var cfg0 = { max_usd: 0, retries: 2, privacy: "private", maxdia: 2, vel: 1.0, hora: "18:00", pordia: 1 };
  S.cfg = S.cfg || { salvo: clone(cfg0), rasc: clone(cfg0), vers: [{ n: 1, q: "10/11 08:00", nota: "Arquivo atual" }] };
  var yaml = function (c) { return "budget:\n  max_usd_per_video: " + c.max_usd + "\n  max_retries_per_step: " + c.retries + "\npublish:\n  privacy: " + c.privacy + "\ncompliance:\n  max_videos_per_day: " + c.maxdia + "\nvoz:\n  velocidade: " + c.vel + "\ncronograma:\n  hora: \"" + c.hora + "\"\n  videos_por_dia: " + c.pordia + "\n"; };
  var validaCfg = function (c) {
    var e = [];
    if (!(+c.max_usd >= 0)) e.push("max_usd_per_video precisa ser 0 ou mais."); if (!(+c.retries >= 0 && +c.retries <= 5)) e.push("max_retries_per_step: de 0 a 5.");
    if (["private", "unlisted", "public"].indexOf(c.privacy) < 0) e.push("publish.privacy: private, unlisted ou public."); if (!(+c.maxdia >= 1 && +c.maxdia <= 5)) e.push("max_videos_per_day: de 1 a 5.");
    if (!(+c.vel >= 0.5 && +c.vel <= 1.5)) e.push("voz.velocidade: de 0,5 a 1,5."); if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(c.hora)) e.push("cronograma.hora: formato HH:MM."); if (+c.pordia > +c.maxdia) e.push("videos_por_dia passa do limite de conformidade (max_videos_per_day).");
    return e;
  };
  S.claude = S.claude || { salvo: D.claudeSecoes.map(function (s) { return s.t; }), rasc: D.claudeSecoes.map(function (s) { return s.t; }), vers: [{ n: 1, q: "10/11 08:00", nota: "Arquivo atual" }] };
  var CAD = [["Resumo diário no Telegram (Ronaldo)", "08:30", "lembretes.json"], ["Aviso antes de cada compromisso", "60", "lembretes.json (minutos antes)"], ["Daily da programação (Xavi)", "10:30", "lembretes.json (ainda não cadastrado)"], ["Postagem de Shorts", "18:00", "config_shorts.yaml, seção cronograma"], ["Referências virais (Memphis)", "semanal", "sob demanda"]];
  S.cad = S.cad || CAD.map(function (c) { return c[1]; });
  var viewConfig = function () {
    var c = S.cfg.rasc, ev = validaCfg(c), sujo = yaml(c) !== yaml(S.cfg.salvo), cs = S.claude, sujoC = cs.rasc.join("\n§\n") !== cs.salvo.join("\n§\n");
    var campo = function (rot, k, tipo, extra, aviso) { return '<label class="campo">' + rot + '<input type="' + tipo + '" value="' + esc(c[k]) + '" data-chg="cfgCampo" data-k="' + k + '" ' + (extra || "") + ">" + (aviso ? "<small>" + aviso + "</small>" : "") + "</label>"; };
    return '<div class="pilha g"><div class="nota am"><p><b>Estes dois arquivos mandam em tudo.</b> Salvar exige digitar "confirmo". O sistema grava só as chaves alteradas e mantém os comentários do arquivo.</p></div>' +
      painel("config_shorts.yaml", '<div class="grade">' + campo("Orçamento por vídeo (US$)", "max_usd", "number", 'step="0.1" min="0"', "Travado: mexer aqui libera gasto pago.") + campo("Novas tentativas por etapa", "retries", "number", 'min="0" max="5"') + '<label class="campo">Publicação: privacidade<select data-chg="cfgCampo" data-k="privacy">' + ["private", "unlisted", "public"].map(function (p) { return "<option" + (c.privacy === p ? " selected" : "") + ">" + p + "</option>"; }).join("") + "</select><small>Travado: public tira a revisão manual no Studio.</small></label>" + campo("Limite de vídeos por dia", "maxdia", "number", 'min="1" max="5"') + campo("Velocidade da voz", "vel", "number", 'step="0.05" min="0.5" max="1.5"') + campo("Hora da postagem", "hora", "text", 'placeholder="18:00"') + campo("Vídeos por dia (cronograma)", "pordia", "number", 'min="1" max="5"') + "</div>" +
        (c.privacy === "public" ? '<div class="nota lj" style="margin-top:10px"><p>Atenção: com <code>public</code>, o vídeo sobe aberto. A regra atual é sempre privado.</p></div>' : "") + (ev.length ? '<div class="nota lj" role="alert" style="margin-top:10px"><ul style="margin:0 0 0 18px;padding:0">' + ev.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" : "") +
        '<div class="linha" style="margin-top:12px">' + btn("Revisar e salvar", "cfgSalvar", sujo && !ev.length ? "" : "disabled", "pri") + btn("Descartar", "cfgDesc", sujo ? "" : "disabled") + '<span class="mudo pequeno">Trecho de exemplo do arquivo. Versão atual: v' + S.cfg.vers.length + "</span></div>", btn("Desfazer última versão", "cfgDesfaz", S.cfg.vers.length > 1 ? "" : "disabled", "peq")) +
      painel("CLAUDE.md, por seções", '<div class="nota"><p>O arquivo é carregado em todo job de agente (18.952 caracteres medidos). Edite só o que precisa; texto novo custa em cada execução.</p></div><div class="pilha" style="margin-top:12px">' + D.claudeSecoes.map(function (s, i) { return '<label class="campo">' + s.n + (s.inegociavel ? ' <span class="chip">regra inegociável: pede motivo</span>' : "") + '<textarea rows="4" class="cod" data-chg="claudeCampo" data-i="' + i + '">' + esc(cs.rasc[i]) + "</textarea></label>"; }).join("") + '</div><div class="linha" style="margin-top:12px">' + btn("Revisar e salvar", "claudeSalvar", sujoC ? "" : "disabled", "pri") + btn("Desfazer última versão", "claudeDesfaz", cs.vers.length > 1 ? "" : "disabled") + '<span class="mudo pequeno">Versão atual: v' + cs.vers.length + "</span></div>") +
      painel("Cadências", '<div class="rolar"><table><thead><tr><th>Rotina</th><th>Valor</th><th>Onde grava</th></tr></thead><tbody>' + CAD.map(function (r, i) { return "<tr><td>" + r[0] + '</td><td><label class="vh" for="cad' + i + '">' + r[0] + '</label><input id="cad' + i + '" type="text" value="' + esc(S.cad[i]) + '" data-chg="cadCampo" data-i="' + i + '" style="max-width:120px"></td><td class="mudo pequeno">' + r[2] + "</td></tr>"; }).join("") + '</tbody></table></div><p class="pequeno mudo" style="margin:8px 0 0">Aqui só mudam os lembretes e o cronograma. Tarefas do Agendador do Windows não são editadas pela tela: o estado aparece em Saúde e conexões, com o comando para copiar.</p>') +
      painel("Prompts do canal", '<ul class="lista">' + ["writer.md", "angle.md", "reviewer.md", "metadata.md", "tipos_de_roteiro.md"].map(function (p) { return "<li><code>prompts/" + p + '</code><span class="grow"></span>' + btn("Editar", "promptEd", 'data-p="' + p + '"', "peq") + "</li>"; }).join("") + "</ul>", "", "s") + "</div>";
  };
  ACT.cfgCampo = function (t) { S.cfg.rasc[t.dataset.k] = t.type === "number" ? (t.value === "" ? "" : +t.value) : t.value; H.rerender(); };
  ACT.cfgDesc = function () { S.cfg.rasc = clone(S.cfg.salvo); H.rerender(); };
  ACT.cfgSalvar = function () {
    var c = S.cfg;
    H.confirmar({ titulo: "Salvar config_shorts.yaml", corpo: H.diffHtml(yaml(c.salvo), yaml(c.rasc)) + (c.rasc.max_usd !== c.salvo.max_usd || c.rasc.privacy !== c.salvo.privacy ? '<div class="nota lj"><p>Você está mudando um campo travado (orçamento ou privacidade).</p></div>' : ""), rotulo: "Salvar", fn: function () { var ant = { s: clone(c.salvo), v: clone(c.vers) }; c.salvo = clone(c.rasc); c.vers.push({ n: c.vers.length + 1, q: quando(), nota: "Edição pelo sistema" }); H.rerender(); H.toast("config_shorts.yaml salvo (v" + c.vers.length + ").", function () { c.salvo = ant.s; c.rasc = clone(ant.s); c.vers = ant.v; H.rerender(); }); } });
  };
  ACT.cfgDesfaz = function () { var c = S.cfg; c.vers.pop(); c.salvo = clone(cfg0); c.rasc = clone(cfg0); H.rerender(); H.toast("Voltou para a versão anterior."); };
  ACT.claudeCampo = function (t) { S.claude.rasc[+t.dataset.i] = t.value; H.rerender(); };
  ACT.claudeSalvar = function () {
    var cs = S.claude, ineg = D.claudeSecoes.some(function (s, i) { return s.inegociavel && cs.rasc[i] !== cs.salvo[i]; });
    var d = D.claudeSecoes.map(function (s, i) { return cs.rasc[i] !== cs.salvo[i] ? "## " + s.n + "\n" + H.diffHtml(cs.salvo[i], cs.rasc[i]) : ""; }).join("");
    H.confirmar({ titulo: "Salvar CLAUDE.md", corpo: d + (ineg ? '<div class="nota lj"><p>Você mudou uma regra inegociável (YouTube, fatos, congelamento).</p></div><label class="campo">Motivo (obrigatório)<input type="text" id="cl-mot"></label>' : ""), rotulo: "Salvar", fn: function () { if (ineg && !($("#cl-mot") && $("#cl-mot").value.trim())) { H.toast("Escreva o motivo da mudança na regra inegociável."); return false; } var ant = { s: cs.salvo.slice(), v: clone(cs.vers) }; cs.salvo = cs.rasc.slice(); cs.vers.push({ n: cs.vers.length + 1, q: quando(), nota: "Edição pelo sistema" }); H.rerender(); H.toast("CLAUDE.md salvo (v" + cs.vers.length + ").", function () { cs.salvo = ant.s; cs.rasc = ant.s.slice(); cs.vers = ant.v; H.rerender(); }); } });
  };
  ACT.claudeDesfaz = function () { var cs = S.claude; cs.vers.pop(); cs.salvo = D.claudeSecoes.map(function (s) { return s.t; }); cs.rasc = cs.salvo.slice(); H.rerender(); H.toast("Voltou para a versão anterior do CLAUDE.md."); };
  ACT.cadCampo = function (t) { var i = +t.dataset.i, v = t.value.trim(), ant = S.cad[i]; if (!v) { t.value = ant; H.toast("Valor vazio não vale."); return; } H.modal({ titulo: "Mudar cadência", corpo: H.diffHtml(CAD[i][0] + ": " + ant, CAD[i][0] + ": " + v) + '<p class="pequeno mudo">Grava em ' + CAD[i][2] + ". Vale a partir da próxima execução.</p>", botoes: [{ r: "Cancelar", fn: function () { H.rerender(); } }, { r: "Salvar cadência", cls: "pri", fn: function () { S.cad[i] = v; H.rerender(); H.toast("Cadência atualizada.", function () { S.cad[i] = ant; H.rerender(); }); } }] }); };
  ACT.promptEd = function (a) { H.modal({ titulo: "prompts/" + a.dataset.p, corpo: '<textarea rows="10" class="cod" aria-label="Conteúdo do prompt">Você escreve o roteiro de um Short de 30 a 60 s. Situação concreta antes de dado. Gancho no frame 0, nunca com estatística. No máximo 2 números e 1 gráfico. Tese em uma frase.</textarea><p class="pequeno mudo">Usa o mesmo mecanismo de versão, diff e desfazer dos agentes.</p>', botoes: [{ r: "Cancelar" }, { r: "Ver diferenças", cls: "pri", fn: function () { H.toast("Diferenças geradas (simulado)."); } }] }); };

  /* ---------- mapa, consumo, saúde, engenharia ---------- */
  var viewMapa = function () {
    var total = D.agentesBase.length;
    return '<div class="pilha g"><div class="nota"><p>Contagem lida da lista de agentes: <b>' + total + " agentes</b> em " + D.setores.length + " setores. O texto do README ainda diz 42; o sistema sempre mostra a contagem real.</p></div>" +
      '<div class="grade">' + D.setores.map(function (s) { var n = D.agentesBase.filter(function (a) { return a[2] === s.id; }); return '<section class="painel"><header><h2>' + s.nome + "</h2>" + est(s.ativo ? "ok" : "fila", s.ativo ? "Setor ativo" : "Sob demanda") + "</header><p class=\"mudo\">" + s.desc + '</p><p class="pequeno">Chefe: <b>' + s.chefe + "</b>. " + n.length + ' agentes.</p><div class="linha">' + n.map(function (a) { return '<button class="chip" data-act="abrirAg" data-id="' + a[0] + '">' + esc(a[1]) + "</button>"; }).join("") + '</div><p style="margin:10px 0 0"><a href="#/' + s.id + '">Abrir setor</a></p></section>'; }).join("") + "</div>" +
      painel("Fluxo de mudanças de agente e setor", H.fluxoSvg(D.fluxos.ecossistema.nos, { ped: "ok", val: "ok", luiz: "ok", ap: "espera", cod: "bloq" }, { id: "ecossistema" })) +
      painel("O que o mapa ainda precisa corrigir", '<ul class="lista"><li>Firmino existe como agente e não consta em setores.json.</li><li>Pirlo, Totti, Figo e Roberto Carlos estão no cadastro e faltam no README do mapa.</li><li>Reels e Finanças ainda aparecem agrupados em outros setores no arquivo atual.</li><li>Kane e Memphis ainda não têm pasta de saída documentada.</li></ul>', "", "s") + "</div>";
  };
  var viewConsumo = function () {
    var tot = D.consumo.reduce(function (s, x) { return s + x.v; }, 0);
    return '<div class="pilha g"><div class="nota am"><p><b>Os valores abaixo são de exemplo.</b> O custo real por job só é conhecido por <code>custo.json</code> e <code>.ronaldo_custo.jsonl</code>. Nenhuma sugestão de trocar modelo sai sem medição.</p></div><div class="grade dois">' +
      painel("Hoje por agente (total " + us(tot) + ")", H.barrasH(D.consumo.map(function (x) { return { n: x.n, v: x.v }; }), function (v) { return us(v); })) +
      painel("Tetos configurados", '<ul class="lista">' + D.tetos.map(function (t) { return "<li>" + t.n + '<span class="grow"></span><b>' + t.v + "</b></li>"; }).join("") + '</ul><div style="margin-top:10px">' + btn("Pedir mudança de teto", "tetoPed", "", "peq") + '</div><p class="pequeno mudo" style="margin:8px 0 0">Mudar teto é decisão sua (A8) e grava em configuração.</p>') + "</div>" +
      painel("Modelos em uso", '<div class="linha">' + ["haiku", "sonnet", "opus"].map(function (m) { return '<span class="chip">' + m + ": " + D.agentesBase.filter(function (a) { return atual(a[0]).modelo === m; }).length + "</span>"; }).join("") + '</div><p class="pequeno mudo" style="margin:8px 0 0">Raphinha é o único em opus. Cada job headless recarrega o CLAUDE.md e a definição do agente.</p>', "", "s") + "</div>";
  };
  ACT.tetoPed = function () { H.modal({ titulo: "Mudar teto de custo", corpo: '<label class="campo">Qual teto<select><option>Inteligência por dia</option><option>De Bruyne pelo Telegram</option><option>Mensagem comum do Ronaldo</option></select></label><label class="campo">Novo valor (US$)<input type="number" step="0.1" min="0" value="1.10"></label>', botoes: [{ r: "Cancelar" }, { r: "Ver diferença", cls: "pri", fn: function () { H.toast("Diferença mostrada; salvar exige o \"confirmo\" da configuração (simulado)."); } }] }); };
  var viewSaude = function () {
    var sv = D.saude;
    return '<div class="pilha g"><div class="nota"><p><b>Este é um protótipo.</b> Os dados são de exemplo e nenhum botão chama de verdade um agente, o YouTube, o Trello ou o Telegram. A seção de limites mostra o que o sistema real <b>não</b> consegue fazer.</p></div>' +
      '<div class="grade dois">' + painel("Conexões", '<ul class="lista">' + D.conexoes.map(function (c) { return "<li><span class=\"grow\"><b>" + c.n + '</b><br><span class="mudo pequeno">' + c.d + "</span></span>" + est(c.e, c.e === "bloq" ? "Não conectado" : c.e === "espera" ? "Vence em breve" : "Conectado") + "</li>"; }).join("") + "</ul>") +
      painel("Servidores e agendador", '<ul class="lista">' + sv.servidores.map(function (s) { return "<li><b>" + s.n + '</b><span class="grow mudo pequeno">porta ' + s.p + "</span>" + est(s.e, "Ligado") + "</li>"; }).join("") + sv.agendador.map(function (s) { return "<li><code>" + s.n + '</code><span class="grow mudo pequeno">' + s.i + "</span>" + est(s.e, s.e === "pausa" ? "Desligada" : "Ativa") + "</li>"; }).join("") + '</ul><div class="linha" style="margin-top:10px">' + btn("Copiar comando de verificação", "copiaVer", "", "peq") + btn("Verificar espelho do Codex", "rodaCmd", 'data-c="python tools/sincronizar_codex.py --verificar"', "peq") + "</div>") + "</div>" +
      painel("Limites reais do sistema", '<ul class="lista">' + D.limites.map(function (l) { return "<li><span class=\"grow\"><b>" + l[0] + '</b><br><span class="mudo">' + l[1] + "</span></span></li>"; }).join("") + "</ul>") +
      painel("Reserva Codex", "<p style=\"margin:0\">O Codex só refaz o trabalho de agente quando o Claude esgota o limite (5 horas, semanal ou de uso). Enquanto o Claude estiver disponível, nunca é usado. Cada job mostra o selo do motor; não existe botão para forçar o Codex.</p>", "", "s") +
      painel("Demonstrar estados de tela", '<p class="mudo" style="margin:0 0 8px">Mostra como cada tela aparece vazia, carregando, com erro ou bloqueada.</p><div class="linha" role="group" aria-label="Estado de demonstração">' + [["normal", "Normal"], ["carregando", "Carregando"], ["vazio", "Vazio"], ["erro", "Erro"], ["bloqueado", "Bloqueado"]].map(function (x) { return '<button class="chip" aria-pressed="' + (S.demo === x[0]) + '" data-act="demoSet" data-v="' + x[0] + '">' + x[1] + "</button>"; }).join("") + "</div>", "", "s") + "</div>";
  };
  ACT.copiaVer = function () { H.copiar("schtasks /query /fo LIST | findstr ContextoExplica", "Comando copiado."); };
  ACT.demoSet = function (a) { S.demo = a.dataset.v; var s = $("#demo-sel"); if (s) s.value = a.dataset.v; H.rerender(); };
  var viewEng = function () {
    return '<div class="pilha g"><div class="nota"><p>O Valverde só propõe. Cada proposta abre o editor já com o texto sugerido; nada é gravado sem o diff e a sua confirmação.</p></div>' + painel("Propostas", '<ul class="lista">' + D.propostas.map(function (p) { return "<li><b class=\"mono\">" + p.id + "</b><span class=\"grow\"><b>" + p.t + '</b><br><span class="mudo pequeno">' + p.d + "</span></span>" + est(p.e === "Aguardando você" ? "espera" : "ok", p.e) + btn("Abrir", "ir", 'data-h="#/ecossistema/agentes"', "peq") + "</li>"; }).join("") + "</ul>", btn("Pedir diagnóstico ao Valverde", "rodaAg", 'data-a="Valverde"', "peq")) + painel("Desperdícios de token monitorados", '<ul class="lista"><li>Abrir tela nunca dispara agente.</li><li>Mesmo agente com a mesma entrada não roda de novo (hash).</li><li>Pedir ajuste reabre só o ramo afetado.</li><li>Ciclos automáticos só com teto diário.</li></ul>', "", "s") + "</div>";
  };

  H.views.ecossistema = function (s) {
    s = s || "mapa"; var c = { mapa: viewMapa, agentes: viewAgentes, fluxos: viewFluxos, config: viewConfig, consumo: viewConsumo, conexoes: viewSaude, engenharia: viewEng }[s] || viewMapa;
    return '<div class="cab"><div><h1>Ecossistema</h1><p>Agentes, setores, fluxos, configuração e custo. Chefe: Luiz Henrique. Segredos (.env, tokens) nunca aparecem aqui.</p></div></div>' + H.abas("ecossistema", ABAS, ABAS.some(function (a) { return a[0] === s; }) ? s : "mapa") + c();
  };
})();
