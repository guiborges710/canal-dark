"""Conexão com a conta Google pessoal do Guilherme (Agenda e Planilhas).

Usa o mesmo client OAuth do projeto (client_secret.json), mas um token próprio,
.google_pessoal_token.json (nunca versionar), separado do token do YouTube.

Escopos (o mínimo necessário):
  calendar.events        criar/ler/alterar eventos da Agenda (não mexe em outras configurações)
  spreadsheets.readonly  só LER planilhas (nada é escrito na planilha)

Uso:
  python produtividade/google_pessoal.py     abre o navegador uma vez para o Guilherme autorizar
"""
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

RAIZ = Path(__file__).resolve().parent.parent
TOKEN = RAIZ / ".google_pessoal_token.json"
SEGREDO = RAIZ / "client_secret_pessoal.json"  # projeto Google próprio da conta pessoal (não é o do YouTube)
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def credenciais(interativo=False):
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except Exception as e:  # noqa: BLE001  (token revogado ou expirado)
            if not interativo:
                sys.exit(f"Token do Google expirou ou foi revogado ({e}). Rode: python produtividade/google_pessoal.py")
    if not interativo:
        sys.exit("Google ainda não conectado. Rode: python produtividade/google_pessoal.py")
    fluxo = InstalledAppFlow.from_client_secrets_file(str(SEGREDO), SCOPES)
    creds = fluxo.run_local_server(port=0, prompt="consent", open_browser=True)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


if __name__ == "__main__":
    from googleapiclient.discovery import build
    c = credenciais(interativo=True)
    ag = build("calendar", "v3", credentials=c, cache_discovery=False)
    proximos = ag.events().list(calendarId="primary", maxResults=1, singleEvents=True, orderBy="startTime",
                                timeMin="2000-01-01T00:00:00Z").execute()
    print("Agenda conectada (fuso:", proximos.get("timeZone"), ")")
    print("Token salvo em", TOKEN.name)
