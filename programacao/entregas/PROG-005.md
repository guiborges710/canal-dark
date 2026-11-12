# Entrega PROG-005 · Atualizar testes e2e antigos (Rodrygo, 2026-11-04, versão final)

## O que mudou
- `estudio/testes/e2e_corte.mjs`: o `.catch(() => true)` vazio virou asserção real (sem `se_sketch` e com `narracao`, mais narração `ignorado` com parecer BLOQUEADO). O `.catch(() => {})` da l.422 (`ap("ap_componentes")`) agora tem comentário dizendo por que é tolerado.
- `estudio/testes/e2e_estilos.mjs`: o **Raphinha** agora precisa ser acionado e receber as regras do Cartoon Vivo (mais forte que antes); a variação do Caderno pautado chega a ele. A falha antiga ("Raphinha não observado") não se repetiu.
- `se_sketch` só aparece como asserção de ausência/comentário (guarda contra o nó voltar ao fluxo padrão).
- `estudio/README.md` (l.159-173): comandos das baterias, o que cada uma mede, `E2E_PORTA` com as portas padrão e o aviso para rodar uma bateria por vez.

## Resultados reais
- QA do **Alisson** (isoladas, mock): e2e_interface 120/0, e2e_corte 152/0, e2e_estilos 98/0, e2e_celular 63/0, testar_estilos.py 103/0.
- Rerodada minha agora: `E2E_PORTA=18893 node estudio/testes/e2e_estilos.mjs` → **98 ok, 0 falhas**.
- A primeira rodada em paralelo teve 1 falha e MemoryError (disco C: quase cheio); repetidas sozinhas passaram.

## Pendente
- **Alisson** repetir `e2e_estilos` 2x seguidas isolado (pedido do **Thiago Silva**; já tenho 1 passagem limpa) e o aceite do **Zico**.
