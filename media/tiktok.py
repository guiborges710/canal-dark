"""Upload de vídeos para o TikTok (Content Posting API, OAuth 2.0).

Espelha o media/youtube.py. O modelo do canal continua o mesmo: o UPLOAD é
automático, a PUBLICAÇÃO é manual. Aqui o vídeo sobe direto para os RASCUNHOS
(Drafts) da sua conta TikTok, via o endpoint de "inbox". Você abre o app do
TikTok, revisa (legenda, som, capa, privacidade) e publica.

Esse caminho (escopo `video.upload`) funciona de imediato, inclusive com app em
sandbox / não auditado — ao contrário do "direct post", que exige auditoria do
app pelo TikTok para postar em público. Nada aqui torna o vídeo público sozinho.

Pré-requisitos (uma vez só, manuais — veja TIKTOK_SETUP.md):
  1. Ter a conta do canal no TikTok.
  2. Criar um app em https://developers.tiktok.com (produto "Content Posting API",
     escopo video.upload) e pegar Client key / Client secret.
  3. Pôr TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET no .env (gitignored).
  4. Rodar `python run.py publish --to tiktok ...` e autorizar uma vez no navegador.

O token fica em .tiktok_token.json (gitignored) e é renovado sozinho depois.
"""
import json
import time
import urllib.parse
from pathlib import Path

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
INBOX_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
API_BASE = "https://open.tiktokapis.com"
SCOPES = "video.upload"


def _require_libs():
    try:
        import requests  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise SystemExit(
            "Falta a lib `requests` para o upload no TikTok. Instale com:\n"
            "  .venv/bin/pip install requests\n"
            f"(detalhe: {e})")


def _env(name):
    import os
    v = os.environ.get(name)
    return v.strip() if v else None


def _save_token(token_file: Path, data: dict):
    data = dict(data)
    data["_obtained_at"] = int(time.time())
    token_file.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def _exchange(requests, client_key, client_secret, **params):
    body = {"client_key": client_key, "client_secret": client_secret, **params}
    r = requests.post(TOKEN_URL, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    data = r.json()
    if "error" in data and data.get("error") not in (None, ""):
        raise SystemExit(f"TikTok OAuth falhou: {data.get('error')} — {data.get('error_description')}")
    if "access_token" not in data:
        raise SystemExit(f"TikTok OAuth: resposta inesperada: {data}")
    return data


def _credentials(root: Path, cfg_pub: dict, token_file: Path):
    """Carrega o token salvo (renovando se expirou) ou abre o consentimento uma vez."""
    import requests
    client_key = _env("TIKTOK_CLIENT_KEY")
    client_secret = _env("TIKTOK_CLIENT_SECRET")
    if not (client_key and client_secret):
        raise SystemExit(
            "Faltam TIKTOK_CLIENT_KEY e/ou TIKTOK_CLIENT_SECRET no .env.\n"
            "Crie um app em https://developers.tiktok.com (Content Posting API, escopo video.upload) "
            "e copie as chaves. Passo a passo em TIKTOK_SETUP.md.")

    if token_file.exists():
        tok = json.loads(token_file.read_text(encoding="utf-8"))
        age = int(time.time()) - int(tok.get("_obtained_at", 0))
        # access_token dura ~24h; renova com folga usando o refresh_token.
        if tok.get("access_token") and age < int(tok.get("expires_in", 86400)) - 600:
            return tok["access_token"]
        if tok.get("refresh_token"):
            data = _exchange(requests, client_key, client_secret,
                             grant_type="refresh_token", refresh_token=tok["refresh_token"])
            _save_token(token_file, data)
            return data["access_token"]

    # Primeira vez: consentimento no navegador (fluxo de colar o código).
    redirect_uri = cfg_pub.get("tiktok_redirect_uri", "https://localhost/callback")
    state = "canaldark"
    q = urllib.parse.urlencode({
        "client_key": client_key,
        "scope": SCOPES,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state,
    })
    print("\n  Autorize o canal no TikTok abrindo este link no navegador onde a conta está logada:\n")
    print(f"    {AUTH_URL}?{q}\n")
    print(f"  Depois de autorizar, o TikTok redireciona para {redirect_uri}?code=...&state=...")
    print("  Copie a URL inteira da barra de endereço (ou só o valor de code=) e cole aqui.\n")
    pasted = input("  code / URL de retorno: ").strip()
    code = pasted
    if "code=" in pasted:
        parsed = urllib.parse.urlparse(pasted)
        code = urllib.parse.parse_qs(parsed.query).get("code", [pasted])[0]
    code = urllib.parse.unquote(code)
    data = _exchange(requests, client_key, client_secret,
                     grant_type="authorization_code", code=code, redirect_uri=redirect_uri)
    _save_token(token_file, data)
    return data["access_token"]


def _caption(out: Path, meta: dict, max_len: int = 2200) -> str:
    """Legenda do TikTok: título + descrição + hashtags a partir das tags."""
    titulo = meta.get("titulo", "").strip()
    desc = meta.get("descricao", "").strip()
    tags = meta.get("tags", []) or []
    hashtags = " ".join("#" + "".join(ch for ch in t if ch.isalnum()) for t in tags if t.strip())
    parts = [p for p in (titulo, desc, hashtags) if p]
    return "\n\n".join(parts)[:max_len]


def upload(cfg, out: Path, root: Path):
    """Sobe out/video.mp4 para os RASCUNHOS do TikTok. Devolve dict com publish_id.

    Não publica em público: o vídeo fica em Drafts para você finalizar no app.
    """
    _require_libs()
    import requests

    pub = cfg.get("publish", {}) or {}
    video_file = out / "video.mp4"
    if not video_file.exists():
        raise SystemExit(f"Falta {video_file}. Gere o vídeo antes de publicar.")
    meta_file = out / "metadados.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}

    token_file = root / pub.get("tiktok_token_file", ".tiktok_token.json")
    access_token = _credentials(root, pub, token_file)

    size = video_file.stat().st_size
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    # Vídeo pequeno (shorts): envia em um único chunk.
    init_body = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": size,
            "total_chunk_count": 1,
        }
    }
    r = requests.post(INBOX_INIT_URL, headers=headers, json=init_body, timeout=30)
    data = r.json()
    err = (data.get("error") or {})
    if err.get("code") not in (None, "ok"):
        raise SystemExit(f"TikTok init falhou: {err.get('code')} — {err.get('message')} "
                         f"(log_id {err.get('log_id')})")
    publish_id = data["data"]["publish_id"]
    upload_url = data["data"]["upload_url"]

    print(f"   Enviando {video_file.name} para os rascunhos do TikTok ({size} bytes)...", flush=True)
    with open(video_file, "rb") as f:
        blob = f.read()
    put = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(size),
            "Content-Range": f"bytes 0-{size - 1}/{size}",
        },
        data=blob, timeout=300)
    if put.status_code not in (200, 201, 206):
        raise SystemExit(f"TikTok upload falhou (HTTP {put.status_code}): {put.text[:300]}")
    print("   Vídeo enviado. Está nos RASCUNHOS do TikTok — abra o app para revisar e publicar.", flush=True)

    result = {
        "publish_id": publish_id,
        "status": "draft (inbox)",
        "title": meta.get("titulo", ""),
        "caption_suggestion": _caption(out, meta),
        "where": "Abra o app TikTok > Perfil > Rascunhos para finalizar e publicar.",
    }
    (out / "upload_tiktok.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result
