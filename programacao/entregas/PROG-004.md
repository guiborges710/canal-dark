# Entrega PROG-004 · Validar a reserva com Codex (Rodrygo, 2026-11-04)

Pronto para **Alisson** e revisão do **Thiago Silva**. Nada commitado, sem gasto de API paga.

## Escopo

Decisão D-005 (`tecnico/decisoes.md`): a reserva fica mantida, aciona só no limite de uso do Claude, uma tentativa por trabalho, e todo trabalho novo tenta o Claude primeiro.

## Devoluções do Thiago Silva

1. **Isolamento falso.** `ESTUDIO_DADOS` era `setdefault` (herdava o do ambiente) e o caso `--real` não passava `cwd`, então o Codex rodava na raiz do repositório. Agora o teste força uma pasta de dados temporária e o `--real` passa `cwd` temporário.
2. **Critérios 2 e 3 sem integração real.** Novo bloco que roda `executor.rodar` de verdade, com um `claude` e um `codex` falsos (`.cmd`, offline, sem credencial): Claude no limite termina com `motor=codex` e `motor_nota`; o Codex roda na pasta do job (`cwd` e `-C`); Claude disponível usa Claude e o Codex não é chamado; um job seguinte volta a tentar o Claude. Também passa pelo `trabalhos.rodada` e `fluxo.status_job_publico`, confirmando que `motor` e `motor_nota` chegam ao estado que a tela lê.
3. **Login inválido não testado.** Teste com `CODEX_HOME` sem `auth.json` (o `logado()` real, sem monkeypatch): a reserva não executa e a mensagem manda rodar `codex login`. Falha da própria reserva (Codex sai com erro) também testada: erro legível, motor volta a claude.
4. **README corrompido.** Linha de teste da seção "Reserva com Codex" em `estudio/README.md` tinha tabulações no lugar de `\t`; corrigida.
5. **Timer não cancelado.** Bug real em `estudio/executor.py`: exceção durante a leitura da saída deixava o `threading.Timer` (45 min) vivo, e o processo do executor não saía. Reproduzido primeiro pelo teste (falha "vivos: 1" e o processo ficou preso até o timeout), depois corrigido com `try/finally` (cancela o timer e mata o processo filho) nos dois pontos, o do Claude e o do Codex.

## Arquivos

- `estudio/executor.py`: `try/finally` do timer em `rodar` e `_tentar_codex`.
- `estudio/testes/testar_reserva_codex.py`: isolamento, integração com Claude/Codex falsos, login ausente, falha da reserva, estado público do job, timer.
- `estudio/README.md`: linha corrigida e descrição do teste.

## Comandos e resultado real

- Vermelho: `testar_reserva_codex.py` -> "FALHA timer do Codex é cancelado mesmo com exceção (vivos: 1)", processo preso (timeout 124).
- Verde: `.venv\Scripts\python.exe -X utf8 estudio\testes\testar_reserva_codex.py` -> **Tudo certo**, 50 ok (exit 0).
- Regressão: `e2e_interface` 133, `e2e_celular` 63, `e2e_corte` 152, `e2e_estilos` 98, `testar_estilos` 103, todas com 0 falhas (uma por vez).
- `--real`: o Codex está sem cota de uso no momento (a conta devolveu "You've hit your usage limit ... try again at 3:14 PM"). Por isso o caso real **não repetiu o sucesso** desta vez (2 falhas, causa externa). O sucesso real já havia sido registrado antes (ver histórico desta entrega: `motor=codex`, nota "Executado pelo Codex"), mas essa rodada foi feita com `cwd` na raiz; **falta repetir o `--real` com o `cwd` temporário quando a cota voltar.** O caminho de falha da reserva foi exercitado de verdade e o erro apareceu legível, sem derrubar nada.

## Pendente

- Repetir `testar_reserva_codex.py --real` quando a cota do Codex voltar (critério 2 com o Codex de verdade e `cwd` isolado).
- Validação do **Alisson** (critérios 2 a 5; critério 1 já registrado em D-005) e revisão do **Thiago Silva**.
