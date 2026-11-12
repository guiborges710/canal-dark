# Entrega PROG-012 · Status automático de cada vídeo
Autor: **Rodrygo** · 2026-11-04 · Segue `tecnico/PROG-012.md` e a regra D-001 (`tecnico/decisoes.md`).

## O que mudou
- Novo `estudio/status_video.py`: `status_do_video`, `ler_fila`, `todos`, CLI `python -m estudio.status_video`. Só leitura (uma varredura de pasta por vídeo; sem rede, sem banco, sem escrita).
- `estudio/servidor.py`: rota `GET /api/videos/status` (POST cai no 404 padrão).
- `estudio/README.md`: seção "Status de cada vídeo" e o teste novo na lista.
- Novo `estudio/testes/testar_status_video.py` (pasta temporária; nunca `output/` real).
- Não toquei em `fluxo.py`, `postar_pendentes.py`, `media/youtube.py`, `run.py`.

Observação de processo: escrevi o módulo antes do arquivo de teste; o teste foi então rodado contra ele e achou 2 problemas (abaixo), corrigidos.

## Resultados reais (rodados hoje)
- `testar_status_video.py`: **45 ok, 0 falhas** (cobre C1-C8, C10-C12, C14-C17, C18, C21-C27 do `qa/PROG-012-casos.md`, paridade, sem efeito colateral, rota GET/POST e desempenho: 100 pastas em ~194 ms, limite 300 ms).
- `testar_roteiro.py`: 29 ok, 0 falhas.
- `testar_estilos.py`: 103 ok, 0 falhas.
- `e2e_interface.mjs` (E2E_PORTA=8791): 150 ok, 0 falhas.
- CLI contra o `output/` real (só leitura): lista os vídeos e o aviso de BLOQUEADA e de "na fila sem auditoria" aparecem corretamente; próxima postagem pronta = não, com motivo.
- Problemas achados pelo teste: (1) desempenho 696 ms por 25 `stat` por pasta; resolvido com `os.scandir` único; (2) premissa errada da nota técnica: `postar_pendentes.pendentes()` NÃO remove duplicata da fila (a nota dizia que removia); a paridade é comparada como conjunto.

## Divergências / decisões para Thiago Silva e Zico
1. **Critério 11 do backlog x D-001**: o backlog diz "sim" só se o *primeiro* da fila está na fila; D-001 diz "o primeiro `na_fila`", que é o que `postar_pendentes` enviaria. Implementei D-001 e o motivo cita os bloqueios à frente.
2. **C23**: `APROVADO` e `REPROVADO` juntos: a regra reusada (`status_auditoria`, igual ao `run.py publish`) aprova. Mantive a paridade e acrescentei só um aviso; endurecer exige mudar o `run.py` (fora do escopo).
3. **Paridade parcial**: vídeo com `upload.json` mas sem `publicado.json` aparece como publicado aqui, mas `postar_pendentes` ainda o enviaria de novo. Risco real de reenvio, vira pedido ao Zico.
4. **Público**: marcador `publico.json` (manual). Quem cria e se haverá botão: pendente do Zico/Guilherme.
5. **Critério 6 como tela própria**: só rota JSON + CLI; tela fica no PROG-011 (**Endrick**/**Iniesta**). C28 (celular) continua bloqueado por tela, não é deste item.
6. C13 (auditoria mais antiga que o vídeo) fora do escopo, como na nota técnica; C19/C20 por revisão: nenhum import de `media.youtube`/`postar_pendentes` no módulo; hash dos arquivos da pasta temporária idêntico.

## Pendente
Revisão do **Thiago Silva** e testes do **Alisson**. Não commitei.
