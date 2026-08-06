# =====================================================================
# ECO MONITOR — CREDIT.PY (MODEL)
# Purpose: Defines the SQLAlchemy ORM schema for the "credit_retirements" table.
#          Tracks certificates issued when carbon credits are permanently retired.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy column types
from sqlalchemy import Column, String, DateTime, Float, ForeignKey

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class CreditRetirement(Base):
    # Map class to database table name
    __tablename__ = "credit_retirements"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # Foreign Key to User
    # WHY:
    # - Identifies who retired the credits and holds the certificate
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Foreign Key to the original Carbon Credit asset
    # WHY:
    # - Tracks which specific carbon credit asset was retired/burned
    carbon_credit_id = Column(
        String(36),
        ForeignKey("carbon_credits.id", ondelete="CASCADE"),
        nullable=False
    )

    # Amount of credits retired (in tonnes of CO2 offset)
    amount = Column(Float, nullable=False)

    # Certificate Serial Number generated for the retirement proof
    # WHY:
    # - Provides immutable proof of retirement for sustainability reporting/compliance
    certificate_number = Column(String(100), unique=True, nullable=False)

    # Retired Reason / Notes
    notes = Column(String(255), nullable=True)

    # Timestamp of the retirement event
    created_at = Column(DateTime, nullable=False, default=func.now())
