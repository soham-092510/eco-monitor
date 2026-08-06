# =====================================================================
# ECO MONITOR — AUTH_SERVICE.PY (SERVICE)
# Purpose: Core business logic for user registration and login flows.
# =====================================================================

# Import Session from SQLAlchemy
from sqlalchemy.orm import Session

# Import HTTPException and status from FastAPI
from fastapi import HTTPException, status

# Import User and Account models
from backend.models.user import User
from backend.models.account import Account

# Import validation schemas
from backend.schemas.auth_schema import UserRegister

# Import security utilities
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


def register_user(db: Session, schema: UserRegister) -> User:
    # Business logic for registering a new user
    # WHY:
    # - Validates uniqueness of credentials
    # - Creates user account, generates default double-entry accounts, and commits them transactionally
    
    # 1. Check if username already exists in DB
    existing_username = db.query(User).filter(User.username == schema.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered"
        )
        
    # 2. Check if email already exists in DB
    existing_email = db.query(User).filter(User.email == schema.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )
        
    # 3. Create user instance
    # WHY:
    # - Hashes plaintext password using bcrypt before database write
    new_user = User(
        name=schema.name,
        username=schema.username,
        email=schema.email,
        hashed_password=hash_password(schema.password),
        role="INVESTOR"  # Default role assigned to standard registrations
    )
    
    # 4. Add user to database session
    db.add(new_user)
    
    # Flush changes to assign user.id UUID
    # WHY:
    # - We need the user.id value to link their default asset/liability accounts
    db.flush()
    
    # 5. Initialize double-entry accounts
    # WHY:
    # - Every user needs a "carbon_asset" account (to hold positive credit balance)
    # - Every user needs a "carbon_liability" account (to track logged emission debts)
    asset_account = Account(
        user_id=new_user.id,
        name="carbon_asset",
        type="asset",
        balance=0.0
    )
    liability_account = Account(
        user_id=new_user.id,
        name="carbon_liability",
        type="liability",
        balance=0.0
    )
    
    db.add(asset_account)
    db.add(liability_account)
    
    # 6. Commit the transaction
    # WHY:
    # - Saves user and both accounts atomically
    db.commit()
    
    # Refresh to load auto-generated fields from DB
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> dict:
    # Business logic to validate login credentials and issue tokens
    # WHY:
    # - Checks credentials and returns JWT Access & Refresh tokens if valid
    
    # 1. Fetch user by username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # 2. Verify hashed password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # 3. Create token payloads
    # WHY:
    # - "sub" stores subject identification (username)
    # - "role" stores authorization level
    payload = {"sub": user.username, "role": user.role}
    
    # 4. Generate access and refresh tokens
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    
    # 5. Return token response structure
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }
