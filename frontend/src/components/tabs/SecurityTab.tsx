'use client';

import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Filter, Search, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { getSeverityColor } from '@/lib/utils';
import type { SecurityFinding } from '@/types';

interface SecurityTabProps {
  projectId: string;
  findings: SecurityFinding[];
  isLoading?: boolean;
}

/**
 * Security Tab Component
 * Displays security vulnerabilities with filtering
 */
export default function SecurityTab({ projectId, findings, isLoading = false }: SecurityTabProps) {
  const [filteredFindings, setFilteredFindings] = useState<SecurityFinding[]>(findings);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');

  /**
   * Filter findings based on search and severity
   */
  useEffect(() => {
    let filtered = findings;

    // Filter by severity
    if (selectedSeverity !== 'all') {
      filtered = filtered.filter((f) => f.severity === selectedSeverity);
    }

    // Filter by search query
    if (searchQuery.trim() !== '') {
      filtered = filtered.filter(
        (f) =>
          f.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          f.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          f.file_path.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredFindings(filtered);
  }, [searchQuery, selectedSeverity, findings]);

  /**
   * Get severity statistics
   */
  const getSeverityStats = () => {
    return {
      critical: findings.filter((f) => f.severity === 'critical').length,
      high: findings.filter((f) => f.severity === 'high').length,
      medium: findings.filter((f) => f.severity === 'medium').length,
      low: findings.filter((f) => f.severity === 'low').length,
      info: findings.filter((f) => f.severity === 'info').length,
    };
  };

  const stats = getSeverityStats();

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-6">
        <Loader2 className="h-16 w-16 text-blue-400 animate-spin" />
        <div className="text-center space-y-2">
          <p className="text-2xl font-bold text-white">Coming Soon...</p>
          <p className="text-gray-400">Security analysis is being processed in the background</p>
          <p className="text-sm text-gray-500">This usually takes 1-2 minutes</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-red-500/10 border border-red-400/30 rounded-lg p-4">
          <p className="text-red-400 text-sm mb-1">Critical</p>
          <p className="text-2xl font-bold text-white">{stats.critical}</p>
        </div>
        <div className="bg-orange-500/10 border border-orange-400/30 rounded-lg p-4">
          <p className="text-orange-400 text-sm mb-1">High</p>
          <p className="text-2xl font-bold text-white">{stats.high}</p>
        </div>
        <div className="bg-yellow-500/10 border border-yellow-400/30 rounded-lg p-4">
          <p className="text-yellow-400 text-sm mb-1">Medium</p>
          <p className="text-2xl font-bold text-white">{stats.medium}</p>
        </div>
        <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4">
          <p className="text-blue-400 text-sm mb-1">Low</p>
          <p className="text-2xl font-bold text-white">{stats.low}</p>
        </div>
        <div className="bg-gray-500/10 border border-gray-400/30 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Info</p>
          <p className="text-2xl font-bold text-white">{stats.info}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Search findings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
          />
        </div>
        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="px-4 py-2 rounded-md bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" style={{ backgroundColor: '#1e293b', color: '#fff' }}>All Severities</option>
          <option value="critical" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Critical</option>
          <option value="high" style={{ backgroundColor: '#1e293b', color: '#fff' }}>High</option>
          <option value="medium" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Medium</option>
          <option value="low" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Low</option>
          <option value="info" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Info</option>
        </select>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="text-center py-12 bg-white/5 rounded-lg border border-white/10">
          <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            {findings.length === 0 ? 'No Security Issues Found' : 'No Results'}
          </h3>
          <p className="text-gray-400">
            {findings.length === 0
              ? 'Great job! Your code has no security vulnerabilities.'
              : 'Try adjusting your filters'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFindings.map((finding) => (
            <div
              key={finding.id}
              className="bg-white/5 rounded-lg p-6 border border-white/10 hover:border-blue-400/50 transition-colors"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Badge className={`${getSeverityColor(finding.severity)} border`}>
                      {finding.severity.toUpperCase()}
                    </Badge>
                    <span className="text-sm text-gray-400">{finding.category}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {finding.title}
                  </h3>
                </div>
                <AlertTriangle className={`h-6 w-6 flex-shrink-0 ${
                  finding.severity === 'critical' ? 'text-red-400' :
                  finding.severity === 'high' ? 'text-orange-400' :
                  finding.severity === 'medium' ? 'text-yellow-400' :
                  'text-blue-400'
                }`} />
              </div>

              {/* Description */}
              <p className="text-gray-300 mb-3">{finding.description}</p>

              {/* File Location */}
              <div className="bg-white/5 rounded px-3 py-2 mb-3">
                <p className="text-sm text-gray-400">Location:</p>
                <p className="text-sm text-white font-mono">
                  {finding.file_path}
                  {finding.line_number && `:${finding.line_number}`}
                </p>
              </div>

              {/* Recommendation */}
              <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4">
                <p className="text-sm font-semibold text-blue-400 mb-2">
                  Recommendation:
                </p>
                <p className="text-sm text-gray-300">{finding.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

