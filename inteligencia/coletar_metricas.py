"""Coleta as métricas dos vídeos do canal (setor de inteligência, Yuri Alberto).

Lê a própria conta com o mesmo token OAuth do upload (escopo youtube.force-ssl) e acrescenta
uma linha por vídeo em inteligencia/metricas/videos.csv. Só lê: não publica, não altera vídeo
nem miniatura. Retenção, CTR, tráfego e inscritos vêm da YouTube Analytics API, com um token
SEPARADO (.youtube_analytics_token.json, escopo yt-analytics.readonly). Sem esse token, o
coletor grava só o público e avisa o que faltou.

Uso:
  .venv/Scripts/python.exe inteligencia/coletar_metricas.py                        coleta diária
  .venv/Scripts/python.exe inteligencia/coletar_metricas.py --autorizar-analytics  consentimento (1 vez)
"""
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from media.youtube import _credentials, _require_libs  # noqa: E402

METRICAS = ROOT / "inteligencia" / "metricas"
CSV_FILE = METRICAS / "videos.csv"
CAMPOS = ["slug", "video_id", "titulo", "publicado_em", "duracao_s",
          "views", "likes", "comentarios", "coletado_em", "privacidade"]

# Analytics: token separado do upload (que expira a cada 7 dias).
ANALYTICS_SCOPE = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
ANALYTICS_TOKEN = ROOT / ".youtube_analytics_token.json"
CLIENT_SECRET = ROOT / "client_secret.json"
ANALYTICS_CSV = METRICAS / "analytics_videos.csv"
TRAFEGO_CSV = METRICAS / "analytics_trafego.csv"
ANALYTICS_CAMPOS = ["coletado_em", "janela_inicio", "janela_fim", "video_id", "slug", "views",
                    "minutos_assistidos", "duracao_media_s", "retencao_media_pct",
                    "inscritos_ganhos", "impressoes", "ctr_impressoes_pct"]
TRAFEGO_CAMPOS = ["coletado_em", "janela_inicio", "janela_fim", "video_id", "slug",
                  "fonte_trafego", "views", "minutos_assistidos"]


def _slugs_por_video():
    """Liga cada video_id ao slug da pasta output/<slug>/ (só leitura de upload.json)."""
    mapa = {}
    for up in (ROOT / "output").glob("*/upload.json"):
        try:
            video_id = json.loads(up.read_text(encoding="utf-8")).get("video_id")
        except ValueError:
            continue
        if video_id:
            mapa[video_id] = up.parent.name
    manual = METRICAS / "slugs_manuais.csv"  # vídeos sem upload.json; mapeamento conferido à mão
    if manual.exists():
        with manual.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                mapa.setdefault(r["video_id"], r["slug"])
    return mapa


def _duracao_s(iso):
    """Converte a duração ISO 8601 do YouTube (ex.: PT1M2S) em segundos."""
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(g or 0) for g in m.groups())
    return h * 3600 + mi * 60 + s


def _ids_do_canal(youtube):
    canal = youtube.channels().list(part="contentDetails,snippet", mine=True).execute().get("items", [])
    if not canal:
        raise SystemExit("Nenhum canal encontrado para esta conta OAuth.")
    uploads = canal[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = []
    req = youtube.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50)
    while req is not None:
        resp = req.execute()
        ids += [item["contentDetails"]["videoId"] for item in resp.get("items", [])]
        req = youtube.playlistItems().list_next(req, resp)
    return canal[0]["snippet"]["title"], ids


def _detalhes(youtube, ids):
    itens = []
    for i in range(0, len(ids), 50):
        resp = youtube.videos().list(part="snippet,contentDetails,statistics,status",
                                     id=",".join(ids[i:i + 50])).execute()
        itens += resp.get("items", [])
    return itens


def _migrar_csv(slugs):
    """Garante o cabeçalho novo (coluna privacidade) sem perder linhas; preenche slug vazio."""
    if not CSV_FILE.exists():
        return
    with CSV_FILE.open(encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        cab = leitor.fieldnames
        linhas = list(leitor)
    mudou = False
    for r in linhas:
        if not r.get("slug") and slugs.get(r["video_id"]):
            r["slug"] = slugs[r["video_id"]]
            mudou = True
    if cab != CAMPOS or mudou:
        with CSV_FILE.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS, restval="")
            w.writeheader()
            w.writerows(linhas)


def _anexar(arquivo, campos, linhas):
    novo = not arquivo.exists()
    with arquivo.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, restval="")
        if novo:
            w.writeheader()
        w.writerows(linhas)


def _credenciais_analytics(interativo=False):
    """Token separado do upload. Sem token e sem interativo: devolve None (não abre nada)."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    if ANALYTICS_TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(ANALYTICS_TOKEN), ANALYTICS_SCOPE)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                ANALYTICS_TOKEN.write_text(creds.to_json(), encoding="utf-8")
                return creds
            except Exception as e:  # token revogado ou expirado
                print(f"AVISO: token do Analytics não renovou ({type(e).__name__}).", flush=True)
    if not interativo:
        return None
    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Falta {CLIENT_SECRET.name} na raiz do projeto.")
    import google_auth_oauthlib.flow
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET), ANALYTICS_SCOPE)
    creds = flow.run_local_server(
        port=0, prompt="consent", open_browser=False,
        authorization_prompt_message="Abra este link no navegador (conta do canal) para autorizar o Analytics:\n{url}")
    ANALYTICS_TOKEN.write_text(creds.to_json(), encoding="utf-8")
    print("Token do Analytics salvo (arquivo separado do upload).", flush=True)
    return creds


def _consulta(an, inicio, fim, metricas, dims="video", extra=None):
    """Uma consulta ao Analytics; devolve as linhas ou levanta a exceção da API."""
    args = dict(ids="channel==MINE", startDate=inicio, endDate=fim,
                metrics=",".join(metricas), dimensions=dims, maxResults=200)
    args.update(extra or {})
    return an.reports().query(**args).execute().get("rows", [])


def _ctr_manual():
    """Último registro por video_id de ctr_manual.csv (preenchido à mão a partir do Studio)."""
    arq = METRICAS / "ctr_manual.csv"
    res = {}
    if arq.exists():
        with arq.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(l for l in f if not l.lstrip().startswith("#")):
                if r.get("video_id") and (r.get("impressoes") or r.get("ctr_pct")):
                    res[r["video_id"].strip()] = r  # linhas mais novas sobrescrevem (ordem do arquivo)
    return res


def _coletar_analytics(videos, slugs, coletado_em):
    """Retenção, inscritos, impressões/CTR e tráfego. Tudo opcional: o que falhar é avisado."""
    creds = _credenciais_analytics()
    if creds is None:
        print("AVISO: sem token do Analytics (.youtube_analytics_token.json). Não coletei retenção, "
              "CTR, tráfego nem inscritos. Para liberar: rode com --autorizar-analytics.", flush=True)
        return
    from googleapiclient.discovery import build
    an = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    inicio = min((v["snippet"]["publishedAt"][:10] for v in videos), default="2026-01-01")
    fim = datetime.now().strftime("%Y-%m-%d")
    base = ["views", "estimatedMinutesWatched", "averageViewDuration",
            "averageViewPercentage", "subscribersGained"]
    por_video = {}
    try:
        for r in _consulta(an, inicio, fim, base, extra={"sort": "-views"}):
            por_video[r[0]] = dict(zip(base, r[1:]))
    except Exception as e:
        print(f"AVISO: consulta principal do Analytics falhou: {type(e).__name__}: {e}", flush=True)
        return
    # Impressões e CTR: a API não aceita para este canal; vêm de ctr_manual.csv (Studio).
    imp = _ctr_manual()
    linhas = []
    for vid, m in por_video.items():
        i = imp.get(vid)
        linhas.append({"coletado_em": coletado_em, "janela_inicio": inicio, "janela_fim": fim,
                       "video_id": vid, "slug": slugs.get(vid, ""), "views": m["views"],
                       "minutos_assistidos": m["estimatedMinutesWatched"],
                       "duracao_media_s": m["averageViewDuration"],
                       "retencao_media_pct": m["averageViewPercentage"],
                       "inscritos_ganhos": m["subscribersGained"],
                       "impressoes": i["impressoes"] if i else "", "ctr_impressoes_pct": i["ctr_pct"] if i else ""})
    _anexar(ANALYTICS_CSV, ANALYTICS_CAMPOS, linhas)
    trafego, falhas = [], 0
    # insightTrafficSourceType só é aceito sozinho (canal) ou com filters=video==ID; uma chamada por vídeo.
    # Vídeo sem views na janela é pulado.
    for vid, m in por_video.items():
        if not m["views"]:
            continue
        try:
            for r in _consulta(an, inicio, fim, ["views", "estimatedMinutesWatched"],
                               dims="insightTrafficSourceType",
                               extra={"filters": f"video=={vid}", "sort": "-views"}):
                trafego.append({"coletado_em": coletado_em, "janela_inicio": inicio, "janela_fim": fim,
                                "video_id": vid, "slug": slugs.get(vid, ""), "fonte_trafego": r[0],
                                "views": r[1], "minutos_assistidos": r[2]})
        except Exception as e:
            falhas += 1
            if falhas == 1:
                print(f"AVISO: tráfego por fonte falhou em {vid}: {type(e).__name__}: {e}", flush=True)
    if trafego:
        _anexar(TRAFEGO_CSV, TRAFEGO_CAMPOS, trafego)
    print(f"Analytics: {len(linhas)} vídeo(s) em {ANALYTICS_CSV.name}, {len(trafego)} linha(s) de "
          f"tráfego ({falhas} falha(s)); CTR manual em {len(imp)} vídeo(s).", flush=True)


def main():
    sys.stdout.reconfigure(line_buffering=True)
    _require_libs()
    from googleapiclient.discovery import build

    if "--autorizar-analytics" in sys.argv:
        _credenciais_analytics(interativo=True)
        return

    creds = _credentials(ROOT, CLIENT_SECRET, ROOT / ".youtube_token.json")
    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    nome_canal, ids = _ids_do_canal(youtube)
    videos = _detalhes(youtube, ids)
    slugs = _slugs_por_video()
    coletado_em = datetime.now().strftime("%Y-%m-%dT%H:%M")

    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    _migrar_csv(slugs)
    novo = not CSV_FILE.exists()
    with CSV_FILE.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo:
            w.writeheader()
        for v in videos:
            est = v.get("statistics", {})
            w.writerow({
                "slug": slugs.get(v["id"], ""),
                "video_id": v["id"],
                "titulo": v["snippet"]["title"],
                "publicado_em": v["snippet"]["publishedAt"][:10],
                "duracao_s": _duracao_s(v["contentDetails"]["duration"]),
                "views": est.get("viewCount", 0),
                "likes": est.get("likeCount", 0),
                "comentarios": est.get("commentCount", 0),
                "coletado_em": coletado_em,
                "privacidade": v.get("status", {}).get("privacyStatus", ""),
            })

    print(f"Canal: {nome_canal}. {len(videos)} vídeo(s) gravado(s) em {CSV_FILE.relative_to(ROOT)} "
          f"(coleta {coletado_em}).", flush=True)
    _coletar_analytics(videos, slugs, coletado_em)


if __name__ == "__main__":
    main()
