
import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Sidebar from './components/Sidebar';
import Login from './components/Login';
import Dashboard from './pages/Dashboard';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activePage, setActivePage] = useState('dashboard');

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex flex-grow">
        {isAuthenticated && <Sidebar setActivePage={setActivePage} />}
        <div className="flex-grow p-4">
          {!isAuthenticated ? (
            <Login onLogin={() => setIsAuthenticated(true)} />
          ) : (
            activePage === 'dashboard' ? <Dashboard /> : <div>Page not found</div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;
