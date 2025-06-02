import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const PostDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [likeCount, setLikeCount] = useState(0);
  const [liked, setLiked] = useState(false);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/posts/${id}`);
        setPost(res.data);
        setLikeCount(res.data.likes_count || 0);
        setLiked(res.data.liked_by_user || false);
      } catch (e) {
        setError('Пост не найден');
      }
    };
    const fetchComments = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/posts/${id}/comments`);
        setComments(res.data);
      } catch (e) {
        setComments([]);
      }
    };
    fetchPost();
    fetchComments();
    setLoading(false);
  }, [id]);

  const handleLike = async () => {
    try {
      if (!liked) {
        await axios.post(`http://localhost:8000/api/posts/${id}/like`);
        setLikeCount(likeCount + 1);
        setLiked(true);
      } else {
        await axios.delete(`http://localhost:8000/api/posts/${id}/like`);
        setLikeCount(likeCount - 1);
        setLiked(false);
      }
    } catch {}
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    try {
      await axios.post(
        `http://localhost:8000/api/posts/${id}/comments`,
        { content: commentText },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setCommentText('');
      const res = await axios.get(`http://localhost:8000/api/posts/${id}/comments`);
      setComments(res.data);
    } catch (e) {
      setError('Ошибка при добавлении комментария');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!post) return null;

  return (
    <div>
      <h1>{post.title}</h1>
      <div style={{ color: '#888', marginBottom: 8 }}>Автор: {post.author_username}</div>
      <div style={{ marginBottom: 16 }}>{post.content}</div>
      <div style={{ marginBottom: 16 }}>
        <button onClick={handleLike} disabled={!user} style={{ marginRight: 8 }}>
          {liked ? '❤️' : '🤍'}
        </button>
        <span>{likeCount} лайков</span>
      </div>
      <h2>Комментарии</h2>
      {user && (
        <form onSubmit={handleComment} style={{ marginBottom: 16 }}>
          <input
            type="text"
            value={commentText}
            onChange={e => setCommentText(e.target.value)}
            placeholder="Ваш комментарий..."
            style={{ width: '70%', marginRight: 8 }}
          />
          <button type="submit">Отправить</button>
        </form>
      )}
      {comments.length === 0 ? (
        <p>Комментариев пока нет.</p>
      ) : (
        <ul>
          {comments.map(comment => (
            <li key={comment.id}>
              <b>{comment.author_username}:</b> {comment.content}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PostDetail; 