'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Code2, Mail, Lock } from 'lucide-react';
import Swal from 'sweetalert2';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { AuthResponse } from '@/types';

/**
 * Login Page Component
 * Handles user authentication with email and password
 */
export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);

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
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate inputs
    if (!formData.email || !formData.password) {
      Swal.fire({
        icon: 'error',
        title: 'Missing Fields',
        text: 'Please fill in all fields',
        confirmButtonColor: '#3b82f6',
      });
      return;
    }

    setIsLoading(true);

    try {
      // Show loading alert
      Swal.fire({
        title: 'Logging in...',
        text: 'Please wait',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Make API call
      const response = await apiClient.post<{ success: boolean; data: AuthResponse }>('/auth/login', formData);
      
      // Store token and user data in localStorage
      localStorage.setItem('token', response.data.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.data.user));

      // Show success message
      Swal.fire({
        icon: 'success',
        title: 'Login Successful!',
        text: `Welcome back, ${response.data.data.user.full_name}!`,
        timer: 1500,
        showConfirmButton: false,
      });

      // Redirect to dashboard
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    } catch (error: any) {
      console.error('Login error:', error);
      
      // Show error message
      Swal.fire({
        icon: 'error',
        title: 'Login Failed',
        text: error.response?.data?.error || error.response?.data?.message || error.message || 'Invalid email or password',
        confirmButtonColor: '#3b82f6',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-6">
            <Code2 className="h-10 w-10 text-blue-400" />
            <span className="text-2xl font-bold text-white">CodeDocs AI</span>
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">Login to continue to your dashboard</p>
        </div>

        {/* Login Form */}
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-gray-300">
                Email Address
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-gray-300">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don&apos;t have an account?{' '}
              <Link href="/register" className="text-blue-400 hover:text-blue-300 font-semibold">
                Sign up
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-gray-400 hover:text-white text-sm">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

