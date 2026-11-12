# Pré-planning · Iniesta · PROG-003 (aba Agentes ao vivo)

Detalhe completo: `programacao/ux/prog-003-aba-agentes.md`.

## Situação hoje
A aba `/agentes` é só catálogo e editor (lista + ficha), carregada uma vez, sem polling e sem sinal de atividade. O Estúdio de cada vídeo já tem painel de agentes com estado, progresso e log ao vivo: é o vocabulário a reaproveitar. Faltam textos de "Na fila" e "Livre". Jobs já trazem `motor`.

## Proposta
- Estados com ícone + palavra: `◐ Trabalhando`, `⏳ Na fila`, `✕ Falhou`, `○ Livre`, mais `⏻ Desativado` (existente). Sugestão: `❚❚ Espera você` para aprovação pendente.
- Linha ativa: agente, vídeo, etapa, "há 2 min" (contador local de 1 s), chip do motor (Claude/Codex, com aviso quando for reserva).
- Clique na linha leva ao Estúdio do vídeo com o painel do nó e log abertos; falhou mostra o erro e "Tentar de novo". Clique no nome abre a ficha.
- Vazio: "Nenhum agente trabalhando agora." Desatualizada: faixa âmbar "Sem atualização desde 14:32 ... Mostrando o último estado conhecido" + "Tentar agora".
- Celular: uma coluna, resumo no topo ("2 trabalhando · 1 na fila · 1 falhou"), "Todos" recolhido, toque de 44 px.

## Alternativas
- **A (recomendada):** seções Atenção / Agora / Todos acima da lista atual. Mudança menor, vale igual no celular.
- **B:** duas abas, "Ao vivo" e "Catálogo". Isola a edição, mas esconde a atividade atrás de um clique.

## Dúvidas
1. Aprovação pendente conta como estado do agente? (recomendo sim)
2. Limite do "mais que o normal" (sugiro 15 min).
3. Um agente com vários vídeos: uma linha com lista?
4. Agentes de outros setores aparecem nessa aba?

## Outros 3 pontos de usabilidade
1. Aviso de erro some em 7 s, sem fechar nem histórico (`aviso()`, `app.js:32`).
2. "Atualizado há X" não avança sozinho; só muda quando os dados mudam.
3. Menu principal não mostra falha nem espera de aprovação quando se está em Agentes/Fluxos.
