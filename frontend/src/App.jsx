import React from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">FestServe Frontend</h1>
      <p>Your PWA will live here.</p>
    </div>
  );
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);