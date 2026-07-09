import os
import uuid

from state import InvestmentState
from llm import _create_llm
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ---------- Gateway Client ----------
client = OpenAI(base_url="http://localhost:11434", api_key="dummy-key")

MODEL_MAP = {
    "simple": "simple-tier",  # Ollama
    "complex": "complex-tier",  # GPT-4o-mini
}


def critic_node(state: InvestmentState):
    crew_response = state.get("crew_response", "")
    summary = str(crew_response)
    user_prompt = str(state.get("user_prompt", ""))

    retries = state.get("retries", 0)

    if retries >= 3:
        return {
            "critic_decision": "human_handoff",
            "retries": retries,
            "humanHandOff": True,
            "humanHandOffRef": uuid.uuid4().hex,  # Generate a unique reference for human handoff
        }

    evaluation_prompt = (
        "You are a strict evaluator. Judge whether the provided response answers the user's query. "
        "Respond with exactly one word: PASS or FAIL.\n\n"
        f"User Query: {user_prompt}\n\n"
        f"Response: {summary}"
    )

    try:

        complexity = assess_complexity(user_prompt)
        model = MODEL_MAP[complexity]
        if model == "simple-tier":
            llm_output = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": evaluation_prompt}]
            )
        else:
            llm = _create_llm()
            llm_output = llm.call(evaluation_prompt)

        decision = str(llm_output).strip().upper()
        if decision not in {"PASS", "FAIL"}:
            decision = "FAIL" if "fail" in decision.lower() else "PASS"
    except Exception:
        decision = "FAIL"

    decision_value = decision.lower()
    retries = state.get("retries", 0) + (0 if decision_value == "pass" else 1)

    return {
        "critic_decision": decision_value,
        "retries": retries,
    }


def assess_complexity(query: str) -> str:
    """
    Heuristic tuned for the investment-agent workflow.

    Queries that request portfolio reasoning, risk analysis, market evaluation,
    rebalancing, or strategy synthesis are treated as complex. Short factual
    questions about basic concepts are treated as simple.
    """

    if not query:
        return "simple"

    query_lower = query.lower().strip()
    word_count = len(query.split())

    finance_complex_keywords = [
        "analyze",
        "evaluate",
        "compare",
        "recommend",
        "strategy",
        "optimize",
        "portfolio",
        "risk",
        "market",
        "allocation",
        "rebalance",
        "volatility",
        "diversification",
        "asset",
        "return",
        "drawdown",
        "macro",
        "scenario",
        "forecast",
        "investment",
        "position",
        "trading",
    ]

    finance_simple_keywords = [
        "what is",
        "define",
        "explain",
        "who",
        "when",
        "where",
        "list",
        "basic",
        "overview",
        "meaning",
    ]

    if any(keyword in query_lower for keyword in finance_complex_keywords):
        return "complex"

    if (
        any(keyword in query_lower for keyword in finance_simple_keywords)
        and word_count <= 15
    ):
        return "simple"

    if word_count > 40:
        return "complex"

    return "simple"
