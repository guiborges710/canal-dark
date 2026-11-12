# Trello: o que falta refletir (2026-11-11)

**Atualização após comentários do Guilherme:** ele removeu os bloqueios dos cards ativos. O PROG-032 já existe no Trello e os assets foram enviados; não criar cartão duplicado nem reaplicar a etiqueta **Bloqueado**. A validação local ainda aponta lacunas P0/P1.

Escrito por **Ancelotti**. Fonte do detalhe: `programacao/melhoria.md`, seção "Reestruturação por ordem do dono". Quem executa: a sessão principal, via `produtividade/trello_sync.py` / `kanban_programacao.py`. Regras: NUNCA apagar checklist, nunca apagar cartão; o maestro continua desligado.

Pré-requisito: o **Zico** grava os itens em `backlog.md` e o **Xavi** abre `sprints/sprint-02.md` e o `quadro.md`; só depois se espelha. Ids PROG-024 a PROG-035 são provisórios (Zico confirma).

## Cartões a mover
1. PROG-011 `[Sprint 01] [PROG-011]`: de "Backlog da sprint" para Backlog geral. Manter título, descrição e checklist; acrescentar comentário "devolvido em 2026-11-11: sprint 01 encerrada por ordem do dono; pausa de 05/11 mantida".
2. Cartões Feito da Sprint 01 (PROG-001, 002, 003, 004, 005, 006, 010, 012, 013, 014, 015, 016): ficam onde estão, sem mexer.

## Cartões da Sprint 02 (prefixo `[Sprint 02] [PROG-NNN] ...`; sem duplicar os existentes)
Posição atual observada no Trello em 11/11: PROG-024 e PROG-032 em "Pronto para fazer"; PROG-025 e PROG-026 em "Fazendo". Preservar essas posições manuais e atualizar prefixo/etiqueta sem sobrescrever os comentários.
1. PROG-024 Finanças no H (saldo, gastos, vencimentos, movimentos, alertas do Casemiro). Card existente. Resp.: Endrick, Rodrygo, Marquinhos; Firmino no visual. Checklist: 024a gerador local sem token (saída em pasta ignorada pelo git); regra de `.gitignore` conferida; 024b tela no H (saldo e por conta, receitas x gastos, categorias, vencimentos com texto e cor, movimentos, alertas, 390 px e 1280 px); critérios 1 a 7 do melhoria.md; teste com fixture; Alisson; Thiago Silva; aceite.
2. PROG-032 Assets do H (prioridade acelerada; card existente, sem etiqueta Bloqueado). Validar as reposições P0/P1 enviadas, integrar cada asset aprovado na casca e registrar o QA visual.
3. PROG-025 Casca do app H (8 grupos, tema, Ctrl K). Card existente; depende do 024b.
4. PROG-026 Servidor único: estender o Corte. Back-end. Card existente; refinamento técnico concluído; implementação e validação em andamento.
5. PROG-027 Espera você. Depende de 025 e 026.
6. PROG-028 Canal (inclui o cronograma do PROG-011 só leitura). Depende de 025 e 026.
7. PROG-029 Agentes no H (Ao vivo e Catálogo).
8. PROG-030 Editores de agentes e fluxos.
9. PROG-031 Console de jobs.
10. PROG-033 Clipes, Inteligência, Trabalho, Programação (fatiar a/b/c/d).
11. PROG-034 Acesso pelo celular.
12. PROG-035 Testes e2e do sistema único.
Em cada descrição: meta, história, critérios, responsável, tamanho (P/M/G), dependências, "Back-end: sim/não" e "Firmino participa" (itens 1 a 8, 10 e 11). Checklist de critérios em cada cartão, criado uma vez.

## Etiquetas
- "Sprint 02" nos 12 cartões; "Back-end" nos 026, 027, 028, 031, 033, 034; sem etiqueta "Bloqueado" no 032.
- PROG-018 a 023 (fora do quadro) e PROG-017: sem mudança.

## Decisões do Guilherme ainda necessárias
- Nenhuma decisão bloqueia os itens ativos: retomada da sprint e autorização de privacidade foram confirmadas; revisão visual da 024b recebeu retorno positivo.
- Acesso financeiro pelo celular permanece adiado até o PROG-034.
