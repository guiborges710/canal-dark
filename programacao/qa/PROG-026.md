# QA PROG-026 — servidor do dashboard

**Data:** 2026-11-11  
**Estado:** parcial; não aceitar ainda.  
**Escopo:** rotas do dashboard `/api/sistema/*`, casca local de Finanças e segurança do servidor. Nenhuma funcionalidade do Corte foi alterada.

## Testes

| Bateria | Resultado |
|---|---:|
| Testes de edição local, rota HTTP e recuperação dos arquivos derivados | 19/19 passou |
| `python estudio/testes/testar_painel.py` | 202/202 passou |
| `python estudio/testes/testar_ao_vivo.py` | 49/49 passou |
| `python estudio/testes/testar_cronograma.py` | 42/42 passou |
| `python estudio/testes/testar_status_video.py` | 45/45 passou na repetição; a primeira rodada excedeu o teto de desempenho (544 ms, limite 300 ms) |
| `node estudio/testes/e2e_interface.mjs` | 149 passou, 1 falhou, repetido duas vezes |
| `node estudio/testes/e2e_financas.mjs --real` | 208/208 passou; nenhum valor real foi impresso |

As rotas usam CSV temporário inventado nos testes. A cobertura inclui edição e regeneração, restauração do CSV quando a geração falha, gravação atômica dos dois arquivos derivados, origem e Host externos, traversal codificado, symlink, dispatch fechado, corpo excessivo, JSON inválido e recusa de cliente remoto às rotas do sistema mesmo com `--rede` ativo. Os arquivos reais de Finanças e capturas estão ignorados pelo Git.

## Falha pendente

`e2e_interface.mjs` falha em **“só a narração da cena alterada fica desatualizada”** (`fluxoDependencias`). A resposta informa que o roteiro mudou, mas `obsoleto.cenas` vem vazio; a suíte conclui com 149 aprovações e 1 falha em duas execuções. A asserção chama `/api/producoes/...`; esta alteração acrescenta dispatch fechado em `/api/sistema/*`. A revisão estática não encontrou sobreposição entre as rotas, mas a regressão geral continua vermelha. Não alterar o Corte fora do escopo do dashboard.

## Conclusão

As rotas direcionadas do dashboard e a tela local de Finanças passaram na cobertura. O PROG-026 permanece parcial até a falha da regressão ser classificada sem mudança no Corte e a bateria geral ficar verde.
