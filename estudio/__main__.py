"""Inicia o Corte (a interface do estúdio):  python -m estudio [--porta 8765] [--nao-abrir] [--rede]   (ou  python -m corte)"""
import argparse
import sys
import threading
import webbrowser

from .config import PORTA, REPO

sys.path.insert(0, str(REPO))


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Corte: acompanhar, aprovar e editar as produções, e mudar quem faz o quê")
    ap.add_argument("--porta", type=int, default=PORTA)
    ap.add_argument("--nao-abrir", action="store_true", help="não abre o navegador")
    ap.add_argument("--rede", action="store_true", help="também aceita o celular e outros aparelhos do Wi-Fi de casa, com senha")
    a = ap.parse_args()
    from . import acesso
    from .servidor import servir
    url = f"http://127.0.0.1:{a.porta}/"
    print(f"Corte em {url}  (Ctrl+C encerra; trabalhos em andamento continuam e são reencontrados na próxima vez)", flush=True)
    if a.rede:
        acesso.ativar(True)
        print("\nNo celular, conectado ao mesmo Wi-Fi, abra:", flush=True)
        for ip in acesso.enderecos_da_rede():
            print(f"   http://{ip}:{a.porta}/", flush=True)
        print(f"   senha: {acesso.senha_da_rede()}", flush=True)
        print("O Windows pode perguntar se o Python pode receber conexões: permita só em rede particular.\n", flush=True)
    if not a.nao_abrir:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        servir(a.porta, a.rede)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
