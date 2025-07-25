import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For now, simulate a logged-in user
    // In production, this would check for stored tokens and validate with the backend
    setTimeout(() => {
      setUser({
        id: '1',
        name: 'Dr. Sarah Johnson',
        email: 'sarah.johnson@hospital.com',
        role: 'admin',
        organization: 'General Hospital',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612c167?w=150'
      });
      setLoading(false);
    }, 1000);
  }, []);

  const login = async (email, password) => {
    // Simulate login API call
    setLoading(true);
    try {
      // In production, make actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setUser({
        id: '1',
        name: 'Dr. Sarah Johnson',
        email: email,
        role: 'admin',
        organization: 'General Hospital'
      });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
