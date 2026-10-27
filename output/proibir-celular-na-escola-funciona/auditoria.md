APROVADO

# Auditoria final (depois do render com narração): proibir celular na escola funciona?

Escopo: imagem, som, narração, animação, miniatura e descrição do render. O texto já foi aprovado em `auditoria_texto.md` (com adendo sobre as falas).

## Itens verificados
- **Especificações:** 53,5 s, 1080×1920, 30 fps, H.264 + AAC 48 kHz estéreo. Dentro da faixa de 30 a 60 s. OK.
- **Narração:** três falas (gancho, barras, fechamento), com a duração de cada uma registrada em `falas/falas.json` (5,7 s, 18,5 s e 27,5 s). O texto das falas é o do roteiro aprovado. OK.
- **Volume:** média de -18,3 dB; pico de -0,2 dB. Sem clipagem, mas o pico está perto de 0 dB: vale conferir no upload se o áudio não estourou. Atenção leve.
- **Sons:** efeitos gerados por código (`media/sfx.py`), mixados abaixo da narração. Sem música de terceiros. OK.
- **Animação:** cenas válidas (`validate` passou); texto nos cartões dentro da tela, verificado nos frames anteriores. Não houve mudança visual além da duração. OK.
- **Imagens:** todo o visual é desenhado por código. Sem foto de terceiros nem imagem de IA. OK.
- **Descrição:** traz "Animação feita por computador, com narração por IA a partir da voz do autor" e "Fontes:". OK.
- **Verificador automático:** `CONFORMIDADE.md` com 10 ok, 2 atenção, 0 faltando.

## Atenções (não bloqueiam)
- **Voz sintética:** o verificador marca a narração gerada por IA. Ao subir, marcar "conteúdo alterado ou sintético", como ele pede.
- **Cadência:** 3 vídeos nas últimas 24 h (limite sugerido: 2).
- **Pico de áudio** perto de 0 dB (ver acima).

## Pendências que só o Guilherme confirma
- Assistir ao vídeo inteiro e ouvir a narração.
- Confirmar que o vídeo não é para crianças.

## Veredito
APROVADO para publicação privada. A decisão final de monetização é do YouTube.
