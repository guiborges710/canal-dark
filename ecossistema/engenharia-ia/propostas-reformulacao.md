# Propostas de reformulação (2026-11-03)

Todas são **proposta**. Nenhuma foi aplicada. Aplicador do texto de agente: **Luiz Henrique**, depois do aval do Guilherme. Código (`compliance.py`, `media/`, `run.py`, gate do `publish`): **Thiago Silva**/**Rodrygo** pelo quadro da sprint.

Intocáveis (não propostos para corte): políticas do YouTube e monetização, tom com vítimas, fatos só das notas com 3+ fontes, congelamento do roteiro e do vídeo, ação externa só com confirmação, decisões explícitas do Guilherme (nicho, estilos, tipos de roteiro, tom de gancho de 2026-10-27).

Ordem: economia contra risco. Economia em tokens é estimativa (bytes / 3,8).

| # | Proposta | Economia | Risco | Esforço | Dono |
|---|---|---|---|---|---|
| P1 | **Vini FINAL**: só metadados e miniatura | Alta | Baixo | Texto | Luiz Henrique |
| P2 | **Vini TEXTO**: 5 perguntas, sem reler `notas.md` | Alta | Baixo-médio | Texto | Luiz Henrique |
| P3 | **Courtois**: dono único de fato, gancho e % próprio; saída só com exceções | Média | Baixo | Texto | Luiz Henrique |
| P4 | **Modric**: `notas.md` com teto de ~6 KB e formato tabela | Alta | Médio | Texto | Luiz Henrique |
| P5 | Fala em fonte única (script) | Média | Baixo | Script | Rodrygo |
| P6 | **De Bruyne**: handoff curto, definição enxuta | Média | Baixo | Texto | Luiz Henrique |
| P7 | `CLAUDE.md`: mover "Arquitetura" e "Comandos" para `programacao/arquitetura.md` | Alta (a confirmar) | Baixo | Doc do dono | Guilherme/Luiz Henrique |
| P8 | Backlog e README por demanda | Alta | Baixo | Doc | Xavi/Zico, Luiz Henrique |
| P9 | Modelos: **Olise**/**Raphinha** | Média | Médio | Texto | Guilherme decide |
| P10 | Setor de inteligência: leitura única e resumo | Média | Baixo | Texto | Luiz Henrique |

---

## P1. Vini FINAL: só metadados e miniatura

Problema: a regra de 2026-11-03 diz que depois do render só metadados e miniatura podem bloquear; o resto é observação sem ação. Mesmo assim o modo FINAL abre quadros, mede áudio e reaudita v2 e v3 (31 itens em `jovens-bebendo-menos/auditoria.md`).

Corte: itens F1 a F5 e F8 de `analise-vini-courtois.md`. `ffprobe` e formato passam para `run.py check` (tarefa de código).

Risco real: uma observação audiovisual que nunca poderia ser agida deixa de ser escrita. Isso **não** toca o congelamento, que continua. Nenhuma checagem de política sai: sensível e título honesto ficam.

Texto novo sugerido para a seção "Procedimento" do **Vini**:

```
## Modo FINAL (depois do render)
Só decide sobre metadados e miniatura. Leia: CONFORMIDADE.md, metadados.json, thumbnail.jpg (uma imagem) e roteiro.txt (só para comparar com o título).
Bloqueie apenas por: título/descrição/tags/miniatura enganosos, isca de assunto alheio, conteúdo sensível explorador, aviso de animação/voz sintética ausente.
Qualquer observação de imagem, som ou narração: no máximo 3 linhas em "Observações", sem tabela e sem pedir mudança.
Se o pacote já foi aprovado e só mudou o vídeo (nova versão autorizada pelo Guilherme), reaudite só se metadados.json ou a miniatura mudaram.
Saída: auditoria.md com APROVADO ou BLOQUEADO na primeira linha, bloqueios (se houver) e Observações. Máximo ~1,5 KB.
```

## P2. Vini TEXTO: cinco perguntas

Problema: 17 itens, 13 "OK", e os itens de fato, gancho e % próprio repetem o **Courtois**; `notas.md` (até 37 KB), `sketch_cenas.py` e todos os outros roteiros são relidos.

Risco real: um erro de fato que o **Courtois** deixe passar não seria pego pela segunda leitura. Mitigação: o **Courtois** registra em `revisao.md` as linhas "não verificado na origem" e o **Vini** as lê. A regra de 3+ fontes continua automática (`compliance.py`, domínios distintos) e o **Courtois** continua obrigado a rejeitar o que não tem apoio. É a mesma segurança com um leitor a menos, não com nenhuma checagem a menos.

Texto novo sugerido:

```
## Modo TEXTO (antes do render)
Rode `python run.py check --topic "<tema>"` e leia CONFORMIDADE.md. Leia também revisao.md (Courtois), roteiro.txt, metadados.json e a tese do angulo.md. NÃO releia notas.md, sketch_cenas.py nem outros roteiros: fato é do Courtois, repetição é do check.
Responda só a cinco perguntas, uma linha cada:
1. O vídeo pode ser lido como conteúdo inautêntico, repetitivo ou reutilizado? (use o % próprio e o aviso de cópia do check)
2. Há conteúdo sensível, ou tom com vítimas que precise de cuidado?
3. Título, descrição e miniatura dizem o que o roteiro entrega? Há isca de assunto alheio?
4. Há pedido de curtir, comentar ou inscrever que seja isca (engagement bait)?
5. O check marcou algo em ATENÇÃO ou FALTA que ainda não foi tratado? Algum "não verificado na origem" da revisao.md sustenta uma frase do vídeo?
Veredito APROVADO/BLOQUEADO na primeira linha. Bloqueia: infração de política, fato sem apoio nas notas, falta de ângulo. Resto é Observação. Aprovar congela roteiro.txt. Máximo ~1,5 KB.
```

## P3. Courtois: dono único de fato

Corte: C3 (cópia, já no `check`), C4 (legibilidade na tela), C7 (contagem de números, vai para `media/roteiro.py`), tabela de itens "OK".
Mantém: C1/C2 (fato x nota), C5 (gancho), C6 (1/3 próprio), C8 (sobrescrever `roteiro.txt`).
Risco: baixo. A contagem de números por texto "pode errar por um ou dois" (o próprio módulo diz); o **Vini** vê o aviso no `check`.

Texto novo sugerido (substitui a seção "O que fazer" e "Saída"):

```
## O que fazer
Compare roteiro.txt com notas.md. Você é o único dono de fato, gancho e comentário próprio.
1. Remova ou reescreva afirmação sem apoio, exagerada, ou número sem fonte (3+ fontes). Marque o que ficou "não verificado na origem".
2. Gancho: confirme que o vídeo entrega o que a abertura promete e que o tema é o do vídeo.
3. Comentário próprio: confirme que o texto tem pelo menos 1/3 de análise própria. Use a contagem do Neymar em roteiro_notas.md e só recalcule se estiver abaixo de 40%.
4. Números: rode `python -c "from media import roteiro; print(roteiro.numeros(open('output/<slug>/roteiro.txt',encoding='utf-8').read()))"`. Se passar de 2 ou houver número na abertura, corte o menos importante sem mudar o sentido.
5. Só se uma palavra puder ser lida errado pela voz sintética (ex.: "Gen Z"), sugira a forma falada.
## Saída
1. Sobrescreva roteiro.txt (só o texto do vídeo).
2. revisao.md: veredito na 1ª linha; "Corrigido" (antes/depois/motivo); "Não verificado na origem"; % próprio. NÃO liste itens OK. Máximo ~1,5 KB.
Se faltar roteiro.txt ou notas.md, pare e diga o que falta.
```
(Isso exige adicionar `Bash` às `tools` do **Courtois**.)

## P4. Modric: `notas.md` com teto

Problema: `notas.md` é lido por **Neymar**, **Courtois**, **Vini** e outros; temas chegam a 23 e 37 KB. Cada KB poupado se multiplica por 4 a 5 leituras.

Risco médio: cortar contexto pode tirar uma fonte ou um contraexemplo que sustenta a tese. Por isso o teto é de formato, não de fonte: as 3+ fontes e os "NÃO USAR sem conferir" ficam.

Texto novo sugerido (acrescentar ao final do **Modric**):

```
## Formato de notas.md (teto de ~6 KB)
Tabela única: id | afirmação (1 frase) | número/data | fonte (URL) | grau (PRIMÁRIA/ALTA/MÉDIA).
Depois, em até 10 linhas: "Situações do dia a dia" (com fonte), "Divergências" e "NÃO USAR sem conferir".
Sem resumo de artigos, sem cópia de trecho, sem "contexto geral". Pesquisa que passe de 6 KB: guarde o excedente em `notas_extra.md` (que ninguém lê por padrão).
```

## P5. Fala em fonte única (script)

Hoje: a fala existe em `roteiro.txt`, em `direcao_viral.md` (`## Narração`) e em `cenas.json`. **Courtois**, **Olise** e **Vini** garantem que são iguais.

Proposta (código, não texto): `tools/` um script que (a) deriva ou confere `roteiro.txt` a partir de `## Narração` e (b) preenche `fala` no `cenas.json` a partir dela. O **Olise** deixa de copiar texto; `run.py check` falha se divergir.
Risco baixo; economia: some um item de conferência em três agentes e a chance de uma divergência entrar depois da aprovação (o que violaria o congelamento).

## P6. De Bruyne: handoff curto

Problema: definição de 9,4 KB (carregada a cada turno do orquestrador); tabela de dependência e "Ondas" dizem a mesma coisa duas vezes; cada briefing repete os caminhos.

Proposta: manter só a tabela; apagar "Ondas"; briefing padrão de uma linha: "`<slug>`; leia o que o seu contrato manda; salve só o seu arquivo". Remover as menções a **Messi** e **Cristiano** do mapa (ficam só como agentes sob demanda no `CLAUDE.md`). Remover a repetição da regra de congelamento (ela já está no `CLAUDE.md` e no **Vini**).
Risco baixo: o contrato por agente está em cada definição e no `CLAUDE.md`.
Esperado: -2 a -3 KB (~600 a 800 tokens por turno do orquestrador, estimativa).

## P7. `CLAUDE.md` mais curto

Mover "Arquitetura do código" (4,3 KB) e "Comandos" (1,9 KB) para `programacao/arquitetura.md`, que só o setor de programação lê; deixar um link de uma linha no `CLAUDE.md`. Resultado: de 18,9 KB para ~12,7 KB (-33%). Em cada chamada de subagente, ~1.600 tokens a menos, **se** subagentes carregam o `CLAUDE.md` (confirmar). Risco baixo: os agentes de produção não usam essas seções; o **De Bruyne** usa os comandos, que podem ficar como bloco de 4 linhas.
Dono: arquivo do Guilherme; aplicação por **Luiz Henrique** após aprovação.

## P8. Backlog e README por demanda

- `programacao/backlog.md` (34 KB): mover os itens "Feito" para `programacao/backlog_arquivo.md`; agentes leem só o ativo e o item citado.
- `ecossistema/README.md` (15 KB): criar `ecossistema/mapa-resumo.md` (~3 KB, tabela de agentes e setores) e usar o resumo no "Leia antes" dos agentes de programação e pessoais; o completo fica para **Luiz Henrique**.
- **Ronaldo**: deixar de ler o `ecossistema/README.md` a cada mensagem; usar só `produtividade/README.md` e o roteamento.
Risco baixo; economia alta por ser relido muitas vezes por dia.

## P9. Modelos e passes

- **Olise** e **Raphinha** em opus com effort high são as duas leituras mais pesadas do fluxo diário. Proposta: testar **Olise** em sonnet effort medium em 3 vídeos e comparar a prévia; manter **Raphinha** em opus só na fase "aprendendo". Risco médio (qualidade do desenho, que é decisão visual do Guilherme): **não mudar sem aprovação dele**.
- **Vini** TEXTO em sonnet (julgamento de política); **Vini** FINAL em haiku (leitura de metadados/miniatura) depois de P1.
- **Messi** e **Cristiano**: sem custo se ninguém os chamar. Manter como estão, mas tirar do mapa de dependências do **De Bruyne**.

## P10. Setor de inteligência: leitura única

- **Fagner**, **André Carrillo** e **Raniele** leem as mesmas 17 fichas de canal. Proposta: `inteligencia/canais/_indice.md` com uma linha de resumo por ficha (título, nicho, formato, links), e cada analista abre a ficha completa só do canal que vai citar.
- **Vitinho** lê só os relatórios `padroes_*.md` mais recentes de cada pasta, não todos os arquivos.
- `inteligencia/fontes.md` (24 KB): ninguém além do **Hugo Souza** precisa lê-lo; marcar como "só para acrescentar".
- WebSearch: **Hugo Souza** já usa modo padrão; manter.
Risco baixo.

---

## Ordem sugerida de aplicação
1. P1 e P2 (**Vini**) e P3 (**Courtois**): só texto de agente, maior ganho por risco. Juntas atacam os "filtros à toa" que o Guilherme citou.
2. P4 (**Modric**): economia em cadeia, risco médio controlado pelo formato.
3. P5 (script) e o item `ffprobe` do `check`: entram na sprint de programação.
4. P6, P7, P8, P10: higiene de contexto.
5. P9: só com decisão do Guilherme.

## O que eu preciso que o Guilherme decida
1. Aprova cortar o modo FINAL para metadados e miniatura (P1)? Isso não toca o congelamento.
2. Aprova que o **Courtois** seja o único dono de fato, gancho e % próprio, e que o **Vini** confie na `revisao.md` (P2/P3)?
3. A intenção é manter o modo FINAL como agente ou transformá-lo numa checagem de código? (afeta o gate do `publish`.)
4. Quer testar **Olise** fora do opus (P9)?
