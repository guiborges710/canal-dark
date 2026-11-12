# Entrega PROG-024 (Endrick, 12/11/2026)

**Problema:** `ecossistema/app/index.html` (commit 8853702) virou uma tela de login com senha e valores reais escritos no código; a Finanças (024a/024b) deixou de abrir e o e2e dava exceção.

**Correção:** `index.html` restaurado como casca da Finanças (carrega `dados_demo.js`, `base.js`, `comum_gh.js`, `financas.js`), sem login falso e sem valor fixo. `login.html` ficou intocado, sem uso.

**Teste primeiro:** novo caso em `estudio/testes/e2e_financas.mjs` (index sem senha/auth e sem R$ fixo). Antes da correção: 2 ok, 1 falha (exceção). Depois: ver abaixo.

**Resultados reais:**
- `node estudio/testes/e2e_financas.mjs`: ver linha final registrada na decisão (0 falhas).
- `PYTHONPATH=. python -m estudio.testes.testar_financas`: 59 ok, 0 falhas; `..._edicao`, `..._edicao_http`, `..._gravar_atomico`: OK.
- Caso de erro e estado vazio já cobertos pelo e2e (dados atrasados/divergentes, mês vazio, sem `meses`).

**Alerta ao Guilherme:** o commit 8853702 já colocou no histórico git a senha `ecossistema123` e saldos/pendências reais em `index.html`. Se o repositório for ou for ficar público, é preciso trocar a senha e reescrever o histórico. Não mexi no histórico.
