from langchain_core.messages import HumanMessage, SystemMessage

from src.core.compliance import detect_bias_signals
from src.core.llm import get_llm
from src.core.state import UnderwritingState
from src.rag.policy_store import retrieve_relevant_policies
from src.tools.calculators import calculate_ltv_ratio


def collateral_analyst_node(
    state: UnderwritingState, *, policy_store=None, llm=None
) -> dict:
    """Analyze property value and condition."""
    if llm is None:
        llm = get_llm()

    policies = ""
    if policy_store is not None:
        policies = retrieve_relevant_policies(
            "appraisal property condition LTV collateral",
            policy_store,
        )

    app_data = state["sanitized_data"]
    property_data = app_data.get("property", {})
    loan = app_data.get("loan", {})

    loan_amount = loan.get("amount", 0)
    appraised_value = property_data.get("appraised_value", 0)

    ltv_result = calculate_ltv_ratio.invoke({
        "loan_amount": loan_amount,
        "property_value": appraised_value,
    })

    system_prompt = f"""You are a Senior Collateral Analyst with expertise in property valuation.

RELEVANT POLICIES:
{policies}

Your task is to assess the property as collateral for the loan.

ANALYSIS FRAMEWORK:
1. Appraisal Review - Validate property value
2. LTV Calculation - Use provided calculation (DO NOT recalculate)
3. Property Condition - Evaluate habitability
4. Marketability - Consider market factors
5. Risk Assessment - Identify collateral risks
6. Recommendations - Note any concerns

IMPORTANT: Use the EXACT LTV calculation provided below. Do not recalculate."""

    user_prompt = f"""Analyze property collateral for case {app_data.get('case_id')}:

PROPERTY:
- Type: {property_data.get('type')}
- Appraised Value: ${appraised_value:,.2f}
- Condition: {property_data.get('condition')}
- Use: {loan.get('use')}

LOAN:
- Loan Amount: ${loan_amount:,.2f}
- Down Payment: ${loan.get('down_payment', 0):,.2f}

CALCULATED LTV (ACCURATE - DO NOT RECALCULATE):
{ltv_result}

Provide your collateral analysis based on this ACCURATE calculation."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        "collateral_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": [
            "Collateral Analyst: Completed property analysis (LTV from tool)"
        ],
    }
