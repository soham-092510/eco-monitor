# =====================================================================
# ECO MONITOR — AUTH_MIDDLEWARE.PY
# Purpose: Intercepts incoming requests to perform basic audit logs or
#          context injection if JWT headers are present.
# =====================================================================

# Import BaseHTTPMiddleware and Request from fastapi
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

# Import decode_access_token to inspect headers
from backend.core.security import decode_access_token

# Import logger
from backend.middleware.logger import logger


class AuthMiddleware(BaseHTTPMiddleware):
    # Optional HTTP Middleware for intercepting authorizations
    # WHY:
    # - Operates globally at the request/response pipeline
    # - Extracts and prints calling identities in server logs for auditability
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get Auth header from the request
        auth_header = request.headers.get("Authorization")
        user_identity = "Anonymous"
        
        if auth_header and auth_header.startswith("Bearer "):
            # Extract token slice
            token = auth_header.split(" ")[1]
            # Decode payload
            payload = decode_access_token(token)
            if payload:
                # Retrieve subject (username)
                user_identity = payload.get("sub", "Unknown")
        
        # Log calling identity and requested path
        logger.info(f"Incoming Request | User: {user_identity} | Path: {request.url.path}")
        
        # Proceed with request execution chain
        response = await call_next(request)
        return response
