"""Rotas da API de Clipes: GET/POST /api/clipes*, SSE /api/eventos."""
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

from .config import REPO

CLIPES_OUT = REPO / "clipes_out"
CLIPES_OUT.mkdir(exist_ok=True)

# Gerenciador de SSE: lista de clientes aguardando eventos
_clientes_sse = []
_lock_sse = threading.Lock()


def _ler_estado(slug: str) -> dict:
    """Lê o estado.json de um projeto de clipes."""
    arquivo = CLIPES_OUT / slug / "estado.json"
    if arquivo.exists():
        try:
            return json.loads(arquivo.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return {"nos": {}, "eventos": []}


def _ler_fonte(slug: str) -> dict:
    """Lê fonte.json para pegar URL e autor."""
    arquivo = CLIPES_OUT / slug / "fonte.json"
    if arquivo.exists():
        try:
            return json.loads(arquivo.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return {}


def listar_projetos() -> dict:
    """GET /api/clipes: lista de projetos com status agregado."""
    projetos = []

    if not CLIPES_OUT.exists():
        return {"projetos": [], "error": None}

    try:
        for pasta in sorted(CLIPES_OUT.iterdir()):
            if not pasta.is_dir() or pasta.name.startswith("."):
                continue

            slug = pasta.name
            estado = _ler_estado(slug)
            fonte = _ler_fonte(slug)

            # Status agregado: qual é o nó mais avançado?
            status_geral = "pendente"
            progresso_geral = 0
            agentes_lista = []

            if estado.get("nos"):
                for no_id, no_info in estado["nos"].items():
                    st = no_info.get("status", "pendente")
                    agentes_lista.append({
                        "nome": no_id,
                        "status": st,
                        "agente": no_info.get("agente", "?"),
                        "msg": no_info.get("msg", ""),
                        "progresso": no_info.get("progresso")
                    })

                    # Status geral: mais avançado (em ordem: trabalhando > esperando_voce > falhou > concluido > bloqueado > pendente)
                    if st == "trabalhando":
                        status_geral = "fazendo"
                    elif st == "esperando_voce" and status_geral not in ("fazendo",):
                        status_geral = "esperando_voce"
                    elif st == "falhou" and status_geral not in ("fazendo", "esperando_voce"):
                        status_geral = "erro"
                    elif st == "concluido" and status_geral in ("pendente", "bloqueado"):
                        status_geral = "prontos"

            # Nota do Rivaldo (se existir)
            nota_rivaldo = ""
            for evento in reversed(estado.get("eventos", [])):
                if evento.get("no") == "triagem" and evento.get("agente") == "Rivaldo":
                    nota_rivaldo = evento.get("msg", "")
                    break

            # Contar cortes prontos
            cortes_dir = pasta / "clipes"
            cortes_prontos = 0
            if cortes_dir.exists():
                cortes_prontos = len(list(cortes_dir.glob("*.mp4")))

            projetos.append({
                "slug": slug,
                "titulo": fonte.get("titulo", "Sem título"),
                "fonte_url": fonte.get("url", ""),
                "fonte": {
                    "criador": fonte.get("autor", "Desconhecido"),
                    "url": fonte.get("url", "")
                },
                "status": status_geral,
                "nota_rivaldo": nota_rivaldo,
                "notas": {
                    "rivaldo": nota_rivaldo
                },
                "tempo_inicio": datetime.fromtimestamp(
                    (pasta / "estado.json").stat().st_mtime
                ).isoformat() if (pasta / "estado.json").exists() else "",
                "agentes": agentes_lista,
                "data_criacao": datetime.fromtimestamp(
                    (pasta / "estado.json").stat().st_mtime
                ).isoformat() if (pasta / "estado.json").exists() else "",
                "cortes_prontos": cortes_prontos
            })

        return {"projetos": projetos, "error": None}
    except Exception as e:
        return {"projetos": [], "error": str(e)}


def iniciar_projeto(url: str, autor: str, autorizacao: str, perfil: str = "geral") -> dict:
    """POST /api/clipes/novo: dispara python -m clipes tudo em background."""
    try:
        # Validar autorizacao
        autorizacoes_validas = ["sem_autorizacao", "parceria", "licenca", "dominio_publico", "fair_use"]
        if autorizacao not in autorizacoes_validas:
            return {
                "slug": None,
                "status": "erro",
                "error": f"Autorização inválida. Use: {', '.join(autorizacoes_validas)}"
            }

        # Gerar slug a partir da URL ou criar um genérico
        import re
        slug_match = re.search(r"(?:v=([a-zA-Z0-9_-]+)|youtu\.be/([a-zA-Z0-9_-]+))", url)
        if slug_match:
            slug = (slug_match.group(1) or slug_match.group(2))[:20]
        else:
            slug = f"projeto-{int(time.time())}"

        # Disparar em thread para não bloquear a resposta
        def executar():
            try:
                cmd = [
                    "python", "-m", "clipes", "tudo",
                    url,
                    "--autor", autor,
                    "--autorizacao", autorizacao,
                    "--perfil", perfil,
                    "--slug", slug
                ]
                subprocess.Popen(cmd, cwd=str(REPO))
            except Exception as e:
                # Marcar como falha no estado
                print(f"[clipes] erro ao disparar: {e}")

        thread = threading.Thread(target=executar, daemon=True)
        thread.start()

        return {
            "slug": slug,
            "status": "iniciando",
            "error": None
        }
    except Exception as e:
        return {"slug": None, "status": "erro", "error": str(e)}


def ajustar_corte(slug: str, id_corte: int, ini: float, fim: float, layout: str = "borrado") -> dict:
    """POST /api/clipes/ajustar/<slug>/<id>: refaz um corte com novo intervalo."""
    try:
        # Disparar em thread
        def executar():
            try:
                cmd = [
                    "python", "-m", "clipes", "ajustar",
                    slug,
                    "--id", str(id_corte),
                    "--ini", str(ini),
                    "--fim", str(fim),
                    "--layout", layout
                ]
                subprocess.Popen(cmd, cwd=str(REPO))
            except Exception as e:
                print(f"[clipes] erro ao ajustar: {e}")

        thread = threading.Thread(target=executar, daemon=True)
        thread.start()

        return {
            "slug": slug,
            "id": id_corte,
            "status": "ajustando",
            "error": None
        }
    except Exception as e:
        return {"slug": slug, "id": id_corte, "status": "erro", "error": str(e)}


class ClienteSSE:
    """Representa um cliente conectado via SSE."""
    def __init__(self, escrever_fn):
        self.escrever = escrever_fn
        self.ultimo_timestamp = time.time()
        self.slugs_vistos = set()


def registrar_sse(cliente: ClienteSSE) -> None:
    """Registra um cliente SSE para receber eventos."""
    with _lock_sse:
        _clientes_sse.append(cliente)


def remover_sse(cliente: ClienteSSE) -> None:
    """Remove um cliente SSE."""
    with _lock_sse:
        if cliente in _clientes_sse:
            _clientes_sse.remove(cliente)


def monitorar_mudancas() -> None:
    """Thread que monitora estado.json de todos os projetos e notifica SSE."""
    ultimos_timestamp = {}

    while True:
        time.sleep(2)  # Verificar a cada 2 segundos

        if not CLIPES_OUT.exists():
            continue

        try:
            for pasta in CLIPES_OUT.iterdir():
                if not pasta.is_dir() or pasta.name.startswith("."):
                    continue

                slug = pasta.name
                arquivo_estado = pasta / "estado.json"

                if arquivo_estado.exists():
                    try:
                        mtime = arquivo_estado.stat().st_mtime
                        if slug in ultimos_timestamp and mtime > ultimos_timestamp[slug]:
                            # Arquivo foi modificado
                            estado = _ler_estado(slug)
                            if estado.get("eventos"):
                                ultimo_evento = estado["eventos"][-1]
                                # Notificar todos os clientes SSE
                                evento_sse = {
                                    "slug": slug,
                                    "novo_status": ultimo_evento.get("status"),
                                    "no": ultimo_evento.get("no"),
                                    "agente": ultimo_evento.get("agente"),
                                    "msg": ultimo_evento.get("msg")
                                }
                                notificar_sse(evento_sse)

                        ultimos_timestamp[slug] = mtime
                    except OSError:
                        pass
        except Exception:
            pass


def notificar_sse(evento: dict) -> None:
    """Envia um evento para todos os clientes SSE conectados."""
    with _lock_sse:
        clientes_mortos = []
        for cliente in _clientes_sse:
            try:
                dados_json = json.dumps(evento, ensure_ascii=False)
                cliente.escrever(f'data: {dados_json}\n\n'.encode('utf-8'))
            except Exception:
                clientes_mortos.append(cliente)

        # Remover clientes com erro
        for cliente in clientes_mortos:
            _clientes_sse.remove(cliente)


# Iniciar thread de monitoramento na primeira importação
_monitor_thread = None
def _iniciar_monitor():
    global _monitor_thread
    if _monitor_thread is None or not _monitor_thread.is_alive():
        _monitor_thread = threading.Thread(target=monitorar_mudancas, daemon=True)
        _monitor_thread.start()

_iniciar_monitor()
