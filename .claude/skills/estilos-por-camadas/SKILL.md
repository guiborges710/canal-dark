---
name: estilos-por-camadas
description: Monta o cenas.json dos estilos Cartoon Vivo (cartoon_alive) e Colagem Documental (documentary_collage). A cena é descrita em dados e o renderizador compõe as camadas; não há sketch_cenas.py. Use quando o estilo do projeto for um desses dois.
---

# Estilos por camadas

Nestes estilos **você não escreve código de desenho**. Você descreve cada cena no `output/<slug>/cenas.json`, e `media/cartoon_lib.py` ou `media/colagem_lib.py` compõe as camadas a cada quadro. O vídeo continua sendo feito em cima do áudio: a cena dura o que a fala dura.

Toda cena tem os campos comuns: `tipo` (o id do estilo, igual em todas), `desenho` (`cena_0`, `cena_1`..., sem repetir), `fala` (da seção `## Narração`, sem alterar), `duracao` (mínimo, ≥ 2.5 s), `acao` (o que acontece, em uma frase), `transicao`, `camera`, e opcionais `rotulos` e `sons` (`{"t": s, "tipo": "impact|ding|whoosh"}`).

Posições em pixels no quadro de 1080x1920. `t` é o segundo da cena em que o elemento aparece. Mantenha textos entre y 190 e y 1500. A cena sempre tem de se sustentar sem som e nada pode ficar parado.

Confira com `python -m media.sketch --slug <slug> --previa` e abra `previa.jpg`: o erro aponta a cena e o campo. Não rode o render.

Antes de montar o `cenas.json`, leia `output/<slug>/componentes.md` (do **Raphinha**, que agora faz componentes dos quatro estilos): use os elenco/recortes/objetos aprovados, pelo nome, nas cenas indicadas, e siga as regras de layout (componente não cobre personagem nem texto).

## Câmera (os dois estilos)
`"camera": {"chaves": [{"t": 1.2, "x": 540, "y": 800, "zoom": 1.0}, {"t": 1.4, "x": 470, "y": 700, "zoom": 1.35, "curva": "rapida"}], "tremidas": [{"t": 1.4, "forca": 24}]}`

`curva: "rapida"` é o zoom de revelação. As camadas se movem em velocidades diferentes por conta própria (parallax).

## Cartoon Vivo (`"tipo": "cartoon_alive"`)
Desenho animado 2D, com personagens recorrentes e expressões fortes. **Use os mesmos personagens em todo o vídeo**, mudando pose e expressão no momento em que a fala vira.

- `paleta` (igual em todas as cenas): `sol`, `noite`, `menta`, `tijolo`. São 6 cores; nada foge delas.
- `cenario`: `rua`, `sala`, `quarto`, `escritorio`, `escola`, `cidade`, `liso`, `explosao` (raios girando, bom para revelação).
- `personagens`: `{"id", "x", "y": 1440, "escala", "olha": "dir|esq", "entrada", "t", "fala": true, "poses": [{"t", "pose", "expressao"}], "segura": {"tipo": "celular", "texto": "...", "escala": 1.1}}`.
  - `id`: `bia`, `teo`, `lu`, `zeca`.
  - `pose`: `neutra`, `aponta`, `bracos_cima`, `pensando`, `ombros`, `triste`, `comemora`, `maos_cintura`, `segura`, `medo`, `caminha`.
  - `expressao`: `neutra`, `feliz`, `risada`, `surpresa`, `triste`, `brava`, `pensativa`, `medo`.
  - `fala: true` mexe a boca. Piscar e respirar já acontecem sozinhos.
- `entrada` (personagem, objeto e texto): `corte`, `pop`, `salto`, `queda`, `deslize`.
- `objetos`: `{"tipo", "x", "y", "escala", "t", "ate", "entrada", "rot", "texto", "atras": true}`.
  - `tipo`: `celular`, `nota`, `moeda`, `casa`, `relogio`, `coracao`, `calendario`, `grafico`, `caixa`, `lampada`, `predio`, `seta`, `exclamacao`, `interrogacao`, `estrela`, `raio`, `suor`.
  - `celular` **sempre** com `texto` coerente com a cena. `grafico` precisa de `barras: [{rotulo, valor, texto}]`.
- `textos`: `{"texto" (até 26 caracteres), "x", "y", "tam", "t", "ate", "entrada", "cor": "claro|destaque|apoio|fundo|contorno", "rot", "pulsa"}`. Grandes e curtos.
- `baloes`: `{"de": "bia", "linhas": ["até 22 caracteres"], "t", "ate", "x", "y"}`.
- `transicao`: entrada `corte`, `chicote`, `zoom`, `continua`; saída as mesmas e `loop`. Para match cut, termine uma cena em `continua` e comece a seguinte em `continua`, com o personagem no mesmo lugar. Use `"saida": "loop"` na última cena para o vídeo recomeçar sem emenda.

Original sempre: nada de copiar personagem, canal ou propriedade existente.

## Colagem Documental (`"tipo": "documentary_collage"`)
Mural de evidências em papel. Cada cena revela uma prova: o que está na mesa precisa estar em `notas.md`. Documento é ilustração clara, nunca imitação de documento real de um órgão ou empresa.

- `superficie`: `mesa_preta`, `kraft`, `papel_bege`, `folha_branca`.
- `recortes`: `{"id", "tipo", "x", "y", "larg", "rot", "t", "entrada", "camada": "fundo|meio|frente", "fita": true, "ax", "ay"}`, mais os campos do tipo. `ax` e `ay` deslocam o ponto onde a conexão prende.
  - `tipo`:
    - `documento`: `titulo`, `linhas`.
    - `jornal`: `manchete`, `sub`.
    - `ficha`: `nome`, `campos: [{rotulo, valor}]`, `figura`.
    - `foto`: `figura`, `legenda` ou `arquivo` (asset local licenciado, na pasta do projeto, com licença em `notas.md`).
    - `mapa`: `pinos: [{x, y, rotulo}]`, de 0 a 1. É esquemático, não geográfico.
    - `linha_tempo`: `eventos: [{data, texto}]`.
    - `grafico`: `titulo`, `barras: [{rotulo, valor, texto}]`.
    - `data`: `data`.
    - `papel`: `cor`.
    - `tira`: `texto`.
  - `figura`: `pessoa`, `grupo`, `predio`, `casa`, `celular`. Silhueta sem rosto, nunca uma pessoa real.
  - `entrada`: `pousa`, `desliza`, `rasga`, `corte`.
- `conexoes`: `{"de": id, "para": id, "t", "dur"}`: o barbante cresce de uma evidência à outra.
- `destaques`: `{"em": id, "linha": n, "t", "dur"}`: o marca-texto percorre a linha n do recorte.
- `carimbos`: `{"texto" (até 18 caracteres), "x", "y", "rot", "t"}`.
- `anotacoes`: `{"texto" (até 26), "x", "y", "t", "seta_para": [x, y]}`.
- `textos`: `{"texto" (até 26), "x", "y", "tam", "t", "ate", "entrada", "rot"}`: tira recortada, em cima de tudo.
- `camera.chaves`: x de -400 a 1500, y de -300 a 2200, zoom de 1 a 2,6. O mural pode ir além da tela: ande sobre ele.
- `transicao`: entrada `corte`, `virada`, `recorte`, `sobrepoe`; saída as mesmas e `loop`.

Modelo pronto dos dois estilos: `media/demos/<id>/cenas.json`.
