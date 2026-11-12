# Diagnóstico: Fluxo de Programação Enxuto

**Data:** 2026-11-04  
**Problema:** Sprint com 5 itens travados em "Code Review" aguardando **Thiago Silva**, Guilherme precisa cobrar manualmente.  
**Escopo:** Automação da fila de revisão + paralelização do fluxo + otimização de token.

---

## 1. Situação atual (snapshot)

### Quadro (2026-11-04, 10:38)

| Estado | Itens | Status |
|---|---|---|
| **Fazendo** | PROG-005 | 1/2 WIP. Testes passando, aguarda **Thiago Silva** revisar critério 3. |
| **Code Review** | PROG-015, 001, 002, 004, 005 | **5 itens ✅ QA aprovados**, aguardando revisão técnica do **Thiago Silva** |
| **Impedimentos** | 6 abertos | Disco C 99% (derruba testes), D-005 em PROG-004, Codex sem cota, tarefa Trello desativada, chat id Telegram, escopo PROG-011 |

### Fluxo de trabalho (sequencial, bloqueador)

```
Dev escreve → Testes rodando → QA passa ✅ → Code Review (aguarda Thiago) → Aceite (aguarda Zico) → Feito
                                                      ↑
                                            Gargalo aqui (sem notificação)
```

**Problema:** Nenhuma notificação automática sai quando item entra em Code Review. **Thiago Silva** descobre por polling manual (quando **Xavi** ou **Zico** avisam).

---

## 2. Diagnóstico

### A. Fila de Code Review não dispara notificação

**Causa:** Não há gatilho automático de mudança de estado → notificação.

**Impacto:**
- **Thiago Silva** demora a revisar (não sabe que espera)
- Devs ficam ociosos (WIP 0/2) enquanto revisão toma tempo indeterminado
- Guilherme cobra manualmente (overhead)

**SLA hoje:** Indeterminado. Última atualização de CR: 2026-11-04, 10:38. Tempo esperado de revisão: ~2-4 horas por item.

### B. Fluxo é sequencial, não paralelo

**Causa:** Dev espera revisão antes de puxar próximo item.

**Impacto:**
- WIP em "Fazendo" = 0/2 (capacidade ociosa)
- Limite de WIP (2 por dev) não é aproveitado
- Se **Thiago Silva** demora 4h em uma revisão, **Rodrygo** fica parado

**Oportunidade:** Pull paralelo: enquanto **Thiago Silva** revisa PROG-005, **Rodrygo** começa PROG-012 (próximo da sprint).

### C. Impedimentos travados (decision blocker)

**PROG-004 critério 1:** Cita D-005 (Codex como reserva).  
**Status:** D-005 foi registrada em 2026-11-04, `programacao/tecnico/decisoes.md` tem o conteúdo completo.  
**Problema:** Critério 1 pode estar esperando uma aprovação explícita que nunca chega.

**Ação:** **Zico** marcou como "bloqueado", precisa de **Thiago Silva** + Guilherme destravar.

### D. Consumo de tokens (diagnóstico, não é o gargalo)

| Agente | Ponto de consumo | Custo | Otimização |
|---|---|---|---|
| **Courtois** | Comparar roteiro vs notas | Médio (análise textual) | Grep + análise simples, já está bom |
| **Vini** (ANTES) | Validação de texto | Baixo (checagem) | Mantém |
| **Vini** (DEPOIS) | WebFetch de políticas YouTube | Médio (1-2 chamadas por vídeo) | **Cache local de políticas** (atualizar 1x/semana) |

**Insight:** Token **não é o gargalo principal**. O gargalo é **falta de notificação + fluxo sequencial**.

---

## 3. Soluções (prioridade de impacto)

### P1: Notificação automática de Code Review (30 min)

**O quê:** Quando um item entra em "Code Review" (QA aprova), **Thiago Silva** recebe aviso automático.

**Como:**

**Opção A (simples, imediato):** Hook em `quadro.md`
- Quando **Alisson** aprova um teste, ele escreve em `programacao/quadro.md`: item X vai para "Code Review"
- **Xavi** tira o item de "Em teste" e escreve em "Code Review"
- Trigger: adicionar uma linha no `quadro.md` tipo `<!-- notificar thiago-silva -->`
- (Superado) O antigo `monitor_cr.py` foi substituído pelo maestro da sprint (`programacao/maestro.py`), que a cada 15 min chama o agente dono de cada coluna e é o único que move cartões

**Opção B (integrada):** Editar `xavi-scrum-master.md`
- Quando **Xavi** move item para Code Review, sua checklist inclui "enviar mensagem ao **Ronaldo**: 'Thiago, item X aprovado em QA, aguarda sua revisão'."
- **Ronaldo** roteia para **Thiago Silva** via Telegram

**Recomendação:** Opção B é mais simples e não precisa de código novo. **Xavi** já tem o hábito; é só formalizar na descrição do agente.

**Artefato:** Editar `.claude/agents/xavi-scrum-master.md` linha ~30, adicionar checklist de notificação.

---

### P2: Maestro da sprint (antes proposto como "Monitor de fila")

**Situação atual:** esta proposta virou o maestro da sprint (`programacao/maestro.py`, tarefa `ContextoExplica-Sprint` a cada 15 min): chama o dono de cada coluna, aplica a decisão gravada e move o cartão no quadro e no Trello. O pseudo-código abaixo é histórico.

**O quê (proposta original):** Script que roda a cada 30 min, verifica quantos itens estão em CR e alerta se houver atraso.

**Como (proposta original):**

Pseudo-código do antigo `monitor_cr.py`:

```python
# Pseudo-code
def monitor_cr():
    quadro = read("programacao/quadro.md")
    cr_items = parse_cr_section(quadro)
    
    if len(cr_items) > 0:
        oldest = get_oldest_timestamp(cr_items)
        age_hours = (now() - oldest).total_seconds() / 3600
        
        if age_hours > 2:
            # Notificar Thiago
            notify_ronaldo("thiago-silva", f"Code Review: {len(cr_items)} itens, o mais antigo há {age_hours:.1f}h")
        
        if age_hours > 8:
            # Escalar para Zico
            notify_ronaldo("zico-po-programacao", f"Escalation: {len(cr_items)} itens em CR há {age_hours:.1f}h, rev. com Thiago")
```

**Agendamento:**
- Tarefa Windows atual: `ContextoExplica-Sprint`, a cada 15 min (a antiga `ContextoExplica-Monitor-CR` não existe mais)

**SLA definido:**
- 2h: notificação regular
- 8h: escalation

**Artefato:** Script novo + entrada em `programacao/README.md` (cadências).

---

### P3: Paralelizar fluxo (capacidade ociosa, 20 min)

**O quê:** Devs não ficam bloqueados esperando revisão. Pull paralelo de novos itens.

**Como:**

1. **Xavi** (Scrum Master) muda o fluxo em `quadro.md`:
   - Antes: dev aguarda revisão para puxar próximo
   - Depois: dev puxa próximo do backlog imediatamente (respeitando WIP 2)

2. **Zico** ordena backlog por prioridade (já faz).

3. **Thiago Silva** revisa em paralelo (não é um gargalo se houver paralelismo).

**Impacto:**
- WIP "Fazendo" pode ir de 0/2 para 2/2 (aproveita capacidade)
- Reduz tempo total de sprint de ~8h para ~6h
- **Rodrygo** e **Endrick** têm trabalho contínuo

**Artefato:** Editar `.claude/agents/xavi-scrum-master.md` para mencionar pull paralelo; mencionar em `programacao/README.md` na regra de Kanban.

---

### P4: Desbloquear PROG-004 (5 min)

**O quê:** PROG-004 está em CR mas não passa porque D-005 não está marcada como completa.

**Status:** D-005 existe e tem conteúdo (decisão sobre Codex como reserva, registrada em 2026-11-04).

**Ação:**
- **Zico** + **Thiago Silva** (na próxima revisão) marcam o critério 1 de PROG-004 como "revisado com sucesso contra D-005"
- PROG-004 segue normal para aceite

**Artefato:** Nada. Só comunicação via **Ronaldo** ou daily.

---

### P5: Cache de políticas YouTube (otimização token, 1h)

**O quê:** **Vini** reutiliza cache de políticas em vez de WebFetch toda vez.

**Como:**

1. Criar `estudio/cache_yt_politicas.json`:
```json
{
  "atualizado": "2026-11-04",
  "politicas": {
    "conteudo_enganoso": "Falsidade, clickbait excessivo bloqueia",
    "copyright": "Bloqueio automático + claim; resolver em estúdio",
    ...
  }
}
```

2. **Vini** (agente) lê do cache em vez de fazer WebFetch.

3. Cache atualizado 1x/semana (via script).

**Economia:** ~1-2 WebFetch/vídeo → 0 (cache local).

**Artefato:** Editar `.claude/agents/vini-auditor-conformidade.md` para ler cache; criar script de atualização.

---

## 4. Plano de ação imediato (para o Guilherme fazer hoje)

| # | O quê | Quem | Tempo | Bloqueia |
|---|---|---|---|---|
| **1** | Editar `xavi-scrum-master.md`: (superado pelo maestro, que chama **Thiago Silva** sozinho quando há item em Code Review) | **Luiz Henrique** | 5 min | - |
| **2** | Criar o maestro da sprint (`programacao/maestro.py`) + agendamento de tarefa Windows | **Zico** ou **Rodrygo** | 30 min | - |
| **3** | Daily com **Thiago Silva** + **Zico**: confirmar que D-005 cobre PROG-004 critério 1 | **Xavi** (daily) | 10 min | PROG-004 |
| **4** | Editar `programacao/README.md`: mencionar fluxo paralelo, SLA de revisão, monitor | **Luiz Henrique** | 10 min | - |
| **5** | (Opcional, depois) Cache de políticas YouTube | **Rodrygo** | 1h | - |

---

## 5. O que muda na sprint

### Estado futuro (esperado em 1-2 dias)

```
Dev escreve → Testes rodando → QA passa ✅ → Code Review + NOTIFICAÇÃO → Thiago revisa paralelo (2-4h)
                                                                     ↓
                                            Dev já puxou próximo item (WIP paralelo)
```

### Métricas

- **Tempo em Code Review:** SLA 2h → notificação; 8h → escalation
- **WIP capacidade:** 0/2 → 2/2 (devs ocupados)
- **Fluxo:** Sequencial → Paralelo (reduz total de sprint)
- **Tokens:** Mesmos (não é o gargalo)

---

## 6. Próximos passos

1. **Guilherme aprova o plano** (sim/não/ajustes) — hoje
2. **Luiz Henrique** aplica P1 (editar agente **Xavi**) — hoje
3. **Rodrygo** implementa P2 (maestro da sprint) — amanhã
4. Sprint roda com novo fluxo (próxima daily, 2026-11-05)
5. Colher feedback (review de sprint, 2026-11-10)

---

**Assinado:** **Valverde** (2026-11-04)

---

## Apêndices

### A. Timestamps esperados

- Agora (04/11, 11:00): 5 itens em CR desde ~09:00 (2h)
- PROG-005 (testes atualizados): aprox. 2-4h de revisão (testes, 3 critérios)
- PROG-001, 002: ~1h cada (bugs simples)
- PROG-004, 015: ~2-4h cada (decisão, regressão)

### B. Arquivos afetados

```
.claude/agents/xavi-scrum-master.md          ← Editar (checklist de notificação)
programacao/README.md                         ← Editar (SLA, fluxo paralelo)
programacao/maestro.py                        ← Criar (maestro da sprint)
estudio/cache_yt_politicas.json               ← Criar (opcional, depois)
```

### C. Agentes envolvidos

- **Luiz Henrique:** aplica mudanças estruturais (agentes, README)
- **Xavi:** fluxo de notificação e paralelismo
- **Zico:** priorização de backlog, aceite com Guilherme
- **Thiago Silva:** revisão com SLA
- **Valverde:** diagnosis e proposta (já fez)
