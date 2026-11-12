# PROG-003 · Aba Agentes, Ao vivo · Entrega do back, dia 1 (Rodrygo)

Data: 2026-11-05. Escopo: só o backend (contrato em `tecnico/PROG-003.md`). Tela, selo do menu e `seloMotor` são do **Endrick**. Sem commit.

## O que mudou
- `estudio/ao_vivo.py` (novo): `montar()` devolve o contrato. Uma única query em `jobs` (ativos, falhos ainda abertos e concluídos na última hora, com `NOT EXISTS` para a regra "sem job posterior da mesma etapa"). "Espera você" fica em cache de 3 s com trava única (`invalidar_cache()` existe para teste). Não lê `log.txt` nem `trabalhos.progresso()`.
- `estudio/servidor.py`: import de `ao_vivo` e rota `GET /api/agentes/ao-vivo`, colocada antes de `/api/agentes/<id>`. Qualquer exceção vira 500 JSON `{"erro": [...]}` sem vazar o detalhe.
- `estudio/testes/testar_ao_vivo.py` (novo): 49 verificações, banco e pasta temporários (`ESTUDIO_RAIZ`/`ESTUDIO_DADOS`), agentes das fixtures vindos de `fluxo.ETAPAS`.

## Testes cobertos (lista de "Testes exigidos")
ocioso; trabalhando; fila (posição e espera); falhou (erro de 1 linha, máx. 160, some ao dispensar, some com sucesso posterior da mesma etapa, não some com sucesso de outra etapa, continua aberta após 1 h); espera você (agente do último job, reserva no agente fixo da etapa, arquivada fora, cache de 3 s); vários jobs por agente (uma entrada com lista); job sem `spec.agente` (e spec ilegível) em `resumo.ignorados`; motor com nota; motor sem nota; job sem `motor` (antigo); `alerta_longo` (899 não, 900 sim); concluídos só da última hora; teste de agente com `origem` e rótulo; 50 jobs; erro na consulta devolve 500 JSON e o servidor segue; a rota `ao-vivo` não cai no `<id>`; leitura não altera o banco.

## Comandos e resultado real (`.venv\Scripts\python`)
- `estudio\testes\testar_ao_vivo.py`: **49 ok, 0 falhas**. 50 jobs + 30 produções esperando você, cache frio: `montar()` em 30 ms; pela rota, pior de 5 pedidos em 39 ms (limite 200 ms); com cache quente `montar()` em 5 ms.
- `testar_prog001_002.py`: tudo passou. `testar_cronograma.py`: 42 ok, 0 falhas. `testar_reserva_codex.py`: tudo certo. `testar_roteiro.py`: 29 ok.
- `testar_status_video.py`: 45 ok, 0 falhas na minha rodada. Uma rodada anterior (versão anterior deste relatório, escrita por outra chamada) registrou 1 falha de tempo ("100 pastas em 526 ms, limite 300 ms"); a minha deu 200 ms. É medida de tempo de outro módulo, sensível à carga da máquina; não toco nele.
- Não rodados: e2e (`.mjs`), `testar_estilos.py`: dependem da tela ou não tocam o que mudei.

## Decisões e mudanças de contrato (avisar **Thiago Silva**)
O contrato de campos ficou como na nota. Mudanças e escolhas a registrar:
1. `resumo` ganhou `ignorados` (já previsto na regra de `spec.agente`; o exemplo do JSON não o mostrava).
2. `frescor` vale `"ok"` ou `"parcial"` (parcial quando uma produção não pôde ser lida no "Espera você"; as demais seguem).
3. Prioridade do estado do agente: `falhou` > `espera_voce` > `trabalhando` > `fila` (a nota dizia só que as duas primeiras "sobem").
4. "Espera você" usa `fluxo.Contexto(slug).etapa_status(...) == "aguardando"` das produções não arquivadas, em vez de `fluxo.estado(slug, sincroniza=False)`: é o mesmo cálculo de status da etapa, sem montar ações e consequências. Não grava no banco além do que `Contexto` já faz.
5. Entrada `espera_voce`: `segundos_na_tarefa` = null; `aguarda_s` = segundos desde o término do último job da etapa (null se não houver job).
6. `origem`: `teste_agente` (spec), `grafo` (slug com execução) ou `estudio`. Jobs de teste usam slug `__agentes__` e `etapa_nome` "Teste de agente".
7. `concluidos_1h` limitado a 30, mais recentes primeiro. `craque` vem do mapa do fluxo (inclui Barcola), senão do job, senão de `agentes.nome_curto`.
8. Não criei índice em `jobs(status)`: não toquei em `banco.py` (fora do escopo) e com 50 jobs a query não pesa. Se o histórico crescer muito, vale reavaliar.
9. Barra final (`/api/agentes/ao-vivo/`) dá 404, como as demais rotas do servidor.

## Pendente
- Tela Ao vivo, selo no menu, `seloMotor`, e2e `e2e_agentes_ao_vivo.mjs` e regressões (**Endrick**, depois **Alisson**).
- Aceite do **Alisson**.

---

# PROG-003 · Aba Agentes, Ao vivo · Front, entrega 1 (Endrick)

Data: 2026-11-05. Escopo: só a entrega 1 (Ao vivo). Catálogo (entrega 2: selos na lista e faixa na ficha) fica fora; o conteúdo do Catálogo segue como estava. Sem commit.

## O que mudou na tela
- `/agentes` agora abre **Ao vivo**; `/agentes?aba=catalogo` abre o Catálogo de hoje; `/agentes/<id>` continua abrindo a ficha. Abas com `role="tablist"`, setas esquerda/direita trocam, foco acompanha. Na aba que não está aberta, "Ao vivo" leva `(N)` (trabalhando + fila + espera você) ou `(!)` se algo falhou.
- Menu: o item "Agentes" ganha um selo com a contagem (ou `!` em vermelho). É um `aria-live="polite"` e lê o resumo completo ("Agentes: 1 trabalhando · 1 falhou"). Funciona em qualquer tela, não só em Agentes.
- Ao vivo: resumo no topo (aria-live), faixa de aviso, seções **Atenção** (falhou, depois espera você), **Agora** (trabalhando, depois na fila) e **Concluídos na última hora** (recolhido). Cartão por agente; vários vídeos do mesmo agente viram um cartão com lista ("Trabalhando em 2 vídeos"). Motor com `seloMotor(job)` do PROG-006 (Codex tocável, nota aparece). Até 10 cartões por seção e "+12 na fila, ver todos".
- Estados: carregando (esqueletos), vazio ("Nenhum agente trabalhando agora." com Ir para Projetos e Ver o Catálogo), desatualizado (faixa âmbar "Sem atualização desde HH:MM (há N min). Mostrando o último estado conhecido." + Tentar agora; contadores param e ganham "(pode ter mudado)"; ao voltar, faixa verde "Atualizado." some em 3 s), servidor fora do ar por mais de 30 s (faixa vermelha, "no computador" ou "no computador de casa" na rede), primeira consulta com erro (mensagem sem afirmar que ninguém trabalha) e `frescor: "parcial"` (aviso de que "Espera você" pode estar incompleto).
- Tempo: contador local de 1 s a partir de `segundos_na_tarefa`/`aguarda_s`/`terminou_ha_s` mais `Date.now()` desde o recebimento; `iniciado_em` e `gerado_em` nunca são lidos. Depois de 900 s, âmbar "mais que o normal".
- Clique: "Abrir no Estúdio" (trabalhando, fila), "Ver o que houve" (falhou), "Abrir para decidir" (espera você) vão a `/estudio/<slug>` e mostram "Abrindo…". "Ver ficha do agente" abre `/agentes/<id>`. Job de teste de agente mostra "Teste de agente" e "Ver o teste" (leva à ficha, não ao Estúdio).
- Polling: um só, a cada 4 s (`Vivo` em `corte_nav.js`), compartilhado pelo selo do menu e pela aba; para com `document.hidden` e consulta na hora ao voltar. A tela só é refeita se a resposta mudou (sem contar os segundos).

## Arquivos
- `estudio/web/corte_nav.js`: `Vivo` (polling e estado), selo do menu, `duracao()`, estados `trabalhando`, `fila` e `espera_voce` em `seloEstado`.
- `estudio/web/corte_agentes.js`: `AoVivo` (aba), `Agentes` com abas; Catálogo sem mudança de lógica, só duas guardas (`carregar` e `abrir` não desenham se a aba/tela já trocou; sem elas a troca rápida de aba dava erro de JS).
- `estudio/web/corte.css`, `estudio/web/celular.css`: aba, cartões, faixas, selo, celular (uma coluna, alvos de 44 px, chip do motor para baixo, sem animação com "reduzir movimento").
- Testes: `estudio/testes/e2e_agentes_ao_vivo.mjs` (novo). Ajustei a URL do Catálogo em `e2e_celular.mjs` e `e2e_corte.mjs` (agora `/agentes?aba=catalogo`, porque `/agentes` mudou de destino por decisão do contrato) e acrescentei a tela Ao vivo ao e2e do celular.
- Não toquei em `servidor.py`, `ao_vivo.py` nem `app.js`.

## Testes e resultado real (`node`, Chrome real, caixa descartável, `claude_simulado`)
- `e2e_agentes_ao_vivo.mjs`: **88 ok, 0 falhas** (primeira rodada: 3 falhas, duas de teste e uma real, o erro de JS na troca rápida de aba, já corrigida). Cobre: vazio e job falho/concluído pela rota de verdade; cada estado, seções, ordem, resumo, motor Claude/Codex/ausente, desativado, teste de agente, vários vídeos, 50 trabalhos; contador que avança sem nova consulta; atualização por polling sem recarregar; não redesenha sem mudança; consulta com erro (faixa, último estado, contador parado, volta, queda >30 s, primeira consulta sem dados); `frescor` parcial; cliques ao Estúdio e à ficha; rotas e abas por teclado; selo do menu fora da aba; pausa com aba oculta; celular a 390 px.
- `e2e_celular.mjs`: **64 ok, 0 falhas** (com Ao vivo e Catálogo).
- `e2e_interface.mjs`: **150 ok, 0 falhas**.
- `e2e_corte.mjs` (tem a regressão da edição de agentes: duplicar, salvar, testar, restaurar): **152 ok, 0 falhas**.
- `e2e_motor.mjs`: **29 ok, 0 falhas**.
- Não rodados: `testar_estilos.py`, `e2e_estilos.mjs` (não toquei no que eles exercitam); Python (`testar_ao_vivo.py` etc.) é do back, já rodado pelo **Rodrygo**.

## Limites e pontos para o **Thiago Silva** e o **Zico**
1. O estado "Sem agentes cadastrados" do desenho não existe na Ao vivo: a rota não informa o total de agentes, então o vazio é sempre "Nenhum agente trabalhando agora".
2. "Abrir no Estúdio" não abre o painel do nó (`abrirExecucao`) nem checa se o vídeo existe (aviso "Este vídeo não está mais no Corte"): o Estúdio não aceita um parâmetro de nó, e isso exigiria mexer em `corte_estudio.js`, fora do escopo. Vai ao Estúdio do vídeo.
3. O desenho do **Iniesta** fala em azul para "Trabalhando/Na fila"; a interface atual usa a paleta amarela, então usei o amarelo do tema (trabalhando), cinza (fila), amarelo de decisão (espera você) e vermelho (falhou), sempre com ícone e palavra.
4. A função do agente ("diretor de arte") não vem no contrato; o cartão mostra craque e id.
5. O selo do menu e a aba contam trabalhando + fila + espera você; `!` quando há falha (decisão minha; o desenho só citava trabalhando + fila).
6. Aguardando: o aviso de contador "aguardando você há X" usa `aguarda_s` como o contrato novo define.

---

# PROG-003 · Rodrygo, rodada de 05/11 (tarde)
- Reroda: `testar_ao_vivo.py` **49 ok, 0 falhas** (50 jobs: 31 ms, rota 40 ms).
- Pendência da revisão fechada: `estudio/README.md` agora documenta a rota `/api/agentes/ao-vivo`, a prioridade dos estados, `frescor`, o selo do menu e os dois testes novos.
- Ficam com outros: índice em `jobs` (item novo ao **Zico**, prioridade baixa), contrato atualizado (**Thiago Silva**), aceite (**Alisson**).

---

# PROG-003 · Rodrygo, rodada de 05/11 (fim da tarde, chamada do maestro)
- Reroda: `testar_ao_vivo.py` **49 ok, 0 falhas** (50 jobs: `montar()` 32 ms frio, rota 40 ms no pior de 5).
- Sem mudança de código nesta rodada. Os dois pontos que o **Alisson** devolveu não são do back: o critério 1 (indicador "ocioso" por agente) é o Catálogo, entrega 2 (**Endrick**); o critério 6 (clique chegar à etapa) exige mexer em `corte_estudio.js` (**Endrick**), e o contrato atual não traz o que falta. Se o **Zico** quiser, o back só entra se pedirem campo novo (`funcao`, total de agentes, ou lista de agentes ociosos).
- Cartão fica em Fazendo até o **Zico** decidir: aceitar a entrega 1 como fatia (com itens novos para 1 e 6) ou manter aberto para a entrega 2.

---

# PROG-003 · Endrick, rodada de 05/11 (chamada do maestro): critério 6

## O que mudou na tela
- Clicar em "Abrir no Estúdio", "Ver o que houve" ou "Abrir para decidir" leva a `/estudio/<slug>?etapa=<id da etapa>`. O Estúdio (`corte_estudio.js`, `focarEtapa`) destaca o nó dessa etapa (`em-foco`, `aria-current="step"`), rola até ele e põe o foco nele, uma vez. Etapa que não existe na tela: nada quebra, só não destaca.
- Cartão de teste de agente continua indo à ficha (não há etapa de vídeo).

## Testes (caixa descartável, Chrome real, uma bateria por vez, portas próprias)
- `e2e_agentes_ao_vivo.mjs`: **91 ok, 0 falhas** (inclui "O clique leva o id da etapa na URL" e "Critério 6: o Estúdio abre com o nó da etapa em foco e destacado", e "só um nó em foco").
- `e2e_corte.mjs`: 152 ok, 0 falhas. `e2e_celular.mjs`: 64 ok, 0 falhas. `e2e_interface.mjs`: 150 ok, 0 falhas (regressão da edição de agentes em `e2e_corte`).
- Observação honesta: na primeira passada, `e2e_agentes_ao_vivo` (2 falhas) e `e2e_interface` (falha de espera) falharam porque outra chamada mexia no mesmo teste e usava a mesma porta ao mesmo tempo. Com `E2E_PORTA` própria e o teste já corrigido, ficaram verdes.
- Caso de erro: consulta falha mantém último estado com faixa "Sem atualização". Caso vazio: "Nenhum agente trabalhando agora."
- Não testado: celular real com `--rede`.

## Falta
Aceite do **Alisson** (critérios 1 e 15 já saíram para o PROG-016) e confirmação do **Guilherme** do ajuste de critérios.

## Critério 6 (clique chega à etapa) — Endrick, 05/11/2026
Feito: o botão do cartão em Agentes > Ao vivo agora abre `/estudio/<slug>?etapa=<etapa_id>`. O Estúdio lê `?etapa=`, destaca o nó correspondente na coluna Agentes (classe `em-foco`, `aria-current="step"`), rola até ele e dá foco, uma vez; os redesenhos seguintes mantêm o destaque sem roubar o foco.
Arquivos: `estudio/web/corte_agentes.js` (URL com etapa), `estudio/web/corte_estudio.js` (`montar` lê a etapa; `focarEtapa`), `estudio/web/corte.css` (`.agente-linha.em-foco`), `estudio/testes/e2e_agentes_ao_vivo.mjs` (3 casos novos: etapa na URL, nó em foco/destacado, só um em foco).
Limite: se o `etapa_id` do job não for um nó da execução (ex.: execução antiga sem grafo), o Estúdio abre normalmente, sem destaque.
Resultados reais (um por vez): e2e_agentes_ao_vivo 91 ok / 0 falhas; e2e_celular 64/0; e2e_motor 29/0; e2e_interface 143 ok / 7 falhas na rodada em sequência, repetido isolado 150/0 (intermitente, não reproduz).
