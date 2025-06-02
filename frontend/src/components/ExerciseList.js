import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ExerciseList.css';

const ExerciseList = () => {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/exercises/');
        setExercises(response.data);
        setLoading(false);
      } catch (err) {
        setError('Ошибка при загрузке упражнений');
        setLoading(false);
      }
    };

    fetchExercises();
  }, []);

  const filteredExercises = filter === 'all' 
    ? exercises 
    : exercises.filter(exercise => exercise.type === filter);

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="exercise-list">
      <div className="exercise-filters">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          Все
        </button>
        <button 
          className={`filter-btn ${filter === 'strength' ? 'active' : ''}`}
          onClick={() => setFilter('strength')}
        >
          Силовые
        </button>
        <button 
          className={`filter-btn ${filter === 'cardio' ? 'active' : ''}`}
          onClick={() => setFilter('cardio')}
        >
          Кардио
        </button>
        <button 
          className={`filter-btn ${filter === 'flexibility' ? 'active' : ''}`}
          onClick={() => setFilter('flexibility')}
        >
          Растяжка
        </button>
      </div>

      <div className="exercises-grid">
        {filteredExercises.map(exercise => (
          <Link to={`/exercises/${exercise.id}`} key={exercise.id} className="exercise-card">
            {exercise.image_url && (
              <img src={exercise.image_url} alt={exercise.name} className="exercise-image" />
            )}
            <div className="exercise-info">
              <h3>{exercise.name}</h3>
              <p>{exercise.description}</p>
              <div className="exercise-tags">
                <span className="tag type">{exercise.type}</span>
                {exercise.target_muscles.map(muscle => (
                  <span key={muscle} className="tag muscle">{muscle}</span>
                ))}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default ExerciseList; 