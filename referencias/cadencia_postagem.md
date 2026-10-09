# Cadência de postagem — Contexto Explica (Shorts)

> Definido em 2026-10-09 (Guilherme + **De Bruyne**), base no estudo do **Memphis**.
> Reavaliar com dados reais do YouTube Studio após ~3 semanas (semana de 2026-10-27).

## Decisões fixas
- **Cadência:** 3 shorts/semana — **terça, quinta e sábado**.
- **Janela de publicação:** 18h–20h (horário de Brasília). Conteúdo analítico pede cabeça disponível → fim de tarde/noite.
- **Duração-alvo:** 45–55s (teto dos 30–60s). Shorts 40s+ engajam ~33% mais. Diretriz para o **Neymar**.
- **Qualidade > volume:** 3/semana com ângulo próprio e 1/3 de comentário original, em vez de 1/dia com IA repetitiva (risco de autenticidade/monetização apontado pelo **Memphis**).

## Fluxo de publicação (100% automático — Guilherme não toca em nada)
1. Squad produz + **Vini** aprova (`auditoria.md` = APROVADO).
2. **Memphis** sobe cada vídeo JÁ AGENDADO via `run.py publish --publish-at "<data> <hora>"` (horário de Brasília).
   - Ex.: `python run.py publish --slug <pasta> --publish-at "2026-10-14 18:30"`
   - O vídeo sobe privado e o **YouTube torna público sozinho** na data/hora. Sem passo manual no Studio.
   - O `--publish-at` força `private` e vale só para YouTube (TikTok continua caindo nos rascunhos).
3. Guilherme só pede "quero X"; a publicação agendada acontece sozinha.

## Calendário-base (modelo semanal)
| Dia | Janela (Brasília) | Status produção | Status publicação |
|-----|-------------------|-----------------|-------------------|
| Terça   | 18h–20h | — | — |
| Quinta  | 18h–20h | — | — |
| Sábado  | 18h–20h | — | — |

Produzir os 3 da semana **com antecedência** (idealmente até segunda), subir privados, e o Guilherme programa os 3 de uma vez no Studio.

## Reavaliação (após 3 semanas)
- **Memphis** puxa YouTube Studio → "Quando seus espectadores estão no YouTube" + retenção/views nas primeiras 72h.
- Recalibrar dias e horários com dado REAL do nosso público (vale mais que qualquer blog).
- Só subir para 4/semana ou 1/dia depois que cada vídeo estabilizar em views consistentes.

## O que NÃO levar a sério
- "Terça/sábado 16h é mágico" (Adobe): os próprios dados mostraram posts fora do pico rendendo mais → correlação fraca. Não otimizar grade por isso.
