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
  confirmAction: (sessionId: string, actionType: string, actionData: any, confirmed: boolean) => 
    api.post('/api/chat/confirm-action', { 
      session_id: sessionId, 
      action_type: actionType, 
      action_data: actionData, 
      confirmed 
    }),
  getCategories: () => api.get('/api/chat/categories'),
};

// Contracts API
export const contractsApi = {
  list: () => api.get('/api/contracts'),
  get: (contractId: string) => api.get(`/api/contracts/${contractId}`),
  upload: (formData: FormData) =>
    api.post('/api/contracts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  analyze: (contractId: string, autoAssign: boolean = true) => 
    api.post(`/api/contracts/${contractId}/analyze?auto_assign=${autoAssign}`),
  autoAssignTasks: (contractId: string) => 
    api.post(`/api/contracts/${contractId}/auto-assign-tasks`),
  delete: (contractId: string) => api.delete(`/api/contracts/${contractId}`),
};

// Sprints API (NEW)
export const sprintsApi = {
  list: (projectId: string) => api.get(`/api/sprints/project/${projectId}`),
  get: (projectId: string, sprintId: string) => api.get(`/api/sprints/${projectId}/${sprintId}`),
  generate: (projectId: string, duration: number = 2) =>
    api.post('/api/sprints/generate', { project_id: projectId, sprint_duration_weeks: duration }),
  replan: (projectId: string, vacationDays: number, delays: number) =>
    api.post('/api/sprints/replan', { project_id: projectId, vacation_days: vacationDays, delays }),
  getHealth: (sprintId: string, projectId?: string) =>
    api.get(`/api/sprints/${sprintId}/health`, { params: { project_id: projectId } }),
  getCalendarEvents: (sprintId: string) => api.get(`/api/sprints/${sprintId}/calendar-events`),
};

// Dynamic Sprint Management API (NEW)
export const dynamicSprintApi = {
  // Employee availability
  updateAvailability: (employeeId: string, data: { status: string; unavailable_until?: string; reason?: string }) =>
    api.put(`/api/employees/${employeeId}/availability`, data),
  getEmployeeTasks: (employeeId: string) => api.get(`/api/employees/${employeeId}/tasks`),
  
  // Task reassignment
  reassignTask: (data: { task_title: string; from_employee_id: string; reason: string; project_id?: string }) =>
    api.post('/api/tasks/reassign', data),
  updateTaskDates: (data: { task_id: string; project_id: string; start_date?: string; due_date?: string }) =>
    api.put('/api/tasks/dates', data),
  getAvailableAssignees: (taskTitle: string, projectId?: string) =>
    api.get('/api/tasks/available-assignees', { params: { task_title: taskTitle, project_id: projectId } }),
  
  // Project risk analysis
  getRiskAnalysis: (projectId: string) => api.get(`/api/projects/${projectId}/risk-analysis`),
  getCalendarView: (projectId: string) => api.get(`/api/projects/${projectId}/calendar-view`),
};

