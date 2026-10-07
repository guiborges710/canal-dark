# SHORT: Quem lucra com polarização Gen Z vs boomers

**Prompt pronto para gerar o SHORT completo. Copie e cole as etapas sequencialmente.**

---

## Etapa 1: Roteiro (30-60s)
@neymar-roteirista Escreva o roteiro narrado para o SHORT "Quem lucra com polarização Gen Z vs boomers".

**Contexto:**
- Nicho: Análise de Comportamento Social
- Assinatura do canal: output/messi_assinatura_canal.md (tese: "Geração é rótulo; contexto é explicação")
- Notas com fontes: output/polarizacao-genz-boomers/notas.md
- Tema: "Quem lucra com polarização Gen Z vs boomers"
- Ângulo: Efeito colateral, não conspiração. Plataformas amplificam conteúdo emocional, mídia exagera diferenças, consultoria lucra.
- **Formato: 30-60 segundos (SHORT)**
- Estrutura obrigatória: gancho (3s) → insight único (10-15s) → contraexemplo (10-15s) → pergunta de volta (5-10s)
- Pelo menos 1/3 de comentário original (não resumo de fontes)
- Termina com pergunta provocante que engaja

Salve em `output/polarizacao-genz-boomers/roteiro.md`

---

## Etapa 2: Revisão de Fatos
@courtois-revisor-fatos Revise o roteiro SHORT contra as notas. Confira fatos, percentuais, links. Marque qualquer imprecisão.

Arquivo: `output/polarizacao-genz-boomers/roteiro.md`
Notas: `output/polarizacao-genz-boomers/notas.md`

Salve a versão revisada/corrigida em `output/polarizacao-genz-boomers/roteiro.md` (sobrescreva se necessário)

---

## Etapa 3: Cenas e Prompts de Imagem
@olise-diretor-arte Divida o roteiro SHORT em 3-5 cenas e crie um prompt fotorrealista para cada cena.

**Contexto:**
- Tema: Quem lucra com polarização geracional
- Formato: SHORT (60 segundos) — cenas rápidas, impactantes
- Estilo: Fotorrealista, consistente, sem anime/cartoon
- Visuais sugeridos: dados em gráficos, plataformas (redes sociais), pessoas de diferentes idades discutindo, consultores, jornalistas, influenciadores

Salve em `output/polarizacao-genz-boomers/cenas.md` com os prompts prontos para Flux/API

---

## Etapa 4: Gerar Vídeo
```
python run.py video --topic "Quem lucra com polarização Gen Z vs boomers" --format shorts
```

Isso vai usar:
- Roteiro de `output/polarizacao-genz-boomers/roteiro.md`
- Cenas e prompts de `output/polarizacao-genz-boomers/cenas.md`
- Notas/fontes de `output/polarizacao-genz-boomers/notas.md`
- Assinatura do canal de `output/messi_assinatura_canal.md`

Resultado: `output/polarizacao-genz-boomers/video.mp4` (pronto para metadados)

---

## Etapa 5: Metadados para Upload
@mbappe-editor-metadados Crie título, descrição, tags e prompt de miniatura para o SHORT "Quem lucra com polarização Gen Z vs boomers".

**Requisitos:**
- **Título:** max 60 caracteres, impactante, mencionável em rede (ex: "Quem lucra com a polarização?", "Gen Z vs Boomers: quem paga a conta?")
- **Descrição:** 2-3 linhas curtas. Incluir: pergunta-gancho, menção ao canal, CTA (inscreva-se, ligue notificações)
- **Tags:** 8-12 tags relevantes (polarização, gerações, eleições, Gen Z, boomers, redes sociais, etc)
- **Miniatura:** prompt visual breve e claro (será usado para thumbnail no YouTube)

Salve em `output/polarizacao-genz-boomers/metadados.md`

---

## Etapa 6: Auditoria de Conformidade YouTube
@vini-auditor-conformidade Audite o SHORT "Quem lucra com polarização Gen Z vs boomers" contra as políticas de monetização do YouTube.

**Checklist:**
- Conteúdo pode ser monetizado (dinheiro)?
- Tem warnings ou restrições de anunciante?
- Precisa marcar como conteúdo sintético (IA)?
- Foca em análise, não sensacionalismo?
- Segue tom respeitoso (sem atacar geração)?
- Tem conteúdo político? Se sim, está equilibrado?

Resultado esperado: ✅ Aprovado para upload ou ❌ Lista de ajustes necessários

Salve parecer em `output/polarizacao-genz-boomers/auditoria.md`

---

## Resultado Final

Após etapa 6, você terá:
- ✅ `video.mp4` pronto
- ✅ `metadados.md` (título, descrição, tags)
- ✅ `auditoria.md` (aprovado ✅ ou pendências)

**Próximo passo:** Upload manual no YouTube com os metadados.

---

## Como rodar:
1. Cole **Etapa 1** e aguarde neymar terminar
2. Cole **Etapa 2** e aguarde courtois terminar
3. Cole **Etapa 3** e aguarde olise terminar
4. Execute **Etapa 4** (bash/terminal)
5. Cole **Etapa 5** e aguarde mbappe terminar
6. Cole **Etapa 6** e aguarde vini terminar
7. Arquivo pronto em `output/polarizacao-genz-boomers/video.mp4`
