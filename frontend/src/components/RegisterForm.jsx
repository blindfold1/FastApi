import React, { useState } from 'react';
import axios from 'axios';

const RegisterForm = ({ onRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/register', {
        username,
        password,
      });
      setError('');
      onRegister(true); // Уведомляем родительский компонент об успешной регистрации
    } catch (err) {
      setError('Registration failed: ' + (err.response?.data?.detail || err.message));
      onRegister(false);
    }
  };

  return (
    <div>
      <h1>Register</h1>
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
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default RegisterForm;