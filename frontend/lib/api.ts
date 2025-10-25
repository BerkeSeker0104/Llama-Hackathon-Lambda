import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const projectsApi = {
  list: () => api.get('/api/projects'),
  get: (id: string) => api.get(`/api/projects/${id}`),
  create: (data: { detailedDescription: string; department: string }) =>
    api.post('/api/projects', data),
};

// Tasks API
export const tasksApi = {
  list: (projectId: string) => api.get(`/api/projects/${projectId}/tasks`),
  assign: (taskId: string) => api.post(`/api/tasks/${taskId}/assign`),
};

// Employees API
export const employeesApi = {
  list: () => api.get('/api/employees'),
  getByDepartment: (department: string) => api.get(`/api/employees/department/${department}`),
  getWorkload: (department: string) => api.get(`/api/employees/workload/${department}`),
};

// Chat API
export const chatApi = {
  sendMessage: (sessionId: string, message: string) =>
    api.post('/api/chat', { session_id: sessionId, message }),
  getHistory: (sessionId: string) => api.get(`/api/chat/history/${sessionId}`),
};

// Contracts API
export const contractsApi = {
  upload: (formData: FormData) =>
    api.post('/api/contracts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  analyze: (contractId: string) => api.post(`/api/contracts/${contractId}/analyze`),
};

