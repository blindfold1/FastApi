import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { isAuthenticated, isAdmin, isTrainer, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">GymHelper</Link>
      </div>
      <div className="navbar-menu">
        <Link to="/posts" className="navbar-item">Блог</Link>
        <Link to="/exercises" className="navbar-item">Упражнения</Link>
        {isAuthenticated && (
          <Link to="/workouts" className="navbar-item">Мои тренировки</Link>
        )}
        {(isAdmin || isTrainer) && (
          <Link to="/create-post" className="navbar-item">Создать пост</Link>
        )}
        {isAuthenticated && (
          <Link to="/create-workout" className="navbar-item">Новая тренировка</Link>
        )}
      </div>
      <div className="navbar-end">
        {isAuthenticated ? (
          <>
            <Link to="/profile" className="navbar-item">Профиль</Link>
            <button onClick={handleLogout} className="navbar-item logout-btn">
              Выйти
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="navbar-item">Вход</Link>
            <Link to="/register" className="navbar-item">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar; 