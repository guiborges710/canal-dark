"""Cronograma de postagem (PROG-011, entrega 1): SÓ SUGERE datas e horários para publicar no Studio.
Só lê (status do PROG-012, fila e config_shorts.yaml); não escreve, não usa rede, não reordena a fila e não agenda nada.
A cadência vem da seção `cronograma` de config_shorts.yaml; sem ela vale 1 vídeo por dia (assunção do Zico, item 11), avisada na saída."""
from datetime import datetime, timedelta
from pathlib import Path

from . import config, status_video

DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]  # índice = datetime.weekday()
HORA_PADRAO = "18:00"
PRAZO_ALERTA_DIAS = 2  # alerta quando faltam menos de 2 dias corridos
MIN_LINHAS = 3
AVISO_DIAS = "Cadência ainda não definida: ver config_shorts.yaml (seção cronograma). Vale 1 vídeo por dia."
PUBLICADOS = ("publicado_privado", "publico")


def ler_cadencia(arquivo=None):
    """Lê a seção `cronograma` do yaml. Devolve {"dias", "hora"} ou None se não existir."""
    arquivo = Path(arquivo) if arquivo else config.REPO / "config_shorts.yaml"
    try:
        import yaml
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8-sig")) or {}
    except (OSError, ImportError, ValueError, Exception):  # noqa: BLE001 - yaml quebrado vale como sem seção
        return None
    sec = dados.get("cronograma") if isinstance(dados, dict) else None
    if not isinstance(sec, dict):
        return None
    return {"dias": sec.get("dias", "todos"), "hora": str(sec.get("hora", HORA_PADRAO))}


def _normalizar(cadencia):
    """(dias[0-6], (h, m), assumida, aviso). Cadência ausente ou inválida cai na assunção, sem inventar exceção."""
    padrao = (list(range(7)), (18, 0))
    if not cadencia:
        return (*padrao, True, AVISO_DIAS)
    dias, hora = cadencia.get("dias", "todos"), cadencia.get("hora", HORA_PADRAO)
    try:
        h, m = (int(x) for x in str(hora).split(":"))
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError
        if dias in ("todos", "diario", "diária", None):
            idx = list(range(7))
        else:
            idx = sorted({DIAS.index(str(d).strip().lower()[:3].replace("á", "a")) for d in dias})
            if not idx:
                raise ValueError
    except (ValueError, TypeError):
        return (*padrao, True, "Cadência inválida em config_shorts.yaml; vale 1 vídeo por dia às 18:00 até corrigir.")
    return idx, (h, m), False, ""


def _slots(agora, dias, hora, n):
    """Próximos n horários a partir de `agora` (estritamente depois dele), nos dias da cadência."""
    out, d = [], agora.date()
    while len(out) < n:
        if d.weekday() in dias:
            t = datetime(d.year, d.month, d.day, hora[0], hora[1])
            if t > agora:
                out.append(t)
        d += timedelta(days=1)
    return out


def calcular(agora=None, cadencia=None, saida=None, usar_config=False):
    """`agora` e `cadencia` entram por parâmetro (teste). usar_config=True lê o yaml real (rota)."""
    agora = agora or datetime.now()
    if usar_config:
        cadencia = ler_cadencia()
    dias, hora, assumida, aviso = _normalizar(cadencia)
    estado = status_video.todos(saida)
    fila = status_video.ler_fila(saida)
    por_slug = {v["slug"]: v for v in estado["videos"]}

    itens = []  # a fila sem o que já foi publicado, na ordem do arquivo
    for s in fila:
        v = por_slug.get(s)
        if v is not None and v["status"] in PUBLICADOS:
            continue
        itens.append((s, v))

    slots = _slots(agora, dias, hora, max(len(itens), MIN_LINHAS))
    linhas = []
    for i, t in enumerate(slots):
        faltam = (t.date() - agora.date()).days
        base = {"data": t.date().isoformat(), "data_br": t.strftime("%d/%m"), "hora": t.strftime("%H:%M"), "dias_ate": faltam}
        urgente = faltam < PRAZO_ALERTA_DIAS
        if i < len(itens):
            s, v = itens[i]
            if v is None:
                linhas.append({**base, "slug": s, "titulo": "sem título", "status": "sem_pasta", "status_texto": "Pasta não encontrada",
                               "falta": ["pasta do vídeo em output/"], "avisos": [], "alerta": urgente})
            else:
                linhas.append({**base, "slug": s, "titulo": v["titulo"] or "sem título", "status": v["status"], "status_texto": v["status_texto"],
                               "falta": v["falta"], "avisos": v["avisos"], "alerta": urgente and v["status"] != "na_fila"})
        else:
            linhas.append({**base, "slug": None, "titulo": f"Sem vídeo na fila para {base['data_br']}", "status": "vazio",
                           "status_texto": "Sem vídeo", "falta": ["vídeo na fila de postagem"], "avisos": [], "alerta": urgente})

    p = linhas[0]
    if not itens:
        proxima = {"pronto": False, "texto": f"Nenhum vídeo na fila para {p['data_br']}", "envio": ""}
    elif p["status"] == "na_fila":
        proxima = {"pronto": True, "texto": "Pronto para postar", "envio": ""}
    else:
        falta = ", ".join(p["falta"]) or (p["avisos"][0] if p["avisos"] else p["status_texto"].lower())
        proxima = {"pronto": False, "texto": f"Sem vídeo pronto para {p['data_br']}, falta: {falta}", "envio": ""}
    pp = estado["proximo_pronto"]
    if itens and p["status"] != "na_fila" and pp["sim"] and pp["slug"]:
        proxima["envio"] = f"O envio vai pular {p['slug']} e subir {pp['slug']}."
    proxima["alerta"] = bool(linhas[0]["alerta"])
    return {"agora": agora.isoformat(timespec="minutes"), "linhas": linhas, "proxima": proxima,
            "cadencia": {"dias": [DIAS[d] for d in dias], "hora": f"{hora[0]:02d}:{hora[1]:02d}", "assumida": assumida, "aviso": aviso},
            "nota": "Só sugestão para publicar no Studio. A ordem é a de output/fila_postagem.txt (edite o arquivo à mão)."}
