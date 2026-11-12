"""Faz o papel do `claude -p --agent ...` nos testes: lê o pedido, altera os arquivos como o agente faria e responde em stream-json.
Sem rede e sem custo. Falha sob encomenda: crie output/<slug>/.falhar_<agente>."""
import json
import os
import re
import sys
import time
from pathlib import Path


def registrar_pedido(pasta, agente, pedido):
    """O grafo dispara agentes em paralelo; serialize o log compartilhado do simulador.

    No Windows, dois processos abrindo o mesmo arquivo com ``a`` podem calcular a
    posicao de append ao mesmo tempo e uma entrada encobrir a outra. O diretorio
    de lock e criado atomicamente e existe apenas durante a escrita curta.
    """
    trava = pasta / ".pedidos.lock"
    limite = time.monotonic() + 10
    while True:
        try:
            trava.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= limite:
                raise TimeoutError(f"nao consegui travar o registro de pedidos: {trava}")
            time.sleep(0.01)
    try:
        with (pasta / ".pedidos_recebidos.txt").open("a", encoding="utf-8") as f:
            f.write(f"=== {agente}\n{pedido}\n")
    finally:
        trava.rmdir()


def responder(texto, erro=False):
    print(json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write", "input": {"file_path": "roteiro.txt"}}]}}), flush=True)
    print(json.dumps({"type": "result", "is_error": erro, "subtype": "error_during_execution" if erro else "success", "result": texto, "total_cost_usd": 0.0}), flush=True)


def main():
    a = sys.argv
    if len(a) > 2 and a[1] == "auth":
        print(json.dumps({"loggedIn": True, "authMethod": "simulado"}))
        return
    # Agente preso a uma versão não vem com --agent: as instruções vêm em arquivo e o executor informa o id.
    agente = a[a.index("--agent") + 1] if "--agent" in a else os.environ["ESTUDIO_AGENTE"]
    pedido = sys.stdin.read()
    if "TESTE isolado" in pedido:
        return testar_isolado(a)
    if "UM tema novo" in pedido:  # o botão Gerar um tema: não há produção ainda
        time.sleep(0.6)
        if Path("output/.falhar_tema").exists():
            print("simulação: sem acesso à internet", file=sys.stderr, flush=True)
            responder("Falha simulada: não consegui abrir as fontes.", erro=True)
            sys.exit(1)
        Path("output/modric_tema_dormir-menos.md").write_text("# Tema: Por que os jovens estão dormindo menos\n\n**Descrição:** Dados de sono por idade.\n\n**Por que agora:** Pesquisa recente.\n\n**Fontes:**\n- a.com\n\n**Direção de ângulo:** Contexto, não preguiça.\n", encoding="utf-8")
        responder("Tema gravado.")
        return
    slug = re.search(r"Produção: ([\w.-]+)\.", pedido).group(1)
    p = Path("output") / slug
    # Registro do que o agente recebeu: o teste confere se o comentário e a versão chegaram mesmo.
    registrar_pedido(p, agente, pedido)
    time.sleep(0.6)
    if (p / ".lento").exists():
        time.sleep(120)
    if (p / f".falhar_{agente}").exists():
        print("simulação: o agente falhou de propósito", file=sys.stderr, flush=True)
        responder("Falha simulada: o arquivo que eu precisava não abriu.", erro=True)
        sys.exit(1)
    if agente.startswith("modric"):
        (p / "notas.md").write_text("# Notas\nFato 1. Fonte: a.com\nFato 2. Fonte: b.com\nFato 3. Fonte: c.com\n", encoding="utf-8")
    elif agente.startswith("neymar"):
        if "voz_ajustes.json" in pedido:
            cenas = re.findall(r"\[cena (\d+)", pedido)
            f = p / "voz_ajustes.json"
            atual = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
            for c in cenas or ["1"]:
                atual[str(int(c) - 1)] = {"dizer": "texto de pronúncia simulado", "velocidade": 1.05}
            f.write_text(json.dumps(atual, ensure_ascii=False), encoding="utf-8")
        elif "pediu ajustes" in pedido:
            if not (p / ".neymar_sem_mudar").exists():
                r = p / "roteiro.txt"
                d = p / "direcao_viral.md"
                texto = r.read_text(encoding="utf-8")
                antiga = next(x for x in re.split(r"\n\s*\n", texto) if len(x) > 40)
                frase = "Nos Estados Unidos, o tempo semanal com amigos ficou em quase 7 horas até 2013. Em 2021, menos de 3."
                alvo = frase if frase in texto else antiga
                nova = "Nos Estados Unidos, o tempo com amigos caiu de quase 7 horas por semana para menos de 3 em 2021."
                r.write_text(texto.replace(alvo, nova), encoding="utf-8")
                if d.exists():
                    d.write_text(d.read_text(encoding="utf-8").replace(alvo, nova), encoding="utf-8")
        else:
            (p / "angulo.md").write_text("Tese própria do vídeo.\n", encoding="utf-8")
            (p / "roteiro.txt").write_text("Primeira frase do roteiro novo, com bastante conteúdo.\n\nSegunda frase, que fecha com uma pergunta?\n", encoding="utf-8")
            (p / "direcao_viral.md").write_text("# Direção\n\n## Narração\nPrimeira frase do roteiro novo, com bastante conteúdo.\n\nSegunda frase, que fecha com uma pergunta?\n", encoding="utf-8")
    elif agente.startswith("courtois"):
        (p / "revisao.md").write_text("Conferido pelo Courtois simulado.\n", encoding="utf-8")
    elif agente.startswith("raphinha"):
        pasta = p / "componentes"
        if "pediu ajustes" in pedido:
            for nome in re.findall(r"(?:\[|· )item ([a-z_0-9]+)", pedido):
                _imagem(pasta / f"{nome}.png", (220, 90, 40))
        else:
            pasta.mkdir(exist_ok=True)
            for i, nome in enumerate(("mesa", "cadeira", "balao")):
                _imagem(pasta / f"{nome}.png", (40 + i * 60, 90, 180))
    elif agente.startswith("olise") or agente.startswith("barcola"):
        if "pediu ajustes" in pedido or "O roteiro mudou" in pedido:
            f = p / "cenas.json"
            cenas = json.loads(f.read_text(encoding="utf-8"))
            if "O roteiro mudou" in pedido:
                for c in cenas:
                    if "7 horas" in c.get("fala", ""):
                        c["fala"] = "Nos Estados Unidos, o tempo com amigos caiu de quase 7 horas por semana para menos de 3 em 2021."
            else:
                cenas[0]["sons"] = [{"t": 0.4, "tipo": "ding"}]
            f.write_text(json.dumps(cenas, ensure_ascii=False, indent=1), encoding="utf-8")
        elif re.search(r"\(id: (cartoon_alive|documentary_collage)\)", pedido):
            ident = re.search(r"\(id: (cartoon_alive|documentary_collage)\)", pedido).group(1)
            # A amostra real do estilo, com as falas do roteiro: é ela que o editor desenha e exporta de verdade.
            cenas = json.loads((Path(__file__).resolve().parents[2] / "media" / "demos" / ident / "cenas.json").read_text(encoding="utf-8"))
            falas = ["Primeira frase do roteiro novo, com bastante conteúdo.", "Segunda frase, que fecha com uma pergunta?"]
            (p / "cenas.json").write_text(json.dumps([{**c, "fala": f} for c, f in zip(cenas, falas)], ensure_ascii=False, indent=1), encoding="utf-8")
            _previa(p / "previa.jpg", 2)
        else:
            (p / "cenas.json").write_text(json.dumps([
                {"tipo": "sketch", "desenho": "cena_0", "duracao": 12, "fala": "Primeira frase do roteiro novo, com bastante conteúdo.", "rotulos": ["primeira"], "sons": []},
                {"tipo": "sketch", "desenho": "cena_1", "duracao": 12, "fala": "Segunda frase, que fecha com uma pergunta?", "rotulos": ["segunda"], "sons": []}], ensure_ascii=False, indent=1), encoding="utf-8")
            (p / "sketch_cenas.py").write_text("# simulado\n", encoding="utf-8")
            _previa(p / "previa.jpg", 2)
    elif agente.startswith("mbappe"):
        (p / "metadados.json").write_text(json.dumps({"titulo": "Título simulado do vídeo", "descricao": "Descrição simulada.", "tags": ["a", "b"], "thumbnail_texto": "TEXTO"}, ensure_ascii=False), encoding="utf-8")
    elif agente.startswith("vini"):
        if (p / ".vini_bloqueia").exists():
            responder("**BLOQUEADO**\n\nO título promete mais do que o vídeo entrega.")
            return
        responder("**APROVADO**\n\nModo simulado. Nenhuma infração encontrada.")
        return
    elif agente.startswith("sidorf"):
        d = Path("thumbnails") / "sidorf" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "relatorio.md").write_text("# Thumbnail\nPrompt simulado.\n", encoding="utf-8")
    responder(f"{agente} simulado concluiu.")


def testar_isolado(a):
    """A saída ecoa as instruções recebidas: é assim que o teste confere qual versão do agente rodou."""
    corpo = Path(a[a.index("--system-prompt-file") + 1]).read_text(encoding="utf-8")
    Path("saida_teste.md").write_text("# Saída de teste\n" + corpo[:200], encoding="utf-8")
    responder("Instruções usadas: " + corpo[:400])


def _imagem(destino, cor):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (400, 400), (250, 250, 245))
    ImageDraw.Draw(im).ellipse((60, 60, 340, 340), fill=cor)
    im.save(destino)


def _previa(destino, n):
    from PIL import Image, ImageDraw
    w, h = 216, 384
    linhas = (n + 1) // 2
    folha = Image.new("RGB", (w * 6, h * linhas), (252, 252, 247))
    d = ImageDraw.Draw(folha)
    for i in range(n):
        x0, y0 = (i % 2) * 3 * w, (i // 2) * h
        for k in range(3):
            d.rectangle((x0 + k * w + 20, y0 + 30 + 40 * i, x0 + k * w + 190, y0 + 230), outline=(30, 30, 30), width=4, fill=(120 + i * 40, 160, 210 - i * 30))
    folha.save(destino, quality=88)


if __name__ == "__main__":
    main()
