#!/usr/bin/python3
"""
Mysql Database initialization module
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

DATABASE_URL = (
    f"mysql+mysqldb://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@"
    f"{getenv('DB_HOST')}/{getenv('DB_NAME')}"
)


engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
