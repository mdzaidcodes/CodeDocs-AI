"""
Application configuration settings.
Loads environment variables and provides configuration classes.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Check if we should use AWS Secrets Manager
USE_SECRETS_MANAGER = os.environ.get('USE_SECRETS_MANAGER', 'true').lower() != 'false'

# Load secrets BEFORE defining Config class
def _load_environment():
    """Load environment variables from AWS Secrets Manager or .env file."""
    if USE_SECRETS_MANAGER:
        print("🔐 Production mode: Loading configuration from AWS Secrets Manager...")
        try:
            # Import here to avoid circular imports
            import boto3
            import json
            
            aws_region = os.environ.get('AWS_REGION', 'me-central-1')
            secret_name = os.environ.get('SECRET_NAME', 'codedocs-ai')
            
            # Get secrets directly without importing utils.secrets_manager
            client = boto3.client('secretsmanager', region_name=aws_region)
            response = client.get_secret_value(SecretId=secret_name)
            secrets = json.loads(response['SecretString'])
            
            # Set environment variables
            for key, value in secrets.items():
                os.environ[key] = str(value)
            
            print(f"✅ Successfully loaded {len(secrets)} secrets from AWS Secrets Manager")
            return True
        except Exception as e:
            print(f"❌ Error loading from Secrets Manager: {e}")
            print("⚠️  Falling back to local .env file")
            load_dotenv()
            return False
    else:
        print("🔧 Development mode: Loading configuration from .env file...")
        load_dotenv()
        return True

# Load environment before defining Config
_load_environment()


class Config:
    """Base configuration class with all settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Database settings (Supabase PostgreSQL)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
        raise ValueError("AWS credentials and bucket name are required")
    
    # Claude API settings (Anthropic)
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY environment variable is required")
    
    CLAUDE_MODEL = 'claude-sonnet-4-20250514'  # Claude Sonnet 4.5
    CLAUDE_MAX_TOKENS = 4096
    
    # OpenAI API settings (for embeddings)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'
    EMBEDDING_DIMENSION = 1536
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    JWT_ALGORITHM = 'HS256'
    
    # CORS settings
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    FRONTEND_URL_PROD = os.getenv('FRONTEND_URL_PROD', '')
    
    # Build CORS origins list
    CORS_ORIGINS = [FRONTEND_URL]
    
    # Add production frontend URL if specified
    if FRONTEND_URL_PROD:
        CORS_ORIGINS.append(FRONTEND_URL_PROD)
    
    # Add Vercel preview URLs (for deployment previews)
    if os.getenv('ALLOW_VERCEL_PREVIEWS', 'true').lower() == 'true':
        CORS_ORIGINS.append('https://*.vercel.app')
    
    # Allow all origins in development (for testing)
    if FLASK_ENV == 'development' and os.getenv('CORS_ALLOW_ALL', 'false').lower() == 'true':
        CORS_ORIGINS = ['*']
    
    # File upload settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max total upload
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB per file
    ALLOWED_EXTENSIONS = {
        '.js', '.jsx', '.ts', '.tsx',
        '.py', '.java', '.cpp', '.c', '.h', '.cs',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.html', '.css', '.scss', '.sass', '.less',
        '.json', '.xml', '.yml', '.yaml',
        '.md', '.txt', '.sh', '.bash'
    }
    
    # Processing settings
    ANALYSIS_BATCH_SIZE = 10  # Files to analyze at once
    MAX_FILE_SIZE_FOR_ANALYSIS = 1024 * 1024  # 1MB max per file for analysis
    
    # Redis settings (for background tasks)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    @classmethod
    def validate_config(cls):
        """Validate all required configuration variables."""
        required = [
            'DATABASE_URL',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'S3_BUCKET_NAME',
            'CLAUDE_API_KEY',
            'OPENAI_API_KEY',
        ]
        
        missing = []
        for var in required:
            if not getattr(cls, var, None):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True


# Validate configuration on import
Config.validate_config()

