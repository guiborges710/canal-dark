APROVADO (com condições; nenhuma bloqueia o render). Reconferido em 2026-11-02 após o corte da linha 5 (adiamento) e o atempo de 4%: parecer segue válido.

Auditoria de TEXTO (Vini), 2026-11-02. Escopo: roteiro.txt, notas.md, angulo.md, revisao.md, metadados.json, cenas3d.json (legenda, placas, rotulos, calendario) e textos3d.json.

## Reconferência após o corte da linha 5 (adiamento) e atempo +4%
- Gancho e título seguem honestos. "A proposta existe, mas não foi aprovada" continua verdadeiro (nenhuma votação achada após 02/09/2026) e o vídeo ainda entrega a promessa: nome (Permissão para Dirigir), regras (16 a 18, cidade, adulto). Perdeu-se o "porquê/quando" da não aprovação, o que enfraquece só o contexto, não a verdade. Título e miniatura ("NÃO foi aprovada") não prometem nada além disso. Sem isca de assunto.
- O adiamento segue na descrição, com a fonte da Câmara e "Informações até 02/11/2026." (confirmado em metadados.json). Sem ocorrência de calendário/urna em cenas3d.json nem de "adiou" em textos3d.json: cenas, legendas e roteiro estão alinhados em 12 linhas.
- Comentário próprio: melhorou. A linha cortada era fato; a análise (linhas 5, 9, 10, 12 atuais) não mudou. Estimativa: cerca de 28% só de análise (antes 26%) e cerca de 41% contando o esquete (antes 38%). Ainda abaixo de 1/3 só na leitura estrita, e acima na ampla.
- Risco 1 (estado da votação) muda de forma: o roteiro agora afirma só "não foi aprovada", sem "sem data". Continua exigindo olhar a tramitação antes do publish, mas só a linha 1, a descrição e a miniatura mudariam.
- Atempo +4%: não altera texto. Só conferir na auditoria final se as legendas seguem sincronizadas e a fala compreensível (duração estimada 58,4 s, dentro de 60 s, margem curta; a duração de 2,0 s por cena em cenas3d.json é provisória e o render segue o áudio).

## Infrações (bloqueiam)
Nenhuma.

## Riscos (atenção, resolver antes do publish)
1. MÉDIO - Estado da votação. Reconferi hoje a página da comissão (Câmara): nenhuma reunião após 02/09/2026 e a notícia de 02/09 confirma "adiou para depois das eleições" e nenhuma data. Mas a página não mostra resultado e hoje já passou a eleição; o roteiro diz "sem data" corretamente, e não afirma status atual. Antes de subir, olhar a ficha de tramitação do PL 8085/2014. Se houve votação, mudam linhas 1 e 5, os metadados e a miniatura. Sugestão em metadados.json: acrescentar "Informações até 02/11/2026." na descrição.
2. MÉDIO - Regra "3+ fontes" do CLAUDE.md não é cumprida por quatro fatos: IIHS (1 fonte, mas confirmei agora que a frase "cerca de 3 vezes", 16-19 vs 20+, por milha, dados de 2022, está na página), custo R$ 3.200 (1 aberta, Senatran via Exame), pedidos/emitidas (2 fontes que repetem o mesmo dado do Ministério) e 20 para 2 horas-aula (2 confirmadas). Todos estão atribuídos no áudio e na legenda (Senatran, governo, Contran, "um instituto"/"Nos EUA"), sem afirmação de causa. Aceito como exceção registrada pelo Courtois. Se o dono exigir a regra estrita, cortar as linhas 11-12 e o "R$ 3.200" (linha 7) ou achar a 3ª fonte.
3. BAIXO - 1/3 de comentário próprio: 26% só de análise; 38% contando o esquete (linhas 2-3). A heurística do compliance pode contar só a análise. O ângulo (rótulo vs. contexto, "pedido não é carteira", contraexemplo de segurança, pergunta) é original e marcado como "Nossa leitura". Aceitável, mas margem curta; se o compliance acusar, trocar a linha 8 ou 9 por um comentário curto de análise.
4. BAIXO - Conteúdo inautêntico/repetitivo: formato novo, bonecos 3D por código e voz clonada. Risco de ser lido como produção em massa se todos os vídeos usarem o mesmo molde sem variação de roteiro. Aqui há ponto de vista próprio e fontes, o que mitiga.

## Verificações (OK)
- Título e miniatura ("Dirigir aos 16? NÃO foi aprovada"): honestos, o vídeo entrega o gancho nas linhas 3-5, sem isca de assunto.
- Desinformação: não diz que está no plano de governo (premissa falsa descartada nas notas), não cita candidato nem partido. Política eleitoral: só "depois das eleições", neutro.
- Números nas cenas batem com as notas e o áudio: 20 -> 2 h-aula, 2,3 -> 7,3 mi (jan-ago 2025 -> 2026; o rótulo traz o período), +216% / +17,1% (216% é o número da fonte), 3x vs 1x. Alturas das barras proporcionais.
- Legendas = fala (só abreviam: "16", "EUA", "20+", "Dez. de 2025").
- "Isso não prova causa" e "Nossa leitura" mantêm a opinião marcada como nossa.
- Respeito: sem vítimas ou xingamento. Menores: o jovem de 16 anos é personagem de desenho, sentado ao lado de adulto, sem incentivo a dirigir sem habilitação; o contraexemplo mostra o risco. Sem tema sensível.
- Cópia: sem trecho reaproveitado das fontes.
- Descrição: fontes listadas e aviso de animação por computador e voz gerada por IA presentes. Tags coerentes.

## Recomendações (não bloqueiam)
- No Studio, marcar "não é conteúdo para crianças" e avaliar marcar "conteúdo alterado/sintético" por causa da voz clonada, mesmo sendo a do próprio autor e desenho.
- Auditoria FINAL (pós-render): conferir que a narração diz "dezesseis", "dois vírgula três" etc. como em `fala`, que nenhuma placa estoura a tela e que a legenda destacada em vermelho não cobre os rótulos.
- Não prometer monetização; a decisão é do YouTube.

## Incertezas
- Resultado de votação depois de 02/09/2026 (não verificável na página).
- Minuta citada pela CNN na 4ª versão; o roteiro diz "na proposta", sem fixar o texto final.
- Não reabri as páginas de Exame, A Tarde, CNN, O Povo e Canaltech, só Câmara, IIHS e as notas.
