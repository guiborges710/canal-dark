# Entrega PROG-025 — casca do app (Endrick, 2026-11-12)

**Estado:** bloqueada por regressão. Nenhum arquivo alterado por mim nesta rodada.

## O que encontrei
- `ecossistema/app/index.html` e `login.html` foram sobrescritos em 11/11 às 22:17 (depois da última bateria verde). O `index.html` agora é uma tela simples "Ecossistema / Entrar" com usuário e senha escritos no próprio HTML, e um painel fixo com valores financeiros digitados à mão. Não é a casca dos 8 grupos.
- A pasta `ecossistema/app` não está no Git (untracked), então não há versão anterior para restaurar com segurança.

## Teste rodado
`node estudio/testes/e2e_financas.mjs` → **2 ok, 1 falha** ("exceção": `.nav-dica` não existe, porque a página mostra o login). Antes (QA de 11/11): 194/194. Falhou antes de chegar aos oito grupos, Ctrl K e temas.

## Também
PROG-032 segue com 5 P0 faltando (avatares Casemiro, De Bruyne, Luiz Henrique, Ronaldo e `vazio_espera`), então a validação integrada final também não é possível ainda.

## Para destravar
1. Quem criou o login (22:17) confirmar se foi intencional; senha em HTML não deve ficar no projeto.
2. Restaurar a casca (index.html) — possível ponto de partida: `ecossistema/prototipo_estilos/h/financas/index.html`, a conferir.
3. Rodar de novo a bateria (esperado 194/194) e fechar com os P0 do 032.
