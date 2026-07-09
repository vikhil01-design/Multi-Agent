from crewai import Agent


def fundamentalAgent(llm) -> Agent:
    """Create a Fundamental Analysis Agent for the investment crew."""

    fundamental_agent = Agent(
        role="Fundamental Analysis Agent",
        goal=(
            "Evaluate the underlying financial health, earnings quality, cash flow, "
            "and valuation of the proposed investment assets."
        ),
        backstory=(
            "You specialize in company fundamentals and long-term durability. Your analysis "
            "should determine whether the selected assets are fundamentally sound and "
            "aligned with the investment thesis."
        ),
        llm=llm,
        verbose=True,
    )

    return fundamental_agent
