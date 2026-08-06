# =====================================================================
# ECO MONITOR — AUTH.PY (ROUTER)
# Purpose: Handles API endpoints for user registration and authentication.
# =====================================================================

# Import APIRouter, Depends, and status from FastAPI
from fastapi import APIRouter, Depends, status

# Import OAuth2PasswordRequestForm from fastapi.security
# WHY:
# - Standard FastAPI tool to handle form-based login inputs (username/password)
# - Direct match with the FormData request structure built in frontend app.js
from fastapi.security import OAuth2PasswordRequestForm

# Import Session type hint
from sqlalchemy.orm import Session

# Import DB session dependency
from backend.db.session import get_db

# Import schemas
from backend.schemas.auth_schema import UserRegister, Token
from backend.schemas.user_schema import UserResponse

# Import auth services logic
from backend.services import auth_service

# Create APIRouter instance
# WHY:
# - Modulates endpoints under the "/auth" prefix and tags them for Swagger documentation
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register(
    schema: UserRegister,
    db: Session = Depends(get_db)
):
    # Handles user registration requests
    # WHY:
    # - Passes registration inputs to the business service layer
    # - Auto-logs the user in after registration by returning JWT tokens
    
    # Register user and initialize double-entry ledger accounts
    user = auth_service.register_user(db=db, schema=schema)
    
    # Generate and return active JWT credentials
    tokens = auth_service.authenticate_user(
        db=db,
        username=schema.username,
        password=schema.password
    )
    return tokens


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and issue JWT credentials"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Handles user login form credentials check
    # WHY:
    # - Standard OAuth2 OAuth2PasswordRequestForm reads username and password from form bodies
    # - Returns JWT Access Token and Refresh Token on valid login
    tokens = auth_service.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    return tokens
