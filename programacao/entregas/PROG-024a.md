# PROG-024a: gerador local de dados financeiros (Rodrygo)

Mudou: `estudio/dados/gerar_financas.py` (novo), `estudio/testes/testar_financas.py` (novo), `.gitignore` (+ `ecossistema/app/dados/`), `programacao/tecnico/prog-024-contrato-financas.md` (contrato).
Testes (fixture inventada): `python estudio/testes/testar_financas.py` -> 37 ok, 0 falhas (valores, categorias vazias, vencimento atrasado, saldo divergente, arquivo ausente, linha mal formada, CSV intacto, regerar muda).
Execução real (uma vez): `python estudio/dados/gerar_financas.py` -> 32 movimentos, 2 contas, 0 vencimentos, 10 alertas. Saída ignorada pelo git (`git check-ignore` confirmou).
Achados nos dados reais (sem valores): (1) `saldos.csv` linha 4 tem 5 colunas (vírgula não aspada na observação), então o saldo mais recente da conta do extrato é ignorado e aparece alerta de saldo velho; corrigir é decisão do Casemiro/Guilherme. (2) 1 conta NÃO CONFIRMADO (fora do disponível). (3) 6 pendências abertas. (4) 1 valor estimado/a confirmar. (5) `git ls-files financas` mostra CSV, dashboard e pendências rastreados: pendente, decisão do Guilherme (não removi nada).
Pendente: 024b (tela, Endrick + Firmino); conferência do Marquinhos no git.
