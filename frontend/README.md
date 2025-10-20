# CodeDocs AI - Frontend

AI-powered code documentation generator with security scanning and RAG-powered chat assistant.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **HTTP Client:** Axios
- **Alerts:** SweetAlert2
- **Markdown:** react-markdown, react-syntax-highlighter

## Features

- 🎨 Modern dark bluish theme with responsive design
- 🔐 JWT-based authentication with secure storage
- 📁 Upload code folders or connect GitHub repositories
- 📝 AI-generated documentation with markdown editor
- 🛡️ Security vulnerability detection and analysis
- ✨ Code quality improvement suggestions
- 💬 RAG-powered chat assistant for code queries
- 📊 Multi-project dashboard with search and filtering

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   # Copy the example file
   cp .env.local.example .env.local
   ```

4. **Configure environment variables:**
   ```env
   # Edit .env.local
   NEXT_PUBLIC_API_URL=http://localhost:5000/api
   ```
   
   For production, update this to your deployed backend URL.

### Development

Run the development server:

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### Building for Production

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx           # Landing page
│   │   ├── login/             # Login page
│   │   ├── register/          # Register page
│   │   ├── dashboard/         # Dashboard page
│   │   ├── get-started/       # Upload/GitHub page
│   │   ├── projects/[id]/     # Project detail page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── label.tsx
│   │   │   ├── badge.tsx
│   │   │   └── tabs.tsx
│   │   ├── tabs/             # Tab components for project view
│   │   │   ├── DocumentationTab.tsx
│   │   │   ├── SecurityTab.tsx
│   │   │   ├── ImprovementsTab.tsx
│   │   │   └── ChatTab.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── UploadModal.tsx
│   │   └── GitHubConnectModal.tsx
│   ├── lib/                   # Utilities and configurations
│   │   ├── api.ts            # Axios client with auth interceptor
│   │   └── utils.ts          # Helper functions
│   └── types/                 # TypeScript type definitions
│       └── index.ts
├── public/                    # Static assets
├── package.json              # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.ts       # Tailwind CSS config
├── next.config.js           # Next.js config
└── README.md                # This file
```

## Key Components

### Authentication
- **Login/Register:** Custom auth with JWT tokens stored in localStorage
- **Protected Routes:** Automatic redirect to login if not authenticated
- **Auth Interceptor:** Automatically adds JWT to all API requests

### Project Management
- **Upload Modal:** Drag-drop interface for uploading code files
- **GitHub Modal:** Connect public/private GitHub repos with PAT support
- **Project Card:** Display project stats, language, security score
- **Dashboard:** Search and filter all projects

### Project View
- **Documentation Tab:** White background markdown viewer with edit capability
- **Security Tab:** List security findings with severity filters
- **Improvements Tab:** Code quality suggestions with priority filters
- **Chat Tab:** RAG-powered assistant for querying documentation

### Loading States
- All async operations use SweetAlert2 for consistent loading UI
- Progress polling for long-running operations (doc generation)

## API Integration

The frontend communicates with the Flask backend via REST API:

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Project Endpoints
- `GET /api/projects` - Get all user projects
- `POST /api/projects/upload` - Upload code files
- `POST /api/projects/github` - Connect GitHub repo
- `GET /api/projects/:id` - Get project details
- `GET /api/projects/:id/status` - Poll processing status
- `DELETE /api/projects/:id` - Delete project

### Project Data Endpoints
- `GET /api/projects/:id/documentation` - Get documentation
- `PUT /api/projects/:id/documentation` - Update documentation
- `GET /api/projects/:id/security` - Get security findings
- `GET /api/projects/:id/improvements` - Get code improvements
- `POST /api/projects/:id/chat` - Send chat message

## Deployment

### Vercel Deployment

1. **Connect repository to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your Git repository
   - Select the `frontend` directory as the root

2. **Configure environment variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com/api
   ```

3. **Deploy:**
   - Vercel will automatically build and deploy
   - Custom domain can be configured in settings

### Build Settings
- **Framework Preset:** Next.js
- **Root Directory:** frontend
- **Build Command:** npm run build
- **Output Directory:** .next

## Styling

### Tailwind Configuration
- Dark bluish theme with blue primary color
- Custom animations for loading states
- Responsive breakpoints for mobile/tablet/desktop

### Documentation Viewer
- White background with prose styling
- Syntax highlighting for code blocks
- Editable markdown with live preview

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues
- Ensure backend is running and accessible
- Check CORS configuration in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Build Errors
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Authentication Issues
- Clear localStorage: `localStorage.clear()` in browser console
- Check JWT token format in Network tab
- Verify backend auth endpoints are working

## Development Tips

### Hot Reload
Next.js supports hot module replacement. Changes to pages and components will reflect immediately.

### API Testing
Use the browser's Network tab to inspect API requests/responses.

### State Management
Currently using React hooks (useState, useEffect). Consider adding a state management library for complex state.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the GitHub repository.

