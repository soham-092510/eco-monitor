# Import Request object from FastAPI
# WHY:
# - Gives access to incoming request details (URL, headers, body, etc.)
from fastapi import Request, status


# Import JSONResponse to return custom JSON responses
# WHY:
# - Instead of default HTML errors, we return clean API-friendly JSON
from fastapi.responses import JSONResponse


# Import validation error exception
# WHY:
# - Triggered when request body/query params fail validation (Pydantic)
from fastapi.exceptions import RequestValidationError


# Import Starlette's HTTPException (FastAPI is built on Starlette)
# WHY:
# - This handles standard HTTP errors like 404, 403, 401, etc.
# - We alias it to avoid confusion with FastAPI's HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException


# Custom handler for HTTP exceptions (e.g., 404 Not Found)
# WHY:
# - Overrides default FastAPI error format
# - Gives consistent structure across API responses
async def http_exception_handler(request: Request, exc: StarletteHTTPException):

    # Return JSON response
    # WHY:
    # - Ensures API clients always receive structured JSON errors
    return JSONResponse(

        # Use the same status code as the exception
        # WHY:
        # - Preserves correct HTTP semantics (e.g., 404, 401)
        status_code=exc.status_code,

        # Custom response body
        # WHY:
        # - "error": message describing the issue
        # - "path": helps identify which endpoint caused the error
        content={
            "error": exc.detail,
            "path": str(request.url)
        },
    )


# Custom handler for validation errors (422)
# WHY:
# - Happens when request data doesn't match schema
# - Example: missing required field, wrong data type
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    return JSONResponse(

        # 422 status code (Unprocessable Entity)
        # WHY:
        # - Standard for validation errors in APIs
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

        # Custom response structure
        # WHY:
        # - "error": general message
        # - "details": exact validation issues from Pydantic
        content={
            "error": "Validation failed",
            "details": exc.errors()
        },
    )


# Catch-all handler for unexpected errors
# WHY:
# - Handles any unhandled exceptions in the app
# - Prevents crashing and leaking internal details
async def unhandled_exception_handler(request: Request, exc: Exception):

    return JSONResponse(

        # 500 Internal Server Error
        # WHY:
        # - Indicates something went wrong on server side
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

        # Safe error message (no sensitive info)
        # WHY:
        # - Avoid exposing stack traces or internal logic to users
        content={
            "error": "Internal server error"
        },
    )