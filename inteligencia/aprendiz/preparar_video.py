"""Prepara um vídeo para o Busquets estudar: extrai quadros, conta cortes e transcreve a fala. Não gasta token.

Só trabalha com arquivo local que o Guilherme colocou em _entrada/. Não baixa nada da internet
(o único download possível é o do modelo Whisper, se ainda não estiver no computador).

Grava em <destino>/:
  manifesto.json    duração, cortes, quadros (arquivo, tempo, motivo) e nível de acesso
  q01_00m03s.jpg    quadros: gancho, viradas (cortes), intervalos regulares e final
  transcricao.txt   fala com tempo (pode ficar vazia, se não houver fala)

Uso: python inteligencia/aprendiz/preparar_video.py <arquivo> <destino>
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAX_QUADROS = 12
MAX_VIRADAS = 3
LIMIAR_CORTE = 0.05  # medido em 05/11: nosso sketch (fundo igual entre cenas) tem 6 cortes reais; 0.30 achava 0 e 0.05 acha os 6
MAX_ANALISE_SEG = 600  # vídeo longo: cortes e fala só dos primeiros 10 minutos
GANCHO = (0.5, 1.5, 3.0)
NIVEL_COMPLETO = "assistido com quadros e transcrição"
NIVEL_SEM_FALA = "só quadros: nenhuma fala reconhecida"


class ErroPreparo(Exception):
    """Falha que o relatório mostra ao Guilherme em texto simples."""


def _rodar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def duracao_de(arquivo):
    r = _rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(arquivo)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise ErroPreparo("o arquivo não abriu como vídeo (pode estar corrompido ou incompleto)") from None


def achar_cortes(arquivo):
    """Tempos dos cortes de cena nos primeiros 10 minutos."""
    r = _rodar(["ffmpeg", "-hide_banner", "-t", str(MAX_ANALISE_SEG), "-i", str(arquivo), "-an", "-vf",
                f"scale=320:-2,select='gt(scene,{LIMIAR_CORTE})',showinfo", "-f", "null", "-"])
    return [float(t) for t in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def escolher_tempos(duracao, cortes):
    """(tempo, motivo) do gancho, das viradas, de intervalos regulares e do final, sem quadros quase iguais."""
    fim = max(duracao - 0.5, 0.0)
    fixos = [(t, "gancho") for t in GANCHO if t < fim] or [(0.0, "gancho")]
    fixos.append((fim, "final"))
    meio = [t for t in cortes if GANCHO[-1] < t < fim]
    passo = max(len(meio) / MAX_VIRADAS, 1)
    viradas = [(meio[int(i * passo)], "virada (corte)") for i in range(min(MAX_VIRADAS, len(meio)))]
    vagas = max(MAX_QUADROS - len(fixos) - len(viradas), 0)
    intervalos = [(duracao * (i + 1) / (vagas + 1), "intervalo") for i in range(vagas)]

    escolhidos = []
    distancia = min(1.0, duracao / (MAX_QUADROS * 2))
    for t, motivo in fixos + viradas + intervalos:  # a ordem dá prioridade em caso de quadros muito próximos
        if all(abs(t - e[0]) >= distancia for e in escolhidos):
            escolhidos.append((round(t, 2), motivo))
    return sorted(escolhidos)


def extrair_quadros(arquivo, destino, tempos):
    quadros = []
    for n, (t, motivo) in enumerate(tempos, 1):
        nome = f"q{n:02d}_{int(t // 60):02d}m{int(t % 60):02d}s.jpg"
        r = _rodar(["ffmpeg", "-y", "-hide_banner", "-ss", str(t), "-i", str(arquivo), "-frames:v", "1",
                    "-vf", "scale='min(iw,720)':-2", "-q:v", "4", str(destino / nome)])
        if r.returncode == 0 and (destino / nome).exists():
            quadros.append({"arquivo": nome, "tempo": t, "motivo": motivo})
    if not quadros:
        raise ErroPreparo("não consegui tirar nenhum quadro (o arquivo pode não ter imagem)")
    return quadros


def carregar_modelo():
    from faster_whisper import WhisperModel
    try:
        return WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
    except Exception:  # noqa: BLE001  # modelo ainda não baixado neste computador
        return WhisperModel("small", device="cpu", compute_type="int8")


def transcrever(arquivo, destino):
    """Grava transcricao.txt. Devolve (há fala?, aviso ou None)."""
    wav = destino / "_audio.wav"
    alvo = destino / "transcricao.txt"
    alvo.write_text("", encoding="utf-8")
    r = _rodar(["ffmpeg", "-y", "-hide_banner", "-t", str(MAX_ANALISE_SEG), "-i", str(arquivo), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    if r.returncode != 0 or not wav.exists():
        return False, "o vídeo não tem áudio legível"
    try:
        segmentos, _ = carregar_modelo().transcribe(str(wav), beam_size=5, vad_filter=True)  # idioma detectado: o nicho aberto pode ser em inglês
        linhas = [f"[{int(s.start // 60):02d}:{int(s.start % 60):02d}] {s.text.strip()}" for s in segmentos]
    except Exception as e:  # noqa: BLE001  # falha de transcrição não impede o estudo dos quadros
        return False, f"a transcrição falhou: {str(e)[:150]}"
    finally:
        wav.unlink(missing_ok=True)
    alvo.write_text("\n".join(linhas), encoding="utf-8")
    return bool(linhas), None if linhas else "nenhuma fala reconhecida"


def preparar(arquivo, destino):
    """Devolve o manifesto. Levanta ErroPreparo se o arquivo não for utilizável."""
    arquivo, destino = Path(arquivo), Path(destino)
    if not arquivo.is_file():
        raise ErroPreparo(f"arquivo não encontrado: {arquivo}")
    for programa in ("ffmpeg", "ffprobe"):
        if not shutil.which(programa):
            raise ErroPreparo(f"{programa} não está instalado neste computador")
    duracao = duracao_de(arquivo)
    destino.mkdir(parents=True, exist_ok=True)
    for velho in destino.glob("q*.jpg"):  # preparo refeito não deixa quadro da tentativa anterior
        velho.unlink()
    cortes = achar_cortes(arquivo)
    quadros = extrair_quadros(arquivo, destino, escolher_tempos(duracao, cortes))
    tem_fala, aviso_fala = transcrever(arquivo, destino)
    analisado = min(duracao, MAX_ANALISE_SEG)
    avisos = [aviso_fala] if aviso_fala else []
    if duracao > MAX_ANALISE_SEG:
        avisos.append(f"vídeo longo: cortes e fala só dos primeiros {MAX_ANALISE_SEG // 60} minutos")
    manifesto = {
        "arquivo_origem": arquivo.name,
        "duracao_seg": round(duracao, 1),
        "cortes_detectados": len(cortes),  # estimativa pela diferença entre imagens
        "cortes_por_minuto": round(len(cortes) / (analisado / 60), 1) if analisado else 0,
        "nivel_acesso": NIVEL_COMPLETO if tem_fala else NIVEL_SEM_FALA,
        "avisos": avisos,
        "quadros": quadros,
    }
    (destino / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifesto


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        print(json.dumps(preparar(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=1))
    except ErroPreparo as e:
        sys.exit(f"Não preparei o vídeo: {e}")
