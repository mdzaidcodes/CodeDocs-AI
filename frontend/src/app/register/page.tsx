'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Code2, Mail, Lock, User, Check, X } from 'lucide-react';
import Swal from 'sweetalert2';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { AuthResponse } from '@/types';

/**
 * Register Page Component
 * Handles new user registration
 */
export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Calculate password strength based on requirements
   * Requirements: 12+ chars, 1 uppercase, 1 special symbol
   */
  const passwordStrength = useMemo(() => {
    const password = formData.password;
    
    if (!password) {
      return { score: 0, label: '', color: '', checks: [] };
    }

    const checks = [
      {
        label: 'At least 12 characters',
        passed: password.length >= 12,
      },
      {
        label: 'One uppercase letter',
        passed: /[A-Z]/.test(password),
      },
      {
        label: 'One special symbol (!@#$%^&* etc.)',
        passed: /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]/.test(password),
      },
    ];

    const passedCount = checks.filter((c) => c.passed).length;
    const score = (passedCount / checks.length) * 100;

    let label = '';
    let color = '';

    if (score === 0) {
      label = '';
      color = '';
    } else if (score < 50) {
      label = 'Weak';
      color = 'text-red-400';
    } else if (score < 100) {
      label = 'Fair';
      color = 'text-yellow-400';
    } else {
      label = 'Strong';
      color = 'text-green-400';
    }

    return { score, label, color, checks };
  }, [formData.password]);

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
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.password || !formData.confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: 'Missing Fields',
        text: 'Please fill in all fields',
        confirmButtonColor: '#3b82f6',
      });
      return;
    }

    // Validate password match
    if (formData.password !== formData.confirmPassword) {
      Swal.fire({
        icon: 'error',
        title: 'Password Mismatch',
        text: 'Passwords do not match',
        confirmButtonColor: '#3b82f6',
      });
      return;
    }

    // Validate password strength (all requirements must be met)
    if (passwordStrength.score < 100) {
      const failedChecks = passwordStrength.checks
        .filter((check) => !check.passed)
        .map((check) => check.label)
        .join(', ');
      
      Swal.fire({
        icon: 'error',
        title: 'Password Requirements Not Met',
        text: `Your password must include: ${failedChecks}`,
        confirmButtonColor: '#3b82f6',
      });
      return;
    }

    setIsLoading(true);

    try {
      // Show loading alert
      Swal.fire({
        title: 'Creating your account...',
        text: 'Please wait',
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      // Make API call
      const response = await apiClient.post<{ success: boolean; data: AuthResponse }>('/auth/register', {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        password: formData.password,
      });
      
      // Store token and user data in localStorage
      localStorage.setItem('token', response.data.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.data.user));

      // Show success message
      Swal.fire({
        icon: 'success',
        title: 'Account Created!',
        text: `Welcome, ${response.data.data.user.full_name}!`,
        timer: 1500,
        showConfirmButton: false,
      });

      // Redirect to get-started page
      setTimeout(() => {
        router.push('/get-started');
      }, 1500);
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // Show error message
      Swal.fire({
        icon: 'error',
        title: 'Registration Failed',
        text: error.response?.data?.error || error.response?.data?.message || error.message || 'Email already exists or invalid data',
        confirmButtonColor: '#3b82f6',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-6">
            <Code2 className="h-10 w-10 text-blue-400" />
            <span className="text-2xl font-bold text-white">CodeDocs AI</span>
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-gray-400">Start generating AI-powered documentation</p>
        </div>

        {/* Register Form */}
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* First Name Field */}
            <div className="space-y-2">
              <Label htmlFor="firstName" className="text-gray-300">
                First Name
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="firstName"
                  name="firstName"
                  type="text"
                  placeholder="John"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  required
                />
              </div>
            </div>

            {/* Last Name Field */}
            <div className="space-y-2">
              <Label htmlFor="lastName" className="text-gray-300">
                Last Name
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="lastName"
                  name="lastName"
                  type="text"
                  placeholder="Doe"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  required
                />
              </div>
            </div>

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
              
              {/* Password Strength Indicator */}
              {formData.password && (
                <div className="space-y-2 mt-3">
                  {/* Strength Bar */}
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          passwordStrength.score < 50
                            ? 'bg-red-500'
                            : passwordStrength.score < 100
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                        style={{ width: `${passwordStrength.score}%` }}
                      />
                    </div>
                    {passwordStrength.label && (
                      <span className={`text-sm font-medium ${passwordStrength.color}`}>
                        {passwordStrength.label}
                      </span>
                    )}
                  </div>
                  
                  {/* Requirements Checklist */}
                  <div className="space-y-1">
                    {passwordStrength.checks.map((check, index) => (
                      <div key={index} className="flex items-center space-x-2 text-xs">
                        {check.passed ? (
                          <Check className="h-4 w-4 text-green-400" />
                        ) : (
                          <X className="h-4 w-4 text-gray-400" />
                        )}
                        <span className={check.passed ? 'text-green-400' : 'text-gray-400'}>
                          {check.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-gray-300">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
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
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300 font-semibold">
                Login
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

