import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('accessToken'));
  const [loading, setLoading] = useState(true);

  // Initialize/Restore session
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // If we have a token, fetch the profile to confirm it's valid and get user info
          const response = await api.get('/api/users/profile/');
          setUser(response.data);
        } catch (error) {
          console.error("Session restore failed", error);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      // NOTE: Using 'username' field for email as per standard DRF behavior if tailored, 
      // but checking CustomTokenObtainPairView assumes it accepts username/password 
      // or email/password depending on config. Trying 'username': email.
      const response = await api.post('/api/users/login/', {
        username: email,
        password
      });

      const { tokens, user } = response.data;

      // Save tokens
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      setToken(tokens.access);

      // Set user directly from login response
      setUser(user);

      return { success: true };
    } catch (error) {
      console.error("Login failed", error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      await api.post('/api/users/register/', userData);
      // Auto login after register? Or require manual login. 
      // Let's assume manual login for security unless requested otherwise.
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Registration failed'
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
