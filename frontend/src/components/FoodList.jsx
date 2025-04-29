import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FoodList = () => {
  const [foods, setFoods] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchFoods = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:8000/foods', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setFoods(response.data);
      } catch (err) {
        setError('Failed to fetch foods: ' + (err.response?.data?.detail || err.message));
      }
    };
    fetchFoods();
  }, []);

  return (
    <div>
      <h2>My Foods</h2>
      {error && <p className="error">{error}</p>}
      <ul>
        {foods.map((food) => (
          <li key={food.id}>
            {food.name} - {food.calories} kcal, {food.proteins}g protein, {food.fats}g fats, {food.carbs}g carbs
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FoodList;