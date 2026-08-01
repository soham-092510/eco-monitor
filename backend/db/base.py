# Import DeclarativeBase from SQLAlchemy ORM
# WHY:
# - SQLAlchemy uses a "declarative system" to define database tables as Python classes
# - DeclarativeBase is the modern (SQLAlchemy 2.0) way to create a base class
# - All ORM models (tables) must inherit from this base so SQLAlchemy can track them
from sqlalchemy.orm import DeclarativeBase


# Create a Base class for all database models
# WHY:

# - This acts as the parent class for every table in your database
# - Example: User, Transaction, CarbonRecord will inherit from this
# - It allows SQLAlchemy to collect metadata of all models in one place
class Base(DeclarativeBase):

    # Docstring (documentation string)
    # WHY:
    # - Helps developers understand purpose of this class
    # - No effect on execution, only for readability and documentation
    """Base class all ORM models inherit from."""

    # pass means "do nothing"
    # WHY:
    # - We don't need to define anything inside this class right now
    # - It simply exists to be inherited by other models
    pass