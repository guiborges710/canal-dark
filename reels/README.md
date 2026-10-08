# Mini-fluxo de Reels (Instagram) — SEPARADO do canal do YouTube

Fluxo enxuto e barato para o **outro Instagram**. Não encosta em `run.py`, nos agentes,
prompts nem nos configs do canal. A diferença central: **as imagens vêm de FORA** (outra IA).
Aqui só geramos roteiro/cenas (no chat, custo zero de API) e montamos o vídeo.

Responsável: o agente **Dembelé** (`.claude/agents/dembele-reels-instagram.md`), que só
cuida deste mini-fluxo e não participa da squad do canal.

## Como funciona (2 estágios)

**Estágio 1 — conteúdo (feito pela squad no chat):**
Você passa o briefing já mastigado. A squad escreve e salva em `reels/projetos/<slug>/`:
- `cenas.json` — lista `[{ "text": "frase narrada", "image_prompt": "..." }]` (8–10 cenas).
- `prompt_imagens.txt` — **o prompt em lote**: um único texto com o estilo global + todas as
  8–10 imagens numeradas, pronto pra colar na sua outra IA.

**Estágio 2 — imagens (você):**
Cola o `prompt_imagens.txt` na outra IA, gera as imagens e salva em
`reels/projetos/<slug>/imagens/` — uma por cena, em ordem alfabética do nome
(`001.png`, `002.png`, …). Uma imagem por cena = sincronia exata com a narração.

**Estágio 3 — montagem (script, sem LLM):**
```bash
python reels/make_reel.py <slug>
```
Gera narração (Kokoro local, grátis), queima legendas estilo viral, mistura a música e
monta `reels/projetos/<slug>/reel.mp4` (9:16). O resto (postar) é manual.

## Comandos
```bash
python reels/make_reel.py novo <slug>    # cria a pasta do projeto (esqueleto)
python reels/make_reel.py <slug>         # monta o reel.mp4 (precisa das imagens)
python reels/make_reel.py <slug> --mock  # testa sem Kokoro nem imagens (placeholders)
python reels/make_reel.py --vozes        # lista as vozes do Kokoro
```

## Formato do prompt em lote (prompt_imagens.txt)
Cabeçalho com o estilo/consistência + bloco numerado por cena. Ex.:
```
ESTILO GLOBAL (aplicar a todas): fotorrealista, 9:16 vertical, iluminação suave, ...
Gere 9 imagens separadas, na ordem, nomeadas 001 a 009:

001 — <image_prompt da cena 1>
002 — <image_prompt da cena 2>
...
```

## Notas
- Números por extenso no `text` (a voz lê melhor).
- Reusa só os utilitários de mídia em `../media/` (ffmpeg/TTS/legenda) via import; não os modifica.
- Ajustes de voz/legenda/música ficam em `reels/config.yaml` (próprio deste mini-fluxo).
