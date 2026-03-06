import api from './axios';

export const getProjects = async (params) => {
  const res = await api.get('/projects/', { params });

  console.log("PROJECT LIST RESPONSE:", res.data);

  // 🔥 Your backend structure
  if (res.data.projects) return res.data.projects;

  // fallback (if wrapped in data)
  if (res.data.data?.projects) return res.data.data.projects;

  return [];
};
export const getProject = async (id) => {
  const res = await api.get(`/projects/${id}/`);

  console.log("FULL PROJECT DETAIL RESPONSE:", res.data);

  return res.data.data;
};

export const createProject = async (data) => {
  const res = await api.post('/projects/', data);
  return res.data.data;
};

export const updateProject = async (id, data) => {
  const res = await api.patch(`/projects/${id}/`, data);
  return res.data;
};

export const deleteProject = async (id) => {
  await api.delete(`/projects/${id}/`);
};

export const getProjectTasks = async (id) => {
  const res = await api.get(`/projects/${id}/tasks/`);

  console.log("TASK API RESPONSE:", res.data);

  // 🔥 Case 1: data.tasks array
  if (Array.isArray(res.data?.data?.tasks)) {
    return res.data.data.tasks;
  }

  // 🔥 Case 2: data itself array
  if (Array.isArray(res.data?.data)) {
    return res.data.data;
  }

  // 🔥 Case 3: plain array
  if (Array.isArray(res.data)) {
    return res.data;
  }

  return [];
};

export const updateTask = async (taskId, data) => {
  const res = await api.patch(`/tasks/${taskId}/`, data);
  return res.data;
};

export const createTask = async (projectId, data) => {
  const res = await api.post(`/projects/${projectId}/tasks/`, data);
  return res.data;
};

export const getProjectMembers = async (id) => {
  const res = await api.get(`/projects/${id}/members/`);
  return res.data;
};

export const assignMember = async (projectId, data) => {
  const res = await api.post(`/projects/${projectId}/assign-member/`, data);
  return res.data;
};

// 🔥 DELETE TASK
export const deleteTask = async (taskId) => {
  const res = await api.delete(`/projects/tasks/${taskId}/`);
  return res.data.data;
};

export const moveTask = async (taskId, data) => {
  const res = await api.patch(`/tasks/${taskId}/move/`, data);
  return res.data.data;
};