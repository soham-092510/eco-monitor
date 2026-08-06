# =====================================================================
# ECO MONITOR — PORTFOLIO.PY (ROUTER)
# Purpose: Handles API endpoints for querying user portfolio aggregation summaries
#          and performing ESG asset allocation rebalancing.
# =====================================================================

# Import APIRouter, Depends, and schema
from fastapi import APIRouter, Depends

# Import DB Session type
from sqlalchemy.orm import Session

# Import dependencies
from backend.db.session import get_db
from backend.core.dependencies import get_current_user

# Import User model
from backend.models.user import User

# Import business service layer
from backend.services import portfolio_service

# Import Pydantic model for rebalancing inputs
from pydantic import BaseModel, Field


# Define request schema for portfolio rebalancing
# WHY:
# - Validates incoming preference payload for target ESG score (0-10) and risk profiles
class RebalanceRequest(BaseModel):
    target_esg: int = Field(..., ge=0, le=10, description="Target ESG rating of portfolio credits (0-10)")
    risk_level: str = Field(..., description="Desired risk level profile: low, medium, high")


# Create APIRouter instance
router = APIRouter(prefix="/portfolio", tags=["Portfolio Analytics"])


@router.get(
    "",
    summary="Get user's carbon credit and emission portfolio summary"
)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve aggregated portfolio metrics
    # WHY:
    # - Computes total emissions, total credits, net credits, and sustainability score
    return portfolio_service.get_user_portfolio_summary(db=db, user_id=current_user.id)


@router.post(
    "/rebalance",
    summary="Optimize and rebalance carbon credit portfolio allocations"
)
def rebalance_portfolio(
    schema: RebalanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Runs the carbon portfolio rebalancing optimization engine
    # WHY:
    # - Compares current asset allocation weights vs target weights based on risk/ESG preferences
    # - Returns buy/sell recommendations if allocation drift exceeds 5%
    return portfolio_service.rebalance_portfolio_optimization(
        db=db,
        user_id=current_user.id,
        target_esg=schema.target_esg,
        risk_level=schema.risk_level
    )
