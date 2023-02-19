import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './app';

const root = ReactDOM.createRoot(document.getElementById('root'));
const appData = JSON.parse(document.getElementById('app-data').textContent);
root.render(
  <React.StrictMode>
    <App {...appData} />
  </React.StrictMode>
);