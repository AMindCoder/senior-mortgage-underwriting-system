from langchain_core.messages import HumanMessage, SystemMessage

from src.core.compliance import detect_bias_signals
from src.core.llm import get_llm
from src.core.state import UnderwritingState
from src.rag.policy_store import retrieve_relevant_policies
from src.tools.calculators import calculate_reserves, check_large_deposits


def asset_analyst_node(
    state: UnderwritingState, *, policy_store=None, llm=None
) -> dict:
    """Analyze borrower's assets and reserves."""
    if llm is None:
        llm = get_llm()

    policies = ""
    if policy_store is not None:
        policies = retrieve_relevant_policies(
            "down payment reserves assets large deposits gift funds",
            policy_store,
        )

    app_data = state["sanitized_data"]
    assets = app_data.get("assets", {})
    loan = app_data.get("loan", {})
    monthly_income = app_data.get("employment", {}).get("monthly_income", 0)

    liquid_assets = assets.get("checking", 0) + assets.get("savings", 0)
    monthly_payment = loan.get("estimated_payment", 0)

    reserves_result = calculate_reserves.invoke({
        "liquid_assets": liquid_assets,
        "monthly_payment": monthly_payment,
        "required_months": 2,
    })

    deposits_result = check_large_deposits.invoke({
        "deposits": assets.get("recent_deposits", []),
        "monthly_income": monthly_income,
    })

    system_prompt = f"""You are a Senior Asset Analyst specializing in funds verification.

RELEVANT POLICIES:
{policies}

Your task is to verify adequate funds and identify documentation requirements.

ANALYSIS FRAMEWORK:
1. Down Payment Adequacy - Verify sufficient funds
2. Reserve Requirements - Use provided calculation (DO NOT recalculate)
3. Large Deposits - Use provided analysis (DO NOT recalculate)
4. Source of Funds - Ensure proper sourcing
5. Risk Assessment - Identify asset-related risks
6. Documentation Needs - List required documents

IMPORTANT: Use the EXACT calculations provided below. Do not recalculate."""

    user_prompt = f"""Analyze assets for case {app_data.get('case_id')}:

ASSETS:
- Checking: ${assets.get('checking', 0):,.2f}
- Savings: ${assets.get('savings', 0):,.2f}
- 401k/Retirement: ${assets.get('401k', 0):,.2f}
- Total Liquid Assets: ${liquid_assets:,.2f}

LOAN REQUIREMENTS:
- Required Down Payment: ${loan.get('down_payment', 0):,.2f}
- Estimated Monthly Payment: ${monthly_payment:,.2f}

CALCULATED RESERVES (ACCURATE - DO NOT RECALCULATE):
{reserves_result}

LARGE DEPOSITS ANALYSIS (ACCURATE - DO NOT RECALCULATE):
{deposits_result}

Provide your asset analysis based on these ACCURATE calculations."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        "asset_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": [
            "Asset Analyst: Completed asset analysis and deposit review"
        ],
    }
