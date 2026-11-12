"""Acesso pelo celular, na rede de casa. Desligado por padrão: sem `--rede` o servidor só escuta em 127.0.0.1, como sempre.

Com `--rede` o servidor escuta na rede local, e só quem digita a senha entra. Quem está no próprio computador (127.0.0.1) continua
sem senha. Defesas, na ordem em que valem:
- o endereço de quem chama precisa ser de rede privada (192.168.x, 10.x, 172.16-31.x): se um roteador encaminhar a porta para a
  internet, o endereço que chega é público e é recusado;
- o cabeçalho Host precisa ser um IP privado ou o nome do computador, o que barra páginas de outros sites que apontam para cá;
- sem a sessão, só a tela de senha existe; a API, os vídeos e os arquivos respondem 401;
- 5 erros de senha bloqueiam aquele aparelho por 5 minutos, mesmo que depois acerte.
É HTTP, sem criptografia: serve para o Wi-Fi de casa, não para a internet. A senha mora em estudio/dados/senha_rede.txt (gitignored).
"""
import hmac
import ipaddress
import os
import secrets
import socket
import threading
import time
from urllib.parse import urlparse

from .config import DADOS

COOKIE = "corte_sessao"
VALIDADE_S = 30 * 86400
MAX_ERROS = 5
BLOQUEIO_S = 300
LETRAS = "abcdefghjkmnpqrstuvwxyz23456789"  # sem 0/o/1/l/i: a senha é digitada no celular
_lock = threading.Lock()
_sessoes = {}  # token -> expira (epoch)
_erros = {}  # ip -> [quantos, desde quando]
_estado = {"rede": False, "senha": None}


def ativar(rede=True):
    _estado["rede"] = rede
    if rede:
        _estado["senha"] = senha_da_rede()


def rede_ativa():
    return _estado["rede"]


def senha_da_rede():
    """ESTUDIO_SENHA vence; senão a senha guardada; senão uma nova, gravada para valer nas próximas vezes."""
    if os.environ.get("ESTUDIO_SENHA"):
        return os.environ["ESTUDIO_SENHA"]
    arq = DADOS / "senha_rede.txt"
    try:
        s = arq.read_text(encoding="utf-8").strip()
        if s:
            return s
    except OSError:
        pass
    s = "-".join("".join(secrets.choice(LETRAS) for _ in range(5)) for _ in range(2))
    DADOS.mkdir(parents=True, exist_ok=True)
    arq.write_text(s + "\n", encoding="utf-8")
    return s


def e_local(ip):
    return ip in ("127.0.0.1", "::1")


def ip_permitido(ip):
    """Computador, ou rede privada com o acesso por rede ligado."""
    if e_local(ip):
        return True
    if not _estado["rede"]:
        return False
    try:
        a = ipaddress.ip_address(ip.split("%")[0])
    except ValueError:
        return False
    return a.is_private and not a.is_loopback and not a.is_unspecified


def _nome_host(cabecalho):
    h = (cabecalho or "").strip()
    if h.startswith("["):
        return h[1:h.find("]")] if "]" in h else h
    return h.rsplit(":", 1)[0] if h.count(":") == 1 else h


def host_permitido(cabecalho):
    """Um site de fora que aponta o próprio nome para cá (DNS rebinding) chega com o nome dele, que não passa aqui."""
    h = _nome_host(cabecalho).lower()
    if h in ("127.0.0.1", "localhost", "::1"):
        return True
    if not _estado["rede"]:
        return False
    try:
        return ipaddress.ip_address(h).is_private
    except ValueError:
        return h.endswith(".local") or h == socket.gethostname().lower()


def origem_da_mesma_pagina(origem, host):
    """O navegador manda Origin nos POST. Se vier, tem de ser a própria página: o que vem de outro site é recusado."""
    return not origem or urlparse(origem).netloc.lower() == (host or "").lower()


def _limpar(agora):
    for t in [t for t, exp in _sessoes.items() if exp < agora]:
        del _sessoes[t]


def sessao_valida(token):
    if not token:
        return False
    agora = time.time()
    with _lock:
        _limpar(agora)
        return any(hmac.compare_digest(token, t) for t in _sessoes)


def token_do_cookie(cabecalho):
    for parte in (cabecalho or "").split(";"):
        nome, _, valor = parte.strip().partition("=")
        if nome == COOKIE:
            return valor
    return None


def entrar(ip, senha):
    """(ok, motivo, token). Erro de senha conta; passado o limite, nem a senha certa entra até o bloqueio acabar."""
    agora = time.time()
    with _lock:
        n, desde = _erros.get(ip, (0, agora))
        if n >= MAX_ERROS and agora - desde < BLOQUEIO_S:
            return False, "bloqueado", None
        if n >= MAX_ERROS:
            n = 0
        certa = _estado["senha"] or ""
        if senha and certa and hmac.compare_digest(senha.strip().lower().encode(), certa.strip().lower().encode()):
            _erros.pop(ip, None)
            token = secrets.token_urlsafe(32)
            _sessoes[token] = agora + VALIDADE_S
            return True, None, token
        _erros[ip] = [n + 1, agora if n == 0 else desde]
        return False, "bloqueado" if n + 1 >= MAX_ERROS else "erro", None


def enderecos_da_rede():
    """Endereços do computador na rede de casa, para mostrar no terminal."""
    achados = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))  # não envia nada: só descobre por qual placa sairia
        achados.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip not in achados and ipaddress.ip_address(ip).is_private and not ip.startswith("169.254."):
                achados.append(ip)
    except OSError:
        pass
    return achados


PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Corte · Entrar</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;min-height:100dvh;display:grid;place-items:center;padding:16px;background:#0b0b0d;color:#f4f4f1;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{width:min(100%,360px);background:#16171a;border:1px solid #2b2d33;border-radius:12px;padding:22px}
.marca{display:flex;align-items:center;gap:8px;font-weight:750;font-size:1.1rem;margin-bottom:14px}
.logo{width:26px;height:26px;border-radius:6px;background:#FFC400;color:#111;display:grid;place-items:center;font-size:.75rem}
label{display:block;font-weight:600;font-size:.9rem;margin-bottom:6px}
input{width:100%;padding:11px 12px;font:inherit;background:#1f2125;color:#f4f4f1;border:1px solid #41444c;border-radius:8px}
button{width:100%;margin-top:14px;padding:12px;font:inherit;font-weight:650;background:#FFC400;color:#141414;border:0;border-radius:8px}
.erro{margin:0 0 12px;padding:9px 11px;border-radius:8px;background:rgba(255,90,70,.14);border:1px solid rgba(255,110,90,.5);color:#ff9b8f;font-size:.9rem}
.mudo{color:#8b8e97;font-size:.82rem;margin:14px 0 0}
</style></head><body><main>
<div class="marca"><span class="logo">&#9654;</span>Corte</div>
%AVISO%
<form method="post" action="/acesso/entrar">
<label for="senha">Senha</label>
<input id="senha" name="senha" type="password" autocomplete="current-password" autocapitalize="none" autocorrect="off" spellcheck="false" autofocus required>
<button type="submit">Entrar</button>
</form>
<p class="mudo">A senha aparece no terminal do computador, quando o Corte é aberto com --rede.</p>
</main></body></html>
"""
AVISOS = {
    "erro": '<p class="erro">Senha incorreta.</p>',
    "bloqueado": '<p class="erro">Muitas tentativas. Espere 5 minutos para tentar de novo.</p>',
}


def pagina_de_entrada(motivo=None):
    return PAGINA.replace("%AVISO%", AVISOS.get(motivo, "")).encode("utf-8")
