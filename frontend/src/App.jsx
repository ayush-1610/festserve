import React from 'react';
import { createRoot } from 'react-dom/client';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import Login from './pages/Login';
import CampaignList from './pages/CampaignList';

function App() {
  const token = localStorage.getItem('token');
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={token ? <CampaignList /> : <Navigate to="/login" replace />}
        />
      </Routes>
    </Router>
  );
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
