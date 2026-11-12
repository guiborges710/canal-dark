# App do ecossistema: Finanças (PROG-024b)

Primeira tela do sistema único. A casca tem oito grupos navegáveis; Finanças está conectada e os demais grupos mostram o estado enquanto entram nas próximas tarefas da sprint.

## Como abrir e atualizar
- Duplo clique em `abrir_financas.bat`: gera os dados e abre Financas em `http://127.0.0.1:8765/financas/` no servidor local.
- Use o botao Editar em cada movimento para corrigir data, descricao, categoria, valor ou status. O salvamento cria backup local ignorado pelo git, atualiza somente movimentos.csv e regenera a leitura.
- A edição é protegida contra sobrescrita concorrente: se a linha mudou desde que a tela foi aberta, o servidor pede para recarregar antes de salvar.
- O menu lateral troca entre os oito grupos; Ctrl K ou `/` abre a busca, e as teclas 1 a 8 abrem cada grupo. `O` oculta valores e `T` alterna o tema.
- Se `dados/financas.js` não existe ou está incompleto, a tela mostra o erro e o comando a rodar. Nunca mostra número antigo como se fosse de agora.

## De onde vêm os dados
Os CSVs de financas sao a fonte. A edicao local altera somente os campos do movimento; nao efetua pagamentos nem marca itens pagos automaticamente. A rota aceita apenas acesso loopback, mesmo com o Estudio aberto em rede.

## Seletor de mês
Barra "Mês" no topo: setas e chips (rolam na horizontal no celular), atual marcado. Abre no mês atual; lembra a escolha (`localStorage`) e aceita `#mes=AAAA-MM`. Teclado: setas esquerda/direita no seletor; Ctrl K, "Ir para mês...". Trocar o mês muda números da ilha, receitas x gastos, categorias, vencimentos, movimentos e destaca o gráfico (clicar numa barra escolhe o mês). Saldo das contas, alertas e selo de dados velhos não são do mês e ficam rotulados. Mês sem lançamentos mostra estado vazio (e sugere o último mês com lançamentos). Lê o bloco `meses` do gerador; arquivo antigo sem ele mostra só o mês atual.

## Painel dos 4 números (PROG-024c)
Saldo disponível, Recebido, Gasto pago e A pagar são botões. Clicar (ou Enter/Espaço) abre um painel lateral de 480 px (folha de tela inteira no celular) com os movimentos que formam o número, resumo com contagem e soma, seletor de mês, busca por descrição e categoria, ordenação e agrupamento por dia (A pagar agrupa por situação: Vencidos, Vencem em até 3 dias, Mais adiante). "Editar" abre o modal que já existia. A âncora `#/financas/saldo|recebido|gasto|a-pagar` faz o botão voltar do navegador fechar o painel. Estados: carregando (esqueleto só após 300 ms), vazio por tipo, erro com Tentar de novo, sem permissão (acesso fora do computador; `?acesso=remoto` simula, só para teste) e dados velhos (mais de 3 dias). Só leitura: "Marcar como pago" e o Fluxo 2 (alertas e pendências) não fazem parte desta entrega.

## Privacidade
- `dados/` (inclui `capturas/` e backups) e os arquivos pessoais em `financas/` estão no `.gitignore`; as cópias locais são preservadas. Os scripts `.py` de Finanças continuam versionáveis. Nenhum CSV, captura ou relatório financeiro deve entrar em commits.
- Botão "Ocultar valores" (tecla O): valores, mensagens e observações com número, gráfico dos 6 meses e barras que revelariam valor somem. Ficam percentuais de categoria, datas e contagens. A escolha fica no navegador (`localStorage`).
- Código, testes e documentação versionada não devem conter valores reais; os testes usam dados inventados.

## Arquivos
`index.html`, `financas.js` (tela e shell), `financas.css`, `estilo.css` (H), `base.js`, `comum_gh.js`, `dados_demo.js` (só nomes de agentes e menu; sem dado financeiro), `assets/` (WebP validados disponíveis).

## Testes
`node estudio/testes/e2e_financas.mjs` (dados inventados, Chrome headless, 1440 e 390). Com `--real`, roda uma vez com os dados reais e salva capturas em `dados/capturas/` sem imprimir valores.
