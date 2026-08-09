def format_response(kind: str, payload: dict, confidence: float, canon: dict | None = None) -> dict:
    return {
        "type": kind,
        "data": payload,
        "canon_validation": canon or {"passed": True, "warnings": []},
        "confidence": round(confidence, 4),
    }
