# Melhorias aplicadas ao setor de programação (2026-11-12)

Aplicadas por **Luiz Henrique**, a partir das 3 melhorias do Valverde.

## 1. Modelo inherit
`model: sonnet` virou `model: inherit` nos 9 agentes de `.claude/agents/`: `zico-po-programacao`, `xavi-scrum-master`, `ancelotti-agile-coach`, `thiago-silva-tech-lead`, `rodrygo-dev-back`, `endrick-dev-front`, `iniesta-ux-corte`, `alisson-qa`, `marquinhos-devops-release`.

## 2. Textos genéricos
- `iniesta-ux-corte.md`: "interface do Corte" virou "interface web do projeto indicado no item" (descrição e corpo; `estudio/` ficou só como exemplo).
- `endrick-dev-front.md`: idem na descrição e no corpo.
- `rodrygo-dev-back.md`: "servidor do Corte" virou "código Python do repositório" (descrição e corpo).
- `zico-po-programacao.md`: "o que trava o uso do Corte e do canal" virou "o que trava o que o Guilherme pediu".
- `thiago-silva-tech-lead.md`: o Corte agora aparece como exemplo, e o escopo é o projeto indicado no item.

Observação: o corpo do `zico-po-programacao.md` (linha 8) ainda cita "Corte em `estudio/`" como parte do código-alvo. Não estava no pedido e foi mantido; fácil de trocar se quiser.

## 3. Sincronização do Codex
**Pendente.** Esta sessão não tem ferramenta de terminal, então não consegui rodar o comando. Rodar na raiz do repositório:

```
python tools/sincronizar_codex.py
python tools/sincronizar_codex.py --verificar
```

O Codex não tem campo de modelo, então a mudança de `model` não deve alterar os `.toml`; só os textos genéricos serão espelhados.
