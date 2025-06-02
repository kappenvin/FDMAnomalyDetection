"""Database dependency and session management."""

from sqlalchemy.orm import Session
import sys
import os

# Add the database_src directory to the path
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../../data_processing/database_src")
)

from database import Session as DatabaseSession


def get_db() -> Session:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()
