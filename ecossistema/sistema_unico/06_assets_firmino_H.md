# 06. Assets do estilo H (Profissional): análise do Firmino

Data: 2026-11-11. Autor: **Firmino**. Base: `prototipo_estilos/h/` (estilo.css, app.js), `g/comum_gh.js` (slots `data-asset`, `GH.TIPOS`), `base.js` (ícones), `dados.js` (56 agentes), e os arquivos 01 a 04 de `sistema_unico/`. Nenhuma imagem foi gerada e o prompt final não está aqui: vem depois, juntando este arquivo, as fichas do **Luiz Henrique** e o modelo do **Valverde**.

Legenda de prioridade: **P0** = primeira entrega (Finanças + o que a moldura já mostra), **P1** = telas seguintes do H, **P2** = vitrine/opcional.

## 0. Decisões de base (leia primeiro)

1. **Um arquivo gerado por agente, três derivados localmente.** O H usa cada agente em 3 formatos (`rd` 256, `sq` 512, `rt` 640x800). Pedir 3 imagens por agente seria 168 imagens e personagens diferentes entre si. Em vez disso o ChatGPT entrega **1 retrato vertical 1024x1536 por agente** e o script de pós-processo recorta `rd`, `sq` e `rt` (e exporta WebP). Isso corta o prompt em ~66% e garante que o mesmo rosto aparece nos 3 slots. É um ajuste ao 04 (que previa arquivos separados por proporção): o recorte é feito no script, não no navegador, então o princípio do 04 continua valendo.
2. **Nome do arquivo usa `GH.slug(nome)`, o mesmo que o protótipo já usa** (`de_bruyne`, `andre_carrillo`, `seedorf`, `luiz_henrique`, `mbappe`, `dembele`...), não o id técnico. Assim o slot `avatar_<slug>_rd` acha o arquivo sem tabela de tradução. Divergência para o **Valverde** ajustar no 04: onde ele escreveu `courtois-revisor-fatos` virar `courtois`, vale o slug do nome exibido. Atenção: o nome exibido é **Seedorf** (id técnico segue `sidorf-...`), então o arquivo é `avatar_seedorf_*`.
3. **Avatar com fundo opaco na cor do setor** (sem chroma key). O H já pinta cada slot com a cor do setor (`[data-s=...]`); o retrato nasce com esse fundo chapado, então não há recorte, halo nem fundo "xadrez". Só ilustrações e logo usam chave de cor.
4. **Chave de cor para o que precisa de transparência: magenta `#FF00FF`** (não verde). Motivo: a paleta do H tem dois verdes (`#1FBF8A` aprova, `#1FA37B` finanças), e um verde-chave sangraria nas bordas. Regra no prompt: nenhum rosa/magenta nessas peças (o rosa `#D14B93` do setor Programação só aparece em avatares, que são opacos).
5. **Nada de texto dentro das imagens** (regra do 04). Iniciais, nomes, rótulos, números de camisa e cifras ficam no HTML.
6. **Formato dos tamanhos:** o ChatGPT entrega 1024x1024, 1024x1536 ou 1536x1024. Peço nesses tamanhos e o script entrega os tamanhos finais dos slots (2x para telas retina quando possível). Todos os arquivos da lista abaixo têm o tamanho gerado no nome e o tamanho final de slot na coluna "vira".

## 1. Lista de assets

Totais gerados no ChatGPT: **66 imagens** (P0 = 9, P1 = 25, P2 = 32), mais 8 opcionais que recomendo cortar. Derivados localmente: ~190 arquivos WebP/PNG.

### 1.1 `avatares/` (57 imagens)

Formato do arquivo gerado: **vertical 2:3**, 1024x1536, **fundo opaco** na cor do setor (hex na seção 3.4), busto até o peito, ombros cortados pela base.

| arquivo gerado | forma | px | fundo | vira (slots do H) | onde aparece | prio | qtd |
|---|---|---|---|---|---|---|---|
| `avatar_casemiro_ver_1024x1536.png` | vertical | 1024x1536 | opaco, `#1FA37B` | `avatar_casemiro_rd` 256, `_sq` 512, `_rt` 640x800 | Finanças (cabeçalho do setor, quem lançou o movimento, conversa), Espera você, Agentes | P0 | 1 |
| `avatar_ronaldo_ver_1024x1536.png` | vertical | 1024x1536 | opaco, `#E0AA1E` | idem | Estações, Espera, Agentes, paleta Ctrl K | P0 | 1 |
| `avatar_de_bruyne_ver_1024x1536.png` | vertical | 1024x1536 | opaco, `#2F7DE1` | idem | Metrô de estações, Canal, Agentes | P0 | 1 |
| `avatar_luiz_henrique_ver_1024x1536.png` | vertical | 1024x1536 | opaco, `#5B7283` | idem | Ecossistema, Agentes, mapa | P0 | 1 |
| **P1, 22 agentes** que já têm estado de exemplo no protótipo: `olise`, `valverde`, `alisson`, `salah`, `vini`, `neymar`, `raphinha`, `seedorf`, `memphis`, `rivaldo`, `kaka`, `zidane`, `zico`, `lamine_yamal`, `modric`, `courtois`, `mbappe`, `vitinho`, `rodrygo`, `endrick`, `thiago_silva`, `marquinhos` | vertical | 1024x1536 | opaco, cor do setor | idem (rd/sq/rt) | fila "Espera você", lista de Agentes, ficha do agente, metrô de estações | P1 | 22 |
| **P2, 30 agentes** restantes: `haaland`, `messi`, `cristiano`, `barcola`, `kane`, `dembele`, `hugo_souza`, `fagner`, `andre_carrillo`, `raniele`, `yuri_alberto`, `garro`, `busquets`, `xabi_alonso`, `pele`, `figo`, `totti`, `buffon`, `lewandowski`, `roberto_carlos`, `pirlo`, `guardiola`, `pedri`, `rodri`, `kroos`, `bellingham`, `xavi`, `ancelotti`, `iniesta`, `firmino` | vertical | 1024x1536 | opaco, cor do setor | idem | só na lista de Agentes e na ficha | P2 | 30 |
| `avatar_voce_ver_1024x1536.png` (o próprio Guilherme, cartoon neutro e genérico, sem semelhança, útil para a versão vendável: "você") | vertical | 1024x1536 | opaco, `#0B63E5` (cor de foco) | `avatar_voce_rd` 256, `_sq`, `_rt` | pontos de decisão "você", menu de usuário, estação de aprovação | P1 | 1 |

Setor de cada agente para a cor de fundo: o de `dados.js` (Dembelé e Kane em canal, Pirlo em clipes, Valverde e Firmino em ecossistema, Ronaldo em trabalho, Casemiro em finanças).

### 1.2 `ilustracoes/` (5 imagens, estados vazio e erro)

Gerar 1536x1024 (3:2), **fundo magenta chapado `#FF00FF`**, objeto isolado ao centro com margem de 12%, sem personagem humano (evita deriva de rosto e fica neutro para vender), estilo adesivo (seção 3.2). Vira 960x640 (slot `vz`).

| arquivo gerado | forma | px | fundo | vira | onde aparece | prio | qtd |
|---|---|---|---|---|---|---|---|
| `vazio_espera_ret_1536x1024.png` (caixa de entrada vazia com um check, "tudo em dia") | retangular | 1536x1024 | chave `#FF00FF` | `vazio_espera` 960x640 | Espera você: "Fila zerada" | P0 | 1 |
| `vazio_financas_ret_1536x1024.png` (carteira/cofrinho aberto e vazio) | retangular | 1536x1024 | chave `#FF00FF` | `vazio_financas` 960x640 | Finanças: sem movimentos, sem vencimentos, sem categorias ainda | P0 | 1 |
| `erro_geral_ret_1536x1024.png` (tomada/cabo desconectado) | retangular | 1536x1024 | chave `#FF00FF` | `erro_geral` 960x640 | qualquer tela quando o dado não carrega ou o servidor local caiu (Finanças: não leu `financas/*.csv`) | P0 | 1 |
| `vazio_generico_ret_1536x1024.png` (prancheta vazia com um sinal de "+") | retangular | 1536x1024 | chave `#FF00FF` | `vazio_generico` 960x640 | setores sem dados ainda (Trabalho, Clipes, Inteligência...), listas vazias, resultado de busca zero | P0 | 1 |
| `vazio_agentes_ret_1536x1024.png` (lupa sobre uma fila vazia de peões) | retangular | 1536x1024 | chave `#FF00FF` | `vazio_agentes` 960x640 | Agentes: "Nenhum agente encontrado" | P1 | 1 |

Estado **carregando**: não gerar imagem. É esqueleto (barras cinza pulsantes) + o `rodando` em giro que já existe em `GH.ico`.

### 1.3 `icones/` (1 imagem + 8 opcionais)

| arquivo gerado | forma | px | fundo | vira | onde aparece | prio | qtd |
|---|---|---|---|---|---|---|---|
| `logo_contexto_explica_sq_1024x1024.png` (marca sem letras; o nome fica em texto Bahnschrift no HTML) | quadrado | 1024x1024 | chave `#FF00FF` | `logo_contexto_explica` 256 (e 34 px na barra); derivados: `favicon_32`, `favicon_180` (apple-touch), `icon_512` | topo da ilha, aba do navegador, tela de abertura, e-mail/capa | P0 | 1 |
| `icone_setor_<id>_sq_1024x1024.png` x 8 (`espera`, `canal`, `clipes`, `inteligencia`, `trabalho`, `financas`, `programacao`, `ecossistema`) | quadrado | 1024x1024 | chave `#FF00FF` | `icone_setor_<id>` 128 | tile do setor e cabeçalho de setor (56 px) | P2, **recomendo cortar** | 8 (opcional) |

### 1.4 `fundos/` (2 imagens)

| arquivo gerado | forma | px | fundo | vira | onde aparece | prio | qtd |
|---|---|---|---|---|---|---|---|
| `fundo_hero_ilha_hor_1536x1024.png` (geometria de linhas de metrô abstratas, azul-marinho profundo, baixíssimo contraste) | horizontal | 1536x1024 | opaco (cena) | `hero` 1600x700 (recorte 16:7 do miolo, `object-position: center`) | atrás da ilha escura (números grandes): Home, Finanças, Canal | P1 | 1 |
| `fundo_splash_ver_1024x1536.png` (mesma linguagem, para celular/abertura) | vertical | 1024x1536 | opaco (cena) | `splash` 1080x1920 (recorte 9:16) | tela de abertura e versão celular com `--rede` | P2 | 1 |

### 1.5 `extras/` (1 imagem)

| arquivo gerado | forma | px | fundo | vira | onde aparece | prio | qtd |
|---|---|---|---|---|---|---|---|
| `extra_og_capa_hor_1536x1024.png` (composição de vitrine: a mesma marca + linhas de metrô, centro limpo) | horizontal | 1536x1024 | opaco (cena) | `og_capa` 1200x630 (recorte do miolo) | pré-visualização de link, página de venda, capa da apresentação | P2 | 1 |

### 1.6 Resumo de quantidades

| prioridade | avatares | ilustrações | ícones/logo | fundos | extras | total |
|---|---|---|---|---|---|---|
| P0 | 4 | 4 | 1 | 0 | 0 | **9** |
| P1 | 22 + 1 (você) | 1 | 0 | 1 | 0 | **25** |
| P2 | 30 | 0 | 0 | 1 | 1 | **32** |
| total | 57 | 5 | 1 | 2 | 1 | **66** |
| opcional a cortar | | | 8 ícones de setor | | | (+8) |

Ordem de geração sugerida (cada lote traz os P0 como âncora de estilo do 04): lote 1 = P0 (testa o estilo e os limites do ChatGPT); lote 2 = P1; lotes 3 a 5 = P2 por setor.

## 2. Pitacos de design

**O que vale gastar imagem gerada**
- **Avatares**: são a alma do produto e o que o ícone SVG não substitui. Um retrato por agente, formato único, fundo na cor do setor. A cor chapada do fundo é o que une 56 faces diferentes numa só família; ela já faz o trabalho de identificação por setor sem texto.
- **Estados vazio e erro**: 5 ilustrações de **objetos**, sem gente. Rosto muda de uma imagem para outra e distrai; objeto não. E são as telas que fazem um sistema "parecer terminado" quando o dono de outro negócio abrir pela primeira vez.
- **Logo**: 1 marca. Sem ela o produto não é vendável. Alternativa: o **Endrick** vetoriza o resultado em SVG depois da aprovação; até lá o monograma "CE" amarelo (`#FFB703`) que o protótipo já usa continua servindo.
- **Hero**: 1 fundo sutil e 1 splash. Contraste de 3 a 6% contra a ilha `#0E1A24`, para os números de 84 px continuarem sendo o herói da tela. Nada de rosto nem objeto no hero.

**O que NÃO gerar com IA (faça por código)**
- **Ícones de categorias financeiras**: SVG de traço 1,5 como o resto de `base.js`, herdando `currentColor` (funcionam nos dois temas, escalam de 16 a 56 px, trocam de cor por estado). Raster gerado a 24 px vira borrão e não acompanha o tema escuro. Lista para o **Endrick** (nomes `icone_cat_<nome>.svg` ou entradas no mapa `P` de `base.js`): `moradia`, `mercado`, `restaurantes`, `transporte`, `contas_servicos` (luz, água, internet), `saude`, `lazer`, `assinaturas`, `educacao`, `impostos`, `cartao`, `renda`, `investimento`, `outros` (14).
- **Ícones de setores** (8): já existem em `base.js` (`canal`, `clipes`, `inteligencia`, `trabalho`, `financas`, `programacao`, `ecossistema`, `inbox`). Ficam. Por isso os 8 ícones gerados estão marcados como "cortar": gastam cota do ChatGPT, saem inconsistentes e não acompanham o tema.
- **Ícones de status** (5): já são SVG de `GH.ico` (círculo, triângulo, losango, tracejado, giro). A regra "forma + cor" do H depende disso; imagem gerada quebraria.
- **Ícones de interface** (busca, copiar, tentar de novo, fechar, cadeado): SVG já existente.
- **Textura de papel**: ruído sutil por CSS/SVG (`feTurbulence`, 3%). Imagem repetida pesa e emenda mal.
- **Favicons**: derivados do logo pelo script (32, 180, 512), não são imagens extras.
- **Gráficos, barras, anéis, miniaturas de dado** de Finanças: SVG de `B.*`.
- **Carregando**: esqueleto + giro do `rodando`.
- **Avatar de reserva** (agente sem imagem): as iniciais do slot atual já funcionam como fallback.

**Telas e estados de Finanças e o que cada um usa** (primeira entrega: saldo, categorias de gasto, vencimentos, movimentos)
- Saldo: só texto grande em Bahnschrift. Nenhuma imagem.
- Categorias de gasto: SVG (14 ícones) + anel/barras por código.
- Vencimentos: ícones de status SVG (`pendente` para a vencer, `erro` para atrasado, `ok` para pago) + data. Nenhuma imagem.
- Movimentos: ícone de categoria SVG + avatar `avatar_casemiro_rd` (quem lançou). Primeiro e único uso de avatar nesta tela.
- Vazio: `vazio_financas` (sem movimentos) e `vazio_generico` (busca sem resultado).
- Erro: `erro_geral` (não achei `financas/movimentos.csv`).
- Carregando: esqueleto.

**Riscos e cuidados**
- **Modo escuro**: contorno azul-marinho (`#0E1A24`) some contra o cartão escuro (`#111D28`). Nas ilustrações e no logo, usar o estilo **adesivo**: contorno interno azul-marinho + borda externa branca `#EFF3F1` de ~6 px; funciona nos dois temas e ainda separa bem do magenta no recorte. Avatares não precisam (fundo opaco).
- **Pessoas reais**: o prompt-mestre **não deve citar o nome do jogador**. Descrever só pelos traços da ficha (cor da camisa, cabelo, pose). O ChatGPT tende a recusar pessoa real identificável, e para um produto à venda isso é também a decisão segura (o 04 e o 03 já registram o risco como decisão do Guilherme).
- **Rótulo de venda**: não mostrar em nenhuma imagem logos de clube/marca, escudos, nomes ou números na camisa.
- **Deriva de estilo em 57 retratos**: gerar por setor, sempre com 2 âncoras P0 anexadas e o bloco de estilo idêntico (`[[ESTILO]]` do 04).
- **Imagem que vira cara-a-cara com a cor do estado**: nenhum fundo de avatar usa vermelho/âmbar/verde dos estados (ver 3.4). Só as cores de setor do CSS, que o protótipo já separou delas.

## 3. Bloco de ESTILO fixo para o prompt-mestre

Texto pronto para copiar entre `[[ESTILO]]` e `[[/ESTILO]]` (o **Luiz Henrique** acrescenta a ficha de cada personagem depois). Em português para o prompt; hex extraídos de `h/estilo.css`.

### 3.1 Paleta (extraída do CSS do H)

| papel | hex | uso na imagem |
|---|---|---|
| azul-marinho profundo (ilha) | `#0E1A24` | contorno, sombra de 2º nível, cabelo/roupa escura |
| azul-marinho 2 | `#162838` | volumes escuros, fundo do hero |
| linha azulada | `#2A4559` | linhas finas do hero, detalhes internos |
| papel frio | `#EFF3F1` | luz, branco da camisa/papel, borda "adesivo" |
| cinza esverdeado claro | `#E6ECE9` | sombra suave sobre branco |
| texto | `#13202A` | pupilas, cabelo preto |
| cinza-azulado médio | `#4B5E6A` | meios-tons neutros |
| sinal (âmbar) | `#FFB703` | único acento quente: detalhe pequeno por imagem (1 elemento) |
| aprova (verde-menta) | `#1FBF8A` | check, "tudo certo" |
| foco (azul) | `#0B63E5` | detalhes de interface, "você" |
| azul de estado | `#1560D6` / `#62B2FF` | só em ilustração de "carregando", se houver |

Fundos de avatar por setor (`[data-s]` do CSS): canal `#2F7DE1`, clipes `#D9542D`, inteligência `#7C5FDB`, trabalho `#E0AA1E`, finanças `#1FA37B`, programação `#D14B93`, ecossistema `#5B7283`.

### 3.2 Traço, forma, luz

```
[[ESTILO]]
Ilustração vetorial cartoon plana, limpa e profissional, no espírito de sinalização de metrô e interface moderna:
formas geométricas simples, cantos arredondados, sem textura de pincel.
Contorno uniforme azul-marinho #0E1A24 de espessura constante (cerca de 1% da largura), sem variar.
Cores chapadas com no máximo 2 níveis de sombra (cel-shading em 2 tons), sem degradê, sem brilho especular, sem ruído.
Luz vindo de cima à esquerda; sombra projetada sempre à direita e abaixo, em tom mais escuro da própria cor.
Paleta restrita: azul-marinho #0E1A24, #162838, branco frio #EFF3F1, cinza-azulado #4B5E6A, acento único âmbar #FFB703
(no máximo 1 detalhe pequeno por imagem), verde-menta #1FBF8A só para "ok". Nada de vermelho puro, nada de neon.
Nenhum texto, letra, número, logotipo, escudo, marca registrada, marca d'água ou assinatura dentro da imagem.
Fundo conforme a instrução de cada item; nunca xadrez, nunca sombra no fundo, nunca moldura.

Avatares (personagens): caricatura de craque na melhor fase, SEM semelhança facial com pessoa real:
traços simplificados (olhos grandes redondos, nariz em uma curva, boca em uma curva), rosto expressivo e simpático.
Cabeça grande (cerca de 1/3 da altura do busto, bobblehead moderado), pescoço curto, ombros largos, busto cortado no peito,
olhar frontal ou 3/4 leve, sorriso discreto. Cabeça ocupa 50 a 55% da largura do quadro, topo da cabeça a 8% do topo,
rosto sempre centralizado horizontalmente, para o recorte redondo e quadrado funcionarem.
Roupa: camisa/uniforme na cor e padrão indicados na ficha, sem escudo, sem patrocinador, sem número, sem logo de fabricante.
Pose e acessório típicos da ficha (luva de goleiro, braçadeira, terno de treinador, etc.), visíveis só da cintura para cima.
Fundo: cor chapada do setor indicada no item, sem detalhes. Todos os avatares com o mesmo enquadramento, mesma proporção e mesma espessura de contorno.

Ilustrações de estado e logo: objeto único centralizado, margem de 12% em volta, estilo adesivo:
contorno interno azul-marinho #0E1A24 e borda externa branca #EFF3F1 de espessura fina e uniforme.
Fundo magenta chapado #FF00FF, uniforme, sem sombra, sem degradê. Não use magenta, rosa ou roxo no objeto.
Sem personagem humano nas ilustrações de estado.

Fundos de tela: geometria abstrata de linhas de metrô, estações em círculos pequenos, curvas suaves, azul-marinho profundo,
contraste muito baixo (3 a 6%), nenhum elemento chamativo no centro, nenhum texto.
[[/ESTILO]]
```

### 3.3 Proporções e composição por tipo

| tipo | enquadramento | área segura |
|---|---|---|
| avatar 1024x1536 | busto, cabeça central, olhos a ~30% da altura; ombros chegam à base | quadrado central superior de 1024x1024 contém o rosto inteiro (para `rd` e `sq`); recorte 4:5 (`rt`) = topo 1024x1280 |
| ilustração 1536x1024 | objeto central, ocupa ~60% da largura | miolo 1280x860 |
| logo 1024x1024 | símbolo centrado, ocupa ~65% | círculo inscrito (para ícone redondo e favicon) |
| hero 1536x1024 | faixa útil horizontal no miolo | recorte 16:7 central (cerca de 1536x672); evitar detalhe nas bordas superior e inferior |

### 3.4 Instruções fixas de saída para este pacote (para o prompt-mestre, resumo)
- PNG, nomes exatos da lista 1, um item por arquivo, sem folha de contatos, `manifest.csv` no zip com `arquivo, pasta, largura, altura, forma, fundo, descricao`.
- Estrutura: `assets_sistema_v1/{avatares,ilustracoes,icones,fundos,extras}/` conforme o 04.
- Avisar qual item não conseguiu gerar em vez de inventar substituto.

## 4. Mapa para o protótipo (zip → slots `data-asset`)

Os slots já têm nome fixo no HTML (`data-asset`, `data-forma`, `data-size`). O pós-processo (script local de recorte e WebP, sem passar pelo ChatGPT) grava os arquivos **com o nome exato do slot**, em `prototipo_estilos/assets/<pasta>/<data-asset>.webp`. Para o protótipo trocar placeholder por imagem **sem retrabalho** basta um gancho único em `GH.slot` (feito pelo **Endrick**, uma função): se existir `assets/<pasta>/<data-asset>.webp`, renderiza `<img src alt="" loading="lazy" decoding="async">` dentro do slot e esconde o placeholder; se não existir (`onerror`), mantém iniciais/silhueta como hoje. As chamadas de tela (`GH.av`, `GH.icSetor`, `GH.slot`) não mudam.

| arquivo do zip | recorte local | arquivo final | slot (`data-asset`) / forma (`data-forma`) | tamanho do slot |
|---|---|---|---|---|
| `avatar_<slug>_ver_1024x1536.png` | quadrado central 1024x1024, máscara redonda feita pelo CSS (`.sl-rd`) | `assets/avatares/avatar_<slug>_rd.webp` | `avatar_<slug>_rd` / `rd` (lista, conversa, estações, paleta) | 256 |
| idem | quadrado 1024x1024 do topo, redimensiona para 512 | `assets/avatares/avatar_<slug>_sq.webp` | `avatar_<slug>_sq` / `sq` (cartão do agente) | 512 |
| idem | recorte 4:5 do topo (1024x1280) para 640x800 | `assets/avatares/avatar_<slug>_rt.webp` | `avatar_<slug>_rt` / `rt` (ficha do agente, 168 px na tela) | 640x800 |
| `vazio_espera_ret_1536x1024.png` | chroma `#FF00FF` → alfa, reduz 960x640 | `assets/ilustracoes/vazio_espera.webp` | `vazio_espera` / `vz` (Espera: "Fila zerada") | 960x640 |
| `vazio_agentes_ret_1536x1024.png` | idem | `assets/ilustracoes/vazio_agentes.webp` | `vazio_agentes` / `vz` (Agentes sem resultado) | 960x640 |
| `vazio_financas_ret_1536x1024.png` | idem | `assets/ilustracoes/vazio_financas.webp` | **novo** `vazio_financas` / `vz` | 960x640 |
| `vazio_generico_ret_1536x1024.png` | idem | `assets/ilustracoes/vazio_generico.webp` | **novo** `vazio_generico` / `vz` (telas de setor sem dados) | 960x640 |
| `erro_geral_ret_1536x1024.png` | idem | `assets/ilustracoes/erro_geral.webp` | **novo** `erro_geral` / `vz` (erro de carregamento) | 960x640 |
| `logo_contexto_explica_sq_1024x1024.png` | chroma → alfa, 256 | `assets/icones/logo_contexto_explica.webp` | `logo_contexto_explica` / `logo` (marca na ilha, 34 px) | 256 |
| idem | 32, 180, 512 | `favicon.png`, `apple-touch-icon.png`, `icon_512.png` na raiz | `<link rel="icon">`, não são slots | 32/180/512 |
| `fundo_hero_ilha_hor_1536x1024.png` | recorte 16:7 central, 1600x700 | `assets/fundos/fundo_hero_ilha.webp` | **novo** `fundo_hero_ilha` / `hero` (atrás da ilha, `background-size: cover`) | 1600x700 |
| `fundo_splash_ver_1024x1536.png` | recorte 9:16, 1080x1920 | `assets/fundos/fundo_splash.webp` | **novo** `fundo_splash` (abertura/celular) | 1080x1920 |
| `extra_og_capa_hor_1536x1024.png` | recorte 1200x630 | `assets/extras/og_capa.webp` | `<meta property="og:image">`, não é slot | 1200x630 |
| `avatar_voce_ver_1024x1536.png` | mesmos 3 recortes | `assets/avatares/avatar_voce_{rd,sq,rt}.webp` | **novo** `avatar_voce_*` (pontos de decisão do Guilherme, menu de usuário) | 256/512/640x800 |
| `icone_setor_<id>_sq_1024x1024.png` (opcional) | chroma → alfa, 128 | `assets/icones/icone_setor_<id>.webp` | `icone_setor_<id>` / `ic` (já existe `GH.icSetor`) | 128 |

Pontos que exigem uma linha nova no protótipo (todos pequenos, fora do escopo desta análise):
1. **Novos tipos em `GH.TIPOS`**: `vazio_financas`, `vazio_generico`, `erro_geral` reutilizam o tipo `vz`; `fundo_hero_ilha` reutiliza `hero`; só `fundo_splash` e `avatar_voce` precisam de entrada nova.
2. **Gancho de imagem em `GH.slot`** (descrito acima), com `.slot img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover }`. No `rd`, a máscara redonda já vem do `border-radius:50%` existente. O `object-position` do `rt` é `center top`.
3. **Estado vazio/erro/carregando como função única** `GH.estado(tipo, titulo, texto, acao)` que escolhe a ilustração e devolve o bloco `.vazio` já estilizado, para Finanças e para as outras telas. Texto sempre explica o que houve e o que fazer (por exemplo: "Não achei os movimentos. Confira se `financas/movimentos.csv` existe e toque em Tentar de novo.").
4. **Modo "ver slots"** continua funcionando: as caixas magenta de debug ficam por cima das imagens e o painel lista as novas chaves. A lista copiada ("Copiar lista") serve de conferência para o script de validação do **Valverde** (nome do slot = nome do arquivo final, 1 para 1).

Conferência cruzada com o 04: nome com sufixo de forma e tamanho (`_ver_1024x1536`), pastas iguais (`avatares/ ilustracoes/ icones/ fundos/ extras/`), PNG na entrega e WebP só no pós-processo, fundo opaco ou chave de cor (aqui `#FF00FF`), `manifest.csv` no zip.

## 5. Pendências para o Guilherme, o **Luiz Henrique** e o **Valverde**

1. **Valverde**: adotar `GH.slug(nome)` como `<id>` nos nomes (Seedorf, De Bruyne, André Carrillo...), e a chave de cor `#FF00FF` no lugar de `#00FF00`.
2. **Luiz Henrique**: cada ficha de avatar precisa dar só cor/padrão da camisa, cabelo, pose e acessório, **sem nome de jogador, clube ou número** (o prompt-mestre não cita pessoa real).
3. **Guilherme**: confirmar (a) cortar os 8 ícones de setor gerados, (b) 5 ilustrações de objeto sem personagem, (c) 56 avatares em um só retrato 2:3 com 3 recortes locais, (d) logo como símbolo sem letras, vetorizado depois.
