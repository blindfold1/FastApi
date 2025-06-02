import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Здесь можно добавить запрос для получения данных пользователя
      setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/users/login', 
        `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      const { access_token, role } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser({ token: access_token, role });
      return true;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('http://localhost:8000/api/users/', userData);
      const { access_token, role } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser({ token: access_token, role });
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isTrainer: user?.role === 'trainer'
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}; 