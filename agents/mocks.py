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
    "thumbnail_prompt": "a dramatic mountain landscape at sunrise",
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
