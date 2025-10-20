# CodeDocs AI - Backend

Flask backend with Claude AI integration for intelligent code documentation generation.

## 🛠 Tech Stack

- **Framework:** Flask 3.0
- **Language:** Python 3.11+
- **Database:** PostgreSQL (Supabase) with pgvector
- **Storage:** AWS S3
- **AI:** Claude API (Anthropic) for code analysis
- **Embeddings:** OpenAI for RAG
- **Authentication:** bcrypt + JWT

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Supabase recommended)
- AWS S3 bucket
- Claude API key (Anthropic)
- OpenAI API key

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Flask
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Claude API (Anthropic)
CLAUDE_API_KEY=your-claude-api-key

# OpenAI API (for embeddings)
OPENAI_API_KEY=your-openai-api-key

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRATION_HOURS=24

# CORS
FRONTEND_URL=http://localhost:3000
FRONTEND_URL_PROD=https://your-app.vercel.app
```

### 3. Initialize Database

The application will automatically create the database schema on first run:

```bash
python app.py
```

Or manually initialize:

```python
from config.database import init_db
init_db()
```

### 4. Run Development Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

### 5. Test API

```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

## 📁 Project Structure

```
backend/
├── config/                   # Configuration
│   ├── __init__.py
│   ├── settings.py          # App settings & env vars
│   └── database.py          # Database connection & schema
│
├── models/                   # Database models
│   ├── __init__.py
│   ├── user.py              # User model
│   ├── project.py           # Project model
│   ├── documentation.py     # Documentation model
│   ├── security_finding.py  # Security findings
│   ├── code_improvement.py  # Code improvements
│   └── embedding.py         # Vector embeddings
│
├── services/                 # Business logic
│   ├── __init__.py
│   ├── auth_service.py      # Authentication
│   ├── s3_service.py        # AWS S3 operations
│   ├── github_service.py    # GitHub integration
│   ├── claude_service.py    # Claude API wrapper
│   ├── embedding_service.py # OpenAI embeddings
│   ├── rag_service.py       # RAG implementation
│   ├── code_analyzer.py     # Code analysis
│   ├── documentation_generator.py  # Doc generation
│   ├── security_analyzer.py        # Security scanning
│   └── code_quality_analyzer.py    # Quality suggestions
│
├── routes/                   # API endpoints
│   ├── __init__.py
│   ├── auth_routes.py       # /api/auth/*
│   └── project_routes.py    # /api/projects/*
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── validators.py        # Input validation
│   ├── decorators.py        # Route decorators
│   └── helpers.py           # Helper functions
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # This file
```

## 🔌 API Endpoints

### Authentication

#### Register User
```
POST /api/auth/register
Body: {"name": "string", "email": "string", "password": "string"}
Response: {"success": true, "data": {"token": "...", "user": {...}}}
```

#### Login User
```
POST /api/auth/login
Body: {"email": "string", "password": "string"}
Response: {"success": true, "data": {"token": "...", "user": {...}}}
```

### Projects

#### Get All Projects
```
GET /api/projects
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {"projects": [...]}}
```

#### Upload Code Files
```
POST /api/projects/upload
Headers: Authorization: Bearer <token>
Form Data: 
  - project_name: string
  - files[]: File[]
Response: {"success": true, "data": {"project_id": "...", "status": "processing"}}
```

#### Connect GitHub Repository
```
POST /api/projects/github
Headers: Authorization: Bearer <token>
Body: {
  "project_name": "string",
  "github_url": "https://github.com/user/repo",
  "github_branch": "main",
  "github_pat": "optional_for_private_repos"
}
Response: {"success": true, "data": {"project_id": "...", "status": "processing"}}
```

#### Get Project Status
```
GET /api/projects/:id/status
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {"status": "...", "progress": 0-100, "current_step": "..."}}
```

#### Get Project Details
```
GET /api/projects/:id
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {...project}}
```

#### Get Documentation
```
GET /api/projects/:id/documentation
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {"content": "...", "sections": {...}}}
```

#### Update Documentation
```
PUT /api/projects/:id/documentation
Headers: Authorization: Bearer <token>
Body: {"content": "markdown content"}
Response: {"success": true, "message": "..."}
```

#### Get Security Findings
```
GET /api/projects/:id/security
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {"findings": [...]}}
```

#### Get Code Improvements
```
GET /api/projects/:id/improvements
Headers: Authorization: Bearer <token>
Response: {"success": true, "data": {"improvements": [...]}}
```

#### Chat with RAG Assistant
```
POST /api/projects/:id/chat
Headers: Authorization: Bearer <token>
Body: {"message": "What does this project do?"}
Response: {"success": true, "data": {"message": "...", "sources": [...]}}
```

#### Delete Project
```
DELETE /api/projects/:id
Headers: Authorization: Bearer <token>
Response: {"success": true, "message": "..."}
```

## 🔄 Processing Flow

When a project is uploaded or connected:

1. **Upload to S3** (0%)
   - Files are stored in AWS S3
   - Folder structure: `projects/{project_id}/...`

2. **Analyze Code Structure** (10%)
   - Count files, lines, detect language
   - Identify important files (README, config, entry points)

3. **Generate Documentation** (40%)
   - Claude AI analyzes code
   - Generates comprehensive markdown documentation
   - Sections: Overview, Setup, Architecture, API, Usage

4. **Security Analysis** (60%)
   - Claude AI scans for vulnerabilities
   - Categorizes by severity (critical → info)
   - Provides recommendations

5. **Code Quality Analysis** (80%)
   - Claude AI suggests improvements
   - Categories: Performance, Readability, Best Practices, Maintainability
   - Prioritizes suggestions

6. **Create Embeddings** (90%)
   - OpenAI creates vector embeddings
   - Stores in PostgreSQL with pgvector
   - Enables RAG-powered chat

7. **Complete** (100%)
   - Project status set to 'completed'
   - Ready for viewing and interaction

## 🗄 Database Schema

### Tables

- **users**: User accounts with auth
- **projects**: Code documentation projects
- **documentation**: Generated documentation
- **security_findings**: Security vulnerabilities
- **code_improvements**: Quality suggestions
- **embeddings**: Vector embeddings for RAG (with pgvector)

### Indexes

- User ID indexes on all tables
- Vector index on embeddings (IVFFlat for fast similarity search)
- Status and type indexes for filtering

## 🔐 Security

### Authentication
- bcrypt password hashing
- JWT tokens with configurable expiration
- `@require_auth` decorator for protected routes

### Authorization
- User ownership verification on all operations
- JWT payload includes user ID
- Database queries filter by user_id

### Data Protection
- Sensitive data in environment variables
- CORS configured for specific origins
- File type validation on uploads
- SQL injection protection (parameterized queries)

## 🚀 Deployment

### Production Setup

1. **Set Environment**
```env
FLASK_ENV=production
SECRET_KEY=strong-random-secret-key
```

2. **Use Production Server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

3. **Set Up Nginx Reverse Proxy**
```nginx
location /api {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### AWS EC2 Deployment

1. Launch EC2 instance (Ubuntu 22.04)
2. Install Python 3.11+
3. Clone repository
4. Install dependencies
5. Configure .env
6. Set up systemd service
7. Configure Nginx
8. Enable HTTPS with Let's Encrypt

## 🧪 Testing

### Manual API Testing

```bash
# Set environment variables
export API_URL="http://localhost:5000"
export TOKEN="your_jwt_token"

# Test endpoints
curl $API_URL/health
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/projects
```

### Database Testing

```python
from config.database import test_db_connection
test_db_connection()
```

## ⚠️ Troubleshooting

### Database Connection Issues
```
Error: could not connect to server
```
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check network/firewall settings

### pgvector Extension Missing
```
Error: extension "vector" does not exist
```
- Install pgvector extension in PostgreSQL
- Supabase has it pre-installed

### S3 Upload Failures
```
Error: Failed to upload file to S3
```
- Verify AWS credentials
- Check S3 bucket exists and permissions
- Verify region is correct

### Claude API Errors
```
Error: Failed to generate completion
```
- Check CLAUDE_API_KEY is valid
- Verify API quota/limits
- Check API endpoint is accessible

## 📝 Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| AWS_ACCESS_KEY_ID | AWS access key | `AKIA...` |
| AWS_SECRET_ACCESS_KEY | AWS secret key | `abc123...` |
| S3_BUCKET_NAME | S3 bucket name | `codedocs-files` |
| CLAUDE_API_KEY | Anthropic API key | `sk-ant-...` |
| OPENAI_API_KEY | OpenAI API key | `sk-...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | Random |
| JWT_SECRET_KEY | JWT signing key | Same as SECRET_KEY |
| JWT_EXPIRATION_HOURS | Token expiration | 24 |
| FRONTEND_URL | Frontend URL for CORS | `http://localhost:3000` |

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Claude API Docs](https://docs.anthropic.com/claude/reference)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Supabase Docs](https://supabase.com/docs)

## 🤝 Support

For issues and questions:
1. Check this README
2. Review API_CONTRACT.md in project root
3. Check application logs
4. Open an issue on GitHub

## 📄 License

MIT License - See LICENSE file for details

