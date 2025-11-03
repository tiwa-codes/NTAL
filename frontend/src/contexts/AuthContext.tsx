import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';
import type { Provider } from '../types';

interface AuthContextType {
  provider: Provider | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [provider, setProvider] = useState<Provider | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      authService
        .getCurrentProvider()
        .then(setProvider)
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    const response = await authService.login({ username, password });
    localStorage.setItem('token', response.access_token);
    setToken(response.access_token);
    const providerData = await authService.getCurrentProvider();
    setProvider(providerData);
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setProvider(null);
  };

  return (
    <AuthContext.Provider value={{ provider, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
