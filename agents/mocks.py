"""Respostas simuladas para testar o pipeline sem gastar nada (--mock)."""
import json

NOTES = "- Fato simulado 1 (fonte: exemplo.com)\n- Fato simulado 2 (fonte: exemplo.com)\n- Fato simulado 3 (fonte: exemplo.com)"
SCRIPT = "\n\n".join(
    " ".join(f"Esta é a frase simulada número {p * 4 + i} do roteiro de teste, escrita só para validar o pipeline."
             for i in range(1, 5))
    for p in range(4)
)
REVIEW = json.dumps({"aprovado": True, "problemas": [], "roteiro_revisado": SCRIPT})
METADATA = json.dumps({
    "titulo": "Título simulado do vídeo de teste",
    "descricao": "Descrição simulada. Este vídeo foi gerado apenas para testar o pipeline.",
    "tags": ["teste", "simulado", "pipeline"],
    "thumbnail_texto": "TESTE",
})
IDEAS = json.dumps([
    {"titulo": f"Ideia simulada {i}", "angulo": "ângulo simulado", "por_que_funciona": "teste",
     "dificuldade_visual": "baixa"} for i in range(1, 4)
])

ANGLE = ("## Tese\nTese simulada do vídeo de teste.\n\n## Pergunta que prende\nPergunta simulada?\n\n"
         "## Três ideias que o espectador não encontra numa busca rápida\n1. Ideia simulada (fonte: exemplo.com)\n"
         "2. Ideia simulada (fonte: exemplo.com)\n3. Ideia simulada (fonte: exemplo.com)\n\n"
         "## Comentário próprio\nInterpretação simulada, marcada como interpretação.\n\n## Estrutura\nBlocos simulados.\n")

# Cenas de teste (--mock): a animação roda de verdade, só o texto é simulado.
CENAS = [
    {"tipo": "gancho", "duracao": 4, "numeros": ["3%", "15%"], "legenda": ["TESTE SIMULADO", "SEM API"],
     "pergunta": ["ESTE É O TESTE", "DO MOTOR?"], "rodape": ["PIPELINE OK"]},
    {"tipo": "barras", "duracao": 6, "titulo": ["BARRAS DE TESTE"], "escala_max": 15,
     "barras": [{"rotulo": "A", "valor": 3, "cor": "azul"}, {"rotulo": "B", "valor": 15, "cor": "laranja"}],
     "rodape": ["SIMULADO, SEM DADOS"]},
    {"tipo": "barras_horizontais", "duracao": 6, "titulo": ["COMPARAÇÃO DE TESTE"],
     "barras": [{"rotulo": ["PRIMEIRA"], "valor": 60, "cor": "azul"}, {"rotulo": ["SEGUNDA"], "valor": 33, "cor": "laranja"}],
     "destaque": ["RESULTADO", "SIMULADO"]},
    {"tipo": "fechamento", "duracao": 10, "negacao": ["NÃO É: TESTE", "É ESSA?"], "afirmacao": ["É: O MOTOR", "FUNCIONA?"],
     "reforco": ["SE VOCÊ VIU ISTO,", "O RENDER ESTÁ OK"], "pergunta": ["QUAL CARTÃO", "FICOU MELHOR?"]},
]
