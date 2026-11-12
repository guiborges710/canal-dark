# Ambiente · checagem de 2026-11-03 (noite)

Dono: **Marquinhos**. Só leitura; nada instalado, atualizado ou commitado.

| Item | Resultado |
|---|---|
| Python do `.venv` | 3.10.11 (ok, mínimo 3.10) |
| Dependências Python | `pip check`: sem conflito; todos os pacotes de `requirements.txt` instalados |
| Node / npm | v24.15.0 / 11.12.1; `render/node_modules` presente |
| ffmpeg / ffprobe | 9.0.2 (gyan full build), no PATH |
| Chrome | `C:\Program Files\Google\Chrome\Application\chrome.exe` presente (`CHROME_PATH` não necessário) |
| Voz | `voz/amostra.wav` presente |
| `.env` | existe (conteúdo não lido) |
| Tarefa ContextoExplica-Trello | estado Ready (ativa). Não foi rodada nem alterada. Segue o impedimento de pausá-la antes das baterias do **Alisson**. |

## Pixel Agents (somente leitura)
- `~/.claude/settings.json`: JSON válido. O hook `node ~/.pixel-agents/hooks/claude-hook.js` (timeout 5) está registrado, sem matcher, em SessionStart, SessionEnd, Stop, PermissionRequest, Notification, PreToolUse, PostToolUse, PostToolUseFailure, **SubagentStart**, **SubagentStop**, TeammateIdle e TaskCompleted. Cobre agentes e subagentes.
- `~/.pixel-agents/hooks/claude-hook.js` existe (atualizado em 26/10). `config.json`: `hooksEnabled.claude = true`, consentimento `granted`, `watchAllSessions = true` (perfil vscode).
- Servidor: `server.json` e `servers/32576-52827.json` coerentes (porta 52827, protocolo 1, token presente). PID 32576 é o `Code.exe` vivo e a porta 52827 está em LISTENING em 127.0.0.1. O hook descarta registros de PID morto; este está vivo.
- O projeto não tem `.claude/settings.json`, e `.claude/settings.local.json` não define hooks: nada sobrescreve os hooks globais.
- Hook paralelo do Agent Flow (`~/.claude/agent-flow/hook.js`) também íntegro.

Conclusão: configuração íntegra. Limites: (1) o servidor depende do VS Code aberto (se fechar, o hook não entrega, sem erro); (2) a leitura não prova a chegada de eventos, só um agente aparecendo no escritório prova; (3) `watchAllSessions` está ligado só no perfil vscode, e o perfil standalone tem `false`.

## Problemas encontrados
1. Árvore git muito suja (mais de 5000 entradas em `git status`; 68 só em `estudio/`, `media/`, `render/`, `run.py`), com muita coisa só em stage (`A`/`AM`). Commit da Sprint 01 exigirá separar por item. Avisos de LF/CRLF em vários arquivos.
2. Tarefa ContextoExplica-Trello ativa (impedimento já aberto).
3. Telegram sem chat id (impedimento já aberto).
