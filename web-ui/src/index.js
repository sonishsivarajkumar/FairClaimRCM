import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './index.css';
import App from './App';

// Ensure DOM is ready before mounting React
const initializeApp = () => {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    console.error('Root element not found. Make sure there is a div with id="root" in your HTML.');
    return;
  }

  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
        <Toaster position="top-right" />
      </BrowserRouter>
    </React.StrictMode>
  );
};

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}
