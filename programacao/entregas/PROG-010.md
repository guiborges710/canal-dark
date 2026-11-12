# Entrega · PROG-010

Data: 2026-11-03  
Responsáveis: **Endrick** / **Marquinhos**  
Status do handoff: pronto para revisão técnica e novo ciclo de QA após movimentação para **Em teste**.

## Escopo entregue

O instalador de agentes deixou de sobrescrever arquivos já presentes em `.claude/agents`.

- Arquivos existentes são sempre preservados e recebem aviso explícito no terminal.
- Somente agentes ainda inexistentes no destino são copiados.
- O argumento opcional `/simular` lista o que seria instalado ou preservado sem criar ou alterar arquivos e pastas.
- Origem ausente ou sem arquivos `.md` encerra com código 1 e mensagem legível, sem criar o destino.
- Argumento desconhecido encerra com código 2 e mostra a forma de uso.

## Arquivos alterados no item

- `instalar_agentes.bat`: valida argumentos e origem, implementa `/simular`, instala apenas arquivos novos e preserva todo destino existente.
- `programacao/qa/testar_instalar_agentes.py`: teste isolado em pasta temporária para simulação, instalação de arquivo novo, preservação de arquivo diferente e origem vazia.
- `programacao/entregas/PROG-010.md`: este registro de entrega.

## Testes executados

Comando:

```powershell
.venv\Scripts\python.exe programacao\qa\testar_instalar_agentes.py
```

Resultado em 2026-11-03: **PASSOU**.

```text
OK PROG-010: simulação sem escrita; novo instalado; existente preservado.
```

Verificação adicional:

```powershell
git diff --check -- instalar_agentes.bat programacao/qa/testar_instalar_agentes.py
```

Resultado: **PASSOU**, sem erro de whitespace. O Git exibiu apenas o aviso informativo de futura conversão de LF para CRLF em `instalar_agentes.bat`.

As baterias do Corte e do render não foram executadas porque o item altera somente o instalador e seu teste isolado; não modifica `estudio/`, `media/`, `render/` nem `run.py`.

## Limitações e riscos

- A preservação é incondicional: se houver uma versão nova na origem e o arquivo já existir no destino, o instalador não atualiza nem compara conteúdo; informa que o arquivo foi preservado.
- O instalador não cria backup porque não existe mais caminho de sobrescrita.
- O teste depende de Windows e `cmd.exe`, coerente com o formato `.bat`.
- O aviso LF/CRLF deve ser observado na preparação do commit para evitar alteração de fim de linha não intencional.
- O worktree contém muitas mudanças alheias; a revisão e o commit devem selecionar apenas os arquivos deste item.

## Handoff para revisão

1. **Thiago Silva**: revisar a lógica de não sobrescrita, os códigos de saída e a proteção do modo `/simular`.
2. **Xavi** ou **Zico**: mover o cartão de **Fazendo** para **Em teste** quando a revisão técnica estiver registrada.
3. **Alisson**: repetir a bateria específica e atualizar o veredito processual em `programacao/qa/PROG-010.md`. A validação técnica anterior já registrou os quatro critérios como atendidos.
4. **Zico**: realizar o aceite após revisão técnica e aprovação formal do QA.

Nenhum commit, push, publicação, instalação de dependência ou uso de API paga foi realizado nesta entrega.
