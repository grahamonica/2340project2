import React from 'react';
import ReactDOM from 'react-dom/client';
import './globals.css'; // Make sure this path is correct.
import App from './App'; // Make sure this path is correct as well.

document.addEventListener('DOMContentLoaded', () => {
  const rootElement = document.getElementById('root'); // Ensure the 'root' div is available in index.html.
  if (rootElement) {
    const root = ReactDOM.createRoot(rootElement); // React 18+ createRoot
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } else {
    console.error("Root element not found!");
  }
});
