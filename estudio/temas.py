"""Temas prontos para virar vídeo: o que o Modric e o Haaland já separaram em output/ e ainda não tem vídeo.

Não existe uma segunda lista: os temas continuam nos arquivos que os agentes já escrevem (modric_10_temas.md, modric_tema_*.md e
ideias.json). Gerar um tema aciona o Modric de verdade, e ele grava mais um modric_tema_<assunto>.md.
"""
import re
import unicodedata

from . import fluxo, materiais as M
from .banco import agora, evento, um, varios
from .config import SAIDA
from .fluxo import Recusado

SLUG_TEMAS = "__temas__"
PALAVRAS_FORA = set("a o e as os de da do das dos em no na nos nas um uma uns umas por para pra com sem que se ao aos sua seu suas seus mais menos como quem qual sao nao ou entre sobre the of and "
                    "porque contra vs ja tem ter foi ser esta este essa esse isso".split())
PROMPT_GERAR = """Você foi acionado pelo Corte: o Guilherme quer UM tema novo para um Short. Não pergunte nada: ele não está nesta conversa.
Nicho do canal: Análise de Comportamento Social e Gerações. Leia output/messi_assinatura_canal.md (identidade editorial).

Proponha exatamente UM tema, com fatos atuais e 3+ fontes abertas, que funcione como Short de 30 a 60 s para brasileiros de 18 a 45 anos.
O tema nasce de uma situação que a pessoa reconhece, não de uma estatística: veja prompts/tipos_de_roteiro.md.
Não repita nem chegue perto destes, que já existem:
{existentes}

Grave o resultado em output/modric_tema_{{assunto}}.md, trocando {{assunto}} por 2 a 5 palavras em minúsculas, sem acento, separadas por hífen. Use exatamente este formato:

# Tema: <título curto do vídeo, até 70 caracteres>

**Descrição:** <o que o vídeo explica, em 1 ou 2 frases>

**Por que agora:** <por que é relevante hoje>

**Fontes:**
- <fonte com link e o número que ela traz>

**Direção de ângulo:** <direção inicial, não definitiva>

Grave só esse arquivo. Não crie pasta de produção nem escreva notas.md."""


def _fichas(texto):
    def campo(*nomes):
        for n in nomes:
            m = re.search(rf"\*\*{n}[^*]*:\*\*\s*(.+?)(?=\n\s*\n|\n\*\*|\Z)", texto, re.S)
            if m:
                return " ".join(m.group(1).split())
            m = re.search(rf"^#+\s*(?:\d+\.\s*)?{n}[^\n]*\n+(.+?)(?=\n\s*\n|\n#|\Z)", texto, re.S | re.M)
            if m:
                return " ".join(m.group(1).split())
        return ""
    return {"descricao": campo("Descrição", "Descricao"), "por_que": campo("Por que agora", "Por que é relevante"), "angulo": campo("Direção de ângulo", "Direcao de angulo", "Ângulo")}


def _do_modric():
    saida = []
    lista = SAIDA / "modric_10_temas.md"
    if lista.is_file():
        texto = M.ler_texto(lista)
        partes = re.split(r"^##\s+(\d+)\.\s+(.+)$", texto, flags=re.M)
        for n, titulo, corpo in zip(partes[1::3], partes[2::3], partes[3::3]):
            saida.append({"titulo": titulo.strip(), "origem": "Modric", "arquivo": f"{lista.name}, tema {n}", **_fichas(corpo)})
    for f in sorted(SAIDA.glob("modric_tema_*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        texto = M.ler_texto(f)
        m = re.search(r"^#\s*Tema:\s*(.+)$", texto, re.M)
        if m:
            saida.append({"titulo": m.group(1).strip(), "origem": "Modric", "arquivo": f.name, **_fichas(texto)})
    return saida


def _do_haaland():
    d = M.ler_json(SAIDA / "ideias.json", None)
    if not isinstance(d, dict):
        return []
    saida = []
    for x in d.get("ideias") or []:
        titulo = str(x.get("titulo") or "").strip() if isinstance(x, dict) else ""
        if titulo and "simulad" not in titulo.lower():  # `run.py ideas --mock` grava exemplos: não são temas de verdade
            saida.append({"titulo": titulo, "origem": "Haaland", "arquivo": "ideias.json", "descricao": str(x.get("por_que_funciona") or ""), "por_que": "", "angulo": str(x.get("angulo") or "")})
    return saida


def _radicais(texto):
    """Palavras que identificam o assunto, sem acento e sem as miúdas. Quatro letras bastam para "adia" achar "adiaram"."""
    limpo = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode().lower()
    return {p[:4] for p in re.split(r"[^a-z0-9]+", limpo) if len(p) > 1 and p not in PALAVRAS_FORA}


def _parecidos(a, b):
    comuns = a & b
    return len(comuns) >= 2 and len(comuns) / max(1, min(len(a), len(b))) >= 0.5


def _mesmo_assunto(titulo, contexto, projeto):
    """O nome da pasta é curto e o tema é descrito com mais palavras. Palavra sozinha (nem-nem-2025) só vale se estiver no título;
    na descrição, precisa de pelo menos três e da maior parte da pasta, para um "bebê" solto não esconder um tema que ainda não foi feito."""
    nomes = {p for p in projeto if not p.isdigit()}
    if len(nomes) == 1:
        return nomes <= titulo
    comuns = contexto & nomes
    return len(comuns) >= 3 and len(comuns) / len(nomes) >= 0.75


def _projetos():
    temas = {r["slug"]: r["tema"] for r in varios("SELECT slug, tema FROM producoes")}
    saida = []
    for p in SAIDA.iterdir() if SAIDA.is_dir() else ():
        if M.e_producao(p) or p.name in temas:
            saida.append({"slug": p.name, "radicais": _radicais(p.name) | _radicais(temas.get(p.name)), "video": (p / "video.mp4").exists()})
    return saida


def gerando():
    return um("SELECT id, status FROM jobs WHERE slug=? AND status IN ('fila','rodando') ORDER BY id DESC LIMIT 1", SLUG_TEMAS)


def listar():
    """Só o que não tem vídeo pronto. Tema com projeto começado aparece com o link dele, para não abrir outro igual."""
    projetos = _projetos()
    vistos, temas, com_video = [], [], 0
    for t in _do_modric() + _do_haaland():
        r = _radicais(t["titulo"])
        if any(_parecidos(r, v) for v in vistos):
            continue
        vistos.append(r)
        contexto = r | _radicais(t.get("descricao")) | _radicais(t.get("angulo"))
        ligados = sorted((p for p in projetos if _parecidos(r, p["radicais"]) or _mesmo_assunto(r, contexto, p["radicais"])), key=lambda p: not p["video"])
        if any(p["video"] for p in ligados):
            com_video += 1
            continue
        temas.append({"id": M.sha_texto(t["titulo"])[:12], **t, "projeto": ligados[0]["slug"] if ligados else None})
    ultimo = um("SELECT status, erro, terminado_em FROM jobs WHERE slug=? ORDER BY id DESC LIMIT 1", SLUG_TEMAS) or {}
    return {"temas": temas, "com_video": com_video, "gerando": bool(gerando()), "erro_geracao": ultimo.get("erro") if ultimo.get("status") == "falhou" else None}


def gerar():
    """Aciona o Modric para um tema. Clique duplo cai no mesmo trabalho."""
    from . import agentes, trabalhos
    integ = trabalhos.integracoes()["claude"]
    if not integ["ok"]:
        raise Recusado(integ["detalhe"])
    existentes = "\n".join(f"- {t['titulo']}" for t in _do_modric() + _do_haaland()) or "- (nenhum ainda)"
    feitos = "\n".join(f"- {p['slug']}" for p in _projetos())
    agente = agentes.foto("modric-pesquisador-tema")
    spec = {"tipo": "agente", "agente": agente["id"], "prompt": PROMPT_GERAR.format(existentes=existentes + "\n" + feitos), "raia": "agente", "craque": "Modric", "origem": "gerar_tema", "materiais": [], "titulo": "Modric: gerando um tema"}
    job, novo = fluxo.inserir_job(SLUG_TEMAS, "gerar_tema", spec, assinatura=f"tema:{agora()}")
    if novo:
        evento(SLUG_TEMAS, "Modric acionado para gerar um tema")
    return {"job": job["id"], "novo": novo}


def briefing_de(t):
    """O que já se sabe do tema vai junto: o Modric não recomeça do zero e o Neymar recebe a direção."""
    partes = [f"Tema separado em output/{t['arquivo']}: use o que já foi levantado ali como ponto de partida e confira as fontes."] if t.get("arquivo") else []
    if t.get("angulo"):
        partes.append(f"Direção inicial: {t['angulo']}")
    return "\n".join(partes)

