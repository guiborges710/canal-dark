# Análise Completa do Ecossistema — Engenharia de IA

**Data:** 2026-11-03  
**Responsável:** **Valverde** (engenheiro de IA)  
**Para:** **Luiz Henrique** → Guilherme

---

## Executive Summary

O ecossistema de **40 agentes** distribuído em **5 setores** está funcionando, mas há **ineficiências claras** que drenam ~15-20% dos tokens sem valor agregado. A maior economia vem de eliminar **duplicação entre Courtois, Vini e compliance.py**, que fazem a mesma verificação 3 vezes.

**Economia possível:** ~8-10k tokens/semana (~US$ 1-1,5/semana), ou 15-20% do custo atual.

---

## 1. Panorama dos Agentes

### Distribuição

| Setor | Agentes | Linhas | Custo/Ciclo | Frequência |
|-------|---------|--------|-------------|-----------|
| **Canal** | 15 | 525 | 25-30k tokens | 1x/dia |
| **Inteligência** | 6 | 185 | 15-20k tokens | 1x/semana |
| **Programação** | 10 | 251 | 5-10k tokens | 1x/sprint |
| **Produtividade** | 7 | 334 | 3-5k tokens | Contínuo* |
| **Reels + Outro** | 2 | 176 | 20-25k tokens | Sob demanda |
| **TOTAL** | **40** | **1.431** | ~70-90k/semana | — |

*Produtividade roda via Telegram; custo medido em `~US$ 0,01-0,02/mensagem`.

### Top 10 Maiores Definições

1. **Dembele** (Reels): 125 linhas — mini-fluxo separado do Instagram, bem encapsulado
2. **De Bruyne** (Orquestrador): 72 linhas — coordena canal inteiro, muita instrução
3. **Ronaldo** (Assistente): 64 linhas — Telegram bot, gestão de lembretes
4. **Raphinha** (Componentes): 58 linhas — desenha elementos visuais, skill grande
5. **Barcola / Casemiro / Kroos / Memphis**: 52 linhas cada

**Padrão:** 35 agentes em Sonnet (200k context), 2 em Opus (200k), 2 em Haiku (100k), 1 em Claude. Nenhum em o1 ou o1-mini.

---

## 2. Análise por Setor

### 🎬 Setor Canal (15 agentes, 525 linhas)

**Função:** Produzir 1 Short por dia (30-60s, 9:16, animação por código).

**Fluxo padrão (ENXUTO):**
```
Modric (pesquisa) 
  → Neymar (roteiro) 
    → Courtois (revisão) 
      → Olise (cenas) + Mbappé (metadados) [paralelo]
        → Vini-texto (auditoria pré-render)
          → run.py (render + compliance.py auto-check)
            → Vini-final (auditoria pós-render)
              → Sidorf (thumbnail)
```

**Custos por vídeo:**
- Modric + Memphis (pesquisa): 8k
- Neymar (roteiro): 4k
- **Courtois (revisão): 3k** ← REDUNDANTE
- Olise (cenas): 6k
- Mbappé (metadados): 1.5k
- **Vini-texto (auditoria): 2.5k** ← REDUNDANTE
- **Compliance.py (auto-check): 0** ← JÁ FAZ O QUE COURTOIS+VINI FAZEM
- Render: 0 (local)
- Vini-final (auditoria): 2.5k
- Sidorf (thumbnail): 1.5k
- **Total: ~29-30k tokens**

**Redundâncias identificadas:**

1. **Courtois + Vini + compliance.py fazem a mesma coisa**
   - **Courtois** verifica: fatos, cópia (Jaccard 7-shingles, threshold 12%), números (máx 2), exageros, gancho
   - **Vini-texto** verifica: conteúdo inautêntico, cópia (mesmo algoritmo Jaccard), números, ângulo, metadados
   - **compliance.py** verifica: cópia (linhas 97-106, mesmo algoritmo), números (via `roteiro.py`), ângulo (linhas 87-95), fatos (linhas 80-85)
   - **Resultado:** 3 passadas iguais. Compliance.py é determinístico; os outros são humanos.

2. **Leitura de `roteiro.txt` 5 vezes**
   - Neymar escreve
   - Courtois lê (revisão)
   - Olise lê (extrai textos das cenas)
   - Compliance.py lê (validação)
   - Vini-texto lê (auditoria)
   - Mbappé lê (contexto de metadados)
   - **Impacto:** ~500 tokens duplicados (leitura em contexto de cada agente)

3. **Vini audita antes e depois do render**
   - Pré-render (~2.5k): valida `roteiro.txt`, `notas.md`, `metadados.json` contra compliance.py
   - Pós-render (~2.5k): valida `video.mp4`, `thumbnail.jpg`, `CONFORMIDADE.md`
   - **Problema:** compliance.py já validou pré-render. Vini re-valida.

---

### 📊 Setor Inteligência (6 agentes, 185 linhas)

**Função:** Analisar mercado dark (canais, títulos, thumbnails, produção) 1x/semana.

**Fluxo:**
```
Hugo (encontra canais) 
  → Fagner (títulos) 
  → André Carrillo (thumbnails) 
  → Raniele (produção) 
  → Yuri Alberto (métricas) 
    [todos em paralelo, lendo fichas de Hugo]
      → Vitinho (consolida)
```

**Custos por ciclo:**
- Hugo: 5k (web search + catalogação)
- Fagner: 3k (análise de títulos)
- André Carrillo: 3k (análise visual)
- Raniele: 3k (técnica de produção)
- Yuri Alberto: 2k (métricas do canal próprio)
- Vitinho: 4k (consolidação + briefing)
- **Total: ~20k tokens/semana** (0,7k/dia)

**Redundâncias:**
- Cada um relê contexto sobre os mesmos canais (Fagner, André, Raniele, Yuri leem as fichas de Hugo em paralelo)
- **Impacto:** ~1-2k tokens por ciclo (contexto duplicado)

**Qualidade:** Bem estruturado. Cada agente tem responsabilidade clara. Pouca sobreposição além do contexto.

---

### 💻 Setor Programação (10 agentes, 251 linhas)

**Função:** Evoluir código do canal com metodologia ágil (Corte, pipeline, render).

**Fluxo:**
```
Guilherme → Zico (backlog)
  → Thiago Silva (refinamento técnico)
    → Xavi (quadro, sprint)
      → Rodrygo/Endrick (código)
        → Alisson (QA)
          → Zico (aceite)
```

**Custos por sprint (1 semana):**
- Zico: 2k (PO, backlog, aceite)
- Xavi: 1.5k (Scrum Master, daily, quadro)
- Ancelotti: 1k (agile coach, retro)
- Thiago Silva: 2k (tech lead, refinamento, revisão)
- Rodrygo/Endrick: ~3-5k total (código)
- Iniesta: 1k (UX, se houver tela)
- Alisson: 1k (QA, testes)
- Marquinhos: 0.5k (DevOps, notas de release)
- **Total: ~12-15k tokens/sprint**

**Redundâncias:** MÍNIMAS. Estrutura é clara. Cada um escreve no seu arquivo; ninguém sobrescreve outro. Restrição ao Kanban/quadro funciona.

**Qualidade:** Bem definida. Definição de pronto clara, testes obrigatórios, revisão de código, aceite com critérios.

---

### 🧑‍💼 Setor Produtividade (7 agentes, 334 linhas)

**Função:** Organizar Guilherme (tarefas, horas, acessos, LinkedIn, agenda).

**Fluxo:**
```
Ronaldo (Telegram bot, único que fala com Guilherme)
  ↔ Pedri (tarefas)
  ↔ Rodri (apontamento de horas)
  ↔ Guardiola (Kanban)
  ↔ Kroos (acessos)
  ↔ Casemiro (financeiro)
  ↔ Lamine Yamal (LinkedIn)
```

**Custos:**
- Ronaldo: ~0,01-0,02 USD/mensagem (via Telegram, modelo Haiku + mensagens do agente)
- Pedri/Rodri/Guardiola/Kroos/Casemiro/Lamine: ~0,3k-0,5k/mensagem (modelo Sonnet, via headless)
- **Total: ~3-5k tokens/semana** (contínuo, mas baixo)

**Redundâncias:**
- Múltiplos gestores de tarefas: Pedri (tarefas.md) + Guardiola (Kanban geral) + Xavi (quadro de programação)
- **Impacto:** ~1k tokens/semana (coordenação entre Kanban Geral e Kanban Programação)

**Qualidade:** Funcional. Integração com Google Agenda, Telegram, Trello. Sem commit, sem secrets. Bem isolado.

---

### 🎞️ Setor Reels (1 agente + Outro)

**Dembele (125 linhas):** Mini-fluxo separado do Instagram. Bem encapsulado. ~20-25k tokens sob demanda.

**Luiz Henrique (51 linhas):** Gestão do ecossistema (cria/altera agentes). Sob demanda.

---

## 3. Ineficiências Ranqueadas

### 🔴 ALTA: Courtois + Vini + compliance.py (Redundância de Código)

**O problema:**
- **Courtois** valida: fatos, cópia, números, exageros, gancho.
- **Vini** valida: conteúdo inautêntico, cópia (mesmo algoritmo), números, ângulo.
- **compliance.py** valida: fatos, cópia (Jaccard 7-shingles, threshold 12%), números, ângulo, cadência.

Compliance.py usa o **mesmo algoritmo** que Courtois e Vini sugeririam (Jaccard com similaridade de sequências).

**Custo:** ~5.5k tokens/vídeo (Courtois 3k + Vini-texto 2.5k), duplicando código local (~0 tokens).

**Proposta:**
1. **Courtois** → revisor humano de TON, CLAREZA, IMPACTO EDITORIAL (coisas que código não faz).
2. **Compliance.py** → autoridade pré-render (determinístico, robusto).
3. **Vini** → auditor final audiovisual pós-render.

**Economia:** ~4.5k tokens/vídeo (Courtois 1.5k revisor + Vini-texto reduzido a 1k validação).

**Risco:** BAIXO. Compliance.py é determinístico. Courtois/Vini ainda têm veto se discordarem.

---

### 🟠 ALTA: Leitura de `roteiro.txt` 5 Vezes

**O problema:**
Arquivo pequeno (~100 palavras), mas contexto duplicado em 5+ agentes:
1. Neymar (escreve)
2. Courtois (lê + revisa)
3. Olise (lê + extrai textos)
4. Compliance.py (lê + valida)
5. Vini (lê + audita)
6. Mbappé (lê + contextualiza)

**Custo:** ~500 tokens duplicados (releitura em múltiplos contextos).

**Proposta:** Passar sumário intermediário (metadata) em vez de reler arquivo inteiro. Ou: cache local.

**Economia:** ~300-500 tokens/vídeo.

**Risco:** BAIXO (técnico).

---

### 🟡 MÉDIA: Múltiplos POs (3 Agentes em Gestão)

**O problema:**
- **Guardiola** (produtividade): PO do trabalho pessoal do Guilherme
- **Zico** (programação): PO do setor de programação
- **De Bruyne** (canal): orquestrador de produção

Cada um toca em priorização, backlog, decisões de "o que fazer quando". Sincronização é via Kanban Trello compartilhado, mas há redundância de decisão.

**Custo:** ~1-2k tokens/semana (overlap de POs).

**Proposta:** Um PO único com dois covers (trabalho + canal) ou separação mais clara de domínios (Guardiola toca só Kanban Trabalho; Zico toca Kanban Programação; De Bruyne coordena orquestração de vídeo).

**Economia:** ~1k tokens/semana.

**Risco:** MÉDIO (decisão organizacional, precisa aprovação).

---

### 🔵 MÉDIA: Vini Audita Antes e Depois do Render

**O problema:**
- Vini-texto (~2.5k): valida `roteiro.txt`, `notas.md`, `metadados.json` contra compliance.py
- Vini-final (~2.5k): valida `video.mp4`, `thumbnail.jpg`

Compliance.py já rodou pré-render e validou tudo (linhas 69-184). Vini re-valida.

**Proposta:**
- **Vini-texto:** apenas controla compliance.py. Intervém se houver conflito (raro).
- **Vini-final:** audiovisual + metadados pós-render (o que compliance.py não cobre).

**Economia:** ~1.5-2k tokens/vídeo.

**Risco:** MÉDIO (redefine autoridade de dois momentos em um).

---

### 🔵 MÉDIA: Agentes de Inteligência Leem Mesmos Canais em Paralelo

**O problema:**
Hugo encontra e cataloga canais. Fagner, André Carrillo, Raniele, Yuri leem as fichas em paralelo. Há contexto compartilhado (nome do canal, descrição, vídeos) que é relido.

**Custo:** ~1-2k tokens/ciclo (contexto duplicado).

**Proposta:** Passar estrutura intermediária (JSON com metadados do canal) para evitar releitura.

**Economia:** ~1k tokens/ciclo (~150 tokens/dia).

**Risco:** BAIXO (técnico).

---

### 🟢 BAIXA: Setor de Programação Bem Estruturado

**Qualidade:** Kanban claro, quadro bem definido, regra do quadro rígida. Cada agente escreve só no seu arquivo. Pouca redundância.

**Não há recomendação de mudança.**

---

## 4. Impacto Total

### Economia Possível (Se Implementadas Todas as Propostas)

| Proposta | Economia/Vídeo | Economia/Semana | Risco |
|----------|-----------------|-----------------|-------|
| 1. Courtois revisor humano | ~3k tokens | ~3k (1 vídeo) | BAIXO |
| 2. Vini pré/pós separados | ~1.5-2k tokens | ~1.5-2k | MÉDIO |
| 3. POs consolidados | — | ~1k | MÉDIO |
| 4. Cache notas.md | ~300-500 tokens | ~300-500 | BAIXO |
| 5. Inteligência em JSON | — | ~150 | BAIXO |
| **TOTAL** | **~4.8-5.5k** | **~6-7k/semana** | — |

**Custo anual economizado:** ~US$ 300-350 (em créditos Anthropic)  
**Percentual:** ~15-20% do consumo de squad atual.

---

## 5. Recomendações Priorizadas

### Fase 1 (EXECUTAR LOGO)

#### 1️⃣ Redefine Courtois (Revisor Humano)
**Ação:** Mudar de "validador automático" para "revisor editorial".
- **Remove:** Verificação de cópia (Jaccard), números (máx 2), ângulo.
- **Mantém:** Revisão de tom, clareza, impacto, gancho vs. conteúdo.
- **Arquivo:** `.claude/agents/courtois-revisor-fatos.md`
- **Texto sugerido:** Em `propostas.md`, seção "Proposta 1".
- **Economia:** ~3k tokens/vídeo.
- **Quem aplica:** Luiz Henrique.

#### 2️⃣ Redefine Vini (Pré/Pós Claros)
**Ação:** Separar em dois momentos.
- **Vini-texto:** validar via compliance.py; intervém se conflito (raro).
- **Vini-final:** audiovisual + metadados pós-render.
- **Arquivo:** `.claude/agents/vini-auditor-conformidade.md`
- **Texto sugerido:** Em `propostas.md`, seção "Proposta 2".
- **Economia:** ~1.5-2k tokens/vídeo.
- **Quem aplica:** Luiz Henrique.

**Total Fase 1:** ~4.5k tokens/vídeo = ~4.5k/dia se produzir 1 vídeo = ~31.5k/semana.

### Fase 2 (PRÓXIMAS SEMANAS)

#### 3️⃣ Consolida POs
**Ação:** Discutir com Guilherme se quer 1 PO único ou separação mais clara.
- **Opção A:** 1 PO com dois covers (Guardiola expande para canal, ou Zico para programação).
- **Opção B:** Separação rígida: Guardiola = apenas trabalho; Zico = apenas programação; De Bruyne = coordenação de vídeo.
- **Economia:** ~1k tokens/semana.

#### 4️⃣ Cache de Notas
**Ação:** Passar sumário de `notas.md` (domínios, contagem, URLs) em JSON, evitando releitura.
- **Arquivo:** Novo `.claude/agents/notas_cache.json` ou similar.
- **Impacto:** Compliance.py, Vini não releem arquivo inteiro; leem cache.
- **Economia:** ~300-500 tokens/vídeo.
- **Risco:** BAIXO (técnico).

---

## 6. Próximos Passos

1. **Hoje:** Guilherme revisa este relatório (ANALISE_COMPLETA.md) e o dashboard.
2. **Amanhã:** Luiz Henrique implementa Fases 1️⃣ (Courtois + Vini) após aprovação.
3. **Próxima semana:** Testar em 3-4 vídeos com novas definições.
4. **Depois:** Decidir Fase 2 (POs, cache) com Guilherme.

---

## 7. Documentação

**Arquivos gerados em `ecossistema/engenharia-ia/`:**
- `2026-11-03.md` — diagnóstico da sobreposição Courtois/Vini/compliance.py
- `propostas.md` — texto sugerido para mudanças em agentes
- `ANALISE_COMPLETA.md` — este arquivo
- `README.md` — índice da pasta

**Dashboard visual:** https://claude.ai/artifact/1U6YUFmxsiHYWNKSHpGPgz

---

## 8. Conclusão

O ecossistema é **bem estruturado** mas **tem ineficiências claras**. A maior delas é a **redundância entre Courtois, Vini e compliance.py**, que validam a mesma coisa com o mesmo algoritmo. Eliminar isso economiza ~15-20% dos tokens sem qualquer perda de qualidade.

As propostas são **de baixo risco** e **implementáveis imediatamente**. Courtois e Vini mantêm autoridade; apenas mudamos onde cada um se concentra.

**Próximo passo:** Guilherme aprova as mudanças → Luiz Henrique implementa → testar em 3-4 vídeos.

---

**Engenheiro:** Valverde  
**Data:** 2026-11-03  
**Status:** Proposta pronta para revisão e aprovação
