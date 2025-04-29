import React, { useState } from 'react';
import axios from 'axios';

const FoodForm = ({ onAddFood }) => {
  const [name, setName] = useState('');
  const [calories, setCalories] = useState('');
  const [proteins, setProteins] = useState('');
  const [fats, setFats] = useState('');
  const [carbs, setCarbs] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://127.0.0.1:8000/foods',
        { name, calories: parseFloat(calories), proteins: parseFloat(proteins), fats: parseFloat(fats), carbs: parseFloat(carbs) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setError('');
      onAddFood(response.data);
    } catch (err) {
      setError('Failed to add food: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <h2>Add Food</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Food Name"
          required
        />
        <input
          type="number"
          value={calories}
          onChange={(e) => setCalories(e.target.value)}
          placeholder="Calories"
          required
        />
        <input
          type="number"
          value={proteins}
          onChange={(e) => setProteins(e.target.value)}
          placeholder="Proteins (g)"
          required
        />
        <input
          type="number"
          value={fats}
          onChange={(e) => setFats(e.target.value)}
          placeholder="Fats (g)"
          required
        />
        <input
          type="number"
          value={carbs}
          onChange={(e) => setCarbs(e.target.value)}
          placeholder="Carbs (g)"
          required
        />
        <button type="submit">Add Food</button>
      </form>
    </div>
  );
};

export default FoodForm;