"""PROG-013/014: prepara vídeo e monta rodadas do aprendiz, em pasta temporária. Não chama o Claude nem a internet.

Uso: .venv\\Scripts\\python -X utf8 estudio/testes/testar_aprendiz.py
"""
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "inteligencia" / "aprendiz"))
import preparar_video as pv  # noqa: E402
import rodar  # noqa: E402

HOJE = date(2026, 11, 5)
falhas = []
total = 0


def checar(nome, ok, detalhe=""):
    global total
    total += 1
    print(f"{'ok  ' if ok else 'FALHA'} {nome}{'' if ok else f': {detalhe}'}")
    if not ok:
        falhas.append(nome)


def video_teste(destino, seg=8):
    """Duas cores (um corte no meio) com tom de áudio, sem fala."""
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "lavfi", "-i", f"color=red:s=320x568:d={seg / 2}", "-f", "lavfi", "-i", f"color=blue:s=320x568:d={seg / 2}",
                    "-f", "lavfi", "-i", f"sine=frequency=440:duration={seg}",
                    "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(destino)],
                   check=True)


def apontar_para(tmp):
    rodar.ENTRADA = tmp / "_entrada"
    rodar.TRABALHO = tmp / "_trabalho"
    rodar.FILA = tmp / "fila.md"
    rodar.ESTUDADOS = tmp / "estudados.md"
    rodar.HISTORICO = tmp / "historico.jsonl"
    rodar.LISTAS = tmp / "listas"
    rodar.PASTA = tmp
    rodar.RAIZ = tmp
    rodar.ENTRADA.mkdir()


def escrever_fila(*ids):
    linhas = ["# Fila", "", "| ordem | id | link | canal | nicho | o que aprender | fonte |", "|---|---|---|---|---|---|---|"]
    linhas += [f"| {n} | {i} | https://exemplo/{i} | Canal {i} | nicho | gancho | busca |" for n, i in enumerate(ids, 1)]
    rodar.FILA.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def falso_ok(textos_pedidos, custo=0.12):
    """Faz o papel do Busquets: grava o relatório no caminho que o pedido indica."""
    def chamar(chave, pedido, teto):
        textos_pedidos.append(pedido)
        caminho = rodar.RAIZ / re.search(r"relatório em `([^`]+)`", pedido).group(1)
        ids = re.findall(r"^- id `([^`]+)`", pedido, re.M)
        caminho.write_text("\n".join(f"## Vídeo: {i}\n- Nível de acesso: teste" for i in ids), encoding="utf-8")
        return custo, "feito", False
    return chamar


def nao_chamar(*_):
    raise AssertionError("o Claude não devia ter sido chamado")


with tempfile.TemporaryDirectory() as t:
    tmp = Path(t)
    video = tmp / "v.mp4"
    video_teste(video)

    # --- escolha de quadros ---
    tempos = pv.escolher_tempos(40.0, [5.0, 12.0, 20.0, 30.0])
    motivos = [m for _, m in tempos]
    checar("quadros: tem gancho, virada, intervalo e final", {"gancho", "virada (corte)", "intervalo", "final"} <= set(motivos), motivos)
    checar("quadros: nunca passa do limite", len(tempos) <= pv.MAX_QUADROS, len(tempos))
    checar("quadros: em ordem de tempo", tempos == sorted(tempos))
    checar("quadros: nenhum depois do fim", all(t_ <= 40.0 for t_, _ in tempos))
    curto = pv.escolher_tempos(1.0, [])
    checar("quadros: vídeo de 1 s ainda rende quadro", len(curto) >= 1 and all(0 <= t_ <= 1.0 for t_, _ in curto), curto)
    checar("quadros: virada não duplica gancho", all(t_ > pv.GANCHO[-1] for t_, m in pv.escolher_tempos(40.0, [1.0, 2.0]) if m == "virada (corte)"))

    # --- preparo real, com o Whisper trocado por fala conhecida ---
    original_transcrever = pv.transcrever
    pv.transcrever = lambda arq, dest: ((dest / "transcricao.txt").write_text("[00:01] oi", encoding="utf-8"), True, None)[1:]
    destino = tmp / "prep"
    m = pv.preparar(video, destino)
    checar("preparo: grava manifesto", (destino / "manifesto.json").exists())
    checar("preparo: quadros existem", m["quadros"] and all((destino / q["arquivo"]).exists() for q in m["quadros"]), m["quadros"])
    checar("preparo: duração certa", abs(m["duracao_seg"] - 8) < 0.5, m["duracao_seg"])
    checar("preparo: acha o corte do meio", m["cortes_detectados"] >= 1, m["cortes_detectados"])
    checar("preparo: nível completo com fala", m["nivel_acesso"] == pv.NIVEL_COMPLETO, m["nivel_acesso"])
    checar("preparo: refazer não duplica quadros", len(list(destino.glob("q*.jpg"))) == len(pv.preparar(video, destino)["quadros"]))
    pv.transcrever = lambda arq, dest: (False, "nenhuma fala reconhecida")
    m2 = pv.preparar(video, tmp / "prep2")
    checar("preparo: sem fala fica como só quadros, com aviso", m2["nivel_acesso"] == pv.NIVEL_SEM_FALA and m2["avisos"], m2)
    pv.transcrever = original_transcrever

    # --- arquivo ruim ---
    ruim = tmp / "ruim.mp4"
    ruim.write_bytes(b"isto nao e video")
    for nome, arq in (("corrompido", ruim), ("inexistente", tmp / "nada.mp4")):
        try:
            pv.preparar(arq, tmp / f"prep_{nome}")
            checar(f"preparo: arquivo {nome} avisa", False, "não levantou erro")
        except pv.ErroPreparo:
            checar(f"preparo: arquivo {nome} avisa", True)

    # --- corte discreto: mesmo fundo claro, só o desenho muda (é o nosso sketch; o limiar antigo não via nada)
    discreto = tmp / "discreto.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "lavfi", "-i", "color=0xF5F0E0:s=320x568:d=2,drawbox=x=40:y=60:w=120:h=120:color=black:t=fill",
                    "-f", "lavfi", "-i", "color=0xF5F0E0:s=320x568:d=2,drawbox=x=160:y=380:w=120:h=120:color=black:t=fill",
                    "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(discreto)], check=True)
    cortes = pv.achar_cortes(discreto)
    checar("cortes: vê corte com o mesmo fundo", len(cortes) == 1, cortes)

    # --- transcrição, com vídeo sem fala de verdade (sem carregar o Whisper real) ---
    sem_audio = tmp / "mudo.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=red:s=64x64:d=1", str(sem_audio)], check=True)
    fala, aviso = pv.transcrever(sem_audio, tmp)
    checar("fala: vídeo sem áudio avisa e não quebra", fala is False and "áudio" in aviso, aviso)

pv.preparar_original = pv.preparar
pv.preparar = lambda arq, dest: {"nivel_acesso": pv.NIVEL_COMPLETO} if b"isto" not in Path(arq).read_bytes() else (_ for _ in ()).throw(pv.ErroPreparo("corrompido"))


def novo_cenario():
    t = tempfile.TemporaryDirectory()
    apontar_para(Path(t.name))
    return t


# --- rodada sem nenhum arquivo: custo zero ---
with novo_cenario() as t:
    escrever_fila("aaa", "bbb")
    rodar.rodar_aprendiz(hoje=HOJE, chamar=nao_chamar)
    rel = Path(t) / "2026-11-05" / "rodada-1.md"
    texto = rel.read_text(encoding="utf-8") if rel.exists() else ""
    checar("sem arquivo: não chama o Claude e grava relatório", rel.exists())
    checar("sem arquivo: marca não assistido e diz onde colocar", "não assistido" in texto and "_entrada/aaa.mp4" in texto, texto)
    checar("sem arquivo: não pede senha, cookie ou login", "nada de senha, cookie ou login" in texto, texto)
    checar("sem arquivo: registra custo zero", json.loads(rodar.HISTORICO.read_text(encoding="utf-8").splitlines()[0])["custo_usd"] == 0)
    rodar.rodar_aprendiz(hoje=HOJE, chamar=nao_chamar)
    checar("segunda rodada não sobrescreve a primeira", (Path(t) / "2026-11-05" / "rodada-2.md").exists())

# --- fila vazia ---
with novo_cenario() as t:
    escrever_fila()
    rodar.rodar_aprendiz(hoje=HOJE, chamar=nao_chamar)
    checar("fila vazia: relatório diz que não há nada", "fila está vazia" in (Path(t) / "2026-11-05" / "rodada-1.md").read_text(encoding="utf-8"))

# --- mistura: arquivo e aguardando, limite por rodada, sem repetir ---
with novo_cenario() as t:
    escrever_fila("a1", "a2", "a3", "a4", "semarquivo")
    for i in ("a1", "a2", "a3", "a4", "Avulso Novo"):
        (rodar.ENTRADA / f"{i}.mp4").write_bytes(b"video")
    (rodar.ENTRADA / "LEIA-ME.txt").write_text("x", encoding="utf-8")
    pedidos = []
    rodar.rodar_aprendiz(hoje=HOJE, chamar=falso_ok(pedidos))
    ids = re.findall(r"^- id `([^`]+)`", pedidos[0], re.M)
    checar("limite: no máximo 3 vídeos por rodada", ids == ["a1", "a2", "a3"], ids)
    checar("aguardando vai no pedido, marcado como não assistido", "semarquivo" in pedidos[0] and "não assistido" in pedidos[0], pedidos[0])
    checar("txt de leia-me não vira vídeo", "LEIA-ME" not in pedidos[0])
    checar("estudados marcados", rodar.ids_estudados() == {"a1", "a2", "a3"}, rodar.ids_estudados())
    pedidos.clear()
    rodar.rodar_aprendiz(hoje=HOJE, chamar=falso_ok(pedidos))
    ids = re.findall(r"^- id `([^`]+)`", pedidos[0], re.M)
    checar("não repete; arquivo fora da fila também é estudado", ids == ["a4", "Avulso-Novo"], ids)
    checar("arquivo fora da fila leva link não informado", "link não informado" in pedidos[0], pedidos[0])

# --- arquivo corrompido não derruba os outros ---
with novo_cenario() as t:
    escrever_fila("bom", "ruim")
    (rodar.ENTRADA / "bom.mp4").write_bytes(b"video")
    (rodar.ENTRADA / "ruim.mp4").write_bytes(b"isto")
    pedidos = []
    rodar.rodar_aprendiz(hoje=HOJE, chamar=falso_ok(pedidos))
    checar("corrompido: o bom segue, o ruim vira não assistido", re.findall(r"^- id `([^`]+)`", pedidos[0], re.M) == ["bom"] and "ruim" in pedidos[0] and "corrompido" in pedidos[0], pedidos[0])
    checar("corrompido: não fica como estudado", rodar.ids_estudados() == {"bom"}, rodar.ids_estudados())

# --- só corrompido: falha legível, sem Claude ---
with novo_cenario() as t:
    escrever_fila("ruim")
    (rodar.ENTRADA / "ruim.mp4").write_bytes(b"isto")
    rodar.rodar_aprendiz(hoje=HOJE, chamar=nao_chamar)
    texto = (Path(t) / "2026-11-05" / "rodada-1.md").read_text(encoding="utf-8")
    checar("só corrompido: relatório de falha legível", "corrompido" in texto and "não assistido" in texto, texto)

# --- teto da execução e falha do Claude ---
with novo_cenario() as t:
    escrever_fila("x1")
    (rodar.ENTRADA / "x1.mp4").write_bytes(b"video")
    codigo = rodar.rodar_aprendiz(hoje=HOJE, chamar=lambda *a: (0.31, "parou ao atingir o teto de US$ 0.30 desta execução", True))
    texto = (Path(t) / "2026-11-05" / "rodada-1.md").read_text(encoding="utf-8")
    checar("teto: relatório diz que parou no teto", "teto" in texto, texto)
    checar("teto: vídeo não fica como estudado", rodar.ids_estudados() == set(), rodar.ids_estudados())
    checar("teto: sai com erro", codigo == 1, codigo)
    checar("teto: custo registrado", json.loads(rodar.HISTORICO.read_text(encoding="utf-8").splitlines()[-1])["custo_usd"] == 0.31)
    rodar.rodar_aprendiz(hoje=HOJE, chamar=falso_ok([]))
    checar("depois da falha: a próxima rodada estuda normalmente", rodar.ids_estudados() == {"x1"}, rodar.ids_estudados())

# --- agente termina sem relatório ---
with novo_cenario() as t:
    escrever_fila("x1")
    (rodar.ENTRADA / "x1.mp4").write_bytes(b"video")
    codigo = rodar.rodar_aprendiz(hoje=HOJE, chamar=lambda *a: (0.05, "pronto", False))
    checar("sem relatório do agente: vira falha", codigo == 1 and "sem gravar" in (Path(t) / "2026-11-05" / "rodada-1.md").read_text(encoding="utf-8"))

# --- teto do dia ---
with novo_cenario() as t:
    escrever_fila("x1")
    (rodar.ENTRADA / "x1.mp4").write_bytes(b"video")
    rodar.HISTORICO.write_text(json.dumps({"quando": "2026-11-05T09:00:00", "custo_usd": rodar.TETO_DIA}) + "\n" + json.dumps({"quando": "2026-11-04T09:00:00", "custo_usd": 9}) + "\n", encoding="utf-8")
    rodar.rodar_aprendiz(hoje=HOJE, chamar=nao_chamar)
    rodar.rodar_curador(hoje=HOJE, chamar=nao_chamar)
    checar("teto do dia: não chama ninguém", not (Path(t) / "2026-11-05").exists())
    checar("teto do dia: outro dia não conta", abs(rodar.gasto_hoje(date(2026, 11, 3))) == 0)

# --- simular não escreve ---
with novo_cenario() as t:
    escrever_fila("x1")
    rodar.rodar_aprendiz(simular=True, hoje=HOJE, chamar=nao_chamar)
    rodar.rodar_curador(simular=True, hoje=HOJE, chamar=nao_chamar)
    checar("simular: não escreve nada", not (Path(t) / "2026-11-05").exists() and not rodar.HISTORICO.exists() and not rodar.LISTAS.exists())

# --- curador ---
with novo_cenario() as t:
    def curador_ok(chave, pedido, teto):
        (rodar.RAIZ / re.search(r"lista em `([^`]+)`", pedido).group(1)).write_text("# lista", encoding="utf-8")
        return 0.1, "ok", False
    checar("curador: sucesso", rodar.rodar_curador(hoje=HOJE, chamar=curador_ok) == 0 and (rodar.LISTAS / "2026-11-05.md").exists())
    rodar.rodar_curador(hoje=HOJE, chamar=curador_ok)
    checar("curador: segunda entrega não sobrescreve", (rodar.LISTAS / "2026-11-05-2.md").exists())
    codigo = rodar.rodar_curador(hoje=HOJE, chamar=lambda *a: (0.2, "parou ao atingir o teto", True))
    texto = (rodar.LISTAS / "2026-11-05-3.md").read_text(encoding="utf-8")
    checar("curador: falha registra texto claro, sem inventar", codigo == 1 and "Sem lista" in texto and "teto" in texto, texto)

# --- proteções do repositório e dos agentes ---
gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
checar("git ignora vídeos e quadros", "inteligencia/aprendiz/_entrada/" in gitignore and "inteligencia/aprendiz/_trabalho/" in gitignore)
fonte = (RAIZ / "inteligencia" / "aprendiz" / "rodar.py").read_text(encoding="utf-8") + (RAIZ / "inteligencia" / "aprendiz" / "preparar_video.py").read_text(encoding="utf-8")
checar("scripts não baixam vídeo", not re.search(r"yt.?dlp|urllib|requests\.", fonte))
for agente in ("busquets-aprendiz-canais-dark", "xabi-alonso-curador-referencias"):
    txt = (RAIZ / ".claude" / "agents" / f"{agente}.md").read_text(encoding="utf-8")
    cabecalho = txt.split("---")[1]
    checar(f"{agente}: existe, sem Bash", f"name: {agente}" in cabecalho and "Bash" not in cabecalho)
    checar(f"{agente}: limites escritos", all(p in txt.lower() for p in ("não publica", "senha, token ou cookie")), agente)

print(f"\n{total - len(falhas)}/{total} passaram.")
if falhas:
    print("Falharam:", *falhas, sep="\n - ")
sys.exit(1 if falhas else 0)
