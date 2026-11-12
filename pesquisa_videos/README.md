# Setor de Pesquisa de vídeos longos

Alimenta o setor de Clipes (`clipes/`) com vídeos longos para cortar. Agente: **Pirlo** (`pirlo-pesquisador-videos`).

```
.venv\Scripts\python -m pesquisa_videos                                   # GTA 6: dia, semana e mês
.venv\Scripts\python -m pesquisa_videos --tema "gta 6" --min-minutos 20 --quantos 10 --regiao BR
```

Gera `saida/AAAA-MM-DD.md` (tabela por janela: views, minutos, canal, título, data, link) e `.json`. As janelas são as últimas 24 horas, 7 dias e 30 dias, ordenadas por visualizações, só vídeos de 20+ min.

- Usa a YouTube Data API (`YOUTUBE_API_KEY` no `.env`; cerca de 100 unidades de cota por busca, 3 por rodada).
- **Duas listas:** português (BR) e inglês. O idioma vem da busca e da língua declarada no vídeo; vídeo sem idioma declarado entra nas duas buscas conforme o resultado, então a lista em português pode ter menos de 10 na semana e no mês.
- **Só pesquisa.** O download e o corte são do setor de Clipes (`python -m clipes tudo <url> --autor "..." --autorizacao teste`).
