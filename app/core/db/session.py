from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config.setting import get_settings

engine = None
SessionLocal = None


def init_db():

    global engine, SessionLocal
    settings = get_settings()

    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set in environment variables")

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "Database not initialized. Did you call init_db() on startup?"
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
