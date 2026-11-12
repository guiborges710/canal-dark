# Auditoria de TEXTO (antes do render) - jovens-trocam-de-emprego

**APROVADO**

Aprovação congela `roteiro.txt` (150 palavras). Não reescrever. Metadados têm 2 ajustes recomendados abaixo; podem ser corrigidos agora, antes do render, sem bloquear.

## Verificado
- Falas de `cenas.json` (8 cenas) concatenadas = `roteiro.txt`, idênticas após normalizar espaços. Rótulos coerentes com as notas.
- Fatos do roteiro x notas: "mais de cinco empregos" = 5,6 aos 18-24 (BLS NLSY79); "quase três anos" = 2,8 em 2022 vs 3,0 em 1983 (Pew 2022); "na média, não em todos" cobre a ressalva do Pew 2017; Brasil com "não achei essa comparação" e "o que aparece", sem afirmar "sempre foi igual". EUA dito explicitamente.
- Números: 2 (cinco empregos, quase três anos). Sem gráfico. Gancho sem estatística, situação antes do dado. Tipo "Cena do dia a dia".
- Comentário próprio: reenquadramento, ressalva do Brasil, tese e volta à cena somam bem mais de 1/3. Opinião marcada ("Na nossa leitura"). Sem trecho copiado das fontes.
- Metadados: aviso de animação por computador presente; 5 fontes listadas; título e thumbnail_texto honestos e sobre o tema do vídeo; tags pertinentes. Sem imagem de terceiros ou IA. Tema sem conteúdo sensível.
- Tema não repete nenhuma outra pasta em output/ (busca por "troca de emprego/rotatividade" só achou este slug).

## Observações e riscos
1. (Metadados, recomendação, severidade baixa-média) A descrição diz "a troca de emprego cai com a idade, em qualquer geração". A fonte (NLSY79) é de uma única coorte, e as notas dizem que isso sozinho não separa idade de geração. Sugestão: "nos EUA, a geração dos pais e avós também trocou muito aos 18-24 anos e depois a troca caiu com a idade".
2. (Metadados, recomendação, baixa) "No Brasil, as causas são de mercado" é mais forte que o vídeo e que as notas (fonte de 2011 mais reportagem secundária de 2026). Sugestão: "No Brasil, as fontes apontam causas de mercado...". Também pode citar a ressalva "dados dos EUA; não há série brasileira por geração".
3. (Risco, atenção) Fonte 5 (O Imparcial) é secundária e o estudo original não foi conferido; a descrição já a nomeia como "sobre estudo Seet/MTE". Manter assim. O vídeo não usa os percentuais dessa fonte.
4. (Recomendação) A narração usa voz clonada do próprio Guilherme. Na publicação, conferir a pergunta de "conteúdo alterado ou sintético" do YouTube Studio e responder conforme a regra vigente (não confirmei a regra atual nesta auditoria).
5. (Nota técnica) Em cena_5 o som `impact` está em t=8.0 e a duração declarada é 5 s; em cena_6 t=4.8 com 4 s. Se a duração final seguir o áudio da fala, não há problema; confirmar no render que os sons caem dentro da cena.
6. `direcao_viral.md` traz uma narração em versão antiga (diferente do roteiro). Não vale como roteiro; vale `roteiro.txt`.

## Incertezas
- Não verifiquei o `sketch_cenas.py` nem a `previa.jpg` (fora do escopo do modo texto). Os textos dos desenhos devem seguir os rótulos de `cenas.json`.
- Não consultei regras atuais do YouTube; nada aqui promete monetização.
