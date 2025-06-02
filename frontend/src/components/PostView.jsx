import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Spinner, Alert, Button, Form, ListGroup } from 'react-bootstrap';
import api from '../api';

const PostView = () => {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [likeLoading, setLikeLoading] = useState(false);
  const [commentLoading, setCommentLoading] = useState(false);

  const fetchPost = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/posts/${postId}`);
      setPost(res.data);
      const cRes = await api.get(`/posts/${postId}/comments`);
      setComments(cRes.data);
    } catch (err) {
      setError('Ошибка загрузки поста');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPost();
    // eslint-disable-next-line
  }, [postId]);

  const handleLike = async () => {
    setLikeLoading(true);
    try {
      await api.post(`/posts/${postId}/like`);
      await fetchPost();
    } catch {}
    setLikeLoading(false);
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    setCommentLoading(true);
    try {
      await api.post(`/posts/${postId}/comments`, { content: comment });
      setComment('');
      await fetchPost();
    } catch {}
    setCommentLoading(false);
  };

  if (loading) return <div className="text-center mt-5">Loading...</div>;
  if (error) return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;
  if (!post) return null;

  return (
    <div className="container mt-4">
      <Card className="mb-4">
        <Card.Body>
          <Card.Title>{post.title}</Card.Title>
          <div className="mb-2 text-muted">Автор: {post.author_username} • {new Date(post.created_at).toLocaleString()}</div>
          <Card.Text>{post.content}</Card.Text>
          <div className="d-flex align-items-center gap-3">
            <Button variant="outline-primary" size="sm" onClick={handleLike} disabled={likeLoading}>
              👍 {post.likes_count}
            </Button>
            <span>💬 {post.comments_count}</span>
          </div>
        </Card.Body>
      </Card>
      <h5>Комментарии</h5>
      <ListGroup className="mb-3">
        {comments.map(c => (
          <ListGroup.Item key={c.id}>
            <b>{c.author_username}</b> <span className="text-muted">{new Date(c.created_at).toLocaleString()}</span>
            <div>{c.content}</div>
          </ListGroup.Item>
        ))}
        {comments.length === 0 && <ListGroup.Item>Нет комментариев</ListGroup.Item>}
      </ListGroup>
      {localStorage.getItem('token') && (
        <Form onSubmit={handleComment} className="mb-3">
          <Form.Group>
            <Form.Control
              as="textarea"
              rows={2}
              value={comment}
              onChange={e => setComment(e.target.value)}
              placeholder="Добавить комментарий..."
              required
            />
          </Form.Group>
          <Button type="submit" variant="primary" className="mt-2" disabled={commentLoading}>
            {commentLoading ? 'Отправка...' : 'Отправить'}
          </Button>
        </Form>
      )}
    </div>
  );
};

export default PostView; 