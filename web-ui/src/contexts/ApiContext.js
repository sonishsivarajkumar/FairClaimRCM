import React, { createContext, useContext } from 'react';
import axios from 'axios';

const ApiContext = createContext();

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

// Configure axios defaults
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const ApiProvider = ({ children }) => {
  // Claims API
  const claimsApi = {
    getAll: (params = {}) => api.get('/api/v1/claims/', { params }),
    getById: (id) => api.get(`/api/v1/claims/${id}`),
    create: (data) => api.post('/api/v1/claims/', data),
    update: (id, data) => api.put(`/api/v1/claims/${id}`, data),
    delete: (id) => api.delete(`/api/v1/claims/${id}`),
    search: (query) => api.post('/api/v1/claims/search', query),
    getCoding: (id) => api.get(`/api/v1/claims/${id}/coding`)
  };

  // Coding API
  const codingApi = {
    analyze: (data) => api.post('/api/v1/coding/analyze', data),
    validate: (codes) => api.post('/api/v1/coding/validate', codes),
    estimateReimbursement: (data) => api.post('/api/v1/coding/reimbursement/estimate', data),
    analyzeBatch: (data) => api.post('/api/v1/coding/analyze/batch', data)
  };

  // Terminology API
  const terminologyApi = {
    searchICD10: (query, limit = 10) => api.get('/api/v1/terminology/icd10/search', { params: { q: query, limit } }),
    getICD10: (code) => api.get(`/api/v1/terminology/icd10/${code}`),
    searchCPT: (query, limit = 10, category) => api.get('/api/v1/terminology/cpt/search', { params: { q: query, limit, category } }),
    getCPT: (code) => api.get(`/api/v1/terminology/cpt/${code}`),
    searchDRG: (query, limit = 10) => api.get('/api/v1/terminology/drg/search', { params: { q: query, limit } }),
    getDRG: (code) => api.get(`/api/v1/terminology/drg/${code}`)
  };

  // Audit API
  const auditApi = {
    getClaimLogs: (claimId) => api.get(`/api/v1/audit/logs/${claimId}`),
    getUserLogs: (userId, limit = 100) => api.get(`/api/v1/audit/user/${userId}`, { params: { limit } }),
    getRecentLogs: (hours = 24) => api.get('/api/v1/audit/recent', { params: { hours } })
  };

  // Analytics API (to be implemented)
  const analyticsApi = {
    getDashboardMetrics: () => api.get('/api/v1/analytics/dashboard'),
    getCodingPatterns: (params = {}) => api.get('/api/v1/analytics/coding-patterns', { params }),
    getPerformanceMetrics: (params = {}) => api.get('/api/v1/analytics/performance', { params }),
    getReimbursementTrends: (params = {}) => api.get('/api/v1/analytics/reimbursement-trends', { params })
  };

  // Users API (to be implemented)
  const usersApi = {
    getAll: (params = {}) => api.get('/api/v1/users/', { params }),
    getById: (id) => api.get(`/api/v1/users/${id}`),
    create: (data) => api.post('/api/v1/users/', data),
    update: (id, data) => api.put(`/api/v1/users/${id}`, data),
    delete: (id) => api.delete(`/api/v1/users/${id}`)
  };

  // Health check
  const healthCheck = () => api.get('/health');

  // Generic API call function
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await api.get(endpoint, options);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const value = {
    api,
    apiCall,
    claimsApi,
    codingApi,
    terminologyApi,
    auditApi,
    analyticsApi,
    usersApi,
    healthCheck
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
};
