"""Confere um MP4 exportado contra a prévia do editor: quadro no mesmo timecode (PSNR) e áudio (correlação e atraso).
Uso: python comparar_midia.py <mp4> <prévia.png> <quadro> <prévia2.png> <quadro2> <áudio da prévia.wav> <fps>. Imprime JSON."""
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image


def quadro(mp4, f, fps, pasta):
    """Decodifica o quadro exato: seleciona pelo número, sem depender de -ss."""
    d = Path(pasta) / f"q{f}.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", f"select=eq(n\\,{f})", "-frames:v", "1", "-fps_mode", "passthrough", str(d)], check=True)
    return np.asarray(Image.open(d).convert("RGB"), dtype=float)


def psnr(a, b):
    m = ((a - b) ** 2).mean()
    return round(float(10 * np.log10(255 ** 2 / max(m, 1e-9))), 2)


def wav(p):
    with wave.open(str(p), "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
        return x.reshape(-1, w.getnchannels()).mean(axis=1), w.getframerate()


def main(mp4, p1, f1, p2, f2, audio, fps):
    with tempfile.TemporaryDirectory() as d:
        a1, a2 = np.asarray(Image.open(p1).convert("RGB"), dtype=float), np.asarray(Image.open(p2).convert("RGB"), dtype=float)
        q1, q2 = quadro(mp4, int(f1), fps, d), quadro(mp4, int(f2), fps, d)
        fora = quadro(mp4, max(0, int(f2) - 120), fps, d)
        saida = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(saida)], check=True)
        x, sr = wav(saida)
    y, sr2 = wav(audio)
    assert sr == sr2
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    # Atraso por correlação cruzada em um trecho central (o AAC acrescenta um pequeno atraso de codificação).
    ini, tam = n // 3, min(sr * 6, n // 3)
    a, b = x[ini:ini + tam], y[ini:ini + tam]
    tamanho = 1 << int(np.ceil(np.log2(2 * tam)))
    cc = np.fft.irfft(np.fft.rfft(a, tamanho) * np.conj(np.fft.rfft(b, tamanho)))
    atraso = int(np.argmax(np.abs(cc)))
    if atraso > tamanho // 2:
        atraso -= tamanho
    alinhado = np.roll(y, atraso)
    correl = float(np.corrcoef(x[sr:n - sr], alinhado[sr:n - sr])[0, 1])
    print(json.dumps({"psnr_editado": psnr(a1, q1), "psnr_sem_edicao": psnr(a2, q2), "quadro_errado_psnr": psnr(a2, fora), "audio_correl": round(correl, 4), "audio_atraso_ms": round(1000 * atraso / sr, 1)}))


if __name__ == "__main__":
    main(*sys.argv[1:])
