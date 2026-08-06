# =====================================================================
# ECO MONITOR — AUTH_GUARD.PY
# Purpose: Implements Role-Based Access Control (RBAC) guards for protecting
#          routes based on user roles (INVESTOR, AUDITOR, ADMIN).
# =====================================================================

# Import HTTPException and status from fastapi
# WHY:
# - Used to return a 403 Forbidden status if a user lacks required permissions
from fastapi import Depends, HTTPException, status

# Import User model
from backend.models.user import User

# Import get_current_user dependency
from backend.core.dependencies import get_current_user

# Import List type from typing
from typing import List


class RoleChecker:
    # Role checking class validator
    # WHY:
    # - Enforces RBAC permissions declaratively on route controllers
    # - Usage: Depends(RoleChecker(["ADMIN", "AUDITOR"]))
    
    def __init__(self, allowed_roles: List[str]):
        # Store allowed roles list
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # Dependency invocation handler
        # WHY:
        # - Checks if the authenticated user's role is in the list of allowed roles
        # - If check succeeds, returns user object; otherwise, raises a 403 Forbidden error
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{current_user.role}' lacks sufficient privileges."
            )
            
        return current_user
