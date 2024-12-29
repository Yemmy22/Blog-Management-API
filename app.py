#!/usr/bin/python3
"""Entry point to link classes to tables and initialize the database."""
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from models import Base
from config import DB_URI

if __name__ == "__main__":
    try:
        engine = create_engine(DB_URI, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        print("Database and tables created successfully!")
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
