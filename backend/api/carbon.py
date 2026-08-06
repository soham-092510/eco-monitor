# =====================================================================
# ECO MONITOR — CARBON.PY (ROUTER)
# Purpose: Handles API endpoints for tracking carbon emission records.
# =====================================================================

# Import APIRouter, Depends, and List
from fastapi import APIRouter, Depends, status

# Import DB Session type
from sqlalchemy.orm import Session

# Import dependencies
from backend.db.session import get_db
from backend.core.dependencies import get_current_user

# Import models
from backend.models.user import User

# Import schemas
from backend.schemas.carbon_schema import CarbonRecordCreate, CarbonRecordResponse

# Import carbon services logic
from backend.services import carbon_service

# Import List typing helper
from typing import List

# Create APIRouter instance
# WHY:
# - Map requests with "/carbon" prefix
router = APIRouter(prefix="/carbon", tags=["Carbon Footprint"])


@router.get(
    "",
    response_model=List[CarbonRecordResponse],
    summary="Get user's carbon emission records"
)
def list_emissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve user's logged emissions list
    # WHY:
    # - Serves historical logs for frontend display
    records = carbon_service.get_user_records(db=db, user_id=current_user.id)
    return records


@router.post(
    "",
    response_model=CarbonRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new carbon emission record"
)
def add_emission(
    schema: CarbonRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Logs a new carbon footprint entry
    # WHY:
    # - Accepts activity metrics (e.g. transport miles, energy kWh)
    # - Converts metrics using database emission factors and increments environmental liability
    record = carbon_service.log_emission(
        db=db,
        user_id=current_user.id,
        activity_type=schema.activity_type,
        metric_value=schema.amount,  # Uses the amount field as metric value input
        description=schema.description
    )
    return record
