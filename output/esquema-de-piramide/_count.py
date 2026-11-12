cenas = {
    1: "Você sabe o que é esquema de pirâmide?",
    2: "É quando o dinheiro não vem de um produto real. Vem da entrada de quem foi recrutado depois de você. Enquanto entra gente nova, parece mágica. Quando para, a base perde tudo.",
    3: "E aqui está a diferença que quase ninguém olha. No multinível legal, o dinheiro vem da venda real. Na pirâmide, vem só da adesão. Mesmo discurso, origens opostas.",
    4: "No Brasil isso pega, e não por culpa de uma geração. Pega porque o convite vem de quem você confia. A confiança no mensageiro desarma a desconfiança no negócio.",
    5: "Avestruz Master, dois mil e cinco: dirigentes condenados. TelexFree, dois mil e treze: sócios condenados. E o Faraó dos Bitcoins, que segundo a acusação movimentou bilhões, condenado em dois mil e vinte e cinco.",
    6: "Muda a fachada: gado, avestruz, bitcoin. A mecânica se repete.",
    7: "Então, quando a oportunidade chega pela pessoa em quem você confia, o que você confere primeiro: a pessoa, ou de onde sai o dinheiro?",
}

pisos = {1: 3.0, 7: 4.0}
total = 0.0
soma_pal = 0
for n, t in cenas.items():
    p = len(t.split())
    est = p / 3.0 + 0.2
    if n in pisos:
        est = max(est, pisos[n])
    soma_pal += p
    total += est
    print(f"Cena {n}: {p} palavras -> {est:.2f}s")
print(f"TOTAL palavras: {soma_pal}")
print(f"TOTAL estimado: {total:.2f}s")
