# =====================================================================
# ECO MONITOR — CARBON_SERVICE.PY (SERVICE)
# Purpose: Calculates carbon footprints based on Scope 1, 2, 3 formulas,
#          logs carbon records, and updates user liability accounts.
# =====================================================================

# Import Session from SQLAlchemy ORM
from sqlalchemy.orm import Session

# Import CarbonRecord and EmissionFactor models
from backend.models.carbon_record import CarbonRecord, EmissionFactor

# Import Account model
from backend.models.account import Account

# Import List and Optional types
from typing import List, Optional


def log_emission(
    db: Session,
    user_id: str,
    activity_type: str,
    metric_value: float,
    description: Optional[str] = None
) -> CarbonRecord:
    # Business logic for logging a carbon emission record
    # WHY:
    # - Computes the carbon footprint by looking up conversion factors
    # - Stores the emission history and increases user environmental liability balance
    
    # 1. Look up the emission factor for the activity type
    # WHY:
    # - Fetches the certified conversion rate from the database (e.g. kg CO2 per mile)
    factor_record = db.query(EmissionFactor).filter(
        EmissionFactor.activity_type == activity_type.lower()
    ).first()
    
    # Fallback to standard 1.0 factor if not found in database
    factor = factor_record.factor if factor_record else 1.0
    
    # 2. Calculate emission in kg CO2
    # WHY:
    # - Core formula: operational metric * emission factor
    calculated_amount = metric_value * factor
    
    # 3. Create CarbonRecord database object
    new_record = CarbonRecord(
        user_id=user_id,
        activity_type=activity_type.lower(),
        amount=calculated_amount,
        description=description
    )
    
    # Add record to DB session
    db.add(new_record)
    
    # 4. Update the user's Carbon Liability Account balance
    # WHY:
    # - Tracks the cumulative carbon footprint debt that needs offsetting
    liability_account = db.query(Account).filter(
        Account.user_id == user_id,
        Account.name == "carbon_liability"
    ).first()
    
    if liability_account:
        # Increase liability balance by the calculated emission
        liability_account.balance += calculated_amount
        db.add(liability_account)
        
    # 5. Commit transaction atomically
    db.commit()
    
    # Refresh to return populated object
    db.refresh(new_record)
    
    return new_record


def get_user_records(db: Session, user_id: str) -> List[CarbonRecord]:
    # Retrieve all logged carbon records for a specific user
    # WHY:
    # - Provides history for tables and chart components in the dashboard
    return db.query(CarbonRecord).filter(CarbonRecord.user_id == user_id).all()
