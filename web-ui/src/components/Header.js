import React from 'react';
import { Menu, Bell, User, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Header({ setSidebarOpen }) {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex justify-between items-center px-6 py-4">
        {/* Left side - Menu button */}
        <div className="flex items-center">
          <button
            className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="hidden lg:block">
            <h1 className="text-2xl font-semibold text-gray-900">
              Healthcare Revenue Cycle Management
            </h1>
          </div>
        </div>

        {/* Right side - User menu */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 relative">
            <Bell className="h-6 w-6" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.organization}</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-primary-500 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              
              <button 
                onClick={logout}
                className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
