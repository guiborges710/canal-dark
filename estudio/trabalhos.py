"""Fila de trabalhos: uma thread olha o banco, inicia o que a raia permite e conclui o que terminou.

O estado fica todo no banco e em estudio/dados/jobs/<id>/. Se o servidor cair, ao voltar ele reencontra os trabalhos vivos
pelo batimento e marca como falha os que morreram, com ação para tentar de novo.
"""
import json
import re
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from . import fluxo, materiais as M
from .banco import agora, evento, faz, um, varios
from .config import BATIMENTO_MORTO_S, CLAUDE, DADOS, LIMITE_RAIAS, ORCAMENTO_AGENTE, PY, RAIZ, REPO, SIMULADOR

JOBS = DADOS / "jobs"
_integracoes = {"em": 0, "dados": None}
_lock = threading.Lock()


def pasta_job(job_id):
    return JOBS / str(job_id)


def integracoes():
    """O que o estúdio precisa para cada ação. Sem isso, a ação fica indisponível e a tela diz exatamente o que falta."""
    with _lock:
        if _integracoes["dados"] and time.time() - _integracoes["em"] < 60:
            return _integracoes["dados"]
    dados = {}
    dados["claude"] = _claude_status()
    if SIMULADOR:
        ok = {"ok": True, "detalhe": "simulador de teste"}
        dados.update(voz=ok, render=ok, ffmpeg=ok)
    else:
        amostra, venv = REPO / "voz" / "amostra.wav", REPO / ".venv-voz" / "Scripts" / "python.exe"
        faltas = [t for ok_, t in ((venv.exists(), f"ambiente da voz em {venv}"), (amostra.exists(), f"amostra da voz em {amostra}")) if not ok_]
        dados["voz"] = {"ok": not faltas, "detalhe": "Falta " + " e ".join(faltas) if faltas else "Chatterbox com a voz do canal"}
        modulos = (REPO / "render" / "node_modules").is_dir()
        dados["render"] = {"ok": modulos and bool(shutil.which("node")), "detalhe": "Node e render/node_modules" if modulos else "Rode `npm install` em render/ (necessário para o estilo cartões)"}
        ff = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
        dados["ffmpeg"] = {"ok": ff, "detalhe": "ffmpeg e ffprobe no PATH" if ff else "Instale o ffmpeg e o ffprobe no PATH"}
    with _lock:
        _integracoes.update(em=time.time(), dados=dados)
    return dados


def _claude_status():
    if not CLAUDE:
        return {"ok": False, "detalhe": "Claude Code não encontrado no PATH: os agentes da squad não podem ser acionados."}
    if SIMULADOR:
        return {"ok": True, "detalhe": "simulador de teste"}
    try:
        r = subprocess.run([CLAUDE, "auth", "status"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
                           env=_env_sem_chaves(), creationflags=0x08000000)
        dados = json.loads(r.stdout)
        if not dados.get("loggedIn"):
            return {"ok": False, "detalhe": "Claude Code sem login: rode `claude auth login`."}
        return {"ok": True, "detalhe": f"Claude Code logado ({dados.get('authMethod')})"}
    except Exception:  # noqa: BLE001
        return {"ok": True, "detalhe": "Claude Code encontrado (login não verificado)"}


def _env_sem_chaves():
    from .executor import ambiente_agente
    return ambiente_agente()


def integracao_faltando(etapa, ctx):
    """Motivos para a etapa estar indisponível por falta de integração."""
    dados = integracoes()
    e = fluxo.POR_ID[etapa]
    motivos = []
    if e["agente"] and not dados["claude"]["ok"]:
        motivos.append(dados["claude"]["detalhe"])
    if e["agente"] and (RAIZ / ".claude" / "agents").is_dir() and not (RAIZ / ".claude" / "agents" / f"{fluxo._agente_de(ctx, e)[0] if ctx else e['agente']}.md").exists():
        motivos.append(f"Agente não instalado: .claude/agents/{e['agente']}.md")
    if etapa == "narracao" and not dados["voz"]["ok"]:
        motivos.append(dados["voz"]["detalhe"])
    if etapa == "video":
        if not dados["ffmpeg"]["ok"]:
            motivos.append(dados["ffmpeg"]["detalhe"])
        if ctx and ctx.estilo in ("cartoes", "3d") and not dados["render"]["ok"]:
            motivos.append(dados["render"]["detalhe"])
        if ctx and not ctx.versoes.get("narracao") and ctx.cenas and ctx.aplicavel(fluxo.POR_ID["narracao"]) and not dados["voz"]["ok"]:
            motivos.append(dados["voz"]["detalhe"])
    return motivos


def progresso(job, ctx=None):
    """Só o que dá para medir: quadros do render e falas da narração. Sem número medido, sem porcentagem."""
    if not job:
        return None
    arq = pasta_job(job["id"]) / "log.txt"
    linhas = M.ler_texto(arq).splitlines()[-40:]
    passo, pct, detalhe = None, None, None
    for x in linhas:
        if x.startswith("▶"):
            passo = x.lstrip("▶ ").strip()
        m = re.match(r"\s*(\d+)/(\d+)\s*$", x)
        if m and int(m.group(2)):
            pct = round(100 * int(m.group(1)) / int(m.group(2)))
    falas_feitas = [x for x in linhas if re.match(r"\s*fala \d+:", x)]
    spec = json.loads(job["spec"])
    if falas_feitas and ctx and ctx.cenas and not pct:
        total = len(spec.get("escopo") or ctx.cenas)
        pct = min(100, round(100 * len(falas_feitas) / total))
    uteis = [x.strip() for x in linhas if x.strip() and "%|" not in x and not x.startswith(("$", "[fim]"))]
    detalhe = uteis[-1][:160] if uteis else None
    # Contador real, se o log tiver: falas prontas da narração ou fontes de imagem do editor.
    contador = None
    if falas_feitas and ctx and ctx.cenas:
        total = len(spec.get("escopo") or ctx.cenas)
        contador = f"Cena {min(total, len(falas_feitas) + 1)} de {total}"
    for x in reversed(linhas):
        m = re.match(r"\s*fonte (\d+)/(\d+):", x)
        if m:
            contador = f"Cena {m.group(1)} de {m.group(2)}"
            break
    return {"passo": passo, "porcentagem": pct if job["status"] == "rodando" else None, "detalhe": detalhe, "contador": contador}


def iniciar_processo(job):
    spec = json.loads(job["spec"])
    pasta = pasta_job(job["id"])
    pasta.mkdir(parents=True, exist_ok=True)
    spec["slug"] = job["slug"]
    spec.setdefault("orcamento", ORCAMENTO_AGENTE)
    (pasta / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "batimento").write_text(str(time.time()), encoding="ascii")
    # Destacado: sobrevive ao fechamento do terminal do estúdio. Console escondido (CREATE_NO_WINDOW) em vez de sem console (DETACHED_PROCESS):
    # sem console, cada ffmpeg, node ou trabalhador do render que ele chama abre a própria janela preta na frente do que você está fazendo.
    # Com o console escondido, todos os filhos o herdam e nenhuma janela aparece.
    proc = subprocess.Popen([PY, "-m", "estudio.executor", str(pasta)], cwd=str(REPO), creationflags=0x08000000 | 0x00000200, close_fds=True,
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    faz("UPDATE jobs SET status='rodando', pid=?, iniciado_em=? WHERE id=?", proc.pid, agora(), job["id"])


def cancelar(job_id):
    j = um("SELECT * FROM jobs WHERE id=?", job_id)
    if not j or j["status"] not in ("fila", "rodando"):
        raise fluxo.Recusado("Este trabalho não está em execução.")
    if j["status"] == "rodando" and j["pid"]:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(j["pid"])], capture_output=True)
    faz("UPDATE jobs SET status='cancelado', terminado_em=?, erro='Cancelado por você.' WHERE id=?", agora(), job_id)
    faz("UPDATE feedback SET status='rascunho', job_id=NULL WHERE job_id=?", job_id)
    evento(j["slug"], f"Cancelado: {j['titulo']}")


def motor_do_job(j):
    """Quem roda (ou rodou) o trabalho de agente: "claude" ou "codex" (reserva quando o Claude esgota). None para comandos."""
    if j.get("motor"):
        return j["motor"]
    try:
        if json.loads(j["spec"]).get("tipo") != "agente":
            return None
    except (ValueError, KeyError):
        return None
    ativo = M.ler_texto(pasta_job(j["id"]) / "motor.txt").strip()
    return ativo if ativo in ("claude", "codex") else "claude"


def registrar_motor(j, res):
    """Grava no job qual motor rodou e, quando foi o Codex (ou a reserva falhou), deixa o aviso no histórico."""
    motor = res.get("motor") or motor_do_job(j)
    if not motor:
        return
    nota = res.get("motor_nota")
    faz("UPDATE jobs SET motor=?, motor_nota=? WHERE id=?", motor, nota, j["id"])
    if nota:
        evento(j["slug"], f"{nota} ({j['titulo']})")


def rodada():
    """Uma passada da fila. Separada do laço para os testes conseguirem chamar direto."""
    from . import grafos
    grafos.reconciliar()
    for j in varios("SELECT * FROM jobs WHERE status='rodando'"):
        pasta = pasta_job(j["id"])
        fim = pasta / "resultado.json"
        if fim.exists():
            res = M.ler_json(fim, {"erro": "Resultado ilegível."})
            registrar_motor(j, res)
            fluxo.concluir_job(j, res)
            continue
        try:
            vivo = time.time() - (pasta / "batimento").stat().st_mtime < BATIMENTO_MORTO_S
        except OSError:
            vivo = False
        if not vivo:
            fluxo.concluir_job(j, {"erro": "O processo parou sem terminar (computador desligado ou processo encerrado)."})
    ocupados = {r["raia"]: r["n"] for r in varios("SELECT raia, COUNT(*) n FROM jobs WHERE status='rodando' GROUP BY raia")}
    for j in varios("SELECT * FROM jobs WHERE status='fila' ORDER BY id"):
        if ocupados.get(j["raia"], 0) < LIMITE_RAIAS.get(j["raia"], 1):
            try:
                iniciar_processo(j)
                ocupados[j["raia"]] = ocupados.get(j["raia"], 0) + 1
            except Exception as e:  # noqa: BLE001
                fluxo.concluir_job(j, {"erro": f"Não foi possível iniciar: {e}"})


def monitor(parar):
    while not parar.is_set():
        try:
            rodada()
        except Exception as e:  # noqa: BLE001
            print(f"[{datetime.now():%H:%M:%S}] fila: {e!r}", flush=True)
        parar.wait(1.0)


def ler_log(job_id, tail=400):
    linhas = M.ler_texto(pasta_job(job_id) / "log.txt").splitlines()
    return "\n".join(linhas[-tail:])
