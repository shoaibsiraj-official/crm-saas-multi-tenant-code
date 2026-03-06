import api from './axios';

export const getInvoices = async () => {
  const res = await api.get('/invoices/');
  return res.data.data.results; 
};

export const createInvoice = async (data) => {
  const res = await api.post('/invoices/', data);
  return res.data;
};

export const updateInvoice = async (id, data) => {
  const res = await api.patch(`/invoices/${id}/`, data);
  return res.data;
};

export const deleteInvoice = async (id) => {
  await api.delete(`/invoices/${id}/`);
};