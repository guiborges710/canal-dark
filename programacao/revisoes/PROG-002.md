# Revisão PROG-002 · "Iniciar cenas" não faz nada (Thiago Silva, 2026-11-04)

**Veredito: DEVOLVIDO** (pequeno: um teste e uma prova; sem mudança de produção).

Método: leitura do código atual (sem shell nesta sessão, então sem `git diff`).

## O que li
- `estudio/web/app.js` 653-659 (`iniciar`), 722-733 (botão `#iniciar`, `orientarInicio`, `semPorque`).
- `e2e_celular.mjs` 155-186; `e2e_interface.mjs` linhas com `#iniciar` (293, 370, 415, 455); `testar_prog001_002.py` 84-101.

## Posição sobre o critério 5 ("falha sem a correção")
O critério vale **só como cobertura**, não como regressão provada. Não houve correção de comportamento: o clique já funcionava. Então "falha sem a correção" só se cumpre se eu aceitar uma prova de mutação equivalente. Não há: o QA cita "estrutura de código" (app.js 722-729) como prova, e isso não é execução.

## Por que devolvo
1. **Celular com POST simulado.** O e2e do celular substitui `fetch` para o POST e para o estado (linhas 160-173). Prova que o toque chama `/iniciar` com `etapa: cenas`, mas não prova o servidor. Isso é aceitável porque o servidor real é provado no desktop (PROG-015 [1c], clique duplo e 1 trabalho). Mas o "Iniciar cenas" no desktop não tem clique real: os `#iniciar` reais de `e2e_interface` são narração (370), render (415) e 455. A entrega afirma "desktop e celular" sem essa distinção.
2. **Texto de orientação sem teste de tela.** A entrega e o QA divergem: a entrega diz que o botão bloqueado ganhou "o que fazer" (`orientarInicio`, `semPorque`, em `app.js`); o QA diz "nenhum código mudou". Nenhum teste verifica esse texto no DOM (busquei "Gere e aprove", "Aguarde esse trabalho", "sistema não informou": zero ocorrências). A linha 293 só confere `disabled`.
3. **Sem prova de mutação para o celular.** A sabotagem do PROG-015 desligou o ramo do CTA do topo (app.js 234), não o `onclick` do `#iniciar` (730).

## O que fechar (**Endrick**, com **Alisson**)
- (a) Um teste de tela: com a etapa cenas bloqueada (sem roteiro aprovado), o DOM mostra o motivo e a orientação (o texto de `orientarInicio`) e o botão está `disabled`. O caso `semPorque` também.
- (b) Uma rodada de mutação: trocar o `onclick` do `#iniciar` (app.js 730) por no-op e registrar que `e2e_celular` fica vermelho. Restaurar e conferir o diff.
- (c) Corrigir a entrega e o QA para dizerem o mesmo sobre o que mudou em `app.js`, e para dizerem que o "Iniciar cenas" real no desktop é coberto pelo mesmo handler dos outros `#iniciar`.

Depois disso aprovo na hora; não preciso reler o resto.


## Reanálise (Thiago Silva, 2026-11-04, com shell)
Rodei `e2e_interface` (E2E_PORTA=18911): **150 ok, 0 falhas**. Conferi no código: `#iniciar` em app.js l.730, `orientarInicio` l.740, `semPorque` l.726; o teste checa os textos de orientação (e2e_interface l.260-274). Mutação do `onclick` (60 ok/3 falhas no celular, 8 falhas no desktop) e restauração byte a byte estão registradas por Endrick e Alisson; aceito como prova equivalente. Entrega e QA agora dizem o mesmo.
**Veredito: APROVADO.** Limite aceito: no celular o POST é simulado; o servidor real é provado no desktop.
