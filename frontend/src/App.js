import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import PostList from './components/PostList';
import PostDetail from './components/PostDetail';
import CreatePost from './components/CreatePost';
import Profile from './components/Profile';
import ExerciseList from './components/ExerciseList';
import ExerciseDetail from './components/ExerciseDetail';
import WorkoutList from './components/WorkoutList';
import WorkoutDetail from './components/WorkoutDetail';
import CreateWorkout from './components/CreateWorkout';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="container">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/posts" element={<PostList />} />
              <Route path="/posts/:id" element={<PostDetail />} />
              <Route path="/exercises" element={<ExerciseList />} />
              <Route path="/exercises/:id" element={<ExerciseDetail />} />
              <Route 
                path="/create-post" 
                element={
                  <PrivateRoute>
                    <CreatePost />
                  </PrivateRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <PrivateRoute>
                    <Profile />
                  </PrivateRoute>
                } 
              />
              <Route 
                path="/workouts" 
                element={
                  <PrivateRoute>
                    <WorkoutList />
                  </PrivateRoute>
                } 
              />
              <Route 
                path="/workouts/:id" 
                element={
                  <PrivateRoute>
                    <WorkoutDetail />
                  </PrivateRoute>
                } 
              />
              <Route 
                path="/create-workout" 
                element={
                  <PrivateRoute>
                    <CreateWorkout />
                  </PrivateRoute>
                } 
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App; 