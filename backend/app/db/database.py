"""Database compatibility module for application imports and migrations."""

from backend.app.db.session import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
