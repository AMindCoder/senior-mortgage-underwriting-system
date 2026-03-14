"""Database operations for persisting workflow state."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from src.db.models import Application, AuditLog, Decision, get_session

logger = logging.getLogger(__name__)


def save_application(case_id: str, applicant_data: Dict[str, Any]) -> Application:
    """Insert or update an application record."""
    session = get_session()
    try:
        app = session.query(Application).filter_by(case_id=case_id).first()
        if app is None:
            app = Application(
                case_id=case_id,
                applicant_data=applicant_data,
                status="pending",
            )
            session.add(app)
        else:
            app.applicant_data = applicant_data
            app.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(app)
        return app
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_application_status(case_id: str, status: str):
    session = get_session()
    try:
        app = session.query(Application).filter_by(case_id=case_id).first()
        if app:
            app.status = status
            app.updated_at = datetime.utcnow()
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_decision(state: Dict[str, Any]) -> Decision:
    """Persist the final workflow state as a Decision record."""
    session = get_session()
    try:
        dec = Decision(
            case_id=state.get("case_id", ""),
            credit_analysis=state.get("credit_analysis"),
            income_analysis=state.get("income_analysis"),
            asset_analysis=state.get("asset_analysis"),
            collateral_analysis=state.get("collateral_analysis"),
            critic_review=state.get("critic_review"),
            decision_memo=state.get("decision_memo"),
            final_decision=state.get("final_decision"),
            risk_score=state.get("risk_score"),
            human_review_required=state.get("human_review_required", False),
            human_review_completed=state.get("human_review_completed", False),
            human_notes=state.get("human_notes"),
            bias_flags=state.get("bias_flags", []),
            policy_violations=state.get("policy_violations", []),
            reasoning_chain=state.get("reasoning_chain", []),
        )
        session.add(dec)
        session.commit()
        session.refresh(dec)
        return dec
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def add_audit_log(case_id: str, agent_name: str, action: str, details: str = ""):
    session = get_session()
    try:
        log = AuditLog(
            case_id=case_id,
            agent_name=agent_name,
            action=action,
            details=details,
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_application(case_id: str) -> Optional[Application]:
    session = get_session()
    try:
        return session.query(Application).filter_by(case_id=case_id).first()
    finally:
        session.close()


def get_decision(case_id: str) -> Optional[Decision]:
    session = get_session()
    try:
        return (
            session.query(Decision)
            .filter_by(case_id=case_id)
            .order_by(Decision.created_at.desc())
            .first()
        )
    finally:
        session.close()


def get_all_applications():
    session = get_session()
    try:
        return session.query(Application).order_by(Application.created_at.desc()).all()
    finally:
        session.close()


def get_audit_trail(case_id: str):
    session = get_session()
    try:
        return (
            session.query(AuditLog)
            .filter_by(case_id=case_id)
            .order_by(AuditLog.timestamp.asc())
            .all()
        )
    finally:
        session.close()
