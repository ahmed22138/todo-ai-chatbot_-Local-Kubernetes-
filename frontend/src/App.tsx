import React, { useState, useEffect } from 'react';
import { Chat } from './pages/Chat';
import { Auth } from './pages/Auth';
import { isAuthenticated } from './services/auth';

const App: React.FC = () => {
  // Start with null to show loading, then check auth
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Small delay to ensure clean state check
    const checkAuth = () => {
      const isAuth = isAuthenticated();
      setAuthenticated(isAuth);
    };

    // Check auth after component mounts
    setTimeout(checkAuth, 100);
  }, []);

  const handleLogin = () => {
    setAuthenticated(true);
  };

  // Show loading briefly while checking auth
  if (authenticated === null) {
    return (
      <div style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)',
        color: 'white',
        fontSize: '1.2rem'
      }}>
        Loading...
      </div>
    );
  }

  // Show login page if not authenticated
  if (!authenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  // Show chat after successful login
  return (
    <div className="App">
      <Chat />
    </div>
  );
};

export default App;
