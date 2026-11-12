"""Perfis de conteúdo do setor de Clipes (V2).

Um perfil reúne tudo o que é específico de um nicho: público, idioma, termos, critérios de
seleção, duração, quantidade, contexto, preset de edição, hashtags e instruções para os agentes.
O processamento (pipeline.py) é o mesmo para todos; só lê o perfil.

Onde ficam:
  clipes/perfis/<id>.json              perfil atual (editável pelo painel ou à mão)
  clipes/perfis/_historico/<id>.vN.json versões anteriores (nunca apagadas)
  clipes_out/<slug>/perfil.json        cópia congelada usada pelo projeto

A cópia congelada garante que mudar o perfil depois não altera trabalhos antigos. Projeto
criado antes da V2 (sem perfil.json) usa o GTA 6 versão 1, que reproduz as regras fixas de antes.
"""
from __future__ import annotations

import copy
import json
import os
import re
import time
from pathlib import Path

# CLIPES_PERFIS só para testes (pasta temporária); o normal é clipes/perfis/.
PASTA = Path(os.environ.get("CLIPES_PERFIS") or Path(__file__).resolve().parent / "perfis")
HISTORICO = PASTA / "_historico"
LEGADO = ("gta6", 1)  # perfil/versão de projetos anteriores à V2
PADRAO_NOVOS = "geral"  # perfil sugerido para projetos novos (método para qualquer vídeo)

FORMATOS = ("9:16", "16:9", "1:1")
IDIOMAS_FALA = ("auto", "pt", "en", "es")
PRESETS = ("borrado", "zoom", "preencher", "ajustar")
AGENTES = ("kaka", "zidane", "figo", "totti", "lewandowski", "pirlo", "rivaldo")

# Sinais que o código mede de verdade (ver pipeline.momentos). Nada de detecção visual.
SINAIS = {
    "pico_audio": "Pico de volume do áudio (grito, reação, explosão, torcida)",
    "palavras_chave": "Palavras-chave e entidades do perfil ditas no trecho",
    "abertura_forte": "Primeira frase termina em pergunta ou exclamação",
    "densidade_fala": "Fala contínua (palavras por segundo)",
    "assunto_excluido": "Termos de assuntos a excluir (peso negativo)",
}

MODELO = {
    "id": "", "versao": 1, "arquivado": False, "atualizado_em": 0,
    "nome": "", "descricao": "", "publico": "", "idioma": "pt-BR", "idioma_fala": "auto", "objetivo": "",
    "temas": [], "palavras_chave": [], "entidades": [], "termos_tecnicos": [],
    "assuntos_desejados": [], "assuntos_excluir": [],
    "selecao": {
        "pesos": {"pico_audio": 1.0, "palavras_chave": 0.8, "abertura_forte": 0.5,
                  "densidade_fala": 0.6, "assunto_excluido": -1.5},
        "limite_palavras": 4,
        "criterios": [],  # critérios editoriais em texto (o agente Kaká avalia; o código não)
    },
    "duracao": {"min": 20.0, "max": 55.0},
    "quantidade": 5,
    "contexto": {"antes": 0.0, "depois": 0.0},
    "estilo_editorial": "", "formato": "9:16", "preset_edicao": "borrado", "estilo_legenda": "padrao",
    "fontes": {"tema_pesquisa": "", "canais": []},
    "hashtags": [],
    "instrucoes_agentes": {a: "" for a in AGENTES},
}


class PerfilInvalido(ValueError):
    def __init__(self, erros: list[str]):
        super().__init__("; ".join(erros))
        self.erros = erros


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _gravar(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


def gerar_id(nome: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "perfil"


def _lista_txt(v) -> list[str]:
    if isinstance(v, str):  # texto: uma por linha; sem quebra de linha, separado por vírgula
        v = v.splitlines() if "\n" in v else v.split(",")
    if not isinstance(v, list):
        return []
    vistos, out = set(), []
    for x in v:
        x = str(x).strip()
        if x and x.lower() not in vistos and len(x) <= 120:
            vistos.add(x.lower())
            out.append(x)
    return out[:200]


def normalizar(dados: dict) -> dict:
    """Completa campos ausentes com o modelo e converte tipos. Não valida (ver `validar`)."""
    p = copy.deepcopy(MODELO)
    for k, v in (dados or {}).items():
        if k in ("selecao", "duracao", "contexto", "fontes", "instrucoes_agentes") and isinstance(v, dict):
            for k2, v2 in v.items():
                if k == "selecao" and k2 == "pesos" and isinstance(v2, dict):
                    p["selecao"]["pesos"].update(v2)
                else:
                    p[k][k2] = v2
        elif k in p:
            p[k] = v
    for k in ("temas", "palavras_chave", "entidades", "termos_tecnicos", "assuntos_desejados",
              "assuntos_excluir", "hashtags"):
        p[k] = _lista_txt(p[k])
    p["selecao"]["criterios"] = _lista_txt(p["selecao"].get("criterios", []))
    p["fontes"]["canais"] = _lista_txt(p["fontes"].get("canais", []))
    p["hashtags"] = [h if h.startswith("#") else "#" + h.replace(" ", "") for h in p["hashtags"]]
    for k in ("nome", "descricao", "publico", "idioma", "idioma_fala", "objetivo", "estilo_editorial",
              "formato", "preset_edicao", "estilo_legenda"):
        p[k] = str(p.get(k) or "").strip()
    p["arquivado"] = bool(p["arquivado"])
    for a in AGENTES:
        p["instrucoes_agentes"][a] = str(p["instrucoes_agentes"].get(a) or "").strip()[:3000]
    return p


def validar(p: dict) -> list[str]:
    e: list[str] = []
    if not p["nome"] or len(p["nome"]) > 60:
        e.append("Nome é obrigatório (até 60 caracteres).")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", p["id"] or ""):
        e.append("Identificador inválido.")
    try:
        mn, mx = float(p["duracao"]["min"]), float(p["duracao"]["max"])
        p["duracao"] = {"min": mn, "max": mx}
        if not (3 <= mn < mx <= 180):
            e.append("Duração: mínimo de 3 s, máximo de 180 s, e o mínimo menor que o máximo.")
    except (TypeError, ValueError, KeyError):
        e.append("Duração mínima e máxima devem ser números.")
    try:
        p["quantidade"] = int(p["quantidade"])
        if not 1 <= p["quantidade"] <= 20:
            e.append("Quantidade de cortes: de 1 a 20.")
    except (TypeError, ValueError):
        e.append("Quantidade de cortes deve ser um número inteiro.")
    try:
        a, d = float(p["contexto"]["antes"]), float(p["contexto"]["depois"])
        p["contexto"] = {"antes": a, "depois": d}
        if not (0 <= a <= 15 and 0 <= d <= 15):
            e.append("Contexto antes/depois: de 0 a 15 s.")
    except (TypeError, ValueError, KeyError):
        e.append("Contexto antes/depois deve ser número.")
    pesos = p["selecao"]["pesos"]
    for k in list(pesos):
        if k not in SINAIS:
            e.append(f"Sinal de seleção desconhecido: {k}.")
            continue
        try:
            pesos[k] = float(pesos[k])
            if not -5 <= pesos[k] <= 5:
                e.append(f"Peso de {k}: de -5 a 5.")
        except (TypeError, ValueError):
            e.append(f"Peso de {k} deve ser número.")
    try:
        p["selecao"]["limite_palavras"] = int(p["selecao"].get("limite_palavras", 4))
    except (TypeError, ValueError):
        e.append("Limite de palavras-chave deve ser inteiro.")
    if p["formato"] not in FORMATOS:
        e.append(f"Formato deve ser um de {', '.join(FORMATOS)}.")
    if p["idioma_fala"] not in IDIOMAS_FALA:
        e.append(f"Idioma da fala deve ser um de {', '.join(IDIOMAS_FALA)}.")
    if p["preset_edicao"] not in PRESETS:
        e.append(f"Preset de edição deve ser um de {', '.join(PRESETS)}.")
    return e


# ------------------------------------------------------------------ leitura
def _arquivo(pid: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", pid or ""):
        raise KeyError(pid)
    return PASTA / f"{pid}.json"


def listar(incluir_arquivados: bool = False) -> list[dict]:
    out = []
    for f in sorted(PASTA.glob("*.json")):
        try:
            p = normalizar(_ler(f))
        except (OSError, ValueError):
            continue
        if p["arquivado"] and not incluir_arquivados:
            continue
        out.append(p)
    return sorted(out, key=lambda p: (p["arquivado"], p["nome"].lower()))


def carregar(pid: str, versao: int | None = None) -> dict:
    """Perfil atual, ou uma versão específica (do histórico)."""
    atual = _arquivo(pid)
    if versao is not None:
        h = HISTORICO / f"{pid}.v{int(versao)}.json"
        if h.exists():
            return normalizar(_ler(h))
        if atual.exists():
            p = normalizar(_ler(atual))
            if p["versao"] == int(versao):
                return p
        raise KeyError(f"{pid} v{versao}")
    if not atual.exists():
        raise KeyError(pid)
    return normalizar(_ler(atual))


def historico(pid: str) -> list[dict]:
    vs = []
    for f in HISTORICO.glob(f"{pid}.v*.json"):
        p = normalizar(_ler(f))
        vs.append({"versao": p["versao"], "atualizado_em": p["atualizado_em"]})
    return sorted(vs, key=lambda v: v["versao"])


# ------------------------------------------------------------------ escrita
def _conteudo(p: dict) -> dict:
    return {k: v for k, v in p.items() if k not in ("versao", "atualizado_em")}


def salvar(dados: dict, novo: bool = False) -> dict:
    """Cria ou atualiza. Atualizar com conteúdo diferente gera nova versão e guarda a anterior."""
    p = normalizar(dados)
    if novo:
        base = p["id"] or gerar_id(p["nome"])
        pid, n = base, 2
        while (PASTA / f"{pid}.json").exists():
            pid, n = f"{base[:36]}-{n}", n + 1
        p["id"], p["versao"] = pid, 1
    erros = validar(p)
    if erros:
        raise PerfilInvalido(erros)
    arq = _arquivo(p["id"])
    if not novo:
        if not arq.exists():
            raise KeyError(p["id"])
        antigo = normalizar(_ler(arq))
        if _conteudo(antigo) == _conteudo(p):
            return antigo
        _gravar(HISTORICO / f"{p['id']}.v{antigo['versao']}.json", antigo)
        p["versao"] = antigo["versao"] + 1
    p["atualizado_em"] = round(time.time())
    _gravar(arq, p)
    return p


def duplicar(pid: str, nome: str | None = None) -> dict:
    p = carregar(pid)
    p.update(id="", nome=(nome or f"{p['nome']} (cópia)")[:60], arquivado=False)
    return salvar(p, novo=True)


def arquivar(pid: str, arquivado: bool = True) -> dict:
    p = carregar(pid)
    p["arquivado"] = arquivado
    return salvar(p)


# ------------------------------------------------------------------ projeto
def congelar(d: Path, pid: str) -> dict:
    """Grava a cópia do perfil atual no projeto (só se ainda não houver uma)."""
    alvo = Path(d) / "perfil.json"
    if alvo.exists():
        return do_projeto(d)
    p = carregar(pid)
    p["congelado_em"] = round(time.time())
    _gravar(alvo, p)
    return p


def do_projeto(d: Path) -> dict:
    """Perfil que o projeto usa. Sem perfil.json (projeto anterior à V2): GTA 6 v1."""
    alvo = Path(d) / "perfil.json"
    if alvo.exists():
        return normalizar(_ler(alvo))
    return carregar(*LEGADO)


def ajustar_projeto(d: Path, campos: dict) -> dict:
    """Ajuste por projeto: altera só a cópia do projeto, nunca o perfil-base."""
    p = do_projeto(d)
    base = {"id": p["id"], "versao": p["versao"]}
    for k in ("id", "versao", "arquivado", "atualizado_em"):
        campos.pop(k, None)
    novo = normalizar({**p, **campos})
    novo.update(base)
    erros = validar(novo)
    if erros:
        raise PerfilInvalido(erros)
    novo["ajustado_no_projeto"] = True
    novo["congelado_em"] = p.get("congelado_em") or round(time.time())
    _gravar(Path(d) / "perfil.json", novo)
    return novo


def resumo(p: dict) -> dict:
    return {"id": p["id"], "nome": p["nome"], "versao": p["versao"],
            "ajustado": bool(p.get("ajustado_no_projeto")), "formato": p["formato"]}


def termos_selecao(p: dict) -> list[str]:
    """Termos que contam no sinal `palavras_chave` (minúsculos, sem repetição)."""
    vistos, out = set(), []
    for t in p["palavras_chave"] + p["entidades"] + p["termos_tecnicos"]:
        t = t.lower()
        if t not in vistos:
            vistos.add(t)
            out.append(t)
    return out


def vocabulario(p: dict) -> str:
    """Dica de vocabulário para o Whisper (nomes próprios e termos técnicos do nicho)."""
    return ", ".join((p["entidades"] + p["termos_tecnicos"])[:60])
