import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Profile = () => {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const postsRes = await axios.get('http://localhost:8000/api/posts/?mine=true');
        setPosts(postsRes.data);
      } catch (e) {
        setPosts([]);
      }
      try {
        const workoutsRes = await axios.get('http://localhost:8000/api/workouts/');
        setWorkouts(workoutsRes.data);
      } catch (e) {
        setWorkouts([]);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  if (!user) return <div className="error">Войдите в аккаунт</div>;
  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div>
      <h1>Профиль</h1>
      <div style={{ marginBottom: 24 }}>
        <b>Имя пользователя:</b> {user.username || '—'}<br />
        <b>Роль:</b> {user.role || '—'}
      </div>
      <h2>Мои посты</h2>
      {posts.length === 0 ? <p>Нет постов</p> : (
        <ul>
          {posts.map(post => (
            <li key={post.id}><Link to={`/posts/${post.id}`}>{post.title}</Link></li>
          ))}
        </ul>
      )}
      <h2>Мои тренировки</h2>
      {workouts.length === 0 ? <p>Нет тренировок</p> : (
        <ul>
          {workouts.map(workout => (
            <li key={workout.id}><Link to={`/workouts/${workout.id}`}>{workout.title}</Link></li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Profile; 