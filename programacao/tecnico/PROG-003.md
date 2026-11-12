# PROG-003 + PROG-006 · Aba Agentes, desenho B (Ao vivo, depois Catálogo), com motor embutido · Nota técnica

Autor: **Thiago Silva** · 2026-11-03 · Quem faz: **Rodrygo** (contrato e rota, primeiro) e **Endrick** (tela, só depois do contrato publicado). Desenho: **Iniesta** (`ux/prog-003-aba-agentes.md`, alternativa B; a ata da planning fixou B com as regras da decisão 4).

## Contrato da API (fechado aqui; **Endrick** consome sem esperar o resto)
`GET /api/agentes/ao-vivo`, só leitura. Atenção: `servidor.py:234` tem `fullmatch(r"/api/agentes/([\w-]+)")` e `ao-vivo` casa com ele (hífen entra em `[\w-]`). A rota nova tem de ser testada antes dessa. Teste cobre isso.

```
{
  "gerado_em": "2026-11-03T21:40:12",   // informativo
  "servidor_s": 1793000000.4,            // epoch do servidor
  "resumo": {"trabalhando": 2, "fila": 1, "falhou": 1, "espera_voce": 1},
  "agentes": [                           // só quem tem estado diferente de livre
    {"id": "olise-diretor-arte", "craque": "Olise", "ativo": true,
     "estado": "trabalhando|fila|falhou|espera_voce",
     "estado_texto": "Trabalhando",
     "trabalhos": [                      // um por job ou etapa; o estado do agente é o do mais relevante
       {"job_id": 41, "slug": "krakatoa-geracoes", "titulo_video": "...", "etapa_id": "cenas", "etapa_nome": "Cenas",
        "estado": "trabalhando", "motor": "claude|codex|null", "motor_nota": "texto em PT ou null",
        "segundos_na_tarefa": 128, "aguarda_s": null, "posicao_fila": null, "erro_curto": null,
        "origem": "grafo|estudio|teste_agente", "alerta_longo": false}
     ]}
  ],
  "concluidos_1h": [ {"agente": "neymar-roteirista", "craque": "Neymar", "slug": "...", "etapa_nome": "Roteiro", "motor": "claude", "terminou_ha_s": 900} ],
  "frescor": "ok"
}
```
Regras:
- Prioridade do estado do agente: `espera_voce` e `falhou` sobem (seção Atenção), depois `trabalhando`, depois `fila`. Um agente com vários trabalhos tem uma entrada com a lista (decisão do Iniesta: uma linha com lista).
- **Tempo**: o servidor manda `segundos_na_tarefa` calculado por ele. O navegador soma o que passou desde que recebeu (`Date.now()`), nunca interpreta `iniciado_em`. Motivo: `agora()` do banco é hora local sem fuso; o celular em `--rede` pode estar em outro fuso e mostraria "há 3 h" errado.
- `alerta_longo` = `segundos_na_tarefa >= 900` (15 min, decisão 4 da ata), por etapa.
- `motor` vem de `trabalhos.motor_do_job` (já usado em `status_job_publico`); comando (Render, Voz do canal) não é agente: não entra. `motor_nota` aparece quando houver; nunca devolver `null` como texto.
- Falhou: job `falhou`, `dispensado=0`, sem job posterior `ok` da mesma etapa (mesma regra de `Contexto.falha`, `fluxo.py:257`). `erro_curto` = primeira linha do erro, máx. 160 caracteres.
- **Espera você**: etapa com status `aguardando` no estado da produção; agente = o do último job da etapa (`spec["agente"]`), com reserva no agente fixo da etapa (`fluxo.POR_ID`, e `BARCOLA` nas cenas horizontais).
- Mapa job para agente: `json.loads(job["spec"])["agente"]` (id técnico, existe em `fluxo.py` `grafos.py:658` e `agentes.py:319`). `jobs.craque` é nome de exibição, não serve de chave. Job sem `spec.agente` fica de fora; a quantidade vai em `resumo.ignorados` só para depuração.
- Falha na leitura devolve 500 JSON com `erro`; o front mantém o último estado (critério 9).

## Custo e polling (risco central)
Há dois pollings hoje (Projetos a cada 2 s, relógio do Estúdio a cada 4 s). O novo deve ser mais barato, não somar.
- Jobs ativos, falhos e concluídos na última hora: **uma query** em `jobs` (`status IN ('fila','rodando') OR (terminado_em > agora-1h)`), com índice em `status` se `EXPLAIN` mostrar varredura. Sem ler `log.txt` nem `trabalhos.progresso()` (ele lê disco por job). Contador de cena fica de fora desta versão; o Estúdio já o mostra no diálogo.
- Espera você exige olhar produções: **não** chamar `fluxo.estado(slug)` por produção a cada pedido (grava no banco via `sincronizar` e lê muitos arquivos). Usar `estado(slug, sincroniza=False)` só das produções não arquivadas, com **cache em memória de 3 s e trava única** (vários clientes não multiplicam o custo). Se o 50-jobs do critério 8 estourar 200 ms nesta parte, a queda é: calcular Espera você a partir de `aprovacoes`/`itens` em SQL. Rodrygo mede e registra.
- Front: polling de 4 s apenas na aba Ao vivo e para o selo do menu; **para quando `document.hidden`** e atualiza ao voltar (já existe `visibilitychange` em `app.js:116`). Sem redesenho se a assinatura não mudou (padrão `seMudou`); não redesenhar com `Corte.editando`.

## PROG-006 embutido (motor na tela)
O backend já entrega `motor` e `motor_nota` em `status_job_publico` (`fluxo.py:757`). Falta o front: selo `Claude`/`Codex` em texto no cartão do Ao vivo e na etapa/versão do Estúdio, dica com `motor_nota` (só quando existe), job antigo sem `motor` não mostra nada nem "undefined". Uma função única `seloMotor(job)` em `corte_nav.js` (junto de `seloEstado`) usada nos dois lugares. Depende do resultado do PROG-004 só para o texto da dica, não para o contrato.

## Front (Endrick), em duas entregas
1. **Ao vivo** (semana 1): `corte_agentes.js` ganha abas. Rotas: `/agentes` abre **Ao vivo**; `/agentes/<id>` continua abrindo a ficha (Catálogo) para não quebrar links e e2e existentes; a aba Catálogo é `/agentes?aba=catalogo`. Não usar `/agentes/catalogo` nem `/agentes/ao-vivo` como caminho: colidem com id de agente (`Corte.registrar(/^\/agentes(?:\/([\w-]+))?\/?$/)`). Selo de contagem no item "Agentes" de `corte_nav.js` (texto para leitor de tela, `aria-live="polite"`). Textos e estados do **Iniesta**; "Espera você" em âmbar; blocos "Atenção", "Agora", e "Concluídos na última hora" recolhido. Estados vazio, desatualizado e servidor fora do ar conforme o desenho.
2. **Catálogo** (semana 2, é o que cai se faltar tempo): a tela de hoje intacta dentro da aba. Mudança mínima: mover o conteúdo atual de `montar`/`carregar` para uma função de aba, sem alterar a lógica de edição (critério 12).

## Riscos
1. Colisão de rota (acima). 2. Custo de "Espera você". 3. Fuso do celular (resolvido por segundos). 4. **Colisão de edição** em `app.js`, `corte_nav.js`, `corte_agentes.js`, `servidor.py` com PROG-011 e os PROG-001/002/015 em curso: **Rodrygo** só mexe em `servidor.py` e em módulo novo (`estudio/ao_vivo.py`); **Endrick** só em `corte_agentes.js`, `corte_nav.js`, CSS. PROG-011 espera o fim da entrega 1. 5. Lacunas no mapa job para agente: jobs de teste de agente (`teste_agente`) aparecem com `origem` e rótulo "teste"; jobs de comando ficam fora. 6. Agente desativado enquanto roda: `ativo=false` no item, mantém na lista.
7. Agentes de outros setores aparecem se tiverem job (catálogo é `.claude/agents` inteiro). Pergunta 4 do **Iniesta** segue com o **Zico**; o contrato não filtra.

## Arquivos afetados
Novo: `estudio/ao_vivo.py`, `estudio/testes/testar_ao_vivo.py`, `estudio/testes/e2e_agentes_ao_vivo.mjs`. Editar: `estudio/servidor.py` (rota nova antes da de `/api/agentes/<id>`; ver cuidado de rota de página), `estudio/web/corte_agentes.js`, `corte_nav.js`, `app.js` (só se precisar do selo no Estúdio), `corte.css`, `celular.css`, `estudio/README.md`.

## Testes exigidos
- Unidade/integração (`testar_ao_vivo.py`, banco temporário): ocioso (não aparece), trabalhando, fila, falhou (e sumir após dispensar e após sucesso posterior), espera você, vários jobs por agente, job sem `spec.agente`, motor com nota, motor sem nota, job sem campo `motor` (job antigo), `alerta_longo` em 900 s, concluídos só da última hora, **50 jobs** (tempo da resposta abaixo de 200 ms e servidor vivo), consulta com erro devolve JSON de erro sem derrubar, a rota `ao-vivo` não cai no `<id>`.
- e2e (`e2e_agentes_ao_vivo.mjs` com `claude_simulado`): estados e vazio, contagem no menu, atualização sem recarregar, falha de consulta mantém o último estado com faixa "Sem atualização", clique leva ao Estúdio, contador de tempo avança sozinho, celular (`e2e_celular.mjs`), edição de agente no Catálogo continua funcionando (regressão: `e2e_interface.mjs`).
- Rodar também: `testar_estilos.py`, `e2e_corte.mjs`, `e2e_estilos.mjs` (dependem do PROG-005 verde antes; se ele atrasar, **Alisson** roda só o que está verde e registra).
- Fixtures derivam nós de `grafos.py`, nunca de ids fixos.

## Ordem
Dia 1 **Rodrygo**: `ao_vivo.py`, rota e testes de back (contrato congelado a partir daqui; mudança de campo me avisa). Dia 2 em diante **Endrick**: Ao vivo com a rota real. Depois PROG-011. Catálogo por último. Estimativa total M-G, como na planning.
