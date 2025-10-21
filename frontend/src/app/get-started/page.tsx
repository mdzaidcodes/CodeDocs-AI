'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Upload, Github, Code2, ArrowLeft } from 'lucide-react';
import Swal from 'sweetalert2';
import { isAuthenticated } from '@/lib/api';
import apiClient from '@/lib/api';
import UploadModal from '@/components/UploadModal';
import GitHubConnectModal from '@/components/GitHubConnectModal';

/**
 * Get Started Page Component
 * Presents two options: Upload code folder or Connect GitHub repo
 */
export default function GetStartedPage() {
  const router = useRouter();
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [githubModalOpen, setGithubModalOpen] = useState(false);

  /**
   * Check authentication on mount
   */
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  /**
   * Handle file upload submission
   * Uploads entire folder with nested structure preserved
   */
  const handleUploadSubmit = async (projectName: string, files: File[]) => {
    setUploadModalOpen(false);

    try {
      // Show processing alert
      Swal.fire({
        title: 'Uploading Files...',
        text: 'Please wait while we upload your code',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('project_name', projectName);
      formData.append('source_type', 'upload');
      
      // Append all files with their relative paths
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formData.append('files', file);
        
        // Send relative path for each file to preserve folder structure
        // @ts-ignore - webkitRelativePath exists but not in TypeScript types
        const relativePath = file.webkitRelativePath || file.name;
        formData.append('file_paths', relativePath);
      }

      // Upload files
      const response = await apiClient.post('/projects/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const projectId = response.data.data.project_id;

      // Start polling for status
      pollProjectStatus(projectId);
    } catch (error: any) {
      console.error('Upload error:', error);
      
      // Check if it's a quota exceeded error
      if (error.response?.status === 429 || error.response?.data?.error_code === 'QUOTA_EXCEEDED') {
        Swal.fire({
          icon: 'warning',
          title: 'Daily Quota Reached',
          html: error.response?.data?.message || "You&apos;ve reached your limit of 3 projects for today. Your quota will reset tomorrow. Thank you for your patience!",
          confirmButtonText: 'Understood',
          confirmButtonColor: '#3b82f6',
          background: '#1e293b',
          color: '#fff',
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Upload Failed',
          text: error.response?.data?.error || error.response?.data?.message || error.message || 'Failed to upload files',
          confirmButtonColor: '#3b82f6',
        });
      }
    }
  };

  /**
   * Handle GitHub connection submission
   */
  const handleGitHubSubmit = async (data: {
    projectName: string;
    url: string;
    branch: string;
    pat?: string;
  }) => {
    setGithubModalOpen(false);

    try {
      // Show processing alert
      Swal.fire({
        title: 'Connecting to GitHub...',
        text: 'Please wait while we clone your repository',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Send GitHub connection request
      const response = await apiClient.post('/projects/github', {
        project_name: data.projectName,
        github_url: data.url,
        github_branch: data.branch,
        github_pat: data.pat,
      });

      const projectId = response.data.data.project_id;

      // Start polling for status
      pollProjectStatus(projectId);
    } catch (error: any) {
      console.error('GitHub connection error:', error);
      
      // Check if it's a quota exceeded error
      if (error.response?.status === 429 || error.response?.data?.error_code === 'QUOTA_EXCEEDED') {
        Swal.fire({
          icon: 'warning',
          title: 'Daily Quota Reached',
          html: error.response?.data?.message || "You&apos;ve reached your limit of 3 projects for today. Your quota will reset tomorrow. Thank you for your patience!",
          confirmButtonText: 'Understood',
          confirmButtonColor: '#3b82f6',
          background: '#1e293b',
          color: '#fff',
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Connection Failed',
          text: error.response?.data?.error || error.response?.data?.message || error.message || 'Failed to connect to GitHub repository',
          confirmButtonColor: '#3b82f6',
        });
      }
    }
  };

  /**
   * Poll project status until processing is complete
   */
  const pollProjectStatus = async (projectId: string) => {
    // Show loading spinner with just title
    Swal.fire({
      title: 'Generating Documentation',
      allowOutsideClick: true,
      allowEscapeKey: true,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    const pollInterval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/projects/${projectId}/status`);
        const { status, progress, current_step, progress_percentage } = response.data.data;

        const progressValue = progress_percentage || progress || 0;

        // Update browser title with progress
        document.title = `Processing ${progressValue}% - CodeDocs AI`;

        // Keep showing spinner (no updates needed - just title and spinner)

        // Check if processing is complete
        if (status === 'completed') {
          clearInterval(pollInterval);
          document.title = 'CodeDocs AI';
          
          // Close any existing Swal alerts
          Swal.close();
          
          // Show success message briefly then redirect
          Swal.fire({
            icon: 'success',
            title: 'Documentation Ready!',
            text: 'Redirecting to your project...',
            showConfirmButton: false,
            timer: 1500,
            timerProgressBar: true,
          });

          // Auto-redirect immediately after brief success message
          setTimeout(() => {
            router.push(`/projects/${projectId}`);
          }, 1500);
          
        } else if (status === 'failed') {
          clearInterval(pollInterval);
          document.title = 'CodeDocs AI';
          
          Swal.fire({
            icon: 'error',
            title: 'Processing Failed',
            text: 'Failed to generate documentation. Please try again.',
            confirmButtonColor: '#3b82f6',
          });
        }
      } catch (error) {
        clearInterval(pollInterval);
        document.title = 'CodeDocs AI';
        console.error('Status polling error:', error);
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Failed to check processing status',
          confirmButtonColor: '#3b82f6',
        });
      }
    }, 3000); // Poll every 3 seconds
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center space-x-2 text-gray-300 hover:text-white">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Dashboard</span>
            </Link>
            <div className="flex items-center space-x-2">
              <Code2 className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-white">CodeDocs AI</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Get Started
          </h1>
          <p className="text-xl text-gray-300">
            Choose how you want to add your code
          </p>
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Upload Option */}
          <button
            onClick={() => setUploadModalOpen(true)}
            className="group bg-white/5 backdrop-blur-sm rounded-lg p-8 border-2 border-white/10 hover:border-blue-400 transition-all hover:scale-105"
          >
            <div className="bg-blue-500/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-blue-500/30 transition-colors">
              <Upload className="h-10 w-10 text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">Upload Folder</h2>
            <p className="text-gray-300 mb-6">
              Drag and drop your code files or select them from your computer
            </p>
            <div className="text-blue-400 font-semibold group-hover:text-blue-300">
              Choose Files →
            </div>
          </button>

          {/* GitHub Option */}
          <button
            onClick={() => setGithubModalOpen(true)}
            className="group bg-white/5 backdrop-blur-sm rounded-lg p-8 border-2 border-white/10 hover:border-blue-400 transition-all hover:scale-105"
          >
            <div className="bg-blue-500/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-blue-500/30 transition-colors">
              <Github className="h-10 w-10 text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">GitHub Repository</h2>
            <p className="text-gray-300 mb-6">
              Connect your GitHub repository (public or private with PAT)
            </p>
            <div className="text-blue-400 font-semibold group-hover:text-blue-300">
              Connect GitHub →
            </div>
          </button>
        </div>

        {/* Info Section */}
        <div className="mt-16 max-w-2xl mx-auto bg-blue-500/10 border border-blue-400/30 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-3">What happens next?</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">•</span>
              <span>Our AI will analyze your code structure and content</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">•</span>
              <span>Generate comprehensive documentation automatically</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">•</span>
              <span>Identify security vulnerabilities and code quality issues</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">•</span>
              <span>Enable RAG-powered chat for your codebase</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Modals */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onSubmit={handleUploadSubmit}
      />
      <GitHubConnectModal
        isOpen={githubModalOpen}
        onClose={() => setGithubModalOpen(false)}
        onSubmit={handleGitHubSubmit}
      />
    </div>
  );
}

