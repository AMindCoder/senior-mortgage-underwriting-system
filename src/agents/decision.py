import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import get_llm
from src.core.state import UnderwritingState


def decision_agent_node(state: UnderwritingState, *, llm=None) -> dict:
    """Synthesize all findings into a final decision and credit memo."""
    if llm is None:
        llm = get_llm()

    system_prompt = """You are a Senior Underwriter making final loan decisions.

Based on all analyses, you must:
1. Assign a risk score (0-100, where 0=no risk, 100=extreme risk)
2. Make a final decision: APPROVED, DENIED, or CONDITIONAL_APPROVAL
3. List specific conditions if conditional approval
4. Write a comprehensive credit memo documenting your decision

DECISION CRITERIA:
- Risk Score 0-30: APPROVED (strong application)
- Risk Score 31-60: CONDITIONAL_APPROVAL (acceptable with conditions)
- Risk Score 61-100: DENIED (unacceptable risk)

Your memo must be audit-ready and clearly explain the rationale."""

    user_prompt = f"""Make final underwriting decision for case {state.get('case_id')}:

CREDIT ANALYSIS SUMMARY:
{(state.get('credit_analysis') or 'N/A')[:500]}...

INCOME ANALYSIS SUMMARY:
{(state.get('income_analysis') or 'N/A')[:500]}...

ASSET ANALYSIS SUMMARY:
{(state.get('asset_analysis') or 'N/A')[:500]}...

COLLATERAL ANALYSIS SUMMARY:
{(state.get('collateral_analysis') or 'N/A')[:500]}...

CRITIC REVIEW:
{(state.get('critic_review') or 'N/A')[:500]}...

COMPLIANCE ALERTS:
- Bias Flags: {len(state.get('bias_flags', []))}
- Policy Violations: {len(state.get('policy_violations', []))}

Provide:
1. RISK_SCORE: (number 0-100)
2. DECISION: (APPROVED/DENIED/CONDITIONAL_APPROVAL)
3. CREDIT_MEMO: (comprehensive decision documentation)"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    content = response.content

    # Extract risk score
    risk_score = 50
    match = re.search(r"RISK_SCORE:\s*(\d+)", content)
    if match:
        risk_score = int(match.group(1))

    # Extract decision
    decision = "CONDITIONAL_APPROVAL"
    if "APPROVED" in content and "CONDITIONAL" not in content:
        decision = "APPROVED"
    elif "DENIED" in content:
        decision = "DENIED"
    elif "CONDITIONAL_APPROVAL" in content or "CONDITIONAL APPROVAL" in content:
        decision = "CONDITIONAL_APPROVAL"

    human_review_required = (
        risk_score >= 65
        or len(state.get("bias_flags", [])) > 0
        or decision == "DENIED"
    )

    return {
        "decision_memo": content,
        "risk_score": risk_score,
        "final_decision": decision,
        "human_review_required": human_review_required,
        "reasoning_chain": [
            f"Decision Agent: Final decision {decision} with risk score {risk_score}"
        ],
    }
