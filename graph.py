from langgraph.graph import StateGraph, START, END

from nodes.handoff_service import send_handoff_email
from nodes.crew import investment_crew_node
from nodes.criticNode import critic_node
from state import InvestmentState
from nodes.conditionalNode import should_route


def build_graph():
    builder = StateGraph(InvestmentState)

    builder.add_node("crew", investment_crew_node)
    builder.add_node("critic", critic_node)
    builder.add_node("humanHandoff", send_handoff_email)

    builder.set_entry_point("crew")
    builder.add_edge("crew", "critic")
    builder.add_conditional_edges(
        "critic",
        should_route,
        {"revise": "crew", "humanHandoff": "humanHandoff", "finalize": END},
    )
    builder.add_edge("humanHandoff", END)

    return builder.compile()
