import React, { useState, useEffect, useCallback } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

const API_BASE_URL = 'http://localhost:8080/api';

const App = () => {
  const [activeView, setActiveView] = useState('login');
  const [currentUser, setCurrentUser] = useState(null);

  const verifyToken = useCallback(async (authToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-token`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.valid) {
        setCurrentUser(data.user);
        setActiveView('dashboard');
      } else {
        handleLogout();
      }
    } catch (err) {
      console.error('Token verification failed:', err);
      handleLogout();
    }
  }, []);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      verifyToken(savedToken);
    }
  }, [verifyToken]);

  const handleLoginSuccess = (token, user) => {
    localStorage.setItem('token', token);
    setCurrentUser(user);
    setActiveView('dashboard');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('token');
    setActiveView('login');
  };

  const switchToRegister = () => {
    setActiveView('register');
  };

  const switchToLogin = () => {
    setActiveView('login');
  };

  if (activeView === 'dashboard' && currentUser) {
    return <Dashboard currentUser={currentUser} onLogout={handleLogout} />;
  } else if (activeView === 'register') {
    return <Register onSwitchToLogin={switchToLogin} />;
  } else {
    return <Login onLoginSuccess={handleLoginSuccess} onSwitchToRegister={switchToRegister} />;
  }
};

export default App;