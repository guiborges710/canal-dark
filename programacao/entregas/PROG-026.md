# Entrega PROG-026 (Rodrygo) — 2026-11-12

**Estado:** parcial. Não vai para Em teste: a regressão geral do Corte ainda não ficou verde no repositório real.

## O que já existe (de antes)
Rotas GET `/api/sistema/*` por chaves fixas, confinamento da pasta Finanças, recusa de cliente remoto mesmo com `--rede`. Testes e resultados em `qa/PROG-026.md` (19/19 de edição e regeneração, 202, 49, 42 e 45 nas baterias Python, 208/208 no e2e de Finanças).

## O que fiz nesta rodada: classificar a falha do e2e
Falha: `e2e_interface.mjs`, "só a narração da cena alterada fica desatualizada" (`obsoleto.cenas` vazio, motivo "O roteiro mudou depois desta narração.").

| Execução | Resultado |
|---|---|
| Repositório real, `servidor.py` atual (E2E_PORTA=8812) | 149 ok, 1 falha (mesma falha) |
| Cópia limpa em pasta temporária (estudio, media, agents, prompts, render, .venv, 2 slugs de `output/`), `servidor.py` do HEAD | 150/150 |
| Mesma cópia, `servidor.py` ATUAL (com as rotas do sistema) | 150/150 |

Conclusão: o código do `servidor.py` atual não causa a falha. O mesmo código passa na cópia e falha no repo real, então a causa está no ambiente do repo real. Pista: a falha ocorre em `fluxo.cenas_afetadas`, que não achou a versão antiga do roteiro (devolve "alcance desconhecido" e lista vazia). Isso sai de `fluxo.py`/`materiais.py` (sem relação com as rotas do sistema). `git diff` de `fluxo.py` só troca "Sidorf" por "Seedorf". Não alterei o Corte.

Não identifiquei o que difere no repo real (a cópia não levou `corte.py` da raiz, `tools/`, `models/` nem os arquivos soltos do raiz; não consegui rodar o experimento seguinte, que apaga `estudio/dados` da cópia, por falta de permissão).

## Pendente
1. Descobrir a diferença de ambiente (próximo passo: copiar `corte.py`, `tools/`, `models/` para a cópia e repetir; ou depurar `cenas_afetadas` no repo real). Decisão sobre mexer no Corte é do **Thiago Silva**.
2. Com e2e 150/150 no repo real, atualizar `qa/PROG-026.md` e mover para Em teste.

Nenhum commit, publicação ou gasto. A cópia temporária está em /tmp/tmp.euMqnoCOTE (fora do repo).

## Rodrygo, 2026-11-12: nova rodada da regressão

- `E2E_PORTA=8791 node estudio/testes/e2e_interface.mjs`: 149 ok, 1 falha (3ª repetição, igual às anteriores): "só a narração da cena alterada fica desatualizada" → `{"motivo":"O roteiro mudou depois desta narração.","cenas":[]}`.
- Diagnóstico: a mensagem vem de `estudio/fluxo.py` `_calcular_obsoleto("narracao")` (ramo `cenas_afetadas` sem "conhecido"). O diff de `fluxo.py` no working tree só troca o nome "Sidorf" por "Seedorf"; as rotas `/api/sistema/*` não participam do caminho. Falta confirmar se a falha já existia sem as mudanças do PROG-026 (rodar a mesma bateria em cópia limpa do HEAD); não alterei o Corte.
- Não declaro pronto: critério 6 (baterias verdes) segue aberto.
