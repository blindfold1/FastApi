import React, { useState } from 'react';
import { Form, Button, Alert, Card } from 'react-bootstrap';
import api from '../api';

const LoginForm = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      const res = await api.post('/users/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);
      if (onLogin) onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mx-auto" style={{ maxWidth: 400, marginTop: 60 }}>
      <Card.Body>
        <h3 className="mb-4 text-center">Вход</h3>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleSubmit} autoComplete="off">
          <Form.Group className="mb-3">
            <Form.Label>Имя пользователя</Form.Label>
            <Form.Control type="text" value={username} onChange={e => setUsername(e.target.value)} required autoFocus />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Пароль</Form.Label>
            <Form.Control type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </Form.Group>
          <Button type="submit" variant="primary" className="w-100" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default LoginForm;