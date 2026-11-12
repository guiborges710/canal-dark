# Entrega PROG-013 · Aprendiz de canais dark (**Busquets**)

Feito em 2026-11-05 pelo Claude Code, a pedido direto do Guilherme, no lugar de **Rodrygo** e **Luiz Henrique**. Os critérios foram ajustados pelas decisões dele no mesmo dia (`programacao/backlog.md`): vídeos só por arquivo que ele subir, e nada agendado.

## Arquivos
- `.claude/agents/busquets-aprendiz-canais-dark.md` (sem Bash; só lê e grava)
- `inteligencia/aprendiz/rodar.py`, `preparar_video.py`, `README.md`, `fila.md`, `estudados.md`, `historico.jsonl`, `_entrada/LEIA-ME.txt`
- `estudio/testes/testar_aprendiz.py`
- `.gitignore`, `inteligencia/README.md`, `ecossistema/README.md`, espelho `.codex/`

## Evidência real
- `.venv/Scripts/python.exe -X utf8 estudio/testes/testar_aprendiz.py`: **50/50** (não chama o Claude).
- Rodada real: `inteligencia/aprendiz/2026-11-05/rodada-1.md`. Um vídeo com arquivo (`canal-proprio-jovens-bebendo-menos`, 46,8 s, 12 quadros, 6 cortes, transcrição) e três links sem arquivo, marcados "não assistido" com o caminho onde colocar. Custo US$ 0,15, teto US$ 0,30.
- Corrigido durante o teste: o limiar de corte de 0,30 achava 0 cortes no nosso sketch, que tem 6 (7 cenas em `cenas.json`), e o relatório concluía errado. Agora é 0,05, com teste de regressão. A rodada foi refeita.

## O que NÃO foi testado
- Nenhum vídeo de terceiro foi estudado: o vídeo com arquivo é do nosso próprio canal, porque nada é baixado sem o Guilherme subir. Vídeo com pessoa na câmera, em outro idioma ou com mais de 10 minutos não passou pelo fluxo real.
- O corte pelo teto do Claude Code (`error_max_budget_usd`) foi testado só com retorno simulado: nenhuma execução real chegou ao teto.
- O Whisper erra palavras (ex.: "a agência" em 00:00, em vez de "Gen Z"): a fala é aproximada.
