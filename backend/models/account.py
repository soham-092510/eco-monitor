# =====================================================================
# ECO MONITOR — ACCOUNT.PY (MODEL)
# Purpose: Defines the SQLAlchemy ORM schema for the "accounts" table.
#          Accounts track asset (credits owned) or liability (emissions) balances.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy fields and constraints
# WHY:
# - CheckConstraint: Ensures database-level rules (like non-negative balances) are strictly enforced
# - ForeignKey: Connects an account to its owning user
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, CheckConstraint

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class Account(Base):
    # Map class to database table name
    __tablename__ = "accounts"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # Foreign Key to User
    # WHY:
    # - Connects this account to a User row in the "users" table
    # - ondelete="CASCADE" automatically deletes the user's accounts if the user is deleted
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Name of the Account (e.g. "carbon_asset", "carbon_liability", "cash_wallet")
    # WHY:
    # - Identifies the purpose of this ledger account
    name = Column(String(50), nullable=False)

    # Type of Account (e.g. "asset" or "liability")
    # WHY:
    # - Dictates whether debits or credits increase/decrease this account's balance
    type = Column(String(20), nullable=False)

    # Running Balance of the Account
    # WHY:
    # - Tracks credits/emissions currently held by the user
    # - Defaults to 0.0
    balance = Column(Float, nullable=False, default=0.0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Database-level Constraints
    # WHY:
    # - CheckConstraint("balance >= 0"): Enforces at the SQL level that balances can NEVER go negative.
    # - Any transaction trying to subtract more credits than a user owns will fail and rollback.
    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_positive_balance"),
    )
