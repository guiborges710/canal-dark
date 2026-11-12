"""Painel do setor de Clipes: fluxo visual ao vivo (http://127.0.0.1:8767/).

Mostra cada agente do setor num nó do fluxo, quem está trabalhando agora e o andamento etapa
por etapa, lendo clipes_out/<slug>/estado.json. Não publica nem chama API paga. Só biblioteca padrão.
Também lista o setor no mapa do ecossistema (ecossistema/setores.json) e liga aos outros painéis.

Leitura (GET): /api/fluxo, /api/projetos, /api/estado/<slug>, /api/cortes/<slug>,
  /api/transcricao/<slug>?ini=&fim=, /api/eventos (SSE: avisa quando algo mudou), /midia/<slug>/<NN|fonte>.mp4.
Perfis (V2): GET /api/perfis[?todos=1], /api/perfis/<id>, /api/projeto/<slug>/perfil.
Ações (POST, só no computador local; no modo --rede continuam só leitura):
  /api/iniciar           -> python -m clipes tudo ... --perfil <id> (download, transcrição, momentos e cortes)
  /api/perfis            -> cria ({"novo": true, "perfil": {...}}) ou salva nova versão de um perfil
  /api/perfis/<id>/duplicar, /api/perfis/<id>/arquivar ({"arquivado": bool})
  /api/projeto/<slug>/perfil -> ajuste só na cópia do perfil do projeto
  /api/ajustar/<slug>/<N> -> python -m clipes ajustar ... (refaz UM corte com novo intervalo/legenda/enquadramento/áudio)
  /api/avaliar/<slug>[/<N>] -> python -m clipes avaliar ... (plano B: o Totti avalia o corte N, ou os sem nota)
Os demais agentes de texto (Kaká, Zidane, Figo, Buffon, Lewandowski) não são disparados daqui: o painel só
mostra quando chegam a vez deles. O Totti roda no fluxo normal; o botão "Avaliar potencial" é o plano B.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import estado as E
from . import etapas as T
from . import perfis as PF
from .pipeline import AUTORIZACOES, LAYOUTS, RAIZ, SAIDA, slugify

WEB = Path(__file__).parent / "web"
# Fluxo do botão Iniciar. "v1" = encadeamento automático de código (agentes pelo Pelé) até a tela de
# revisão de sugestões da V2 ficar pronta; depois passa a "v2".
FLUXO_INICIAR = "v2"
SENHA: str | None = None  # só existe no modo --rede
SETORES = RAIZ / "ecossistema" / "setores.json"


def _ler(p: Path, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def projetos() -> list[dict]:
    out = []
    for d in sorted(SAIDA.glob("*/")) if SAIDA.exists() else []:
        f = _ler(d / "fonte.json", None)
        if not f:
            continue
        est = E.ler(d)
        nos = est["nos"]
        ids = [x["id"] for x in T.para_painel(d)]
        feitos = sum(1 for k, n in nos.items() if k in ids and n.get("status") == "concluido")
        ativo = next((k for k, n in nos.items() if n.get("status") == "trabalhando"), None)
        ultimo = est["eventos"][-1]["t"] if est["eventos"] else 0
        try:
            perfil = PF.resumo(PF.do_projeto(d))
        except (KeyError, OSError, ValueError):
            perfil = None
        out.append({"slug": d.name, "autor": f.get("autor", ""), "titulo": f.get("titulo_original", ""),
                    "perfil": perfil,
                    "origem": f.get("origem", ""), "trabalho": _trabalho(d.name),
                    "autorizacao": f.get("autorizacao", {}).get("tipo", "?"),
                    "feitos": feitos, "total": len(ids), "ativo": ativo, "ultimo": ultimo,
                    "clipes": len(list((d / "clipes").glob("*.mp4"))) if (d / "clipes").exists() else 0})
    return sorted(out, key=lambda x: x["ultimo"], reverse=True)


def _projeto(slug: str) -> Path | None:
    d = (SAIDA / slug).resolve()
    return d if d.parent == SAIDA.resolve() and d.is_dir() else None


def _fim_corte(j: dict):
    """Fim do trecho na fonte. Cortes antigos não gravavam `fim`: deriva da duração menos o gancho na frente."""
    if j.get("fim") is not None:
        return j["fim"]
    if j.get("ini") is None or j.get("dur") is None:
        return None
    gt = j.get("gancho_trecho")
    return round(j["ini"] + j["dur"] - ((gt["fim"] - gt["ini"]) if gt else 0), 1)


def cortes(d: Path) -> list[dict]:
    """Cortes gerados do projeto (clipes/NN.mp4 + NN.json) com os textos de postagem, se existirem."""
    out = []
    for mp4 in sorted((d / "clipes").glob("[0-9][0-9].mp4")) if (d / "clipes").exists() else []:
        n = mp4.stem
        j = _ler(d / "clipes" / f"{n}.json", {})
        pub = {}
        for rede in ("instagram", "tiktok"):
            p = d / "publicar" / f"{n}_{rede}.txt"
            if p.exists():
                try:
                    pub[rede] = p.read_text(encoding="utf-8")
                except OSError:
                    pass
        pot = _ler(d / "clipes" / f"{n}.potencial.json", None)
        out.append({"id": n, "arquivo": mp4.name, "potencial": pot, "teaser": bool(j.get("gancho_trecho")), "serie": j.get("serie"), "cta": j.get("cta", ""), "dur": j.get("dur"), "gancho": j.get("gancho", ""),
                    "fecho": j.get("fecho", ""), "ini": j.get("ini"), "fim": _fim_corte(j), "gancho_trecho": j.get("gancho_trecho"), "layout": j.get("layout"),
                    "legenda": j.get("legenda", True), "audio": j.get("audio", True), "ajuste": j.get("ajuste"),
                    "comentario_proprio": bool(j.get("comentario_proprio")),
                    "tamanho_mb": round(mp4.stat().st_size / 1e6, 1), "publicar": pub,
                    "versao": int(mp4.stat().st_mtime)})
    return out


# ------------------------------------------------------------------ trabalhos em segundo plano
TRABALHOS: dict[str, dict] = {}
_trava = threading.Lock()
_duracoes: dict[str, tuple[float, float | None]] = {}
_transcricoes: dict[str, tuple[float, list]] = {}


def _trabalho(slug: str) -> dict | None:
    with _trava:
        t = TRABALHOS.get(slug)
        return {"tipo": t["tipo"], "id": t.get("id"), "ini": t["ini"]} if t else None


def duracao_fonte(d: Path) -> float | None:
    """Duração do vídeo original (ffprobe), guardada em memória até o arquivo mudar."""
    arq = d / "fonte.mp4"
    if not arq.is_file():
        return None
    m = arq.stat().st_mtime
    c = _duracoes.get(str(arq))
    if c and c[0] == m:
        return c[1]
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(arq)], capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        v = float(r.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        v = None
    _duracoes[str(arq)] = (m, v)
    return v


def transcricao(d: Path, ini: float, fim: float) -> list[dict]:
    arq = d / "transcricao.json"
    if not arq.is_file():
        return []
    m = arq.stat().st_mtime
    c = _transcricoes.get(str(arq))
    if not c or c[0] != m:
        c = (m, _ler(arq, {}).get("segmentos", []))
        _transcricoes[str(arq)] = c
    return [s for s in c[1] if s["fim"] >= ini and s["ini"] <= fim][:500]


def _fim_do_processo(slug: str, proc: subprocess.Popen, tipo: str, log: Path) -> None:
    inicio = time.time()
    rc = proc.wait()
    with _trava:
        TRABALHOS.pop(slug, None)
    if rc == 0:
        return
    d = SAIDA / slug
    try:
        cauda = [x for x in log.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()][-4:]
    except OSError:
        cauda = []
    if not (d / "fonte.json").exists():  # caiu antes de registrar o projeto: cria o mínimo para o erro aparecer
        (d / "fonte.json").write_text(json.dumps({"origem": "", "autor": "", "titulo_original": "",
                                                  "autorizacao": {"tipo": "?"}}), encoding="utf-8")
    est = E.ler(d)
    if any(n.get("status") == "falhou" and (n.get("fim") or 0) >= inicio - 1 for n in est["nos"].values()):
        return  # o próprio pipeline já registrou a falha com detalhes melhores
    ativos = [k for k, n in est["nos"].items() if n.get("status") == "trabalhando"] or ["fonte" if tipo == "iniciar" else "corte"]
    for no in ativos:
        E.marcar(d, no, "falhou", "o processo terminou com erro", None, cauda or [f"código de saída {rc}"],
                 f"Veja clipes_out/{slug}/processo.log. Depois de corrigir, rode de novo: o pipeline continua de onde parou.")


def lancar(slug: str, args: list[str], tipo: str, ident: int | None = None) -> None:
    d = SAIDA / slug
    d.mkdir(parents=True, exist_ok=True)
    log = d / "processo.log"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    with _trava:
        if slug in TRABALHOS:
            raise RuntimeError("ocupado")
        with log.open("ab") as fh:
            proc = subprocess.Popen([sys.executable, "-m", "clipes", *args], cwd=str(RAIZ), stdout=fh, stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT, env=env, creationflags=flags)
        TRABALHOS[slug] = {"tipo": tipo, "id": ident, "ini": time.time(), "pid": proc.pid}
    threading.Thread(target=_fim_do_processo, args=(slug, proc, tipo, log), daemon=True).start()


def validar_inicio(b: dict) -> tuple[dict | None, str]:
    url = str(b.get("url", "")).strip()
    autor = str(b.get("autor", "")).strip()
    aut = str(b.get("autorizacao", "livre")).strip()
    prova = str(b.get("prova", "")).strip()
    titulo = str(b.get("titulo", "")).strip()
    if not re.match(r"^https?://\S{4,}$", url) or len(url) > 500:
        return None, "Informe um link completo que comece com http:// ou https://."
    if not autor or len(autor) > 120:
        return None, "Informe o nome do criador do vídeo (ele recebe o crédito nos cortes)."
    if aut not in AUTORIZACOES:
        return None, "Tipo de autorização desconhecido."
    if aut not in ("proprio", "teste", "livre") and not prova:
        return None, "Este tipo de autorização exige a prova (link, e-mail ou print)."
    perfil = str(b.get("perfil") or PF.PADRAO_NOVOS).strip()
    try:
        pf = PF.carregar(perfil)
    except KeyError:
        return None, "Perfil não encontrado."
    if pf["arquivado"]:
        return None, "Este perfil está arquivado. Restaure-o ou escolha outro."
    try:
        quantos = int(b.get("quantos") or pf["quantidade"])
    except (TypeError, ValueError):
        quantos = pf["quantidade"]
    quantos = max(1, min(20, quantos))
    return {"url": url, "autor": autor, "autorizacao": aut, "prova": prova[:300], "titulo": titulo[:200],
            "quantos": quantos, "perfil": perfil}, ""


def validar_ajuste(d: Path, b: dict) -> tuple[dict | None, str]:
    try:
        ini, fim = float(b["ini"]), float(b["fim"])
    except (KeyError, TypeError, ValueError):
        return None, "Informe início e fim em segundos."
    dur = duracao_fonte(d)
    if ini < 0 or fim <= ini or (dur and fim > dur + 0.5):
        return None, "Intervalo fora do vídeo original."
    if not 3 <= fim - ini <= 90:
        return None, "O corte precisa ter entre 3 e 90 segundos."
    layout = b.get("layout", "borrado")
    if layout not in LAYOUTS:
        return None, "Enquadramento desconhecido."
    return {"ini": ini, "fim": fim, "layout": layout, "legenda": b.get("legenda", "palavra") != "nenhuma",
            "audio": b.get("audio", "original") != "mudo"}, ""


def assinatura() -> str:
    """Muda sempre que um estado, fonte ou corte muda (alimenta o /api/eventos)."""
    h = hashlib.md5()
    for d in sorted(SAIDA.glob("*/")) if SAIDA.exists() else []:
        for arq in [d / "estado.json", d / "fonte.json", d / "perfil.json", d / "fluxo.json", d / "momentos.json",
                    *sorted((d / "clipes").glob("*"))]:
            try:
                st = arq.stat()
                h.update(f"{arq.name}{st.st_mtime_ns}{st.st_size}".encode())
            except OSError:
                pass
    for arq in sorted(PF.PASTA.glob("*.json")):
        try:
            h.update(f"{arq.name}{arq.stat().st_mtime_ns}".encode())
        except OSError:
            pass
    h.update(",".join(sorted(TRABALHOS)).encode())
    return h.hexdigest()


def _atualiza_revisao(d: Path) -> None:
    """Depois de cada decisão, o nó da revisão mostra a situação REAL (antes ficava com a contagem antiga)."""
    try:
        no = E.ler(d)["nos"].get("revisao", {})
        if no.get("status") != "espera_voce":
            return
        mm = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
        pend = sum(1 for x in mm if x.get("status", "sugerido") == "sugerido")
        ac = sum(1 for x in mm if x.get("status") == "aceito")
        msg = (f"aceite ou rejeite as sugestões ({pend} sem decisão) e clique em Continuar" if pend or not ac
               else f"{ac} aceita(s): clique em “Continuar com as aceitas” para gerar os cortes")
        E.marcar(d, "revisao", "espera_voce", msg, "Guilherme")
    except (OSError, ValueError):
        pass


def ecossistema() -> dict:
    s = _ler(SETORES, {"setores": []})
    return {"setores": [{"id": x["id"], "nome": x["nome"], "agentes": len(x["agentes"])}
                        for x in s.get("setores", [])]}


class H(BaseHTTPRequestHandler):
    def _json(self, dados, cod=200):
        b = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(cod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _liberado(self, u) -> bool:
        if not SENHA:
            return True
        if parse_qs(u.query).get("k", [""])[0] == SENHA:
            return True
        return f"clipes_k={SENHA}" in (self.headers.get("Cookie") or "")

    def _midia(self, caminho: str):
        """Serve clipes/NN.mp4 de um projeto, com Range (o player precisa para avançar e voltar)."""
        partes = [unquote(p) for p in caminho.split("/")[2:]]
        if len(partes) != 2 or not re.fullmatch(r"\d{2}\.mp4|fonte\.mp4", partes[1]):
            return self.send_error(404)
        d = _projeto(partes[0])
        arq = (d / partes[1] if partes[1] == "fonte.mp4" else d / "clipes" / partes[1]) if d else None
        if not arq or not arq.is_file():
            return self.send_error(404)
        tam = arq.stat().st_size
        ini, fim = 0, tam - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m:
            if m.group(1):
                ini = int(m.group(1))
                fim = int(m.group(2)) if m.group(2) else tam - 1
            elif m.group(2):
                ini = max(0, tam - int(m.group(2)))
            fim = min(fim, tam - 1)
            if ini > fim:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{tam}")
                self.end_headers()
                return
        self.send_response(206 if m else 200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fim - ini + 1))
        self.send_header("Cache-Control", "no-store")
        if m:
            self.send_header("Content-Range", f"bytes {ini}-{fim}/{tam}")
        self.end_headers()
        try:
            with arq.open("rb") as fh:
                fh.seek(ini)
                resto = fim - ini + 1
                while resto > 0:
                    b = fh.read(min(1 << 20, resto))
                    if not b:
                        break
                    self.wfile.write(b)
                    resto -= len(b)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def do_GET(self):  # noqa: N802
        u = urlparse(self.path)
        if not self._liberado(u):
            self.send_error(401, "Abra o link completo mostrado no terminal (com ?k=senha).")
            return
        if u.path == "/api/fluxo":
            return self._json({"fluxo": E.FLUXO})
        if u.path == "/api/projetos":
            return self._json({"projetos": projetos(), "ecossistema": ecossistema()})
        if u.path.startswith("/api/estado/"):
            slug = unquote(u.path.rsplit("/", 1)[1])
            d = (SAIDA / slug).resolve()
            if d.parent != SAIDA.resolve() or not d.is_dir():
                return self._json({"erro": "projeto não encontrado"}, 404)
            return self._json({**E.ler(d), "fluxo": T.para_painel(d), "legado": bool(T.do_projeto(d).get("legado"))})
        if u.path.startswith("/api/cortes/"):
            d = _projeto(unquote(u.path.rsplit("/", 1)[1]))
            if not d:
                return self._json({"erro": "projeto não encontrado"}, 404)
            return self._json({"cortes": cortes(d), "trabalho": _trabalho(d.name),
                               "fonte": {"duracao": duracao_fonte(d), "tem_video": (d / "fonte.mp4").is_file(),
                                         "tem_transcricao": (d / "transcricao.json").is_file()}})
        if u.path.startswith("/api/transcricao/"):
            d = _projeto(unquote(u.path.rsplit("/", 1)[1]))
            if not d:
                return self._json({"erro": "projeto não encontrado"}, 404)
            q = parse_qs(u.query)
            try:
                ini, fim = float(q.get("ini", ["0"])[0]), float(q.get("fim", ["1e9"])[0])
            except ValueError:
                return self._json({"erro": "ini e fim devem ser números"}, 400)
            return self._json({"disponivel": (d / "transcricao.json").is_file(), "segmentos": transcricao(d, ini, fim)})
        if u.path == "/api/perfis":
            todos = parse_qs(u.query).get("todos", ["0"])[0] == "1"
            return self._json({"perfis": PF.listar(todos), "meta": {
                "sinais": PF.SINAIS, "formatos": PF.FORMATOS, "idiomas_fala": PF.IDIOMAS_FALA,
                "presets": PF.PRESETS, "agentes": PF.AGENTES, "modelo": PF.MODELO, "legado": PF.LEGADO[0],
                "padrao": PF.PADRAO_NOVOS}})
        m = re.fullmatch(r"/api/perfis/([a-z0-9-]{1,40})", u.path)
        if m:
            try:
                return self._json({"perfil": PF.carregar(m.group(1)), "historico": PF.historico(m.group(1))})
            except KeyError:
                return self._json({"erro": "perfil não encontrado"}, 404)
        m = re.fullmatch(r"/api/projeto/([^/]+)/perfil", u.path)
        if m:
            d = _projeto(unquote(m.group(1)))
            if not d:
                return self._json({"erro": "projeto não encontrado"}, 404)
            return self._json({"perfil": PF.do_projeto(d), "congelado": (d / "perfil.json").is_file()})
        m = re.fullmatch(r"/api/fluxo/([^/]+)", u.path)
        if m:
            d = _projeto(unquote(m.group(1)))
            if not d:
                return self._json({"erro": "projeto não encontrado"}, 404)
            return self._json({"fluxo": T.do_projeto(d), "padrao": T.padrao(), **T.catalogo_publico()})
        if u.path == "/api/fluxo-padrao":
            return self._json({"fluxo": T.padrao(), **T.catalogo_publico()})
        m = re.fullmatch(r"/api/momentos/([^/]+)", u.path)
        if m:
            d = _projeto(unquote(m.group(1)))
            if not d:
                return self._json({"erro": "projeto não encontrado"}, 404)
            return self._json({"momentos": _ler(d / "momentos.json", []), "duracao": duracao_fonte(d),
                               "revisao": T.ativa(d, "revisao"), "perfil": PF.resumo(PF.do_projeto(d))})
        if u.path == "/api/eventos":
            return self._eventos()
        if u.path.startswith("/midia/"):
            return self._midia(u.path)
        if u.path in ("/", "/index.html"):
            b = (WEB / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            if SENHA:
                self.send_header("Set-Cookie", f"clipes_k={SENHA}; Path=/; HttpOnly; SameSite=Strict")
            self.end_headers()
            self.wfile.write(b)
            return
        self.send_error(404)

    def _eventos(self):
        """Server-Sent Events: manda um aviso quando algo muda; o navegador então busca os dados."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        ultimo, n = "", 0
        try:
            while True:
                a = assinatura()
                if a != ultimo:
                    ultimo = a
                    self.wfile.write(f"data: {json.dumps({'t': time.time()})}\n\n".encode())
                    self.wfile.flush()
                elif n % 20 == 19:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                n += 1
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def _corpo_json(self):
        """Valida origem e tipo; devolve o JSON do corpo ou None (já respondeu o erro)."""
        if SENHA:
            self._json({"erro": "No modo --rede o painel é só leitura. Faça a ação no computador local."}, 403)
            return None
        host = (self.headers.get("Host") or "").split(":")[0]
        origem = self.headers.get("Origin")
        if host not in ("127.0.0.1", "localhost") or (origem and urlparse(origem).netloc != self.headers.get("Host")):
            self._json({"erro": "Origem não permitida."}, 403)
            return None
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            self._json({"erro": "Envie JSON."}, 415)
            return None
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 65536:
                raise ValueError
            b = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, OSError):
            self._json({"erro": "Corpo inválido."}, 400)
            return None
        if not isinstance(b, dict):
            self._json({"erro": "Corpo inválido."}, 400)
            return None
        return b

    def do_POST(self):  # noqa: N802
        u = urlparse(self.path)
        b = self._corpo_json()
        if b is None:
            return
        if u.path == "/api/iniciar":
            v, erro = validar_inicio(b)
            if not v:
                return self._json({"erro": erro}, 400)
            slug = f"{slugify(v['titulo'] or v['autor'])}-{datetime.now():%m%d-%H%M}"
            args = ["tudo", v["url"], f"--autor={v['autor']}", f"--autorizacao={v['autorizacao']}",
                    f"--prova={v['prova']}", f"--titulo={v['titulo']}", f"--slug={slug}", f"--quantos={v['quantos']}",
                    f"--perfil={v['perfil']}", f"--fluxo={FLUXO_INICIAR}"]
            try:
                lancar(slug, args, "iniciar")
            except RuntimeError:
                return self._json({"erro": "Já existe um processamento em andamento com este nome. Tente de novo em um minuto."}, 409)
            return self._json({"slug": slug, "aviso": "Processamento iniciado. As etapas dos agentes de texto continuam pelo Pelé."}, 202)
        r = self._post_perfis(u.path, b)
        if r is None:
            r = self._post_fluxo(u.path, b)
        if r is not None:
            return self._json(*r)
        m = re.fullmatch(r"/api/ajustar/([^/]+)/(\d{1,3})", u.path)
        if m:
            d = _projeto(unquote(m.group(1)))
            ident = int(m.group(2))
            if not d or not (d / "clipes" / f"{ident:02d}.mp4").is_file():
                return self._json({"erro": "Corte não encontrado."}, 404)
            if not (d / "transcricao.json").is_file() or not (d / "fonte.mp4").is_file():
                return self._json({"erro": "O vídeo original ou a transcrição não está no projeto; não dá para refazer o corte."}, 409)
            v, erro = validar_ajuste(d, b)
            if not v:
                return self._json({"erro": erro}, 400)
            args = ["ajustar", d.name, f"--id={ident}", f"--ini={v['ini']}", f"--fim={v['fim']}", f"--layout={v['layout']}"]
            if not v["legenda"]:
                args.append("--sem-legenda")
            if not v["audio"]:
                args.append("--sem-audio")
            try:
                lancar(d.name, args, "ajustar", ident)
            except RuntimeError:
                return self._json({"erro": "Este projeto já está processando algo. Espere terminar."}, 409)
            return self._json({"slug": d.name, "id": f"{ident:02d}"}, 202)
        m = re.fullmatch(r"/api/avaliar/([^/]+)(?:/(\d{1,3}))?", u.path)
        if m:  # plano B: o fluxo já roda o Totti; o botão cobre nota que faltou ou etapa que falhou
            d = _projeto(unquote(m.group(1)))
            if not d:
                return self._json({"erro": "Projeto não encontrado."}, 404)
            ident = int(m.group(2)) if m.group(2) else None
            if ident is not None and not (d / "clipes" / f"{ident:02d}.mp4").is_file():
                return self._json({"erro": "Corte não encontrado."}, 404)
            if ident is None and not any(not (d / "clipes" / f"{x.stem}.potencial.json").exists()
                                         for x in (d / "clipes").glob("[0-9][0-9].mp4")):
                return self._json({"erro": "Todos os cortes já têm avaliação."}, 409)
            args = ["avaliar", d.name] + (["--ids", str(ident)] if ident is not None else [])
            try:
                lancar(d.name, args, "avaliar", ident)
            except RuntimeError:
                return self._json({"erro": "Este projeto já está processando algo. Espere terminar."}, 409)
            return self._json({"slug": d.name, "id": f"{ident:02d}" if ident is not None else None}, 202)
        self._json({"erro": "rota desconhecida"}, 404)

    def _post_perfis(self, caminho: str, b: dict):
        """Rotas de escrita de perfis. Devolve (dados, código) ou None se a rota não é de perfis."""
        try:
            if caminho == "/api/perfis":
                p = b.get("perfil")
                if not isinstance(p, dict):
                    return {"erro": "Envie o perfil."}, 400
                return {"perfil": PF.salvar(p, novo=bool(b.get("novo")))}, 201 if b.get("novo") else 200
            m = re.fullmatch(r"/api/perfis/([a-z0-9-]{1,40})/(duplicar|arquivar)", caminho)
            if m:
                if m.group(2) == "duplicar":
                    return {"perfil": PF.duplicar(m.group(1), str(b.get("nome") or "")[:60] or None)}, 201
                return {"perfil": PF.arquivar(m.group(1), bool(b.get("arquivado", True)))}, 200
            m = re.fullmatch(r"/api/projeto/([^/]+)/perfil", caminho)
            if m:
                d = _projeto(unquote(m.group(1)))
                if not d:
                    return {"erro": "projeto não encontrado"}, 404
                if not isinstance(b.get("campos"), dict):
                    return {"erro": "Envie os campos."}, 400
                return {"perfil": PF.ajustar_projeto(d, b["campos"])}, 200
        except PF.PerfilInvalido as e:
            return {"erro": "Corrija o perfil: " + " ".join(e.erros), "erros": e.erros}, 400
        except KeyError:
            return {"erro": "Perfil não encontrado."}, 404
        return None

    def _post_fluxo(self, caminho: str, b: dict):
        """Fluxo, revisão das sugestões e execução. Devolve (dados, código) ou None se não é destas rotas."""
        if caminho == "/api/fluxo-padrao":
            try:
                return {"fluxo": T.gravar_padrao(b.get("fluxo") or {})}, 200
            except ValueError as e:
                return {"erro": "Fluxo inválido: " + " ".join(e.args[0]), "erros": e.args[0]}, 400
        m = re.fullmatch(r"/api/(fluxo|rodar|aprovar|momentos|texto|aprovar-texto)/([^/]+)(?:/(\d{1,3}))?", caminho)
        if not m:
            return None
        acao, d = m.group(1), _projeto(unquote(m.group(2)))
        if not d:
            return {"erro": "projeto não encontrado"}, 404
        ocupado = _trabalho(d.name) is not None
        if acao == "fluxo":
            if ocupado:
                return {"erro": "O projeto está processando. Espere terminar para mudar o fluxo."}, 409
            try:
                return {"fluxo": T.gravar(d, b.get("fluxo") or {}), "erros": []}, 200
            except ValueError as e:
                return {"erro": "Fluxo inválido: " + " ".join(e.args[0]), "erros": e.args[0]}, 400
        if acao == "momentos":
            if not m.group(3):
                return {"erro": "Informe a sugestão."}, 400
            if ocupado:
                return {"erro": "O projeto está processando. Espere terminar para decidir."}, 409
            try:
                ini, fim = b.get("ini"), b.get("fim")
                dur = duracao_fonte(d)
                if fim is not None and dur and float(fim) > dur + 0.5:
                    return {"erro": "O fim passa do vídeo original."}, 400
                from .pipeline import decidir
                res = decidir(d, int(m.group(3)), b.get("status"),
                              None if ini is None else float(ini), None if fim is None else float(fim))
                _atualiza_revisao(d)
                return {"momento": res}, 200
            except (ValueError, TypeError) as e:
                return {"erro": str(e)}, 400
        if acao == "texto":
            if not m.group(3):
                return {"erro": "Informe o corte."}, 400
            if ocupado:
                return {"erro": "O projeto está processando. Espere terminar para editar."}, 409
            try:
                from .pipeline import editar_texto
                return {"momento": editar_texto(d, int(m.group(3)), {k: b[k] for k in ("gancho", "fecho", "cta") if k in b})}, 200
            except (ValueError, TypeError) as e:
                return {"erro": str(e)}, 400
        if acao == "aprovar-texto":
            if ocupado:
                return {"erro": "O projeto está processando. Espere terminar para aprovar."}, 409
            try:
                from .pipeline import aprovar_texto
                aprovar_texto(d)
            except ValueError as e:
                return {"erro": str(e)}, 400
            try:
                lancar(d.name, ["rodar", d.name], "rodar")
            except RuntimeError:
                return {"erro": "Este projeto já está processando algo. Espere terminar."}, 409
            return {"ok": True}, 202
        if acao == "aprovar":
            from .orquestrador import aprovar
            aprovar(d)
            return {"ok": True}, 200
        # rodar
        desde = b.get("desde")
        if desde is not None and desde not in [e["id"] for e in T.ativas(d)]:
            return {"erro": "Etapa desconhecida ou desativada."}, 400
        args = ["rodar", d.name] + ([f"--desde={desde}"] if desde else []) + (["--refazer"] if b.get("refazer") else [])
        try:
            lancar(d.name, args, "rodar")
        except RuntimeError:
            return {"erro": "Este projeto já está processando algo. Espere terminar."}, 409
        return {"slug": d.name}, 202

    def log_message(self, *a):  # silencioso
        pass


def _ip_local() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as c:
            c.connect(("10.255.255.255", 1))
            return c.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def servir(porta: int = 8767, navegador: bool = True, rede: bool = False) -> None:
    global SENHA
    if rede:
        SENHA = secrets.token_urlsafe(6)
    srv = ThreadingHTTPServer(("0.0.0.0" if rede else "127.0.0.1", porta), H)
    url = f"http://127.0.0.1:{porta}/"
    print(f"Painel de Clipes em {url} (Ctrl+C para sair)")
    if rede:
        print(f"Em outro computador da mesma rede: http://{_ip_local()}:{porta}/?k={SENHA}")
        print("Só leitura. A senha vale até fechar o painel.", flush=True)
    if navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url + (f"?k={SENHA}" if SENHA else ""))).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
