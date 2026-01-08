import React, { useState } from 'react';
import { devLogin, login, signup } from '../services/auth';
import './Auth.css';

interface AuthProps {
  onLogin: () => void;
}

export const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsLoading(false);
      return;
    }

    try {
      if (isLogin) {
        // Login flow - call real backend API
        await login({
          email: email,
          password: password,
        });
        await new Promise(resolve => setTimeout(resolve, 500));
        onLogin();
      } else {
        // Signup flow - call real backend API
        await signup({
          email: email,
          password: password,
          name: name || undefined,
        });
        await new Promise(resolve => setTimeout(resolve, 500));
        // After successful signup, show success message and switch to login
        setSuccessMessage('Account created successfully! Please login with your credentials.');
        setIsLogin(true); // Switch to login tab
        setPassword(''); // Clear password for security
        // Do NOT auto-login - user must manually login
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickStart = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await devLogin();
      await new Promise(resolve => setTimeout(resolve, 500));
      onLogin();
    } catch (err: any) {
      setError(err.message || 'Quick start failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="app-logo">
              <div className="logo-icon">✓</div>
              <h1>TodoAI</h1>
            </div>
            <p className="app-tagline">Manage tasks with AI-powered conversations</p>
          </div>

          <div className="auth-tabs">
            <button
              className={`tab ${isLogin ? 'active' : ''}`}
              onClick={() => setIsLogin(true)}
            >
              Login
            </button>
            <button
              className={`tab ${!isLogin ? 'active' : ''}`}
              onClick={() => setIsLogin(false)}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  id="name"
                  type="text"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required={!isLogin}
                  disabled={isLoading}
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                minLength={8}
              />
              <small style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
                Minimum 8 characters required
              </small>
            </div>

            {error && (
              <div className="error-banner">
                <span className="error-icon">⚠</span>
                {error}
              </div>
            )}

            {successMessage && (
              <div className="success-banner">
                <span className="success-icon">✓</span>
                {successMessage}
              </div>
            )}

            <button
              type="submit"
              className="submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  {isLogin ? 'Logging in...' : 'Creating account...'}
                </>
              ) : (
                isLogin ? 'Login' : 'Create Account'
              )}
            </button>
          </form>

          <div className="divider">
            <span>or</span>
          </div>

          <button
            onClick={handleQuickStart}
            className="quick-start-btn"
            disabled={isLoading}
          >
            <span className="quick-icon">⚡</span>
            Quick Start (Demo Mode)
          </button>

          <p className="auth-footer-text">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              className="switch-mode-btn"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? 'Sign up' : 'Login'}
            </button>
          </p>
        </div>

        <div className="features-section">
          <h3>Why TodoAI?</h3>
          <div className="feature-grid">
            <div className="feature-item">
              <div className="feature-icon">🤖</div>
              <h4>AI-Powered</h4>
              <p>Natural language task management</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">💬</div>
              <h4>Conversational</h4>
              <p>Chat with your todo list</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">⚡</div>
              <h4>Fast & Simple</h4>
              <p>Add tasks in seconds</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <h4>Smart History</h4>
              <p>Track all conversations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
