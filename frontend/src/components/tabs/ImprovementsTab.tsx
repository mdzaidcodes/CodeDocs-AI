'use client';

import { useState, useEffect } from 'react';
import { Sparkles, Search, TrendingUp, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { getPriorityColor } from '@/lib/utils';
import type { CodeImprovement } from '@/types';

interface ImprovementsTabProps {
  projectId: string;
  improvements: CodeImprovement[];
  isLoading?: boolean;
}

/**
 * Improvements Tab Component
 * Displays code quality suggestions with filtering
 */
export default function ImprovementsTab({ projectId, improvements, isLoading = false }: ImprovementsTabProps) {
  const [filteredImprovements, setFilteredImprovements] = useState<CodeImprovement[]>(improvements);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedPriority, setSelectedPriority] = useState<string>('all');

  /**
   * Filter improvements based on search, category, and impact level
   */
  useEffect(() => {
    let filtered = improvements;

    // Filter by category
    if (selectedType !== 'all') {
      filtered = filtered.filter((i) => i.category === selectedType);
    }

    // Filter by impact level
    if (selectedPriority !== 'all') {
      filtered = filtered.filter((i) => i.impact_level === selectedPriority);
    }

    // Filter by search query
    if (searchQuery.trim() !== '') {
      filtered = filtered.filter(
        (i) =>
          i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          i.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          i.file_path.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredImprovements(filtered);
  }, [searchQuery, selectedType, selectedPriority, improvements]);

  /**
   * Get category statistics
   */
  const getTypeStats = () => {
    return {
      performance: improvements.filter((i) => i.category === 'performance').length,
      readability: improvements.filter((i) => i.category === 'readability').length,
      bestPractice: improvements.filter((i) => i.category === 'best-practice').length,
      maintainability: improvements.filter((i) => i.category === 'maintainability').length,
      security: improvements.filter((i) => i.category === 'security').length,
      errorHandling: improvements.filter((i) => i.category === 'error-handling').length,
    };
  };

  const stats = getTypeStats();

  /**
   * Get type icon and color
   */
  const getTypeStyle = (type: string) => {
    const styles: { [key: string]: string } = {
      performance: 'bg-purple-500/20 text-purple-400 border-purple-400/30',
      readability: 'bg-blue-500/20 text-blue-400 border-blue-400/30',
      'best-practice': 'bg-green-500/20 text-green-400 border-green-400/30',
      maintainability: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30',
      security: 'bg-red-500/20 text-red-400 border-red-400/30',
      'error-handling': 'bg-orange-500/20 text-orange-400 border-orange-400/30',
    };
    return styles[type] || 'bg-gray-500/20 text-gray-400 border-gray-400/30';
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-4">
        <Loader2 className="h-12 w-12 text-blue-400 animate-spin" />
        <div className="text-center">
          <p className="text-xl font-semibold text-white mb-2">Analyzing Code Quality...</p>
          <p className="text-gray-400">Finding improvement opportunities</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-purple-500/10 border border-purple-400/30 rounded-lg p-4">
          <p className="text-purple-400 text-sm mb-1">Performance</p>
          <p className="text-2xl font-bold text-white">{stats.performance}</p>
        </div>
        <div className="bg-blue-500/10 border border-blue-400/30 rounded-lg p-4">
          <p className="text-blue-400 text-sm mb-1">Readability</p>
          <p className="text-2xl font-bold text-white">{stats.readability}</p>
        </div>
        <div className="bg-green-500/10 border border-green-400/30 rounded-lg p-4">
          <p className="text-green-400 text-sm mb-1">Best Practice</p>
          <p className="text-2xl font-bold text-white">{stats.bestPractice}</p>
        </div>
        <div className="bg-yellow-500/10 border border-yellow-400/30 rounded-lg p-4">
          <p className="text-yellow-400 text-sm mb-1">Maintainability</p>
          <p className="text-2xl font-bold text-white">{stats.maintainability}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Search improvements..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
          />
        </div>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 rounded-md bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" style={{ backgroundColor: '#1e293b', color: '#fff' }}>All Types</option>
          <option value="performance" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Performance</option>
          <option value="readability" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Readability</option>
          <option value="best-practice" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Best Practice</option>
          <option value="maintainability" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Maintainability</option>
          <option value="security" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Security</option>
          <option value="error-handling" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Error Handling</option>
        </select>
        <select
          value={selectedPriority}
          onChange={(e) => setSelectedPriority(e.target.value)}
          className="px-4 py-2 rounded-md bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{ colorScheme: 'dark' }}
        >
          <option value="all" style={{ backgroundColor: '#1e293b', color: '#fff' }}>All Impact Levels</option>
          <option value="high" style={{ backgroundColor: '#1e293b', color: '#fff' }}>High Impact</option>
          <option value="medium" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Medium Impact</option>
          <option value="low" style={{ backgroundColor: '#1e293b', color: '#fff' }}>Low Impact</option>
        </select>
      </div>

      {/* Improvements List */}
      {filteredImprovements.length === 0 ? (
        <div className="text-center py-12 bg-white/5 rounded-lg border border-white/10">
          <TrendingUp className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            {improvements.length === 0 ? 'No Improvements Suggested' : 'No Results'}
          </h3>
          <p className="text-gray-400">
            {improvements.length === 0
              ? 'Your code is already optimized!'
              : 'Try adjusting your filters'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredImprovements.map((improvement) => (
            <div
              key={improvement.id}
              className="bg-white/5 rounded-lg p-6 border border-white/10 hover:border-blue-400/50 transition-colors"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Badge className={`${getTypeStyle(improvement.category)} border`}>
                      {improvement.category.replace('-', ' ').toUpperCase()}
                    </Badge>
                    <Badge className={`${getPriorityColor(improvement.impact_level)} border`}>
                      {improvement.impact_level.toUpperCase()} IMPACT
                    </Badge>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {improvement.title}
                  </h3>
                </div>
                <Sparkles className="h-6 w-6 text-blue-400 flex-shrink-0" />
              </div>

              {/* Description */}
              <p className="text-gray-300 mb-3">{improvement.description}</p>

              {/* File Location */}
              <div className="bg-white/5 rounded px-3 py-2 mb-3">
                <p className="text-sm text-gray-400">Location:</p>
                <p className="text-sm text-white font-mono">
                  {improvement.file_path}
                  {improvement.line_number && `:${improvement.line_number}`}
                </p>
              </div>

              {/* Suggestion */}
              <div className="bg-green-500/10 border border-green-400/30 rounded-lg p-4">
                <p className="text-sm font-semibold text-green-400 mb-2">
                  Suggestion:
                </p>
                <p className="text-sm text-gray-300">{improvement.suggestion}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

