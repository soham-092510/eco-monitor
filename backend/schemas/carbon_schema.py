# =====================================================================
# ECO MONITOR — CARBON_SCHEMA.PY
# Purpose: Defines Pydantic validation schemas for carbon record logging
#          and reporting operations.
# =====================================================================

# Import BaseModel and Field
from pydantic import BaseModel, Field

# Import datetime
from datetime import datetime

# Import Optional
from typing import Optional


class CarbonRecordCreate(BaseModel):
    # Carbon logging request schema
    # WHY:
    # - Validates incoming activity type and footprint amounts logged by users
    
    activity_type: str = Field(
        ...,
        description="Type of activity causing emission (e.g. transport, energy, manufacturing, agriculture, other)"
    )
    
    amount: float = Field(
        ...,
        gt=0.0,
        description="Emissions amount tracked in kg CO2 (must be greater than 0)"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Brief notes describing the emission event"
    )


class CarbonRecordResponse(BaseModel):
    # Carbon logging response schema
    # WHY:
    # - Defines structure of carbon records returned by list or detail queries
    
    id: str
    user_id: str
    activity_type: str
    amount: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
