# Revisão · PROG-012 · Status automático de cada vídeo
Revisor: **Thiago Silva** · 2026-11-05 · Código de **Rodrygo** (`estudio/status_video.py`, rota em `estudio/servidor.py:221`, teste `testar_status_video.py`).

**Veredito: APROVADO.**

## O que conferi (código real e testes rodados hoje)
- `testar_status_video.py`: 45 ok, 0 falhas. CLI contra o `output/` real: lista os vídeos, mostra aviso de BLOQUEADA e de "na fila sem auditoria".
- Tabela D-001 aplicada na ordem certa (`status_video.py:113-127`); contradições viram aviso e nunca status falso (`:129-153`).
- Só leitura: um `scandir` por pasta, sem rede, sem banco, sem import de `media.youtube` nem `postar_pendentes`. Rota só GET (`servidor.py:221`).
- Reusa `materiais.status_auditoria` (mesmo critério do `run.py publish`).
- Regressões já rodadas pela **Alisson** (roteiro 29, estilos 103, e2e 150): verdes.

## Divergências do texto do backlog (decisão do **Zico**, não minha)
1. **Critério 11**: o backlog diz "sim" só se o PRIMEIRO da fila está pronto; o código (D-001, escrita por mim) diz "sim" se algum item está pronto, pois é o que `postar_pendentes` envia, e o motivo cita os bloqueios à frente. Mudar o texto do critério ou o código é escopo. Não conto o 11 como comprovado.
2. **Critério 12**: pasta totalmente vazia não aparece na lista (`todos()` filtra com `e_producao`, como o Corte); só a pasta com algum arquivo sem roteiro aparece como "sem roteiro". O `status_do_video` de uma pasta vazia devolve "sem roteiro". Se o Zico quiser a pasta vazia na lista, é uma linha (tirar o filtro). Não conto o 12 como comprovado literalmente.

## Observações (não bloqueiam)
- Risco de reenvio: vídeo com `upload.json` sem `publicado.json` aparece como publicado, mas `postar_pendentes` o enviaria de novo. Item separado para o Zico.
- Limite de desempenho interno de 300 ms é sensível a carga; sugiro 1 s (o critério é 2 s).
- `publico.json` (marcador manual): quem cria segue pendente do Zico/Guilherme.
