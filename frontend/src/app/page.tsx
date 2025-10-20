import Link from 'next/link';
import { 
  Code2, 
  Shield, 
  Sparkles, 
  MessageSquare, 
  Github, 
  Upload,
  CheckCircle,
  Zap,
  Lock,
  FileCode
} from 'lucide-react';

/**
 * Landing Page Component
 * Hero section with features and CTAs for new users
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Code2 className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-white">CodeDocs AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/login" 
                className="text-gray-300 hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link 
                href="/register" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            AI-Powered Code
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
              Documentation Generator
            </span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Upload your code or connect your GitHub repository to instantly generate 
            comprehensive documentation, security analysis, and quality improvements using Claude AI.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/register" 
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors flex items-center justify-center space-x-2"
            >
              <Sparkles className="h-5 w-5" />
              <span>Start Free</span>
            </Link>
            <a 
              href="#features" 
              className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors backdrop-blur-sm"
            >
              Learn More
            </a>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">5min</div>
            <div className="text-gray-300">Average Documentation Time</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">100%</div>
            <div className="text-gray-300">AI-Powered Analysis</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">24/7</div>
            <div className="text-gray-300">Available Support</div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Everything You Need for Better Documentation
          </h2>
          <p className="text-xl text-gray-300">
            Powered by Claude AI for intelligent code analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Feature 1: Upload Options */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Upload className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Multiple Upload Options
            </h3>
            <p className="text-gray-300">
              Upload code folders directly or connect GitHub repositories (public or private with PAT).
            </p>
          </div>

          {/* Feature 2: AI Documentation */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <FileCode className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Comprehensive Documentation
            </h3>
            <p className="text-gray-300">
              Auto-generate docs covering purpose, setup, architecture, API references, and usage examples.
            </p>
          </div>

          {/* Feature 3: Security Scanning */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Shield className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Security Vulnerability Detection
            </h3>
            <p className="text-gray-300">
              AI-powered security analysis identifies vulnerabilities with severity ratings and recommendations.
            </p>
          </div>

          {/* Feature 4: Code Quality */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Code Quality Suggestions
            </h3>
            <p className="text-gray-300">
              Get actionable improvements for performance, readability, and best practices.
            </p>
          </div>

          {/* Feature 5: RAG Chat */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <MessageSquare className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              RAG-Powered Chat Assistant
            </h3>
            <p className="text-gray-300">
              Ask questions about your code and get intelligent answers using retrieval-augmented generation.
            </p>
          </div>

          {/* Feature 6: Multi-Project */}
          <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10 hover:border-blue-400/50 transition-colors">
            <div className="bg-blue-500/20 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Github className="h-7 w-7 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Multi-Project Dashboard
            </h3>
            <p className="text-gray-300">
              Manage multiple projects with stats, search, and filtering in one unified dashboard.
            </p>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-300">
            Get started in minutes with our simple workflow
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-400">1</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Sign Up</h3>
            <p className="text-gray-300">Create your free account in seconds</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-400">2</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Upload Code</h3>
            <p className="text-gray-300">Upload folder or connect GitHub repo</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-400">3</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">AI Analysis</h3>
            <p className="text-gray-300">Claude AI generates comprehensive docs</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-500/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-400">4</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Review & Edit</h3>
            <p className="text-gray-300">View docs, security, and improvements</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-12 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Documentation?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join developers who are using AI to create better documentation
          </p>
          <Link 
            href="/register" 
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-block"
          >
            Get Started for Free
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Code2 className="h-6 w-6 text-blue-400" />
              <span className="text-lg font-bold text-white">CodeDocs AI</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2024 CodeDocs AI. Powered by Claude AI.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

