# Proposta: Dashboard de Orquestração do Ecossistema para Ronaldo

**Diagóstico por:** **Valverde** (`valverde-engenheiro-ia`)  
**Data:** 2026-11-04  
**Status:** Proposta em refinamento  
**Prioridade sugerida:** Média (suporte operacional; não bloqueia o canal)  
**Estimativa inicial:** 3-4 sprints (grande, transversal)

## Contexto

O ecossistema tem agora 5 setores (canal, inteligência, produtividade, finanças, programação) + **Ronaldo** como assistente pessoal do Guilherme. Hoje:

- **Ronaldo** lê arquivos para dar resumos (`agenda.json`, `lembretes.json`, `tarefas.md`, `kanban.md`) — estado é estático e reativo.
- O **Corte** mostra vídeos, versões e agentes trabalhando — mas é focado em canal.
- O Guilherme vê cada setor em lugar diferente: Trello (Kanban), Telegram (avisos), `estudio/` (interface web), Google Agenda, arquivos Markdown.
- Avisar **Ronaldo** de bloqueios ou pedir ação exige mensagem de texto, sem contexto visual ou histórico.

**Oportunidade:** um dashboard único, em tempo real, onde **Ronaldo** (e o Guilherme) veem o estado operacional completo do ecossistema e dão ordens sem sair de um lugar.

## Proposta: Dashboard Ecossistema

### Visão geral (o que mostrar)

Um painel, no browser ou celular, estruturado em **abas** ou **cards** mostrando:

#### 1. **Resumo (Home)**
   - **Status dos setores** (5 cards):
     - Canal (próximo vídeo, status: parado / em produção / pronto para publicar)
     - Inteligência (última coleta, próxima rodada)
     - Produtividade (compromissos de hoje, tarefas abertas)
     - Finanças (saldo, próxima transação esperada)
     - Programação (Sprint ativa, WIP, bloqueios)
   - **Indicador visual**: verde (ok), amarelo (atenção), vermelho (bloqueado)
   - **Últimos avisos**: últimas 3 mensagens de aviso (ex.: "Impedimento: Trello pausada")

#### 2. **Agora (ao vivo)**
   - **Quem está trabalhando**: lista em tempo real de agentes ativos + tempo de execução
   - **Fila de trabalho**: próximos agentes/tarefas na fila
   - **Último erro**: se houver falha recente (com link para detalhes)
   - Atualização automática a cada 4 segundos (polling)

#### 3. **Agenda + Lembretes**
   - **Hoje**: compromissos e lembretes de hoje (integra `agenda.json` + `lembretes.json`)
   - **Próximos 3 dias**: preview
   - Clique para reabrir/editar no **Ronaldo** pelo Telegram

#### 4. **Tarefas + Bloqueios**
   - **Tarefas abertas do dia** (de `tarefas.md`)
   - **Impedimentos do Trello/programação** (de `quadro.md`, coluna "Bloqueado")
   - Cada bloqueio mostra: quem está travado, por que, desde quando, ação necessária

#### 5. **Ordens (control panel)**
   - **Campo de texto + autocompletar**: "@agente mensagem" ou "/ comando"
     - Ex.: `@Pedri priorizar tarefa X`, `@De Bruyne começar vídeo de comportamento`, `/ajuda`
   - **Botões rápidos**: "Pausar Trello", "Retomar Trello", "Rodar daily", etc.
   - **Histórico de ordens**: últimas 10 ações disparadas
   - Confirmação de cada ação (ex.: "Ordem enviada a **De Bruyne**")

#### 6. **Setores (detalhes por pasta)**
   - Abas por setor: **Canal**, **Inteligência**, **Produtividade**, **Finanças**, **Programação**
   - Cada uma mostra: estado atual, último trabalho, próximas ações
   - Links para ferramentas específicas (Corte, Trello, Google Agenda)

---

## Arquitetura técnica

### Backend (Python)

**Novo módulo:** `estudio/ecossistema.py`

```python
class EstadoEcossistema:
    """Lê estado em tempo real de todos os setores."""
    
    def status_setores(self) -> Dict:
        """Resumo de cada setor: canal, inteligência, produtividade, finanças, programação."""
        # Lê: output/, inteligencia/, produtividade/, financas/, programacao/quadro.md
        pass
    
    def agentes_ao_vivo(self) -> List:
        """Agentes/tarefas trabalhando agora (integra Corte + produtividade)."""
        # Jobs do Corte + status do Ronaldo (se processando mensagem)
        pass
    
    def agenda_lembretes_hoje(self) -> Dict:
        """Compromissos + lembretes de hoje."""
        # Lê agenda.json, lembretes.json
        pass
    
    def bloqueios_abertos(self) -> List:
        """Impedimentos de programação + alertas do ecossistema."""
        # Lê quadro.md (coluna Bloqueado) + avisos registrados
        pass
    
    def historico_ordens(self, limite: int = 10) -> List:
        """Últimas N ordens disparadas."""
        # Lê `.cronograma_ordens.jsonl` (novo arquivo de auditoria)
        pass
```

**Rota nova (no servidor do Corte):**
```
GET /api/ecossistema
  -> EstadoEcossistema.status_setores() + agentes_ao_vivo() + ...

POST /api/ecossistema/ordem
  -> recebe {"agente": "Pedri", "mensagem": "..."}
  -> valida
  -> chama ronaldo_telegram.py para rotear
  -> registra em `.cronograma_ordens.jsonl`
```

### Frontend (HTML/JS)

**Nova página:** `estudio/public/ecossistema.html`

- Abas com CSS (sem framework pesado, compatível com celular)
- Polling a cada 4 segundos para "Agora" e "Status setores"
- Autocompletar no campo de ordens (lista de agentes + comandos rápidos)
- Ícones/cores por setor (azul=canal, verde=programação, roxo=finanças, etc.)
- Layout adaptativo: desktop = cards lado a lado; celular = cards em coluna, com scroll

### Integração com **Ronaldo**

Quando o Guilherme (ou **Ronaldo**) envia ordem via dashboard:
1. Dashboard valida e formata a ordem
2. Chama a rota `POST /api/ecossistema/ordem`
3. Backend roteia para `ronaldo_telegram.py` (mesma função já usada)
4. **Ronaldo** processa e avisa o resultado
5. Dashboard mostra confirmação e atualiza estado

**Exemplo fluxo:**
```
Guilherme digita no dashboard: "@Pedri marcar como feito a tarefa X"
  ↓ (clica enviar)
Dashboard → /api/ecossistema/ordem {"agente": "Pedri", ...}
  ↓
Backend chama ronaldo_telegram.chamada_agente("pedri-gestor-tarefas", "marcar...")
  ↓
Telegram processa e **Ronaldo** responde
  ↓
Dashboard atualiza histórico e mostra "✅ Pedri processou seu pedido"
```

---

## Critérios de aceite (proposta)

1. **Página acessível** em `http://127.0.0.1:8765/ecossistema` (ou `/dashboard`) no computador e no celular (`--rede`).

2. **Aba Home (Resumo)**:
   - 5 cards de setores, cada um com status (verde/amarelo/vermelho).
   - Status de cada setor derivado dos dados reais (não hardcoded).
   - Últimos 3 avisos do dia, com timestamp.

3. **Aba Agora**:
   - Lista de agentes trabalhando (nome + tempo de execução + vídeo/tarefa).
   - Atualiza sem recarregar a página a cada 4 s.
   - Mostra "Ninguém trabalhando" quando ocioso.

4. **Aba Agenda + Lembretes**:
   - Integra `agenda.json` + `lembretes.json`.
   - Mostra compromissos e lembretes de hoje com hora.
   - Link "Editar" leva a conversa com **Ronaldo** no Telegram (fora do dashboard).

5. **Aba Tarefas + Bloqueios**:
   - Tarefas de hoje (de `produtividade/tarefas.md`).
   - Impedimentos da sprint atual (de `programacao/quadro.md`).
   - Cada item com: descrição, dono, data de criação, ação sugerida.

6. **Aba Ordens (Control Panel)**:
   - Campo de texto com autocompletar (@agente, /comando).
   - Botões rápidos para ações comuns (ex.: "Pausar Trello", "Rodar daily").
   - Histórico das últimas 10 ordens enviadas.
   - Confirmação visual de cada ordem ("Enviado a **Pedri**").

7. **Abas de Setores**:
   - Canal: próximo vídeo, status, link para Corte.
   - Inteligência: última coleta, próxima rodada.
   - Produtividade: tarefas do dia, kanban, link para Trello.
   - Finanças: resumo (saldo, últimos 3 movimentos).
   - Programação: sprint ativa, WIP, bloqueios.

8. **Performance**:
   - Carregar a página inicial em menos de 2 s.
   - Polling em "Agora" não trava a interface (teste com 50 agentes simultâneos).
   - Celular: scroll fluido, sem layout quebrado.

9. **Teste automatizado**:
   - e2e: abrir dashboard, verificar presença de cada aba e dados.
   - Enviar uma ordem via dashboard e confirmar roteamento ao Telegram.
   - Simular agente trabalhando e verificar atualização ao vivo.

10. **Segurança**:
    - Acesso ao dashboard só com o servidor do Corte rodando localmente (não expor para a rede sem autenticação).
    - Ordens disparadas são registradas em `.cronograma_ordens.jsonl` (auditoria).
    - Nenhuma senha, token ou chave no arquivo ou interface.

---

## Esforço e risco

### Estimativa

| Componente | Esforço | Dev | Risco |
|---|---|---|---|
| Backend `ecossistema.py` | 8h | **Rodrygo** | Baixo (leitura de arquivos existentes) |
| Rota API + integração Telegram | 4h | **Rodrygo** | Baixo (usa `ronaldo_telegram.py` existente) |
| Frontend (HTML/CSS/JS) | 12h | **Endrick** | Médio (primeira página de dashboard, muitos dados) |
| UX (desenho de abas e layout) | 4h | **Iniesta** | Baixo (reutiliza padrão do Corte) |
| Teste e2e + QA | 6h | **Alisson** | Médio (múltiplas abas, polling, integração) |
| **Total** | **34h** | — | — |

**Sprints:** 1 sprint de 5 dias ≈ 40h de equipe → cabe **se priorizado**; ou 2 sprints em paralelo (fatias A e B).

### Risco

- **Acoplamento:** integra 5 setores diferentes; mudança em um afeta a visão geral.
  - **Mitigação:** módulo `ecossistema.py` é puro (lê, não escreve) e testável isoladamente.

- **Performance:** polling de muitos agentes + 5 setores pode travar.
  - **Mitigação:** cache de 3-4 s, leitura lazy (só carregar dados da aba ativa).

- **Ordering/Telegram:** ordem enviada via dashboard precisa rotear corretamente.
  - **Mitigação:** reutiliza `ronaldo_telegram.py` existente; testar com 2-3 agentes reais.

---

## Dependências

1. **PROG-012** (status automático de vídeo) — base para o resumo de canal.
2. **PROG-003/006** (agentes ao vivo) — base para a aba "Agora".
3. **Infraestrutura existente**: Telegram bot, Google Agenda, Trello, `estudio/` servidor.

**Bloqueadores:** nenhum; pode começar em paralelo com Sprint 01.

---

## Próximos passos (para o time de programação)

1. **Zico** refina este documento com o Guilherme: confirma escopo, prioridade, prazo.
2. **Thiago Silva** decide: uma entrega única, ou fatias (Backend → Frontend → Testes)?
3. **Iniesta** desenha o layout de abas e responsividade.
4. **Rodrygo** + **Endrick** implementam em paralelo (back e front).
5. **Alisson** testa (e2e, dados reais, polling).

---

## Suposições

- Dashboard é acessível só localmente (sem publicar na web).
- Dados não são armazenados em banco (tudo leitura de arquivos existentes).
- Ordens são roteadas pelo **Ronaldo** (via Telegram), não disparam ação direta do dashboard.
- Não há autenticação no dashboard (segue a mesma lógica do Corte local).
- O layout é adaptativo (desktop + celular `--rede`), sem app nativo.

---

## Questões em aberto (para o Guilherme)

1. **Onde colocar o dashboard?** Na mesma `http://127.0.0.1:8765/` ou em servidor separado?
2. **Prioridade vs. Sprint 01:** isso entra na próxima sprint ou em paralelo?
3. **Ordens rápidas:** quais botões rápidos são mais úteis? (ex.: pausar Trello, rodar daily, gerar vídeo, etc.)
4. **Acesso remoto:** o dashboard precisa ser acessível via `--rede` (celular em casa)?

---

**Próximo:** **Zico** refina com o Guilherme e propõe como PROG-016 ou similar no backlog.
