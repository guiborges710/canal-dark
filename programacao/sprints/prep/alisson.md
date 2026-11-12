# Pré-planning · QA (Alisson) · 2026-11-03

Regra do dono respeitada: nada foi executado (sem bateria, servidor ou vídeo). Tudo abaixo vem de leitura de código. Onde digo "provável", falta rodar para confirmar.

## 1. Mapa das baterias (`estudio/testes/`)

| Bateria | Cobre | Situação hoje |
|---|---|---|
| `testar_estilos.py` | registro/estilos, bibliotecas de camadas | não lida a fundo; rodar na regressão |
| `testar_roteiro.py` | contagem de números/gráficos, tipos de roteiro | independe do Corte; baixo risco |
| `testar_reserva_codex.py` | limite do Claude, escolha de motor, comando do codex (montado, nunca executado), nota "não pôde rodar" (l.80) | cobre o backend (`executor.py` 158-209); não cobre o front (não exibe `motor`) |
| `validar_real.py` | comandos reais sem simulador (Chatterbox, `run.py`, `--mock`) | l.146 confere `nao_aplica` da auditoria no modo simulado (continua certo, `fluxo.py` 264); fixture usa só sketch (l.66-67), não cobre componentes nos 4 estilos. **Gasta GPU/render: só com ordem do Guilherme** |
| `e2e_interface.mjs` | Chrome real, cópia descartável, executor simulado (`claude_simulado.py`, `comandos_simulados.py`) | l.111 e l.153 esperam "Aprovar roteiro vN e liberar componentes" (rótulo montado em `fluxo.py` ~752; confirmar texto real ao rodar). Nenhum caso de motivo de "não se aplica" nem de "Iniciar cenas" |
| `e2e_corte.mjs` | aceites do Corte, fluxo `canal`, Vini bloqueia, editor, fluxos | **l.419** ainda busca o nó `se_sketch`; o `.catch(()=>true)` faz o teste passar sem checar nada (falso verde). l.420 `ap("ap_componentes").catch(()=>{})` engole erro. l.302 `arestas.length === 5` e l.251 grafo real: conferir se contam o grafo antigo. l.392 aprova `ap_componentes` (ok) |
| `e2e_estilos.mjs` | estilos, temas, troca de estilo, export | **l.193** afirma que o Raphinha NÃO é acionado em `cartoon_alive`: contradiz a decisão de hoje (componentes nos quatro estilos, `fluxo.py` 263). Falhará. **l.307-310** assume `ap_componentes` só no sketch; confirmar nos outros estilos. l.40 mensagem de erro lista nós |
| `e2e_celular.mjs` | layout `--rede` | precisa de casos para motivo de não-aplica e Iniciar cenas |
| `comparar_midia.py`, `preparar_caixa.py`, `comandos_simulados.py`, `claude_simulado.py`, `referencia_sketch.json` | apoio | `claude_simulado.py` existe: é o executor sem custo |

Testes que contam nós do grafo: não achei assert numérico de nós do grafo padrão em arquivos `*test*`. O que existe é `grafos.py:407` (campo `nos`) e `e2e_corte.mjs` l.251/302. Procurar também `testar_*` dentro de `estudio/` ao rodar. `grafos.py:124-150` migra o fluxo publicado (`_sem_se_sketch`); falta teste dessa migração (execução antiga com o nó vs. nova).

Lacunas novas, sem nenhum teste hoje: motivo de não-aplica na tela (`fluxo.py:272-287`, `app.js:307`); bloqueio do fluxo visível; `motor`/`motor_nota` no front.

## 2. Plano de teste

Princípio: executor simulado (`ESTUDIO_SIMULADOR`, `estudio/config.py:15`; `claude_simulado.py`; `comandos_simulados.py`). Zero token, zero render real, caixa descartável.

**PROG-001 (motivo de não-aplica)**
- Casos: (a) produção `simulado` (mock) → componentes e auditorias "não se aplica" com texto de `fluxo.py` 279 e 282; (b) pasta de origem terminal (`origem != estudio`) → texto da l.280; (c) cenas sem `fala` → narração (l.286); (d) cenas formato `antigo` (l.285); (e) produção normal estilo cartões/cartoon/colagem → componentes SE aplica e sem aviso (critério 6); (f) projeto com versão de componentes já existente → aplica (l.261).
- Validar: API `/api/producoes/<slug>` → `etapas[].motivo_nao_aplica` (`fluxo.py:702`); no Chrome, o texto de `app.js:307` visível na etapa, sem abrir log, em viewport desktop e celular (`e2e_celular`).
- Pontos de atenção: o motivo não cita "estilo/fase de aprendizado" (critério 2 pede a regra real) e não diz o que fazer (critério 3). Os textos atuais cobrem só parte; devolver se faltar.

**PROG-002 (Iniciar cenas)**
- Casos: clique com pré-requisito ok → job criado e estado "em andamento" imediato; clique sem dependência (componentes pendentes) → mensagem de por quê; outra etapa rodando → mensagem; clique duplo e clique em duas abas (padrão do `e2e_corte` l.397-398: `Promise.all` com 2 `liberar`, exatamente 1 `ja===false`); falha do agente simulado → erro na tela; sucesso → nova versão em `cenas`.
- Dados: caixa de `preparar_caixa.py`, fluxo `canal`, simulado. Para provar que "falha sem a correção" (critério 5): rodar o teste novo contra o commit anterior/stash, só se o Guilherme autorizar.
- Cobrir também os estilos sem sketch, pois a causa pode vir da remoção do `se_sketch`.

**PROG-003 (Agentes em tempo real)**
- Dados: semear jobs no SQLite da caixa (status `rodando`, `fila`, `falhou`, `ok`; campo `motor` claude/codex; slug e etapa) em vez de rodar agente. Casos: ocioso, trabalhando (tempo "há N min" avançando com relógio falso), fila, falhou (slug+etapa), estado vazio em pt-BR, clique leva ao vídeo/etapa, mudança de estado sem recarregar (inserir job durante o teste e esperar 1 ciclo de polling), 50 jobs (tempo de resposta do endpoint e do desenho), endpoint falhando (interceptar a requisição no puppeteer → "desatualizada", último estado mantido), edição de agente (regressão de `corte_agentes.js`, `e2e_corte` ~l.500). Celular: `e2e_celular`.
- Nota: o refinamento técnico precisa decidir como mapear job → agente (hoje `spec.agente`); sem isso o teste não tem contrato.

## 3. Riscos e exigências de pronto

Riscos: (1) falsos verdes (l.419 do `e2e_corte` e os `.catch(()=>{})`); (2) testes antigos vermelhos misturados com falhas reais, escondendo regressão; (3) a causa de PROG-001/002 não está investigada nem há `entregas/<id>.md`; sem relatório do autor não valido; (4) o mesmo fluxo é tocado por três itens, com risco de conflito na regressão; (5) polling + 50 jobs pode pesar o SQLite do servidor; (6) reserva com Codex em conflito com a regra "só Claude" (decisão do Guilherme pendente); (7) mock não prova render real, `validar_real.py` custa tempo.

Exijo, além da definição do README: relatório em `entregas/<id>.md` com a causa real; teste novo que falha sem a correção; baterias `e2e_interface`, `e2e_corte`, `e2e_estilos`, `e2e_celular`, `testar_reserva_codex` e `testar_estilos` verdes (nenhum teste desligado/relaxado para passar; `.catch` que engole erro não vale); fluxo antigo e novo cobertos; zero token e zero `--allow-paid`; nada commitado; critério do aceite do Guilherme registrado.

## 4. Estimativa para deixar a regressão verde
**M** (provável 1 a 2 dias). Atualizar e2e_estilos l.193/307-310, e2e_interface l.111/153 (se o rótulo mudou), e2e_corte l.419-420 e contagens; criar casos novos de não-aplica e Iniciar cenas. Vira **G** se a primeira rodada mostrar quebra além do mapeado ou se for necessário acertar o contrato de PROG-003 junto.
