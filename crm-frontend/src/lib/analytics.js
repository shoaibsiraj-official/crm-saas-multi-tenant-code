import api from './axios';

export const getDashboardAnalytics = async () => {
  const res = await api.get('/analytics/dashboard/');
  return res.data;
};