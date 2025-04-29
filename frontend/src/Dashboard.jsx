import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1>Welcome to GymHelper</h1>
      <p>Track your nutrition and stay healthy!</p>
      <div>
        <Link to="/foods">
          <button>Manage Foods</button>
        </Link>
        <Link to="/tracker">
          <button>Track Nutrition</button>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;