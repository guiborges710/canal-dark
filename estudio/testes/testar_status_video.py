"""PROG-012: confere o status automático de cada vídeo (estudio/status_video.py) em pasta temporária; nunca toca em output/ real.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_status_video.py"""
import hashlib
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="status_video_"))
os.environ["ESTUDIO_RAIZ"] = str(TMP / "raiz")
os.environ["ESTUDIO_DADOS"] = str(TMP / "dados")
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import status_video as S  # noqa: E402

SAIDA = TMP / "raiz" / "output"
SAIDA.mkdir(parents=True)
(TMP / "dados").mkdir()
passou, falhas = 0, []


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}", flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def pasta(slug, **arqs):
    """arqs: nome_sem_ponto=conteúdo (str/bytes/dict). Ex.: roteiro_txt='oi'."""
    p = SAIDA / slug
    p.mkdir(parents=True, exist_ok=True)
    for k, v in arqs.items():
        nome = k.replace("_", ".", 1) if "_" in k else k
        if isinstance(v, dict):
            v = json.dumps(v)
        (p / nome).write_bytes(v if isinstance(v, bytes) else v.encode("utf-8"))
    return p


def fila(*slugs, bruto=None):
    (SAIDA / "fila_postagem.txt").write_text(bruto if bruto is not None else "\n".join(slugs) + "\n", encoding="utf-8")


def st(slug):
    return S.status_do_video(slug, saida=SAIDA)


def completo(slug, aud="APROVADO", **extra):
    return pasta(slug, roteiro_txt="texto", video_mp4=b"x", auditoria_md=aud, thumbnail_jpg=b"x",
                 metadados_json={"titulo": f"T {slug}"}, **extra)


def hashes():
    h = {}
    for f in sorted(TMP.rglob("*")):
        if f.is_file():
            h[str(f)] = (hashlib.sha256(f.read_bytes()).hexdigest(), f.stat().st_mtime_ns)
    return h


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    fila()
    print("[Um status por degrau]")
    pasta("a-sem", notas_md="n")
    confere(st("a-sem")["status"] == "sem_roteiro", "C1 só notas -> sem roteiro")
    pasta("a-vazio", roteiro_txt=b"", notas_md="n")
    confere(st("a-vazio")["status"] == "sem_roteiro", "C21 roteiro vazio -> sem roteiro")
    pasta("b-prod", roteiro_txt="x")
    confere(st("b-prod")["status"] == "em_producao", "C2 roteiro sem vídeo -> em produção")
    pasta("c-pronto", roteiro_txt="x", video_mp4=b"v")
    confere(st("c-pronto")["status"] == "video_pronto", "C3 vídeo sem auditoria -> vídeo pronto")
    pasta("c-zero", roteiro_txt="x", video_mp4=b"")
    r = st("c-zero")
    confere(r["status"] == "em_producao" and r["avisos"], "C22 vídeo de 0 bytes não é pronto e avisa", r)
    pasta("c-bloq", roteiro_txt="x", video_mp4=b"v", auditoria_md="BLOQUEADO")
    r = st("c-bloq")
    confere(r["status"] == "video_pronto" and any("BLOQUEADA" in a for a in r["avisos"]), "auditoria BLOQUEADA -> pronto + aviso", r)
    pasta("c-repr", roteiro_txt="x", video_mp4=b"v", auditoria_md="REPROVADO")
    confere(st("c-repr")["status"] == "video_pronto" and st("c-repr")["avisos"], "C5 REPROVADO -> vídeo pronto + aviso")
    pasta("c-semver", roteiro_txt="x", video_mp4=b"v", auditoria_md="")
    confere(st("c-semver")["status"] == "video_pronto", "C6 auditoria sem veredito -> vídeo pronto")
    pasta("c-ambos", roteiro_txt="x", video_mp4=b"v", auditoria_md="APROVADO ... REPROVADO")
    r = st("c-ambos")
    confere(any("REPROVADO" in a for a in r["avisos"]), "C23 APROVADO+REPROVADO gera aviso", r)
    completo("d-aud")
    r = st("d-aud")
    confere(r["status"] == "auditado" and r["titulo"] == "T d-aud", "C4 auditado (e traz o título)", r)
    confere("entrar em output/fila_postagem.txt" in r["falta"], "auditado diz que falta entrar na fila")
    pasta("d-min", roteiro_txt="x", video_mp4=b"v", auditoria_md="aprovado")
    confere(st("d-min")["status"] == "auditado", "C24 'aprovado' minúsculo vale (mesmo critério do run.py)")

    print("[Fila]")
    completo("e-fila")
    fila("e-fila")
    r = st("e-fila")
    confere(r["status"] == "na_fila" and r["fila_posicao"] == 1 and not r["avisos"], "C7 na fila completo", r)
    completo("e-sem-thumb")
    (SAIDA / "e-sem-thumb" / "thumbnail.jpg").unlink()
    fila("e-sem-thumb")
    r = st("e-sem-thumb")
    confere(r["status"] == "auditado" and any("thumbnail.jpg" in a for a in r["avisos"]), "na fila sem thumbnail -> auditado + aviso", r)
    pasta("e-sem-video", roteiro_txt="x")
    fila("e-sem-video")
    r = st("e-sem-video")
    confere(r["status"] == "em_producao" and any("não tem vídeo" in a for a in r["avisos"]), "C11 na fila sem vídeo -> aviso, não é na fila", r)
    pasta("e-sem-rot")
    (SAIDA / "e-sem-rot" / "notas.md").write_text("n")
    fila("e-sem-rot")
    confere(st("e-sem-rot")["status"] == "sem_roteiro", "na fila sem vídeo nem roteiro -> sem roteiro")
    pasta("e-sem-aud", roteiro_txt="x", video_mp4=b"v")
    fila("e-sem-aud")
    r = st("e-sem-aud")
    confere(r["status"] == "video_pronto" and any("auditoria APROVADA" in a for a in r["avisos"]), "na fila sem auditoria -> vídeo pronto + aviso", r)
    fila("e-fila", "fantasma")
    t = S.todos(SAIDA)
    confere(t["fila_orfaos"] == ["fantasma"], "C12 slug da fila sem pasta vai para fila_orfaos", t["fila_orfaos"])
    confere("fantasma" not in [v["slug"] for v in t["videos"]], "órfão não vira vídeo")
    fila(bruto="  e-fila \n\n# comentario\ne-fila\n\ne-sem-aud\n")
    confere(S.ler_fila(SAIDA) == ["e-fila", "e-sem-aud"], "C26 fila: espaços, vazias, comentário e duplicata", S.ler_fila(SAIDA))
    fila(bruto="")
    confere(S.ler_fila(SAIDA) == [], "fila vazia")

    print("[Publicação]")
    completo("f-priv", upload_json={"video_id": "abc", "url": "https://y/abc", "privacy": "private"})
    fila("f-priv")
    r = st("f-priv")
    confere(r["status"] == "publicado_privado" and r["publicado"]["url"] == "https://y/abc", "C8 upload.json private -> publicado (privado), mesmo na fila", r)
    pasta("f-pubjson", roteiro_txt="x", video_mp4=b"v", publicado_json={"privacidade": "private", "url": "u"})
    confere(st("f-pubjson")["status"] == "publicado_privado", "publicado.json -> publicado (privado)")
    completo("f-vazio", upload_json={})
    r = st("f-vazio")
    confere(r["status"] == "publicado_privado" and r["avisos"], "upload.json {} -> privado com aviso", r)
    completo("f-ruim", upload_json=b"{nao e json")
    r = st("f-ruim")
    confere(r["status"] == "publicado_privado" and r["avisos"], "C25 upload.json inválido -> sem exceção, privado, aviso", r)
    completo("f-pub", upload_json={"privacy": "public", "url": "u"})
    confere(st("f-pub")["status"] == "publico", "privacy public -> público")
    completo("f-marca", upload_json={"privacy": "private"}, publico_json={})
    confere(st("f-marca")["status"] == "publico", "C10 publico.json (marcação do Guilherme) -> público")
    pasta("f-semvideo", upload_json={"privacy": "private"})
    r = st("f-semvideo")
    confere(r["status"] == "publicado_privado" and any("não há video.mp4" in a for a in r["avisos"]), "C12 publicado sem vídeo -> aviso", r)
    pasta("f-acentoç", roteiro_txt="x")
    confere(st("f-acentoç")["status"] == "em_producao", "C27 slug com acento")

    print("[Muda sozinho]")
    pasta("g-vivo", roteiro_txt="x")
    s1 = st("g-vivo")["status"]
    (SAIDA / "g-vivo" / "video.mp4").write_bytes(b"v")
    s2 = st("g-vivo")["status"]
    (SAIDA / "g-vivo" / "auditoria.md").write_text("APROVADO")
    s3 = st("g-vivo")["status"]
    confere((s1, s2, s3) == ("em_producao", "video_pronto", "auditado"), "C14 status acompanha os arquivos", (s1, s2, s3))
    ok = {v["status"] for v in S.todos(SAIDA)["videos"]} <= set(S.STATUS)
    confere(ok, "C15 todo status pertence ao conjunto dos 7")

    print("[Próximo pronto]")
    for d in SAIDA.iterdir():
        if d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()
    completo("h-1")
    pasta("h-2", roteiro_txt="x", video_mp4=b"v")
    completo("h-3")
    fila("h-2", "h-3")
    pp = S.todos(SAIDA)["proximo_pronto"]
    confere(pp["sim"] and pp["slug"] == "h-3" and "h-2" in pp["motivo"], "primeiro não pronto, segundo pronto -> devolve o segundo e cita o bloqueio", pp)
    fila("h-2")
    pp = S.todos(SAIDA)["proximo_pronto"]
    confere(not pp["sim"] and pp["slug"] is None and "h-2" in pp["motivo"], "nenhum pronto -> não, com motivo", pp)
    fila(bruto="")
    pp = S.todos(SAIDA)["proximo_pronto"]
    confere(not pp["sim"] and "vazia" in pp["motivo"], "C17 fila vazia -> não, com texto", pp)
    fila("h-1", "h-3")
    pp = S.todos(SAIDA)["proximo_pronto"]
    confere(pp["sim"] and pp["slug"] == "h-1", "C16 primeiro da fila pronto -> sim", pp)
    (SAIDA / "nada").mkdir()
    confere("nada" not in [v["slug"] for v in S.todos(SAIDA)["videos"]], "pasta sem arquivo de produção é ignorada")

    print("[Paridade com postar_pendentes]")
    try:
        import postar_pendentes as PP
    except ImportError as e:
        PP = None
        confere(False, "importar postar_pendentes", e)
    if PP:
        pasta("p-ok", roteiro_txt="x", video_mp4=b"v", auditoria_md="APROVADO", thumbnail_jpg=b"x", metadados_json={})
        pasta("p-sem-thumb", roteiro_txt="x", video_mp4=b"v", auditoria_md="APROVADO", metadados_json={})
        pasta("p-bloq", roteiro_txt="x", video_mp4=b"v", auditoria_md="APROVADO BLOQUEADO", thumbnail_jpg=b"x", metadados_json={})
        pasta("p-sem-aud", roteiro_txt="x", video_mp4=b"v", thumbnail_jpg=b"x", metadados_json={})
        pasta("p-enviado", roteiro_txt="x", video_mp4=b"v", auditoria_md="APROVADO", thumbnail_jpg=b"x", metadados_json={}, publicado_json={"privacidade": "private"})
        fila("p-ok", "p-sem-thumb", "p-bloq", "p-sem-aud", "p-enviado", "p-nao-existe", "p-ok", "h-1")
        velho = (PP.FILA, PP.ROOT)
        PP.ROOT, PP.FILA = TMP / "raiz", SAIDA / "fila_postagem.txt"
        try:
            esperado = [o.name for o in PP.pendentes()]
        finally:
            PP.FILA, PP.ROOT = velho
        meu = [v["slug"] for v in S.todos(SAIDA)["videos"] if v["status"] == "na_fila"]
        confere(sorted(set(esperado)) == sorted(meu), "conjunto 'na fila' == postar_pendentes.pendentes()", (esperado, meu))
        confere(sorted(set(esperado)) == ["h-1", "p-ok"], "paridade não é vazia", esperado)

    print("[Sem efeito colateral]")
    antes = hashes()
    S.todos(SAIDA)
    for s in ("h-1", "h-2", "p-ok"):
        S.status_do_video(s, saida=SAIDA)
    confere(hashes() == antes, "C18 nenhum arquivo mudou (conteúdo e data) após ler a visão")
    confere(not any((TMP / "dados").iterdir()), "nenhum arquivo/banco criado em estudio/dados")

    print("[Rota]")
    from estudio.servidor import Manipulador
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        with urllib.request.urlopen(base + "/api/videos/status") as resp:
            corpo = json.loads(resp.read().decode("utf-8"))
            confere(resp.status == 200 and "json" in resp.headers["Content-Type"], "GET /api/videos/status -> 200 JSON")
        confere(set(corpo) == {"videos", "proximo_pronto", "fila_orfaos"} and any(v["slug"] == "h-1" for v in corpo["videos"]), "rota devolve a visão da pasta temporária", list(corpo))
        try:
            urllib.request.urlopen(urllib.request.Request(base + "/api/videos/status", data=b"{}", method="POST"))
            confere(False, "POST na rota deve dar 404")
        except urllib.error.HTTPError as e:
            confere(e.code == 404, "POST na rota -> 404", e.code)
    finally:
        srv.shutdown()
    confere(hashes() == antes, "rota também não altera arquivos")

    print("[Desempenho]")
    for d in list(SAIDA.iterdir()):
        if d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()
    for i in range(100):
        completo(f"z{i:03d}")
    fila(*[f"z{i:03d}" for i in range(0, 100, 2)])
    t0 = time.perf_counter()
    r = S.todos(SAIDA)
    dt = time.perf_counter() - t0
    confere(len(r["videos"]) == 100 and dt < 0.3, f"100 pastas em {dt * 1000:.0f} ms (limite 300 ms)", dt)

    print(f"\n{passou} ok, {len(falhas)} falhas")
    for f in falhas:
        print("  -", f)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
