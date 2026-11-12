# Sprint 02

Dono: **Xavi**. Estado: **ABERTA e retomada em 2026-11-11**, por ordem do Guilherme. O foco atual é somente o dashboard do ecossistema. Fim previsto: 2026-11-25 (2 semanas; confirmar na planning).

AVISO DE IDS: o **Zico** ainda não gravou estes itens em `backlog.md` (conferido em 2026-11-11). Os ids PROG-024 a PROG-035 são PROVISÓRIOS, vindos da proposta do **Ancelotti** (`melhoria.md`, seção "Reestruturação por ordem do dono"). Conferir com o **Zico** antes de espelhar no Trello.

## Meta
Sistema único: visual H + Finanças primeiro. O Guilherme abre uma interface única no visual H, e a primeira tela viva é Finanças, com os dados reais do **Casemiro**, lidos só localmente.

## Escopo (ordem; ids provisórios)
| # | Id | Item | Resp. | Firmino | Tam. | Depende de | Compromisso |
|---|---|---|---|---|---|---|---|
| 1 | PROG-024 | Finanças no H: 024a gerador local, 024b tela | **Rodrygo** (gerador), **Endrick** (tela), **Marquinhos** (git) | sim | G | nada; desenho do **Iniesta** se tocar fluxo | FIRME |
| 2 | PROG-032 | Assets do H: completar o manifesto e integrar na casca | **Endrick** | sim | P | 5 P0 pendentes segundo validacao revisada; 119 WebP validos integrados parcialmente; lotes de prompts atualizados | ACELERAR; em paralelo |
| 3 | PROG-025 | Casca do app: 8 grupos, tema claro/escuro, Ctrl K | **Endrick** | sim | M | 024b | FIRME |
| 4 | PROG-026 | Servidor único: estender o Corte (`/api/sistema/*`, lista de permissão) | **Rodrygo**, **Thiago Silva** | não | G | refinamento pronto em `entregas/PROG-026-refinamento.md` | FIRME |
| 5 | PROG-027 | Espera você | **Endrick** | sim | M | 025, 026 | previsto (entra se sobrar) |
| 6 | PROG-028 | Canal (status PROG-012, cronograma só leitura = retomar PROG-011) | **Endrick**, **Rodrygo** | sim | M | 025, 026 | previsto |
| 7 | PROG-029 | Agentes no H (reuso PROG-003/016) | **Endrick** | sim | M | 025, 026 | previsto |
| 8 | PROG-030 | Editores de agentes e fluxos | **Endrick**, **Rodrygo** | sim | G | 026, 029 | previsto |
| 9 | PROG-031 | Console de jobs | **Rodrygo**, **Endrick** | sim | M | 026 | previsto |
| 10 | PROG-033 | Clipes, Inteligência, Trabalho, Programação (fatias a/b/c/d) | **Endrick**, **Rodrygo** | sim | G | 025, 026; dado pessoal | previsto |
| 11 | PROG-034 | Acesso pelo celular | **Endrick**, **Rodrygo** | sim | M | 025, 026; decisão do Guilherme | previsto |
| 12 | PROG-035 | Testes e2e do sistema único e regressão do Corte | **Alisson** (com **Rodrygo**, **Endrick**) | não | M | cresce a cada item | consolidação no fim |

Compromisso firme: itens 1 a 3 (024, 025 e 026). A 032 recebe preparação acelerada em paralelo à 024b e integra assim que a casca 025 existir; validar o lote e as lacunas P0 antes de declarar pronta. A 026 depende de decisão técnica do **Thiago Silva**. Os demais previstos em ordem e sujeitos à capacidade medida na daily. Os 12 itens excedem uma sprint.

Teste de cada item faz parte da definição de pronto; o PROG-035 é a consolidação.

## Regras de WIP
- Máximo 2 em Fazendo por dev; máximo 3 em Em teste no total.
- O 024 em duas fatias (a e b) para caber no WIP.
- Nenhum commit, publish ou gasto pago sem o Guilherme pedir. Dado financeiro real: nunca em `qa/`, `dados.js`, espelho, API ou git.

## Riscos
1. Privacidade dos dados: arquivos de origem ficam fora de qualquer commit; verificar o `.gitignore` antes de preparar release e preservar o controle local.
2. Escopo: 12 itens, vários G, 2 devs, sem velocidade confiável. Por isso compromisso firme só nos 3 primeiros.
3. Revisão da 024b: captura enviada pelo **Ronaldo** no Telegram; o Guilherme deu retorno positivo sobre os dados e a edição solicitada foi entregue. Segue para Code Review.
4. Servidor único (026) é o maior risco técnico; o 024 não depende dele (gerador local).
5. Saldo desatualizado: conferir com o **Casemiro** a data dos saldos; a tela mostra a data de cada saldo.
6. Dado pessoal em Trabalho e Programação (033): mesma regra do PROG-018.
7. Firmino fora do README (acima).

## Decisões pendentes do Guilherme
(nenhuma nos itens ativos, conforme a mensagem e os comentários do Guilherme em 11/11; acesso financeiro por celular permanece fora do compromisso atual e será decidido somente ao chegar ao PROG-034.)

## Hipótese do Ancelotti (uma só): fatia vertical visível primeiro
Entregar Finanças de ponta a ponta (dados reais, tela, teste) antes de casca e servidor, e mostrar cedo ao Guilherme.
- Medir: (a) dias úteis do 024 de Fazendo a Pronto para aceite (meta: até 3); (b) devoluções do **Alisson** e do **Thiago Silva** no 024 (meta: no máximo 1); (c) Guilherme ver a tela com dados reais antes do Code Review; (d) itens que mudam de ordem após a planning (meta: no máximo 1).
- Sucesso: 024 aceito em até 5 dias úteis sem vazamento no `git status`. Fracasso: 024 depender da casca ou do servidor; então inverter (026 primeiro).

## Cerimônias
Planning curta: a marcar com o Guilherme (pauta: meta, corte firme, decisões acima). Daily: 10:30, estado por item; primeira medição da hipótese na daily de 14/11. Review e retro: 25/11.

## Resultado
(preencher na review)

## Pontos da retro
(preencher na retro; **Ancelotti** registra a melhoria a testar)
