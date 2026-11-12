"""Lê (só leitura) a planilha oficial "Meu Financeiro — Base de Dados" e guarda uma cópia local.

Cada aba vira financas/planilha/<aba>.csv (valores como aparecem na planilha). Nada é
escrito na planilha. O Casemiro usa essas cópias para conferir com o movimentos.csv.

Uso: python financas/planilha_ler.py
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "produtividade"))

from googleapiclient.discovery import build  # noqa: E402

import google_pessoal  # noqa: E402

PLANILHA_ID = "1wQx28VhiIAbKN1eUxLzCybG0bIKOyBVvnMsu4TZ3uAE"
SAIDA = Path(__file__).resolve().parent / "planilha"


def main():
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    api = build("sheets", "v4", credentials=google_pessoal.credenciais(), cache_discovery=False).spreadsheets()
    meta = api.get(spreadsheetId=PLANILHA_ID, fields="properties.title,sheets.properties.title").execute()
    SAIDA.mkdir(exist_ok=True)
    print("Planilha:", meta["properties"]["title"])
    for aba in meta["sheets"]:
        nome = aba["properties"]["title"]
        valores = api.values().get(spreadsheetId=PLANILHA_ID, range=f"'{nome}'",
                                   valueRenderOption="FORMATTED_VALUE").execute().get("values", [])
        arq = SAIDA / (re.sub(r"[^\w\-]+", "_", nome).strip("_").lower() + ".csv")
        with arq.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(valores)
        print(f"  {nome}: {len(valores)} linhas -> {arq.name}")


if __name__ == "__main__":
    main()
