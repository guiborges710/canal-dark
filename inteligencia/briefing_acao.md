# Briefing para o setor de ação

Mantido por **Vitinho**, a partir de `relatorios/semana_2026-11-09.md`. Só entra item com evidência suficiente. O setor de ação ainda não existe: quem executar hoje é o De Bruyne com os agentes de produção.

Status: **ciclo 5 concluído (2026-11-09).**

## Aviso principal

O canal tem 24 vídeos, ~220 views, mediana ~0,2 view/dia. O melhor tem 74 views. O CTR vem de 8 a 83 impressões digitadas à mão. **Nada abaixo é regra.** Cada item é um teste de baixo custo: mudar uma coisa por vez, anotar o resultado, e só chamar de padrão com 5 ou mais ocorrências e algumas centenas de impressões. O nível de evidência de todos é **fraco a médio**; o de medição é **forte**.

Regras que valem para todos os itens: nada que viole políticas do YouTube; respeito às vítimas; gancho do próprio tema do vídeo (sem isca de assunto alheio); o vídeo entrega o que o título promete; nunca copiar outro canal, só testar padrões que o nosso canal pode fazer.

## Ações para melhorar os Shorts (ordem de prioridade)

### 1. Medir cada Short novo: CTR, impressões e número de cenas
- **O que fazer:** anotar em `ctr_manual.csv` as impressões e o CTR de cada Short novo e dos de 11-04 e 11-06; anotar o número de cenas e a cena média.
- **Hipótese:** sem isso, as ações 2 a 6 não se confirmam nem se descartam.
- **Evidência:** `metricas/canal_2026-11-09.md`, `relatorios/semana_2026-11-09.md` (lacunas 1 e 3). Nível: **forte**.
- **Como testar:** coluna preenchida em 100% dos Shorts novos, 3 dias depois de cada postagem.

### 2. Título: dilema no centro, número fora do começo
- **O que fazer:** nos próximos 3 a 4 Shorts, variar a estrutura do título e registrar qual foi usada. A: dilema de duas opções ("faz X ou não consegue Y?"). B: pergunta que testa uma crença, com o tema em palavra do dia a dia (filhos, morar com os pais). C (controle): rótulo ou dado no começo. Dado, quando houver, só depois do tema. Alternar o fecho "o que os dados mostram" com outros ("depende de quê?"). Se possível, ~40 a 50 caracteres, com o tema nos primeiros 40.
- **Hipótese:** o dilema gera mais clique que o número seco; o fecho repetido perde força. A causa pode ser o tema e não a estrutura.
- **Evidência:** o nº 1 (74 views, CTR 5,2% sobre 58 impr.) e o nº 2 têm pergunta ou dilema; `nem-nem` 0% sobre 83 impr. e `esquema-de-piramide` 0% sobre 21 impr. abrem com número ou rótulo. (`titulos/padroes_2026-11-09.md` §2 e §3). Nível: **fraco** (2 casos a favor).
- **Como testar:** CTR por estrutura em `ctr_manual.csv`. Só vira regra com 5 Shorts por estrutura.
- **Risco:** o dilema tem de ter dado dos dois lados nas notas e ser entregue no vídeo; sem isca, sem "você está perdendo".

### 3. Frame 0: situação ou pergunta, sem estatística, com uma etiqueta de uma palavra parada
- **O que fazer:** manter o gancho do `CLAUDE.md` (situação concreta antes de dado). Em 1 ou 2 Shorts, abrir com uma etiqueta de uma palavra parada nos 3 primeiros segundos. Como variação, testar um frame 0 partido em duas metades (rótulo x contexto), com o mesmo boneco de palito nos dois lados e expressão diferente; o contraste vira traço preto x traço colorido. Rótulos entre ~15% e ~70% da altura do quadro, 1 a 3 palavras por metade, todo texto escrito por código.
- **Hipótese:** o gancho visual retém os primeiros segundos; a divisão ilustra a tese ("geração é rótulo; contexto é explicação") sem número.
- **Evidência:** o vídeo de retenção 76% abre com cena de 5,9 s e etiqueta de uma palavra (`producao/padroes_2026-11-09.md` §4); o Short do Sr. Stickman usa dois mundos num quadro (`thumbnails/` §1.1; 1.481 views, 1 canal). Nível: **fraco**. A parte da divisão depende de conferência do Hugo (se o quadro é o frame 0).
- **Como testar:** retenção nos primeiros 3 a 10 s e retenção final, comparando com Shorts sem a etiqueta ou sem a divisão.
- **Risco:** a divisão muda o estilo do caderno pautado; precisa de autorização do dono. Não repetir o erro do concorrente de texto fora da área segura ou quebrado por IA.

### 4. Ritmo e cenas: 6 a 7 cenas, cena média de ~9 s, em dois Shorts
- **O que fazer:** produzir 2 Shorts de sketch com 6 a 7 cenas, cena média de ~9 s e primeira cena de ~6 s, e comparar com os de 9 e 10 cenas quando houver retenção. Manter o limite de 2 números por Short (`prompts/tipos_de_roteiro.md`), já que `divisao-politica` tem ~9 e `fim-dos-terceiros-lugares` 4.
- **Hipótese:** menos cortes e menos números seguram mais. Contra: o vídeo de 76% tem 6 números falados.
- **Evidência:** 76% de retenção em 6 cenas; 9 e 10 cenas sem retenção ainda (`producao/` §4; `metricas/` hipótese 3). Nível: **fraco**.
- **Como testar:** retenção de `divisao-politica` e `fim-dos-terceiros-lugares` na próxima coleta; depois, dos 2 Shorts de 6 a 7 cenas. Só comparar com tema parecido.
- **Risco:** um caso só; conferir a regra dos números antes de cortar cena.

### 5. Thumbnail: palavra-tema única com cor própria, resto neutro
- **O que fazer:** para o que a busca e a página do canal mostram, usar uma palavra-tema (1 a 3 palavras), uma cor de destaque (amarelo ou vermelho-laranja) sobre papel claro e o boneco de palito como assinatura. O prompt é do **Sidorf**; texto sempre sobreposto por código, nunca desenhado pela imagem gerada.
- **Hipótese:** a palavra-tema aumenta o clique em busca e na página do canal. Em Shorts, o feed mostra o vídeo, então o efeito pode ser nulo.
- **Evidência:** padrão em 2 de 2 longos do Sr. Stickman, Koo, ipe, Show de Informações (`thumbnails/padroes_2026-11-09.md` §3), sem CTR. Nível: **fraco**.
- **Como testar:** CTR de busca por vídeo, separando por fonte de tráfego quando o Analytics permitir.
- **Risco:** sem rosto de pessoa real; nada de rótulo de tipo de pessoa; sem promessa de saúde ou ganho.

### 6. Legenda (teste pequeno, depende do dono)
- **O que fazer:** testar, em 1 ou 2 Shorts, legenda grande no meio do quadro em trechos curtos que seguem a fala, e comparar com sketch sem legenda.
- **Hipótese:** a legenda palavra a palavra segura quem assiste sem som.
- **Evidência:** presente em 3 de 4 canais novos, com 200 a 4 mil views (`producao/padroes_2026-11-09.md` §5). Nível: **fraco**. Não se sabe se segue a fala.
- **Como testar:** retenção média comparada ao Short mais parecido sem legenda.
- **Risco:** contraria o estilo sketch ("sem legenda na base"); só com decisão do dono. Em Shorts, a legenda não pode cair na faixa do app (~80% a 95% da altura).

## Ações de medição e de coleta (herdadas, atualizadas)

- **Escopo de analytics:** o Analytics de 21 vídeos já veio neste ciclo (janela 10-08 a 11-09). O item de 11-01 está atendido; manter o consentimento válido. CTR/impressões seguem manuais.
- **Privacidade:** o coletor registra que não há vídeo privado nesta coleta. O item de 11-01 está atendido.
- **Coleta diária:** manter, no mesmo horário.
- **Ligar slug a vídeo:** 9 dos 24 vídeos continuam `sem-pasta`. Preencher o slug nos que ainda têm pasta.
- **Descrição, tags e hashtags de terceiros:** 6º ciclo sem coleta; o Hugo deve gravar `snippet.title` nas fichas e coletar os campos de 5 vídeos por canal.
- **Caracteres visíveis do título no celular:** continua sem medição.

## Decisões que dependem do Guilherme

1. **Os 3 vídeos longos** (`8ho4eV51O5E`, `dypjMpqhWlo`, `Un0RCLhs2TI`) estão fora do formato Shorts. Manter, ocultar ou apagar? Dados: retenção 1% a 18%; o 8ho4 tem 21 views e CTR 6,9%. Sem pressa técnica, mas é uma incoerência com o `CLAUDE.md`.
2. **Subir em `aprendiz/_entrada/` um Short do Sr. Stickman (`2XhkMfTG4SQ`) e um da Mente Primitiva (`8gyHhIPc4Ew`)** para o **Busquets**. É o único jeito de ouvir voz, cronometrar o gancho e ver se a legenda segue a fala. Nenhum agente baixa vídeo de terceiros.
3. **Colar as 6 linhas de `thumbnails/catalogo_adendo_2026-11-09.md` no final da tabela de `thumbnails/catalogo.md`.** O **André Carrillo** não tinha ferramenta de edição neste ciclo.
4. **Autorizar (ou não) os testes que mudam o estilo sketch**: legenda no meio do quadro (item 6) e frame 0 partido em duas metades (item 3).
5. **Setor de ação e agendamento do ciclo:** segue sem definição.

## Pedidos registrados aos outros agentes

- **Hugo Souza:** gravar `snippet.title` nas fichas dos 4 canais novos (e nas próximas); conferir se o Short `2XhkMfTG4SQ` usa o quadro dividido como capa e como frame 0; conferir onde estão os textos desse Short.
- **Yuri Alberto:** registrar o número de cenas por vídeo; registrar impressões/CTR dos vídeos novos; trazer retenção de política e terceiros na próxima coleta.
- **Xabi Alonso:** colocar os dois Shorts acima na fila quando o Guilherme confirmar; preferir Shorts de até 60 s em pt-BR.

## Fora do briefing por falta de evidência

Hipóteses H1 a H12 do relatório que não viraram item acima: título curto de ~40 caracteres como regra, hashtag no título, duração acima de 60 s, volume diário como estratégia, vídeo longo com título de busca. **Não adotar:** estilo 3D de IA em série (Skeleton Science), promessa de saúde ou ciência não verificada (Sr. Stickman), "defeito" clínico simplificado (Mente Primitiva), produção em massa com repetição (Story Toon), texto escrito pela IA dentro da imagem, tom de alarme ("CUIDADO") e rótulos de tipo de pessoa.

Formato de cada item: **O que fazer / Hipótese / Evidência e nível / Como testar / Risco.**
