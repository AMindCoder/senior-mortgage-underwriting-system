"""SQLAlchemy models for persisting underwriting applications and decisions."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import settings


class Base(DeclarativeBase):
    pass


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    applicant_data = Column(JSON, nullable=False)
    sanitized_data = Column(JSON, nullable=True)
    status = Column(
        String(30), nullable=False, default="pending"
    )  # pending, processing, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), nullable=False, index=True)
    credit_analysis = Column(Text, nullable=True)
    income_analysis = Column(Text, nullable=True)
    asset_analysis = Column(Text, nullable=True)
    collateral_analysis = Column(Text, nullable=True)
    critic_review = Column(Text, nullable=True)
    decision_memo = Column(Text, nullable=True)
    final_decision = Column(String(30), nullable=True)
    risk_score = Column(Integer, nullable=True)
    human_review_required = Column(Boolean, default=False)
    human_review_completed = Column(Boolean, default=False)
    human_notes = Column(Text, nullable=True)
    bias_flags = Column(JSON, default=list)
    policy_violations = Column(JSON, default=list)
    reasoning_chain = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(50), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


def get_engine():
    return create_engine(settings.postgres.url, echo=False)


def get_session() -> Session:
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def init_db():
    """Create all tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)
