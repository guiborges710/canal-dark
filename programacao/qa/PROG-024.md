# QA PROG-024 · Finanças no H (Alisson, 12/11/2026)

**Veredito: APROVADO, com 1 ressalva de privacidade que depende do Guilherme (histórico git).**
Nenhum valor financeiro real foi copiado para este relatório (critério 7).

## Regressão rodada por mim (resultado real)
| Bateria | Resultado |
|---|---|
| `python -m estudio.testes.testar_financas` (fixture inventada) | 59 ok, 0 falhas |
| `testar_financas_edicao` | 5 testes, OK |
| `testar_financas_edicao_http` | 11 testes, OK |
| `testar_financas_gravar_atomico` | 3 testes, OK |
| `node estudio/testes/e2e_financas.mjs` (fixture, 1440 e 390 px) | 196 ok, 0 falhas |
| `node estudio/testes/e2e_financas.mjs --real` (dados reais locais, nada impresso) | 210 ok, 0 falhas |

## Critérios
| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Dados vêm de `financas/*.csv` (saldos com data, total e por conta, vencimentos, movimentos, receitas x gastos, categorias) | PASSOU | `testar_financas` 59 ok e e2e 196/210 conferem cada bloco; captura real 390 px mostra todos os blocos |
| 2 | Valores batem com os CSV; fixture inventada; alterar e regerar muda a tela | PASSOU | fixture montada no próprio teste (cópia descartável); casos de mês vazio, virada de ano e `meses` torto ok |
| 3 | Status em TEXTO e cor, barras, claro/escuro | PASSOU (via e2e) | asserções do e2e; na captura os selos têm texto ("A pagar", "Vencido" etc.). Não fiz inspeção pixel a pixel, a imagem foi reduzida |
| 4 | Faixa de alertas do **Casemiro** com origem | PASSOU | e2e ok; captura mostra a faixa "Alertas" com origem em cada item |
| 5 | Estado vazio, erro e data/hora da última leitura | PASSOU | e2e: "sem meses", "meses torto", dados atrasados/divergentes |
| 6 | Privacidade: gerado e CSV ignorados; `git ls-files financas` | PASSOU para o estado atual | `git ls-files financas` = só `dashboard.py` e `planilha_ler.py` (código); `check-ignore`: `financas/*`, `estudio/dados/`, `ecossistema/app/dados/` ignorados; nenhum CSV ou dado gerado no `git status` |
| 7 | Nenhum dado financeiro para API, `dados.js`, `qa/`, `revisoes/` | PASSOU | e2e `--real` não imprime valores; capturas reais ficam em `ecossistema/app/dados/capturas` (ignorado); `index.html` atual sem `R$` fixo nem senha (grep vazio) |
| 8 | 1280 e 390 px sem rolagem lateral | PASSOU | e2e roda 1440 e 390 px, sem falha; captura 390 px em coluna única |
| 9 | Aceite visual, **Thiago Silva**, QA com resultado real | PASSOU | capturas geradas (`financas_real_2026-11_390.png` e `_1440.png`); revisão do **Thiago Silva** em `programacao/revisoes/PROG-024.md`; este relatório |

## Ressalva (não é falha de código; bloqueia só publicar o repositório)
O commit `8853702` (HEAD) ainda contém em `ecossistema/app/index.html` a senha `ecossistema123` e saldos/pendências reais (`git show HEAD:ecossistema/app/index.html` confirma a senha). A versão de trabalho atual está limpa, mas o histórico não. Se o repositório for ou estiver em remoto/público, o **Guilherme** precisa decidir sobre trocar a senha e reescrever o histórico; o **Marquinhos** executa. Também há alterações do PROG-024 ainda sem commit (`index.html` modificado, `login.html` removido no índice, arquivos novos em `ecossistema/app/`): antes de commitar, repetir `git ls-files financas` e conferir que `ecossistema/app/dados/` não entra.

## Bugs novos
Nenhum.

## Para o aceite do Guilherme
Ver as capturas em `c:\Users\Guilherme\Documents\canal-dark\ecossistema\app\dados\capturas\` (locais, ignoradas pelo git) e decidir a ressalva acima.

---
# Reteste 12/11/2026 (Alisson) após a edição local do 024b — **DEVOLVIDO**
Nenhum valor financeiro real copiado.

| Bateria | Resultado real |
|---|---|
| `testar_financas` | 59 ok, 0 falhas |
| `testar_financas_edicao` / `_http` / `_gravar_atomico` | 5 / 11 / 3 testes, OK |
| `e2e_financas.mjs` (fixture) | 194 ok, **2 FALHAS** |
| `e2e_financas.mjs --real` | mesmas **2 FALHAS** (as duas são sobre cor, não sobre dados) |

**Falha (bug novo, pequeno):** `normal: gastos aparecem em vermelho` nos temas claro e escuro. O teste (e2e_financas.mjs linhas 162-166) espera `rgb(198, 40, 40)` e `rgb(255, 107, 99)`; a tela entrega `rgb(196, 48, 29)` e `rgb(255, 123, 110)` (`.mv-v.neg` usa `var(--c-erro)`, financas.css:115). Ainda é vermelho, mas o teste e a paleta divergem. Esperado: bateria verde. Obtido: 2 falhas. Corrigir: o **Endrick** decide se a cor nova é a do H (e atualiza o teste) ou volta ao valor antigo.

Critérios 1, 2, 4, 5, 6, 7, 8: continuam PASSOU (mesmas baterias, `git ls-files financas` = só `dashboard.py` e `planilha_ler.py`; `index.html` sem "R$ nº" nem senha). Critério 3 (cores do H em claro/escuro): **FALHOU na verificação automatizada** até o teste e a cor concordarem. Ressalva do histórico git (commit 8853702 com senha) segue pendente com o **Guilherme**/**Marquinhos**.
Veredito: DEVOLVIDO ao **Endrick**.
