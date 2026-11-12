# Backlog · Setor de programação

Dono: **Zico** (`zico-po-programacao`). Formato por item: id, tipo, prioridade, status, contexto, critérios de aceite.

## Resumo e ordem de prioridade (atualizado em 2026-11-03, pré-planning)
Valor para o Guilherme: A = alto, M = médio, B = baixo. PC = pré-requisito de confiança; N = entrega nova.

| Ordem | Id | Cartão | Tipo | Valor | Classe | Por que nesta posição |
|---|---|---|---|---|---|---|
| 1 | PROG-002 | "Iniciar cenas" não faz nada | Bug | A | PC | Travava o uso do Corte; atendido, falta validar. |
| 2 | PROG-001 | Etapa "não se aplica" sem motivo | Bug | A | PC | Mesma razão; atendido, falta validar. |
| 3 | PROG-015 | Ação da próxima etapa precisa funcionar e mostrar o resultado | Bug | A | PC | A chamada “Resolver o parecer do Vini” hoje só navega; o Guilherme precisa comprovar a ação prometida. Prioridade pedida para a Sprint 01. |
| 4 | PROG-005 | Atualizar testes e2e antigos | Dívida | A | PC | Sem bateria confiável, a validação de tudo o mais não vale. |
| 5 | PROG-004 | Validar a reserva com Codex | Validação | M | PC | Implementada e nunca testada; depende de decisão sobre "só Claude". |
| 6 | PROG-010 | Instalador não sobrescrever agentes | Bug/risco | A | N | Perda silenciosa de trabalho; correção pequena. |
| 7 | PROG-009 | Player de vídeo falha ao Vini terminar | Bug | M | N | Bug conhecido, causa a investigar; atrapalha a revisão do vídeo. |
| 8 | PROG-006 | Mostrar motor e motor_nota na tela | Melhoria | M | N | Backend pronto; vira base do PROG-003. |
| 9 | PROG-012 | Status automático de cada vídeo (Corte/output) | Melhoria | M | N | Base do PROG-011; pequena e ligada ao canal (sabe se há vídeo pronto). Empate com PROG-003 desfeito por tocar a publicação, que é o objetivo do canal. |
| 10 | PROG-011 | Cronograma de postagem no Kanban | Melhoria | M | N | Depende do PROG-012; mostra o que sobe em que dia. |
| 11 | PROG-003 | Aba Agentes em tempo real (fatia Ao vivo) | Melhoria | M | N | Grande; depende do PROG-006. Em 05/11 ficou só a entrega 1 (Ao vivo); o Catálogo virou o PROG-016. |
| 11b | PROG-016 | Aba Agentes: Catálogo e indicador ocioso | Melhoria | M | N | Entrega 2 do PROG-003; dentro da Sprint 01 por decisão do Guilherme em 09/11 (PROG-003 aceito). |
| 12 | PROG-014 | Agente de referências de canais dark (nicho aberto e nosso) | Melhoria | M | N | Alimenta o aprendiz. Entrou na Sprint 01 a pedido do Guilherme (05/11). |
| 13 | PROG-013 | Agente aprendiz de canal dark (estuda vídeos enviados pelo Guilherme) | Melhoria | M | N | Entrou na Sprint 01 a pedido do Guilherme (05/11), com as decisões de ferramenta e agendamento registradas no item. |
| 14 | PROG-008 | Botão migrar execuções antigas | Melhoria | B | N | Só afeta execuções velhas; contornável. |
| 15 | PROG-007 | AGENTS.md defasado | Dívida | B | N | Depende de decisão do Guilherme (Codex vs só Claude). |
| 0a | PROG-018 | Épico: sistema central do ecossistema no Corte | Épico | A | N | Pedido do Guilherme em 09/11 (prioridade alta); filhas 019 a 023, nessa ordem. Em execução fora do quadro (autorizado em 2026-11-09); app "Ecossistema do Guilherme". |
| 0b | PROG-019 a 022 | Documentos+data; atualização automática; Resumo 2 linhas; espelho dentro do Corte | Melhoria | A | N | Objetivo da semana: ver o que mudou antes do novo canal dark. |
| 0c | PROG-023 | Dashboard geral (agentes e setores) | Melhoria | M | N | Por último: Documentos e Resumo já respondem ao pedido principal. |
| 16 | PROG-017 | Setor de LinkedIn (Lamine Yamal fora da produtividade) | Melhoria | B | N | Pedido em 09/11; não trava canal nem Corte; escopo a definir com o Guilherme. |

Todo item do backlog tem o campo `Dono:` (sugerido; o time confirma na planning).

## PROG-001 · Bug · Prioridade alta · Status: em teste (atendido por Rodrygo e Endrick; aguarda validação de Alisson e do Guilherme)
**Dono:** Alisson
**Título:** Etapa de componentes aparece como "não se aplica" sem explicação.

**Contexto (reportado em 2026-11-03):** num vídeo rodado no Corte, a etapa de componentes foi marcada como "não se aplica" e o Guilherme não entendeu o motivo. Causa não investigada aqui.

**Critérios de aceite:**
1. Sempre que uma etapa aparece como "não se aplica" (ou pulada), a interface mostra o motivo em português claro, na própria etapa, sem precisar abrir log.
2. O motivo do caso de componentes é a regra real que o aplicou (ex.: estilo, fase de aprendizado, configuração do projeto), citando qual.
3. O texto diz o que o Guilherme pode fazer para a etapa se aplicar, quando houver como.
4. Vale na tela do computador e no celular (`--rede`).
5. Teste automatizado cobre a presença do motivo para uma etapa "não se aplica".
6. Etapas que se aplicam não mostram o aviso.

## PROG-002 · Bug · Prioridade alta · Status: em teste (atendido por Rodrygo e Endrick; aguarda validação de Alisson e do Guilherme)
**Dono:** Alisson
**Título:** Clicar em "Iniciar cenas" não faz nada.

**Contexto (reportado em 2026-11-03):** ao clicar em "Iniciar cenas" no Corte, nada acontece. Causa não investigada aqui.

**Critérios de aceite:**
1. Ao clicar, a etapa de cenas inicia e a interface mostra retorno imediato (estado "em andamento" ou equivalente).
2. Se a etapa não puder iniciar (dependência faltando, outra etapa rodando), a interface diz por quê e o que fazer; nunca fica sem resposta.
3. Clique repetido não dispara a etapa duas vezes.
4. O progresso e o fim (sucesso ou erro) aparecem na tela, e o resultado aparece como nova versão, como nas demais etapas.
5. Teste automatizado (e2e) cobre o clique e o resultado esperado, e falha sem a correção.
6. Funciona no computador e no celular.

## PROG-003 · Melhoria · Prioridade média (sugerida) · Status: novo
**Dono:** Iniesta
**Título:** Aba "Agentes" do Corte mostrar, em tempo real, qual agente está trabalhando.

**História:** como Guilherme, quero ver na aba "Agentes" quem está trabalhando agora, em qual vídeo e etapa, para acompanhar a produção sem abrir log nem adivinhar.

**Contexto (pedido em 2026-11-03, candidato à planning das 16:50):** hoje a aba "Agentes" lista e edita agentes, mas não mostra quem está rodando. O Corte já tem jobs com status/progresso, etapa, slug e, desde hoje, o campo `motor` (Claude/Codex). O pedido é expor isso por agente. Solução técnica fica para o refinamento.

**Prioridade (justificativa):** média. Não trava o uso do Corte nem do canal (os bugs PROG-001 e PROG-002 travam e vêm antes), mas reduz a incerteza durante as produções. Quem decide é o Guilherme.

**Critérios de aceite:**
**DECISÃO DO ZICO (2026-11-05, ~13:30, a pedido do prazo do Guilherme de aceite antes das 14h; o Guilherme confirma no aceite):** o PROG-003 passa a ser só a fatia "Ao vivo" (entrega 1). Os critérios 1 (indicador "ocioso") e 15 (agente sem job e sem histórico no Catálogo) só fazem sentido no Catálogo e saíram para o **PROG-016**. O critério 6 (clique chega à etapa exata do vídeo) continua aqui; o **Endrick** o implementa em paralelo. Na Ao vivo, o critério 1 vale para: trabalhando, na fila e falhou.

1. (Ajustado em 05/11) Cada agente que aparece na tela Ao vivo mostra um indicador visível de um destes estados: trabalhando, na fila ou falhou, com ícone e texto (não só cor). "Ocioso" e a visão de todos os agentes ficam no PROG-016.
2. Agente "trabalhando" ou "na fila" mostra o vídeo (slug) e a etapa em andamento; "falhou" mostra o vídeo e a etapa onde falhou.
3. Agente "trabalhando" mostra há quanto tempo está na tarefa (ex.: "há 2 min"), que avança sozinho.
4. Cada agente ativo mostra o motor usado (Claude ou Codex), conforme o campo `motor` do job.
5. A tela atualiza sozinha, sem recarregar a página, no mesmo esquema de polling já usado no Corte; mudança de estado aparece em até um ciclo de polling.
6. Clicar no agente ativo (ou em falhou) leva ao vídeo e à etapa do trabalho correspondente.
7. Funciona no computador e no celular (`--rede`), sem quebrar o layout.
8. Com muitos jobs (ex.: 50 simultâneos/históricos), a tela continua respondendo, o servidor não cai e a atualização não atrasa a interface de forma perceptível.
9. Se a consulta de estado falhar, a tela mantém o último estado conhecido e avisa que está desatualizada; o servidor não derruba.
10. Quando ninguém trabalha, a aba mostra estado vazio claro em português (ex.: "Nenhum agente trabalhando agora"), sem indicadores quebrados.
11. Teste automatizado cobre os estados (ocioso, trabalhando, fila, falhou), o estado vazio e a atualização sem recarregar; roda nas baterias de `estudio/testes/`.
12. A edição de agentes existente na aba continua funcionando (regressão).

**Refinamento do Zico (2026-11-03, noite) — PROG-003 + PROG-006 como um pacote em duas fatias:**
- Fatia A = PROG-006 (Endrick, com desenho do **Iniesta**): o motor e a nota aparecem na etapa/versão. Pronta sozinha vale como entrega.
- Fatia B = PROG-003: reaproveita o componente da fatia A para mostrar o motor de cada agente ativo. Só começa depois da A aceita.
- Se a Sprint 01 não couber as duas, entra só a A; a B vai para a Sprint 02 (sugestão; quem decide capacidade é o **Xavi**).
13. Mapeamento dos estados (teste confere cada linha): ocioso = nenhum job ativo ou na fila para o agente; trabalhando = job com status em andamento; na fila = job aceito e ainda não iniciado; falhou = último job do agente terminou em erro e ainda não houve job novo bem-sucedido do mesmo agente. "Falhou" some quando o agente roda de novo com sucesso.
14. Números verificáveis: "tempo na tarefa" avança a cada 1 s sem nova consulta ao servidor; o polling segue o intervalo já usado no Corte (sem criar um novo); com 50 jobs a resposta de estado volta em menos de 1 s e a tela não congela (teste mede).
15. (Ajustado em 05/11) Na Ao vivo, agente sem job e sem histórico não aparece (logo não mostra "falhou" nem tempo). A visão de Catálogo desse caso é do PROG-016.
**Refinamento PROG-006 (critérios extras):**
6. O texto do motor é fixo em português ("Claude" ou "Codex"); motor desconhecido aparece como "motor não informado", nunca vazio, nunca "undefined".
7. A mesma exibição aparece nas duas telas onde o job é visto (versão do vídeo e, depois, aba Agentes), vinda de um único componente.
**Aberto para o Guilherme:** PROG-004 define se o Codex continua existindo; até lá a exibição trata "Codex" como valor possível sem prometer que a reserva funciona.

## PROG-016 · Melhoria · Prioridade média (sugerida) · Status: dentro da Sprint 01 por decisão do Guilherme em 2026-11-09 ("bora fazer a 016"); dependência PROG-003 aceita em 05/11; prioridade do Guilherme, topo do Backlog da sprint
**Dono:** Iniesta (desenho), Endrick (tela), Rodrygo (dados)
**Título:** Aba Agentes: Catálogo com indicador "ocioso" por agente (entrega 2 do PROG-003).

**Contexto:** nasceu em 2026-11-05 da divisão do PROG-003 (decisão do **Zico** pelo prazo do Guilherme; ele confirma). A tela Ao vivo só lista quem está trabalhando, na fila ou falhou. Falta a visão de todos os agentes, incluindo os ociosos. Base: `estudio/ao_vivo.py` já calcula "ocioso" (coberto em `testar_ao_vivo.py`); a rota `/agentes?aba=catalogo` já abre a ficha.

**Valor:** médio-baixo. Não trava o Corte nem o canal; só completa a visão.

**Critérios de aceite:**
1. A aba Catálogo mostra todos os agentes, cada um com um indicador visível de um destes estados: ocioso, trabalhando, na fila ou falhou, com texto (não só cor).
2. Agente ocioso (sem job ativo, na fila ou com falha pendente) mostra "ocioso" e nenhum vídeo, etapa ou tempo.
3. Agente sem job e sem histórico não mostra "falhou" nem tempo.
4. Os estados seguem o mapeamento do critério 13 do PROG-003, sem divergir da tela Ao vivo para o mesmo agente.
5. O estado do Catálogo atualiza sozinho, sem recarregar, usando o polling já existente (sem criar um novo).
6. Funciona no computador e no celular (390 px, uma coluna, sem rolagem lateral).
7. Com 50 jobs e todos os agentes listados, a resposta volta em menos de 1 s.
8. A edição de agentes continua funcionando (regressão) e as rotas `/agentes/<id>` seguem abrindo a ficha.
9. Teste automatizado cobre os quatro estados no Catálogo e roda nas baterias de `estudio/testes/`; resultado real em `qa/PROG-016.md`.

**Depende de:** PROG-003 (Ao vivo) aceito.

## PROG-004 · Validação · Prioridade média · Status: novo (origem C-01)
**Dono:** Rodrygo
**Cartão:** Validar a reserva com Codex quando o Claude esgota

**Contexto:** `estudio/reserva.py` e `tools/sincronizar_codex.py` foram implementados em 2026-11-03 e nunca testados pelo Guilherme nem por **Alisson**. Existe `estudio/testes/testar_reserva_codex.py`. A regra do setor e a memória do Guilherme dizem "só Claude": o escopo precisa da confirmação dele antes de testar.

**Valor:** médio. **Depende de:** decisão do Guilherme sobre o escopo (pergunta 3 de `prep/zico.md`).

**Critérios de aceite:**
1. O Guilherme confirma por escrito o escopo da reserva (mantém, restringe ou remove); a decisão fica registrada em `tecnico/decisoes.md`.
2. Se mantida: com o Claude simulado como esgotado, a etapa roda pelo motor reserva e o job termina com `motor` = Codex e `motor_nota` preenchida.
3. Com o Claude disponível, o job usa Claude e a reserva não é acionada.
4. Falha da reserva produz erro legível ao usuário, sem derrubar o servidor.
5. `testar_reserva_codex.py` roda e o resultado real fica em `qa/PROG-004.md`.
6. Se removida: código, teste e referências saem e a bateria continua verde.

## PROG-005 · Dívida de teste · Prioridade alta · Status: novo (origem C-02)
**Dono:** Alisson
**Cartão:** Atualizar testes e2e antigos (se_sketch removido)

**Contexto:** o nó `se_sketch` saiu do fluxo padrão e `grafos.py` publica o fluxo sem ele, mas `e2e_estilos.mjs` (~193, ~307-310), `e2e_interface.mjs` (~111, ~153), `e2e_corte.mjs` (~419) e testes que contam nós do grafo ainda esperam o estado antigo. A regressão do **Alisson** não é confiável até isso fechar.

**Valor:** alto (destrava a confiança em todo o resto). **Depende de:** nada.

**Critérios de aceite:**
1. Nenhum teste em `estudio/testes/` referencia `se_sketch` nem a contagem antiga de nós do grafo padrão (busca no repositório comprova).
2. `e2e_estilos`, `e2e_interface`, `e2e_corte` e os testes de contagem de nós passam contra o código atual; o resultado real de cada um fica em `qa/PROG-005.md`.
3. Um teste que quebre por motivo legítimo continua quebrando (as asserções foram atualizadas, não afrouxadas nem removidas); **Thiago Silva** confere na revisão.
4. `estudio/README.md` descreve como executar cada bateria e o que se espera ver.

## PROG-006 · Melhoria · Prioridade média · Status: novo (origem C-03)
**Dono:** Endrick
**Cartão:** Tela mostrar o motor usado (Claude/Codex) e a nota

**Contexto:** o backend já entrega `motor` e `motor_nota` no estado público do job (`estudio/fluxo.py`), mas o front não os exibe. Toca a tela: **Iniesta** desenha. É a base do PROG-003.

**Valor:** médio. **Depende de:** **Iniesta** (desenho); PROG-004 define se o Codex continua existindo.

**Critérios de aceite:**
1. Na etapa/versão de um job, a tela mostra o motor em texto (Claude ou Codex), não só cor.
2. Quando há `motor_nota`, ela aparece em português legível junto do motor (ex.: motivo da troca); sem nota, nada vazio ou "undefined" aparece.
3. Job antigo sem o campo `motor` não quebra a tela.
4. Funciona no computador e no celular (`--rede`) sem quebrar o layout.
5. Teste automatizado cobre motor com nota, motor sem nota e job sem o campo.

## PROG-007 · Dívida de doc · Prioridade baixa · Status: novo (origem C-04)
**Dono:** Rodrygo
**Cartão:** Decidir: atualizar ou remover o AGENTS.md da raiz

**Contexto:** o `AGENTS.md` da raiz está defasado, e a regra do setor e a memória do Guilherme proíbem manter arquivos de Codex. Decisão do Guilherme, não do time.

**Valor:** baixo. **Depende de:** decisão do Guilherme (mesma da PROG-004).

**Critérios de aceite:**
1. A decisão do Guilherme (atualizar ou remover) está registrada em `tecnico/decisoes.md`.
2. Se remover: o arquivo some e nenhuma doc ou script do repositório o referencia (busca comprova).
3. Se atualizar: o conteúdo bate com `CLAUDE.md` e com os agentes atuais, e **Thiago Silva** revisa.

## PROG-008 · Melhoria · Prioridade baixa · Status: novo (origem C-05)
**Dono:** Rodrygo
**Cartão:** Botão para migrar execuções antigas ao fluxo novo

**Contexto:** `grafos.py` já migra o fluxo padrão (sem `se_sketch`), mas execuções antigas não têm um comando na tela para isso. Envolve tela e back-end.

**Valor:** baixo. **Depende de:** PROG-005 (testes confiáveis) e **Iniesta**.

**Critérios de aceite:**
1. Execução antiga mostra um botão claro para migrar; execução já atual não mostra.
2. Antes de migrar, a tela diz o que muda; depois, mostra o resultado (sucesso ou erro) em português.
3. A migração não apaga versões nem arquivos do vídeo; o histórico anterior continua acessível.
4. Clique repetido não migra duas vezes.
5. Teste automatizado cobre execução antiga, execução atual e falha; funciona no celular.

## PROG-009 · Bug · Prioridade média · Status: novo (origem C-06)
**Dono:** Thiago Silva
**Cartão:** Player de vídeo falha quando o Vini termina

**Sintoma:** de forma intermitente, o `<video>` é substituído quando o **Vini** termina e o vídeo para ou some da tela. Causa não investigada aqui (**Thiago Silva** investiga).

**Valor:** médio. **Depende de:** nada.

**Critérios de aceite:**
1. Com um vídeo em reprodução, a conclusão do **Vini** não interrompe nem reinicia a reprodução, nem some com o player.
2. Se o vídeo muda de versão de fato, a tela avisa e carrega o novo sem tela em branco.
3. Teste automatizado reproduz a sequência (reproduzir, **Vini** termina) e falha antes da correção; roda repetido (ex.: 10 vezes) sem falha.
4. Funciona no computador e no celular.

## PROG-010 · Bug/risco · Prioridade alta · Status: feito (aceito em 2026-11-03) (origem C-07)
**Dono:** Marquinhos
**Cartão:** instalar_agentes.bat apaga agentes atuais

**Sintoma:** `instalar_agentes.bat` faz `copy /Y agentes_para_instalar\*.md .claude\agents\` e sobrescreve agentes atuais com cópias antigas. Resultado esperado: rodar o instalador nunca faz perder versão mais nova.

**Valor:** alto (evita perda de trabalho). **Depende de:** o Guilherme dizer se o `.bat` pode mudar ou sair (pergunta 4 do `prep/zico.md`). Dono provável: **Marquinhos**.

**Critérios de aceite:**
1. Rodar o instalador não substitui um agente cuja versão em `.claude/agents` seja mais nova ou diferente sem aviso explícito.
2. Antes de sobrescrever, existe cópia de segurança ou confirmação do usuário.
3. Teste em pasta temporária (não nas pastas reais) comprova: arquivo novo é instalado; arquivo existente diferente não é perdido.
4. A decisão do Guilherme (manter, mudar ou remover o `.bat`) está registrada.

## PROG-011 · Melhoria · Prioridade média (sugerida) · Status: backlog geral (devolvido em 2026-11-11: Sprint 01 encerrada por ordem do Guilherme; pausa de 05/11 mantida; sugestão: reabsorver no PROG-028 Canal, só leitura)
**Dono:** Zico (refinar)
**Cartão:** Kanban geral com cronograma de postagem do canal

**História:** como Guilherme, quero ver no Kanban/Trello geral o lado de publicação do canal (o que sobe em que dia e se já há vídeo pronto), para saber se a próxima postagem está coberta sem abrir pastas.

**Contexto (pedido em 2026-11-03, candidato à planning das 16:50):** hoje o Kanban cobre só a programação. A publicação vive em `output/fila_postagem.txt` e em `output/<slug>/`, sem visão de calendário. Solução técnica fica para o refinamento.

**Valor:** médio. Não trava o Corte, mas evita canal sem vídeo no dia da postagem. **Depende de:** PROG-012 (status de cada vídeo) e do Guilherme definir a cadência (quantos vídeos por semana e em que dias).

**Critérios de aceite:**
1. Existe um cronograma que lista, por data, qual vídeo (slug e título) está previsto para subir; a ordem respeita `output/fila_postagem.txt`.
2. O cronograma é editável pelo Guilherme (mudar dia ou trocar a ordem) e a mudança persiste.
3. Cada item mostra o status do vídeo (os do PROG-012) com texto, não só cor.
4. Há um indicador no topo, em português, da próxima postagem: "Pronto para postar" (vídeo auditado e na fila) ou "Sem vídeo pronto para DD/MM", citando o que falta.
5. Postagem prevista sem vídeo pronto a menos de 2 dias aparece destacada como alerta.
6. Publicar continua manual e só com `auditoria.md` APROVADA; o Kanban não publica nada nem muda privacidade.
7. Vale no computador e no celular (`--rede`).
8. Fila vazia, vídeo na fila sem pasta em `output/` e data passada têm estado claro, sem erro.
9. Teste automatizado cobre: fila com vários vídeos, fila vazia, vídeo sem auditoria e alerta de prazo.

**Refinamento do Zico (2026-11-03, noite) para PROG-011:**
10. Fatia mínima (entrega 1): só leitura. Lista por data + indicador do topo + alerta, derivados do PROG-012 e de `output/fila_postagem.txt`. A edição (critério 2) é entrega 2, para caber na capacidade da Sprint 01.
11. Cadência assumida até o Guilherme decidir: 1 vídeo por dia a partir da próxima data livre, na ordem da fila. A cadência fica em configuração, não fixa no código; teste cobre a mudança de 1/dia para 3/semana.
12. Alerta do critério 5: "a menos de 2 dias" = data prevista menos hoje menor que 2 dias corridos e status diferente de "na fila de postagem" ou acima. Teste usa data simulada (relógio injetável), não a data real.
13. Fila com slug inexistente em `output/`: linha com aviso "pasta não encontrada" e o resto do cronograma continua.
14. Onde mora a visão (Kanban do Corte ou Trello) não está decidido: critério de aceite vale para qualquer um, mas a escolha é do Guilherme com **Iniesta**. Não reduzir o PROG-011 a cartões no Trello preenchidos à mão: o cronograma deve ser derivado dos dados.
**Aberto para o Guilherme:** (a) cadência real (vídeos por semana e dias); (b) onde ver (Corte ou Trello). Sem (a) vale a assunção do item 11.

## PROG-012 · Melhoria · Prioridade média (sugerida) · Status: novo
**Dono:** Zico (refinar)
**Cartão:** Status automático de cada vídeo vindo do Corte/output

**História:** como Guilherme, quero que cada vídeo mostre sozinho em que etapa está, para não atualizar o quadro à mão.

**Contexto (pedido em 2026-11-03):** o estado real está nos arquivos de `output/<slug>/` e nas execuções do Corte, mas não há um status único por vídeo.

**Valor:** médio. **Depende de:** nada (é a base do PROG-011).

**Critérios de aceite:**
1. Cada vídeo tem exatamente um destes status, em texto: sem roteiro, em produção, vídeo pronto, auditado, na fila de postagem, publicado (privado), público.
2. O status é derivado dos dados reais (`roteiro.txt`, `video.mp4`, `auditoria.md` APROVADA, `output/fila_postagem.txt`, registro de publicação) e muda sozinho quando eles mudam, sem edição manual.
3. "Auditado" só vale com `auditoria.md` APROVADA; reprovada ou ausente mantém "vídeo pronto".
4. "Público" exige confirmação da fonte (YouTube/registro de publicação) ou marcação manual do Guilherme, pois o Studio é passo manual; sem confirmação, o status fica em "publicado (privado)".
5. Vídeo com dados contraditórios (ex.: na fila sem `video.mp4`) mostra aviso em português, não um status falso.
6. Uma visão lista todos os vídeos com seu status e responde "há vídeo pronto para a próxima postagem: sim/não".
7. Nenhuma ação da visão publica, move arquivos ou altera `fila_postagem.txt`.
8. Teste automatizado cria pastas temporárias para cada status e para o caso contraditório, sem tocar `output/` real.

**Refinamento do Zico (2026-11-03, noite) para PROG-012:**
9. Regra de precedência (vale o status mais avançado cujas condições estão todas verdadeiras; teste cobre cada degrau): sem roteiro (sem `roteiro.txt`) < em produção (há `roteiro.txt`, falta `video.mp4`) < vídeo pronto (`video.mp4` existe) < auditado (`video.mp4` + `auditoria.md` APROVADA) < na fila de postagem (auditado + slug em `output/fila_postagem.txt`) < publicado (privado) < público.
10. Os dados contraditórios do critério 5 incluem no mínimo: slug na fila sem `video.mp4`; slug na fila sem `auditoria.md` APROVADA; publicado sem `video.mp4`. Cada caso mostra o aviso em português e o status derivado só dos dados que são consistentes.
11. A visão responde "há vídeo pronto para a próxima postagem" com "sim" só quando o primeiro slug da fila está em "na fila de postagem" sem aviso; caso contrário "não", com o motivo em texto.
12. Pasta de `output/` sem nenhum arquivo do contrato (ex.: vazia) aparece como "sem roteiro", sem erro.
13. Desempenho: listar 100 pastas de vídeo leva menos de 2 s e só lê arquivos, sem escrever nada (teste confere que `fila_postagem.txt` e as pastas não mudam de conteúdo nem de data de modificação).
**Ajuste do Zico (2026-11-05, na conferência de aceite):** 
11'. (substitui o 11) A visão responde "há vídeo pronto para a próxima postagem" com "sim" quando algum item da fila está em "na fila de postagem" sem aviso (o primeiro pronto, que é o que `postar_pendentes` realmente envia); com "não" caso contrário. O motivo em texto cita os itens bloqueados à frente. Motivo do ajuste: o texto antigo não bate com o comportamento real da publicação (D-001).
12'. (complementa o 12) Pasta totalmente vazia não entra na lista (mesmo filtro do Corte); `status_do_video` de pasta vazia devolve "sem roteiro". Pasta com algum arquivo e sem roteiro aparece como "sem roteiro", sem erro.
Ambos os ajustes são reversíveis se o Guilherme preferir o texto original (custo: uma linha de código cada).

**Aberto para o Guilherme (bloqueia só o degrau "publicado"):** onde fica o "registro de publicação" hoje? Proposta do Zico: usar o resultado gravado por `run.py publish` / `postar_pendentes.py` se existir; se não existir, a primeira entrega cobre até "na fila de postagem" e "publicado/público" ficam por marcação manual dele (critério 4). Rodrygo confirma se o registro existe.

**Recado para o Xavi:** os dois itens entram no backlog como "novo"; a coluna e a sprint ficam a seu critério depois da planning das 16:50 (não editei o `quadro.md`).

## PROG-013 · Melhoria (novo agente) · Prioridade média (sugerida) · Status: em teste na Sprint 01 (entrou em 2026-11-05)
**Dono:** Luiz Henrique (`luiz-henrique-ecossistema`, cria o agente e decide a estrutura)
**Cartão:** Agente aprendiz de canal dark (estuda vídeos enviados pelo Guilherme)

**Decisões do Guilherme (2026-11-05), que mudaram os critérios 2 a 5 e 12:** estrutura e nomes da proposta aprovados (**Busquets** e **Xabi Alonso**, em `inteligencia/`); vídeos só por arquivo que ele subir, sem download automático de vídeo, áudio ou legenda; nada agendado, os agentes só rodam quando chamados. Tetos em uso: os sugeridos na proposta, não confirmados como definitivos.

**História:** como Guilherme, quero um agente que estude todo dia, de verdade, como os canais dark fazem seus vídeos (roteiro, ritmo, edição, voz, gancho, retenção, thumbnail, ferramentas), para o Contexto Explica aprender com métodos reais e não com resumos de terceiros.

**Contexto (pedido em 2026-11-03):** hoje o setor de inteligência cataloga canais, títulos, thumbnails, produção e métricas (`inteligencia/README.md`: **Hugo Souza**, **Fagner**, **André Carrillo**, **Raniele**, **Yuri Alberto**, **Vitinho**) e o **Memphis** levanta referências virais por semana. Nenhum deles assiste ao vídeo inteiro com quadros e transcrição. O aprendiz preenche essa lacuna: o ponto central é ASSISTIR (ver a imagem e ouvir a fala), não só ler títulos e descrições. Solução técnica fica para o refinamento.

**Como se encaixa e difere (sem duplicar):**
- **Hugo Souza** cataloga canais (quem é, nicho, tamanho); o aprendiz usa o catálogo, não refaz.
- **Fagner** (títulos) e **André Carrillo** (thumbnails) analisam em escala só o que é visível na listagem; o aprendiz entra fundo em poucos vídeos e pode passar achados a eles.
- **Raniele** (produção) analisa como se produz; o aprendiz fornece evidência observada vídeo a vídeo, e o **Raniele** consolida o padrão.
- **Memphis** acha o que está viral toda semana; o aprendiz estuda o método por trás, todo dia.
- **Vitinho** continua consolidando; o relatório do aprendiz vira insumo dele.
- O **Luiz Henrique** decide a estrutura final: dentro do setor de inteligência ou um setor novo, e como se liga aos agentes acima.

**Critérios de aceite:**
1. Existe o agente em `.claude/agents/` (definição por **Luiz Henrique**), com limites escritos: só estuda e relata; não publica, não escreve roteiro do canal, não guarda senha, token ou cookie.
2. Roda quando chamado (`python inteligencia/aprendiz/rodar.py aprendiz`), sem tarefa agendada, por decisão do Guilherme; cada execução fica registrada com data e custo em `inteligencia/aprendiz/historico.jsonl`.
3. Limite por execução definido e respeitado: de 1 a 3 vídeos por rodada e um teto por rodada (US$ 0,30) e por dia (US$ 1,10), registrados; ao atingir o teto, a rodada para e diz isso. Sem arquivo para estudar, a rodada não chama o Claude.
4. Para cada vídeo com arquivo em `inteligencia/aprendiz/_entrada/`, o agente assiste de verdade: quadros em intervalos e nos pontos-chave (gancho, viradas, final) e fala por transcrição local do áudio.
5. Sem o arquivo do vídeo, o agente pede ao Guilherme que o suba e diz exatamente onde colocar; enquanto não vier, o vídeo fica marcado como "não assistido". Nada é baixado automaticamente.
6. Cada execução grava um relatório com data em pasta própria (ex.: `inteligencia/aprendiz/AAAA-MM-DD/`; caminho final por **Luiz Henrique**) contendo, por vídeo: link, nível de acesso em texto ("assistido com quadros e transcrição", "só transcrição", "só lido: título e descrição"), transcrição ou trecho curto, lista dos quadros analisados com o que mostram, e honestidade explícita sobre o que NÃO foi visto.
7. O relatório lista os métodos observados (roteiro, ritmo, edição, voz, gancho, retenção, thumbnail, ferramentas) com evidência (tempo do vídeo ou quadro) e uma seção "como aplicar ao Contexto Explica", coerente com `CLAUDE.md` (Shorts, nicho Análise de Comportamento Social e Gerações, regras do canal).
8. Nunca copia roteiro: trechos citados são curtos e só como evidência; a aplicação ao canal é descrita como método, não como texto reaproveitado. Verificação: nenhum relatório traz fala transcrita longa nem proposta de reutilizar texto de terceiro.
9. Direitos autorais e termos das plataformas respeitados: sem raspagem em massa, sem contornar proteção, volume baixo por rodada, vídeos baixados guardados só para estudo local e fora do repositório (ou ignorados pelo git); regras conferidas contra `inteligencia/README.md`.
10. Nenhuma credencial é pedida nem guardada; quando o acesso exigir login, o agente pede o vídeo baixado, não senha nem cookie.
11. Falha em uma rodada (vídeo indisponível, ferramenta ausente) gera relatório de falha legível, sem derrubar as próximas rodadas do dia.
12. Teste de aceite com 2 vídeos reais: um com arquivo (relatório completo com quadros e transcrição; pode ser do próprio canal) e um só com link, sem arquivo (relatório marca "não assistido" e pede o arquivo ao Guilherme); **Alisson** confere o relatório contra estes critérios.

**Precisa do Guilherme:** quando quiser um estudo, baixar e colocar o vídeo na pasta indicada (sem senha, sem cookie, sem login compartilhado). Confirmar ou trocar os tetos.

**Pergunta respondida em 2026-11-05 (só arquivos que ele subir; texto original mantido):** quais ferramentas de download e transcrição são aceitáveis? Exemplos para considerar, sem decidir: yt-dlp para baixar, legenda automática do próprio YouTube, Whisper local para transcrever, ffmpeg para extrair quadros (já está nas dependências do projeto). Pontos a pesar: termos do YouTube, custo (Whisper local é grátis mas gasta máquina), e se baixar vídeo de terceiros só para estudo é aceitável para ele.

**Depende de:** PROG-014 (fonte dos vídeos), embora arquivo fora da fila também seja estudado.

## PROG-014 · Melhoria (novo agente) · Prioridade média (sugerida) · Status: em teste na Sprint 01 (entrou em 2026-11-05)
**Dono:** Luiz Henrique (`luiz-henrique-ecossistema`, cria o agente e decide a estrutura)
**Cartão:** Agente de referências de canais dark (nicho aberto e o nosso)

**História:** como Guilherme, quero uma lista curada de referências de conteúdo de canal dark, de qualquer nicho e do nosso, com o que aprender de cada uma, para o aprendiz estudar o que vale a pena e a squad ter bons exemplos.

**Contexto (pedido em 2026-11-03):** o **Memphis** gera `referencias_virais.md` uma vez por semana, focado no que viraliza; o **Hugo Souza** cataloga canais. O novo agente é o curador de referências para estudo: procura em nicho ABERTO (qualquer nicho de canal dark, para aprender formato e técnica) e no NOSSO (Análise de Comportamento Social e Gerações, para ver concorrência e lacunas), e entrega o que o aprendiz deve assistir. Solução fica para o refinamento.

**Como se encaixa e difere:** difere do **Memphis** por não medir viralidade da semana e sim valor de aprendizado, e por cobrir qualquer nicho; difere do **Hugo Souza** por entregar vídeos específicos para estudar, não o catálogo de canais (usa o catálogo como fonte). Passa os vídeos ao aprendiz (PROG-013). A estrutura final (setor de inteligência ou novo) é do **Luiz Henrique**; ele também decide se este agente absorve ou apenas consome o trabalho do **Memphis**.

**Critérios de aceite:**
1. Existe o agente em `.claude/agents/`, com limites escritos: só pesquisa e recomenda; não baixa vídeo em massa, não publica, não guarda senha, token ou cookie.
2. Cada entrega é uma lista curada com data (arquivo em pasta de inteligência definida por **Luiz Henrique**), separada em duas partes: nicho aberto e nosso nicho.
3. Cada referência traz: link do vídeo e do canal, nicho, formato (Short ou longo, estilo visual, voz), por que serve ao Contexto Explica e o que aprender (método específico, por exemplo gancho, ritmo ou thumbnail).
4. Cada referência declara de onde veio (catálogo do **Hugo Souza**, referências do **Memphis** ou busca própria) e é só de canal dark, sem pessoa falando para a câmera (memória do Guilherme).
5. A lista é curta e priorizada (ex.: até 10 por entrega, com ordem de estudo) e não repete referência já estudada, conferindo a pasta de relatórios do aprendiz.
6. Entrega ao aprendiz uma fila de vídeos para a rodada (1 a 3 por rodada, conforme o limite do PROG-013) em formato que o aprendiz leia sem intermediário.
7. Roda quando chamado (`python inteligencia/aprendiz/rodar.py curador`), sem tarefa agendada, por decisão do Guilherme, com teto por execução (US$ 0,20) e registro em `inteligencia/aprendiz/historico.jsonl`.
8. Respeita direitos autorais e termos das plataformas: só links e metadados públicos, sem raspagem em massa; conferido contra `inteligencia/README.md`.
9. Execução sem resultado útil (busca vazia, fonte indisponível) registra isso em texto claro, sem inventar referência.
10. **Alisson** confere uma entrega real contra os critérios 2 a 6.

**Precisa do Guilherme:** confirmar ou trocar o teto; opcionalmente indicar nichos abertos que já lhe interessam e canais que ele admira (somente nomes e links, nada de senha).

**Depende de:** integração com PROG-013.

## PROG-015 · Bug · Prioridade alta · Status: fazendo na Sprint 01 (implementação iniciada em 2026-11-03)
**Dono:** Endrick (proposta; confirmar no refinamento)
**Cartão:** Ação da próxima etapa precisa funcionar e mostrar o resultado

**Contexto (reportado em 2026-11-03):** no topo da tela de produção, “Resolver o parecer do Vini (auditoria de texto)” não executava o encaminhamento, e “Iniciar vídeo final” também só abria o painel, sem iniciar o render. No `app.js`, só o caso especial `resolver_parecer` disparava uma operação; os demais rótulos eram tratados como navegação. A chamada precisa cumprir o texto exibido, ou dizer claramente que apenas abre uma etapa.

**História:** como Guilherme, quero que cada chamada para ação do topo execute a ação descrita ou me leve claramente à ação específica, e mostre o resultado real, para saber se o sistema fez o que prometeu.

**Critérios de aceite:**
1. Para cada estado em que a chamada aparece, o rótulo descreve corretamente o efeito do clique: se apenas navega, diz “Abrir ...”; se promete resolver/iniciar, dispara essa ação.
2. Ao clicar, a interface dá retorno imediato e inequívoco (por exemplo, estado em andamento/desabilitado ou confirmação da etapa aberta) e mantém o vínculo com a etapa/versão correta.
3. Sucesso só aparece depois da confirmação do efeito real; o estado/resultado permanece visível após atualização da tela.
4. Se a ação estiver bloqueada ou falhar, a interface explica o motivo e o próximo passo, sem exibir sucesso falso.
5. Cliques repetidos não duplicam ações nem execuções.
6. Teste e2e reproduz “Resolver o parecer do Vini” e um CTA de início (ex.: “Iniciar vídeo final”), verifica a operação/API e o estado resultante; testa também erro/bloqueio e falha contra o comportamento atual. Não basta verificar a presença do botão nem exibir um toast.
7. Funciona nos tamanhos de tela em que a chamada aparece (computador e celular, se habilitado).

**Refinamento técnico obrigatório:** identificar a operação correta para cada tipo de estado da chamada. Uma etapa bloqueada pelo parecer do Vini pode exigir ação do usuário; o sistema não deve aprovar nem alterar o parecer automaticamente. Se o controle for apenas navegação, ajustar o texto e dar retorno visível ao abrir a etapa.

**Prioridade na Sprint 01:** entrou como primeiro item da fila após pedido do Guilherme em 2026-11-03. O planejamento original excede a capacidade se todos os itens forem mantidos; reavaliar PROG-011 e o escopo do Catálogo (PROG-003) na próxima atualização de capacidade.

## PROG-017 · Melhoria (novo setor) · Prioridade baixa (sugerida) · Status: novo (fora da Sprint 01; sem prazo)
**Dono:** Zico (a definir no refinamento; proposta: Thiago Silva com o Luiz Henrique, que cria agentes e setores)
**Cartão:** Setor de LinkedIn (tirar o Lamine Yamal do setor de produtividade)

**Contexto (pedido do Guilherme em 2026-11-09):** o agente de LinkedIn (**Lamine Yamal**, `lamine-yamal-linkedin`) hoje vive dentro do setor de produtividade. O Guilherme quer um setor próprio, com contrato e README como os demais setores.

**História:** como Guilherme, quero um setor de LinkedIn separado da produtividade, para preparar meus posts com rascunhos e aprender com o que já publiquei, sem que nada saia sem a minha aprovação.

**Escopo a definir com o Guilherme (antes de refinar):** quais agentes compõem o setor (só o **Lamine Yamal** ou mais), formato dos rascunhos, e como os prints dos posts já publicados chegam (pasta, envio pelo Telegram ou outro).

**Critérios de aceite (enxutos):**
1. Existe `linkedin/README.md` (ou pasta equivalente definida no refinamento) com contrato do setor: missão, entradas, saídas, limites e fluxo; o ecossistema (`ecossistema/README.md`) lista o setor e o agente deixa de constar como parte da produtividade.
2. O setor gera rascunhos de posts em arquivo, marcados como "rascunho, não publicado".
3. O Guilherme pode enviar prints de posts já publicados e o setor os usa para atualizar seu conhecimento de tom e formato; há registro do que foi aprendido, com a data.
4. Nunca publica: nenhuma ação de postar ou agendar ocorre sem aprovação explícita do Guilherme, registrada por post. Teste/conferência: o fluxo termina em rascunho aguardando aprovação.
5. Sem dado da empresa: rascunhos e aprendizados não contêm dados internos, de clientes ou confidenciais; o contrato traz essa regra e há verificação documentada (checklist) antes de entregar um rascunho.
6. Nenhuma senha, token ou chave em arquivos do setor.

**Precisa do Guilherme:** definir o escopo acima e confirmar a prioridade.

**Prioridade (justificativa):** baixa; não trava o Corte nem o canal. Sobe para média se o Guilherme quiser usar o LinkedIn de forma regular.

## PROG-018 · Épico · Prioridade alta · Status: em execução fora do quadro (autorizado em 2026-11-09)
**Cartão:** Sistema central do ecossistema dentro do Corte (uma interface só)

**Autorização (2026-11-09):** o Guilherme disse explicitamente "faz já, fora do quadro, não precisa de Trello" para este épico e para PROG-019 a 023, e deixou os agentes decidirem as perguntas abertas. Vale a exceção da regra do quadro: registrado aqui depois; sem cartão no Trello e sem `quadro.md`.

**Nome da aplicação:** passa a ser **"Ecossistema do Guilherme"**.

**Decisões tomadas (respondem as perguntas 1 a 6 abaixo; o Guilherme pode rever):**
1. Pastas FORA da lista de documentos: `produtividade/`, `financas/`, `.env`, acessos, LinkedIn e `voz/`. As demais pastas propostas na pergunta 1 entram.
2. "Último prompt" = marcador "visto" que o Guilherme limpa (ação "marcar tudo como visto"); itens alterados depois dele aparecem como novo/alterado.
3. Resumo de 2 linhas por regra determinística a partir dos arquivos, sem API paga e sem agente.
4. Espelho antigo (`espelho_sistema.html`, gerador e hook) mantido como está; sem hook novo.
5. Só no computador (127.0.0.1); sem celular/`--rede` para estas telas.
6. Dashboard (PROG-023): sinais escolhidos pelos agentes na refinagem (vídeos em andamento, agentes ativos, sprint, pendências para o Guilherme), conforme os dados reais.

**Contexto (pedido do Guilherme em 2026-11-09):** hoje há o espelho (`espelho_sistema.html`, gerado por `tools/gerar_espelho.py` e disparado por `tools/hook_espelho.py`) e o Corte (`python -m corte`, `estudio/`) separados. O Guilherme quer UMA interface, dentro do Corte, com dashboard, agentes, setores, documentos e resumo, onde faz vídeo, mexe em agente e vê setores. O objetivo da semana dele é organizar e simplificar o ecossistema antes de um novo canal dark: ver depressa o que mudou desde o último prompt é o ganho principal.

**Fora do escopo (decisão do Guilherme):** a interface do **Ronaldo** (`produtividade/painel.py`) fica à parte e não é tocada. Esta etapa é só interface: sem mudança no fluxo de vídeo, nos agentes nem nos roteiros.

**Regra transversal de confidencialidade (vale para todas as histórias):** dados da empresa do Guilherme (documentos pessoais e de trabalho, `produtividade/` pessoal, LinkedIn, acessos) NÃO aparecem em telas versionadas nem em arquivo gerado que entre no git. Documentos fora de uma lista de pastas permitidas não são listados; o que for gerado com conteúdo sensível fica em local ignorado pelo git (`.gitignore`) ou só é servido em memória pelo Corte local.

**Histórias (ordem sugerida):** PROG-019 (aba Documentos + data) -> PROG-020 (atualização automática) -> PROG-021 (aba Resumo, 2 linhas) -> PROG-022 (espelho dentro do Corte) -> PROG-023 (dashboard geral: agentes e setores).

**Critério de aceite do épico:** as cinco histórias aceitas; o Guilherme abre só o Corte e vê Documentos, Resumo, Agentes e Setores; o `espelho_sistema.html` standalone deixa de ser necessário (ou vira apenas export).

**Perguntas em aberto (para o Guilherme):**
1. "Documento" = quais arquivos? Proposta: `.md`/`.txt`/`.json` de `ecossistema/`, `programacao/`, `inteligencia/`, `prompts/`, `.claude/agents` e `output/<slug>/` (notas, roteiro, metadados). Fora: `produtividade/` pessoal, `.env`, acessos, LinkedIn, `voz/`. Confirma?
2. O que conta como "último prompt": o horário do último envio dele, a última sessão do Claude Code, ou "desde a última vez que abri a aba" (marcador "novo desde que você viu")?
3. Quem escreve o resumo de 2 linhas: texto determinístico derivado dos arquivos/commits (grátis, previsível) ou um agente (custo e variação)? Proposta: determinístico, sem API paga.
4. O espelho antigo (`espelho_sistema.html`) deve ser mantido como export ou aposentado depois da PROG-022?
5. A tela do Corte é só local (127.0.0.1) ou também no celular (`--rede`, com senha)? Isso afeta a regra de confidencialidade.
6. Dashboard (PROG-023): quais 3 a 5 números ou sinais importam mais (ex.: vídeos em andamento, agentes ativos, sprint, pendências para ele decidir)?

## PROG-019 · Melhoria · Prioridade alta · Status: em execução fora do quadro (autorizado em 2026-11-09; filha do épico PROG-018)
**Cartão:** Aba Documentos no Corte, recentes no topo, com data da última atualização

**História:** como Guilherme, quero uma aba Documentos que liste os documentos do ecossistema com o mais recente no topo e a data/hora da última atualização de cada um, para ver o que mudou sem procurar pasta por pasta.

**Critérios de aceite:**
1. Existe a aba Documentos no Corte, acessível pela navegação principal, em computador e (se o celular estiver habilitado) no celular.
2. Cada linha mostra nome, caminho relativo, setor/pasta de origem e data e hora da última modificação no horário local (dd/mm/aaaa hh:mm), em texto.
3. A ordem padrão é da modificação mais recente para a mais antiga; teste cria dois arquivos com datas diferentes e confere a ordem.
4. Só entram arquivos de pastas permitidas (lista fixa e documentada, resposta da pergunta 1 do PROG-018); teste coloca um arquivo em `produtividade/` pessoal, `.env` e `acessos` e confere que NÃO aparecem na lista nem na resposta da API.
5. Clicar num documento abre o conteúdo (leitura) dentro do Corte; arquivo fora da lista permitida não abre nem por URL direta (teste de tentativa de acesso a caminho proibido e a `..`).
6. Lista grande não trava: mostra os N mais recentes com opção de ver mais, e a abertura da aba leva menos de 2 s com o repositório atual (medido, registrado em `qa/PROG-019.md`).
7. Teste automatizado novo em `estudio/testes/` e resultado real em `qa/PROG-019.md`. Nenhum arquivo de agente, roteiro ou fluxo de vídeo é alterado.

**Depende de:** pergunta 1 do PROG-018. **Valor:** alto.

## PROG-020 · Melhoria · Prioridade alta · Status: em execução fora do quadro (autorizado em 2026-11-09; filha do épico PROG-018)
**Cartão:** Atualização automática da aba Documentos (sem ação manual)

**História:** como Guilherme, quero que a aba Documentos reflita sozinha qualquer alteração feita por mim ou por um agente, para ver o que saiu do último prompt sem rodar nada.

**Critérios de aceite:**
1. Alterar, criar ou apagar um documento permitido faz a lista mudar na tela aberta em até 5 s, sem clicar em nada e sem recarregar a página (teste e2e altera um arquivo e observa a lista).
2. Funciona para alterações vindas de qualquer origem (editor, agente do Claude Code, script), porque a fonte é o estado real dos arquivos e não depende do hook do espelho. Teste: alteração por script externo aparece.
3. Itens alterados desde o marcador escolhido (resposta da pergunta 2 do PROG-018) ficam destacados como "novo/alterado" com texto, não só cor, e há ação para "marcar tudo como visto".
4. Sem alterações, não há recarga nem piscar da tela; com a aba fechada não há varredura constante (consumo baixo, registrado em `qa/PROG-020.md`).
5. Várias alterações em rajada (agentes em paralelo) resultam em uma lista consistente, sem duplicados, e sem travar o Corte.
6. Se a atualização falhar, a tela mostra aviso visível ("atualização parada, última leitura às hh:mm") em vez de ficar parada em silêncio.
7. Teste automatizado novo e resultado real em `qa/PROG-020.md`.

**Depende de:** PROG-019 e pergunta 2 do PROG-018. **Valor:** alto.

## PROG-021 · Melhoria · Prioridade alta · Status: em execução fora do quadro (autorizado em 2026-11-09; filha do épico PROG-018)
**Cartão:** Aba Resumo: até 2 linhas sobre as últimas coisas executadas no ecossistema

**História:** como Guilherme, quero uma aba Resumo com no máximo 2 linhas sobre o que foi executado por último no ecossistema, para me situar em segundos.

**Critérios de aceite:**
1. A aba Resumo existe no Corte e mostra no máximo 2 linhas (limite verificado por teste, mesmo com muitas alterações).
2. O texto cita fatos reais e recentes (ex.: quais documentos/setores mudaram por último e quando), derivados dos dados da PROG-019/020; teste com fixtures confere que o resumo muda quando os arquivos mudam e não inventa item que não existe.
3. Mostra a data/hora da base usada, para ele saber o quão fresco é o resumo.
4. Respeita a regra de confidencialidade: nunca cita nome ou conteúdo de documento fora da lista permitida (teste).
5. Sem alteração recente, diz isso em uma linha, em vez de ficar vazio.
6. Sem custo: não chama API paga (confirmado no relatório). Se a resposta à pergunta 3 do PROG-018 for "agente", este critério é revisto antes de refinar.
7. Teste automatizado novo e resultado real em `qa/PROG-021.md`.

**Depende de:** PROG-019 (fonte dos dados) e pergunta 3 do PROG-018. **Valor:** alto.

## PROG-022 · Melhoria · Prioridade alta · Status: em execução fora do quadro (autorizado em 2026-11-09; filha do épico PROG-018)
**Cartão:** Mover o conteúdo do espelho para dentro do Corte

**História:** como Guilherme, quero ver dentro do Corte tudo o que hoje só existe no espelho, para abrir uma interface só.

**Critérios de aceite:**
1. Antes de implementar, **Thiago Silva** e **Iniesta** inventariam o que o `espelho_sistema.html` mostra hoje (lista em `programacao/tecnico/PROG-022.md`) e o Guilherme confirma o que migra e o que se descarta; cada bloco migrado ou descartado fica marcado.
2. Cada bloco migrado aparece numa aba/seção do Corte e mostra os mesmos dados do espelho no momento da comparação (teste compara contagem e títulos, por bloco).
3. O Corte lê os dados direto dos arquivos, sem depender de rodar `tools/gerar_espelho.py` nem do hook; o hook e o gerador seguem funcionando até o Guilherme decidir aposentá-los (pergunta 4 do PROG-018), sem regressão.
4. Confidencialidade: nenhum conteúdo de `produtividade/` pessoal, acessos ou LinkedIn é exibido nem gravado em arquivo versionado; teste confere que o que o Corte serve e o que entra no git não contêm esses caminhos, e o status do git não muda com o uso da tela.
5. A interface do **Ronaldo** (`produtividade/painel.py`) permanece intacta (nenhum arquivo dela alterado; conferido por diff no relatório).
6. Navegação coerente com as abas existentes do Corte (desenho do **Iniesta**), em computador e celular se habilitado.
7. Regressão: as baterias de `estudio/testes/` seguem verdes (resultado real em `qa/PROG-022.md`).

**Depende de:** PROG-019 a 021 (reaproveita as leituras) e perguntas 4 e 5 do PROG-018. **Valor:** alto. Pode ser fatiada na refinagem por blocos do espelho se for grande.

## PROG-023 · Melhoria · Prioridade média (parte do épico alto) · Status: em execução fora do quadro (autorizado em 2026-11-09; filha do épico PROG-018)
**Cartão:** Dashboard geral do ecossistema: agentes e setores

**História:** como Guilherme, quero uma tela inicial com visão geral dos setores e agentes (e o que precisa de decisão minha), para organizar e simplificar o ecossistema.

**Critérios de aceite:**
1. A tela mostra, por setor (produção do canal, inteligência, programação, produtividade só como nome e contagem, sem dados pessoais), os agentes e o estado de cada um, reaproveitando as definições do PROG-003/016 (Ao vivo e Catálogo) sem divergir deles.
2. Mostra os 3 a 5 sinais escolhidos pelo Guilherme (pergunta 6 do PROG-018) com valor e data da leitura.
3. Do dashboard se chega à ficha do agente, à aba Documentos e ao Resumo em um clique.
4. A lista de setores e agentes vem dos arquivos reais (`.claude/agents`, READMEs dos setores) e atualiza sozinha (mesma regra do PROG-020); setor ou agente novo aparece sem editar código.
5. Nenhum dado pessoal ou confidencial aparece (mesma regra transversal), com teste.
6. Alterar agente pela tela (o "mexer em agente" do pedido) fica FORA desta história: se o Guilherme quiser, vira item novo, porque toca nos agentes. Hoje o Corte já tem a edição de agentes; o dashboard só linka.
7. Teste automatizado e resultado real em `qa/PROG-023.md`.

**Depende de:** PROG-016 e PROG-003 (aceitos ou na sprint), PROG-019/020 e pergunta 6 do PROG-018. **Valor:** médio-alto; fica por último porque Documentos e Resumo já respondem a "o que mudou".

## SPRINT 02 · "Sistema único: visual H + Finanças primeiro" (registrado em 2026-11-11 por ordem do Guilherme)

**Origem:** Sprint 01 encerrada antes do fim (12 Feito, PROG-011 devolvido); proposta do **Ancelotti** em `programacao/melhoria.md` (seção "Reestruturação por ordem do dono · 2026-11-11") e `programacao/trello_pendente.md`. Ids 024 a 035 conferidos livres (confirmados como definitivos). Documentação base: `ecossistema/sistema_unico/01 a 05` e protótipo `ecossistema/prototipo_estilos/h/`. Quadro e `sprints/sprint-02.md` são do **Xavi**; o Trello não foi tocado.
**Meta:** o Guilherme abre uma interface única no visual H e a primeira tela viva é Finanças, com dados reais do **Casemiro**.
**Legenda:** Tam. P/M/G; "Back-end" = toca servidor; "Firmino" = participa do visual (propõe desenho e CSS; só **Rodrygo** e **Endrick** gravam código, conforme o contrato). Teste de cada item é parte do pronto (README do setor); o PROG-035 só consolida.
**Regra transversal:** nenhum dado financeiro, pessoal (`produtividade/`, acessos, LinkedIn) ou segredo em tela versionada, `dados.js` do protótipo, espelho ou arquivo que entre no git.

| Ordem | Id | Item | Valor | Tam. | Prioridade |
|---|---|---|---|---|---|
| 1 | PROG-024 (a, b) | Finanças no H | A | G | Alta |
| 3 | PROG-025 | Casca do app | A | M | Alta |
| 4 | PROG-026 | Servidor único (estende o Corte) | A | G | Alta |
| 4 | PROG-027 | Espera você | A | M | Alta |
| 5 | PROG-028 | Canal (absorve PROG-011) | M | M | Média |
| 6 | PROG-029 | Agentes no H | M | M | Média |
| 7 | PROG-030 | Editores de agentes e fluxos | M | G | Média |
| 8 | PROG-031 | Console de jobs | M | M | Média |
| 2 | PROG-032 | Assets de imagem (desbloqueado; acelerar) | A | P | Alta |
| 10 | PROG-033 (a a d) | Clipes, Inteligência, Trabalho, Programação | M | G | Média |
| 11 | PROG-034 | Acesso pelo celular | M | M | Média |
| 12 | PROG-035 | Testes e2e do sistema único | A | M | Alta (fecha no fim) |

Por que nesta ordem: fatia vertical visível primeiro (Finanças de ponta a ponta, sem back-end), depois a base (casca, servidor) e as telas que dependem dela. Ordem e valor são sugestão; quem decide é o Guilherme.

### PROG-024 · Melhoria · Prioridade alta · Status: Code Review (Sprint 02, item 1)
**Dono:** Endrick (tela), Rodrygo (gerador), Marquinhos (git); **Firmino** no visual; **Iniesta** só se tocar fluxo. **Tam.:** G. **Back-end:** não (gerador local, sem token). **Depende de:** nada. **Privacidade:** o Guilherme autorizou prosseguir no comentário do card; arquivos pessoais foram removidos do índice e seguem ignorados localmente.
**História:** como Guilherme, quero ver no visual H meu saldo atual, vencimentos a pagar, movimentos e categorias vindos dos CSV do **Casemiro**, para saber minha situação financeira sem abrir planilha.
**Fatias (cabem no WIP 2 por dev):**
- **024a, gerador local (Rodrygo; Marquinhos no git).** Lê `financas/*.csv` (`saldos`, `movimentos`, `transferencias`), `pendencias.md` e `contexto.md`; grava SÓ em local ignorado pelo git (sugestão: `estudio/dados/`); sem token, sem API, sem servidor; regerável por um comando; nunca marca nada como pago nem escreve nos CSV. Se o Ronaldo/`financas/dashboard.py` o chama junto é decisão do **Thiago Silva**.
- **024b, tela no H (Endrick + Firmino).** Só começa com o 024a pronto.
**Critérios de aceite:**
1. Os dados vêm de `financas/*.csv`: saldo atual (valor informado em 2026-11-11, com a data de cada saldo exibida), saldo total e por conta, vencimentos a pagar (data, valor, dias restantes), movimentos recentes, receitas x gastos do mês e gasto por categoria.
2. Os valores da tela batem com os CSV; teste com CSV de fixture inventado (nunca os reais) confere cada bloco; alterar a fixture e regerar muda a tela.
3. Vencimentos mostram status em TEXTO e cor do H (vencido, vence hoje, a pagar, pago), nunca só cor; receitas x gastos em barras e demais cores de status seguem o visual H (`g/comum_gh.js`), modos claro e escuro.
4. Faixa de alertas do **Casemiro** com a origem de cada um (conta sem saldo confirmado, saldo velho, pago sem lançamento, pendência aberta).
5. Estado vazio (sem CSV ou sem linhas) e estado de erro (CSV ilegível, gerador falhou) em português, dizendo o que fazer; mostra data/hora da última leitura.
6. Privacidade: o arquivo gerado com dados financeiros está no `.gitignore` e nunca vai ao git; o CSV real e os arquivos gerados não aparecem no `git status` (teste e conferência do **Marquinhos**); antes de qualquer commit, `git ls-files financas` é conferido e, se houver rastreio, para e vai ao Guilherme.
7. Nenhum dado financeiro vai para API, servidor externo, `dados.js` do protótipo, espelho, `qa/` ou `revisoes/` (a validação com dados reais é só local, sem copiar valores).
8. Funciona em 1280 px e em 390 px, sem rolagem lateral; o acesso remoto continua fechado e só será avaliado no PROG-034.
9. Aceite visual: captura da tela ao Guilherme antes do Code Review; **Alisson** e **Thiago Silva** conferem; teste automatizado com fixture e resultado real em `qa/PROG-024.md`.

### PROG-024c · Melhoria · Prioridade alta · Status: liberado fora do quadro pelo Guilherme (2026-11-12); só o Fluxo 1; Endrick pode começar
**Dono:** Endrick (tela); **Rodrygo** só se faltar rota de leitura; desenho do **Iniesta** em `programacao/ux/PROG-financa-detalhes.md` (seção "FLUXO 1", itens 1.1 a 1.5.7). **Tam.:** M. **Back-end:** não, em princípio (reaproveita `editarMovimento` e `POST /api/financas/movimentos/editar`).
**Autorização:** o Guilherme disse "fora do quadro" em 2026-11-12. Vale a exceção da regra do quadro: registrado aqui; sem cartão no Trello e sem `quadro.md` por ora. Decisão do **Zico**: o pedido é filho do PROG-024 (Finanças no H), por isso 024c. Se o **Xavi** quiser cartão depois, usa este id.
**FORA do escopo (ainda não liberado):** Fluxo 2 da spec (alertas e pendências: resolver, editar, apagar com desfazer, "Marcar como pago" com lançamento no saldo). Não implementar até o Guilherme liberar. Em A pagar, a spec cita o botão "Marcar como pago" (1.4): NÃO entra nesta entrega; a lista A pagar é só leitura e com "Editar".
**História:** como Guilherme, quero clicar em cada um dos 4 números da ilha (Saldo disponível, Recebido no mês, Gasto pago no mês, A pagar no mês) e ver a lista de movimentos que formam aquele número, para entender de onde ele vem sem abrir planilha.
**Critérios de aceite:**
1. Os 4 cards viram `<button>` com `aria-label` conforme a spec (1.1), chevron "›", foco de teclado visível; Enter e Espaço abrem; clique responde em até 100 ms.
2. O painel abre com o título e a lista corretos de cada card: Recebido = receitas recebidas; Gasto pago = gastos pagos; A pagar = gastos a pagar (inclui vencidos); Saldo = recebidos e gastos pagos do mês, com as contas no topo e o texto "O saldo do banco não é a soma destes movimentos...".
3. Cabeçalho do painel mostra mês, contagem e soma da lista; a soma bate com o número do card. Se não bater, aparece o aviso em texto (1.3). Teste com fixture inventada confere a soma dos 4 painéis (nunca CSV real).
4. Desktop (acima de 900 px): painel lateral de 480 px; 390 px: folha de tela inteira com "Voltar", sem rolagem lateral. `<dialog>` com Esc fechando; foco vai ao título ao abrir e volta ao card ao fechar. `#/financas/saldo|recebido|gasto|a-pagar` permite o botão voltar do navegador fechar o painel.
5. Seletor de mês (padrão mês atual, meses de `meses`), busca local por descrição e categoria, ordenação por data; busca sem resultado mostra a mensagem com "Limpar busca".
6. A pagar agrupa em Vencidos, Vencem em até 3 dias e Mais adiante, cada grupo com contagem e soma, com situação em texto ("Venceu há 3 dias", "Vence hoje"...), nunca só cor. Receita e gasto também com texto e sinal ("+"/"−"), não só cor.
7. "Editar" em cada linha abre o modal existente sem alterá-lo; ao salvar, o painel recarrega a lista e os cards da ilha atualizam.
8. Estados em português, cada um dizendo por que e o que fazer: carregando (esqueleto só se passar de 300 ms), vazio (um texto por painel, tabela 1.5.3), erro com "Tentar de novo" e "Ver detalhes" sem mostrar valor antigo, sem permissão (403: "Finanças só abre neste computador", cards desabilitados com o motivo; 401: sessão expirada), dados velhos (`idade_dias` maior que 3: faixa com "Atualizar leitura").
9. Com "Ocultar valores" ligado, painel, cabeçalho, soma e avisos continuam mascarados.
10. Privacidade: nenhum valor real em teste, `qa/`, `revisoes/`, captura versionada ou arquivo no git; `git status` não muda com o uso da tela; acesso remoto continua fechado (PROG-034 decide).
11. Teste automatizado com fixture cobrindo os 4 painéis, vazio, erro, 403 e a soma; resultado real em `qa/PROG-024c.md`; captura da tela ao Guilherme antes do aceite; **Alisson** e **Thiago Silva** conferem.
**Perguntas para o Guilherme (não bloqueiam; assunção em itálico):** (a) renomear o card para "Gasto pago no mês"? *Assunção: manter "Gasto no mês" com a legenda "só o que já foi pago"; painel usa "Gasto pago no mês".* (b) Finanças no celular? *Assunção: só no computador, como já é hoje.*
**Registro:** pedido liberado verbalmente pelo Guilherme em 2026-11-12; registro feito pelo **Zico** depois. Nada foi aceito ainda.

### PROG-025 · Melhoria · Prioridade alta · Status: em andamento (Sprint 02, item 2)
**Dono:** Endrick; **Firmino** participa. **Tam.:** M. **Back-end:** não. **Depende de:** 024b (aproveita o componente).
**História:** como Guilherme, quero uma casca única no visual H, com navegação em 8 grupos, tema claro/escuro e busca Ctrl K, para entrar em qualquer área do ecossistema de um lugar só.
**Critérios de aceite:** 1) navegação em 8 grupos conforme `ecossistema/sistema_unico/`, com o grupo atual destacado em texto; 2) tema claro e escuro persistem entre aberturas; 3) Ctrl K abre a busca e leva ao grupo/tela escolhido, Esc fecha; 4) Finanças (024) abre dentro da casca sem refazer; 5) 1280 px e 390 px sem rolagem lateral; 6) estado vazio de grupo sem tela ainda, em português; 7) teste automatizado e `qa/PROG-025.md`.

### PROG-026 · Melhoria (back-end) · Prioridade alta · Status: em andamento (Sprint 02, item 3)
**Dono:** Rodrygo, **Thiago Silva** (decisão técnica). **Tam.:** G. **Back-end:** SIM. **Refinamento técnico:** concluído por **Thiago Silva** em `programacao/entregas/PROG-026-refinamento.md`. **Firmino:** não.
**História:** como Guilherme, quero um servidor único (o Corte estendido) que sirva a casca e os dados do sistema, para não abrir vários programas.
**Critérios de aceite:** 1) rotas `/api/sistema/*` com lista de permissão de pastas; caminho fora da lista ou com `..` é recusado (teste); 2) absorve `/painel` e `/central` sem regressão do que existe; 3) só em 127.0.0.1 por padrão; 4) nada de `produtividade/` pessoal, `financas/`, `.env`, acessos, LinkedIn ou `voz/` servido por rota genérica; 5) falha de uma rota não derruba o servidor, erro legível; 6) baterias de `estudio/testes/` seguem verdes (regressão do Corte) e resultado real em `qa/PROG-026.md`; 7) a interface do **Ronaldo** (`produtividade/painel.py`) permanece intacta.

### PROG-027 · Melhoria · Prioridade alta · Status: novo (Sprint 02, item 4)
**Dono:** Endrick; **Firmino**. **Tam.:** M. **Back-end:** sim. **Depende de:** 025, 026.
**História:** como Guilherme, quero uma tela "Espera você" com tudo que depende de mim (aceites, aprovações, gates), para decidir sem caçar pendência.
**Critérios de aceite:** 1) lista aceites pendentes (`programacao/aceites/`), versões aguardando aprovação e gates, cada um com origem, item e há quanto tempo, em texto; 2) aprovar ou aceitar grava o registro real (arquivo de aceite ou aprovação do Corte) e só mostra sucesso após a gravação confirmada; 3) nada é aceito ou aprovado automaticamente; 4) vazio: "Nada espera você agora"; 5) erro de leitura/gravação em português, sem sucesso falso; 6) clique repetido não duplica registro; 7) teste e `qa/PROG-027.md`.

### PROG-028 · Melhoria · Prioridade média · Status: novo (Sprint 02, item 5; absorve PROG-011)
**Dono:** Endrick, Rodrygo; **Firmino**. **Tam.:** M. **Back-end:** sim. **Depende de:** 025, 026.
**História:** como Guilherme, quero ver o Canal: projetos, status de cada vídeo e cronograma de postagem (só leitura), para saber se a próxima postagem está coberta.
**Critérios de aceite:** 1) lista de projetos/vídeos com o status do PROG-012 (já aceito) em texto; 2) cronograma de postagem só leitura, por data, derivado de `output/fila_postagem.txt` e do status (critérios 1, 3 a 5, 8 e 10 a 13 do PROG-011, que fica absorvido: o texto original permanece no PROG-011); 3) indicador "Pronto para postar" / "Sem vídeo pronto para DD/MM" com o que falta; 4) a tela não publica, não muda privacidade nem altera a fila; 5) estados vazio e erro em português; 6) cadência em configuração (assunção do PROG-011 até o Guilherme decidir); 7) teste com relógio injetável e `qa/PROG-028.md`. A edição do cronograma (critério 2 do PROG-011) fica fora e volta ao backlog geral.

### PROG-029 · Melhoria · Prioridade média · Status: novo (Sprint 02, item 6)
**Dono:** Endrick; **Firmino**. **Tam.:** M. **Back-end:** usa `ao_vivo.py` existente. **Depende de:** 025, 026.
**Critérios de aceite:** Ao vivo e Catálogo no visual H, reaproveitando as definições aceitas do PROG-003 e PROG-016 (mapeamento de estados, polling existente, tempo na tarefa, motor Claude/Codex); sem divergir entre as duas abas para o mesmo agente; vazio e erro em português; 390 px e 1280 px; teste cobre os quatro estados e `qa/PROG-029.md`; a edição de agentes do Corte continua funcionando (regressão).

### PROG-030 · Melhoria · Prioridade média · Status: novo (Sprint 02, item 7)
**Dono:** Endrick, Rodrygo; **Firmino**. **Tam.:** G. **Back-end:** reuso do Corte, só casca nova. **Depende de:** 026, 029.
**Critérios de aceite:** editores de agentes e de fluxos acessíveis pela casca H, com as mesmas capacidades do Corte atual; salvar só mostra sucesso após gravar; erro e validação em português; nenhum agente ou fluxo é alterado sem ação explícita; regressão das baterias de `estudio/testes/` verde; teste e `qa/PROG-030.md`. Fatiar na refinagem (agentes / fluxos) se ultrapassar a capacidade.

### PROG-031 · Melhoria (back-end) · Prioridade média · Status: novo (Sprint 02, item 8)
**Dono:** Rodrygo, Endrick; **Firmino**. **Tam.:** M. **Back-end:** sim. **Depende de:** 026.
**Critérios de aceite:** console de jobs mostra executor, estado, log e tempo de cada job; log atualiza sozinho no polling existente; falha mostra motivo em português; iniciar/parar só com ação explícita e sem duplicar por clique repetido; log não expõe segredo (teste com valor sentinela); teste e `qa/PROG-031.md`.

### PROG-032 | Melhoria | Prioridade alta | Status: em andamento, sem bloqueio humano (Sprint 02, acelerado)
**Dono:** Endrick; **Firmino**. Tam.: P. Back-end: nao. Validacao integral: cinco P0, um P1 e quatro P2 sem candidato claro; 16 P2 reprovados. Prompts em `output/032_asset_check/prompts_pendentes.md`; mapear candidatos, gerar lacunas e integrar apos 025.
**Critérios de aceite (provisórios):** assets integrados à casca H nos locais previstos, com texto alternativo; peso e tempo de carregamento dentro de limite acordado com o **Firmino**; sem asset de origem desconhecida ou sem direito de uso; teste visual e `qa/PROG-032.md`.

### PROG-033 · Melhoria · Prioridade média · Status: novo (Sprint 02, item 10; fatiar a/b/c/d)
**Dono:** Endrick, Rodrygo; **Firmino**. **Tam.:** G. **Back-end:** sim. **Depende de:** 025, 026.
**Fatias:** 033a Clipes; 033b Inteligência; 033c Trabalho; 033d Programação (cada uma com critérios próprios na refinagem).
**Critérios comuns:** cada tela lê dados reais por rota com lista de permissão; vazio e erro em português; 033c e 033d seguem a regra transversal (nenhum dado pessoal ou de empresa em tela versionada ou arquivo no git; só local e ignorado); teste e `qa/PROG-033x.md` por fatia.

### PROG-034 · Melhoria · Prioridade média · Status: novo (Sprint 02, item 11)
**Dono:** Endrick, Rodrygo; **Firmino**. **Tam.:** M. **Back-end:** sim. **Depende de:** 025, 026; decisão do Guilherme sobre Finanças no celular.
**Critérios de aceite:** acesso por `--rede` com senha, 390 px, uma coluna, sem rolagem lateral; sem senha não abre nada; telas com dado sensível (Finanças, Trabalho, Programação) só abrem no celular se o Guilherme tiver liberado explicitamente (padrão: só computador); senha nunca em arquivo versionado; teste e `qa/PROG-034.md`.

### PROG-035 · Dívida de teste · Prioridade alta (fecha no fim) · Status: novo (Sprint 02, item 12)
**Dono:** Alisson (com Rodrygo e Endrick). **Tam.:** M. **Firmino:** não. **Back-end:** não. **Depende de:** cresce a cada item; fecha no fim.
**Critérios de aceite:** e2e cobre o fluxo de cada tela entregue (Finanças com fixture, casca, Espera você, Canal, Agentes) e a regressão do Corte; nenhum teste afrouxado para passar; confere que o `git status` não muda com o uso das telas; resultado real por bateria em `qa/PROG-035.md`; `estudio/README.md` descreve como rodar.

### Decisões e dependências do Guilherme
- Sprint 02 retomada e compromisso de trabalho autorizados em 11/11; PROG-032 acelerado em paralelo, mantendo o foco no dashboard.
- Finanças por acesso remoto segue fora do escopo comprometido; a decisão será necessária apenas se o PROG-034 entrar em execução.
- Revisão visual da 024b: captura enviada pelo **Ronaldo** no Telegram; o Guilherme respondeu positivamente sobre os dados e pediu edição, entregue nesta rodada. Implementação segue para Code Review.
- Privacidade da pasta `financas/`: autorização recebida no comentário do card; verificação atual confirma somente scripts `.py` rastreados, fontes financeiras ignoradas.
- Cadência de postagem pertence ao PROG-011, devolvido ao backlog geral; não bloqueia a Sprint 02.

## Ideias futuras
(vazio; o **Zico** abastece com pedidos do Guilherme)
