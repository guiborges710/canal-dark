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
**Fluxo ENXUTO (padrão diário de SHORTS, 5 passos + render):**
modric-pesquisador-tema → neymar-roteirista (num passe só: ângulo + roteiro 30-60s premium/viral + direcao_viral.md) → courtois-revisor-fatos → olise-diretor-arte (3-5 cenas, lendo direcao_viral.md) → mbappe-editor-metadados → **python run.py video --format shorts** (narração+imagens+edição) → vini-auditor-conformidade → **publicação (Memphis): `python run.py publish --to all`** sobe para YouTube (privado) **e** TikTok (rascunhos); você finaliza/torna público manualmente em cada plataforma.

**Agentes sob-demanda (fora do fluxo diário):**
- memphis-social-media → referencias_virais.md: rodar **~1x por semana**; o neymar reusa o arquivo existente.
- haaland-pesquisador-nicho → só para trocar/expandir nicho ou lote de ideias (nicho atual já fixo).
- messi-estrategista-angulo e cristiano-otimizador-viral → passes dedicados de ângulo/viral para **vídeo longo** (`--format long`) ou reforço pontual. No diário, o **Neymar** já absorve os dois.

**Para SHORTS:**
- neymar define o ângulo (gancho → insight → contraexemplo → pergunta), escreve 30-60s (não 8-12 min), deixa o roteiro premium (gancho 1-3s, retenção, pattern interrupts) e gera direcao_viral.md para imagem/edição — tudo num passe
- olise cria 3-5 cenas, seguindo a direcao_viral.md
- `--format shorts` é o **padrão** do run.py (perfil config_shorts.yaml, 9:16); `--format long` usa config.yaml (16:9)

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
- **Publicação:** `python run.py publish` sobe como **PRIVADO** via OAuth (credenciais em `client_secret.json` + `.youtube_token.json`, ambos gitignored; nunca versionar). Exige `auditoria.md` APROVADA. Tornar público é passo manual seu no Studio. **Memphis** é o responsável pela postagem.

## Comandos
- `python run.py video --topic "..."` gera o SHORT (cada etapa guarda em output/<slug>/ e pula o que já existe). `--format long` para 16:9. `--allow-paid` libera etapas pagas. `--mock` simula tudo sem custo.
- `python run.py ideas`, `python run.py check --topic "..."`, `python run.py voices`.
- `python run.py publish --slug <pasta>` (ou `--topic "..."`) sobe o vídeo pronto. **`--to youtube` (padrão) | `tiktok` | `all`.** YouTube via OAuth, **PRIVADO** por padrão (`publish.privacy`); TikTok via Content Posting API, cai nos **rascunhos** da conta (escopo `video.upload`, sem auditoria). Em ambos você revê e torna público manualmente (Studio / app TikTok). Só roda se `auditoria.md` estiver **APROVADO** (regra do **Vini**). `--privacy unlisted|public` sobrepõe (só YouTube). **`--publish-at "2026-10-14 18:30"` (horário de Brasília) AGENDA a publicação no YouTube: sobe privado e o YouTube torna público sozinho na data/hora — 100% automático, sem passo manual no Studio. Força `private`; só vale para YouTube.** Setup do TikTok (conta + app dev + chaves no `.env`): ver [TIKTOK_SETUP.md](TIKTOK_SETUP.md). Chaves novas no `.env`: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`. Módulo: [media/tiktok.py](media/tiktok.py), espelha [media/youtube.py](media/youtube.py).

## Arquitetura do código (o run.py consome o que a squad produz)
Duas camadas distintas: a **squad** são os subagentes do Claude Code em [.claude/agents/](.claude/agents/) (escrevem o conteúdo de graça); o **pipeline** é código Python que faz voz, imagem e edição. Os `agents/*.py` são um *fallback* pago que gera o mesmo conteúdo pela API da Anthropic, usado só com `--mock` ou `--allow-paid`.

**Dependências de runtime:** Python 3.12, `ffmpeg`+`ffprobe` no PATH (todo o vídeo/áudio passa por eles), libs em [requirements.txt](requirements.txt). Os modelos da voz local Kokoro ficam em [models/](models/) (~123 MB, versionados). `.venv/` já existe.

**Fluxo em [run.py](run.py) `make_video()` — 8 etapas, cada uma idempotente (pula se o arquivo já existe):**
1. `notas.md` ← [agents/research.py](agents/research.py) `research_topic` (web search)
1b. `angulo.md` ← `make_angle` (ponto de vista próprio, antes do roteiro)
2. `roteiro.txt` ← [agents/script.py](agents/script.py) `write_script`+`review_script` (rascunho em `roteiro_rascunho.txt`, revisão em `revisao.json`)
3. `cenas.json` ← [agents/scenes.py](agents/scenes.py): `split_scenes` quebra o roteiro frase a frase **por código** (não inventa texto); `image_prompts` pede os prompts de imagem ao Claude
4. narração por cena → `audio/NNN.mp3` ← [media/tts.py](media/tts.py) (`parallel`, um áudio por cena = sincronia exata, sem Whisper)
5. imagens por cena → `images/NNN.jpg` ← [media/images.py](media/images.py)
6. edição → `video.mp4` ← [media/render.py](media/render.py) (clipe por cena com zoompan, concat, música com ducking+loudnorm) + `captions.srt`
7. `metadados.json` ← [agents/metadata.py](agents/metadata.py); gera `thumbnail.jpg`, `creditos.txt`, `PUBLICAR.txt`, e roda [compliance.py](compliance.py) → `CONFORMIDADE.md`
8. `custo.json` (só chamadas novas desta execução)

**Módulos-chave:**
- [agents/llm.py](agents/llm.py) — acesso único ao Claude; roteia modelo por `tier` (`config*.yaml` → `tiers`/`models`), conta tokens e custo, extrai JSON de respostas, 3 retries. Os agentes carregam o system prompt de [prompts/*.md](prompts/) via [agents/common.py](agents/common.py) `prompt()` (substitui `<<chave>>`). Em `--mock` devolve os textos de [agents/mocks.py](agents/mocks.py).
- [media/tts.py](media/tts.py) — `provider: kokoro` (local, grátis) ou `google` (pago). `--mock` gera tom senoidal.
- [media/images.py](media/images.py) `generate()` — provedores: `commons` (foto real de arquivo), `cloudflare` (Flux grátis), `fal` (pago), `local_art` (procedural, só demo). Falha de provedor **cai para local_art** em vez de derrubar o vídeo.
- [media/commons.py](media/commons.py) — baixa imagem livre do Wikimedia Commons, filtra licença (PD/CC0/CC BY; SA só com flag), enquadra, grava crédito no `.json` ao lado.
- [media/captions.py](media/captions.py) — texto na tela estilo viral: um PNG por bloco (Pillow), composto via `overlay` do ffmpeg. **Não usa libass/drawtext** (este ffmpeg não tem). O `.srt` continua separado.
- [media/render.py](media/render.py), [media/util.py](media/util.py) `run()`/`duration()`/`parallel()` — wrappers de ffmpeg/ffprobe e paralelismo.
- [compliance.py](compliance.py) — heurísticas pré-publicação (fontes, ângulo, texto copiado, cadência, créditos, clickbait, aviso de conteúdo sintético). **Não garante monetização.**

**Config:** [config_shorts.yaml](config_shorts.yaml) (9:16, padrão) e [config.yaml](config.yaml) (16:9, `--format long`). `enforce_budget()` troca provedores pagos pelo grátis equivalente quando falta `--allow-paid`. Chaves em `.env` (gitignored): `ANTHROPIC_API_KEY`, `YOUTUBE_API_KEY`, `GOOGLE_TTS_API_KEY`, `FAL_KEY`, `CF_ACCOUNT_ID`/`CF_API_TOKEN`.

**Demonstração vs. canal:** [exemplo/](exemplo/) e o vídeo do Krakatoa são só prova técnica do pipeline — não são o tema do canal. [agentes_para_instalar/](agentes_para_instalar/) + `instalar_agentes.bat` copiam os subagentes no Windows. Teste rápido sem custo: `python run.py video --topic "teste" --mock`.
