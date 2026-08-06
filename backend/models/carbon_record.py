# =====================================================================
# ECO MONITOR — CARBON_RECORD.PY (MODEL)
# Purpose: Defines ORM schemas for "carbon_records" and "emission_factors" tables.
#          Tracks logged carbon emissions and lookup emission factors.
# =====================================================================

# Import Base from db setup
from backend.db.base import Base

# Import SQLAlchemy column types
from sqlalchemy import Column, String, DateTime, Float, ForeignKey

# Import database timestamp builder
from sqlalchemy import func

# Import UUID generator
import uuid


class EmissionFactor(Base):
    # Map class to database table name
    # WHY:
    # - Stores the emission conversion factors (e.g. kg CO2 per unit)
    __tablename__ = "emission_factors"

    # Primary key is the activity type (e.g., "transport", "energy")
    activity_type = Column(String(50), primary_key=True, index=True)
    
    # Conversion Factor (e.g., 0.2 kg CO2 per mile, 0.4 kg CO2 per kWh)
    factor = Column(Float, nullable=False)
    
    # Measurement unit (e.g. "mile", "kWh", "USD")
    unit = Column(String(20), nullable=False)


class CarbonRecord(Base):
    # Map class to database table name
    __tablename__ = "carbon_records"

    # UUID Primary Key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    # Foreign Key to User
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Activity Type of the emission
    activity_type = Column(String(50), nullable=False)

    # Emission amount (stored in kg CO2)
    amount = Column(Float, nullable=False)

    # Description of the activity
    description = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
