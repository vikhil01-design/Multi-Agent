from typing import TypedDict


class InvestmentState(TypedDict, total=False):
    user_prompt: str
    crew_response: str
    critic_decision: str
    retries: int
    humanHandOff: bool
    humanHandOffRef: str
