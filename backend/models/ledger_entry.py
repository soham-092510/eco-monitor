# =====================================================================
# ECO MONITOR — LEDGER_ENTRY.PY (MODEL)
# Purpose: Defines the SQLAlchemy ORM schema for the "ledger_entries" table.
#          Each row is an individual debit or credit to an account, associated
#          with an atomic transaction.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy column types and constraints
from sqlalchemy import Column, String, DateTime, Float, ForeignKey

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class LedgerEntry(Base):
    # Map class to database table name
    __tablename__ = "ledger_entries"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # Foreign Key to Transaction
    # WHY:
    # - Links this entry to its parent Transaction header
    # - CASCADE deletion deletes entries if the transaction header is removed
    transaction_id = Column(
        String(36),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Foreign Key to Account
    # WHY:
    # - Identifies which account (e.g., carbon_asset, carbon_liability) this entry modifies
    account_id = Column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Entry Type: "debit" or "credit"
    # WHY:
    # - Distinguishes between increase and decrease operations depending on account type
    type = Column(String(20), nullable=False)

    # Amount of the change
    # WHY:
    # - The quantitative value of this debit/credit entry
    amount = Column(Float, nullable=False)

    # Running Balance after this entry
    # WHY:
    # - Helps reconstruct historic account balances at a specific point in time
    running_balance = Column(Float, nullable=False)

    # Timestamp of the ledger post
    created_at = Column(DateTime, nullable=False, default=func.now())
