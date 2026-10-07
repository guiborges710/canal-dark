# Gerar SHORT (Análise de Comportamento Social)

**Use este prompt para gerar um SHORT completo do canal.**

---

## Etapa 1: Roteiro
@neymar-roteirista Escreva o roteiro narrado para o SHORT sobre "{TEMA}".

**Contexto:**
- Nicho: Análise de Comportamento Social
- Assinatura do canal: em output/messi_assinatura_canal.md (tese: "Geração é rótulo; contexto é explicação")
- Notas com fontes: output/{SLUG}/notas.md
- Tema: {TEMA}
- Ângulo: {ANGULO_PROPOSTO}
- **Formato SHORT: 30-60 segundos**
- Estrutura: gancho (3s) → insight único (10-15s) → contraexemplo (10-15s) → pergunta de volta (5-10s)
- Pelo menos 1/3 de comentário original, não só resumir fontes
- Salve em output/{SLUG}/roteiro.md

---

## Etapa 2: Revisão de Fatos
@courtois-revisor-fatos Revise o roteiro SHORT contra as notas. Confira fatos, percentuais, links. Marque qualquer imprecisão.
- Arquivo: output/{SLUG}/roteiro.md
- Nota: é SHORT (60s), então seja conciso nas observações

---

## Etapa 3: Cenas e Prompts de Imagem
@olise-diretor-arte Divida o roteiro SHORT em 3-5 cenas e crie prompts fotorrealistas para cada uma.
- Formato: SHORT (60 segundos), então poucas cenas mas impactantes
- Estilo: fotorrealista, consistente com o canal
- Salve em output/{SLUG}/cenas.md

---

## Etapa 4: Gerar Vídeo
```
python run.py video --topic "{TEMA}" --format shorts
```
(Cada etapa guarda resultado em output/{SLUG}/ e pula o que já existe)

---

## Etapa 5: Metadados (Short)
@mbappe-editor-metadados Crie título, descrição (com CTA), tags e prompt da miniatura para o SHORT.
- SHORT title: max 60 caracteres, impactante
- Descrição: 2-3 linhas com CTA (link canal, inscreva-se, etc)
- Tags: 5-8 tags relevantes
- Miniatura: prompt breve (será usada também para analytics)
- Salve em output/{SLUG}/metadados.md

---

## Etapa 6: Auditoria YouTube
@vini-auditor-conformidade Audite o SHORT contra políticas de monetização do YouTube. Aprove ou liste pendências.
- Foco: conteúdo pode ser monetizado? Tem warnings?
- Marque se conteúdo sintético (IA) precisa ser marcado
- Arquivo: output/{SLUG}/auditoria.md

---

## Como usar:
1. Substitua `{TEMA}`, `{SLUG}`, `{ANGULO_PROPOSTO}` pelos valores corretos
2. Cole cada etapa sequencialmente
3. Aguarde cada agente terminar antes de mandar a próxima
4. Após etapa 6, arquivo está pronto para upload manual no YouTube

**Exemplo com tema real:**
- TEMA: "Quem lucra com polarização Gen Z vs boomers"
- SLUG: polarizacao-genz-boomers
- ANGULO_PROPOSTO: "Efeito colateral, não conspiração. Plataformas, mídia e consultoria ganham com conflito geracional."
