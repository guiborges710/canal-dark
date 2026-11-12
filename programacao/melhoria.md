# Melhoria de processo

Dono: **Ancelotti** (`ancelotti-agile-coach`). Formato: observação, hipótese, como medir, resultado, decisão. Uma hipótese por vez. Propostas de mudança no README do setor passam por **Luiz Henrique**, com aval do Guilherme.

## Sprint 01 · Observação do início (2026-11-03, dia 1)

Fontes lidas: `quadro.md`, `sprints/sprint-01.md`, `planning-2026-11-03.md`, `daily-2026-11-03.md`, `backlog.md`, entregas e QA do PROG-010. Nada foi rodado nem alterado fora deste arquivo.

### Linha de base (dia 1)
| Métrica | Valor |
|---|---|
| Itens comprometidos na planning | 9 (7 linhas de escopo) |
| Itens Feito | 1 (PROG-010, passou por Endrick, Thiago Silva, Alisson e Zico no mesmo dia) |
| Itens Em teste | 2 (PROG-001, PROG-002), ambos "atendidos" antes da sprint e ainda sem validação do **Alisson** |
| Itens Fazendo | 3 (PROG-004, PROG-005, PROG-015) |
| Itens adicionados depois da planning | 1 (PROG-015, a pedido do Guilherme; fora da capacidade) |
| Retrabalho (devolvido por **Alisson** ou recusado por **Zico**) | 0 |
| Bugs escapados | não medido ainda |
| Lead time | PROG-010: menos de 1 dia (única amostra) |

### O que funcionou
- PROG-010 mostrou o fluxo completo funcionando: refino, código, revisão do **Thiago Silva**, QA do **Alisson** com hashes da árvore real, aceite do **Zico** com evidência por critério. Bom modelo de referência.
- O risco residual do PROG-010 (código de saída em falha) foi dito de forma explícita e não bloqueou o aceite.
- Decisões da planning ficaram numeradas e rastreáveis na ata.

### O que atrapalha (observações)
1. **Trabalho começado, validação parada.** PROG-001 e PROG-002 estão Em teste desde antes da sprint, e a validação depende de PROG-005 (regressão confiável) e da pausa da tarefa do Trello, que depende do Guilherme. Enquanto isso, entram itens novos em Fazendo. Fluxo empurra, não puxa.
2. **Impedimentos que só o Guilherme destrava** (pausar tarefa do Trello, chat id do Telegram, regra de horários do PROG-011) estão abertos desde o dia 1, e o primeiro bloqueia a validação do **Alisson**. É o gargalo real, junto das duas janelas de 1 h de aceite.
3. **Capacidade excedida no dia 1.** PROG-015 entrou antes da fila e a própria sprint reconhece que excede o compromisso. A reavaliação de PROG-011 e do Catálogo está escrita como "reavaliar", sem dono nem data.
4. **Duração ambígua.** `programacao/README.md` diz sprint de 1 semana (a combinar); a Sprint 01 foi aberta com 2 semanas (03/11 a 17/11). A planning decidiu 2 semanas, mas o contrato não foi atualizado.
5. **Rastro desatualizado.** `sprint-01.md` ("Início") ainda lista PROG-010 em Fazendo e a ata diz "sprint ainda NÃO aberta"; o quadro já mostra PROG-010 Feito e a sprint aberta. A fonte única é o quadro, mas os dois textos induzem a erro quem lê só a sprint.
6. **Itens "atendidos" sem teste do critério antes de entrar em teste.** PROG-001 e PROG-002 foram para Em teste antes de existir bateria confiável (PROG-005 corrige exatamente isso). O **Alisson** pode validar contra um teste que ele próprio ainda não pode confiar.
7. **Execução fora da equipe prevista.** PROG-015 está com Codex, por pedido explícito do Guilherme, fora da contagem por dev. Não há problema de regra (exceção registrada), mas o item escapa do WIP e do fluxo de revisão/QA se ninguém garantir as mesmas etapas.

### Hipótese de melhoria (a testar nesta sprint, uma só)
**"Terminar antes de começar": nenhum item novo entra em Fazendo enquanto houver item Em teste parado há mais de 1 dia útil sem parecer do Alisson, ou enquanto houver item Em teste sem impedimento registrado.** Em outras palavras: a ordem de puxada passa a ser Em teste, depois Fazendo, depois Backlog da sprint. Quando o gargalo for o Guilherme, o **Xavi** registra o impedimento no quadro com a data e pede o destrave via **Ronaldo**, em vez de abrir mais um item.

- **Por que esta e não outra:** ataca as observações 1, 2, 3 e 6 juntas e não exige código nem mudança de contrato.
- **Quem aplica:** **Xavi** (quadro e puxada); **Zico** (não pede furar a fila sem registrar o trade-off); **Alisson** (parecer em até 1 dia útil ou impedimento escrito).
- **Como medir (simples, direto do quadro e das ata/daily):**
  - Idade de cada cartão em Em teste: meta de no máximo 1 dia útil sem parecer, ou com impedimento registrado.
  - Itens Feito ao fim da sprint em relação aos comprometidos (hoje 1 de 9).
  - Itens adicionados fora da planning: meta de no máximo 1 e com troca declarada (o que sai).
  - Retrabalho: itens devolvidos pelo **Alisson** ou recusados pelo **Zico** (linha de base 0).
- **Sucesso:** na retro de 17/11, nenhum cartão ficou mais de 1 dia útil parado em Em teste sem impedimento, e Feito/comprometido é maior que na primeira semana (comparar a daily de 06/11 com a de 14/11). Fracasso: cartões continuam parados por falta de destrave; nesse caso o problema é o aceite do Guilherme, não o método, e a hipótese seguinte vai para ele (ver pendente 1).
- **Resultado:** (preencher na retro)
- **Decisão:** (preencher na retro)

### Propostas de fluxo (sem teste ainda; vão para decisão do **Xavi** e do Guilherme)
1. **Impedimentos do Guilherme em um lote só.** Um único recado diário com os destraves pendentes e o custo de cada um em itens parados (hoje o recado já existe no quadro; falta ligar impedimento a item bloqueado). Quem leva: **Xavi** via **Ronaldo**.
2. **Alinhar a duração da sprint no contrato.** Decidir com o Guilherme se o padrão é 1 ou 2 semanas e deixar `programacao/README.md` coerente (**Luiz Henrique** edita). Se for 2 semanas, ajustar a cadência de daily e review.
3. **Nova entrada na sprint = troca declarada.** Item novo (como o PROG-015) só entra dizendo o que sai ou adia, na hora, no quadro e na ata. Evita "reavaliar" sem dono.
4. **Execução por Codex segue o mesmo caminho.** Mesmo quando o item é feito fora de **Rodrygo** e **Endrick**, mantém-se: teste primeiro, entrega em `entregas/`, revisão do **Thiago Silva**, QA do **Alisson**, aceite do **Zico**. Contar o item no WIP do setor (hoje fora da contagem por dev).
5. **Quadro e sprint com uma fonte.** `sprint-01.md` deveria apontar para o quadro nas partes que mudam todo dia (colunas) e guardar só meta, compromisso e decisões, para não ficar desatualizado.

### Sugestões para a definição de pronto (propostas; mudança no README só por **Luiz Henrique** com aval do Guilherme)
Base: itens 1 a 8 atuais do README. Nada é retirado.
1. **Bug corrigido exige teste que falha sem a correção.** Hoje o item (2) pede "teste novo ou ajustado". Para bugs (PROG-001, PROG-002, PROG-015), exigir que o relatório mostre o teste falhando antes e passando depois. O PROG-002 já pede isso nos critérios; vale generalizar.
2. **Risco residual vira cartão ou nota no backlog.** O PROG-010 deixou um risco (código de saída em falha) apenas dentro do documento de revisão. Proposta: todo risco residual aceito entra como linha em `backlog.md` (o **Zico** decide a prioridade), para não se perder.
3. **Evidência rastreável no cartão.** Reforço do item (7): o cartão do Trello aponta para os arquivos `entregas/<id>.md`, `qa/<id>.md` e o aceite, com o comando e o resultado real da bateria. O PROG-010 já faz isso; virar padrão.
4. **Escopo de bateria declarado.** O **Alisson** e o aceite escreveram "não se aplica" para baterias não relevantes, com motivo. Padronizar: toda entrega lista baterias aplicáveis, as não aplicáveis e o porquê.
5. **Validação do que depende do Guilherme é marcada.** Itens que só o Guilherme pode aceitar (visuais, de celular) carregam a marca "aceite do Guilherme" desde a planning; os demais seguem o caminho técnico do **Zico**. Já foi acertado para itens técnicos; falta marcar o outro lado nos cartões.

### Ação urgente (2026-11-03, noite) · Endrick puxa PROG-012; nada é pausado

**Observação.** O quadro mostra 3 itens em Fazendo (PROG-015, PROG-004, PROG-005), não 5. O limite do README é 2 por dev: **Rodrygo** 2/2, **Endrick** 0/2, PROG-015 com Codex fora da contagem. O problema é a distribuição, não o total: **Rodrygo** está cheio e **Endrick** está parado esperando contrato do **Thiago Silva**.

**Hipótese (uma só).** Pausar PROG-004 não é o corte mais rápido. Ele libera **Rodrygo**, mas **Endrick** já está livre e não pega PROG-012 por falta de refino, não por falta de vaga. Além disso PROG-004 valida justamente a reserva com Codex. Corte proposto: manter os 3 em Fazendo, e pedir ao **Thiago Silva** o contrato mínimo do PROG-012 para **Endrick** puxar hoje (1 item, 1/2). **Rodrygo** não puxa nada novo até PROG-004 ou PROG-005 irem para Em teste. Quem decide a ordem é o **Zico**; o **Xavi** aplica.

**Fluxo ideal para Codex (PROG-004 e PROG-015), quando o Claude esgotar os tokens.**
1. Cartão não muda de coluna por troca de motor. Continua em Fazendo, com a nota "motor: Codex desde <data/hora>, motivo: limite do Claude". O **Xavi** registra; o dono original (**Rodrygo** no PROG-004) continua responsável pelo item.
2. Codex conta no WIP: PROG-015 e PROG-004 contam como 1 cada na contagem do dev dono. Hoje PROG-015 fica fora; passar a contar evita estouro escondido.
3. Contrato de entrega igual ao do Claude: teste que falha antes e passa depois, relatório em `programacao/entregas/<id>.md` com o motor usado, revisão do **Thiago Silva**, QA do **Alisson**, aceite do **Zico**. Sem exceção por ser Codex.
4. Passagem de bastão: ao trocar de motor, quem para escreve no relatório do item o que foi feito, o que falta e o último comando rodado. Codex não recomeça do zero.
5. Retorno ao Claude: só quando o limite renovar e entre itens, nunca no meio de um item.
6. Codex não toca em backlog nem em quadro; só em código e entrega do item que tem cartão em Fazendo.
Proposta de mudança no README do setor (se o Guilherme concordar): **Luiz Henrique**.

**Métricas de sucesso (leitura do quadro na daily de 06/11 e na retro de 17/11).**
| Métrica | Linha de base | Meta |
|---|---|---|
| Feito/comprometido | 1/9 | maior na daily de 14/11 do que na de 06/11; ideal 6/9 ou mais ao fim |
| Lead time (Fazendo até Feito) | PROG-010: menos de 1 dia | mediana de até 3 dias úteis |
| Retrabalho (devolvidos pelo **Alisson** ou recusados pelo **Zico**) | 0 | continua 0 |
| **Endrick** em Fazendo | 0/2 | pelo menos 1/2 até a daily de 04/11 |
| Itens com motor Codex sem relatório de passagem | n/a | 0 |

**Risco.** (1) **Thiago Silva** não entregar o contrato do PROG-012 e **Endrick** continuar parado; nesse caso o gargalo é refino e a ação vai para o **Zico**. (2) Pausa do Trello não feita pelo Guilherme segura PROG-001, 002 e 005 e derruba Feito/comprometido, independentemente do método. (3) Codex pegar item sem passagem de bastão e gerar retrabalho.

- **Resultado:** (preencher na daily de 04/11 e na retro)
- **Decisão:** (preencher na retro)

### Reestruturação por ordem do dono · 2026-11-11 (PROPOSTA; quem grava backlog, quadro e sprint é o Zico/Xavi)

**Estado lido hoje.** Sprint 01 (03/11 a 17/11): 12 itens Feito (PROG-001, 002, 003, 004, 005, 006, 010, 012, 013, 014, 015, 016), 0 em Fazendo/Em teste/Code Review, 1 item restante no Backlog da sprint: PROG-011 (pausado pelo Guilherme em 05/11). PROG-018 a 023 rodam fora do quadro (autorização de 09/11). Ou seja, "cancelar" a Sprint 01 hoje custa um único cartão devolvido; é um encerramento antecipado, não um descarte. Retrabalho na sprint: não medido aqui (conferir em `qa/` e `revisoes/` na retro).

**Como encerrar sem destruir (para o Zico e o Xavi aplicarem).**
1. `sprint-01.md`: estado ENCERRADA em 2026-11-11, motivo "ordem do Guilherme, mudança de prioridade"; preencher Resultado (12 Feito, 1 devolvido) e Pontos da retro. Nada apagado.
2. PROG-011: volta ao Backlog geral com texto, critérios e a nota de pausa de 05/11 intactos; recebe a linha "devolvido em 2026-11-11 (sprint encerrada); sugestão: reabsorver no item Canal da sprint nova". PROG-018 a 023 e PROG-017: permanecem como estão (fora do quadro).
3. Itens Feito ficam Feito, na Sprint 01, com aceite e release (`release/notas-sprint-01.md`) como estão.
4. Retro curta da Sprint 01 no lugar da retro de 17/11 (Xavi conduz; eu registro). A hipótese "terminar antes de começar" (acima) fecha com leitura do quadro de hoje: nenhum cartão parado em Em teste; resultado a preencher pelo Xavi.

**Nova sprint (Sprint 02): "Sistema único: visual H + Finanças primeiro".**
Meta: o Guilherme abre uma interface única no visual H, e a primeira tela viva é Finanças, com os dados reais do Casemiro. Ids abaixo são provisórios (próximo livre é PROG-024; o Zico confirma). Cada item cita a documentação em `ecossistema/sistema_unico/01 a 05` e o protótipo `ecossistema/prototipo_estilos/h/` (núcleo `g/comum_gh.js`, dados de demonstração `../dados.js`).

| # | Id | Item | Resp. | Firmino | Tam. | Depende de | Back-end? |
|---|---|---|---|---|---|---|---|
| 1 | PROG-024 | Finanças no H (fatias a e b abaixo) | Endrick (tela), Rodrygo (gerador), Marquinhos (git) | sim | G | nada; desenho do Iniesta se tocar fluxo | não: gerador local, sem servidor |
| 2 | PROG-025 | Casca do app: navegação em 8 grupos, tema claro/escuro, Ctrl K | Endrick | sim | M | 024b (aproveita o componente) | não |
| 3 | PROG-026 | Servidor único: estender o Corte (rotas `/api/sistema/*`, lista de permissão, absorver `/painel` e `/central`) | Rodrygo, Thiago Silva | não | G | decisão técnica do Thiago Silva (recomendação do Valverde em 02) | SIM, é o item de back-end |
| 4 | PROG-027 | Espera você (aceites, aprovações, gates) | Endrick | sim | M | 025, 026 | sim (gravar aceite, aprovar versão) |
| 5 | PROG-028 | Canal (projetos, status PROG-012, cronograma = retomar PROG-011 só leitura) | Endrick, Rodrygo | sim | M | 025, 026 | sim |
| 6 | PROG-029 | Agentes (Ao vivo e Catálogo no H, reuso de PROG-003/016) | Endrick | sim | M | 025, 026 | usa `ao_vivo.py` existente |
| 7 | PROG-030 | Editores de agentes e de fluxos | Endrick, Rodrygo | sim | G | 026, 029 | reuso do Corte; só casca nova |
| 8 | PROG-031 | Console de jobs (executor, log, estado) | Rodrygo, Endrick | sim | M | 026 | sim |
| 2 | PROG-032 | Integra??o dos assets de imagem | Endrick | sim | P | assets dispon?veis; preparar em paralelo ? 024b, integrar ap?s 025 | acelerar |
| 10 | PROG-033 | Clipes, Inteligência, Trabalho, Programação (4 telas; fatiar a/b/c/d) | Endrick, Rodrygo | sim | G | 025, 026; Trabalho e Programação com dado pessoal | sim |
| 11 | PROG-034 | Acesso pelo celular (`--rede`, senha, 390 px) | Endrick, Rodrygo | sim | M | 025, 026; decisão do Guilherme sobre Finanças no celular | sim |
| 12 | PROG-035 | Testes e2e consolidados do sistema único e regressão do Corte | Alisson (com Rodrygo e Endrick) | não | M | cresce a cada item; fecha no fim | não |

Teste de cada item faz parte da definição de pronto (README do setor); o PROG-035 é a consolidação, não a única hora de teste.

**PROG-024 em duas fatias (cabem no WIP 2 por dev):**
- **024a, gerador local (Rodrygo; Marquinhos no git).** Script lê `financas/saldos.csv`, `movimentos.csv`, `transferencias.csv`, `pendencias.md` e `contexto.md` e grava SÓ em local ignorado pelo git (sugestão: `estudio/dados/`, que já está no `.gitignore`), sem token e sem API. Regerável com um comando; deve rodar sempre que o Casemiro mudar os CSV (o Ronaldo já chama `financas/dashboard.py` nessa hora: avaliar chamar o gerador junto, decisão do Thiago Silva). Calcula: saldo por conta e total (com a data de cada saldo), receitas x gastos do mês, gasto por categoria, a pagar com data de vencimento e dias restantes (vencido / hoje / próximos), movimentos recentes, alertas de inconsistência (conta sem saldo confirmado, saldo mais velho que N dias, pago sem lançamento, pendência aberta do Casemiro). Nunca marca nada como pago nem escreve nos CSV.
- **024b, tela no H (Endrick + Firmino).** Saldo total e por conta; barras receitas x gastos do mês; categorias; lista de vencimentos com cor de status do H e TEXTO (vencido, vence hoje, a pagar, pago), nunca só cor; movimentos recentes; faixa de alertas do Casemiro; data/hora da última leitura dos CSV e aviso se o gerador falhou; modos claro e escuro; funciona em 1280 px e em 390 px.
- Critérios de aceite do 024 (para o Zico refinar): 1) os valores da tela batem com os CSV (teste com CSV de fixture inventado, nunca os reais); 2) alterar um CSV de fixture e regerar muda a tela; 3) nenhum arquivo gerado nem o CSV real aparece no `git status`; 4) nenhum dado financeiro vai para API, servidor externo, `dados.js` do protótipo nem espelho; 5) estados vazio e erro em português; 6) alertas listados com a origem; 7) Alisson valida contra os dados reais só localmente, sem copiar valores para `qa/`.

**Riscos (em ordem de gravidade).**
1. **Privacidade (bloqueia o 024).** O `.gitignore` só protege `financas/planilha/`. Não encontrei regra para `financas/*.csv`, `contexto.md`, `dashboard.html` e `dashboard.png`. Se esses arquivos estiverem versionados ou forem adicionados, os saldos iriam ao git. Primeiro passo do 024a: **Marquinhos** conferir `git ls-files financas` e, se houver rastreio, parar e levar ao Guilherme antes de qualquer commit (remover do índice é decisão dele); regra de ignorar a pasta e os arquivos gerados entra antes do gerador. Também: `PROG-019` já exclui `financas/` da lista de documentos, o gerador e o H não podem furar isso.
2. **Escopo cabe em uma sprint?** São 12 itens, vários G, e dois devs. Sem histórico de velocidade confiável (a Sprint 01 entregou 12 em 8 dias, mas com itens pequenos e correções). Proposta de compromisso firme: itens 1 a 3 (e 4 se sobrar); 5 a 12 ficam previstos em ordem, sujeitos à capacidade medida na daily. É a decisão do Thiago Silva (estimar) e do Xavi (fechar). Se o dono quer tudo, será mais de uma sprint; dizer isso a ele desde já.
3. **Maestro pausado.** O README diz que só o maestro move cartão, e ele está desligado por ordem do Guilherme. Sem ele, cartão só anda quando a sessão principal aplicar a decisão (arquivo em `maestro/decisoes/`) e o aceite do Guilherme (`aceites/`). Gargalo: o aceite visual dele. Sugestão: mostrar captura da tela de Finanças ao Guilherme logo que a 024b existir, antes do Code Review, para ajustar cedo.
4. **Servidor único (026)** é o maior risco técnico: toca `estudio/servidor.py`, em uso por tudo. Item 1 não deve esperar por ele (gerador local, sem back-end), o que evita travar a primeira entrega.
5. **Dado de demonstração.** O protótipo usa `dados.js` com dados de exemplo; precisa continuar assim. Finanças reais só entram pelo gerador local.
6. **Saldo recém-atualizado.** Conferir com o **Casemiro** que o `saldos.csv` já traz a data nova (as linhas que li no topo são de 26 e 29/10) e que `pendencias.md` não tem pergunta aberta que muda o saldo. A tela deve mostrar a data de cada saldo, não só o número.
7. **Papéis.** O **Firmino** (`firmino-frontend-design`) não consta na tabela de equipe do `programacao/README.md`. Pedir a **Luiz Henrique** que o inclua (ele é o dono do README) como participante de itens visuais, ao lado de **Endrick** e **Iniesta**. Enquanto isso, o código continua sendo gravado só por **Rodrygo** e **Endrick**, conforme o contrato; o Firmino propõe o desenho e o CSS que o Endrick integra, a menos que o Guilherme diga outra coisa.
8. **Dado pessoal em Trabalho e Programação (033).** Mesma regra transversal do PROG-018: nada de `produtividade/` pessoal, acessos ou LinkedIn em tela versionada.

**Hipótese de melhoria desta sprint (uma só): fatia vertical visível primeiro.** Em vez de construir casca e servidor antes, entregar Finanças de ponta a ponta (dados reais, tela, teste) em um item pequeno e mostrar ao Guilherme cedo.
- Medir: (a) dias úteis do PROG-024 de Fazendo até Pronto para aceite (meta: até 3); (b) devoluções do Alisson e do Thiago Silva no 024 (meta: no máximo 1); (c) o Guilherme ver a tela com os dados reais antes do Code Review (sim/não); (d) itens da sprint que mudam de ordem depois da planning (meta: no máximo 1, com troca declarada).
- Sucesso: 024 aceito em até 5 dias úteis sem vazamento no `git status`, e o feedback do Guilherme sobre o visual já aplicado nos itens 2 e 4 sem refazer o 024. Fracasso: o 024 depende de algo que só vem da casca ou do servidor; então a hipótese seguinte é inverter a ordem (026 primeiro).
- Resultado: (preencher na daily de 14/11 e na retro). Decisão: (preencher na retro).

### Observação da Sprint 02 · 2026-11-12 (leitura do quadro, sem alterar nada além deste arquivo)

**Estado lido.** Compromisso firme: PROG-024 (Em teste, segue para Code Review), PROG-032 (Fazendo, 5 itens P0 de imagem faltando), PROG-025 (Bloqueado), PROG-026 (Fazendo, regressão geral 149/150 com 1 falha ainda sem causa classificada). Previstos 027 a 035 parados, todos dependentes de 025 e 026. Feito na Sprint 02: 0. Code Review e Pronto para aceite: vazios.

**O que atrapalha.**
1. **Quadro se contradiz.** PROG-024 aparece no Backlog como "segue para Code Review" e na coluna Em teste; PROG-025 aparece no Backlog como "em andamento" e na coluna Bloqueado; PROG-032 aparece em Fazendo e em "Acelerado". Quem lê não sabe o estado real.
2. **Bloqueio de 025 é regressão, não decisão humana.** Os recados do maestro diferem pela hora: 07:25 diz que o `index.html` ainda é a tela de login com senha no código; 10:40 diz que a Finanças foi restaurada e a senha saiu. Falta confirmar que a casca de 8 grupos ainda não existe e que o motivo do bloqueio continua válido.
3. **WIP escondido.** A contagem diz **Endrick** 1/2, mas ele segura 024 (Em teste), 032 (Fazendo) e 025 (Bloqueado). Item bloqueado continua ocupando atenção e não é contado.
4. **Fila de previstos parada por dependência.** 027, 028, 029, 030, 031, 033 dependem de 025 e 026; 025 está bloqueado e 026 parcial. Enquanto isso o esforço vai para o 032 (assets), que não destrava ninguém.
5. **Falha de regressão sem dono.** Falha única do `e2e_interface.mjs` (`obsoleto.cenas`) repetida 3 vezes, "causa não classificada". Sem classificar, o 026 fica parcial para sempre e o PROG-035 herda a dúvida.
6. **Arquivo crítico trocado fora do item.** O `index.html` foi sobrescrito em 11/11 às 22:17 por uma versão com senha no código. Nenhum agente deve ter feito isso por um item do quadro; é risco de segredo e de privacidade.

**Hipótese de melhoria (uma só): "destravar a dependência antes de abrir frente nova".** Nesta semana, a ordem de puxada passa a ser 024 (fechar revisão) -> 026 (classificar a falha) -> 025 (casca) -> só então 032 e os previstos. Bloqueado só vale com motivo e dono datados; sem isso, o cartão volta a Fazendo.
- **Quem aplica:** **Xavi** (ordem e coluna única por item), **Thiago Silva** (classificar a falha do 026 e confirmar o estado do `index.html`), **Endrick** e **Rodrygo** (puxar na ordem).
- **Como medir:** (a) cartões que aparecem em mais de uma coluna no `quadro.md` (hoje 3; meta 0); (b) dias úteis de 025 em Bloqueado (meta: no máximo 1 a mais); (c) falha do 026 classificada como "do Corte, fora do escopo" ou "do dashboard" em `qa/PROG-026.md` até a daily de 13/11; (d) itens da Sprint 02 em Pronto para aceite até 14/11 (meta: 024 e 026); (e) bugs escapados e retrabalho do 024 (meta: no máximo 1 devolução).
- **Sucesso:** na daily de 14/11, 025 fora de Bloqueado, 026 com a falha classificada, nenhum cartão em duas colunas e pelo menos 024 em Pronto para aceite. **Fracasso:** 025 continua parado por dependência de arquivo que alguém mais edita; então o problema é de governança do `index.html` e a hipótese seguinte é dar um único dono de escrita para esse arquivo.
- **Resultado:** (preencher na daily de 14/11). **Decisão:** (preencher na retro).

**Proposta de contrato (via Luiz Henrique, com aval do Guilherme).** Incluir **Firmino** na tabela de equipe do `programacao/README.md` (já proposta em 11/11) e registrar que a contagem de WIP inclui itens Bloqueados quando o dev continua dono deles.

### Próximas observações planejadas
- Daily ou aceite de quinta 06/11: medir idade dos cartões Em teste e quantos itens chegaram a Feito.
- Antes da retro de 17/11: contar retrabalho, itens adicionados fora da planning e bugs escapados (bug achado depois do aceite).
