'use client';

import { useState, useRef, useCallback } from 'react';
import { X, Upload, File, Folder } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { formatFileSize } from '@/lib/utils';
import Swal from 'sweetalert2';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (projectName: string, files: File[]) => void;
}

/**
 * Upload Modal Component
 * Allows users to drag-drop or select files for upload
 */
export default function UploadModal({ isOpen, onClose, onSubmit }: UploadModalProps) {
  const [projectName, setProjectName] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const folderInputRef = useRef<HTMLInputElement>(null);

  /**
   * Handle drag enter event
   */
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  /**
   * Handle drag leave event
   */
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  /**
   * Handle drag over event
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  /**
   * Handle file drop event
   * Supports dropping entire folders
   */
  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const items = e.dataTransfer.items;
    if (items && items.length > 0) {
      const files: File[] = [];
      
      // Process all dropped items (files and folders)
      for (let i = 0; i < items.length; i++) {
        const item = items[i].webkitGetAsEntry();
        if (item) {
          await processEntry(item, '', files);
        }
      }
      
      if (files.length > 0) {
        // Get folder name from first file
        // @ts-ignore - webkitRelativePath exists but not in TypeScript types
        const firstFilePath = files[0].webkitRelativePath || files[0].name;
        const folderName = firstFilePath.split('/')[0] || 'this folder';
        
        // Show confirmation dialog
        const result = await Swal.fire({
          title: 'Confirm Upload',
          html: `
            <p class="text-gray-300 mb-4">You're about to upload:</p>
            <p class="text-white font-semibold text-lg mb-4">"${folderName}"</p>
            <p class="text-gray-400 text-sm">${files.length} files detected</p>
          `,
          icon: 'question',
          showCancelButton: true,
          confirmButtonText: 'Yes, Upload',
          cancelButtonText: 'Cancel',
          confirmButtonColor: '#3b82f6',
          cancelButtonColor: '#6b7280',
          background: '#1e293b',
          color: '#fff',
        });
        
        if (result.isConfirmed) {
          setSelectedFiles(files);
        }
      }
    }
  }, []);

  /**
   * Recursively process directory entries
   */
  const processEntry = async (entry: any, path: string, files: File[]): Promise<void> => {
    if (entry.isFile) {
      return new Promise((resolve) => {
        entry.file((file: File) => {
          // Create a new File object with the relative path
          const relativePath = path ? `${path}/${file.name}` : file.name;
          const fileWithPath = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
          });
          // Store relative path as a property
          Object.defineProperty(fileWithPath, 'webkitRelativePath', {
            value: relativePath,
            writable: false,
          });
          files.push(fileWithPath);
          resolve();
        });
      });
    } else if (entry.isDirectory) {
      const dirReader = entry.createReader();
      const entries: any[] = await new Promise((resolve) => {
        dirReader.readEntries((entries: any[]) => resolve(entries));
      });
      
      for (const childEntry of entries) {
        const childPath = path ? `${path}/${entry.name}` : entry.name;
        await processEntry(childEntry, childPath, files);
      }
    }
  };

  /**
   * Handle folder input change
   * Preserves folder structure using webkitRelativePath
   */
  const handleFolderChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      
      // Get folder name from first file's path
      // @ts-ignore - webkitRelativePath exists but not in TypeScript types
      const firstFilePath = filesArray[0].webkitRelativePath || filesArray[0].name;
      const folderName = firstFilePath.split('/')[0] || 'this folder';
      
      // Show our own confirmation dialog
      const result = await Swal.fire({
        title: 'Confirm Upload',
        html: `
          <p class="text-gray-300 mb-4">You're about to upload:</p>
          <p class="text-white font-semibold text-lg mb-4">"${folderName}"</p>
          <p class="text-gray-400 text-sm">${filesArray.length} files selected</p>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, Upload',
        cancelButtonText: 'Cancel',
        confirmButtonColor: '#3b82f6',
        cancelButtonColor: '#6b7280',
        background: '#1e293b',
        color: '#fff',
      });
      
      if (result.isConfirmed) {
        setSelectedFiles(filesArray);
      } else {
        // Reset the input if user cancels
        e.target.value = '';
      }
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (projectName && selectedFiles.length > 0) {
      onSubmit(projectName, selectedFiles);
      // Reset form
      setProjectName('');
      setSelectedFiles([]);
    }
  };

  /**
   * Calculate total size of selected files
   */
  const getTotalSize = () => {
    if (!selectedFiles || selectedFiles.length === 0) return 0;
    return selectedFiles.reduce((total, file) => total + file.size, 0);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-white/10">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white">Upload Code Folder</h2>
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
              type="text"
              placeholder="My Awesome Project"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
              required
            />
          </div>

          {/* Folder Upload Area */}
          <div className="space-y-2">
            <Label className="text-gray-300">Select Project Folder *</Label>
            <div
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                isDragging
                  ? 'border-blue-400 bg-blue-400/10'
                  : 'border-white/20 hover:border-blue-400/50 bg-white/5'
              }`}
              onClick={() => folderInputRef.current?.click()}
            >
              <Folder className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-white mb-2 font-semibold text-lg">
                🎯 Drag and drop your project folder here
              </p>
              <p className="text-sm text-gray-300 mb-3">
                This is the easiest way - no browser warnings!
              </p>
              <div className="text-xs text-gray-500 border-t border-white/10 pt-3 mt-3">
                <p>Or click to browse (may show browser security dialog)</p>
              </div>
              <input
                ref={folderInputRef}
                type="file"
                onChange={handleFolderChange}
                className="hidden"
                // @ts-ignore - webkitdirectory is not in TypeScript types but is supported
                webkitdirectory=""
                directory=""
                multiple
              />
            </div>
          </div>

          {/* Selected Files Display */}
          {selectedFiles.length > 0 && (
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-semibold">
                  Selected Files ({selectedFiles.length})
                </h3>
                <span className="text-sm text-gray-400">
                  Total: {formatFileSize(getTotalSize())}
                </span>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {selectedFiles.slice(0, 10).map((file, index) => {
                  // @ts-ignore - webkitRelativePath exists but not in TypeScript types
                  const displayPath = file.webkitRelativePath || file.name;
                  return (
                    <div
                      key={index}
                      className="flex items-center space-x-2 text-sm text-gray-300"
                    >
                      <File className="h-4 w-4 text-blue-400 flex-shrink-0" />
                      <span className="truncate flex-1" title={displayPath}>
                        {displayPath}
                      </span>
                      <span className="text-gray-400 flex-shrink-0">
                        {formatFileSize(file.size)}
                      </span>
                    </div>
                  );
                })}
                {selectedFiles.length > 10 && (
                  <p className="text-sm text-gray-400 text-center pt-2">
                    + {selectedFiles.length - 10} more files...
                  </p>
                )}
              </div>
            </div>
          )}

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
              disabled={!projectName || selectedFiles.length === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              Upload & Generate Docs
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

