"""
Database configuration: SQLAlchemy base, engine, session factory, and init.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.settings import get_settings

# Declarative base shared by all ORM models
Base = declarative_base()

_engine = None
_SessionLocal = None


def init_db() -> None:
    """
    Initialise the database engine and create all tables.

    Called once during application startup via the lifespan handler.

    Raises:
        RuntimeError: If DATABASE_URL is not configured.
    """
    global _engine, _SessionLocal

    settings = get_settings()

    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Import models so SQLAlchemy registers them before create_all
    from app.modules.auth.model import RefreshToken, User  # noqa: F401
    from app.modules.chat.model import Chat  # noqa: F401

    Base.metadata.create_all(bind=_engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a DB session and closes it after the request.

    Raises:
        RuntimeError: If init_db() has not been called yet.
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialised. Ensure init_db() ran on startup.")

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
