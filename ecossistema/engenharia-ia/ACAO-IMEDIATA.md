# Ação Imediata: Sprint enxuta sem intervenção manual

**Data:** 2026-11-04, 11:00  
**Problema:** 5 itens em Code Review aguardando **Thiago Silva**, você cobra manualmente.  
**Solução:** 3 mudanças simples + 1 script = sprint roda sozinha.  
**Tempo total:** 40 min de setup (na verdade: 5 min que você faz, 35 min que **Luiz Henrique** faz).

---

## O que foi feito (já pronto)

✅ **Luiz Henrique atualiza os agentes e documentação**
- `xavi-scrum-master.md`: o maestro chama **Thiago Silva** sozinho quando há item em Code Review (substitui a notificação via Telegram)
- `programacao/README.md`: mencionado SLA (2h / 8h) e fluxo paralelo (devs não ficam bloqueados)
- maestro da sprint (`programacao/maestro.py`, substituiu o antigo `monitor_cr.py`): a cada 15 min chama o agente dono de cada coluna com cartão, e só ele move cartões, aplicando a decisão gravada pelo agente (detalhes em `INSTALACAO-MONITOR-CR.md`)

✅ **Pronto para testar**
- Arquivo: `ecossistema/engenharia-ia/INSTALACAO-MONITOR-CR.md` (nota curta sobre o maestro)

---

## O que você faz (5 min, hoje)

| # | O quê | Tempo | Resultado |
|---|---|---|---|
| **1** | Pedir ao **Luiz Henrique** rodar os 3 arquivos acima (lê + compra a estratégia) | 2 min | Mudanças prontas |
| **2** | Pedir ao **Marquinhos** conferir o maestro da sprint (`INSTALACAO-MONITOR-CR.md`) | 30 min | Tarefa agendada ✅ |
| **3** | Na daily de amanhã (2026-11-05, 10:30), **Xavi** avisa: "fluxo mudou, devs puxam paralelo" | 5 min | Equipe alinhada |

---

## O que muda na sprint (amanhã)

### Antes (hoje)
```
QA aprova PROG-005 → PROG-005 em "Code Review" → Thiago demora 4h → Rodrygo espera ocioso
```

### Depois (amanhã)
```
QA aprova PROG-005 → maestro move para "Code Review" e chama **Thiago Silva**
                  → Rodrygo PULA: pula PROG-012 do backlog (WIP 2/2)
                  → Thiago revisa PROG-005 em paralelo
                  → Maestro (`programacao/maestro.py`) chama o dono da coluna a cada 15 min e move o cartão
```

---

## Impacto esperado

| Métrica | Hoje | Depois |
|---|---|---|
| Notificação de Code Review | Manual | Automática (maestro da sprint) |
| Devs ociosos esperando revisão | Sim (WIP 0/2) | Não (WIP 2/2, puxam paralelo) |
| Tempo total de sprint | ~8h | ~6h |
| Tempo médio de revisão | ? | Visível (SLA 2h) |
| Intervenção manual sua | Alto ("Thiago, revisa") | Baixo (só se ultrapassar 8h) |

---

## Arquivos/Pessoas envolvidas

```
Você
 ├─ Luiz Henrique (estratégia + edições)
 │   ├─ xavi-scrum-master.md (checklist de notificação)
 │   ├─ programacao/README.md (SLA, fluxo paralelo)
 │   └─ validar que as mudanças fazem sentido
 │
 └─ Marquinhos (instalação técnica)
     ├─ Rodar programacao/maestro.py --simular (validar)
     └─ Conferir a tarefa Windows ContextoExplica-Sprint
```

---

## Próximos passos

1. **Hoje (11/04):** você aprova, **Luiz Henrique** aplica, **Marquinhos** instala
2. **Amanhã (11/05), 10:30:** daily + **Xavi** alinha equipe
3. **Esta semana:** rodar a sprint com novo fluxo, colher feedback
4. **Próxima sprint:** **Ancelotti** mede fluxo (lead time, WIP, SLA cumprido?)

---

## Se não gostar, volta em 2 min

Tudo é reversível:
- Desfazer **Xavi**: editar `xavi-scrum-master.md` (remover checklist de notificação)
- Pausar o maestro: `Disable-ScheduledTask ContextoExplica-Sprint`
- Fluxo sequencial: **Xavi** volta a bloqueador (devs esperam revisão)

Mas acredito que funciona. 😊

---

**Próxima ação:** Responder aqui: "Aprova? Sim/Não/Ajustes".
