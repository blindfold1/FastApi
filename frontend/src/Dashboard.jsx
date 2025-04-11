import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

function Dashboard() {
  const [productName, setProductName] = useState('');
  const [addedFood, setAddedFood] = useState(null);
  const [tracker, setTracker] = useState(null);
  const [todayFoods, setTodayFoods] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const refreshAccessToken = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      setError('No refresh token found. Please login again.');
      navigate('/');
      return null;
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`,
        },
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      return access_token;
    } catch (err) {
      setError('Session expired. Please login again.');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/');
      return null;
    }
  };

  const searchAndAddFood = async () => {
    if (isLoading) return;
    setIsLoading(true);

    let accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setError('No access token found. Please login again.');
      navigate('/');
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/food/search-and-add-food/',
        { name: productName, exact_match: false, data_type: "Foundation" },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setAddedFood(response.data);
      setProductName('');
      await fetchTodayTracker();
      await fetchTodayFoods();
    } catch (err) {
      if (err.response?.status === 401) {
        accessToken = await refreshAccessToken();
        if (accessToken) {
          try {
            const response = await axios.post(
              'http://127.0.0.1:8000/food/search-and-add-food/',
              { name: productName, exact_match: false, data_type: "Foundation" },
              {
                headers: {
                  Authorization: `Bearer ${accessToken}`,
                  'Content-Type': 'application/json',
                },
              }
            );
            setAddedFood(response.data);
            setProductName('');
            await fetchTodayTracker();
            await fetchTodayFoods();
          } catch (retryErr) {
            setError('Failed to add food: ' + (retryErr.response?.data?.detail || retryErr.message));
          }
        }
      } else {
        setError('Failed to add food: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTodayTracker = async () => {
    if (isLoading) return;
    setIsLoading(true);

    let accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setError('No access token found. Please login again.');
      navigate('/');
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/tracker/today', {
        headers: {
          Authorization: `Bearer ${accessToken}`, // Исправлено
        },
      });
      setTracker(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        accessToken = await refreshAccessToken();
        if (accessToken) {
          try {
            const response = await axios.get('http://127.0.0.1:8000/tracker/today', {
              headers: {
                Authorization: `Bearer ${accessToken}`, // Исправлено
              },
            });
            setTracker(response.data);
          } catch (retryErr) {
            setError('Failed to fetch tracker: ' + (retryErr.response?.data?.detail || retryErr.message));
          }
        }
      } else {
        setError('Failed to fetch tracker: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTodayFoods = async () => {
    if (isLoading) return;
    setIsLoading(true);

    let accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      setError('No access token found. Please login again.');
      navigate('/');
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/tracker/foods/today', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      setTodayFoods(response.data);
    } catch (err) {
      if (err.response?.status === 401) {
        accessToken = await refreshAccessToken();
        if (accessToken) {
          try {
            const response = await axios.get('http://127.0.0.1:8000/tracker/foods/today', {
              headers: {
                Authorization: `Bearer ${accessToken}`,
              },
            });
            setTodayFoods(response.data);
          } catch (retryErr) {
            setError('Failed to fetch foods: ' + (retryErr.response?.data?.detail || retryErr.message));
          }
        }
      } else {
        setError('Failed to fetch foods: ' + (err.response?.data?.detail || err.message));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/');
  };

  useEffect(() => {
    fetchTodayTracker();
    fetchTodayFoods();
  }, []);

  return (
    <div className="dashboard">
      <header>
        <h1>Calorie Tracker</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>
      <main>
        {error && <p className="error">{error}</p>}
        <section>
          <h2>Add Food</h2>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="Enter food name"
            disabled={isLoading}
          />
          <button onClick={searchAndAddFood} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Search and Add'}
          </button>
          {addedFood && (
            <div className="added-food">
              <h3>Added: {addedFood.name}</h3>
              <p>Calories: {addedFood.calories} kcal</p>
              <p>Proteins: {addedFood.proteins} g</p>
              <p>Fats: {addedFood.fats} g</p>
              <p>Carbs: {addedFood.carbs} g</p>
              <p>Added at: {new Date(addedFood.created_at).toLocaleString()}</p>
            </div>
          )}
        </section>
        <section>
          <h2>Today's Summary</h2>
          {tracker ? (
            <div className="tracker-summary">
              <p>Total Calories: {tracker.calories.toFixed(2)} kcal</p>
              <p>Total Proteins: {tracker.proteins.toFixed(2)} g</p>
              <p>Total Fats: {tracker.fats.toFixed(2)} g</p>
              <p>Total Carbs: {tracker.carbs.toFixed(2)} g</p>
            </div>
          ) : (
            <p>Loading tracker...</p>
          )}
        </section>
        <section>
          <h2>Today's Foods</h2>
          {todayFoods.length > 0 ? (
            <ul className="food-list">
              {todayFoods.map((food) => (
                <li key={food.id}>
                  <p>{food.name}</p>
                  <p>Calories: {food.calories} kcal</p>
                  <p>Proteins: {food.proteins} g</p>
                  <p>Fats: {food.fats} g</p>
                  <p>Carbs: {food.carbs} g</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No foods added today.</p>
          )}
        </section>
      </main>
    </div>
  );
}

export default Dashboard;