# Apresentação e formulário · Planning da Sprint 01

Data: 2026-11-03, 17:20. Facilitação: **Xavi**. Fontes: `prep/zico.md`, `prep/thiago-silva.md`, `prep/iniesta.md`, `prep/alisson.md`, `ux/prog-003-aba-agentes.md`, `backlog.md`, `quadro.md`, `sprint-01.md`, `planning-2026-11-03.md`. Quem decide é o Guilherme: prioridade com o **Zico**, técnica com o **Thiago Silva**. Estimativas P/M/G são do **Thiago Silva**, sem histórico (P = meio dia, M = 1-2 dias, G = 3+ dias).

# (A) APRESENTAÇÃO

## Slide 1 · Abertura e meta provisória da Sprint 01
- Sprint de 1 semana (sugestão 2026-11-03 a 2026-11-10); ainda não aberta, só abre quando o Guilherme disser "abre a sprint".
- Meta provisória: o Guilherme usa o Corte sem surpresa, com a bateria de testes confiável.
- Hoje: 50 min, abertura, rodadas por item, fecho e ata.
- **Ancelotti** observa o processo e fecha com uma melhoria a testar na retro.

## Slide 2 · O que foi entregue hoje e está em teste
- PROG-001: motivo de "não se aplica" visível; componentes para os quatro estilos.
- PROG-002: bloqueio do fluxo visível ao clicar em "Iniciar cenas".
- Reserva com Codex (`estudio/reserva.py`, `tools/sincronizar_codex.py`): implementada, nunca testada (PROG-004).
- Kanban/Trello e setor de programação criados hoje.
- Nada disso foi validado por **Alisson** nem pelo Guilherme; faltam os relatórios em `entregas/` (hoje vazio).

## Slide 3 · Como o time trabalha
- Só se trabalha o que está no quadro; fora dele, vai para o backlog do **Zico**.
- **Zico** decide o quê; **Thiago Silva** decide o como; **Xavi** cuida do ritmo.
- Pronto = definição de `programacao/README.md` + aceite do Guilherme; relatório em `entregas/<id>.md` com a causa real.
- Sem commit, publish ou gasto com API paga sem o Guilherme pedir.

## Slide 4 · Visão do quadro
- Colunas: Backlog da sprint, Em refinamento técnico, Fazendo, Em teste, Pronto para aceite, Feito, Bloqueado.
- WIP: 2 em Fazendo por dev, 3 em Em teste no total.
- Hoje: PROG-001 e PROG-002 em Em teste (2 de 3 vagas); candidatos no Backlog da sprint: PROG-005, 004, 010, 009, 006, 008, 007.
- PROG-003 fica fora do quadro até entrar na sprint.

## Slide 5 · Itens candidatos
Esforço do **Thiago Silva** (ele usa C-01 a C-07 = PROG-004 a 010).

| Id | Título | Valor | Esforço | Risco | Dono |
|---|---|---|---|---|---|
| PROG-001 | Motivo de "não se aplica" (em teste) | Alto | P (só validar) | Baixo | **Alisson**; relatório de **Rodrygo**/**Endrick** |
| PROG-002 | "Iniciar cenas" (em teste) | Alto | P (só validar) | Baixo | **Alisson** |
| PROG-005 | Atualizar testes e2e antigos | Alto | M (vira G se quebra além do mapeado) | Médio (falsos verdes) | **Alisson** + **Rodrygo**/**Endrick** |
| PROG-004 | Validar reserva com Codex | Médio | P-M | Médio (depende de decisão e do binário `codex`) | **Rodrygo**; **Alisson** valida |
| PROG-010 | `instalar_agentes.bat` sobrescreve | Alto | P | Baixo | **Marquinhos** |
| PROG-009 | Player falha quando o **Vini** termina | Médio | M (investigação) | Médio (causa incerta) | **Thiago Silva** (causa), depois **Endrick** |
| PROG-006 | Tela mostra motor e nota | Médio | P | Baixo | **Iniesta** > **Endrick** |
| PROG-003 | Aba Agentes em tempo real | Médio | M-G | Médio | **Iniesta**; back **Rodrygo**, front **Endrick** |
| PROG-008 | Botão migrar execuções antigas | Baixo | M-G | Alto (dados reais) | **Iniesta**, **Endrick**, **Rodrygo** |
| PROG-007 | AGENTS.md defasado | Baixo | P | Baixo | **Rodrygo**, após decisão |

Divergência **Zico** x **Thiago Silva** (decide o Guilherme):
- PROG-009: **Zico** põe na sprint (como risco; sai primeiro se for alto). **Thiago Silva** deixa para a sprint 2, só com diagnóstico dele se houver folga.
- PROG-003: **Zico** deixa fora (com PROG-006, por depender de **Iniesta** e ser o maior item). **Thiago Silva** põe dentro, com PROG-006 embutido, nos dias 3 a 5.

## Slide 6 · QA: testes antigos e o que exige
- Falsos verdes: `e2e_corte.mjs` l.419 passa por `.catch(() => true)`; l.420 engole erro.
- Vão falhar: `e2e_estilos.mjs` l.193 (contradiz componentes nos 4 estilos) e l.307-310; `e2e_interface.mjs` l.111 e l.153 (rótulo a confirmar).
- Sem teste hoje: motivo de "não se aplica" na tela, bloqueio do fluxo, motor no front, migração do fluxo antigo.
- Exigências: relatório com causa real; teste novo que falha sem a correção; baterias verdes sem teste relaxado; fluxo antigo e novo cobertos; zero token e zero `--allow-paid`.
- Regressão verde: M (1 a 2 dias), G se a primeira rodada mostrar quebra além do mapeado.

## Slide 7 · UX: proposta da aba Agentes (PROG-003)
- Hoje: só catálogo e editor, sem polling nem sinal de atividade.
- Estados com ícone e palavra: Trabalhando, Na fila, Falhou, Livre, Desativado; sugestão de "Espera você".
- Linha ativa: agente, vídeo, etapa, "há 2 min" (contador local), motor (Claude/Codex).
- Alternativa A (recomendada): seções Atenção / Agora / Todos acima da lista atual; menor mudança, vale igual no celular.
- Alternativa B: duas abas, "Ao vivo" e "Catálogo"; isola a edição, mas esconde a atividade atrás de um clique.
- Se a lista de 38 agentes pesar no polling, cair de A para B sem mudar textos nem estados.

## Slide 8 · Capacidade x comprometido e riscos
- Sem histórico de velocidade: capacidade em pontos será fixada pelo **Thiago Silva** hoje; o gargalo real é o tempo de aceite do Guilherme.
- Cenário **Zico**: PROG-002, 001, 005, 004, 010, 009 (três primeiros são validação/teste).
- Cenário **Thiago Silva**: validar 001/002 + 004 + 005 + 010 + 007 + PROG-003 com PROG-006; fora PROG-008 e PROG-009.
- Riscos: PROG-005 pode revelar falhas escondidas; PROG-009 de duração incerta; **Rodrygo** e **Endrick** mexem nos mesmos arquivos (`app.js`, `corte_*.js`, `servidor.py`), então o front é sequenciado; banco/porta isolados para os testes (**Marquinhos**).
- Itens parados por decisão do Guilherme: PROG-004, 007, 010.

## Slide 9 · Decisões que dependem do Guilherme
- Validar o que já existe ou abrir novos itens primeiro.
- Quais itens entram; PROG-003 e PROG-009 dentro ou fora.
- Aba Agentes: A ou B; "espera você" como estado; limite do aviso "mais que o normal".
- Codex: mantém, restringe ou remove; destino do `AGENTS.md`; futuro do `instalar_agentes.bat`.
- Tempo dele para testar e aceitar; sprint de 1 semana.

## Slide 10 · Próximos passos
- Guilherme responde o formulário (B); **Xavi** consolida na ata.
- **Zico** ajusta a ordem do backlog; **Thiago Silva** fecha pontos e capacidade.
- Registro das decisões em `tecnico/decisoes.md` (Codex, `.bat`, AGENTS.md).
- "Abre a sprint" do Guilherme; daily e review agendadas pelo **Ronaldo**.
- Primeiro dia: **Alisson** valida PROG-001/002; **Rodrygo** e **Endrick** começam PROG-005.

---

# (B) FORMULÁRIO DE PERGUNTAS PARA O GUILHERME
Marque uma opção por pergunta. A primeira é a recomendada.

**1. O que vem primeiro?**
- a) Validar o que já foi feito (PROG-001, 002, reserva) e consertar os testes antes de itens novos. Por quê: sem teste confiável, nenhuma validação vale (PROG-005).
- b) Misturar validação e itens novos na mesma semana.
- c) Itens novos primeiro.

**2. Quais itens entram na Sprint 01?**
- a) PROG-001, 002 (validação), 005, 004, 010 e 009 (proposta do **Zico**). Por quê: o gargalo é seu tempo de aceite, e estes itens são pequenos, com 009 saindo primeiro se for alto.
- b) PROG-001, 002, 004, 005, 010, 007 e PROG-003 com PROG-006 (proposta do **Thiago Silva**). Por quê: entrega a aba Agentes já nesta semana, mas aumenta o aceite pedido a você.
- c) Só validação e testes (PROG-001, 002, 005, 004).
- d) Outra combinação (diga quais).

**3. Aba Agentes: alternativa A ou B?**
- a) A: seções Atenção / Agora / Todos acima da lista. Por quê: mudança menor e igual no celular.
- b) B: abas "Ao vivo" e "Catálogo". Por quê: isola a edição, mas esconde a atividade.
- c) Adiar a decisão para depois do refinamento.

**4. "Espera você" (aprovação pendente) vira estado do agente?**
- a) Sim. Por quê: é o que mais trava a produção e vira critério novo no PROG-003.
- b) Não, só trabalhando, fila, falhou e livre.

**5. Limite do aviso "mais que o normal" na tarefa do agente?**
- a) 15 min, geral. Por quê: valor sugerido pela **Iniesta**, simples de implementar.
- b) Por etapa (cada etapa com seu tempo), mais preciso, mais trabalho.
- c) Outro valor (diga qual).

**6. Reserva com Codex quando o Claude esgota?**
- a) Restringe: só a reserva automática, fora dela vale "só Claude". Por quê: aproveita o que foi feito sem manter arquivos Codex soltos.
- b) Mantém como está.
- c) Remove (código, teste e referências saem).

**7. O `AGENTS.md` da raiz?**
- a) Seguir a resposta 6: se a reserva sai, remove; se fica, deixa o `CLAUDE.md` como fonte e remove o AGENTS.md. Por quê: a regra do setor proíbe manter arquivos Codex.
- b) Atualizar o AGENTS.md para bater com o `CLAUDE.md`.
- c) Manter como está, fora desta sprint.

**8. O `instalar_agentes.bat`?**
- a) Corrigir para nunca sobrescrever versão mais nova (cópia de segurança ou só copiar o que não existe). Por quê: o `copy /Y` hoje pode apagar agentes atuais e a correção é pequena.
- b) Aposentar o `.bat` e `agentes_para_instalar/`. Por quê: as cópias já estão defasadas; só vale se você não usa.
- c) Deixar como está (aceita o risco).

**9. Duração da sprint?**
- a) 1 semana, com daily curta. Por quê: primeira sprint, feedback rápido e sem histórico de velocidade.
- b) 2 semanas.

**10. Quanto tempo você tem esta semana para testar e aceitar?**
- a) Cerca de 30 min por dia, em horário fixo. Por quê: aceite em lote dá previsibilidade e o dado define a capacidade.
- b) Cerca de 1 hora duas vezes na semana.
- c) Só no fim de semana.
- d) Menos que isso (diga quanto).

**11. Cronograma de postagem no quadro?**
- a) Próxima sprint. Por quê: esta sprint já está cheia de validação e testes.
- b) Nesta sprint (**Zico** cria o item e entra no lugar de outro).
- c) Não quero no quadro.

**12. Aberta: o que está doendo no Corte ou no pipeline que não aparece na lista?** Algo pode passar na frente de PROG-005 a PROG-010? (resposta livre, e inclua o resultado de qualquer teste que você já fez de PROG-001, 002 e da reserva.)

---

# (C) FALAS DE CADA AGENTE

**Zico:** "Eu trago 6 itens: PROG-002, 001, 005, 004, 010 e 009, e deixo PROG-003 e 006 fora porque precisam da **Iniesta** e são o maior item. Quero ouvir quanto tempo você tem para aceitar, o que dói e não está na lista, e o que fazemos com Codex e AGENTS.md."

**Thiago Silva:** "Eu colocaria PROG-005 primeiro, porque libera a regressão, e cabe PROG-003 com PROG-006 embutido nos dias 3 a 5. PROG-009 e PROG-008 ficam para a sprint 2, e PROG-009 só com diagnóstico meu se houver folga."

**Iniesta:** "Recomendo a alternativa A para a aba Agentes, com estado em ícone e palavra e o aviso de dado desatualizado. Preciso saber se 'Espera você' vira estado, qual o limite de 15 min, como mostrar um agente com vários vídeos e se agentes de outros setores aparecem."

**Rodrygo:** "Pergunta que vou fazer: qual a ordem entre PROG-005 e o relatório da causa de PROG-001 e PROG-002, e quem fica com o back de PROG-003 se ele entrar na sprint?"

**Endrick:** "Pergunta que vou fazer: como evitamos colidir em `app.js` e nos `corte_*.js` se PROG-003, 006 e 009 mexerem no mesmo front, e qual desenho da **Iniesta** eu implemento primeiro?"

**Alisson:** "Não valido PROG-001 e PROG-002 sem relatório em `entregas/` e sem teste que falhe antes da correção, e não aceito teste relaxado nem `.catch` que engole erro. Os falsos verdes do `e2e_corte` (l.419) precisam cair antes de qualquer regressão valer."

**Marquinhos:** "Pergunta que vou fazer: posso mudar o `instalar_agentes.bat` para nunca sobrescrever versão mais nova, ou ele deve sair? E posso isolar banco e porta para as baterias de teste?"

**Ancelotti:** "Vou observar se cada decisão sai com dono e critério de aceite, se o WIP é respeitado e se o aceite do Guilherme vira gargalo. Fecho com uma única melhoria para testar na retro."
