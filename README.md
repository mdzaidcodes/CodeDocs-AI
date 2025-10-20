# CodeDocs AI - Intelligent Code Documentation Generator

> **AI-powered tool that generates comprehensive documentation from uploaded code or GitHub repositories.**

Uses Claude API for code analysis, security scanning, and quality suggestions with a RAG-powered chat assistant.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Tech Stack](#-tech-stack)
- [Key Features](#-key-features)
- [Local Development Setup](#-local-development-setup)
- [Environment Configuration](#-environment-configuration)
- [Project Structure](#-project-structure)
- [Testing the Application](#-testing-the-application)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)

---

## 🚀 Project Overview

CodeDocs AI is a hackathon project that helps developers automatically generate high-quality documentation for their codebases using AI. Simply upload your code or connect a GitHub repository, and the AI will:

- 📖 Generate comprehensive documentation (purpose, setup, architecture, API references, usage)
- 🔒 Detect security vulnerabilities with severity ratings
- 💡 Provide code quality improvement suggestions
- 💬 Enable RAG-powered chat for querying your codebase

---

## 🛠 Tech Stack

### Frontend
- **Framework:** Next.js 14 with TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** React Hooks
- **HTTP Client:** Axios with JWT auth interceptors
- **Alerts:** SweetAlert2
- **Markdown:** react-markdown + react-syntax-highlighter
- **Hosting:** Vercel

### Backend
- **Framework:** Flask (Python 3.11+)
- **Authentication:** bcrypt + JWT
- **Database:** Supabase PostgreSQL with pgvector extension
- **Storage:** AWS S3
- **AI Services:**
  - Claude API (Anthropic) for code analysis
  - OpenAI for embeddings (RAG)
- **Hosting:** AWS EC2 with Elastic IP

---

## ✨ Key Features

1. **Multiple Upload Options**
   - Upload code folders directly via drag-and-drop
   - Connect GitHub repositories (public or private with PAT)

2. **AI-Generated Documentation**
   - Comprehensive markdown documentation
   - Syntax-highlighted code examples
   - Covers setup, architecture, API, and usage

3. **Security Analysis**
   - Vulnerability detection with severity ratings (Critical/High/Medium/Low)
   - File-level findings with line numbers
   - Actionable recommendations

4. **Code Quality Suggestions**
   - Performance improvements
   - Readability enhancements
   - Best practice recommendations
   - Maintainability tips

5. **RAG-Powered Chat Assistant**
   - Ask questions about your codebase in natural language
   - Context-aware responses using vector embeddings
   - Sources provided with answers

6. **Multi-Project Dashboard**
   - Manage multiple projects
   - Search and filter functionality
   - Project stats and metrics

---

## 🏠 Local Development Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** and **npm** (for frontend)
- **Python 3.11+** and **pip** (for backend)
- **Git** (for cloning repositories)

You'll also need accounts and credentials for:
- **Supabase** (PostgreSQL database with pgvector)
- **AWS S3** (file storage)
- **Anthropic** (Claude API key)
- **OpenAI** (API key for embeddings)

---

### 📦 Backend Setup (Flask)

#### Step 1: Navigate to Backend Directory

```bash
cd backend
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages including:
- Flask, Flask-CORS
- psycopg2-binary (PostgreSQL driver)
- boto3 (AWS S3 SDK)
- anthropic (Claude API)
- openai (OpenAI API)
- bcrypt, PyJWT (Authentication)
- python-dotenv (Environment variables)

#### Step 4: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   copy env.example .env     # Windows
   cp env.example .env       # macOS/Linux
   ```

2. **Edit `.env` file** and fill in all required values:

   ```env
   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   FRONTEND_URL=http://localhost:3000
   
   # Database (Supabase PostgreSQL with pgvector)
   DATABASE_URL=postgresql://username:password@host:5432/database
   
   # AWS S3
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   S3_BUCKET_NAME=your-bucket-name
   AWS_REGION=us-east-1
   
   # AI Services
   CLAUDE_API_KEY=your-claude-api-key
   OPENAI_API_KEY=your-openai-api-key
   
   # JWT
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

   **Important Notes:**
   - URL-encode special characters in your DATABASE_URL password (e.g., `@` → `%40`)
   - See `backend/env.example` for detailed explanations of each variable
   - Generate secure keys using: `python -c "import secrets; print(secrets.token_hex(32))"`

#### Step 5: Set Up Database Tables

Your Supabase database should have the following tables created:
- `users` (with `full_name`, `email`, `password_hash`)
- `projects`
- `security_findings`
- `code_improvements`
- `document_chunks` (with vector embedding column)
- `chat_messages`

**Note:** The app will skip automatic schema initialization if you've already created tables manually.

#### Step 6: Test Backend Setup

```bash
python setup.py
```

This validates all environment variables and database connectivity.

#### Step 7: Start Backend Server

**Option 1: Using the startup script (Recommended for Windows):**
```bash
start-dev.bat
```

**Option 2: Direct command:**
```bash
python app.py
```

The backend will start on **http://localhost:5000**

**Verify it's running:**
- Visit http://localhost:5000/health in your browser
- You should see: `{"status": "healthy", "service": "CodeDocs AI API", "version": "1.0.0"}`

---

### 🎨 Frontend Setup (Next.js)

#### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

#### Step 2: Install Dependencies

```bash
npm install
```

This will install all required packages including:
- Next.js 14, React, TypeScript
- Tailwind CSS, shadcn/ui
- Axios (HTTP client)
- SweetAlert2 (alerts)
- react-markdown (documentation viewer)

#### Step 3: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   copy env.example .env.local     # Windows
   cp env.example .env.local       # macOS/Linux
   ```

2. **Edit `.env.local` file:**

   ```env
   # Backend API URL
   # For local development, point to your local Flask backend
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```

   **Note:** The `NEXT_PUBLIC_` prefix is required for Next.js to expose this variable to the browser.

#### Step 4: Start Frontend Server

**Option 1: Using the startup script (Recommended for Windows):**
```bash
start-dev.bat
```

**Option 2: Direct command:**
```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

**Verify it's running:**
- Visit http://localhost:3000 in your browser
- You should see the CodeDocs AI landing page

---

### 🚀 Quick Start (Both Servers)

**For Windows users**, you can start both frontend and backend simultaneously:

```bash
# From the project root directory
start-dev-all.bat
```

This will:
1. Check that both `.env` and `.env.local` files exist
2. Start the backend server in a new window (http://localhost:5000)
3. Start the frontend server in a new window (http://localhost:3000)

---

## 🔐 Environment Configuration

### Backend Environment Variables (`.env`)

Located in `backend/.env`:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_ENV` | Yes | Flask environment mode | `development` |
| `SECRET_KEY` | Yes | Flask secret key for sessions | Random 32-byte hex string |
| `FRONTEND_URL` | Yes | Frontend URL for CORS | `http://localhost:3000` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `AWS_ACCESS_KEY_ID` | Yes | AWS IAM access key | From AWS Console |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS IAM secret key | From AWS Console |
| `S3_BUCKET_NAME` | Yes | S3 bucket name | `codedocs-ai-bucket` |
| `AWS_REGION` | Yes | AWS region | `us-east-1` |
| `CLAUDE_API_KEY` | Yes | Anthropic Claude API key | From Anthropic Console |
| `OPENAI_API_KEY` | Yes | OpenAI API key | From OpenAI Platform |
| `JWT_SECRET_KEY` | Yes | JWT signing secret | Random 32-byte hex string |

**CORS Configuration:**
The backend is configured to allow requests from `http://localhost:3000` by default. This is set in:
- `backend/config/settings.py` - Loads `FRONTEND_URL` from `.env`
- `backend/app.py` - Configures Flask-CORS with the allowed origin

### Frontend Environment Variables (`.env.local`)

Located in `frontend/.env.local`:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL | `http://localhost:5000/api` |

**API Client Configuration:**
The frontend API client is configured in `frontend/src/lib/api.ts`:
- Base URL defaults to `http://localhost:5000/api`
- Automatically attaches JWT token from localStorage to all requests
- Includes auth interceptors for token management
- Handles 401 (unauthorized) responses by redirecting to login

---

## 📦 Project Structure

```
CodeDocs-AI/
├── frontend/                      # Next.js 14 Frontend
│   ├── src/
│   │   ├── app/                  # App router pages
│   │   │   ├── page.tsx          # Landing page
│   │   │   ├── register/         # Registration page
│   │   │   ├── login/            # Login page
│   │   │   ├── dashboard/        # Projects dashboard
│   │   │   ├── get-started/      # Upload/GitHub connection
│   │   │   └── projects/[id]/    # Project detail view
│   │   ├── components/           # Reusable React components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── UploadModal.tsx
│   │   │   ├── GitHubConnectModal.tsx
│   │   │   ├── ProjectCard.tsx
│   │   │   └── ...
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts           # Axios client with auth
│   │   │   └── utils.ts
│   │   └── types/                # TypeScript type definitions
│   │       └── index.ts
│   ├── public/                   # Static assets
│   ├── package.json
│   ├── env.example               # Frontend env template
│   ├── start-dev.bat            # Windows startup script
│   └── tailwind.config.ts
│
├── backend/                       # Flask Backend
│   ├── config/                   # Configuration
│   │   ├── settings.py          # App config (loads .env)
│   │   └── database.py          # Database connection
│   ├── routes/                   # API endpoints
│   │   ├── auth_routes.py       # Authentication routes
│   │   └── project_routes.py    # Project routes
│   ├── models/                   # Database models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── security_finding.py
│   │   ├── code_improvement.py
│   │   └── documentation.py
│   ├── services/                 # Business logic
│   │   ├── auth_service.py
│   │   ├── s3_service.py
│   │   ├── github_service.py
│   │   ├── claude_service.py
│   │   ├── code_analyzer.py
│   │   ├── documentation_generator.py
│   │   ├── security_analyzer.py
│   │   ├── code_quality_analyzer.py
│   │   ├── embedding_service.py
│   │   └── rag_service.py
│   ├── utils/                    # Helper functions
│   │   ├── decorators.py        # @require_auth, @handle_errors
│   │   └── validators.py
│   ├── app.py                    # Flask app entry point
│   ├── setup.py                  # Setup validation script
│   ├── requirements.txt          # Python dependencies
│   ├── env.example               # Backend env template
│   └── start-dev.bat            # Windows startup script
│
├── start-dev-all.bat             # Start both servers (Windows)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🧪 Testing the Application

### 1. Test Backend API Health

**Endpoint:** `GET http://localhost:5000/health`

**Using browser:**
Visit http://localhost:5000/health

**Expected response:**
```json
{
  "status": "healthy",
  "service": "CodeDocs AI API",
  "version": "1.0.0"
}
```

### 2. Test User Registration

**Endpoint:** `POST http://localhost:5000/api/auth/register`

**Using the frontend:**
1. Open http://localhost:3000
2. Click "Get Started" → "Register"
3. Fill in:
   - First Name
   - Last Name
   - Email
   - Password
4. Click "Create Account"

**Expected result:**
- Success alert: "Account Created! Welcome, [Your Name]!"
- Redirect to "Get Started" page
- JWT token stored in localStorage
- User data stored in localStorage

**Verify in database:**
Check your Supabase `users` table for the new user with:
- `full_name`: "FirstName LastName"
- `email`: Your email
- `password_hash`: Bcrypt hash

### 3. Test User Login

**Endpoint:** `POST http://localhost:5000/api/auth/login`

**Using the frontend:**
1. Open http://localhost:3000/login
2. Enter email and password
3. Click "Login"

**Expected result:**
- Success alert: "Login Successful! Welcome back, [Your Name]!"
- Redirect to Dashboard
- JWT token refreshed in localStorage

### 4. Test Protected Routes

**Endpoints:** All `/api/projects/*` routes require authentication

**Using the frontend:**
1. After logging in, visit http://localhost:3000/dashboard
2. Dashboard should load without errors
3. Check browser DevTools → Network tab
4. API requests should include: `Authorization: Bearer <your-jwt-token>`

**If you're logged out:**
- Accessing protected routes should redirect to `/login`
- You'll see: "Session Expired. Please login again."

### 5. Test CORS Configuration

**What to check:**
1. Open http://localhost:3000 (frontend)
2. Open browser DevTools → Console
3. Perform any API action (login, register, etc.)
4. **Should NOT see CORS errors** like:
   - `Access-Control-Allow-Origin`
   - `CORS policy: No 'Access-Control-Allow-Origin' header`

**If you see CORS errors:**
- Check `backend/.env` has `FRONTEND_URL=http://localhost:3000`
- Restart the backend server
- Check `backend/config/settings.py` → `CORS_ORIGINS` includes your frontend URL

### 6. Test Project Creation (Once Fully Set Up)

**Endpoint:** `POST http://localhost:5000/api/projects/upload`

**Using the frontend:**
1. Go to http://localhost:3000/get-started
2. Click "Upload Code"
3. Drag and drop code files or select folder
4. Enter project name
5. Click "Upload"

**Expected result:**
- Progress indicator shows: "Uploading...", "Analyzing...", etc.
- Redirect to dashboard when complete
- New project appears in dashboard

---

## 🐛 Troubleshooting

### Backend Issues

#### ❌ "Database connection failed"

**Problem:** Cannot connect to Supabase PostgreSQL

**Solutions:**
1. **Check DATABASE_URL format:**
   ```
   postgresql://postgres.PROJECT:PASSWORD@host.pooler.supabase.com:6543/postgres
   ```
2. **URL-encode special characters in password:**
   - `@` → `%40`
   - `,` → `%2C`
   - Use this Python script:
     ```python
     from urllib.parse import quote_plus
     password = "your,pass@word"
     print(quote_plus(password))
     ```
3. **Check if database is paused** (Supabase free tier):
   - Go to Supabase dashboard
   - Click "Restore" if database is paused
4. **Use connection pooling URL:**
   - In Supabase → Settings → Database
   - Copy "Connection pooling" URL (port 6543)
   - NOT "Direct connection" URL (port 5432)

#### ❌ "UnicodeEncodeError" on Windows

**Problem:** Emojis in print statements fail on Windows console

**Solution:** Already fixed in `app.py` and `setup.py` - emojis replaced with `[SUCCESS]` / `[FAILED]` text

#### ❌ "ModuleNotFoundError: No module named 'X'"

**Problem:** Missing Python dependency

**Solutions:**
1. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

#### ❌ "Flask app not starting"

**Problem:** `python app.py` does nothing or errors

**Solutions:**
1. **Check `.env` file exists in `backend/` directory**
2. **Validate environment variables:**
   ```bash
   python setup.py
   ```
3. **Check if port 5000 is already in use:**
   - Windows: `netstat -ano | findstr :5000`
   - macOS/Linux: `lsof -i :5000`
   - Kill the process or use a different port

### Frontend Issues

#### ❌ "Network Error: Unable to connect to server"

**Problem:** Frontend can't reach backend

**Solutions:**
1. **Ensure backend is running:**
   - Visit http://localhost:5000/health
   - Should return JSON with "healthy" status
2. **Check `.env.local` file:**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```
3. **Restart frontend after env changes:**
   ```bash
   # Stop server (Ctrl+C), then:
   npm run dev
   ```

#### ❌ "CORS Error: No 'Access-Control-Allow-Origin' header"

**Problem:** Backend rejecting frontend requests

**Solutions:**
1. **Check backend `.env`:**
   ```env
   FRONTEND_URL=http://localhost:3000
   ```
2. **Restart backend server** after changing `.env`
3. **Verify CORS in backend:**
   - Open `backend/config/settings.py`
   - Check `CORS_ORIGINS` includes `http://localhost:3000`

#### ❌ "Error: The `prose` class does not exist"

**Problem:** Tailwind Typography plugin not installed

**Solution:** Already fixed - `@tailwindcss/typography` added to `package.json`

If still occurring:
```bash
npm install @tailwindcss/typography
```

#### ❌ "Session Expired" when accessing dashboard

**Problem:** JWT token expired or invalid

**Solutions:**
1. **Clear localStorage and login again:**
   - Open DevTools → Application → Local Storage
   - Clear `token` and `user` items
   - Go to login page
2. **Check JWT expiration** in `backend/config/settings.py`:
   ```python
   JWT_EXPIRATION_HOURS = 24  # Increase if needed
   ```

### Database Issues

#### ❌ "relation 'users' does not exist"

**Problem:** Database tables not created

**Solution:** Create tables manually in Supabase:
- See the database schema provided earlier
- Or enable auto-initialization in `backend/app.py`:
  ```python
  # Uncomment this line:
  init_db()
  ```

#### ❌ "password authentication failed"

**Problem:** Wrong database password

**Solutions:**
1. **Reset password** in Supabase dashboard
2. **URL-encode the new password** before adding to DATABASE_URL
3. **Use the correct connection string** from Supabase Settings → Database

---

## 🚀 Deployment

### Frontend (Vercel)

1. **Connect Repository:**
   - Go to [Vercel Dashboard](https://vercel.com)
   - Import your GitHub repository
   - Set root directory to `frontend`

2. **Configure Environment Variables:**
   - Add `NEXT_PUBLIC_API_URL` with your production backend URL
   - Example: `https://api.codedocs-ai.com/api`

3. **Deploy:**
   - Vercel will automatically build and deploy
   - Your site will be live at `your-project.vercel.app`

### Backend (AWS EC2)

1. **Launch EC2 Instance:**
   - Ubuntu 22.04 LTS
   - t2.small or larger
   - Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 5000 (Flask)

2. **Set Up Server:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python 3.11+
   sudo apt install python3.11 python3.11-venv python3-pip -y
   
   # Clone repository
   git clone <your-repo-url>
   cd CodeDocs-AI/backend
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure .env file
   nano .env
   ```

3. **Set Up Gunicorn:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Set Up Nginx (Reverse Proxy):**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/codedocs
   ```
   
   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name your-ec2-ip-or-domain;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable and Start:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/codedocs /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

6. **Set Up Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/codedocs.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=CodeDocs AI Backend
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/CodeDocs-AI/backend
   Environment="PATH=/home/ubuntu/CodeDocs-AI/backend/venv/bin"
   ExecStart=/home/ubuntu/CodeDocs-AI/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start:
   ```bash
   sudo systemctl enable codedocs
   sudo systemctl start codedocs
   ```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "full_name": "John Doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as register

### Project Endpoints

#### Get All Projects
```http
GET /api/projects
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "uuid",
        "name": "My Project",
        "description": "...",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### Upload Project
```http
POST /api/projects/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

project_name: "My Project"
files: [File, File, ...]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "status": "processing"
  }
}
```

#### Get Project Documentation
```http
GET /api/projects/:id/documentation
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "content": "# Documentation\n\n...",
    "sections": {
      "overview": "...",
      "setup": "..."
    }
  }
}
```

---

## 🔒 Security Notes

- **JWT Tokens:** Stored in localStorage, expires in 24 hours (configurable)
- **Password Hashing:** bcrypt with salt rounds
- **CORS:** Configured to allow only specified origins
- **Environment Variables:** Never commit `.env` or `.env.local` files
- **S3 Bucket:** Use IAM roles with minimal required permissions
- **API Keys:** Rotate regularly and monitor usage

---

## 🤝 Contributing

This is a hackathon project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

Created for a hackathon - CodeDocs AI

---

## 🙏 Acknowledgments

- **Claude AI** (Anthropic) for intelligent code analysis
- **OpenAI** for embeddings and RAG capabilities
- **shadcn/ui** for beautiful, accessible components
- **Next.js** and **Flask** communities for excellent documentation
- **Supabase** for managed PostgreSQL with pgvector
- **Vercel** and **AWS** for hosting infrastructure

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review environment variable configuration
3. Open an issue on GitHub

---

**Happy Coding! 🚀**
