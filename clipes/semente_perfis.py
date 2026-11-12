"""Gera os perfis iniciais da V2 (rodar uma vez: python -m clipes.semente_perfis).

Dois perfis: `geral` (método para qualquer vídeo, padrão de projetos novos) e `gta6` (apartado;
v1 reproduz exatamente as regras fixas da V1: palavras, pesos, janelas e hashtags).
Não sobrescreve perfil existente.
"""
import json
import time

from clipes import perfis as PF

REACAO_PT = ["olha", "meu deus", "caramba", "absurdo", "inacreditável", "inacreditavel", "impossível",
             "impossivel", "insano", "louco", "incrível", "incrivel"]
REACAO_EN = ["wow", "no way", "omg", "oh my god", "insane", "crazy", "unreal"]
SEM = {"kaka": "", "zidane": "", "figo": "", "totti": "", "lewandowski": "", "pirlo": ""}

PERFIS = [
    {"id": "gta6", "nome": "GTA 6",
     "descricao": "Cortes de lives, reacts e análises de GTA 6 (perfil original do setor, migrado das regras fixas da V1).",
     "publico": "Gamers brasileiros 16-35 que acompanham o lançamento de GTA 6", "idioma_fala": "auto",
     "objetivo": "Cortes curtos de descobertas, novidades e reações fortes para Reels e TikTok",
     "temas": ["GTA 6", "Rockstar Games", "lançamento", "trailer", "gameplay"],
     "palavras_chave": ["gta", "gta6", "gta 6", "trailer"] + REACAO_PT + REACAO_EN,
     "entidades": ["rockstar", "vice city", "lucia", "jason"], "termos_tecnicos": [],
     "assuntos_desejados": ["descobertas no mapa ou no trailer", "novidades confirmadas",
                            "momentos relevantes de gameplay", "reação forte do streamer"],
     "selecao": {"pesos": {"pico_audio": 1.0, "palavras_chave": 0.8, "abertura_forte": 0.5,
                           "densidade_fala": 0.6, "assunto_excluido": -1.5}, "limite_palavras": 4,
                 "criterios": ["Descoberta ou novidade sobre GTA 6 explicada no trecho",
                               "Reação forte do criador (grito, surpresa, risada)",
                               "Momento de gameplay que se entende sem o resto do vídeo"]},
     "duracao": {"min": 20, "max": 55}, "quantidade": 5, "contexto": {"antes": 0, "depois": 0},
     "estilo_editorial": "Hype com fidelidade: gancho curto que o trecho cumpre; nada de vazamento ou spoiler.",
     "preset_edicao": "borrado", "fontes": {"tema_pesquisa": "GTA 6", "canais": []},
     "hashtags": ["#gta6", "#gta", "#games", "#cortes", "#gamer"],
     "instrucoes_agentes": {**SEM,
         "totti": "Tema quente (20%): GTA 6 e o momento do lançamento (19/11/2026) pesam; assunto frio pesa menos.",
         "figo": "Sem vazamento, spoiler, cutscene isolada ou trailer cru.",
         "pirlo": "Tema padrão: GTA 6, vídeos de 20+ minutos."}},
    {"id": "geral", "nome": "Geral (qualquer vídeo)",
     "descricao": "Método único para qualquer vídeo falado: fofoca, vlog, podcast, entrevista, react, aula, gameplay comentado.",
     "publico": "Público de Reels e TikTok no Brasil", "idioma_fala": "auto",
     "objetivo": "Trechos que se entendem sozinhos e prendem nos primeiros segundos",
     "temas": [], "palavras_chave": [], "entidades": [], "termos_tecnicos": [],
     "assuntos_desejados": ["revelação ou novidade", "história com começo, meio e fim", "opinião forte com argumento",
                            "reação forte (surpresa, risada, indignação)", "explicação clara de algo",
                            "conflito ou discordância", "momento engraçado"],
     "assuntos_excluir": ["publi", "publicidade", "código de desconto", "cupom", "link na bio", "inscreva-se"],
     "selecao": {"pesos": {"pico_audio": 0.8, "palavras_chave": 0.0, "abertura_forte": 0.6,
                           "densidade_fala": 0.7, "assunto_excluido": -2.0}, "limite_palavras": 4,
                 "criterios": ["O trecho se entende sem o resto do vídeo (quem, o quê, por quê)",
                               "Começa forte: a primeira frase já desperta curiosidade, surpresa ou riso",
                               "Termina numa conclusão, virada ou reação, não no meio de uma ideia",
                               "Sem afirmar como fato o que no vídeo é boato ou suposição (fofoca: deixe claro que é o que a pessoa diz)"]},
     "duracao": {"min": 20, "max": 60}, "quantidade": 5, "contexto": {"antes": 1.5, "depois": 1},
     "estilo_editorial": "Fiel ao vídeo: o gancho promete só o que o trecho entrega; tom respeitoso com pessoas citadas.",
     "preset_edicao": "borrado", "fontes": {"tema_pesquisa": "", "canais": []},
     "hashtags": ["#cortes", "#viral", "#fyp"],
     "instrucoes_agentes": {**SEM,
         "kaka": "Serve para qualquer tipo de vídeo. Primeiro identifique pela transcrição o tipo (fofoca, vlog, podcast, entrevista, react, aula, gameplay) e escolha o que funciona nesse tipo: em vlog, situações e reações; em fofoca e podcast, revelações e opiniões com o contexto de quem fala; em aula, uma ideia completa. Não há análise visual: se o que importa é só a imagem (paisagem, jogada sem narração), diga isso no parecer.",
         "zidane": "Em fofoca, o gancho e o fecho deixam claro que é o relato ou a opinião de quem fala, sem afirmar como fato.",
         "totti": "Tema quente: o quanto o assunto do trecho está em alta agora; sem dado de alcance, diga que é estimativa."}},
]


def main() -> None:
    PF.PASTA.mkdir(exist_ok=True)
    for p in PERFIS:
        alvo = PF.PASTA / f"{p['id']}.json"
        if alvo.exists():
            print(f"já existe: {p['id']}")
            continue
        n = PF.normalizar({**p, "versao": 1, "atualizado_em": round(time.time())})
        erros = PF.validar(n)
        assert not erros, (p["id"], erros)
        alvo.write_text(json.dumps(n, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"criado: {p['id']}")


if __name__ == "__main__":
    main()
