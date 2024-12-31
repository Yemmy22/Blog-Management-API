#!/usr/bin/python3
"""Test database connection."""
from sqlalchemy import create_engine
from config import DB_URI

try:
    engine = create_engine(DB_URI, pool_pre_ping=True)
    connection = engine.connect()
    print("Connection to MySQL database was successful!")
    connection.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")

