# UX · PROG-003 + PROG-006 · Aba "Agentes", desenho B (Ao vivo e Catálogo)

Autor: **Iniesta** · 2026-11-03 (noite) · Sprint 01. Proposta de desenho, não código. Cartão: [PROG-003] + [PROG-006] no quadro.
Complementa `ux/prog-003-aba-agentes.md`: lá estão a conferência do código, os estados de agente, as linhas ativas e os textos de tempo. Aqui ficam só a estrutura B (duas abas) e o que muda por causa dela. Estados, ícones e textos de estado do outro arquivo valem iguais.

## Decisão de estrutura
A tela Agentes tem duas abas no topo: **Ao vivo** e **Catálogo**.
- **Ao vivo** (nova): painel largo de cartões, só leitura, mostra quem trabalha.
- **Catálogo**: a tela de hoje, intacta (lista à esquerda, ficha com editar, duplicar, desativar, testar, versões à direita). Garante o critério 12 (regressão da edição).

Qual abre primeiro (regra, a **Zico** confirmar):
1. Se há alguém trabalhando, na fila, falhou ou esperando o Guilherme: abre **Ao vivo**.
2. Se não há nada: abre **Catálogo**.
3. Depois que o Guilherme troca de aba, o Corte lembra a escolha dele naquela sessão e não troca sozinho de aba.
Na aba que não está aberta, o título leva um indicador: `Ao vivo (2)` com o número de trabalhando + na fila, ou `Ao vivo (!)` se algo falhou. Assim a atividade não fica escondida atrás do clique (a fraqueza do desenho B).

## Barra de abas
```
Agentes     [ Ao vivo (2) ] [ Catálogo ]                 [＋ Novo]
```
- Aba ativa sublinhada e com `aria-selected`. O botão "＋ Novo" só existe no Catálogo.
- Celular: duas abas de largura meia-tela, 44 px de altura.

## Aba "Ao vivo"
### Ordem das seções (seção vazia some)
1. **Precisa de você**: `❚❚ Espera você` (âmbar) e `✕ Falhou` (vermelho). É o que mais trava.
2. **Trabalhando agora**: `◐ Trabalhando`.
3. **Na fila**: `⏳ Na fila`.
4. **Terminaram há pouco** (últimos 30 min, no máximo 5): `✓ Concluído`, para dar fecho. Dúvida para o **Zico**.
Agentes livres e desativados não aparecem aqui (estão no Catálogo).

### Cartão (cada agente ativo)
```
+--------------------------------------------------+
| ◐ Trabalhando                          [ Claude ]|
| Olise · diretor de arte                          |
| krakatoa-geracoes                                |
| Etapa: Cenas (cena 4 de 9)   ▓▓▓▓▓░░░░           |
| há 2 min                                         |
| [ Abrir no Estúdio ]    Ver ficha do agente      |
+--------------------------------------------------+
```
Grade de cartões de 2 a 3 colunas no computador; 1 coluna no celular (chip do motor desce para a linha de baixo).
- Selo, craque, vídeo, etapa, tempo: iguais ao arquivo anterior.
- Tempo conta localmente a cada segundo. Depois de 15 min: âmbar "há 15 min: mais que o normal" (limite a confirmar).
- Dois vídeos para o mesmo agente: um cartão, "Trabalhando em 2 vídeos", com as duas linhas dentro; cada linha tem seu "Abrir no Estúdio".

### Motor e nota (PROG-006), o que aparece e onde
O motor aparece em **todo lugar onde há um trabalho**, sempre em texto:
- Cartão da aba Ao vivo: chip no canto.
- Painel "Agentes" do Estúdio de cada vídeo e diálogo de execução (`abrirExecucao`), ao lado do selo de estado e também na versão: `Motor: Claude`.
- Linhas de histórico/versões do job, onde existirem.

| Dado do job | O que mostra |
|---|---|
| `motor` = Claude, sem nota | Chip `Claude` neutro. Nada além. |
| `motor` = Codex, com `motor_nota` | Chip `Codex` com ponto âmbar. Sob ele, em cinza, a nota. Se a nota for técnica/inglesa, o desenho pede a frase padrão (abaixo) e guarda a nota original num "Detalhes" recolhido. |
| `motor` = Codex, sem nota | Chip `Codex` com ponto âmbar e a frase padrão: "Este trabalho rodou no Codex, a reserva usada quando o Claude esgota o limite." |
| `motor` ausente (job antigo) | Nenhum chip, nenhum "undefined", nenhuma linha vazia. Texto no diálogo de execução apenas: "Motor: não registrado (trabalho antigo)." |
| `motor` com valor desconhecido | Chip neutro com o texto cru ("Outro: <valor>") para nunca esconder a informação. |
| `motor_nota` vazia ou só espaços | Tratada como sem nota. |

Dica ao passar o mouse/tocar no chip Codex: "O Claude estava no limite; este trabalho rodou no Codex." (presente: "está rodando"). O chip Codex deve ser tocável no celular e abrir esse mesmo texto numa caixinha (não depende de hover).

### Retorno de cada clique
- "Abrir no Estúdio": o botão muda para "Abrindo…" e fica desabilitado até a navegação. Leva para o painel do nó com o log ao vivo. Se o vídeo não existe mais: aviso "Este vídeo não está mais no Corte. Veja em Projetos > Arquivados." (o cartão fica, o botão fica desabilitado com esse motivo).
- Cartão Falhou: botão "Ver o que houve" abre o diálogo com o erro no topo e "Tentar de novo".
- Cartão "Espera você": botão "Abrir para decidir" leva à etapa que aguarda aprovação.
- "Ver ficha do agente": troca para a aba Catálogo já com esse agente aberto. Retorno: a aba muda e o agente aparece destacado.

### Estados da aba Ao vivo
| Situação | O que aparece |
|---|---|
| Carregando | Três cartões-esqueleto + "Buscando quem está trabalhando…" |
| Ninguém ativo | `Nenhum agente trabalhando agora.` / `Quando uma produção rodar, ela aparece aqui sozinha.` / botões "Ir para Projetos" e "Ver o Catálogo" |
| Consulta falhou | Mantém o último estado; faixa âmbar `Sem atualização desde 14:32 (há 1 min). Mostrando o último estado conhecido.` + "Tentar agora". Contadores "há X" param e ganham "(pode ter mudado)". Ao voltar, faixa verde "Atualizado." some em 3 s. |
| Servidor fora do ar > 30 s | Faixa vermelha `O Corte não responde. Verifique se a janela do Corte ainda está aberta no computador.` (celular: "…no computador de casa") |
| Muitos trabalhos (50) | Até 10 cartões por seção + `+12 na fila, ver todos` que expande. Só estado atual, sem histórico. |
| Agente desativado durante o trabalho | Cartão com selo extra `⏻ Desativado: termina o trabalho atual` |
| Sem agentes cadastrados | Em Ao vivo: "Nenhum agente cadastrado." + botão "Ir para o Catálogo" |

Resumo fixo no topo da aba (região `aria-live="polite"`): `2 trabalhando · 1 na fila · 1 falhou · 1 espera você` (zeros omitidos). Rodapé: "Atualizado agora" / "há 20 s".

## Aba "Catálogo"
- Idêntica à de hoje, mais duas melhorias de baixo risco:
  1. Cada item da lista ganha o selo de estado atual à direita do nome: `◐ Trabalhando`, `⏳ Na fila`, `✕ Falhou`, `○ Livre` ou `⏻ Desativado` (assim a atividade também aparece aqui, sem depender da outra aba).
  2. Na ficha de um agente que está trabalhando, faixa curta no topo: `Trabalhando em krakatoa-geracoes · Cenas · há 2 min · Claude` + botão "Abrir no Estúdio".
- Edição não pode ser atrapalhada pela atualização: enquanto o Guilherme edita (`Corte.editando`), a ficha não redesenha; só o selo da lista atualiza.
- Texto do filtro sugerido (extra, opcional): "Mostrar: Todos · Só ativos · Só em fluxo".
- Seleção do agente é preservada ao trocar de aba e voltar.

## Celular
Abas no topo; "Ao vivo" empilha os cartões; resumo fixo em uma linha que pode quebrar; Catálogo mantém o padrão atual de lista e detalhe em tela cheia com "← Agentes". Nenhum chip ou texto passa da largura; linhas de etapa quebram em duas.

## Acessibilidade
- Abas com `role="tablist"`, setas esquerda/direita trocam de aba, Enter ativa.
- Cada cartão com `aria-label` completo: "Olise, trabalhando no vídeo krakatoa-geracoes, etapa Cenas, há 2 minutos, motor Claude."
- Ícone girando respeita a preferência "reduzir movimento".

## Atualização
Mesmo plano do outro arquivo: polling de 2 a 4 s, redesenho só se a assinatura mudar, pausa com aba oculta, contador local de 1 s. Ao vivo carrega só os jobs ativos (não os 38 agentes), o que atende o critério 8; o Catálogo só atualiza os selos.

## Mapa para os critérios
- PROG-003 critérios 1 a 4: cartão e selo; 5: polling; 6: botões; 7: celular; 8: seção com limite; 9: faixa desatualizada; 10: estado "Ninguém ativo"; 12: Catálogo intacto.
- PROG-006 critérios 1 a 3: tabela de motor e nota; 4: celular com toque no chip.

## Dúvidas para o Zico / Guilherme
1. Qual aba abre primeiro: regra acima (Ao vivo só quando há atividade)? Alternativa: sempre Ao vivo.
2. "Espera você" é estado de agente (vira critério novo)? Recomendo sim.
3. Seção "Terminaram há pouco" entra no escopo ou fica para depois?
4. Agentes de outros setores aparecem em Ao vivo? Sugiro sim, com o setor em cinza ao lado do craque.
5. Limite do "mais que o normal" (15 min) e se vale por etapa.
6. Ordem da entrega: Ao vivo primeiro; o Catálogo só ganha selos e faixa depois (conforme o escopo apertado da sprint, que o **Zico** vai reavaliar).
7. A frase padrão do Codex fala em "reserva quando o Claude esgota o limite". Depende de PROG-004; se o Guilherme decidir remover a reserva, o chip Codex some e a dica sai.

## Pontos de uso notados (sem mexer)
O aviso de erro some em 7 s sem botão de fechar (`app.js:32`), e o "há X" só se corrige quando os dados mudam. Já listados no arquivo anterior; seguem valendo.
