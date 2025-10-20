"""
Authentication routes for user registration and login.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.decorators import handle_errors
from utils.validators import validate_password

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@handle_errors
def register():
    """
    Register a new user.
    
    POST /api/auth/register
    Body: {first_name, last_name, email, password}
    Returns: {success, data: {token, user}}
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['first_name', 'last_name', 'email', 'password']):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: first_name, last_name, email, password'
        }), 400
    
    # Validate password
    is_valid, error = validate_password(data['password'])
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # Register user
    result = AuthService.register(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password']
    )
    
    return jsonify({
        'success': True,
        'data': result
    }), 201


@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """
    Login user and return JWT token.
    
    POST /api/auth/login
    Body: {email, password}
    Returns: {success, data: {token, user}}
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['email', 'password']):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: email, password'
        }), 400
    
    # Login user
    result = AuthService.login(
        email=data['email'],
        password=data['password']
    )
    
    return jsonify({
        'success': True,
        'data': result
    }), 200

