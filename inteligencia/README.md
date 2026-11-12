# Contexto Explica · Setor de Inteligência

Primeiro setor da empresa **Contexto Explica** (o canal). Função: **métricas, análises e atualização de mercado** sobre canais dark, sem produzir vídeo e sem publicar nada. O setor de **ação** (que executa o que este setor recomenda) ainda não existe; será definido depois, com a orientação do Guilherme.

Responsável pelo setor: **De Bruyne** (`debruyne-orquestrador`). Coordena os agentes abaixo e fecha o briefing para a ação.

## Equipe

| Craque | id técnico | Papel | Pasta que ele escreve |
|---|---|---|---|
| **Yuri Alberto** | `yuri-alberto-analista-metricas` | Métricas do próprio canal: o que entregou mais e o porquê (gancho, conteúdo, thumbnail) | `metricas/` |
| **Hugo Souza** | `hugo-souza-pesquisador-canais` | Acha canais dark do nicho e cataloga como um humano faria | `canais/` e `fontes.md` |
| **Fagner** | `fagner-analista-titulos` | Títulos, descrições, tags e hashtags dos canais catalogados | `titulos/` |
| **André Carrillo** | `andre-carrillo-analista-thumbnails` | Thumbnails: composição, texto, cor, rosto ou não, padrão de cada canal | `thumbnails/` |
| **Raniele** | `raniele-analista-producao` | Como o vídeo é feito: animação, voz, ritmo, duração, som | `producao/` |
| **Garro** | `garro-scout-tecnologia-ia` | Scout de tecnologia de produção com IA (vídeo, imagem, voz/TTS, animação, edição, legenda, música e sons), custo zero primeiro, sempre com links verificados (desde 2026-11-09) | `tecnologia/` |
| **Vitinho** | `vitinho-consolidador` | Cruza tudo, separa o que é fato do que é hipótese, escreve o briefing para a ação e o resumo visual de destaques | `relatorios/`, `briefing_acao.md` e `destaques.md` |
| **Busquets** | `busquets-aprendiz-canais-dark` | Estuda vídeos que o Guilherme sobe: olha os quadros, lê a fala e relata os métodos com evidência | `aprendiz/AAAA-MM-DD/` |
| **Xabi Alonso** | `xabi-alonso-curador-referencias` | Lista curada de vídeos para estudo, do nicho aberto e do nosso | `referencias_estudo/` e `aprendiz/fila.md` |

**Busquets** e **Xabi Alonso** rodam sob demanda, fora do ciclo: como usar em `aprendiz/README.md`.

Os nomes dos seis primeiros são de jogadores do Corinthians com base nas notícias de 2026. Confirmar no site oficial do clube antes de qualquer troca: se alguém sair do elenco, o nome vira só rótulo, e a função não muda.

## Estrutura de arquivos

```
inteligencia/
  README.md            este contrato
  fontes.md            log de toda fonte usada (URL, data de acesso, o que é)   · Hugo
  canais/              uma ficha por canal: canais/<nome-do-canal>.md          · Hugo
    _indice.md         lista de canais catalogados e status                    · Hugo
  titulos/             análise de títulos, descrições, tags                    · Fagner
  thumbnails/          análise de thumbnails                                   · André
  producao/            como os canais produzem                                 · Raniele
  coletar_metricas.py  coletor do canal próprio (OAuth, só leitura)            · Yuri
  metricas/            métricas do canal próprio                               · Yuri
    videos.csv         uma linha por vídeo por coleta (dados públicos + data)
  relatorios/          relatório consolidado por ciclo: semana_AAAA-MM-DD.md   · Vitinho
  briefing_acao.md     o que o setor de ação deve fazer (ainda sem executor)   · Vitinho
  destaques.md         resumo curto e visual: só links + "por que olhar"; substitui a cada ciclo, com histórico curto no fim · Vitinho
  tecnologia/          ferramentas de IA para produção (custo zero primeiro)   · Garro
    README.md          contrato da pasta
    ferramentas.md     catálogo vivo por área, com veredito
    AAAA-MM-DD.md      um arquivo por ciclo
  aprendiz/            estudo de vídeos enviados pelo Guilherme                · Busquets
  referencias_estudo/  listas curadas de vídeos para estudar                   · Xabi Alonso
```

**Regra de escrita:** cada agente escreve só na pasta dele. Ninguém reescreve o arquivo de outro. Para conversar entre si, deixam recado no arquivo do próprio ciclo, e quem precisa lê. A "conversa" do setor é essa troca de arquivos, coordenada pelo De Bruyne.

## Ciclo de trabalho

1. **Hugo** acha e cataloga canais novos e atualiza `fontes.md`. **Garro**, em paralelo, pesquisa ferramentas de IA para produção e escreve `tecnologia/AAAA-MM-DD.md` (alimenta o **Vitinho**).
2. **Fagner**, **André** e **Raniele** leem as fichas de `canais/` e analisam cada um a sua parte.
3. **Yuri** coleta as métricas do canal próprio e registra em `videos.csv`.
4. **Vitinho** lê tudo e escreve `relatorios/semana_<data>.md`, com: (a) fatos com fonte; (b) hipóteses marcadas como hipótese; (c) o que está faltando. Depois atualiza `briefing_acao.md` (mantido) e reescreve `destaques.md` (resumo curto e visual, com a seção de tecnologia vinda do **Garro**).

## Regras do setor

- **Análise, não cópia.** Nada de copiar título, roteiro, imagem, voz ou trecho de outro canal. Descrever o padrão, não reproduzir o conteúdo.
- **Pesquisa como um humano, não raspagem.** Usar busca web e páginas públicas com leitura pontual. Para vídeos de **outros** canais, a **YouTube Data API** com a chave em `.env` (nunca exibida), dentro da cota. Para o **canal próprio**, o coletor `coletar_metricas.py` usa o token OAuth do upload. Nada de coleta em massa que viole os termos do YouTube. Nenhum agente baixa vídeo de terceiro: o Guilherme sobe o arquivo (decisão de 2026-11-05).
- **Respeitar robots.txt** e não tentar contornar bloqueios.
- **Sem dado pessoal de criador** além do nome público do canal. Nada de contato, endereço ou vida privada.
- **Toda afirmação com data e fonte.** Sem fonte, vira hipótese e é marcada como tal.
- **Nunca gravar chave de API** em arquivo do setor.
- **Nunca mexer em `output/`, `render/` ou nos agentes de produção.** O setor só lê o canal; não altera o pipeline.

## Onde o Guilherme lê

Ele prefere ler os documentos no **espelho do sistema** (`espelho_sistema.html`, gerado por `tools/gerar_espelho.py`), que se regenera sozinho por hook sempre que um agente cria ou altera `.md` ou `.txt` (regra de 2026-11-09). Nenhum agente precisa fazer nada, mas todo documento novo deve ser `.md` legível. O ponto de entrada do setor para ele é `destaques.md`.

## Escala de 24 horas

O setor é desenhado para rodar 24 horas, mas hoje cada agente só roda quando é chamado. Para ter ciclo automático, há duas opções a decidir: (1) rotinas agendadas (`schedule`/`CronCreate`) com custo de tokens por execução; (2) ciclo diário manual pelo De Bruyne. Nada foi agendado ainda.

## Pendências

- **Métricas de retenção e CTR** precisam do escopo `yt-analytics.readonly` na autenticação OAuth. Hoje o token tem `youtube.upload` e `youtube.force-ssl`, o que basta para as métricas públicas que o **coletor** já lê (visualizações, curtidas, comentários, data, duração). Sem o escopo novo, **Yuri** não estima retenção nem CTR. Para liberar, é preciso refazer o consentimento OAuth no navegador, decisão do Guilherme.
- Elenco do Corinthians a confirmar no site oficial.
- Definir o setor de ação e como ele recebe `briefing_acao.md`.
