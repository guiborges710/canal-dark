# PROG-026 · Refinamento técnico: servidor único do dashboard

**Decisão:** estender o processo HTTP do Corte (`estudio.servidor.Manipulador`) com rotas explícitas para a casca do sistema e seus recursos autorizados. Não criar outro servidor nem implementar um endpoint genérico que receba caminhos de arquivos. O PROG-026 é infraestrutura para o dashboard do ecossistema; a interface e os dados de cada setor permanecem responsabilidade dos itens próprios.

## Abordagem mínima

1. Servir a casca e os assets do dashboard por prefixos explícitos, com uma raiz estática dedicada e resolvida (`Path.resolve()`), validando que o destino continua dentro dessa raiz antes de abrir qualquer arquivo.
2. Implementar `/api/sistema/*` como dispatch por identificadores/rotas conhecidos. Para leitura de arquivos necessária à casca, declarar uma allowlist fechada de raízes relativas ao repositório, inicialmente limitada aos recursos públicos e não pessoais que o dashboard precisa. O cliente envia uma chave lógica, nunca um caminho arbitrário. Resolver e conferir a raiz e o destino após normalização; rejeitar `..`, caminhos absolutos, separadores alternativos, symlinks que escapem da raiz e aliases codificados antes de acessar o disco.
3. Manter rotas específicas por método e recurso. Não reutilizar a allowlist de leitura para gravação: cada mutação deve ter rota, schema, tamanho máximo, validação e destino fixos. Sem gravação genérica por caminho.
4. Incorporar `/painel` e `/central` no processo atual sem alterar contratos ou páginas existentes. A migração de lógica do painel do **Ronaldo** fica fora do escopo desta entrega; `produtividade/painel.py` permanece intacto.
5. Capturar erros no limite da rota, responder JSON com status coerente e mensagem segura, e manter o servidor disponível após uma requisição malformada. Não devolver stack trace nem caminho físico ao cliente.

## Segurança e escuta

- Preservar o padrão atual de `estudio.servidor.iniciar()`: bind em `127.0.0.1`; `0.0.0.0` só pelo modo de rede já existente (`--rede`). PROG-026 não ativa rede nem muda autenticação.
- Para rotas do dashboard, manter a política local equivalente a `_so_computador()` (IP de loopback **e** `Host` `127.0.0.1`/`localhost`) para evitar acesso via IP da LAN e DNS rebinding. Para APIs com escrita, conservar a validação de origem e acrescentar proteção contra corpo excessivo.
- Não permitir leitura por rota genérica de `produtividade/`, `financas/`, `.env`, arquivos de acesso, LinkedIn ou `voz/`. Os dados financeiros continuam no fluxo isolado atual; não expor CSV nem snapshot pessoal pelo namespace do sistema.
- A allowlist deve ser constante/configurada no servidor, revisável por teste; não aceitar prefixos parciais, `resolve()` sem checagem de ancestralidade, ou validação textual antes da decodificação/normalização.
- O `ThreadingHTTPServer` pode receber pedidos simultâneos. Escritas persistentes compartilhadas não entram nesta fatia sem lock/idempotência específicos; a unificação de processo, por si só, não torna acessos concorrentes seguros.

## Arquivos previstos

- `estudio/servidor.py`: montagem das rotas, raiz estática e política de acesso.
- Novo módulo em `estudio/` para a allowlist/dispatch do sistema, se isso evitar aumentar a complexidade de `servidor.py` (responsabilidade back-end de **Rodrygo**).
- `estudio/testes/`: bateria nova focada em allowlist, traversal, métodos, Host/origem, falha isolada e compatibilidade das rotas absorvidas.
- `ecossistema/app/` somente para ajustar URL-base/integração da casca quando a rota do servidor estiver definida; mudanças de interface com **Endrick** e validação visual por **Firmino**.
- `qa/PROG-026.md`: evidência do QA, fora da implementação técnica.

O servidor atual já serve `/painel`, `/central` e as rotas `/api/central/*`; `/financas/` também foi acrescentado recentemente sob guarda local e raiz confinada ao app. Preservar esse comportamento e evitar mover/duplicar os arquivos de origem durante a primeira integração.

## Critérios de aceite refinados

1. A casca e os assets autorizados abrem no servidor do Corte, sem iniciar outra porta/processo.
2. `/api/sistema/*` atende somente operações declaradas. Recursos fora da allowlist retornam 403/404; `..`, caminho absoluto, traversal codificado, separador alternativo e escape por symlink são recusados antes de leitura.
3. Verificação de contenção usa caminhos resolvidos e comparação de ancestralidade (ou equivalência segura no Windows), sem confiar só em `startswith` textual.
4. `/painel`, `/central` e endpoints existentes preservam status, payload, autenticação e comportamento anteriores nos fluxos cobertos.
5. Sem `--rede`, o socket continua em loopback. A rota do dashboard recusa Host/IP LAN mesmo que o pedido alcance o processo; com `--rede`, não amplia acesso a rotas locais restritas.
6. Rotas genéricas não servem nenhum dos diretórios/arquivos pessoais vedados no backlog; testes incluem tentativas positivas e negativas.
7. Erro de rota (incluindo JSON inválido ou arquivo ausente) responde com erro legível e o servidor aceita a requisição seguinte.
8. Todas as baterias de regressão listadas em `estudio/README.md` passam sequencialmente e o relatório real é salvo em `qa/PROG-026.md`. Evidência obrigatória antes de declarar pronto.
9. `produtividade/painel.py` não muda.

## Testes exigidos

- Novo `estudio/testes/testar_sistema_unico.py`: allowlist positiva/negativa, traversal plain/URL-encoded, caminho absoluto, separadores Windows/POSIX, symlink escape quando suportado, Host/IP/origem, limites do corpo, GET/POST não declarados, falha sem derrubar servidor e recuperação na requisição seguinte.
- Novo E2E da casca no servidor compartilhado, verificando carregamento de HTML/assets e que chamadas da tela chegam às rotas esperadas.
- Regressão sequencial das baterias de servidor existentes relacionadas à superfície preservada: `estudio/testes/testar_painel.py`, `estudio/testes/testar_ao_vivo.py`, `estudio/testes/testar_status_video.py`, `estudio/testes/testar_cronograma.py`, `estudio/testes/e2e_corte.mjs`, `estudio/testes/e2e_interface.mjs`, `estudio/testes/e2e_celular.mjs` (última para confirmar que `--rede` não ampliou acesso indevidamente). Depois, executar a bateria completa declarada em `estudio/README.md` conforme o critério do backlog.

## Riscos e dependências

- **Risco alto — exposição por path traversal:** mitigado por chaves lógicas, allowlist fechada, resolução física e testes de bypass no Windows.
- **Risco alto — ampliar inadvertidamente dados pessoais:** nenhuma rota genérica para o repositório; endpoints explicitamente aprovados e sem importar módulos de finanças/produtividade para servir arquivos.
- **Risco médio — regressões de compatibilidade:** `/painel` tem guarda local própria enquanto `/central` passa pelo porteiro comum; preservar cada política e testar ambas antes de refatorar compartilhamento.
- **Risco médio — concorrência:** servidor é multithread. PROG-026 não unifica os escritores de Telegram, Clipes ou arquivos de setores. Qualquer gravação compartilhada futura exige item e desenho próprios.
- **Dependência de escopo:** IDs 024–035 são provisórios no quadro; confirmar o cartão/aceite oficial antes de fechar. A decisão de rotas deve listar exatamente quais recursos do dashboard entram na allowlist; se houver dúvida sobre quais dados/setores podem aparecer, devolver ao **Zico**.
- **Sequência:** a casca do PROG-025 e os assets P0 do PROG-032 orientam o consumo das rotas; o PROG-026 pode preparar o servidor sem servir dados de setor não finalizados. PROG-027 depende de 025 e 026.

## Responsáveis

- **Rodrygo** implementa o servidor, dispatch, contenção e testes de back-end.
- **Thiago Silva** revisa a implementação antes do teste formal, com foco em segurança de caminho, escuta loopback e preservação dos contratos.
- **Endrick** ajusta a casca apenas onde a integração exigir URLs/estado do servidor; **Firmino** revisa a interação visual.
- **Alisson** executa as baterias e grava `qa/PROG-026.md`.

## Progresso da implementação (11/11/2026)
- O **Rodrygo** adicionou ao `estudio/servidor.py` as rotas de leitura `/api/sistema/{setores,sprint-ativa,quadro,agentes}` por dispatch fechado e confinou o serving da casca local de Finanças após decodificação e `resolve()`.
- Revisão estática do **Thiago Silva**: sem falha concreta observada nas mudanças. Cobertura HTTP confirma traversal codificado, symlink, Hosts não locais e dispatch fechado; uma prova específica também confirma que `/api/sistema/*` segue indisponível a clientes remotos mesmo quando `--rede` está ativo.
- Testes HTTP da edição e da casca de Finanças: salvamento e regeneração em CSV temporário, recusa de origem externa e Host de rede, traversal codificado, symlink, dispatch fechado, limite de corpo, recuperação após JSON malformado e recusa de rota do dashboard via rede; **9/9 passaram**. O corpo excessivo fecha a conexão e os erros internos não expõem exceção ao cliente.
- Regressão sequencial concluída: painel 202/202, agentes ao vivo 49/49, cronograma 42/42 e status de vídeo 45/45 na repetição (a primeira rodada excedeu transitoriamente o limite de 300 ms). `e2e_interface.mjs` concluiu 149 verificações e falhou em uma dependência de narração do Corte; ainda não se sabe se é preexistente ou regressão.
- Estado: validação parcial. O acesso remoto foi confirmado como recusado. Resta fechar compatibilidade da regressão completa; `e2e_interface.mjs` continua com uma falha nas dependências de narração do Corte. A causa não foi classificada; não alterar o Corte fora do escopo dashboard.
