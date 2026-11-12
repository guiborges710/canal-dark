# Entrega PROG-001 · motivo de "não se aplica"

Data: 2026-11-04. Responsável: **Endrick**. Pronto para nova validação do **Alisson**.

## O que mudou na tela

- A etapa continua mostrando a regra real que a tornou não aplicável.
- Agora também mostra o próximo passo quando existe uma saída: criar pelo Corte sem `--mock`, iniciar pelo Corte em vez de importar do terminal, atualizar o formato das cenas ou adicionar falas.
- A orientação aparece no computador e no celular, sem rolagem horizontal.
- Etapa aplicável não recebe esse aviso (caso vazio/normal).

## Arquivos

- `estudio/web/app.js`
- `estudio/testes/e2e_interface.mjs`
- `estudio/testes/e2e_celular.mjs`
- `estudio/testes/testar_prog001_002.py`

## Testes e resultado real

- Antes da mudança: `node estudio/testes/e2e_celular.mjs` detectou o vermelho esperado: o motivo aparecia, mas faltava o próximo passo.
- `.venv\Scripts\python.exe estudio\testes\testar_prog001_002.py` → passou; inclui `sketch`, `cartoes`, `cartoon_alive` e `documentary_collage`.
- `node estudio/testes/e2e_interface.mjs` → 120 verificações ok, 0 falhas.
- `node estudio/testes/e2e_celular.mjs` → 63 verificações ok, 0 falhas.
- `node estudio/testes/e2e_corte.mjs` → 152 verificações ok, 0 falhas.
- `node estudio/testes/e2e_estilos.mjs` → 98 verificações ok, 0 falhas (repetição isolada; a primeira execução paralela teve uma falha transitória fora do PROG-001).

Caso de erro: motivo ausente ainda cai numa explicação genérica legível, sem inventar regra. Caso vazio: etapa aplicável não mostra aviso de "não se aplica".
