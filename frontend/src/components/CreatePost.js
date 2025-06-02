import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './auth-form.css';

const CreatePost = () => {
  const { isTrainer, isAdmin } = useAuth();
  const [form, setForm] = useState({ title: '', content: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  if (!isTrainer && !isAdmin) {
    return <div className="error">Только тренеры и администраторы могут создавать посты.</div>;
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/posts/', form);
      navigate(`/posts/${res.data.id}`);
    } catch (err) {
      setError('Ошибка при создании поста');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h1>Создать пост</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="text"
          name="title"
          placeholder="Заголовок"
          value={form.title}
          onChange={handleChange}
          required
        />
        <textarea
          name="content"
          placeholder="Текст поста"
          value={form.content}
          onChange={handleChange}
          rows={6}
          required
        />
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Создание...' : 'Создать пост'}
        </button>
      </form>
    </div>
  );
};

export default CreatePost; 