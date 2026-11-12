"""Roda o fluxo configurado de um projeto de clipes, etapa por etapa (V2).

  python -m clipes rodar <slug>                  # continua de onde parou
  python -m clipes rodar <slug> --desde corte    # refaz a partir de uma etapa (tentar de novo)
  python -m clipes rodar <slug> --desde momentos --refazer   # apaga o resultado da etapa e refaz

- Etapa já concluída é pulada (resultados intermediários ficam em clipes_out/<slug>/).
- Código roda aqui; agentes rodam por `claude -p --agent <id>` com o login do Claude Code (nunca a
  ANTHROPIC_API_KEY do .env); etapas humanas (revisão, aprovação) param o fluxo com "espera você".
- Projeto sem fluxo.json (anterior à V2) segue o fluxo da V1: os agentes não são disparados aqui.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

from . import estado as E
from . import etapas as T
from . import perfis as PF
from . import pipeline as P
from . import triagem as TG

TEMPO_AGENTE_S = 30 * 60
FERRAMENTAS = ("Read,Write,Edit,Glob,Grep,Bash(.venv\\Scripts\\python -m clipes *),"
               "Bash(.venv/Scripts/python -m clipes *),Bash(python -m clipes *)")


class Parada(Exception):
    """O fluxo parou de propósito (espera você, bloqueio ou falha já registrada no painel)."""


# ------------------------------------------------------------------ agentes
def _comando_claude() -> list[str]:
    """CLIPES_CLAUDE (só testes: simulador) ou o `claude` do PATH."""
    sim = os.environ.get("CLIPES_CLAUDE")  # lista JSON: ["python", "simulador.py"]
    if sim:
        return json.loads(sim)
    exe = shutil.which("claude")
    if not exe:
        raise FileNotFoundError("comando `claude` não encontrado no PATH")
    return [exe]


def _ambiente() -> dict:
    try:  # mesma regra do Corte: nenhuma chave do .env vai para o agente
        from estudio.executor import ambiente_agente
        env = ambiente_agente()
    except Exception:  # noqa: BLE001
        env = dict(os.environ)
        env.pop("ANTHROPIC_API_KEY", None)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _instrucao(d: Path, e: dict, ids: list[int] | None = None) -> str:
    slug = d.name
    revisao = T.ativa(d, "revisao")
    base = (f"Projeto do setor de Clipes: clipes_out/{slug}/ (slug `{slug}`). Sua etapa: {e['titulo']} (nó `{e['id']}`).\n"
            "MODO ORQUESTRADO PELO PAINEL: faça só a sua etapa e termine. NÃO rode `python -m clipes cortar`, "
            "`tudo`, `ajustar` nem `rodar`: o painel gera os cortes na etapa seguinte.\n"
            f"Leia `clipes_out/{slug}/perfil.json` (perfil do projeto) antes de decidir.\n"
            f"Reporte o andamento: `.venv\\Scripts\\python -m clipes estado {slug} {e['id']} trabalhando \"...\" --agente {e['agente']}`.\n")
    alvo = ("as sugestões com status `aceito`" if revisao else "as sugestões que não estão com status `rejeitado`")
    marcos = ""
    if e["id"] == "potencial":
        alvo = ids or sorted(int(j.stem) for j in (d / "clipes").glob("[0-9][0-9].json"))
        n = max(len(alvo), 1)
        linhas = []
        for k, i in enumerate(alvo):
            p1, p2, p3 = ((k + f) / n for f in (0.33, 0.66, 0.95))
            linhas.append(f"  corte {i:02d}: depois de ler o corte e a transcrição --progresso {p1:.2f}; depois de aplicar os critérios "
                          f"--progresso {p2:.2f}; depois de gravar clipes/{i:02d}.potencial.json --progresso {p3:.2f}")
        marcos = ("\nANDAMENTO REAL (o painel mostra uma barra de progresso com estes números): em cada ponto abaixo rode "
                  f"`.venv\\Scripts\\python -m clipes estado {slug} potencial trabalhando \"<o que acabou de fazer>\" --agente Totti "
                  "--progresso <número>` com o número EXATO indicado. Só reporte nesses pontos, depois de fazer de verdade; "
                  "não marque `concluido` (o código fecha a etapa).\n" + "\n".join(linhas) + "\n")
    especifico = {
        "curadoria": (
            "Em momentos.json, para cada sugestão: mantenha todos os campos; acrescente `parecer` (uma frase: "
            "se o trecho se sustenta sozinho e por quê). Ajuste `ini`/`fim` só para fronteira de frase, dentro da "
            "duração do perfil. Momentos com `serie` são PARTES de um mesmo assunto que não coube em um vertical: "
            "aceite ou rejeite todas juntas, não mexa nos limites entre elas e decida se o assunto inteiro vale uma série. "
            "Há até o dobro da quantidade pedida em candidatos: escolha só os melhores, no máximo "
                f"{PF.do_projeto(d)['quantidade']}, e marque os outros como `rejeitado` (entregar menos é aceitável). " + (
                "Deixe `status` como `sugerido` (o Guilherme decide na revisão) e marque `rejeitado` só o que "
                "contém assunto a excluir ou não faz sentido sozinho."
                if revisao else
                "A revisão humana está desligada neste projeto: marque `status` como `aceito` ou `rejeitado`.")),
        "comentario": f"Escreva `gancho` e `fecho` em momentos.json para {alvo}.",
        "gancho": (f"Decida o teaser (`gancho_trecho`) de {alvo}, e grave ganchos.md. O Guilherme aprovou o texto do Zidane: "
                   "NÃO altere `gancho`, `fecho` nem `cta`; escolha o teaser sem mexer neles."
                   if T.ativa(d, "revisao_texto") else
                   f"Decida o teaser (`gancho_trecho`) e o `gancho` de {alvo}, e grave ganchos.md."),
        "triagem": ("Avalie a FONTE (o vídeo longo inteiro): leia triagem_dados.json (medições do código) e a transcrição, "
                    "e grave triagem.json e triagem.md. Você roda ANTES do Kaká e de qualquer corte. PASSO 4 (obrigatório): "
                    "dê `nota` de 0 a 100 a CADA momento de `momentos_promissores` (mesma régua do Totti) e deixe a lista "
                    "ordenada da maior nota para a menor; o código segue só com a melhor parte (30% por padrão). Se `triagem.json` já existir "
                    "com momentos SEM `nota`, não reavalie a fonte: só complete o passo 4 e regrave."),
        "potencial": ("Avalie " + (f"SÓ os cortes {', '.join(f'{i:02d}' for i in ids)}" if ids else "cada corte pronto") +
                      " em clipes/NN.json e grave clipes/NN.potencial.json" + ("" if ids else " e potencial.md") + "."),
    }[e["id"]]
    extra = PF.do_projeto(d)["instrucoes_agentes"].get(
        {"curadoria": "kaka", "comentario": "zidane", "gancho": "figo", "potencial": "totti",
         "triagem": "rivaldo"}[e["id"]], "")
    return base + especifico + marcos + (f"\nInstrução do perfil para você: {extra}" if extra else "")


def _vigia_potencial(d: Path, alvo: list[int], desde: float, parar: threading.Event) -> None:
    """Progresso REAL da avaliação: conta os `NN.potencial.json` já gravados nesta rodada e só SOBE a barra
    (os marcos que o Totti reporta podem ser mais finos; este vigia garante o andamento mesmo se ele esquecer)."""
    cl = Path(d) / "clipes"
    n = max(len(alvo), 1)
    while not parar.wait(1.0):
        feitos = sum(1 for i in alvo if (cl / f"{i:02d}.potencial.json").exists()
                     and (cl / f"{i:02d}.potencial.json").stat().st_mtime >= desde - 1)
        no = E.ler(d)["nos"].get("potencial", {})
        if no.get("status") != "trabalhando":
            continue
        p = min(feitos / n, 0.99)
        if (no.get("progresso") or 0.0) + 1e-6 < p:
            E.marcar(d, "potencial", "trabalhando", f"Totti avaliou {feitos} de {len(alvo)} corte(s)", "Totti", progresso=p)


def _rodar_agente(d: Path, e: dict, ids: list[int] | None = None, fechar: bool = True) -> None:
    log = d / "agentes" / f"{e['id']}.log"
    log.parent.mkdir(exist_ok=True)
    inicio_agente = time.time()
    eh_pot = e["id"] == "potencial"
    if e["id"] == "triagem":  # medições do código ANTES do agente (rápido, sem áudio)
        E.marcar(d, "triagem", "trabalhando", "medindo a fonte (duração, fala, candidatos)", "Código", progresso=0.05)
        TG.coletar(d)
    E.marcar(d, e["id"], "trabalhando", f"{e['agente']} trabalhando (Claude Code)", e["agente"],
             progresso=0.0 if eh_pot else 0.2 if e["id"] == "triagem" else None)
    parar = threading.Event()
    if eh_pot:
        alvo_pot = ids or sorted(int(j.stem) for j in (d / "clipes").glob("[0-9][0-9].json"))
        threading.Thread(target=_vigia_potencial, args=(d, alvo_pot, inicio_agente, parar), daemon=True).start()
    try:
        cmd = _comando_claude() + ["-p", "--agent", e["agente_id"], "--permission-mode", "acceptEdits",
                                   "--allowedTools", FERRAMENTAS, "--strict-mcp-config", "--no-session-persistence"]
    except FileNotFoundError as x:
        _falha(d, e["id"], str(x), [], "Instale o Claude Code ou desative a etapa no fluxo do projeto.")
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} {e['agente_id']}\n")
        fh.flush()
        try:
            r = subprocess.run(cmd, input=_instrucao(d, e, ids), text=True, encoding="utf-8", errors="replace",
                               stdout=fh, stderr=subprocess.STDOUT, cwd=str(P.RAIZ), env=_ambiente(),
                               timeout=TEMPO_AGENTE_S)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = "tempo esgotado"
        finally:
            parar.set()
    if rc != 0:
        cauda = [x for x in log.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()][-4:]
        _falha(d, e["id"], f"{e['agente']} terminou com erro ({rc})", cauda,
               f"Veja clipes_out/{d.name}/agentes/{e['id']}.log e use “Tentar de novo”.")
    falta = _confere_agente(d, e["id"], ids, inicio_agente)
    if falta:
        _falha(d, e["id"], f"{e['agente']} terminou sem completar a etapa", [falta],
               "Use “Tentar de novo” ou desative a etapa no fluxo do projeto.")
    if fechar:
        E.marcar(d, e["id"], "concluido", _resumo_agente(d, e["id"]), e["agente"])


def _confere_agente(d: Path, eid: str, ids: list[int] | None = None, desde: float = 0.0) -> str:
    """Confere o resultado que o agente deveria ter gravado. Devolve o que falta ('' se ok)."""
    if eid == "triagem":
        return TG.validar(d, desde)
    try:
        mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
        assert isinstance(mom, list) and all("id" in m and "ini" in m and "fim" in m for m in mom)
    except (OSError, ValueError, AssertionError):
        return "momentos.json ficou ilegível ou sem os campos id/ini/fim"
    if eid == "curadoria" and (d / "perfil.json").exists():
        return _revalida_curadoria(d, mom)
    alvos = set(P.alvos_corte(d, T.ativa(d, "revisao")))
    if eid == "comentario":
        # parte de série: o CTA ocupa o lugar do fecho, então `cta` vale no lugar de `fecho`
        sem = [m["id"] for m in mom if m["id"] in alvos and not (m.get("gancho") and (m.get("fecho") or (m.get("serie") and m.get("cta"))))]
        return f"sem gancho/fecho nas sugestões {sem}" if sem else ""
    if eid == "potencial":
        cl = d / "clipes"
        alvo = [f"{i:02d}" for i in ids] if ids else [j.stem for j in cl.glob("[0-9][0-9].json")]
        sem = [n for n in alvo if not (cl / f"{n}.potencial.json").exists()
               or (cl / f"{n}.potencial.json").stat().st_mtime < desde - 1]  # tem de ser avaliação NOVA
        return f"sem avaliação nos cortes {sem}" if sem else ""
    return ""


def _revalida_curadoria(d: Path, mom: list[dict]) -> str:
    """Depois do Kaká: todo intervalo que ele mexeu passa pelos critérios de integridade do código.
    Alinha às fronteiras de palavra e registra o que o código encontrou em `problemas`/`correcoes`."""
    from . import editorial as ED
    tj = json.loads((d / "transcricao.json").read_text(encoding="utf-8"))
    tr, idioma = tj["segmentos"], tj.get("idioma")
    perfil = PF.do_projeto(d)
    for m in mom:
        if m.get("status") == "rejeitado":
            continue
        rv = ED.revalidar(tr, m["ini"], m["fim"], perfil, idioma)
        m["problemas"] = sorted(set(rv["problemas"]))
        m["avisos"] = sorted(set(rv.get("avisos", [])))
        if m.get("serie"):  # continuação entre partes é esperada, não é defeito
            m["avisos"] = [a for a in m["avisos"] if "continuar" not in a and "depender" not in a]
        m["correcoes"] = sorted(set(m.get("correcoes", []) + rv["correcoes"]))
        if not rv["problemas"] and (abs(rv["ini"] - m["ini"]) > 0.01 or abs(rv["fim"] - m["fim"]) > 0.01):
            m.setdefault("ini_agente", m["ini"]); m.setdefault("fim_agente", m["fim"])
            m["ini"], m["fim"], m["dur"] = rv["ini"], rv["fim"], round(rv["fim"] - rv["ini"], 1)
        # `texto` é o que o resto do fluxo usa (gancho padrão, descrição): refaz a partir do intervalo FINAL
        pal = [w["t"] for sg in tr for w in sg.get("palavras", []) if m["ini"] <= w["ini"] < m["fim"]]
        if pal:
            m["texto"] = " ".join(pal)[:160].lower()
        if rv["problemas"]:  # corte que o código reprova não segue como se estivesse bom
            m["parecer_codigo"] = "reprovado na integridade: " + "; ".join(rv["problemas"])
            if T.ativa(d, "revisao"):
                m["status"] = "sugerido"
            else:
                m["status"] = "rejeitado"
    chave = lambda m: (m.get("serie") or {}).get("id") or f"u{m['id']}"  # noqa: E731
    for m in mom:  # uma série vive ou morre inteira: parte órfã quebra o contexto
        if m.get("serie") and any(x.get("status") == "rejeitado" or x.get("problemas")
                                  for x in mom if chave(x) == chave(m)):
            if m.get("status") != "rejeitado":
                m["status"] = "rejeitado"
                m["parecer_codigo"] = m.get("parecer_codigo") or "série incompleta: uma das partes foi rejeitada ou reprovada"
    cota = int(perfil["quantidade"])  # o pool da curadoria é maior que a cota; a cota conta ASSUNTOS (série = 1)
    grupos: dict[str, list] = {}
    for m in mom:
        if m.get("status") != "rejeitado":
            grupos.setdefault(chave(m), []).append(m)
    ordem = sorted(grupos.values(), key=lambda g: max(x.get("score", 0) for x in g), reverse=True)
    for g in ordem[cota:]:
        for m in g:
            m["status"] = "rejeitado"
            m["parecer_codigo"] = f"acima da cota do perfil ({cota}): ficaram os de maior nota"
    (d / "momentos.json").write_text(json.dumps(mom, ensure_ascii=False, indent=2), encoding="utf-8")
    return ""


def avaliar_potencial(d: Path, ids: list[int] | None = None) -> str:
    """Plano B, botão "Avaliar potencial": o Totti avalia só os cortes pedidos (ou os que ainda não têm nota).
    O fluxo normal já roda o Totti (etapa `potencial`); isto serve quando a nota faltou ou a etapa falhou.
    Devolve 'concluido', 'nada a avaliar' ou a falha."""
    d = Path(d)
    cl = d / "clipes"
    existentes = sorted(int(j.stem) for j in cl.glob("[0-9][0-9].mp4")) if cl.exists() else []
    if ids:
        ids = [i for i in ids if i in existentes]
    else:
        ids = [i for i in existentes if not (cl / f"{i:02d}.potencial.json").exists()]
    if not ids:
        return "nada a avaliar"
    e = {**T.POR_ID["potencial"], "ferramentas": {}}
    try:
        _rodar_agente(d, e, ids)
    except Parada as p:
        return f"falhou: {p}"
    return "concluido"


def _resumo_agente(d: Path, eid: str) -> str:
    if eid == "triagem":
        t = json.loads((d / "triagem.json").read_text(encoding="utf-8"))
        ms = sorted((float(m["nota"]) for m in (t.get("momentos_promissores") or []) if "nota" in m), reverse=True)
        top = ", ".join(f"{x:.0f}" for x in ms[:3])
        return (f"Nota {float(t['nota']):.0f} ({t.get('veredito', '?')}): {t.get('recomendacao', '?').replace('_', ' ')}; "
                f"{len(ms)} momento(s) promissor(es)" + (f", melhores notas {top}" if top else ""))
    mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
    if eid == "curadoria":
        rej = sum(1 for m in mom if m.get("status") == "rejeitado")
        return f"{len(mom)} sugestões revisadas, {rej} rejeitada(s)"
    if eid == "gancho":
        return f"{sum(1 for m in mom if m.get('gancho_trecho'))} corte(s) com teaser"
    if eid == "comentario":
        return "gancho e fecho escritos"
    return "avaliação gravada (estimativa editorial, não previsão de views)"


def _falha(d: Path, eid: str, msg: str, detalhe: list[str], resolver: str):
    E.marcar(d, eid, "falhou", msg, None, detalhe, resolver)
    raise Parada(msg)


# ------------------------------------------------------------------ etapas de código
def _melhores_da_triagem(d: Path):
    """(lista ordenada por nota, N) quando a triagem do Rivaldo está ativa, válida e N > 0; senão None."""
    if not T.ativa(d, "triagem") or not (d / "triagem.json").exists() or TG.validar(d):
        return None
    pct = int(T.ferramenta(d, "triagem", "melhores_pct") or 0)
    if pct <= 0:
        return None
    ms = TG.melhores(d)
    n = max(1, round(len(ms) * pct / 100))  # 30% de 10 destaques = 3; sempre pelo menos 1
    return (ms, n) if ms else None


def _triagem(d: Path, e: dict) -> None:
    """Rivaldo avalia a fonte. Nota abaixo do mínimo do projeto: o fluxo PARA e pergunta a você (nunca decide sozinho).
    Rodar de novo com a etapa em 'espera você' = você escolheu continuar mesmo assim."""
    tj = d / "triagem.json"
    if E.ler(d)["nos"].get("triagem", {}).get("status") == "espera_voce" and tj.exists():
        E.marcar(d, "triagem", "concluido", _resumo_agente(d, "triagem") + " · você escolheu continuar", "Guilherme")
        return
    _rodar_agente(d, e, fechar=False)
    minimo = float(e["ferramentas"].get("nota_minima", 45))
    nota = float(json.loads(tj.read_text(encoding="utf-8"))["nota"])
    if minimo > 0 and nota < minimo:
        E.marcar(d, "triagem", "espera_voce",
                 f"{_resumo_agente(d, 'triagem')}. Nota abaixo de {minimo:.0f}: vale clipar mesmo assim? "
                 "Clique em Continuar para seguir.", "Guilherme")
        raise Parada("triagem com nota baixa: espera você")
    E.marcar(d, "triagem", "concluido", _resumo_agente(d, "triagem"), "Rivaldo")


def _fonte(d: Path, e: dict) -> None:
    f = json.loads((d / "fonte.json").read_text(encoding="utf-8"))
    if (d / "fonte.mp4").exists():  # já baixado: só registra (nada é refeito)
        E.marcar(d, "fonte", "concluido", f"{f.get('autor', '')}: {f.get('titulo_original') or f.get('origem', '')}"[:120])
        E.marcar(d, "autorizacao", "concluido", f"{f.get('autorizacao', {}).get('tipo', '?')}")
        return
    P.ingest(f["origem"], d.name, f["autorizacao"]["tipo"], f["autorizacao"].get("prova", ""), f["autor"],
             f.get("titulo_original", ""), PF.do_projeto(d)["id"])


def _corte(d: Path, e: dict) -> None:
    ids = P.alvos_corte(d, T.ativa(d, "revisao"))
    if not ids:
        _falha(d, "corte", "nenhuma sugestão aceita para cortar", [],
               "Aceite ao menos uma sugestão na revisão e use “Continuar”.")
    refino = T.ferramenta(d, "transcricao", "refino")
    if refino and not (d / "refino.json").exists():
        P.refinar(d, refino, ids=ids)
        (d / "refino.json").write_text(json.dumps({"modelo": refino, "ids": ids}), encoding="utf-8")
    legenda = bool(e["ferramentas"].get("legenda", True))
    audio = bool(e["ferramentas"].get("audio", True))
    if not audio or not legenda:  # opção desligada em "Configurar etapas": nunca em silêncio
        faltam = " e ".join(x for x, on in (("ÁUDIO", audio), ("LEGENDA", legenda)) if not on)
        E.marcar(d, "corte", "trabalhando", f"ATENÇÃO: cortando SEM {faltam} (opção desligada em Configurar etapas)")
        print(f"[corte] ATENÇÃO: sem {faltam}")
    P.cortar(d, ids, legenda=legenda, audio=audio)


def _humano(d: Path, e: dict) -> None:
    if e["id"] == "revisao_texto":
        return _revisao_texto(d)
    if e["id"] == "revisao":
        mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
        pend = [m["id"] for m in mom if m.get("status", "sugerido") == "sugerido"]
        if pend or not any(m.get("status") == "aceito" for m in mom):
            E.marcar(d, "revisao", "espera_voce",
                     f"aceite ou rejeite as sugestões ({len(pend)} sem decisão) e clique em Continuar", "Guilherme")
            raise Parada("espera a revisão")
        n = sum(1 for m in mom if m.get("status") == "aceito")
        E.marcar(d, "revisao", "concluido", f"{n} aceita(s), {len(mom) - n} rejeitada(s)", "Guilherme")
        return
    E.marcar(d, e["id"], "espera_voce", "revisar os cortes e postar à mão no Instagram e TikTok", "Guilherme")
    raise Parada("espera aprovação")


def _revisao_texto(d: Path) -> None:
    mom = json.loads((d / "momentos.json").read_text(encoding="utf-8"))
    alvos = set(P.alvos_corte(d, T.ativa(d, "revisao")))
    falta = [m["id"] for m in mom if m["id"] in alvos and not m.get("texto_aprovado")]
    if falta:
        E.marcar(d, "revisao_texto", "espera_voce",
                 f"leia o texto do Zidane ({len(falta)} corte(s) sem aprovação), edite como quiser e aprove", "Guilherme")
        raise Parada("espera a aprovação do texto")
    n = sum(1 for m in mom if m["id"] in alvos and m.get("texto_editado"))
    E.marcar(d, "revisao_texto", "concluido", f"texto aprovado ({n} editado(s) por você)", "Guilherme")


CODIGO = {
    "fonte": _fonte,
    "autorizacao": lambda d, e: None,  # registrada junto com a fonte
    "transcricao": lambda d, e: P.transcrever(d, e["ferramentas"].get("modelo", "small")),
    # com curadoria ativa, o código entrega um conjunto maior de candidatos íntegros e o Kaká escolhe os melhores;
    # com a triagem do Rivaldo ativa, só os N melhores momentos dela viram candidatos
    "momentos": lambda d, e: P.momentos(d, quantos=(PF.do_projeto(d)["quantidade"] * 2 if T.ativa(d, "curadoria") else None),
                                        energia=bool(e["ferramentas"].get("energia", True)),
                                        usar_termos=bool(e["ferramentas"].get("termos", True)),
                                        intervalos=_melhores_da_triagem(d)),
    "corte": _corte,
    "originalidade": lambda d, e: P.check(d) or _falha_silenciosa(),
    "embalagem": lambda d, e: P.embalar(d),
}


def _falha_silenciosa():
    raise Parada("bloqueado no check (detalhes no painel)")


ARTEFATOS = {"transcricao": ["transcricao.json"], "momentos": ["momentos.json"], "corte": ["refino.json"],
             "triagem": ["triagem.json"]}


# ------------------------------------------------------------------ execução
def rodar(d: Path, desde: str | None = None, refazer: bool = False) -> str:
    """Roda as etapas ativas na ordem. Devolve 'concluido', 'parado' ou a etapa em espera."""
    d = Path(d)
    fl = T.do_projeto(d)
    etapas = T.ativas(d)
    ids = [e["id"] for e in etapas]
    if desde:
        if desde not in ids:
            raise SystemExit(f"etapa {desde!r} não está ativa neste projeto: {', '.join(ids)}")
        for eid in ids[ids.index(desde):]:
            E.marcar(d, eid, "pendente", "na fila para rodar de novo")
        if refazer:
            for a in ARTEFATOS.get(desde, []):
                (d / a).unlink(missing_ok=True)
    E.marcar(d, "saida", "pendente", "")
    est = E.ler(d)["nos"]
    for e in etapas:
        if est.get(e["id"], {}).get("status") == "concluido":
            continue
        try:
            if e["executor"] == "codigo":
                CODIGO[e["id"]](d, e)
                if e["id"] in ("fonte", "autorizacao"):
                    continue  # ingest já marca os dois nós
                st = E.ler(d)["nos"].get(e["id"], {}).get("status")
                if st != "concluido":
                    E.marcar(d, e["id"], "concluido", E.ler(d)["nos"].get(e["id"], {}).get("msg") or "feito")
            elif e["executor"] == "agente":
                if fl.get("legado"):  # V1: o Pelé aciona os agentes
                    if est.get(e["id"], {}).get("status") != "concluido":
                        E.marcar(d, e["id"], "pendente", f"aguarda o Pelé acionar {e['agente']}", e["agente"])
                    continue
                if e["id"] == "triagem":
                    _triagem(d, e)
                else:
                    _rodar_agente(d, e)
                    if e["id"] == "comentario":
                        P.limpar_aprovacao_texto(d)  # texto novo do Zidane precisa de aprovação nova
            else:
                _humano(d, e)
        except Parada as p:
            print(f"[rodar] parou em {e['id']}: {p}")
            return e["id"]
        except SystemExit as x:
            if E.ler(d)["nos"].get(e["id"], {}).get("status") != "falhou":
                E.marcar(d, e["id"], "falhou", str(x)[:120], None, [str(x)], "Corrija e use “Tentar de novo”.")
            print(f"[rodar] falhou em {e['id']}: {x}")
            return e["id"]
        except Exception as x:  # noqa: BLE001 - o painel precisa mostrar a falha
            if E.ler(d)["nos"].get(e["id"], {}).get("status") != "falhou":
                txt = str(getattr(x, "stderr", "") or x)
                rc = getattr(x, "returncode", None)
                memoria = rc in (-542398533, 3752568763) or any(
                    k in txt.lower() for k in ("cannot allocate", "malloc", "out of memory", "memória"))
                if memoria:  # AVERROR_EXTERNAL do x264/libass costuma ser falta de memória neste PC
                    E.marcar(d, e["id"], "falhou", "faltou memória para o ffmpeg/Whisper", None, [txt[-400:]],
                             "Feche programas pesados (Chrome, jogos) e use “Tentar de novo”: as etapas anteriores "
                             "não são refeitas. Se repetir, aumente o arquivo de paginação do Windows.")
                else:
                    E.marcar(d, e["id"], "falhou", f"erro na etapa: {str(x)[:100]}", None, [txt[-400:]],
                             "Veja o erro e use “Tentar de novo”: as etapas anteriores não são refeitas.")
            print(f"[rodar] falhou em {e['id']}: {x}")
            return e["id"]
    E.marcar(d, "saida", "concluido", "fluxo completo")
    return "concluido"


def aprovar(d: Path) -> None:
    """Botão Aprovar da última etapa humana: fecha o fluxo (postar continua manual)."""
    E.marcar(Path(d), "aprovacao", "concluido", "aprovado pelo Guilherme", "Guilherme")
    E.marcar(Path(d), "saida", "concluido", "pacote pronto")
