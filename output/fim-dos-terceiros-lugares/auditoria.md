**APROVADO** (modo FINAL, 2026-11-01). Nenhuma infração. 3 riscos/atenções e 2 recomendações abaixo. Isto não promete monetização; a decisão é do YouTube.

Escopo: imagem, som, animação, narração, duração e miniatura do render. O texto já foi aprovado em `auditoria_texto.md`.

## Infrações (bloqueiam)
Nenhuma.

## Os 2 itens de atenção do CONFORMIDADE.md
1. **Cadência alta (3 vídeos em 24 h, limite sugerido 2). Severidade: risco médio, não bloqueia.** É heurística do projeto, não regra do YouTube. A política de conteúdo inautêntico mira produção em massa com molde repetido. Mitigação: não subir os 3 no mesmo dia. `postar_pendentes.py` já sobe um por execução; espaçar os agendamentos. Este vídeo tem tema, dados e ângulo próprios.
2. **Voz sintética (narração por IA com a voz do autor). Severidade: obrigação de divulgação, não infração.** A descrição já diz "A narração é gerada por IA". Falta só marcar "conteúdo alterado ou sintético" no upload, porque a voz soa como pessoa real. Se o upload for via API/`publish`, conferir o campo no Studio antes de tornar público. Regra atual: https://support.google.com/youtube/answer/14328491 (não reconsultada hoje; confirmar no Studio).

## Verificação do render
- **Formato (OK):** H.264 yuv420p, 1080x1920, 30 fps, AAC. Duração 59,9 s, dentro de 30-60 s mas **sem folga**. O cenas.json soma 45 s, mas o vídeo segue a narração, que tem 59,9 s (audio.wav igual). Qualquer re-render com voz um pouco mais lenta estoura os 60 s. **Risco baixo.** Se regerar a voz, conferir a duração.
- **Imagem (OK):** 8 frames amostrados (0, 6, 14, 22, 30, 38, 46, 58 s). Folha pautada, traço de caneta, sem legenda na base. Texto legível, sem corte nas bordas. Cartões de -7,1% e +28,3% corretos. Cena do streaming ("continuar assistindo?") usa interface genérica, sem logo de terceiro. Não há foto, nem imagem de IA, nem rosto. Todo o visual é feito por código.
- **Fidelidade texto-imagem (OK):** os rótulos batem com roteiro e notas: "EUA (pesquisa ATUS)", "até 2013", "Brasil: consumo", "1º tri 2026 x 1º tri 2025", "nossa leitura", "hipótese, não prova", "economista Bryce Ward", "tempo sozinho cresceu". O gancho e a pergunta final estão presentes.
- **Ajustes do texto-auditoria aplicados (OK):** a fala diz "não encontramos essa medida" no Brasil e o rótulo é "sem essa medida". O gancho ficou "Seu terceiro lugar sumiu, e você nem percebeu" (afirmação, risco já registrado antes). O fecho "É hipótese, não prova" cobre o corpo do vídeo.
- **Som (OK):** pico -0,2 dB, média -18,2 dB. Não há clipping evidente, mas -0,2 dB está encostado em 0. Sem silêncios maiores que 1 s. Efeitos gerados por código, sem música de terceiros. **Não ouvi o áudio**, só medi.
- **Narração (incerto):** não ouvi. Verifiquei apenas existência, duração e ausência de buracos. Pronúncia, "1º tri", "7,1%" e "28,3%" precisam de uma escuta humana.
- **Metadados/PUBLICAR (OK):** título sem isca. Aviso de animação por computador presente. 4 fontes na descrição. custo.json: US$ 0.

## Miniatura (atenção leve)
- thumbnail.jpg é o frame 0 do vídeo (mesa, xícara, cadeiras e "seu 3º lugar sumiu"). Honesta e sem imagem de terceiros nem de IA. Mesmo tema do vídeo.
- **Recomendação:** o texto da miniatura está sem "?" ("seu 3º lugar sumiu"), enquanto o título e `thumbnail_texto` trazem "Seu terceiro lugar sumiu?". Vira afirmação. Colocar o "?" deixa a miniatura coerente com o título e com a hipótese do vídeo. O **Sidorf** pode ainda substituir a miniatura.
- **Recomendação (herdada do texto):** o título "dados de EUA e Brasil" sugere medida equivalente nos dois países, mas o Brasil é só consumo. O vídeo esclarece isso na fala. Opcional ajustar.

## Incertezas que restam
- Narração não escutada por mim, e a gíria "terceiro lugar" pode ser lida como "3º" ou "terceiro".
- A marcação de conteúdo sintético depende do upload.
- Heurística de cadência é do projeto; não confirmei limite oficial do YouTube.
- Marcar manualmente: "não é feito para crianças".
