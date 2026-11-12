"""Testes da triagem da fonte. Rodar: .venv\\Scripts\\python -m clipes.testes.testar_triagem

Casos SINTÉTICOS (rotulados): conferem as medições do código e a validação do triagem.json. O julgamento
do Rivaldo (agente) não é testado aqui.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from clipes import triagem as TG
from clipes.testes import testar_editorial as TE

falhas: list[str] = []


def ok(cond, msg):
    print(("  ok   " if cond else "  FALHA ") + msg)
    if not cond:
        falhas.append(msg)


def main():
    raiz = Path(tempfile.mkdtemp(prefix="clipes_triagem_"))
    try:
        print("Dados medidos pelo código")
        a, t1 = TE._topico("bolo de cenoura", 14, 5.0)
        b, t2 = TE._topico("motor de bicicleta", 14, t1 + 3.0)
        d = TE._proj_segs(raiz, "t1", a + b)
        dd = TG.coletar(d)
        ok((d / "triagem_dados.json").exists(), "grava triagem_dados.json")
        ok(dd["duracao_min"] > 1.0 and dd["fala"]["palavras_por_min"] > 50, f"mede duração e ritmo ({dd['duracao_min']} min, {dd['fala']['palavras_por_min']} pal/min)")
        ok(dd["seletor"]["candidatos_integros"] > 0 and dd["candidatos"], "acha candidatos íntegros com tempo e texto")
        ok(all(c["fim"] > c["ini"] and c["texto"] for c in dd["candidatos"]), "cada candidato traz ini, fim e a fala")
        ok(0 <= dd["fala"]["fala_pct"] <= 100 and 0 <= dd["fala"]["trechos_ruidosos_pct"] <= 100, "percentuais coerentes")
        ok("momentos_fortes_por_10min" in dd["seletor"], "densidade de momentos por 10 min")
        # fonte sem nada aproveitável: falas picadas e curtas
        picado = [{"ini": i * 2.0, "fim": i * 2.0 + 1.0, "texto": "tá né sim", "palavras": []} for i in range(60)]
        d2 = TE._proj_segs(raiz, "t2", picado)
        dd2 = TG.coletar(d2)
        ok(dd2["fala"]["falas_picadas_pct"] > 90 and dd2["seletor"]["candidatos_integros"] == 0, "fonte só de falas picadas: nenhum candidato")

        print("Validação do triagem.json")
        ok("não foi gravado" in TG.validar(d), "sem arquivo é recusado")
        base = {"nota": 70, "veredito": "alto", "recomendacao": "seguir", "formato": "podcast", "motivos": [], "riscos": [],
                "sugestoes": [], "momentos_promissores": [{"ini": 10, "fim": 40, "nota": 70, "por_que": "x"}]}
        (d / "triagem.json").write_text(json.dumps(base), encoding="utf-8")
        ok(TG.validar(d) == "", "arquivo completo é aceito")
        for rotulo, mud in [("sem campo", {"nota": None}), ("nota fora de 0-100", {"nota": 130}),
                            ("recomendação inválida", {"recomendacao": "talvez"}),
                            ("momento com fim antes do ini", {"momentos_promissores": [{"ini": 40, "fim": 10, "nota": 70}]}),
                            ("momento sem nota", {"momentos_promissores": [{"ini": 10, "fim": 40}]}),
                            ("nota do momento fora de 0-100", {"momentos_promissores": [{"ini": 10, "fim": 40, "nota": 140}]}),
                            ("momento sem tempo", {"momentos_promissores": [{"por_que": "x"}]})]:
            t = dict(base)
            t.update(mud)
            if rotulo == "sem campo":
                t.pop("nota")
            (d / "triagem.json").write_text(json.dumps(t), encoding="utf-8")
            ok(TG.validar(d) != "", f"recusa: {rotulo}")
        print("Os N melhores seguem o fluxo")
        from clipes import editorial as ED
        from clipes import perfis as PF
        ms = [{"ini": 5.0, "fim": 40.0, "nota": 55, "por_que": "médio"}, {"ini": 80.0, "fim": 110.0, "nota": 90, "por_que": "ótimo"},
              {"ini": 160.0, "fim": 190.0, "nota": 72, "por_que": "bom"}, {"ini": 400.0, "fim": 430.0, "nota": 20, "por_que": "fraco"}]
        t = dict(base)
        t["momentos_promissores"] = ms  # fora de ordem de propósito
        (d / "triagem.json").write_text(json.dumps(t), encoding="utf-8")
        ok([m["nota"] for m in TG.melhores(d)] == [90, 72, 55, 20], "o código ordena da maior nota para a menor (não depende do agente)")
        segs = json.loads((d / "transcricao.json").read_text(encoding="utf-8"))["segmentos"]
        perfil = PF.do_projeto(d)
        sel, rel = ED.momentos_de_intervalos(segs, perfil, TG.melhores(d), 3, "pt")
        ok(len({(m.get("serie") or {}).get("id") or m["id"] for m in sel}) <= 3 and all(m["origem"] == "rivaldo" for m in sel),
           f"no máximo 3 assuntos, todos vindos da triagem ({len(sel)} cortes, descartes {rel['descartes']})")
        ok(all(m["dur"] <= perfil["duracao"]["max"] for m in sel), "nenhum corte passa do limite do vertical")
        (d / "triagem.json").write_text(json.dumps(base), encoding="utf-8")
        ok("anterior" in TG.validar(d, desde=(d / "triagem.json").stat().st_mtime + 100), "arquivo de rodada anterior é recusado")
    finally:
        shutil.rmtree(raiz, ignore_errors=True)
    print("\nTUDO OK" if not falhas else f"\n{len(falhas)} FALHA(S): " + "; ".join(falhas))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
