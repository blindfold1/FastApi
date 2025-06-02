import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import './ExerciseDetail.css';

const ExerciseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin, isTrainer } = useAuth();
  const [exercise, setExercise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/exercises/${id}`);
        setExercise(response.data);
        setLoading(false);
      } catch (err) {
        setError('Ошибка при загрузке упражнения');
        setLoading(false);
      }
    };

    fetchExercise();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить это упражнение?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:8000/api/exercises/${id}`);
      navigate('/exercises');
    } catch (err) {
      setError('Ошибка при удалении упражнения');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!exercise) return <div className="error">Упражнение не найдено</div>;

  return (
    <div className="exercise-detail">
      <div className="exercise-header">
        <h1>{exercise.name}</h1>
        {(isAdmin || isTrainer) && (
          <div className="exercise-actions">
            <button 
              className="edit-btn"
              onClick={() => navigate(`/exercises/${id}/edit`)}
            >
              Редактировать
            </button>
            <button 
              className="delete-btn"
              onClick={handleDelete}
            >
              Удалить
            </button>
          </div>
        )}
      </div>

      {exercise.image_url && (
        <img 
          src={exercise.image_url} 
          alt={exercise.name} 
          className="exercise-image"
        />
      )}

      <div className="exercise-content">
        <div className="exercise-info">
          <h2>Описание</h2>
          <p>{exercise.description}</p>

          <h2>Тип упражнения</h2>
          <p className="exercise-type">{exercise.type}</p>

          <h2>Целевые мышцы</h2>
          <div className="muscle-tags">
            {exercise.target_muscles.map(muscle => (
              <span key={muscle} className="muscle-tag">{muscle}</span>
            ))}
          </div>

          {exercise.equipment && (
            <>
              <h2>Оборудование</h2>
              <p>{exercise.equipment}</p>
            </>
          )}

          {exercise.video_url && (
            <div className="video-container">
              <h2>Видео</h2>
              <iframe
                src={exercise.video_url}
                title={exercise.name}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExerciseDetail; 