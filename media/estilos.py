"""Registro único dos estilos de vídeo. A interface, os prompts dos agentes, a validação e o render leem daqui.

O id é o que fica gravado (`producoes.estilo`, `estilo.json` e o `tipo` das cenas); o `nome` é só o que aparece na tela. `cartoes` e
`sketch` são os ids de sempre, usados nos projetos antigos e no fluxo publicado: `card` e `scratch` são aceitos como sinônimos.

`motor` diz quem desenha:
- "svg": render/ no Chrome (media/motion.py).
- "codigo": `sketch_cenas.py` escrito pelo agente, com `cena_N(lt, dur)` (media/sketch.py).
- "dados": a própria cena do cenas.json descreve tudo, e a `lib` desenha. Passa pelo mesmo media/sketch.py.

Para criar um estilo novo: uma entrada aqui com `motor: "dados"`, uma lib com `CAMPOS`, `validar(cena, onde)`, `textos(cena)` e
`quadro(cena, lt, dur, ctx)`, e `media/demos/<id>/cenas.json`. Depois `python -m media.estilos_demo <id>` gera a demonstração da tela.
"""
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

ARQUIVO = "estilo.json"
PADRAO = "sketch"
ESTILOS = {
    "cartoes": {
        "nome": "Cartão", "sinonimos": ["card"], "motor": "svg", "tipos": ["gancho", "barras", "barras_horizontais", "fechamento"], "formatos": ["vertical"],
        "descricao": "Cartões de texto com contorno grafite, barras que crescem e flash entre as cenas. É o único estilo feito de números.",
        "melhor_para": "Comparações de números, rankings e dados diretos.",
        "direcao_roteiro": "Estilo Cartão: o texto vira cartões curtos e barras. Escreva frases de até 26 caracteres por linha. É o único estilo feito de números: uma comparação só, com um par de números.",
        "regras_assets": "Estilo Cartão: o visual é o que o contrato de cartões oferece (texto, barras e cores da lista); leia output/<slug>/componentes.md (Raphinha) para cartões, ícones e regras de layout.",
        "regras_cenas": "Estilo Cartão: siga o contrato de cartões (SVG) do seu arquivo de agente: gancho, barras, barras_horizontais e fechamento.",
        "regras_componentes": "Estilo Cartão: componentes são os cartões, ícones e gráficos (barras) do vídeo, nas cores da lista (azul, azul-claro, amarelo, laranja, branco e grafite), com contorno grafite e sombra sólida. Mostre cada um em imagem e diga em componentes.md em qual cena entra e onde fica. Regra de layout: nenhum componente cobre boneco, personagem ou texto; deixe a área do texto livre e registre isso em componentes.md.",
        "precisa_arquivos": [],
    },
    "sketch": {
        "nome": "Scratch", "sinonimos": ["scratch"], "motor": "codigo", "tipos": ["sketch"], "formatos": ["vertical", "horizontal"],
        "descricao": "Desenho à mão em folha de papel, traço de caneta tremido e corte seco. Padrão do canal.",
        "melhor_para": "Explicar uma ideia passo a passo, com bonecos, setas e ícones simples.",
        "direcao_roteiro": "Estilo Scratch: pense em uma imagem desenhada à mão por frase: boneco, ícone, seta, número grande. Sem texto longo na tela.",
        "regras_assets": "Estilo Scratch: componentes em traço à mão (media/sketch_componentes.py), um por elemento, sobre papel; leia output/<slug>/componentes.md (Raphinha).",
        "regras_cenas": "Estilo Scratch: siga a skill roteiro-para-video-sketch: cenas.json com \"tipo\": \"sketch\" e sketch_cenas.py com media/sketch_lib.py.",
        "regras_componentes": "Estilo Scratch: componentes são os elementos em traço à mão para a media/sketch_lib.py (boneco, objeto, ícone, seta, gráfico simples), um por arquivo, sobre papel, com o nome que o Olise vai chamar no sketch_cenas.py. Regra de layout: nenhum componente cobre boneco, personagem ou texto; deixe a área do texto livre e registre isso em componentes.md.",
        "precisa_arquivos": ["sketch_cenas.py"],
        "variantes": {
            "caderno_pautado": {
                "nome": "Caderno pautado", "detalhe": "Linhas azul-claro, margem vermelha, bonecos simples, setas e anotações à mão.",
                "opcoes": {"papel": {"bege": "Papel bege", "branco": "Papel branco"}, "traco": {"grafite": "Traço de grafite", "marcador": "Traço de marcador"}},
                "regras": "Variação Caderno pautado: a folha e o traço já vêm da biblioteca; não desenhe pauta nem margem. Use `marcador(d, x0, y, x1)` para destacar, em cor pontual, e `anotacao(d, x, y, \"texto\", seta_para=(x, y))` para notas à mão.",
            },
        },
    },
    "cartoon_alive": {
        "nome": "Cartoon Vivo", "sinonimos": [], "motor": "dados", "lib": "media.cartoon_lib", "tipos": ["cartoon_alive"], "formatos": ["vertical"],
        "descricao": "Desenho animado 2D com personagens recorrentes, expressões fortes e poses que mudam.",
        "melhor_para": "Comportamento do dia a dia, situações entre pessoas e histórias com reação.",
        "direcao_roteiro": "Estilo Cartoon Vivo: escreva como cena de desenho animado. Cada fala precisa de uma ação visível e de uma reação de um personagem recorrente. Prefira situações do dia a dia e uma virada que muda a expressão de alguém.",
        "regras_assets": "Estilo Cartoon Vivo: use o elenco, as poses, as expressões, os objetos e os cenários de media/cartoon_lib.py, escolhidos pelo nome, e leia output/<slug>/componentes.md (Raphinha) para o que foi aprovado e para as regras de layout. A paleta é única por vídeo, de 6 cores. Personagem é original: nada de copiar personagem, canal ou propriedade existente. Celular precisa de texto coerente na tela.",
        "regras_cenas": "Estilo Cartoon Vivo: leia a skill estilos-por-camadas (.claude/skills/estilos-por-camadas/SKILL.md). Entregue só o cenas.json, com \"tipo\": \"cartoon_alive\" em toda cena, sem sketch_cenas.py. Use o mesmo personagem em poses diferentes entre as cenas e feche com \"saida\": \"loop\" quando fizer sentido.",
        "regras_componentes": "Estilo Cartoon Vivo: componentes são o elenco, as poses e expressões, os objetos e os cenários da media/cartoon_lib.py. Escolha-os pelo nome da biblioteca, mostre cada um em imagem, fixe a paleta única de 6 cores do vídeo e use personagem original, sem copiar propriedade existente. Celular precisa de texto coerente. Regra de layout: nenhum componente cobre boneco, personagem ou texto; deixe a área do texto livre e registre isso em componentes.md.",
        "precisa_arquivos": [],
    },
    "documentary_collage": {
        "nome": "Colagem Documental", "sinonimos": [], "motor": "dados", "lib": "media.colagem_lib", "tipos": ["documentary_collage"], "formatos": ["vertical"],
        "descricao": "Mural de evidências em papel: recortes, fita, carimbos, marca-texto e câmera sobre a mesa.",
        "melhor_para": "Investigações, linhas do tempo e histórias com documentos.",
        "direcao_roteiro": "Estilo Colagem Documental: escreva como investigação. Cada fala revela uma evidência: um documento, uma pessoa, um lugar, uma data ou uma ligação entre fatos. Só afirme o que está nas notas: tudo que aparece no mural vira prova para quem assiste.",
        "regras_assets": "Estilo Colagem Documental: recortes, texturas, mapas, fichas e silhuetas vêm de media/colagem_lib.py; leia output/<slug>/componentes.md (Raphinha) para o que foi aprovado e para as regras de layout. Não use foto de pessoa real, nem mídia externa ou paga. Foto só como arquivo local licenciado, na pasta do projeto, com a licença anotada em notas.md. Documento mostrado tem de ser ilustração clara, nunca falsificação de documento real.",
        "regras_cenas": "Estilo Colagem Documental: leia a skill estilos-por-camadas (.claude/skills/estilos-por-camadas/SKILL.md). Entregue só o cenas.json, com \"tipo\": \"documentary_collage\" em toda cena, sem sketch_cenas.py. Toda cena tem superfície, um recorte central, destaque e movimento de câmera; ligue as evidências com `conexoes`.",
        "regras_componentes": "Estilo Colagem Documental: componentes são os recortes, documentos, mapas, fichas, carimbos, fitas e silhuetas da media/colagem_lib.py. Sem foto de pessoa real nem mídia externa ou paga; documento mostrado é ilustração clara, nunca falsificação de documento real. Regra de layout: nenhum componente cobre boneco, personagem ou texto; deixe a área do texto livre e registre isso em componentes.md.",
        "precisa_arquivos": [],
    },
}
_SINONIMOS = {s: i for i, e in ESTILOS.items() for s in e["sinonimos"]}
_TIPOS = {t: i for i, e in ESTILOS.items() for t in e["tipos"]}


def normalizar(ident):
    """Id gravado de qualquer forma aceita. Devolve None se não for um estilo."""
    ident = _SINONIMOS.get(ident, ident)
    return ident if ident in ESTILOS else None


def obter(ident):
    return ESTILOS.get(normalizar(ident))


def do_tipo(tipo):
    return _TIPOS.get(tipo)


def das_cenas(cenas):
    """Estilo que um cenas.json realmente é. Mistura ou tipo desconhecido devolve None."""
    achados = {do_tipo(c.get("tipo")) for c in cenas} if cenas else set()
    return next(iter(achados)) if len(achados) == 1 and None not in achados else None


def por_quadros(ident):
    """Desenhado quadro a quadro em Python, pelo media/sketch.py."""
    e = obter(ident)
    return bool(e) and e["motor"] in ("codigo", "dados")


def por_dados(ident):
    e = obter(ident)
    return bool(e) and e["motor"] == "dados"


def lib(ident):
    return importlib.import_module(obter(ident)["lib"])


def publico():
    """O que a interface recebe. As regras dos agentes ficam fora."""
    saida = []
    for i, e in ESTILOS.items():
        saida.append({"id": i, "nome": e["nome"], "detalhe": e["descricao"], "melhor_para": e["melhor_para"], "formatos": e["formatos"], "demo": f"/web/demos/{i}.mp4", "poster": f"/web/demos/{i}.jpg", "variantes": e.get("variantes", {}), "narrado": True})
    return saida


def rotulo(ident, escolha=None):
    """Nome na tela, com a variação quando houver."""
    e = obter(ident)
    if not e:
        return "3D" if ident == "3d" else "Formato antigo" if ident == "antigo" else (ident or "Sem estilo")
    var = (e.get("variantes") or {}).get((escolha or {}).get("variante"))
    return f"{e['nome']} · {var['nome']}" if var else e["nome"]


def validar_escolha(ident, variante=None, opcoes=None, formato="vertical"):
    """Devolve a escolha limpa, ou levanta ValueError com a explicação."""
    i = normalizar(ident)
    if not i:
        raise ValueError(f"Estilo inválido: {ident}. Use: {', '.join(ESTILOS)}")
    e = ESTILOS[i]
    if formato not in e["formatos"]:
        raise ValueError(f"O formato {formato} não existe no estilo {e['nome']}.")
    escolha = {"estilo": i, "variante": None, "opcoes": {}}
    if variante:
        v = (e.get("variantes") or {}).get(variante)
        if not v:
            raise ValueError(f"O estilo {e['nome']} não tem a variação {variante}.")
        escolha["variante"] = variante
        for campo, valores in v["opcoes"].items():
            valor = (opcoes or {}).get(campo) or next(iter(valores))
            if valor not in valores:
                raise ValueError(f"{campo}: {valor} não existe. Use: {', '.join(valores)}")
            escolha["opcoes"][campo] = valor
    return escolha


def ler(pasta):
    """A escolha gravada no projeto. Projeto antigo não tem o arquivo: vale o que as cenas disserem, sem variação."""
    try:
        d = json.loads((Path(pasta) / ARQUIVO).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and normalizar(d.get("estilo")) else None


def gravar(pasta, escolha):
    Path(pasta).mkdir(parents=True, exist_ok=True)
    (Path(pasta) / ARQUIVO).write_text(json.dumps(escolha, ensure_ascii=False, indent=1), encoding="utf-8")


def modulo_dados(cenas_path):
    """Faz um cenas.json de estilo por dados se comportar como um sketch_cenas.py: `cena_N(lt, dur)` para cada cena.
    É o que deixa render, prévia e editor iguais para todos os estilos desenhados em Python."""
    cenas_path = Path(cenas_path)
    cenas = json.loads(cenas_path.read_text(encoding="utf-8"))
    ident = das_cenas(cenas)
    biblioteca = lib(ident)
    if hasattr(biblioteca, "definir_pasta"):
        biblioteca.definir_pasta(cenas_path.parent)
    funcoes = {}
    for i, c in enumerate(cenas):
        def fn(lt, dur, c=c, i=i):
            return biblioteca.quadro(c, lt, dur, {"cenas": cenas, "i": i})
        funcoes[c["desenho"]] = fn
    return SimpleNamespace(**funcoes)


def assinatura_cena(cena):
    """Muda quando o desenho da cena muda. Fala e duração ficam de fora: a duração já entra na chave do clipe, e a fala só muda o som."""
    return json.dumps({k: v for k, v in cena.items() if k not in ("fala", "duracao", "rotulos", "sons")}, sort_keys=True, ensure_ascii=False)
