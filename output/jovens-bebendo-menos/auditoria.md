**APROVADO** (modo FINAL, reauditoria da v3, Vini, 2026-10-29)

Escopo: só o que mudou desde a v2: (1) chamado desenhado "Comenta aqui" na cena 7; (2) primeira linha da descrição; (3) comentario_fixado.txt. Narração, falas, duração e demais cenas não foram reabertas. A v2 segue em versoes/v2-opus/.

| # | Item | Resultado |
|---|---|---|
| 1 | Formato (ffprobe): H.264 1080x1920, 30 fps, yuv420p, 46,77 s; áudio AAC 48 kHz estéreo, mesma duração da v2. Média -18,1 dB e pico -0,3 dB, iguais à v2 (o ding de 1,3 s não muda o nível) | OK |
| 2 | Chamado (final_v3.jpg e quadro em 46,6 s em tamanho cheio): balão de comentário com "..." , "Comenta aqui" sublinhado em laranja e seta curva. Ocupa y de cerca de 1375 a 1490, acima do limite de 1500; legível (vermelho-escuro sobre papel claro, fonte grande). Não toca no braço, nas setas, nos bonecos nem no título; o espaço entre a seta da chave e o texto é livre | OK |
| 3 | Fora da faixa coberta pela interface: texto e balão ficam acima de y=1500 (zona de título/descrição/canal do Short). A ponta da seta curva chega a x≈900, y≈1485, na borda da coluna de botões da direita (curtir/comentar/compartilhar). Fica acima da área mais ocupada, mas é o ponto mais próximo da interface | OK, com observação |
| 4 | Engagement bait: "Comenta aqui" é um convite simples e coerente com a pergunta do vídeo ("Coisa de uma geração?"). Não oferece recompensa, não pede curtir/inscrever em troca de algo, não promete conteúdo que não entrega, não força comentário com informação falsa. Não é a prática que a política de spam/engagement bait do YouTube descreve (isca de interação por troca ou enganosa). Não consultei a página oficial novamente nesta checagem | OK (risco baixo) |
| 5 | Descrição, nova linha 1: "Ainda faz sentido chamar de coisa de uma geração, se a queda aparece em todas as idades? Conta nos comentários como é aí." É a pergunta de fecho já aprovada, sem número nem fato novo. Restante da descrição idêntico (fontes, aviso de animação por computador e narração por IA presentes) | OK |
| 6 | comentario_fixado.txt: enquete "A) menos B) diferente C) igual de sempre" e alternativa "geração ou momento da vida". São perguntas de opinião, sem afirmar fato, número ou data novos. Não é pedido de curtir/compartilhar nem prometem nada | OK |
| 7 | Miniatura (thumbnail.jpg): igual à v2 ("Gen Z parou de beber?", copo com X e boneco de boné). Sem imagem de terceiros nem de IA | OK |
| 8 | Sem imagem de terceiros nem de IA; o novo elemento é desenho por código; o ding é gerado por sfx.py | OK |

## Bloqueios
Nenhum.

## Observações e incertezas
- Vi o quadro final em tamanho cheio e os 4 quadros de final_v3.jpg; não revi o vídeo inteiro nem ouvi o ding para conferir a sincronia com o aparecimento do chamado (o hash do áudio mudou em relação à v2, como esperado pelo ding).
- A ponta da seta curva em x≈900 fica perto da coluna de botões do Short; se quiser margem, encurte a seta (não bloqueia). Mantêm-se os lembretes anteriores: marcar "conteúdo alterado ou sintético" no Studio e a ausência de legenda queimada.
- Esta auditoria não promete monetização; a decisão é do YouTube.

---

**APROVADO** (modo FINAL, reauditoria da v2, Vini, 2026-10-29)

Escopo: só a imagem da v2 (desenho refeito pelo Olise: sketch_cenas.py e tempos de "sons" no cenas.json). Narração, falas, rótulos, metadados e duração são os da v1, aprovada abaixo. O texto não foi reaberto (auditoria_texto.md já APROVADA). A v1 segue em versoes/v1-sonnet/ para comparação.

## Checagens da v2

| # | Item | Resultado |
|---|---|---|
| 1 | Formato (ffprobe): H.264 1080x1920, 30 fps, yuv420p, 1403 quadros, 46,77 s; áudio AAC 48 kHz estéreo, mesma duração (46,77 s). Pico -0,3 dB, média -18,1 dB | OK, igual à v1 (a observação sobre pico perto de 0 dBFS continua, não bloqueia) |
| 2 | Imagem (contato.jpg, previa.jpg com 18 quadros e 8 quadros extras do video.mp4 em 1,3 s, 11 s, 14 s, 21 s, 29 s, 33 s, 38 s e 46,7 s): nada cortado, nada sobreposto, nada fora do quadro; títulos legíveis; elementos ocupam a metade de cima e o centro | OK |
| 3 | Sem legenda ou texto na base (a parte inferior fica só com a pauta do caderno; nenhuma fala transcrita) | OK |
| 4 | Rótulos x cenas.json: Gen Z parou de beber?; Adultos nos EUA que bebem (62%, 58%, 54%); Adultos jovens: 59% -> 50% (59%, 50%); 53%: moderação faz mal; Queda em todas as idades; Brasil: sem número único; Coisa de uma geração? | OK, todos batem |
| 5 | Números nas barras: 62/58/54 (2023/2024/2025) e 59/50 batem com as notas (fatos 2 e 4). Alturas proporcionais a partir do zero (54/62 ~ 0,87; 50/59 ~ 0,85); a linha tracejada marca o nível de 54% | OK |
| 6 | Textos novos sem nota correspondente: anos 2023/2024/2025 sob as barras da cena 1 (são os anos de 62/58/54 nas notas, iguais à v1); símbolos "?", "!" e "≠" (sinais gráficos, sem afirmar número ou fato); "=" entre garrafa e copo na cena 5 (destilado empata com cerveja, nota 23, fala da cena) | OK. Nenhum número ou texto sem fonte |
| 7 | Cena do Brasil: mancha verde genérica com um ponto, três pranchetas com gráficos de barras sem números e "≠" (as pesquisas divergem). Não reproduz o contorno do país nem induz a erro | OK |
| 8 | Cena 4: cinco bonecos (de boné a idoso) com setas para baixo e a garrafa = copo; sem número novo | OK |
| 9 | Só desenho por código (copo, bonecos, barras, balança, lâmpada, coração, pranchetas, lupa, fundo de caderno). Sem foto, sem imagem de terceiros, sem imagem de IA. Sons continuam por código (sfx.py) | OK |
| 10 | Miniatura (thumbnail.jpg): "Gen Z parou de beber?", copo com X e boneco de boné. Representa o tema do vídeo, sem clickbait, sem conteúdo gráfico. Observação igual à v1: metade inferior vazia e sem o recorte "Nos EUA" (a pergunta aberta é honesta com o conteúdo) | OK |
| 11 | Conteúdo sensível: álcool em copo e garrafa genéricos, sem cena de consumo nem incentivo; ícone de alerta (triângulo) na cena 3 é neutro | OK |

## Bloqueios
Nenhum.

## Observações e incertezas
- Conferi 12 quadros do contato, 18 da prévia e 8 extras; não vi o vídeo inteiro quadro a quadro, nem ouvi o áudio de novo (o áudio e a narração não mudaram).
- Os tempos de "sons" foram alterados no cenas.json; só verifiquei que o áudio entregue tem a mesma duração e nível. Não fiz a conferência de sincronia som x animação ouvindo.
- Lembretes da v1 mantidos: **Memphis** deve marcar "conteúdo alterado ou sintético" no Studio (voz realista); sem legenda queimada, quem assiste sem som perde a fala (recomendação).
- Esta auditoria não promete monetização; a decisão é do YouTube.

---

# Histórico: parecer da v1 (versoes/v1-sonnet/)

**APROVADO** (modo FINAL, Vini, 2026-10-29)

Escopo: só o que o render produziu (imagem, som, animação, narração, formato, miniatura). O texto não foi reaberto (auditoria_texto.md já APROVADA).

## Checagens

| # | Item | Resultado |
|---|---|---|
| 1 | Formato: 1080x1920, 30 fps, H.264 yuv420p, faixa TV (limited), AAC 48 kHz estéreo | OK |
| 2 | Duração: 46,8 s (faixa 30 a 60 s do canal) | OK |
| 3 | Áudio: faixa presente, pico -0,34 dBFS, média -18,1 dB, flat factor 0 (sem clipping detectado), silencedetect sem silêncio longo | OK. Observação: pico muito perto de 0 dBFS; o encode do YouTube pode causar intersample peak leve. Não bloqueia |
| 4 | Imagem (contato.jpg + quadros extras de 9 a 18 s): nada cortado ou sobreposto; títulos legíveis; barras partem do zero; rótulos batem com cenas.json (Gen Z parou de beber?; Adultos nos EUA que bebem 62/58/54%; Adultos jovens 59% -> 50%; 53%: moderação faz mal; Queda em todas as idades; Brasil: sem número único; Coisa de uma geração?) | OK |
| 5 | Sem legenda/texto na base do quadro (a metade inferior fica livre; não há legendas da fala) | OK. Observação: sem legenda queimada, quem assiste sem som perde a fala; recomendação, não exigência |
| 6 | Animação: só desenho por código (copo, boneco, barras, lupa, mapa genérico, fundo de caderno). Sem foto, sem imagem de terceiros, sem imagem de IA | OK |
| 7 | Cena do Brasil: blob verde genérico, sem a forma do país | OK (ilustração; não afirma nada) |
| 8 | Narração (IA, voz clonada do autor): 7 falas de 3,9 a 11,2 s; 2,7 a 3,8 palavras/s | ATENÇÃO (observação). A fala da cena 1 (11,15 s, a mais densa, com números) e as de ~3,8 pal/s podem ficar rápidas para compreensão, sobretudo os números 62/58/54. Não bloqueia por gosto; se o dono quiser, desacelerar só essa fala |
| 9 | Divulgação sintética: descrição tem aviso de animação por computador e de narração por IA com a voz do autor. CONFORMIDADE.md: 10 OK, 1 ATENÇÃO (lembrete do aviso sintético, já atendido na descrição) | OK. Lembrete para **Memphis**: marcar também o campo "conteúdo alterado ou sintético" no Studio (voz realista); a descrição não substitui o campo |
| 10 | Miniatura (thumbnail.jpg, quadro de 1,5 s): "Gen Z parou de beber?", copo com X e boneco com "?". Representa o tema, sem clickbait, sem conteúdo gráfico, sem imagem de terceiros | OK. Observações: ocupa só a parte de cima/centro (metade inferior vazia) e não traz o recorte "Nos EUA"; a pergunta aberta do vídeo é honesta com o conteúdo. Se **Sidorf** gerar outra, manter coerência com o vídeo |
| 11 | Sons: efeitos por código (sfx.py), sem música ou áudio de terceiros | OK |
| 12 | Conteúdo sensível: álcool tratado de forma neutra, sem cena de consumo explícito nem incentivo | OK |

## Bloqueios
Nenhum.

## Incertezas
- Conferi 8 quadros do contato mais 6 quadros de 9 a 18 s; não assisti ao vídeo inteiro quadro a quadro nem ouvi a pronúncia de "Gen Z" e dos números (só medi o áudio). Recomenda-se uma escuta final pelo dono antes de tornar público.
- Esta auditoria não promete monetização nem ausência de risco; a decisão é do YouTube.
