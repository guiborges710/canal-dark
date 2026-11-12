# Painel "Ecossistema do Guilherme": desenho de UX

Data: 2026-11-09. Autor: **Iniesta**. Para: **Endrick** (telas) e **Rodrygo** (dados). Base: `programacao/refinamento-painel-unificado.md` e PROG-018 a 023. Execução autorizada pelo Guilherme fora do quadro. Só desenho; nenhum código tocado.

## 0. Decisões que este desenho assume (do Guilherme)
- Nome na interface: **Ecossistema do Guilherme** (no lugar de "Corte"): marca no topo (`nav-marca`), título da aba do navegador (`<title>`: "Ecossistema do Guilherme") e textos de tela. Nomes técnicos (`python -m corte`, ids, arquivos) não mudam.
- Cinco abas dentro de uma página nova `/painel`: **Dashboard, Agentes, Setores, Documentos, Resumo**.
- Só no computador (127.0.0.1). Em `--rede` a página `/painel` mostra o bloqueio da seção 9, sem dados.
- Fora do painel, sem nem aparecer como nome de arquivo: `produtividade/`, `financas/`, `.env`, acessos, LinkedIn, `voz/`. A interface do Ronaldo fica à parte; o painel não linka para ela.

## 1. Navegação
Menu principal (`corte_nav.js`), da esquerda para a direita: marca "Ecossistema do Guilherme" | Projetos | Agentes | Fluxos | **Painel** (novo, ícone "◫") | espaço | "Local: só nesta máquina".
- "Painel" abre `/painel` na aba Dashboard. Cada aba tem URL própria (`/painel`, `/painel/agentes`, `/painel/setores`, `/painel/documentos`, `/painel/resumo`) para o botão Voltar funcionar e para os links do Dashboard.
- Abas em linha, sob o menu, com a ativa sublinhada e `aria-current`. Teclado: setas esquerda/direita trocam de aba.
- Em tela estreita (janela pequena), as abas rolam na horizontal; nunca quebram em duas linhas.
- Ordem das abas: Dashboard, Resumo, Documentos, Agentes, Setores (o que ele mais olha vem primeiro). Os nomes ficam exatamente como pedido.
- Todas as abas mostram, no canto direito do cabeçalho, "Lido às 14:02" (hora da última leitura bem-sucedida) e o botão "Atualizar agora". Clique no botão: o texto vira "Atualizando..." (desabilitado) por até 3 s e volta com a hora nova; se falhar, ver erro (seção 8).

## 2. Aba Dashboard
Objetivo: em 5 segundos, saber se há algo que exige ele.

Layout: faixa de 5 cartões (grade 5 colunas no computador, 1 coluna se a janela for estreita). Cada cartão é um link (clique em qualquer parte) com: título pequeno, número grande, linha de apoio e "lido às hh:mm". Abaixo, uma faixa "O que exige você" (lista curta) e o bloco "Resumo agora" (as 2 linhas da aba Resumo, com link "Ver resumo").

Os 5 sinais (ordem fixa; o 4 recebe destaque quando for maior que zero):
| # | Título | Número | Apoio | Clique leva a | Fonte |
|---|---|---|---|---|---|
| 1 | Vídeos em andamento | contagem | "2 em produção, 1 esperando você" | `/` (Projetos) | jobs do Corte e pastas de `output/` sem vídeo pronto |
| 2 | Agentes ativos agora | contagem | "de 48 agentes" (e nome dos 2 primeiros ativos) | `/painel/agentes` com filtro "Ativos" | `ao_vivo` |
| 3 | Sprint | "PROG-0xx em andamento" ou "Sprint pausada" | "Pausada por ordem sua desde 09/11" ou "x de y cartões prontos" | `/painel/setores` no setor Programação | `central.sprint_ativa` |
| 4 | Decisões pendentes suas | contagem | "PROG-018, PROG-021" (até 3 ids, resto "+2") | lista "O que exige você" logo abaixo | `decisoes/*.json` com `precisa_do_guilherme` |
| 5 | Documentos alterados hoje | contagem | "3 novos, 5 alterados" | `/painel/documentos` com filtro "Hoje" | índice de documentos |

Faixa "O que exige você" (só aparece se o sinal 4 > 0): uma linha por decisão: "PROG-021 · Resumo de 2 linhas · precisa da sua escolha: [texto do porquê, truncado em 100 caracteres] · [Abrir]". "Abrir" abre o documento ou a decisão na aba Documentos. Zero decisões: a faixa não aparece e o cartão 4 mostra "0" com apoio "Nada esperando você" (verde, com o texto, não só cor).

Estados do Dashboard:
- Carregando: 5 cartões com esqueleto cinza e o texto "Lendo o ecossistema..." sob a faixa (aria-live). Nunca tela branca.
- Vazio por cartão: número "0" e apoio explicando: "Nenhum vídeo em andamento", "Nenhum agente trabalhando agora", "Sem sprint ativa", "Nada esperando você", "Nenhum documento mudou hoje".
- Sinal indisponível (uma fonte falhou, as outras ok): só aquele cartão mostra "—" com "Não consegui ler: [motivo curto]. Tente Atualizar agora."; os demais seguem normais.
- Erro geral: ver seção 8.

## 3. Aba Resumo
Objetivo: situar em segundos. Regra dura: **no máximo 2 linhas**, cada uma com até 120 caracteres (o back já entrega cortado; a tela aplica `line-clamp: 2` no bloco e `1` por linha).

Layout: um cartão largo centralizado. Duas linhas em fonte grande. Abaixo, em cinza pequeno: "Base lida às 14:02 · atualiza sozinho a cada 10 s". Botão "Atualizar agora".

Textos (modelos, do refinamento):
- Linha 1 (última execução, ou decisão que espera ele, que tem prioridade): `14:02 · Rodrygo implementou PROG-019: em teste` ou, se houver decisão: `Espera você: PROG-021, escolha entre as opções A e B`. Falha: `14:02 · Alisson falhou em PROG-019 (veja o log)`, com o rótulo "falhou" em destaque textual.
- Linha 2 (documentos): `Atualizados: painel-ux.md, backlog.md (+3)`.

Estados:
- Vazio: linha 1 "Nada executado ainda." e linha 2 omitida. Nunca texto inventado.
- Sem alteração recente (nada nas últimas 24 h): linha 1 "Nada mudou nas últimas 24 horas." linha 2 "Última atividade: 07/11, 18:40."
- Carregando: duas barras cinza e "Lendo o último registro...".
- Erro: ver seção 8; o resumo antigo permanece visível, marcado "desatualizado".
- Confidencial: nunca cita documento fora da lista permitida (garantido no back).

## 4. Aba Documentos
Objetivo: ver o que mudou sem procurar pasta por pasta.

Layout: duas colunas. Esquerda (40%): barra de ferramentas e lista. Direita (60%): leitura do documento selecionado. Em janela estreita, a leitura abre por cima da lista com botão "Voltar à lista".

Barra de ferramentas (de cima para baixo):
1. Caixa de busca: placeholder "Buscar por título ou texto". Busca é pelo título no cliente; pelo texto, no servidor, com 300 ms de espera depois de digitar.
2. Filtros em fileira: "Todos | Hoje | Novos/alterados" (grupo exclusivo) e um seletor "Área: Todas, Programação, Agentes, Produção, Inteligência, Componentes, Prompts, Raiz".
3. Linha de status: "42 documentos · 5 novos/alterados · lido às 14:02" e o botão **"Marcar tudo como visto"**.

Cada item da lista (ordem: mais recente no topo, sempre):
- Linha 1: título do documento (primeiro `#` do arquivo; sem ele, o nome do arquivo) e, à direita, a etiqueta.
- Linha 2 (cinza): caminho relativo curto (`programacao/ux/PROG-012.md`), área, e data: "há 3 min" até 1 h; "hoje 14:02" no dia; "ontem 18:40"; depois "07/11 18:40". Dica (tooltip e `title`) com a data completa "domingo, 09/11/2026 às 14:02:31".
- Etiquetas com texto, não só cor: **Novo** (arquivo criado depois do marcador) em azul e **Alterado** (mudou depois do marcador) em laranja. Itens vistos ficam sem etiqueta e em fonte normal; não vistos ficam em negrito.
- Botão pequeno por item "Marcar como visto" (aparece ao passar o mouse e com foco de teclado). Abrir o documento (clique no item) também marca como visto, depois de 2 s com ele aberto.
- Mostra os 50 mais recentes; ao fim, "Ver mais 50" (mostra quantos faltam: "Ver mais 50 (de 128)").

Marcador "visto" (decisão que o Guilherme limpa):
- Guardado por documento, com a data/hora em que foi visto, no navegador (localStorage), sem escrever no projeto. Documento é "novo" se nunca existiu no último "visto"; "alterado" se a data de modificação for maior que o visto.
- Primeira abertura da aba (nada guardado): o marcador começa em "agora" e aparece um aviso azul na linha de status: "Primeira visita: tudo começa como visto. A partir de agora, o que mudar aparece como Novo ou Alterado." (com "Entendi" para dispensar). Evita 300 itens marcados como novos.
- "Marcar tudo como visto" abre uma confirmação leve em linha (não modal): "Marcar os 5 documentos novos/alterados como vistos?" com "Marcar" e "Cancelar". Depois do clique: etiquetas somem, a linha de status mostra "Tudo visto às 14:05" e aparece "Desfazer" por 8 s (restaura o estado anterior).
- Se o Guilherme usar outro navegador, o marcador é separado; avisar uma vez na ajuda (ícone "?" ao lado da linha de status): "O 'visto' fica guardado neste navegador."

Leitura (coluna direita):
- Topo: título, caminho, "Atualizado em 09/11/2026 às 14:02", etiqueta Novo/Alterado se houver, botão "Copiar caminho" (retorno: vira "Copiado" por 2 s).
- Corpo: texto em markdown formatado (renderizador extraído do espelho). Somente leitura; dica fixa no rodapé: "Somente leitura. Para editar, use o editor ou a tela Agentes."
- Documento de agente (`.claude/agents/*.md`): botão extra "Abrir na tela Agentes" (leva a `/agentes`).
- Documento mudou enquanto aberto: faixa amarela no topo da leitura "Este documento mudou às 14:07. [Recarregar]". Não troca o texto sozinho (evita perder a posição de rolagem).
- Sem seleção: "Escolha um documento na lista para ler aqui."
- Corpo omitido pela rede de segurança: "Conteúdo omitido: parece conter credencial. Abra o arquivo direto no seu editor." (sem mostrar nenhum trecho).
- Documento sumiu (apagado): "Este documento foi apagado ou saiu da lista permitida." com "Voltar à lista".

Atualização sozinha (PROG-020): a lista consulta a marca de mudança a cada 5 s; só recarrega quando a marca muda. Item que sobe ao topo faz uma pequena animação de destaque (fundo amarelo claro por 3 s) e, para leitores de tela, um anúncio em `aria-live=polite`: "Documento atualizado: nome". Sem mudança: nada pisca nem recarrega. Aba do navegador oculta: pausa a consulta. A cada rajada, a lista é reordenada de uma vez, sem duplicados; se o Guilherme está rolando a lista, a reordenação espera ele parar por 1 s.

Estados da aba:
- Carregando: 6 linhas em esqueleto e "Lendo documentos..."; a leitura mostra o texto do estado sem seleção.
- Vazio (índice sem nenhum arquivo): "Nenhum documento encontrado. O painel lê as pastas do ecossistema permitidas; se isso é novo, avise o Rodrygo." (sem listar caminhos).
- Filtro sem resultado: "Nenhum documento combina com 'xyz'. [Limpar busca]". Filtro Hoje vazio: "Nada mudou hoje." Filtro Novos/alterados vazio: "Você já viu tudo. Nada novo ou alterado."
- Erro de lista: faixa vermelha (seção 8), a última lista boa continua visível, marcada "desatualizada".
- Erro só na leitura de um documento: na coluna direita, "Não consegui abrir este documento. Pode estar sendo salvo agora. [Tentar de novo]".
- Bloqueado: documento fora da lista nunca aparece; se alguém tentar a URL direta, a resposta é a mesma de "apagado" (não revela que o arquivo existe).

## 5. Aba Agentes
Objetivo: quem é cada agente, em que setor, se está trabalhando, quando o prompt mudou. Leitura apenas.

Layout: barra de filtros (busca "Buscar agente"; filtros "Todos | Ativos agora | Sem setor"; seletor de setor), contagem "48 agentes · 2 ativos agora", depois tabela:
| Coluna | Conteúdo |
|---|---|
| Agente | nome com inicial maiúscula (ex.: "Iniesta") e id técnico em cinza pequeno |
| Setor | nome do setor; se não tiver, etiqueta amarela "Sem setor" |
| Estado | "Ativo agora" (com o que faz, ex.: "refinando PROG-021"), "Parado", ou "Setor inativo" (ver Setores) |
| Prompt alterado | data/hora do `.md` e etiqueta Novo/Alterado (mesmo marcador "visto" da aba Documentos) |
| Ações | "Ver ficha" e "Editar na tela Agentes" |

- "Ver ficha": painel lateral com descrição (do frontmatter), modelo, ferramentas e o prompt em leitura. Nada é editado aqui.
- "Editar na tela Agentes": leva a `/agentes` (já existente); texto de apoio na página: "Aqui você só consulta. Para editar um agente, use a tela Agentes."
- Ordem padrão: ativos primeiro, depois por prompt alterado mais recente.
- Agente sem setor: o aviso no topo "2 agentes sem setor: não estão em ecossistema/setores.json. [Ver]". Aparece, não some.
- Vazio: "Nenhum agente encontrado em .claude/agents." Carregando: esqueleto de 8 linhas. Erro: seção 8.
- Filtro "Ativos agora" vazio: "Ninguém está trabalhando neste momento."

## 6. Aba Setores
Objetivo: ver a empresa por setor.

Layout: um cartão por setor, em grade 2 colunas. Cada cartão: nome, etiqueta "Ativo" ou "Inativo" com motivo, contagem "9 agentes · 2 ativos agora", lista de nomes dos agentes (primeiros 8, "+4 ver todos"), data da última atividade do setor ("Última atividade: hoje 14:02") e dois links: "Ver agentes do setor" (aba Agentes com filtro) e "Ver documentos do setor" (aba Documentos com a área).
- Setor inativo: cartão cinza com o motivo escrito: "Inativo: sprint pausada por ordem do Guilherme" ou "Inativo: ainda não existe (setor de ação)". Nunca só cinza sem explicação.
- Setores mostrados: produção do canal, inteligência, programação, ação (se existir no arquivo), e o que mais estiver em `ecossistema/setores.json`. Setor novo no arquivo aparece sozinho, sem tocar em código.
- Produtividade: não aparece (fora do painel, por decisão). Nenhum nome de arquivo ou dado dele em lugar nenhum.
- Vazio (arquivo de setores sem setor): "Nenhum setor cadastrado. Peça ao Luiz Henrique para criar ecossistema/setores.json."
- Carregando: 4 cartões em esqueleto. Erro: seção 8.
- Cartão do setor Programação mostra também a sprint (mesmo texto do cartão 3 do Dashboard), para o clique do Dashboard cair aqui com sentido.

## 7. Componentes e linguagem comuns
- Etiquetas sempre com palavra: Novo, Alterado, Ativo agora, Inativo, Sem setor, Desatualizado, Falhou.
- Datas: "há N min" (até 59), "hoje hh:mm", "ontem hh:mm", "dd/mm hh:mm"; tooltip com a data completa. Fuso do computador.
- Todo botão dá retorno visível em até 200 ms (mudança de texto, "Copiado", "Atualizando...", "Tudo visto às hh:mm").
- Todo botão desabilitado diz o motivo no `title` e em texto de apoio ("Marcar tudo como visto" desabilitado: "Nada novo para marcar").
- Contraste e foco: foco visível em item de lista, aba e botão; cor nunca é o único sinal.
- Leitura de tela: regiões `aria-live=polite` para atualização, `role=tablist` nas abas.

## 8. Estados transversais: carregando, vazio, erro
- **Carregando** (primeira leitura): esqueleto + frase da aba ("Lendo o ecossistema...", "Lendo documentos..."). Se passar de 5 s: acrescenta "Está demorando. Seguimos tentando." Passando de 15 s vira erro.
- **Atualização falhou** (já havia dados): faixa vermelha fixa no topo da página: "Atualização parada. Última leitura às 14:02. [Tentar agora]". Dados antigos ficam visíveis, com etiqueta "Desatualizado" ao lado de "Lido às 14:02". Quando volta: a faixa vira verde por 3 s "Voltou a atualizar" e some. A consulta tenta de novo a cada 15 s sozinha.
- **Erro sem nenhum dado** (primeira leitura falhou): no lugar do conteúdo, "Não consegui ler o ecossistema. O servidor do Ecossistema pode ter sido fechado ou travou. Próximo passo: [Tentar de novo]; se continuar, reabra com `python -m corte`." Sem jargão de pilha de erro; o detalhe técnico fica num "Ver detalhe" recolhido.
- **Vazio**: sempre diz o que é, por que está vazio e, quando existir, a ação (ver textos por aba).
- **Servidor fechado** (a conexão cai com a página aberta): mesma faixa de "Atualização parada".

## 9. Bloqueio fora do computador
Se o endereço não for `127.0.0.1`/`localhost` (acesso por `--rede` ou celular), `/painel` e `/api/painel/*` não devolvem dados. A página mostra: "O painel do ecossistema abre só no computador onde o Corte está rodando. Motivo: ele mostra textos internos dos agentes e do projeto, e não deve trafegar pelo Wi-Fi. Abra http://127.0.0.1:8765/painel neste computador." O item "Painel" nem aparece no menu quando o acesso é pela rede. Teste exigido (**Alisson**): pedido pela rede devolve 403, sem corpo com dados.

## 10. Regras de confidencialidade visíveis na tela (para o teste)
- Nenhum caminho de `produtividade/`, `financas/`, `voz/`, `.env`, acessos, LinkedIn aparece em lista, busca, resumo, dashboard ou mensagem de erro (inclusive "Atualizados: ..." do Resumo).
- Busca por texto só varre arquivos do índice permitido; buscar "agenda" ou "senha" não pode revelar arquivo proibido.
- Mensagem de documento proibido é igual à de documento inexistente.

## 11. Mapa de telas para o Endrick (arquivos sugeridos, sem obrigatoriedade)
`estudio/web/painel.html` + `corte_painel.js` (abas e Dashboard/Resumo/Agentes/Setores) e `corte_md.js` (markdown). Rótulo da marca e `<title>` trocados em `corte_nav.js` e nas páginas existentes. Testes de tela: `e2e_painel.mjs` novo: abrir cada aba; criar/alterar um arquivo no disco e vê-lo subir ao topo em até 5 s sem recarregar; "Marcar tudo como visto" e "Desfazer"; estado vazio e erro (servidor fora); texto do Resumo com no máximo 2 linhas.

## 12. Dúvidas para o Zico / Guilherme
1. O "visto" fica só no navegador (sem gravar no projeto). Serve? A alternativa (gravar em `estudio/dados/`) permitiria o mesmo "visto" em dois navegadores, mas só no computador isso quase não importa.
2. A marca "Ecossistema do Guilherme" é longa para o menu: mantenho o nome inteiro no topo (só computador, cabe) ou abrevio para "Ecossistema" onde faltar espaço?
3. Quais agentes/setores contam como "ativo" no Dashboard quando a sprint está pausada: só os que o `ao_vivo` reporta, sem presumir nada? (Assumido assim.)
4. Quer aviso (faixa) também quando uma decisão nova dele aparece enquanto a tela está aberta? Assumi que não; o cartão 4 só muda de número.
