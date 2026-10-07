"""Verificação automática antes de publicar.

Pega problemas comuns ligados às políticas de monetização do YouTube: conteúdo inautêntico ou repetitivo,
conteúdo reutilizado, divulgação de conteúdo sintético, metadados enganosos e conteúdo sensível.

NÃO garante monetização: a decisão final é sempre do YouTube. O que isto faz é reduzir risco e lembrar
do que só uma pessoa pode confirmar.
"""
import json
import re
import time
from pathlib import Path

OK, WARN, MISS = "OK", "ATENÇÃO", "FALTA"
CLICKBAIT = ["você não vai acreditar", "chocante", "ninguém te conta", "vai te chocar", "bomba", "urgente",
             "o que não querem que você saiba", "segredo proibido"]
SENSITIVE = ["morto", "mortos", "morte", "cadáver", "cadáveres", "massacre", "corpos", "sangue", "gore", "tragédia"]
DISCLOSURE = re.compile(r"sint[eé]tic|gerad[ao]s? por (computador|ia)|inteligência artificial|\bIA\b", re.I)

LINKS = [
    ("Monetização e conteúdo inautêntico/reutilizado", "https://support.google.com/youtube/answer/1311392"),
    ("Divulgação de conteúdo alterado ou sintético", "https://support.google.com/youtube/answer/14328491"),
    ("Requisitos do Programa de Parcerias do YouTube", "https://support.google.com/youtube/answer/72851"),
    ("Conteúdo adequado para anunciantes", "https://support.google.com/youtube/answer/6162278"),
]


def _read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _words(s):
    return re.findall(r"\w+", s.lower())


def _shingles(ws, n):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def check(out, cfg):
    """Devolve (relatório em markdown, contagem por status)."""
    out = Path(out)
    cc = cfg.get("compliance", {})
    res = []

    def add(status, title, detail):
        res.append((status, title, detail))

    notes, script, angle = _read(out / "notas.md"), _read(out / "roteiro.txt"), _read(out / "angulo.md")
    publicar = _read(out / "PUBLICAR.txt")
    try:
        meta = json.loads(_read(out / "metadados.json") or "{}")
    except Exception:
        meta = {}
    try:
        scenes = json.loads(_read(out / "cenas.json") or "[]")
    except Exception:
        scenes = []

    # 1. Pesquisa e fontes
    domains = {u.split("/")[2] for u in re.findall(r"https?://[^\s)>\]]+", notes) if u.count("/") >= 2}
    if len(domains) >= 3:
        add(OK, "Pesquisa com várias fontes", f"{len(domains)} sites distintos em notas.md.")
    else:
        add(WARN, "Poucas fontes", f"Só {len(domains)} site(s) em notas.md. Use 3 ou mais e traga algo que uma busca rápida não mostra.")

    # 2. Ponto de vista próprio
    if not angle.strip():
        add(MISS, "Sem ângulo editorial (angulo.md)",
            "Sem ponto de vista próprio o vídeo vira resumo de fontes, o perfil que a política de conteúdo inautêntico mira. "
            "O pipeline gera o ângulo antes do roteiro quando há chave de API; aqui ele não existe.")
    elif len(angle.split()) < 60 or "SEM APOIO NAS NOTAS" in angle:
        add(WARN, "Ângulo editorial fraco", "Curto demais ou com itens marcados como sem apoio nas notas. Reforce a pesquisa.")
    else:
        add(OK, "Ângulo editorial definido", "Tese, pergunta e comentário próprio registrados em angulo.md.")

    # 3. Texto copiado das notas (risco de conteúdo reutilizado)
    sw, nw = _words(script), _words(notes)
    if len(sw) >= 50 and len(nw) >= 50:
        sh = _shingles(sw, 7)
        ratio = len(sh & _shingles(nw, 7)) / max(1, len(sh))
        if ratio > 0.12:
            add(WARN, "Trechos iguais às notas", f"{ratio:.0%} das sequências de 7 palavras do roteiro aparecem nas notas. "
                "Reescreva com suas palavras e some análise própria.")
        else:
            add(OK, "Texto próprio", f"Só {ratio:.0%} das sequências de 7 palavras coincidem com as notas.")
    target = int(cfg["channel"]["minutes"] * 150)
    if sw and len(sw) < target * 0.7:
        add(WARN, "Roteiro curto", f"{len(sw)} palavras para um alvo de ~{target}.")

    # 4. Repetição entre vídeos do canal e cadência
    others = [d for d in out.parent.iterdir() if d.is_dir() and d != out and not d.name.startswith("mock-")
              and (d / "roteiro.txt").exists()] if out.parent.exists() else []
    worst = 0.0
    for d in others:
        ow = _words(_read(d / "roteiro.txt"))
        if len(ow) > 50 and len(sw) > 50:
            worst = max(worst, _jaccard(sw[:25], ow[:25]), _jaccard(sw[-25:], ow[-25:]))
    if others and worst > 0.5:
        add(WARN, "Abertura ou fecho muito parecidos com outro vídeo", f"Similaridade {worst:.0%}. Vídeos em molde repetido são o alvo da política.")
    elif others:
        add(OK, "Abertura e fecho variados", f"Comparado com {len(others)} outro(s) vídeo(s) do canal.")
    recent = [d for d in others if (d / "video.mp4").exists() and time.time() - (d / "video.mp4").stat().st_mtime < 86400]
    limit = cc.get("max_videos_per_day", 2)
    if len(recent) + 1 > limit:
        add(WARN, "Cadência alta", f"{len(recent) + 1} vídeos nas últimas 24 h (limite sugerido: {limit}). "
            "Uploads em volume que uma equipe humana não faria são um sinal de produção em massa.")

    # 5. Imagens: reais, créditos e divulgação
    real = len(list((out / "images").glob("*.json")))
    n = len(scenes)
    provider = cfg["images"].get("provider")
    fallback = cfg["images"].get("fallback") if provider == "commons" else provider
    if provider == "commons" and n:
        if real / n >= 0.5:
            add(OK, "Imagens reais de arquivo", f"{real} de {n} cenas.")
        else:
            add(WARN, "Poucas imagens reais", f"{real} de {n} cenas. Melhore as buscas ou use fontes de arquivo adicionais.")
    if real:
        if "CRÉDITOS" in publicar:
            add(OK, "Créditos das imagens", "Estão no PUBLICAR.txt; cole-os no fim da descrição.")
        else:
            add(WARN, "Créditos das imagens ausentes", "Licenças como CC BY exigem atribuição.")
    if n and real < n:
        if fallback in ("fal", "cloudflare"):
            add(WARN, "Imagens geradas por IA em cenas sem registro",
                "Se parecerem reais (cena de um evento que não foi fotografado), é preciso marcar conteúdo sintético no upload. "
                "Prefira ilustração claramente estilizada.")
        else:
            add(OK, "Ilustrações estilizadas nas cenas sem registro", "Diga na descrição que são ilustrações geradas por computador.")

    # 6. Metadados
    title = meta.get("titulo", "")
    maxc = cc.get("max_title_chars", 70)
    if not title:
        add(MISS, "Título", "metadados.json sem título.")
    else:
        issues = []
        if len(title) > maxc:
            issues.append(f"{len(title)} caracteres (máx. {maxc})")
        letters = [c for c in title if c.isalpha()]
        if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:
            issues.append("quase tudo em maiúsculas")
        issues += [f'expressão de isca: "{w}"' for w in CLICKBAIT if w in title.lower()]
        add(WARN if issues else OK, "Título honesto", "; ".join(issues) if issues else "Sem isca nem exagero visível. Confirme que o vídeo entrega o que o título promete.")
    blob = (title + " " + meta.get("thumbnail_texto", "") + " " + meta.get("thumbnail_prompt", "")).lower()
    hits = [w for w in SENSITIVE if re.search(rf"\b{w}\b", blob)]
    if hits:
        add(WARN, "Conteúdo sensível no título ou na miniatura", f"Termos: {', '.join(hits)}. Tragédias podem monetizar em contexto educativo, "
            "mas miniaturas gráficas ou tom explorador limitam os anúncios.")
    desc = meta.get("descricao", "")
    add(OK if DISCLOSURE.search(desc) else WARN, "Aviso de voz/ilustração sintética na descrição",
        "Presente." if DISCLOSURE.search(desc) else "Acrescente que a narração é sintética e que há ilustrações geradas por computador.")
    add(OK if re.search(r"fontes?:", desc, re.I) else WARN, "Fontes na descrição",
        "Presente." if re.search(r"fontes?:", desc, re.I) else "Liste as fontes usadas na descrição.")

    # 7. Música
    music = cfg["render"].get("music_file")
    add(OK if music else WARN, "Trilha sonora",
        "Trilha sintética própria do projeto (sem direitos de terceiros). Se trocar, use só música com licença clara." if music
        else "Sem trilha configurada.")

    counts = {k: sum(1 for r in res if r[0] == k) for k in (OK, WARN, MISS)}
    icon = {OK: "[OK]    ", WARN: "[ATENÇÃO]", MISS: "[FALTA] "}
    lines = [f"# Conformidade com as políticas do YouTube: {out.name}", "",
             "Verificação automática de problemas comuns. **Não garante monetização**: a decisão é do YouTube, "
             "que também revisa o canal.", "",
             f"Resultado: {counts[OK]} ok, {counts[WARN]} atenção, {counts[MISS]} faltando.", "",
             "## Verificações automáticas", ""]
    for st, t, d in sorted(res, key=lambda r: {MISS: 0, WARN: 1, OK: 2}[r[0]]):
        lines.append(f"- {icon[st]} **{t}**: {d}")
    lines += ["", "## O que só você pode confirmar (marque antes de publicar)", "",
              "- [ ] Assisti ao vídeo inteiro e conferi os fatos principais contra as fontes de notas.md.",
              "- [ ] O título e a miniatura mostram o que o vídeo realmente entrega.",
              "- [ ] No upload, respondi a pergunta de conteúdo alterado ou sintético conforme a regra atual.",
              "- [ ] O vídeo tem ponto de vista e pesquisa próprios, não é só um resumo de outras fontes.",
              "- [ ] Não usei trechos de vídeo, áudio ou imagem de terceiros fora das licenças registradas.",
              "- [ ] Confirmei a licença de uso comercial da voz sintética (modelo) que estou usando.",
              "- [ ] Marquei que o vídeo NÃO é feito para crianças, se for o caso.",
              "- [ ] Mantenho uma cadência de publicação plausível para uma pessoa ou equipe pequena.",
              "", "## Requisitos do canal para monetizar (fonte oficial)", "",
              "- 1.000 inscritos e 4.000 horas de exibição pública em vídeos longos nos últimos 12 meses, "
              "ou 1.000 inscritos e 10 milhões de visualizações de Shorts em 90 dias.",
              "- Seguir as políticas de monetização, sem avisos ativos das Diretrizes da Comunidade, "
              "verificação em duas etapas e AdSense vinculado. Atingir os números não garante aprovação: o canal é revisado.",
              "", "## Páginas oficiais", ""]
    lines += [f"- {t}: {u}" for t, u in LINKS]
    return "\n".join(lines) + "\n", counts
