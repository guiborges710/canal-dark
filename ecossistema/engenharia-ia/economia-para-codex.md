# Economia de tokens para o Codex (2026-11-03)

Autor: **Valverde**. Tokens são estimativa (bytes / 3,8). Medido: `CLAUDE.md` 18.952 B; **Vini** 2.093 B; **Courtois** 1.329 B; **Neymar** 1.971 B. A pasta já tem `economia-possivel.md` com a lista completa; aqui estão só os cortes rápidos, prontos para aplicar.

## Situação
Eu não apliquei nenhum corte. Texto de agente é do **Luiz Henrique**, `CLAUDE.md` é do dono, e corte de filtro do **Vini** ou do **Courtois** exige proposta com risco declarado e aprovação do Guilherme. Abaixo está o texto novo, pronto para colar. Depois de aplicar, rodar `python tools/sincronizar_codex.py`.

## Corte 1. Vini TEXTO: 5 perguntas, sem reler `notas.md` (economia alta, risco baixo)
Hoje o **Vini** relê `notas.md` (mediana 10 KB, máx. 37 KB) e refaz o que a `revisao.md` do **Courtois** já registrou.
Texto novo para a seção Procedimento (modo TEXTO):
```
Modo TEXTO. Leia só: CONFORMIDADE.md (saída de `python run.py check`), revisao.md, roteiro.txt, metadados.json e os textos de cena. NÃO releia notas.md: o Courtois já conferiu fato contra nota; confie em revisao.md.
Responda apenas:
1. O CONFORMIDADE.md tem alguma infração? (se sim, bloqueia)
2. Título, descrição e tags prometem o que o roteiro entrega, sem isca de outro tema?
3. Há conteúdo sensível ou tom desrespeitoso com vítimas?
4. A descrição traz o aviso de animação gerada por computador?
5. A revisao.md do Courtois está fechada (sem item pendente)?
Escreva auditoria_texto.md com APROVADO/BLOQUEADO e só os itens que falharam.
```
Risco: o **Vini** deixa de pegar nota errada que o **Courtois** deixou passar. Mitigação: `compliance.py` continua checando fontes e texto copiado sem tokens.

## Corte 2. Vini FINAL: só metadados (economia alta, risco zero)
Já é a regra do dono (2026-11-03): depois do render nada audiovisual bloqueia. Texto novo: "Modo FINAL: leia só `metadados.json`, `PUBLICAR.txt` e `CONFORMIDADE.md`. Não reabra imagem, áudio nem animação. Uma linha por resultado; sem tabela de 'OK'." Evidência do desperdício: `jovens-bebendo-menos/auditoria.md` com 10 KB, 31 itens e 3 passes.

## Corte 3. Courtois: dono único de fato, gancho e porcentagem (economia média, risco baixo)
Acrescentar à definição: "Você é o único dono de: fato x nota, gancho que promete demais, 1/3 de comentário próprio e limite de 2 números. Registre em `revisao.md` só o que mudou ou o que ficou em dúvida, sem listar itens 'OK'." O **Vini** passa a só ler esse resultado (Corte 1). Risco: concentrar falha num agente só; por isso o **Courtois** continua em sonnet.

## Corte 4. `CLAUDE.md`: mover "Arquitetura do código" e "Comandos" (economia alta, a confirmar)
São ~4,3 KB + ~1,9 KB (medidos antes) que só o dev usa. Proposta: mover para `docs/arquitetura.md` e deixar uma linha de ponteiro no `CLAUDE.md`. Isso corta ~30% do arquivo carregado em cada chamada, **se** ele entra em cada subagente (não confirmei). Arquivo do dono: precisa aprovação do Guilherme. Nenhuma regra inviolável está nessas seções.

## Corte 5. Backlog e README: ler por item (economia média)
`programacao/backlog.md` tem 34 KB e `ecossistema/README.md` 15 KB, lidos inteiros. Em cada agente de programação, trocar "leia o backlog" por "use `Grep` para achar o item `PROG-nnn` e leia só esse trecho". Quem aplica: **Luiz Henrique** (definições) e **Zico** (backlog). Observação: o backlog não está em `backlog.md` na raiz; está em `programacao/`.

## Estimativa de ganho (não medida)
Cortes 1 a 3 reduzem a leitura do **Vini** de ~4 arquivos grandes para ~4 pequenos por vídeo, e a saída de ~10 KB para poucas linhas. Corte 4 dá a maior economia por chamada. Somados, plausivelmente passam de 20% por vídeo, mas **não medi** antes e depois; para medir, comparar `custo.json` e os tamanhos de `auditoria*.md` nos 3 próximos vídeos.

## Ordem sugerida
2, 1, 3 (texto de agente, sem risco novo ou baixo), depois 5 e 4 (arquivos de outros donos).
