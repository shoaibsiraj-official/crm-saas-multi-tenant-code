import Cookies from 'js-cookie';
import api from './axios';

export const login = async (email, password) => {
  const response = await api.post("/auth/login/", { email, password });

  const tokens = response.data.data.tokens;

  // ✅ SAVE BOTH TOKENS
  Cookies.set("access_token", tokens.access);
  Cookies.set("refresh_token", tokens.refresh);

  return response.data.data.user;
};

export const register = async (userData) => {
  const response = await api.post('/auth/register/', userData);
  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/auth/logout/');
  } catch (error) {
    console.error('Logout error', error);
  } finally {
    Cookies.remove('access_token');
    window.location.href = '/login';
  }
};

export const forgotPassword = async (email) => {
  return await api.post('/auth/password-reset/', { email });
};

export const resetPassword = async (uid, token, newPassword) => {
  return await api.post('/auth/password/reset/confirm/', { 
    uid, 
    token, 
    new_password: newPassword 
  });
};

export const getUser = async () => {
  const response = await api.get('/auth/me/');
  return response.data.data;  // 🔥 YAHAN FIX
};