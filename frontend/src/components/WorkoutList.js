import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import './WorkoutList.css';

const WorkoutList = () => {
  const { user } = useAuth();
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWorkouts = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/workouts/');
        setWorkouts(response.data);
        setLoading(false);
      } catch (err) {
        setError('Ошибка при загрузке тренировок');
        setLoading(false);
      }
    };

    fetchWorkouts();
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="workout-list">
      <div className="workout-header">
        <h1>Мои тренировки</h1>
        <Link to="/create-workout" className="create-btn">
          Новая тренировка
        </Link>
      </div>

      {workouts.length === 0 ? (
        <div className="no-workouts">
          <p>У вас пока нет тренировок</p>
          <Link to="/create-workout" className="create-btn">
            Создать первую тренировку
          </Link>
        </div>
      ) : (
        <div className="workouts-grid">
          {workouts.map(workout => (
            <Link to={`/workouts/${workout.id}`} key={workout.id} className="workout-card">
              <div className="workout-info">
                <h3>{workout.title}</h3>
                <p className="workout-date">{formatDate(workout.date)}</p>
                <p className="workout-duration">
                  Длительность: {workout.duration} минут
                </p>
                <div className="workout-exercises">
                  <h4>Упражнения:</h4>
                  <ul>
                    {workout.exercises.map(exercise => (
                      <li key={exercise.exercise_id}>
                        {exercise.name} - {exercise.sets} x {exercise.reps}
                        {exercise.weight && ` (${exercise.weight} кг)`}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkoutList; 