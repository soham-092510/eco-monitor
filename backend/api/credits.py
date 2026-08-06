# =====================================================================
# ECO MONITOR — CREDITS.PY (ROUTER)
# Purpose: Handles API endpoints for carbon credits (minting, transfers, retirement).
# =====================================================================

# Import APIRouter, Depends, status
from fastapi import APIRouter, Depends, status

# Import DB Session type
from sqlalchemy.orm import Session

# Import dependencies
from backend.db.session import get_db
from backend.core.dependencies import get_current_user

# Import models & schemas
from backend.models.user import User
from backend.schemas.credit_schema import (
    CarbonCreditCreate,
    CarbonCreditResponse,
    CreditRetireRequest,
    CreditRetireResponse,
    CreditTransferRequest
)

# Import business services
from backend.services import credit_service

# Import List typing
from typing import List

# Create APIRouter instance
router = APIRouter(prefix="/credits", tags=["Carbon Credits"])


@router.get(
    "",
    response_model=List[CarbonCreditResponse],
    summary="Get user's carbon credits"
)
def list_credits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Returns the carbon credits active/retired in user's inventory
    # WHY:
    # - Speeds up responses by utilizing Redis cache layer
    return credit_service.get_user_credits(db=db, user_id=current_user.id)


@router.post(
    "/mint",
    response_model=CarbonCreditResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mint new carbon credits (Admin/Investor Demo)"
)
def mint_credit(
    schema: CarbonCreditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mints carbon credits to the user's account
    # WHY:
    # - Facilitates minting new verified offsets into the system
    # - Generates balancing double-entry ledger listings automatically
    return credit_service.mint_carbon_credit(
        db=db,
        user_id=current_user.id,
        credit_type=schema.credit_type,
        amount=schema.amount,
        source=schema.source,
        vintage_year=schema.vintage_year
    )


@router.post(
    "/transfer",
    response_model=CarbonCreditResponse,
    summary="Transfer carbon credits to another user"
)
def transfer_credit(
    schema: CreditTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Transfers carbon credits asset ownership
    # WHY:
    # - Atomically handles partial or complete splits
    # - Posts double-entry credit ledger updates verifying balance constraints
    return credit_service.transfer_carbon_credit(
        db=db,
        sender_id=current_user.id,
        recipient_username=schema.recipient_username,
        credit_id=schema.carbon_credit_id,
        transfer_amount=schema.amount
    )


@router.post(
    "/retire",
    response_model=CreditRetireResponse,
    summary="Retire (burn) carbon credits to offset emissions"
)
def retire_credit(
    schema: CreditRetireRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Permanently offsets carbon footprint liability
    # WHY:
    # - Reductions are logged in double-entry account ledgers
    # - Issues a unique certificate of retirement proof
    return credit_service.retire_carbon_credit(
        db=db,
        user_id=current_user.id,
        credit_id=schema.carbon_credit_id,
        retire_amount=schema.amount,
        notes=schema.notes
    )
