# Gerar um SHORT (Análise de Comportamento Social e Gerações)

Jeito recomendado (autônomo): peça ao orquestrador e ele coordena tudo e entrega o vídeo pronto.

```
@debruyne-orquestrador Produza um SHORT sobre "{TEMA}". Slug: {SLUG}. Ângulo de partida: {ANGULO_PROPOSTO}.
```

De Bruyne roda a sequência abaixo sozinho, com recursos gratuitos, sem pedir aprovação a cada passo. Use as etapas manuais só se quiser conduzir à mão.

---

## Etapas manuais (opcional)

Sempre em `output/{SLUG}/`. Contrato de arquivos que o `run.py` consome: `notas.md`, `angulo.md`, `roteiro.txt` (só narração), `cenas.json`, `metadados.json`.

1. `@modric-pesquisador-tema Pesquise "{TEMA}" com 3+ fontes e salve output/{SLUG}/notas.md`
2. `@messi-estrategista-angulo Defina o ângulo do SHORT a partir de output/{SLUG}/notas.md e salve output/{SLUG}/angulo.md`
3. `@neymar-roteirista Escreva o roteiro do SHORT (30-60s) e salve output/{SLUG}/roteiro.txt (só texto narrado)`
4. `@courtois-revisor-fatos Confira o roteiro contra as notas; corrija output/{SLUG}/roteiro.txt e liste em revisao.md`
5. `@cristiano-otimizador-viral Deixe output/{SLUG}/roteiro.txt premium; gere roteiro_notas.md e direcao_viral.md`
6. `@olise-diretor-arte Divida em 3-5 cenas lendo direcao_viral.md e salve output/{SLUG}/cenas.json`
7. `@mbappe-editor-metadados Crie output/{SLUG}/metadados.json (titulo, descricao com Fontes: e aviso sintético, tags, thumbnail_prompt, thumbnail_texto)`
8. Renderizar (gratuito): `python run.py video --topic "{TEMA}" --format shorts`
9. `@vini-auditor-conformidade Audite o SHORT e salve output/{SLUG}/auditoria.md (APROVADO/BLOQUEADO)`

Resultado em `output/{SLUG}/`: `video.mp4`, `thumbnail.jpg`, `PUBLICAR.txt`, `CONFORMIDADE.md`, `custo.json`. **Upload manual.**

> Nota: `--format shorts` é o padrão (perfil `config_shorts.yaml`, 9:16). Sem `--allow-paid`, o `run.py` usa só a voz local Kokoro e imagens sem custo.
