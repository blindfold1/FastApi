import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const PostList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/posts/');
        setPosts(res.data);
      } catch (e) {
        setError('Ошибка при загрузке постов');
      } finally {
        setLoading(false);
      }
    };
    fetchPosts();
  }, []);

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1>Посты</h1>
      {posts.length === 0 ? (
        <p>Постов пока нет.</p>
      ) : (
        <ul>
          {posts.map(post => (
            <li key={post.id}>
              <Link to={`/posts/${post.id}`}>{post.title}</Link>
              <div style={{ fontSize: 12, color: '#888' }}>Автор: {post.author_username}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PostList; 