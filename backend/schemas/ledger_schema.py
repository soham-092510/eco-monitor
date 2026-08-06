# =====================================================================
# ECO MONITOR — LEDGER_SCHEMA.PY
# Purpose: Defines Pydantic validation schemas for double-entry ledger listings.
# =====================================================================

# Import BaseModel and Field
from pydantic import BaseModel, Field

# Import datetime
from datetime import datetime


class LedgerEntryResponse(BaseModel):
    # Ledger entry representation schema
    # WHY:
    # - Standardizes the output fields matching the UI expectations in app.js
    
    id: str = Field(..., description="UUID of the ledger entry")
    type: str = Field(..., description="Entry type: debit or credit")
    amount: float = Field(..., description="Quantitative amount of the change")
    description: str = Field(..., description="Description pulled from the parent transaction")
    running_balance: float = Field(..., description="Running account balance after entry")
    created_at: datetime = Field(..., description="Timestamp when ledger entry was recorded")

    class Config:
        from_attributes = True
