from crewai import Agent


def riskAgent(llm) -> Agent:
    """Create a Risk Assessment Agent for the investment crew."""

    risk_agent = Agent(
        role="Risk Assessment Agent",
        goal=(
            "Assess downside exposure, volatility, and portfolio risk relative to the "
            "stated risk tolerance and investment horizon."
        ),
        backstory=(
            "You quantify risk factors and stress-test scenarios. Your task is to identify "
            "concentration risks, drawdown scenarios, and guardrails for a responsible strategy."
        ),
        llm=llm,
        verbose=True,
    )

    return risk_agent
