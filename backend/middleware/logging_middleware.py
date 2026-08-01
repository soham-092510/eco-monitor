# Import time module
# WHY:
# - Used to measure how long each request takes
import time


# Import BaseHTTPMiddleware from Starlette
# WHY:
# - Middleware allows you to run code before and after each request
# - BaseHTTPMiddleware is the base class for creating custom middleware
from starlette.middleware.base import BaseHTTPMiddleware


# Import Request object
# WHY:
# - Gives access to request data (method, URL, headers, etc.)
from starlette.requests import Request


# Import your custom logger
# WHY:
# - Used to log request details instead of using print()
from backend.middleware.logger import logger


# Create custom logging middleware
# WHY:
# - This middleware logs every incoming request automatically
# - Useful for debugging, monitoring, and performance tracking
class LoggingMiddleware(BaseHTTPMiddleware):

    # Override dispatch method (core middleware logic)
    # WHY:
    # - dispatch() runs for every request
    # - call_next is used to pass request to next handler (route)
    async def dispatch(self, request: Request, call_next):

        # Record start time of request
        # WHY:
        # - Used to calculate how long request takes
        start_time = time.time()


        # Process the request and get response
        # WHY:
        # - call_next sends request to actual API endpoint
        # - Without this, request would never reach your route
        response = await call_next(request)


        # Calculate request duration in milliseconds
        # WHY:
        # - Helps track API performance
        # - Useful for identifying slow endpoints
        duration_ms = round((time.time() - start_time) * 1000, 2)


        # Log request details
        # WHY:
        # - Provides visibility into API usage
        # - Includes method, path, status, and response time
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} duration={duration_ms}ms"
        )


        # Return response back to client
        # WHY:
        # - Middleware must always return a response
        return response