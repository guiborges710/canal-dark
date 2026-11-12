"""Seleção editorial dos cortes (V3): unidades de pensamento, integridade de início e fim, critérios e redundância.

Substitui a janela cega "segmentos contíguos + pontuação de sinais" nos projetos com perfil (geral, gta6 e
os criados no painel). Projeto sem perfil.json (anterior à V2) continua na seleção V1 (regressão).

O que o código decide, tudo a partir da transcrição com carimbos de palavra:
  1. Unidades de pensamento: segmentos do Whisper colados/separados por pontuação e pausa (não por tempo).
  2. Início íntegro: não começa em "isso/ele/essa situação..." nem em conector solto; recupera a premissa
     (a unidade anterior, em geral a pergunta) até um limite. Sem premissa possível, o candidato é descartado.
  3. Fim íntegro: termina em frase fechada, não em pergunta sem resposta, não em palavra de ligação e não
     se a fala seguinte continua a mesma ideia (conector colado, sem pausa). Se precisar, estende o fim.
  4. Critérios por candidato (0 a 1; pausas antes/depois pesam em início e conclusão): abertura, clareza, interesse, progressão, conclusão, independência.
     São heurísticas de comparação, não previsão de alcance. Integridade vem ANTES da nota.
  5. Redundância: candidatos com o mesmo conteúdo não entram juntos. Sem preencher cota com corte fraco.
  6. Limites em tempo de PALAVRA (com folga curta), nunca no meio de uma palavra.

Nada aqui depende de tema: os termos do perfil só entram como sinal de interesse (o Geral não tem nenhum).
"""
from __future__ import annotations

import math
import re

import numpy as np

VERSAO = 4
PAUSA_UNIDADE = 0.6      # pausa que separa unidades de pensamento
PAUSA_MIN_FRONTEIRA = 0.5  # sem pausa dessa duração, a fala corrida não é fronteira de corte
PAUSA_FECHA = 0.6        # pausa depois do fim que confirma que a ideia acabou
PREMISSA_MAX_S = 20.0    # quanto contexto anterior dá para recuperar
PREMISSA_MAX_UNID = 3
FOLGA_INI, FOLGA_FIM = 0.12, 0.25
NOTA_MINIMA = 0.45
SIMILARIDADE_MAX = 0.5
PALAVRAS_MIN = 15
PARTES_MAX = 4            # máximo de partes de um assunto que não coube em um vertical
SERIE_BONUS = 0.05        # assunto completo em partes vale um pouco mais que um pedaço dele
PAUSA_TOPICO = 2.0        # pausa que, com frase íntegra, já fecha um assunto
COESAO_BAIXA = 0.12       # vocabulário raro que deixa de se repetir = mudança de assunto
LIGA_PAUSA_MAX = 2.0     # até essa pausa, palavra rara repetida liga duas falas na mesma ideia

PESOS = {"abertura": 0.20, "clareza": 0.15, "interesse": 0.20, "progressao": 0.15,
         "conclusao": 0.20, "independencia": 0.10}

# --- Pacotes de idioma -------------------------------------------------------------------------
# Só o que é linguístico fica aqui (pronomes de referência, conectores, palavras que não fecham frase, marcadores
# de fala, abertura forte, metadiscurso). O idioma vem da transcrição (Whisper). Idioma sem pacote usa só os
# sinais neutros (pontuação, maiúscula, pausa, pergunta/resposta), que valem para qualquer língua de alfabeto latino.
PACOTES = {
    "pt": {
        "forte": ["isso", "isto", "ele", "ela", "eles", "elas", "esse", "essa", "esses", "essas", "este", "esta", "aquilo",
                  "aquele", "aquela", "nisso", "disso", "nesse", "nessa", "desse", "dessa", "dele", "dela", "deles",
                  "delas", "por isso", "por esse", "por essa"],
        "conector": ["e", "mas", "então", "aí", "daí", "porque", "pois", "ou", "também", "só que", "tipo", "que", "né"],
        "pronomes": ["isso", "isto", "ele", "ela", "eles", "elas", "esse", "essa", "esses", "essas", "aquilo", "aquele",
                     "aquela", "nisso", "disso", "dele", "dela"],
        "abertos": ["e", "mas", "que", "de", "do", "da", "dos", "das", "a", "o", "os", "as", "um", "uma", "para", "pra",
                    "com", "porque", "pois", "ou", "se", "em", "no", "na", "por", "então", "aí", "tipo", "como", "quando",
                    "onde", "pelo", "pela", "ao", "à", "num", "numa", "sem", "até"],
        "tag": ["né", "certo", "tá", "ta", "entendeu", "sabe", "viu", "hein", "não", "ok", "beleza", "tipo", "cara", "mano"],
        "abertura": ["nunca", "ninguém", "sério", "absurdo", "chocante", "descobri", "descobriu", "revelou", "verdade",
                     "mentira", "segredo", "erro", "problema", "incrível", "inacreditável", "impossível", "pior",
                     "melhor", "culpa", "surpreendente"],
        "virada": ["mas", "porém", "só que", "na verdade", "até que", "de repente", "no fim", "afinal", "então"],
        "contraste": r"\b(mas|só que|porém|não)\b", "pessoal": r"^\W*(eu |a gente |nós |olha|cara|sabe)",
        "meta": r"deixa eu|um segundo|já volto|esqueci|deixa pra lá|o que eu (ia|estava) falar|vamos lá|rapidinho|voltei|"
                r"pronto,|obrigad[oa]|valeu|deixa o like|live ?pix|mandou \d+|inscreva|gente.*gente",
    },
    "fr": {
        "forte": ["ça", "cela", "ceci", "il", "elle", "ils", "elles", "ce", "cet", "cette", "ces", "celui", "celle", "ceux",
                  "pour ça", "à cause de ça"],
        "conector": ["et", "mais", "donc", "du coup", "alors", "parce que", "car", "puisque", "ou", "aussi", "enfin",
                     "bon", "ben", "bah", "voilà", "ouais", "oui", "non"],
        "pronomes": ["ça", "cela", "il", "elle", "ils", "elles", "celui", "celle", "ceux", "ceci"],
        "abertos": ["et", "mais", "que", "qui", "de", "du", "des", "la", "le", "les", "un", "une", "pour", "avec", "parce",
                    "car", "ou", "si", "en", "dans", "sur", "par", "donc", "alors", "comme", "quand", "où", "au", "aux",
                    "à", "sans", "jusqu", "ce", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses"],
        "tag": ["hein", "non", "d'accord", "ok", "bon", "voilà", "quoi", "ouais", "oui", "vu", "tu vois", "n'est-ce pas"],
        "abertura": ["jamais", "personne", "sérieux", "incroyable", "vérité", "mensonge", "secret", "erreur", "problème",
                     "pire", "meilleur", "honte", "choquant", "impossible", "inimaginable"],
        "virada": ["mais", "pourtant", "sauf que", "en fait", "tout à coup", "finalement", "du coup"],
        "contraste": r"\b(mais|sauf que|pourtant|pas)\b", "pessoal": r"^\W*(moi |je |nous |on |regarde|écoute)",
        "meta": r"une seconde|attends|j'ai oublié|je reviens|je vais chercher|merci beaucoup|abonne|n'oubliez pas|"
                r"prochaine question|next question|on enchaîne|question suivante",
    },
    "en": {
        "forte": ["it", "this", "that", "these", "those", "he", "she", "they", "him", "her", "them", "his", "its", "there",
                  "that's why", "because of that"],
        "conector": ["and", "but", "so", "because", "or", "also", "then", "well", "like", "cause", "yeah", "yes", "no"],
        "pronomes": ["it", "this", "that", "these", "those", "he", "she", "they", "him", "her", "them"],
        "abertos": ["and", "but", "that", "of", "a", "an", "the", "to", "with", "because", "or", "if", "in", "on", "at",
                    "for", "so", "as", "when", "where", "by", "from", "which", "who", "my", "your", "his", "her", "their"],
        "tag": ["right", "you know", "okay", "ok", "huh", "yeah", "isn't it", "though", "eh", "no"],
        "abertura": ["never", "nobody", "seriously", "insane", "crazy", "truth", "lie", "secret", "mistake", "problem",
                     "worst", "best", "shocking", "impossible", "unbelievable"],
        "virada": ["but", "however", "except", "actually", "suddenly", "finally", "turns out"],
        "contraste": r"\b(but|however|except|not)\b", "pessoal": r"^\W*(i |we |look|listen)",
        "meta": r"hold on|one second|i forgot|be right back|thank you so much|subscribe|next question|like and",
    },
    "es": {
        "forte": ["eso", "esto", "él", "ella", "ellos", "ellas", "ese", "esa", "esos", "esas", "este", "esta", "aquello",
                  "por eso", "por esto"],
        "conector": ["y", "pero", "entonces", "porque", "pues", "o", "también", "bueno", "es que", "o sea", "así que",
                     "sí", "no"],
        "pronomes": ["eso", "esto", "él", "ella", "ellos", "ellas", "ese", "esa", "esos", "esas", "aquello"],
        "abertos": ["y", "pero", "que", "de", "del", "la", "el", "los", "las", "un", "una", "para", "con", "porque", "o",
                    "si", "en", "por", "entonces", "como", "cuando", "donde", "al", "a", "sin", "hasta", "mi", "tu", "su"],
        "tag": ["verdad", "vale", "sabes", "eh", "ok", "entiendes", "no"],
        "abertura": ["nunca", "nadie", "increíble", "verdad", "mentira", "secreto", "error", "problema", "peor", "mejor",
                     "impactante", "imposible"],
        "virada": ["pero", "sin embargo", "excepto", "en realidad", "de repente", "al final", "entonces"],
        "contraste": r"\b(pero|sin embargo|excepto|no)\b", "pessoal": r"^\W*(yo |nosotros |mira|oye)",
        "meta": r"un segundo|espera|se me olvidó|ahora vuelvo|muchas gracias|suscríbete|siguiente pregunta",
    },
}
_NUNCA = re.compile(r"(?!x)x")
_FORTE = _CONECTOR = _META = _CONTRASTE = _PESSOAL = _NUNCA
_PRONOMES: set = set()
_ABERTOS: set = set()
_TAG: set = set()
_FORTES_ABERTURA: set = set()
_VIRADA: list = []


def _alt(lista):
    return "|".join(re.escape(x) for x in sorted(lista, key=len, reverse=True))


def _definir(idioma):
    """Escolhe o pacote pelo idioma da transcrição. Sem pacote: só sinais neutros. Devolve o pacote usado."""
    global _FORTE, _CONECTOR, _META, _CONTRASTE, _PESSOAL, _PRONOMES, _ABERTOS, _TAG, _FORTES_ABERTURA, _VIRADA
    cod = (idioma or "").lower().replace("_", "-").split("-")[0]
    pk = PACOTES.get(cod)
    if not pk:
        _FORTE = _CONECTOR = _META = _CONTRASTE = _PESSOAL = _NUNCA
        _PRONOMES, _ABERTOS, _TAG, _FORTES_ABERTURA, _VIRADA = set(), set(), set(), set(), []
        return "neutro"
    _FORTE = re.compile(r"^\W*(" + _alt(pk["forte"]) + r")\b")
    _CONECTOR = re.compile(r"^\W*(" + _alt(pk["conector"]) + r")\b")
    _META = re.compile(pk["meta"])
    _CONTRASTE = re.compile(pk["contraste"])
    _PESSOAL = re.compile(pk["pessoal"])
    _PRONOMES, _ABERTOS, _TAG = set(pk["pronomes"]), set(pk["abertos"]), set(pk["tag"])
    _FORTES_ABERTURA, _VIRADA = set(pk["abertura"]), list(pk["virada"])
    return cod


_definir("pt")  # padrão do módulo; selecionar/revalidar redefinem pelo idioma da transcrição


def _norm(t: str) -> str:
    return t.lower().strip()


def _ultima(texto: str) -> str:
    p = re.findall(r"[\wÀ-ÿ'-]+", texto.lower())
    return p[-1] if p else ""


def _conteudo(texto: str) -> set[str]:
    return {w for w in re.findall(r"[\wÀ-ÿ]+", texto.lower()) if len(w) > 3}


def _pergunta_real(texto: str) -> bool:
    """Pergunta que espera resposta. 'né?', 'sabe?', 'hein?' e interjeições curtas são marcadores, não perguntas."""
    t = texto.rstrip()
    if not t.endswith("?"):
        return False
    ult = re.split(r"(?<=[.!?…])\s+", t)[-1]
    pal = re.findall(r"[\wÀ-ÿ'-]+", ult.lower())
    return not (len(pal) <= 2 or pal[-1] in _TAG)


def ruidosa(texto: str) -> str:
    """Transcrição que não merece corte: alfabeto estranho (alucinação do Whisper) ou repetição em laço."""
    if re.search(r"[Ѐ-ӿͰ-Ͽ一-鿿؀-ۿ]", texto):
        return "alfabeto estranho na transcrição"
    pal = re.findall(r"[\wÀ-ÿ]+", texto.lower())
    if len(pal) >= 12:
        from collections import Counter
        if Counter(pal).most_common(1)[0][1] / len(pal) > 0.30 or len(set(pal)) / len(pal) < 0.30:
            return "repetição em laço (provável erro de transcrição)"
    return ""


def _raras(texto: str) -> set:
    return {w for w in re.findall(r"[^\W\d_]+", texto.lower()) if len(w) >= 6}


def _fecha(texto: str) -> bool:
    """Frase terminada. Reticências ('...', '…'), vírgula e dois-pontos indicam fala interrompida ou em curso."""
    t = texto.rstrip()
    return t[-1:] in (".", "?", "!") and not t.endswith("...")


def _minuscula(texto: str) -> bool:
    m = re.search(r"[^\W\d_]", texto)
    return bool(m) and m.group(0).islower()


def unidades(segs: list[dict]) -> list[dict]:
    """Agrupa segmentos em unidades de pensamento (fronteira: ponto final/pergunta/exclamação + pausa, ou pausa longa)."""
    out: list[dict] = []
    cur: dict | None = None
    prev_fim = None
    for k, s in enumerate(segs):
        gap = (s["ini"] - prev_fim) if prev_fim is not None else 99.0
        fim_ant = cur["texto"].rstrip()[-1:] if cur else ""
        corta = cur is None or gap >= PAUSA_UNIDADE or (fim_ant in ".?!…" and gap >= 0.25)
        if corta:
            cur = {"ini": s["ini"], "fim": s["fim"], "texto": s["texto"].strip(), "seg": [k],
                   "pal": list(s.get("palavras") or [])}
            out.append(cur)
        else:
            cur["fim"] = s["fim"]
            cur["texto"] += " " + s["texto"].strip()
            cur["seg"].append(k)
            cur["pal"] += list(s.get("palavras") or [])
        prev_fim = s["fim"]
    for i, u in enumerate(out):
        u["fecha"] = _fecha(u["texto"])
        u["pergunta"] = _pergunta_real(u["texto"])
        u["pausa"] = (out[i + 1]["ini"] - u["fim"]) if i + 1 < len(out) else 99.0
    for i, u in enumerate(out):
        t = _norm(u["texto"])
        dep = 2 if _FORTE.match(t) else (1 if _CONECTOR.match(t) else 0)
        if i > 0:
            ant = out[i - 1]
            # sinais neutros, valem em qualquer língua de alfabeto latino:
            if _minuscula(u["texto"]) and not ant["fecha"]:
                dep = 2  # começa em minúscula depois de frase não terminada = meio de frase
            if ant["pergunta"] and not u["pergunta"] and u["ini"] - ant["fim"] < 4.0:
                dep = 2  # resposta sem a pergunta
        u["liga"] = False
        if i > 0 and u["ini"] - out[i - 1]["fim"] < LIGA_PAUSA_MAX:
            # palavra "rara" repetida na fronteira = mesma fala/assunto (neutro quanto ao idioma)
            if _raras(out[i - 1]["texto"]) & _raras(u["texto"]):
                u["liga"] = True
                dep = 2
        if len(re.findall(r"[^\W\d_]+", u["texto"])) <= 2:
            dep = 2  # interjeição/reação de uma ou duas palavras não abre um corte
        u["dep"] = dep
    return out


def _dep_inicio(u: dict) -> int:
    return u["dep"]


def _colado(us: list[dict], k: int) -> bool:
    """Começa no meio de uma fala corrida (sem pausa antes) e não é pergunta nem abertura própria."""
    if k == 0 or us[k]["ini"] - us[k - 1]["fim"] >= PAUSA_MIN_FRONTEIRA:
        return False
    return not (us[k]["pergunta"] or _abertura(us[k]["texto"]) >= 0.4)


def _resolver_inicio(us: list[dict], i: int, mx: float, fim: float) -> tuple[int | None, str]:
    """Recua para recuperar a premissa. Devolve (índice do início, motivo se falhar)."""
    k, passos = i, 0
    while us[k]["dep"] >= 1 or _colado(us, k):
        if k == 0:
            return None, "inicio_dependente"
        anterior = us[k - 1]
        gap = us[k]["ini"] - anterior["fim"]
        if us[k]["dep"] == 1 and gap > 1.5:
            break  # conector depois de pausa longa: recomeço de assunto, aceitável
        if passos >= PREMISSA_MAX_UNID or fim - anterior["ini"] > mx or us[i]["ini"] - anterior["ini"] > PREMISSA_MAX_S:
            return None, "inicio_dependente"
        k -= 1
        passos += 1
    return k, ""


def _fim_integro(us: list[dict], j: int) -> str:
    """'' se a unidade j encerra a ideia; senão o motivo."""
    u = us[j]
    if not u["fecha"]:
        return "fim_incompleto"
    if u["pergunta"]:
        return "pergunta_sem_resposta"
    if _ultima(u["texto"]) in _ABERTOS:
        return "fim_incompleto"
    if j + 1 < len(us):
        nxt = us[j + 1]
        if u["pausa"] < 1.0 and nxt["dep"] >= 1 and nxt["dep"] + (1 if u["pausa"] < 0.4 else 0) >= 2:
            return "ideia_continua"
        if u["pausa"] < PAUSA_MIN_FRONTEIRA:
            return "ideia_continua"
        if nxt.get("liga"):
            return "ideia_continua"
    return ""


def _abertura(texto: str) -> float:
    ini = " ".join(texto.split()[:14]).lower()
    s = 0.0
    if re.search(r"[?!]", " ".join(texto.split()[:14])):
        s += 0.4
    if re.search(r"\d", ini):
        s += 0.2
    if _conteudo(ini) & _FORTES_ABERTURA:
        s += 0.3
    if _CONTRASTE.search(ini):
        s += 0.15
    if _PESSOAL.match(ini):
        s += 0.1
    return min(s, 1.0)


def _clareza(texto: str, premissa: bool) -> float:
    pal = re.findall(r"[\wÀ-ÿ]+", texto.lower())
    ini = pal[:8]
    refs = sum(1 for w in ini if w in _PRONOMES)
    c = 1.0 - min(refs, 3) / 3 * (0.4 if premissa else 0.9)
    tot = sum(1 for w in pal if w in _PRONOMES) / max(len(pal), 1)
    return max(0.0, c - min(tot * 3, 0.3))


def _progressao(us: list[dict], i: int, j: int) -> float:
    n = j - i + 1
    base = min(n / 4, 1.0)
    metade = " ".join(u["texto"] for u in us[i + n // 2: j + 1]).lower()
    virada = any(re.search(rf"\b{re.escape(v)}\b", metade) for v in _VIRADA)
    return min(base * 0.75 + (0.25 if virada else 0.0), 1.0)


def _conclusao(us: list[dict], j: int) -> float:
    """Frase fechada vale pouco sozinha; o que prova que a ideia acabou é a pausa depois dela
    (fim no meio de uma história cai: a fala seguinte vem colada)."""
    u = us[j]
    p = u["pausa"]
    pausa = 1.0 if p >= 2.0 else 0.8 if p >= 1.0 else 0.55 if p >= PAUSA_FECHA else 0.3
    return 0.7 * pausa + 0.3 * (1.0 if u["fecha"] and not u["pergunta"] else 0.5)


def _inicio_limpo(us: list[dict], i: int) -> float:
    """Pausa antes do início: 1.0 = recomeço claro; sem pausa, o trecho nasce no meio de uma fala corrida."""
    if i == 0:
        return 1.0
    p = us[i]["ini"] - us[i - 1]["fim"]
    return 1.0 if p >= 1.5 else 0.75 if p >= 1.0 else 0.5


def _vazio(us: list[dict], i: int, j: int) -> float:
    """Fração das unidades que são metadiscurso/enrolação/interação de plataforma (nada a dizer sobre o assunto)."""
    n = j - i + 1
    return sum(1 for u in us[i: j + 1] if _META.search(u["texto"].lower())) / n


def _coesao(us: list, j: int, w: int = 4) -> float:
    """Quanto do vocabulário raro das w falas até j reaparece nas w seguintes (0 a 1). Neutro quanto ao idioma."""
    a = set().union(*[_raras(u["texto"]) for u in us[max(0, j - w + 1): j + 1]])
    b = set().union(*[_raras(u["texto"]) for u in us[j + 1: j + 1 + w]]) if j + 1 < len(us) else set()
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _fecho_forte(us: list, j: int) -> bool:
    """Fim de ASSUNTO: frase íntegra e (pausa longa ou o vocabulário muda)."""
    return not _fim_integro(us, j) and (us[j]["pausa"] >= PAUSA_TOPICO or _coesao(us, j) <= COESAO_BAIXA)


def _dividir(us: list, i: int, j: int, mn: float, mx: float):
    """Divide o assunto i..j no MENOR número de partes que cabem em [mn, mx], cortando só em frase fechada
    (nunca em pergunta, nunca em palavra de ligação, com pausa), com durações equilibradas. None se não der."""
    cortes = [k for k in range(i, j) if us[k]["fecha"] and not us[k]["pergunta"]
              and _ultima(us[k]["texto"]) not in _ABERTOS and us[k]["pausa"] >= PAUSA_MIN_FRONTEIRA]
    fins = cortes + [j]
    dur = lambda a, b: us[b]["fim"] - us[a]["ini"]  # noqa: E731
    total = dur(i, j)
    teto = mx - 0.8  # folga: as bordas em tempo de palavra ganham ~0,4 s
    for n in range(max(2, math.ceil(total / teto)), PARTES_MAX + 1):
        media = total / n
        dp: list[dict] = [{} for _ in range(n + 1)]
        dp[0][i - 1] = (0.0, None)
        for m in range(1, n + 1):
            for e in fins:
                melhor = None
                for pe, (c, _) in dp[m - 1].items():
                    a = pe + 1
                    if a > e:
                        continue
                    d_ = dur(a, e)
                    if d_ < mn or d_ > teto:
                        continue
                    corte_ruim = 0.0
                    if e != j:  # evita cortar onde a fala seguinte retoma a mesma frase/piada (vocabulário raro repetido)
                        corte_ruim = 0.15 * (1 - min(us[e]["pausa"], 1.5) / 1.5) + (0.3 if us[e + 1].get("liga") else 0.0)
                    custo = c + ((d_ - media) / mx) ** 2 + corte_ruim
                    if melhor is None or custo < melhor[0]:
                        melhor = (custo, pe)
                if melhor:
                    dp[m][e] = melhor
        if j in dp[n]:
            partes, e = [], j
            for m in range(n, 0, -1):
                _, pe = dp[m][e]
                partes.append((pe + 1, e))
                e = pe
            return partes[::-1]
    return None


def cta_padrao(n: int, de: int, idioma: str | None) -> str:
    """CTA padrão de série (o Zidane pode reescrever em `cta`). Língua do perfil (público), não da fala."""
    cod = (idioma or "pt").lower().replace("_", "-").split("-")[0]
    if cod == "en":
        return (f"PART {n}/{de} - THERE'S MORE! FOLLOW AND WATCH PART {n + 1}" if n < de
                else f"PART {n}/{de} - THE END! WATCH THE OTHER PARTS ON THE PROFILE")
    if cod == "es":
        return (f"PARTE {n}/{de} - ¡HAY MÁS! SIGUE Y VE LA PARTE {n + 1}" if n < de
                else f"PARTE {n}/{de} - ¡FIN! VE LAS OTRAS PARTES EN EL PERFIL")
    return (f"PARTE {n}/{de} - TEM MAIS! SIGA O PERFIL E VEJA A PARTE {n + 1}" if n < de
            else f"PARTE {n}/{de} - FIM! VEJA AS OUTRAS PARTES NO PERFIL")


def _limites(us: list[dict], i: int, j: int, dur_video: float | None) -> tuple[float, float]:
    """Início e fim em tempo de palavra, com folga curta que não invade a fala vizinha."""
    pi, pj = us[i]["pal"], us[j]["pal"]
    ini = (pi[0]["ini"] if pi else us[i]["ini"]) - FOLGA_INI
    fim = (pj[-1]["fim"] if pj else us[j]["fim"]) + FOLGA_FIM
    if i > 0:
        pa = us[i - 1]["pal"]
        ini = max(ini, (pa[-1]["fim"] if pa else us[i - 1]["fim"]) + 0.02)
    if j + 1 < len(us):
        pn = us[j + 1]["pal"]
        fim = min(fim, (pn[0]["ini"] if pn else us[j + 1]["ini"]) - 0.02)
    if dur_video:
        fim = min(fim, dur_video)
    return round(max(ini, 0.0), 2), round(fim, 2)


def _chamada(us: list[dict], i: int, j: int) -> dict | None:
    """Sugestão de abertura com fala forte do próprio trecho (só sugere; quem aplica é o Figo/cortar).
    Só quando o início cronológico é fraco, a fala é completa, independente e NÃO é o desfecho."""
    if _abertura(us[i]["texto"]) >= 0.4:
        return None
    melhor, nota = None, 0.0
    for k in range(i + 1, j):  # nunca a última unidade: antecipar o desfecho estraga piada/revelação
        u = us[k]
        d = u["fim"] - u["ini"]
        if not (1.5 <= d <= 7.0) or not u["fecha"] or u["pergunta"] or u["dep"] >= 1:
            continue
        a = _abertura(u["texto"])
        if a >= 0.5 and a > nota:
            melhor, nota = u, a
    if not melhor:
        return None
    pw = melhor["pal"]
    return {"ini": round((pw[0]["ini"] if pw else melhor["ini"]) - 0.05, 2),
            "fim": round((pw[-1]["fim"] if pw else melhor["fim"]) + 0.15, 2), "texto": melhor["texto"],
            "motivo": "fala forte e completa do próprio trecho; o desfecho continua no final"}


def selecionar(segs: list[dict], perfil: dict, z: np.ndarray, quantos: int, energia: bool = True,
               usar_termos: bool = True, dur_video: float | None = None,
               idioma: str | None = None) -> tuple[list[dict], dict]:
    """Devolve (momentos, relatório). Momentos já no formato de momentos.json, com o registro editorial."""
    mn, mx = perfil["duracao"]["min"], perfil["duracao"]["max"]
    w = dict(perfil["selecao"]["pesos"])
    if not energia:
        w["pico_audio"] = 0.0
    if not usar_termos:
        w["palavras_chave"] = 0.0
    lim = max(perfil["selecao"]["limite_palavras"], 1)
    from . import perfis as PF
    termos = PF.termos_selecao(perfil) if usar_termos else []
    excluir = [t.lower() for t in perfil["assuntos_excluir"]]
    pacote = _definir(idioma)
    us = unidades(segs)
    curto = np.concatenate([[0], np.cumsum([1 if len(sg["texto"].split()) <= 3 else 0 for sg in segs])])
    desc: dict[str, int] = {}

    def nega(m):
        desc[m] = desc.get(m, 0) + 1

    def avaliar(i, i0, j, partes=None):
        """Gates de integridade + critérios de uma janela i..j (ou de um assunto dividido em `partes`)."""
        texto = " ".join(u["texto"] for u in us[i: j + 1])
        low = texto.lower()
        faixas = partes or [(i, j)]
        for (a, b) in faixas:
            t_ = " ".join(u["texto"] for u in us[a: b + 1])
            if len(t_.split()) < PALAVRAS_MIN:
                nega("pouca_fala")
                return None
            a_, b_ = us[a]["seg"][0], us[b]["seg"][-1]
            if float(curto[b_ + 1] - curto[a_]) / (b_ - a_ + 1) > 0.5:  # fração de falas de até 3 palavras
                nega("fala_picada")
                return None
            if _vazio(us, a, b) > 0.34:
                nega("conversa_vazia")
                return None
        # ruído é local (a razão de palavras únicas cai com o tamanho do texto): confere cada parte, não o assunto todo
        if any(ruidosa(" ".join(u["texto"] for u in us[a: b + 1])) for (a, b) in faixas):
            nega("transcricao_ruidosa")
            return None
        if [t for t in excluir if t in low]:
            nega("assunto_excluido")
            return None
        ini, fim = _limites(us, i, j, dur_video)
        a_, b_ = us[i]["seg"][0], us[j]["seg"][-1]
        picado = float(curto[b_ + 1] - curto[a_]) / (b_ - a_ + 1)
        janela = z[int(ini / 0.5): int(fim / 0.5) + 1] if energia else ()
        pico = float(np.percentile(janela, 90)) if len(janela) else 0.0
        achados = [t for t in termos if t in low]
        wps = len(low.split()) / max(fim - ini, 1.0)
        premissa = i < i0
        pos = {k: w.get(k, 0) for k in ("pico_audio", "palavras_chave", "densidade_fala")}
        soma = sum(v for v in pos.values() if v > 0)
        interesse = ((pos["pico_audio"] * min(max(pico, 0) / 3, 1) + pos["palavras_chave"] * min(len(achados), lim) / lim
                      + pos["densidade_fala"] * min(wps / 3, 1)) / soma) if soma else 0.5
        interesse *= 1.0 - 0.5 * picado
        crit = {"abertura": _abertura(us[i]["texto"]) if not premissa else max(_abertura(us[i]["texto"]), _abertura(us[i0]["texto"])),
                "clareza": _clareza(texto, premissa), "interesse": interesse,
                "progressao": _progressao(us, i, j), "conclusao": _conclusao(us, j),
                "independencia": (0.75 if premissa else 1.0) * (0.6 + 0.4 * _inicio_limpo(us, i))}
        nota = sum(PESOS[k] * v for k, v in crit.items()) + (SERIE_BONUS if partes else 0.0)
        return {"i": i, "j": j, "i0": i0, "ini": ini, "fim": fim, "nota": nota, "crit": crit, "texto": texto,
                "achados": achados, "pico": pico, "wps": wps, "premissa": premissa, "partes": partes}

    cands: list[dict] = []
    vistos: set[tuple[int, int]] = set()
    for i0 in range(len(us)):
        i, falha = _resolver_inicio(us, i0, mx, us[i0]["fim"])
        if i is None:
            nega(falha)
            continue
        for j in range(i0, len(us)):
            if (i, j) in vistos:
                continue
            dur = us[j]["fim"] - us[i]["ini"]
            if dur > mx:
                break
            if dur < mn:
                continue
            vistos.add((i, j))
            m = _fim_integro(us, j)
            if m:
                nega(m)
                continue
            c = avaliar(i, i0, j)
            if c:
                cands.append(c)

    # Assunto que não coube em um vertical: série em partes (cada uma dentro do limite, cortes em frase fechada)
    series = 0
    if PARTES_MAX > 1:
        vistas: set[tuple[int, int]] = set()
        for i0 in range(len(us)):
            i, _f = _resolver_inicio(us, i0, mx, us[i0]["fim"])
            if i is None:
                continue
            for j in range(i0, len(us)):
                dur = us[j]["fim"] - us[i]["ini"]
                if dur > mx * PARTES_MAX:
                    break
                if dur < mn or not _fecho_forte(us, j):
                    continue
                if dur <= mx:
                    break  # o assunto fechou dentro de um vertical: é corte único, não série
                if (i, j) not in vistas:
                    vistas.add((i, j))
                    partes = _dividir(us, i, j, mn, mx)
                    if not partes:
                        nega("serie_sem_corte_integro")
                    else:
                        c = avaliar(i, i0, j, partes)
                        if c:
                            cands.append(c)
                            series += 1
                break

    cands.sort(key=lambda c: c["nota"], reverse=True)
    ok: list[dict] = []
    for c in cands:
        if c["nota"] < NOTA_MINIMA:
            nega("abaixo_do_minimo")
            continue
        if any(not (c["fim"] <= e["ini"] or c["ini"] >= e["fim"]) for e in ok):
            nega("sobreposto")
            continue
        cc = _conteudo(c["texto"])
        if any(len(cc & e["_cc"]) / max(len(cc | e["_cc"]), 1) > SIMILARIDADE_MAX for e in ok):
            nega("redundante")
            continue
        c["_cc"] = cc
        ok.append(c)
        if len(ok) == quantos:
            break
    ok.sort(key=lambda c: c["ini"])

    momentos = []
    rot = {"abertura": "abertura forte", "clareza": "se entende sozinho", "interesse": "sinais de interesse",
           "progressao": "tem desenvolvimento", "conclusao": "fecha a ideia", "independencia": "sem dependência de contexto"}
    for ns, c in enumerate(ok, 1):
        i, j = c["i"], c["j"]
        crit = {k: round(v, 2) for k, v in c["crit"].items()}
        fortes = sorted(crit, key=crit.get, reverse=True)[:2]
        faixas = c["partes"] or [(i, j)]
        for k, (a, b) in enumerate(faixas, 1):
            ini, fim = _limites(us, a, b, dur_video) if c["partes"] else (c["ini"], c["fim"])
            just = "Íntegro (início e fim completos); destaca: " + ", ".join(rot[x] for x in fortes)
            if c["premissa"] and k == 1:
                just += "; premissa recuperada"
            if c["partes"]:
                just = (f"Assunto de {c['fim'] - c['ini']:.0f}s que não coube em um vertical: parte {k} de {len(faixas)}, "
                        f"cortada em frase fechada; " + just)
            txt = " ".join(u["texto"] for u in us[a: b + 1])
            m = {"id": len(momentos) + 1, "ini": ini, "fim": fim, "dur": round(fim - ini, 1),
                 "score": round(c["nota"], 3), "quentes": len(c["achados"]), "texto": txt[:160].lower(),
                 "sinais": {"pico_audio": round(c["pico"], 2), "palavras_chave": c["achados"][:8],
                            "abertura_forte": crit["abertura"] >= 0.4, "densidade_fala": round(c["wps"], 2),
                            "assunto_excluido": []},
                 "criterios": [rot[x] for x in fortes], "motivo": just, "justificativa": just,
                 "avaliacao": crit,
                 "segmentos_origem": sorted({sg for u in us[a: b + 1] for sg in u["seg"]}),
                 "montagem": {"ordem": "cronologica", "trechos": [{"ini": ini, "fim": fim}]},
                 "contexto_necessario": (" ".join(u["texto"] for u in us[i: c["i0"]]) if c["premissa"] and k == 1 else ""),
                 "conclusao": us[b]["texto"], "problemas": [],
                 "correcoes": (["premissa recuperada antes do início"] if c["premissa"] and k == 1 else []),
                 "versao_selecao": VERSAO, "status": "sugerido"}
            if c["partes"]:
                m["serie"] = {"id": f"s{ns}", "parte": k, "de": len(faixas)}
                m["cta"] = cta_padrao(k, len(faixas), perfil.get("idioma"))
            else:
                ch = _chamada(us, i, j)
                if ch:
                    m["gancho_trecho_sugerido"] = ch
            momentos.append(m)
    rel = {"versao": VERSAO, "pacote_idioma": pacote, "idioma": idioma, "unidades": len(us), "candidatos_integros": len(cands), "escolhidos": len(ok), "cortes": len(momentos), "series": sum(1 for c in ok if c["partes"]),
           "pedidos": quantos, "descartes": desc,
           "nota": "Notas são heurísticas de comparação, não previsão de alcance. Menos cortes que o pedido = "
                   "não havia mais momentos íntegros acima da nota mínima."}
    return momentos, rel


def revalidar(segs: list[dict], ini: float, fim: float, perfil: dict, idioma: str | None = None) -> dict:
    """Confere um intervalo qualquer (ajuste do Kaká ou manual) com os mesmos critérios de integridade.
    Alinha às fronteiras de palavra e devolve {ini, fim, problemas, correcoes}. Não inventa precisão: se o
    intervalo cai no meio de uma unidade, ESTENDE até a fronteira da unidade (não encurta o conteúdo)."""
    _definir(idioma)
    us = unidades(segs)
    mx = perfil["duracao"]["max"]
    probs: list[str] = []   # duros: reprovam o intervalo
    avisos: list[str] = []  # heurísticas: o código não derruba o julgamento de quem leu o texto (Kaká ou o usuário)
    corr: list[str] = []
    # unidade que contém o instante de início e a que contém o instante de fim
    i = next((k for k, u in enumerate(us) if u["ini"] - 0.3 <= ini <= u["fim"]), None)
    j = next((k for k in range(len(us) - 1, -1, -1) if us[k]["ini"] <= fim <= us[k]["fim"] + 0.3), None)
    if i is None or j is None or j < i:
        return {"ini": ini, "fim": fim, "problemas": ["intervalo sem fala alinhada na transcrição"], "avisos": [], "correcoes": []}
    if ini > us[i]["ini"] + 0.5:
        corr.append("início no meio de uma frase: recuado para o começo da frase")
    if fim < us[j]["fim"] - 0.5:
        corr.append("fim no meio de uma frase: avançado até o fim da frase")
    k, falha = _resolver_inicio(us, i, mx, us[i]["fim"])
    if k is None:
        avisos.append("início parece depender de contexto que ficou de fora (referência sem explicação)")
    elif k < i:
        corr.append("premissa recuperada antes do início")
        i = k
    m = _fim_integro(us, j)
    if m in ("fim_incompleto", "pergunta_sem_resposta"):  # só estende o que é objetivamente inacabado
        for t in (j + 1, j + 2):
            if t < len(us) and us[t]["fim"] - us[i]["ini"] <= mx and not _fim_integro(us, t):
                corr.append("fim estendido até a conclusão")
                j = t
                m = ""
                break
    if m == "ideia_continua":
        avisos.append("a fala seguinte pode continuar a mesma ideia")
    elif m:
        probs.append({"fim_incompleto": "termina antes de a ideia fechar",
                      "pergunta_sem_resposta": "termina numa pergunta sem a resposta"}[m])
    a, b = _limites(us, i, j, None)
    if b - a > mx:
        probs.append(f"intervalo íntegro ({b - a:.0f}s) passa do máximo do perfil ({mx:.0f}s)")
    r = ruidosa(" ".join(u["texto"] for u in us[i: j + 1]))
    if r:
        probs.append(r)
    return {"ini": a, "fim": b, "problemas": probs, "avisos": avisos, "correcoes": corr}


def momentos_de_intervalos(segs: list[dict], perfil: dict, itens: list[dict], quantos: int, idioma: str | None = None,
                           dur_video: float | None = None) -> tuple[list[dict], dict]:
    """Transforma os melhores momentos do Rivaldo (`itens`: ini, fim, nota, por_que, ordenados da maior nota) em
    momentos do fluxo: alinha às palavras, recupera a premissa, estende o que termina no meio, divide em partes
    (Parte 1/2...) o que passa do limite de um vertical e descarta o que não dá para cortar íntegro, seguindo para
    o próximo da lista até completar `quantos` assuntos. Mesmo formato de `selecionar`."""
    _definir(idioma)
    us = unidades(segs)
    mn, mx = perfil["duracao"]["min"], perfil["duracao"]["max"]
    ok: list[dict] = []
    descartes: dict[str, list[int]] = {}

    def nega(m: str, it: dict) -> None:
        descartes.setdefault(m, []).append(int(it["ini"]))

    for rank, it in enumerate(itens, 1):
        if len(ok) >= quantos:
            break
        a, b = float(it["ini"]), float(it["fim"])
        i = next((k for k, u in enumerate(us) if u["ini"] - 0.3 <= a <= u["fim"]), None)
        j = next((k for k in range(len(us) - 1, -1, -1) if us[k]["ini"] <= b <= us[k]["fim"] + 0.3), None)
        if i is None or j is None or j < i:
            nega("sem_fala_alinhada", it)
            continue
        i0 = i
        k, _f = _resolver_inicio(us, i, mx * PARTES_MAX, us[i]["fim"])
        if k is not None:
            i = k
        for t in (j + 1, j + 2):  # só estende o que é objetivamente inacabado
            if _fim_integro(us, j) in ("fim_incompleto", "pergunta_sem_resposta") and t < len(us) \
                    and us[t]["fim"] - us[i]["ini"] <= mx * PARTES_MAX:
                j = t
        if ruidosa(" ".join(u["texto"] for u in us[i: j + 1])[:4000]):
            nega("transcricao_ruidosa", it)
            continue
        dur = us[j]["fim"] - us[i]["ini"]
        if dur <= mx:
            faixas = [(i, j)]
        elif dur <= mx * PARTES_MAX:
            faixas = _dividir(us, i, j, mn, mx)
            if not faixas:
                nega("serie_sem_corte_integro", it)
                continue
        else:
            nega("maior_que_o_maximo_de_partes", it)
            continue
        ok.append({"it": it, "rank": rank, "i": i, "j": j, "i0": i0, "premissa": i < i0, "faixas": faixas})
    ok.sort(key=lambda c: us[c["i"]]["ini"])
    momentos: list[dict] = []
    for ns, c in enumerate(ok, 1):
        nota = float(c["it"].get("nota", 0))
        for n, (a, b) in enumerate(c["faixas"], 1):
            ini, fim = _limites(us, a, b, dur_video)
            txt = " ".join(u["texto"] for u in us[a: b + 1])
            crit = {"abertura": _abertura(us[a]["texto"]), "clareza": _clareza(txt, c["premissa"] and n == 1),
                    "interesse": nota / 100.0, "progressao": _progressao(us, a, b), "conclusao": _conclusao(us, b),
                    "independencia": (0.75 if c["premissa"] and n == 1 else 1.0) * (0.6 + 0.4 * _inicio_limpo(us, a))}
            por_que = str(c["it"].get("por_que") or "")
            just = f"Escolhido pelo Rivaldo: nota {nota:.0f}, #{c['rank']} da triagem. {por_que}".strip()
            if len(c["faixas"]) > 1:
                just = f"Assunto que não coube em um vertical: parte {n} de {len(c['faixas'])}. " + just
            m = {"id": len(momentos) + 1, "ini": ini, "fim": fim, "dur": round(fim - ini, 1), "score": round(nota / 100.0, 3),
                 "quentes": 0, "texto": txt[:160].lower(),
                 "sinais": {"pico_audio": 0.0, "palavras_chave": [], "abertura_forte": crit["abertura"] >= 0.4,
                            "densidade_fala": 0.0, "assunto_excluido": []},
                 "criterios": [f"melhor momento da triagem (nota {nota:.0f})"], "motivo": just, "justificativa": just,
                 "avaliacao": {k_: round(v, 2) for k_, v in crit.items()},
                 "segmentos_origem": sorted({sg for u in us[a: b + 1] for sg in u["seg"]}),
                 "montagem": {"ordem": "cronologica", "trechos": [{"ini": ini, "fim": fim}]},
                 "contexto_necessario": (" ".join(u["texto"] for u in us[c["i"]: c["i0"]]) if c["premissa"] and n == 1 else ""),
                 "conclusao": us[b]["texto"], "problemas": [],
                 "correcoes": (["premissa recuperada antes do início"] if c["premissa"] and n == 1 else []),
                 "origem": "rivaldo", "nota_rivaldo": nota, "rank_triagem": c["rank"],
                 "versao_selecao": VERSAO, "status": "sugerido"}
            if len(c["faixas"]) > 1:
                m["serie"] = {"id": f"s{ns}", "parte": n, "de": len(c["faixas"])}
                m["cta"] = cta_padrao(n, len(c["faixas"]), perfil.get("idioma"))
            momentos.append(m)
    rel = {"versao": VERSAO, "origem": "triagem do Rivaldo", "idioma": idioma, "pedidos": quantos, "escolhidos": len(ok),
           "cortes": len(momentos), "series": sum(1 for c in ok if len(c["faixas"]) > 1), "descartes": descartes,
           "nota": "Momentos escolhidos pelo Rivaldo (nota editorial, não previsão de alcance) e alinhados pelo código às "
                   "palavras e às frases. Menos que o pedido = os outros não davam corte íntegro dentro do limite."}
    return momentos, rel
