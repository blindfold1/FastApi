import './App.css'; // Импорт стилей
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import axios from 'axios';
import ErrorBoundary from './ErrorBoundary';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './Dashboard';
import FoodList from './components/FoodList';
import FoodForm from './components/FoodForm';
import Tracker from './components/Tracker';
import TrackerEntryForm from './components/TrackerEntryForm';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = () => {
    const accessToken = localStorage.getItem('access_token');
    setIsAuthenticated(!!accessToken);
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await axios.post('http://127.0.0.1:8000/auth/refresh', null, {
        headers: {
          Authorization: `Bearer ${refreshToken}`,
        },
      });
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setIsAuthenticated(true);
      return response.data.access_token;
    } catch (err) {
      console.error('Failed to refresh token:', err.response?.data || err.message);
      handleLogout();
      return null;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  useEffect(() => {
    checkAuth();

    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const newAccessToken = await refreshToken();
          if (newAccessToken) {
            originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            return axios(originalRequest);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(interceptor);
  }, []);

  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          {isAuthenticated && (
            <nav>
              <Link to="/dashboard">Dashboard</Link> |{' '}
              <Link to="/foods">Foods</Link> |{' '}
              <Link to="/tracker">Tracker</Link> |{' '}
              <button onClick={handleLogout}>Logout</button>
            </nav>
          )}
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" />
                ) : (
                  <LoginForm onLogin={setIsAuthenticated} />
                )
              }
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" />
                ) : (
                  <RegisterForm onRegister={setIsAuthenticated} />
                )
              }
            />
            <Route
              path="/dashboard"
              element={
                isAuthenticated ? <Dashboard /> : <Navigate to="/" />
              }
            />
            <Route
              path="/foods"
              element={
                isAuthenticated ? (
                  <div>
                    <FoodForm onAddFood={(food) => console.log('Food added:', food)} />
                    <FoodList />
                  </div>
                ) : (
                  <Navigate to="/" />
                )
              }
            />
            <Route
              path="/tracker"
              element={
                isAuthenticated ? (
                  <div>
                    <TrackerEntryForm onAddEntry={(entry) => console.log('Entry added:', entry)} />
                    <Tracker />
                  </div>
                ) : (
                  <Navigate to="/" />
                )
              }
            />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;