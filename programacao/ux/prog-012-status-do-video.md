# UX · PROG-012 · Status automático de cada vídeo

Autor: **Iniesta** · 2026-11-03 (noite) · Sprint 01. Proposta de desenho, não código. Cartão: [PROG-012] no quadro da Sprint 01.

## Objetivo da tela
Responder, sem o Guilherme abrir pasta nenhuma: "em que pé está cada vídeo?" e "tem vídeo pronto para a próxima postagem?". Só leitura: nada aqui publica, move arquivo ou muda `fila_postagem.txt` (critério 7).

## Onde fica
Dentro de **Projetos** (lista que já existe), sem aba nova:
1. Cada projeto ganha um **selo de status** (um só) ao lado do nome.
2. Acima da lista, uma **faixa "Próxima postagem"** (resposta do critério 6).
3. Filtro por status ("Todos", e um por status) acima da lista.
Dúvida de local para o **Zico**/**Thiago Silva**: se preferirem uma visão própria (`/status`), os textos abaixo valem iguais.

## Os 7 status (exatamente um por vídeo)
Sempre ícone + palavra. A cor é reforço. Ordem = ordem natural da vida do vídeo.

| # | Texto do selo | Ícone | Cor | Regra (dados) | Linha de apoio (cinza, sob o nome) |
|---|---|---|---|---|---|
| 1 | Sem roteiro | ○ | cinza | sem `roteiro.txt` | "Falta o roteiro. Próximo passo: o Neymar escrever." |
| 2 | Em produção | ◐ | azul | tem `roteiro.txt`, sem `video.mp4` | "Etapa: <etapa do Corte>" (ou "Parado: aguarda você" em âmbar) |
| 3 | Vídeo pronto | ▶ | azul claro | tem `video.mp4`, sem auditoria APROVADA | ver abaixo (3 variantes) |
| 4 | Auditado | ✓ | verde | `auditoria.md` APROVADA | "Aprovado pelo Vini. Falta entrar na fila de postagem." |
| 5 | Na fila de postagem | ⏳ | verde | está em `fila_postagem.txt`, ainda não publicado | "Posição 2 na fila." |
| 6 | Publicado (privado) | ◉ | roxo | há registro de publicação | "Enviado em 03/11 como privado. Falta torná-lo público no YouTube Studio." |
| 7 | Público | ● | verde forte | confirmado pela fonte ou marcado pelo Guilherme | "Público desde 05/11." |

Linha de apoio do status 3 (diz por que não avançou):
- sem auditoria: "Falta a auditoria final do Vini."
- auditoria REPROVADA: "O Vini reprovou a auditoria. Só os metadados (título, descrição, tags, miniatura) podem mudar; veja o parecer." + botão "Ver parecer".
- auditoria ausente por erro de leitura: "Não consegui ler a auditoria." (cai em aviso, ver Contraditório).

## Contraditório (critério 5): aviso, não status falso
Quando os dados se contradizem, o selo vira `⚠ Verificar` (âmbar) e o status provável aparece em cinza. Exemplos exatos:
| Caso | Texto |
|---|---|
| Na fila sem `video.mp4` | "⚠ Verificar: está na fila de postagem, mas não existe o vídeo (`video.mp4`). Nada será postado até o vídeo existir." |
| Na fila sem pasta em `output/` | "⚠ Verificar: o nome está na fila, mas a pasta do vídeo não existe. Confira o nome em `fila_postagem.txt`." |
| Publicado sem `video.mp4` | "⚠ Verificar: há registro de publicação, mas o arquivo do vídeo sumiu. O vídeo no YouTube não foi afetado." |
| Auditado sem `video.mp4` | "⚠ Verificar: a auditoria está aprovada, mas falta o vídeo." |
| Publicado, mas não está mais na fila e sem registro | sem aviso (é o caso normal depois de postar) |
Cada aviso tem a ação "Ver detalhes" que abre o projeto. Nunca some em silêncio.

## "Público" e o Studio manual (critério 4)
- Sem confirmação, o vídeo fica em **Publicado (privado)**, com a frase de apoio acima. O sistema não chuta "Público".
- Botão discreto na linha: **"Marquei como público no Studio"**. Ao clicar: diálogo "Confirma? Isso só muda o status aqui no Corte. Não altera nada no YouTube." [Confirmar] [Cancelar]. Depois: selo vira Público e aparece "Marcado por você em 05/11" com link "Desfazer".
- Atenção para o **Zico**/**Thiago Silva**: isso é a única escrita do Guilherme; o critério 7 diz que a visão não altera `fila_postagem.txt`, e uma marcação manual é um arquivo à parte (ex.: `publicacao.json`). Confirmar que é aceitável.

## Faixa "Próxima postagem" (critério 6)
Fica acima da lista, uma frase grande e um detalhe.
- Há vídeo pronto: `✓ Há vídeo pronto para a próxima postagem: SIM` / detalhe: "<título ou slug> · auditado · 1º da fila."
- Não há: `✕ Há vídeo pronto para a próxima postagem: NÃO` / detalhe com o que falta, no mais adiantado: "O mais adiantado é <slug>: falta a auditoria final do Vini." Se nenhum existe: "Nenhum vídeo passou da etapa de roteiro."
- Fila vazia mas com vídeo auditado: `Há vídeo auditado, mas a fila de postagem está vazia.` / "Para postar, coloque <slug> em `output/fila_postagem.txt` (o Corte não mexe nesse arquivo)."
- Definição para o **Zico** confirmar: "pronto" = status Auditado ou Na fila de postagem, com `video.mp4` existente.
Esta faixa **não** tem datas de calendário (isso é o PROG-011); a frase é a mesma que o PROG-011 vai reutilizar.

## Lista (layout)
Computador: linhas, uma por vídeo.
```
+--------------------------------------------------------------+
| Próxima postagem                                             |
| ✓ Há vídeo pronto para a próxima postagem: SIM               |
| krakatoa-geracoes · auditado · 1º da fila                    |
+--------------------------------------------------------------+
| Status: [Todos v]  Mostrando 12 de 12 vídeos                 |
|                                                              |
| geracao-z-trabalho      ⏳ Na fila de postagem    posição 1   |
| boomer-vs-millennial    ✓ Auditado                           |
| sem-filhos-por-escolha  ◐ Em produção  Etapa: Cenas          |
| casa-propria            ⚠ Verificar  na fila, mas sem vídeo  |
+--------------------------------------------------------------+
```
Ordem padrão: Verificar primeiro, depois do mais adiantado (Na fila, Auditado, Vídeo pronto) ao menos adiantado, Publicados por último. Dentro do mesmo status, mais recente primeiro.

Celular (até 820 px): faixa "Próxima postagem" fixa no topo, cartões empilhados, selo na linha de cima, linha de apoio embaixo podendo quebrar; filtro como lista suspensa de largura total; áreas de toque de 44 px.

## Atualização sozinha (critério 2)
- Atualiza no mesmo ritmo do Corte (2 a 4 s) só quando o status muda; sem recarregar a página.
- Quando um status muda diante dos olhos do Guilherme, a linha pisca um destaque de 2 s e o texto de região `aria-live="polite"` anuncia: "geracao-z-trabalho agora está em Auditado."
- Rótulo do rodapé: "Atualizado agora" / "há 20 s". Se a consulta falhar: faixa âmbar "Sem atualização desde 14:32. Mostrando o último estado conhecido." + "Tentar agora" (mesmo padrão do PROG-003).

## Estados da tela
| Situação | O que aparece |
|---|---|
| Carregando | Linhas-esqueleto + "Lendo o estado dos vídeos…" |
| Nenhum vídeo | "Ainda não há vídeos no Corte." + botão "Criar projeto" |
| Filtro sem resultado | "Nenhum vídeo com o status 'Auditado'." + link "Mostrar todos" |
| Consulta falhou | Faixa âmbar acima; lista mantida |
| Pasta ilegível/corrompida | Linha com `⚠ Verificar: não consegui ler esta pasta (<nome>). Abra o projeto para ver o que houve.` |
| Muitos vídeos (50+) | Lista em páginas de 25 com "Mostrar mais"; faixa e filtros sempre visíveis |
| `fila_postagem.txt` ausente | Tratar como fila vazia, sem erro; nota cinza "Não há fila de postagem criada." |

## Retorno de cada controle (heurística: todo botão responde)
- Filtro: atualiza a lista na hora e o contador ("Mostrando 3 de 12").
- "Ver detalhes"/"Ver parecer": abre o projeto; durante o carregamento o botão fica "Abrindo…".
- "Marquei como público no Studio": ver diálogo acima; após confirmar o botão fica "Salvando…" e depois vira o selo Público; em erro: "Não consegui salvar a marcação (<motivo>). O status continua Publicado (privado). Tente de novo."

## Acessibilidade
Cada linha tem `aria-label` completo: "geracao-z-trabalho, status Na fila de postagem, posição 1." Selo sempre com palavra; foco visível; selo de `Verificar` com texto, não só cor.

## Dúvidas para o Zico / Guilherme
1. Local: dentro de Projetos (recomendado) ou visão própria?
2. Definição de "pronto para postar": Auditado ou Na fila, com `video.mp4` presente?
3. A marcação "Público" manual pode gravar um arquivo próprio do Corte (ex.: `publicacao.json`)? Onde fica o "registro de publicação" que o critério 2 cita? Preciso saber para o texto "Enviado em <data>".
4. Vídeo reprovado na auditoria: o critério 3 o mantém em "Vídeo pronto". Concordo, mas a linha de apoio precisa dizer "reprovado" (feito acima). Confirmar.
5. Não existe status "reprovado" separado entre os 7; a reprovação aparece só na linha de apoio. Ok com isso?
