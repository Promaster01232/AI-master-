import axios from 'axios';
import { store } from '../store/store';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const chat = {
  completions: (data) => api.post('/chat/completions', data),
  stream: (data) => api.post('/chat/stream', data),
  history: (params) => api.get('/chat/history', { params }),
  clearHistory: () => api.delete('/chat/history'),
  rag: (data) => api.post('/chat/rag', data),
};

const models = {
  list: () => api.get('/models'),
  load: (modelName) => api.post(`/models/load/${modelName}`),
  status: () => api.get('/models/status'),
  download: (modelName) => api.post(`/models/download/${modelName}`),
};

const documents = {
  upload: (file, processNow = true) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('process_now', processNow);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  list: (params) => api.get('/documents', { params }),
  get: (documentId) => api.get(`/documents/${documentId}`),
  delete: (documentId) => api.delete(`/documents/${documentId}`),
  process: (documentId) => api.post(`/documents/${documentId}/process`),
  chunks: (documentId, params) => api.get(`/documents/${documentId}/chunks`, { params }),
};

const training = {
  start: (config) => api.post('/training/start', config),
  jobs: (params) => api.get('/training/jobs', { params }),
  job: (jobId) => api.get(`/training/jobs/${jobId}`),
  cancel: (jobId) => api.post(`/training/jobs/${jobId}/cancel`),
  logs: (jobId, params) => api.get(`/training/jobs/${jobId}/logs`, { params }),
  datasets: () => api.get('/training/datasets'),
  createDataset: (data) => api.post('/training/datasets/create', data),
};

const auth = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
};

const health = {
  check: () => api.get('/health'),
};

export const initializeApp = async () => {
  try {
    await health.check();
    console.log('✅ API is connected');
    
    // Load initial data
    store.dispatch({ type: 'models/getModels' });
    
  } catch (error) {
    console.error('❌ Failed to connect to API:', error);
  }
};

export default {
  chat,
  models,
  documents,
  training,
  auth,
  health,
};