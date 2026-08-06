# =====================================================================
# ECO MONITOR — CARBON_CREDIT.PY (MODEL)
# Purpose: Defines the SQLAlchemy ORM schema for the "carbon_credits" table.
#          Tracks carbon credit inventory, origins, vintage, serials, and status.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy column types
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class CarbonCredit(Base):
    # Map class to database table name
    __tablename__ = "carbon_credits"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # Foreign Key to User
    # WHY:
    # - Tracks which user owns this carbon credit asset
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Type of Credit (e.g. wind, solar, forestry)
    # WHY:
    # - Defines the renewable/offset technology type
    credit_type = Column(String(50), nullable=False)

    # Amount of credits (1 credit usually = 1 tonne or 1000 kg of CO2 offset)
    amount = Column(Float, nullable=False)

    # Source / Project Name (e.g. "Amazon Rainforest Protection")
    source = Column(String(100), nullable=False)

    # Vintage Year (e.g. 2024, 2025)
    # WHY:
    # - Tracks when the emission offset was certified
    vintage_year = Column(Integer, nullable=False, default=2026)

    # Serial Number (unique identifier for credit authentication)
    # WHY:
    # - Essential for tracking credits to prevent double-counting or fraud
    serial_number = Column(String(100), unique=True, nullable=False)

    # Status of the credit ("active", "retired")
    # WHY:
    # - Credits start as "active" and transition permanently to "retired" once burned for offsets
    status = Column(String(20), nullable=False, default="active")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
