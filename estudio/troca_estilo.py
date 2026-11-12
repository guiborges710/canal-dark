"""Estilo do projeto: o que muda ao trocar e a troca em si.

Nada é apagado. O que pertence ao estilo antigo vai para output/<slug>/_troca_estilo/<data>/, as versões continuam no histórico, e o
projeto passa a ignorar as versões anteriores à troca (`producoes.estilo_corte`). A narração fica: se as falas não mudarem, o render a reaproveita.
"""
import json
import shutil
from datetime import datetime

from media import estilos

from . import fluxo, materiais as M
from .banco import evento, faz, um
from .fluxo import NOME_MATERIAL, Recusado

MOTIVOS = {
    "componentes": "Os componentes são desenhados para um estilo.",
    "cenas": "As cenas são compostas de outro jeito em cada estilo.",
    "auditoria_texto": "Os textos da tela mudam com as novas cenas, então a auditoria de texto precisa rodar de novo.",
    "video": "O vídeo precisa ser renderizado no novo estilo.",
    "auditoria_final": "A auditoria final vale para o vídeo que ela viu.",
    "thumbnail": "A thumbnail foi pensada para o visual antigo.",
}
MANTEM = {
    "pesquisa": "As notas não dependem do estilo.",
    "roteiro": "O texto continua valendo. O roteiro não é refeito; se quiser reescrever para o novo estilo, peça um ajuste.",
    "metadados": "Título, descrição e tags continuam valendo.",
    "narracao": "A narração é reaproveitada se as falas não mudarem. Se uma fala mudar nas novas cenas, só ela é narrada de novo.",
}
# Só a variação mudou: o desenho é o mesmo código, com outro papel e outro traço.
SO_VARIACAO = ("video", "auditoria_final")
ARQUIVOS = {
    "componentes": ["componentes", "componentes.md", "componentes_video.py"],
    "cenas": ["cenas.json", "sketch_cenas.py", "previa.jpg", "cenas_render.json", "corte.json", "corte_assets"],
    "auditoria_texto": ["auditoria_texto.md"],
    "video": ["video.mp4", "thumbnail.jpg", "audio.wav", "eventos.json", "PUBLICAR.txt", "CONFORMIDADE.md", "custo.json", "corte.json", "corte_assets"],
    "auditoria_final": ["auditoria.md"],
}


def escolha_atual(slug):
    ctx = fluxo.Contexto(slug)
    gravada = estilos.ler(ctx.pasta)
    if gravada and gravada["estilo"] == ctx.estilo:
        return gravada
    return {"estilo": ctx.estilo, "variante": None, "opcoes": {}}


def descrever(slug):
    e = escolha_atual(slug)
    return {**e, "nome": estilos.rotulo(e["estilo"], e)}


def impacto(slug, estilo, variante=None, opcoes=None):
    """O que precisará ser refeito se a troca for confirmada. `assinatura` prende a confirmação ao que foi mostrado."""
    fluxo.sincronizar(slug, forcar=True)
    ctx = fluxo.Contexto(slug)
    try:
        nova = estilos.validar_escolha(estilo, variante, opcoes, ctx.formato)
    except ValueError as ex:
        raise Recusado(str(ex), 400)
    atual = escolha_atual(slug)
    if (atual["estilo"], atual.get("variante"), atual.get("opcoes") or {}) == (nova["estilo"], nova["variante"], nova["opcoes"]):
        return {"nova": nova, "igual": True, "refazer": [], "mantem": [], "bloqueios": [], "assinatura": None}
    so_variacao = atual["estilo"] == nova["estilo"]
    candidatos = SO_VARIACAO if so_variacao else tuple(MOTIVOS)
    refazer = [{"etapa": m, "nome": NOME_MATERIAL[m], "versao": ctx.versoes[m]["numero"], "aprovada": ctx.versoes[m]["id"] in ctx.aprovadas, "motivo": MOTIVOS[m]} for m in candidatos if ctx.versoes.get(m)]
    mantem = [{"etapa": m, "nome": NOME_MATERIAL[m], "motivo": t} for m, t in MANTEM.items() if ctx.versoes.get(m)]
    if so_variacao and ctx.versoes.get("cenas"):
        mantem.append({"etapa": "cenas", "nome": NOME_MATERIAL["cenas"], "motivo": "O desenho é o mesmo código: só muda o papel e o traço."})
    bloqueios = []
    if (ctx.pasta / "upload.json").exists():
        bloqueios.append("Este vídeo já foi enviado ao YouTube. Crie um novo projeto para fazê-lo em outro estilo.")
    afetados = {x["etapa"] for x in refazer} | set(candidatos)
    for j in ctx.jobs:
        if j["status"] in fluxo.ATIVOS and afetados & set(json.loads(j["spec"]).get("materiais", [])):
            bloqueios.append(f"{j['titulo']} está em andamento: espere terminar ou cancele antes de trocar o estilo.")
    if nova["estilo"] not in estilos.ESTILOS:
        bloqueios.append("Estilo inválido.")
    if (ctx.pasta / "corte.json").exists():
        refazer.append({"etapa": "corte", "nome": "o corte editado", "versao": None, "aprovada": False, "motivo": "As edições apontam para as cenas antigas. O corte fica guardado junto com elas e o editor recomeça do novo vídeo."})
    assinatura = M.sha_texto(json.dumps([nova, [(x["etapa"], x["versao"]) for x in refazer]], sort_keys=True))
    return {"nova": nova, "nome": estilos.rotulo(nova["estilo"], nova), "atual": estilos.rotulo(atual["estilo"], atual), "igual": False, "refazer": refazer, "mantem": mantem, "bloqueios": bloqueios, "assinatura": assinatura}


def trocar(slug, estilo, variante=None, opcoes=None, confirmar=None):
    """Sem nada produzido, troca direto. Com produção, só aceita a confirmação do impacto que acabou de ser mostrado."""
    im = impacto(slug, estilo, variante, opcoes)
    if im["igual"]:
        return {"trocado": False, "estilo": descrever(slug)}
    if im["bloqueios"]:
        raise Recusado(im["bloqueios"])
    if im["refazer"] and confirmar != im["assinatura"]:
        return {"trocado": False, "precisa_confirmar": True, "impacto": im}
    ctx = fluxo.Contexto(slug)
    materiais = [x["etapa"] for x in im["refazer"] if x["etapa"] != "corte"]
    # Arquivo recém-gravado pode ainda não ter virado versão: tudo que é do estilo antigo sai junto, com ou sem versão.
    guardados = _guardar_arquivos(ctx, SO_VARIACAO if estilos.normalizar(estilo) == ctx.estilo else tuple(MOTIVOS))
    corte_atual = json.loads(ctx.prod.get("estilo_corte") or "{}")
    for m in materiais:
        corte_atual[m] = ctx.versoes[m]["numero"]
    for m in materiais:  # aprovação de item vale para o estilo em que foi dada, mesmo que a imagem nova saia igual
        faz("UPDATE itens SET decisao='pendente' WHERE slug=? AND material=?", slug, m)
    nova = im["nova"]
    estilos.gravar(ctx.pasta, nova)
    faz("UPDATE producoes SET estilo=?, estilo_corte=? WHERE slug=?", nova["estilo"], json.dumps(corte_atual), slug)
    evento(slug, f"Estilo trocado: {im['atual']} → {im['nome']}" + (f". Refazer: {fluxo.lista_e(x['nome'] for x in im['refazer'])}." if im["refazer"] else ""))
    refazendo = _retomar(slug, materiais, nova["estilo"] != ctx.estilo)
    return {"trocado": True, "estilo": descrever(slug), "refazer": im["refazer"], "guardados": guardados, "refazendo": refazendo}


def _guardar_arquivos(ctx, materiais):
    """Move o que é do estilo antigo para fora do contrato de arquivos. Continua na pasta, é só voltar à mão se quiser."""
    nomes = list(dict.fromkeys(a for m in materiais for a in ARQUIVOS.get(m, ())))
    if (ctx.pasta / "corte.json").exists() and "corte.json" not in nomes:
        nomes += ["corte.json", "corte_assets"]
    existentes = [n for n in nomes if (ctx.pasta / n).exists()]
    if not existentes:
        return []
    destino = ctx.pasta / "_troca_estilo" / datetime.now().strftime("%Y%m%d-%H%M%S")
    destino.mkdir(parents=True, exist_ok=True)
    for n in existentes:
        shutil.move(str(ctx.pasta / n), str(destino / n))
    return existentes


def _retomar(slug, materiais, estilo_mudou):
    """Quem refaz é quem já fazia: o grafo reabre só os nós afetados; no fluxo fixo, a primeira etapa pendente começa."""
    from . import grafos
    if um("SELECT 1 x FROM execucoes WHERE slug=? LIMIT 1", slug):
        return grafos.ao_trocar_estilo(slug, materiais, estilo_mudou)
    ctx = fluxo.Contexto(slug)
    if "cenas" not in materiais and "video" not in materiais:
        return []
    if "cenas" not in materiais or not ctx.aprovado("roteiro"):
        return []  # o render continua manual, como sempre
    etapa = "componentes" if ctx.aplicavel(fluxo.POR_ID["componentes"]) and not ctx.versoes.get("componentes") else "cenas"
    try:
        fluxo.iniciar_etapa(slug, etapa)
        return [etapa]
    except Recusado as ex:
        evento(slug, f"Refazer {NOME_MATERIAL[etapa]} ficou para depois: {ex}")
        return []


def versoes_validas(slug, material):
    """Número a partir do qual uma versão vale para o estilo atual."""
    p = um("SELECT estilo_corte FROM producoes WHERE slug=?", slug) or {}
    return json.loads(p.get("estilo_corte") or "{}").get(material, 0)

