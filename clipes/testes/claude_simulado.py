"""Simula o `claude -p --agent <id>` nos testes (nenhuma chamada real). Lê a instrução do stdin,
acha o projeto e grava o que o agente gravaria. CLIPES_SIM_FALHA=<agente> faz esse agente falhar uma vez."""
import json
import os
import re
import sys
from pathlib import Path

args = sys.argv[1:]
agente = args[args.index("--agent") + 1]
txt = sys.stdin.read()
slug = re.search(r"slug `([^`]+)`", txt).group(1)
d = Path(os.environ.get("CLIPES_SAIDA_TESTE") or os.environ.get("CLIPES_SAIDA") or "clipes_out") / slug
marca = d / f".falhou_{agente}"
if os.environ.get("CLIPES_SIM_FALHA") == agente and not marca.exists():
    marca.write_text("1")
    print("erro simulado do agente")
    sys.exit(3)
if agente.startswith("rivaldo"):  # triagem da fonte: roda ANTES de existir momentos.json
    nota = float(os.environ.get("CLIPES_SIM_TRIAGEM_NOTA", "80"))
    (d / "triagem.json").write_text(json.dumps({
        "nota": nota, "veredito": "alto" if nota >= 70 else "medio" if nota >= 45 else "baixo",
        "recomendacao": "seguir" if nota >= 70 else "seguir_com_ressalvas" if nota >= 45 else "nao_vale",
        "formato": "podcast", "densidade": "simulado", "motivos": ["simulado"], "riscos": [], "sugestoes": [],
        "momentos_promissores": [{"ini": 10.0, "fim": 40.0, "nota": 70, "por_que": "simulado"}], "melhor_plataforma": "ambos"}),
        encoding="utf-8")
    (d / "triagem.md").write_text("simulado\n", encoding="utf-8")
    print("rivaldo: feito (simulado)")
    sys.exit(0)
mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
revisao = "Deixe `status` como `sugerido`" in txt
if agente.startswith("kaka"):
    for m in mom:
        m["parecer"] = "se sustenta sozinho (simulado)"
    mom[-1]["status"] = "rejeitado"
    if not revisao:
        for m in mom[:-1]:
            m["status"] = "aceito"
elif agente.startswith("zidane"):
    for m in mom:
        if m.get("status") != "rejeitado":
            m["gancho"], m["fecho"] = f"GANCHO {m['id']}", f"fecho {m['id']}"
elif agente.startswith("figo"):
    (d / "ganchos.md").write_text("simulado\n", encoding="utf-8")
elif agente.startswith("totti"):
    so = re.search(r"SÓ os cortes ([\d, ]+)", txt)  # plano B: avaliar só os cortes pedidos
    alvos = {x.strip() for x in so.group(1).split(",")} if so else None
    for j in (d / "clipes").glob("[0-9][0-9].json"):
        if alvos is not None and j.stem not in alvos:
            continue
        (d / "clipes" / f"{j.stem}.potencial.json").write_text(json.dumps({"nota": 50, "veredito": "medio"}), encoding="utf-8")
        import time
        time.sleep(float(os.environ.get("CLIPES_SIM_LENTO", "0")))  # avaliação lenta, para observar o progresso real
(d / "momentos.json").write_text(json.dumps(mom, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{agente}: feito (simulado)")
