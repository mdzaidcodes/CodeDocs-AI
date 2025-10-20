"""
Decorators for route protection and error handling.
"""

from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config


def require_auth(f):
    """
    Decorator to protect routes with JWT authentication.
    Extracts user_id from JWT token and passes it to the route function.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route(user_id):
            return {'message': f'Hello user {user_id}'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Authorization header missing'
            }), 401
        
        try:
            # Extract token from "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format'
                }), 401
            
            token = parts[1]
            
            # Decode JWT token
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM]
            )
            
            # Extract user_id from payload
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token payload'
                }), 401
            
            # Pass user_id to the route function
            return f(user_id=user_id, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Authentication failed'
            }), 401
    
    return decorated_function


def handle_errors(f):
    """
    Decorator to handle common errors and return JSON responses.
    
    Usage:
        @app.route('/api/endpoint')
        @handle_errors
        def endpoint():
            # Your code here
            return {'data': 'success'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except PermissionError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 403
        except FileNotFoundError as e:
            return jsonify({
                'success': False,
                'error': 'Resource not found'
            }), 404
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    return decorated_function

