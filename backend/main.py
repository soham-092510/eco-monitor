# Import FastAPI framework
# WHY:
# - Core framework used to build your API
from fastapi import FastAPI


# Import HTTP exception from Starlette (base framework of FastAPI)
# WHY:
# - Used for handling standard HTTP errors (404, 401, etc.)
from starlette.exceptions import HTTPException as StarletteHTTPException


# Import validation error exception
# WHY:
# - Triggered when request data fails validation (Pydantic)
from fastapi.exceptions import RequestValidationError


# Import Prometheus instrumentator
# WHY:
# - Adds monitoring metrics (request count, latency, etc.)
# - Useful for production monitoring (DevOps / observability)
from prometheus_fastapi_instrumentator import Instrumentator


# Import application settings
# WHY:
# - Centralized configuration (app name, DB URL, etc.)
from backend.core.config import settings


# Import logging middleware
# WHY:
# - Logs every request automatically
from backend.middleware.logging_middleware import LoggingMiddleware


# Import custom error handlers
# WHY:
# - Ensures consistent error responses across the API
from backend.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)


# Import DB initialization function
# WHY:
# - Creates tables automatically on startup (dev only)
from backend.db.database import init_db


# Import API routes (health check)
# WHY:
# - Keeps routes modular and clean
from backend.api import health


# Create FastAPI app instance
# WHY:
# - This is the main application object
# - title/version used in Swagger docs
app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)


# ------------------ Middleware ------------------

# Add logging middleware
# WHY:
# - Logs every request (method, path, duration, status)
app.add_middleware(LoggingMiddleware)


# ------------------ Exception Handlers ------------------

# Handle HTTP errors (404, 401, etc.)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# Handle validation errors (422)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Handle all unexpected errors (500)
app.add_exception_handler(Exception, unhandled_exception_handler)


# ------------------ Routes ------------------

# Include health check routes
# WHY:
# - Keeps API modular (routes separated into files)
app.include_router(health.router)


# ------------------ Monitoring ------------------

# Enable Prometheus metrics endpoint
# WHY:
# - Tracks API performance (latency, request count, etc.)
# - Exposes metrics at /metrics endpoint
Instrumentator().instrument(app).expose(app)


# ------------------ Startup Event ------------------

# Run code when app starts
# WHY:
# - Used to initialize resources (like DB tables)
@app.on_event("startup")
def on_startup():

    # Initialize database
    # WHY:
    # - Creates tables automatically (development only)
    init_db()