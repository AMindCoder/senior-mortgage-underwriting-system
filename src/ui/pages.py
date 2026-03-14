"""Streamlit page components for the underwriting UI."""

import json
import logging

import streamlit as st

logger = logging.getLogger(__name__)


def render_sidebar():
    """Render the navigation sidebar."""
    st.sidebar.title("Mortgage Underwriting")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Submit Application",
            "Processing Dashboard",
            "Human Review",
            "Audit Trail",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Multi-Agent AI System using LangGraph, ChromaDB, and OpenAI."
    )
    return page


def render_submit_page(run_workflow_callback):
    """Render the application submission form."""
    st.header("Submit Loan Application")

    tab_json, tab_form = st.tabs(["JSON Input", "Form Input"])

    with tab_json:
        st.subheader("Paste Application JSON")
        default_json = json.dumps(
            {
                "case_id": "CASE-001",
                "name": "John Doe",
                "ssn": "123-45-6789",
                "phone": "555-123-4567",
                "email": "john@example.com",
                "address": "123 Main St, Anytown, USA",
                "credit_score": 750,
                "credit_history": {
                    "bankruptcies": 0,
                    "foreclosures": 0,
                    "late_payments_12mo": 0,
                    "collections": [],
                },
                "employment": {
                    "employer": "Acme Corp",
                    "position": "Senior Engineer",
                    "years": 8,
                    "type": "W-2",
                    "monthly_income": 12000,
                },
                "debts": {"car_loan": 450, "student_loan": 300, "credit_cards": 200},
                "loan": {
                    "amount": 400000,
                    "down_payment": 80000,
                    "estimated_payment": 2500,
                    "use": "Primary Residence",
                },
                "assets": {
                    "checking": 25000,
                    "savings": 85000,
                    "401k": 150000,
                    "recent_deposits": [
                        {"amount": 3000, "date": "2024-01-15"},
                        {"amount": 1500, "date": "2024-02-01"},
                    ],
                },
                "property": {
                    "type": "Single Family",
                    "appraised_value": 500000,
                    "condition": "Good",
                },
            },
            indent=2,
        )
        json_input = st.text_area(
            "Application Data (JSON)", value=default_json, height=400
        )

        if st.button("Submit Application", type="primary", key="submit_json"):
            try:
                applicant_data = json.loads(json_input)
                case_id = applicant_data.get("case_id", "UNKNOWN")
                with st.spinner(f"Processing application {case_id}..."):
                    result = run_workflow_callback(case_id, applicant_data)
                st.session_state["last_result"] = result
                st.session_state["last_case_id"] = case_id
                st.success(f"Application {case_id} processed successfully!")
                _render_result_summary(result)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
            except Exception as e:
                st.error(f"Processing error: {e}")
                logger.exception("Workflow error")

    with tab_form:
        st.subheader("Fill Application Form")
        with st.form("application_form"):
            col1, col2 = st.columns(2)
            with col1:
                case_id = st.text_input("Case ID", value="CASE-001")
                name = st.text_input("Applicant Name", value="John Doe")
                credit_score = st.number_input(
                    "Credit Score", min_value=300, max_value=850, value=750
                )
                monthly_income = st.number_input(
                    "Monthly Income ($)", min_value=0, value=12000
                )
                employer = st.text_input("Employer", value="Acme Corp")
                years_employed = st.number_input(
                    "Years Employed", min_value=0, value=8
                )

            with col2:
                loan_amount = st.number_input(
                    "Loan Amount ($)", min_value=0, value=400000
                )
                down_payment = st.number_input(
                    "Down Payment ($)", min_value=0, value=80000
                )
                property_value = st.number_input(
                    "Property Value ($)", min_value=0, value=500000
                )
                property_type = st.selectbox(
                    "Property Type",
                    ["Single Family", "Condo", "Townhouse", "Multi-Family"],
                )
                property_condition = st.selectbox(
                    "Property Condition", ["Excellent", "Good", "Fair", "Poor"]
                )
                employment_type = st.selectbox(
                    "Employment Type", ["W-2", "Self-Employed", "Contract"]
                )

            submitted = st.form_submit_button("Submit Application", type="primary")

            if submitted:
                applicant_data = {
                    "case_id": case_id,
                    "name": name,
                    "ssn": "000-00-0000",
                    "phone": "000-000-0000",
                    "email": "applicant@example.com",
                    "address": "Address not provided",
                    "credit_score": credit_score,
                    "credit_history": {
                        "bankruptcies": 0,
                        "foreclosures": 0,
                        "late_payments_12mo": 0,
                        "collections": [],
                    },
                    "employment": {
                        "employer": employer,
                        "position": "Not specified",
                        "years": years_employed,
                        "type": employment_type,
                        "monthly_income": monthly_income,
                    },
                    "debts": {},
                    "loan": {
                        "amount": loan_amount,
                        "down_payment": down_payment,
                        "estimated_payment": int(loan_amount * 0.006),
                        "use": "Primary Residence",
                    },
                    "assets": {
                        "checking": 10000,
                        "savings": down_payment + 20000,
                        "401k": 50000,
                        "recent_deposits": [],
                    },
                    "property": {
                        "type": property_type,
                        "appraised_value": property_value,
                        "condition": property_condition,
                    },
                }
                with st.spinner(f"Processing application {case_id}..."):
                    try:
                        result = run_workflow_callback(case_id, applicant_data)
                        st.session_state["last_result"] = result
                        st.session_state["last_case_id"] = case_id
                        st.success(f"Application {case_id} processed successfully!")
                        _render_result_summary(result)
                    except Exception as e:
                        st.error(f"Processing error: {e}")
                        logger.exception("Workflow error")


def _render_result_summary(result: dict):
    """Show a compact summary of the workflow result."""
    st.markdown("---")
    st.subheader("Decision Summary")

    col1, col2, col3 = st.columns(3)
    decision = result.get("final_decision", "PENDING")
    risk = result.get("risk_score", "N/A")

    color = {"APPROVED": "green", "DENIED": "red"}.get(decision, "orange")
    col1.metric("Decision", decision)
    col2.metric("Risk Score", f"{risk}/100")
    col3.metric(
        "Human Review",
        "Required" if result.get("human_review_required") else "Not Required",
    )

    with st.expander("Credit Analysis"):
        st.markdown(result.get("credit_analysis", "N/A"))
    with st.expander("Income Analysis"):
        st.markdown(result.get("income_analysis", "N/A"))
    with st.expander("Asset Analysis"):
        st.markdown(result.get("asset_analysis", "N/A"))
    with st.expander("Collateral Analysis"):
        st.markdown(result.get("collateral_analysis", "N/A"))
    with st.expander("Critic Review"):
        st.markdown(result.get("critic_review", "N/A"))
    with st.expander("Decision Memo"):
        st.markdown(result.get("decision_memo", "N/A"))

    st.markdown("**Reasoning Chain:**")
    for i, step in enumerate(result.get("reasoning_chain", []), 1):
        st.text(f"  {i}. {step}")


def render_dashboard():
    """Render the processing dashboard page."""
    st.header("Processing Dashboard")

    if "last_result" not in st.session_state:
        st.info("No applications processed yet. Submit one from the sidebar.")
        return

    result = st.session_state["last_result"]
    case_id = st.session_state.get("last_case_id", "Unknown")

    st.subheader(f"Case: {case_id}")
    _render_result_summary(result)


def render_human_review():
    """Render the human review (HITL) page."""
    st.header("Human-in-the-Loop Review")

    if "last_result" not in st.session_state:
        st.info("No applications pending review.")
        return

    result = st.session_state["last_result"]
    case_id = st.session_state.get("last_case_id", "Unknown")

    if not result.get("human_review_required", False):
        st.success(f"Case {case_id} does not require human review.")
        return

    st.warning(f"Case {case_id} requires human review.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("AI Decision", result.get("final_decision", "PENDING"))
        st.metric("Risk Score", f"{result.get('risk_score', 'N/A')}/100")
        st.metric("Bias Flags", len(result.get("bias_flags", [])))
    with col2:
        if result.get("bias_flags"):
            st.markdown("**Bias Flags:**")
            for flag in result["bias_flags"]:
                st.warning(flag)

    with st.expander("Decision Memo", expanded=True):
        st.markdown(result.get("decision_memo", "N/A"))

    st.markdown("---")
    st.subheader("Your Review")

    human_decision = st.radio(
        "Decision",
        ["APPROVED", "CONDITIONAL_APPROVAL", "DENIED"],
        index=0,
    )
    human_comments = st.text_area(
        "Review Comments",
        placeholder="Explain your reasoning...",
        height=150,
    )

    if st.button("Submit Review", type="primary"):
        if not human_comments.strip():
            st.error("Please provide review comments.")
        else:
            result["human_review_completed"] = True
            result["human_notes"] = (
                f"Human Decision: {human_decision}\nComments: {human_comments}"
            )
            result["final_decision"] = human_decision
            st.session_state["last_result"] = result
            st.success("Review submitted successfully!")
            st.balloons()


def render_audit_trail():
    """Render the audit trail page."""
    st.header("Audit Trail")

    if "last_result" not in st.session_state:
        st.info("No audit data available.")
        return

    result = st.session_state["last_result"]
    case_id = st.session_state.get("last_case_id", "Unknown")

    st.subheader(f"Case: {case_id}")

    st.markdown("**Reasoning Chain:**")
    for i, step in enumerate(result.get("reasoning_chain", []), 1):
        st.text(f"  {i}. {step}")

    st.markdown("---")
    st.markdown("**Compliance:**")
    col1, col2 = st.columns(2)
    col1.metric("Bias Flags", len(result.get("bias_flags", [])))
    col2.metric("Policy Violations", len(result.get("policy_violations", [])))

    if result.get("bias_flags"):
        st.markdown("**Bias Flag Details:**")
        for flag in result["bias_flags"]:
            st.warning(flag)

    st.markdown("---")
    st.markdown("**Full State (JSON):**")
    st.json(result)
