import Link from 'next/link';
import { FileCode, Calendar, Shield, Github, Upload, Trash2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import type { Project } from '@/types';

interface ProjectCardProps {
  project: Project;
  onDelete?: (projectId: string) => void;
}

/**
 * Project Card Component
 * Displays project information with stats and actions
 */
export default function ProjectCard({ project, onDelete }: ProjectCardProps) {
  /**
   * Get status badge color
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-400/30';
      case 'processing':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-400/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-400/30';
    }
  };

  /**
   * Get security score color
   */
  const getSecurityScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <Card className="bg-white/5 border-white/10 hover:border-blue-400/50 transition-all group">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <Link href={`/projects/${project.id}`}>
              <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors mb-2">
                {project.name}
              </h3>
            </Link>
            {project.description && (
              <p className="text-gray-400 text-sm mb-3">{project.description}</p>
            )}
            <div className="flex items-center space-x-2">
              <Badge className={`${getStatusColor(project.status)} border`}>
                {project.status}
              </Badge>
              <div className="flex items-center space-x-1 text-gray-400 text-sm">
                {project.source_type === 'github' ? (
                  <Github className="h-4 w-4" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                <span className="capitalize">{project.source_type}</span>
              </div>
            </div>
          </div>

          {/* Delete Button */}
          {onDelete && (
            <button
              onClick={(e) => {
                e.preventDefault();
                onDelete(project.id);
              }}
              className="text-gray-400 hover:text-red-400 transition-colors p-2"
              title="Delete project"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {/* Language */}
          {project.language && (
            <div className="space-y-1">
              <p className="text-xs text-gray-400">Language</p>
              <p className="text-sm font-semibold text-white">{project.language}</p>
            </div>
          )}

          {/* Files */}
          {project.file_count !== undefined && (
            <div className="space-y-1">
              <p className="text-xs text-gray-400">Files</p>
              <p className="text-sm font-semibold text-white">{project.file_count}</p>
            </div>
          )}

          {/* Security Score */}
          {project.security_score !== undefined && (
            <div className="space-y-1">
              <p className="text-xs text-gray-400">Security</p>
              <p className={`text-sm font-semibold ${getSecurityScoreColor(project.security_score)}`}>
                {project.security_score}/100
              </p>
            </div>
          )}

          {/* Created Date */}
          <div className="space-y-1">
            <p className="text-xs text-gray-400">Created</p>
            <p className="text-sm font-semibold text-white">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* GitHub URL (if applicable) */}
        {project.github_url && (
          <div className="mt-4 pt-4 border-t border-white/10">
            <a
              href={project.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 text-sm flex items-center space-x-1"
            >
              <Github className="h-4 w-4" />
              <span className="truncate">{project.github_url}</span>
            </a>
          </div>
        )}

        {/* View Button */}
        <Link href={`/projects/${project.id}`}>
          <div className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-2 rounded-md transition-colors">
            View Project
          </div>
        </Link>
      </CardContent>
    </Card>
  );
}

