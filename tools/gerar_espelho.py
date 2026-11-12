"""Gera o espelho do sistema: um HTML único, só para consulta (sem servidor nem banco).

Uso:  python tools/gerar_espelho.py   ->  espelho_sistema.html na raiz do projeto.
Rode de novo sempre que quiser atualizar. Só LÊ o projeto; não altera nada.
Fica de fora de propósito: segredos (.env, client_secret, tokens), acessos.md e
movimentos/saldos das finanças (só o README das finanças entra).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "espelho_sistema.html"
LIM_DOC = 60_000  # caracteres por documento
IGNORAR = {".venv", "node_modules", "__pycache__", ".git", "blobs", "falas", "falas_v1_65s",
           "corte_assets", "audios_previa", "jobs", "exportando", "miniaturas"}
BLOQUEADOS = {"acessos.md", ".env", "client_secret.json", "client_secret_pessoal.json",
              "movimentos.csv", "saldos.csv"}


def ler(p: Path, lim=LIM_DOC) -> str:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # noqa
        return f"(não foi possível ler: {e})"
    if len(t) > lim:
        t = t[:lim] + f"\n\n… (cortado: o arquivo tem {len(t):,} caracteres)"
    return t


def rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def doc_de(p: Path, titulo=None):
    return {"titulo": titulo or p.name, "caminho": rel(p), "data": mtime(p), "texto": ler(p)}


def docs_md(pasta: Path, recursivo=True, max_docs=150):
    """Lista de documentos .md/.txt de uma pasta."""
    if not pasta.exists():
        return []
    it = pasta.rglob("*") if recursivo else pasta.glob("*")
    out = []
    for p in sorted(it):
        if not p.is_file() or p.suffix.lower() not in (".md", ".txt"):
            continue
        if p.name in BLOQUEADOS or any(x in IGNORAR for x in p.relative_to(RAIZ).parts):
            continue
        out.append(doc_de(p, p.relative_to(pasta).as_posix()))
        if len(out) >= max_docs:
            break
    return out


SETORES = {
    "Canal dark (produção)": ["debruyne-orquestrador", "modric-pesquisador-tema", "memphis-social-media",
        "haaland-pesquisador-nicho", "messi-estrategista-angulo", "neymar-roteirista",
        "courtois-revisor-fatos", "cristiano-otimizador-viral", "raphinha-curador-componentes",
        "olise-diretor-arte", "barcola-diretor-horizontal", "mbappe-editor-metadados",
        "vini-auditor-conformidade", "sidorf-thumbnail-estrategista", "kane-narrador",
        "dembele-reels-instagram"],
    "Inteligência": ["hugo-souza-pesquisador-canais", "fagner-analista-titulos",
        "andre-carrillo-analista-thumbnails", "raniele-analista-producao",
        "yuri-alberto-analista-metricas", "vitinho-consolidador", "busquets-aprendiz-canais-dark",
        "xabi-alonso-curador-referencias", "garro-scout-tecnologia-ia"],
    "Programação": ["zico-po-programacao", "xavi-scrum-master", "ancelotti-agile-coach",
        "thiago-silva-tech-lead", "rodrygo-dev-back", "endrick-dev-front", "iniesta-ux-corte",
        "alisson-qa", "marquinhos-devops-release"],
    "Produtividade pessoal": ["ronaldo-assistente", "guardiola-po-agilista", "pedri-gestor-tarefas",
        "rodri-apontamento-horas", "kroos-acessos-seguranca", "lamine-yamal-linkedin",
        "casemiro-financeiro"],
    "Ecossistema / transversal": ["luiz-henrique-ecossistema", "valverde-engenheiro-ia"],
}
DOIS_NOMES = {"hugo-souza", "andre-carrillo", "thiago-silva", "luiz-henrique", "lamine-yamal", "xabi-alonso"}


def agentes():
    por_setor = {i: s for s, ids in SETORES.items() for i in ids}
    lista = []
    for p in sorted((RAIZ / ".claude" / "agents").glob("*.md")):
        t = ler(p, 40_000)
        fm, corpo = {}, t
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", t, re.S)
        if m:
            for ln in m.group(1).splitlines():
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            corpo = m.group(2)
        partes = p.stem.split("-")
        n = 2 if "-".join(partes[:2]) in DOIS_NOMES else 1
        lista.append({"id": p.stem, "nome": " ".join(w.capitalize() for w in partes[:n]),
                      "setor": por_setor.get(p.stem, "Outros"), "descricao": fm.get("description", ""),
                      "tools": fm.get("tools", ""), "modelo": fm.get("model", ""),
                      "prompt": corpo.strip(), "data": mtime(p)})
    return lista


def videos():
    vs = []
    for d in sorted((RAIZ / "output").iterdir()):
        if not d.is_dir():
            continue
        arqs = [f for f in d.iterdir() if f.is_file()]
        if not arqs:
            continue
        nomes = {f.name for f in arqs}
        meta = {}
        if "metadados.json" in nomes:
            try:
                meta = json.loads(ler(d / "metadados.json", 200_000))
            except Exception:
                meta = {}
        aud = ""
        if "auditoria.md" in nomes:
            a = ler(d / "auditoria.md", 6000).upper()
            aud = "APROVADO" if "APROVAD" in a and "REPROVAD" not in a[:400] else "ver auditoria"
        if "video.mp4" in nomes:
            estado = "Vídeo pronto"
        elif "cenas.json" in nomes or "cenas3d.json" in nomes:
            estado = "Cenas prontas, sem render"
        elif "roteiro.txt" in nomes:
            estado = "Só roteiro"
        else:
            estado = "Em pesquisa"
        textos = [{"titulo": n, "texto": ler(d / n, 25_000)} for n in
                  ["roteiro.txt", "angulo.md", "direcao_viral.md", "notas.md", "revisao.md",
                   "auditoria_texto.md", "auditoria.md", "CONFORMIDADE.md", "PUBLICAR.txt", "roteiro_notas.md"]
                  if n in nomes]
        vs.append({"slug": d.name, "estado": estado, "auditoria": aud,
                   "titulo": meta.get("titulo", ""), "descricao": meta.get("descricao", ""),
                   "tags": meta.get("tags", []), "thumb": meta.get("thumbnail_texto", ""),
                   "data": mtime(max(arqs, key=lambda f: f.stat().st_mtime)),
                   "arquivos": sorted((f.name, round(f.stat().st_size / 1024)) for f in arqs),
                   "textos": textos})
    return vs


PASTAS_CODIGO = [("media", "Motores de render, voz, estilos, sons"), ("estudio", "Corte: servidor e interface web"),
    ("agents", "Fallback pago de texto pela API"), ("tools", "Ferramentas de apoio"),
    ("render", "Motor de animação SVG (Node)"), ("render3d", "Render 3D"),
    ("programacao", "Setor de programação (quadro, sprints, maestro)"),
    ("inteligencia", "Setor de inteligência"), ("produtividade", "Ronaldo e produtividade"),
    ("financas", "Finanças pessoais"), ("reels", "Reels do outro Instagram"), ("tiktok", "TikTok"),
    ("componentes", "Catálogo de componentes visuais"), ("prompts", "Prompts do fluxo pago e tipos de roteiro"),
    ("thumbnails", "Miniaturas"), ("voz", "Amostra da voz"), ("music", "Músicas"),
    ("ecossistema", "Mapa do ecossistema")]


def codigo():
    out = []
    for nome, desc in PASTAS_CODIGO:
        p = RAIZ / nome
        if not p.exists():
            continue
        n = sum(1 for f in p.rglob("*") if f.is_file() and not any(x in IGNORAR for x in f.relative_to(RAIZ).parts))
        mods = []
        for f in sorted(p.glob("*.py")):
            doc = ""
            m = re.match(r'\s*(?:#.*\n)*\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', ler(f, 3000), re.S)
            if m and m.group(1).strip():
                doc = m.group(1).strip().splitlines()[0]
            mods.append({"arquivo": f.name, "doc": doc, "kb": round(f.stat().st_size / 1024)})
        out.append({"pasta": nome, "desc": desc, "arquivos": n, "modulos": mods})
    return out


def main():
    raiz_docs = [doc_de(RAIZ / n) for n in ("CLAUDE.md", "README.md", "AUDITORIA_E_ARQUITETURA.md",
                                            "output/messi_assinatura_canal.md") if (RAIZ / n).exists()]
    areas = [("Canal: regras e fluxo", raiz_docs + docs_md(RAIZ / "prompts") + docs_md(RAIZ / "componentes")),
             ("Programação", docs_md(RAIZ / "programacao")),
             ("Inteligência", docs_md(RAIZ / "inteligencia"))]
    prod = docs_md(RAIZ / "produtividade")
    for n in ("agenda.json", "lembretes.json"):
        f = RAIZ / "produtividade" / n
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            prod.append({"titulo": n, "caminho": rel(f), "data": mtime(f),
                         "texto": "```\n" + json.dumps(j, ensure_ascii=False, indent=2)[:LIM_DOC] + "\n```"})
        except Exception:
            pass
    areas += [("Ronaldo e produtividade", prod),
              ("Finanças (só README)", [d for d in docs_md(RAIZ / "financas") if d["titulo"] == "README.md"]),
              ("Ecossistema", docs_md(RAIZ / "ecossistema")),
              ("Corte (estúdio)", docs_md(RAIZ / "estudio", recursivo=False)),
              ("Reels e TikTok", docs_md(RAIZ / "reels", max_docs=30) + docs_md(RAIZ / "tiktok", max_docs=30)),
              ("Pesquisa e relatórios", docs_md(RAIZ / "research_notes", max_docs=40)
               + docs_md(RAIZ / "reports", max_docs=40) + docs_md(RAIZ / "referencias", max_docs=40)),
              ("Skills", docs_md(RAIZ / ".claude" / "skills"))]
    dados = {"gerado": datetime.now().strftime("%Y-%m-%d %H:%M"), "agentes": agentes(), "videos": videos(),
             "codigo": codigo(), "areas": [{"nome": n, "docs": d} for n, d in areas if d]}
    html = TEMPLATE.replace("__DADOS__", json.dumps(dados, ensure_ascii=False).replace("</", "<\\/"))
    SAIDA.write_text(html, encoding="utf-8")
    print(f"OK: {SAIDA} ({SAIDA.stat().st_size // 1024} KB, {len(dados['agentes'])} agentes, "
          f"{len(dados['videos'])} videos, {sum(len(a['docs']) for a in dados['areas'])} documentos)")


TEMPLATE = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Espelho do sistema</title>
<style>
:root{--bg:#0f1218;--p:#171c26;--p2:#1f2633;--t:#e6e9ef;--m:#8b94a7;--a:#5ea1ff;--ok:#4cc38a;--w:#f0b84a;--b:#2a3344}
@media (prefers-color-scheme:light){:root{--bg:#f4f5f8;--p:#fff;--p2:#eef0f5;--t:#1a1f2b;--m:#667085;--a:#1f6feb;--ok:#168a55;--w:#a26a00;--b:#d9dde6}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--t);font:15px/1.55 system-ui,Segoe UI,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--p);border-bottom:1px solid var(--b);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header h1{font-size:17px;margin:0}header small{color:var(--m)}
#q{flex:1;min-width:180px;max-width:420px;padding:8px 10px;border-radius:8px;border:1px solid var(--b);background:var(--p2);color:var(--t)}
nav{display:flex;gap:4px;flex-wrap:wrap;padding:10px 16px}
nav button{background:var(--p);color:var(--t);border:1px solid var(--b);padding:7px 12px;border-radius:8px;cursor:pointer;font:inherit}
nav button.on{background:var(--a);color:#fff;border-color:var(--a)}
main{padding:0 16px 40px;max-width:1300px;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.card{background:var(--p);border:1px solid var(--b);border-radius:10px;padding:12px 14px;cursor:pointer}
.card:hover{border-color:var(--a)}.card h3{margin:0 0 4px;font-size:15px}.card p{margin:0 0 4px;color:var(--m);font-size:13px}
.tag{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;background:var(--p2);color:var(--m);margin:2px 4px 2px 0;border:1px solid var(--b)}
.tag.ok{color:var(--ok)}.tag.w{color:var(--w)}
h2{margin:22px 0 10px;font-size:18px}
.split{display:grid;grid-template-columns:300px 1fr;gap:14px}
@media(max-width:800px){.split{grid-template-columns:1fr}}
.lista{background:var(--p);border:1px solid var(--b);border-radius:10px;max-height:75vh;overflow:auto}
.lista div{padding:8px 12px;border-bottom:1px solid var(--b);cursor:pointer;font-size:13px;word-break:break-all}
.lista div:hover,.lista div.on{background:var(--p2)}.lista small{color:var(--m);display:block}
.painel{background:var(--p);border:1px solid var(--b);border-radius:10px;padding:16px 20px;min-width:0}
.md h1,.md h2,.md h3{margin:1em 0 .4em}.md h1{font-size:20px}.md h2{font-size:17px}.md h3{font-size:15px}
.md code{background:var(--p2);padding:1px 5px;border-radius:4px;font-size:13px}
.md pre,pre{background:var(--p2);padding:10px;border-radius:8px;overflow:auto;font-size:12.5px;white-space:pre-wrap}.md pre code{padding:0}
.md table{border-collapse:collapse;display:block;overflow:auto}.md td,.md th{border:1px solid var(--b);padding:4px 9px;font-size:13px;text-align:left}
.md blockquote{border-left:3px solid var(--a);margin:8px 0;padding:2px 12px;color:var(--m)}
.md a{color:var(--a)}details{margin:8px 0}summary{cursor:pointer;color:var(--a)}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:14px 0}
.stat{background:var(--p);border:1px solid var(--b);border-radius:10px;padding:12px}.stat b{font-size:24px;display:block}.stat span{color:var(--m);font-size:12px}
table.t{width:100%;border-collapse:collapse;background:var(--p);border:1px solid var(--b)}
table.t td,table.t th{padding:6px 10px;border-bottom:1px solid var(--b);text-align:left;font-size:13px;vertical-align:top}
.vazio{color:var(--m);padding:20px}.volta{cursor:pointer;color:var(--a);margin:12px 0;display:inline-block}
.chips button{margin:2px;padding:5px 10px;border-radius:8px;border:1px solid var(--b);background:var(--p);color:var(--t);cursor:pointer}
.chips button.on{background:var(--a);color:#fff}
</style></head><body>
<header><h1>Espelho do sistema · Contexto Explica</h1><small id="ger"></small>
<input id="q" placeholder="Buscar em tudo (agentes, vídeos, documentos)…"></header>
<nav id="nav"></nav><main id="app"></main>
<script>
const D=__DADOS__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function inl(s){s=esc(s);
 s=s.replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>").replace(/(^|[^*])\*([^*\s][^*]*)\*/g,"$1<i>$2</i>")
 .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');return s}
function md(t){const L=String(t||"").replace(/\r/g,"").split("\n");let o=[],i=0;
 while(i<L.length){let l=L[i];
  if(/^```/.test(l)){let b=[];i++;while(i<L.length&&!/^```/.test(L[i]))b.push(L[i++]);i++;o.push("<pre><code>"+esc(b.join("\n"))+"</code></pre>");continue}
  let h=l.match(/^(#{1,6})\s+(.*)/);if(h){const n=Math.min(h[1].length,3);o.push(`<h${n}>${inl(h[2])}</h${n}>`);i++;continue}
  if(/^\s*\|.*\|\s*$/.test(l)&&i+1<L.length&&/^\s*\|[\s:|-]+\|\s*$/.test(L[i+1])){
   const row=r=>r.trim().replace(/^\||\|$/g,"").split("|").map(c=>c.trim());let hd=row(l);i+=2;let rs=[];
   while(i<L.length&&/^\s*\|.*\|\s*$/.test(L[i]))rs.push(row(L[i++]));
   o.push("<table><tr>"+hd.map(c=>"<th>"+inl(c)+"</th>").join("")+"</tr>"+rs.map(r=>"<tr>"+r.map(c=>"<td>"+inl(c)+"</td>").join("")+"</tr>").join("")+"</table>");continue}
  if(/^\s*([-*]|\d+\.)\s+/.test(l)){let it=[];while(i<L.length&&/^\s*([-*]|\d+\.)\s+/.test(L[i]))it.push("<li>"+inl(L[i++].replace(/^\s*([-*]|\d+\.)\s+/,""))+"</li>");o.push("<ul>"+it.join("")+"</ul>");continue}
  if(/^>/.test(l)){o.push("<blockquote>"+inl(l.replace(/^>\s?/,""))+"</blockquote>");i++;continue}
  if(!l.trim()){i++;continue}
  let p=[l];i++;while(i<L.length&&L[i].trim()&&!/^(#|```|>|\s*([-*]|\d+\.)\s|\s*\|)/.test(L[i]))p.push(L[i++]);o.push("<p>"+inl(p.join(" "))+"</p>")}
 return '<div class="md">'+o.join("")+"</div>"}

const ABAS=["Início","Agentes","Vídeos","Documentos","Código"];let aba="Início",busca="";
let selSetor="",selAg="",selVid="",selArea=0,selDoc=0;
$("#ger").textContent="gerado em "+D.gerado;
function nav(){$("#nav").innerHTML=ABAS.map(a=>`<button class="${a==aba?"on":""}" data-a="${a}">${a}</button>`).join("");
 $("#nav").querySelectorAll("button").forEach(b=>b.onclick=()=>{aba=b.dataset.a;busca="";$("#q").value="";selSetor="";selAg="";selVid="";render()})}
function render(){nav();const f={"Início":inicio,"Agentes":agentes,"Vídeos":videos,"Documentos":docs,"Código":codigo}[aba];$("#app").innerHTML="";f($("#app"))}
$("#q").oninput=e=>{busca=e.target.value.toLowerCase().trim();if(busca&&aba=="Início")aba="Agentes";selAg="";selVid="";render()};
const ok=(...x)=>!busca||x.join(" ").toLowerCase().includes(busca);

function inicio(el){const nDocs=D.areas.reduce((s,a)=>s+a.docs.length,0),prontos=D.videos.filter(v=>v.estado=="Vídeo pronto").length,aprov=D.videos.filter(v=>v.auditoria=="APROVADO").length;
 const setores=[...new Set(D.agentes.map(a=>a.setor))];
 el.innerHTML=`<div class="stats">
 <div class="stat"><b>${D.agentes.length}</b><span>agentes</span></div><div class="stat"><b>${setores.length}</b><span>setores</span></div>
 <div class="stat"><b>${D.videos.length}</b><span>pastas de vídeo</span></div><div class="stat"><b>${prontos}</b><span>vídeos prontos</span></div>
 <div class="stat"><b>${aprov}</b><span>com auditoria aprovada</span></div><div class="stat"><b>${nDocs}</b><span>documentos</span></div></div>
 <h2>Setores</h2><div class="grid">${setores.map(s=>{const l=D.agentes.filter(a=>a.setor==s);return `<div class="card" data-s="${esc(s)}"><h3>${esc(s)}</h3><p>${l.length} agentes</p><p>${esc(l.map(a=>a.nome).join(", "))}</p></div>`}).join("")}</div>
 <h2>Áreas de documentação</h2><div class="grid">${D.areas.map((a,i)=>`<div class="card" data-d="${i}"><h3>${esc(a.nome)}</h3><p>${a.docs.length} documentos</p></div>`).join("")}</div>
 <h2>Últimos vídeos mexidos</h2><div class="grid">${[...D.videos].sort((a,b)=>b.data.localeCompare(a.data)).slice(0,6).map(v=>`<div class="card" data-v="${esc(v.slug)}"><h3>${esc(v.titulo||v.slug)}</h3><p>${esc(v.estado)} · ${v.data}</p></div>`).join("")}</div>`;
 el.querySelectorAll("[data-s]").forEach(c=>c.onclick=()=>{aba="Agentes";selSetor=c.dataset.s;render()});
 el.querySelectorAll("[data-d]").forEach(c=>c.onclick=()=>{aba="Documentos";selArea=+c.dataset.d;selDoc=0;render()});
 el.querySelectorAll("[data-v]").forEach(c=>c.onclick=()=>{aba="Vídeos";selVid=c.dataset.v;render()})}

function agentes(el){const setores=[...new Set(D.agentes.map(a=>a.setor))];
 if(selAg){const a=D.agentes.find(x=>x.id==selAg);el.innerHTML=`<span class="volta">← voltar</span><div class="painel"><h2 style="margin-top:0">${esc(a.nome)} <small style="color:var(--m)">${esc(a.id)}</small></h2>
 <p>${esc(a.descricao)}</p><span class="tag">${esc(a.setor)}</span>${a.modelo?`<span class="tag">modelo: ${esc(a.modelo)}</span>`:""}<span class="tag">atualizado ${a.data}</span>
 ${a.tools?`<p><b>Ferramentas:</b> ${esc(a.tools)}</p>`:""}<h3>Instruções do agente</h3>${md(a.prompt)}</div>`;
  el.querySelector(".volta").onclick=()=>{selAg="";render()};return}
 let h="";for(const s of setores){if(selSetor&&selSetor!=s&&!busca)continue;const l=D.agentes.filter(a=>a.setor==s&&ok(a.nome,a.id,a.descricao,a.prompt));if(!l.length)continue;
  h+=`<h2>${esc(s)}</h2><div class="grid">${l.map(a=>`<div class="card" data-a="${a.id}"><h3>${esc(a.nome)}</h3><p>${esc(a.descricao.slice(0,170))}</p></div>`).join("")}</div>`}
 if(selSetor)h=`<span class="volta" id="todos">← todos os setores</span>`+h;
 el.innerHTML=h||'<div class="vazio">Nada encontrado.</div>';
 el.querySelectorAll("[data-a]").forEach(c=>c.onclick=()=>{selAg=c.dataset.a;render()});
 const t=el.querySelector("#todos");if(t)t.onclick=()=>{selSetor="";render()}}

function videos(el){
 if(selVid){const v=D.videos.find(x=>x.slug==selVid);
  el.innerHTML=`<span class="volta">← voltar</span><div class="painel"><h2 style="margin-top:0">${esc(v.titulo||v.slug)}</h2>
  <span class="tag">${esc(v.slug)}</span><span class="tag ${v.estado=="Vídeo pronto"?"ok":"w"}">${esc(v.estado)}</span>${v.auditoria?`<span class="tag ok">auditoria: ${esc(v.auditoria)}</span>`:""}<span class="tag">${v.data}</span>
  ${v.thumb?`<p><b>Texto da miniatura:</b> ${esc(v.thumb)}</p>`:""}${v.descricao?`<h3>Descrição</h3><p style="white-space:pre-wrap">${esc(v.descricao)}</p>`:""}
  ${v.tags&&v.tags.length?`<p>${v.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</p>`:""}
  ${v.textos.map(t=>`<details ${t.titulo=="roteiro.txt"?"open":""}><summary>${esc(t.titulo)}</summary>${t.titulo.endsWith(".txt")?`<pre>${esc(t.texto)}</pre>`:md(t.texto)}</details>`).join("")}
  <details><summary>Arquivos da pasta (${v.arquivos.length})</summary><table class="t">${v.arquivos.map(a=>`<tr><td>${esc(a[0])}</td><td>${a[1]} KB</td></tr>`).join("")}</table></details></div>`;
  el.querySelector(".volta").onclick=()=>{selVid="";render()};return}
 const l=D.videos.filter(v=>ok(v.slug,v.titulo,v.descricao));
 el.innerHTML=`<h2>${l.length} vídeos / temas</h2><div class="grid">${l.map(v=>`<div class="card" data-v="${esc(v.slug)}"><h3>${esc(v.titulo||v.slug)}</h3><p>${esc(v.slug)}</p>
 <span class="tag ${v.estado=="Vídeo pronto"?"ok":"w"}">${esc(v.estado)}</span>${v.auditoria=="APROVADO"?'<span class="tag ok">auditado</span>':""}<span class="tag">${v.data}</span></div>`).join("")}</div>`;
 el.querySelectorAll("[data-v]").forEach(c=>c.onclick=()=>{selVid=c.dataset.v;render()})}

function docs(el){
 if(busca){let h="";D.areas.forEach((a,ai)=>a.docs.forEach((d,di)=>{if(ok(d.titulo,d.texto))h+=`<div class="card" data-a="${ai}" data-d="${di}" style="margin-bottom:8px"><h3>${esc(d.titulo)}</h3><p>${esc(a.nome)} · ${d.data}</p></div>`}));
  el.innerHTML="<h2>Documentos encontrados</h2>"+(h||'<div class="vazio">Nada encontrado.</div>');
  el.querySelectorAll("[data-a]").forEach(c=>c.onclick=()=>{selArea=+c.dataset.a;selDoc=+c.dataset.d;busca="";$("#q").value="";render()});return}
 const a=D.areas[selArea],d=a.docs[selDoc]||a.docs[0];
 el.innerHTML=`<h2>${esc(a.nome)}</h2><div class="chips" style="margin-bottom:10px">${D.areas.map((x,i)=>`<button data-i="${i}" class="${i==selArea?"on":""}">${esc(x.nome)}</button>`).join("")}</div>
 <div class="split"><div class="lista">${a.docs.map((x,i)=>`<div class="${x===d?"on":""}" data-j="${i}">${esc(x.titulo)}<small>${x.data}</small></div>`).join("")}</div>
 <div class="painel"><small style="color:var(--m)">${esc(d.caminho)}</small>${md(d.texto)}</div></div>`;
 el.querySelectorAll("[data-i]").forEach(b=>b.onclick=()=>{selArea=+b.dataset.i;selDoc=0;render()});
 el.querySelectorAll("[data-j]").forEach(b=>b.onclick=()=>{selDoc=+b.dataset.j;render()})}

function codigo(el){
 el.innerHTML="<h2>Estrutura do projeto</h2>"+D.codigo.filter(p=>ok(p.pasta,p.desc,p.modulos.map(m=>m.arquivo+m.doc).join(" "))).map(p=>`<details ${busca?"open":""}><summary><b>${esc(p.pasta)}/</b> — ${esc(p.desc)} <span class="tag">${p.arquivos} arquivos</span></summary>
 ${p.modulos.length?`<table class="t">${p.modulos.map(m=>`<tr><td><code>${esc(m.arquivo)}</code></td><td>${esc(m.doc)}</td><td>${m.kb} KB</td></tr>`).join("")}</table>`:'<div class="vazio">Sem módulos .py na raiz da pasta.</div>'}</details>`).join("")}
render();
</script></body></html>
"""

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
