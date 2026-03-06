import api from './axios';

// GET LIST
export const getClients = async (params) => {
  const res = await api.get('/clients/', { params });
  return res.data.data.results; // ✅ only array
};

// GET SINGLE
export const getClient = async (id) => {
  const res = await api.get(`/clients/${id}/`);
  return res.data.data; // ✅ only client object
};

// CREATE
export const createClient = async (data) => {
  const res = await api.post('/clients/', data);
  return res.data.data; // ✅ only client object
};

// UPDATE
export const updateClient = async (id, data) => {
  const res = await api.patch(`/clients/${id}/`, data);
  return res.data.data; // ✅ only updated client object
};

// DELETE
export const deleteClient = async (id) => {
  const res = await api.delete(`/clients/${id}/`);
  return res.data; // usually just message
};