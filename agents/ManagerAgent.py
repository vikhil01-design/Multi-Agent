from crewai import Agent
from llm import _create_llm


def ManagerAgent(llm) -> Agent:
    """Create a Manager Agent for the investment crew."""
    if llm is None:
        llm = _create_llm()

    manager_agent = Agent(
        role="Investment Strategy Manager",
        goal=(
            "Oversee the investment strategy process, ensuring that all analysis is "
            "cohesive, aligned with the investment thesis, and meets the stated objectives."
        ),
        backstory=(
            "You are responsible for coordinating the efforts of the fundamental, market, "
            "and risk assessment agents. Your task is to synthesize their insights into a "
            "clear and actionable investment strategy."
        ),
        llm=llm,
        verbose=True,
    )

    return manager_agent
