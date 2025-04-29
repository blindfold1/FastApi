import React, { useState } from 'react';
import axios from 'axios';

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Проверка на пустые поля после удаления пробелов
    const trimmedUsername = username.trim();
    const trimmedPassword = password.trim();
    if (!trimmedUsername || !trimmedPassword) {
      setError('Username and password are required');
      return;
    }

    try {
      const formData = new URLSearchParams();
      formData.append('username', trimmedUsername);
      formData.append('password', trimmedPassword);

      console.log('Sending login request to /auth/token with data:', formData.toString());

      const response = await axios.post('http://127.0.0.1:8000/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('Login response:', response.data);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      setError('');
      onLogin(true);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
      console.error('Login error:', err.response?.data || err);
      setError(`Login failed: ${errorMessage}`);
      onLogin(false);
    }
  };

  return (
    <div>
      <h1>Login</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginForm;