import React, { useEffect, useState } from 'react';
import { Card, Spinner, Alert } from 'react-bootstrap';
import api from '../api';

const UserProfile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get('/users/me');
        setUser(res.data);
      } catch (err) {
        setError('Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  if (!localStorage.getItem('token')) {
    return <Alert variant="warning" className="mt-5 text-center">Только для авторизованных пользователей</Alert>;
  }
  if (loading) return <div className="text-center mt-5"><Spinner animation="border" /></div>;
  if (error) return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;
  if (!user) return null;

  return (
    <Card className="mx-auto mt-5" style={{ maxWidth: 500 }}>
      <Card.Body>
        <h3 className="mb-4 text-center">Профиль</h3>
        <p><b>Имя пользователя:</b> {user.username}</p>
        <p><b>Email:</b> {user.email}</p>
        <p><b>Роль:</b> {user.role}</p>
        <p><b>Дата регистрации:</b> {new Date(user.created_at).toLocaleString()}</p>
      </Card.Body>
    </Card>
  );
};

export default UserProfile; 