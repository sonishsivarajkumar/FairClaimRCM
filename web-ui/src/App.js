import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Claims from './pages/Claims';
import Coding from './pages/Coding';
import Analytics from './pages/Analytics';
import Users from './pages/Users';
import Settings from './pages/Settings';
import { AuthProvider } from './contexts/AuthContext';
import { ApiProvider } from './contexts/ApiContext';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <AuthProvider>
      <ApiProvider>
        <div className="flex h-screen bg-gray-100">
          <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
          
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header setSidebarOpen={setSidebarOpen} />
            
            <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/claims" element={<Claims />} />
                <Route path="/coding" element={<Coding />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/users" element={<Users />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </div>
      </ApiProvider>
    </AuthProvider>
  );
}

export default App;
