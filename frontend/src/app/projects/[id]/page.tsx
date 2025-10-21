'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Code2, FileText, Shield, Sparkles, MessageSquare, Loader2, Palette } from 'lucide-react';
import Swal from 'sweetalert2';
import { isAuthenticated } from '@/lib/api';
import apiClient from '@/lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import DocumentationTab from '@/components/tabs/DocumentationTab';
import SecurityTab from '@/components/tabs/SecurityTab';
import ImprovementsTab from '@/components/tabs/ImprovementsTab';
import ChatTab from '@/components/tabs/ChatTab';
import ColorPaletteTab from '@/components/tabs/ColorPaletteTab';
import type { Project, SecurityFinding, CodeImprovement } from '@/types';

/**
 * Project Detail Page Component
 * Main view for a specific project with tabs for different features
 */
export default function ProjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [activeTab, setActiveTab] = useState('documentation');
  const [project, setProject] = useState<Project | null>(null);
  const [documentation, setDocumentation] = useState('');
  const [securityFindings, setSecurityFindings] = useState<SecurityFinding[]>([]);
  const [improvements, setImprovements] = useState<CodeImprovement[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [securityLoading, setSecurityLoading] = useState(true); // Start with true
  const [improvementsLoading, setImprovementsLoading] = useState(true); // Start with true
  const [securityNotificationShown, setSecurityNotificationShown] = useState(false);
  const [improvementsNotificationShown, setImprovementsNotificationShown] = useState(false);

  /**
   * Check authentication and load project data
   */
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    fetchProjectData();
  }, [router, projectId]);

  /**
   * Poll for background task completion
   */
  useEffect(() => {
    if (!project || project.status !== 'completed') return;

    // Check if security/improvements are still being processed
    const hasSecurityData = securityFindings.length > 0;
    const hasImprovementsData = improvements.length > 0;
    
    if (hasSecurityData && hasImprovementsData) {
      // Everything loaded
      return;
    }

    // Poll for updates
    const pollInterval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/projects/${projectId}/status`);
        const { progress_stage } = response.data.data;

        // Check if security analysis just completed
        if (!hasSecurityData && !securityNotificationShown) {
          try {
            const securityResponse = await apiClient.get(`/projects/${projectId}/security`);
            const findings = securityResponse.data.data.findings || [];
            if (findings.length > 0 || securityResponse.status === 200) {
              setSecurityFindings(findings);
              setSecurityLoading(false);
              setSecurityNotificationShown(true);
              
              // Show toast notification
              Swal.fire({
                icon: 'success',
                title: 'Security Analysis Complete!',
                html: `Security vulnerabilities for <strong>${project.name}</strong> are done.<br><a href="#" id="viewSecurityLink" style="color: #3b82f6; text-decoration: underline;">Click here to view them</a>`,
                toast: true,
                position: 'bottom-end',
                showConfirmButton: false,
                timer: 8000,
                timerProgressBar: true,
                didOpen: () => {
                  document.getElementById('viewSecurityLink')?.addEventListener('click', (e) => {
                    e.preventDefault();
                    Swal.close();
                    setActiveTab('security');
                  });
                },
              });

              // Refresh project data to get updated security score
              const projectResponse = await apiClient.get(`/projects/${projectId}`);
              setProject(projectResponse.data.data);
            }
          } catch (error) {
            // Security data not ready yet
          }
        }

        // Check if improvements analysis just completed
        if (!hasImprovementsData && !improvementsNotificationShown) {
          try {
            const improvementsResponse = await apiClient.get(`/projects/${projectId}/improvements`);
            const imps = improvementsResponse.data.data.improvements || [];
            if (imps.length > 0 || improvementsResponse.status === 200) {
              setImprovements(imps);
              setImprovementsLoading(false);
              setImprovementsNotificationShown(true);
              
              // Show toast notification
              Swal.fire({
                icon: 'success',
                title: 'Code Quality Analysis Complete!',
                html: `Improvement tips for <strong>${project.name}</strong> are done.<br><a href="#" id="viewImprovementsLink" style="color: #3b82f6; text-decoration: underline;">Click here to view them</a>`,
                toast: true,
                position: 'bottom-end',
                showConfirmButton: false,
                timer: 8000,
                timerProgressBar: true,
                didOpen: () => {
                  document.getElementById('viewImprovementsLink')?.addEventListener('click', (e) => {
                    e.preventDefault();
                    Swal.close();
                    setActiveTab('improvements');
                  });
                },
              });
            }
          } catch (error) {
            // Improvements data not ready yet
          }
        }

        // Stop polling if both are loaded
        if (securityFindings.length > 0 && improvements.length > 0) {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 5000); // Poll every 5 seconds

    // Cleanup
    return () => clearInterval(pollInterval);
  }, [project, projectId, securityFindings, improvements, securityNotificationShown, improvementsNotificationShown]);

  /**
   * Fetch all project data
   */
  const fetchProjectData = async () => {
    setIsLoading(true);
    try {
      // Fetch project details
      const projectResponse = await apiClient.get(`/projects/${projectId}`);
      setProject(projectResponse.data.data);

      // Check if project is still processing
      if (projectResponse.data.data.status === 'processing') {
        Swal.fire({
          icon: 'info',
          title: 'Project Processing',
          text: 'This project is still being processed. Some features may not be available yet.',
          confirmButtonColor: '#3b82f6',
        });
      }

      // Fetch documentation
      try {
        const docsResponse = await apiClient.get(`/projects/${projectId}/documentation`);
        setDocumentation(docsResponse.data.data.content || '');
      } catch (error) {
        console.error('Error fetching documentation:', error);
        setDocumentation('# Documentation\n\nDocumentation is being generated...');
      }

      // Fetch security findings
      try {
        const securityResponse = await apiClient.get(`/projects/${projectId}/security`);
        const findings = securityResponse.data.data.findings || [];
        setSecurityFindings(findings);
        setSecurityLoading(false); // Data loaded
        
        // If no findings and project is completed, analysis might still be running
        if (findings.length === 0 && projectResponse.data.data.status === 'completed') {
          setSecurityLoading(true);
        }
      } catch (error: any) {
        console.error('Error fetching security findings:', error);
        // If 404 or empty response and project is completed, analysis is in progress
        if (projectResponse.data.data.status === 'completed') {
          setSecurityLoading(true);
        }
      }

      // Fetch improvements
      try {
        const improvementsResponse = await apiClient.get(`/projects/${projectId}/improvements`);
        const imps = improvementsResponse.data.data.improvements || [];
        setImprovements(imps);
        setImprovementsLoading(false); // Data loaded
        
        // If no improvements and project is completed, analysis might still be running
        if (imps.length === 0 && projectResponse.data.data.status === 'completed') {
          setImprovementsLoading(true);
        }
      } catch (error: any) {
        console.error('Error fetching improvements:', error);
        // If 404 or empty response and project is completed, analysis is in progress
        if (projectResponse.data.data.status === 'completed') {
          setImprovementsLoading(true);
        }
      }
    } catch (error: any) {
      console.error('Error fetching project data:', error);
      
      if (error.response?.status === 404) {
        Swal.fire({
          icon: 'error',
          title: 'Project Not Found',
          text: 'The project you are looking for does not exist.',
          confirmButtonColor: '#3b82f6',
        }).then(() => {
          router.push('/dashboard');
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Failed to load project data',
          confirmButtonColor: '#3b82f6',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Loading state
   */
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-16 w-16 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-300">Loading project...</p>
        </div>
      </div>
    );
  }

  /**
   * Error state
   */
  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Code2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-300 mb-4">Project not found</p>
          <Link href="/dashboard" className="text-blue-400 hover:text-blue-300">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link
              href="/dashboard"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
            >
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Project Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">{project.name}</h1>
          {project.description && (
            <p className="text-gray-400 mb-4">{project.description}</p>
          )}
          <div className="flex items-center space-x-6 text-sm text-gray-400">
            {project.language && (
              <div>
                <span className="font-semibold">Language:</span> {project.language}
              </div>
            )}
            {project.file_count !== undefined && (
              <div>
                <span className="font-semibold">Files:</span> {project.file_count}
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 bg-white/5 border border-white/10">
            <TabsTrigger value="documentation" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Documentation</span>
            </TabsTrigger>
            <TabsTrigger value="colors" className="flex items-center space-x-2">
              <Palette className="h-4 w-4" />
              <span>Colors</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center space-x-2">
              <Shield className="h-4 w-4" />
              <span>Security</span>
              {securityFindings.length > 0 && (
                <span className="ml-2 bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded-full">
                  {securityFindings.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="improvements" className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4" />
              <span>Improvements</span>
              {improvements.length > 0 && (
                <span className="ml-2 bg-blue-500/20 text-blue-400 text-xs px-2 py-0.5 rounded-full">
                  {improvements.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Chat</span>
            </TabsTrigger>
          </TabsList>

          {/* Tab Contents */}
          <div className="mt-6">
            <TabsContent value="documentation">
              <DocumentationTab projectId={projectId} documentation={documentation} />
            </TabsContent>

            <TabsContent value="colors">
              <ColorPaletteTab 
                projectId={projectId} 
                colorPalette={project?.color_palette || null}
              />
            </TabsContent>

            <TabsContent value="security">
              <SecurityTab 
                projectId={projectId} 
                findings={securityFindings} 
                isLoading={securityLoading}
              />
            </TabsContent>

            <TabsContent value="improvements">
              <ImprovementsTab 
                projectId={projectId} 
                improvements={improvements}
                isLoading={improvementsLoading}
              />
            </TabsContent>

            <TabsContent value="chat">
              <ChatTab projectId={projectId} />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}

