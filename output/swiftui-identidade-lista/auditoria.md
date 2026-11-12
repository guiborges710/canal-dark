# Auditoria FINAL (imagem, som, animação, narração, miniatura): swiftui-identidade-lista

**APROVADO** (com ressalvas leves; vídeo de demonstração/pedido direto, fora do nicho, NÃO será publicado nem entrará na fila)

## Itens "atenção" do CONFORMIDADE.md
1. Cadência alta (4 vídeos em 24 h, limite sugerido 2): RISCO, não infração. Irrelevante aqui porque o vídeo não vai ao ar. Se algum dia for publicado, espaçar uploads.
2. Voz sintética: RISCO/recomendação. Marcar "conteúdo alterado ou sintético" no upload (voz clonada do autor soa como pessoa real). A descrição já declara a narração sintética e a animação por computador.

## Verificado
- video.mp4: H.264 1080x1920, 30 fps, AAC, 39,17 s (dentro de 30-60 s). Áudio presente, média -18,4 dB, pico -0,2 dB (sem clipping evidente), sem silêncio >1 s.
- Telas nunca vazias: em todas as cenas há título/rótulos desde o início; o desenho entra em menos de ~1 s. Sem congelamento de quadros.
- Rótulos legíveis e fiéis ao cenas.json; sincronia cena/fala consistente com as durações das falas (cena a cena em cima do áudio).
- Visual 100% por código, sem imagem de terceiros ou de IA. Sons por código, sem música de terceiros. Custo 0.
- Descrição com aviso de animação por computador e fontes (checado no CONFORMIDADE.md). Título honesto: o vídeo entrega o que promete, com a ressalva "hipótese/causa possível" repetida.
- thumbnail.jpg: mostra "O check pulou" com a lista e o check na linha errada; coerente com o título.

## Pontos menores (severidade baixa, não bloqueiam)
- Recomendação: thumbnail_texto no metadados.json ("O check foi para outra linha?") difere do texto da imagem ("O check pulou"). Alinhar se for publicar.
- Recomendação: cenas de código (cena 2 e 3) deixam ~60% da tela inferior vazia (composição concentrada no topo). Aceitável, mas pode ficar mais equilibrada.
- Recomendação: thumbnail com metade inferior em branco; baixa densidade visual em feed.

## Incertezas
- Não ouvi o áudio: qualidade e pronúncia da voz (termos como "id ponto self", "UUID") não confirmadas; só níveis medidos.
- Frames inspecionados por amostragem (contato a cada 2,4 s e detalhe de 3-6 s), não quadro a quadro.
- Fatos técnicos de SwiftUI: dependem de auditoria_texto.md (já aprovado); não revalidados.
- Nenhuma garantia de monetização; a decisão é do YouTube.
