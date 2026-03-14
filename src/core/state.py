from typing import Annotated, Any, Dict, List, Optional, TypedDict


class UnderwritingState(TypedDict):
    """Complete state of a loan application as it moves through the workflow."""

    # Application Information
    case_id: str
    applicant_data: Dict[str, Any]
    sanitized_data: Dict[str, Any]

    # Agent Analysis Results
    credit_analysis: Optional[str]
    income_analysis: Optional[str]
    asset_analysis: Optional[str]
    collateral_analysis: Optional[str]

    # Coordination & Decision
    critic_review: Optional[str]
    decision_memo: Optional[str]
    final_decision: Optional[str]  # APPROVED, DENIED, CONDITIONAL_APPROVAL
    risk_score: Optional[int]  # 0-100

    # Workflow Control
    next_agent: Optional[str]
    analysis_complete: bool
    human_review_required: bool
    human_review_completed: bool
    human_notes: Optional[str]

    # Compliance
    bias_flags: List[str]
    policy_violations: List[str]

    # Audit Trail
    reasoning_chain: Annotated[List[str], "append"]
    timestamp: str


def create_initial_state(case_id: str, applicant_data: Dict[str, Any]) -> dict:
    """Create a fresh initial state dict for the workflow."""
    return {
        "case_id": case_id,
        "applicant_data": applicant_data,
        "sanitized_data": {},
        "credit_analysis": None,
        "income_analysis": None,
        "asset_analysis": None,
        "collateral_analysis": None,
        "critic_review": None,
        "decision_memo": None,
        "final_decision": None,
        "risk_score": None,
        "next_agent": None,
        "analysis_complete": False,
        "human_review_required": False,
        "human_review_completed": False,
        "human_notes": None,
        "bias_flags": [],
        "policy_violations": [],
        "reasoning_chain": [],
        "timestamp": "",
    }
