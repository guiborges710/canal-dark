# Auditoria e arquitetura do ecossistema de agentes — Canal dark

Data: 2026-10-07. Escopo: entender o ecossistema real, corrigir falhas e torná-lo integrado e autônomo (pedir a produção → receber o vídeo pronto, sem autorizar cada etapa). Distinção entre **fato confirmado** (li o código/arquivo ou rodei), **inferência** e **ausência de informação** está marcada no texto.

---

## 1. Mapa da estrutura (como era)

Dois subsistemas que **não se conversavam**:

- **Fábrica em Python** (`run.py` + `agents/*.py` + `media/*.py` + `compliance.py`): pipeline de 8 etapas, idempotente (pula o que já existe), com modo `--mock`. Consome arquivos com nomes exatos em `output/<slug>/`: `notas.md`, `angulo.md`, `roteiro.txt` (narração pura, quebrada em cenas frase a frase), `cenas.json`, `metadados.json`. Faz voz (Kokoro local ou Google), imagens (Commons/Cloudflare/fal/local_art), edição (FFmpeg), conformidade e custo.
- **Squad do Claude Code** (`.claude/agents/*.md`): 10 agentes que escrevem o conteúdo criativo. `debruyne-orquestrador` coordena os outros via a ferramenta `Agent(...)`.

Apoio: `config.yaml` (perfil longo 16:9) e `config_shorts.yaml` (perfil 9:16); `prompts/*.md` (prompts do pipeline Python); `.claude/prompts/*.md` (runbooks manuais de Short); `agentes_para_instalar/` (cópia para instalar no Windows); `models/` (Kokoro ONNX, 92 MB + 28 MB — **presentes**); `music/ambient.mp3`; `exemplo/` e `output/` (execuções anteriores).

**Quem executa o quê (confirmado):** narração, imagens, edição e renderização são **ferramentas do `run.py`** (Kokoro, provedores de imagem, FFmpeg), não agentes. Antes, nenhum agente podia acioná-las (o orquestrador não tinha `Bash`).

---

## 2. Diagnóstico priorizado (evidência → impacto → correção)

### P0 — bloqueadores (quebravam a produção)

1. **Renderização quebrava no FFmpeg (legendas).**
   - *Evidência:* `output/quem-lucra-.../_run.log` → `No option name near 'captions.srt...'` na etapa 6/8. Causa real: `ffmpeg -filters` **não lista `subtitles`** (este Homebrew FFmpeg 9.0.2 foi compilado **sem libass**). Nenhum ajuste de escape de vírgula resolveria.
   - *Impacto:* todo vídeo com `captions: true` (o `config.yaml` padrão) morria antes de gerar `video.mp4`. As pastas `quem-lucra` (pipeline) e `polarizacao-genz-boomers` (squad) acabaram com o **mesmo `video.mp4`/`thumbnail.jpg` byte a byte** — remendo manual.
   - *Correção:* `media/render.py` agora detecta o filtro (`has_filter`); sem libass, grava `captions.srt` para subir como faixa separada e segue sem queimar. **Validado** (mock long + run real).

2. **Flag `--format shorts` não existia.**
   - *Evidência:* `CLAUDE.md` e os dois runbooks mandavam `python run.py video ... --format shorts`; o `argparse` não tinha `--format` → erro "unrecognized arguments".
   - *Correção:* `run.py` agora aceita `--format shorts|long` (padrão `shorts`), escolhe o config certo e ajusta a proporção no mock. **Validado.**

3. **Contrato de arquivos divergente (squad em `.md` × pipeline em `.json/.txt`).**
   - *Evidência:* os runbooks e o cristiano mandavam salvar `roteiro.md`, `cenas.md`, `metadados.md`; o `run.py`/`compliance.py` leem `roteiro.txt`, `cenas.json`, `metadados.json`. Resultado: `polarizacao-genz-boomers/` tem `cenas.md`/`metadados.md` que o pipeline **ignora** (regeraria por API paga) e o `compliance` lê vazio.
   - *Correção:* a squad agora emite os nomes canônicos; notas humanas vão para arquivos à parte (`revisao.md`, `roteiro_notas.md`, `direcao_viral.md`, `auditoria.md`). Atualizados: neymar, courtois, cristiano, olise, mbappe, os runbooks e o `CLAUDE.md`.

### P1 — autonomia e custo

4. **Orquestrador contradizia a autonomia e não podia renderizar.**
   - *Evidência:* `debruyne` dizia "Pare e pergunte antes de qualquer passo que gaste dinheiro, gere imagens ou rode `python run.py video`"; e suas ferramentas eram só `Agent, Read, Glob, Grep` (sem `Bash`).
   - *Correção:* `debruyne` reescrito: ganhou `Bash`, coordena de ponta a ponta **até `video.mp4` + auditoria APROVADO**, trata o pedido de "produza um vídeo" como autorização do fluxo gratuito, e só pausa por informação indispensável, conflito, gasto acima do orçamento ou publicação.

5. **Gasto não autorizado era possível/silencioso.**
   - *Correção:* `run.py` ganhou `--allow-paid` + `enforce_budget` (troca voz/imagem paga por gratuita e avisa) + `need_creative` (se um arquivo criativo falta e não há `--allow-paid`, **para com mensagem** em vez de chamar a API paga da Anthropic). Padrão = **R$0**. **Validado** (guard barra sem gastar).

6. **Provedor de imagem direto sem rede de segurança.**
   - *Evidência:* com `provider: cloudflare`, qualquer falha derrubava o vídeo inteiro (só `commons` tinha fallback).
   - *Correção:* `media/images.py` cai para `local_art` e avisa, garantindo que a produção termine com material aproveitável.

### P2 — consistência

7. **`agentes_para_instalar/` desatualizado** (sem `cristiano`, com `debruyne`/`olise` antigos) → sincronizado com `.claude/agents/`.
8. **Nicho errado nos configs** ("curiosidades históricas") → corrigido para "Análise de Comportamento Social e Gerações" nos dois configs.
9. **Sem configuração persistente do canal** (idioma, público, voz, formato, orçamento, destino, publicação) → adicionada em `CLAUDE.md` e refletida nos configs (`budget:`, `publish:`).

### Observações (não bloqueadores)
- **Sem `drawtext` tampouco** neste FFmpeg: **nenhum texto é queimado na imagem** nesta máquina (nem legenda nem overlay). Os overlays que o cristiano sugere na `direcao_viral.md` são orientação de edição; hoje só saem como `captions.srt` separado. Para queimar, instalar um FFmpeg com libass/freetype.
- Imagens do Commons **nunca foram testadas contra o Commons real** (documentado no README). Cloudflare Flux foi **confirmado funcionando** neste ambiente (ver §5).

---

## 3. Arquitetura proposta (implementada)

```
Guilherme: "produza um SHORT sobre X"
        │
        ▼
debruyne-orquestrador  ── coordena e acompanha até a entrega ──┐
  1 modric   → notas.md            (3+ fontes)                 │
  2 messi    → angulo.md           (tese, pergunta, análise)   │
  3 neymar   → roteiro.txt         (só narração, 30-60s)       │  squad (Claude Code), grátis
  4 courtois → roteiro.txt+revisao.md                          │
  5 cristiano→ roteiro.txt+roteiro_notas.md+direcao_viral.md   │
  6 olise    → cenas.json          (lê direcao_viral.md)       │
  7 mbappe   → metadados.json                                  ┘
  8 python run.py video --format shorts   → voz Kokoro + imagens + FFmpeg
        → video.mp4, thumbnail.jpg, PUBLICAR.txt, CONFORMIDADE.md, custo.json
  9 vini     → auditoria.md (APROVADO/BLOQUEADO)
        ▼
  entrega: vídeo + thumbnail + título(+alternativas) + metadados + roteiro/fontes + custo
  (upload no YouTube = manual, separado, só com autorização)
```

**Princípios:** um responsável final por entregável; a squad é o cérebro criativo e o `run.py` é a fábrica; `run.py` só gera por API paga como fallback explícito (`--allow-paid`); idempotência = checkpoint (reexecutar reaproveita e não recobra); nada vai ao ar sem o vini.

---

## 4. Contratos de entrada/saída (em `output/<slug>/`)

| Agente | Lê | Escreve (obrigatório) |
|---|---|---|
| modric | tema | `notas.md` |
| messi | notas.md | `angulo.md` |
| neymar | notas.md, angulo.md | `roteiro.txt` (só narração) |
| courtois | roteiro.txt, notas.md | `roteiro.txt` (corrigido), `revisao.md` |
| cristiano | roteiro.txt, notas.md, angulo.md | `roteiro.txt` (premium), `roteiro_notas.md`, `direcao_viral.md` |
| olise | roteiro.txt, direcao_viral.md | `cenas.json` (`text`, `search[3]`, `image_prompt`) |
| mbappe | roteiro.txt | `metadados.json` (`titulo`, `descricao` com `Fontes:` e aviso sintético, `tags`, `thumbnail_prompt`, `thumbnail_texto`) |
| run.py | os acima | `audio/`, `images/`, `video.mp4`, `thumbnail.jpg`, `captions.srt`, `PUBLICAR.txt`, `CONFORMIDADE.md`, `custo.json` |
| vini | tudo + CONFORMIDADE.md | `auditoria.md` (começa com APROVADO/BLOQUEADO) |

Regra de ouro: `roteiro.txt` é **só o texto narrado** (sem markdown/rubricas) porque o `run.py` o quebra em cenas frase a frase.

---

## 5. Alterações implementadas e validação

**Arquivos alterados:** `media/render.py` (detecção de libass), `run.py` (`--format`, `--allow-paid`, `enforce_budget`, `need_creative`), `media/images.py` (fallback para local_art), `config.yaml` e `config_shorts.yaml` (nicho real + `budget:`/`publish:`), `CLAUDE.md` (contrato, autonomia, config persistente), os 7 agentes da squad + `debruyne`, `vini`, os 2 runbooks em `.claude/prompts/`, `agentes_para_instalar/*` (sincronizado), `.claude/settings.local.json` (allowlist).

**Testes executados (nesta máquina):**
- `--mock --format long` (caminho que quebrava): completou; legenda caiu para `captions.srt`; `video.mp4` 1280×720, h264+aac. ✅
- `--mock --format shorts`: `video.mp4` 720×1280. ✅
- **Run real, $0, conteúdo real** ("Quem lucra com polarização Gen Z vs boomers"), reaproveitando os arquivos canônicos da squad: Kokoro (voz local) + Cloudflare Flux (imagens, **confirmado funcionando**, sem fallback) + FFmpeg. Saída: `video.mp4` **1080×1920**, 46,6s, h264+aac; `CONFORMIDADE.md` 8 OK / 1 atenção / 0 faltando; `custo.json` total **US$ 0,00**; ~61s de relógio. ✅
- Guard de gasto: tema novo sem `--allow-paid` **parou** pedindo a squad, sem chamar API paga. ✅

**Simulado/limitação:** nesta validação eu mesmo escrevi o `metadados.json` (papel do mbappe) a partir do rascunho `metadados.md` da squad, para testar a fábrica de ponta a ponta. Com os prompts atualizados, o mbappe passa a emitir o `metadados.json` direto.

---

## 6. Autorizações recorrentes resolvidas e bloqueios que restam

**Resolvido (persistente em `.claude/settings.local.json`):** `python run.py …`, `ffmpeg`, `ffprobe` liberados — o fluxo não pede "Allow" para eles.

**Obrigatórios da plataforma / humanos (por design, não removíveis):**
- **Upload no YouTube**: manual e separado; depende de autorização explícita.
- **Marcar conteúdo alterado/sintético** no upload quando imagens de IA parecerem reais (o `CONFORMIDADE.md` lembra).
- **Gastos**: qualquer etapa paga exige `--allow-paid` + sua autorização (voz Google, imagens fal, geração de texto pela API da Anthropic).
- **Chaves de API**: só no `.env`; nenhum agente lê ou expõe.

---

## Suposições registradas (secundárias, coerentes com o briefing)
- Orçamento padrão = **R$0** (só recursos gratuitos), porque nenhum teto foi definido e o pedido manda usar recursos sem custo.
- Provedor de imagem gratuito = **Cloudflare Flux** quando há `CF_ACCOUNT_ID`/`CF_API_TOKEN` (confirmado funcionando), senão `local_art` (demonstração).
- Voz = **Kokoro `pm_alex`** (pt-BR local). Troque em `tts.voice` e ouça com `python run.py voices` se quiser outra — a voz pesa muito na retenção.
- Formato padrão = **SHORT 9:16**, conforme o `CLAUDE.md`.
