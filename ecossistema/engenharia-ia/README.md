# Engenharia de IA — Diagnósticos e Propostas

Pasta de relatórios técnicos sobre eficiência do ecossistema: consumo de tokens, fluxo de agentes, automação.

**Responsável:** **Valverde** (`valverde-engenheiro-ia`)  
**Reporta a:** **Luiz Henrique** (`luiz-henrique-ecossistema`)

---

## Projetos

### 1. Fluxo de programação enxuto (2026-11-04) ⚡ ATIVO

**Problema:** 5 itens em Code Review travados, Guilherme cobra manualmente.  
**Solução:** Notificação automática + fluxo paralelo de devs.  
**Status:** ✅ Pronto para aprovação

**Leia:**
1. **`ACAO-IMEDIATA.md`** (5 min, Guilherme aprova aqui)
2. `DIAGNOSTICO-FLUXO-PROGRAMACAO.md` (análise completa)
3. `INSTALACAO-MONITOR-CR.md` (nota curta sobre o maestro da sprint)

**Implementação:**
- Editar: `xavi-scrum-master.md` (checklist de notificação)
- Editar: `programacao/README.md` (SLA, fluxo paralelo)
- Maestro da sprint (`programacao/maestro.py`, substituiu o antigo `monitor_cr.py`): chama o dono de cada coluna a cada 15 min e é o único que move cartões

**Impacto:** Notificação automática, WIP paralelo (0/2 → 2/2), SLA visível.

---

### 2. Token e eficiência do canal (2026-11-03)

**Problema:** Sobreposição entre **Courtois** e **Vini**, duplicação com `compliance.py`.  
**Solução:** Separar revisão pré-render (texto) de auditoria pós-render (vídeo).  
**Status:** Proposta pronta, aguarda aprovação

**Leia:**
- `2026-11-03.md` (diagnóstico)
- `propostas.md` (soluções, ~56% economia de tokens)

**Implementação:**
- Editar: `.claude/agents/courtois-revisor-fatos.md` (humano, sem auto-check)
- Editar: `.claude/agents/vini-auditor-conformidade.md` (modo TEXTO vs FINAL)

---

## Estrutura de arquivos

| Arquivo | Propósito | Status |
|---|---|---|
| `README.md` | Este documento | ✅ |
| **FLUXO PROGRAMAÇÃO** | |
| `ACAO-IMEDIATA.md` | Sumário executivo (leia primeiro) | ✅ |
| `DIAGNOSTICO-FLUXO-PROGRAMACAO.md` | Análise completa: problema raiz, soluções P1-P5 | ✅ |
| `INSTALACAO-MONITOR-CR.md` | Nota sobre o maestro da sprint | ✅ |
| **TOKEN E EFICIÊNCIA** | |
| `2026-11-03.md` | Diagnóstico completo: mapa de consumo, sobreposição, ineficiências ranqueadas | ✅ |
| `propostas.md` | Propostas prontas: redefinir **Courtois** e **Vini**, impacto esperado | ✅ |
| `analise-vini-courtois.md` | Deep dive: filtragem, duplicação, recomendações | ✅ |
| `mapa-consumo.md` | Visualização: onde token é gasto (por agente/função) | ✅ |
| Outros | Análises exploratórias, ideias, notas | 🗂️ |

---

## Como usar

### Se você é o Guilherme

1. Leia `ACAO-IMEDIATA.md` (5 min, fluxo de programação)
2. Aprova/recusa (responda no documento)
3. Passa ao **Luiz Henrique** para aplicação

### Se você é o Luiz Henrique

1. Leia `DIAGNOSTICO-FLUXO-PROGRAMACAO.md` seção 3 (Plano de ação)
2. Aplique P1, P3, P4 (editar 2 agentes; o monitor virou o maestro)
3. Passe ao **Marquinhos** para conferir o maestro da sprint

### Se você é o Marquinhos (DevOps)

1. Leia `INSTALACAO-MONITOR-CR.md` (maestro da sprint)
2. Roda `maestro.py --simular` e confere a tarefa `ContextoExplica-Sprint`
3. Confirma no Telegram que foi

### Se você é o Valverde (futuro)

1. Leia tudo para contexto
2. Próximas análises: P5 (cache de políticas YouTube), métricas de fluxo (**Ancelotti**)
3. Feedback da sprint 01 na retro (2026-11-10)

---

## Regras

- **Diagnóstico e proposta apenas.** Não edita arquivos de outros agentes nem do canal.
- **Nenhuma ação externa:** sem commit, sem publicação, sem senha/token.
- **Medidas reais:** baseadas em leitura de código, não em estimativa ou achismo.
- **Reversível:** todas as propostas podem ser desfeitas em minutos se não funcionarem.

---

**Mantido por:** **Valverde**  
**Última atualização:** 2026-11-04, 11:35  
**Próxima revisão:** 2026-11-10 (retro da sprint 01)
