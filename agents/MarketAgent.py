from crewai import Agent


def MarketAgent(llm) -> Agent:
    """Create a Market Analysis Agent for the investment crew."""

    market_agent = Agent(
        role="Market Analysis Agent",
        goal=(
            "Analyze market trends, sentiment, and macroeconomic signals relevant "
            "to the investment opportunity."
        ),
        backstory=(
            "You are a market expert tracking sector momentum, volatility, and broader "
            "economic forces. Your recommendations should clarify whether the current "
            "environment supports the requested investment strategy."
        ),
        llm=llm,
        verbose=True,
    )

    return market_agent
