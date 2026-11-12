# Diagnóstico de Espaço em Disco — canal-dark
**Data:** 2026-11-04  
**Total do projeto:** 4.66 GB  
**Coordenação:** De Bruyne (orquestrador), Valverde (engenheiro de IA), Luiz Henrique (ecossistema)

---

## 1. BREAKDOWN POR DIRETÓRIO PRINCIPAL

| Pasta | Tamanho | Tipo | Essencialidade |
|-------|---------|------|---|
| `.venv-voz` | 2.00 GB | Ambiente Python (PyTorch, TTS) | **Regenerável** |
| `.venv` | 0.52 GB | Ambiente Python (deps) | **Regenerável** |
| `output/` | 1.11 GB | Vídeos + metadados de produção | **Misto: vídeos finais=essencial; intermediários=lixo** |
| `reels/` | 0.49 GB | Projetos de Reels (outro Instagram) | **Questionável: inativo?** |
| `models/` | 0.11 GB | Modelos de IA (Kokoro TTS, voices) | **Essencial para render** |
| `estudio/` | 0.21 GB | DB do editor visual (blobs) | **Questionável: cópia do video.mp4?** |
| `render/node_modules` | 0.037 GB | npm packages (renderer) | **Regenerável** |
| `tiktok/`, `videos-kane/`, `render3d/` | 0.17 GB | Projetos secundários/descontinuados | **Questionável** |

**Subtotal regenerável:** ~2.6 GB  
**Subtotal essencial:** ~1.5 GB  
**Subtotal questionável:** ~0.56 GB

---

## 2. DENTRO DE `output/` — O MAIOR CONSUMIDOR VIVO

### 2.1 Vídeos Principais (mantém)
- `a-erupcao-do-krakatoa-em-1883` — 246.7 MB (demo, pode apagar)
- `companhias-de-ia-entre-adolescentes-amizade-entretenimento-o` — 138.3 MB (video final) ✓
- `todos_os_videos` — 133.5 MB (cópia consolidada?)
- `por-que-toda-geracao-acha-que-a-proxima-e-mais-mimada` — 40.1 MB ✓
- `quem-lucra-com-polarizacao-gen-z-vs-boomers` — 36.9 MB ✓

### 2.2 Arquivos Intermediários (LIXO ÓBVIO)
```
output/*/clips/joined.mp4  (~150 MB total)
```
- `a-erupcao-do-krakatoa-em-1883/clips/joined.mp4` — 82 MB
- Outros 7 slugs — ~68 MB
- **Tipo:** Resultado intermediário da junção de clips durante o render
- **Pode apagar?** **SIM** — o `video.mp4` final é o que importa

### 2.3 Estrutura Típica de um Slug
```
slug/
  ├── notas.md (essencial: fontes)
  ├── angulo.md (essencial: tese)
  ├── roteiro.txt (essencial: congelado após auditoria)
  ├── cenas.json (essencial: descrição de cenas)
  ├── metadados.json (essencial: título/tags)
  ├── sketch_cenas.py (essencial: código de desenho para sketch)
  ├── video.mp4 (essencial: vídeo final, 70-100 MB)
  ├── thumbnail.jpg (essencial: miniatura)
  ├── audio.wav (essencial: narração, 15-20 MB)
  ├── PUBLICAR.txt (útil: checklist)
  ├── CONFORMIDADE.md (útil: auditoria)
  ├── custo.json (útil: billing)
  ├── eventos.json (útil: timeline)
  ├── revisao.md (útil: notas humanas)
  ├── auditoria.md (útil: aprovação final)
  ├── auditoria_texto.md (útil: aprovação de texto)
  └── clips/ ← **AQUI FICA O LIXO**
      └── joined.mp4 (intermediário, pode apagar)
```

---

## 3. ANÁLISE POR PERSPECTIVA

### 3.1 **De Bruyne (Técnico)**
**Padrões de Lixo Identificados:**

1. **Arquivos intermediários de render** (150 MB)
   - `output/*/clips/joined.mp4` — clips juntados durante o encode, não são usados depois
   - `estudio/dados/blobs/` — pode conter cópias antigas do video.mp4?

2. **Ambientes Python virgens** (2.52 GB)
   - `.venv` e `.venv-voz` — regeneráveis com `pip install -r requirements.txt`
   - Não devem estar versionados (`gitignore` está ativo?)

3. **node_modules** (37 MB)
   - `render/node_modules` — regenerável com `npm install`

4. **Projetos inativos ou em outro escopo** (0.56 GB)
   - `reels/` (Reels de outro Instagram, não o canal dark)
   - `tiktok/`, `render3d/`, `videos-kane/` — manutenção não especificada em CLAUDE.md
   - `exemplo/` (demo técnica, só prova de conceito)

### 3.2 **Valverde (Engenheiro de IA)**
**Consumo de Recurso (Tokens + Disco)**

A **questão principal**: `.venv-voz` (2 GB) é usado **uma única vez** por render (TTS e voz), mas consome **25% do espaço do projeto**. 

**O que faz sentido reduzir:**
- **Ambiente de voz**: talvez rodar apenas quando necessário (criar o `.venv-voz` sob demanda, não guardar).
- **Modelos grandes**: `kokoro-v1.0.int8.onnx` (88 MB) e `voices-v1.0.bin` (26.9 MB) — são **essenciais**, mas considerar se estão otimizados (quantized).
- **Arquivos intermediários de render**: `joined.mp4` (150 MB) — são **à toa**, não faz sentido guardar.

**Consumo de IA no fluxo**: nenhuma relação — os agentes escrevem de graça, o custo pago (`--allow-paid`) é ínfimo. O espaço é disk, não token.

### 3.3 **Luiz Henrique (Ecossistema)**
**Essencialidade Estrutural**

**Essencial (não tocar):**
- `output/<slug>/` — vídeos finalizados e metadados do canal
- `.claude/agents/` — definição da squad
- `media/`, `render/`, `prompts/` — pipeline de produção
- `config_shorts.yaml` — configuração do canal
- `models/` — modelos de IA para render e TTS

**Questionável (depende da estratégia):**
- `reels/` — é ativo? Se o setor de Reels parou, pode arquivar externo e deletar local
- `tiktok/` — TikTok integrado ao projeto? Ou era teste?
- `estudio/` — banco de dados visual. Se tiver vídeos importantes armazenados lá, manter; senão, pode limpar
- Projetos de "setor de ação" ainda não lançado: `produtividade/`, `financas/`, `programacao/` — vazios, não ocupam espaço mas podem ser deixados

**Estrutura saudável**: projeto não deveria ter 4 GB de ambiente Python. Ambientes devem ser regenerados do `requirements.txt`, não versionados.

---

## 4. CANDIDATOS A LIMPEZA (POR PRIORIDADE)

### 🔴 **PRIORIDADE ALTA** — Apagar com segurança
- `output/*/clips/joined.mp4` (~150 MB) — intermediários de render, nunca reutilizados
- `exemplo/` — demo técnica apenas (~200 MB se houver vídeos lá)
- `.codex/` — se está sincronizado e `.claude/agents/` é o primário, considerar deletar (0.1 MB, mínimo)

**Liberação estimada:** ~350 MB

### 🟡 **PRIORIDADE MÉDIA** — Avaliar com Guilherme
- `.venv` e `.venv-voz` (~2.5 GB) — regeneráveis, mas conveniente manter? Ou criar sob demanda?
- `reels/` (~0.49 GB) — ativo ainda? Se não, arquivar em HD externo e deletar
- `estudio/dados/blobs/` — contém cópias antigas de `video.mp4`? Se sim, apagar; se for DB único, manter
- `tiktok/`, `render3d/` (~0.17 GB) — projetos secundários vivos ou descontinuados?

**Liberação estimada se tudo:** ~3 GB; se conservador (só .venv-voz): ~2 GB

### 🟢 **PRIORIDADE BAIXA** — Manter
- `output/<slug>/` — vídeos finalizados
- `models/`, `media/`, `render/`, `.claude/agents/` — pipeline essencial
- `config_shorts.yaml`, `CLAUDE.md` — configuração do projeto

---

## 5. PERGUNTAS PARA O GUILHERME

1. **Os ambientes Python (`.venv`, `.venv-voz`) devem ser regenerados do zero, ou é melhor manter pré-compilado?**
   - Caso A: Deletar, regenerar com `pip install -r requirements.txt` (libera 2.5 GB imediatos, mas recompila na próxima execução)
   - Caso B: Manter, por comodidade (mantém 2.5 GB)

2. **`reels/` e `tiktok/` ainda estão ativos?**
   - Sim: manter
   - Não: arquivar em HD externo ou cloud, deletar local (libera ~0.65 GB)

3. **`estudio/dados/blobs/` — são cópias redundantes do `video.mp4`, ou dados do editor que precisam?**
   - Se redundantes: deletar (libera ~200 MB)
   - Se essenciais: manter

4. **`exemplo/` — teste que pode ser descartado?**
   - Sim: deletar (libera ~250 MB)
   - Não: manter por referência

---

## RESUMO EXECUTIVO

| Cenário | Ação | Liberação |
|---------|------|-----------|
| **Agressivo** | Apagar intermediários + .venv + reels + tiktok + estudio blobs + exemplo | ~3.2 GB |
| **Moderado** | Apagar intermediários + exemplo + limpeza no estudio | ~0.6 GB |
| **Conservador** | Apagar só intermediários + .codex | ~0.15 GB |

**Recomendação De Bruyne + Valverde + Luiz Henrique:** Comece pelo **agressivo em ambientes** (`.venv` e `.venv-voz` regeneráveis) e **intermediários de render** (joined.mp4). Isso libera ~2.65 GB com zero impacto operacional. Depois, valide `reels/`, `tiktok/` e `estudio/` com o Guilherme.

---

**Próximo passo:** Guilherme aprova a limpeza, e a gente rodas os comandos de delete sem risco.
