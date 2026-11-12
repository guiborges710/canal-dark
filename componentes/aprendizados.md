Fase: aprendendo

# Aprendizados do Raphinha (o que o Guilherme ensinou)

Lido pelo **Raphinha** antes de todo vídeo e repassado ao **Olise**. Manda sobre qualquer outra regra de componentes. Formato de cada item: **regra** · por quê · como aplicar · data.

## Regras de layout
- **Não cobrir bonecos.** Nenhum elemento (tela, texto, seta, balão) pode tapar um boneco. · pedido do Guilherme · checar sobreposição na prévia antes de entregar · 2026-10-30
- **Não cobrir texto.** Nenhum elemento pode tapar texto que ainda precisa ser lido; se um novo elemento entra no mesmo lugar, o anterior sai antes. · pedido do Guilherme · 2026-10-30

## Regras de estilo
- Tela de celular, chat ou mensagem sempre com texto coerente com o contexto da cena. · ver memória "celular sempre com texto" · 2026-10-30
- **Linha vermelha da margem do caderno com opacidade bem baixa** (visível, mas só de levinho, ~28%). · pedido do Guilherme · já aplicada em `papel()` de `media/sketch_lib.py`; não usar a cor cheia · 2026-10-30

## Correções e aprovações por vídeo
(O Raphinha acrescenta aqui, em ordem, o que o Guilherme corrigir ou aprovar em cada vídeo.)

### 2026-10-30 · pair-programming-colaboracao · APROVADO (sem correções)
- **Método aprovado: manter assim.** · o Guilherme aprovou os 13 componentes e o layout de primeira ("ficou legal, ficou bacana, gostei"), sem nenhuma correção · repetir o mesmo processo nos próximos vídeos:
  1. **Componentes isolados** — uma função por componente em `componentes_video.py`, parametrizada por posição/escala/`frac`.
  2. **Tabela de caixas** — cada componente tem a função companheira `*_box(cx, cy, s, ...)` devolvendo a caixa ocupada `(x, y, w, h)` (âncora no canto superior esquerdo), incluindo pés/rótulos/caudas.
  3. **Checador automático de sobreposição** — `gerar_componentes.py` usa as caixas para verificar que nada cobre boneco nem texto antes de entregar.
  4. **Imagens transparentes** — um PNG por componente, para o Olise compor sem fundo.
  5. **cenas_exemplo.jpg** — montagem das cenas com os componentes nas posições sugeridas, para o Guilherme validar o layout (além do `contato.jpg` rotulado).

### 2026-10-31 · esquema-de-piramide · APROVADO (sem correções)
- **Método aprovado de novo: manter assim.** · o Guilherme aprovou de primeira os 12 componentes novos e o layout ("pode seguir"), sem nenhuma correção · segue valendo o mesmo processo de 2026-10-30 (componentes isolados + `*_box` + checador de sobreposição + PNGs + contato rotulado); nada a mudar no pipeline de componentes.
- Os 12 novos foram promovidos para `media/sketch_componentes.py` e entraram no `catalogo.md` (piramide_pessoas, pilha_dinheiro, fonte_dinheiro, convite_confianca, icone_avestruz, icone_gado, icone_bitcoin, martelo_juiz, caixa_caso, pessoa_ou_dinheiro — mais os ícones de fachada). Convenção de cor deste vídeo: AZUL=pessoa/multinível legal, LARANJA=dinheiro em movimento/recrutamento, VERDE=produto real, VERMELHO=colapso/condenação, SOL_AMARELO=moeda.

### 2026-11-03 · companhias-de-ia-entre-adolescentes (Colagem Documental) · CORREÇÃO, nova versão aguardando validação
- **Na colagem, não usar anotação em letra vermelha sobre faixa branca, com frase picada.** · o Guilherme revisou `anotacoes_a_mao` e disse "tudo, não gostei de nada" · a v3 usa bilhete amarelo, caneta preta e frase inteira em até duas linhas (`postit` em `componentes_video.py`). Só vira padrão se ele aprovar; a letra é a fonte fixa da biblioteca, então, se a queixa continuar, o próximo teste é trocar a fonte (`media/colagem_lib.py`, fora da escrita do **Raphinha**).
