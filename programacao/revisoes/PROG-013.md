# Revisão PROG-013 · Busquets · por Thiago Silva, 2026-11-05

**Veredito: APROVADO.**

Evidência: `testar_aprendiz.py` rodado agora, 50/50. Código lido: `inteligencia/aprendiz/rodar.py` e `preparar_video.py`.
- O `rodar.py` chama o Claude com `--tools` e `--disallowedTools` restritos, sem MCP e sem slash commands. Os tetos estão em `TETOS` e `TETO_DIA`, nas linhas 33-34 e 191/248. Só `subprocess` para o `claude` e o `ffmpeg`.
- Não há download (yt-dlp, urlopen, requests). O agente não tem Bash. `_entrada/` e `_trabalho/` estão no `.gitignore`.
- Relatório real `2026-11-05/rodada-1.md` confere com os critérios 4 a 8.
Ressalvas (já declaradas na entrega): nenhum vídeo de terceiro foi estudado; o teto real nunca foi atingido, só simulado; o Whisper erra palavras.
