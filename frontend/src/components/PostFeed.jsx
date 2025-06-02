import React, { useEffect, useState } from 'react';
import { Card, Button, Spinner, Alert, Row, Col, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../api';

const PostFeed = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get('/posts/feed');
        setPosts(res.data);
      } catch (err) {
        setError('Ошибка загрузки постов');
      } finally {
        setLoading(false);
      }
    };
    fetchPosts();
  }, []);

  if (loading) return <div className="text-center mt-5">Loading...</div>;
  if (error) return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Лента постов</h2>
      <Row>
        {posts.map(post => (
          <Col md={6} key={post.id} className="mb-4">
            <Card>
              <Card.Body>
                <Card.Title as={Link} to={`/post/${post.id}`}>{post.title}</Card.Title>
                <div className="mb-2">
                  <Badge bg="secondary" className="me-2">{post.author_username}</Badge>
                  <Badge bg="light" text="dark">{new Date(post.created_at).toLocaleString()}</Badge>
                </div>
                <Card.Text>{post.content.slice(0, 120)}...</Card.Text>
                <div className="d-flex justify-content-between align-items-center mt-3">
                  <div>
                    <span role="img" aria-label="like">👍</span> {post.likes_count}
                    <span className="ms-3" role="img" aria-label="comments">💬</span> {post.comments_count}
                  </div>
                  <Button as={Link} to={`/post/${post.id}`} variant="outline-primary" size="sm">Читать</Button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default PostFeed; 