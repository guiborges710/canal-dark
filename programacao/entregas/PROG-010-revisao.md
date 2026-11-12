# Revisão técnica · PROG-010

Data: 2026-11-03  
Revisor: **Thiago Silva**  
Veredito: **APROVADO**

## Resultado

Não foram encontrados problemas bloqueantes. A implementação atende aos quatro critérios de aceite do backlog e pode seguir para **Em teste**, onde **Alisson** repete a validação formal.

## Revisão por arquivo

### `instalar_agentes.bat`

- Linhas 13-16: origem ausente ou sem `.md` encerra com código 1 antes de criar `.claude/agents`.
- Linhas 18-23: `/simular` não executa `mkdir`; portanto também não cria a árvore de destino.
- Linhas 25-44: cada destino existente entra somente no ramo de preservação. A única chamada de `copy` fica no ramo em que o arquivo não existia.
- Linha 36: `copy /-Y` acrescenta uma segunda proteção contra sobrescrita caso o destino passe a existir entre a verificação e a cópia. Não há mais `copy /Y` nem outro caminho de sobrescrita.
- Linhas 27-40: a saída distingue de forma explícita `INSTALARIA`, `PRESERVARIA`, `INSTALADO`, `PRESERVADO` e `NAO INSTALADO`.
- Linhas 7-11: `/simular` é aceito sem diferença de maiúsculas/minúsculas; argumento desconhecido encerra com código 2 e mostra o uso.

### `programacao/qa/testar_instalar_agentes.py`

- Linhas 39-46: o teste cria uma pasta temporária e copia o `.bat` para ela; o `cd /d "%~dp0"` do instalador faz com que toda origem e todo destino do teste fiquem dentro dessa caixa descartável.
- Linhas 48-52: comprova que origem vazia retorna código 1 sem criar `.claude`.
- Linhas 56-65: prepara arquivo novo e arquivo existente diferente e confirma que `/simular` não altera o snapshot binário do destino.
- Linhas 66-73: comprova que a simulação informa o que instalaria e o que preservaria.
- Linhas 75-81: comprova que o novo é instalado e o conteúdo local diferente é preservado.

O teste não lê nem escreve em `.claude/agents` do repositório. A inspeção do código e a execução confirmaram o isolamento.

## Critérios do backlog

1. **PASSOU** — um agente existente, seja mais novo ou apenas diferente, nunca chega à operação de cópia e recebe aviso explícito de preservação.
2. **PASSOU / não se aplica à sobrescrita** — a solução removeu a sobrescrita em vez de pedir confirmação ou criar backup. `copy /-Y` ainda protege a janela entre verificação e cópia.
3. **PASSOU** — o teste em pasta temporária comprova instalação de arquivo novo, preservação de arquivo existente diferente e ausência de escrita em `/simular`.
4. **PASSOU** — a decisão do Guilherme está registrada em `programacao/sprints/planning-2026-11-03.md`: manter e corrigir o `.bat` para nunca sobrescrever, com modo `/simular`.

## Evidências executadas

Comando específico:

```powershell
.venv\Scripts\python.exe programacao\qa\testar_instalar_agentes.py
```

Resultado: **PASSOU**, código 0.

```text
OK PROG-010: simulação sem escrita; novo instalado; existente preservado.
```

Prova adicional independente, também em `TemporaryDirectory`, com espaços no caminho:

- `/simular`: código 0, informou `INSTALARIA` e não criou `.claude`;
- primeira instalação: código 0;
- segunda instalação após editar localmente o arquivo: código 0, hash preservado e saída `PRESERVADO`;
- argumento `/desconhecido`: código 2 e nenhuma alteração no destino.

Qualidade do diff:

```powershell
git diff --check -- instalar_agentes.bat programacao/qa/testar_instalar_agentes.py programacao/entregas/PROG-010.md
```

Resultado: **PASSOU**. Houve apenas o aviso informativo do Git sobre futura conversão de LF para CRLF no `.bat`.

As baterias do Corte e do render não são relevantes para este item, pois ele não altera `estudio/`, `media/`, `render/` nem `run.py`.

## Riscos e observações não bloqueantes

- `instalar_agentes.bat:21` e `instalar_agentes.bat:36-49`: uma falha de criação de diretório ou de cópia é mostrada como `NAO INSTALADO`, mas não é acumulada no código de saída; ao final o processo pode retornar 0 e também imprimir `Instalacao concluida`. Isso não viola o escopo de proteção contra perda nem os critérios atuais, mas deve ser endurecido em item futuro se o instalador for consumido por automação.
- A preservação é intencionalmente incondicional: o instalador não atualiza nem compara um agente já existente. Essa é a decisão registrada para eliminar perda silenciosa.
- O teste é exclusivo de Windows por depender de `cmd.exe`, coerente com o artefato `.bat`.

## Handoff

Abordagem aprovada: instalação somente de arquivos inexistentes, preservação incondicional dos existentes e simulação sem escrita. Risco residual baixo, limitado principalmente ao código de saída em falhas operacionais. **Xavi** ou **Zico** pode mover o item para **Em teste**; em seguida, **Alisson** executa a bateria específica e registra o parecer formal. Nenhum ajuste de implementação é exigido de **Endrick** para o escopo atual.
