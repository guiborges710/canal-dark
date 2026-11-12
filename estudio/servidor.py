"""Servidor do estúdio (biblioteca padrão do Python). Só escuta em 127.0.0.1, a menos que seja aberto com --rede (ver acesso.py)."""
import json
import mimetypes
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from media import estilos

from . import acesso, agentes, ao_vivo, central, corte, cronograma, fluxo, grafos, materiais as M, painel, revisao, status_video, temas, trabalhos, troca_estilo
from .banco import um
from .config import REPO, WEB

BLOCO = 1 << 18
ERROS_DE_CONEXAO = (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)
mimetypes.add_type("audio/wav", ".wav")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("font/ttf", ".ttf")
LIMITE_UPLOAD = 30 << 20


class Manipulador(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Estudio"

    def log_message(self, *a):
        pass

    def _json(self, dados, codigo=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _erro(self, motivos, codigo=409):
        self._json({"erro": motivos if isinstance(motivos, list) else [motivos]}, codigo)

    def _corpo(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def _origem_local(self):
        """Uma página de outro site não pode mandar o estúdio aprovar nem gastar: só a própria origem chama a API."""
        host = (self.headers.get("Host") or "").split(":")[0]
        origem = self.headers.get("Origin")
        if host not in ("127.0.0.1", "localhost"):
            return False
        return not origem or urlparse(origem).hostname in ("127.0.0.1", "localhost")

    def _porteiro(self, metodo):
        """Quem chama pode? O computador passa como sempre; um aparelho da rede de casa só depois da senha. True = segue."""
        ip = self.client_address[0]
        host = self.headers.get("Host")
        origem = self.headers.get("Origin")
        caminho = urlparse(self.path).path
        if acesso.e_local(ip):
            if metodo == "POST" and not self._origem_local():
                return self._recusar("Origem não permitida.", 403)
            return True
        if not acesso.ip_permitido(ip) or not acesso.host_permitido(host):
            return self._recusar("Acesso não permitido.", 403)
        if metodo == "POST" and not acesso.origem_da_mesma_pagina(origem, host):
            return self._recusar("Origem não permitida.", 403)
        if metodo == "POST" and caminho == "/acesso/entrar":
            self._entrar(ip)
            return False
        if acesso.sessao_valida(acesso.token_do_cookie(self.headers.get("Cookie"))):
            return True
        if metodo == "GET" and (caminho == "/" or caminho.startswith(("/producao/", "/estudio/", "/editor/", "/agentes", "/fluxos", "/central", "/painel"))):
            corpo = acesso.pagina_de_entrada(parse_qs(urlparse(self.path).query).get("acesso", [None])[0])
            self.send_response(401)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(corpo)
            return False
        return self._recusar("Entre com a senha.", 401)

    def _so_computador(self):
        """O painel só abre no computador: IP local E Host 127.0.0.1/localhost (a rede e o DNS rebinding levam 403). True = segue."""
        host = (self.headers.get("Host") or "").split(":")[0]
        if acesso.e_local(self.client_address[0]) and host in ("127.0.0.1", "localhost"):
            return True
        self._erro("O painel só abre no computador.", 403)
        return False

    def _arquivo_app(self, caminho_url):
        """Serve arquivos da casca, depois de decodificar e confinar o caminho."""
        try:
            rel = unquote(caminho_url, errors="strict")
        except (UnicodeDecodeError, ValueError):
            return self._erro("Caminho inválido.", 400)
        if "%" in rel or "\\" in rel or "\x00" in rel or any(p in (".", "..") for p in rel.split("/")):
            return self._erro("Caminho inválido.", 400)
        raiz = (REPO / "ecossistema" / "app").resolve()
        destino = (raiz / (rel or "index.html")).resolve()
        if destino != raiz and raiz not in destino.parents:
            return self._erro("Caminho inválido.", 400)
        return self._arquivo(destino)

    def _sistema_get(self, chave):
        """Dispatch fechado de recursos públicos; a chave nunca é um caminho."""
        recursos = {
            "setores": lambda: {"setores": central.SETORES},
            "sprint-ativa": central.sprint_ativa,
            "quadro": central.quadro,
            "agentes": lambda: {"agentes": central.agentes()},
        }
        recurso = recursos.get(chave)
        if recurso is None:
            return self._erro("Recurso do sistema não encontrado.", 404)
        try:
            return self._json(recurso())
        except Exception:
            return self._erro("Não foi possível carregar este recurso.", 500)

    def _recusar(self, motivo, codigo):
        self.close_connection = True  # um POST recusado não teve o corpo lido: reaproveitar a conexão corromperia o próximo pedido
        self._erro(motivo, codigo)
        return False

    def _entrar(self, ip):
        n = int(self.headers.get("Content-Length") or 0)
        campos = parse_qs(self.rfile.read(min(n, 2048)).decode("utf-8", "replace")) if n else {}
        ok, motivo, token = acesso.entrar(ip, (campos.get("senha") or [""])[0])
        self.send_response(303)
        self.send_header("Location", "/" if ok else f"/?acesso={motivo}")
        if ok:
            self.send_header("Set-Cookie", f"{acesso.COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age={acesso.VALIDADE_S}")
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _arquivo(self, caminho, tipo=None, nome_download=None, imutavel=False):
        caminho = Path(caminho)
        if not caminho.is_file():
            return self._erro("Arquivo não encontrado.", 404)
        tamanho = caminho.stat().st_size
        tipo = tipo or mimetypes.guess_type(caminho.name)[0] or "application/octet-stream"
        ini, fim, parcial = 0, tamanho - 1, False
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                ini = int(m.group(1))
                fim = min(int(m.group(2)), tamanho - 1) if m.group(2) else tamanho - 1
            else:
                ini = max(0, tamanho - int(m.group(2)))
            if ini > fim or ini >= tamanho:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{tamanho}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            parcial = True
        self.send_response(206 if parcial else 200)
        self.send_header("Content-Type", tipo)
        self.send_header("Accept-Ranges", "bytes")  # sem isso o player não consegue buscar um ponto do áudio ou vídeo
        self.send_header("Content-Length", str(fim - ini + 1))
        if parcial:
            self.send_header("Content-Range", f"bytes {ini}-{fim}/{tamanho}")
        self.send_header("Cache-Control", "public, max-age=31536000, immutable" if imutavel else "no-cache")
        if nome_download:
            self.send_header("Content-Disposition", f'attachment; filename="{nome_download}"')
        self.end_headers()
        with caminho.open("rb") as f:
            f.seek(ini)
            faltam = fim - ini + 1
            while faltam > 0:
                bloco = f.read(min(BLOCO, faltam))
                if not bloco:
                    break
                self.wfile.write(bloco)
                faltam -= len(bloco)
        return None

    def _caminho_ruim(self):
        """O slug vem da URL e vira pasta: `..` nunca é um projeto."""
        return bool(re.search(r"(^|/)\.\.?(/|$)", urlparse(self.path).path))

    def do_GET(self):
        if not self._porteiro("GET"):
            return None
        if self._caminho_ruim():
            return self._erro("Caminho inválido.", 400)
        try:
            self._rota_get()
        except ERROS_DE_CONEXAO:
            self.close_connection = True
        except fluxo.Recusado as r:
            self._erro(r.motivos, r.codigo)
        except FileNotFoundError:
            self._erro("Arquivo não encontrado.", 404)
        except Exception:  # noqa: BLE001
            self._erro("Erro interno. Tente novamente.", 500)

    def do_POST(self):
        if not self._porteiro("POST"):
            return None
        if self._caminho_ruim():
            self.close_connection = True
            return self._erro("Caminho inválido.", 400)
        try:
            self._rota_post()
        except ERROS_DE_CONEXAO:
            self.close_connection = True
        except fluxo.Recusado as r:
            self._erro(r.motivos, r.codigo)
        except Exception:  # noqa: BLE001
            self._erro("Erro interno. Tente novamente.", 500)
        return None

    def _rota_get(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        c = u.path
        if c == "/financas" or c.startswith("/financas/"):
            if not self._so_computador():
                return
            rel = c[len("/financas/"):] if c.startswith("/financas/") else "index.html"
            return self._arquivo_app(rel)
        if c == "/" or c.startswith(("/producao/", "/estudio/", "/editor/", "/agentes", "/fluxos")):
            return self._arquivo(WEB / "index.html", "text/html; charset=utf-8")
        if c == "/central":
            return self._arquivo(WEB / "central.html", "text/html; charset=utf-8")
        if c == "/painel" or c.startswith("/painel/"):
            if not self._so_computador():
                return
            return self._arquivo(WEB / "painel.html", "text/html; charset=utf-8")
        if c.startswith("/api/painel/"):
            if not self._so_computador():
                return
            return self._painel_get(c[len("/api/painel/"):], q)
        m = re.fullmatch(r"/api/sistema/([a-z][a-z0-9-]{0,31})", c)
        if m:
            if not self._so_computador():
                return
            return self._sistema_get(m.group(1))
        if c == "/api/central/setores":
            return self._json({"setores": central.SETORES})
        if c == "/api/sprints/ativa":
            return self._json(central.sprint_ativa())
        if c == "/api/central/quadro":
            return self._json(central.quadro())
        if c == "/api/agentes/status":
            return self._json({"agentes": central.agentes()})
        m = re.fullmatch(r"/api/central/agentes/([\w-]+)", c)
        if m:
            return self._json(central.agente(m.group(1)))
        m = re.fullmatch(r"/fontes/(Kalam-Bold\.ttf)", c)
        if m:
            return self._arquivo(REPO / "media" / "fonts" / m.group(1), imutavel=True)
        m = re.fullmatch(r"/quadro/([0-9a-f]{64})", c)
        if m:
            return self._arquivo(corte.quadro_de(m.group(1), float(q.get("t", 0)), max(40, min(1080, int(q.get("l", 216))))), "image/jpeg", imutavel=True)
        if c.startswith("/web/"):
            alvo = (WEB / c[5:]).resolve()
            if WEB.resolve() not in alvo.parents:
                return self._erro("Caminho inválido.", 400)
            return self._arquivo(alvo)
        m = re.fullmatch(r"/blob/([0-9a-f]{64})", c)
        if m:
            nome = q.get("nome", "")
            return self._arquivo(M.caminho_blob(m.group(1)), mimetypes.guess_type(nome)[0], imutavel=True)
        m = re.fullmatch(r"/download/([\w.-]+)", c)
        if m:
            return self._download(m.group(1), q.get("versao"))
        if c == "/api/producoes":
            return self._json({"grupos": fluxo.listar(), "integracoes": trabalhos.integracoes()})
        if c == "/api/opcoes":
            return self._json({"fluxos": [x for x in grafos.listar() if x["publicada"]], "legendas": corte.PRESETS_LEGENDA, "estilos": estilos.publico(), "formatos": [{"id": "vertical", "nome": "Short 9:16", "detalhe": "1080 × 1920, 30 fps"}, {"id": "horizontal", "nome": "Horizontal 16:9", "detalhe": "1920 × 1080, só no estilo Scratch"}], "padrao": {"duracao": 30, "idioma": "pt-BR", "formato": "vertical", "estilo": estilos.PADRAO, "legenda": "nenhum"}})
        if c == "/api/videos/status":
            return self._json(status_video.todos())  # só leitura (PROG-012)
        if c == "/api/cronograma":
            return self._json(cronograma.calcular(usar_config=True))  # só leitura e só sugestão (PROG-011)
        if c == "/api/temas":
            return self._json(temas.listar())
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/estilo", c)
        if m:
            return self._json({"atual": troca_estilo.descrever(m.group(1)), "estilos": estilos.publico()})
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/estudio", c)
        if m:
            return self._json(revisao.vista_estudio(m.group(1)))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/corte", c)
        if m:
            fluxo.garantir_producao(m.group(1))
            return self._json(corte.vista(m.group(1)))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/corte/audio", c)
        if m:
            return self._arquivo(corte.audio_previa(m.group(1)), "audio/wav")
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/corte/galeria", c)
        if m:
            return self._json({"itens": corte.galeria(m.group(1))})
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/tomadas", c)
        if m:
            return self._json({"tomadas": revisao.tomadas(m.group(1), int(q.get("cena", 0)))})
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/thumbnail", c)
        if m:
            return self._json({"thumbnail": revisao.thumbnail(m.group(1))})
        if c == "/api/agentes":
            return self._json({"agentes": _com_usos(agentes.catalogo()), "opcoes": agentes.opcoes()})
        if c == "/api/agentes/ao-vivo":  # antes da rota de <id>: "ao-vivo" casaria com [\w-]+ (PROG-003)
            try:
                return self._json(ao_vivo.montar())
            except Exception as e:
                return self._erro(f"Não foi possível ler o estado ao vivo: {type(e).__name__}.", 500)
        m = re.fullmatch(r"/api/agentes/([\w-]+)", c)
        if m:
            return self._json({**agentes.detalhe(m.group(1)), "opcoes": agentes.opcoes()})
        m = re.fullmatch(r"/api/agentes/([\w-]+)/comparar", c)
        if m:
            return self._json(agentes.comparar(m.group(1), int(q["a"]), int(q["b"])))
        m = re.fullmatch(r"/api/agentes/([\w-]+)/versao/(\d+)", c)
        if m:
            return self._json(agentes.texto_da_versao(m.group(1), int(m.group(2))))
        if c == "/api/fluxos":
            return self._json({"fluxos": grafos.listar()})
        m = re.fullmatch(r"/api/fluxos/([\w-]+)", c)
        if m:
            return self._json(grafos.detalhe(m.group(1)))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)", c)
        if m:
            return self._json(fluxo.estado(m.group(1)))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/material/(\w+)", c)
        if m:
            return self._json(fluxo.conteudo(m.group(1), m.group(2), int(q["versao"]) if q.get("versao") else None))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/detalhes", c)
        if m:
            return self._json(fluxo.detalhes(m.group(1)))
        m = re.fullmatch(r"/api/jobs/(\d+)/log", c)
        if m:
            return self._json({"log": trabalhos.ler_log(int(m.group(1)))})
        if c == "/api/clipes":
            from . import clipes_routes
            return self._json(clipes_routes.listar_projetos())
        if c == "/api/eventos":
            return self._sse()
        return self._erro("Rota não encontrada.", 404)

    def _painel_get(self, rota, q):
        """Painel (PROG-018 a 023): só leitura; o documento só sai se estiver no índice da lista de permissão."""
        if rota == "visao":
            return self._json(painel.visao())
        if rota == "documentos":
            return self._json(painel.documentos(q.get("area") or None, q.get("q") or None, q.get("limite", 100), q.get("offset", 0)))
        if rota == "documento":
            dados, codigo = painel.documento(q.get("caminho", ""))
            return self._json(dados, codigo)
        if rota == "mudancas":
            return self._json(painel.mudancas(q.get("desde")))
        if rota == "resumo":
            return self._json(painel.resumo())
        if rota == "setores":
            return self._json(painel.setores())
        return self._erro("Rota do painel desconhecida.", 404)

    def _rota_post(self):
        u = urlparse(self.path)
        c = u.path
        if c == "/api/financas/movimentos/editar":
            if not self._so_computador():
                return
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > 16_384:
                if n > 16_384:
                    self.close_connection = True  # o corpo não foi consumido; não reutilizar a conexão com bytes pendentes
                return self._erro("Pedido vazio ou grande demais.", 413 if n > 16_384 else 400)
            d = json.loads(self.rfile.read(n).decode("utf-8"))
            from . import financas_edicao
            with financas_edicao.TRAVA:
                try:
                    editado = financas_edicao.editar(d)
                except financas_edicao.EdicaoRecusada as e:
                    return self._erro(str(e), e.codigo)
                try:
                    from .dados import gerar_financas
                    dados = gerar_financas.gerar(REPO / "financas")
                    gerar_financas.gravar(dados, REPO / "ecossistema" / "app" / "dados")
                except Exception:
                    try:
                        financas_edicao.restaurar_backup(editado["backup"], editado["sha256"])
                    except financas_edicao.EdicaoRecusada as erro:
                        return self._erro(str(erro), erro.codigo)
                    return self._erro("Não consegui atualizar o dashboard; o lançamento original foi restaurado.", 500)
            return self._json({"ok": True, "gerado_em": dados["gerado_em"]})
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/enviar/(asset|componente|thumbnail)", c)
        if m:
            return self._upload(m.group(1), m.group(2), {k: v[0] for k, v in parse_qs(u.query).items()})
        d = self._corpo()
        m = re.fullmatch(r"/api/central/acao/(\w+)", c)
        if m:
            try:
                return self._json(central.acao(m.group(1), d), 201)
            except ValueError as e:
                return self._erro(str(e), 400)
        if c == "/api/temas/gerar":
            return self._json(temas.gerar(), 201)
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/estilo/impacto", c)
        if m:
            return self._json(troca_estilo.impacto(m.group(1), d.get("estilo"), d.get("variante"), d.get("opcoes")))
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/estilo", c)
        if m:
            return self._json(troca_estilo.trocar(m.group(1), d.get("estilo"), d.get("variante"), d.get("opcoes"), d.get("confirmar")))
        if c == "/api/producoes":
            return self._json({"slug": fluxo.criar_producao(d.get("tema"), d.get("formato", "vertical"), d.get("estilo", "sketch"), bool(d.get("simulado")), d.get("fluxo"), d.get("legenda"), d.get("briefing"), d.get("duracao"), d.get("variante"), d.get("opcoes"))}, 201)
        if c == "/api/fluxos":
            return self._json(grafos.criar_fluxo(d.get("nome"), d.get("copiar_de")), 201)
        m = re.fullmatch(r"/api/fluxos/([\w-]+)/(\w+)", c)
        if m:
            return self._post_fluxo(m.group(1), m.group(2), d)
        if c == "/api/agentes":
            return self._json(agentes.criar(d), 201)
        m = re.fullmatch(r"/api/agentes/([\w-]+)/(\w+)", c)
        if m:
            return self._post_agente(m.group(1), m.group(2), d)
        m = re.fullmatch(r"/api/execucoes/(\d+)/(\w+)", c)
        if m:
            return self._post_execucao(int(m.group(1)), m.group(2), d)
        m = re.fullmatch(r"/api/producoes/([\w.-]+)/(\w+)", c)
        if m:
            slug, acao = m.groups()
            fluxo.garantir_producao(slug)
            if acao == "aprovar":
                return self._json({"iniciados": fluxo.aprovar(slug, d["material"], d["versao_id"])})
            if acao == "item":
                return self._json({"iniciados": fluxo.decidir_item(slug, d["material"], d["versao_id"], d["item"], d["decisao"])})
            if acao == "feedback":
                return self._json(fluxo.anotar_feedback(slug, d["material"], d["versao_id"], d.get("texto"), d.get("item"), d.get("cena"), d.get("tempo_s"), d.get("categoria")), 201)
            if acao == "remover_feedback":
                fluxo.remover_feedback(slug, d["id"])
                return self._json({"ok": True})
            if acao == "enviar_ajustes":
                return self._json({"jobs": [j["id"] for j in fluxo.enviar_ajustes(slug, d["material"], d["versao_id"])]}, 201)
            if acao == "resolver_parecer":
                return self._json(fluxo.resolver_parecer_vini(slug), 201)
            if acao == "pular_vini":
                return self._json(fluxo.pular_auditoria_vini(slug, d.get("etapa"), d.get("escopo")))
            if acao == "manter_cenas_aprovadas":
                return self._json(fluxo.manter_cenas_aprovadas(slug))
            if acao == "iniciar":
                ex = um("SELECT id FROM execucoes WHERE slug=? AND status='ativa'", slug)
                if ex and (fluxo.POR_ID.get(d["etapa"]) or {}).get("agente") and not d.get("forcar"):  # produção conduzida por grafo: quem decide o que roda é o grafo
                    iniciados = grafos.avancar(ex["id"])
                    return self._json({"job": None, "novo": bool(iniciados), "iniciados": iniciados, "motivos": [] if iniciados else ["O fluxo não tinha nenhum passo novo para iniciar: veja qual nó está esperando (falha, aprovação ou início manual)."]}, 201 if iniciados else 200)
                job, novo = fluxo.iniciar_etapa(slug, d["etapa"], bool(d.get("forcar")), d.get("escopo"))
                return self._json({"job": job["id"], "novo": novo}, 201 if novo else 200)
            if acao == "arquivar":
                fluxo.arquivar(slug, d.get("arquivada", True))
                return self._json({"ok": True})
            if acao == "corte_salvar":
                corte.salvar(slug, d["estado"], d.get("rev"))
                return self._json(corte.vista(slug))
            if acao == "corte_versao":
                return self._json(corte.nova_versao(slug, d.get("nota")), 201)
            if acao == "corte_restaurar":
                corte.restaurar_versao(slug, int(d["numero"]), d.get("rev"))
                return self._json(corte.vista(slug))
            if acao == "corte_aplicar":
                r = corte.aplicar_conflitos(slug, d.get("ids") or [], d.get("rev"))
                return self._json({**corte.vista(slug), "aplicados": r["aplicados"], "ressincronizar": r["ressincronizar"]})
            if acao == "corte_recomecar":
                return self._json(corte.recomecar(slug))
            if acao == "corte_fontes":
                return self._json(corte.pedir_fontes(slug), 201)
            if acao == "corte_exportar":
                return self._json(corte.pedir_exportacao(slug, bool(d.get("confirmado"))), 201)
            if acao == "editar_cena":
                return self._json(revisao.editar_cena(slug, int(d["cena"]), d["campo"], d.get("valor")))
            if acao == "editar_roteiro":
                return self._json(revisao.editar_roteiro(slug, d.get("texto")))
            if acao == "editar_metadados":
                return self._json(revisao.editar_metadados(slug, d))
            if acao == "usar_tomada":
                return self._json(revisao.usar_tomada(slug, int(d["cena"]), d["sha"]))
            if acao == "decidir_thumbnail":
                return self._json({"thumbnail": revisao.decidir_thumbnail(slug, d.get("decisao"))})
            if acao == "executar":
                return self._json({"execucao": grafos.iniciar_execucao(slug, d.get("fluxo") or grafos.PADRAO, bool(d.get("forcar")))}, 201)
        m = re.fullmatch(r"/api/jobs/(\d+)/(\w+)", c)
        if m:
            job_id, acao = int(m.group(1)), m.group(2)
            if acao == "tentar":
                job, novo = fluxo.tentar_novamente(job_id)
                return self._json({"job": job["id"], "novo": novo}, 201 if novo else 200)
            if acao == "cancelar":
                trabalhos.cancelar(job_id)
                return self._json({"ok": True})
            if acao == "dispensar":
                fluxo.dispensar_falha(job_id)
                return self._json({"ok": True})
        if c == "/api/clipes/novo":
            from . import clipes_routes
            return self._json(clipes_routes.iniciar_projeto(
                d.get("url", ""),
                d.get("autor", ""),
                d.get("autorizacao", ""),
                d.get("perfil", "geral")
            ), 201)
        m = re.fullmatch(r"/api/clipes/ajustar/([\w.-]+)/(\d+)", c)
        if m:
            from . import clipes_routes
            return self._json(clipes_routes.ajustar_corte(
                m.group(1),
                int(m.group(2)),
                d.get("ini", 0.0),
                d.get("fim", 0.0),
                d.get("layout", "borrado")
            ), 201)
        return self._erro("Rota não encontrada.", 404)

    def _sse(self):
        """GET /api/eventos: Server-Sent Events com atualizações de projetos de clipes."""
        from . import clipes_routes

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Enviar heart-beat inicial
        try:
            self.wfile.write(b": SSE conectado\n\n")
            self.wfile.flush()
        except ERROS_DE_CONEXAO:
            return

        # Criar cliente SSE e registrar
        cliente = clipes_routes.ClienteSSE(self.wfile.write)
        clipes_routes.registrar_sse(cliente)

        try:
            # Manter a conexão aberta; cliente será notificado por notificar_sse()
            # Enviar heart-beat a cada 30s para manter a conexão
            import time
            ultima_pulsacao = time.time()
            while True:
                time.sleep(5)
                now = time.time()
                if now - ultima_pulsacao > 30:
                    try:
                        self.wfile.write(b": heart-beat\n\n")
                        self.wfile.flush()
                        ultima_pulsacao = now
                    except ERROS_DE_CONEXAO:
                        break
        except ERROS_DE_CONEXAO:
            pass
        finally:
            clipes_routes.remover_sse(cliente)

    def _upload(self, slug, destino, q):
        n = int(self.headers.get("Content-Length") or 0)
        if n > LIMITE_UPLOAD:
            self.close_connection = True  # o corpo não foi lido: reaproveitar a conexão corromperia o próximo pedido
            return self._erro("Arquivo grande demais (máximo 30 MB).", 413)
        corpo = self.rfile.read(n)
        fluxo.garantir_producao(slug)
        if destino == "asset":
            return self._json(corte.adicionar_asset(slug, q.get("nome"), corpo), 201)
        if destino == "componente":
            return self._json(revisao.substituir_componente(slug, q.get("item"), corpo), 201)
        return self._json({"thumbnail": revisao.substituir_thumbnail(slug, corpo)}, 201)

    def _post_fluxo(self, ident, acao, d):
        if acao == "salvar":
            return self._json(grafos.salvar_rascunho(ident, d["grafo"], d.get("nome")))
        if acao == "publicar":
            return self._json(grafos.publicar(ident, d.get("nota")), 201)
        if acao == "ensaiar":
            return self._json(grafos.ensaiar(grafos._limpar_grafo(d["grafo"]), d["slug"]))
        if acao == "impacto":
            return self._json(grafos.impacto_desativar(grafos._limpar_grafo(d["grafo"]), d["no"]))
        if acao == "restaurar":
            return self._json(grafos.restaurar_rascunho(ident, int(d["numero"])))
        return self._erro("Rota não encontrada.", 404)

    def _post_agente(self, ident, acao, d):
        if acao == "salvar":
            return self._json(agentes.salvar(ident, d, d.get("versao_vista")))
        if acao == "duplicar":
            return self._json(agentes.duplicar(ident, d.get("novo")), 201)
        if acao == "ativar":
            return self._json(agentes.alternar(ident, bool(d.get("ativo"))))
        if acao == "restaurar":
            return self._json(agentes.restaurar(ident, int(d["numero"])))
        if acao == "testar":
            return self._json(agentes.testar(ident, d.get("entrada"), d.get("projeto"), d.get("versao")), 201)
        return self._erro("Rota não encontrada.", 404)

    def _post_execucao(self, ident, acao, d):
        if acao == "aprovar":
            return self._json(grafos.aprovar_no(ident, d["no"], d["versao_id"]))
        if acao == "liberar":
            return self._json(grafos.liberar_no(ident, d["no"]))
        if acao == "repetir":
            return self._json(grafos.repetir_no(ident, d["no"]))
        if acao == "devolver":
            return self._json(grafos.devolver(ident, d["no"], d.get("texto"), d.get("cena"), d.get("tempo_s"), d.get("categoria"), d.get("item")), 201)
        return self._erro("Rota não encontrada.", 404)

    def _download(self, slug, versao):
        """Só entrega a versão aprovada: é o que garante que o arquivo baixado é o que passou pela revisão."""
        v = fluxo.versao_dict(um("SELECT * FROM versoes WHERE slug=? AND material='video' AND id=?", slug, int(versao or 0)))
        if not v or not um("SELECT id FROM aprovacoes WHERE versao_id=?", v["id"]):
            return self._erro("Esta versão ainda não foi aprovada.", 403)
        return self._arquivo(M.caminho_blob(v["manifesto"]["arquivos"]["video.mp4"]), "video/mp4", f"{slug}-v{v['numero']}.mp4")


def _com_usos(lista):
    usos = {}
    for a in lista:
        usos[a["id"]] = grafos.usos_do_agente(a["id"])
    return [{**a, "instrucoes": None, "usos": sorted({u["fluxo_nome"] for u in usos[a["id"]]})} for a in lista]


def servir(porta, rede=False):
    parar = threading.Event()
    threading.Thread(target=trabalhos.monitor, args=(parar,), daemon=True).start()
    acesso.ativar(rede)
    servidor = ThreadingHTTPServer(("0.0.0.0" if rede else "127.0.0.1", porta), Manipulador)
    servidor.daemon_threads = True
    try:
        servidor.serve_forever()
    finally:
        parar.set()
        servidor.server_close()
