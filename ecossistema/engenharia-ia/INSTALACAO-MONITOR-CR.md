# Maestro da sprint (`programacao/maestro.py`)

Substituiu o antigo `monitor_cr.py`. A cada 15 min chama o agente dono de cada coluna com cartão; ele age e grava a decisão em `programacao/maestro/decisoes/PROG-NNN.json`, e só o maestro move o cartão (quadro e Trello).

- Tarefa `ContextoExplica-Sprint`: a cada 15 min, só com a Sprint ABERTA e entre 07h e 23h.
- `python programacao/maestro.py --simular`: mostra o que chamaria, sem custo.
- `python programacao/maestro.py --forcar PROG-NNN`: chama o dono do cartão agora.
- Pausar: `Disable-ScheduledTask ContextoExplica-Sprint`.
- Limite diário de gasto e teto por chamada: constantes no topo do arquivo.
- Log: `programacao/maestro/log.md`.
- "Pronto para aceite" só vai a "Feito" com o aceite do Guilherme em `programacao/aceites/PROG-NNN.md`.
