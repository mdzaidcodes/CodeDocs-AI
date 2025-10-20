'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Edit2, Save, X, Globe, FileText, List, Download, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import Swal from 'sweetalert2';
import apiClient from '@/lib/api';

interface DocumentationTabProps {
  projectId: string;
  documentation: string;
}

type ViewMode = 'web' | 'markdown';

/**
 * Documentation Tab Component
 * Displays and allows editing of project documentation with two view modes
 */
export default function DocumentationTab({ projectId, documentation }: DocumentationTabProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(documentation);
  const [currentContent, setCurrentContent] = useState(documentation);
  const [isSaving, setIsSaving] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('web');
  const [tableOfContents, setTableOfContents] = useState<Array<{id: string; text: string; level: number}>>([]);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  /**
   * Close download menu when clicking outside
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showDownloadMenu && !target.closest('.relative')) {
        setShowDownloadMenu(false);
      }
    };

    if (showDownloadMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showDownloadMenu]);

  /**
   * Extract table of contents from markdown - ONLY allowed headings
   */
  useEffect(() => {
    // Define allowed headings (exact match, case-insensitive)
    const allowedH2 = [
      'purpose and objectives',
      'setup and installation',
      'architecture documentation',
      'code documentation',
      'user guides',
      'development documentation',
      'maintenance information',
      'additional notes',
      'reference materials'
    ];
    
    const allowedH3 = [
      // Setup and Installation subsections
      'prerequisites and dependencies',
      'installation instructions',
      'configuration steps',
      'environment setup',
      // Architecture Documentation subsections
      'system architecture and tech stack',
      'component relationships',
      'simple data flow',
      'database schemas or data models',
      // Code Documentation subsections
      'api reference and endpoints',
      'function/method documentation',
      'code comments and inline documentation',
      'usage examples and code samples',
      // User Guides subsections
      'feature documentation',
      'faqs',
      // Development Documentation subsections
      'coding standards and conventions',
      'development workflow',
      'testing procedures',
      'deployment processes',
      // Maintenance Information subsections
      'version history and changelog',
      'known issues and limitations',
      'performance considerations',
      'security considerations',
      // Reference Materials subsections
      'glossary of terms',
      'external dependencies',
      'contact information for support'
    ];
    
    const lines = currentContent.split('\n');
    const toc: Array<{id: string; text: string; level: number}> = [];
    let lineNumber = 0;
    
    lines.forEach((line) => {
      lineNumber++;
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const text = match[2].trim();
        const textLower = text.toLowerCase();
        
        // Only include if it's an allowed heading
        const isAllowedH2 = level === 2 && allowedH2.includes(textLower);
        const isAllowedH3 = level === 3 && allowedH3.includes(textLower);
        
        if (isAllowedH2 || isAllowedH3) {
          // Generate ID that matches ReactMarkdown's heading IDs
          const id = `heading-${lineNumber}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
          toc.push({ id, text, level });
        }
      }
    });
    
    setTableOfContents(toc);
  }, [currentContent]);

  /**
   * Handle save documentation
   */
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await apiClient.put(`/projects/${projectId}/documentation`, {
        content: editedContent,
      });

      setCurrentContent(editedContent);
      setIsEditing(false);

      Swal.fire({
        icon: 'success',
        title: 'Saved',
        text: 'Documentation updated successfully',
        timer: 1500,
        showConfirmButton: false,
      });
    } catch (error) {
      console.error('Save error:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Failed to save documentation',
        confirmButtonColor: '#3b82f6',
      });
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle cancel editing
   */
  const handleCancel = () => {
    setEditedContent(currentContent);
    setIsEditing(false);
  };

  /**
   * Handle documentation export/download
   * 
   * Downloads documentation in the specified format (md, docx, or pdf).
   * Process:
   * 1. Show loading toast
   * 2. Make API request to export endpoint with format parameter
   * 3. Create blob from response and trigger download
   * 4. Show success/error toast
   * 
   * @param format - Export format ('md', 'docx', or 'pdf')
   */
  const handleDownload = async (format: 'md' | 'docx' | 'pdf') => {
    // Close dropdown
    setShowDownloadMenu(false);

    // Show loading toast
    const loadingToast = Swal.fire({
      title: 'Preparing Download',
      text: `Generating ${format.toUpperCase()} file...`,
      icon: 'info',
      toast: true,
      position: 'bottom-end',
      showConfirmButton: false,
      timer: 10000,
      timerProgressBar: true,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      // Make API request to export endpoint
      const response = await apiClient.get(
        `/projects/${projectId}/documentation/export?format=${format}`,
        {
          responseType: 'blob', // Important for file download
        }
      );

      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extract filename from Content-Disposition header or create default
      const contentDisposition = response.headers['content-disposition'];
      let filename = `documentation.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Close loading toast and show success
      loadingToast.close();
      
      Swal.fire({
        title: 'Download Complete!',
        text: `Your ${format.toUpperCase()} file has been downloaded successfully.`,
        icon: 'success',
        toast: true,
        position: 'bottom-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
      });

    } catch (error: any) {
      console.error('Download error:', error);
      
      // Close loading toast and show error
      loadingToast.close();
      
      Swal.fire({
        title: 'Download Failed',
        text: error.response?.data?.error || 'Failed to download documentation. Please try again.',
        icon: 'error',
        toast: true,
        position: 'bottom-end',
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
      });
    }
  };

  /**
   * Scroll to heading
   */
  const scrollToHeading = (id: string) => {
    console.log('Scrolling to:', id);
    const element = document.getElementById(id);
    
    if (element) {
      console.log('Element found:', element);
      
      // Scroll the entire page to the element
      element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start',
        inline: 'nearest'
      });
      
      // Add offset by scrolling up a bit
      setTimeout(() => {
        window.scrollBy({ top: -80, behavior: 'smooth' });
      }, 100);
      
      // Highlight the heading briefly
      element.classList.add('highlight-heading');
      setTimeout(() => {
        element.classList.remove('highlight-heading');
      }, 2000);
    } else {
      console.error('Element not found:', id);
    }
  };

  return (
    <div className="space-y-4">
      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        {/* View Mode Toggle */}
        {!isEditing && (
          <div className="flex space-x-2 bg-white/5 rounded-lg p-1 border border-white/10">
            <button
              onClick={() => setViewMode('web')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                viewMode === 'web'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Globe className="h-4 w-4" />
              <span>Web View</span>
            </button>
            <button
              onClick={() => setViewMode('markdown')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                viewMode === 'markdown'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Documentation View</span>
            </button>
          </div>
        )}

        {/* Download and Edit/Save Buttons */}
        <div className="flex space-x-2">
          {/* Download Dropdown - Always visible when not editing */}
          {!isEditing && (
            <div className="relative">
              <Button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
                <ChevronDown className="h-4 w-4 ml-2" />
              </Button>
              
              {/* Dropdown Menu */}
              {showDownloadMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-white/20 rounded-lg shadow-lg z-10">
                  <button
                    onClick={() => handleDownload('md')}
                    className="w-full text-left px-4 py-3 hover:bg-white/10 text-white transition-colors flex items-center justify-between rounded-t-lg"
                  >
                    <span>Markdown</span>
                    <span className="text-xs text-gray-400">.md</span>
                  </button>
                  <button
                    onClick={() => handleDownload('docx')}
                    className="w-full text-left px-4 py-3 hover:bg-white/10 text-white transition-colors flex items-center justify-between"
                  >
                    <span>Microsoft Word</span>
                    <span className="text-xs text-gray-400">.docx</span>
                  </button>
                  <button
                    onClick={() => handleDownload('pdf')}
                    className="w-full text-left px-4 py-3 hover:bg-white/10 text-white transition-colors flex items-center justify-between rounded-b-lg"
                  >
                    <span>PDF</span>
                    <span className="text-xs text-gray-400">.pdf</span>
                  </button>
                </div>
              )}
            </div>
          )}
          
          {/* Edit Documentation Button - Only in Documentation View */}
          {!isEditing ? (
            viewMode === 'markdown' && (
              <Button
                onClick={() => setIsEditing(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Edit2 className="h-4 w-4 mr-2" />
                Edit Documentation
              </Button>
            )
          ) : (
            <>
              <Button
                onClick={handleCancel}
                variant="outline"
                className="border-white/20 text-white hover:bg-white/10"
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Content Display */}
      {isEditing ? (
        <div className="bg-white/5 rounded-lg p-6 border border-white/10">
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="min-h-[600px] font-mono text-sm bg-white/10 border-white/20 text-white"
            placeholder="Enter documentation in Markdown format..."
          />
          <p className="text-sm text-gray-400 mt-2">
            Supports Markdown formatting
          </p>
        </div>
      ) : viewMode === 'web' ? (
        /* Web View with Table of Contents */
        <div className="grid grid-cols-12 gap-6">
          {/* Table of Contents */}
          <div className="col-span-4 sticky top-6 self-start">
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-white/10">
                <List className="h-5 w-5 text-blue-400 flex-shrink-0" />
                <h3 className="text-white font-semibold">Table of Contents</h3>
              </div>
              <nav className="space-y-1 pr-2">
                {tableOfContents.length === 0 ? (
                  <p className="text-gray-500 text-sm italic">No headings found</p>
                ) : (
                  tableOfContents.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => scrollToHeading(item.id)}
                      className={`block w-full text-left py-2 px-1 rounded transition-all hover:bg-white/10 whitespace-nowrap overflow-x-auto ${
                        item.level === 2
                          ? 'text-white font-semibold text-base border-l-2 border-blue-400 pl-2'
                          : item.level === 3
                          ? 'text-gray-300 font-medium text-sm pl-6'
                          : 'text-gray-400 text-sm pl-4'
                      }`}
                      title={item.text}
                    >
                      {item.level === 3 && <span className="mr-2">•</span>}
                      {item.text}
                    </button>
                  ))
                )}
              </nav>
            </div>
          </div>

          {/* Documentation Content - Web Styled */}
          <div className="col-span-8 min-h-screen">
            <div className="bg-gradient-to-br from-white/5 to-white/10 rounded-lg p-8 border border-white/10">
              <ReactMarkdown
                components={{
                  h1: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h1 
                        id={id} 
                        className="text-4xl font-bold text-white mb-6 pb-4 border-b border-white/20 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h1>
                    );
                  },
                  h2: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h2 
                        id={id} 
                        className="text-3xl font-bold text-white mt-8 mb-4 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h2>
                    );
                  },
                  h3: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h3 
                        id={id} 
                        className="text-2xl font-semibold text-white mt-6 mb-3 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h3>
                    );
                  },
                  h4: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h4 
                        id={id} 
                        className="text-xl font-semibold text-gray-200 mt-5 mb-2 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h4>
                    );
                  },
                  h5: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h5 
                        id={id} 
                        className="text-lg font-semibold text-gray-300 mt-4 mb-2 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h5>
                    );
                  },
                  h6: ({ node, children, ...props }) => {
                    const text = String(children);
                    const lineNum = node?.position?.start?.line || 0;
                    const id = `heading-${lineNum}-${text.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
                    return (
                      <h6 
                        id={id} 
                        className="text-base font-semibold text-gray-400 mt-3 mb-2 scroll-mt-6" 
                        {...props}
                      >
                        {children}
                      </h6>
                    );
                  },
                  p: ({ node, children, ...props }) => (
                    <p className="text-gray-300 mb-4 leading-relaxed" {...props}>
                      {children}
                    </p>
                  ),
                  ul: ({ node, children, ...props }) => (
                    <ul className="list-disc list-inside text-gray-300 mb-4 space-y-2" {...props}>
                      {children}
                    </ul>
                  ),
                  ol: ({ node, children, ...props }) => (
                    <ol className="list-decimal list-inside text-gray-300 mb-4 space-y-2" {...props}>
                      {children}
                    </ol>
                  ),
                  li: ({ node, children, ...props }) => (
                    <li className="text-gray-300" {...props}>
                      {children}
                    </li>
                  ),
                  blockquote: ({ node, children, ...props }) => (
                    <blockquote className="border-l-4 border-blue-400 pl-4 py-2 mb-4 text-gray-300 italic bg-blue-400/5" {...props}>
                      {children}
                    </blockquote>
                  ),
                  code({ node, inline, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <div className="my-4">
                        <SyntaxHighlighter
                          style={vscDarkPlus}
                          language={match[1]}
                          PreTag="div"
                          className="rounded-lg"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code className="bg-white/10 px-2 py-1 rounded text-blue-300 text-sm font-mono" {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre: ({ node, children, ...props }) => (
                    <pre className="bg-slate-900 rounded-lg p-4 mb-4 overflow-x-auto" {...props}>
                      {children}
                    </pre>
                  ),
                  a: ({ node, children, ...props }) => (
                    <a className="text-blue-400 hover:text-blue-300 underline" {...props}>
                      {children}
                    </a>
                  ),
                  strong: ({ node, children, ...props }) => (
                    <strong className="font-bold text-white" {...props}>
                      {children}
                    </strong>
                  ),
                  em: ({ node, children, ...props }) => (
                    <em className="italic text-gray-200" {...props}>
                      {children}
                    </em>
                  ),
                }}
              >
                {currentContent || 'No documentation available'}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      ) : (
        /* Documentation View - Original Markdown Style */
        <div className="markdown-viewer">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {currentContent || 'No documentation available'}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

