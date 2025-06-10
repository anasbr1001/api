'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface AuthFormProps {
  mode: 'login' | 'register';
}

export default function AuthForm({ mode }: AuthFormProps) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    const { username, email, password, confirmPassword } = formData;

    if (!username.trim()) {
      setError('Username is required');
      return false;
    }
    if (username.length < 2) {
      setError('Username must be at least 2 characters long');
      return false;
    }

    if (mode === 'register') {
      if (!email.trim()) {
        setError('Email is required');
        return false;
      }
      if (!email.includes('@')) {
        setError('Invalid email format');
        return false;
      }
      if (password.length < 8) {
        setError('Password must be at least 8 characters long');
        return false;
      }
      if (!/[A-Z]/.test(password)) {
        setError('Password must contain at least one uppercase letter');
        return false;
      }
      if (!/[a-z]/.test(password)) {
        setError('Password must contain at least one lowercase letter');
        return false;
      }
      if (!/[0-9]/.test(password)) {
        setError('Password must contain at least one number');
        return false;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
    }

    if (!password.trim()) {
      setError('Password is required');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    try {
      if (mode === 'login') {
        await login(formData.username, formData.password);
      } else {
        await register(
          formData.username,
          formData.email,
          formData.password,
          formData.confirmPassword
        );
      }
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h2>{mode === 'login' ? 'Login' : 'Register'}</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            className="form-input"
            required
            minLength={2}
          />
        </div>

        {mode === 'register' && (
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              required
              pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input"
            required
            minLength={mode === 'register' ? 8 : 1}
          />
          {mode === 'register' && (
            <div className="password-requirements">
              <p>Password must:</p>
              <ul>
                <li>Be at least 8 characters long</li>
                <li>Contain at least one uppercase letter</li>
                <li>Contain at least one lowercase letter</li>
                <li>Contain at least one number</li>
              </ul>
            </div>
          )}
        </div>

        {mode === 'register' && (
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="form-input"
              required
              minLength={8}
            />
          </div>
        )}

        <button type="submit" className="submit-btn">
          {mode === 'login' ? 'Login' : 'Register'}
        </button>

        <div className="auth-links">
          {mode === 'login' ? (
            <>
              <Link href="/register" className="auth-link">
                Need an account? Register
              </Link>
              <Link href="/forgot-password" className="auth-link">
                Forgot Password?
              </Link>
            </>
          ) : (
            <Link href="/login" className="auth-link">
              Already have an account? Login
            </Link>
          )}
        </div>
      </form>
    </div>
  );
} 