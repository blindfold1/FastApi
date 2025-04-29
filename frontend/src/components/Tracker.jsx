import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Tracker = () => {
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTracker = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://127.0.0.1:8000/tracker', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setEntries(response.data);
      } catch (err) {
        setError('Failed to fetch tracker: ' + (err.response?.data?.detail || err.message));
      }
    };
    fetchTracker();
  }, []);

  return (
    <div>
      <h2>Nutrition Tracker</h2>
      {error && <p className="error">{error}</p>}
      <ul>
        {entries.map((entry) => (
          <li key={entry.id}>
            {entry.date}: {entry.calories} kcal, {entry.proteins}g protein, {entry.fats}g fats, {entry.carbs}g carbs
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Tracker;