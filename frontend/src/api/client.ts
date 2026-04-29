import axios from 'axios';

// baseURL is empty — all requests use relative paths like /api/query
// Vite proxy routes /api/* to http://backend:8000/api/*
export const apiClient = axios.create({
  baseURL: '',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Network Error';
    console.error('API Error:', message, error.config?.url);
    return Promise.reject(new Error(message));
  }
);
