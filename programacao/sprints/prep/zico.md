# Pré-planning · visão do Zico (2026-11-03)

Backlog completo e critérios em `programacao/backlog.md` (PROG-001 a PROG-010). Quem decide a prioridade é o Guilherme.

## Lista priorizada
PC = pré-requisito de confiança; N = entrega nova.

| # | Id | Cartão | Classe | Valor | Justificativa |
|---|---|---|---|---|---|
| 1 | PROG-002 | "Iniciar cenas" não faz nada | PC | alto | Travava o Corte; atendido, falta validar. |
| 2 | PROG-001 | Etapa "não se aplica" sem motivo | PC | alto | Atendido, falta validar. |
| 3 | PROG-005 | Atualizar testes e2e antigos | PC | alto | Sem bateria confiável, nenhuma validação vale. |
| 4 | PROG-004 | Validar reserva com Codex | PC | médio | Feita e nunca testada; depende de decisão sobre "só Claude". |
| 5 | PROG-010 | Instalador sobrescreve agentes | N | alto | Risco de perda silenciosa; correção pequena. |
| 6 | PROG-009 | Player falha quando o Vini termina | N | médio | Bug conhecido; atrapalha revisar o vídeo. |
| 7 | PROG-006 | Tela mostra motor e nota | N | médio | Backend pronto; base do PROG-003. |
| 8 | PROG-003 | Aba Agentes em tempo real | N | médio | Grande; depois do PROG-006. |
| 9 | PROG-008 | Botão migrar execuções antigas | N | baixo | Só execuções velhas; dá para contornar. |
| 10 | PROG-007 | AGENTS.md defasado | N | baixo | Decisão do Guilherme, não de código. |

## Recomendação para a Sprint 01 (1 semana)
Meta: o Guilherme usa o Corte sem surpresa, com a bateria confiável.
- **Entra:** PROG-002, PROG-001 (só validação), PROG-005, PROG-004 (conforme a decisão), PROG-010 e PROG-009.
- **Fica de fora:** PROG-003 e PROG-006 (precisam de **Iniesta** e são o maior item), PROG-008 e PROG-007.
- **Cabe?** Sim, se o Guilherme reservar tempo para aceitar: os três primeiros são validação e teste, sem código novo grande. PROG-009 é o risco (causa desconhecida); se **Thiago Silva** estimar alto, ele sai primeiro. O gargalo é o tempo de aceite do Guilherme, não os devs. Estimativa de pontos é de **Thiago Silva**, na planning.

## As 3 perguntas que mais preciso ouvir
1. Você testou PROG-001 e PROG-002 hoje, e quanto tempo tem esta semana para testar e aceitar? Isso define o tamanho real da sprint.
2. O que está doendo no Corte que não está nesta lista? Algo pode passar na frente de PROG-005 a PROG-010?
3. Reserva com Codex e AGENTS.md: mantém, restringe ou remove, dado o "só Claude"? Isso decide PROG-004 e PROG-007.

Pergunta de apoio (se der tempo): o `instalar_agentes.bat` pode mudar ou sair? (PROG-010)
