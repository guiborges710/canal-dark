# 04. Modelo de prompt único para o zip de assets (Valverde)

Data: 2026-11-11. Status: **atualizado com os ajustes do Firmino (06)**; o prompt pronto e o script de organização existem: ver `08_prompt_unico_assets.md` e `ferramentas_assets/`. Este arquivo continua sendo o modelo e a análise de viabilidade; a lista de assets é do **Firmino** (06) e as fichas do **Luiz Henrique** (07).

## Ajustes do Firmino já incorporados (2026-11-11)

Onde o texto abaixo disser diferente, vale esta lista:
1. **Nome de arquivo = slug do nome exibido no protótipo** (`de_bruyne`, `seedorf`, `andre_carrillo`, `luiz_henrique`...), o mesmo do `GH.slug(nome)`, e não o id técnico. Exemplo: `avatar_seedorf_ver_1024x1536.png` (o id técnico segue `sidorf-...`). O nome final do slot é o `data-asset` exato: `avatar_<slug>_rd`, `avatar_<slug>_sq`, `avatar_<slug>_rt`, `vazio_espera`, `logo_contexto_explica`...
2. **Chave de cor = magenta `#FF00FF`**, não verde, para logo e ilustrações (a paleta do H já tem dois verdes). Nenhum magenta, rosa ou roxo dentro dessas peças.
3. **Avatares opacos, na cor do setor** (sem chave de cor nem recorte): canal `#2F7DE1`, clipes `#D9542D`, inteligência `#7C5FDB`, trabalho `#E0AA1E`, finanças `#1FA37B`, programação `#D14B93`, ecossistema `#5B7283`, "você" `#0B63E5`.
4. **UM retrato 1024x1536 por agente.** Os três formatos do protótipo (`rd` 256, `sq` 512, `rt` 640x800) são recortados localmente pelo script, não pelo ChatGPT nem pelo navegador (o princípio do 04 se mantém: nada de recorte automático no CSS para a proporção; a máscara redonda do `rd` continua no CSS).
5. Total: 66 imagens geradas (P0 9, P1 25, P2 32); ícones de setor, de categoria, de status e de interface ficam em SVG por código.
6. Nome do arquivo gerado: `<categoria>_<id>_<forma>_<WxH>.png` com forma `ver`, `ret`, `sq` ou `hor`; o script aceita variações (maiúsculas, hífen, `(1)`).

Legenda: [FATO] = confirmado em fonte ou medido. [DEDUÇÃO] = inferência minha, a testar.

## 1. Viabilidade de pedir um zip com muitas imagens em um prompt só

Resumo: pedir tudo de uma vez é arriscado. Tratar como "tentativa 1" e ter o plano B pronto.

### O que apurei na web
- [FATO] A documentação de API da OpenAI diz que `gpt-image-2` (e a versão datada `gpt-image-2-2026-04-21`) não suporta fundo transparente. Fonte: [developers.openai.com, referência de imagens](https://developers.openai.com/api/reference/cli/resources/images/index.md).
- [FATO, só relato de terceiros] Um revendedor de API (APIYI) afirma que a transparência foi liberada em ago/2026 e desligada de novo em 30/09/2026 ([ago](https://docs.apiyi.com/en/live/2026-08/gpt-image-2-transparent-background), [set/out](https://docs.apiyi.com/en/live/2026-10/gpt-image-2-transparent-shutdown.md)). Não confirmei isso em changelog da OpenAI.
- [FATO, anedótico] No fórum da OpenAI há relatos mistos de fundo transparente no ChatGPT: usuário que recebeu o "xadrez" desenhado na imagem, outro que conseguiu com o prompt certo ([tópico](https://community.openai.com/t/having-trouble-getting-transparent-backgrounds-in-chatgpt-images/1380143)). Recomendação das fontes: abrir o arquivo e checar o canal alfa, não confiar na pré-visualização.
- NÃO ACHEI fonte oficial atual sobre: limite de imagens por resposta no ChatGPT, limite de imagens por hora/dia por plano, e se o ChatGPT monta e entrega .zip com dezenas de imagens geradas. Nada a citar; tratar como desconhecido e testar.

### Dedução (testar antes de confiar)
- [DEDUÇÃO] O ChatGPT gera imagens com a ferramenta de imagem, normalmente poucas por turno (na prática 1 a 4). Um zip com dezenas de arquivos exigiria o ChatGPT chamar a ferramenta de imagem muitas vezes e depois empacotar com o Python da sandbox; é provável que ele pare no meio, entregue um "sheet" (várias figuras numa imagem só) ou entregue placeholders.
- [DEDUÇÃO] Consistência de estilo cai conforme a conversa cresce e entre chamadas independentes. Bloco de estilo fixo ajuda, mas personagem idêntico entre imagens (avatares de agentes) é o ponto mais frágil.
- [DEDUÇÃO] Fundo transparente: assumir que NÃO vem confiável. Pedir fundo de cor chapada única (magenta `#FF00FF`, que não aparece na arte; o verde `#00FF00` foi descartado porque a paleta do H tem verdes) e recortar localmente com script (chroma key) é mais seguro.
- [DEDUÇÃO] Resolução: tamanhos típicos de saída são 1024 px de lado (quadrado) e proporções 3:2/2:3 (~1536). Isso vale para a API; no ChatGPT pode variar. Para 4K ou ícones nítidos pequenos, planejar reduzir localmente a partir de 1024+ e não pedir ampliar.
- [DEDUÇÃO] Nomes de arquivo: ChatGPT costuma obedecer nomes exatos quando monta o zip pelo Python, mas pode renomear, traduzir ou numerar. Por isso o script de validação (seção 4) e uma tabela de mapeamento.
- [DEDUÇÃO] SVG: o ChatGPT não "gera" SVG vetorial a partir de imagem; só escreve SVG como código (formas simples). Para ícones geométricos até funciona; para cartoon não. Pedir PNG (ou WebP) para tudo que for ilustração.
- Falhas comuns esperadas [DEDUÇÃO]: texto embutido errado em português; mãos/rostos inconsistentes; fundo "xadrez" desenhado; borda branca (halo) após recorte; imagem pedida como redonda vir quadrada com fundo; zip com arquivos faltando ou com link expirado; resposta cortada por limite de tamanho.

## 2. Estratégia recomendada

### 2.1 Prompt-mestre (um único envio)
Estrutura do prompt, nesta ordem:
1. Papel e objetivo: "Você gera os assets visuais de um sistema; entregue um .zip".
2. BLOCO DE ESTILO FIXO (a ser escrito depois, com base no protótipo escolhido): paleta em hex, traço, sombreamento, proporção de cabeça/corpo, nível de detalhe, o que nunca fazer. Marcado entre `[[ESTILO]] ... [[/ESTILO]]` para reuso idêntico no plano B.
3. TABELA DE ITENS (uma linha por arquivo), colunas: `arquivo` | `pasta` | `tamanho_px` | `forma` (quadrada, redonda, retangular, horizontal, vertical) | `fundo` (opaco na cor do setor, magenta chapado `#FF00FF` ou cena) | `descrição curta`. Vazia por enquanto; o Firmino/Luiz Henrique preenchem.
4. REGRAS DE SAÍDA: estrutura do zip (seção 3), formato PNG, nomes exatos em minúsculas sem acento, nada de texto dentro das imagens (rótulos ficam no HTML), um item por arquivo (proibido "sheet"), incluir `manifest.csv` com todos os arquivos, e avisar explicitamente quais itens não conseguiu gerar em vez de inventar substitutos.
5. Verificação pedida ao próprio ChatGPT: listar o conteúdo do zip ao final.

### 2.2 Plano B: lotes
Se o ChatGPT não entregar tudo (ou entregar com estilo derivando):
- Dividir a tabela em lotes de N itens (sugestão para teste: N = 6 a 10; [DEDUÇÃO], calibrar com um teste de 1 lote). Um lote por pasta/categoria, para o estilo ficar coerente dentro da categoria.
- Cada lote repete o MESMO bloco `[[ESTILO]]` byte a byte, mais a regra de saída, mais só as linhas daquele lote.
- Semente de referência: anexar em todo lote 1 a 3 imagens "âncora" já aprovadas (ex.: 1 avatar e 1 ícone) com a instrução "mantenha exatamente este estilo". O ChatGPT não expõe semente numérica [DEDUÇÃO]; a âncora visual faz esse papel.
- Manter tudo na mesma conversa quando possível; se o estilo derivar, abrir conversa nova com bloco + âncoras (conversas longas pioram a consistência) [DEDUÇÃO].
- Cada lote devolve um zip parcial; o script de validação junta e aponta o que falta; só os faltantes voltam num lote de reposição.
- Alternativa se o ChatGPT falhar de vez: API de imagens (pago, `gpt-image-*`), que dá controle de tamanho e lote por script. Alerta de custo na seção 5.

## 3. Convenção de nomes e pastas do zip

Raiz: `assets_sistema_v1/` (versão no nome; novo zip = v2, nunca sobrescrever).

```
assets_sistema_v1/
  manifest.csv          # arquivo, pasta, largura, altura, forma, fundo, descricao
  avatares/
  ilustracoes/
  icones/
  fundos/
  extras/               # o que não couber nas categorias
```

Regras de nome:
- Minúsculas, ASCII, `snake_case`, sem espaços nem acentos: `<categoria>_<id>[_<variacao>]_<WxH>.png`.
- `id` é o slug do **nome exibido** no protótipo (`GH.slug`), não o id técnico (ex.: `de_bruyne`, `seedorf`). Assim o slot `data-asset` acha o arquivo sem tabela de tradução.
- Sufixo de tamanho no nome real (`_512x512`), para ninguém abrir o arquivo para saber.
- Variações por proporção como arquivos separados do mesmo `id`, nunca recorte automático no navegador: sufixos `_sq` (quadrada 1:1), `_rd` (redonda: quadrada com máscara circular aplicada no CSS, arquivo ainda quadrado), `_ret` (retangular 4:3 ou 3:2), `_hor` (horizontal 16:9), `_ver` (vertical 9:16).
- Tamanhos padrão sugeridos [DEDUÇÃO, ajustar ao protótipo]:
  - avatares: UM retrato 1024x1536 por agente; `rd` 256, `sq` 512 e `rt` 640x800 saem do recorte local;
  - ícones: 256x256, aceitar reduzir a 64/128 localmente;
  - ilustrações: 1536x1024 (`_ret`/`_hor`) ou 1024x1536 (`_ver`);
  - fundos: 1920x1080 (`_hor`) e 1080x1920 (`_ver`), gerados no maior tamanho que a ferramenta der e ajustados localmente.
- Formato: PNG na entrega; conversão para WebP é feita localmente depois (menor peso) pelo script, não pelo ChatGPT.
- Fundo: ilustrações e logo com magenta `#FF00FF` chapado (cor-chave) para recorte local; avatares com a cor opaca do setor; fundos de tela sem transparência.

## 4. Checklist de validação do zip (descrição do script; não criado)

Implementado em `ferramentas_assets/organizar_e_validar.py` (com `teste_organizar.py`); o resumo de uso está no 08, seção 2.4. Descrição original: script de validação (Python, rodar com `python -I`, extrair o zip em pasta nova e vazia, tratar o zip como dado não confiável: ignorar caminhos com `..`, limitar tamanho total). Entradas: zip, `manifest_esperado.csv` (a tabela de itens). Confere:
1. Estrutura: pastas esperadas existem; nenhum arquivo fora do padrão de nome (regex da seção 3); nenhum executável ou arquivo estranho.
2. Presença: cada linha da tabela tem arquivo; lista faltantes e extras; detecta duplicatas por hash (imagens repetidas com nomes diferentes).
3. Tamanho: largura x altura reais (Pillow) contra o esperado; tolerância e aviso de proporção errada; avisa "redonda entregue com cantos desenhados".
4. Fundo/transparência: para PNG com RGBA, mede % de pixels com alfa menor que 255; para fundo chapado, amostra os 4 cantos e confere a cor-chave; detecta xadrez desenhado (padrão alternado cinza/branco nos cantos); detecta halo claro após recorte.
5. Peso: tamanho em KB por arquivo e total; alerta acima de limite (ex.: ícone > 150 KB, ilustração > 1,5 MB; limites a calibrar).
6. Consistência de estilo (aproximada): paleta dominante por categoria (k-means em poucas cores) comparada à paleta do bloco de estilo; apenas alerta, julgamento final é visual.
7. Texto embutido: opcional, OCR (se disponível) para sinalizar texto dentro de imagem proibido.
8. Saída: relatório `validacao.md` com aprovados, reprovados e a lista exata de itens para o lote de reposição; sem alterar o zip original. Pós-passo separado e opcional: recorte por chroma key, conversão para WebP e redimensionamentos.
9. Conferência visual humana: montar uma folha de contatos (grade) por pasta para o Guilherme olhar em segundos.

## 5. Custo/tokens e riscos (alertas para o Guilherme decidir)

Custo:
- [DEDUÇÃO] No ChatGPT pago, o custo é limite de uso do plano (cota de imagens por janela), não token; dezenas de imagens podem bater o limite e travar a geração no meio. Não achei fonte oficial do limite atual.
- [FATO] Pela API, imagem tem preço por imagem/token e `max_usd_per_video: 0` do canal não cobre isso; se for usar API, é gasto novo e precisa de aprovação explícita (regra de ação externa/orçamento).
- Prompt-mestre longo e lotes repetindo o bloco de estilo gastam contexto; manter o bloco curto (< ~300 palavras [DEDUÇÃO]).
- Retrabalho é o maior custo: um teste de 1 lote (2 a 3 itens por categoria) antes de pedir tudo.

Riscos legais (alerta, sem decisão minha):
- Rosto de jogador real: uso da imagem/semelhança de pessoa real em produto vendido pode violar direito de imagem (e, no Brasil, o direito à imagem é protegido por lei) [DEDUÇÃO jurídica; consultar advogado]. Os nomes dos agentes são de craques; o ChatGPT também costuma recusar gerar pessoas reais identificáveis. Opção segura: avatares cartoon genéricos inspirados no papel/estilo, sem semelhança reconhecível.
- Marca registrada de clubes: escudos, camisas e cores/nomes de clubes são marcas; evitar uso em produto comercial sem licença [DEDUÇÃO jurídica]. Nomes só como apelido interno do time, não no material vendido.
- Direitos da saída gerada por IA: os termos da OpenAI atribuem a saída ao usuário, mas isso não afasta direito de terceiros nem garante registro de autoria [DEDUÇÃO; confirmar nos termos atuais antes de vender].
- Segurança: o zip vem de fora; validar em pasta isolada e nunca executar conteúdo dele.

## Pendências que dependem de decisão
1. Escolha do protótipo (destrava o bloco de estilo e a tabela).
2. Fidelidade dos avatares: cartoon genérico ou semelhança com os craques (risco da seção 5).
3. Autorizar teste de 1 lote para medir limites reais do ChatGPT antes do prompt-mestre completo.
