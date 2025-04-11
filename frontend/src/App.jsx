import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Dashboard from './Dashboard';
import ErrorBoundary from './ErrorBoundary';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  console.log('App.jsx: Rendering App component'); // Отладка

  const login = async (username, password) => {
    console.log('App.jsx: login function called with:', { username, password }); // Отладка
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/token', {
        username,
        password,
      });
      console.log('App.jsx: Login response:', response.data); // Отладка
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setIsAuthenticated(true);
      setError('');
    } catch (err) {
      console.error('App.jsx: Login error:', err); // Отладка
      setError('Login failed: ' + (err.response?.data?.detail || err.message));
      setIsAuthenticated(false);
    }
  };

  const checkAuth = () => {
    const accessToken = localStorage.getItem('access_token');
    console.log('App.jsx: Access token:', accessToken); // Отладка
    if (accessToken) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  console.log('App.jsx: isAuthenticated:', isAuthenticated); // Отладка

  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" />
                ) : (
                  <div>
                    <h1>Login</h1>
                    {error && <p className="error">{error}</p>}
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        const username = e.target.username.value;
                        const password = e.target.password.value;
                        console.log('App.jsx: Form submitted with:', { username, password }); // Отладка
                        login(username, password);
                      }}
                    >
                      <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        required
                      />
                      <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        required
                      />
                      <button type="submit">Login</button>
                    </form>
                  </div>
                )
              }
            />
            <Route
              path="/dashboard"
              element={
                isAuthenticated ? <Dashboard /> : <Navigate to="/" />
              }
            />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;