import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileText, 
  Code, 
  BarChart3, 
  Users, 
  Settings,
  Heart,
  X
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Claims', href: '/claims', icon: FileText },
  { name: 'Coding', href: '/coding', icon: Code },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar({ open, setOpen }) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        lg:relative lg:translate-x-0 lg:flex lg:flex-col
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 bg-primary-600 text-white">
          <div className="flex items-center space-x-2">
            <Heart className="h-8 w-8" />
            <span className="text-xl font-bold">FairClaimRCM</span>
          </div>
          <button
            className="lg:hidden"
            onClick={() => setOpen(false)}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            v0.3.0 - Healthcare RCM
          </p>
        </div>
      </div>
    </>
  );
}
