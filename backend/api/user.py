# =====================================================================
# ECO MONITOR — USER.PY (ROUTER)
# Purpose: Handles API endpoints for user profile queries.
# =====================================================================

# Import APIRouter and Depends
from fastapi import APIRouter, Depends

# Import User model
from backend.models.user import User

# Import dependency providers
from backend.core.dependencies import get_current_user

# Import schema response mapping
from backend.schemas.user_schema import UserResponse

# Create APIRouter instance
router = APIRouter(prefix="/user", tags=["User Profiles"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user profile"
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    # Returns current user context
    # WHY:
    # - Protects route using get_current_user dependency
    # - Returns user profile information sanitized by UserResponse schema
    return current_user
