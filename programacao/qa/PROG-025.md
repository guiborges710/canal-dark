# QA PROG-025 — casca do app H

**Data:** 2026-11-11  
**Estado:** parcial; revisão visual consolidada de **Firmino** concluída em cópia temporária, sem dados reais. Mantém Fazendo até a validação final integrada com P0 do 032.  
**Escopo:** navegação entre os oito grupos, tema, paleta Ctrl K, Finanças e estados vazios na casca local.

## Evidência automatizada

`node estudio/testes/e2e_financas.mjs`: **194/194** com dados inventados; `--real`: **208/208**. A bateria cobre os oito grupos, dica de navegação horizontal somente no celular, estados vazios, paleta Ctrl K, links internos, alternância e persistência de tema, edição de movimentos, gastos em vermelho nos dois temas, larguras desktop e 390 px, sem rolagem lateral nem erro de JavaScript. A execução real não imprimiu valores financeiros. As capturas e os arquivos derivados de dados estão sob caminhos ignorados pelo Git.

## Revisão visual de Firmino

A casca foi renderizada numa cópia temporária segura, sem `dados/` pessoais; os dados usados eram fictícios. A bateria E2E da cópia passou **192/192**. **Firmino** abriu os oito grupos e confirmou estados vazios em português, Ctrl K com todos os destinos, Esc e seleção atual, alternância claro/escuro e gastos vermelhos nos dois temas. Não houve overflow horizontal em 390/1440 px.

Refinamento responsivo aplicado após a revisão: em telas até 560 px, a barra agora mostra a dica “Deslize para ver todos os grupos”; ela fica oculta no desktop. O E2E confirmou visibilidade em 390 px, ausência em 1440 px e nenhuma rolagem lateral. Resta como P2 usar ilustrações específicas nos estados vazios dos grupos. Capturas da revisão ficaram em `%TEMP%\shell025-assets-Pj82JN` e `%TEMP%\shell025_*`; nenhum arquivo do workspace foi alterado.

## Pendente

- Revisar a casca consolidada após integrar os P0 aprovados. O PROG-032 ainda tem cinco P0 faltantes/reprovados.

## Conclusão

A casca atual passou cobertura funcional e revisão visual nos dois temas. Manter em Fazendo até integrar e validar visualmente os P0 do PROG-032; os refinamentos P2 podem ser priorizados depois.
