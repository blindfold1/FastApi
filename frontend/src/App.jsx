import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <Link to="/">Home</Link> |{' '}
          <Link to="/articles">Articles</Link> |{' '}
          <Link to="/profile">Profile</Link>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/articles" element={<Articles />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  );
}

function Home() {
  return (
    <div>
      <h1>Welcome to Blog Platform</h1>
      <p>Share your thoughts and ideas with the world!</p>
    </div>
  );
}

function Articles() {
  return (
    <div>
      <h1>Articles</h1>
      <p>Browse and read interesting articles</p>
    </div>
  );
}

function Profile() {
  return (
    <div>
      <h1>Profile</h1>
      <p>Manage your account and articles</p>
    </div>
  );
}

export default App;