# PROG-financa-detalhes: detalhes dos cards e ações em alertas e pendências (Finanças, visual H)

Desenho de **Iniesta** para o **Endrick**. Estende `prog-024b-especificacao-visual.md` (não a substitui). Parte da tela `ecossistema/app/financas.js` e do modal de edição que já existe (`editarMovimento`, `<dialog class="edicao-mov">`, rota `POST /api/financas/movimentos/editar`).

Situação do quadro: pedido feito por autorização direta do Guilherme, sem cartão próprio. O trabalho está logicamente sob o PROG-024 (Finanças no H). O **Zico** deve decidir se vira PROG-024c ou cartão novo antes do **Endrick** começar.

Valores de exemplo abaixo são inventados.

## Princípios (valem para os dois fluxos)
- Todo clique dá retorno visível em até 100 ms (botão em "ocupado", painel abrindo ou aviso).
- Estado desabilitado sempre explica o motivo (texto visível, não só tooltip) e diz o que fazer.
- Erro diz o que houve e a próxima ação, com botão "Tentar de novo".
- Nenhum pagamento real é feito por aqui. Onde houver "pago", o texto deixa claro que é só o registro.
- Status nunca só por cor: texto + forma, como no 024b.
- Com "Ocultar valores" ligado, tudo continua mascarado (R$ ••••) nos painéis, modais e avisos.

---

# FLUXO 1: clicar nos 4 números da ilha

## 1.1 Os 4 cards viram botões
Os 4 `.nm` da ilha (Saldo disponível, Recebido no mês, Gasto no mês, A pagar no mês) passam a ser `<button>` (mesmo visual, mais um chevron "›" discreto no canto e, ao passar o mouse, a dica "Ver movimentos"). Foco de teclado com `--foco`. Enter e Espaço abrem.

Nomes (rótulo do painel e `aria-label` do botão):
| Card | `aria-label` | Título do painel | O que lista |
|---|---|---|---|
| Saldo disponível | "Saldo disponível: ver movimentos que o compõem" | "Movimentos do saldo" | Recebidos e gastos pagos do mês (entradas e saídas já realizadas), mais as contas no topo |
| Recebido no mês | "Recebido no mês: ver movimentos" | "Recebido no mês" | `tipo` receita com status recebido |
| Gasto no mês | "Gasto pago no mês: ver movimentos" | "Gasto pago no mês" | `tipo` gasto com status pago |
| A pagar no mês | "A pagar no mês: ver movimentos" | "A pagar no mês" | `tipo` gasto com status a pagar (inclui vencidos) |

Observação de texto: hoje a ilha diz "Gasto no mês". O pedido do Guilherme chama de "gasto pago". Sugestão: manter "Gasto no mês" no card e, na legenda pequena do card, escrever "só o que já foi pago". O painel usa o título completo "Gasto pago no mês".

## 1.2 Onde abre
- **Desktop (>900 px):** painel lateral à direita, 480 px de largura, sobre a tela com fundo escurecido leve. A tela atrás não rola.
- **Celular (390 px):** folha de baixo para cima ocupando a tela inteira (altura 100%, cantos de cima arredondados). Botão "Voltar" grande no topo à esquerda. Sem rolagem lateral.
- Implementar como `<dialog>` (já usado no modal de edição e na paleta), com `showModal()`. Esc fecha. Foco vai para o título do painel ao abrir e volta ao card clicado ao fechar.
- A URL ganha `#/financas/saldo|recebido|gasto|a-pagar` para o botão voltar do navegador fechar o painel (celular, principalmente).

## 1.3 Layout do painel (de cima para baixo)
```
[ Voltar ]  Recebido no mês                          [ X ]
Novembro de 2026 · 6 movimentos · Total R$ 6.400,00
[ Mês: Novembro ▾ ]   [ Buscar na lista ______ ]

Ordenar:  Data (mais nova primeiro) ▾

-- Hoje, 12/11 ------------------------------------------
(avatar) Salário                       + R$ 5.200,00
         Renda · recebido em 05/11       [Editar]
(avatar) Reembolso de viagem           + R$ 1.200,00
         Renda · recebido em 03/11       [Editar]
...
-- Rodapé (fixo) ------------------------------------------
Fonte: movimentos.csv, lido hoje às 08:14
```
- Cabeçalho mostra a contagem e a soma da lista, e confere com o número do card. Se não bater, aparece uma linha de aviso: "A soma desta lista (R$ X) não bate com o card (R$ Y). Veja Alertas." (usa `.al`, estado erro).
- Seletor de mês: padrão `mes_atual`. Lista os meses disponíveis em `meses` (já existe no JSON). Trocar de mês mostra carregando (1.5.2) só se houver espera.
- Busca filtra por descrição e categoria, no próprio navegador, sem esperar rede. Sem resultado: "Nenhum movimento com “{texto}”. Limpe a busca para ver todos." com botão "Limpar busca".
- Linha de movimento (reaproveita `.mv` e `.mv-a`): descrição, categoria e data/status em texto, valor à direita (recebido em verde com "+", gasto em azul com "−", ambos com o texto do status, não só cor). Botão "Editar" abre o modal que já existe (`editarMovimento`), sem mudar nada nele. Depois de salvar, o painel recarrega a lista e os cards da ilha atualizam.
- Agrupamento por dia: "Hoje", "Ontem", depois "dd/mm". Em A pagar o agrupamento é por situação (ver 1.4).

### 1.3.1 Saldo disponível (variação)
Topo do painel mostra as contas (`saldos.contas`) em cartões pequenos: nome, saldo, "atualizado em dd/mm". Texto fixo abaixo, igual ao do cartão Contas:
"O saldo do banco não é a soma destes movimentos. Esta lista mostra só o que você lançou como pago ou recebido."
Contas fora do disponível aparecem com a etiqueta "fora do disponível" e a observação de `contas_fora_do_disponivel`.
Entradas com "+" e saídas com "−" na mesma lista, em ordem de data.

## 1.4 A pagar (variação com ação)
Grupos, nesta ordem, cada um com contagem e soma:
1. "Vencidos" (estado erro): "Venceu há 3 dias" em cada linha.
2. "Vencem em até 3 dias" (estado pendente): "Vence hoje", "Vence amanhã", "Vence em 2 dias".
3. "Mais adiante" (estado backlog): "Vence em 15/12".

Cada linha tem o botão primário **"Marcar como pago"** (fluxo 2.5) e o secundário "Editar". No celular, o primário ocupa a largura da linha, abaixo do texto, com altura mínima de 44 px.

Texto de ajuda fixo no topo do painel (fechável, lembra em `localStorage`):
"Marcar como pago só registra aqui. Nenhum pagamento é feito por este app."

## 1.5 Estados do painel

### 1.5.1 Normal
Como acima.

### 1.5.2 Carregando
Aparece se a leitura demorar mais de 300 ms (evita piscar). Esqueleto `.sk` com 5 linhas cinzas e o texto acessível "Carregando movimentos…" (`aria-live="polite"`). Cabeçalho do painel já aparece completo com "Novembro de 2026". Botões Editar e Marcar como pago ainda não aparecem. Botão Fechar funciona sempre.

### 1.5.3 Vazio (um texto por tipo; sempre diz por que e o que fazer)
| Painel | Título | Texto | Ação |
|---|---|---|---|
| Recebido | "Nada recebido em novembro" | "Ainda não há receitas com status recebido neste mês. Se você já recebeu algo, confira o status do lançamento." | "Ver outro mês" |
| Gasto pago | "Nenhum gasto pago em novembro" | "Não há gastos com status pago neste mês. Gastos ainda não pagos aparecem em “A pagar”." | "Abrir A pagar" |
| A pagar | "Nada a pagar em novembro" | "Todas as contas deste mês estão pagas ou ainda não foram lançadas." | "Ver outro mês" |
| Saldo | "Sem movimentos neste mês" | "O saldo mostrado vem das contas. Ainda não há lançamentos pagos ou recebidos em novembro." | "Ver outro mês" |
Usa o bloco `.vazio` com o slot `vazio_financas` (placeholder até o PROG-032).
Se o mês escolhido não tem nada mas existem outros meses com dados, o botão "Ver outro mês" abre o seletor.

### 1.5.4 Erro
Quando a leitura falha (rede, arquivo de dados ausente, resposta inválida):
- Título: "Não consegui carregar os movimentos"
- Texto: "A leitura dos dados falhou. Nenhum valor antigo é mostrado aqui para você não confundir com o atual."
- Botões: "Tentar de novo" (primário; mostra "Tentando…" e fica desabilitado enquanto roda) e "Fechar".
- Se falhar de novo: "Continua sem carregar. Verifique se o Corte está aberto neste computador e tente de novo em alguns segundos."
- Detalhe técnico recolhido em "Ver detalhes" (código e mensagem), para o Guilherme copiar e mandar ao **Rodrygo**.

Erro só na ação Editar (salvar falhou): mensagem dentro do modal, sem fechar, igual ao que já existe ("A linha mudou desde que a tela foi aberta. Recarregue antes de salvar." mantém).

### 1.5.5 Sem permissão
Hoje as rotas de finanças só aceitam acesso local (loopback), mesmo com `--rede`. Quando a resposta for 403 (ou o app detectar que não é acesso local):
- Título: "Finanças só abre neste computador"
- Texto: "Por segurança, os movimentos não aparecem quando o Corte é aberto pela rede (celular, por exemplo). Abra o Corte direto no computador para ver e editar."
- Botão único: "Entendi". Sem botão de tentar de novo (não adianta).
- Os 4 cards da ilha, nesse caso, já nem deveriam mostrar valores. Se hoje mostram, os cards ficam desabilitados com o texto "Bloqueado: abra no computador" (e `aria-disabled="true"`).
- Se for 401 (sessão expirada em `--rede`): "Sua sessão expirou. Entre de novo com a senha do Corte." + botão "Entrar".
Pergunta aberta ao **Zico**/**Rodrygo**: confirmar se o celular deve mesmo ficar sem Finanças (decisão pendente do PROG-034).

### 1.5.6 Dados velhos
Se `idade_dias` > 3: faixa amarela no topo do painel: "Dados de {N} dias atrás. Os valores podem estar desatualizados." + botão "Atualizar leitura" (aciona a regeneração; mostra "Atualizando…").

### 1.5.7 Celular 390 px (resumo das regras)
- Folha de tela inteira, sem rolagem lateral, nenhum texto cortado: descrição quebra em até 2 linhas e depois "…".
- Valor sempre visível à direita, nunca sob o texto.
- Alvos de toque de pelo menos 44×44 px (Editar vira ícone de lápis com `aria-label="Editar {descrição}"`; "Marcar como pago" em largura total).
- Busca e seletor de mês ficam em duas linhas, não lado a lado.
- Cabeçalho fixo (título + X); o rodapé "Fonte" rola com a lista.
- Botão voltar do sistema fecha o painel (por causa da âncora `#/financas/...`).

---

# FLUXO 2: alertas e pendências abertos

## 2.0 Modelo de estado (o que o **Endrick** e o **Rodrygo** precisam combinar)
Cada alerta e cada pendência precisa de um **id estável**. Estados:
- `aberto` (padrão)
- `resolvido` (guarda `resolvido_em`)
- `apagando` (escondido, com contagem de 8 s para desfazer)
- `apagado` (sai das listas; fica só no backup local)

Alertas hoje são derivados dos dados pelo gerador, não linhas do CSV; por isso o estado (resolvido, editado, apagado) precisa de um arquivo local próprio, por exemplo `financas/alertas_estado.json` (fora do Git, com backup, como o CSV). Regra de reaparecimento a confirmar com o Guilherme: um alerta resolvido ou apagado que **continua verdadeiro** na próxima leitura reaparece? Proposta: não reaparece enquanto a causa for a mesma (mesmo id e mesmos valores); reaparece só se os valores mudarem. Registrar "reapareceu porque o valor mudou" no próprio item.

## 2.1 Como a seção fica
A seção `#alertas` continua com duas colunas (alertas à esquerda, pendências à direita; empilham no celular). Cada coluna tem:
1. Cabeçalho: "Alertas abertos (3)" / "Pendências abertas (2)".
2. Itens abertos.
3. No fim, bloco recolhido **"Resolvidos (4)"** (um por coluna), fechado por padrão.

Item aberto (`.al`):
```
[!] Pago sem lançamento                           [ Editar ] [ ⋯ ]
Conta de luz marcada como paga em 05/11, mas não há lançamento de R$ 214,30.
O que fazer: lance o gasto ou volte o status para "a pagar".
                                   [ Marcar como resolvido ]
```
- Ação principal visível: **"Marcar como resolvido"**.
- "Editar" fica visível no desktop. O menu "⋯" ("Mais ações", `aria-haspopup="menu"`) tem "Editar" e "Apagar" (em vermelho). No celular, só o principal e o "⋯" ficam visíveis (Editar dentro do menu).
- Pendência de conta a pagar (ligada a um movimento "a pagar") também mostra **"Marcar como pago"** como ação principal no lugar de "Marcar como resolvido" (ver 2.5). Se a pendência não for de pagamento, só "Marcar como resolvido".
- Apagar não tem confirmação em caixa: usa Desfazer (2.4), que é mais rápido e seguro.

## 2.2 Marcar como resolvido
1. Clique em "Marcar como resolvido".
2. Resposta imediata: o botão muda para "Resolvendo…" e fica desabilitado (só se a gravação demorar mais de 150 ms).
3. O item sai da lista de abertos com animação curta (desligada com `prefers-reduced-motion`) e entra em "Resolvidos". A contagem do cabeçalho e do rótulo "Resolvidos (N)" atualizam.
4. Aviso (toast) de 6 s: **"Marcado como resolvido."** com botão **"Desfazer"**.
5. Em "Resolvidos", cada item aparece esmaecido, com o texto "Resolvido em 12/11 às 10:40" e dois botões: **"Reabrir"** e "Apagar".
6. Quando a lista de abertos esvazia: linha "Tudo conferido." (já existe) e, se houver resolvidos, "N resolvidos abaixo".

Bloco "Resolvidos":
- Fechado: botão de expandir "Resolvidos (4)" com seta; `aria-expanded="false"`.
- Aberto: lista dos itens, ordenados do mais recente. Estado lembrado em `localStorage` (`ce_h_fin_resolvidos`).
- Vazio: "Nada resolvido ainda. Itens que você marcar como resolvidos aparecem aqui."
- Erro ao gravar: o item **volta** para a lista de abertos e aparece "Não consegui marcar como resolvido. O item continua aberto. Tente de novo." com "Tentar de novo".

## 2.3 Editar
Abre um modal (`<dialog class="edicao-alerta">`, mesmo estilo do `edicao-mov`; no celular vira folha de tela inteira). Título: "Editar alerta" ou "Editar pendência".

Campos editáveis:
| Campo | Alerta | Pendência | Regra |
|---|---|---|---|
| Título | sim (obrigatório, até 80 caracteres) | sim | Vazio: "Escreva um título." |
| Detalhe | sim (até 300) | sim | Texto livre |
| O que fazer | sim (até 200) | sim | Texto livre |
| Valor (R$) | opcional | opcional | Aceita "1.234,56"; guarda em centavos. Inválido: "Valor inválido. Use números, como 214,30." |
| Data limite | não | opcional | `dd/mm/aaaa`. Inválida: "Data inválida. Use dia/mês/ano." |
Texto de ajuda do modal: "Você está mudando só este aviso. Os lançamentos (movimentos) não mudam por aqui. Para corrigir um lançamento, use Editar na lista de movimentos."

Botões: "Salvar" (primário), "Cancelar". "Salvar" só habilita quando algo mudou; enquanto desabilitado, o texto abaixo diz "Nenhuma alteração para salvar."
- Ao salvar: botão "Salvando…", depois o modal fecha, o item atualiza e aparece o toast **"Alterações salvas."**.
- Cancelar com alterações não salvas: pergunta curta dentro do modal, "Descartar as alterações?" com "Descartar" e "Continuar editando". Sem alterações, fecha direto.
- Esc se comporta como Cancelar.
- Erro de gravação: faixa vermelha no topo do modal, "Não consegui salvar. Suas alterações continuam aqui. Tente de novo." O modal fica aberto.
- Conflito (o item mudou desde que a tela abriu, mesma lógica da edição de movimento): "Este aviso mudou depois que você abriu a tela. Recarregue para ver a versão atual." com "Recarregar". 
- Editar um item em Resolvidos é permitido; ele continua resolvido.
- Se o alerta foi gerado pelos dados (não escrito à mão), mostrar sob o título a etiqueta pequena "Gerado pela leitura dos dados" e, na primeira edição, o aviso: "Se os dados mudarem, a leitura pode gerar este aviso de novo." (ligado à regra de reaparecimento de 2.0).

## 2.4 Apagar com Desfazer
1. Clique em "Apagar" (no menu "⋯" ou no item resolvido).
2. O item some da lista na hora (estado `apagando`). Nada é apagado ainda.
3. Toast fixo no rodapé (no celular, acima da barra do sistema), com `role="status"` e `aria-live="polite"`:
   **"Alerta apagado."** (ou "Pendência apagada.") + botão **"Desfazer"** + barra fina de contagem regressiva de **8 segundos**.
4. Desfazer dentro de 8 s: o item volta exatamente para onde estava (lista de abertos ou de resolvidos) e o toast diz **"Apagar desfeito."** por 3 s.
5. Passados 8 s sem Desfazer: grava o apagamento definitivo. O toast some sem mensagem extra (o Desfazer já avisou). Um backup local fica no servidor (o mesmo padrão da edição de movimentos), mas **não há botão de restaurar na tela**.
6. O tempo pausa se o mouse estiver sobre o toast ou o foco estiver no botão Desfazer, e recomeça ao sair. Leitores de tela têm o tempo estendido para 15 s.
7. Vários apagamentos seguidos: um toast por vez, empilhados (máximo 3 visíveis); cada um tem seu Desfazer e seu tempo. O mais novo fica embaixo.
8. Atalho: se o foco está no toast, Enter aciona Desfazer. Ctrl Z logo após apagar também desfaz o último (opcional, o Endrick decide).
9. Se a gravação definitiva falhar (após os 8 s): o item reaparece na lista com aviso **"Não consegui apagar “{título}”. Ele voltou para a lista. Tente de novo."**
10. Se o usuário fechar ou recarregar a página durante a contagem: o item **não** é apagado e volta (escolha segura). Pergunta ao Guilherme: prefere que apague mesmo assim?

Nunca se apaga movimento do CSV por este fluxo. Apagar vale só para alertas e pendências.

## 2.5 Marcar como pago em "A pagar" (também lança no saldo)
Vale para as linhas do painel A pagar (fluxo 1.4) e para pendências ligadas a uma conta a pagar. Resultado final: o movimento passa de "a pagar" para "pago" e entra no saldo e no "Gasto no mês". Nenhum pagamento real é feito.

### Passo a passo
1. Clique em **"Marcar como pago"**.
2. Abre um modal pequeno de confirmação (não é o de edição completa):
   - Título: "Marcar como pago"
   - Resumo: "Conta de luz · R$ 214,30 · venceu em 05/11"
   - Campo "Data do pagamento" (padrão: hoje).
   - Campo "Valor pago (R$)" (padrão: o valor da conta). Se mudar, aparece "Diferença de R$ X em relação ao valor previsto."
   - Campo "Conta" (de onde saiu o dinheiro; lista de `saldos.contas`, padrão: a conta usual daquele lançamento, se existir).
   - Texto de efeito, sempre visível: **"Vai lançar uma saída de R$ 214,30 no saldo da conta {nome}. Isso só registra aqui; nenhum pagamento é feito por este app."**
   - Pré-visualização: "Saldo disponível: R$ 3.100,00 → R$ 2.885,70" (com valores ocultos, vira "••••").
   - Botões: "Confirmar pagamento" (primário) e "Cancelar".
3. "Confirmar pagamento": botão vira "Registrando…" e desabilita.
4. Sucesso, tudo na mesma ação (uma gravação só, para não ficar pela metade):
   - O movimento muda de status "a pagar" para "pago" com a data informada (e o valor, se mudou). Não cria linha duplicada.
   - O saldo disponível, o "Gasto no mês" e o "A pagar no mês" recalculam e as barras da ilha animam (sem animação com `prefers-reduced-motion`).
   - A linha sai da lista A pagar e passa a aparecer em "Gasto pago no mês".
   - A pendência ligada vai automaticamente para "Resolvidos" com a nota "Resolvido ao marcar como pago".
   - Toast de 8 s: **"Conta de luz marcada como paga. Saldo atualizado."** com **"Desfazer"**.
5. Desfazer: volta o movimento para "a pagar", restaura data e valor originais, desfaz o lançamento no saldo, reabre a pendência. Toast: **"Pagamento desfeito. A conta voltou para “A pagar”."**
6. Se o vencimento **não tem linha no CSV** (só existe como vencimento previsto): a confirmação cria uma linha nova de gasto pago, e o texto de efeito diz "Vai criar um lançamento de gasto pago de R$ 214,30." Desfazer remove a linha criada.

### Casos e proteções
- Já está pago (mudou em outra aba ou na leitura): "Esta conta já consta como paga. Atualize a tela para ver a versão atual." com "Atualizar".
- Valor zero ou vazio: "Informe o valor pago." Valor negativo: "Use um valor maior que zero."
- Data no futuro: aviso (não bloqueia): "A data é futura. Confirme se é isso mesmo."
- Conflito de linha (CSV mudou): "O lançamento mudou depois que você abriu a tela. Recarregue antes de pagar." com "Recarregar". Nada é gravado.
- Erro de gravação: "Não consegui registrar o pagamento. Nada foi alterado. Tente de novo." O modal fica aberto com os dados preenchidos.
- Dados velhos (> 3 dias): a confirmação abre com a faixa "Os dados têm {N} dias. Confira o saldo antes de confirmar." Não bloqueia.
- Gravação parcial nunca deve ocorrer: o servidor faz as duas coisas (movimento e estado da pendência) ou nenhuma. Pendência: **Rodrygo** define a transação.

## 2.6 Estados da seção de alertas
| Estado | O que a pessoa vê |
|---|---|
| Carregando | Dois blocos com esqueleto (3 linhas cada). Texto acessível "Carregando alertas e pendências…" |
| Sem nada aberto | "Tudo conferido. Nenhum alerta ou pendência aberta." (e "N resolvidos abaixo", se houver) |
| Só resolvidos | Igual ao anterior, com "Resolvidos (N)" visível |
| Erro ao ler | "Não consegui carregar os alertas. Tente de novo." + botão "Tentar de novo". Os 4 números da ilha continuam normais se vierem de outra leitura |
| Sem permissão (acesso por rede) | "Alertas só abrem neste computador." (mesmo texto do 1.5.5, versão curta). Ações escondidas |
| Gravando | Item com o botão em "ocupado"; os outros itens continuam clicáveis |
| Offline / Corte fechado | Ao tentar ação: "Sem conexão com o Corte. A ação não foi feita. Abra o Corte neste computador e tente de novo." O item volta ao estado anterior |

## 2.7 Celular 390 px
- Colunas de alertas e pendências empilhadas (alertas primeiro).
- Item: texto em largura total; "Marcar como resolvido" (ou "Marcar como pago") em largura total, 44 px de altura; "⋯" no canto superior direito.
- Menu "⋯" abre uma folha de baixo com "Editar" e "Apagar" em linhas grandes, e "Cancelar".
- Modais (editar, marcar como pago) viram tela cheia, com Salvar/Confirmar fixo na base e teclado do celular sem cobrir o botão (usar `visualViewport`).
- Toast acima do rodapé, largura total menos 16 px de margem de cada lado; botão "Desfazer" com 44 px de altura.

## 2.8 Acessibilidade
- Todos os botões têm rótulo que inclui o item, por exemplo `aria-label="Marcar como resolvido: Pago sem lançamento"`.
- "Resolvidos" usa `aria-expanded` e `aria-controls`.
- Toasts: `role="status"`, `aria-live="polite"`; o Desfazer alcançável por Tab logo após a ação (foco não é roubado, mas o toast é o próximo elemento na ordem de foco do fim da página; alternativa: tecla U dentro de 8 s, anunciada em "Para desfazer, pressione U").
- Dialogs: foco inicial no primeiro campo (ou no título no painel de movimentos); Tab fica preso dentro; Esc fecha; foco volta ao botão que abriu.
- Contagem regressiva é visual e também texto oculto "8 segundos para desfazer".
- Cores: erro, pendente e ok seguem o H; sempre com texto.

---

## Resumo dos textos curtos (para colar no código)
| Onde | Texto |
|---|---|
| Resolver | "Marcar como resolvido" / "Resolvendo…" / "Marcado como resolvido." |
| Reabrir | "Reabrir" / "Reaberto." |
| Editar | "Editar" / "Salvar" / "Salvando…" / "Alterações salvas." / "Nenhuma alteração para salvar." |
| Apagar | "Apagar" / "Alerta apagado." / "Pendência apagada." / "Desfazer" / "Apagar desfeito." |
| Pagar | "Marcar como pago" / "Confirmar pagamento" / "Registrando…" / "Conta de {nome} marcada como paga. Saldo atualizado." / "Pagamento desfeito. A conta voltou para “A pagar”." |
| Resolvidos | "Resolvidos ({N})" / "Nada resolvido ainda. Itens que você marcar como resolvidos aparecem aqui." |
| Sem nada | "Tudo conferido. Nenhum alerta ou pendência aberta." |
| Erro leitura | "Não consegui carregar os movimentos" / "Tentar de novo" |
| Sem permissão | "Finanças só abre neste computador" / "Entendi" |

## Dependências e perguntas
Para o **Zico** (e **Thiago Silva**, no refinamento):
1. Cartão: PROG-024c ou novo? Pedido veio sem cartão.
2. Persistência de estado de alertas e pendências (resolvido, editado, apagado) com id estável: dono **Rodrygo**; novos endpoints (resolver, reabrir, editar aviso, apagar, restaurar, marcar pago com transação única). O endpoint de editar movimento já existe e deve ser reaproveitado para "Marcar como pago".
3. Marcar como pago em vencimento sem linha no CSV cria um lançamento novo: confirmar que isso é aceito.
Para o Guilherme:
1. Um alerta resolvido ou apagado volta se o problema continuar nos dados? (proposta: só volta se o valor mudar)
2. Se a página for fechada durante os 8 s do Desfazer: apagar ou restaurar? (proposta: restaurar)
3. Finanças deve aparecer no celular via `--rede` ou continuar só no computador?
4. O card "Gasto no mês" deve passar a se chamar "Gasto pago no mês"?
