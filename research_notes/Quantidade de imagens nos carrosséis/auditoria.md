# Auditoria local do comprimento dos carrosséis

## Quantas imagens estamos publicando de fato?

### Takeaway
O usuário tem razão sobre o padrão curto: o inventário local contém apenas carrosséis de 2 ou 3 slides. Não há teste publicado de 5, 6, 8 ou mais slides que permita avaliar a sugestão dentro desta operação.

### Cited Findings
- Auditoria dos registros locais em 21/10/2026: 19 linhas com `status=publicado`, sendo 11 de 3 slides e 8 de 2 slides. Há mais 1 de 2 slides agendado para 21/10 às 20h. São 20 posts ativos enviados, 11 de 3 slides e 9 de 2 slides; média descritiva de 2,55 slides, sem valor causal. Contagem usa `media_count` e, quando ausente, comprimento de `assets`. — [Fila local](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/fila.json)
- O registro `7698029651645435142`, 18/10 18h, foi excluído de forma recuperável para substituição e NÃO entrou nas 20 linhas ativas. A versão válida é `7698083157718879506`, com 3 slides. — [Fila local](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/fila.json), [manifest da substituição](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/posts/2026-10-18/1800-teste-cta/manifest.json)
- Em 13–15/10 foram publicados 7 carrosséis de 3 slides. Em 16–17/10 os 3 publicados tinham 2 slides; em 18/10 houve 2 de 2 slides e o teste final de 3; em 19/10, 2 de 2; em 20/10, 2 de 3; em 21/10, um de 3 às 15h, um de 2 às 18h30 e um de 2 agendado às 20h. — [Fila local](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/fila.json)
- Slide não equivale a número de fotografias/ideias: o primeiro carrossel tem 3 arquivos, mas o manifesto descreve colagens 2×2; o post do parque de 17/10 promete 3 ideias em 2 slides. É preciso distinguir quantidade de páginas de quantidade de exemplos úteis. — [carrossel de 13/10](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/posts/2026-10-14/1000/carrossel.json), [carrossel de 17/10](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/posts/2026-10-17/1000/carrossel.json)

### Inferences
- O fluxo ainda não testou a variável solicitada pelo usuário. O padrão de 2–3 slides é uma decisão de produção, não uma conclusão de desempenho.
- Acrescentar slides só tem valor editorial se acrescentar ideias, demonstrações, variações ou instruções úteis; repartir artificialmente o mesmo conteúdo não é uma hipótese equivalente.

### Gaps
- As contagens são auditadas nos registros e arquivos locais, não representam nova recontagem de cada publicação na interface TikTok nesta pesquisa.
- Parte dos manifests individuais conserva `status=agendado` histórico mesmo quando a fila já foi reconciliada como publicada. Para estado operacional, esta auditoria usa a fila atual; para arquivos, usa manifests/carrossel.json.

## Os resultados locais demonstram que o tamanho causou o desempenho?

### Takeaway
Não. Existe informação de curtidas e views em cortes diferentes, mas não há grupo longo nem controle de idade, gancho, tema, formato visual, horário ou CTA. Não podemos concluir que 2–3 slides são melhores ou piores que 6–8.

### Cited Findings
- No snapshot único de 18/10 às 14h10, os 12 posts publicados eram 7 de 3 slides e 5 de 2. Os 7 de 3 slides foram publicados em 13–15/10; os 5 de 2 em 16–18/10. Logo, o grupo de 3 slides teve sistematicamente mais tempo para acumular alcance. Dois posts de 2 slides tinham menos de 2 horas e cerca de 10 minutos de idade, respectivamente. — [Dados auditados do snapshot](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/relatorio-dados-2026-10-18.json), [fila com slots e contagens](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/fila.json)
- Exemplos no MESMO snapshot 18/10: casal sem rosto, 3 slides, 855 views/30 curtidas; casal no espelho, 3 slides, 603/25; casal sentado, 2 slides, 582/3; para onde olhar, 2 slides, 394/9. São observações descritivas de posts diferentes e idades diferentes, não um experimento sobre tamanho. — [Relatório auditado 18/10](C:/Users/Guilherme/Documents/canal-dark/reports/Relatorio%20Closet%20Minimal%2013%20a%2018%20outubro%202026.md)
- O agregado de 5.573 views e 104 curtidas do relatório é dos 12 posts do agente até o snapshot de 18/10; 6,9 mil views e 119 curtidas referem-se à conta inteira em outro intervalo, 13–17/10. Não somar essas populações nem trocar uma pela outra. — [Dados auditados](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/relatorio-dados-2026-10-18.json)
- `analytics.json` contém referências anteriores ao agente: 611,5 mil views/33,6 mil curtidas em post de 25/11/2025 e 536,5 mil/46 mil em post de 15/12/2025, contadores observados em 13/10/2026. O arquivo NÃO registra a quantidade de slides desses dois virais. Não deduzir seu tamanho nem atribuí-los ao agente. — [Analytics local](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/analytics.json)
- Os registros mais recentes da fila combinam coletas de 18, 19 e 21/10. A taxa de seguidores atribuídos por post, retenção por slide, quantidade média de fotos vistas e taxa de conclusão não estão disponíveis nesses arquivos. — [Fila](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/fila.json), [analytics](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/analytics.json)

### Inferences
- Qualquer ranking agregado de performance por 2 versus 3 slides com esse histórico mistura idade e mudanças de produção. Seria uma base fraca mesmo para correlacionar tamanho; para causalidade, é insuficiente.
- Baixo alcance e baixo crescimento merecem revisão criativa, mas não autorizam dizer que mais imagens resolverão. Vale testar em vez de tratar o palpite como fato.

### Gaps
- Não há leituras padronizadas exatamente às 24h e 72h dos posts, amostra de comprimento maior, retenção por página nem atribuição confiável de seguidores.
- Os virais de 2025 contam vários meses de exposição; comparar seus contadores acumulados aos posts com horas/dias de vida é inadequado.

## Como testar mais imagens sem fingir certeza?

### Takeaway
Proposta editorial futura, não ação executada: testar carrosséis mais desenvolvidos, por exemplo 6 slides, contra o padrão atual de 3 em séries pareadas. O número 6 é uma condição de teste prática, não um ótimo descoberto.

### Cited Findings
- A operação exige posts originais, conta @closetminimal, margens quadradas, anatomia realista, CTA visual e rótulo nativo de IA; preservá-los em todos os braços evita introduzir mudanças desnecessárias. — [Configuração atual](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/config.json)
- A meta registrada é 2.000 seguidores; o último snapshot exato de seguidores do relatório é 1.192 em 18/10, não uma medição de hoje. Por isso seguidores atribuídos, quando disponíveis, precisam ser priorizados e datados. — [Configuração](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/config.json), [Relatório 18/10](C:/Users/Guilherme/Documents/canal-dark/tiktok/closetminimal/relatorio-dados-2026-10-18.json)

### Inferences
- Para os próximos conteúdos autorizados: versão curta de 3 slides (gancho, exemplo útil, CTA integrado) versus versão de 6 (gancho, 4 exemplos/etapas genuinamente diferentes, fechamento com CTA). Manter uma ideia/pose claramente identificável por página. Evitar um slide que serve apenas para pedir interação.
- Usar temas pareados, sem republicar a mesma arte. Alternar os comprimentos entre os horários habituais ao longo de vários dias; não dar sempre um horário a cada grupo. Manter fonte, margens, nível de detalhe, qualidade de imagem e tipo de CTA comparáveis.
- Medir cada post às 24h e 72h: views, curtidas/views, comentários/views, salvamentos/views, compartilhamentos/views e seguidores atribuídos por 1.000 views, se a interface os expuser. Registrar visitas ao perfil e consumo/retencão quando disponíveis. Ausência de dados é `null`, não zero.
- Começar com pelo menos alguns pares (por exemplo 4–6 pares) é mais informativo que um único vencedor; mesmo isso continua exploratório, sem garantia de significância estatística. Comparar medianas e dispersão, não escolher apenas o máximo.
- Decisão futura: adotar o formato mais longo se mostrar benefício consistente nas mesmas janelas e sem perda de clareza/conversão; se os resultados forem inconclusivos, declarar isso. Não prometer viral nem seguidor com base somente no comprimento.

### Gaps
- Esta auditoria não executou o teste nem alterou nenhum post ou agendamento. A validação externa do tamanho dos concorrentes cabe à pesquisa paralela.
