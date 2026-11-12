# QA PROG-005 · Atualizar testes e2e antigos (Alisson, 2026-11-04)

Execução: mock, sem API paga, `PYTHONUTF8=1`, `E2E_PORTA` própria por bateria. Primeira rodada com tudo em paralelo: `e2e_estilos` falhou 1 e `testar_estilos` deu MemoryError (carga + disco C: a 99%). Repeti os dois sozinhos: passam. Falso negativo de ambiente, não de código.

| # | Critério | Resultado | Evidência |
|---|---|---|---|
| 1 | Nenhum teste referencia `se_sketch` nem a contagem antiga | PASSOU (com ressalva) | `grep se_sketch estudio/testes`: só 3 linhas, todas em e2e_corte (asserção de ausência `!linhas.includes("se_sketch")`) e e2e_estilos (comentário). Nenhuma espera o nó. Ressalva literal: a asserção de ausência ainda cita o nome; **Thiago Silva** decide se aceita. |
| 2 | e2e_estilos, e2e_interface, e2e_corte e contagem de nós passam | PASSOU | e2e_interface 120 ok / 0 falhas; e2e_corte 152 / 0; e2e_estilos 98 / 0 (isolado); e2e_celular 63 / 0; testar_estilos.py 103 / 0 |
| 3 | Asserções atualizadas, não afrouxadas | NÃO VERIFICADO por mim | Sem baseline git (esses arquivos estão no HEAD já alterados). Conferência é do **Thiago Silva**. Vi que o `.catch(() => true)` vazio foi trocado por asserção real (e2e_corte 419-427). |
| 4 | `estudio/README.md` descreve como executar e o que esperar | PASSOU (com observação) | Seção de comandos (linhas 158-172) cobre as 6 baterias e o que cada uma mede. Observação: não documenta `E2E_PORTA` nem o risco de rodar em paralelo. |

Observações: a entrega `entregas/PROG-005.md` está desatualizada (118/97 com 1 falha); o número bate com o quadro só após a correção. Disco C: com ~4 GB livres; baterias em paralelo falham por espaço/memória.

**Veredito: APROVADO pelo QA**, condicionado à conferência do critério 3 pelo **Thiago Silva**.


## Reconfirmação final (Alisson, 2026-11-04)
`e2e_estilos` isolado, 2 execuções (portas próprias): 98 ok / 0 falhas e 98 ok / 0 falhas. As 3 pendências do **Thiago Silva** conferidas: comentário sobre o `.catch(() => {})` em e2e_corte l.418; `E2E_PORTA` documentada em estudio/README.md l.167; `grep se_sketch estudio/testes` só acha a asserção de ausência (e2e_corte) e um comentário. **Veredito: APROVADO.**
