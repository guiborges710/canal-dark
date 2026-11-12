# Revisão PROG-005 · Atualizar testes e2e antigos (Thiago Silva, 2026-11-04)

**Veredito: APROVADO** (código e testes). Duas correções documentais antes do aceite do Zico.

Método: leitura do código atual. Esta sessão não tem shell, então **não consegui rodar `git diff`** contra o baseline; o critério 3 foi julgado pelo estado atual das asserções, não pelo diff. Registro isso de propósito.

## Critério 3 · asserções atualizadas, não afrouxadas
Li as asserções tocadas e o entorno:
- `e2e_estilos.mjs` 194-195: Raphinha agora **precisa** ser acionado (`raph !== ""`) e receber as regras do Cartoon Vivo, e `!raph.includes("Estilo Scratch")` continua. É mais forte que "não acionado". Reflete a decisão do dono de 2026-11-03 (componentes nos 4 estilos). 312: variação do Caderno pautado chega ao Raphinha (era a falha restante da entrega; passa, 98/0).
- `e2e_corte.mjs` 419-427: o `.catch(() => true)` vazio virou asserção real (`semSketch`: sem `se_sketch` **e** com `narracao`), mais a checagem de que a narração é `ignorado` com o parecer BLOQUEADO.
- Os `confere(true, ...)` que existem (e2e_corte 89, 97, 100, 129, 322, 348) vêm todos logo depois de `waitForFunction`/`sel` com timeout que lança erro; são o padrão do arquivo, não asserções esvaziadas. Não conferi os de e2e_estilos (74, 186, 212, 232, 287, 335) e e2e_celular (118, 141) um a um; seguem o mesmo padrão pelo trecho que li (241-271).
- Não achei asserção trocada por `true` incondicional sem espera antes.

## As 3 menções a `se_sketch` (e2e_corte 419/420/427 e e2e_estilos 153)
**Aceitáveis.** São asserção de ausência e comentário, não dependência do nó. Elas guardam a regressão que o item queria evitar (voltar o nó ao fluxo padrão). O D-004 proíbe depender de id fixo para esperar um nó; aqui o id é a prova de que o nó foi removido. As menções em `estudio/grafos.py` (`_sem_se_sketch`) são a migração de produção e não são teste.

## Ressalvas (não bloqueiam, mas fecham antes do aceite)
1. Dois `.catch(() => {})` engolem erro: `e2e_corte.mjs` 421 (`ap("ap_componentes")`) e `e2e_estilos.mjs` 246 (`statusNo(a,"pesquisa",...)`). O primeiro é justificado (projeto de fora do estúdio pode não ter componentes), mas precisa de um comentário dizendo isso. **Rodrygo.**
2. `E2E_PORTA` não está no `estudio/README.md` (zero ocorrências), apesar de a entrega dizer que documenta. O QA já notou. Documentar também o risco de rodar baterias em paralelo (disco C: e memória geraram falhas falsas).
3. `entregas/PROG-005.md` está desatualizada (118/97 com 1 falha; o quadro e o QA dizem 118/152/98/63/103 sem falhas). Reescrever com o resultado real.
4. A primeira rodada em paralelo do QA teve 1 falha em `e2e_estilos` e MemoryError em `testar_estilos`. Foi atribuído à carga. Como a falha original da entrega era justamente "Raphinha não observado" no caso `teste-caderno-pautado`, sugiro o **Alisson** repetir `e2e_estilos` 2 vezes seguidas isoladas para descartar flake real.


## Fechamento (Thiago Silva, 2026-11-04)
Conferi com shell: `grep se_sketch estudio/testes` só acha asserção de ausência (e2e_corte l.419-420, 428) e um comentário (e2e_estilos l.153); comentário do `.catch` em e2e_corte l.421; `E2E_PORTA` em estudio/README.md l.167; Alisson registrou `e2e_estilos` 98/0 duas vezes isolado. A entrega ainda lista "pendente" a repetição do Alisson, já feita (só texto, sem efeito).
**Veredito: APROVADO.** Pendências fechadas.
