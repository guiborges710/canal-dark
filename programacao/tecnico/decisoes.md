# Decisões técnicas

Dono: **Thiago Silva** (`thiago-silva-tech-lead`). Formato: data, contexto, decisão, consequência.

## D-001 · 2026-11-03 · Regra única de status do vídeo (PROG-012)
**Contexto.** Cada vídeo precisa de exatamente um status derivado de arquivos reais, sem edição manual. Há dois registros de publicação (`upload.json`, de `media/youtube.py`, e `publicado.json`, de `postar_pendentes.py`), a fila nunca perde o vídeo já enviado e "público" não deixa rastro automático.

**Decisão.** Vale a primeira condição verdadeira, de cima para baixo. Implementação única em `estudio/status_video.py`; nenhum outro código recalcula status.

| # | Condição | Status (texto) |
|---|---|---|
| 1 | `upload.json` com `privacy == "public"`, ou `publico.json` existe | `publico` · Público |
| 2 | `upload.json` ou `publicado.json` existe (privacidade ausente conta como privado) | `publicado_privado` · Publicado (privado) |
| 3 | `video.mp4` ausente e `roteiro.txt` presente | `em_producao` · Em produção |
| 4 | `video.mp4` ausente e `roteiro.txt` ausente | `sem_roteiro` · Sem roteiro |
| 5 | `video.mp4` presente, auditoria APROVADA, `thumbnail.jpg` e `metadados.json` presentes, slug na fila | `na_fila` · Na fila de postagem |
| 6 | `video.mp4` presente e auditoria APROVADA | `auditado` · Auditado |
| 7 | `video.mp4` presente | `video_pronto` · Vídeo pronto |

- "Auditoria APROVADA" = `materiais.status_auditoria(texto) == "APROVADO"` (BLOQUEADO vence). Mesmo critério de `run.py publish` e `postar_pendentes.py`.
- Contradições nunca viram status falso: o status cai na linha que os arquivos sustentam e a lista `avisos` explica em português. Casos obrigatórios: na fila sem `video.mp4` (cai em 3 ou 4), na fila sem auditoria APROVADA (cai em 7), na fila com auditoria mas sem `thumbnail.jpg` ou `metadados.json` (cai em 6), BLOQUEADA (7 com aviso), slug da fila sem pasta (vai para `fila_orfaos`, não é vídeo).
- Linhas 1 e 2 vêm antes da fila porque `postar_pendentes.py` não remove da fila o vídeo já enviado.
- "Há vídeo pronto para a próxima postagem" = existe algum vídeo em `na_fila`; o "próximo" é o primeiro `na_fila` na ordem do arquivo (é o que `postar_pendentes.py` enviaria, pois ele pula quem não está pronto).
- A derivação nunca chama rede nem grava em arquivo ou banco.

**Consequência.** Um teste por linha da tabela e um por contradição (ver `PROG-012.md`), mais teste de paridade com `postar_pendentes.pendentes()`. Mudar a regra exige mudar esta tabela e o teste juntos. Pendente: quem cria `publico.json` (decisão de **Zico**/Guilherme).

## D-002 · 2026-11-03 · Cronograma só sugere, em módulo puro (PROG-011)
**Contexto.** A ata da planning manda "só sugere horário; nunca reordena a fila; tela só de leitura". `media/youtube.py` aceita `publishAt`, o que permitiria agendar publicação de verdade.
**Decisão.** `estudio/cronograma.py` é função pura (entrada: status do PROG-012, cadência, `agora`). Não importa `media.youtube` nem `postar_pendentes`, não escreve arquivo, não usa fuso (horário local do computador; `zoneinfo` exigiria `tzdata`, ausente do `requirements.txt`). Cadência em `config_shorts.yaml`, seção `cronograma`; sem a seção, a tela mostra a fila sem datas e pede a cadência.
**Consequência.** O critério 2 do backlog ("editável e persiste") conflita com a ata; segue a ata e o **Zico** ajusta o backlog.

## D-003 · 2026-11-03 · Contrato da aba Agentes ao vivo (PROG-003/006)
**Contexto.** A aba precisa de estado por agente sem somar carga ao polling existente, e o celular pode estar em outro fuso.
**Decisão.** Uma rota `GET /api/agentes/ao-vivo` (registrada antes de `/api/agentes/<id>`, que a capturaria), uma query em `jobs`, chave job-agente = `spec["agente"]` (nunca `jobs.craque`), tempo em segundos calculados no servidor, cache de 3 s para "Espera você", polling de 4 s pausado com a aba oculta. Rotas de página: `/agentes` = Ao vivo, `/agentes/<id>` = ficha (Catálogo), aba Catálogo em `?aba=catalogo`. Campos e regras em `PROG-003.md`.
**Consequência.** O contrato fica congelado quando **Rodrygo** publica a rota; mudar campo exige aviso a **Endrick** e a mim. Rota de página `/agentes/ao-vivo` ou `/agentes/catalogo` fica proibida (colide com id de agente).

## D-004 · 2026-11-03 · Testes novos não dependem de ids fixos de nó
**Contexto.** PROG-005 existe porque testes presos a `se_sketch` quebraram.
**Decisão.** Testes e fixtures novos derivam etapas e nós de `fluxo.ETAPAS`/`grafos.py` e criam dados em pasta e banco temporários, nunca em `output/` ou `estudio/dados` reais.
**Consequência.** Entrega que viole isso volta na revisão.

## D-005 · 2026-11-04 · Reserva com Codex: escopo e como testar (PROG-004)
**Contexto.** O Guilherme decidiu em 2026-11-03 (registrado em `CLAUDE.md` e `estudio/README.md`) que o Codex é reserva só para o limite de uso do Claude; a regra antiga "só Claude" foi revogada.
**Decisão.** A reserva fica mantida. Aciona apenas quando `reserva.e_limite_do_claude` é verdadeiro, uma tentativa por trabalho, sem voltar ao Claude, e todo trabalho novo tenta o Claude primeiro. Teste que usa o Codex de verdade (`--real`) é opt-in e roda com `cwd` em pasta temporária: o `codex exec` usa `workspace-write` e, com `cwd` igual à raiz do repositório, poderia gravar em qualquer arquivo dele.
**Consequência.** Todo teste real da reserva passa `cwd` temporário no spec. A integração (Claude simulado em limite no `executor.executar`, motor chegando ao estado público do job) precisa de teste próprio, além do teste direto de `_tentar_codex`.

## 2026-11-09: Painel só no computador; RAIZ do painel
- Contexto: o painel serve texto bruto de agentes e estratégia; o desenho previa 403 via rede, mas só o front escondia.
- Decisão: o servidor devolve 403 para /painel e /api/painel/* quando o cliente não é local ou o Host não é 127.0.0.1/localhost (ordem em `painel-403-rede.md`, com o **Rodrygo**). `painel.RAIZ = config.REPO`: `ESTUDIO_RAIZ` não isola o painel; só o teste troca `RAIZ` à mão. Aceito e documentado.
- Consequência: celular não abre o painel até o Guilherme decidir o contrário (pergunta 3 do refinamento).
