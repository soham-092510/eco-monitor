# =====================================================================
# ECO MONITOR — CONNECTION.PY (DATABASE ENGINE INITIALIZATION)
# =====================================================================
# Purpose/Existence of this file:
# This file is responsible for establishing the pipe/channel to our database.
# Think of it like dialing a telephone number. This code sets up the speed dial, 
# configurations, and keeps the line open so the application can communicate with 
# SQLite or PostgreSQL databases.
# =====================================================================

# 🔹 Import create_engine
# create_engine is a function from the "sqlalchemy" database library.
# It acts like the actual telephone company technician that wires the connection 
# between our app and the database.
from sqlalchemy import create_engine

# 🔹 Import settings
# We import our configuration manager settings so we can read the database address (database_url).
from backend.core.config import settings


# 🔹 Configure dialect-specific connection options
# "Dialect" is the database engine brand (e.g. SQLite dialect vs PostgreSQL dialect).
# We check if the address starts with "sqlite" or not, because different brands
# require different wiring arguments.
if settings.database_url.startswith("sqlite"):
    # If using SQLite:
    # 1. We create the engine.
    # 2. We pass `connect_args={"check_same_thread": False}`.
    #    WHY: SQLite is a lightweight single-file database. By default, it only allows 
    #    the same thread/worker to talk to it. But FastAPI handles multiple visitors at once 
    #    using different workers. Setting this to False allows all workers to safely query SQLite.
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
else:
    # If using PostgreSQL:
    # 1. `pool_pre_ping=True`: Before sending a query, ping the database to verify if 
    #    the connection is still alive. If it died, reset it.
    # 2. `pool_size=10`: Keep 10 connections open and waiting at all times so we don't 
    #    waste time dialing every time.
    # 3. `max_overflow=20`: If 10 connections are busy, we can open up to 20 more temporary lines.
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# =====================================================================
# 🕸️ CONNECTIONS & WORKFLOW (How this file communicates with others):
# =====================================================================
# 1. READS FROM:
#    - [config.py](file:///c:/Users/HP/Downloads/Projects/eco-monitor/backend/core/config.py):
#      Reads `settings.database_url` configuration.
#
# 2. READ BY (CONNECTIONS):
#    - [session.py](file:///c:/Users/HP/Downloads/Projects/eco-monitor/backend/db/session.py):
#      Imports this `engine` to bind connection sessions (which carry queries back and forth).
#    - [database.py](file:///c:/Users/HP/Downloads/Projects/eco-monitor/backend/db/database.py):
#      Imports `engine` to execute table creation script `Base.metadata.create_all(bind=engine)` on startup.
# =====================================================================