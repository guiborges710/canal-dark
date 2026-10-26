# Canal dark — pipeline de Shorts em animação

Para cada Short, o pipeline entrega uma pasta `output/<slug>/` com `video.mp4`, `thumbnail.jpg`,
`PUBLICAR.txt` (título, descrição e tags prontos), `CONFORMIDADE.md` e `custo.json`. **O upload é manual**
(ou `python run.py publish`, que sobe como privado).

O vídeo é uma **animação vetorial feita por código**: cartões de texto, barras que crescem e pergunta de volta,
com efeitos sonoros gerados por código. Não há narração, não há imagens de IA e não há fotos de terceiros.

```
tema → pesquisa (squad + busca web) → ângulo → texto do vídeo → cenas animadas (cenas.json)
     → render (Node + Chrome local, motor em render/) → sons por código (media/sfx.py)
     → MP4 (ffmpeg, 1080×1920, 30 fps) → metadados → CONFORMIDADE.md
```

## Como rodar

Pré-requisitos: Python 3.10+, `ffmpeg`/`ffprobe` no PATH, Node.js e o Google Chrome instalado.

```
cd render && npm install && cd ..        # uma vez só
python run.py video --topic "tema do Short"
```

- Cada etapa grava seu arquivo em `output/<slug>/` e pula o que já existe.
- `--mock` simula o texto (sem API). O render, o áudio e o MP4 são reais.
- `--allow-paid` libera a geração de texto pela API da Anthropic, usada só quando a squad não entregou o arquivo.
- Caminho do Chrome: variável `CHROME_PATH` (padrão: `C:/Program Files/Google/Chrome/Application/chrome.exe`).
- Render direto, sem o `run.py`: `cd render && node render.mjs --spec ../output/<slug>/cenas.json --out ../output/<slug>`.

## Arquivos que a squad produz (`output/<slug>/`)

| Arquivo | Quem escreve | Conteúdo |
|---|---|---|
| `notas.md` | Modric | Fatos com fonte (3+ sites) |
| `angulo.md` | Messi / Neymar | Tese, pergunta e comentário próprio |
| `roteiro.txt` | Neymar, revisado por Courtois | Texto do vídeo, sem markdown |
| `cenas.json` | Olise | Lista de cenas animadas (ver abaixo) |
| `metadados.json` | Mbappé | `titulo`, `descricao`, `tags`, `thumbnail_texto` |

### `cenas.json`

Cada cena tem `tipo` e `duracao` (segundos); o total fica entre 20 e 60 s.

| tipo | duração | o que mostra |
|---|---|---|
| `gancho` | 4 s | Dois números grandes, a explicação e a pergunta com tremor |
| `barras` | 4 a 6 s | Até 3 barras verticais que crescem, com contador e rótulo |
| `barras_horizontais` | 6 s | Até 2 barras horizontais (0 a 100), com destaque e conclusão |
| `fechamento` | 8 a 10 s | O rótulo riscado, a pergunta de volta e o convite final |

Exemplo mínimo:

```json
[
  {"tipo": "gancho", "duracao": 4, "numeros": ["3%", "15%"], "legenda": ["HOMENS SEM NENHUM", "AMIGO PRÓXIMO (EUA)"],
   "pergunta": ["A CULPA É DA", "GERAÇÃO?"]},
  {"tipo": "fechamento", "duracao": 10, "negacao": ["NÃO É: QUE GERAÇÃO", "É ESSA?"],
   "afirmacao": ["É: QUE LUGAR", "SUMIU?"], "reforco": ["E NINGUÉM COLOCOU", "OUTRO NO LUGAR?"],
   "pergunta": ["QUAL LUGAR SUMIU", "NA SUA VIDA?"]}
]
```

Regras que o `run.py` confere antes de renderizar: tipo conhecido, campos obrigatórios, linhas de texto com no máximo
26 caracteres, valores de barra dentro da escala, cores válidas. Um erro aponta a cena e o campo.

## Estrutura do código

- `run.py`: orquestra as etapas (`video`, `check`, `ideas`, `publish`).
- `render/`: motor de animação. `src/` tem cores, componentes (cartões, barras, mola, flash) e um módulo por tipo de cena;
  `render.mjs` abre o `index.html` no Chrome e grava um PNG por frame e o `eventos.json` (momentos dos sons).
- `media/motion.py`: valida o `cenas.json`, chama o motor, codifica o MP4 (H.264, yuv420p, faixa TV) e tira a miniatura de um frame.
- `media/sfx.py`: impactos, dings e whooshes gerados por código a partir do `eventos.json`. Determinístico.
- `compliance.py`: checagens antes do upload. **Não garante monetização.**
- `agents/`: fallback pago (texto pela API), usado só com `--allow-paid` ou `--mock`.
- `media/render.py`, `media/tts.py`, `media/captions.py`: são do fluxo de Reels (`reels/`), não do canal.

## Políticas que o pipeline respeita

- **Conteúdo original:** animação própria, sem foto, sem imagem de IA e sem trilha de terceiros.
- **Sem voz sintética:** o vídeo não tem narração; a descrição diz que é animação feita por computador.
- **Fontes:** a descrição precisa ter "Fontes:" com os sites usados.
- **Ângulo próprio:** `angulo.md` é obrigatório e o `compliance.py` confere se ele existe.
- **Publicação:** `python run.py publish` só roda com `auditoria.md` aprovada pelo Vini.

Revise sempre o vídeo inteiro e confira os fatos contra `notas.md` antes de subir.
