# Revisão PROG-004 · Reserva com Codex (Thiago Silva, 2026-11-04)

**Veredito técnico: APROVADO.** O aceite final fica **bloqueado pela confirmação do Guilherme sobre D-005** (critério 1 exige confirmação por escrito).

Método: leitura do código atual (sem shell nesta sessão, então sem `git diff`).

## O que li
- `estudio/reserva.py` (inteiro), `estudio/executor.py` 95-220, `tools/sincronizar_codex.py` 20-134, `estudio/testes/testar_reserva_codex.py` 1-30 e 120-194.

## Pontos aprovados
- `e_limite_do_claude` é restrito a mensagens de limite de uso; os casos de timeout, custo, 429 e erro de conteúdo são negativos nos testes.
- Uma tentativa por trabalho; falha do Codex não volta ao Claude e preserva o erro original com nota (executor 211-219).
- O `try/finally` do timer, nos dois pontos (122-125 e 199-202), é correção real de um bug real, reproduzido antes pelo teste.
- O teste força `ESTUDIO_DADOS` temporário antes do import (linha 14), roda `executor.rodar` de verdade com Claude e Codex falsos, e passa pelo `trabalhos.rodada` e `fluxo.status_job_publico`. Login ausente usa o `logado()` real.
- `sincronizar_codex.py` é local, sem rede, sem apagar (só informa órfãos), grava bytes com LF. Ok.

## D-005
Já existe em `programacao/tecnico/decisoes.md`, redigida a partir do que está escrito no `CLAUDE.md` (decisão do dono de 2026-11-03: Codex só como reserva do limite do Claude) e em `estudio/README.md`. Eu **não inventei** decisão nova. Falta apenas o Guilherme confirmar por escrito (resposta no chat ou assinatura na linha da decisão).

**Atenção ao Guilherme:** a memória do assistente ainda traz "Só Claude, nunca Codex — não manter nem atualizar arquivos de Codex". Isso conflita com o `CLAUDE.md` mais recente (reserva mantida). Preciso que ele diga qual vale. Se a regra "só Claude" voltar, o PROG-004 vira remoção da reserva (critério 6) e o D-005 muda.

## Riscos (não bloqueiam; registrar na decisão)
1. Em produção, sem `cwd` no spec, o Codex roda com `workspace-write` em `RAIZ`. O docstring de `reserva.py` diz "escreve só dentro da pasta de trabalho", mas essa pasta é a raiz do repositório de dados. O mesmo alcance que o agente do Claude já tem, então não piora; mas o texto do docstring e de D-005 deve dizer isso com clareza. Alternativa: **Rodrygo** passar `cwd` da pasta `output/<slug>` nos jobs que só escrevem lá.
2. `-c windows.sandbox="elevated"` nunca foi provado com o Codex real (sem cota). O `--real` continua pendente.
3. A mensagem de limite depende de padrões de texto do Claude Code. Se o texto mudar, a reserva deixa de acionar em silêncio (falha segura, mas sem aviso). Os padrões estão em `_LIMITE`; sugiro revisão a cada atualização do Claude Code.

## Pendências
- **Guilherme:** confirmar D-005 por escrito e dizer se a regra "só Claude" da memória ainda vale.
- **Alisson:** o relatório `qa/PROG-004.md` ainda diz DEVOLVIDO (critério 1); atualizar depois da confirmação. Quadro e QA hoje divergem.
- **Rodrygo:** repetir `testar_reserva_codex.py --real` com `cwd` temporário quando houver cota (critério 2 real).
