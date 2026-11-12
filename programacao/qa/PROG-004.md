# QA PROG-004 · Validar a reserva com Codex (Alisson, 2026-11-04)

Executado: `.venv\Scripts\python.exe -X utf8 estudio\testes\testar_reserva_codex.py` (modo simulado, sem `--real`; não acionei o Codex real por regra de não gastar e pela memória "só Claude"). Resultado: "Tudo certo", exit 0.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Guilherme confirma o escopo por escrito e a decisão está em `tecnico/decisoes.md` | FALHOU | `grep Codex/reserva programacao/tecnico/decisoes.md` não retorna nada. A entrega cita a linha do `CLAUDE.md` (2026-11-03), mas o critério exige registro em decisoes.md. O quadro ainda lista isso como pendência do Guilherme. |
| 2 | Claude esgotado: reserva roda, `motor` = Codex, `motor_nota` preenchida | PASSOU (simulado) | testes de detecção de limite, comando `codex exec` e nota. O caso real é só reportado pelo **Rodrygo** (`--real`), não reproduzi. |
| 3 | Claude disponível: não aciona reserva | PASSOU | "NÃO é limite" para timeout, teto de custo, 429, créditos, erro de conteúdo |
| 4 | Falha da reserva dá erro legível sem derrubar | PASSOU | "sem Codex: falha original preservada e motivo anotado"; "Codex sem login: motivo claro" |
| 5 | Teste roda e resultado fica em qa | PASSOU | este arquivo |
| 6 | Se removida... | N/A | escopo mantido |

**Veredito (atualizado em 04/11): parte técnica APROVADA.** O critério 1 segue aberto: o D-005 está em `tecnico/decisoes.md` (apoiado no `CLAUDE.md`), mas falta o Guilherme confirmar por escrito. Revisão do **Thiago Silva** em `revisoes/PROG-004.md`: aprovado tecnicamente. O item fica **Bloqueado** até essa confirmação.
