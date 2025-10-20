"""
Setup script for CodeDocs AI backend.
Helps initialize the database and verify configuration.
"""

import sys
from config.database import init_db, test_db_connection
from config.settings import Config


def check_environment():
    """Check if all required environment variables are set."""
    print("\n[1/3] Checking environment variables...")
    
    try:
        Config.validate_config()
        print("[SUCCESS] All required environment variables are set")
        return True
    except ValueError as e:
        print(f"[FAILED] Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("See .env.example for reference.")
        return False


def setup_database():
    """Test connection and initialize database schema."""
    print("\n[2/3] Setting up database...")
    
    # Test connection
    print("  - Testing database connection...")
    if not test_db_connection():
        print("[FAILED] Database connection failed")
        print("\nPlease check your DATABASE_URL in .env file.")
        return False
    print("  [SUCCESS] Database connection successful")
    
    # Initialize schema
    print("  - Initializing database schema...")
    try:
        init_db()
        print("  [SUCCESS] Database schema initialized")
        return True
    except Exception as e:
        print(f"[FAILED] Database initialization failed: {e}")
        return False


def verify_services():
    """Verify external services are accessible."""
    print("\n[3/3] Verifying external services...")
    
    # Check AWS S3
    print("  - Checking AWS S3 access...")
    try:
        from services.s3_service import S3Service
        s3 = S3Service()
        # Try to list objects (should work even if bucket is empty)
        s3.list_files("")
        print("  [SUCCESS] AWS S3 accessible")
    except Exception as e:
        print(f"  [WARNING] AWS S3 check failed: {e}")
        print("     Make sure AWS credentials and bucket name are correct")
    
    # Check Claude API
    print("  - Checking Claude API access...")
    try:
        from services.claude_service import ClaudeService
        claude = ClaudeService()
        # Try a simple completion
        response = claude.generate_completion("Say 'API test successful'", max_tokens=10)
        if response:
            print("  [SUCCESS] Claude API accessible")
        else:
            print("  [WARNING] Claude API returned empty response")
    except Exception as e:
        print(f"  [WARNING] Claude API check failed: {e}")
        print("     Make sure CLAUDE_API_KEY is correct and has credits")
    
    # Check OpenAI API
    print("  - Checking OpenAI API access...")
    try:
        from services.embedding_service import EmbeddingService
        embedder = EmbeddingService()
        # Try creating a simple embedding
        embedding = embedder.create_embedding("test")
        if embedding and len(embedding) > 0:
            print("  [SUCCESS] OpenAI API accessible")
        else:
            print("  [WARNING] OpenAI API returned invalid embedding")
    except Exception as e:
        print(f"  [WARNING] OpenAI API check failed: {e}")
        print("     Make sure OPENAI_API_KEY is correct")
    
    return True


def main():
    """Run the setup process."""
    print("=" * 60)
    print("CodeDocs AI - Backend Setup")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n[FAILED] Setup failed: Environment configuration incomplete")
        sys.exit(1)
    
    # Step 2: Setup database
    if not setup_database():
        print("\n[FAILED] Setup failed: Database setup incomplete")
        sys.exit(1)
    
    # Step 3: Verify services (non-blocking)
    verify_services()
    
    # Success
    print("\n" + "=" * 60)
    print("[SUCCESS] Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now start the server with:")
    print("  python app.py")
    print("\nOr for production:")
    print("  gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'")
    print("=" * 60)


if __name__ == '__main__':
    main()

