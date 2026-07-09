import re
from llm import _create_llm

HIGH_RISK_PATTERNS = [
    r"\bguarantee(?:d)?\b",
    r"\b100\s*%\b",
    r"\bdouble\b",
    r"\bmake\s+money\s+fast\b",
    r"\bquick\s+profit\b",
    r"\binstant\s+profit\b",
    r"\bwin\s+big\b",
    r"\b(?:buy|sell|trade|invest)\s+(?:now|today|tomorrow)\b",
    r"\bgive\s+me\s+a\s+(?:stock|crypto|coin|forex|option)\b",
    r"\b(?:best|top|hot|sure|safe)\s+(?:stock|trade|pick|investment)\b",
]


def guardrail_check(query: str) -> dict:
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        return {
            "allowed": False,
            "reason": "Empty query is not allowed",
            "mode": "heuristic",
        }

    lowered = cleaned_query.lower()
    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, lowered):
            return {
                "allowed": False,
                "reason": "The request appears to ask for high-risk or guaranteed financial advice.",
                "mode": "heuristic",
            }

    try:
        llm = _create_llm()
        prompt = (
            "You are a safety guardrail for an investment research assistant. "
            "Decide whether the user's request is safe to process. "
            "Return exactly one word: ALLOW or BLOCK.\n\n"
            "Block requests that ask for guaranteed profits, guaranteed stock picks, "
            "high-risk speculative advice, or manipulative '100% gain today' style prompts. "
            "Allow normal research, analysis, or educational questions.\n\n"
            f"User request: {cleaned_query}"
        )
        decision = str(llm.call(prompt)).strip().upper()
        if decision == "BLOCK":
            return {
                "allowed": False,
                "reason": "The request was blocked by the safety guardrail.",
                "mode": "llm",
            }
        return {
            "allowed": True,
            "reason": "Request passed the safety guardrail.",
            "mode": "llm",
        }
    except Exception:
        return {
            "allowed": True,
            "reason": "LLM guardrail unavailable; allowing request based on local heuristics.",
            "mode": "heuristic",
        }
