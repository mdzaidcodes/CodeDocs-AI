'use client';

import { useState } from 'react';
import { X, Github, GitBranch, Key } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface GitHubConnectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { projectName: string; url: string; branch: string; pat?: string }) => void;
}

/**
 * GitHub Connect Modal Component
 * Allows users to connect GitHub repositories (public or private with PAT)
 */
export default function GitHubConnectModal({ isOpen, onClose, onSubmit }: GitHubConnectModalProps) {
  const [formData, setFormData] = useState({
    projectName: '',
    url: '',
    branch: 'main',
    pat: '',
  });
  const [isPrivate, setIsPrivate] = useState(false);

  /**
   * Handle input change
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Prepare submission data
    const submitData = {
      projectName: formData.projectName,
      url: formData.url,
      branch: formData.branch || 'main',
      ...(isPrivate && formData.pat && { pat: formData.pat }),
    };
    
    onSubmit(submitData);
    
    // Reset form
    setFormData({
      projectName: '',
      url: '',
      branch: 'main',
      pat: '',
    });
    setIsPrivate(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg w-full max-w-2xl border border-white/10">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <Github className="h-6 w-6 text-white" />
            <h2 className="text-2xl font-bold text-white">Connect GitHub Repository</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Project Name */}
          <div className="space-y-2">
            <Label htmlFor="projectName" className="text-gray-300">
              Project Name *
            </Label>
            <Input
              id="projectName"
              name="projectName"
              type="text"
              placeholder="My GitHub Project"
              value={formData.projectName}
              onChange={handleChange}
              className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              required
            />
          </div>

          {/* GitHub URL */}
          <div className="space-y-2">
            <Label htmlFor="url" className="text-gray-300">
              Repository URL *
            </Label>
            <div className="relative">
              <Github className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                id="url"
                name="url"
                type="text"
                placeholder="https://github.com/username/repo"
                value={formData.url}
                onChange={handleChange}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                required
              />
            </div>
            <p className="text-xs text-gray-400">
              Enter the full GitHub repository URL
            </p>
          </div>

          {/* Branch */}
          <div className="space-y-2">
            <Label htmlFor="branch" className="text-gray-300">
              Branch
            </Label>
            <div className="relative">
              <GitBranch className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                id="branch"
                name="branch"
                type="text"
                placeholder="main"
                value={formData.branch}
                onChange={handleChange}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              />
            </div>
            <p className="text-xs text-gray-400">
              Default: main (leave empty to use default branch)
            </p>
          </div>

          {/* Private Repository Toggle */}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="flex items-center justify-between mb-2">
              <Label htmlFor="isPrivate" className="text-gray-300 cursor-pointer">
                Private Repository
              </Label>
              <input
                id="isPrivate"
                type="checkbox"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
            </div>
            <p className="text-xs text-gray-400">
              Enable if your repository is private and requires authentication
            </p>
          </div>

          {/* Personal Access Token (conditional) */}
          {isPrivate && (
            <div className="space-y-2 animate-in fade-in duration-200">
              <Label htmlFor="pat" className="text-gray-300">
                Personal Access Token (PAT) *
              </Label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="pat"
                  name="pat"
                  type="password"
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  value={formData.pat}
                  onChange={handleChange}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  required={isPrivate}
                />
              </div>
              <p className="text-xs text-gray-400">
                Generate a PAT from GitHub Settings → Developer Settings → Personal Access Tokens
              </p>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4">
            <p className="text-sm text-blue-300">
              <strong>Note:</strong> Make sure your repository contains source code files. 
              The AI will analyze all files in the repository to generate documentation.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-white/20 text-gray-300 hover:bg-white/10"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!formData.projectName || !formData.url || (isPrivate && !formData.pat)}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              Connect & Generate Docs
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

