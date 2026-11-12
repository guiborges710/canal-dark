# API do Corte para a central de programação: especificação (2026-11-03)

Autor: **Valverde**. Não editei `estudio/servidor.py` nem criei `estudio/agentes_api.py`: ficam fora da minha pasta de escrita e o pedido de autorização veio de outro agente, não do Guilherme. Esta especificação deixa a implementação pronta para quem for dono do código (**Rodrygo**, com **Thiago Silva** revisando).

## O que já existe em `estudio/servidor.py`
`GET /api/agentes`, `GET /api/agentes/<id>`, `POST /api/agentes` e `POST /api/agentes/<id>/<ação>` já existem (linhas ~232-290). Conferir antes de criar rota nova: `start` pode ser só uma ação nova na rota que já existe, em vez de um endpoint novo.

## Endpoints pedidos
1. `GET /api/agentes/status`
   Resposta: `[{"id", "nome", "estado", "job_id", "desde"}]`. `estado` em: `rodando`, `parado`, `esperando_prompt`, `esperando_autorizacao`. Fonte: jobs ativos do `estudio/executor.py` e `estudio/trabalhos.py`; sem job é `parado`. Atenção: regex de `/api/agentes/([\w-]+)` captura `status` como id; registrar a rota `status` **antes** dela.
2. `GET /api/sprints/ativa`
   Fonte: o quadro da sprint ativa (Trello, conforme "Regra do quadro" de `programacao/README.md`). Resposta: `{"nome", "inicio", "fim", "itens": [{"id", "titulo", "estado", "dono"}]}`. Se o Trello não estiver acessível, devolver 503 com o motivo, sem inventar dados. Credenciais só no `.env`, nunca na resposta.
3. `POST /api/agentes/<id>/start`
   Corpo: `{"prompt": "..."}`. Dispara pelo mesmo caminho do Corte (inclui a reserva Codex de `estudio/reserva.py`). **Ação que gasta cota**: exigir confirmação explícita do usuário na interface; recusar com 409 se o agente já estiver `rodando`; recusar `id` que não exista em `.claude/agents/`. Não aceitar caminho de arquivo no corpo.

## Segurança
Servidor local (127.0.0.1) por padrão; em `--rede` já tem senha (`estudio/acesso.py`): as três rotas passam pelo mesmo controle. Validar `id` com o regex existente.

## Onde documentar depois de implementar
`ecossistema/README.md`, `ecossistema/API.md` e `estudio/README.md`, escritos por quem implementar (não alterei).
