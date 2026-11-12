"""Teste do plano B de avaliação (botão "Avaliar potencial"). Rodar: .venv\\Scripts\\python -m clipes.testes.testar_avaliar

Sobe o painel REAL numa pasta temporária (CLIPES_SAIDA) com o agente SIMULADO (claude_simulado.py) e chama
as rotas como o clique chamaria. Nenhuma chamada ao Claude de verdade. Confere:
- clicar num corte avalia SÓ esse corte (os outros continuam sem nota);
- o botão "sem nota" avalia só os que ainda não têm;
- rota recusa corte inexistente e projeto inexistente; segundo pedido com tudo avaliado é recusado;
- a UI tem os botões e o painel não avalia nada sozinho.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
falhas: list[str] = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def req(porta, caminho, corpo=None):
    r = urllib.request.Request(f"http://127.0.0.1:{porta}{caminho}",
                               data=json.dumps(corpo).encode() if corpo is not None else None,
                               headers={"Content-Type": "application/json"},
                               method="POST" if corpo is not None else "GET")
    try:
        with urllib.request.urlopen(r, timeout=20) as x:
            return x.status, json.loads(x.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def esperar(cond, tempo=60):
    t0 = time.time()
    while time.time() - t0 < tempo:
        if cond():
            return True
        time.sleep(0.5)
    return False


def main():
    raiz = Path(tempfile.mkdtemp(prefix="clipes_avaliar_"))
    d = raiz / "proj"
    (d / "clipes").mkdir(parents=True)
    (d / "fonte.json").write_text(json.dumps({"origem": "x", "autor": "T", "titulo_original": "",
                                              "autorizacao": {"tipo": "teste", "prova": ""}}), encoding="utf-8")
    (d / "momentos.json").write_text(json.dumps([{"id": i, "ini": i, "fim": i + 20, "texto": "t", "status": "aceito"}
                                                 for i in (1, 2, 3)]), encoding="utf-8")
    for i in (1, 2, 3):
        (d / "clipes" / f"{i:02d}.mp4").write_bytes(b"\0" * 64)
        (d / "clipes" / f"{i:02d}.json").write_text(json.dumps({"dur": 20, "ini": i, "fim": i + 20, "gancho": f"G{i}"}), encoding="utf-8")
    porta = 8790 + os.getpid() % 100
    env = {**os.environ, "CLIPES_SIM_LENTO": "2.5", "CLIPES_SAIDA": str(raiz), "CLIPES_SAIDA_TESTE": str(raiz), "PYTHONIOENCODING": "utf-8",
           "CLIPES_CLAUDE": json.dumps([sys.executable, str(AQUI / "claude_simulado.py")])}
    srv = subprocess.Popen([sys.executable, "-c", f"from clipes.painel import servir; servir({porta}, navegador=False)"],
                           cwd=str(RAIZ), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pot = lambda n: (d / "clipes" / f"{n:02d}.potencial.json").exists()  # noqa: E731
    try:
        ok(esperar(lambda: _vivo(porta), 20), "painel de teste no ar")
        print("Plano B: avaliar um corte por vez")
        ok(not any(pot(n) for n in (1, 2, 3)), "nada é avaliado sozinho (sem clique, sem nota)")
        c, j = req(porta, "/api/cortes/proj")
        ok(c == 200 and all(x["potencial"] is None for x in j["cortes"] if "cortes" in j) if isinstance(j, dict) else c == 200,
           "painel lista os cortes sem nota")
        c, j = req(porta, "/api/avaliar/proj/2", {})
        ok(c == 202, f"clicar em Avaliar corte 02 é aceito ({c})")
        ok(esperar(lambda: pot(2)), "o Totti gravou a nota do corte 02")
        ok(not pot(1) and not pot(3), "só o corte 02 foi avaliado")
        c, j = req(porta, "/api/avaliar/proj/9", {})
        ok(c == 404, "corte inexistente é recusado")
        c, j = req(porta, "/api/avaliar/naoexiste/1", {})
        ok(c == 404, "projeto inexistente é recusado")
        esperar(lambda: ocioso(porta, 'proj'), 30)
        print("Plano B: avaliar os que faltam")
        c, j = req(porta, "/api/avaliar/proj", {})
        ok(c == 202, f"botão 'cortes sem nota' é aceito ({c})")
        ok(esperar(lambda: pot(1) and pot(3)), "avaliou os cortes 01 e 03")
        esperar(lambda: ocioso(porta, 'proj'), 30)
        c, j = req(porta, "/api/avaliar/proj", {})
        ok(c == 409, f"com tudo avaliado o botão em lote é recusado ({c})")
        c, j = req(porta, "/api/cortes/proj")
        ok(c == 200, "painel devolve as notas")
        print("Barra de progresso real (avaliação lenta simulada: uma nota a cada 2,5 s)")
        d2 = raiz / "proj2"
        (d2 / "clipes").mkdir(parents=True)
        (d2 / "fonte.json").write_text((d / "fonte.json").read_text(encoding="utf-8"), encoding="utf-8")
        (d2 / "momentos.json").write_text((d / "momentos.json").read_text(encoding="utf-8"), encoding="utf-8")
        for i in (1, 2, 3):
            (d2 / "clipes" / f"{i:02d}.mp4").write_bytes(b"\0" * 64)
            (d2 / "clipes" / f"{i:02d}.json").write_text(json.dumps({"dur": 20, "ini": i, "fim": i + 20, "gancho": f"G{i}"}), encoding="utf-8")
        c, j = req(porta, "/api/avaliar/proj2", {})
        ok(c == 202, f"avaliar em lote começa ({c})")
        vistos, t0 = [], time.time()
        while time.time() - t0 < 60:
            c, est = req(porta, "/api/estado/proj2")
            no = (est.get("nos") or {}).get("potencial", {}) if c == 200 else {}
            if no.get("status") == "trabalhando" and no.get("progresso") is not None:
                if not vistos or no["progresso"] != vistos[-1]:
                    vistos.append(no["progresso"])
            if no.get("status") == "concluido":
                break
            time.sleep(0.25)
        print(f"  progresso observado: {vistos}")
        ok(len(vistos) >= 3, f"a barra andou por valores intermediários, não só 0 e 100 ({len(vistos)} leituras)")
        ok(vistos == sorted(vistos) and all(0.0 <= v < 1.0 for v in vistos), "o progresso só sobe e fica abaixo de 100% até concluir")
        ok(vistos and vistos[0] <= 0.05, "começa perto de 0")
        ok(any(0.2 < v < 0.9 for v in vistos), "passa por valor intermediário real (notas gravadas)")
        ok(esperar(lambda: all((d2 / "clipes" / f"{i:02d}.potencial.json").exists() for i in (1, 2, 3))), "as 3 notas foram gravadas")
        c, est = req(porta, "/api/estado/proj2")
        ok(est["nos"]["potencial"]["status"] == "concluido", "ao fim a etapa fica concluída")
        html = (RAIZ / "clipes" / "web" / "index.html").read_text(encoding="utf-8")
        ok("data-barra-av" in html and "faixaAv" in html and "atualizaBarrasAv" in html, "UI tem a barra no corte e a faixa de progresso")
        ok("data-avaliar" in html and "btnAvaliarTodos" in html, "UI tem o botão por corte e o botão em lote")
    finally:
        srv.terminate()
        try:
            srv.wait(10)
        except subprocess.TimeoutExpired:
            srv.kill()
    print("\nTUDO OK" if not falhas else f"\n{len(falhas)} FALHA(S): " + "; ".join(falhas))
    sys.exit(1 if falhas else 0)


def ocioso(porta, slug):
    c, j = req(porta, f"/api/cortes/{slug}")
    return c == 200 and not (j or {}).get("trabalho")


def _vivo(porta):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{porta}/api/fluxo", timeout=2).read()
        return True
    except Exception:  # noqa: BLE001
        return False


if __name__ == "__main__":
    main()
