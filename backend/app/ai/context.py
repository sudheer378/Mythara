class ContextBuilder:
    def __init__(self, token_budget: int = 1800):
        self.token_budget = token_budget

    def build(self, chunks: list[dict]) -> dict:
        used = 0
        selected = []
        for chunk in chunks:
            approx_tokens = max(1, len(chunk["text"]) // 4)
            if used + approx_tokens > self.token_budget:
                continue
            selected.append(chunk)
            used += approx_tokens
        return {
            "context": "\n\n---\n\n".join(chunk["text"] for chunk in selected),
            "sources": sorted({chunk["source"] for chunk in selected}),
            "confidence": min(0.95, 0.35 + (0.12 * len(selected))),
        }
