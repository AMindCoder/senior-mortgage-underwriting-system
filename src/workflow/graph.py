"""Build and compile the LangGraph underwriting workflow."""

import functools

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.agents.asset_analyst import asset_analyst_node
from src.agents.collateral_analyst import collateral_analyst_node
from src.agents.credit_analyst import credit_analyst_node
from src.agents.critic import critic_agent_node
from src.agents.decision import decision_agent_node
from src.agents.income_analyst import income_analyst_node
from src.agents.supervisor import (
    initialize_application,
    should_continue_to_agents,
    supervisor_node,
)
from src.core.llm import get_llm
from src.core.state import UnderwritingState
from src.rag.policy_store import create_policy_store


def build_graph(policy_store=None, llm=None):
    """Construct and compile the underwriting StateGraph.

    Args:
        policy_store: Optional pre-built Chroma vector store.
            Created automatically if not provided.
        llm: Optional pre-configured ChatOpenAI instance.
            Created automatically if not provided.

    Returns:
        Compiled LangGraph graph with MemorySaver checkpointer.
    """
    if policy_store is None:
        policy_store = create_policy_store()
    if llm is None:
        llm = get_llm()

    # Bind shared dependencies to agent nodes via functools.partial
    credit_node = functools.partial(
        credit_analyst_node, policy_store=policy_store, llm=llm
    )
    income_node = functools.partial(
        income_analyst_node, policy_store=policy_store, llm=llm
    )
    asset_node = functools.partial(
        asset_analyst_node, policy_store=policy_store, llm=llm
    )
    collateral_node = functools.partial(
        collateral_analyst_node, policy_store=policy_store, llm=llm
    )
    critic_node = functools.partial(critic_agent_node, llm=llm)
    decision_node = functools.partial(decision_agent_node, llm=llm)

    # Build the graph
    workflow = StateGraph(UnderwritingState)

    workflow.add_node("initialize", initialize_application)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("credit", credit_node)
    workflow.add_node("income", income_node)
    workflow.add_node("asset", asset_node)
    workflow.add_node("collateral", collateral_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("decision", decision_node)

    # Define flow
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "supervisor")

    # Conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        should_continue_to_agents,
        {
            "credit": "credit",
            "income": "income",
            "asset": "asset",
            "collateral": "collateral",
            "critic": "critic",
        },
    )

    # All specialist agents return to supervisor
    workflow.add_edge("credit", "supervisor")
    workflow.add_edge("income", "supervisor")
    workflow.add_edge("asset", "supervisor")
    workflow.add_edge("collateral", "supervisor")

    # Critic flows to decision, decision ends
    workflow.add_edge("critic", "decision")
    workflow.add_edge("decision", END)

    # Compile with checkpointing
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph
