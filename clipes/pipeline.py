"""Pipeline de clipagem: fonte -> transcrição -> melhores momentos -> cortes 9:16.

Tudo local e gratuito (ffmpeg, faster-whisper, yt-dlp). Cada etapa é idempotente
e grava em clipes_out/<slug>/. O que é específico de um nicho (termos, pesos, duração,
quantidade, hashtags, idioma) vem do perfil do projeto (perfis.py, clipes_out/<slug>/perfil.json).

TRAVA DE AUTORIZAÇÃO: material de terceiros só entra com `autorizacao` registrada
(tipo + prova). Sem isso, `ingest` recusa e `check` reprova. Reupload sem
permissão derruba a monetização (conteúdo reutilizado) e gera strike.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from . import estado as E
from . import perfis as PF

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = Path(os.environ.get("CLIPES_SAIDA") or RAIZ / "clipes_out")  # CLIPES_SAIDA só para testes

# Tipos de autorização aceitos. "teste" só para provas técnicas, nunca publica.
AUTORIZACOES = {"proprio", "parceria", "permissao", "licenca", "livre", "teste"}
# "livre" = corte sem autorização do criador, risco assumido pelo Guilherme (decisão de 2026-11-10).
# Não exige prova, mas o check continua exigindo crédito e comentário próprio (gancho/fecho).

# Termos, pesos e janelas de seleção vêm do perfil (clipes/perfis/). As regras fixas da V1
# (termos de GTA 6, janelas de 20-55 s, hashtags) viraram o perfil gta6 versão 1.


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    # stdin vazio: sem console (painel aberto sem terminal) o ffmpeg falha ao tentar ler o teclado
    return subprocess.run(cmd, check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL, **kw)


def pasta(slug: str) -> Path:
    p = SAIDA / slug
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _gravar(p: Path, d) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:50] or "clipe"


# --------------------------------------------------------------------- ingest
def _baixar(d: Path, origem: str, destino: Path) -> None:
    """yt-dlp com o percentual real de download reportado ao painel."""
    cmd = [sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]",
           "--merge-output-format", "mp4", "--retries", "20", "--fragment-retries", "20",
           "--newline", "-o", str(destino), origem]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, stdin=subprocess.DEVNULL,
                            encoding="utf-8", errors="replace")
    linhas: list[str] = []
    ultimo = -10.0
    for lin in proc.stdout:  # type: ignore[union-attr]
        linhas.append(lin.rstrip())
        m = re.search(r"\[download\]\s+([\d.]+)%", lin)
        if m and float(m.group(1)) - ultimo >= 2:
            ultimo = float(m.group(1))
            E.marcar(d, "fonte", "trabalhando", f"baixando o vídeo: {ultimo:.0f}%", progresso=ultimo / 100)
    if proc.wait() != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, "\n".join(linhas), "\n".join(linhas[-12:]))


def ingest(origem: str, slug: str | None, autorizacao: str, prova: str,
           autor: str, titulo_original: str = "", perfil: str = PF.PADRAO_NOVOS) -> Path:
    """Registra a fonte (arquivo local ou URL) com a autorização e congela o perfil. Baixa se URL."""
    if autorizacao not in AUTORIZACOES:
        raise SystemExit(f"autorizacao invalida: {autorizacao!r}. Use: {sorted(AUTORIZACOES)}")
    if autorizacao not in ("proprio", "teste", "livre") and not prova.strip():
        raise SystemExit("material de terceiros exige --prova (link/print/e-mail da permissão).")
    if not autor.strip():
        raise SystemExit("--autor é obrigatório (crédito no vídeo e na descrição).")

    try:
        PF.carregar(perfil)
    except KeyError:
        raise SystemExit(f"perfil não encontrado: {perfil!r}. Veja: python -m clipes perfis") from None
    eh_url = origem.startswith(("http://", "https://"))
    slug = slug or slugify(titulo_original or (origem if not eh_url else autor))
    d = pasta(slug)
    PF.congelar(d, perfil)
    destino = d / "fonte.mp4"
    _gravar(d / "fonte.json", {  # cedo, para o painel já mostrar o projeto durante o download
        "origem": origem, "autor": autor, "titulo_original": titulo_original,
        "autorizacao": {"tipo": autorizacao, "prova": prova},
    })
    E.marcar(d, "fonte", "trabalhando", "baixando/copiando o vídeo")

    if not destino.exists():
        if eh_url:
            try:
                _baixar(d, origem, destino)
            except subprocess.CalledProcessError as e:
                linhas = [x for x in (e.stderr or "").strip().splitlines() if x.strip()]
                E.marcar(d, "fonte", "falhou", "o download do vídeo falhou", None, linhas[-4:] or [str(e)],
                         "Rode o mesmo comando de novo (o yt-dlp continua de onde parou). Se repetir, "
                         "veja o erro acima: vídeo privado, sem internet ou YouTube bloqueando.")
                raise SystemExit("download falhou; veja o painel.") from e
        else:
            src = Path(origem)
            if not src.exists():
                raise SystemExit(f"arquivo não encontrado: {src}")
            _run(["ffmpeg", "-y", "-i", str(src), "-c", "copy", str(destino)])

    _gravar(d / "fonte.json", {
        "origem": origem, "autor": autor, "titulo_original": titulo_original,
        "autorizacao": {"tipo": autorizacao, "prova": prova},
    })
    E.marcar(d, "fonte", "concluido", f"{autor}: {titulo_original or origem}"[:120])
    if autorizacao == "teste":
        E.marcar(d, "autorizacao", "bloqueado", "tipo 'teste': só prova técnica, não publica")
    elif autorizacao == "livre":
        E.marcar(d, "autorizacao", "concluido", "sem autorização do criador: risco assumido pelo Guilherme")
    else:
        E.marcar(d, "autorizacao", "concluido", f"{autorizacao}: {prova or 'conteúdo próprio'}"[:120])
    print(f"[ingest] {slug} registrado ({autorizacao}).")
    return d


# ----------------------------------------------------------------- transcrever
def pertence_ao_bloco(seg: dict, off: float, bloco: float, primeiro: bool) -> bool:
    """Cada segmento fica com UM bloco: o do seu ponto médio. Com a sobreposição, a frase que cruza a fronteira
    é transcrita inteira no bloco a que pertence e descartada (sem duplicar) no outro."""
    meio = (seg["ini"] + seg["fim"]) / 2
    return (primeiro or meio >= off) and meio < off + bloco


def transcrever(d: Path, modelo: str = "small") -> dict:
    alvo = d / "transcricao.json"
    if alvo.exists():
        return _ler(alvo)
    from faster_whisper import WhisperModel

    perfil = PF.do_projeto(d)
    idioma = None if perfil["idioma_fala"] == "auto" else perfil["idioma_fala"]
    vocab = PF.vocabulario(perfil) or None  # nomes e termos do nicho ajudam o Whisper a acertar a grafia
    E.marcar(d, "transcricao", "trabalhando", f"modelo whisper {modelo}")

    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    # Em blocos: vídeo longo inteiro estoura a memória no extrator de áudio do Whisper.
    dur = float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(d / "fonte.mp4")]).stdout.strip())
    bloco = 600.0
    sobre = 30.0  # sobreposição: nenhuma frase é partida na fronteira de um bloco
    n_blocos = int(dur // bloco) + 1
    out = {"idioma": None, "segmentos": []}
    wav = d / "_bloco.wav"
    try:
        for i in range(n_blocos):
            off = i * bloco
            ini_a = max(0.0, off - sobre)  # o áudio começa antes; só se guarda o que "pertence" ao bloco
            E.marcar(d, "transcricao", "trabalhando", f"modelo {modelo}: bloco {i + 1}/{n_blocos}",
                     progresso=i / n_blocos)
            _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini_a}", "-t", f"{bloco + off - ini_a + sobre}", "-i",
                  str(d / "fonte.mp4"), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
            segs, info = m.transcribe(str(wav), language=idioma, word_timestamps=True, vad_filter=True,
                                      hotwords=vocab)
            out["idioma"] = out["idioma"] or info.language
            for s in segs:
                seg = {"ini": s.start + ini_a, "fim": s.end + ini_a, "texto": s.text.strip(),
                       "palavras": [{"ini": w.start + ini_a, "fim": w.end + ini_a, "t": w.word.strip()}
                                    for w in (s.words or [])]}
                if pertence_ao_bloco(seg, off, bloco, i == 0):
                    out["segmentos"].append(seg)
    except Exception as e:  # noqa: BLE001 - o painel precisa mostrar a falha
        txt = str(e)
        faltou_mem = any(k in txt.lower() for k in ("memória", "memory", "mkl_malloc", "paginação"))
        E.marcar(d, "transcricao", "falhou", txt[:120], None, [txt[-400:]],
                 "O Windows ficou sem memória: feche programas (Chrome, Steam, ChatGPT) e rode o comando de novo; ele continua de onde parou."
                 if faltou_mem else "Veja o erro acima e rode o comando de novo.")
        raise
    finally:
        wav.unlink(missing_ok=True)
    _gravar(alvo, out)
    E.marcar(d, "transcricao", "concluido", f"{len(out['segmentos'])} trechos, idioma {out['idioma']}")
    print(f"[transcrever] {len(out['segmentos'])} segmentos, idioma {out['idioma']}.")
    return out


def refinar(d: Path, modelo: str = "small", folga: float = 1.0, ids: list[int] | None = None) -> int:
    """Retranscreve só os trechos escolhidos (momentos.json; `ids` limita a alguns) com um modelo melhor.
    Troca as palavras desses trechos em transcricao.json e atualiza o texto do momento."""
    from faster_whisper import WhisperModel

    tr = _ler(d / "transcricao.json")
    mom = _ler(d / "momentos.json")
    perfil = PF.do_projeto(d)
    idioma = "pt" if perfil["idioma_fala"] == "auto" else perfil["idioma_fala"]  # V1 refinava sempre em pt
    vocab = PF.vocabulario(perfil) or None
    alvos = [c for c in mom if not ids or c["id"] in ids]
    E.marcar(d, "transcricao", "trabalhando", f"refinando {len(alvos)} trecho(s) com {modelo}")
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    wav = d / "_refino.wav"
    try:
        for k, c in enumerate(alvos):
            E.marcar(d, "transcricao", "trabalhando", f"refinando trecho {k + 1} de {len(alvos)} com {modelo}",
                     progresso=k / len(alvos))
            ini = max(0.0, c["ini"] - folga)
            fim = c["fim"] + folga
            _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini}", "-t", f"{fim - ini}", "-i",
                  str(d / "fonte.mp4"), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
            segs, _ = m.transcribe(str(wav), language=idioma, word_timestamps=True, vad_filter=True,
                                   hotwords=vocab)
            novos = [{"ini": s.start + ini, "fim": s.end + ini, "texto": s.text.strip(),
                      "palavras": [{"ini": w.start + ini, "fim": w.end + ini, "t": w.word.strip()}
                                   for w in (s.words or [])]} for s in segs]
            tr["segmentos"] = [s for s in tr["segmentos"] if s["fim"] <= ini or s["ini"] >= fim] + novos
            c["texto"] = " ".join(s["texto"] for s in novos
                                  if s["ini"] >= c["ini"] - 0.5 and s["fim"] <= c["fim"] + 0.5)[:160].lower()
    finally:
        wav.unlink(missing_ok=True)
    tr["segmentos"].sort(key=lambda s: s["ini"])
    _gravar(d / "transcricao.json", tr)
    _gravar(d / "momentos.json", mom)
    E.marcar(d, "transcricao", "concluido", f"{len(alvos)} trecho(s) refinado(s) com {modelo}")
    print(f"[refinar] {len(alvos)} trecho(s) retranscrito(s) com {modelo}.")
    return len(alvos)


# --------------------------------------------------------------------- momentos
def _energia(video: Path, passo: float = 0.5) -> np.ndarray:
    """RMS do áudio por janela de `passo` s (picos = gritos, reações, explosões)."""
    sr = 8000
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr),
         "-f", "s16le", "-"], check=True, capture_output=True, stdin=subprocess.DEVNULL).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    n = int(sr * passo)
    k = len(a) // n
    return np.sqrt((a[: k * n].reshape(k, n) ** 2).mean(axis=1)) if k else np.zeros(1)


def _contexto(segs: list[dict], i: int, j: int, antes: float, depois: float) -> tuple[float, float]:
    """Estende o trecho para incluir falas inteiras que começam/terminam dentro do contexto pedido."""
    ini, fim = segs[i]["ini"], segs[j]["fim"]
    k = i
    while antes > 0 and k > 0 and segs[k - 1]["ini"] >= ini - antes:
        k -= 1
    m = j
    while depois > 0 and m + 1 < len(segs) and segs[m + 1]["fim"] <= fim + depois:
        m += 1
    return segs[k]["ini"], segs[m]["fim"]


def momentos(d: Path, quantos: int | None = None, energia: bool = True, usar_termos: bool = True,
             legado: bool | None = None, intervalos: tuple | None = None) -> list[dict]:
    """Sugere trechos pelo perfil do projeto. Sinais medidos de verdade: pico de áudio, termos do perfil,
    abertura com pergunta/exclamação, densidade de fala e termos a excluir. Cada sugestão traz o
    intervalo, os sinais encontrados e o motivo. Não detecta nada visual (lance, jogada, rosto).
    `energia`/`usar_termos` False desligam esses sinais (ferramentas da etapa no fluxo do projeto)."""
    alvo = d / "momentos.json"
    if alvo.exists():
        return _ler(alvo)
    perfil = PF.do_projeto(d)
    quantos = quantos or perfil["quantidade"]
    mn, mx = perfil["duracao"]["min"], perfil["duracao"]["max"]
    w = dict(perfil["selecao"]["pesos"])
    if not energia:
        w["pico_audio"] = 0.0
    if not usar_termos:
        w["palavras_chave"] = 0.0
    lim = perfil["selecao"]["limite_palavras"]
    termos = PF.termos_selecao(perfil)
    excluir = [t.lower() for t in perfil["assuntos_excluir"]]
    E.marcar(d, "momentos", "trabalhando", f"perfil {perfil['nome']}: medindo áudio e termos")
    tr = _ler(d / "transcricao.json")
    segs = tr["segmentos"]
    if energia:
        en = _energia(d / "fonte.mp4")
        z = (en - en.mean()) / (en.std() + 1e-6)
    else:
        z = np.zeros(1)

    if legado is None:
        legado = not (d / "perfil.json").exists()  # `legado` explícito só para comparar antes/depois nos testes
    if not legado:  # V3: seleção editorial (projetos legados sem perfil seguem a V1 abaixo)
        from . import editorial as ED
        dv = float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                         str(d / "fonte.mp4")]).stdout.strip()) if (d / "fonte.mp4").exists() else None
        if intervalos:  # os N melhores momentos da triagem do Rivaldo seguem; o seletor geral não roda
            escolhidos, rel = ED.momentos_de_intervalos(segs, perfil, intervalos[0], intervalos[1], tr.get("idioma"), dv)
            for m in escolhidos:
                m["perfil"] = {"id": perfil["id"], "versao": perfil["versao"]}
            _gravar(alvo, escolhidos)
            _gravar(d / "selecao.json", rel)
            notas = ", ".join(f"{m['nota_rivaldo']:.0f}" for m in escolhidos if not m.get("serie") or m["serie"]["parte"] == 1)
            E.marcar(d, "momentos", "concluido",
                     f"os {rel['escolhidos']} melhores da triagem do Rivaldo (notas {notas}): {len(escolhidos)} corte(s) (revisar)")
            E.marcar(d, "comentario", "pendente", "aguarda Zidane: gancho e fecho próprios em momentos.json")
            print(f"[momentos] {rel['escolhidos']} melhores da triagem ({len(escolhidos)} cortes).")
            return escolhidos
        escolhidos, rel = ED.selecionar(segs, perfil, z, quantos, energia, usar_termos, dv, tr.get("idioma"))
        for m in escolhidos:
            m["perfil"] = {"id": perfil["id"], "versao": perfil["versao"]}
        _gravar(alvo, escolhidos)
        _gravar(d / "selecao.json", rel)
        E.marcar(d, "momentos", "concluido",
                 f"{len(escolhidos)} momento(s) íntegro(s) pelo perfil {perfil['nome']} (revisar)"
                 + ("" if len(escolhidos) == quantos else f"; pedidos {quantos}: o resto não tinha início e fim completos"))
        E.marcar(d, "comentario", "pendente", "aguarda Zidane: gancho e fecho próprios em momentos.json")
        print(f"[momentos] {len(escolhidos)} candidatos íntegros (selecao.json traz os descartes).")
        return escolhidos

    cands = []
    for i, s0 in enumerate(segs):
        ini = s0["ini"]
        for j in range(i, len(segs)):
            fim = segs[j]["fim"]
            dur = fim - ini
            if dur > mx:
                break
            if dur < mn:
                continue
            texto = " ".join(x["texto"] for x in segs[i : j + 1]).lower()
            nw = len(texto.split())
            janela = z[int(ini / 0.5) : int(fim / 0.5) + 1] if energia else ()
            pico = float(np.percentile(janela, 90)) if len(janela) else 0.0
            achados = [t for t in termos if t in texto] if usar_termos else []
            quentes = len(achados)
            gancho = 1.0 if re.search(r"[?!]", segs[i]["texto"]) else 0.0
            excl = [t for t in excluir if t in texto]
            score = (w.get("pico_audio", 0) * pico + w.get("palavras_chave", 0) * min(quentes, lim)
                     + w.get("abertura_forte", 0) * gancho + w.get("densidade_fala", 0) * min(nw / dur / 3, 1))
            score += w.get("assunto_excluido", 0) * min(len(excl), 3)
            cands.append({"ini": ini, "fim": fim, "dur": round(dur, 1), "score": round(score, 3),
                          "quentes": quentes, "texto": texto[:160], "_i": i, "_j": j,
                          "_s": {"pico": pico, "achados": achados, "gancho": gancho, "wps": nw / dur, "excl": excl}})

    cands.sort(key=lambda c: c["score"], reverse=True)
    escolhidos: list[dict] = []
    for c in cands:  # sem sobreposição
        if all(c["fim"] <= e["ini"] or c["ini"] >= e["fim"] for e in escolhidos):
            escolhidos.append(c)
        if len(escolhidos) == quantos:
            break
    escolhidos.sort(key=lambda c: c["ini"])
    ctx = perfil["contexto"]
    for n, c in enumerate(escolhidos, 1):
        c["id"] = n
        sx = c.pop("_s")
        i, j = c.pop("_i"), c.pop("_j")
        if ctx["antes"] or ctx["depois"]:
            c["ini_sugerido"], c["fim_sugerido"] = c["ini"], c["fim"]
            c["ini"], c["fim"] = _contexto(segs, i, j, ctx["antes"], ctx["depois"])
            c["dur"] = round(c["fim"] - c["ini"], 1)
        c["sinais"] = {"pico_audio": round(sx["pico"], 2), "palavras_chave": sx["achados"][:8],
                       "abertura_forte": bool(sx["gancho"]), "densidade_fala": round(sx["wps"], 2),
                       "assunto_excluido": sx["excl"]}
        c["criterios"], c["motivo"] = _motivo(sx, w)
        c["status"] = "sugerido"
        c["perfil"] = {"id": perfil["id"], "versao": perfil["versao"]}
    _gravar(alvo, escolhidos)
    E.marcar(d, "momentos", "concluido", f"{len(escolhidos)} sugestões pelo perfil {perfil['nome']} (revisar)")
    E.marcar(d, "comentario", "pendente", "aguarda Zidane: gancho e fecho próprios em momentos.json")
    print(f"[momentos] {len(escolhidos)} candidatos (revise momentos.json).")
    return escolhidos


def _motivo(sx: dict, w: dict) -> tuple[list[str], str]:
    """Critérios atendidos, em texto, a partir dos sinais medidos (sem prometer viralização)."""
    crit = []
    if w.get("pico_audio", 0) > 0 and sx["pico"] >= 1.0:
        crit.append(f"pico de áudio acima da média ({sx['pico']:.1f} desvios)")
    if w.get("palavras_chave", 0) > 0 and sx["achados"]:
        crit.append("termos do perfil: " + ", ".join(sx["achados"][:5]))
    if w.get("abertura_forte", 0) > 0 and sx["gancho"]:
        crit.append("abre com pergunta ou exclamação")
    if w.get("densidade_fala", 0) > 0 and sx["wps"] >= 2.4:
        crit.append(f"fala contínua ({sx['wps']:.1f} palavras/s)")
    if sx["excl"]:
        crit.append("ATENÇÃO, contém assunto a excluir: " + ", ".join(sx["excl"]))
    motivo = "; ".join(crit[:3]) if crit else "melhor combinação disponível dos sinais medidos, sem destaque forte"
    return crit, motivo[:1].upper() + motivo[1:]


STATUS_MOMENTO = ("sugerido", "aceito", "rejeitado")


def decidir(d: Path, id_: int, status: str | None = None, ini: float | None = None,
            fim: float | None = None) -> dict:
    """Aceita/rejeita uma sugestão e/ou ajusta seus limites (em segundos do vídeo original).
    Não refaz transcrição nem análise: só atualiza momentos.json."""
    mom = _ler(d / "momentos.json")
    m = next((x for x in mom if x["id"] == id_), None)
    if m is None:
        raise ValueError(f"sugestão {id_} não existe")
    if status is not None:
        if status not in STATUS_MOMENTO:
            raise ValueError("status deve ser sugerido, aceito ou rejeitado")
        m["status"] = status
    if ini is not None or fim is not None:
        ini = float(m["ini"] if ini is None else ini)
        fim = float(m["fim"] if fim is None else fim)
        if ini < 0 or not 3 <= fim - ini <= 180:
            raise ValueError("intervalo inválido: de 3 a 180 s, começando em 0 ou depois")
        for k in ("ini", "fim"):
            m.setdefault(f"{k}_original", m[k])
        tr = _ler(d / "transcricao.json")
        texto = " ".join(w["t"] for s_ in tr["segmentos"] for w in s_["palavras"] if ini <= w["ini"] < fim)
        m.update(ini=round(ini, 2), fim=round(fim, 2), dur=round(fim - ini, 1), ajustado=True,
                 texto=(texto or m.get("texto", ""))[:160].lower())
        if (d / "perfil.json").exists():  # ajuste manual passa pelos mesmos critérios de integridade
            from . import editorial as ED
            rv = ED.revalidar(tr["segmentos"], ini, fim, PF.do_projeto(d), tr.get("idioma"))
            m["problemas"], m["correcoes"] = rv["problemas"], rv["correcoes"]
            m["sugestao_limites"] = {"ini": rv["ini"], "fim": rv["fim"]}  # o ajuste do usuário vale; isto só avisa
    m["decidido_em"] = time.time()
    _gravar(d / "momentos.json", mom)
    return m


CAMPOS_TEXTO = {"gancho": 120, "fecho": 200, "cta": 120}


def editar_texto(d: Path, id_: int, campos: dict) -> dict:
    """O Guilherme reescreve o texto do Zidane (gancho, fecho, cta). O que ele escreve vale como está."""
    mom = _ler(d / "momentos.json")
    m = next((x for x in mom if x["id"] == id_), None)
    if m is None:
        raise ValueError(f"sugestão {id_} não existe")
    for k, v in campos.items():
        if k not in CAMPOS_TEXTO:
            raise ValueError(f"campo desconhecido: {k}")
        v = " ".join(str(v or "").split())
        if k == "gancho" and not v:
            raise ValueError("O gancho não pode ficar vazio.")
        if len(v) > CAMPOS_TEXTO[k]:
            raise ValueError(f"{k}: no máximo {CAMPOS_TEXTO[k]} caracteres.")
        if "{" in v or "}" in v or "\\" in v:
            raise ValueError(f"{k}: não use chaves nem barra invertida.")
        if k == "cta" and not v:
            m.pop("cta", None)
        else:
            m[k] = v
    m["texto_editado"] = True
    m.pop("texto_aprovado", None)
    _gravar(d / "momentos.json", mom)
    return m


def aprovar_texto(d: Path) -> int:
    """Marca como aprovado o texto de todos os cortes que vão ser feitos. Devolve quantos."""
    from . import etapas as T
    mom = _ler(d / "momentos.json")
    alvos = set(alvos_corte(d, T.ativa(d, "revisao")))
    for m in mom:
        if m["id"] in alvos:
            if not m.get("gancho"):
                raise ValueError(f"O corte {m['id']} está sem gancho.")
            m["texto_aprovado"] = True
    _gravar(d / "momentos.json", mom)
    return len(alvos)


def limpar_aprovacao_texto(d: Path) -> None:
    """Texto novo do Zidane precisa de aprovação nova."""
    p = d / "momentos.json"
    mom = _ler(p)
    for m in mom:
        m.pop("texto_aprovado", None)
        m.pop("texto_editado", None)
    _gravar(p, mom)


def alvos_corte(d: Path, so_aceitos: bool) -> list[int]:
    """Ids que viram corte: só os aceitos (revisão ativa) ou todos os não rejeitados."""
    mom = _ler(d / "momentos.json")
    if so_aceitos:
        return [m["id"] for m in mom if m.get("status") == "aceito"]
    return [m["id"] for m in mom if m.get("status") != "rejeitado"]


# ------------------------------------------------------------------------ corte
def _ass_t(t: float) -> str:
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _ass(palavras: list[dict], trechos: list[tuple[float, float]], gancho: str, credito: str,
         fecho: str = "", legenda: bool = True, parte: str = "", cta: str = "") -> str:
    """`trechos` = [(início na fonte, duração)], na ordem em que aparecem no corte (gancho primeiro, se houver)."""
    dur = sum(t[1] for t in trechos)
    ini = 0.0
    cab = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
        "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,"
        "Bold,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\n"
        "Style: Leg,Arial,78,&H00FFFFFF,&H00000000,&H00000000,1,6,2,2,60,60,420\n"
        "Style: Gan,Arial,70,&H0000D7FF,&H00000000,&H00000000,1,6,2,8,60,60,230\n"
        "Style: Cre,Arial,40,&H00FFFFFF,&H00000000,&H00000000,0,3,1,2,40,40,90\n"
        "Style: Par,Arial,46,&H0000D7FF,&H00000000,&H00000000,1,5,1,8,60,60,110\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    linhas = [f"Dialogue: 0,{_ass_t(0)},{_ass_t(min(3.0, dur))},Gan,,0,0,0,,{gancho}",
              f"Dialogue: 0,{_ass_t(0)},{_ass_t(dur)},Cre,,0,0,0,,{credito}"]
    if parte:  # série: "PARTE X/N" o tempo todo
        linhas.append(f"Dialogue: 0,{_ass_t(0)},{_ass_t(dur)},Par,,0,0,0,,{parte}")
    if cta:  # série: CTA no final (substitui o fecho)
        linhas.append(f"Dialogue: 0,{_ass_t(max(0, dur - 3.5))},{_ass_t(dur)},Gan,,0,0,0,,{cta}")
    elif fecho:
        linhas.append(f"Dialogue: 0,{_ass_t(max(0, dur - 3.0))},{_ass_t(dur)},Gan,,0,0,0,,{fecho}")
    pals, off = [], 0.0
    for ti, td in (trechos if legenda else []):
        for w in palavras:
            if ti <= w["ini"] < ti + td:
                pals.append({"t": w["t"], "ini": w["ini"] - ti + off, "fim": min(w["fim"], ti + td) - ti + off})
        off += td
    for k in range(0, len(pals), 3):
        g = pals[k : k + 3]
        t0 = g[0]["ini"]
        t1 = min(g[-1]["fim"] + 0.15, dur)
        prox = pals[k + 3]["ini"] if k + 3 < len(pals) else dur
        t1 = max(t0 + 0.2, min(t1, prox))  # nunca sobrepõe o próximo grupo
        txt = " ".join(w["t"] for w in g).upper().replace("{", "").replace("}", "")
        linhas.append(f"Dialogue: 0,{_ass_t(t0)},{_ass_t(t1)},Leg,,0,0,0,,{txt}")
    return cab + "\n".join(linhas) + "\n"


CAM_PADRAO = "1320:0:600:340"  # câmera no canto superior direito de um vídeo 1920x1080 (x:y:w:h)


def _filtro(layout: str, n: str, cam: str, ent: str = "[0:v]") -> str:
    """Filtro de vídeo do corte. 'borrado' = original pequeno no centro; 'zoom' = câmera em
    cima e jogo ampliado embaixo (sem a câmera dentro do jogo), sobre fundo borrado;
    'preencher' = recorte central que ocupa a tela toda; 'ajustar' = original inteiro sobre fundo preto."""
    if layout == "preencher":
        return f"{ent}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,ass={n}.ass,format=yuv420p[v]"
    if layout == "ajustar":
        return (f"{ent}scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
                f"setsar=1,fps=30,ass={n}.ass,format=yuv420p[v]")
    bg = (f"{ent}split=2[a][b];"
          "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];")
    fim = f",fps=30,ass={n}.ass,format=yuv420p[v]"
    if layout == "zoom" and cam != "nenhuma":
        x, y, w, h = (int(v) for v in cam.split(":"))
        return (f"{ent}split=3[a][b][c];"
                "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];"
                f"[b]crop={x}:1080:0:0,scale=1080:-2[jogo];"
                f"[c]crop={w}:{h}:{x}:{y},scale=810:-2[cam];"
                "[bg][jogo]overlay=0:(H-h)/2+170[t1];"
                f"[t1][cam]overlay=(W-w)/2:330{fim}")
    if layout == "zoom":  # sem câmera: recorte central 4:3 ampliado
        return (bg + "[b]crop=1440:1080:240:0,scale=1080:-2[fg];"
                f"[bg][fg]overlay=0:(H-h)/2{fim}")
    return (bg + "[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2{fim}")


LAYOUTS = ("borrado", "zoom", "preencher", "ajustar")


def cortar(d: Path, ids: list[int] | None = None, gancho: str | None = None,
           layout: str | None = None, cam: str = CAM_PADRAO, legenda: bool = True,
           audio: bool = True) -> list[Path]:
    """`layout` None = o preset do perfil do projeto (GTA 6 v1: borrado, como na V1)."""
    layout = layout or PF.do_projeto(d)["preset_edicao"]
    fonte = _ler(d / "fonte.json")
    tr = _ler(d / "transcricao.json")
    palavras = [w for s in tr["segmentos"] for w in s["palavras"]]
    mom = _ler(d / "momentos.json")
    (d / "clipes").mkdir(exist_ok=True)
    E.marcar(d, "corte", "trabalhando", "ffmpeg: 9:16, legenda e crédito")
    saidas = []
    alvos = [m for m in mom if not ids or m["id"] in ids]
    for k, m in enumerate(alvos):
        E.marcar(d, "corte", "trabalhando", f"ffmpeg: corte {m['id']:02d} ({k + 1} de {len(alvos)})",
                 progresso=k / len(alvos))
        n = f"{m['id']:02d}"
        ini, dur = m["ini"], m["fim"] - m["ini"]
        gt = m.get("gancho_trecho")  # {"ini","fim"}: frase forte que abre o corte (teaser) antes do corte inteiro
        trechos = ([(gt["ini"], gt["fim"] - gt["ini"])] if gt else []) + [(ini, dur)]
        dur_total = sum(t[1] for t in trechos)
        propria = bool(gancho or m.get("gancho"))  # comentário próprio escrito pelo Zidane
        g = gancho or m.get("gancho") or " ".join(m["texto"].split()[:7]).upper()
        g = re.sub(r"[{}\\]", "", g)
        fecho = re.sub(r"[{}\\]", "", m.get("fecho", ""))
        cred = f"Vídeo: {fonte['autor']}"
        ass = d / "clipes" / f"{n}.ass"
        serie = m.get("serie")  # parte de um assunto longo: marca "PARTE X/N" e CTA no final
        parte_txt, cta = "", ""
        if serie:
            from . import editorial as ED
            parte_txt = f"PARTE {serie['parte']}/{serie['de']}"
            cta = re.sub(r"[{}\\]", "", m.get("cta") or ED.cta_padrao(serie["parte"], serie["de"], PF.do_projeto(d).get("idioma")))
        ass.write_text(_ass(palavras, trechos, g, cred, fecho, legenda, parte_txt, cta), encoding="utf-8")
        out = d / "clipes" / f"{n}.mp4"
        # fundo borrado + original centralizado (transformação visual) + legenda/gancho/crédito
        fonte_mp4 = str((d / "fonte.mp4").resolve())
        entradas, pre = [], ""
        for ti, td in trechos:
            entradas += ["-ss", f"{ti:.2f}", "-t", f"{td:.2f}", "-i", fonte_mp4]
        if len(trechos) >= 2:  # montagem (chamada + corte, ou lista ordenada de trechos): junta antes do layout
            nt = len(trechos)
            vs = "".join(f"[{k}:v]setpts=PTS-STARTPTS[v{k}];" for k in range(nt))
            if audio:
                as_ = "".join(f"[{k}:a]asetpts=PTS-STARTPTS[a{k}];" for k in range(nt))
                lig = "".join(f"[v{k}][a{k}]" for k in range(nt))
                pre = vs + as_ + lig + f"concat=n={nt}:v=1:a=1[vc][ac];"
            else:
                pre = vs + "".join(f"[v{k}]" for k in range(nt)) + f"concat=n={nt}:v=1:a=0[vc];"
            fc, audio_map = pre + _filtro(layout, n, cam, "[vc]"), "[ac]"
        else:
            fc, audio_map = _filtro(layout, n, cam), "0:a:0?"
        _run(["ffmpeg", "-y", *entradas, "-filter_complex", fc, "-map", "[v]",
              *(["-map", audio_map] if audio else ["-an"]),
              "-c:v", "libx264", "-crf", "18", "-preset", "medium",
              *(["-c:a", "aac", "-b:a", "160k"] if audio else []),
              str(out.resolve())], cwd=str(d / "clipes"))
        _gravar(d / "clipes" / f"{n}.json", {
            "arquivo": out.name, "ini": ini, "fim": round(m["fim"], 2), "dur": round(dur_total, 1), "gancho": g, "fecho": fecho,
            "gancho_trecho": gt, "serie": serie, "cta": cta, "layout": layout, "legenda": legenda, "audio": audio,
            "comentario_proprio": propria,
            "autor_credito": fonte["autor"], "origem": fonte["origem"],
            "autorizacao": fonte["autorizacao"],
            "descricao": (f"Trecho do vídeo original de {fonte['autor']}"
                          f"{' — ' + fonte['titulo_original'] if fonte['titulo_original'] else ''}.\n"
                          f"Original: {fonte['origem']}\nTodos os créditos ao criador."),
        })
        verif = verificar_clipe(out, dur_total, audio, trechos, palavras, legenda)
        j = _ler(d / "clipes" / f"{n}.json")
        j["verificacao"] = verif
        j["trechos_origem"] = [{"ini": round(a, 2), "fim": round(a + b, 2)} for a, b in trechos]
        _gravar(d / "clipes" / f"{n}.json", j)
        if not verif["ok"]:
            raise RuntimeError(f"corte {n} reprovado na verificação do arquivo: " + "; ".join(verif["problemas"]))
        saidas.append(out)
        print(f"[cortar] {out}")
    n_prop = sum(1 for j in (d / "clipes").glob("[0-9][0-9].json") if _ler(j).get("comentario_proprio"))
    E.marcar(d, "corte", "concluido", f"{len(saidas)} corte(s) gerado(s)")
    if saidas and n_prop >= len(saidas):
        E.marcar(d, "comentario", "concluido", "comentário próprio presente em todos os cortes")
    return saidas


def verificar_clipe(mp4: Path, dur_esperada: float, audio: bool, trechos: list[tuple[float, float]],
                    palavras: list[dict], legenda: bool) -> dict:
    """Confere o ARQUIVO renderizado (não a proposta): resolução, duração, áudio com som e legenda coerente."""
    import json as _j
    probs: list[str] = []
    info = _j.loads(_run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,duration",
                          "-show_entries", "format=duration", "-of", "json", str(mp4)]).stdout)
    v = next((x for x in info["streams"] if x["codec_type"] == "video"), None)
    a = next((x for x in info["streams"] if x["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    if not v or (int(v["width"]), int(v["height"])) != (1080, 1920):
        probs.append("vídeo ausente ou fora de 1080x1920")
    if abs(dur - dur_esperada) > 0.35:
        probs.append(f"duração {dur:.2f}s difere dos segmentos aprovados ({dur_esperada:.2f}s)")
    if audio and not a:
        probs.append("sem faixa de áudio")
    if audio and a:
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(mp4), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        mm = re.search(r"mean_volume: (-?[\d.]+|-inf) dB", r.stderr)
        if mm and (mm.group(1) == "-inf" or float(mm.group(1)) < -60):
            probs.append("áudio mudo")
    n_pal = sum(1 for ti, td in trechos for w in palavras if ti <= w["ini"] < ti + td)
    if legenda and n_pal == 0:
        probs.append("sem palavras para legendar nos trechos")
    return {"ok": not probs, "duracao_real": round(dur, 2), "duracao_esperada": round(dur_esperada, 2),
            "palavras_legendadas": n_pal, "problemas": probs}


def reeditar(d: Path, id_: int, ini: float, fim: float, layout: str = "borrado",
             legenda: bool = True, audio: bool = True) -> None:
    """Refaz UM corte com novo intervalo (e legenda, enquadramento e áudio). Mantém a versão anterior em
    NN.anterior.mp4/.json e a restaura se o ffmpeg falhar. A nota do Totti passa a constar como desatualizada."""
    mom = _ler(d / "momentos.json")
    m = next((x for x in mom if x["id"] == id_), None)
    if m is None:
        raise SystemExit(f"momento {id_} não existe em momentos.json")
    if not (3 <= fim - ini <= 90) or ini < 0:
        raise SystemExit("intervalo inválido: use de 3 a 90 s, começando em 0 ou depois")
    n = f"{id_:02d}"
    cl = d / "clipes"
    bak = d / "momentos.pre-ajuste.json"
    if not bak.exists():
        shutil.copy2(d / "momentos.json", bak)
    for ext in ("mp4", "json"):
        if (cl / f"{n}.{ext}").exists():
            shutil.copy2(cl / f"{n}.{ext}", cl / f"{n}.anterior.{ext}")
    tr = _ler(d / "transcricao.json")
    texto = " ".join(w["t"] for s_ in tr["segmentos"] for w in s_["palavras"] if ini <= w["ini"] < fim)
    m.update(ini=round(ini, 2), fim=round(fim, 2), dur=round(fim - ini, 1), texto=texto or m.get("texto", ""),
             ajustado=True)
    _gravar(d / "momentos.json", mom)
    E.marcar(d, "corte", "trabalhando", f"refazendo o corte {n} com o intervalo ajustado", "Código")
    try:
        cortar(d, [id_], None, layout, CAM_PADRAO, legenda, audio)
    except BaseException as e:  # noqa: BLE001 - restaura e mostra no painel
        for ext in ("mp4", "json"):
            if (cl / f"{n}.anterior.{ext}").exists():
                shutil.copy2(cl / f"{n}.anterior.{ext}", cl / f"{n}.{ext}")
        txt = str(getattr(e, "stderr", "") or e)
        E.marcar(d, "corte", "falhou", f"não foi possível refazer o corte {n}", "Código", [txt[-400:]],
                 "A versão anterior do corte foi restaurada. Confira o intervalo e tente de novo.")
        raise
    j = _ler(cl / f"{n}.json")
    j["ajuste"] = {"ini": round(ini, 2), "fim": round(fim, 2), "layout": layout, "legenda": legenda,
                   "audio": audio, "em": time.time()}
    _gravar(cl / f"{n}.json", j)
    pot = cl / f"{n}.potencial.json"
    if pot.exists():
        pj = _ler(pot)
        pj["desatualizado"] = True
        _gravar(pot, pj)
    total = len(list(cl.glob("[0-9][0-9].mp4")))
    E.marcar(d, "corte", "concluido", f"{total} corte(s) pronto(s); corte {n} refeito com o intervalo ajustado", "Código")


# ------------------------------------------------------------------------ check
def check(d: Path) -> bool:
    """Gate de publicação. Falha sem autorização válida, crédito e tamanho de Short."""
    problemas: list[str] = []
    E.marcar(d, "originalidade", "trabalhando", "conferindo autorização, comentário e crédito")
    fonte = _ler(d / "fonte.json")
    aut = fonte.get("autorizacao", {})
    if aut.get("tipo") not in AUTORIZACOES - {"teste"}:
        problemas.append(f"Autorização {aut.get('tipo')!r} não permite publicar (tipo 'teste' é só prova técnica).")
    if aut.get("tipo") not in ("proprio", "teste", "livre") and not aut.get("prova"):
        problemas.append("Falta a prova da permissão (link, print ou e-mail).")
    sem_comentario, sem_credito = [], []
    for j in sorted((d / "clipes").glob("[0-9][0-9].json")):
        c = _ler(j)
        if not (15 <= c["dur"] <= 60):
            print(f"[check] {j.stem}: duração {c['dur']}s fora de 15-60s (aviso).")
        if not c.get("autor_credito"):
            sem_credito.append(j.stem)
        if not c.get("comentario_proprio"):
            sem_comentario.append(j.stem)
    sem_cta = [j.stem for j in sorted((d / "clipes").glob("[0-9][0-9].json"))
               if _ler(j).get("serie") and not _ler(j).get("cta")]
    if sem_cta:
        problemas.append(f"Partes de série sem CTA nos cortes {', '.join(sem_cta)}: o espectador precisa saber que há mais partes.")
    if sem_credito:
        problemas.append(f"Sem crédito ao criador nos cortes {', '.join(sem_credito)}.")
    if sem_comentario:
        problemas.append(f"Sem comentário próprio (gancho e fecho nossos) nos cortes {', '.join(sem_comentario)}: "
                         "o Instagram e o TikTok rebaixam repost sem nada novo.")
    for p in problemas:
        print(f"[check] REPROVADO: {p}")
    ok = not problemas
    if ok:
        E.marcar(d, "originalidade", "concluido", "autorização, crédito e comentário próprio ok")
    else:
        E.marcar(d, "originalidade", "bloqueado", f"{len(problemas)} problema(s) impedem de publicar", None, problemas,
                 "Peça ao Zidane o gancho e o fecho de cada corte (campos gancho e fecho em momentos.json) e rode "
                 "`python -m clipes cortar <slug>` de novo; para autorização, use --autorizacao livre ou informe --prova.")
    print("[check] APROVADO" if ok else "[check] BLOQUEADO")
    return ok


# --------------------------------------------------------------------- embalagem
def embalar(d: Path) -> list[Path]:
    """Texto de postagem por plataforma. Instagram: 3-5 tags, Reels curto. TikTok: até 5 tags."""
    fonte = _ler(d / "fonte.json")
    tags = fonte.get("hashtags") or PF.do_projeto(d)["hashtags"]
    (d / "publicar").mkdir(exist_ok=True)
    E.marcar(d, "embalagem", "trabalhando", "texto por plataforma")
    saidas = []
    for j in sorted((d / "clipes").glob("[0-9][0-9].json")):
        c = _ler(j)
        sr = c.get("serie")
        corpo = (f"Parte {sr['parte']}/{sr['de']}: " if sr else "") + f"{c['gancho'].capitalize()}\n\n{c['descricao']}"
        for plat, n_tags, dica in (("instagram", 5, "Reels rende melhor entre 15 e 45 s."),
                                   ("tiktok", 5, "TikTok aceita corte mais cru e direto.")):
            alvo = d / "publicar" / f"{j.stem}_{plat}.txt"
            texto = f"{corpo}\n\n{' '.join(tags[:n_tags])}\n\n[dica: {dica} Duração: {c['dur']} s]\n"
            alvo.write_text(texto, encoding="utf-8")
            saidas.append(alvo)
    E.marcar(d, "embalagem", "concluido", f"{len(saidas)} textos em publicar/")
    E.marcar(d, "aprovacao", "espera_voce", "revisar os cortes e postar à mão no Instagram e TikTok")
    return saidas
