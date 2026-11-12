# Notas do roteiro: esquema-de-piramide

## Decisões
- Gancho literal pedido pelo dono no frame 0: "Você sabe o que é esquema de pirâmide?".
- Ângulo comportamental (confiança no mensageiro + golpe antigo de fachada nova) garante
  mais de 1/3 de comentário original: cenas 3, 4 e 6 são interpretação/reenquadre; só as
  cenas 2 e 5 são fato puro.
- Contagem pelo critério do validador (`len(texto.split())` por cena, est. = palavras/3,0
  + 0,2 s, piso 3 s no gancho e 4 s no fechamento): 165 palavras no total, ~56,5 s. Dentro
  do limite de 60 s. Verificada com `_count.py` (.venv).

## Contagem por cena (verificada)
- Cena 1: 8 palavras -> 3,00 s (piso)
- Cena 2: 32 palavras -> 10,87 s
- Cena 3: 28 palavras -> 9,53 s
- Cena 4: 29 palavras -> 9,87 s
- Cena 5: 34 palavras -> 11,53 s
- Cena 6: 10 palavras -> 3,53 s
- Cena 7: 24 palavras -> 8,20 s
- Total: 165 palavras, ~56,53 s.

## Enxugamento (de 187 para 165 palavras)
- Cena 5 foi de 53 para 34 palavras: formato telegráfico por caso (nome, ano, condenação),
  sem "e os casos são enormes", sem "por organização criminosa" e sem repetir "caiu/ruiu".
  Mantidas as datas, os nomes e o "segundo a acusação movimentou bilhões" do Faraó.
- Cena 2: "de verdade" -> "real" (−2 palavras).
- Cena 4: "o convite chega pela pessoa em quem você confia" -> "o convite vem de quem você
  confia" (−2 palavras), sem perder o insight da confiança no mensageiro.

## Como tratei os pontos frágeis
- TelexFree: sem valor total (divergência R$1bi a R$5bi+). Só a condenação confirmada.
- Faraó: "segundo a acusação movimentou bilhões"; condenação de 2025 (como nas notas). Não
  atribuí a condenação "à pirâmide em si"; o texto fala só da condenação no ano.
- Avestruz: só ano 2005 + "dirigentes condenados" (fato). Sem reparação nem nº de vítimas.
- Trader Group / Atlas Quantum / Boi Gordo: fora (frágeis ou para não sobrecarregar).
- Geração: afirmo explicitamente que NÃO é por culpa de uma geração; nenhum recorte etário.

## "Condenado" só onde há condenação
- Avestruz (dirigentes), TelexFree (sócios), Faraó (2025): todos com condenação nas notas.
  Não usei "condenado" para Trader Group (foi multa da CVM, não citado).

## Gramática revisada
- Concordância conferida. "dirigentes condenados" e "sócios condenados" (plural). Faraó:
  "condenado" (singular). Sem erro de concordância.

## Diferença pirâmide x multinível
- Incluída na cena 3, pela origem do dinheiro (venda real vs. adesão), conforme CVM/Senacon.
- Nenhuma marca de venda direta/multinível citada.

## Fecho
- Pergunta de volta aberta, sem resposta pronta, puxando o ângulo (confiança x origem do
  dinheiro). Abertura e fecho diferentes dos outros vídeos do canal.
