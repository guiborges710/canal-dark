# Referências virais — acervo do canal

Biblioteca de inspiração do canal dark (nicho: **Análise de Comportamento Social e Gerações**).
Serve para o **Memphis** mapear o que viralizou e para o **Cristiano** extrair os padrões de
"o que viraliza / o que não" que alimentam os roteiros.

> **Importante:** os agentes são de texto — não assistem o vídeo. A análise sai dos
> **metadados, da transcrição e da capa** de cada referência, não dos pixels do vídeo.

## O que mora aqui

| Caminho | O que é | Versionado? |
|---|---|---|
| `referencias_nicho.md` | Lista curada de referências (nome, perfil, views, likes, link) + padrão observado. Entrega do **Memphis**. | ✅ sim |
| `analise_viral.md` | Leitura do acervo: ganchos, estruturas e sinais de retenção que funcionam no nosso nicho. Entrega do **Cristiano**. | ✅ sim |
| `transcricoes/<id>.txt` | Transcrição/legenda crua de cada vídeo (via yt-dlp). | ❌ gitignored (terceiros) |
| `capas/<id>.jpg` | Thumbnail da referência. | ❌ gitignored (terceiros) |
| `videos/` | (opcional) .mp4 pesado — hoje **não** baixamos, só transcrição+capa. | ❌ gitignored |

## Como adicionar uma referência (manual)

Rode na raiz do projeto, com o `.venv` ativo. Baixa só transcrição + capa + metadados (sem o vídeo):

```bash
.venv/bin/yt-dlp --skip-download \
  --write-info-json --write-thumbnail --convert-thumbnails jpg \
  --write-auto-subs --write-subs --sub-langs "pt.*,en.*" --sub-format "vtt/srt/best" \
  -o "referencias/transcricoes/%(id)s.%(ext)s" \
  "<URL_DO_SHORT_OU_REEL>"
```

Depois, registre a linha em `referencias_nicho.md` e avise o **Cristiano** pra reanalisar.

## Regras

- **Só inspiração de forma e ritmo** — nunca copiar texto, fatos ou ideias (política de conteúdo inautêntico).
- Números (views/likes) são coletados numa data e mudam: sempre anotar a **data da coleta** e nunca inventar ("n/d" quando a plataforma não expõe).
- Conteúdo de terceiros fica **fora do git** (ver `.gitignore`).
