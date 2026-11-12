"""PROG-018 a 023: confere o back-end do painel (estudio/painel.py) numa pasta temporária; nunca toca no repositório real.
Cobre confidencialidade, ordenação/mudança, path traversal, resumo, setores e rotas HTTP.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_painel.py"""
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="painel_"))
RAIZ = TMP / "raiz"
os.environ["ESTUDIO_RAIZ"] = str(RAIZ)
os.environ["ESTUDIO_DADOS"] = str(TMP / "dados")
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import painel as P  # noqa: E402

P.RAIZ = RAIZ
(TMP / "dados").mkdir()
passou, falhas = 0, []


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}", flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def w(rel, texto="# Titulo\ncorpo", mtime=None):
    p = RAIZ / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(texto.encode("utf-8") if isinstance(texto, str) else texto)
    if mtime:
        os.utime(p, (mtime, mtime))
    return p


def estado_limpo():
    P._docs.clear()
    P.invalidar()
    P._cache["indice"] = None


def lista():
    return P.varrer(forcar=True)


SEGREDO = "chave SUPERSECRETA"
agora = time.time()

print("[Confidencialidade]")
permitidos = ["CLAUDE.md", "README.md", "ecossistema/a.md", "ecossistema/setores.json", "programacao/quadro.md", "programacao/maestro/decisoes/PROG-001.json",
              "inteligencia/x.md", "componentes/c.md", "prompts/p.md", ".claude/agents/zico-po-programacao.md", ".claude/skills/s/SKILL.md",
              "output/meu-video/roteiro.txt", "produtividade/agenda.json", "produtividade/tarefas.md", "produtividade/acessos.md", "produtividade/README.md",
              "produtividade/.ronaldo_contexto.md", "produtividade/.ronaldo_contexto_pedri.md", "produtividade/linkedin/rascunhos.md", "financas/README.md", "financas/saldos.csv",
              "financas/pendencias.md", "programacao/acessos.md", ".claude/agents/casemiro-financeiro.md", "output/meu-video/metadados.json", "output/messi_assinatura_canal.md"]
proibidos = ["produtividade/.env", "produtividade/token_google.json", "produtividade/client_secret_x.json", "produtividade/.google_agenda_estado.json",
             "produtividade/.ronaldo_historico.json", "produtividade/.ronaldo_historico_pedri.json", "produtividade/.ronaldo.log", "produtividade/.ronaldo_custo.jsonl",
             "produtividade/.ronaldo_offset", "produtividade/.ronaldo_regras_tarefa.md", "produtividade/.feitos.json", "produtividade/.ronaldo_contexto/x.md",
             "produtividade/linkedin/.ronaldo_contexto.md", "financas/grafico.png", "financas/dashboard.html", "financas/.env", "programacao/dados.csv",
             ".env", ".env.local", "estudio/dados/senha_rede.txt", "estudio/dados/log.md", "voz/amostra.txt", "output/meu-video/falas/fala1.txt",
             "client_secret.json", "client_secret_123.json", ".youtube_token.json", "inteligencia/aprendiz/_entrada/x.md", "inteligencia/token_x.md",
             "ecossistema/chaves.key", ".venv/lib/x.md", ".git/config.json", "output/meu-video/video.mp4",
             "output/meu-video/corte_assets/a.json", "output/meu-video/sub/n.md", "src/codigo.md", "tools/x.md", "memory/m.md"]
for rel in permitidos + proibidos:
    w(rel, f"# {rel}\n{SEGREDO if rel in proibidos else 'ok'}")
estado_limpo()
ind = lista()
for rel in permitidos:
    confere(rel in ind, f"permitido entra: {rel}", sorted(ind))
for rel in proibidos:
    confere(rel not in ind, f"proibido fora do índice: {rel}")
api = json.dumps(P.documentos(limite=500)) + json.dumps(P.resumo()) + json.dumps(P.mudancas("0:0:0"))
confere(".env" not in api and "client_secret" not in api and "token_google" not in api and ".ronaldo_historico" not in api and ".google_agenda_estado" not in api, "API de lista/resumo/mudanças não cita arquivos de segredo")
confere(SEGREDO not in api, "conteúdo de arquivo proibido não aparece na API")
for rel in proibidos:
    d, cod = P.documento(rel)
    confere(cod == 404 and SEGREDO not in json.dumps(d), f"documento() recusa: {rel}")
confere(all(P.area_de(r) for r in permitidos) and not any(P.area_de(r) for r in proibidos), "area_de concorda com o índice")

print("[Credencial no corpo]")
w("ecossistema/cred.md", "# Cred\nusar sk-ant-api03-abcdefghijklmnopqrstuvwxyz")
w("ecossistema/cred2.md", "# Cred2\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz0123")
w("ecossistema/ok.md", "# Normal\ntexto sem nada de mais")
P.invalidar()
ind = lista()
d, cod = P.documento("ecossistema/cred.md")
confere(cod == 200 and d["conteudo"] is None and d["omitido"] and "credencial" in d["motivo_omitido"], "corpo com chave é omitido", d)
d, cod = P.documento("ecossistema/cred2.md")
confere(d["conteudo"] is None, "Bearer é omitido")
d, cod = P.documento("ecossistema/ok.md")
confere(d["conteudo"] and "sem nada" in d["conteudo"] and not d["omitido"], "documento normal abre")
confere("sk-ant" not in json.dumps(P.documentos(limite=500)) and "sk-ant" not in json.dumps(P.resumo()), "chave não vaza na lista nem no resumo")

print("[Path traversal]")
w("../fora.md", "# fora do repo\nSEGREDO_FORA")
for cam in ["../fora.md", "..\\fora.md", "ecossistema/../../fora.md", str(TMP / "fora.md"), "/etc/passwd", "C:\\Windows\\win.ini", "ecossistema/../produtividade/agenda.json",
            ".env", "ecossistema", "ecossistema/", "", "ecossistema/a.md\x00.txt", "ECOSSISTEMA/a.md", "ecossistema//a.md", None]:
    d, cod = P.documento(cam)
    confere(cod == 404 and "SEGREDO_FORA" not in json.dumps(d) and SEGREDO not in json.dumps(d), f"traversal recusado: {cam!r}")
d, cod = P.documento("ecossistema/a.md")
confere(cod == 200 and "ok" in d["conteudo"], "caminho legítimo abre")
try:
    link = RAIZ / "ecossistema" / "link.md"
    os.symlink(TMP / "fora.md", link)
    P.invalidar()
    ind = lista()
    confere("ecossistema/link.md" not in ind, "link simbólico para fora não entra")
    d, cod = P.documento("ecossistema/link.md")
    confere(cod == 404, "link simbólico não abre")
except (OSError, NotImplementedError):
    print("  (sem permissão para criar link simbólico neste Windows; caso não testado)")

print("[Ordenação e mudança]")
estado_limpo()
(RAIZ / "prompts" / "p.md").unlink()
for i, n in enumerate(["velho", "meio", "novo"]):
    w(f"prompts/{n}.md", f"# {n}\nv1", mtime=agora - 5000 + i * 1000)
P.invalidar()
d0 = P.documentos(area="prompts")
caminhos = [x["caminho"] for x in d0["documentos"]]
confere(caminhos == ["prompts/novo.md", "prompts/meio.md", "prompts/velho.md"], "mais recente no topo", caminhos)
confere(all(x["alterado_em"] and "T" in x["alterado_em"] for x in d0["documentos"]), "cada documento traz data/hora ISO")
confere(all("flag" not in x for x in d0["documentos"]) and "novos_ou_alterados" not in d0 and "visto_em" not in d0, "sem etiquetas novo/alterado nem visto")
m0 = P.marca()
w("prompts/velho.md", "# velho\nv2 editado")
P.invalidar()
top = P.documentos(area="prompts")["documentos"]
confere(top[0]["caminho"] == "prompts/velho.md", "arquivo editado sobe ao topo", top[0])
confere(P.marca() != m0 and P.mudancas(m0)["mudou"] and "prompts/velho.md" in P.mudancas(m0)["caminhos"], "marca muda e mudancas aponta o caminho")
m1 = P.marca()
confere(P.mudancas(m1) == {"marca": m1, "mudou": False, "caminhos": []}, "sem mudança: 'igual'")
ant = {x["caminho"]: x for x in P.documentos(area="prompts")["documentos"]}["prompts/meio.md"]["alterado_em"]
os.utime(RAIZ / "prompts" / "meio.md", (agora + 50, agora + 50))
P.invalidar()
dep = {x["caminho"]: x for x in P.documentos(area="prompts")["documentos"]}["prompts/meio.md"]
confere(dep["alterado_em"] == ant, "touch sem mudar o conteúdo não muda a data", dep)
w("prompts/criado.md", "# criado agora")
P.invalidar()
top = P.documentos(area="prompts")["documentos"]
confere(top[0]["caminho"] == "prompts/criado.md", "arquivo novo aparece no topo", top[0])
(RAIZ / "prompts" / "meio.md").unlink()
P.invalidar()
confere("prompts/meio.md" not in {x["caminho"] for x in P.documentos(area="prompts")["documentos"]}, "arquivo apagado sai da lista")
confere(not (Path(os.environ["ESTUDIO_DADOS"]) / "painel_estado.json").exists() and not [f for f in Path(os.environ["ESTUDIO_DADOS"]).iterdir() if "painel" in f.name], "nada gravado em estudio/dados")
confere(len(P.documentos(limite=2)["documentos"]) == 2 and P.documentos(limite=2)["total"] > 2, "paginação: limite e total")
confere(all(x["area"] == "videos" for x in P.documentos(area="videos")["documentos"]) and P.documentos(area="videos")["total"] >= 2, "filtro por área")
confere(all("velho" in x["caminho"] or "velho" in x["titulo"].lower() for x in P.documentos(q="velho")["documentos"]) and P.documentos(q="velho")["total"] >= 1, "busca por título/caminho")

print("[Rajada de alterações]")
for i in range(40):
    w(f"programacao/rajada{i}.md", f"# r{i}")
P.invalidar()
c = [x["caminho"] for x in P.documentos(limite=500)["documentos"]]
confere(len(c) == len(set(c)), "rajada sem duplicados")

print("[Resumo]")
estado_limpo()
for rel in list(P._candidatos(RAIZ)):
    (RAIZ / rel).unlink()
d = RAIZ / "programacao" / "maestro"
for f in (d / "decisoes").glob("*.json"):
    f.unlink()
if (d / "log.md").exists():
    (d / "log.md").unlink()
P.invalidar()
r = P.resumo(RAIZ)
confere(len(r["linhas"]) == 2 and r["linhas"][0] == "Nada executado ainda" and "Nenhum documento" in r["linhas"][1], "tudo vazio: 2 linhas honestas", r)
confere(r["custo_usd"] == 0, "sem custo")
(d).mkdir(parents=True, exist_ok=True)
(d / "decisoes").mkdir(exist_ok=True)
log = [f"2026-11-04 16:35:36 chamando Zico para ['PROG-015', 'PROG-001'] em Pronto para aceite",
       f"2026-11-04 16:36:13 Zico terminou (US$ 0.17, erro=False): 'texto longo {'x' * 500}'",
       f"2026-11-04 17:05:16 chamando Rodrygo para ['PROG-005'] em Fazendo",
       f"2026-11-04 17:30:00 Rodrygo terminou (US$ 0.63, erro=False): 'ok'"]
(d / "log.md").write_text("\n".join(log), encoding="utf-8")
P.invalidar()
r = P.resumo(RAIZ)
confere("Rodrygo implementou PROG-005" in r["linhas"][0], "linha 1: última ação do log com verbo da coluna", r["linhas"][0])
(d / "log.md").write_text("\n".join(log[:2] + ["2026-11-04 17:05:16 chamando Rodrygo para ['PROG-005'] em Fazendo", "2026-11-04 17:30:00 Rodrygo terminou (US$ 0.63, erro=True): 'x'"]), encoding="utf-8")
P.invalidar()
confere("falhou em PROG-005" in P.resumo(RAIZ)["linhas"][0], "falha vira 'falhou'", P.resumo(RAIZ)["linhas"][0])
# decisão mais recente que o log, esperando o Guilherme, com texto enorme
dec = {"id": "PROG-009", "acao": "manter", "status": "A" * 600, "precisa_do_guilherme": True, "pedido_ao_guilherme": "Aceita?"}
(d / "decisoes" / "PROG-009.json").write_text(json.dumps(dec), encoding="utf-8")
w("ecossistema/a1.md", "# a1", mtime=agora + 100)
w("ecossistema/a2.md", "# a2", mtime=agora + 110)
w("ecossistema/a3.md", "# a3", mtime=agora + 120)
w("produtividade/agenda.json", '{"x": "medico"}', mtime=agora + 5)
P.invalidar()
r = P.resumo(RAIZ)
confere(r["linhas"][0].startswith("Espera você: ") and "PROG-009" in r["linhas"][0], "decisão que espera o Guilherme vira 'Espera você'", r["linhas"][0])
confere(all(len(l) <= 120 for l in r["linhas"]) and len(r["linhas"]) == 2, "no máximo 2 linhas de 120 caracteres", [len(l) for l in r["linhas"]])
confere("a3.md, a2.md" in r["linhas"][1] and "medico" not in json.dumps(r), "linha 2: 2 documentos mais recentes", r["linhas"][1])
confere(r["base_em"] is not None, "traz a data/hora da base")
w("ecossistema/a4.md", "# a4", mtime=agora + 200)
P.invalidar()
confere("a4.md" in P.resumo(RAIZ)["linhas"][1], "resumo muda quando os arquivos mudam")
confere("inventado" not in json.dumps(r), "não inventa itens")

print("[Setores e visão]")
w("ecossistema/setores.json", json.dumps({"nomes_compostos": ["thiago-silva"], "setores": [
    {"id": "programacao", "nome": "Programação", "ativo": True, "agentes": ["rodrygo-dev-back", "thiago-silva-tech-lead", "fantasma-sem-arquivo"]},
    {"id": "pessoal", "nome": "Produtividade pessoal", "ativo": False, "privado": True, "agentes": ["ronaldo-assistente"]}]}))
for a in ["rodrygo-dev-back", "thiago-silva-tech-lead", "ronaldo-assistente", "novato-sem-setor"]:
    w(f".claude/agents/{a}.md", f"---\nname: {a}\n---\ncorpo {a}")
P.invalidar()
s = P.setores()
prog = next(x for x in s["setores"] if x["id"] == "programacao")
pess = next(x for x in s["setores"] if x["id"] == "pessoal")
confere([a["nome"] for a in prog["agentes"]] == ["Rodrygo", "Thiago Silva", "Fantasma"], "nomes dos agentes", prog["agentes"])
confere(prog["agentes_sem_arquivo"] == ["fantasma-sem-arquivo"], "agente da lista sem arquivo é sinalizado")
confere([a["id"] for a in s["sem_setor"]] == ["novato-sem-setor"], "agente sem setor é sinalizado, não some", s["sem_setor"])
confere(pess["nome"] == "Produtividade pessoal" and pess["agentes_total"] == 1 and [a["nome"] for a in pess["agentes"]] == ["Ronaldo"] and "privado" not in pess, "setor pessoal aparece com nome real e agentes, como os demais", pess)
d, cod = P.documento(".claude/agents/ronaldo-assistente.md")
confere(cod == 200 and "corpo ronaldo-assistente" in d["conteudo"], "prompt de agente pessoal abre em Documentos")
(RAIZ / "programacao" / "sprints").mkdir(parents=True, exist_ok=True)
(RAIZ / "programacao" / "quadro.md").write_text("## Fazendo\n- [PROG-001] x\n## Feito\n- [PROG-009] y\n", encoding="utf-8")
from estudio import central  # noqa: E402
confere(any(x["id"] == "programacao" for x in central.SETORES) and len(central.AGENTES) >= 9, "central.py lê a fonte única (repositório real)", central.AGENTES)

print("[Rotas HTTP]")
from estudio.servidor import Manipulador  # noqa: E402
srv = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"


def get(caminho):
    try:
        with urllib.request.urlopen(base + caminho) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "{}")


try:
    central.PROG = RAIZ / "programacao"
    w("ecossistema/ok.md", "# Normal\ntexto sem nada de mais")
    for rel in ["produtividade/tarefas.md", "produtividade/agenda.md", "produtividade/horas.md", "produtividade/kanban.md", "produtividade/README.md", "financas/README.md", "financas/pendencias.md", "financas/saldos.csv"]:
        w(rel, f"# {rel}\nok")
    P.invalidar()
    cod, v = get("/api/painel/visao")
    confere(cod == 200 and {"videos", "agentes_ativos", "sprint", "decisoes_pendentes", "documentos_hoje", "setores", "sem_setor"} <= set(v), "GET visao", list(v))
    confere(any(x["id"] == "PROG-009" for x in v["decisoes_pendentes"]) is False, "decisão já Feita no quadro não conta como pendente")
    cod, v = get("/api/painel/documentos?limite=500")
    confere(cod == 200 and v["documentos"] and "marca" in v, "GET documentos")
    confere(v["areas"].get("produtividade", 0) >= 5 and v["areas"].get("financas", 0) >= 2, "áreas produtividade e financas contadas", v["areas"])
    confere(not any(".env" in x["caminho"] or "token" in x["caminho"] for x in v["documentos"]) and any(x["caminho"] == "produtividade/tarefas.md" for x in v["documentos"]), "HTTP: tarefas.md na lista, nenhum segredo")
    cod, dd = get("/api/painel/documento?caminho=" + urllib.parse.quote("ecossistema/ok.md"))
    confere(cod == 200 and "sem nada" in dd["conteudo"], "GET documento legítimo")
    for cam in ["produtividade/.ronaldo_historico.json", "produtividade/.env", "../fora.md", "%2e%2e/fora.md", ".env", "ecossistema%2F..%2F..%2Ffora.md", "estudio/dados/senha_rede.txt"]:
        cod, dd = get("/api/painel/documento?caminho=" + cam)
        confere(cod == 404 and "SEGREDO" not in json.dumps(dd), f"HTTP documento recusa {cam}", (cod, dd))
    cod, mu = get("/api/painel/mudancas?desde=" + urllib.parse.quote(v["marca"]))
    confere(cod == 200 and mu["mudou"] is False, "GET mudancas igual")
    cod, rs = get("/api/painel/resumo")
    confere(cod == 200 and len(rs["linhas"]) == 2 and all(len(l) <= 120 for l in rs["linhas"]), "GET resumo")
    cod, _ = get("/api/painel/inexistente")
    confere(cod == 404, "rota desconhecida -> 404")
    try:
        urllib.request.urlopen(urllib.request.Request(base + "/api/painel/visto", data=b"{}", method="POST"))
        confere(False, "endpoint de visto não deve existir")
    except urllib.error.HTTPError as e:
        confere(e.code in (404, 405, 409, 500), "endpoint de visto não existe", e.code)
    # 403 fora do computador (achados 1 e 2 do review)
    import http.client
    from types import SimpleNamespace
    for host in ("127.0.0.1:%d" % srv.server_address[1], "localhost:8765"):
        for cam in ("/painel", "/api/painel/visao", "/api/painel/documento?caminho=ecossistema/ok.md"):
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1]); c.request("GET", cam, headers={"Host": host}); r = c.getresponse(); r.read(); c.close()
            confere(r.status == 200, f"local com Host {host} abre {cam}", r.status)
    for host in ("evil.example", "evil.example:8765", "192.168.0.5:8765", ""):
        for cam in ("/painel", "/api/painel/visao", "/api/painel/documento?caminho=ecossistema/ok.md"):
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1]); c.putrequest("GET", cam, skip_host=True)
            if host: c.putheader("Host", host)
            c.endheaders(); r = c.getresponse(); corpo = r.read(); c.close()
            confere(r.status == 403 and b"sem nada" not in corpo, f"Host {host!r} em {cam} -> 403 (rebinding)", r.status)
    for ip in ("192.168.0.20", "10.0.0.7", "8.8.8.8"):
        regs = []
        fake = SimpleNamespace(headers={"Host": "127.0.0.1:8765"}, client_address=(ip, 5000), _erro=lambda m, cod=409: regs.append(cod))
        confere(Manipulador._so_computador(fake) is False and regs == [403], f"cliente {ip} (mesmo com Host local e sessao) -> 403", regs)
    fake = SimpleNamespace(headers={"Host": "localhost:8765"}, client_address=("127.0.0.1", 5000), _erro=lambda *a: None)
    confere(Manipulador._so_computador(fake) is True, "cliente local + Host localhost segue")
    fake.client_address = ("::1", 5000)
    confere(Manipulador._so_computador(fake) is True, "cliente ::1 segue")
    try:
        urllib.request.urlopen(urllib.request.Request(base + "/api/painel/documentos", data=b"{}", method="POST"))
        confere(False, "POST em rota de leitura deve falhar")
    except urllib.error.HTTPError as e:
        confere(e.code in (404, 405, 409, 500), "POST em rota de leitura não é aceito", e.code)
finally:
    srv.shutdown()

print("[Junction]")
if os.name == "nt":
    import subprocess
    jt = Path(tempfile.mkdtemp()); (jt / "ecossistema").mkdir(); (jt / "ecossistema" / "a.md").write_text("x"); (jt / "alvo").mkdir(); (jt / "alvo" / "b.md").write_text("y")
    subprocess.run(["cmd", "/c", "mklink", "/J", str(jt / "ecossistema" / "jn"), str(jt / "alvo")], capture_output=True)
    confere(P._candidatos(jt) == ["ecossistema/a.md"], "junction do Windows fora do índice", P._candidatos(jt))

print("[Repositório real]")
P.RAIZ = REPO
P._docs.clear()
P._cache["indice"] = None
t0 = time.perf_counter()
real = P.varrer(forcar=True)
dt = time.perf_counter() - t0
confere(len(real) > 50, f"índice real tem {len(real)} documentos", len(real))
confere(dt < 2.0, f"varredura real em {dt:.2f}s (limite 2 s)", dt)
confere("produtividade/tarefas.md" in real and "financas/README.md" in real and not any(k.startswith(("estudio/dados/", "voz/")) or "/." in k.replace("/.claude/", "/") and not k.startswith("produtividade/.ronaldo_contexto") or ".env" in k or "client_secret" in k or "token" in k.lower() for k in real), "repositório real: nada proibido no índice")
confere(not [k for k in real if k.endswith((".mp4", ".wav", ".jpg", ".png"))], "sem mídia")
t0 = time.perf_counter()
P.varrer(forcar=True)
confere(time.perf_counter() - t0 < 2.0, "segunda varredura (com estado) abaixo de 2 s")

print(f"\n{passou} ok, {len(falhas)} falhas")
for f in falhas:
    print("  -", f)
sys.exit(1 if falhas else 0)
