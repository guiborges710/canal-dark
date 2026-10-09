"""Edição com FFmpeg: movimento de câmera em cada imagem, áudio por cena, legendas, música com ducking e loudnorm."""
import functools
import subprocess
from pathlib import Path

from .util import run

ROOT = Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=None)
def has_filter(name):
    """True se este ffmpeg tem o filtro pedido (ex.: 'subtitles' exige libass na compilação)."""
    try:
        out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    except Exception:
        return False
    return f" {name} " in out


def _srt_time(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02}:{m:02}:{int(s):02},{int((s % 1) * 1000):03}"


def build_srt(scenes, durs, pause, max_words=7):
    t, n, lines = 0.0, 1, []
    for sc, d in zip(scenes, durs):
        words = sc["text"].split()
        chunks = [words[i:i + max_words] for i in range(0, len(words), max_words)]
        speak = max(0.1, d - pause)
        cur = t
        for ch in chunks:
            dur = speak * len(ch) / max(1, len(words))
            lines.append(f"{n}\n{_srt_time(cur)} --> {_srt_time(cur + dur)}\n{' '.join(ch)}\n")
            cur += dur
            n += 1
        t += d
    return "\n".join(lines)


def scene_clip(cfg, img, audio, dur, out, idx):
    r = cfg["render"]
    w, h, fps = r["width"], r["height"], r["fps"]
    frames = int(dur * fps) + 1
    # zoom in nas cenas pares, zoom out nas ímpares (sem vírgulas, para não precisar escapar no filtro)
    z = f"1+0.15*on/{frames}" if idx % 2 == 0 else f"1.15-0.15*on/{frames}"
    vf = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={fps},"
          f"format=yuv420p")
    run(["ffmpeg", "-y", "-i", str(img), "-i", str(audio), "-vf", vf,
         "-af", "apad,aresample=48000", "-t", f"{dur:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(fps),
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", str(out)])


def assemble(cfg, clips, outdir, final_name="video.mp4", srt_text=None, captions=None, total=0.0):
    r = cfg["render"]
    joined = outdir / "clips" / "joined.mp4"
    (outdir / "clips" / "list.txt").write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "joined.mp4"],
        cwd=outdir / "clips")

    music = r.get("music_file") or ""
    if music and not Path(music).is_absolute():
        music = str(ROOT / music)  # relativo à pasta do projeto, não à pasta do vídeo
    # A legenda sempre vai para captions.srt (dá para subir como faixa separada no YouTube).
    if srt_text:
        (outdir / "captions.srt").write_text(srt_text, encoding="utf-8")
    # O texto na tela estilo "viral" é uma SEQUÊNCIA de frames PNG (gerada pelo media/captions.py
    # com Pillow: poucas palavras, palavra falada em destaque, pop de escala). Entra como UM único
    # input (demuxer image2) + UM único overlay — memória constante, sem libass/drawtext no build.
    # `captions`, quando presente, é a tupla (dir_frames, fps, n_frames).
    use_caps = bool(captions)
    cap_dir = cap_fps = None
    if use_caps:
        cap_dir, cap_fps, _ = captions

    cmd = ["ffmpeg", "-y", "-i", str(joined)]
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
    base = 2 if music else 1  # índice do input de legenda entre os inputs do ffmpeg
    if use_caps:
        cmd += ["-framerate", str(cap_fps), "-i", str(cap_dir / "%05d.png")]
    fc = []
    if use_caps:
        # Compõe a sequência de legendas sobre o vídeo num overlay só. Os PNGs já têm o texto
        # posicionado no quadro inteiro e são transparentes onde não há legenda.
        fc.append(f"[0:v][{base}:v]overlay=0:0:shortest=1[vout]")
    if music:
        mv = r.get("music_volume", 0.15)
        fc.append("[0:a]asplit=2[asrc1][asrc2]")
        fc.append(f"[1:a]volume={mv}[m]")
        fc.append("[m][asrc1]sidechaincompress=threshold=0.05:ratio=10:attack=20:release=500[duck]")
        fc.append("[asrc2][duck]amix=inputs=2:duration=first:dropout_transition=0[mix]")
        fc.append("[mix]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    else:
        fc.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    cmd += ["-filter_complex", ";".join(fc)]
    cmd += ["-map", "[vout]" if use_caps else "0:v", "-map", "[aout]"]
    if use_caps:
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p"]
    else:
        cmd += ["-c:v", "copy"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    if total:
        cmd += ["-t", f"{total:.3f}"]
    cmd += ["-movflags", "+faststart", final_name]
    run(cmd, cwd=outdir)
    return outdir / final_name
