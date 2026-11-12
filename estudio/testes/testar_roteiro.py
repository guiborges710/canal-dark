"""Confere a regra de roteiro: a contagem de números e gráficos, o aviso da conformidade e o que cada agente passa a receber.
Uso: .venv\\Scripts\\python estudio\\testes\\testar_roteiro.py"""
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from estudio import prompts  # noqa: E402
from media import roteiro  # noqa: E402

passou, falhas = 0, []


def confere(cond, nome, extra=None):
    global passou
    if cond:
        passou += 1
        print(f"  ok  {nome}" + (f" ({extra})" if extra is not None else ""), flush=True)
    else:
        falhas.append(nome)
        print(f"  FALHOU  {nome}" + (f" -> {extra}" if extra is not None else ""), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("[Contagem]")
    for texto, n in (
        ("Você marcou com os amigos e todo mundo cancelou.", 0),
        ("Um amigo cancelou e uma amiga também.", 0),
        ("Em 2021, 54% dos adultos bebiam.", 2),
        ("Foram R$ 3.200 no total.", 1),
        ("dezessete vírgula cinco por cento dos jovens", 1),
        ("Em dois mil e vinte e cinco, dezessete vírgula cinco por cento.", 2),
        ("1 em cada 3 amigos", 1),
        ("um em cada três amigos", 1),
        ("onze milhões para oito vírgula dois milhões", 2),
    ):
        confere(len(roteiro.numeros(texto)) == n, f"{texto!r} tem {n}", roteiro.numeros(texto))
    print("[Gráficos]")
    py = "from media.sketch_lib import *\n\n\ndef cena_0(lt, dur):\n    barras(d, 1, 2, [])\n    return im\n\n\ndef cena_1(lt, dur):\n    pessoa(d, 1, 2)\n    return im\n"
    confere(roteiro.cenas_com_grafico([{"tipo": "sketch", "desenho": "cena_0"}, {"tipo": "sketch", "desenho": "cena_1"}], py) == 1, "Scratch: olha só a função da cena")
    confere(roteiro.cenas_com_grafico([{"tipo": "barras"}, {"tipo": "gancho"}]) == 1, "Cartão")
    confere(roteiro.cenas_com_grafico([{"objetos": [{"tipo": "grafico"}]}, {"objetos": [{"tipo": "celular"}]}]) == 1, "Cartoon Vivo")
    confere(roteiro.cenas_com_grafico([{"recortes": [{"tipo": "grafico"}]}, {"recortes": [{"tipo": "foto"}]}]) == 1, "Colagem")

    print("[Vídeos reais]")
    real = (REPO / "output" / "nem-nem-2025" / "roteiro.txt").read_text(encoding="utf-8")
    confere(len(roteiro.numeros(real)) > roteiro.MAX_NUMEROS, "Um roteiro antigo cheio de dado é detectado", len(roteiro.numeros(real)))

    print("[Conformidade]")
    import compliance
    fala = "Você marcou com os amigos e todo mundo cancelou de novo e ninguém achou estranho porque virou costume."
    cena = {"tipo": "sketch", "desenho": "cena_0", "duracao": 30, "fala": fala}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        (p / "cenas.json").write_text(json.dumps([cena]), encoding="utf-8")
        (p / "roteiro.txt").write_text("Em 2013 eram 7 horas. Em 2021, 3 horas. Em 2023, 2 horas.", encoding="utf-8")
        avisos = "\n".join(str(x) for x in compliance.avisos_de_roteiro(p, [cena]))
        confere("números" in avisos, "Muitos números geram aviso", avisos)
        (p / "roteiro.txt").write_text(fala, encoding="utf-8")
        confere(not compliance.avisos_de_roteiro(p, [cena]), "Roteiro sem número não gera aviso")
        (p / "roteiro.txt").write_text("7 horas, 3 horas e 2 horas, 54%.", encoding="utf-8")
        confere(not compliance.avisos_de_roteiro(p, [{"tipo": "gancho"}]), "O estilo Cartão fica de fora: ele é feito de números")

    print("[O que cada agente recebe]")
    confere("prompts/tipos_de_roteiro.md" in prompts.ETAPA["roteiro"], "O Neymar é mandado ler os tipos de roteiro")
    confere("no máximo 2" in prompts.ETAPA["courtois"], "O Courtois confere o limite")
    tipos = (REPO / "prompts" / "tipos_de_roteiro.md").read_text(encoding="utf-8")
    for arq, deve, nao in (
        (".claude/agents/neymar-roteirista.md", "tipos_de_roteiro", "Números em algarismos (ex.: 15%)"),
        (".claude/agents/cristiano-otimizador-viral.md", "tipos_de_roteiro", "Números em algarismos (ex.: 15%)"),
        (".claude/agents/olise-diretor-arte.md", "tipos_de_roteiro", "O dado da cena aparece como número grande ou barra"),
        (".claude/agents/courtois-revisor-fatos.md", "tipos_de_roteiro", None),
        (".claude/agents/modric-pesquisador-tema.md", "Situações", None),
        (".claude/agents/messi-estrategista-angulo.md", "tipos_de_roteiro", None),
        (".claude/skills/roteiro-para-video-sketch/SKILL.md", "tipos_de_roteiro", "rótulo curto que carrega dado"),
        ("prompts/writer.md", "tipos_de_roteiro", "Números em algarismos (ex.: 15%)"),
        ("CLAUDE.md", "tipos_de_roteiro", "1 a 3 blocos com números"),
    ):
        t = (REPO / arq).read_text(encoding="utf-8")
        confere(deve in t and (nao is None or nao not in t), f"{arq} segue a regra nova")
    confere(all(x in tipos for x in ("Cena do dia a dia", "Mesma coisa, outra época", "Antigamente, e por quê", "Não é o que dizem", "História de um caso", "Um número só")), "Os seis tipos estão descritos")
    print(f"\n{passou} verificações ok, {len(falhas)} falhas.")
    if falhas:
        print("\n".join(f" - {f}" for f in falhas))
        sys.exit(1)


if __name__ == "__main__":
    main()
