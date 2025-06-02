import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const WorkoutDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workout, setWorkout] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchWorkout = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/api/workouts/${id}`);
        setWorkout(res.data);
      } catch (e) {
        setError('Тренировка не найдена');
      } finally {
        setLoading(false);
      }
    };
    fetchWorkout();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Удалить эту тренировку?')) return;
    try {
      await axios.delete(`http://localhost:8000/api/workouts/${id}`);
      navigate('/workouts');
    } catch (e) {
      setError('Ошибка при удалении');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!workout) return null;

  return (
    <div>
      <h1>{workout.title}</h1>
      <div style={{ color: '#888', marginBottom: 8 }}>Дата: {new Date(workout.date).toLocaleString('ru-RU')}</div>
      <div style={{ marginBottom: 8 }}>Длительность: {workout.duration} минут</div>
      <div style={{ marginBottom: 16 }}>Заметки: {workout.notes || '—'}</div>
      <h2>Упражнения</h2>
      <ul>
        {workout.exercises.map((ex, i) => (
          <li key={i}>
            <b>{ex.name}</b>: {ex.sets} x {ex.reps} {ex.weight ? `(${ex.weight} кг)` : ''} {ex.notes && `— ${ex.notes}`}
          </li>
        ))}
      </ul>
      <button onClick={handleDelete} style={{ marginTop: 24, background: '#d32f2f', color: 'white' }}>
        Удалить тренировку
      </button>
    </div>
  );
};

export default WorkoutDetail; 