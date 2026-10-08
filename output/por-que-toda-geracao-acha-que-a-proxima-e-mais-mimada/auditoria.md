# APROVADO

Re-auditoria de **Vini** em 2026-10-08. Slug: por-que-toda-geracao-acha-que-a-proxima-e-mais-mimada. O bloqueio anterior (imagens fora do tema) foi resolvido. Resta uma recomendacao de qualidade (item R1) e os passos manuais do upload. Este parecer nao promete monetizacao nem ausencia de risco: a decisao e do YouTube.

## Bloqueio anterior: RESOLVIDO

- Abri as 5 imagens e a miniatura e comparei com os image_prompt de cenas.json. Todas sao fotorrealistas, sem rosto identificavel, sem texto e no tema:
  - 000: sala escura, adulto de costas com bracos cruzados, jovem ao fundo, lampada quente. Bate com a cena 1.
  - 001: espelho com silhueta desfocada em penumbra, livros a esquerda. Bate com a cena 2 (a estante quase nao aparece, e aceitavel).
  - 002: ruinas gregas com colunas e banco de pedra, luz dourada. Bate com a cena 3.
  - 003: jovem de costas com caixas rumo a casa, carro com porta-malas aberto. Bate com a cena 4.
  - 004: mesa com radio e fita cassete, conta e celular, xicara e celular. Bate com a cena 5 (ver R1).
- thumbnail.jpg: dois espelhos, mochila, caneca e casaco numa mesa. Bate com thumbnail_prompt e com "Espelho, nao retrato". Honesta quanto ao tema.
- video.mp4: 1080x1920, 50,6 s (dentro de 60 s). Custo total US$ 0,00 (custo.json).

## Recomendacoes (nao bloqueiam)

- R1 [RISCO baixo/medio, qualidade] images/004.jpg e uma colagem 2x2 de quatro paineis. No video (frame em 48 s) aparece como tela dividida com linhas brancas no meio e quadros cortados, e o texto da legenda cai sobre a emenda. E a cena mais longa (pergunta final). Nao e infracao, mas parece descuidado e pode pesar na impressao de baixo esforco. Sugestao: regenerar a cena 5 com um unico quadro (por exemplo so a mesa com xicara e celular, prompt "single frame, no collage, no split screen") e remontar. Se preferir publicar assim, a decisao e sua.
- R2 [RECOMENDACAO] As imagens saem quadradas (1024x1024) e sao recortadas para 9:16 (perde-se cerca de 44% da largura). Funciona, mas gerar em 1080x1920 melhora o enquadramento. Em 002 ha um carro/van pequeno entre as ruinas (anacronismo menor) e rostos em relevo no banco; nao ha problema de politica.
- R3 [RECOMENDACAO] PUBLICAR.txt ainda traz a linha interna "Obs.: ... diga isso na descricao". Nao cole no upload; a descricao em metadados.json ja tem o aviso.
- R4 [RECOMENDACAO] Opcional: dizer "em dois mil e dezoito" na fala do Pew, para ancorar o ano.

## Passos manuais obrigatorios no upload (Studio)

1. Divulgacao de conteudo alterado ou sintetico: MARCAR. As imagens agora sao fotorrealistas geradas por IA (cenas de pessoas, casa e ruinas que parecem reais) e a voz e sintetica. CONFORMIDADE.md tambem sinaliza isso como atencao. Nao reconsultei a pagina oficial nesta rodada; confirme a pergunta atual no Studio (https://support.google.com/youtube/answer/14328491).
2. Marcar "nao e para criancas", se for o caso, e manter o aviso sintetico na descricao.
3. Cadencia: CONFORMIDADE.md aponta 4 videos nas ultimas 24 h (limite sugerido 2). Isso reflete testes e re-renders, mas publique poucos shorts por semana.

## Itens reconfirmados

- Pew: 15% (millennials, 25-37, 2018) vs 8% (primeiros boomers), EUA, fiel a notas 3.1 e ao roteiro. Sem generalizar para o Brasil. OK.
- Sem atribuicao a Socrates/Platao/Hesiodo/Horacio em roteiro.txt, metadados.json ou cenas.json. OK.
- Estudo de 2019: "tende", "padrao"; a metafora do espelho esta marcada como "Na nossa leitura". Aristoteles "descrevia". Teste de 1983 como hipotese. Sem sensacionalismo nem guerra de geracoes. OK.
- Descricao: aviso de voz/imagens sinteticas, fontes (Science Advances com ressalva de resumo de imprensa, Pew com link e "dados dos EUA", Retorica II.12). OK.
- Creditos: creditos.txt so tem nota de ilustracao; nao ha imagens de arquivo a creditar. OK.
- Originalidade: tese propria em angulo.md, cerca de 40% de comentario original (revisao.md), 0% de sequencias de 7 palavras copiadas das notas, 23 fontes. OK.
- Titulo honesto e entregue pelo conteudo. Trilha sintetica propria. OK.

## Incertezas que restam

- O artigo original de Protzko e Schooler nao foi lido (403); os dados vem de resumos de imprensa, como declarado na descricao.
- Licenca comercial do modelo de voz Kokoro: confirmar por conta propria (item aberto de CONFORMIDADE.md).
- Nao consegui rodar `python run.py check` neste shell (comando python nao encontrado fora do venv); usei o CONFORMIDADE.md regenerado (00:21), cujo conteudo e consistente com os arquivos atuais.
- Nao assisti ao video inteiro com audio; conferi quadros em 5, 20 e 48 s e a duracao.
