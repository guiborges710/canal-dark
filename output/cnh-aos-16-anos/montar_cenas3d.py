"""Monta cenas3d.json do Short CNH aos 16 anos (estilo 3D low-poly). Texto = roteiro.txt revisado (Courtois)."""
import json
from pathlib import Path

AQUI = Path(__file__).parent
T = json.loads((AQUI / "textos3d.json").read_text(encoding="utf-8"))  # [{"fala":..., "legenda":...}] na ordem

SALA = "sala"
DUO = {"pos": [0, 2.6, 8.6], "look": [0, 2.3, 0], "fov": 35, "push": 0.05}
BUSTO = {"pos": [0, 2.35, 5.4], "look": [0, 2.1, 0], "fov": 35, "push": 0.07}


BARRAS = {"pos": [0, 1.1, 9.5], "look": [0, 0.8, 0], "fov": 36, "push": 0.04}


def ator_b(quem, **k):
    return {"quem": quem, "pos": [1.5, 0, -0.9], "rotY": -0.35, "esc": 0.8, **k}


def barra(x, h, cor, entra, rotulo):
    linhas = rotulo if isinstance(rotulo, list) else ([rotulo.split(" ", 1)[0], rotulo.split(" ", 1)[1]] if len(rotulo) > 9 else [rotulo])
    return [{"tipo": "barra", "pos": [x, 0, 0.2], "h": h, "cor": cor, "entra": entra, "w": 0.8, "d": 0.8},
            {"tipo": "rotulo", "pos": [x, h + 0.38, 0.4], "linhas": linhas, "w": 1.5, "hpx": 160 if len(linhas) == 1 else 230,
             "entra": entra + 0.3}]


def filho(x=-0.85, **k):
    return {"quem": "jovem", "pos": [x, 0, 0], "rotY": 0.3, **k}


def pai(x=0.85, **k):
    return {"quem": "pai", "pos": [x, 0, 0], "rotY": -0.3, **k}


cenas = [
    # 1 gancho: filho com volante imaginário; carimbo NÃO APROVADA no frame 0
    {"env": SALA, "camera": BUSTO, "duracao": 3.5,
     "atores": [{"quem": "jovem", "pos": [0, 0, 0], "pose": [[0, "volante"]], "expr": [[0, "feliz"], [2.0, "triste"]], "fala": True}],
     "objetos": [{"tipo": "volante", "pos": [0, 1.65, 0.75], "rot": [-0.4, 0, 0], "esc": 0.9},
                 {"tipo": "placa", "pos": [0.0, 3.3, 0.4], "rot": [0, 0, -0.12], "w": 1.7, "h": 0.5, "linhas": ["NÃO APROVADA"], "bg": "#e5202e", "fg": "#ffffff", "moldura": 0x8a0f19, "esc": 0.95, "entra": 0.0}],
     "sons": [{"t": 0.05, "tipo": "impact"}]},
    # 2 filho pede a chave
    {"env": SALA, "camera": DUO, "duracao": 3,
     "atores": [filho(pose="mostra", expr="feliz", fala=True), pai(pose="neutro", expr="cansado", olhar=[0.5, 0])],
     "objetos": [{"tipo": "chave", "pos": [0.0, 2.0, 0.9], "rot": [0, 0.3, 0], "esc": 1.1, "entra": 0.3, "balanca": 0.05}]},
    # 3 pai ri; placa Permissão para Dirigir
    {"env": SALA, "camera": DUO, "duracao": 3.5,
     "atores": [filho(pose="neutro", expr=[[0, "neutro"], [1.5, "triste"]]), pai(pose="quadril", expr="feliz", fala=True, salta=True)],
     "objetos": [{"tipo": "placa", "pos": [0, 4.0, 0.6], "w": 2.5, "h": 0.8, "linhas": ["PERMISSÃO", "PARA DIRIGIR"], "bg": "#2f6fe0", "fg": "#ffffff", "moldura": 0x16377a, "entra": 1.6}]},
    # 4 carro urbano, filho ao volante, pai de carona
    {"env": "rua", "camera": {"pos": [4.0, 2.0, 3.4], "look": [0, 1.25, 0], "fov": 36, "push": 0.08}, "duracao": 3.5,
     "atores": [{"quem": "jovem", "pos": [-0.05, 0.95, 0.28], "rotY": 1.25, "sentado": True, "esc": 0.62, "pose": "volante", "expr": "feliz", "fala": True},
                {"quem": "pai", "pos": [-0.05, 0.95, -0.28], "rotY": 1.25, "sentado": True, "esc": 0.62, "pose": "segura", "expr": "surpreso"}],
     "objetos": [{"tipo": "carro", "aberto": True, "pos": [0, 0, 0], "cor": 0x2f6fe0},
                 {"tipo": "placa", "pos": [1.2, 2.3, -2.2], "w": 1.7, "h": 0.9, "linhas": ["16 a 18", "anos"], "bg": "#ffffff", "poste": 2.3, "entra": 0.8}]},
    # 6 virada: rótulo vira conta
    {"env": SALA, "camera": DUO, "duracao": 5,
     "atores": [filho(pose="cruzado", expr=[[0, "bravo"], [2.4, "duvida"]], fala=True), pai(pose="aponta", expr="duvida")],
     "objetos": [{"tipo": "placa", "pos": [0, 3.95, 0.5], "w": 2.4, "h": 0.8, "linhas": ["JOVEM DESISTIU?"], "bg": "#f2c230", "fg": "#222", "entra": 0.2, "sai": 2.8},
                 {"tipo": "placa", "pos": [0, 3.95, 0.5], "w": 2.4, "h": 0.8, "linhas": ["A CONTA PESA"], "bg": "#ffffff", "fg": "#2f6fe0", "entra": 2.8}],
     "sons": [{"t": 2.8, "tipo": "ding"}]},
    # 7 preço cai sobre o filho
    {"env": SALA, "camera": DUO, "duracao": 4,
     "atores": [filho(pose="encolhe", expr="surpreso"), pai(pose="neutro", expr="surpreso", fala=True)],
     "objetos": [{"tipo": "placa", "pos": [0, 3.9, 0.7], "w": 2.4, "h": 0.9, "linhas": ["R$ 3.200"], "bg": "#e5202e", "fg": "#ffffff", "moldura": 0x8a0f19, "entra": 0.3,
                  "kf": [[0, [0, 7.5, 0.7]], [0.7, [0, 3.9, 0.7]]]}],
     "sons": [{"t": 0.9, "tipo": "impact"}]},
    # 8 barras 20 -> 2
    {"env": "estudio", "camera": BARRAS, "duracao": 4,
     "atores": [ator_b("jovem", pose="relax", expr="feliz", fala=True)],
     "objetos": [*barra(-0.75, 2.6, 0x8fb4f2, 0.2, ["20", "horas-aula"]), *barra(0.4, 0.26, 0xf2c230, 1.4, ["2", "horas-aula"])],
     "sons": [{"t": 1.4, "tipo": "ding"}]},
    # 9 pedidos 2,3 -> 7,3 milhões
    {"env": "estudio", "camera": BARRAS, "duracao": 4,
     "atores": [ator_b("jovem", pose="comemora", expr="feliz", salta=True, fala=True)],
     "objetos": [*barra(-0.75, 0.82, 0x8fb4f2, 0.2, "2,3 mi"), *barra(0.4, 2.6, 0x2f9e6e, 1.3, "7,3 mi"),
                 {"tipo": "rotulo", "pos": [-0.2, 4.0, 0.3], "linhas": ["jan-ago 2025 → 2026"], "w": 2.4, "hpx": 120, "entra": 0.3, "fg": "#dbe7ff"}],
     "sons": [{"t": 1.3, "tipo": "ding"}]},
    # 10 pedido não é carteira
    {"env": "estudio", "camera": BARRAS, "duracao": 4.5,
     "atores": [ator_b("jovem", pose="cabeca", expr="duvida", fala=True)],
     "objetos": [*barra(-0.75, 2.6, 0x2f9e6e, 0.2, ["pedidos", "+216%"]), *barra(0.4, 0.21, 0xe5202e, 1.2, ["emitidas", "+17,1%"]),
                 {"tipo": "rotulo", "pos": [1.4, 3.6, 0.3], "linhas": ["?"], "w": 0.8, "hpx": 220, "entra": 2.4}]},
    # 11 preço não é tudo (tom sério)
    {"env": SALA, "camera": DUO, "duracao": 3,
     "atores": [filho(pose="neutro", expr="neutro"), pai(pose="cruzado", expr="neutro", fala=True)],
     "objetos": [{"tipo": "placa", "pos": [0, 4.0, 0.5], "w": 2.5, "h": 0.8, "linhas": ["PREÇO NÃO É TUDO"], "bg": "#ffffff", "fg": "#14141a", "entra": 0.3},
                 {"tipo": "carro", "pos": [0, 0, 1.0], "esc": 0.4, "cor": 0xe5202e, "rot": [0, 0.6, 0], "entra": 0.8}]},
    # 12 risco 3x
    {"env": "estudio", "camera": BARRAS, "duracao": 4.5,
     "atores": [ator_b("pai", pose="neutro", expr="neutro", fala=True)],
     "objetos": [*barra(-0.75, 0.87, 0x8fb4f2, 0.2, ["20 ou mais", "1x"]), *barra(0.4, 2.6, 0xe5202e, 1.3, ["16 a 19", "3x"]),
                 {"tipo": "rotulo", "pos": [-0.2, 3.9, 0.3], "linhas": ["EUA · acidente fatal por milha"], "w": 2.4, "hpx": 120, "entra": 2.6, "fg": "#dbe7ff"}],
     "sons": [{"t": 1.3, "tipo": "impact"}]},
    # 13 pergunta final: carro e moto
    {"env": SALA, "camera": DUO, "duracao": 3.5,
     "atores": [filho(pose="pensa", expr="duvida", olhar=[-0.2, 0.1]), pai(pose="pensa", expr="duvida", olhar=[0.2, 0.1], fala=False)],
     "objetos": [{"tipo": "carro", "pos": [-1.0, 0, 1.0], "esc": 0.4, "cor": 0x2f6fe0, "rot": [0, 0.5, 0]},
                 {"tipo": "moto", "pos": [1.0, 0, 1.0], "esc": 0.55, "cor": 0xe5202e, "rot": [0, -0.5, 0]},
                 {"tipo": "rotulo", "pos": [0, 4.1, 0.4], "linhas": ["?"], "w": 1.0, "hpx": 260, "entra": 0.6}]},
]

assert len(cenas) == len(T), f"{len(cenas)} cenas, {len(T)} textos"
for c, t in zip(cenas, T):
    c["fala"] = t["fala"]
    c["legenda"] = t["legenda"]
    c["duracao"] = 2.0  # só o mínimo: a cena dura o que a fala dura
    c.setdefault("sons", [])
(AQUI / "cenas3d.json").write_text(json.dumps(cenas, ensure_ascii=False, indent=1), encoding="utf-8")
print("cenas3d.json:", len(cenas), "cenas")
