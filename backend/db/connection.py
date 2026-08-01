from sqlalchemy import create_engine
from backend.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # avoids stale connection errors
    pool_size=10,
    max_overflow=20,
)