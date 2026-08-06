# =====================================================================
# ECO MONITOR — USER_SCHEMA.PY
# Purpose: Defines Pydantic validation schemas for returning User information.
# =====================================================================

# Import BaseModel, Field from pydantic
from pydantic import BaseModel, Field, EmailStr

# Import datetime
from datetime import datetime

# Import Optional
from typing import Optional


class UserResponse(BaseModel):
    # User profile response schema
    # WHY:
    # - Serializes and filters user data before sending it to the client (excludes password hashes)
    
    id: str = Field(..., description="Universally unique identifier (UUID) for user")
    username: str = Field(..., description="Unique username identifier")
    email: EmailStr = Field(..., description="Validated email address")
    name: Optional[str] = Field(None, description="Full name of the user")
    role: str = Field(..., description="Role-based tag (INVESTOR, AUDITOR, ADMIN)")
    created_at: datetime = Field(..., description="Datetime when user account was created")
    
    # Configure Pydantic to read ORM objects
    # WHY:
    # - from_attributes=True (in Pydantic v2) or orm_mode=True (in v1) allows Pydantic
    #   to automatically extract data from SQLAlchemy models (like User.username)
    class Config:
        from_attributes = True
