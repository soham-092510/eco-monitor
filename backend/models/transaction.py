# =====================================================================
# ECO MONITOR — TRANSACTION.PY (MODEL)
# Purpose: Defines the SQLAlchemy ORM schema for the "transactions" table.
#          A Transaction is a header grouping multiple balanced LedgerEntries.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy column types
from sqlalchemy import Column, String, DateTime

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class Transaction(Base):
    # Map class to database table name
    __tablename__ = "transactions"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # General description of the Transaction (e.g. "Carbon Credit Purchase - Solar Project")
    # WHY:
    # - Explains the business context of the ledger updates
    description = Column(String(255), nullable=False)

    # Timestamp of the transaction
    # WHY:
    # - Immutable record of when the ledger transaction was registered
    created_at = Column(DateTime, nullable=False, default=func.now())
