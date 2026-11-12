# Componentes do vídeo: companhias-de-ia-entre-adolescentes-amizade-entretenimento-o

**AGUARDANDO APROVAÇÃO DO GUILHERME** (fase "aprendendo"). O **Olise** só começa depois do ok na tela do estúdio.

Estilo: Colagem Documental (`documentary_collage`). Proposta do **Raphinha**. Nada foi promovido para `componentes/catalogo.md` antes da aprovação.

## Onde está
- `componentes/contato.jpg`: todos os componentes, rotulados.
- `componentes/cenas_exemplo.jpg`: as 10 cenas montadas pelo compositor real (`compor_cena`), no fim de cada cena.
- `componentes/<nome>.png`: um por componente, sobre kraft. `componentes/transparentes/`: os mesmos, com fundo transparente.
- `componentes/figuras/`: figuras em cinza que entram nos recortes pelo campo `arquivo`.
- `componentes_video.py`: specs (`RECORTES`, `CARIMBOS`, `TIRAS`, `ANOTACOES`) e o layout completo em `CENAS`.
- `componentes_gerar.py`: gera tudo e roda o checador. Da raiz: `.venv/Scripts/python output/<slug>/componentes_gerar.py`. Com `--so-anotacoes`, refaz só os bilhetes e as folhas de conferência.

## Componentes (nenhum reutilizado do catálogo: ele só tem sketch)
| Grupo | Nomes |
|---|---|
| Fotos com figura nova (7) | `foto_adolescente_celular`, `foto_robo`, `foto_ia`, `foto_ferramenta`, `foto_diversao`, `foto_curiosidade`, `foto_um_em_cada_tres`, `foto_com_quem` (as duas do robô usam a mesma figura) |
| Fotos com figura da biblioteca | `foto_amigos`, `foto_amigos_de_verdade`, `foto_gente` (`figura: grupo`) |
| Documentos | `doc_pesquisa`, `doc_como_veem`, `doc_assunto_serio`, `doc_ia`, `doc_gente` |
| Selo e jornal | `selo_um_em_cada_tres`, `jornal_aviso` |
| Mapas | `mapa_eua`, `mapa_brasil` (esquemáticos, sem rótulo: o nome vem na tira) |
| Carimbos | `carimbo_quase_o_contrario`, `carimbo_atencao`, `carimbo_dados_dos_eua`, `carimbo_anunciado` |
| Textos | `tiras_de_texto.png` (14 tiras), `anotacoes_a_mao.png` (4 bilhetes amarelos, refeitos na v3) |

## Cenas e posições (x, y em px; `larg` e demais campos em `CENAS`)
Dividi as cenas 3 e 5 da `direcao_viral.md` em frases, para ter uma ideia visual por cena. A numeração abaixo é a da direção. O bloco de cada cena em `CENAS` já traz `t`, `entrada`, `conexoes` e `destaques`.

| Cena | Mesa | Componentes e posição |
|---|---|---|
| 1 gancho | `mesa_preta` | `tira_trocou` (540,265); `tira_robo` (540,395); `foto_adolescente_celular` (210,715); `foto_amigos` (860,705); `foto_robo` (540,1115); barbante das duas fotos ao robô; `carimbo_quase_o_contrario` (540,1412) |
| 2 pesquisa | `kraft` | `tira_americana` (540,300); `doc_pesquisa` (540,640); `tira_eua` tam 72 (275,962); `mapa_eua` larg 430 (275,1280); `foto_amigos` com legenda "adolescentes", larg 390 (790,1185) |
| 3a ferramenta | `mesa_preta` | `tira_quase_metade` (540,300); `foto_ferramenta` (540,720); `doc_como_veem` (540,1230), marca-texto na linha 0 |
| 3b motivos | `papel_bege` | `tira_motivo` (540,285); `foto_diversao` (390,690); `nota_depois` (270,1130) com seta para (500,1060); `foto_curiosidade` (720,1170) |
| 3c amigos | `kraft` | `tira_maioria` (540,265); `tira_mais_tempo` (540,405); `foto_amigos_de_verdade` (540,810); `foto_robo` com legenda "a IA", larg 240 (840,1290); `nota_menos_tempo` (320,1385) com seta para (690,1255) |
| 4 virada | `mesa_preta` | `carimbo_atencao` (540,1405); `foto_um_em_cada_tres` (540,655); `selo_um_em_cada_tres` (540,305); `doc_assunto_serio` (540,1095). Sem dramatização: trecho sensível |
| 5a leitura | `papel_bege` | `tira_leitura` (540,285); `tira_nao_e_defeito` (540,1370); `foto_ia` (205,600) e `doc_ia` (715,600); `foto_gente` (205,1040) e `doc_gente` (715,1040) |
| 5b ressalva | `folha_branca` | `tira_atencao` (540,265); `tira_eua` (275,445); `tira_brasil` (805,445); `mapa_eua` (275,810); `mapa_brasil` (805,810); `carimbo_dados_dos_eua` (540,1185); `nota_nao_da` (540,1420) |
| 6 empresa | `kraft` | `jornal_aviso` (540,760), marca-texto na linha 1; `carimbo_anunciado` (540,1350). Sem nome de empresa e sem data |
| 7 pergunta | `mesa_preta` | `nota_nao_e_se_usam` (540,1310); `foto_adolescente_celular` larg 400 (285,850); `foto_com_quem` (800,850); barbante entre as duas; `tira_com_quem` (540,265); `tira_pesa` (540,405) |

## Regras de composição
1. **Nada cobre figura nem texto.** Vale para recorte, carimbo, tira, anotação, seta e barbante. Se um elemento novo entra no lugar de outro, o anterior sai antes. Única exceção: o papel de apoio, que fica embaixo do próprio carimbo ou anotação.
2. **Carimbo sobre papel de apoio** (`apoio_carimbo`) e **anotação sempre em bilhete amarelo com caneta preta** (`postit`; os dois já incluídos em `CENAS`). Cada linha do bilhete é uma anotação com `cor` preta: não troque a cor nem separe as linhas do papel.
3. **Seta de anotação sai por cima do texto.** A seta nasce 44 px acima do centro da primeira linha, ainda dentro do bilhete (a biblioteca fixa esse ponto); o alvo tem de ficar acima dela, ou o traço risca a frase.
4. **Barbante preso na borda da peça** (`ax`, `ay`), nunca no centro: não pode passar sobre figura ou texto.
5. Texto entre `SEGURO_TOPO` e `SEGURO_BASE` (y 190 a 1500). No máximo uma ideia visual por cena.
6. **Câmera com pouco zoom onde há peça perto da borda** (cenas 1, 2, 5a e 5b): até 1,05, centrada. Nas cenas com bilhete (3b, 3c, 5b e 7), o mesmo limite: papel e caneta andam em velocidades um pouco diferentes com a câmera, e zoom maior desalinha a letra do papel. O checador confere a posição sem câmera; zoom maior corta as peças. Confira em `previa.jpg`.
7. Leve o bloco de `CENAS` sem o campo `rotulo_raphinha`. `acao` e `duracao` nele são provisórios: escreva a `acao` e ajuste a duração à fala. A divisão de `fala` é sugestão; o texto vem do `roteiro.txt`.

## Conteúdo e monetização
- **Textos dos bilhetes (v3):** "e depois..."; "menos tempo / com a IA" (notas: 80% passam mais tempo com amigos reais do que com a IA); "não dá para dizer / que o Brasil é igual" e "a pergunta não é / se eles usam" (do `roteiro.txt`).
- **Números na tela:** "quase metade" e "1 EM CADA 3". Usei "1 em cada 3", como no roteiro, porque `media/roteiro.py` conta "1 em 3" como dois números.
- **"2025" em `doc_pesquisa`** vem da `direcao_viral.md` e das notas, mas a mesma direção diz "só dois números". Se contar como terceiro, troque a linha por "Estados Unidos".
- **Documento é ilustração:** sem logo, assinatura, selo ou nome de organização; `doc_pesquisa` e `jornal_aviso` trazem "Ilustração do canal".
- **`jornal_aviso` diz "anuncia":** é só o que a revisão do **Courtois** confirma. Não trocar por "acabou" ou "encerrou".
- Sem foto de pessoa real, sem mídia externa, sem instrução de uso e sem cena que romantize relação com bot. As silhuetas não têm rosto.
- **`arquivo`:** as figuras foram desenhadas por código neste projeto, então não há licença de terceiros. A regra do estilo pede licença em `notas.md` para foto local; **Vini** precisa saber que estas não são fotos.
- **Sem celular com tela:** a figura `celular` da biblioteca tem tela vazia, o que fere a regra de `aprendizados.md`. Por isso o celular aparece só de lado, em `foto_adolescente_celular`. Não use `figura: celular`.

## Regras de `aprendizados.md` aplicadas
Não cobrir bonecos; não cobrir texto; tela de celular sempre com texto coerente; método aprovado de componentes isolados, caixas, checador, PNGs transparentes e `cenas_exemplo.jpg`. Aqui as caixas saem de `elementos()` em `componentes_gerar.py`, medidas nas próprias peças, em vez de funções `*_box`.

## Atenção para o **De Bruyne** e o **Olise**
O roteiro tem 151 palavras: deve dar perto de 1 minuto de narração (estimativa, sem voz gerada), contra a duração alvo de 30 s. As 10 cenas acompanham o texto atual; se o roteiro for cortado, a cena 3c e a 5b são as primeiras a mudar.
