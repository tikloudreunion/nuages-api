from contextlib import contextmanager

from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///development.sqlite3"
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_database():
    """Context manager for database sessions."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_database_session():
    """Dependency for FastAPI to get database session."""
    with get_database() as session:
        yield session
