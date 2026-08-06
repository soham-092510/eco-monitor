# =====================================================================
# ECO MONITOR — DEPENDENCIES.PY
# Purpose: Defines reusable dependencies for FastAPI routes, such as retrieving
#          database sessions and authenticating/authorizing users via JWT tokens.
# =====================================================================

# Import HTTPException and status from fastapi
# WHY:
# - Used to raise standard HTTP errors (like 401 Unauthorized or 403 Forbidden)
from fastapi import Depends, HTTPException, status

# Import OAuth2PasswordBearer from fastapi.security
# WHY:
# - It specifies that the client must provide a Bearer token in the Authorization header
# - tokenUrl specifies the endpoint where clients can obtain the token (auth/login)
from fastapi.security import OAuth2PasswordBearer

# Import Session from sqlalchemy.orm
# WHY:
# - For type hinting the database session parameter
from sqlalchemy.orm import Session

# Import get_db function from backend/db/session
# WHY:
# - Used to retrieve a database session per HTTP request
from backend.db.session import get_db

# Import decode_access_token from security utilities
# WHY:
# - To decrypt and validate the JWT token sent by the client
from backend.core.security import decode_access_token

# Import User model from backend/models/user
# WHY:
# - To fetch the user from the database once the token is decoded
from backend.models.user import User


# Define the OAuth2 security scheme
# WHY:
# - Tells FastAPI that our app uses OAuth2 Bearer tokens for authorization
# - Automatically adds authorization details and security UI elements to Swagger docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # FastAPI dependency to get the currently authenticated user
    # WHY:
    # - Protects routes by requiring a valid JWT token
    # - Extracts the token, decodes it, verifies the user, and injects the user object into routes
    
    # 1. Define standard credentials exception
    # WHY:
    # - This is reuseable and returned if token decoding fails or user doesn't exist
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 2. Decode the JWT token
    # WHY:
    # - Extracts the claims (payload) inside the token
    payload = decode_access_token(token)
    if payload is None:
        # Raise exception if token signature is invalid or expired
        raise credentials_exception
        
    # 3. Extract the username from payload
    # WHY:
    # - "sub" is a standard JWT claim representing the subject (the username in our case)
    username: str = payload.get("sub")
    if username is None:
        # Raise exception if username is missing from payload
        raise credentials_exception
        
    # 4. Query the user from the database
    # WHY:
    # - Verifies that the user actually exists in our PostgreSQL/SQLite instance
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        # Raise exception if user in token does not exist in DB
        raise credentials_exception
        
    # 5. Return the user object
    # WHY:
    # - FastAPI routes can now access this user object directly (e.g. current_user: User = Depends(get_current_user))
    return user
