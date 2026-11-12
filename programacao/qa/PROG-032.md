# QA PROG-032 — assets do H

**Data:** 2026-11-11 (revalidado nesta retomada)  
**Estado:** parcial; faltam cinco assets P0 aprovados.  
**Entrada:** `ecossistema/sistema_unico/assets`, indicada pelo Guilherme no comentário do Trello.

## Validação atual

Executado `organizar_e_validar.py` em modo `--so-validar --prio P0,P1`, sem alterar a pasta de entrada. Resultado para 61 itens: **42 OK, 1 OK*, 8 reprovados e 10 faltando**. O novo lote de saída, produzido em pasta temporária para comparação, contém 119 WebP aceitos; todos os 119 caminhos já existem em `ecossistema/app/assets` e não há WebP extra nessa pasta.

Os cinco P0 sem aprovação são:

- `avatar_casemiro`: faltando.
- `avatar_ronaldo`: reprovado por divergência do fundo setorial.
- `avatar_de_bruyne`: faltando.
- `avatar_luiz_henrique`: faltando.
- `vazio_espera`: faltando.

Prompts para reposição estão em `output/032_asset_check/prompts_pendentes.md`. A pasta indicada pelo Guilherme foi revalidada nesta retomada e preservada. O resultado permaneceu igual; os nomes/arquivos atuais não suprem os cinco P0 acima. O lote de prompts já preparado continua em `output/032_asset_check/prompts_pendentes.md`; não foi gerada uma segunda leva para evitar duplicidade.

## Conclusão

Os 119 WebP aceitos já estão integrados. Manter o PROG-032 em andamento até validar e integrar os cinco P0 restantes e concluir a revisão visual da casca por **Firmino**.
