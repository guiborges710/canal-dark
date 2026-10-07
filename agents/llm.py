"""Camada única de acesso ao Claude: roteia modelo por 'tier', conta tokens e custo."""
import json
import re
import time


def parse_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S).strip()
    m = re.search(r"[\[{]", t)
    if not m:
        raise ValueError("Resposta sem JSON: " + text[:200])
    t = t[m.start():]
    end = max(t.rfind("}"), t.rfind("]"))
    return json.loads(t[: end + 1])


class LLM:
    def __init__(self, cfg, mock=False):
        self.cfg = cfg
        self.mock = mock
        self.usage = {}  # modelo -> [tokens_in, tokens_out]
        self._client = None

    def _c(self):
        if self._client is None:
            import anthropic  # importado só no modo real
            self._client = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY
        return self._client

    def ask(self, agent, system, user, max_tokens=4000, web=False, mock_reply=""):
        if self.mock:
            return mock_reply
        model = self.cfg["models"][self.cfg["tiers"][agent]]
        kwargs = dict(model=model, max_tokens=max_tokens, system=system,
                      messages=[{"role": "user", "content": user}])
        if web:
            kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]
        for attempt in range(3):
            try:
                r = self._c().messages.create(**kwargs)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
        u = self.usage.setdefault(model, [0, 0])
        u[0] += r.usage.input_tokens
        u[1] += r.usage.output_tokens
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")

    def ask_json(self, agent, system, user, max_tokens=4000, mock_reply=""):
        raw = self.ask(agent, system, user, max_tokens, mock_reply=mock_reply)
        try:
            return parse_json(raw)
        except Exception:
            raw = self.ask(agent, system, user + "\n\nResponda SOMENTE com JSON válido.", max_tokens,
                           mock_reply=mock_reply)
            return parse_json(raw)

    def cost_usd(self):
        prices = self.cfg["prices"]["llm_per_mtok"]
        total = 0.0
        for model, (i, o) in self.usage.items():
            p = prices.get(model, {"in": 0, "out": 0})
            total += i / 1e6 * p["in"] + o / 1e6 * p["out"]
        return round(total, 4)
