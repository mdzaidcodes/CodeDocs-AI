import axios, { AxiosInstance, AxiosError } from 'axios';
import Swal from 'sweetalert2';

/**
 * API Client Configuration
 * Creates an axios instance with base configuration and auth interceptors
 */

// Get API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

/**
 * Request interceptor to add JWT token to headers
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('token');
    
    // Add token to headers if it exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => {
    // Return successful responses as-is
    return response;
  },
  (error: AxiosError) => {
    // Handle different error scenarios
    
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      
      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        // Only redirect if not already on auth pages
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        
        Swal.fire({
          icon: 'error',
          title: 'Session Expired',
          text: 'Please login again to continue',
          confirmButtonColor: '#3b82f6',
        });
      } else if (status === 403) {
        // Forbidden
        Swal.fire({
          icon: 'error',
          title: 'Access Denied',
          text: 'You do not have permission to perform this action',
          confirmButtonColor: '#3b82f6',
        });
      } else if (status === 404) {
        // Not found - don't show alert for 404s
        console.error('Resource not found:', error.config?.url);
      } else if (status >= 500) {
        // Server error
        Swal.fire({
          icon: 'error',
          title: 'Server Error',
          text: 'Something went wrong on our end. Please try again later.',
          confirmButtonColor: '#3b82f6',
        });
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response received:', error.request);
      
      Swal.fire({
        icon: 'error',
        title: 'Network Error',
        text: 'Unable to connect to the server. Please check your internet connection.',
        confirmButtonColor: '#3b82f6',
      });
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;

/**
 * Helper function to get auth headers
 */
export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Helper function to check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('token');
};

/**
 * Helper function to get current user
 */
export const getCurrentUser = () => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Helper function to logout user
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

