import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './CreateWorkout.css';

const CreateWorkout = () => {
  const navigate = useNavigate();
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    date: new Date().toISOString().slice(0, 16),
    duration: 60,
    notes: '',
    exercises: []
  });

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddExercise = () => {
    setFormData(prev => ({
      ...prev,
      exercises: [
        ...prev.exercises,
        {
          exercise_id: '',
          name: '',
          sets: 3,
          reps: 10,
          weight: 0,
          notes: ''
        }
      ]
    }));
  };

  const handleExerciseChange = (index, field, value) => {
    setFormData(prev => {
      const newExercises = [...prev.exercises];
      newExercises[index] = {
        ...newExercises[index],
        [field]: value
      };

      // Если изменился exercise_id, обновляем name
      if (field === 'exercise_id') {
        const exercise = exercises.find(e => e.id === value);
        if (exercise) {
          newExercises[index].name = exercise.name;
        }
      }

      return {
        ...prev,
        exercises: newExercises
      };
    });
  };

  const handleRemoveExercise = (index) => {
    setFormData(prev => ({
      ...prev,
      exercises: prev.exercises.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/workouts/', formData);
      navigate('/workouts');
    } catch (err) {
      setError('Ошибка при создании тренировки');
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="create-workout">
      <h1>Создать тренировку</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Название тренировки</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="date">Дата и время</label>
          <input
            type="datetime-local"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="duration">Длительность (минуты)</label>
          <input
            type="number"
            id="duration"
            name="duration"
            value={formData.duration}
            onChange={handleInputChange}
            min="1"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Заметки</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            rows="4"
          />
        </div>

        <div className="exercises-section">
          <h2>Упражнения</h2>
          {formData.exercises.map((exercise, index) => (
            <div key={index} className="exercise-form">
              <div className="form-group">
                <label>Упражнение</label>
                <select
                  value={exercise.exercise_id}
                  onChange={(e) => handleExerciseChange(index, 'exercise_id', e.target.value)}
                  required
                >
                  <option value="">Выберите упражнение</option>
                  {exercises.map(ex => (
                    <option key={ex.id} value={ex.id}>
                      {ex.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Подходы</label>
                  <input
                    type="number"
                    value={exercise.sets}
                    onChange={(e) => handleExerciseChange(index, 'sets', parseInt(e.target.value))}
                    min="1"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Повторения</label>
                  <input
                    type="number"
                    value={exercise.reps}
                    onChange={(e) => handleExerciseChange(index, 'reps', parseInt(e.target.value))}
                    min="1"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Вес (кг)</label>
                  <input
                    type="number"
                    value={exercise.weight}
                    onChange={(e) => handleExerciseChange(index, 'weight', parseFloat(e.target.value))}
                    min="0"
                    step="0.5"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Заметки</label>
                <input
                  type="text"
                  value={exercise.notes}
                  onChange={(e) => handleExerciseChange(index, 'notes', e.target.value)}
                />
              </div>

              <button
                type="button"
                className="remove-btn"
                onClick={() => handleRemoveExercise(index)}
              >
                Удалить упражнение
              </button>
            </div>
          ))}

          <button
            type="button"
            className="add-btn"
            onClick={handleAddExercise}
          >
            Добавить упражнение
          </button>
        </div>

        <div className="form-actions">
          <button type="submit" className="submit-btn">
            Создать тренировку
          </button>
          <button
            type="button"
            className="cancel-btn"
            onClick={() => navigate('/workouts')}
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateWorkout; 