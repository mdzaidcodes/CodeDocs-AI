"""
CodeDocs AI - Flask Backend Application
Main application file with Flask setup, CORS, and route registration.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import Config
from config.database import init_db, test_db_connection
from routes import auth_bp, project_bp


def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        Flask app instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints (routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'service': 'CodeDocs AI API',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API info."""
        return jsonify({
            'service': 'CodeDocs AI API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'projects': '/api/projects',
                'health': '/health'
            }
        }), 200
    
    # Global error handler
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


def main():
    """
    Main entry point for the application.
    Initializes database and starts Flask server.
    """
    print("=" * 60)
    print("CodeDocs AI - Backend Server")
    print("=" * 60)
    
    # Test database connection
    print("\n[1/3] Testing database connection...")
    if not test_db_connection():
        print("[FAILED] Database connection failed!")
        print("Please check your DATABASE_URL in .env file")
        return
    print("[SUCCESS] Database connection successful")
    
    # Initialize database schema (skip if you've already set up tables manually)
    print("\n[2/3] Checking database schema...")
    try:
        # Uncomment the line below if you want to auto-initialize tables
        # init_db()
        print("[SKIPPED] Database schema check (tables created manually)")
    except Exception as e:
        print(f"[FAILED] Database initialization failed: {e}")
        return
    
    # Create Flask app
    print("\n[3/3] Starting Flask application...")
    app = create_app()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Server ready!")
    print(f"Environment: {Config.FLASK_ENV}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Allowed CORS origins: {', '.join(Config.CORS_ORIGINS)}")
    print("=" * 60)
    print("\nEndpoints:")
    print("  - POST   /api/auth/register")
    print("  - POST   /api/auth/login")
    print("  - GET    /api/projects")
    print("  - POST   /api/projects/upload")
    print("  - POST   /api/projects/github")
    print("  - GET    /api/projects/:id")
    print("  - GET    /api/projects/:id/status")
    print("  - GET    /api/projects/:id/documentation")
    print("  - PUT    /api/projects/:id/documentation")
    print("  - GET    /api/projects/:id/security")
    print("  - GET    /api/projects/:id/improvements")
    print("  - POST   /api/projects/:id/chat")
    print("  - DELETE /api/projects/:id")
    print("  - GET    /health")
    print("=" * 60)
    print("\n[STARTING] Server starting on http://0.0.0.0:5000")
    print("Press CTRL+C to stop\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )


if __name__ == '__main__':
    main()

