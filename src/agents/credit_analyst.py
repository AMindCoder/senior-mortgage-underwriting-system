from langchain_core.messages import HumanMessage, SystemMessage

from src.core.compliance import detect_bias_signals
from src.core.llm import get_llm
from src.core.state import UnderwritingState
from src.rag.policy_store import retrieve_relevant_policies
from src.tools.calculators import check_credit_score_policy


def credit_analyst_node(
    state: UnderwritingState, *, policy_store=None, llm=None
) -> dict:
    """Analyze borrower's credit profile and payment history."""
    if llm is None:
        llm = get_llm()

    policies = ""
    if policy_store is not None:
        policies = retrieve_relevant_policies(
            "credit score requirements bankruptcies foreclosures late payments",
            policy_store,
        )

    app_data = state["sanitized_data"]
    credit_score = app_data.get("credit_score", 0)
    credit_score_analysis = check_credit_score_policy.invoke(
        {"credit_score": credit_score}
    )

    system_prompt = f"""You are a Senior Credit Analyst with 15+ years of experience in mortgage underwriting.

RELEVANT POLICIES:
{policies}

Your task is to analyze the borrower's credit profile and provide a detailed assessment.

ANALYSIS FRAMEWORK:
1. Credit Score Assessment - Use provided assessment (DO NOT recalculate)
2. Payment History - Review late payments and patterns
3. Derogatory Items - Evaluate bankruptcies, foreclosures, collections
4. Policy Compliance - Check against credit guidelines
5. Risk Rating - Assign credit risk (Low/Medium/High)
6. Recommendations - Provide conditions or concerns

Be thorough, objective, and policy-compliant. Support conclusions with data.
IMPORTANT: Use the EXACT credit score assessment provided below. Do not recalculate."""

    user_prompt = f"""Analyze the credit profile for case {app_data.get('case_id')}:

CALCULATED CREDIT SCORE ASSESSMENT (ACCURATE - DO NOT RECALCULATE):
{credit_score_analysis}

CREDIT HISTORY DATA:
- Bankruptcies: {app_data.get('credit_history', {}).get('bankruptcies', 0)}
- Foreclosures: {app_data.get('credit_history', {}).get('foreclosures', 0)}
- Late Payments (12mo): {app_data.get('credit_history', {}).get('late_payments_12mo', 0)}
- Collections: {app_data.get('credit_history', {}).get('collections', [])}

Provide your detailed credit analysis based on the ACCURATE assessment above."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        "credit_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": [
            f"Credit Analyst: Completed credit analysis for {app_data.get('case_id')}"
        ],
    }
