# UX · PROG-003 · Aba "Agentes" mostra quem está trabalhando

Autor: **Iniesta** · 2026-11-03 · Pré-planning (reunião 16:50). Proposta, não código.

## O que existe hoje (conferido no código)
- `estudio/web/corte_agentes.js`: tela `/agentes` = lista à esquerda (`ag-lista`, busca, "＋ Novo") e detalhe à direita (editar, duplicar, desativar, testar, versões). Cada item da lista mostra craque, versão, id, descrição, "⛓ fluxos" ou "Fora dos fluxos", e "⏻ Desativado". **Nenhum sinal de atividade.** A tela carrega uma vez (`carregar`) e não faz polling; `atualizar()` só relê testes em fila do agente aberto.
- `estudio/web/corte_estudio.js` (`agentes()`, linha 220): o Estúdio de cada vídeo já tem um painel "Agentes" com uma linha por nó: craque, tarefa, selo de estado (`seloEstado`: Na espera, Em execução, Aguarda sua aprovação, Concluído, Falhou), contador de cena, barra de progresso, "Atualizado há X". Clique abre `abrirExecucao` (diálogo com log ao vivo, atualizado a cada 2 s). Reaproveitar esse vocabulário visual e de texto.
- Jobs têm `motor` e `motor_nota` (`estudio/trabalhos.py`, `fluxo.py`). Estado "fila" já existe como classe `.selo.fila`/`.pino.fila`.
- Visual: tema escuro (`--fundo #0b0b0d`, painéis `#16171a`), selos arredondados, verde = ok, vermelho = erro, azul/âmbar = ação/decisão. Celular: `celular.css`, corte em 820 px.
- Lacuna: `seloEstado` não tem "Na fila" nem "Ocioso" (só `pendente` = "Na espera"). Texto precisa ser acrescentado.

## Princípios
1. Estado sempre com ícone + palavra (nunca só cor).
2. Quem trabalha sobe para o topo; o resto fica quieto.
3. Toda linha ativa responde "quem, em qual vídeo, em qual etapa, há quanto tempo, com qual motor".
4. Se os dados podem estar velhos, a tela diz isso.

## Estados (um por agente)
| Estado | Ícone + texto | Cor | Linha mostra |
|---|---|---|---|
| Trabalhando | `◐ Trabalhando` (ícone gira devagar; sem animação se o sistema pede) | azul | vídeo, etapa, "há 2 min", motor, barra se houver progresso |
| Na fila | `⏳ Na fila` | azul claro | vídeo, etapa que espera, "aguarda há 40 s", posição se houver ("2º da fila") |
| Falhou | `✕ Falhou` | vermelho | vídeo, etapa onde falhou, "há 12 min", 1 linha do motivo, botão "Ver o que houve" |
| Ocioso | `○ Livre` (linha apagada) | cinza | só "Último trabalho: <vídeo>, há 3 h" ou "Nunca rodou" |
| Desativado | `⏻ Desativado` (já existe) | cinza | sem tentar mostrar atividade |

Nota: "Aguarda sua aprovação" (nó parado esperando o Guilherme) é diferente de "Livre". Mostrar `❚❚ Espera você` em âmbar, com o vídeo, porque é a ação mais útil do dia. Dúvida para o **Zico** (ver abaixo).

## O que cada linha ativa mostra
```
◐ Trabalhando                                  [Claude]
Olise · diretor de arte
krakatoa-geracoes · Cenas (cena 4 de 9)  ▓▓▓▓░░░░
há 2 min
```
- Linha 1: selo de estado + chip do motor à direita (`Claude` neutro; `Codex` com ponto âmbar e dica "O Claude estava no limite; este trabalho rodou no Codex", usando `motor_nota`).
- Linha 2: craque em negrito, função em cinza.
- Linha 3: vídeo (slug, ou título do projeto quando houver) + etapa em português do fluxo.
- Linha 4: tempo na tarefa, atualizado a cada segundo no navegador (contador local a partir de `iniciado_em`; não depende do servidor). Após 15 min mostrar em âmbar "há 15 min: mais que o normal" (limite a definir pelo **Zico**).

## Layout
**Computador (acima de 820 px).** A tela ganha, acima da lista atual, uma faixa "Agora" ocupando a coluna esquerda inteira; o detalhe/edição à direita fica como está.
```
+-----------------------+--------------------------------------+
| Agentes     [＋ Novo] | (detalhe do agente escolhido,        |
| [Buscar...]           |  igual a hoje)                       |
| AGORA  2 trabalhando  |                                      |
|  linha ativa 1        |                                      |
|  linha ativa 2        |                                      |
|  Na fila: 1           |                                      |
| ATENÇÃO 1 falhou      |                                      |
|  linha falhou         |                                      |
| TODOS (38)            |                                      |
|  Neymar  ○ Livre ...  |                                      |
+-----------------------+--------------------------------------+
```
- Seções na ordem: Atenção (falhou e espera você), Agora (trabalhando, depois na fila), Todos (livres e desativados, ordem de hoje). Seção vazia some.
- Cada item de "Todos" ganha o selo de estado à direita do nome (hoje só mostra Desativado).
- Cabeçalho da coluna: "Atualizado agora" / "Atualizado há 20 s" (ver desatualizada).
- Clicar numa linha ativa NÃO abre mais só a ficha do agente: ver Interação.

**Celular (até 820 px).** Uma coluna só. Ordem: faixa de resumo fixa no topo ("2 trabalhando · 1 na fila · 1 falhou"), cartões "Atenção" e "Agora" com área de toque de pelo menos 44 px e a linha 3 podendo quebrar em duas, depois "Todos" recolhido (`<details>`, "Todos os agentes (38)"). Busca abaixo do resumo. O detalhe do agente abre em tela cheia com "← Agentes" (padrão já usado nas outras telas do celular). Chip do motor vai para a linha de baixo, não ao lado do nome.

## Interação (clique leva ao trabalho)
- Linha Trabalhando/Na fila: abre o Estúdio do vídeo em `/estudio/<slug>` já com o painel do nó aberto (o diálogo `abrirExecucao` com log ao vivo). Botão na linha: "Abrir no Estúdio".
- Linha Falhou: mesmo destino, e o diálogo mostra o erro no topo e o botão "Tentar de novo" (já existe em `app.js`, `tentar-de-novo`).
- Linha Livre: abre a ficha do agente (comportamento de hoje). Para chegar à ficha de um agente ativo, link secundário "Ver ficha do agente" dentro da linha (ou clique no nome). Assim nenhum clique é ambíguo: nome = ficha; resto da linha = trabalho.
- Teclado: linha é `<a>`/botão com foco visível; Enter abre.
- Retorno visível: ao clicar, a linha ganha estado "abrindo…" (desabilita por meio de `acao`) e a navegação ocorre; se o vídeo não existir mais: aviso "Este vídeo não está mais no Corte. Veja em Projetos > Arquivados."

## Estados da tela
| Situação | O que aparece |
|---|---|
| Carregando (primeira vez) | Três linhas-esqueleto cinza e o texto "Buscando quem está trabalhando…" |
| Ninguém trabalhando | Faixa "Agora": `Nenhum agente trabalhando agora.` + sub "Quando uma produção rodar, ela aparece aqui sozinha." + botão "Ir para Projetos" |
| Sem agentes cadastrados | `Nenhum agente em .claude/agents.` + "＋ Novo" |
| Tela desatualizada (consulta falhou) | Mantém o último estado e acende faixa âmbar no topo: `Sem atualização desde 14:32 (há 1 min). Mostrando o último estado conhecido.` + botão "Tentar agora". Linhas ativas ganham sufixo "(pode ter mudado)" e o contador "há X min" para de avançar. Ao voltar: faixa verde some em 3 s com "Atualizado." |
| Servidor fora do ar por > 30 s | Faixa vermelha: `O Corte não responde. Verifique se a janela do Corte ainda está aberta no computador.` (no celular: "…no computador de casa") |
| Muitos trabalhos (50) | Mostra no máx. 10 linhas em "Agora" e "+12 na fila, ver todos" que expande; histórico não entra na tela, só o estado atual por agente |
| Agente rodando e desativado depois | Mantém na seção Agora com selo extra "⏻ Desativado: termina o trabalho atual" |
| Mesmo agente com 2 trabalhos | Uma linha por agente, "Trabalhando em 2 vídeos" e lista curta dentro; clique abre a escolha |

## Textos (pt-BR)
- Título da faixa: `Agora` / `Atenção` / `Todos os agentes (N)`.
- Resumo: `2 trabalhando · 1 na fila · 1 falhou` (omitir zeros).
- Tempo: `há 40 s`, `há 2 min`, `há 1 h 10 min`. Fila: `aguarda há 40 s`.
- Motor: `Claude`, `Codex`; dica do Codex: `O Claude estava no limite; este trabalho está rodando no Codex.`
- Falhou: `Falhou em <etapa>: <motivo curto>` + `Ver o que houve`.
- Aria: cada linha tem `aria-label` completo ("Olise, trabalhando no vídeo krakatoa, etapa Cenas, há 2 minutos, motor Claude") e a região de resumo é `aria-live="polite"` para mudança de estado.

## Atualização
- Polling no mesmo ritmo do Corte (2 a 4 s, como `corte_estudio.js`). Só redesenhar quando a assinatura mudar (padrão `muda()` do Estúdio), para não perder foco nem rolagem. Não redesenhar a ficha aberta/edição em curso (usar `Corte.editando`).
- Contador "há X" é local (1 s), sem pedir ao servidor.
- Pausar polling quando a aba do navegador está oculta; ao voltar, atualizar na hora.

## Alternativas
**A. Faixa "Agora" no topo da lista atual (recomendada).** Mantém a tela conhecida (lista + ficha), adiciona seções Atenção/Agora acima de Todos, selo de estado em cada item. Menor mudança, serve igual no celular, o Guilherme continua editando agentes no mesmo lugar. Custo: coluna esquerda fica mais longa.

**B. Duas abas dentro de Agentes: "Ao vivo" e "Catálogo".** "Ao vivo" é um painel largo de cartões (estilo do painel do Estúdio) e "Catálogo" é a tela de hoje intacta. Mais espaço e zero risco para a edição (critério 12), mas esconde a atividade atrás de um clique e precisa de uma regra de qual aba abre primeiro.

**Recomendação: A**, com o selo de estado em cada item de "Todos". Se o **Thiago Silva** achar que a lista de 38 agentes fica pesada para o polling, cair para B sem mudar textos nem estados.

## Dúvidas para o Zico / Guilherme
1. "Espera você" (aprovação pendente) entra como estado do agente? Recomendo sim, é o que mais trava a produção. Se entrar, vira critério novo.
2. Limite do aviso "mais que o normal" (sugiro 15 min) e se vale por etapa.
3. Mostrar um agente que tem vários vídeos ao mesmo tempo como uma linha ou várias? Sugiro uma linha com lista.
4. Os agentes de outros setores (produtividade, inteligência) aparecem aqui também? Hoje a lista inclui tudo de `.claude/agents`.

## Outros 3 pontos de usabilidade notados (conferidos no código)
1. **Aviso de sucesso some em 3,5 s e o de erro em 7 s** (`aviso()` em `app.js:32`), sem botão para fechar nem histórico. Erro longo com motivo ("Nada foi disparado. ...") pode sumir antes de ser lido, principalmente no celular. Sugestão: erro fica até clicar; sucesso continua curto.
2. **Cada item da lista de Agentes e do Estúdio mostra "Atualizado há X"/"há X min" que só se corrige quando os dados mudam** (`quando()` é calculado no desenho; o Estúdio só redesenha quando a assinatura muda, `muda()` em `corte_estudio.js:200`). Resultado: "agora" pode ficar parado na tela por minutos. Sugestão: o mesmo contador local de 1 s proposto aqui, para toda a interface.
3. **Navegação principal não mostra que há algo acontecendo.** `corte_nav.js` tem Projetos, Agentes e Fluxos, mas nenhum indicador. Quem está em Fluxos ou Agentes não vê que uma produção falhou ou espera aprovação. Sugestão: pontinho/contador no item "Projetos" e "Agentes" (`2` trabalhando, `!` falhou), com texto para leitor de tela. Combina com esta proposta.

(Observação extra, menor: a lista de Agentes tem busca mas nenhum filtro por estado ou por fluxo; com 38+ agentes, "Mostrar só ativos/em fluxo" ajudaria.)
