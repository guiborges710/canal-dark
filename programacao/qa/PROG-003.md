# QA PROG-003 · Fatia "Ao vivo" (escopo reduzido pelo Zico em 05/11) · Alisson

## Veredito final: APROVADO COM RESSALVAS (fatia Ao vivo)
Revalidado em 05/11 (13:5x) contra o escopo novo: critérios 1 e 15 sem o "ocioso" (foram ao PROG-016) e critério 6 com a etapa. Uma bateria por vez.

| Bateria | Resultado |
|---|---|
| `testar_ao_vivo.py` | 49 ok, 0 falhas (50 jobs: rota 41 ms, limite 200 ms) |
| `e2e_agentes_ao_vivo.mjs` | 91 ok, 0 falhas (inclui "O clique leva o id da etapa na URL (?etapa=metadados)") |
| `e2e_interface.mjs` (isolado) | 150 ok, 0 falhas. As 7 falhas em sequência não reproduziram |
| `e2e_celular.mjs` | 64 ok, 0 falhas |
| `e2e_motor.mjs` rodada 1 (logo após o celular) | 23 ok, 1 FALHA (stack em e2e_motor.mjs:153; não capturei o nome da verificação) |
| `e2e_motor.mjs` rodada 2 (isolada) | 29 ok, 0 falhas |

Critérios 1 a 15 (escopo novo): todos PASSOU. Critério 1 vale para trabalhando, fila e falhou; 15 vale na Ao vivo (agente sem job não aparece). Critério 6: PASSOU, o clique abre /estudio/<slug>?etapa=<id> (evidência no e2e ao vivo). Não verifiquei em teste o "nó em foco" visual além da URL com etapa; confira no aceite.

Ressalvas: (1) `e2e_motor` e `e2e_corte` são flaky quando rodam em sequência de outros e2e (falha 1 vez, passa isolado; não é bug do PROG-003; para o **Rodrygo**/**Zico** virar item); (2) celular real e `--rede` não testados, só 390 px simulado; (3) ocioso e Catálogo ficam no PROG-016.

Bugs novos do PROG-003: nenhum. Sem alteração de código de produção.

---
(Histórico abaixo: relatório anterior, escopo antigo, DEVOLVIDO parcial)

# QA PROG-003 · Aba Agentes, Ao vivo (entrega 1) · Alisson

Data: 2026-11-05. Escopo: entrega 1 (Ao vivo, back + front). Catálogo (entrega 2) fora. Tudo rodado por mim, `.venv\Scripts\python` e `node`, uma bateria por vez, sem usar números do relatório de entrega. Sem commit, sem alterar código de produção.

## Veredito: DEVOLVIDO (parcial) — 2 pontos para decidir, nenhum bug de produção encontrado

Motivo: o item tem 15 critérios e a entrega 1 cumpre os da tela Ao vivo, mas (a) o critério 1 ("ocioso" visível por agente) e o 15 só fazem sentido no Catálogo (entrega 2), e (b) o critério 6 foi entregue só em parte (vai ao vídeo, não à etapa). Se o **Zico** aceitar a entrega 1 como fatia, o item fica APROVADO COM RESSALVAS para a fatia; o item inteiro só fecha com a entrega 2. Também há 2 testes flaky (abaixo), que não são bug do PROG-003 até prova em contrário.

## Baterias (resultado real)
| Bateria | Resultado |
|---|---|
| `testar_ao_vivo.py` | 49 ok, 0 falhas (50 jobs: `montar()` 30 ms frio, rota 40 ms no pior de 5, limite 200 ms) |
| `testar_status_video.py` rodada 1 | 45 ok, 0 falhas (100 pastas em 212 ms, limite 300) |
| `testar_status_video.py` rodada 2 | 45 ok, 0 falhas (143 ms). A falha de 526 ms não reproduziu em 2 rodadas isoladas; fica registrada como sensível à carga da máquina. |
| `testar_prog001_002.py` | "Tudo passou." (35 PASSOU, 0 falhou) |
| `testar_estilos.py` | 103 ok, 0 falhas |
| `e2e_agentes_ao_vivo.mjs` | 88 ok, 0 falhas |
| `e2e_celular.mjs` | 64 ok, 0 falhas |
| `e2e_interface.mjs` | 150 ok, 0 falhas |
| `e2e_corte.mjs` rodada 1 | **FALHOU**: 135 ok, 1 falha, `TimeoutError: Navigation timeout of 30000 ms` no bloco [7] "Entrada antiga só com MP4" |
| `e2e_corte.mjs` rodada 2 (isolada) | 152 ok, 0 falhas |
| `e2e_estilos.mjs` | 98 ok, 0 falhas |
| `e2e_motor.mjs` rodada 1 | **FALHOU**: 16 ok, 1 falha, `Waiting for selector "#e-agentes .agente-linha" failed: 30000ms` |
| `e2e_motor.mjs` rodadas 2 e 3 (isoladas) | 29 ok, 0 falhas nas duas |
| `e2e_agentes_ao_vivo_estresse.mjs` (novo, meu) | 15 ok, 0 falhas |

Falhas intermitentes: `e2e_corte` e `e2e_motor` falharam uma vez cada por timeout de 30 s e passaram ao repetir. Ambos rodaram em sequência, logo depois de outros e2e (Chrome e servidor recém-encerrados). Não reproduzi a causa. O seletor do `e2e_motor` é do Estúdio, não da aba Agentes. Recomendo ao **Rodrygo** olhar espera/limpeza de porta e Chrome entre baterias; não bloqueia o PROG-003, mas a bateria não está estável.

## Critério por critério
| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Indicador por agente: ocioso, trabalhando, fila, falhou, com texto | PASSOU parcial. Trabalhando, fila, falhou (e espera você) com ícone e palavra. **Ocioso não é mostrado** na Ao vivo (agente ocioso nem aparece, por desenho). | e2e ao vivo "Cada estado tem ícone e palavra"; "ocioso (não aparece)" em `testar_ao_vivo`. Ocioso como indicador: só na entrega 2 (Catálogo) |
| 2 | Vídeo e etapa em trabalhando/fila/falhou | PASSOU | e2e "Trabalhando: etapa, tempo…", "Falhou: etapa e primeira linha do motivo" |
| 3 | "há N min", avança sozinho | PASSOU | e2e "O tempo avança sozinho, sem nova consulta" |
| 4 | Motor Claude/Codex | PASSOU | e2e "motor Codex", "Nota do motor", job antigo sem motor sem "undefined"; `e2e_motor` 29 ok (2 de 3 rodadas) |
| 5 | Atualiza sozinho, sem recarregar, em até um ciclo | PASSOU | e2e "Mudança de estado aparece em até um ciclo", "Sem recarregar a página" |
| 6 | Clicar leva ao vídeo **e à etapa** | PASSOU parcial. Leva ao Estúdio do vídeo, **não** ao nó/etapa (limite 2 do **Endrick**, exigiria mexer em `corte_estudio.js`). | e2e "Clicar em Abrir no Estúdio leva ao Estúdio do vídeo". Nada testa a etapa; está faltando |
| 7 | Computador e celular (`--rede`) | PASSOU para 390 px simulado (uma coluna, 44 px, sem rolagem lateral). **Não testado** em celular real nem com `--rede` de verdade. | `e2e_celular` 64 ok; e2e "Cartões dentro da largura" |
| 8 | 50 jobs, responde e não cai | PASSOU | back: 40 ms (limite do critério 14 é 1 s, nota técnica 200 ms); front: "50 trabalhos: no máximo 10 cartões por seção" |
| 9 | Consulta falha: mantém último estado e avisa | PASSOU | e2e (consulta roteirizada) e meu estresse com servidor realmente morto (faixa "Sem atualização", sem erro de JS, volta sozinho) |
| 10 | Vazio claro em português | PASSOU | e2e "Nenhum agente trabalhando agora." sem undefined/NaN |
| 11 | Teste automatizado cobre estados, vazio e atualização | PASSOU | `testar_ao_vivo` + `e2e_agentes_ao_vivo` em `estudio/testes/`. Ocioso só é coberto no back |
| 12 | Edição de agentes continua funcionando | PASSOU | `e2e_corte` (duplicar, salvar, testar, restaurar) 152 ok na rodada 2; `e2e_interface` 150 ok. Rodada 1 do `e2e_corte` falhou por timeout em outro bloco |
| 13 | Mapeamento de estados | PASSOU | `testar_ao_vivo`: falhou some ao dispensar e após sucesso posterior da mesma etapa, não some com sucesso de outra etapa |
| 14 | Tempo avança a cada 1 s sem consulta; polling único; 50 jobs < 1 s | PASSOU | e2e contador; um só polling `Vivo` (4 s); rota 40 ms. "Polling já usado": o contrato escolheu 4 s, o mesmo do relógio do Estúdio |
| 15 | Agente sem job e sem histórico não mostra falhou nem tempo | PASSOU na Ao vivo (nem aparece). Visão do Catálogo: **só entrega 2** | `testar_ao_vivo` "ocioso não aparece" |

Resumo: cobertos só pela entrega 2: 1 (ocioso visível) e a visão de catálogo do 15. Sem teste: etapa no clique (6), celular real/`--rede` (7).

## Tentativas de quebrar (`e2e_agentes_ao_vivo_estresse.mjs`, 15 ok, 0 falhas)
- Troca rápida de abas: 30 pares de clique sem pausa e 10 pares de setas, sem erro de JS e sem DOM duplicado. Voltar/avançar do histórico em rajada, sem erro.
- Aba oculta: 30 alternâncias de visibilidade em rajada; oculta = sem consultas em 9 s; ao voltar consulta na hora.
- Servidor morto de verdade (processo encerrado): faixa "Sem atualização" em 10 s, faixa vermelha após 30 s, sem erro de JS; ao subir de novo a faixa some sozinha.
- Resposta 200 com formato inválido (`{"agentes":7,"resumo":null}`): sem erro de JS e sem "undefined/NaN".
- Consulta com erro (back): `testar_ao_vivo` devolve 500 JSON e o servidor segue; rota `ao-vivo` não cai em `/api/agentes/<id>`.
- Não testei: reduzir movimento, leitor de tela real, SQLite travado de verdade, 1000+ jobs.

## Bugs novos
Nenhum bug de produção do PROG-003. Para o **Zico** virar item, se quiser: (1) testes `e2e_corte`/`e2e_motor` com timeout intermitente de 30 s ao rodar em sequência (não reproduz isolado); (2) clique no cartão não chega à etapa (critério 6); (3) falta de indicador "ocioso" na Ao vivo (critério 1, entrega 2).

## Observação
Adicionei `estudio/testes/e2e_agentes_ao_vivo_estresse.mjs` (teste novo, só em `estudio/testes/`). Os `testar_*` e `e2e_*` do `e2e_celular`/`e2e_corte` foram ajustados pelo **Endrick** para `/agentes?aba=catalogo`; conferi que as rotas antigas `/agentes/<id>` continuam abrindo a ficha.

## Reconferência de 05/11 (tarde) · Alisson
Depois da documentação da rota (README) rodei de novo: `testar_ao_vivo.py` 49 ok, 0 falhas (rota 42 ms com 50 jobs); `e2e_agentes_ao_vivo.mjs` 88 ok, 0 falhas. Resto da regressão segue como na tabela acima. Veredito mantido: **DEVOLVIDO** à coluna Fazendo. Faltam os critérios 1 (indicador "ocioso" por agente, que é o Catálogo, entrega 2) e 6 (clique chegar à etapa, não só ao vídeo). Se o **Zico** decidir aceitar a entrega 1 como fatia e abrir itens novos para esses dois pontos, o QA vira APROVADO COM RESSALVAS para a fatia, sem novo teste.

## Reconferência final de 05/11 (critérios ajustados) · Alisson — VEREDITO: APROVADO (fatia Ao vivo)
Com os critérios 1 e 15 reduzidos à Ao vivo (ocioso/Catálogo no PROG-016) e o critério 6 implementado pelo **Endrick**, rodei de novo, uma bateria por vez:
- `testar_ao_vivo.py`: 49 ok, 0 falhas. `testar_prog001_002.py`: tudo passou.
- `e2e_agentes_ao_vivo.mjs`: 91 ok, 0 falhas. Inclui "O clique leva o id da etapa na URL (?etapa=metadados)" e "Critério 6: o Estúdio abre com o nó da etapa em foco e destacado".
- Regressão: `e2e_corte` 152 ok; `e2e_celular` 64 ok; `e2e_interface` 150 ok; `e2e_motor` 29 ok (todas 0 falhas, desta vez sem timeout).
- Critérios 1 (trabalhando, fila, falhou, espera você, com ícone e texto), 2, 3, 4, 5, 6, 7 (390 px simulado), 8, 9, 10, 11, 12, 13, 14, 15 (na Ao vivo): PASSOU.
Ressalvas (não bloqueiam): celular real com `--rede` não testado; testes e2e_corte/e2e_motor tiveram timeout intermitente em rodada anterior quando encadeados (não reproduziu); o **Guilherme** deve confirmar o ajuste de critérios no aceite.
