# Import BaseSettings from pydantic_settings
# WHY:
# - This allows us to automatically read environment variables (from .env file or system)
# - Converts them into Python variables with type validation
# - Helps avoid hardcoding secrets like DB URL, JWT keys
from pydantic_settings import BaseSettings


# Define a Settings class that will hold ALL configuration of the app
# WHY:
# - Central place for configuration (single source of truth)
# - Easy to import anywhere in the project
# - Keeps code clean and maintainable
class Settings(BaseSettings):

    # Application name
    # WHY:
    # - Used in FastAPI title, logging, monitoring, etc.
    # - Default value provided in case not defined in .env
    app_name: str = "green-finance"

    # Environment type (development, staging, production)
    # WHY:
    # - Helps control behavior (e.g., debug logs only in development)
    environment: str = "development"

    # Database connection URL (PostgreSQL / SQLite)
    # WHY:
    # - Required to connect backend to database
    # - No default → must be provided in .env (important for safety)
    database_url: str

    # Redis connection URL
    # WHY:
    # - Used for caching, background jobs, sessions, etc.
    # - Again, required → must come from .env
    redis_url: str

    # Secret key for JWT authentication
    # WHY:
    # - Used to sign tokens securely
    # - MUST NOT be hardcoded → must come from .env for security
    jwt_secret_key: str

    # Algorithm used for JWT encoding
    # WHY:
    # - Defines how tokens are encrypted
    # - HS256 is a common and secure default
    jwt_algorithm: str = "HS256"

    # Access token expiry time (in minutes)
    # WHY:
    # - Controls how long user stays logged in
    # - Short expiry improves security
    access_token_expire_minutes: int = 30

    # Refresh token expiry (in days)
    # WHY:
    # - Used to generate new access tokens without re-login
    # - Longer expiry for better user experience
    refresh_token_expire_days: int = 7


    # Internal configuration for Pydantic
    # WHY:
    # - Controls how environment variables are read
    class Config:

        # Specifies that variables should be loaded from ".env" file
        # WHY:
        # - Allows storing secrets/config outside code
        # - Makes app portable across environments
        env_file = ".env"

        # Makes variable names case-insensitive
        # WHY:
        # - So DATABASE_URL and database_url both work
        # - Avoids bugs due to casing mismatch
        case_sensitive = False


# Create a single instance of Settings
# WHY:
# - This object will be imported everywhere in the app
# - Ensures config is loaded only once (efficient)
# - Example usage anywhere:
#   from backend.core.config import settings
#   print(settings.database_url)
settings = Settings()