# Import sessionmaker and Session from SQLAlchemy ORM
# WHY:
# - sessionmaker: factory used to create new database sessions
# - Session: type hint for better readability and IDE support
from sqlalchemy.orm import sessionmaker, Session


# Import the engine (database connection manager)
# WHY:
# - Sessions need the engine to communicate with the database
from backend.db.connection import engine


# Create a Session factory
# WHY:
# - This is used to generate new DB sessions whenever needed
# - Each session represents a "conversation" with the database
SessionLocal = sessionmaker(

    # Disable autocommit
    # WHY:
    # - Changes are NOT automatically saved
    # - You must explicitly call db.commit()
    # - Prevents accidental data loss or unwanted writes
    autocommit=False,

    # Disable autoflush
    # WHY:
    # - SQLAlchemy won’t automatically push changes before queries
    # - Gives you full control over when data is sent to DB
    autoflush=False,

    # Bind this session factory to the engine
    # WHY:
    # - Connects session to the actual database
    bind=engine
)


# Dependency function for FastAPI
# WHY:
# - Provides a database session per request
# - Ensures proper opening and closing of DB connections
def get_db() -> Session:

    # Docstring explanation
    # WHY:
    # - Clarifies this is used as a FastAPI dependency
    """FastAPI dependency — gives each request its own DB session and closes it after."""

    # Create a new session
    # WHY:
    # - Each request gets its own isolated session
    # - Prevents conflicts between users/requests
    db = SessionLocal()

    try:
        # Yield the session to the API endpoint
        # WHY:
        # - FastAPI uses this with Depends()
        # - Execution pauses here and resumes after request finishes
        yield db

    finally:
        # Always close the session
        # WHY:
        # - Releases DB connection back to pool
        # - Prevents memory leaks and connection exhaustion
        db.close()