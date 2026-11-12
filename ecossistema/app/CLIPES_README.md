# Tela de Clipes (PROG-033c)

## Implementação

A tela de Clipes foi implementada seguindo a especificação de UX do Firmino (PROG-033c.md).

### Arquivos criados

1. **`clipes.js`** (269 linhas)
   - Estado local: filtro, selecionado, tema, projetos
   - Fetch via `/api/clipes` com fallback para `clipes_demo.json`
   - SSE listener em `/api/eventos` (atualização em tempo real)
   - Render de: cabeçalho com menu + lista com filtro e busca
   - Ações: novo projeto, abrir painel 8767, aprovar, rejeitar
   - Atalhos de teclado: Ctrl K, N, A, R, F, J/K, 1-5

2. **`clipes.css`** (102 linhas)
   - Integrado ao visual H (variáveis CSS do design system)
   - Responsivo: mobile, tablet, desktop (1600px+)
   - Estados: carregando, vazio, erro, ok

3. **`clipes_demo.json`** 
   - Dados de teste com 4 projetos em diferentes estados
   - Usado como fallback quando `/api/clipes` não está disponível

4. **`index.html`** (atualizado)
   - Router para carregar `clipes.js` ou `financas.js` baseado em `location.hash`
   - Suporta navegação entre abas via menu na ilha

### Estados da tela

| Estado | Descrição | O que mostra |
|---|---|---|
| **Carregando** | Fetch em progresso | "Carregando projetos..." |
| **Vazio** | Nenhum projeto | Ilustração + botão "+ Novo Projeto" |
| **Erro** | API indisponível | Mensagem de erro + instruções |
| **Pronto** | Com projetos | Lista com filtro, busca e cartões |

### Atalhos de teclado

- `Ctrl K` ou `Cmd K`: Focar busca
- `N`: Novo projeto (modal)
- `F`: Alternar filtro (cicla entre Todas, Fazendo, Esperando você, Prontos, Erro)
- `A`: Aprovar projeto selecionado (se em estado "Esperando você")
- `R`: Rejeitar / refazer (se em estado "Esperando você" ou "Erro")
- `1` a `5`: Alternar filtro diretamente (Todas=1, Fazendo=2, Esperando=3, Prontos=4, Erro=5)
- `J` / `K`: Navegação anterior/próximo projeto (estilo H)

### Filtros

- **Todas**: mostra todos os projetos
- **Fazendo**: apenas projetos com agente rodando
- **Esperando você**: projetos com gate aberto (bloqueio para aprovação)
- **Prontos**: projetos com aprovação final concluída
- **Erro**: projetos travados por falha técnica

### Busca

Filtra por:
- ID do projeto (slug)
- Título
- Criador (fonte)

### Como testar

#### 1. Com dados de demo (sem servidor)

```bash
# Abrir no navegador:
# file:///caminho/para/ecossistema/app/index.html#clipes
```

A tela carregará `clipes_demo.json` automaticamente (fallback).

#### 2. Com API local (com servidor)

```bash
# Em outro terminal, rodar:
python -m http.server 8000 --directory ecossistema/app

# Abrir:
# http://localhost:8000/index.html#clipes
```

Para que a API funcione, é necessário que `/api/clipes` retorne JSON com a estrutura:

```json
{
  "projetos": [
    {
      "slug": "clip-001",
      "titulo": "Título do projeto",
      "status": "fazendo|esperando_voce|prontos|erro",
      "fonte": { "criador": "...", "url": "..." },
      "etapa_atual": "...",
      "etapa_nome": "...",
      "agente_nome": "...",
      "notas": { "rivaldo": 87 },
      "tempo_inicio": "2026-11-11T10:00:00Z",
      "cortes_prontos": 0
    }
  ]
}
```

#### 3. SSE (atualização em tempo real)

Se `/api/eventos` estiver disponível, a tela se conectará e renderizará atualizações em tempo real:

```javascript
const sse = new EventSource("/api/eventos");
sse.onmessage = (e) => {
  const evento = JSON.parse(e.data);
  // evento.slug, evento.novo_status, evento.agente, evento.progresso
};
```

### Funcionalidades não implementadas (próximos passos)

- Modal de novo projeto (POST `/api/clipes/novo`)
- Downloads e ZIP
- Fluxo do setor (metrô das etapas)
- Edição de propostas (gancho/fecho/CTA)
- Detalhes expandidos do cartão

### Integração com Rodrygo (dev back)

Endpoints necessários:

1. **GET `/api/clipes`**
   - Retorna lista de projetos com estado
   - Lê de `clipes_out/*/estado.json`

2. **POST `/api/clipes/novo`**
   - URL, criador, autorização, título, perfil
   - Dispara `python -m clipes tudo <URL> ...`

3. **SSE `/api/eventos`**
   - Para cada mudança em `estado.json`, publica evento para todos os clientes
   - Evento: `{ slug, novo_status, agente, progresso }`

### Design responsivo

- **Mobile (320–599px)**: Stack vertical, ícones na barra de ações, dropdown de filtro
- **Tablet (600–1199px)**: Stack vertical, ações em linha, cartões mais largos
- **Desktop (1200–1599px)**: Stack (lista toma 100%), fluxo em seção colapsável
- **Grande (1600px+)**: Colunas (lista 60%, fluxo 40%, lado a lado)

### Cores do setor (visual H)

- **Setor Clipes**: `#D9542D` (laranja-avermelhado)
- **Status OK**: `--c-ok` (verde)
- **Status Erro**: `--c-erro` (vermelho)
- **Status Pendente**: `--c-pendente` (amarelo)
- **Status Rodando**: `--c-rodando` (azul)

### Temas

A tela suporta tema claro (padrão) e escuro. O botão na ilha alterna entre eles.

Persistência:
- Filtro salvo em `localStorage` (chave: `ce_h_cli_filtro`)
- Tema salvo em `localStorage` (chave: `ce_h_cli_tema`)
- Projeto selecionado salvo em `localStorage` (chave: `ce_h_cli_selec`)

---

**Próximos passos:**
1. **Rodrygo** implementa endpoints (`/api/clipes`, `/api/clipes/novo`, `/api/eventos`)
2. **Iniesta** refina estados e transições de UX
3. **Alisson** testa filtros, atalhos, estados, integração com painel 8767

---

**Pronto para testar em `http://localhost/index.html#clipes`**
