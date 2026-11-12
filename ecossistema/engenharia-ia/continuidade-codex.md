# Continuidade em Codex (2026-11-03)

Autor: **Valverde**. Verificado com `python tools/sincronizar_codex.py --verificar` e leitura de `estudio/README.md` (seção "Reserva com Codex").

## Estado do espelho
- `.claude/agents/`: 40 definições. `.codex/agents/`: 40 `.toml` (mais `closetminimal-tiktok.toml`, órfão, sem agente no Claude; o script não mexe nele).
- Em dia: 38. **Defasados: 4** — `debruyne-orquestrador`, `mbappe-editor-metadados`, `vini-auditor-conformidade` e `valverde-engenheiro-ia`.
- Não atualizei: o espelho fica fora da minha pasta de escrita. Quem roda é o dono do espelho (**Luiz Henrique** ou **Rodrygo**), com um comando só:
  `python tools/sincronizar_codex.py` (depois `--verificar` deve dizer "42 em dia" sem DEFASADO).
- Faça isso depois de qualquer corte aprovado em `economia-para-codex.md`, para o Codex herdar a versão enxuta.

## Como o fallback funciona (o que existe de fato)
1. **Automático, só no Corte.** Quando um trabalho de agente do Corte falha com o texto de limite do Claude (`reserva.e_limite_do_claude`), `estudio/reserva.py` refaz o trabalho uma vez com `codex exec` (sandbox `workspace-write`, sem rede, sem aprovação, sem sessão salva). Instruções vêm de `.claude/agents/<id>.md`, o pedido e a pasta são os mesmos. O próximo trabalho tenta o Claude primeiro.
2. **Não é automático na conversa do Claude Code.** Esta sessão não migra sozinha. Para continuar no terminal: abrir o Codex na pasta `canal-dark` e chamar o agente de `.codex/agents/`.
3. Pré-requisitos do Codex: instalado, `codex login` feito, achável por `ESTUDIO_CODEX`/`CODEX`, PATH ou extensão `openai.chatgpt-*`. `CODEX_MODELO` no `.env` é opcional.

## O que NÃO foi possível garantir
- **"O Codex lê o contexto desta sessão" é falso.** Não existe passagem de histórico de conversa entre Claude e Codex. O que o Codex enxerga é o disco: `.codex/agents`, `AGENTS.md` se existir, `output/<slug>/`, `ecossistema/`, `programacao/`. Não testei uma execução real do Codex (sem ação externa, e o login é do Guilherme).
- Teste que dá para rodar sem tocar em nada real: `.venv\Scripts\python estudio\testes\testar_reserva_codex.py`.

## Como tornar a troca sem perda (a única coisa que importa)
Tudo o que o Codex precisa saber tem de estar em arquivo. Checklist antes do limite acabar:
1. Rodar a sincronização acima.
2. Cada trabalho em andamento grava o estado em disco: slug, etapa feita, próxima etapa (`output/<slug>/` já faz isso por ser idempotente).
3. Decisões desta sessão que valem para o Codex vão para `CLAUDE.md` ou `ecossistema/README.md` (arquivos do dono; **Luiz Henrique** aplica).
4. Regras invioláveis (congelamento do roteiro e do vídeo, políticas do YouTube, ação externa só com confirmação) já estão nas definições espelhadas. Conferir que o `.toml` do **Vini** e do **Courtois** as contém depois da sincronização.
5. Ao abrir o Codex: pedir "leia `ecossistema/engenharia-ia/continuidade-codex.md` e `CLAUDE.md`, depois chame o agente X".

## Risco aberto
O `CLAUDE.md` (19 KB) não é lido pelo Codex como o Claude Code lê; o equivalente é `AGENTS.md`. Confirmar com **Luiz Henrique** se existe e está em dia (a memória do projeto manda não editá-lo à mão fora da sincronização).
