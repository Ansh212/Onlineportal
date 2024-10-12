import './App.css';
import LoginWindow from './components/LoginWindow';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import TestWindow from './components/TestWindow';

function App() {
  const [IsAuthenticated, SetIsAuthenticated] = useState(
    () => localStorage.getItem('isAuthenticated') === 'true'
  );


  const handlelogin = () => {
    SetIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true');
  };

  const handleLogout = () => {
    SetIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated'); 
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginWindow onlogin={handlelogin} />} />
        <Route path="/Dashboard" element={IsAuthenticated ? <Dashboard onLogout={handleLogout} /> : <Navigate to="/" />} />
        <Route path="/TestWindow/:testId" element={IsAuthenticated ? <TestWindow /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
