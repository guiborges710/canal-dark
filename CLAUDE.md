# Canal dark (YouTube, pt-BR)

Objetivo: canal sem rosto, automatizado ao máximo, **monetizável**. Seguir TODAS as políticas do YouTube.

## Nicho e tema
- **Nicho do canal: Análise de Comportamento Social e Gerações** (definido em 2026-10-07).
- Assinatura do canal em `output/messi_assinatura_canal.md` (tese: "Geração é rótulo; contexto é explicação").
- O nicho "curiosidades históricas" e o vídeo do Krakatoa no config.yaml e em exemplo/ são só DEMONSTRAÇÃO técnica. Não trate como tema do canal.
- Nenhum agente deve assumir nicho ou tema. Se faltar, proponha opções com dados e pergunte.

## Formato
- **PRIMEIRA VERSÃO: SHORTS APENAS** (até 60 segundos). Não vídeos longos.
- Estrutura para shorts: gancho (3s) → insight único (10-15s) → contraexemplo (10-15s) → pergunta de volta (5-10s).
- Cada short é um vídeo completo e independente.
- Depois de validar shorts, expande para vídeos longos se houver demanda.

## Regras do canal
- Cada vídeo precisa de ângulo próprio (angulo.md) e pelo menos 1/3 de comentário original. Nunca só resumir fontes.
- Fatos só das notas (3+ fontes). Tom respeitoso com vítimas. Sem sensacionalismo.
- Imagens: reais de arquivo livre quando existirem; senão geradas (Flux), em estilo fotorrealista consistente. Marcar conteúdo sintético no upload quando parecer real.
- Publicar poucos shorts por semana. Só o upload é manual.
- Chaves de API ficam só no `.env`. Nunca em chat ou código.

## Fluxo (agentes em .claude/agents)
haaland-pesquisador-nicho → modric-pesquisador-tema → messi-estrategista-angulo (SHORTS FORMAT) → neymar-roteirista (30-60s) → courtois-revisor-fatos → olise-diretor-arte (3-5 cenas) → (python run.py video --format shorts) → mbappe-editor-metadados → vini-auditor-conformidade → upload manual.

**Para SHORTS:**
- messi define ângulo em formato short (gancho → insight → contraexemplo → pergunta)
- neymar escreve roteiro de 30-60 segundos, não 8-12 minutos
- olise cria 3-5 cenas visuais (não 8-12)
- python run.py video precisa da flag `--format shorts` (ou valida se já deteta)

## Comandos
- `python run.py video --topic "..."` gera o vídeo (cada etapa guarda o resultado em output/<slug>/ e pula o que já existe).
- `python run.py ideas`, `python run.py check`, `python run.py voices`.
