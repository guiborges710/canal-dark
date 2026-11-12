# Proposta de estrutura · PROG-013 (aprendiz) e PROG-014 (referências)

Autor: **Luiz Henrique**. Data: 2026-11-03. Estado: EXECUTADA em 2026-11-05, com duas mudanças do Guilherme: vídeos só por arquivo que ele subir (sem download automático) e nada agendado. Valem `inteligencia/aprendiz/README.md` e os critérios do backlog; o texto abaixo é o registro da proposta. Critérios de aceite completos em `programacao/backlog.md`.

## Onde ficam
Dentro do setor de inteligência (`inteligencia/`), chefiado por **De Bruyne**. Motivo: os dois só estudam e relatam, como o resto do setor, e os consumidores (**Raniele**, **Vitinho**, **Fagner**, **André Carrillo**) já estão lá. Setor novo seria cerimônia demais para dois agentes.

## Agentes propostos (nomes sujeitos à confirmação)
| Craque sugerido | id técnico | Função |
|---|---|---|
| **Busquets** | `busquets-aprendiz-canais-dark` | PROG-013. Assiste 1 a 3 vídeos por rodada, 3 rodadas por dia; relata método com evidência. |
| **Xabi Alonso** | `xabi-alonso-curador-referencias` | PROG-014. Curadoria de referências para estudo, nicho aberto e nosso. |

Nomes conferidos contra o mapa: nenhum repete. Tools mínimas: leitura, escrita na própria pasta, busca web e Bash só para ffmpeg e ferramentas aprovadas. `model: sonnet`.

## Pastas
- `inteligencia/referencias_estudo/AAAA-MM-DD.md`: lista do curador (até 10, em duas partes: nicho aberto e nosso; ordem de estudo; fonte de cada item).
- `inteligencia/aprendiz/AAAA-MM-DD/rodada-N.md`: relatório por rodada, com nível de acesso por vídeo, quadros analisados, métodos, "como aplicar ao Contexto Explica" e o que NÃO foi visto.
- `inteligencia/aprendiz/fila.md`: fila de vídeos que o curador passa ao aprendiz.
- `inteligencia/aprendiz/_entrada/`: onde o Guilherme coloca vídeo baixado quando o acesso falhar (adicionar ao `.gitignore`, junto com quadros e vídeos locais).

## Fluxo
1. **Xabi Alonso** (1x por dia, leve) usa o catálogo do **Hugo Souza** e o `referencias_virais.md` do **Memphis** como fontes, mais busca própria. Grava a lista e alimenta `fila.md`. Não repete o que já está nos relatórios do aprendiz.
2. **Busquets** (3x por dia) pega até 3 itens da fila, tenta assistir (quadros por ffmpeg e fala por legenda ou transcrição) e grava o relatório. Se não acessar, marca "não assistido" e pede o arquivo ao Guilherme, dizendo a pasta.
3. **Raniele** consolida padrões de produção; **Vitinho** inclui o relatório no consolidado; **Fagner** e **André Carrillo** recebem achados de título e thumbnail.
4. Avisos ao Guilherme só via **Ronaldo**.

## Decisão sobre o Memphis
O curador consome o trabalho do **Memphis** e não o absorve. O **Memphis** segue semanal, voltado a viralidade e postagem.

## Limites (valem para os dois)
Só estudam e relatam. Não publicam, não escrevem roteiro do canal, não guardam senha, token ou cookie. Sem raspagem em massa. Só canal dark, sem pessoa falando para a câmera. Citação de fala só curta, como evidência; nunca texto para reaproveitar.

## Agendamento (proposto, não criado)
Mecanismo do **Ronaldo** (`produtividade/`). Horários sugeridos do aprendiz: 09:00, 14:00 e 20:00. Curador: 08:00. Teto sugerido de gasto: a definir pelo Guilherme.

## Decisões que só o Guilherme pode tomar
1. Aprovar a estrutura (dentro de `inteligencia/`) e os nomes dos craques.
2. Ferramentas aceitáveis: yt-dlp para baixar, legenda automática do YouTube, Whisper local, ffmpeg. Baixar vídeo de terceiros só para estudo local é aceitável para ele?
3. Os 3 horários do aprendiz e a cadência do curador.
4. Teto de orçamento ou tokens por rodada e por dia.
5. Opcional: nichos abertos de interesse e canais que ele admira (só nomes e links).

## Suposições tomadas
- Os dois agentes entram juntos, com o aprendiz como núcleo.
- Pastas dentro de `inteligencia/`, não em pasta nova na raiz.
- O curador cobre qualquer nicho dark, mas só indica vídeos sem pessoa na câmera.
- Os critérios de aceite do backlog valem sem mudança. **Alisson** confere com 2 vídeos reais (um acessível e um inacessível).

## Para criar depois da confirmação
Os dois arquivos em `.claude/agents/`, as pastas acima com `README.md` e cabeçalhos, a linha no `inteligencia/README.md` e no mapa, o `.gitignore`, os lembretes pelo **Ronaldo** e `python tools/sincronizar_codex.py`.
