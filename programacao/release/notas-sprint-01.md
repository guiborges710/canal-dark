# Notas da Sprint 01 · RASCUNHO

Dono: **Marquinhos**. Sprint 01: 03/11 a 17/11/2026. Rascunho de 2026-11-03 (noite); só o que o quadro (`programacao/quadro.md`) mostra. Nada commitado.

Meta: validar PROG-001, PROG-002 e PROG-004, confiabilizar a bateria (PROG-005) e entregar aba Agentes "Ao vivo" (PROG-003+006), status automático (PROG-012) e cronograma (PROG-011).

## Itens aceitos (Feito)
| Id | Item | Quem | Evidência |
|---|---|---|---|
| PROG-010 | Instalador `.bat` que nunca sobrescreve (`/simular`) | **Endrick** / **Marquinhos**; QA **Alisson**; aceite **Zico** | `programacao/qa/PROG-010.md`, `entregas/PROG-010*.md`, `programacao/qa/testar_instalar_agentes.py` |
| PROG-006 | Aba Agentes, fatia A: motor e nota na tela (componente único `seloMotor`) | **Endrick**; desenho **Iniesta**; revisão **Thiago Silva**; QA **Alisson**; aceite do Guilherme (05/11) | `revisoes/PROG-006.md`, `qa/PROG-006.md`, `entregas/PROG-006.md`; reexecutado por **Marquinhos** em 05/11: `e2e_motor.mjs` 29 ok, 0 falhas |

## Em andamento / em teste (ainda não entram)
- Em teste: PROG-001, PROG-002 (falta **Alisson** e Guilherme).
- Fazendo: PROG-004, PROG-005 (**Rodrygo** + **Alisson**); PROG-015 (Codex, a pedido do Guilherme).
- Na fila: PROG-012, PROG-011, PROG-003+006.

## Arquivos tocados (a preencher por item; hoje só a árvore geral)
Código em `estudio/` (Corte: servidor, executor, fluxo, reserva, web), `media/`, `render/corte_compor.mjs` e `run.py` está modificado ou novo, sem separação por item. Para cada item aceito, copiar a lista do relatório em `programacao/entregas/<id>.md`. Pendente: pedir aos devs o mapa arquivo-por-item antes do commit.

## Testes rodados
Pendente. Registrar aqui o resultado real de cada bateria (`testar_estilos`, `testar_roteiro`, `testar_reserva_codex`, `comandos_simulados`, e2e) quando o **Alisson** rodar, depois de pausar a ContextoExplica-Trello. PROG-010: ver `qa/PROG-010.md`.

## Riscos
- Árvore git suja e com muita coisa só em stage: risco de commit misturar itens.
- Tarefa ContextoExplica-Trello ativa durante baterias.
- Sem histórico de velocidade (primeira sprint); aceite do Guilherme é o gargalo (06/11 e 14/11).
- Pixel Agents depende do VS Code aberto (ver `ambiente.md`).

## Como desfazer
Nada commitado; o `.bat` de PROG-010 não sobrescreve. Depois do commit: `git revert <hash>` do commit do item. Antes dele, arquivos novos (`??`) se removem apagando-os e os modificados com `git restore <arquivo>`, só com o Guilherme pedindo (há trabalho não commitado que se perderia).

## Lista para commit e mensagem sugerida
Ainda não definida: nenhum item além de PROG-010 está aceito. Sugestão provisória após aceite: `Sprint 01: PROG-010 instalador de agentes sem sobrescrita (modo /simular)` com a atribuição padrão. Quem commita é o Guilherme.

## PROG-006 · registro de release (Marquinhos, 2026-11-05)
- Arquivos tocados (só front; back-end intocado): `estudio/web/corte_nav.js` (`seloMotor`), `estudio/web/corte_estudio.js`, `estudio/web/app.js`, `estudio/web/corte.css` (bloco no fim), `estudio/README.md` (linha da bateria). Teste novo: `estudio/testes/e2e_motor.mjs`.
- Testes: `e2e_motor.mjs` 29 ok/0 falhas (reexecutado por mim); QA: `e2e_interface` 150 ok, `e2e_celular` 63 ok. `e2e_corte` 152 ok só na entrega original, não repetido após o ajuste de texto.
- Riscos: testes injetam o job na página (contrato real do back coberto por `testar_reserva_codex.py`, não rodado de novo); `corte.css`, `corte_nav.js` e `corte_estudio.js` estão como não rastreados (`??`), então o commit deve incluí-los junto dos demais itens; Codex segue como valor possível até o PROG-004.
- Como desfazer: antes do commit, reverter o bloco `seloMotor` e o CSS `.selo-motor/.chip-motor/.motor-dica` (só com o Guilherme pedindo); depois do commit, `git revert` do commit.

## PROG-013 e PROG-014 · registro de release (Marquinhos, 2026-11-09)
Aceitos pelo Guilherme em 09/11 10:16. Feitos pelo Claude Code a pedido dele (05/11); QA **Alisson** e revisão **Thiago Silva** APROVADOS.
- Arquivos tocados: `.claude/agents/busquets-aprendiz-canais-dark.md`, `.claude/agents/xabi-alonso-curador-referencias.md`; `inteligencia/aprendiz/` (`rodar.py`, `preparar_video.py`, `README.md`, `fila.md`, `estudados.md`, `historico.jsonl`, `_entrada/LEIA-ME.txt`); `inteligencia/referencias_estudo/2026-11-05.md` e `2026-11-05-2.md`; relatório `inteligencia/aprendiz/2026-11-05/rodada-1.md`; `estudio/testes/testar_aprendiz.py`; `.gitignore`, `inteligencia/README.md`, `ecossistema/README.md`, espelho `.codex/`.
- Testes: `.venv/Scripts/python.exe -X utf8 estudio/testes/testar_aprendiz.py` reexecutado por mim em 09/11: **50/50** (não chama o Claude, custo zero).
- Riscos: nenhum vídeo de terceiro estudado de fato; teto de custo provado só em simulação; Whisper erra palavras; links do curador não abertos para confirmar que estão no ar; vídeos longos na fila (até 19 min). `_entrada/` e `_trabalho/` ficam fora do git (conferido). Árvore suja: não misturar com outros itens no commit.
- Como desfazer: antes do commit, apagar os arquivos novos listados (só com o Guilherme pedindo); depois, `git revert` do commit. Nenhum agendamento criado, nada a desligar.

## PROG-016 · registro de release (Marquinhos, 2026-11-09)
Aceito pelo Guilherme em 09/11 ("016 aceito"). QA **Alisson** 9/9 critérios; revisão **Thiago Silva** APROVADA.
- O que entrou: aba Agentes > Catálogo mostra o estado de cada agente (ocioso, trabalhando, na fila, falhou, espera você), com ícone e texto, atualizando no polling já existente; "Verificando" antes da 1ª resposta; aviso "(desatualizado)" se a consulta falhar; celular 390 px.
- Arquivos tocados (só front; servidor e `ao_vivo.py` intocados): `estudio/web/corte_agentes.js`, `corte_nav.js`, `corte.css`, `celular.css`; teste novo `estudio/testes/e2e_agentes_catalogo.mjs`.
- Testes reexecutados por mim em 09/11, um por vez: `E2E_PORTA=8803 node estudio/testes/e2e_agentes_catalogo.mjs` → 47 ok, 0 falhas; `.venv/Scripts/python.exe -X utf8 estudio/testes/testar_ao_vivo.py` → 49 ok, 0 falhas (50 jobs: rota em 40 ms, limite 1 s do critério). Regressões (`e2e_agentes_ao_vivo` 91, `e2e_celular` 64, `e2e_interface` 150) vêm do QA do **Alisson**; não repeti.
- Riscos: os quatro arquivos web estão como não rastreados (`??`) e devem ir no mesmo commit dos demais itens da tela Agentes; falta o caso "agente ausente = ocioso" em `testar_ao_vivo.py` (dívida pequena do **Rodrygo**, coberta pelo e2e); o e2e foi escrito junto com o código, mas o **Thiago Silva** conferiu que as asserções não são frouxas.
- Como desfazer: antes do commit, reverter só os blocos do Catálogo nos quatro arquivos web e apagar o e2e novo (só com o Guilherme pedindo); depois do commit, `git revert`.
