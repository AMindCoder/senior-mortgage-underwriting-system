"""Streamlit entry point for the Senior Mortgage Underwriting System."""

import logging
import sys
from pathlib import Path
from uuid import uuid4

import streamlit as st

# Ensure project root is on sys.path so `src.*` imports resolve
_project_root = str(Path(__file__).resolve().parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.core.config import settings  # noqa: E402
from src.core.state import create_initial_state  # noqa: E402
from src.ui.pages import (  # noqa: E402
    render_audit_trail,
    render_dashboard,
    render_human_review,
    render_sidebar,
    render_submit_page,
)

logging.basicConfig(level=settings.app.log_level)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mortgage Underwriting System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Lazy-init expensive resources once per Streamlit session
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading AI models and policy store...")
def _init_graph():
    from src.workflow.graph import build_graph

    return build_graph()


def run_workflow(case_id: str, applicant_data: dict) -> dict:
    """Execute the full underwriting workflow and return the final state."""
    graph = _init_graph()
    thread_id = f"{case_id}-{uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    inputs = create_initial_state(case_id, applicant_data)

    final_state = {}
    for event in graph.stream(inputs, config):
        for node_name, node_output in event.items():
            if node_name == "__start__":
                continue
            final_state.update(node_output)
            logger.info("Node completed: %s", node_name)

    # Merge with inputs for completeness
    full = {**inputs, **final_state}
    return full


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
page = render_sidebar()

if page == "Submit Application":
    render_submit_page(run_workflow)
elif page == "Processing Dashboard":
    render_dashboard()
elif page == "Human Review":
    render_human_review()
elif page == "Audit Trail":
    render_audit_trail()
