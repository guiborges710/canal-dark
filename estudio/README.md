# Corte (pacote `estudio/`)

Interface web local para acompanhar e aprovar cada produção, editar o vídeo e mudar quem faz o quê no fluxo. Não substitui nada do terminal: `run.py`, a squad e os agentes continuam funcionando como antes, e o que for feito por fora aparece aqui como nova versão.

```
.venv\Scripts\python -m corte      (ou, como sempre: .venv\Scripts\python -m estudio)
```

| Tela | Rota | O que faz |
|---|---|---|
| Projetos | `/` | fila de revisão, abrir produções, novo projeto com fluxo, estilo e legenda |
| Estúdio | `/estudio/<slug>` | agentes à esquerda, prévia ao centro, direção e aprovações à direita, cenas abaixo |
| Revisão | `/producao/<slug>?etapa=...` | roteiro, narração, assets e vídeo final, por versão |
| Editor | `/editor/<slug>?t=...` | linha do tempo que altera a exportação |
| Agentes | `/agentes` | catálogo e editor; grava em `.claude/agents/<id>.md` |
| Fluxos | `/fluxos` | grafo editável; o executor obedece à versão publicada |

## Editor de vídeo

**Estado:** `output/<slug>/corte.json`, só depois da primeira edição. IDs estáveis (`cn-cena_3`, `na-cena_3`, `le-...`), intervalos e referências aos originais por sha. Nada disso entra no `run.py`.

**Uma compilação só:** `corte.compilar()` resolve o corte em quadros. A prévia e o export recebem o mesmo resultado e desenham com o mesmo `web/compositor.js` (no export, pelo Chrome local em `render/corte_compor.mjs`). O áudio sai do mesmo `corte.mixar()`, com as falas em stems e os efeitos de `media/sfx.py`. `testes/comparar_midia.py` confere isso no MP4.

**Fonte de imagem por cena:** no sketch, um clipe desenhado por `cena_N(lt, dur)` de `sketch_cenas.py`, guardado por chave (mudar outra cena não invalida esta). Sem desenho que rode, recorta do vídeo do projeto. No estilo cartões, recorta o MP4 pelos tempos das cenas, se a soma bater com o vídeo. Sem isso, o projeto abre como "só MP4": aparar, legenda e volume, e a tela diz o que falta para o resto.

**Exportar** grava `output/<slug>/video.mp4` com o encode do render. Ele vira nova versão do vídeo final, precisa de revisão, e o **Vini** audita, como depois de todo render. A versão anterior continua no depósito.

**Conflitos:** o corte usa o que estava quando foi editado. Se um agente refaz uma fala ou um desenho, o editor mostra o que mudou e você escolhe aplicar. Legenda manual, enquadramento, volume e asset ficam. Se a fala nova não cabe na cena, ele avisa que exige ressincronizar.

**Legendas:** `viral` (de `media/captions.py`), `caderno` (Kalam, do sketch), `cartao` (do motor SVG) ou nenhuma, o padrão do canal. Sem tempo por palavra: o Chatterbox não informa, então o tempo é proporcional ao texto, como em `captions.build_cues`.

## Fluxos

**Primeira abertura:** `grafos.grafo_real()` é o fluxo enxuto do `CLAUDE.md`, já publicado como v1. Nós: briefing, agente, aprovação, condição, junção, render e saída.

**Separação:** a definição do agente está no `.md`; a configuração do nó (tarefa, instruções, agente, versão fixa) está no grafo; o estado da execução está em `exec_nos`. Execução em andamento guarda a foto do grafo e dos agentes (`execucoes`), e roda o agente com `--system-prompt-file` a partir dessa foto.

**Produção antiga continua no fluxo fixo** de `fluxo.py`. O grafo vale só para quem foi criado com um fluxo, ou acionou "Executar pelo fluxo": aí o que já existe é reaproveitado.

**Sem duplicar:** toda mudança de estado de nó é um `UPDATE ... WHERE status=<anterior>`, e a fila continua recusando dois trabalhos ativos na mesma etapa. Pedir ajuste reabre só aquele ramo; ao retomar, nó com as mesmas entradas não roda de novo.

**Narração em paralelo às cenas:** sem `cenas.json`, `estudio/narrar.py` narra um trecho por parágrafo da seção `## Narração`. Funciona com o render se o **Olise** cumprir o contrato dele ("cada fala vira uma cena"). Se ele dividir diferente, o render narra de novo.

**Testar com um projeto** percorre o grafo contra os arquivos do projeto, sem acionar agente. O teste de verdade de um agente fica na tela Agentes.

## Agentes

Salvar escreve no `.md`; o banco guarda só o histórico (`agente_versoes`). Mudança feita por fora entra como versão nova. Desativar move o arquivo para `.claude/agents_desativados/`, e isso vale no terminal também. O contrato é `entradas:` e `saidas:` no frontmatter; quem não declarou usa `agentes.CONTRATOS`. Ferramentas e modelos oferecidos são só os que já existem: `Bash(...)` novo não entra pela interface. O teste roda de verdade, numa pasta só dele, com teto de US$ 1,00.

### Ao vivo (PROG-003)

`GET /api/agentes/ao-vivo` (`estudio/ao_vivo.py`) devolve, só lendo o banco, o estado de cada agente com trabalho: `trabalhando`, `fila`, `espera_voce` ou `falhou` (prioridade nessa ordem: falhou > espera_voce > trabalhando > fila), mais `resumo`, `frescor` (`ok` ou `parcial`) e `concluidos_1h`. "Espera você" tem cache de 3 s. A tela consulta a cada 4 s (`Vivo` em `corte_nav.js`), para com a aba oculta, e o selo do menu Agentes mostra a contagem (trabalhando + fila + espera você) ou `!` se algo falhou. Contrato em `programacao/tecnico/PROG-003.md`. Testes: `testar_ao_vivo.py` e `e2e_agentes_ao_vivo.mjs`.

## Reserva com Codex

Os mesmos agentes rodam pelo Codex **somente quando o Claude esgota** (limite de 5 horas, semanal ou de uso). Vale só para os trabalhos de agente do Corte (inclusive agentes presos a versão e execuções de fluxo), e só quando a falha do Claude é o texto de limite (`reserva.e_limite_do_claude`); erro comum, tempo esgotado, teto de custo ou falha de conteúdo continuam falhando como antes.
- O trabalho é refeito uma única vez, com o mesmo agente (instruções lidas de `.claude/agents/<id>.md`), o mesmo pedido e a mesma pasta, por `codex exec` não interativo: sandbox `workspace-write`, sem rede de shell, sem aprovação, sem sessão salva. O Codex falhar não volta ao Claude, e o próximo trabalho sempre tenta o Claude primeiro.
- O job mostra `motor` (`claude` ou `codex`) e `motor_nota` no estado público do job (`fluxo.status_job_publico`), e o histórico registra "Executado pelo Codex: o Claude estava no limite". Se o Codex não estiver instalado, logado ou falhar, a falha original do Claude continua visível com a nota do motivo.
- O Codex é achado por `ESTUDIO_CODEX` ou `CODEX` (ambiente ou `.env`), depois pelo PATH e pela extensão do VS Code (`openai.chatgpt-*`). Precisa de `codex login`. `CODEX_MODELO` no `.env` (opcional) escolhe o modelo.
- Para o uso no terminal, `python tools/sincronizar_codex.py` espelha `.claude/agents` em `.codex/agents/*.toml` e as skills em `.agents/skills` (`--verificar` só confere). Rode depois de mudar um agente. A conversa do Claude Code NÃO troca sozinha de motor: nesse caso abra o Codex na pasta e chame os agentes de `.codex/agents`.
- Teste (offline, com Claude e Codex falsos e pasta de dados temporária): `.venv\Scripts\python estudio/testes/testar_reserva_codex.py`. Com `--real` usa o login do Codex só numa pasta temporária (sem gastar o Claude).

## Celular, na rede de casa

```
.venv\Scripts\python -m corte --rede
```

O terminal mostra o endereço (por exemplo `http://192.168.0.190:8765/`) e a senha. No celular, no mesmo Wi-Fi, abra o endereço e digite a senha. Sem `--rede`, nada muda: o Corte só escuta no próprio computador.

- **Senha:** gerada na primeira vez e guardada em `estudio/dados/senha_rede.txt` (fora do git). `ESTUDIO_SENHA` troca por outra. Cinco erros bloqueiam o aparelho por 5 minutos. Reiniciar o Corte desconecta todos os celulares; a sessão dura 30 dias.
- **O que é recusado:** quem não é de rede privada (se um roteador abrir a porta para a internet, o endereço que chega é público e não entra), nome de site no cabeçalho Host (DNS rebinding) e POST vindo de outra página.
- **Sem criptografia:** é HTTP. Serve para o Wi-Fi de casa, onde a senha trafega em claro entre o celular e o computador. Não abra a porta do roteador para a internet.
- **Firewall:** na primeira vez, o Windows pergunta se o Python pode receber conexões. Permita só em rede particular.
- **Fora de casa:** não funciona. Isso pede uma rede privada entre os aparelhos (Tailscale, por exemplo), que não está montada.
- **Layout:** até 820 px de largura as telas viram uma coluna só (`web/celular.css`). Acompanhar, aprovar e pedir ajuste são pensados para o dedo; o editor e o grafo dos fluxos abrem, mas editar com precisão ali é melhor no computador.

## Estilos de vídeo

O registro único é `media/estilos.py`. A interface, os prompts, a validação e o render leem dele.

| Na tela | Id gravado | Motor |
|---|---|---|
| Cartão | `cartoes` (aceita `card`) | `render/`, no Chrome |
| Scratch | `sketch` (aceita `scratch`) | `sketch_cenas.py`, escrito pelo agente |
| Cartoon Vivo | `cartoon_alive` | cena em dados, `media/cartoon_lib.py` |
| Colagem Documental | `documentary_collage` | cena em dados, `media/colagem_lib.py` |

`cartoes` e `sketch` continuam sendo os ids porque já estão nos projetos antigos, nos `cenas.json` e no fluxo publicado.

**Persistência:** `producoes.estilo` e `output/<slug>/estilo.json` (com a variação). No terminal, sem banco, vale o `tipo` das cenas, mais a variação do `estilo.json`.

**Trocar o estilo:** selo no Estúdio. A tela lista o que será refeito, e o servidor só aceita a confirmação daquela lista. Os arquivos antigos vão para `_troca_estilo/<data>/`, as versões ficam no histórico e `producoes.estilo_corte` diz a partir de qual versão elas valem. No grafo, só os nós afetados reabrem.

**Criar outro estilo:** uma entrada em `media/estilos.py` com `motor: "dados"`; uma lib com `CAMPOS`, `validar(cena, onde)`, `textos(cena)` e `quadro(cena, lt, dur, ctx)`; a amostra em `media/demos/<id>/cenas.json`; o contrato na skill `estilos-por-camadas`; e `python -m media.estilos_demo <id>`. Render, prévia, editor e conformidade já funcionam por esse caminho.

## Temas prontos

A janela de novo projeto lista o que `output/modric_10_temas.md`, `output/modric_tema_*.md` e `output/ideias.json` trazem e ainda não tem vídeo (`estudio/temas.py`). Não há lista à parte. "Gerar um tema" aciona o **Modric** de verdade, e ele grava mais um `modric_tema_<assunto>.md`. O cruzamento com os projetos é por palavras do título e do nome da pasta.

## Estúdio e revisão

Abre em http://127.0.0.1:8765/ (só nesta máquina). `--porta N` troca a porta; `--nao-abrir` não abre o navegador. Fechar a página não interrompe nada. Encerrar o servidor também não: o trabalho em andamento roda em processo próprio e é reencontrado quando o estúdio volta.

## Como funciona

**Os arquivos continuam sendo a fonte da verdade.** A cada leitura, o estúdio compara `output/<slug>/` com a última versão registrada de cada material. Se mudou, grava uma versão nova, com cópia em `estudio/dados/blobs` (por conteúdo, sem repetir o que não mudou). É assim que a versão anterior continua consultável.

**A aprovação fica presa à versão.** Roteiro e vídeo final se aprovam por versão. Narração e assets se aprovam por item, e a decisão fica presa ao conteúdo daquele item: quando o agente refaz só um, os demais continuam aprovados.

**Cada versão registra de quem dependia.** Assim dá para saber o que uma mudança invalida. Se uma frase do roteiro muda, o estúdio compara com a versão anterior, acha as cenas afetadas e marca só a narração delas e o render como desatualizados.

### Etapas

| Etapa | Quem faz | Como começa | Sua decisão |
|---|---|---|---|
| Pesquisa | **Modric** | ao criar o vídeo | não |
| Roteiro | **Neymar**, depois **Courtois** | depois da pesquisa | sim, por versão |
| Componentes | **Raphinha** | ao aprovar o roteiro (todos os estilos: sketch, cartões, cartoon vivo e colagem) | sim, por item (fase "aprendendo") |
| Cenas | **Olise** (**Barcola** no horizontal) | ao aprovar os componentes | sim, por cena (recorte da `previa.jpg`) |
| Metadados | **Mbappé** | ao aprovar o roteiro | não |
| Auditoria de texto | **Vini** | quando cenas e metadados ficam prontos | só se bloquear |
| Narração | `python -m estudio.narrar` | botão | sim, por trecho |
| Vídeo final | `python run.py video` (no 3D, `media.clay3d`) | botão | sim, por versão; libera o download |
| Auditoria final | **Vini** | depois de cada render | só se bloquear |

Na API de estado (`/api/producoes/<slug>`): `execucao` (id da execução ativa), e por etapa `motivo_nao_aplica` (texto) e `bloqueio` (`{execucao, no, nome, status, nota}`, também em `acoes.iniciar.bloqueio`) quando um nó do fluxo falhado ou parado segura a etapa; "Tentar de novo" é `POST /api/execucoes/<id>/repetir {no}`. Em produção conduzida por grafo, `acoes.iniciar.via_fluxo` pede ao grafo o próximo passo (`POST .../iniciar` chama `grafos.avancar`). Um trabalho concluído fora do grafo pelo mesmo agente resolve o nó que tinha falhado (`grafos._resolver_por_fora`). `grafos.migrar_execucao(slug)` leva uma execução ativa para a versão mais nova do fluxo.
| Thumbnail | **Seedorf** | botão | não |

Abrir uma produção nunca dispara agente. Só disparam, sozinhos, os agentes logo depois de um trabalho ou de uma aprovação, e o botão diz isso antes do clique. Narração e render sempre têm botão próprio. Publicar continua fora do estúdio: `python run.py publish --slug <pasta>`.

### Para onde vai o seu comentário

| Material | Agente |
|---|---|
| Roteiro | **Neymar**, depois **Courtois** confere |
| Componentes | **Raphinha** |
| Cenas | **Olise** ou **Barcola** |
| Narração | **Neymar** grava o ajuste em `voz_ajustes.json`, e o estúdio gera de novo só aqueles trechos |
| Vídeo final | conforme a categoria: imagem ou som vão para **Olise**; texto, para **Neymar**; narração, como na linha acima |

O agente recebe o material, a versão, a cena, o instante e o seu texto. **Kane** não entra aqui: pelo contrato dele, ele narra vídeos soltos de `videos-kane/` e não usa `output/`.

`voz_ajustes.json` (novo, opcional, em `output/<slug>/`) muda como um trecho é dito sem mudar a `fala` oficial das cenas: `{"2": {"dizer": "í bê gê é", "velocidade": 1.05, "exaggeration": 0.7}}`.

### Trabalhos

Cada trabalho roda em `estudio/executor.py`, destacado do servidor, e escreve em `estudio/dados/jobs/<id>/`. O banco recusa dois trabalhos ativos na mesma etapa, então clique duplo ou recarga não duplicam nada. Render e narração rodam um por vez; agentes, até três juntos.

Os agentes rodam com `claude -p --agent <id>`, do mesmo jeito que o Telegram: sem as chaves do `.env` (usa o login, nunca a `ANTHROPIC_API_KEY`) e com teto de US$ 3,00 por trabalho (`ORCAMENTO_AGENTE`). O `--allow-paid` não é oferecido na interface.

Pastas de antes do estúdio entram em "Em andamento" até a primeira decisão. Pastas já enviadas ao YouTube ou paradas há mais de 14 dias entram arquivadas e podem ser abertas e trazidas de volta.

## Status de cada vídeo (PROG-012)

`estudio/status_video.py` deriva, só lendo `output/<slug>/` e `output/fila_postagem.txt`, um status por vídeo: sem roteiro, em produção, vídeo pronto, auditado, na fila de postagem, publicado (privado) e público. Não grava nada, não usa rede nem banco. A regra (primeira condição verdadeira, de cima para baixo) é a D-001 de `programacao/tecnico/decisoes.md`.

- Rota `GET /api/videos/status` (só leitura): `{videos[], proximo_pronto{sim, slug, motivo}, fila_orfaos[]}`; cada vídeo traz `status`, `status_texto`, `avisos[]` (contradições em português), `falta[]`, `fila_posicao`, `publicado` e `atualizado_em`.
- Terminal: `.venv\Scripts\python -m estudio.status_video`.
- "Público" só aparece com `upload.json` de `privacy: public` ou com o arquivo `output/<slug>/publico.json` (marcação manual do Guilherme; o conteúdo pode ser `{}`).
- "Auditado" usa o mesmo critério do `run.py publish` (APROVADO e sem BLOQUEADO).
- Teste: `.venv\Scripts\python estudio\testes\testar_status_video.py`.

## Dados

`estudio/dados/` (fora do git): `estudio.db` (SQLite), `blobs/` (versões) e `jobs/` (logs). Apagar a pasta zera decisões e histórico, sem tocar em `output/`. Os blobs guardam cópias de vídeo e áudio de cada versão das produções abertas, então a pasta cresce com o uso.

## Testes

Nenhum deles toca nas produções reais nem consome nada pago:

```
node estudio/testes/e2e_corte.mjs [pasta para capturas]
node estudio/testes/e2e_estilos.mjs [pasta para capturas]
node estudio/testes/e2e_celular.mjs [pasta para capturas]
.venv\Scripts\python estudio\testes\testar_estilos.py [pasta para capturas]
node estudio/testes/e2e_interface.mjs [pasta para capturas]
.venv\Scripts\python estudio\testes\validar_real.py
.venv\Scripts\python estudio\testes\testar_status_video.py
.venv\Scripts\python estudio	estes	estar_ao_vivo.py
node estudio/testes/e2e_agentes_ao_vivo.mjs
```

Rode **uma bateria por vez**: em paralelo elas disputam CPU, memória e disco e geram falhas falsas. Para rodar duas ao mesmo tempo mesmo assim, dê uma porta própria a cada uma com a variável `E2E_PORTA` (PowerShell: `$env:E2E_PORTA=18891; node estudio/testes/e2e_interface.mjs`). Sem ela, cada bateria usa a sua porta padrão (interface 8799, corte 8798, estilos 8797, celular 8801).

- `testar_estilos.py`: mede nos quadros cada movimento dos estilos novos, contra a mesma cena sem ele, e compara os projetos antigos com a referência em `referencia_sketch.json`.
- `e2e_motor.mjs` (PROG-006): o selo do motor (Claude/Codex) e a nota na lista de agentes, no diálogo de execução e nas faixas da revisão, com job antigo, nota vazia, motor desconhecido e toque no celular. Uso: `node estudio/testes/e2e_motor.mjs [pasta para capturas]` (`E2E_PORTA` muda a porta). Esperado: 29 verificações ok.
- `e2e_celular.mjs`: o acesso pela rede, com senha, recusas e bloqueio, e cada tela num Chrome com tamanho e toque de celular, chamando pelo IP do computador na rede.
- `e2e_estilos.mjs`: estilos e temas na interface, do novo projeto ao MP4 exportado, troca de estilo e reabertura. Desenho e export são reais; agentes e narração são simulados.
- `e2e_corte.mjs`: as demonstrações de aceite do Corte. Editor, compositor, ffmpeg e a comparação com a prévia são reais; agentes e narração são simulados.
- `e2e_interface.mjs`: Chrome real clicando na interface, em uma cópia descartável de produções reais; agentes e comandos pesados são simulados (`claude_simulado.py`, `comandos_simulados.py`).
- `validar_real.py`: Chatterbox, `run.py` e `run.py --mock` de verdade, sem agentes, em pastas próprias de `output/` apagadas no final. Leva alguns minutos de CPU.

## Cronograma de postagem (PROG-011, só leitura)
`GET /api/cronograma` (módulo `estudio/cronograma.py`) sugere data e hora para cada vídeo da fila, na ordem de `output/fila_postagem.txt`, com o status do PROG-012, o alerta (menos de 2 dias e vídeo não pronto) e o topo "Pronto para postar" / "Sem vídeo pronto para DD/MM, falta: ...". A cadência vem da seção `cronograma` de `config_shorts.yaml` (sem ela: 1 vídeo por dia). Não grava nada, não agenda e não publica. Teste: `.venv\Scripts\python estudio\testes\testar_cronograma.py`. A tela ainda não existe (depende do desenho do Iniesta).
