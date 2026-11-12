# Sprint 01

Dono: **Xavi**. Estado: **ENCERRADA em 2026-11-11** (encerramento antecipado; motivo: ordem do Guilherme, mudança de prioridade; planejada para 03/11 a 17/11/2026). Sucessora: `programacao/sprints/sprint-02.md`. Histórico abaixo preservado.

Estado anterior: ABERTA (03/11 a 17/11/2026). Aberta em 2026-11-03, a pedido do Guilherme ("abre a sprint"); hora exata: não registrada (o relógio não foi consultado, pois nada foi rodado). Planning feita em 2026-11-03; ata em `programacao/sprints/planning-2026-11-03.md`. Daily do dia 1: `programacao/sprints/daily-2026-11-03.md`.

## Meta
Fechar e validar o que foi mexido no Corte (PROG-001, PROG-002 e a reserva com Codex, PROG-004), deixar a bateria de testes confiável (PROG-005) e entregar a aba Agentes "Ao vivo" (PROG-003 com PROG-006) com status automático dos vídeos (PROG-012) e sugestão de horário de postagem (PROG-011). Meta herdada da planning; o Guilherme abriu a sprint sem alterá-la.

## Aceites marcados com o Guilherme (1 h cada)
- Semana 1: quinta 2026-11-06.
- Semana 2: sexta 2026-11-14.
- Folga: 2026-11-16 (domingo), antes do fecho em 2026-11-17 (review e retro).

## Duração e capacidade
- 2 semanas: 2026-11-03 a 2026-11-17.
- Equipe: **Rodrygo** (back), **Endrick** (front), **Iniesta** (UX), **Alisson** (QA), **Marquinhos** (DevOps), **Thiago Silva** (tech lead). Apoio: **Zico** (PO), **Xavi**.
- Pontos: sem histórico de velocidade (primeira sprint); esforço em P/M/G conforme `prep/thiago-silva.md`.
- Aceite do Guilherme (gargalo): 1 h duas vezes por semana, quinta da semana 1 (2026-11-06) e sexta da semana 2 (2026-11-14), deixando um dia de folga antes de 17/11.
- Itens só técnicos (PROG-005, PROG-010, PROG-004 e testes): aceite do **Zico** pelo relatório do **Alisson**.

## Regras de WIP
- Máximo 2 itens em Fazendo por dev.
- Máximo 3 itens em Em teste no total.
- Item só vai para Feito com a definição de pronto de `programacao/README.md`.
- Nenhum commit, publish ou gasto com API paga sem o Guilherme pedir. O **Alisson** roda baterias (mock) e `validar_real.py` (render real, sem API paga) por autorização do Guilherme.

## Itens comprometidos (ordem)
1. PROG-001 e PROG-002: validar (Em teste). **Alisson**.
2. PROG-012: status automático de cada vídeo (arquivos existentes; regra única em `tecnico/decisoes.md`; um teste por estado). Vem antes do 011.
3. PROG-011: cronograma de postagem (só sugere; nunca reordena `output/fila_postagem.txt`; tela leve só de leitura, proposta do **Iniesta**).
4. PROG-004: validar a reserva com Codex (Codex fica como reserva; `AGENTS.md` só avisa para ler o `CLAUDE.md`).
5. PROG-005: atualizar testes e2e antigos.
6. PROG-010: instalador `.bat` que nunca sobrescreve, com modo `/simular`.
7. PROG-003 + PROG-006: aba Agentes desenho B, em duas entregas (Ao vivo, depois Catálogo; se faltar tempo, perde-se o Catálogo).

## Sequência
- Semana 1: **Rodrygo** PROG-001/002, PROG-004, PROG-005. **Endrick** PROG-010 e a aba Agentes.
- Semana 2: **Rodrygo** PROG-003+006 e a base do PROG-012. **Endrick** a tela do PROG-011.
- **Thiago Silva** fixa o contrato da API da aba Agentes antes de o **Endrick** consumir.

## Riscos
- Aceite do Guilherme é o gargalo (2 h por semana no total).
- PROG-005 pode revelar falhas reais escondidas atrás dos testes velhos.
- PROG-003 e PROG-006 tocam os mesmos arquivos de front que PROG-011: sequenciar para evitar colisão entre **Endrick** e **Rodrygo**.
- PROG-004 depende do binário `codex` e do login; regex de limite do Claude é frágil.
- Catálogo (PROG-003, entrega 2) é o item que cai se faltar tempo.
- Regra de horários do PROG-011 ainda depende do Guilherme.

## Atualização de escopo · 2026-11-09
Por decisão do Guilherme ("bora fazer a 016"), o PROG-016 (Aba Agentes: Catálogo e indicador ocioso; **Iniesta** desenho, **Endrick** tela, **Rodrygo** dados) entra na Sprint 01 como prioridade, no topo do Backlog da sprint. É a entrega 2 do PROG-003, que foi aceito em 05/11. PROG-011 segue pausado. Antes de puxar para Fazendo, o refinamento técnico é do **Thiago Silva**. Risco: capacidade até 17/11 e aceite do Guilherme (próximo marcado: sexta 14/11).

## Fora da sprint
PROG-007 (volta ao Backlog geral), PROG-008, PROG-009. PROG-013 e PROG-014 entraram na sprint a pedido do Guilherme em 05/11.

## Pendência
Tarefa agendada ContextoExplica-Trello: o Guilherme precisa pausá-la antes das baterias do **Alisson** (apoio: **Marquinhos**). Nada foi pausado até agora.

## Atualização de prioridade · 2026-11-03
Por pedido do Guilherme, o PROG-015 entrou como primeiro item da fila da Sprint 01: a ação da próxima etapa precisa cumprir o que o botão promete e mostrar o resultado verificável. O refinamento técnico confirmou o desvio entre rótulo e ação; a implementação começou a pedido do Guilherme. A adição excede o compromisso de capacidade original; reavaliar PROG-011 e o escopo do Catálogo (PROG-003) antes de puxar novos itens.

## Retomada · 2026-11-03
O Guilherme priorizou corrigir o CTA do topo após baixar o vídeo de companhias de IA. O defeito foi reproduzido no fluxo: “Iniciar vídeo final” chamava apenas a navegação. PROG-015 está em implementação pelo Codex a pedido do Guilherme; manter PROG-011/Catálogo sob reavaliação de capacidade.

## Início (dia 1, 2026-11-03)
Em Fazendo: PROG-004 (**Rodrygo**), PROG-005 (**Rodrygo** + **Alisson**), PROG-010 (**Endrick**, com **Marquinhos**). Em Em teste: PROG-001 e PROG-002. Backlog da sprint, nesta ordem: PROG-012, PROG-011, PROG-003+006.

## Resultado (fechamento em 2026-11-11)
- Encerrada por ordem do Guilherme (mudança de prioridade: sistema único, visual H). Não foi descarte.
- **12 itens Feito e entregues**, com aceite e release (`release/notas-sprint-01.md`): PROG-001, 002, 003, 004, 005, 006, 010, 012, 013, 014, 015, 016.
- **1 item devolvido:** PROG-011 (cronograma de postagem) volta ao Backlog geral, intacto (texto, critérios e nota de pausa de 05/11 preservados). Anotação: "devolvido em 2026-11-11 (sprint encerrada); sugestão: reabsorver no item Canal (PROG-028) da Sprint 02, só leitura".
- Em Fazendo, Code Review e Em teste: 0. Nenhum cartão parado.
- PROG-017 e PROG-018 a 023 seguem fora do quadro, sem mudança.
- Impedimentos herdados: PROG-004 `--real` (Codex sem cota, destrava sozinho); horários do PROG-011 (Guilherme).
- Nada apagado; checklists preservados.

## Pontos da retro
Retro curta no lugar da de 17/11 (o **Ancelotti** registra a melhoria a testar):
- Foi bem: 12 entregas em 8 dias úteis, com aceite; nenhum cartão acumulado em teste ao encerrar.
- Atenção: itens adicionados fora da planning (PROG-013 a 016) excederam o compromisso original; retrabalho e bugs escapados não medidos (contar em `qa/` e `revisoes/`).
- Hipótese "terminar antes de começar": fecha com o quadro de hoje (0 em andamento ao encerrar). Leitura numérica: a preencher pelo **Ancelotti**.
- Lição para a Sprint 02: compromisso firme menor que o previsto, e mudança de prioridade do dono entra declarada na planning.
