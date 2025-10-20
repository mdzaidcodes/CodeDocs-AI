'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Code2, Plus, Search, LogOut, User } from 'lucide-react';
import Swal from 'sweetalert2';
import { isAuthenticated, getCurrentUser, logout } from '@/lib/api';
import apiClient from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import ProjectCard from '@/components/ProjectCard';
import type { Project } from '@/types';

/**
 * Dashboard Page Component
 * Displays all user projects with search and filtering
 */
export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  /**
   * Check authentication and load user data
   */
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const currentUser = getCurrentUser();
    setUser(currentUser);
    fetchProjects();
  }, [router]);

  /**
   * Fetch all projects for the user
   */
  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/projects');
      setProjects(response.data.data.projects || []);
      setFilteredProjects(response.data.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Failed to load projects',
        confirmButtonColor: '#3b82f6',
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle search input change
   */
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredProjects(projects);
    } else {
      const filtered = projects.filter((project) =>
        project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.language?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredProjects(filtered);
    }
  }, [searchQuery, projects]);

  /**
   * Handle project deletion
   */
  const handleDeleteProject = async (projectId: string) => {
    const result = await Swal.fire({
      title: 'Delete Project?',
      text: 'This action cannot be undone',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Yes, delete it',
    });

    if (result.isConfirmed) {
      try {
        await apiClient.delete(`/projects/${projectId}`);
        
        // Remove project from state
        setProjects(projects.filter((p) => p.id !== projectId));
        
        Swal.fire({
          icon: 'success',
          title: 'Deleted',
          text: 'Project deleted successfully',
          timer: 1500,
          showConfirmButton: false,
        });
      } catch (error) {
        console.error('Delete error:', error);
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Failed to delete project',
          confirmButtonColor: '#3b82f6',
        });
      }
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    Swal.fire({
      title: 'Logout?',
      text: 'Are you sure you want to logout?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3b82f6',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Yes, logout',
    }).then((result) => {
      if (result.isConfirmed) {
        logout();
      }
    });
  };

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
              <div className="flex items-center space-x-2 text-gray-300">
                <User className="h-5 w-5" />
                <span>{user?.name || 'User'}</span>
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                className="border-white/20 text-gray-300 hover:bg-white/10"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div className="mb-4 md:mb-0">
            <h1 className="text-3xl font-bold text-white mb-2">My Projects</h1>
            <p className="text-gray-400">
              {projects.length} {projects.length === 1 ? 'project' : 'projects'} total
            </p>
          </div>
          <Link href="/get-started">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="h-5 w-5 mr-2" />
              New Project
            </Button>
          </Link>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
            />
          </div>
        </div>

        {/* Projects Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-pulse-slow text-gray-400">
              <Code2 className="h-16 w-16 mx-auto mb-4" />
              <p>Loading projects...</p>
            </div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-20">
            <div className="bg-white/5 rounded-lg p-12 border border-white/10 max-w-md mx-auto">
              <Code2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {searchQuery ? 'No projects found' : 'No projects yet'}
              </h3>
              <p className="text-gray-400 mb-6">
                {searchQuery
                  ? 'Try a different search term'
                  : 'Create your first project to get started'}
              </p>
              {!searchQuery && (
                <Link href="/get-started">
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <Plus className="h-5 w-5 mr-2" />
                    Create Project
                  </Button>
                </Link>
              )}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onDelete={handleDeleteProject}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

