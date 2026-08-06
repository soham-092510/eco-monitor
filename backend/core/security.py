# =====================================================================
# ECO MONITOR — SECURITY.PY
# Purpose: Manages password hashing (using bcrypt directly) and JWT authentication token generation/verification
# =====================================================================

# Import bcrypt directly
# WHY:
# - Avoids passlib compatibility bugs with bcrypt 4.0+ (ValueError on 72-byte passwords during passlib tests)
# - Provides clean, modern, and standard hashing without deprecated dependencies
import bcrypt

# Import jwt and JWTError from jose
# WHY:
# - jwt: used to sign and verify JSON Web Tokens (JWTs) securely
# - JWTError: used to capture and handle validation errors (expired or invalid signature)
from jose import jwt, JWTError

# Import datetime and timedelta from datetime module
# WHY:
# - Used to compute token expiration dates (e.g., current time + 30 minutes)
from datetime import datetime, timedelta

# Import Optional type hint from typing
from typing import Optional

# Import settings from backend.core.config
# WHY:
# - Contains the JWT secret key, signing algorithm, and default expiration values loaded from .env
from backend.core.config import settings


def hash_password(password: str) -> str:
    # Hash a plain-text password using bcrypt
    # WHY:
    # - Storing passwords in plain text is a severe security vulnerability
    # - This converts the password into an irreversible, secure cryptographic hash
    
    # 1. Generate salt value (default work factor 12)
    salt = bcrypt.gensalt()
    
    # 2. Compute hash and decode byte representation back to string
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify a plain-text password against a stored hash
    # WHY:
    # - Validates user credentials during login by hashing the input and comparing it to the DB value
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        # Return False if password encoding fails or parameters are invalid
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Generate a signed JWT Access Token
    # WHY:
    # - Access tokens are sent by the client in HTTP headers to access protected routes
    # - They contain payload data like user ID or username securely signed by the server
    
    # Create a copy of the payload data
    # WHY:
    # - Avoid mutating the original dictionary passed into the function
    to_encode = data.copy()
    
    # Determine the token expiration timestamp
    # WHY:
    # - If an explicit expires_delta is passed, use it; otherwise, use default from settings (e.g., 30 minutes)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Add expiration claim to the payload
    # WHY:
    # - "exp" is a standard JWT claim representing token expiration
    to_encode.update({"exp": expire})
    
    # Encode and sign the JWT token
    # WHY:
    # - Sign using jwt_secret_key and jwt_algorithm to prevent user tampering
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    # Return the signed token string
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    # Generate a signed JWT Refresh Token
    # WHY:
    # - Used to request a new Access Token when the short-lived Access Token expires
    # - Has a much longer duration (e.g., 7 days) and should be stored securely
    
    # Create a copy of the payload data
    to_encode = data.copy()
    
    # Set long-term expiration date
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    
    # Sign and encode the refresh token
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    # Return the signed token string
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    # Decode and validate a JWT access token
    # WHY:
    # - Verifies that the token was signed by our server and has not expired
    # - If valid, returns the decoded dictionary payload (e.g. user details); otherwise, returns None
    try:
        # Decode the token using settings keys
        # WHY:
        # - Validates the signature and verifies the "exp" claim automatically
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        # Return decoded payload
        return payload
    except JWTError:
        # Return None if token is invalid or expired
        # WHY:
        # - Gracefully informs the caller that authentication failed
        return None
