# utils/db.py

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config
from exceptions.api_errors import DatabaseError

# Initialize engine and session factory
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy session object
        
    Raises:
        DatabaseError: If database operations fail
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}")
    finally:
        session.close()
