# QA PROG-013 · Aprendiz de canais dark (Busquets) · por Alisson, 2026-11-05

**Veredito: APROVADO** (com ressalvas abaixo, nenhuma bloqueia).

Evidência de execução: `.venv/Scripts/python.exe -X utf8 estudio/testes/testar_aprendiz.py` → **50/50** (rodado agora; não chama o Claude). Relatório real lido: `inteligencia/aprendiz/2026-11-05/rodada-1.md`.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Agente em `.claude/agents/` com limites | PASSOU | `busquets-aprendiz-canais-dark.md`: tools Read/Write/Glob/Grep (sem Bash); testes "existe, sem Bash" e "limites escritos" ok |
| 2 | Roda quando chamado, sem agendamento, registra data e custo | PASSOU | `rodar.py aprendiz`; `historico.jsonl` tem quando/agente/custo (0,1634 e 0,1474); nenhum agendador no repo para ele |
| 3 | Limites 1–3 vídeos, US$0,30/rodada, US$1,10/dia; sem arquivo não chama o Claude | PASSOU | `rodar.py` linhas 32–34, 149, 191; testes "parou ao atingir o teto" e custo zero sem arquivo (simulados; teto real nunca atingido, ver ressalva) |
| 4 | Assiste com quadros e transcrição local | PASSOU | rodada-1: 12 quadros com tempo, cortes (6), fala transcrita |
| 5 | Sem arquivo: pede ao Guilherme, "não assistido", nada baixado | PASSOU | rodada-1 "Não assistidos" traz o caminho exato `_entrada/<id>.mp4`; teste "scripts não baixam vídeo" ok; sem yt-dlp/urlopen em `inteligencia/aprendiz/*.py` |
| 6 | Relatório datado com link, nível de acesso, trecho, quadros, o que NÃO foi visto | PASSOU | pasta `2026-11-05/`; link "não informado" porque é vídeo do canal próprio, declarado |
| 7 | Métodos com evidência + "como aplicar" coerente com CLAUDE.md | PASSOU | métodos com tempo (00:00…00:46); seção de aplicação fala em Short 9:16, nicho de gerações |
| 8 | Não copia roteiro | PASSOU | só 3 falas curtas citadas, como evidência |
| 9 | Direitos/termos; vídeos fora do git | PASSOU | `git check-ignore`: `_entrada/` e `_trabalho/` ignorados (.gitignore:25-26) |
| 10 | Sem credencial | PASSOU | agente sem terminal, pede só o arquivo; "nada de senha, cookie ou login" no relatório |
| 11 | Falha gera relatório legível sem derrubar rodadas | PASSOU | testes de falha/legibilidade do aprendiz e do curador ok |
| 12 | Teste de aceite: 1 vídeo com arquivo + 1 só com link | PASSOU | rodada-1 tem 1 estudado completo e 3 só com link marcados "não assistido" |

## Ressalvas (não bloqueiam)
- Nenhum vídeo de terceiro foi estudado de fato (nada foi baixado). Pessoa na câmera, outro idioma e vídeo longo nunca passaram pelo fluxo real.
- O corte pelo teto foi provado só com retorno simulado.
- O Whisper erra palavras (relatório avisa e não usa esses trechos).
- Autoria: feito pelo Claude Code, não por **Luiz Henrique**/**Rodrygo**; aceito por decisão do Guilherme registrada na entrega.

Nenhum bug novo.
