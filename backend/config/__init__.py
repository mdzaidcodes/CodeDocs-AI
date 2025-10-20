"""
Configuration module for CodeDocs AI backend.
Contains database, API, and service configurations.
"""

from .database import get_db_connection, init_db
from .settings import Config

__all__ = ['get_db_connection', 'init_db', 'Config']

