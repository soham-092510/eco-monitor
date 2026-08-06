# =====================================================================
# ECO MONITOR — BASE.PY
# Purpose: Defines the base class for all database models and registers
#          them to metadata for automatic DDL generation (table creation).
# =====================================================================

# Import DeclarativeBase from SQLAlchemy ORM
# WHY:
# - SQLAlchemy uses a "declarative system" to map database tables to Python classes
# - All models must inherit from this Base so SQLAlchemy can collect table metadata
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Docstring explaining purpose
    """Base class all ORM models inherit from."""
    pass


# Import all models to ensure they are registered on Base.metadata
# WHY:
# - When Base.metadata.create_all(bind=engine) is called, SQLAlchemy needs to know which tables exist
# - Importing all models here guarantees that their classes are loaded in Python memory
#   and registered on the metadata object automatically.
from backend.models.user import User
from backend.models.account import Account
from backend.models.carbon_record import CarbonRecord, EmissionFactor
from backend.models.carbon_credit import CarbonCredit
from backend.models.transaction import Transaction
from backend.models.ledger_entry import LedgerEntry
from backend.models.credit import CreditRetirement