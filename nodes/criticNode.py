import uuid

from state import InvestmentState
from llm import _create_llm


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
