# =====================================================================
# ECO MONITOR — CREDIT_SCHEMA.PY
# Purpose: Defines Pydantic validation schemas for carbon credit asset operations
#          (listings, transfers, retirements).
# =====================================================================

# Import BaseModel and Field
from pydantic import BaseModel, Field

# Import datetime
from datetime import datetime

# Import Optional
from typing import Optional


class CarbonCreditCreate(BaseModel):
    # Carbon credit creation input schema
    # WHY:
    # - Used by administrators or system triggers to mint/issue new carbon credits
    credit_type: str = Field(..., description="Renewable technology source (e.g. wind, solar, forestry)")
    amount: float = Field(..., gt=0.0, description="Amount of credits in metric tonnes of CO2 offset")
    source: str = Field(..., description="Project name generating the credit")
    vintage_year: int = Field(..., ge=2000, le=2050, description="Certification vintage year")
    serial_number: str = Field(..., description="Unique carbon registry tracking number")


class CarbonCreditResponse(BaseModel):
    # Carbon credit details response schema
    # WHY:
    # - Serializes carbon credit rows for API display
    id: str
    user_id: str
    credit_type: str
    amount: float
    source: str
    vintage_year: int
    serial_number: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreditRetireRequest(BaseModel):
    # Carbon credit retirement input schema
    # WHY:
    # - Validates input payloads when a user requests to burn credits for certificates
    carbon_credit_id: str = Field(..., description="UUID of the carbon credit asset to retire")
    amount: float = Field(..., gt=0.0, description="Amount of credits to retire (must be positive)")
    notes: Optional[str] = Field(None, max_length=255, description="Auditing reasons or notes")


class CreditRetireResponse(BaseModel):
    # Carbon credit retirement outcome schema
    # WHY:
    # - Returns the details of the created offset certificate
    id: str
    user_id: str
    carbon_credit_id: str
    amount: float
    certificate_number: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CreditTransferRequest(BaseModel):
    # Carbon credit transfer schema
    # WHY:
    # - Validates payload to transfer asset ownership to another user on the platform
    recipient_username: str = Field(..., description="Username of the recipient user")
    carbon_credit_id: str = Field(..., description="UUID of the carbon credit asset to transfer")
    amount: float = Field(..., gt=0.0, description="Quantity of credit to transfer")
