"""O que cada agente recebe do estúdio, em cima do contrato que ele já tem em .claude/agents/."""
from media import estilos

REGRAS = """Você foi acionado pelo Estúdio do canal (interface de aprovação do Guilherme).
Siga seu contrato em .claude/agents e o CLAUDE.md. Escreva só os arquivos do seu contrato, em output/{slug}/.
Não publique nada, não use --allow-paid, não rode `run.py video` nem gere narração: o estúdio cuida do render.
Não pergunte nada: o Guilherme não está nesta conversa. Se faltar algo indispensável, termine dizendo exatamente o que falta.
Produção: {slug}. Tema: {tema}. Formato: {formato}. Estilo: {estilo}.
"""


# Quem recebe qual parte da direção do estilo. Roteiro e revisão pensam no visual; assets e cenas seguem as regras de produção.
DIRECAO_POR_ETAPA = {"roteiro": ("direcao_roteiro",), "componentes": ("regras_componentes",), "cenas": ("regras_assets", "regras_cenas")}


def direcao_estilo(p, etapa):
    e = estilos.obter(p["estilo"])
    if not e or etapa not in DIRECAO_POR_ETAPA:
        return ""
    linhas = [e[k] for k in DIRECAO_POR_ETAPA[etapa]]
    escolha = p.get("escolha") or {}
    var = (e.get("variantes") or {}).get(escolha.get("variante"))
    if var and etapa != "roteiro":
        linhas.append(var["regras"] + (" Opções escolhidas: " + ", ".join(f"{k} = {v}" for k, v in escolha["opcoes"].items()) + "." if escolha.get("opcoes") else ""))
    return "Direção visual do estilo escolhido:\n" + "\n".join(linhas) + "\n"


def cabecalho(p, etapa=None):
    estilo = estilos.rotulo(p["estilo"] or estilos.PADRAO, p.get("escolha")) + (f" (id: {p['estilo']})" if estilos.obter(p["estilo"]) else "")
    extras = (f"Duração alvo: {p['duracao_alvo']} s. " if p.get("duracao_alvo") else "") + (f"Idioma: {p['idioma']}. " if p.get("idioma") else "")
    return REGRAS.format(slug=p["slug"], tema=p["tema"] or p["slug"], formato=p["formato"], estilo=estilo) + (extras + "\n" if extras else "") + (f"Briefing do Guilherme:\n{p['briefing']}\n" if p.get("briefing") else "") + direcao_estilo(p, etapa)


ETAPA = {
    "pesquisa": "Pesquise o tema e salve output/{slug}/notas.md, com fatos e fontes (3+ sites).",
    "roteiro": "Leia prompts/tipos_de_roteiro.md, escolha o tipo de roteiro e escreva o vídeo a partir de output/{slug}/notas.md: salve angulo.md, roteiro.txt, direcao_viral.md (com a "
               "seção `## Narração`) e roteiro_notas.md, com o tipo na primeira linha, em output/{slug}/.",
    "courtois": "Confira output/{slug}/roteiro.txt contra output/{slug}/notas.md, corrija e salve revisao.md. Confira também o limite de prompts/tipos_de_roteiro.md: no máximo 2 números no vídeo e nenhum na abertura, fora do estilo Cartão. Se mudar uma "
                "frase que também está na seção `## Narração` de direcao_viral.md, corrija lá também, para os dois não divergirem.",
    "componentes": "O roteiro de {slug} foi aprovado. Desenhe os componentes do vídeo, para o estilo desta produção (veja a direção do estilo acima), e salve as imagens em "
                   "output/{slug}/componentes/ e as regras de layout em output/{slug}/componentes.md. "
                   "A validação do Guilherme acontece na tela do estúdio: não precisa pedir por mensagem.",
    "cenas": "O roteiro e os componentes de {slug} estão aprovados (leia output/{slug}/componentes.md, em qualquer estilo, e respeite as regras de layout: "
             "componente não cobre boneco nem texto). Monte output/{slug}/cenas.json e, só no estilo Scratch, "
             "output/{slug}/sketch_cenas.py, e confira com `python -m media.sketch --slug {slug}{formato_arg} --previa`.",
    "metadados": "Crie output/{slug}/metadados.json a partir do roteiro revisado e do ângulo.",
    "thumbnail": "O vídeo de {slug} foi aprovado pelo Guilherme e pelo Vini. Analise-o e produza a estratégia e o prompt da "
                 "thumbnail em thumbnails/sidorf/{slug}/relatorio.md. Não gere imagem.",
}

AUDITORIA = {
    "auditoria_texto": "Audite em MODO TEXTO, antes do render: confira roteiro.txt, notas.md, angulo.md, metadados.json e "
                       "os textos e falas de cenas.json em output/{slug}/, contra as políticas do YouTube e as regras do canal.",
    "auditoria_final": "Audite em MODO FINAL somente os metadados de publicação (título, descrição, tags e texto da miniatura) "
                       "de output/{slug}/. O audiovisual já foi aprovado e é imutável: não bloqueie nem peça alteração de roteiro, cenas, voz, áudio, edição ou video.mp4. "
                       "Rode `python run.py check --topic {topico}` apenas como informação e não use ressalvas audiovisuais para bloquear a publicação.",
}

FIM_AUDITORIA = """
Devolva o parecer como sua resposta final, em markdown: o estúdio grava o arquivo com essa resposta.
A primeira linha é **APROVADO** ou **BLOQUEADO**. Use só a palavra do resultado em todo o parecer: o `run.py publish` procura essas palavras no arquivo."""

ATUALIZAR_CENAS = """O roteiro mudou depois que as cenas foram feitas. {alcance}
Atualize em output/{slug}/cenas.json a `fala` e os rótulos só do que foi afetado, e redesenhe só o que precisar (em sketch_cenas.py no estilo Scratch; na própria cena nos estilos por dados).
Não mexa nas demais cenas: elas já foram aprovadas e continuam valendo. Depois rode `python -m media.sketch --slug {slug}{formato_arg} --previa`."""

AJUSTE = """O Guilherme revisou {material} v{versao} ({hash}) e pediu ajustes:

{itens}

{tarefa}
Altere só o pedido. Se algum pedido contrariar as notas ou as regras do canal, não aplique esse item e explique na resposta final."""

TAREFA_AJUSTE = {
    "roteiro": "Corrija output/{slug}/roteiro.txt e, com a mesma mudança, a seção `## Narração` de direcao_viral.md. O **Courtois** confere em seguida.",
    "componentes": "Refaça só os componentes citados, mantendo o nome do arquivo em output/{slug}/componentes/. "
                   "Não altere a imagem dos demais: eles continuam aprovados.",
    "cenas": "Altere em output/{slug}/cenas.json (e em sketch_cenas.py, se o estilo usar esse arquivo) só o que foi pedido e rode "
             "`python -m media.sketch --slug {slug}{formato_arg} --previa`. As demais cenas estão aprovadas: não mude o desenho delas.",
    "narracao": "A narração é gerada por código a partir da `fala` de cada cena, que não deve mudar por causa disso. "
                "Registre o ajuste em output/{slug}/voz_ajustes.json, um objeto com o índice da cena (começando em 0) como chave e, por cena, "
                "só os campos necessários: `dizer` (o texto como deve ser pronunciado, ex.: \"í bê gê é\" para IBGE), "
                "`velocidade` (hoje {velocidade}), `exaggeration` (expressividade, hoje {exaggeration}), `cfg_weight`, `pausa_frase_s`, `pausa_max_s`. "
                "Preserve as entradas das outras cenas. O estúdio gera de novo só esses trechos.",
    "metadados": "Corrija output/{slug}/metadados.json.",
    "pesquisa": "Corrija output/{slug}/notas.md, com fonte.",
    "thumbnail": "Refaça thumbnails/sidorf/{slug}/relatorio.md.",
}


def descrever_feedback(f, fmt_tempo):
    partes = []
    if f.get("cena") is not None:
        partes.append(f"cena {f['cena'] + 1}")
    if f.get("item") and not str(f["item"]).startswith("cena_"):
        partes.append(f"item {f['item']}")
    if f.get("tempo_s") is not None:
        partes.append(f"em {fmt_tempo(f['tempo_s'])}")
    if f.get("categoria"):
        partes.append(f["categoria"])
    return f"- {'[' + ' · '.join(partes) + '] ' if partes else ''}{f['texto']}"
