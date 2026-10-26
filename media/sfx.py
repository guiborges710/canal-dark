"""Efeitos sonoros gerados por código, a partir dos eventos do render/ (eventos.json).

Impacto (grave com queda), ding (senoide com harmônico) e whoosh (ruído filtrado que sobe).
Determinístico: o ruído usa semente fixa, então o mesmo cenas.json gera sempre o mesmo áudio.
Sem voz, sem banco de áudio: tudo sai de conta.
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
SEED = 20261026


def _impacto(rng):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    fase = 45 * t + 95 * (1 - np.exp(-12 * t)) / 12  # varredura de 140 Hz até 45 Hz
    tom = np.sin(2 * np.pi * fase) * np.exp(-8 * t) * 0.9
    clique = rng.standard_normal(n) * np.exp(-80 * t) * 0.3
    return tom + clique


def _ding(_rng):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    env = np.exp(-6 * t)
    return (np.sin(2 * np.pi * 1320 * t) + 0.35 * np.sin(2 * np.pi * 1980 * t)) * env * 0.45


def _whoosh(rng):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    ruido = rng.standard_normal(n)
    saida = np.zeros(n)
    y = 0.0
    for i in range(n):
        a = 0.02 + 0.28 * (i / n)  # filtro passa-baixa que abre: o som sobe
        y += a * (ruido[i] - y)
        saida[i] = y
    env = np.sin(np.pi * t / 0.6) ** 1.5
    return saida * env * 1.6


SONS = {"impact": _impacto, "ding": _ding, "whoosh": _whoosh}


def build(eventos, total_frames, fps, out_wav):
    """Mistura os eventos num WAV estéreo de 16 bits com a duração do vídeo."""
    rng = np.random.default_rng(SEED)
    total = int(round(total_frames / fps * SR))
    mix = np.zeros(total)
    for ev in eventos:
        kind = ev["kind"]
        if kind not in SONS:
            raise ValueError(f"evento de som desconhecido: {kind}")
        start = int(ev["frame"] / fps * SR)
        som = SONS[kind](rng)
        end = min(total, start + len(som))
        mix[start:end] += som[: end - start]
    mix = np.tanh(mix * 0.9) * 0.85  # limitador suave, evita estouro
    estereo = np.stack([mix, mix], axis=1)
    pcm = (np.clip(estereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return Path(out_wav)
