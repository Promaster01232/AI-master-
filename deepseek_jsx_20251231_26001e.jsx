import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';

import store from './store/store';
import Layout from './components/Layout/Layout';
import Home from './pages/Home';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Training from './pages/Training';
import Settings from './pages/Settings';
import { initializeApp } from './services/api';

import './styles/globals.css';

function App() {
  useEffect(() => {
    // Initialize app
    initializeApp();
  }, []);

  return (
    <Provider store={store}>
      <Router>
        <div className="App min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/training" element={<Training />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          <Toaster position="top-right" />
        </div>
      </Router>
    </Provider>
  );
}

export default App;