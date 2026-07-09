from crewai import Agent


def portfolioAgent(llm) -> Agent:

    portfolio_agent = Agent(
        role="Portfolio Optimization Agent",
        goal=(
            "Synthesize specialist analysis into a unified allocation recommendation "
            "that balances return potential with diversification and risk control."
        ),
        backstory=(
            "You combine the insights from market, fundamental, and risk analysis into a "
            "cohesive portfolio recommendation. Your focus is on allocation balance, diversification, "
            "and clear rationale."
        ),
        llm=llm,
        verbose=True,
    )

    return portfolio_agent
