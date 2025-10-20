"""
API routes for CodeDocs AI backend.
"""

from .auth_routes import auth_bp
from .project_routes import project_bp

__all__ = ['auth_bp', 'project_bp']

