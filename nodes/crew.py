from crewai import Task, Crew, Process
from llm import _create_llm
from agents import (
    MarketAgent,
    FundamentalAgent,
    RiskAgent,
    PortfolioAgent,
    ManagerAgent,
)


def build_investment_crew() -> Crew:
    """Build the autonomous investment crew for the LangGraph node."""

    llm = _create_llm()

    market_agent = MarketAgent(llm=llm)
    fundamental_agent = FundamentalAgent(llm=llm)
    risk_agent = RiskAgent(llm=llm)
    portfolio_agent = PortfolioAgent(llm=llm)
    manager_agent = ManagerAgent(llm=llm)

    return Crew(
        agents=[market_agent, fundamental_agent, risk_agent, portfolio_agent],
        tasks=[],
        process=Process.hierarchical,
        manager_agent=manager_agent,
        verbose=True,
        tracing=True,
    )


def investment_crew_node(state: dict) -> dict:
    """LangGraph node that executes the investment crew on the user query."""
    crew = build_investment_crew()
    user_prompt = state.get("user_prompt", "Evaluate the investment opportunity.")
    previous_response = state.get("crew_response", "")

    retry_context = ""
    if previous_response:
        retry_context = (
            "You previously produced this response and it was judged insufficient. "
            f"Please review it carefully and avoid repeating the same mistake. "
            f"Previous response: {previous_response}"
        )

    task = Task(
        description=(
            f"User query: {user_prompt}\n\n"
            f"{retry_context}\n"
            "Please produce a better answer that directly addresses the user query, includes "
            "a coordinated investment strategy with allocation guidance, risk rationale, "
            "and a final portfolio recommendation."
        ),
        expected_output=(
            "A short but complete investment strategy response with clear allocation guidance."
        ),
    )
    crew.tasks = [task]

    try:
        result = crew.kickoff()
        response_text = str(result)
    except Exception as exc:
        response_text = f"Crew execution failed: {exc}"

    return {
        "crew_response": response_text,
        "user_prompt": user_prompt,
    }
