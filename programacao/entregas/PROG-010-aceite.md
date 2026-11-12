# Aceite · PROG-010

Data: 2026-11-03  
Responsável pelo aceite: **Zico**  
Veredito: **ACEITO**

## Resultado

O PROG-010 atende aos quatro critérios de aceite do backlog e à definição de pronto aplicável ao item. O instalador preserva agentes já existentes, instala somente arquivos novos e oferece o modo `/simular` sem escrita.

## Critérios de aceite

1. **PASSOU** — arquivo existente diferente não é substituído e recebe aviso explícito `[PRESERVADO]`.
2. **PASSOU** — não existe caminho de sobrescrita; por isso backup ou confirmação antes de sobrescrever não se aplica. A proteção adicional `copy /-Y` cobre o caso de o destino surgir entre a verificação e a cópia.
3. **PASSOU** — o teste isolado em pasta temporária comprova arquivo novo instalado, arquivo existente diferente preservado e modo `/simular` sem alteração.
4. **PASSOU** — a decisão do Guilherme de manter e corrigir o `.bat`, sem sobrescrita e com `/simular`, está registrada em `programacao/sprints/planning-2026-11-03.md`.

## Evidências da definição de pronto

- Entrega registrada em `programacao/entregas/PROG-010.md`.
- Teste automatizado novo em `programacao/qa/testar_instalar_agentes.py`.
- Bateria específica repetida no aceite: `.venv\Scripts\python.exe programacao\qa\testar_instalar_agentes.py` — **PASSOU**, código 0.
- Qualidade do diff: `git diff --check` nos arquivos do item e laudos — **PASSOU**, sem erro de whitespace; apenas aviso informativo de futura conversão LF para CRLF no `.bat`.
- Revisão técnica de **Thiago Silva** em `programacao/entregas/PROG-010-revisao.md` — **APROVADO**.
- QA final de **Alisson** em `programacao/qa/PROG-010.md` — **APROVADO**, com os quatro critérios atendidos e proteção das pastas reais confirmada por hashes.
- Baterias de Corte, pipeline e render: não se aplicam, pois o item altera apenas o instalador Windows e seu teste isolado.
- Documentação afetada: a decisão e o comportamento estão registrados no planning, na entrega, na revisão, no QA e neste aceite; nenhuma documentação de uso adicional foi exigida pelo escopo.
- Nenhum commit, push, publicação, alteração de branch, instalação de dependência ou uso de API paga foi realizado neste aceite.

## Decisão

**ACEITO.** O PROG-010 está feito segundo a definição do setor. O risco residual apontado por **Thiago Silva** sobre código de saída em falha operacional não viola os critérios atuais e pode ser tratado em item futuro.
