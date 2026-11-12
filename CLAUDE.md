# Canal dark (YouTube, pt-BR)

Objetivo: canal sem rosto, automatizado ao máximo, **monetizável**. Seguir TODAS as políticas do YouTube.

## Nicho e tema
- **Nicho do canal: Análise de Comportamento Social e Gerações** (definido em 2026-10-07).
- Assinatura do canal em `output/messi_assinatura_canal.md` (tese: "Geração é rótulo; contexto é explicação").
- Os vídeos de demonstração (ex.: Krakatoa em `exemplo/`) são só prova técnica do pipeline. Não são tema do canal.
- Nenhum agente deve assumir nicho ou tema. Se faltar, proponha opções com dados e pergunte.

## Formato
- **SHORTS APENAS** (30 a 60 segundos, 1080×1920, 30 fps). Não vídeos longos por enquanto.
- Estrutura: um dos tipos de `prompts/tipos_de_roteiro.md` (decisão do dono em 2026-11-03), sem repetir o tipo dos últimos 3 vídeos. Situação concreta antes de dado, gancho já no frame 0 e nunca com estatística, **no máximo 2 números e 1 gráfico por Short** (o estilo Cartão é a exceção) e tese em uma frase. `media/roteiro.py` conta, e a conformidade avisa.
- Cada short é um vídeo completo e independente.
- **Estilo visual: animação feita por código, em dois estilos** (decisão do dono em 2026-10-29: o **sketch** é o padrão; o SVG fica disponível se o pedido disser "estilo cartões"):
  - **Sketch (padrão):** folha de caderno pautada, traço de caneta tremido, ícones simples (boneco de palito, copo, casa, barras...), sem legenda na base, corte seco entre cenas. Skill `.claude/skills/roteiro-para-video-sketch/SKILL.md`; biblioteca `media/sketch_lib.py`; renderer `media/sketch.py`. **O vídeo é feito em cima do áudio**: a narração é gerada primeiro e cada cena dura o que a fala dura.
  - **Cartões (SVG):** cartões de texto com contorno grafite, sombra sólida e entrada por mola; barras que crescem; flash branco entre cenas. Cores: azul, azul-claro, amarelo, laranja, branco e grafite.
  - **Cartoon Vivo (`cartoon_alive`) e Colagem Documental (`documentary_collage`):** decisão do dono em 2026-11-03, escolhidos no Corte por projeto (ou em `estilo.json`). A cena é descrita em dados no `cenas.json`, sem `sketch_cenas.py`, e as bibliotecas desenham por camadas. Skill `.claude/skills/estilos-por-camadas/SKILL.md`. O registro único dos estilos é `media/estilos.py`.
- **Sons** Os sons são efeitos gerados por código (impactos, dings, whooshes).

## Regras do canal
- Cada vídeo precisa de ângulo próprio (angulo.md) e pelo menos 1/3 de comentário original. Nunca só resumir fontes.
- Fatos só das notas (3+ fontes). Tom respeitoso com vítimas. Sensacionalismo permitido no começo do canal (gancho, miniatura, títulos), desde que: (a) o tema seja o do próprio vídeo, sem isca de assunto alheio (nada de título ou miniatura sobre um tema e conteúdo sobre outro); (b) nada seja falso ou não confirmado pelas notas; (c) o vídeo entregue o que o gancho promete. Revisar esse tom quando o canal tiver inscritos e volume, e voltar a um tom mais sério. Decisão do dono (2026-10-27).

<!-- CRIAR UM ARQUIVO PARA DEIXAR EXPLICITO A CADENCIA DE POSTAGEM -->
<!-- - Publicar poucos shorts por semana. O upload é automático como **privado** (`postar_pendentes.py`, um vídeo por execução, só com auditoria APROVADA do Vini). Tornar público é sempre manual, no Studio. -->

- Chaves de API ficam só no `.env`. Nunca em chat ou código.

## Fluxo (agentes em .claude/agents; debruyne-orquestrador coordena de ponta a ponta)
**Fluxo ENXUTO (padrão diário de SHORTS, com auditoria de texto antes do render):**
modric-pesquisador-tema (+ memphis-social-media, se as referências tiverem mais de ~7 dias; juntos) → neymar-roteirista (ângulo + texto de 30-60s + direcao_viral.md, num passe) → courtois-revisor-fatos → **raphinha-curador-componentes** (desenha os componentes do vídeo nos quatro estilos: sketch, cartões, cartoon_alive e colagem; manda as imagens para o Guilherme validar e passa as regras de layout; na fase "aprendendo" de `componentes/aprendizados.md`, espera a aprovação) → **olise-diretor-arte** (cenas animadas, lendo direcao_viral.md e componentes.md) **em paralelo com** mbappe-editor-metadados (metadados) → **vini-auditor-conformidade, modo TEXTO** (valida roteiro.txt, notas, metadados e textos das cenas ANTES de qualquer render; grava `auditoria_texto.md`) → **python run.py video --topic "..."** (render da animação + sons + conformidade) → vini-auditor-conformidade, modo FINAL (só imagem, som, animação e miniatura; grava `auditoria.md`, que libera o publish) → **sidorf-thumbnail-estrategista** (prompt da thumbnail para o ChatGPT; não gera imagem) → upload manual (Memphis).

**Orquestração por dependência:** o **De Bruyne** dispara de uma vez, na mesma mensagem, todos os agentes cujo insumo já existe (ex.: **Olise** e **Mbappé** juntos) e só segura quem espera uma entrega. Em lote, cada slug corre em paralelo; só o render roda um por vez.

**Regra do texto:** nenhum vídeo entra no render sem `auditoria_texto.md` APROVADO. Problema de texto depois do render não é corrigido refazendo o vídeo: é tratado no texto, antes do render. A auditoria final só revisa o que o render produziu (imagem, som, animação, narração).

**Regra inviolável de congelamento (decisão do Guilherme, 2026-11-03):** o roteiro precisa ser aprovado pelo **Vini** antes de produzir o vídeo. Depois dessa aprovação, `roteiro.txt` é imutável: ninguém o reescreve nem o corrige. Antes do render, cenas, narração e demais materiais devem ser preparados e validados contra esse roteiro aprovado. Depois que o vídeo final for gerado, o pacote audiovisual fica congelado: não alterar roteiro, cenas, narração/voz, áudio, edição nem `video.mp4`, e não regenerar o vídeo por parecer posterior do **Vini**. A auditoria final pode bloquear a publicação somente por metadados (`titulo`, `descricao`, `tags`, texto/miniatura); ressalvas audiovisuais são observações, sem bloquear nem modificar o vídeo. Só o Guilherme pode autorizar explicitamente uma nova versão do vídeo.

**Agentes sob-demanda (fora do fluxo diário):**
- memphis-social-media → referencias_virais.md: rodar **~1x por semana**; o neymar reusa o arquivo existente.
- haaland-pesquisador-nicho → só para trocar/expandir nicho ou lote de ideias (nicho atual já fixo).
- maradona-estrategista-angulo e cristiano-otimizador-viral → passes dedicados de ângulo/viral para reforço pontual. No diário, o **Neymar** já absorve os dois.

**Para SHORTS:**
- neymar define o ângulo, escolhe o tipo de roteiro em `prompts/tipos_de_roteiro.md`, escreve 30-60s de texto (não 8-12 min) e gera direcao_viral.md para o desenho e o ritmo
- olise transforma o texto em cenas animadas (`cenas.json`), seguindo a direcao_viral.md
- `python run.py video` é o único comando de produção: não há `--format`, o perfil é `config_shorts.yaml`

## Comunicação entre agentes (nomes)
Ao **mencionar** outro agente em mensagens, updates de progresso, handoffs e relatórios, use o nome do craque com inicial maiúscula e em **negrito**: **Courtois**, **Vini**, **Modric**, **Haaland**, **De Bruyne**, **Maradona**, **Olise**, **Neymar**, **Mbappé**, **Cristiano**, **Memphis**. Ex.: "**Modric** concluiu a pesquisa e passou as fontes para **Courtois** revisar." Preserve os **identificadores técnicos** (ids, `@nome-do-agente`, nomes de arquivo, listas de ferramentas) em código, arquivos e configurações.

| Craque | id técnico |
|---|---|
| **Courtois** | courtois-revisor-fatos 
| **Maradona** | maradona-estrategista-angulo
| **Vini** | vini-auditor-conformidade 
| **Olise** | olise-diretor-arte
| **Raphinha** | raphinha-curador-componentes (componentes visuais; vem antes do Olise; aprende com o Guilherme em `componentes/aprendizados.md`)
| **Barcola** | barcola-diretor-horizontal (cenas sketch dos vídeos horizontais 16:9, `--formato horizontal`)
| **Modric** | modric-pesquisador-tema 
| **Neymar** | neymar-roteirista
| **Haaland** | haaland-pesquisador-nicho 
| **Mbappé** | mbappe-editor-metadados
| **De Bruyne** | debruyne-orquestrador 
| **Cristiano** | cristiano-otimizador-viral
| **Memphis** | memphis-social-media
| **Seedorf** | sidorf-thumbnail-estrategista
| **Zico** | zico-po-programacao (setor de programação, `programacao/README.md`; só se trabalha em item do quadro Trello da sprint ativa, ver "Regra do quadro")
| **Xavi** | xavi-scrum-master
| **Ancelotti** | ancelotti-agile-coach
| **Thiago Silva** | thiago-silva-tech-lead
| **Rodrygo** | rodrygo-dev-back
| **Endrick** | endrick-dev-front
| **Iniesta** | iniesta-ux-corte
| **Alisson** | alisson-qa
| **Marquinhos** | marquinhos-devops-release

## Contrato de arquivos (a squad produz, o run.py consome) — em output/<slug>/
- `notas.md`: fatos com fonte (3+ sites).
- `angulo.md`: tese, pergunta e comentário próprio.
- `roteiro.txt`: **texto do vídeo, sem markdown e sem rubricas**, na ordem em que aparece. Serve de base para os cartões e para a conformidade (texto próprio, abertura e fecho). Não é narração.
- `cenas.json`: lista de cenas animadas (tipo, duracao e textos). Contrato completo em `.claude/agents/olise-diretor-arte.md` (estilo cartões) e na skill `roteiro-para-video-sketch` (estilo sketch, `"tipo": "sketch"`). O `run.py` valida o arquivo antes de renderizar.
- `estilo.json` (opcional, gravado pelo Corte): `{"estilo", "variante", "opcoes"}`. Projeto sem ele vale pelo `tipo` das cenas.
- `sketch_cenas.py` (só no estilo sketch): as funções de desenho `cena_N(lt, dur)`, escritas pelo Olise com `media/sketch_lib.py`. Conferir o desenho: `python -m media.sketch --slug <pasta> --previa` (gera `previa.jpg`, sem voz).
- `metadados.json`: `titulo`, `descricao`, `tags`, `thumbnail_texto`.
- `corte.json` e `corte_assets/` (opcionais, escritos só pelo editor do Corte): as decisões de edição. O `run.py` não os lê; exportar pelo editor grava o `video.mp4`.
- Notas humanas ficam em arquivos à parte: `revisao.md`, `roteiro_notas.md`, `direcao_viral.md`, `auditoria.md`. **Não** salve `roteiro.md`, `cenas.md` nem `metadados.md`: o run.py não os lê.

## Autonomia
Pedir "produza um vídeo sobre X" autoriza todo o fluxo com recursos **gratuitos** e dentro do `budget`. Não pergunte "posso continuar?"/"aprova o roteiro?" a cada passo: decida o rotineiro pelo briefing e registre as suposições. Pare só por falta de informação indispensável, conflito editorial, gasto acima do orçamento (`--allow-paid`) ou publicação no YouTube.

## Configuração persistente do canal (reutilizar; não reperguntar)
- **Idioma/público:** pt-BR; brasileiros 18-45.
- **Identidade editorial:** `output/messi_assinatura_canal.md`.
- **Formato padrão:** SHORT 9:16, 30-60s, 1080×1920, 30 fps, H.264 yuv420p com faixa TV (config_shorts.yaml).
- **Visual:** animação vetorial por código (render/).
- **Ferramentas:** squad (Claude Code) escreve o conteúdo de graça; `run.py` renderiza (Node + Chrome local, ffmpeg) e gera os sons por código. Custo zero no render.
- **Orçamento:** `budget.max_usd_per_video: 0` (nada pago); `max_retries_per_step: 2`. O único gasto possível é o texto pela API da Anthropic, só com `--allow-paid`.
- **Destino:** `output/<slug>/` (video.mp4, thumbnail.jpg, PUBLICAR.txt, CONFORMIDADE.md, custo.json, cenas.json, eventos.json).
- **Publicação:** `postar_pendentes.py` sobe, um por execução, o próximo slug de `output/fila_postagem.txt` como **PRIVADO**; `python run.py publish` faz o mesmo para um slug específico. Ambos usam OAuth (credenciais em `client_secret.json` + `.youtube_token.json`, ambos gitignored; nunca versionar). Exige `auditoria.md` APROVADA. Tornar público é passo manual no Studio. **Memphis** é o responsável pela postagem.

## Empresa e setor de inteligência
- **Contexto Explica** é o nome da empresa (o canal é o seu primeiro produto). **De Bruyne** é o CEO: fala com o Guilherme e coordena os setores.
- **Setor de inteligência** (métricas, análises e atualização de mercado dark; sem produção e sem publicação): contrato em `inteligencia/README.md`. Equipe: **Hugo Souza**, **Fagner**, **André Carrillo**, **Raniele**, **Yuri Alberto** e **Vitinho** (agentes `*-analista-*`, `hugo-souza-*`, `vitinho-consolidador` em `.claude/agents/`). Coletor do canal próprio: `inteligencia/coletar_metricas.py`.
- **Setor de ação:** ainda não existe. Será definido com o Guilherme; o briefing de entrada é `inteligencia/briefing_acao.md`.

## Comandos
- `.venv\Scripts\python -m media.estilos_demo [id]`: gera de novo as demonstrações da tela de estilos, pelos renderizadores reais.
- `.venv\Scripts\python -m corte` (ou `-m estudio`): abre o Corte (interface web local em http://127.0.0.1:8765/) para acompanhar as produções, aprovar por versão, editar o vídeo e mudar agentes e fluxos. Lê e aciona o mesmo fluxo abaixo; o que roda pelo terminal aparece lá como nova versão. Detalhes em `estudio/README.md`.
- `python tools/sincronizar_codex.py` (`--verificar` só confere): espelha `.claude/agents` e as skills para o Codex (`.codex/agents`, `.agents/skills`). **Reserva com Codex** (decisão do dono, 2026-11-03): os trabalhos de agente do Corte são refeitos pelo Codex só quando o Claude esgota o limite (5 horas, semanal ou de uso); enquanto o Claude estiver disponível, nunca se usa Codex. A conversa interativa do Claude Code não troca sozinha de motor: no terminal, o dono abre o Codex na pasta e chama os agentes de `.codex/agents`. Detalhes em `estudio/README.md`.
- `.venv\Scripts\python -m corte --rede`: o mesmo Corte, também para o celular no Wi-Fi de casa, com senha (mostrada no terminal). Detalhes e limites em `estudio/README.md`.
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
5. render → `video.mp4`, `prompt_thumbnail.txt` (feito pelo Seedorf), `eventos.json` e `audio.wav` ← [media/motion.py](media/motion.py) (valida o cenas.json, chama `render/render.mjs`, gera o áudio com [media/sfx.py](media/sfx.py) e codifica com ffmpeg)
6. `metadados.json` ← a squad (mbappe); `PUBLICAR.txt`; [compliance.py](compliance.py) → `CONFORMIDADE.md`; `custo.json`

**Módulos-chave:**
- [render/](render/) — motor de animação: `index.html` + `src/` (cores, componentes, uma cena por tipo: gancho, barras, barras_horizontais, fechamento) + `render.mjs` (puppeteer-core com o Chrome local; gera um PNG por frame e o `eventos.json`). Determinístico: só depende do frame.
- [media/motion.py](media/motion.py) — `validate(cenas)` (erro aponta cena e campo; linhas com mais de 26 caracteres são recusadas), `render(out)`, codificação e miniatura.
- [media/sfx.py](media/sfx.py) — efeitos sonoros por código a partir dos eventos (semente fixa, mesmo áudio sempre).
- [media/sketch.py](media/sketch.py) + [media/sketch_lib.py](media/sketch_lib.py) — estilo sketch: valida o `cenas.json`, gera a narração primeiro, desenha cada cena no tempo da fala (multiprocessamento) e codifica com o mesmo encode do SVG. O `run.py` escolhe sozinho quando todas as cenas são `"tipo": "sketch"`.
- [media/estilos.py](media/estilos.py) — registro único dos estilos (id, nome, motor, direção para os agentes). [media/camadas.py](media/camadas.py), [media/cartoon_lib.py](media/cartoon_lib.py) e [media/colagem_lib.py](media/colagem_lib.py) desenham os estilos por camadas, e passam pelo mesmo `media/sketch.py`.
- [media/voz.py](media/voz.py) + [media/voz_worker.py](media/voz_worker.py) — narração com a voz do Guilherme (Chatterbox, clone de `voz/amostra.wav`). Ritmo ajustável em `config_shorts.yaml`, seção `voz` (velocidade, pausas, expressividade).
- [agents/llm.py](agents/llm.py) — acesso único ao Claude (só fallback pago); roteia modelo por `tier` em `config_shorts.yaml`, conta custo. Em `--mock` devolve [agents/mocks.py](agents/mocks.py).
- [media/render.py](media/render.py), [media/tts.py](media/tts.py), [media/captions.py](media/captions.py) — **não são do canal**: são usados pelo fluxo separado de Reels (`reels/`). Não entram no `run.py video`.
- [media/roteiro.py](media/roteiro.py) — conta números e gráficos do vídeo, para a regra de `prompts/tipos_de_roteiro.md`.
- [compliance.py](compliance.py) — heurísticas pré-publicação (fontes, ângulo, texto copiado, cadência, animação válida, excesso de números, clickbait, aviso de animação gerada por computador). **Não garante monetização.**

**Config:** [config_shorts.yaml](config_shorts.yaml) (único perfil). Chaves em `.env` (gitignored): `ANTHROPIC_API_KEY` e `YOUTUBE_API_KEY` (opcionais), `CHROME_PATH` se o Chrome não estiver no caminho padrão.

**Demonstração vs. canal:** [exemplo/](exemplo/) é só prova técnica do pipeline. [agentes_para_instalar/](agentes_para_instalar/) + `instalar_agentes.bat` copiam os subagentes no Windows. Teste rápido sem custo: `python run.py video --topic "teste" --mock`.
