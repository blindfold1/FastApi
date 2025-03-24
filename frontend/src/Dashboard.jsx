// frontend/src/Dashboard.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No token found. Please login.');
        navigate('/');
        return;
      }

      try {
        const response = await axios.get('http://127.0.0.1:8000/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setUser(response.data);
      } catch (err) {
        setError('Failed to fetch user: ' + (err.response?.data?.detail || err.message));
        navigate('/');
      }
    };

    fetchUser().catch((err) => {
      console.error('Error in fetchUser:', err);
    });
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/');
  };

  return (
    <div>
      <h2>Dashboard</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {user && (
        <div>
          <p>Username: {user.username}</p>
          <p>Name: {user.name || 'N/A'}</p>
          <p>Weight: {user.weight || 'N/A'}</p>
          <p>Height: {user.height || 'N/A'}</p>
          <p>Age: {user.age || 'N/A'}</p>
          <p>Active: {user.is_active ? 'Yes' : 'No'}</p>
          <p>Scopes: {user.scopes || 'N/A'}</p>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
    </div>
  );
}

export default Dashboard;