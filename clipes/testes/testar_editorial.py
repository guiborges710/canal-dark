"""Testes da seleção editorial (V3). Rodar: .venv\\Scripts\\python -m clipes.testes.testar_editorial [--render]

ATENÇÃO: os casos abaixo são SINTÉTICOS (texto escrito para o teste, tempos gerados). Provam que o código cumpre
as regras de integridade; NÃO medem desempenho editorial real. O teste --render usa o vídeo real
clipes_out/flow-games-fgn (se existir) para conferir o arquivo renderizado.
Imprime antes (seleção V1, `legado=True`) e depois (V3) sobre as mesmas transcrições.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from clipes import editorial as ED
from clipes import perfis as PF
from clipes import pipeline as P

falhas: list[str] = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


# ----------------------------------------------------------------- transcrição sintética
BLOCOS = {
    "A_pergunta_resposta": ["Por que a maioria das reuniões não resolve nada?",
                            "Isso acontece porque ninguém define a decisão antes de começar.",
                            "Quando o objetivo é vago, cada pessoa sai com uma tarefa diferente.",
                            "A solução é simples: escreva a decisão no convite e cancele a reunião se ela não existir.",
                            "Foi assim que a nossa equipe cortou metade das reuniões em um mês."],
    "B_historia_cs": ["Semana passada eu joguei uma partida decisiva de Counter-Strike com meus amigos.",
                      "Faltavam dois rounds e o placar estava empatado em quatorze a quatorze.",
                      "Meu time inteiro tinha morrido e eu fiquei sozinho contra três jogadores.",
                      "Eu me escondi atrás da caixa do bomb site B e esperei o plantio da bomba.",
                      "Quando o primeiro inimigo passou, eu abati ele sem fazer barulho.",
                      "O segundo percebeu e atirou, mas eu estava agachado e ele errou tudo.",
                      "Matei o segundo, mas o terceiro já estava plantando a bomba.",                      "Então eu fiz a única coisa possível: corri até ele e taquei uma granada nos pés dele.",
                      "A granada matou o terceiro e eu desarmei a bomba com um segundo de sobra.",
                      "A gente ganhou o campeonato e meu amigo gritou tão alto que a vizinha chamou a polícia."],
    "C_piada_futebol": ["Tem um treinador que vive reclamando do gramado do estádio.",
                        "Um dia o presidente do clube resolveu o problema e trocou o gramado inteiro.",
                        "O treinador entrou em campo, olhou em volta e ficou em silêncio por um tempo.",
                        "O presidente perguntou: agora está bom, professor?",
                        "E o treinador respondeu: está ótimo, presidente, agora o problema são só os jogadores."],
    "D_frase_chamativa_vazia": ["Você não vai acreditar no que aconteceu hoje!",
                                "Bom, então, deixa eu ver aqui, um segundo, tá?",
                                "Ah, eu esqueci o que eu ia falar, mas depois eu lembro, né?",
                                "Enfim, gente, vamos lá, vamos ver o que a gente tem para hoje.",
                                "Deixa eu pegar a água aqui rapidinho, já volto, tá bom?",
                                "Pronto, voltei, acho que a gente pode continuar, né?",
                                "Então, o que eu estava falando, ah, deixa pra lá mesmo."],
    "L_historia_longa_demais": [f"No dia {k} da expedição o grupo seguiu pela trilha e anotou mais um detalhe importante da viagem."
                                for k in range(1, 9)] + ["No fim, a trilha acabou num lago escondido que ninguém conhecia."],
    "G_gta_noticia_rumor": ["A Rockstar confirmou oficialmente que o GTA 6 chega em maio.",
                            "Isso foi dito no comunicado da própria empresa, publicado hoje de manhã.",
                            "Já o rumor de que o mapa terá seis cidades vem de uma fonte anônima e não foi confirmado.",
                            "Por isso vale tratar essa informação como boato até a Rockstar falar.",
                            "No resumo, a data é fato, o tamanho do mapa é especulação."],
    "H_chamada": ["Na sexta a gente estava revisando o código do sistema de pagamentos.",
                  "Primeiro vimos que o teste automático estava desligado há três meses.",
                  "Depois descobrimos que ninguém tinha percebido porque o alerta ia para um e-mail antigo.",
                  "Eu nunca tinha visto um erro tão absurdo!",
                  "No fim, religamos o teste e ele achou onze falhas escondidas."],
    "F_redundante_de_A": ["Por que a maioria das reuniões não resolve nada?",
                          "Isso acontece porque ninguém define a decisão antes de começar.",
                          "Quando o objetivo é vago, cada pessoa sai com uma tarefa diferente.",
                          "A solução é simples: escreva a decisão no convite e cancele a reunião se ela não existir.",
                          "Foi assim que a equipe reduziu as reuniões pela metade."],
}
INICIOS = {"A_pergunta_resposta": 30, "D_frase_chamativa_vazia": 120, "C_piada_futebol": 200, "H_chamada": 300,
           "G_gta_noticia_rumor": 400, "B_historia_cs": 585, "L_historia_longa_demais": 1200,  # B atravessa a fronteira de 600 s
           "F_redundante_de_A": 900}


def transcricao() -> dict:
    segs = []
    for nome, frases in BLOCOS.items():
        t = INICIOS[nome]
        for fr in frases:
            pal = fr.split()
            dur = max(2.0, len(pal) / 2.6)
            passo = dur / len(pal)
            segs.append({"ini": t, "fim": t + dur, "texto": fr,
                         "palavras": [{"ini": t + k * passo, "fim": t + (k + 1) * passo - 0.03, "t": p}
                                      for k, p in enumerate(pal)]})
            t += dur + 0.3
    segs.sort(key=lambda s: s["ini"])
    return {"idioma": "pt", "segmentos": segs}


def projeto(raiz: Path, nome: str, perfil: str) -> Path:
    d = raiz / nome
    d.mkdir()
    (d / "transcricao.json").write_text(json.dumps(transcricao(), ensure_ascii=False), encoding="utf-8")
    (d / "fonte.json").write_text(json.dumps({"origem": "sintetico", "autor": "Teste", "titulo_original": "",
                                              "autorizacao": {"tipo": "teste", "prova": ""}}), encoding="utf-8")
    PF.congelar(d, perfil)
    return d


def bloco_de(m: dict) -> str | None:
    for nome, t0 in INICIOS.items():
        if m["ini"] < t0 + 70 and m["fim"] > t0:
            return nome
    return None


def texto_do(d: Path, m: dict) -> str:
    tr = json.loads((d / "transcricao.json").read_text(encoding="utf-8"))["segmentos"]
    return " ".join(s["texto"] for s in tr if s["ini"] >= m["ini"] - 0.2 and s["fim"] <= m["fim"] + 0.2)


def mostrar(rotulo: str, d: Path, ms: list[dict]):
    print(f"  [{rotulo}]")
    for m in ms:
        t = texto_do(d, m)
        print(f"    {bloco_de(m)} {m['ini']:.1f}-{m['fim']:.1f} | ini: {t[:60]!r} | fim: {t[-55:]!r}")


# ------------------------------------------------------------------------------ casos
def teste_sintetico(raiz: Path):
    print("Casos sintéticos (texto escrito para o teste)")
    res = {}
    for perfil in ("geral", "gta6"):
        d = projeto(raiz, perfil, perfil)
        ant = P.momentos(d, 7, energia=False, legado=True)
        (d / "momentos.json").unlink()
        novo = P.momentos(d, 7, energia=False)
        mostrar(f"ANTES {perfil}", d, ant)
        mostrar(f"DEPOIS {perfil}", d, novo)
        res[perfil] = (d, novo)

    d, novo = res["geral"]
    por = {bloco_de(m): m for m in novo}
    a = por.get("A_pergunta_resposta")
    ok(a is not None, "pergunta/resposta selecionada")
    if a:
        t = texto_do(d, a)
        ok(t.startswith("Por que a maioria"), "recupera a pergunta antes da frase dependente ('Isso acontece...')")
        ok(t.endswith("em um mês."), "termina depois da conclusão")
    b = por.get("B_historia_cs")
    ok(b is not None and texto_do(d, b).endswith("chamou a polícia."), "história que atravessa o bloco de 600 s sai inteira, com desfecho")
    if b:
        ok(b["ini"] < 600 < b["fim"], "o intervalo cruza a fronteira de 600 s sem ser partido")
    c = por.get("C_piada_futebol")
    ok(c is not None and texto_do(d, c).endswith("são só os jogadores."), "piada inclui a punchline")
    ok("L_historia_longa_demais" not in por, "história íntegra maior que o máximo não vira pedaço mutilado (entrega menos)")
    ok("D_frase_chamativa_vazia" not in por, "frase chamativa sem desenvolvimento não é selecionada")
    n_ab = sum(1 for m in novo if bloco_de(m) in ("A_pergunta_resposta", "F_redundante_de_A"))
    ok(n_ab == 1, "candidatos redundantes: só um dos dois entra")
    h = por.get("H_chamada")
    ok(h is not None and h.get("gancho_trecho_sugerido", {}).get("texto", "").startswith("Eu nunca tinha visto"),
       "sugere chamada inicial com fala real do trecho (e não o desfecho)")
    if h:
        ch = h["gancho_trecho_sugerido"]
        ok(h["ini"] < ch["ini"] and ch["fim"] < h["fim"] - 3, "chamada vem do meio; o desfecho continua no final")
    g_geral = {bloco_de(m) for m in novo}
    ok({"A_pergunta_resposta", "B_historia_cs", "C_piada_futebol"} <= g_geral,
       "modo genérico atende reunião, Counter-Strike e futebol sem vocabulário de tema")
    dg, ng = res["gta6"]
    ok("G_gta_noticia_rumor" in {bloco_de(m) for m in ng}, "modo GTA 6 seleciona o trecho de notícia versus rumor")
    for perfil, (dd, ms) in res.items():
        for m in ms:
            ok(all(k in m for k in ("segmentos_origem", "avaliacao", "justificativa", "contexto_necessario", "conclusao",
                                    "problemas", "montagem")), f"{perfil} #{m['id']}: registro editorial completo")
            break
    rel = json.loads((d / "selecao.json").read_text(encoding="utf-8"))
    ok(rel["escolhidos"] == len(novo) and "descartes" in rel, "selecao.json registra descartes e motivos")
    # menos cortes quando só há poucos bons: pedir 7 e receber só os íntegros
    ok(len(novo) <= 7 and all(m["score"] >= ED.NOTA_MINIMA for m in novo), "não preenche cota com corte fraco")


def teste_revalidar():
    print("Revalidação (ajuste manual ou do Kaká)")
    segs = transcricao()["segmentos"]
    perfil = PF.carregar("geral")
    a0 = INICIOS["A_pergunta_resposta"]
    # começa na frase dependente e termina antes da conclusão
    r_ini = next(s for s in segs if s["texto"].startswith("Isso acontece"))
    r = ED.revalidar(segs, r_ini["ini"], r_ini["ini"] + 12, perfil)
    ok(any("premissa" in c for c in r["correcoes"]), "recupera a premissa de um início dependente")
    ok(abs(r["ini"] - (a0 - 0.12 if a0 - 0.12 > 0 else 0)) < 0.2, "início alinhado à primeira palavra da pergunta")
    r2 = ED.revalidar(segs, a0, a0 + 8, perfil)
    ok(r2["fim"] > a0 + 8 or r2["problemas"], "fim no meio da ideia é estendido ou reprovado")
    r3 = ED.revalidar(segs, 5000, 5020, perfil)
    ok(r3["problemas"], "intervalo sem fala é reprovado")


def _mk(linhas):
    """linhas: [(ini, fim, texto)] -> segmentos sintéticos."""
    out = []
    for a, b, t in linhas:
        pal = t.split()
        passo = (b - a) / max(len(pal), 1)
        out.append({"ini": a, "fim": b, "texto": t,
                    "palavras": [{"ini": a + k * passo, "fim": a + (k + 1) * passo - 0.02, "t": w} for k, w in enumerate(pal)]})
    return out


def teste_regras_neutras():
    print("Regras neutras ao idioma (sintético, idiomas e frases diferentes do vídeo de teste)")
    casos = {
        "fr": dict(reticencias="Il est parti chercher le...", frag=("Il a dit qu'il viendrait mais", "demain matin finalement."),
                   perg=("Pourquoi les prix ont augmenté ?", "Parce que les coûts de transport ont doublé."),
                   liga=("Le fournisseur a refusé la proposition.", "Cette proposition était pourtant raisonnable.")),
        "en": dict(reticencias="She walked into the...", frag=("He said he would come but", "tomorrow morning in the end."),
                   perg=("Why did the prices go up?", "Because transport costs have doubled."),
                   liga=("The supplier refused the proposal.", "That proposal was actually reasonable.")),
        "xx": dict(reticencias="Han gått och hämtade den...", frag=("Han sa att han skulle komma men", "i morgon bitti till slut."),
                   perg=("Varför steg priserna egentligen?", "Eftersom transportkostnaderna dubblerades helt."),
                   liga=("Leverantören avvisade erbjudandet direkt.", "Erbjudandet var egentligen helt rimligt.")),
    }
    for idioma, c in casos.items():
        ED._definir(idioma)
        u = ED.unidades(_mk([(0, 3, c["reticencias"])]))[0]
        ok(not u["fecha"], f"[{idioma}] reticências no fim = fala interrompida, não conclusão")
        us = ED.unidades(_mk([(0, 3, c["frag"][0]), (3.8, 6, c["frag"][1])]))
        ok(us[1]["dep"] == 2, f"[{idioma}] começo em minúscula depois de frase não terminada = meio de frase")
        us = ED.unidades(_mk([(0, 3, c["perg"][0]), (3.4, 7, c["perg"][1])]))
        ok(us[1]["dep"] == 2, f"[{idioma}] resposta sem a pergunta depende da pergunta")
        us = ED.unidades(_mk([(0, 3, c["liga"][0]), (3.8, 7, c["liga"][1])]))
        ok(us[1]["liga"], f"[{idioma}] palavra rara repetida na fronteira liga as duas falas")
        us = ED.unidades(_mk([(0, 3, c["liga"][0]), (6.0, 9, c["liga"][1])]))
        ok(not us[1]["liga"], f"[{idioma}] com pausa longa a repetição não liga")
    ok(ED._definir("fr") == "fr" and ED._definir("pt-BR") == "pt" and ED._definir("xx") == "neutro", "pacote de idioma escolhido pelo idioma detectado")
    ED._definir("xx")
    ok(ED.unidades(_mk([(0, 3, "Isso acontece porque ninguém avisou.")]))[0]["dep"] == 0, "idioma sem pacote não aplica o vocabulário de outra língua")
    ED._definir("pt")
    ok(ED.unidades(_mk([(0, 3, "Isso acontece porque ninguém avisou.")]))[0]["dep"] == 2, "pacote pt continua detectando 'isso' como referência")
    # recuperação da pergunta pela revalidação, em francês
    segs = _mk([(0, 3, "Pourquoi les prix ont augmenté ?"), (3.4, 8, "Parce que les coûts de transport ont doublé cette année."),
                (8.8, 12, "Et personne n'a prévenu les clients à temps pour changer de fournisseur.")])
    r = ED.revalidar(segs, 3.4, 12, {"duracao": {"min": 5, "max": 60}}, "fr")
    ok(r["ini"] < 0.3 and any("premissa" in x for x in r["correcoes"]), "[fr] revalidação recua para incluir a pergunta da resposta")


_LEXICO = ("temperatura tempero textura ingrediente cuidado paciência tentativa erro acerto receita forma tamanho medida "
           "mistura sabor cheiro cor tempo calor frio pressa vontade costume segredo truque dica cuidado detalhe passo etapa "
           "resultado diferença melhora piora surpresa dúvida pergunta resposta exemplo caso motivo razão jeito maneira "
           "ideia plano rotina hábito prática teste prova fracasso sucesso gosto prazer trabalho esforço ajuda conselho "
           "história lembrança infância família vizinho amigo colega professor cozinha mercado feira padaria balcão").split()


def _topico(chave: str, n: int, t0: float, pausa: float = 0.7, semente: int = 7):
    """Assunto sintético coeso: n frases de vocabulário variado que repetem a palavra-chave, com pausa entre elas."""
    import random
    rnd = random.Random(semente + len(chave))
    segs, t = [], t0
    for k in range(n):
        corpo = rnd.sample(_LEXICO, 11)
        txt = f"Sobre {chave} eu {corpo[0]} {corpo[1]} e {corpo[2]} {corpo[3]} sempre {corpo[4]} {corpo[5]} com {corpo[6]} {corpo[7]} {corpo[8]}."
        pal = txt.split()
        dur = len(pal) / 2.6
        passo = dur / len(pal)
        segs.append({"ini": t, "fim": t + dur, "texto": txt,
                     "palavras": [{"ini": t + q * passo, "fim": t + (q + 1) * passo - 0.03, "t": w} for q, w in enumerate(pal)]})
        t += dur + pausa
    return segs, t


def _proj_segs(raiz: Path, nome: str, segs: list, idioma: str = "pt") -> Path:
    d = raiz / nome
    d.mkdir()
    (d / "transcricao.json").write_text(json.dumps({"idioma": idioma, "segmentos": segs}, ensure_ascii=False), encoding="utf-8")
    (d / "fonte.json").write_text(json.dumps({"origem": "s", "autor": "Teste", "titulo_original": "",
                                              "autorizacao": {"tipo": "teste", "prova": ""}}), encoding="utf-8")
    PF.congelar(d, "geral")
    return d


def teste_series(raiz: Path):
    print("Séries em partes (assunto que não coube em um vertical; sintético)")
    # 1) um assunto de ~2 min vira 3 partes, cada uma dentro do limite, cortadas em frase fechada
    a, fim_a = _topico("bolo de cenoura", 24, 10.0)
    d = _proj_segs(raiz, "serie1", a)
    ms = P.momentos(d, 5, energia=False)
    partes = [m for m in ms if m.get("serie")]
    ok(len(partes) >= 2, f"assunto longo vira série ({len(partes)} partes)")
    if partes:
        mx = 60.0
        ok(all(20 <= m["dur"] <= mx for m in partes), f"cada parte cabe no limite do vertical ({[m['dur'] for m in partes]})")
        ok([m["serie"]["parte"] for m in partes] == list(range(1, len(partes) + 1)) and all(m["serie"]["de"] == len(partes) for m in partes),
           "partes numeradas em ordem (Parte X de N)")
        ok(all(partes[k]["fim"] <= partes[k + 1]["ini"] for k in range(len(partes) - 1)), "partes em sequência, sem sobreposição")
        ok(all(m["conclusao"].rstrip().endswith(".") for m in partes), "cada parte termina em frase fechada")
        ok(partes[0]["ini"] <= a[0]["ini"] + 0.5 and partes[-1]["fim"] >= fim_a - 5, "juntas, as partes cobrem o assunto inteiro")
        ok("TEM MAIS" in partes[0]["cta"] and "PARTE 1/" in partes[0]["cta"], "partes intermediárias têm CTA de 'tem mais'")
        ok("FIM" in partes[-1]["cta"], "a última parte avisa que acabou e aponta as anteriores")
        ok(json.loads((d / "selecao.json").read_text(encoding="utf-8"))["series"] == 1, "selecao.json registra a série")
    # 2) dois assuntos seguidos: nenhuma parte atravessa a troca de assunto
    a1, t1 = _topico("bolo de cenoura", 14, 10.0)
    b1, t2 = _topico("motor de bicicleta", 14, t1 + 0.7)
    d = _proj_segs(raiz, "serie2", a1 + b1)
    ms = P.momentos(d, 5, energia=False)
    misturou = [m for m in ms if m["ini"] < t1 - 3 and m["fim"] > t1 + 3]
    ok(not misturou, "nenhum corte/parte mistura dois assuntos diferentes")
    ok(any(m.get("serie") for m in ms), "os dois assuntos longos viram séries separadas")
    # 3) assunto que cabe em um vertical continua corte único
    c1, _ = _topico("bolo de cenoura", 6, 10.0)
    d = _proj_segs(raiz, "serie3", c1)
    ms = P.momentos(d, 5, energia=False)
    ok(ms and not any(m.get("serie") for m in ms), "assunto que cabe em um vertical não vira série")
    # 4) assunto longo demais (acima do máximo de partes) não vira série: não inventa 10 partes
    e1, _ = _topico("bolo de cenoura", 70, 10.0)
    d = _proj_segs(raiz, "serie4", e1)
    ms = P.momentos(d, 5, energia=False)
    ok(not any(m.get("serie") and m["serie"]["de"] > ED.PARTES_MAX for m in ms), "nunca passa do máximo de partes")
    # 5) sem pausa para cortar com segurança, não divide (entrega menos em vez de cortar no meio)
    f1, _ = _topico("bolo de cenoura", 24, 10.0, pausa=0.1)
    d = _proj_segs(raiz, "serie5", f1)
    ms = P.momentos(d, 5, energia=False)
    ok(not any(m.get("serie") for m in ms), "fala corrida sem ponto de corte íntegro não é dividida")
    # 6) CTA em outros idiomas e a legenda ASS com "PARTE X/N" e o CTA no fim
    ok("PART 1/3" in ED.cta_padrao(1, 3, "en-US") and "PARTE 2/3" in ED.cta_padrao(2, 3, "es"), "CTA no idioma do perfil")
    ass = P._ass([], [(0.0, 40.0)], "GANCHO", "Vídeo: X", "", True, "PARTE 1/3", "PARTE 1/3 - TEM MAIS! SIGA O PERFIL")
    ok(ass.count("PARTE 1/3") >= 2 and "Dialogue: 0,0:00:36.50,0:00:40.00,Gan" in ass, "ASS mostra a parte o tempo todo e o CTA nos últimos 3,5 s")


def teste_blocos_whisper():
    print("Transcrição em blocos com sobreposição")
    seg = {"ini": 597.0, "fim": 604.0}  # frase que cruza a fronteira de 600 s: ponto médio 600,5
    dono = [i for i in range(3) if P.pertence_ao_bloco(seg, i * 600.0, 600.0, i == 0)]
    ok(dono == [1], "frase na fronteira pertence a exatamente um bloco (sem duplicar nem perder)")
    ok(P.pertence_ao_bloco({"ini": 1.0, "fim": 2.0}, 0, 600, True), "início do vídeo fica no primeiro bloco")


def teste_verificacao_render(raiz: Path, render: bool):
    print("Arquivo renderizado")
    real = P.SAIDA / "flow-games-fgn"
    if not render or not (real / "fonte.mp4").exists():
        print("  (pule: rode com --render e com clipes_out/flow-games-fgn presente)")
        return
    d = raiz / "render"
    d.mkdir()
    for f in ("transcricao.json", "fonte.json"):
        shutil.copy2(real / f, d / f)
    try:
        import os
        os.link(real / "fonte.mp4", d / "fonte.mp4")
    except OSError:
        shutil.copy2(real / "fonte.mp4", d / "fonte.mp4")
    PF.congelar(d, "geral")
    ms = P.momentos(d, 2)
    m = ms[0]
    # montagem com chamada: usa a sugestão do motor, se houver; senão uma frase íntegra do meio do trecho
    ch = m.get("gancho_trecho_sugerido")
    if not ch:
        tr = json.loads((d / "transcricao.json").read_text(encoding="utf-8"))["segmentos"]
        s = next(x for x in tr if x["ini"] > m["ini"] + 8 and x["fim"] < m["fim"] - 8 and 1.5 < x["fim"] - x["ini"] < 7)
        ch = {"ini": s["ini"], "fim": s["fim"]}
    mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
    mom[0].update(gancho="TESTE DE RENDER", fecho="FECHO", gancho_trecho={"ini": ch["ini"], "fim": ch["fim"]})
    mom[1].update(gancho="TESTE", fecho="FECHO")
    (d / "momentos.json").write_text(json.dumps(mom), encoding="utf-8")
    P.cortar(d, [1, 2])
    j1 = json.loads((d / "clipes" / "01.json").read_text(encoding="utf-8"))
    ok(j1["verificacao"]["ok"], "clipe com chamada passa na verificação do arquivo")
    esperado = (m["fim"] - m["ini"]) + (ch["fim"] - ch["ini"])
    ok(abs(j1["verificacao"]["duracao_real"] - esperado) < 0.35, f"duração do arquivo ({j1['verificacao']['duracao_real']}s) = segmentos aprovados ({esperado:.2f}s)")
    ok(len(j1["trechos_origem"]) == 2 and j1["trechos_origem"][0]["ini"] == round(ch["ini"], 2), "ordem de montagem registrada (chamada, depois corte)")
    j2 = json.loads((d / "clipes" / "02.json").read_text(encoding="utf-8"))
    ok(j2["verificacao"]["ok"] and j2["verificacao"]["palavras_legendadas"] > 10, "clipe cronológico: áudio, resolução e legenda ok")
    # a verificação precisa realmente reprovar um arquivo errado
    v = P.verificar_clipe(d / "clipes" / "02.mp4", 999.0, True, [(m["ini"], 5.0)], [], True)
    ok(not v["ok"], "verificação reprova arquivo cuja duração não bate com o aprovado")


def main():
    render = "--render" in sys.argv
    raiz = Path(tempfile.mkdtemp(prefix="clipes_editorial_"))
    try:
        teste_sintetico(raiz)
        teste_revalidar()
        teste_regras_neutras()
        teste_series(raiz)
        teste_blocos_whisper()
        teste_verificacao_render(raiz, render)
    finally:
        shutil.rmtree(raiz, ignore_errors=True)
    print("\nTUDO OK" if not falhas else f"\n{len(falhas)} FALHA(S): " + "; ".join(falhas))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
