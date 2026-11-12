"""Ações diretas de revisão: editar fala e direção, substituir asset, escolher tomada. Sempre nos arquivos do contrato (CLAUDE.md):
a mudança vira versão nova pelo mesmo caminho de um agente ou do terminal, e o resto do fluxo reage como sempre."""
import io
import json
import re
import wave

from . import fluxo, grafos, materiais as M
from .banco import agora, evento, faz, um, varios
from .fluxo import Recusado

SECAO_DIRECAO = "## Direção por cena (Guilherme)"


def _exige_parado(ctx, material):
    if any(j["status"] in fluxo.ATIVOS and material in json.loads(j["spec"]).get("materiais", []) for j in ctx.jobs):
        raise Recusado("Um agente está trabalhando neste material agora: espere terminar para editar.")


def _gravar(p, texto):
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    tmp.replace(p)


def _numero(slug, material):
    v = fluxo.ultima_versao(slug, material)
    return v["numero"] if v else 0


def _fechar_edicao(slug, material, antes, resolve_no=False):
    """Sincroniza a edição direta: a versão nova nasce marcada como feita pelo usuário (origem "usuario"). A auditoria de texto fica
    desatualizada sozinha (as dependências dela mudaram de hash). Nenhum agente é reaberto nem iniciado; um nó de agente que
    tinha falhado em produzir este material passa a valer pelo que o Guilherme gravou."""
    fluxo.sincronizar(slug, forcar=True, assentar=False)
    v = fluxo.ultima_versao(slug, material)
    if v and v["numero"] > antes:
        faz("UPDATE versoes SET origem='usuario' WHERE id=?", v["id"])
    if resolve_no:
        grafos.ao_editar_manual(slug, material)


def editar_cena(slug, i, campo, valor):
    """`fala` muda o cenas.json: a narração daquela cena fica desatualizada e só ela é refeita. `direcao` entra no direcao_viral.md, que o Olise lê antes de desenhar."""
    fluxo.sincronizar(slug, forcar=True)
    ctx = fluxo.Contexto(slug)
    valor = str(valor or "").strip()
    material = "cenas" if campo == "fala" else "roteiro"
    antes = _numero(slug, material)
    if campo == "fala":
        if not valor:
            raise Recusado("A fala não pode ficar vazia: toda cena tem narração.", 400)
        _exige_parado(ctx, "cenas")
        f = M.arquivo_cenas(slug)
        cenas = M.ler_cenas(slug)
        if not f or not 0 <= i < len(cenas):
            raise Recusado("Cena não encontrada.", 404)
        cenas[i]["fala"] = valor
        _gravar(f, json.dumps(cenas, ensure_ascii=False, indent=1))
        evento(slug, f"Fala da cena {i + 1} editada")
    elif campo == "direcao":
        _exige_parado(ctx, "roteiro")
        p = M.pasta(slug) / "direcao_viral.md"
        texto = M.ler_texto(p)
        atuais = direcoes_manuais(slug)
        atuais[i] = valor
        corpo = SECAO_DIRECAO + "\n" + "\n".join(f"- Cena {k + 1}: {v}" for k, v in sorted(atuais.items()) if v) + "\n"
        if SECAO_DIRECAO in texto:
            texto = re.sub(re.escape(SECAO_DIRECAO) + r"\n(?:- [^\n]*\n?)*", lambda _: corpo, texto)
        else:
            texto = texto.rstrip() + "\n\n" + corpo
        _gravar(p, texto)
        evento(slug, f"Direção visual da cena {i + 1} editada")
    else:
        raise Recusado("Campo inválido.", 400)
    _fechar_edicao(slug, material, antes, resolve_no=True)
    return {"ok": True}


def direcoes_manuais(slug):
    m = re.search(re.escape(SECAO_DIRECAO) + r"\n((?:- [^\n]*\n?)*)", M.ler_texto(M.pasta(slug) / "direcao_viral.md"))
    saida = {}
    for linha in (m.group(1) if m else "").splitlines():
        x = re.match(r"- Cena (\d+): (.*)", linha)
        if x:
            saida[int(x.group(1)) - 1] = x.group(2)
    return saida


def editar_roteiro(slug, texto):
    texto = str(texto or "").strip()
    if not texto:
        raise Recusado("O roteiro não pode ficar vazio.", 400)
    ctx = fluxo.Contexto(slug)
    _exige_parado(ctx, "roteiro")
    antes = _numero(slug, "roteiro")
    _gravar(M.pasta(slug) / "roteiro.txt", texto + "\n")
    evento(slug, "Roteiro editado à mão")
    _fechar_edicao(slug, "roteiro", antes, resolve_no=True)
    return {"ok": True}


LIMITES_METADADOS = {"titulo": 100, "descricao": 5000, "tags": 500, "thumbnail_texto": 60}


def editar_metadados(slug, campos):
    """Edição direta do metadados.json (titulo, descricao, tags, thumbnail_texto). Só grava os campos enviados e preserva os demais."""
    if not isinstance(campos, dict):
        raise Recusado("Envie os campos a editar.", 400)
    novos = {}
    if campos.get("titulo") is not None:
        t = " ".join(str(campos["titulo"]).split())
        if not t:
            raise Recusado("O título não pode ficar vazio.", 400)
        if len(t) > LIMITES_METADADOS["titulo"]:
            raise Recusado(f"O título tem {len(t)} caracteres: o máximo é {LIMITES_METADADOS['titulo']}.", 400)
        novos["titulo"] = t
    if campos.get("descricao") is not None:
        d = str(campos["descricao"]).strip()
        if len(d) > LIMITES_METADADOS["descricao"]:
            raise Recusado(f"A descrição tem {len(d)} caracteres: o máximo é {LIMITES_METADADOS['descricao']}.", 400)
        novos["descricao"] = d
    if campos.get("tags") is not None:
        bruto = campos["tags"]
        if isinstance(bruto, str):
            bruto = bruto.split(",")
        if not isinstance(bruto, (list, tuple)):
            raise Recusado("As tags devem ser uma lista ou um texto separado por vírgula.", 400)
        tags = list(dict.fromkeys(" ".join(str(x).split()) for x in bruto if str(x).strip()))
        total = len(",".join(tags))
        if total > LIMITES_METADADOS["tags"]:
            raise Recusado(f"As tags somam {total} caracteres: o máximo é {LIMITES_METADADOS['tags']}.", 400)
        novos["tags"] = tags
    if campos.get("thumbnail_texto") is not None:
        x = " ".join(str(campos["thumbnail_texto"]).split())
        if len(x) > LIMITES_METADADOS["thumbnail_texto"]:
            raise Recusado(f"O texto da thumbnail tem {len(x)} caracteres: o máximo é {LIMITES_METADADOS['thumbnail_texto']}.", 400)
        novos["thumbnail_texto"] = x
    if not novos:
        raise Recusado("Nenhum campo para editar.", 400)
    fluxo.sincronizar(slug, forcar=True)
    ctx = fluxo.Contexto(slug)
    _exige_parado(ctx, "metadados")
    p = M.pasta(slug) / "metadados.json"
    atual = M.ler_json(p, None)
    if not isinstance(atual, dict):
        raise Recusado("Os metadados ainda não existem neste projeto.", 404)
    antes = _numero(slug, "metadados")
    _gravar(p, json.dumps({**atual, **novos}, ensure_ascii=False, indent=2) + "\n")
    evento(slug, f"Metadados editados à mão ({', '.join(novos)})")
    _fechar_edicao(slug, "metadados", antes, resolve_no=True)
    return {"ok": True, "campos": list(novos), "metadados": {**atual, **novos}}


def _imagem_valida(corpo):
    from PIL import Image
    if len(corpo) > 30 << 20:
        raise Recusado("Imagem grande demais (máximo 30 MB).", 400)
    try:
        Image.open(io.BytesIO(corpo)).verify()
        return Image.open(io.BytesIO(corpo))
    except Exception:
        raise Recusado("O arquivo não é uma imagem válida.", 400)


def substituir_componente(slug, item, corpo):
    """Troca a imagem de um componente mantendo o nome. A decisão é por conteúdo: os demais continuam aprovados e só este volta para revisão."""
    fluxo.sincronizar(slug, forcar=True)
    _exige_parado(fluxo.Contexto(slug), "componentes")
    im = _imagem_valida(corpo)
    alvo = next((f for f in M.imagens_componentes(slug) if f.stem == item), None)
    if not alvo:
        raise Recusado(f"Componente não encontrado: {item}.", 404)
    buf = io.BytesIO()
    im.convert("RGBA" if alvo.suffix.lower() == ".png" else "RGB").save(buf, "PNG" if alvo.suffix.lower() == ".png" else "JPEG", quality=92)
    tmp = alvo.with_suffix(alvo.suffix + ".tmp")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(alvo)
    evento(slug, f"Componente substituído: {item}")
    fluxo.sincronizar(slug, forcar=True, assentar=False)
    return {"ok": True}


def thumbnail(slug):
    f = M.pasta(slug) / "thumbnail.jpg"
    if not f.exists():
        return None
    sha = M.sha_arquivo(f)
    M.guardar_blob(f, sha)
    d = um("SELECT decisao FROM itens WHERE slug=? AND material='thumbnail_img' AND sha=?", slug, sha)
    return {"sha": sha, "url": fluxo.blob_url(sha, "thumbnail.jpg"), "decisao": d["decisao"] if d else None}


def substituir_thumbnail(slug, corpo):
    t = thumbnail(slug)  # guarda a atual no depósito antes de trocar
    im = _imagem_valida(corpo)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=92)
    p = M.pasta(slug) / "thumbnail.jpg"
    tmp = p.with_suffix(".tmp")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(p)
    evento(slug, "Thumbnail substituída" + (" (a anterior continua guardada)" if t else ""))
    return thumbnail(slug)


def decidir_thumbnail(slug, decisao):
    t = thumbnail(slug)
    if not t:
        raise Recusado("Este projeto não tem thumbnail.jpg.", 404)
    if decisao == "aprovado":
        faz("INSERT INTO itens (slug, material, sha, decisao, criada_em) VALUES (?, 'thumbnail_img', ?, 'aprovado', ?) ON CONFLICT (slug, material, sha) DO UPDATE SET decisao='aprovado'", slug, t["sha"], agora())
    else:
        faz("DELETE FROM itens WHERE slug=? AND material='thumbnail_img' AND sha=?", slug, t["sha"])
    return thumbnail(slug)


def _dur_wav(p):
    try:
        with wave.open(str(p), "rb") as w:
            return round(w.getnframes() / w.getframerate(), 3)
    except (OSError, wave.Error):
        return None


def tomadas(slug, i):
    """As tomadas já gravadas desta fala, de todas as versões da narração. Nada é gerado aqui."""
    atual = M.falas(slug).get(i)
    vistas, saida = set(), []
    for v in fluxo.varios("SELECT id, numero, manifesto, criada_em FROM versoes WHERE slug=? AND material='narracao' ORDER BY numero DESC", slug):
        man = json.loads(v["manifesto"])
        sha = man["itens"].get(f"cena_{i}")
        if not sha or sha in vistas:
            continue
        vistas.add(sha)
        saida.append({"sha": sha, "versao": v["numero"], "criada_em": v["criada_em"], "url": fluxo.blob_url(sha, f"cena_{i}.wav"), "dur": _dur_wav(M.caminho_blob(sha)), "atual": bool(atual and atual["sha"] == sha)})
    return saida


def usar_tomada(slug, i, sha):
    """Volta uma tomada antiga. Vira versão nova da narração, e o editor mostra o conflito se o corte estiver usando outra."""
    if not any(t["sha"] == sha for t in tomadas(slug, i)):
        raise Recusado("Tomada não encontrada nesta fala.", 404)
    ctx = fluxo.Contexto(slug)
    _exige_parado(ctx, "narracao")
    pasta = M.pasta(slug) / "falas"
    tabela = M.ler_json(pasta / "falas.json", {}) or {}
    if str(i) not in tabela:
        raise Recusado("Esta fala não existe na narração atual.", 404)
    destino = pasta / f"{i:02d}.wav"
    tmp = destino.with_suffix(".tmp")
    tmp.write_bytes(M.caminho_blob(sha).read_bytes())
    tmp.replace(destino)
    tabela[str(i)] = {"wav": str(destino), "dur": _dur_wav(destino)}
    _gravar(pasta / "falas.json", json.dumps(tabela, ensure_ascii=False, indent=1))
    evento(slug, f"Tomada antiga recolocada na cena {i + 1}")
    fluxo.sincronizar(slug, forcar=True, assentar=False)
    return {"ok": True}


def _quando_mudou(slug, material):
    """Pasta de antes do estúdio não tem trabalho registrado: a data real é a do arquivo."""
    from datetime import datetime
    m = M.manifesto(slug, material)
    datas = [o.stat().st_mtime for o in (m[0].values() if m else ()) if not isinstance(o, (bytes, bytearray)) and o.exists()]
    return datetime.fromtimestamp(max(datas)).isoformat(timespec="seconds") if datas else None


STATUS_LEGADO = {"executando": "rodando", "fila": "rodando", "falhou": "falhou", "aguardando": "aguardando", "desatualizada": "aguardando", "bloqueio": "falhou", "aprovada": "concluido", "concluida": "concluido", "bloqueada": "pendente", "pronta": "aguardando_inicio", "nao_aplica": "ignorado"}


def vista_estudio(slug):
    """A tela do Estúdio: nada aqui é inventado. Sem job rodando, nenhum agente aparece como ativo."""
    from . import corte
    est = fluxo.estado(slug)
    ctx = fluxo.Contexto(slug)
    ex = grafos.visao_execucao(slug)
    if ex:
        linhas = [x for x in ex["linhas"] if x["tipo"] in ("agente", "render", "aprovacao")]
        decisoes = [{"no": x["no"], "nome": x["nome"], "material": x["material"], "status": x["status"], "status_texto": x["status_texto"], "versao": x["versao"], "nota": x["nota"], "exec": ex["id"]} for x in linhas if x["tipo"] == "aprovacao"]
    else:
        linhas = []
        for e in est["etapas"]:
            job = e["job"] or e["falha"]
            linhas.append({"no": e["id"], "nome": e["nome"], "tipo": "agente" if fluxo.POR_ID[e["id"]]["agente"] else "render", "funcao": fluxo.POR_ID[e["id"]]["faz"].capitalize(), "status": STATUS_LEGADO.get(e["status"], "pendente"), "status_texto": e["status_texto"], "nota": e["falha"]["erro"] if e["falha"] else (e["obsoleto"] or {}).get("motivo"), "atualizado_em": (job or {}).get("terminado_em") or (job or {}).get("iniciado_em") or _quando_mudou(slug, e["material"]), "job": job, "progresso": e["progresso"], "agente": fluxo.POR_ID[e["id"]]["agente"], "craque": e["craque"], "versao": {"numero": e["versao"]} if e["versao"] else None, "material": e["material"], "legado": True})
        decisoes = [{"no": e["id"], "nome": e["nome"], "material": e["material"], "status": STATUS_LEGADO.get(e["status"], "pendente"), "status_texto": e["status_texto"], "versao": {"id": e["versao_id"], "numero": e["versao"]} if e["versao"] else None, "nota": None, "exec": None, "acao": e["acoes"]["aprovar"]} for e in est["etapas"] if e["gate"]]
    video = ctx.versoes.get("video")
    versoes_video = varios("SELECT id, numero, manifesto, criada_em, origem FROM versoes WHERE slug=? AND material='video' ORDER BY numero DESC", slug)
    from .troca_estilo import versoes_validas
    corte_video = versoes_validas(slug, "video")
    versoes_video = [v for v in versoes_video if v["numero"] > corte_video]  # o vídeo do estilo anterior fica no histórico da revisão
    videos = [{"id": v["id"], "numero": v["numero"], "criada_em": v["criada_em"], "origem": v["origem"], "sha": json.loads(v["manifesto"])["arquivos"]["video.mp4"], "aprovada": v["id"] in ctx.aprovadas} for v in versoes_video]
    cenas, exato = fluxo._cenas_visao(ctx)
    manuais = direcoes_manuais(slug)
    for c in cenas:
        if c["i"] in manuais:
            c["direcao"] = manuais[c["i"]]
    if video:
        exp = corte.exportacao_do_video(slug, video["manifesto"]["arquivos"]["video.mp4"])
        if exp:
            segs = json.loads(exp["compilado"])["segmentos"]
            por_i = {c["i"]: c for c in cenas}
            cenas = [{**por_i.get(s["i"], {"direcao": "", "tela": []}), "i": s["i"], "fala": s["fala"] or por_i.get(s["i"], {}).get("fala", ""), "inicio": s["ini"], "dur": round(s["fim"] - s["ini"], 2)} for s in segs]
            exato = True
    return {"estado": est, "execucao": {k: ex[k] for k in ("id", "fluxo", "fluxo_numero", "fluxo_atual", "status", "criada_em")} if ex else None, "linhas": linhas, "decisoes": decisoes, "videos": videos, "cenas": cenas, "tempos_exatos": exato, "corte": corte.situacao(slug), "thumbnail": thumbnail(slug), "pasta": str(M.pasta(slug))}
