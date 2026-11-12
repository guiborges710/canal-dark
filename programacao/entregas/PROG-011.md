# PROG-011 · Cronograma de postagem · Entrega 1 (cálculo e rota, só leitura) · Rodrygo · 2026-11-05

## O que mudou
- Novo `estudio/cronograma.py`: `calcular(agora, cadencia, saida)` e `ler_cadencia()`. Só lê (status do PROG-012, fila, yaml). Não importa youtube nem postar_pendentes, não escreve, não reordena a fila.
- `estudio/servidor.py`: rota `GET /api/cronograma` (import + 2 linhas).
- `config_shorts.yaml`: seção `cronograma` só como comentário de exemplo (sem ela vale 1 vídeo/dia às 18:00, item 11 do Zico, e a saída avisa).
- `estudio/README.md`: parágrafo da rota.

## Teste (escrito antes do código)
`estudio/testes/testar_cronograma.py`, 42 verificações com relógio fixo: ordem da fila e reordenação; título ausente/inválido; sem auditoria / sem vídeo no topo; alerta a 0, 1 (sim) e 2, 3 dias (não); virada de ano; seg/qua/sex; minuto exato do horário; sem cadência e cadência inválida; fila vazia; slug sem pasta; publicado não ocupa slot; 50 itens; hash de `output/` e da fila inalterado; rota GET e POST recusado.

## Rodado (resultado real)
- `.venv\Scripts\python estudio\testes\testar_cronograma.py` → 42 ok, 0 falhas.
- `.venv\Scripts\python estudio\testes\testar_status_video.py` → 45 ok, 0 falhas.

## Critérios do backlog cobertos nesta entrega
1, 3, 4, 5, 6 (só no cálculo/rota), 8 (fila vazia, slug sem pasta), 9 (backend). Data passada: o cálculo só gera datas futuras.

## Não feito / pendente
- Tela (critérios 7 e visão de celular, T14/T24): é do **Endrick** e precisa do desenho do **Iniesta**; e2e e `e2e_celular.mjs` ainda não escritos.
- Critério 2 (editar): fora da entrega 1 (item 10 do Zico); conflito de redação com a ata segue com o **Zico**.
- Cadência real do Guilherme: não definida; vale a assunção.
- Não rodei `e2e_interface.mjs`/`e2e_celular.mjs`: a mudança no servidor é só uma rota GET nova e não há tela.
