"""Status automático de cada vídeo (PROG-012). Só lê arquivos de output/<slug>/ e a fila; não grava, não usa rede, não usa banco.
A regra única é a tabela D-001 de programacao/tecnico/decisoes.md; nenhum outro código recalcula status.

Uso no terminal: .venv\\Scripts\\python -m estudio.status_video"""
import json
import os
from datetime import datetime
from pathlib import Path

from . import config
from . import materiais as M

STATUS = {
    "sem_roteiro": "Sem roteiro",
    "em_producao": "Em produção",
    "video_pronto": "Vídeo pronto",
    "auditado": "Auditado",
    "na_fila": "Na fila de postagem",
    "publicado_privado": "Publicado (privado)",
    "publico": "Público",
}


def _saida(saida):
    return Path(saida) if saida else config.SAIDA


def _indice(p):
    """{nome: (tamanho, mtime)} dos arquivos do topo da pasta, numa só varredura (no Windows o DirEntry já traz o stat)."""
    try:
        with os.scandir(p) as it:
            out = {}
            for e in it:
                if e.is_file():
                    st = e.stat()
                    out[e.name] = (st.st_size, st.st_mtime)
            return out
    except OSError:
        return {}


def _json(p, nome, ind):
    """(existe, dados|None). Dados None com existe True = JSON inválido."""
    f = p / nome
    if nome not in ind:
        return False, None
    try:
        return True, json.loads(f.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return True, None


def ler_fila(saida=None):
    """Mesma leitura de postar_pendentes.py: strip, ignora vazio e '#', sem duplicata (vale a primeira)."""
    f = _saida(saida) / "fila_postagem.txt"
    try:
        linhas = f.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return []
    fila = []
    for linha in linhas:
        slug = linha.strip()
        if slug and not slug.startswith("#") and slug not in fila:
            fila.append(slug)
    return fila


def status_do_video(slug, fila=None, saida=None):
    saida = _saida(saida)
    p = saida / slug
    fila = ler_fila(saida) if fila is None else fila
    avisos = []
    na_fila = slug in fila
    posicao = fila.index(slug) + 1 if na_fila else None

    ind = _indice(p)

    def _tem(_p, nome):  # existe e não está vazio (0 bytes é arquivo quebrado, não material)
        return ind.get(nome, (0, 0))[0] > 0

    video = _tem(p, "video.mp4")
    if "video.mp4" in ind and not video:
        avisos.append("O video.mp4 está vazio (0 bytes); não conta como vídeo pronto.")
    roteiro = _tem(p, "roteiro.txt")
    ok_aud = False
    aud = ""
    if "auditoria.md" in ind:
        aud = M.ler_texto(p / "auditoria.md")
        veredito = M.status_auditoria(aud)
        ok_aud = veredito == "APROVADO"
        if veredito == "BLOQUEADO":
            avisos.append("A auditoria do Vini está BLOQUEADA; o vídeo não pode ser postado.")
        elif veredito is None:
            avisos.append("A auditoria não tem veredito (nem APROVADO nem BLOQUEADO).")
        elif "REPROVADO" in aud.upper():
            avisos.append("A auditoria cita APROVADO e REPROVADO ao mesmo tempo; confira o veredito do Vini.")

    ex_up, up = _json(p, "upload.json", ind)
    ex_pub, pub = _json(p, "publicado.json", ind)
    publicado = None
    if ex_up or ex_pub:
        dados = up if isinstance(up, dict) else (pub if isinstance(pub, dict) else {})
        outro = pub if isinstance(pub, dict) else {}
        priv = dados.get("privacy") or dados.get("privacidade") or outro.get("privacidade")
        if ex_up and up is None:
            avisos.append("O upload.json está ilegível; a privacidade é desconhecida e vale como privado.")
        elif not priv:
            avisos.append("O registro de publicação não diz a privacidade; vale como privado.")
        publicado = {"url": dados.get("url") or outro.get("url"), "privacidade": priv or "desconhecida"}
    marcador_publico = "publico.json" in ind

    # tabela D-001: vale a primeira condição verdadeira
    if (publicado and publicado["privacidade"] == "public") or marcador_publico:
        st = "publico"
        if publicado is None:
            publicado = {"url": None, "privacidade": "public"}
    elif publicado:
        st = "publicado_privado"
        publicado["privacidade"] = publicado["privacidade"] if publicado["privacidade"] != "desconhecida" else "private"
    elif not video:
        st = "em_producao" if roteiro else "sem_roteiro"
    elif ok_aud and na_fila and _tem(p, "thumbnail.jpg") and _tem(p, "metadados.json"):
        st = "na_fila"
    elif ok_aud:
        st = "auditado"
    else:
        st = "video_pronto"

    falta = []
    if st in ("publico", "publicado_privado"):
        if not video:
            avisos.append("Consta como publicado, mas não há video.mp4 na pasta.")
    else:
        if na_fila and not video:
            avisos.append("Está na fila de postagem, mas não tem vídeo.")
        if na_fila and video and not ok_aud:
            avisos.append("Está na fila de postagem, mas não tem auditoria APROVADA.")
        if na_fila and ok_aud and video:
            for nome in ("thumbnail.jpg", "metadados.json"):
                if not _tem(p, nome):
                    avisos.append(f"Está na fila de postagem, mas falta o {nome}.")
        if st == "sem_roteiro":
            falta.append("roteiro.txt")
        elif st == "em_producao":
            falta.append("video.mp4")
        elif st == "video_pronto":
            falta.append("auditoria APROVADA do Vini")
        elif st == "auditado":
            falta += [n for n in ("thumbnail.jpg", "metadados.json") if not _tem(p, n)]
            if not na_fila:
                falta.append("entrar em output/fila_postagem.txt")
        elif st == "na_fila":
            falta.append("enviar (manual) e publicar no Studio")

    _, meta = _json(p, "metadados.json", ind)
    titulo = meta.get("titulo") if isinstance(meta, dict) else None
    return {"slug": slug, "titulo": titulo, "status": st, "status_texto": STATUS[st], "avisos": avisos,
            "falta": falta, "fila_posicao": posicao, "publicado": publicado,
            "atualizado_em": _atualizado(ind)}


def _atualizado(ind):
    try:
        return datetime.fromtimestamp(max(m for _, m in ind.values())).isoformat(timespec="seconds") if ind else None
    except (OSError, ValueError, OverflowError):
        return None


def todos(saida=None):
    saida = _saida(saida)
    fila = ler_fila(saida)
    videos = []
    try:
        pastas = sorted(d for d in saida.iterdir() if d.is_dir())
    except OSError:
        pastas = []
    for d in pastas:
        if M.e_producao(d):
            videos.append(status_do_video(d.name, fila, saida))
    por_slug = {v["slug"]: v for v in videos}
    orfaos = [s for s in fila if not (saida / s).is_dir()]
    proximo = {"sim": False, "slug": None, "motivo": ""}
    bloqueios = []
    for s in fila:
        v = por_slug.get(s)
        if v is None:
            bloqueios.append(f"{s}: pasta não encontrada")
        elif v["status"] == "na_fila":
            proximo = {"sim": True, "slug": s, "motivo": "Há vídeo pronto para a próxima postagem."}
            if bloqueios:
                proximo["motivo"] += " Antes dele na fila, não estão prontos: " + "; ".join(bloqueios) + "."
            break
        else:
            bloqueios.append(f"{s}: {v['status_texto'].lower()}" + (f" ({v['avisos'][0]})" if v["avisos"] else (f" (falta {', '.join(v['falta'])})" if v["falta"] else "")))
    else:
        if not fila:
            proximo["motivo"] = "A fila de postagem está vazia."
        else:
            proximo["motivo"] = "Nenhum vídeo da fila está pronto: " + "; ".join(bloqueios) + "."
    return {"videos": videos, "proximo_pronto": proximo, "fila_orfaos": orfaos}


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    r = todos()
    for v in r["videos"]:
        print(f"{v['status_texto']:<22} {v['slug']}")
        for a in v["avisos"]:
            print(f"    aviso: {a}")
    for o in r["fila_orfaos"]:
        print(f"    aviso: {o} está na fila, mas a pasta não existe")
    pp = r["proximo_pronto"]
    print(f"\nPróxima postagem pronta: {'sim' if pp['sim'] else 'não'}" + (f" ({pp['slug']})" if pp["slug"] else "") + f". {pp['motivo']}")


if __name__ == "__main__":
    main()
