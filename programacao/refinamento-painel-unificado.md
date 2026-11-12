# Refinamento técnico: espelho unificado ao Corte (painel central)

Data: 2026-11-09. Autor: **Thiago Silva**. Estado: refinamento, nada implementado. Falta cartão no quadro: o **Zico** precisa abrir o item (sugestão de id na seção f) antes de qualquer fatia ser feita.

Escopo pedido pelo Guilherme: o "espelho" vira um sistema central dentro do Corte (`python -m corte`), com dashboard, agentes, setores, aba Documentos (recém-atualizados no topo, com data da última atualização, atualizando sozinha) e aba de resumo com no máximo 2 linhas do que foi executado por último. A interface do Ronaldo (`produtividade/painel.py`) fica à parte.

## (a) Como o espelho funciona hoje

**Arquivos:** `tools/gerar_espelho.py` (339 linhas), `tools/hook_espelho.py` (81 linhas), saída `espelho_sistema.html` (2,2 MB, raiz). Nenhum dos três está versionado no git (`git ls-files` não devolve nada para eles).

**Geração:** um script Python lê tudo do disco e injeta um JSON gigante dentro de um HTML único (`TEMPLATE`, com CSS, um renderizador de markdown próprio e 5 abas: Início, Agentes, Vídeos, Documentos, Código). Sem servidor, sem banco: é um retrato estático, só consulta.

**O que lista:**
- Agentes: todos os `.claude/agents/*.md`, com frontmatter (description, tools, model), prompt completo e data (mtime). O setor de cada agente vem de um dicionário `SETORES` escrito à mão dentro do script (5 setores, ~48 ids).
- Vídeos: cada pasta de `output/<slug>/`, com estado deduzido pelos arquivos (Vídeo pronto, Cenas prontas, Só roteiro, Em pesquisa), selo de auditoria lendo `auditoria.md`, metadados e 10 textos (roteiro, angulo, notas, auditorias...).
- Documentos: `.md` e `.txt` de CLAUDE.md, README, AUDITORIA_E_ARQUITETURA, assinatura do canal, `prompts/`, `componentes/`, `programacao/`, `inteligencia/`, `produtividade/` (mais `agenda.json` e `lembretes.json`), `financas/` (só README), `ecossistema/`, `estudio/` (raiz), `reels/`, `tiktok/`, `research_notes/`, `reports/`, `referencias/`, `.claude/skills/`. Até 60 mil caracteres por documento e 150 por pasta, em ordem alfabética de caminho (não por data).
- Código: contagem de arquivos e primeira linha da docstring de cada `.py` das pastas principais.
- Bloqueios por nome: `acessos.md`, `.env`, `client_secret*.json`, `movimentos.csv`, `saldos.csv`. Pastas ignoradas: `.venv`, `node_modules`, `.git`, `blobs`, `falas`, `corte_assets`, `jobs` etc.

**Como detecta mudança:** não detecta. Ele **refaz tudo do zero** a cada execução; o campo "data" é só o `mtime` de cada arquivo no momento da geração. Quem dispara a regeneração é o hook (`.claude/settings.local.json`): `PostToolUse` em `Write|Edit`, mais `Stop` e `SubagentStop`. O `hook_espelho.py` só roda o gerador se o evento for Stop/SubagentStop, ou se o `file_path` da ferramenta for `.md`/`.txt` dentro do repo. Para várias escritas em paralelo usa trava em `%TEMP%` (`contexto_explica_espelho.lock`) e um marcador `.pendente` (quem chega com outra execução em andamento só marca; a atual roda mais uma vez no fim). Erros são engolidos.

**Limites que pesam na unificação:**
1. Só enxerga edição feita por Write/Edit do Claude Code. Edição por Bash, pelo editor do Guilherme, pelo Corte (a tela Agentes grava `.md` direto), pelo Codex ou pelo `maestro.py` só aparece no próximo Stop/SubagentStop, ou nunca.
2. Cada atualização reescreve 2,2 MB e relê centenas de arquivos, mesmo se mudou uma linha.
3. A lista de setores/agentes é uma cópia à mão (diverge de `estudio/central.py`, que tem outra lista: 4 setores, 3 inativos, e só 9 agentes). Agente novo cai em "Outros".
4. Inclui `produtividade/` (agenda, lembretes, horas, kanban, linkedin) e o README de finanças: conteúdo pessoal num arquivo que se abre e se copia com facilidade.
5. Não dá "quem mexeu", nem "o que foi executado por último".

## (b) Abordagem recomendada

**Painel vivo dentro do Corte, lendo sob demanda. O HTML estático e o hook de regeneração saem de cena depois da paridade.**

Peças (nomes sugeridos; o **Rodrygo** pode ajustar sem me consultar se não mudar o contrato):
- `estudio/painel.py` (back): índice de documentos (seção c), resumo (seção d), visão do dashboard. Só lê; não escreve nada do projeto.
- Rotas novas em `estudio/servidor.py`, seguindo o padrão de `central`: `GET /painel` (página), `GET /api/painel/visao` (contadores, setores, agentes, sprint, vídeos recentes), `GET /api/painel/documentos` (lista só com metadados: caminho, título, área, data, tamanho), `GET /api/painel/documento?caminho=` (conteúdo), `GET /api/painel/mudancas?desde=<marca>` (barato, para o polling) e `GET /api/painel/resumo`.
- Front: `estudio/web/painel.html` + `corte_painel.js`, item "Painel" no menu de `corte_nav.js`. Abas: **Dashboard, Agentes, Setores, Documentos, Resumo**. A aba Agentes do painel é visão de leitura (quem é, setor, estado ao vivo, data do `.md`) e **linka para a tela `/agentes` já existente** (editor/catálogo/Ao vivo, PROG-003) em vez de duplicá-la. Reaproveitar `central.sprint_ativa/quadro/agentes` e `ao_vivo` para sprint, quadro e estado.
- **Fonte única de setores/agentes:** um arquivo versionado `ecossistema/setores.json` (id, nome, ativo, lista de agentes) que o painel e o `central.py` leem. Acaba a cópia à mão; agente fora da lista aparece como "Sem setor" visível (alerta), não some. Alternativa: chave `setor:` no frontmatter de cada agente, mas isso mexe em ~48 arquivos de agentes (inclusive de outros setores) e exige pedido do Guilherme; não recomendo.
- **Conteúdo sob demanda:** a lista leva só metadados; o texto de um documento só vem quando se clica nele (o espelho carregava 2,2 MB de uma vez, inviável no celular). O renderizador de markdown do espelho (função `md`) deve ser extraído para um `corte_md.js` reutilizável.
- **Atualização sozinha:** a aba Documentos consulta `mudancas?desde=` a cada ~5 s (mesmo padrão do `Vivo` em `corte_nav.js`: para com a aba oculta). Só quando a marca muda ela busca a lista de novo. Sem WebSocket, sem hook obrigatório.
- **Transição:** manter `gerar_espelho.py` e o hook rodando até o **Alisson** liberar a paridade e o Guilherme confirmar; depois, remover o hook de `.claude/settings.local.json` (mudança de configuração: só com pedido do Guilherme) e arquivar os dois scripts. Não apagar antes.

Detalhes de código que o **Rodrygo** precisa lembrar: a nova rota entra em **dois** lugares de `servidor.py` (o `startswith` do `_rota_get` e a lista de caminhos HTML do `_porteiro`, senão o celular recebe 401 sem a página de senha). O endpoint de documento só serve caminho **que está no índice** (nunca abrir pelo texto recebido: `..`, caminho absoluto, link simbólico e `.env` têm de falhar).

## (c) Detectar documentos alterados e confidencialidade

**Comparação das três técnicas:**

| Técnica | Pega | Não pega / custo |
|---|---|---|
| **mtime** (varredura com `os.scandir`) | qualquer escrita, por qualquer ferramenta, no instante | git pull/checkout também mexe no mtime; "touch" sem mudar o conteúdo |
| **git** (`git status`, `git log -1 -- path`) | histórico e autoria de commit | não vê arquivo ignorado, demora com muitos caminhos, data de commit não é data de edição (o canal quase não commita) |
| **hook** (PostToolUse) | quem mexeu (agente) e qual ferramenta | só no Claude Code; falha em silêncio; não cobre Corte, Codex, Bash, edição manual |

**Recomendação: mtime como fonte da verdade + hash de conteúdo + hook leve só para "quem".**
1. Varredura por lista de permissão (abaixo), guardando em memória `{caminho: (mtime_ns, tamanho)}`. Para ~600 arquivos pequenos custa milissegundos; só relê o conteúdo se mtime/tamanho mudou.
2. Quando mudou, calcula o SHA-1 e compara com o último visto: se igual, **não** vira "atualizado" (evita falso positivo de git checkout e de `touch`). A data exibida é a do mtime real da última mudança de conteúdo.
3. A "marca" do polling é `max(mtime) + contagem + hash curto`; `mudancas?desde=` responde `igual` ou os caminhos novos.
4. Persistência do índice: arquivo em `estudio/dados/` (já gitignored). Depois de reiniciar o Corte, a primeira varredura reconstrói por mtime (sem perder a ordem).
5. **Hook opcional leve** (`tools/hook_atividade.py`, substitui o `hook_espelho.py`): em vez de regenerar HTML, só **acrescenta uma linha** em `estudio/dados/atividade.jsonl` (hora, caminho, ferramenta, agente se o payload trouxer). Custo ~0, sem trava. O painel casa a linha com o documento para mostrar "alterado por X". Sem a linha, mostra só a data (nunca inventa autor). Instalar esse hook mexe em `.claude/settings.local.json`: depende do OK do Guilherme.

**Ordem e exibição:** `mtime` decrescente por padrão, rótulo "há 3 min / hoje 14:02 / 07/11", filtro por área, busca por título e texto (a busca no texto pode ser feita no servidor, sob demanda, só nos arquivos do índice).

**Pastas que entram (lista de permissão, `.md` e `.txt`, e `.json` só os de decisão listados):**
- Raiz: `CLAUDE.md`, `README.md`, `AUDITORIA_E_ARQUITETURA.md`; `output/messi_assinatura_canal.md`.
- `ecossistema/`, `programacao/` (inclui `maestro/decisoes/*.json` para o resumo, `revisoes/`, `qa/`, `tecnico/`, `ux/`, `sprints/`), `inteligencia/` (exceto `aprendiz/_entrada` e `_trabalho`), `componentes/`, `prompts/`, `estudio/` (README e docs da raiz), `.claude/agents/`, `.claude/skills/`.
- `output/<slug>/`: só os textos de produção (roteiro.txt, angulo.md, notas.md, direcao_viral.md, revisao.md, auditoria*.md, CONFORMIDADE.md, PUBLICAR.txt, metadados.json). Nunca mp4, wav, imagens, `falas/`, `corte_assets/`.
- `research_notes/`, `reports/`, `referencias/` (só os `.md` curados), `reels/`, `tiktok/` (`.md`/`.txt`).

**Pastas que ficam de fora (padrão de bloqueio, não de aviso):**
- **Segredos:** `.env*`, `client_secret*.json`, `.youtube_token.json`, `.youtube_analytics_token.json`, `estudio/dados/` (banco, senha da rede, logs), qualquer `*token*`, `*senha*`, `*.pem`, `*.key`.
- **Pessoal (confidencial por natureza):** `produtividade/` inteira (acessos.md, agenda.json, lembretes.json, horas, kanban, linkedin, dicas, estado dos avisos) e `financas/` inteira (README incluído, que o espelho de hoje mostra). A interface do Ronaldo já cobre esse conteúdo à parte, como pedido.
- **Dados pessoais/biometria:** `voz/`, `output/*/falas/`.
- **Terceiros e volume:** `referencias/capas|transcricoes|videos`, `inteligencia/aprendiz/_entrada|_trabalho`, `.venv`, `.git`, `node_modules`, `__pycache__`.
- **Memória do assistente** (`~/.claude/projects/.../memory`) fica fora do repo e do painel.
- **Rede de segurança:** varredura do conteúdo antes de servir; se o texto casar com padrões de segredo (`sk-ant-`, `AIza`, `Bearer `, `chat_id`, `token=`, `senha:`), o painel esconde o corpo e mostra "conteúdo omitido: parece conter credencial". Alerta, não substitui a lista de permissão.
- Mudança de regra (entrar/sair pasta) exige decisão do Guilherme; o **Rodrygo** guarda a lista num lugar só (constante no `painel.py`, coberta por teste).

**Acesso pelo celular (`--rede`):** hoje o Corte vai por HTTP com senha. Documentos de agentes e do ecossistema pelo celular são úteis, mas é a primeira vez que texto bruto de prompts/estratégia trafega no Wi-Fi. Proposta: aba Documentos funciona no computador sempre; no celular, só se o Guilherme confirmar (pergunta 3).

## (d) Resumo de 2 linhas sem gastar token

**Regra, sem LLM, só leitura de logs que já existem.** Fontes, em ordem de qualidade:
1. `programacao/maestro/decisoes/PROG-NNN.json` (campo `status`): já é frase escrita para o Guilherme ler no celular, com o porquê. É a melhor fonte para "o que o setor de programação fez por último".
2. `programacao/maestro/log.md`: linhas `chamando <Agente> para [itens] em <coluna>` e `<Agente> terminou (US$..., erro=...)`. Dá quem, o que, em que coluna e se falhou, com carimbo de hora.
3. Tabela `jobs`/`eventos` do banco do Corte (`craque`, `titulo`, `status`, `terminado_em`, `resumo`): trabalho dos agentes de produção (vídeos).
4. `estudio/dados/atividade.jsonl` (hook leve) ou, sem ele, os documentos de maior mtime do índice.
5. Fallback final: `git log -1 --format=%s`.

**Montagem (limite duro de 2 linhas, ~120 caracteres cada, truncando na primeira frase e com reticências):**
- Linha 1, a última execução de agente: `{hora} · {Agente} {verbo} {alvo}: {status curto}`. O verbo vem de um mapa fixo por coluna ou etapa (Em refinamento técnico = refinou, Fazendo = implementou, Em teste = testou, Code Review = revisou, Pronto para aceite = conferiu; jobs de produção usam o `titulo` do job). Falha vira `falhou` em destaque.
- Linha 2, o que mudou nos documentos: `Atualizados: a.md, b.md (+3)` com os 2 mais recentes do índice.
- Se for o caso de coluna que espera o Guilherme (decisão com `precisa_do_guilherme`), a linha 1 cede lugar a `Espera você: PROG-NNN ...` (informação mais útil que a última ação).
- A interface aplica `line-clamp: 2`; o back já devolve o texto cortado, então a regra vale também para o celular e para teste.
- Custo: zero token. Cache de 5 a 10 s no servidor. Sem nenhum dado, mostra "Nada executado ainda" (nunca texto inventado).

Resumo por IA fica fora de escopo (decisão de custo); se o Guilherme quiser frases mais ricas depois, é item separado.

## (e) Riscos e impacto

| Risco | Gravidade | Mitigação |
|---|---|---|
| Vazamento de conteúdo pessoal/segredo pela lista de documentos, sobretudo com `--rede` (HTTP) | alta | lista de permissão (não bloqueio); `produtividade/` e `financas/` fora; varredura de padrões de segredo; endpoint só serve caminho do índice; teste de confidencialidade obrigatório |
| Path traversal / leitura de arquivo fora do índice | alta | resolver caminho real, exigir que esteja no índice, recusar link simbólico para fora do repo |
| Duas listas de setores divergindo (espelho, `central.py`) | média | `ecossistema/setores.json` como fonte única; alerta para agente sem setor |
| Varredura pesada em `output/` (muitas pastas e arquivos grandes) | média | só nomes de produção permitidos, sem recursão em mídia, cache por mtime, limite de tamanho (60 mil caracteres) |
| Ler arquivo no meio da escrita de outro processo (texto cortado) | baixa | tolerar erro, tentar de novo na próxima rodada; hash só de leitura completa |
| mtime muda com git pull/checkout | baixa | hash de conteúdo decide "atualizado" |
| Hook não dispara (Bash, Codex, edição manual) | baixa | hook é só enriquecimento ("quem"); a verdade é o mtime |
| Quebrar testes do Corte (menu novo muda contagem de itens nos e2e) | média | **Alisson** roda `e2e_interface`, `e2e_celular`, `e2e_corte`, `testar_ao_vivo` e ajusta o que depender do menu |
| Servidor do Corte atender polling junto com o resto | baixa | rotas só leem e usam cache; polling para com aba oculta |
| Escopo: mexe em `servidor.py` e `corte_nav.js` (arquivos centrais do Corte) | média | mudança pequena e isolada; novo módulo e nova página; **Thiago Silva** revisa o diff dos arquivos centrais |

Impacto no canal: nenhum (nada em `output/` é alterado, o pipeline `run.py` não é tocado). Impacto no usuário: o `espelho_sistema.html` continua até a paridade; depois o Guilherme abre o Corte em `/painel`.

Fora do escopo desta unificação: Ronaldo (`produtividade/painel.py`), finanças, edição de documentos pelo painel (a aba é de leitura; editar continua no editor ou na tela Agentes), qualquer escrita em `output/`.

## (f) Fatiamento sugerido

Sugestão de cartão: "Painel central unificado no Corte" (id a definir pelo **Zico**), com as fatias abaixo, nesta ordem. Cada fatia passa por **Thiago Silva** (code review) e **Alisson** (QA) antes do aceite.

| # | Fatia | Dono | Entrega | Testes exigidos |
|---|---|---|---|---|
| 0 | Desenho de UX: abas Dashboard, Agentes, Setores, Documentos, Resumo; recentes no topo, "atualizado há...", versão celular, estado vazio/erro, onde linka para `/agentes` | **Iniesta** | wireframe em `programacao/ux/` | revisão do **Zico** |
| 1 | Índice de documentos: lista de permissão, mtime + hash, cache, marca de mudança, rotas `documentos`, `documento`, `mudancas` | **Rodrygo** | `estudio/painel.py` + rotas | novo `estudio/testes/testar_painel.py`: nenhum arquivo proibido aparece, caminho fora do índice é recusado (`..`, absoluto, `.env`), ordem por data, "touch" sem mudança não atualiza, arquivo novo/alterado/apagado, padrão de segredo omite o corpo |
| 2 | Fonte única de setores/agentes + visão do dashboard + resumo de 2 linhas por regra | **Rodrygo** | `ecossistema/setores.json`, rotas `visao` e `resumo`, ajuste de `central.py` | `testar_painel.py` ampliado (resumo ≤ 2 linhas e ≤ 120 caracteres com log vazio, log cheio e falha; agente sem setor sinalizado); `testar_ao_vivo.py` continua verde |
| 3 | Hook leve de atividade ("quem mexeu") | **Rodrygo** (script); troca em `.claude/settings.local.json` só com OK do Guilherme | `tools/hook_atividade.py` | teste do hook com payloads simulados (arquivo fora do projeto, agente ausente, erro nunca falha o fluxo) |
| 4 | Telas: página `/painel`, menu, Documentos com polling, Resumo, Dashboard, extração do renderizador de markdown | **Endrick** (depende de 0 e 1; Dashboard/Resumo dependem de 2) | `painel.html`, `corte_painel.js`, `corte_md.js`, item no menu | `e2e_painel.mjs` novo (clique real: abrir documento, editar um arquivo no disco e ver subir ao topo sem recarregar); `e2e_interface`, `e2e_corte` verdes |
| 5 | QA completo, incluindo celular e confidencialidade ponta a ponta | **Alisson** | `programacao/qa/<id>.md` | `e2e_celular` (sem scroll lateral, 401 sem senha, página de senha na rota nova), as baterias de `estudio/testes/` do README, mais o e2e novo, 2 execuções seguidas |
| 6 | Desligar o espelho antigo (remover hook, arquivar scripts) | **Rodrygo**, depois da paridade e do OK do Guilherme | commit separado, sem apagar histórico | verificar que nada mais chama `gerar_espelho`/`hook_espelho` |

As fatias 1, 2 e 3 são independentes do desenho e podem começar em paralelo com a 0 (WIP: o **Rodrygo** com no máximo 2 em Fazendo; sugiro 1 e 2 primeiro, a 3 depois).

Nota técnica de cada fatia será gravada em `programacao/tecnico/<id>.md` quando o **Zico** abrir os cartões; este documento é a base.

## Perguntas para o Guilherme

1. **Pessoal fora do painel:** confirma que `produtividade/` (agenda, lembretes, acessos, horas, linkedin) e `financas/` (inclusive o README que o espelho hoje mostra) **ficam de fora** do painel do Corte, ficando só no Ronaldo?
2. **Que mais deve sair?** Quer esconder também algum outro conteúdo (por exemplo `inteligencia/`, `referencias/` ou `output/<slug>/notas.md`) ou o painel pode listar tudo o que está na lista da seção (c)?
3. **Celular:** a aba Documentos (texto bruto de agentes e estratégia, por HTTP no Wi-Fi com senha) deve abrir também pelo celular com `--rede`, ou só no computador?
4. **"Atualizado por quem":** aceita instalar o hook leve (muda `.claude/settings.local.json`) para mostrar o agente que alterou o documento? Sem ele, o painel mostra só a data e a hora.
5. **Resumo:** o que deve contar como "executado por último"? Proposta: última ação de agente do setor de programação e dos jobs de produção, mais os documentos recém-alterados. Quer também commits e postagens (Memphis)?
6. **Espelho antigo:** posso planejar desligar o `espelho_sistema.html` e o hook quando o painel estiver igual (fatia 6), ou prefere manter os dois por um tempo?
7. **Prioridade na sprint ativa:** entra agora (Zico abre o cartão e escolhe a sprint) ou espera a sprint atual fechar? A sprint está pausada por sua ordem; só retomo o refinamento em cartão depois de o **Zico** abri-lo.
8. **Nome e lugar:** "Painel" no menu do Corte serve, ou prefere manter o nome "Espelho"?
