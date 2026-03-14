from langchain_core.messages import HumanMessage, SystemMessage

from src.core.compliance import detect_bias_signals
from src.core.llm import get_llm
from src.core.state import UnderwritingState
from src.rag.policy_store import retrieve_relevant_policies
from src.tools.calculators import (
    calculate_dti_ratio,
    calculate_housing_expense_ratio,
    calculate_total_debt_obligations,
)


def income_analyst_node(
    state: UnderwritingState, *, policy_store=None, llm=None
) -> dict:
    """Analyze borrower's income stability and capacity to repay."""
    if llm is None:
        llm = get_llm()

    policies = ""
    if policy_store is not None:
        policies = retrieve_relevant_policies(
            "employment income verification DTI ratio self-employed",
            policy_store,
        )

    app_data = state["sanitized_data"]
    debts = app_data.get("debts", {})
    proposed_payment = app_data.get("loan", {}).get("estimated_payment", 0)
    monthly_income = app_data.get("employment", {}).get("monthly_income", 0)

    total_debt = sum(debts.values())
    dti_result = calculate_dti_ratio.invoke({
        "monthly_debt": total_debt + proposed_payment,
        "monthly_income": monthly_income,
    })

    housing_ratio_result = calculate_housing_expense_ratio.invoke({
        "monthly_payment": proposed_payment,
        "monthly_income": monthly_income,
    })

    debt_breakdown = calculate_total_debt_obligations.invoke({
        "debts": debts,
        "proposed_payment": proposed_payment,
    })

    system_prompt = f"""You are a Senior Income Analyst with expertise in employment and income verification.

RELEVANT POLICIES:
{policies}

Your task is to verify income stability and assess capacity to afford the loan.

ANALYSIS FRAMEWORK:
1. Employment Stability - Review job history and tenure
2. Income Verification - Validate income sources
3. DTI Calculation - Use provided calculation (DO NOT recalculate)
4. Payment Capacity - Assess affordability
5. Risk Assessment - Identify income risks
6. Recommendations - Provide conditions if needed

IMPORTANT: Use the EXACT calculations provided below. Do not recalculate."""

    user_prompt = f"""Analyze income profile for case {app_data.get('case_id')}:

EMPLOYMENT:
- Employer: {app_data.get('employment', {}).get('employer')}
- Position: {app_data.get('employment', {}).get('position')}
- Years: {app_data.get('employment', {}).get('years')}
- Type: {app_data.get('employment', {}).get('type')}
- Monthly Income: ${monthly_income:,.2f}

CALCULATED DEBT OBLIGATIONS (ACCURATE - DO NOT RECALCULATE):
{debt_breakdown}

CALCULATED DTI RATIO (ACCURATE - DO NOT RECALCULATE):
{dti_result}

CALCULATED HOUSING RATIO (ACCURATE - DO NOT RECALCULATE):
{housing_ratio_result}

Provide your income analysis based on these ACCURATE calculations."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    analysis = response.content
    bias_flags = detect_bias_signals(analysis, app_data)

    return {
        "income_analysis": analysis,
        "bias_flags": state.get("bias_flags", []) + bias_flags,
        "reasoning_chain": [
            "Income Analyst: Completed income analysis with DTI calculation"
        ],
    }
