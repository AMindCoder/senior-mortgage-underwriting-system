from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import get_llm
from src.core.state import UnderwritingState


def critic_agent_node(state: UnderwritingState, *, llm=None) -> dict:
    """Review all specialist analyses for consistency and completeness."""
    if llm is None:
        llm = get_llm()

    system_prompt = """You are a Quality Assurance Critic reviewing underwriting analyses.

Your role is to:
1. Verify all analyses are complete and thorough
2. Identify any contradictions or inconsistencies
3. Ensure policy compliance
4. Flag any missing information
5. Provide a synthesis of key findings

Be critical but fair. Focus on ensuring decision quality."""

    user_prompt = f"""Review all analyses for case {state.get('case_id')}:

CREDIT ANALYSIS:
{state.get('credit_analysis', 'Not completed')}

INCOME ANALYSIS:
{state.get('income_analysis', 'Not completed')}

ASSET ANALYSIS:
{state.get('asset_analysis', 'Not completed')}

COLLATERAL ANALYSIS:
{state.get('collateral_analysis', 'Not completed')}

BIAS FLAGS:
{state.get('bias_flags', [])}

Provide your critical review and synthesis."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    return {
        "critic_review": response.content,
        "reasoning_chain": [
            "Critic: Completed review of all specialist analyses"
        ],
    }
