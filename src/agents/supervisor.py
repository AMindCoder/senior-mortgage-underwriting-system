from datetime import datetime

from src.core.compliance import sanitize_pii
from src.core.state import UnderwritingState


def initialize_application(state: UnderwritingState) -> dict:
    """Initialize a new application with sanitized data."""
    sanitized = sanitize_pii(state["applicant_data"])

    return {
        "sanitized_data": sanitized,
        "analysis_complete": False,
        "human_review_required": False,
        "human_review_completed": False,
        "bias_flags": [],
        "policy_violations": [],
        "reasoning_chain": [f"Application {state.get('case_id')} initialized"],
        "timestamp": datetime.now().isoformat(),
    }


def supervisor_node(state: UnderwritingState) -> dict:
    """Route workflow to next agent or mark completion."""
    analyses_done = {
        "credit": state.get("credit_analysis") is not None,
        "income": state.get("income_analysis") is not None,
        "asset": state.get("asset_analysis") is not None,
        "collateral": state.get("collateral_analysis") is not None,
    }

    if not analyses_done["credit"]:
        next_agent = "credit"
    elif not analyses_done["income"]:
        next_agent = "income"
    elif not analyses_done["asset"]:
        next_agent = "asset"
    elif not analyses_done["collateral"]:
        next_agent = "collateral"
    else:
        next_agent = "critic"

    return {
        "next_agent": next_agent,
        "analysis_complete": all(analyses_done.values()),
    }


def should_continue_to_agents(state: UnderwritingState) -> str:
    """Conditional routing: continue to agents or move to critic."""
    if state.get("analysis_complete", False):
        return "critic"
    return state.get("next_agent", "credit")


def check_human_review_required(state: UnderwritingState) -> str:
    """Determine if human review is needed."""
    if state.get("human_review_required", False):
        return "human_review"
    return "end"
