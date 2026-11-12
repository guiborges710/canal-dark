# Setor de programação · Contrato

Criado em 2026-11-03 por **Luiz Henrique**. Responde a **Luiz Henrique**. Chefe técnico: **Thiago Silva**.

## Função
Evoluir o código deste repositório (canal-dark) com metodologia ágil: o Corte (`estudio/`), o pipeline (`media/`, `run.py`, `compliance.py`) e o motor de render (`render/`). Não é o código de app do trabalho do Guilherme (esse é feito na IA da empresa).

## Equipe

| Craque | id técnico | Papel |
|---|---|---|
| **Zico** | `zico-po-programacao` | PO: backlog, critérios de aceite, prioridade, aceite final |
| **Xavi** | `xavi-scrum-master` | Scrum Master: quadro, cerimônias, WIP, impedimentos |
| **Ancelotti** | `ancelotti-agile-coach` | Agile Master: coach de processo, retro de melhoria, métricas de fluxo |
| **Thiago Silva** | `thiago-silva-tech-lead` | Tech lead e arquiteto: refinamento técnico, revisão, decisões |
| **Rodrygo** | `rodrygo-dev-back` | Dev back-end (Python) |
| **Endrick** | `endrick-dev-front` | Dev front-end (web do Corte) |
| **Iniesta** | `iniesta-ux-corte` | UX da interface do Corte |
| **Alisson** | `alisson-qa` | QA: valida critérios e regressão |
| **Marquinhos** | `marquinhos-devops-release` | DevOps e release: ambiente, notas de versão |

## Estrutura de arquivos (cada agente escreve só no seu)

| Arquivo/pasta | Dono |
|---|---|
| `backlog.md` | **Zico** |
| `quadro.md`, `sprints/sprint-NN.md` | **Xavi** é o dono (ordem e WIP); na sprint ativa quem grava as movimentações é o maestro (`maestro.py`), não os agentes |
| `melhoria.md` | **Ancelotti** |
| `tecnico/<id>.md`, `tecnico/decisoes.md` | **Thiago Silva** |
| `ux/<id>.md` | **Iniesta** |
| `entregas/<id>.md` | **Rodrygo** / **Endrick** (o autor do item) |
| `qa/<id>.md` | **Alisson** |
| `release/` | **Marquinhos** |

O código em si (`estudio/`, `media/`, `render/`, `run.py`) é editado só por **Rodrygo** e **Endrick**.

## Regra do quadro (decisão do Guilherme, 2026-11-03)
O Kanban/Trello "Kanban Trabalho" (espelho em `produtividade/kanban.md`; cartões `[Sprint NN] [PROG-NNN]`) é a **única fonte de trabalho** do setor.
- Devs e time (**Rodrygo**, **Endrick**, **Iniesta**, **Alisson**, **Marquinhos**, **Thiago Silva**) só fazem o que está no quadro, e só itens da **sprint ativa**.
- Pedido que não chegou ao quadro não é feito: volta ao **Zico**, que registra em `backlog.md` e leva ao quadro (`trello_programacao.py`).
- Única exceção: o Guilherme dizer explicitamente "faz já, fora do quadro"; o **Zico** registra depois.
- Quem move o cartão é **só o maestro** (`programacao/maestro.py`), aplicando a decisão que o agente dono da coluna grava em `programacao/maestro/decisoes/PROG-NNN.json`, no `quadro.md` e no Trello. Nenhum agente move cartão nem edita `quadro.md` à mão durante a sprint ativa. **Xavi** continua dono do quadro como PO de processo: decide a ordem e o WIP.
- Fluxo dos estados: Backlog da sprint, Fazendo (puxado por **Xavi** na ordem do quadro), Em teste (o dev conclui e **Alisson** valida), Code Review (**Thiago Silva**), Pronto para aceite (**Zico** confere os critérios e recomenda) e Feito, só depois do aceite do Guilherme registrado em `programacao/aceites/PROG-NNN.md` (o maestro verifica o arquivo). A coluna "Em teste" existe também no Trello.
- Cada entrega cita o id PROG-NNN.

## Quadro
Colunas: Backlog da sprint · Em refinamento técnico · Fazendo · Em teste · Pronto para aceite · Feito · Bloqueado. WIP: 2 em Fazendo por dev, 3 em Em teste.

## Cadências
- **Sprint de 1 semana** (a combinar com o Guilherme). Meta única por sprint.
- **Planning** (início): **Zico** apresenta itens prontos, **Thiago Silva** estima e divide, **Xavi** fecha a sprint.
- **Daily** (10:30 cada dia útil): **Xavi** resume por item, impedimentos e próximos passos. Participantes: **Zico**, **Xavi**, **Ancelotti**, **Thiago Silva**, **Rodrygo**, **Endrick**, **Iniesta**, **Alisson**, **Marquinhos**, **Valverde** (transversal, engenharia de IA).
- **Review** (fim): demonstra o que foi aceito ao Guilherme; **Zico** recolhe feedback.
- **Retro** (fim): **Xavi** conduz; **Ancelotti** registra a melhoria a testar na próxima sprint.
- **Refinamento** (contínuo): **Zico** + **Thiago Silva** (+ **Iniesta** se tocar a tela).

## Fluxo de trabalho (paralelo)

Cada coluna do quadro tem UM agente dono. O maestro (`programacao/maestro.py`) chama o dono a cada 15 min, enquanto a sprint estiver ABERTA, quando há cartão na coluna dele. O dono age (ou diz por que o cartão está parado) e grava `programacao/maestro/decisoes/PROG-NNN.json`; só o maestro move o cartão no `quadro.md` e no Trello.

| Coluna | Dono (id técnico) | O que faz | Saídas permitidas |
|---|---|---|---|
| Backlog da sprint | **Xavi** (`xavi-scrum-master`) | puxa o próximo item, na ordem do quadro, quando o dev dono tem menos de 2 itens em Fazendo; senão explica por que espera | Fazendo; Bloqueado |
| Em refinamento técnico | **Thiago Silva** (`thiago-silva-tech-lead`), com **Zico** e, se tocar tela, **Iniesta** | fecha nota técnica e critérios | Backlog da sprint |
| Fazendo | o dev dono do item: **Rodrygo** (`rodrygo-dev-back`) ou **Endrick** (`endrick-dev-front`) | implementa com teste primeiro, roda as baterias, escreve `programacao/entregas/PROG-NNN.md` com resultados reais; se não avançou, diz por quê | Em teste; Bloqueado |
| Em teste | **Alisson** (`alisson-qa`) | valida cada critério, roda a regressão, grava `programacao/qa/PROG-NNN.md` | Code Review (aprovado); Fazendo (devolvido, com o que falta) |
| Code Review | **Thiago Silva** | revisa o código real, grava `programacao/revisoes/PROG-NNN.md` com `**Veredito: APROVADO.**` ou `**Veredito: DEVOLVIDO.**` | Pronto para aceite; Fazendo |
| Pronto para aceite | **Zico** (`zico-po-programacao`) | confere os critérios de aceite contra qa/ e revisoes/ e recomenda aceitar ou recusar; o aceite é do Guilherme, em `programacao/aceites/PROG-NNN.md` | Feito (só com o aceite do Guilherme); Fazendo |
| Bloqueado | **Xavi** | tenta destravar; se depende do Guilherme, diz exatamente o que precisa dele | Fazendo; Backlog da sprint |
| Feito | **Marquinhos** (`marquinhos-devops-release`) | registra o item em `programacao/release/notas-sprint-01.md` | nenhuma |

1. Guilherme reporta ou pede algo; **Zico** registra no backlog com critérios de aceite (sem investigar a causa).
2. **Thiago Silva** refina: nota técnica, riscos, testes exigidos. **Iniesta** desenha, se houver tela.
3. **Xavi** coloca na sprint e no quadro. Devs puxam itens do backlog respeitando WIP (2 em Fazendo por dev).
4. **Rodrygo** ou **Endrick**: teste primeiro, código, bateria rodada, relatório em `entregas/`.
5. **Alisson** valida cada critério e roda a regressão; aprova (move para Code Review) ou devolve.
6. **Thiago Silva** revisa o código em paralelo, chamado sozinho pelo maestro (`maestro.py`, substitui o antigo `monitor_cr.py`) quando há item na coluna Code Review. Grava `revisoes/PROG-NNN.md` com o veredito; o maestro aplica no quadro e no Trello.
   - Devs NÃO ficam bloqueados: **Rodrygo** e **Endrick** puxam próximo item do backlog enquanto espera revisão (fluxo paralelo).
7. **Thiago Silva** aprova ou devolve. Se aprova, vai para "Pronto para aceite".
8. **Zico** confere os critérios e recomenda; o Guilherme aceita ou recusa em `aceites/PROG-NNN.md`. Só então o maestro move para Feito e **Marquinhos** registra nas notas da release.
9. O Guilherme decide se commita (só quando ele pedir).

## Definição de pronto
Um item só vai para Feito quando: (1) todos os critérios de aceite passam, comprovados por **Alisson**; (2) existe teste novo ou ajustado para a mudança, em `estudio/testes/` ou ao lado do módulo; (3) as baterias relevantes rodaram e o resultado real está registrado; (4) o código foi revisado por **Thiago Silva**; (5) a documentação afetada (`estudio/README.md`, `CLAUDE.md` só se o Guilherme pedir) está atualizada; (6) **Zico** conferiu e recomendou, e o Guilherme aceitou, com o aceite registrado em `programacao/aceites/PROG-NNN.md` (sem esse arquivo o maestro não move para Feito); (7) todos os itens da checklist de critérios no cartão do Trello estão marcados como concluídos com base nessas evidências, antes de mover o cartão para **Feito**; (8) nada foi commitado, publicado ou gasto fora do combinado.

## Quem aciona quem
- Guilherme aciona **Zico** (pedidos e bugs) e, via **Luiz Henrique**, o setor inteiro. Pedido amplo vai ao **Thiago Silva**.
- **Zico** aciona **Thiago Silva** e **Iniesta** (refinamento). **Xavi** aciona os devs, **Alisson** e **Marquinhos** conforme o quadro.
- **Alisson** devolve ao dev; bug novo vai ao **Zico**. **Ancelotti** aciona só a si e propõe mudanças ao **Xavi** e a **Luiz Henrique**.
- Aviso ao Guilherme: via **Ronaldo**. Mudança de canal/vídeos: **De Bruyne**.

## O que o setor NÃO faz
- Não commita nem faz push sem o Guilherme pedir. Não publica nada no YouTube nem roda `publish`.
- Não muda código sem teste. Não gasta com API paga (`--allow-paid`) sem autorização.
- Não toca em `output/` de vídeos, `voz/`, `.env` nem guarda senha, token ou chave.
- Não produz conteúdo de canal nem código de app do trabalho do Guilherme.
- Codex é reserva: roda os mesmos agentes só quando o Claude esgota o limite (regra antiga "só Claude" revogada em 2026-11-03). O espelho `.codex/` é gerado por `tools/sincronizar_codex.py`, não editado à mão.

## Baterias de teste disponíveis
`estudio/testes/`: `testar_estilos.py`, `testar_roteiro.py`, `validar_real.py`, `comparar_midia.py`, `comandos_simulados.py`, e2e: `e2e_interface.mjs`, `e2e_corte.mjs`, `e2e_celular.mjs`, `e2e_estilos.mjs`. **Alisson** e os devs confirmam em `estudio/README.md` como executar cada uma.

## Suposições (trocar se quiser)
Sprint de 1 semana; **Thiago Silva** como chefe técnico; o backlog continua sendo a fonte, em Markdown, e é espelhado no Kanban geral ("Kanban Trabalho", Trello) como cartões `[PROG-NNN]` por `produtividade/kanban_programacao.py` (mapa de colunas em `produtividade/README.md`). Quem move esses cartões é só o maestro (`programacao/maestro.py`), aplicando as decisões dos agentes donos de coluna no `quadro.md` e no Trello; **Xavi** decide ordem e WIP, **Zico** mantém o `backlog.md`; o cartão nunca é apagado.
