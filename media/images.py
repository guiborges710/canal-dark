"""Imagens por cena. Provedores (images.provider no config.yaml):

  commons     imagem REAL de arquivo livre (Wikimedia Commons, sem chave). Se não achar, usa images.fallback.
  cloudflare  Flux schnell na Cloudflare Workers AI (faixa gratuita; precisa de CF_ACCOUNT_ID e CF_API_TOKEN)
  fal         Flux schnell no fal.ai (pago; precisa de FAL_KEY)
  local_art   arte procedural por código (grátis, sem internet; é só demonstração)
"""
import base64
import os

import requests


def _mock_image(prompt, out_path, size=(1280, 720)):
    from PIL import Image, ImageDraw
    h = abs(hash(prompt))
    c1 = (h % 200 + 30, (h // 7) % 200 + 30, (h // 13) % 200 + 30)
    c2 = ((h // 3) % 120, (h // 5) % 120, (h // 11) % 120)
    img = Image.new("RGB", size, c1)
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        d.line([(0, y), (size[0], y)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    d.text((40, 40), prompt[:60], fill=(255, 255, 255))
    img.save(out_path, "JPEG")


def _fal(cfg, prompt, out_path):
    key = os.environ["FAL_KEY"]
    r = requests.post(f"https://fal.run/{cfg['images']['model']}",
                      headers={"Authorization": f"Key {key}"}, timeout=180,
                      json={"prompt": prompt, "image_size": cfg["images"]["image_size"],
                            "num_images": 1, "num_inference_steps": 4})
    r.raise_for_status()
    img = requests.get(r.json()["images"][0]["url"], timeout=180)
    img.raise_for_status()
    out_path.write_bytes(img.content)


def _cloudflare(cfg, prompt, out_path):
    """NÃO testado aqui (sem conta). Segue a documentação da Cloudflare: o resultado vem em base64."""
    acct, token = os.environ["CF_ACCOUNT_ID"], os.environ["CF_API_TOKEN"]
    r = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        headers={"Authorization": f"Bearer {token}"}, timeout=180,
        json={"prompt": prompt[:2000], "steps": 4})
    r.raise_for_status()
    out_path.write_bytes(base64.b64decode(r.json()["result"]["image"]))


def _local_art(cfg, prompt, out_path):
    from .art import paint
    paint(prompt).save(out_path, "JPEG", quality=92)


def generate(cfg, prompt, out_path, mock=False, queries=None):
    """Gera (ou baixa) a imagem da cena em out_path. 'queries' são buscas por imagem real, em inglês."""
    if out_path.exists():
        return
    if mock:
        _mock_image(prompt, out_path)
        return
    provider = cfg["images"].get("provider", "local_art")
    if provider == "commons":
        if queries:
            from . import commons
            try:
                if commons.fetch(cfg, queries, out_path):
                    return
            except Exception as e:  # sem internet, bloqueio etc.: segue para o provedor de reserva
                print(f"   (aviso) imagem real indisponível ({type(e).__name__}); usando a reserva")
        provider = cfg["images"].get("fallback", "local_art")
    gen = {"fal": _fal, "cloudflare": _cloudflare, "local_art": _local_art}[provider]
    try:
        gen(cfg, prompt, out_path)
    except Exception as e:
        # Um provedor de imagem pode falhar (conta, rede, cota). Em vez de derrubar o vídeo inteiro,
        # cai para a arte local gratuita e avisa — assim a produção sempre termina com um resultado aproveitável.
        if provider != "local_art":
            print(f"   (aviso) provedor de imagem '{provider}' falhou ({type(e).__name__}); usando local_art nesta cena")
            _local_art(cfg, prompt, out_path)
        else:
            raise
