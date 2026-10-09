"""Upload de vídeos para o YouTube (OAuth 2.0).

Diferente da YOUTUBE_API_KEY (que é só leitura, usada no `ideas`), o upload exige
OAuth: um "client secret" de um app no Google Cloud + o seu consentimento uma única vez.
O token gerado fica em .youtube_token.json (gitignored) e é reutilizado nas próximas vezes.

Modo padrão do canal: sobe o vídeo como PRIVADO. Assim funciona de imediato, sem a
verificação (audit) do app pelo Google. Você revê no YouTube Studio e clica em publicar.

Nada aqui publica em público sozinho. Nada envia chaves a terceiros além do próprio Google.
"""
import json
from pathlib import Path

# Escopos: enviar o vídeo e definir a miniatura.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _require_libs():
    try:
        import google_auth_oauthlib.flow  # noqa: F401
        import googleapiclient.discovery  # noqa: F401
        import googleapiclient.http  # noqa: F401
        import google.auth.transport.requests  # noqa: F401
        from google.oauth2.credentials import Credentials  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "Faltam as bibliotecas do Google para o upload. Instale com:\n"
            "  .venv/bin/pip install google-api-python-client google-auth-oauthlib google-auth-httplib2\n"
            f"(detalhe: {e})")


def _credentials(root: Path, client_secret: Path, token_file: Path):
    """Carrega o token salvo ou abre o consentimento no navegador na primeira vez."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import google_auth_oauthlib.flow

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds
    # Primeira vez: precisa do client_secret e do consentimento no navegador.
    if not client_secret.exists():
        raise SystemExit(
            f"Não encontrei o arquivo de credenciais OAuth em {client_secret}.\n"
            "Baixe o 'client secret' (tipo Desktop/App para computador) do seu projeto no "
            "Google Cloud e salve nesse caminho (veja os passos no README/CLAUDE.md).")
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        str(client_secret), SCOPES)
    # open_browser=False: imprime o link para você abrir no navegador que quiser (ex.: Chrome,
    # onde está logado na conta do canal). O redirect volta para localhost nesta máquina.
    creds = flow.run_local_server(port=0, prompt="consent", open_browser=False,
                                  authorization_prompt_message="Abra este link no navegador para autorizar:\n{url}")
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _read_metadata(out: Path):
    meta_file = out / "metadados.json"
    if not meta_file.exists():
        raise SystemExit(f"Falta {meta_file}. Rode a produção do vídeo antes de publicar.")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    desc = meta.get("descricao", "")
    creditos = out / "creditos.txt"
    if creditos.exists():
        block = creditos.read_text(encoding="utf-8").strip()
        if block:
            desc = (desc + "\n\n" + block).strip()
    return meta, desc


def upload(cfg, out: Path, root: Path, privacy=None, publish_at=None):
    """Sobe out/video.mp4 para o YouTube e define a miniatura. Devolve dict com id/url.

    `privacy` sobrepõe o config; o padrão do canal é 'private'.
    `publish_at` (RFC3339 UTC, ex.: '2026-10-14T21:30:00Z') agenda a publicação: o vídeo
    sobe PRIVADO e o YouTube o torna público sozinho nessa data/hora. Quando usado, a
    visibilidade é forçada para 'private' (exigência da API para agendamento).
    """
    _require_libs()
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    pub = cfg.get("publish", {}) or {}
    video_file = out / "video.mp4"
    if not video_file.exists():
        raise SystemExit(f"Falta {video_file}. Gere o vídeo antes de publicar.")

    privacy = privacy or pub.get("privacy", "private")
    if publish_at:
        # A API só agenda (publishAt) quando o vídeo é enviado como privado.
        if privacy != "private":
            print(f"   ⚠ Agendamento exige privacy=private; ignorando --privacy {privacy}.", flush=True)
        privacy = "private"
    client_secret = root / pub.get("client_secret_file", "client_secret.json")
    token_file = root / pub.get("token_file", ".youtube_token.json")

    meta, desc = _read_metadata(out)
    lang = cfg.get("channel", {}).get("language", "pt-BR")

    creds = _credentials(root, client_secret, token_file)
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    body = {
        "snippet": {
            "title": meta["titulo"][:100],
            "description": desc[:5000],
            "tags": meta.get("tags", [])[:60],
            "categoryId": str(pub.get("category_id", 22)),
            "defaultLanguage": lang,
            "defaultAudioLanguage": lang,
        },
        "status": {
            "privacyStatus": privacy,              # private por padrão
            "selfDeclaredMadeForKids": False,      # canal não é feito para crianças
            "madeForKids": False,
        },
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at   # YouTube publica sozinho nessa data/hora (UTC)

    media = MediaFileUpload(str(video_file), mimetype="video/mp4",
                            chunksize=4 * 1024 * 1024, resumable=True)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    agendado = f", agendado para {publish_at}" if publish_at else ""
    print(f"   Enviando {video_file.name} ({privacy}{agendado})...", flush=True)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"   ... {int(status.progress() * 100)}%", flush=True)
    video_id = resp["id"]
    url = f"https://youtu.be/{video_id}"
    print(f"   Vídeo enviado: {url}", flush=True)

    # Miniatura (opcional; falha aqui não derruba o upload já feito).
    thumb = out / "thumbnail.jpg"
    if thumb.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
            print("   Miniatura definida.", flush=True)
        except Exception as e:
            print(f"   ⚠ Não consegui definir a miniatura (defina manualmente no Studio): {e}", flush=True)

    result = {
        "video_id": video_id,
        "url": url,
        "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "privacy": privacy,
        "publish_at": publish_at,
        "title": meta["titulo"],
    }
    (out / "upload.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result
