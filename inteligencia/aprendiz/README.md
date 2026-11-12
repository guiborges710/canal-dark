# Aprendiz de canais dark

Dois agentes do setor de inteligência, que estudam como os canais dark fazem seus vídeos. **Xabi Alonso** escolhe o que vale a pena estudar e **Busquets** estuda: olha os quadros, lê a fala e relata os métodos com evidência. Só estudam e relatam; não publicam nem escrevem roteiro.

## Como usar

1. **Pedir referências** (opcional): `.venv\Scripts\python inteligencia/aprendiz/rodar.py curador`. A lista sai em `inteligencia/referencias_estudo/` e os vídeos entram na `fila.md`.
2. **Baixar o vídeo** e salvar em `inteligencia/aprendiz/_entrada/`, com o `id` da fila como nome (`abc123.mp4`). Vídeo fora da fila também vale: é estudado com o link "não informado".
3. **Pedir o estudo:** `.venv\Scripts\python inteligencia/aprendiz/rodar.py aprendiz`. O relatório sai em `inteligencia/aprendiz/AAAA-MM-DD/rodada-N.md`.

Sem arquivo em `_entrada/`, a rodada grava o relatório dizendo o que falta e não chama o Claude (custo zero). Use `--simular` para ver o que faria.

## Decisões do Guilherme (2026-11-05)

- **Vídeos só por arquivo que ele subir.** Nenhum agente baixa vídeo, áudio ou legenda da internet.
- **Nada agendado.** Os dois só rodam quando alguém chama, para não gastar o limite do Claude sem pedido.
- Estrutura e nomes da proposta aprovados (`ecossistema/proposta-prog-013-014.md`).

## Limites de gasto

Valores equivalentes informados pelo Claude Code, definidos em `rodar.py`. São os sugeridos na proposta e não foram confirmados pelo Guilherme como teto final.

| Execução | Teto |
|---|---|
| **Busquets**, por rodada (até 3 vídeos) | US$ 0,30 |
| **Xabi Alonso**, por entrega (até 10 referências) | US$ 0,20 |
| Os dois, por dia | US$ 1,10 |

Ao atingir o teto, a execução para e diz isso no relatório. Cada execução fica registrada em `historico.jsonl`.

## Arquivos

| Caminho | O que é | Quem escreve | No git? |
|---|---|---|---|
| `fila.md` | Vídeos para estudar | **Xabi Alonso** (ou o Guilherme à mão) | sim |
| `estudados.md` | Vídeos já estudados, para não repetir | `rodar.py` | sim |
| `AAAA-MM-DD/rodada-N.md` | Relatório da rodada | **Busquets** (`rodar.py`, se a rodada falhar ou não tiver vídeo) | sim |
| `historico.jsonl` | Registro de execuções e custo | `rodar.py` | sim |
| `_entrada/` | Vídeos que o Guilherme sobe | Guilherme | não |
| `_trabalho/<id>/` | Quadros, fala e manifesto de cada vídeo | `preparar_video.py` | não |
| `../referencias_estudo/AAAA-MM-DD.md` | Lista curada | **Xabi Alonso** | sim |

## Como o vídeo é preparado

`preparar_video.py` roda antes do agente, sem gastar token: até 12 quadros (gancho, viradas por corte de cena, intervalos e final), contagem de cortes e fala por Whisper local. Em vídeo longo, cortes e fala cobrem só os 10 primeiros minutos, e o manifesto avisa. Os arquivos ficam em `_entrada/` depois do estudo: podem ser apagados à mão, e o vídeo não é estudado de novo porque está em `estudados.md`.

## Teste

`.venv\Scripts\python -X utf8 estudio/testes/testar_aprendiz.py` (não chama o Claude).
