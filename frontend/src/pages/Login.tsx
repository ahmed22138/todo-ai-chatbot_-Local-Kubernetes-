import React, { useState } from 'react';
import { devLogin } from '../services/auth';
import './Login.css';

interface LoginProps {
  onLogin: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDevLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await devLogin();
      onLogin();
    } catch (err: any) {
      setError(err.message || 'Failed to login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>Todo AI Chatbot</h1>
        <p className="login-subtitle">Manage your tasks with natural language</p>

        <div className="login-card">
          <h2>Development Login</h2>
          <p className="dev-note">
            This is a development authentication. In production, this would be replaced
            with proper user authentication.
          </p>

          {error && <div className="error-message">{error}</div>}

          <button
            onClick={handleDevLogin}
            disabled={isLoading}
            className="login-button"
          >
            {isLoading ? 'Logging in...' : 'Continue as Test User'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
