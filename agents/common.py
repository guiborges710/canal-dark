from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


def prompt(name, **vars):
    """Carrega prompts/<name>.md e troca os marcadores <<chave>> pelos valores."""
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    for k, v in vars.items():
        text = text.replace(f"<<{k}>>", str(v))
    return text
