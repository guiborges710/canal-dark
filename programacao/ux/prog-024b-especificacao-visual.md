# PROG-024b: especificação visual da tela Finanças (H)

Desenho e mock estático do **Firmino**; a ligação aos dados reais é do **Endrick**. Protótipo: `ecossistema/prototipo_estilos/h/financas/index.html` (abra com `?cenario=`: normal, atrasado, divergente, sem_vencimentos, vazio, erro, velho, carregando). Capturas inventadas em `h/financas/capturas/`. Os valores do mock são inventados; nenhum dado real foi usado.

## Arquivos
- `financas.js`: toda a tela. Funções por seção (`secAlertas`, `secSerie`, `secRxG`, `secContas`, `secCategorias`, `secVenc`, `secMov`, `secFonte`) e `ilha()` com os 4 números. Reaproveita `B` (base.js) e `GH` (g/comum_gh.js) sem editá-los.
- `financas.css`: soma ao `h/estilo.css` (que fica intocado). Tudo sob `body.fin`.
- `dados_mock.js`: só o mock. Na integração, trocar por `<script src=".../app/dados/financas.js">` (define `window.FINANCAS`) e apagar o mock e as chaves `FINANCAS_MOCK`, `FINANCAS_CENARIOS`, `FINANCAS_ESTADO`.

## Estrutura (ordem na tela)
1. Ilha escura (`.ilha`, `.i-nums` com 4 `.nm`): Saldo disponível (maior), Recebido no mês, Gasto no mês, A pagar no mês. Cada um com barra `.pb` (recebido/(recebido+previsto), pago/(pago+a pagar), parte já vencida do a pagar). Abaixo, legenda dos 5 estados e o selo `.selo` (lido hoje ou dados velhos há N dias, gerado em, fontes lidas).
2. Alertas (`#alertas`): inconsistências (`.al`, com origem e "O que fazer") à esquerda, pendências abertas à direita. Sem nada, uma linha "tudo conferido".
3. Últimos 6 meses (`#serie-box`, SVG desenhado na largura real, redesenhado no resize) + coluna com Receitas e gastos e Contas.
4. Gastos por categoria (8 maiores, botão para todas) e Vencimentos.
5. Movimentos recentes (avatar `avatar_casemiro_rd` em `.mv-a` via `GH.av`, slot 26 px).
6. De onde vêm estes números (`fonte.arquivos` e `contagens`).

## Estados dos 5 (forma + cor, vindos do H)
| estado H | aqui significa |
|---|---|
| ok | pago ou recebido; lido hoje |
| erro | vencido; inconsistência (divergente, pago sem lançamento, linha inválida); dados velhos há mais de 3 dias |
| pendente | vence em até 3 dias (inclui hoje); atenção (não confirmado, saldo velho, valor estimado); dados de 1 a 3 dias |
| backlog | a pagar adiante, previsto, a receber, histórico |
| rodando | lendo os dados (carregando) |
Gastos usam o azul `--c-rodando` por classe `.e-gasto` (sem listras animadas) e recebidos o verde `--c-ok`. Status sempre em texto além da cor.

## Tokens do H usados
`--ilha*`, `--papel`, `--card`, `--card2`, `--tx`, `--mut`, `--linha`, `--linha-f`, `--sinal`, `--c-ok/erro/pendente/backlog/rodando`, `--foco`, `--num` (Bahnschrift nos números), `--txt`. Classes do H: `.ilha`, `.i-in`, `.i-top`, `.busca`, `.bt-i`, `.i-nav`, `.aba`, `.nm`, `.nn`, `.nr`, `.ns`, `.mini`, `.legenda`, `.est`, `.pb`, `.cartao`, `.vazio`, `.slot`, `.bt`, `.bt.prim`, `.paleta`, `.toast`. Novas: `.cat-i`, `.cat`, `.vc`, `.mv`, `.al`, `.cta`, `.rg2`, `.res`, `.serie`, `.selo`, `.sk`.

## Regras de formatação (só na tela)
- Entrada em centavos inteiros. `partes()` separa reais e centavos; `T()` texto puro ("R$ 1.234,56", negativo com "−"); `R()` HTML; `RG()` número grande (R$ pequeno, reais grandes, centavos pequenos); `K()` compacto no gráfico ("6,1 mil").
- Datas ISO viram `dd/mm`; `gerado_em` vira "dd/mm às hh:mm"; dias de atraso e restantes vêm do JSON (`dias_restantes`, `idade_dias`).
- Percentual `31,2%` (vírgula). Plural tratado em `plural()`.
- Categoria: texto livre do CSV é normalizado (`catKey`, sem acento, com apelidos como contas, luz, internet) para um dos 14 ícones SVG (`CAT`); sem correspondência vira "outros" e mantém o rótulo original. Os 14 SVGs são candidatos a entrar em `base.js`.

## Ocultar valores
Botão "Ocultar valores" na ilha e tecla O. Padrão visível; a escolha fica em `localStorage` (`ce_h_fin_ocultar`). Oculto: todo valor vira "R$ ••••" com texto "valor oculto" para leitor de tela; aria-labels, tooltips do gráfico e valores em mensagens de alerta (regex `R$ ...`) também são mascarados. Proporções (barras, percentuais) continuam visíveis: decisão a confirmar com o Guilherme.

## O que ligar ao `window.FINANCAS` real
Já consumido (nomes do contrato): `gerado_em`, `mes_atual`, `saldos.{contas,disponivel,contas_fora_do_disponivel,observacao}`, `recebido`, `gastos`, `serie_mensal` (6 itens), `receitas_x_gastos`, `categorias` (já ordenadas), `vencimentos`, `movimentos_recentes`, `alertas`, `pendencias`, `fonte`. Falta decidir/ligar:
1. Trocar o script do mock pelo arquivo gerado; remover as chaves de mock.
2. Estado carregando: hoje só no mock (`FINANCAS_ESTADO`); no real, mostrar `esqueleto()` até o script carregar (`onload`) ou o `fetch` responder.
3. Erro: ausência de `window.FINANCAS` já cai no bloco de erro; "Tentar de novo" hoje faz `location.reload()`. Pode virar nova leitura. Se o gerador falhar, não mostrar número antigo como atual (texto do bloco já diz isso).
4. `movimentos_recentes[].tipo` deve ser `gasto` ou outro valor tratado como receita (confirmar com o gerador os valores de `tipo` e `status`: `pago`, `a pagar`, `a receber`).
5. Navegação: os links da ilha apontam para `../index.html#/grupo`; dentro da casca (PROG-025), usar a rota real. Paleta Ctrl K: o item Finanças já existe; integrar à paleta global.
6. Slots de imagem usados: `avatar_casemiro_rd` (movimentos), `vazio_financas`, `erro_geral` (tipo `vz`), `logo_contexto_explica`. Chaves `vazio_financas`/`erro_geral` entram em `GH.TIPOS` quando o PROG-032 liberar as imagens; hoje aparece o placeholder do H.

## Estados da tela
- Normal, atrasado, divergente, velho: tudo preenchido; alertas e selo mudam.
- Sem vencimentos: cartão com texto explicando; o número "A pagar" fica R$ 0,00 e sem barra.
- Vazio (`fonte.contagens` e listas sem linhas): bloco "Ainda não há lançamentos" + fontes.
- Erro e carregando: ilha com traços ou esqueleto, selo coerente.

## Pontos de atenção
- Acessibilidade: foco de teclado do H (`:focus-visible`), chips com texto, barras `role="progressbar"` com rótulo, gráfico com `role="img"` e tabela `.so` equivalente, tema claro e escuro, `prefers-reduced-motion` (a única animação própria, o crescimento das barras na primeira abertura, e as do H são desligadas pela regra global do H).
- Responsivo: 1440 e 390 sem rolagem lateral (testado em Chrome headless, 8 cenários). Celular é só "não quebrar"; ≤900 px o saldo ocupa a linha inteira e os demais números ficam em 2 colunas.
- Privacidade: este mock não carrega nem copia dados reais. Os dados reais continuam só em `ecossistema/app/dados/` (fora do git).
- O saldo bancário não é o resultado das movimentações (texto fixo no cartão Contas); o "Resultado do mês" usa só o que está pago.
- Se `idade` dos dados passar de 3 dias o selo vira erro; limites ajustáveis em `selo()`.
