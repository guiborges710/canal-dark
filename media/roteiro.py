"""Mede o que o roteiro tem de número e de gráfico. Regra em prompts/tipos_de_roteiro.md: no máximo 2 números por Short e 1 gráfico.

Só avisa: quem decide é o agente que revisa e o Guilherme. A contagem é por texto, então pode errar por um ou dois.
"""
import re

MAX_NUMEROS = 2
MAX_GRAFICOS = 1
# "um" e "uma" ficam de fora: quase sempre são artigo. Palavras seguidas, ligadas por "e" ou "vírgula", contam como um número só.
_PALAVRAS = (r"dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|quatorze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|"
             r"vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cem|cento|duzent[oa]s|trezent[oa]s|quatrocent[oa]s|quinhent[oa]s|"
             r"seiscent[oa]s|setecent[oa]s|oitocent[oa]s|novecent[oa]s|mil|milh[aã]o|milh[oõ]es|bilh[aã]o|bilh[oõ]es")
_POR_EXTENSO = rf"(?:{_PALAVRAS})(?:(?:\s+e\s+|\s+v[ií]rgula\s+|\s+)(?:{_PALAVRAS}|um|uma))*(?:\s+por\s+cento)?"
_ALGARISMO = r"(?:R\$\s*)?\d[\d.,]*\s*(?:%|por\s+cento|mil\b|milh[oõ]es\b|milh[aã]o\b|bilh[oõ]es\b)?"
_UM_EM_CADA = rf"(?:\d+|um|uma|{_PALAVRAS})\s+(?:em\s+cada|de\s+cada)\s+(?:\d+|{_PALAVRAS})"  # "1 em cada 3" é um número só, e o jeito certo de dizer
_NUMERO = re.compile(rf"(?<!\w)(?:{_UM_EM_CADA}|{_ALGARISMO}|{_POR_EXTENSO})(?!\w)", re.I)
_TIPOS_GRAFICO = {"barras", "barras_horizontais"}


def numeros(texto):
    """Os números citados no texto, em algarismos ou por extenso."""
    return [m.group(0).strip().rstrip(".,") for m in _NUMERO.finditer(texto or "")]


def cenas_com_grafico(cenas, sketch_py=""):
    """Quantas cenas mostram gráfico, em qualquer estilo. No Scratch, olha a função de desenho da cena."""
    funcoes = dict(re.findall(r"^def (cena_\w+)\(.*?\n((?:[ \t]+.*\n?|\s*\n)*)", sketch_py or "", re.M))
    total = 0
    for c in cenas or ():
        if c.get("tipo") in _TIPOS_GRAFICO:
            total += 1
        elif any(o.get("tipo") == "grafico" for o in c.get("objetos") or ()) or any(r.get("tipo") == "grafico" for r in c.get("recortes") or ()):
            total += 1
        elif c.get("desenho") in funcoes and re.search(r"\bbarras?\(", funcoes[c["desenho"]]):
            total += 1
    return total
