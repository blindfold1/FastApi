import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './auth-form.css';

const Register = () => {
  const { register, isAuthenticated } = useAuth();
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'user',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError('Ошибка регистрации. Возможно, пользователь с таким именем или email уже существует.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h1>Регистрация</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="text"
          name="username"
          placeholder="Имя пользователя"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Пароль"
          value={form.password}
          onChange={handleChange}
          required
        />
        <select name="role" value={form.role} onChange={handleChange} required>
          <option value="user">Обычный пользователь</option>
          <option value="trainer">Тренер</option>
        </select>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>
      <div style={{ marginTop: 16 }}>
        Уже есть аккаунт? <a href="/login">Войти</a>
      </div>
    </div>
  );
};

export default Register; 