# PROG-033c: Tela de Clipes (Visual H)

**Especificação de UX/Design**  
Data: 2026-11-12  
Autor: **Firmino** (curador de componentes visuais)  
Status: Proposta para implementação  

---

## 1. Visão geral

A tela de Clipes integra o setor no visual H do Ecossistema do Guilherme. Mostra a **lista de projetos de clipes** (entrada de vídeos de terceiros, triagem, edição, embalagem e aprovação), o **fluxo de agentes em tempo real** e **ações principais** (disparar novo projeto, abrir o painel 8767 do Clipes, baixar pacote).

**Diferenças do painel 8767:**
- O painel 8767 (`http://127.0.0.1:8767/`) é a **central de trabalho detalhada** dos agentes de Clipes (edição granular, ajuste de cortes, transcrição, momentos).
- A tela H é o **painel de gestão** para o Guilherme: ver status de projetos, aprovar Gates, saber o que está rodando, o que está parado.

**Cor do setor (visual H):** `#D9542D` (laranja-avermelhado) em slots e chips.

---

## 2. Estrutura da tela (layout)

### 2.1 Desktop (1280px +)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CABEÇALHO (Ilha)                                                            │
│  [Logo] Ecossistema do Guilherme | [Busca Ctrl K] | [S] [T] [?]           │
│  [1]Canal [2]Clipes [3]Inteligência [4]Trabalho [5]Finanças [6]Programação │
│  ✎ Esperam você: 3 | ● Rodando: Kaká, Zidane | ⚠ Erro: nenhum | $ hoje: US$0 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEÚDO (Clipes)                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PAINEL: CLIPES                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Setor de Clipes (Pelé)  📊 4 em andamento  ⏱ 2 esperando você    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─ AÇÕES PRINCIPAIS ────────────────────────────────────────────────────┐ │
│  │ [+ Novo projeto] [📊 Abrir painel 8767] [⬇ Downloads] [Baixar ZIP]  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ PROJETOS (Últimos 10 + busca) ──────────────────────────────────────┐ │
│  │ Filtro: [Todas] [Fazendo] [Esperando você] [Prontos] [Erro]         │ │
│  │ ┌────────────────────────────────────────────────────────────────┐  │ │
│  │ │ [clip-001] GTA 6 gameplay clip #1                  [Em corte]  │  │ │
│  │ │ Fonte: Flow Games FGN | Rivaldo: 87 | Pronto em: 1 dia        │  │ │
│  │ │ [Ver detalhes] [Abrir no 8767] [Download]                     │  │ │
│  │ └────────────────────────────────────────────────────────────────┘  │ │
│  │ ┌────────────────────────────────────────────────────────────────┐  │ │
│  │ │ [clip-002] React na votação do senado                [Esperando] │ │ │
│  │ │ BLOQUEIO: Você precisa aprovar o gancho/fecho            [Zidane] │ │ │
│  │ │ [Ver detalhes] [Editar] [Rejeitar] [Aprovar - A]               │ │ │
│  │ │ [Abrir no 8767] [Download]                                     │ │ │
│  │ └────────────────────────────────────────────────────────────────┘  │ │
│  │ ┌────────────────────────────────────────────────────────────────┐  │ │
│  │ │ [clip-003] Meme do TikTok                     [Esperando você] │  │ │
│  │ │ BLOQUEIO: Você precisa aprovar a embalagem final            [Lw] │ │ │
│  │ │ [Ver detalhes] [Revisar] [Aprovar - A] [Rejeitar]           │ │ │
│  │ │ [Abrir no 8767] [Download]                                     │ │ │
│  │ └────────────────────────────────────────────────────────────────┘  │ │
│  │ [...]                                                              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ FLUXO DO SETOR (Em paralelo ao lado esquerdo em 1600px+) ───────────┐ │
│  │ Clipes: de um vídeo longo a um pacote                               │ │
│  │                                                                      │ │
│  │  1️⃣  Fonte (Salah)                 [✓ ok]                           │ │
│  │  2️⃣  Autorização (você)             [✓ ok]                           │ │
│  │  3️⃣  Transcrição (Whisper local)    [✓ ok]                           │ │
│  │  4️⃣  Triagem (Rivaldo)              [● rodando 42%]                 │ │
│  │  5️⃣  Continuar mesmo assim (você)   [⏳ esperando]                   │ │
│  │  6️⃣  Momentos (perfil)              [⏳ esperando]                   │ │
│  │  7️⃣  Curadoria (Kaká)               [⏳ esperando]                   │ │
│  │  8️⃣  Gancho/fecho/CTA (Zidane)      [✓ ok]  ← estação atual         │ │
│  │  9️⃣  Aprovação de texto (você)      [⏳ esperando]                   │ │
│  │  🔟 Gancho de abertura (Figo)      [⏳ esperando]                   │ │
│  │  1️⃣1️⃣  Corte 9:16 (ffmpeg)          [⏳ esperando]                   │ │
│  │  1️⃣2️⃣  Potencial (Totti)            [⏳ esperando]                   │ │
│  │  1️⃣3️⃣  Originalidade (Buffon)       [⏳ esperando]                   │ │
│  │  1️⃣4️⃣  Embalagem (Lewandowski)      [⏳ esperando]                   │ │
│  │  1️⃣5️⃣  Aprovação final (você)       [⏳ esperando]                   │ │
│  │                                                                      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Dois layouts possíveis (breakpoint ~1600px):**

1. **Estreito (<1600px):** lista de projetos toma toda a largura; fluxo abaixo da lista em seção colapsável.
2. **Largo (≥1600px):** layout de colunas: lista à esquerda (60%), fluxo à direita (40%).

---

### 2.2 Mobile (390px)

```
┌──────────────────────────────┐
│ CABEÇALHO (Ilha compacta)   │
│ [=] Clipes (Pelé) | [?]     │
│ Esperando você: 3           │
└──────────────────────────────┘

┌──────────────────────────────┐
│ CONTEÚDO                     │
├──────────────────────────────┤
│ 4 em andamento ⏱ 2 espera   │
│                              │
│ [+ Novo] [Painel] [Baixar]  │
│                              │
│ Filtro: [Todas ▼]           │
│                              │
│ ┌────────────────────────┐   │
│ │ clip-001              │   │
│ │ GTA 6 gameplay        │   │
│ │ Rivaldo: 87           │   │
│ │ [Detalhe] [8767] [⬇] │   │
│ └────────────────────────┘   │
│ ┌────────────────────────┐   │
│ │ clip-002              │   │
│ │ React votação         │   │
│ │ 🔴 BLOQUEIO (Zidane)  │   │
│ │ [Editar] [Aprovar]    │   │
│ └────────────────────────┘   │
│                              │
│ [Carregar mais...]           │
│                              │
│ FLUXO ▼ (colapsável)         │
│ ┌────────────────────────┐   │
│ │ Etapa 7/15             │   │
│ │ Curadoria (Kaká)       │   │
│ │ ⏳ Esperando           │   │
│ └────────────────────────┘   │
│                              │
└──────────────────────────────┘
```

---

## 3. Componentes principais

### 3.1 Cabeçalho de setor

```
╔════════════════════════════════════════════╗
║ SETOR DE CLIPES (Pelé)                    ║
║ 📊 4 em andamento   ⏱ 2 esperando você    ║
║ ● Salah rodando (triagem em 42%)          ║
║ ⚠ 1 erro (fonte 003: acesso negado)       ║
╚════════════════════════════════════════════╝
```

**Elementos:**
- **Ícone + nome do setor + chefe:** `[Ícone Clipes] Clipes (Pelé)` em `#D9542D`
- **Métricas em linha:** 
  - `📊 4 em andamento` (projetos com status "fazendo" + "esperando você")
  - `⏱ 2 esperando você` (gates abertos)
  - `● X rodando` (agentes ativos)
  - `⚠ X erro` (projetos bloqueados por erro)

---

### 3.2 Barra de ações principais

```
╔════════════════════════════════════════════════════════════════╗
║ [+ Novo projeto]  [📊 Abrir painel 8767]  [⬇ Downloads]     ║
║ [📋 Baixar ZIP com pendentes]                                ║
╚════════════════════════════════════════════════════════════════╝
```

**Botões:**
- **+ Novo projeto:** abre modal com "URL do vídeo", "Criador", "Autorização", "Título opcional"
- **📊 Abrir painel 8767:** link externo para `http://127.0.0.1:8767` (abre aba nova)
- **⬇ Downloads:** dropdown com opções:
  - Baixar projeto selecionado (ZIP com MP4, JSON, metadados)
  - Baixar todos prontos (ZIP)
  - Baixar prontos por perfil (Geral / GTA 6)
- **📋 Baixar ZIP com pendentes:** botão secundário, agrupa todos os projetos "esperando você" em um ZIP

---

### 3.3 Filtro de status

```
╔════════════════════════════════════════════╗
║ Filtro: [Todas] [Fazendo] [Esperando] [Prontos] [Erro]
╚════════════════════════════════════════════╝
```

**Estados:**
- `Todas` (padrão)
- `Fazendo` (algum agente rodando)
- `Esperando você` (Gate aberto, Guilherme precisa decidir)
- `Prontos` (Aprovação final + download disponível)
- `Erro` (projeto travado por falha técnica)

---

### 3.4 Cartão de projeto

Cada projeto é um **cartão expansível** com:

```
┌─────────────────────────────────────────────────────────────┐
│ [ID] Título do projeto                    [Chip de status]  │
├─────────────────────────────────────────────────────────────┤
│ Fonte: [Criador] | Nota Rivaldo: [87] | Tempo: [1d 3h]      │
│                                                              │
│ ┌─ DETALHES (expandível) ─────────────────────────────────┐ │
│ │ Etapa atual: Gancho/Fecho/CTA (Zidane)                 │ │
│ │ Status: ✓ Aprovado pelo Guilherme                      │ │
│ │ Perfil: Geral                                          │ │
│ │ Momentos: 3 cortes propostos                           │ │
│ │ Cortes prontos: 2 (clip_001.mp4, clip_002.mp4)        │ │
│ │                                                         │ │
│ │ 🔗 Arquivo: clipes_out/clip-002/                      │ │
│ │ 📄 Estado: clipes_out/clip-002/estado.json            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─ AÇÕES ─────────────────────────────────────────────────┐ │
│ │ [Ver detalhes] [Abrir no painel 8767] [⬇ Download]    │ │
│ │ [Editar] [Aprovar] [Rejeitar] [Refazer] [Pausar]     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Estrutura por estado:**

#### Estado: **Fazendo** (agente rodando)
```
[clip-001] GTA 6 gameplay #1                  [● Rodando 42%]
Fonte: Flow Games | Rivaldo: 87 | Tempo: 1d 2h
Etapa atual: Triagem (Rivaldo) - 42% concluído
[Ver detalhes] [Abrir 8767] [Pausar]
```

#### Estado: **Esperando você** (Gate aberto)
```
[clip-002] React na votação                   [⏳ Espera sua decisão]
Fonte: Podcast XYZ | Rivaldo: 91 | Tempo: 2h 15m
BLOQUEIO: Você precisa aprovar o gancho e fecho (Zidane)
Zidane propõe:
  Gancho: "Reação viral ao resultado do senado"
  Fecho: "Siga para mais momentos assim"
  CTA: "Assista os clips completos no TikTok"
[Ver detalhes] [Editar gancho/fecho] [Aprovar ✓] [Rejeitar ✗]
```

#### Estado: **Pronto** (pronto para download)
```
[clip-003] Meme do TikTok                     [✓ Pronto]
Fonte: Creator X | Rivaldo: 79 | Tempo: 6h 30m
Aprovação final concluída. 2 cortes prontos.
Nota Totti: 82 (bom potencial)
[Ver detalhes] [Abrir 8767] [⬇ Download ZIP] [Publicar (manual)]
```

#### Estado: **Erro**
```
[clip-004] Vídeo deletado                     [⚠ Erro]
Fonte: YouTube (deletado) | Tempo: 3h
ERRO: Acesso negado. Vídeo não existe mais ou está privado.
[Tentar de novo] [Descartar] [Abrir no 8767]
```

---

### 3.5 Fluxo do setor (metrô)

**Versão expandida (desktop, 1600px+):**

```
╔════════════════════════════════════════════════════════════╗
║ FLUXO: Clipes (de um vídeo longo a um pacote)            ║
╠════════════════════════════════════════════════════════════╣
║                                                           ║
║ 1. Fonte (Salah)              [✓ ok]    [Avatar Salah]   ║
║    └─ Acha fontes e autorização                          ║
║                                                           ║
║ 2. Autorização (você)         [✓ ok]    [Avatar Você]    ║
║    └─ Gate: confirma autorização                         ║
║                                                           ║
║ 3. Transcrição (Whisper local) [✓ ok]   [Código]         ║
║    └─ Extrai o áudio do vídeo                            ║
║                                                           ║
║ 4. Triagem (Rivaldo)          [● 42%]   [Avatar Rivaldo] ║
║    └─ Avalia o potencial da fonte                        ║
║    PROGRESSO: Processando transcrição...                 ║
║                                                           ║
║ 5. Continuar mesmo assim (você) [⏳]    [Avatar Você]    ║
║    └─ Gate: se Rivaldo der nota baixa                    ║
║                                                           ║
║ 6. Momentos (perfil)          [⏳]      [Código]          ║
║    └─ Seleciona os melhores trechos                      ║
║                                                           ║
║ 7. Curadoria (Kaká)           [⏳]      [Avatar Kaká]    ║
║    └─ Escolhe os cortes que funcionam sozinhos           ║
║                                                           ║
║ 8. Gancho/fecho/CTA (Zidane)  [✓ ok]   [Avatar Zidane]  ║
║    └─ Escreve comentário próprio                         ║
║                                                           ║
║ ... (mais 7 etapas)                                      ║
║                                                           ║
║ 15. Aprovação final (você)    [⏳]      [Avatar Você]    ║
║     └─ Gate: pronto para baixar e publicar               ║
║                                                           ║
╚════════════════════════════════════════════════════════════╝
```

**Versão compacta (mobile):**

```
Etapa atual: 4 de 15
Triagem (Rivaldo) - ● Rodando 42%

[⬆ Anterior] [Próxima ⬇]
[Expandir fluxo completo]
```

---

## 4. Interações e estados

### 4.1 Estados da tela

| Estado | Descrição | O que mostrar |
|---|---|---|
| **Vazio** | Nenhum projeto | Ilustração "prancheta vazia + +" (asset do H), botão "+ Novo projeto", explicação "Você ainda não iniciou nenhum projeto de clipes" |
| **Carregando** | Primeiro carregamento da lista | Esqueleto (5 cartões cinza pulsantes), mensagem "Carregando projetos..." |
| **Normal** | Com projetos | Lista de cartões, filtro ativo, fluxo colapsável |
| **Erro** | API do Clipes indisponível | Ilustração "tomada desconectada" (asset do H), "A interface de Clipes não respondeu. Verifique se `python -m clipes painel` está rodando em `http://127.0.0.1:8767`" |
| **Carregando projeto** | Um cartão sendo carregado | Barra de progresso dentro do cartão |
| **Atualização ao vivo** | SSE novo evento | Verde/amarelo piscante por 1.5s (estado trocou), depois volta ao normal |

### 4.2 Atalhos de teclado

- `Ctrl K` ou `Cmd K`: buscar projeto (filtra por ID, título, criador)
- `N`: novo projeto (abre modal)
- `F`: alternar filtro (cicla: Todas → Fazendo → Esperando → Prontos → Erro → Todas)
- `A`: aprovar projeto selecionado (só se em estado "Esperando você")
- `R`: rejeitar / refazer (só se em estado "Esperando você" ou "Erro")
- `1` a `5`: alternar filtro diretamente (Todas, Fazendo, Esperando, Prontos, Erro)
- `J` / `K`: navegação anterior/próximo projeto (estilo H)

---

## 5. Responsividade

### 5.1 Breakpoints

| Breakpoint | Viewport | Layout | Mudanças |
|---|---|---|---|
| **Mobile** | 320–599px | Stack vertical | Barra ações reduzida a ícones |
| **Tablet** | 600–1199px | Stack vertical | Ações em linha, cartões mais largos |
| **Desktop** | 1200–1599px | Stack (lista toma 100%) | Fluxo em seção colapsável abaixo |
| **Grande** | 1600px+ | Colunas (60/40) | Lista esquerda, fluxo direita |

### 5.2 Ajustes por tamanho

**Mobile (390px):**
- Cabeçalho: nome do setor + 1 métrica (esperando você), resto em tooltip
- Barra de ações: stack em 2 linhas, ícones + label curto
- Cartão: título + nota Rivaldo, detalhes colapsáveis
- Filtro: dropdown em vez de botões
- Fluxo: colapsável, mostra só etapa atual

**Desktop (1280px):**
- Cabeçalho: nome + todas as métricas em linha
- Cartão: completo, com ações visíveis
- Fluxo ao lado (se 1600px+) ou abaixo (tab colapsável se <1600px)

---

## 6. Integração com dados

### 6.1 Fonte de dados

Dados vêm de `clipes_out/<slug>/estado.json` (mesmo do painel 8767):

```json
{
  "slug": "clip-002",
  "titulo": "React na votação do senado",
  "fonte": {
    "url": "https://youtube.com/watch?v=ABC",
    "criador": "Podcast XYZ",
    "autorizacao": "permissao",
    "prova": "email do criador"
  },
  "etapa_atual": "coment",
  "etapa_nome": "Gancho/fecho/CTA",
  "agente_nome": "Zidane",
  "status": "esperando_voce",
  "notas": { "rivaldo": 91, "totti": 82 },
  "tempo_inicio": "2026-11-11T10:00:00Z",
  "cortes_prontos": 2,
  "propostas": {
    "gancho": "Reação viral ao resultado do senado",
    "fecho": "Siga para mais momentos assim",
    "cta": "Assista os clips completos no TikTok"
  }
}
```

### 6.2 Atualização em tempo real

Conectar a SSE do painel 8767 em `/api/eventos`:

```javascript
const sse = new EventSource("http://127.0.0.1:8767/api/eventos");
sse.onmessage = (e) => {
  const evento = JSON.parse(e.data);
  // evento.slug, evento.novo_status, evento.agente, evento.progresso
  atualizar_cartao(evento.slug);
};
```

---

## 7. Casos de uso principais

### Use case 1: Disparar novo projeto

1. Usuário clica "+ Novo projeto"
2. Modal abre com campos:
   - URL do vídeo (YouTube, Vimeo, arquivo local)
   - Criador (texto livre)
   - Autorização: [dropdown] livre / próprio / parceria / permissão / licença / teste
   - Prova (URL de e-mail ou DM, opcional se "livre")
   - Título (opcional, padrão = "Sem título")
   - Perfil: [dropdown] Geral / GTA 6
3. Usuário clica "Disparar"
4. Modal fecha, cartão do novo projeto aparece no topo da lista com status "Carregando"
5. Background: `python -m clipes tudo <URL> ...` começa

---

### Use case 2: Aprovar gancho/fecho

1. Cartão mostra "⏳ Esperando sua decisão" (Zidane)
2. Usuário vê as propostas (gancho, fecho, CTA)
3. Usuário clica "[Editar gancho/fecho]" para mudar (abre campo de texto inline)
4. Usuário clica "[Aprovar ✓]" (ou `A`)
5. Cartão atualiza para "✓ Aprovado", cor verde, próximo agente (Figo) já começa

---

### Use case 3: Revisar embalagem final

1. Cartão mostra "⏳ Esperando sua decisão" (Lewandowski)
2. Usuário vê propostas para Instagram e TikTok (descrição, hashtags, legenda)
3. Usuário clica "[Revisar]" → abre modal com:
   - Aba "Instagram Reels"
   - Aba "TikTok"
   - Preview do vídeo (src=`clipes_out/<slug>/NN.mp4`)
4. Usuário edita ou aprova
5. "[Aprovar ✓]" (ou `A`) → próximo é Gates, depois download

---

## 8. Wireframe narrativo (versão texto)

### Desktop (1280px)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🖥 Ecossistema do Guilherme (1280px desktop, modo claro)     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ CABEÇALHO ILHA                                              ┃
┃ [Logo] Ecossistema | [Busca...] | [S] [T] [?]              ┃
┃ [1 Canal] [2 Clipes] [3 Inteligência]...                   ┃
┃ ⏳ Esperando: 3 | ● Rodando: Kaká, Zidane | $ Hoje: US$ 0  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┃                                                             ┃
┃ CLIQUES: SETOR                                              ┃
┃ ┌─────────────────────────┐       ┌────────────────────┐  ┃
┃ │ 📊 Clipes (Pelé)        │       │ FLUXO DO SETOR     │  ┃
┃ │ 4 fazendo ⏱ 2 espera    │       │ 1. Fonte ✓         │  ┃
┃ │ ● Salah (42%)           │       │ 2. Autori. ✓       │  ┃
┃ │ ⚠ 1 erro               │       │ 3. Transc. ✓       │  ┃
┃ └─────────────────────────┘       │ 4. Triagem ● 42%   │  ┃
┃                                   │ 5. Continuar ⏳    │  ┃
┃ [+ Novo] [📊 8767] [⬇] [ZIP]    │ 6. Momentos ⏳     │  ┃
┃                                   │ ... (9 mais)       │  ┃
┃ [Filtro: Todas ▼]                │ 15. Aprovação ⏳   │  ┃
┃                                   └────────────────────┘  ┃
┃ ┌─────────────────────────────────────────────────────┐   ┃
┃ │ [clip-001]                           [● 42%]        │   ┃
┃ │ GTA 6 gameplay #1                                   │   ┃
┃ │ Fonte: Flow Games | Rivaldo: 87 | 1d 2h            │   ┃
┃ │ Triagem (Salah) - ● rodando                        │   ┃
┃ │ [Detalhe] [8767] [⬇] [Pausar]                      │   ┃
┃ └─────────────────────────────────────────────────────┘   ┃
┃                                                             ┃
┃ ┌─────────────────────────────────────────────────────┐   ┃
┃ │ [clip-002]                      [⏳ Espera você]    │   ┃
┃ │ React na votação do senado                          │   ┃
┃ │ Fonte: Podcast XYZ | Rivaldo: 91 | 2h 15m          │   ┃
┃ │                                                      │   ┃
┃ │ VOCÊ PRECISA: Aprovar gancho/fecho (Zidane)        │   ┃
┃ │ Gancho: "Reação viral ao resultado"                │   ┃
┃ │ Fecho: "Siga para mais momentos"                   │   ┃
┃ │ CTA: "Assista os clips no TikTok"                  │   ┃
┃ │                                                      │   ┃
┃ │ [Editar] [Aprovar ✓] [Rejeitar] [8767] [⬇]         │   ┃
┃ └─────────────────────────────────────────────────────┘   ┃
┃                                                             ┃
┃ ┌─────────────────────────────────────────────────────┐   ┃
┃ │ [clip-003]                        [✓ Pronto]        │   ┃
┃ │ Meme do TikTok                                       │   ┃
┃ │ Fonte: Creator X | Rivaldo: 79 | 6h 30m            │   ┃
┃ │ 2 cortes prontos. Nota Totti: 82 (bom potencial)   │   ┃
┃ │ [Detalhe] [8767] [⬇ ZIP] [Publicar (manual)]        │   ┃
┃ └─────────────────────────────────────────────────────┘   ┃
┃                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Mobile (390px)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📱 Mobile (390px)            ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ [=] Clipes (Pelé) | [?]      ┃
┃ ⏳ Espera você: 3            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┃                              ┃
┃ 4 fazendo | ⏱ 2 espera     ┃
┃ ● Salah 42%                 ┃
┃                              ┃
┃ [+ Novo] [📊] [⬇] [ZIP]    ┃
┃                              ┃
┃ Filtro: [Todas ▼]          ┃
┃                              ┃
┃ ┌────────────────────────┐  ┃
┃ │ clip-001              │  ┃
┃ │ GTA 6 gameplay        │  ┃
┃ │ Rivaldo: 87           │  ┃
┃ │ ● 42% (Triagem)       │  ┃
┃ │ [Mais] [8767] [⬇]     │  ┃
┃ └────────────────────────┘  ┃
┃                              ┃
┃ ┌────────────────────────┐  ┃
┃ │ clip-002              │  ┃
┃ │ React votação         │  ┃
┃ │ Rivaldo: 91           │  ┃
┃ │ 🔴 Espera: Zidane     │  ┃
┃ │ [Editar] [Aprovar ✓]  │  ┃
┃ │ [8767] [⬇]            │  ┃
┃ └────────────────────────┘  ┃
┃                              ┃
┃ FLUXO ▼                      ┃
┃ ┌────────────────────────┐  ┃
┃ │ Etapa 8/15             │  ┃
┃ │ Gancho/fecho (Zidane)  │  ┃
┃ │ ✓ Aprovado            │  ┃
┃ │ [Próxima etapa]        │  ┃
┃ └────────────────────────┘  ┃
┃                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 9. Checklist de implementação

- [ ] **Endrick** (dev front): estrutura HTML/CSS base
- [ ] **Endrick**: lista de projetos com scroll infinito
- [ ] **Endrick**: filtro e busca
- [ ] **Endrick**: cartões com estados (fazendo, esperando, pronto, erro)
- [ ] **Endrick**: barra de ações principais
- [ ] **Rodrygo** (dev back): endpoint GET `/api/clipes/lista` (lista projetos com estado)
- [ ] **Rodrygo**: endpoint POST `/api/clipes/novo` (dispara novo projeto)
- [ ] **Rodrygo**: SSE `/api/eventos` (atualização ao vivo)
- [ ] **Iniesta** (UX): revisar responsividade em 3 tamanhos
- [ ] **Alisson** (QA): testar filtros, atalhos, estados
- [ ] **Alisson**: testar integração com painel 8767
- [ ] **Alisson**: teste de performance (lista com 100+ projetos)

---

## 10. Notas para o **Endrick** (dev front)

1. **Layout:** use CSS Grid para a coluna dupla (>1600px), Grid ou Flexbox para mobile
2. **Temas:** herdar variáveis CSS do H (`--card`, `--tx`, `--aprovva`, etc.)
3. **Ícones:** usar `GH.ico()` do `base.js` para status, avatares com `GH.av()`
4. **Filtro:** estado no URL (`?filtro=fazendo`) para compartilhar
5. **Atalhos:** usar o mesmo roteador do H (Ctrl K para busca, J/K para navegação)
6. **Slots de assets:** usar `GH.slot()` para avatares do Pelé, Salah, etc.
7. **SSE:** reconnect automático se cair, fallback para polling a cada 3s
8. **Busca:** cliente (não servidor) se lista <500 itens, senão paginar

---

## 11. Notas para o **Rodrygo** (dev back)

1. **Dados:** ler de `clipes_out/*/estado.json`, agregar com `estado.json`
2. **Novo projeto:** integrar com `python -m clipes tudo <URL> ...` via subprocess
3. **SSE:** para cada mudança em `estado.json`, publicar evento para todos os clientes conectados
4. **Autorização:** só o Guilherme (via `ronaldo-assistente` ou `debruyne-orquestrador`) pode disparar
5. **Rate limit:** 1 novo projeto por minuto (evita spam)

---

## 12. Design system (cores, ícones, estados)

| Elemento | Cor | Ícone | Exemplo |
|---|---|---|---|
| Setor Clipes | `#D9542D` | 🎬 | backgrounds, chips |
| Status OK | `#1FBF8A` (claro) / `#3DDC97` (escuro) | ✓ | "Aprovado", "Pronto" |
| Status Erro | `#C4301D` (claro) / `#FF7B6E` (escuro) | ⚠ | "Erro", "Falhou" |
| Status Pendente | `#9A5B00` (claro) / `#FFC247` (escuro) | ⏳ | "Esperando você" |
| Status Rodando | `#1560D6` (claro) / `#62B2FF` (escuro) | ● | "Triagem 42%" |
| Status Backlog | `#546B78` (claro) / `#93ABB9` (escuro) | ◯ | próximas etapas |

---

## 13. Exemplos de propostas do Guilherme

Se o Guilherme disser:
- *"Clipes só em um aba, sem fluxo aqui"* → esconder o fluxo, abrir em novo painel 8767
- *"Mostrar só projetos deste mês"* → adicionar filtro de data
- *"Ordenar por nota do Rivaldo"* → coluna clicável para sort
- *"Só móvel, sem desktop"* → design mobile-first, desktop é responsivo para 1280+
- *"Integrar com o painel local do Ronaldo"* → adicionar cartão Clipes em `produtividade/painel.html`

---

**Próximos passos:**
1. Guilherme aprova este design
2. **Iniesta** refina estados e transições
3. **Endrick** implementa estrutura HTML/CSS
4. **Rodrygo** implementa APIs
5. **Alisson** testa e valida

---

*Documento finalizado: 2026-11-12*
