# Catálogo de ferramentas de IA para produção

Mantido pelo **Garro**. Atualizado a cada ciclo. Veredito: `recomendada`, `observar` ou `descartada` (com motivo). Preço: `GRATUITO`, `GRATUITO COM LIMITE` ou `PAGO`.

Último ciclo: [2026-11-09](2026-11-09.md). Detalhe de cada item (encaixe, termos, riscos) está no arquivo do ciclo. Todos os links abaixo foram abertos em 2026-11-09 (`verificado`), salvo nota.

## Geração de vídeo

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| Wan2.2 | GRATUITO (Apache-2.0) | Texto/imagem para vídeo; 5B pede 24 GB de VRAM | Clipes de fundo na colagem; pesado | observar | [repo](https://github.com/Wan-Video/Wan2.2) | 2026-11-09 |
| LTX-2 / 2.5 | Código Apache-2.0; pesos em licença comunitária (termos não lidos) | Vídeo com áudio sincronizado | Idem; ler licença antes | observar | [repo](https://github.com/Lightricks/LTX-2) | 2026-11-09 |
| LTX-Video 0.9.x | sem desenvolvimento ativo | Antecessor do LTX-2 | Usar o LTX-2 | descartada (substituída) | [repo](https://github.com/Lightricks/LTX-Video) | 2026-11-09 |

## Geração de imagem

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| FLUX.1 schnell | GRATUITO (Apache-2.0; o dev é não comercial) | Imagem por texto | Fundos para colagem e miniatura | recomendada (testar) | [repo](https://github.com/black-forest-labs/flux) | 2026-11-09 |
| Qwen-Image | GRATUITO (Apache-2.0) | Imagem 20B, bom em texto, edição | Cartazes e fundos | observar | [repo](https://github.com/QwenLM/Qwen-Image) | 2026-11-09 |
| ComfyUI | GRATUITO (GPL-3.0) | Painel em nós para rodar modelos locais | Banco de testes (usar por API, não misturar código) | recomendada (painel de teste) | [repo](https://github.com/Comfy-Org/ComfyUI) | 2026-11-09 |

## Voz, TTS e clonagem

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| Chatterbox Multilingual V3 | GRATUITO (MIT) | Clonagem de voz, pt-br e pt-pt; **aposentado**; marca d'água PerTh | Voz atual do canal; testar V3 pt-br | recomendada (testar), com alerta | [repo](https://github.com/resemble-ai/chatterbox) | 2026-11-09 |
| Kokoro-82M | GRATUITO (Apache-2.0) | TTS leve com pt-BR; sem clonagem | Voz reserva para prévias | observar | [repo](https://github.com/hexgrad/kokoro) | 2026-11-09 |
| F5-TTS | Código MIT, pesos CC-BY-NC | Clonagem | Não pode monetizar | descartada: pesos não comerciais, sem pt-BR confirmado (2026-11-09) | [repo](https://github.com/SWivid/F5-TTS) | 2026-11-09 |
| Piper | GRATUITO (MIT) | TTS local rápido | Voz não clona; repositório arquivado em 2025-10-06 (continua em outro repositório, não aberto) | observar (vozes pt não confirmadas) | [repo arquivado](https://github.com/rhasspy/piper) | 2026-11-09 |

## Animação

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| Remotion | GRATUITO COM LIMITE (empresa grande paga) | Vídeo em React | Já temos motor próprio; só referência | observar | [repo](https://github.com/remotion-dev/remotion) · [licença](https://www.remotion.dev/license) | 2026-11-09 |
| Motion Canvas | GRATUITO (MIT) | Animação vetorial em TypeScript | Inspiração para linha do tempo | observar | [repo](https://github.com/motion-canvas/motion-canvas) | 2026-11-09 |

## Edição automática

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| Auto-Editor | GRATUITO (Unlicense) | Corta silêncio e trechos parados | Pouco útil: a narração já é controlada | observar | [repo](https://github.com/WyattBlue/auto-editor) | 2026-11-09 |

## Legenda

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| faster-whisper | GRATUITO (MIT) | Transcrição com tempo por palavra | Legenda no meio do quadro, palavra a palavra | recomendada | [repo](https://github.com/SYSTRAN/faster-whisper) | 2026-11-09 |
| WhisperX | GRATUITO (BSD-2) | Alinhamento de palavra mais exato | Se o item acima for impreciso; pt não confirmado | observar | [repo](https://github.com/m-bain/whisperX) | 2026-11-09 |

## Música e sons

| Ferramenta | Preço | O que faz | Encaixe no pipeline | Veredito | Link | Checado em |
|---|---|---|---|---|---|---|
| ACE-Step 1.5 | GRATUITO (MIT) | Música local por texto; roda com pouca VRAM | Trilha de fundo dos Shorts | recomendada (testar) | [repo](https://github.com/ace-step/ACE-Step-1.5) | 2026-11-09 |
| ACE-Step v1 | GRATUITO (Apache-2.0) | Versão anterior | Usar a 1.5 | descartada (substituída) | [repo](https://github.com/ace-step/ACE-Step) | 2026-11-09 |
| Stable Audio Open (stable-audio-tools) | Código MIT; termos do modelo no Hugging Face **não lidos** | Áudio/música por texto | Possível efeito sonoro | observar (termos comerciais não verificados) | [repo](https://github.com/Stability-AI/stable-audio-tools) | 2026-11-09 |
| AudioCraft (MusicGen/AudioGen) | Código MIT, pesos CC-BY-NC | Música e som | Não pode monetizar | descartada: pesos não comerciais (2026-11-09) | [repo](https://github.com/facebookresearch/audiocraft) | 2026-11-09 |

## Descartadas (histórico)

| Ferramenta | Motivo | Data |
|---|---|---|
| F5-TTS | Pesos CC-BY-NC (não comercial); sem pt-BR confirmado | 2026-11-09 |
| AudioCraft / MusicGen | Pesos CC-BY-NC 4.0 | 2026-11-09 |
| LTX-Video 0.9.x | Sem desenvolvimento ativo; substituído por LTX-2.x | 2026-11-09 |
| ACE-Step v1 | Substituído pela 1.5 | 2026-11-09 |
