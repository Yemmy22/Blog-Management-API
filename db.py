#!/usr/bin/python3
"""
Database connection module.

This module provides a singleton database connection class that manages
SQLAlchemy sessions for the application.

Classes:
    DB: Database connection manager singleton
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import DB_URI

class DB:
    """
    Database connection manager singleton.
    
    This class manages database connections and sessions using SQLAlchemy.
    Implements the singleton pattern to ensure only one instance exists.
    
    Attributes:
        _instance: Singleton instance of the class
        _session: SQLAlchemy scoped session
        _engine: SQLAlchemy engine instance
    """
    _instance = None
    _session = None
    _engine = None

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection."""
        try:
            self._engine = create_engine(DB_URI, pool_pre_ping=True)
            session_factory = sessionmaker(bind=self._engine)
            self._session = scoped_session(session_factory)
        except SQLAlchemyError as e:
            raise Exception(f"Failed to initialize database: {str(e)}")

    @property
    def session(self):
        """Get the current database session."""
        return self._session

    @property
    def engine(self):
        """Get the database engine."""
        return self._engine

    def close(self):
        """Close the current session."""
        if self._session:
            self._session.remove()
