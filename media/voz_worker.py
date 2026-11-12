"""Narração por cena com Chatterbox (MIT, multilíngue, roda em CPU). Roda no ambiente .venv-voz (Python 3.13),
separado do pipeline. Chamado por media/voz.py; não é para rodar à mão no dia a dia.

Entrada: cenas.json (campo opcional "fala" em cada cena) e, se houver, uma amostra da voz do canal.
Saída: <out>/falas/NN.wav (48 kHz, mono, 16 bits) e <out>/falas/falas.json com a duração de cada fala.
"""
import argparse
import json
import re
import subprocess
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


# Padrões do ritmo (config_shorts.yaml, seção voz, sobrepõe todos eles).
PAUSA_ENTRE_FRASES = 0.10  # segundos entre frases dentro de uma fala
PAUSA_MAX = 0.18  # pausas internas maiores que isso são encurtadas para este valor
VELOCIDADE = 1.15  # 1.0 = como o modelo falou; acelera sem mudar o tom (ffmpeg atempo)
EXAGGERATION = 0.6  # expressividade (padrão do modelo: 0.5)
CFG_WEIGHT = 0.4  # peso da amostra (padrão do modelo: 0.5); mais baixo deixa o ritmo mais solto
CHARS_POR_SEGUNDO = 17.0  # ritmo típico de fala em português; referência para detectar fala "divagando"


def _frases(texto):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", texto) if p.strip()]


def afinar(x, sr, pausa_max):
    """Corta o silêncio do começo e do fim e encurta as pausas internas maiores que pausa_max (segundos).
    O modelo deixa uns 0,2 s de silêncio no fim de cada frase e pausas longas em vírgulas."""
    n = max(1, int(sr * 0.01))  # quadros de 10 ms
    k = len(x) // n
    if k == 0:
        return x
    quadros = x[:k * n].reshape(k, n)
    rms = np.sqrt((quadros ** 2).mean(axis=1))
    ativo = rms > max(0.003, 0.05 * np.percentile(rms, 95))
    if not ativo.any():
        return x
    ini = max(0, int(np.argmax(ativo)) - 2)  # deixa 20 ms antes da primeira palavra
    fim = min(k, k - int(np.argmax(ativo[::-1])) + 4)  # e 40 ms depois da última
    maximo = max(1, int(pausa_max / 0.01))
    manter, i = [], ini
    while i < fim:
        if ativo[i]:
            manter.append(i)
            i += 1
            continue
        j = i
        while j < fim and not ativo[j]:
            j += 1
        if j - i <= maximo:
            manter.extend(range(i, j))
        else:  # mantém o começo e o fim da pausa, para a voz não "cortar seco"
            metade = maximo // 2
            manter.extend(range(i, i + metade))
            manter.extend(range(j - (maximo - metade), j))
        i = j
    return quadros[manter].reshape(-1)


def acelerar(caminho, velocidade):
    """Acelera o WAV sem mudar o tom (atempo do ffmpeg)."""
    if abs(velocidade - 1.0) < 0.01:
        return
    tmp = caminho.with_suffix(".tmp.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(caminho), "-filter:a",
                    f"atempo={velocidade}", "-ar", str(SR_SAIDA), "-ac", "1", str(tmp)], check=True)
    tmp.replace(caminho)


def gerar_fala(model, texto, amostra, p):
    """Gera a fala frase por frase, porque o modelo às vezes alonga demais uma frase longa (a fala sai com o
    dobro do tempo, com trecho inventado). Cada frase é refeita, com outra amostragem, se ficar longa demais.
    Cada frase é aparada (sem silêncio nas pontas, pausas internas curtas) antes de juntar."""
    partes = []
    for frase in _frases(texto):
        esperado = len(frase) / CHARS_POR_SEGUNDO
        melhor = None
        for tentativa in range(3):
            wav = model.generate(frase, language_id="pt", audio_prompt_path=amostra,
                                 exaggeration=p.exaggeration, cfg_weight=p.cfg_weight,
                                 temperature=0.8 - 0.1 * tentativa)
            mono = wav.squeeze(0).cpu().numpy()
            dur = len(mono) / model.sr
            if melhor is None or dur < melhor[1]:
                melhor = (mono, dur)
            if dur <= 2.0 * esperado + 1.0:
                break
        partes.append(afinar(melhor[0], model.sr, p.pausa_max))
        partes.append(np.zeros(int(p.pausa_frase * model.sr), dtype=np.float32))
    return np.concatenate(partes[:-1]) if partes else np.zeros(1, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cenas", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--amostra", default="")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--velocidade", type=float, default=VELOCIDADE)
    ap.add_argument("--pausa-frase", dest="pausa_frase", type=float, default=PAUSA_ENTRE_FRASES)
    ap.add_argument("--pausa-max", dest="pausa_max", type=float, default=PAUSA_MAX)
    ap.add_argument("--exaggeration", type=float, default=EXAGGERATION)
    ap.add_argument("--cfg-weight", dest="cfg_weight", type=float, default=CFG_WEIGHT)
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
        mono = gerar_fala(model, fala, amostra, a)
        mono48 = torchaudio.functional.resample(torch.from_numpy(mono), model.sr, SR_SAIDA).numpy()
        destino = pasta / f"{i:02d}.wav"
        _salvar_wav(destino, mono48, SR_SAIDA)
        acelerar(destino, a.velocidade)
        with wave.open(str(destino)) as w:
            dur = w.getnframes() / w.getframerate()
        resultado[str(i)] = {"wav": str(destino), "dur": round(dur, 3)}
        print(f"   fala {i + 1}: {dur:.1f} s ({len(fala.split()) / dur:.1f} palavras/s)", flush=True)

    (pasta / "falas.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
