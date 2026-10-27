"""Narração por cena com Chatterbox (MIT, multilíngue, roda em CPU). Roda no ambiente .venv-voz (Python 3.13),
separado do pipeline. Chamado por media/voz.py; não é para rodar à mão no dia a dia.

Entrada: cenas.json (campo opcional "fala" em cada cena) e, se houver, uma amostra da voz do canal.
Saída: <out>/falas/NN.wav (48 kHz, mono, 16 bits) e <out>/falas/falas.json com a duração de cada fala.
"""
import argparse
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np
import torch
import torchaudio

# Os pesos do Chatterbox foram salvos em CUDA. Aqui carregamos tudo na CPU.
# Nesta máquina (12 GB de RAM) o carregamento pode estourar a memória comprometida do Windows.
# mmap=True foi testado e causa segfault com este modelo; por isso não é usado.
_load = torch.load
torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": torch.device("cpu")})

# O tokenizador carrega o segmentador de chinês (pkuseg) mesmo para português, e ele estoura a memória
# em máquinas com pouca RAM livre. Bloqueamos o import: o próprio Chatterbox trata ImportError e segue sem ele.
sys.modules["spacy_pkuseg"] = None

from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # noqa: E402

SR_SAIDA = 48000


def _salvar_wav(caminho, pcm_float, sr):
    pcm = (np.clip(pcm_float, -1, 1) * 32767).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


PAUSA_ENTRE_FRASES = 0.25  # segundos
CHARS_POR_SEGUNDO = 17.0  # ritmo típico de fala em português; referência para detectar fala "divagando"


def _frases(texto):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", texto) if p.strip()]


def gerar_fala(model, texto, amostra):
    """Gera a fala frase por frase, porque o modelo às vezes alonga demais uma frase longa (a fala sai com o
    dobro do tempo, com trecho inventado). Cada frase é refeita, com outra amostragem, se ficar longa demais."""
    partes = []
    for frase in _frases(texto):
        esperado = len(frase) / CHARS_POR_SEGUNDO
        melhor = None
        for tentativa in range(3):
            wav = model.generate(frase, language_id="pt", audio_prompt_path=amostra,
                                 temperature=0.8 - 0.1 * tentativa)
            mono = wav.squeeze(0).cpu()
            dur = mono.shape[-1] / model.sr
            if melhor is None or dur < melhor[1]:
                melhor = (mono, dur)
            if dur <= 2.0 * esperado + 1.0:
                break
        partes.append(melhor[0])
        partes.append(torch.zeros(int(PAUSA_ENTRE_FRASES * model.sr)))
    return torch.cat(partes[:-1]) if partes else torch.zeros(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--amostra", default="")
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()

    torch.set_num_threads(a.threads)
    cenas = json.loads(Path(a.cenas).read_text(encoding="utf-8"))
    pasta = Path(a.out) / "falas"
    pasta.mkdir(parents=True, exist_ok=True)

    model = ChatterboxMultilingualTTS.from_pretrained(device=torch.device("cpu"))
    amostra = a.amostra if a.amostra and Path(a.amostra).exists() else None
    if not amostra:
        print("   (voz) sem amostra da voz do canal: usando a voz padrão do modelo", flush=True)

    resultado = {}
    for i, c in enumerate(cenas):
        fala = (c.get("fala") or "").strip()
        if not fala:
            continue
        mono = gerar_fala(model, fala, amostra)
        mono48 = torchaudio.functional.resample(mono, model.sr, SR_SAIDA).numpy()
        destino = pasta / f"{i:02d}.wav"
        _salvar_wav(destino, mono48, SR_SAIDA)
        resultado[str(i)] = {"wav": str(destino), "dur": round(len(mono48) / SR_SAIDA, 3)}
        print(f"   fala {i + 1}: {len(mono48) / SR_SAIDA:.1f} s", flush=True)

    (pasta / "falas.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
