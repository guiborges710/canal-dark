# Canal dark (YouTube, pt-BR)

Objetivo: canal sem rosto, automatizado ao máximo, **monetizável**. Seguir TODAS as políticas do YouTube.

## Nicho e tema
- **Nicho do canal: Análise de Comportamento Social e Gerações** (definido em 2026-10-07).
- Assinatura do canal em `output/messi_assinatura_canal.md` (tese: "Geração é rótulo; contexto é explicação").
- Os vídeos de demonstração (ex.: Krakatoa em `exemplo/`) são só prova técnica do pipeline. Não são tema do canal.
- Nenhum agente deve assumir nicho ou tema. Se faltar, proponha opções com dados e pergunte.

## Formato
- **SHORTS APENAS** (30 a 60 segundos, 1080×1920, 30 fps). Não vídeos longos por enquanto.
- Estrutura: gancho (4 s, a ideia mais forte já no frame 0) → desenvolvimento em 1 a 3 blocos com números e texto-chave → contraexemplo → pergunta de volta (fechamento, sem resposta pronta).
- Cada short é um vídeo completo e independente.
- **Estilo visual: animação vetorial feita por código** (SVG). Cartões de texto com contorno grafite, sombra sólida e entrada por mola; barras que crescem; movimento em todo o vídeo; flash branco entre cenas. Cores: azul, azul-claro, amarelo, laranja, branco e grafite.
- **Sem voz e sem narração.** Os sons são efeitos gerados por código (impactos, dings, whooshes).
- **Sem imagens de IA e sem fotos de terceiros.** Todo o visual é desenhado pelo motor em `render/`.

## Regras do canal
- Cada vídeo precisa de ângulo próprio (angulo.md) e pelo menos 1/3 de comentário original. Nunca só resumir fontes.
- Fatos só das notas (3+ fontes). Tom respeitoso com vítimas. Sem sensacionalismo.
- Números e datas no texto dos cartões precisam estar nas notas, com fonte citada na descrição.
- Publicar poucos shorts por semana. O upload é automático como **privado** (`postar_pendentes.py`, um vídeo por execução, só com auditoria APROVADA do Vini). Tornar público é sempre manual, no Studio.
- Chaves de API ficam só no `.env`. Nunca em chat ou código.

## Fluxo (agentes em .claude/agents; debruyne-orquestrador coordena de ponta a ponta)
**Fluxo ENXUTO (padrão diário de SHORTS, com auditoria de texto antes do render):**
modric-pesquisador-tema → neymar-roteirista (ângulo + texto de 30-60s + direcao_viral.md, num passe) → courtois-revisor-fatos → **vini-auditor-conformidade, modo TEXTO** (valida roteiro.txt, notas e metadados ANTES de qualquer render; grava `auditoria_texto.md`) → olise-diretor-arte (cenas animadas, lendo direcao_viral.md) → mbappe-editor-metadados → **python run.py video --topic "..."** (render da animação + sons + conformidade) → vini-auditor-conformidade, modo FINAL (só imagem, som, animação e miniatura; grava `auditoria.md`, que libera o publish) → **sidorf-thumbnail-estrategista** (prompt da thumbnail para o ChatGPT; não gera imagem) → upload manual (Memphis).

**Regra do texto:** nenhum vídeo entra no render sem `auditoria_texto.md` APROVADO. Problema de texto depois do render não é corrigido refazendo o vídeo: é tratado no texto, antes do render. A auditoria final só revisa o que o render produziu (imagem, som, animação, miniatura).

**Agentes sob-demanda (fora do fluxo diário):**
- memphis-social-media → referencias_virais.md: rodar **~1x por semana**; o neymar reusa o arquivo existente.
- haaland-pesquisador-nicho → só para trocar/expandir nicho ou lote de ideias (nicho atual já fixo).
- messi-estrategista-angulo e cristiano-otimizador-viral → passes dedicados de ângulo/viral para reforço pontual. No diário, o **Neymar** já absorve os dois.

**Para SHORTS:**
- neymar define o ângulo (gancho → insight → contraexemplo → pergunta), escreve 30-60s de texto para os cartões (não 8-12 min) e gera direcao_viral.md para o desenho e o ritmo
- olise transforma o texto em cenas animadas (`cenas.json`), seguindo a direcao_viral.md
- `python run.py video` é o único comando de produção: não há `--format`, o perfil é `config_shorts.yaml`

## Comunicação entre agentes (nomes)
Ao **mencionar** outro agente em mensagens, updates de progresso, handoffs e relatórios, use o nome do craque com inicial maiúscula e em **negrito**: **Courtois**, **Vini**, **Modric**, **Haaland**, **De Bruyne**, **Messi**, **Olise**, **Neymar**, **Mbappé**, **Cristiano**, **Memphis**. Ex.: "**Modric** concluiu a pesquisa e passou as fontes para **Courtois** revisar." Preserve os **identificadores técnicos** (ids, `@nome-do-agente`, nomes de arquivo, listas de ferramentas) em código, arquivos e configurações.

| Craque | id técnico | Craque | id técnico |
|---|---|---|---|
| **Courtois** | courtois-revisor-fatos | **Messi** | messi-estrategista-angulo |
| **Vini** | vini-auditor-conformidade | **Olise** | olise-diretor-arte |
| **Modric** | modric-pesquisador-tema | **Neymar** | neymar-roteirista |
| **Haaland** | haaland-pesquisador-nicho | **Mbappé** | mbappe-editor-metadados |
| **De Bruyne** | debruyne-orquestrador | **Cristiano** | cristiano-otimizador-viral |
| **Memphis** | memphis-social-media | | |
| **Sidorf** | sidorf-thumbnail-estrategista | | |

## Contrato de arquivos (a squad produz, o run.py consome) — em output/<slug>/
- `notas.md`: fatos com fonte (3+ sites).
- `angulo.md`: tese, pergunta e comentário próprio.
- `roteiro.txt`: **texto do vídeo, sem markdown e sem rubricas**, na ordem em que aparece. Serve de base para os cartões e para a conformidade (texto próprio, abertura e fecho). Não é narração.
- `cenas.json`: lista de cenas animadas (tipo, duracao e textos). Contrato completo em `.claude/agents/olise-diretor-arte.md`. O `run.py` valida o arquivo antes de renderizar.
- `metadados.json`: `titulo`, `descricao` (com "Fontes:" e "Animação feita por computador, sem voz"), `tags`, `thumbnail_texto`.
- Notas humanas ficam em arquivos à parte: `revisao.md`, `roteiro_notas.md`, `direcao_viral.md`, `auditoria.md`. **Não** salve `roteiro.md`, `cenas.md` nem `metadados.md`: o run.py não os lê.

## Autonomia
Pedir "produza um vídeo sobre X" autoriza todo o fluxo com recursos **gratuitos** e dentro do `budget`. Não pergunte "posso continuar?"/"aprova o roteiro?" a cada passo: decida o rotineiro pelo briefing e registre as suposições. Pare só por falta de informação indispensável, conflito editorial, gasto acima do orçamento (`--allow-paid`) ou publicação no YouTube.

## Configuração persistente do canal (reutilizar; não reperguntar)
- **Idioma/público:** pt-BR; brasileiros 18-45 que querem entender comportamento e gerações com nuance.
- **Identidade editorial:** `output/messi_assinatura_canal.md` ("Geração é rótulo; contexto é explicação"). Tom respeitoso, analítico, sem sensacionalismo nem partido.
- **Formato padrão:** SHORT 9:16, 30-60s, 1080×1920, 30 fps, H.264 yuv420p com faixa TV (config_shorts.yaml).
- **Visual:** animação vetorial por código (render/). Sem imagens de IA, sem fotos de terceiros, sem voz.
- **Ferramentas:** squad (Claude Code) escreve o conteúdo de graça; `run.py` renderiza (Node + Chrome local, ffmpeg) e gera os sons por código. Custo zero no render.
- **Orçamento:** `budget.max_usd_per_video: 0` (nada pago); `max_retries_per_step: 2`. O único gasto possível é o texto pela API da Anthropic, só com `--allow-paid`.
- **Destino:** `output/<slug>/` (video.mp4, thumbnail.jpg, PUBLICAR.txt, CONFORMIDADE.md, custo.json, cenas.json, eventos.json).
- **Publicação:** `postar_pendentes.py` sobe, um por execução, o próximo slug de `output/fila_postagem.txt` como **PRIVADO**; `python run.py publish` faz o mesmo para um slug específico. Ambos usam OAuth (credenciais em `client_secret.json` + `.youtube_token.json`, ambos gitignored; nunca versionar). Exige `auditoria.md` APROVADA. Tornar público é passo manual no Studio. **Memphis** é o responsável pela postagem.

## Comandos
- `python run.py video --topic "..."`: gera o SHORT. Cada etapa guarda em `output/<slug>/` e pula o que já existe. `--mock` simula o texto (o render é real). `--allow-paid` libera a geração de texto pela API.
- `python run.py check --topic "..."`: confere a conformidade de um vídeo já gerado.
- `python run.py ideas`: lista de ideias de pauta.
- `python run.py publish --slug <pasta>` (ou `--topic "..."`): sobe o vídeo para o YouTube via OAuth. **Padrão: PRIVADO** (`publish.privacy`). Só roda se `auditoria.md` estiver **APROVADO** (regra do **Vini**). `--privacy unlisted|public` sobrepõe.
- Render direto (sem `run.py`): `cd render && node render.mjs --spec ../output/<slug>/cenas.json --out ../output/<slug>`.

## Arquitetura do código (o run.py consome o que a squad produz)
Duas camadas distintas: a **squad** são os subagentes do Claude Code em [.claude/agents/](.claude/agents/) (escrevem o conteúdo de graça); o **pipeline** é código Python que valida, renderiza e confere. Os `agents/*.py` são um *fallback* pago que gera o texto pela API da Anthropic, usado só com `--mock` ou `--allow-paid`.

**Dependências de runtime:** Python 3.10+ (o `.venv` do projeto), `ffmpeg`+`ffprobe` no PATH, **Node.js** (para o motor de render em `render/`, com `npm install` feito uma vez) e o Chrome instalado (`CHROME_PATH` sobrepõe o caminho padrão). Libs Python em [requirements.txt](requirements.txt).

**Fluxo em [run.py](run.py) `make_video()` — 6 etapas, cada uma idempotente:**
1. `notas.md` ← [agents/research.py](agents/research.py) `research_topic` (web search)
2. `angulo.md` ← `make_angle` (ponto de vista próprio, antes do texto)
3. `roteiro.txt` ← [agents/script.py](agents/script.py) `write_script`+`review_script` (só com `--allow-paid`; a squad escreve normalmente)
4. `cenas.json` ← a squad (olise). Com `--mock`, usa [agents/mocks.py](agents/mocks.py) `CENAS`.
5. render → `video.mp4`, `thumbnail.jpg` (um frame do próprio vídeo), `eventos.json` e `audio.wav` ← [media/motion.py](media/motion.py) (valida o cenas.json, chama `render/render.mjs`, gera o áudio com [media/sfx.py](media/sfx.py) e codifica com ffmpeg)
6. `metadados.json` ← a squad (mbappe); `PUBLICAR.txt`; [compliance.py](compliance.py) → `CONFORMIDADE.md`; `custo.json`

**Módulos-chave:**
- [render/](render/) — motor de animação: `index.html` + `src/` (cores, componentes, uma cena por tipo: gancho, barras, barras_horizontais, fechamento) + `render.mjs` (puppeteer-core com o Chrome local; gera um PNG por frame e o `eventos.json`). Determinístico: só depende do frame.
- [media/motion.py](media/motion.py) — `validate(cenas)` (erro aponta cena e campo; linhas com mais de 26 caracteres são recusadas), `render(out)`, codificação e miniatura.
- [media/sfx.py](media/sfx.py) — efeitos sonoros por código a partir dos eventos (semente fixa, mesmo áudio sempre).
- [agents/llm.py](agents/llm.py) — acesso único ao Claude (só fallback pago); roteia modelo por `tier` em `config_shorts.yaml`, conta custo. Em `--mock` devolve [agents/mocks.py](agents/mocks.py).
- [media/render.py](media/render.py), [media/tts.py](media/tts.py), [media/captions.py](media/captions.py) — **não são do canal**: são usados pelo fluxo separado de Reels (`reels/`). Não entram no `run.py video`.
- [compliance.py](compliance.py) — heurísticas pré-publicação (fontes, ângulo, texto copiado, cadência, animação válida, clickbait, aviso de animação gerada por computador). **Não garante monetização.**

**Config:** [config_shorts.yaml](config_shorts.yaml) (único perfil). Chaves em `.env` (gitignored): `ANTHROPIC_API_KEY` e `YOUTUBE_API_KEY` (opcionais), `CHROME_PATH` se o Chrome não estiver no caminho padrão.

**Demonstração vs. canal:** [exemplo/](exemplo/) é só prova técnica do pipeline. [agentes_para_instalar/](agentes_para_instalar/) + `instalar_agentes.bat` copiam os subagentes no Windows. Teste rápido sem custo: `python run.py video --topic "teste" --mock`.
