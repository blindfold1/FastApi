import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert } from 'react-bootstrap';
import api from '../api';

const PostForm = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/posts/', {
        title,
        content,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        is_published: true
      });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания поста');
    } finally {
      setLoading(false);
    }
  };

  if (!localStorage.getItem('token')) {
    return <Alert variant="warning" className="mt-5 text-center">Только для авторизованных пользователей</Alert>;
  }

  return (
    <Card className="mx-auto" style={{ maxWidth: 600, marginTop: 60 }}>
      <Card.Body>
        <h3 className="mb-4 text-center">Создать пост</h3>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form onSubmit={handleSubmit} autoComplete="off">
          <Form.Group className="mb-3">
            <Form.Label>Заголовок</Form.Label>
            <Form.Control type="text" value={title} onChange={e => setTitle(e.target.value)} required autoFocus />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Текст</Form.Label>
            <Form.Control as="textarea" rows={5} value={content} onChange={e => setContent(e.target.value)} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Теги (через запятую)</Form.Label>
            <Form.Control type="text" value={tags} onChange={e => setTags(e.target.value)} />
          </Form.Group>
          <Button type="submit" variant="primary" className="w-100" disabled={loading}>
            {loading ? 'Создание...' : 'Создать'}
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default PostForm; 