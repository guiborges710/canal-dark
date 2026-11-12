# PAINEL-REVISAO-2026-11-09 (fora do quadro, autorizado pelo Guilherme)

Revisão completa do painel (`/painel`), por **Endrick**. Capturas reais (Chrome, API real) de Dashboard, Resumo, Documentos (.md e .json), Agentes, Setores e Vídeos, em escuro e claro, a 1440, 1024 e 390 px. Sem erro de console, sem rolagem horizontal e sem rolagem dupla em nenhuma.

## Corrigido
- Dashboard: o cartão "Decisões pendentes" ficava mais baixo que os outros (a classe global `.destaque` do Corte vazava margem e sombra). Corrigido também em itens da lista de Documentos.
- Menu lateral: a marca quebrava em 3 linhas ("Ecossistema / do / Guilherme"); agora 2 ("Ecossistema / do Guilherme").
- Agentes: removida a linha "Prompt alterado ..." (data de arquivo sem sentido, tudo igual após sincronias).
- Setores: setor privado agora aparece só como "Pessoal" + contagem, sem o nome real ("Produtividade pessoal"), sem nomes, sem botões; "1 agente" no singular.
- Documentos: título não se repete mais no corpo; título de leitura menor (3 linhas viravam 2); item da lista alinhado no celular.
- Documentos .json: rótulos com inicial maiúscula e acento (Cartões, Última), datas ISO formatadas, vazio vira "—".
- Resumo: linha divisória com a largura da página e respiro antes de "Base lida".
- Celular: "Abrir o Corte" volta a aparecer no menu.
- Confidencialidade (`estudio/painel.py`, mudança pequena, avisar **Thiago Silva**/**Rodrygo**): prompts de agentes de setor `privado` (ex.: casemiro-financeiro, pedri-gestor-tarefas, rodri-apontamento-horas, ronaldo) apareciam na lista de Documentos. Agora saem do índice e do endpoint de documento. O servidor em execução precisa ser reiniciado para pegar isso.

## Não alterado (dado verdadeiro)
- "Documentos alterados hoje: 266": são arquivos de fato modificados hoje (151 em `output/`, 52 em inteligência, 28 em agentes). Sugestão ao **Rodrygo**: contar só áreas de trabalho, sem `videos`.
- Cartão de vídeos mostra o slug cru; só há `slug` na API.

## Testes
- `node estudio/testes/e2e_painel.mjs`: 60 verificações ok, 0 falhas (novos: agente privado fora de Documentos, título não repetido, JSON legível, setor privado sem nome real).
- `.venv\Scripts\python estudio/testes/testar_painel.py`: 167 ok, 0 falhas.

Arquivos: `estudio/web/corte_painel.js`, `estudio/web/corte.css`, `estudio/painel.py`, `estudio/testes/e2e_painel.mjs`.

## Revisão visual completa (09/11/2026)

Gerei e inspecionei individualmente a matriz completa em Chromium com API do painel servida por uma caixa temporária. As cinco imagens de referência citadas pelo Guilherme não estão disponíveis no histórico visual desta rodada nem no workspace; não foram inventadas nem substituídas. Nenhum arquivo ou pasta de `produtividade/` ou `financas/` foi aberto, alterado ou removido.

### Matriz de capturas
42 PNGs em `C:\Users\Guilherme\AppData\Local\Temp\painel-matriz-20261109\capturas\`, nomeados como `<aba>-<tema>-<largura>.png`, com 7 estados × 2 temas × 3 larguras:
- Abas/estados: Dashboard, Resumo, Documentos com `.md` aberto, Documentos com `.json` aberto, Agentes, Setores e Vídeos.
- Temas: escuro e claro.
- Larguras: 1440, 1024 e 390 px.
- `matriz.json` contém as métricas por captura e erros de console: **zero erros** e `scrollWidth === innerWidth` nas 42 imagens.

### Achados corrigidos
- Dashboard a 1024 px quebrava “Sprint 01” entre letras (`Sprin` / `t 01`). Ajustei o tamanho e o não quebramento do número no intervalo de 1001–1100 px em `estudio/web/corte.css`.
- Agentes com uma pessoa mostrava “1 agentes”. A contagem agora flexiona singular/plural tanto para agentes quanto para ativos, em `estudio/web/corte_painel.js`.
- O aviso geral de Setores para um agente sem setor também foi corrigido para “1 agente sem setor” (correção registrada acima).

A releitura visual das capturas atualizadas confirmou as duas correções; tema claro/escuro manteve contraste legível, e não observei texto cortado ou rolagem horizontal nas combinações. A matriz não continha conteúdo das áreas pessoais proibidas. As cinco referências seguem indisponíveis para comparação direta.

### Teste final
- Executei uma vez `node estudio/testes/e2e_painel.mjs C:\Users\Guilherme\AppData\Local\Temp\painel-revisao-final`: **63 verificações ok, 0 falhas**. Inclui a verificação do cartão Sprint a 1024 px, concordância no aviso geral de Setores, mensagem vazia/erro, ausência de rolagem lateral no teste estreito e erros JavaScript.
- Arquivos alterados nesta continuação: `estudio/web/corte.css`, `estudio/web/corte_painel.js`, `estudio/testes/e2e_painel.mjs` e este relatório.
