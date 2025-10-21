"""
Authentication routes for user registration and login.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.decorators import handle_errors
from utils.validators import validate_password
from utils.rate_limiter import login_rate_limiter

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
    Rate limited: 5 attempts per 6 hours per email/IP combination.
    
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
    
    email = data['email']
    password = data['password']
    ip_address = request.remote_addr
    
    # Check rate limiting
    is_limited, attempts_remaining, reset_time = login_rate_limiter.is_rate_limited(email, ip_address)
    
    if is_limited:
        # Calculate hours until reset
        from datetime import datetime
        hours_remaining = round((reset_time - datetime.now()).total_seconds() / 3600, 1)
        
        return jsonify({
            'success': False,
            'error': 'Too many failed login attempts',
            'message': f'Account temporarily locked. Please try again in {hours_remaining} hours.',
            'rate_limit_info': {
                'max_attempts': 5,
                'lockout_period_hours': 6,
                'reset_time': reset_time.isoformat(),
                'attempts_remaining': 0
            }
        }), 429  # 429 Too Many Requests
    
    try:
        # Attempt login
        result = AuthService.login(email=email, password=password)
        
        # Clear rate limiting on successful login
        login_rate_limiter.clear_attempts(email, ip_address)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    except ValueError as e:
        # Record failed attempt
        login_rate_limiter.record_failed_attempt(email, ip_address)
        
        # Get updated attempts remaining
        _, attempts_remaining, _ = login_rate_limiter.is_rate_limited(email, ip_address)
        
        # Construct error message with attempts remaining
        error_message = str(e)
        if attempts_remaining > 0:
            error_message += f" ({attempts_remaining} attempt{'s' if attempts_remaining != 1 else ''} remaining)"
        
        return jsonify({
            'success': False,
            'error': error_message,
            'attempts_remaining': attempts_remaining
        }), 401

