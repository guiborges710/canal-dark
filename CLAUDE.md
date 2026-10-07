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

## Fluxo (agentes em .claude/agents; debruyne-orquestrador coordena de ponta a ponta)
haaland-pesquisador-nicho → modric-pesquisador-tema → messi-estrategista-angulo → neymar-roteirista (30-60s) → courtois-revisor-fatos → cristiano-otimizador-viral (roteiro premium + direcao_viral.md) → olise-diretor-arte (3-5 cenas, lendo direcao_viral.md) → mbappe-editor-metadados → **python run.py video --format shorts** (narração+imagens+edição) → vini-auditor-conformidade → upload manual.

**Para SHORTS:**
- messi define ângulo em formato short (gancho → insight → contraexemplo → pergunta)
- neymar escreve roteiro de 30-60 segundos, não 8-12 minutos
- cristiano deixa o roteiro premium (gancho de 1-3s, retenção, pattern interrupts) e gera direcao_viral.md para imagem/edição
- olise cria 3-5 cenas, seguindo a direcao_viral.md
- `--format shorts` é o **padrão** do run.py (perfil config_shorts.yaml, 9:16); `--format long` usa config.yaml (16:9)

## Comunicação entre agentes (nomes)
Ao **mencionar** outro agente em mensagens, updates de progresso, handoffs e relatórios, use o nome do craque com inicial maiúscula e em **negrito**: **Courtois**, **Vini**, **Modric**, **Haaland**, **De Bruyne**, **Messi**, **Olise**, **Neymar**, **Mbappé**, **Cristiano**. Ex.: "**Modric** concluiu a pesquisa e passou as fontes para **Courtois** revisar." Preserve os **identificadores técnicos** (ids, `@nome-do-agente`, nomes de arquivo, listas de ferramentas) em código, arquivos e configurações.

| Craque | id técnico | Craque | id técnico |
|---|---|---|---|
| **Courtois** | courtois-revisor-fatos | **Messi** | messi-estrategista-angulo |
| **Vini** | vini-auditor-conformidade | **Olise** | olise-diretor-arte |
| **Modric** | modric-pesquisador-tema | **Neymar** | neymar-roteirista |
| **Haaland** | haaland-pesquisador-nicho | **Mbappé** | mbappe-editor-metadados |
| **De Bruyne** | debruyne-orquestrador | **Cristiano** | cristiano-otimizador-viral |

## Contrato de arquivos (a squad produz, o run.py consome) — em output/<slug>/
`notas.md`, `angulo.md`, `roteiro.txt` (**só texto narrado, sem markdown** — é quebrado em cenas frase a frase), `cenas.json` (lista com text/search/image_prompt), `metadados.json` (titulo/descricao/tags/thumbnail_prompt/thumbnail_texto). Notas humanas ficam em arquivos à parte: `revisao.md`, `roteiro_notas.md`, `direcao_viral.md`, `auditoria.md`. **Não** salve `roteiro.md`, `cenas.md` nem `metadados.md`: o run.py não os lê.

## Autonomia
Pedir "produza um vídeo sobre X" autoriza todo o fluxo com recursos **gratuitos** e dentro do `budget`. Não pergunte "posso continuar?"/"aprova o roteiro?" a cada passo: decida o rotineiro pelo briefing e registre as suposições. Pare só por falta de informação indispensável, conflito editorial, gasto acima do orçamento (`--allow-paid`) ou publicação no YouTube.

## Configuração persistente do canal (reutilizar; não reperguntar)
- **Idioma/público:** pt-BR; brasileiros 18-45 que querem entender comportamento e gerações com nuance.
- **Identidade editorial:** `output/messi_assinatura_canal.md` ("Geração é rótulo; contexto é explicação"). Tom respeitoso, analítico, sem sensacionalismo nem partido.
- **Formato padrão:** SHORT 9:16, 30-60s, 1080×1920, 30fps (config_shorts.yaml).
- **Voz/narração:** Kokoro local pt-BR (config: `pm_alex`), gratuita. Números por extenso.
- **Ferramentas/modelos:** squad (Claude Code) escreve o conteúdo de graça; run.py faz voz/imagem/edição. Imagens gratuitas (cloudflare se houver chave, senão local_art de demonstração). Pagos (Google TTS, fal, API Anthropic) só com `--allow-paid`.
- **Orçamento:** `budget.max_usd_per_video: 0` por padrão (só grátis); `max_retries_per_step: 2`.
- **Destino:** `output/<slug>/` (video.mp4, thumbnail.jpg, PUBLICAR.txt, CONFORMIDADE.md, custo.json).
- **Publicação:** upload manual, separado, só com autorização explícita.

## Comandos
- `python run.py video --topic "..."` gera o SHORT (cada etapa guarda em output/<slug>/ e pula o que já existe). `--format long` para 16:9. `--allow-paid` libera etapas pagas. `--mock` simula tudo sem custo.
- `python run.py ideas`, `python run.py check --topic "..."`, `python run.py voices`.
