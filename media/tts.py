"""Narração por cena com o Google Cloud Text-to-Speech (um áudio por cena = sincronia exata, sem Whisper)."""
import base64
import os
import threading
from pathlib import Path

import requests

from .util import run

ROOT = Path(__file__).resolve().parent.parent
_KOKORO = None
_LOCK = threading.Lock()

API = "https://texttospeech.googleapis.com/v1"


def _kokoro_model(cfg):
    global _KOKORO
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        t = cfg["tts"]
        _KOKORO = Kokoro(str(ROOT / t["model_path"]), str(ROOT / t["voices_path"]))
    return _KOKORO


def _synth_kokoro(cfg, text, out_path):
    import soundfile as sf
    t = cfg["tts"]
    with _LOCK:  # o modelo local sintetiza uma cena por vez
        samples, sr = _kokoro_model(cfg).create(text, voice=t["voice"], speed=t.get("speaking_rate", 1.0),
                                                lang=t.get("kokoro_lang", "pt-br"))
    wav = out_path.with_suffix(".wav")
    sf.write(str(wav), samples, sr)
    run(["ffmpeg", "-y", "-i", str(wav), "-ar", "24000", "-ac", "1", "-q:a", "3", str(out_path)])
    wav.unlink()


def list_voices(cfg):
    if cfg["tts"].get("provider") == "kokoro":
        return sorted(_kokoro_model(cfg).get_voices())
    key = os.environ["GOOGLE_TTS_API_KEY"]
    lang = cfg["tts"]["language_code"]
    r = requests.get(f"{API}/voices", params={"languageCode": lang, "key": key}, timeout=30)
    r.raise_for_status()
    return sorted(v["name"] for v in r.json().get("voices", []))


def synth(cfg, text, out_path, mock=False):
    if out_path.exists():
        return
    if mock:  # tom senoidal com duração proporcional ao texto
        secs = max(1.5, len(text.split()) / 2.5)
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={secs}",
             "-ar", "24000", "-ac", "1", "-q:a", "4", str(out_path)])
        return
    if cfg["tts"].get("provider") == "kokoro":
        _synth_kokoro(cfg, text, out_path)
        return
    key = os.environ["GOOGLE_TTS_API_KEY"]
    t = cfg["tts"]
    audio_cfg = {"audioEncoding": "MP3"}
    if t.get("speaking_rate", 1.0) != 1.0:
        audio_cfg["speakingRate"] = t["speaking_rate"]
    body = {"input": {"text": text},
            "voice": {"languageCode": t["language_code"], "name": t["voice"]},
            "audioConfig": audio_cfg}
    r = requests.post(f"{API}/text:synthesize", params={"key": key}, json=body, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(base64.b64decode(r.json()["audioContent"]))
