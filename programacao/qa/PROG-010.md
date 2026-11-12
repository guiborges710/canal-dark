# QA · PROG-010

Data: 2026-11-03  
Responsável: **Alisson**  
Veredito: **APROVADO**

## Pré-condições de QA

- **PASSOU** — o item pertence à Sprint 01 ativa e está em **Em teste**. Evidência: `programacao/quadro.md` lista o PROG-010 nessa coluna.
- **PASSOU** — existe entrega em `programacao/entregas/PROG-010.md`.
- **PASSOU** — a revisão de **Thiago Silva** está registrada em `programacao/entregas/PROG-010-revisao.md` com veredito **APROVADO**.

## Critérios de aceite

1. **PASSOU** — rodar o instalador não substitui agente existente diferente e emite aviso explícito. Evidência: `.venv\Scripts\python.exe programacao\qa\testar_instalar_agentes.py` terminou com código 0 e `OK PROG-010: simulação sem escrita; novo instalado; existente preservado.`; o teste mantém `trabalho atual` no destino embora a origem contenha `cópia antiga`, e o instalador informa `[PRESERVADO]`.
2. **PASSOU** — não há caminho de sobrescrita, portanto backup ou confirmação antes de sobrescrever não se aplica: todo destino existente é preservado. Evidência: inspeção de `instalar_agentes.bat`; `copy /-Y` só é executado no ramo de arquivo inexistente e acrescenta proteção caso o destino passe a existir entre a verificação e a cópia.
3. **PASSOU** — teste em pasta temporária comprova arquivo novo instalado e arquivo existente diferente preservado. Evidência: `programacao/qa/testar_instalar_agentes.py` usa `tempfile.TemporaryDirectory`, copia o instalador para a caixa isolada e a execução acima passou; hashes SHA-256 da árvore real `.claude/agents` foram comparados antes e depois, com 39 arquivos em ambos e `REAL_AGENT_TREE_UNCHANGED=True`.
4. **PASSOU** — a decisão do Guilherme está registrada. Evidência: `programacao/sprints/planning-2026-11-03.md` registra que o instalador deve nunca sobrescrever e deve oferecer o modo `/simular`.

## Regressão relevante

- **PASSOU** — `.venv\Scripts\python.exe programacao\qa\testar_instalar_agentes.py`: código 0; simulação sem escrita, arquivo novo instalado e existente preservado.
- **PASSOU** — proteção das pastas reais: 39 arquivos antes e depois da bateria; hashes SHA-256 sem diferença.
- **PASSOU** — `git diff --check -- instalar_agentes.bat programacao/qa/testar_instalar_agentes.py programacao/entregas/PROG-010.md programacao/entregas/PROG-010-revisao.md`: código 0, sem erro de whitespace; apenas aviso informativo de futura conversão LF para CRLF no `.bat`.
- **NÃO SE APLICA** — baterias de `estudio/`, `media/`, `render/` e `run.py`: o item altera somente o instalador Windows e seu teste isolado, sem tocar esses módulos.

## Veredito final

**APROVADO.** Nenhum critério falhou. O PROG-010 pode seguir para o aceite técnico de **Zico**. Nenhum código de produção, quadro, backlog ou branch foi alterado por **Alisson**.
