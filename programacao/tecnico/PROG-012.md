# PROG-012 · Status automático de cada vídeo · Nota técnica

Autor: **Thiago Silva** · 2026-11-03 · Quem faz: **Rodrygo** (back, tudo). **Endrick** não entra.

## Abordagem
Um módulo novo, puro e só de leitura: `estudio/status_video.py`. Sem banco, sem rede, sem escrita. Recebe a pasta `output/<slug>/` e a lista da fila e devolve um status. A regra única está em `decisoes.md` (D-001); o código e o teste seguem a tabela de lá, nada mais.

API do módulo:
- `status_do_video(slug, fila=None)` devolve `{slug, titulo, status, status_texto, avisos[], falta, fila_posicao, publicado{url, privacidade}|None, atualizado_em}`.
- `ler_fila()` lê `output/fila_postagem.txt` (mesma leitura de `postar_pendentes.py`: `strip`, ignora vazio e `#`, remove duplicata mantendo a primeira).
- `todos()` devolve `{videos[], proximo_pronto{sim, slug, motivo}, fila_orfaos[]}`.
- Rota `GET /api/videos/status` em `estudio/servidor.py` (só GET, sem efeito colateral) e CLI `python -m estudio.status_video` (tabela em texto no terminal).

Por que não reusar `fluxo.estado()`: ele chama `garantir_producao` e `sincronizar`, que gravam no banco; é caro e a regra do PROG-012 é só sobre arquivos. Por que não importar `postar_pendentes.py`: ele depende de `yaml` e de `ROOT` fixo. A paridade com ele é garantida por teste (abaixo), não por import.

Fontes reais conferidas no código:
- `upload.json` é gravado por `media/youtube.py:163` em qualquer envio (`run.py publish` e `postar_pendentes.py`), com `video_id`, `url`, `privacy`. É o registro canônico.
- `publicado.json` (só `postar_pendentes.py:88`, com `privacidade`) é redundante; lê-se como reserva.
- `fluxo.publicado()` (`fluxo.py:827`) já lê `upload.json`; não mudar, só manter coerente.
- `auditoria.md`: critério de `materiais.status_auditoria` (BLOQUEADO vence APROVADO). Reusar essa função, não reescrever. Atenção: a dispensa do Guilherme (`fluxo.py:1099`) grava "APROVADO COM DISPENSA DO GUILHERME" e conta como APROVADO (igual ao `run.py publish`). Mostrar no texto "auditado (dispensa do Guilherme)" é bônus, não obrigatório.

## Riscos
1. **Dois nomes de registro de publicação** (`upload.json` e `publicado.json`): ler os dois; `upload.json` vazio (`{}`, como no e2e) conta como publicado, privacidade desconhecida, e cai em "privado" com aviso (critério 4).
2. **Fila contém vídeo já publicado**: `postar_pendentes` nunca remove da fila. A regra põe "publicado" acima de "na fila".
3. **Pré-condições do envio**: `postar_pendentes` só pega vídeo com `video.mp4`, `thumbnail.jpg`, `metadados.json` e auditoria APROVADA. "Na fila" só vale se tudo isso existir; senão "auditado" + aviso do que falta. Duplicar essa lógica pode divergir: o teste de paridade abaixo trava isso.
4. **"Público" não é observável por arquivo** depois que o Guilherme publica no Studio. Só vale com `upload.json.privacy == "public"` ou o marcador `publico.json`. Falta definir quem cria o marcador (lacuna para o **Zico**, ver abaixo). Nada de chamada ao YouTube na derivação.
5. **Auditoria mais velha que o vídeo** (novo render autorizado): fora do escopo; fica como aviso futuro, não mexer agora.
6. **Custo**: `output/` tem dezenas de pastas. Por pasta: ~6 `stat`, leitura de `auditoria.md` e de `metadados.json` (só o título). Sem varrer `falas/` nem `frames/`. Meta: 100 pastas em menos de 300 ms.
7. **Pasta sem nenhum arquivo de produção** (`e_producao` falso) não é vídeo: ignorar, igual ao Corte.

## Arquivos afetados
- Novo: `estudio/status_video.py`, `estudio/testes/testar_status_video.py`.
- Editar: `estudio/servidor.py` (uma rota GET, registrada com as de `/api/`), `estudio/README.md` (documentar rota, CLI e regra).
- Não tocar: `fluxo.py`, `postar_pendentes.py`, `media/youtube.py`, `run.py`.

## Testes exigidos
Novo `estudio/testes/testar_status_video.py` (pasta temporária, nunca `output/` real). Um caso por estado e por contradição:
- sem roteiro; em produção; vídeo pronto (sem auditoria, auditoria ausente, BLOQUEADA, reprovada); auditado; na fila (completo); na fila sem `thumbnail.jpg` (vira auditado + aviso); publicado privado via `upload.json`; via `publicado.json`; `upload.json` `{}`; público via `privacy: public`; público via `publico.json`.
- contradições com aviso em português: na fila sem `video.mp4`; na fila sem auditoria; slug da fila sem pasta (aparece em `fila_orfaos`).
- `proximo_pronto`: sim/não; o primeiro da fila não pronto e o segundo pronto devolve o segundo (é o que `postar_pendentes` enviaria) e informa o bloqueio do primeiro.
- **Paridade**: com `postar_pendentes.FILA` e `ROOT` trocados para a pasta temporária, o conjunto de slugs "na fila" tem de ser igual a `postar_pendentes.pendentes()`.
- **Sem efeito colateral**: hash de `fila_postagem.txt` e de todos os arquivos da pasta igual antes e depois; nenhuma linha nova em `estudio/dados` (banco).
- Rota: `GET /api/videos/status` responde JSON; POST na rota dá 404.
- Desempenho: 100 pastas fictícias abaixo do limite.
Baterias a rodar antes de entregar: `testar_status_video.py` (nova), `testar_roteiro.py`, `testar_estilos.py` (garante que o servidor sobe) e `e2e_interface.mjs` (regressão da rota nova não quebrar o roteamento). **Alisson** confirma a lista no `qa/`.

## Pergunta para o Zico (escopo, não decido)
Critério 6 diz "uma visão lista todos os vídeos". Planejei a visão como rota JSON + CLI de terminal, e a tela fica dentro do PROG-011 (cada linha do cronograma já mostra o status). Se o Guilherme quer uma tela própria do PROG-012, vira item de **Endrick** (pequeno) e precisa de desenho do **Iniesta**. Também: quem cria o marcador `publico.json` (critério 4 aceita "marcação manual")? Sugestão: por ora o Guilherme cria o arquivo à mão e o botão fica para depois.

## Ordem e estimativa
**Rodrygo**, 1 dia: regra e testes primeiro (a regra já está fechada em D-001), rota por último. Entrega registrada em `entregas/PROG-012.md`; eu reviso antes do **Alisson**.
