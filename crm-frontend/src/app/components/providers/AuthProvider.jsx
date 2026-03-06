'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { getUser } from '../../../lib/auth';
import Cookies from 'js-cookie';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const verifyUser = async () => {
      const token = Cookies.get('access_token');
      const userData = await getUser();
      setUser(userData);
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const userData = await getUser();
        setUser(userData);
      } catch (error) {
        console.error("Session invalid", error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    verifyUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}