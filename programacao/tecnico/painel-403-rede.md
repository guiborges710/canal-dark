# Ordem ao Rodrygo: 403 do painel via rede e checagem de Host

De: **Thiago Silva**. Fora do quadro (autorizado pelo Guilherme, 2026-11-09). Origem: `painel-review.md`, achados 1 e 2.

## O que fazer (só `estudio/servidor.py`, ~8 linhas)
Em `_rota_get`, nos ramos `c == "/painel" or startswith("/painel/")` e `c.startswith("/api/painel/")`, antes de servir, chamar um helper:

```python
def _so_computador(self):
    host = (self.headers.get("Host") or "").split(":")[0]
    if acesso.e_local(self.client_address[0]) and host in ("127.0.0.1", "localhost"):
        return True
    self._erro("O painel só abre no computador.", 403)
    return False
```
Retornar sem servir se False. Não mexer no `_porteiro` (sem senha: 401 como hoje; com senha de rede: 403; no computador: segue). Manter 403 também para Host estranho vindo de 127.0.0.1 (rebinding).

## Testes
- `estudio/testes/testar_painel.py`: novo caso que simula cliente não local com sessão válida (ou chama o helper) e espera 403 em `/painel`, `/api/painel/visao`, `/documento`; cliente local com Host 127.0.0.1 = 200; cliente local com Host `evil.example` = 403.
- Rodar: `testar_painel.py`, `e2e_celular.mjs` (a página do painel pelo celular passa a ser 403, ajustar a expectativa se existir), `e2e_painel.mjs`, `e2e_interface`.
- Opcional (baixo): parentesar a condição de `painel.area_de` linha 53 e documentar em `decisoes.md` que `painel.RAIZ = config.REPO` (ESTUDIO_RAIZ não isola).

## Retorno
Avisar o **Thiago Silva** para revisão do diff; depois **Alisson** testa.
