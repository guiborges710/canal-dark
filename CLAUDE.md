# Canal dark (YouTube, pt-BR)

Objetivo: canal sem rosto, automatizado ao máximo, **monetizável**. Seguir TODAS as políticas do YouTube.

## Nicho e tema
- **Nicho do canal: AINDA NÃO ESCOLHIDO (a definir com o Guilherme).**
- O nicho "curiosidades históricas" e o vídeo do Krakatoa no config.yaml e em exemplo/ são só DEMONSTRAÇÃO técnica. Não trate como tema do canal.
- Nenhum agente deve assumir nicho ou tema. Se faltar, proponha opções com dados e pergunte.

## Regras do canal
- Cada vídeo precisa de ângulo próprio (angulo.md) e pelo menos 1/3 de comentário original. Nunca só resumir fontes.
- Fatos só das notas (3+ fontes). Tom respeitoso com vítimas. Sem sensacionalismo.
- Imagens: reais de arquivo livre quando existirem; senão geradas (Flux), em estilo fotorrealista consistente. Marcar conteúdo sintético no upload quando parecer real.
- Publicar poucos vídeos por semana. Só o upload é manual.
- Chaves de API ficam só no `.env`. Nunca em chat ou código.

## Fluxo (agentes em .claude/agents)
haaland-pesquisador-nicho → modric-pesquisador-tema → messi-estrategista-angulo → neymar-roteirista → courtois-revisor-fatos → olise-diretor-arte → (python run.py video) → mbappe-editor-metadados → vini-auditor-conformidade → upload manual.

## Comandos
- `python run.py video --topic "..."` gera o vídeo (cada etapa guarda o resultado em output/<slug>/ e pula o que já existe).
- `python run.py ideas`, `python run.py check`, `python run.py voices`.
