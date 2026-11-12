"""Reserva com Codex: detecção do limite do Claude, escolha do motor, montagem do comando e sincronização de um agente.
Os casos padrão usam Claude e Codex falsos (offline), pasta de dados temporária e não tocam em output/. Com --real, usa o login do Codex só numa pasta temporária.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_reserva_codex.py"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
# Isolamento garantido: nunca herda o ESTUDIO_DADOS do ambiente.
os.environ["ESTUDIO_DADOS"] = tempfile.mkdtemp(prefix="estudio_reserva_")

from estudio import executor, reserva  # noqa: E402

falhas = []
REAL = "--real" in sys.argv


def confere(ok, texto):
    print(("ok   " if ok else "FALHA ") + texto)
    if not ok:
        falhas.append(texto)


# 1. Detecção do limite: só a mensagem de limite de uso aciona
for t in ("You've hit your limit · resets 3pm (America/Sao_Paulo)", "5-hour limit reached ∙ resets 9pm", "Claude AI usage limit reached|1760000000",
          "You've hit your weekly limit. Your limit will reset Monday", "Weekly limit reached, resets Mon 9am"):
    confere(reserva.e_limite_do_claude(t), f"limite detectado: {t[:45]}")
for t in ("", None, "Passou do tempo limite de 45 minutos e foi interrompido.", "O agente parou no teto de US$ 3.00 por trabalho.", "rate_limit_error 429 overloaded",
          "Credit balance is too low", "simulação: sem acesso à internet", "Traceback (most recent call last): KeyError", "o limite de caracteres por linha é 26",
          "Permissões negadas: Bash"):
    confere(not reserva.e_limite_do_claude(t), f"NÃO é limite: {str(t)[:45]}")

# 2. Instruções do agente (fonte: .claude/agents) e prompt
spec = {"tipo": "agente", "agente": "zico-po-programacao", "prompt": "Registre um item no backlog."}
corpo = reserva.instrucoes_do_agente(spec)
confere("Zico" in corpo and not corpo.startswith("---"), "instruções do agente vêm do .md, sem o cabeçalho")
p = reserva.montar_prompt(spec)
confere("<pedido>\nRegistre um item no backlog.\n</pedido>" in p and "RESERVA" in p, "prompt traz instruções e pedido")
confere(reserva.instrucoes_do_agente({"agente": "x", "sistema": {"corpo": "---\nname: x\n---\nCorpo preso"}}) == "Corpo preso", "agente preso a versão usa a foto guardada")

# 3. Comando do codex (montado, nunca executado)
cmd = reserva.montar_comando(spec, "codex.exe", "C:/trabalho", "C:/tmp/ultima.txt")
confere(cmd[:2] == ["codex.exe", "exec"] and cmd[-1] == "-", "codex exec lendo o prompt do stdin")
confere(cmd[cmd.index("-s") + 1] == "workspace-write", "sandbox workspace-write (nunca danger-full-access)")
confere("--dangerously-bypass-approvals-and-sandbox" not in cmd, "sem o bypass de sandbox")
confere(cmd[cmd.index("-C") + 1] == "C:/trabalho" and cmd[cmd.index("-o") + 1] == "C:/tmp/ultima.txt", "pasta de trabalho e arquivo da última mensagem")
confere("sandbox_workspace_write.network_access=false" in cmd and "--ephemeral" in cmd, "sem rede de shell e sem sessão salva")
confere('web_search="live"' not in cmd, "agente sem WebSearch não ganha busca na web")
com_web = reserva.montar_comando({**spec, "sistema": {"ferramentas": ["Read", "WebSearch"]}}, "codex.exe", "C:/t", "C:/u")
confere('web_search="live"' in com_web, "agente que já tinha WebSearch mantém a busca")

# 4. Escolha do motor / localização do Codex
os.environ["ESTUDIO_CODEX"] = sys.executable
confere(reserva.achar_codex() == sys.executable, "ESTUDIO_CODEX define o executável")
os.environ["ESTUDIO_CODEX"] = str(REPO / "nao_existe" / "codex.exe")
confere(reserva.achar_codex() != os.environ["ESTUDIO_CODEX"], "caminho inexistente é ignorado")
os.environ.pop("ESTUDIO_CODEX")


class Log:
    def __init__(self):
        self.t = []

    def write(self, x):
        self.t.append(x)

    def texto(self):
        return "".join(self.t)


# Sem Codex: a falha do Claude continua visível, com a nota do motivo, e o motor segue "claude"
achar_antes, logado_antes = reserva.achar_codex, reserva.logado
reserva.achar_codex = lambda: None
pasta = Path(tempfile.mkdtemp(prefix="job_"))
res, log = {"erro": "You've hit your limit · resets 3pm"}, Log()
executor._tentar_codex(spec, pasta, log, res)
confere(res["erro"].startswith("You've hit your limit") and "Reserva com Codex indisponível" in res["erro"] and "motor" not in res, "sem Codex: falha original preservada e motivo anotado")
confere("não pôde rodar" in res["motor_nota"], "nota explica que a reserva não rodou")
reserva.achar_codex, reserva.logado = lambda: "codex.exe", lambda: False
res = {"erro": "weekly limit reached"}
executor._tentar_codex(spec, pasta, Log(), res)
confere("codex login" in res["erro"], "Codex sem login: motivo claro")
reserva.achar_codex, reserva.logado = achar_antes, logado_antes

# Caso real controlado (opt-in): usa o login do Codex, mas trabalha somente em
# uma pasta temporaria e nao le nem grava producoes do canal.
if REAL:
    exe = reserva.achar_codex()
    confere(bool(exe), "caso real: executavel do Codex encontrado")
    confere(bool(exe) and reserva.logado(), "caso real: Codex logado")
    if exe and reserva.logado():
        pasta_real = Path(tempfile.mkdtemp(prefix="job_codex_real_"))
        spec_real = {
            "tipo": "agente",
            "agente": "teste-reserva",
            "prompt": "Responda somente com a palavra OK. Nao leia nem altere arquivos.",
            "cwd": str(pasta_real),
            "sistema": {"corpo": "Voce valida a reserva do Estudio em um teste isolado.", "ferramentas": []},
        }
        resultado_real = {"erro": "You've hit your limit - controlled acceptance test"}
        executor._tentar_codex(spec_real, pasta_real, Log(), resultado_real)
        confere(resultado_real.get("motor") == "codex" and resultado_real.get("erro") is None,
                "caso real: limite do Claude termina pelo motor codex")
        confere("Claude estava no limite" in resultado_real.get("motor_nota", ""),
                "caso real: motor_nota explica a reserva")
        confere("OK" in resultado_real.get("resumo", ""), "caso real: resposta final do Codex foi capturada")

# 4b. Integração real do executor (Claude e Codex falsos, offline, sem credencial): critérios 2, 3 e 4 do PROG-004
import threading  # noqa: E402

fake = Path(tempfile.mkdtemp(prefix="fakes_"))
(fake / "claude_falso.py").write_text(r"""import json, os, sys
sys.stdin.read()
if os.environ.get("FAKE_CLAUDE") == "limite":
    print(json.dumps({"type": "result", "is_error": True, "subtype": "error", "result": "You've hit your limit · resets 3pm", "total_cost_usd": 0.0}), flush=True)
    sys.exit(1)
print(json.dumps({"type": "result", "is_error": False, "subtype": "success", "result": "Feito pelo Claude.", "total_cost_usd": 0.0}), flush=True)
""", encoding="utf-8")
(fake / "codex_falso.py").write_text(r"""import json, os, sys
a = sys.argv
sys.stdin.read()
Path = __import__("pathlib").Path
Path(os.environ["FAKE_MARCA"]).write_text(os.getcwd() + "|" + a[a.index("-C") + 1], encoding="utf-8")
if os.environ.get("FAKE_CODEX") == "falha":
    print("codex quebrou", file=sys.stderr, flush=True)
    sys.exit(3)
Path(a[a.index("-o") + 1]).write_text("Feito pelo Codex.", encoding="utf-8")
print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Feito pelo Codex."}}), flush=True)
""", encoding="utf-8")
for nome in ("claude", "codex"):
    (fake / f"{nome}_falso.cmd").write_text(f'@echo off\r\n"{sys.executable}" "{fake / (nome + "_falso.py")}" %*\r\n', encoding="ascii")
marca = fake / "codex_chamado.txt"
os.environ["FAKE_MARCA"] = str(marca)
home_codex = Path(tempfile.mkdtemp(prefix="codex_home_"))
os.environ["CODEX_HOME"] = str(home_codex)
(home_codex / "auth.json").write_text("{}", encoding="utf-8")  # só a existência importa; sem credencial real
os.environ["ESTUDIO_CODEX"] = str(fake / "codex_falso.cmd")
executor.CLAUDE = str(fake / "claude_falso.cmd")


def rodar_job(claude, codex=None):
    pasta_j, trab = Path(tempfile.mkdtemp(prefix="job_int_")), Path(tempfile.mkdtemp(prefix="trab_"))
    (pasta_j / "spec.json").write_text(json.dumps({"tipo": "agente", "agente": "zico-po-programacao", "prompt": "Faça algo.", "cwd": str(trab)}), encoding="utf-8")
    os.environ["FAKE_CLAUDE"], os.environ["FAKE_CODEX"] = claude, codex or ""
    if marca.exists():
        marca.unlink()
    executor.rodar(pasta_j)
    return json.loads((pasta_j / "resultado.json").read_text(encoding="utf-8")), pasta_j, trab


r, pj, trab = rodar_job("limite")
confere(r.get("motor") == "codex" and r["erro"] is None and "Claude estava no limite" in r["motor_nota"] and "Codex" in r["resumo"], "job real: Claude no limite termina com motor=codex e motor_nota")
confere((pj / "motor.txt").read_text() == "codex", "job real: motor.txt registra codex")
confere(marca.exists() and marca.read_text(encoding="utf-8").split("|")[0] == str(trab) and marca.read_text(encoding="utf-8").endswith(str(trab)), "job real: o Codex roda na pasta do job (cwd e -C)")
r, pj, _ = rodar_job("ok")
confere(r.get("motor") is None and r["erro"] is None and r["resumo"] == "Feito pelo Claude." and (pj / "motor.txt").read_text() == "claude", "job real: Claude disponível usa Claude")
confere(not marca.exists(), "job real: Claude disponível não aciona o Codex")
r, pj, _ = rodar_job("limite", "falha")
confere(r["erro"] and "hit your limit" in r["erro"] and "Reserva com Codex falhou" in r["erro"] and "motor" not in r and (pj / "motor.txt").read_text() == "claude", "job real: falha da reserva dá erro legível e o motor volta a claude")
os.environ["ESTUDIO_CODEX"] = str(fake / "codex_falso.cmd")
(home_codex / "auth.json").unlink()  # login ausente de verdade (logado() real, sem monkeypatch)
r, pj, _ = rodar_job("limite")
confere(not marca.exists() and "codex login" in r["erro"] and "motor" not in r, "job real: sem login do Codex não executa e explica")
(home_codex / "auth.json").write_text("{}", encoding="utf-8")
r, pj, _ = rodar_job("ok")
confere(r["erro"] is None, "job seguinte volta a tentar o Claude primeiro")

# O motor chega ao estado público do job pelo monitor real (trabalhos.rodada), como a tela lê
from estudio import fluxo, trabalhos  # noqa: E402
from estudio.banco import faz, um  # noqa: E402


def job_publico(claude):
    spec = {"tipo": "agente", "agente": "zico-po-programacao", "prompt": "Faça algo.", "origem": "gerar_tema", "cwd": str(Path(tempfile.mkdtemp(prefix="trab_")))}
    jid = faz("INSERT INTO jobs (slug, etapa, raia, titulo, craque, assinatura, status, spec, criada_em) VALUES (?,?,?,?,?,?,?,?,?)",
              "teste-reserva", "teste", "agentes", "Teste da reserva", "Zico", "x", "rodando", json.dumps(spec), "2026-01-01T00:00:00").lastrowid
    pj = trabalhos.pasta_job(jid)
    pj.mkdir(parents=True, exist_ok=True)
    (pj / "spec.json").write_text(json.dumps(spec | {"slug": "teste-reserva"}), encoding="utf-8")
    (pj / "batimento").write_text("1", encoding="ascii")
    os.environ["FAKE_CLAUDE"], os.environ["FAKE_CODEX"] = claude, ""
    executor.rodar(pj)
    trabalhos.rodada()
    return fluxo.status_job_publico(dict(um("SELECT * FROM jobs WHERE id=?", jid)))


pub = job_publico("limite")
confere(pub["motor"] == "codex" and "Claude estava no limite" in (pub["motor_nota"] or "") and pub["status"] == "ok", "estado público do job: motor codex e motor_nota")
pub = job_publico("ok")
confere(pub["motor"] == "claude" and not pub["motor_nota"] and pub["status"] == "ok", "estado público do job: Claude disponível mostra motor claude")

# Timer do tempo limite não pode sobreviver a uma exceção no meio da leitura (ele manteria o processo vivo por 45 min)
linha_antes = reserva.linha_codex
reserva.linha_codex = lambda l: (_ for _ in ()).throw(ValueError("boom"))
r, pj, _ = rodar_job("limite")
reserva.linha_codex = linha_antes
vivos = [t for t in threading.enumerate() if isinstance(t, threading.Timer) and t.is_alive()]
confere(not vivos and "Reserva com Codex falhou" in r["erro"], "timer do Codex é cancelado mesmo com exceção (vivos: %d)" % len(vivos))
os.environ.pop("ESTUDIO_CODEX", None)

# 5. Linhas do --json do Codex
txt, final = reserva.linha_codex(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Pronto, gravei o arquivo."}}))
confere(final == "Pronto, gravei o arquivo.", "mensagem final do agente é lida do --json")
confere(reserva.linha_codex("{ não é json")[0] == "{ não é json", "linha que não é JSON passa direto para o log")

# 6. Sincronização de um agente
spec_s = importlib.util.spec_from_file_location("sincronizar_codex", REPO / "tools" / "sincronizar_codex.py")
sync = importlib.util.module_from_spec(spec_s)
spec_s.loader.exec_module(sync)
tmp = Path(tempfile.mkdtemp(prefix="agente_")) / "teste-agente.md"
tmp.write_bytes('---\r\nname: teste-agente\r\ndescription: Faz "teste": com aspas e dois pontos.\r\ntools: Read, Write\r\nmodel: opus\r\neffort: high\r\n---\r\n\r\nLinha 1\\n com barra.\r\nLinha 2.\r\n'.encode("utf-8"))
saida = sync.toml_do_agente(tmp)
confere("\r" not in saida, "TOML gerado só com LF")
confere('name = "teste-agente"' in saida and 'description = "Faz \\"teste\\": com aspas e dois pontos."' in saida, "name e description escapados")
chaves = [l.split("=")[0].strip() for l in saida.split("developer_instructions")[0].split("\n") if "=" in l and not l.startswith("#")]
confere('model_reasoning_effort = "high"' in saida and "tools" not in chaves and "model" not in chaves and "opus" not in saida.split("developer_instructions")[0], "effort mapeado; tools e model omitidos (chaves: %s)" % chaves)
confere(chaves == ["name", "description", "model_reasoning_effort"], "só as chaves esperadas no cabeçalho do TOML")
confere("Linha 1\\n com barra.\nLinha 2." in saida, "corpo preservado (barra literal intacta)")
try:
    import tomllib
    d = tomllib.loads(saida)
    confere(d["name"] == "teste-agente" and d["developer_instructions"].rstrip().endswith("Linha 2."), "TOML válido")
except ImportError:
    print("pula: tomllib só existe no Python 3.11+")
confere(len(sync.planejar()) >= len(list(sync.AGENTES.glob("*.md"))), "o plano cobre todos os agentes de .claude/agents")
confere({"estilos-por-camadas", "roteiro-para-video-sketch"} <= set(sync.skills_usadas()), "skills dos agentes entram no espelho")

print("\nFALHARAM: %d" % len(falhas) if falhas else "\nTudo certo.")
sys.exit(1 if falhas else 0)
