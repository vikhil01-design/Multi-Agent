from state import InvestmentState


def should_route(state: InvestmentState) -> str:
    if state.get("critic_decision") == "FAIL":
        return "revise"
    elif state.get("critic_decision") == "human_handoff":
        return "humanHandoff"
    else:
        return "finalize"
