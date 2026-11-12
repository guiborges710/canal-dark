# Code review: painel "Ecossistema do Guilherme"

Data: 2026-11-09. Revisor: **Thiago Silva**. Fora do quadro, autorizado pelo Guilherme. Só leitura do código; `estudio/testes/testar_painel.py` rodado: 143 ok, 0 falhas. e2e não rodado por mim.

**Veredito: APROVADO COM RESSALVAS.** Nenhum achado alto.

## Achados por gravidade

### Médio
1. **Sem 403 para /painel e /api/painel/* via rede** (`estudio/servidor.py`, `_porteiro` linhas 55-83 e `_rota_get` 188-191). Quem tem a senha da rede lê o texto bruto de agentes/estratégia pelo celular; o único bloqueio é o front (`corte_painel.js:151`, `corte_nav.js:16`, só escondem o menu e a página). O desenho previa 403. **Decisão: corrigir agora** (pequeno, e a pergunta 3 do refinamento sobre celular não consta como respondida a favor). Ordem escrita em `programacao/tecnico/painel-403-rede.md`, dono **Rodrygo**.
2. **Host não é validado para cliente local** (`servidor.py:61-64`): GET vindo de 127.0.0.1 passa sem checar `Host`. Uma página maliciosa com DNS rebinding conseguiria ler `/api/painel/*` (só POST checa origem). Entra na mesma ordem: exigir IP local **e** Host 127.0.0.1/localhost no painel.

### Baixo
3. **`painel.RAIZ = config.REPO`**: `ESTUDIO_RAIZ` não isola o painel (só `subir_painel_caixa.py` troca `RAIZ` à mão). Além disso `visao()` usa `central`/`ao_vivo`/`status_video`, que seguem no REPO real, e `documento()` usa `RAIZ` enquanto `varrer(raiz=)` aceita outro: dois conceitos de raiz. Aceitar e documentar em `decisoes.md`; não é vazamento (sempre o repo do próprio Corte). Se o e2e for rodado esperando isolamento total, o dashboard mostrará dados reais.
4. **Junction do Windows**: `os.path.islink`/`is_symlink` não pegam junction em Pythons antigos; `_candidatos` poderia entrar numa junction dentro do repo apontando para pasta proibida (ex.: `produtividade`), pois o bloqueio é pelo nome. `documento()` impede só sair do repo (`resolve().relative_to`). Mitigação barata: comparar `Path.resolve()` do arquivo com o caminho esperado. Risco real baixo (exige criar a junction).
5. `area_de` linha 53 mistura `or`/`and` sem parênteses; funciona (`.claude/` é exceção) mas é frágil. Parentesar.
6. `.json` e `.txt` liberados em `.claude/skills` e `programacao/`: o filtro de credencial cobre o corpo; ok, mas é rede de segurança, não garantia.

### Conferido, sem problema
- Lista de permissão com bloqueio por cima (partes, nome, sufixo, `.env*`), `..`, barra invertida, `:` e absoluto recusados; endpoint só serve caminho que está no índice, resposta 404 igual para tudo (não revela motivo). `produtividade/`, `financas/`, `voz/`, `falas/`, `estudio/dados/` fora. Mídia e subpasta de `output/<slug>` fora.
- Links simbólicos: ignorados na varredura e recusados na leitura. Credencial: corpo e título omitidos; releitura na hora de servir.
- XSS: `corte_painel.js` monta tudo por `h()` com `textContent`; nenhum `innerHTML`/`eval`/`srcdoc` no painel. `href` são fixos ou `encodeURIComponent`.
- Servidor em 127.0.0.1 padrão; `--rede` só com senha (401 com página de entrada em `/painel`, linha 74 já inclui). Nada é gravado em disco por `painel.py`.
- Coerência com `programacao/refinamento-painel-unificado.md`: rotas, abas, fonte única `setores.json` (com fallback em `central.py`), resumo de 2 linhas sem IA, lista de permissão e rede de segurança seguem o desenho. Diferenças aceitas: índice só em memória (o desenho dizia `estudio/dados/`; melhor assim) e hook de atividade (fatia 3) não implementado; espelho antigo não desligado (fatia 6, depende do Guilherme).
- Correção do Guilherme: **não existe "visto" nem etiquetas Novo/Alterado** em `painel.py` nem em `painel.html`/`corte_painel.js` (grep limpo; só o comentário que afirma a ausência). Sem estado de leitura gravado. As áreas e o corpo mostram só "alterado em".
