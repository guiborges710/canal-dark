# PROG-011 · Cronograma de postagem (só sugere horário) · Nota técnica

Autor: **Thiago Silva** · 2026-11-03 · Quem faz: **Rodrygo** (cálculo e rota, depois do PROG-012) e **Endrick** (tela de leitura desenhada pelo **Iniesta**). Depende do PROG-012 e da cadência do Guilherme (impedimento aberto).

## Conflito de critérios para o Zico resolver
O backlog (critério 2) pede cronograma "editável, com a mudança persistida". A ata da planning (decisão 7) diz: só sugere, nunca reordena `fila_postagem.txt`, tela leve só de leitura. Sigo a **ata** (é mais nova e do Guilherme). **Zico** precisa ajustar o critério 2 do backlog: editar a ordem continua sendo editar o arquivo à mão; a cadência fica em configuração. Nada na tela grava.

## Abordagem
Função pura em `estudio/cronograma.py`, sem escrita e sem rede:
`sugerir(videos, cadencia, agora)`.
- Entrada: a lista de `todos()` do PROG-012 (já na ordem da fila) e a cadência.
- Slots: a partir de `agora`, os próximos N horários da cadência (datas e `HH:MM` locais, sem fuso: o computador do Guilherme é no Brasil e o Brasil não tem horário de verão desde 2019). Não usar `zoneinfo`: no Windows ele exige o pacote `tzdata`, que não está em `requirements.txt`.
- Atribuição: o i-ésimo vídeo não publicado da fila, na ordem do arquivo, recebe o i-ésimo slot. Vídeo não pronto também recebe slot (é o que mostra o alerta).
- Saída por linha: `{data, hora, slug, titulo, status, status_texto, falta, alerta}`; `alerta` quando o slot está a menos de 2 dias e o vídeo não está "na fila". Slot sem vídeo na fila gera linha "Sem vídeo na fila para DD/MM" com alerta no mesmo prazo.
- Topo: `proxima`: "Pronto para postar" (o primeiro slot tem vídeo "na fila") ou "Sem vídeo pronto para DD/MM, falta: <falta>". O texto de `falta` vem do PROG-012 (ex.: "auditoria final APROVADA do Vini").
- Cadência: seção nova `cronograma` em `config_shorts.yaml`, por exemplo `dias: [seg, qua, sex]` e `hora: "18:00"`. **Sem a seção, nada é inventado**: a tela lista a fila com status e diz "Cadência ainda não definida: ver config_shorts.yaml". Assim o código não espera a resposta do Guilherme, e quando ela chegar basta preencher o arquivo.
- Rota `GET /api/cronograma` (só GET). Tela: nova rota `/cronograma` em `corte_nav.js`/`index.html` com o padrão de `Corte.registrar`, ou bloco no topo de Projetos (decisão do **Iniesta**; ver `ux/`). Hoje não há desenho do **Iniesta** para esta tela: bloqueia a parte do **Endrick**.

## O que o item nunca faz (travas)
- Não chama `youtube.upload` nem monta `publish_at`. `media/youtube.py:128` já aceita `publishAt`; ligar a sugestão nele seria agendar publicação, o que a regra do setor proíbe. Teste verifica que o módulo não importa `media.youtube` nem `postar_pendentes`.
- Não escreve em `output/`, não reordena `fila_postagem.txt`, não muda privacidade.
- Os horários são sugestão: o upload real continua sendo `postar_pendentes.py` (privado) e a publicação, manual no Studio. Dizer isso na tela ("sugestão para publicar no Studio").

## Riscos
1. Cadência indefinida: tratada acima (estado "sem cadência"). Não bloqueia o código; bloqueia só o aceite com dados reais.
2. Divergência entre "ordem sugerida" e o que `postar_pendentes` envia: ele pula vídeo não pronto e sobe o próximo pronto. A tela precisa dizer isso quando o primeiro slot está bloqueado ("o envio vai pular este e subir <slug>"). Dado já vem do `proximo_pronto` do PROG-012.
3. Data passada / fila vazia / fila com slug sem pasta: estados definidos nos testes, sem exceção.
4. Hora do relógio: `agora` entra como parâmetro (testável); a rota usa `datetime.now()`.
5. Colisão de front com PROG-003/006: ver `PROG-003.md` (sequência).

## Arquivos afetados
Novo: `estudio/cronograma.py`, `estudio/testes/testar_cronograma.py`, tela (`estudio/web/corte_cronograma.js` ou bloco em `corte_estudio.js`, definido pelo **Iniesta**), CSS em `corte.css` e `celular.css`. Editar: `estudio/servidor.py` (rota GET e a rota de página `/cronograma` junto de `startswith(("/producao/", ...))`), `corte_nav.js`, `index.html`, `config_shorts.yaml` (comentário de exemplo, seção comentada), `estudio/README.md`.

## Testes exigidos
Novo `testar_cronograma.py`, com `agora` fixo: fila com vários vídeos; fila vazia; vídeo sem auditoria; alerta a 1 dia e sem alerta a 3 dias; slot sem vídeo; data de cadência no mesmo dia depois da hora; sem cadência; fila com slug sem pasta; garantia de que `fila_postagem.txt` não muda (hash). e2e novo (`e2e_cronograma.mjs`, ou casos em `e2e_interface.mjs`): tela mostra texto do status e o topo "Pronto para postar"/"Sem vídeo pronto"; funciona na largura de celular (`e2e_celular.mjs`). Rodar: `testar_cronograma.py`, `testar_status_video.py`, `e2e_interface.mjs`, `e2e_celular.mjs`. Testes de e2e derivam dados de fixtures próprias, não de nós fixos do grafo.

## Ordem
Só começa depois do PROG-012 aceito pela revisão. **Rodrygo** primeiro (cálculo e rota, ½ dia); **Endrick** a tela depois do desenho do **Iniesta**.
