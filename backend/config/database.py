"""
Database connection and initialization.
Handles PostgreSQL connection with pgvector extension for embeddings.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import Config


def get_db_connection():
    """
    Get a database connection.
    Returns a connection object with RealDictCursor for dict-like row access.
    Configured with 30 minute timeout for long-running operations.
    """
    try:
        conn = psycopg2.connect(
            Config.DATABASE_URL,
            cursor_factory=RealDictCursor,
            connect_timeout=30,  # 30 seconds to establish connection
            keepalives=1,
            keepalives_idle=30,  # Start sending keepalives after 30 seconds
            keepalives_interval=10,  # Send keepalive every 10 seconds
            keepalives_count=5,  # Close after 5 failed keepalives
            options='-c statement_timeout=1800000'  # 30 minutes (1800000ms)
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database operations.
    Automatically handles connection and cursor cleanup.
    
    Args:
        commit: Whether to commit the transaction on success
        
    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO ...")
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_db():
    """
    Initialize database schema.
    Creates all necessary tables and extensions.
    """
    
    # SQL statements for table creation
    schema_sql = """
    -- Enable pgvector extension for embeddings
    CREATE EXTENSION IF NOT EXISTS vector;
    
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Projects table
    CREATE TABLE IF NOT EXISTS projects (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('upload', 'github')),
        github_url TEXT,
        github_branch VARCHAR(255),
        language VARCHAR(50),
        file_count INTEGER DEFAULT 0,
        security_score INTEGER,
        status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
        progress INTEGER DEFAULT 0,
        current_step TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Documentation table
    CREATE TABLE IF NOT EXISTS documentation (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        sections JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Security findings table
    CREATE TABLE IF NOT EXISTS security_findings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
        title VARCHAR(500) NOT NULL,
        description TEXT NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        line_number INTEGER,
        recommendation TEXT NOT NULL,
        category VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Code improvements table
    CREATE TABLE IF NOT EXISTS code_improvements (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        type VARCHAR(50) NOT NULL CHECK (type IN ('performance', 'readability', 'best-practice', 'maintainability')),
        title VARCHAR(500) NOT NULL,
        description TEXT NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        line_number INTEGER,
        suggestion TEXT NOT NULL,
        priority VARCHAR(50) NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Embeddings table for RAG
    CREATE TABLE IF NOT EXISTS embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        embedding vector(1536),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
    CREATE INDEX IF NOT EXISTS idx_documentation_project_id ON documentation(project_id);
    CREATE INDEX IF NOT EXISTS idx_security_findings_project_id ON security_findings(project_id);
    CREATE INDEX IF NOT EXISTS idx_security_findings_severity ON security_findings(severity);
    CREATE INDEX IF NOT EXISTS idx_code_improvements_project_id ON code_improvements(project_id);
    CREATE INDEX IF NOT EXISTS idx_code_improvements_type ON code_improvements(type);
    CREATE INDEX IF NOT EXISTS idx_embeddings_project_id ON embeddings(project_id);
    
    -- Create vector index for embeddings (for fast similarity search)
    CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    
    -- Create trigger to update updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    CREATE TRIGGER update_documentation_updated_at BEFORE UPDATE ON documentation
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Execute schema creation
            cursor.execute(schema_sql)
            print("Database schema initialized successfully")
            return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def test_db_connection():
    """
    Test database connection and pgvector extension.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # Test pgvector extension
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            vector_ext = cursor.fetchone()
            
            if result and vector_ext:
                print("Database connection successful")
                print("pgvector extension is installed")
                return True
            else:
                print("Database connection failed or pgvector not installed")
                return False
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

