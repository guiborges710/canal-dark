# Canal dark — pipeline de vídeo semi-automatizado

Entrega, para cada vídeo, uma pasta com `video.mp4`, `thumbnail.jpg` e `PUBLICAR.txt`
(título, descrição e tags prontos). **O upload no YouTube é manual.**

```
tema → pesquisa (Claude + busca web) → roteiro (Sonnet) → revisão (Haiku)
     → cenas + prompts de imagem (Haiku) → narração (Google TTS) → imagens (Flux)
     → edição (FFmpeg: zoom, legendas, música com ducking, volume normalizado)
     → título/descrição/tags/thumbnail → PUBLICAR.txt
```

## Instalação no Windows

1. Instale o **Python** em python.org (marque "Add python.exe to PATH").
2. Abra o terminal (PowerShell) e instale o **FFmpeg**: `winget install Gyan.FFmpeg`. Depois **feche e abra o terminal**.
3. Extraia esta pasta e dê dois cliques em **`setup_windows.bat`** (cria o ambiente e instala tudo).
4. Dê dois cliques em **`teste_simulado.bat`**: gera um vídeo de teste sem usar nenhuma chave nem gastar nada,
   e abre a pasta com o resultado.

Se preferir o terminal: `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`,
`copy .env.example .env`. Depois, os comandos abaixo funcionam com `python run.py ...`.

No Mac: `brew install ffmpeg`, `python3 -m venv .venv && source .venv/bin/activate`, `pip install -r requirements.txt`.

Se a legenda der problema no seu FFmpeg, ponha `render.captions: false` no `config.yaml`.

## Monetização e políticas do YouTube (leia antes de publicar)

Ninguém garante monetização: quem decide é o YouTube, que revisa o canal. O que o projeto faz é reduzir risco.
As regras abaixo vêm das páginas oficiais (links no fim do `CONFORMIDADE.md` de cada vídeo).

- **Conteúdo inautêntico (julho de 2025):** vídeos intercambiáveis, em molde repetido, "apresentações de imagens com comentário
  insignificante" ou conteúdo de IA genérico, sem ponto de vista próprio, não monetizam. **Este é o maior risco de um canal como este,
  maior que a qualidade das imagens.** Por isso o pipeline gera um `angulo.md` (tese, pergunta, ideias que uma busca rápida não mostra,
  comentário próprio) antes do roteiro, e o roteirista deve dedicar cerca de um terço do texto à análise.
- **Conteúdo reutilizado:** nada de trechos de vídeo, áudio ou texto de terceiros sem transformação. Imagens vêm só de fontes com
  licença livre, com crédito no `PUBLICAR.txt`; a trilha é sintética e própria.
- **Conteúdo sintético:** cenas realistas de um evento real que não foi registrado exigem a divulgação no upload. Imagens reais de
  arquivo e ilustrações claramente estilizadas evitam isso; geração por IA fotorrealista de eventos reais, não.
- **Temas sensíveis:** história e tragédias podem monetizar em tom educativo, sem detalhes gráficos nem exploração. Evite miniaturas gráficas.
- **Requisitos do canal:** 1.000 inscritos e 4.000 horas de exibição pública em vídeos longos em 12 meses (ou 10 milhões de visualizações
  de Shorts em 90 dias), sem avisos ativos, verificação em duas etapas e AdSense. Atingir os números não garante aprovação.
- **Cadência:** publicar em volume que uma equipe humana não faria é sinal de produção em massa. O verificador avisa acima de
  `compliance.max_videos_per_day`.

O `CONFORMIDADE.md` de cada vídeo reúne as verificações automáticas e a lista do que só você pode confirmar. A comparação de texto copiado
usa só o `notas.md`, não as páginas originais: ela ajuda, mas não substitui a sua leitura.

## Imagens reais de arquivo (Wikimedia Commons)

Com `images.provider: commons`, cada cena busca uma imagem real usando as consultas do campo `search` do `cenas.json`
(o agente de cenas as escreve). Só aceita domínio público, CC0 e CC BY; descarta NC, ND, marcadas como não livres, SVG e imagens pequenas,
e não repete imagens no mesmo vídeo. O crédito de cada uma vai para o `PUBLICAR.txt`. Onde não achar nada, usa `images.fallback`
(`local_art`, `cloudflare` ou `fal`). **Coloque o seu e-mail em `commons.user_agent` no `config.yaml`** (o Wikimedia pede um contato).

Limites desta versão: a lógica foi testada contra um servidor simulado, mas **não contra o Commons de verdade**, porque o ambiente onde
desenvolvi bloqueia o acesso. As buscas do exemplo do Krakatoa são palpites razoáveis e podem trazer pouca coisa; ajuste-as conforme
o que o Commons realmente tiver. O adaptador da Cloudflare também não foi testado.

## Modo 100% gratuito (sem nenhuma chave de API)

O `config.yaml` já vem com os provedores gratuitos ligados:

- `tts.provider: kokoro`: voz local (Kokoro, em português do Brasil: `pf_dora`, `pm_alex`, `pm_santa`), roda no seu computador.
- `images.provider: local_art`: arte gerada por código (`media/art.py`). **É uma demonstração**: silhuetas de vulcão, mar,
  mapa, relógio etc., guiadas por palavras-chave no prompt da cena. Não tem a qualidade nem a variedade do Flux.
- Pesquisa, roteiro, revisão, prompts de cena e metadados: neste modo, quem escreve é o Claude **no chat**, e os arquivos
  vão para a pasta do vídeo (`notas.md`, `roteiro.txt`, `cenas.json`, `metadados.json`). O pipeline reaproveita o que já existe.
- Trilha: `music/ambient.mp3` (ambiente sintético original, gerado com FFmpeg).

Para ver funcionando no Windows: instale com `setup_windows.bat` e dê dois cliques em **`video_gratis_exemplo.bat`**
(instala a voz local, baixa o modelo de ~120 MB e gera o vídeo de exemplo em `exemplo/`). A primeira geração leva alguns minutos.

Para voltar aos serviços pagos, troque `tts.provider` para `google` e `images.provider` para `fal` e preencha o `.env`.
A voz local fala um pouco rápido; se quiser mais calma, reduza `tts.speaking_rate` (por exemplo, 0.92).

## Chaves de API (no arquivo .env, nunca no chat)

| Variável | Onde obter |
|---|---|
| `ANTHROPIC_API_KEY` | console da Anthropic (cobrança por uso, separada da assinatura Pro) |
| `GOOGLE_TTS_API_KEY` | Google Cloud: ative "Cloud Text-to-Speech API" e crie uma chave de API |
| `YOUTUBE_API_KEY` | Google Cloud: ative "YouTube Data API v3" e crie uma chave (só para o comando `ideas`) |
| `FAL_KEY` | painel do fal.ai |

Restrinja cada chave de API ao serviço correspondente e defina um limite de gasto nos painéis.

## Ordem recomendada

1. **Teste sem custo:** `teste_simulado.bat` (ou `python run.py video --topic "teste" --mock`)
   Roda tudo com dados falsos e confirma que o FFmpeg e o encanamento funcionam na sua máquina.
2. **Escolha a voz:** `python run.py voices` lista as vozes do idioma. Ajuste `tts.voice` no `config.yaml`
   e ouça uma amostra antes de decidir. **Qualidade da voz é o fator que mais pesa na retenção.**
3. **Primeiro vídeo real, curto:** no `config.yaml` use `channel.minutes: 2` e rode
   `python run.py video --topic "seu tema"`. Confira o `custo.json` gerado.
4. **Ideias de pauta:** preencha `channel.niche` e `research.youtube_queries`, depois `python run.py ideas`.

Cada etapa salva seu resultado na pasta do vídeo. Se algo falhar, rode o mesmo comando de novo:
o que já foi gerado é reaproveitado (e não cobrado outra vez). Para refazer uma etapa, apague o arquivo dela.

## Onde ajustar

- `config.yaml`: nicho, idioma, duração, estilo visual, modelo de cada agente, voz, música, legendas.
- `prompts/*.md`: instruções de cada agente (pesquisa, roteiro, revisão, cenas, metadados).

## Limites desta versão (MVP)

- **Testado só no modo simulado.** As chamadas reais (Claude com busca web, Google TTS, fal.ai, YouTube Data API)
  seguem a documentação dos serviços, mas ainda não foram executadas. Espere pequenos ajustes no primeiro uso real.
- Legendas com tempo proporcional por cena (sem Whisper); funcionam bem, mas não são palavra a palavra.
- Thumbnail sem texto sobreposto (o texto sugerido vai no `PUBLICAR.txt`).
- Uma imagem por cena; sem clipes de vídeo por IA.
- O roteiro depende da qualidade das notas: leia o `roteiro.txt` antes de publicar.

## Antes de publicar (checkpoint humano)

Assista ao vídeo, confira fatos importantes e marque a divulgação de conteúdo alterado/sintético
no YouTube Studio quando for exigida.
