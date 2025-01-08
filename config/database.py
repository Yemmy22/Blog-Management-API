# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqldb://user:password@localhost/blog_db"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
