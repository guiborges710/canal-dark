# PROG-024b: Finanças no H, app real (Endrick)

## Retomada e edição (11/11/2026)
- Edição local por movimento: data, descrição, categoria, valor e status; salvamento com cópia de segurança, comparação da linha original e regeneração da leitura.
- Validação adicionada nesta rodada: 5 testes unitários da escrita isolada e a bateria HTTP local passou 9/9 (8 cenários de Finanças mais a recusa remota das rotas do sistema; origem, Host, traversal codificado, symlink, limite do corpo, gravação/regeneração e recuperação após erro). O E2E da tela passou 194 verificacoes com dados inventados e 208 no total com dados reais, incluindo envio do formulário, decimal pt-BR, oito grupos e layouts 1440/390.
- Correção encontrada pelo E2E: removido `<base href="/financas/">`, que quebrava carregamento por `file://` ao apontar os recursos para a raiz do disco. A rota local `/financas/` continua servindo os recursos relativos.
- A edição usa o servidor local e altera somente `financas/movimentos.csv`; não grava dados financeiros no app nem faz pagamentos.
- Casca do PROG-025 iniciada na tela: oito grupos navegáveis, tema, paleta de comandos e atalhos 1–8. As áreas ainda não implementadas exibem estado vazio claro.
- Revisão local dos lançamentos: relatório ignorado pelo git em `ecossistema/app/dados/financas-pendencias-revisao.md`; 14 itens pedem detalhe ou reconciliação. CSV não foi alterado nessa revisão.
- Estado: edição e validações passaram. Captura da tabela enviada pelo **Ronaldo** no Telegram; o Guilherme respondeu que os dados estão bons e pediu edição dos lançamentos, agora implementada. Segue para Code Review. Nenhum CSV real foi alterado durante os testes.

## Arquivos (ecossistema/app/)
`index.html`, `financas.js` (tela, ligada a `dados/financas.js`), `financas.css`, `estilo.css`/`base.js`/`comum_gh.js` (cópias do H; `prototipo_estilos/` não foi tocado), `dados_demo.js` (cópia de `dados.js`: só nomes de agentes e menu que `base.js` exige, sem dado financeiro; some no PROG-025), `abrir_financas.bat`, `README.md`.
Teste: `estudio/testes/e2e_financas.mjs`.

## Testes
`node estudio/testes/e2e_financas.mjs --real`: 127 ok, 0 falhas (Chrome headless, file://, 1440 e 390, sem erro de JS, sem rolagem lateral). Cenários com dados inventados em cópia descartável: normal, atrasado, divergente, sem vencimentos, velho, vazio, erro (arquivo ausente, incompleto, sintaxe quebrada, tipo errado), Tentar de novo sem recarregar, carregando (esqueleto), ocultar valores (nenhum valor em texto/aria/tooltip; persiste; tecla O), Ctrl K, links só internos. Execução com dados reais: 1 vez, tela renderizou sem erro de JS e sem rolagem lateral em 1440 e 390; capturas em `ecossistema/app/dados/capturas/` (ignorada pelo git). Nenhum valor real impresso ou copiado.

## Critérios do PROG-024 (evidência)
- Mock e chaves FINANCAS_MOCK/CENARIOS/ESTADO removidos: atendido.
- Carregando, erro (com comando `python estudio/dados/gerar_financas.py` e botão que relê), vazio: atendido (testes acima).
- Links e Ctrl K coerentes: abas e atalhos 1-8 das outras telas ficam apagados e explicam "ainda não existe neste app"; atendido, a navegação real é PROG-025.
- Privacidade: atendido (ver README); decisão de manter percentuais visíveis segue o Firmino, a confirmar com o Guilherme.
- Atalho `.bat` e README: atendido (o `.bat` não foi executado; o gerador e a abertura foram testados por fora).
- Revisão visual via Telegram: retorno positivo sobre os dados apresentados; edição solicitada foi implementada e validada. A revisão técnica segue pendente no Code Review.

## Divergências do contrato real (conferidas na saída real e no código do gerador)
1. `movimentos_recentes[].tipo` real: `gasto` ou `recebido`; `status`: `pago`, `a pagar`, `a receber`. A tela trata como previsto.
2. `receitas_x_gastos.gastos` = só gastos PAGOS (não inclui "a pagar"; confirmado no gerador). A tela já rotulava "Gastos pagos". `categorias` inclui pagos + a pagar.
3. `dias_restantes`, `atrasado`, `status` dos vencimentos e `idade_dias` dos saldos ficam congelados na hora do gerador. A tela recalcula todos pela data e pelo dia de hoje (e `idade` do selo vem de `gerado_em`).
4. Vazamento: a mensagem `saldo_divergente` traz a diferença em centavos ("diferenca de N centavos") e `observacao` pode trazer "extrato: N". Ao ocultar, a tela mascara esses padrões (além de "R$"). Sugestão ao **Rodrygo**: tirar o valor da mensagem ou entregá-lo em campo próprio.
5. `categorias[].percentual` é número decimal (não inteiro); a validação aceita.
6. Se o gerador falhar, ele não grava e o arquivo antigo permanece: a tela mostra a última leitura com selo "dados velhos há N dias" (não vira erro).

## Seletor de mês (pedido direto do Guilherme)
- Barra "Mês" na ilha: setas anterior/próximo + chips com mês e ano por extenso ("Outubro 2026"), o atual marcado "atual". Padrão: mês atual; a escolha fica em `localStorage` (`ce_h_fin_mes`, com try/catch) e `#mes=AAAA-MM` na URL vale mais que a lembrada. Teclado: setas esquerda/direita com foco no seletor; Ctrl K, "Ir para mês..." lista os meses. No celular os chips rolam na horizontal.
- Muda com o mês (lê `meses[AAAA-MM]`): recebido, a receber, gasto pago, a pagar, resultado (rotulado "resultado das movimentações, não é saldo bancário"), receitas x gastos, categorias, vencimentos, movimentos completos (paginados de 40 em 40). O gráfico dos 6 meses destaca o mês escolhido e a barra clicável seleciona o mês.
- Fica fixo e rotulado: saldo por conta/saldo disponível ("saldo de hoje, não muda com o mês"), alertas e pendências ("da leitura toda, não só do mês"), selo de dados velhos.
- Estado vazio: "Nenhum lançamento em <mês>"; se for o mês atual, botão "Ver <último mês com lançamentos>". Mês só com recebimento renderiza (gastos zero, categorias e vencimentos explicados).
- Arquivo sem `meses` (ou com o bloco torto): um único chip, o mês atual, aviso "só traz o mês atual", sem erro.
- Ocultar valores vale em todos os meses (movimentos inclusive).
- Teste: `node estudio/testes/e2e_financas.mjs --real`: 187 ok, 0 falhas. Novos cenários inventados: mês passado só com recebimento, mês atual vazio (e atalho), virada de ano (Dez 2025 / Jan 2026), arquivo sem `meses`, `meses` torto, troca por clique, teclado, Ctrl K, gráfico e URL, paginação (85 lançamentos), ocultar em mês antigo, 390px com chips rolando e alvos de 44px.
- Capturas reais (um arquivo por mês disponível e largura, sem valores no relatório): `ecossistema/app/dados/capturas/financas_real_<AAAA-MM>_<1440|390>.png` (pasta ignorada pelo git).


## Atualizacao de robustez (11/11/2026)
- Se a regeneracao ou gravacao dos dados derivados falhar apos editar, a API restaura o CSV a partir do backup.
- A geracao de `financas.json` e `financas.js` usa arquivos temporarios e restaura/remove saidas parciais em falha.
- Cobertura atual: 19 testes unitarios e HTTP passaram; `testar_financas.py`: 59/59; `e2e_financas.mjs --real`: 208/208. Os CSVs reais nao foram editados. Saidas e capturas financeiras continuam ignoradas pelo Git.
