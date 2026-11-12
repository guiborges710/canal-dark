# Métricas do canal próprio (Yuri Alberto)

## Rodar todo dia (mesmo horário)
`.venv/Scripts/python.exe inteligencia/coletar_metricas.py`

Só lê o canal. Acrescenta linhas; nunca apaga. Sem o token do Analytics, coleta o público e avisa o que faltou.

## O que é coletado

| Arquivo | Conteúdo | Depende de |
|---|---|---|
| `videos.csv` | slug, video_id, título, publicação, duração, views, curtidas, comentários, **privacidade atual**, data da coleta (uma linha por vídeo por coleta) | token de upload (`.youtube_token.json`) |
| `analytics_videos.csv` | por vídeo, desde a publicação mais antiga: views, minutos assistidos, duração média, **retenção média (%)**, **inscritos ganhos**, impressões e **CTR** | token do Analytics |
| `analytics_trafego.csv` | views e minutos por vídeo e **fonte de tráfego** (busca, sugeridos, Shorts, externo...). Uma chamada por vídeo (`dimensions=insightTrafficSourceType` + `filters=video==ID`); a API recusa `video` + fonte juntos. Vídeo sem views é pulado | token do Analytics |
| `ctr_manual.csv` | impressões e CTR copiados **à mão** do Studio (Análise > Alcance); o coletor junta em `analytics_videos.csv` | à mão |
| `slugs_manuais.csv` | video_id -> slug dos vídeos sem `output/<slug>/upload.json` (conferir com o Guilherme) | à mão |

O slug vem de `output/<slug>/upload.json` (só leitura); `slugs_manuais.csv` é o reserva.

## O que depende do consentimento
1. Habilitar a **YouTube Analytics API** no mesmo projeto do Google Cloud do `client_secret.json` (APIs e serviços > Biblioteca > "YouTube Analytics API" > Ativar). A YouTube Data API v3 já está ativa.
2. Rodar uma vez, com o Guilherme logado na conta do canal: `.venv/Scripts/python.exe inteligencia/coletar_metricas.py --autorizar-analytics`. Imprime um link; abrir no navegador e autorizar `yt-analytics.readonly`. O token vai para `.youtube_analytics_token.json`, **separado** do de upload (que expira a cada 7 dias se o app estiver em modo teste; o do Analytics sofre o mesmo, então a autorização pode precisar ser repetida enquanto o app não for publicado).
3. Conferir que `.youtube_analytics_token.json` está no `.gitignore` (hoje NÃO está; ver relatório).

## Limites conhecidos
- A API não aceita impressões/CTR para este canal; o coletor não pede mais. Use `ctr_manual.csv`.
- Vídeos privados aparecem no `videos.csv` (coluna `privacidade`); views de privado não são desempenho.
- Os dados do Analytics têm atraso de cerca de 2 dias.
- Não rodar duas vezes no mesmo minuto: duplica linhas.

## Registrar impressões e CTR à mão
Studio > Análise > Alcance (do vídeo, ou do canal filtrando por vídeo): anote impressões e CTR do período. Acrescente uma linha em `ctr_manual.csv` (cabeçalho: `video_id,slug,data,impressoes,ctr_pct,fonte`). Exemplo (linhas começando com `#` são ignoradas):

```
# G97IVsiHtAs,geracao-z-nao-quer-filhos-ou-nao-pode-ter,2026-11-02,1200,4.8,studio
```

`ctr_pct` em número (4.8 = 4,8%), `fonte` sempre `studio`. Para o mesmo video_id vale a última linha do arquivo; use a data para saber de quando é o número. Na próxima coleta os valores entram nas colunas `impressoes` e `ctr_impressoes_pct`.
