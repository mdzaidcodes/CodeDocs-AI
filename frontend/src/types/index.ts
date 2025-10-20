// User authentication types
export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

// Project types
export interface Project {
  id: string;
  name: string;
  description?: string;
  source_type: 'upload' | 'github';
  github_url?: string;
  github_branch?: string;
  language?: string;
  file_count?: number;
  security_score?: number;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  color_palette?: {
    colors: Array<{
      hex: string;
      name: string;
      category: string;
      description: string;
      frequency: number;
      rgb: { r: number; g: number; b: number };
    }>;
    total_colors_found: number;
    scheme_type: string;
  };
}

export interface ProjectStats {
  total_files: number;
  total_lines: number;
  languages: { [key: string]: number };
  security_issues: number;
  improvement_suggestions: number;
}

// Documentation types
export interface Documentation {
  id: string;
  project_id: string;
  content: string;
  sections: {
    overview?: string;
    purpose?: string;
    setup?: string;
    architecture?: string;
    api?: string;
    usage?: string;
  };
  created_at: string;
  updated_at: string;
}

// Security types
export interface SecurityFinding {
  id: string;
  project_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  title: string;
  description: string;
  file_path: string;
  line_number?: number;
  code_snippet?: string;
  recommendation: string;
  cwe_id?: string;
  cvss_score?: number;
  references?: any[]; // JSON array
  status?: 'open' | 'acknowledged' | 'fixed' | 'false_positive' | 'wont_fix';
  notes?: string;
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
}

// Code improvement types
export interface CodeImprovement {
  id: string;
  project_id: string;
  category: string; // e.g., 'performance', 'readability', 'best-practice', 'maintainability'
  title: string;
  description: string;
  file_path: string;
  line_number?: number;
  code_snippet?: string;
  improved_code?: string;
  suggestion: string;
  impact_level: 'high' | 'medium' | 'low';
  estimated_effort?: 'high' | 'medium' | 'low';
  status?: 'pending' | 'implemented' | 'dismissed';
  created_at: string;
  updated_at?: string;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  message: string;
  sources?: string[];
}

// Upload types
export interface UploadFile {
  path: string;
  name: string;
  size: number;
  type: string;
}

// GitHub connection types
export interface GitHubConnection {
  url: string;
  branch: string;
  pat?: string;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface ProjectStatus {
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  message?: string;
}

